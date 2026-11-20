#!/usr/bin/env python3
"""Post a Sill note when a filesystem is fuller than --threshold percent.

Posts at most once per --every hours for each mount.
"""
import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

SILL = Path.home() / ".local/share/sill/core-rs/sill-core"
STATE = Path.home() / ".local/state/agent-cleanup/disk-alert.json"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mounts", nargs="*", default=["/", "/data"])
    ap.add_argument("--threshold", type=float, default=85, metavar="PERCENT")
    ap.add_argument("--every", type=float, default=12, metavar="HOURS")
    args = ap.parse_args()

    try:
        sent = json.loads(STATE.read_text())
    except (OSError, ValueError):
        sent = {}
    now = time.time()
    status = 0
    for mount in args.mounts:
        try:
            st = os.statvfs(mount)
        except OSError:
            continue
        used = 100 * (1 - st.f_bavail / st.f_blocks)
        free_gb = st.f_bavail * st.f_frsize / 1e9
        print(f"{mount}: {used:.0f}% used, {free_gb:.0f} GB free")
        if used < args.threshold or now - sent.get(mount, 0) < args.every * 3600:
            continue
        text = (f"{mount} on {os.uname().nodename} is {used:.0f}% full, {free_gb:.0f} GB free. "
                f"Run linux/cleanup/disk-janitor.py in agent-config to see what it can remove.")
        r = subprocess.run([str(SILL), "note", "--from", "Disk", text], capture_output=True, text=True)
        if r.returncode:
            print(f"sill-core note failed: {r.stderr.strip()}", file=sys.stderr)
            status = 1
            continue
        sent[mount] = now
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(sent))
    return status


if __name__ == "__main__":
    sys.exit(main())
