#!/usr/bin/env python3
"""
Generate self-contained, zero-dependency interactive HTML figures for
site/figures/anaesthetics-microtubules/ strictly from locked results/summary.json
and results/poses_3d.json.

Figures produced:
  1. tiles.html   - Native .tiles headline strip
  2. verdict.html - Native .verdict pre-registered check table
  3. potency.html - Interactive Target-by-Target Potency, Meyer-Overton & Size Explorer
  4. matrix.html  - Interactive Target Specificity Scorecard & 35x8 Affinity Heatmap
  5. pockets.html - Interactive 3D Drag-to-Rotate Pocket & Docked Pose Observatory

Palette and typography strictly follow site/assets/site.css (warm obsidian --band,
parchment ink, copper/ochre/verdigris/slate accents, shape + colour encoding, no neon glow).
"""
from __future__ import annotations

import html
import json
import math
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT.parent.parent
RESULTS = ROOT / "results"
OUT_DIR = REPO / "site" / "figures" / "anaesthetics-microtubules"

esc = lambda s: html.escape(str(s), quote=True)


def fmt_p(p: float) -> str:
    if p < 0.001:
        return "p < 0.001"
    return f"p = {p:.3f}"


def fmt_signed(x: float, digits: int = 2) -> str:
    return f"{x:+.{digits}f}".replace("-", "−")


# Plain names for the eight proteins (PDB codes stay in small type and tooltips).
PLAIN_LABEL = {
    "tubulin_1jff": "Tubulin",
    "tubulin_4i4t": "Tubulin, sharper structure",
    "gabaa_6x3t": "GABA-A channel",
    "glic_3p4w": "GLIC channel",
    "hsa_1e7b": "Albumin",
    "luciferase_1ba3": "Luciferase",
    "lysozyme_1dpx": "Lysozyme",
    "ubiquitin_1ubq": "Ubiquitin",
}
# Two-line column heads for the narrow heatmap columns.
SHORT_LABEL = {
    "tubulin_1jff": ["Tubulin", ""],
    "tubulin_4i4t": ["Tubulin", "sharper"],
    "gabaa_6x3t": ["GABA-A", "channel"],
    "glic_3p4w": ["GLIC", "channel"],
    "hsa_1e7b": ["Albumin", ""],
    "luciferase_1ba3": ["Luciferase", ""],
    "lysozyme_1dpx": ["Lysozyme", ""],
    "ubiquitin_1ubq": ["Ubiquitin", ""],
}


def plain_targets(meta: Dict) -> Dict:
    """Copy target metadata with plain-language labels; the PDB code is kept separately."""
    out = {}
    for tid, m in meta.items():
        mm = dict(m)
        mm["label"] = PLAIN_LABEL[tid]
        mm["short"] = SHORT_LABEL[tid]
        out[tid] = mm
    return out


def build_tiles(summary: Dict) -> str:
    vina = summary["scoring"]["vina"]
    best = vina["targets_best"]
    t_tub = best["tubulin_1jff"]

    # Trial fits = pockets on all proteins x molecules x scoring methods (24 x 35 x 2 = 1,680).
    n_pockets = sum(m["n_sites"] for m in summary["target_meta"].values())
    n_fits = n_pockets * len(summary["molecules"]) * len(summary["scoring"])
    n_mols = len(summary["molecules"])
    n_prot = len(summary["target_meta"])

    # The ubiquitin tile claims it matches potency at least as well as every other protein.
    assert best["ubiquitin_1ubq"]["rho_pot"] >= max(v["rho_pot"] for v in best.values()), "ubiquitin tile wording no longer holds"
    assert summary["verdict"]["verdict_code"] == "no_potency_or_selectivity", "verdict tile wording assumes this verdict"

    items = [
        (f"{n_fits:,}", f"trial fits of {n_mols} gases into pockets on {'eight' if n_prot == 8 else n_prot} proteins", False),
        (f"{t_tub['rho_pot']:.2f}", "how well predicted grip on tubulin matches anaesthetic strength, where 1 is perfect and 0 is none", False),
        ("Ubiquitin", "an unrelated protein, matches anaesthetic strength at least as well as tubulin or the accepted targets", True),
        ("Cannot tell", "the method does not pick out microtubules, and does not pick out the accepted targets either", True),
    ]
    return '<div class="tiles">\n' + "\n".join(
        f'<div class="tile"><p class="tile-value{" is-word" if is_w else ""}">{esc(val)}</p><p class="tile-label">{esc(lbl)}</p></div>'
        for val, lbl, is_w in items
    ) + "\n</div>\n"


def build_verdict(summary: Dict) -> str:
    best = summary["scoring"]["vina"]["targets_best"]
    t1 = best["tubulin_1jff"]
    gab = best["gabaa_6x3t"]
    checks = summary["verdict"]["checks"]

    # The wording below states these facts; fail loudly if the results ever say otherwise.
    assert not checks["pot_1jff_vina"] and not checks["rej_1jff_vina"], "row (a) wording assumes the test failed"
    assert t1["auc_sep"] < 0.5 and gab["auc_sep"] < 0.5, "look-alikes no longer score tighter"
    assert best["ubiquitin_1ubq"]["rho_pot"] >= max(v["rho_pot"] for v in best.values()), "ubiquitin wording no longer holds"

    rows = [
        (
            "The test fixed in advance",
            "Does predicted grip on tubulin follow anaesthetic strength, and tell real anaesthetics from look-alikes?",
            f"No. The match with strength is weak ({t1['rho_pot']:.2f}, {fmt_p(t1['p_rho_pot'])}), and the look-alikes score tighter than the real anaesthetics.",
            "is-no",
            "Not found",
        ),
        (
            "The check on the method",
            "Does the same calculation pick out the ion channels that anaesthetics are known to act on?",
            "No. On the GABA-A channel the look-alikes also score tighter, and the unrelated protein ubiquitin does as well as any.",
            "is-no",
            "Fails too",
        ),
        (
            "What follows",
            "This kind of calculation cannot tell an anaesthetic target from any other protein",
            "The scores mostly follow the size of the molecule. So the result neither supports the idea that anaesthetics act on microtubules nor counts much against it.",
            "is-open",
            "Cannot tell",
        ),
    ]
    parts = ['<div class="verdict">']
    for kicker, title, note, cls, chip in rows:
        parts.append(
            f'<div class="verdict-row">\n'
            f'  <div>\n'
            f'    <p class="verdict-kicker">{esc(kicker)}</p>\n'
            f'    <p class="verdict-text">{esc(title)}</p>\n'
            f'    <p class="verdict-note">{esc(note)}</p>\n'
            f'  </div>\n'
            f'  <p class="verdict-status {cls}"><span class="dot" aria-hidden="true"></span>{esc(chip)}</p>\n'
            f'</div>'
        )
    parts.append("</div>\n")
    return "\n".join(parts)


SHARED_PANEL_CSS = """
.am-plate {
  background: var(--band, #171310);
  color: var(--band-ink, #f6f1e8);
  border: 1px solid var(--band-line, #3c352a);
  border-radius: 3px;
  padding: 1.15rem 1.25rem 1rem;
  margin: 1.5rem 0;
  font-family: var(--sans, system-ui, sans-serif);
}
.am-head {
  display: flex; flex-wrap: wrap; justify-content: space-between; align-items: baseline;
  gap: .5rem 1rem; border-bottom: 1px solid var(--band-line, #3c352a);
  padding-bottom: .65rem; margin-bottom: .85rem;
}
.am-kicker {
  font: 400 11px/1.4 var(--mono, monospace); text-transform: uppercase; letter-spacing: .18em;
  color: var(--band-copper, #d08a5c); margin: 0;
}
.am-title {
  font: 500 1.05rem/1.3 var(--serif, Georgia, serif); color: var(--band-ink, #f6f1e8); margin: .15rem 0 0;
}
.am-controls {
  display: flex; flex-wrap: wrap; gap: .45rem .65rem; align-items: center; margin-bottom: .8rem;
}
.am-group {
  display: inline-flex; flex-wrap: wrap; gap: .25rem; align-items: center;
  background: var(--band-soft, #211c16); border: 1px solid var(--band-line, #3c352a);
  border-radius: 2px; padding: .2rem;
}
.am-glabel {
  font: 400 10px/1 var(--mono, monospace); text-transform: uppercase; letter-spacing: .14em;
  color: var(--band-faint, #a1977f); padding: 0 .4rem;
}
.am-btn {
  appearance: none; border: 1px solid transparent; background: transparent;
  color: var(--band-ink-soft, #d9d0be); cursor: pointer;
  font: 400 12px/1.2 var(--sans, system-ui, sans-serif);
  padding: .32rem .55rem; border-radius: 2px; transition: background .12s, color .12s, border-color .12s;
}
.am-btn:hover { background: #2c261e; color: var(--band-ink, #f6f1e8); }
.am-btn.is-on {
  background: #332a20; color: var(--band-ink, #f6f1e8);
  border-color: var(--band-copper, #d08a5c); font-weight: 500;
}
.am-stats {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(135px, 1fr));
  gap: .5rem; margin-bottom: .75rem;
}
.am-stat {
  background: var(--band-soft, #211c16); border: 1px solid var(--band-line, #3c352a);
  border-radius: 2px; padding: .45rem .65rem;
}
.am-stat-k {
  font: 400 10px/1.3 var(--mono, monospace); text-transform: uppercase; letter-spacing: .14em;
  color: var(--band-faint, #a1977f); margin: 0;
}
.am-stat-v {
  font: 500 1rem/1.25 var(--mono, monospace); color: var(--band-ink, #f6f1e8); margin: .15rem 0 0;
}
.am-stat-s {
  font: 400 11px/1.3 var(--sans, system-ui, sans-serif); color: var(--band-faint, #a1977f); margin: .1rem 0 0;
}
.am-stage { position: relative; width: 100%; }
.am-canvas { display: block; width: 100%; background: #14110e; border: 1px solid var(--band-line, #3c352a); border-radius: 2px; }
.am-tip {
  position: absolute; pointer-events: none; z-index: 20; display: none;
  background: #1c1813; color: #f6f1e8; border: 1px solid #d08a5c; border-radius: 2px;
  padding: .45rem .65rem; font: 400 12px/1.45 var(--sans, system-ui, sans-serif);
  max-width: 260px; box-shadow: 0 6px 20px rgba(0,0,0,.45);
}
.am-tip strong { color: #f6f1e8; font-weight: 600; }
.am-tip .am-mono { font-family: var(--mono, monospace); font-size: 11px; color: #d9d0be; }
.am-legend {
  display: flex; flex-wrap: wrap; gap: .6rem 1.1rem; align-items: center;
  margin-top: .6rem; font: 400 12px/1.4 var(--sans, system-ui, sans-serif);
  color: var(--band-ink-soft, #d9d0be);
}
.am-leg-item { display: inline-flex; align-items: center; gap: .38rem; }
.am-cap {
  margin: .65rem 0 0; font: 400 13px/1.55 var(--sans, system-ui, sans-serif);
  color: var(--band-faint, #a1977f);
}
"""


def build_potency_explorer(summary: Dict) -> str:
    payload = {
        "molecules": summary["molecules"],
        "targets": plain_targets(summary["target_meta"]),
        "targetOrder": list(summary["target_meta"].keys()),
        "scoring": {
            sf: {
                "best": summary["scoring"][sf]["b_best_matrix"],
                "single": summary["scoring"][sf]["b_single_matrix"],
                "statsBest": summary["scoring"][sf]["targets_best"],
                "statsSingle": summary["scoring"][sf]["targets_single"],
            }
            for sf in ("vina", "vinardo")
        },
    }
    data_json = json.dumps(payload, separators=(",", ":"))
    return f"""<figure class="am-plate" id="am-potency-fig" aria-label="Interactive potency and non-anaesthetic binding explorer across eight proteins">
<style>{SHARED_PANEL_CSS}</style>
<div class="am-head">
  <div>
    <p class="am-kicker">Interactive Plate 1 · Target-by-Target Binding</p>
    <p class="am-title">Switch between tubulin, ion channels and control proteins</p>
  </div>
</div>
<div class="am-controls" id="am-p-targets"></div>
<div class="am-controls">
  <div class="am-group" id="am-p-xmode">
    <span class="am-glabel">X-Axis</span>
    <button type="button" class="am-btn is-on" data-v="potency">Potency (−log₁₀ MAC)</button>
    <button type="button" class="am-btn" data-v="oil">Fat solubility (log₁₀ λ_oil)</button>
    <button type="button" class="am-btn" data-v="heavy">Molecular size (heavy atoms)</button>
  </div>
  <div class="am-group" id="am-p-sf">
    <span class="am-glabel">Scoring</span>
    <button type="button" class="am-btn is-on" data-v="vina">Vina</button>
    <button type="button" class="am-btn" data-v="vinardo">Vinardo</button>
  </div>
  <div class="am-group" id="am-p-pmode">
    <span class="am-glabel">Pocket</span>
    <button type="button" class="am-btn is-on" data-v="best">Best pocket</button>
    <button type="button" class="am-btn" data-v="single">Single pocket</button>
  </div>
</div>
<div class="am-stats" id="am-p-stats"></div>
<div class="am-stage">
  <canvas class="am-canvas" id="am-p-canvas" height="410"></canvas>
  <div class="am-tip" id="am-p-tip"></div>
</div>
<div class="am-legend">
  <span class="am-leg-item"><svg width="12" height="12"><circle cx="6" cy="6" r="4.5" fill="#cfa544"/></svg> Clinical volatile anaesthetics (n = 9)</span>
  <span class="am-leg-item"><svg width="12" height="12"><polygon points="6,1.5 10.8,10.5 1.2,10.5" fill="#d08a5c"/></svg> Experimental volatile anaesthetics, Fang 1996 (n = 18)</span>
  <span class="am-leg-item"><svg width="12" height="12"><polygon points="6,1 11,6 6,11 1,6" fill="none" stroke="#7fb39d" stroke-width="1.8"/></svg> Confirmed non-immobilizers (n = 7)</span>
  <span class="am-leg-item"><svg width="12" height="12"><rect x="2" y="2" width="8" height="8" fill="none" stroke="#9aa5b3" stroke-width="1.6"/></svg> Flurothyl (convulsant)</span>
</div>
<figcaption class="am-cap">Higher on the vertical axis (−ΔG, kcal/mol) means tighter predicted binding. In Potency view, the right-hand strip places the 7 non-immobilizers (which fail to produce anaesthesia) directly alongside true anaesthetics; in Fat solubility and Molecular size views, the dashed line shows the anaesthetic trend so non-immobilizer residuals are directly visible. Hover any point for details.</figcaption>
<script>
(function(){{
  const D = {data_json};
  let target = 'tubulin_1jff', xmode = 'potency', sf = 'vina', pmode = 'best';
  const roleTag = {{test_primary:'Microtubule', test_replication:'Microtubule', rival_channel:'Rival channel', positive_control:'Soluble control', negative_control:'Negative control'}};

  const tWrap = document.getElementById('am-p-targets');
  const groups = [
    ['Microtubule', ['tubulin_1jff','tubulin_4i4t']],
    ['Rival channels', ['gabaa_6x3t','glic_3p4w']],
    ['Soluble controls', ['hsa_1e7b','luciferase_1ba3']],
    ['Negative controls', ['lysozyme_1dpx','ubiquitin_1ubq']]
  ];
  groups.forEach(([gl, ids]) => {{
    const g = document.createElement('div');
    g.className = 'am-group';
    const sp = document.createElement('span'); sp.className = 'am-glabel'; sp.textContent = gl; g.appendChild(sp);
    ids.forEach(id => {{
      const b = document.createElement('button');
      b.type = 'button'; b.className = 'am-btn' + (id === target ? ' is-on' : '');
      b.dataset.v = id; b.textContent = D.targets[id].label;
      b.addEventListener('click', () => {{ target = id; syncButtons(); draw(); }});
      g.appendChild(b);
    }});
    tWrap.appendChild(g);
  }});

  function bindGroup(id, setter){{
    document.getElementById(id).querySelectorAll('button').forEach(b => {{
      b.addEventListener('click', () => {{ setter(b.dataset.v); syncButtons(); draw(); }});
    }});
  }}
  bindGroup('am-p-xmode', v => xmode = v);
  bindGroup('am-p-sf', v => sf = v);
  bindGroup('am-p-pmode', v => pmode = v);

  function syncButtons(){{
    tWrap.querySelectorAll('button').forEach(b => b.classList.toggle('is-on', b.dataset.v === target));
    document.getElementById('am-p-xmode').querySelectorAll('button').forEach(b => b.classList.toggle('is-on', b.dataset.v === xmode));
    document.getElementById('am-p-sf').querySelectorAll('button').forEach(b => b.classList.toggle('is-on', b.dataset.v === sf));
    document.getElementById('am-p-pmode').querySelectorAll('button').forEach(b => b.classList.toggle('is-on', b.dataset.v === pmode));
  }}

  const canvas = document.getElementById('am-p-canvas');
  const tip = document.getElementById('am-p-tip');
  let hitPts = [];

  function fmtS(v, d=2){{ return (v >= 0 ? '+' : '−') + Math.abs(v).toFixed(d); }}
  function fmtP(p){{ return p < 0.001 ? 'p < 0.001' : 'p = ' + p.toFixed(3); }}

  function ols(xs, ys){{
    const n = xs.length;
    const mx = xs.reduce((a,b)=>a+b,0)/n, my = ys.reduce((a,b)=>a+b,0)/n;
    let num=0, den=0;
    for(let i=0;i<n;i++){{ num+=(xs[i]-mx)*(ys[i]-my); den+=(xs[i]-mx)*(xs[i]-mx); }}
    const sl = den > 1e-12 ? num/den : 0;
    return [my - sl*mx, sl];
  }}

  function renderStats(st){{
    const meta = D.targets[target];
    const el = document.getElementById('am-p-stats');
    const siteTxt = pmode === 'best' ? (meta.n_sites > 1 ? 'best of ' + meta.n_sites + ' pockets' : meta.primary_single_site) : meta.primary_single_site;
    el.innerHTML =
      '<div class="am-stat"><p class="am-stat-k">Potency Spearman ρ</p><p class="am-stat-v">' + fmtS(st.rho_pot) + '</p><p class="am-stat-s">' + fmtP(st.p_rho_pot) + ' · ' + siteTxt + '</p></div>' +
      '<div class="am-stat"><p class="am-stat-k">Partial ρ | Size</p><p class="am-stat-v">' + fmtS(st.rho_partial_heavy) + '</p><p class="am-stat-s">' + fmtP(st.p_partial_heavy) + ' · oil: ' + fmtS(st.rho_partial_oil) + '</p></div>' +
      '<div class="am-stat"><p class="am-stat-k">Non-Immobilizer AUC</p><p class="am-stat-v">' + st.auc_sep.toFixed(2) + '</p><p class="am-stat-s">' + fmtP(st.p_auc_sep) + ' · 0.50 = chance</p></div>' +
      '<div class="am-stat"><p class="am-stat-k">Non-Imm Oil Residual</p><p class="am-stat-v">' + fmtS(st.r_non_oil) + ' kcal</p><p class="am-stat-s">' + fmtP(st.p_non_oil) + ' · size: ' + fmtS(st.r_non_heavy) + '</p></div>';
  }}

  function draw(){{
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const W = canvas.parentElement.clientWidth || 720;
    const H = 410;
    canvas.width = Math.round(W * dpr);
    canvas.height = Math.round(H * dpr);
    canvas.style.height = H + 'px';
    const ctx = canvas.getContext('2d');
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    const sc = D.scoring[sf];
    const bMap = (pmode === 'best' ? sc.best : sc.single)[target];
    const st = (pmode === 'best' ? sc.statsBest : sc.statsSingle)[target];
    renderStats(st);

    ctx.fillStyle = '#14110e';
    ctx.fillRect(0, 0, W, H);

    const padL = 62, padT = 26, padB = 46;
    const stripW = xmode === 'potency' ? Math.max(96, Math.min(130, W * 0.19)) : 0;
    const gapStrip = xmode === 'potency' ? 18 : 0;
    const padR = 22 + stripW + gapStrip;
    const plotW = W - padL - padR;
    const plotH = H - padT - padB;

    const allB = D.molecules.map(m => bMap[m.mol_id]);
    const yMin = Math.floor((Math.min(...allB) - 0.35) * 2) / 2;
    const yMax = Math.ceil((Math.max(...allB) + 0.35) * 2) / 2;
    const sy = v => padT + plotH - ((v - yMin) / (yMax - yMin)) * plotH;

    let xMin, xMax, xLabel, xFn;
    if(xmode === 'potency'){{
      xMin = -0.15; xMax = 3.15;
      xLabel = 'Anaesthetic potency  −log₁₀(MAC in atm)   [higher = more potent]';
      xFn = m => m.mac_atm ? -Math.log10(m.mac_atm) : null;
    }} else if(xmode === 'oil'){{
      xMin = -0.6; xMax = 4.3;
      xLabel = 'Olive-oil / gas solubility  log₁₀(λ_oil at 37 °C)   [Meyer–Overton axis]';
      xFn = m => m.oil_gas ? Math.log10(m.oil_gas) : null;
    }} else {{
      xMin = 2; xMax = 19;
      xLabel = 'Heavy-atom count  N_heavy   [molecular size]';
      xFn = m => m.n_heavy;
    }}
    const sx = v => padL + ((v - xMin) / (xMax - xMin)) * plotW;

    // Grid lines
    ctx.strokeStyle = '#27211a'; ctx.lineWidth = 1;
    const yStep = (yMax - yMin) > 4.5 ? 1.0 : 0.5;
    for(let yv = Math.ceil(yMin/yStep)*yStep; yv <= yMax + 1e-6; yv += yStep){{
      const py = sy(yv);
      ctx.beginPath(); ctx.moveTo(padL, py); ctx.lineTo(W - 22, py); ctx.stroke();
      ctx.fillStyle = '#a1977f'; ctx.font = '11px "IBM Plex Mono", monospace'; ctx.textAlign = 'right';
      ctx.fillText(yv.toFixed(1), padL - 8, py + 4);
    }}

    const xTicks = xmode === 'potency' ? [0, 0.5, 1, 1.5, 2, 2.5, 3] : (xmode === 'oil' ? [0, 1, 2, 3, 4] : [4, 6, 8, 10, 12, 14, 16, 18]);
    xTicks.forEach(xv => {{
      const px = sx(xv);
      if(px < padL || px > padL + plotW) return;
      ctx.strokeStyle = '#27211a'; ctx.beginPath(); ctx.moveTo(px, padT); ctx.lineTo(px, padT + plotH); ctx.stroke();
      ctx.fillStyle = '#a1977f'; ctx.font = '11px "IBM Plex Mono", monospace'; ctx.textAlign = 'center';
      ctx.fillText(String(xv), px, padT + plotH + 17);
    }});

    // Axes
    ctx.strokeStyle = '#4c4337'; ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(padL, padT); ctx.lineTo(padL, padT + plotH); ctx.lineTo(padL + plotW, padT + plotH); ctx.stroke();

    // Axis titles
    ctx.fillStyle = '#d9d0be'; ctx.font = '12px system-ui, sans-serif'; ctx.textAlign = 'center';
    ctx.fillText(xLabel, padL + plotW / 2, H - 10);
    ctx.save(); ctx.translate(16, padT + plotH / 2); ctx.rotate(-Math.PI/2);
    ctx.fillText('Predicted binding  −ΔG (kcal/mol)', 0, 0); ctx.restore();

    // Anaesthetic OLS trend line
    const anPts = D.molecules.filter(m => m.mol_class === 'anaesthetic').map(m => [xFn(m), bMap[m.mol_id]]);
    const [a0, a1] = ols(anPts.map(p=>p[0]), anPts.map(p=>p[1]));
    ctx.save();
    ctx.strokeStyle = '#cfa544'; ctx.globalAlpha = 0.65; ctx.setLineDash([5, 4]); ctx.lineWidth = 1.6;
    ctx.beginPath();
    ctx.moveTo(sx(xMin + 0.05*(xMax-xMin)), sy(a0 + a1*(xMin + 0.05*(xMax-xMin))));
    ctx.lineTo(sx(xMax - 0.03*(xMax-xMin)), sy(a0 + a1*(xMax - 0.03*(xMax-xMin))));
    ctx.stroke();
    ctx.restore();

    // Strip panel for non-immobilizers in potency mode
    const stripX0 = padL + plotW + gapStrip;
    if(xmode === 'potency'){{
      ctx.fillStyle = '#1a1612';
      ctx.fillRect(stripX0, padT, stripW, plotH);
      ctx.strokeStyle = '#3c352a'; ctx.strokeRect(stripX0, padT, stripW, plotH);
      ctx.fillStyle = '#7fb39d'; ctx.font = '10px "IBM Plex Mono", monospace'; ctx.textAlign = 'center';
      ctx.fillText('NON-ANAESTH.', stripX0 + stripW/2, padT - 8);
      ctx.fillStyle = '#a1977f'; ctx.font = '10px system-ui, sans-serif';
      ctx.fillText('(no MAC)', stripX0 + stripW/2, padT + plotH + 17);
      // Median lines
      const medAn = st.median_B_anaes, medNon = st.median_B_non;
      ctx.strokeStyle = '#cfa544'; ctx.setLineDash([3,3]); ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(stripX0 + 4, sy(medAn)); ctx.lineTo(stripX0 + stripW - 4, sy(medAn)); ctx.stroke();
      ctx.strokeStyle = '#7fb39d'; ctx.setLineDash([]); ctx.lineWidth = 1.6;
      ctx.beginPath(); ctx.moveTo(stripX0 + 10, sy(medNon)); ctx.lineTo(stripX0 + stripW - 10, sy(medNon)); ctx.stroke();
    }}

    // Plot points
    hitPts = [];
    const nonMols = D.molecules.filter(m => m.mol_class !== 'anaesthetic');
    D.molecules.forEach((m, idx) => {{
      const bVal = bMap[m.mol_id];
      const py = sy(bVal);
      let px = null;
      if(m.mol_class === 'anaesthetic'){{
        px = sx(xFn(m));
      }} else {{
        if(xmode === 'potency'){{
          const ni = nonMols.indexOf(m);
          const frac = (ni + 0.8) / (nonMols.length + 0.6);
          px = stripX0 + 12 + frac * (stripW - 24);
        }} else {{
          const xv = xFn(m);
          if(xv === null) return;
          px = sx(xv);
          // Residual stem from anaesthetic trendline
          const yPred = a0 + a1 * xv;
          ctx.strokeStyle = m.mol_class === 'non_immobilizer' ? 'rgba(127,179,157,0.55)' : 'rgba(154,165,179,0.45)';
          ctx.lineWidth = 1.2;
          ctx.beginPath(); ctx.moveTo(px, sy(yPred)); ctx.lineTo(px, py); ctx.stroke();
        }}
      }}
      if(px === null) return;

      // Draw distinct shape per class
      ctx.save();
      if(m.subset === 'clinical'){{
        ctx.fillStyle = '#cfa544'; ctx.strokeStyle = '#14110e'; ctx.lineWidth = 1;
        ctx.beginPath(); ctx.arc(px, py, 5.2, 0, Math.PI*2); ctx.fill(); ctx.stroke();
      }} else if(m.subset === 'fang1996'){{
        ctx.fillStyle = '#d08a5c'; ctx.strokeStyle = '#14110e'; ctx.lineWidth = 1;
        ctx.beginPath(); ctx.moveTo(px, py - 5.8); ctx.lineTo(px + 5.2, py + 4.4); ctx.lineTo(px - 5.2, py + 4.4); ctx.closePath();
        ctx.fill(); ctx.stroke();
      }} else if(m.mol_class === 'non_immobilizer'){{
        ctx.fillStyle = '#14110e'; ctx.strokeStyle = '#7fb39d'; ctx.lineWidth = 2;
        ctx.beginPath(); ctx.moveTo(px, py - 6.2); ctx.lineTo(px + 6.2, py); ctx.lineTo(px, py + 6.2); ctx.lineTo(px - 6.2, py); ctx.closePath();
        ctx.fill(); ctx.stroke();
      }} else {{
        ctx.fillStyle = '#14110e'; ctx.strokeStyle = '#9aa5b3'; ctx.lineWidth = 1.8;
        ctx.fillRect(px - 4.5, py - 4.5, 9, 9); ctx.strokeRect(px - 4.5, py - 4.5, 9, 9);
      }}
      ctx.restore();

      // Label key landmarks cleanly
      const keyLabels = new Set(['methoxyflurane','halothane','isoflurane','desflurane','nitrous_oxide','o_xylene','TFMB','F6','F8','cyclooctane','perfluoropentane']);
      if(keyLabels.has(m.mol_id)){{
        ctx.fillStyle = m.mol_class === 'non_immobilizer' ? '#7fb39d' : '#d9d0be';
        ctx.font = '10px system-ui, sans-serif';
        ctx.textAlign = px > W - 110 ? 'right' : 'left';
        const dx = px > W - 110 ? -8 : 8;
        const shortName = m.mol_id === 'nitrous_oxide' ? 'N₂O' : (m.mol_id === 'methoxyflurane' ? 'Methoxyfl.' : (m.mol_id === 'perfluoropentane' ? 'C₅F₁₂' : m.name.split(' ')[0]));
        ctx.fillText(shortName, px + dx, py + 3);
      }}
      const resid = xFn(m) !== null ? (bVal - (a0 + a1 * xFn(m))) : null;
      hitPts.push({{px, py, m, bVal, resid}});
    }});
  }}

  canvas.addEventListener('mousemove', e => {{
    const rect = canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left, my = e.clientY - rect.top;
    let best = null, bd = 14;
    for(const pt of hitPts){{
      const d = Math.hypot(pt.px - mx, pt.py - my);
      if(d < bd){{ bd = d; best = pt; }}
    }}
    if(!best){{ tip.style.display = 'none'; return; }}
    const m = best.m;
    const cls = m.mol_class === 'anaesthetic' ? (m.subset === 'clinical' ? 'Clinical volatile anaesthetic' : 'Experimental anaesthetic (Fang 1996)') : (m.mol_class === 'non_immobilizer' ? 'Confirmed non-immobilizer' : 'Convulsant (annotated)');
    let html = '<strong>' + m.name + '</strong><br><span class="am-mono">' + cls + '</span><br>';
    html += 'ΔG = <span class="am-mono">−' + best.bVal.toFixed(2) + ' kcal/mol</span><br>';
    if(m.mac_atm) html += 'MAC = <span class="am-mono">' + (m.mac_atm*100).toFixed(3) + '% atm</span> (−log₁₀ = ' + (-Math.log10(m.mac_atm)).toFixed(2) + ')<br>';
    if(m.oil_gas) html += 'λ_oil = <span class="am-mono">' + m.oil_gas + '</span> · ';
    html += 'Heavy atoms = <span class="am-mono">' + m.n_heavy + '</span> · MW = <span class="am-mono">' + m.mw + '</span>';
    if(best.resid !== null) html += '<br>Residual vs trend: <span class="am-mono">' + fmtS(best.resid) + ' kcal/mol</span>';
    tip.innerHTML = html;
    tip.style.display = 'block';
    const tx = Math.min(rect.width - 265, Math.max(8, mx + 14));
    const ty = Math.max(8, my - 40);
    tip.style.left = tx + 'px'; tip.style.top = ty + 'px';
  }});
  canvas.addEventListener('mouseleave', () => {{ tip.style.display = 'none'; }});
  window.addEventListener('resize', draw);
  draw();
}})();
</script>
</figure>
"""


def build_matrix_explorer(summary: Dict) -> str:
    payload = {
        "molecules": summary["molecules"],
        "targets": plain_targets(summary["target_meta"]),
        "targetOrder": list(summary["target_meta"].keys()),
        "scoring": {
            sf: {
                "best": summary["scoring"][sf]["b_best_matrix"],
                "single": summary["scoring"][sf]["b_single_matrix"],
                "statsBest": summary["scoring"][sf]["targets_best"],
                "statsSingle": summary["scoring"][sf]["targets_single"],
            }
            for sf in ("vina", "vinardo")
        },
    }
    data_json = json.dumps(payload, separators=(",", ":"))
    return f"""<figure class="am-plate" id="am-matrix-fig" aria-label="Target specificity scorecard and full 35-molecule by 8-protein docking matrix">
<style>{SHARED_PANEL_CSS}</style>
<div class="am-head">
  <div>
    <p class="am-kicker">Interactive Plate 2 · Eight-Protein Comparison &amp; Full Matrix</p>
    <p class="am-title">How tubulin compares with ion channels, soluble binders and negative controls</p>
  </div>
</div>
<div class="am-controls">
  <div class="am-group" id="am-m-sf">
    <span class="am-glabel">Scoring</span>
    <button type="button" class="am-btn is-on" data-v="vina">Vina</button>
    <button type="button" class="am-btn" data-v="vinardo">Vinardo</button>
  </div>
  <div class="am-group" id="am-m-pmode">
    <span class="am-glabel">Pocket</span>
    <button type="button" class="am-btn is-on" data-v="best">Best pocket</button>
    <button type="button" class="am-btn" data-v="single">Single pocket</button>
  </div>
  <div class="am-group" id="am-m-scale">
    <span class="am-glabel">Heatmap Scale</span>
    <button type="button" class="am-btn is-on" data-v="raw">Raw −ΔG (kcal/mol)</button>
    <button type="button" class="am-btn" data-v="zscore">Within-protein Z-score</button>
  </div>
</div>
<div class="am-stage">
  <canvas class="am-canvas" id="am-m-forest" height="270"></canvas>
</div>
<div class="am-stage" style="margin-top:.85rem;">
  <canvas class="am-canvas" id="am-m-heat" height="620"></canvas>
  <div class="am-tip" id="am-m-tip"></div>
</div>
<figcaption class="am-cap">Top: side-by-side scorecard across all 8 proteins showing raw potency Spearman ρ (with 95% bootstrap interval), size-adjusted partial ρ (controlling for heavy-atom count), and non-immobilizer ROC AUC (dashed line at 0.50 = chance; values below 0.50 mean non-anaesthetics score tighter than true anaesthetics). Bottom: complete 35-molecule × 8-protein docking matrix; switch to Within-protein Z-score to see that all eight proteins rank the same molecules similarly. Hover any cell for exact energies.</figcaption>
<script>
(function(){{
  const D = {data_json};
  let sf = 'vina', pmode = 'best', scale = 'raw';

  function bind(id, fn){{
    document.getElementById(id).querySelectorAll('button').forEach(b => {{
      b.addEventListener('click', () => {{
        fn(b.dataset.v);
        document.getElementById(id).querySelectorAll('button').forEach(x => x.classList.toggle('is-on', x === b));
        drawAll();
      }});
    }});
  }}
  bind('am-m-sf', v => sf = v);
  bind('am-m-pmode', v => pmode = v);
  bind('am-m-scale', v => scale = v);

  const cForest = document.getElementById('am-m-forest');
  const cHeat = document.getElementById('am-m-heat');
  const tip = document.getElementById('am-m-tip');
  let heatCells = [];

  const roleColor = {{
    test_primary: '#cfa544',
    test_replication: '#d08a5c',
    rival_channel: '#7fb39d',
    positive_control: '#9aa5b3',
    negative_control: '#877d6b'
  }};

  function drawForest(){{
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const W = cForest.parentElement.clientWidth || 720;
    const H = 270;
    cForest.width = Math.round(W * dpr); cForest.height = Math.round(H * dpr);
    cForest.style.height = H + 'px';
    const ctx = cForest.getContext('2d');
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.fillStyle = '#14110e'; ctx.fillRect(0, 0, W, H);

    const stats = (pmode === 'best' ? D.scoring[sf].statsBest : D.scoring[sf].statsSingle);
    const ids = D.targetOrder;
    const leftW = Math.min(155, W * 0.27);
    const colGap = 18;
    const avail = W - leftW - 20 - 2 * colGap;
    const colW = avail / 3;
    const cols = [
      {{ title: 'POTENCY ρ (95% CI)', x0: leftW, min: -0.4, max: 1.0, zero: 0 }},
      {{ title: 'PARTIAL ρ | SIZE', x0: leftW + colW + colGap, min: -0.6, max: 0.8, zero: 0 }},
      {{ title: 'NON-IMMOBILIZER AUC', x0: leftW + 2*(colW + colGap), min: 0.0, max: 1.0, zero: 0.5 }}
    ];

    const top = 34, rowH = (H - top - 28) / ids.length;
    cols.forEach(c => {{
      ctx.fillStyle = '#d9d0be'; ctx.font = '10px "IBM Plex Mono", monospace'; ctx.textAlign = 'center';
      ctx.fillText(c.title, c.x0 + colW/2, 18);
      const zx = c.x0 + ((c.zero - c.min)/(c.max - c.min)) * colW;
      ctx.strokeStyle = '#4c4337'; ctx.setLineDash([3,3]); ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(zx, top - 4); ctx.lineTo(zx, H - 24); ctx.stroke();
      ctx.setLineDash([]);
      // ticks
      [c.min, c.zero, c.max].forEach(tk => {{
        const tx = c.x0 + ((tk - c.min)/(c.max - c.min)) * colW;
        ctx.fillStyle = '#a1977f'; ctx.font = '10px "IBM Plex Mono", monospace';
        ctx.fillText(tk.toFixed(1), tx, H - 8);
      }});
    }});

    ids.forEach((tid, i) => {{
      const y = top + (i + 0.5) * rowH;
      const st = stats[tid];
      const meta = D.targets[tid];
      const col = roleColor[meta.role];
      if(i % 2 === 0){{
        ctx.fillStyle = 'rgba(255,255,255,0.02)';
        ctx.fillRect(0, top + i*rowH, W, rowH);
      }}
      ctx.fillStyle = meta.role.startsWith('test') ? '#f6f1e8' : '#d9d0be';
      ctx.font = (meta.role.startsWith('test') ? '600 ' : '400 ') + '12px system-ui, sans-serif';
      ctx.textAlign = 'right';
      ctx.fillText(meta.label, leftW - 12, y + 4);

      // Col 0: rho_pot + CI
      const c0 = cols[0];
      const sx0 = v => c0.x0 + ((Math.max(c0.min, Math.min(c0.max, v)) - c0.min)/(c0.max - c0.min)) * colW;
      ctx.strokeStyle = col; ctx.lineWidth = 2;
      ctx.beginPath(); ctx.moveTo(sx0(st.rho_pot_ci95[0]), y); ctx.lineTo(sx0(st.rho_pot_ci95[1]), y); ctx.stroke();
      ctx.fillStyle = col; ctx.beginPath(); ctx.arc(sx0(st.rho_pot), y, 4.5, 0, Math.PI*2); ctx.fill();
      ctx.fillStyle = '#a1977f'; ctx.font = '10px "IBM Plex Mono", monospace'; ctx.textAlign = 'left';
      ctx.fillText((st.rho_pot>=0?'+':'−')+Math.abs(st.rho_pot).toFixed(2), Math.min(c0.x0 + colW - 34, sx0(st.rho_pot_ci95[1]) + 5), y + 3.5);

      // Col 1: partial rho | heavy
      const c1 = cols[1];
      const sx1 = v => c1.x0 + ((Math.max(c1.min, Math.min(c1.max, v)) - c1.min)/(c1.max - c1.min)) * colW;
      const z1 = sx1(0), vx1 = sx1(st.rho_partial_heavy);
      ctx.fillStyle = col; ctx.globalAlpha = 0.78;
      ctx.fillRect(Math.min(z1, vx1), y - 5.5, Math.abs(vx1 - z1), 11);
      ctx.globalAlpha = 1;
      ctx.fillStyle = '#d9d0be'; ctx.font = '10px "IBM Plex Mono", monospace';
      ctx.textAlign = st.rho_partial_heavy >= 0 ? 'left' : 'right';
      ctx.fillText((st.rho_partial_heavy>=0?'+':'−')+Math.abs(st.rho_partial_heavy).toFixed(2), vx1 + (st.rho_partial_heavy>=0?5:-5), y + 3.5);

      // Col 2: AUC_sep
      const c2 = cols[2];
      const sx2 = v => c2.x0 + ((Math.max(c2.min, Math.min(c2.max, v)) - c2.min)/(c2.max - c2.min)) * colW;
      const z2 = sx2(0.5), vx2 = sx2(st.auc_sep);
      ctx.fillStyle = st.auc_sep >= 0.5 ? '#7fb39d' : '#d08a5c';
      ctx.globalAlpha = 0.8;
      ctx.fillRect(Math.min(z2, vx2), y - 5.5, Math.abs(vx2 - z2), 11);
      ctx.globalAlpha = 1;
      ctx.fillStyle = '#d9d0be'; ctx.font = '10px "IBM Plex Mono", monospace';
      ctx.textAlign = st.auc_sep >= 0.5 ? 'left' : 'right';
      ctx.fillText(st.auc_sep.toFixed(2), vx2 + (st.auc_sep>=0.5?5:-5), y + 3.5);
    }});
  }}

  function heatColor(t){{
    // t in [0, 1] -> warm obsidian (#1e1914) -> copper (#955730) -> bright ochre (#e2bc63)
    t = Math.max(0, Math.min(1, t));
    if(t < 0.5){{
      const u = t * 2;
      const r = Math.round(30 + u * (149 - 30));
      const g = Math.round(25 + u * (87 - 25));
      const b = Math.round(20 + u * (48 - 20));
      return `rgb(${{r}},${{g}},${{b}})`;
    }} else {{
      const u = (t - 0.5) * 2;
      const r = Math.round(149 + u * (226 - 149));
      const g = Math.round(87 + u * (188 - 87));
      const b = Math.round(48 + u * (99 - 48));
      return `rgb(${{r}},${{g}},${{b}})`;
    }}
  }}

  function drawHeat(){{
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const W = cHeat.parentElement.clientWidth || 720;
    const H = 620;
    cHeat.width = Math.round(W * dpr); cHeat.height = Math.round(H * dpr);
    cHeat.style.height = H + 'px';
    const ctx = cHeat.getContext('2d');
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.fillStyle = '#14110e'; ctx.fillRect(0, 0, W, H);

    const mat = (pmode === 'best' ? D.scoring[sf].best : D.scoring[sf].single);
    const ids = D.targetOrder;
    const mols = D.molecules;

    // Precompute per-column mean & sd for Z-score mode, plus global min/max for raw
    const colStats = {{}};
    let gMin = 99, gMax = -99;
    ids.forEach(tid => {{
      const vals = mols.map(m => mat[tid][m.mol_id]);
      const mu = vals.reduce((a,b)=>a+b,0)/vals.length;
      const sd = Math.sqrt(vals.reduce((a,b)=>a+(b-mu)*(b-mu),0)/vals.length) || 1;
      colStats[tid] = {{mu, sd}};
      vals.forEach(v => {{ if(v<gMin) gMin=v; if(v>gMax) gMax=v; }});
    }});

    const leftW = Math.min(185, W * 0.30);
    const topH = 44, botH = 26, rightP = 14;
    const cellW = (W - leftW - rightP) / ids.length;
    const cellH = (H - topH - botH) / mols.length;

    // Column headers
    ids.forEach((tid, ci) => {{
      const cx = leftW + (ci + 0.5) * cellW;
      const lbl = D.targets[tid].label.replace(' (1.8 Å)', '').replace(' (', '\\n(');
      const parts = lbl.split('\\n');
      ctx.fillStyle = D.targets[tid].role.startsWith('test') ? '#cfa544' : '#d9d0be';
      ctx.font = '10px "IBM Plex Mono", monospace'; ctx.textAlign = 'center';
      ctx.fillText(parts[0], cx, 18);
      if(parts[1]){{ ctx.fillStyle = '#a1977f'; ctx.fillText(parts[1], cx, 31); }}
    }});

    heatCells = [];
    mols.forEach((m, ri) => {{
      const y = topH + ri * cellH;
      // Group separator lines
      if(ri === 9 || ri === 27 || ri === 34){{
        ctx.strokeStyle = '#cfa544'; ctx.lineWidth = 1;
        ctx.beginPath(); ctx.moveTo(6, y); ctx.lineTo(W - rightP, y); ctx.stroke();
      }}
      ctx.fillStyle = m.mol_class === 'non_immobilizer' ? '#7fb39d' : (m.subset === 'clinical' ? '#f6f1e8' : '#b8ae99');
      ctx.font = '10.5px system-ui, sans-serif'; ctx.textAlign = 'right';
      const label = m.name.length > 26 ? m.mol_id : m.name;
      ctx.fillText(label, leftW - 8, y + cellH * 0.72);

      ids.forEach((tid, ci) => {{
        const x = leftW + ci * cellW;
        const val = mat[tid][m.mol_id];
        const z = (val - colStats[tid].mu) / colStats[tid].sd;
        const norm = scale === 'raw' ? (val - gMin) / (gMax - gMin) : (z + 2.2) / 4.4;
        ctx.fillStyle = heatColor(norm);
        ctx.fillRect(x + 1, y + 1, cellW - 2, cellH - 1.5);
        if(cellW > 46){{
          ctx.fillStyle = norm > 0.62 ? '#171310' : '#f6f1e8';
          ctx.font = '9.5px "IBM Plex Mono", monospace'; ctx.textAlign = 'center';
          ctx.fillText(scale === 'raw' ? val.toFixed(1) : (z>=0?'+':'−')+Math.abs(z).toFixed(1), x + cellW/2, y + cellH*0.72);
        }}
        heatCells.push({{x, y, w: cellW, h: cellH, m, tid, val, z}});
      }});
    }});

    // Scale footer
    ctx.fillStyle = '#a1977f'; ctx.font = '10.5px "IBM Plex Mono", monospace'; ctx.textAlign = 'left';
    ctx.fillText(scale === 'raw' ? `Colour scale: ${{gMin.toFixed(1)}} (dark) → ${{gMax.toFixed(1)}} kcal/mol (bright ochre)` : 'Colour scale: −2.2σ (dark) → +2.2σ (bright ochre) within each protein', leftW, H - 8);
  }}

  cHeat.addEventListener('mousemove', e => {{
    const rect = cHeat.getBoundingClientRect();
    const mx = e.clientX - rect.left, my = e.clientY - rect.top;
    const hit = heatCells.find(c => mx >= c.x && mx <= c.x + c.w && my >= c.y && my <= c.y + c.h);
    if(!hit){{ tip.style.display = 'none'; return; }}
    const m = hit.m;
    let html = '<strong>' + m.name + '</strong> → ' + D.targets[hit.tid].label + '<br>';
    html += 'ΔG = <span class="am-mono">−' + hit.val.toFixed(2) + ' kcal/mol</span> (Z = ' + (hit.z>=0?'+':'−') + Math.abs(hit.z).toFixed(2) + ')<br>';
    if(m.mac_atm) html += 'MAC = <span class="am-mono">' + (m.mac_atm*100).toFixed(3) + '% atm</span> · ';
    else html += '<span class="am-mono">' + (m.mol_class === 'non_immobilizer' ? 'Non-immobilizer' : 'Convulsant') + '</span> · ';
    html += 'N_heavy = <span class="am-mono">' + m.n_heavy + '</span>';
    tip.innerHTML = html;
    tip.style.display = 'block';
    tip.style.left = Math.min(rect.width - 265, Math.max(8, mx + 12)) + 'px';
    tip.style.top = Math.max(8, my - 46) + 'px';
  }});
  cHeat.addEventListener('mouseleave', () => {{ tip.style.display = 'none'; }});

  function drawAll(){{ drawForest(); drawHeat(); }}
  window.addEventListener('resize', drawAll);
  drawAll();
}})();
</script>
</figure>
"""


def build_pockets_3d(poses_3d: Dict, summary: Dict) -> str:
    mol_lookup = {m["mol_id"]: m for m in summary["molecules"]}
    payload = {
        "targets": poses_3d["targets"],
        "targetOrder": list(poses_3d["targets"].keys()),
        "molMeta": {
            mid: {
                "name": mol_lookup[mid]["name"],
                "mol_class": mol_lookup[mid]["mol_class"],
                "mac_atm": mol_lookup[mid]["mac_atm"],
                "n_heavy": mol_lookup[mid]["n_heavy"],
            }
            for mid in ("methoxyflurane", "halothane", "isoflurane", "o_xylene", "desflurane", "F6", "TFMB", "cyclooctane")
        },
    }
    data_json = json.dumps(payload, separators=(",", ":"))
    return f"""<figure class="am-plate" id="am-3d-fig" aria-label="Interactive 3D docked ligand and protein pocket explorer">
<style>{SHARED_PANEL_CSS}</style>
<div class="am-head">
  <div>
    <p class="am-kicker">Interactive Plate 3 · 3D Pocket Architecture (Real Docked Coordinates)</p>
    <p class="am-title">Drag to rotate the docked molecule inside each protein cavity</p>
  </div>
</div>
<div class="am-controls">
  <div class="am-group" id="am-3d-t">
    <span class="am-glabel">Pocket</span>
  </div>
</div>
<div class="am-controls">
  <div class="am-group" id="am-3d-l">
    <span class="am-glabel">Ligand</span>
  </div>
  <div class="am-group">
    <button type="button" class="am-btn is-on" id="am-3d-spin">Auto-rotate</button>
    <button type="button" class="am-btn" id="am-3d-reset">Reset view</button>
  </div>
</div>
<div class="am-stats" id="am-3d-stats"></div>
<div class="am-stage">
  <canvas class="am-canvas" id="am-3d-canvas" height="400" style="cursor:grab;"></canvas>
</div>
<div class="am-legend">
  <span class="am-leg-item"><svg width="12" height="12"><circle cx="6" cy="6" r="4.5" fill="#cfa544"/></svg> Aromatic pocket residues (Phe, Tyr, Trp, His)</span>
  <span class="am-leg-item"><svg width="12" height="12"><circle cx="6" cy="6" r="4.5" fill="#9aa5b3"/></svg> Hydrophobic residues (Leu, Ile, Val, Ala, Met, Pro, Cys)</span>
  <span class="am-leg-item"><svg width="12" height="12"><circle cx="6" cy="6" r="4.5" fill="#7fb39d"/></svg> Docked ligand fluorine (F) · <span style="color:#d08a5c;">Cl/Br</span> · <span style="color:#f6f1e8;">C</span></span>
</div>
<figcaption class="am-cap">Every atom position is taken directly from AutoDock Vina v1.2.5 MODEL 1 and the RCSB PDB crystal structure (residues within 8.5 Å of the pocket centre). Compare how a true clinical anaesthetic (such as halothane or isoflurane) and a Meyer–Overton non-immobilizer (such as TFMB or F6) pack into the same hydrophobic pocket on tubulin, GABA_A, GLIC, albumin and luciferase.</figcaption>
<script>
(function(){{
  const D = {data_json};
  let curT = 'tubulin_1jff', curL = 'TFMB';
  let yaw = 0.55, pitch = 0.28, spinning = true, dragging = false, lx = 0, ly = 0;

  const tBox = document.getElementById('am-3d-t');
  D.targetOrder.forEach(tid => {{
    const b = document.createElement('button');
    b.type = 'button'; b.className = 'am-btn' + (tid === curT ? ' is-on' : '');
    b.dataset.v = tid; b.textContent = D.targets[tid].label;
    b.addEventListener('click', () => {{ curT = tid; sync(); render(); }});
    tBox.appendChild(b);
  }});

  const lOrder = ['methoxyflurane','halothane','isoflurane','o_xylene','desflurane','F6','TFMB','cyclooctane'];
  const lBox = document.getElementById('am-3d-l');
  lOrder.forEach(lid => {{
    const b = document.createElement('button');
    b.type = 'button'; b.className = 'am-btn' + (lid === curL ? ' is-on' : '');
    b.dataset.v = lid;
    const isNon = D.molMeta[lid].mol_class === 'non_immobilizer';
    b.textContent = (isNon ? '◇ ' : '● ') + D.molMeta[lid].name.split(' ')[0];
    b.addEventListener('click', () => {{ curL = lid; sync(); render(); }});
    lBox.appendChild(b);
  }});

  const spinBtn = document.getElementById('am-3d-spin');
  spinBtn.addEventListener('click', () => {{ spinning = !spinning; spinBtn.classList.toggle('is-on', spinning); }});
  document.getElementById('am-3d-reset').addEventListener('click', () => {{ yaw = 0.55; pitch = 0.28; render(); }});

  function sync(){{
    tBox.querySelectorAll('button').forEach(b => b.classList.toggle('is-on', b.dataset.v === curT));
    lBox.querySelectorAll('button').forEach(b => b.classList.toggle('is-on', b.dataset.v === curL));
  }}

  const canvas = document.getElementById('am-3d-canvas');
  canvas.addEventListener('pointerdown', e => {{ dragging = true; spinning = false; spinBtn.classList.remove('is-on'); lx = e.clientX; ly = e.clientY; canvas.setPointerCapture(e.pointerId); canvas.style.cursor='grabbing'; }});
  canvas.addEventListener('pointermove', e => {{ if(!dragging) return; yaw += (e.clientX - lx)*0.009; pitch = Math.max(-1.4, Math.min(1.4, pitch + (e.clientY - ly)*0.009)); lx = e.clientX; ly = e.clientY; render(); }});
  canvas.addEventListener('pointerup', () => {{ dragging = false; canvas.style.cursor='grab'; }});

  const elemCol = {{C:'#f6f1e8', A:'#f6f1e8', F:'#7fb39d', Cl:'#cfa544', Br:'#d08a5c', O:'#e06b50', N:'#8cb8d9'}};
  const resCol = {{aromatic:'#cfa544', hydrophobic:'#9aa5b3', polar:'#6e665a', charged:'#826250'}};

  function project(x, y, z, cx, cy, scale){{
    const cyw = Math.cos(yaw), syw = Math.sin(yaw);
    const cpi = Math.cos(pitch), spi = Math.sin(pitch);
    const x1 = x * cyw - z * syw;
    const z1 = x * syw + z * cyw;
    const y2 = y * cpi - z1 * spi;
    const z2 = y * spi + z1 * cpi;
    const persp = 28 / (28 + z2);
    return {{ sx: cx + x1 * scale * persp, sy: cy - y2 * scale * persp, z: z2, p: persp }};
  }}

  function render(){{
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const W = canvas.parentElement.clientWidth || 720;
    const H = 400;
    canvas.width = Math.round(W * dpr); canvas.height = Math.round(H * dpr);
    canvas.style.height = H + 'px';
    const ctx = canvas.getContext('2d');
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.fillStyle = '#14110e'; ctx.fillRect(0, 0, W, H);

    const T = D.targets[curT];
    const L = T.ligands[curL];
    const M = D.molMeta[curL];
    const c = T.center;

    // Center camera on ligand centroid for clear inspection
    const lx0 = L.atoms.reduce((s,a)=>s+a.x,0)/L.atoms.length;
    const ly0 = L.atoms.reduce((s,a)=>s+a.y,0)/L.atoms.length;
    const lz0 = L.atoms.reduce((s,a)=>s+a.z,0)/L.atoms.length;

    const nearRes = T.pocket_residues.map(r => ({{
      ...r,
      dist: Math.hypot(r.x - lx0, r.y - ly0, r.z - lz0)
    }})).filter(r => r.dist <= 9.5).sort((a,b) => a.dist - b.dist);

    const nArom = nearRes.filter(r => r.kind === 'aromatic' && r.dist <= 6.5).length;
    const nHyd = nearRes.filter(r => (r.kind === 'hydrophobic' || r.kind === 'aromatic') && r.dist <= 6.5).length;
    const closest = nearRes[0] ? `${{nearRes[0].resn}}${{nearRes[0].resi}} (${{nearRes[0].dist.toFixed(1)}} Å)` : '—';

    document.getElementById('am-3d-stats').innerHTML =
      '<div class="am-stat"><p class="am-stat-k">Docked Affinity (Vina)</p><p class="am-stat-v">' + L.dG.toFixed(2) + ' kcal/mol</p><p class="am-stat-s">' + T.label + ' · ' + T.site_id + '</p></div>' +
      '<div class="am-stat"><p class="am-stat-k">Ligand Class</p><p class="am-stat-v">' + (M.mol_class === 'non_immobilizer' ? 'Non-immobilizer' : 'Anaesthetic') + '</p><p class="am-stat-s">' + (M.mac_atm ? 'MAC = ' + (M.mac_atm*100).toFixed(2) + '% atm' : 'No anaesthesia in vivo') + '</p></div>' +
      '<div class="am-stat"><p class="am-stat-k">Nonpolar Contacts ≤6.5 Å</p><p class="am-stat-v">' + nHyd + ' residues</p><p class="am-stat-s">' + nArom + ' aromatic (Phe/Tyr/Trp/His)</p></div>' +
      '<div class="am-stat"><p class="am-stat-k">Nearest Residue</p><p class="am-stat-v">' + closest + '</p><p class="am-stat-s">PDB ' + T.pdb_id + '</p></div>';

    const cx = W / 2, cy = H / 2, sc = Math.min(W, H) / 18.5;

    // Subtle pocket boundary ring
    ctx.strokeStyle = 'rgba(208,138,92,0.16)'; ctx.lineWidth = 1; ctx.setLineDash([4,4]);
    ctx.beginPath(); ctx.arc(cx, cy, sc * 7.2, 0, Math.PI*2); ctx.stroke();
    ctx.setLineDash([]);

    // Project ligand atoms & infer covalent bonds (<= 2.05 A)
    const pAtoms = L.atoms.map(a => ({{ ...a, pr: project(a.x - lx0, a.y - ly0, a.z - lz0, cx, cy, sc) }}));
    const drawList = [];

    nearRes.forEach(r => {{
      const pr = project(r.x - lx0, r.y - ly0, r.z - lz0, cx, cy, sc);
      drawList.push({{ kind: 'res', z: pr.z, pr, r }});
    }});
    for(let i=0;i<pAtoms.length;i++){{
      for(let j=i+1;j<pAtoms.length;j++){{
        const d = Math.hypot(pAtoms[i].x-pAtoms[j].x, pAtoms[i].y-pAtoms[j].y, pAtoms[i].z-pAtoms[j].z);
        if(d <= 2.1){{
          drawList.push({{ kind: 'bond', z: (pAtoms[i].pr.z + pAtoms[j].pr.z)/2, a: pAtoms[i], b: pAtoms[j] }});
        }}
      }}
    }}
    pAtoms.forEach(a => drawList.push({{ kind: 'atom', z: a.pr.z, a }}));
    drawList.sort((u,v) => v.z - u.z); // far to near

    drawList.forEach(item => {{
      if(item.kind === 'res'){{
        const {{pr, r}} = item;
        const alpha = Math.max(0.22, Math.min(0.9, 0.95 - (pr.z + 8)/22));
        const rad = Math.max(3.2, (r.kind === 'aromatic' ? 7.2 : 5.4) * pr.p);
        ctx.save();
        ctx.globalAlpha = alpha;
        ctx.fillStyle = resCol[r.kind] || '#6e665a';
        ctx.beginPath(); ctx.arc(pr.sx, pr.sy, rad, 0, Math.PI*2); ctx.fill();
        if(r.dist <= 6.2 || r.kind === 'aromatic'){{
          ctx.fillStyle = r.kind === 'aromatic' ? '#e8c97a' : '#b8ae99';
          ctx.font = '10px "IBM Plex Mono", monospace';
          ctx.fillText(r.resn + r.resi, pr.sx + rad + 3, pr.sy + 3);
        }}
        ctx.restore();
      }} else if(item.kind === 'bond'){{
        ctx.strokeStyle = '#d9d0be'; ctx.lineWidth = Math.max(1.8, 3.0 * item.a.pr.p);
        ctx.beginPath(); ctx.moveTo(item.a.pr.sx, item.a.pr.sy); ctx.lineTo(item.b.pr.sx, item.b.pr.sy); ctx.stroke();
      }} else {{
        const a = item.a, pr = a.pr;
        const col = elemCol[a.elem] || elemCol[a.elem[0]] || '#f6f1e8';
        const rad = Math.max(5.5, (a.elem === 'Br' || a.elem === 'Cl' ? 9.5 : 7.5) * pr.p);
        ctx.fillStyle = col; ctx.strokeStyle = '#14110e'; ctx.lineWidth = 1.4;
        ctx.beginPath(); ctx.arc(pr.sx, pr.sy, rad, 0, Math.PI*2); ctx.fill(); ctx.stroke();
        ctx.fillStyle = '#14110e'; ctx.font = 'bold 9px "IBM Plex Mono", monospace'; ctx.textAlign = 'center';
        ctx.fillText(a.elem === 'A' ? 'C' : a.elem, pr.sx, pr.sy + 3);
      }}
    }});
  }}

  function tick(){{
    if(spinning && !dragging){{ yaw += 0.0055; render(); }}
    requestAnimationFrame(tick);
  }}
  window.addEventListener('resize', render);
  render();
  requestAnimationFrame(tick);
}})();
</script>
</figure>
"""


def main() -> None:
    summary = json.loads((RESULTS / "summary.json").read_text())
    poses_3d = json.loads((RESULTS / "poses_3d.json").read_text())
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    (OUT_DIR / "tiles.html").write_text(build_tiles(summary))
    (OUT_DIR / "verdict.html").write_text(build_verdict(summary))
    (OUT_DIR / "potency.html").write_text(build_potency_explorer(summary))
    (OUT_DIR / "matrix.html").write_text(build_matrix_explorer(summary))
    (OUT_DIR / "pockets.html").write_text(build_pockets_3d(poses_3d, summary))

    print(f"Wrote 5 figures to {OUT_DIR}:")
    for p in sorted(OUT_DIR.glob("*.html")):
        print(f"  {p.name:16s} {p.stat().st_size:7d} bytes")


if __name__ == "__main__":
    main()
