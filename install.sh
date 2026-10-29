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
  if [[ ! -e "$src" || ( -d "$src" && -z "$(ls -A "$src")" ) ]]; then
    [[ "$1" == vendor/* ]] && { echo "skipped: $dst (submodule not cloned)" >&2; return; }
    echo "missing source: $src" >&2; failed=1; return
  fi
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
# a submodule that fails to clone is skipped, with its links
if [[ $check -eq 0 ]]; then
  for sub in $(git -C "$root" config -f .gitmodules --get-regexp '\.path$' | awk '{print $2}'); do
    # nested submodules, such as repo-map's copy of pr-map, clone too when they can
    git -C "$root" submodule update --init --recursive --quiet -- "$sub" 2>/dev/null ||
      { git -C "$root" submodule update --init --quiet -- "$sub" &&
        echo "warning: $sub cloned, but not all of its nested submodules" >&2; } ||
      echo "warning: $sub did not clone, its skills are skipped" >&2
  done
fi

while read -r src dst; do
  [[ -z "$src" || "$src" == \#* ]] && continue
  link "$src" "$dst"
done < "$root/links"

[[ $backed_up -eq 1 ]] && echo "backups: $backups"
git -C "$root" config core.hooksPath hooks
"$root/check.sh" || failed=1
exit $failed
