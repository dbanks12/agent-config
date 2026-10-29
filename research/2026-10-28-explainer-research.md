# Instructional video and explanation research, applied to the explainer and Excalidraw skills

Date: 2026-10-28. Research window: foundational studies from 1999 on, with emphasis on 2022–2026 work. No saved research was reused, except the 2026-10-16 Excalidraw review for local context.

Four research subagents gathered the sources. Each appendix keeps its own verification labels (full text, abstract, snippet, vendor). I read all four reports and compared every recommendation against the current `skills/explainer/SKILL.md`, `player.js`, `scripts/qa.cjs`, and `excalidraw-skill/SKILL.md`. I did not re-open every cited source myself. Treat snippet-labeled claims as leads, not findings.

## Answer

The skills already follow the strongest evidence. Narration drives each reveal on the word that names it. Scenes hold one idea each. The context opening works as pre-training. A cross-vendor review checks the facts. The pictures label in place and animate the mechanism, never decoration.

The gap is the **script's shape**, not the pipeline. Both the learning research and the practitioners say that a clear, fluent, correct explanation can still leave viewers confident in the wrong model. Four cheap script rules address it:

1. Open with a concrete question, and answer that exact question at the end.
2. Walk one real instance with real values before the general rule.
3. Name the tempting wrong model and show why it fails.
4. End with a "predict what happens if" question that the viewer answers alone.

The next tier is smaller: treat the audio-tag count as a ceiling, add short silences at scene boundaries, carry recurring parts from scene to scene in the Excalidraw look, and gate the Excalidraw self-critique so a revision never makes lint worse.

Several popular ideas lack support and should stay out: a drawing hand, music, interpolated quizzes, more VLM critique rounds, and a slower voice.

## Areas of agreement

### Correctness and the illusion of understanding

- Fluent delivery raises confidence more than learning (Carpenter et al. 2013, 2016).
- A fluent explainer built on misconceptions gave viewers equal confidence and more wrong ideas (Kulgemeyer & Wittwer 2022, partial η² = 0.48).
- Muller's 2008 physics study found that a clear, correct explanation left misconceptions intact and raised confidence in them. Refutation or dialogue videos gave d ≈ 0.8.
- Matuschak, Sanderson, and Muller agree as practitioners that watching alone gives limited understanding.
- A demanding "explain why" prompt reduced the illusion of understanding (Hörnlein & Kulgemeyer 2026, d = 0.69). Generative prompts after a segment helped transfer (Fiorella 2020).

### Concrete before abstract, and a question as the hook

- Six practitioners (Sanderson, Case, Victor, Evans, Patel, Pinker) say to show a concrete instance before the abstraction.
- Seven or more practitioners say to pose a real question early and answer it at the end. A hook that is never paid off breaks trust.
- Practitioners link scenes by cause ("but", "so", "therefore") instead of sequence ("and then"). Case, Evans, and Olson (ABT) agree.

### Sync, signaling, and labels

- Temporal contiguity (d ≈ 0.78) and spatial contiguity (g ≈ 0.63) are among the largest effects in the Noetel 2022 meta-review.
- Cues help only when they are synced in space and time (Boucheix & Lowe 2010). Agent-made videos score worst on narration–visual sync (VideoAgent 2025).
- Labels belong on the diagram, not in a legend. Use a key only for notation, such as a color code.

### Animation that carries content

- Animation beats static pictures only slightly overall (g ≈ 0.23). It pays off when the change itself is the content (g ≈ 0.65 for complex change, Ploetzner 2020–2021).
- Representational motion helps (d ≈ 0.40). Decorative motion does nothing (≈ 0).
- People think of processes as discrete steps (Tversky, Morrison & Bétrancourt 2002). Build in steps that hold, and end each scene on a complete diagram.
- Keep earlier states visible, dimmed, instead of erasing them. This reduces the transient-information load (Ng et al. 2013, Wong et al. 2012).
- Seductive details hurt most in short lessons and for novices (Sundararajan & Adesope 2020).

### Narration and voice

- Modern neural TTS matches human voices on learning (Craig & Schroeder 2017, 2019; Netland et al. 2025, N = 447). Voice quality affects trust, not learning (Chiou et al. 2020).
- Conversational "you" and "we" has the strongest meta-analytic support in this set: transfer d = 0.54, retention d = 0.30 (Ginns, Martin & Marsh 2013).
- A warm baseline beats peaks. Positive affect helps (Lawson & Mayer 2021). An enthusiastic synthetic voice did not raise learning (Liew et al. 2022). A "cute" synthetic voice hurt learning.
- ElevenLabs' own v4 guidance says to use one tag per clause, and only where delivery shifts. v4 has no SSML break.
- Segmenting helps in system-paced media (Rey et al. 2019). Learners rarely press pause on their own (Hasler 2007, Biard 2018).
- Learners tolerate 1.5–2x playback (Murphy et al. 2022). Energy, not speed, explains Guo 2014's engagement finding.

### Agent-made explainers and diagrams (2025–2026)

- Code2Video, TheoremExplainAgent, OmniManim, and PhysicsSolutionAgent report the same failures: overlap, overflow, leftover elements, and occlusion during a transition.
- Grid anchors and numeric geometry checks gave the large gains. One VLM critique pass moved layout from 3.64 to 3.66.
- VLM critics sometimes made diagrams worse. VLM–human agreement on layout was only ρ ≈ 0.42.
- Removing the planner roughly halved Code2Video's scores. Planning before drawing is the main lever.

## Disagreements and tradeoffs

- **Effect sizes.** Mayer's own medians (d ≈ 0.7–0.8) exceed independent meta-analyses (modality d ≈ 0.25, overall g ≈ 0.37). Treat each principle as a moderate effect.
- **Captions.** The redundancy principle says verbatim on-screen text hurts. Adesope & Nesbit 2012 found that spoken plus written text beats spoken alone for novices and for system-paced material. Key-term labels beat verbatim text. Accessibility (WCAG 1.2.2) requires captions anyway. The evidence supports a caption toggle. It does not settle the default.
- **Draw-on animation.** Fiorella et al. 2019 found that hand-free dynamic drawing beat static drawing (d = .54). Fiorella & Mayer 2016 found no reliable difference (snippet only). Türkay 2022 found that whiteboard animation did not beat audio alone. Our element-by-element draw-on is plausible but unproven by itself. Its value comes from sync and signaling.
- **Signaling for experts.** Richter et al. 2016 found that the cue benefit vanishes for high prior knowledge. Schneider et al. 2018 found it consistent.
- **Personalization.** Almeida et al. 2024 found a reversal on transfer, possibly for aversive content.
- **Quizzes and pre-questions.** Szpunar 2013 reports large effects. A 2022 replication (N = 195) found almost none. Pre-question benefits stay specific to the questioned items (general g = 0.04).
- **Engagement versus understanding.** Comeau and Sanderson put enjoyment first. Matuschak and Muller say enjoyment does not produce understanding. The two fit: engagement is necessary, not sufficient.
- **Script first or visuals first.** Kurzgesagt and Tom Scott write the script first. Sanderson lays out animations first. TTS timing forces our pipeline to be script-first. A sketch of each scene's picture before the script is final keeps the picture as the prompt.
- **Staging.** Heer & Robertson 2007 found that simple staging helps but aggressive one-property-at-a-time staging was slower and disliked. "One thing at a time" means one conceptual change.
- **"At most 7 boxes".** No verified source sets 7. Miller's 7±2 is memory span. Cowan 2001 puts working memory near 4 chunks (not verified here). Treat 7 as a heuristic.
- **AI disclosure.** Labels cost engagement on social platforms but not in ads. No study covers educational explainers.

## What to change in our skills

The evidence column names the support. "Already" means the skill does it today.

### Explainer skill, step 1 (script)

| Change | Evidence | Cost | Status |
|---|---|---|---|
| Open with a concrete question about the mechanism in the first ~20 s. Answer that question in the last scene. | 7+ practitioners | one rule | new |
| Put one real instance, with real names and values, before the general rule. The context scene can be that instance. | 6 practitioners; pre-training | one rule | new |
| When a tempting wrong model exists, give it a scene: say it, then show why it fails. | Muller 2008 d ≈ 0.8; Kulgemeyer 2022 | one rule | new |
| End on one "predict what happens if" or "why" question, with a beat of silence before the answer or the end. | Hörnlein & Kulgemeyer 2026 d = 0.69; Fiorella 2020 | one rule | new |
| Join scenes with "but" or "so", not "and then". | Case, Evans, Olson | one rule | new |
| Speak to the viewer as "you", except for bad outcomes. | Ginns 2013 d = 0.54 | one rule | partly (no rule) |
| Say each simplification aloud in one clause. | Kurzgesagt, Evans, Pinker | one rule | new |
| One idea per scene, short sentences, no code. | NPR, Mayer segmenting | — | already |
| A context opening that defines the terms. | pre-training | — | already |

### Explainer skill, narration

| Change | Evidence | Cost | Status |
|---|---|---|---|
| Make "5–9 tags" a ceiling, with 0–1 per scene. Never put `[excited]` on a neutral fact. | ElevenLabs v4 docs; Liew 2022; incongruent-voice studies | edit one line | change |
| Insert 0.4–0.8 s of silence at each scene boundary and shift the timings. Land the scene's final state inside it. | Rey 2019; Hasler 2007 | medium: an ffmpeg step outside `tts.ts`, plus a timings shift | new |
| Keep 150 wpm as a word budget. Cut words to fix an overrun. | Guo 2014; Murphy 2022 | — | already |

### Explainer skill, visuals and player

| Change | Evidence | Cost | Status |
|---|---|---|---|
| Carry a recurring part across scenes with the same id, position, color, and label in the Excalidraw look. | Heer & Robertson 2007 object constancy | guidance in `scenes.example.py` | new |
| Dim earlier steps instead of removing them, where a scene builds on the last. | Ng 2013; Wong 2012 | guidance | new |
| A caption toggle. The research does not settle the default. Off, as on `main`, matches the key-terms-over-verbatim finding. | Adesope & Nesbit 2012; WCAG | — | already (#36) |
| Sync each reveal to its word. Animate only the mechanism. | Noetel 2022; Ploetzner | — | already |
| Chapters, 2x, 5 s skip, the "?" ask button. | Guo 2014; Murphy 2022 | — | already |

### Excalidraw skill

| Change | Evidence | Cost | Status |
|---|---|---|---|
| Cap the critique loop at two rounds of one to three named fixes. Keep the previous render, and keep a revision only when lint does not regress. | Code2Video, OmniManim, "Sorted" critic results | two lines in section 5 | new |
| Prefer 4–5 groups in an overview, with 7 boxes as the upper bound. | Cowan 2001 (unverified); no source for 7 | one line | consider |
| Claim-first brief, grid placement, lint, render. | Code2Video planner ablation; grid-anchor gains | — | already |
| Labels in place, labeled arrows, one accent color. | spatial contiguity g ≈ 0.63; C4 | — | already |

### Leave out

- A drawing hand. It adds motivation at best, and no reliable learning effect.
- Music, flourishes, and decorative motion. Seductive-detail harm is largest in short lessons.
- Interpolated quizzes. The replications shrink the effect.
- More VLM critique rounds. One pass barely helps, and critics sometimes regress layout.
- A slower voice. Energy helps more than speed, and viewers already control the rate.

## Sources and limits

- The research found no study of narrated explainers about software mechanisms. Every transfer to that domain is inference.
- No study tests ElevenLabs v3/v4 audio tags, or tag density, for learning.
- Several publisher pages (Springer, Taylor & Francis) blocked the crawler. Effect sizes for Rey 2019, Adesope & Nesbit 2012, Lawson 2021, and parts of Noetel 2022 rest on abstracts or snippets.
- The subagents found no firsthand advice from Steve Mould, Sebastian Lague, Primer, Bartosz Ciechanowski, Amelia Wattenberger, or Johnny Harris. NPR guidance rests on search snippets.
- No primary Grant Sanderson source for "transform, don't cut" turned up. The continuity rule rests on Heer & Robertson 2007 and practitioner skills.
- WebFetch summarizes pages. Re-check exact wording before quoting any line from the appendices.
- Wiseman's "15% better recall" doodle claim is vendor-commissioned and unreviewed. It is excluded.

---

The appendices follow verbatim. Each one is a subagent's full report with its own links and labels.

# Appendix A

## Learning science for narrated, animated explainers

Research brief for an agent skill that generates 2–5 minute narrated explainer web pages about software mechanisms. One TTS narration track drives SVG or Excalidraw scene animations. Each page has 5–13 scenes at about 150 wpm. The player has pause, scrub, chapters, 5-second skip, and 2x speed.

Research date: 2026-10-28.

### Verification labels

Each finding carries one label.

- **[FT]**: I read the full text of the original paper.
- **[ABS]**: I read the original abstract verbatim, through OpenAlex, PMC, arXiv, or the publisher.
- **[SNIP]**: The claim rests on search-engine snippets or secondary summaries only. Treat the numbers as unverified.

Effect sizes use the metric that the source reports (d, g, r, or partial eta squared). They are not directly comparable across metrics.

---

### A. Meta-reviews that set the frame

#### A1. Multimedia design principles have moderate average effects. The effects grow for complex material and system-paced media.

- **Claim:** Eleven multimedia principles have significant positive meta-analytic effects on learning. Good design matters more for complex material and for system-paced media, such as lectures, than for self-paced media, such as websites.
- **Evidence:** Noetel, Griffith, Delaney, et al. (2022, online 2021). "Multimedia Design for Learning: An Overview of Reviews With Meta-Meta-Analysis." *Review of Educational Research* 92(3), 413–454. https://doi.org/10.3102/00346543211052329. Design: an overview of 29 reviews, with 1,189 studies and 78,177 participants. The largest benefits were for captioning second-language videos, temporal and spatial contiguity, and signaling. The abstract also reports "robust evidence for modality, animation, coherence/removing seductive details, anthropomorphics, segmentation, personalisation, pedagogical agents, and verbal redundancy effects." Five principles improved cognitive-load management. **[ABS]**
- Per-principle numbers from secondary summaries: the average effect on learning is g ≈ 0.38, the average effect on cognitive load is g ≈ 0.22, and prior knowledge was not a significant moderator (p = 0.14). **[SNIP]**: these come from an AI-generated wiki page. I could not get the paper's table.
- **Boundary conditions:** Many component meta-analyses come from Mayer's own lab. Mayer-corpus effects decline slightly with publication year (Carl Hendrick's summary of a later meta-analysis gives an overall g = 0.37) **[SNIP]**. Pre-training is absent from the abstract's "robust" list.
- **Implication:** An explainer is system-paced, complex, linear media, so design quality matters more for it than for a web page. Apply the principles strictly.

#### A2. Video supplements teaching better than it replaces teaching

- **Claim:** Video added to existing teaching has a large effect. Video that replaces other teaching has a small effect.
- **Evidence:** Noetel et al. (2021). "Video Improves Learning in Higher Education: A Systematic Review." *Review of Educational Research*. https://doi.org/10.3102/0034654321990713. Design: a systematic review of 105 randomized trials with 7,776 students. Replacement gave g = 0.28 and supplementation gave g = 0.80. Video helped skills more than knowledge. Videos also did better when they were at least as interactive as the comparison activity. **[SNIP]**: the abstract numbers appear consistently across AERA and ACU pages.
- **Boundary conditions:** The authors note possible experimental and publication bias. A 2024 preprint calls the skills-versus-knowledge split simplistic.
- **Implication:** Present the explainer as a companion to the code or docs, not a substitute. Link back to the real source.

---

### B. Mayer's principles, one by one

Mayer (2021) is the canonical list for video. Mayer, R. E. "Evidence-based principles for how to design effective instructional videos." *Journal of Applied Research in Memory and Cognition* 10(2), 229–240. https://doi.org/10.1016/j.jarmac.2021.03.007. The abstract names 14 principles: multimedia, coherence, signaling, redundancy, spatial contiguity, temporal contiguity, segmenting, pre-training, modality, personalization, voice, image, embodiment, and generative activity. **[ABS]**

Mayer's handbook chapters report median d values: segmenting 0.79, pre-training 0.75, and modality 0.76 **[SNIP]**. These medians come from Mayer's own experiments. Independent meta-analyses usually report smaller values, as the entries below show.

#### B1. Segmenting

- **Claim:** Learning improves when the material is split into learner-paced or clearly separated parts.
- **Evidence:** Rey, Beege, Nebel, Wirzberger, Schmitt & Schneider (2019). "A Meta-analysis of the Segmenting Effect." *Educational Psychology Review* 31, 389–419. https://doi.org/10.1007/s10648-018-9456-4. Design: 56 studies with 88 comparisons. The authors report small-to-medium effects on retention and transfer. Segmentation also reduced overall cognitive load and increased learning time. **[SNIP]**: OpenAlex has no abstract, so the numbers come from consistent snippets. One snippet says high-prior-knowledge learners gained more retention from segmenting **[SNIP]**.
- Mayer & Chandler (2001). *Journal of Educational Psychology* 93(2), 390. https://doi.org/10.1037//0022-0663.93.2.390. Learner-controlled pacing of a narrated lightning animation improved transfer but not retention. **[ABS]**
- Biard, Cojean & Jamet (2018). *Computers in Human Behavior* 89, 411–417. https://doi.org/10.1016/j.chb.2017.12.002. For procedural video, system-paced pauses after each step beat a plain pause button. Novices rarely used the pause button. **[SNIP]**
- **Boundary conditions:** Part of the benefit may come from extra time, not from chunking. Garrett (*BJET*) found that segmentation failed to improve software video tutorials **[SNIP]**.
- **Implication:** Make each scene one idea with a clear boundary. Insert a short narration gap or visual "beat" at the boundary. Do not rely on viewers to press pause.

#### B2. Signaling (cueing)

- **Claim:** Highlighting essential elements improves learning.
- **Evidence:**
  - Alpizar, Adesope & Wong (2020). *Educational Technology Research and Development* 68(5). https://doi.org/10.1007/s11423-020-09748-7. Design: 29 studies, 44 effect sizes, and 2,726 participants. The overall effect was d = 0.38. Study, participant, presentation, and method features moderated the effect. **[SNIP]**
  - Schneider, Beege, Nebel & Rey (2018). *Educational Research Review* 23, 1–24. https://doi.org/10.1016/j.edurev.2017.11.001. Signaling had a stronger effect on retention than on transfer. It also lowered perceived difficulty and mental effort. **[SNIP]**
  - Richter, Scheiter & Eitel (2016). *Educational Research Review*. Text-picture signaling gave r = 0.17 for comprehension and transfer, and it helped most for low-prior-knowledge learners. **[SNIP]**
  - Noetel 2022 ranks signaling among the largest effects. **[ABS]**
- **Boundary conditions:** The effect shrinks for high-prior-knowledge learners. Results for dynamic signals, such as moving arrows, are mixed.
- **Implication:** Highlight the element that the narration names at the moment the narrator names it. Use one highlight style throughout. Dim the rest of the scene.

#### B3. Coherence (removing seductive details)

- **Claim:** Interesting but irrelevant material, such as anecdotes, decorative graphics, or music, hurts learning.
- **Evidence:** Sundararajan & Adesope (2020). "Keep it Coherent: A Meta-Analysis of the Seductive Details Effect." *Educational Psychology Review* 32, 707–734. Design: 58–68 experiments; the sources disagree on the count. Seductive details hurt learning. The effect was larger in short lessons, for novices, and on paper than on screen. **[SNIP]**: no pooled g was found. In Muller et al. (2008, JCAL), the "Extended Exposition" condition with extra interesting facts did not beat the plain exposition **[ABS]**.
- **Boundary conditions:** The effect was not significant in longer lessons. A detail that is relevant to the learning goal is not seductive.
- **Implication:** Cut background music, decorative motion, and asides. A 2–5 minute explainer is the "short lesson" case, where the harm is largest.

#### B4. Redundancy, and the cases where on-screen text helps

- **Claim:** Do not add verbatim captions to narrated graphics. The rule reverses in identifiable cases.
- **Evidence:**
  - Adesope & Nesbit (2012). "Verbal redundancy in multimedia learning environments: A meta-analysis." *Journal of Educational Psychology* 104(1), 250–263. https://doi.org/10.1037/a0026147. Design: 57 studies. Spoken plus written text beat spoken-only text. It did not differ from written-only text. The advantage held for low-prior-knowledge learners, system-paced material, and **picture-free** material. **Key terms extracted from the narration beat verbatim spoken plus written text**, and they explained much of the advantage. **[ABS]**
  - Noetel 2022 found that captioning second-language video gave one of the largest effects. **[ABS]** Montero Perez et al. (2013, *System*) found large caption effects for second-language listening and vocabulary across 18 studies **[SNIP]**.
  - Kalyuga, Chandler & Sweller (2000). *Journal of Educational Psychology* 92(1), 126. Audio text beat visual text for novices, but adding the same text on screen removed the advantage. After training, the diagram-only format beat diagram plus audio. That is an expertise reversal. **[ABS]**
- **Boundary conditions:** Captions help second-language viewers, deaf and hard-of-hearing viewers, and viewers who watch on mute. Accessibility law can also require captions, separately from any learning effect.
- **Implication:** Put short key-term labels in the scene, not full transcripts. Offer full captions as an optional toggle, off by default, for accessibility and second-language viewers.

#### B5. Spatial and temporal contiguity

- **Claim:** Put labels next to what they label. Narrate an element while it is visible, not before or after.
- **Evidence:** Ginns (2006). *Learning and Instruction* 16, 511–525. Design: 50 studies. The pooled effect was d ≈ 0.85 (95% CI 0.68–1.02), reported as cited by Beege et al. 2019 **[SNIP]**. Schroeder & Cenkci (2018), *Educational Psychology Review* 30, 679–701, studied spatial contiguity across 60 effect sizes **[SNIP]**. Noetel 2022 ranks contiguity among the largest effects **[ABS]**.
- **Boundary conditions:** The effect is larger when the material has high element interactivity.
- **Implication:** Sync each animation cue to the word that names it, at word level, from TTS timestamps. Put labels on the nodes, not in a legend.

#### B6. Pre-training

- **Claim:** Teaching the names and characteristics of key parts first helps learners follow the explanation of how the parts interact.
- **Evidence:** Mayer 2021 lists pre-training **[ABS]**. Mayer's handbook gives a median d = 0.75 **[SNIP]**. Noetel 2022 does not list pre-training among its robust effects **[ABS]**.
- **Boundary conditions:** The evidence comes mostly from one lab. Pre-training mainly helps novices.
- **Implication:** Open with a short "cast of components" scene that names each box once, before showing the flow.

#### B7. Modality

- **Claim:** Spoken words with graphics beat printed words with graphics.
- **Evidence:** Ginns (2005), *Learning and Instruction* 15(4), 313–331, a modality meta-analysis **[SNIP]**. Wang, Xie & Li (2016) pooled 91 studies and found much smaller effects (d = 0.24 for retention, d = 0.25 for transfer). The pace of presentation, the dynamism of pictures, and the duration of the material moderated the effect **[SNIP]**.
- Leahy & Sweller (2011), *Applied Cognitive Psychology*, https://doi.org/10.1002/acp.1787. **Long** audio segments reversed the modality effect: written text beat narration. Shortening the segments restored the effect. **[ABS]**
- **Boundary conditions:** The transient information effect applies (see C1). Modality works best when the presentation is system-paced.
- **Implication:** Narration is the right channel. Keep each narrated sentence short and tied to one visual change.

#### B8. Personalization

- **Claim:** Conversational style ("you", "we") improves learning.
- **Evidence:** Ginns, Martin & Marsh (2013). *Educational Psychology Review* 25(4), 445–472. The meta-analysis found a medium effect on transfer and a small effect on retention **[SNIP]**. Noetel 2022 lists personalisation as robust **[ABS]**.
- **Boundary conditions:** Almeida et al. (2024), *JCAL*, https://doi.org/10.1111/jcal.13026, with N = 139, found that **non**-personalized text gave better transfer. The authors question the robustness of the effect. **[ABS]**
- **Implication:** Use a plain conversational register, such as "you call `commit()`". Do not overdo second person when it makes the viewer play a role that does not fit.

#### B9. Voice (human vs TTS)

- **Claim:** Mayer's original principle says that a human voice beats a machine voice. Modern TTS appears to close the gap.
- **Evidence:**
  - Craig & Schroeder (2017). *Computers & Education* 114, 193–205. https://doi.org/10.1016/j.compedu.2017.07.003. A modern TTS engine matched a human voice on credibility. It gave **better** transfer than both a classic TTS engine and the human voice. Retention did not differ. **[SNIP]**
  - Netland et al. (2025). *Computers & Education* 224, 105164. https://doi.org/10.1016/j.compedu.2024.105164. With N = 447 and 1,788 video treatments, AI-generated videos gave similar exam results to human-made videos. Human-made videos gave a small but significant advantage in learning experience. **[ABS]**
  - Mayer and colleagues (2021, *IJAIED*). Learners recognize the instructor's emotion from voice alone as accurately as from voice plus an on-screen agent. This supports voice as a channel for social-emotional cues. **[ABS]**
  - A vendor study (TechSmith, N = 768) found that voice quality mattered more than whether the voice was human or AI. **[SNIP]**, not peer-reviewed.
- **Boundary conditions:** Monotone or mechanical TTS still hurts. The effect depends on the quality of the TTS.
- **Implication:** Use a high-quality, expressive TTS voice. Spend effort on prosody, such as emphasis on key terms and pauses at scene boundaries, more than on human-likeness.

#### B10. Image and embodiment

- **Claim:** A static instructor face adds nothing. Gesture and drawing by a visible hand can help.
- **Evidence:**
  - Mayer 2021 states the image principle ("do not display static image of instructor's face") and the embodiment principle ("display gesturing instructor") **[ABS]**.
  - Fiorella & Mayer (2016). *Journal of Educational Psychology* 108, 528–546. https://doi.org/10.1037/edu0000065. In five experiments, watching the instructor draw beat static diagrams for low-prior-knowledge learners (d = 0.58), but not for high-prior-knowledge learners (d = −0.24). A drawing hand alone helped (d = 0.35). Drawing without a hand did not help (d = −0.16). **Computer diagrams animated to match the act of drawing did not significantly beat static computer diagrams (d = 0.33, n.s.)**. **[ABS]**
  - Fiorella, Stull, Kuhlmann & Mayer (2020). *Journal of Educational Psychology* 112(5), 895–906. https://doi.org/10.1037/edu0000408. With N = 196, diagrams drawn dynamically on screen without an instructor, followed by **learner-written explanations**, gave the best transfer (d > 1.0 for the explain condition with dynamic visuals). Learner drawing and rewatching were weaker. **[ABS]**
  - Alemdağ (2022), *Education and Information Technologies*, meta-analyzed 20 studies. An on-screen instructor did not improve learning, but it raised motivation outcomes. **[SNIP]**
- **Boundary conditions:** The evidence on progressive drawing is mixed: the hand-free and computer-animated versions failed in some experiments and worked in Fiorella 2020.
- **Implication:** Progressive build-up of Excalidraw-style diagrams is defensible but not proven. Do not add an avatar or a face. Treat a sketched hand cursor as an optional experiment, not a default.

#### B11. Multimedia (words plus pictures)

- **Claim:** Words plus relevant graphics beat words alone.
- **Evidence:** Mayer 2021 **[ABS]**. Playback-speed work also shows that a visual component protects comprehension at high speed (Murphy et al. 2024, see E1) **[ABS]**.
- **Implication:** Each sentence should have a matching visual state. A scene with no visual change during a long narration span wastes the visual channel.

---

### C. Transient information, animation vs static, and learner control

#### C1. The transient information effect

- **Claim:** Speech and animation vanish as they play. When a segment is long or complex, the transience can overload working memory and make the permanent version better.
- **Evidence:** Leahy & Sweller (2011) **[ABS]**, above in B7. Wong, Leahy, Marcus & Sweller (2012, *Learning and Instruction*) found that shorter segments overcome transience **[SNIP]**. Ng, Kalyuga & Sweller (2013) reduced transience with pause/play and with tracing that leaves a trail of prior states **[SNIP]**.
- **Implication:** Keep earlier states visible. Leave a trace of the path a request took and dim it, instead of erasing it. End each scene on a static "summary frame" that holds long enough to inspect.

#### C2. Animation beats static pictures only modestly, except when the change itself must be learned

- **Evidence:**
  - Höffler & Leutner (2007). *Learning and Instruction* 17(6), 722–738. Design: 26 studies with 76 comparisons, d = 0.37. Effects were larger for procedural-motor knowledge and for realistic animations. **[SNIP]**
  - Berney & Bétrancourt (2016). *Computers & Education* 101, 150–167. Design: 140 comparisons, g = 0.226 (95% CI 0.12–0.33). **[SNIP]**
  - Castro-Alonso, Wong, Adesope, Ayres & Paas (2019). *Educational Psychology Review*. https://doi.org/10.1007/s10648-019-09469-1. Design: 46 studies, 82 effect sizes, and 5,474 participants, g+ = 0.23. The gender ratio of the sample moderated the effect. **[SNIP]**: I could not confirm the direction of the gender effect.
  - Ploetzner, Berney & Bétrancourt (2020). *Journal of Computer Assisted Learning*. https://doi.org/10.1111/jcal.12476. Animations were "significantly more successful" when **the features of the displayed change had to be learned** **[ABS]**. The re-analysis gives g = 0.340 for simple changes and g = 0.647 for complex changes **[SNIP]**.
  - Ploetzner et al. (2021). *Instructional Science* 49, 497–514. https://doi.org/10.1007/s11251-021-09541-w. With N = 88, animation was best for identifying motions. **Static pictures were best for identifying spatial arrangements.** **[ABS]**
- **Boundary conditions:** The "illusion of understanding" applies to animation (E3). Representational animation even hurt learning in Paik & Schraw (2013).
- **Implication:** Animate only what changes in the mechanism: message flow, state transitions, ordering, and races. Show structure, such as architecture and data layout, as a still frame.

#### C3. Learner control: pausing helps, but people rarely use it

- **Evidence:**
  - Hasler, Kersten & Sweller (2007). *Applied Cognitive Psychology*. https://doi.org/10.1002/acp.1345. Learner-paced versions, either segments or stop/play buttons, gave higher scores and lower load than system-paced versions, **even though the stop/play buttons were rarely used**. The effect appeared only on high element-interactivity questions. **[ABS]**
  - Karich, Burns & Maki (2014). *Review of Educational Research* 84(3). https://doi.org/10.3102/0034654314526064. In educational technology broadly, learner control had an overall effect of g = 0.05, which is near zero. **[ABS]**
  - Biard et al. (2018) found that novices underuse pause, so system-imposed pauses work better. **[SNIP]**
- **Boundary conditions:** The benefit of learner control is specific to complex, transient material. Learner control in general does little.
- **Implication:** Keep the pause, scrub, and chapter controls, but do not count on them. Build pacing into the narration with pauses at scene ends.

#### C4. Expertise reversal

- **Claim:** Supports that help novices can hurt experts, for example narration over a diagram the expert can already read.
- **Evidence:** Kalyuga (2007), *Educational Psychology Review* 19, 509–539 (review) **[SNIP]**. Kalyuga et al. (2000) found a reversal after training **[ABS]**. In Fiorella & Mayer (2016), drawing helped low-prior-knowledge learners but not high-prior-knowledge learners **[ABS]**. In Paik & Schraw (2013), animation made low-proficiency learners overconfident and high-proficiency learners pessimistic **[ABS]**.
- **Implication:** Pick a target reader before writing, such as "knows the language, new to this subsystem". 2x speed and 5-second skips give experts a way past material they already know.

---

### D. Engagement data from real platforms

#### D1. Guo, Kim & Rubin (2014): length, style, and speaking rate

- **Evidence:** Guo, Kim & Rubin (2014). "How Video Production Affects Student Engagement: An Empirical Study of MOOC Videos." ACM Learning@Scale. https://doi.org/10.1145/2556325.2566239. Design: a retrospective log analysis of 6.9M sessions in four Fall-2012 edX math and science courses, plus interviews with edX staff. **[FT]**: I extracted the text from the PDF.
  - **Length:** "median engagement time is at most 6 minutes, regardless of total video length". Students often watched less than half of videos longer than 9 minutes. Recommendation: "segment videos into short chunks, ideally less than 6 minutes."
  - **Khan-style drawing:** In tutorials, students engaged 1.5–2x longer with tablet drawing than with slides or code screencasts. 40% vs 31% of sessions were followed by a problem attempt.
  - **Talking head:** Videos that cut between the instructor's head and the slides were more engaging than slides alone.
  - **Speaking rate:** Rates ranged from 48 to 254 wpm (mean 156, SD 31). Within a length bucket, engagement rose by up to 2x with speaking rate. The mid bucket (145–165 wpm) was the least energetic. The authors call speaking rate "merely a surface feature that correlates with enthusiasm". They recommend not forcing speed, and editing out pauses and filler words. They found no difference in play or pause counts by speaking rate.
  - **Tutorials vs lectures:** Students engaged with tutorials for only 2–3 minutes regardless of length. For tutorials, the authors recommend support for rewatching and skimming, such as visual signposts for transitions.
  - **Limitations stated by the authors:** The study is retrospective, not a controlled experiment. Engagement time is a proxy, not a learning measure. The sample is only early-adopter edX learners in math and science.
- **Critiques and replications:** A 2022 multiple-case MOOC study (arXiv 2204.03405) found no relation between video length and mid-video drop-off. It warns against a "magic number" **[SNIP]**. Brame (2016) relays the 6-minute guidance **[ABS/FT via PMC]**.
- **Implication:** A total of 2–5 minutes is well inside the engagement window. Avoid a slow, flat 150 wpm delivery. Aim for about 150–170 wpm with energetic prosody, and trim dead air.

#### D2. Brame (2016): a synthesis for practitioners

- **Evidence:** Brame (2016). "Effective Educational Videos: Principles and Guidelines for Maximizing Student Learning from Video Content." *CBE—Life Sciences Education* 15(4), es6. https://doi.org/10.1187/cbe.16-03-0125. Design: a narrative review organized around three elements: cognitive load, engagement, and active learning. Its recommendations are to keep videos to 6 minutes or less, use signaling, segment, weed out extraneous material, match the modality, use a conversational style, speak with enthusiasm, provide guiding questions, provide interactive navigation, embed questions, and integrate the video into homework. **[ABS]**; I read the recommendation table from PMC.
- **Boundary conditions:** It is a narrative review, not a meta-analysis. Many of its cited studies are the same Mayer and Guo studies.
- **Implication:** Brame's checklist is a reasonable rubric for a self-critique pass. Its "active learning" leg is the one that auto-generated explainers most often lack.

---

### E. Speed, fluency, and the illusion of understanding

#### E1. Playback speed up to 2x costs little for young adults

- **Evidence:**
  - Murphy, Hoover, Agadzhanyan, Kuehn & Castel (2022, online 2021). "Learning in double time." *Applied Cognitive Psychology* 36(1), 69–82. https://doi.org/10.1002/acp.3899. Speeds of 1.5x and 2x had minimal costs on immediate and one-week tests. "Performance declined beyond 2x speed." Watching twice at 2x did not beat watching once at 1x, unless the rewatch came just before the test. The authors caution that "these trends may differ for videos with different speech rates, complexity or difficulty, and audiovisual overlap." **[ABS]**
  - Murphy, Hoover & Castel (2023). *Memory*. https://doi.org/10.1080/09658211.2023.2198326. Older adults were impaired at faster speeds. Faster speeds reduced mind-wandering in younger adults. **[ABS]**
  - Murphy et al. (2024). *Educational Psychology Review*. https://doi.org/10.1007/s10648-024-09917-7. In four experiments, 2.5x did not impair performance, but the authors "still do not advise exceeding 2x". Visuals helped, "especially when processing information at faster speeds". **[ABS]**
  - Risko et al. (2023/24). *Journal of Experimental Psychology: Applied*. https://doi.org/10.1037/xap0000494. The benefits of 1.5x speed and of interpolated tests were additive. **[ABS]**
- **Boundary conditions:** The test lectures were non-technical (the Roman Empire, real estate appraisal). Dense technical narration at 150 wpm becomes 300 wpm at 2x, which exceeds Guo's fastest observed rate (254 wpm).
- **Implication:** Keep the 2x control. Visuals must carry the key facts, so a viewer at 2x can still follow. Do not raise the base narration rate much above 160 wpm, because 2x then becomes too fast.

#### E2. Fluent delivery inflates confidence more than learning

- **Evidence:**
  - Carpenter, Wilford, Kornell & Mullaney (2013). *Psychonomic Bulletin & Review* 20, 1350–1356. https://doi.org/10.3758/s13423-013-0442-z. A fluent instructor raised perceived learning but not actual learning. **[SNIP]**
  - Carpenter, Mickes, Rahman & Fernandez (2016). *JEP: Applied*. https://doi.org/10.1037/xap0000077. In a 22-minute lecture, the fluent instructor received higher ratings, and test scores "did not consistently differ". **[ABS]**
  - Toftness et al. (2018). *Metacognition and Learning*. "Instructor fluency leads to higher confidence in learning, but not better learning." **[SNIP]**: title only.
- **Implication:** Polished TTS and smooth animation will make viewers feel they learned more than they did. Add a check that reveals gaps (see F2 and F3).

#### E3. The illusion of understanding from explainer videos and animations

- **Evidence:**
  - Paik & Schraw (2013). *Journal of Educational Psychology* 105(2), 278–289. https://doi.org/10.1037/a0030281. In a randomized 2 × 2 study, representational animation hurt learning and directive animation helped. **Both** kinds of animation induced the illusion of understanding. **[ABS]**
  - Kulgemeyer & Wittwer (2022). *International Journal of Science and Mathematics Education*. https://doi.org/10.1007/s10763-022-10265-7. With N = 149 low-prior-knowledge learners and videos of about 2.2 minutes, a video built on misconceptions produced the **same** belief of understanding (F = 0.32, p = .57). It also produced more misconceptions (partial η² = 0.48) and fewer correct conceptions (partial η² = 0.21). **[ABS + PMC text]**
  - Hörnlein & Kulgemeyer (2026). *International Journal of Science Education*. https://doi.org/10.1080/09500693.2026.2646710 (arXiv 2512.02824). In two studies (N = 244 and N = 175), high-level learning tasks after a physics explainer reduced the illusion immediately (d = 0.69). High-level and low-level tasks were similarly effective in the long term. Low-prior-knowledge learners were more susceptible. The authors conclude that "explainer videos should not be used in isolation". **[ABS]**
  - Kulgemeyer (2018). *Research in Science Education*. https://doi.org/10.1007/s11165-018-9787-7. The paper describes a framework of seven factors with 14 features. Confirmed factors include adaptation to prior knowledge, misconceptions, and interest; structure, including summaries; and minimal explanation, meaning no digressions. A video that followed the framework improved declarative but not conceptual knowledge. **[SNIP]**
  - YouTube views and likes do not track explaining quality, but the number of content-related comments does (Kulgemeyer and colleagues, 2023, https://doi.org/10.1007/s10763-022-10351-w). **[ABS]**
- **Implication:** Correctness matters more than polish. A smooth, wrong explainer is worse than none, so verify every claim against the source code. Follow the explainer with at least one demanding question.

#### E4. Addressing misconceptions directly (Muller)

- **Evidence:**
  - Muller, Bewes, Sharma & Reimann (2008). "Saying the wrong thing." *JCAL* 24(2), 144–155. https://doi.org/10.1111/j.1365-2729.2007.00248.x. With N = 364, the Refutation video (d = 0.79) and the Dialogue video (d = 0.83) gave larger gains than the Exposition video. High-prior-knowledge learners were not disadvantaged. **[ABS]** A later symposium write-up says the differences were not significant **[SNIP]**.
  - Muller, Sharma & Reimann (2008). *Science Education* 92, 278–296. https://doi.org/10.1002/sce.20244. With N = 272, a dialogue video that raised alternative conceptions increased **reported mental effort** and posttest scores. Students reported a more active approach. **[ABS]**
- **Boundary conditions:** The studies used physics content with strong everyday misconceptions. The transfer to software assumes that common wrong mental models exist, for example "`await` blocks the thread" or "the mutex protects the data".
- **Implication:** For each mechanism, state the most common wrong model, show why it fails, and then show the right model. This raises useful effort and counters the fluency illusion.

---

### F. Generative activities: pre-questions, interpolated questions, and explanation

#### F1. Pre-questions

- **Evidence:**
  - Carpenter & Toftness (2017). *JARMAC* 6, 104–109. https://doi.org/10.1016/j.jarmac.2016.07.014. With a short three-segment video, pre-questions improved learning of **both** pre-questioned and non-pre-questioned information. **[ABS]**
  - Toftness, Carpenter, Lauber & Mickes (2018). *JARMAC* 7(3). https://doi.org/10.1016/j.jarmac.2018.06.003. With authentic lectures over 20 minutes, pre-questions helped pre-questioned items. Non-pre-questioned items did not differ, or were only marginally better. The authors call the benefits "positive but limited". **[ABS]**
  - St. Hilaire, Chan & Ahn (2024, online 2023). *Psychonomic Bulletin & Review* 31, 411–441. https://doi.org/10.3758/s13423-023-02353-8. In a preregistered meta-analysis, the specific effect was g = 0.54 (k = 97) and the general effect was g = 0.04 (k = 91). **[SNIP]**
  - Pan & Carpenter (2023). *Educational Psychology Review*. https://doi.org/10.1007/s10648-023-09814-5. In this review, pre-questioning "can often enhance learning", including with videos, if the learner can study the correct answers afterwards. **[ABS]**
  - Kane-lab replication (2022). *Cognitive Research: Principles and Implications*. https://doi.org/10.1186/s41235-022-00372-y. With N = 195, content pretesting did not reduce mind-wandering or improve learning. **[ABS]**
- **Implication:** Before scene 1, ask one or two questions about the mechanism's key facts. Make sure the explainer answers them explicitly. Do not expect a broad attention boost.

#### F2. Interpolated questions

- **Evidence:**
  - Szpunar, Khan & Schacter (2013). *PNAS* 110(16), 6313–6317. https://doi.org/10.1073/pnas.1221764110. Design: a 21-minute statistics lecture in four segments of about 5.5 minutes, with N = 32 + 48. Mind-wandering fell to 19% for the tested group, versus 39% for restudy and 41% for no test. The final cumulative score was 90% for tested, versus 76% and 68%. Tested students took more notes and reported less test anxiety. **[ABS + PMC text]**
  - Chan, Meissner & Davis (2018). *Psychological Bulletin* 144(11). https://doi.org/10.1037/bul0000166. In a meta-analysis of test-potentiated new learning, g ≈ 0.44 **[SNIP]**. The authors note that testing too often can impair new learning. A 2020 erratum corrected mis-sorted data. Boustani & Shanks (2022) argue that the evidence is weak once heterogeneity and publication bias are handled **[SNIP]**.
  - Kane-lab replication (2022). Interpolated tests reduced task-unrelated thought only slightly, with no Bayes-factor support. They had **no** detectable effect on learning. **[ABS]**
- **Boundary conditions:** The large effects come from roughly 20-minute lectures, where attention decays. A 2–5 minute explainer gives mind-wandering less time to build up.
- **Implication:** Interpolated quizzes are optional for a 3-minute explainer. A single retrieval question at a chapter boundary in the middle, or at the end, is a cheap hedge.

#### F3. Learner-generated explanation after a segment

- **Evidence:** In Fiorella et al. (2020), writing an explanation after each part of a lesson beat rewatching (transfer d = 0.87) and drawing (transfer d = 0.67) **[ABS]**. In Hörnlein & Kulgemeyer (2026), high-level follow-up tasks reduced the illusion of understanding (d = 0.69) **[ABS]**. Mayer 2021 lists generative activity as a principle **[ABS]**.
- **Implication:** End with a prompt such as "Explain in two sentences why X happens before Y". Optionally route the answer to the existing "ask an agent" feature for feedback.

#### F4. Worked examples and video modeling

- **Evidence:** Hoogerheide, van Gog, and colleagues describe video modeling examples, in which a model demonstrates and explains a task, as an effective method. They note that little empirical work guides the design choices. **[SNIP]** I found no 2023–2025 meta-analysis specific to video modeling.
- **Implication:** For "how to use" content, walk through one concrete trace with real values, such as a request with ID 42 moving through the stages, instead of an abstract flow.

---

### G. Generated video specifically (2024–2026)

- Netland et al. (2025). AI-generated teaching videos matched human-made ones on exam scores. Learners slightly preferred the human-made videos. Production took hours instead of days. **[ABS]**
- Reviews from 2025 report comparable immediate learning from AI-generated and human videos. Most studies are pilots with immediate tests only. **[SNIP]**
- **Implication:** The format is not the bottleneck. Correctness, structure, and generative follow-up are.

---

### Ten implications ranked by value

1. **Verify every claim against the source before publishing.** A fluent, wrong explainer creates confident misconceptions (Kulgemeyer & Wittwer 2022, partial η² = 0.48). Polish does not reveal errors to the viewer (Carpenter 2013 and 2016).
2. **Sync each visual change to the word that names it, and label in place.** Contiguity and signaling are among the largest effects in Noetel 2022 (Ginns 2006, d ≈ 0.85).
3. **End with at least one demanding generative prompt**, such as "explain why" or "predict what happens if". This counters the illusion of understanding (Hörnlein & Kulgemeyer 2026, d = 0.69) and helps transfer (Fiorella 2020).
4. **Name and refute the most common wrong mental model.** Refutation and dialogue gave d ≈ 0.8 in Muller et al. 2008 and raised useful effort.
5. **Animate change, and show structure still.** Animation pays off when the change itself must be learned (g = 0.65 for complex changes), and static pictures win for spatial layout (Ploetzner 2020, 2021). The overall animation advantage is only g ≈ 0.23.
6. **Make one scene equal one idea, with a built-in pause or held summary frame at its end.** Segmenting works (Rey 2019), learners rarely press pause (Hasler 2007, Biard 2018), and long transient segments reverse the modality benefit (Leahy & Sweller 2011).
7. **Leave traces instead of erasing.** Keep prior states visible and dimmed to reduce transience (Ng et al. 2013, Wong et al. 2012).
8. **Cut everything decorative**, such as music, flourishes, and asides. The seductive-details harm is largest in short lessons and for novices (Sundararajan & Adesope 2020).
9. **Show key terms on screen, not transcripts.** Key-term labels beat verbatim text (Adesope & Nesbit 2012). Keep full captions as an off-by-default accessibility toggle.
10. **Use an expressive, high-quality TTS voice at about 150–170 wpm, with a pre-training "cast" scene and a stated target reader.** Modern TTS matches human voices (Craig & Schroeder 2017, Netland 2025). Energy matters more than speed (Guo 2014). The 2x control stays usable only if the base rate is moderate (Murphy 2022, 2024).

Ranks 11 and 12, if space allows: put one or two pre-questions before scene 1 (specific effect g = 0.54, general effect g = 0.04, St. Hilaire 2024). Name chapters after mechanism steps, for skimming and rewatching (Guo 2014, tutorials).

---

### Credible disagreements

- **How large the effects are.** Mayer's own medians (d ≈ 0.7–0.8) are much larger than independent meta-analyses: modality d ≈ 0.25 in Wang et al. 2016, animation g ≈ 0.23, and an overall Mayer corpus g ≈ 0.37 that declines over time. Noetel 2022 supports most principles but reports moderate averages.
- **Whether animation is worth it.** Three meta-analyses find small overall effects. Ploetzner argues that the studies measure the wrong outcomes. Castro-Alonso argues that sample gender imbalance confounds the results. Paik & Schraw find that representational animation can hurt and that all animation inflates confidence.
- **Redundancy.** The classic principle says "no captions". Adesope & Nesbit find that spoken plus written text beats spoken-only text for novices, for system-paced material, and for picture-free material. Second-language captioning is one of the largest effects in Noetel 2022. Accessibility requires captions regardless.
- **The voice principle.** Mayer's 2003-era finding favored human voices. Craig & Schroeder 2017 found modern TTS equal or better. Netland 2025 found equal learning but a small preference for human-made videos.
- **Personalization.** Meta-analyses support it (Ginns 2013, Noetel 2022). Almeida et al. 2024 found a reversal on transfer and questioned its robustness.
- **The 6-minute rule.** Guo 2014 is engagement data, not learning data, and comes from one 2012 cohort. A 2022 multi-case study found no relation between length and drop-off. A short explainer meets the rule either way.
- **Faster speech.** Guo found that faster speakers were more engaging, but the authors attribute this to enthusiasm, not speed. Murphy finds up to 2x harmless for young adults with non-technical lectures. Murphy 2023 finds harm for older adults. Nobody has tested dense technical narration at 2x.
- **Interpolated testing and pre-questions.** Szpunar 2013 reports large effects. A 2022 replication with N = 195 found almost none on learning. Boustani & Shanks challenge the robustness of Chan 2018. Pre-question benefits are mostly specific to the questioned items (g = 0.04 general), and they shrink with authentic lectures (Toftness 2018).
- **Learner control.** The pause benefit for complex animation is real (Hasler 2007, Mayer & Chandler 2001). Learner control in general shows g = 0.05 (Karich 2014), and novices underuse it (Biard 2018).
- **Progressive drawing.** Watching a hand draw helped. Hand-free and computer-animated drawing did not differ significantly from static diagrams in Fiorella & Mayer 2016. They did help in Fiorella et al. 2020 when combined with self-explanation.

### Gaps and items I could not verify

- The per-principle effect table of Noetel 2022. I read only its abstract.
- The pooled g values of Rey 2019 (segmenting), Schneider 2018 and Alpizar 2020 (signaling), and Sundararajan 2020 (seductive details). I have snippets only.
- The direction of the gender moderator in Castro-Alonso 2019.
- The full list of factors in Kulgemeyer's 2018 framework.
- I found no study of narrated explainers for software or programming mechanisms specifically. All transfer to that domain is inference.

# Appendix B

## Practitioner advice on explaining complex concepts in video and interactive essays

Target: an agent skill that generates 2–5 minute narrated, animated explainer pages about software mechanisms (5–13 scenes, ~150 wpm TTS with emotion tags, SVG or Excalidraw diagrams that draw on as words are spoken).

### Verification key

- **[V]**: I fetched the original source (page, transcript, or paper) and the short quote appears there. Note: WebFetch returns pages through a summarizer. Treat quotes as near-verbatim. Re-check wording before you publish any quote.
- **[T]**: verified against a third-party transcript (rosetta.to) of the original video. The wording is likely exact but not checked against the video.
- **[S]**: snippet or secondary summary only. I could not open the original.

### Sources and author experience

| Person | Relevant experience | Sources used |
|---|---|---|
| Grant Sanderson (3Blue1Brown) | Math YouTube channel with over 4M subscribers. Wrote Manim. Runs the Summer of Math Exposition (SoME). 2023 JPBM Communications Award. | SoME1 announcement video, 2021-07-16 [T]. SoME1 post, 2021-07-16 [V]. SoME1 results, 2021-10-23 [V]. SoME2 results video "What makes a great math explanation?", 2022-10-01 [T]. Dropbox profile, 2021-03-04 [V]. Dwarkesh Podcast, 2023-10-12 [V] |
| Derek Muller (Veritasium) | PhD in physics education (Sydney, 2008) on multimedia and misconceptions. Large science channel. | "Khan Academy and the Effectiveness of Science Videos", 2011-03-17 [T]. Muller & Sharma, "Tackling misconceptions in introductory physics using multimedia presentations", 2012 [V, abstract]. "Clickbait is Unreasonably Effective", 2021-08-17 [T] |
| Nicky Case | Makes explorable explanations (Parable of the Polygons, The Evolution of Trust). | "How I Make Explorable Explanations", 2017-09-20 [V]. "How To Explain Things Real Good", Stanford talk transcript, undated [V] |
| Bret Victor | Interface researcher (Apple, Dynamicland). Coined "explorable explanations". | "Explorable Explanations", 2011-03-10, postscript 2024-02 [V]. "Up and Down the Ladder of Abstraction", 2011-10 [V] |
| Amit Patel (Red Blob Games) | Game developer and author of interactive algorithm tutorials (A*, hex grids) since the 1990s. | "Thoughts on explorable explanations", 2018-05-14 [V]. EDUC432 talk notes, 2023-02 [V] |
| Julia Evans | Author of programming zines and a long-running technical blog. | "Patterns in confusing explanations", 2021-08-19 [V]. "Write good examples by starting with real code", 2021-07-08 [V] |
| Andy Matuschak | Former Apple iOS engineer and Khan Academy R&D lead. Researches tools for thought. Co-created Quantum Country. | "Why books don't work", 2019-05-11 [V]. Dwarkesh Podcast, 2023-07-12 [V] |
| Josh W. Comeau | Builds interactive CSS and React courses and blog posts with a custom widget in nearly every article. | Twitter thread on teaching developers, 12 April, year not shown on the page (likely 2021) [V via threadreader] |
| Kurzgesagt (Philipp Dettmer, head writer) | Animated science studio with a team of about 15. | "Our video process" page, undated [V]. "...And We'll Do it Again", 2021-12-07 [T] |
| CGP Grey | Animated explainer YouTuber. | "Grey Answers Your Most Common Questions", 2013-02-25 [T] |
| Tom Scott | Weekly explainer videos for 10 years, every word scripted. | Waveform podcast, "How Tom Scott Makes Videos", date unverified [T] |
| NPR Training | Public radio's in-house training site. | Search snippets of training.npr.org pages, 2015–2017 [S]. The pages time out or redirect. |
| Randy Olson | Former marine biology professor, later filmmaker. Created the ABT template. | NCSE and Sigma Xi interviews [S] |
| Trey Parker and Matt Stone | South Park writers. Source of the "but/therefore" rule. | NYU / mtvU "Stand In" talk, 2011 or 2014 [S] |
| Steven Pinker | Psycholinguist and author of *The Sense of Style* (2014). | APS Observer report, 2015-07-30 [V, secondary report with Pinker quotes] |
| Kulgemeyer & Wittwer | Physics education researchers who study explainer videos. | IJSME 2022/2023, n=149 RCT [V]. Hörnlein & Kulgemeyer 2025 follow-up [S] |
| Richard Mayer | Multimedia learning researcher. | Principle summaries from university pages [S] |

No primary process advice turned up for Steve Mould, Sebastian Lague, Primer (Justin Helps), Bartosz Ciechanowski, Amelia Wattenberger, Johnny Harris, or Hamish Todd. The searches returned only secondary profiles or HN commenters. See "Gaps" at the end.

---

### Principle 1. Start concrete, then abstract

**Advice.** Open with one specific case the viewer can see. State the general rule after that case. Experts reverse this order because the abstraction feels natural once they know it.

- **Grant Sanderson**, SoME1 announcement video, 2021-07-16 [T]: "try very hard to structure your explanation to go from the concrete to the abstract." He also says to "be aware of the layers of abstraction that are relevant to your topic."
- **Grant Sanderson**, Dropbox profile, 2021-03-04 [V]: "resist the temptation to start with the general abstract thing and then populate it with examples to explain later." He adds: "Pretty much all textbooks and explanations do it the other way around ... because that's so tempting to do once you understand a topic."
- **Nicky Case**, "How I Make Explorable Explanations", 2017-09-20 [V]: "The very first thing you should do is give the reader a concrete experience." In the Stanford talk transcript, trick #2 is "Show, then tell" and the summary is "Concrete, then abstract." [V]
- **Bret Victor**, "Up and Down the Ladder of Abstraction", 2011-10 [V]: "The most powerful way to gain insight into a system is by moving between levels of abstraction." Insight is born "in the transitions between them," and "stepping down is as important as stepping up."
- **Julia Evans**, "Patterns in confusing explanations", 2021-08-19 [V]: pattern 9 is "starting out abstract" and pattern 11 is "no examples." She writes: "Leaving out examples makes it harder for the reader to relate the new terminology to their own experiences."
- **Amit Patel**, EDUC432 notes, 2023 [V]: "I usually present a simplified problem at beginning."
- **Steven Pinker**, via APS Observer, 2015 [V, secondary]: readers can follow work when they can "visualize the experiment, to follow the logic."

**Agreement.** Seven independent practitioners agree. This is the strongest consensus in the set.

**Implication.** Each mechanism explainer opens with one traced concrete instance, such as a real request with real values. The skill names the general rule only after that trace. Later scenes step back down to the instance.

### Principle 2. Make the viewer want the question first

**Advice.** Give the viewer a reason to care within the first seconds. The hook is a question or puzzle, not a list of facts. Each new idea also needs its own reason to appear.

- **Grant Sanderson**, SoME1 post, 2021-07-16 [V]: "It should be clear to the reader/viewer within the first 30 seconds why they should care."
- **Grant Sanderson**, SoME2 results video, 2022 [T]: motivation is the first of four judging criteria: "how well do you hook someone into the lesson as a whole?" He also asks whether each new idea feels like it has a good reason to be there. In the SoME1 video he says: "Try to let them be well motivated" (about definitions).
- **Grant Sanderson**, Dropbox, 2021 [V]: curiosity is "the hook of the video." Also: "The visual is heavily intertwined into the story, it is the prompt."
- **Nicky Case**, 2017 [V]: "you've got to make them love your question." The Stanford talk gives trick #1 [V]: "Just show them what made *you* care about that topic."
- **Josh Comeau**, thread [V]: "if your article doesn't provide value and/or entertainment right away, they'll bounce."
- **Derek Muller**, "Clickbait is Unreasonably Effective", 2021 [T]: "Making the title and thumbnail is at least half the job." Muller separates legitimate curiosity bait from teasers that "give you enough information to make you curious but not enough to satisfy that curiosity" and then fail to deliver.
- **Ros Atkins** (BBC explainers) [S]: "You need to set up the reason why you're asking the question before you then launch into the explanation."
- **Johnny Harris** (new channel) [S]: each episode starts from one discrete question, such as "Why is housing so expensive?"
- **Tom Scott** [T]: he structures videos to "land somewhere" and sometimes starts from the title and works backward.

**Agreement.** Seven or more practitioners agree. Muller adds a condition: the hook must be paid off.

**Implication.** Scene 1 states a concrete question about the mechanism within about 75 words (30 s). An example: "Why does this retry never fire?" The final scene answers that exact question.

### Principle 3. Link scenes by cause, not sequence ("but / therefore")

**Advice.** Join beats with "but" (a problem) or "therefore" (a consequence), not "and then." Causal links make the story feel consequential.

- **Nicky Case**, 2017 [V]: build up the ladder using "BUT" and "THEREFORE" rather than "and then." The Stanford talk gives trick #3 [V]: "If events aren't consequences of each other, they won't feel consequential."
- **Trey Parker and Matt Stone**, NYU talk [S]: replace "and then" with "but" or "therefore" between beats.
- **Randy Olson**, ABT template [S]: "And" sets context, "But" adds conflict, and "Therefore" resolves it. He calls it "easy to grasp but difficult to master."
- **Julia Evans**, pattern 13 "'what' without 'why'" [V]: "a weak 'why' is much better than no 'why'."

**Agreement.** Four sources, of which two are independent explainer-makers (Case, Evans). Parker/Stone and Olson are storytelling sources.

**Implication.** The skill should check each scene boundary for a "but" or "so" relationship to the previous scene. Each mechanism step needs a stated reason, either the problem it solves or the constraint that forces it.

### Principle 4. Confront the plausible wrong model

**Advice.** Learners arrive with wrong models. A clear, correct explanation can raise confidence in the wrong model. Name the misconception, show it failing, and then give the correct model. Confusion that the viewer resolves is productive.

- **Derek Muller**, 2011 video [T]: viewers who saw only correct information "get more confident in the ideas they were thinking before." Students called the plain video "clear concise and easy to understand," but scores rose only from 6.0 to 6.3 out of 26. In the misconception video, "increased mental effort translated into more learning." His conclusion: "we really have to tackle these misconceptions somehow."
- **Muller & Sharma**, 2012 abstract [V, paraphrased]: misconceptions create a false sense of understanding, which lowers mental effort. Videos that present common misconceptions helped, even without interactivity. The study covered over 1,000 students across three years.
- **Kulgemeyer & Wittwer**, 2022 RCT, n=149 [V]: a video built on misconceptions and a correct video produced "an equally high belief of understanding." The misconception group learned the misconceptions. Prior work found that "neither likes nor views reflect explaining quality."
- **CGP Grey**, 2013 [T]: "being confused and frustrated with the topic is a vital part of figuring out how to explain it to others." This is confusion on the author's side, a related point.
- **Julia Evans**, pattern 12 [V]: the failure is explaining the wrong way without saying up front that it is wrong. Showing the wrong way is fine if you flag it.

**Agreement.** Three independent sources (Muller, Kulgemeyer, Evans) plus Grey on the author side. The research evidence comes from physics education.

**Implication.** Add an optional "tempting wrong model" scene. Flag it as wrong in its first sentence, for example "You might expect X. That's not what happens." Then show where it breaks. Give an empathetic, rising emotion tag at the moment the model fails.

### Principle 5. Write for the ear

**Advice.** Listeners cannot re-read. Use one idea per sentence and active verbs. Avoid dependent clauses. Signpost transitions. Speak the script before you finalize it.

- **NPR Training** pages, 2015–2017 [S]: "Each sentence should only have one new idea in it." "The first rule of writing for your voice is to speak it before you write it." "If you wouldn't say it that way, don't write it that way." "Use a short, sharp sentence (a 'signpost') ... to mark a change." The pages also quote Jonathan Kern's *Sound Reporting*: "time goes in only one direction; listeners can't go back." NPR advises against packing the who/what/when/where/why into the opening. I could not open these pages, so treat the quotes as snippet-only.
- **Tom Scott** [T]: he writes "in roughly the same way I talk. I can write in my own voice."
- **Kurzgesagt**, process page [V]: scripts take "about a dozen drafts to cut away unnecessary bit and polish the final result."
- **Grant Sanderson**, SoME1 video [T]: "sound quality actually matters," although content matters more.

**Agreement.** NPR (institutional), Scott, and Kurzgesagt agree. This is standard broadcast practice.

**Implication.** Narration sentences should be short and carry one new idea each. Replace symbols and code tokens with their spoken form. Put a one-line spoken signpost at each scene start, for example "Now the cache misses." Before rendering, have the skill re-read the script aloud through TTS or a read-aloud pass and flag sentences that require a re-read.

### Principle 6. Cut to one idea and fewer concepts

**Advice.** Pick a narrow topic. Cut fluff. Introduce few concepts at a time. Quick understanding beats completeness.

- **Nicky Case**, Stanford talk trick #4 [V]: "at least 10% of your first draft will always be fluff."
- **Kurzgesagt** [V]: a dozen drafts "to cut away unnecessary bit."
- **Tom Scott** [T]: his one real skill is "taking a thousand pages of content and turning them into four paragraphs that tell a story."
- **Grant Sanderson**, SoME1 video [T]: "try to choose something much more esoteric and specific than you might be inclined to."
- **Julia Evans**, pattern 8 "introducing too many concepts at a time" [V].
- **Josh Comeau** [V]: "I try and prioritize quick wins, even if it comes at the expense of thoroughness."
- **Mayer coherence principle** [S]: people learn better when extraneous words, pictures, and sounds are excluded.

**Agreement.** Six practitioners plus Mayer.

**Implication.** Each explainer covers one mechanism. Each scene introduces at most one new term. After drafting, cut 10% of narration words before timing the scenes.

### Principle 7. Make the visual carry the idea, in sync with the words

**Advice.** The picture should be the explanation, not decoration. Show each element when the narration names it. Use cues such as arrows and highlights to signal what matters. Do not repeat the narration as on-screen text.

- **Grant Sanderson**, Dropbox [V]: ideas feel "more sensible and understandable" with "a nice visual behind it" than when "driven by notation." "The visual is heavily intertwined into the story, it is the prompt."
- **Grant Sanderson**, Dwarkesh [V]: he does not write a script first. "I start by laying out all of the animations and stuff that I want in a timeline."
- **Kurzgesagt** [V]: the team deliberates "over the best visual metaphors and ideas for each scene in the sketching phase."
- **Johnny Harris** [S, third-party analysis]: he writes with a visual idea in mind first.
- **Julia Evans**, pattern 4 "fun illustrations on dry explanations" [V]: decoration cannot rescue a dry explanation.
- **Mayer** [S]: temporal contiguity means words and the matching picture appear at the same time. Signaling means cues highlight the organization. Redundancy means graphics plus narration beat graphics plus narration plus on-screen text. Modality means spoken words beat printed words with graphics.

**Agreement.** Sanderson, Kurzgesagt, Evans, and Harris (snippet), plus Mayer's research.

**Implication.** Key each draw-on to the word that names the element. Highlight or arrow the one active element per beat. Keep on-screen text to labels, not narration sentences. Captions-only mode is an exception for accessibility. Every diagram element must show a part of the mechanism. Drop decorative drawings.

### Principle 8. Know the reader and beat the curse of knowledge

**Advice.** State the assumed background. Define jargon. Do not assume outdated or inconsistent knowledge. Use analogies to existing mental models, and say where they break.

- **Grant Sanderson**, SoME1 post [V]: "Jargon should be explained." Entrants should mention the assumed background level.
- **Julia Evans** [V]: pattern 1 is outdated assumptions about the audience, pattern 2 is inconsistent expectations of knowledge, pattern 3 is strained analogies, and pattern 6 is jargon that means nothing. Her fix for pattern 2: write for one specific person.
- **Steven Pinker**, via APS [V, secondary]: "It simply doesn't occur to the writer that readers haven't learned their jargon." He calls it "the chief contributor to opaque writing."
- **Josh Comeau** [V]: "Analogies are great because you can copy/paste a mental model they already have," but "make sure they understand the differences." Also: "take advantage of stuff the learner already knows."

**Agreement.** Four independent sources.

**Implication.** The script header records the target viewer, such as "backend dev who knows HTTP but not QUIC". The skill checks each term against that viewer. Each analogy gets one sentence on where it breaks.

### Principle 9. Use realistic examples

**Advice.** Build examples from real usage, then strip irrelevant detail. Toy examples that nobody would write make the concept harder to picture.

- **Julia Evans**, 2021-07-08 [V]: "start with real code that you wrote and then remove irrelevant details"; "good examples are realistic." Pattern 5 in the confusing-explanations post is "unrealistic examples."
- **Amit Patel**, 2018 [V]: readers mostly want solutions to problems they are trying to solve.

**Agreement.** Two sources. Evans is a primary source for software topics.

**Implication.** The concrete instance in Principle 1 comes from the user's actual codebase or a realistic trace. Do not use foo/bar.

### Principle 10. Content matters more than polish

**Advice.** Topic choice and a clear insight matter more than production quality.

- **Grant Sanderson**, SoME1 video [T]: "content is king." Production polish is "secondary to making sure you've chosen an actually good topic."
- **Grant Sanderson**, SoME1 results [V]: "lower production quality but highly interesting lessons still managed to bubble toward the top." "As long as it's a solid idea, with an engaging explanation, people will resonate with it."
- **Grant Sanderson**, SoME2 [T]: under novelty, stylistic originality is the less important half. What counts is content that "would have been very hard to find elsewhere on the internet."
- **Grant Sanderson**, Dwarkesh [V]: "It's okay that most of them suck."

**Agreement.** Sanderson only, but repeated across his judging of thousands of entries. The large-studio practice of Kurzgesagt and Ciechanowski is a counterweight. See Disagreements.

**Implication.** Spend the generation budget on correct mechanism content, example choice, and the hook before animation flourishes.

### Principle 11. Simplify honestly and say so

**Advice.** Every explainer simplifies. Simplify to build a foundation, document the simplification, and warn that the result can feel like deeper knowledge than it is.

- **Kurzgesagt**, "...And We'll Do it Again", 2021-12-07 [T]: science communication "has to use lies to children to some degree." "By beginning at a place of oversimplification, you're building a framework, a foundation." It can also "give you a false sense of security and an illusion of deep knowledge." Their mitigation: "read as many primary sources as possible, talk to multiple experts, and document our simplifications."
- **Julia Evans**, pattern 7 "missing key information" [V]: some explanations omit "the most important idea to understand the concept." A simplification must not cut the core idea.
- **Grant Sanderson**, JPBM lecture "Math's pedagogical curse", 2023 [S, third-party summary]: learners want an authentic encounter with the real material, so do not talk down.

**Agreement.** Kurzgesagt and Evans, plus Sanderson (snippet).

**Implication.** When a scene omits a real complication, add one spoken line such as "In practice there's also X, which we'll skip." The skill should keep a list of simplifications, possibly shown under the player.

### Principle 12. Test with real viewers early

**Advice.** You cannot predict what confuses others. Test drafts on representative people early and often.

- **Nicky Case**, Stanford talk trick #5 [V]: "we should do real tests, early and often."
- **Steven Pinker**, via APS [V]: "You'd often be surprised to find that what's obvious to you is not obvious to anyone else." Show drafts to a representative reader.
- **Grant Sanderson**, SoME4 [S]: he weights whether teachers think an entry would help their students.

**Agreement.** Three sources.

**Implication.** Add a review pass with a fresh agent that has only the target-viewer profile and the script. The agent reports where it lost the thread and what it would mispredict. The repo's existing "ask an agent about a confusing moment" feature can feed confusion reports back into revisions.

### Principle 13. Watching alone gives limited understanding

**Advice.** Engaging explanations feel like understanding. Without retrieval, prediction, or practice, viewers retain little and may not notice their gaps.

- **Andy Matuschak**, "Why books don't work", 2019 [V]: he calls the belief in direct knowledge transfer "transmissionism." "Lectures, as a medium, have no carefully-considered cognitive model at their foundation." He describes readers who "certainly thought [they] understood."
- **Andy Matuschak**, Dwarkesh, 2023-07-12 [V]: "People will watch Grant Sanderson spend an hour going through some explanation of an esoteric math problem ... The issue is that they will not walk away from that interaction with much understanding."
- **Grant Sanderson**, Dwarkesh, 2023 [V]: "what's probably most important to getting people to actually learn something is not the explanation." Also: "Putting in the work with the calculations is where you solidify all of those underlying intuitions." And: "the job of an educator is not to like take their knowledge and shove it into the heads of someone else."
- **Kulgemeyer & Wittwer** 2022 [V]: watching is often the only activity with explainer videos, so learners have no chance to notice an illusion of understanding. **Hörnlein & Kulgemeyer** 2025 [S]: high-level learning tasks after the video reduced that illusion.
- **Bret Victor**, 2011 [V]: an active reader "asks questions, considers alternatives, questions assumptions." Passive reading leaves readers who "blindly trust, or blindly don't."
- **Kurzgesagt**, 2021 [T]: the "illusion of deep knowledge" risk.

**Agreement.** Five or more independent sources, including the most famous explainer-maker (Sanderson) and the published research.

**Implication.** Put at least one pause-and-predict beat in the script. The narrator asks "what happens to the second request?", holds briefly, and then reveals. End with a question or task the viewer can try in their own code. Do not claim that the video teaches mastery.

### Principle 14. Know when a narrated explainer is the wrong format

**Advice.** Video works best once someone already has a question. Content that people need to look up, explore, or check against a model fits text or interactives better.

- **Grant Sanderson**, Dwarkesh [V]: video "is there to answer something once someone has a question."
- **Amit Patel**, EDUC432 [V]: "not everything benefits from being interactive." In the 2018 post [V]: "The interactive parts are there to make the explanation better." A page should read as complete without interaction.
- **Bret Victor**, 2024 postscript [V]: he meant "a written argument whose assertions are backed by explorable computational models," not interactive teaching articles in general.
- **Amit Patel** quoting Victor [V]: "Most interactive widgets dump the user in a sandbox and say 'figure it out for yourself'." That is not an explanation. "The author must guide the reader."
- **Josh Comeau** [V]: "If you stick with a single content type, learners will go on 'autopilot'." He alternates formats.

**Agreement.** Four sources.

**Implication.** The skill fits a single causal mechanism with a story: request flow, state machine, or algorithm. For reference material, API surfaces, or configuration matrices, it should suggest a teach-me page or docs. Pair each explainer with a text transcript or summary for lookup.

### Principle 15. Keep it short and segmented

**Advice.** Attention fades. Keep units short and let the viewer control pacing.

- **Josh Comeau** [V]: "Our mind wanders during long videos. So I keep them short."
- **Mayer segmenting principle** [S]: user-paced segments beat one continuous unit.
- **CGP Grey**, 2013 [T]: "every minute of final video you see takes me between 10 and 20 hours of writing and animating." This shows how much effort short videos take.

**Agreement.** Two sources plus Mayer.

**Implication.** Keep the 2–5 minute cap. Keep scenes at about 20–40 s, which is 50–100 words at 150 wpm. Each scene should be seekable as a unit. The repo already supports arrow-key skipping.

---

### Ranked top 10 implications for the skill

1. **Open with a concrete trace and add the abstraction later (P1).** Seven practitioners agree. Scene 1 or 2 walks one real instance through the mechanism with real values. The general rule is named afterward.
2. **Pose a concrete question within the first 30 s and answer that exact question at the end (P2).** Seven or more practitioners agree. The hook must be paid off.
3. **Add a pause-and-predict beat, and end with something the viewer can try (P13).** Without an active step, viewers keep an illusion of understanding (Matuschak, Sanderson, Kulgemeyer).
4. **Include a flagged "tempting wrong model" scene when one exists (P4).** Muller's research shows that a clear, correct explanation alone can raise confidence in wrong models.
5. **Sync each draw-on to the spoken word that names it, and keep on-screen text to labels (P7).** This follows Mayer's contiguity and redundancy principles and Sanderson's "the visual is the prompt."
6. **Narrate in short sentences with one new idea each, and signpost each scene start (P5).** This is NPR broadcast practice. TTS cannot recover from a long dependent clause.
7. **Join scenes with "but" or "so", and give every step a "why" (P3).** Case, Evans, and Olson agree. The skill can check transitions mechanically.
8. **Cover one mechanism, one new term per scene, and cut 10% of the draft (P6).** Case, Kurzgesagt, Scott, Evans, and Comeau agree.
9. **Declare the target viewer, define terms against that profile, and say where each analogy breaks (P8).** Sanderson, Evans, Pinker, and Comeau agree.
10. **Run a fresh-agent "confused viewer" review before rendering, and list the simplifications (P11, P12).** Case, Pinker, and Kurzgesagt agree. This automates "test early" and "document your lies-to-children."

### Disagreements and tensions

- **Engagement compared with understanding.** Comeau says "the *most* important thing is that people enjoy it!" Sanderson ranks motivation first. Matuschak says Sanderson's own viewers "will not walk away ... with much understanding." Muller and Kulgemeyer show that "clear concise" and liked explanations can leave misconceptions intact. Sanderson agrees with part of this ("not the explanation" is what makes people learn). *Resolution for the skill:* engagement is necessary but not sufficient. Pair the hook with prediction and misconception beats.
- **Script first compared with visuals first.** Kurzgesagt says "Our scripts are the backbone of our videos." Tom Scott writes "every word" in advance. Sanderson does not write a script first and lays out animations in a timeline. Johnny Harris reportedly starts from visuals [S]. *For the skill:* the pipeline is script-first by necessity because TTS sets the timing. Add a step that sketches the visual for each scene before the narration is final, so the picture can be the prompt.
- **Production quality.** Sanderson says polish is secondary and low-production entries won. Kurzgesagt spends weeks to years per video, and Ciechanowski's articles reportedly embed about 50 demos each [S, HN commenters]. *For the skill:* polish is cheap when generated, but correctness and example choice decide quality.
- **How far to simplify.** Kurzgesagt defends "lies to children" as scaffolding. Sanderson's JPBM lecture [S] warns against talking down. Evans warns against dropping the key idea. *For the skill:* simplify the periphery, never the core causal step, and state each omission.
- **What counts as interactive.** Victor originally meant model-backed arguments the reader can challenge, and he says the term drifted. Patel says interaction is optional and the text must stand alone. Case builds guided explorables that end in a sandbox. *For the skill:* a narrated linear explainer sits at the "guided" end. Do not present it as an explorable.
- **Curiosity-gap hooks.** Muller embraces strong packaging ("half the job") but separates legitimate bait from broken promises. Evans warns that a friendly surface on a dry explanation misleads. NPR advises against front-loading facts. *For the skill:* hook with a real question about the mechanism, not with withheld drama, and answer it.
- **Hook speed compared with setup.** Comeau and Scott want value in the first seconds. Atkins wants the reason for the question set up first. These fit together: the first 30 s should establish why the question matters.

### Gaps and unverified items

- **No primary advice found** for Steve Mould, Sebastian Lague, Primer, Bartosz Ciechanowski (HN commenters only, no comments from him), Amelia Wattenberger, Johnny Harris or Vox (third-party analysis only), Hamish Todd (only a 2017 Game Developer post title), or CGP Grey's scripting process (Cortex ep. 9 covers it, but no transcript was found).
- **NPR quotes** come from search snippets. training.npr.org redirects to npr.org, which timed out.
- **Trey Parker/Stone, Olson, Atkins, Mayer, Hörnlein 2025, and the Sanderson JPBM lecture** content rests on secondary summaries.
- **Muller's TEDxSydney 2012 talk** is the classic "confusion" source. I verified the 2011 Veritasium video and the 2012 paper abstract instead.
- **Tom Scott's Waveform interview date** is unverified.
- **Quote fidelity.** WebFetch passes pages through a summarizer. Re-check exact wording against the linked pages before quoting any line in user-facing text.

### Links

- Sanderson, SoME1 post: https://www.3blue1brown.com/blog/some1
- Sanderson, SoME1 announcement transcript: https://rosetta.to/u/3blue1brown/make-math-videos-summer-of-math-exposition-announcement
- Sanderson, SoME1 results: https://www.3blue1brown.com/blog/some1-results
- Sanderson, SoME2 results video transcript: https://rosetta.to/u/3blue1brown/what-makes-a-great-math-explanation-some2-results
- Sanderson, Dropbox profile: https://blog.dropbox.com/topics/work-culture/grant-sanderson-channels-his-passion-for-math-into-marvelously-i
- Sanderson, Dwarkesh: https://www.dwarkesh.com/p/grant-sanderson
- Muller, Khan Academy video transcript: https://rosetta.to/u/veritasium/khan-academy-and-the-effectiveness-of-science-videos
- Muller & Sharma 2012: https://openjournals.library.sydney.edu.au/IISME/article/view/6345
- Muller, Clickbait video transcript: https://rosetta.to/u/veritasium/clickbait-is-unreasonably-effective
- Kulgemeyer & Wittwer 2022: https://pmc.ncbi.nlm.nih.gov/articles/PMC8932681/
- Hörnlein & Kulgemeyer 2025: https://arxiv.org/abs/2512.02824
- Case, How I make explorables: https://blog.ncase.me/how-i-make-an-explorable-explanation/
- Case, Stanford talk: https://ncase.me/StanfordTalk/transcript.html
- Victor, Explorable Explanations: http://worrydream.com/ExplorableExplanations/
- Victor, Ladder of Abstraction: http://worrydream.com/LadderOfAbstraction/
- Patel, Thoughts on explorables: https://simblob.blogspot.com/2018/05/thoughts-on-explorable-explanations.html
- Patel, EDUC432 notes: https://www.redblobgames.com/x/2306-educ432/
- Evans, Confusing explanations: https://jvns.ca/blog/confusing-explanations/
- Evans, Good examples: https://jvns.ca/blog/2021/07/08/writing-great-examples/
- Matuschak, Why books don't work: https://andymatuschak.org/books/
- Matuschak, Dwarkesh: https://www.dwarkesh.com/p/andy-matuschak
- Comeau thread: https://threadreaderapp.com/thread/1381611771841146883.html
- Kurzgesagt process: https://kurzgesagt.org/youtube/
- Kurzgesagt, "...And We'll Do it Again" transcript: https://rosetta.to/u/kurzgesagt/and-we-ll-do-it-again
- Grey Q&A transcript: https://rosetta.to/u/cgpgrey/grey-answers-your-most-common-questions
- Tom Scott, Waveform transcript: https://rosetta.to/u/waveform/how-tom-scott-makes-videos
- NPR Training search results (snippets): https://training.npr.org/2015/03/20/campfire-tales-the-essentials-of-writing-for-radio/
- Olson ABT: https://ncse.ngo/and-therefore-randy-olson-and-art-science-storytelling-part-1
- Pinker via APS: https://www.psychologicalscience.org/observer/the-curse-of-knowledge-pinker-describes-a-key-cause-of-bad-writing
- Mayer principles summary: https://services.dartmouth.edu/TDClient/1806/Portal/KB/PrintArticle?ID=171655

# Appendix C

## Visual explanation research: diagrams, progressive build-up, and narrated animation

Research date: 2026-10-28. The research serves two skills:

- `excalidraw-skill`: claim-first briefs, overviews of 7 boxes or fewer, labeled arrows, color with meaning, and a lint, render, and self-critique loop.
- `explainer`: hand-drawn diagrams that build element by element as the narration names each element. The skill also has other looks: kinetic type, blueprint, and terminal.

### Verification legend

- **[full text]**: I read the original paper or file, or the relevant sections of it.
- **[abstract]**: I read the original abstract, README, or official page.
- **[secondary]**: the claim comes from a meta-review table or a citing paper that I read in full. The original was not read.
- **[snippet]**: the claim comes only from search-result snippets or third-party summaries. Treat it as unverified.

---

### A. Whiteboard and drawing-hand animation

#### A1. Watching a diagram being drawn beats seeing it finished, in short STEM lessons

- **Claim:** A narrated lesson teaches more when the drawings are produced on screen during the narration than when the same finished drawings appear with the same narration.
- **Evidence:**
  - Fiorella, Stull, Kuhlmann & Mayer (2019), *J. Educ. Psych.* 111(7), 1162–1171, doi:10.1037/edu0000325 **[abstract]**. Experiment 1 used a kidney lesson. Dynamic drawings without a visible instructor beat static, already-drawn drawings on the posttest (d = .54). Experiment 2 showed that eye contact through a transparent whiteboard beat a conventional whiteboard (d = .54). Instructor visibility alone added nothing.
  - Fiorella & Mayer (2016), *J. Educ. Psych.* 108, 528–546, "Effects of observing the instructor draw diagrams on learning from multimedia messages" **[snippet]**. This was a Doppler-effect lesson. Watching the instructor's hand draw beat already-drawn diagrams on transfer (d ≈ 0.35). Drawing with the hand removed lost the benefit (d ≈ −0.16). A full instructor body did worse than the hand alone (d ≈ 0.36 favoring the hand). Computer-animated diagrams that mimicked drawing did not differ significantly from static diagrams (d ≈ 0.33, not significant). These numbers come from the dissertation abstract via snippets. The number of experiments (4 or 5) is unclear.
- **Boundary conditions:**
  - The lessons were short (1–3 min), causal STEM topics, with college students.
  - The 2016 hand-removed and computer-animated conditions are the closest match to our case: no hand, programmatic draw-on. They did *not* reliably beat static diagrams. The drawing-hand benefit may come from social or gesture cues, not from the progressive reveal itself.
  - The "Fiorella & Mayer 2017" study named in the brief is probably the 2019 JEP paper, which was published online in 2018. I found no separate 2017 drawing-hand paper.
- **Implication (explainer):** A synced draw-on is a plausible but unproven gain over a static picture. Its value comes from pacing attention, so tie each reveal to the narration. Do not count on "hand-drawn" itself to teach.

#### A2. Whiteboard animation beats slides and filmed lectures, but not audio alone

- **Claim:** Whiteboard animations improved comprehension compared with narrated slides and on-stage lectures. Audio-only came second and did not differ significantly from the whiteboard animation.
- **Evidence:**
  - Türkay (2022), *AJET* 38(5) **[full text]**. Mechanical Turk participants (N = 299) saw a ~10-min social science lecture in one of four formats. Whiteboard animation beat slides (p = .005) and lecture (p = .006) on multiple-choice questions. "There were no significant differences between other groups." Audio-only and whiteboard groups reported more enjoyment and engagement.
  - The author adds that "aesthetically pleasing static drawings (as shown to the slides group) are not sufficient to aid learning."
  - Türkay (2016), *Computers & Education* 98, 102–114, doi:10.1016/j.compedu.2016.03.004. It covered physics topics, retention, and subjective experience. **The abstract is elided by the publisher.** The 2022 paper cites it for enjoyment and for the dynamic-drawing benefit.
  - The Wikipedia summary says "little to no compelling experimental evidence" that whiteboard animations are more effective in learning, motivation, or persuasion **[snippet]**.
- **Boundary conditions:** Each study tested one presenter's materials with an online sample, and engagement was self-reported. Slides with static art did *worse* than audio alone, which suggests that badly synced visuals can cost more than they add.
- **Implication (explainer):** The narration carries most of the learning. A visual must earn its place by showing structure the voice cannot. A pretty static scene beside the narration may hurt.

#### A3. The drawing hand: motivation, not clearly learning

- **Claim:** A hand that draws content raised intrinsic motivation compared with a hand that pushes content in. Earlier work treats the hand as a possible seductive detail.
- **Evidence:** Smart Learning Environments (2023), doi:10.1186/s40561-023-00258-6, N = 84, with three conditions: hand drawing, hand pushing, and no hand **[snippet]**. Krieglstein et al. (2023), *Computers & Education* 194, 104702, tested segmentation and metacognitive prompts in whiteboard animations **[snippet, no findings read]**.
- **Implication (explainer):** Do not add a cursor or hand sprite to the Excalidraw look. The evidence for it is mixed, and the stroke draw-on already supplies the motion cue.

#### A4. Wiseman's "doodle" study is industry-commissioned and unreviewed

- **Claim:** A scribed version of a talking-head video, with identical audio, gave "15% better retention" and was "33% more entertaining."
- **Evidence:** Richard Wiseman ran an online experiment for Sparkol (VideoScribe) and Cognitive Media. It was reported on vendor blogs and dated about 2012, not 2016 **[snippet]**. I found no peer-reviewed paper and no sample size.
- **Implication:** Do not cite it as evidence.

#### A5. Tablet drawing engages more than slides (observational)

- **Claim:** Khan-style tablet-drawing tutorials kept edX viewers watching longer than PowerPoint slides. Shorter videos were much more engaging.
- **Evidence:** Guo, Kim & Rubin (2014), L@S, 6.9M sessions, observational **[full text, abstract and headline]**. Their recommendation: "Introduce motion and continuous visual flow into tutorials."
- **Boundary conditions:** The study measured watch time, not learning, and was confounded by course and instructor.
- **Implication (explainer):** This supports continuous visual flow and the 2–5 minute cap.

#### A6. Meta-analytic picture: animation helps only when the motion carries content

- **Claim:**
  - Animations beat static pictures by a small amount overall.
  - Representational animations (the motion *is* the content) help.
  - Decorational animations do not.
- **Evidence:**
  - Höffler & Leutner (2007), *Learning and Instruction* 17, 722–738: 26 studies, d = 0.37. Representational animation d = 0.40. Decorational animation d ≈ −0.05 to 0.05, n.s. Procedural-motor content gained most **[abstract + secondary via Noetel 2022]**.
  - Berney & Bétrancourt (2016), *Computers & Education* 101, 150–167: 61 studies, 140 comparisons, g = 0.23. Effects were larger for factual than conceptual knowledge, larger with audio commentary, and larger under system pacing **[secondary, Noetel 2022 table]**.
  - Ploetzner, Berney & Bétrancourt (2021), *Instructional Science*: in a re-analysis, animation is "considerably more effective" when learners must learn the *specifics of change* **[snippet/abstract]**.
  - Noetel et al. (2022), *Review of Educational Research* 92(3), 413–454: an overview of 29 reviews, 1,189 studies, and 78,177 participants **[full text]**. The largest benefits came from temporal/spatial contiguity and signaling. "Good design was more important for more complex materials, and in system-paced environments (e.g., lectures)."
- **Implication (both):** Animate an element only when its appearance or motion means something: a step happens, a message flows, a state changes. A narrated, system-paced video is the setting where design discipline matters most.

---

### B. Progressive build-up, animation versus static, cueing, contiguity, and contrast

#### B1. Animation often fails because it is too fast, and because people think in steps

- **Claim:**
  - Animations of complex systems rarely beat *equivalent* static graphics.
  - Apparent wins usually came from extra information or from interactivity.
  - Animations violate the Apprehension Principle because they are too fast or complex to perceive.
  - "Many continuous events are conceived of as sequences of discrete steps."
- **Evidence:** Tversky, Morrison & Bétrancourt (2002), *IJHCS* 57, 247–262 **[full text, abstract + §3–4]**. Two quotes:
  - "If motion is conceived of in discrete steps instead of continuously, then the natural way of conveying it is to portray it in discrete steps."
  - Multiple diagrams "easily allow comparison and reinspection," whereas "animations are fleeting."
  - The paper also defines the Congruence Principle: the external structure should match the desired mental structure. Its example: routes are conceived as turns, so draw turns.
- **Boundary conditions:** The review covers complex mechanical, biological, and computational systems. The authors restrict their conclusions to those. They name real-time changes and reorientations as promising uses.
- **Implication (explainer):**
  - Build each scene as discrete, named steps that hold, not as continuous motion.
  - End each scene on a complete static diagram that stays on screen.
  - Keep pause, seek, and skip controls, because interactivity is the main remedy the paper names. The player already has them.
- **Implication (Excalidraw):** The diagram's structure must match the mental model the claim names. A pipeline is a left-to-right chain. A decision is a fork.

#### B2. Static media can beat narrated animation

- **Claim:** Paper-based static diagrams with printed text matched or beat computer narrated animations, across four topics: lightning, toilets, ocean waves, and brakes.
- **Evidence:** Mayer, Hegarty, Mayer & Campbell (2005), *J. Exp. Psych.: Applied* 11(4), 256–265, 4 experiments **[abstract/snippet]**. The authors propose that static media reduce extraneous processing and invite germane, active processing. Hegarty (2004), *Learning and Instruction* 14, 343–351, argues that realism is not always better and that "distorting reality can sometimes aid understanding" **[abstract]**.
- **Implication (both):** Every explainer scene's final frame must work as a good static diagram. Ship the static diagram as well, for reinspection: the teach-me page or the scene sheet.

#### B3. Signaling or cueing helps, most for novices and when the cue is synced

- **Claim:** Cues that direct attention, such as color, arrows, highlighting, and motion, improve learning. Dynamic cues and low-prior-knowledge learners gain most.
- **Evidence (all via Noetel 2022 table [full text], originals [abstract]):**
  - Alpizar, Adesope & Wong (2020), *ETR&D* 68(5): 29 experiments, d = 0.38. Multimedia d = 0.63. Low prior knowledge d = 0.47. Dynamic (moving or animated) signals d = 0.43.
  - Richter, Scheiter & Eitel (2016), *Educational Research Review* 17, 19–36: 27 studies, r = 0.17. Low prior knowledge r = 0.19. High prior knowledge r = −0.08, which suggests cues can be redundant for experts.
  - Schneider, Beege, Nebel & Rey (2018), *Educational Research Review* 23, 1–24: 103 studies, transfer g = 0.53, retention g = 0.33, cognitive load reduced g = 0.25. Text signaling helped more than graphic signaling. The effect was consistent across prior-knowledge levels and pacing. This partly contradicts Richter.
  - de Koning, Tabbers, Rikers & Paas (2009), *Educ. Psych. Review* 21(2), 113–140 **[abstract]**. It is a framework of cue functions: selection, organization, and integration. Cues help *selection* most reliably. Cues for animation should be designed for animation, not copied from static graphics.
  - de Koning et al. (2007), *Applied Cognitive Psychology* 21, 731–746 **[abstract snippet]**. A spotlight cue in a cardiovascular animation improved comprehension and transfer, even for uncued content. Follow-ups found mixed results: the 2010 eye-tracking study and the 2011 speed study showed no cueing effect.
  - Boucheix & Lowe (2010), *Learning and Instruction* 20, 123–135 **[abstract snippet]**. In a piano-mechanism animation, *spreading-colour* cues along the causal path beat arrow cues and no cues. The cues worked only when "coordinated in both space and time" with the relevant events.
  - Lowe & Boucheix (2008, Diagrams LNCS 5223) **[abstract]**. Realistic animations make learners miss "high relevance information that has low intrinsic perceptual salience."
- **Implication (explainer):**
  - The word-cued reveal is a dynamic signal. Fire it on the word that names the element.
  - Prefer a cue that travels along the causal path, such as an arrow drawing on or a highlight spreading along a flow, over a static pointer.
  - Make the element that matters salient, even when it is small.
- **Implication (Excalidraw):** Give the claim's key element the strongest contrast. Low-relevance context gets low contrast.

#### B4. Labels belong on the diagram, not in a legend

- **Claim:** Placing text next to the part it describes (spatial contiguity) and narrating while the part shows (temporal contiguity) give some of the largest effects in multimedia learning.
- **Evidence:**
  - Ginns (2006), *Learning and Instruction* 16(6), 511–525: 50 studies, overall d = 0.85, spatial d = 0.72, temporal d = 0.78. The effect was larger for high element interactivity (d = 0.78) than for simple materials (d = 0.28) **[secondary via Noetel 2022, full text]**.
  - Schroeder & Cenkci (2018), *Educ. Psych. Review* 30, 679–701: 58 comparisons, g = 0.63 **[secondary via Noetel 2022]**.
  - Noetel 2022 frames this directly: "label images directly, rather than using legends, where learners have to connect the legend to the image."
  - Beege et al. (2019) found that a medium distance can beat a minimal one **[snippet]**. Labels must not collide with the shapes.
- **Tension with C4:** C4 requires a key/legend on every diagram (see C2). Reconciliation: label elements and arrows directly. Use a legend only for notation, such as what a dashed border or a color means, and keep it small.
- **Implication (Excalidraw):** Label each arrow on the arrow and each box inside the box. Put a color legend only when color encodes a category the labels do not already state.
- **Implication (explainer):** Temporal contiguity means each element appears *while* the voice names it, not seconds before or after. Narration and picture must overlap.

#### B5. Narration and visual timing

- **Claim:** Simultaneous narration and animation beat successive presentation (narration then picture, or picture then narration).
- **Evidence:**
  - Mayer's temporal contiguity chapter reports 8 of 8 tests, median d = 1.31 **[snippet]**. Mayer et al. (1999) found the effect only with longer segments **[snippet]**.
  - Baggett (1984), *J. Educ. Psych.* 76(3), 408–417, tested lead and lag offsets **[citation only, findings not verified]**. A common secondary claim says a visual leading by a few seconds is tolerated and narration leading is worse. I could not confirm it.
  - The Hermes manim-video skill doc (practitioner) recommends that the visual appear "slightly before the narration describes it" **[snippet]**.
- **Implication (explainer):** Fire the reveal on or just before the cue word. A lead of 0–300 ms is a reasonable default, but no study I verified sets this number. Never fire the reveal after the word ends.

#### B6. Pop-out, layering, and the smallest effective difference

- **Claim:**
  - A single strong feature difference (color, size, motion, shape) pops out pre-attentively.
  - Conjunctions of features do not pop out.
  - Secondary elements should be muted with the smallest effective difference.
- **Evidence:**
  - Ware, *Visual Thinking for Design* (2008) **[snippet: review and lecture slides]**. Use "a different channel for each type of information." Motion is a strong pop-out channel.
  - Tufte, *Visual Explanations* (1997), chapter "The smallest effective difference": "make all visual distinctions as subtle as possible, but still clear and effective" (p. 73) **[snippet]**. *Envisioning Information* (1990) covers layering and separation, and "1 + 1 = 3" (unintended interactions between adjacent marks) **[snippet]**.
- **Implication (Excalidraw):**
  - Color with meaning means one accent hue for the claim and neutrals for everything else.
  - Use at most one channel per meaning.
  - Use gray, thin strokes for context.
- **Implication (explainer):** Motion is the strongest pop-out channel. Move or draw one thing at a time, and keep everything else still.

#### B7. Hand-drawn style signals "provisional" and costs precise reading

- **Claim:** Sketchy rendering may raise engagement and willingness to critique. It impairs judgments of area and ratio as sketchiness grows.
- **Evidence:** Wood, Isenberg, Isenberg, Dykes, Boukhelifa & Slingsby (2012), *IEEE TVCG* (InfoVis) **[abstract]**. The engagement result is framed as "may be increased."
- **Implication (Excalidraw):** The hand-drawn look suits mechanisms and concepts. Do not use it to encode quantities by size. Choose a crisp look, such as Swiss or blueprint, when the scene compares magnitudes.

#### B8. Segment the material

- **Claim:** Meaningful, learner-paced segments beat one continuous unit.
- **Evidence:** Rey et al. (2019), *Educ. Psych. Review* 31, 389–419: 56 studies, 88 comparisons, small to medium effects for retention and transfer **[abstract snippet]**. Noetel 2022 lists segmentation as robust **[full text]**.
- **Implication (explainer):** Use one idea per scene with a hold at its end. The 5-second skip and seek controls make the explainer partly learner-paced.

---

### C. Practitioner craft

#### C1. Diagrams should argue, and their structure should carry the meaning

- **Claim:** "Diagrams should ARGUE, not DISPLAY." "The Isomorphism Test: if you removed all text, would the structure alone communicate the concept?" Technical diagrams need real names and concrete evidence artifacts, not "Input → Output."
- **Evidence:** coleam00/excalidraw-diagram-skill `SKILL.md` **[full text, read via gh]**. It is a widely shared Claude Code skill with a render-to-PNG, inspect, and edit loop. A blog reports 2–4 iterations, with arrow spacing as an example fix **[snippet]**.
- **Implication (Excalidraw):** This matches the claim-first brief. Add the isomorphism test to the self-critique: strip the labels and ask whether the shape still says the claim.

#### C2. C4 notation: titles, typed elements, one-way labeled arrows, consistent color

- **Claim:**
  - "Every diagram should have a title describing the diagram type and scope."
  - "Every line should represent a unidirectional relationship," with a specific label, not "Uses."
  - Acronyms must be understandable.
  - Color coding must be "consistent (within and across diagrams)," with printing and color blindness in mind.
  - A key explains the notation.
- **Evidence:** Simon Brown, c4model.com/diagrams/notation **[official page]**.
- **Boundary condition:** C4 does not set a box limit. The "≤7" rule is a skill heuristic (see Disagreements).
- **Implication (Excalidraw):** Lint for:
  - unlabeled arrows;
  - bidirectional arrows;
  - generic verbs ("uses", "calls" with no object);
  - inconsistent color meaning across the overview and the deep dive.

#### C3. Julia Evans: drawings summarize fast

- **Claim:** A comic conveyed a service-discovery post's main points in about 30 seconds. The prose took 15 minutes.
- **Evidence:** jvns.ca, "why cute drawings" (2016) **[snippet; reader anecdote]**. Her "How I write useful programming comics" (2020) exists. I could not fetch its URL (404), so the specific tips are unverified.
- **Implication:** This is a weak anecdote. It supports short labels and one idea per drawing.

#### C4. Maggie Appleton, Ralph Ammer, Dan Roam

- Maggie Appleton makes illustrated notes and visual metaphors for programming concepts, for example "React is a potato plant" **[snippet]**. No empirical claim.
- Ralph Ammer's TEDxTUM talk "How drawing helps you think" treats drawing as thinking **[snippet]**. I found no text-level rules.
- Dan Roam, *The Back of the Napkin* (2008): 6×6 rule. Each way of seeing has a default way of showing:
  - who/what → portrait;
  - how much → chart;
  - where → map;
  - when → timeline;
  - how → flowchart;
  - why → multivariable plot.
  - **[snippet]** The how and why pairings are less certain.
- **Implication (Excalidraw):** Pick the diagram form from the question the claim answers. "When" calls for a timeline, "how" for a flow, "where" for a map or topology. This is a useful brief field: `question: how|when|where|why|who|how much`.

#### C5. Arrows are the verbs of diagrams

- **Claim:** People read diagrams without arrows as structure and diagrams with arrows as function or causal sequence.
- **Evidence:** Heiser & Tversky (2006), "Arrows in comprehending and producing mechanical diagrams," *Cognitive Science* **[snippet]**. Alikhani & Stone (2018), COLING, "Arrows are the Verbs of Diagrams" **[title/abstract snippet]**.
- **Implication (both):** Use an arrow only for a real action or flow, and label it with a verb. In the explainer, *draw* an arrow on the verb of its sentence.

#### C6. Manim conventions: identity, ancestry, and transform versus cut

- **Claim (practitioner):** "The animation is only a proof if every frame is a well-formed diagram and every mobject has an ancestry. Nothing may appear, vanish, flip, or morph without a semantic reason." Glyphs keep identity. A symbol may glide, appear, or disappear, but "never smears into a different symbol." Transforms must match counts one to one, or Manim makes ghost duplicates.
- **Evidence:**
  - thomasahle/tensorgrad `paper/animations/SKILL.md` **[full text]**. It records lessons from about 40 review rounds on three videos:
    - Check *mid-transition* frames, not only settled ones.
    - Review at delivery resolution, because 480p hides 1–2 px defects.
    - "Each note usually generalizes: fix the instance, then apply the principle everywhere."
    - Semantic color stays "constant per object across formula AND diagram."
  - Hermes manim-video skill **[official doc page]**. Use `ReplacementTransform` instead of writing new text on top. Wait after every animation. Share color constants across scenes. Use opacity tiers: primary 1.0, context 0.4, grid 0.15.
  - I found **no verified Grant Sanderson quote** for "transform, don't cut." The phrase is community lore. 3b1b's practice of persistent objects is visible in the videos, but I did not source a statement.
- **Implication (explainer):** An element that persists across scenes keeps its position, color, and label. When a scene goes deeper, move or scale the existing element instead of redrawing a new one elsewhere.

---

### D. Continuity across scenes

#### D1. Object constancy in animated transitions

- **Claim:** Animated transitions that keep each element trackable improve graphical perception. Simple staging helps. Transitions should take about 1 s. Do not reuse a mark for a different entity.
- **Evidence:** Heer & Robertson (2007), *IEEE TVCG* (InfoVis), two controlled experiments **[full text]**. The design principles, verbatim headings:
  - "Maintain valid data graphics during transitions."
  - "Use consistent semantic-syntactic mappings."
  - "Respect semantic correspondence": marks should not be reused to show different data points.
  - "Avoid ambiguity."
  - "Group similar transitions."
  - "Minimize occlusion."
  - "Maximize predictability" (slow-in, slow-out).
  - "Use simple transitions": translation and expansion are easier than rotation.
  - "Use staging for complex transitions."
  - "Make transitions as long as needed, but no longer": about 1 s, with the experiments using 1.25 s.
  - Results: "simple staging proved beneficial, though the advantages are not overwhelming." Aggressive "do one thing at a time" staging was less preferred.
- **Related:** Bostock, "Object Constancy" (2012) **[official page]**. "Animation should only be used when it enhances understanding." Use a cross-fade or a cut between unrelated datasets. Use a key to track the same element.
- **Implication (explainer):**
  - Morph only when the element is the *same* entity.
  - Cut or cross-fade when the subject changes.
  - Run one simple stage at a time. Do not animate three properties at once.
  - Use eased transitions of 0.5–1.25 s.

#### D2. Hard cuts are fine when the action stays continuous

- **Claim:** In film, breaks in *action* drive the viewer's event boundaries. Cuts in space or time have only minor effects.
- **Evidence:** Magliano & Zacks (2011), *Cognitive Science* 35(8), 1489–1517, behavioral segmentation plus fMRI **[abstract]**.
- **Implication (explainer):** A scene change is a natural event boundary. Put it where the narration's idea changes, and the cut will feel natural. Within one idea, keep continuity.

#### D3. Reuse positions and colors from overview to deep dive

- **Claim:** Color and notation must stay consistent within and across diagrams (C4). Semantic color stays constant per object (tensorgrad). Heer's "consistent semantic-syntactic mappings" says the same.
- **Evidence:** C2, C6, and D1. I found no controlled study of overview-to-deep-dive position reuse in diagrams. The principle is an inference from object constancy.
- **Implication (both):** Give each entity one canonical id, color, and label across all scenes. The deep dive opens by zooming or expanding the overview box in place. Lint across scenes for the same label with a different color.

---

### E. LLM and agent explainer video and diagram generation (2024–2026)

#### E1. TheoremExplainAgent (Ku et al., ACL 2025, arXiv 2502.19400)

- **Design:** A planner agent writes the narrative and a coding agent writes Manim. Videos run longer than 5 min. The benchmark has 240 theorems **[full text via HTML]**.
- **Failure modes:** "Most of the videos produced exhibit minor issues with visual element layout": misaligned text, overlapping shapes, inconsistent sizes. Code failures were mostly API hallucinations in Manim, then LaTeX errors.
- **Fix loop:** Retrying on render errors raised success from 0–7% to 91–96% within 5 attempts. RAG over the docs *hurt* on hard theorems (73% vs 96%). The paper tested no VLM visual-critique loop.
- **Rubric:** 5 dimensions scored by GPT-4o/Gemini: Accuracy & Depth, Visual Relevance, Logical Flow, Element Layout, Visual Consistency. The score is their geometric mean.
- **Human agreement:**
  - Visual Relevance ρ = 0.72.
  - Element Layout ρ = 0.42.
  - Logical Flow ρ = 0.16.
  - Visual Consistency ρ = 0.17.
  - Accuracy ρ = 0.14.
  - VLM judges agree with humans on relevance, partly on layout, and barely on flow or consistency.
- **Implication (both):**
  - A deterministic render-error loop is high value.
  - VLM judgment of layout is only moderately reliable. Pair it with geometric lint.
  - Do not trust a VLM on narrative flow.

#### E2. Code2Video (Chen, Lin & Shou, arXiv 2510.01174, Oct 2025)

- **Design:** Planner, Coder, and Critic agents **[full text via HTML]**.
  - The Critic uses **visual anchors**: a 6×6 grid of fixed coordinates.
  - An **occupancy table** maps each element to its anchors and code lines, so a defect traces back to the code.
  - The Critic flags overlaps, lecture text occluded by animations, and large unused regions.
- **Ablation (Aesthetics / TeachQuiz):**

  | Variant | Aesthetics | TeachQuiz |
  |---|---|---|
  | Full system | 79.0 | 82.0 |
  | No planner | 38.1 | 40.5 |
  | No visual anchor | 69.2 | 55.2 |
  | No critic | 72.5 | 60.7 |
  | No external database (assets) | 68.1 | 52.0 |

  An 8×8 grid caused clutter and occlusion, so finer is not better.
- **Human study:** Humans "penalized layout errors more heavily than the VLM judge," because they notice brief occlusions that VideoLLMs miss. Longer videos reduced willingness to finish. Aesthetics and TeachQuiz correlated r = 0.971 across 5 systems.
- **Implication (Excalidraw):** Coarse grid placement plus an occupancy map beats free coordinates. This supports the `place.py` grid. Lint must check transient occlusion, not only final frames.
- **Implication (explainer):** Planning is the biggest lever: the storyboard and the cue plan come before drawing.

#### E3. OmniManim, "See Before You Code" (Li et al., Wuhan U., arXiv 2605.15585, May 2026)

- **Claim:** "Executable correctness does not imply render quality." The common failures are:
  - viewport overflow;
  - element overlap;
  - **remnant content from previous frames**;
  - scale mismatch.
- The paper says: "Post-render critique and VLM-based assessment can flag visible defects, but natural-language feedback is difficult to translate into precise coordinate adjustments." **[full text]**
- **Design:**
  - A Vision Agent plans keyframe bounding boxes with an *interpolation-aware* objective. Two valid keyframes can still overlap mid-tween.
  - A Repair Agent computes *deterministic CV diagnostics*: overlap, relation violation, boundary overflow, and compile failure.
  - The Repair Agent routes each failure to the owning stage. Layout goes to the vision agent, code to the coder, and temporal or remnant problems to the scene planner. It never regenerates the whole script.
- **Results:**
  - Removing the Vision Agent dropped Overlap 0.763 → 0.491 and Layout 0.931 → 0.614.
  - Removing the interpolation term mostly hurt Animation Continuity (−0.052).
  - In the human study (60 tasks, 4 raters each), overall scores were 81.0 vs 68.4 for Code2Video and 76.0 for GPT-5.4. Overlap avoidance improved +32.1 over Code2Video.
- **Implication (Excalidraw):** Prefer numeric lint (bounding-box overlap, off-canvas, label collision) over prose critique. Route each defect to a precise fix.
- **Implication (explainer):** Lint mid-transition frames and check that no element lingers after its scene ends.

#### E4. PhysicsSolutionAgent (Thole et al., arXiv 2601.13453, Jan 2026)

- **Design:** A one-shot VLM screenshot critique runs on 3 frames per scene (start, middle, end). The rubric covers overlap, readability, and content cut off at the edges **[full text via HTML]**.
- **Gains were tiny:**
  - Layout 3.64 → 3.66.
  - Scene-content alignment 3.31 → 3.53.
  - Max visual 3.98 → 4.05.
- **Limits:**
  - Humans found errors in "how the AI evaluates and interprets images."
  - Static screenshots miss animation smoothness and audio-visual sync.
  - The most frequent issue was verbosity and redundancy (36 occurrences).
- **Implication (both):** One VLM critique pass gives modest returns. Spend the effort on planning and deterministic checks. Sample frames at cue times, not only at scene start, middle, and end.

#### E5. Paper2Video / PaperTalker (Zhu, Lin & Shou, arXiv 2510.05096, NeurIPS 2025 workshop)

- **Design:** Slides, subtitles, cursor grounding (a GUI-grounding model plus WhisperX word timestamps), TTS, and a talking head **[full text via HTML]**.
- **Results:**
  - The cursor raised a localization QA score from 0.084 to 0.633. This supports word-synced pointing for "where is the thing being discussed."
  - Tree-search layout choice moved the VLM Design score only 2.73 → 2.85.
  - The paper did not validate the VLM layout judge against humans.
- **Metrics:**
  - PresentQuiz: a VideoLLM answers questions after watching.
  - PresentArena: pairwise preference.
- **Implication (explainer):** Word-level timestamps, which we have from ElevenLabs alignment, are the right sync primitive. Pointing at the element under discussion measurably helps the viewer find it.

#### E6. VideoAgent (Liang et al., arXiv 2509.11253, Sept 2025, v2 April 2026)

- **Design:** It mixes static slides and dynamic animations according to narration density. Per-chapter TTS produces narration with synced subtitles. A VLM judge rates "Synchronization" (6.58/10 for Gemini 2.5 Pro, lower than Visual Quality 8.03) **[abstract; sync scores snippet]**.
- **Implication (explainer):** Sync is the weakest dimension in agent videos. A word-cue design addresses it directly.

#### E7. Agent diagram generation and critic reliability

- **Sorted** (Zhang, Liu & Li, arXiv 2508.15222, Aug 2025) **[full text via HTML]**. "The primary bottleneck lies in the Critic VLM, which occasionally produces imprecise or inappropriate suggestions that can lead to worse candidates." A separate Judge VLM filters regressions. If no candidate improves, the step is reverted. The critic is limited to 1–3 changes per step.
- **PaperBanana** (Zhu et al., Google, arXiv 2601.23265, Jan 2026) **[abstract]**. Diagrams are refined iteratively by self-critique and rated on faithfulness, conciseness, readability, and aesthetics. I did not read its ablation.
- **Implication (Excalidraw):**
  - Self-critique can make a diagram worse.
  - Keep the previous render.
  - Accept a revision only if lint does not regress and a side-by-side comparison prefers it.
  - Limit each round to a few named fixes.

#### E8. GitHub agent skills: what they teach and what broke

- **remotion-dev/skills** (official) **[full text via gh]**:
  - The `video-layout.md` file says: "Decide what the viewer should notice first in each scene. Build the frame around that one thing." It also says: keep a safe area (80 px sides, 100 px top and bottom at 1080 wide), "Do not add redundant elements," headline ≥ 84 px, supporting text ≥ 44 px.
  - The markup rules say: drive every animation with `useCurrentFrame()`, because "CSS `transition` or `animation` will not render correctly."
  - The voiceover rule: generate TTS per scene, then size the composition to the audio duration.
  - Open issues show doc-rot as the main failure:
    - dead sub-skill links after install (#24);
    - frames-versus-seconds unit bugs (#15, #19);
    - inconsistent `spring()` guidance (#20).
- **thomasahle/tensorgrad animations skill** (C6): about 5–15 user review rounds per video. Shipped bugs recurred 4–5 times: wrong-end transforms and ghost objects from `Transform` versus `ReplacementTransform`.
- **Sync strategies seen in the wild** **[snippet]**:
  - audio first, where the TTS timeline drives the animation (Anvaya/Explanimator);
  - video first, with the audio stretched to fit (manim-mcp).
  - Audio first matches our design.
- **Implication (explainer):**
  - Pure functions of time match Remotion's rule. The explainer already does this.
  - Keep one unit (seconds) everywhere.
  - Test skill links after install.
  - Expect the user's first viewing to find issues an agent cannot see.

---

### Ranked top-10 implications

1. **Animate only what carries meaning (explainer).** Reveal an element when the narration names it. Draw an arrow when the narration says its verb. Never add decorative motion. Representational animation helps (d ≈ 0.40). Decorational animation does not (≈0). See A6.
2. **Sync reveals to the spoken word, on or slightly before it (explainer).** Temporal contiguity is among the largest effects (d ≈ 0.78). Cues work only when synced in space and time (Boucheix & Lowe 2010). Agent videos score worst on sync (VideoAgent). See B4, B5, B3, E6.
3. **Build in discrete steps that hold, and end every scene on a complete static diagram (both).** People conceive processes as steps. Static diagrams often match animation. Reinspection matters. Keep the scene sheet or static diagram available. See B1, B2.
4. **Lint geometry deterministically, and check mid-transition and cue-time frames, not only final frames (both).** Overlap, overflow, remnants, and transient occlusion are the dominant agent failures. Prose VLM critique converts poorly to fixes. One VLM pass gave about +0.02 on layout. See E1–E4, C6.
5. **Gate self-critique (Excalidraw).** Keep the prior render. Accept a change only when lint does not regress and a side-by-side comparison prefers it. Limit each round to 1–3 named fixes. VLM critics sometimes make diagrams worse (Sorted). VLM–human agreement on layout is only ρ ≈ 0.42. See E7, E1.
6. **Plan before drawing (both).** The claim-first brief, the diagram form chosen from the question (Roam), and the cue plan are the biggest lever. Removing the planner halved Code2Video's scores. See E2, C4.
7. **Place on a coarse grid with an occupancy map (Excalidraw).** Anchor grids beat free coordinates. A grid that is too fine (8×8) brings clutter back. See E2, E3.
8. **Label in place and use a legend only for notation (Excalidraw).** Label arrows with specific verbs, one direction per arrow, and give every diagram a title. Spatial contiguity gives g ≈ 0.63. C4 sets the arrow and title rules. See B4, C2, C5.
9. **Keep identity across scenes (both).** Give each entity one id, position, color, and label. Morph only the *same* entity, and cut or cross-fade on a change of subject. Use simple, staged, eased transitions of about 1 s, one property at a time. See D1–D3, C6.
10. **Use contrast sparingly (both).** Give one accent to the claim and mute the context (smallest effective difference). Move one thing at a time, because motion is the strongest pop-out channel. Do not use the sketchy look for size-encoded quantities. See B6, B7.

---

### Disagreements and open questions

- **Does progressive drawing itself help, or only the hand?** Fiorella & Mayer (2016) found that hand-free or computer-animated drawing did *not* reliably beat static drawings **[snippet]**. Fiorella et al. (2019) found that dynamic drawing without a visible instructor *did* beat static (d = .54) **[abstract]**. Our programmatic draw-on lies between the two. The benefit is plausible but unconfirmed.
- **Is whiteboard animation better than audio alone?** Türkay (2022) found no significant difference. Static slides did worse than audio alone. Visuals can subtract.
- **Signaling for experts:** Richter et al. (2016) found that the cue benefit vanishes for high prior knowledge (r = −0.08). Schneider et al. (2018) found the benefit consistent across knowledge levels. Rey et al. (2019) found that *segmenting* helps high prior knowledge more.
- **Legend versus direct labels:** C4 requires a key on every diagram. The contiguity research says to label in place. Reconciliation: label in place, and use a small key only for encodings.
- **"≤7 boxes":** No source I verified sets 7. Miller's 7±2 is about memory span. Later working-memory estimates put the limit near 4 chunks (Cowan 2001, not verified here). C4 sets no limit. Treat 7 as a heuristic. Overviews of 4–5 groups may be safer, with detail in deep dives.
- **Lead time of visual over voice:** Practitioner advice (Hermes) says to lead slightly. Mayer says simultaneous. Baggett (1984) studied offsets, but I could not verify the numbers.
- **Staging intensity:** Heer & Robertson found that simple staging helps. Aggressive "one thing at a time" staging was disliked and slower. "Animate one thing at a time" should mean one *conceptual* change, not one property per beat.
- **VLM judges:**
  - Code2Video reports strong VLM–human trend agreement but says humans penalize brief occlusions that VLMs miss.
  - TheoremExplainAgent reports low agreement on flow and consistency.
  - Paper2Video did not validate its VLM layout judge.
  - Conclusion: VLM scores are usable for coarse ranking, not as a pass/fail gate.
- **"Transform, don't cut" attribution:** I found no primary Grant Sanderson source. The rule rests on practitioner skills and Heer & Robertson's object constancy, not on a 3b1b statement.
- **Wiseman 15%:** This is vendor-commissioned and was never peer reviewed. Exclude it.

# Appendix D

## Narration and voice for TTS explainers: research findings

Research date: 2026-10-28. Scope: a skill that writes a 300–750 word script (5–13 scenes, 150 wpm), narrates it with ElevenLabs `eleven_v4` and emotion audio tags (5–9 per 3 minutes), and syncs animation to word timestamps. A captions-only fallback exists.

### Verification labels

- **[fetched]**: I read the primary page or the author's own write-up.
- **[abstract]**: I read abstract text or highlights quoted in search results or on indexing pages. I did not read the full paper.
- **[snippet]**: The claim comes from a search snippet or a secondary summary only. Treat it as unverified.
- **[vendor]**: A vendor or marketing source. The claim is useful as practice, not as evidence.

Several publisher pages (Springer, Taylor & Francis, ResearchGate, Academia) returned 403 or login redirects. Effect sizes that I could not see are marked "not retrieved".

---

### 1. Voice principle with modern TTS

#### 1.1 The original voice principle came from old machine voices

- **Claim.** People learned more from a human narrator than from a machine voice.
- **Evidence.** Mayer, Sobko & Mautone (2003), *Journal of Educational Psychology*. Narrated lightning animation. Human voice beat machine voice, d = 0.79. [snippet, via a secondary summary]
- **Boundaries.** The machine voices were early-2000s concatenative or formant engines. Mayer & DaPra (2012) used better TTS and found no learning difference. [snippet]
- **Implication.** Do not cite the voice principle as a reason to avoid TTS. Its evidence base used much worse voices.

#### 1.2 Modern TTS matches human voice on learning, but not on perceived humanness

- **Claim.** A modern TTS engine produced equal or better learning than a recorded human voice. Learners still rated the human voice as more human and engaging.
- **Evidence.**
  - Craig & Schroeder (2017), "Reconsidering the voice effect when learning from a virtual human," *Computers & Education* 114. Design: human voice vs. modern TTS (NeoSpeech) vs. classic TTS (Microsoft), with a virtual human. Modern TTS produced higher transfer than both. Retention did not differ. Credibility and "facilitating learning" ratings were similar for modern TTS and human voice. [abstract]
  - Craig & Schroeder (2019), *Journal of Educational Computing Research* 57. Narrated animation with no visible agent. Randomized pretest–posttest design. Modern TTS and human voice did not differ on learning, perceptions, or cognitive efficiency. In the agent version, human voice got higher persona ratings for humanness and engagement. [abstract]
  - Dinçer (2022), *Journal of Pedagogical Research*. Human vs. traditional machine vs. modern machine voice, pretest–posttest. [snippet; result not retrieved]
- **Boundaries.** One research group did most of this work. The voices were 2017-era engines, which are weaker than 2026 neural TTS. Samples were mostly US undergraduates or online workers. Effect sizes were not retrieved.
- **Implication.** A good neural voice is safe for learning outcomes. Spend effort on humanness and engagement cues, not on proving parity.

#### 1.3 Voice quality affects trust, not learning

- **Claim.** A virtual human's voice quality did not change learning. It did change trust and perceptions of the agent.
- **Evidence.** Chiou, Schroeder & Craig (2020), "How we trust, perceive, and learn from virtual humans: The influence of voice quality," *Computers & Education* 146, 103756. Online experiment. Trust related to perceived "facilitating learning," "credibility," and "engaging." [abstract] DBLP lists the author order as Schroeder, Chiou, Craig. Most other records list Chiou first.
- **Boundaries.** This is a single online study with a visible agent. Trust was self-reported.
- **Implication.** A poor or glitchy voice costs trust before it costs learning. Re-render any line that has artifacts.

#### 1.4 Prosody interacts with listener population

- **Claim.** Strong prosody can hurt non-native listeners. A flatter voice can raise germane load and persona ratings for them.
- **Evidence.** Davis, Vincent & Park (2019), "Reconsidering the voice principle with non-native language speakers," *Computers & Education* 140, 103605. Strong-prosody human vs. weak-prosody human vs. modern computer voice. Non-native English speakers. A weak-prosody human voice raised germane load. Fewer prosodic elements improved agent persona ratings. [abstract highlights]
- **Supporting.** Liew et al. (2020, below) found that a calm voice gave higher germane load than an enthusiastic voice in non-native speakers. [abstract]
- **Boundaries.** Small, population-specific samples. Sample size and effect sizes were not retrieved.
- **Implication.** Heavy emotional styling is a cost for non-native viewers. Keep tags sparse and keep captions available.

#### 1.5 Studies from 2024–2026 on AI voices and AI instructors

- **Claim.** AI-generated videos give similar learning. Learners enjoy them less and rate them as less human. The penalty runs through perceived human-likeness and motivation.
- **Evidence.**
  - Netland, von Dzengelevski, Tesch & Kwasnitschka (2025), "Comparing human-made and AI-generated teaching videos," *Computers & Education*, doi 10.1016/j.compedu.2024.105164, CC BY. N = 447 online participants, within-subjects counterbalanced, 4 videos. The AI videos used ChatGPT scripts, Midjourney images, and HeyGen avatars with synthetic speech. Exam results did not differ significantly. Participants preferred the human videos for learning experience. Netland's write-up: "students enjoyed them less but learned the same." [fetched: author write-up, media-and-learning.eu, Mar 2025]
  - Xu et al. (2024), *British Journal of Educational Technology*. AI-generated vs. recorded videos. Comparable overall learning, higher retention, similar transfer. [snippet, secondary citation]
  - "Real versus AI-generated instructors and human versus synthetic voices in educational videos" (2026), *Education and Information Technologies*, doi 10.1007/s10639-026-14085-y. 2×2 design, N = 130. AI instructors were rated less human-like. Lower human-likeness reduced motivation, and lower motivation reduced retention. [snippet; voice-factor result not retrieved]
  - Zhang, Lucas, Bem-Haja & Pedro (2025), "AI versus human-generated voices and avatars: rethinking user engagement and cognitive load," *Education and Information Technologies*, doi 10.1007/s10639-025-13654-x. 2×2 voice × avatar, foreign-language learning. Engagement rose significantly only when both voice and avatar were AI. [snippet]
  - Chen (2026), *European Journal of Education*, doi 10.1111/ejed.70413. N = 340 Grade 8–9 students. Higher pitch and prosodic prominence of an AI voice predicted engagement intentions. [snippet]
  - Jing et al. (2024/2025), "Cute computer-synthesized voice hinders learning performance in instructional videos," *Journal of Experimental Education* 94(4), doi 10.1080/00220973.2024.2446169. Eye-tracking study. A "cute" stylized synthetic voice hurt learning. [snippet: title and framing only; design not retrieved]
  - Zhang (2025), arXiv 2511.20660. Gemini scripts plus Amazon Polly narration in two courses. Learning was comparable to human-made videos. Students cited audio quality as a weakness. [fetched abstract; pilot, weak design]
- **Boundaries.** Most studies use short videos, online gig workers, and immediate tests. None isolates ElevenLabs v3/v4-class expressive voices. The 2026 studies are recent and not replicated.
- **Implication.** Expect parity on learning and a penalty on enjoyment. Reduce that penalty with a natural voice, specific content, and visual craft, not with more emotion.

#### 1.6 Over-stylized or incongruent voices

- **Claim.** A voice style that draws attention to itself can hurt learning. Emotion that mismatches the content hurts credibility.
- **Evidence.**
  - Jing et al. (2024/2025), cute synthetic voice hurt learning (above). [snippet]
  - CogSci 2025 paper on emotional prosody in human vs. advanced TTS. It frames inauthentic emotion as parallel to the uncanny valley. [snippet; findings not retrieved]
  - Queen Mary University of London (2025) press release. AI voices (clones and generic) were rated more dominant than human voices, and some were rated more trustworthy. No "hyperrealism" effect appeared. [snippet]
  - Secondary trust article: cheerful delivery of bad news undermines credibility. [snippet, secondary]
  - Practitioner reports on ElevenLabs v3: output can feel "too dramatic for normal speech" and "unnaturally excited." [snippet, secondary review, 2025]
- **Boundaries.** No study isolates over-expression in neural TTS as a cause of lower learning. The evidence is indirect.
- **Implication.** Match every tag to the content of its sentence. Never tag neutral factual statements with [excited].

#### 1.7 Enthusiastic voice: mixed evidence

- **Claim.** An enthusiastic voice sometimes improves transfer and social ratings. With a synthetic voice, enthusiasm did not improve learning.
- **Evidence.**
  - Liew, Tan, Tan & Kew (2020), "Does speaker's voice enthusiasm affect social cue, cognitive load and transfer in multimedia learning?" *Information and Learning Sciences* 121(3/4), 117–135, doi 10.1108/ILS-11-2019-0124. Two lab experiments. Computer-algorithm lesson narrated by an enthusiastic or a calm human voice. Enthusiasm raised social ratings (human-like, engaging) and transfer in both experiments. The calm voice gave higher germane load. Participants were non-native speakers. [abstract]
  - Liew et al. (2022/2023), "I am Alexa, your virtual tutor!" *Education and Information Technologies* 28(2), 1455–1489, doi 10.1007/s10639-022-11255-6. N = 244, between-subjects. Alexa voice at neutral, low, medium, or high enthusiasm. Learners heard more enthusiasm at medium and high. Persona ratings did not rise. Low and high enthusiasm reduced intrinsic and extraneous load. Medium raised positive emotion. Immediate retention and transfer did not improve. [abstract]
  - Liew, Zin & Sahari (2017), *Human-centric Computing and Information Sciences*. An agent enthusiastic in voice, face, and remarks improved emotion, motivation, and cognitive outcome. [abstract]
- **Boundaries.** The positive results used a human voice or multi-channel enthusiasm. The synthetic voice result was null on learning. Liew's samples were Malaysian university students.
- **Implication.** Use moderate warmth as the baseline. Do not expect [excited] tags to raise learning. Their benefit is affect and attention.

#### 1.8 Positive instructor emotion (Lawson & Mayer)

- **Claim.** Learners recognize instructor emotion from voice, face, and gesture. A positive instructor produced better learning in one of two experiments.
- **Evidence.**
  - Lawson, Mayer, Adamo-Villani, Benes, Lei & Cheng (2021), "The positivity principle: do positive instructors improve learning from video lectures?" *Educational Technology Research and Development*, doi 10.1007/s11423-021-10057-w. Two experiments with a statistics lecture. Learners rated the positive instructor as more positive. The positive group scored higher on a delayed posttest (Experiment 2), not on an immediate posttest (Experiment 1). [snippet; effect sizes not retrieved]
  - Lawson et al. (2021), "Recognizing the emotional state of human and virtual instructors," *Computers in Human Behavior*. Viewers detected happy, content, bored, and frustrated states in human and animated instructors. [abstract]
  - Lawson et al. (2021), *International Journal of Artificial Intelligence in Education*. Emotions of an animated pedagogical agent. [abstract]
- **Boundaries.** These studies contrast positive with negative or bored emotion. They do not test "very excited" against "warm." The emotion came from several channels, not voice alone.
- **Implication.** The goal is to avoid a bored or flat delivery. A consistent, warm, positive tone matters more than emotional peaks.

---

### 2. Speaking rate, pauses, and playback speed

#### 2.1 Guo, Kim & Rubin (2014): faster speakers held viewers longer

- **Claim.** In edX videos, instructors who spoke faster had higher engagement. The authors linked fast speech to enthusiasm.
- **Evidence.** Guo, Kim & Rubin (2014), "How video production affects student engagement: An empirical study of MOOC videos," ACM Learning @ Scale, 41–50, doi 10.1145/2556325.2566239. Observational analysis of 6.9 million sessions, about 128,000 students, 862 videos. Speaking rate was extracted automatically as wpm. Summaries report that videos at up to 254 wpm retained viewers about twice as long as videos below 166 wpm. Recommendation: "Coach instructors to bring out their enthusiasm and reassure them that they do not need to purposely slow down." [snippet, several secondary summaries quoting the paper; full PDF not fetched]
- **Boundaries.** The data is correlational. Engagement was watch time, not learning. Speaking rate likely proxies for enthusiasm and preparation. Video length was the strongest predictor (shorter is better). Human instructors only.
- **Implication.** 150 wpm is a safe planning rate, not a ceiling. Do not slow a synthetic voice below its natural pace for "clarity."

#### 2.2 Comfortable rates for synthetic speech

- **Claim.** Listeners are comfortable with synthetic speech at about 150–200 wpm. Comprehension falls when the rate leaves too little processing time.
- **Evidence.** Sutton et al. reported comfort at 150–200 wpm for young and older adults. A study of synthesized persuasive messages used 155 wpm as normal and found lower comprehension at accelerated rates for native and non-native listeners (Western Sydney University). Aldholmi et al. (Interspeech 2021) argue that wpm is imprecise and that syllables per second is a better unit. [snippet, all]
- **Boundaries.** No study tests instructional narration rate with modern neural TTS.
- **Implication.** Keep the 150 wpm budget. Measure the rendered duration and adjust the script, not the voice speed.

#### 2.3 Playback speed tolerance

- **Claim.** Learners lost little comprehension at 1.5x and 2x. Comprehension dropped at 2.5x.
- **Evidence.** Murphy, Hoover, Agadzhanyan, Kuehn & Castel (2022), "Learning in double time: The effect of lecture video speed on immediate and delayed comprehension," *Applied Cognitive Psychology* 36(1), 69–82, doi 10.1002/acp.3899. Scores out of 40: 1x about 26, 2x about 25, 2.5x about 22. Students believed slower was better. [abstract and press summaries]
- **Boundaries.** The videos were human lectures of moderate difficulty. The authors warn that complex or technical material may need slower pacing or pauses.
- **Implication.** A 150 wpm script has headroom. Dense technical scenes need pauses, not a slower overall rate.

#### 2.4 Segmentation and pauses help, especially in system-paced media

- **Claim.** Splitting a presentation into meaningful segments improves retention and transfer. System-inserted pauses help learners at risk of overload.
- **Evidence.**
  - Rey, Beege, Nebel, Wirzberger, Schmitt & Schneider (2019), "A meta-analysis of the segmenting effect," *Educational Psychology Review* 31(2), 389–419, doi 10.1007/s10648-018-9456-4. 56 investigations, 88 pairwise comparisons. Small to medium effects on retention and transfer. Lower cognitive load and longer learning time. The effects were confirmed for system-paced segmentation. [abstract; exact g values not retrieved]
  - Spanjers et al. (2012), *Computers & Education*. N = 161 secondary students, probability animations. Both pauses and structural cues contributed to the segmentation effect, in different ways. [abstract]
  - Spanjers et al. (2011) is cited for the claim that system pauses help learners at risk of overload. [snippet]
  - Wang, Mayer et al.: segmenting improved retention but not transfer. Asking learners to summarize during pauses improved both. [snippet]
- **Boundaries.** Most studies segment by pauses or "continue" buttons, not by sub-second gaps. Segment benefit is larger for some prior-knowledge groups (the direction varies by source).
- **Implication.** Put a real pause (about 0.5–1.5 s) at each scene boundary. Let the animation finish its reveal inside that pause.

#### 2.5 ElevenLabs v4 cannot insert exact pauses

- **Claim.** Eleven v4 and v3 do not support SSML `<break>` tags. Punctuation and text structure control pauses.
- **Evidence.** ElevenLabs, "Prompting Eleven v4" docs: "Eleven v4 and Eleven v3 do not support SSML break tags." "Punctuation significantly affects delivery in v4." Ellipses add pauses and weight. Capitalization adds emphasis. "Text structure strongly influences output with v4." [fetched, elevenlabs.io/docs/best-practices/prompting, Oct 2026]
- **Implication.** Make scene pauses in the audio pipeline (insert silence between per-scene renders, or shift timestamps), not in the prompt text.

---

### 3. Personalization (conversational style)

#### 3.1 The meta-analytic effect

- **Claim.** Conversational style ("you," "we," direct address) improves learning, more for transfer than for retention.
- **Evidence.** Ginns, Martin & Marsh (2013), "Designing instructional text in a conversational style: A meta-analysis," *Educational Psychology Review* 25, 445–472. Retention d = 0.30, transfer d = 0.54. Small effects on interest (d = 0.15) and lower perceived difficulty. [abstract] Mayer's book reports a median d = 0.79 across 17 tests, with 14 of 17 supporting. That figure uses a different aggregation. [snippet]
- **Boundaries.** The effect shrinks in longer lessons. It may not hold for high-achieving learners. Ginns et al. reported moderators by lesson length. Our 2–5 minute format sits inside the favourable range.
- **Implication.** Write the narration in second person with "you" and "we." It is the best-supported script rule in this report.

#### 3.2 A recent failure to replicate

- **Claim.** Personalized wording produced worse transfer in a health-information study.
- **Evidence.** Almeida, Münzer & Kühl (2024), "More personal, but not better: The personalization effect in learning neutral and aversive health information," *Journal of Computer Assisted Learning* 40(5), 2248–2260, doi 10.1111/jcal.13026. Non-personalized materials gave better transfer for neutral and aversive content. [abstract]
- **Boundaries.** One study, health content. The authors suspect self-reference to aversive content may distract.
- **Implication.** Use "you" for the viewer's actions and goals. Do not use "you" for bad outcomes ("your data gets stolen") when a neutral subject works.

---

### 4. Redundancy versus captions

#### 4.1 The meta-analysis contradicts the strict redundancy rule

- **Claim.** Spoken plus written text beat spoken-only text overall. It did not beat written-only. The benefit depended on images, pacing, and prior knowledge.
- **Evidence.** Adesope & Nesbit (2012), "Verbal redundancy in multimedia learning environments: A meta-analysis," *Journal of Educational Psychology* 104(1), 250–263, doi 10.1037/a0026147. 48 effect sizes from 32 reports (per Adesope's dissertation). Spoken–written beat spoken-only. Spoken–written and written-only did not differ. The benefit held for low-prior-knowledge learners with system-paced materials when no images appeared at the same time. [abstract and dissertation summary; pooled g not retrieved]
- **Review.** Trypke, Stebner & Wirth (2023), "Two types of redundancy in multimedia learning: a literature review," *Frontiers in Psychology*. Narration with short written keywords fosters learning. Narration with identical full text, alongside visuals, impaired learning (Mayer et al., 2001). Mayer & Johnson (2008) found embedded keywords helped retention, not transfer. Recommendation: short redundant text or keywords for complex material and low-prior-knowledge learners. [fetched]
- **Boundaries.** The harmful case is full verbatim text on screen at the same time as animation. Our scenes are animated, so they sit in the harmful zone if full captions show by default.
- **Implication.** With narration on, show short on-screen keywords tied to the animation. Make full captions optional and off by default.

#### 4.2 Non-native speakers: mixed results

- **Claim.** Captions did not help non-native speakers with a fast, dense video. Text plus narration helped them with a slower video.
- **Evidence.**
  - Mayer, Lee & Peebles (2014), "Multimedia learning in a second language: A cognitive load perspective," *Applied Cognitive Psychology*, doi 10.1002/acp.3050. Experiment 1: adding video to slow narration helped non-native speakers, d = 0.63. Experiment 2: captions on a fast 9-minute chemistry video did not help. [abstract]
  - Lee & Mayer (2018), "Fostering learning from instructional video in a second language," *Applied Cognitive Psychology*, doi 10.1002/acp.3436. Video + narration + text beat video + narration, against the redundancy effect. [abstract]
- **Boundaries.** Rate and density decide whether L2 learners can use captions.
- **Implication.** Offer a caption toggle. Captions help L2 viewers most when the narration is not rushed.

#### 4.3 Accessibility requires captions regardless

- **Claim.** Deaf and hard-of-hearing viewers need synchronized captions for prerecorded audio.
- **Evidence.** WCAG 2.x Success Criterion 1.2.2 (Captions, Prerecorded), level A. [known standard; not re-fetched]
- **Implication.** Ship captions always. Learning research only decides the default visibility.

---

### 5. Practitioner advice: writing for the ear and directing the voice

#### 5.1 Writing for the ear

- **Claim.** Narration needs short sentences, active voice, conversational wording, and a read-aloud test.
- **Evidence.** Consistent advice across voice-over and e-learning guides: The eLearning Coach (Connie Malamed), Debbie Grattan (voice actor), Articulate community, TruScribe, Murf, WellSaid, Typecast. Common rules: write for the ear, one idea per sentence, avoid hard-to-pronounce words, mark pauses with line breaks and dashes, script every word, end with a takeaway. [vendor/practitioner]
- **Implication.** Lint the script for sentence length, nested clauses, and symbols the TTS will misread (numbers, acronyms, code).

#### 5.2 ElevenLabs v4 audio-tag guidance

- **Claim.** Tags work best when sparse, auditory, matched to the voice, and placed next to the words they change.
- **Evidence.**
  - ElevenLabs, "Prompting Eleven v4" docs [fetched, Oct 2026]:
    - Place tags before or after the line: "[annoyed] This is hard." / "This is hard. [sighs]."
    - Tags "MUST describe something auditory."
    - "Match tags to your voice's character and training data." "A serious, professional voice may not respond well to playful tags."
    - "Some experimental tags may be less consistent across different voices. Test thoroughly before production use."
    - "A tag can occasionally be interpreted as a request for a sound effect rather than a delivery instruction."
    - v4 follows tags more reliably than v3, even outside the voice's training data, but "the result may not be optimal."
    - Example voice tags: [laughs], [whispers], [sighs], [exhales], [sarcastic], [curious], [excited], [mischievously].
  - ElevenLabs blog, "Audio tags list," published 2026-09-30, updated 2026-10-15 [fetched]: "Use one tag per clause: Contrasting tags on the same words can blur the performance." "You only need to introduce another tag when you want the delivery to shift." "Eleven v4 also adds small human touches when the emotion calls for them."
  - ElevenLabs v3 docs (2025): stability Creative/Natural give the most tag responsiveness. Robust "reduces responsiveness to directional prompts." [snippet; v4 stability modes not confirmed]
  - Eleven v4 launched about 2026-09-28 with v4 Turbo. Model ID `eleven_v4`. 10,000-character request limit per OpenRouter. [snippet, news and listings]
- **Boundaries.** Vendor docs give no guidance on tag density for narration. The examples favour drama and comedy.
- **Implication.** Treat a tag as a change of delivery, not decoration. Because v4 "adds small human touches" by itself, fewer explicit tags may suffice.

#### 5.3 Overacting in AI voiceovers

- **Claim.** Expressive TTS models can sound theatrical in plain narration.
- **Evidence.** Reviewers of v3 alpha reported "too dramatic for normal speech" and "unnaturally excited" output. [snippet, 2025 secondary review] Runware's v3 guide advises using punctuation before tags: an ellipsis or period often does the work. [vendor]
- **Implication.** Prefer punctuation and sentence rhythm for pacing. Reserve tags for real emotional turns, such as a surprise result or an aside.

---

### 6. Audience reception: AI slop, disclosure, platforms

#### 6.1 "AI slop" perception in explainers

- **Claim.** Viewers and educators complain about mass-produced AI explainers. The complaint targets templated, low-effort content more than the voice itself.
- **Evidence.**
  - r/matheducation thread, "Fully AI-generated math explainer videos are flooding YouTube," about February 2026. Commenters called it "AI slop" and "dead internet." [snippet via a Reddit mirror; body not captured]
  - YouTube renamed its "repetitious content" policy to "inauthentic content," effective 2025-07-15. It targets mass-produced, templated content. YouTube said it does not target creators who use AI as a tool. [snippet, TechCrunch 2025-07-09 and others]
  - Creator anecdotes: early faceless channels failed when the AI voice felt "emotionless or detached." One creator reported better retention after switching to an AI voice. [vendor blogs and a single Reddit comment]
  - I found no Hacker News thread with substantive data on AI-narrated explainers.
- **Implication.** Avoid the slop signature: generic hooks, stock phrasing, uniform pacing, and stacked emotions. Specific content and visuals are the defence.

#### 6.2 Disclosure lowers engagement in some settings

- **Claim.** Labels lower likes and stated trust on social platforms. In ads, labels did not hurt performance.
- **Evidence.**
  - TikTok analysis (Journal of Consumer Research, via Science Says): posts with AI disclosure got about 7–8% fewer likes. [snippet, secondary]
  - Studio Resonate (SiriusXM) industry study: trust fell 27% when listeners were primed to expect an AI voice. Human voices labelled as AI were penalized equally. [snippet, industry]
  - MediaScience and Ehrenberg-Bass study, N = 900: AI labels on video ads did not lower any performance measure. Audiences most wanted labels for AI humans (60%) and voices (45%). [snippet]
- **Boundaries.** None of these studies concern educational explainers or self-made internal tools. The penalty seems to come from the label expectation, not only from the sound.
- **Implication.** Disclose the AI voice in one quiet line (credits or caption), not as a banner. Do not hide it.

---

### Ranked top-10 implications for the explainer skill

1. **Write in conversational second person.** Personalization has the strongest meta-analytic support: transfer d = 0.54, retention d = 0.30 (Ginns et al., 2013). Avoid "you" for aversive outcomes (Almeida et al., 2024).
2. **Make tags sparse and tied to content.** Use one tag per clause, and only where delivery should shift (ElevenLabs, 2026). No study shows that tags improve learning. Cute or incongruent styling can hurt learning. Treat 5–9 tags per 3 minutes as a ceiling, not a target. Use 0–1 tags per scene.
3. **Set a warm baseline instead of peaks.** Positive affect helps (Lawson et al., 2021). Synthetic enthusiasm did not raise learning (Liew et al., 2022). Choose a voice that sounds warm untagged, then use [curious] or [excited] only at real reveals.
4. **Do not tag neutral facts with excitement.** Incongruent emotion costs credibility, and v3/v4 can overact. Prefer punctuation (ellipsis, full stop, short sentence) for rhythm.
5. **Put real pauses at scene boundaries.** Segmentation has small-to-medium effects on retention and transfer in system-paced media (Rey et al., 2019). v4 has no `<break>`, so insert the silence in the audio pipeline and land animation reveals inside it.
6. **Show keywords, not full captions, by default.** Verbatim text alongside narration and animation hurts. Short keywords help (Adesope & Nesbit, 2012; Trypke et al., 2023). Provide a caption toggle for accessibility (WCAG 1.2.2) and L2 viewers.
7. **Keep 150 wpm as a budget, not a voice setting.** Faster speech correlated with engagement (Guo et al., 2014). Learners tolerate 1.5–2x (Murphy et al., 2022). Fix overruns by cutting words. Do not slow the voice.
8. **Choose and test the voice for clean, natural prosody.** Modern TTS matches human voices on learning, but quality drives trust (Craig & Schroeder, 2017/2019; Chiou et al., 2020). Re-render any line with artifacts, mispronunciations, or sound-effect misreads of tags.
9. **Beat the "AI slop" signature with specific content.** AI videos teach equally but are enjoyed less (Netland et al., 2025). The penalty runs through perceived human-likeness. Use concrete examples, varied sentence rhythm, and no generic hooks.
10. **Disclose the synthetic voice quietly.** Labels can cost some trust, but hidden AI voices risk more when discovered. One line in credits or the caption track is enough.

### Disagreements and open questions

- **Voice principle.** Mayer's original principle (d = 0.79, 2003) says human voices teach better. Craig & Schroeder (2017, 2019), Mayer & DaPra (2012), and Netland et al. (2025) found parity or better with modern TTS. The 2026 *Education and Information Technologies* 2×2 study reports that lower human-likeness reduced motivation and then retention. The disagreement is about mechanism: learning parity in short tests versus a motivation path that may matter over time.
- **Enthusiasm.** Liew et al. (2020) found that an enthusiastic human voice improved transfer. Liew et al. (2022) found that an enthusiastic synthetic Alexa voice did not. Guo et al. (2014) tied enthusiasm to watch time, not learning. Davis et al. (2019) found that weaker prosody helped non-native listeners. The evidence supports "not flat," not "more excited."
- **Redundancy versus captions.** Mayer's redundancy principle says verbatim on-screen text hurts. Adesope & Nesbit (2012) found that spoken plus written beat spoken-only overall. Lee & Mayer (2018) found that added text helped L2 learners. Mayer, Lee & Peebles (2014) found that captions did not help L2 learners on a fast video. Images, pacing, and rate seem to decide the outcome.
- **Personalization.** The meta-analysis is positive (Ginns et al., 2013), but Almeida et al. (2024) found a reversal. The effect may depend on content valence and lesson length.
- **Speaking rate.** Guo et al. (2014) suggest faster is more engaging. Synthetic-speech comprehension studies show declines at accelerated rates. Murphy et al. (2022) show tolerance up to 2x for human lectures. No study tests neural TTS narration rate for learning.
- **AI voices and engagement.** Zhang et al. (2025) found higher engagement when voice and avatar were both AI. Netland et al. (2025) and the 2026 study found lower enjoyment and human-likeness. The novelty, audience, and task may explain the difference.
- **Disclosure.** Social-platform data shows a label penalty. Ad research shows none. No study covers educational explainers.
- **Tag density.** ElevenLabs gives no density guidance for narration. The skill's 5–9 tags per 3 minutes has no research basis in either direction. Treat it as a tunable ceiling and test it with listeners.

### Gaps

- No study tests ElevenLabs v3/v4-class expressive TTS, or audio tags, for learning outcomes.
- No study tests caption default visibility in short animated explainers with neural TTS.
- I did not retrieve exact effect sizes for Adesope & Nesbit (2012), Rey et al. (2019), or Lawson et al. (2021). The publisher pages blocked access.
- Hacker News evidence on reception of AI-narrated explainers was absent from search results.
