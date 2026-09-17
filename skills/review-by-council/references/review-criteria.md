# Review criteria

## Context for reviewers

Give every reviewer the same scope context alongside the target, comparison base, and validation evidence:

- Requested outcome and acceptance criteria.
- Explicit exclusions and accepted limitations.
- Relevant deployment conditions and existing system invariants.
- Unresolved requirements and assumptions, marked as unresolved.

Cite user decisions or repository sources when available. Mark missing information as unknown.

Scope context conveys requirements, not the author's conclusions about correctness. Exclude suspected findings, private reasoning, and other reviewers' output.

Require reviewers to check scope claims against their sources and the implementation. Surface contradictions instead of accepting unsupported exclusions.

## Each finding

Report material findings with location, severity, claim, failure scenario, evidence, and the smallest correction direction. Also supply:

- Requirement or invariant at risk, with its source or an explicit statement that it is unknown.
- Applicability of the failure scenario to supported operating conditions.
- Attribution: introduced, worsened, pre-existing, or unknown relative to the review target.
- Scope disposition: required for this task, optional improvement, or needs a user decision.

Keep technical validity separate: confirmed, plausible, or refuted. A reproducible failure does not establish that this task must prevent it.

Existing security, data integrity, and compatibility invariants can establish a requirement without an explicit task sentence. Support the claimed invariant with evidence.

For a design, assess whether each major component serves the agreed outcome. Flag unnecessary components as well as missing behavior.

## Disposition

Preserve the reviewer's original severity and wording in the review record. Show scope assessment separately.

Only technically supported findings tied to an applicable requirement justify required changes.

Report an unresolved material requirement as a decision with options, costs, and consequences. Keep optional improvements separate from required corrections.
