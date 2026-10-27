#!/usr/bin/env python3
"""Build styles.html, the four-look style board, from board.json in a work dir.

Usage: build_board.py <work dir>

board.json:
  {"moment": {"title": "...", "caption": "the line spoken over it",
              "nodes": [{"id": "a", "label": "..."}, ...],       # 2-6 parts, in the order they appear
              "flow": [["a", "b", "label"], ...]},               # label optional
   "looks": [{"look": "excalidraw", "note": "how it feels and what it suits"}, ...]}  # exactly four

A look is a key of assets/board.js (excalidraw, swiss, terminal, cutout, phone, blueprint), or
{"look": "custom", "name": "...", "note": "...", "js": "<body of (m, t) => svg markup string>"} for
one direction the library lacks. Every preview loops the same 6-second moment.
"""
import json
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
NAMES = {"excalidraw": "Excalidraw sketch", "swiss": "Kinetic Swiss type", "terminal": "Retro terminal",
         "cutout": "Paper cut-out", "phone": "Phone and card", "blueprint": "Blueprint"}


def fail(msg):
    sys.exit(f"build_board: {msg}")


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace('"', "&quot;")


def main():
    if len(sys.argv) != 2:
        fail("usage: build_board.py <work dir>")
    w = Path(sys.argv[1]).resolve()
    b = json.loads((w / "board.json").read_text())
    m, looks = b["moment"], b["looks"]
    if len(looks) != 4:
        fail(f"need exactly four looks, got {len(looks)}")
    if not 2 <= len(m["nodes"]) <= 6:
        fail("the moment needs 2-6 nodes")
    ids = {n["id"] for n in m["nodes"]}
    for f in m.get("flow", []):
        if f[0] not in ids or f[1] not in ids:
            fail(f"flow {f} names a node that does not exist")
    m.setdefault("flow", [])
    if not any(x["look"] == "excalidraw" for x in looks):
        fail("Excalidraw sketch is always one of the four")
    if sum(x["look"] == "custom" for x in looks) > 1:
        fail("at most one custom look")
    cards = []
    for i, x in enumerate(looks):
        if x["look"] != "custom" and x["look"] not in NAMES:
            fail(f"unknown look {x['look']}; use one of {', '.join(NAMES)} or custom")
        name = x.get("name") or NAMES.get(x["look"], "Custom")
        cards.append(f'<figure class="card"><svg id="look-{i}" viewBox="0 0 640 360" role="img" aria-label="{esc(name)} preview"></svg>'
                     f'<figcaption><b>{chr(65 + i)}. {esc(name)}</b> {esc(x.get("note", ""))}</figcaption></figure>')
    page = (SKILL / "assets" / "board.html").read_text()
    page = page.replace("%TITLE%", esc(m["title"])).replace("%CARDS%", "\n".join(cards))
    page = page.replace("%BOARD%", json.dumps(b).replace("<", "\\u003c")).replace("%BOARDJS%", (SKILL / "assets" / "board.js").read_text())
    (w / "styles.html").write_text(page)
    print(f"build_board: styles.html, looks {', '.join(c.get('name') or NAMES.get(c['look'], 'custom') for c in looks)}")


if __name__ == "__main__":
    main()
