#!/usr/bin/env bash
# Install Ubuntu's packaged Bubblewrap AppArmor profile.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
profile=/usr/share/apparmor/extra-profiles/bwrap-userns-restrict
destination=/etc/apparmor.d/bwrap-userns-restrict

[[ $EUID -ne 0 ]] || { echo "Run this script as the normal Codex user. It uses sudo for installation." >&2; exit 2; }
[[ "$(readlink -f "$(command -v bwrap)")" == /usr/bin/bwrap ]] || {
  echo "This profile requires Bubblewrap at /usr/bin/bwrap." >&2
  exit 2
}
command -v codex >/dev/null
command -v python3 >/dev/null
# A second profile attached to the same executable can break Bubblewrap.
while IFS= read -r existing; do
  [[ "$existing" == "$destination" ]] && continue
  echo "Check the existing Bubblewrap profile before installation: $existing" >&2
  exit 2
done < <(grep -rlF /usr/bin/bwrap /etc/apparmor.d)
sudo apt update
sudo apt install apparmor-profiles apparmor-utils
apparmor_parser --skip-kernel-load --skip-cache "$profile"
sudo install -o root -g root -m 0644 "$profile" "$destination"
sudo apparmor_parser --replace "$destination"
python3 "$root/test-codex-sandbox.py"
