---
name: holocron
description: Publish an HTML page to the user's local holocron server instead of as a claude.ai Artifact, and reply with its localhost link. Use when the user asks for a holocron, or asks for another skill's output (an explainer, a teach-me page, a PR guide) as a holocron.
---

# Holocron

A holocron is a local stand-in for an Artifact. One server on this host serves every page on one port. The user forwards that port to their laptop once, so each link works with no new setup.

- Each page lives in `~/holocron/<slug>/`, and its link is `http://localhost:7777/<slug>/`.
- The index at `http://localhost:7777/` lists the pages. The user selects pages there, or selects all pages older than N days, and deletes them.
- The `holocron` command publishes, lists, and deletes pages. Run `holocron --help` for its usage.

## Make a holocron

1. Build the page as a folder with `index.html` and its supporting files, in your scratchpad. A single HTML file also works.
   - Design the page as you would an Artifact. In Claude Code, load `artifact-design` for the design rules, and skip its publishing steps.
   - The page gets no `window.claude` runtime and no Artifact capabilities. For saved state, use `localStorage` for one viewer's conveniences only.
   - Refer to supporting files by relative paths, such as `narration.mp3`. A path that starts with `/` points outside the page folder.
   - For another skill's output, such as an explainer, run that skill. Replace its Artifact publish step with step 3.
2. Pick the slug: a short kebab-case name for the subject, such as `zk-money-card`. To update a page, reuse its slug, so its link stays the same. Run `holocron list` to see the slugs.
3. Publish: `holocron publish <folder-or-file> --slug <slug>`. The command replaces the slug's old files and prints the link. The index shows the page's `<title>`. Pass `--title` to override it.
4. Check the link: `curl -sf -o /dev/null <link> && echo ok`. If the check fails, run `systemctl --user status holocron`. Start the server with `systemctl --user start holocron`.
5. Reply with the link. Name the slug. When the user asks for it in their Notes, post the link there.

The page is done when `curl` gets the link and the reply gives it.

## Setup

Do these steps once per host. Run them only when the server is missing.

1. Run `./install.sh` in `~/projects/agent-config`. It links the skill, `~/.local/bin/holocron`, and the user service.
2. Run `systemctl --user daemon-reload`, then `systemctl --user enable --now holocron`.
3. On the laptop, add `LocalForward 7777 localhost:7777` to the host's entry in `~/.ssh/config`.

## Limits

- The server listens on `127.0.0.1` only. The SSH tunnel is the only way to reach it from another machine. Every user with a shell on this host can read the pages.
- The server sends byte ranges, so audio and video seek correctly.
- `HOLOCRON_PORT` and `HOLOCRON_ROOT` override the port and the folder. Set the same values for the service and the command.
- Pages stay until the user deletes them. Delete a page only when the user asks.
