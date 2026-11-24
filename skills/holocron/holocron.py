#!/usr/bin/env python3
"""Holocron: local pages served on one port, as a stand-in for claude.ai Artifacts.

Each page lives in ~/holocron/<slug>/ and is served at http://localhost:<port>/<slug>/.
The index at / lists every page and deletes the ones you select.

  holocron publish <file-or-dir> --slug <slug> [--title <title>]
  holocron list
  holocron delete <slug>...
  holocron serve
"""

import argparse
import datetime as dt
import html
import json
import os
import re
import shutil
import sys
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(os.environ.get("HOLOCRON_ROOT", Path.home() / "holocron"))
PORT = int(os.environ.get("HOLOCRON_PORT", "7777"))
META = ".holocron.json"
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{0,79}$")


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def check_slug(slug: str) -> str:
    if not SLUG.match(slug):
        raise ValueError(f"bad slug {slug!r}: use 1-80 lowercase letters, digits, and hyphens")
    return slug


def read_meta(page: Path) -> dict:
    try:
        meta = json.loads((page / META).read_text())
    except (OSError, ValueError):
        meta = {}
    stamp = dt.datetime.fromtimestamp(page.stat().st_mtime, dt.timezone.utc).isoformat(timespec="seconds")
    meta.setdefault("created", stamp)
    meta.setdefault("updated", meta["created"])
    meta.setdefault("title", page.name)
    meta["slug"] = page.name
    return meta


def pages() -> list[dict]:
    if not ROOT.is_dir():
        return []
    found = [read_meta(p) for p in ROOT.iterdir() if p.is_dir() and SLUG.match(p.name)]
    return sorted(found, key=lambda m: m["updated"], reverse=True)


def url(slug: str) -> str:
    return f"http://localhost:{PORT}/{slug}/"


def title_of(index: Path) -> str | None:
    m = re.search(r"<title[^>]*>(.*?)</title>", index.read_text(errors="replace"), re.S | re.I)
    return html.unescape(m.group(1).strip()) if m else None


def publish(src: Path, slug: str, title: str | None) -> str:
    check_slug(slug)
    src = src.resolve()
    if not src.exists():
        raise ValueError(f"{src} does not exist")
    page = ROOT / slug
    old = read_meta(page) if page.is_dir() else {}
    staging = ROOT / f".staging-{slug}"
    shutil.rmtree(staging, ignore_errors=True)
    if src.is_dir():
        shutil.copytree(src, staging)
    else:
        staging.mkdir(parents=True)
        shutil.copy2(src, staging / "index.html")
    if not (staging / "index.html").is_file():
        shutil.rmtree(staging)
        raise ValueError(f"{src} has no index.html")
    meta = {
        "title": title or title_of(staging / "index.html") or slug,
        "created": old.get("created", now()),
        "updated": now(),
    }
    (staging / META).write_text(json.dumps(meta, indent=2) + "\n")
    shutil.rmtree(page, ignore_errors=True)
    staging.rename(page)
    return url(slug)


def delete(slugs: list[str]) -> list[str]:
    gone = []
    for slug in slugs:
        page = ROOT / check_slug(slug)
        if page.is_dir():
            shutil.rmtree(page)
            gone.append(slug)
    return gone


INDEX = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Holocron</title>
<style>
:root { --bg: #f4f5f7; --card: #fff; --fg: #1b1f24; --muted: #5d6670; --line: #d5dae0; --accent: #2d5bd7; --danger: #c62828; color-scheme: light; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --bg: #15181c; --card: #1e2227; --fg: #e8ebee; --muted: #9aa3ad; --line: #30363d; --accent: #7fa2ff; --danger: #ff6b6b; color-scheme: dark; } }
:root[data-theme="dark"] { --bg: #15181c; --card: #1e2227; --fg: #e8ebee; --muted: #9aa3ad; --line: #30363d; --accent: #7fa2ff; --danger: #ff6b6b; color-scheme: dark; }
body { margin: 0; background: var(--bg); color: var(--fg); font: 16px/1.5 system-ui, sans-serif; padding: 28px 16px 48px; }
main { max-width: 900px; margin: 0 auto; display: grid; gap: 16px; }
h1 { margin: 0; font-size: 1.6rem; }
.bar { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; background: var(--card); border: 1px solid var(--line); border-radius: 8px; padding: 10px 12px; }
.bar input[type=number] { width: 4.5em; font: inherit; padding: 4px 6px; border: 1px solid var(--line); border-radius: 6px; background: var(--bg); color: var(--fg); }
button { font: 600 0.9rem system-ui, sans-serif; border-radius: 6px; padding: 6px 12px; cursor: pointer; border: 1px solid var(--line); background: var(--card); color: var(--fg); }
button.danger { background: var(--danger); border-color: var(--danger); color: #fff; }
button:disabled { opacity: 0.5; cursor: default; }
.count { color: var(--muted); font-size: 0.9rem; margin-left: auto; }
ul { list-style: none; margin: 0; padding: 0; display: grid; gap: 8px; }
li { display: grid; grid-template-columns: auto 1fr auto; gap: 12px; align-items: center; background: var(--card); border: 1px solid var(--line); border-radius: 8px; padding: 10px 12px; }
li a { color: var(--accent); font-weight: 600; text-decoration: none; overflow-wrap: anywhere; }
li a:hover { text-decoration: underline; }
.slug { color: var(--muted); font: 0.8rem ui-monospace, monospace; overflow-wrap: anywhere; }
.age { color: var(--muted); font-size: 0.85rem; white-space: nowrap; }
input[type=checkbox] { width: 18px; height: 18px; accent-color: var(--danger); }
.empty { color: var(--muted); }
</style></head>
<body><main>
<h1>Holocron</h1>
<div class="bar">
  <label><input type="checkbox" id="all"> All</label>
  <label>Older than <input type="number" id="days" min="0" value="7"> days</label>
  <button type="button" id="old">Select</button>
  <button type="button" id="del" class="danger" disabled>Delete selected</button>
  <span class="count" id="count"></span>
</div>
<ul id="list"></ul>
</main>
<script>
const list = document.getElementById("list"), del = document.getElementById("del"), count = document.getElementById("count");
const ageDays = (iso) => (Date.now() - Date.parse(iso)) / 86400000;
const ageText = (iso) => { const d = ageDays(iso); return d < 1 / 24 ? "just now" : d < 1 ? `${Math.round(d * 24)} h ago` : `${Math.floor(d)} d ago`; };
let items = [];
const boxes = () => [...list.querySelectorAll("input[type=checkbox]")];
function sync() {
  const n = boxes().filter((b) => b.checked).length;
  del.disabled = n === 0;
  del.textContent = n ? `Delete ${n} selected` : "Delete selected";
  count.textContent = `${items.length} page${items.length === 1 ? "" : "s"}`;
}
function draw() {
  list.replaceChildren(...items.map((p) => {
    const li = document.createElement("li");
    const box = document.createElement("input");
    box.type = "checkbox"; box.value = p.slug; box.setAttribute("aria-label", `Select ${p.title}`);
    const info = document.createElement("div");
    const a = document.createElement("a"); a.href = `/${p.slug}/`; a.textContent = p.title;
    const slug = document.createElement("div"); slug.className = "slug"; slug.textContent = p.slug;
    info.append(a, slug);
    const age = document.createElement("span"); age.className = "age"; age.title = `Updated ${p.updated}`; age.textContent = ageText(p.updated);
    li.append(box, info, age);
    return li;
  }));
  if (!items.length) list.innerHTML = '<li class="empty" style="display:block">No pages yet.</li>';
  sync();
}
async function load() { items = await (await fetch("/api/pages")).json(); draw(); }
list.addEventListener("change", sync);
document.getElementById("all").addEventListener("change", (e) => { boxes().forEach((b) => (b.checked = e.target.checked)); sync(); });
document.getElementById("old").addEventListener("click", () => {
  const days = Number(document.getElementById("days").value);
  const byslug = Object.fromEntries(items.map((p) => [p.slug, p]));
  boxes().forEach((b) => (b.checked = ageDays(byslug[b.value].updated) >= days));
  sync();
});
del.addEventListener("click", async () => {
  const slugs = boxes().filter((b) => b.checked).map((b) => b.value);
  if (!slugs.length || !confirm(`Delete ${slugs.length} page${slugs.length === 1 ? "" : "s"}? This cannot be undone.`)) return;
  const r = await fetch("/api/delete", { method: "POST", headers: { "Content-Type": "application/json", "X-Holocron": "1" }, body: JSON.stringify({ slugs }) });
  if (!r.ok) alert(`Delete failed: ${r.status} ${await r.text()}`);
  document.getElementById("all").checked = false;
  load();
});
load();
</script>
</body></html>
"""


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(ROOT), **kw)

    def log_message(self, fmt, *args):
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def local_host(self) -> bool:
        # A page on another site can make the browser send requests here. A Host header for
        # another name means DNS rebinding, so refuse it.
        host = (self.headers.get("Host") or "").rsplit(":", 1)[0]
        return host in ("localhost", "127.0.0.1", "[::1]")

    def send_body(self, status: int, body: bytes, ctype: str):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, value, status=HTTPStatus.OK):
        self.send_body(status, json.dumps(value).encode(), "application/json")

    def do_GET(self):
        if not self.local_host():
            return self.send_error(HTTPStatus.FORBIDDEN, "Use http://localhost")
        path = self.path.split("?", 1)[0]
        if path == "/":
            return self.send_body(HTTPStatus.OK, INDEX.encode(), "text/html; charset=utf-8")
        if path == "/api/pages":
            return self.send_json(pages())
        if path.startswith("/.") or "/." in path:
            return self.send_error(HTTPStatus.NOT_FOUND)
        if "Range" in self.headers:
            return self.send_range()
        return super().do_GET()

    def do_HEAD(self):
        if not self.local_host():
            return self.send_error(HTTPStatus.FORBIDDEN)
        super().do_HEAD()

    def send_range(self):
        # Media seeking needs partial content. SimpleHTTPRequestHandler always sends the whole file.
        fpath = Path(self.translate_path(self.path))
        if not fpath.is_file():
            return super().do_GET()
        size = fpath.stat().st_size
        m = re.match(r"bytes=(\d*)-(\d*)$", self.headers["Range"].strip())
        if not m or (not m.group(1) and not m.group(2)):
            return super().do_GET()
        if m.group(1):
            start, end = int(m.group(1)), int(m.group(2) or size - 1)
        else:
            start, end = max(0, size - int(m.group(2))), size - 1
        end = min(end, size - 1)
        if start > end:
            self.send_response(HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE)
            self.send_header("Content-Range", f"bytes */{size}")
            self.end_headers()
            return
        self.send_response(HTTPStatus.PARTIAL_CONTENT)
        self.send_header("Content-Type", self.guess_type(str(fpath)))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(end - start + 1))
        self.end_headers()
        with fpath.open("rb") as f:
            f.seek(start)
            left = end - start + 1
            while left > 0:
                chunk = f.read(min(1 << 16, left))
                if not chunk:
                    break
                self.wfile.write(chunk)
                left -= len(chunk)

    def do_POST(self):
        # The custom header and the JSON body force a CORS preflight, which this server never
        # answers, so other sites cannot delete pages.
        if not self.local_host() or self.headers.get("X-Holocron") != "1" or self.path != "/api/delete":
            return self.send_error(HTTPStatus.FORBIDDEN)
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", "0"))))
            self.send_json({"deleted": delete(list(body["slugs"]))})
        except (ValueError, KeyError, TypeError) as e:
            self.send_error(HTTPStatus.BAD_REQUEST, str(e))


def main():
    ap = argparse.ArgumentParser(prog="holocron", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("publish", help="copy a page (a file, or a dir with index.html) to a slug and print its URL")
    p.add_argument("src", type=Path)
    p.add_argument("--slug", required=True)
    p.add_argument("--title", help="index title; default is the page <title>")
    sub.add_parser("list", help="print each page: updated, URL, title")
    d = sub.add_parser("delete", help="delete pages by slug")
    d.add_argument("slugs", nargs="+")
    sub.add_parser("serve", help=f"serve {ROOT} on 127.0.0.1:{PORT}")
    args = ap.parse_args()
    try:
        if args.cmd == "publish":
            print(publish(args.src, args.slug, args.title))
        elif args.cmd == "list":
            for m in pages():
                print(f"{m['updated']}  {url(m['slug'])}  {m['title']}")
        elif args.cmd == "delete":
            for slug in delete(args.slugs):
                print(f"deleted {slug}")
        else:
            ROOT.mkdir(parents=True, exist_ok=True)
            ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
    except ValueError as e:
        sys.exit(f"holocron: {e}")


if __name__ == "__main__":
    main()
