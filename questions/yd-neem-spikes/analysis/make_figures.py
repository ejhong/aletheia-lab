#!/usr/bin/env python3
"""Generate 4 self-contained, zero-dependency interactive HTML figures for
site/figures/yd-neem-spikes/ from locked results/summary.json.
"""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT.parent.parent
RESULTS = ROOT / "results"
OUT_DIR = REPO / "site" / "figures" / "yd-neem-spikes"

esc = lambda s: html.escape(str(s), quote=True)


def build_tiles(s: dict) -> str:
    p1 = s["pillar1_neem_104_150ka"]
    a, b = p1["window_after"], p1["window_before"]
    items = [
        (
            f"{p1['level_after_over_before']:.2f}×",
            f"jump in NEEM's steady yearly median ammonium after Younger Dryas onset ({a['level']:.1f} vs. {b['level']:.1f} µg/kg — rank 1 of {p1['n_windows']} stretches, carrying {p1['share_of_rise_from_level']*100:.0f}% of the rise)",
            False,
        ),
        (
            f"{a['spike_years_x5']} vs. {b['spike_years_x5']}",
            f"years with sharp >5× fire spikes in the 150 years after onset versus before (typical {p1['medians']['spike_years_x5']:.0f}; p = {p1['rate_tests']['x5_after_vs_before']['p_two_sided']:.4f}; zero >10× spikes vs. {b['spike_years_x10']} before)",
            False,
        ),
        (
            f"{a['spike_years_add50']} vs. {b['spike_years_add50']}",
            f"years with absolute >50 µg/kg plumes above baseline (rank {p1['ranks']['spike_years_add50']['after_rank_desc']} of {p1['n_windows']}, p = {p1['rate_tests']['add50_after_vs_before']['p_two_sided']:.2f}; flux-scaled {a['spike_years_flux50']} vs. {b['spike_years_flux50']}, p = {p1['rate_tests']['flux50_after_vs_before']['p_two_sided']:.2f})",
            False,
        ),
        (
            "Replicated in NEEM",
            "Steady baseline surge with fewer relative spikes and ordinary absolute plumes—contradicting a century of repeated airburst fires",
            True,
        ),
    ]
    return '<div class="tiles">\n' + "\n".join(
        f'<div class="tile"><p class="tile-value{" is-word" if w else ""}">{esc(v)}</p>'
        f'<p class="tile-label">{esc(l)}</p></div>'
        for v, l, w in items
    ) + "\n</div>\n"


def build_verdict(s: dict) -> str:
    p1 = s["pillar1_neem_104_150ka"]
    a, b = p1["window_after"], p1["window_before"]
    p2 = s["pillar2_stadial_onsets"]
    rows = [
        (
            "Steady level vs. spike excess",
            "Did the Younger Dryas ammonium rise in NEEM come from a raised steady level or from short smoke spikes?",
            f"Entirely from the steady level. Yearly median ammonium jumped {p1['level_after_over_before']:.2f}× ({b['level']:.2f} → {a['level']:.2f} µg/kg, rank 1 of {p1['n_windows']}), "
            f"while the excess spike component (mean minus median) actually fell from {b['spike_part']:.2f} to {a['spike_part']:.2f} µg/kg — putting {p1['share_of_rise_from_level']*100:.0f}% of the total rise in the steady background.",
            "is-yes",
            "102% from steady level",
        ),
        (
            "Exact NGRIP replication (>5× spikes)",
            "Does NEEM confirm NGRIP's exploratory finding of fewer sharp (>5×) fire-spike years after onset?",
            f"Yes, strongly. Years with a peak exceeding 5× the 51-year running median dropped nearly fourfold from {b['spike_years_x5']} in the 150 years before onset (median {p1['medians']['spike_years_x5']:.1f}) "
            f"to {a['spike_years_x5']} after onset (exact two-sided binomial p = {p1['rate_tests']['x5_after_vs_before']['p_two_sided']:.4f}). Extreme >10× spikes fell from {b['spike_years_x10']} to {a['spike_years_x10']}.",
            "is-yes",
            "Confirmed (8 vs. 31, p = 0.0003)",
        ),
        (
            "Anti-denominator control (additive >50 µg/kg)",
            "Could the higher baseline have masked a real surge in absolute wildfire plumes?",
            f"No. Counting years where the peak rises >50 µg/kg above the running baseline gives {a['spike_years_add50']} years after onset vs. {b['spike_years_add50']} before "
            f"(median {p1['medians']['spike_years_add50']:.1f}, ordinary rank {p1['ranks']['spike_years_add50']['after_rank_desc']} of {p1['n_windows']}, p = {p1['rate_tests']['add50_after_vs_before']['p_two_sided']:.2f}). "
            f"The single largest plume after onset ({a['largest_excess']:.0f} µg/kg) was half as big as before ({b['largest_excess']:.0f} µg/kg), and far below warm early-Holocene boreal fire centuries (28–36 plumes/150 yr).",
            "is-yes",
            "No plume surge (rank 11/28)",
        ),
        (
            "Snowfall-flux control (>50 µg/kg-eq)",
            "Does correcting for the ~2× drop in Younger Dryas snowfall change the plume count?",
            f"No. Scaling each year's plume excess by NEEM's local 5-cm GICC05 annual layer thickness yields {a['spike_years_flux50']} flux-plume years after onset vs. {b['spike_years_flux50']} before "
            f"(median {p1['medians']['spike_years_flux50']:.1f}, p = {p1['rate_tests']['flux50_after_vs_before']['p_two_sided']:.2f})—less than half the early-Holocene rate (34–58/150 yr).",
            "is-yes",
            "Ordinary flux plumes (p = 0.58)",
        ),
        (
            "Earlier glacial stadials (Pillar 2)",
            "How does the Younger Dryas compare with earlier resolved abrupt coolings in NEEM?",
            f"Only {p2['n_events']} stadial onsets in NEEM retain ≥10 samples/yr (GS-1, GS-2.1c at 22.9 ka, GS-4 at 28.6 ka); deeper ice thins below 10 mm/yr. "
            f"All three show steady-level jumps (2.50×, 1.48×, 3.46×) with zero spike surges.",
            "is-open",
            "3 resolved stadials; all steady",
        ),
    ]
    out = [
        '<div class="verdict" role="table" aria-label="Pre-registered NEEM fire-spike replication checks">',
        '<div class="verdict-head" role="row"><span>Check</span><span>Question</span><span>Result</span><span>Call</span></div>',
    ]
    for chk, q, r, cls, badge in rows:
        out.append(
            f'<div class="verdict-row" role="row">'
            f'<p class="verdict-name" role="cell">{esc(chk)}</p>'
            f'<p class="verdict-q" role="cell">{esc(q)}</p>'
            f'<p class="verdict-r" role="cell">{esc(r)}</p>'
            f'<p class="verdict-call" role="cell"><span class="chip {cls}">{esc(badge)}</span></p>'
            f'</div>'
        )
    out.append("</div>")
    return "\n".join(out) + "\n"


def build_decomposition(s: dict) -> str:
    wins = s["pillar1_neem_104_150ka"]["windows"]
    payload = json.dumps(wins)
    return f'''<figure class="fig" aria-label="Interactive 150-year window comparison of NEEM steady ammonium level and fire-spike counts from 14,700 to 10,500 years ago">
<style>
.ns-bar{{display:flex;flex-wrap:wrap;gap:.45rem;margin-bottom:.65rem}}
.ns-btn{{font:500 13px/1.2 var(--sans);padding:.38rem .75rem;border-radius:4px;border:1px solid var(--line);background:var(--panel);color:var(--ink);cursor:pointer}}
.ns-btn.is-on{{background:var(--ink);color:var(--paper);border-color:var(--ink)}}
.ns-tip{{position:fixed;pointer-events:none;z-index:50;background:var(--band);color:var(--band-ink);border:1px solid var(--band-line);border-radius:5px;padding:.4rem .65rem;font:400 12.5px/1.4 var(--sans);display:none}}
</style>
<div class="ns-bar" role="tablist" aria-label="NEEM metric selector">
  <button type="button" class="ns-btn is-on" data-m="level">1 · Steady level (µg/kg)</button>
  <button type="button" class="ns-btn" data-m="spike_years_x5">2 · Relative >5× spike years</button>
  <button type="button" class="ns-btn" data-m="spike_years_add50">3 · Additive >50 µg/kg plumes</button>
  <button type="button" class="ns-btn" data-m="spike_part">4 · Spike excess (mean − median)</button>
</div>
<div class="fig-scroll"><svg id="ns-svg" class="chart" viewBox="0 0 740 310" width="100%" role="img" aria-label="NEEM 150-year window bar chart"></svg></div>
<div class="ns-tip" id="ns-tip"></div>
<figcaption>All 28 non-overlapping 150-year stretches in NEEM from 14,696 to 10,496 years before 2000 CE (older left → younger right). The highlighted copper bar is <strong>Window 0 (12,896–12,746 b2k)</strong>, the 150 years immediately after Younger Dryas onset; the slate bar beside it is <strong>Window −1</strong>, the 150 years just before. Switch metrics above: the steady background level jumps to #1 of 28, yet relative &gt;5× spikes drop nearly fourfold (8 vs. 31), additive &gt;50 µg/kg plumes remain completely ordinary (18 vs. 14, rank 11/28), and the spike-excess component actually shrinks—in sharp contrast to the warm early Holocene (right), where real North American boreal wildfires drive both &gt;5× and &gt;50 µg/kg spikes sharply upward.</figcaption>
<script>
(function(){{
  const WINS = {payload};
  const svg = document.getElementById("ns-svg");
  const tip = document.getElementById("ns-tip");
  const NS = "http://www.w3.org/2000/svg";
  const el = (t,a,tx) => {{ const n=document.createElementNS(NS,t); for(const[k,v] of Object.entries(a||{{}})) n.setAttribute(k,v); if(tx!==undefined) n.textContent=tx; return n; }};
  const showTip = (e,s) => {{ tip.innerHTML=s; tip.style.display="block"; tip.style.left=Math.min(window.innerWidth-280,e.clientX+14)+"px"; tip.style.top=Math.max(10,e.clientY-20)+"px"; }};
  const hideTip = () => {{ tip.style.display="none"; }};

  const META = {{
    level: {{label:"Mean of yearly median NH₄⁺ (µg/kg) — steady background level", unit:"µg/kg"}},
    spike_years_x5: {{label:"Years per 150-yr stretch with annual peak > 5× running median", unit:"years"}},
    spike_years_add50: {{label:"Years per 150-yr stretch with peak > 50 µg/kg above baseline (anti-denominator control)", unit:"years"}},
    spike_part: {{label:"Mean of (yearly mean − yearly median) NH₄⁺ (µg/kg) — short-plume excess", unit:"µg/kg"}},
  }};

  function render(metric) {{
    svg.innerHTML = "";
    const L=60, R=720, T=30, B=245;
    const vals = WINS.map(w => w[metric]);
    const yMax = Math.max(...vals) * 1.15;
    const med = [...vals].sort((a,b)=>a-b)[Math.floor(vals.length/2)];
    const sy = v => B - (v / yMax) * (B - T);
    const bw = (R - L) / WINS.length;

    // Horizontal grid & median line
    for (let i=0; i<=4; i++) {{
      const v = (i/4)*yMax;
      const y = sy(v);
      svg.appendChild(el("line", {{x1:L, x2:R, y1:y, y2:y, stroke:"var(--line)", "stroke-width":0.7}}));
      svg.appendChild(el("text", {{x:L-7, y:y+4, "text-anchor":"end", fill:"var(--faint)", "font-size":"11"}}, yMax>=10?v.toFixed(0):v.toFixed(1)));
    }}
    svg.appendChild(el("line", {{x1:L, x2:R, y1:sy(med), y2:sy(med), stroke:"var(--ink-soft)", "stroke-dasharray":"4 3", "stroke-width":1.1}}));
    svg.appendChild(el("text", {{x:R-4, y:sy(med)-5, "text-anchor":"end", fill:"var(--ink-soft)", "font-size":"10.5"}}, `28-window median = ${{med>=10?med.toFixed(1):med.toFixed(2)}}`));

    // Regime labels
    const xYD = L + WINS.findIndex(w => w.k === 0) * bw;
    const xHol = L + WINS.findIndex(w => w.k === 8) * bw;
    svg.appendChild(el("line", {{x1:xYD, x2:xYD, y1:T-8, y2:B, stroke:"#955730", "stroke-dasharray":"3 3", "stroke-width":1.1}}));
    svg.appendChild(el("text", {{x:xYD+3, y:T-11, fill:"#955730", "font-size":"10.5", "font-weight":"600"}}, "YD onset (12,896)"));
    svg.appendChild(el("line", {{x1:xHol, x2:xHol, y1:T-8, y2:B, stroke:"#47705f", "stroke-dasharray":"3 3", "stroke-width":1.0}}));
    svg.appendChild(el("text", {{x:xHol+3, y:T-11, fill:"#47705f", "font-size":"10.5"}}, "Holocene (11,703)"));

    WINS.forEach((w, i) => {{
      const x = L + i * bw + 1.5;
      const v = w[metric];
      const y = sy(v);
      const col = w.k === 0 ? "#c04b2d" : w.k === -1 ? "#5d6672" : (w.k >= 8 ? "#47705f" : "#b8ab96");
      const r = el("rect", {{x:x, y:y, width:Math.max(4, bw-3), height:B-y, rx:2, fill:col, opacity:w.k===0||w.k===-1?0.95:0.78}});
      r.style.cursor = "pointer";
      r.addEventListener("mousemove", e => showTip(e, `<strong>Window k = ${{w.k}} (${{w.from_b2k.toLocaleString()}}–${{w.to_b2k.toLocaleString()}} b2k)</strong><br>Steady level: ${{w.level}} µg/kg · Spike excess: ${{w.spike_part}} µg/kg<br>&gt;5× spikes: ${{w.spike_years_x5}} yr · &gt;10× spikes: ${{w.spike_years_x10}} yr<br>Additive &gt;50 µg/kg: ${{w.spike_years_add50}} yr · Flux &gt;50: ${{w.spike_years_flux50}} yr`));
      r.addEventListener("mouseleave", hideTip);
      svg.appendChild(r);
      if (i % 4 === 0 || w.k === 0) {{
        svg.appendChild(el("text", {{x:x + bw/2, y:B+16, "text-anchor":"middle", fill:"var(--faint)", "font-size":"10.5"}}, (w.from_b2k/1000).toFixed(1)+"k"));
      }}
    }});
    svg.appendChild(el("text", {{x:(L+R)/2, y:B+42, "text-anchor":"middle", fill:"var(--ink-soft)", "font-size":"12"}}, META[metric].label));
  }}

  document.querySelectorAll(".ns-btn").forEach(b => {{
    b.addEventListener("click", () => {{
      document.querySelectorAll(".ns-btn").forEach(x => x.classList.remove("is-on"));
      b.classList.add("is-on");
      render(b.dataset.m);
    }});
  }});
  render("level");
}})();
</script>
</figure>
'''


def build_annual(s: dict) -> str:
    ann = s["yd_annual_series"]
    payload = json.dumps(ann)
    return f'''<figure class="fig" aria-label="Year-by-year NEEM ammonium steady median versus annual peak plume across 13,500 to 12,000 years ago">
<div class="fig-scroll"><svg id="na-svg" class="chart" viewBox="0 0 740 310" width="100%" role="img" aria-label="NEEM annual median and peak ammonium around the Younger Dryas onset"></svg></div>
<figcaption>Year-by-year anatomy of NEEM's Younger Dryas ammonium anomaly (13,500 to 12,000 years before 2000 CE; older left → younger right). Each faint vertical stem rises from that year's steady median (solid copper line) to its highest single 1-mm sample (smoke-plume peak); copper dots mark years exceeding 5× the 51-year running median. After the Younger Dryas begins (12,896 b2k, dashed line), the smooth baseline lifts abruptly and stays high for over a century while extreme plume spikes virtually vanish—the opposite of a century of repeated airburst wildfires.</figcaption>
<script>
(function(){{
  const ANN = {payload};
  const svg = document.getElementById("na-svg");
  const NS = "http://www.w3.org/2000/svg";
  const el = (t,a,tx) => {{ const n=document.createElementNS(NS,t); for(const[k,v] of Object.entries(a||{{}})) n.setAttribute(k,v); if(tx!==undefined) n.textContent=tx; return n; }};

  const L=60, R=716, T=28, B=256;
  const xOld=13500, xYng=12000;
  const sx = yr => L + (xOld - yr) / (xOld - xYng) * (R - L);
  const yMax = 220;
  const sy = v => B - Math.min(yMax, v) / yMax * (B - T);

  // Shaded Window 0 (12896 -> 12746)
  svg.appendChild(el("rect", {{x:sx(12896), y:T, width:sx(12746)-sx(12896), height:B-T, fill:"#955730", opacity:"0.11"}}));
  svg.appendChild(el("line", {{x1:sx(12896), x2:sx(12896), y1:T-6, y2:B, stroke:"#955730", "stroke-dasharray":"4 3", "stroke-width":1.3}}));
  svg.appendChild(el("text", {{x:sx(12896)+4, y:T+13, fill:"#955730", "font-size":"11", "font-weight":"600"}}, "YD onset → 150-yr window 0"));

  [0, 50, 100, 150, 200].forEach(v => {{
    const y = sy(v);
    svg.appendChild(el("line", {{x1:L, x2:R, y1:y, y2:y, stroke:"var(--line)", "stroke-width":0.7}}));
    svg.appendChild(el("text", {{x:L-7, y:y+4, "text-anchor":"end", fill:"var(--faint)", "font-size":"11"}}, String(v)));
  }});
  [13500, 13200, 12900, 12600, 12300, 12000].forEach(yr => {{
    svg.appendChild(el("text", {{x:sx(yr), y:B+18, "text-anchor":"middle", fill:"var(--faint)", "font-size":"11"}}, yr.toLocaleString()));
  }});
  svg.appendChild(el("text", {{x:(L+R)/2, y:B+42, "text-anchor":"middle", fill:"var(--ink-soft)", "font-size":"12"}}, "Years before 2000 CE (GICC05modelext-NEEM-1) · vertical stems clipped at 220 µg/kg"));
  svg.appendChild(el("text", {{x:18, y:(T+B)/2, "text-anchor":"middle", fill:"var(--ink-soft)", "font-size":"12", transform:`rotate(-90 18 ${{(T+B)/2}})`}}, "NEEM NH₄⁺ (µg/kg)"));

  // Vertical stems from yearly median to yearly max
  const sorted = [...ANN].sort((a,b) => b.year_b2k - a.year_b2k);
  sorted.forEach(d => {{
    const x = sx(d.year_b2k);
    const isSpike = d.ratio !== null && d.ratio > 5.0;
    svg.appendChild(el("line", {{x1:x, x2:x, y1:sy(d.med), y2:sy(d.top), stroke:isSpike?"#c04b2d":"#8c8273", "stroke-width":isSpike?1.2:0.7, opacity:isSpike?0.75:0.35}}));
    if (isSpike) {{
      svg.appendChild(el("circle", {{cx:x, cy:sy(d.top), r:2.4, fill:"#c04b2d"}}));
    }}
  }});

  // Yearly median line on top
  const path = sorted.map((d,i) => `${{i===0?"M":"L"}}${{sx(d.year_b2k).toFixed(1)}},${{sy(d.med).toFixed(1)}}`).join(" ");
  svg.appendChild(el("path", {{d:path, fill:"none", stroke:"#955730", "stroke-width":1.8}}));
}})();
</script>
</figure>
'''


def main() -> None:
    s = json.loads((RESULTS / "summary.json").read_text())
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, content in {
        "tiles.html": build_tiles(s),
        "verdict.html": build_verdict(s),
        "decomposition.html": build_decomposition(s),
        "annual.html": build_annual(s),
    }.items():
        (OUT_DIR / name).write_text(content)
        print(f"Wrote {OUT_DIR / name} ({len(content):,} B)")


if __name__ == "__main__":
    main()
