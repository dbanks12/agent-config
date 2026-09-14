# agent-config

Shared instructions and skills for Claude Code and Codex. One source, both tools.

## Install

```sh
./install.sh          # link files into ~/.claude and ~/.codex
./install.sh --check  # report drift, change nothing
```

Replaced files go to `~/.local/state/agent-config/backups/`.

## Edit

Edit files in this repo and commit. The installed paths are symlinks, so changes apply at once.

## Layout

- `instructions/AGENTS.md` is the global instruction file for both tools.
- `skills/` holds shared skills.
- `cross-review/` holds the model list and script behind the review-with-* skills.
- `links` lists every managed symlink as `source target`.
