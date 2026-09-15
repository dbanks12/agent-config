#!/usr/bin/env python3
"""Install local status bars without replacing unrelated settings."""

import json
from pathlib import Path
import re
import shutil
import tomllib

root = Path(__file__).resolve().parent
home = Path.home()
claude = home / ".claude/settings.json"
codex = home / ".codex/config.toml"

settings = json.loads(claude.read_text()) if claude.exists() else {}
settings["statusLine"] = {
    "type": "command",
    "command": 'python3 "$HOME/.claude/statusline.py"',
    "padding": 0,
}

config = codex.read_text() if codex.exists() else ""
items = ["context-used", "model-with-reasoning", "current-dir", "git-branch"]
entries = "status_line = " + json.dumps(items) + "\nstatus_line_use_colors = true\n"
match = re.search(r"(?m)^\[tui\]\s*\n", config)
if match:
    start = match.end()
    next_table = re.search(r"(?m)^\[", config[start:])
    end = start + next_table.start() if next_table else len(config)
    section = config[start:end]
    section = re.sub(r"(?m)^status_line(?:_use_colors)?\s*=.*\n?", "", section)
    config = config[:start] + entries + section + config[end:]
else:
    config += "\n[tui]\n" + entries
parsed = tomllib.loads(config)
assert parsed["tui"]["status_line"] == items

for path in (claude, codex):
    path.parent.mkdir(parents=True, exist_ok=True)
    backup = path.with_name(path.name + ".before-statusline")
    if path.exists() and not backup.exists():
        shutil.copy2(path, backup)

link = home / ".claude/statusline.py"
target = root / "claude.py"
if not link.is_symlink() or link.resolve() != target:
    if link.exists() or link.is_symlink():
        raise SystemExit(f"Status script already exists: {link}")
    link.symlink_to(target)
claude.write_text(json.dumps(settings, indent=2) + "\n")
codex.write_text(config)
print("Installed Claude and Codex status bars. Restart Codex to load its bar.")
