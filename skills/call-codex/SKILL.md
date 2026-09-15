---
name: call-codex
description: Call Codex (OpenAI) as a separate process for any task, not only reviews. Use when the user wants to ask, consult, or cross-call an OpenAI model or tool, named with or without a version number, including Codex, OpenAI, GPT, astra, sol, terra, luna. A bare family name means its latest version. Higher skills (review-with-codex, review-by-council) build on this one.
---

# Call Codex

Run Codex once as a separate, independent process. The current session stays the coordinator. In Claude Code this reaches a different vendor. In Codex it gives a fresh process with no memory of this session.

## Modes

- `prompt`: a free prompt on standard input. Use for questions, design reviews, document reviews, and second opinions.
- `code-review`: Codex's built-in code review. Use only for a review of code changes. It takes a target flag or stdin instructions, not both.

```bash
~/.config/cross-review/codex.sh prompt [-m MODEL] [-e EFFORT] <<'PROMPT'
...
PROMPT

~/.config/cross-review/codex.sh code-review [-m MODEL] [-e EFFORT] --base <branch>
~/.config/cross-review/codex.sh code-review [-m MODEL] [-e EFFORT] --commit <sha>
~/.config/cross-review/codex.sh code-review [-m MODEL] [-e EFFORT] --uncommitted
~/.config/cross-review/codex.sh code-review [-m MODEL] [-e EFFORT] <<'PROMPT'
Review the changes against <base>. <extra instructions>
PROMPT
```

Use a quoted heredoc to prevent shell expansion. Every mode is read-only. The script runs from the Git worktree root.

## Model

`-m` takes a short name from `~/.config/cross-review/models` (astra, sol, terra, luna) or an exact Codex model. The script resolves short names to the CLI model. Leave `-m` unset when the user names no model or names only the family (Codex, GPT). If the user gives a version, pass the exact model.

To add a name, run `~/.config/cross-review/update-models.sh add openai <name> <cli-model>`. It re-renders the descriptions of the skills that trigger on model names.

## Effort

`-e` takes low, medium, high, or xhigh. Use high for reviews. Leave it unset for a quick question.

## Rules

- If `ENGINEERING_CROSS_MODEL_REVIEW_ACTIVE` is set, stop. State that nested cross-model calls are disabled.
- Do not include secrets, credentials, environment files, private keys, or unrelated untracked files in a prompt.
- Run the call once. Do not start an exchange between models.
- If the script fails, report its exit status and error. Do not replace the failed call with your own answer to the same question.
- The output stays in this session. Do not post it to a pull request, an issue, a commit, or Slack unless the user asks after reading it.
- Name Codex as the source when you relay its answer. Do not weaken or reinterpret it.
