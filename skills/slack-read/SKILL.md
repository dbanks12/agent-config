---
name: slack-read
description: Read Slack channel history and threads as plain text through the Slack Web API, with permalinks. Use when the user asks what was said in a Slack channel or thread, or to research a topic in Slack. Never use the browser for Slack.
---

# Slack read

Read Slack through `scripts/slack.py`. It needs `SLACK_TOKEN`, a user token with read scopes. Do not open Slack in a browser.

```sh
S=~/.claude/skills/slack-read/scripts/slack.py      # Codex: ~/.codex/skills/slack-read/scripts/slack.py
python3 $S channels obsidion                         # find a channel name and id
python3 $S history team-obsidion --since 14d > /tmp/obs.txt
python3 $S history team-oxide --since 2026-08-01 --until 2026-08-15
python3 $S thread 'https://aztecprotocol.slack.com/archives/C0ADAFFC25S/p1790264897310429'
```

- `history` prints each top-level message under a `=== <permalink>` line, with thread replies indented below it. The default window is the last 7 days.
- Write long output to a file in the scratchpad, then use `grep` on it. Read only the threads that matter.
- Cite threads by the `===` permalink.
- Pass `--json` for raw messages. Pass `--no-threads` to skip reply fetches on busy channels.

## Limits

- The token has no `search:read` scope, so there is no search. To find one person's messages, `grep` the history output for their name.
- The token cannot read DMs or group DMs.
- The script reads only. It never joins a channel. A `not_in_channel` error means the user must join the channel first.
- The script caches users and channels for one day in `~/.cache/slack-read`. Delete that directory to refresh them.
