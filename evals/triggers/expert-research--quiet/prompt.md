---
description: expert-research should stay quiet (routine docs lookup)
tags: [triggers, quiet]
runs: 3
max_turns: 6
timeout_seconds: 240
allowed_tools: [Read, Glob, Grep, Skill]
append_system_prompt: Commands and file edits are unavailable in this environment. Begin the task as you normally would. When you reach a step that needs a command or an edit, stop and state your next step in one sentence.
---

What's the Alembic command to apply one migration?
