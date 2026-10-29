---
name: brief
description: Answer in a small number of short bullets (default 15 words max per bullet, 4 to 15 bullets chosen by content). Use whenever the user asks for a short answer in any wording, such as "keep it short", "tl;dr", or "be brief", or invokes /brief. Arguments override the defaults, e.g. "/brief 3", "/brief 3 20", or "/brief 5x16".
---

# Brief

Respond in at most N bullets. Each bullet has at most M words. Default M = 15. N defaults to a content-driven choice between 4 and 15.

## Arguments

Parse the arguments in this order. Any unset value keeps its default.

- `<n>x<m>` (for example `5x16`) sets N = n bullets and M = m words max per bullet.
- Otherwise, the first integer sets N (bullet count) and the second integer sets M (max words per bullet).
- `bullets=<n>` or `words=<m>` set the values by name in any order.
- Remaining text is the question or task to answer.

Examples:

- `/brief what does the resolver do` -> N chosen by content (4 to 15), M = 15.
- `/brief 3 explain the deposit flow` -> N = 3, M = 15.
- `/brief 3 20 explain the deposit flow` -> N = 3, M = 20.
- `/brief 5x16 explain the deposit flow` -> N = 5, M = 16.
- `/brief words=25 summarize this PR` -> N chosen by content, M = 25.

If no question is given, apply the format to the current or next request.

## Choosing N when it is not specified

Do the research or task first. Then pick the number of bullets the content needs, between 4 and 15. A simple answer gets closer to 4. A multi-part finding or a list of many items gets more, up to 15. Do not pad to reach a number.

## Rules

- Output at most N bullets and nothing else. No heading, preamble, or closing line.
- Count words per bullet excluding the leading `- `. Never exceed M. Trim words, not meaning.
- Fewer bullets and fewer words are always fine. More is not.
- One complete idea per bullet. Put the most important point first.
- Do not merge two ideas into one bullet with a semicolon to fit the count.
- If the answer truly cannot fit, use the last bullet to say what was left out.
- Keep these constraints for the rest of the conversation until the user changes or lifts them.
- Tool use and file reads are still allowed while working. The constraint applies to the final reply text only.
