#!/usr/bin/env python3
"""Add data-id attributes to an Excalidraw SVG export, so explainer scenes can animate elements by id.

Usage: tag_svg.py <scene.excalidraw> <scene.svg> <out.svg> [--strip-fonts]

The export drops element ids. It writes one top-level <g> per live element, in scene order,
after a background <rect>; arrows add a sibling <mask>. This script pairs the two lists and
fails when their lengths differ, so a renderer change never mislabels an element.

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
        elements = [e for e in json.load(f)["elements"] if not e.get("isDeleted")]
    tree = ET.parse(svg_path)
    groups = [c for c in tree.getroot() if c.tag == f"{{{SVG}}}g"]
    if len(groups) != len(elements):
        sys.exit(f"tag_svg: {len(elements)} live elements but {len(groups)} top-level <g>; re-export with render --format svg")
    for el, g in zip(elements, groups):
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
