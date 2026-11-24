#!/usr/bin/env python3
"""Generate interactive HTML/SVG figures for #44 (flood-myths)."""
from __future__ import annotations

import html
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
RES = ROOT / "results"
OUT = ROOT.parent.parent / "site" / "figures" / "flood-myths"
OUT.mkdir(parents=True, exist_ok=True)


def esc(s: object) -> str:
    return html.escape(str(s), quote=True)


def make_tiles(s: dict) -> None:
    m4_nb = s["models"]["coastal_150km"]["nb_flood_share_z"]["M4"]
    m4_fr = s["models"]["coastal_150km"]["flood_related_z"]["M4"]
    eq = s["calibration"]["pos_earthquake_vs_quake_prox_langFE"]
    qs = s["coastal_quartiles"]
    items = [
        (f"{qs[3]['any_nb_flood_pct']:.1f}% vs. {qs[0]['any_nb_flood_pct']:.1f}%", "non-biblical flood-myth rate on the widest drowned shelves (Q4: 40k–187k km²) vs. steepest shelves (Q1: <10.4k km²) across 396 coastal societies", False),
        (f"β = {m4_nb['beta']:+.3f} SD", f"coastal M4 slope (75 language-family FE + climate/river/quake controls): p = {m4_nb['p_conley_1000']:.2f} (Conley 1,000 km), p = {m4_nb['p_perm_within_continent']:.2f} (perm)", False),
        (f"β = {eq['beta']:+.3f} SD", f"positive control in the same 927 societies: earthquake myths track real seismic zones even with language-family FE (p = {eq['p_conley_1000']:.4f})", False),
        ("Null", "Worldwide flood myths do not cluster where Ice Age shelves drowned—under −120 m, −60 m Holocene, Noah-free, or regional checks", True),
    ]
    body = ['<div class="tiles">']
    for v, lbl, is_w in items:
        cls = "tile-value is-word" if is_w else "tile-value"
        body.append(f'<div class="tile"><p class="{cls}">{esc(v)}</p><p class="tile-label">{esc(lbl)}</p></div>')
    body.append("</div>\n")
    (OUT / "tiles.html").write_text("\n".join(body), encoding="utf-8")


def make_quartiles_and_forest(s: dict) -> None:
    m = s["models"]["coastal_150km"]
    nf = s["models"]["coastal_noah_free"]
    es = s["exposure_sensitivity_coastal"]
    cal = s["calibration"]

    def row(label, r, kind):
        return {
            "lbl": label,
            "b": round(r["beta"], 4),
            "se": round(r["se_conley_1000"], 4),
            "p": round(r["p_conley_1000"], 4),
            "kind": kind,
        }

    forest = [
        row("Positive control: Earthquakes vs. seismic proximity (Lang FE)", cal["pos_earthquake_vs_quake_prox_langFE"], "pos"),
        row("Negative control: Fire vs. drowned shelf (Coastal M4)", cal["neg_fire_vs_drowned120_coastal_M4"], "neg"),
        row("Non-biblical flood share — Coastal M1 (sampling + coast)", m["nb_flood_share_z"]["M1"], "main"),
        row("Non-biblical flood share — Coastal M2 (+ river/quake/climate)", m["nb_flood_share_z"]["M2"], "main"),
        row("Non-biblical flood share — Coastal M3 (+ continent FE)", m["nb_flood_share_z"]["M3"], "main"),
        row("Non-biblical flood share — Coastal M4 (PRIMARY, + 75 Lang FE)", m["nb_flood_share_z"]["M4"], "primary"),
        row("MX flood_related share — Coastal M4 (+ 75 Lang FE)", m["flood_related_z"]["M4"], "primary"),
        row("Noah-free subsample (n=340) — Non-biblical flood M4", nf["nb_flood_share_z"]["M4"], "main"),
        row("Holocene −60 m shelf (12–7 ka) — Non-biblical flood M4", es["log_drowned_60m_250km"]["nb_flood_share_z"]["M4"], "main"),
        row("Wider 500 km radius (−120 m) — Non-biblical flood M4", es["log_drowned_120m_500km"]["nb_flood_share_z"]["M4"], "main"),
        row("Shallow-shelf fraction of sea — Non-biblical flood M4", es["drowned_frac_ocean_250km"]["nb_flood_share_z"]["M4"], "main"),
    ]
    payload = {
        "quartiles": s["coastal_quartiles"],
        "forest": forest,
    }
    data_json = json.dumps(payload)
    html_out = f"""<figure class="fig" aria-label="Coastal drowned-shelf quartiles and spatial regression forest plot for flood myths">
<div class="fig-controls" style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px;align-items:center">
  <span style="font-size:12px;color:var(--muted);margin-right:4px">View:</span>
  <button type="button" class="fm-c-btn is-on" data-k="forest" style="font-size:12px;padding:4px 9px;border:1px solid var(--rule);border-radius:4px;background:var(--copper);color:#fff;cursor:pointer">Spatial Regression Forest Plot (Conley 1,000 km 95% CI)</button>
  <button type="button" class="fm-c-btn" data-k="quartiles" style="font-size:12px;padding:4px 9px;border:1px solid var(--rule);border-radius:4px;background:transparent;color:var(--ink);cursor:pointer">Coastal Shelf Quartiles (Q1 Steep → Q4 Wide)</button>
</div>
<div class="fig-scroll">
<svg id="fm-c-svg" class="chart" viewBox="0 0 720 355" role="img" aria-label="Flood myth slopes and coastal shelf quartiles" xmlns="http://www.w3.org/2000/svg"></svg>
</div>
<figcaption><strong>Flood myths vs. post-glacial drowned continental shelf across 396 coastal societies (&le;150 km from modern ocean).</strong> In the forest plot, horizontal bars show 95% Conley (1999) spatial-HAC confidence intervals at a 1,000 km Bartlett cutoff (standard deviations of motif share per 1-SD increase in exposure). The positive control (earthquake myths vs. proximity to seismic zones, teal) is clearly positive (&beta; = +0.157 SD, p = 0.0005). Every drowned-shelf flood-myth model—from M1 to primary M4 with 75 language-family fixed effects, Noah-free subsamples, and Holocene &minus;60 m shelves—sits dead on zero or slightly negative. The quartile toggle confirms the raw pattern: societies beside the widest drowned shelves (Q4: 40k–187k km&sup2;) actually have slightly <em>fewer</em> non-biblical flood myths (34.3%) than societies on the steepest shelves (Q1: 36.4%).</figcaption>
<script>
(function(){{
  var D = {data_json};
  var svg = document.getElementById("fm-c-svg");
  var btns = document.querySelectorAll(".fm-c-btn");
  function el(tag, attrs, txt){{
    var n = document.createElementNS("http://www.w3.org/2000/svg", tag);
    for (var k in attrs) n.setAttribute(k, attrs[k]);
    if (txt !== undefined) n.textContent = txt;
    return n;
  }}
  function draw(k){{
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    if (k === "forest") {{
      var L = 325, R = 680, T = 30, B = 315;
      var xmin = -0.36, xmax = 0.32;
      function sx(v){{ return L + (v - xmin) / (xmax - xmin) * (R - L); }}
      svg.appendChild(el("text", {{x: 16, y: 18, "font-size": 12, "font-weight": 600, fill: "var(--ink)"}}, "Effect size (SD of motif share per 1-SD exposure) with 95% Conley 1,000 km CIs"));
      var x0 = sx(0);
      svg.appendChild(el("line", {{x1: x0, x2: x0, y1: T, y2: B, stroke: "var(--ink)", "stroke-dasharray": "4,3", "stroke-width": 1.1}}));
      svg.appendChild(el("line", {{x1: L, x2: R, y1: B, y2: B, stroke: "var(--rule)"}}));
      [-0.3, -0.2, -0.1, 0, 0.1, 0.2, 0.3].forEach(function(tv){{
        var tx = sx(tv);
        svg.appendChild(el("line", {{x1: tx, x2: tx, y1: B, y2: B + 4, stroke: "var(--muted)"}}));
        svg.appendChild(el("text", {{x: tx, y: B + 17, "text-anchor": "middle", "font-size": 10, fill: "var(--muted)"}}, (tv > 0 ? "+" : "") + tv.toFixed(1)));
      }});
      var step = (B - T) / D.forest.length;
      D.forest.forEach(function(r, i){{
        var cy = T + (i + 0.5) * step;
        var col = r.kind === "pos" ? "var(--teal)" : (r.kind === "primary" ? "var(--copper)" : (r.kind === "neg" ? "#64748b" : "#475569"));
        var lo = sx(Math.max(xmin, r.b - 1.96 * r.se));
        var hi = sx(Math.min(xmax, r.b + 1.96 * r.se));
        var cx = sx(r.b);
        svg.appendChild(el("text", {{x: L - 8, y: cy + 3.5, "text-anchor": "end", "font-size": 10.5, "font-weight": (r.kind === "primary" || r.kind === "pos") ? 600 : 400, fill: (r.kind === "primary" || r.kind === "pos") ? col : "var(--ink)"}}, r.lbl));
        svg.appendChild(el("line", {{x1: lo, x2: hi, y1: cy, y2: cy, stroke: col, "stroke-width": r.kind === "primary" ? 2.4 : 1.7}}));
        svg.appendChild(el("circle", {{cx: cx, cy: cy, r: r.kind === "primary" ? 4.3 : 3.5, fill: col}}));
        svg.appendChild(el("text", {{x: hi + 5, y: cy + 3.5, "font-size": 9.5, fill: "var(--muted)"}}, (r.b >= 0 ? "+" : "") + r.b.toFixed(2) + " (p=" + (r.p < 0.001 ? "<.001" : r.p.toFixed(2)) + ")"));
      }});
    }} else {{
      var L = 70, R = 685, T = 40, B = 280;
      svg.appendChild(el("text", {{x: L, y: 20, "font-size": 12, "font-weight": 600, fill: "var(--ink)"}}, "396 Coastal Societies by Quartile of Drowned Continental Shelf (−120 m to 0 m within 250 km)"));
      function sy(v){{ return B - (v / 50) * (B - T); }}
      svg.appendChild(el("line", {{x1: L, x2: R, y1: B, y2: B, stroke: "var(--rule)"}}));
      svg.appendChild(el("line", {{x1: L, x2: L, y1: T, y2: B, stroke: "var(--rule)"}}));
      [0, 10, 20, 30, 40, 50].forEach(function(yv){{
        svg.appendChild(el("text", {{x: L - 8, y: sy(yv) + 3.5, "text-anchor": "end", "font-size": 10, fill: "var(--muted)"}}, yv + "%"));
      }});
      var step = (R - L) / 4;
      D.quartiles.forEach(function(q, i){{
        var cx = L + (i + 0.5) * step;
        var y1 = sy(q.any_nb_flood_pct);
        svg.appendChild(el("rect", {{x: cx - 38, y: y1, width: 76, height: B - y1, rx: 3, fill: i === 3 ? "var(--copper)" : "#94a3b8", opacity: 0.88}}));
        svg.appendChild(el("text", {{x: cx, y: y1 - 7, "text-anchor": "middle", "font-size": 12, "font-weight": 700, fill: i === 3 ? "var(--copper)" : "var(--ink)"}}, q.any_nb_flood_pct.toFixed(1) + "%"));
        svg.appendChild(el("text", {{x: cx, y: B + 17, "text-anchor": "middle", "font-size": 11, "font-weight": 600, fill: "var(--ink)"}}, q.quartile + " (n=" + q.n + ")"));
        svg.appendChild(el("text", {{x: cx, y: B + 32, "text-anchor": "middle", "font-size": 9.8, fill: "var(--muted)"}}, Math.round(q.drowned_lo_km2/1000) + "k–" + Math.round(q.drowned_hi_km2/1000) + "k km²"));
      }});
      svg.appendChild(el("text", {{x: (L+R)/2, y: 336, "text-anchor": "middle", "font-size": 11, fill: "var(--muted)"}}, "Share of coastal societies with ≥1 non-biblical Berezkin deluge/flood motif (inland >150 km baseline = 39.4%)"));
    }}
  }}
  btns.forEach(function(b){{
    b.addEventListener("click", function(){{
      btns.forEach(function(x){{ x.classList.remove("is-on"); x.style.background = "transparent"; x.style.color = "var(--ink)"; }});
      b.classList.add("is-on"); b.style.background = "var(--copper)"; b.style.color = "#fff";
      draw(b.getAttribute("data-k"));
    }});
  }});
  draw("forest");
}})();
</script>
</figure>
"""
    (OUT / "coastal_quartiles_and_models.html").write_text(html_out, encoding="utf-8")


def make_world_and_regional(s: dict) -> None:
    payload = {
        "pts": s["map_points"],
        "reg": s["regional_coastal"],
    }
    data_json = json.dumps(payload)
    html_out = f"""<figure class="fig" aria-label="Global distribution of Berezkin flood myths and regional drowned-shelf slopes">
<div class="fig-controls" style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px;align-items:center">
  <span style="font-size:12px;color:var(--muted);margin-right:4px">Geographic view:</span>
  <button type="button" class="fm-m-btn is-on" data-k="coastal" style="font-size:12px;padding:4px 9px;border:1px solid var(--rule);border-radius:4px;background:var(--copper);color:#fff;cursor:pointer">396 Coastal Societies (Sized by Drowned Shelf)</button>
  <button type="button" class="fm-m-btn" data-k="all" style="font-size:12px;padding:4px 9px;border:1px solid var(--rule);border-radius:4px;background:transparent;color:var(--ink);cursor:pointer">All 927 Berezkin Societies</button>
  <button type="button" class="fm-m-btn" data-k="regional" style="font-size:12px;padding:4px 9px;border:1px solid var(--rule);border-radius:4px;background:transparent;color:var(--ink);cursor:pointer">Regional Slopes (6 Continents)</button>
</div>
<div class="fig-scroll">
<svg id="fm-m-svg" class="chart" viewBox="0 0 720 330" role="img" aria-label="Global map of Berezkin flood myths and regional regression slopes" xmlns="http://www.w3.org/2000/svg"></svg>
</div>
<figcaption><strong>Global geography of non-biblical flood myths and regional drowned-shelf slopes.</strong> Copper circles mark societies with &ge;1 non-biblical Berezkin deluge/flood motif; slate dots mark societies without. Circle area in the coastal view scales with post-glacial drowned continental shelf area (&minus;120 m to 0 m within 250 km). Flood myths occur across inland and steep-coast regions alike (North America, South America, inland Eurasia), while major drowned-shelf regions—North Sea/Europe, coastal Australia/Sahul (18.8%), and Sundaland/Oceania—show no systematic excess.</figcaption>
<script>
(function(){{
  var D = {data_json};
  var svg = document.getElementById("fm-m-svg");
  var btns = document.querySelectorAll(".fm-m-btn");
  function el(tag, attrs, txt){{
    var n = document.createElementNS("http://www.w3.org/2000/svg", tag);
    for (var k in attrs) n.setAttribute(k, attrs[k]);
    if (txt !== undefined) n.textContent = txt;
    return n;
  }}
  function draw(k){{
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    if (k === "regional") {{
      var L = 165, R = 670, T = 36, B = 280;
      var xmin = -0.45, xmax = 0.35;
      function sx(v){{ return L + (v - xmin) / (xmax - xmin) * (R - L); }}
      svg.appendChild(el("text", {{x: 20, y: 20, "font-size": 12, "font-weight": 600, fill: "var(--ink)"}}, "Regional M2 slopes (Coastal societies, Non-biblical flood share vs. log drowned shelf)"));
      var x0 = sx(0);
      svg.appendChild(el("line", {{x1: x0, x2: x0, y1: T, y2: B, stroke: "var(--ink)", "stroke-dasharray": "4,3"}}));
      svg.appendChild(el("line", {{x1: L, x2: R, y1: B, y2: B, stroke: "var(--rule)"}}));
      [-0.4, -0.2, 0, 0.2].forEach(function(tv){{
        svg.appendChild(el("text", {{x: sx(tv), y: B + 17, "text-anchor": "middle", "font-size": 10, fill: "var(--muted)"}}, (tv > 0 ? "+" : "") + tv.toFixed(1)));
      }});
      var step = (B - T) / D.reg.length;
      D.reg.forEach(function(r, i){{
        var y = T + i * step + 6, h = step - 12;
        var b = r.nb_flood_beta_M2;
        var xA = Math.min(x0, sx(b)), w = Math.max(2, Math.abs(sx(b) - x0));
        svg.appendChild(el("text", {{x: L - 8, y: y + h * 0.72, "text-anchor": "end", "font-size": 11, fill: "var(--ink)"}}, r.region + " (n=" + r.n_coastal + ")"));
        svg.appendChild(el("rect", {{x: xA, y: y, width: w, height: h, rx: 2, fill: b >= 0 ? "var(--copper)" : "var(--teal)", opacity: 0.85}}));
        var lblX = b >= 0 ? sx(b) + 6 : sx(b) - 6;
        svg.appendChild(el("text", {{x: lblX, y: y + h * 0.72, "text-anchor": b >= 0 ? "start" : "end", "font-size": 10, fill: "var(--muted)"}}, (b >= 0 ? "+" : "") + b.toFixed(3) + " (p=" + r.nb_flood_p_conley500.toFixed(2) + ")"));
      }});
      svg.appendChild(el("text", {{x: (L+R)/2, y: 316, "text-anchor": "middle", "font-size": 11, fill: "var(--muted)"}}, "Zero continents reach p < 0.05 positive; Australia/Sahul (n=16) Spearman ρ = −0.41"));
      return;
    }}
    var L = 30, R = 690, T = 26, B = 294;
    function sx(lon){{ return L + (lon + 180) / 360 * (R - L); }}
    function sy(lat){{ return T + (82 - lat) / 142 * (B - T); }}
    svg.appendChild(el("rect", {{x: L, y: T, width: R - L, height: B - T, fill: "none", stroke: "var(--rule)"}}));
    // Equator & 30/60 lat lines
    [-30, 0, 30, 60].forEach(function(lat){{
      var y = sy(lat);
      svg.appendChild(el("line", {{x1: L, x2: R, y1: y, y2: y, stroke: "var(--rule)", "stroke-dasharray": lat === 0 ? "4,3" : "2,4", opacity: 0.7}}));
      svg.appendChild(el("text", {{x: L + 3, y: y - 3, "font-size": 9, fill: "var(--muted)"}}, lat === 0 ? "0°" : lat + "°"));
    }});
    var pts = k === "coastal" ? D.pts.filter(function(p){{ return p.c === 1; }}) : D.pts;
    pts.forEach(function(p){{
      var r = k === "coastal" ? (2.2 + Math.sqrt(Math.max(0, p.d120)) / 75.0) : 2.3;
      svg.appendChild(el("circle", {{
        cx: sx(p.lon).toFixed(1), cy: sy(p.lat).toFixed(1), r: r.toFixed(1),
        fill: p.nb ? "var(--copper)" : "#94a3b8",
        opacity: p.nb ? 0.85 : 0.45,
        stroke: p.nb ? "#fff" : "none", "stroke-width": 0.4
      }}));
    }});
    svg.appendChild(el("text", {{x: L, y: 17, "font-size": 11.5, "font-weight": 600, fill: "var(--ink)"}}, k === "coastal" ? "396 coastal societies (≤150 km): copper = non-biblical flood myth, size = drowned shelf area" : "All 927 Berezkin societies: copper = non-biblical flood myth (37.9% global, 35.9% coastal, 39.4% inland)"));
    svg.appendChild(el("text", {{x: (L+R)/2, y: 318, "text-anchor": "middle", "font-size": 10.5, fill: "var(--muted)"}}, "Equirectangular projection (−180° to +180° longitude; −60° to +82° latitude)"));
  }}
  btns.forEach(function(b){{
    b.addEventListener("click", function(){{
      btns.forEach(function(x){{ x.classList.remove("is-on"); x.style.background = "transparent"; x.style.color = "var(--ink)"; }});
      b.classList.add("is-on"); b.style.background = "var(--copper)"; b.style.color = "#fff";
      draw(b.getAttribute("data-k"));
    }});
  }});
  draw("coastal");
}})();
</script>
</figure>
"""
    (OUT / "world_map.html").write_text(html_out, encoding="utf-8")


def main():
    summary = json.loads((RES / "flood_myths_summary.json").read_text(encoding="utf-8"))
    make_tiles(summary)
    make_quartiles_and_forest(summary)
    make_world_and_regional(summary)
    print("Generated 3 figures in", OUT)


if __name__ == "__main__":
    main()
