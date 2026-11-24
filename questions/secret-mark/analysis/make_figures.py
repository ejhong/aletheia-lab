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
        ("2nd or 3rd", "where Clement comes among 14 authors on each of four measures of style, for the letter proper; never first", False),
        ("6% to 24%", "how often three of the same measures recognise Clement's own short homily as his; the letter is too short to judge by style", False),
        ("49% against 28%", "of two-word phrases found word for word in Mark: the quoted passages, against the average for 62 passages of Mark itself (highest 40%)", False),
        ("Inconclusive", "Style cannot say who wrote the letter. The quoted passages are unusually dense in Mark's phrases, which fits imitation and gives no date", True),
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
  <button type="button" class="sm-a-btn is-on" data-m="mfw" style="font-size:12px;padding:4px 9px;border:1px solid var(--rule);border-radius:4px;background:var(--copper);color:#fff;cursor:pointer">Common words</button>
  <button type="button" class="sm-a-btn" data-m="c34" style="font-size:12px;padding:4px 9px;border:1px solid var(--rule);border-radius:4px;background:transparent;color:var(--ink);cursor:pointer">Letter groups</button>
  <button type="button" class="sm-a-btn" data-m="gi" style="font-size:12px;padding:4px 9px;border:1px solid var(--rule);border-radius:4px;background:transparent;color:var(--ink);cursor:pointer">Imposters test</button>
  <button type="button" class="sm-a-btn" data-m="lr" style="font-size:12px;padding:4px 9px;border:1px solid var(--rule);border-radius:4px;background:transparent;color:var(--ink);cursor:pointer">Classifier</button>
  <button type="button" class="sm-a-btn" data-m="oneclass" style="font-size:12px;padding:4px 9px;border:1px solid var(--rule);border-radius:4px;background:transparent;color:var(--ink);cursor:pointer">Distance from each author</button>
</div>
<div class="fig-scroll">
<svg id="sm-a-svg" class="chart" viewBox="0 0 720 390" role="img" aria-label="14-author stylometry rankings for Mar Saba letter frame" xmlns="http://www.w3.org/2000/svg"></svg>
</div>
<figcaption><strong>The letter proper (529 words) against 14 Greek Christian authors of the first to fifth centuries.</strong> Each button is one measure of style; Clement is in copper. He comes second or third on the first four and never first; a fifth-century writer, Theodoret, comes first on three. The last button shows how far the letter sits from the middle of each author&rsquo;s own writing: it is nearest Clement (88.6th percentile), but Eusebius, Epiphanius and Theodoret are within two points, and Clement&rsquo;s own short homily <em>Quis dives salvetur</em> sits further out (97.6th). At this length the measures cannot tell.</figcaption>
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
  <button type="button" class="sm-b-btn is-on" data-k="cento_bg" style="font-size:12px;padding:4px 9px;border:1px solid var(--rule);border-radius:4px;background:var(--copper);color:#fff;cursor:pointer">Two-word phrases</button>
  <button type="button" class="sm-b-btn" data-k="cento_tg" style="font-size:12px;padding:4px 9px;border:1px solid var(--rule);border-radius:4px;background:transparent;color:var(--ink);cursor:pointer">Three-word phrases</button>
  <button type="button" class="sm-b-btn" data-k="criddle" style="font-size:12px;padding:4px 9px;border:1px solid var(--rule);border-radius:4px;background:transparent;color:var(--ink);cursor:pointer">Rare-word ratio</button>
  <button type="button" class="sm-b-btn" data-k="monroe" style="font-size:12px;padding:4px 9px;border:1px solid var(--rule);border-radius:4px;background:transparent;color:var(--ink);cursor:pointer">Clementine vocabulary</button>
</div>
<div class="fig-scroll">
<svg id="sm-b-svg" class="chart" viewBox="0 0 720 270" role="img" aria-label="Histogram comparing Mar Saba diagnostics against authentic baselines" xmlns="http://www.w3.org/2000/svg"></svg>
</div>
<figcaption><strong>Two tests.</strong> The first two buttons: the share of the quoted passages&rsquo; two-word and three-word phrases that occur word for word in Mark, against the same share for 62 passages of Mark, each compared with the rest of the gospel. The quotations stand above all 62 on two-word phrases (48.6% against a highest of 40.1%). On three-word phrases the margin depends on where the passages are cut. The last two buttons: two measures of how Clementine the letter&rsquo;s vocabulary is, against 484 passages of Clement. The letter is ordinary on both. The first of them is not the ratio Andrew Criddle used in 1995, so it does not test his argument.</figcaption>
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
      title: "Two-word phrases found word for word in Mark (common words left out)",
      arr: D.cento_bg_dist, val: D.cento_bg_sm, xmin: 10, xmax: 55, bins: 18,
      unit: "%", label: "Quoted passages: " + D.cento_bg_sm + "% (above all 62)",
      refLabel: "62 passages of Mark, 181 words each", color: "#b91c1c"
    }},
    cento_tg: {{
      title: "Three-word phrases found word for word in Mark (common words left out)",
      arr: D.cento_tg_dist, val: D.cento_tg_sm, xmin: 0, xmax: 24, bins: 16,
      unit: "%", label: "Quoted passages: " + D.cento_tg_sm + "% (above all 62 as cut here)",
      refLabel: "62 passages of Mark, 181 words each", color: "#b91c1c"
    }},
    criddle: {{
      title: "The letter's rare-word ratio against 484 passages of Clement (not Criddle's ratio)",
      arr: D.criddle_dist, val: D.criddle_ms, xmin: 0.02, xmax: 0.26, bins: 20,
      unit: "", label: "The letter: " + D.criddle_ms,
      refLabel: "484 passages of Clement", color: "var(--teal)"
    }},
    monroe: {{
      title: "How Clementine the letter's vocabulary is, against 484 passages of Clement",
      arr: D.monroe_dist, val: D.monroe_ms, xmin: -1.8, xmax: 1.0, bins: 22,
      unit: "", label: "The letter: " + D.monroe_ms + " (other authors: " + D.monroe_nonclem + ")",
      refLabel: "484 passages of Clement", color: "var(--teal)"
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
