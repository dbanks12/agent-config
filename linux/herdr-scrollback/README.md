# Herdr scrollback viewers

These personal Linux helpers export a snapshot into a new floating Alacritty window.
They support the installed Herdr 0.9.0, tmux 3.4, and Neovim 0.11.5.
They use the existing Regolith `floating_window` rule.
Each viewer uses the source pane’s actual PTY column count at capture time.
The helper centers the window within the current workspace and uses 95% of its available height.
If the source columns are too wide, the helper reduces this viewer’s font until they fit within 95% of the workspace width.
The column count remains unchanged. The helper measures the current screen and actual terminal cells at each launch.
Each viewer has its own Alacritty socket. Font updates target only that viewer’s window ID.
Other Alacritty windows and user configuration files remain unchanged.

The export contains at most 1,000 retained rendered rows. Source row breaks remain intact.
Copies preserve those row breaks instead of joining wrapped rows.
The helper reads the source PTY size through a read-only file descriptor. It never resizes the source.
The helper requests recent ANSI output and removes formatting locally.
This matters: Herdr 0.9.0 can inject mouse-wheel events for text reads from idle alternate-screen agents.
ANSI reads skip that path in `src/server/headless.rs::alt_screen_read_spec`.
The helper does not send input, scroll, resize, or create panes in Herdr.
It cannot recover discarded history or alternate-screen content that Herdr does not retain.

## Keys

The local Herdr prefix is Ctrl+A.

- Press Ctrl+A, then Ctrl+T, for tmux.
- Press Ctrl+A, then Ctrl+V, for Neovim.

Press the other keybind to switch viewers. Each export captures a new snapshot.
The existing viewer remains open until you close it.

Tmux opens directly in copy mode after the complete snapshot arrives.
It loads your `~/.tmux.conf` into its private server, including your regular prefixes and navigation bindings.
Your current prefixes are Ctrl+B and Ctrl+A.
Press Space or `v` to start selection. Move the cursor, then press `y` to copy without leaving copy mode.
Enter copies and leaves copy mode. Your mouse navigation follows your regular tmux configuration.
Press `q` to leave copy mode. Press `q` again to close the viewer.
Each export uses a private tmux server. Existing tmux sessions remain unchanged.

Neovim uses the system `+` clipboard by default in this viewer only.
Use normal `y`, `yy`, or visual selection followed by `y`. Explicit `"+y` also works.
Use `"+p` to paste from the desktop clipboard. The snapshot buffer permits temporary edits.
Enter `:q!` to close Neovim.
Neovim starts read-only, without user configuration, plugins, modelines, swap files, or persistent history.
A temporary configuration sets `clipboard=unnamedplus` and uses xclip for the clipboard provider.
No user Neovim configuration file changes are needed.
See [Neovim's clipboard documentation](https://neovim.io/doc/user/provider/#clipboard-integration).

Both modes copy through `setsid -f xclip`. The clipboard owner can survive the viewer's exit.
Snapshots have private file permissions. Normal window closure removes the temporary directory.
A forced process kill or power failure can leave temporary files under `/tmp/herdr-scrollback-*`.
Failures produce a desktop notification through `notify-send`.

## Setup

Required programs: Python 3, Herdr 0.9.0, Alacritty, tmux, Neovim, xclip, setsid, and notify-send.
The helper uses `nvim` from PATH, or your `~/apps/nvim-linux-x86_64.appimage` installation.
The Herdr server must inherit DISPLAY and the desktop's X11 authorization.

Run `./install.sh` from the agent-config repository to install the helper link.
Add the entries from `keybindings.toml` to `~/.config/herdr/config.toml`.
Run `herdr config check`.
Run `herdr server reload-config`.

For a manual export inside Herdr, run:

```sh
herdr-scrollback tmux --pane "$HERDR_PANE_ID"
herdr-scrollback nvim --pane "$HERDR_PANE_ID"
```

Run the helper tests with:

```sh
python3 linux/herdr-scrollback/test_scrollback.py
```

To remove the integration, remove both custom keybind entries and reload Herdr's configuration.
Remove `~/.local/bin/herdr-scrollback` if you no longer need manual exports.
Opening Neovim inside Herdr is a possible later change. This version creates only external windows.
