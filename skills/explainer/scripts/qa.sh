#!/usr/bin/env bash
# Run qa.cjs with a pinned Playwright from the npx cache. Usage: qa.sh <work dir> [extra seconds...]
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# npx puts the package's bin dir on PATH. Its node_modules is two levels up, and NODE_PATH lets require() find it.
exec timeout 300 npx -y -p playwright@1.49.1 bash -c \
  'NODE_PATH="$(dirname "$(dirname "$(command -v playwright)")")" exec node "$0" "$@"' "$here/qa.cjs" "$@"
