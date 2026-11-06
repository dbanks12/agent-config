---
name: rdr
description: Route a request to a new Herdr worktree in a named session and repo. Usage: /rdr <session> <repo> <request>.
disable-model-invocation: true
---

# Route a request to a new worktree

Arguments are `<session> <repo> <request>`, for example `/rdr az aztec-node investigate and fix X`. If an argument is missing, show this usage and stop.

This session only routes. The new agent owns the request, so stop after the report in step 5.

## 1. Resolve the session and repo

| Session | Nickname | Searched first |
| --- | --- | --- |
| `aztec` | `az` | `~/aztec` |
| `side-quests` | `sq` | `~/projects` |

Any other session name must appear exactly in `herdr session list`, and it searches both directories in the order shown.

The repo is the directory with that exact name in the first searched directory that has one. Sibling names such as `obsidion-wallet-port` are other checkouts. If no exact match exists, list the near matches and stop.

## 2. Create the worktree

Fetch, and find the base. Use a base that the request names in place of `origin/HEAD`:

```bash
git -C <repo-path> fetch origin
git -C <repo-path> symbolic-ref --short refs/remotes/origin/HEAD
```

Choose a kebab-case slug of at most 32 characters that starts with a letter and describes the request. The slug is the branch name and the agent name. Then create the worktree:

```bash
herdr --session <session> worktree create --cwd <repo-path> --branch <slug> --base <base> --label "<short label>" --no-focus
```

Read `.result.root_pane.pane_id` and `.result.worktree.path`. If the branch or path already exists, choose a new slug. A `server_not_running` error means the session is stopped, so report the error and stop.

## 3. Start the agent

Use `claude`, unless the request names another agent.

```bash
herdr --session <session> agent start <slug> --kind claude --pane <pane-id>
```

For Codex, use `--kind codex` and append `-- -a never -s workspace-write`.

An `agent_not_ready` error means a startup dialog is open. Claude shows a trust dialog once for each repo that it does not trust yet. Read the dialog with `agent read`, and leave the answer to the user. Tell the user the session and pane, then wait:

```bash
herdr --session <session> agent wait <slug> --until idle --timeout 300000
```

If the wait times out, report the worktree and the undelivered prompt, then stop.

## 4. Send the prompt

The new agent has no memory of this conversation. Keep the request's own words, and replace references such as "this bug" or "the error above" with the facts, paths, links, and errors they mean.

```bash
herdr --session <session> agent prompt <slug> "$(cat <<'PROMPT'
<request>

You work in the new worktree <path> on branch <slug>, based on <base>. Rename the branch if the repo's rules need another name.
PROMPT
)" --wait --timeout 15000
```

Read the result:

- A `timeout` error means the agent is still working, so the prompt arrived. Confirm `working` with `herdr --session <session> agent get <slug>`.
- `.result.agent.agent_status` of `done` or `idle` means the agent already finished a turn.
- `.result.agent.agent_status` of `blocked` means the agent waits at a dialog. Tell the user the session and pane.
- An `agent_prompt_stalled` error, or `idle` straight after a startup dialog, can mean a lost prompt. Run `herdr --session <session> agent read <slug> --source recent-unwrapped --lines 40`. If the request is absent, send the prompt once more.

The step is done when `agent get` reports `working`, or when `agent read` on a settled agent shows the request.

## 5. Report the route

Give the session, repo, branch, worktree path, pane, and agent status. Quote any dialog that waits for the user.
