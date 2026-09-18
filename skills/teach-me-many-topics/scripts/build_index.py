#!/usr/bin/env python3
"""Build the index page for a teach-me-many-topics set from a manifest.

Usage:
    python3 build_index.py MANIFEST.json --out INDEX.html

The manifest schema lives in ../references/manifest.md.
Run it again after any manifest edit, then republish to the same artifact URL.
"""
import argparse
import json
import re
import sys
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parents[1] / "assets" / "index-template.html"
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]*$")
# A published page carries an https URL. A local set carries a relative path
# beside the index, such as "btree.html" or "pages/btree.html".
LOCAL = re.compile(r"^[A-Za-z0-9._-]+(?:/[A-Za-z0-9._-]+)*\.html$")


def fail(msg):
    print("build_index: %s" % msg, file=sys.stderr)
    sys.exit(1)


def validate(m):
    if not isinstance(m.get("groups"), list) or not m["groups"]:
        fail("manifest needs a non-empty groups list")
    if not m.get("title"):
        fail("manifest needs a title")
    if not SLUG.match(m.get("key", "")):
        fail("manifest needs a key: lowercase letters, digits and hyphens")

    seen = set()
    for g in m["groups"]:
        if not g.get("name"):
            fail("every group needs a name")
        items = g.get("items")
        if not isinstance(items, list) or not items:
            fail("group %r needs a non-empty items list" % g["name"])
        for it in items:
            slug = it.get("slug", "")
            if not SLUG.match(slug):
                fail("bad slug %r in group %r" % (slug, g["name"]))
            if slug in seen:
                fail("duplicate slug %r; a slug keys one item's saved status" % slug)
            seen.add(slug)
            if not it.get("title"):
                fail("item %r needs a title" % slug)
            url = it.get("url", "")
            if not (url.startswith("https://") or LOCAL.match(url)):
                fail("item %r needs an https url or a relative .html path beside "
                     "the index; build or publish the page first" % slug)
    return sum(len(g["items"]) for g in m["groups"])


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def build(manifest_path, out_path):
    m = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    total = validate(m)
    html = TEMPLATE.read_text(encoding="utf-8")

    payload = json.dumps({
        "key": m["key"],
        "groups": [{
            "name": g["name"],
            "note": g.get("note", ""),
            "core": bool(g.get("core", False)),
            "items": [{
                "slug": it["slug"],
                "title": it["title"],
                "desc": it.get("desc", ""),
                "url": it["url"],
                "tag": it.get("tag", ""),
            } for it in g["items"]],
        } for g in m["groups"]],
    }, ensure_ascii=False)
    # A literal </script> inside the data would close the page script early.
    payload = payload.replace("</", "<\\/")

    html = html.replace("/*{{MANIFEST}}*/{\"groups\":[]}", payload)
    for marker, value in (("{{TITLE}}", m["title"]),
                          ("{{EYEBROW}}", m.get("eyebrow", "")),
                          ("{{LEDE}}", m.get("lede", "")),
                          ("{{FOOTNOTE}}", m.get("footnote", ""))):
        html = html.replace(marker, esc(value))

    left = sorted(set(re.findall(r"\{\{[A-Z_]+\}\}", html)))
    if left:
        fail("unreplaced markers: " + ", ".join(left))

    Path(out_path).write_text(html, encoding="utf-8")
    print("wrote %s: %d items in %d groups" % (out_path, total, len(m["groups"])))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("manifest")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    build(a.manifest, a.out)


if __name__ == "__main__":
    main()
