---
name: teach-me-many-topics
description: Teach several subjects as a set of HTML pages plus an index that tracks which ones you have read. Use when the user names several topics to learn, asks to break one large subject into a course or curriculum, or invokes /teach-me-many-topics. For one subject alone, use teach-me.
---

# Teach me many topics

Build one page per topic with [teach-me](../teach-me/SKILL.md), then one index page that links them and records progress.

Each page carries about 900 words, 4 to 6 diagrams, and one foundation idea.
That budget decides everything below. A topic too broad for one page teaches nothing.

## Where the set goes

Decide this first, because it sets every link in the index.

**Published set.** The session offers the Artifact tool. Each page gets a claude.ai URL, and the
manifest carries those URLs.

**Local set.** The session offers no Artifact tool, or the user asks for files, HTML files, or pages
they can open in a browser. Write every page into one directory, name each file `<slug>.html` after
its manifest slug, and set each manifest URL to that same `<slug>.html`. The index then links its
neighbours by relative path.

A local index saves progress in browser storage, on one device, and no agent can read it back.
A published index saves progress per viewer and survives across devices.

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
- Its output path. In a local set, that path is `<directory>/<slug>.html`.
- For a published set, the instruction to publish with the Artifact tool and report the URL.
  For a local set, the instruction to write the file and report the path.

Collect what each subagent reports, and put it in the manifest as that item's URL.

## Build the index

Write the manifest. The schema and its rules live in [references/manifest.md](references/manifest.md).

```sh
python3 /absolute/skill/scripts/build_index.py /absolute/manifest.json --out /absolute/index.html
```

The script rejects a duplicate slug, a missing URL, and an unreplaced marker.
Fix the manifest and run it again until it writes the file.

For a published set, publish the index with the Artifact tool and declare the capabilities that save
progress:

```
capabilities: {"db": {}, "user": {}}
```

The index then writes each viewer's progress to `data/users/<id>/progress`, private to that viewer.

For a local set, write the index as `index.html` in the same directory as the pages. It falls back
to browser storage on its own.

Report the index location and the page count.

## Change a set later

Keep the manifest. Add the new items and run the script again. For a published set, republish with
`url` set to the index's own URL. For a local set, overwrite the same file. Stable slugs keep the
saved progress either way.

To read a user's progress in a later session, call the Artifact tool with `action: "read_db"`,
`db_op: "get"`, collection `data/users/me`, and doc id `progress`. A local set keeps progress in the
browser, where no agent reaches it, so ask the user instead.
