#!/usr/bin/env bash
# Claude Code PreToolUse hook (Bash). Blocks a stacked PR made without gh stack:
# `gh pr create` or `gh pr edit` with a --base/-B that is the head branch of another open PR.
# A base branch such as main or next is not the head of an open PR, so the hook allows it.
# Stacked PRs must be a GitHub stack (gh stack init/add/submit, or gh stack link).
cmd=$(jq -r '.tool_input.command // ""')
grep -Eq '(^|[^[:alnum:]-])gh[[:space:]]+pr[[:space:]]+(create|edit)\b' <<<"$cmd" || exit 0
base=$(grep -Eo -- '(--base|-B)[= ]+["'"'"']?[^[:space:]"'"'"']+' <<<"$cmd" | head -1 | sed -E 's/^(--base|-B)[= ]+["'"'"']?//')
[ -z "$base" ] && exit 0
default=$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null | sed 's#^origin/##')
if [ -n "$default" ]; then
  [ "$base" = "$default" ] && exit 0
else
  case "$base" in main | master) exit 0 ;; esac
fi
open_prs=$(gh pr list --head "$base" --state open --json number --jq length 2>/dev/null)
[ "$open_prs" = "0" ] && exit 0
reason="Blocked: this PR targets '$base', the head branch of an open PR, so it is a stacked PR. Never stack PRs without gh stack. Use 'gh stack init <branches...>' then 'gh stack submit --auto' (drafts), or 'gh stack link <PRs...>' for existing PRs. Rebase with 'gh stack rebase' and push with 'gh stack push'."
jq -n --arg r "$reason" '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "deny", permissionDecisionReason: $r}}'
