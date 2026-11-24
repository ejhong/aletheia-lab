#!/usr/bin/env python3
"""Generate interactive HTML/SVG figures for #88 (ice-age-farming)."""
from __future__ import annotations

import html
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
RES = ROOT / "results"
OUT = ROOT.parent.parent / "site" / "figures" / "ice-age-farming"
OUT.mkdir(parents=True, exist_ok=True)


def esc(s: object) -> str:
    return html.escape(str(s), quote=True)


def make_tiles(s: dict) -> None:
    cnt = s["counts"]
    cal = s["calibration"]
    sw = s["pre12ka_sweep"]
    lg = sw["late_glacial_12_18ka"]
    lgm = sw["lgm_glacial_neg_18_50ka"]
    items = [
        ("150", "cores with cereal-type pollen older than 12,000 years were examined, most of them in Europe and the Mediterranean", False),
        (f"{cal['eu_holocene_8500_2000bp']['farm_strict_pct']:.0f}%", "of known farming-era cores in Europe set off the strict detector; the plan required at least 50%", False),
        ("0 of 14", "cores in the Fertile Crescent set it off during the centuries when farming began there", False),
        ("Inconclusive", "No farming signal before 12,000 years ago, from a detector that failed its own test and cannot see the first real farming", True),
    ]
    body = ['<div class="tiles">']
    for v, lbl, is_w in items:
        cls = "tile-value is-word" if is_w else "tile-value"
        body.append(f'<div class="tile"><p class="{cls}">{esc(v)}</p><p class="tile-label">{esc(lbl)}</p></div>')
    body.append("</div>\n")
    (OUT / "tiles.html").write_text("\n".join(body), encoding="utf-8")


def make_calibration_and_sweep(s: dict) -> None:
    cnt = s["counts"]
    cal = s["calibration"]
    sw = s["pre12ka_sweep"]
    lg = sw["late_glacial_12_18ka"]
    lgm = sw["lgm_glacial_neg_18_50ka"]
    n12 = cnt["global_neotoma_pollen_cores_ge12ka"]
    n18 = cnt["global_neotoma_pollen_cores_ge18ka"]

    bars = [
        {
            "lbl": "Holocene Neolithic Europe\n(8.5–2 ka calibration, n=100)",
            "short": "Holocene Neolithic Europe (8.5–2 ka)",
            "relaxed": cal["eu_holocene_8500_2000bp"]["farm_relaxed_pct"],
            "strict": cal["eu_holocene_8500_2000bp"]["farm_strict_pct"],
            "n_txt": f"{cal['eu_holocene_8500_2000bp']['farm_relaxed_n']}/100 relaxed · {cal['eu_holocene_8500_2000bp']['farm_strict_n']}/100 strict",
            "kind": "pos",
        },
        {
            "lbl": "Mesolithic N/C Europe\n(11.5–9 ka neg. control, n=40)",
            "short": "Mesolithic N/C Europe (11.5–9 ka)",
            "relaxed": cal["eu_mesolithic_neg_11500_9000bp"]["farm_relaxed_pct"],
            "strict": cal["eu_mesolithic_neg_11500_9000bp"]["farm_strict_pct"],
            "n_txt": f"{cal['eu_mesolithic_neg_11500_9000bp']['farm_relaxed_n']}/40 relaxed · {cal['eu_mesolithic_neg_11500_9000bp']['farm_strict_n']}/40 strict",
            "kind": "neg",
        },
        {
            "lbl": f"Global Late Glacial\n(12–18 ka target, n={n12:,})",
            "short": f"Global Late Glacial (12–18 ka, n={n12:,})",
            "relaxed": round(100.0 * lg["farm_relaxed_n"] / n12, 2),
            "strict": round(lg["pct_of_global_ge12ka"], 2),
            "n_txt": f"{lg['farm_relaxed_n']}/{n12:,} relaxed · {lg['farm_strict_chron_ok_n']}/{n12:,} strict",
            "kind": "target",
        },
        {
            "lbl": f"Global Deep Glacial LGM/MIS 3\n(18–50 ka neg. control, n={n18:,})",
            "short": f"Global Deep Glacial (18–50 ka, n={n18:,})",
            "relaxed": round(100.0 * lgm["farm_relaxed_n"] / n18, 2),
            "strict": round(lgm["pct_of_global_ge18ka"], 2),
            "n_txt": f"{lgm['farm_relaxed_n']}/{n18:,} relaxed · {lgm['farm_strict_chron_ok_n']}/{n18:,} strict",
            "kind": "neg",
        },
    ]

    payload = {
        "bars": bars,
        "onsets": cal["neolithic_onsets"],
    }
    data_json = json.dumps(payload)

    html_out = f"""<figure class="fig" aria-label="Neotoma pollen farming detector calibration and global pre-12,000 BP sweep">
<div class="fig-controls" style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px;align-items:center">
  <span style="font-size:12px;color:var(--muted);margin-right:4px">View:</span>
  <button type="button" class="iaf-c-btn is-on" data-k="rates" style="font-size:12px;padding:4px 9px;border:1px solid var(--rule);border-radius:4px;background:var(--copper);color:#fff;cursor:pointer">Detection Rates: Calibration vs. Ice Age Sweep</button>
  <button type="button" class="iaf-c-btn" data-k="wave" style="font-size:12px;padding:4px 9px;border:1px solid var(--rule);border-radius:4px;background:transparent;color:var(--ink);cursor:pointer">Positive Control: European Neolithic Wave (n=23)</button>
</div>
<div class="fig-scroll">
<svg id="iaf-c-svg" class="chart" viewBox="0 0 720 330" role="img" aria-label="Farming detection rates and Neolithic wave calibration" xmlns="http://www.w3.org/2000/svg"></svg>
</div>
<figcaption><strong>The detectors on known farming, and on the Ice Age.</strong> The strict detector (copper) fires in 23% of European cores from the farming era, against the 50% the plan required, and in none from before farming in northern Europe. The looser screen (teal) fires in 59%. Before 12,000 years ago neither fires more often at 12,000 to 18,000 years than at 18,000 to 50,000. The rates shown are over every core that reaches those ages; only the 150 with cereal-type pollen were examined, and among those the looser screen fires in about a third in both periods, which is to say it does not tell farming from Ice Age grassland. The second button shows when the strict detector first fires in each European core.</figcaption>
<script>
(function(){{
  var D = {data_json};
  var svg = document.getElementById("iaf-c-svg");
  var btns = document.querySelectorAll(".iaf-c-btn");
  function el(tag, attrs, txt){{
    var n = document.createElementNS("http://www.w3.org/2000/svg", tag);
    for (var k in attrs) n.setAttribute(k, attrs[k]);
    if (txt !== undefined) n.textContent = txt;
    return n;
  }}
  function draw(k){{
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    if (k === "rates") {{
      var L = 240, R = 680, T = 40, B = 280;
      var xmax = 68;
      function sx(v){{ return L + (v / xmax) * (R - L); }}
      svg.appendChild(el("text", {{x: 16, y: 20, "font-size": 12, "font-weight": 600, fill: "var(--ink)"}}, "Share of cores triggering multi-proxy farming signature (%)"));
      // legend
      svg.appendChild(el("rect", {{x: 425, y: 10, width: 11, height: 11, rx: 2, fill: "var(--teal)"}}));
      svg.appendChild(el("text", {{x: 441, y: 19, "font-size": 10.5, fill: "var(--ink)"}}, "FARM_RELAXED"));
      svg.appendChild(el("rect", {{x: 545, y: 10, width: 11, height: 11, rx: 2, fill: "var(--copper)"}}));
      svg.appendChild(el("text", {{x: 561, y: 19, "font-size": 10.5, fill: "var(--ink)"}}, "FARM_STRICT"));

      svg.appendChild(el("line", {{x1: L, x2: R, y1: B, y2: B, stroke: "var(--rule)"}}));
      svg.appendChild(el("line", {{x1: L, x2: L, y1: T, y2: B, stroke: "var(--rule)"}}));
      [0, 10, 20, 30, 40, 50, 60].forEach(function(v){{
        var x = sx(v);
        svg.appendChild(el("line", {{x1: x, x2: x, y1: T, y2: B, stroke: "var(--rule)", "stroke-dasharray": "2,3", opacity: 0.5}}));
        svg.appendChild(el("text", {{x: x, y: B + 16, "text-anchor": "middle", "font-size": 10, fill: "var(--muted)"}}, v + "%"));
      }});

      var step = (B - T) / D.bars.length;
      D.bars.forEach(function(b, i){{
        var y0 = T + i * step + 10;
        var bh = 16;
        svg.appendChild(el("text", {{x: L - 10, y: y0 + 13, "text-anchor": "end", "font-size": 11, "font-weight": b.kind === "target" || b.kind === "pos" ? 600 : 400, fill: "var(--ink)"}}, b.short));
        svg.appendChild(el("text", {{x: L - 10, y: y0 + 27, "text-anchor": "end", "font-size": 9.3, fill: "var(--muted)"}}, b.n_txt));
        var w1 = Math.max(2, sx(b.relaxed) - L);
        var w2 = Math.max(2, sx(b.strict) - L);
        svg.appendChild(el("rect", {{x: L, y: y0, width: w1, height: bh, rx: 2, fill: "var(--teal)", opacity: 0.85}}));
        svg.appendChild(el("text", {{x: L + w1 + 5, y: y0 + 12, "font-size": 10, "font-weight": 600, fill: "var(--teal)"}}, b.relaxed.toFixed(b.relaxed < 5 ? 2 : 1) + "%"));
        svg.appendChild(el("rect", {{x: L, y: y0 + bh + 3, width: w2, height: bh, rx: 2, fill: "var(--copper)", opacity: 0.9}}));
        svg.appendChild(el("text", {{x: L + w2 + 5, y: y0 + bh + 15, "font-size": 10, "font-weight": 600, fill: "var(--copper)"}}, b.strict.toFixed(b.strict < 5 ? 2 : 1) + "%"));
      }});
      svg.appendChild(el("text", {{x: (L+R)/2, y: 316, "text-anchor": "middle", "font-size": 10.5, fill: "var(--muted)"}}, "Late Glacial (12–18 ka) shows no excess over deep LGM/MIS 3 (18–50 ka): Fisher p = 0.95 (strict), p = 0.77 (relaxed)"));
    }} else {{
      var L = 70, R = 680, T = 36, B = 276;
      var latMin = 38, latMax = 61, ageMin = 2000, ageMax = 8800;
      function sx(lat){{ return L + (lat - latMin) / (latMax - latMin) * (R - L); }}
      function sy(age){{ return B - (age - ageMin) / (ageMax - ageMin) * (B - T); }}
      svg.appendChild(el("text", {{x: L, y: 20, "font-size": 12, "font-weight": 600, fill: "var(--ink)"}}, "Calibration check: Earliest FARM_STRICT onset vs. latitude in European/Anatolian Holocene cores (n=23)"));
      svg.appendChild(el("line", {{x1: L, x2: R, y1: B, y2: B, stroke: "var(--rule)"}}));
      svg.appendChild(el("line", {{x1: L, x2: L, y1: T, y2: B, stroke: "var(--rule)"}}));
      [40, 45, 50, 55, 60].forEach(function(lv){{
        var x = sx(lv);
        svg.appendChild(el("line", {{x1: x, x2: x, y1: T, y2: B, stroke: "var(--rule)", "stroke-dasharray": "2,4", opacity: 0.5}}));
        svg.appendChild(el("text", {{x: x, y: B + 16, "text-anchor": "middle", "font-size": 10, fill: "var(--muted)"}}, lv + "°N"));
      }});
      [2000, 4000, 6000, 8000].forEach(function(av){{
        var y = sy(av);
        svg.appendChild(el("line", {{x1: L, x2: R, y1: y, y2: y, stroke: "var(--rule)", "stroke-dasharray": "2,4", opacity: 0.5}}));
        svg.appendChild(el("text", {{x: L - 8, y: y + 3.5, "text-anchor": "end", "font-size": 10, fill: "var(--muted)"}}, av.toLocaleString()));
      }});
      // Simple OLS trend line
      var xs = D.onsets.map(function(o){{ return o.lat; }});
      var ys = D.onsets.map(function(o){{ return o.onset_cal_bp; }});
      var mx = xs.reduce(function(a,b){{return a+b;}},0)/xs.length;
      var my = ys.reduce(function(a,b){{return a+b;}},0)/ys.length;
      var num = 0, den = 0;
      for (var i = 0; i < xs.length; i++){{ num += (xs[i]-mx)*(ys[i]-my); den += (xs[i]-mx)*(xs[i]-mx); }}
      var sl = den > 0 ? num/den : 0, ic = my - sl*mx;
      svg.appendChild(el("line", {{x1: sx(40), y1: sy(ic + sl*40), x2: sx(60), y2: sy(ic + sl*60), stroke: "var(--copper)", "stroke-width": 1.8, "stroke-dasharray": "5,4", opacity: 0.8}}));
      D.onsets.forEach(function(o){{
        var cx = sx(o.lat), cy = sy(o.onset_cal_bp);
        var c = el("circle", {{cx: cx.toFixed(1), cy: cy.toFixed(1), r: 5, fill: "var(--teal)", opacity: 0.88, stroke: "#fff", "stroke-width": 0.9}});
        c.appendChild(el("title", {{}}, o.sitename + " (" + o.lat + "°N, " + o.lon + "°E): " + o.onset_cal_bp + " cal BP"));
        svg.appendChild(c);
        if (o.onset_cal_bp >= 6800 || o.lat >= 58) {{
          svg.appendChild(el("text", {{x: cx + 7, y: cy + 3, "font-size": 9.2, fill: "var(--ink)"}}, o.sitename));
        }}
      }});
      svg.appendChild(el("text", {{x: (L+R)/2, y: 314, "text-anchor": "middle", "font-size": 10.5, fill: "var(--muted)"}}, "Latitude (°N) — Earlier farming in Anatolia/Balkans (7–8 ka) spreading NW to Northern Europe (Spearman ρ = −0.59, p = 0.0029)"));
    }}
  }}
  btns.forEach(function(b){{
    b.addEventListener("click", function(){{
      btns.forEach(function(x){{ x.classList.remove("is-on"); x.style.background = "transparent"; x.style.color = "var(--ink)"; }});
      b.classList.add("is-on"); b.style.background = "var(--copper)"; b.style.color = "#fff";
      draw(b.getAttribute("data-k"));
    }});
  }});
  draw("rates");
}})();
</script>
</figure>
"""
    (OUT / "calibration_and_sweep.html").write_text(html_out, encoding="utf-8")


def make_global_map(s: dict) -> None:
    pts = []
    for c in s["pre12ka_sweep"]["all_pre12ka_candidates_summary"]:
        if c["lat"] is None or c["lon"] is None:
            continue
        status = "occ"
        if c["lg_strict"]:
            status = "lg_strict"
        elif c["lgm_strict"]:
            status = "lgm_strict"
        elif c["lg_relaxed"]:
            status = "lg_relaxed"
        pts.append({
            "id": c["datasetid"],
            "name": c["sitename"],
            "lat": c["lat"],
            "lon": c["lon"],
            "st": status,
            "crop": c["max_crop_pct_12_50"],
            "taxa": ", ".join(c["occ_taxa"][:2]),
        })
    data_json = json.dumps(pts)
    html_out = f"""<figure class="fig" aria-label="Global map of pre-12,000 BP crop-bearing Neotoma pollen cores">
<div class="fig-controls" style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px;align-items:center">
  <span style="font-size:12px;color:var(--muted);margin-right:4px">Map extent:</span>
  <button type="button" class="iaf-m-btn is-on" data-k="global" style="font-size:12px;padding:4px 9px;border:1px solid var(--rule);border-radius:4px;background:var(--copper);color:#fff;cursor:pointer">Global View (All 150 Audited Pre-12 ka Cores)</button>
  <button type="button" class="iaf-m-btn" data-k="med" style="font-size:12px;padding:4px 9px;border:1px solid var(--rule);border-radius:4px;background:transparent;color:var(--ink);cursor:pointer">Mediterranean / Anatolia Wild-Cereal Belt Zoom</button>
</div>
<div class="fig-scroll">
<svg id="iaf-m-svg" class="chart" viewBox="0 0 720 335" role="img" aria-label="Map of pre-12,000 BP Neotoma pollen cores with cereal-type grains" xmlns="http://www.w3.org/2000/svg"></svg>
</div>
<figcaption><strong>Where anything was flagged before 12,000 years ago.</strong> Diamonds and squares mark the cores that set off the strict detector: two in Italy, two in Turkey, one in Syria. Small dots mark cores that set off only the looser screen or hold stray cereal-type grains. The grains are most simply read as wild grasses, which is asserted here and not tested. The map is nearly empty outside Europe and the Mediterranean because few cores were examined there: of the 150, two are in the tropics.</figcaption>
<script>
(function(){{
  var PTS = {data_json};
  var svg = document.getElementById("iaf-m-svg");
  var btns = document.querySelectorAll(".iaf-m-btn");
  function el(tag, attrs, txt){{
    var n = document.createElementNS("http://www.w3.org/2000/svg", tag);
    for (var k in attrs) n.setAttribute(k, attrs[k]);
    if (txt !== undefined) n.textContent = txt;
    return n;
  }}
  function draw(k){{
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    var L = 36, R = 688, T = 30, B = 290;
    var lonMin = k === "med" ? -10 : -165;
    var lonMax = k === "med" ? 50 : 165;
    var latMin = k === "med" ? 30 : -55;
    var latMax = k === "med" ? 52 : 76;
    function sx(lon){{ return L + (lon - lonMin) / (lonMax - lonMin) * (R - L); }}
    function sy(lat){{ return T + (latMax - lat) / (latMax - latMin) * (B - T); }}

    svg.appendChild(el("rect", {{x: L, y: T, width: R - L, height: B - T, fill: "none", stroke: "var(--rule)"}}));
    var lats = k === "med" ? [35, 40, 45, 50] : [-30, 0, 30, 60];
    lats.forEach(function(lv){{
      var y = sy(lv);
      svg.appendChild(el("line", {{x1: L, x2: R, y1: y, y2: y, stroke: "var(--rule)", "stroke-dasharray": lv === 0 ? "4,3" : "2,4", opacity: 0.6}}));
      svg.appendChild(el("text", {{x: L - 4, y: y + 3, "text-anchor": "end", "font-size": 9, fill: "var(--muted)"}}, lv + "°"));
    }});
    var lons = k === "med" ? [0, 10, 20, 30, 40] : [-120, -60, 0, 60, 120];
    lons.forEach(function(ln){{
      var x = sx(ln);
      svg.appendChild(el("line", {{x1: x, x2: x, y1: T, y2: B, stroke: "var(--rule)", "stroke-dasharray": "2,4", opacity: 0.45}}));
      svg.appendChild(el("text", {{x: x, y: B + 14, "text-anchor": "middle", "font-size": 9, fill: "var(--muted)"}}, ln + "°"));
    }});

    // Highlight Mediterranean/Anatolia wild-cereal native range box
    var bx1 = Math.max(L, sx(-5)), bx2 = Math.min(R, sx(46)), by1 = Math.max(T, sy(45)), by2 = Math.min(B, sy(32));
    svg.appendChild(el("rect", {{x: bx1, y: by1, width: bx2 - bx1, height: by2 - by1, fill: "var(--copper)", opacity: 0.08, stroke: "var(--copper)", "stroke-dasharray": "4,3", "stroke-width": 1}}));
    svg.appendChild(el("text", {{x: bx1 + 4, y: by2 - 5, "font-size": 9.2, fill: "var(--copper)"}}, "Mediterranean and Anatolia"));

    // Draw background points first, then highlighted strict hits
    var order = {{occ: 0, lg_relaxed: 1, lgm_strict: 2, lg_strict: 3}};
    var sorted = PTS.slice().sort(function(a,b){{ return order[a.st] - order[b.st]; }});
    sorted.forEach(function(p){{
      if (p.lon < lonMin || p.lon > lonMax || p.lat < latMin || p.lat > latMax) return;
      var cx = sx(p.lon), cy = sy(p.lat);
      var tip = p.name + " (DS " + p.id + ", " + p.lat + "°, " + p.lon + "°) | " + p.taxa + " | max " + p.crop + "%";
      if (p.st === "lg_strict") {{
        var d = "M" + cx + "," + (cy - 7) + " L" + (cx + 7) + "," + cy + " L" + cx + "," + (cy + 7) + " L" + (cx - 7) + "," + cy + " Z";
        var sh = el("path", {{d: d, fill: "var(--copper)", stroke: "#fff", "stroke-width": 1.2}});
        sh.appendChild(el("title", {{}}, "Late Glacial STRICT (12–18 ka): " + tip));
        svg.appendChild(sh);
        if (k === "med") {{
          svg.appendChild(el("text", {{x: cx + 9, y: cy - 3, "font-size": 10, "font-weight": 700, fill: "var(--copper)"}}, p.name + " (14–15 ka)"));
        }}
      }} else if (p.st === "lgm_strict") {{
        var sq = el("rect", {{x: cx - 5.5, y: cy - 5.5, width: 11, height: 11, fill: "#0f766e", stroke: "#fff", "stroke-width": 1.2}});
        sq.appendChild(el("title", {{}}, "Deep LGM/MIS 3 STRICT (18–50 ka): " + tip));
        svg.appendChild(sq);
        if (k === "med") {{
          var ageLbl = p.id === 26608 ? "22.5 ka" : "36.6 ka";
          svg.appendChild(el("text", {{x: cx + 9, y: cy + 10, "font-size": 10, "font-weight": 700, fill: "#0f766e"}}, p.name + " (" + ageLbl + ")"));
        }}
      }} else if (p.st === "lg_relaxed") {{
        var c = el("circle", {{cx: cx.toFixed(1), cy: cy.toFixed(1), r: k === "med" ? 4.2 : 3.2, fill: "var(--teal)", opacity: 0.78, stroke: "#fff", "stroke-width": 0.4}});
        c.appendChild(el("title", {{}}, "Late Glacial RELAXED: " + tip));
        svg.appendChild(c);
      }} else {{
        var g = el("circle", {{cx: cx.toFixed(1), cy: cy.toFixed(1), r: k === "med" ? 3.0 : 2.3, fill: "#94a3b8", opacity: 0.55}});
        g.appendChild(el("title", {{}}, "Isolated pre-12 ka grain: " + tip));
        svg.appendChild(g);
      }}
    }});
    svg.appendChild(el("text", {{x: L, y: 18, "font-size": 11.5, "font-weight": 600, fill: "var(--ink)"}}, k === "med" ? "Zoom: Mediterranean & Anatolia (all 4 chron-verified FARM_STRICT pre-12 ka hits)" : "Global Neotoma cores with ≥1 pre-12,000 BP crop/cereal-type pollen grain (n=150 audited)"));
    svg.appendChild(el("text", {{x: (L+R)/2, y: 322, "text-anchor": "middle", "font-size": 10, fill: "var(--muted)"}}, "◆ Copper diamond = 12–18 ka STRICT (n=2)  ·  ■ Teal square = 18–50 ka LGM STRICT (n=2)  ·  ● Teal = 12–18 ka RELAXED  ·  ● Slate = isolated grain"));
  }}
  btns.forEach(function(b){{
    b.addEventListener("click", function(){{
      btns.forEach(function(x){{ x.classList.remove("is-on"); x.style.background = "transparent"; x.style.color = "var(--ink)"; }});
      b.classList.add("is-on"); b.style.background = "var(--copper)"; b.style.color = "#fff";
      draw(b.getAttribute("data-k"));
    }});
  }});
  draw("global");
}})();
</script>
</figure>
"""
    (OUT / "global_pre12ka_map.html").write_text(html_out, encoding="utf-8")


def main() -> None:
    s = json.loads((RES / "ice_age_farming_summary.json").read_text(encoding="utf-8"))
    make_tiles(s)
    make_calibration_and_sweep(s)
    make_global_map(s)
    print(f"Wrote 3 figures to {OUT}")


if __name__ == "__main__":
    main()
