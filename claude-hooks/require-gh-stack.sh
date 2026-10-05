#!/usr/bin/env bash
# Claude Code PreToolUse hook (Bash). Blocks a stacked PR made without gh stack:
# `gh pr create` or `gh pr edit` with a --base/-B that is not the repo's default branch.
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
reason="Blocked: this PR targets '$base', not the default branch, so it is a stacked PR. Never stack PRs without gh stack. Use 'gh stack init <branches...>' then 'gh stack submit --auto' (drafts), or 'gh stack link <PRs...>' for existing PRs. Rebase with 'gh stack rebase' and push with 'gh stack push'."
jq -n --arg r "$reason" '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "deny", permissionDecisionReason: $r}}'
