#!/usr/bin/env bash
# Install the Ubuntu AppArmor exception required by system Bubblewrap.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
profile="$root/agent-config-bwrap"
destination=/etc/apparmor.d/agent-config-bwrap

[[ $EUID -ne 0 ]] || { echo "Run this script as the normal Codex user. It uses sudo for installation." >&2; exit 2; }
[[ "$(readlink -f "$(command -v bwrap)")" == /usr/bin/bwrap ]] || {
  echo "This profile requires Bubblewrap at /usr/bin/bwrap." >&2
  exit 2
}
command -v codex >/dev/null
command -v python3 >/dev/null
apparmor_parser --skip-kernel-load --skip-cache "$profile"
sudo install -o root -g root -m 0644 "$profile" "$destination"
sudo apparmor_parser --replace "$destination"
python3 "$root/test-codex-sandbox.py"
