#!/usr/bin/env python3
"""Behavior checks. Clipboard tests use a fake xclip and never change the desktop clipboard."""
import base64
import importlib.util
import json
import os
from pathlib import Path
import pty
import select
import signal
import struct
import subprocess
import tempfile
import termios
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("scrollback", ROOT / "herdr-scrollback.py")
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)


class CaptureTests(unittest.TestCase):
    def test_ansi_read_does_not_request_interactive_text_probe(self):
        env = {"HERDR_BIN_PATH": "/test/herdr", "HERDR_SOCKET_PATH": "/test/socket"}
        with patch.object(app.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "\x1b[31mhello\x1b[0m\n")) as run:
            self.assertEqual(app.capture("w1:p2", env), "hello\n")
        args = run.call_args.args[0]
        self.assertEqual(args, ["/test/herdr", "pane", "read", "w1:p2", "--source", "recent", "--format", "ansi", "--lines", "1000"])
        self.assertEqual(run.call_args.kwargs["env"], env)
        self.assertEqual(run.call_args.kwargs["timeout"], 15)

    def test_source_columns_reads_actual_pty_without_resizing(self):
        master, slave = pty.openpty()
        try:
            termios.tcsetwinsize(slave, (37, 137))
            original_open = os.open
            def open_source(path, flags):
                self.assertEqual(path, "/proc/1234/fd/0")
                self.assertEqual(flags, os.O_RDONLY | os.O_NOCTTY | os.O_NONBLOCK)
                return original_open(os.ttyname(slave), flags)
            response = subprocess.CompletedProcess([], 0, '{"result":{"process_info":{"shell_pid":1234}}}')
            with patch.object(app.subprocess, "run", return_value=response), patch.object(app.os, "open", side_effect=open_source):
                self.assertEqual(app.source_columns("w1:p2", {"HERDR_BIN_PATH": "/test/herdr"}), 137)
            self.assertEqual(termios.tcgetwinsize(slave), (37, 137))
        finally:
            os.close(master)
            os.close(slave)

    def test_auto_fit_shrinks_only_the_viewer_on_different_screens(self):
        for screen_width, small_cell in ((1920, 5), (3840, 11)):
            with self.subTest(screen_width=screen_width):
                state = {"width": 4190, "height": 600, "cell": 13, "font_changes": 0, "resizes": 0}
                workspace = {"x": 100, "y": 50, "width": screen_width, "height": 1000}
                def query(argv, **kwargs):
                    if "get-config" in argv:
                        self.assertEqual(argv[-2:], ["-w", "123"])
                        return json.dumps({"font": {"size": 8}})
                    if "get_tree" in argv:
                        node = {"window": 123, "window_properties": {"class": "floating_window", "title": "Herdr Scrollback (tmux)"},
                                "rect": {"x": 120, "y": 70, "width": state["width"], "height": state["height"]},
                                "window_rect": {"width": state["width"] - 4}}
                        return json.dumps({"type": "workspace", "rect": workspace, "floating_nodes": [node]})
                    self.assertTrue(argv[-1].startswith("[id=123] resize set"))
                    state.update(width=322 * small_cell + 4, height=950, resizes=state["resizes"] + 1)
                    return '[{"success":true}]'
                def configure(argv, **kwargs):
                    self.assertEqual(argv[:6], ["/test/alacritty", "msg", "--socket", "/test/viewer.sock", "config", "-w"])
                    self.assertEqual(argv[6], "123")
                    self.assertNotIn("-1", argv)
                    self.assertLess(float(argv[7].split("=")[1]), 8)
                    state.update(cell=small_cell, font_changes=state["font_changes"] + 1)
                def dimensions(*args):
                    columns = (state["width"] - 4) // state["cell"]
                    return struct.pack("HHHH", 40, columns, columns * state["cell"], 800)
                with patch.dict(os.environ, {"ALACRITTY_WINDOW_ID": "123", "ALACRITTY_SOCKET": "/test/viewer.sock"}), patch.object(app, "require", side_effect=lambda name: "/test/" + name), patch.object(app.subprocess, "check_output", side_effect=query), patch.object(app.subprocess, "run", side_effect=configure), patch.object(app.fcntl, "ioctl", side_effect=dimensions), patch.object(app.time, "sleep"):
                    app.fit_viewer(322)
                self.assertEqual(state["font_changes"], 1)
                self.assertEqual(state["resizes"], 1)
                self.assertLessEqual(state["width"], screen_width * .95)

    def test_capture_failure_never_launches_window(self):
        with patch.dict(os.environ, {"DISPLAY": ":0"}), patch.object(app, "require", return_value="/test/tool"), patch.object(app, "clipboard_command", return_value="copy"), patch.object(app, "source_columns", return_value=137), patch.object(app, "capture", side_effect=RuntimeError("capture failed")), patch.object(app.subprocess, "run") as call:
            with self.assertRaisesRegex(RuntimeError, "capture failed"):
                app.launch("tmux", "w1:p2")
            call.assert_not_called()

    def test_control_sequences_never_reach_terminal(self):
        value = "héllo\t世界\n\x1b[31mred\x1b[0m\x1b]52;c;bad\x07\x1bPbad\x1b\\\x9b1mOK\x9dtitle\x9c\x00\x7f\x08\r"
        self.assertEqual(app.plain_text(value), "héllo\t世界\nredOK")
        self.assertEqual(app.plain_text("abc\x1b]52;unfinished"), "abc")

    def test_private_file_and_cleanup_after_terminal_failure(self):
        paths = []
        def fail(argv, **kwargs):
            self.assertIn("window.dimensions.columns=137", argv)
            path = Path(argv[-1]); paths.append(path)
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.assertEqual(path.parent.stat().st_mode & 0o777, 0o700)
            self.assertIn("latest 1000", path.read_text())
            self.assertNotIn("HERDR_SOCKET_PATH", kwargs["env"])
            raise OSError("terminal failed")
        with patch.dict(os.environ, {"DISPLAY": ":0", "HERDR_SOCKET_PATH": "/test/socket"}), patch.object(app, "require", return_value="/test/tool"), patch.object(app, "clipboard_command", return_value="copy"), patch.object(app, "source_columns", return_value=137), patch.object(app, "capture", return_value="hello"), patch.object(app.subprocess, "run", side_effect=fail):
            with self.assertRaises(OSError): app.launch("vim", "w1:p2")
        self.assertFalse(paths[0].parent.exists())

    def test_nonzero_viewer_exits_notify(self):
        for mode in ("alacritty", "tmux", "nvim"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory(prefix="scrollback-error-") as temp:
                root = Path(temp)
                for tool in ("alacritty", "tmux", "nvim"):
                    fake = root / tool
                    fake.write_text("#!/bin/sh\nexit 7\n")
                    fake.chmod(0o700)
                notifier = root / "notify-send"
                notifier.write_text('#!/bin/sh\nprintf notified > "$NOTIFY_TEST_FILE"\n')
                notifier.chmod(0o700)
                snapshot = root / "snapshot.txt"
                snapshot.write_text("test snapshot\n")
                env = {"PATH": f"{root}:{os.environ['PATH']}", "DISPLAY": ":0",
                       "HERDR_ACTIVE_PANE_ID": "w1:p2", "HERDR_SOCKET_PATH": "/unused",
                       "NOTIFY_TEST_FILE": str(root / "notified")}
                argv = ["helper", "nvim"] if mode == "alacritty" else ["helper", "--view", mode, str(snapshot)]
                with patch.dict(os.environ, env), patch.object(app.sys, "argv", argv), patch.object(app, "source_columns", return_value=137), patch.object(app, "capture", return_value="test snapshot"):
                    self.assertEqual(app.main(), 1)
                self.assertEqual((root / "notified").read_text(), "notified")

    def test_missing_active_context_does_not_use_inherited_pane(self):
        with patch.dict(os.environ, {"HERDR_PANE_ID": "wrong:p1", "HERDR_SOCKET_PATH": "/test/socket"}, clear=True), patch.object(app.sys, "argv", ["helper", "tmux"]), patch.object(app, "launch") as launch, patch.object(app.shutil, "which", return_value=None):
            self.assertEqual(app.main(), 1)
            launch.assert_not_called()


class ViewerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="scrollback-test-")
        self.root = Path(self.temp.name)
        self.snapshot = self.root / "scrollback.txt"
        self.master, self.slave = pty.openpty()
        self.process = None
        self.output = b""
        fake = self.root / "xclip"
        fake.write_text('#!/bin/sh\ncase " $* " in *" -out "*) cat "$CLIPBOARD_TEST_FILE";; *) cat > "$CLIPBOARD_TEST_FILE";; esac\n')
        fake.chmod(0o700)
        self.env = app.clean_environment() | {"PATH": f"{self.root}:{os.environ['PATH']}", "CLIPBOARD_TEST_FILE": str(self.root / "clipboard"), "TERM": "xterm-256color"}

    def start(self, mode):
        self.process = subprocess.Popen([app.sys.executable, str(app.SELF), "--view", mode, str(self.snapshot)], stdin=self.slave, stdout=self.slave, stderr=self.slave, env=self.env, start_new_session=True)

    def wait_for(self, check):
        until = time.monotonic() + 10
        while time.monotonic() < until:
            if select.select([self.master], [], [], .03)[0]:
                self.output += os.read(self.master, 65536)
            if check(): return
            if self.process.poll() is not None: self.fail(f"Viewer exited early: {self.process.returncode}")
        self.fail("Viewer did not become ready")

    def tearDown(self):
        app.stop_tmux(self.root)
        if self.process and self.process.poll() is None:
            self.process.send_signal(signal.SIGHUP)
            try: self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(self.process.pid, signal.SIGKILL)
                self.process.wait()
        os.close(self.master); os.close(self.slave)
        self.temp.cleanup()

    def test_tmux_retains_wrapped_unicode_and_copies_to_external_owner(self):
        text = "first\n" + "世界 abc " * 300 + "\n" + "\n".join(f"row {i}" for i in range(1100)) + "\nlast-snapshot-line\n"
        self.snapshot.write_text(text)
        self.start("tmux")
        base = ["tmux", "-S", str(self.root / "tmux.sock")]
        def ready():
            r = subprocess.run(base + ["capture-pane", "-p", "-J", "-S", "-", "-t", "scrollback:0.0"], capture_output=True, text=True)
            if "last-snapshot-line" not in r.stdout:
                return False
            return subprocess.check_output(base + ["display-message", "-p", "-t", "scrollback:0.0", "#{pane_in_mode}"], text=True).strip() == "1"
        self.wait_for(ready)
        captured = subprocess.check_output(base + ["capture-pane", "-p", "-J", "-S", "-", "-t", "scrollback:0.0"], text=True)
        self.assertIn(text.rstrip(), captured)
        self.assertEqual(subprocess.check_output(base + ["show-options", "-gv", "prefix2"], text=True).strip(), "C-a")
        self.assertEqual(subprocess.check_output(base + ["show-options", "-gv", "prefix"], text=True).strip(), "C-b")
        self.assertIn("select-pane -L", subprocess.check_output(base + ["list-keys", "-T", "prefix", "C-h"], text=True))
        for action in ["history-top", "select-line"]:
            command = base + ["send-keys", "-X", "-t", "scrollback:0.0", action]
            subprocess.run(command, check=True)
        os.write(self.master, b"y")
        self.wait_for(lambda: (self.root / "clipboard").exists() and (self.root / "clipboard").stat().st_size > 0)
        self.assertEqual((self.root / "clipboard").read_text(), "first\n")
        self.assertEqual(subprocess.check_output(base + ["display-message", "-p", "-t", "scrollback:0.0", "#{pane_in_mode}"], text=True).strip(), "1")
        subprocess.run(base + ["kill-session", "-t", "scrollback"], check=True)
        self.process.wait(timeout=5)
        self.assertEqual(self.process.returncode, 0)

    def test_neovim_default_and_explicit_clipboard(self):
        self.snapshot.write_text("alpha\nbeta\ngamma\n")
        # A real plugin attempts to disable our copy shortcut. It must never load.
        plugin_dir = self.root / "runtime" / "plugin"
        plugin_dir.mkdir(parents=True)
        (plugin_dir / "override.vim").write_text("vnoremap y <Nop>\n")
        wrapper = self.root / "nvim"
        wrapper.write_text(f'#!/bin/sh\nexec {app.nvim_binary()} --cmd "set runtimepath^={plugin_dir.parent}" "$@"\n')
        wrapper.chmod(0o700)
        self.start("nvim")
        self.wait_for(lambda: (self.root / "viewer.vim").exists())
        # A Vim process queues input until startup completes.
        os.write(self.master, b"ggVjy")
        self.wait_for(lambda: (self.root / "clipboard").exists() and (self.root / "clipboard").stat().st_size > 0)
        self.assertEqual((self.root / "clipboard").read_text(), "alpha\nbeta\n")
        os.write(self.master, b'gg0vll"+y')
        self.wait_for(lambda: (self.root / "clipboard").read_text() == "alp")
        # Read + through the clipboard provider, rather than through a cached yank.
        (self.root / "clipboard").write_text("external clipboard")
        register_file = self.root / "plus-register"
        os.write(self.master, f':call writefile([getreg("+")], "{register_file}")\r'.encode())
        self.wait_for(lambda: register_file.exists())
        self.assertEqual(register_file.read_text(), "external clipboard\n")
        os.write(self.master, b"\x1b:q!\r")
        self.process.wait(timeout=5)
        self.assertEqual(self.process.returncode, 0)

    def test_popup_neovim_copies_through_osc52(self):
        herdr = self.root / "herdr"
        herdr.write_text("#!/bin/sh\nprintf 'alpha\\nbeta\\ngamma\\n'\n")
        herdr.chmod(0o700)
        env = self.env | {"HERDR_BIN_PATH": str(herdr), "HERDR_SOCKET_PATH": "/unused", "HERDR_ACTIVE_PANE_ID": "w1:p2"}
        env.pop("DISPLAY", None)
        self.process = subprocess.Popen([app.sys.executable, str(app.SELF), "nvim", "--popup"], stdin=self.slave, stdout=self.slave, stderr=self.slave, env=env, start_new_session=True)
        # Select the "alpha" and "beta" rows below the snapshot header, then yank them.
        os.write(self.master, b"ggjVjy")
        expected = b"\x1b]52;c;" + base64.b64encode(b"alpha\nbeta\n")
        self.wait_for(lambda: expected in self.output)
        self.assertFalse((self.root / "clipboard").exists())
        os.write(self.master, b"\x1b:q!\r")
        self.process.wait(timeout=5)
        self.assertEqual(self.process.returncode, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
