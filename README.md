# agent-config

Shared instructions and skills for Claude Code and Codex. One source, both tools.

## Install

```sh
./install.sh          # link files into ~/.claude and ~/.codex
./install.sh --check  # report drift, change nothing
```

Replaced files go to `~/.local/state/agent-config/backups/`.

For Ubuntu Bubblewrap errors in Codex, see [Linux sandbox setup](linux/README.md).

`check.sh` enforces the skill pattern. `install.sh` runs it and installs it as the git pre-commit hook.

## Edit

Edit files in this repo and commit. The installed paths are symlinks, so changes apply at once.

## Settings

`~/.codex/config.toml` links to `settings/codex.toml`.
`~/.claude/settings.json` links to `settings/claude.json`.
Edits through these links change the tracked files. Review the diff and commit it.
Credentials, sessions, and caches stay outside this repo.

If a tool replaces a symlink during a save, `./install.sh --check` reports drift.
Copy the changed settings into the matching repository file before you run `./install.sh` to restore the link.
The installer backs up the replaced local file.

## Layout

- `instructions/AGENTS.md` is the global instruction file for both tools.
- `skills/` holds shared skills. Link each into both tools unless it is tool-specific.
- `cross-review/` holds the model list, the runner scripts (`claude.sh`, `codex.sh`), and `fable-usage.sh`, which reads the weekly Fable limit so the Claude runner and the council fall back to Opus at 90 percent.
- `settings/` holds the complete Codex and Claude settings files, including machine-specific paths and trust entries.
- `links` lists every managed symlink as `source target`.
- `check.sh` verifies each skill has a valid SKILL.md, is in `links`, and links into every tool unless listed as tool-specific.
- Name a tool-specific skill `<purpose>-with-<tool>`, for example `review-with-codex`, so agents can find it by name.

## Cross-tool skills

Three layers. Each layer calls the one below it.

- `call-codex`, `call-claude`: run the other tool once as a separate process. Own the command line, model names, and effort levels. Two modes: a free `prompt`, or the tool's built-in `code-review`. Linked into both tools.
- `review-with-codex`, `review-with-claude`: review policy. Claude uses scoped prompts for code reviews. Codex uses built-in review with scope context. A design review prompt for everything else. Tool-specific.
- `review-by-council`: several seats in parallel (default fable, opus, astra, sol at high), then dedupe, verify each finding, report. Linked into both tools.

`cross-review/update-models.sh add <family> <name> [<cli-model>]` adds a trigger name and re-renders the skill descriptions.

## Browser interviews

Use `$grill-me-html` in Codex or `/grill-me-html` in Claude Code for a browser interview.
[The skill](skills/grill-me-html/SKILL.md) provides recommendation buttons, custom answers, question navigation, changing estimates, and collapsed section history.
Submitted answers return to the launching session and remain on disk with a readable transcript and resume commands.

## Imported Pocock skills

Eight skills come from [mattpocock/skills](https://github.com/mattpocock/skills) at commit `74ca5fe077456a0b3b2f5310cf9430999fd0b5fd`.
Each copied skill includes the upstream MIT license.

- `grill-me`, `handoff`, `to-questionnaire`, and `wait-what` retain upstream explicit invocation.
- `grilling` and `writing-for-agents` retain automatic discovery.
- `tdd` and `code-review` require explicit invocation in both tools.

Use `$skill-name` in Codex or `/skill-name` in Claude Code.
The `grill-me` and `handoff` instructions support agents without a Skill tool.
TDD includes the upstream codebase-design documents as local references.
Code review uses existing tracker guidance or a supplied spec without requiring the upstream setup skill.
