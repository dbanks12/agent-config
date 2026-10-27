#!/usr/bin/env python3
"""Example scenes/scenes.py for the Excalidraw look. `python3 scenes.py <id>` prints one scene's elements.

Diagram(<scene id>, title) prefixes every id with the scene id, so the ids below become s1-repo,
s1-repo--claude (an arrow), s1-repo--claude-label (its label), s2-rules, s2-rules-title, and so on.
cues.json names these full ids. Positions are top-left corners on a grid you choose: keep a scene
inside about 900 x 500 so it reads at 640 x 360, and 80-130 px between boxes.

place.py API (all positions in px, ids without the scene prefix):
  box(name, x, y, label, sub=None, fam="gray")   diamond(name, x, y, question, fam="blue")
  arrow(a, b, label=None, dashed=False, route="straight" | "elbow", via=[(x, y)])
  zone(name, x, y, w, h, title)   panel(name, x, y, title, [lines])   note(name, x, y, text)   start(name, x, y)
  fam: gray, blue, green, orange, purple, red, teal. A diamond doubles its label's size.
"""
import os
import sys

for skills in ("~/.claude/skills", "~/.codex/skills"):
    sys.path.insert(0, os.path.expanduser(f"{skills}/excalidraw-skill/scripts"))
from place import Diagram  # noqa: E402


def s1(d):
    d.box("repo", 0, 120, "agent-config repo", sub="one source of truth", fam="blue")
    d.box("claude", 420, 20, "~/.claude", fam="purple")
    d.box("codex", 420, 220, "~/.codex", fam="teal")
    d.arrow("repo", "claude", "symlink")
    d.arrow("repo", "codex", "symlink")


def s2(d):
    d.diamond("same", 0, 80, "already linked?")
    d.box("skip", 500, -20, "nothing to do", fam="green")
    d.box("backup", 500, 200, "move old file", sub="to backups/", fam="orange")
    d.arrow("same", "skip", "yes")
    d.arrow("same", "backup", "no")
    d.panel("rules", 0, 260, "Rules", ["never deletes", "--check only reports"])


SCENES = {"s1": ("One repo, two homes", s1), "s2": ("Each line, once", s2)}

if __name__ == "__main__":
    title, draw = SCENES[sys.argv[1]]
    d = Diagram(sys.argv[1], title)
    draw(d)
    d.emit()
