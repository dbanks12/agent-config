// Step 6 checks for a built explainer. Run through qa.sh, which supplies Playwright.
// Usage: qa.sh <work dir> [extra seconds...]
// Serves the work dir with HTTP Range support, then checks: console errors, a [data-scene] div per scene,
// the right scene at each sampled time, a backward seek, pause and resume, the 5 s skip keys and buttons, Space, 2x speed,
// the captions toggle, full screen, the audio-only view, the ? prompt, and the last two seconds. Saves labeled 3x3 contact sheets of the stage to <work dir>/qa/sheet-N.jpg. Exits 1 on a failure.
const http = require("node:http");
const fs = require("node:fs");
const path = require("node:path");
const { chromium } = require("playwright");

const dir = path.resolve(process.argv[2] || ".");
const extra = process.argv.slice(3).map(Number);
const page_ = fs.existsSync(path.join(dir, "page.html")) ? "page.html" : null;
if (!page_) { console.error("qa: no page.html in " + dir); process.exit(2); }
const tm = JSON.parse(fs.readFileSync(path.join(dir, "timings.json"), "utf8"));
const types = { ".html": "text/html", ".mp3": "audio/mpeg", ".mp4": "audio/mp4", ".json": "application/json" };

const server = http.createServer((req, res) => {
  const f = path.join(dir, decodeURIComponent(req.url === "/" ? page_ : req.url.slice(1).split("?")[0]));
  if (!f.startsWith(dir) || !fs.existsSync(f)) { res.writeHead(404); return res.end(); }
  const size = fs.statSync(f).size;
  const head = { "Content-Type": types[path.extname(f)] || "application/octet-stream", "Accept-Ranges": "bytes" };
  const m = /bytes=(\d*)-(\d*)/.exec(req.headers.range || "");
  if (!m) { res.writeHead(200, { ...head, "Content-Length": size }); return fs.createReadStream(f).pipe(res); }
  const start = m[1] ? +m[1] : 0, end = m[2] ? +m[2] : size - 1;
  res.writeHead(206, { ...head, "Content-Range": `bytes ${start}-${end}/${size}`, "Content-Length": end - start + 1 });
  fs.createReadStream(f, { start, end }).pipe(res);
}).listen(0, "127.0.0.1");

const failures = [];
const check = (ok, msg) => { console.log(`${ok ? "PASS" : "FAIL"} ${msg}`); if (!ok) failures.push(msg); };

(async () => {
  const browser = await chromium.launch({ args: ["--autoplay-policy=no-user-gesture-required"] });
  const page = await browser.newPage({ viewport: { width: 1100, height: 1300 } });
  const errors = [];
  page.on("console", (m) => m.type() === "error" && errors.push(m.text()));
  page.on("pageerror", (e) => errors.push(String(e)));
  await page.goto(`http://127.0.0.1:${server.address().port}/`);
  await page.waitForTimeout(300);
  const hasAudio = await page.$(".xp-audio[src]").then(Boolean);
  if (hasAudio) await page.waitForFunction(() => document.querySelector(".xp-audio").readyState >= 1, null, { timeout: 15000 });

  const frames = () => page.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))));
  const seek = async (t) => {
    if (hasAudio) {
      await page.evaluate((t) => new Promise((r) => { const a = document.querySelector(".xp-audio"); a.addEventListener("seeked", r, { once: true }); a.currentTime = t; }), t);
    } else {
      await page.evaluate((t) => { const b = document.querySelector(".xp-bar"); b.value = t; b.dispatchEvent(new Event("input", { bubbles: true })); }, t);
    }
    await frames();
  };
  const visible = () => page.$$eval("[data-scene]", (els) => els.filter((e) => !e.hidden).map((e) => e.dataset.scene).join(","));
  const position = () => hasAudio ? page.$eval(".xp-audio", (a) => a.currentTime) : page.$eval(".xp-bar", (b) => +b.value);
  const sceneAt = (t) => (tm.scenes.find((s) => t >= s.start && t < s.end) || tm.scenes.at(-1)).id;

  const ids = await page.$$eval("[data-scene]", (els) => els.map((e) => e.dataset.scene));
  const missing = tm.scenes.map((s) => s.id).filter((i) => !ids.includes(i));
  check(missing.length === 0, `a [data-scene] div for every scene${missing.length ? ": missing " + missing : ""}`);

  const times = tm.scenes.flatMap((s) => [s.start + Math.min(1, (s.end - s.start) / 4), (s.start + s.end) / 2, s.end - 0.3])
    .concat(extra).sort((a, b) => a - b);
  const shots = [];
  const wrong = [];
  for (const t of times) {
    await seek(t);
    const v = await visible();
    if (v !== sceneAt(t)) wrong.push(`${t.toFixed(1)}s shows "${v}", expected ${sceneAt(t)}`);
    shots.push([t, v, (await page.locator(".xp-stage").screenshot()).toString("base64")]);
  }
  check(wrong.length === 0, `the right scene at ${times.length} sampled times${wrong.length ? ": " + wrong.join("; ") : ""}`);

  if (tm.scenes.length >= 3) {
    const later = tm.scenes[tm.scenes.length - 1], earlier = tm.scenes[tm.scenes.length - 3];
    await seek((later.start + later.end) / 2);
    const t = (earlier.start + earlier.end) / 2;
    await seek(t);
    check(await visible() === earlier.id, `a backward seek across two scenes lands on ${earlier.id}`);
  }

  const mid = Math.min(tm.duration / 2, tm.duration - 6);
  await seek(mid);
  await page.click(".xp-play");
  await page.waitForTimeout(1200);
  await page.click(".xp-play");
  const p1 = await position();
  await page.waitForTimeout(800);
  const p2 = await position();
  check(p1 > mid + 0.5 && Math.abs(p2 - p1) < 0.05, `play advances (${(p1 - mid).toFixed(2)} s) and pause holds (${(p2 - p1).toFixed(2)} s)`);

  const k0 = Math.min(15, tm.duration / 2);
  await seek(k0);
  await page.evaluate(() => document.activeElement && document.activeElement.blur());
  await page.keyboard.press("ArrowRight");
  const k1 = await position();
  await page.keyboard.press("h");
  const k2 = await position();
  const want1 = Math.min(k0 + 5, tm.duration), want2 = Math.max(want1 - 5, 0);
  check(Math.abs(k1 - want1) < 0.1 && Math.abs(k2 - want2) < 0.1, `right arrow skips to ${k1.toFixed(2)} s and h back to ${k2.toFixed(2)} s`);
  await page.focus(".xp-speed");
  await page.keyboard.press("ArrowLeft");
  const k3 = await position(), rate = await page.$eval(".xp-speed", (x) => x.value);
  check(Math.abs(k3 - Math.max(k2 - 5, 0)) < 0.1 && rate === "1", `with the speed menu focused, left arrow skips to ${k3.toFixed(2)} s and the speed stays ${rate}x`);
  await page.click('.xp-skip[data-skip="5"]');
  const b1 = await position();
  await page.click('.xp-skip[data-skip="-5"]');
  const b2 = await position();
  check(Math.abs(b1 - Math.min(k3 + 5, tm.duration)) < 0.1 && Math.abs(b2 - Math.max(b1 - 5, 0)) < 0.1, `the +5s button skips to ${b1.toFixed(2)} s and −5s back to ${b2.toFixed(2)} s`);

  const isPlaying = () => page.$eval(".xp-play", (b) => b.textContent === "Pause");
  await page.focus(".xp-speed");
  await page.keyboard.press(" ");
  await page.waitForTimeout(300);
  const sp1 = await isPlaying();
  await page.focus('.xp-skip[data-skip="5"]');
  const sp0 = await position();
  await page.keyboard.press(" ");
  await page.waitForTimeout(300);
  const sp2 = !(await isPlaying()) && (await position()) - sp0 < 1;
  check(sp1 && sp2, `Space plays and pauses with the speed menu or a skip button focused`);

  await page.click(".xp-play");
  await page.waitForTimeout(300);
  await page.selectOption(".xp-speed", "2");
  const s0 = await position();
  await page.waitForTimeout(2000);
  const s1 = await position();
  check(s1 - s0 > 3.2 && s1 - s0 < 4.8, `2x speed advances ${(s1 - s0).toFixed(2)} s in 2 s`);
  await page.click(".xp-play");
  await page.selectOption(".xp-speed", "1");

  const a0 = Math.min(20, tm.duration - 1);
  await seek(a0);
  await page.click(".xp-ask");
  const askOpen = await page.$eval(".xp-ask-panel", (x) => !x.hidden);
  const askTxt = await page.$eval(".xp-ask-text", (x) => x.value);
  const recent = tm.words.filter((x) => x.s >= a0 - 5 && x.s <= a0).map((x) => x.w).join(" ");
  await page.click(".xp-ask-modes input[value=explainer]");
  const askExp = await page.$eval(".xp-ask-text", (x) => x.value);
  await page.keyboard.press("Escape");
  const askShut = await page.$eval(".xp-ask-panel", (x) => x.hidden);
  check(askOpen && askShut && askTxt.includes(recent) && askTxt.includes("confused") && /Answer in text/.test(askTxt) && /Make an explainer/.test(askExp),
    `the ? button opens a prompt with the last 5 s of narration, switches modes, and closes on Escape`);

  const ccState = () => page.$eval(".xp-captions", (x) => x.hidden ? "hidden" : x.textContent.trim() ? "shown" : "empty");
  const cc0 = await ccState();
  await page.click(".xp-cc");
  const cc1 = await ccState();
  await page.click(".xp-cc");
  const cc2 = await ccState();
  check(cc0 === (hasAudio ? "hidden" : "shown") && cc1 === (hasAudio ? "shown" : "hidden") && cc2 === cc0,
    `captions start ${cc0}, and the Captions button toggles them (${cc1}, then ${cc2})`);

  const isFull = () => page.evaluate(() => document.fullscreenElement === document.querySelector(".xp"));
  await page.click(".xp-full");
  await page.waitForTimeout(300);
  const fullOn = await isFull();
  await page.click(".xp-full");
  await page.waitForTimeout(300);
  const fullOff = !(await isFull());
  check(fullOn && fullOff, `the full-screen button enters and leaves full screen`);

  const shown = () => page.$$eval(".xp-stage, .xp-chapters, .xp details, .xp-controls > *", (els) =>
    els.filter((e) => e.checkVisibility()).map((e) => e.className || e.tagName.toLowerCase()).sort().join(","));
  const v0 = Math.min(10, tm.duration / 3);
  await seek(v0);
  await page.click(".xp-play");
  await page.waitForTimeout(500);
  await page.click(".xp-view");
  const vOn = await shown();
  const vp1 = await position();
  await page.waitForTimeout(800);
  const vp2 = await position();
  await page.click(".xp-play");
  const vp3 = await position();
  await page.click('.xp-skip[data-skip="5"]');
  const vp4 = await position();
  await page.click('.xp-skip[data-skip="-5"]');
  const vp5 = await position();
  await page.evaluate((t) => { const b = document.querySelector(".xp-bar"); b.value = t; b.dispatchEvent(new Event("input", { bubbles: true })); }, v0 + 8);
  await frames();
  const vp6 = await position();
  await page.click(".xp-view");
  await frames();
  const vOff = await shown();
  const vp7 = await position();
  const vScene = await visible();
  check(vOn === "xp-bar,xp-play,xp-skip,xp-skip,xp-time" && vp2 - vp1 > 0.5 && Math.abs(vp4 - vp3 - 5) < 0.1 && Math.abs(vp5 - vp3) < 0.1
      && Math.abs(vp6 - (v0 + 8)) < 0.1 && Math.abs(vp7 - vp6) < 0.05 && vOff.includes("xp-stage") && vScene === sceneAt(vp7),
    `audio-only view shows only ${vOn}, keeps playing (${(vp2 - vp1).toFixed(2)} s), skips and seeks, and the video view resumes at ${vp7.toFixed(2)} s on ${vScene}`);

  await seek(tm.duration - 2);
  await page.click(".xp-play");
  await page.waitForTimeout(2800);
  const end = await position();
  check(end >= tm.duration - 0.3, `playing the last two seconds reaches the end (${end.toFixed(2)} of ${tm.duration.toFixed(2)} s)`);

  fs.mkdirSync(path.join(dir, "qa"), { recursive: true });
  const sheets = [];
  for (let i = 0; i < shots.length; i += 9) {
    const cells = shots.slice(i, i + 9).map(([t, v, b]) =>
      `<div style="position:relative"><img src="data:image/png;base64,${b}" style="width:640px;display:block">` +
      `<span style="position:absolute;left:4px;top:2px;background:#000;color:#fff;font:14px monospace;padding:1px 4px">${t.toFixed(1)}s ${v}</span></div>`).join("");
    const sheet = await browser.newPage({ viewport: { width: 1932, height: 400 } });
    await sheet.setContent(`<body style="margin:0;display:grid;grid-template-columns:repeat(3,640px);gap:6px;background:#888">${cells}</body>`);
    const out = path.join(dir, "qa", `sheet-${i / 9 + 1}.jpg`);
    await sheet.screenshot({ path: out, type: "jpeg", quality: 80, fullPage: true });
    await sheet.close();
    sheets.push(out);
  }
  check(errors.length === 0, `no console errors${errors.length ? ": " + errors.join(" | ") : ""}`);
  console.log(`qa: ${failures.length} failed. Read the contact sheets: ${sheets.join(" ")}`);
  await browser.close();
  server.close();
  process.exit(failures.length ? 1 : 0);
})().catch((e) => { console.error(e); server.close(); process.exit(2); });
