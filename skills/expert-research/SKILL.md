---
name: expert-research
description: Research expert guidance and practitioner agreement on engineering tools, processes, design decisions, and problem-solving approaches. Use for requests about what experienced engineers recommend or industry consensus. Not for routine documentation lookups.
---

# Expert Research

Find what experienced practitioners recommend, why they recommend it, and where their advice differs.
Treat agreement as a finding to establish, not an outcome to assume.

## Scope and dates

- Use the user's question, constraints, preferred sources, and requested date window.
- Interpret time windows relative to the current date unless the user gives an end date.
- Without a date window, balance current advice with established guidance.
- Label older foundational material separately when the user requests recent evidence.
- Check publication dates rather than search-engine crawl dates.
- Ask a focused question only when missing context materially changes the recommendation.

Examples:

- `/expert-research What do experienced engineers recommend for code review?`
- `/expert-research Agent orchestration tools — last 6 months`
- `$expert-research How do experienced engineers approach database migrations?`

## Find evidence

- Use available web search and browsing tools to research the question.
- Start with engineering blogs, prominent engineers and AI practitioners on X, and relevant GitHub issues or discussions.
- Search recent, highly upvoted Reddit posts, Hacker News discussions, and relevant specialist forums.
- Follow relevant comments and replies, not only post titles or summaries.
- Select sources for the topic rather than forcing every platform into every report.
- Use engagement to discover useful discussions, not to establish expertise or correctness.
- Verify important claims against original posts, technical documentation, code, benchmarks, or reported production experience.
- Seek independent accounts and credible counterarguments before calling a view widely shared.
- If search tools or sources are unavailable, disclose the gap and use accessible alternatives.
- Do not imply that an inaccessible source was searched.

This skill requires no specific plugin, additional account, or background service.
If saved research is available, check its dates and coverage before reuse.
Label reused evidence and refresh claims whose currency affects the answer.

## Assess advice

- Identify each important author's relevant work or firsthand experience when available.
- Separate production experience and measured results from speculation, vendor claims, and promotion.
- Explain the reasoning behind recommendations, including applicable workloads, team constraints, and tradeoffs.
- Treat reposts and articles citing one original claim as one evidence chain.
- Distinguish agreement among sampled practitioners from claims about the entire industry.
- Preserve credible minority views and unresolved questions.
- Do not infer agreement from silence, high vote counts, or repeated marketing claims.
- When evidence is thin or conflicting, say that it cannot establish consensus.
- Distinguish your recommendation from the sources' statements and your own inferences.

## Report

Adapt length and format to the user's request. By default, cover these points in order:

1. **Recommendation:** State what the evidence suggests for the user's question.
2. **Areas of agreement:** Describe recurring guidance across independent practitioners.
3. **Disagreements and tradeoffs:** Explain objections and conditions that change the advice.
4. **Sources and limits:** Identify important authors, dates, relevant experience, and gaps in coverage.

Link original sources beside the claims they support.
Distinguish documented capabilities from features you actually tested when comparing tools.
State the research window and whether material conclusions rely on saved research.
