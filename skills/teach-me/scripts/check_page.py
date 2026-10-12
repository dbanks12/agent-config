#!/usr/bin/env python3
"""Check a drafted teach-me page against the skill's budget and wiring rules.

Usage:
    python3 check_page.py PAGE.html [--words 900] [--quiet]

Exit status is 0 when every hard rule passes, and 1 otherwise.
"""
import argparse
import re
import sys
from pathlib import Path

SECTIONS = ["summary", "foundation", "blocks", "flow", "plug",
            "guarantees", "compare", "glossary", "quizpage"]

DIAGRAMS = (4, 6)
TERMS = (25, 40)
QUIZ = (6, 8)
SENTENCE_WORDS = 25


def strip(html, tag):
    return re.sub(r"<%s\b.*?</%s>" % (tag, tag), " ", html, flags=re.S | re.I)


# Chrome: navigation, tabs, the definition panel, the generated glossary index,
# the reading hint, and the footer. None of it is prose the budget governs.
CHROME = [
    r"<nav\b.*?</nav>",
    r"<aside\b[^>]*id=\"panel\".*?</aside>",
    r"<footer\b.*?</footer>",
    r"<div\b[^>]*class=\"tabs\"[^>]*>.*?</div>",
    r"<div\b[^>]*class=\"gloss-index\"[^>]*>.*?</div>",
    r"<div\b[^>]*class=\"hint\"[^>]*>.*?</div>",
    r"<div\b[^>]*class=\"score\"[^>]*>.*?</div>",
    r"<div\b[^>]*class=\"quiz-actions\"[^>]*>.*?</div>",
]


def body_only(html):
    """Drop script, style, svg, code blocks, tables, and page chrome."""
    body = strip(strip(strip(strip(html, "script"), "style"), "svg"), "pre")
    body = re.sub(r"<table\b.*?</table>", " ", body, flags=re.S | re.I)
    for pat in CHROME:
        body = re.sub(pat, " ", body, flags=re.S | re.I)
    return body


BLOCK_END = r"</(?:h[1-6]|p|li|figcaption|div|td|th|section|dt|dd)>"


def text_of(html):
    # A heading carries no full stop, so end every block to keep it out of the
    # sentence that follows it.
    body = re.sub(BLOCK_END, " . ", html, flags=re.I)
    body = re.sub(r"<[^>]+>", " ", body)
    body = re.sub(r"&[a-z]+;|&#\d+;", " ", body)
    return re.sub(r"\s+", " ", body).strip()


def prose_words(html):
    """Word count over prose only: no diagrams, code, tables, glossary bodies, or chrome."""
    return len([w for w in text_of(body_only(html)).split() if w != "."])


def long_sentences(html):
    out = []
    for raw in re.split(r"(?<=[.!?])\s+", text_of(body_only(html))):
        s = raw.strip()
        if len(s.split()) > SENTENCE_WORDS:
            out.append(s)
    return out


def js_object_keys(html, name):
    """Top-level keys of `const <name> = { ... }` in the page script."""
    m = re.search(r"\b(?:const|var|let)\s+%s\s*=\s*\{" % re.escape(name), html)
    if not m:
        return []
    i = m.end() - 1
    depth, end = 0, None
    for j in range(i, len(html)):
        if html[j] == "{":
            depth += 1
        elif html[j] == "}":
            depth -= 1
            if depth == 0:
                end = j
                break
    if end is None:
        return []
    body = html[i + 1:end]
    keys, depth = [], 0
    for line in body.splitlines():
        stripped = line.strip()
        if depth == 0:
            k = re.match(r"""^["']?([A-Za-z0-9_-]+)["']?\s*:\s*\{""", stripped)
            if k:
                keys.append(k.group(1))
        depth += line.count("{") - line.count("}")
    return keys


def count_quiz(html):
    m = re.search(r"\b(?:const|var|let)\s+Q\s*=\s*\[", html)
    if not m:
        return 0
    # Skip the template's example items, which sit in a block comment.
    rest = re.sub(r"/\*.*?\*/", " ", html[m.end():], flags=re.S)
    return len(re.findall(r"\bwhy\s*:", rest))


def check(path, budget, quiet):
    html = Path(path).read_text(encoding="utf-8")
    fails, notes = [], []

    words = prose_words(html)
    ceiling = int(budget * 1.1)
    if words > ceiling:
        fails.append("prose %d words, ceiling %d. Cut, do not pad." % (words, ceiling))
    else:
        notes.append("prose %d words, budget %d" % (words, budget))

    figures = len(re.findall(r"<figure\b", html, re.I))
    svgs = len(re.findall(r"<svg\b", html, re.I))
    if not DIAGRAMS[0] <= figures <= DIAGRAMS[1]:
        fails.append("%d figures, want %d to %d" % (figures, *DIAGRAMS))
    else:
        notes.append("%d figures" % figures)
    if svgs != figures:
        notes.append("%d svg against %d figure elements" % (svgs, figures))

    # Skip slugs the page script interpolates, such as data-t="${k}".
    used = {s for s in re.findall(r'data-t="([^"]+)"', html) if "$" not in s}
    defined = set(js_object_keys(html, "G"))
    missing = sorted(used - defined)
    orphan = sorted(defined - used)
    if missing:
        fails.append("data-t slugs with no glossary entry: " + ", ".join(missing))
    if orphan:
        notes.append("glossary entries never linked in prose: " + ", ".join(orphan))
    if defined and not TERMS[0] <= len(defined) <= TERMS[1]:
        fails.append("%d glossary terms, want %d to %d" % (len(defined), *TERMS))
    elif defined:
        notes.append("%d glossary terms" % len(defined))

    # Links are information, not a pass condition.
    prose_links = len(re.findall(r'<a\s[^>]*href="https://', html))
    term_links = len(re.findall(r'\blink\s*:\s*\{\s*url\s*:', html))
    notes.append("%d prose links, %d glossary links" % (prose_links, term_links))

    also = set()
    for m in re.finditer(r"also\s*:\s*\[([^\]]*)\]", html):
        also.update(re.findall(r"""["']([A-Za-z0-9_-]+)["']""", m.group(1)))
    dangling = sorted(also - defined)
    if dangling:
        fails.append("see-also slugs with no entry: " + ", ".join(dangling))

    # A page has no quiz by default. A quiz, once added, has a fixed size.
    quiz = count_quiz(html)
    if quiz == 0:
        notes.append("no quiz")
    elif not QUIZ[0] <= quiz <= QUIZ[1]:
        fails.append("%d quiz questions, want %d to %d" % (quiz, *QUIZ))
    else:
        notes.append("%d quiz questions" % quiz)

    absent = [s for s in SECTIONS if 'id="%s"' % s not in html]
    if absent:
        fails.append("missing section ids: " + ", ".join(absent))

    markers = sorted(set(re.findall(r"\{\{[A-Z_]+\}\}", html)))
    if markers:
        fails.append("unreplaced template markers: " + ", ".join(markers))

    long = long_sentences(html)
    if long:
        fails.append("%d sentences over %d words. First: %s"
                     % (len(long), SENTENCE_WORDS, long[0][:90] + "..."))

    markers_def = len(re.findall(r'<marker\b[^>]*id="arr"', html))
    if markers_def > 1:
        fails.append("arrow marker id 'arr' defined %d times, define it once" % markers_def)

    for tag in ("section", "figure", "table", "ol", "ul"):
        o = len(re.findall(r"<%s\b" % tag, html, re.I))
        c = len(re.findall(r"</%s>" % tag, html, re.I))
        if o != c:
            fails.append("%s tags unbalanced: %d open, %d close" % (tag, o, c))

    if not quiet:
        for n in notes:
            print("  note %s" % n)
    for f in fails:
        print("  FAIL %s" % f)
    print(("FAIL %s" % path) if fails else ("PASS %s" % path))
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("page")
    ap.add_argument("--words", type=int, default=900,
                    help="prose budget; ceiling is 10 percent above it")
    ap.add_argument("--quiet", action="store_true", help="print failures only")
    a = ap.parse_args()
    sys.exit(check(a.page, a.words, a.quiet))


if __name__ == "__main__":
    main()
