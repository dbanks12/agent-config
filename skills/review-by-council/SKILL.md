---
name: review-by-council
description: Review a code change or design with several independent models in parallel, then dedupe, verify, and report the findings. Use when the user asks for a council, panel, multi-model, or consensus review, or for "all the models" to review something. Default seats are fable, opus, astra, and sol at high effort.
---

# Review by council

Several models review the same target independently. The current session is the chair. The chair does not review. It launches the seats, merges their findings, verifies each one, and reports.

Findings are not put to a vote. A finding that one seat raised and the verifier confirmed outranks a finding that three seats raised and the verifier refuted. Agreement sets priority within a disposition. Verification checks technical validity and requirement applicability separately.

Read and apply [review criteria](references/review-criteria.md) before preparing prompts or assessing findings. Paste the review criteria into seat and verifier prompts to avoid external file reads.

## Seats

Default seats, each at effort high:

| Seat  | Runner (`<mode>` is `code-review` or `prompt`)          |
|-------|----------------------------------------------------------|
| fable | `~/.config/cross-review/claude.sh <mode> -m fable -e high` |
| opus  | `~/.config/cross-review/claude.sh <mode> -m opus -e high`  |
| astra | `~/.config/cross-review/codex.sh <mode> -m astra -e high`  |
| sol   | `~/.config/cross-review/codex.sh <mode> -m sol -e high`    |

The user can name other seats or another effort. A seat whose CLI is missing is skipped and named in the report. Read `call-claude` and `call-codex` for model names and flags.

Fable seat and the weekly limit: before launch, run `~/.config/cross-review/fable-usage.sh --near`. If it exits 0 and the user did not name Fable, drop the fable seat and print `Fable usage is near limit. Dropping Fable agent from council.` The other seats run as normal. If the user named Fable, keep the seat and pass `--pin` to its runner.

Every seat is a separate process with no memory of this session. The chair gives every seat the same target and sourced scope context from the shared review criteria. It never gives a seat suspected findings, the author's conclusions, or another seat's output.

## Review kind

- Code change: include the shared review criteria and scope context in every seat request. Use Codex's stdin code-review form and Claude's prompt mode. Name the exact base, commit, or working-tree target in the prompt. When the user explicitly requests native review, each seat runs the tool's built-in code review, and every seat gets the same base. Claude's built-in review defaults to the branch's upstream, which can be empty on a pushed branch, so pass the base as a range. Claude seats: `claude.sh code-review --target <base>...HEAD`. Codex seats: `codex.sh code-review --base <base>`. For one commit use `--target <sha>` and `--commit <sha>`. For the working tree use `--target HEAD` and `--uncommitted`.
- Design or document: each seat runs `prompt` mode with the design review prompt from `review-with-claude` or `review-with-codex`. Use the same prompt text for every seat. Include the shared review criteria and scope context.
- For an explicitly requested native review, supply scope context during verification and mark the limitation in the report.

## Run

1. Check the Fable limit as described under Seats. Then launch every seat at once in the background. Send each seat's output to its own file. Record each seat's exit status. A bare `wait` returns 0 even when a seat failed.

Prepare `/tmp/council-request.txt` with the exact target, shared review criteria, and scope context. Omit skipped seats from this example. If the user explicitly named Fable, add `--pin` to its command. For a design or document, set `codex_mode=prompt`.

```bash
cd "$(git rev-parse --show-toplevel)" || exit 1
prompt=/tmp/council-request.txt
[[ -s "$prompt" ]] || { echo "Prepare $prompt before launch." >&2; exit 1; }
out=$(mktemp -d)
pids=()
seats=()
codex_mode=code-review

~/.config/cross-review/claude.sh prompt -m fable -e high < "$prompt" > "$out/fable.txt" 2>&1 &
pids+=($!); seats+=(fable)
~/.config/cross-review/claude.sh prompt -m opus -e high < "$prompt" > "$out/opus.txt" 2>&1 &
pids+=($!); seats+=(opus)
~/.config/cross-review/codex.sh "$codex_mode" -m astra -e high < "$prompt" > "$out/astra.txt" 2>&1 &
pids+=($!); seats+=(astra)
~/.config/cross-review/codex.sh "$codex_mode" -m sol -e high < "$prompt" > "$out/sol.txt" 2>&1 &
pids+=($!); seats+=(sol)

for i in "${!pids[@]}"; do
  rc=0
  wait "${pids[$i]}" || rc=$?
  printf '%s rc=%s\n' "${seats[$i]}" "$rc" >> "$out/status.txt"
done
printf 'Review output: %s\n' "$out"
cat "$out/status.txt"
```

2. Read every seat's output. Extract each finding as: file, line, severity, claim, failure scenario, seat, requirement source, applicability, attribution, and scope disposition. A Codex transcript prints its final message twice. Read it once.

3. Merge. Two findings are the same when they name the same file, lines within three of each other, and the same defect in substance. Keep the clearest wording. Record every seat that raised it.

4. Verify each merged finding with one fresh verifier per finding, all in parallel. A verifier gets one finding, the repository, and the shared review criteria with sourced scope context. It does not get the other findings, the seat names, or the count of seats. It returns technical validity (confirmed, plausible, or refuted), requirement applicability, attribution, and scope disposition. Require evidence for both the defect and its claimed requirement.
   - In Claude Code, use one Agent subagent per finding.
   - In Codex, use `~/.config/cross-review/codex.sh prompt -m astra -e high` per finding.
   - Verification uses the host tool's strongest model at effort high. The task is narrow, so the cost per finding is small, and this step decides what the user sees.

5. Report required corrections, unresolved scope decisions, and optional improvements separately. Sort within each group by validity, severity, then seat count. Show the finding fields and verifier evidence from both checks. List refuted findings in a short appendix with evidence. Name skipped or failed seats and any missing context.

## Rules

- If `ENGINEERING_CROSS_MODEL_REVIEW_ACTIVE` is set, stop. State that nested cross-model review is disabled.
- Do not include secrets, credentials, environment files, private keys, or unrelated untracked files in a prompt.
- Do not edit files or implement fixes during this skill. The user decides after reading the report.
- The report stays in this session. Do not post it to a pull request, an issue, a commit, or Slack unless the user asks after reading it.
- Return each seat's findings without weakening their severity. Keep chair triage separate from seat output.
- If a seat fails, report its exit status and error. Do not replace it with a chair review.

## Time and cost

Seats run in parallel, so the review phase takes as long as the slowest seat. Verification adds another parallel round. Native Claude review can fan out to subagents. Prompt-mode seats use one process each.
