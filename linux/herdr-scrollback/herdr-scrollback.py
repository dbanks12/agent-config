#!/usr/bin/env python3
"""Open a passive Herdr snapshot in an isolated external viewer."""

import argparse
import datetime
import fcntl
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import struct
import sys
import tempfile
import termios
import time

SELF = Path(__file__).resolve()
# Strip CSI, OSC, DCS, SOS, PM, APC, and ordinary two-byte ESC sequences.
ANSI = re.compile(
    r"(?:\x1b\[|\x9b)[0-?]*[ -/]*[@-~]"
    r"|(?:\x1b\]|\x9d)[^\x07\x1b\x9c]*(?:\x07|\x1b\\|\x9c|$)"
    r"|(?:\x1b[P^_X]|[\x90\x98\x9e\x9f]).*?(?:\x1b\\|\x9c|$)"
    r"|\x1b[ -/]*[@-~]", re.DOTALL
)


def plain_text(text):
    text = ANSI.sub("", text)
    return "".join(c for c in text if c in "\n\t" or ord(c) >= 32 and not 127 <= ord(c) <= 159)


def require(name):
    path = shutil.which(name)
    if not path:
        raise RuntimeError(f"Install {name} before opening this viewer.")
    return path


def source_columns(pane, env):
    result = subprocess.run(
        [env.get("HERDR_BIN_PATH") or require("herdr"), "pane", "process-info", "--pane", pane],
        env=env, capture_output=True, text=True, timeout=15, check=True,
    )
    info = json.loads(result.stdout)["result"]["process_info"]
    pid = info.get("shell_pid")
    if not isinstance(pid, int) or pid <= 0:
        raise RuntimeError("Herdr did not report the source terminal process.")
    # Read the PTY dimensions only. Do not read input, write output, or resize it.
    fd = os.open(f"/proc/{pid}/fd/0", os.O_RDONLY | os.O_NOCTTY | os.O_NONBLOCK)
    try:
        _, columns = termios.tcgetwinsize(fd)
    finally:
        os.close(fd)
    if columns <= 0:
        raise RuntimeError("The source terminal did not report a column count.")
    return columns


def capture(pane, env):
    # ANSI is essential: Herdr 0.9.0 can inject scroll events for text reads.
    result = subprocess.run(
        [env.get("HERDR_BIN_PATH") or require("herdr"), "pane", "read", pane,
         "--source", "recent", "--format", "ansi", "--lines", "1000"],
        env=env, capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=15, check=True,
    )
    text = plain_text(result.stdout)
    if not text.strip():
        raise RuntimeError("Herdr returned no retained text for this pane.")
    return text


def private_write(path, text):
    with open(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "w", encoding="utf-8") as file:
        file.write(text)


def clipboard_command():
    # Paths on this machine are fixed. Reject shell metacharacters in PATH results.
    paths = [require("setsid"), require("xclip")]
    if any(not re.fullmatch(r"[/\w.-]+", p) for p in paths):
        raise RuntimeError("Clipboard program paths contain unsupported characters.")
    return f"{paths[0]} -f {paths[1]} -selection clipboard -in >/dev/null 2>&1"


def clean_environment():
    return {k: v for k, v in os.environ.items() if not k.startswith("HERDR_") and k not in ("TMUX", "TMUX_PANE")}


def stop_tmux(directory):
    sock = directory / "tmux.sock"
    if sock.exists():
        subprocess.run([require("tmux"), "-S", str(sock), "kill-server"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)


def tmux_view(snapshot):
    directory = snapshot.parent
    columns, rows = shutil.get_terminal_size((120, 40))
    # Bound wrapped rows conservatively, including wide characters and tab expansion.
    history = max(50000, len(snapshot.read_bytes()) * 8 // max(1, columns - 1) + 2000)
    config = directory / "tmux.conf"
    copy = clipboard_command()
    private_write(config, f'''source-file -q ~/.tmux.conf
set -g history-limit {history}
set -g mouse on
set -g mode-keys vi
set -g set-titles off
set -g destroy-unattached on
set -g status-left "Scrollback "
set -g status-right "wheel: scroll | v: select | y: copy | q: exit"
bind-key -n q kill-session
bind-key -T copy-mode-vi v send-keys -X begin-selection
bind-key -T copy-mode-vi y send-keys -X copy-pipe "{copy}"
bind-key -T copy-mode-vi Enter send-keys -X copy-pipe-and-cancel "{copy}"
bind-key -T copy-mode-vi MouseDragEnd1Pane send-keys -X copy-pipe-and-cancel "{copy}"
''')
    try:
        return subprocess.run(
            [require("tmux"), "-S", str(directory / "tmux.sock"), "-f", str(config),
             "new-session", "-s", "scrollback", "-x", str(columns), "-y", str(rows),
             sys.executable, str(SELF), "--emit", str(snapshot)], env=clean_environment(), check=True).returncode
    finally:
        stop_tmux(directory)


def nvim_binary():
    binary = shutil.which("nvim")
    if binary:
        return binary
    appimage = Path.home() / "apps/nvim-linux-x86_64.appimage"
    if appimage.is_file() and os.access(appimage, os.X_OK):
        return str(appimage)
    raise RuntimeError("Install Neovim before opening this viewer.")


def nvim_view(snapshot):
    config = snapshot.parent / "viewer.vim"
    copy = clipboard_command()
    xclip = require("xclip")
    provider = {
        "name": "Herdr snapshot clipboard",
        "copy": {"+": ["sh", "-c", copy],
                 "*": ["sh", "-c", copy.replace("-selection clipboard", "-selection primary")]},
        "paste": {"+": [xclip, "-selection", "clipboard", "-out"],
                  "*": [xclip, "-selection", "primary", "-out"]},
        "cache_enabled": 0,
    }
    private_write(config, "set nomodeline noswapfile notitle mouse= nowrap\n"
                  + "let g:clipboard = " + json.dumps(provider) + "\n"
                  + "set clipboard=unnamedplus\n")
    return subprocess.run([nvim_binary(), "--noplugin", "-u", str(config), "-i", "NONE",
                           "-n", "-R", "+$", "--", str(snapshot)],
                          env=clean_environment(), check=True).returncode


def emit_snapshot(snapshot):
    # A unique footer proves tmux consumed the final PTY output before copy mode freezes it.
    footer = f"End of snapshot [{snapshot.parent.name}]"
    sys.stdout.write(snapshot.read_text(encoding="utf-8") + "\n\n" + footer + "\n")
    sys.stdout.flush()
    command = [require("tmux"), "-S", str(snapshot.parent / "tmux.sock")]
    target = os.environ["TMUX_PANE"]
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        output = subprocess.run(command + ["capture-pane", "-p", "-J", "-t", target],
                                capture_output=True, text=True, timeout=2, check=True).stdout
        if output.rstrip().endswith(footer):
            subprocess.run(command + ["copy-mode", "-t", target], timeout=2, check=True)
            while True:
                signal.pause()
        time.sleep(0.02)
    raise RuntimeError("Tmux did not finish displaying the snapshot.")


def viewer_geometry(tree, window_id, workspace=None):
    if tree.get("type") == "workspace":
        workspace = tree["rect"]
    if tree.get("window") == window_id:
        props = tree.get("window_properties", {})
        if props.get("class") != "floating_window" or not props.get("title", "").startswith("Herdr Scrollback"):
            raise RuntimeError("Refusing to resize a window that is not a scrollback viewer.")
        return tree, workspace
    for child in tree.get("nodes", []) + tree.get("floating_nodes", []):
        found = viewer_geometry(child, window_id, workspace)
        if found:
            return found
    return None


def fit_viewer(columns):
    window_id = int(os.environ["ALACRITTY_WINDOW_ID"])
    if window_id <= 0:
        raise RuntimeError("The viewer did not report its own window ID.")
    ipc = [require("alacritty"), "msg", "--socket", os.environ["ALACRITTY_SOCKET"]]
    config = json.loads(subprocess.check_output(ipc + ["get-config", "-w", str(window_id)], text=True, timeout=3))
    font_size = float(config["font"]["size"])
    for _ in range(30):
        tree = json.loads(subprocess.check_output([require("i3-msg"), "-t", "get_tree"], text=True, timeout=3))
        found = viewer_geometry(tree, window_id)
        if not found:
            time.sleep(0.1)
            continue
        node, workspace = found
        _, current_columns, pixels, _ = struct.unpack("HHHH", fcntl.ioctl(0, termios.TIOCGWINSZ, bytes(8)))
        if not current_columns or not pixels or not workspace:
            raise RuntimeError("Cannot measure the viewer's terminal cells.")
        cell_width = pixels // current_columns
        border_width = node["rect"]["width"] - node["window_rect"]["width"]
        max_width = int(workspace["width"] * 0.95)
        height = int(workspace["height"] * 0.95)
        width = columns * cell_width + border_width
        if width > max_width:
            smaller = round(min(font_size - 0.25, font_size * (max_width - border_width) / (columns * cell_width) * 0.98), 2)
            if smaller < 0.5:
                raise RuntimeError("The source has too many columns to fit on this screen.")
            # Always address this specific window. Never use the global window ID (-1).
            subprocess.run(ipc + ["config", "-w", str(window_id), f"font.size={smaller}"], check=True, timeout=3)
            font_size = smaller
        else:
            rect = node["rect"]
            inside = (workspace["x"] <= rect["x"] and workspace["y"] <= rect["y"]
                      and rect["x"] + rect["width"] <= workspace["x"] + workspace["width"]
                      and rect["y"] + rect["height"] <= workspace["y"] + workspace["height"])
            if current_columns == columns and rect["width"] == width and rect["height"] == height and inside:
                return
            command = f'[id={window_id}] resize set width {width} px height {height} px, move position center'
            results = json.loads(subprocess.check_output([require("i3-msg"), command], text=True, timeout=3))
            if not all(result.get("success") for result in results):
                raise RuntimeError("The window manager could not fit the viewer.")
        time.sleep(0.1)
    raise RuntimeError("The viewer could not settle at the source column count.")


def launch(mode, pane):
    if not os.environ.get("DISPLAY"):
        raise RuntimeError("This viewer needs an X11 desktop session.")
    terminal = require("alacritty")
    clipboard_command()
    require("tmux") if mode == "tmux" else nvim_binary()
    columns = source_columns(pane, os.environ.copy())
    text = capture(pane, os.environ.copy())
    with tempfile.TemporaryDirectory(prefix="herdr-scrollback-") as temp:
        directory = Path(temp)
        snapshot = directory / "scrollback.txt"
        stamp = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
        header = f"Herdr {pane} | latest 1000 retained rendered rows at most | {stamp}\n"
        private_write(snapshot, header + text)
        try:
            # Regolith already floats this class before the window can resize Herdr.
            return subprocess.run(
                [terminal, "--socket", str(directory / "alacritty.sock"), "--class", "floating_window", "--title", f"Herdr Scrollback ({mode})",
                 "-o", "window.dynamic_title=false", "-o", "window.padding.x=0",
                 "-o", "window.dynamic_padding=false", "-o", f"window.dimensions.columns={columns}",
                 "-o", "window.dimensions.lines=40", "-e", sys.executable, str(SELF),
                 "--columns", str(columns), "--view", mode, str(snapshot)], env=clean_environment(), check=True).returncode
        finally:
            if mode == "tmux":
                stop_tmux(directory)


def interrupted(signum, frame):
    raise KeyboardInterrupt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", nargs="?", choices=["tmux", "nvim", "vim"])
    parser.add_argument("--pane", help="Explicit source pane. Otherwise use the keybind's active pane.")
    parser.add_argument("--view", nargs=2, metavar=("MODE", "FILE"), help=argparse.SUPPRESS)
    parser.add_argument("--columns", type=int, help=argparse.SUPPRESS)
    parser.add_argument("--emit", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    for sig in (signal.SIGHUP, signal.SIGTERM):
        signal.signal(sig, interrupted)
    try:
        if args.emit:
            return emit_snapshot(args.emit)
        if args.view:
            mode, path = args.view
            if mode not in ("tmux", "nvim", "vim"):
                raise RuntimeError("Unknown viewer.")
            if args.columns is not None:
                fit_viewer(args.columns)
            return (tmux_view if mode == "tmux" else nvim_view)(Path(path))
        pane = args.pane or os.environ.get("HERDR_ACTIVE_PANE_ID")
        if not args.mode or not pane or not os.environ.get("HERDR_SOCKET_PATH"):
            raise RuntimeError("Use a Herdr keybind, or specify --pane and HERDR_SOCKET_PATH.")
        return launch(args.mode, pane)
    except KeyboardInterrupt:
        return 130
    except (OSError, RuntimeError, ValueError, KeyError, subprocess.SubprocessError) as error:
        message = str(error)
        print(f"Herdr scrollback: {message}", file=sys.stderr)
        notifier = shutil.which("notify-send")
        if notifier:
            try:
                subprocess.run([notifier, "Herdr scrollback failed", message], timeout=5, check=False)
            except (OSError, subprocess.SubprocessError):
                pass
        return 1


if __name__ == "__main__":
    sys.exit(main())
