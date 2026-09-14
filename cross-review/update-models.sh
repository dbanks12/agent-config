#!/usr/bin/env bash
# Maintain the model-name list that both cross-tool review skills trigger on,
# and regenerate the `description:` frontmatter line in each SKILL.md.
set -euo pipefail

dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
models="$dir/models"
claude_skill="$HOME/.claude/skills/review-with-codex/SKILL.md"
codex_skill="$HOME/.codex/skills/review-with-claude/SKILL.md"
stale_days=30

usage() {
  cat <<USAGE
usage: update-models.sh <command>
  list                      show the current list
  add <family> <name>...    add names (family: claude | openai) and re-render
  remove <family> <name>... remove names and re-render
  render                    rewrite the description line in both SKILL.md files
  check <family>            print a reminder if the list is older than $stale_days days
  ack                       mark the list as reviewed (resets the reminder timer)
USAGE
}

names_for() {  # names_for <family> -> comma-joined names
  awk -v f="$1" '$1 == f { printf "%s%s", (n++ ? ", " : ""), $2 }' "$models"
}

set_description() {  # set_description <file> <text>
  local file="$1" text="$2"
  awk -v text="$text" '
    NR == 1 && $0 == "---" { fm = 1 }
    fm && NR > 1 && $0 == "---" { fm = 0 }
    fm && /^description:/ { print "description: " text; next }
    { print }
  ' "$file" > "$file.tmp" && mv "$file.tmp" "$file"
}

render() {
  local openai claude
  openai="$(names_for openai)"
  claude="$(names_for claude)"
  set_description "$claude_skill" \
    "Run an independent, read-only Codex review of a code change. Use whenever the user asks for a review, second opinion, or cross-model review from any non-Claude model or tool, named with or without a version number, including $openai. A bare family name means its latest version. Do not use for ordinary self-review or to implement fixes."
  set_description "$codex_skill" \
    "Run an independent, read-only Claude review of a code change. Use whenever the user asks for a review, second opinion, or cross-model review from any non-OpenAI model or tool, named with or without a version number, including $claude. A bare family name means its latest version. Do not use for ordinary self-review or to implement fixes."
  echo "rendered: $claude_skill"
  echo "rendered: $codex_skill"
}

cmd="${1:-}"; shift || true
case "$cmd" in
  list) grep -v '^#' "$models" ;;
  add|remove)
    family="${1:?family}"; shift
    [[ "$family" == claude || "$family" == openai ]] || { echo "family must be claude or openai" >&2; exit 2; }
    [[ $# -gt 0 ]] || { echo "no names given" >&2; exit 2; }
    for name in "$@"; do
      if [[ "$cmd" == add ]]; then
        grep -qix "$family $name" "$models" || echo "$family $name" >> "$models"
      else
        grep -vix "$family $name" "$models" > "$models.tmp" && mv "$models.tmp" "$models"
      fi
    done
    touch "$models"
    render ;;
  render) render ;;
  ack) touch "$models"; echo "acknowledged" ;;
  check)
    family="${1:?family}"
    [[ -f "$models" ]] || { echo "cross-review: model list missing at $models"; exit 0; }
    age=$(( ( $(date +%s) - $(stat -c %Y "$models") ) / 86400 ))
    [[ $age -ge $stale_days ]] || exit 0
    case "$family" in claude) label="Claude";; openai) label="OpenAI";; *) label="$family";; esac
    echo "cross-review reminder: the review-trigger model list ($models) was last updated $age days ago. You maintain its '$family' entries: $(names_for "$family"). Compare with the $label models that exist today. If any are missing, run '$dir/update-models.sh add $family <name>' for each and tell the user in one line what you added. If nothing is missing, run '$dir/update-models.sh ack'. Do not mention this if no change was needed." ;;
  ""|-h|--help) usage ;;
  *) usage >&2; exit 2 ;;
esac
