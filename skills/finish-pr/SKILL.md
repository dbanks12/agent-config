---
name: finish-pr
description: Finish an open pull request with a cross-tool review, trimmed comments and tests, and a slim description with a diagram. Optional steps mark it ready, request Greptile or LabsBox reviews, watch CI, link an explainer, and merge. Use when the user asks to finish, polish, or wrap up a PR, or to get it ready for review or merge. To open a new PR, use create-pr.
argument-hint: "[ready|robots|greptile|labsbox] [ci|ci-draft] [explainer [--review <level>]] [merge]"
---

# Finish a pull request

Run the steps in order on the PR for the current branch. Find it with `gh pr view --json number,url,baseRefName,isDraft`. If no PR exists, stop and ask.

Arguments:

- `ready` (also `ready_and_greptile`, `robots`): run step 4 with both Greptile and LabsBox.
- `greptile`: run step 4 with Greptile only, and keep the PR a draft.
- `labsbox`: run step 4 with LabsBox only. The PR becomes ready, because LabsBox ignores drafts.
- `ci`: run step 5. It works with or without a step 4 argument.
- `ci-draft`: run step 5, but first label the PR `ci-draft`.
- `merge`: run steps 5 and 6. Step 6 runs last.
- `explainer`: run step 7. It starts after step 3 and finishes before step 6. Options after it, such as `--review medium`, pass to the explainer skill.

When an agent invokes this skill, take the arguments from the user's own words. For example, "get it merged" means `merge`, and "watch CI" means `ci`. Run steps 1 to 3 only when the user asked for no optional step.

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
- With `explainer`, the explainer link from step 7.

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

## 4. Request and address bot reviews (`ready`, `robots`, `greptile`, `labsbox`)

Check for LabsBox before you change the PR. Run `gh api repos/<owner>/<repo>/labels/labsbox-review --silent`. A 404 means that the repository has no LabsBox review:

- With `ready` or `robots`, continue with Greptile only and report that LabsBox was skipped.
- With `labsbox`, leave the PR a draft, report the missing label, and end this step.
- Never create the label.

Push all commits. Record the time as `since` and the head SHA as `head`. Then request the reviews:

- **Ready**: with every argument except `greptile`, run `gh pr ready`.
- **Greptile**: with `greptile`, comment `gh pr comment --body "@greptileai"`. With `ready` or `robots` on a PR that was already ready, post the same comment, because `gh pr ready` starts nothing there.
- **LabsBox**: after the PR is ready, run `gh pr edit --add-label labsbox-review`. If the PR already has the label, remove it first, because only a new `labeled` event starts a review.

Poll every 30 seconds, with Monitor in Claude Code. Each poll lists the bot inline comments created after `since`:

```bash
gh api --paginate "repos/<owner>/<repo>/pulls/<pr>/comments?since=<since>" \
  --jq '.[] | select(.user.login == "greptile-apps[bot]" or .user.login == "labsbox[bot]") | "\(.id) \(.user.login) \(.path):\(.line)"'
```

Address each new comment as soon as it appears. Do not wait for the full review. Time out after 30 minutes and report. Each review finishes as follows:

- **Greptile**: `gh pr view --json reviews` shows a new review from `greptile-apps`, and no new comments arrive for one minute. With `labsbox`, Greptile may also start when the PR becomes ready. Address its comments that arrive, and do not wait for its review.
- **LabsBox**: `gh api repos/<owner>/<repo>/pulls/<pr>/reviews` shows a review from `labsbox[bot]` with `commit_id` equal to `head`. Report a body that says LabsBox could not or did not complete the review. If the body lists findings because GitHub rejected the inline comments, address them and answer in one PR comment.

LabsBox reacts `eyes` on the PR when it accepts the label (`gh api repos/<owner>/<repo>/issues/<pr>/reactions`). It rejects a request silently for a fork, more than 200 files, more than 10,000 changed lines, or an author or labeler outside the organization. If no `labsbox[bot]` reaction appears within two minutes, report the rejection and stop waiting for LabsBox.

Fix each real problem in a new commit. While a LabsBox review is pending, hold the push, because LabsBox discards its review when the head moves. Push when LabsBox posts, rejects the request, or times out. Then reply to each thread with the commit. Reply to the other comments with a one-line reason. Done when every requested review has finished and every bot comment has a reply.

## 5. Watch CI (`ci`, `ci-draft`)

Push all commits. With `ci-draft`, run `gh pr edit --add-label ci-draft`. Watch the checks with `timeout 3600 gh pr checks --watch`. For each failure, read the job log with `gh run view --log-failed`.

If the cause is clear and the fix is small, fix it in a new commit, push, and watch again. Otherwise, stop and report the failure with the log excerpt. A flaky failure unrelated to the diff is a report, not a fix. Done when all required checks pass, or every failure is reported.

## 6. Merge (`merge`)

Merge only after every earlier step is done, step 7 too with `explainer`, and all required checks pass on the latest pushed commit. If a check failed, a bot review comment has no reply, or a fix is not pushed, stop and report.

Merge with the repository's allowed method, for example `gh pr merge --squash`. Do not pass `--admin` and do not bypass branch protection. If a review or other rule blocks the merge, stop and report the blocker. Done when GitHub shows the PR as merged.

## 7. Link an explainer (`explainer`)

The `explainer` argument is the user's request for one explainer of this PR, so it authorizes that job under the explainer skill's rules. Start it as soon as step 3 is done, as the explainer skill's background worker, so it runs while steps 4 and 5 wait on the bot reviews and CI.

- Sources: the slim PR description and the changed files the script describes. Host: standalone.
- Look: the Excalidraw sketch, to match the PR diagram, so skip the style board. Use another look only when the user named one.
- Mode: `narrated` when the explainer skill's preflight passes, else `captions`.
- Publish the page as a private Artifact. In Codex, follow "Artifacts from Codex" in `AGENTS.md`.
- Add one line under the diagram: `▶ [Narrated explainer, <m:ss>](<artifact url>)`, or `Captioned explainer` in `captions` mode. Update the body the way step 3 does.
- Tell the user that the Artifact is private. Reviewers can open it only after the user shares it from the page's Share menu.

Done when the PR body shows the link and the explainer's manifest says `ready`.

## Report

List each review finding and bot comment with its disposition, the commits you added, the final CI state, the explainer link, and the merge result.
