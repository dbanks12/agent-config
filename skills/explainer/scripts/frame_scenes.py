#!/usr/bin/env python3
"""Give consecutive Excalidraw scenes that share a part one frame, so the shared part stays in place.

Usage: frame_scenes.py <scenes dir> <id>...   (ids in story order)

Each export is cropped to its own drawing, so a box at the same canvas position lands in a different
place on screen once two scenes differ in size. A run of consecutive scenes that share a part name
(a box or diamond id without its scene prefix) gets the union of their canvas bounds as every
scene's viewBox. Only <id>.tagged.svg changes. Bounds come from the untouched <id>.svg, so a rerun
gives the same frames.
"""
import json
import re
import sys
import xml.etree.ElementTree as ET

SVG = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG)
ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")
SHAPES = {"rectangle", "diamond", "ellipse"}


def scene(d, sid):
    """Return (part names, canvas bounds x0, y0, x1, y1, offset ox, oy) of one scene."""
    with open(f"{d}/{sid}.excalidraw") as f:
        live = {e["id"]: e for e in json.load(f)["elements"] if not e.get("isDeleted")}
    parts = {i[len(sid) + 1:] for i, e in live.items() if e["type"] in SHAPES and i.startswith(sid + "-")}
    root = ET.parse(f"{d}/{sid}.tagged.svg").getroot()
    natural = ET.parse(f"{d}/{sid}.svg").getroot()
    _, _, w, h = map(float, natural.get("viewBox").split())
    # The export translates every element by one offset. Read it from the first shape: svg = canvas + offset.
    for g in root.iter(f"{{{SVG}}}g"):
        e = live.get(g.get("data-id"))
        m = re.match(r"translate\(([-\d.]+)[ ,]+([-\d.]+)\)", g.get("transform", ""))
        if e and e["type"] in SHAPES and m:
            ox, oy = float(m[1]) - e["x"], float(m[2]) - e["y"]
            return parts, (-ox, -oy, w - ox, h - oy), (ox, oy)
    sys.exit(f"frame_scenes: {sid} has no box to read its offset from")


def main(d, ids):
    info = {sid: scene(d, sid) for sid in ids}
    runs, run = [], [ids[0]]
    for a, b in zip(ids, ids[1:]):
        if info[a][0] & info[b][0]:
            run.append(b)
        else:
            runs.append(run)
            run = [b]
    runs.append(run)
    for run in runs:
        if len(run) < 2:
            continue
        x0 = min(info[s][1][0] for s in run)
        y0 = min(info[s][1][1] for s in run)
        x1 = max(info[s][1][2] for s in run)
        y1 = max(info[s][1][3] for s in run)
        for sid in run:
            ox, oy = info[sid][2]
            path = f"{d}/{sid}.tagged.svg"
            tree = ET.parse(path)
            root = tree.getroot()
            box = [x0 + ox, y0 + oy, x1 - x0, y1 - y0]
            root.set("viewBox", " ".join(f"{v:g}" for v in box))
            root.set("width", f"{box[2]:g}")
            root.set("height", f"{box[3]:g}")
            bg = next((c for c in root if c.tag == f"{{{SVG}}}rect"), None)
            if bg is not None:  # the export's background fills its own crop; stretch it over the frame
                for k, v in zip(("x", "y", "width", "height"), box):
                    bg.set(k, f"{v:g}")
            tree.write(path, encoding="unicode")
        print(f"frame_scenes: {' '.join(run)} share one frame ({', '.join(sorted(info[run[0]][0] & info[run[1]][0]))})")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit("usage: frame_scenes.py <scenes dir> <id>...")
    main(sys.argv[1], sys.argv[2:])
