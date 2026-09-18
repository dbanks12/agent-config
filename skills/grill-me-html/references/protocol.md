# Section protocol

Publish a JSON object with this shape:

```json
{
  "id": "scope",
  "title": "Scope and workflow",
  "remaining": {"min": 3, "max": 6},
  "questions": [
    {
      "id": "location",
      "title": "Where should the interview run?",
      "body": "A local page can return answers to this active session.\n\nDoes that fit your workflow?",
      "recommendation": "Use a local browser page while this session stays active."
    }
  ]
}
```

Section ids must be unique across the interview.
Question ids must be unique within each section.
All question fields must contain text.
Remaining estimates count questions after the published section.
Use integer estimates with `0 <= min <= max`.
Only one section can await answers at a time.

The `wait` command returns one of these results:

```json
{"status": "waiting", "section": "scope"}
```

```json
{
  "status": "answered",
  "section": {
    "id": "scope",
    "title": "Scope and workflow",
    "questions": ["The original question objects appear here."],
    "answers": {
      "location": {
        "mode": "accepted",
        "text": "Use a local browser page while this session stays active."
      }
    }
  }
}
```

Custom responses use `"mode": "custom"` with the user's text.
Repeated waits return the same submitted section without consuming it.
Use a new section id for each follow-up.
The `read` command returns the complete interview state, including every submitted answer.

The server binds to `127.0.0.1` on a free port.
Each interview uses a private URL token and private files.
Treat the URL and runtime directory as private interview data.
Anyone with local access to the URL can read and submit answers.
The browser sends answers only when the user clicks **Send section to agent**.
Unsubmitted drafts stay in browser storage.
The server rejects submissions larger than 1 MiB.

Run helper tests with:

```sh
python3 -B -m unittest discover -s skills/grill-me-html/tests -p 'test_*.py'
```

Run browser tests with an installed Playwright package:

```sh
node skills/grill-me-html/tests/browser.cjs
```

If Playwright is outside the module search path, set `NODE_PATH` to its parent directory.
If its default browser is unavailable, set `CHROMIUM_PATH` to a compatible Chromium executable.

## Session recovery

The helper saves session recovery commands in `resume.txt` and the browser page.
The command uses the recorded project directory and exact session id when available.
It supplies a continuation prompt that tells the agent to read stored answers.
Without a session id, the command opens a picker and the page supplies a message to paste.

Codex commands explicitly use `workspace-write` with `on-request` approvals.
Claude commands explicitly use manual permissions and enable its sandbox.
The helper only displays these commands. The user runs them when needed.

The local CLI help verifies the resume flags.
[Codex documentation](https://learn.chatgpt.com/docs/codex/cli) describes session resumption.
[Claude skill documentation](https://code.claude.com/docs/en/skills#available-string-substitutions) documents substitution of the current session id.
