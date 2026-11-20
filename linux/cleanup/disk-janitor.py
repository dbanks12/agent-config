#!/usr/bin/env python3
"""Remove oversized or stale Cargo target dirs.

Dry run by default. Pass --apply to delete.

Units of deletion:
  <target>/.../incremental   Cargo's incremental cache, when the target is over --cargo-cap
  <target>                   a whole Cargo target, when it is untouched for --stale-days
                             or still over --cargo-cap without its incremental cache

A unit is kept when any of these is true:
  - a live process of this user has its cwd or an open file inside it
  - a cargo or rustc process of this user is running
"""
import argparse
import os
import shutil
import stat
import sys
import time
from pathlib import Path

UID = os.getuid()
HOME = Path.home()
# Cargo writes .rustc_info.json at the root of every target dir.
CARGO_ROOTS = [HOME / ".cache", HOME / "projects", Path("/data/worktrees"), Path("/data/kotor-overhaul")]
CARGO_DEPTH = 4


def scan_processes():
    """Return (paths in use, set of comm names) for this user's live processes."""
    in_use, comms = set(), set()
    for d in Path("/proc").iterdir():
        if not d.name.isdigit():
            continue
        try:
            if d.stat().st_uid != UID:
                continue
            comms.add((d / "comm").read_text().strip())
            in_use.add(os.readlink(d / "cwd"))
            for fd in os.listdir(d / "fd"):
                try:
                    in_use.add(os.readlink(d / "fd" / fd))
                except OSError:
                    pass
        except OSError:
            continue
    return in_use, comms


def inside(path, in_use):
    p = str(path)
    return any(u == p or u.startswith(p + "/") for u in in_use)


def newest_mtime_and_size(path):
    """Walk without following symlinks. Return (newest mtime, total bytes)."""
    st = path.lstat()
    newest, size = st.st_mtime, st.st_blocks * 512
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


def cargo_targets():
    """Yield each Cargo target dir under CARGO_ROOTS, without descending into one."""
    def walk(d, depth):
        try:
            entries = list(os.scandir(d))
        except OSError:
            return
        if any(e.name == ".rustc_info.json" for e in entries):
            yield Path(d)
            return
        if depth == CARGO_DEPTH:
            return
        for e in entries:
            if e.is_dir(follow_symlinks=False) and e.name not in ("node_modules", ".git"):
                yield from walk(e.path, depth + 1)
    for root in CARGO_ROOTS:
        yield from walk(root, 0)


def cargo_units(in_use, cap, stale_cutoff):
    """Yield (path, size, why) for Cargo caches to delete."""
    for t in cargo_targets():
        if inside(t, in_use):
            continue
        newest, size = newest_mtime_and_size(t)
        if newest < stale_cutoff:
            yield t, size, "stale"
            continue
        if size <= cap:
            continue
        for inc in sorted(t.glob("**/incremental")):
            if inc.is_dir() and not inc.is_symlink() and len(inc.relative_to(t).parts) <= 3:
                _, s = newest_mtime_and_size(inc)
                size -= s
                yield inc, s, "over cap"
        if size > cap:
            yield t, size, "over cap"


def human(n):
    for unit in "BKMG":
        if n < 1024:
            return f"{n:.0f}{unit}"
        n /= 1024
    return f"{n:.1f}T"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="delete (default: dry run)")
    ap.add_argument("--cargo-cap", type=float, default=40, metavar="GIB",
                    help="shrink a Cargo target dir larger than this (default: 40)")
    ap.add_argument("--stale-days", type=float, default=7, metavar="DAYS",
                    help="delete a Cargo target dir untouched for this many days (default: 7)")
    args = ap.parse_args()

    in_use, comms = scan_processes()
    if comms & {"cargo", "rustc"}:
        print("skip: a cargo or rustc process is running")
        return 0
    units = cargo_units(in_use, args.cargo_cap * 2**30, time.time() - args.stale_days * 86400)

    verb = "removed" if args.apply else "would remove"
    total = errors = 0
    for path, size, why in units:
        if args.apply:
            try:
                shutil.rmtree(path)
            except FileNotFoundError:
                pass
            except OSError as e:
                print(f"error {why:8} {path}: {e}", file=sys.stderr)
                errors += 1
                continue
        total += size
        print(f"{verb} {why:8} {human(size):>6} {path}")

    mode = "" if args.apply else " (dry run; pass --apply to delete)"
    print(f"total {verb}: {human(total)}{mode}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
