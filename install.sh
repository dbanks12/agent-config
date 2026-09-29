#!/usr/bin/env bash
# Link each entry in ./links into place, then run check.sh. --check reports drift and links nothing.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
backups="${XDG_STATE_HOME:-$HOME/.local/state}/agent-config/backups/$(date -u +%Y%m%d-%H%M%S)"
check=0; failed=0; backed_up=0

[[ "${1:-}" == --check ]] && check=1 && shift
[[ $# -eq 0 ]] || { echo "usage: $0 [--check]" >&2; exit 2; }

link() {
  local src="$root/$1" dst="${2/#\~/$HOME}"
  [[ -e "$src" ]] || { echo "missing source: $src" >&2; failed=1; return; }
  [[ -L "$dst" && "$(readlink -f "$dst")" == "$(readlink -f "$src")" ]] && return
  if [[ $check -eq 1 ]]; then echo "drift: $dst" >&2; failed=1; return; fi
  mkdir -p "$(dirname "$dst")"
  if [[ -e "$dst" || -L "$dst" ]]; then
    mkdir -p "$backups/$(dirname "${dst#"$HOME"/}")"
    mv "$dst" "$backups/${dst#"$HOME"/}"
    backed_up=1
  fi
  ln -s "$src" "$dst"
  echo "linked: $dst -> $src"
}

# skills from other repos (for example vendor/claude-authoring-tools) are submodules
[[ $check -eq 1 ]] || git -C "$root" submodule update --init --quiet

while read -r src dst; do
  [[ -z "$src" || "$src" == \#* ]] && continue
  link "$src" "$dst"
done < "$root/links"

[[ $backed_up -eq 1 ]] && echo "backups: $backups"
git -C "$root" config core.hooksPath hooks
"$root/check.sh" || failed=1
exit $failed
