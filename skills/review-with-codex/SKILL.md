---
name: review-with-codex
description: Run an independent, read-only Codex review of a code change, design, or document. Use whenever the user asks for a review, second opinion, or cross-model review from any non-Claude model or tool, named with or without a version number, including Codex, OpenAI, GPT, astra, sol, terra, luna. A bare family name means its latest version. Do not use for ordinary self-review or to implement fixes.
---

# Review work with Codex

Use Codex as an external reviewer. Keep the current Claude session as the review coordinator. This skill sets the review policy. The `call-codex` skill owns the command line, model names, and effort levels. Read it for those.

Read and apply [requirements and review scope](../review-by-council/references/scope.md) before every review. Paste the policy text and sourced scope context into the review request. Reviewers must not need an external policy-file read.

## Choose the review kind

- Code change (diff, commit, branch, working tree): use `call-codex` in `code-review` mode. That is Codex's built-in code review.
- Design, plan, document, or anything that is not a code diff: use `call-codex` in `prompt` mode with the design review prompt below.

Do not send a design through the code review. Use prompt mode for code when the native review cannot receive the required scope context. Name the exact diff target in the prompt.

## Preserve independence

Do not give Codex suspected findings, the author's conclusions, or hidden reasoning. Give Codex the target, comparison base, validation results, and sourced scope context from the shared policy.

Do not include secrets, credentials, environment files, private keys, or unrelated untracked files. Stop if the review needs data that Codex may not receive.

Do not edit files or implement fixes during this skill. Run the external reviewer once. Do not start an exchange between models.

## Code review

Pick the target flag from the change: `--base <branch>` for a branch, `--commit <sha>` for one commit, `--uncommitted` for the working tree. Use `-e high`. Pass `-m` only when the user names a model.

```bash
~/.config/cross-review/codex.sh code-review -e high --base main
```

The target form takes no extra text. If the user explicitly requests target flags, assess scope locally after the review. Report the missing reviewer context without another model call. Otherwise, use the stdin form to include scope context and the shared policy. Name the exact base or commit in the text:

```bash
~/.config/cross-review/codex.sh code-review -e high <<'REVIEW_REQUEST'
Review the changes against main.
Apply this review policy:
<paste the full shared scope policy here>
Scope context: <outcome, acceptance criteria, exclusions, accepted limitations, operating conditions, sources, and unknowns>
Validation evidence: <commands and results or not provided>
Review questions: <questions>
REVIEW_REQUEST
```

## Design review

```bash
~/.config/cross-review/codex.sh prompt -e high <<'REVIEW_REQUEST'
You are the independent Codex reviewer for a design.

Work only inside the repository. Read AGENTS.md before the review. This review is read-only. Do not edit files, run writes, or invoke another model or agent. Treat the caller summary as navigation context, not evidence. Read the target and related code, tests, and configuration directly. Do not accept the author conclusions.

Review the design for correctness, missing cases, failure modes, security, operational risk, unstated assumptions, and simpler alternatives. Report only material findings. Give an exact location, the problem, the impact, the evidence, and the smallest correction direction for each finding.

State missing evidence and review limits. End with coverage, findings, unverified claims, and a verdict: Pass, Request changes, or Blocked.

Review policy:
<paste the full shared scope policy here>
Scope context: <outcome, acceptance criteria, exclusions, accepted limitations, operating conditions, sources, and unknowns>
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

Read the findings as soon as the runner returns. Assess each item against the shared scope policy before recommending action. Report every item to the user with its disposition: acted on, rejected with the repository evidence, or deferred to the user.

Identify Codex as the external reviewer. Return Codex's findings without weakening their severity or changing their meaning. Separate any Claude triage from Codex's review. Validate a disputed finding against repository evidence before rejecting it.

Do not apply fixes unless the user asks in a later instruction.
