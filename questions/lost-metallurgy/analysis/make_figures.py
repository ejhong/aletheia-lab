#!/usr/bin/env python3
"""Generate interactive HTML/SVG figures for #82 (lost-metallurgy)."""
from __future__ import annotations

import html
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
RES = ROOT / "results"
OUT = ROOT.parent.parent / "site" / "figures" / "lost-metallurgy"
OUT.mkdir(parents=True, exist_ok=True)


def esc(s: object) -> str:
    return html.escape(str(s), quote=True)


def make_tiles(s: dict) -> None:
    rec = s["recap_greenland_8kyr"]
    fur = s["furamoos_germany_14kyr"]
    gisp = s["gisp2_greenland_40_47ka"]
    items = [
        ("0", "stretches of 50 years or more before 5,000 years ago with lead at three times its usual level, in the ice and peat sampled", False),
        ("4 to 5 times Rome", "the lead needed in Greenland ice before the locked rule fires; applied to the Roman and medieval centuries themselves, it does not", False),
        ("7,000 years", "since copper was first smelted in the Balkans, on the archaeological evidence; none of these records shows it", False),
        ("Too coarse", "Nothing unusual before 5,000 years ago, in records that would miss early metalworking and barely show Rome", True),
    ]
    body = ['<div class="tiles">']
    for v, lbl, is_w in items:
        cls = "tile-value is-word" if is_w else "tile-value"
        body.append(f'<div class="tile"><p class="{cls}">{esc(v)}</p><p class="tile-label">{esc(lbl)}</p></div>')
    body.append("</div>\n")
    (OUT / "tiles.html").write_text("\n".join(body), encoding="utf-8")


def make_holocene_timeline(s: dict) -> None:
    rec = s["recap_greenland_8kyr"]
    fur = s["furamoos_germany_14kyr"]
    payload = {
        "recap_ef": [{"a": round(b["age_mid"] / 1000.0, 2), "v": round(b["median"], 3)} for b in rec["bins_100yr_ef"]],
        "recap_nc": [{"a": round(b["age_mid"] / 1000.0, 2), "v": round(b["median"], 2)} for b in rec["bins_100yr_ncpb_pg_g"]],
        "fur_ef": [{"a": round(p["age_bp"] / 1000.0, 2), "v": round(p["ef"], 3)} for p in fur["xrf_series_downsampled"]],
        "fur_iso": [{"a": round(p["age_bp"] / 1000.0, 2), "v": round(p["iso206_207"], 4)} for p in fur["icpms_isotopes"]["points"]],
    }
    data_json = json.dumps(payload)
    html_out = f"""<figure class="fig" aria-label="14,300-year Northern Hemisphere heavy-metal pollution timeline across Greenland ice and European peat">
<div class="fig-controls" style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px;align-items:center">
  <span style="font-size:12px;color:var(--muted);margin-right:4px">Northern Hemisphere archive:</span>
  <button type="button" class="lm-h-btn is-on" data-k="recap_ef" style="font-size:12px;padding:4px 9px;border:1px solid var(--rule);border-radius:4px;background:var(--copper);color:#fff;cursor:pointer">RECAP Greenland Pb EF (8 ka)</button>
  <button type="button" class="lm-h-btn" data-k="recap_nc" style="font-size:12px;padding:4px 9px;border:1px solid var(--rule);border-radius:4px;background:transparent;color:var(--ink);cursor:pointer">RECAP Non-Crustal Pb (pg/g)</button>
  <button type="button" class="lm-h-btn" data-k="fur_ef" style="font-size:12px;padding:4px 9px;border:1px solid var(--rule);border-radius:4px;background:transparent;color:var(--ink);cursor:pointer">Füramoos Peat Pb EF (14.3 ka)</button>
  <button type="button" class="lm-h-btn" data-k="fur_iso" style="font-size:12px;padding:4px 9px;border:1px solid var(--rule);border-radius:4px;background:transparent;color:var(--ink);cursor:pointer">Füramoos 206Pb/207Pb Isotopes</button>
</div>
<div class="fig-scroll">
<svg id="lm-h-svg" class="chart" viewBox="0 0 720 285" role="img" aria-label="Holocene and Late Glacial atmospheric lead enrichment and isotopes" xmlns="http://www.w3.org/2000/svg"></svg>
</div>
<figcaption><strong>Lead in East Greenland ice and a southern German bog.</strong> The dashed line is 5,000 years ago, the cut the plan chose; smelting is in fact some 2,000 years older. The shaded band is the Roman period. Nothing before 5,000 years ago stands out. Look also at what follows it: in the ice, the Bronze and Iron Ages are indistinguishable from the earlier scatter and Rome rises to about one and a half times it; in the bog, lead and its isotopes do not move until about 3,600 years ago. These records show a large lead industry near Europe and little else.</figcaption>
<script>
(function(){{
  var D = {data_json};
  var svg = document.getElementById("lm-h-svg");
  var btns = document.querySelectorAll(".lm-h-btn");
  var L = 62, R = 690, T = 34, B = 235;
  function el(tag, attrs, txt){{
    var n = document.createElementNS("http://www.w3.org/2000/svg", tag);
    for (var k in attrs) n.setAttribute(k, attrs[k]);
    if (txt !== undefined) n.textContent = txt;
    return n;
  }}
  var CFG = {{
    recap_ef: {{title: "RECAP East Greenland Ice Core — 100-yr Volcanic-Masked Pb Enrichment Factor (EF, capped at 10)", xmax: 8.2, ymin: 0, ymax: 10, ref: 3.0, refTxt: "EF = 3.0 threshold", unit: "EF"}},
    recap_nc: {{title: "RECAP East Greenland Ice Core — 100-yr Non-Crustal Pb Excess (pg/g, capped at 25)", xmax: 8.2, ymin: 0, ymax: 25, ref: 2.15, refTxt: "Roman median (2.15 pg/g)", unit: "pg/g"}},
    fur_ef:   {{title: "Füramoos Peat Bog (S. Germany) — 14.3 kyr XRF Lead Enrichment Factor (EF)", xmax: 14.5, ymin: 0, ymax: 6, ref: 3.0, refTxt: "EF = 3.0 threshold", unit: "EF"}},
    fur_iso:  {{title: "Füramoos Peat Bog (S. Germany) — ICP-MS 206Pb/207Pb (lower = unradiogenic ore lead)", xmax: 14.5, ymin: 1.13, ymax: 1.23, ref: 1.20, refTxt: "Natural crustal floor (~1.20)", unit: "ratio"}}
  }};
  function draw(k){{
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    var c = CFG[k], pts = D[k].slice().sort(function(x,y){{ return y.a - x.a; }});
    svg.appendChild(el("text", {{x: L, y: 19, "font-size": 12, "font-weight": 600, fill: "var(--ink)"}}, c.title));
    function sx(ka){{ return L + (c.xmax - ka) / c.xmax * (R - L); }}
    function sy(v){{
      var vc = Math.max(c.ymin, Math.min(c.ymax, v));
      return B - (vc - c.ymin) / (c.ymax - c.ymin) * (B - T);
    }}
    // Roman positive control band (2.15 - 1.65 ka)
    var rx0 = sx(2.15), rx1 = sx(1.65);
    svg.appendChild(el("rect", {{x: rx0, y: T, width: rx1 - rx0, height: B - T, fill: "var(--copper)", opacity: 0.14}}));
    svg.appendChild(el("text", {{x: (rx0 + rx1)/2, y: T + 12, "text-anchor": "middle", "font-size": 9.5, fill: "var(--copper)"}}, "Roman"));
    // 5.0 ka Bronze Age boundary
    var x5 = sx(5.0);
    svg.appendChild(el("line", {{x1: x5, x2: x5, y1: T, y2: B, stroke: "var(--ink)", "stroke-dasharray": "4,3", "stroke-width": 1.2}}));
    svg.appendChild(el("text", {{x: x5 - 5, y: T + 13, "text-anchor": "end", "font-size": 10, fill: "var(--muted)"}}, "← Pre-Bronze (>5 ka)"));
    svg.appendChild(el("text", {{x: x5 + 5, y: T + 13, "text-anchor": "start", "font-size": 10, fill: "var(--muted)"}}, "Bronze → Modern"));
    // Reference horizontal line
    var ry = sy(c.ref);
    svg.appendChild(el("line", {{x1: L, x2: R, y1: ry, y2: ry, stroke: "var(--teal)", "stroke-dasharray": "3,3", "stroke-width": 1.1}}));
    svg.appendChild(el("text", {{x: L + 4, y: ry - 4, "font-size": 10, fill: "var(--teal)"}}, c.refTxt));
    // Axes
    svg.appendChild(el("line", {{x1: L, x2: R, y1: B, y2: B, stroke: "var(--rule)"}}));
    svg.appendChild(el("line", {{x1: L, x2: L, y1: T, y2: B, stroke: "var(--rule)"}}));
    // X ticks
    var xstep = c.xmax > 10 ? 2 : 1;
    for (var xa = 0; xa <= Math.floor(c.xmax); xa += xstep){{
      var tx = sx(xa);
      svg.appendChild(el("line", {{x1: tx, x2: tx, y1: B, y2: B + 4, stroke: "var(--muted)"}}));
      svg.appendChild(el("text", {{x: tx, y: B + 17, "text-anchor": "middle", "font-size": 10.5, fill: "var(--muted)"}}, xa + " ka"));
    }}
    // Y ticks
    for (var yi = 0; yi <= 4; yi++){{
      var yv = c.ymin + yi * (c.ymax - c.ymin) / 4;
      var ty = sy(yv);
      svg.appendChild(el("line", {{x1: L - 4, x2: L, y1: ty, y2: ty, stroke: "var(--muted)"}}));
      svg.appendChild(el("text", {{x: L - 7, y: ty + 3.5, "text-anchor": "end", "font-size": 10, fill: "var(--muted)"}}, c.unit === "ratio" ? yv.toFixed(2) : yv.toFixed(0)));
    }}
    // Line + points
    var pathD = pts.map(function(p, i){{ return (i === 0 ? "M" : "L") + sx(p.a).toFixed(1) + "," + sy(p.v).toFixed(1); }}).join(" ");
    svg.appendChild(el("path", {{d: pathD, fill: "none", stroke: "var(--copper)", "stroke-width": 1.8}}));
    if (k === "fur_iso") {{
      pts.forEach(function(p){{
        var pre = p.a >= 5.0;
        svg.appendChild(el("circle", {{cx: sx(p.a), cy: sy(p.v), r: 3.4, fill: pre ? "var(--teal)" : "var(--copper)", stroke: "#fff", "stroke-width": 0.7}}));
      }});
    }}
    svg.appendChild(el("text", {{x: (L + R)/2, y: 274, "text-anchor": "middle", "font-size": 11, fill: "var(--muted)"}}, "Age (thousands of years before 1950 CE, oldest on left)"));
  }}
  btns.forEach(function(b){{
    b.addEventListener("click", function(){{
      btns.forEach(function(x){{ x.classList.remove("is-on"); x.style.background = "transparent"; x.style.color = "var(--ink)"; }});
      b.classList.add("is-on"); b.style.background = "var(--copper)"; b.style.color = "#fff";
      draw(b.getAttribute("data-k"));
    }});
  }});
  draw("recap_ef");
}})();
</script>
</figure>
"""
    (OUT / "holocene_timeline.html").write_text(html_out, encoding="utf-8")


def make_glacial_and_controls(s: dict) -> None:
    edc = s["edc_antarctica_217kyr"]
    gisp = s["gisp2_greenland_40_47ka"]
    rec = s["recap_greenland_8kyr"]
    fur = s["furamoos_germany_14kyr"]
    payload = {
        "edc": [{"a": round(p["age_bp"] / 1000.0, 2), "ef": round(p["ef"], 2), "iso": round(p["iso206_207"], 3)} for p in edc["series_0_50ka"]],
        "gisp_pb": [{"a": round(b["age_mid"] / 1000.0, 2), "ef": round(b["median"], 2)} for b in gisp["elements"]["Pb"]["bins_100yr_ef"]],
        "gisp_bars": [
            {"el": el, "p95": round(gisp["elements"][el]["b100_ef_p95"], 2), "max": round(gisp["elements"][el]["b100_ef_max"], 2)}
            for el in ["Pb", "Cd", "Bi", "Tl"]
        ],
        "era_bars": [
            {"era": "Pre-5 ka (8–5 ka)", "recap": round(rec["eras_volc_masked_emp"]["pre_bronze_gt5ka"]["ef_median"], 2), "fur": round(fur["eras_published_ef"]["pre_bronze_gt5ka"]["ef_median"], 2)},
            {"era": "Bronze/Iron", "recap": round(rec["eras_volc_masked_emp"]["bronze_iron_5_2.15ka"]["ef_median"], 2), "fur": round(fur["eras_published_ef"]["bronze_iron_5_2.15ka"]["ef_median"], 2)},
            {"era": "Roman Empire", "recap": round(rec["eras_volc_masked_emp"]["roman_2.15_1.65ka"]["ef_median"], 2), "fur": round(fur["eras_published_ef"]["roman_2.15_1.65ka"]["ef_median"], 2)},
            {"era": "High Medieval", "recap": round(rec["eras_volc_masked_emp"]["medieval_1.0_0.5ka"]["ef_median"], 2), "fur": round(fur["eras_published_ef"]["medieval_1.0_0.5ka"]["ef_median"], 2)},
            {"era": "Industrial", "recap": round(rec["eras_volc_masked_emp"]["industrial_lt0.25ka"]["ef_median"], 2), "fur": round(fur["eras_published_ef"]["industrial_lt0.25ka"]["ef_median"], 2)},
        ],
    }
    data_json = json.dumps(payload)
    html_out = f"""<figure class="fig" aria-label="Deep Ice Age Antarctic and Greenland heavy-metal scans and historical positive controls">
<div class="fig-controls" style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px;align-items:center">
  <span style="font-size:12px;color:var(--muted);margin-right:4px">Deep-time &amp; control view:</span>
  <button type="button" class="lm-g-btn is-on" data-k="edc" style="font-size:12px;padding:4px 9px;border:1px solid var(--rule);border-radius:4px;background:var(--copper);color:#fff;cursor:pointer">Antarctica EPICA Dome C (50–2 ka)</button>
  <button type="button" class="lm-g-btn" data-k="gisp" style="font-size:12px;padding:4px 9px;border:1px solid var(--rule);border-radius:4px;background:transparent;color:var(--ink);cursor:pointer">Greenland GISP2 MIS 3 (47–40 ka, 4 metals)</button>
  <button type="button" class="lm-g-btn" data-k="eras" style="font-size:12px;padding:4px 9px;border:1px solid var(--rule);border-radius:4px;background:transparent;color:var(--ink);cursor:pointer">Era Calibration (Pre-5 ka vs. Roman/Industrial)</button>
</div>
<div class="fig-scroll">
<svg id="lm-g-svg" class="chart" viewBox="0 0 720 275" role="img" aria-label="Deep Ice Age heavy-metal profiles and positive controls" xmlns="http://www.w3.org/2000/svg"></svg>
</div>
<figcaption><strong>The Ice Age records.</strong> Antarctic ice (30 samples between 40,000 and 5,000 years ago): one high reading at 18,160 years ago, isolated and of the wrong isotope signature for ore lead. This record does not register Rome either. Central Greenland ice, 47,400 to 40,400 years ago: four metals, none at three times its usual level in any century; here too the usual level is taken from the same stretch of ice, so only a burst would show, not a steady source. The third button compares periods. Between 40,400 and 14,300 years ago there are no northern data at all.</figcaption>
<script>
(function(){{
  var D = {data_json};
  var svg = document.getElementById("lm-g-svg");
  var btns = document.querySelectorAll(".lm-g-btn");
  var L = 62, R = 685, T = 36, B = 225;
  function el(tag, attrs, txt){{
    var n = document.createElementNS("http://www.w3.org/2000/svg", tag);
    for (var k in attrs) n.setAttribute(k, attrs[k]);
    if (txt !== undefined) n.textContent = txt;
    return n;
  }}
  function draw(k){{
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    if (k === "edc") {{
      svg.appendChild(el("text", {{x: L, y: 20, "font-size": 12, "font-weight": 600, fill: "var(--ink)"}}, "EPICA Dome C (East Antarctica) — Pb/Ba Enrichment Factor (50–2 ka BP; baseline = 217–40 ka)"));
      function sx(ka){{ return L + (50 - ka) / 50 * (R - L); }}
      function sy(v){{ return B - Math.min(5, v) / 5 * (B - T); }}
      svg.appendChild(el("line", {{x1: L, x2: R, y1: sy(3), y2: sy(3), stroke: "var(--teal)", "stroke-dasharray": "3,3"}}));
      svg.appendChild(el("text", {{x: L + 5, y: sy(3) - 4, "font-size": 10, fill: "var(--teal)"}}, "EF = 3.0 threshold"));
      svg.appendChild(el("line", {{x1: L, x2: R, y1: B, y2: B, stroke: "var(--rule)"}}));
      svg.appendChild(el("line", {{x1: L, x2: L, y1: T, y2: B, stroke: "var(--rule)"}}));
      for (var ka = 0; ka <= 50; ka += 10){{
        var tx = sx(ka);
        svg.appendChild(el("text", {{x: tx, y: B + 17, "text-anchor": "middle", "font-size": 10.5, fill: "var(--muted)"}}, ka + " ka"));
      }}
      for (var yv = 0; yv <= 5; yv++){{
        svg.appendChild(el("text", {{x: L - 8, y: sy(yv) + 3.5, "text-anchor": "end", "font-size": 10, fill: "var(--muted)"}}, yv));
      }}
      var pts = D.edc.slice().sort(function(a,b){{ return b.a - a.a; }});
      var pathD = pts.map(function(p, i){{ return (i===0?"M":"L") + sx(p.a).toFixed(1) + "," + sy(p.ef).toFixed(1); }}).join(" ");
      svg.appendChild(el("path", {{d: pathD, fill: "none", stroke: "#64748b", "stroke-width": 1.4}}));
      pts.forEach(function(p){{
        var hi = p.ef >= 3.0;
        svg.appendChild(el("circle", {{cx: sx(p.a), cy: sy(p.ef), r: hi ? 4.5 : 3, fill: hi ? "var(--copper)" : "var(--teal)"}}));
        if (hi) {{
          svg.appendChild(el("text", {{x: sx(p.a) - 6, y: sy(p.ef) + 4, "text-anchor": "end", "font-size": 10, "font-weight": 600, fill: "var(--copper)"}}, "18.16 ka: isolated, radiogenic (1.257)"));
        }}
      }});
      svg.appendChild(el("text", {{x: (L+R)/2, y: 263, "text-anchor": "middle", "font-size": 11, fill: "var(--muted)"}}, "Age (ka BP, oldest on left)"));
    }} else if (k === "gisp") {{
      svg.appendChild(el("text", {{x: L, y: 20, "font-size": 12, "font-weight": 600, fill: "var(--ink)"}}, "GISP2 Central Greenland (47.4–40.4 ka, 70 century bins) — 95th-Pct & Max 100-yr EF across 4 Chalcophile Metals"));
      var bars = D.gisp_bars;
      function sy(v){{ return B - Math.min(3.5, v) / 3.5 * (B - T); }}
      svg.appendChild(el("line", {{x1: L, x2: R, y1: sy(3.0), y2: sy(3.0), stroke: "#b91c1c", "stroke-dasharray": "4,3", "stroke-width": 1.3}}));
      svg.appendChild(el("text", {{x: R - 4, y: sy(3.0) - 5, "text-anchor": "end", "font-size": 10.5, fill: "#b91c1c"}}, "EF = 3.0 smelting threshold (0/70 bins exceeded)"));
      svg.appendChild(el("line", {{x1: L, x2: R, y1: B, y2: B, stroke: "var(--rule)"}}));
      svg.appendChild(el("line", {{x1: L, x2: L, y1: T, y2: B, stroke: "var(--rule)"}}));
      for (var yv = 0; yv <= 3; yv++){{
        svg.appendChild(el("text", {{x: L - 8, y: sy(yv) + 3.5, "text-anchor": "end", "font-size": 10, fill: "var(--muted)"}}, yv + ".0"));
      }}
      var step = (R - L) / bars.length;
      bars.forEach(function(b, i){{
        var cx = L + (i + 0.5) * step;
        var y95 = sy(b.p95), ymax = sy(b.max);
        svg.appendChild(el("rect", {{x: cx - 34, y: y95, width: 30, height: B - y95, fill: "var(--teal)", opacity: 0.85}}));
        svg.appendChild(el("rect", {{x: cx + 4, y: ymax, width: 30, height: B - ymax, fill: "var(--copper)", opacity: 0.85}}));
        svg.appendChild(el("text", {{x: cx - 19, y: y95 - 5, "text-anchor": "middle", "font-size": 10, fill: "var(--teal)"}}, b.p95.toFixed(2)));
        svg.appendChild(el("text", {{x: cx + 19, y: ymax - 5, "text-anchor": "middle", "font-size": 10, fill: "var(--copper)"}}, b.max.toFixed(2)));
        svg.appendChild(el("text", {{x: cx, y: B + 18, "text-anchor": "middle", "font-size": 11.5, "font-weight": 600, fill: "var(--ink)"}}, b.el + "/Ce"));
      }});
      svg.appendChild(el("text", {{x: (L+R)/2, y: 263, "text-anchor": "middle", "font-size": 11, fill: "var(--muted)"}}, "Teal = 95th-percentile 100-yr bin EF  |  Copper = Maximum 100-yr bin EF (all volcanic-masked)"));
    }} else {{
      svg.appendChild(el("text", {{x: L, y: 20, "font-size": 12, "font-weight": 600, fill: "var(--ink)"}}, "Positive-Control Calibration — Median Pb Enrichment Factor by Archaeological Era"));
      var bars = D.era_bars;
      function sy(v){{ return B - Math.min(9.5, v) / 9.5 * (B - T); }}
      svg.appendChild(el("line", {{x1: L, x2: R, y1: B, y2: B, stroke: "var(--rule)"}}));
      svg.appendChild(el("line", {{x1: L, x2: L, y1: T, y2: B, stroke: "var(--rule)"}}));
      for (var yv = 0; yv <= 9; yv += 3){{
        svg.appendChild(el("text", {{x: L - 8, y: sy(yv) + 3.5, "text-anchor": "end", "font-size": 10, fill: "var(--muted)"}}, yv));
      }}
      var step = (R - L) / bars.length;
      bars.forEach(function(b, i){{
        var cx = L + (i + 0.5) * step;
        var yr = sy(b.recap), yf = sy(b.fur);
        svg.appendChild(el("rect", {{x: cx - 28, y: yr, width: 25, height: B - yr, fill: "var(--copper)", opacity: 0.9}}));
        svg.appendChild(el("rect", {{x: cx + 3, y: yf, width: 25, height: B - yf, fill: "var(--teal)", opacity: 0.85}}));
        svg.appendChild(el("text", {{x: cx - 15, y: yr - 4, "text-anchor": "middle", "font-size": 9.5, fill: "var(--copper)"}}, b.recap.toFixed(2)));
        svg.appendChild(el("text", {{x: cx + 15, y: yf - 4, "text-anchor": "middle", "font-size": 9.5, fill: "var(--teal)"}}, b.fur.toFixed(2)));
        svg.appendChild(el("text", {{x: cx, y: B + 17, "text-anchor": "middle", "font-size": 10, fill: "var(--ink)"}}, b.era));
      }});
      svg.appendChild(el("text", {{x: (L+R)/2, y: 263, "text-anchor": "middle", "font-size": 11, fill: "var(--muted)"}}, "Copper = RECAP East Greenland Ice Core  |  Teal = Füramoos Peat Bog (S. Germany)"));
    }}
  }}
  btns.forEach(function(b){{
    b.addEventListener("click", function(){{
      btns.forEach(function(x){{ x.classList.remove("is-on"); x.style.background = "transparent"; x.style.color = "var(--ink)"; }});
      b.classList.add("is-on"); b.style.background = "var(--copper)"; b.style.color = "#fff";
      draw(b.getAttribute("data-k"));
    }});
  }});
  draw("edc");
}})();
</script>
</figure>
"""
    (OUT / "glacial_and_controls.html").write_text(html_out, encoding="utf-8")


def main():
    summary = json.loads((RES / "metallurgy_summary.json").read_text(encoding="utf-8"))
    make_tiles(summary)
    make_holocene_timeline(summary)
    make_glacial_and_controls(summary)
    print("Generated 3 figures in", OUT)


if __name__ == "__main__":
    main()
