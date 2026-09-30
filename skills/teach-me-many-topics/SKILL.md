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

Either way, write every page into one directory, name each file `<slug>.html` after its manifest
slug, and set each manifest URL to that same `<slug>.html`. The index links its neighbours by
relative path.

**Published set.** The session offers the Artifact tool. Publish the whole set as **one** artifact:
the index is the page, and every `<slug>.html` goes in `files`. Each artifact has its own origin,
so pages published as separate artifacts cannot share browser storage, and the index would never
see their quiz scores.

**Local set.** The session offers no Artifact tool, or the user asks for files, HTML files, or pages
they can open in a browser. Tell the user to open the set through a local server, such as
`python3 -m http.server` in that directory. Some browsers give each `file://` page its own storage.

Progress lives in the reader's browser storage, one origin per set: the index's done marks, and each
page's quiz score, written by the page's Finish button. It is private to that browser, and no agent
can read it back.

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
- Its output path, `<directory>/<slug>.html`, and the instruction to write the file there and report
  the path. The subagent never publishes. The set publishes as one artifact.
- Its quiz key, `<manifest key>/<slug>`, to replace `{{QUIZ_KEY}}`. The index reads the score
  under that key.
- Whether to write a quiz. Pass the user's request through.
- A scratch directory of its own, such as `<scratchpad>/<slug>/`. Subagents that share one
  scratchpad overwrite each other's drafts.

Collect what each subagent reports, and put it in the manifest as that item's URL.

## Build the index

Write the manifest. The schema and its rules live in [references/manifest.md](references/manifest.md).

```sh
python3 /absolute/skill/scripts/build_index.py /absolute/manifest.json --out /absolute/index.html
```

The script rejects a duplicate slug, a missing URL, a missing page file, and an unreplaced marker.
Fix the manifest and run it again until it writes the file.

The script also prepares every local page in place. It adds the document head that files published
beside a page lack, and a link back to the index. The index opens pages in its own frame, because a
framed page and a new tab keep separate browser storage.

Write the index as `index.html` in the same directory as the pages.

For a published set, publish `index.html` with the Artifact tool and map every page into `files`,
`{"<slug>.html": "<directory>/<slug>.html"}`. The set needs no capabilities.

Report the index location and the page count.

## Change a set later

Keep the manifest. Add the new items and run the script again. For a published set, republish the
index to the same artifact, passing the new and changed pages in `files`. For a local set, overwrite
the same files. Stable slugs and a stable manifest key keep the saved progress.

Progress stays in the reader's browser, where no agent reaches it. To learn a user's scores, ask them.
