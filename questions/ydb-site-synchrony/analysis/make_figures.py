#!/usr/bin/env python3
"""
Generate interactive, self-contained HTML/SVG/JS figures for Issue #113
(ydb-site-synchrony) in site/figures/ydb-site-synchrony/.
Uses only site.css design tokens and zero external CDNs.
"""

from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT.parent.parent
SUMMARY_PATH = ROOT / "results" / "summary.json"
FIG_DIR = REPO / "site" / "figures" / "ydb-site-synchrony"

esc = lambda s: html.escape(str(s), quote=True)


def write_tiles(d: dict) -> None:
    p1 = d["pillar1_primary_9sites"]
    lst = d["positive_control_lst_sites5"]
    p2 = d["pillar2_kennett32_audit"]
    items = [
        (f"T = {p1['ward_wilson_T']:.0f} vs. {lst['ward_wilson_T']:.2f}",
         "radiocarbon scatter across 9 direct-dated YDB sites vs. 5 single-year Laacher See volcano sites (p = 0.0005 vs. 0.998)", False),
        (f"{p2['n_tight_direct_le300']} of {p2['n_total_sites']}",
         "claimed YDB sites with both a direct date on the proxy layer and a 95% interval ≤ 300 yr wide (12.5%)", False),
        (f"{int(p2['W_50']['width_yr'])} yr",
         "calendar span (12,260–13,190 cal BP) where ≥ 50% of Kennett's 23 modeled sites overlap any placebo year", False),
        ("Mixed / Unproven",
         "raw dates reject a single year; selective old-wood pruning + wide intervals leave synchrony unfalsifiable", True),
    ]
    out = ['<div class="tiles">']
    for v, l, is_word in items:
        cls = "tile-value is-word" if is_word else "tile-value"
        out.append(f'<div class="tile"><p class="{cls}">{esc(v)}</p><p class="tile-label">{esc(l)}</p></div>')
    out.append("</div>")
    (FIG_DIR / "tiles.html").write_text("\n".join(out) + "\n", encoding="utf-8")


def write_pillar1_calibration(d: dict) -> None:
    payload = {
        "lst": d["positive_control_lst_sites5"]["dates"],
        "lst_meta": {
            "T": d["positive_control_lst_sites5"]["ward_wilson_T"],
            "pM0": d["positive_control_lst_sites5"]["M0"]["p_T_best"],
            "pM1": d["positive_control_lst_sites5"]["M1"]["p_T_best"],
            "sd": d["positive_control_lst_sites5"]["cal_median_sd"],
            "ov_n": d["positive_control_lst_sites5"]["max_hpd95_overlap_n"],
            "ov_yr": d["positive_control_lst_sites5"]["max_hpd95_overlap_years"],
        },
        "primary": d["pillar1_primary_9sites"]["dates"],
        "primary_meta": {
            "T": d["pillar1_primary_9sites"]["ward_wilson_T"],
            "pM0": d["pillar1_primary_9sites"]["M0"]["p_T_best"],
            "pM1": d["pillar1_primary_9sites"]["M1"]["p_T_best"],
            "sd": d["pillar1_primary_9sites"]["cal_median_sd"],
            "ov_n": d["pillar1_primary_9sites"]["max_hpd95_overlap_n"],
            "ov_yr": d["pillar1_primary_9sites"]["max_hpd95_overlap_years"],
        },
        "favorable": d["pillar1_favorable_9sites"]["dates"],
        "favorable_meta": {
            "T": d["pillar1_favorable_9sites"]["ward_wilson_T"],
            "pM0": d["pillar1_favorable_9sites"]["M0"]["p_T_best"],
            "pM1": d["pillar1_favorable_9sites"]["M1"]["p_T_best"],
            "sd": d["pillar1_favorable_9sites"]["cal_median_sd"],
            "ov_n": d["pillar1_favorable_9sites"]["max_hpd95_overlap_n"],
            "ov_yr": d["pillar1_favorable_9sites"]["max_hpd95_overlap_years"],
        },
    }
    data_json = json.dumps(payload)

    html_doc = f"""<figure class="fig" id="ydb-cal-fig" aria-label="IntCal20 calibrated 95.4% HPD intervals for Laacher See Tephra and nine direct-dated YDB sites">
<style>
#ydb-cal-fig .cal-controls {{ display:flex; flex-wrap:wrap; gap:.5rem; align-items:center; margin:0 0 .85rem; }}
#ydb-cal-fig .cal-btn {{ font:500 11.5px/1.2 var(--mono); letter-spacing:.04em; padding:.42rem .75rem; border:1px solid var(--line); background:var(--panel); color:var(--ink); cursor:pointer; border-radius:2px; }}
#ydb-cal-fig .cal-btn[aria-pressed="true"] {{ background:var(--copper); border-color:var(--copper); color:var(--paper); }}
#ydb-cal-fig .cal-stat {{ margin-left:auto; font:400 11.5px/1.4 var(--mono); color:var(--ink-soft); }}
#ydb-cal-fig .cal-tip {{ min-height:1.4rem; margin:.4rem 0 0; font:400 12px/1.4 var(--mono); color:var(--ink-soft); }}
</style>
<div class="cal-controls">
  <button type="button" class="cal-btn" data-mode="primary" aria-pressed="true">Primary direct-14C (9 sites)</button>
  <button type="button" class="cal-btn" data-mode="favorable" aria-pressed="false">Old-wood-mitigated (9 sites)</button>
  <span class="cal-stat" id="ydb-cal-stat"></span>
</div>
<div class="fig-scroll">
  <svg id="ydb-cal-svg" class="chart" viewBox="0 0 740 470" role="img" aria-label="Calibrated age intervals on IntCal20 comparing Laacher See positive control with nine YDB sites"></svg>
</div>
<p class="cal-tip" id="ydb-cal-tip">Hover or focus any site bar for uncalibrated 14C age, IntCal20 median, and 95.4% HPD interval.</p>
<figcaption>Unmodeled IntCal20 calibration (95.4% HPD bars and median markers) for the real single-year Laacher See volcanic eruption positive control (top, green; 5 localities up to 335 km apart) vs. nine directly radiocarbon-dated YDB sites (bottom, copper). Toggle between the unfiltered primary horizon dates and Kennett et al.'s old-wood-mitigated selection. The shaded vertical band marks the revised IntCal20 YDB window (12,875–12,775 cal BP); the thin green line marks the Laacher See eruption (13,006 cal BP).</figcaption>
<script>
(function() {{
  const DATA = {data_json};
  const svg = document.getElementById("ydb-cal-svg");
  const statEl = document.getElementById("ydb-cal-stat");
  const tipEl = document.getElementById("ydb-cal-tip");
  const btns = document.querySelectorAll("#ydb-cal-fig .cal-btn");
  const NS = "http://www.w3.org/2000/svg";

  const W = 740, left = 186, right = 716, topPad = 32;
  const X_MAX = 13650, X_MIN = 12450; // older on left, younger on right
  const sx = yr => left + (X_MAX - yr) / (X_MAX - X_MIN) * (right - left);

  function el(tag, attrs, text) {{
    const n = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs || {{}})) n.setAttribute(k, String(v));
    if (text !== undefined) n.textContent = text;
    return n;
  }}

  function render(mode) {{
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    const ydb = mode === "primary" ? DATA.primary : DATA.favorable;
    const meta = mode === "primary" ? DATA.primary_meta : DATA.favorable_meta;
    const lst = DATA.lst;

    statEl.textContent = "YDB T=" + meta.T.toFixed(1) + " (p_M0=" + meta.pM0.toFixed(4) + ", p_M1=" + meta.pM1.toFixed(3) + ") | overlap " + meta.ov_n + "/9";

    const rowH = 24;
    const lstY0 = topPad + 18;
    const ydbY0 = lstY0 + lst.length * rowH + 42;
    const H = ydbY0 + ydb.length * rowH + 48;
    svg.setAttribute("viewBox", "0 0 " + W + " " + H);

    // Gridlines
    for (let yr = 13600; yr >= 12500; yr -= 200) {{
      const x = sx(yr);
      svg.appendChild(el("line", {{ x1: x, x2: x, y1: topPad, y2: H - 36, stroke: "var(--line)", "stroke-width": 1 }}));
      svg.appendChild(el("text", {{ x: x, y: H - 18, "text-anchor": "middle", fill: "var(--faint)", "font-family": "var(--mono)", "font-size": 10.5 }}, yr.toLocaleString()));
    }}
    svg.appendChild(el("text", {{ x: (left + right) / 2, y: H - 3, "text-anchor": "middle", fill: "var(--faint)", "font-family": "var(--sans)", "font-size": 11 }}, "Calibrated calendar age (IntCal20 cal BP, older left → younger right)"));

    // Reference bands: LST 13,006 and YDB IntCal20 window 12,875-12,775
    svg.appendChild(el("rect", {{ x: sx(12875), y: topPad, width: sx(12775) - sx(12875), height: H - topPad - 36, fill: "var(--copper)", opacity: 0.14 }}));
    svg.appendChild(el("text", {{ x: sx(12825), y: topPad - 8, "text-anchor": "middle", fill: "var(--copper)", "font-family": "var(--mono)", "font-size": 10 }}, "YDB (12,875–12,775)"));

    svg.appendChild(el("line", {{ x1: sx(13006), x2: sx(13006), y1: topPad, y2: lstY0 + lst.length * rowH + 4, stroke: "var(--verdigris)", "stroke-width": 1.6, "stroke-dasharray": "4 3" }}));
    svg.appendChild(el("text", {{ x: sx(13006) - 4, y: topPad - 8, "text-anchor": "end", fill: "var(--verdigris)", "font-family": "var(--mono)", "font-size": 10 }}, "LST 13,006 BP"));

    // Section headers
    svg.appendChild(el("text", {{ x: 4, y: lstY0 - 6, fill: "var(--verdigris)", "font-family": "var(--mono)", "font-size": 10.5, "font-weight": 600 }}, "POSITIVE CONTROL: LAACHER SEE TEPHRA (5/5 overlap, SD=20 yr)"));
    svg.appendChild(el("text", {{ x: 4, y: ydbY0 - 10, fill: "var(--copper)", "font-family": "var(--mono)", "font-size": 10.5, "font-weight": 600 }}, (mode === "primary" ? "YDB PRIMARY DIRECT-14C" : "YDB OLD-WOOD-MITIGATED") + " (" + meta.ov_n + "/9 overlap, SD=" + meta.sd.toFixed(0) + " yr)"));

    function drawRows(rows, yStart, color, shape) {{
      rows.forEach((r, i) => {{
        const y = yStart + i * rowH + 10;
        const g = el("g", {{ tabindex: 0, style: "cursor:pointer" }});
        const label = r.site.length > 24 ? r.site.slice(0, 23) + "…" : r.site;
        g.appendChild(el("text", {{ x: left - 8, y: y + 4, "text-anchor": "end", fill: "var(--ink)", "font-family": "var(--sans)", "font-size": 11.5 }}, label));
        // Draw each HPD sub-interval
        (r.hpd95_intervals || [[r.hpd95_lower, r.hpd95_upper]]).forEach(seg => {{
          const x1 = Math.max(left, sx(seg[1]));
          const x2 = Math.min(right, sx(seg[0]));
          if (x2 > x1) {{
            g.appendChild(el("rect", {{ x: x1, y: y - 4, width: Math.max(2, x2 - x1), height: 8, rx: 2, fill: color, opacity: 0.35 }}));
          }}
        }});
        // Whisker line across outer HPD bounds
        const ox1 = Math.max(left, sx(r.hpd95_upper));
        const ox2 = Math.min(right, sx(r.hpd95_lower));
        g.appendChild(el("line", {{ x1: ox1, x2: ox2, y1: y, y2: y, stroke: color, "stroke-width": 1.8 }}));
        // Median marker (shape + color encoding)
        const mx = sx(r.cal_median);
        if (shape === "diamond") {{
          g.appendChild(el("polygon", {{ points: `${{mx}},${{y-5}} ${{mx+5}},${{y}} ${{mx}},${{y+5}} ${{mx-5}},${{y}}`, fill: color, stroke: "var(--paper)", "stroke-width": 1 }}));
        }} else {{
          g.appendChild(el("circle", {{ cx: mx, cy: y, r: 4.5, fill: color, stroke: "var(--paper)", "stroke-width": 1 }}));
        }}
        const msg = r.site + " [" + r.lab_id + "]: " + r.rcybp + " ± " + r.sigma + " 14C BP → IntCal20 median " + r.cal_median + " cal BP (95.4% HPD " + r.hpd95_upper + "–" + r.hpd95_lower + " BP)";
        const show = () => {{ tipEl.textContent = msg; }};
        g.addEventListener("mouseenter", show);
        g.addEventListener("focus", show);
        svg.appendChild(g);
      }});
    }}

    drawRows(lst, lstY0, "var(--verdigris)", "diamond");
    drawRows(ydb, ydbY0, "var(--copper)", "circle");
  }}

  btns.forEach(b => b.addEventListener("click", () => {{
    btns.forEach(x => x.setAttribute("aria-pressed", String(x === b)));
    render(b.dataset.mode);
  }}));
  render("primary");
}})();
</script>
</figure>
"""
    (FIG_DIR / "pillar1_calibration.html").write_text(html_doc, encoding="utf-8")


def write_simulation_benchmark(d: dict) -> None:
    rows = []
    for key, label, kind in [
        ("positive_control_lst_sites5", "Laacher See (5 sites)", "lst"),
        ("positive_control_lst_all16", "Laacher See (16 dates)", "lst"),
        ("pillar1_favorable_9sites", "YDB Old-Wood-Mitigated (9 sites)", "ydb_fav"),
        ("pillar1_primary_9sites", "YDB Primary Direct-14C (9 sites)", "ydb"),
        ("pillar1_allraw_33dates", "YDB All Raw Direct-14C (33 dates)", "ydb"),
    ]:
        p = d[key]
        rows.append({
            "label": label,
            "kind": kind,
            "T_obs": p["ward_wilson_T"],
            "df": p["ward_wilson_df"],
            "M0": {
                "med": p["M0"]["sim_T_median_at_best"],
                "q95": p["M0"]["sim_T_q95_at_best"],
                "p": p["M0"]["p_T_best"],
            },
            "M1": {
                "med": p["M1"]["sim_T_median_at_best"],
                "q95": p["M1"]["sim_T_q95_at_best"],
                "p": p["M1"]["p_T_best"],
            },
        })
    data_json = json.dumps(rows)

    html_doc = f"""<figure class="fig" id="ydb-sim-fig" aria-label="Observed vs forward-simulated single-year Ward-Wilson T statistics on IntCal20">
<style>
#ydb-sim-fig .sim-controls {{ display:flex; flex-wrap:wrap; gap:.5rem; align-items:center; margin:0 0 .85rem; }}
#ydb-sim-fig .sim-btn {{ font:500 11.5px/1.2 var(--mono); letter-spacing:.04em; padding:.42rem .75rem; border:1px solid var(--line); background:var(--panel); color:var(--ink); cursor:pointer; border-radius:2px; }}
#ydb-sim-fig .sim-btn[aria-pressed="true"] {{ background:var(--copper); border-color:var(--copper); color:var(--paper); }}
#ydb-sim-fig .sim-tip {{ min-height:1.4rem; margin:.4rem 0 0; font:400 12px/1.4 var(--mono); color:var(--ink-soft); }}
</style>
<div class="sim-controls">
  <button type="button" class="sim-btn" data-model="M0" aria-pressed="true">Model M0 (lab + IntCal20 curve error)</button>
  <button type="button" class="sim-btn" data-model="M1" aria-pressed="false">Model M1 (+ 20 yr inter-lab + 50 yr old-wood)</button>
</div>
<div class="fig-scroll">
  <svg id="ydb-sim-svg" class="chart" viewBox="0 0 740 270" role="img" aria-label="Log-scale comparison of observed Ward-Wilson T against 2,000 forward-simulated single-year catalogues"></svg>
</div>
<p class="sim-tip" id="ydb-sim-tip">Hover or focus any row to inspect observed T, simulated single-year 95th percentile, and best p-value across the calendar-year sweep.</p>
<figcaption>Observed Ward–Wilson radiocarbon inhomogeneity T (points) versus the most generous single-year simulated distribution across the calendar sweep (bars show median to 95th percentile of 2,000 IntCal20 forward simulations; log scale). Laacher See Tephra (diamonds, green) sits comfortably below the single-year benchmark under both models. Unfiltered YDB primary dates (circles, copper) exceed the 95th percentile by 4× to 26× under both M0 and M1; only the old-wood-mitigated 9-site subset (triangle, ochre) enters the M1 tolerance band while still failing M0 (p = 0.009).</figcaption>
<script>
(function() {{
  const ROWS = {data_json};
  const svg = document.getElementById("ydb-sim-svg");
  const tipEl = document.getElementById("ydb-sim-tip");
  const btns = document.querySelectorAll("#ydb-sim-fig .sim-btn");
  const NS = "http://www.w3.org/2000/svg";

  const W = 740, H = 270, left = 240, right = 708, topPad = 32;
  const LOG_MIN = Math.log10(0.3), LOG_MAX = Math.log10(1500);
  const sx = v => left + (Math.log10(Math.max(0.3, v)) - LOG_MIN) / (LOG_MAX - LOG_MIN) * (right - left);

  function el(tag, attrs, text) {{
    const n = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs || {{}})) n.setAttribute(k, String(v));
    if (text !== undefined) n.textContent = text;
    return n;
  }}

  function render(model) {{
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    [0.5, 1, 5, 10, 50, 100, 500, 1000].forEach(v => {{
      const x = sx(v);
      svg.appendChild(el("line", {{ x1: x, x2: x, y1: topPad - 4, y2: H - 40, stroke: "var(--line)", "stroke-width": 1 }}));
      svg.appendChild(el("text", {{ x: x, y: H - 22, "text-anchor": "middle", fill: "var(--faint)", "font-family": "var(--mono)", "font-size": 10.5 }}, String(v)));
    }});
    svg.appendChild(el("text", {{ x: (left + right) / 2, y: H - 5, "text-anchor": "middle", fill: "var(--faint)", "font-family": "var(--sans)", "font-size": 11 }}, "Ward–Wilson radiocarbon inhomogeneity T (log scale; lower = more synchronous)"));

    const rowH = 38;
    ROWS.forEach((r, i) => {{
      const y = topPad + 16 + i * rowH;
      const m = r[model];
      const g = el("g", {{ tabindex: 0, style: "cursor:pointer" }});
      const color = r.kind === "lst" ? "var(--verdigris)" : (r.kind === "ydb_fav" ? "var(--ochre)" : "var(--copper)");

      g.appendChild(el("text", {{ x: left - 10, y: y + 4, "text-anchor": "end", fill: "var(--ink)", "font-family": "var(--sans)", "font-size": 11.5 }}, r.label));

      // Simulated single-year null bar (from 0.3 to q95, with tick at median)
      const x0 = sx(0.3);
      const xMed = sx(m.med);
      const x95 = sx(m.q95);
      g.appendChild(el("rect", {{ x: x0, y: y - 7, width: Math.max(2, x95 - x0), height: 14, rx: 2, fill: "var(--slate)", opacity: 0.22 }}));
      g.appendChild(el("line", {{ x1: xMed, x2: xMed, y1: y - 9, y2: y + 9, stroke: "var(--slate)", "stroke-width": 2 }}));
      g.appendChild(el("line", {{ x1: x95, x2: x95, y1: y - 9, y2: y + 9, stroke: "var(--slate)", "stroke-width": 1.5, "stroke-dasharray": "2 2" }}));

      // Observed T marker
      const xObs = sx(r.T_obs);
      if (r.kind === "lst") {{
        g.appendChild(el("polygon", {{ points: `${{xObs}},${{y-6.5}} ${{xObs+6.5}},${{y}} ${{xObs}},${{y+6.5}} ${{xObs-6.5}},${{y}}`, fill: color, stroke: "var(--paper)", "stroke-width": 1.2 }}));
      }} else if (r.kind === "ydb_fav") {{
        g.appendChild(el("polygon", {{ points: `${{xObs}},${{y-7}} ${{xObs+6.5}},${{y+5.5}} ${{xObs-6.5}},${{y+5.5}}`, fill: color, stroke: "var(--paper)", "stroke-width": 1.2 }}));
      }} else {{
        g.appendChild(el("circle", {{ cx: xObs, cy: y, r: 6, fill: color, stroke: "var(--paper)", "stroke-width": 1.2 }}));
      }}

      const pTxt = m.p < 0.001 ? "p=0.0005" : "p=" + m.p.toFixed(3);
      const lblX = Math.min(right - 2, xObs + 10);
      const anchor = xObs > right - 95 ? "end" : "start";
      const tx = anchor === "end" ? xObs - 10 : lblX;
      g.appendChild(el("text", {{ x: tx, y: y + 4, "text-anchor": anchor, fill: color, "font-family": "var(--mono)", "font-size": 10.5, "font-weight": 600 }}, "T=" + r.T_obs.toFixed(1) + " (" + pTxt + ")"));

      const msg = r.label + " [" + model + "]: observed T=" + r.T_obs.toFixed(2) + " (df=" + r.df + ") vs. simulated single-year median " + m.med.toFixed(1) + " (95th pct " + m.q95.toFixed(1) + "), best p=" + m.p.toFixed(4);
      const show = () => {{ tipEl.textContent = msg; }};
      g.addEventListener("mouseenter", show);
      g.addEventListener("focus", show);
      svg.appendChild(g);
    }});

    // Legend top-right
    svg.appendChild(el("rect", {{ x: left, y: 8, width: 14, height: 10, fill: "var(--slate)", opacity: 0.25 }}));
    svg.appendChild(el("text", {{ x: left + 19, y: 17, fill: "var(--ink-soft)", "font-family": "var(--sans)", "font-size": 10.5 }}, "Simulated single-year 0–95th pct band (solid tick = median)"));
  }}

  btns.forEach(b => b.addEventListener("click", () => {{
    btns.forEach(x => x.setAttribute("aria-pressed", String(x === b)));
    render(b.dataset.model);
  }}));
  render("M0");
}})();
</script>
</figure>
"""
    (FIG_DIR / "simulation_benchmark.html").write_text(html_doc, encoding="utf-8")


def write_placebo_overlap(d: dict) -> None:
    p2 = d["pillar2_kennett32_audit"]
    modeled = [s for s in p2["sites"] if s["quality"] != "Unmodeled"]
    # Sort by 95% CI width ascending so tight vs wide contrast is visually instant
    modeled.sort(key=lambda s: s["ci95_width"])
    payload = {
        "curve": p2["placebo_curve"],
        "sites": modeled,
        "w50": p2["W_50"],
        "w80": p2["W_80"],
    }
    data_json = json.dumps(payload)

    html_doc = f"""<figure class="fig" id="ydb-placebo-fig" aria-label="Placebo-year overlap audit of Kennett et al. 2015's 23 modeled YDB sites">
<style>
#ydb-placebo-fig .pl-controls {{ display:flex; flex-wrap:wrap; gap:.75rem; align-items:center; margin:0 0 .85rem; }}
#ydb-placebo-fig .pl-controls label {{ font:500 11.5px/1.2 var(--mono); color:var(--ink); }}
#ydb-placebo-fig input[type="range"] {{ flex:1; min-width:180px; accent-color:var(--copper); }}
#ydb-placebo-fig .pl-readout {{ font:600 12px/1.3 var(--mono); color:var(--copper); min-width:240px; text-align:right; }}
#ydb-placebo-fig .pl-presets {{ display:flex; flex-wrap:wrap; gap:.4rem; margin:0 0 .7rem; }}
#ydb-placebo-fig .pl-preset {{ font:500 11px/1.2 var(--mono); padding:.3rem .6rem; border:1px solid var(--line); background:var(--panel); color:var(--ink); cursor:pointer; border-radius:2px; }}
#ydb-placebo-fig .pl-preset:hover {{ border-color:var(--copper); color:var(--copper); }}
</style>
<div class="pl-controls">
  <label for="ydb-pl-slider">Test year:</label>
  <input id="ydb-pl-slider" type="range" min="11500" max="14000" step="10" value="12300">
  <span class="pl-readout" id="ydb-pl-readout"></span>
</div>
<div class="pl-presets">
  <button type="button" class="pl-preset" data-yr="13800">13,800 BP (+1000 yr)</button>
  <button type="button" class="pl-preset" data-yr="13300">13,300 BP (+500 yr)</button>
  <button type="button" class="pl-preset" data-yr="13050">13,050 BP (+250 yr)</button>
  <button type="button" class="pl-preset" data-yr="12800">12,800 BP (YDB target)</button>
  <button type="button" class="pl-preset" data-yr="12550">12,550 BP (−250 yr)</button>
  <button type="button" class="pl-preset" data-yr="12300">12,300 BP (−500 yr)</button>
  <button type="button" class="pl-preset" data-yr="11800">11,800 BP (−1000 yr)</button>
</div>
<div class="fig-scroll">
  <svg id="ydb-pl-svg" class="chart" viewBox="0 0 740 590" role="img" aria-label="Placebo-year overlap fraction curve and sorted 95% credible intervals for all 23 modeled sites in Kennett et al. 2015"></svg>
</div>
<figcaption>Precision and placebo-year overlap audit of all 23 Bayesian-modeled YDB sites in Kennett et al. (2015, Fig. 2; 9 more sites could not be modeled at all). Drag the slider or click a preset placebo year. Top: fraction of sites whose published 95% CI contains any test year from 14,000 to 11,500 cal BP (shaded band shows the 930-yr window where ≥ 50% of sites overlap). Bottom: all 23 modeled sites sorted from tightest (Aalsterhut, 120 yr) to widest (Melrose, 9,475 yr, clipped at frame edge), with solid circles marking direct dates on the proxy layer and open circles marking indirect/interpolated chronologies. Sites overlapping the chosen placebo year light up.</figcaption>
<script>
(function() {{
  const DATA = {data_json};
  const svg = document.getElementById("ydb-pl-svg");
  const slider = document.getElementById("ydb-pl-slider");
  const readout = document.getElementById("ydb-pl-readout");
  const presets = document.querySelectorAll("#ydb-placebo-fig .pl-preset");
  const NS = "http://www.w3.org/2000/svg";

  const W = 740, left = 165, right = 716;
  const X_MAX = 14000, X_MIN = 11500;
  const sx = yr => left + (X_MAX - yr) / (X_MAX - X_MIN) * (right - left);

  const topY0 = 24, topH = 128;
  const botY0 = 198, rowH = 15.5;
  const H = botY0 + DATA.sites.length * rowH + 38;
  svg.setAttribute("viewBox", "0 0 " + W + " " + H);

  function el(tag, attrs, text) {{
    const n = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs || {{}})) n.setAttribute(k, String(v));
    if (text !== undefined) n.textContent = text;
    return n;
  }}

  function render(testYr) {{
    while (svg.firstChild) svg.removeChild(svg.firstChild);

    const pt = DATA.curve.find(c => c.year_cal_bp === testYr) || DATA.curve[0];
    readout.textContent = testYr.toLocaleString() + " BP → " + pt.n_all + "/23 (" + (100 * pt.frac_all).toFixed(1) + "%) overlap";

    // W_50 shading on top plot
    svg.appendChild(el("rect", {{
      x: sx(DATA.w50.max_bp), y: topY0,
      width: sx(DATA.w50.min_bp) - sx(DATA.w50.max_bp), height: topH,
      fill: "var(--ochre)", opacity: 0.14
    }}));

    // Horizontal grid for top plot
    [0, 0.25, 0.5, 0.75, 1.0].forEach(f => {{
      const y = topY0 + topH - f * topH;
      svg.appendChild(el("line", {{ x1: left, x2: right, y1: y, y2: y, stroke: "var(--line)", "stroke-width": f === 0.5 ? 1.2 : 0.8, "stroke-dasharray": f === 0.5 ? "3 3" : "" }}));
      svg.appendChild(el("text", {{ x: left - 8, y: y + 4, "text-anchor": "end", fill: "var(--faint)", "font-family": "var(--mono)", "font-size": 10 }}, Math.round(f * 100) + "%"));
    }});
    svg.appendChild(el("text", {{ x: 6, y: topY0 + 14, fill: "var(--ink)", "font-family": "var(--mono)", "font-size": 10.5, "font-weight": 600 }}, "OVERLAP CURVE"));
    svg.appendChild(el("text", {{ x: 6, y: topY0 + 30, fill: "var(--faint)", "font-family": "var(--sans)", "font-size": 10.5 }}, "% of 23 modeled sites"));
    svg.appendChild(el("text", {{ x: 6, y: topY0 + 44, fill: "var(--faint)", "font-family": "var(--sans)", "font-size": 10.5 }}, "covering test year"));

    // Vertical year gridlines
    for (let yr = 14000; yr >= 11500; yr -= 500) {{
      const x = sx(yr);
      svg.appendChild(el("line", {{ x1: x, x2: x, y1: topY0, y2: H - 30, stroke: "var(--line)", "stroke-width": 0.9 }}));
      svg.appendChild(el("text", {{ x: x, y: H - 14, "text-anchor": "middle", fill: "var(--faint)", "font-family": "var(--mono)", "font-size": 10.5 }}, yr.toLocaleString()));
    }}

    // Curve paths: Low, Med, High, and All
    function makePath(key, stroke, width, dash) {{
      const pts = DATA.curve.map(c => sx(c.year_cal_bp).toFixed(1) + "," + (topY0 + topH - c[key] * topH).toFixed(1));
      svg.appendChild(el("path", {{ d: "M" + pts.join(" L"), fill: "none", stroke: stroke, "stroke-width": width, "stroke-dasharray": dash || "" }}));
    }}
    makePath("frac_low", "var(--slate)", 1.3, "4 3");
    makePath("frac_med", "var(--ochre)", 1.3, "2 2");
    makePath("frac_high", "var(--verdigris)", 1.5, "");
    makePath("frac_all", "var(--copper)", 2.4, "");

    // Top legend
    svg.appendChild(el("text", {{ x: left + 6, y: topY0 - 8, fill: "var(--copper)", "font-family": "var(--mono)", "font-size": 10 }}, "━ All 23"));
    svg.appendChild(el("text", {{ x: left + 74, y: topY0 - 8, fill: "var(--verdigris)", "font-family": "var(--mono)", "font-size": 10 }}, "━ High (9)"));
    svg.appendChild(el("text", {{ x: left + 158, y: topY0 - 8, fill: "var(--ochre)", "font-family": "var(--mono)", "font-size": 10 }}, "┈ Med (8)"));
    svg.appendChild(el("text", {{ x: left + 236, y: topY0 - 8, fill: "var(--slate)", "font-family": "var(--mono)", "font-size": 10 }}, "┄ Low (6)"));
    svg.appendChild(el("text", {{ x: right, y: topY0 - 8, "text-anchor": "end", fill: "var(--ochre)", "font-family": "var(--mono)", "font-size": 10 }}, "W50 = 930 yr (13,190–12,260)"));

    // Bottom header
    svg.appendChild(el("text", {{ x: 6, y: botY0 - 12, fill: "var(--ink)", "font-family": "var(--mono)", "font-size": 10.5, "font-weight": 600 }}, "23 MODELED SITES (SORTED BY 95% CI WIDTH; ● DIRECT ON PROXIES, ○ INDIRECT)"));

    // Site bars
    DATA.sites.forEach((s, i) => {{
      const y = botY0 + i * rowH + 6;
      const hit = s.ci95_lower <= testYr && testYr <= s.ci95_upper;
      const tierCol = s.quality === "High" ? "var(--verdigris)" : (s.quality === "Med" ? "var(--ochre)" : "var(--slate)");
      const op = hit ? 0.92 : 0.22;

      // Site label + direct circle
      svg.appendChild(el("circle", {{
        cx: 12, cy: y, r: 3.3,
        fill: s.direct_on_proxies ? tierCol : "none",
        stroke: tierCol, "stroke-width": 1.3
      }}));
      svg.appendChild(el("text", {{
        x: left - 8, y: y + 3.5, "text-anchor": "end",
        fill: hit ? "var(--ink)" : "var(--faint)",
        "font-family": "var(--sans)", "font-size": 10.5,
        "font-weight": hit ? 600 : 400
      }}, s.site + " (" + Math.round(s.ci95_width) + "y)"));

      const x1 = Math.max(left, sx(s.ci95_upper));
      const x2 = Math.min(right, sx(s.ci95_lower));
      svg.appendChild(el("rect", {{
        x: x1, y: y - 4, width: Math.max(2, x2 - x1), height: 8, rx: 1.5,
        fill: hit ? "var(--copper)" : tierCol, opacity: op
      }}));
      // Clip arrows for sites extending outside 14,000-11,500
      if (s.ci95_upper > X_MAX) {{
        svg.appendChild(el("text", {{ x: left + 3, y: y + 3.5, fill: "var(--paper)", "font-family": "var(--mono)", "font-size": 9 }}, "◀"));
      }}
      if (s.ci95_lower < X_MIN) {{
        svg.appendChild(el("text", {{ x: right - 10, y: y + 3.5, fill: "var(--paper)", "font-family": "var(--mono)", "font-size": 9 }}, "▶"));
      }}
    }});

    // Active vertical scrubber line
    const tx = sx(testYr);
    svg.appendChild(el("line", {{ x1: tx, x2: tx, y1: topY0, y2: H - 30, stroke: "var(--copper)", "stroke-width": 2 }}));
    svg.appendChild(el("circle", {{ cx: tx, cy: topY0 + topH - pt.frac_all * topH, r: 4.5, fill: "var(--copper)", stroke: "var(--paper)", "stroke-width": 1.5 }}));
  }}

  slider.addEventListener("input", () => render(Number(slider.value)));
  presets.forEach(b => b.addEventListener("click", () => {{
    const yr = Number(b.dataset.yr);
    slider.value = String(yr);
    render(yr);
  }}));
  render(12300);
}})();
</script>
</figure>
"""
    (FIG_DIR / "placebo_overlap.html").write_text(html_doc, encoding="utf-8")


def write_funnel_summary(d: dict) -> None:
    p2 = d["pillar2_kennett32_audit"]
    stages = [
        ("Claimed YDB sites (Kennett 2015 Fig. 2)", p2["n_total_sites"], "var(--slate)"),
        ("Sufficient data for Bayesian age model", p2["n_modeled_sites"], "var(--ochre)"),
        ("Direct date from proxy layer itself", p2["n_direct_on_proxies_modeled"], "var(--copper)"),
        ("Direct date + 95% CI ≤ 500 yr wide", sum(1 for s in p2["sites"] if s["quality"] != "Unmodeled" and s["direct_on_proxies"] and s["ci95_width"] <= 500), "var(--copper)"),
        ("Direct date + 95% CI ≤ 300 yr wide", p2["n_tight_direct_le300"], "var(--verdigris)"),
    ]
    W, H = 720, 215
    left, right = 278, 668
    bar_max = right - left
    svg_parts = [
        f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="Funnel from 32 claimed YDB sites down to 4 sites with direct tight dating" xmlns="http://www.w3.org/2000/svg">'
    ]
    for i, (label, count, col) in enumerate(stages):
        y = 22 + i * 36
        bw = (count / 32.0) * bar_max
        pct = 100.0 * count / 32.0
        svg_parts.append(f'<text x="{left - 10}" y="{y + 15}" text-anchor="end" fill="var(--ink)" font-family="var(--sans)" font-size="12">{esc(label)}</text>')
        svg_parts.append(f'<rect x="{left}" y="{y}" width="{bar_max:.1f}" height="22" rx="2" fill="var(--paper-deep)"/>')
        svg_parts.append(f'<rect x="{left}" y="{y}" width="{bw:.1f}" height="22" rx="2" fill="{col}" opacity="0.82"/>')
        svg_parts.append(f'<text x="{left + bw + 8:.1f}" y="{y + 15}" fill="var(--ink)" font-family="var(--mono)" font-size="11.5" font-weight="600">{count}/32 ({pct:.1f}%)</text>')
    svg_parts.append("</svg>")
    html_doc = (
        '<figure class="fig" aria-label="Precision funnel across all 32 claimed YDB sites">\n'
        '<div class="fig-scroll">\n'
        + "\n".join(svg_parts)
        + '\n</div>\n'
        '<figcaption>Chronological precision funnel across all 32 claimed YDB sites in Kennett et al. (2015, Fig. 2). Nine sites cannot be modeled at all; 13 modeled sites rely on indirect or interpolated age models rather than dates on the proxy layer itself; only 4 of 32 sites (12.5% — Abu Hureyra, Arlington Canyon, Aalsterhut, and Bull Creek) combine a direct date on the proxy layer with a modeled 95% credible interval ≤ 300 yr wide.</figcaption>\n'
        '</figure>\n'
    )
    (FIG_DIR / "precision_funnel.html").write_text(html_doc, encoding="utf-8")


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    d = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    write_tiles(d)
    write_pillar1_calibration(d)
    write_simulation_benchmark(d)
    write_placebo_overlap(d)
    write_funnel_summary(d)
    print("Wrote figures:", sorted(p.name for p in FIG_DIR.iterdir()))


if __name__ == "__main__":
    main()
