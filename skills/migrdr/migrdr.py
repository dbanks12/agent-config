#!/usr/bin/env python3
"""Move Herdr workspaces, tabs, or panes to another Herdr session.

Herdr cannot move a live process between servers. This script rebuilds the
layout in the target session with layout.apply and resumes each agent there
from the session ID that Herdr recorded. Closing the source is left to the
caller, after it verifies the result.

  migrdr.py plan <target-session> [--scope group|workspace|tab|pane] [--pane ID]
  migrdr.py apply <plan.json>
"""
import argparse
import json
import os
import re
import socket
import subprocess
import sys

SESSION_FLAGS = {"-r", "--resume", "--session-id"}            # take a value
SESSION_SWITCHES = {"-c", "--continue", "--fork-session", "--last", "-p", "--print"}
UNSAFE = {"--dangerously-skip-permissions", "--yolo", "--dangerously-bypass-approvals-and-sandbox"}
AUTO_TAB_LABEL = re.compile(r"^\d+ · ")                        # Herdr's automatic tab label


def die(msg):
    print(f"migrdr: {msg}", file=sys.stderr)
    sys.exit(1)


def call(sock_path, method, params, timeout=30):
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        s.connect(sock_path)
        s.sendall((json.dumps({"id": "migrdr", "method": method, "params": params}) + "\n").encode())
        buf = b""
        while not buf.endswith(b"\n"):
            chunk = s.recv(65536)
            if not chunk:
                break
            buf += chunk
    resp = json.loads(buf)
    if "error" in resp:
        raise RuntimeError(f"{method}: {resp['error'].get('code')}: {resp['error'].get('message')}")
    return resp["result"]


def sessions():
    out = subprocess.run(["herdr", "session", "list", "--json"], check=True, capture_output=True, text=True)
    return {s["name"]: s for s in json.loads(out.stdout)["sessions"]}


def socket_for(name):
    s = sessions().get(name)
    if not s:
        die(f"no session named {name!r}. Sessions: {', '.join(sessions())}")
    if not s["running"]:
        die(f"session {name!r} is not running")
    return s["socket_path"]


def snapshot(sock):
    return call(sock, "session.snapshot", {})["snapshot"]


def leaves(node):
    if node["type"] == "pane":
        return [node]
    return leaves(node["first"]) + leaves(node["second"])


def find_leaf(node, pane_id):
    return next(l for l in leaves(node) if l.get("pane_id") == pane_id)


def carried_args(argv):
    """Keep the user's launch flags. Drop session flags, unsafe flags, and a likely prompt."""
    out, i, args = [], 0, argv[1:]
    if args[:1] == ["resume"]:                                 # codex resume <id>
        args = args[2:] if len(args) > 1 and not args[1].startswith("-") else args[1:]
    while i < len(args):
        a = args[i]
        if a in SESSION_FLAGS:
            i += 2
            continue
        if a in SESSION_SWITCHES or a in UNSAFE or a.split("=")[0] in SESSION_FLAGS:
            i += 1
            continue
        prev = args[i - 1] if i else ""
        if not a.startswith("-") and not prev.startswith("-"):  # positional: a prompt
            i += 1
            continue
        out.append(a)
        i += 1
    return out


def resume_args(kind, session_id, argv):
    rest = carried_args(argv) if argv and os.path.basename(argv[0]) == kind else []
    if kind == "claude":
        return ["--resume", session_id] + rest
    if kind == "codex":
        if not {"-a", "--ask-for-approval"} & set(rest):
            rest += ["-a", "never"]
        if not {"-s", "--sandbox"} & set(rest):
            rest += ["-s", "workspace-write"]
        return ["resume", session_id] + rest
    return None


def describe_leaf(sock, snap, leaf, caller):
    pid = leaf["pane_id"]
    agent = next((a for a in snap["agents"] if a["pane_id"] == pid), None)
    info = call(sock, "pane.process_info", {"pane_id": pid})["process_info"]
    fg = info.get("foreground_processes") or []
    shell_idle = info.get("foreground_process_group_id") == info.get("shell_pid")
    m = {"caller": pid == caller}
    if agent:
        kind, sess = agent["agent"], (agent.get("agent_session") or {}).get("value")
        argv = fg[0]["argv"] if fg else []
        args = resume_args(kind, sess, argv) if sess else None
        name = agent.get("name") or re.sub(r"[^a-z0-9]", "", f"{kind}{pid}".lower())[:32]
        m.update(agent=kind, name=name, status=agent["agent_status"], session_id=sess, args=args)
        if args is None:
            m["dropped"] = " ".join(argv) or kind              # no resumable session
    elif not shell_idle and fg:
        m["dropped"] = fg[0]["cmdline"]
    leaf["migrdr"] = m
    return leaf


def workspace_source(snap, ws):
    wt = ws.get("worktree")
    return {
        "source_id": ws["workspace_id"],
        "label": ws["label"],
        "kind": ("linked" if wt["is_linked_worktree"] else "primary") if wt else "plain",
        "checkout": wt["checkout_path"] if wt else None,
        "repo_root": wt["repo_root"] if wt else None,
        "tabs": [],
    }


def plan(args):
    sock = os.environ.get("HERDR_SOCKET_PATH") or die("HERDR_SOCKET_PATH is not set")
    source = os.environ.get("HERDR_SESSION", "default")
    if args.target == source:
        die(f"already in session {source!r}")
    target_sock = socket_for(args.target)
    caller = os.environ.get("HERDR_PANE_ID")
    pane_id = args.pane or caller or die("pass --pane")
    snap, tsnap = snapshot(sock), snapshot(target_sock)

    pane = next((p for p in snap["panes"] if p["pane_id"] == pane_id), None) or die(f"pane {pane_id} not found")
    by_id = {w["workspace_id"]: w for w in snap["workspaces"]}
    ws = by_id[pane["workspace_id"]]
    if args.scope == "group" and ws.get("worktree"):
        key = ws["worktree"]["repo_key"]
        group = [w for w in snap["workspaces"] if (w.get("worktree") or {}).get("repo_key") == key]
        group.sort(key=lambda w: (w["worktree"]["is_linked_worktree"], w["number"]))
    else:
        group = [ws]

    out = {"source_session": source, "target_session": args.target, "scope": args.scope,
           "caller_pane": caller, "workspaces": [], "close": []}
    for w in group:
        entry = workspace_source(snap, w)
        tabs = sorted((t for t in snap["tabs"] if t["workspace_id"] == w["workspace_id"]), key=lambda t: t["number"])
        if args.scope in ("tab", "pane"):
            tabs = [t for t in tabs if t["tab_id"] == pane["tab_id"]]
        for t in tabs:
            root = call(sock, "layout.export", {"tab_id": t["tab_id"]})["layout"]["root"]
            if args.scope == "pane":
                root = find_leaf(root, pane_id)
            for leaf in leaves(root):
                describe_leaf(sock, snap, leaf, caller)
            label = None if args.scope == "pane" or AUTO_TAB_LABEL.match(t["label"]) else t["label"]
            entry["tabs"].append({"source_tab_id": t["tab_id"], "label": label, "root": root})
        if not entry["checkout"]:
            entry["checkout_cwd"] = leaves(entry["tabs"][0]["root"])[0].get("cwd") if entry["tabs"] else None
        match = [tw for tw in tsnap["workspaces"]
                 if entry["checkout"] and (tw.get("worktree") or {}).get("checkout_path") == entry["checkout"]]
        entry["target_workspace_id"] = match[0]["workspace_id"] if match else None
        out["workspaces"].append(entry)

    s = f"herdr --session {source}"
    first = group[0]["workspace_id"]
    if args.scope == "pane":
        out["close"] = [f"{s} pane close {pane_id}"]
    elif args.scope == "tab":
        out["close"] = [f"{s} tab close {pane['tab_id']}"]
    elif args.scope == "group" and len(group) > 1:
        out["close"] = [f"{s} workspace close {first} --group"]
    else:
        out["close"] = [f"{s} workspace close {first}"]
    json.dump(out, sys.stdout, indent=2)
    print()


def strip(node):
    if node["type"] == "pane":
        m = node.get("migrdr", {})
        clean = {k: v for k, v in node.items() if k in ("type", "label", "cwd", "command")}
        if m.get("agent"):
            clean.pop("command", None)                         # agent start types the agent into a shell
        return clean
    return {**{k: node[k] for k in ("type", "direction", "ratio")},
            "first": strip(node["first"]), "second": strip(node["second"])}


def open_workspace(tsock, ws):
    """Return (workspace_id, root tab to replace or None) in the target session."""
    if ws["target_workspace_id"]:
        return ws["target_workspace_id"], None
    if ws["kind"] == "linked":
        r = call(tsock, "worktree.open", {"cwd": ws["repo_root"], "path": ws["checkout"], "label": ws["label"]})
    else:
        r = call(tsock, "workspace.create", {"cwd": ws["checkout"] or ws.get("checkout_cwd"), "label": ws["label"]})
    wid = r["workspace"]["workspace_id"]
    tabs = call(tsock, "tab.list", {"workspace_id": wid})["tabs"]
    return wid, tabs[0]["tab_id"] if tabs else None


def apply(args):
    with open(args.plan) as f:
        p = json.load(f)
    tsock = socket_for(p["target_session"])
    live = {a.get("name") for a in snapshot(tsock)["agents"]}
    result, starts = {"target_session": p["target_session"], "workspaces": [], "panes": []}, []
    for ws in p["workspaces"]:
        wid, replace = open_workspace(tsock, ws)
        result["workspaces"].append({"source_id": ws["source_id"], "target_id": wid})
        for tab in ws["tabs"]:
            params = {"root": strip(tab["root"])}
            params.update({"tab_id": replace} if replace else {"workspace_id": wid})
            if tab["label"]:
                params["tab_label"] = tab["label"]
            layout = call(tsock, "layout.apply", params)["layout"]
            replace = None
            for old, new in zip(leaves(tab["root"]), leaves(layout["root"])):
                row = {"source_pane": old["pane_id"], "target_pane": new["pane_id"], **old.get("migrdr", {})}
                result["panes"].append(row)
                if row.get("args") is not None:
                    starts.append(row)
    starts.sort(key=lambda r: r["caller"])                     # the calling agent resumes last
    for row in starts:
        name, n = row["name"], 2
        while name in live:
            name, n = f"{row['name'][:29]}-{n}", n + 1
        live.add(name)
        row["name"] = name
        try:
            call(tsock, "agent.start", {"name": name, "kind": row["agent"], "pane_id": row["target_pane"],
                                        "args": row["args"], "timeout_ms": 60000}, timeout=90)
            row["started"] = "ok"
        except RuntimeError as e:
            row["started"] = str(e)
    json.dump(result, sys.stdout, indent=2)
    print()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    pp = sub.add_parser("plan")
    pp.add_argument("target")
    pp.add_argument("--scope", choices=["group", "workspace", "tab", "pane"], default="group")
    pp.add_argument("--pane", help="pane that selects the scope (default: the calling pane)")
    pa = sub.add_parser("apply")
    pa.add_argument("plan")
    a = ap.parse_args()
    plan(a) if a.cmd == "plan" else apply(a)


if __name__ == "__main__":
    main()
