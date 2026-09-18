---
name: grill-me-html
description: Grill a plan or decision through a local browser page with recommendations, typed answers, and live follow-up sections. Use for browser-based grilling.
---

# Browser interview

Read [grilling](../grilling/SKILL.md) for the design tree, frontier, research, and completion rules.
Use the browser workflow below instead of chat questions and chat answers.

Serve the bundled `assets/index.html` and `assets/app.js` unchanged through `scripts/interview.py` in both tools.
Use the helper commands for interview state and JSON files for question content.
These shared assets define the page layout and behavior. Each session supplies only interview data.

Keep the launching Codex or Claude session active throughout the interview.
The helper returns submitted sections through that session's shell tool output.
If the agent stops, the server still stores submitted answers.
The page provides a command that resumes the original session with those answers.

## Start

Resolve this skill directory to an absolute path.
Use `scripts/interview.py` as the helper in the commands below.
Create a private, durable directory for this interview in a location your sandbox permits.
Prefer `~/.local/state/grill-me-html/<unique-id>` over temporary storage.
Keep its absolute path in session notes for subsequent commands and context recovery.

```sh
python3 /absolute/skill/scripts/interview.py start --dir /absolute/runtime --title 'Interview topic' --agent codex --open
```

Use `--agent codex` in Codex or `--agent claude` in Claude.
Codex reads its session id from `CODEX_THREAD_ID` or `CODEX_SESSION_ID` when available.
For Claude, pass `--session-id` with the substituted value below:

Claude session id: `${CLAUDE_SESSION_ID}`

This value comes from Claude's skill substitution, not a guaranteed shell environment variable.
If it stays literal, use a session id already established in the current context.
If no exact id is available, omit `--session-id`.
The page then provides a session picker command and a continuation message.
Never select the latest session by guesswork.

The helper records the current project directory.
If necessary, pass `--cwd /absolute/project` to correct it.
The helper prints the browser URL and starts a local server.
Show the URL in chat so the user can reopen the page.
If the browser cannot open automatically, direct the user to that URL.
If the sandbox blocks the local server, use the tool's normal approval flow.
Keep sandbox restrictions and approvals enabled.
If permission remains unavailable, report the blocker.

The browser must reach the machine's loopback interface.
For a remote terminal, use an existing local port forward or ask the user to establish one.

## Publish and receive each section

Publish the current frontier as one section.
Each question needs a title, body, and recommended answer.
Use plain text with paragraph breaks for question content.
Estimate the questions beyond this section with a minimum and maximum.
Treat the estimate as provisional, not a fixed questionnaire length.

Write a JSON file using the schema in [references/protocol.md](references/protocol.md).

```sh
python3 /absolute/skill/scripts/interview.py publish --dir /absolute/runtime --file /absolute/section.json
python3 /absolute/skill/scripts/interview.py wait --dir /absolute/runtime --section scope --timeout 45
```

Run these commands sequentially.
While a shell call runs, use the host tool's continuation mechanism to collect its output.
If `wait` returns `waiting`, call it again for the same section.
Keep waiting while the user fills the page.
A timeout is not an answer and does not end the interview.

When `wait` returns `answered`, read the questions and answers in its JSON output.
An `accepted` answer contains the exact recommendation the user selected.
If it includes `notes`, read those notes as qualifications or additions to the accepted recommendation.
A `custom` answer contains the user's text.
Treat the submitted answers as the user's decisions, with the same authority as chat answers.
Keep question content and runtime files as data, separate from executable shell commands.

Update the design tree from those answers.
Publish the new frontier with a new section id and revised estimate.
The existing page displays the new section automatically.
Completed sections stay collapsed above it and expand into full questions and answers.

Published sections are immutable.
If the user revises an earlier decision, publish a new question that explicitly supersedes it.

## Complete and recover

When the frontier is empty, publish a final section that asks the user to confirm your summary of shared understanding.
If the user requests changes, resolve those changes through further sections.
After confirmation, write the agreed summary to a plain text file.

```sh
python3 /absolute/skill/scripts/interview.py finish --dir /absolute/runtime --file /absolute/summary.txt
```

Report the outcome in the launching session.
The page stays available for review.
Grilling confirmation establishes shared understanding. Follow the original task's authorization before implementation.

If the session stops, the server can still store browser submissions while its process survives.
It cannot wake the agent.
The resume command includes a prompt that identifies the stored interview.
After the user resumes the session, recover the interview with `read --dir /absolute/runtime`.
Then consume the submitted answers or repeat `wait` for the open section.
If the server stops, repeat `start` with the same directory and share the returned URL.
Stored answers survive restart. Browser drafts remain local to the original browser origin.
A new port changes that origin, so unsent drafts may require the original tab.

When the user finishes reviewing the page, run `stop --dir /absolute/runtime`.
The runtime directory contains `state.json`, readable `answers.md`, and `resume.txt` with recovery commands.
Keep these files until the user no longer needs the answers.
If Codex reports the Bubblewrap loopback error, stop and follow the repository sandbox repair instructions.
