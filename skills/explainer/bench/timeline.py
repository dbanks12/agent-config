#!/usr/bin/env python3
"""Split the wall time of a Claude Code session into model, tool, and wait time, by explainer step.

Usage: timeline.py <transcript.jsonl> [--from ISO] [--to ISO] [--calls] [--json]

A turn starts at a human prompt and ends at the next one. Background-task notifications continue the
current turn, so time spent waiting on a background job counts as agent time. Time after a turn's last
record, before the next human prompt, is the human's and is left out.
"""
import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime

# First match wins. Patterns run on the tool name plus its JSON input.
CATEGORIES = [
    ("review", r"call-codex|call-claude|codex (exec|review)|\bcodex\b.*-e high|claude (-p|--print)|review-?\d*\.prompt"),
    ("narrate", r"narrate\.sh|tts\.ts"),
    ("style-board", r"styles\.html|build_styles"),
    ("scene-draw", r"place\.py|scenes\.py|draw\.py|\.excalidraw|mcp-excalidraw-server|tag_svg|render-scenes|tag-scenes|sheet\.sh"),
    ("qa", r"playwright|chromium|qa\.(m?js|cjs|py)|/qa/|\bqa\b"),
    ("publish", r"^Artifact"),
    ("build", r"page\.html|build[-_]?\w*\.py|template\.html|explainer\.html|player\.js|scenes\.js|cues"),
    ("script", r"narration(\.v\d)?\.json|manifest\.json"),
    ("skill-load", r"^Skill"),
    ("read", r"^(Read|Grep|Glob)|\b(cat|sed -n|grep|head|ls|find|rg)\b"),
]
CAT_RE = [(name, re.compile(p, re.S)) for name, p in CATEGORIES]
# The skill sets manifest.json `status` at every step. A tool call that writes one starts that phase.
STATUS_RE = re.compile(r'status\W{1,8}(scripting|reviewing|styling|narrating|building|qa|ready|failed)\b')


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def category(name, inp):
    text = name + " " + json.dumps(inp)
    for cat, rx in CAT_RE:
        if rx.search(text):
            return cat
    return "other"


def human_prompt(r):
    if r.get("type") != "user" or r.get("isMeta") or r.get("isCompactSummary"):
        return False
    c = r["message"].get("content")
    if isinstance(c, list):
        c = " ".join(x.get("text", "") for x in c if isinstance(x, dict) and x.get("type") == "text")
        if not c:
            return False
    return not c.lstrip().startswith(("<task-notification>", "<bash-", "<local-command", "This session is being continued"))


def prompt_text(r):
    c = r["message"]["content"]
    if isinstance(c, list):
        c = " ".join(x.get("text", "") for x in c if isinstance(x, dict))
    return re.sub(r"\s+", " ", c)[:90]


def analyze(records, t_from=None, t_to=None):
    records = [r for r in records if r.get("timestamp")]
    records = [r for r in records if (not t_from or r["timestamp"] >= t_from) and (not t_to or r["timestamp"] <= t_to)]
    if not records:
        sys.exit("timeline: no records in range")

    requests = {}  # request id -> {start, end, cats}
    calls = {}  # tool_use id -> call
    order = []
    phases = [(ts(records[0]["timestamp"]), "start")]
    for r in records:
        t = ts(r["timestamp"])
        typ = r.get("type")
        if typ == "api-request":
            requests[r["id"]] = {"start": t, "end": t, "cats": [], "out": 0, "source": r.get("querySource")}
        elif typ == "assistant":
            req = requests.get(r.get("requestRef"))
            if req:
                req["end"] = max(req["end"], t)
                req["out"] = max(req["out"], (r["message"].get("usage") or {}).get("output_tokens", 0))
            for c in r["message"].get("content", []):
                if c.get("type") == "tool_use":
                    bg = bool(c["input"].get("run_in_background")) if isinstance(c["input"], dict) else False
                    m = STATUS_RE.findall(json.dumps(c["input"]))
                    if m:
                        phases.append((t, m[-1]))
                    call = {"id": c["id"], "name": c["name"], "cat": category(c["name"], c["input"]), "start": t,
                            "end": None, "bg": bg, "bg_end": None, "input": json.dumps(c["input"])[:160]}
                    calls[c["id"]] = call
                    order.append(call)
                    if req:
                        req["cats"].append(call["cat"])
        elif typ == "user":
            c = r["message"].get("content")
            if isinstance(c, list):
                for x in c:
                    if isinstance(x, dict) and x.get("type") == "tool_result" and x.get("tool_use_id") in calls:
                        calls[x["tool_use_id"]]["end"] = t
            elif isinstance(c, str) and c.lstrip().startswith("<task-notification>"):
                m = re.search(r"<tool-use-id>([^<]+)</tool-use-id>", c)
                if m and m.group(1) in calls:
                    calls[m.group(1)]["bg_end"] = t

    # Turns: human prompt to the last record before the next human prompt.
    turns = []
    for r in records:
        if human_prompt(r):
            turns.append({"start": ts(r["timestamp"]), "prompt": prompt_text(r), "last": ts(r["timestamp"])})
        elif turns and r.get("type") in ("assistant", "user"):
            # Only agent activity extends a turn. Bookkeeping records can land minutes later.
            turns[-1]["last"] = ts(r["timestamp"])
    if not turns:
        turns = [{"start": ts(records[0]["timestamp"]), "prompt": "(no human prompt in range)", "last": ts(records[-1]["timestamp"])}]

    def in_turn(t, turn):
        return turn["start"] <= t <= turn["last"]

    out = []
    for turn in turns:
        reqs = [q for q in requests.values() if in_turn(q["start"], turn)]
        tcalls = [c for c in order if in_turn(c["start"], turn) and c["end"]]
        agent = turn["last"] - turn["start"]
        # Busy intervals: model requests and foreground tools. Their union, against agent time, gives the gaps.
        model_iv = [(q["start"], q["end"]) for q in reqs]
        tool_iv = [(c["start"], c["end"]) for c in tcalls if not c["bg"]]
        bg_iv = [(c["start"], min(c["bg_end"], turn["last"])) for c in tcalls if c["bg"] and c["bg_end"]]
        by_cat = defaultdict(lambda: {"model": 0.0, "tool": 0.0, "bg": 0.0, "calls": 0, "requests": 0})
        for q in reqs:
            cat = q["cats"][0] if q["cats"] else "answer"
            by_cat[cat]["model"] += q["end"] - q["start"]
            by_cat[cat]["requests"] += 1
        # Parallel calls overlap, so per-category tool time is the union of that category's intervals.
        for cat in {c["cat"] for c in tcalls}:
            by_cat[cat]["tool"] += union([(c["start"], c["end"]) for c in tcalls if c["cat"] == cat and not c["bg"]])
            by_cat[cat]["bg"] += union([(c["start"], c["bg_end"]) for c in tcalls if c["cat"] == cat and c["bg"] and c["bg_end"]])
            by_cat[cat]["calls"] += sum(1 for c in tcalls if c["cat"] == cat)
        busy = union(model_iv + tool_iv)
        # Wall time per phase, with the model and foreground tool time inside it.
        marks = [p for p in phases if in_turn(p[0], turn)] or [(turn["start"], "start")]
        marks = [(turn["start"], marks[0][1] if marks[0][0] <= turn["start"] else "start")] + [p for p in marks if p[0] > turn["start"]]
        by_phase = []
        for i, (p_start, name) in enumerate(marks):
            p_end = marks[i + 1][0] if i + 1 < len(marks) else turn["last"]
            clip = lambda iv: [(max(a, p_start), min(b, p_end)) for a, b in iv if b > p_start and a < p_end]
            if by_phase and by_phase[-1]["phase"] == name:
                prev = by_phase.pop()
                p_start = prev["start"]
            by_phase.append({"phase": name, "start": p_start, "wall": p_end - p_start,
                             "model": union(clip(model_iv)), "tool": union(clip(tool_iv)), "bg": union(clip(bg_iv))})
        out.append({
            "prompt": turn["prompt"],
            "start": datetime.fromtimestamp(turn["start"]).isoformat(timespec="seconds"),
            "agent_s": agent,
            "model_s": union(model_iv),
            "tool_s": union(tool_iv),
            "bg_only_s": union(model_iv + tool_iv + bg_iv) - busy,
            "gap_s": agent - union(model_iv + tool_iv + bg_iv),
            "requests": len(reqs),
            "output_tokens": sum(q["out"] for q in reqs),
            "calls": len(tcalls),
            "by_category": dict(by_cat),
            "by_phase": by_phase,
            "call_list": [{**c, "dur": c["end"] - c["start"], "bg_dur": (c["bg_end"] - c["start"]) if c["bg_end"] else None} for c in tcalls],
        })
    return out


def union(iv):
    total, cur_s, cur_e = 0.0, None, None
    for s, e in sorted(iv):
        if cur_e is None or s > cur_e:
            if cur_e is not None:
                total += cur_e - cur_s
            cur_s, cur_e = s, e
        else:
            cur_e = max(cur_e, e)
    if cur_e is not None:
        total += cur_e - cur_s
    return total


def fmt(s):
    return f"{int(s // 60)}m{int(s % 60):02d}s"


def report(turns, show_calls):
    tot = defaultdict(float)
    for i, t in enumerate(turns, 1):
        print(f"\nTurn {i} at {t['start']}: {t['prompt']}")
        print(f"  agent {fmt(t['agent_s'])} = model {fmt(t['model_s'])} + tools {fmt(t['tool_s'])}"
              f" + waiting on background {fmt(t['bg_only_s'])} + gaps {fmt(t['gap_s'])}"
              f"  ({t['requests']} requests, {t['output_tokens']} output tokens, {t['calls']} tool calls)")
        print(f"  {'category':12} {'model':>7} {'tool':>7} {'bg':>7} {'req':>4} {'calls':>5}")
        for cat, v in sorted(t["by_category"].items(), key=lambda kv: -(kv[1]["model"] + kv[1]["tool"])):
            print(f"  {cat:12} {fmt(v['model']):>7} {fmt(v['tool']):>7} {fmt(v['bg']):>7} {v['requests']:>4} {v['calls']:>5}")
        if len(t["by_phase"]) > 1:
            print(f"  {'phase':12} {'wall':>7} {'model':>7} {'tool':>7} {'bg':>7}")
            for p in t["by_phase"]:
                print(f"  {p['phase']:12} {fmt(p['wall']):>7} {fmt(p['model']):>7} {fmt(p['tool']):>7} {fmt(p['bg']):>7}")
        if show_calls:
            for c in t["call_list"]:
                bg = f" bg {c['bg_dur']:.0f}s" if c["bg_dur"] else ""
                print(f"    {c['cat']:11} {c['dur']:6.1f}s{bg} {c['name']:8} {c['input'][:110]}")
        for k in ("agent_s", "model_s", "tool_s", "bg_only_s", "gap_s"):
            tot[k] += t[k]
    if len(turns) > 1:
        print(f"\nAll turns: agent {fmt(tot['agent_s'])} = model {fmt(tot['model_s'])} + tools {fmt(tot['tool_s'])}"
              f" + background {fmt(tot['bg_only_s'])} + gaps {fmt(tot['gap_s'])}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("transcript")
    ap.add_argument("--from", dest="t_from")
    ap.add_argument("--to", dest="t_to")
    ap.add_argument("--calls", action="store_true", help="list every tool call")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    with open(a.transcript) as f:
        records = [json.loads(line) for line in f if line.strip()]
    turns = analyze(records, a.t_from, a.t_to)
    if a.json:
        json.dump(turns, sys.stdout, indent=1)
    else:
        report(turns, a.calls)


if __name__ == "__main__":
    main()
