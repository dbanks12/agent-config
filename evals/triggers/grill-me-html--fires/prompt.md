---
description: grill-me-html should fire on natural phrasing
tags: [triggers, fires]
runs: 3
max_turns: 6
timeout_seconds: 240
allowed_tools: [Read, Glob, Grep, Skill]
append_system_prompt: Commands and file edits are unavailable in this environment. Begin the task as you normally would. When you reach a step that needs a command or an edit, stop and state your next step in one sentence.
---

Grill me on my plan to move cron jobs to a queue, in a browser page I can type answers into.
