---
name: review-with-claude
description: Run an independent, read-only Claude review of a code change. Use whenever the user asks for a review, second opinion, or cross-model review from any non-OpenAI model or tool, named with or without a version number, including Claude, Anthropic, Fable, Opus, Sonnet, Haiku. A bare family name means its latest version. Do not use for ordinary self-review or to implement fixes.
---

# Review work with Claude

Use Claude as an external reviewer. Keep the current Codex session as the review coordinator.

## Preserve independence

Do not give Claude suspected findings, the author's conclusions, or hidden reasoning. Give Claude the original request, the review target, the comparison base, and completed validation results.

Do not include secrets, credentials, environment files, private keys, or unrelated untracked files. Stop if the requested review requires data that Claude may not receive.

Do not edit files or implement fixes during this skill. Run the external reviewer once. Do not start a review exchange between models.

## Select the model

The user may name the reviewer by family or codename alone (for example "opus", "gpt", "astra") or with a version number. If they give a version, use it. If they give only a family or codename, use the latest version of it. Set `ENGINEERING_CLAUDE_REVIEW_MODEL` to the name the Claude CLI accepts for that choice; leave it unset when the user names no model.

The list of trigger names lives in `~/.config/cross-review/models`. To add a name, run `~/.config/cross-review/update-models.sh add <claude|openai> <name>`; it re-renders this file's description.

## Prepare the request

Include these fields:

- Original user request.
- Target documents, files, commit, branch, or working-tree changes.
- Comparison base.
- Validation commands and results already available.
- Specific review questions from the user.

State `not provided` for a missing field. Do not invent a base.

## Run Claude

The runner uses the `fable` model alias with high effort by default.

Pass the request through standard input. Use a quoted heredoc to prevent shell expansion:

```bash
~/.codex/skills/review-with-claude/scripts/run-review.sh <<'REVIEW_REQUEST'
Original request: <request>
Target: <paths or revision>
Comparison base: <base or not provided>
Validation evidence: <commands and results or not provided>
Review questions: <questions or none>
REVIEW_REQUEST
```

If `ENGINEERING_CROSS_MODEL_REVIEW_ACTIVE` is set, stop. State that nested cross-model review is disabled.

If the runner fails, report its exit status and error. Do not replace the failed independent review with a self-review.

## Return the review

Identify Claude as the external reviewer. Return Claude's findings without weakening their severity or changing their meaning.

Separate any Codex triage from Claude's review. Validate a disputed finding against repository evidence before rejecting it.

Do not apply fixes unless the user asks in a later instruction.
