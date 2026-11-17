#!/usr/bin/env bash
# Copy the skills and instructions into the personal Capy Drive. Run it in a Capy thread. --check reports drift and copies nothing.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
host_only="herdr rdr migrdr hunk-review hunk-extensions slack-read"   # need this host's terminal tools, or Capy has its own
marker="<!-- Written by agent-config/install-capy.sh. Edit instructions/ in that repo, then run the script again. -->"
usage="usage: $0 [--check] [--drive <dir>]"
check=0; drive=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --check) check=1 ;;
    --drive) [[ $# -ge 2 ]] || { echo "$usage" >&2; exit 2; }; drive="$2"; shift ;;
    *) echo "$usage" >&2; exit 2 ;;
  esac
  shift
done

if [[ -z "$drive" ]]; then
  drives=("$HOME"/.capy/drive/user-*/)
  [[ ${#drives[@]} -eq 1 && -d "${drives[0]}" ]] || { echo "install-capy: no single personal drive in ~/.capy/drive. Run it in a Capy thread, or pass --drive <dir>." >&2; exit 2; }
  drive="${drives[0]}"
fi
drive="$(cd "$drive" && pwd)"

# Skills name sibling skills by their ~/.claude/skills path. Point those paths at the drive copy.
rel="${drive#"$HOME"}"
if [[ "$rel" != "$drive" ]]; then tilde="~$rel"; dollar="\$HOME$rel"; else tilde="$drive"; dollar="$drive"; fi

stage="$(mktemp -d)"
trap 'rm -rf "$stage"' EXIT
[[ $check -eq 1 ]] || git -C "$root" submodule update --init --recursive --quiet

# Every skill that links installs into ~/.claude or ~/.codex, under the same name, except host_only.
mkdir -p "$stage/skills"
re='^~/\.(claude|codex)/skills/([^/]+)$'
while read -r src dst _; do
  [[ "$dst" =~ $re ]] || continue
  name="${BASH_REMATCH[2]}"
  case " $host_only " in *" $name "*) continue ;; esac
  [[ -e "$stage/skills/$name" ]] || cp -a "$root/$src" "$stage/skills/$name"
done < "$root/links"
find "$stage" \( -name .git -o -name node_modules -o -name __pycache__ -o -name '*.pyc' \) -prune -exec rm -rf {} +
{ find "$stage/skills" -type f -exec grep -lIE '(~|\$HOME)/\.claude/skills/' {} + || true; } | while IFS= read -r f; do
  sed -i.capy-bak -e "s#~/\.claude/skills/#$tilde/skills/#g" -e "s#\\\$HOME/\.claude/skills/#$dollar/skills/#g" "$f"
  rm "$f.capy-bak"
done

# AGENTS.md is the drive's instructions. instructions/ keeps relative links such as teach-me's working.
mkdir -p "$stage/instructions"
cp "$root/instructions/AGENTS.md" "$root/instructions/writing-sources.md" "$stage/instructions/"
{ printf '%s\n\n' "$marker"; cat "$root/instructions/AGENTS.md"; printf '\n'; cat "$root/instructions/capy.md"; } > "$stage/AGENTS.md"

names=$(ls "$stage/skills")
manifest="$drive/.agent-config-skills"   # skills that the last install wrote, so a renamed or dropped skill is removed
stale=""
for n in $host_only $(cat "$manifest" 2>/dev/null || true); do
  [[ -d "$drive/skills/$n" && ! -d "$stage/skills/$n" && " $stale " != *" $n "* ]] && stale+=" $n"
done

if [[ $check -eq 1 ]]; then
  failed=0
  for n in $names; do diff -rq "$stage/skills/$n" "$drive/skills/$n" >/dev/null 2>&1 || { echo "drift: skills/$n" >&2; failed=1; }; done
  for n in $stale; do echo "drift: skills/$n is not in the Capy set" >&2; failed=1; done
  for f in AGENTS.md instructions; do diff -rq "$stage/$f" "$drive/$f" >/dev/null 2>&1 || { echo "drift: $f" >&2; failed=1; }; done
  exit $failed
fi

if [[ -f "$drive/AGENTS.md" && "$(head -n 1 "$drive/AGENTS.md")" != "$marker" ]]; then
  echo "install-capy: $drive/AGENTS.md holds other instructions. Move them into this repo or aside, then run again." >&2
  exit 1
fi
for n in $stale; do rm -rf "${drive:?}/skills/$n"; echo "removed: skills/$n"; done
mkdir -p "$drive/skills"
for n in $names; do rm -rf "${drive:?}/skills/$n"; cp -a "$stage/skills/$n" "$drive/skills/$n"; done
rm -rf "${drive:?}/instructions"
cp -a "$stage/instructions" "$drive/instructions"
cp "$stage/AGENTS.md" "$drive/AGENTS.md"
printf '%s\n' $names > "$manifest"
echo "installed: AGENTS.md and $(wc -w <<< "$names" | tr -d ' ') skills in $drive"
