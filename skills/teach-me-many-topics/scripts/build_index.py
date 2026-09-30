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
            for r in it.get("resources", []):
                if not r.get("title") or not str(r.get("url", "")).startswith("https://"):
                    fail("item %r has a resource without a title and an https url" % slug)
    return sum(len(g["items"]) for g in m["groups"])


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


# A published artifact serves files beside the page without the page's document
# skeleton, so each local page gets its own head. Each also gets a link back to
# the index, whose URL the index saves in browser storage when it loads.
HEAD = ('<!doctype html>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n')
NAV_MARK = "<!-- teach-set-nav -->"
NAV = NAV_MARK + """
<nav id="setBack" hidden style="max-width:1100px;margin:0 auto;padding:12px 16px 0;font:13px/1.4 ui-monospace,monospace;">
  <a href="#" style="color:var(--accent,inherit);">&larr; Course index</a>
</nav>
<script>(function(){try{var u=localStorage.getItem("teach-index-url:%s");
if(u){var n=document.getElementById("setBack");n.querySelector("a").href=u;n.hidden=false;}}catch(e){}})();</script>
"""


def prepare_pages(m, directory):
    n = 0
    for g in m["groups"]:
        for it in g["items"]:
            if it["url"].startswith("https://"):
                continue
            page = directory / it["url"]
            if not page.is_file():
                fail("page %s for item %r is missing; build it first" % (page, it["slug"]))
            html = page.read_text(encoding="utf-8")
            if NAV_MARK not in html:
                cut = html.find("</style>")
                cut = cut + len("</style>") if cut != -1 else 0
                html = html[:cut] + "\n" + NAV % m["key"] + html[cut:]
            if not html.lstrip().lower().startswith("<!doctype"):
                html = HEAD + html
            page.write_text(html, encoding="utf-8")
            n += 1
    return n


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
                "summary": it.get("summary", ""),
                "resources": [{"title": r["title"], "url": r["url"]}
                              for r in it.get("resources", [])],
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
    pages = prepare_pages(m, Path(out_path).parent)
    print("wrote %s: %d items in %d groups; prepared %d local pages"
          % (out_path, total, len(m["groups"]), pages))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("manifest")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    build(a.manifest, a.out)


if __name__ == "__main__":
    main()
