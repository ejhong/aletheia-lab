#!/usr/bin/env python3
"""Generate interactive observatory HTML/Canvas figures for site/figures/taurid-swarm/.

Reads ONLY locked results/ and primary data/ catalogs. Produces five self-contained,
zero-dependency fragments for site/content/taurid-swarm.md:
  1. tiles.html     - Headline metric tiles
  2. verdict.html   - Native Aletheia Lab 4-criterion verdict scorecard
  3. orrery.html    - Interactive Inner Solar System & Taurid Corridor Orrery
  4. radar.html     - Interactive Longitude-of-Perihelion Rose & Size-Inversion Explorer
  5. fireballs.html - Interactive 32-Year NASA CNEOS Satellite Airburst Explorer
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


def build_tiles_html(summary: Dict) -> str:
    return """<div class="tiles">
<div class="tile"><p class="tile-value">0 of 4</p><p class="tile-label">pre-registered criteria met across 43,156 NASA NEAs &amp; 1,045 satellite airbursts</p></div>
<div class="tile"><p class="tile-value">65% → 19%</p><p class="tile-label">drop in Encke-aligned share from Napier's 17 giants (H&lt;16.5) to the next 47 1-km NEAs</p></div>
<div class="tile"><p class="tile-value">6 objects</p><p class="tile-label">tight Encke-like NEAs (H&lt;20) inside the 7:2 Jupiter resonance across the whole catalog</p></div>
<div class="tile"><p class="tile-value">12.7% vs 13.0%</p><p class="tile-label">Autumn satellite bolide share in 6 swarm return years vs. 26 non-swarm years (p = 0.52)</p></div>
</div>
"""


def build_verdict_html(summary: Dict) -> str:
    return """<div class="verdict">
<div class="verdict-row">
  <div>
    <p class="verdict-kicker">Test A1 · NASA/JPL Near-Earth Asteroids (H &lt; 18.0, ~1 km+)</p>
    <p class="verdict-text">Do 1-km asteroids in Napier's orbital box align with Comet Encke (ϖ = 161.3°)?</p>
    <p class="verdict-note">Napier's (2010) H &lt; 16.5 alignment (N = 17, c̄ = +0.557, p = 0.0005) collapses to zero at H &lt; 18.0 (N = 64, c̄ = −0.001, p = 0.504) and turns slightly negative at H &lt; 20.0 (N = 331, c̄ = −0.068)—the opposite of a cometary fragmentation cascade.</p>
  </div>
  <p class="verdict-status is-no"><span class="dot" aria-hidden="true"></span>Not met</p>
</div>
<div class="verdict-row">
  <div>
    <p class="verdict-kicker">Test A2 · 7:2 Jupiter Mean-Motion Resonance (2.21–2.30 AU, H &lt; 20.0)</p>
    <p class="verdict-text">Is there a ≥ 2× excess of sub-km fragments trapped in the 7:2 Taurid resonance?</p>
    <p class="verdict-note">Only 13 of 72 aligned NEAs (18.1%) sit in 2.21–2.30 AU vs. 11.2% anti-Taurid (1.61×, p = 0.095) and 15.1% in the secular control (p = 0.302). Just 6 meet tight Encke-like bounds (and 2 of the 3 largest are bright stony asteroids).</p>
  </div>
  <p class="verdict-status is-no"><span class="dot" aria-hidden="true"></span>Not met</p>
</div>
<div class="verdict-row">
  <div>
    <p class="verdict-kicker">Test B1 · NASA CNEOS Satellite Bolides (1994–2025, N = 1,045)</p>
    <p class="verdict-text">Do US satellite-detected airbursts spike during Autumn or Daytime Taurid seasons?</p>
    <p class="verdict-note">Autumn Taurids (Oct 15–Nov 30): 133 observed vs. 134.5 expected (0.99×, p = 0.568; ≥ 1 kt: 12 vs. 14.8, p = 0.820). Daytime β-Taurids (Jun 10–Jul 10): 81 vs. 88.7 expected (0.91×, p = 0.818).</p>
  </div>
  <p class="verdict-status is-no"><span class="dot" aria-hidden="true"></span>Not met</p>
</div>
<div class="verdict-row">
  <div>
    <p class="verdict-kicker">Test B2 · Published 7:2 Resonant Swarm Return Years (1998, 2005, 2015, 2018, 2022, 2025)</p>
    <p class="verdict-text">Do meter-scale airbursts surge when Earth crosses the 7:2 resonant swarm?</p>
    <p class="verdict-note">Within-year Autumn bolide share is 12.70% in swarm years vs. 12.96% in the 26 non-swarm years (p = 0.520). Large ≥ 1 kt bolides average 0.33/yr in swarm years vs. 0.38/yr outside (p = 0.688).</p>
  </div>
  <p class="verdict-status is-no"><span class="dot" aria-hidden="true"></span>Not met</p>
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
.taurid-orrery-fig {{ margin: 2.3rem 0 2.7rem; }}
.orr-plate {{
  background: radial-gradient(circle at 50% 45%, #141c30 0%, #0b101d 58%, #070a12 100%);
  border: 1px solid rgba(207, 165, 68, 0.34);
  border-radius: 6px;
  color: #f3ecdf;
  overflow: hidden;
  box-shadow: 0 22px 54px rgba(12, 10, 8, 0.28);
}}
.orr-head {{
  display: flex; flex-wrap: wrap; align-items: baseline; justify-content: space-between;
  gap: 0.5rem 1rem;
  padding: 1.1rem 1.35rem 0.85rem;
  border-bottom: 1px solid rgba(207, 165, 68, 0.18);
}}
.orr-eyebrow {{
  font: 500 10.5px/1.4 var(--mono); text-transform: uppercase; letter-spacing: 0.2em;
  color: #d8ad5e; margin: 0 0 0.22rem;
}}
.orr-title {{ font: 400 1.4rem/1.2 var(--serif); color: #f8f2e6; margin: 0; }}
.orr-badge {{
  font: 500 11.5px/1.3 var(--mono); color: #f5d082;
  background: rgba(8, 11, 19, 0.78); border: 1px solid rgba(207, 165, 68, 0.32);
  padding: 0.36rem 0.78rem; border-radius: 999px;
}}
.orr-stage {{ position: relative; display: flex; justify-content: center; padding: 0.7rem 1rem 0.4rem; }}
.orr-wrap {{ position: relative; width: 100%; max-width: 650px; aspect-ratio: 1 / 1; }}
.orr-wrap canvas {{ display: block; width: 100%; height: 100%; }}
.orr-legend {{
  display: flex; flex-wrap: wrap; justify-content: center; gap: 0.45rem 1.25rem;
  padding: 0.4rem 1.2rem 0.75rem; font: 400 11.5px/1.4 var(--sans); color: #b7c2d6;
}}
.orr-leg {{ display: inline-flex; align-items: center; gap: 0.4rem; }}
.orr-swatch {{ width: 14px; height: 2px; display: inline-block; }}
.orr-hud {{
  display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1px;
  background: rgba(207, 165, 68, 0.18);
  border-top: 1px solid rgba(207, 165, 68, 0.2);
  border-bottom: 1px solid rgba(207, 165, 68, 0.2);
}}
.orr-cell {{ background: rgba(10, 15, 26, 0.9); padding: 0.68rem 0.9rem; text-align: center; }}
.orr-val {{ font: 600 1.05rem/1.2 var(--mono); color: #f6e7c4; font-variant-numeric: tabular-nums; }}
.orr-val.is-warn {{ color: #e88565; }}
.orr-val.is-good {{ color: #8ad3b5; }}
.orr-lbl {{ font: 400 10.5px/1.35 var(--sans); color: #9aa7bd; margin-top: 0.18rem; }}
.orr-controls {{
  display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between;
  gap: 0.6rem 1rem; padding: 0.9rem 1.35rem 1.1rem; background: rgba(8, 11, 19, 0.74);
}}
.orr-tabs {{ display: flex; flex-wrap: wrap; gap: 0.4rem; }}
.orr-btn {{
  font: 400 11.5px/1.25 var(--sans); padding: 0.4rem 0.7rem; border-radius: 3px; cursor: pointer;
  background: rgba(255,255,255,0.04); border: 1px solid rgba(207,165,68,0.24); color: #d6cbb7;
}}
.orr-btn:hover {{ border-color: rgba(207,165,68,0.65); color: #fff4da; }}
.orr-btn.is-active {{ background: rgba(207,165,68,0.25); border-color: #e6ba63; color: #fff4da; font-weight: 500; }}
.orr-play {{
  font: 500 11px/1 var(--mono); text-transform: uppercase; letter-spacing: 0.12em;
  padding: 0.5rem 0.85rem; border-radius: 4px; cursor: pointer;
  background: rgba(207, 165, 68, 0.22); border: 1px solid rgba(207, 165, 68, 0.55); color: #f8e5b8;
}}
@media (max-width: 42rem) {{ .orr-hud {{ grid-template-columns: 1fr; }} }}
</style>
<div class="orr-plate">
  <div class="orr-head">
    <div>
      <p class="orr-eyebrow">Live NASA/JPL SBDB Orbits · Top-Down Heliocentric Orrery</p>
      <h3 class="orr-title">The Taurid Orbital Corridor — Watch Napier's Fan Dissolve</h3>
    </div>
    <div class="orr-badge" id="orr-badge">Napier Box · H &lt; 16.5 (17 NEAs)</div>
  </div>
  <div class="orr-stage">
    <div class="orr-wrap">
      <canvas id="orr-canvas" aria-label="Interactive heliocentric solar system orrery showing Earth, Jupiter, Comet 2P/Encke, and real NASA/JPL near-Earth asteroid orbits across magnitude cutoffs."></canvas>
    </div>
  </div>
  <div class="orr-legend">
    <span class="orr-leg"><i class="orr-swatch" style="background:#56e0c8;height:2.5px"></i>Comet 2P/Encke (ϖ = 161.3°)</span>
    <span class="orr-leg"><i class="orr-swatch" style="background:#f5cb75"></i>Encke-aligned NEAs (|Δϖ| ≤ 45°)</span>
    <span class="orr-leg"><i class="orr-swatch" style="background:#6f98cc"></i>Unaligned NEAs (|Δϖ| &gt; 45°)</span>
    <span class="orr-leg"><i class="orr-swatch" style="background:none;border-top:1.5px dashed #e08652"></i>Jupiter orbit (ϖ_J = 14.7°)</span>
  </div>
  <div class="orr-hud">
    <div class="orr-cell"><div class="orr-val" id="orr-n">—</div><div class="orr-lbl">NEAs plotted in Napier's (a, e, i) box</div></div>
    <div class="orr-cell"><div class="orr-val" id="orr-f45">—</div><div class="orr-lbl">Share within ±45° of Encke (random = 25%)</div></div>
    <div class="orr-cell"><div class="orr-val" id="orr-cbar">—</div><div class="orr-lbl">Mean alignment c̄ toward Encke (0 = random)</div></div>
  </div>
  <div class="orr-controls">
    <div class="orr-tabs" id="orr-tabs">
      <button type="button" class="orr-btn is-active" data-mode="16.5">Napier 2010 (H &lt; 16.5 · 17)</button>
      <button type="button" class="orr-btn" data-mode="18.0">1 km Tier (H &lt; 18.0 · 64)</button>
      <button type="button" class="orr-btn" data-mode="20.0">400 m Tier (H &lt; 20.0 · 331)</button>
      <button type="button" class="orr-btn" data-mode="res72">7:2 Resonance Census (13)</button>
    </div>
    <button type="button" class="orr-play" id="orr-play">&#9654; Animate Orbits</button>
  </div>
</div>
<figcaption>Real Keplerian orbits from NASA/JPL's Small-Body Database (2026-11-23) projected onto the ecliptic plane (vernier 0° right, increasing counterclockwise). At Napier's (2010) bright cutoff (<em>H &lt; 16.5</em>, 17 giants), golden ellipses fan conspicuously toward Comet 2P/Encke's perihelion (161.3°, lower-left). Click <strong>1 km Tier (H &lt; 18.0)</strong> or <strong>400 m Tier (H &lt; 20.0)</strong> and watch that golden fan vanish into a symmetric halo—opposite to what a fragmenting comet produces. Click <strong>7:2 Resonance Census</strong> to isolate all 13 H &lt; 20 NEAs inside the 2.21–2.30 AU resonant band.</figcaption>
<script>
(function() {{
  const D = {payload_json};
  const canvas = document.getElementById("orr-canvas");
  const ctx = canvas.getContext("2d");
  const badge = document.getElementById("orr-badge");
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
    W = Math.max(300, Math.round(rect.width));
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = W * dpr; canvas.height = W * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    render();
  }}

  function render() {{
    const cx = W / 2, cy = W / 2;
    const scale = (W * 0.44) / 5.4; // 5.4 AU radius fits Jupiter (5.2 AU)
    ctx.clearRect(0, 0, W, W);

    // Coordinate rings (1, 2, 3, 4, 5 AU)
    ctx.font = "400 9.5px " + getComputedStyle(document.body).getPropertyValue("--mono");
    for (let au = 1; au <= 5; au++) {{
      ctx.beginPath();
      ctx.arc(cx, cy, au * scale, 0, Math.PI * 2);
      ctx.strokeStyle = au === 1 ? "rgba(110, 178, 255, 0.35)" : "rgba(190, 204, 232, 0.08)";
      ctx.lineWidth = au === 1 ? 1.2 : 0.8;
      ctx.stroke();
    }}

    // Taurid +/-45 deg perihelion wedge around 161.3 deg
    const vpE = (D.encke.varpi * Math.PI) / 180;
    ctx.save();
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    // Canvas y is inverted so angle -> -angle
    ctx.arc(cx, cy, 4.9 * scale, -(vpE + Math.PI / 4), -(vpE - Math.PI / 4));
    ctx.closePath();
    ctx.fillStyle = "rgba(245, 203, 117, 0.055)";
    ctx.fill();
    ctx.restore();

    // Jupiter orbit (a=5.203, e=0.0489, varpi=14.7 deg)
    drawEllipse(5.203, 0.0489, 14.7, cx, cy, scale, "rgba(224, 134, 82, 0.45)", 1.3, [5, 4]);
    // Jupiter perihelion arrow
    const jAng = (14.7 * Math.PI) / 180;
    ctx.fillStyle = "rgba(235, 152, 102, 0.8)";
    ctx.fillText("Jupiter (ϖ=14.7°)", cx + Math.cos(jAng) * 4.35 * scale - 44, cy - Math.sin(jAng) * 4.35 * scale - 6);

    // Mars (1.524) & Earth (1.000)
    drawEllipse(1.524, 0.0934, 336.0, cx, cy, scale, "rgba(218, 128, 92, 0.22)", 0.9, null);

    // Plot active NEAs
    const list = activeOrbits();
    const alphaUn = list.length > 150 ? 0.14 : list.length > 40 ? 0.26 : 0.42;
    const alphaAl = list.length > 150 ? 0.28 : list.length > 40 ? 0.46 : 0.68;

    let nAl = 0, sumCos = 0;
    list.forEach(o => {{
      const [a, e, vp, H, al45, res72, tight, ma0] = o;
      if (al45) nAl++;
      sumCos += Math.cos(((vp - D.encke.varpi) * Math.PI) / 180);
      const col = mode === "res72"
        ? (tight ? "rgba(248, 206, 110, 0.78)" : "rgba(155, 198, 245, 0.45)")
        : (al45 ? "rgba(245, 203, 117, " + alphaAl + ")" : "rgba(110, 155, 212, " + alphaUn + ")");
      drawEllipse(a, e, vp, cx, cy, scale, col, mode === "res72" ? 1.35 : 0.9, null);

      // Draw moving asteroid dot
      const perY = Math.pow(a, 1.5);
      const M = ((ma0 * Math.PI) / 180) + (simYr / perY) * Math.PI * 2;
      const [px, py] = orbitPos(a, e, vp, M);
      ctx.beginPath();
      ctx.arc(cx + px * scale, cy - py * scale, mode === "res72" ? 3.2 : (list.length > 100 ? 1.5 : 2.3), 0, Math.PI * 2);
      ctx.fillStyle = al45 ? "#f9d682" : "#7ca8df";
      ctx.fill();
    }});

    // Comet 2P/Encke luminous orbit + moving nucleus
    drawEllipse(D.encke.a, D.encke.e, D.encke.varpi, cx, cy, scale, "#56e0c8", 2.2, null);
    const ePer = Math.pow(D.encke.a, 1.5);
    const [ex, ey] = orbitPos(D.encke.a, D.encke.e, D.encke.varpi, 2.15 + (simYr / ePer) * Math.PI * 2);
    ctx.beginPath();
    ctx.arc(cx + ex * scale, cy - ey * scale, 4.5, 0, Math.PI * 2);
    ctx.fillStyle = "#7cf5df";
    ctx.shadowColor = "#56e0c8"; ctx.shadowBlur = 10; ctx.fill(); ctx.shadowBlur = 0;

    // Encke perihelion label
    ctx.fillStyle = "#7cf5df";
    ctx.fillText("2P/Encke (ϖ=161.3°)", cx + Math.cos(vpE) * 4.45 * scale - 32, cy - Math.sin(vpE) * 4.45 * scale + 12);

    // Earth & Jupiter dots
    const eAng = simYr * Math.PI * 2;
    ctx.beginPath(); ctx.arc(cx + Math.cos(eAng) * scale, cy - Math.sin(eAng) * scale, 4, 0, Math.PI * 2);
    ctx.fillStyle = "#6cbaff"; ctx.fill();
    const jpAng = (14.7 * Math.PI) / 180 + (simYr / 11.86) * Math.PI * 2;
    ctx.beginPath(); ctx.arc(cx + Math.cos(jpAng) * 5.203 * scale, cy - Math.sin(jpAng) * 5.203 * scale, 5.5, 0, Math.PI * 2);
    ctx.fillStyle = "#e59663"; ctx.fill();

    // Glowing Sun at center
    const sunG = ctx.createRadialGradient(cx, cy, 0, cx, cy, 14);
    sunG.addColorStop(0, "#fff8d6");
    sunG.addColorStop(0.35, "#f7c75b");
    sunG.addColorStop(1, "rgba(247, 199, 91, 0)");
    ctx.fillStyle = sunG;
    ctx.beginPath(); ctx.arc(cx, cy, 14, 0, Math.PI * 2); ctx.fill();

    // Update HUD
    const n = list.length;
    const f45 = n ? (100 * nAl) / n : 0;
    const cbar = n ? sumCos / n : 0;
    hudN.textContent = String(n);
    hudF.textContent = mode === "res72" ? "100% (filtered)" : (f45.toFixed(1) + "% (" + nAl + "/" + n + ")");
    hudF.className = "orr-val " + (mode !== "res72" && f45 > 45 ? "is-good" : mode !== "res72" && f45 <= 32 ? "is-warn" : "");
    hudC.textContent = (cbar >= 0 ? "+" : "") + cbar.toFixed(3);
    hudC.className = "orr-val " + (cbar > 0.25 ? "is-good" : cbar < 0.05 ? "is-warn" : "");

    const titles = {{
      "16.5": "Napier 2010 Cutoff · H < 16.5 (17 NEAs)",
      "18.0": "Primary 1 km Tier · H < 18.0 (64 NEAs)",
      "20.0": "Sub-km 400 m Tier · H < 20.0 (331 NEAs)",
      "res72": "7:2 Resonance Band (2.21–2.30 AU) · 13 NEAs"
    }};
    badge.textContent = titles[mode];
  }}

  tabs.forEach(btn => {{
    btn.addEventListener("click", () => {{
      mode = btn.dataset.mode;
      tabs.forEach(b => b.classList.toggle("is-active", b === btn));
      render();
    }});
  }});

  playBtn.addEventListener("click", () => {{
    anim = !anim;
    playBtn.innerHTML = anim ? "&#9646;&#9646; Pause Orbits" : "&#9654; Animate Orbits";
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
.taurid-radar-fig {{ margin: 2.2rem 0 2.6rem; }}
.rad-plate {{
  background: linear-gradient(180deg, #101626 0%, #090d17 100%);
  border: 1px solid rgba(207, 165, 68, 0.34);
  border-radius: 6px;
  color: #f3ecdf;
  overflow: hidden;
  box-shadow: 0 18px 46px rgba(12, 10, 8, 0.24);
}}
.rad-head {{
  display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between;
  gap: 0.6rem 1rem; padding: 1rem 1.35rem 0.85rem;
  border-bottom: 1px solid rgba(207, 165, 68, 0.18);
}}
.rad-tabs {{ display: flex; flex-wrap: wrap; gap: 0.36rem; }}
.rad-tab {{
  font: 500 11px/1.2 var(--mono); padding: 0.36rem 0.62rem; border-radius: 3px; cursor: pointer;
  background: rgba(255,255,255,0.04); border: 1px solid rgba(207,165,68,0.22); color: #cfc3ad;
}}
.rad-tab:hover {{ border-color: rgba(207,165,68,0.6); color: #fff4da; }}
.rad-tab.is-active {{ background: rgba(207,165,68,0.24); border-color: #e6ba63; color: #fff4da; }}
.rad-stage {{ display: flex; justify-content: center; padding: 0.8rem 1rem 0.5rem; }}
.rad-stage canvas {{ display: block; width: 100%; max-width: 680px; height: 340px; }}
.rad-bar {{
  padding: 0.7rem 1.35rem 0.95rem; border-top: 1px solid rgba(207,165,68,0.16);
  background: rgba(7, 10, 18, 0.75); font: 400 11.5px/1.45 var(--mono); color: #b8c4d8;
  text-align: center;
}}
.rad-bar strong {{ color: #f6d483; }}
</style>
<div class="rad-plate">
  <div class="rad-head">
    <div>
      <p class="orr-eyebrow" style="margin-bottom:.18rem">Perihelion Rose · Size-Inversion Test</p>
      <h3 class="orr-title">Taurid Corridor vs. Jupiter's Secular Gravity Pull</h3>
    </div>
    <div class="rad-tabs" id="rad-tabs">
      <button type="button" class="rad-tab is-active" data-k="H_lt_16.5">H &lt; 16.5</button>
      <button type="button" class="rad-tab" data-k="H_lt_18.0">H &lt; 18.0</button>
      <button type="button" class="rad-tab" data-k="H_lt_20.0">H &lt; 20.0</button>
      <button type="button" class="rad-tab" data-k="H_lt_22.0">H &lt; 22.0</button>
      <button type="button" class="rad-tab" data-k="all_H">All H</button>
    </div>
  </div>
  <div class="rad-stage">
    <canvas id="rad-canvas" aria-label="Polar rose histograms of asteroid longitude of perihelion comparing Napier's Taurid box against Jupiter's moderate-eccentricity secular control across five magnitude tiers."></canvas>
  </div>
  <div class="rad-bar" id="rad-bar">—</div>
</div>
<figcaption>Side-by-side normalized polar distributions of longitude of perihelion (ϖ in 20° wedges). <strong>Left (gold):</strong> Napier's Taurid orbital box (e ≥ 0.63, i ≤ 14°). <strong>Right (sapphire):</strong> Moderate-eccentricity control (0.40 ≤ e &lt; 0.63), which stays permanently locked toward Jupiter's perihelion (14.7°, right). Step from <em>H &lt; 16.5</em> to <em>H &lt; 18.0</em> and <em>H &lt; 20.0</em>: Napier's bright-only bulge toward Encke (161.3°, left) flattens completely to a round circle while Jupiter's secular bulge stays razor-sharp.</figcaption>
<script>
(function() {{
  const T = {pjson};
  const canvas = document.getElementById("rad-canvas");
  const ctx = canvas.getContext("2d");
  const bar = document.getElementById("rad-bar");
  const tabs = Array.from(document.querySelectorAll("#rad-tabs .rad-tab"));
  let key = "H_lt_16.5";
  let W = 680, H = 340;

  function resize() {{
    const rect = canvas.parentElement.getBoundingClientRect();
    W = Math.max(300, Math.min(680, Math.round(rect.width - 16)));
    H = W < 500 ? 520 : 340;
    canvas.style.height = H + "px";
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = W * dpr; canvas.height = H * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    render();
  }}

  function drawRose(cx, cy, R, counts, nTot, fillCol, strokeCol, title, sub) {{
    // Background concentric rings (expected uniform = 1/18 = 5.56%, rings at 1x, 2x, 3x uniform)
    const expFrac = 1 / 18;
    const maxFrac = Math.max(expFrac * 2.4, ...counts.map(c => (nTot ? c / nTot : 0)));
    ctx.save();
    for (const mult of [1, 2]) {{
      const rr = R * Math.min(1, (mult * expFrac) / maxFrac);
      ctx.beginPath(); ctx.arc(cx, cy, rr, 0, Math.PI * 2);
      ctx.strokeStyle = mult === 1 ? "rgba(255,255,255,0.28)" : "rgba(255,255,255,0.1)";
      ctx.setLineDash(mult === 1 ? [3, 3] : []);
      ctx.lineWidth = 1; ctx.stroke();
    }}
    ctx.setLineDash([]);

    // Outer frame circle
    ctx.beginPath(); ctx.arc(cx, cy, R, 0, Math.PI * 2);
    ctx.strokeStyle = "rgba(207,165,68,0.25)"; ctx.lineWidth = 1; ctx.stroke();

    // 18 wedges (20 deg each)
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

    // Encke (161.3 deg) & Jupiter (14.7 deg) reference spokes
    const eA = -(161.29 * Math.PI) / 180;
    ctx.beginPath(); ctx.moveTo(cx, cy); ctx.lineTo(cx + (R + 10) * Math.cos(eA), cy + (R + 10) * Math.sin(eA));
    ctx.strokeStyle = "#56e0c8"; ctx.lineWidth = 1.8; ctx.stroke();

    const jA = -(14.7 * Math.PI) / 180;
    ctx.beginPath(); ctx.moveTo(cx, cy); ctx.lineTo(cx + (R + 10) * Math.cos(jA), cy + (R + 10) * Math.sin(jA));
    ctx.strokeStyle = "#e08652"; ctx.lineWidth = 1.5; ctx.setLineDash([3, 3]); ctx.stroke();
    ctx.setLineDash([]);

    ctx.font = "600 10px " + getComputedStyle(document.body).getPropertyValue("--mono");
    ctx.fillStyle = "#7cf5df"; ctx.textAlign = "right";
    ctx.fillText("Encke 161°", cx + (R + 12) * Math.cos(eA) - 2, cy + (R + 12) * Math.sin(eA) + 4);
    ctx.fillStyle = "#ee9a6a"; ctx.textAlign = "left";
    ctx.fillText("Jup 15°", cx + (R + 12) * Math.cos(jA) + 3, cy + (R + 12) * Math.sin(jA) + 4);

    ctx.textAlign = "center";
    ctx.font = "500 13px " + getComputedStyle(document.body).getPropertyValue("--serif");
    ctx.fillStyle = "#f8f0df";
    ctx.fillText(title, cx, cy - R - 20);
    ctx.font = "400 10.5px " + getComputedStyle(document.body).getPropertyValue("--mono");
    ctx.fillStyle = "#a5b2c7";
    ctx.fillText(sub, cx, cy + R + 22);
    ctx.restore();
  }}

  function render() {{
    const d = T[key];
    ctx.clearRect(0, 0, W, H);
    const stacked = W < 500;
    const R = stacked ? Math.min(100, W * 0.3) : Math.min(112, W * 0.175);
    const c1 = stacked ? [W / 2, H * 0.26] : [W * 0.27, H * 0.52];
    const c2 = stacked ? [W / 2, H * 0.75] : [W * 0.73, H * 0.52];

    drawRose(c1[0], c1[1], R, d.h_t, d.n_t, "rgba(245, 203, 117, 0.42)", "rgba(245, 203, 117, 0.9)",
             "Napier Taurid Box (e ≥ 0.63)", "N=" + d.n_t + " · c̄=" + (d.c_t >= 0 ? "+" : "") + d.c_t.toFixed(3) + " · p=" + d.p_unif.toFixed(4));
    drawRose(c2[0], c2[1], R, d.h_l, d.n_l, "rgba(114, 180, 250, 0.36)", "rgba(114, 180, 250, 0.88)",
             "Jupiter Secular Control (0.40 ≤ e < 0.63)", "N=" + d.n_l + " · c̄=" + (d.c_l >= 0 ? "+" : "") + d.c_l.toFixed(3) + " (locked to Jupiter)");

    bar.innerHTML = 'Tier <strong>' + key.replace("H_lt_", "H < ").replace("all_H", "All H") + '</strong> &nbsp;|&nbsp; Taurid ±45° share: <strong>' + (100 * d.f45_t).toFixed(1) + '%</strong> (random = 25.0%) &nbsp;|&nbsp; vs. Inclined high-e control: <strong>p = ' + d.p_hi.toFixed(3) + '</strong>';
  }}

  tabs.forEach(t => {{
    t.addEventListener("click", () => {{
      key = t.dataset.k;
      tabs.forEach(b => b.classList.toggle("is-active", b === t));
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
.taurid-fb-fig {{ margin: 2.2rem 0 2.6rem; }}
.fb-plate {{
  background: linear-gradient(180deg, #101626 0%, #090d17 100%);
  border: 1px solid rgba(207, 165, 68, 0.34);
  border-radius: 6px;
  color: #f3ecdf;
  overflow: hidden;
  box-shadow: 0 18px 46px rgba(12, 10, 8, 0.24);
}}
.fb-head {{
  display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between;
  gap: 0.6rem 1rem; padding: 1rem 1.35rem 0.85rem;
  border-bottom: 1px solid rgba(207, 165, 68, 0.18);
}}
.fb-tabs {{ display: flex; flex-wrap: wrap; gap: 0.4rem; }}
.fb-tab {{
  font: 500 11px/1.2 var(--mono); padding: 0.38rem 0.7rem; border-radius: 3px; cursor: pointer;
  background: rgba(255,255,255,0.04); border: 1px solid rgba(207,165,68,0.22); color: #cfc3ad;
}}
.fb-tab:hover {{ border-color: rgba(207,165,68,0.6); color: #fff4da; }}
.fb-tab.is-active {{ background: rgba(207,165,68,0.24); border-color: #e6ba63; color: #fff4da; }}
.fb-wrap {{ padding: 0.7rem 1rem 0.35rem; }}
.fb-wrap canvas {{ display: block; width: 100%; height: 320px; cursor: crosshair; }}
.fb-bar {{
  padding: 0.65rem 1.35rem 0.9rem; border-top: 1px solid rgba(207,165,68,0.16);
  background: rgba(7, 10, 18, 0.75); font: 400 11.5px/1.4 var(--mono); color: #b8c4d8;
}}
.fb-bar strong {{ color: #f6d483; }}
</style>
<div class="fb-plate">
  <div class="fb-head">
    <div>
      <p class="orr-eyebrow" style="margin-bottom:.18rem">NASA CNEOS Global Satellite Sensors · 1994–2025 (1,045 Airbursts)</p>
      <h3 class="orr-title">Do Meter-Scale Airbursts Surge During Taurid Swarm Returns?</h3>
    </div>
    <div class="fb-tabs" id="fb-tabs">
      <button type="button" class="fb-tab is-active" data-v="swarm">Swarm Return Years (1994–2025)</button>
      <button type="button" class="fb-tab" data-v="monthly">Calendar Seasonality (Jan–Dec)</button>
    </div>
  </div>
  <div class="fb-wrap">
    <canvas id="fb-canvas" aria-label="Interactive chart of 32 years of NASA CNEOS satellite-detected fireballs comparing published 7:2 Taurid resonant swarm return years against non-swarm years and across all 12 calendar months."></canvas>
  </div>
  <div class="fb-bar" id="fb-bar">Hover any bar to inspect exact yearly or monthly satellite bolide counts and impact energy.</div>
</div>
<figcaption>US government satellite bolide detections from NASA/JPL CNEOS across 32 complete years (1994–2025; 1,045 events, 1,182 kt total energy). <strong>Swarm Return Years view:</strong> within-year Autumn Taurid bolide share (Oct 15–Nov 30) removes long-term sensor-sensitivity drift; the 6 published 7:2 resonant swarm years (gold bars: 1998, 2005, 2015, 2018, 2022, 2025) average <strong>12.7%</strong> vs. <strong>13.0%</strong> in the 26 non-swarm years (p = 0.520). <strong>Calendar Seasonality view:</strong> both the Autumn Taurids (0.99× expected) and Daytime β-Taurids (0.91× expected) sit completely flat.</figcaption>
<script>
(function() {{
  const D = {pjson};
  const canvas = document.getElementById("fb-canvas");
  const ctx = canvas.getContext("2d");
  const bar = document.getElementById("fb-bar");
  const tabs = Array.from(document.querySelectorAll("#fb-tabs .fb-tab"));
  let view = "swarm", hoverIdx = -1, W = 700, H = 320;
  const PAD = {{ l: 50, r: 20, t: 24, b: 40 }};
  const MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];

  function resize() {{
    const rect = canvas.parentElement.getBoundingClientRect();
    W = Math.max(300, Math.round(rect.width - 32));
    H = W < 500 ? 290 : 320;
    canvas.style.height = H + "px";
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = W * dpr; canvas.height = H * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    render();
  }}

  function render() {{
    const pw = W - PAD.l - PAD.r, ph = H - PAD.t - PAD.b;
    ctx.clearRect(0, 0, W, H);
    ctx.font = "400 10px " + getComputedStyle(document.body).getPropertyValue("--mono");

    if (view === "swarm") {{
      const rows = D.yearly;
      const yMax = 0.34;
      const yOf = v => PAD.t + ((yMax - v) / yMax) * ph;
      const bw = pw / rows.length;

      // Grid lines
      ctx.textAlign = "right";
      for (const p of [0, 0.10, 0.20, 0.30]) {{
        const y = yOf(p);
        ctx.beginPath(); ctx.moveTo(PAD.l, y); ctx.lineTo(PAD.l + pw, y);
        ctx.strokeStyle = "rgba(255,255,255,0.08)"; ctx.stroke();
        ctx.fillStyle = "#94a2b8"; ctx.fillText(Math.round(p * 100) + "%", PAD.l - 7, y + 3.5);
      }}

      // Expected uniform 12.87% & swarm mean 12.70%
      const yExp = yOf(0.1287);
      ctx.save();
      ctx.setLineDash([4, 4]);
      ctx.strokeStyle = "rgba(138, 211, 181, 0.65)"; ctx.lineWidth = 1.3;
      ctx.beginPath(); ctx.moveTo(PAD.l, yExp); ctx.lineTo(PAD.l + pw, yExp); ctx.stroke();
      ctx.restore();
      ctx.textAlign = "right"; ctx.fillStyle = "#8ad3b5";
      ctx.fillText("Expected uniform 12.9% · Swarm avg 12.7%", PAD.l + pw - 4, yExp - 5);

      rows.forEach((r, i) => {{
        const x = PAD.l + i * bw + bw * 0.14;
        const w = Math.max(3, bw * 0.72);
        const y = yOf(r.s_cnt);
        const isHov = i === hoverIdx;
        ctx.fillStyle = r.swarm6
          ? (isHov ? "#ffe39e" : "#e8b456")
          : (isHov ? "#95b9e8" : "rgba(104, 134, 178, 0.55)");
        ctx.fillRect(x, y, w, PAD.t + ph - y);
        if (r.swarm6) {{
          ctx.fillStyle = "#f7cf78";
          ctx.textAlign = "center";
          ctx.fillText("★", x + w / 2, y - 4);
        }}
        if (r.year % 4 === 0 || r.swarm6) {{
          ctx.fillStyle = r.swarm6 ? "#f7cf78" : "#8c9ab0";
          ctx.textAlign = "center";
          ctx.fillText(String(r.year).slice(2), x + w / 2, PAD.t + ph + 15);
        }}
      }});
      ctx.textAlign = "center"; ctx.fillStyle = "#9aa7bd";
      ctx.fillText("Year (1994–2025 · ★ = Published 7:2 Resonant Swarm Return Years)", PAD.l + pw / 2, H - 6);
    }} else {{
      const rows = D.monthly;
      const yMax = 115;
      const yOf = v => PAD.t + ((yMax - v) / yMax) * ph;
      const bw = pw / 12;

      // Shaded Taurid season columns (Jun-Jul daytime, Oct-Nov autumn)
      ctx.fillStyle = "rgba(114, 185, 255, 0.08)";
      ctx.fillRect(PAD.l + 5.3 * bw, PAD.t, 1.0 * bw, ph);
      ctx.fillStyle = "rgba(245, 203, 117, 0.09)";
      ctx.fillRect(PAD.l + 9.45 * bw, PAD.t, 1.55 * bw, ph);

      ctx.textAlign = "right";
      for (const v of [0, 30, 60, 90]) {{
        const y = yOf(v);
        ctx.beginPath(); ctx.moveTo(PAD.l, y); ctx.lineTo(PAD.l + pw, y);
        ctx.strokeStyle = "rgba(255,255,255,0.08)"; ctx.stroke();
        ctx.fillStyle = "#94a2b8"; ctx.fillText(String(v), PAD.l - 7, y + 3.5);
      }}

      const yAvg = yOf(1045 / 12);
      ctx.save(); ctx.setLineDash([4, 4]); ctx.strokeStyle = "rgba(138, 211, 181, 0.65)";
      ctx.beginPath(); ctx.moveTo(PAD.l, yAvg); ctx.lineTo(PAD.l + pw, yAvg); ctx.stroke(); ctx.restore();

      rows.forEach((r, i) => {{
        const x = PAD.l + i * bw + bw * 0.18;
        const w = bw * 0.64;
        const y = yOf(r.count);
        const isAut = (i === 9 || i === 10);
        const isDay = (i === 5 || i === 6);
        const isHov = i === hoverIdx;
        ctx.fillStyle = isAut ? (isHov ? "#ffe29b" : "#e8b456")
                     : isDay ? (isHov ? "#a7d5ff" : "#6ca8e6")
                     : (isHov ? "#9ab0cf" : "rgba(110, 134, 170, 0.52)");
        ctx.fillRect(x, y, w, PAD.t + ph - y);
        ctx.fillStyle = "#e6ebf2"; ctx.textAlign = "center";
        ctx.fillText(String(r.count), x + w / 2, y - 5);
        ctx.fillStyle = isAut ? "#f7cf78" : isDay ? "#8cc7ff" : "#9aa7bd";
        ctx.fillText(MONTHS[i], x + w / 2, PAD.t + ph + 16);
      }});
      ctx.textAlign = "center"; ctx.fillStyle = "#9aa7bd";
      ctx.fillText("Calendar Month (1994–2025 · Gold = Oct–Nov Autumn Taurids, Blue = Jun–Jul Daytime β-Taurids)", PAD.l + pw / 2, H - 6);
    }}
    ctx.strokeStyle = "rgba(207, 165, 68, 0.3)"; ctx.lineWidth = 1;
    ctx.strokeRect(PAD.l, PAD.t, pw, ph);
  }}

  tabs.forEach(t => {{
    t.addEventListener("click", () => {{
      view = t.dataset.v; hoverIdx = -1;
      tabs.forEach(b => b.classList.toggle("is-active", b === t));
      bar.textContent = "Hover any bar to inspect exact yearly or monthly satellite bolide counts and impact energy.";
      render();
    }});
  }});

  canvas.addEventListener("mousemove", ev => {{
    const rect = canvas.getBoundingClientRect();
    const mx = ev.clientX - rect.left;
    const pw = W - PAD.l - PAD.r;
    if (mx < PAD.l || mx > PAD.l + pw) {{ hoverIdx = -1; render(); return; }}
    const n = view === "swarm" ? D.yearly.length : 12;
    const idx = Math.min(n - 1, Math.max(0, Math.floor(((mx - PAD.l) / pw) * n)));
    if (idx !== hoverIdx) {{ hoverIdx = idx; render(); }}
    if (view === "swarm") {{
      const r = D.yearly[idx];
      bar.innerHTML = '<strong>' + r.year + (r.swarm6 ? ' ★ (7:2 Swarm Year)' : ' (Non-swarm)') + '</strong> &nbsp;|&nbsp; Autumn Taurids: <strong>' + r.n_aut + '/' + r.n_year + ' (' + (100 * r.s_cnt).toFixed(1) + '%)</strong> &nbsp;|&nbsp; ≥1 kt: <strong>' + r.n_aut_1kt + '</strong> &nbsp;|&nbsp; Autumn energy: <strong>' + r.e_aut_kt.toFixed(2) + ' kt</strong>';
    }} else {{
      const r = D.monthly[idx];
      bar.innerHTML = '<strong>' + MONTHS[idx] + ' (1994–2025)</strong> &nbsp;|&nbsp; Bolides: <strong>' + r.count + '</strong> &nbsp;|&nbsp; Large (≥1 kt): <strong>' + r.count_1kt + '</strong> &nbsp;|&nbsp; Total energy: <strong>' + r.energy_kt.toFixed(1) + ' kt</strong>';
    }}
  }});
  canvas.addEventListener("mouseleave", () => {{ hoverIdx = -1; render(); }});

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
