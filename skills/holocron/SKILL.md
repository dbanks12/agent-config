---
name: holocron
description: Publish an HTML page to the user's local holocron server instead of as a claude.ai Artifact, and reply with its tailnet link. Use when the user asks for a holocron, or asks for another skill's output (an explainer, a teach-me page, a PR guide) as a holocron.
---

# Holocron

A holocron is a local stand-in for an Artifact. One server on this host serves every page on one port to the user's tailnet, so each link opens on the user's laptop and phone with no setup.

- Each page lives in `~/holocron/<slug>/`. Its link is `http://<tailscale name>:7777/<slug>/`, which `holocron publish` prints.
- The index at `/` lists the pages. The user selects pages there, or selects all pages older than N days, and deletes them.
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
3. Make sure that Tailscale runs on this host and on the user's devices.

## Limits

- The server answers this host and tailnet addresses (`100.64.0.0/10`) only. Every device on the tailnet, and every user with a shell on this host, can read the pages. Tailscale ACLs can limit the devices.
- The server refuses a `Host` header that is not an IP address, `localhost`, a MagicDNS short name, or a `.ts.net` name. This check stops DNS rebinding.
- The server sends byte ranges, so audio and video seek correctly.
- `HOLOCRON_PORT` and `HOLOCRON_ROOT` override the port and the folder. Set the same values for the service and the command. `HOLOCRON_URL` overrides the link base, which comes from `tailscale status`.
- Pages stay until the user deletes them. Delete a page only when the user asks.
