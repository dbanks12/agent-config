# Sources for scope and review guidance

These sources informed the requirements section in AGENTS.md and the shared review policy. The rules are a local synthesis, not quotations.

- [Anthropic: Claude Code best practices](https://code.claude.com/docs/en/best-practices) recommends exploration, planning, and interviews for ambiguous work. It also advises concise persistent guidance and explicit exclusions in specifications. We apply focused questions to material unknowns without requiring planning for every edit.
- [OpenAI: Codex best practices](https://learn.chatgpt.com/guides/best-practices) recommends goals, context, constraints, completion criteria, and planning for difficult tasks. We preserve those decisions across implementation and review.
- [Google: What to look for in a code review](https://google.github.io/eng-practices/review/reviewer/looking-for.html) asks whether functionality belongs and warns against speculative generality. We require evidence that a reported defect violates an applicable requirement.
- [Google: Small changelists](https://google.github.io/eng-practices/review/developer/small-cls.html) recommends one self-contained concept and early consideration of dependent changes. We distinguish PR decomposition from authorization for additional outcomes.
- [Addy Osmani: My LLM coding workflow going into 2026](https://addyosmani.com/blog/ai-coding-workflow/) describes interactive specifications and incremental implementation. We use explicit constraints and manageable work items without mandating a new specification file.
- [Harper Reed: My LLM codegen workflow atm](https://harper.blog/2025/02/16/my-llm-codegen-workflow-atm/) separates requirement discovery, planning, and execution. We ask focused questions and preserve answers for later work.
- [Armin Ronacher: What Actually Is Claude Code’s Plan Mode?](https://lucumr.pocoo.org/2025/12/17/what-is-plan-mode/) examines planning as a workflow of context, questions, and a written plan. We recommend the workflow where useful without treating the mode switch as sufficient.

The local scope audit identified a specific gap: technical verification did not establish whether preventing a failure was required. The shared policy therefore separates technical validity, requirement applicability, and authorization. Reviewer agreement and severity remain evidence, not permission to expand implementation.
