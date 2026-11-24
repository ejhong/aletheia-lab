#!/usr/bin/env python3
"""
Generate 5 self-contained, zero-dependency interactive HTML figures for
site/figures/yd-megafauna-timing/ strictly from locked results/summary.json.

Figures produced:
  1. tiles.html        - Native .tiles headline strip (plain English)
  2. verdict.html      - Native .verdict pre-registered check table
  3. sporormiella.html - Interactive 11-core North American dung-fungus explorer
  4. radiocarbon.html  - Interactive IntCal20 fossil density vs H_impact plateau envelope
  5. taxa.html         - Interactive per-taxon Signor-Lipps extinction timeline (OLE & GRIWM)
"""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT.parent.parent
RESULTS = ROOT / "results"
OUT_DIR = REPO / "site" / "figures" / "yd-megafauna-timing"

esc = lambda s: html.escape(str(s), quote=True)

COMMON_NAMES = {
    "Equus": "North American horse (Equus)",
    "Mammuthus": "Mammoth (Mammuthus)",
    "Mammut": "American mastodon (Mammut)",
    "Oreamnos harringtoni": "Harrington's mountain goat",
    "Nothrotheriops": "Shasta ground sloth",
    "Smilodon": "Saber-toothed cat (Smilodon)",
    "Canis dirus": "Dire wolf (Canis dirus)",
    "Arctodus": "Giant short-faced bear",
    "Camelops": "Western camel (Camelops)",
    "Castoroides": "Giant beaver (Castoroides)",
    "Panthera leo atrox": "American lion",
}


def build_tiles(summary: dict) -> str:
    p1 = summary["pillar1_sporormiella"]
    p2 = summary["pillar2_radiocarbon"]
    t50 = p1["tests"]["t_50pct"]["vs_12896"]
    s12 = p2["subsets"]["score12_ams"]
    surv_s12 = p2["survivors"]["n_s12_p95"]
    m_ratio = s12["obs_raw"]["m_yd"] / s12["h_impact_uniform"]["raw"]["m_yd_p990"]

    items = [
        (
            f"{t50['n_before']} of {t50['n']}",
            f"lake and cave cores show herbivore dung spores falling past half their peak before the Younger Dryas began (median {t50['median']:,.0f} years ago — {t50['median_lead_yr']:,.0f} years early)",
            False,
        ),
        (
            f"{surv_s12}",
            "modern AMS collagen dates from mammoths, mastodons, a giant beaver and a short-faced bear fall squarely after 12,750 years ago (each >99% sure, up to 1,900 years past the claimed impact)",
            False,
        ),
        (
            f"{m_ratio:.1f}×",
            f"more fossil probability inside the Younger Dryas ({s12['obs_raw']['m_yd']*100:.1f}%) than calibration-curve smearing can produce after an instant 12,850-year wipeout (at most {s12['h_impact_uniform']['raw']['m_yd_p990']*100:.2f}%, 0 of 2,000 runs)",
            False,
        ),
        (
            "Drawn-out, not one day",
            "Decline began a millennium before the cold, accelerated around 12,800–12,600 years ago, and left giant mammals walking North America for centuries after",
            True,
        ),
    ]
    return '<div class="tiles">\n' + "\n".join(
        f'<div class="tile"><p class="tile-value{" is-word" if w else ""}">{esc(v)}</p>'
        f'<p class="tile-label">{esc(l)}</p></div>'
        for v, l, w in items
    ) + "\n</div>\n"


def build_verdict(summary: dict) -> str:
    p1 = summary["pillar1_sporormiella"]["tests"]
    p2 = summary["pillar2_radiocarbon"]
    s12 = p2["subsets"]["score12_ams"]
    sall = p2["subsets"]["all"]
    t50 = p1["t_50pct"]["vs_12896"]
    tcp = p1["t_cp"]["vs_12896"]
    t2p = p1["t_2pct"]["vs_12896"]
    tons = p1["t_onset"]["vs_12896"]

    rows = [
        (
            "Pillar 1 · Dung spores in lake mud",
            "Did large herbivores start collapsing before the Younger Dryas (12,896 years ago)?",
            f"Yes, in most cores — but not everywhere at once. All {tons['n_before']} of {tons['n']} high-spore cores peaked before the cold (median {tons['median']:,.0f} BP, p = {tons['wilcoxon_p_two_sided']:.4f}), "
            f"{t50['n_before']} of {t50['n']} dropped past half their peak beforehand (median {t50['median']:,.0f} BP, {t50['median_lead_yr']:,.0f} years early, Wilcoxon p = {t50['wilcoxon_p_two_sided']:.4f}), "
            f"and {tcp['n_before']} of {tcp['n']} had their main step-down before the cold (median {tcp['median']:,.0f} BP). "
            f"Yet 3 of {t2p['n']} cores (Colorado, Texas, and one Indiana lake) stayed above 2% spores well into the Younger Dryas.",
            "is-yes",
            "Started ~1,000–1,800 yr early",
        ),
        (
            "Pillar 2 · Radiocarbon plateau test",
            "Could an instant wipeout at 12,850 years ago explain the younger fossils through radiocarbon smearing?",
            f"No. Across 2,000 simulated instant-wipeout catalogues run through IntCal20 with the exact lab errors, plateau smearing leaks at most "
            f"{s12['h_impact_uniform']['raw']['m_yd_p990']*100:.2f}% of probability mass into 12,700–11,700 BP (99th percentile). "
            f"The real AMS record holds {s12['obs_raw']['m_yd']*100:.2f}% — {s12['obs_raw']['m_yd']/s12['h_impact_uniform']['raw']['m_yd_p990']:.1f}× higher (0 of 2,000 runs reach it, p < 0.0005). "
            f"All six subsets and Surovell taphonomy correction give the same p < 0.0005 result.",
            "is-no",
            "Ruled out (p < 0.0005)",
        ),
        (
            "Pillar 2 · Direct bone dates around 12,800 BP",
            "Do direct fossil dates drop before the Younger Dryas, or right at it?",
            f"Here the two archives diverge in an instructive way. Direct AMS bone dates do not fall before 13,000 BP — they surge to {s12['obs_raw']['r_pre']:.2f}× Bølling–Allerød density "
            f"during 13,500–12,900 BP, then plunge roughly tenfold between 12,800 and 12,600 BP — before settling into a real 700-to-1,900-year survival tail. "
            f"Ten gold-standard Score-12 AMS collagen dates (5 mammoths, 3 mastodons, 1 giant beaver, 1 short-faced bear) each have >99.3% probability of living after 12,750 BP.",
            "is-open",
            "Sharp drop, clear survivors",
        ),
        (
            "Pillar 2 · Genus-by-genus extinction",
            "Did North America's giant mammals disappear together or one by one?",
            "One by one, over more than a millennium. On modern Score-12 AMS dates alone (dropping older 1960s–70s conventional outliers), "
            "horses (OLE 13,061 BP, 95% CI 12,715–13,143) and dire wolves (youngest 13,674 BP) vanish before or near the onset of the cold, "
            "while mammoths (OLE 11,852 BP, CI 10,295–12,150), mastodons (OLE 11,867 BP, CI 11,079–12,412), and Harrington's mountain goat (OLE 10,333 BP, CI 7,117–12,329) "
            "all survive centuries into the Younger Dryas.",
            "is-no",
            "Staggered (>1,200 yr span)",
        ),
    ]

    out = ['<div class="verdict" role="region" aria-label="Pre-registered timing checks">']
    for kicker, title, note, cls, status in rows:
        out.append(
            '<div class="verdict-row">'
            f'<div><p class="verdict-kicker">{esc(kicker)}</p>'
            f'<p class="verdict-text">{esc(title)}</p>'
            f'<p class="verdict-note">{esc(note)}</p></div>'
            f'<p class="verdict-status {cls}"><span class="dot" aria-hidden="true"></span>{esc(status)}</p>'
            '</div>'
        )
    out.append("</div>\n")
    return "\n".join(out)


def build_sporormiella_fig(summary: dict) -> str:
    p1 = summary["pillar1_sporormiella"]
    payload = {
        "t_yd": summary["t_yd_gicc05"],
        "t_ydb": summary["t_ydb_kennett"],
        "composite": p1["composite"],
        "sites": [
            {
                "id": s["dataset_id"],
                "name": s["site_name"],
                "state": s["state"],
                "n_samples": s["n_samples"],
                "n_nonzero": s["n_nonzero"],
                "max_pct": round(s["max_pct_17_115"], 2),
                "t_onset": None if s["t_onset"] is None else round(s["t_onset"], 0),
                "t_2pct": None if s["t_2pct"] is None else round(s["t_2pct"], 0),
                "t_50pct": None if s["t_50pct"] is None else round(s["t_50pct"], 0),
                "t_cp": None if s["t_cp"] is None else round(s["t_cp"], 0),
                "r2_step": None if s["r2_step"] is None else round(s["r2_step"], 3),
                "series": s["series"],
            }
            for s in p1["sites"]
        ],
    }
    data_json = json.dumps(payload, separators=(",", ":"))

    return f"""<figure class="fig" id="fig-sporormiella" aria-label="Interactive North American Sporormiella dung-fungus spore record across 11 lake and cave cores">
<style>
#fig-sporormiella .sp-bar{{display:flex;flex-wrap:wrap;align-items:center;gap:.45rem .6rem;margin:0 0 .85rem;font-family:var(--mono);font-size:11px;}}
#fig-sporormiella .sp-label{{text-transform:uppercase;letter-spacing:.14em;color:var(--faint);}}
#fig-sporormiella .sp-select,#fig-sporormiella .sp-btn{{font:500 11px/1.2 var(--mono);padding:.36rem .62rem;border:1px solid var(--line);background:var(--panel);color:var(--ink);border-radius:2px;cursor:pointer;}}
#fig-sporormiella .sp-btn.is-on{{background:var(--copper);border-color:var(--copper);color:#fff;}}
#fig-sporormiella .sp-meta{{margin:0 0 .6rem;font-size:.86rem;color:var(--ink-soft);min-height:1.4em;}}
#fig-sporormiella .sp-readout{{font-family:var(--mono);font-size:11.5px;color:var(--ink);padding:.45rem .7rem;background:var(--panel);border:1px solid var(--line);margin-top:.5rem;min-height:2.1em;}}
#fig-sporormiella svg{{display:block;width:100%;min-width:620px;height:auto;font-family:var(--sans);}}
#fig-sporormiella .sp-row-hit{{cursor:pointer;fill:transparent;}}
#fig-sporormiella .sp-row-hit:hover{{fill:color-mix(in oklab, var(--copper) 8%, transparent);}}
</style>
<div class="sp-bar">
  <span class="sp-label">View</span>
  <button type="button" class="sp-btn is-on" data-mode="composite">Continental composite (11 cores)</button>
  <button type="button" class="sp-btn" data-mode="site">Single lake / cave core</button>
  <select class="sp-select" aria-label="Choose a lake or cave core">
    <option value="14957">Appleman Lake, IN (56 samples)</option>
    <option value="17717">Silver Lake, OH (49 samples)</option>
    <option value="61900">Mono Lake, CA (52 samples)</option>
    <option value="16175">Binnewater Pond, NY (29 samples)</option>
    <option value="16179">Otisville, NY (16 samples)</option>
    <option value="46645">Lower Paintrock Lake, WY (36 samples)</option>
    <option value="47259">Hall's Cave, TX (17 samples)</option>
    <option value="3056">Como Lake, CO (10 samples)</option>
    <option value="19937">Spicer Lake, IN (43 samples)</option>
    <option value="45695">Triangle Lake Bog, OH (79 samples)</option>
    <option value="15876">Tulare Lake, CA (10 samples)</option>
  </select>
</div>
<p class="sp-meta" id="sp-meta"></p>
<div class="fig-scroll">
  <svg id="sp-svg" viewBox="0 0 740 500" role="img" aria-label="Sporormiella dung-fungus spore trajectory and per-core decline ages across North America"></svg>
</div>
<div class="sp-readout" id="sp-readout">Move across the curve or click any core in the lower strip to inspect its individual dung-spore record.</div>
<figcaption>Dung-fungus spores (<em>Sporormiella</em>) as a proxy for large-herbivore biomass across 11 calibrated North American Neotoma cores (7 US states, 16,500 to 10,200 years ago; older to the left, younger to the right). Top panel shows either the cross-site normalized median with 5,000-draw site-bootstrap 95% band, or any individual core's raw upland-pollen percentage with its classic 2% functional-extinction line. Lower strip plots each core's half-drop age (circle, 9 of 11 before Younger Dryas onset, Wilcoxon p = 0.014) and step-drop changepoint (diamond, 7 of 10 before onset). Click any core row to open its full curve.</figcaption>
<script>
(function(){{
  const D = {data_json};
  const root = document.getElementById("fig-sporormiella");
  const svg = document.getElementById("sp-svg");
  const meta = document.getElementById("sp-meta");
  const readout = document.getElementById("sp-readout");
  const sel = root.querySelector(".sp-select");
  const btns = root.querySelectorAll(".sp-btn");
  const NS = "http://www.w3.org/2000/svg";

  let mode = "composite";
  let activeId = 14957;

  const W = 740, L = 142, R = 716;
  const T_MAX = 16600, T_MIN = 10200;
  const sx = t => L + (T_MAX - t) / (T_MAX - T_MIN) * (R - L);

  function el(tag, attrs, text){{
    const n = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs || {{}})) n.setAttribute(k, String(v));
    if (text !== undefined) n.textContent = text;
    return n;
  }}

  // Sort cores chronologically by t_50pct (oldest first) for the lower strip
  const sortedSites = [...D.sites].sort((a, b) => (b.t_50pct || 0) - (a.t_50pct || 0));

  function render(){{
    svg.innerHTML = "";
    const topY = 26, topH = 190, botTop = 264, rowH = 18.5;

    // Background YD cooling shading (12,896 to 11,700 BP)
    const xYD0 = sx(12896), xYD1 = sx(11700);
    svg.appendChild(el("rect", {{x: xYD0, y: topY, width: xYD1 - xYD0, height: topH, fill: "var(--slate)", opacity: 0.11}}));
    svg.appendChild(el("rect", {{x: xYD0, y: botTop - 8, width: xYD1 - xYD0, height: sortedSites.length * rowH + 12, fill: "var(--slate)", opacity: 0.09}}));

    // Vertical time gridlines
    for (let t = 16000; t >= 11000; t -= 1000){{
      const x = sx(t);
      svg.appendChild(el("line", {{x1: x, x2: x, y1: topY, y2: topY + topH, stroke: "var(--line)", "stroke-width": 1}}));
      svg.appendChild(el("line", {{x1: x, x2: x, y1: botTop - 6, y2: botTop + sortedSites.length * rowH, stroke: "var(--line)", "stroke-width": 1, opacity: 0.65}}));
      svg.appendChild(el("text", {{x, y: topY + topH + 16, "text-anchor": "middle", fill: "var(--faint)", "font-size": 11}}, (t / 1000).toFixed(0) + "k"));
    }}

    // Reference line: YD onset 12,896 cal BP
    svg.appendChild(el("line", {{x1: xYD0, x2: xYD0, y1: topY - 6, y2: botTop + sortedSites.length * rowH + 4, stroke: "var(--copper)", "stroke-width": 1.6, "stroke-dasharray": "4 3"}}));
    svg.appendChild(el("text", {{x: xYD0 - 5, y: topY - 10, "text-anchor": "end", fill: "var(--copper)", "font-size": 11, "font-weight": 600}}, "YD cold starts (12,896 BP)"));
    svg.appendChild(el("text", {{x: (xYD0 + xYD1) / 2, y: topY + 13, "text-anchor": "middle", fill: "var(--faint)", "font-size": 10}}, "Younger Dryas"));

    // Reference line: Bolling-Allerod onset ~14,700 BP
    const xBA = sx(14700);
    svg.appendChild(el("line", {{x1: xBA, x2: xBA, y1: topY, y2: topY + topH, stroke: "var(--verdigris)", "stroke-width": 1, "stroke-dasharray": "2 4", opacity: 0.75}}));
    svg.appendChild(el("text", {{x: xBA - 4, y: topY + 13, "text-anchor": "end", fill: "var(--verdigris)", "font-size": 10}}, "B–A warming (14.7k)"));

    // Top panel axes
    svg.appendChild(el("line", {{x1: L, x2: R, y1: topY + topH, y2: topY + topH, stroke: "var(--faint)", "stroke-width": 1}}));

    if (mode === "composite"){{
      const pts = D.composite.filter(p => p.median !== null && p.age <= T_MAX && p.age >= T_MIN);
      const yMax = 3.2;
      const sy = v => topY + topH - Math.min(v, yMax) / yMax * (topH - 12);
      for (const v of [0, 1, 2, 3]){{
        const y = sy(v);
        svg.appendChild(el("line", {{x1: L, x2: R, y1: y, y2: y, stroke: "var(--line)", "stroke-width": 0.7, opacity: 0.6}}));
        svg.appendChild(el("text", {{x: L - 8, y: y + 4, "text-anchor": "end", fill: "var(--faint)", "font-size": 11}}, v.toFixed(0) + "×"));
      }}
      svg.appendChild(el("text", {{x: 8, y: topY + 14, fill: "var(--faint)", "font-size": 10.5, "font-family": "var(--mono)"}}, "CONTINENTAL MEDIAN"));
      svg.appendChild(el("text", {{x: 8, y: topY + 29, fill: "var(--faint)", "font-size": 10.5}}, "relative to each core's"));
      svg.appendChild(el("text", {{x: 8, y: topY + 43, fill: "var(--faint)", "font-size": 10.5}}, "17–10k mean (95% CI)"));

      // Bootstrap CI polygon
      const up = pts.map(p => `${{sx(p.age).toFixed(1)}},${{sy(p.median_ci_hi).toFixed(1)}}`).join(" L");
      const dn = [...pts].reverse().map(p => `${{sx(p.age).toFixed(1)}},${{sy(p.median_ci_lo).toFixed(1)}}`).join(" L");
      svg.appendChild(el("path", {{d: `M${{up}} L${{dn}} Z`, fill: "var(--copper)", opacity: 0.17}}));

      // Mean dashed line
      const meanPath = pts.map(p => `${{sx(p.age).toFixed(1)}},${{sy(p.mean).toFixed(1)}}`).join(" L");
      svg.appendChild(el("path", {{d: `M${{meanPath}}`, fill: "none", stroke: "var(--faint)", "stroke-width": 1.3, "stroke-dasharray": "4 3"}}));

      // Median solid copper line
      const medPath = pts.map(p => `${{sx(p.age).toFixed(1)}},${{sy(p.median).toFixed(1)}}`).join(" L");
      svg.appendChild(el("path", {{d: `M${{medPath}}`, fill: "none", stroke: "var(--copper)", "stroke-width": 2.6}}));

      // Interactive hover targets
      pts.forEach(p => {{
        const x = sx(p.age), y = sy(p.median);
        const hit = el("rect", {{x: x - 9, y: topY, width: 18, height: topH, fill: "transparent", style: "cursor:crosshair"}});
        hit.addEventListener("mouseenter", () => {{
          readout.textContent = `${{p.age.toLocaleString()}} cal BP (${{p.n_sites}} cores) · Median normalized spores = ${{p.median.toFixed(2)}}× (95% CI ${{p.median_ci_lo.toFixed(2)}}–${{p.median_ci_hi.toFixed(2)}}×) · Mean = ${{p.mean.toFixed(2)}}×`;
        }});
        svg.appendChild(hit);
        svg.appendChild(el("circle", {{cx: x, cy: y, r: 2.6, fill: "var(--copper)", "pointer-events": "none"}}));
      }});
      meta.innerHTML = "<strong>Continental composite (11 cores, 7 states):</strong> median dung spores drop by more than half between 15,200 BP (1.57×) and 13,000 BP (0.68×), then drift slowly to zero through the Younger Dryas — no cliff at 12,896 BP.";
    }} else {{
      const site = D.sites.find(s => s.id === activeId) || D.sites[0];
      const pts = site.series.filter(p => p.age <= T_MAX && p.age >= T_MIN);
      const yMax = Math.max(2.6, Math.ceil(Math.max(...pts.map(p => p.pct)) * 1.15));
      const sy = v => topY + topH - (v / yMax) * (topH - 12);

      // Y ticks
      const step = yMax > 8 ? 3 : yMax > 4 ? 2 : 1;
      for (let v = 0; v <= yMax; v += step){{
        const y = sy(v);
        svg.appendChild(el("line", {{x1: L, x2: R, y1: y, y2: y, stroke: "var(--line)", "stroke-width": 0.7, opacity: 0.6}}));
        svg.appendChild(el("text", {{x: L - 8, y: y + 4, "text-anchor": "end", fill: "var(--faint)", "font-size": 11}}, v + "%"));
      }}
      // 2% reference line
      if (yMax >= 2.0){{
        const y2 = sy(2.0);
        svg.appendChild(el("line", {{x1: L, x2: R, y1: y2, y2: y2, stroke: "var(--ochre)", "stroke-width": 1.2, "stroke-dasharray": "3 3"}}));
        svg.appendChild(el("text", {{x: R - 4, y: y2 - 4, "text-anchor": "end", fill: "var(--ochre)", "font-size": 10}}, "2% threshold"));
      }}

      svg.appendChild(el("text", {{x: 8, y: topY + 14, fill: "var(--ink)", "font-size": 11, "font-weight": 600}}, site.name + ", " + site.state));
      svg.appendChild(el("text", {{x: 8, y: topY + 30, fill: "var(--faint)", "font-size": 10.5}}, "Sporormiella % upland"));
      svg.appendChild(el("text", {{x: 8, y: topY + 44, fill: "var(--faint)", "font-size": 10.5}}, `${{site.n_samples}} samples (${{site.n_nonzero}} > 0)`));

      // Area & line
      const linePts = pts.map(p => `${{sx(p.age).toFixed(1)}},${{sy(p.pct).toFixed(1)}}`).join(" L");
      if (pts.length >= 2){{
        const areaD = `M${{sx(pts[0].age).toFixed(1)}},${{(topY + topH).toFixed(1)}} L${{linePts}} L${{sx(pts[pts.length-1].age).toFixed(1)}},${{(topY + topH).toFixed(1)}} Z`;
        svg.appendChild(el("path", {{d: areaD, fill: "var(--copper)", opacity: 0.14}}));
        svg.appendChild(el("path", {{d: `M${{linePts}}`, fill: "none", stroke: "var(--copper)", "stroke-width": 2.2}}));
      }}

      // Decline markers
      if (site.t_50pct){{
        const x5 = sx(site.t_50pct);
        svg.appendChild(el("line", {{x1: x5, x2: x5, y1: topY + 18, y2: topY + topH, stroke: "var(--verdigris)", "stroke-width": 1.3}}));
        svg.appendChild(el("text", {{x: x5 + 4, y: topY + 28, fill: "var(--verdigris)", "font-size": 10}}, "50% drop: " + site.t_50pct.toLocaleString()));
      }}
      if (site.t_cp){{
        const xc = sx(site.t_cp);
        svg.appendChild(el("line", {{x1: xc, x2: xc, y1: topY + 34, y2: topY + topH, stroke: "var(--ink)", "stroke-width": 1.2, "stroke-dasharray": "2 2"}}));
        svg.appendChild(el("text", {{x: xc + 4, y: topY + 44, fill: "var(--ink)", "font-size": 10}}, "Step: " + site.t_cp.toLocaleString()));
      }}

      pts.forEach(p => {{
        const x = sx(p.age), y = sy(p.pct);
        const dot = el("circle", {{cx: x, cy: y, r: 3.4, fill: "var(--copper)", stroke: "var(--paper)", "stroke-width": 1.2, style: "cursor:pointer"}});
        dot.addEventListener("mouseenter", () => {{
          readout.textContent = `${{site.name}} (${{site.state}}) at ${{Math.round(p.age).toLocaleString()}} cal BP · Sporormiella = ${{p.pct.toFixed(2)}}% (${{p.n_spo}} spores / ${{p.n_upland}} upland pollen)`;
        }});
        svg.appendChild(dot);
      }});
      const f = v => v ? v.toLocaleString() + " BP" : "n/a";
      meta.innerHTML = `<strong>${{site.name}}, ${{site.state}}:</strong> peak ${{site.max_pct.toFixed(1)}}% · half-drop <code>${{f(site.t_50pct)}}</code> · 2% crossing <code>${{f(site.t_2pct)}}</code> · step changepoint <code>${{f(site.t_cp)}}</code>.`;
    }}

    // Lower strip: all 11 cores decline timing
    svg.appendChild(el("text", {{x: 8, y: botTop - 12, fill: "var(--faint)", "font-size": 10.5, "font-family": "var(--mono)"}}, "ALL 11 CORES (CLICK TO OPEN)"));
    svg.appendChild(el("text", {{x: L, y: botTop - 12, fill: "var(--faint)", "font-size": 10.5}}, "● Half-drop (t₅₀%, 9/11 pre-YD)   ◆ Step changepoint (t_cp, 7/10 pre-YD)   □ 2% crossing (6/9 pre-YD)"));

    sortedSites.forEach((s, i) => {{
      const y = botTop + i * rowH + 9;
      const isAct = mode === "site" && s.id === activeId;
      if (isAct){{
        svg.appendChild(el("rect", {{x: 0, y: y - 9, width: W, height: rowH, fill: "var(--copper)", opacity: 0.1}}));
      }}
      const hit = el("rect", {{x: 0, y: y - 9, width: W, height: rowH, class: "sp-row-hit"}});
      hit.addEventListener("click", () => {{
        mode = "site";
        activeId = s.id;
        sel.value = String(s.id);
        btns.forEach(b => b.classList.toggle("is-on", b.dataset.mode === "site"));
        render();
      }});
      hit.addEventListener("mouseenter", () => {{
        const lead = s.t_50pct ? Math.round(s.t_50pct - 12896) : 0;
        const dir = lead >= 0 ? `+${{lead.toLocaleString()}} yr BEFORE YD` : `${{Math.abs(lead).toLocaleString()}} yr AFTER YD`;
        readout.textContent = `${{s.name}}, ${{s.state}} · Half-drop ${{s.t_50pct ? s.t_50pct.toLocaleString() + " BP (" + dir + ")" : "n/a"}} · Step ${{s.t_cp ? s.t_cp.toLocaleString() + " BP" : "n/a"}} · 2% ${{s.t_2pct ? s.t_2pct.toLocaleString() + " BP" : "never ≥2%"}}`;
      }});
      svg.appendChild(hit);

      svg.appendChild(el("text", {{x: L - 8, y: y + 4, "text-anchor": "end", fill: isAct ? "var(--copper)" : "var(--ink)", "font-size": 11, "font-weight": isAct ? 600 : 400, "pointer-events": "none"}}, `${{s.name}}, ${{s.state}}`));
      svg.appendChild(el("line", {{x1: L, x2: R, y1: y, y2: y, stroke: "var(--line)", "stroke-width": 0.7, "pointer-events": "none"}}));

      // Connector between t_50pct and t_cp if both exist
      if (s.t_50pct && s.t_cp){{
        svg.appendChild(el("line", {{x1: sx(s.t_50pct), x2: sx(s.t_cp), y1: y, y2: y, stroke: "var(--ink-soft)", "stroke-width": 1.6, opacity: 0.45, "pointer-events": "none"}}));
      }}
      if (s.t_2pct){{
        const x = sx(s.t_2pct);
        svg.appendChild(el("rect", {{x: x - 3.5, y: y - 3.5, width: 7, height: 7, fill: "var(--paper)", stroke: "var(--ochre)", "stroke-width": 1.6, "pointer-events": "none"}}));
      }}
      if (s.t_cp){{
        const x = sx(s.t_cp);
        svg.appendChild(el("polygon", {{points: `${{x}},${{y-4.5}} ${{x+4.5}},${{y}} ${{x}},${{y+4.5}} ${{x-4.5}},${{y}}`, fill: s.t_cp > 12896 ? "var(--copper)" : "var(--slate)", stroke: "var(--paper)", "stroke-width": 1, "pointer-events": "none"}}));
      }}
      if (s.t_50pct){{
        const x = sx(s.t_50pct);
        svg.appendChild(el("circle", {{cx: x, cy: y, r: 4, fill: s.t_50pct > 12896 ? "var(--verdigris)" : "var(--slate)", stroke: "var(--paper)", "stroke-width": 1.2, "pointer-events": "none"}}));
      }}
    }});

    svg.appendChild(el("text", {{x: (L + R) / 2, y: botTop + sortedSites.length * rowH + 22, "text-anchor": "middle", fill: "var(--faint)", "font-size": 11}}, "Calibrated years before present (cal BP; older ← → younger)"));
  }}

  btns.forEach(b => b.addEventListener("click", () => {{
    mode = b.dataset.mode;
    btns.forEach(x => x.classList.toggle("is-on", x === b));
    render();
  }}));
  sel.addEventListener("change", () => {{
    activeId = Number(sel.value);
    mode = "site";
    btns.forEach(x => x.classList.toggle("is-on", x.dataset.mode === "site"));
    render();
  }});
  render();
}})();
</script>
</figure>
"""


def build_radiocarbon_fig(summary: dict) -> str:
    p2 = summary["pillar2_radiocarbon"]
    # Package 4 primary subsets (clean 25-yr grids from 16,500 down to 10,500 cal BP)
    keep_subs = [
        ("score12_ams", "Score-12 AMS only"),
        ("all", "All vetted (Score 11–12)"),
        ("herbivores_s12", "Herbivores AMS"),
        ("no_labrea_s12", "Excl. Rancho La Brea AMS"),
    ]
    sub_data = {}
    for key, label in keep_subs:
        sub = p2["subsets"][key]
        t_all = sub["t_grid_25yr"]
        idxs = [i for i, t in enumerate(t_all) if 10500.0 <= t <= 16500.0]
        sub_data[key] = {
            "label": label,
            "n": sub["n_dates"],
            "n_surv_95": sub["n_surv_p95"],
            "n_surv_99": sub["n_surv_p99"],
            "t": [t_all[i] for i in idxs],
            "raw": {
                "obs": [round(sub["obs_spd_raw_25yr"][i] * 1000, 4) for i in idxs],
                "h_lo": [round(sub["h_impact_uniform"]["raw"]["spd_p025"][i] * 1000, 4) for i in idxs],
                "h_med": [round(sub["h_impact_uniform"]["raw"]["spd_p500"][i] * 1000, 4) for i in idxs],
                "h_hi": [round(sub["h_impact_uniform"]["raw"]["spd_p975"][i] * 1000, 4) for i in idxs],
                "r_pre": round(sub["obs_raw"]["r_pre"], 2),
                "m_yd": round(sub["obs_raw"]["m_yd"] * 100, 2),
                "h_m_yd_p99": round(sub["h_impact_uniform"]["raw"]["m_yd_p990"] * 100, 2),
                "p_myd": sub["p_myd_exceeds_unif"],
            },
            "taph": {
                "obs": [round(sub["obs_spd_taph_25yr"][i] * 1000, 4) for i in idxs],
                "h_lo": [round(sub["h_impact_taph_truth"]["taph_corrected"]["spd_p025"][i] * 1000, 4) for i in idxs],
                "h_med": [round(sub["h_impact_taph_truth"]["taph_corrected"]["spd_p500"][i] * 1000, 4) for i in idxs],
                "h_hi": [round(sub["h_impact_taph_truth"]["taph_corrected"]["spd_p975"][i] * 1000, 4) for i in idxs],
                "r_pre": round(sub["obs_taph"]["r_pre"], 2),
                "m_yd": round(sub["obs_taph"]["m_yd"] * 100, 2),
                "h_m_yd_p99": round(sub["h_impact_taph_truth"]["taph_corrected"]["m_yd_p990"] * 100, 2),
                "p_myd": sub["p_myd_exceeds_taph_truth"],
            },
        }

    survivors = [
        {
            "taxon": r["taxon"],
            "state": r["state"],
            "site": r["site"],
            "lab_id": r["lab_id"],
            "score": r["score"],
            "method": r["method"],
            "cal": round(r["cal_median"], 0),
            "lo": round(r["cal_ci95_lo"], 0),
            "hi": round(r["cal_ci95_hi"], 0),
            "p": round(r["p_lt_12750"] * 100, 1),
            "rc": f"{int(r['rcybp'])}±{int(r['error'])}",
        }
        for r in p2["survivors"]["specimens_p95"]
        if r["cal_median"] >= 10500.0
    ]

    payload = {"subsets": sub_data, "survivors": survivors}
    data_json = json.dumps(payload, separators=(",", ":"))

    return f"""<figure class="fig" id="fig-radiocarbon" aria-label="Interactive IntCal20 megafauna radiocarbon density versus instant-impact H_impact simulation">
<style>
#fig-radiocarbon .rc-bar{{display:flex;flex-wrap:wrap;align-items:center;gap:.4rem .55rem;margin:0 0 .85rem;font-family:var(--mono);font-size:11px;}}
#fig-radiocarbon .rc-label{{text-transform:uppercase;letter-spacing:.14em;color:var(--faint);}}
#fig-radiocarbon .rc-btn{{font:500 11px/1.2 var(--mono);padding:.34rem .58rem;border:1px solid var(--line);background:var(--panel);color:var(--ink);border-radius:2px;cursor:pointer;}}
#fig-radiocarbon .rc-btn.is-on{{background:var(--copper);border-color:var(--copper);color:#fff;}}
#fig-radiocarbon .rc-sep{{width:1px;height:1.1rem;background:var(--line);margin:0 .2rem;}}
#fig-radiocarbon .rc-meta{{margin:0 0 .6rem;font-size:.86rem;color:var(--ink-soft);}}
#fig-radiocarbon .rc-readout{{font-family:var(--mono);font-size:11.5px;color:var(--ink);padding:.45rem .7rem;background:var(--panel);border:1px solid var(--line);margin-top:.5rem;min-height:2.1em;}}
#fig-radiocarbon svg{{display:block;width:100%;min-width:620px;height:auto;font-family:var(--sans);}}
</style>
<div class="rc-bar">
  <span class="rc-label">Subset</span>
  <button type="button" class="rc-btn is-on" data-sub="score12_ams">Score-12 AMS (214)</button>
  <button type="button" class="rc-btn" data-sub="all">All vetted (326)</button>
  <button type="button" class="rc-btn" data-sub="herbivores_s12">Herbivores AMS (192)</button>
  <button type="button" class="rc-btn" data-sub="no_labrea_s12">No La Brea AMS (197)</button>
  <span class="rc-sep" aria-hidden="true"></span>
  <button type="button" class="rc-btn is-on" data-corr="raw">Raw SPD</button>
  <button type="button" class="rc-btn" data-corr="taph">Surovell taphonomy-corrected</button>
</div>
<p class="rc-meta" id="rc-meta"></p>
<div class="fig-scroll">
  <svg id="rc-svg" viewBox="0 0 740 340" role="img" aria-label="Observed IntCal20 megafauna summed probability density compared with 2,000 instant-impact Monte Carlo simulations"></svg>
</div>
<div class="rc-readout" id="rc-readout">Hover along the timeline or over the post-impact survivor diamonds at the bottom to inspect individual AMS collagen dates.</div>
<figcaption>Direct megafauna bone and tooth radiocarbon dates (Broughton &amp; Weitzel 2018, recalibrated on IntCal20) compared against 2,000 forward-simulated catalogues (<em>H</em><sub>impact</sub>, slate 95% band) in which populations stayed constant and vanished instantly at 12,850 cal BP. Observed fossil density rises sharply in 13,500–12,900 BP and drops ~10-fold around 12,800–12,600 BP — yet inside the post-impact Younger Dryas window (12,700–11,700 BP, shaded), real fossil probability sits 4× to 7× above the 99th percentile of radiocarbon-plateau leakage (p &lt; 0.0005 across every subset). Bottom diamonds mark individual specimens with &gt;95% posterior probability of living after 12,750 BP.</figcaption>
<script>
(function(){{
  const D = {data_json};
  const root = document.getElementById("fig-radiocarbon");
  const svg = document.getElementById("rc-svg");
  const meta = document.getElementById("rc-meta");
  const readout = document.getElementById("rc-readout");
  const NS = "http://www.w3.org/2000/svg";

  let activeSub = "score12_ams";
  let activeCorr = "raw";

  const W = 740, L = 58, R = 716, topY = 28, H = 220, rugY = 282;
  const T_MAX = 16500, T_MIN = 10500;
  const sx = t => L + (T_MAX - t) / (T_MAX - T_MIN) * (R - L);

  function el(tag, attrs, text){{
    const n = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs || {{}})) n.setAttribute(k, String(v));
    if (text !== undefined) n.textContent = text;
    return n;
  }}

  function render(){{
    svg.innerHTML = "";
    const sub = D.subsets[activeSub];
    const c = sub[activeCorr];
    const yMax = Math.max(...c.obs, ...c.h_hi) * 1.12;
    const sy = v => topY + H - (v / yMax) * H;

    // Shaded post-impact Younger Dryas window (12,700 to 11,700 BP)
    const xW0 = sx(12700), xW1 = sx(11700);
    svg.appendChild(el("rect", {{x: xW0, y: topY, width: xW1 - xW0, height: H, fill: "var(--verdigris)", opacity: 0.12}}));
    svg.appendChild(el("text", {{x: (xW0 + xW1) / 2, y: topY + 14, "text-anchor": "middle", fill: "var(--verdigris)", "font-size": 10.5, "font-weight": 600}}, "Post-impact window"));
    svg.appendChild(el("text", {{x: (xW0 + xW1) / 2, y: topY + 28, "text-anchor": "middle", fill: "var(--verdigris)", "font-size": 10}}, "12,700–11,700 BP"));

    // Gridlines
    for (let t = 16000; t >= 11000; t -= 1000){{
      const x = sx(t);
      svg.appendChild(el("line", {{x1: x, x2: x, y1: topY, y2: topY + H, stroke: "var(--line)", "stroke-width": 1}}));
      svg.appendChild(el("text", {{x, y: topY + H + 16, "text-anchor": "middle", fill: "var(--faint)", "font-size": 11}}, (t / 1000).toFixed(0) + "k"));
    }}
    svg.appendChild(el("line", {{x1: L, x2: R, y1: topY + H, y2: topY + H, stroke: "var(--faint)", "stroke-width": 1}}));

    // Y ticks
    const yStep = yMax > 3 ? 1.0 : 0.5;
    for (let v = 0; v <= yMax; v += yStep){{
      const y = sy(v);
      svg.appendChild(el("line", {{x1: L, x2: R, y1: y, y2: y, stroke: "var(--line)", "stroke-width": 0.7, opacity: 0.6}}));
      svg.appendChild(el("text", {{x: L - 7, y: y + 4, "text-anchor": "end", fill: "var(--faint)", "font-size": 10.5}}, v.toFixed(1)));
    }}
    svg.appendChild(el("text", {{x: 12, y: topY + H / 2, transform: `rotate(-90 12 ${{topY + H / 2}})`, "text-anchor": "middle", fill: "var(--faint)", "font-size": 10.5}}, "Density (×10⁻³ / 5 yr)"));

    // H_impact 95% envelope
    const up = sub.t.map((t, i) => `${{sx(t).toFixed(1)}},${{sy(c.h_hi[i]).toFixed(1)}}`).join(" L");
    const dn = [...sub.t].reverse().map((t, j) => {{
      const i = sub.t.length - 1 - j;
      return `${{sx(t).toFixed(1)}},${{sy(c.h_lo[i]).toFixed(1)}}`;
    }}).join(" L");
    svg.appendChild(el("path", {{d: `M${{up}} L${{dn}} Z`, fill: "var(--slate)", opacity: 0.24}}));
    const hMedPath = sub.t.map((t, i) => `${{sx(t).toFixed(1)}},${{sy(c.h_med[i]).toFixed(1)}}`).join(" L");
    svg.appendChild(el("path", {{d: `M${{hMedPath}}`, fill: "none", stroke: "var(--slate)", "stroke-width": 1.6, "stroke-dasharray": "4 3"}}));

    // Observed SPD
    const obsPts = sub.t.map((t, i) => `${{sx(t).toFixed(1)}},${{sy(c.obs[i]).toFixed(1)}}`).join(" L");
    const obsArea = `M${{sx(sub.t[0]).toFixed(1)}},${{(topY + H).toFixed(1)}} L${{obsPts}} L${{sx(sub.t[sub.t.length-1]).toFixed(1)}},${{(topY + H).toFixed(1)}} Z`;
    svg.appendChild(el("path", {{d: obsArea, fill: "var(--copper)", opacity: 0.14}}));
    svg.appendChild(el("path", {{d: `M${{obsPts}}`, fill: "none", stroke: "var(--copper)", "stroke-width": 2.4}}));

    // Impact / YD onset line (12,850 BP)
    const xImp = sx(12850);
    svg.appendChild(el("line", {{x1: xImp, x2: xImp, y1: topY - 6, y2: rugY + 14, stroke: "var(--copper)", "stroke-width": 1.5, "stroke-dasharray": "4 3"}}));
    svg.appendChild(el("text", {{x: xImp - 6, y: topY - 10, "text-anchor": "end", fill: "var(--copper)", "font-size": 11, "font-weight": 600}}, "Claimed wipeout (12,850 BP)"));

    // Interactive hover overlay on curve
    const hoverLine = el("line", {{x1: L, x2: L, y1: topY, y2: topY + H, stroke: "var(--ink)", "stroke-width": 1, opacity: 0}});
    svg.appendChild(hoverLine);
    const hitOverlay = el("rect", {{x: L, y: topY, width: R - L, height: H, fill: "transparent", style: "cursor:crosshair"}});
    hitOverlay.addEventListener("mousemove", ev => {{
      const rect = svg.getBoundingClientRect();
      const px = (ev.clientX - rect.left) * (W / rect.width);
      const tEst = T_MAX - ((px - L) / (R - L)) * (T_MAX - T_MIN);
      let best = 0, bestD = 1e9;
      for (let i = 0; i < sub.t.length; i++){{
        const d = Math.abs(sub.t[i] - tEst);
        if (d < bestD){{ bestD = d; best = i; }}
      }}
      const x = sx(sub.t[best]);
      hoverLine.setAttribute("x1", x);
      hoverLine.setAttribute("x2", x);
      hoverLine.setAttribute("opacity", "0.5");
      readout.textContent = `${{sub.t[best].toLocaleString()}} cal BP · Observed SPD = ${{c.obs[best].toFixed(3)}} · H_impact 12,850 median = ${{c.h_med[best].toFixed(3)}} (95% band ${{c.h_lo[best].toFixed(3)}}–${{c.h_hi[best].toFixed(3)}})`;
    }});
    hitOverlay.addEventListener("mouseleave", () => hoverLine.setAttribute("opacity", "0"));
    svg.appendChild(hitOverlay);

    // Survivor diamond rug at bottom
    const showAll = activeSub === "all";
    const survList = D.survivors.filter(s => showAll ? true : s.score >= 12);
    svg.appendChild(el("text", {{x: L, y: rugY - 10, fill: "var(--faint)", "font-size": 10.5, "font-family": "var(--mono)"}}, `POST-IMPACT SURVIVORS IN WINDOW (${{survList.length}} specimens with P(age < 12,750 BP) > 95%)`));
    svg.appendChild(el("line", {{x1: L, x2: R, y1: rugY + 6, y2: rugY + 6, stroke: "var(--line)", "stroke-width": 1}}));

    survList.forEach((s, idx) => {{
      const x = sx(s.cal);
      const y = rugY + 6 + (idx % 2 === 0 ? -4 : 6);
      const col = s.score >= 12 ? "var(--verdigris)" : "var(--ochre)";
      svg.appendChild(el("line", {{x1: sx(s.hi), x2: sx(s.lo), y1: y, y2: y, stroke: col, "stroke-width": 1.4, opacity: 0.45}}));
      const dmd = el("polygon", {{points: `${{x}},${{y-4.5}} ${{x+4.5}},${{y}} ${{x}},${{y+4.5}} ${{x-4.5}},${{y}}`, fill: col, stroke: "var(--paper)", "stroke-width": 1, style: "cursor:pointer"}});
      dmd.addEventListener("mouseenter", () => {{
        readout.textContent = `${{s.taxon}} · ${{s.site}}, ${{s.state}} (${{s.lab_id}}, Score-${{s.score}} ${{s.method}}, ${{s.rc}} ¹⁴C BP) → ${{s.cal.toLocaleString()}} cal BP (95% CI ${{s.lo.toLocaleString()}}–${{s.hi.toLocaleString()}}, P<12,750 = ${{s.p}}%)`;
      }});
      svg.appendChild(dmd);
    }});

    svg.appendChild(el("text", {{x: (L + R) / 2, y: 326, "text-anchor": "middle", fill: "var(--faint)", "font-size": 11}}, "Calibrated years before present (IntCal20; older ← → younger)"));

    const ratio = (c.m_yd / Math.max(c.h_m_yd_p99, 0.01)).toFixed(1);
    meta.innerHTML = `<strong>${{sub.label}} (n = ${{sub.n}}):</strong> Younger Dryas mass (12,700–11,700 BP) = <strong>${{c.m_yd.toFixed(2)}}%</strong> vs. <em>H</em><sub>impact</sub> 99th-percentile leakage <strong>${{c.h_m_yd_p99.toFixed(2)}}%</strong> (<strong>${{ratio}}× higher</strong>, p &lt; 0.0005) · High-confidence survivors (&gt;99% after 12,750 BP): <strong>${{sub.n_surv_99}}</strong>.`;
  }}

  root.querySelectorAll("[data-sub]").forEach(b => b.addEventListener("click", () => {{
    activeSub = b.dataset.sub;
    root.querySelectorAll("[data-sub]").forEach(x => x.classList.toggle("is-on", x === b));
    render();
  }}));
  root.querySelectorAll("[data-corr]").forEach(b => b.addEventListener("click", () => {{
    activeCorr = b.dataset.corr;
    root.querySelectorAll("[data-corr]").forEach(x => x.classList.toggle("is-on", x === b));
    render();
  }}));
  render();
}})();
</script>
</figure>
"""


def build_taxa_fig(summary: dict) -> str:
    p2 = summary["pillar2_radiocarbon"]
    # Build rich dataset for both Score-12 AMS (default, cleanest!) and All (Score 11+12)
    taxa_list = []
    for tx in p2["taxa"]:
        taxa_list.append({
            "taxon": tx["taxon"],
            "label": COMMON_NAMES.get(tx["taxon"], tx["taxon"]),
            "n_all": tx["n_all_25_9"],
            "n_s12": tx["n_s12_25_9"],
            "surv_all": tx["n_surv_p95_all"],
            "surv_s12": tx["n_surv_p95_s12"],
            "all": tx["all"],
            "s12": tx["score12_ams"],
            "medians": [round(m, 0) for m in tx["specimen_medians_bp"] if 9000 <= m <= 16500],
        })

    # Add concise context rows for smaller-n iconic genera (youngest AMS LAD from calibrated list)
    # Computed directly from megafauna_calibrated.tsv so every number is exact
    import csv
    cal_rows = list(csv.DictReader((RESULTS / "megafauna_calibrated.tsv").open(encoding="utf-8"), delimiter="\t"))
    extra_genera = ["Canis dirus", "Panthera leo atrox", "Camelops", "Castoroides", "Arctodus"]
    context_rows = []
    for g in extra_genera:
        sub_s12 = [r for r in cal_rows if r["taxon"] == g and int(r["score"]) >= 12 and float(r["cal_median"]) <= 25000]
        if not sub_s12:
            continue
        youngest = min(sub_s12, key=lambda r: float(r["cal_median"]))
        context_rows.append({
            "taxon": g,
            "label": COMMON_NAMES.get(g, g),
            "n_s12": len(sub_s12),
            "lad": round(float(youngest["cal_median"]), 0),
            "lo": round(float(youngest["cal_ci95_lo"]), 0),
            "hi": round(float(youngest["cal_ci95_hi"]), 0),
            "site": f"{youngest['site']}, {youngest['state']}",
        })
    context_rows.sort(key=lambda r: -r["lad"])

    payload = {"taxa": taxa_list, "context": context_rows}
    data_json = json.dumps(payload, separators=(",", ":"))

    return f"""<figure class="fig" id="fig-taxa" aria-label="Per-taxon Signor-Lipps extinction estimates across North American megafauna">
<style>
#fig-taxa .tx-bar{{display:flex;flex-wrap:wrap;align-items:center;gap:.45rem .6rem;margin:0 0 .85rem;font-family:var(--mono);font-size:11px;}}
#fig-taxa .tx-label{{text-transform:uppercase;letter-spacing:.14em;color:var(--faint);}}
#fig-taxa .tx-btn{{font:500 11px/1.2 var(--mono);padding:.34rem .58rem;border:1px solid var(--line);background:var(--panel);color:var(--ink);border-radius:2px;cursor:pointer;}}
#fig-taxa .tx-btn.is-on{{background:var(--copper);border-color:var(--copper);color:#fff;}}
#fig-taxa .tx-meta{{margin:0 0 .6rem;font-size:.86rem;color:var(--ink-soft);}}
#fig-taxa .tx-readout{{font-family:var(--mono);font-size:11.5px;color:var(--ink);padding:.45rem .7rem;background:var(--panel);border:1px solid var(--line);margin-top:.5rem;min-height:2.1em;}}
#fig-taxa svg{{display:block;width:100%;min-width:620px;height:auto;font-family:var(--sans);}}
</style>
<div class="tx-bar">
  <span class="tx-label">Dating tier</span>
  <button type="button" class="tx-btn is-on" data-tier="s12">Gold-standard Score-12 AMS (cleanest)</button>
  <button type="button" class="tx-btn" data-tier="all">All vetted Score 11–12 (includes older conventional dates)</button>
</div>
<p class="tx-meta" id="tx-meta"></p>
<div class="fig-scroll">
  <svg id="tx-svg" viewBox="0 0 740 430" role="img" aria-label="Extinction timeline by megafauna genus showing youngest dated fossil, OLE, and GRIWM 95% intervals"></svg>
</div>
<div class="tx-readout" id="tx-readout">Hover any genus row to compare its youngest dated fossil (LAD) with its Signor–Lipps OLE and GRIWM extinction intervals.</div>
<figcaption>Per-genus extinction estimates on IntCal20 (1,000 calibrated posterior draws per taxon). Top block shows every genus with enough dates for formal Signor–Lipps estimation: individual dated fossils (faint vertical ticks), youngest fossil (hollow circle), Solow Optimal Linear Estimation (<em>OLE</em>, solid copper diamond + 95% interval), and Bradshaw <em>GRIWM</em> (verdigris square). Lower block adds the youngest Score-12 AMS fossils from five iconic lower-count genera (dire wolf, American lion, camel, giant beaver, short-faced bear) for context. Switching from All vetted dates to Score-12 AMS removes questionable 1960s–70s conventional outliers — and still leaves &gt;1,200 years of staggered extinction spanning both sides of the Younger Dryas onset.</figcaption>
<script>
(function(){{
  const D = {data_json};
  const root = document.getElementById("fig-taxa");
  const svg = document.getElementById("tx-svg");
  const meta = document.getElementById("tx-meta");
  const readout = document.getElementById("tx-readout");
  const NS = "http://www.w3.org/2000/svg";

  let tier = "s12";
  const W = 740, L = 196, R = 716;
  const T_MAX = 15800, T_MIN = 7500;
  const sx = t => L + (T_MAX - Math.max(T_MIN, Math.min(T_MAX, t))) / (T_MAX - T_MIN) * (R - L);

  function el(tag, attrs, text){{
    const n = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs || {{}})) n.setAttribute(k, String(v));
    if (text !== undefined) n.textContent = text;
    return n;
  }}

  function render(){{
    svg.innerHTML = "";
    const rows = D.taxa.filter(tx => tier === "all" ? true : tx.s12 !== null);
    rows.sort((a, b) => {{
      const ea = (tier === "all" ? a.all : a.s12).ole.median;
      const eb = (tier === "all" ? b.all : b.s12).ole.median;
      return eb - ea;
    }});

    const topY = 32, rowH = 36;
    const ctxTop = topY + rows.length * rowH + 34;
    const ctxH = 26;
    const totalH = ctxTop + D.context.length * ctxH + 38;
    svg.setAttribute("viewBox", `0 0 ${{W}} ${{totalH}}`);

    // YD shading
    const xYD0 = sx(12896), xYD1 = sx(11700);
    svg.appendChild(el("rect", {{x: xYD0, y: topY - 8, width: xYD1 - xYD0, height: totalH - topY - 26, fill: "var(--slate)", opacity: 0.10}}));

    // Gridlines
    for (let t = 15000; t >= 8000; t -= 1000){{
      const x = sx(t);
      svg.appendChild(el("line", {{x1: x, x2: x, y1: topY - 8, y2: totalH - 34, stroke: "var(--line)", "stroke-width": 1}}));
      svg.appendChild(el("text", {{x, y: totalH - 18, "text-anchor": "middle", fill: "var(--faint)", "font-size": 11}}, (t / 1000).toFixed(0) + "k"));
    }}

    // Reference lines
    svg.appendChild(el("line", {{x1: xYD0, x2: xYD0, y1: topY - 12, y2: totalH - 32, stroke: "var(--copper)", "stroke-width": 1.6, "stroke-dasharray": "4 3"}}));
    svg.appendChild(el("text", {{x: xYD0 - 5, y: topY - 16, "text-anchor": "end", fill: "var(--copper)", "font-size": 11, "font-weight": 600}}, "YD cold starts (12,896 BP)"));
    svg.appendChild(el("text", {{x: (xYD0 + xYD1) / 2, y: topY - 16, "text-anchor": "middle", fill: "var(--faint)", "font-size": 10}}, "Younger Dryas"));

    // Legend top-left
    svg.appendChild(el("text", {{x: 6, y: topY - 16, fill: "var(--faint)", "font-size": 10.5, "font-family": "var(--mono)"}}, "FORMAL OLE / GRIWM GENERA"));

    rows.forEach((tx, i) => {{
      const est = tier === "all" ? tx.all : tx.s12;
      const y = topY + i * rowH + 18;

      const hit = el("rect", {{x: 0, y: y - 16, width: W, height: rowH - 2, fill: "transparent", style: "cursor:pointer"}});
      hit.addEventListener("mouseenter", () => {{
        hit.setAttribute("fill", "color-mix(in oklab, var(--copper) 7%, transparent)");
        readout.textContent = `${{tx.label}} (n=${{est.n_dates}}) · Youngest fossil ${{est.lad.median.toLocaleString()}} BP · OLE ${{est.ole.median.toLocaleString()}} BP (95% CI ${{est.ole.ci95_lo.toLocaleString()}}–${{est.ole.ci95_hi.toLocaleString()}}) · GRIWM ${{est.griwm.median.toLocaleString()}} BP`;
      }});
      hit.addEventListener("mouseleave", () => hit.setAttribute("fill", "transparent"));
      svg.appendChild(hit);

      svg.appendChild(el("line", {{x1: L, x2: R, y1: y, y2: y, stroke: "var(--line)", "stroke-width": 0.8, "pointer-events": "none"}}));
      svg.appendChild(el("text", {{x: L - 10, y: y + 2, "text-anchor": "end", fill: "var(--ink)", "font-size": 11.5, "font-weight": 500, "pointer-events": "none"}}, tx.label));
      svg.appendChild(el("text", {{x: L - 10, y: y + 14, "text-anchor": "end", fill: "var(--faint)", "font-size": 10, "pointer-events": "none"}}, `n = ${{est.n_dates}} · OLE ${{Math.round(est.ole.median).toLocaleString()}} BP`));

      // Faint specimen ticks
      tx.medians.forEach(m => {{
        if (m <= T_MAX && m >= T_MIN){{
          const xm = sx(m);
          svg.appendChild(el("line", {{x1: xm, x2: xm, y1: y - 7, y2: y + 7, stroke: "var(--faint)", "stroke-width": 1, opacity: 0.35, "pointer-events": "none"}}));
        }}
      }});

      // OLE 95% CI whisker
      const xLo = sx(est.ole.ci95_hi), xHi = sx(est.ole.ci95_lo);
      svg.appendChild(el("line", {{x1: xLo, x2: xHi, y1: y, y2: y, stroke: "var(--copper)", "stroke-width": 2.6, opacity: 0.55, "pointer-events": "none"}}));

      // Youngest fossil LAD (hollow circle)
      const xLad = sx(est.lad.median);
      svg.appendChild(el("circle", {{cx: xLad, cy: y, r: 4.5, fill: "var(--paper)", stroke: "var(--ink)", "stroke-width": 1.6, "pointer-events": "none"}}));

      // GRIWM square
      const xGr = sx(est.griwm.median);
      svg.appendChild(el("rect", {{x: xGr - 3.8, y: y - 3.8, width: 7.6, height: 7.6, fill: "var(--verdigris)", stroke: "var(--paper)", "stroke-width": 1.2, "pointer-events": "none"}}));

      // OLE diamond
      const xOle = sx(est.ole.median);
      svg.appendChild(el("polygon", {{points: `${{xOle}},${{y-5.5}} ${{xOle+5.5}},${{y}} ${{xOle}},${{y+5.5}} ${{xOle-5.5}},${{y}}`, fill: "var(--copper)", stroke: "var(--paper)", "stroke-width": 1.2, "pointer-events": "none"}}));
    }});

    // Context section: youngest Score-12 AMS fossils for smaller-n iconic genera
    svg.appendChild(el("text", {{x: 6, y: ctxTop - 10, fill: "var(--faint)", "font-size": 10.5, "font-family": "var(--mono)"}}, "LOWER-COUNT GENERA (YOUNGEST SCORE-12 AMS FOSSIL ± 95% CI)"));
    D.context.forEach((c, j) => {{
      const y = ctxTop + j * ctxH + 12;
      const hit = el("rect", {{x: 0, y: y - 11, width: W, height: ctxH - 2, fill: "transparent", style: "cursor:pointer"}});
      hit.addEventListener("mouseenter", () => {{
        hit.setAttribute("fill", "color-mix(in oklab, var(--slate) 8%, transparent)");
        readout.textContent = `${{c.label}} (n=${{c.n_s12}} AMS dates) · Youngest AMS fossil: ${{c.lad.toLocaleString()}} cal BP (95% CI ${{c.lo.toLocaleString()}}–${{c.hi.toLocaleString()}}) at ${{c.site}}`;
      }});
      hit.addEventListener("mouseleave", () => hit.setAttribute("fill", "transparent"));
      svg.appendChild(hit);

      svg.appendChild(el("line", {{x1: L, x2: R, y1: y, y2: y, stroke: "var(--line)", "stroke-width": 0.6, "stroke-dasharray": "2 3", "pointer-events": "none"}}));
      svg.appendChild(el("text", {{x: L - 10, y: y + 4, "text-anchor": "end", fill: "var(--ink-soft)", "font-size": 11, "pointer-events": "none"}}, `${{c.label}} (n=${{c.n_s12}})`));
      svg.appendChild(el("line", {{x1: sx(c.hi), x2: sx(c.lo), y1: y, y2: y, stroke: "var(--slate)", "stroke-width": 2, opacity: 0.65, "pointer-events": "none"}}));
      svg.appendChild(el("circle", {{cx: sx(c.lad), cy: y, r: 4, fill: c.lad < 12750 ? "var(--verdigris)" : "var(--slate)", stroke: "var(--paper)", "stroke-width": 1.2, "pointer-events": "none"}}));
    }});

    svg.appendChild(el("text", {{x: (L + R) / 2, y: totalH - 4, "text-anchor": "middle", fill: "var(--faint)", "font-size": 11}}, "Calibrated years before present (IntCal20; older ← → younger)   ○ Youngest fossil (LAD)   ◆ OLE (95% CI)   ■ GRIWM"));

    if (tier === "s12"){{
      meta.innerHTML = "<strong>Gold-standard Score-12 AMS dates:</strong> horses disappear around 13,061 BP (and dire wolves by 13,674 BP), whereas mammoths (11,852 BP), mastodons (11,867 BP), and mountain goats (10,333 BP) all have 95% extinction bounds strictly inside or after the Younger Dryas.";
    }} else {{
      meta.innerHTML = "<strong>All vetted Score 11–12 dates:</strong> includes older 1960s–70s conventional dates (some later questioned for collagen pretreatment), stretching the nominal OLE span to 4,138 years (12,495 to 8,357 BP). Switch back to Score-12 AMS for the strictest modern subset.";
    }}
  }}

  root.querySelectorAll("[data-tier]").forEach(b => b.addEventListener("click", () => {{
    tier = b.dataset.tier;
    root.querySelectorAll("[data-tier]").forEach(x => x.classList.toggle("is-on", x === b));
    render();
  }}));
  render();
}})();
</script>
</figure>
"""


def main() -> None:
    summary = json.loads((RESULTS / "summary.json").read_text(encoding="utf-8"))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "tiles.html").write_text(build_tiles(summary), encoding="utf-8")
    (OUT_DIR / "verdict.html").write_text(build_verdict(summary), encoding="utf-8")
    (OUT_DIR / "sporormiella.html").write_text(build_sporormiella_fig(summary), encoding="utf-8")
    (OUT_DIR / "radiocarbon.html").write_text(build_radiocarbon_fig(summary), encoding="utf-8")
    (OUT_DIR / "taxa.html").write_text(build_taxa_fig(summary), encoding="utf-8")
    print(f"Wrote 5 interactive figures to {OUT_DIR}")


if __name__ == "__main__":
    main()
