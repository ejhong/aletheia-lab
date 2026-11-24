#!/usr/bin/env python3
"""Generate interactive HTML/SVG figures for #15 (Secret Mark)."""
from __future__ import annotations

import html
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
RES = ROOT / "results"
OUT = ROOT.parent.parent / "site" / "figures" / "secret-mark"
OUT.mkdir(parents=True, exist_ok=True)


def esc(s: object) -> str:
    return html.escape(str(s), quote=True)


def make_tiles(s: dict) -> None:
    t1 = s["test1_attribution"]["clement_frame"]
    t3 = s["test3_lexical_criddle"]["vs_all_authentic_clement"]
    t5 = s["test5_layer_b_gospels"]
    items = [
        ("0 / 4", f"unconscious-style methods rank Clement #1 on the 529-word frame (Clement ranks #{t1['clement_rank_mfw']}, #{t1['clement_rank_c34']}, #{t1['clement_rank_gi']}, #{t1['clement_rank_lr']} behind Theodoret & Eusebius)", False),
        (f"z = {t3['r_criddle']['z_score']:+.2f}", f"Criddle rare-word ratio vs. 484 authentic Clement chunks (p = {t3['r_criddle']['p_two_sided']:.2f})—no 'hyper-Clementine' lexical packing", False),
        ("62 / 62", f"genuine Canonical Mark passages exceeded by Secret Mark in verbatim Mark+John content bigrams ({t5['cento_vs_mark_union_john']['content_bigram_rate']['mar_saba']*100:.1f}% vs. {t5['cento_vs_mark_union_john']['content_bigram_rate']['ref_mean']*100:.1f}%, z = {t5['cento_vs_mark_union_john']['content_bigram_rate']['z_score']:+.2f})", False),
        ("Split / Mixed", "Epistolary frame inconclusive (no Criddle excess, but weak Clement attribution); Secret Mark quotes show a clear Mark+John cento signature", True),
    ]
    body = ['<div class="tiles">']
    for v, lbl, is_w in items:
        cls = "tile-value is-word" if is_w else "tile-value"
        body.append(f'<div class="tile"><p class="{cls}">{esc(v)}</p><p class="tile-label">{esc(lbl)}</p></div>')
    body.append("</div>\n")
    (OUT / "tiles.html").write_text("\n".join(body), encoding="utf-8")


def make_layer_a_figure(s: dict) -> None:
    t1 = s["test1_attribution"]["clement_frame"]
    t2 = s["test2_oneclass"]
    payload = {
        "mfw": [{"a": a, "v": round(v, 4)} for a, v in t1["rank_mfw"]],
        "c34": [{"a": a, "v": round(v, 4)} for a, v in t1["rank_c34"]],
        "gi": [{"a": a, "v": round(v, 4)} for a, v in t1["rank_gi"]],
        "lr": [{"a": a, "v": round(v, 4)} for a, v in t1["rank_lr"]],
        "oneclass": [
            {"a": r["author"], "v": round(r["mar_saba_percentile"] * 100.0, 1), "d": round(r["mar_saba_dist"], 3)}
            for r in t2["per_author_oneclass"]
        ],
        "gi_thresh": round(s["test0_calibration"]["gi_clement_95_specificity_threshold"], 3),
    }
    data_json = json.dumps(payload)
    html_out = f"""<figure class="fig" aria-label="14-author Greek stylometry attribution of the Mar Saba Letter epistolary frame">
<div class="fig-controls" style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px;align-items:center">
  <span style="font-size:12px;color:var(--muted);margin-right:4px">Stylometric method (529-word Clement frame):</span>
  <button type="button" class="sm-a-btn is-on" data-m="mfw" style="font-size:12px;padding:4px 9px;border:1px solid var(--rule);border-radius:4px;background:var(--copper);color:#fff;cursor:pointer">MFW-150 Cosine Delta</button>
  <button type="button" class="sm-a-btn" data-m="c34" style="font-size:12px;padding:4px 9px;border:1px solid var(--rule);border-radius:4px;background:transparent;color:var(--ink);cursor:pointer">Char 3–4-gram Delta</button>
  <button type="button" class="sm-a-btn" data-m="gi" style="font-size:12px;padding:4px 9px;border:1px solid var(--rule);border-radius:4px;background:transparent;color:var(--ink);cursor:pointer">General Imposters</button>
  <button type="button" class="sm-a-btn" data-m="lr" style="font-size:12px;padding:4px 9px;border:1px solid var(--rule);border-radius:4px;background:transparent;color:var(--ink);cursor:pointer">TF-IDF LogReg</button>
  <button type="button" class="sm-a-btn" data-m="oneclass" style="font-size:12px;padding:4px 9px;border:1px solid var(--rule);border-radius:4px;background:transparent;color:var(--ink);cursor:pointer">One-Class Percentile</button>
</div>
<div class="fig-scroll">
<svg id="sm-a-svg" class="chart" viewBox="0 0 720 390" role="img" aria-label="14-author stylometry rankings for Mar Saba letter frame" xmlns="http://www.w3.org/2000/svg"></svg>
</div>
<figcaption><strong>Layer A (529-word epistolary frame) across 14 Greek Christian &amp; Alexandrian authors (1st–5th c. CE).</strong> Clement of Alexandria (highlighted in copper) finishes #2 on MFW-150 and Character 3–4-gram Cosine Delta and #3 on General Imposters and Logistic Regression—edged out by 4th–5th c. Fathers (Theodoret of Cyrus, Eusebius of Caesarea, Origen). Yet on one-class self-distance percentile (rightmost toggle), Clement ranks #1 (88.6th percentile, closer to Clement's training centroid than Clement's own held-out homily <em>Quis dives salvetur</em> at the 97.6th percentile). Short epistolary Greek leaves authentic Clement and later patristic prose closely overlapping.</figcaption>
<script>
(function(){{
  var DATA = {data_json};
  var svg = document.getElementById("sm-a-svg");
  var btns = document.querySelectorAll(".sm-a-btn");
  var L = 190, R = 680, T = 30, B = 355;
  function el(tag, attrs, txt){{
    var n = document.createElementNS("http://www.w3.org/2000/svg", tag);
    for (var k in attrs) n.setAttribute(k, attrs[k]);
    if (txt !== undefined) n.textContent = txt;
    return n;
  }}
  var META = {{
    mfw: {{title: "MFW-150 Function-Word Cosine Delta (lower = closer)", min: 0.65, max: 1.25, fmt: function(v){{return v.toFixed(3);}}, lower: true}},
    c34: {{title: "Character 3–4-gram Cosine Delta (lower = closer)", min: 0.75, max: 1.25, fmt: function(v){{return v.toFixed(3);}}, lower: true}},
    gi:  {{title: "General Imposters Win Rate (500 iters; higher = closer; 95%-spec line = " + DATA.gi_thresh + ")", min: 0, max: 0.28, fmt: function(v){{return (v*100).toFixed(1) + "%";}}, lower: false}},
    lr:  {{title: "L2 TF-IDF Logistic Regression Probability (higher = closer)", min: 0, max: 0.18, fmt: function(v){{return (v*100).toFixed(1) + "%";}}, lower: false}},
    oneclass: {{title: "One-Class Percentile Inside Each Author's Own Chunks (lower = better fit)", min: 70, max: 102, fmt: function(v){{return v.toFixed(1) + "%";}}, lower: true}}
  }};
  function draw(m){{
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    var rows = DATA[m];
    var meta = META[m];
    svg.appendChild(el("text", {{x: L, y: 18, "font-size": 12, "font-weight": 600, fill: "var(--ink)"}}, meta.title));
    var step = (B - T) / rows.length;
    function sx(v){{
      var t = (v - meta.min) / (meta.max - meta.min);
      if (t < 0) t = 0; if (t > 1) t = 1;
      return L + t * (R - L);
    }}
    if (m === "gi") {{
      var tx = sx(DATA.gi_thresh);
      svg.appendChild(el("line", {{x1: tx, x2: tx, y1: T, y2: B, stroke: "var(--teal)", "stroke-dasharray": "4,3", "stroke-width": 1.2}}));
    }}
    if (m === "oneclass") {{
      var tx95 = sx(95);
      svg.appendChild(el("line", {{x1: tx95, x2: tx95, y1: T, y2: B, stroke: "#b91c1c", "stroke-dasharray": "4,3", "stroke-width": 1.2}}));
    }}
    rows.forEach(function(r, i){{
      var y = T + i * step + 3;
      var h = step - 6;
      var isClem = r.a === "Clement of Alexandria";
      var xEnd = sx(r.v);
      svg.appendChild(el("text", {{x: L - 8, y: y + h * 0.72, "text-anchor": "end", "font-size": 11, "font-weight": isClem ? 700 : 400, fill: isClem ? "var(--copper)" : "var(--ink)"}}, (i+1) + ". " + r.a));
      svg.appendChild(el("rect", {{x: L, y: y, width: Math.max(2, xEnd - L), height: h, rx: 2, fill: isClem ? "var(--copper)" : "#94a3b8", opacity: isClem ? 0.92 : 0.65}}));
      svg.appendChild(el("text", {{x: xEnd + 5, y: y + h * 0.72, "font-size": 10.5, "font-weight": isClem ? 700 : 400, fill: isClem ? "var(--copper)" : "var(--muted)"}}, meta.fmt(r.v)));
    }});
  }}
  btns.forEach(function(b){{
    b.addEventListener("click", function(){{
      btns.forEach(function(x){{ x.classList.remove("is-on"); x.style.background = "transparent"; x.style.color = "var(--ink)"; }});
      b.classList.add("is-on"); b.style.background = "var(--copper)"; b.style.color = "#fff";
      draw(b.getAttribute("data-m"));
    }});
  }});
  draw("mfw");
}})();
</script>
</figure>
"""
    (OUT / "layer_a_panel.html").write_text(html_out, encoding="utf-8")


def make_lexical_and_cento_figure(s: dict) -> None:
    t3 = s["test3_lexical_criddle"]
    t5 = s["test5_layer_b_gospels"]
    payload = {
        "criddle_dist": [round(x, 4) for x in t3["clement_ref_distributions"]["r_criddle"]],
        "criddle_ms": round(t3["vs_all_authentic_clement"]["r_criddle"]["mar_saba"], 4),
        "criddle_z": round(t3["vs_all_authentic_clement"]["r_criddle"]["z_score"], 2),
        "monroe_dist": [round(x, 4) for x in t3["clement_ref_distributions"]["mean_monroe_log_odds"]],
        "monroe_ms": round(t3["vs_all_authentic_clement"]["mean_monroe_log_odds"]["mar_saba"], 4),
        "monroe_z": round(t3["vs_all_authentic_clement"]["mean_monroe_log_odds"]["z_score"], 2),
        "monroe_nonclem": round(t3["non_clement_medians"]["mean_monroe_log_odds"], 3),
        "cento_bg_dist": [round(x * 100.0, 2) for x in t5["mark_loo_content_bigram_dist"]],
        "cento_bg_sm": round(t5["cento_vs_mark"]["content_bigram_rate"]["mar_saba"] * 100.0, 1),
        "cento_bg_z": round(t5["cento_vs_mark"]["content_bigram_rate"]["z_score"], 2),
        "cento_tg_dist": [round(x * 100.0, 2) for x in t5["mark_loo_content_trigram_dist"]],
        "cento_tg_sm": round(t5["cento_vs_mark"]["content_trigram_rate"]["mar_saba"] * 100.0, 1),
        "cento_tg_z": round(t5["cento_vs_mark"]["content_trigram_rate"]["z_score"], 2),
        "cento_mj_bg_sm": round(t5["cento_vs_mark_union_john"]["content_bigram_rate"]["mar_saba"] * 100.0, 1),
        "cento_mj_bg_z": round(t5["cento_vs_mark_union_john"]["content_bigram_rate"]["z_score"], 2),
        "cento_mj_tg_sm": round(t5["cento_vs_mark_union_john"]["content_trigram_rate"]["mar_saba"] * 100.0, 1),
        "cento_mj_tg_z": round(t5["cento_vs_mark_union_john"]["content_trigram_rate"]["z_score"], 2),
    }
    data_json = json.dumps(payload)
    html_out = f"""<figure class="fig" aria-label="Comparison of Criddle hyper-Clementine lexical test vs Markan cento verbatim phrase-stitching test">
<div class="fig-controls" style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px;align-items:center">
  <span style="font-size:12px;color:var(--muted);margin-right:4px">Diagnostic test:</span>
  <button type="button" class="sm-b-btn is-on" data-k="cento_bg" style="font-size:12px;padding:4px 9px;border:1px solid var(--rule);border-radius:4px;background:var(--copper);color:#fff;cursor:pointer">Layer B: Mark Content Bigrams (Cento)</button>
  <button type="button" class="sm-b-btn" data-k="cento_tg" style="font-size:12px;padding:4px 9px;border:1px solid var(--rule);border-radius:4px;background:transparent;color:var(--ink);cursor:pointer">Layer B: Mark Content Trigrams (Cento)</button>
  <button type="button" class="sm-b-btn" data-k="criddle" style="font-size:12px;padding:4px 9px;border:1px solid var(--rule);border-radius:4px;background:transparent;color:var(--ink);cursor:pointer">Layer A: Criddle Rare-Word Ratio</button>
  <button type="button" class="sm-b-btn" data-k="monroe" style="font-size:12px;padding:4px 9px;border:1px solid var(--rule);border-radius:4px;background:transparent;color:var(--ink);cursor:pointer">Layer A: Clement Log-Odds Density</button>
</div>
<div class="fig-scroll">
<svg id="sm-b-svg" class="chart" viewBox="0 0 720 270" role="img" aria-label="Histogram comparing Mar Saba diagnostics against authentic baselines" xmlns="http://www.w3.org/2000/svg"></svg>
</div>
<figcaption><strong>Two forgery diagnostics, opposite outcomes.</strong> In <strong>Layer B (Secret Mark quotes, 181 words)</strong>, verbatim content-bigram overlap with Canonical Mark hits <strong>48.6%</strong> (z = +3.35)—higher than all 62 genuine 181-word passages of Canonical Mark (max 40.1%)—and reaches <strong>55.6%</strong> (z = +3.38) against Mark &cup; John, with 25.0% content trigrams (z = +2.93), the clear fingerprint of a Mark+John phrase cento. By contrast, in <strong>Layer A (Clement frame, 529 words)</strong>, the Criddle (1995) rare-word ratio (0.139 vs. authentic Clement 0.133 &plusmn; 0.036, z = +0.17) and Clement-distinctive vocabulary density (&minus;0.327, z = &minus;1.32 vs. all Clement; z = +0.22 vs. held-out <em>Quis dives</em> + <em>Eclogae</em>) show <strong>zero 'hyper-Clementine' packing</strong>.</figcaption>
<script>
(function(){{
  var D = {data_json};
  var svg = document.getElementById("sm-b-svg");
  var btns = document.querySelectorAll(".sm-b-btn");
  var L = 58, R = 685, T = 36, B = 222;
  function el(tag, attrs, txt){{
    var n = document.createElementNS("http://www.w3.org/2000/svg", tag);
    for (var k in attrs) n.setAttribute(k, attrs[k]);
    if (txt !== undefined) n.textContent = txt;
    return n;
  }}
  var VIEWS = {{
    cento_bg: {{
      title: "Layer B: Content-bearing bigrams appearing verbatim in Canonical Mark (62 LOO Mark chunks vs. Secret Mark)",
      arr: D.cento_bg_dist, val: D.cento_bg_sm, xmin: 10, xmax: 55, bins: 18,
      unit: "%", label: "Secret Mark: " + D.cento_bg_sm + "% (z = +" + D.cento_bg_z + ", 100th pct)",
      refLabel: "62 genuine 181-word Mark chunks (leave-one-out)", color: "#b91c1c"
    }},
    cento_tg: {{
      title: "Layer B: Content-bearing trigrams appearing verbatim in Canonical Mark (62 LOO Mark chunks vs. Secret Mark)",
      arr: D.cento_tg_dist, val: D.cento_tg_sm, xmin: 0, xmax: 24, bins: 16,
      unit: "%", label: "Secret Mark: " + D.cento_tg_sm + "% (z = +" + D.cento_tg_z + ", 100th pct)",
      refLabel: "62 genuine 181-word Mark chunks (leave-one-out)", color: "#b91c1c"
    }},
    criddle: {{
      title: "Layer A: Criddle rare-to-common ratio C1/(C1+C2+) vs. 484 authentic Clement 529-word chunks",
      arr: D.criddle_dist, val: D.criddle_ms, xmin: 0.02, xmax: 0.26, bins: 20,
      unit: "", label: "Mar Saba frame: " + D.criddle_ms + " (z = +" + D.criddle_z + ", p = 0.76)",
      refLabel: "484 authentic Clement chunks (dead center)", color: "var(--teal)"
    }},
    monroe: {{
      title: "Layer A: Mean Monroe Clement-distinctiveness log-odds vs. 484 authentic Clement chunks",
      arr: D.monroe_dist, val: D.monroe_ms, xmin: -1.8, xmax: 1.0, bins: 22,
      unit: "", label: "Mar Saba frame: " + D.monroe_ms + " (z = " + D.monroe_z + "; Non-Clement med = " + D.monroe_nonclem + ")",
      refLabel: "484 authentic Clement chunks (no hyper-Clementine excess)", color: "var(--teal)"
    }}
  }};
  function draw(k){{
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    var v = VIEWS[k];
    svg.appendChild(el("text", {{x: L, y: 20, "font-size": 12, "font-weight": 600, fill: "var(--ink)"}}, v.title));
    var bw = (v.xmax - v.xmin) / v.bins;
    var counts = new Array(v.bins).fill(0);
    v.arr.forEach(function(x){{
      var bi = Math.floor((x - v.xmin) / bw);
      if (bi >= 0 && bi < v.bins) counts[bi]++;
    }});
    var maxC = Math.max.apply(null, counts) || 1;
    function sx(x){{ return L + (x - v.xmin) / (v.xmax - v.xmin) * (R - L); }}
    function sy(c){{ return B - (c / maxC) * (B - T - 14); }}
    // Axes
    svg.appendChild(el("line", {{x1: L, x2: R, y1: B, y2: B, stroke: "var(--rule)"}}));
    counts.forEach(function(c, i){{
      var x0 = sx(v.xmin + i * bw);
      var x1 = sx(v.xmin + (i + 1) * bw);
      var y0 = sy(c);
      svg.appendChild(el("rect", {{x: x0 + 1, y: y0, width: Math.max(1, x1 - x0 - 2), height: B - y0, fill: "#94a3b8", opacity: 0.72}}));
    }});
    // Ticks
    for (var ti = 0; ti <= 5; ti++){{
      var tv = v.xmin + ti * (v.xmax - v.xmin) / 5;
      var tx = sx(tv);
      svg.appendChild(el("line", {{x1: tx, x2: tx, y1: B, y2: B + 4, stroke: "var(--muted)"}}));
      var txt = (v.unit === "%") ? tv.toFixed(0) + "%" : tv.toFixed(2);
      svg.appendChild(el("text", {{x: tx, y: B + 17, "text-anchor": "middle", "font-size": 10.5, fill: "var(--muted)"}}, txt));
    }}
    // Non-Clement marker on monroe
    if (k === "monroe") {{
      var nx = sx(D.monroe_nonclem);
      svg.appendChild(el("line", {{x1: nx, x2: nx, y1: T + 18, y2: B, stroke: "#64748b", "stroke-dasharray": "3,3", "stroke-width": 1.3}}));
      svg.appendChild(el("text", {{x: nx + 4, y: T + 32, "font-size": 10, fill: "#64748b"}}, "Non-Clement median (" + D.monroe_nonclem + ")"));
    }}
    // Target vertical line
    var mx = sx(v.val);
    svg.appendChild(el("line", {{x1: mx, x2: mx, y1: T + 4, y2: B, stroke: v.color, "stroke-width": 2.4}}));
    var anchor = mx > (L + R) * 0.58 ? "end" : "start";
    var lx = anchor === "end" ? mx - 6 : mx + 6;
    svg.appendChild(el("text", {{x: lx, y: T + 16, "text-anchor": anchor, "font-size": 11.5, "font-weight": 700, fill: v.color}}, v.label));
    svg.appendChild(el("text", {{x: (L + R)/2, y: 258, "text-anchor": "middle", "font-size": 11, fill: "var(--muted)"}}, v.refLabel));
  }}
  btns.forEach(function(b){{
    b.addEventListener("click", function(){{
      btns.forEach(function(x){{ x.classList.remove("is-on"); x.style.background = "transparent"; x.style.color = "var(--ink)"; }});
      b.classList.add("is-on"); b.style.background = "var(--copper)"; b.style.color = "#fff";
      draw(b.getAttribute("data-k"));
    }});
  }});
  draw("cento_bg");
}})();
</script>
</figure>
"""
    (OUT / "lexical_and_cento.html").write_text(html_out, encoding="utf-8")


def main():
    summary = json.loads((RES / "stylometry_summary.json").read_text(encoding="utf-8"))
    make_tiles(summary)
    make_layer_a_figure(summary)
    make_lexical_and_cento_figure(summary)
    print("Generated 3 figures in", OUT)


if __name__ == "__main__":
    main()
