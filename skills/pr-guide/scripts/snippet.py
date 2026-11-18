#!/usr/bin/env python3
"""Cut a code snippet from git and print it as a pr-guide <figure class="code">."""
import argparse, html, subprocess, sys
from pathlib import Path

# file extension -> highlight.js language
LANG = {
    "ts": "typescript", "tsx": "typescript", "mts": "typescript", "cts": "typescript",
    "js": "javascript", "jsx": "javascript", "mjs": "javascript", "cjs": "javascript",
    "py": "python", "rs": "rust", "go": "go", "rb": "ruby", "java": "java", "kt": "kotlin",
    "swift": "swift", "c": "c", "h": "c", "cc": "cpp", "cpp": "cpp", "hpp": "cpp", "cs": "csharp",
    "sh": "bash", "bash": "bash", "zsh": "bash", "sql": "sql", "json": "json", "yml": "yaml",
    "yaml": "yaml", "toml": "ini", "ini": "ini", "md": "markdown", "html": "xml", "xml": "xml",
    "svg": "xml", "css": "css", "scss": "scss", "php": "php", "lua": "lua", "tf": "ini",
    "graphql": "graphql", "diff": "diff", "patch": "diff", "mk": "makefile",
    "sol": "solidity", "nr": "rust",  # Noir reads close to Rust
}
NAMES = {"Dockerfile": "dockerfile", "Makefile": "makefile"}


def span(text):
    a, _, b = text.partition("-")
    a, b = int(a), int(b or a)
    if a < 1 or b < a:
        sys.exit(f"bad line range: {text}")
    return a, b


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo", default=".")
    p.add_argument("--rev", required=True, help="commit that holds the lines: the PR's head, or its base with --old")
    p.add_argument("--file", required=True)
    p.add_argument("--lines", required=True, help="A-B, 1-indexed, inclusive")
    p.add_argument("--title", required=True, help="what the snippet shows, as a statement")
    p.add_argument("--mark", action="append", default=[], help="A-B to mark; repeat for more")
    p.add_argument("--url", help="link for the source line, such as the PR or the blob URL")
    p.add_argument("--lang", help="highlight.js language; the default comes from the file name")
    p.add_argument("--old", action="store_true", help="the snippet shows removed code")
    a = p.parse_args()

    got = subprocess.run(["git", "-C", a.repo, "show", f"{a.rev}:{a.file}"], capture_output=True, text=True)
    if got.returncode:
        sys.exit(got.stderr.strip())
    lo, hi = span(a.lines)
    lines = got.stdout.split("\n")
    if hi > len(lines):
        sys.exit(f"{a.file} has {len(lines)} lines at {a.rev}")
    if hi - lo + 1 > 40:
        print(f"warning: {hi - lo + 1} lines; keep a snippet to 40 or fewer", file=sys.stderr)
    name = Path(a.file).name
    lang = a.lang or NAMES.get(name) or LANG.get(name.rsplit(".", 1)[-1].lower(), "plaintext")
    marks = sorted({n for m in a.mark for n in range(span(m)[0], span(m)[1] + 1)})
    src = f"{a.file}:{lo}-{hi}"
    if a.url:
        src = f'<a href="{html.escape(a.url, quote=True)}" target="_blank" rel="noopener">{html.escape(src)}</a>'
    else:
        src = html.escape(src)
    mark = f' data-mark="{",".join(map(str, marks))}"' if marks else ""
    code = html.escape("\n".join(lines[lo - 1:hi]), quote=False)
    print(f'<figure class="code{" old" if a.old else ""}" data-file="{html.escape(a.file, quote=True)}">\n'
          f'  <figcaption><b>{html.escape(a.title)}</b><span class="src">{src}</span></figcaption>\n'
          f'  <pre><code class="language-{lang}" data-start="{lo}"{mark}>{code}</code></pre>\n'
          f'</figure>')


if __name__ == "__main__":
    main()
