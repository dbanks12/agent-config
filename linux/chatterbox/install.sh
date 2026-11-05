#!/usr/bin/env bash
# Installs Chatterbox Turbo for this user: a Python 3.11 environment with CUDA 12.4 PyTorch in
# ${CHATTERBOX_HOME:-~/.local/share/chatterbox}, and the model weights (about 4 GB) in the Hugging Face cache.
# Run it again to repair the environment. The repo's install.sh links chatterbox-say into ~/.local/bin.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
home="${CHATTERBOX_HOME:-$HOME/.local/share/chatterbox}"
command -v uv >/dev/null || { echo "install.sh: needs uv (https://docs.astral.sh/uv/)" >&2; exit 1; }
[[ -x $home/venv/bin/python ]] || uv venv -q --python 3.11 "$home/venv"
# setuptools<81 keeps pkg_resources, which the resemble-perth watermarker imports.
uv pip install -q --python "$home/venv/bin/python" --torch-backend cu124 chatterbox-tts==0.1.7 'setuptools<81'
"$home/venv/bin/python" -I -c '
import torch
from chatterbox.tts_turbo import ChatterboxTurboTTS
ChatterboxTurboTTS.from_pretrained(device="cpu")
print("install.sh: ready,", "GPU " + torch.cuda.get_device_name(0) if torch.cuda.is_available() else "no GPU, CPU only")'
