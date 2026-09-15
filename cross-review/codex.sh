#!/usr/bin/env bash
# Run Codex once, read-only, from the current Git worktree.
# Lives in agent-config/cross-review. Called by the call-codex, review-with-codex, and review-by-council skills.
#
#   codex.sh prompt      [-m MODEL] [-e EFFORT]                    < prompt
#   codex.sh code-review [-m MODEL] [-e EFFORT] --base REF          # native review
#   codex.sh code-review [-m MODEL] [-e EFFORT] --commit SHA
#   codex.sh code-review [-m MODEL] [-e EFFORT] --uncommitted
#   codex.sh code-review [-m MODEL] [-e EFFORT]                     < instructions
#
# MODEL is a name from ~/.config/cross-review/models (astra, sol, ...) or an
# exact Codex model. EFFORT is low, medium, high, or xhigh.
# `codex review` takes either a target flag or stdin instructions, not both.
set -euo pipefail

models_file="${XDG_CONFIG_HOME:-$HOME/.config}/cross-review/models"

usage() { sed -n '3,13p' "$0" >&2; exit 2; }

if [[ -n "${ENGINEERING_CROSS_MODEL_REVIEW_ACTIVE:-}" ]]; then
  echo "Nested cross-model call is disabled." >&2
  exit 2
fi
command -v codex >/dev/null 2>&1 || { echo "Codex CLI is not on PATH." >&2; exit 127; }
repo_root="$(git rev-parse --show-toplevel 2>/dev/null)" || { echo "Run this from a Git worktree." >&2; exit 2; }

mode="${1:-}"; shift || true
[[ "$mode" == prompt || "$mode" == code-review ]] || usage

model="" effort="" target=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    -m) model="${2:?}"; shift 2 ;;
    -e) effort="${2:?}"; shift 2 ;;
    --base|--commit) target=("$1" "${2:?}"); shift 2 ;;
    --uncommitted) target=("$1"); shift ;;
    *) usage ;;
  esac
done
[[ "$mode" == prompt && ${#target[@]} -gt 0 ]] && usage

# Resolve a short name (astra) to the CLI model (gpt-6-astra) via the models file.
if [[ -n "$model" && -f "$models_file" ]]; then
  resolved="$(awk -v n="$model" 'tolower($1)=="openai" && tolower($2)==tolower(n) { print $3 }' "$models_file")"
  [[ -n "$resolved" ]] && model="$resolved"
fi

cd "$repo_root"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

config=()
[[ -n "$model" ]] && config+=(-c "model=\"$model\"")
[[ -n "$effort" ]] && config+=(-c "model_reasoning_effort=\"$effort\"")

sandbox_failed() {  # sandbox_failed <output-file>: true if the local sandbox broke the run
  grep -Eqi 'sandbox.{0,80}(loopback|setup|configure|failed)|loopback.{0,80}(sandbox|configure|failed)|bwrap:' "$1"
}

if [[ "$mode" == prompt ]]; then
  cat > "$tmp/prompt.txt"
  run() {  # run <sandbox-flag>
    ENGINEERING_CROSS_MODEL_REVIEW_ACTIVE=1 timeout 30m codex exec \
      --cd "$repo_root" "$1" "${config[@]}" --ephemeral --color never - < "$tmp/prompt.txt"
  }
  if [[ "${ENGINEERING_CODEX_YOLO:-0}" == 1 ]]; then run --dangerously-bypass-approvals-and-sandbox; exit $?; fi
  status=0
  run --sandbox=read-only | tee "$tmp/out.txt" || status=$?
  if [[ $status -ne 0 ]] || sandbox_failed "$tmp/out.txt"; then
    echo "The Codex sandbox failed. Retrying this read-only call without the local sandbox." >&2
    run --dangerously-bypass-approvals-and-sandbox
  fi
  exit
fi

# code-review: Codex's built-in review. Pin the sandbox to read-only; a model override can change the default.
if [[ ${#target[@]} -eq 0 ]]; then
  cat > "$tmp/prompt.txt"
  [[ -s "$tmp/prompt.txt" ]] || { echo "code-review needs a target flag or instructions on stdin." >&2; exit 2; }
fi
run() {  # run [extra -c overrides]
  if [[ ${#target[@]} -gt 0 ]]; then
    ENGINEERING_CROSS_MODEL_REVIEW_ACTIVE=1 timeout 30m codex review "${target[@]}" "${config[@]}" "$@"
  else
    ENGINEERING_CROSS_MODEL_REVIEW_ACTIVE=1 timeout 30m codex review "${config[@]}" "$@" - < "$tmp/prompt.txt"
  fi
}
if [[ "${ENGINEERING_CODEX_YOLO:-0}" == 1 ]]; then run -c 'sandbox_mode="danger-full-access"'; exit $?; fi
status=0
run -c 'sandbox_mode="read-only"' | tee "$tmp/out.txt" || status=$?
if [[ $status -ne 0 ]] || sandbox_failed "$tmp/out.txt"; then
  echo "The Codex sandbox failed. Retrying this read-only review without the local sandbox." >&2
  run -c 'sandbox_mode="danger-full-access"'
fi
