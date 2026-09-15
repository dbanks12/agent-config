#!/usr/bin/env python3
"""Exercise the installed Codex sandbox without API calls or credentials."""

import errno
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest


def probe(mode, outside, port):
    workspace_file = Path("fixture.txt")
    assert workspace_file.read_text() == "fixture"
    assert Path(outside).read_text() == "outside"
    for path, allowed in [(workspace_file, mode == "workspace-write"), (Path(outside), False)]:
        try:
            path.write_text("changed")
        except OSError as error:
            assert not allowed, f"Sandbox blocked an allowed write: {path}: {error}"
            assert error.errno in (errno.EACCES, errno.EPERM, errno.EROFS), error
        else:
            assert allowed, f"Sandbox allowed a forbidden write: {path}"
    try:
        connection = socket.create_connection(("127.0.0.1", int(port)), timeout=2)
    except OSError:
        pass
    else:
        connection.close()
        raise AssertionError("Sandbox reached the host network")
    print(f"PASS: {mode}: reads, write boundaries, network isolation")


class SandboxTest(unittest.TestCase):
    def test_permissions(self):
        self.assertNotEqual(os.geteuid(), 0, "Run this test as the normal Codex user")
        # Keep the protected file outside /tmp and the writable workspace.
        with tempfile.TemporaryDirectory(prefix=".codex-sandbox-test-", dir=Path.home()) as temp:
            root = Path(temp)
            workspace = root / "workspace"
            workspace.mkdir()
            outside = root / "outside.txt"
            with socket.socket() as listener:
                listener.bind(("127.0.0.1", 0))
                listener.listen()
                port = str(listener.getsockname()[1])
                for mode in ("read-only", "workspace-write"):
                    with self.subTest(mode=mode):
                        (workspace / "fixture.txt").write_text("fixture")
                        outside.write_text("outside")
                        result = subprocess.run(
                            ["codex", "sandbox", "-c", f'sandbox_mode="{mode}"',
                             "-c", "sandbox_workspace_write.network_access=false", "--",
                             sys.executable, str(Path(__file__).resolve()),
                             "--probe", mode, str(outside), port],
                            cwd=workspace, capture_output=True, text=True, timeout=30,
                        )
                        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                        self.assertEqual(outside.read_text(), "outside")
                        print(result.stdout.strip())


if __name__ == "__main__":
    if sys.argv[1:2] == ["--probe"]:
        probe(*sys.argv[2:])
    else:
        unittest.main()
