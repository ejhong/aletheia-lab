#!/usr/bin/env python3
"""Generate interactive HTML/SVG figures for yd-retracted-plos-audit (Issue #127).
Standard library only. Reads results/summary.json and results/pillar3_spherules_chem.csv.
"""
from __future__ import annotations

import csv
import html
import json
import math
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
RES = ROOT / "results"
OUT = ROOT.parent.parent / "site" / "figures" / "yd-retracted-plos-audit"
OUT.mkdir(parents=True, exist_ok=True)


def esc(s: object) -> str:
    return html.escape(str(s), quote=True)


def make_tiles(summary: dict) -> None:
    p1 = summary["pillar1_baffin_14c"]
    p3 = summary["pillar3_baffin_chem_and_citations"]
    p4 = summary["pillar4_shocked_quartz"]
    vc = p4["vertical_quartz_controls"]
    items = [
        ("4 / 4", "Baffin Bay cores shift off 12.8 ka under correct Marine20 + deglacial ΔR (SI Table S1 had −ΔR sign flip & terrestrial IntCal20)", False),
        (f"{p3['frac_raw_Fe_Ni_gt200_terrestrial']*100:.0f}%", "of Baffin Bay LA-ICP-MS microspherules (18/18) have terrestrial Fe/Ni > 200; pure Earth crust enters the 'comet' box under the ×100 formula", False),
        (f"{vc['pct_strata_analyzed']:.1f}%", f"of strata ({vc['total_strata_analyzed_for_quartz']}/{vc['total_strata_across_3_sites']}) checked for shocked quartz in Paper B (0 below YDB at Arlington Canyon; 1 above/below at Blackwater Draw)", False),
        ("Split verdict", "Baffin Bay retraction strongly supported (4/5 flaws verified); Shocked Quartz mixed/harsh (chronology & controls fail, microscopy unchallenged)", True),
    ]
    body = ['<div class="tiles">']
    for v, lbl, is_w in items:
        cls = "tile-value is-word" if is_w else "tile-value"
        body.append(f'<div class="tile"><p class="{cls}">{esc(v)}</p><p class="tile-label">{esc(lbl)}</p></div>')
    body.append("</div>\n")
    (OUT / "tiles.html").write_text("\n".join(body), encoding="utf-8")


def make_baffin_14c_figure(summary: dict) -> None:
    p1 = summary["pillar1_baffin_14c"]["per_core"]
    cores_data = []
    order = [
        ("52", "Core 52 (625–630 cm)", "IntCal20 bug (+608 yr)"),
        ("64", "Core 64 (312–318 cm)", "−ΔR sign flip (+417 yr)"),
        ("67", "Core 67 (32–35 cm)", "−ΔR sign flip (+414 yr)"),
        ("77", "Core 77 (161–162 cm)", "−ΔR sign flip (+297 yr)"),
    ]
    for cid, label, bug in order:
        cr = p1[cid]
        nd = cr["nearest_date_to_ydb"]
        scens = {}
        for sk in ("S0_Holocene_Pearce2023", "S1_Deglacial_plus200", "S2_Deglacial_plus500", "S3_Stadial_plus800"):
            v = cr["scenarios_nearest"][sk]
            scens[sk] = {
                "med": v["median_cal_bp"],
                "lo": v["hpd95"][0],
                "hi": v["hpd95"][1],
                "p_ydb": v["p_ydb_12900_12700"],
                "p_yd": v["p_yd_12900_11700"],
                "dr": v["delta_r"],
            }
        cores_data.append({
            "cid": cid,
            "label": label,
            "bug": bug,
            "lab": nd["lab_id"],
            "c14": nd["c14_age"],
            "err": nd["c14_err"],
            "si_mu": nd["si_table_s1_mu"],
            "scens": scens,
        })

    data_json = json.dumps(cores_data)
    html_out = f"""<figure class="fig" aria-label="Baffin Bay radiocarbon recalibration under Marine20 across Holocene and deglacial polar reservoir scenarios">
<div class="fig-controls" style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px;align-items:center">
  <span style="font-size:12px;color:var(--muted);margin-right:4px">Marine20 ΔR scenario:</span>
  <button type="button" class="b14c-btn is-on" data-scen="S0_Holocene_Pearce2023" style="font-size:12px;padding:4px 9px;border:1px solid var(--rule);border-radius:4px;background:var(--copper);color:#fff;cursor:pointer">S0: Holocene ΔR (exact Pearce 2023)</button>
  <button type="button" class="b14c-btn" data-scen="S1_Deglacial_plus200" style="font-size:12px;padding:4px 9px;border:1px solid var(--rule);border-radius:4px;background:transparent;color:var(--ink);cursor:pointer">S1: +200 yr deglacial</button>
  <button type="button" class="b14c-btn" data-scen="S2_Deglacial_plus500" style="font-size:12px;padding:4px 9px;border:1px solid var(--rule);border-radius:4px;background:transparent;color:var(--ink);cursor:pointer">S2: +500 yr sea-ice</button>
  <button type="button" class="b14c-btn" data-scen="S3_Stadial_plus800" style="font-size:12px;padding:4px 9px;border:1px solid var(--rule);border-radius:4px;background:transparent;color:var(--ink);cursor:pointer">S3: +800 yr stadial</button>
</div>
<div class="fig-scroll">
<svg id="b14c-svg" class="chart" viewBox="0 0 720 280" role="img" aria-label="Baffin Bay YDB calibrated ages vs Moore et al. SI Table S1" xmlns="http://www.w3.org/2000/svg"></svg>
</div>
<figcaption><strong>Baffin Bay radiocarbon sensitivity across all four cores.</strong> Hollow grey diamonds show the calibrated means reported in Moore et al. (2025) <em>SI Table S1</em>—inflated by +297 to +608 yr by a flipped &Delta;R sign in Cores 64, 67, and 77 and accidental use of terrestrial IntCal20 in Core 52. Solid copper dots and 95.4% HPD bars show exact <code>Marine20</code> recalibrations. Even under Holocene &Delta;R (S0), Core 52 (12,404 cal BP) and Core 77 (11,889 cal BP) miss the Younger Dryas onset (red band, 12,900–12,700 cal BP); under +500 yr (S2) all four cores have P(YDB onset) = 0.000, and under +800 yr (S3) all four fall younger than the entire Younger Dryas (11,700 cal BP).</figcaption>
<script>
(function(){{
  var DATA = {data_json};
  var svg = document.getElementById("b14c-svg");
  var btns = document.querySelectorAll(".b14c-btn");
  var XMIN = 10000, XMAX = 13600;
  var L = 168, R = 695, T = 36, B = 228;
  function sx(v){{ return L + (XMAX - v) / (XMAX - XMIN) * (R - L); }}
  function el(tag, attrs, txt){{
    var n = document.createElementNS("http://www.w3.org/2000/svg", tag);
    for (var k in attrs) n.setAttribute(k, attrs[k]);
    if (txt !== undefined) n.textContent = txt;
    return n;
  }}
  function render(scen){{
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    // Shaded YD (12900-11700) and narrow YDB onset (12900-12700)
    svg.appendChild(el("rect", {{x: sx(12900), y: T, width: sx(11700) - sx(12900), height: B - T, fill: "var(--faint)", opacity: "0.14"}}));
    svg.appendChild(el("rect", {{x: sx(12900), y: T, width: sx(12700) - sx(12900), height: B - T, fill: "var(--copper)", opacity: "0.22"}}));
    svg.appendChild(el("text", {{x: (sx(12900)+sx(12700))/2, y: T - 10, "text-anchor": "middle", class: "c-label-sm"}}, "YDB onset"));
    svg.appendChild(el("text", {{x: (sx(12700)+sx(11700))/2, y: T - 10, "text-anchor": "middle", class: "c-sub"}}, "Younger Dryas (12.9–11.7 ka)"));
    svg.appendChild(el("text", {{x: (sx(11700)+R)/2, y: T - 10, "text-anchor": "middle", class: "c-sub"}}, "Early Holocene"));
    for (var x = 13500; x >= 10000; x -= 500){{
      var px = sx(x);
      svg.appendChild(el("line", {{x1: px, x2: px, y1: T, y2: B, stroke: "var(--rule)", "stroke-dasharray": "2 4"}}));
      svg.appendChild(el("text", {{x: px, y: B + 16, "text-anchor": "middle", class: "c-tick"}}, (x/1000).toFixed(1) + " ka"));
    }}
    svg.appendChild(el("line", {{x1: L, x2: R, y1: B, y2: B, class: "c-zero"}}));
    var step = (B - T) / DATA.length;
    DATA.forEach(function(d, idx){{
      var y = T + (idx + 0.5) * step;
      var s = d.scens[scen];
      svg.appendChild(el("text", {{x: L - 10, y: y - 4, "text-anchor": "end", class: "c-group"}}, d.label));
      svg.appendChild(el("text", {{x: L - 10, y: y + 11, "text-anchor": "end", class: "c-sub"}}, d.lab + " (" + d.c14 + "±" + d.err + ")"));
      // Arrow from SI Table S1 to Marine20 recalibrated
      var xSi = sx(d.si_mu);
      var xRec = sx(s.med);
      svg.appendChild(el("line", {{x1: xSi, x2: xRec, y1: y, y2: y, stroke: "var(--faint)", "stroke-width": "1.2", "stroke-dasharray": "3 3"}}));
      // 95% HPD bar
      svg.appendChild(el("line", {{x1: sx(s.hi), x2: sx(s.lo), y1: y, y2: y, stroke: "var(--copper)", "stroke-width": "4", "stroke-linecap": "round", opacity: "0.45"}}));
      // Hollow diamond for Moore et al SI Table S1
      var pts = xSi + "," + (y-6) + " " + (xSi+6) + "," + y + " " + xSi + "," + (y+6) + " " + (xSi-6) + "," + y;
      svg.appendChild(el("polygon", {{points: pts, fill: "#fff", stroke: "var(--ink)", "stroke-width": "1.6"}}));
      // Solid dot for Marine20 recalibrated
      svg.appendChild(el("circle", {{cx: xRec, cy: y, r: "5.2", fill: "var(--copper)", stroke: "#fff", "stroke-width": "1.2"}}));
      var lblTxt = Math.round(s.med) + " BP (P_YDB=" + s.p_ydb.toFixed(2) + ")";
      var lblX = Math.min(R - 4, sx(s.lo) + 6);
      var anc = (sx(s.lo) + 120 > R) ? "end" : "start";
      svg.appendChild(el("text", {{x: anc === "end" ? sx(s.hi) - 6 : sx(s.lo) + 6, y: y + 4, "text-anchor": anc, class: "c-tick"}}, lblTxt));
    }});
    svg.appendChild(el("text", {{x: L, y: 266, class: "c-axis"}}, "Calibrated age (cal yr BP, older left to younger right). Hollow diamond = Moore et al. SI Table S1; copper dot/bar = exact Marine20 median & 95.4% HPD."));
  }}
  btns.forEach(function(b){{
    b.addEventListener("click", function(){{
      btns.forEach(function(x){{ x.classList.remove("is-on"); x.style.background = "transparent"; x.style.color = "var(--ink)"; }});
      b.classList.add("is-on"); b.style.background = "var(--copper)"; b.style.color = "#fff";
      render(b.getAttribute("data-scen"));
    }});
  }});
  render("S0_Holocene_Pearce2023");
}})();
</script>
</figure>
"""
    (OUT / "baffin_14c_sensitivity.html").write_text(html_out, encoding="utf-8")


def make_x100_math_figure(summary: dict) -> None:
    pts = []
    with open(RES / "pillar3_spherules_chem.csv", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            fc = float(r["raw_Fe_Cr"]) if r["raw_Fe_Cr"] else None
            fn = float(r["raw_Fe_Ni"]) if r["raw_Fe_Ni"] else None
            if fc and fn:
                pts.append({
                    "name": r["sample"],
                    "tbl": r["source_table"],
                    "raw_fc": fc,
                    "raw_fn": fn,
                    "x100_fc": float(r["moore_x100_Fe_Cr"]),
                    "x100_fn": float(r["moore_x100_Fe_Ni"]),
                })
    p3 = summary["pillar3_baffin_chem_and_citations"]
    controls = [
        {"name": "Pure Upper Continental Crust (0% cosmic)", "raw_fc": p3["pure_UCC_control"]["raw_Fe_Cr"], "raw_fn": p3["pure_UCC_control"]["raw_Fe_Ni"], "x100_fc": p3["pure_UCC_control"]["moore_x100_Fe_Cr"], "x100_fn": p3["pure_UCC_control"]["moore_x100_Fe_Ni"]},
        {"name": "Pure USGS Basalt BIR-1G (0% cosmic)", "raw_fc": p3["pure_BIR1G_basalt_control"]["raw_Fe_Cr"], "raw_fn": p3["pure_BIR1G_basalt_control"]["raw_Fe_Ni"], "x100_fc": p3["pure_BIR1G_basalt_control"]["moore_x100_Fe_Cr"], "x100_fn": p3["pure_BIR1G_basalt_control"]["moore_x100_Fe_Ni"]},
    ]
    payload = json.dumps({"spherules": pts, "controls": controls})
    html_out = f"""<figure class="fig" aria-label="Effect of Moore et al. 100x Ni and Cr multiplier on Baffin Bay microspherules and pure terrestrial rocks">
<div class="fig-controls" style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px;align-items:center">
  <span style="font-size:12px;color:var(--muted);margin-right:4px">View:</span>
  <button type="button" class="x100-btn is-on" data-mode="raw" style="font-size:12px;padding:4px 9px;border:1px solid var(--rule);border-radius:4px;background:var(--copper);color:#fff;cursor:pointer">Raw LA-ICP-MS measurements (0/18 cosmic)</button>
  <button type="button" class="x100-btn" data-mode="x100" style="font-size:12px;padding:4px 9px;border:1px solid var(--rule);border-radius:4px;background:transparent;color:var(--ink);cursor:pointer">After Moore et al. ×100 Ni &amp; Cr multiplier (16/18 + pure Earth crust!)</button>
</div>
<div class="fig-scroll">
<svg id="x100-svg" class="chart" viewBox="0 0 720 340" role="img" aria-label="Log-log scatter plot of Fe/Cr versus Fe/Ni" xmlns="http://www.w3.org/2000/svg"></svg>
</div>
<figcaption><strong>Why the &times;100 rescaling creates a false cosmic match.</strong> Measured raw (default view), all 18 Baffin Bay LA-ICP-MS microspherules (copper dots, <code>Table S8a/S8b</code>) sit squarely in the terrestrial crustal zone (100% have Fe/Ni &gt; 200; median Fe/Cr = 1,031, Fe/Ni = 1,556), far outside the chondrite / Comet Wild 2 field (shaded box, bottom left). Multiplying total Ni and Cr by 100&times; <em>without first subtracting 99% terrestrial crustal Ni and Cr</em> divides Fe/Cr and Fe/Ni by 100—mechanically pushing 16 of 18 spherules AND <strong>100% pure terrestrial Upper Continental Crust and USGS basalt BIR-1G (blue squares)</strong> straight into the cosmic box.</figcaption>
<script>
(function(){{
  var D = {payload};
  var svg = document.getElementById("x100-svg");
  var btns = document.querySelectorAll(".x100-btn");
  var L = 74, R = 690, T = 26, B = 286;
  var XLO = 0, XHI = 5, YLO = 0, YHI = 5; // log10(1) to log10(100,000)
  function sx(v){{ var lg = Math.log10(Math.max(1, v)); return L + (lg - XLO)/(XHI - XLO)*(R - L); }}
  function sy(v){{ var lg = Math.log10(Math.max(1, v)); return B - (lg - YLO)/(YHI - YLO)*(B - T); }}
  function el(tag, attrs, txt){{
    var n = document.createElementNS("http://www.w3.org/2000/svg", tag);
    for (var k in attrs) n.setAttribute(k, attrs[k]);
    if (txt !== undefined) n.textContent = txt;
    return n;
  }}
  function render(mode){{
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    // Cosmic box: Fe/Cr <= 150, Fe/Ni <= 80
    svg.appendChild(el("rect", {{x: sx(1), y: sy(80), width: sx(150)-sx(1), height: sy(1)-sy(80), fill: "var(--copper)", opacity: "0.14", stroke: "var(--copper)", "stroke-dasharray": "4 3"}}));
    svg.appendChild(el("text", {{x: sx(1.4), y: sy(60), class: "c-label-sm"}}, "Cosmic / Comet Wild 2 box"));
    // Terrestrial crustal zone: Fe/Cr > 200, Fe/Ni > 200
    svg.appendChild(el("rect", {{x: sx(200), y: sy(100000), width: sx(100000)-sx(200), height: sy(200)-sy(100000), fill: "var(--faint)", opacity: "0.10"}}));
    svg.appendChild(el("text", {{x: sx(260), y: sy(55000), class: "c-sub"}}, "Terrestrial crustal / oxide zone (Fe/Cr > 200, Fe/Ni > 200)"));
    // Grid ticks
    for (var p = 0; p <= 5; p++){{
      var v = Math.pow(10, p);
      var lbl = v >= 1000 ? (v/1000) + "k" : String(v);
      svg.appendChild(el("line", {{x1: sx(v), x2: sx(v), y1: T, y2: B, stroke: "var(--rule)", "stroke-dasharray": "2 4"}}));
      svg.appendChild(el("text", {{x: sx(v), y: B + 16, "text-anchor": "middle", class: "c-tick"}}, lbl));
      svg.appendChild(el("line", {{x1: L, x2: R, y1: sy(v), y2: sy(v), stroke: "var(--rule)", "stroke-dasharray": "2 4"}}));
      svg.appendChild(el("text", {{x: L - 8, y: sy(v) + 4, "text-anchor": "end", class: "c-tick"}}, lbl));
    }}
    svg.appendChild(el("line", {{x1: L, x2: R, y1: B, y2: B, class: "c-zero"}}));
    svg.appendChild(el("line", {{x1: L, x2: L, y1: T, y2: B, class: "c-zero"}}));
    // CI chondrite star reference (Fe/Cr=70, Fe/Ni=17)
    svg.appendChild(el("circle", {{cx: sx(70), cy: sy(17), r: "5.5", fill: "none", stroke: "var(--ink)", "stroke-width": "2"}}));
    svg.appendChild(el("text", {{x: sx(70)+8, y: sy(17)+4, class: "c-label-sm"}}, "CI Chondrite"));
    // Plot spherules
    D.spherules.forEach(function(pt){{
      var x = mode === "raw" ? sx(pt.raw_fc) : sx(pt.x100_fc);
      var y = mode === "raw" ? sy(pt.raw_fn) : sy(pt.x100_fn);
      if (mode === "x100"){{
        svg.appendChild(el("line", {{x1: sx(pt.raw_fc), y1: sy(pt.raw_fn), x2: x, y2: y, stroke: "var(--copper)", opacity: "0.22", "stroke-width": "1"}}));
      }}
      svg.appendChild(el("circle", {{cx: x, cy: y, r: "4.6", fill: "var(--copper)", stroke: "#fff", "stroke-width": "1"}}));
    }});
    // Plot 100% terrestrial controls
    D.controls.forEach(function(c, i){{
      var x = mode === "raw" ? sx(c.raw_fc) : sx(c.x100_fc);
      var y = mode === "raw" ? sy(c.raw_fn) : sy(c.x100_fn);
      if (mode === "x100"){{
        svg.appendChild(el("line", {{x1: sx(c.raw_fc), y1: sy(c.raw_fn), x2: x, y2: y, stroke: "#2b5c8f", "stroke-dasharray": "4 3", "stroke-width": "1.6"}}));
      }}
      svg.appendChild(el("rect", {{x: x-5.5, y: y-5.5, width: 11, height: 11, fill: "#2b5c8f", stroke: "#fff", "stroke-width": "1.2"}}));
      svg.appendChild(el("text", {{x: x + 9, y: y + (i === 0 ? -4 : 11), class: "c-tick", fill: "#2b5c8f"}}, c.name));
    }});
    svg.appendChild(el("text", {{x: (L+R)/2, y: 325, "text-anchor": "middle", class: "c-axis"}}, "Fe / Cr mass ratio (log scale)"));
    var yl = el("text", {{x: 18, y: (T+B)/2, "text-anchor": "middle", class: "c-axis", transform: "rotate(-90 18 " + ((T+B)/2) + ")"}}, "Fe / Ni mass ratio (log scale)");
    svg.appendChild(yl);
  }}
  btns.forEach(function(b){{
    b.addEventListener("click", function(){{
      btns.forEach(function(x){{ x.classList.remove("is-on"); x.style.background = "transparent"; x.style.color = "var(--ink)"; }});
      b.classList.add("is-on"); b.style.background = "var(--copper)"; b.style.color = "#fff";
      render(b.getAttribute("data-mode"));
    }});
  }});
  render("raw");
}})();
</script>
</figure>
"""
    (OUT / "baffin_x100_math.html").write_text(html_out, encoding="utf-8")


def make_quartz_audit_figure(summary: dict) -> None:
    p4 = summary["pillar4_shocked_quartz"]
    vc = p4["vertical_quartz_controls"]["per_site"]
    sites = [
        ("Arlington Canyon (Table S5)", vc["Arlington Canyon"]["total_strata"], vc["Arlington Canyon"]["n_above_analyzed"], 1, vc["Arlington Canyon"]["n_below_analyzed"]),
        ("Blackwater Draw (Table S6)", vc["Blackwater Draw"]["total_strata"], vc["Blackwater Draw"]["n_above_analyzed"], 1, vc["Blackwater Draw"]["n_below_analyzed"]),
        ("Murray Springs (Table S8)", vc["Murray Springs"]["total_strata"], vc["Murray Springs"]["n_above_analyzed"], 1, vc["Murray Springs"]["n_below_analyzed"]),
    ]
    ww_bars = [
        ("Authors' 3-date pick (uses 482.5 cm above ARL quartz)", p4["ward_wilson_authors_3_selected_cal"]["T"], p4["ward_wilson_authors_3_selected_cal"]["p_value"]),
        ("Swapping Arlington to actual 500.5 cm quartz horizon", p4["ward_wilson_3_using_actual_500cm_arlington"]["T"], p4["ward_wilson_3_using_actual_500cm_arlington"]["p_value"]),
        ("All 25 published direct dates across the 3 sites", p4["ward_wilson_all_25_published_direct_14c"]["T"], p4["ward_wilson_all_25_published_direct_14c"]["p_value"]),
    ]

    o = ['<svg class="chart" viewBox="0 0 720 315" role="img" aria-label="Shocked quartz vertical sampling coverage and radiocarbon synchrony test audit" xmlns="http://www.w3.org/2000/svg">']
    # Top panel: Vertical sampling coverage (13/66 strata)
    o.append('<text class="c-group" x="14" y="20">A. Vertical background sampling for shocked quartz (SI Tables S5, S6, S8)</text>')
    y0 = 42
    for i, (name, tot, abv, ydb, bel) in enumerate(sites):
        y = y0 + i * 34
        checked = abv + ydb + bel
        o.append(f'<text class="c-tick" x="188" y="{y+13}" text-anchor="end">{esc(name)}</text>')
        w_tot = 340.0
        w_chk = w_tot * (checked / tot)
        o.append(f'<rect x="198" y="{y}" width="{w_tot:.1f}" height="18" rx="3" fill="var(--faint)" opacity="0.22"/>')
        o.append(f'<rect x="198" y="{y}" width="{w_chk:.1f}" height="18" rx="3" fill="var(--copper)"/>')
        note = f"{checked}/{tot} strata ({100*checked/tot:.0f}%) — {abv} above, 1 YDB, {bel} below"
        if bel == 0:
            note += " (0 below!)"
        o.append(f'<text class="c-tick" x="546" y="{y+13}">{esc(note)}</text>')

    # Bottom panel: Ward-Wilson chi-square synchrony comparison
    o.append('<line x1="14" x2="706" y1="158" y2="158" stroke="var(--rule)"/>')
    o.append('<text class="c-group" x="14" y="180">B. Radiocarbon synchrony (&chi;&sup2; / Ward&ndash;Wilson T): selected vs. full site inventories</text>')
    y1 = 198
    max_t = 100.0
    for i, (label, tval, pval) in enumerate(ww_bars):
        y = y1 + i * 34
        o.append(f'<text class="c-tick" x="318" y="{y+13}" text-anchor="end">{esc(label)}</text>')
        bw = max(4.0, (min(tval, max_t) / max_t) * 260.0)
        col = "var(--copper)" if pval < 0.01 else "#2b5c8f"
        o.append(f'<rect x="328" y="{y}" width="{bw:.1f}" height="18" rx="3" fill="{col}" opacity="0.85"/>')
        p_str = "p < 1e-9" if pval < 1e-6 else f"p = {pval:.3f}"
        o.append(f'<text class="c-tick" x="{336 + bw:.1f}" y="{y+13}">T = {tval:.2f} ({p_str})</text>')
    o.append('<text class="c-axis" x="14" y="305">Panel A: fraction of stratigraphic rows analyzed for shocked quartz (13/66 total = 19.7%; zero control grain counts tabulated). Panel B: homogeneity statistic T (lower = more synchronous).</text>')
    o.append("</svg>")

    html_out = (
        '<figure class="fig" aria-label="Shocked quartz vertical background sampling and radiocarbon synchrony audit">\n'
        '<div class="fig-scroll">\n' + "\n".join(o) + "\n</div>\n"
        '<figcaption><strong>Paper B (Shocked Quartz, <code>e0319840</code>) audit of PLOS One&rsquo;s two retraction criteria.</strong> '
        '(A) Only 13 of 66 stratigraphic levels (19.7%) across the three sites were analyzed for shocked quartz; Arlington Canyon&rsquo;s YDB sample (<code>ARL-1B</code>, 501 cm) is the bottom row of Table S5 with zero underlying strata checked, and Blackwater Draw checked only one slide above and one below. '
        '(B) The paper&rsquo;s headline &chi;&sup2; = 0.057 (p = 0.97) used Arlington Canyon&rsquo;s 482.5 cm date (18.5 cm above the shocked quartz); swapping in the actual 500.5 cm date raises &chi;&sup2; 66-fold (4.21), and including all 25 published direct dates rejects single-year synchrony decisively (T = 90.94, p &lt; 10<sup>&minus;9</sup>). Crucially, PLOS One&rsquo;s notice raised no challenge to the quartz microscopy images themselves.</figcaption>\n'
        '</figure>\n'
    )
    (OUT / "quartz_audit.html").write_text(html_out, encoding="utf-8")


def main() -> None:
    summary = json.loads((RES / "summary.json").read_text(encoding="utf-8"))
    make_tiles(summary)
    make_baffin_14c_figure(summary)
    make_x100_math_figure(summary)
    make_quartz_audit_figure(summary)
    print("Generated figures in", OUT, ":", sorted(p.name for p in OUT.iterdir()))


if __name__ == "__main__":
    main()
