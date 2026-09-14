# agent-config

Shared instructions and skills for Claude Code and Codex. One source, both tools.

## Install

```sh
./install.sh          # link files into ~/.claude and ~/.codex
./install.sh --check  # report drift, change nothing
```

Replaced files go to `~/.local/state/agent-config/backups/`.

`check.sh` enforces the skill pattern. `install.sh` runs it and installs it as the git pre-commit hook.

## Edit

Edit files in this repo and commit. The installed paths are symlinks, so changes apply at once.

## Layout

- `instructions/AGENTS.md` is the global instruction file for both tools.
- `skills/` holds shared skills. Link each into both tools unless it is tool-specific.
- `cross-review/` holds the model list and script behind the review-with-* skills.
- `links` lists every managed symlink as `source target`.
- `check.sh` verifies each skill has a valid SKILL.md, is in `links`, and links into every tool unless listed as tool-specific.
- Name a tool-specific skill `<purpose>-with-<tool>`, for example `review-with-codex`, so agents can find it by name.
