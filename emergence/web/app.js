"use strict";
// Emergence Lab dashboard. Plain JS, no build step.
// All frames come from the Python engine (/api/frames), replayed from stored specs.

const $ = (s, el = document) => el.querySelector(s);
const h = (tag, attrs = {}, ...kids) => {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") el.className = v;
    else if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
    else if (v !== undefined && v !== null) el.setAttribute(k, v);
  }
  for (const k of kids.flat()) if (k !== null && k !== undefined) el.append(k);
  return el;
};
const api = async (path) => {
  const r = await fetch(path);
  const j = await r.json();
  if (!r.ok) throw new Error(j.error || r.statusText);
  return j;
};
const fmt = (v, d = 3) => v === null || v === undefined ? "–" : typeof v === "number" ? (Number.isInteger(v) ? String(v) : v.toFixed(d)) : String(v);

// Fixed class -> categorical slot mapping (color follows the entity, never rank).
const CLASS_SLOT = { complex: 1, chaotic: 2, periodic: 3, drifting: 4, active: 5, frozen: 6, saturated: 7, extinct: 8 };
const classColor = (c) => `var(--s${CLASS_SLOT[c] || 1})`;
const chip = (c) => h("span", { class: "chip", title: (S.meta?.class_help || {})[c] || "" }, h("i", { style: `background:${classColor(c)}` }), c);

const S = { meta: null, exp: null, universes: [], byId: new Map(), discoveries: [], panels: [], focus: null, hiddenClasses: new Set() };

// ------------------------------------------------------------ cell rendering
// Universe view uses its own dark "observation window" in both themes.
function cellPalette(n) {
  const pal = [[16, 17, 19], [242, 239, 230]];
  for (let s = 2; s < n; s++) {               // refractory / dying states fade orange -> dim
    const f = (s - 2) / Math.max(1, n - 3);
    pal.push([Math.round(235 - 165 * f), Math.round(104 - 60 * f), Math.round(52 - 10 * f)]);
  }
  return pal;
}
function paint(ctx, data, w, hgt, n) {
  const pal = cellPalette(Math.max(n, 2));
  const img = ctx.createImageData(w, hgt);
  for (let i = 0; i < w * hgt; i++) {
    const c = pal[Math.min(data[i], pal.length - 1)];
    img.data[i * 4] = c[0]; img.data[i * 4 + 1] = c[1]; img.data[i * 4 + 2] = c[2]; img.data[i * 4 + 3] = 255;
  }
  ctx.putImageData(img, 0, 0);
}
const b64bytes = (s) => Uint8Array.from(atob(s), (c) => c.charCodeAt(0));
const numStates = (rule) => { const m = /\/C(\d+)/i.exec(rule || ""); return m ? +m[1] : 2; };

// ------------------------------------------------------------ tooltip
const tip = $("#tooltip");
function showTip(e, html) { tip.innerHTML = html; tip.hidden = false; tip.style.left = (e.clientX + 12) + "px"; tip.style.top = (e.clientY + 12) + "px"; }
function hideTip() { tip.hidden = true; }

// ------------------------------------------------------------ boot
async function boot() {
  S.meta = await api("/api/meta");
  const cf = $("#class-filter");
  for (const c of S.meta.classes) cf.append(h("option", { value: c }, c));
  const exps = await api("/api/experiments");
  const sel = $("#exp-select");
  if (!exps.length) sel.append(h("option", {}, "(no experiments yet — run `emergence explore`)"));
  for (const e of exps) sel.append(h("option", { value: e.id }, `#${e.id} ${e.name} (${e.n_universes})`));
  sel.onchange = () => loadExperiment(+sel.value);
  for (const id of ["#sort", "#class-filter", "#role-filter"]) $(id).onchange = renderGallery;
  $("#animate").onchange = renderGallery;
  $("#sync").onchange = () => { if ($("#sync").checked) syncFrom(S.focus); };
  document.querySelectorAll(".tabs button").forEach((b) => b.onclick = () => setTab(b.dataset.tab));
  $("#adhoc").onsubmit = (e) => {
    e.preventDefault();
    const f = new FormData(e.target);
    openPanel({ kind: "adhoc", rule: f.get("rule").trim().toUpperCase(), seed: +f.get("seed"), size: +f.get("size") }, e.shiftKey === false);
  };
  $("#theme-toggle").onclick = () => {
    const cur = document.documentElement.dataset.theme || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    document.documentElement.dataset.theme = cur === "dark" ? "light" : "dark";
  };
  document.addEventListener("keydown", onKey);
  const hash = new URLSearchParams(location.hash.slice(1));
  const want = +hash.get("exp") || (exps[0] && exps[0].id);
  if (want) { sel.value = want; await loadExperiment(want); }
  for (const id of (hash.get("open") || "").split(",").filter(Boolean)) openPanel({ kind: "id", id: +id }, false);
}

function setTab(t) {
  document.querySelectorAll(".tabs button").forEach((b) => b.classList.toggle("active", b.dataset.tab === t));
  $("#tab-explore").hidden = t !== "explore";
  $("#tab-discoveries").hidden = t !== "discoveries";
}

function updateHash() {
  const open = S.panels.filter((p) => p.src.kind === "id").map((p) => p.src.id).join(",");
  history.replaceState(null, "", `#exp=${S.exp?.id || ""}${open ? "&open=" + open : ""}`);
}

async function loadExperiment(id) {
  const d = await api(`/api/experiment/${id}`);
  S.exp = d.experiment; S.universes = d.universes; S.discoveries = d.discoveries;
  S.byId = new Map(d.universes.map((u) => [u.id, u]));
  for (const u of S.universes) u.thumbBytes = b64bytes(u.thumb);
  renderSummary(); renderGallery(); renderDiscoveries(); updateHash();
}

// ------------------------------------------------------------ summary
function renderSummary() {
  const el = $("#summary"); el.innerHTML = "";
  const ex = S.universes.filter((u) => u.role === "explore");
  const counts = {}; for (const c of S.meta.classes) counts[c] = 0;
  for (const u of ex) counts[u.class] = (counts[u.class] || 0) + 1;
  const cfg = S.exp.config, env = S.exp.environment;
  el.append(h("div", { class: "stats" },
    h("span", {}, "Universes ", h("b", {}, ex.length)),
    h("span", {}, "Generations ", h("b", {}, cfg.generations)),
    h("span", {}, "Grid ", h("b", {}, `${cfg.width}×${cfg.height}`)),
    h("span", {}, "Steps ", h("b", {}, cfg.steps)),
    h("span", {}, "Master seed ", h("b", {}, S.exp.master_seed)),
    h("span", {}, "Pareto front ", h("b", {}, ex.filter((u) => u.pareto_rank === 0).length)),
    h("span", {}, "Discoveries ", h("b", {}, S.discoveries.length)),
    h("span", { title: JSON.stringify(env) }, "Status ", h("b", {}, S.exp.status)),
  ));
  const total = ex.length || 1;
  const bar = h("div", { class: "classbar", role: "img", "aria-label": "Class distribution" });
  const legend = h("div", { class: "legend" });
  for (const c of S.meta.classes) {
    if (!counts[c]) continue;
    const pct = (100 * counts[c] / total).toFixed(0);
    const seg = h("div", { style: `flex:${counts[c]};background:${classColor(c)}` });
    seg.onmousemove = (e) => showTip(e, `<b>${c}</b>: ${counts[c]} (${pct}%)<br>${S.meta.class_help[c]}`);
    seg.onmouseleave = hideTip;
    seg.onclick = () => { $("#class-filter").value = $("#class-filter").value === c ? "" : c; renderGallery(); };
    bar.append(seg);
    const item = h("span", { title: S.meta.class_help[c] }, h("i", { class: "swatch", style: `background:${classColor(c)}` }), `${c} ${counts[c]}`);
    item.onclick = seg.onclick;
    legend.append(item);
  }
  el.append(bar, legend);
}

// ------------------------------------------------------------ gallery
const sortKey = {
  priority: (u) => u.priority ?? 1e9,
  novelty: (u) => -(u.novelty ?? 0),
  generation: (u) => u.generation,
  transient: (u) => -(u.metrics.cycle_found ? u.metrics.transient : u.metrics.steps),
};
let animTimer = null, animQueue = [];
function renderGallery() {
  const g = $("#gallery"); g.innerHTML = "";
  clearInterval(animTimer); animQueue = [];
  const cls = $("#class-filter").value, role = $("#role-filter").value, sk = $("#sort").value;
  let list = S.universes.filter((u) => (!cls || u.class === cls) && (!role || u.role === role));
  const key = sortKey[sk] || ((u) => -(u.metrics[sk] ?? 0));
  list = list.slice().sort((a, b) => key(a) - key(b) || a.id - b.id);
  const animate = $("#animate").checked;
  const cards = [];
  for (const u of list) {
    const cv = h("canvas", { width: u.spec.width, height: u.spec.height });
    paint(cv.getContext("2d"), u.thumbBytes, u.spec.width, u.spec.height, numStates(u.rule));
    const card = h("div", { class: "card", "data-id": u.id, title: `#${u.id} ${u.rule} — ${u.class}` },
      cv, h("div", { class: "rule" }, u.rule),
      h("div", { class: "meta" }, chip(u.class), h("span", {}, u.priority ? `#${u.priority}` : u.role === "followup" ? "re-run" : "")));
    card.onclick = (e) => openPanel({ kind: "id", id: u.id }, !e.shiftKey);
    g.append(card);
    cards.push({ u, cv, frames: null, t: 0, loading: false });
  }
  markOpenCards();
  if (animate) startGalleryAnimation(cards);
}
function markOpenCards() {
  const ids = new Set(S.panels.filter((p) => p.src.kind === "id").map((p) => p.src.id));
  document.querySelectorAll(".card").forEach((c) => c.classList.toggle("open", ids.has(+c.dataset.id)));
}
function startGalleryAnimation(cards) {
  const visible = new Set();
  const io = new IntersectionObserver((ents) => ents.forEach((e) => e.isIntersecting ? visible.add(e.target) : visible.delete(e.target)), { root: $("#gallery") });
  const byCanvas = new Map(cards.map((c) => [c.cv, c]));
  cards.forEach((c) => io.observe(c.cv));
  let inflight = 0;
  animTimer = setInterval(() => {
    for (const cv of visible) {
      const c = byCanvas.get(cv);
      if (!c.frames && !c.loading && inflight < 4) {
        c.loading = true; inflight++;
        api(`/api/frames?id=${c.u.id}&start=0&count=200`).then((d) => { c.frames = b64bytes(d.frames); c.n = d.count; })
          .finally(() => { inflight--; c.loading = false; });
      }
      if (c.frames) {
        const fs = c.u.spec.width * c.u.spec.height;
        c.t = (c.t + 1) % c.n;
        paint(c.cv.getContext("2d"), c.frames.subarray(c.t * fs, (c.t + 1) * fs), c.u.spec.width, c.u.spec.height, numStates(c.u.rule));
      }
    }
  }, 80);
}

// ------------------------------------------------------------ viewer panels
const CHUNK = 200, MAX_BUFFER = 4000;
class Panel {
  constructor(src) {
    this.src = src; this.frames = []; this.t = 0; this.playing = false; this.speed = 15;
    this.zoom = 1; this.ox = 0; this.oy = 0; this.loading = null; this.horizon = 0;
    this.u = src.kind === "id" ? S.byId.get(src.id) : null;
    this.build();
    this.ensure(0).then(() => this.draw());
  }
  query(start, count) {
    const s = this.src;
    return s.kind === "id" ? `/api/frames?id=${s.id}&start=${start}&count=${count}`
      : `/api/frames?rule=${encodeURIComponent(s.rule)}&seed=${s.seed}&w=${s.size}&density=0.35&start=${start}&count=${count}`;
  }
  async ensure(t) {
    while (t >= this.frames.length && this.frames.length < MAX_BUFFER) {
      if (!this.loading) {
        const start = this.frames.length;
        this.loadEl.textContent = "loading…";
        this.loading = api(this.query(start, CHUNK)).then((d) => {
          this.w = d.width; this.hgt = d.height; this.n = d.num_states; this.rule = d.rule;
          const bytes = b64bytes(d.frames), fs = d.width * d.height;
          for (let i = 0; i < d.count; i++) this.frames.push(bytes.subarray(i * fs, (i + 1) * fs));
          if (this.off.width !== d.width) { this.off.width = d.width; this.off.height = d.height; }
          this.loadEl.textContent = "";
        }).catch((e) => { this.loadEl.textContent = "error: " + e.message; this.playing = false; throw e; })
          .finally(() => { this.loading = null; });
      }
      await this.loading;
    }
  }
  build() {
    const u = this.u;
    const title = u ? `#${u.id} ${u.rule}` : `${this.src.rule} · seed ${this.src.seed} · ${this.src.size}²`;
    this.canvas = h("canvas");
    this.off = document.createElement("canvas");
    this.loadEl = h("span", { class: "loading" });
    this.stage = h("div", { class: "stage" }, this.canvas, this.loadEl);
    this.scrub = h("input", { type: "range", class: "scrub", min: 0, max: 0, value: 0, "aria-label": "Time" });
    this.tEl = h("span", { class: "t" }, "t=0");
    this.playBtn = h("button", { title: "Play/pause (Space)" }, "▶");
    const speed = h("input", { type: "range", min: 1, max: 60, value: this.speed, title: "Speed (steps/s)", "aria-label": "Speed", style: "width:70px" });
    this.el = h("div", { class: "panel" },
      h("header", {}, h("span", { class: "title", title }, title), u ? chip(u.class) : h("span", { class: "chip" }, "ad-hoc"),
        h("button", { class: "close ghost", title: "Close", onclick: () => closePanel(this) }, "×")),
      this.stage,
      h("div", { class: "controls" },
        h("button", { title: "Rewind to start", onclick: () => this.seek(0) }, "⏮"),
        h("button", { title: "Step back (←)", onclick: () => this.seek(this.t - 1) }, "◀"),
        this.playBtn,
        h("button", { title: "Step forward (→)", onclick: () => this.seek(this.t + 1) }, "▶|"),
        this.scrub, this.tEl, speed,
        h("button", { class: "ghost", title: "Reset zoom", onclick: () => { this.zoom = 1; this.ox = this.oy = 0; this.draw(); } }, "⤢")));
    this.playBtn.onclick = () => this.toggle();
    speed.oninput = () => { this.speed = +speed.value; };
    this.scrub.oninput = () => this.seek(+this.scrub.value);
    this.el.addEventListener("pointerdown", () => setFocus(this));
    // zoom & pan
    this.stage.addEventListener("wheel", (e) => {
      e.preventDefault();
      const r = this.stage.getBoundingClientRect();
      const mx = (e.clientX - r.left) / r.width, my = (e.clientY - r.top) / r.height;
      const nz = Math.min(32, Math.max(1, this.zoom * (e.deltaY < 0 ? 1.2 : 1 / 1.2)));
      this.ox = mx - (mx - this.ox) * nz / this.zoom; this.oy = my - (my - this.oy) * nz / this.zoom;
      this.zoom = nz; this.clampView(); this.draw();
    }, { passive: false });
    let drag = null;
    this.stage.addEventListener("pointerdown", (e) => { drag = { x: e.clientX, y: e.clientY, ox: this.ox, oy: this.oy }; this.stage.setPointerCapture(e.pointerId); });
    this.stage.addEventListener("pointermove", (e) => {
      if (!drag) return;
      const r = this.stage.getBoundingClientRect();
      this.ox = drag.ox + (e.clientX - drag.x) / r.width; this.oy = drag.oy + (e.clientY - drag.y) / r.height;
      this.clampView(); this.draw();
    });
    this.stage.addEventListener("pointerup", () => { drag = null; });
    this.stage.addEventListener("dblclick", () => { this.zoom = 1; this.ox = this.oy = 0; this.draw(); });
    new ResizeObserver(() => this.draw()).observe(this.stage);
  }
  clampView() {
    this.ox = Math.min(0, Math.max(1 - this.zoom, this.ox));
    this.oy = Math.min(0, Math.max(1 - this.zoom, this.oy));
  }
  async seek(t, fromSync = false) {
    t = Math.max(0, Math.min(MAX_BUFFER - 1, t));
    await this.ensure(t);
    this.t = Math.min(t, this.frames.length - 1);
    this.draw();
    if (!fromSync && $("#sync").checked) syncFrom(this);
    if (S.focus === this) updateCursor(this.t);
  }
  toggle(force) {
    this.playing = force ?? !this.playing;
    this.playBtn.textContent = this.playing ? "⏸" : "▶";
    if (!fromSyncGuard && $("#sync").checked) for (const p of S.panels) if (p !== this) { fromSyncGuard = true; p.toggle(this.playing); fromSyncGuard = false; }
    if (this.playing) this.loop();
  }
  async loop() {
    let last = performance.now(), acc = 0;
    const tick = async (now) => {
      if (!this.playing || !this.el.isConnected) return;
      acc += (now - last) * this.speed / 1000; last = now;
      if (acc >= 1) {
        const n = Math.floor(acc); acc -= n;
        if (this.t + n >= this.frames.length) {
          if (this.frames.length >= MAX_BUFFER) { this.toggle(false); return; }
          await this.ensure(this.t + n); last = performance.now();
        }
        this.t = Math.min(this.t + n, this.frames.length - 1);
        this.draw();
        if (S.focus === this) updateCursor(this.t);
      }
      requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }
  draw() {
    const f = this.frames[this.t];
    const r = this.stage.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    const W = Math.max(1, Math.round(r.width * dpr)), H = Math.max(1, Math.round(r.height * dpr));
    if (this.canvas.width !== W || this.canvas.height !== H) { this.canvas.width = W; this.canvas.height = H; }
    if (!f) return;
    paint(this.off.getContext("2d"), f, this.w, this.hgt, this.n);
    const ctx = this.canvas.getContext("2d");
    ctx.imageSmoothingEnabled = false;
    ctx.fillStyle = "#101113"; ctx.fillRect(0, 0, W, H);
    // keep cells square
    const side = Math.min(W / this.w, H / this.hgt);
    const gw = side * this.w, gh = side * this.hgt, x0 = (W - gw) / 2, y0 = (H - gh) / 2;
    ctx.drawImage(this.off, x0 + this.ox * gw, y0 + this.oy * gh, gw * this.zoom, gh * this.zoom);
    this.scrub.max = Math.max(this.frames.length - 1, this.u ? this.u.steps : 0);
    this.scrub.value = this.t;
    this.tEl.textContent = `t=${this.t}`;
  }
}
let fromSyncGuard = false;
function syncFrom(src) {
  if (!src) return;
  for (const p of S.panels) if (p !== src) p.seek(src.t, true);
}

function openPanel(src, replace) {
  if (src.kind === "id" && !S.byId.has(src.id)) return;
  if (replace) { for (const p of S.panels) p.playing = false; S.panels = []; }
  const existing = S.panels.find((p) => JSON.stringify(p.src) === JSON.stringify(src));
  if (existing) { setFocus(existing); return; }
  if (S.panels.length >= 4) { S.panels[0].playing = false; S.panels.shift(); }
  const p = new Panel(src);
  S.panels.push(p);
  layoutPanels(); setFocus(p); updateHash(); markOpenCards();
}
function closePanel(p) {
  p.playing = false;
  S.panels = S.panels.filter((x) => x !== p);
  if (S.focus === p) S.focus = null;
  layoutPanels(); setFocus(S.panels[S.panels.length - 1] || null); updateHash(); markOpenCards();
}
function layoutPanels() {
  const el = $("#panels"); el.innerHTML = "";
  el.className = `panels n${S.panels.length}`;
  if (!S.panels.length) el.append(h("div", { class: "empty" }, "Select a universe on the left."));
  for (const p of S.panels) el.append(p.el);
  for (const p of S.panels) p.draw();
}
function setFocus(p) {
  if (S.focus === p && p) return;
  S.focus = p;
  for (const x of S.panels) x.el.classList.toggle("focus", x === p);
  renderDetails(p);
}
function onKey(e) {
  if (["INPUT", "SELECT", "TEXTAREA"].includes(document.activeElement?.tagName)) return;
  const p = S.focus; if (!p) return;
  if (e.code === "Space") { e.preventDefault(); p.toggle(); }
  else if (e.key === "ArrowRight") p.seek(p.t + 1);
  else if (e.key === "ArrowLeft") p.seek(p.t - 1);
}

// ------------------------------------------------------------ details
const METRIC_LABELS = [
  ["class", "Class"], ["activity_late", "Activity (late)"], ["activity_persistence", "Activity persistence"],
  ["density_late", "Density (late)"], ["entropy_late", "2×2 block entropy"],
  ["spatial_ratio_late", "Spatial compressibility vs noise"], ["spacetime_ratio", "Space-time compressibility vs noise"],
  ["damage_norm", "Damage spreading (0 heal · 1 chaos)"], ["period", "Cycle period"], ["transient", "Transient length"],
  ["cycle_shift", "Cycle drift (dy,dx)"], ["still_structures", "Still structures"], ["vocabulary", "Persistent shapes"],
  ["mover_shapes", "Moving shapes"], ["mover_events", "Mover sightings"], ["mover_velocities", "Distinct velocities"],
  ["local_periodic_frac", "Changing cells that oscillate locally"], ["objects_per_frame", "Objects / frame"], ["langton_lambda", "Langton λ (rule)"],
];
let cursorFns = [];
function updateCursor(t) { for (const f of cursorFns) f(t); }

async function renderDetails(p) {
  const el = $("#details"); el.innerHTML = ""; cursorFns = [];
  if (!p) return;
  if (!p.u) {
    el.append(h("div", { class: "box" }, h("h3", {}, "Ad-hoc universe"),
      h("p", { class: "hint" }, "Rendered live by the engine; not part of an experiment, so no observatory record. Run `emergence observe " + p.src.rule + "` for measurements.")));
    return;
  }
  const u = await api(`/api/universe/${p.u.id}`);
  if (S.focus !== p) return;
  const m = u.metrics;
  const tbl = h("table", { class: "metrics" });
  tbl.append(h("tr", {}, h("td", {}, "Universe"), h("td", {}, `#${u.id} · gen ${u.generation} · ${u.role}`)));
  tbl.append(h("tr", {}, h("td", {}, "Seed / density / size"), h("td", {}, `${u.spec.seed} / ${u.spec.density} / ${u.spec.width}×${u.spec.height}`)));
  tbl.append(h("tr", {}, h("td", {}, "Priority / Pareto rank / novelty"), h("td", {}, `${fmt(u.priority)} / ${fmt(u.pareto_rank)} / ${fmt(u.novelty)}`)));
  for (const [k, label] of METRIC_LABELS) tbl.append(h("tr", {}, h("td", {}, label), h("td", {}, Array.isArray(m[k]) ? m[k].join(",") : fmt(m[k]))));
  tbl.append(h("tr", {}, h("td", {}, "Final-state hash"), h("td", { title: u.final_hash }, u.final_hash.slice(0, 12) + "…")));
  el.append(h("div", { class: "box" }, h("h3", {}, `Measurements · ${u.rule}`), tbl,
    h("p", { class: "hint" }, `Class: ${S.meta.class_help[u.class] || ""}`)));

  const ts = u.timeseries;
  const charts = h("div", { class: "box" }, h("h3", {}, "History (observatory samples)"));
  charts.append(spark("Activity (fraction of cells changed)", ts.t, ts.activity));
  charts.append(spark("Density", ts.t, ts.density));
  charts.append(spark("2×2 block entropy", ts.t, ts.entropy));
  charts.append(spark("Spatial compressibility vs noise (1 = noise)", ts.t, ts.spatial_ratio));
  if (ts.damage_curve?.length) {
    const t0 = u.steps - ts.damage_curve.length;
    charts.append(spark("Damage from one flipped cell (twin experiment)", ts.damage_curve.map((_, i) => t0 + i + 1), ts.damage_curve));
  }
  el.append(charts);

  const disc = S.discoveries.filter((d) => d.universe_id === u.id || (d.evidence.replicate_ids || []).includes(u.id));
  const links = h("div", { class: "box links" }, h("h3", {}, "Lineage & investigations"));
  const link = (x) => h("a", { onclick: (e) => openPanel({ kind: "id", id: x.id }, !e.shiftKey) }, `#${x.id} ${x.rule}`);
  if (u.lineage.length) links.append(h("div", {}, "Ancestors (mutation chain):"), h("ul", {}, u.lineage.map((x) => h("li", {}, link(x), " ", chip(x.class), ` gen ${x.generation}`))));
  else links.append(h("div", { class: "hint" }, u.role === "explore" ? "No parent: random rule (generation 0 or immigrant)." : ""));
  const reps = u.children.filter((c) => c.role === "followup"), kids = u.children.filter((c) => c.role !== "followup");
  if (reps.length) links.append(h("div", {}, "Robustness re-runs (new seeds / larger world):"), h("ul", {}, reps.map((x) => h("li", {}, link(x), " ", chip(x.class), ` ${x.size}²`))));
  if (kids.length) links.append(h("div", {}, `Mutant offspring (${kids.length}):`), h("ul", {}, kids.slice(0, 12).map((x) => h("li", {}, link(x), " ", chip(x.class)))));
  for (const d of disc) links.append(h("div", { style: "margin-top:8px" }, h("b", {}, `Discovery [${d.kind}]`), h("div", { class: "hint" }, d.summary)));
  el.append(links);
  updateCursor(p.t);
}

function spark(label, xs, ys) {
  const W = 300, H = 44, n = ys.length;
  const valEl = h("span", {}, n ? fmt(ys[n - 1], 4) : "");
  const wrap = h("div", { class: "spark" }, h("div", { class: "lbl" }, h("span", {}, label), valEl));
  if (!n) return wrap;
  const x0 = xs[0], x1 = xs[n - 1] || 1, ymax = Math.max(...ys, 1e-9), ymin = Math.min(0, ...ys);
  const X = (x) => (x - x0) / Math.max(1e-9, x1 - x0) * W, Y = (y) => H - 2 - (y - ymin) / (ymax - ymin) * (H - 4);
  const ns = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(ns, "svg");
  svg.setAttribute("viewBox", `0 0 ${W} ${H}`); svg.setAttribute("preserveAspectRatio", "none");
  svg.innerHTML = `<line class="base" x1="0" x2="${W}" y1="${H - 1}" y2="${H - 1}"/>` +
    `<path class="line" vector-effect="non-scaling-stroke" d="${ys.map((y, i) => `${i ? "L" : "M"}${X(xs[i]).toFixed(1)},${Y(y).toFixed(1)}`).join("")}"/>` +
    `<line class="cursor" vector-effect="non-scaling-stroke" y1="0" y2="${H}"/><line class="hover" vector-effect="non-scaling-stroke" y1="0" y2="${H}" visibility="hidden"/>`;
  const cur = svg.querySelector(".cursor"), hov = svg.querySelector(".hover");
  cursorFns.push((t) => { const x = Math.max(0, Math.min(W, X(t))); cur.setAttribute("x1", x); cur.setAttribute("x2", x); });
  svg.addEventListener("mousemove", (e) => {
    const r = svg.getBoundingClientRect();
    const xt = x0 + (e.clientX - r.left) / r.width * (x1 - x0);
    let i = 0; while (i < n - 1 && xs[i + 1] <= xt) i++;
    const x = X(xs[i]); hov.setAttribute("x1", x); hov.setAttribute("x2", x); hov.setAttribute("visibility", "visible");
    showTip(e, `t=${xs[i]}<br><b>${fmt(ys[i], 4)}</b>`);
  });
  svg.addEventListener("mouseleave", () => { hov.setAttribute("visibility", "hidden"); hideTip(); });
  svg.addEventListener("click", (e) => {
    const r = svg.getBoundingClientRect();
    if (S.focus) S.focus.seek(Math.round(x0 + (e.clientX - r.left) / r.width * (x1 - x0)));
  });
  svg.style.cursor = "pointer";
  wrap.append(svg);
  return wrap;
}

// ------------------------------------------------------------ discoveries tab
function renderDiscoveries() {
  $("#disc-count").textContent = S.discoveries.length || "";
  const el = $("#disc-list"); el.innerHTML = "";
  if (!S.discoveries.length) el.append(h("p", { class: "hint" }, "No discoveries recorded for this experiment."));
  for (const d of S.discoveries) {
    const u = S.byId.get(d.universe_id);
    const cv = h("canvas", { width: u.spec.width, height: u.spec.height });
    paint(cv.getContext("2d"), u.thumbBytes, u.spec.width, u.spec.height, numStates(u.rule));
    const ev = d.evidence;
    el.append(h("div", { class: "disc", onclick: () => { setTab("explore"); openPanel({ kind: "id", id: u.id }, true); } },
      cv, h("div", {}, h("div", { class: "kind" }, d.kind), h("div", { class: "rule" }, `#${u.id} ${u.rule} `, chip(u.class)),
        h("div", { class: "sum" }, d.summary),
        h("div", { class: "hint" }, `Pareto rank ${fmt(ev.pareto_rank)} · novelty ${fmt(ev.novelty)} · re-run classes: ${ev.replicate_classes.join(", ")}`))));
  }
}

boot().catch((e) => { document.body.prepend(h("pre", { style: "color:var(--s8);padding:16px" }, "Failed to load: " + e.message)); });
