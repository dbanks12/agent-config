# Agent config

This file and the shared skills live in `dbanks12/agent-config`. Paths under `~/.claude` and `~/.codex` are symlinks into that repo. Edit there and commit. Link each skill into both tools unless it is tool-specific.

# Pull requests

Always create pull requests as drafts.

# Sandbox rule

When you launch Codex or Claude Code yourself, from a skill, a script, a pane, or a subprocess, keep its sandbox and approvals on.

- Never pass `--yolo`, `--dangerously-bypass-approvals-and-sandbox`, `--dangerously-bypass-hook-trust`, or `sandbox_mode="danger-full-access"` to Codex. Use `--sandbox read-only` for reviews and questions. Use `-a never -s workspace-write` for unattended work that edits files.
- Never pass `--dangerously-skip-permissions` to Claude Code. Use `--permission-mode plan` for read-only work.
- If the Codex sandbox fails to start (`bwrap: loopback: Failed RTM_NEWADDR`), stop and fix the host with `linux/install-codex-sandbox.sh`. Do not retry without the sandbox.

This rule is about processes you start. It does not change code that a project under review ships.

# Karpathy guidelines

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.

# All writing

Four selected instructions from Ylan Segal's Zinsser-inspired Claude configuration, quoted verbatim:

- Eliminate clutter and unnecessary words
- Ensure clarity and simplicity
- Strengthen unity and flow
- Focus on word choice and sentence structure

# Additional rules for technical writing

Use ASD-STE100-style Simplified Technical English for technical output. This rule applies to documentation, procedures, error messages, commit messages, runbooks, pull-request descriptions, and explanations of code.

- Keep instructions to 20 words or fewer. Keep descriptive sentences to 25 words or fewer.
- Put one instruction in each sentence. Put one topic in each paragraph.
- Use active voice. Name the actor.
- Use simple present, past, or future tense. Do not use the present perfect tense.
- Use commands in procedures.
- Put a condition before the related command.
- Do not use gerund clauses to join ideas. Use separate sentences.
- Use one word for one meaning. Use terminology consistently.
- Prefer plain words, such as `start` instead of `initiate` and `use` instead of `utilize`.
- Do not use noun clusters longer than three words. Break them up with prepositions.
- Do not use hedge stacks or marketing adjectives such as `robust`, `seamless`, or `simply`.
- Avoid semicolons. Use separate sentences.

**Examples** from Google's technical writing courses, quoted verbatim (CC BY 4.0):

- Active voice: "Read-only access is provided by MutableInput." → "MutableInput provides read-only access."
- Clear sentences: "The exception occurs when dividing by zero." → "Dividing by zero raises the exception."
- Short sentences: "This design document provides a detailed description of Project Frambus." → "This design document describes Project Frambus."
- Ambiguous pronouns: "Running the process configures permissions and generates a user ID. This lets users authenticate to the app." → Replacement for the second sentence: "This user ID lets users authenticate."
- Factual specificity: "Setting this flag makes the application run screamingly fast." → "Setting this flag makes the application run 225-250% faster."
- Paragraph openings: "Good opening sentences establish the paragraph's central point." Example: "A loop runs the same block of code multiple times."
- Audience awareness: "Match your vocabulary to your audience." Example: "The average Python programmer is unaware of manipulating memory or pointers."

**Realistic explanatory examples** — Julia Evans, verbatim title and code:

"Write good examples by starting with real code"

```python
tasks.sort(key=lambda task: task['completed_time'])
```

Apply these rules strictly to procedures, error messages, and step-by-step documentation. Use the same sentence discipline, without strict vocabulary limits, for READMEs, pull-request descriptions, and chat explanations. Do not change quotations or text that must match an existing file style.
