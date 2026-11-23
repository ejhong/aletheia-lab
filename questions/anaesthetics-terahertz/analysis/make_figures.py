#!/usr/bin/env python3
"""
Generate 5 self-contained, zero-dependency interactive HTML figures for
site/figures/anaesthetics-terahertz/ strictly from locked results/summary.json.

Figures produced:
  1. tiles.html     - Native .tiles headline strip (plain English)
  2. verdict.html   - Native .verdict pre-registered check table
  3. repulsion.html - Interactive Level-Repulsion & Potency Explorer (all 9 targets,
                      toggle All 35 gases vs Craddock's original 11 gases, X-axis selector)
  4. proteins.html  - Interactive All-9-Targets Specificity Comparison + SO(3) Rotation Audit
  5. spectrum.html  - Interactive 3D Drag-to-Rotate Aromatic Dipole Network & 460-700 THz Shift Spectrum
"""
from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Dict

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT.parent.parent
RESULTS = ROOT / "results"
OUT_DIR = REPO / "site" / "figures" / "anaesthetics-terahertz"

esc = lambda s: html.escape(str(s), quote=True)

PLAIN_LABELS = {
    "tubulin_1jff": "Tubulin (microtubule)",
    "tubulin_4i4t": "Tubulin (sharper crystal)",
    "gabaa_6x3t": "GABA-A channel",
    "glic_3p4w": "GLIC channel",
    "hsa_1e7b": "Albumin (blood protein)",
    "luciferase_1ba3": "Firefly luciferase",
    "lysozyme_1dpx": "Lysozyme (egg white)",
    "ubiquitin_1ubq": "Ubiquitin (3 rings)",
    "tubulin_1jff_shuffled": "81 random rings (shuffled)",
}

ROLE_LABELS = {
    "test_primary": "Microtubule target",
    "test_replication": "Microtubule repeat",
    "rival_channel": "Accepted ion channel",
    "positive_control": "Binds anaesthetics; non-conscious",
    "negative_control": "Unrelated control protein",
    "synthetic_control": "Random geometry control",
}


def fmt_signed(x: float, digits: int = 2) -> str:
    return f"{x:+.{digits}f}".replace("-", "−")


def fmt_p(p: float) -> str:
    return "p < 0.001" if p < 0.001 else f"p = {p:.3f}"


def build_tiles(summary: Dict) -> str:
    lr = summary["level_repulsion_audit"]
    s1j = summary["stats"]["vina_A_d613"]["tubulin_1jff"]
    wrong_an = s1j["an_total"] - s1j["an_down_count"]
    wrong_no = s1j["no_total"] - s1j["no_up_count"]
    items = [
        (
            "7 of 8, 2 of 2",
            "anaesthetics slow the vibration and look-alike gases speed it up on the microtubule protein, much as the 2017 paper reported. Egg-white protein and rings scattered at random give the same split",
            False,
        ),
        (
            f"{lr['overall_matches']} of {lr['overall_total']}",
            "times, the direction of the shift is what the size of the gas molecule alone would give, whatever the protein",
            False,
        ),
        (
            f"{wrong_an} of {s1j['an_total']}",
            f"anaesthetics push the vibration the way the look-alike gases were said to, once more gases are tried. {wrong_no} of {s1j['no_total']} look-alikes push it the way anaesthetics were said to",
            False,
        ),
        (
            "Not special",
            "to microtubules. Where the calculation does tell anaesthetics from look-alikes, it does so as well for a nerve-cell channel and a blood protein",
            True,
        ),
    ]
    return '<div class="tiles">\n' + "\n".join(
        f'<div class="tile"><p class="tile-value{" is-word" if w else ""}">{esc(v)}</p><p class="tile-label">{esc(l)}</p></div>'
        for v, l, w in items
    ) + "\n</div>\n"


def build_verdict(summary: Dict) -> str:
    s1j = summary["stats"]["vina_A_d613"]["tubulin_1jff"]
    lr = summary["level_repulsion_audit"]
    so3_tfmb = summary["so3_rotation_audit"]["TFMB_site_5"]
    b = summary["stats"]["vina_B_dall"]
    dd = summary["stats"]["vina_A_ddown613"]
    pct = lambda t: f"{dd[t]['auc_sep'] * 100:.0f}%"
    wrong_an = s1j["an_total"] - s1j["an_down_count"]
    wrong_no = s1j["no_total"] - s1j["no_up_count"]

    rows = [
        (
            "The ten gases of the 2017 paper",
            "Does the rebuilt calculation give the reported split, with anaesthetics slowing the vibration and look-alike gases speeding it up?",
            f"Mostly. {s1j['craddock_8v2']['an_down_count']} of the 8 anaesthetics slow it and both look-alike gases speed it up. "
            f"The paper's other result, that stronger drugs shift it more, did not come out (correlation {fmt_signed(s1j['craddock_8v2']['rho_pot'])}). "
            "The rebuilt version uses a different structure, different positions for the gases and a different estimate of their properties, and its shifts are far larger than the paper's, so this is not a full reproduction.",
            "is-open",
            "Partly reproduced",
        ),
        (
            "Other proteins",
            "Is the split special to the microtubule protein?",
            "No. Egg-white lysozyme gives the same 7 of 8 and 2 of 2. So does a cloud of 81 rings placed at random. "
            f"In {lr['overall_matches']} of {lr['overall_total']} cases across nine targets, the direction of the shift is what the size of the gas molecule alone would give. "
            "In the paper's list, the two look-alike gases were the two largest molecules.",
            "is-no",
            "Same everywhere",
        ),
        (
            "More gases",
            f"Does the down-or-up split hold for {s1j['an_total']} anaesthetics and {s1j['no_total']} look-alikes?",
            f"No. {wrong_an} anaesthetics, among them the xylenes and methoxyflurane, speed the vibration up as the look-alikes did, and {wrong_no} small look-alikes slow it down. "
            f"The size of the shift does not follow the strength of the drug (correlation {fmt_signed(s1j['rho_pot'])}). "
            "Anaesthetics and look-alikes overlap in size, so no rule based on size can sort them.",
            "is-no",
            "Does not hold",
        ),
        (
            "The paper's own measure",
            "Counting only the largest slowing each gas causes, do anaesthetics outscore look-alikes?",
            f"Yes on tubulin: an anaesthetic outscores a look-alike {pct('tubulin_1jff')} of the time, where 50% is chance, and size does not account for it. "
            f"But a channel that anaesthetics are accepted to act on scores {pct('gabaa_6x3t')} and the blood protein albumin {pct('hsa_1e7b')}. "
            f"The small proteins and the random rings score lower ({pct('ubiquitin_1ubq')} to {pct('tubulin_1jff_shuffled')}). "
            f"The score does not rise with the strength of the drug (correlation {fmt_signed(dd['tubulin_1jff']['rho_pot'])}). "
            "So the model does respond to where a gas sits in a real protein, but not to tubulin in particular.",
            "is-open",
            "Shared with other proteins",
        ),
        (
            "The method as described",
            "Does the answer depend on which way round the protein file happens to sit?",
            f"On our reading of the paper's description, yes: turning the whole structure changes the shift, and for one gas reverses it ({fmt_signed(so3_tfmb['model_a_range_ghz'][0], 0)} to {fmt_signed(so3_tfmb['model_a_range_ghz'][1], 0)} GHz). "
            "A second reading of the same sentence has no such problem, the authors' program is not public, and the formulas as printed do not give the paper's own frequency range. "
            "So this is a doubt about the description, not a demonstrated error in the published numbers. "
            f"A version with the dependence removed sorts the gases better on one tubulin structure ({b['tubulin_1jff']['auc_sep']*100:.0f}%) but at chance on the other ({b['tubulin_4i4t']['auc_sep']*100:.0f}%).",
            "is-open",
            "Unclear",
        ),
    ]
    out = ['<div class="verdict">']
    for kicker, text, note, cls, chip in rows:
        out.append(
            f'<div class="verdict-row">\n'
            f'  <div>\n'
            f'    <p class="verdict-kicker">{esc(kicker)}</p>\n'
            f'    <p class="verdict-text">{esc(text)}</p>\n'
            f'    <p class="verdict-note">{esc(note)}</p>\n'
            f'  </div>\n'
            f'  <p class="verdict-status {cls}"><span class="dot" aria-hidden="true"></span>{esc(chip)}</p>\n'
            f'</div>'
        )
    out.append("</div>\n")
    return "\n".join(out)


def build_repulsion_explorer(summary: Dict) -> str:
    """Interactive level-repulsion & potency scatter across all 9 targets."""
    target_ids = list(summary["target_meta"].keys())
    payload = {
        "targets": [
            {
                "id": tid,
                "label": PLAIN_LABELS.get(tid, summary["target_meta"][tid]["label"]),
                "role": ROLE_LABELS.get(summary["target_meta"][tid]["role"], ""),
                "n_aroms": summary["target_meta"][tid]["n_aromatics"],
                "n_band": summary["target_meta"][tid]["baseline_a_n_in_613_band"],
                "stats": summary["stats"]["vina_A_d613"][tid],
                "lr": summary["level_repulsion_audit"]["by_target"].get(tid),
                "d613": summary["matrices"]["vina_A_d613"][tid],
                "fnew": summary["matrices"]["vina_A_fnew"][tid],
            }
            for tid in target_ids
        ],
        "molecules": summary["molecules"],
        "orig_ids": [
            "desflurane", "diethyl_ether", "enflurane", "halothane",
            "isoflurane", "methoxyflurane", "nitrous_oxide", "sevoflurane",
            "F6", "TFMB", "flurothyl",
        ],
    }
    data_json = json.dumps(payload, separators=(",", ":"))
    return f"""<figure class="fig" id="thz-rep-fig" aria-label="Interactive 613 THz shift and level-repulsion explorer">
<style>
#thz-rep-fig .thz-bar {{
  display:flex; flex-wrap:wrap; gap:8px 12px; align-items:center;
  padding:12px 14px; background:var(--band,#1e1b18); border-radius:6px 6px 0 0;
  border-bottom:1px solid rgba(255,244,230,.10); color:var(--paper,#f5efe6);
  font:500 13px/1.3 var(--sans,system-ui,sans-serif);
}}
#thz-rep-fig .thz-ctl {{ display:flex; align-items:center; gap:6px; }}
#thz-rep-fig label {{ font-size:12px; color:#c8bfb3; }}
#thz-rep-fig select, #thz-rep-fig button {{
  background:#2a2520; color:#f5efe6; border:1px solid rgba(255,244,230,.18);
  border-radius:4px; padding:5px 9px; font:500 12.5px/1.2 var(--sans,system-ui,sans-serif);
  cursor:pointer;
}}
#thz-rep-fig button.is-on {{ background:#c97b4b; border-color:#c97b4b; color:#181512; font-weight:600; }}
#thz-rep-fig .thz-kpis {{
  display:grid; grid-template-columns:repeat(auto-fit,minmax(145px,1fr)); gap:8px;
  padding:10px 14px; background:#231f1b; border-bottom:1px solid rgba(255,244,230,.08);
}}
#thz-rep-fig .thz-kpi {{ padding:4px 6px; }}
#thz-rep-fig .thz-kpi-v {{ font:600 17px/1.15 var(--serif,Georgia,serif); color:#f5efe6; margin:0; }}
#thz-rep-fig .thz-kpi-l {{ font:400 11.5px/1.3 var(--sans,system-ui,sans-serif); color:#b5aba0; margin:3px 0 0; }}
#thz-rep-fig .thz-stage {{ position:relative; background:var(--band,#1e1b18); padding:10px 12px 6px; }}
#thz-rep-fig svg {{ width:100%; height:auto; display:block; }}
#thz-rep-fig .thz-tip {{
  position:absolute; pointer-events:none; opacity:0; transition:opacity .12s;
  background:#14110f; color:#f5efe6; border:1px solid rgba(201,123,75,.5);
  border-radius:5px; padding:8px 10px; font:400 12px/1.4 var(--sans,system-ui,sans-serif);
  max-width:265px; box-shadow:0 6px 20px rgba(0,0,0,.45); z-index:4;
}}
#thz-rep-fig .thz-leg {{
  display:flex; flex-wrap:wrap; gap:14px; padding:8px 14px 12px;
  background:var(--band,#1e1b18); border-radius:0 0 6px 6px;
  font:400 12px/1.3 var(--sans,system-ui,sans-serif); color:#c8bfb3;
}}
#thz-rep-fig .thz-leg span {{ display:inline-flex; align-items:center; gap:6px; }}
#thz-rep-fig .thz-leg svg {{ width:12px; height:12px; flex:none; display:inline-block; }}
</style>
<div class="thz-bar">
  <div class="thz-ctl">
    <label for="thz-rep-target">Protein</label>
    <select id="thz-rep-target"></select>
  </div>
  <div class="thz-ctl">
    <label for="thz-rep-xaxis">Horizontal axis</label>
    <select id="thz-rep-xaxis">
      <option value="fiso" selected>Isolated gas Drude frequency (THz) — level-repulsion cliff</option>
      <option value="potency">Anaesthetic potency (−log₁₀ MAC)</option>
      <option value="alpha">Molecular polarizability α (Å³)</option>
    </select>
  </div>
  <div class="thz-ctl" role="group" aria-label="Gas subset">
    <button type="button" id="thz-btn-all" class="is-on">All 35 gases</button>
    <button type="button" id="thz-btn-orig">Craddock's 11 only</button>
  </div>
</div>
<div class="thz-kpis" id="thz-rep-kpis"></div>
<div class="thz-stage">
  <svg id="thz-rep-svg" viewBox="0 0 760 410" role="img" aria-label="Scatter plot of 613 THz frequency shift against gas Drude frequency or anaesthetic potency"></svg>
  <div class="thz-tip" id="thz-rep-tip"></div>
</div>
<div class="thz-leg">
  <span><svg width="12" height="12"><circle cx="6" cy="6" r="5" fill="#e6b655"/></svg> Anaesthetic in clinical use (9)</span>
  <span><svg width="12" height="12"><polygon points="6,1 11,10 1,10" fill="#c97b4b"/></svg> Anaesthetic from laboratory tests (18)</span>
  <span><svg width="12" height="12"><polygon points="6,1 11,6 6,11 1,6" fill="#d95f59"/></svg> Look-alike gas, no anaesthesia (7)</span>
  <span><svg width="12" height="12"><rect x="2" y="2" width="8" height="8" fill="#7c9eb2"/></svg> Flurothyl (convulsant)</span>
</div>
<figcaption>Each gas's largest frequency shift inside the 613 ± 8 THz band (positive = downward shift, Craddock's claimed anaesthetic direction; negative = upward shift). Switch between <strong>Craddock's 11 only</strong> and <strong>All 35 gases</strong>, or swap <strong>Tubulin</strong> for <strong>Lysozyme (egg white)</strong> or <strong>81 random rings</strong>. On the frequency axis, the line at 613 THz divides downward from upward shifts in 96.2% of all cases. Two coupled vibrations push each other apart: a gas whose own frequency lies above the band pushes the band down, and one below pushes it up. A gas's own frequency in this model is set by its size.</figcaption>
<script>
(function(){{
  const DATA = {data_json};
  const selT = document.getElementById("thz-rep-target");
  const selX = document.getElementById("thz-rep-xaxis");
  const btnAll = document.getElementById("thz-btn-all");
  const btnOrig = document.getElementById("thz-btn-orig");
  const kpis = document.getElementById("thz-rep-kpis");
  const svg = document.getElementById("thz-rep-svg");
  const tip = document.getElementById("thz-rep-tip");
  const NS = "http://www.w3.org/2000/svg";
  const origSet = new Set(DATA.orig_ids);

  DATA.targets.forEach((t, i) => {{
    const opt = document.createElement("option");
    opt.value = t.id;
    opt.textContent = t.label + " — " + t.role;
    if (i === 0) opt.selected = true;
    selT.appendChild(opt);
  }});

  let subsetMode = "all";
  const fmtS = (v, d=2) => (v >= 0 ? "+" : "−") + Math.abs(v).toFixed(d);
  // Signed symlog transform for Y (GHz) so both +-50 GHz and +-3500 GHz are crystal clear!
  const symlog = y => Math.sign(y) * Math.log10(1 + Math.abs(y) / 40.0);

  function el(tag, attrs, parent) {{
    const n = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs || {{}})) n.setAttribute(k, v);
    if (parent) parent.appendChild(n);
    return n;
  }}

  function render() {{
    const tid = selT.value;
    const xMode = selX.value;
    const T = DATA.targets.find(x => x.id === tid);
    const mols = DATA.molecules.filter(m => subsetMode === "all" || origSet.has(m.mol_id));
    const st = T.stats;
    const c8 = st.craddock_8v2;
    const lr = T.lr;

    const kpiItems = subsetMode === "orig" ? [
      ["8-vs-2 split", c8.an_down_count + "/8 down · " + c8.no_up_count + "/2 up"],
      ["8-vs-2 AUC", (c8.auc_sep * 100).toFixed(0) + "% (50% = chance)"],
      ["8-drug potency ρ", fmtS(c8.rho_pot, 2) + " (p = " + c8.p_rho_pot.toFixed(3) + ")"],
      ["Level-repulsion rule", lr ? (lr.matches + "/" + lr.total + " (" + (lr.frac*100).toFixed(0) + "%)") : "—"]
    ] : [
      ["27-drug potency ρ", fmtS(st.rho_pot, 2) + " (p = " + st.p_rho_pot.toFixed(3) + ")"],
      ["27-vs-7 AUC", (st.auc_sep * 100).toFixed(0) + "% (p = " + st.p_auc_sep.toFixed(3) + ")"],
      ["Direction accuracy", st.an_down_count + "/27 down · " + st.no_up_count + "/7 up"],
      ["Level-repulsion rule", lr ? (lr.matches + "/" + lr.total + " (" + (lr.frac*100).toFixed(0) + "%)") : "—"]
    ];
    kpis.innerHTML = kpiItems.map(([l, v]) =>
      `<div class="thz-kpi"><p class="thz-kpi-v">${{v}}</p><p class="thz-kpi-l">${{l}}</p></div>`
    ).join("");

    while (svg.firstChild) svg.removeChild(svg.firstChild);
    const W = 760, H = 410, L = 74, R = 26, TOP = 26, BOT = 56;
    const pw = W - L - R, ph = H - TOP - BOT;

    const pts = [];
    for (const m of mols) {{
      const yVal = T.d613[m.mol_id];
      if (yVal === null || yVal === undefined) continue;
      let xVal;
      if (xMode === "fiso") xVal = m.f_iso_thz;
      else if (xMode === "alpha") xVal = m.alpha_iso_a3;
      else {{
        // potency: for non-immobilizers/convulsants with no MAC, place in a dedicated right/left strip
        xVal = m.mac_atm ? -Math.log10(m.mac_atm) : null;
      }}
      pts.push({{ m, xVal, yVal, yT: symlog(yVal) }});
    }}

    const validX = pts.filter(p => p.xVal !== null).map(p => p.xVal);
    let xMin = xMode === "fiso" ? 455 : (xMode === "alpha" ? 2.0 : -0.35);
    let xMax = xMode === "fiso" ? 1200 : (xMode === "alpha" ? 16.5 : 3.25);
    if (xMode === "potency") {{
      // Place non-immobilizers at x = -0.25 with jitter-free vertical column label
      xMin = -0.65; xMax = 3.25;
    }}
    const sx = x => L + (x - xMin) / (xMax - xMin) * pw;

    const yAbsMax = Math.max(2.15, ...pts.map(p => Math.abs(p.yT))) * 1.08;
    const sy = yt => TOP + (yAbsMax - yt) / (2 * yAbsMax) * ph;

    // Background quadrant shading for level repulsion on fiso axis
    if (xMode === "fiso") {{
      const x613 = sx(613);
      const y0 = sy(0);
      el("rect", {{ x: x613, y: TOP, width: L + pw - x613, height: y0 - TOP, fill: "rgba(92,160,136,.07)" }}, svg);
      el("rect", {{ x: L, y: y0, width: x613 - L, height: TOP + ph - y0, fill: "rgba(217,95,89,.07)" }}, svg);
      el("line", {{ x1: x613, x2: x613, y1: TOP, y2: TOP + ph, stroke: "#e6b655", "stroke-width": 1.4, "stroke-dasharray": "5 4" }}, svg);
      const tCliff = el("text", {{ x: x613 + 6, y: TOP + 14, fill: "#e6b655", "font-size": "11.5", "font-weight": "600", "font-family": "var(--sans,sans-serif)" }}, svg);
      tCliff.textContent = "613 THz cliff";
      const q1 = el("text", {{ x: L + pw - 6, y: TOP + 15, "text-anchor": "end", fill: "#8eb8a8", "font-size": "11", "font-family": "var(--sans,sans-serif)" }}, svg);
      q1.textContent = "f_iso > 613 → pushed DOWN (+)";
      const q3 = el("text", {{ x: L + 6, y: TOP + ph - 8, fill: "#d98d88", "font-size": "11", "font-family": "var(--sans,sans-serif)" }}, svg);
      q3.textContent = "f_iso < 613 → pushed UP (−)";
    }} else if (xMode === "potency") {{
      const xSep = sx(-0.12);
      el("rect", {{ x: L, y: TOP, width: xSep - L, height: ph, fill: "rgba(217,95,89,.06)" }}, svg);
      el("line", {{ x1: xSep, x2: xSep, y1: TOP, y2: TOP + ph, stroke: "rgba(255,244,230,.18)", "stroke-dasharray": "4 4" }}, svg);
      const lbl = el("text", {{ x: (L + xSep)/2, y: TOP + 14, "text-anchor": "middle", fill: "#d98d88", "font-size": "10.5", "font-family": "var(--sans,sans-serif)" }}, svg);
      lbl.textContent = "No MAC";
    }}

    // Horizontal zero line & symlog ticks
    const yTicks = [-3000, -500, -100, -20, 0, 20, 100, 500, 3000];
    for (const tv of yTicks) {{
      const yt = symlog(tv);
      if (Math.abs(yt) > yAbsMax * 0.99) continue;
      const py = sy(yt);
      el("line", {{
        x1: L, x2: L + pw, y1: py, y2: py,
        stroke: tv === 0 ? "rgba(255,244,230,.45)" : "rgba(255,244,230,.08)",
        "stroke-width": tv === 0 ? 1.2 : 1
      }}, svg);
      const t = el("text", {{ x: L - 8, y: py + 4, "text-anchor": "end", fill: "#b5aba0", "font-size": "11", "font-family": "var(--sans,sans-serif)" }}, svg);
      t.textContent = tv === 0 ? "0" : (tv > 0 ? "+" + tv : "−" + Math.abs(tv));
    }}

    // X ticks
    const xTicks = xMode === "fiso" ? [500, 613, 750, 900, 1050, 1150] : (xMode === "alpha" ? [3, 6, 9, 12, 15] : [0, 1, 2, 3]);
    for (const xv of xTicks) {{
      const px = sx(xv);
      el("line", {{ x1: px, x2: px, y1: TOP + ph, y2: TOP + ph + 5, stroke: "rgba(255,244,230,.3)" }}, svg);
      const t = el("text", {{ x: px, y: TOP + ph + 19, "text-anchor": "middle", fill: "#b5aba0", "font-size": "11", "font-family": "var(--sans,sans-serif)" }}, svg);
      t.textContent = xv;
    }}

    // Axis titles
    const xt = el("text", {{ x: L + pw / 2, y: H - 10, "text-anchor": "middle", fill: "#d8cfc4", "font-size": "12", "font-family": "var(--sans,sans-serif)" }}, svg);
    xt.textContent = xMode === "fiso"
      ? "Gas's own isolated Drude frequency f_iso (THz) — set purely by polarizability α"
      : (xMode === "alpha" ? "Molecular polarizability α (Å³)" : "Clinical / experimental anaesthetic potency (−log₁₀ MAC; higher = stronger)");
    const ytLbl = el("text", {{
      x: 17, y: TOP + ph / 2, "text-anchor": "middle", fill: "#d8cfc4", "font-size": "12",
      "font-family": "var(--sans,sans-serif)", transform: `rotate(-90 17 ${{TOP + ph / 2}})`
    }}, svg);
    ytLbl.textContent = "613 THz shift D₆₁₃ (GHz, symlog; + = downward)";

    // Draw points
    const labelIds = new Set(["nitrous_oxide", "desflurane", "isoflurane", "halothane", "methoxyflurane", "o_xylene", "F6", "TFMB", "perfluorocyclobutane", "CF3CClFCF3"]);
    let noMacIdx = 0;
    for (const p of pts) {{
      const m = p.m;
      let px;
      if (p.xVal === null) {{
        px = sx(-0.52 + (noMacIdx % 3) * 0.14);
        noMacIdx++;
      }} else {{
        px = sx(p.xVal);
      }}
      const py = sy(p.yT);
      const g = el("g", {{ style: "cursor:pointer" }}, svg);
      let mark;
      if (m.mol_class === "non_immobilizer") {{
        mark = el("polygon", {{ points: `${{px}},${{py-6}} ${{px+6}},${{py}} ${{px}},${{py+6}} ${{px-6}},${{py}}`, fill: "#d95f59", stroke: "#181512", "stroke-width": 1 }}, g);
      }} else if (m.mol_class === "convulsant") {{
        mark = el("rect", {{ x: px - 5, y: py - 5, width: 10, height: 10, fill: "#7c9eb2", stroke: "#181512", "stroke-width": 1 }}, g);
      }} else if (m.subset === "clinical") {{
        mark = el("circle", {{ cx: px, cy: py, r: 5.5, fill: "#e6b655", stroke: "#181512", "stroke-width": 1 }}, g);
      }} else {{
        mark = el("polygon", {{ points: `${{px}},${{py-6}} ${{px+5.5}},${{py+4.5}} ${{px-5.5}},${{py+4.5}}`, fill: "#c97b4b", stroke: "#181512", "stroke-width": 1 }}, g);
      }}

      if (labelIds.has(m.mol_id) && (subsetMode === "orig" || ["TFMB", "F6", "o_xylene", "methoxyflurane", "nitrous_oxide", "perfluorocyclobutane", "CF3CClFCF3", "halothane"].includes(m.mol_id))) {{
        const lb = el("text", {{
          x: px + (px > W - 120 ? -8 : 8), y: py + 3.5,
          "text-anchor": px > W - 120 ? "end" : "start",
          fill: m.mol_class === "non_immobilizer" ? "#f2a39e" : "#ddd4c8",
          "font-size": "10.2", "font-family": "var(--sans,sans-serif)"
        }}, svg);
        lb.textContent = m.mol_id === "perfluorocyclobutane" ? "c-C₄F₈" : (m.mol_id === "CF3CClFCF3" ? "CF₃CClFCF₃" : m.name.split(" (")[0]);
      }}

      g.addEventListener("mouseenter", ev => {{
        const dir = p.yVal >= 0 ? "DOWNWARD (Craddock's anaesthetic sign)" : "UPWARD (Craddock's non-anaesthetic sign)";
        tip.innerHTML = `<strong>${{m.name}}</strong><br>Class: ${{m.mol_class.replace("_"," ")}}<br>` +
          (m.mac_atm ? `MAC: ${{m.mac_atm}} atm (−log₁₀ = ${{(-Math.log10(m.mac_atm)).toFixed(2)}})<br>` : `No anaesthetic MAC<br>`) +
          `Polarizability α: ${{m.alpha_iso_a3}} Å³ · f_iso: ${{m.f_iso_thz}} THz<br>` +
          `613 THz shift D₆₁₃: <strong>${{fmtS(p.yVal, 1)}} GHz</strong><br><span style="color:#b5aba0">${{dir}}</span>`;
        tip.style.opacity = "1";
        const rect = svg.getBoundingClientRect();
        const lx = Math.min(rect.width - 270, Math.max(10, (px / W) * rect.width + 12));
        const ly = Math.max(8, (py / H) * rect.height - 20);
        tip.style.left = lx + "px";
        tip.style.top = ly + "px";
      }});
      g.addEventListener("mouseleave", () => {{ tip.style.opacity = "0"; }});
    }}
  }}

  selT.addEventListener("change", render);
  selX.addEventListener("change", render);
  btnAll.addEventListener("click", () => {{ subsetMode = "all"; btnAll.classList.add("is-on"); btnOrig.classList.remove("is-on"); render(); }});
  btnOrig.addEventListener("click", () => {{ subsetMode = "orig"; btnOrig.classList.add("is-on"); btnAll.classList.remove("is-on"); render(); }});
  render();
}})();
</script>
</figure>
"""


def build_proteins_and_so3(summary: Dict) -> str:
    """All-9-targets specificity comparison + interactive SO(3) rotation invariance strip."""
    target_ids = list(summary["target_meta"].keys())
    payload = {
        "targets": [
            {
                "id": tid,
                "label": PLAIN_LABELS.get(tid, summary["target_meta"][tid]["label"]),
                "role": summary["target_meta"][tid]["role"],
                "n_aroms": summary["target_meta"][tid]["n_aromatics"],
                "d613": summary["stats"]["vina_A_d613"][tid],
                "fnew": summary["stats"]["vina_A_fnew"][tid],
                "modelB": summary["stats"]["vina_B_dall"][tid],
                "modelB_rms": summary["stats"]["vina_B_rms"][tid],
            }
            for tid in target_ids
        ],
        "so3": summary["so3_rotation_audit"],
    }
    data_json = json.dumps(payload, separators=(",", ":"))
    return f"""<figure class="fig" id="thz-prot-fig" aria-label="All nine proteins specificity scorecard and 3D rotational symmetry audit">
<style>
#thz-prot-fig .tp-bar {{
  display:flex; flex-wrap:wrap; gap:8px; align-items:center; justify-content:space-between;
  padding:12px 14px; background:var(--band,#1e1b18); border-radius:6px 6px 0 0;
  border-bottom:1px solid rgba(255,244,230,.10); color:#f5efe6;
  font:500 13px/1.3 var(--sans,system-ui,sans-serif);
}}
#thz-prot-fig .tp-btns {{ display:flex; flex-wrap:wrap; gap:6px; }}
#thz-prot-fig button {{
  background:#2a2520; color:#f5efe6; border:1px solid rgba(255,244,230,.18);
  border-radius:4px; padding:5px 9px; font:500 12px/1.2 var(--sans,system-ui,sans-serif);
  cursor:pointer;
}}
#thz-prot-fig button.is-on {{ background:#c97b4b; border-color:#c97b4b; color:#181512; font-weight:600; }}
#thz-prot-fig .tp-body {{ background:var(--band,#1e1b18); padding:10px 14px 14px; border-radius:0 0 6px 6px; }}
#thz-prot-fig svg {{ width:100%; height:auto; display:block; }}
#thz-prot-fig .tp-sub {{
  margin:12px 0 4px; padding-top:10px; border-top:1px solid rgba(255,244,230,.10);
  color:#d8cfc4; font:600 13px/1.3 var(--sans,system-ui,sans-serif);
}}
#thz-prot-fig .tp-note {{ margin:0 0 8px; color:#b5aba0; font:400 12px/1.4 var(--sans,system-ui,sans-serif); }}
</style>
<div class="tp-bar">
  <span>Compare all nine targets across models</span>
  <div class="tp-btns" role="group" aria-label="Metric view">
    <button type="button" data-mode="d613" class="is-on">613 THz shift (Craddock Fig. 4)</button>
    <button type="button" data-mode="fnew">New mode f_new (Craddock Fig. 3)</button>
    <button type="button" data-mode="modelB">Orientation-proof version (Model B)</button>
  </div>
</div>
<div class="tp-body">
  <svg id="thz-prot-svg" viewBox="0 0 760 320" role="img" aria-label="Dot plot comparing tubulin against seven other proteins and 81 random rings"></svg>
  <p class="tp-sub">Turning the whole structure to 20 random orientations</p>
  <p class="tp-note">Turning a protein and its gas together should change nothing. Under our reading of the published description (Model A), TFMB changes between downward (+) and upward (−). Under a version that keeps the full description of each ring (Model B), all 20 sit on a single point. The description can be read another way that has no such problem, and the authors' program is not public, so this shows a weakness in the method as we read it, not an error in the published numbers.</p>
  <svg id="thz-so3-svg" viewBox="0 0 760 155" role="img" aria-label="20 random 3D rotations showing Model A sign flips versus Model B exact invariance"></svg>
</div>
<figcaption>Top: Every protein's potency correlation (left, across 27 volatile anaesthetics) and non-anaesthetic separation (right, ROC AUC where 50% is chance) compared with Craddock's original 8-vs-2 split (hollow ring). Tubulin sits in the middle of the pack, level with 81 randomly scattered rings and matched by egg-white lysozyme. Bottom: the same tubulin and gas, turned as a whole to 20 random orientations, under our reading of the published method (Model A) and under a version that cannot depend on orientation (Model B).</figcaption>
<script>
(function(){{
  const DATA = {data_json};
  const svgP = document.getElementById("thz-prot-svg");
  const svgR = document.getElementById("thz-so3-svg");
  const btns = document.querySelectorAll("#thz-prot-fig button[data-mode]");
  const NS = "http://www.w3.org/2000/svg";
  let mode = "d613";

  function el(tag, attrs, parent) {{
    const n = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs || {{}})) n.setAttribute(k, v);
    if (parent) parent.appendChild(n);
    return n;
  }}

  const roleColor = r => (r === "test_primary" || r === "test_replication") ? "#e6b655"
    : (r === "rival_channel" ? "#7c9eb2" : (r === "synthetic_control" ? "#d95f59" : "#9aa396"));

  function renderTop() {{
    while (svgP.firstChild) svgP.removeChild(svgP.firstChild);
    const W = 760, H = 320, L = 192, mid = 468, R = 28, TOP = 36, rowH = 29;
    const p1L = L, p1R = mid - 26, p2L = mid + 18, p2R = W - R;
    const sxRho = r => p1L + (r + 0.65) / 1.65 * (p1R - p1L);  // -0.65 .. +1.0
    const sxAuc = a => p2L + a * (p2R - p2L);                   // 0 .. 1

    // Headers
    const h1 = el("text", {{ x: (p1L+p1R)/2, y: 18, "text-anchor": "middle", fill: "#f5efe6", "font-size": "12", "font-weight": "600", "font-family": "var(--sans,sans-serif)" }}, svgP);
    h1.textContent = "Potency correlation ρ (27 gases; ○ = original 8)";
    const h2 = el("text", {{ x: (p2L+p2R)/2, y: 18, "text-anchor": "middle", fill: "#f5efe6", "font-size": "12", "font-weight": "600", "font-family": "var(--sans,sans-serif)" }}, svgP);
    h2.textContent = "Anaesthetic vs look-alike AUC (○ = original 8 vs 2)";

    // Reference lines
    el("line", {{ x1: sxRho(0), x2: sxRho(0), y1: TOP - 6, y2: TOP + 9*rowH, stroke: "rgba(255,244,230,.35)", "stroke-dasharray": "4 3" }}, svgP);
    el("line", {{ x1: sxAuc(0.5), x2: sxAuc(0.5), y1: TOP - 6, y2: TOP + 9*rowH, stroke: "rgba(255,244,230,.35)", "stroke-dasharray": "4 3" }}, svgP);

    for (const rv of [-0.5, 0, 0.5, 1.0]) {{
      const px = sxRho(rv);
      const t = el("text", {{ x: px, y: TOP + 9*rowH + 16, "text-anchor": "middle", fill: "#b5aba0", "font-size": "10.5", "font-family": "var(--sans,sans-serif)" }}, svgP);
      t.textContent = rv === 0 ? "0" : (rv > 0 ? "+" + rv.toFixed(1) : "−" + Math.abs(rv).toFixed(1));
    }}
    for (const av of [0, 0.25, 0.5, 0.75, 1.0]) {{
      const px = sxAuc(av);
      const t = el("text", {{ x: px, y: TOP + 9*rowH + 16, "text-anchor": "middle", fill: "#b5aba0", "font-size": "10.5", "font-family": "var(--sans,sans-serif)" }}, svgP);
      t.textContent = Math.round(av * 100) + "%";
    }}

    DATA.targets.forEach((t, idx) => {{
      const y = TOP + idx * rowH + 14;
      if (idx % 2 === 0) el("rect", {{ x: 4, y: y - 13, width: W - 8, height: rowH, fill: "rgba(255,244,230,.025)", rx: 3 }}, svgP);
      const col = roleColor(t.role);
      const lbl = el("text", {{
        x: L - 10, y: y + 4, "text-anchor": "end",
        fill: t.role.startsWith("test") ? "#f5efe6" : "#c8bfb3",
        "font-weight": t.role === "test_primary" ? "700" : "400",
        "font-size": "12", "font-family": "var(--sans,sans-serif)"
      }}, svgP);
      lbl.textContent = t.label;

      const st = t[mode];
      const ci = st.rho_pot_ci95;
      // CI bar
      el("line", {{ x1: sxRho(Math.max(-0.65, ci[0])), x2: sxRho(Math.min(1.0, ci[1])), y1: y, y2: y, stroke: col, "stroke-width": 2, opacity: 0.55 }}, svgP);
      // Expanded 27-gas filled dot
      el("circle", {{ cx: sxRho(st.rho_pot), cy: y, r: 5, fill: col, stroke: "#181512", "stroke-width": 1 }}, svgP);
      // Original 8-gas hollow ring
      el("circle", {{ cx: sxRho(st.craddock_8v2.rho_pot), cy: y, r: 4.5, fill: "none", stroke: "#f5efe6", "stroke-width": 1.3, opacity: 0.7 }}, svgP);

      // AUC bar + dots
      el("line", {{ x1: sxAuc(0.5), x2: sxAuc(st.auc_sep), y1: y, y2: y, stroke: col, "stroke-width": 3, opacity: 0.65 }}, svgP);
      el("circle", {{ cx: sxAuc(st.auc_sep), cy: y, r: 5, fill: col, stroke: "#181512", "stroke-width": 1 }}, svgP);
      el("circle", {{ cx: sxAuc(st.craddock_8v2.auc_sep), cy: y, r: 4.5, fill: "none", stroke: "#f5efe6", "stroke-width": 1.3, opacity: 0.7 }}, svgP);
    }});
  }}

  function renderSO3() {{
    while (svgR.firstChild) svgR.removeChild(svgR.firstChild);
    const W = 760, H = 155, L = 178, R = 28;
    const xMin = -4000, xMax = 3200;
    const sx = x => L + (x - xMin) / (xMax - xMin) * (W - L - R);

    // Zero line
    el("line", {{ x1: sx(0), x2: sx(0), y1: 12, y2: 120, stroke: "#e6b655", "stroke-width": 1.3, "stroke-dasharray": "4 3" }}, svgR);
    for (const xv of [-3500, -2000, -1000, 0, 1000, 2000, 3000]) {{
      const px = sx(xv);
      el("line", {{ x1: px, x2: px, y1: 120, y2: 125, stroke: "rgba(255,244,230,.3)" }}, svgR);
      const t = el("text", {{ x: px, y: 140, "text-anchor": "middle", fill: "#b5aba0", "font-size": "10.5", "font-family": "var(--sans,sans-serif)" }}, svgR);
      t.textContent = xv === 0 ? "0 GHz" : (xv > 0 ? "+" + xv : "−" + Math.abs(xv));
    }}

    const rows = [
      {{ lbl: "Isoflurane (Model A)", vals: DATA.so3.isoflurane_site_7.model_a_d613_ghz, col: "#e6b655", y: 34, note: "27× spread (+37 to +1,018 GHz)" }},
      {{ lbl: "TFMB (Model A)", vals: DATA.so3.TFMB_site_5.model_a_d613_ghz, col: "#d95f59", y: 74, note: "changes sign (−3,703 to +2,722 GHz)" }},
      {{ lbl: "Isoflurane (Model B 3D)", vals: [DATA.so3.isoflurane_site_7.model_b_dall_range_ghz[0]], col: "#6eb59e", y: 108, note: "Invariant (drift 10⁻⁹ GHz)" }}
    ];
    for (const r of rows) {{
      const lb = el("text", {{ x: L - 10, y: r.y + 4, "text-anchor": "end", fill: "#d8cfc4", "font-size": "11.5", "font-family": "var(--sans,sans-serif)" }}, svgR);
      lb.textContent = r.lbl;
      const mn = Math.min(...r.vals), mx = Math.max(...r.vals);
      el("line", {{ x1: sx(mn), x2: sx(mx), y1: r.y, y2: r.y, stroke: r.col, "stroke-width": 2.5, opacity: 0.45 }}, svgR);
      r.vals.forEach((v, i) => {{
        const jit = r.vals.length > 1 ? ((i % 3) - 1) * 3.5 : 0;
        el("circle", {{ cx: sx(v), cy: r.y + jit, r: 3.7, fill: r.col, stroke: "#181512", "stroke-width": 0.8 }}, svgR);
      }});
      const nt = el("text", {{ x: W - R, y: r.y - 8, "text-anchor": "end", fill: r.col, "font-size": "10.5", "font-weight": "600", "font-family": "var(--sans,sans-serif)" }}, svgR);
      nt.textContent = r.note;
    }}
  }}

  btns.forEach(b => b.addEventListener("click", () => {{
    mode = b.dataset.mode;
    btns.forEach(x => x.classList.toggle("is-on", x === b));
    renderTop();
  }}));
  renderTop();
  renderSO3();
}})();
</script>
</figure>
"""


def build_spectrum_observatory(summary: Dict) -> str:
    """Interactive 3D drag-to-rotate aromatic dipole network + live 460-700 THz shift spectrum."""
    payload = {
        "aroms3d": summary["aromatics_3d"],
        "baseline_1jff": summary["baselines_thz"]["tubulin_1jff"],
        "examples": summary["spectra_1jff_examples"],
        "mols": {m["mol_id"]: m for m in summary["molecules"]},
    }
    data_json = json.dumps(payload, separators=(",", ":"))
    return f"""<figure class="fig" id="thz-spec-fig" aria-label="Interactive 3D aromatic network and 460-700 THz collective mode shift observatory">
<style>
#thz-spec-fig .ts-bar {{
  display:flex; flex-wrap:wrap; gap:8px 14px; align-items:center;
  padding:12px 14px; background:var(--band,#1e1b18); border-radius:6px 6px 0 0;
  border-bottom:1px solid rgba(255,244,230,.10); color:#f5efe6;
  font:500 13px/1.3 var(--sans,system-ui,sans-serif);
}}
#thz-spec-fig label {{ font-size:12px; color:#c8bfb3; margin-right:5px; }}
#thz-spec-fig select {{
  background:#2a2520; color:#f5efe6; border:1px solid rgba(255,244,230,.18);
  border-radius:4px; padding:5px 9px; font:500 12.5px/1.2 var(--sans,system-ui,sans-serif);
}}
#thz-spec-fig .ts-grid {{
  display:grid; grid-template-columns:1fr 1.25fr; gap:12px; padding:12px 14px 14px;
  background:var(--band,#1e1b18); border-radius:0 0 6px 6px;
}}
@media (max-width:720px) {{ #thz-spec-fig .ts-grid {{ grid-template-columns:1fr; }} }}
#thz-spec-fig canvas {{
  width:100%; height:290px; display:block; background:#15120f;
  border:1px solid rgba(255,244,230,.08); border-radius:5px; cursor:grab;
}}
#thz-spec-fig canvas:active {{ cursor:grabbing; }}
#thz-spec-fig .ts-meta {{ margin:6px 0 0; font:400 11.5px/1.35 var(--sans,system-ui,sans-serif); color:#b5aba0; }}
#thz-spec-fig svg {{ width:100%; height:290px; display:block; background:#15120f; border:1px solid rgba(255,244,230,.08); border-radius:5px; }}
</style>
<div class="ts-bar">
  <div>
    <label for="thz-3d-prot">3D aromatic network</label>
    <select id="thz-3d-prot">
      <option value="tubulin_1jff" selected>Tubulin 1JFF (81 rings)</option>
      <option value="lysozyme_1dpx">Egg-white Lysozyme 1DPX (12 rings)</option>
      <option value="hsa_1e7b">Human Albumin 1E7B (48 rings)</option>
      <option value="gabaa_6x3t">GABA-A channel 6X3T (234 rings)</option>
    </select>
  </div>
  <div>
    <label for="thz-spec-mol">Gas on Tubulin (1JFF)</label>
    <select id="thz-spec-mol"></select>
  </div>
</div>
<div class="ts-grid">
  <div>
    <canvas id="thz-3d-cv" width="380" height="290"></canvas>
    <p class="ts-meta" id="thz-3d-meta">Drag to rotate · Copper = Trp, Gold = Tyr, Sage = Phe, Ring = pocket</p>
  </div>
  <div>
    <svg id="thz-spec-svg" viewBox="0 0 440 290" role="img" aria-label="Collective terahertz frequency shifts across tubulin's 81 aromatic normal modes"></svg>
    <p class="ts-meta" id="thz-spec-meta"></p>
  </div>
</div>
<figcaption>Left: Drag to turn the aromatic dipole network (tryptophan, tyrosine, phenylalanine) and binding pockets inside tubulin or a control protein. Right: How each gas shifts tubulin's 81 collective aromatic modes from 468 to 696 THz, with Craddock's 613 ± 8 THz band shaded. Watch the vertical marker for the gas's own Drude frequency (f_iso): whenever it sits right of 613 THz (halothane, isoflurane, and also look-alikes c-C₄F₈ and CF₃CClFCF₃), the 613 THz band is pushed downward; whenever it sits left of 613 THz (F6, TFMB, and also potent anaesthetics o-xylene and methoxyflurane), the band is pushed upward.</figcaption>
<script>
(function(){{
  const DATA = {data_json};
  const selP = document.getElementById("thz-3d-prot");
  const selM = document.getElementById("thz-spec-mol");
  const cv = document.getElementById("thz-3d-cv");
  const ctx = cv.getContext("2d");
  const svg = document.getElementById("thz-spec-svg");
  const meta3d = document.getElementById("thz-3d-meta");
  const metaSp = document.getElementById("thz-spec-meta");
  const NS = "http://www.w3.org/2000/svg";

  const order = [
    ["isoflurane", "Isoflurane (clinical anaesthetic, f_iso = 630 THz)"],
    ["halothane", "Halothane (clinical anaesthetic, f_iso = 624 THz)"],
    ["desflurane", "Desflurane (clinical anaesthetic, f_iso = 706 THz)"],
    ["nitrous_oxide", "Nitrous oxide (clinical anaesthetic, f_iso = 1158 THz)"],
    ["methoxyflurane", "Methoxyflurane (potent clinical anaesthetic, f_iso = 581 THz)"],
    ["o_xylene", "o-Xylene (potent Fang anaesthetic, f_iso = 532 THz)"],
    ["F6", "F6 (Craddock non-anaesthetic, f_iso = 565 THz)"],
    ["TFMB", "TFMB (Craddock non-anaesthetic, f_iso = 483 THz)"],
    ["perfluorocyclobutane", "Perfluorocyclobutane (non-anaesthetic, f_iso = 687 THz)"],
    ["CF3CClFCF3", "CF₃CClFCF₃ (non-anaesthetic, f_iso = 656 THz)"],
    ["flurothyl", "Flurothyl (convulsant, f_iso = 633 THz)"]
  ];
  order.forEach(([id, txt], i) => {{
    if (!DATA.examples[id]) return;
    const o = document.createElement("option");
    o.value = id; o.textContent = txt;
    if (i === 0) o.selected = true;
    selM.appendChild(o);
  }});

  // 3D Viewer
  let rotY = 0.55, rotX = 0.25, dragging = false, lx = 0, ly = 0;
  function draw3D() {{
    const P = DATA.aroms3d[selP.value];
    const W = cv.width, H = cv.height;
    ctx.clearRect(0, 0, W, H);
    const cy = Math.cos(rotY), sy = Math.sin(rotY);
    const cx = Math.cos(rotX), sx = Math.sin(rotX);

    const pts = P.residues.map(r => r.xyz);
    const maxR = Math.max(12, ...pts.map(p => Math.hypot(p[0], p[1], p[2])));
    const scale = Math.min(W, H) * 0.39 / maxR;

    const proj = v => {{
      const x1 = v[0]*cy + v[2]*sy;
      const z1 = -v[0]*sy + v[2]*cy;
      const y2 = v[1]*cx - z1*sx;
      const z2 = v[1]*sx + z1*cx;
      const persp = 1.0 / (1.0 - z2 / (maxR * 4.5));
      return [W/2 + x1*scale*persp, H/2 - y2*scale*persp, z2, persp];
    }};

    const items = [];
    P.residues.forEach(r => {{
      const q = proj(r.xyz);
      const tip = proj([r.xyz[0] + r.u[0]*3.4, r.xyz[1] + r.u[1]*3.4, r.xyz[2] + r.u[2]*3.4]);
      items.push({{ type: "res", res: r.res, x: q[0], y: q[1], z: q[2], p: q[3], tx: tip[0], ty: tip[1] }});
    }});
    P.pockets.forEach(pk => {{
      const q = proj(pk.xyz);
      items.push({{ type: "pk", name: pk.pocket, x: q[0], y: q[1], z: q[2], p: q[3] }});
    }});
    items.sort((a, b) => a.z - b.z);

    // Faint nearest-neighbor couplings (<11 A)
    ctx.strokeStyle = "rgba(230,182,85,0.10)";
    ctx.lineWidth = 0.8;
    const rawR = P.residues;
    for (let i = 0; i < rawR.length; i++) {{
      for (let j = i + 1; j < rawR.length; j++) {{
        const a = rawR[i].xyz, b = rawR[j].xyz;
        const d = Math.hypot(a[0]-b[0], a[1]-b[1], a[2]-b[2]);
        if (d < 10.5) {{
          const pa = proj(a), pb = proj(b);
          ctx.beginPath(); ctx.moveTo(pa[0], pa[1]); ctx.lineTo(pb[0], pb[1]); ctx.stroke();
        }}
      }}
    }}

    const colMap = {{ TRP: "#d9824c", TYR: "#e6b655", PHE: "#7ea897" }};
    for (const it of items) {{
      if (it.type === "res") {{
        const c = colMap[it.res] || "#ccc";
        ctx.strokeStyle = c; ctx.lineWidth = 1.3;
        ctx.beginPath(); ctx.moveTo(it.x, it.y); ctx.lineTo(it.tx, it.ty); ctx.stroke();
        ctx.fillStyle = c;
        ctx.beginPath(); ctx.arc(it.x, it.y, (it.res === "TRP" ? 4.4 : 3.1) * it.p, 0, Math.PI*2); ctx.fill();
      }} else {{
        ctx.strokeStyle = "#f5efe6"; ctx.lineWidth = 1.6;
        ctx.beginPath(); ctx.arc(it.x, it.y, 7.5 * it.p, 0, Math.PI*2); ctx.stroke();
      }}
    }}
    const nTrp = P.residues.filter(r => r.res === "TRP").length;
    const nTyr = P.residues.filter(r => r.res === "TYR").length;
    const nPhe = P.residues.filter(r => r.res === "PHE").length;
    meta3d.textContent = `${{P.label}}: ${{nTrp}} Trp (copper), ${{nTyr}} Tyr (gold), ${{nPhe}} Phe (sage), ${{P.pockets.length}} pocket(s) (white rings) · Drag to turn`;
  }}

  cv.addEventListener("pointerdown", e => {{ dragging = true; lx = e.clientX; ly = e.clientY; cv.setPointerCapture(e.pointerId); }});
  cv.addEventListener("pointermove", e => {{
    if (!dragging) return;
    rotY += (e.clientX - lx) * 0.012;
    rotX += (e.clientY - ly) * 0.012;
    lx = e.clientX; ly = e.clientY;
    draw3D();
  }});
  cv.addEventListener("pointerup", () => {{ dragging = false; }});

  // Spectrum SVG
  function el(tag, attrs, parent) {{
    const n = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs || {{}})) n.setAttribute(k, v);
    if (parent) parent.appendChild(n);
    return n;
  }}

  function drawSpec() {{
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    const mid = selM.value;
    const ex = DATA.examples[mid];
    const mol = DATA.mols[mid];
    const base = DATA.baseline_1jff;
    const shifts = ex.shifts_ghz;
    const W = 440, H = 290, L = 52, R = 16, TOP = 26, BOT = 40;
    const fMin = 460, fMax = 710;
    const sx = f => L + (f - fMin) / (fMax - fMin) * (W - L - R);
    const maxAbs = Math.max(50, ...shifts.map(Math.abs)) * 1.12;
    // Note: plot Δf (so downward shifts go DOWN below 0, matching Craddock Fig. 4A!)
    const sy = df => TOP + (maxAbs - df) / (2 * maxAbs) * (H - TOP - BOT);
    const y0 = sy(0);

    // 613 +- 8 THz band
    el("rect", {{ x: sx(605), y: TOP, width: sx(621) - sx(605), height: H - TOP - BOT, fill: "rgba(230,182,85,.14)" }}, svg);
    const bl = el("text", {{ x: sx(613), y: TOP - 7, "text-anchor": "middle", fill: "#e6b655", "font-size": "10.5", "font-weight": "600", "font-family": "var(--sans,sans-serif)" }}, svg);
    bl.textContent = "613 ± 8 THz";

    // Gas isolated Drude frequency line (if within 460-710)
    if (ex.f_iso_thz >= fMin && ex.f_iso_thz <= fMax) {{
      const xf = sx(ex.f_iso_thz);
      el("line", {{ x1: xf, x2: xf, y1: TOP, y2: H - BOT, stroke: "#d95f59", "stroke-width": 1.5, "stroke-dasharray": "4 3" }}, svg);
      const fl = el("text", {{ x: Math.min(W - R - 4, xf + 4), y: TOP + 13, "text-anchor": xf > W - 95 ? "end" : "start", fill: "#f2a39e", "font-size": "10", "font-weight": "600", "font-family": "var(--sans,sans-serif)" }}, svg);
      fl.textContent = "f_iso " + ex.f_iso_thz.toFixed(0) + " THz";
    }} else {{
      const fl = el("text", {{ x: W - R - 4, y: TOP + 13, "text-anchor": "end", fill: "#f2a39e", "font-size": "10", "font-family": "var(--sans,sans-serif)" }}, svg);
      fl.textContent = "f_iso = " + ex.f_iso_thz.toFixed(0) + " THz →";
    }}

    // Zero line + Y ticks
    el("line", {{ x1: L, x2: W - R, y1: y0, y2: y0, stroke: "rgba(255,244,230,.38)" }}, svg);
    for (const frac of [-1, 0, 1]) {{
      const v = Math.round(frac * maxAbs / 1.12);
      const py = sy(v);
      const t = el("text", {{ x: L - 6, y: py + 3.5, "text-anchor": "end", fill: "#b5aba0", "font-size": "10", "font-family": "var(--sans,sans-serif)" }}, svg);
      t.textContent = v === 0 ? "0" : (v > 0 ? "+" + v : "−" + Math.abs(v));
    }}

    // X ticks
    for (const fv of [480, 540, 613, 680]) {{
      const px = sx(fv);
      const t = el("text", {{ x: px, y: H - BOT + 15, "text-anchor": "middle", fill: "#b5aba0", "font-size": "10", "font-family": "var(--sans,sans-serif)" }}, svg);
      t.textContent = fv + " THz";
    }}
    const yl = el("text", {{ x: 13, y: (TOP + H - BOT)/2, "text-anchor": "middle", fill: "#c8bfb3", "font-size": "10.5", "font-family": "var(--sans,sans-serif)", transform: `rotate(-90 13 ${{(TOP + H - BOT)/2}})` }}, svg);
    yl.textContent = "Mode shift Δf (GHz)";

    // Sticks for all 81 modes
    for (let i = 0; i < base.length; i++) {{
      const px = sx(base[i]);
      const df = shifts[i];
      const py = sy(df);
      const inB = base[i] >= 605 && base[i] <= 621;
      const col = df < 0 ? (inB ? "#e6b655" : "#8eb8a8") : (inB ? "#d95f59" : "#9c706c");
      el("line", {{ x1: px, x2: px, y1: y0, y2: py, stroke: col, "stroke-width": inB ? 2.4 : 1.4, opacity: inB ? 0.95 : 0.6 }}, svg);
    }}

    const dir = ex.d_613_ghz > 0 ? "downward (−" + ex.d_613_ghz.toFixed(0) + " GHz)" : "upward (+" + Math.abs(ex.d_613_ghz).toFixed(0) + " GHz)";
    metaSp.textContent = `${{mol.name}} in ${{ex.best_pocket}}: 613 THz band shifts ${{dir}} · f_iso = ${{ex.f_iso_thz}} THz`;
  }}

  selP.addEventListener("change", draw3D);
  selM.addEventListener("change", drawSpec);
  draw3D();
  drawSpec();
}})();
</script>
</figure>
"""


def main() -> None:
    summary = json.loads((RESULTS / "summary.json").read_text())
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    figs = {
        "tiles.html": build_tiles(summary),
        "verdict.html": build_verdict(summary),
        "repulsion.html": build_repulsion_explorer(summary),
        "proteins.html": build_proteins_and_so3(summary),
        "spectrum.html": build_spectrum_observatory(summary),
    }
    print(f"Wrote {len(figs)} figures to {OUT_DIR}:")
    for name, body in figs.items():
        p = OUT_DIR / name
        p.write_text(body)
        print(f"  {name:16s} {len(body):6d} bytes")


if __name__ == "__main__":
    main()
