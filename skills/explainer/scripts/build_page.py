#!/usr/bin/env python3
"""Assemble page.html (and explainer.html, the teach-me fragment) from a work dir.

Usage: build_page.py <work dir>

Reads from the work dir:
  timings.json   from tts.ts. Audio tags are stripped from the words and scene texts here.
  page.json      {"title": "...", "lede": "..."}
  style.css      optional, appended after assets/xp.css (the player's styles, scoped to .xp)
  Then one of:
  cues.json      Excalidraw look: [[scene, element id, "show" | "draw", word, nth?], ...]. Inlines
                 scenes/<id>.tagged.svg. The element appears as the voice reaches the nth use (default 1)
                 of the word inside that scene. "draw" draws an arrow on; "show" fades a box and its label in.
  stage.html + scenes.js
                 Any other look: stage.html holds the [data-scene] divs; scenes.js defines
                 `const SCENES = { s1: (el, local, p, t) => {...}, ... }`, with TIMINGS and Explainer in scope.
"""
import json
import re
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
TAG = re.compile(r"^\[[a-z ]+\]$")


def norm(w):
    return re.sub(r"[\W_]", "", w.lower())


def fail(msg):
    sys.exit(f"build_page: {msg}")


def excalidraw_stage(w, tm):
    cues = json.loads((w / "cues.json").read_text())
    words = tm["words"]
    scenes = {s["id"]: s for s in tm["scenes"]}
    spec = {s["id"]: [] for s in tm["scenes"]}
    for item in cues:
        sid, el, kind, word, nth = (item + [1])[:5]
        if sid not in scenes:
            fail(f"cue {item}: no scene {sid}")
        if kind not in ("show", "draw"):
            fail(f"cue {item}: kind must be show or draw")
        s = scenes[sid]
        hits = [i for i, x in enumerate(words) if norm(x["w"]) == norm(word)]
        inside = [i for i in hits if s["start"] <= words[i]["s"] < s["end"]]
        if len(inside) < nth:
            said = " ".join(sorted({norm(x["w"]) for x in words if s["start"] <= x["s"] < s["end"]}))
            fail(f"cue {item}: '{word}' is said {len(inside)} times in {sid}. Words in {sid}: {said}")
        # The player's cue() counts uses across the whole script.
        spec[sid].append([el, kind, norm(word), hits.index(inside[nth - 1])])
    divs = []
    for n, s in enumerate(tm["scenes"]):
        f = w / "scenes" / f"{s['id']}.tagged.svg"
        if not f.exists():
            fail(f"missing {f}; run render_scenes.sh")
        svg = re.sub(r"<\?xml[^>]*>", "", f.read_text()).strip()
        if n > 0:
            # Every export embeds the full font set (about 250 KB). Inline SVGs share one copy.
            svg = re.sub(r'<style class="style-fonts".*?</style>', "", svg, flags=re.S)
        svg = svg.replace("<svg ", f'<svg role="img" aria-label="{esc(s["title"])}" ', 1)
        for el, *_ in spec[s["id"]]:
            if f'data-id="{el}"' not in svg:
                fail(f"cue element {el} is not in {f.name}")
        divs.append(f'<div data-scene="{s["id"]}" aria-label="{esc(s["title"])}" hidden>{svg}</div>')
    script = (SKILL / "scripts" / "cue_scenes.js").read_text().replace("%SPEC%", json.dumps(spec))
    return "\n".join(divs), script


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace('"', "&quot;")


def main():
    if len(sys.argv) != 2:
        fail("usage: build_page.py <work dir>")
    w = Path(sys.argv[1]).resolve()
    tm = json.loads((w / "timings.json").read_text())
    tm["words"] = [x for x in tm["words"] if not TAG.match(x["w"])]
    for s in tm["scenes"]:
        s["text"] = re.sub(r"\s+", " ", re.sub(r"\[[a-z ]+\]", " ", s["text"])).strip()
    meta = json.loads((w / "page.json").read_text())

    if (w / "cues.json").exists():
        stage, scenes_js = excalidraw_stage(w, tm)
    elif (w / "stage.html").exists() and (w / "scenes.js").exists():
        stage, scenes_js = (w / "stage.html").read_text(), (w / "scenes.js").read_text()
    else:
        fail("need cues.json (Excalidraw look) or stage.html + scenes.js")
    ids = set(re.findall(r'data-scene="([^"]+)"', stage))
    missing = [s["id"] for s in tm["scenes"] if s["id"] not in ids]
    if missing:
        fail(f"no [data-scene] div for {', '.join(missing)}")

    audio = f'<audio class="xp-audio" src="{tm["audio"]}" preload="metadata"></audio>' if tm.get("audio") else ""
    css = (w / "style.css").read_text() if (w / "style.css").exists() else ""
    section = (SKILL / "assets" / "section.html").read_text()
    # Substituted in this order, so text from one source can never land in another's placeholder.
    section = section.replace("%STAGE%", stage).replace("%AUDIO%", audio)
    section = section.replace("%TIMINGS%", json.dumps(tm).replace("<", "\\u003c"))
    section = section.replace("%PLAYER%", (SKILL / "player.js").read_text())
    section = section.replace("%SCENES%", scenes_js)
    base_css = (SKILL / "assets" / "xp.css").read_text()
    (w / "explainer.html").write_text(f"<style>\n{base_css}\n{css}\n</style>\n{section}")
    page = (SKILL / "assets" / "page.html").read_text()
    for k, v in (("%TITLE%", esc(meta["title"])), ("%LEDE%", esc(meta.get("lede", "")))):
        page = page.replace(k, v)
    page = page.replace("%CSS%", base_css + "\n" + css).replace("%SECTION%", section)
    (w / "page.html").write_text(page)
    print(f"build_page: page.html {len(page)} bytes, {len(tm['scenes'])} scenes, {len(tm['words'])} words")


if __name__ == "__main__":
    main()
