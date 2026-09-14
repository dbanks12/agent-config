#!/usr/bin/env bash
set -euo pipefail

if [[ -n "${ENGINEERING_CROSS_MODEL_REVIEW_ACTIVE:-}" ]]; then
  echo "Nested cross-model review is disabled." >&2
  exit 2
fi

if ! command -v claude >/dev/null 2>&1; then
  echo "Claude CLI is not installed or is not available on PATH." >&2
  exit 127
fi

if ! repo_root="$(git rev-parse --show-toplevel 2>/dev/null)"; then
  echo "Run this review from a Git worktree." >&2
  exit 2
fi

review_prompt='You are the independent Claude reviewer for a code change.

Work only inside the repository. Read AGENTS.md before the review.

This review is read-only. Do not edit, create, delete, format, or regenerate files. Do not commit, push, change pull requests, or mutate external systems. Do not invoke another model, subagent, agent team, or cross-model review workflow. Do not inspect secrets, credentials, environment files, private keys, or unrelated untracked files. Do not run builds or tests that can write files. Use validation results from the request as evidence.

Treat the caller summary as navigation context, not evidence. Inspect the target, comparison base, related code, tests, and configuration directly. Do not accept the author conclusions.

Inspect the diff for correctness, security, behavior regressions, compatibility risks, and missing tests. Report only material findings. Give an exact location, failure path, impact, evidence, and smallest correction direction for each finding.

State missing evidence and review limits. End with coverage, findings, unverified claims, independence, and a verdict. Use Pass, Request changes, or Blocked.

The review request follows:'

review_model="${ENGINEERING_CLAUDE_REVIEW_MODEL:-fable}"
review_effort="${ENGINEERING_CLAUDE_REVIEW_EFFORT:-high}"

cd "$repo_root"
{
  printf '%s\n\n' "$review_prompt"
  cat
} | ENGINEERING_CROSS_MODEL_REVIEW_ACTIVE=1 timeout 30m claude \
  --print \
  --model "$review_model" \
  --effort "$review_effort" \
  --restricted \
  --permission-mode plan \
  --tools "Read,Glob,Grep,Bash" \
  --strict-mcp-config \
  --no-chrome \
  --no-session-persistence \
  --output-format text
