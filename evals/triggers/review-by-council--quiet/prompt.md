---
description: review-by-council should stay quiet (review-with-codex)
tags: [triggers, quiet]
runs: 3
max_turns: 6
timeout_seconds: 240
allowed_tools: [Read, Glob, Grep, Skill]
append_system_prompt: Commands and file edits are unavailable in this environment. Begin the task as you normally would. When you reach a step that needs a command or an edit, stop and state your next step in one sentence.
---

Have Codex review this branch.
