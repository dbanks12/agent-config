#!/usr/bin/env bash
# Maintain the model-name list that the cross-tool skills trigger on, and
# regenerate the `description:` frontmatter line in each of their SKILL.md files.
# models format: <family> <name> [<cli-model>]. The runner scripts resolve
# <name> to <cli-model>; the description lists <name>.
set -euo pipefail

dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
models="$dir/models"
skills="$dir/../skills"
review_codex="$skills/review-with-codex/SKILL.md"
review_claude="$skills/review-with-claude/SKILL.md"
call_codex="$skills/call-codex/SKILL.md"
call_claude="$skills/call-claude/SKILL.md"
stale_days=30

usage() {
  cat <<USAGE
usage: update-models.sh <command>
  list                      show the current list
  add <family> <name> [<cli-model>]  add or replace a name (family: claude | openai) and re-render
  remove <family> <name>...          remove names and re-render
  render                             rewrite the description line in the four cross-tool SKILL.md files
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
  set_description "$review_codex" \
    "Run an independent, read-only Codex review of a code change, design, or document. Use whenever the user asks for a review, second opinion, or cross-model review from any non-Claude model or tool, named with or without a version number, including $openai. A bare family name means its latest version. Do not use for ordinary self-review or to implement fixes."
  set_description "$review_claude" \
    "Run an independent, read-only Claude review of a code change, design, or document. Use whenever the user asks for a review, second opinion, or cross-model review from any non-OpenAI model or tool, named with or without a version number, including $claude. A bare family name means its latest version. Do not use for ordinary self-review or to implement fixes."
  set_description "$call_codex" \
    "Call Codex (OpenAI) as a separate process for any task, not only reviews. Use when the user wants to ask, consult, or cross-call an OpenAI model or tool, named with or without a version number, including $openai. A bare family name means its latest version. Higher skills (review-with-codex, review-by-council) build on this one."
  set_description "$call_claude" \
    "Call Claude Code (Anthropic) as a separate process for any task, not only reviews. Use when the user wants to ask, consult, or cross-call a Claude model, or a fresh Claude process with no memory of this session, named with or without a version number, including $claude. A bare family name means its latest version. Higher skills (review-with-claude, review-by-council) build on this one."
  for f in "$review_codex" "$review_claude" "$call_codex" "$call_claude"; do echo "rendered: $f"; done
}

cmd="${1:-}"; shift || true
case "$cmd" in
  list) grep -v '^#' "$models" ;;
  add)
    family="${1:?family}"; name="${2:?name}"; cli="${3:-}"
    [[ "$family" == claude || "$family" == openai ]] || { echo "family must be claude or openai" >&2; exit 2; }
    # Upsert: an existing row is replaced so a cli-model can be attached later.
    grep -viE "^$family $name( |$)" "$models" > "$models.tmp" && mv "$models.tmp" "$models"
    echo "$family $name${cli:+ $cli}" >> "$models"
    touch "$models"
    render ;;
  remove)
    family="${1:?family}"; shift
    [[ "$family" == claude || "$family" == openai ]] || { echo "family must be claude or openai" >&2; exit 2; }
    [[ $# -gt 0 ]] || { echo "no names given" >&2; exit 2; }
    for name in "$@"; do
      grep -viE "^$family $name( |$)" "$models" > "$models.tmp" && mv "$models.tmp" "$models"
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
    echo "cross-review reminder: the review-trigger model list ($models) was last updated $age days ago. You maintain its '$family' entries: $(names_for "$family"). Compare with the $label models that exist today. If any are missing, run '$dir/update-models.sh add $family <name> <cli-model>' for each, where <cli-model> is the exact name the $label CLI accepts, and tell the user in one line what you added. If nothing is missing, run '$dir/update-models.sh ack'. Do not mention this if no change was needed." ;;
  ""|-h|--help) usage ;;
  *) usage >&2; exit 2 ;;
esac
