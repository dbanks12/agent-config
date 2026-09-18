---
name: teach-me-many-topics
description: Teach several subjects as a set of published HTML pages plus an index that tracks which ones you have read. Use when the user names several topics to learn, asks to break one large subject into a course or curriculum, or invokes /teach-me-many-topics. For one subject alone, use teach-me.
---

# Teach me many topics

Build one page per topic with [teach-me](../teach-me/SKILL.md), then one index page that links them and records progress.

Each page carries about 900 words, 4 to 6 diagrams, and one foundation idea.
That budget decides everything below. A topic too broad for one page teaches nothing.

## Settle the topic list

The request arrives in one of two shapes.

**Several topics named.** Take them as given. Split any topic that fails the scope test below.

**One large subject.** Break it into topics yourself. Aim for 6 to 15.

Apply the scope test to every topic in either shape:

- One sentence states the topic's foundation idea, and everything else on the page follows from it.
- The topic needs no more than 6 diagrams to show its mechanism.
- Naming what the page excludes still leaves a whole lesson.

A topic that fails the test is a heading, not a page. Cut it along a tighter seam.
"Networking fundamentals" fails. "What the load balancer actually balances" passes.

Order the topics by dependency, not by importance. Put the page that others assume first.
Mark the groups a reader must finish as `core`.

Report the list and the order to the user before you build.

## Assign one idea to one page

Give each idea a single owner. Name the owner in every other page that touches it.
Two pages that both teach consensus spend two budgets on one lesson.

Write the exclusions into each brief. Exclusions keep a page inside its budget.

## Build the pages

Dispatch one subagent per topic with the Agent tool. Send them in one message so they run together.

Give each subagent:

- The instruction to call the Skill tool with `skill="teach-me"` and follow it exactly.
- The topic's foundation idea, in one sentence.
- What to cover, and what to exclude because a sibling page owns it.
- A distinct output path.
- The instruction to publish with the Artifact tool and report the URL.

Collect the URL each subagent reports.

## Build the index

Write the manifest. The schema and its rules live in [references/manifest.md](references/manifest.md).

```sh
python3 /absolute/skill/scripts/build_index.py /absolute/manifest.json --out /absolute/index.html
```

The script rejects a duplicate slug, a missing URL, and an unreplaced marker.
Fix the manifest and run it again until it writes the file.

Publish the index with the Artifact tool. Declare the capabilities that save progress:

```
capabilities: {"db": {}, "user": {}}
```

The index writes each viewer's progress to `data/users/<id>/progress`, private to that viewer.
Without those capabilities the page falls back to browser storage, which one device holds alone.

Report the index URL and the page count.

## Change a set later

Keep the manifest. Add the new items, run the script again, and republish with `url` set to the
index's own URL. Stable slugs keep the saved progress.

To read a user's progress in a later session, call the Artifact tool with `action: "read_db"`,
`db_op: "get"`, collection `data/users/me`, and doc id `progress`.
