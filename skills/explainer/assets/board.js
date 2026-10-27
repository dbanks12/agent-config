// Style board previews. Each look draws the same moment as a pure function of time t (0-6 s, looping).
// A moment is { title, caption, nodes: [{id, label}], flow: [[from, to, label?]] }. build_board.py fills BOARD.
(() => {
  const clamp = (x) => Math.min(1, Math.max(0, x));
  const seg = (t, a, b) => { const x = clamp((t - a) / (b - a)); return x < 0.5 ? 4 * x * x * x : 1 - (-2 * x + 2) ** 3 / 2; };
  const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;");
  const jit = (i) => Math.sin(i * 12.9898) * 2.2; // fixed hand-drawn wobble, never random
  // Font size that fits text into a width, given a font's average glyph width per unit of size.
  const fit = (text, width, max, glyph = 0.55) => Math.min(max, width / (String(text).length * glyph));

  // Nodes on one row (up to 4) or two rows, inside a 640x360 stage below a title band.
  function layout(m, top = 100, h = 80) {
    const n = m.nodes.length, rows = n > 4 ? 2 : 1, per = Math.ceil(n / rows);
    const w = Math.min(190, 600 / per - 22);
    return Object.fromEntries(m.nodes.map((node, i) => {
      const r = Math.floor(i / per), c = i % per, cols = Math.min(per, n - r * per);
      const gap = (600 - cols * w) / (cols + 1);
      return [node.id, { ...node, i, x: 20 + gap + c * (w + gap), y: top + r * (h + 60) + (rows === 1 ? 60 : 0), w, h }];
    }));
  }
  // Each node appears in turn over 0.4-3 s; each flow draws after both its ends.
  const nodeAt = (m, i) => 0.4 + (2.6 * i) / Math.max(1, m.nodes.length);
  const flowAt = (m, L, f) => Math.max(nodeAt(m, L[f[0]].i), nodeAt(m, L[f[1]].i)) + 0.35;
  function ends(a, b) {
    const ax = a.x + a.w / 2, ay = a.y + a.h / 2, bx = b.x + b.w / 2, by = b.y + b.h / 2;
    if (Math.abs(ay - by) < 10) return ax < bx ? [a.x + a.w, ay, b.x, by] : [a.x, ay, b.x + b.w, by];
    return ay < by ? [ax, a.y + a.h, bx, b.y] : [ax, a.y, bx, b.y + b.h];
  }
  const words = (s, t, a, b) => { const w = s.split(" "), k = Math.round(w.length * seg(t, a, b)); return w.slice(0, k).join(" "); };

  const LOOKS = {
    excalidraw: { name: "Excalidraw sketch", draw(m, t) {
      const L = layout(m); let s = `<rect width="640" height="360" fill="#fffdf8"/>`;
      s += `<text x="28" y="56" font-family="Virgil, 'Comic Sans MS', cursive" font-size="${fit(m.title, 584, 34)}" fill="#1e1e1e">${esc(m.title)}</text>`;
      const fills = ["#a5d8ff", "#ffec99", "#b2f2bb", "#ffc9c9", "#d0bfff", "#99e9f2"];
      for (const f of m.flow) {
        const [x1, y1, x2, y2] = ends(L[f[0]], L[f[1]]), k = seg(t, flowAt(m, L, f), flowAt(m, L, f) + 0.6);
        if (k <= 0) continue;
        const ex = x1 + (x2 - x1) * k, ey = y1 + (y2 - y1) * k;
        s += `<path d="M${x1} ${y1} Q${(x1 + ex) / 2 + jit(x1)} ${(y1 + ey) / 2 + jit(y1)} ${ex} ${ey}" stroke="#1e1e1e" stroke-width="2" fill="none"/>`;
        if (k > 0.9) { const a = Math.atan2(y2 - y1, x2 - x1); s += `<path d="M${x2 - 12 * Math.cos(a - 0.4)} ${y2 - 12 * Math.sin(a - 0.4)} L${x2} ${y2} L${x2 - 12 * Math.cos(a + 0.4)} ${y2 - 12 * Math.sin(a + 0.4)}" stroke="#1e1e1e" stroke-width="2" fill="none"/>`; }
        if (f[2] && k > 0.6) s += `<text x="${(x1 + x2) / 2}" y="${(y1 + y2) / 2 - 10}" text-anchor="middle" font-family="Virgil, 'Comic Sans MS', cursive" font-size="15">${esc(f[2])}</text>`;
      }
      for (const n of Object.values(L)) {
        const k = seg(t, nodeAt(m, n.i), nodeAt(m, n.i) + 0.4), { x, y, w, h, i } = n;
        s += `<g opacity="${k}"><path d="M${x + jit(i)} ${y + jit(i + 1)} L${x + w + jit(i + 2)} ${y + jit(i + 3)} L${x + w + jit(i + 4)} ${y + h + jit(i + 5)} L${x + jit(i + 6)} ${y + h + jit(i + 7)} Z" fill="${fills[i % 6]}" stroke="#1e1e1e" stroke-width="2"/>`;
        s += `<text x="${x + w / 2}" y="${y + h / 2 + 6}" text-anchor="middle" font-family="Virgil, 'Comic Sans MS', cursive" font-size="${fit(n.label, w - 14, 24)}">${esc(n.label)}</text></g>`;
      }
      return s;
    } },
    swiss: { name: "Kinetic Swiss type", draw(m, t) {
      let s = `<rect width="640" height="360" fill="#f4f1ea"/><rect x="0" y="0" width="12" height="360" fill="#e10600"/>`;
      s += `<text x="40" y="96" font-family="Helvetica, Arial, sans-serif" font-weight="800" font-size="${fit(m.title, 570, 48, 0.58)}" fill="#111">${esc(words(m.title, t, 0, 1.2))}</text>`;
      m.nodes.forEach((n, i) => {
        const k = seg(t, nodeAt(m, i), nodeAt(m, i) + 0.35), y = 150 + i * (180 / m.nodes.length);
        s += `<g opacity="${k}" transform="translate(${(1 - k) * 40} 0)"><text x="40" y="${y + 24}" font-family="Helvetica, Arial, sans-serif" font-weight="700" font-size="26" fill="${i === m.nodes.length - 1 ? "#e10600" : "#111"}">${String(i + 1).padStart(2, "0")}</text>`;
        s += `<text x="96" y="${y + 24}" font-family="Helvetica, Arial, sans-serif" font-size="26" fill="#111">${esc(n.label)}</text></g>`;
        s += `<rect x="40" y="${y + 34}" width="${560 * k}" height="2" fill="#111"/>`;
      });
      return s;
    } },
    terminal: { name: "Retro terminal", draw(m, t) {
      let s = `<rect width="640" height="360" fill="#0b0f0b"/>`, y = 50;
      const line = (txt, at, color = "#7CFC7C") => {
        const k = clamp((t - at) / 0.6), shown = txt.slice(0, Math.round(txt.length * k));
        if (k > 0) s += `<text x="28" y="${y}" font-family="ui-monospace, Menlo, monospace" font-size="${fit(txt, 590, 22, 0.62)}" fill="${color}">${esc(shown)}${k < 1 && Math.floor(t * 4) % 2 ? "▌" : ""}</text>`;
        y += 34;
      };
      line(`$ ${m.title.toLowerCase()}`, 0, "#b7ffb7");
      m.nodes.forEach((n, i) => line(`[ ok ] ${n.label}`, nodeAt(m, i)));
      m.flow.forEach((f) => line(`  ${f[0]} --${f[2] ? ` ${f[2]} ` : ""}--> ${f[1]}`, flowAt(m, layout(m), f), "#5fd3ff"));
      return s;
    } },
    cutout: { name: "Paper cut-out", draw(m, t) {
      const L = layout(m, 120, 70); let s = `<rect width="640" height="360" fill="#e8dcc6"/>`;
      s += `<text x="32" y="60" font-family="Georgia, serif" font-weight="700" font-size="${fit(m.title, 580, 34, 0.5)}" fill="#3b2f2f">${esc(m.title)}</text>`;
      const papers = ["#f6bd60", "#84a59d", "#f28482", "#90be6d", "#9d8df1", "#f5cac3"];
      for (const f of m.flow) {
        const [x1, y1, x2, y2] = ends(L[f[0]], L[f[1]]), k = seg(t, flowAt(m, L, f), flowAt(m, L, f) + 0.5);
        s += `<line x1="${x1}" y1="${y1}" x2="${x1 + (x2 - x1) * k}" y2="${y1 + (y2 - y1) * k}" stroke="#3b2f2f" stroke-width="4" stroke-dasharray="2 8" stroke-linecap="round"/>`;
      }
      for (const n of Object.values(L)) {
        const k = seg(t, nodeAt(m, n.i), nodeAt(m, n.i) + 0.5), drop = (1 - k) * -80, rot = (n.i % 2 ? 3 : -3) * (1 + (1 - k) * 3);
        s += `<g opacity="${clamp(k * 3)}" transform="translate(${n.x + n.w / 2} ${n.y + n.h / 2 + drop}) rotate(${rot})"><rect x="${-n.w / 2 + 5}" y="${-n.h / 2 + 6}" width="${n.w}" height="${n.h}" fill="#0003"/>`;
        s += `<rect x="${-n.w / 2}" y="${-n.h / 2}" width="${n.w}" height="${n.h}" fill="${papers[n.i % 6]}"/><text y="7" text-anchor="middle" font-family="Georgia, serif" font-size="${fit(n.label, n.w - 14, 22, 0.5)}" fill="#2b2b2b">${esc(n.label)}</text></g>`;
      }
      return s;
    } },
    phone: { name: "Phone and card", draw(m, t) {
      let s = `<rect width="640" height="360" fill="#eef1f6"/>`;
      s += `<text x="36" y="76" font-family="system-ui, sans-serif" font-weight="700" font-size="${fit(m.title, 330, 30, 0.6)}" fill="#1c2430">${esc(words(m.title, t, 0, 1))}</text>`;
      // The caption wraps at about 30 characters a line beside the phone.
      const said = words(m.caption || "", t, 0.6, 3.6).split(" "), lines = [""];
      for (const w of said) (lines.at(-1) + " " + w).length > 30 ? lines.push(w) : (lines[lines.length - 1] = (lines.at(-1) + " " + w).trim());
      lines.slice(0, 5).forEach((l, i) => { s += `<text x="36" y="${120 + i * 26}" font-family="system-ui, sans-serif" font-size="19" fill="#5b6675">${esc(l)}</text>`; });
      s += `<rect x="400" y="24" width="190" height="320" rx="28" fill="#1c2430"/><rect x="410" y="44" width="170" height="284" rx="16" fill="#fff"/>`;
      m.nodes.slice(0, 5).forEach((n, i) => {
        const k = seg(t, nodeAt(m, i), nodeAt(m, i) + 0.45), y = 58 + i * 52 + (1 - k) * 30;
        s += `<g opacity="${k}"><rect x="420" y="${y}" width="150" height="42" rx="10" fill="${i === m.nodes.length - 1 ? "#2d6cdf" : "#f1f4f9"}"/>`;
        s += `<text x="434" y="${y + 26}" font-family="system-ui, sans-serif" font-size="14" fill="${i === m.nodes.length - 1 ? "#fff" : "#1c2430"}">${esc(n.label)}</text></g>`;
      });
      return s;
    } },
    blueprint: { name: "Blueprint", draw(m, t) {
      const L = layout(m); let s = `<rect width="640" height="360" fill="#123a6b"/>`;
      for (let x = 0; x <= 640; x += 32) s += `<line x1="${x}" y1="0" x2="${x}" y2="360" stroke="#ffffff14"/>`;
      for (let y = 0; y <= 360; y += 32) s += `<line x1="0" y1="${y}" x2="640" y2="${y}" stroke="#ffffff14"/>`;
      s += `<text x="28" y="52" font-family="ui-monospace, Menlo, monospace" font-size="${fit(m.title, 584, 26, 0.62)}" fill="#e6f0ff">${esc(m.title.toUpperCase())}</text>`;
      for (const n of Object.values(L)) {
        const k = seg(t, nodeAt(m, n.i), nodeAt(m, n.i) + 0.6), per = 2 * (n.w + n.h);
        s += `<rect x="${n.x}" y="${n.y}" width="${n.w}" height="${n.h}" fill="none" stroke="#e6f0ff" stroke-width="1.5" stroke-dasharray="${per}" stroke-dashoffset="${per * (1 - k)}"/>`;
        s += `<text x="${n.x + n.w / 2}" y="${n.y + n.h / 2 + 5}" text-anchor="middle" font-family="ui-monospace, Menlo, monospace" font-size="${fit(n.label, n.w - 12, 20, 0.62)}" fill="#e6f0ff" opacity="${seg(k, 0.6, 1)}">${esc(n.label)}</text>`;
      }
      for (const f of m.flow) {
        const [x1, y1, x2, y2] = ends(L[f[0]], L[f[1]]), k = seg(t, flowAt(m, L, f), flowAt(m, L, f) + 0.5);
        s += `<line x1="${x1}" y1="${y1}" x2="${x1 + (x2 - x1) * k}" y2="${y1 + (y2 - y1) * k}" stroke="#ffd166" stroke-width="1.5" stroke-dasharray="6 4"/>`;
        if (f[2] && k > 0.8) s += `<text x="${(x1 + x2) / 2}" y="${(y1 + y2) / 2 - 8}" text-anchor="middle" font-family="ui-monospace, Menlo, monospace" font-size="12" fill="#ffd166">${esc(f[2])}</text>`;
      }
      return s;
    } },
  };

  const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const cards = BOARD.looks.map((look, i) => {
    const draw = look.look === "custom" ? new Function("m", "t", look.js) : LOOKS[look.look].draw;
    return { svg: document.getElementById(`look-${i}`), draw };
  });
  const t0 = performance.now();
  const frame = (now) => {
    const t = reduced ? 4.5 : ((now - t0) / 1000) % 6;
    for (const c of cards) c.svg.innerHTML = c.draw(BOARD.moment, t);
    if (!reduced) requestAnimationFrame(frame);
  };
  requestAnimationFrame(frame);
  window.BOARD_LOOKS = Object.fromEntries(Object.entries(LOOKS).map(([k, v]) => [k, v.name]));
})();
