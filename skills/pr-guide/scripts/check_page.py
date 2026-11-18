#!/usr/bin/env python3
"""Check a pr-guide page: its five stages, its snippets, and its links between stages."""
import argparse, json, re, sys
from pathlib import Path

STAGES = ["definitions", "codebase", "changes", "walkthrough", "wrapup"]
# paths the walkthrough leaves out
SKIP = re.compile(r"(^|/)(tests?|__tests__|spec|e2e|fixtures?|__snapshots__|mocks?|testdata)/"
                  r"|\.(test|spec|stories|snap)\.[a-z]+$|_test\.[a-z]+$|(^|/)test_[^/]+\.py$|\.lock$|-lock\.[a-z]+$")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("page")
    p.add_argument("--no-risk", action="store_true", help="the change has no real risk, and the wrap-up says so")
    a = p.parse_args()
    page = Path(a.page).read_text()
    fails = []

    for m in sorted(set(re.findall(r"\{\{[A-Z_]+\}\}", page))):
        fails.append(f"leftover marker {m}")

    at = [page.find(f'<section id="{s}"') for s in STAGES]
    for s, i in zip(STAGES, at):
        if i < 0:
            fails.append(f"no section with id {s}")
    if all(i >= 0 for i in at) and at != sorted(at):
        fails.append("the sections are out of order: " + ", ".join(STAGES))

    def body(stage):
        i = STAGES.index(stage)
        if at[i] < 0:
            return ""
        later = [x for x in at[i + 1:] if x > at[i]]
        return page[at[i]:min(later) if later else len(page)]

    # the glossary: stage 1 and the definition panel both read it
    terms, notes = {}, []
    g = re.search(r'<script type="application/json" id="glossary">(.*?)</script>', page, re.S)
    if not g:
        fails.append('no <script type="application/json" id="glossary">')
    else:
        try:
            terms = json.loads(g.group(1))
        except ValueError as e:
            fails.append(f"the glossary is not valid JSON: {e}")
    if 'id="defs"' not in body("definitions"):
        fails.append('definitions: no <dl class="defs" id="defs"> for the glossary to fill')
    for slug, t in terms.items():
        if not t.get("name") or not t.get("def"):
            fails.append(f"glossary entry {slug}: needs a name and a def")
        for k in t.get("also", []):
            if k not in terms:
                fails.append(f"glossary entry {slug}: see-also slug {k} has no entry")
    # skip slugs the page script interpolates, such as data-t="${k}"
    used = {x for x in re.findall(r'data-t="([^"]+)"', page) if "$" not in x}
    for slug in sorted(used - set(terms)):
        fails.append(f'data-t="{slug}" has no glossary entry')
    later = "".join(body(x) for x in STAGES[1:])
    unlinked = [x for x in terms if f'data-t="{x}"' not in later]
    if terms and len(unlinked) == len(terms):
        fails.append("no stage after the definitions marks a term with <button class=\"t\" data-t=...>")
    elif unlinked:
        notes.append("glossary entries that no later stage links: " + ", ".join(unlinked))
    if "<svg" not in body("codebase") and 'class="mermaid"' not in body("codebase"):
        fails.append("codebase: no diagram")
    comps = set(re.findall(r'id="(c-[\w-]+)"', body("codebase")))
    if not comps:
        fails.append('codebase: no component with an id="c-..."')
    for ref in sorted(set(re.findall(r'href="#(c-[\w-]+)"', page)) - comps):
        fails.append(f"a link names #{ref}, which is not a component in the codebase section")

    walk = body("walkthrough")
    stops = re.findall(r'<article class="stop">.*?</article>', walk, re.S)
    if not stops:
        fails.append("walkthrough: no stops")
    for k, stop in enumerate(stops, 1):
        if "<figure class=\"code" in stop and 'class="comp"' not in stop:
            fails.append(f"walkthrough stop {k}: code with no link to its component")
    if not any('<figure class="code' in s for s in stops):
        fails.append("walkthrough: no code snippets")
    if not a.no_risk and not re.search(r'class="risk"', walk):
        fails.append("walkthrough: no .risk callout (pass --no-risk when the change has none)")
    if a.no_risk and 'class="risk none"' not in body("wrapup"):
        fails.append('wrapup: --no-risk needs a class="risk none" callout that says so')

    for m in re.finditer(r'<figure class="code[^"]*" data-file="([^"]*)">(.*?)</figure>', page, re.S):
        file, fig = m.group(1), m.group(2)
        code = re.search(r'<code class="language-([\w-]+)"[^>]*>(.*?)</code>', fig, re.S)
        if not code:
            fails.append(f"snippet {file}: no <code class=\"language-...\">")
            continue
        n = code.group(2).count("\n") + 1
        if n > 40:
            fails.append(f"snippet {file}: {n} lines, over 40")
        if SKIP.search(file):
            fails.append(f"snippet {file}: a test, fixture or generated file")
    if '<figure class="code' in page and "highlight.min.js" not in page:
        fails.append("the highlight.js script is missing, so code is not highlighted")

    for f in fails:
        print("FAIL", f)
    for n in notes:
        print("note", n)
    print(f"{len(fails)} failures; {len(terms)} terms, {len(stops)} stops, {page.count('<figure class=\"code')} snippets, {len(comps)} components")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
