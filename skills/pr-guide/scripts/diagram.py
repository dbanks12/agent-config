#!/usr/bin/env python3
"""Draw a PR guide diagram with the excalidraw-skill, and put it on the page.

  diagram.py draw <scene.py>
      Runs the place.py scene on a private canvas. Writes <scene>.excalidraw, <scene>.png and <scene>.svg
      beside it, and prints the lint problems. Exit 1 when lint fails.
  diagram.py embed <page.html> <MARKER> <scene.svg> --label "<the diagram's claim>"
      Replaces {{MARKER}} on the page with the SVG. The page keeps one copy of the hand font.
"""
import argparse
import os
import re
import socket
import subprocess
import sys
from pathlib import Path

CLI = "mcp-excalidraw-server@2.1.2"
FONT_STYLE = re.compile(r'<style class="style-fonts">.*?</style>', re.S)


def excalidraw_skill() -> Path:
    for home in ("~/.claude/skills", "~/.codex/skills"):
        skill = Path(home).expanduser() / "excalidraw-skill"
        if skill.exists():
            return skill
    sys.exit("diagram: the excalidraw-skill is not installed")


def draw(scene: Path) -> int:
    out = scene.with_suffix("")
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    env = {**os.environ, "PORT": str(port), "EXPRESS_SERVER_URL": f"http://127.0.0.1:{port}"}

    def cli(*args, **kw):
        return subprocess.run(["npx", "-y", CLI, *args], env=env, timeout=120, check=True, capture_output=True, **kw)

    elements = subprocess.run([sys.executable, scene.name], cwd=scene.parent, check=True, capture_output=True).stdout
    try:
        cli("clear", "--yes")
        cli("add", input=elements)
        cli("export", "--out", f"{out}.excalidraw")
    finally:
        subprocess.run(["npx", "-y", CLI, "stop"], env=env, timeout=120, capture_output=True)
    cli("render", f"{out}.excalidraw", "--scale", "2", "--out", f"{out}.png")
    cli("render", f"{out}.excalidraw", "--format", "svg", "--out", f"{out}.svg")
    lint = subprocess.run(
        [sys.executable, str(excalidraw_skill() / "scripts/lint_diagram.py"), f"{out}.excalidraw"],
        capture_output=True, text=True,
    )
    print("\n".join(line for line in lint.stdout.splitlines() if line and not line.startswith("OK")))
    print(f"view {out}.png, then embed {out}.svg")
    return lint.returncode


def embed(page: Path, marker: str, svg_file: Path, label: str) -> int:
    html, svg = page.read_text(), svg_file.read_text()
    token = "{{" + marker + "}}"
    if html.count(token) != 1:
        sys.exit(f"diagram: {page} must hold {token} exactly once")
    font = FONT_STYLE.search(svg)
    svg = FONT_STYLE.sub("", svg[svg.index("<svg"):])
    svg = re.sub(r'^<svg([^>]*?)\s+width="[^"]*"\s+height="[^"]*"', r"<svg\1", svg, count=1)
    svg = svg.replace("<svg", f'<svg role="img" aria-label="{label.replace(chr(34), "&quot;")}"', 1)
    if font and 'id="sketch-font"' not in html:
        html = html.replace("<style", font.group(0).replace('class="style-fonts"', 'id="sketch-font"') + "\n<style", 1)
    page.write_text(html.replace(token, svg))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("draw").add_argument("scene", type=Path)
    e = sub.add_parser("embed")
    e.add_argument("page", type=Path)
    e.add_argument("marker")
    e.add_argument("svg", type=Path)
    e.add_argument("--label", required=True)
    args = parser.parse_args()
    if args.cmd == "draw":
        return draw(args.scene.resolve())
    return embed(args.page, args.marker, args.svg, args.label)


if __name__ == "__main__":
    sys.exit(main())
