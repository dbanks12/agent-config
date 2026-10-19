#!/usr/bin/env python3
"""Find leaked build and QA process trees whose parent died, and stop them.

Dry run by default. Pass --apply to send SIGTERM, then SIGKILL after --grace seconds.

An orphan root is a process of this user whose parent is PID 1 or this user's
`systemd --user`. The reaper stops the root's whole tree when all of these hold:
  - the root runs at least --min-age
  - the root is a target, or a wrapper (shell, timeout, nohup, env) with a target in its tree
  - no agent, multiplexer, or terminal runs in the tree
  - the Claude process that started the tree (CLAUDE_PID in its environment) is dead,
    unless the tree holds only Gradle or Kotlin daemons, which outlive builds by design
  - (Gradle and Kotlin daemons only) no Gradle client is running

Targets: cargo-mutants, cargo, rustc, the Gradle daemon, the Kotlin compile
daemon, and node processes under a `qa` directory.
"""
import argparse
import os
import re
import signal
import sys
import time
from pathlib import Path

UID = os.getuid()
CLK_TCK = os.sysconf("SC_CLK_TCK")
PAGE = os.sysconf("SC_PAGE_SIZE")

WRAPPERS = {"bash", "sh", "dash", "zsh", "timeout", "nohup", "env", "setsid"}
PROTECTED = {"claude", "codex", "herdr", "tmux", "screen", "sshd", "systemd"}
GRADLE_CLIENT = re.compile(r"org\.gradle\.(wrapper\.GradleWrapperMain|launcher\.GradleMain)")
TARGETS = [
    ("cargo-mutants", lambda p: p["exe"] == "cargo-mutants" or "cargo-mutants" in p["args"]),
    ("gradle-daemon", lambda p: "org.gradle.launcher.daemon.bootstrap.GradleDaemon" in p["args"]),
    ("kotlin-daemon", lambda p: "org.jetbrains.kotlin.daemon.KotlinCompileDaemon" in p["args"]),
    ("cargo", lambda p: p["exe"] == "cargo"),
    ("rustc", lambda p: p["exe"] == "rustc"),
    ("qa-node", lambda p: p["exe"] == "node" and ("/qa/" in p["args"] or "/qa/" in p["cwd"] + "/")),
]
DAEMONS = {"gradle-daemon", "kotlin-daemon"}


def read_procs():
    boot = time.time() - float(Path("/proc/uptime").read_text().split()[0])
    procs = {}
    for d in Path("/proc").iterdir():
        if not d.name.isdigit():
            continue
        try:
            if d.stat().st_uid != UID:
                continue
            fields = (d / "stat").read_text().rsplit(")", 1)[1].split()
            args = (d / "cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace").strip()
            try:
                exe = os.path.basename(os.readlink(d / "exe"))
            except OSError:
                exe = (d / "comm").read_text().strip()
            try:
                cwd = os.readlink(d / "cwd")
            except OSError:
                cwd = ""
            try:
                env = (d / "environ").read_bytes()
                owner = int(re.search(rb"(?:^|\0)CLAUDE_PID=(\d+)", env).group(1))
            except (OSError, AttributeError):
                owner = None
        except (OSError, IndexError):
            continue
        pid = int(d.name)
        procs[pid] = {
            "pid": pid,
            "ppid": int(fields[1]),
            "start": fields[19],
            "age": time.time() - (boot + int(fields[19]) / CLK_TCK),
            "rss": int(fields[21]) * PAGE,
            "exe": exe,
            "comm": (d / "comm").read_text().strip() if (d / "comm").exists() else exe,
            "args": args,
            "cwd": cwd,
            "owner": owner,
        }
    return procs


def target_kind(p):
    for kind, match in TARGETS:
        if match(p):
            return kind
    return None


def tree(root, children):
    out, stack = [], [root]
    while stack:
        pid = stack.pop()
        out.append(pid)
        stack.extend(children.get(pid, ()))
    return out


def find_orphans(procs, min_age):
    reapers = {1} | {p["pid"] for p in procs.values() if p["exe"] == "systemd" and "--user" in p["args"]}
    children = {}
    for p in procs.values():
        children.setdefault(p["ppid"], []).append(p["pid"])
    gradle_client = any(GRADLE_CLIENT.search(p["args"]) for p in procs.values())

    found = []
    for root in procs.values():
        if root["ppid"] not in reapers or root["pid"] in reapers:
            continue
        pids = tree(root["pid"], children)
        kinds = {k for k in (target_kind(procs[q]) for q in pids) if k}
        if not kinds:
            continue
        if not (target_kind(root) or root["exe"] in WRAPPERS):
            continue
        guard = next((procs[q]["exe"] for q in pids if procs[q]["exe"] in PROTECTED or procs[q]["comm"] in PROTECTED), None)
        if guard:
            reason = f"tree contains {guard}"
        elif set(kinds) - DAEMONS and (owner := next((o for o in (procs[q]["owner"] for q in pids) if o in procs and procs[o]["comm"] == "claude"), None)):
            reason = f"owner agent alive (claude pid {owner})"
        elif root["age"] < min_age:
            reason = f"age {root['age'] / 3600:.1f}h"
        elif kinds & DAEMONS and gradle_client:
            reason = "a Gradle client is running"
        else:
            reason = None
        found.append((root, pids, sorted(kinds), reason))
    return found


def still_same(p):
    try:
        return Path(f"/proc/{p['pid']}/stat").read_text().rsplit(")", 1)[1].split()[19] == p["start"]
    except (OSError, IndexError):
        return False


def stop(procs, pids, grace):
    """SIGTERM every PID that is still the same process, then SIGKILL survivors."""
    live = [procs[q] for q in pids if still_same(procs[q])]
    for p in live:
        try:
            os.kill(p["pid"], signal.SIGTERM)
        except ProcessLookupError:
            pass
    deadline = time.time() + grace
    while time.time() < deadline and any(still_same(p) for p in live):
        time.sleep(0.5)
    for p in live:
        if still_same(p):
            try:
                os.kill(p["pid"], signal.SIGKILL)
            except ProcessLookupError:
                pass


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="stop the trees (default: dry run)")
    ap.add_argument("--min-age", type=float, default=2, metavar="HOURS",
                    help="skip orphan roots younger than this (default: 2)")
    ap.add_argument("--grace", type=float, default=10, metavar="SECONDS",
                    help="wait this long after SIGTERM before SIGKILL (default: 10)")
    ap.add_argument("-v", "--verbose", action="store_true", help="also list skipped trees")
    args = ap.parse_args()

    procs = read_procs()
    verb = "killed" if args.apply else "would kill"
    total_rss = count = 0
    for root, pids, kinds, reason in find_orphans(procs, args.min_age * 3600):
        rss = sum(procs[q]["rss"] for q in pids)
        head = f"pid={root['pid']} age={root['age'] / 3600:.1f}h procs={len(pids)} rss={rss / 2**20:.0f}M kinds={','.join(kinds)}"
        if reason:
            if args.verbose:
                print(f"skip {head} ({reason}): {root['args'][:160]}")
            continue
        print(f"{verb} {head}: {root['args'][:160]}")
        if args.verbose:
            for q in pids[1:]:
                print(f"    {q} {procs[q]['args'][:150]}")
        if args.apply:
            stop(procs, pids, args.grace)
        total_rss += rss
        count += 1

    mode = "" if args.apply else " (dry run; pass --apply to kill)"
    print(f"total {verb}: {count} trees, {total_rss / 2**30:.1f}G RSS{mode}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
