# Capy

This section reaches Capy only. `install-capy.sh` appends it to the copy of this file in the personal Capy Drive.

The skills run from copies in the personal drive. `install-capy.sh` makes the copies from `dbanks12/agent-config`, so edit the skills there and run the script again. A thread on the user's own computer can use that computer's tools, such as `~/.config/cross-review`, the `claude` and `codex` CLIs, `chatterbox-say`, and `sill-core`. A cloud machine has none of them.

- **Tool branches.** Where a skill branches between Claude Code and Codex and has no Capy branch, follow the Claude Code branch. A Capy subagent replaces the Agent tool. A background command that you wait on replaces Monitor.
- **Skill tool.** Where a skill invokes another skill with the Skill tool, read that skill's `SKILL.md` from your skill list.
- **Artifacts.** Capy has no Artifact tool, so skills write pages as local files. Attach a self-contained page to your reply. Capy shows it as a sandboxed page. Where a skill needs a link that other people can open, such as an explainer in a PR body, save the page under `pages/` in the personal drive. Then make a link with Capy's Drive share. The link stays private until the user shares it from Drive, like an Artifact.
- **Local servers.** Where a skill serves a page on `localhost`, give that URL in a thread on the user's own computer. On a cloud machine, publish the port as a preview and give the preview. To show a page that needs its folder, such as media or sibling pages, serve the folder with `python3 -m http.server` the same way.
