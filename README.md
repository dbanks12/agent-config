# agent-config

Shared instructions and skills for Claude Code and Codex. One source, both tools.

## Install

```sh
./install.sh          # link files into ~/.claude and ~/.codex
./install.sh --check  # report drift, change nothing
```

Replaced files go to `~/.local/state/agent-config/backups/`.

For Ubuntu Bubblewrap errors in Codex, see [Linux sandbox setup](linux/README.md).
To clean `/tmp` and stop leaked build processes, see [Linux cleanup](linux/cleanup/README.md).

`check.sh` enforces the skill pattern. `install.sh` runs it and installs it as the git pre-commit hook.

## Dependencies

`install.sh` links files and initializes the submodules. It installs no tools. Install these on a new machine before you run it.

### Core

These are required for `install.sh`, the hooks, and the cross-model skills.

| Tool | Used by | Install (Ubuntu / macOS) |
|---|---|---|
| bash, git, GNU coreutils (`timeout`, `stat -c`) | `install.sh`, `cross-review/*.sh` | Preinstalled / `brew install coreutils bash`, then put `$(brew --prefix)/opt/coreutils/libexec/gnubin` first on `PATH` |
| Access to the private repo `dbanks12/claude-authoring-tools` | `install.sh` submodule init | An SSH key on the GitHub account |
| Python 3.11 or later, standard library only | Most skill scripts, `statusline/install.py` | `sudo apt install python3` / `brew install python` |
| jq | `claude-hooks/*.sh` | `sudo apt install jq` / `brew install jq` |
| `gh`, logged in, with the `gh stack` extension | `create-pr` | Install from [cli.github.com](https://cli.github.com), then `gh auth login` and `gh extension install github/gh-stack` |
| `claude` and `codex` CLIs, logged in | `call-claude`, `call-codex`, `review-*`, `review-by-council` | `npm i -g @anthropic-ai/claude-code @openai/codex` |
| bubblewrap with the AppArmor profile (Ubuntu only) | The Codex sandbox | `./linux/install-codex-sandbox.sh`. See [Linux sandbox setup](linux/README.md) |

`install.sh` does not register the Claude Code hooks. Add them to `~/.claude/settings.json` by hand, with this repo's absolute path:

```json
"hooks": {
  "PreToolUse": [
    {
      "matcher": "Bash",
      "hooks": [
        { "type": "command", "command": "bash <repo>/claude-hooks/block-pattern-kills.sh", "timeout": 10 }
      ]
    }
  ]
}
```

### Per skill

A skill without a row needs nothing beyond the core tools.

| Skill | Needs | Install (Ubuntu / macOS) |
|---|---|---|
| `excalidraw-skill` | Node.js with `npx`. The first canvas command fetches `mcp-excalidraw-server@2.1.2` | [nvm](https://github.com/nvm-sh/nvm), then `nvm install --lts` / `brew install node` |
| `slide-deck` | Node.js, Pillow, and Chromium or Google Chrome for PDF output | `pip install --user --break-system-packages pillow` / `pip3 install pillow`. Install Chrome from google.com/chrome |
| `explainer` | Bun. Narrated mode also needs `ffprobe` (from ffmpeg) and an ElevenLabs key. The Excalidraw look needs Node.js | `npm i -g bun`, then `sudo apt install ffmpeg` / `brew install bun ffmpeg`. For the key, follow "Key setup" in [the skill](skills/explainer/SKILL.md) |
| `slack-read` | A Slack user token in `SLACK_TOKEN`, with the scopes listed in [the skill](skills/slack-read/SKILL.md) | Create a Slack app and export the token in your shell profile |
| `hunk-review`, `hunk-extensions` | The `hunk` CLI. Extensions also need Bun | `npm i -g hunkdiff@0.22.0` |
| `herdr` | Herdr 0.9.0, run with `HERDR_ENV=1` | See [herdr-scrollback](linux/herdr-scrollback/README.md) for the full terminal setup |

To check the core tools, run:

```sh
for t in git jq gh claude codex python3 node npx bun ffprobe; do command -v "$t" >/dev/null || echo "missing: $t"; done
gh extension list | grep -q gh-stack || echo "missing: gh stack"
```

## Edit

Edit files in this repo and commit. The installed paths are symlinks, so changes apply at once.

## Settings

`~/.codex/config.toml` and `~/.claude/settings.json` are regular local files. This repo does not track them.
Both tools write local state into these files, such as the paths of trusted projects.
Credentials, sessions, and caches also stay outside this repo.

## Layout

- `instructions/AGENTS.md` is the global instruction file for both tools.
- `skills/` holds shared skills. Link each into both tools unless it is tool-specific.
- `cross-review/` holds the model list, the runner scripts (`claude.sh`, `codex.sh`), and `fable-usage.sh`, which reads the weekly Fable limit so the Claude runner and the council fall back to Opus at 90 percent.
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

## Imported Hunk skills

`hunk-review` and `hunk-extensions` come from the [hunkdiff](https://github.com/modem-dev/hunk) npm package at version `0.22.0`.
Each copied skill includes the upstream MIT license.
`hunk skill path` prints the bundled source. Copy it again after a Hunk upgrade.

## Narrated explainers

`explainer` builds a narrated, animated explainer page. It runs standalone, inside a `teach-me` page, or as a companion to a slide deck. It comes from the `explainer` skill in [alejoamiras/aa-skills](https://github.com/alejoamiras/aa-skills/tree/main/skills/explainer) at commit `b5b5b53`, used with the author's permission. `player.js`, `scripts/tts.ts`, and `scripts/narrate.sh` are upstream copies with two comment fixes. `SKILL.md` drops the upstream `blueprint` coupling. It adds the hosts, the Excalidraw look, and `scripts/tag_svg.py`.

Captions mode needs only Bun. Narration also needs `ffprobe` and an ElevenLabs key in `~/.config/elevenlabs/.env`. See [Dependencies](#per-skill).

## Slide decks and diagrams

`slide-deck` builds an HTML deck and a PDF from a Markdown `slides.md` file. `excalidraw-skill` drives a live Excalidraw canvas. The deck skill draws its figures on that canvas, crops them, and inlines them into the slides.

`slide-deck` lives in [dbanks12/claude-authoring-tools](https://github.com/dbanks12/claude-authoring-tools), a private repo. `excalidraw-skill` lives in its own repo, [dbanks12/excalidraw-skill](https://github.com/dbanks12/excalidraw-skill). This repo pins them as the submodules `vendor/claude-authoring-tools` and `vendor/excalidraw-skill`, and `links` points at the skills inside them. `./install.sh` initializes the submodules. To update one, run `git -C vendor/<name> pull origin <default branch>` and commit the new pointer. The default branch is `master` for `claude-authoring-tools` and `main` for `excalidraw-skill`.

Deck repos pin the same tool repo as their own `slidegen/` submodule and build in CI. See `vendor/claude-authoring-tools/skills/slide-deck/README-ci.md`. `examples/demo-deck` in that repo shows every feature.

For their tools, see [Dependencies](#per-skill). The canvas CLI runs as `npx -y mcp-excalidraw-server <command>` and starts the canvas server at `http://127.0.0.1:3000`. Screenshots and image exports render headless. Only Mermaid conversion needs a browser tab open at that URL.

Optional: register the canvas as an MCP server. For Codex, run `codex mcp add excalidraw -- npx -y mcp-excalidraw-server`. The CLI works without it.

To disable the two skills, comment out their four lines in `links` and delete the four symlinks in `~/.claude/skills` and `~/.codex/skills`.
