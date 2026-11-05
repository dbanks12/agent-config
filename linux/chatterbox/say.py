"""Speak text with Chatterbox Turbo on this machine's GPU (CPU when there is none). Free, and sends nothing.

Usage: chatterbox-say [-v VOICE] [-o OUT.wav] [TEXT]     TEXT defaults to stdin
       chatterbox-say [-v VOICE] --batch JOBS.json        [{"text": "...", "out": "a.wav"}, ...], one model load

VOICE is a name in voices/ (default "male"), "builtin" for the model's own female voice, or the path to a
clean 10-20 s clip of any voice to clone. Writes 24 kHz mono WAV. Long text is read a few sentences at a time,
because Turbo stops after about 40 s of speech per request.
"""
import argparse
import contextlib
import json
import re
import sys
import warnings
from pathlib import Path

VOICES = Path(__file__).resolve().parent / "voices"
CHUNK = 300  # characters per request


def chunks(text):
    out = []
    for s in re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", text).strip()):
        if out and len(out[-1]) + len(s) < CHUNK:
            out[-1] += " " + s
        else:
            out.append(s)
    return [c for c in out if c]


def voice_path(v):
    if v == "builtin":
        return None
    for p in (Path(v), VOICES / f"{v}.flac", VOICES / f"{v}.wav"):
        if p.is_file():
            return p
    sys.exit(f"chatterbox-say: no voice {v}; names: builtin, " + ", ".join(sorted(p.stem for p in VOICES.iterdir())))


def main():
    ap = argparse.ArgumentParser(prog="chatterbox-say", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("text", nargs="?")
    ap.add_argument("-v", "--voice", default="male")
    ap.add_argument("-o", "--out", default="speech.wav")
    ap.add_argument("--batch", type=Path)
    a = ap.parse_args()
    jobs = json.loads(a.batch.read_text()) if a.batch else [{"text": a.text if a.text is not None else sys.stdin.read(), "out": a.out}]
    ref = voice_path(a.voice)

    warnings.filterwarnings("ignore")
    # The library prints progress to stdout. Keep stdout clean for callers.
    with contextlib.redirect_stdout(sys.stderr):
        speak(jobs, ref)


def speak(jobs, ref):
    import numpy as np
    import soundfile
    import torch
    from chatterbox.tts_turbo import ChatterboxTurboTTS

    model = ChatterboxTurboTTS.from_pretrained(device="cuda" if torch.cuda.is_available() else "cpu")
    if ref:
        model.prepare_conditionals(str(ref))
    for job in jobs:
        parts = [model.generate(c).squeeze(0).numpy() for c in chunks(job["text"])]
        audio = np.concatenate(parts) if parts else np.zeros(0, dtype="float32")
        soundfile.write(job["out"], audio, model.sr)
        print(f"chatterbox-say: {job['out']} {len(audio) / model.sr:.1f} s", file=sys.stderr)


if __name__ == "__main__":
    main()
