"""Narrate a script on this machine, and time its words with Whisper. Free, and sends nothing.

Usage: local_tts.py <narration.json> <out-dir> [--engine chatterbox|kokoro] [--voice <voice>]
chatterbox (the default) runs `chatterbox-say` (linux/chatterbox in agent-config) on the GPU, in chatterbox-say's default voice.
kokoro runs in this process, voice am_michael. Run it with the Sill core's Python (finish.sh does): it has
kokoro-onnx and faster-whisper, and the models sit in ~/.cache/herdr-manager. Writes narration.mp3 and the
same timings.json as tts.ts. Audio tags are dropped. Each scene's audio and word times are cached by hash
of engine, voice, and text. Exit 3 means an engine, the Sill Python packages, or the models are missing.
"""
import difflib
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

MODELS = Path.home() / ".cache" / "herdr-manager"
VOICES = {"chatterbox": None, "kokoro": "am_michael"}  # None: chatterbox-say picks, and names it
JOIN = 0.3  # silence between scenes, so pad_scenes.py finds a quiet cut


def fail(code, msg):
    print(f"local_tts: {msg}", file=sys.stderr)
    sys.exit(code)


def norm(w):
    return re.sub(r"[\W_]", "", w.lower())


def align(script, heard):
    """Gives each script word the time of the Whisper word it matches, and spreads the rest between."""
    out = [None] * len(script)
    sm = difflib.SequenceMatcher(a=[norm(w) for w in script], b=[norm(h["w"]) for h in heard], autojunk=False)
    for a, b, n in sm.get_matching_blocks():
        for k in range(n):
            out[a + k] = (heard[b + k]["s"], heard[b + k]["e"])
    known = [i for i, x in enumerate(out) if x]
    for i, x in enumerate(out):
        if x:
            continue
        lo = max((j for j in known if j < i), default=None)
        hi = min((j for j in known if j > i), default=None)
        t0 = out[lo][1] if lo is not None else (heard[0]["s"] if heard else 0.0)
        t1 = out[hi][0] if hi is not None else (heard[-1]["e"] if heard else t0 + 0.4 * len(script))
        gap = (hi if hi is not None else len(script)) - (lo if lo is not None else -1)
        step = (t1 - t0) / gap
        k = i - (lo if lo is not None else -1)
        out[i] = (t0 + step * (k - 1), t0 + step * k)
    return [{"w": w, "s": round(s, 3), "e": round(e, 3)} for w, (s, e) in zip(script, out)]


def main():
    args = sys.argv[1:]
    opts = {"--engine": "chatterbox", "--voice": None}
    for k in opts:
        if k in args:
            i = args.index(k)
            opts[k] = args[i + 1]
            del args[i : i + 2]
    engine = opts["--engine"]
    args = [a for a in args if a != "--long"]  # neither engine has a request limit
    if len(args) != 2 or engine not in VOICES:
        fail(1, "usage: local_tts.py <narration.json> <out-dir> [--engine chatterbox|kokoro] [--voice <voice>]")
    say = shutil.which("chatterbox-say")
    if engine == "chatterbox" and not say:
        fail(3, "chatterbox-say is not on PATH; run linux/chatterbox/install.sh in agent-config")
    voice = opts["--voice"] or VOICES[engine]
    if voice is None:
        voice = subprocess.run([say, "--default-voice"], capture_output=True, text=True, check=True).stdout.strip()
    n = json.loads(Path(args[0]).read_text())
    out = Path(args[1])
    try:
        import numpy as np
        import soundfile
        from faster_whisper import WhisperModel
        from kokoro_onnx import Kokoro
    except ImportError as exc:
        fail(3, f"{exc}; run with the Sill core's Python")
    cache = out / "cache"
    cache.mkdir(exist_ok=True)
    todo = []
    for s in n["scenes"]:
        text = re.sub(r"\s+", " ", re.sub(r"\[[a-z ]+\]", " ", s["text"])).strip()
        s["base"] = base = cache / (f"{engine}-" + hashlib.sha256(f"{voice}\n{text}".encode()).hexdigest()[:16])
        if not Path(f"{base}.json").exists():
            todo.append({"text": text, "out": f"{base}.wav"})
    if todo and engine == "chatterbox":
        batch = cache / "chatterbox-batch.json"
        batch.write_text(json.dumps(todo))
        if subprocess.run([say, "--voice", voice, "--batch", str(batch)]).returncode:
            fail(3, "chatterbox-say failed")
    elif todo:
        if not (MODELS / "kokoro-v1.0.int8.onnx").exists():
            fail(3, f"no Kokoro model in {MODELS}")
        tts = Kokoro(str(MODELS / "kokoro-v1.0.int8.onnx"), str(MODELS / "voices-v1.0.bin"))
        if voice not in tts.get_voices():
            fail(1, f"unknown voice {voice}")
        for job in todo:
            audio, rate = tts.create(job["text"], voice=voice, speed=1.0, lang="en-us")
            soundfile.write(job["out"], audio, rate)
    if todo:
        whisper = WhisperModel("small.en", device="cpu", compute_type="int8", download_root=str(MODELS / "whisper"))
        for job in todo:
            segs, _ = whisper.transcribe(job["out"], word_timestamps=True, language="en")
            heard = [{"w": w.word.strip(), "s": w.start, "e": w.end} for g in segs for w in g.words]
            Path(job["out"]).with_suffix(".json").write_text(json.dumps(align(job["text"].split(), heard)))
    clips, scenes, words, t = [], [], [], 0.0
    for i, s in enumerate(n["scenes"]):
        base = s.pop("base")
        audio, rate = soundfile.read(f"{base}.wav", dtype="float32")
        if i:
            clips.append(np.zeros(int(JOIN * rate), dtype="float32"))
            t += JOIN / 2
            scenes[-1]["end"] = round(t, 3)
            t += JOIN / 2
        scenes.append({"id": s["id"], "title": s["title"], "text": s["text"], "start": round(t, 3)})
        words += [{**w, "s": round(w["s"] + t, 3), "e": round(w["e"] + t, 3)} for w in json.loads(Path(f"{base}.json").read_text())]
        clips.append(audio)
        t += len(audio) / rate
    scenes[-1]["end"] = round(t, 3)
    wav = out / "narration.local.wav"
    soundfile.write(str(wav), np.concatenate(clips), rate)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(wav), "-ac", "1", "-c:a", "libmp3lame", "-q:a", "4", str(out / "narration.mp3")], check=True)
    wav.unlink()
    timings = {"audio": "narration.mp3", "duration": round(t, 3), "model": f"{engine}:{voice}", "approx": False,
               "requestId": None, "scenes": scenes, "words": words}
    (out / "timings.json").write_text(json.dumps(timings).replace("<", "\\u003c"))
    print(f"local_tts: {len(scenes)} scenes, {t:.1f} s, {engine} voice {voice}")


if __name__ == "__main__":
    main()
