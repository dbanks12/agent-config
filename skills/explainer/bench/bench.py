#!/usr/bin/env python3
"""Run the explainer skill headless on fixed inputs and measure where the time goes.

Usage:
  bench.py run [--inputs install,player] [--label NAME] [--narrated] [--serial]
  bench.py report [RUN_DIR ...]      # default: every run under the results root

Each input runs in its own `claude -p` session, in a fresh copy of bench/inputs/<name>/. The session
uses the skill as checked out in this repo, through the ~/.claude/skills symlink. Results go to
~/.local/share/explainer-bench/<time>-<label>/<input>/: the transcript, timeline.json, report.txt,
the CLI's JSON result, and the job's work dir, moved out of ~/.local/share/explainers so bench
manifests never join the style history.

Captions mode is the default, so a run spends no ElevenLabs characters. --narrated spends about
3,000 per input.
"""
import argparse
import glob
import json
import os
import shutil
import subprocess
import sys
import threading
import time
import uuid
from pathlib import Path

import timeline

HERE = Path(__file__).resolve().parent
ROOT = Path.home() / ".local/share/explainer-bench"
JOBS = Path.home() / ".local/share/explainers"
TIMEOUT_S = 3600

PROMPT = """/explainer {topic}

Sources: the files in {src}. Host: standalone. Mode: {mode}. Use the slug {slug}.
I will not be around to choose a look: build the style board as step 3 says, then pick the Excalidraw sketch look yourself and keep going without asking.
There is no Artifact tool in this session, so finish step 7 by leaving page.html in the work dir and printing its path."""


def git_rev():
    r = subprocess.run(["git", "-C", str(HERE), "log", "-1", "--format=%h %s"], capture_output=True, text=True)
    dirty = subprocess.run(["git", "-C", str(HERE), "status", "--porcelain", "--", ".."], capture_output=True, text=True).stdout
    return r.stdout.strip() + (" (dirty)" if dirty.strip() else "")


def run_one(name, run_dir, narrated):
    out = run_dir / name
    src = out / "src"
    shutil.copytree(HERE / "inputs" / name, src)
    topic = (src / "topic.txt").read_text().strip()
    slug = f"bench-{name}-{run_dir.name[:15]}"
    session = str(uuid.uuid4())
    mode = "narrated" if narrated else "captions only; do not use ElevenLabs"
    prompt = PROMPT.format(topic=topic, src=src, mode=mode, slug=slug)
    (out / "prompt.txt").write_text(prompt)
    cmd = ["timeout", str(TIMEOUT_S), "claude", "-p", "--permission-mode", "auto", "--session-id", session,
           "--output-format", "json", prompt]
    t0 = time.time()
    with open(out / "result.json", "w") as stdout, open(out / "stderr.txt", "w") as stderr:
        code = subprocess.run(cmd, cwd=src, stdout=stdout, stderr=stderr, stdin=subprocess.DEVNULL).returncode
    wall = time.time() - t0

    meta = {"input": name, "slug": slug, "session": session, "exit": code, "wall_s": wall, "rev": git_rev(),
            "narrated": narrated}
    transcripts = glob.glob(str(Path.home() / ".claude/projects/*" / f"{session}.jsonl"))
    if transcripts:
        shutil.copy(transcripts[0], out / "transcript.jsonl")
        with open(transcripts[0]) as f:
            turns = timeline.analyze([json.loads(line) for line in f if line.strip()])
        (out / "timeline.json").write_text(json.dumps(turns, indent=1))
        with open(out / "report.txt", "w") as f:
            sys.stdout, saved = f, sys.stdout
            try:
                timeline.report(turns, show_calls=True)
            finally:
                sys.stdout = saved
    job = JOBS / slug
    if job.is_dir():
        shutil.move(str(job), out / "job")
    page = out / "job" / "page.html"
    meta["page_bytes"] = page.stat().st_size if page.exists() else 0
    (out / "meta.json").write_text(json.dumps(meta, indent=1))
    print(f"bench: {name} finished in {timeline.fmt(wall)}, exit {code}, page {meta['page_bytes']} bytes", flush=True)


def cmd_run(a):
    names = a.inputs.split(",")
    for n in names:
        if not (HERE / "inputs" / n / "topic.txt").exists():
            sys.exit(f"bench: no input {n}")
    run_dir = ROOT / f"{time.strftime('%Y%m%d-%H%M%S')}-{a.label}"
    run_dir.mkdir(parents=True)
    print(f"bench: {run_dir}", flush=True)
    if a.serial:
        for n in names:
            run_one(n, run_dir, a.narrated)
    else:
        threads = [threading.Thread(target=run_one, args=(n, run_dir, a.narrated)) for n in names]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
    report([run_dir])


def summarize(out):
    meta = json.loads((out / "meta.json").read_text())
    row = {"run": out.parent.name, "input": meta["input"], "wall": meta["wall_s"], "exit": meta["exit"],
           "page": meta["page_bytes"] > 0}
    if (out / "timeline.json").exists():
        turns = json.loads((out / "timeline.json").read_text())
        t = turns[0]
        row.update(model=t["model_s"], tool=t["tool_s"], bg=t["bg_only_s"], gap=t["gap_s"], req=t["requests"],
                   phases={p["phase"]: p["wall"] for p in t["by_phase"]},
                   cats={k: v["model"] + v["tool"] for k, v in t["by_category"].items()})
    return row


def report(run_dirs):
    rows = [summarize(m.parent) for d in run_dirs for m in sorted(Path(d).glob("*/meta.json"))]
    f = timeline.fmt
    print(f"\n{'run':34} {'input':8} {'wall':>7} {'model':>7} {'tool':>7} {'bgwait':>7} {'req':>4} ok  top phases")
    for r in rows:
        ok = "y" if r["exit"] == 0 and r["page"] else "n"
        ph = " ".join(f"{k}:{f(v)}" for k, v in sorted(r.get("phases", {}).items(), key=lambda kv: -kv[1])[:4])
        print(f"{r['run'][:34]:34} {r['input']:8} {f(r['wall']):>7} {f(r.get('model', 0)):>7} {f(r.get('tool', 0)):>7}"
              f" {f(r.get('bg', 0)):>7} {r.get('req', 0):>4} {ok:2}  {ph}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--inputs", default="install,player")
    r.add_argument("--label", default="run")
    r.add_argument("--narrated", action="store_true")
    r.add_argument("--serial", action="store_true", help="run inputs one after another, not in parallel")
    p = sub.add_parser("report")
    p.add_argument("runs", nargs="*")
    a = ap.parse_args()
    if a.cmd == "run":
        cmd_run(a)
    else:
        report(a.runs or sorted(d for d in ROOT.glob("*") if d.is_dir()))


if __name__ == "__main__":
    main()
