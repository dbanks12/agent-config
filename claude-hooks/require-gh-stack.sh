#!/usr/bin/env bash
# Claude Code PreToolUse hook (Bash). Blocks a stacked PR made without gh stack:
# `gh pr create` or `gh pr edit` with a --base/-B that is the head branch of another open PR.
# A base branch such as main or next is not the head of an open PR, so the hook allows it.
# Stacked PRs must be a GitHub stack (gh stack init/add/submit, or gh stack link).
input=$(cat)
cmd=$(jq -r '.tool_input.command // ""' <<<"$input")
grep -Eq '(^|[^[:alnum:]-])gh[[:space:]]+pr[[:space:]]+(create|edit)\b' <<<"$cmd" || exit 0
flag() { grep -Eo -- "($1)[= ]+[\"']?[^[:space:]\"']+" <<<"$cmd" | head -1 | sed -E "s/^($1)[= ]+[\"']?//"; }
base=$(flag '--base|-B')
[ -z "$base" ] && exit 0
# The hook runs in the session folder, which may not be the repository. Check the folder of a
# leading `cd <dir> &&`, or the repository that --repo/-R names.
dir=$(jq -r '.cwd // empty' <<<"$input")
if [[ $cmd =~ ^[[:space:]]*cd[[:space:]]+([^[:space:]\;\&\|]+)[[:space:]]*(\&\&|\;) ]]; then
  target=${BASH_REMATCH[1]//[\"\']/}
  target=${target/#\~/$HOME}
  [[ $target == /* ]] || target=$dir/$target
  dir=$target
fi
[ -n "$dir" ] && cd "$dir" 2>/dev/null
repo=$(flag '--repo|-R')
gh_repo=()
[ -n "$repo" ] && gh_repo=(--repo "$repo")
if [ -n "$repo" ]; then
  default=$(gh repo view "$repo" --json defaultBranchRef --jq .defaultBranchRef.name 2>/dev/null)
else
  default=$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null | sed 's#^origin/##')
fi
if [ -n "$default" ]; then
  [ "$base" = "$default" ] && exit 0
else
  case "$base" in main | master) exit 0 ;; esac
fi
open_prs=$(gh pr list "${gh_repo[@]}" --head "$base" --state open --json number --jq length 2>/dev/null)
[ "$open_prs" = "0" ] && exit 0
if [[ $open_prs =~ ^[0-9]+$ ]]; then
  reason="Blocked: this PR targets '$base', the head branch of an open PR, so it is a stacked PR. Never stack PRs without gh stack. Use 'gh stack init <branches...>' then 'gh stack submit --auto' (drafts), or 'gh stack link <PRs...>' for existing PRs. Rebase with 'gh stack rebase' and push with 'gh stack push'."
else
  reason="Blocked: the hook could not check whether '$base' is the head branch of an open PR. Start the command with 'cd <repository> &&', or pass --repo <owner>/<name>."
fi
jq -n --arg r "$reason" '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "deny", permissionDecisionReason: $r}}'
