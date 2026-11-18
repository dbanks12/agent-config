---
name: pr-guide
description: Guide a reviewer through a pull request or a stack of them as one Artifact page, in five stages - definitions, a codebase diagram with the touched components, the change in concept with its data flow, a code walkthrough of the cruxes with the risky parts flagged, and a wrap-up. Use when the user asks for a PR guide, a guide or walkthrough of a PR, stack, branch or diff, or invokes /pr-guide. Not for the zoomable map (pr-viz) or for posting review findings (code-review).
---

# PR guide

Build one page that takes a reviewer from zero to ready to review. The reader knows the language and general engineering. Assume they never opened this part of the codebase.

The page is a **guide**: it teaches in a fixed order, and each stage uses only what the stages before it taught.

`/pr-guide [target] [--explain [stages|captions]] [--file]`

- `target`: a PR number or URL, `base...head`, a branch, or nothing for the uncommitted changes. A PR in a stack guides the whole stack, unless the user names one PR.
- `--explain`: add an explainer video to stages. See [Explainer videos](#explainer-videos). The user's words can ask for the same thing.
- `--file`: write the page as a file and do not publish it.

## 1. Read the change

1. Collect the diff. For a PR use `gh pr view` and `gh pr diff`. For a stack, find each PR's base and head, bottom first. When the `pr-viz` skill is installed, `~/.claude/skills/pr-viz/scripts/collect.py --repo <repo> <target>` does both and writes `diff.json` with each PR's head.
2. Read each PR description, then the diff of each source file. Skip tests, fixtures, snapshots, generated files and lockfiles for the walkthrough. Read the tests only to learn what is covered.
3. Read enough unchanged code around the change to explain each touched component: what it is for and who calls it.
4. Write down, before any HTML:
   - the **claim**: one sentence that the rest of the diff follows from
   - the **components**: 4 to 9 parts of the codebase, touched ones and the untouched neighbors a data flow needs
   - the **cruxes**: 2 to 5 places in the code where a reviewer's attention matters most
   - the **risks**: each place where a mistake costs funds, data, security, or users in production, and each claim you could not verify

Done when each crux and risk names a file and line range that you read.

## 2. Write the page

Copy `assets/template.html`, replace each `{{MARKER}}`, and fill the five sections. Keep their order and ids. The template carries the palette, both themes, the diagram frame and the code highlighting.

Open the page with an **introduction** in `{{LEDE}}`: two to four sentences that say what the guide covers and what it leaves out. When another guide or page covers the wider work, link it there.

Load `artifact-design` when the session offers it. This skill wins where they differ. Draw each diagram with the `excalidraw-skill` skill. See [Diagrams](#diagrams).

1. **`definitions`**: each term the later stages use that a newcomer may not know. The list starts collapsed, because each term also opens inline. Write them in the glossary, and the page fills this stage's list from it. See [Clickable terms](#clickable-terms).
2. **`codebase`**: one diagram of the codebase at the level where the change is visible. Draw touched components with `change="changed"` and neighbors with `change="context"`. Under it, one short entry for each component: what it is and what job it does. Describe the codebase as it is with the change merged. Leave how it changed to stage 3.
3. **`changes`**: the claim, then what the change does in concept, what a user or caller sees after it, and what stays the same. Draw the data flow or call path that the change adds or reroutes, as a before-and-after or one flow with `change` set on the new, changed and removed edges. Name the gate when the change is behind a flag or config. For a stack, add one table row for each PR in review order: number, what it does, and the components it touches.
4. **`walkthrough`**: one `<article class="stop">` for each crux, in the order a reviewer should read them. Each stop names its component from stage 2, shows one to three snippets, and says what to check. Flag each risk with a `.risk` callout beside the code it is about. After the cruxes, add one short stop, "The rest", that lists the remaining source changes in a sentence each, without code.
5. **`wrapup`**: the claim again in one sentence, a table of the risks with where each lives, the open questions, and what you did not verify. Add no new facts here.

Rules for each stage:

- A stage may have more diagrams when a picture is faster than prose. Give each diagram one claim, stated in its `figcaption`.
- Tie each stop and each risk back to a component of stage 2 with `<a class="comp" href="#c-<id>">`.
- Apply the [shared writing rules](../../instructions/AGENTS.md#all-writing).

### Diagrams

Draw each diagram with the `excalidraw-skill` skill. Follow its design rules and its code-change palette. Do not write SVG by hand.

1. Write one `place.py` scene file for each diagram, in a scratch directory. Use a box name that matches the component's `c-<id>`.
2. Draw, lint and render it:

   ```sh
   <skill dir>/scripts/diagram.py draw <scene.py>
   ```

   Fix each lint `FAIL`. View the PNG, critique it as the `excalidraw-skill` says, and draw again.
3. Put the SVG on the page. The template holds `{{CODEBASE_DIAGRAM}}`. For another diagram, add `<figure class="diagram"><div>{{A_MARKER}}</div><figcaption>its claim</figcaption></figure>`.

   ```sh
   <skill dir>/scripts/diagram.py embed <page.html> CODEBASE_DIAGRAM <scene.svg> --label "<the diagram's claim>"
   ```

The page shows each diagram on white paper, and inverts it in the dark theme. Color by the `change` palette, so both themes keep its meaning.

### Clickable terms

Each definition is written once, in the `glossary` JSON script near the end of the template. Stage 1 lists every entry, and a marked term anywhere on the page opens its definition in a side panel.

- An entry is `"slug": { "name": ..., "def": ..., "also": [...] }`. Order the entries as stage 1 shows them: domain terms first, then the names of types and functions.
- `def` is one to two sentences that stand alone, in the names the code uses. Start an abbreviation's `def` with its expansion. `name` and `def` may hold inline HTML, such as `<code>`.
- `also` names two to four related slugs. The panel's Back button retraces a chain of them.
- Give `link: { "url", "label" }` to an entry with one canonical place, such as a type's definition in the PR's files or a spec page.
- Mark a term in stages 2 to 5 as `<button class="t" data-t="slug">the words as they read</button>`. Wrap a code name whole: `<button class="t" data-t="savings-line"><code>SavingsLine</code></button>`.
- Mark the first mention in each component entry, each paragraph group of stage 3, each stop, and the wrap-up. A reader who lands on any stop can then open each term it uses.
- Leave terms unmarked inside headings, links, diagrams and code snippets.
- Use each term with its one meaning in every stage.

### Code snippets

Cut each snippet with the script. It reads the file from git, escapes it, and sets the language for highlighting.

```sh
<skill dir>/scripts/snippet.py --repo <repo> --rev <head sha> --file <path> --lines 59-64 \
  --title "A waiting move is pending, then delayed at 14 days" --url <PR or blob URL>
```

- Paste its output into the stop. Edit the title and add a note under it. Leave the code as cut.
- For a stack, pass the head of the PR that wrote the lines, and that PR's URL.
- Keep a snippet to 40 lines or fewer. Show the lines that carry the idea. Use `--mark 61-62` to mark the lines the note talks about.
- Add `--old` to show removed code from the base.
- The page loads highlight.js's common languages. For another language, such as Solidity, add its script from cdnjs after the main script, as the template's comment shows. A language that highlight.js lacks renders as plain text.

## 3. Check and deliver

1. Run `<skill dir>/scripts/check_page.py <page.html>`. It fails on a missing or misordered section, a leftover marker, a marked term or see-also slug with no glossary entry, a page whose later stages mark no term, a snippet with no language, over 40 lines, or from a test or fixture path, a stop with no component link, a `codebase` section with no diagram, and a walkthrough with no `.risk`. Fix what it names and run it again.
2. Read the page top to bottom once. Each term a stage uses must have a glossary entry and a marked mention. The checker's `note` lines name entries that no later stage links: link each, or delete it. Each component a stop names must be in the stage 2 diagram.
3. Publish the page with the Artifact tool and report the URL. With `--file`, or without the Artifact tool, write the file and report its absolute path. The page holds the change's code, so it stays private unless the user shares it.

When a change has no real risk, say so in a `.risk` callout in the wrap-up's place for it, and pass `--no-risk` to the checker.

## Explainer videos

Make them only when the user asks, with `--explain` or in words. `--explain` alone covers stages 2, 3 and 4. `--explain changes,walkthrough` names stages. `--explain captions` sends no text to a narration service.

1. Finish and check the page first.
2. For each stage, run one standalone job of the `explainer` skill, 30 seconds to 2 minutes long. Open it with the slug `pr-guide-<target>-<stage>` and the stage's source files. Script it from that stage's text and diagrams. Follow that skill's authorization and mode rules.
3. Put each video on the page:

   ```sh
   <skill dir>/scripts/embed_explainers.py <page.html> codebase=<work dir> changes=<work dir>
   ```

   It adds a "Watch the explainer" button under each stage's heading and prints the `files` map of narration audio for the Artifact tool.
4. Publish the same page path again with that `files` map.

## After delivering

Answer follow-up questions in chat. Edit the page only when the user asks for a change, or when the PR gets new commits and the user asks for a refresh. Republish to the same path.
