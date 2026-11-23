#!/usr/bin/env python3
"""Generate the interactive HTML/Canvas figures for site/figures/taurid-swarm/.

Reads ONLY locked results/ and primary data/ catalogs. Produces five self-contained,
zero-dependency fragments for site/content/taurid-swarm.md:
  1. tiles.html     - Headline tiles
  2. verdict.html   - Verdict panel
  3. orrery.html    - The orbits, seen from above
  4. radar.html     - Which way the orbits point
  5. fireballs.html - Airbursts seen by satellite, 1994 to 2025

The figures share the site's night-blue panel (the same treatment as the ancient-sky-hole
figures): site fonts through the tokens, copper for Comet Encke and the selected state,
cream for asteroids aligned with Encke, pale blue rings for the rest, slate for Jupiter and
the comparison group. No glows, shadows or gradients.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Dict

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT.parent.parent
RESULTS = ROOT / "results"
OUT_DIR = REPO / "site" / "figures" / "taurid-swarm"

sys.path.insert(0, str(ROOT / "analysis"))
import taurid as td


# The site's band tokens (site/assets/site.css) are re-pointed to blues on the panel only; copper,
# ochre, verdigris and the cream ink stay the site's. `.fig` prefixes beat `.prose p` / `.prose h3`.
# Copied from questions/ancient-sky-hole/analysis/make_figures.py so the two pages match.
PANEL_CSS = """
.fig .sky-panel {
  --band: #0d1421; --band-soft: #131c2c; --band-line: #2a3750;
  --band-ink: #f6f1e8; --band-ink-soft: #cdd3de; --band-faint: #8f9bb1; --band-slate: #c9daf0;
  --band-copper: #d08a5c; --band-verdigris: #7fb39d; --band-ochre: #cfa544;
  background: var(--band); color: var(--band-ink-soft);
  border: 1px solid var(--band-line); border-radius: 3px; overflow: hidden;
  font-family: var(--sans);
}
.fig .sky-head {
  display: flex; flex-wrap: wrap; align-items: baseline; justify-content: space-between;
  gap: 0.5rem 1.25rem; padding: 1rem 1.25rem 0.85rem; border-bottom: 1px solid var(--band-line);
}
.fig .sky-eyebrow {
  font: 500 10.5px/1.4 var(--mono); text-transform: uppercase; letter-spacing: 0.12em;
  color: var(--band-faint); margin: 0 0 0.3rem;
}
.fig .sky-title { font: 400 1.3rem/1.25 var(--serif); color: var(--band-ink); margin: 0; letter-spacing: -0.005em; }
.fig .sky-legend {
  display: flex; flex-wrap: wrap; gap: 0.35rem 1.4rem; margin: 0;
  padding: 0.6rem 1.25rem 0.7rem; font: 400 0.84rem/1.4 var(--sans); color: var(--band-ink-soft);
}
.fig .sky-legend .key { display: inline-flex; align-items: center; gap: 0.4rem; }
.fig .sky-legend svg { flex: none; }
.fig .sky-btn {
  font: 400 0.8rem/1.25 var(--sans); padding: 0.4rem 0.7rem; border-radius: 3px; cursor: pointer;
  background: transparent; border: 1px solid var(--band-line); color: var(--band-ink-soft);
}
.fig .sky-btn:hover { border-color: var(--band-faint); color: var(--band-ink); }
.fig .sky-btn.is-active, .fig .sky-btn[aria-pressed="true"] {
  border-color: var(--band-copper); color: var(--band-ink);
  background: color-mix(in oklab, var(--band-copper) 16%, transparent);
}
.fig .sky-panel :focus-visible { outline: 2px solid var(--band-copper); outline-offset: 2px; }
.fig .sky-panel input[type="checkbox"] { accent-color: var(--band-copper); }
.fig .sky-panel strong { color: var(--band-ink); font-weight: 600; }
"""

# Read-out strip and button row shared by the three figures (same sizes as the sky-hole figures).
SHARED_CSS = """
.fig .ts-readout { font: 400 0.9rem/1.3 var(--sans); color: var(--band-ink); font-variant-numeric: tabular-nums; }
.fig .ts-hud {
  display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1px;
  background: var(--band-line); border-top: 1px solid var(--band-line); border-bottom: 1px solid var(--band-line);
}
.fig .ts-hud-cell { background: var(--band-soft); padding: 0.7rem 0.9rem; text-align: center; }
.fig .ts-hud-val { font: 600 1.05rem/1.2 var(--sans); font-variant-numeric: tabular-nums; color: var(--band-ink); }
.fig .ts-hud-lbl { font: 400 0.78rem/1.4 var(--sans); color: var(--band-ink-soft); margin-top: 0.25rem; }
.fig .ts-controls {
  display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between;
  gap: 0.6rem 1rem; padding: 0.9rem 1.25rem 1.1rem; background: var(--band-soft);
}
.fig .ts-tabs { display: flex; flex-wrap: wrap; gap: 0.4rem; }
.fig .ts-bar {
  padding: 0.7rem 1.25rem 0.9rem; border-top: 1px solid var(--band-line); background: var(--band-soft);
  font: 400 0.8rem/1.45 var(--sans); color: var(--band-ink-soft); font-variant-numeric: tabular-nums;
}
.fig .ts-note { margin: 0; padding: 0.55rem 1.25rem 0.65rem; font: 400 0.8rem/1.45 var(--sans); color: var(--band-ink-soft); }
.fig .ts-note:empty { display: none; }
@media (max-width: 44rem) { .fig .ts-hud { grid-template-columns: 1fr; } }
"""

# Canvas colours, matching PANEL_CSS (JS object literal).
JS_COLOURS = (
    'const C = { band: "#0d1421", soft: "#131c2c", line: "#2a3750", ink: "#f6f1e8", inkSoft: "#cdd3de", '
    'faint: "#8f9bb1", copper: "#d08a5c", cream: "#e9d7a8", pale: "#c9daf0", slate: "#9aa5b3", ochre: "#cfa544" };\n'
    '  const SANS = (getComputedStyle(document.documentElement).getPropertyValue("--sans") || "").trim() || "system-ui, sans-serif";'
)


def build_tiles_html(summary: Dict) -> str:
    a1 = summary["archive_a_neos"]["test_a1_alignment"]
    big = a1["H_lt_16.5"]["box_t"]
    km = a1["H_lt_18.0"]["box_t"]
    fb = summary["archive_b_fireballs_1994_2025"]
    aut = fb["test_b1_seasonality"]["autumn_taurids"]
    n_years = fb["years"][1] - fb["years"][0] + 1
    passed = summary["criteria_passed"]["total_passed"]
    n_crit = sum(1 for k in summary["criteria_passed"] if k != "total_passed")
    return f"""<div class="tiles">
<div class="tile"><p class="tile-value is-word">{big["n_45"]} of {big["n"]}</p><p class="tile-label">of the largest asteroids on Taurid-like orbits point the same way as Comet Encke: the observation the idea was built on</p></div>
<div class="tile"><p class="tile-value">{round(100 * km["f_45"])}%</p><p class="tile-label">of the {km["n"]} down to about a kilometre across point that way, where chance gives 25%: no alignment</p></div>
<div class="tile"><p class="tile-value">{aut["count"]}</p><p class="tile-label">airbursts seen by satellite in the autumn Taurid weeks over {n_years} years, where chance gives {aut["expected_count"]:.1f}</p></div>
<div class="tile"><p class="tile-value is-word">{passed} of {n_crit}</p><p class="tile-label">tests set in advance passed: no sign of a swarm of large fragments</p></div>
</div>
"""


def build_verdict_html(summary: Dict) -> str:
    return """<div class="verdict">
<div class="verdict-row">
  <div>
    <p class="verdict-kicker">The test fixed in advance</p>
    <p class="verdict-text">Is there a swarm of large fragments in the Taurid stream today?</p>
    <p class="verdict-note">None of four tests passed: not in the orbits of kilometre-sized asteroids, not in the 7:2 resonance, not in the airbursts of the Taurid weeks, not in the years the swarm was due back.</p>
  </div>
  <p class="verdict-status is-no"><span class="dot" aria-hidden="true"></span>Not found</p>
</div>
<div class="verdict-row">
  <div>
    <p class="verdict-kicker">What does hold</p>
    <p class="verdict-text">Eleven of the seventeen largest asteroids on such orbits line up with Comet Encke</p>
    <p class="verdict-note">This is the 2010 observation, and they are the same asteroids now as then, so it is not new evidence. The pattern does not continue to smaller bodies.</p>
  </div>
  <p class="verdict-status is-open"><span class="dot" aria-hidden="true"></span>Known since 2010</p>
</div>
<div class="verdict-row">
  <div>
    <p class="verdict-kicker">What it cannot show</p>
    <p class="verdict-text">What the stream held 12,900 years ago</p>
    <p class="verdict-note">Small debris is certainly there: it makes the Taurid meteors. A swarm of large pieces could have broken down since. The test is of large fragments today.</p>
  </div>
  <p class="verdict-status is-open"><span class="dot" aria-hidden="true"></span>Not tested</p>
</div>
</div>
"""


def build_orrery_html(cat: Dict, encke: Dict, summary: Dict) -> str:
    a, e, inc, H, varpi = cat["a"], cat["e"], cat["i"], cat["H"], cat["varpi"]
    d_varpi = td.ang_diff_deg(varpi, encke["varpi"])
    box_t = (a >= 1.83) & (a <= 2.70) & (e >= 0.63) & (e <= 1.00) & (inc <= 14.0)
    mask = box_t & (H < 20.0)
    idxs = np.where(mask)[0]
    idxs = idxs[np.argsort(H[idxs])]

    # Compact orbit records: [a, e, varpi, H, aligned45, res72, tight, phase, name, albedo]
    orbits = []
    for k, i in enumerate(idxs):
        al45 = 1 if abs(float(d_varpi[i])) <= 45.0 else 0
        res72 = 1 if (2.21 <= float(a[i]) <= 2.30 and al45 == 1) else 0
        tight = 1 if (res72 == 1 and float(e[i]) >= 0.75 and float(inc[i]) <= 12.0 and abs(float(d_varpi[i])) <= 30.0) else 0
        alb = None if math.isnan(cat["albedo"][i]) else round(float(cat["albedo"][i]), 3)
        orbits.append([
            round(float(a[i]), 3),
            round(float(e[i]), 3),
            round(float(varpi[i]), 1),
            round(float(H[i]), 2),
            al45,
            res72,
            tight,
            round(float(cat["ma"][i]), 1),
            str(cat["name"][i]),
            alb,
        ])

    payload = {
        "encke": {
            "a": round(encke["a"], 3),
            "e": round(encke["e"], 4),
            "varpi": round(encke["varpi"], 2),
        },
        "orbits": orbits,
    }
    payload_json = json.dumps(payload, separators=(",", ":"))

    return f"""<figure class="fig taurid-orrery-fig" id="taurid-orrery">
<style>
{PANEL_CSS}
{SHARED_CSS}
.orr-stage {{ position: relative; display: flex; justify-content: center; padding: 0.9rem 1rem 0.4rem; }}
.orr-wrap {{ position: relative; width: 100%; max-width: 640px; aspect-ratio: 1 / 1; }}
.orr-wrap canvas {{ display: block; width: 100%; height: 100%; }}
.fig .orr-play {{ white-space: nowrap; color: var(--band-ink); padding: 0.5rem 0.95rem; }}
</style>
<div class="sky-panel">
  <div class="sky-head">
    <div>
      <p class="sky-eyebrow">Asteroid orbits from NASA/JPL, 23 November 2026</p>
      <h3 class="sky-title">The orbits, seen from above</h3>
    </div>
    <div class="ts-readout" id="orr-badge" aria-live="polite">The 17 largest (about 2 km and up)</div>
  </div>
  <p class="sky-legend">
    <span class="key"><svg viewBox="0 0 16 12" width="16" height="12" aria-hidden="true"><line x1="0" x2="16" y1="6" y2="6" stroke="#d08a5c" stroke-width="2.2"/></svg>Comet Encke</span>
    <span class="key"><svg viewBox="0 0 12 12" width="12" height="12" aria-hidden="true"><circle cx="6" cy="6" r="4" fill="#e9d7a8"/></svg>Asteroids pointing within 45° of Encke (filled)</span>
    <span class="key"><svg viewBox="0 0 12 12" width="12" height="12" aria-hidden="true"><circle cx="6" cy="6" r="3.8" fill="none" stroke="#c9daf0" stroke-width="1.5"/></svg>Other asteroids (rings)</span>
    <span class="key"><svg viewBox="0 0 16 12" width="16" height="12" aria-hidden="true"><line x1="0" x2="16" y1="6" y2="6" stroke="#9aa5b3" stroke-width="1.5" stroke-dasharray="4 3"/></svg>Jupiter's orbit</span>
    <span class="key"><svg viewBox="0 0 12 12" width="12" height="12" aria-hidden="true"><path d="M6 11 L1 1 L11 1 Z" fill="#d08a5c" fill-opacity="0.22" stroke="#d08a5c" stroke-opacity="0.5"/></svg>Within 45° of the direction of Encke's closest point to the Sun</span>
  </p>
  <div class="orr-stage">
    <div class="orr-wrap">
      <canvas id="orr-canvas" role="img" aria-label="Orbits of asteroids on Taurid-like orbits, seen from above the plane of the planets, with the Sun, Earth, Jupiter and Comet Encke. Buttons switch between size ranges and the 7:2 resonance."></canvas>
    </div>
  </div>
  <p class="ts-note" id="orr-note" aria-live="polite"></p>
  <div class="ts-hud">
    <div class="ts-hud-cell"><div class="ts-hud-val" id="orr-n">-</div><div class="ts-hud-lbl">Asteroids shown, all on Taurid-like orbits</div></div>
    <div class="ts-hud-cell"><div class="ts-hud-val" id="orr-f45">-</div><div class="ts-hud-lbl">Share pointing within 45° of Encke (chance gives 25%)</div></div>
    <div class="ts-hud-cell"><div class="ts-hud-val" id="orr-cbar">-</div><div class="ts-hud-lbl">Alignment (1 = all point with Encke, 0 = none)</div></div>
  </div>
  <div class="ts-controls">
    <div class="ts-tabs" id="orr-tabs" role="group" aria-label="Which asteroids to show">
      <button type="button" class="sky-btn orr-btn is-active" aria-pressed="true" data-mode="16.5">The 17 largest (about 2 km and up)</button>
      <button type="button" class="sky-btn orr-btn" aria-pressed="false" data-mode="18.0">Down to about 1 km (64)</button>
      <button type="button" class="sky-btn orr-btn" aria-pressed="false" data-mode="20.0">Down to about 400 m (331)</button>
      <button type="button" class="sky-btn orr-btn" aria-pressed="false" data-mode="res72">In the 7:2 resonance (13)</button>
    </div>
    <button type="button" class="sky-btn orr-play" id="orr-play" aria-pressed="false">&#9654; Play</button>
  </div>
</div>
<figcaption>Real orbits from NASA/JPL's Small-Body Database (23 November 2026), seen from above the plane of the planets, with Comet Encke's orbit in copper. Among the 17 largest asteroids on Taurid-like orbits, most swing out on the same side as Encke; step down to about 1 km or 400 m and that lopsided fan disappears, with the orbits pointing every way. The last button shows the 13 aligned asteroids in the 7:2 resonance: orbits that go round the Sun seven times for every two of Jupiter's.</figcaption>
<script>
(function() {{
  const D = {payload_json};
  {JS_COLOURS}
  const canvas = document.getElementById("orr-canvas");
  const ctx = canvas.getContext("2d");
  const badge = document.getElementById("orr-badge");
  const note = document.getElementById("orr-note");
  const hudN = document.getElementById("orr-n");
  const hudF = document.getElementById("orr-f45");
  const hudC = document.getElementById("orr-cbar");
  const playBtn = document.getElementById("orr-play");
  const tabs = Array.from(document.querySelectorAll("#orr-tabs .orr-btn"));

  let mode = "16.5";
  let anim = false, simYr = 0, W = 640, raf = null;

  function activeOrbits() {{
    if (mode === "res72") return D.orbits.filter(o => o[5] === 1);
    const hMax = Number(mode);
    return D.orbits.filter(o => o[3] < hMax);
  }}

  function solveE(M, e) {{
    let E = M;
    for (let k = 0; k < 5; k++) E = E - (E - e * Math.sin(E) - M) / (1 - e * Math.cos(E));
    return E;
  }}

  function orbitPos(a, e, varpiDeg, M_rad) {{
    const E = solveE(M_rad, e);
    const xv = a * (Math.cos(E) - e);
    const yv = a * Math.sqrt(1 - e * e) * Math.sin(E);
    const th = (varpiDeg * Math.PI) / 180;
    const ct = Math.cos(th), st = Math.sin(th);
    return [xv * ct - yv * st, xv * st + yv * ct];
  }}

  function drawEllipse(a, e, varpiDeg, cx, cy, scale, stroke, lw, dash) {{
    const th = (varpiDeg * Math.PI) / 180;
    const ct = Math.cos(th), st = Math.sin(th);
    const b = a * Math.sqrt(1 - e * e);
    ctx.save();
    if (dash) ctx.setLineDash(dash);
    ctx.beginPath();
    for (let k = 0; k <= 90; k++) {{
      const E = (k / 90) * Math.PI * 2;
      const xv = a * (Math.cos(E) - e);
      const yv = b * Math.sin(E);
      const x = cx + (xv * ct - yv * st) * scale;
      const y = cy - (xv * st + yv * ct) * scale;
      if (k === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    }}
    ctx.closePath();
    ctx.strokeStyle = stroke;
    ctx.lineWidth = lw;
    ctx.stroke();
    ctx.restore();
  }}

  function resize() {{
    const rect = canvas.parentElement.getBoundingClientRect();
    W = Math.max(240, Math.round(rect.width));
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = W * dpr; canvas.height = W * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    render();
  }}

  function label(txt, x, y, col, align) {{
    ctx.textAlign = align || "left";
    ctx.lineWidth = 3; ctx.lineJoin = "round";
    ctx.strokeStyle = "rgba(13, 20, 33, 0.85)";
    ctx.strokeText(txt, x, y);
    ctx.fillStyle = col;
    ctx.fillText(txt, x, y);
  }}

  function render() {{
    const cx = W / 2, cy = W / 2;
    const scale = (W * 0.46) / 5.4; // 5.4 AU radius fits Jupiter (5.2 AU)
    ctx.clearRect(0, 0, W, W);
    ctx.font = "400 11px " + SANS;

    // Distance rings at 1 to 5 AU (Earth's orbit is the 1 AU ring)
    for (let au = 1; au <= 5; au++) {{
      ctx.beginPath();
      ctx.arc(cx, cy, au * scale, 0, Math.PI * 2);
      ctx.strokeStyle = au === 1 ? "rgba(205, 211, 222, 0.45)" : "rgba(42, 55, 80, 0.9)";
      ctx.lineWidth = 1;
      ctx.stroke();
    }}

    // 90-degree slice centred on the direction of Encke's closest point to the Sun (out to 1.4 AU,
    // where the closest points of these orbits lie)
    const vpE = (D.encke.varpi * Math.PI) / 180;
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    // Canvas y is inverted so angle -> -angle
    ctx.arc(cx, cy, 1.4 * scale, -(vpE + Math.PI / 4), -(vpE - Math.PI / 4));
    ctx.closePath();
    ctx.fillStyle = "rgba(208, 138, 92, 0.16)";
    ctx.fill();
    ctx.strokeStyle = "rgba(208, 138, 92, 0.45)"; ctx.lineWidth = 1; ctx.stroke();

    // Jupiter's orbit (a=5.203, e=0.0489, varpi=14.7 deg) and Mars's (faint)
    drawEllipse(5.203, 0.0489, 14.7, cx, cy, scale, "rgba(154, 165, 179, 0.75)", 1.2, [5, 4]);
    drawEllipse(1.524, 0.0934, 336.0, cx, cy, scale, "rgba(143, 155, 177, 0.3)", 0.8, null);

    // Asteroids
    const list = activeOrbits();
    const alphaUn = list.length > 150 ? 0.16 : list.length > 40 ? 0.28 : 0.45;
    const alphaAl = list.length > 150 ? 0.32 : list.length > 40 ? 0.5 : 0.75;
    const r = mode === "res72" ? 3.4 : (list.length > 100 ? 1.8 : 2.6);

    let nAl = 0, nTight = 0, sumCos = 0;
    list.forEach(o => {{
      const [a, e, vp, H, al45, res72, tight, ma0] = o;
      if (al45) nAl++;
      if (tight) nTight++;
      sumCos += Math.cos(((vp - D.encke.varpi) * Math.PI) / 180);
      // In the resonance view all are aligned: filled cream for the closest matches to Encke, rings for the rest.
      const filled = mode === "res72" ? !!tight : !!al45;
      const col = filled ? "rgba(233, 215, 168, " + alphaAl + ")" : "rgba(201, 218, 240, " + alphaUn + ")";
      drawEllipse(a, e, vp, cx, cy, scale, col, mode === "res72" ? 1.3 : 0.9, null);

      const perY = Math.pow(a, 1.5);
      const M = ((ma0 * Math.PI) / 180) + (simYr / perY) * Math.PI * 2;
      const [px, py] = orbitPos(a, e, vp, M);
      ctx.beginPath();
      ctx.arc(cx + px * scale, cy - py * scale, r, 0, Math.PI * 2);
      if (filled) {{ ctx.fillStyle = C.cream; ctx.fill(); }}
      else {{ ctx.strokeStyle = C.pale; ctx.lineWidth = 1.1; ctx.stroke(); }}
    }});

    // Comet Encke: orbit and nucleus
    drawEllipse(D.encke.a, D.encke.e, D.encke.varpi, cx, cy, scale, C.copper, 2.2, null);
    const ePer = Math.pow(D.encke.a, 1.5);
    const [ex, ey] = orbitPos(D.encke.a, D.encke.e, D.encke.varpi, 2.15 + (simYr / ePer) * Math.PI * 2);
    ctx.beginPath();
    ctx.arc(cx + ex * scale, cy - ey * scale, 4.5, 0, Math.PI * 2);
    ctx.fillStyle = C.copper; ctx.fill();
    ctx.strokeStyle = C.band; ctx.lineWidth = 1.5; ctx.stroke();

    // Earth and Jupiter
    const eAng = simYr * Math.PI * 2;
    const exE = cx + Math.cos(eAng) * scale, eyE = cy - Math.sin(eAng) * scale;
    ctx.beginPath(); ctx.arc(exE, eyE, 3.5, 0, Math.PI * 2);
    ctx.fillStyle = C.inkSoft; ctx.fill();
    const jpAng = (14.7 * Math.PI) / 180 + (simYr / 11.86) * Math.PI * 2;
    const jx = cx + Math.cos(jpAng) * 5.203 * scale, jy = cy - Math.sin(jpAng) * 5.203 * scale;
    ctx.beginPath(); ctx.arc(jx, jy, 5, 0, Math.PI * 2);
    ctx.fillStyle = C.slate; ctx.fill();

    // Sun: a plain cream disc
    ctx.beginPath(); ctx.arc(cx, cy, 6, 0, Math.PI * 2);
    ctx.fillStyle = C.ink; ctx.fill();

    // Labels
    label("Sun", cx + 9, cy - 8, C.ink);
    label("Earth", exE + 7, eyE + 4, C.inkSoft);
    label("Jupiter", jx + (jx > cx ? -8 : 8), jy + (jy > cy ? -9 : 15), C.slate, jx > cx ? "right" : "left");
    const lx = cx + Math.cos(vpE + 0.5) * 1.5 * scale, ly = cy - Math.sin(vpE + 0.5) * 1.5 * scale;
    if (W >= 420) {{
      // On narrow screens the legend names the slice instead, so the middle stays clear
      const txt = "Toward Encke's closest point to the Sun";
      label(txt, Math.max(4 + ctx.measureText(txt).width, lx), ly - 4, C.copper, "right");
    }}

    // Read-outs
    const n = list.length;
    const f45 = n ? (100 * nAl) / n : 0;
    const cbar = n ? sumCos / n : 0;
    hudN.textContent = String(n);
    hudF.textContent = mode === "res72" ? "100% (chosen that way)" : (f45.toFixed(1) + "% (" + nAl + " of " + n + ")");
    hudC.textContent = (cbar >= 0 ? "+" : "") + cbar.toFixed(3);

    const titles = {{
      "16.5": "The 17 largest (about 2 km and up)",
      "18.0": "Down to about 1 km: 64 asteroids",
      "20.0": "Down to about 400 m: 331 asteroids",
      "res72": "In the 7:2 resonance: 13 asteroids"
    }};
    badge.textContent = titles[mode];
    note.textContent = mode === "res72"
      ? "All " + n + " point within 45° of Encke, because only those were picked. Filled: the " + nTight + " whose orbits most closely match Encke's. Rings: the other " + (n - nTight) + "."
      : "";
  }}

  tabs.forEach(btn => {{
    btn.addEventListener("click", () => {{
      mode = btn.dataset.mode;
      tabs.forEach(b => {{ b.classList.toggle("is-active", b === btn); b.setAttribute("aria-pressed", b === btn ? "true" : "false"); }});
      render();
    }});
  }});

  playBtn.addEventListener("click", () => {{
    anim = !anim;
    playBtn.setAttribute("aria-pressed", anim ? "true" : "false");
    playBtn.innerHTML = anim ? "&#10074;&#10074; Pause" : "&#9654; Play";
    if (anim) {{
      function step() {{
        if (!anim) return;
        simYr += 0.012;
        render();
        raf = requestAnimationFrame(step);
      }}
      raf = requestAnimationFrame(step);
    }} else if (raf) {{
      cancelAnimationFrame(raf);
    }}
  }});

  if (typeof ResizeObserver !== "undefined") {{
    new ResizeObserver(resize).observe(canvas.parentElement);
  }} else {{
    window.addEventListener("resize", resize);
  }}
  resize();
}})();
</script>
</figure>
"""


def build_radar_html(summary: Dict) -> str:
    a1 = summary["archive_a_neos"]["test_a1_alignment"]
    tiers_payload = {}
    for k, v in a1.items():
        tiers_payload[k] = {
            "n_t": v["box_t"]["n"],
            "c_t": v["box_t"]["c_bar"],
            "f45_t": v["box_t"]["f_45"],
            "p_unif": v["box_t"]["p_unif"],
            "n_l": v["ctrl_lowe"]["n"],
            "c_l": v["ctrl_lowe"]["c_bar"],
            "p_hi": v["p_vs_highi"],
            "h_t": v["hist20_box_t"],
            "h_l": v["hist20_ctrl_lowe"],
        }
    pjson = json.dumps(tiers_payload, separators=(",", ":"))

    return f"""<figure class="fig taurid-radar-fig" id="taurid-perihelion-rose">
<style>
{PANEL_CSS}
{SHARED_CSS}
.rad-stage {{ display: flex; justify-content: center; padding: 0.8rem 1rem 0.5rem; }}
.rad-stage canvas {{ display: block; width: 100%; max-width: 680px; height: 360px; }}
</style>
<div class="sky-panel">
  <div class="sky-head">
    <div>
      <p class="sky-eyebrow">Two groups of asteroids, five size ranges</p>
      <h3 class="sky-title">Which way the orbits point</h3>
    </div>
  </div>
  <p class="sky-legend">
    <span class="key"><svg viewBox="0 0 12 12" width="12" height="12" aria-hidden="true"><path d="M6 11 L1 2 A6 6 0 0 1 11 2 Z" fill="#e9d7a8" fill-opacity="0.5" stroke="#e9d7a8"/></svg>Taurid-like orbits</span>
    <span class="key"><svg viewBox="0 0 12 12" width="12" height="12" aria-hidden="true"><rect x="2" y="2" width="8" height="8" fill="none" stroke="#9aa5b3" stroke-width="1.5"/></svg>Rounder orbits (comparison group)</span>
    <span class="key"><svg viewBox="0 0 16 12" width="16" height="12" aria-hidden="true"><line x1="0" x2="16" y1="6" y2="6" stroke="#d08a5c" stroke-width="2"/></svg>Encke's direction</span>
    <span class="key"><svg viewBox="0 0 16 12" width="16" height="12" aria-hidden="true"><line x1="0" x2="16" y1="6" y2="6" stroke="#9aa5b3" stroke-width="1.5" stroke-dasharray="3 3"/></svg>Jupiter's direction</span>
    <span class="key"><svg viewBox="0 0 16 12" width="16" height="12" aria-hidden="true"><line x1="0" x2="16" y1="6" y2="6" stroke="#cdd3de" stroke-width="1" stroke-dasharray="2 2"/></svg>An even spread (no preferred direction)</span>
  </p>
  <div class="rad-stage">
    <canvas id="rad-canvas" role="img" aria-label="Two rose charts of the direction of each orbit's closest point to the Sun: Taurid-like orbits on one side, rounder orbits as a comparison group on the other, for a chosen size range."></canvas>
  </div>
  <div class="ts-bar" id="rad-bar" aria-live="polite">-</div>
  <div class="ts-controls">
    <div class="ts-tabs" id="rad-tabs" role="group" aria-label="Size range">
      <button type="button" class="sky-btn rad-tab is-active" aria-pressed="true" data-k="H_lt_16.5">The largest (about 2 km and up)</button>
      <button type="button" class="sky-btn rad-tab" aria-pressed="false" data-k="H_lt_18.0">Down to about 1 km</button>
      <button type="button" class="sky-btn rad-tab" aria-pressed="false" data-k="H_lt_20.0">Down to about 400 m</button>
      <button type="button" class="sky-btn rad-tab" aria-pressed="false" data-k="H_lt_22.0">Down to about 150 m</button>
      <button type="button" class="sky-btn rad-tab" aria-pressed="false" data-k="all_H">All sizes</button>
    </div>
  </div>
</div>
<figcaption>Each wedge shows how many orbits have their closest point to the Sun in that direction, in slices of 20°; a round shape means no preferred direction. Taurid-like orbits are in cream; rounder orbits (comparison group) are in slate, and Jupiter's pull keeps them pointing toward Jupiter's own direction. Among the largest asteroids the cream shape bulges toward Encke, but from about 1 km down it is close to round, while the comparison group keeps its bulge toward Jupiter.</figcaption>
<script>
(function() {{
  const T = {pjson};
  {JS_COLOURS}
  const canvas = document.getElementById("rad-canvas");
  const ctx = canvas.getContext("2d");
  const bar = document.getElementById("rad-bar");
  const tabs = Array.from(document.querySelectorAll("#rad-tabs .rad-tab"));
  const TIER = {{
    "H_lt_16.5": "the largest (about 2 km and up)",
    "H_lt_18.0": "down to about 1 km",
    "H_lt_20.0": "down to about 400 m",
    "H_lt_22.0": "down to about 150 m",
    "all_H": "all sizes"
  }};
  let key = "H_lt_16.5";
  let W = 680, H = 360;

  function resize() {{
    const rect = canvas.parentElement.getBoundingClientRect();
    W = Math.max(240, Math.min(680, Math.round(rect.width - 16)));
    H = W < 500 ? 560 : 360;
    canvas.style.height = H + "px";
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = W * dpr; canvas.height = H * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    render();
  }}

  function drawRose(cx, cy, R, counts, nTot, fillCol, strokeCol, title, sub, dashed) {{
    // Even-spread ring: each of 18 slices would hold 1/18 of the orbits
    const expFrac = 1 / 18;
    const maxFrac = Math.max(expFrac * 2.4, ...counts.map(c => (nTot ? c / nTot : 0)));
    ctx.save();
    const rr0 = R * Math.min(1, expFrac / maxFrac);
    ctx.beginPath(); ctx.arc(cx, cy, rr0, 0, Math.PI * 2);
    ctx.strokeStyle = "rgba(205, 211, 222, 0.6)"; ctx.setLineDash([2, 2]); ctx.lineWidth = 1; ctx.stroke();
    ctx.setLineDash([]);
    const rr1 = R * Math.min(1, (2 * expFrac) / maxFrac);
    ctx.beginPath(); ctx.arc(cx, cy, rr1, 0, Math.PI * 2);
    ctx.strokeStyle = C.line; ctx.stroke();

    // Outer frame circle
    ctx.beginPath(); ctx.arc(cx, cy, R, 0, Math.PI * 2);
    ctx.strokeStyle = C.line; ctx.lineWidth = 1; ctx.stroke();

    // 18 wedges of 20 degrees
    for (let i = 0; i < 18; i++) {{
      const frac = nTot ? counts[i] / nTot : 0;
      const rr = R * (frac / maxFrac);
      const a0 = -((i * 20) * Math.PI) / 180;
      const a1 = -(((i + 1) * 20) * Math.PI) / 180;
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.arc(cx, cy, rr, a0, a1, true);
      ctx.closePath();
      ctx.fillStyle = fillCol;
      ctx.fill();
      ctx.strokeStyle = strokeCol;
      ctx.lineWidth = 1;
      ctx.stroke();
    }}

    // Encke (161.3 deg) and Jupiter (14.7 deg) direction lines
    const eA = -(161.29 * Math.PI) / 180;
    ctx.beginPath(); ctx.moveTo(cx, cy); ctx.lineTo(cx + (R + 8) * Math.cos(eA), cy + (R + 8) * Math.sin(eA));
    ctx.strokeStyle = C.copper; ctx.lineWidth = 1.8; ctx.stroke();

    const jA = -(14.7 * Math.PI) / 180;
    ctx.beginPath(); ctx.moveTo(cx, cy); ctx.lineTo(cx + (R + 8) * Math.cos(jA), cy + (R + 8) * Math.sin(jA));
    ctx.strokeStyle = C.slate; ctx.lineWidth = 1.5; ctx.setLineDash([3, 3]); ctx.stroke();
    ctx.setLineDash([]);

    ctx.font = "400 11px " + SANS;
    // Encke's label above its line, Jupiter's below, so neighbouring roses never collide
    function lbl(txt, x, y, col, align) {{
      ctx.textAlign = align;
      ctx.lineWidth = 3; ctx.lineJoin = "round"; ctx.strokeStyle = "rgba(13, 20, 33, 0.9)";
      ctx.strokeText(txt, x, y);
      ctx.fillStyle = col; ctx.fillText(txt, x, y);
    }}
    lbl("Encke, 161°", cx + (R + 8) * Math.cos(eA) + 30, cy + (R + 8) * Math.sin(eA) - 8, C.copper, "right");
    lbl("Jupiter, 15°", cx + (R + 8) * Math.cos(jA) - 22, cy + (R + 8) * Math.sin(jA) + 18, C.slate, "left");

    ctx.textAlign = "center";
    ctx.font = "400 15px " + (getComputedStyle(document.documentElement).getPropertyValue("--serif") || "Georgia, serif");
    ctx.fillStyle = C.ink;
    ctx.fillText(title, cx, cy - R - 22);
    ctx.font = "400 11px " + SANS;
    ctx.fillStyle = C.inkSoft;
    ctx.fillText(sub, cx, cy + R + 24);
    ctx.restore();
  }}

  function fmtC(c) {{ return (c >= 0 ? "+" : "") + c.toFixed(3); }}

  function render() {{
    const d = T[key];
    ctx.clearRect(0, 0, W, H);
    const stacked = W < 500;
    const R = stacked ? Math.min(100, W * 0.3) : Math.min(104, W * 0.16);
    const c1 = stacked ? [W / 2, H * 0.25] : [W * 0.27, H * 0.52];
    const c2 = stacked ? [W / 2, H * 0.75] : [W * 0.73, H * 0.52];

    drawRose(c1[0], c1[1], R, d.h_t, d.n_t, "rgba(233, 215, 168, 0.6)", C.cream,
             "Taurid-like orbits", d.n_t + " asteroids, alignment " + fmtC(d.c_t));
    drawRose(c2[0], c2[1], R, d.h_l, d.n_l, "rgba(154, 165, 179, 0.18)", C.slate,
             "Rounder orbits (comparison)", d.n_l + " asteroids, alignment " + fmtC(d.c_l));

    bar.innerHTML = 'Showing <strong>' + TIER[key] + '</strong>. Taurid-like orbits within 45° of Encke: <strong>' + (100 * d.f45_t).toFixed(1) + '%</strong> (chance gives 25.0%). ' +
      'Chance of an alignment this strong if directions were random: <strong>p = ' + d.p_unif.toFixed(4) + '</strong>. ' +
      'Against more tilted orbits of the same shape: <strong>p = ' + d.p_hi.toFixed(3) + '</strong>.';
  }}

  tabs.forEach(t => {{
    t.addEventListener("click", () => {{
      key = t.dataset.k;
      tabs.forEach(b => {{ b.classList.toggle("is-active", b === t); b.setAttribute("aria-pressed", b === t ? "true" : "false"); }});
      render();
    }});
  }});

  if (typeof ResizeObserver !== "undefined") {{
    new ResizeObserver(resize).observe(canvas.parentElement);
  }} else {{
    window.addEventListener("resize", resize);
  }}
  resize();
}})();
</script>
</figure>
"""


def build_fireballs_html(summary: Dict) -> str:
    fb = summary["archive_b_fireballs_1994_2025"]
    payload = {
        "yearly": fb["yearly"],
        "monthly": fb["monthly"],
        "b1": fb["test_b1_seasonality"],
        "b2": fb["test_b2_swarm_years_6"],
    }
    pjson = json.dumps(payload, separators=(",", ":"))

    return f"""<figure class="fig taurid-fb-fig" id="taurid-fireballs">
<style>
{PANEL_CSS}
{SHARED_CSS}
.fb-wrap {{ padding: 0.7rem 1rem 0.35rem; }}
.fb-wrap canvas {{ display: block; width: 100%; height: 320px; cursor: crosshair; }}
.fb-legend[hidden] {{ display: none; }}
</style>
<div class="sky-panel">
  <div class="sky-head">
    <div>
      <p class="sky-eyebrow">NASA/JPL fireball records, 1,045 airbursts</p>
      <h3 class="sky-title">Airbursts seen by satellite, 1994 to 2025</h3>
    </div>
    <div class="ts-tabs" id="fb-tabs" role="group" aria-label="View">
      <button type="button" class="sky-btn fb-tab is-active" aria-pressed="true" data-v="swarm">Years the swarm was due back</button>
      <button type="button" class="sky-btn fb-tab" aria-pressed="false" data-v="monthly">Month by month</button>
    </div>
  </div>
  <p class="sky-legend fb-legend" id="fb-leg-swarm">
    <span class="key"><svg viewBox="0 0 12 12" width="12" height="12" aria-hidden="true"><rect x="2" y="1" width="8" height="11" fill="#d08a5c"/></svg>Years the swarm was due back</span>
    <span class="key"><svg viewBox="0 0 12 12" width="12" height="12" aria-hidden="true"><rect x="2" y="1" width="8" height="11" fill="#9aa5b3" fill-opacity="0.55"/></svg>Other years</span>
    <span class="key"><svg viewBox="0 0 16 12" width="16" height="12" aria-hidden="true"><line x1="0" x2="16" y1="6" y2="6" stroke="#cdd3de" stroke-width="1.3" stroke-dasharray="4 4"/></svg>What chance gives</span>
    <span class="key">Bar height: share of the year's airbursts in the autumn Taurid weeks (15 Oct to 30 Nov)</span>
  </p>
  <p class="sky-legend fb-legend" id="fb-leg-monthly" hidden>
    <span class="key"><svg viewBox="0 0 12 12" width="12" height="12" aria-hidden="true"><rect x="2" y="1" width="8" height="11" fill="#d08a5c"/></svg>October and November (autumn Taurids)</span>
    <span class="key"><svg viewBox="0 0 12 12" width="12" height="12" aria-hidden="true"><rect x="2" y="1" width="8" height="11" fill="#e9d7a8"/></svg>June and July (daytime Taurids)</span>
    <span class="key"><svg viewBox="0 0 12 12" width="12" height="12" aria-hidden="true"><rect x="2" y="1" width="8" height="11" fill="#9aa5b3" fill-opacity="0.55"/></svg>Other months</span>
    <span class="key"><svg viewBox="0 0 16 12" width="16" height="12" aria-hidden="true"><line x1="0" x2="16" y1="6" y2="6" stroke="#cdd3de" stroke-width="1.3" stroke-dasharray="4 4"/></svg>Average month</span>
  </p>
  <div class="fb-wrap">
    <canvas id="fb-canvas" tabindex="0" role="img" aria-label="Bar chart of airbursts seen by US government satellites, 1994 to 2025, by year or by month. Focus the chart and use the left and right arrow keys to read each bar."></canvas>
  </div>
  <div class="ts-bar" id="fb-bar" aria-live="polite">Point at a bar, or select the chart and use the arrow keys, to see its numbers.</div>
</div>
<figcaption>Airbursts recorded by US government satellites in NASA/JPL's fireball list, 32 full years (1994 to 2025; 1,045 events, 1,182 kilotons in all). Each bar in the first view is one year's share of airbursts that came in the autumn Taurid weeks, which cancels out the sensors improving over time. The six years the swarm was due back (copper: 1998, 2005, 2015, 2018, 2022, 2025) average 12.7%, against 13.0% in the other 26 years (p = 0.520, well within chance); by month, neither the autumn Taurids (0.99 times the expected number) nor the daytime Taurids of June and July (0.91 times) stand out.</figcaption>
<script>
(function() {{
  const D = {pjson};
  {JS_COLOURS}
  const canvas = document.getElementById("fb-canvas");
  const ctx = canvas.getContext("2d");
  const bar = document.getElementById("fb-bar");
  const legSwarm = document.getElementById("fb-leg-swarm");
  const legMonthly = document.getElementById("fb-leg-monthly");
  const tabs = Array.from(document.querySelectorAll("#fb-tabs .fb-tab"));
  const DEFAULT = "Point at a bar, or select the chart and use the arrow keys, to see its numbers.";
  let view = "swarm", hoverIdx = -1, W = 700, H = 320;
  const PAD = {{ l: 42, r: 12, t: 24, b: 34 }};
  const MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
  const MONTHS_LONG = ["January","February","March","April","May","June","July","August","September","October","November","December"];

  function resize() {{
    const rect = canvas.parentElement.getBoundingClientRect();
    W = Math.max(240, Math.round(rect.width - 32));
    H = W < 500 ? 290 : 320;
    canvas.style.height = H + "px";
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = W * dpr; canvas.height = H * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    render();
  }}

  function grid(yOf, ticks, fmt, pw) {{
    ctx.textAlign = "right";
    for (const v of ticks) {{
      const y = yOf(v);
      ctx.beginPath(); ctx.moveTo(PAD.l, y); ctx.lineTo(PAD.l + pw, y);
      ctx.strokeStyle = C.line; ctx.lineWidth = 1; ctx.stroke();
      ctx.fillStyle = C.faint; ctx.fillText(fmt(v), PAD.l - 6, y + 4);
    }}
  }}

  function refLine(y, pw, txt) {{
    ctx.save();
    ctx.setLineDash([4, 4]);
    ctx.strokeStyle = C.inkSoft; ctx.lineWidth = 1.3;
    ctx.beginPath(); ctx.moveTo(PAD.l, y); ctx.lineTo(PAD.l + pw, y); ctx.stroke();
    ctx.restore();
    if (txt) {{
      // Written above the plot, clear of the bars
      ctx.textAlign = "right";
      ctx.fillStyle = C.inkSoft; ctx.fillText(txt, PAD.l + pw, PAD.t - 9);
    }}
  }}

  function render() {{
    const pw = W - PAD.l - PAD.r, ph = H - PAD.t - PAD.b;
    ctx.clearRect(0, 0, W, H);
    ctx.font = "400 11px " + SANS;

    if (view === "swarm") {{
      const rows = D.yearly;
      const yMax = 0.34;
      const yOf = v => PAD.t + ((yMax - v) / yMax) * ph;
      const bw = pw / rows.length;
      grid(yOf, [0, 0.10, 0.20, 0.30], v => Math.round(v * 100) + "%", pw);

      rows.forEach((r, i) => {{
        const x = PAD.l + i * bw + bw * 0.14;
        const w = Math.max(3, bw * 0.72);
        const y = yOf(r.s_cnt);
        const isHov = i === hoverIdx;
        ctx.fillStyle = r.swarm6 ? (isHov ? "#e3a57c" : C.copper)
                                 : (isHov ? "rgba(205, 211, 222, 0.85)" : "rgba(154, 165, 179, 0.55)");
        ctx.fillRect(x, y, w, PAD.t + ph - y);
        if (isHov) {{ ctx.strokeStyle = C.ink; ctx.lineWidth = 1; ctx.strokeRect(x + 0.5, y + 0.5, w - 1, PAD.t + ph - y - 1); }}
        const nearSwarm = (rows[i - 1] && rows[i - 1].swarm6) || (rows[i + 1] && rows[i + 1].swarm6);
        const showYear = r.swarm6 || (W >= 500 && r.year % 4 === 0 && !nearSwarm);
        if (showYear) {{
          ctx.fillStyle = r.swarm6 ? C.copper : C.faint;
          ctx.textAlign = "center";
          ctx.fillText(W >= 640 ? String(r.year) : "'" + String(r.year).slice(2), x + w / 2, PAD.t + ph + 15);
        }}
      }});
      refLine(yOf(0.1287), pw, W >= 500 ? "Dashed line: chance gives 12.9%; swarm years average 12.7%" : "Dashed line: chance, 12.9%");
    }} else {{
      const rows = D.monthly;
      const yMax = 115;
      const yOf = v => PAD.t + ((yMax - v) / yMax) * ph;
      const bw = pw / 12;
      grid(yOf, [0, 30, 60, 90], v => String(v), pw);
      refLine(yOf(1045 / 12), pw, "Dashed line: the average month");

      rows.forEach((r, i) => {{
        const x = PAD.l + i * bw + bw * 0.18;
        const w = bw * 0.64;
        const y = yOf(r.count);
        const isAut = (i === 9 || i === 10);
        const isDay = (i === 5 || i === 6);
        const isHov = i === hoverIdx;
        ctx.fillStyle = isAut ? (isHov ? "#e3a57c" : C.copper)
                     : isDay ? (isHov ? "#f6ecd3" : C.cream)
                     : (isHov ? "rgba(205, 211, 222, 0.85)" : "rgba(154, 165, 179, 0.55)");
        ctx.fillRect(x, y, w, PAD.t + ph - y);
        if (isHov) {{ ctx.strokeStyle = C.ink; ctx.lineWidth = 1; ctx.strokeRect(x + 0.5, y + 0.5, w - 1, PAD.t + ph - y - 1); }}
        ctx.textAlign = "center";
        ctx.lineWidth = 3; ctx.lineJoin = "round"; ctx.strokeStyle = "rgba(13, 20, 33, 0.9)";
        ctx.strokeText(String(r.count), x + w / 2, y - 5);
        ctx.fillStyle = C.inkSoft;
        ctx.fillText(String(r.count), x + w / 2, y - 5);
        ctx.fillStyle = isAut ? C.copper : isDay ? C.cream : C.faint;
        ctx.fillText(W >= 420 ? MONTHS[i] : MONTHS[i].charAt(0), x + w / 2, PAD.t + ph + 16);
      }});
    }}
    ctx.strokeStyle = C.line; ctx.lineWidth = 1;
    ctx.strokeRect(PAD.l + 0.5, PAD.t + 0.5, pw - 1, ph - 1);
  }}

  function describe(idx) {{
    if (idx < 0) {{ bar.textContent = DEFAULT; return; }}
    if (view === "swarm") {{
      const r = D.yearly[idx];
      bar.innerHTML = '<strong>' + r.year + (r.swarm6 ? ', a year the swarm was due back' : '') + '</strong>. In the autumn Taurid weeks: <strong>' + r.n_aut + ' of ' + r.n_year + ' (' + (100 * r.s_cnt).toFixed(1) + '%)</strong>. Of those, 1 kiloton or more: <strong>' + r.n_aut_1kt + '</strong>. Their energy: <strong>' + r.e_aut_kt.toFixed(2) + ' kilotons</strong>.';
    }} else {{
      const r = D.monthly[idx];
      bar.innerHTML = '<strong>' + MONTHS_LONG[idx] + ', 1994 to 2025</strong>. Airbursts: <strong>' + r.count + '</strong>. Of those, 1 kiloton or more: <strong>' + r.count_1kt + '</strong>. Total energy: <strong>' + r.energy_kt.toFixed(1) + ' kilotons</strong>.';
    }}
  }}

  tabs.forEach(t => {{
    t.addEventListener("click", () => {{
      view = t.dataset.v; hoverIdx = -1;
      tabs.forEach(b => {{ b.classList.toggle("is-active", b === t); b.setAttribute("aria-pressed", b === t ? "true" : "false"); }});
      legSwarm.hidden = view !== "swarm";
      legMonthly.hidden = view === "swarm";
      describe(-1);
      render();
    }});
  }});

  canvas.addEventListener("mousemove", ev => {{
    const rect = canvas.getBoundingClientRect();
    const mx = ev.clientX - rect.left;
    const pw = W - PAD.l - PAD.r;
    if (mx < PAD.l || mx > PAD.l + pw) {{ if (hoverIdx !== -1) {{ hoverIdx = -1; render(); }} return; }}
    const n = view === "swarm" ? D.yearly.length : 12;
    const idx = Math.min(n - 1, Math.max(0, Math.floor(((mx - PAD.l) / pw) * n)));
    if (idx !== hoverIdx) {{ hoverIdx = idx; render(); describe(idx); }}
  }});
  canvas.addEventListener("mouseleave", () => {{ hoverIdx = -1; render(); }});
  canvas.addEventListener("keydown", ev => {{
    const n = view === "swarm" ? D.yearly.length : 12;
    let idx = hoverIdx;
    if (ev.key === "ArrowRight") idx = idx < 0 ? 0 : Math.min(n - 1, idx + 1);
    else if (ev.key === "ArrowLeft") idx = idx < 0 ? n - 1 : Math.max(0, idx - 1);
    else if (ev.key === "Home") idx = 0;
    else if (ev.key === "End") idx = n - 1;
    else if (ev.key === "Escape") idx = -1;
    else return;
    ev.preventDefault();
    hoverIdx = idx; render(); describe(idx);
  }});

  if (typeof ResizeObserver !== "undefined") {{
    new ResizeObserver(resize).observe(canvas.parentElement);
  }} else {{
    window.addEventListener("resize", resize);
  }}
  resize();
}})();
</script>
</figure>
"""


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summary = json.loads((RESULTS / "summary.json").read_text(encoding="utf-8"))
    cat, encke = td.load_neos()

    (OUT_DIR / "tiles.html").write_text(build_tiles_html(summary), encoding="utf-8")
    (OUT_DIR / "verdict.html").write_text(build_verdict_html(summary), encoding="utf-8")
    (OUT_DIR / "orrery.html").write_text(build_orrery_html(cat, encke, summary), encoding="utf-8")
    (OUT_DIR / "radar.html").write_text(build_radar_html(summary), encoding="utf-8")
    (OUT_DIR / "fireballs.html").write_text(build_fireballs_html(summary), encoding="utf-8")

    for p in sorted(OUT_DIR.glob("*.html")):
        print(f"Wrote {p.relative_to(REPO)} ({p.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
