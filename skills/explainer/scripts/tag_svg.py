#!/usr/bin/env python3
"""Add data-id attributes to an Excalidraw SVG export, so explainer scenes can animate elements by id.

Usage: tag_svg.py <scene.excalidraw> <scene.svg> <out.svg> [--strip-fonts]

The export drops element ids. It writes one top-level <g> per live element after a background
<rect>; arrows add a sibling <mask>. The order is the renderer's: each element in scene order,
with a container's bound text drawn right after it instead of in its own place. This script
rebuilds that order, pairs it with the groups, and checks every text group's content, so a
renderer change fails loudly instead of mislabeling an element.

Every export embeds the full font set (about 250 KB). Inline SVGs share the page's CSS, so
--strip-fonts drops that block from every scene but one.
"""
import json
import sys
import xml.etree.ElementTree as ET

SVG = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG)
ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")


def main(scene_path, svg_path, out_path, strip_fonts):
    with open(scene_path) as f:
        live = [e for e in json.load(f)["elements"] if not e.get("isDeleted")]
    bound = {e["containerId"]: e for e in live if e.get("containerId")}
    elements = []
    for e in live:
        if not e.get("containerId"):
            elements.append(e)
            if e["id"] in bound:
                elements.append(bound.pop(e["id"]))
    elements += bound.values()  # text bound to a missing container keeps its own place
    tree = ET.parse(svg_path)
    groups = [c for c in tree.getroot() if c.tag == f"{{{SVG}}}g"]
    if len(groups) != len(elements):
        sys.exit(f"tag_svg: {len(elements)} live elements but {len(groups)} top-level <g>; re-export with render --format svg")
    squash = lambda s: "".join(s.split())
    for el, g in zip(elements, groups):
        if el["type"] == "text" and squash(el.get("text", "")) != squash("".join(g.itertext())):
            sys.exit(f"tag_svg: element {el['id']} text does not match its <g>; the renderer order changed")
        g.set("data-id", el["id"])
        if el.get("containerId"):
            g.set("data-container", el["containerId"])
    if strip_fonts:
        for defs in tree.getroot().iter(f"{{{SVG}}}defs"):
            for style in defs.findall(f"{{{SVG}}}style[@class='style-fonts']"):
                defs.remove(style)
    tree.write(out_path, encoding="unicode")
    print(f"tag_svg: tagged {len(groups)} elements")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--strip-fonts"]
    if len(args) != 3:
        sys.exit(__doc__.strip().splitlines()[2])
    main(*args, strip_fonts="--strip-fonts" in sys.argv)
