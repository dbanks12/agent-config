#!/usr/bin/env python3
"""Add a beat of silence at the end of every scene but the last, in narration.mp3 and timings.json.

Usage: pad_scenes.py <abs work dir> [seconds, default 0.6]

Learners rarely pause on their own, and eleven_v4 has no break tag. The silence goes into the gap
between a scene's last word and the next scene's first word, and the scene keeps the screen, so its
finished drawing holds for the beat. Every later scene and word shifts by the silence so far.
timings.json records "padded", so a rerun leaves padded audio alone. narrate.sh rewrites both files
unpadded, and the next run pads them again. Captions mode already has a beat between scenes.
"""
import json
import os
import subprocess
import sys


def main(w, gap):
    path = f"{w}/timings.json"
    with open(path) as f:
        t = json.load(f)
    if not t.get("audio") or t.get("padded") or len(t["scenes"]) < 2:
        return
    words, scenes = t["words"], t["scenes"]
    cuts = []
    for a, b in zip(scenes, scenes[1:]):
        last = [x for x in words if a["start"] <= x["s"] < a["end"]]
        first = [x for x in words if b["start"] <= x["s"] < b["end"]]
        # Approximate timings have no words: cut at the scene boundary.
        cuts.append((last[-1]["e"] + first[0]["s"]) / 2 if last and first else b["start"])
    audio = f"{w}/{t['audio']}"
    edges = [0.0, *cuts]
    parts = [f"[0:a]atrim=start={s}:end={e},asetpts=PTS-STARTPTS,apad=pad_dur={gap}[p{i}]"
             for i, (s, e) in enumerate(zip(edges, edges[1:]))]
    parts.append(f"[0:a]atrim=start={edges[-1]},asetpts=PTS-STARTPTS[p{len(cuts)}]")
    graph = ";".join(parts) + ";" + "".join(f"[p{i}]" for i in range(len(cuts) + 1)) + f"concat=n={len(cuts) + 1}:v=0:a=1[out]"
    tmp = f"{audio}.padded.mp3"
    rate = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=bit_rate",
                           "-of", "csv=p=0", audio], check=True, capture_output=True, text=True).stdout.strip()
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", audio, "-filter_complex", graph,
                    "-map", "[out]", "-c:a", "libmp3lame", "-b:a", rate or "64000", tmp], check=True)
    shift = lambda x: x + gap * sum(1 for c in cuts if c <= x)
    for x in words:
        x["s"], x["e"] = round(shift(x["s"]), 3), round(shift(x["e"]), 3)
    for i, s in enumerate(scenes):
        if i:
            s["start"] = round(cuts[i - 1] + gap * i, 3)
        if i < len(cuts):
            s["end"] = round(cuts[i] + gap * (i + 1), 3)
    probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", tmp],
                           check=True, capture_output=True, text=True)
    t["duration"] = scenes[-1]["end"] = round(float(probe.stdout), 3)
    t["padded"] = gap
    os.replace(tmp, audio)
    with open(path, "w") as f:
        json.dump(t, f)
    print(f"pad_scenes: {len(cuts)} beats of {gap} s, {t['duration']:.1f} s")


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3) or not sys.argv[1].startswith("/"):
        sys.exit("usage: pad_scenes.py <abs work dir> [seconds]")
    main(sys.argv[1], float(sys.argv[2]) if len(sys.argv) == 3 else 0.6)
