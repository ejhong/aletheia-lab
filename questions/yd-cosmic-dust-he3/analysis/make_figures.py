#!/usr/bin/env python3
"""
Generate interactive HTML figures for Issue #121 (yd-cosmic-dust-he3) from results files.
Outputs into site/figures/yd-cosmic-dust-he3/*.html (standard library only).
"""

import csv
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
QDIR = ROOT / "questions" / "yd-cosmic-dust-he3"
RES = QDIR / "results"
OUT = ROOT / "site" / "figures" / "yd-cosmic-dust-he3"

esc = lambda s: html.escape(str(s), quote=True)


def write_fig(name: str, content: str):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{name}.html").write_text(content, encoding="utf-8")


def make_tiles(summary: dict):
    w1 = summary["pillar1_pooled_230Th_norm"]["W1_YD_13.5_11.5"]
    w3 = summary["pillar1_pooled_230Th_norm"]["W3_Broad_20_10"]
    pk = summary["pillar1_blind_peak_scan"]
    hits_w2 = pk["window_overlap"]["W2_Deglacial_15_10"]["top_hits_in_window"]
    k_top = pk["k_top_10pct"]
    v926 = summary["pillar0_positive_controls"]["Veritas_8.2Ma_ODP926B"]

    items = [
        (f"{w1['median_ratio']:.2f}×", f"Younger Dryas (13.5–11.5 ka) cosmic-dust flux vs. baseline (95% CI {w1['boot_ci95'][0]:.2f}–{w1['boot_ci95'][1]:.2f}×, p = {w1['p_perm_one_sided']:.2f})", False),
        (f"{w3['median_ratio']:.2f}×", f"Broad 20–10 ka Taurid breakup window vs. baseline (95% CI {w3['boot_ci95'][0]:.2f}–{w3['boot_ci95'][1]:.2f}×, p = {w3['p_perm_one_sided']:.3f})", False),
        (f"{hits_w2} / {k_top}", "top-10% cosmic-dust peaks falling inside 15–10 ka (100% outside the Younger Dryas & Bølling–Allerød)", False),
        (f"{v926['median_ratio']:.2f}×", f"real 8.2 Ma Veritas breakup positive control in Atlantic & Indian oceans (p ≤ 0.0005)", False),
    ]
    body = '<div class="tiles">\n' + "\n".join(
        f'<div class="tile"><p class="tile-value{" is-word" if w else ""}">{esc(v)}</p><p class="tile-label">{esc(l)}</p></div>'
        for v, l, w in items
    ) + "\n</div>\n"
    write_fig("tiles", body)


def make_positive_control_vs_yd(pos_rows: list, p1_rows: list, summary: dict):
    """Side-by-side interactive visual comparing Veritas 8.2 Ma real breakup vs Younger Dryas 27-0 ka on same fold-change y-axis."""
    def norm_veritas(core_name):
        pts = [(float(r["age_Ma"]), float(r["flux_pcc_cm2_kyr"])) for r in pos_rows if r["core"] == core_name and 6.2 <= float(r["age_Ma"]) <= 10.5]
        base = sorted(f for a, f in pts if not (7.5 <= a <= 8.35))
        med = base[len(base) // 2]
        return [{"a": round(a, 3), "y": round(f / med, 3), "inT": 7.5 <= a <= 8.35} for a, f in sorted(pts)]

    v926 = norm_veritas("ODP-926B")
    v757 = norm_veritas("ODP-757B")
    yd_pts = []
    for r in p1_rows:
        a = float(r["age_ka"])
        if 0 <= a <= 27.5:
            yd_pts.append({
                "a": round(a, 2),
                "y": round(float(r["flux_norm_core_median"]), 3),
                "c": r["core"],
                "inW1": 11.5 <= a <= 13.5,
                "inW2": 10.0 <= a <= 15.0,
            })

    payload = json.dumps({"v926": v926, "v757": v757, "yd": yd_pts})
    uid = "he3pos"
    content = f'''<figure class="fig" aria-label="Real 8.2 Ma cosmic breakup dust shower compared to the Younger Dryas deglaciation on the same fold-change scale">
<div class="he3-ctrl" style="display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-bottom:10px;font-size:13px;">
  <span style="color:var(--muted);font-weight:600;">Positive control ocean:</span>
  <button type="button" id="{uid}-b926" class="he3-btn is-on" style="padding:4px 10px;border:1px solid var(--copper);background:var(--copper);color:#fff;border-radius:4px;cursor:pointer;font-size:12px;">Atlantic ODP 926B (2.31×, p=0.0001)</button>
  <button type="button" id="{uid}-b757" class="he3-btn" style="padding:4px 10px;border:1px solid var(--rule);background:transparent;color:var(--ink);border-radius:4px;cursor:pointer;font-size:12px;">Indian ODP 757B (2.28×, p=0.0005)</button>
</div>
<div class="fig-scroll">
<svg id="{uid}-svg" class="chart" viewBox="0 0 740 310" role="img" aria-label="Two-panel comparison of Veritas 8.2 Ma 3He_ET dust shower versus Younger Dryas 3He_ET flux" xmlns="http://www.w3.org/2000/svg"></svg>
</div>
<figcaption>Left: a real cosmic breakup dust shower — the 8.2 Ma Veritas asteroid-family disruption (Farley et al. 2006) — drives extraterrestrial ³He flux more than twofold above baseline across two independent oceans (shaded band = 8.35–7.50 Ma). Right: across seven ²³⁰Th-normalized Pacific pelagic cores spanning 27–0 ka on the exact same fold-change axis, the Younger Dryas (13.5–11.5 ka, darker band; 15–10 ka, lighter band) stays flat or slightly below baseline (0.92× and 0.84×). Points above 4.2× are clipped at the top border with triangles.</figcaption>
</figure>
<script>
(function() {{
  var DATA = {payload};
  var svg = document.getElementById("{uid}-svg");
  var b926 = document.getElementById("{uid}-b926");
  var b757 = document.getElementById("{uid}-b757");
  var NS = "http://www.w3.org/2000/svg";
  function el(tag, attrs, text) {{
    var n = document.createElementNS(NS, tag);
    for (var k in attrs) n.setAttribute(k, attrs[k]);
    if (text !== undefined) n.textContent = text;
    return n;
  }}
  function render(which) {{
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    var vPts = which === "926" ? DATA.v926 : DATA.v757;
    var YMAX = 4.2;
    var top = 36, bot = 258;
    function sy(v) {{ return bot - Math.min(v, YMAX) / YMAX * (bot - top); }}
    // Y grid & labels
    [0, 1, 2, 3, 4].forEach(function(g) {{
      var y = sy(g);
      svg.appendChild(el("line", {{x1: 48, x2: 342, y1: y, y2: y, stroke: g === 1 ? "var(--ink)" : "var(--rule)", "stroke-dasharray": g === 1 ? "4 3" : "", "stroke-width": g === 1 ? "1.2" : "0.7", opacity: g === 1 ? "0.55" : "0.6"}}));
      svg.appendChild(el("line", {{x1: 416, x2: 722, y1: y, y2: y, stroke: g === 1 ? "var(--ink)" : "var(--rule)", "stroke-dasharray": g === 1 ? "4 3" : "", "stroke-width": g === 1 ? "1.2" : "0.7", opacity: g === 1 ? "0.55" : "0.6"}}));
      svg.appendChild(el("text", {{x: 42, y: y + 4, "text-anchor": "end", class: "c-tick"}}, g + "×"));
      svg.appendChild(el("text", {{x: 410, y: y + 4, "text-anchor": "end", class: "c-tick"}}, g + "×"));
    }});
    svg.appendChild(el("text", {{x: 14, y: (top + bot) / 2, transform: "rotate(-90 14 " + ((top + bot) / 2) + ")", "text-anchor": "middle", class: "c-axis"}}, "³He_ET flux / baseline median"));

    // Panel 1: Veritas (10.5 -> 6.2 Ma, older on left)
    var L1 = 48, R1 = 342;
    function sx1(a) {{ return L1 + (10.5 - a) / (10.5 - 6.2) * (R1 - L1); }}
    svg.appendChild(el("rect", {{x: sx1(8.35), y: top, width: sx1(7.50) - sx1(8.35), height: bot - top, fill: "var(--copper)", opacity: "0.18"}}));
    svg.appendChild(el("text", {{x: (L1 + R1) / 2, y: 18, "text-anchor": "middle", class: "c-group"}}, "Positive Control: Veritas Breakup (" + (which === "926" ? "ODP 926B" : "ODP 757B") + ")"));
    svg.appendChild(el("text", {{x: (sx1(8.35) + sx1(7.50)) / 2, y: top + 14, "text-anchor": "middle", class: "c-label-sm", fill: "var(--copper)"}}, "8.2 Ma shower"));
    // Draw line connecting sorted points
    var path1 = vPts.map(function(p, i) {{ return (i ? "L" : "M") + sx1(p.a).toFixed(1) + "," + sy(p.y).toFixed(1); }}).join(" ");
    svg.appendChild(el("path", {{d: path1, fill: "none", stroke: "var(--copper)", "stroke-width": "1.6", opacity: "0.75"}}));
    vPts.forEach(function(p) {{
      var cx = sx1(p.a), cy = sy(p.y);
      var tip = (which === "926" ? "ODP 926B" : "ODP 757B") + " · " + p.a + " Ma|" + p.y.toFixed(2) + "× baseline";
      var g = el("g", {{class: "c-mark", tabindex: "0", "data-tip": tip}});
      if (p.y > YMAX) {{
        g.appendChild(el("polygon", {{points: (cx-4)+","+(top+6)+" "+(cx+4)+","+(top+6)+" "+cx+","+top, fill: "var(--copper)"}}));
      }} else {{
        g.appendChild(el("circle", {{cx: cx, cy: cy, r: p.inT ? "3.6" : "2.7", fill: p.inT ? "var(--copper)" : "var(--faint)", stroke: "#fff", "stroke-width": "0.6"}}));
      }}
      svg.appendChild(g);
    }});
    [10, 9, 8, 7].forEach(function(t) {{
      svg.appendChild(el("text", {{x: sx1(t), y: bot + 16, "text-anchor": "middle", class: "c-tick"}}, t + " Ma"));
    }});
    svg.appendChild(el("text", {{x: (L1 + R1) / 2, y: 294, "text-anchor": "middle", class: "c-axis"}}, "Age (Ma, older → younger)"));

    // Panel 2: Younger Dryas (27 -> 0 ka, older on left)
    var L2 = 416, R2 = 722;
    function sx2(a) {{ return L2 + (27.5 - a) / 27.5 * (R2 - L2); }}
    svg.appendChild(el("rect", {{x: sx2(15.0), y: top, width: sx2(10.0) - sx2(15.0), height: bot - top, fill: "var(--copper)", opacity: "0.09"}}));
    svg.appendChild(el("rect", {{x: sx2(13.5), y: top, width: sx2(11.5) - sx2(13.5), height: bot - top, fill: "var(--copper)", opacity: "0.22"}}));
    svg.appendChild(el("text", {{x: (L2 + R2) / 2, y: 18, "text-anchor": "middle", class: "c-group"}}, "Younger Dryas & Deglaciation (7 Pacific Cores)"));
    svg.appendChild(el("text", {{x: sx2(12.5), y: top + 14, "text-anchor": "middle", class: "c-label-sm", fill: "var(--copper)"}}, "YD (13.5–11.5 ka)"));

    // 2-kyr median curve
    var bins = [];
    for (var b = 1; b <= 26; b += 2) {{
      var vals = DATA.yd.filter(function(p) {{ return p.a >= b - 1 && p.a < b + 1; }}).map(function(p) {{ return p.y; }}).sort(function(x, y) {{ return x - y; }});
      if (vals.length >= 2) bins.push({{a: b, y: vals[Math.floor(vals.length / 2)]}});
    }}
    bins.sort(function(x, y) {{ return y.a - x.a; }});
    var path2 = bins.map(function(p, i) {{ return (i ? "L" : "M") + sx2(p.a).toFixed(1) + "," + sy(p.y).toFixed(1); }}).join(" ");
    svg.appendChild(el("path", {{d: path2, fill: "none", stroke: "var(--ink)", "stroke-width": "2.2"}}));

    DATA.yd.forEach(function(p) {{
      var cx = sx2(p.a), cy = sy(p.y);
      var tip = p.c + " · " + p.a + " ka BP|" + p.y.toFixed(2) + "× core median";
      var g = el("g", {{class: "c-mark", tabindex: "0", "data-tip": tip}});
      if (p.y > YMAX) {{
        g.appendChild(el("polygon", {{points: (cx-4)+","+(top+6)+" "+(cx+4)+","+(top+6)+" "+cx+","+top, fill: "var(--faint)"}}));
      }} else {{
        g.appendChild(el("circle", {{cx: cx, cy: cy, r: p.inW1 ? "3.6" : "2.6", fill: p.inW1 ? "var(--copper)" : (p.inW2 ? "#8c5d3c" : "var(--faint)"), opacity: p.inW1 ? "0.95" : "0.7", stroke: "#fff", "stroke-width": "0.5"}}));
      }}
      svg.appendChild(g);
    }});
    [25, 20, 15, 10, 5, 0].forEach(function(t) {{
      svg.appendChild(el("text", {{x: sx2(t), y: bot + 16, "text-anchor": "middle", class: "c-tick"}}, t + " ka"));
    }});
    svg.appendChild(el("text", {{x: (L2 + R2) / 2, y: 294, "text-anchor": "middle", class: "c-axis"}}, "Age (ka BP, older → younger)"));
  }}
  b926.addEventListener("click", function() {{
    b926.style.background = "var(--copper)"; b926.style.color = "#fff"; b926.style.borderColor = "var(--copper)";
    b757.style.background = "transparent"; b757.style.color = "var(--ink)"; b757.style.borderColor = "var(--rule)";
    render("926");
  }});
  b757.addEventListener("click", function() {{
    b757.style.background = "var(--copper)"; b757.style.color = "#fff"; b757.style.borderColor = "var(--copper)";
    b926.style.background = "transparent"; b926.style.color = "var(--ink)"; b926.style.borderColor = "var(--rule)";
    render("757");
  }});
  render("926");
}})();
</script>
'''
    write_fig("positive_control", content)


def make_deglacial_timeseries(p1_rows: list, p2_rows: list, summary: dict):
    """Interactive 28-0 ka explorer toggling across Pacific pooled, Subarctic North Pacific, Cocos Ridge, and Mid-Atlantic Ridge."""
    serno_pts = [
        {"a": round(float(r["age_ka"]), 2), "y": round(float(r["flux_pcc_cm2_kyr"]), 3), "yn": round(float(r["flux_norm_core_median"]), 3), "c": r["core"]}
        for r in p1_rows if r["core"] == "SO202-07-6"
    ]
    cocos_pts = [
        {"a": round(float(r["age_ka"]), 2), "y": round(float(r["flux_pcc_cm2_kyr"]), 3), "yn": round(float(r["flux_norm_core_median"]), 3), "c": r["core"]}
        for r in p1_rows if r["core"].startswith("CR")
    ]
    all_pac = [
        {"a": round(float(r["age_ka"]), 2), "y": round(float(r["flux_pcc_cm2_kyr"]), 3), "yn": round(float(r["flux_norm_core_median"]), 3), "c": r["core"]}
        for r in p1_rows if float(r["age_ka"]) <= 28.0
    ]
    # Normalize Atlantic by core median
    atl_by_c = {}
    for r in p2_rows:
        atl_by_c.setdefault(r["core"], []).append(float(r["rel_burial_flux"]))
    atl_med = {c: sorted(v)[len(v)//2] for c, v in atl_by_c.items()}
    atl_pts = [
        {"a": round(float(r["age_ka"]), 2), "y": round(float(r["rel_burial_flux"]) / atl_med[r["core"]], 3), "yn": round(float(r["rel_burial_flux"]) / atl_med[r["core"]], 3), "c": r["core"]}
        for r in p2_rows if float(r["age_ka"]) <= 28.0
    ]

    ice_med = summary["polar_ice_reference_brook2000"]["all_median_pcc_cm2_kyr"]
    payload = json.dumps({"all": all_pac, "serno": serno_pts, "cocos": cocos_pts, "atl": atl_pts, "ice": ice_med})
    uid = "he3ts"
    content = f'''<figure class="fig" aria-label="Interactive deglacial extraterrestrial 3He flux across North Pacific, Equatorial Pacific, and North Atlantic cores">
<div style="display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin-bottom:10px;font-size:12px;">
  <span style="color:var(--muted);font-weight:600;margin-right:4px;">Record:</span>
  <button type="button" data-k="all" class="{uid}-b" style="padding:4px 9px;border:1px solid var(--copper);background:var(--copper);color:#fff;border-radius:4px;cursor:pointer;font-size:12px;">All 7 Pacific cores (²³⁰Th-norm)</button>
  <button type="button" data-k="serno" class="{uid}-b" style="padding:4px 9px;border:1px solid var(--rule);background:transparent;color:var(--ink);border-radius:4px;cursor:pointer;font-size:12px;">North Pacific SO202-07-6 (n=51)</button>
  <button type="button" data-k="cocos" class="{uid}-b" style="padding:4px 9px;border:1px solid var(--rule);background:transparent;color:var(--ink);border-radius:4px;cursor:pointer;font-size:12px;">Cocos Ridge CR01–CR05 (n=73)</button>
  <button type="button" data-k="atl" class="{uid}-b" style="padding:4px 9px;border:1px solid var(--rule);background:transparent;color:var(--ink);border-radius:4px;cursor:pointer;font-size:12px;">Mid-Atlantic Ridge GGC3+GGC6 (n=40)</button>
</div>
<div class="fig-scroll">
<svg id="{uid}-svg" class="chart" viewBox="0 0 740 315" role="img" aria-label="Time series of extraterrestrial 3He flux from 28 to 0 ka BP" xmlns="http://www.w3.org/2000/svg"></svg>
</div>
<figcaption>Extraterrestrial ³He flux from 28 to 0 ka BP across three ocean regions and three independent noble-gas laboratories. Dark shaded band: narrow Younger Dryas window (13.5–11.5 ka); medium band: full Late Deglaciation (15–10 ka); light band: broad Taurid breakup window (20–10 ka). Dashed green line marks the polar ice-core absolute reference median (Brook et al. 2000, Vostok + GISP2 = {ice_med:.2f} pcc cm⁻² kyr⁻¹) on raw-flux views, or 1.0× baseline on normalized views. Switch tabs to inspect each ocean basin individually; hover or focus points for exact ages and fluxes.</figcaption>
</figure>
<script>
(function() {{
  var DATA = {payload};
  var svg = document.getElementById("{uid}-svg");
  var btns = document.querySelectorAll(".{uid}-b");
  var NS = "http://www.w3.org/2000/svg";
  function el(tag, attrs, text) {{
    var n = document.createElementNS(NS, tag);
    for (var k in attrs) n.setAttribute(k, attrs[k]);
    if (text !== undefined) n.textContent = text;
    return n;
  }}
  var META = {{
    all: {{title: "All 7 Pacific Pelagic Cores (²³⁰Th-normalized, core-median scaled)", ylab: "Flux / core baseline median", norm: true, ymax: 3.5, unit: "× baseline"}},
    serno: {{title: "Subarctic North Pacific SO202-07-6 (Serno et al. 2015, 20 ¹⁴C dates in YD)", ylab: "³He_ET flux (pcc cm⁻² kyr⁻¹)", norm: false, ymax: 2.5, unit: " pcc cm⁻² kyr⁻¹"}},
    cocos: {{title: "Eastern Equatorial Pacific Cocos Ridge CR01–CR05 (Tomchovska, Pavia & Farley)", ylab: "³He_ET flux (pcc cm⁻² kyr⁻¹)", norm: false, ymax: 2.0, unit: " pcc cm⁻² kyr⁻¹"}},
    atl: {{title: "Mid-Atlantic Ridge KN207-2-GGC3 & GGC6 (Middleton et al. 2018, bulk burial)", ylab: "Relative bulk ³He_ET burial / core median", norm: true, ymax: 3.0, unit: "× baseline"}}
  }};
  function render(key) {{
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    var m = META[key];
    var pts = DATA[key];
    var L = 62, R = 716, T = 36, B = 258;
    function sx(a) {{ return L + (28.0 - a) / 28.0 * (R - L); }}
    function sy(v) {{ return B - Math.min(v, m.ymax) / m.ymax * (B - T); }}

    // Window shading
    svg.appendChild(el("rect", {{x: sx(20.0), y: T, width: sx(10.0) - sx(20.0), height: B - T, fill: "var(--faint)", opacity: "0.10"}}));
    svg.appendChild(el("rect", {{x: sx(15.0), y: T, width: sx(10.0) - sx(15.0), height: B - T, fill: "var(--copper)", opacity: "0.10"}}));
    svg.appendChild(el("rect", {{x: sx(13.5), y: T, width: sx(11.5) - sx(13.5), height: B - T, fill: "var(--copper)", opacity: "0.22"}}));
    svg.appendChild(el("text", {{x: (L + R) / 2, y: 18, "text-anchor": "middle", class: "c-group"}}, m.title));
    svg.appendChild(el("text", {{x: sx(12.5), y: T + 13, "text-anchor": "middle", class: "c-label-sm", fill: "var(--copper)"}}, "YD"));
    svg.appendChild(el("text", {{x: sx(17.5), y: T + 13, "text-anchor": "middle", class: "c-sub"}}, "20–10 ka"));

    // Y grid
    var steps = m.ymax <= 2.0 ? [0, 0.5, 1.0, 1.5, 2.0] : (m.ymax <= 2.5 ? [0, 0.5, 1.0, 1.5, 2.0, 2.5] : [0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5]);
    steps.forEach(function(g) {{
      if (g > m.ymax) return;
      var y = sy(g);
      svg.appendChild(el("line", {{x1: L, x2: R, y1: y, y2: y, stroke: "var(--rule)", "stroke-width": "0.7", opacity: "0.7"}}));
      svg.appendChild(el("text", {{x: L - 8, y: y + 4, "text-anchor": "end", class: "c-tick"}}, m.norm ? g.toFixed(1) + "×" : g.toFixed(1)));
    }});

    // Reference line (1.0x or polar ice core median)
    var refY = m.norm ? 1.0 : DATA.ice;
    svg.appendChild(el("line", {{x1: L, x2: R, y1: sy(refY), y2: sy(refY), stroke: m.norm ? "var(--ink)" : "#2f7a58", "stroke-dasharray": "5 4", "stroke-width": "1.4", opacity: "0.75"}}));
    svg.appendChild(el("text", {{x: R - 4, y: sy(refY) - 5, "text-anchor": "end", class: "c-sub", fill: m.norm ? "var(--ink)" : "#2f7a58"}}, m.norm ? "1.0× baseline" : "Polar ice median (" + DATA.ice.toFixed(2) + ")"));

    // 2-kyr binned median line
    var bins = [];
    for (var b = 1; b <= 27; b += 2) {{
      var vs = pts.filter(function(p) {{ return p.a >= b - 1 && p.a < b + 1; }}).map(function(p) {{ return m.norm ? p.yn : p.y; }}).sort(function(x, y) {{ return x - y; }});
      if (vs.length >= 2) bins.push({{a: b, v: vs[Math.floor(vs.length / 2)]}});
    }}
    bins.sort(function(x, y) {{ return y.a - x.a; }});
    if (bins.length >= 2) {{
      var d = bins.map(function(p, i) {{ return (i ? "L" : "M") + sx(p.a).toFixed(1) + "," + sy(p.v).toFixed(1); }}).join(" ");
      svg.appendChild(el("path", {{d: d, fill: "none", stroke: "var(--ink)", "stroke-width": "2.1"}}));
    }}

    // Points
    pts.forEach(function(p) {{
      var v = m.norm ? p.yn : p.y;
      var cx = sx(p.a), cy = sy(v);
      var inYD = p.a >= 11.5 && p.a <= 13.5;
      var inW2 = p.a >= 10.0 && p.a <= 15.0;
      var tip = p.c + " · " + p.a.toFixed(2) + " ka BP|" + v.toFixed(2) + m.unit;
      var g = el("g", {{class: "c-mark", tabindex: "0", "data-tip": tip}});
      if (v > m.ymax) {{
        g.appendChild(el("polygon", {{points: (cx-4)+","+(T+6)+" "+(cx+4)+","+(T+6)+" "+cx+","+T, fill: "var(--faint)"}}));
      }} else {{
        g.appendChild(el("circle", {{cx: cx, cy: cy, r: inYD ? "4.0" : "3.0", fill: inYD ? "var(--copper)" : (inW2 ? "#8c5d3c" : "#4b6b8a"), opacity: inYD ? "0.95" : "0.72", stroke: "#fff", "stroke-width": "0.6"}}));
      }}
      svg.appendChild(g);
    }});

    [25, 20, 15, 13, 11.5, 10, 5, 0].forEach(function(t) {{
      if (t === 13 || t === 11.5) return;
      svg.appendChild(el("text", {{x: sx(t), y: B + 16, "text-anchor": "middle", class: "c-tick"}}, t + " ka"));
    }});
    svg.appendChild(el("text", {{x: (L + R) / 2, y: 298, "text-anchor": "middle", class: "c-axis"}}, "Calendar age (ka BP, older → younger)"));
    svg.appendChild(el("text", {{x: 16, y: (T + B) / 2, transform: "rotate(-90 16 " + ((T + B) / 2) + ")", "text-anchor": "middle", class: "c-axis"}}, m.ylab));
  }}
  btns.forEach(function(b) {{
    b.addEventListener("click", function() {{
      btns.forEach(function(x) {{ x.style.background = "transparent"; x.style.color = "var(--ink)"; x.style.borderColor = "var(--rule)"; }});
      b.style.background = "var(--copper)"; b.style.color = "#fff"; b.style.borderColor = "var(--copper)";
      render(b.getAttribute("data-k"));
    }});
  }});
  render("all");
}})();
</script>
'''
    write_fig("deglacial_timeseries", content)


def make_window_forest(summary: dict):
    """Forest plot comparing median flux ratios + 95% CIs across Positive Controls, Pillar 1 Pacific, and Pillar 2 Atlantic."""
    rows = [
        ("POSITIVE CONTROLS (Farley et al. 2006)", None),
        ("Veritas 8.2 Ma · Atlantic ODP 926B", summary["pillar0_positive_controls"]["Veritas_8.2Ma_ODP926B"], "pos"),
        ("Veritas 8.2 Ma · Indian ODP 757B", summary["pillar0_positive_controls"]["Veritas_8.2Ma_ODP757B"], "pos"),
        ("Late Eocene 35.5 Ma · ODP 757B (pre-reg baseline)", summary["pillar0_positive_controls"]["LateEocene_35.5Ma_ODP757B"], "warn"),
        ("PILLAR 1: POOLED 7 PACIFIC CORES (²³⁰Th-normalized)", None),
        ("W1: Younger Dryas (13.5–11.5 ka)", summary["pillar1_pooled_230Th_norm"]["W1_YD_13.5_11.5"], "p1"),
        ("W2: Late Deglacial (15.0–10.0 ka)", summary["pillar1_pooled_230Th_norm"]["W2_Deglacial_15_10"], "p1"),
        ("W3: Broad Taurid (20.0–10.0 ka)", summary["pillar1_pooled_230Th_norm"]["W3_Broad_20_10"], "p1"),
        ("W3 vs. Holocene (<10 ka) only", summary["pillar1_W3_vs_Holocene_only"], "p1sub"),
        ("W3 vs. Glacial (>20 ka) only", summary["pillar1_W3_vs_Glacial_only"], "p1sub"),
        ("BY REGION & ATLANTIC REPLICATION", None),
        ("Subarctic N. Pacific SO202-07-6 · W1 (13.5–11.5 ka)", summary["pillar1_serno_SO202_07_6"]["W1_YD_13.5_11.5"], "reg"),
        ("Subarctic N. Pacific SO202-07-6 · W2 (15–10 ka)", summary["pillar1_serno_SO202_07_6"]["W2_Deglacial_15_10"], "reg"),
        ("Eq. Pacific Cocos Ridge CR01–05 · W2 (15–10 ka)", summary["pillar1_cocos_ridge_CR01_CR05"]["W2_Deglacial_15_10"], "reg"),
        ("Eq. Pacific Cocos Ridge CR01–05 · W3 (20–10 ka)", summary["pillar1_cocos_ridge_CR01_CR05"]["W3_Broad_20_10"], "reg"),
        ("Mid-Atlantic Ridge GGC3+GGC6 · W1 (burial)", summary["pillar2_atlantic_burial"]["W1_YD_13.5_11.5"], "atl"),
        ("Mid-Atlantic Ridge GGC3+GGC6 · W2 (burial)", summary["pillar2_atlantic_burial"]["W2_Deglacial_15_10"], "atl"),
        ("Mid-Atlantic Ridge GGC3+GGC6 · W3 (burial)", summary["pillar2_atlantic_burial"]["W3_Broad_20_10"], "atl"),
    ]

    W = 740
    L = 290
    R = 640
    row_h = 24
    top = 30
    H = top + len(rows) * row_h + 44
    XMAX = 4.0
    sx = lambda v: L + min(v, XMAX) / XMAX * (R - L)

    o = [f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="Forest plot of 3He_ET flux ratios and 95 percent confidence intervals across positive controls and Younger Dryas windows" xmlns="http://www.w3.org/2000/svg">']
    # Vertical reference lines
    for xval, col, dash, lbl in [(1.0, "var(--ink)", "4 3", "1.0× (flat)"), (1.5, "var(--copper)", "2 3", "1.5× threshold"), (2.0, "#2f7a58", "2 3", "2.0× pos ctrl")]:
        x = sx(xval)
        o.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{top - 6}" y2="{H - 34}" stroke="{col}" stroke-dasharray="{dash}" stroke-width="1.1" opacity="0.65"/>')
        o.append(f'<text x="{x:.1f}" y="{top - 12}" text-anchor="middle" class="c-sub" fill="{col}">{lbl}</text>')

    colors = {"pos": "#2f7a58", "warn": "#a07a2c", "p1": "var(--copper)", "p1sub": "#8c5d3c", "reg": "#4b6b8a", "atl": "#6b5b8a"}
    for i, item in enumerate(rows):
        y = top + i * row_h + 14
        if item[1] is None:
            o.append(f'<text x="0" y="{y + 2}" class="c-label-sm" fill="var(--muted)">{esc(item[0])}</text>')
            o.append(f'<line x1="0" x2="{W}" y1="{y + 7}" y2="{y + 7}" stroke="var(--rule)" stroke-width="0.6"/>')
            continue
        label, d, kind = item
        med = d["median_ratio"]
        lo, hi = d["boot_ci95"]
        p1s = d["p_perm_one_sided"]
        col = colors[kind]
        tip = esc(f"{label}|Median ratio {med:.2f}× (95% CI {lo:.2f}–{hi:.2f}×), one-sided p = {p1s:.4f}, n = {d['n_target']}/{d['n_baseline']}")
        o.append(f'<g class="c-mark" tabindex="0" data-tip="{tip}">')
        o.append(f'<rect x="0" y="{y - 10}" width="{W}" height="{row_h - 2}" fill="transparent"/>')
        o.append(f'<text x="{L - 8}" y="{y + 3}" text-anchor="end" class="c-sub" fill="var(--ink)">{esc(label)}</text>')
        o.append(f'<line x1="{sx(lo):.1f}" x2="{sx(hi):.1f}" y1="{y}" y2="{y}" stroke="{col}" stroke-width="2.4" stroke-linecap="round"/>')
        o.append(f'<circle cx="{sx(med):.1f}" cy="{y}" r="4.2" fill="{col}" stroke="#fff" stroke-width="0.9"/>')
        o.append(f'<text x="{R + 8}" y="{y + 3}" class="c-tick" fill="var(--ink)">{med:.2f}× [{lo:.2f}–{hi:.2f}]</text>')
        o.append('</g>')

    for t in [0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]:
        o.append(f'<text x="{sx(t):.1f}" y="{H - 18}" text-anchor="middle" class="c-tick">{t:.1f}×</text>')
    o.append(f'<text x="{(L + R) / 2:.1f}" y="{H - 2}" text-anchor="middle" class="c-axis">Median ³He_ET flux ratio (target window / within-core baseline) with bootstrap 95% CI</text>')
    o.append('</svg>')

    cap = (
        "Summary of median extraterrestrial ³He flux ratios and 10,000-resample bootstrap 95% confidence intervals across all pre-registered panels. "
        "Both Veritas 8.2 Ma breakup positive controls jump cleanly above 2.2× (green, p ≤ 0.0005), whereas every single Younger Dryas and deglacial window "
        "in both the Pacific (²³⁰Th-normalized) and Atlantic (bulk burial) sits at or below 1.0× — ruling out any sustained >1.22× Younger Dryas surge and any >0.97× late-deglacial surge at 95% confidence."
    )
    write_fig("window_forest", f'<figure class="fig" aria-label="Forest plot of 3He_ET flux ratios">\n<div class="fig-scroll">\n' + "\n".join(o) + f'\n</div>\n<figcaption>{cap}</figcaption>\n</figure>\n')


def main():
    summary = json.loads((RES / "summary.json").read_text(encoding="utf-8"))
    with open(RES / "positive_controls.csv", encoding="utf-8") as f:
        pos_rows = list(csv.DictReader(f))
    with open(RES / "pillar1_samples.csv", encoding="utf-8") as f:
        p1_rows = list(csv.DictReader(f))
    with open(RES / "pillar2_atlantic.csv", encoding="utf-8") as f:
        p2_rows = list(csv.DictReader(f))

    make_tiles(summary)
    make_positive_control_vs_yd(pos_rows, p1_rows, summary)
    make_deglacial_timeseries(p1_rows, p2_rows, summary)
    make_window_forest(summary)
    print("Generated figures in", OUT, ":", sorted(p.name for p in OUT.iterdir()))


if __name__ == "__main__":
    main()
