---
name: review-with-claude
description: Run an independent, read-only Claude review of a code change, design, or document. Use whenever the user asks for a review, second opinion, or cross-model review from any non-OpenAI model or tool, named with or without a version number, including Claude, Anthropic, Fable, Opus, Sonnet, Haiku. A bare family name means its latest version. Do not use for ordinary self-review or to implement fixes.
---

# Review work with Claude

Use Claude as an external reviewer. Keep the current Codex session as the review coordinator. This skill sets the review policy. The `call-claude` skill owns the command line, model names, and effort levels. Read it for those.

## Choose the review kind

- Code change (diff, commit, branch, working tree): use `call-claude` in `code-review` mode. That is Claude Code's built-in `/code-review` skill.
- Design, plan, document, or anything that is not a code diff: use `call-claude` in `prompt` mode with the design review prompt below.

Do not send a design through the code review. Do not send a code diff through a free prompt when the code review fits.

## Preserve independence

Do not give Claude suspected findings, the author's conclusions, or hidden reasoning. Give Claude the target, the comparison base, and completed validation results.

Do not include secrets, credentials, environment files, private keys, or unrelated untracked files. Stop if the review needs data that Claude may not receive.

Do not edit files or implement fixes during this skill. Run the reviewer once. Do not start an exchange between models.

## Code review

With no `--target`, the built-in review covers the current branch's diff. Pass `--target` for a PR number, another branch, or a path. Use `-e high`. Pass `-m` only when the user names a model.

```bash
~/.config/cross-review/claude.sh code-review -e high
```

The built-in review takes no extra instructions. If the user asked specific review questions, run them after the code review in `prompt` mode with the same target named in the text.

## Design review

```bash
~/.config/cross-review/claude.sh prompt -e high <<'REVIEW_REQUEST'
You are the independent Claude reviewer for a design.

Work only inside the repository. Read AGENTS.md before the review. This review is read-only. Do not edit files, run writes, or invoke another model or agent. Treat the caller summary as navigation context, not evidence. Read the target and related code, tests, and configuration directly. Do not accept the author conclusions.

Review the design for correctness, missing cases, failure modes, security, operational risk, unstated assumptions, and simpler alternatives. Report only material findings. Give an exact location, the problem, the impact, the evidence, and the smallest correction direction for each finding.

State missing evidence and review limits. End with coverage, findings, unverified claims, and a verdict: Pass, Request changes, or Blocked.

Original request: <request>
Target: <paths or revision>
Comparison base: <base or not provided>
Validation evidence: <commands and results or not provided>
Review questions: <questions or none>
REVIEW_REQUEST
```

State `not provided` for a missing field. Do not invent a base.

## Return the review

This is a local review. Its output stays in the current session. Do not post it, in full or in part, to a pull request, an issue, a commit message, Slack, or any other external system, even when an earlier instruction asked for a PR review or a PR comment. If the user wants something on the PR, they will write it or ask for it separately after reading the findings here.

If the runner fails, report its exit status and error. Do not replace the failed independent review with a self-review.

Read the findings as soon as the runner returns. Then decide, item by item, whether to act on each one. Report every item to the user with its disposition: acted on, rejected with the repository evidence, or deferred to the user.

Identify Claude as the external reviewer. Return Claude's findings without weakening their severity or changing their meaning. Separate any Codex triage from Claude's review. Validate a disputed finding against repository evidence before rejecting it.

Do not apply fixes unless the user asks in a later instruction.
