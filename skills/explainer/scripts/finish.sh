#!/usr/bin/env bash
# Narrate (or caption), build, and QA a job in one call, after its scenes and cues exist.
# Usage: finish.sh <abs work dir> narrated|captions [--long] [extra QA seconds...]
# narrated: reuses timings.json when it is newer than narration.json (narrate.sh already ran in the
# background), else runs narrate.sh. Exit 2 or 3 falls back to captions. Exit 4 stops: the request
# may be billed, so nothing resubmits. captions: strips the audio tags with jq and runs tts.ts
# --captions-only. --long passes on to both. Then build_page.py and qa.sh. Exits with qa.sh's status.
set -euo pipefail
[[ $# -ge 2 && "$1" == /* && ( "$2" == narrated || "$2" == captions ) ]] || { echo "usage: finish.sh <abs work dir> narrated|captions [--long] [seconds...]" >&2; exit 1; }
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
w=$1 mode=$2
shift 2
long=()
if [[ ${1:-} == --long ]]; then long=(--long); shift; fi

captions() {
  jq '.scenes[].text |= (gsub("\\[[a-z ]+\\]\\s*"; "") | gsub("\\s+"; " ") | ltrimstr(" ") | rtrimstr(" "))' \
    "$w/narration.json" > "$w/narration.captions.json"
  bun "$here/tts.ts" "$w/narration.captions.json" "$w" --captions-only "${long[@]}"
}

if [[ $mode == narrated ]]; then
  if [[ -f "$w/timings.json" && "$w/timings.json" -nt "$w/narration.json" ]] && jq -e '.audio' "$w/timings.json" >/dev/null; then
    echo "finish: reusing the narration in timings.json"
  else
    status=0
    "$here/narrate.sh" "$w/narration.json" "$w" "${long[@]}" || status=$?
    if [[ $status -eq 4 ]]; then
      echo "finish: narration outcome unknown and may be billed. Do not resubmit; tell the user." >&2
      exit 4
    elif [[ $status -ne 0 ]]; then
      echo "finish: narration failed (exit $status), falling back to captions. Tell the user." >&2
      captions
    fi
  fi
else
  captions
fi
python3 "$here/build_page.py" "$w"
exec "$here/qa.sh" "$w" "$@"
