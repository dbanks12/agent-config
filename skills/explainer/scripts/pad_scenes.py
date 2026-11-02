#!/usr/bin/env python3
"""Add a beat of silence at the end of every scene but the last, in narration.mp3 and timings.json.

Usage: pad_scenes.py <abs work dir> [seconds, default 1.5]

Learners rarely pause on their own, and eleven_v4 has no break tag. The silence goes into the gap
between a scene's last word and the next scene's first word, and the scene keeps the screen, so its
finished drawing holds for the beat. The alignment's word ends run early, so each cut goes to the middle
of the longest silence near the boundary. A boundary with no silence gets no beat. Every later scene and word shifts by the silence so far.
timings.json records "padded", so a rerun leaves padded audio alone. narrate.sh rewrites both files
unpadded, and the next run pads them again. Captions mode already has a beat between scenes.
"""
import array
import json
import math
import os
import subprocess
import sys


RATE = 16000
FRAME = 0.01  # seconds
QUIET = -50  # dBFS


def quiet_frames(audio):
    pcm = array.array("h", subprocess.run(["ffmpeg", "-loglevel", "error", "-i", audio, "-ac", "1", "-ar", str(RATE),
                                           "-f", "s16le", "-"], check=True, capture_output=True).stdout)
    n = int(RATE * FRAME)
    rms = (math.sqrt(sum(x * x for x in pcm[i:i + n]) / n) for i in range(0, len(pcm) - n + 1, n))
    return [r < 32768 * 10 ** (QUIET / 20) for r in rms]


def silence(quiet, a, b):
    """The middle of the longest quiet run between a and b seconds, or None."""
    best, run = None, 0
    for i in range(max(0, int(a / FRAME)), min(len(quiet), int(b / FRAME))):
        run = run + 1 if quiet[i] else 0
        if run and (best is None or run > best[1]):
            best = (i, run)
    return None if best is None else (best[0] - best[1] / 2 + 1) * FRAME


def main(w, gap):
    path = f"{w}/timings.json"
    with open(path) as f:
        t = json.load(f)
    if not t.get("audio") or t.get("padded") or len(t["scenes"]) < 2:
        return
    words, scenes = t["words"], t["scenes"]
    audio = f"{w}/{t['audio']}"
    quiet = quiet_frames(audio)
    cuts = []
    for a, b in zip(scenes, scenes[1:]):
        last = [x for x in words if a["start"] <= x["s"] < a["end"]]
        first = [x for x in words if b["start"] <= x["s"] < b["end"]]
        # Approximate timings have no words: search around the scene boundary.
        lo, hi = (last[-1]["s"], first[0]["e"]) if last and first else (b["start"] - 0.5, b["start"] + 0.5)
        cuts.append(silence(quiet, lo, hi))
    keep = [i for i, c in enumerate(cuts) if c is not None]
    cuts = [cuts[i] for i in keep]
    if not cuts:
        return
    edges = [0.0, *cuts]
    # 5 ms fades on both sides of each beat, so the step into digital silence never clicks.
    fade = 0.005
    fade_in = f"afade=t=in:d={fade},"
    parts = [f"[0:a]atrim=start={s}:end={e},asetpts=PTS-STARTPTS,{fade_in if i else ''}"
             f"afade=t=out:st={e - s - fade:.3f}:d={fade},apad=pad_dur={gap}[p{i}]"
             for i, (s, e) in enumerate(zip(edges, edges[1:]))]
    parts.append(f"[0:a]atrim=start={edges[-1]},asetpts=PTS-STARTPTS,{fade_in[:-1]}[p{len(cuts)}]")
    graph = ";".join(parts) + ";" + "".join(f"[p{i}]" for i in range(len(cuts) + 1)) + f"concat=n={len(cuts) + 1}:v=0:a=1[out]"
    tmp = f"{audio}.padded.mp3"
    rate = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=bit_rate",
                           "-of", "csv=p=0", audio], check=True, capture_output=True, text=True).stdout.strip()
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", audio, "-filter_complex", graph,
                    "-map", "[out]", "-c:a", "libmp3lame", "-b:a", rate or "64000", tmp], check=True)
    shift = lambda x: x + gap * sum(1 for c in cuts if c <= x)
    for x in words:
        x["s"], x["e"] = round(shift(x["s"]), 3), round(shift(x["e"]), 3)
    # Scene i+1 starts in the middle of its beat, or at its shifted start when it has none.
    for i, s in enumerate(scenes):
        s["start"], s["end"] = round(shift(s["start"]), 3), round(shift(s["end"]), 3)
    for k, i in enumerate(keep):
        scenes[i]["end"] = scenes[i + 1]["start"] = round(cuts[k] + gap * (k + 1), 3)
    probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", tmp],
                           check=True, capture_output=True, text=True)
    t["duration"] = scenes[-1]["end"] = round(float(probe.stdout), 3)
    t["padded"] = gap
    os.replace(tmp, audio)
    with open(path, "w") as f:
        json.dump(t, f)
    print(f"pad_scenes: {len(cuts)} beats of {gap} s, {len(scenes) - 1 - len(cuts)} boundaries without silence, {t['duration']:.1f} s")


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3) or not sys.argv[1].startswith("/"):
        sys.exit("usage: pad_scenes.py <abs work dir> [seconds]")
    main(sys.argv[1], float(sys.argv[2]) if len(sys.argv) == 3 else 1.5)
