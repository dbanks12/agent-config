---
name: call-claude
description: Call Claude Code (Anthropic) as a separate process for any task, not only reviews. Use when the user wants to ask, consult, or cross-call a Claude model, or a fresh Claude process with no memory of this session, named with or without a version number, including Claude, Anthropic, Fable, Opus, Sonnet, Haiku. A bare family name means its latest version. Higher skills (review-with-claude, review-by-council) build on this one.
---

# Call Claude

Run Claude Code once as a separate, independent process. The current session stays the coordinator. In Codex this reaches a different vendor. In Claude Code it gives a fresh process with no memory of this session.

## Modes

- `prompt`: a free prompt on standard input. Use for questions, design reviews, document reviews, and second opinions.
- `code-review`: Claude Code's built-in `/code-review` skill. Use only for a review of code changes. It takes no extra instructions.

```bash
~/.config/cross-review/claude.sh prompt [-m MODEL] [-e EFFORT] <<'PROMPT'
...
PROMPT

~/.config/cross-review/claude.sh code-review [-m MODEL] [-e EFFORT] --target main...HEAD   # branch against main
~/.config/cross-review/claude.sh code-review [-m MODEL] [-e EFFORT] --target <sha>          # one commit
~/.config/cross-review/claude.sh code-review [-m MODEL] [-e EFFORT] --target <pr#|branch|path>
~/.config/cross-review/claude.sh code-review [-m MODEL] [-e EFFORT]                         # diff against the branch upstream; empty once pushed
```

Use a quoted heredoc to prevent shell expansion. Every mode is read-only. The script runs from the Git worktree root.

## Model

`-m` takes a Claude alias (fable, opus, sonnet, haiku) or a full model name. An alias means the latest version of that family. Leave `-m` unset when the user names no model or names only the family (Claude, Anthropic). If the user gives a version, pass the full model name.

The names that trigger this skill live in `~/.config/cross-review/models`. To add one, run `~/.config/cross-review/update-models.sh add claude <name> <alias>`. It re-renders the descriptions of the skills that trigger on model names.

## Fable fallback

The runner checks the weekly Fable limit before a run that would use Fable, which includes a run with no `-m`. If the limit is at 90 percent or more, the runner switches to Opus and prints `Fable usage is near limit (NN%). Using Opus instead of Fable.` Relay that line to the user.

If the user named Fable explicitly, pass `--pin`. The runner then uses Fable regardless of the limit. Do not pass `--pin` when you chose Fable yourself or when no model was named.

`~/.config/cross-review/fable-usage.sh` prints the current percent. `fable-usage.sh --near` exits 0 at or above the limit.

## Effort

`-e` takes low, medium, high, xhigh, or max. Use high for reviews. Leave it unset for a quick question.

## Rules

- If `ENGINEERING_CROSS_MODEL_REVIEW_ACTIVE` is set, stop. State that nested cross-model calls are disabled.
- Do not include secrets, credentials, environment files, private keys, or unrelated untracked files in a prompt.
- Run the call once. Do not start an exchange between models.
- If the script fails, report its exit status and error. Do not replace the failed call with your own answer to the same question.
- The output stays in this session. Do not post it to a pull request, an issue, a commit, or Slack unless the user asks after reading it.
- Name Claude as the source when you relay its answer. Do not weaken or reinterpret it.
