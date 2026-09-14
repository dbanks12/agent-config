#!/usr/bin/env bash
set -euo pipefail

if [[ -n "${ENGINEERING_CROSS_MODEL_REVIEW_ACTIVE:-}" ]]; then
  echo "Nested cross-model review is disabled." >&2
  exit 2
fi

if ! command -v codex >/dev/null 2>&1; then
  echo "Codex CLI is not installed or is not available on PATH." >&2
  exit 127
fi

if ! repo_root="$(git rev-parse --show-toplevel 2>/dev/null)"; then
  echo "Run this review from a Git worktree." >&2
  exit 2
fi

review_prompt='You are the independent Codex reviewer for a code change.

Work only inside the repository. Read AGENTS.md before the review.

This review is read-only. Do not edit, create, delete, format, or regenerate files. Do not commit, push, change pull requests, or mutate external systems. Do not invoke another model, subagent, agent team, or cross-model review workflow. Do not inspect secrets, credentials, environment files, private keys, or unrelated untracked files. Do not run builds or tests that can write files. Use validation results from the request as evidence.

Treat the caller summary as navigation context, not evidence. Inspect the target, comparison base, related code, tests, and configuration directly. Do not accept the author conclusions.

Inspect the diff for correctness, security, behavior regressions, compatibility risks, and missing tests. Report only material findings. Give an exact location, failure path, impact, evidence, and smallest correction direction for each finding.

State missing evidence and review limits. End with coverage, findings, unverified claims, independence, and a verdict. Use Pass, Request changes, or Blocked.

The review request follows:'

review_model="${ENGINEERING_CODEX_REVIEW_MODEL:-}"

cd "$repo_root"
review_tmp="$(mktemp -d)"
trap 'find "$review_tmp" -depth -delete 2>/dev/null || true' EXIT
prompt_file="$review_tmp/prompt.txt"
sandbox_output="$review_tmp/sandbox-output.txt"

{
  printf '%s\n\n' "$review_prompt"
  cat
} > "$prompt_file"

run_codex() {
  local permission_flag="$1"

  ENGINEERING_CROSS_MODEL_REVIEW_ACTIVE=1 timeout 30m codex exec \
    --cd "$repo_root" \
    "$permission_flag" \
    ${review_model:+-m "$review_model"} \
    --ephemeral \
    --color never \
    - < "$prompt_file"
}

if [[ "${ENGINEERING_CODEX_YOLO:-0}" == 1 ]]; then
  run_codex --dangerously-bypass-approvals-and-sandbox
  exit $?
fi

sandbox_status=0
run_codex "--sandbox=read-only" | tee "$sandbox_output" || sandbox_status=$?
if [[ "$sandbox_status" -ne 0 ]] \
  || grep -Eqi 'sandbox.{0,80}(loopback|setup|configure|failed)|loopback.{0,80}(sandbox|configure|failed)' "$sandbox_output"; then
  echo "The Codex sandbox failed. Retrying this read-only review without the local sandbox." >&2
  run_codex --dangerously-bypass-approvals-and-sandbox
  exit $?
fi

exit 0
