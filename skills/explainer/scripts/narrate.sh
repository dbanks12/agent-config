#!/usr/bin/env bash
# The only sanctioned way to run tts.ts with the ElevenLabs key (the key-file exception in SKILL.md).
# Usage: narrate.sh <abs narration.json> <abs out-dir> [--long]
set -euo pipefail

[[ ( $# -eq 2 || ( $# -eq 3 && "$3" == --long ) ) && "$1" == /* && "$2" == /* ]] ||
  { echo "usage: narrate.sh <abs narration.json> <abs out-dir> [--long]" >&2; exit 1; }

# The user never wants a whispered narration. Refuse before the key is read or anything is sent.
if grep -qi '\[whisper' "$1"; then
  echo "narrate.sh: $1 has a whisper tag. Remove every [whisper...] tag, then narrate again." >&2
  exit 1
fi

dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
keyfile="${ELEVENLABS_ENV_FILE:-$HOME/.config/elevenlabs/.env}"
bun="$(command -v bun)"
# Absolute, and checked before anything is sent: without it a bad alignment cannot be rescued.
ffprobe="$(command -v ffprobe)" || { echo "narrate.sh: ffprobe not found (install ffmpeg)" >&2; exit 1; }
# --long joins several requests' audio.
ffmpeg=""
if [[ $# -eq 3 ]]; then ffmpeg="$(command -v ffmpeg)" || { echo "narrate.sh: ffmpeg not found" >&2; exit 1; }; fi
# env -i drops inherited BUN_OPTIONS, NODE_OPTIONS and the like. bun gets an empty HOME and cwd, so no
# global or local bunfig, preload or .env loads; tts.ts reads the key from the file itself, so the key is
# never in this script, an argv or an inherited environment.
empty="$(mktemp -d)"
trap 'rm -rf "$empty"' EXIT
cd "$empty"
env -i HOME="$empty" XDG_CONFIG_HOME="$empty" PATH="/usr/bin:/bin" TMPDIR="${TMPDIR:-/tmp}" \
  EXPLAINER_KEY_FILE="$keyfile" EXPLAINER_FFPROBE="$ffprobe" EXPLAINER_FFMPEG="$ffmpeg" \
  "$bun" --no-env-file "$dir/scripts/tts.ts" "$@"
