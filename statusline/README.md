# Status bars

Run `python3 statusline/install.py` from the repository root. Python 3.11 or later is required.

Claude shows a context meter, model, and folder. The meter is green below 60%, yellow below 80%, and red thereafter.
Unknown usage displays `--`. Set `NO_COLOR` to disable Claude colors.

Codex shows context used, model with reasoning effort, folder, and Git branch. Its native theme colors are enabled.
Codex controls its own status colors. The Claude thresholds do not configure Codex.

Restart Codex after installation. Claude reloads its settings automatically.
The installer preserves other settings and saves `.before-statusline` backups beside both configuration files.

Sources: [Claude status line](https://code.claude.com/docs/en/statusline) and
[Codex configuration](https://learn.chatgpt.com/docs/config-file/config-reference).
