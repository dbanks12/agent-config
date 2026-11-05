# Chatterbox text-to-speech

`chatterbox-say` reads text aloud with [Chatterbox Turbo](https://github.com/resemble-ai/chatterbox), Resemble AI's MIT-licensed 350M-parameter model. It runs on this machine's NVIDIA GPU, or on the CPU when there is none. It is free and sends nothing.

## Install

Run `linux/chatterbox/install.sh`. It needs `uv`.

- The script makes a Python 3.11 environment in `~/.local/share/chatterbox` with CUDA 12.4 PyTorch. `CHATTERBOX_HOME` moves it.
- It downloads the weights, about 4 GB, into the Hugging Face cache.
- The repo's `install.sh` links `chatterbox-say` into `~/.local/bin`.

## Use

```sh
chatterbox-say -o hello.wav "Hello there."
echo "Text from a pipe." | chatterbox-say -v builtin -o out.wav
chatterbox-say --batch jobs.json   # [{"text": "...", "out": "a.wav"}, ...]
```

- The output is 24 kHz mono WAV.
- A batch loads the model once. The load takes about 15 seconds. After it, speech comes at about three times real time on an RTX 2080 Super, using 3 GB of video memory.
- `-v` takes a name from `voices/`, `builtin` for the model's own female voice, or the path to a clean 10–20 second clip to clone.
- The default voice is `male`, cloned from Kokoro's Apache-licensed `am_michael` voice.
- Turbo stops after about 40 seconds of speech per request, so `say.py` reads long text a few sentences at a time.
- Turbo reads paralinguistic tags such as `[laugh]` and `[chuckle]` in the text.
- Every clip carries Resemble's inaudible Perth watermark.
- Library progress goes to stderr, and stdout stays empty.

The explainer skill uses it as its first fallback when ElevenLabs fails (`skills/explainer/scripts/local_tts.py`).
