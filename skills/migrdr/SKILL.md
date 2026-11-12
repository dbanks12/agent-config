---
name: migrdr
description: Move a Herdr workspace with its worktrees, or one tab or pane, to another Herdr session, and resume its agents there. Usage: /migrdr <session> [this pane|this tab|this worktree].
disable-model-invocation: true
---

# Migrate to another Herdr session

Arguments are `<session>` and an optional scope, for example `/migrdr aztec` or `/migrdr az just this tab`. If the session is missing, show the usage and stop.

Herdr cannot move a live process between servers. `migrdr.py`, in this skill's directory, rebuilds the layout in the target session and resumes each agent from the session ID that Herdr recorded. Shells come back empty in the same directory. Any other running process stops.

## 1. Resolve the arguments

Run `test "${HERDR_ENV:-}" = 1`. If it fails, say that this session is not inside Herdr and stop.

The nickname `az` means `aztec`, and `sq` means `side-quests`. Any other name must appear in `herdr session list`.

"This" means the calling pane, `$HERDR_PANE_ID`. Map the scope to a `--scope` value:

| Request | `--scope` | Moves |
| --- | --- | --- |
| nothing, or "this workspace" | `group` | The workspace, and its primary and linked worktree workspaces when it is a Git checkout |
| "this worktree" | `workspace` | Only the calling workspace |
| "this tab" | `tab` | The calling tab |
| "this pane" | `pane` | The calling pane, as a new tab |

If the request names a different pane, tab, or workspace, pass one of its pane IDs with `--pane`.

## 2. Make the plan

```bash
python3 <skill-dir>/migrdr.py plan <session> --scope <scope> > <scratchpad>/migrdr-plan.json
```

Read the plan. Each pane node has a `migrdr` object. Look for these cases:

- `status` is `working` or `blocked`, on a pane other than the caller. The agent loses its current turn.
- `dropped` names a process that stops, such as a dev server, or an agent with no resumable session.
- `args` carries a flag that should not survive, such as a stale prompt.

If any case applies, list each one and ask the user once: wait, skip those panes, or continue. To wait, run `herdr agent wait <name>` and make the plan again. To skip, delete those panes from the plan. If no case applies, continue without asking.

## 3. Apply the plan

```bash
timeout 900 python3 <skill-dir>/migrdr.py apply <scratchpad>/migrdr-plan.json
```

The output maps each source pane to its target pane. The caller resumes last. In each agent row, `started` is `ok` or an error.

- `agent_not_ready` means the agent waits at a startup dialog. Read it with `herdr --session <session> agent read <name>`, and leave the answer to the user.
- If `apply` stops with an error, leave the source open. Report what the target session now holds.

## 4. Verify the target

Run `herdr --session <session> agent list`. The step is done when each agent row in the plan with `args` appears under its new name and pane with the same `agent_session.value`. Do not close the source until this check passes.

## 5. Close the source

The plan's `close` list holds the commands. Closing ends the source processes, so run them only after step 4.

A `workspace_group_close_required` error means a primary workspace still has linked worktrees open. Close its tabs one by one with `herdr tab close`.

If the caller pane is in scope, closing the source ends this agent. Make this command the last tool call, and then give the report of step 6. The delay lets the report print before the pane closes.

```bash
setsid -f sh -c 'sleep 10; <close command>' >/dev/null 2>&1
```

The resumed copy of this agent holds the conversation up to the `apply` call. It does not see the rest of this turn.

## 6. Report the migration

Give the target session, and each workspace, tab, and pane with its new ID. Name each agent that resumed, each dropped process, and each dialog that waits for the user.
