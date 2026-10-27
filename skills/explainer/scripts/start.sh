#!/usr/bin/env bash
# Open a job in one call: make the work dir, prepare it for codex.sh, and print what step 1 reads.
# Usage: start.sh <slug> <source file>...
# Creates ~/.local/share/explainers/<slug>/ with scenes/ and a Git repo (codex.sh needs a worktree),
# prints the style history of earlier jobs, then each source with line numbers.
set -euo pipefail
[[ $# -ge 2 && "$1" =~ ^[a-z0-9-]{1,60}$ ]] || { echo "usage: start.sh <slug> <source file>..." >&2; exit 1; }
w="$HOME/.local/share/explainers/$1"
shift
mkdir -p "$w/scenes"
git -C "$w" init -q 2>/dev/null || true
echo "== work dir: $w"
echo "== style history"
for m in "$HOME"/.local/share/explainers/*/manifest.json; do
  [[ -f "$m" && "$m" != "$w/manifest.json" ]] && jq -c '{style, style_verdict, styles_offered}' "$m" 2>/dev/null
done
for f in "$@"; do
  echo "== $f ($(wc -l < "$f") lines)"
  cat -n "$f"
done
