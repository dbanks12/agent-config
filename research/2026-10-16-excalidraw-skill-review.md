# Excalidraw skill review: content quality and tool choice

Date: 2026-10-16.

Status: implemented in dbanks12/claude-authoring-tools#1. The implementation differs from Section 7 in four ways:

- A test with a headless browser tab on 2.1.2 showed that CLI-written arrows survive the tab. Bound arrows follow moved boxes, and unbound arrows keep their bend points. `layout.mjs` therefore emits native unbound arrows with ELK's routed points. `arrow_doctor.py` stays only for canvases already drawn with connector lines.
- A removed part is red and dashed, with no strike line. The dashed stroke is the second cue besides color.
- Style-system textures are applied after layout with `update`. The spec has no texture field.
- `render_figures.py` and `crop_figures.py` are unchanged, apart from the pinned package version.

## Answer

Keep Excalidraw. The tool does not cause the wordy, hard-to-read drawings. The skill causes them, for three reasons.

1. The skill teaches canvas mechanics only. It says nothing about what a diagram should claim, which diagram type fits a question, or how many words a diagram may hold.
2. The agent places every element by x/y coordinates. Research and practitioner reports agree that LLMs place graph nodes poorly, and errors grow with edge count.
3. The only quality check is visual hygiene: truncation, overlap, and crossings. Nothing checks whether the drawing makes its point.

draw.io would not fix any of these. It would cost more tokens per diagram, and its sketch style is less faithful to the Excalidraw look. The recommended path keeps the Excalidraw look and changes the pipeline:

- The agent writes a one-sentence claim and a small graph spec.
- A layout engine (ELK) places the nodes.
- A lint script enforces word and node budgets.
- A headless render feeds one critique pass against the claim.

D2 with `--sketch` and the newly open-source TALA layout is the best fallback if you do not want to maintain a layout bridge.

## How to read this report

- **Evidence** sections cite sources with links and dates. `[recent]` marks items from 2026-08-16 to 2026-10-16.
- **Opinion** paragraphs are labeled. They are my judgment, not a finding.
- Three research subagents gathered the web sources. I opened and confirmed four of the load-bearing ones myself: `coleam00/excalidraw-diagram-skill`, `cathrynlavery/diagram-design`, `BV-Venky/excalidraw-architect-mcp`, and D2 sketch mode. I also confirmed every local finding about this repo and the npm package. A few web items rest on search snippets only. They are marked "(snippet)".
- Reddit blocked the crawler. Forum evidence comes from Hacker News, GitHub issues, and the Cursor forum.

---

## 1. Current state of the skill (local evidence)

### Files and ownership

| Path | Role |
|---|---|
| `vendor/claude-authoring-tools/skills/excalidraw-skill/SKILL.md` | The skill. Linked to `~/.claude/skills/` and `~/.codex/skills/` through `links`. |
| `.../excalidraw-skill/references/cheatsheet.md` | CLI, MCP, and REST reference, plus a 5-line "design guide" (colors, sizes). |
| `.../excalidraw-skill/evals/evals.json` | Five evals. All test mechanics (CLI use, Mermaid import, Obsidian export). |
| `.../slide-deck/SKILL.md` and `references/style-system.md` | Deck rules, canvas conventions, and a two-axis color and texture system. |
| `.../slide-deck/assets/draw.py` | Python helper that writes diagrams as code. The caller passes coordinates. |
| `.../slide-deck/assets/arrow_doctor.py` | Replaces Excalidraw arrows with plain lines and re-routes them. |
| `.../slide-deck/assets/render_figures.py`, `crop_figures.py`, `trim.py` | Crop figures out of a browser screenshot. |
| `vendor/claude-authoring-tools/notes/diagram-preferences.md` | Your distilled preferences, with a list of "candidates to fold into SKILL.md". |

`vendor/claude-authoring-tools` is a git submodule (`dbanks12/claude-authoring-tools`). Skill changes land there first, then a submodule bump lands here.

### Findings

1. **The SKILL.md is the upstream skill from `mcp-excalidraw-server`, one version behind.** I diffed it against the skill bundled in npm `mcp-excalidraw-server@2.1.2` (published 2026-10-04). The only local change adds `roundness: {type: 3}` as the default. Everything else is upstream text from before v2.1.
2. **The skill has no content guidance.** It has 277 lines. About 30 cover layout spacing and anti-patterns. None cover the diagram's claim, its audience, the diagram type, or a word budget. The closest rule caps arrow labels at 12 characters.
3. **The quality checklist checks hygiene, not meaning.** Its seven checks are truncation, overlap, arrow crossing, arrow-label overlap, spacing, font size, and zone labels. A diagram can pass all seven and still teach nothing.
4. **The evals test mechanics only.** No eval asks for a diagram of a code change or a design choice, and no eval grades whether a reader learns something.
5. **The rules conflict across files.**
   - SKILL.md makes rounded corners the default. `slide-deck/SKILL.md` and `diagram-preferences.md` require square corners. `draw.py` defaults to rounded (`sharp=False`), so the demo diagram renders rounded.
   - `diagram-preferences.md` says "Dashed box = a hash of a thing". `style-system.md` says "Dashed stroke is ONLY for elided filler. Never for hashes".
   - SKILL.md teaches bound `arrow` elements. `slide-deck/SKILL.md` says "NEVER use excalidraw `arrow` elements".
6. **The upstream package fixed several problems that the local tooling works around.** The v2.1 to v2.1.2 changelog in the npm README says:
   - "Screenshots and image exports no longer need a browser tab." A new `render` command renders a `.excalidraw` file offline. I ran `render` on `examples/demo-deck/canvas/demo.excalidraw` and it produced a 2188×768 PNG with no server and no browser.
   - "Text and arrows no longer drift on each canvas sync. (#116)". This may remove the reason for `arrow_doctor.py`. It needs a test.
   - "Large exports no longer fail with `invalid order key`. (#115)". This may remove the reason for `draw.py`'s `reindex()`, which strips invalid fractional indices.
   - `screenshot` gained `--ids`, `--frame`, `--scale 1-4`, and `--padding`. These could replace most of `render_figures.py` and `crop_figures.py`.
7. **The demo diagram shows the layout problem.** The offline render of `demo.excalidraw` has a five-box main row and a side column that joins it with one long diagonal line. The side column hangs from the left edge, so the eye reads an "L", not a pipeline with an input branch. Hand-placed coordinates produced this.
8. **`teach-me` already has better content rules than the Excalidraw skill.** `skills/teach-me/SKILL.md` says "One claim per figure", "Draw the mechanism, not a box with the subject's name on it", "Label arrows with what moves or what happens", "Sentences go in the caption", and it defines a before-and-after pattern. The Excalidraw skill has none of these.

---

## 2. Best places to learn

Ranked by how directly each one answers "how should an agent draw a useful diagram about code".

1. **C4 model notation guide and review checklist** (Simon Brown). <https://c4model.com/diagrams/notation>, <https://c4model.com/diagrams/checklist>. Concrete, checkable rules: title, legend, a label on every arrow, one abstraction level.
2. **Agent diagram skills that set budgets.** `cathrynlavery/diagram-design` (<https://github.com/cathrynlavery/diagram-design>), `coleam00/excalidraw-diagram-skill` (<https://github.com/coleam00/excalidraw-diagram-skill>), and `tt-a1i/archify` (<https://github.com/tt-a1i/archify>). These solve the exact problem in this report.
3. **Official agent-tool references.** `jgraph/drawio-mcp` (<https://github.com/jgraph/drawio-mcp>), the official Excalidraw MCP cheat sheet in `excalidraw/excalidraw-mcp` `src/server.ts`, and the `yctimlin/mcp_excalidraw` README.
4. **Ilograph blog.** "7 Common Mistakes" (2020) and "7 More Common Mistakes" (2026-03-12) at <https://www.ilograph.com/blog/>.
5. **PR Lens guides on diagrams of code changes** (2026-08 and 2026-09) at <https://prlens.dev/guides/>. Note that PR Lens is a vendor.
6. **Diagram research.** Moody, "Physics of Notations" (2009). Purchase's graph aesthetics studies (1997, 2002). Yoghourdjian et al. on network scalability (2020). Mayer's multimedia principles.
7. **D2 blog and Mermaid releases.** These track the layout engines: TALA open source (2026-09-07) and Mermaid 12 with ELK as the default (2026-09-10).
8. **arXiv work on LLM diagrams.** R2ABench (2604.06683), DiagramEval (2510.25761), PlanarBench (2606.02010), and Imperfect Visual Verification (2606.15693).
9. **Hacker News threads on diagram tools.** These are the densest practitioner opinion that I could reach.

---

## 3. Evidence: what makes a diagram effective

### 3.1 Scope: one question per diagram

- C4 FAQ (date unknown): "Large diagrams are usually hard to interpret and comprehend because the cognitive load is too high. And if nobody understands the diagram, nobody is going to look at it." <https://c4model.com/faq>
- Ilograph, "7 Common Mistakes" (2020-01-14): do not mix abstraction levels, and keep each diagram on "one or two concerns at a time". <https://www.ilograph.com/blog/posts/diagram-mistakes/>
- Martin Fowler, "UML as Sketch" (2003-05-28): "The essence of sketching is selectivity." "comprehensiveness is the enemy of comprehensibility." <https://martinfowler.com/bliki/UmlAsSketch.html>
- `teach-me` in this repo: "One claim per figure, stated in the `figcaption`."

### 3.2 Size: node and word budgets

- Cowan (2001) revised Miller's 7±2 to "about four chunks" in working memory. <https://pubmed.ncbi.nlm.nih.gov/11515286/>
- Moody (2009), graphic economy: people tell apart about 6 values per visual variable, such as color or shape. This sets an upper limit on encodings. <https://ieeexplore.ieee.org/document/5353439>
- Yoghourdjian et al. (InfoVis 2020): readers struggle with paths in dense node-link diagrams above 50 nodes. That limit applies to analysis tasks. Explanatory diagrams sit far below it. <https://vcg.seas.harvard.edu/publications/20201001-scalability-of-network-visualisation-from-a-cognitive-load-perspective>
- `cathrynlavery/diagram-design` (I confirmed this): "≤7 nodes" simplified, "≤12" balanced, "≤24" faithful. "The accent color is reserved for the 1 or 2 things the reader should look at first. Target density: 4/10." "The highest-quality move is usually deletion." A write-up (pyshine.com, 2026-04-26) quotes per-type caps: "Max nodes: 9, Max arrows/transitions: 12", at most 5 lifelines in a sequence diagram.
- `[recent]` Archify guide, explainx.ai (2026-08-28): "Show 8–12 core components, one primary path, external dependencies, and trust boundaries. Put supporting detail in cards instead of adding more edges." <https://explainx.ai/blog/archify-agent-skill-architecture-diagrams-guide-2026>
- Official Excalidraw MCP cheat sheet (date unknown): minimum body font 16, never below 14, minimum shape 120×60. <https://github.com/excalidraw/excalidraw-mcp> (`src/server.ts`)
- DiagrammerGPT (2023) found that image models produce "redundant and crowded objects, including excessive unnecessary text descriptions". <https://arxiv.org/pdf/2310.12128>
- No source gives a research-backed word limit per label. The numeric word limits in Section 5 are my opinion.

### 3.3 Text: where words go

- Mayer, coherence principle: "People learn better when extraneous material is excluded rather than included." Spatial contiguity: put words next to the part they describe. Summary at <https://services.dartmouth.edu/TDClient/1806/Portal/KB/PrintArticle?ID=171655>
- C4 notation: "Every line should be labelled, the label being consistent with the direction and intent." Every element gets a short description.
- Ilograph: "An unlabeled arrow tells the viewer that two resources are somehow related but not precisely how."
- `coleam00/excalidraw-diagram-skill` (I confirmed this): "Every shape/group of shapes mirrors the concept it represents — fan-outs for one-to-many, timelines for sequences, convergence for aggregation." The research agent also reported an "isomorphism test": "If you removed all text, would the structure alone communicate the concept?"

### 3.4 Layout and the reader's mental map

- Purchase (GD 1997): "reducing the number of edge crosses is by far the most important aesthetic, while minimising the number of bends and maximising symmetry have a lesser effect." <https://research.monash.edu/en/publications/which-aesthetic-has-the-greatest-effect-on-human-understanding/>
- Huang, Eades, and Hong: when a crossing is unavoidable, a larger crossing angle reads better (snippet).
- NN/g, "Common Region" (2020-07-12): "Creating a clear boundary is a strong visual cue that can overpower other grouping principles such as proximity or similarity." <https://www.nngroup.com/articles/common-region/>
- Misue et al. (1995) define "preserving the mental map": when a diagram changes, keep existing nodes where they were.
- `[recent]` Taku blog on Archify (2026-09-13): the goal is "one obvious main path, short side branches". Its checks reject "an edge crossing an unrelated box, two routes sharing an ambiguous corridor, a label covering another line". <https://taku.ai/blog/skill-archify>
- jls42 (2026-01-11): keep the main data flow on one horizontal row, and put auxiliary services above or below it. <https://jls42.org/en/posts/deep-dive-skill-aws-diagram-claude-code-drawio-mcp>
- Flow direction: the evidence for left-to-right against top-to-bottom is weak and mixed (snippet of a 44-person BPM pilot).

### 3.5 Diagrams of code changes

- `[recent]` CodeAnt AI (2026-10-13): "A one-line null check or a typo correction doesn't require visualization." Use sequence diagrams for architectural refactors, cross-service APIs, and security changes. <https://codeant.ai/blogs/pr-diffs-vs-sequence-diagrams>
- `[recent]` PR Lens, "visualise a pull request" (2026-09-02):
  - A change diagram must show "added, changed and deleted ... without reading a caption".
  - It must also show "the parts of the system the change did not touch".
  - Encoding: "Green for new, amber for modified, red for gone, with removed components struck through."
  - Source: <https://prlens.dev/guides/visualize-a-pull-request-as-a-diagram>
- `[recent]` PR Lens, "explain a pull request" (2026-08-31): "Say in one sentence what the change does to the system." "Some things only exist in the lines: a regular expression, an off-by-one, a permission check." <https://prlens.dev/guides/explain-a-pull-request-without-the-diff>
- `[recent]` CodeRabbit changelog: an Architecture Impact before-and-after diagram gained security overlays (2026-08-21). An attack-surface map arrived (2026-09-04). Sequence diagrams appear only for PRs that change interactions. <https://docs.coderabbit.ai/changelog>, <https://docs.coderabbit.ai/pr-reviews/walkthroughs>
- `[recent]` aws-samples architecture-diagram MCP, issue #23 (2026-09-19, closed by PR #28): a "before / delta / after" view for design reviews and PRs. <https://github.com/aws-samples/sample-architecture-diagram-mcp-server/issues/23>
- Schneider et al. (2024): a data-flow diagram plus code raised security-analysis correctness by 41%. Links from diagram elements to code raised evidence correctness by 315%. <https://arxiv.org/abs/2401.04446>
- Wurzel Gonçalves et al. (2025): reviewers build context first, then inspect. <https://arxiv.org/abs/2503.21455>

### 3.6 Diagram type per question

| Question the reader has | Type | Support |
|---|---|---|
| Where does this system sit? | Context diagram (C4 level 1) | C4, arc42, Google design docs (Ubl, 2020-07-06) |
| What are the deployable parts? | Container diagram | C4. `[recent]` HighCircl (2026-09-26): context and container "are sufficient for most software development teams" |
| In what order do things happen across parts? | Sequence diagram | C4 dynamic diagrams. Ilograph's "conveyor belt syndrome" |
| Where does data go, and what does it cross? | Data-flow with trust boundaries | Schneider et al. 2024, Archify |
| What did this PR change? | Before/delta/after inside unchanged context | PR Lens, CodeRabbit, the aws-samples MCP |
| What states can this object be in? | State machine | No direct source. This is an extension of the C4 principle. |
| Which of two designs? | Same layout twice, or one layout with the differing edge highlighted | `teach-me` before-and-after rule, the `artifact-diagramming` guidance |

---

## 4. Evidence: how other agents generate diagrams

### 4.1 Structure from the LLM, geometry from an engine

Most tools that people report as working well separate the two jobs.

| Tool | LLM writes | Layout by | Source |
|---|---|---|---|
| draw.io official MCP | XML, CSV, or Mermaid | `postLayout: "elk"` or `routing: "libavoid"` | <https://github.com/jgraph/drawio-mcp> |
| Archify | Typed JSON IR | Deterministic renderer with 9 fail-closed checks | `[recent]` taku.ai (2026-09-13) |
| excalidraw-architect-mcp | `nodes` + `connections` | Sugiyama layout, obstacle-aware routing, Python roughjs port, SVG with no browser | <https://github.com/BV-Venky/excalidraw-architect-mcp> (I confirmed this; 159 stars) |
| Excalidraw text-to-diagram | Mermaid | Mermaid's engine, then conversion | Excalidraw parser docs |
| D2 with TALA | D2 text, optional pinned positions | TALA, ELK, or dagre | `[recent]` d2lang.com/blog (2026-09-07) |
| Agents365 drawio-skill | Graph | Graphviz | <https://github.com/Agents365-ai/drawio-skill> |
| Eraser DiagramGPT | Eraser DSL | Eraser engine | <https://www.eraser.io/diagramgpt> |
| Official Excalidraw MCP, yctimlin, coleam00 skill | Coordinates | The LLM | Each repo |

Supporting evidence:

- PlanarBench (2026-06-01): 91 model configurations on 199 planar graphs. Edge count correlates with failure (r = -0.85). <https://arxiv.org/abs/2606.02010>
- `[recent]` besthub.dev (2026-09-10), quoting the D2 founder: "LLMs are good at rough 2D placement but weak at simultaneous constraints." This is a secondary source.
- Classmethod (2026-03-01) used a coordinate-based Excalidraw MCP and got "diagonal vertical lines" in sequence diagrams and a CI/CD diagram "stretched horizontally". <https://dev.classmethod.jp/en/articles/excalidraw-mcp-claude-code/>
- `[recent]` Reladraw on Hacker News (2026-09-27) called draw.io "very time consuming (and inefficient for agents to manipulate)". <https://news.ycombinator.com/item?id=49858513>

### 4.2 Render, then check twice

- coleam00: a Playwright render loop lets the agent see overlapping text and misaligned arrows before it delivers.
- Archify: nine geometry checks, and delivery is "fail-closed".
- Imperfect Visual Verification (2026-04): even imperfect visual verifiers improve refinement. Feedback works when it names the exact defect and stays grounded in the original instruction. <https://arxiv.org/abs/2606.15693>
- DiagramEval (2025-10): judge a diagram as a graph (nodes and paths), not by pixel similarity. "CLIPScore may give generated diagrams relatively good scores even if element-wise logic differs substantially." <https://arxiv.org/html/2510.25761>

### 4.3 Grounding and stability

- R2ABench (2026-04-08): models "produce syntactically correct architecture diagrams but struggle to generate accurate relationships between components". <https://arxiv.org/html/2604.06683v1>
- jls42: "Only diagram what actually exists in the infrastructure code."
- tldraw-canvas-kit (Prateek Rai): "Ask twice, though, and you get two different layouts". The fix is stable ids and layout math that the skill owns. <https://dev.to/prateek11rai/same-prompt-same-diagram-teaching-agents-to-draw-on-a-local-canvas-1ib>
- Google Code Wiki (2025-11) and DeepWiki link each diagram section to source code.

### 4.4 Host renderers fail too

- Cursor forum (2026-05): "Lines/Arrows are barely visible", "Text labels are too small". <https://forum.cursor.com/t/improve-diagramming/159547>
- `[recent]` openai/codex #47720 (2026-09-24): the Codex desktop app renders Mermaid wrong after an upgrade. <https://github.com/openai/codex/issues/47720>
- Lesson: check the image that the reader will see. The headless renderer in `mcp-excalidraw-server` 2.1 produces the same output as the tab.

---

## 5. Rules for effective diagrams of code and designs

Each rule names its support. "Opinion" marks numbers or rules that I chose where the evidence gives no number.

### Before drawing

1. **Write a brief first.** It has three lines: the reader, the one question, and the one-sentence claim that the picture must prove. (PR Lens, `teach-me`, C4 titles.)
2. **Skip the diagram when a sentence or the diff says it faster.** Examples: a one-line fix, a list, a single box, a regex. (CodeAnt, PR Lens, diagram-design, `artifact-diagramming`.)
3. **Pick the type from the table in Section 3.6.** Use one abstraction level per diagram. (C4, Ilograph.)
4. **Read the code first and use names from the code.** Draw only what exists. (R2ABench, jls42, `diagram-preferences.md`.)

### Budgets

| Budget | Value | Basis |
|---|---|---|
| Nodes, default | 3–7 | Cowan's ~4 chunks plus grouping. diagram-design "simplified ≤7". Your notes say "3-8 boxes". |
| Nodes, hard cap | 12. Split above that. | diagram-design "balanced ≤12". Archify "8–12". |
| Groups (zones) | ≤ 4 | Cowan. Opinion. |
| Node label | ≤ 4 words, one line | Opinion. It extends C4's "short description" and Mayer's coherence principle. |
| Node subtitle (type, tech, or file) | ≤ 5 words, smaller font | C4 element type and technology. Opinion on the number. |
| Arrow label | verb-first, ≤ 3 words, such as `writes`, `polls 30s`, `emits Event` | C4, Ilograph, `artifact-diagramming`. Opinion on the number. |
| Free notes inside the drawing | ≤ 2, ≤ 12 words each, attached to an element | Mayer spatial contiguity. Your notes: "Delete orphaned floating notes". |
| Total words in the drawing | ≤ 40. Sentences go in the caption or prose. | Opinion. `teach-me`: "Sentences go in the caption". |
| Colors with meaning | ≤ 5, plus gray | Moody (~6 per visual variable). |
| Accent elements | 1–2 | diagram-design. `artifact-diagramming`. |
| Edge crossings | 0. If one is unavoidable, make it near 90°. | Purchase, Huang et al. |

### Layout

5. **Draw a spine.** Put the main path on one straight axis. Use left-to-right for request or data flow and top-to-bottom for layers. Put side branches above or below the spine, never across it. (Archify, jls42. The direction choice is opinion.)
6. **Make the shape match the idea.** Use a fan-out for one-to-many, convergence for aggregation, a row for a pipeline, a lane per actor for a protocol. (coleam00.)
7. **Draw a group with a zone border only when the group is real,** such as a process, trust boundary, or package. (NN/g, Ilograph.)
8. **Keep positions stable across a diagram set.** Context, then zoom-in, then before/after should reuse positions so the reader keeps one map. (Misue et al. Your notes: "Zoom-in diagrams must look visually reminiscent of the mini version".)
9. **Use a legend only when an encoding repeats.** Otherwise label the mark itself. (C4, `artifact-diagramming`.)

### Code changes

10. **Draw the change inside its unchanged context, in one layout.** Use green for added, amber for changed, red with strike-through for removed, and gray for untouched neighbors. Put the one-sentence summary above the drawing. (PR Lens, CodeRabbit, aws-samples.)
11. **Put a file path under each changed node in small text.** (Schneider et al. 2024 found large gains from links to code.)

---

## 6. Tool comparison

| Criterion | Excalidraw (current) | draw.io | D2 | Mermaid 12 |
|---|---|---|---|---|
| Hand-drawn look | Native. The look you like. | Sketch style (`sketch=1`, `rough=1`). Rough-styled shapes, but not the Excalifont look. | `--sketch` (I confirmed this). Close to Excalidraw. | `look: handDrawn` (snippet) |
| Auto-layout | None in core or in `mcp-excalidraw-server`. Possible through a bridge (elkjs) or `excalidraw-architect-mcp`. | ELK post-layout and libavoid routing in the official MCP. Auto-routed connectors (`[recent]` 2026-10-13). | TALA, ELK, and dagre, all free since 2026-09-07 `[recent]`. | ELK is the default since 12.0 (2026-09-10) `[recent]`. Labels can crowd. One PR pinned dagre (2026-10-11). |
| Tokens per simple diagram | ~500 (dev.to, 2025-10-21) | ~1200, the worst | Compact text | ~50, the best |
| Human edits afterwards | Best GUI. Live canvas. | Strong GUI | Text only | Text only |
| Git diff | JSON. Byte-stable since 2.0. | XML | Text | Text |
| Headless render | Yes, since 2.1 (I confirmed this) | Desktop CLI or MCP export | Go CLI | mmdc (Puppeteer) |
| Agent integration | yctimlin CLI and MCP (installed). Official Excalidraw MCP App. | Official jgraph MCP and Claude Code plugin | Community MCPs | Wide. GitHub renders it inline. |

### Recommendation

- **Keep Excalidraw.** Opinion, based on the evidence above. You like its look, and it has the best live editing. The headless renderer in 2.1 removed its biggest operational cost, the browser tab. Its one real gap is auto-layout, and a small bridge closes that gap.
- **Do not switch to draw.io.** Opinion. It solves layout, but it costs the most tokens, and its sketch look differs from Excalidraw's. It is the right choice only when diagrams must live in Confluence or a draw.io-centric team. Practitioners describe draw.io as inefficient for agents.
- **Fallback: D2 with sketch mode and TALA.** Opinion. Choose it if the Excalidraw layout bridge proves costly. You get layout, a hand-drawn look, and text diffs. You lose GUI editing.
- **Use Mermaid for diagrams inside GitHub PR descriptions only.** Opinion. GitHub renders it inline, and the rules in Section 5 still apply.

---

## 7. Proposed changes

Each change names its target file. Changes 1 to 6 address the stated problem. Changes 7 to 10 are support work. All edits to the skill land in the `claude-authoring-tools` submodule.

### Change 1. Add a "Brief before drawing" gate to the skill

Target: `excalidraw-skill/SKILL.md`, a new section before "Workflow: Drawing a New Diagram".

The agent writes the brief into the scene JSON as `customData` on a frame, or in chat. It does not start drawing until the brief exists.

```text
Reader:   reviewer of PR #412, knows the service, not this module
Question: what does the new retry queue change about write ordering?
Claim:    writes now pass through RetryQueue, so a failed write retries after newer writes.
Type:     before/after, one layout, delta colored
Skip?:    no. The ordering change is spatial, and the diff hides it across 3 files.
```

### Change 2. Add a type chooser and a "do not draw" rule

Target: `SKILL.md`. Copy the table in Section 3.6 and add one line: "If the claim fits in one sentence and has no spatial relationship, write the sentence and stop."

Example: for "Rename `getUser` to `fetchUser` across 14 files", the agent answers in one sentence and draws nothing.

### Change 3. Add budgets that a script enforces

Target: `SKILL.md`, a new "Budgets" section with the table in Section 5. Also add a new `scripts/lint_diagram.py` (see Change 5).

Before (a typical agent node today):

```json
{"id": "svc", "type": "rectangle", "text": "Order Service: validates incoming orders, persists them to Postgres, and publishes OrderCreated events to Kafka"}
```

After:

```json
{"id": "svc", "type": "rectangle", "text": "Order Service\nsrc/orders/service.ts"},
{"type": "arrow", "startElementId": "svc", "endElementId": "db", "text": "persists"},
{"type": "arrow", "startElementId": "svc", "endElementId": "kafka", "text": "emits OrderCreated"}
```

The sentence moves into the arrows. "Validates" either earns its own element or moves to the caption.

### Change 4. Let a layout engine place nodes

Target: a new `excalidraw-skill/scripts/layout.mjs`. It takes a graph spec on stdin and prints Excalidraw elements for `mcp-excalidraw-server add`. `draw.py` gains a `D.auto(spec)` helper that calls it. Coordinates become a manual override, not the default.

Spec that the agent writes:

```json
{
  "direction": "RIGHT",
  "nodes": [
    {"id": "api", "label": "API handler", "sub": "src/api/orders.ts", "fam": "gray"},
    {"id": "q", "label": "RetryQueue", "sub": "src/queue/retry.ts", "fam": "green", "change": "added"},
    {"id": "db", "label": "Postgres", "fam": "gray"}
  ],
  "edges": [
    {"from": "api", "to": "q", "label": "enqueues", "change": "added"},
    {"from": "q", "to": "db", "label": "writes", "change": "added"},
    {"from": "api", "to": "db", "label": "writes", "change": "removed"}
  ],
  "groups": [{"id": "svc", "label": "orders service", "members": ["api", "q"]}]
}
```

The script does four things:

1. It measures labels with the font-width rule already in `draw.py` (`tw`).
2. It runs elkjs `layered` with orthogonal edge routing.
3. It maps nodes to rectangles with the style-system families.
4. It maps routed edges to the connector lines that `arrow_doctor` already uses, or to bound arrows if Change 8 shows they are now stable.

Alternative: first evaluate `BV-Venky/excalidraw-architect-mcp` on two real diagrams. It already ships Sugiyama layout, obstacle-aware routing, and roughjs SVG. Adopt it only if its output matches your style system.

### Change 5. Add a lint script that fails closed

Target: a new `excalidraw-skill/scripts/lint_diagram.py`. It reads a `.excalidraw` file or `export` output. It exits non-zero on any violation.

Checks: node count, words per label, total words, arrow label length, accent count, distinct colors, edge crossings, edges through unrelated boxes, text outside its container, orphan text, and unlabeled arrows (a warning only).

Example output:

```text
FAIL  nodes=14 (max 12). Split the diagram.
FAIL  svc: label has 17 words (max 4). Move the detail to arrows or the caption.
FAIL  crossings=2: api->db crosses q->cache.
WARN  arrow q->db has no label.
PASS  colors=4, accents=1
```

The skill then requires this order: lint passes, then render, then critique.

### Change 6. Replace the hygiene checklist with a critique against the brief

Target: the "Quality Checklist" in `SKILL.md`. Keep the hygiene items. Add three content questions that the agent answers in writing after it views the headless render:

1. **Squint test.** What is the first thing the eye lands on? Is it the claim's subject?
2. **Remove test.** Name one node, arrow, or word that can go. Remove it, or say why it stays.
3. **Claim test.** Restate the claim from the picture alone, without the brief. Does it match?

Example critique:

```text
Squint: eye lands on the large "orders service" zone, not RetryQueue. Fix: drop zone fill, accent RetryQueue.
Remove: "Kafka" node is not part of the claim. Removed.
Claim from picture: "API now writes through RetryQueue. The direct write is gone." Matches.
```

### Change 7. Add a code-change preset

Target: `SKILL.md` and `style-system.md`. Add a "Code change" kind on top of the hue families:

| Change | Stroke | Fill | Extra |
|---|---|---|---|
| Added | green `#2f9e44` | `#d3f9d8` | none |
| Changed | amber `#f08c00` | `#fff9db` | none |
| Removed | red `#e03131` | none | dashed stroke plus a strike line |
| Untouched context | gray `#868e96` | none | thin stroke |

Example: Change 4's spec renders the old `api → db` edge as a red dashed line with a strike, and the new path through `RetryQueue` in green. The summary sentence goes above the figure.

Conflict to resolve: the style system already uses green for deposits and red for nullifiers. Code-change diagrams should use only the change palette and gray. Do not mix them with domain hues.

### Change 8. Upgrade the package and retest the workarounds

Target: `SKILL.md`, `cheatsheet.md`, `slide-deck/SKILL.md`, and the `slide-deck/assets/*.py` scripts.

1. Pin `mcp-excalidraw-server@2.1.2` in every `CLI = [...]` list instead of an unpinned `npx -y`.
2. Re-run `npx -y mcp-excalidraw-server@2.1.2 install-skill`, then reapply the local edits as a separate layer (see Change 10).
3. Replace browser-tab steps with headless `screenshot --scale 2 --ids ...` and offline `render`.
4. Test whether #116 and #115 remove the need for `arrow_doctor.py` and `reindex()`. Draw five bound arrows, move a box, sync, and export twice. Keep the workaround only if the geometry still drifts.
5. Try `screenshot --frame <id> --scale 3` per figure in place of `render_figures.py` and `crop_figures.py`.

Example of the simpler crop step:

```bash
npx -y mcp-excalidraw-server@2.1.2 render canvas/deck.excalidraw --frame fig-flow --scale 3 --out figures/fig-flow.png
```

### Change 9. Replace the mechanics evals with content evals

Target: `excalidraw-skill/evals/evals.json`. Keep one mechanics eval. Add graded content evals, for example:

```json
{
  "id": 10,
  "prompt": "Here is a diff that adds a retry queue in front of database writes. Draw a diagram for the PR description.",
  "expected_output": "One before/after diagram in one layout. 3-7 nodes. Added path green, removed edge red and struck. Every arrow labeled with a verb. No node label over 4 words. Lint passes. A one-sentence claim above the figure mentions write ordering."
}
```

Also add a negative eval: "Draw a diagram for a PR that renames a function". The expected output is no diagram and one sentence.

### Change 10. Separate upstream mechanics from your content rules

Target: the `excalidraw-skill/` layout.

- Keep the upstream SKILL text in `references/mechanics.md`, refreshed by `install-skill`.
- Make `SKILL.md` short and content-first: brief, type, budgets, layout pipeline, lint, critique, and a link to the mechanics reference.
- Move the content rules from `diagram-preferences.md` into `SKILL.md`, or into `references/style-system.md` for the domain-specific ones.
- Resolve the three conflicts from Section 1 in one place:
  - Corners: square or rounded, decided per set.
  - Dashed strokes: elided filler only, or hashes too.
  - Arrows against connector lines: decided by the Change 8 test.

Example `SKILL.md` outline after the change:

```text
1. Decide whether to draw (type table, skip rule)
2. Write the brief
3. Write the graph spec -> scripts/layout.mjs -> canvas
4. scripts/lint_diagram.py (must pass)
5. Headless render -> critique (squint, remove, claim)
6. Export and crop
Reference: mechanics.md (CLI, MCP, REST), style-system.md
```

---

## 8. Open questions for you

1. **Square or rounded corners.** The files disagree. Which is the default for new canvases?
2. **Dashed strokes.** Do they mean hash (`diagram-preferences.md`) or elided filler (`style-system.md`)?
3. **Layout bridge.** Should the bridge be a script we own (elkjs, about 150 lines), or `excalidraw-architect-mcp` after a trial?
4. **Shared rules.** Should the content rules in Section 5 also become a shared reference for `teach-me` and `slide-deck`? This is a scope expansion, so it is listed here and not proposed above.
5. **Word budget.** Is ≤ 40 words per drawing too tight for your protocol diagrams, which carry field lists?

## 9. Verification plan for the changes

- Build Changes 4 and 5 first. Redraw three existing diagrams: the demo flow, one SIPA or oxide figure, and one PR change. Compare word count, crossings, and your own read time before and after.
- Run the new evals with the skill and without it, using the `skill-creator` eval tooling.
- Test the Change 8 workarounds against 2.1.2 before you delete any script.

## Sources

Dates are publication dates where found. `[recent]` = 2026-08-16 to 2026-10-16. "(snippet)" = seen only in search results.

Local:
- npm `mcp-excalidraw-server@2.1.2` README and bundled skill, published 2026-10-04. I read them from the package tarball.

Recent:
- `[recent]` CodeAnt AI, "When to Use PR Diffs or Sequence Diagrams in Reviews", 2026-10-13. <https://codeant.ai/blogs/pr-diffs-vs-sequence-diagrams>
- `[recent]` draw.io, "Connectors now route automatically", 2026-10-13. <https://www.drawio.com/blog/connector-updates/>
- `[recent]` Mermaid 12.0.0 release, 2026-09-10. <https://github.com/mermaid-js/mermaid/releases>
- `[recent]` randalmurphal/agent-overflow PR #31, 2026-10-11. <https://github.com/randalmurphal/agent-overflow/pull/31>
- `[recent]` TechCrunch, "ChatGPT is getting a lot more visual", 2026-10-07. <https://techcrunch.com/2026/10/07/chatgpt-is-getting-a-lot-more-visual-with-the-launch-of-a-new-interface/>
- `[recent]` Jace Benson, "AI Agent Patterns, as Mermaid Diagrams", 2026-10-03. <https://jace.pro/blog/ai-agent-patterns-as-mermaid-diagrams>
- `[recent]` tldraw, "Introducing tldraw for ChatGPT and Codex", 2026-09-29. <https://tldraw.dev/blog/introducing-tldraw-for-chatgpt-and-codex>
- `[recent]` Ken Ashe, "Drawgent puts a coding agent on an Excalidraw canvas", 2026-09-27. <https://kenashe.ai/blog/2026-09-27-drawgent-puts-a-coding-agent-on-an-excalidraw-canvas-what-a-visual-work-surface>
- `[recent]` Show HN: Reladraw, 2026-09-27. <https://news.ycombinator.com/item?id=49858513>
- `[recent]` HighCircl, "Software architecture diagrams", 2026-09-26. <https://www.highcircl.com/en/blog/software-architecture-diagram>
- `[recent]` openai/codex issue #47720, 2026-09-24. <https://github.com/openai/codex/issues/47720>
- `[recent]` aws-samples architecture-diagram MCP issue #23, 2026-09-19. <https://github.com/aws-samples/sample-architecture-diagram-mcp-server/issues/23>
- `[recent]` bicarait.com, "Inside tt-a1i/archify", 2026-09-17. <https://bicarait.com/posts/cool-products-2026-09-17-archify-architecture-visualizer>
- `[recent]` Taku, "Archify: Architecture Diagrams Your Agent Can Verify", 2026-09-13. <https://taku.ai/blog/skill-archify>
- `[recent]` besthub.dev, "D2 goes non-profit, open-sources TALA", 2026-09-10 (secondary). <https://www.besthub.dev/articles/d2-goes-non-profit-open-sources-tala-commits-to-ai-only-development-0880810f9226>
- `[recent]` El Solitario, "TALA Open Source", 2026-09-08. <https://elsolitario.org/en/2026/09/08/tala-d2-autolayout-algorithm-open-source/>
- `[recent]` D2 blog, "TALA is open-source" 2026-09-07 and "D2 is non-profit" 2026-09-05. <https://d2lang.com/blog/>
- `[recent]` Hacker News, "TALA Is Open-Source", about 2026-09-07. <https://news.ycombinator.com/item?id=49604150>
- `[recent]` CodeRabbit changelog, 2026-08-21 and 2026-09-04 entries. <https://docs.coderabbit.ai/changelog>
- `[recent]` Mermaid Chart, "Mermaid Flow Is in Public Beta", 2026-09-03. <https://mermaid.ai/blog/posts/mermaid-flow-is-in-public-beta-heres-what-it-does-today>
- `[recent]` PR Lens, "How to visualise a pull request as a diagram", 2026-09-02. <https://prlens.dev/guides/visualize-a-pull-request-as-a-diagram>
- `[recent]` PR Lens, "How to explain a pull request without walking someone through the diff", 2026-08-31. <https://prlens.dev/guides/explain-a-pull-request-without-the-diff>
- `[recent]` explainx.ai, "Archify: Typed IR, Not Mermaid", 2026-08-28. <https://explainx.ai/blog/archify-agent-skill-architecture-diagrams-guide-2026>
- `[recent]` draw.io, "Advanced layout shapes and layout containers", 2026-08-18. <https://www.drawio.com/blog/layout-shapes/>
- `[recent]` Excalidraw+ changelog, August and September 2026 entries. <https://plus.excalidraw.com/changelog>

Older:
- explainx.ai, "Diagram Design Skill: 27 Editorial Types", 2026-08-13. <https://explainx.ai/blog/diagram-design-claude-code-skill-cathryn-lavery-august-2026>
- draw.io, "Updated Generate tool", 2026-08-04. <https://www.drawio.com/blog/updated-generate/>
- Simon Willison, "Mermaid to ASCII art", 2026-07-16. <https://simonwillison.net/2026/Jul/16/mermaid-ascii/>
- DevelopersIO, "SVG vs Mermaid vs Excalidraw", 2026-07-11. <https://dev.classmethod.jp/en/articles/build-svg-diagram-skill-for-claude-code/>
- draw.io, "Editable Mermaid diagrams", 2026-07-03, and "Better automatic layouts with ELK", 2026-06-26. <https://www.drawio.com/blog/>
- PlanarBench, arXiv 2606.02010, 2026-06-01. <https://arxiv.org/abs/2606.02010>
- Cursor forum, "Improve diagramming", 2026-05-01. <https://forum.cursor.com/t/improve-diagramming/159547>
- Imperfect Visual Verification, arXiv 2606.15693, submitted 2026-04-09. <https://arxiv.org/abs/2606.15693>
- R2ABench, arXiv 2604.06683, 2026-04-08. <https://arxiv.org/html/2604.06683v1>
- pyshine.com on diagram-design, 2026-04-26. <https://pyshine.com/Diagram-Design-Editorial-Diagram-Types-Claude-Code/>
- LLM architecture view generation, arXiv 2603.21178, 2026-03-22. <https://arxiv.org/abs/2603.21178>
- Ilograph, "7 More Common Mistakes", 2026-03-12. <https://ilograph.com/blog/posts/more-common-diagram-mistakes>
- Classmethod, "Excalidraw MCP with Claude Code", 2026-03-01. <https://dev.classmethod.jp/en/articles/excalidraw-mcp-claude-code/>
- jls42, "Generating AWS diagrams with Draw.io MCP", 2026-01-11. <https://jls42.org/en/posts/deep-dive-skill-aws-diagram-claude-code-drawio-mcp>
- dev.to, "Diagramming tools by token efficiency", 2025-10-21. <https://dev.to/akari_iku/analyzing-the-best-diagramming-tools-for-the-llm-age-based-on-token-efficiency-5891>
- DiagramEval, arXiv 2510.25761, 2025-10. <https://arxiv.org/html/2510.25761>
- Wurzel Gonçalves et al., code review comprehension, arXiv 2503.21455, 2025-03-27. <https://arxiv.org/abs/2503.21455>
- Schneider et al., data-flow diagrams and security analysis, arXiv 2401.04446, 2024-01-09. <https://arxiv.org/abs/2401.04446>
- Ilograph, "Diagrams AI Can, and Cannot, Generate", 2024-11-12. <https://ilograph.com/blog/posts/diagrams-ai-can-and-cannot-generate>
- DiagrammerGPT, 2023. <https://arxiv.org/pdf/2310.12128>
- Yoghourdjian et al., InfoVis 2020. <https://vcg.seas.harvard.edu/publications/20201001-scalability-of-network-visualisation-from-a-cognitive-load-perspective>
- NN/g, "Common Region", 2020-07-12. <https://www.nngroup.com/articles/common-region/>
- Malte Ubl, "Design Docs at Google", 2020-07-06. <https://www.industrialempathy.com/posts/design-docs-at-google/>
- Ilograph, "7 Common Mistakes", 2020-01-14. <https://www.ilograph.com/blog/posts/diagram-mistakes/>
- Moody, "The Physics of Notations", IEEE TSE, 2009. <https://ieeexplore.ieee.org/document/5353439>
- Fowler, "UML as Sketch", 2003-05-28. <https://martinfowler.com/bliki/UmlAsSketch.html>
- Purchase, Allder, and Carrington, JGAA, 2002. <https://jgaa.info/index.php/jgaa/article/view/paper54>
- Cowan, "The magical number 4", 2001. <https://pubmed.ncbi.nlm.nih.gov/11515286/>
- Purchase, GD 1997. <https://research.monash.edu/en/publications/which-aesthetic-has-the-greatest-effect-on-human-understanding/>
- Misue et al., "Layout adjustment and the mental map", 1995 (snippet).

Undated:
- C4 notation, checklist, FAQ, and dynamic diagrams. <https://c4model.com/>
- arc42 section 3. <https://docs.arc42.org/section-3/>
- `jgraph/drawio-mcp`. <https://github.com/jgraph/drawio-mcp>
- `excalidraw/excalidraw-mcp`. <https://github.com/excalidraw/excalidraw-mcp>
- `yctimlin/mcp_excalidraw`. <https://github.com/yctimlin/mcp_excalidraw>
- `coleam00/excalidraw-diagram-skill`. <https://github.com/coleam00/excalidraw-diagram-skill>
- `cathrynlavery/diagram-design`. <https://github.com/cathrynlavery/diagram-design>
- `BV-Venky/excalidraw-architect-mcp`. <https://github.com/BV-Venky/excalidraw-architect-mcp>
- `tt-a1i/archify`. <https://github.com/tt-a1i/archify>
- `Agents365-ai/drawio-skill`. <https://github.com/Agents365-ai/drawio-skill>
- Excalidraw element skeleton and mermaid-to-excalidraw docs. <https://docs.excalidraw.com/>
- D2 sketch mode. <https://d2lang.com/tour/sketch/>
- draw.io rough style. <https://www.drawio.com/docs/manual/styles/rough-style/>
- Structurizr AI. <https://docs.structurizr.com/ai>
- CodeRabbit walkthroughs. <https://docs.coderabbit.ai/pr-reviews/walkthroughs>
- DeepWiki docs. <https://docs.devin.ai/work-with-devin/deepwiki>
