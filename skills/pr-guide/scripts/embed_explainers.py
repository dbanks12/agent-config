#!/usr/bin/env python3
"""Put explainer videos on a pr-guide page: one "Watch the explainer" button for each stage.

Each video is the explainer skill's standalone page.html, played in a frame over the guide.
Run it again after a change to a video: it replaces what it added before."""
import json, re, sys
from pathlib import Path

STAGES = ["definitions", "codebase", "changes", "walkthrough", "wrapup"]
START, END = "<!-- explainers:start -->", "<!-- explainers:end -->"
PLAYER = """<div id="xp-modal" hidden role="dialog" aria-modal="true" aria-label="Explainer"><div class="box">
<button class="xp-open" id="xp-close" type="button">Close</button><iframe title="Explainer" allow="autoplay; fullscreen"></iframe></div></div>
<script>
(() => {
  const pages = JSON.parse(document.getElementById("xp-data").textContent)
  const modal = document.getElementById("xp-modal"), frame = modal.querySelector("iframe")
  const close = () => { modal.hidden = true; frame.srcdoc = "" }
  document.addEventListener("click", (e) => {
    const b = e.target.closest("[data-explain]")
    if (b) { frame.srcdoc = pages[b.dataset.explain]; modal.hidden = false }
    else if (e.target === modal || e.target.id === "xp-close") close()
  })
  document.addEventListener("keydown", (e) => { if (e.key === "Escape" && !modal.hidden) close() })
})()
</script>"""


def main():
    if len(sys.argv) < 3 or any("=" not in a for a in sys.argv[2:]):
        sys.exit(f"usage: {sys.argv[0]} <page.html> <stage>=<explainer work dir> ...")
    path = Path(sys.argv[1])
    page = path.read_text()
    # drop what an earlier run added
    page = re.sub(re.escape(START) + r".*?" + re.escape(END) + r"\n?", "", page, flags=re.S)
    page = re.sub(r'\n?[ \t]*<button class="xp-open" type="button" data-explain="[^"]*">.*?</button>', "", page)

    pages, files = {}, {}
    for arg in sys.argv[2:]:
        stage, work = arg.split("=", 1)
        if stage not in STAGES:
            sys.exit(f"unknown stage {stage}; use one of {', '.join(STAGES)}")
        work = Path(work).expanduser()
        src, timings = work / "page.html", work / "timings.json"
        if not src.exists() or not timings.exists():
            sys.exit(f"{stage}: no explainer page in {work}; run the explainer's finish.sh there")
        tm = json.loads(timings.read_text())
        html = src.read_text()
        if tm.get("audio"):
            # the frame resolves a relative src against the guide's URL, so each video's audio needs its own name
            name = f"explain-{stage}{Path(tm['audio']).suffix}"
            html = html.replace(f'src="{tm["audio"]}"', f'src="{name}"', 1)
            files[name] = str((work / tm["audio"]).resolve())
        pages[stage] = html
        secs = round(tm["duration"])
        button = (f'\n    <button class="xp-open" type="button" data-explain="{stage}">'
                  f'&#9654; Watch the explainer &middot; {secs // 60}:{secs % 60:02d}</button>')
        head = re.search(rf'(<section id="{stage}"[^>]*>\s*<h2[^>]*>.*?</h2>)', page, re.S)
        if not head:
            sys.exit(f"{stage}: no <section id=\"{stage}\"> with an <h2> on the page")
        page = page[:head.end()] + button + page[head.end():]

    data = json.dumps(pages).replace("</", "<\\/")
    block = f'{START}\n<script type="application/json" id="xp-data">{data}</script>\n{PLAYER}\n{END}\n'
    page = page.rstrip("\n") + "\n" + block
    path.write_text(page)
    for name, file in files.items():
        Path(path.parent / name).write_bytes(Path(file).read_bytes())
    print(f"added {len(pages)} explainers to {path}")
    if files:
        print("publish with files: " + json.dumps({n: str(path.parent / n) for n in files}))


if __name__ == "__main__":
    main()
