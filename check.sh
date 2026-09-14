#!/usr/bin/env bash
# Check that skills follow the repo pattern. Exit 1 on any problem.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

tool_specific="review-with-codex review-with-claude"   # skills that link into one tool only
failed=0
fail() { echo "check: $*" >&2; failed=1; }

# tools = every ~/.<tool>/skills prefix that appears in links
tools=$(awk '$2 ~ /^~\/\.[a-z]+\/skills\// { sub(/^~\/\./, "", $2); sub(/\/.*/, "", $2); print $2 }' links | sort -u)
[[ -n "$tools" ]] || fail "no skill links found"

for dir in skills/*/; do
  skill=$(basename "$dir")
  [[ -f "$dir/SKILL.md" ]] || { fail "$skill: missing SKILL.md"; continue; }
  grep -q "^name: $skill\$" "$dir/SKILL.md" || fail "$skill: SKILL.md name must be '$skill'"
  grep -q "^description: ." "$dir/SKILL.md" || fail "$skill: SKILL.md needs a description"
  linked=$(awk -v s="skills/$skill" '$1 == s { sub(/^~\/\./, "", $2); sub(/\/.*/, "", $2); print $2 }' links | sort -u)
  [[ -n "$linked" ]] || { fail "$skill: not in links"; continue; }
  case " $tool_specific " in *" $skill "*) continue;; esac
  for tool in $tools; do
    grep -qx "$tool" <<< "$linked" || fail "$skill: not linked into ~/.$tool/skills (add it, or list it in tool_specific)"
  done
done

exit $failed
