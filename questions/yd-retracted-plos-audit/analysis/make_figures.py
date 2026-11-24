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
    p4 = summary["pillar4_shocked_quartz"]
    vc = p4["vertical_quartz_controls"]
    n_checked, n_rows = vc['total_strata_analyzed_for_quartz'], vc['total_strata_across_3_sites']
    items = [
        ("300 to 610", "years: how much younger the four Baffin Bay dates on the claimed layer come out when calibrated the way the paper itself describes", False),
        ("16 of 17", "printed ages in three cores are what that method gives with the sign of the sea-water correction reversed", False),
        (f"{n_checked} of {n_rows}", "samples at the three quartz sites were examined for shocked quartz; none of the ten outside the layer has a count of the grains searched", False),
        ("Not tested", "whether the sixteen quartz grains are shocked quartz: neither the journal nor this study examined them", True),
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
        ("52", "Core 52 (625–630 cm)", "printed 608 years older"),
        ("64", "Core 64 (312–318 cm)", "printed 417 years older"),
        ("67", "Core 67 (32–35 cm)", "printed 414 years older"),
        ("77", "Core 77 (161–162 cm)", "printed 297 years older"),
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
  <span style="font-size:12px;color:var(--muted);margin-right:4px">Allowance for old sea water:</span>
  <button type="button" class="b14c-btn is-on" data-scen="S0_Holocene_Pearce2023" style="font-size:12px;padding:4px 9px;border:1px solid var(--rule);border-radius:4px;background:var(--copper);color:#fff;cursor:pointer">As the paper describes, nothing added</button>
  <button type="button" class="b14c-btn" data-scen="S1_Deglacial_plus200" style="font-size:12px;padding:4px 9px;border:1px solid var(--rule);border-radius:4px;background:transparent;color:var(--ink);cursor:pointer">+200 years for polar water</button>
  <button type="button" class="b14c-btn" data-scen="S2_Deglacial_plus500" style="font-size:12px;padding:4px 9px;border:1px solid var(--rule);border-radius:4px;background:transparent;color:var(--ink);cursor:pointer">+500 years (the test fixed in advance)</button>
  <button type="button" class="b14c-btn" data-scen="S3_Stadial_plus800" style="font-size:12px;padding:4px 9px;border:1px solid var(--rule);border-radius:4px;background:transparent;color:var(--ink);cursor:pointer">+800 years</button>
</div>
<div class="fig-scroll">
<svg id="b14c-svg" class="chart" viewBox="0 0 720 280" role="img" aria-label="Baffin Bay YDB calibrated ages vs Moore et al. SI Table S1" xmlns="http://www.w3.org/2000/svg"></svg>
</div>
<figcaption><strong>The four dates on the claimed layer, as printed and as the paper&rsquo;s stated method gives them.</strong> Hollow grey diamonds are the ages printed in the paper&rsquo;s table of dates (SI Table S1). Copper dots with bars are the same radiocarbon measurements calibrated on the marine curve (Marine20) with the paper&rsquo;s stated allowance for old sea water; bars span the 95% range. The buttons add larger allowances for polar water during the ice age, which are this study&rsquo;s own choices. The shaded band is the 200 years around the start of the Younger Dryas (12,900 to 12,700 years ago). With nothing added, two cores miss it altogether and two have between one chance in six and one in four; with 500 years added none can fall in it.</figcaption>
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
    svg.appendChild(el("text", {{x: (sx(12900)+sx(12700))/2, y: T - 10, "text-anchor": "middle", class: "c-label-sm"}}, "Onset"));
    svg.appendChild(el("text", {{x: (sx(12700)+sx(11700))/2, y: T - 10, "text-anchor": "middle", class: "c-sub"}}, "Younger Dryas"));
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
      var lblTxt = Math.round(s.med) + " (chance of the onset band " + s.p_ydb.toFixed(2) + ")";
      var lblX = Math.min(R - 4, sx(s.lo) + 6);
      var anc = (sx(s.lo) + 120 > R) ? "end" : "start";
      svg.appendChild(el("text", {{x: anc === "end" ? sx(s.hi) - 6 : sx(s.lo) + 6, y: y + 4, "text-anchor": anc, class: "c-tick"}}, lblTxt));
    }});
    svg.appendChild(el("text", {{x: L, y: 266, class: "c-axis"}}, "Age in years before 1950, older to the left. Diamond: as printed. Dot and bar: as the stated method gives."));
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
        {"name": "Average crust", "raw_fc": p3["pure_UCC_control"]["raw_Fe_Cr"], "raw_fn": p3["pure_UCC_control"]["raw_Fe_Ni"], "x100_fc": p3["pure_UCC_control"]["moore_x100_Fe_Cr"], "x100_fn": p3["pure_UCC_control"]["moore_x100_Fe_Ni"]},
        {"name": "Basalt standard", "raw_fc": p3["pure_BIR1G_basalt_control"]["raw_Fe_Cr"], "raw_fn": p3["pure_BIR1G_basalt_control"]["raw_Fe_Ni"], "x100_fc": p3["pure_BIR1G_basalt_control"]["moore_x100_Fe_Cr"], "x100_fn": p3["pure_BIR1G_basalt_control"]["moore_x100_Fe_Ni"]},
    ]
    payload = json.dumps({"spherules": pts, "controls": controls})
    html_out = f"""<figure class="fig" aria-label="Effect of Moore et al. 100x Ni and Cr multiplier on Baffin Bay microspherules and pure terrestrial rocks">
<div class="fig-controls" style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px;align-items:center">
  <span style="font-size:12px;color:var(--muted);margin-right:4px">View:</span>
  <button type="button" class="x100-btn is-on" data-mode="raw" style="font-size:12px;padding:4px 9px;border:1px solid var(--rule);border-radius:4px;background:var(--copper);color:#fff;cursor:pointer">As measured (0 of 18 in the comet field)</button>
  <button type="button" class="x100-btn" data-mode="x100" style="font-size:12px;padding:4px 9px;border:1px solid var(--rule);border-radius:4px;background:transparent;color:var(--ink);cursor:pointer">After multiplying nickel and chromium by 100 (16 of 18, and ordinary crust too)</button>
</div>
<div class="fig-scroll">
<svg id="x100-svg" class="chart" viewBox="0 0 720 340" role="img" aria-label="Log-log scatter plot of Fe/Cr versus Fe/Ni" xmlns="http://www.w3.org/2000/svg"></svg>
</div>
<figcaption><strong>What the paper&rsquo;s &ldquo;multiply by 100&rdquo; step does.</strong> Each copper dot is one of the 18 spherules whose chemistry was measured, placed by its ratio of iron to chromium and iron to nickel. As measured, all 18 sit with ordinary crust (iron to nickel above 200) and none is in the field of comet dust (shaded box, whose edges are our choice; the paper judges overlap by eye). The paper supposes each spherule is 1% cosmic material and multiplies its nickel and chromium by 100. The second view shows the result: 16 of 18 move into the box, and so do average continental crust and a standard basalt (blue squares), which contain nothing cosmic. The step cannot tell the two apart. The authors present it as an assumption and conclude only that the result is &ldquo;consistent with&rdquo; 1% cosmic material.</figcaption>
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
    svg.appendChild(el("text", {{x: sx(1.4), y: sy(60), class: "c-label-sm"}}, "Comet-dust field"));
    // Terrestrial crustal zone: Fe/Cr > 200, Fe/Ni > 200
    svg.appendChild(el("rect", {{x: sx(200), y: sy(100000), width: sx(100000)-sx(200), height: sy(200)-sy(100000), fill: "var(--faint)", opacity: "0.10"}}));
    svg.appendChild(el("text", {{x: sx(4000), y: sy(260), "text-anchor": "middle", class: "c-sub"}}, "Crust-like: both ratios above 200"));
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
        ("The paper's test: three modelled ages", p4["paper_chi2_reproduced_with_kennett2015_modelled_ages"]["T"], p4["paper_chi2_reproduced_with_kennett2015_modelled_ages"]["p_value"]),
        ("Arlington Canyon: all 12 dates, 392 to 503 cm", p4["ward_wilson_arlington_canyon_12_dates_392_503cm_14c"]["T"], p4["ward_wilson_arlington_canyon_12_dates_392_503cm_14c"]["p_value"]),
        ("Arlington Canyon: the 5 not set aside as old wood", p4["ward_wilson_arlington_canyon_dark_layer_not_old_wood_14c"]["T"], p4["ward_wilson_arlington_canyon_dark_layer_not_old_wood_14c"]["p_value"]),
    ]

    o = ['<svg class="chart" viewBox="0 0 720 315" role="img" aria-label="Shocked quartz vertical sampling coverage and radiocarbon synchrony test audit" xmlns="http://www.w3.org/2000/svg">']
    # Top panel: Vertical sampling coverage (13/66 strata)
    o.append('<text class="c-group" x="14" y="20">A. Samples examined for shocked quartz, of those listed at each site</text>')
    y0 = 42
    for i, (name, tot, abv, ydb, bel) in enumerate(sites):
        y = y0 + i * 34
        checked = abv + ydb + bel
        o.append(f'<text class="c-tick" x="188" y="{y+13}" text-anchor="end">{esc(name)}</text>')
        w_tot = 240.0
        w_chk = w_tot * (checked / tot)
        o.append(f'<rect x="198" y="{y}" width="{w_tot:.1f}" height="18" rx="3" fill="var(--faint)" opacity="0.22"/>')
        o.append(f'<rect x="198" y="{y}" width="{w_chk:.1f}" height="18" rx="3" fill="var(--copper)"/>')
        note = f"{checked} of {tot}: {abv} above, 1 in the layer, {bel} below"
        o.append(f'<text class="c-tick" x="448" y="{y+13}">{esc(note)}</text>')

    # Bottom panel: Ward-Wilson chi-square synchrony comparison
    o.append('<line x1="14" x2="706" y1="158" y2="158" stroke="var(--rule)"/>')
    o.append('<text class="c-group" x="14" y="180">B. Do the dates agree on one age? (T: larger means less agreement)</text>')
    y1 = 198
    max_t = max(100.0, max(t for _, t, _ in ww_bars))  # scale to the largest T so no bar is clipped
    for i, (label, tval, pval) in enumerate(ww_bars):
        y = y1 + i * 34
        o.append(f'<text class="c-tick" x="318" y="{y+13}" text-anchor="end">{esc(label)}</text>')
        bw = max(4.0, (min(tval, max_t) / max_t) * 190.0)
        col = "var(--copper)" if pval < 0.01 else "#2b5c8f"
        o.append(f'<rect x="328" y="{y}" width="{bw:.1f}" height="18" rx="3" fill="{col}" opacity="0.85"/>')
        p_str = "p below 0.000001" if pval < 1e-6 else f"p = {pval:.3f}"
        o.append(f'<text class="c-tick" x="{336 + bw:.1f}" y="{y+13}">T = {tval:.2f} ({p_str})</text>')
    o.append('<text class="c-axis" x="14" y="305">Copper bars reject a single age at p below 0.01; blue bars do not.</text>')
    o.append("</svg>")

    html_out = (
        '<figure class="fig" aria-label="Shocked quartz vertical background sampling and radiocarbon synchrony audit">\n'
        '<div class="fig-scroll">\n' + "\n".join(o) + "\n</div>\n"
        '<figcaption><strong>The shocked quartz paper: the journal&rsquo;s two reasons.</strong> '
        '(A) Of 66 samples listed at the three sites, 13 were examined for shocked quartz: three in the layer and ten above or below. At Arlington Canyon nothing lies below, since the section ends on gravel, and the three samples above are inside the layer as the authors define it. '
        '(B) The paper&rsquo;s own test of agreement used three modelled ages, two with errors of 235 and 365 years, and could hardly have failed. The twelve radiocarbon dates from the lower part of the Arlington Canyon section are not one age; without the five the original authors set aside as old wood, the disagreement is modest. The other two sites have no dates on the sampled layer itself. Whether the grains are shocked quartz was not tested by the journal or here.</figcaption>\n'
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
