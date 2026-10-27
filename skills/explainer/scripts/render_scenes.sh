#!/usr/bin/env bash
# Draw, lint, render, and tag Excalidraw scenes in parallel, one private canvas per scene.
# Usage: render_scenes.sh <scenes dir> <id>...
# <scenes dir>/scenes.py <id> prints one scene's element JSON (place.py output). For each id this writes
# <id>.excalidraw, <id>.png, <id>.svg, <id>.tagged.svg, and <id>.lint, and tiles every PNG into sheet.jpg.
# It prints all lint problems at the end, and its last line names the scenes that failed lint.
# Rerun it with only the ids you changed. Every canvas server it starts is stopped on exit.
set -euo pipefail
[[ $# -ge 2 ]] || { echo "usage: render_scenes.sh <scenes dir> <id>..." >&2; exit 1; }

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
excalidraw="$(cd "$here/../../excalidraw-skill" && pwd -P)"
cd "$1"
shift
# Resolve the CLI once: each npx call costs about 1.5 s of CPU, and a batch makes six per scene.
cli="$(timeout 120 npx -y -p mcp-excalidraw-server@2.1.2 bash -c 'command -v mcp-excalidraw-server')"
x() { timeout 120 "$cli" "$@"; }
# A port the kernel just handed out is free. A fixed or random range can collide with another
# batch, and then one batch's stop kills the other's canvas, which restarts and never stops.
free_port() { python3 -c 'import socket; s = socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1])'; }

one() {  # one <id> <index>
  local id=$1 port
  port=$(free_port)
  (
    export PORT=$port EXPRESS_SERVER_URL=http://127.0.0.1:$port
    trap 'x stop >/dev/null 2>&1 || true' EXIT
    x clear --yes >/dev/null 2>&1 || true
    python3 scenes.py "$id" | x add >/dev/null
    x export --out "$id.excalidraw" >/dev/null
  )
  python3 "$excalidraw/scripts/lint_diagram.py" "$id.excalidraw" | grep -v '^OK' | sed "s/^/$id: /" > "$id.lint" || true
  x render "$id.excalidraw" --scale 1 --out "$id.png" >/dev/null &
  x render "$id.excalidraw" --format svg --out "$id.svg" >/dev/null
  wait
  python3 "$here/tag_svg.py" "$id.excalidraw" "$id.svg" "$id.tagged.svg"
}

i=0
pids=()
for id in "$@"; do
  one "$id" "$i" &
  pids+=($!)
  i=$((i + 1))
done
failed=0
for p in "${pids[@]}"; do wait "$p" || failed=1; done
[[ $failed -eq 0 ]] || { echo "render_scenes: a scene failed" >&2; exit 1; }

# 3 columns of 640x360 cells, in argument order.
inputs=() filters="" labels=""
for id in "$@"; do inputs+=(-i "$id.png"); done
for ((k = 0; k < $#; k++)); do
  filters+="[$k:v]scale=640:360:force_original_aspect_ratio=decrease,pad=640:360:-1:-1:white[c$k];"
  labels+="[c$k]"
done
cols=$(( $# < 3 ? $# : 3 ))
layout=""
for ((k = 0; k < $#; k++)); do layout+="$((k % cols * 640))_$((k / cols * 360))|"; done
if [[ $# -eq 1 ]]; then
  ffmpeg -loglevel error -y "${inputs[@]}" -filter_complex "${filters}[c0]null" sheet.jpg
else
  ffmpeg -loglevel error -y "${inputs[@]}" -filter_complex "${filters}${labels}xstack=inputs=$#:layout=${layout%|}:fill=gray" sheet.jpg
fi
# The lint lines come last, so a session that reads only the tail still sees them.
lint_failed=()
for id in "$@"; do
  cat "$id.lint"
  if grep -q FAIL "$id.lint"; then lint_failed+=("$id"); fi
done
echo "render_scenes: $# scenes, sheet.jpg, lint ${lint_failed[*]:+FAIL: }${lint_failed[*]:-clean}"
