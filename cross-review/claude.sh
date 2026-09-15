#!/usr/bin/env bash
# Run Claude Code once, read-only, from the current Git worktree.
# Lives in agent-config/cross-review. Called by the call-claude, review-with-claude, and review-by-council skills.
#
#   claude.sh prompt      [-m MODEL] [-e EFFORT]                       < prompt
#   claude.sh code-review [-m MODEL] [-e EFFORT] [--target <base>...HEAD|<sha>|<pr#>|<branch>|<path>]
#
# MODEL is a name from the models file next to this script (fable, opus, ...),
# a Claude alias, or a full model name.
# EFFORT is low, medium, high, xhigh, or max.
# code-review runs Claude Code's built-in /code-review skill. With no --target
# it diffs against the branch's upstream, which is empty on a pushed branch.
# Pass --target main...HEAD to review a branch against main. It takes no
# extra instructions.
set -euo pipefail

models_file="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/models"

usage() { sed -n '3,11p' "$0" >&2; exit 2; }

if [[ -n "${ENGINEERING_CROSS_MODEL_REVIEW_ACTIVE:-}" ]]; then
  echo "Nested cross-model call is disabled." >&2
  exit 2
fi
command -v claude >/dev/null 2>&1 || { echo "Claude CLI is not on PATH." >&2; exit 127; }
repo_root="$(git rev-parse --show-toplevel 2>/dev/null)" || { echo "Run this from a Git worktree." >&2; exit 2; }

mode="${1:-}"; shift || true
[[ "$mode" == prompt || "$mode" == code-review ]] || usage

model="" effort="" target=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    -m) model="${2:?}"; shift 2 ;;
    -e) effort="${2:?}"; shift 2 ;;
    --target) target="${2:?}"; shift 2 ;;
    *) usage ;;
  esac
done
[[ "$mode" == prompt && -n "$target" ]] && usage

# Resolve a short name (Fable) to the CLI model (fable) via the models file.
if [[ -n "$model" ]]; then
  resolved="$(awk -v n="$model" 'tolower($1)=="claude" && tolower($2)==tolower(n) { print $3 }' "$models_file")"
  [[ -n "$resolved" ]] && model="$resolved"
fi

cd "$repo_root"
common=(--print --permission-mode plan --strict-mcp-config --no-chrome --no-session-persistence --output-format text)
[[ -n "$model" ]] && common+=(--model "$model")
[[ -n "$effort" ]] && common+=(--effort "$effort")

if [[ "$mode" == prompt ]]; then
  ENGINEERING_CROSS_MODEL_REVIEW_ACTIVE=1 timeout 30m claude "${common[@]}" \
    --restricted --tools "Read,Glob,Grep,Bash"
  exit
fi

# code-review: the built-in skill. It fans out to subagents, so leave the tool set open.
ENGINEERING_CROSS_MODEL_REVIEW_ACTIVE=1 timeout 30m claude "${common[@]}" \
  "/code-review ${effort:-high}${target:+ $target}"
