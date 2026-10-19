# Cleanup for /tmp and orphan processes

## Problem

On 2026-10-19, this host had 30 GiB of RAM and a full 8 GiB swap.
`/tmp` is a tmpfs, so its files live in RAM. It held 9.6 GiB:

- 4.1 GiB of agent scratch in `/tmp/claude-1000`
- 2.5 GiB in `/tmp/.pnpm-store`
- 0.8 GiB in `/tmp/pytest-of-david`

Leaked processes held more RAM. Their parents had exited, so PID 1 adopted them:

- a Gradle daemon with a Kotlin compile daemon (4.4 GiB RSS)
- a QA sandbox stack of 44 node, bash, and `bb` processes (0.9 GiB RSS)
- `cargo-mutants` runs that agents started in herdr panes

This directory holds four mitigations. None of them is installed.

| File | Purpose |
| --- | --- |
| `tmp-janitor.py` | Removes stale agent scratch, the pnpm store, and old pytest dirs |
| `orphan-reaper.py` | Stops leaked build and QA process trees |
| `systemd/` | User timers for both scripts. The services run in dry-run mode. |
| `proposed-etc/` | A proposed 4G cap for the `/tmp` tmpfs |

The agent guidance is in `instructions/AGENTS.md` under "Long jobs and cleanup".

## tmp-janitor.py

```sh
linux/cleanup/tmp-janitor.py              # dry run, 24-hour threshold
linux/cleanup/tmp-janitor.py -v           # also list what it keeps, and why
linux/cleanup/tmp-janitor.py --max-age 72 --apply
```

The janitor deletes one unit at a time:

- one session dir, `/tmp/claude-$UID/<project>/<session-id>`
- any other top-level entry in `/tmp/claude-$UID`
- the whole `/tmp/.pnpm-store`
- one `pytest-N` dir in `/tmp/pytest-of-$USER`

It keeps a unit in these cases:

- A file in the unit changed within `--max-age` hours.
- A live process of yours has its cwd or an open file in the unit.
- The unit is the session dir of a live Claude session. The janitor reads `~/.claude/sessions/<pid>.json` and checks the PID start time.
- A live process has its cwd at the worktree of the project dir. Claude Code names the project dir after the cwd and changes each non-alphanumeric character to `-`.
- The unit is the pnpm store and a `pnpm` process is running.
- You do not own the unit.

The janitor removes the pnpm store as one unit. A partial delete can leave index entries that point at missing files. Hard links keep existing `node_modules` dirs working. The next `pnpm install` downloads the packages again.

The janitor does not follow symlinks. After `--apply`, it also removes project dirs that are empty.

The 2026-10-19 dry run listed 6 GiB to remove. It kept 55 live sessions and 75 session dirs of active worktrees.

## orphan-reaper.py

```sh
linux/cleanup/orphan-reaper.py            # dry run, 2-hour threshold
linux/cleanup/orphan-reaper.py -v         # also list skipped trees and every PID
linux/cleanup/orphan-reaper.py --apply
```

An orphan root is a process of yours whose parent is PID 1 or your `systemd --user`.
The reaper selects the whole tree under such a root when all of these conditions are true:

- The tree contains a target. The targets are `cargo-mutants`, `cargo`, `rustc`, the Gradle daemon, the Kotlin compile daemon, and `node` with `/qa/` in its arguments or cwd.
- The root is a target or a wrapper: `bash`, `sh`, `dash`, `zsh`, `timeout`, `nohup`, `env`, or `setsid`. This rule excludes long-lived services such as `herdr server`.
- The tree contains no `claude`, `codex`, `herdr`, `tmux`, `screen`, `sshd`, or `systemd` process.
- The root ran for at least `--min-age` hours.
- The Claude process named by `CLAUDE_PID` in the environment of the tree is dead. Claude Code Bash shells re-parent to PID 1 while their agent still waits on them. This rule protects such jobs. Gradle and Kotlin daemon trees skip this rule because the daemons outlive builds by design.
- For a Gradle or Kotlin daemon tree, no Gradle client runs.

With `--apply`, the reaper sends SIGTERM to each PID in the tree. It waits `--grace` seconds and then sends SIGKILL to the survivors. Before each signal, it compares the PID start time with the recorded value. A reused PID gets no signal.

The 2026-10-19 dry run selected the Gradle and Kotlin daemons and four QA stack trees, 5.2 GiB RSS in total.
It skipped four `cargo-mutants` trees because their agent, Claude PID 625199, was alive.

The reaper does not target `mcp-excalidraw-server` or `codex-linux-sandbox`. Add a line to `TARGETS` to change that.

## Timers

The units run the scripts from `~/projects/agent-config`. The services run in dry-run mode and log to the journal.

1. Link the units:

   ```sh
   systemctl --user link ~/projects/agent-config/linux/cleanup/systemd/agent-{tmp-janitor,orphan-reaper}.{service,timer}
   ```

2. Start the timers:

   ```sh
   systemctl --user enable --now agent-tmp-janitor.timer agent-orphan-reaper.timer
   ```

3. Read the reports for a few days:

   ```sh
   journalctl --user -u agent-tmp-janitor -u agent-orphan-reaper --since today
   ```

4. To make a service delete or kill, add an override and append `--apply` to its command:

   ```sh
   systemctl --user edit agent-tmp-janitor.service
   ```

   ```ini
   [Service]
   ExecStart=
   ExecStart=%h/projects/agent-config/linux/cleanup/tmp-janitor.py --max-age 24 --apply
   ```

To remove the timers, run `systemctl --user disable --now` on both timers. Then delete the links in `~/.config/systemd/user/`.

## Size cap for /tmp

`tmp.mount` from systemd mounts `/tmp` as a tmpfs with `size=50%`, which is 15 GiB here.
The kernel moves tmpfs pages to swap under memory pressure, so a large `/tmp` fills swap.

The proposed drop-in `proposed-etc/systemd/system/tmp.mount.d/size.conf` sets `size=4G`.
When `/tmp` is full, writes fail with `ENOSPC` and the RAM stays free for processes.

1. Run the janitor with `--apply` until `/tmp` holds less than 4 GiB. A remount to a smaller size fails while usage exceeds the new size.

2. Install the drop-in:

   ```sh
   sudo install -D -m 644 linux/cleanup/proposed-etc/systemd/system/tmp.mount.d/size.conf /etc/systemd/system/tmp.mount.d/size.conf
   ```

3. Reload systemd:

   ```sh
   sudo systemctl daemon-reload
   ```

4. Apply the size now without a reboot:

   ```sh
   sudo mount -o remount,size=4G /tmp
   ```

5. Check the result:

   ```sh
   findmnt /tmp
   ```

To revert, delete the drop-in, run `sudo systemctl daemon-reload`, and run `sudo mount -o remount,size=50% /tmp`.

### Alternative: /tmp on disk

The root filesystem has 706 GiB free. To put `/tmp` on disk, run `sudo systemctl mask tmp.mount` and reboot.
After the reboot, `/tmp` is a directory on ext4. RAM use from `/tmp` drops to the page cache, which the kernel can drop.
This option uses no size limit, so leaked files grow without a signal. It also needs a reboot. The shipped rule in `/usr/lib/tmpfiles.d/tmp.conf` removes files older than 10 days.
The cap is the recommended option because a reboot is not necessary and the revert is simple.
