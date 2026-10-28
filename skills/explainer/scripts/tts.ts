#!/usr/bin/env bun
// Narration client for the explainer skill: the ONLY process that ever reads the ElevenLabs key.
// Launch narrated runs through scripts/narrate.sh, which strips the environment so no Bun preload,
// bunfig or dotenv file runs inside this process, and points it at the key file.
// Usage: tts.ts <narration.json> <out-dir> [--captions-only] [--long]
import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { closeSync, existsSync, mkdirSync, openSync, readFileSync, renameSync, rmSync, statSync, writeFileSync } from "node:fs";
import { join, resolve } from "node:path";

type Scene = { id: string; title: string; text: string };
type Narration = { scenes: Scene[]; voice_id?: string; model_id?: string };
type Alignment = {
  characters: string[];
  character_start_times_seconds: number[];
  character_end_times_seconds: number[];
};

const API = "https://api.elevenlabs.io";
const MAX_CHARS = 6000;
// --long, for the long-explainer skill.
const LONG_MAX_CHARS = 30000;
// Whole scenes per request, under eleven_v4's 10,000-character limit and the request timeout.
const REQUEST_CHARS = 6000;
// About 32 minutes at 30,000 characters: mono 48 kbps keeps it near 12 MB, under the Artifact's 15 MB file limit.
const LONG_BITRATE = "48k";
const SCENE_GAP = "\n\n";
// Captions-only pacing: 150 words a minute plus a beat between scenes.
const CHARS_PER_SECOND = 15;
const SCENE_PAUSE = 0.8;

let apiKey = "";

function die(code: number, msg: string): never {
  console.error(`tts: ${apiKey ? msg.split(apiKey).join("[redacted]") : msg}`);
  process.exit(code);
}

// Parsed, never sourced: only these two names are read, and a group- or world-readable file is refused.
function readKeyFile(path: string | undefined) {
  if (!path) die(3, "no key file; run through scripts/narrate.sh or use --captions-only");
  if (!existsSync(path)) die(3, `${path} does not exist; see Key setup in SKILL.md`);
  if (statSync(path).mode & 0o077) die(3, `${path} is readable by other users; chmod 600 it`);
  const vars: Record<string, string> = {};
  for (const line of readFileSync(path, "utf8").split("\n")) {
    const m = /^\s*(ELEVENLABS_API_KEY|ELEVENLABS_VOICE_ID)\s*=\s*"?([^"\s]+)"?\s*$/.exec(line);
    if (m) vars[m[1]] = m[2];
  }
  if (!vars.ELEVENLABS_API_KEY) die(3, `${path} has no ELEVENLABS_API_KEY line`);
  return { key: vars.ELEVENLABS_API_KEY, voice: vars.ELEVENLABS_VOICE_ID };
}

function load(path: string): Narration {
  const n = JSON.parse(readFileSync(path, "utf8")) as Narration;
  if (!Array.isArray(n.scenes) || n.scenes.length === 0) die(1, "narration.scenes must be a non-empty array");
  const ids = new Set<string>();
  for (const s of n.scenes) {
    if (typeof s.id !== "string" || !/^[a-z0-9-]{1,32}$/.test(s.id) || ids.has(s.id)) die(1, `bad or duplicate scene id: ${s.id}`);
    if (typeof s.text !== "string" || !s.text.trim()) die(1, `scene ${s.id} has no text`);
    if (typeof s.title !== "string") die(1, `scene ${s.id} has no title`);
    ids.add(s.id);
  }
  return n;
}

// Offsets are in code points, the unit ElevenLabs' alignment.characters uses.
function joinScenes(scenes: Scene[]) {
  const chars: string[] = [];
  const spans = scenes.map((s, i) => {
    if (i > 0) chars.push(...SCENE_GAP);
    const start = chars.length;
    chars.push(...s.text.trim());
    return { id: s.id, title: s.title, text: s.text.trim(), start, end: chars.length };
  });
  return { chars, spans };
}

// Runs of consecutive whole scenes, each at most REQUEST_CHARS. A narration within MAX_CHARS is one part
// whose text is the whole narration, so its cache key is unchanged.
function requestParts(spans: { id: string; start: number; end: number }[]) {
  const parts: { start: number; end: number }[] = [];
  for (const s of spans) {
    if (s.end - s.start > REQUEST_CHARS) die(1, `scene ${s.id} is ${s.end - s.start} characters, over the ${REQUEST_CHARS}-character request size`);
    const last = parts.at(-1);
    if (last && s.end - last.start <= REQUEST_CHARS) last.end = s.end;
    else parts.push({ start: s.start, end: s.end });
  }
  return parts;
}

function syntheticAlignment(chars: string[], spans: { start: number }[]): Alignment {
  const a: Alignment = { characters: [], character_start_times_seconds: [], character_end_times_seconds: [] };
  let t = 0;
  let next = 1;
  for (let i = 0; i < chars.length; i++) {
    if (next < spans.length && i === spans[next].start) {
      t += SCENE_PAUSE;
      next++;
    }
    a.characters.push(chars[i]);
    a.character_start_times_seconds.push(t);
    t += 1 / CHARS_PER_SECOND;
    a.character_end_times_seconds.push(t);
  }
  return a;
}

function validAlignment(a: Alignment | null | undefined, chars: string[]): a is Alignment {
  if (!a || !Array.isArray(a.characters)) return false;
  const { characters: c, character_start_times_seconds: s, character_end_times_seconds: e } = a;
  if (c.length !== chars.length || s?.length !== c.length || e?.length !== c.length) return false;
  let prev = 0;
  for (let i = 0; i < c.length; i++) {
    if (c[i] !== chars[i] || !Number.isFinite(s[i]) || !Number.isFinite(e[i]) || s[i] < prev || e[i] < s[i]) return false;
    prev = s[i];
  }
  return true;
}

function words(a: Alignment) {
  const out: { w: string; s: number; e: number }[] = [];
  let cur: { w: string; s: number; e: number } | null = null;
  for (let i = 0; i < a.characters.length; i++) {
    const c = a.characters[i];
    if (/\s/.test(c)) {
      if (cur) out.push(cur);
      cur = null;
    } else if (cur) {
      cur.w += c;
      cur.e = a.character_end_times_seconds[i];
    } else cur = { w: c, s: a.character_start_times_seconds[i], e: a.character_end_times_seconds[i] };
  }
  if (cur) out.push(cur);
  return out;
}

function mediaDuration(path: string): number | null {
  // Empty env: the media parser never sees the key.
  const bin = process.env.EXPLAINER_FFPROBE ?? "ffprobe";
  const r = spawnSync(bin, ["-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path], { encoding: "utf8", env: {} });
  const d = Number(r.stdout?.trim());
  return r.status === 0 && Number.isFinite(d) && d > 0 ? d : null;
}

type Cached = { base: string; alignment: Alignment | null; requestId: string | null };

// Each part's times shifted by the audio before it. The gap between two parts takes the boundary's time.
function joinAlignments(chars: string[], parts: { start: number; end: number }[], cached: Cached[]): Alignment | null {
  const a: Alignment = { characters: [], character_start_times_seconds: [], character_end_times_seconds: [] };
  let offset = 0;
  for (const [i, p] of parts.entries()) {
    const part = cached[i].alignment;
    if (!validAlignment(part, chars.slice(p.start, p.end))) return null;
    for (let k = i === 0 ? p.start : parts[i - 1].end; k < p.start; k++) {
      a.characters.push(chars[k]);
      a.character_start_times_seconds.push(offset);
      a.character_end_times_seconds.push(offset);
    }
    a.characters.push(...part.characters);
    a.character_start_times_seconds.push(...part.character_start_times_seconds.map((t) => t + offset));
    a.character_end_times_seconds.push(...part.character_end_times_seconds.map((t) => t + offset));
    const d = mediaDuration(`${cached[i].base}.mp3`);
    if (!d) return null;
    offset += d;
  }
  return a;
}

// Joins the parts' audio into one mono MP3. Empty env, as for ffprobe.
function joinAudio(paths: string[], dest: string) {
  const list = `${dest}.list`;
  writeFileSync(list, paths.map((p) => `file '${p.replace(/'/g, "'\\''")}'\n`).join(""));
  const bin = process.env.EXPLAINER_FFMPEG || "ffmpeg";
  const args = ["-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", list, "-ac", "1", "-c:a", "libmp3lame", "-b:a", LONG_BITRATE, "-f", "mp3", `${dest}.tmp`];
  const r = spawnSync(bin, args, { encoding: "utf8", env: {} });
  rmSync(list);
  if (r.status !== 0) die(2, `ffmpeg could not join the parts: ${r.stderr?.trim()}; the parts stay cached`);
  renameSync(`${dest}.tmp`, dest);
}

function atomicWrite(path: string, data: string | Buffer) {
  writeFileSync(`${path}.tmp`, data);
  renameSync(`${path}.tmp`, path);
}

// One paid request per cache key, ever, unless the owner clears the pending marker by hand.
async function synthesize(text: string, voice: string, model: string, cacheBase: string) {
  const key = apiKey;
  const pending = `${cacheBase}.pending`;
  try {
    closeSync(openSync(pending, "wx"));
  } catch {
    die(4, `${pending} exists: an earlier request is in flight or its outcome is unknown. Check the ElevenLabs history, then delete the file to retry.`);
  }
  let audio: Buffer;
  let alignment: unknown;
  let requestId: string | null;
  try {
    const res = await fetch(`${API}/v1/text-to-speech/${encodeURIComponent(voice)}/with-timestamps?output_format=mp3_44100_128`, {
      method: "POST",
      redirect: "error",
      signal: AbortSignal.timeout(180_000),
      headers: { "xi-api-key": key, "content-type": "application/json", accept: "application/json" },
      body: JSON.stringify({ text, model_id: model }),
    });
    requestId = res.headers.get("request-id");
    if (!res.ok) {
      // An unreadable body throws to the outer catch, which keeps the marker: fail closed.
      const body = (await res.text()).slice(0, 600);
      // Only a 4xx is a confirmed rejection that generated nothing; a 5xx may still have been billed.
      if (res.status >= 400 && res.status < 500) {
        rmSync(pending);
        die(2, `HTTP ${res.status}: ${body}`);
      }
      die(4, `HTTP ${res.status}, outcome unknown, may be billed; ${pending} kept so nothing resubmits: ${body}`);
    }
    const json = (await res.json()) as { audio_base64?: string; alignment?: unknown };
    if (!json.audio_base64) throw new Error("response has no audio_base64");
    audio = Buffer.from(json.audio_base64, "base64");
    alignment = json.alignment ?? null;
  } catch (err) {
    die(4, `outcome unknown, may be billed; ${pending} kept so nothing resubmits: ${String(err)}`);
  }
  // Persist what was paid for before anything can fail on it.
  atomicWrite(`${cacheBase}.mp3`, audio);
  atomicWrite(`${cacheBase}.json`, JSON.stringify({ alignment, requestId }));
  rmSync(pending);
}

async function main() {
  const args = process.argv.slice(2);
  const captionsOnly = args.includes("--captions-only");
  const long = args.includes("--long");
  const positional = args.filter((a) => a !== "--captions-only" && a !== "--long");
  if (positional.length !== 2 || positional.some((a) => a.startsWith("-"))) die(1, "usage: tts.ts <narration.json> <out-dir> [--captions-only] [--long]");
  const out = resolve(positional[1]);
  mkdirSync(join(out, "cache"), { recursive: true });

  const n = load(resolve(positional[0]));
  const { chars, spans } = joinScenes(n.scenes);
  const cap = long ? LONG_MAX_CHARS : MAX_CHARS;
  if (chars.length > cap) die(1, `narration is ${chars.length} characters, over the ${cap} cap`);
  let voice = n.voice_id ?? "";
  const model = n.model_id ?? "eleven_multilingual_v2";
  if (!/^[a-z0-9_]{1,40}$/.test(model)) die(1, `bad model_id: ${model}`);

  let alignment: Alignment;
  let approx = false;
  let requestId: string | null = null;
  let duration: number;

  if (captionsOnly) {
    alignment = syntheticAlignment(chars, spans);
    duration = alignment.character_end_times_seconds.at(-1) ?? 0;
  } else {
    const file = readKeyFile(process.env.EXPLAINER_KEY_FILE);
    apiKey = file.key;
    voice ||= file.voice ?? "";
    if (!/^[A-Za-z0-9]{8,40}$/.test(voice)) die(1, "set voice_id in narration.json or ELEVENLABS_VOICE_ID in the key file");
    const parts = requestParts(spans);
    const cached: Cached[] = [];
    for (const [i, p] of parts.entries()) {
      const partText = chars.slice(p.start, p.end).join("");
      const base = join(out, "cache", createHash("sha256").update(JSON.stringify({ text: partText, voice, model })).digest("hex").slice(0, 32));
      const label = parts.length > 1 ? `part ${i + 1} of ${parts.length}, ` : "";
      if (existsSync(`${base}.mp3`) && existsSync(`${base}.json`)) console.log(`tts: ${label}cache hit, no request sent`);
      else await synthesize(partText, voice, model, base);
      cached.push({ base, ...(JSON.parse(readFileSync(`${base}.json`, "utf8")) as Omit<Cached, "base">) });
    }
    requestId = cached.map((c) => c.requestId).filter(Boolean).join(",") || null;
    const dest = join(out, "narration.mp3");
    let joined: Alignment | null;
    if (parts.length === 1) {
      atomicWrite(dest, readFileSync(`${cached[0].base}.mp3`));
      joined = cached[0].alignment;
    } else {
      joinAudio(cached.map((c) => `${c.base}.mp3`), dest);
      joined = joinAlignments(chars, parts, cached);
    }
    const media = mediaDuration(dest);
    if (validAlignment(joined, chars)) {
      alignment = joined;
      duration = Math.max(media ?? 0, alignment.character_end_times_seconds.at(-1) ?? 0);
    } else {
      // Scene times scaled over the audio; no word cues, because invented ones would drift.
      if (!media) die(2, "alignment unusable and ffprobe cannot read the audio length; rerun with --captions-only");
      approx = true;
      const synth = syntheticAlignment(chars, spans);
      const k = media / (synth.character_end_times_seconds.at(-1) ?? 1);
      alignment = { ...synth, character_start_times_seconds: synth.character_start_times_seconds.map((t) => t * k) };
      duration = media;
    }
  }

  const starts = alignment.character_start_times_seconds;
  const scenes = spans.map((s, i) => ({
    id: s.id,
    title: s.title,
    text: s.text,
    start: i === 0 ? 0 : starts[s.start],
    end: i === spans.length - 1 ? duration : starts[spans[i + 1].start],
  }));
  const timings = { audio: captionsOnly ? null : "narration.mp3", duration, model: captionsOnly ? null : model, approx, requestId, scenes, words: approx ? [] : words(alignment) };
  // `<` escaped so the file can be pasted inside <script type="application/json"> verbatim.
  atomicWrite(join(out, "timings.json"), JSON.stringify(timings).replace(/</g, "\\u003c"));
  const requests = requestId?.includes(",") ? `, ${requestId.split(",").length} requests` : "";
  console.log(`tts: ${scenes.length} scenes, ${duration.toFixed(1)} s, ${chars.length} characters${requests}${approx ? ", approximate scene timing, no word cues" : ""}`);
}

await main();
