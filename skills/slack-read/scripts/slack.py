#!/usr/bin/env python3
"""Read Slack channels and threads as plain text through the Slack Web API.

Needs SLACK_TOKEN (a user token with channels:history, groups:history, channels:read, groups:read, users:read).

  slack.py channels [FILTER]
  slack.py history CHANNEL [--since YYYY-MM-DD|7d] [--until YYYY-MM-DD] [--no-threads] [--json]
  slack.py thread CHANNEL TS        (or: slack.py thread PERMALINK)
"""
import argparse, datetime, json, os, re, sys, time, urllib.error, urllib.parse, urllib.request

CACHE = os.path.expanduser("~/.cache/slack-read")
TOKEN = os.environ.get("SLACK_TOKEN") or sys.exit("SLACK_TOKEN is not set")


def call(method, **params):
    while True:
        req = urllib.request.Request("https://slack.com/api/" + method, data=urllib.parse.urlencode(params).encode(),
                                     headers={"Authorization": f"Bearer {TOKEN}"})
        try:
            with urllib.request.urlopen(req) as r:
                res = json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(int(e.headers.get("Retry-After", "5")))
                continue
            raise
        if res.get("ok"):
            return res
        if res.get("error") == "ratelimited":
            time.sleep(5)
            continue
        sys.exit(f"{method} failed: {res.get('error')}")


def paginate(method, key, **params):
    cursor = None
    while True:
        res = call(method, **params, **({"cursor": cursor} if cursor else {}))
        yield from res.get(key, [])
        cursor = (res.get("response_metadata") or {}).get("next_cursor")
        if not cursor:
            return


def cached(name, build):
    path = os.path.join(CACHE, name)
    if os.path.exists(path) and time.time() - os.path.getmtime(path) < 86400:
        return json.load(open(path))
    data = build()
    os.makedirs(CACHE, exist_ok=True)
    json.dump(data, open(path, "w"))
    return data


def channels():
    return cached("channels.json", lambda: {
        c["name"]: {"id": c["id"], "member": c.get("is_member", False), "private": c.get("is_private", False)}
        for c in paginate("conversations.list", "channels", types="public_channel,private_channel",
                          exclude_archived="true", limit=1000)})


USERS = None


def user(uid):
    global USERS
    if USERS is None:
        USERS = cached("users.json", lambda: {
            u["id"]: u.get("real_name") or u["profile"].get("real_name") or u["name"]
            for u in paginate("users.list", "members", limit=1000)})
    if uid not in USERS:  # external (Slack Connect) users are missing from users.list
        try:
            u = call("users.info", user=uid)["user"]
            USERS[uid] = u.get("real_name") or u["profile"].get("display_name") or u["name"]
        except SystemExit:
            USERS[uid] = uid
    return USERS[uid]


def channel_id(name):
    name = name.lstrip("#")
    if re.fullmatch(r"[CG][A-Z0-9]+", name):
        return name
    info = channels().get(name) or sys.exit(f"no channel named {name}. Run: slack.py channels {name}")
    return info["id"]


def clean(text):
    text = re.sub(r"<@(\w+)(\|[^>]*)?>", lambda m: "@" + user(m.group(1)), text or "")
    text = re.sub(r"<#\w+\|([^>]*)>", r"#\1", text)
    text = re.sub(r"<(https?://[^|>]+)\|([^>]+)>",
                  lambda m: m.group(1) if m.group(2) == m.group(1) else f"{m.group(2)} ({m.group(1)})", text)
    text = re.sub(r"<(https?://[^>]+)>", r"\1", text)
    return text.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")


def line(m, indent=""):
    when = datetime.datetime.fromtimestamp(float(m["ts"])).strftime("%Y-%m-%d %H:%M")
    who = user(m["user"]) if m.get("user") else m.get("username") or m.get("bot_id") or "?"
    files = "".join(f" [file: {f.get('name')}]" for f in m.get("files", []))
    body = clean(m.get("text")).replace("\n", "\n" + indent + "  ")
    return f"{indent}[{when}] {who}: {body}{files}"


def link(base, cid, ts):
    return f"{base}archives/{cid}/p{ts.replace('.', '')}"


def replies(cid, ts):
    return [r for r in paginate("conversations.replies", "messages", channel=cid, ts=ts, limit=200) if r["ts"] != ts]


def when(s, default):
    if not s:
        return default
    if m := re.fullmatch(r"(\d+)d", s):
        return time.time() - int(m.group(1)) * 86400
    return datetime.datetime.strptime(s, "%Y-%m-%d").timestamp()


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("channels")
    c.add_argument("filter", nargs="?", default="")
    h = sub.add_parser("history")
    h.add_argument("channel")
    h.add_argument("--since", help="YYYY-MM-DD or Nd (default 7d)")
    h.add_argument("--until", help="YYYY-MM-DD (default now)")
    h.add_argument("--no-threads", action="store_true")
    h.add_argument("--json", action="store_true")
    t = sub.add_parser("thread")
    t.add_argument("channel", help="channel name, id, or a message permalink")
    t.add_argument("ts", nargs="?")
    a = p.parse_args()

    if a.cmd == "channels":
        for name, info in sorted(channels().items()):
            if a.filter in name:
                print(f"{name}\t{info['id']}\t{'member' if info['member'] else 'not a member'}")
        return

    base = call("auth.test")["url"]
    if a.cmd == "thread":
        if m := re.search(r"archives/(\w+)/p(\d{10})(\d{6})", a.channel):
            cid, ts = m.group(1), f"{m.group(2)}.{m.group(3)}"
        else:
            cid, ts = channel_id(a.channel), a.ts or sys.exit("thread needs TS or a permalink")
        msgs = list(paginate("conversations.replies", "messages", channel=cid, ts=ts, limit=200))
        print(f"=== {link(base, cid, ts)}")
        for i, m in enumerate(msgs):
            print(line(m, "" if i == 0 else "    "))
        return

    cid = channel_id(a.channel)
    oldest, latest = when(a.since, time.time() - 7 * 86400), when(a.until, time.time())
    msgs = sorted(paginate("conversations.history", "messages", channel=cid, oldest=f"{oldest:.6f}",
                           latest=f"{latest:.6f}", limit=200), key=lambda m: float(m["ts"]))
    for m in msgs:
        if m.get("reply_count") and not a.no_threads:
            m["replies"] = replies(cid, m["ts"])
    if a.json:
        json.dump(msgs, sys.stdout, indent=1)
        return
    for m in msgs:
        print(f"\n=== {link(base, cid, m['ts'])}\n{line(m)}")
        for r in m.get("replies", []):
            print(line(r, "    "))


if __name__ == "__main__":
    main()
