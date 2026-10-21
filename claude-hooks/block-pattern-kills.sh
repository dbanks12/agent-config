#!/usr/bin/env bash
# Claude Code PreToolUse hook (Bash). Blocks `pkill` and `killall`.
# They match by name or command line, so they also stop other sessions' processes and live services.
# On 2026-10-17 an agent ran `pkill -f "sill_core serve"` to stop its test server and stopped the live Sill core.
# Kill by PID instead: `$!` of a process you started, or a PID you checked with `pgrep -af`.
cmd=$(jq -r '.tool_input.command // ""')
grep -Eq '(^|[;&|(]|\$\()[[:space:]]*((sudo|timeout[[:space:]]+[0-9.]+[smh]?|exec|command)[[:space:]]+)*(pkill|killall)([[:space:]]|$)' <<<"$cmd" || exit 0
reason="Blocked: pkill and killall match by name or command line, so they can stop processes of other sessions and live services such as the Sill core. Kill by PID: use \$! of a process you started, or run 'pgrep -af <pattern>', check each line, and then 'kill <pid>'."
jq -n --arg r "$reason" '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "deny", permissionDecisionReason: $r}}'
