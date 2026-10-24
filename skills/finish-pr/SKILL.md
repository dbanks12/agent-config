---
name: finish-pr
description: Take an open PR from draft to reviewable. Cross-tool review, a slim description with a diagram, and lean tests. Optionally flip it ready, address Greptile, and watch CI.
disable-model-invocation: true
argument-hint: "[ready] [ci]"
---

# Finish a pull request

Run the steps in order on the PR for the current branch. Find it with `gh pr view --json number,url,baseRefName,isDraft`. If no PR exists, stop and ask.

Arguments:

- `ready` (also `ready_and_greptile`, `greptile`): run step 4.
- `ci`: run step 5. It works with or without `ready`.

The bar for every fix in this skill is a **real problem**: a defect a user could hit, such as wrong funds movement, a crash, data loss, a security hole, or a broken flow. Style preferences, speculative hardening, and "consider also" ideas are not real problems. Record them as rejected and move on.

## 1. Run a cross-tool review

Use the reviewer from the other tool:

- In Claude Code: the `review-with-codex` skill with `-m gpt-6-astra`.
- In Codex: the `review-with-claude` skill with `-m opus`.

Review the branch against the PR base. Ask two review questions: which findings could affect users, and which changes fall outside the PR's stated outcome (**scope creep**).

Keep each finding that is a real problem. Fix it in a new commit. Revert scope creep in a new commit, unless the user asked for that change. Done when every finding has a disposition: fixed, reverted, or rejected with a one-line reason.

## 2. Trim the change

Read the full branch diff again. Rewrite in new commits:

- Comments: apply the repository's comment rules. Delete comments that restate the code or narrate the change.
- Tests: delete tests that only restate the implementation, check a constant, or duplicate another test's case. Collapse repeated setup into the file's existing helpers or a shared fixture. Merge near-identical cases into one table-driven test. Keep every test that guards a real problem.

Run the affected package tests and typecheck. Done when they pass and no comment or test fails the rules above.

## 3. Slim the PR description

Rewrite the body to carry only what a reviewer needs:

- **Context**: the problem, in two to four sentences.
- **Change**: what the PR does, at the level of concepts, in two to five sentences or bullets.
- **Diagram**: one Excalidraw diagram of the flow or structure that changed. Draw it with the `excalidraw-skill` skill and render a PNG.
- Any `Fixes <issue>` lines from the old body.

Cut file-by-file lists, test inventories, and history of how the work went.

Host the PNG on an orphan commit, without a checkout, then push it to `<branch>-pr-assets`:

```bash
blob=$(git hash-object -w diagram.png)
tree=$(printf '100644 blob %s\tdiagram.png\n' "$blob" | git mktree)
sha=$(git commit-tree "$tree" -m "docs: diagram for #<pr>")
git push origin "$sha:refs/heads/<branch>-pr-assets"
```

Embed it as `![<alt text that states the diagram's point>](https://github.com/<owner>/<repo>/blob/<sha>/diagram.png?raw=true)`. Update the body with `gh pr edit --body-file`. Done when the rendered body shows the image and has no section beyond the list above.

## 4. Flip ready and address Greptile (`ready`)

Push all commits. Run `gh pr ready`. Wait for a new review from `greptile-apps`. Poll `gh pr view --json reviews` every two minutes, with Monitor in Claude Code. Time out after 30 minutes and report. Read its inline comments with `gh api repos/<owner>/<repo>/pulls/<pr>/comments`.

Fix each real problem in a new commit and reply to its thread with the commit. Reply to the others with a one-line reason. Done when every Greptile comment has a reply.

## 5. Watch CI (`ci`)

Push all commits. Watch the checks with `timeout 3600 gh pr checks --watch`. For each failure, read the job log with `gh run view --log-failed`.

If the cause is clear and the fix is small, fix it in a new commit, push, and watch again. Otherwise, stop and report the failure with the log excerpt. A flaky failure unrelated to the diff is a report, not a fix. Done when all required checks pass, or every failure is reported.

## Report

List each review finding and Greptile comment with its disposition, the commits you added, and the final CI state.
