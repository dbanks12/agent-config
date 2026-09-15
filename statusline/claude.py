#!/usr/bin/env python3
"""Render Claude Code's context meter from status-line JSON."""

import json
import math
import os
from pathlib import Path
import sys


def render(data):
    def paint(text, color):
        return text if "NO_COLOR" in os.environ else f"\033[{color}m{text}\033[0m"

    def clean(value):
        return "".join(c for c in str(value) if c.isprintable())

    context = data.get("context_window") or {}
    percent = context.get("used_percentage")
    if percent is None:
        meter = paint("ctx ░░░░░░░░░░ --", "90")
    else:
        percent = max(0, min(100, float(percent)))
        filled = math.ceil(percent / 10)
        color = "32" if percent < 60 else "33" if percent < 80 else "31"
        meter = paint(f"ctx {'━' * filled}{'░' * (10 - filled)} {percent:.0f}%", color)
    parts = [meter]
    model = clean((data.get("model") or {}).get("display_name") or "Claude")
    parts.append(paint(model, "36"))
    directory = (data.get("workspace") or {}).get("current_dir") or data.get("cwd")
    if directory:
        parts.append(paint(clean(Path(directory).name or directory), "90"))
    return paint(" │ ", "90").join(parts)


if __name__ == "__main__":
    try:
        data = json.load(sys.stdin)
    except (ValueError, OSError):
        data = {}
    print(render(data))
