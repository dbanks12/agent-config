---
name: teach-me
description: Teach the user one technical subject (a tool, system, protocol, or concept) as a published HTML artifact with clickable glossary terms, simple system diagrams, and a fixed section order. Use when the user asks to be taught something, wants an explainer or primer page, says "explain X to me" for a page-sized answer, or invokes /teach-me <subject>. Not for short chat answers.
---

# Teach me

Build one HTML artifact that teaches a subject to a smart engineer who has never used it. Publish it with the Artifact tool. The Artifact tool requires the `artifact-design` and `artifact-diagramming` skills. Load them, then follow this skill for structure, length, and mechanics. This skill wins where they differ.

## Audience

- Assume no prior knowledge of the subject. Define even basic nouns. Do not assume the reader knows what a "topic" or a "range" is.
- Assume general engineering literacy. Do not explain what a server, a file, or a database is.
- The reader is preparing for design discussions. Favor the mental model over configuration detail.

## Length budget

The page is short. Cut, do not pad.

- Prose: 1,000 to 1,200 words, not counting diagrams and glossary definitions.
- Diagrams: 4 to 6.
- Glossary: 25 to 40 terms. One to three sentences each.
- Every sentence 25 words or fewer. Every paragraph one topic.

Measure before publishing. Strip tags and SVG, count words. If prose is over 1,200, cut until it is under.

## Say each thing once

This is the main failure mode. A concept gets its full explanation in exactly one section. Every later mention is one clause plus the clickable term. Before publishing, read the page once looking only for repeats. Merge or delete them.

Common repeats to watch for: the core guarantee restated in Summary, Foundation, and Guarantees. The "why it exists" argument restated in Summary and Plugging it in. A definition restated in prose that the glossary already carries.

## Section order

Use the template in `template.html` next to this file. Copy it, replace the `{{...}}` markers, fill in the sections. Keep this order and these ids.

1. `summary`: three or four sentences in a `.summary` callout. Then one sentence with the single idea to remember, in bold.
2. `foundation`: the one idea everything else builds on, with the first diagram. For Kafka it was the append-only log. For a database it may be the sorted key space. Find that idea before writing anything.
3. `blocks`: the named parts. Open with a `.summary` callout titled "Two words before anything else" that gives plain analogies for the two nouns the reader will meet most. Then one `h3` per part.
4. `flow`: one numbered list of what happens to one request or record, end to end.
5. `plug`: how a real system uses it. One before-and-after comparison diagram, then a numbered list of steps in the order teams actually do them, then one complete example system diagram.
6. `guarantees`: what it promises and what it does not. Use a table where the content is a matrix. Include a short failure-handling list.
7. `compare`: a table placing the subject next to tools the reader may confuse it with and next to its real alternatives. Name the category of each. Say "different job" plainly when it is.
8. `fit`: a two-column `.compare` grid, "Reach for it when" and "Think twice when". Then one sentence saying what the subject is not.
9. `glossary`: leave the template's index in place. The script fills it.

Skip a section only when the subject truly has nothing for it. Do not add sections unless the user asks. When the user asks for an added topic, add one section of 300 words or fewer with one diagram, and put it in the nav.

## Writing

- Plain words. Short sentences. Active voice. Name the actor.
- Give a physical analogy at first contact with an abstract noun. Shelves and workers. Channels and folders. Then drop the analogy.
- Numbers only when they change a decision. Put them in a table.
- Kickers (`.kicker`) are one or two words naming the section's role: Summary, Foundation, Integration, Guarantees, Orientation, Judgement.
- Numbered lists only for real sequences. Bulleted lists for parallel items.

## Clickable terms

Every word a newcomer might not know is a glossary term. Mark it in prose as `<button class="t" data-t="slug">word as it reads in the sentence</button>`. The button opens the definition panel. Rules:

- Mark the term at every mention, not just the first. The reader may land anywhere.
- Define the term in the `G` object in the script. Fields: `name` (display name), `def` (one to three plain sentences), `also` (two to four related slugs).
- Definitions must stand alone. A reader who opens one from the glossary index has no surrounding context.
- Cross-link generously in `also`. The Back button lets the reader retrace the chain.
- The glossary index at the bottom is generated from `G`. Every slug used in a `data-t` must exist in `G`.

## Diagrams

Inline SVG, hand-authored, using the template's classes. One claim per figure, stated in the `figcaption` and the `aria-label`.

- Draw the mechanism, not a box with the subject's name on it. Show the parts the explanation hinges on and nothing else.
- Label arrows with what moves or what happens.
- Use `.box` for plain parts, `.box-accent` and `.ln-acc` for the one element under discussion, `.box-solid` for a leader or primary, `.group-outline` for a cluster boundary, `.ln-dash` for replication or background flows.
- Keep text 10 to 13px in the drawn scale. Sentences go in the caption.
- The before-and-after diagram in `plug` shows the same system twice, split by a dashed line, with the one edge that changed in the accent color.
- Reuse the `arr` and `arrA` markers defined in the first SVG on the page. Define them only once.

## After publishing

- Answer follow-up questions in chat, briefly. Do not edit the page for a question.
- Edit the page only when the user asks for a change or an added topic.
- Republish to the same path so the URL is stable.
- The page is done at publish. Do not offer more sections.
