// Excalidraw look: reveal tagged SVG elements on spoken-word cues. Filled in by build_page.py.
// SPEC: { scene: [[element id, "show" | "draw", word, occurrence across the whole script], ...] }
const SPEC = %SPEC%;
const SCENES = {};
for (const [sid, items] of Object.entries(SPEC)) {
  const cues = items.map(([id, kind, word, n]) => [id, kind, Explainer.cue(TIMINGS, word, n)]);
  SCENES[sid] = (el, local, p, t) => {
    for (const [id, kind, at] of cues) {
      const k = Explainer.seg(t, at - 0.1, at + (kind === "draw" ? 0.9 : 0.35));
      const self = el.querySelector(`[data-id="${id}"]`);
      // place.py writes labels as free text with ids <id>-label and <id>-title; bound text carries data-container.
      const parts = [...el.querySelectorAll(`[data-id="${id}-label"],[data-id="${id}-title"],[data-container="${id}"]`)];
      if (kind === "show") {
        self.setAttribute("opacity", k);
        parts.forEach((g) => g.setAttribute("opacity", k));
        continue;
      }
      // Arrow: the shaft comes first, arrowheads after. Round caps draw a dot at zero length, so hide the shaft at 0.
      const [shaft, ...heads] = self.children;
      shaft.setAttribute("opacity", k > 0 ? 1 : 0);
      (shaft.tagName === "path" ? [shaft] : shaft.querySelectorAll("path")).forEach((pth) => {
        const len = pth.getTotalLength();
        pth.style.strokeDasharray = len;
        pth.style.strokeDashoffset = len * (1 - k);
      });
      heads.forEach((h) => h.setAttribute("opacity", Explainer.seg(k, 0.85, 1)));
      parts.forEach((g) => g.setAttribute("opacity", Explainer.seg(k, 0.5, 1)));
    }
  };
}
