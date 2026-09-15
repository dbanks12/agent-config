#!/usr/bin/env bash
# Print the Fable weekly usage as a whole-number percent, or "unknown".
# Lives in agent-config/cross-review. Called by claude.sh and the review-by-council skill.
#
#   fable-usage.sh          -> prints e.g. 96, exit 0
#   fable-usage.sh --near   -> exit 0 if usage is at or above the limit below, 1 if below, 2 if unknown
#
# Reads the Claude Code OAuth token from ~/.claude/.credentials.json and asks the
# usage endpoint for the limit scoped to the model named Fable. Never prints the token.
set -uo pipefail

limit_percent=90
creds="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/.credentials.json"

percent="$(python3 - "$creds" 2>/dev/null <<'PY'
import json, sys, urllib.request
try:
    tok = json.load(open(sys.argv[1]))["claudeAiOauth"]["accessToken"]
    req = urllib.request.Request(
        "https://api.anthropic.com/api/oauth/usage",
        headers={"Authorization": "Bearer " + tok, "anthropic-beta": "oauth-2025-04-20",
                 "Content-Type": "application/json", "User-Agent": "agent-config/cross-review"})
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.load(r)
    for lim in data.get("limits") or []:
        model = ((lim.get("scope") or {}).get("model") or {}).get("display_name") or ""
        if model.lower() == "fable" and lim.get("percent") is not None:
            print(int(lim["percent"])); sys.exit(0)
except Exception:
    pass
print("unknown")
PY
)"
percent="${percent:-unknown}"

if [[ "${1:-}" == --near ]]; then
  [[ "$percent" == unknown ]] && exit 2
  [[ "$percent" -ge "$limit_percent" ]] && exit 0
  exit 1
fi
echo "$percent"
