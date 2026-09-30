---
name: teach-me
description: Teach the user one technical subject (a tool, system, protocol, or concept) as an HTML page with clickable glossary terms, simple system diagrams, and a fixed section order. Use when the user asks to be taught something, wants an explainer or primer page, says "explain X to me" for a page-sized answer, or invokes /teach-me <subject>. A word count in the request, such as "/teach-me 1500 words Redis", overrides the default prose budget. Not for short chat answers.
---

# Teach me

Build one HTML page that teaches a subject to a smart engineer who has never used it.
Follow this skill for structure, length, and mechanics.

## Where the page goes

The page is the same either way. Only the last step changes.

**Publish it** when the session offers the Artifact tool. Report the URL.

**Write a file** when the session offers no Artifact tool, or when the user asks for a file, an HTML
file, a local page, or a page they can open in a browser. Report the absolute path.

Load `artifact-design` and `artifact-diagramming` when the session offers them. They set design and
diagram quality, and this skill wins where they differ. Without them, follow `assets/template.html`,
which already carries the palette, both themes, and the diagram classes.

## Audience

- Assume no prior knowledge of the subject. Define even basic nouns. Do not assume the reader knows what a "topic" or a "range" is.
- Assume general engineering literacy. Do not explain what a server, a file, or a database is.
- The reader is preparing for design discussions. Favor the mental model over configuration detail.

## Length budget

The page is short. Cut, do not pad.

- Prose: about 900 words by default, never more than 1,000, not counting diagrams and glossary definitions. If the user names a word count, use theirs instead. Treat the named number as the target and allow 10 percent over.
- Diagrams: 4 to 6.
- Glossary: 25 to 40 terms. One to three sentences each.
- Quiz: none by default. When the user asks for one, 6 to 8 questions.
- Every sentence 25 words or fewer. Every paragraph one topic.

`scripts/check_page.py` measures every number above. Run it before you deliver. See [Check the draft](#check-the-draft).

## Say each thing once

This is the main failure mode. A concept gets its full explanation in exactly one section. Every later mention is one clause plus the clickable term. Before you deliver, read the page once looking only for repeats. Merge or delete them.

Common repeats to watch for: the core guarantee restated in Summary, Foundation, and Guarantees. The "why it exists" argument restated in Summary and Plugging it in. A definition restated in prose that the glossary already carries.

## Section order

Use the template in `assets/template.html` next to this file. Copy it, replace the `{{...}}` markers, fill in the sections. Keep this order and these ids.

1. `summary`: three or four sentences in a `.summary` callout. Then one sentence with the single idea to remember, in bold.
2. `foundation`: the one idea everything else builds on, with the first diagram. For Kafka it was the append-only log. For a database it may be the sorted key space. Find that idea before writing anything.
3. `blocks`: the named parts. Open with a `.summary` callout titled "Two words before anything else" that gives plain analogies for the two nouns the reader will meet most. Then one `h3` per part.
4. `flow`: one numbered list of what happens to one request or record, end to end.
5. `plug`: how a real system uses it. One before-and-after comparison diagram, then a numbered list of steps in the order teams actually do them, then one complete example system diagram.
6. `guarantees`: what it promises and what it does not. Use a table where the content is a matrix. Include a short failure-handling list.
7. `compare`: a table placing the subject next to tools the reader may confuse it with and next to its real alternatives. Name the category of each. Say "different job" plainly when it is.
8. `fit`: a two-column `.compare` grid, "Reach for it when" and "Think twice when". Then one sentence saying what the subject is not.
9. `glossary`: leave the template's index in place. The script fills it.
10. `quizpage`: the Quiz tab. Leave it in place. It stays hidden until the page has a quiz. See "Quiz" below.

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
- If the term is an abbreviation or acronym, start `def` with its expansion. Example: "Fee Payment Contract. A contract that pays a transaction's fee for the user."
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

## Quiz

Do not write a quiz unless the user asks for one. Leave the `Q` array empty. The template then hides the tab bar and the Quiz tab.

When the user asks for a quiz, in the first request or later, fill the `Q` array. The Learn and Quiz tabs then appear. Change nothing else on the page. Republish or rewrite to the same path.

- 6 to 8 questions. Each tests one core idea from the page, not a detail. If a reader gets them all right, they have the mental model.
- Mix types: mostly multiple choice (`t: "mc"`, four options, `a` is the zero-based index of the right one), plus one or two typed answers (`t: "text"`, `accept` lists lowercase answers and synonyms; a match is exact or substring after stripping punctuation).
- Every question has a `why`: one or two sentences that teach the point again, shown on both correct and incorrect.
- Wrong options must be plausible to a newcomer. No joke options.
- Include one question that places the subject against a neighbor it is often confused with.

The quiz mechanics are already in the template: tabs, per-question Check buttons, a running score, Reset, and Finish. Do not rewrite them.

### Quiz score storage

Finish saves `{score, total, finishedAt}` to the reader's `localStorage` under `teach-quiz:<QUIZ_KEY>`. The score stays in that browser, private to that reader, and no agent can read it back.

Replace `{{QUIZ_KEY}}` with the page slug. When a teach-me-many-topics brief names a key, such as `<set key>/<slug>`, use that key exactly: the set's index reads it to show the score.

Leave the marker's replacement in place on a page without a quiz.

## Check the draft

Run the checker on the written file before you publish or hand it over.

```sh
python3 /absolute/skill/scripts/check_page.py /absolute/page.html --words 900
```

Pass the user's word count to `--words` when they named one. The ceiling is 10 percent above it.

The checker reports the prose count, and it fails on an over-budget page, a wrong diagram or term count, a
quiz outside 6 to 8 questions, a `data-t` slug with no glossary entry, a dangling `also` slug, a missing section id, a
leftover `{{MARKER}}`, a sentence over 25 words, a duplicate arrow marker, and unbalanced tags.

Fix what it names and run it again. Deliver once it passes.

It counts prose only: no script, style, SVG, code block, table, navigation, panel, or footer text. A line it
prints as `note` is information, not a failure. Glossary entries never linked in prose are a note,
because the glossary index links them.

## After delivering

- Answer follow-up questions in chat, briefly. Do not edit the page for a question.
- Edit the page only when the user asks for a change, an added topic, or a quiz.
- Republish or rewrite to the same path, so the URL or the file location stays stable.
- The page is done once delivered. Do not offer more sections.
