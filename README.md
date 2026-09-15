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

## Layout

- `instructions/AGENTS.md` is the global instruction file for both tools.
- `skills/` holds shared skills. Link each into both tools unless it is tool-specific.
- `cross-review/` holds the model list and the runner scripts (`claude.sh`, `codex.sh`) behind the cross-tool skills.
- `links` lists every managed symlink as `source target`.
- `check.sh` verifies each skill has a valid SKILL.md, is in `links`, and links into every tool unless listed as tool-specific.
- Name a tool-specific skill `<purpose>-with-<tool>`, for example `review-with-codex`, so agents can find it by name.

## Cross-tool skills

Three layers. Each layer calls the one below it.

- `call-codex`, `call-claude`: run the other tool once as a separate process. Own the command line, model names, and effort levels. Two modes: a free `prompt`, or the tool's built-in `code-review`. Linked into both tools.
- `review-with-codex`, `review-with-claude`: review policy. Built-in code review for code. A design review prompt for everything else. Tool-specific.
- `review-by-council`: several seats in parallel (default fable, opus, astra, sol at high), then dedupe, verify each finding, report. Linked into both tools.

`cross-review/update-models.sh add <family> <name> [<cli-model>]` adds a trigger name and re-renders the skill descriptions.
