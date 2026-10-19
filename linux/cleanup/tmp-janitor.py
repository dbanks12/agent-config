#!/usr/bin/env python3
"""Remove stale agent scratch, the pnpm store, and pytest dirs from /tmp.

Dry run by default. Pass --apply to delete.

Units of deletion:
  /tmp/claude-$UID/<project>/<session>  one Claude session's scratch
  /tmp/claude-$UID/<entry>              any other top-level file or dir
  /tmp/.pnpm-store                      the whole store
  /tmp/pytest-of-$USER/pytest-N         one pytest run

A unit is kept when any of these is true:
  - its newest mtime is younger than --max-age
  - a live process of this user has its cwd or an open file inside it
  - it is the scratch dir of a live Claude session (~/.claude/sessions/<pid>.json)
  - it is the project dir of a worktree where a live process has its cwd
  - (pnpm store only) a pnpm process is running
  - it is not owned by this user
"""
import argparse
import getpass
import json
import os
import re
import shutil
import stat
import sys
import time
from pathlib import Path

UID = os.getuid()
TMP = Path("/tmp")
CLAUDE_TMP = TMP / f"claude-{UID}"
PNPM_STORE = TMP / ".pnpm-store"
PYTEST_ROOT = TMP / f"pytest-of-{getpass.getuser()}"
SESSIONS = Path.home() / ".claude" / "sessions"


def encode(path):
    """Claude Code names a project's scratch dir after its cwd: every non-alphanumeric char becomes '-'."""
    return re.sub(r"[^A-Za-z0-9]", "-", path)


def my_pids():
    for d in Path("/proc").iterdir():
        if d.name.isdigit():
            try:
                if d.stat().st_uid == UID:
                    yield int(d.name)
            except OSError:
                pass


def proc_start(pid):
    """Field 22 of /proc/<pid>/stat. Guards against PID reuse."""
    try:
        return Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[19]
    except (OSError, IndexError):
        return None


def scan_processes():
    """Return (paths in use, cwds, set of comm names) for this user's live processes."""
    in_use, cwds, comms = set(), set(), set()
    for pid in my_pids():
        base = f"/proc/{pid}"
        try:
            comms.add(Path(f"{base}/comm").read_text().strip())
            cwd = os.readlink(f"{base}/cwd")
            cwds.add(cwd)
            in_use.add(cwd)
        except OSError:
            continue
        try:
            for fd in os.listdir(f"{base}/fd"):
                try:
                    in_use.add(os.readlink(f"{base}/fd/{fd}"))
                except OSError:
                    pass
        except OSError:
            pass
    return in_use, cwds, comms


def live_sessions():
    """Session IDs of Claude Code sessions whose process is still alive."""
    ids = set()
    for f in SESSIONS.glob("*.json"):
        try:
            s = json.loads(f.read_text())
        except (OSError, ValueError):
            continue
        if s.get("sessionId") and proc_start(s.get("pid")) == s.get("procStart"):
            ids.add(s["sessionId"])
    return ids


def newest_mtime_and_size(path):
    """Walk without following symlinks. Return (newest mtime, total bytes)."""
    st = path.lstat()
    newest, size = st.st_mtime, st.st_size
    if stat.S_ISDIR(st.st_mode):
        for root, dirs, files in os.walk(path, followlinks=False):
            for name in dirs + files:
                try:
                    s = os.lstat(os.path.join(root, name))
                except OSError:
                    continue
                newest = max(newest, s.st_mtime)
                size += s.st_blocks * 512
    return newest, size


def inside(path, in_use):
    p = str(path)
    return any(u == p or u.startswith(p + "/") for u in in_use)


def candidates():
    """Yield (unit path, kind)."""
    if CLAUDE_TMP.is_dir():
        for entry in sorted(CLAUDE_TMP.iterdir()):
            if entry.name.startswith("-") and entry.is_dir() and not entry.is_symlink():
                for session in sorted(entry.iterdir()):
                    yield session, "claude-session"
            else:
                yield entry, "claude-scratch"
    if PNPM_STORE.exists():
        yield PNPM_STORE, "pnpm-store"
    if PYTEST_ROOT.is_dir():
        for entry in sorted(PYTEST_ROOT.glob("pytest-*")):
            if entry.name != "pytest-current":
                yield entry, "pytest"


def keep_reason(path, kind, ctx, cutoff):
    try:
        st = path.lstat()
    except FileNotFoundError:
        return "gone"
    if st.st_uid != UID:
        return "not mine"
    if kind == "claude-session":
        if path.name in ctx["sessions"]:
            return "live session"
        if path.parent.name in ctx["worktrees"]:
            return "worktree active"
    if kind == "claude-scratch" and path.name in ctx["worktrees"]:
        return "worktree active"
    if kind == "pnpm-store" and "pnpm" in ctx["comms"]:
        return "pnpm running"
    if inside(path, ctx["in_use"]):
        return "in use"
    newest, size = newest_mtime_and_size(path)
    ctx["size"][path] = size
    if newest > cutoff:
        return f"modified {(time.time() - newest) / 3600:.1f}h ago"
    return None


def remove(path):
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    else:
        path.unlink()


def human(n):
    for unit in "BKMG":
        if n < 1024:
            return f"{n:.0f}{unit}"
        n /= 1024
    return f"{n:.1f}T"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="delete (default: dry run)")
    ap.add_argument("--max-age", type=float, default=24, metavar="HOURS",
                    help="keep anything modified within this many hours (default: 24)")
    ap.add_argument("-v", "--verbose", action="store_true", help="also list kept units")
    args = ap.parse_args()

    in_use, cwds, comms = scan_processes()
    ctx = {
        "in_use": in_use,
        "comms": comms,
        "sessions": live_sessions(),
        "worktrees": {encode(c) for c in cwds},
        "size": {},
    }
    cutoff = time.time() - args.max_age * 3600
    verb = "removed" if args.apply else "would remove"
    total = errors = 0

    for path, kind in candidates():
        reason = keep_reason(path, kind, ctx, cutoff)
        if reason:
            if args.verbose:
                print(f"keep  {kind:15} {path}  ({reason})")
            continue
        size = ctx["size"][path]
        if args.apply:
            try:
                remove(path)
            except OSError as e:
                print(f"error {kind:15} {path}: {e}", file=sys.stderr)
                errors += 1
                continue
        total += size
        print(f"{verb} {kind:15} {human(size):>6} {path}")

    # Drop project dirs that are now empty.
    if args.apply and CLAUDE_TMP.is_dir():
        for entry in CLAUDE_TMP.iterdir():
            if entry.name.startswith("-") and entry.is_dir() and not entry.is_symlink():
                try:
                    entry.rmdir()
                except OSError:
                    pass

    mode = "" if args.apply else " (dry run; pass --apply to delete)"
    print(f"total {verb}: {human(total)}{mode}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
