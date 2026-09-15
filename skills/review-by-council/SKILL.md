---
name: review-by-council
description: Review a code change or design with several independent models in parallel, then dedupe, verify, and report the findings. Use when the user asks for a council, panel, multi-model, or consensus review, or for "all the models" to review something. Default seats are fable, opus, astra, and sol at high effort.
---

# Review by council

Several models review the same target independently. The current session is the chair. The chair does not review. It launches the seats, merges their findings, verifies each one, and reports.

Findings are not put to a vote. A finding that one seat raised and the verifier confirmed outranks a finding that three seats raised and the verifier refuted. Agreement sets priority. Verification decides what is reported.

## Seats

Default seats, each at effort high:

| Seat  | Runner (`<mode>` is `code-review` or `prompt`)          |
|-------|----------------------------------------------------------|
| fable | `~/.config/cross-review/claude.sh <mode> -m fable -e high` |
| opus  | `~/.config/cross-review/claude.sh <mode> -m opus -e high`  |
| astra | `~/.config/cross-review/codex.sh <mode> -m astra -e high`  |
| sol   | `~/.config/cross-review/codex.sh <mode> -m sol -e high`    |

The user can name other seats or another effort. A seat whose CLI is missing is skipped and named in the report. Read `call-claude` and `call-codex` for model names and flags.

Every seat is a separate process with no memory of this session. The chair gives a seat the target only. It never gives a seat suspected findings, the author's conclusions, or another seat's output.

## Review kind

- Code change: each seat runs the tool's built-in code review, and every seat gets the same base. Claude's built-in review defaults to the branch's upstream, which can be empty on a pushed branch, so pass the base as a range. Claude seats: `claude.sh code-review --target <base>...HEAD`. Codex seats: `codex.sh code-review --base <base>`. For one commit use `--target <sha>` and `--commit <sha>`. For the working tree use `--target HEAD` and `--uncommitted`.
- Design or document: each seat runs `prompt` mode with the design review prompt from `review-with-claude` or `review-with-codex`. Use the same prompt text for every seat.

## Run

1. Launch every seat at once in the background. Send each seat's output to its own file. Record each seat's exit status. A bare `wait` returns 0 even when a seat failed.

```bash
cd "$(git rev-parse --show-toplevel)"; out=$(mktemp -d); pids=(); seats=()
~/.config/cross-review/claude.sh code-review -m fable -e high --target main...HEAD > "$out/fable.txt" 2>&1 & pids+=($!); seats+=(fable)
~/.config/cross-review/claude.sh code-review -m opus  -e high --target main...HEAD > "$out/opus.txt"  2>&1 & pids+=($!); seats+=(opus)
~/.config/cross-review/codex.sh  code-review -m astra -e high --base main > "$out/astra.txt" 2>&1 & pids+=($!); seats+=(astra)
~/.config/cross-review/codex.sh  code-review -m sol   -e high --base main > "$out/sol.txt"   2>&1 & pids+=($!); seats+=(sol)
for i in "${!pids[@]}"; do wait "${pids[$i]}" || echo "${seats[$i]} rc=$?" >> "$out/failed.txt"; done
echo "$out"; cat "$out/failed.txt" 2>/dev/null
```

2. Read every seat's output. Extract each finding as: file, line, severity, one-sentence claim, failure scenario, seat. A Codex transcript prints its final message twice. Read it once.

3. Merge. Two findings are the same when they name the same file, lines within three of each other, and the same defect in substance. Keep the clearest wording. Record every seat that raised it.

4. Verify each merged finding with one fresh verifier per finding, all in parallel. A verifier gets one finding and the repository. It does not get the other findings, the seat names, or the count of seats. It returns one of: confirmed, plausible, or refuted, with evidence from the code or from running it.
   - In Claude Code, use one Agent subagent per finding.
   - In Codex, use `~/.config/cross-review/codex.sh prompt -m astra -e high` per finding.
   - Verification uses the host tool's strongest model at effort high. The task is narrow, so the cost per finding is small, and this step decides what the user sees.

5. Report. Sort confirmed findings by severity, then by seat count. Show for each: severity, file:line, claim, failure scenario, seats, verifier evidence. List plausible findings after them. List refuted findings last in a short appendix with the refuting evidence, so the user can overrule. Name skipped or failed seats.

## Rules

- If `ENGINEERING_CROSS_MODEL_REVIEW_ACTIVE` is set, stop. State that nested cross-model review is disabled.
- Do not include secrets, credentials, environment files, private keys, or unrelated untracked files in a prompt.
- Do not edit files or implement fixes during this skill. The user decides after reading the report.
- The report stays in this session. Do not post it to a pull request, an issue, a commit, or Slack unless the user asks after reading it.
- Return each seat's findings without weakening their severity. Keep chair triage separate from seat output.
- If a seat fails, report its exit status and error. Do not replace it with a chair review.

## Time and cost

Seats run in parallel, so the review phase takes as long as the slowest seat. Claude's built-in review at high fans out to subagents and is the slowest seat, often several minutes on a small diff. Verification runs in parallel and adds one round. Expect about 1.5 to 2 times the wall-clock of one review, and 3 to 4 times the tokens.
