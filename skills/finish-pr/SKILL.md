---
name: finish-pr
description: Take an open PR from draft to reviewable. Cross-tool review, a slim description with a diagram, and lean tests. Optionally flip it ready or request Greptile on the draft, address Greptile, watch CI, and merge.
disable-model-invocation: true
argument-hint: "[ready|greptile] [ci|ci-draft] [merge]"
---

# Finish a pull request

Run the steps in order on the PR for the current branch. Find it with `gh pr view --json number,url,baseRefName,isDraft`. If no PR exists, stop and ask.

Arguments:

- `ready` (also `ready_and_greptile`): run step 4.
- `greptile`: run step 4, but keep the PR a draft. Comment `@greptileai` instead of `gh pr ready`.
- `ci`: run step 5. It works with or without `ready` or `greptile`.
- `ci-draft`: run step 5, but first label the PR `ci-draft`.
- `merge`: run steps 5 and 6. Step 6 runs last.

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
- **Screenshots**: for a UI change, the before and after captures, in a table with one column per viewport.
- Any `Fixes <issue>` lines from the old body.

Cut file-by-file lists, test inventories, and history of how the work went.

Upload the images through the GitHub REST API. Do not commit them with local git. Create one blob per image, one tree, one parentless commit, and the ref `<branch>-pr-assets`:

```bash
R=repos/<owner>/<repo>
blob=$(base64 -w0 diagram.png | jq -Rs '{content: ., encoding: "base64"}' \
  | gh api $R/git/blobs --input - --jq .sha)
# Repeat for each image. Put every blob in one tree.
tree=$(jq -n --arg b "$blob" '{tree: [{path: "diagram.png", mode: "100644", type: "blob", sha: $b}]}' \
  | gh api $R/git/trees --input - --jq .sha)
sha=$(gh api $R/git/commits -f message="docs: images for #<pr>" -f tree="$tree" --jq .sha)
gh api $R/git/refs -f ref="refs/heads/<branch>-pr-assets" -f sha="$sha"
```

If the ref exists, update it with `gh api -X PATCH $R/git/refs/heads/<branch>-pr-assets -f sha="$sha" -F force=true`.

Embed each image as `https://github.com/<owner>/<repo>/blob/<sha>/<file>?raw=true`. Write alt text that states the image's point. Update the body with `gh api -X PATCH $R/pulls/<pr> -F body=@body.md`. Done when the rendered body (`gh api $R/pulls/<pr> -H "Accept: application/vnd.github.html+json" --jq .body_html`) has every image and no section beyond the list above.

## 4. Flip ready and address Greptile (`ready`, `greptile`)

Push all commits. Record the time as `since`. With `ready`, run `gh pr ready`. With `greptile`, run `gh pr comment --body "@greptileai"` and leave the PR a draft.

Poll every 30 seconds, with Monitor in Claude Code. Each poll lists the `greptile-apps[bot]` inline comments created after `since`:

```bash
gh api --paginate "repos/<owner>/<repo>/pulls/<pr>/comments?since=<since>" \
  --jq '.[] | select(.user.login == "greptile-apps[bot]") | "\(.id) \(.path):\(.line)"'
```

Address each new comment as soon as it appears. Do not wait for the full review. Keep polling until `gh pr view --json reviews` shows a new review from `greptile-apps` and no new comments arrive for one minute. Time out after 30 minutes and report.

Fix each real problem in a new commit and reply to its thread with the commit. Reply to the others with a one-line reason. Done when every Greptile comment has a reply.

## 5. Watch CI (`ci`, `ci-draft`)

Push all commits. With `ci-draft`, run `gh pr edit --add-label ci-draft`. Watch the checks with `timeout 3600 gh pr checks --watch`. For each failure, read the job log with `gh run view --log-failed`.

If the cause is clear and the fix is small, fix it in a new commit, push, and watch again. Otherwise, stop and report the failure with the log excerpt. A flaky failure unrelated to the diff is a report, not a fix. Done when all required checks pass, or every failure is reported.

## 6. Merge (`merge`)

Merge only after every earlier step is done and all required checks pass on the latest pushed commit. If a check failed, a Greptile comment has no reply, or a fix is not pushed, stop and report.

Merge with the repository's allowed method, for example `gh pr merge --squash`. Do not pass `--admin` and do not bypass branch protection. If a review or other rule blocks the merge, stop and report the blocker. Done when GitHub shows the PR as merged.

## Report

List each review finding and Greptile comment with its disposition, the commits you added, the final CI state, and the merge result.
