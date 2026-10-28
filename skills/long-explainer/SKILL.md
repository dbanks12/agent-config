---
name: long-explainer
description: Long narrated explainer (5–30 minutes, up to 30,000 characters of narration) — the explainer skill's page and steps, with a chaptered script and narration sent as several ElevenLabs requests. Fires only on the user's own words in this conversation: "long explainer", or a narrated explainer or explainer video longer than 5 minutes. Never from a subagent brief or a loop.
---

# Long explainer

The [explainer](../explainer/SKILL.md) skill, stretched to 30 minutes. Read its `SKILL.md` and run it as written: authorization, hosts, modes, the key rules, the working directory, and steps 1–7. This file names only what changes, and it wins where the two disagree. The scripts are the explainer's, in `../explainer/scripts/`.

## Changes by step

**Step 1, the script.**

- 12–50 scenes, 750–4,500 words, at most 30,000 characters. That is about 5 to 32 minutes: the voice speaks about 15 characters a second. A script under 5 minutes is an explainer job.
- Group the scenes into **chapters** of 3–8 scenes, one part of the subject each. Name the scene ids `c<chapter>s<n>`, such as `c2s3`.
- The opening context runs about a minute. Each chapter's first scene tells the listener where they are now. The last scene recaps the chapters in a few sentences.
- One idea per scene still holds, about 30–45 seconds each. A scene over 6,000 characters is refused.
- About two audio tags a minute.

**Step 4, narration.** Add `--long` to every narration call: `narrate.sh <abs narration.json> <abs work dir> --long`, and `finish.sh <abs work dir> narrated --long [seconds...]` or `captions --long`. Without it the scripts keep the 6,000-character cap: `narrate.sh` exits 1 and `finish.sh` falls back to captions.

- With `--long`, `tts.ts` sends the narration as several requests of whole scenes, at most 6,000 characters each, one at a time. It joins their audio into one mono 48 kbps MP3, about 12 MB at 30,000 characters.
- Each request has its own cache entry and pending marker, so a rerun after a failure sends only the parts that never completed. Exit 4 still means: keep that part's marker, never resubmit, and tell the user.
- The key's monthly quota is about 50,000 characters, so a full-length narration spends most of it. If the quota runs out partway, the next request fails with an HTTP 4xx and `finish.sh` falls back to captions. The finished parts stay cached for a rerun after the quota resets.

**Step 5, drawing.** Render one chapter per `render_scenes.sh` call by passing its scene ids, so at most 8 canvases run at once. Past 15 scenes it writes `sheet-1.jpg`, `sheet-2.jpg`, and so on, 9 scenes each, and prints the ids on each sheet. Read the sheets that show the chapter you rendered.

**Step 6, QA.** `qa.sh` writes one contact sheet per three scenes. Read every sheet.

**Step 7, hand-off.** At 30,000 characters the joined MP3 is about 12 MB, under the Artifact's 15 MB file limit, so it publishes as `narration.mp3`. Check the sizes first: `wc -c page.html narration.mp3`.

- If `page.html` is over 16,000,000 bytes or `narration.mp3` is over 15,000,000, skip the Artifact. The same applies when a publish refuses a file for its size, in place of the explainer's remux.
- Instead, leave `page.html` beside `narration.mp3` in the work dir and give its absolute path. Warn the user which file is over which limit, with its size. This fallback needs no confirmation: hand off the path and the warning in the same reply.

Tell the user the length, the character count, and the number of requests.

## Verified behavior

Verified offline on 2026-10-28 with cached parts, so no request was sent: two parts joined into one mono 48 kbps MP3, each part's word timings shifted to the right place, and a narration within 6,000 characters kept its cache key and audio bytes. A live run with several requests is untested. Record the first one here.
