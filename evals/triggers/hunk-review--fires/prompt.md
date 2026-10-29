---
description: hunk-review should fire on natural phrasing
tags: [triggers, fires]
runs: 3
max_turns: 6
timeout_seconds: 240
allowed_tools: [Read, Glob, Grep, Skill]
append_system_prompt: Commands and file edits are unavailable in this environment. Begin the task as you normally would. When you reach a step that needs a command or an edit, stop and state your next step in one sentence.
---

In my running Hunk session, add a comment on line 40 of src/app.ts saying it needs a null check.
