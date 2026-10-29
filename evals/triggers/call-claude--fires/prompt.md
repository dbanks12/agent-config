---
description: call-claude should fire on natural phrasing
tags: [triggers, fires]
runs: 3
max_turns: 6
timeout_seconds: 240
allowed_tools: [Read, Glob, Grep, Skill]
append_system_prompt: Commands and file edits are unavailable in this environment. Begin the task as you normally would. When you reach a step that needs a command or an edit, stop and state your next step in one sentence.
---

Ask Opus what it thinks about using SQLite instead of Redis for our job queue.
