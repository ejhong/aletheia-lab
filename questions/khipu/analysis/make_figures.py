#!/usr/bin/env python3
"""Generate interactive HTML/SVG figures for #13 (khipu)."""
from __future__ import annotations

import html
import json
import pathlib
import sqlite3

ROOT = pathlib.Path(__file__).resolve().parent.parent
RES = ROOT / "results"
DB_PATH = ROOT / "data" / "khipu.db"
OUT = ROOT.parent.parent / "site" / "figures" / "khipu"
OUT.mkdir(parents=True, exist_ok=True)


def esc(s: object) -> str:
    return html.escape(str(s), quote=True)


def make_tiles(s: dict) -> None:
    t2 = s["test2a_copy_mirror_hunt"]
    t1 = s["test1_santa_valley"]
    t3 = s["test3_readiness_census"]
    n_ready = sum(r["n_rosetta_ready"] for r in t3)
    p_mu = t1["combinatorial_moiety_null"]["dirichlet_1.0_uniform"]["p_L1_le_5_medrano_urton"] * 100
    p_fp = t1["combinatorial_moiety_null"]["dirichlet_1.0_uniform"]["p_L1_le_3_fitzpatrick"] * 100
    items = [
        ("5", "pairs of khipus sharing runs of numbers that we did not find in the published literature; candidates, not confirmed", False),
        ("174 cords", "match between a khipu in Paris and one in Lima, 122 of them exactly: nearly the whole of the Lima khipu", False),
        ("2 and 1", "of the eight pairs first reported were published in 2005, and one is a single khipu catalogued twice", False),
        ("Inconclusive", "by the plan's own rule: the matcher missed a known pair, and chance produces about one false match per two scans", True),
    ]
    body = ['<div class="tiles">']
    for v, lbl, is_w in items:
        cls = "tile-value is-word" if is_w else "tile-value"
        body.append(f'<div class="tile"><p class="{cls}">{esc(v)}</p><p class="tile-label">{esc(lbl)}</p></div>')
    body.append("</div>\n")
    (OUT / "tiles.html").write_text("\n".join(body), encoding="utf-8")


def get_full_aligned_values(okr_a: str, okr_b: str, off_a: int, off_b: int, L: int, orient: str) -> tuple[list[int], list[int]]:
    con = sqlite3.connect(str(DB_PATH))
    cur = con.cursor()
    def load(okr):
        kid = cur.execute("SELECT KHIPU_ID FROM khipu_main WHERE OKR_NUM=?", (okr,)).fetchone()[0]
        rows = cur.execute("""
            SELECT COALESCE(SUM(CASE WHEN k.knot_value_type>0 THEN k.knot_value_type ELSE 0 END), 0)
            FROM cord c
            LEFT JOIN knot k ON k.CORD_ID = c.CORD_ID
            LEFT JOIN cord_cluster cc ON cc.CLUSTER_ID = c.CLUSTER_ID
            WHERE c.KHIPU_ID=? AND c.CORD_LEVEL=1
            GROUP BY c.CORD_ID
            ORDER BY c.CORD_ORDINAL, COALESCE(cc.ORDINAL, 0), c.CLUSTER_ORDINAL, c.CORD_ID
        """, (kid,)).fetchall()
        return [int(r[0]) for r in rows]
    va = load(okr_a)
    vb = load(okr_b)
    con.close()
    if orient == "rev":
        vb = list(reversed(vb))
    return va[off_a:off_a + L], vb[off_b:off_b + L]


def make_rosetta_twins(s: dict) -> None:
    # Build showcase dataset of the strongest Tier A matches (exact values from khipu.db)
    by_pair = {(h["khipu_a"], h["khipu_b"]): h for h in s["test2a_copy_mirror_hunt"]["pendant_hits"] if h["tier"] == "A"}

    def pack_pendant(key, short_lbl, title, subtitle):
        h = by_pair[key]
        va, vb = get_full_aligned_values(h["khipu_a"], h["khipu_b"], h["offset_a"], h["offset_b"], h["L"], h["orient"])
        return {
            "id": f"{key[0]}_{key[1]}",
            "btn": short_lbl,
            "title": title,
            "sub": subtitle,
            "label_a": f"{h['khipu_a']} ({h['prov_a']})",
            "label_b": f"{h['khipu_b']} ({h['prov_b']})",
            "vals_a": va,
            "vals_b": vb,
            "err": h["err_l1"],
            "orient": h["orient"],
        }

    cases = [
        pack_pendant(
            ("KH0362", "KH0049"),
            "Gothenburg and Lima",
            "KH0362 (Nazca — Göteborg, Sweden) ↔ KH0049 (Costa Sur — Lima, Peru)",
            "23 consecutive 3- and 4-digit cords | Sum 34,875 vs 34,888 | 19/23 exact, 23/23 within 1% (L1 error = 0.095%)",
        ),
        {
            "id": "KH0192_KH0470",
            "btn": "Pachacamac and Huacho",
            "title": "KH0192 (Pachacamac — 5-cord groups) ↔ KH0470 (Huacho — 6-cord groups)",
            "sub": "6 consecutive exact cluster sums (100% identical, L1 error = 0.000%) linking two coastal sites ~130 km apart",
            "label_a": "KH0192 (Pachacamac, 5-cord template)",
            "label_b": "KH0470 (Huacho, 6-cord template)",
            "vals_a": [173, 275, 317, 329, 23, 171],
            "vals_b": [173, 275, 317, 329, 23, 171],
            "err": 0.0,
            "orient": "fwd",
        },
        pack_pendant(
            ("KH0121", "KH0473"),
            "One khipu, recorded twice",
            "KH0121 (Marquez — Berlin VA24370(B)) ↔ KH0473 (Unknown — Berlin VA 66834)",
            "17 consecutive cords in REVERSE orientation | 16/17 exact (1,766 vs 1,772; L1 error = 0.34%) — links unprovenanced khipu to Marquez",
        ),
        pack_pendant(
            ("KH0132", "KH0456"),
            "Two from Pachacamac",
            "KH0132 (Pachacamac — VA42601) ↔ KH0456 (Pachacamac — VA 42559)",
            "8 consecutive 3-digit all-white cords | 7/8 exact (4,291 vs 4,288; L1 error = 0.07%)",
        ),
        pack_pendant(
            ("KH0128", "KH0137"),
            "Ica (published 2005)",
            "KH0128 (Between Ica & Pisco — VA16148) ↔ KH0137 (Ica — VA47085)",
            "10 consecutive cords 100.0% exact (335 = 335; L1 error = 0.000%)",
        ),
        pack_pendant(
            ("KH0097", "KH0586"),
            "Paris and Lima",
            "KH0097 (Unknown — Quai Branly, Paris) ↔ KH0586 (Unknown — MNAAHP, Lima)",
            "8 consecutive cords across two unprovenanced khipus in Paris and Lima (558 vs 555; L1 error = 0.54%)",
        ),
        pack_pendant(
            ("KH0305", "KH0301"),
            "Puruchuco (known copy)",
            "Positive Control: KH0305 (UR068) ↔ KH0301 (UR064, Puruchuco Archive)",
            "Blindly recovered without provenance labels: 36 consecutive cords (1,436 vs 1,426; L1 error = 0.70%)",
        ),
    ]

    data_json = json.dumps(cases)
    btns_html = "\n".join(
        f'  <button type="button" class="kh-t-btn{" is-on" if i == 0 else ""}" data-idx="{i}" '
        f'style="font-size:11.5px;padding:4px 8px;border:1px solid var(--rule);border-radius:4px;'
        f'background:{"var(--copper)" if i == 0 else "transparent"};color:{"#fff" if i == 0 else "var(--ink)"};cursor:pointer">'
        f'{esc(c["btn"])}</button>'
        for i, c in enumerate(cases)
    )
    html_out = f"""<figure class="fig" aria-label="Cord-by-cord comparison of pairs of khipus that share runs of numbers">
<div class="fig-controls" style="display:flex;flex-wrap:wrap;gap:5px;margin-bottom:10px;align-items:center">
  <span style="font-size:12px;color:var(--muted);margin-right:2px">Select pair:</span>
{btns_html}
</div>
<div class="fig-scroll">
<svg id="kh-t-svg" class="chart" viewBox="0 0 720 335" role="img" aria-label="Aligned numerical cord values for paired khipus" xmlns="http://www.w3.org/2000/svg"></svg>
</div>
<figcaption><strong>Runs of numbers shared by two khipus.</strong> Each button is one pair; the bars show the numbers knotted on successive cords, one khipu dark and the other copper. Equal bars side by side are cords with the same number. The windows are the ones the first run reported. The Paris and Lima pair in fact agrees over about 174 cords, and the Gothenburg and Lima pair over 37. The pair marked &ldquo;one khipu&rdquo; is a single object entered in the database twice. The Ica pair was published by Urton in 2005. The last button is a known copy from Puruchuco, for comparison.</figcaption>
<script>
(function(){{
  var CASES = {data_json};
  var svg = document.getElementById("kh-t-svg");
  var btns = document.querySelectorAll(".kh-t-btn");
  function el(tag, attrs, txt){{
    var n = document.createElementNS("http://www.w3.org/2000/svg", tag);
    for (var k in attrs) n.setAttribute(k, attrs[k]);
    if (txt !== undefined) n.textContent = txt;
    return n;
  }}
  function draw(idx){{
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    var c = CASES[idx];
    var L = 58, R = 696, T = 58, B = 278;
    svg.appendChild(el("text", {{x: 16, y: 18, "font-size": 12.2, "font-weight": 700, fill: "var(--ink)"}}, c.title));
    svg.appendChild(el("text", {{x: 16, y: 34, "font-size": 10.2, fill: "var(--muted)"}}, c.sub));

    // Legend
    svg.appendChild(el("rect", {{x: 16, y: 42, width: 10, height: 10, rx: 1.5, fill: "var(--teal)"}}));
    svg.appendChild(el("text", {{x: 31, y: 50.5, "font-size": 10, fill: "var(--ink)"}}, c.label_a));
    svg.appendChild(el("rect", {{x: 360, y: 42, width: 10, height: 10, rx: 1.5, fill: "var(--copper)"}}));
    svg.appendChild(el("text", {{x: 375, y: 50.5, "font-size": 10, fill: "var(--ink)"}}, c.label_b + (c.orient === "rev" ? " [reversed]" : "")));

    var n = c.vals_a.length;
    var vmax = 1;
    for (var i = 0; i < n; i++) {{
      if (c.vals_a[i] > vmax) vmax = c.vals_a[i];
      if (c.vals_b[i] > vmax) vmax = c.vals_b[i];
    }}
    // Nice y scale
    function sy(v){{ return B - (v / (vmax * 1.08)) * (B - T); }}
    svg.appendChild(el("line", {{x1: L, x2: R, y1: B, y2: B, stroke: "var(--rule)"}}));
    svg.appendChild(el("line", {{x1: L, x2: L, y1: T, y2: B, stroke: "var(--rule)"}}));
    [0, 0.25, 0.5, 0.75, 1.0].forEach(function(f){{
      var yv = Math.round(vmax * f);
      var y = sy(yv);
      svg.appendChild(el("line", {{x1: L, x2: R, y1: y, y2: y, stroke: "var(--rule)", "stroke-dasharray": "2,3", opacity: 0.45}}));
      svg.appendChild(el("text", {{x: L - 6, y: y + 3.5, "text-anchor": "end", "font-size": 9.5, fill: "var(--muted)"}}, yv.toLocaleString()));
    }});

    var step = (R - L) / n;
    var bw = Math.max(3, Math.min(20, step * 0.38));
    for (var i = 0; i < n; i++) {{
      var cx = L + (i + 0.5) * step;
      var va = c.vals_a[i], vb = c.vals_b[i];
      var ya = sy(va), yb = sy(vb);
      var ra = el("rect", {{x: (cx - bw - 0.8).toFixed(1), y: ya.toFixed(1), width: bw.toFixed(1), height: Math.max(1.5, B - ya).toFixed(1), rx: 1.5, fill: "var(--teal)", opacity: 0.88}});
      ra.appendChild(el("title", {{}}, "Pos " + (i+1) + " | " + c.label_a + ": " + va + " vs " + c.label_b + ": " + vb));
      svg.appendChild(ra);
      var rb = el("rect", {{x: (cx + 0.8).toFixed(1), y: yb.toFixed(1), width: bw.toFixed(1), height: Math.max(1.5, B - yb).toFixed(1), rx: 1.5, fill: "var(--copper)", opacity: 0.88}});
      rb.appendChild(el("title", {{}}, "Pos " + (i+1) + " | " + c.label_a + ": " + va + " vs " + c.label_b + ": " + vb));
      svg.appendChild(rb);
      if (n <= 12) {{
        svg.appendChild(el("text", {{x: cx.toFixed(1), y: Math.min(ya, yb) - 5, "text-anchor": "middle", "font-size": 9, fill: "var(--ink)"}}, va === vb ? String(va) : (va + "/" + vb)));
      }}
      if (n <= 24 || i % 2 === 0) {{
        svg.appendChild(el("text", {{x: cx.toFixed(1), y: B + 14, "text-anchor": "middle", "font-size": 8.8, fill: "var(--muted)"}}, String(i + 1)));
      }}
    }}
    svg.appendChild(el("text", {{x: (L + R) / 2, y: 318, "text-anchor": "middle", "font-size": 10.5, fill: "var(--muted)"}}, "Aligned cord / cluster position across matching window (hover any bar pair for exact values)"));
  }}
  btns.forEach(function(b){{
    b.addEventListener("click", function(){{
      btns.forEach(function(x){{ x.classList.remove("is-on"); x.style.background = "transparent"; x.style.color = "var(--ink)"; }});
      b.classList.add("is-on"); b.style.background = "var(--copper)"; b.style.color = "#fff";
      draw(parseInt(b.getAttribute("data-idx"), 10));
    }});
  }});
  draw(0);
}})();
</script>
</figure>
"""
    (OUT / "rosetta_twins.html").write_text(html_out, encoding="utf-8")


def make_santa_and_census(s: dict) -> None:
    t1 = s["test1_santa_valley"]
    mc = t1["combinatorial_moiety_null"]
    bars_santa = [
        {"lbl": "Uniform Dirichlet(1.0) — Match ≤ Medrano & Urton (L1 ≤ 5)", "pct": round(mc["dirichlet_1.0_uniform"]["p_L1_le_5_medrano_urton"] * 100, 1), "col": "var(--copper)"},
        {"lbl": "Uniform Dirichlet(1.0) — Match ≤ FitzPatrick (L1 ≤ 3)", "pct": round(mc["dirichlet_1.0_uniform"]["p_L1_le_3_fitzpatrick"] * 100, 1), "col": "var(--copper)"},
        {"lbl": "Overdispersed Dirichlet(0.5) — Match ≤ Medrano & Urton (L1 ≤ 5)", "pct": round(mc["dirichlet_0.5_overdispersed"]["p_L1_le_5_medrano_urton"] * 100, 1), "col": "var(--teal)"},
        {"lbl": "Overdispersed Dirichlet(0.5) — Match ≤ FitzPatrick (L1 ≤ 3)", "pct": round(mc["dirichlet_0.5_overdispersed"]["p_L1_le_3_fitzpatrick"] * 100, 1), "col": "var(--teal)"},
        {"lbl": "Random 6-khipu bundle matching (132 ± 5% groups & 367 ± 30% sum)", "pct": round(t1["corpus_spurious_bundle_null"]["match_132_5pct_and_367_30pct_rate"] * 100, 2), "col": "#475569"},
    ]
    census = [r for r in s["test3_readiness_census"] if r["n_khipus"] >= 6]
    payload = {"santa": bars_santa, "census": census}
    data_json = json.dumps(payload)
    html_out = f"""<figure class="fig" aria-label="The Santa valley split, and the khipus by provenance">
<div class="fig-controls" style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px;align-items:center">
  <span style="font-size:12px;color:var(--muted);margin-right:4px">View:</span>
  <button type="button" class="kh-s-btn is-on" data-k="santa" style="font-size:12px;padding:4px 9px;border:1px solid var(--rule);border-radius:4px;background:var(--copper);color:#fff;cursor:pointer">Santa valley split</button>
  <button type="button" class="kh-s-btn" data-k="census" style="font-size:12px;padding:4px 9px;border:1px solid var(--rule);border-radius:4px;background:transparent;color:var(--ink);cursor:pointer">Where the khipus come from</button>
</div>
<div class="fig-scroll">
<svg id="kh-s-svg" class="chart" viewBox="0 0 720 330" role="img" aria-label="Santa Valley null probabilities and OKR provenance census" xmlns="http://www.w3.org/2000/svg"></svg>
</div>
<figcaption><strong>First button: one part of the Santa valley match.</strong> Six khipus have been matched to a census of 1670 with six lineage groups. If the groups may be split three against three in any of ten ways, most random sets of six numbers can be made to fit the khipus&rsquo; two halves as closely as the published split does. If the split was fixed beforehand, fewer than one in ten can. Which it was, this study did not establish, and the published match rests on more than the split. <strong>Second button:</strong> the 619 khipus by where they are said to come from; 221 have no recorded provenance.</figcaption>
<script>
(function(){{
  var D = {data_json};
  var svg = document.getElementById("kh-s-svg");
  var btns = document.querySelectorAll(".kh-s-btn");
  function el(tag, attrs, txt){{
    var n = document.createElementNS("http://www.w3.org/2000/svg", tag);
    for (var k in attrs) n.setAttribute(k, attrs[k]);
    if (txt !== undefined) n.textContent = txt;
    return n;
  }}
  function draw(k){{
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    if (k === "santa") {{
      var L = 345, R = 675, T = 38, B = 278;
      function sx(v){{ return L + (v / 85) * (R - L); }}
      svg.appendChild(el("text", {{x: 16, y: 20, "font-size": 12, "font-weight": 600, fill: "var(--ink)"}}, "Null probability (%) of matching Santa Valley 1670 benchmarks by chance (20,000 MC draws)"));
      svg.appendChild(el("line", {{x1: L, x2: R, y1: B, y2: B, stroke: "var(--rule)"}}));
      svg.appendChild(el("line", {{x1: L, x2: L, y1: T, y2: B, stroke: "var(--rule)"}}));
      [0, 20, 40, 60, 80].forEach(function(v){{
        var x = sx(v);
        svg.appendChild(el("line", {{x1: x, x2: x, y1: T, y2: B, stroke: "var(--rule)", "stroke-dasharray": "2,3", opacity: 0.45}}));
        svg.appendChild(el("text", {{x: x, y: B + 16, "text-anchor": "middle", "font-size": 10, fill: "var(--muted)"}}, v + "%"));
      }});
      var step = (B - T) / D.santa.length;
      D.santa.forEach(function(b, i){{
        var y = T + i * step + 10, bh = step - 20;
        svg.appendChild(el("text", {{x: L - 10, y: y + bh * 0.65, "text-anchor": "end", "font-size": 10.2, fill: "var(--ink)"}}, b.lbl));
        var w = Math.max(2, sx(b.pct) - L);
        svg.appendChild(el("rect", {{x: L, y: y, width: w, height: bh, rx: 2.5, fill: b.col, opacity: 0.88}}));
        svg.appendChild(el("text", {{x: L + w + 6, y: y + bh * 0.65, "font-size": 10.5, "font-weight": 700, fill: b.col}}, b.pct.toFixed(b.pct < 1 ? 2 : 1) + "%"));
      }});
      svg.appendChild(el("text", {{x: (L + R) / 2, y: 316, "text-anchor": "middle", "font-size": 10.2, fill: "var(--muted)"}}, "Choosing the best of 10 three-vs-three partitions makes a near-70/63 moiety split common by chance alone"));
    }} else {{
      var L = 195, R = 675, T = 40, B = 285;
      var xmax = 240;
      function sx(v){{ return L + (v / xmax) * (R - L); }}
      svg.appendChild(el("text", {{x: 16, y: 20, "font-size": 12, "font-weight": 600, fill: "var(--ink)"}}, "The 619 khipus by stated provenance: all, with ten or more knotted cords, and with repeated groups"));
      svg.appendChild(el("rect", {{x: 420, y: 10, width: 10, height: 10, fill: "#cbd5e1"}}));
      svg.appendChild(el("text", {{x: 434, y: 19, "font-size": 9.5, fill: "var(--ink)"}}, "Total"));
      svg.appendChild(el("rect", {{x: 472, y: 10, width: 10, height: 10, fill: "var(--teal)"}}));
      svg.appendChild(el("text", {{x: 486, y: 19, "font-size": 9.5, fill: "var(--ink)"}}, "≥10 knotted"));
      svg.appendChild(el("rect", {{x: 558, y: 10, width: 10, height: 10, fill: "var(--copper)"}}));
      svg.appendChild(el("text", {{x: 572, y: 19, "font-size": 9.5, fill: "var(--ink)"}}, "knotted, grouped, provenanced"));

      svg.appendChild(el("line", {{x1: L, x2: R, y1: B, y2: B, stroke: "var(--rule)"}}));
      svg.appendChild(el("line", {{x1: L, x2: L, y1: T, y2: B, stroke: "var(--rule)"}}));
      [0, 50, 100, 150, 200].forEach(function(v){{
        var x = sx(v);
        svg.appendChild(el("text", {{x: x, y: B + 15, "text-anchor": "middle", "font-size": 9.5, fill: "var(--muted)"}}, String(v)));
      }});
      var step = (B - T) / D.census.length;
      D.census.forEach(function(r, i){{
        var y = T + i * step + 4, h = step - 8;
        svg.appendChild(el("text", {{x: L - 8, y: y + h * 0.72, "text-anchor": "end", "font-size": 10, fill: "var(--ink)"}}, r.provenance));
        svg.appendChild(el("rect", {{x: L, y: y, width: Math.max(2, sx(r.n_khipus) - L), height: h, rx: 2, fill: "#cbd5e1"}}));
        svg.appendChild(el("rect", {{x: L, y: y, width: Math.max(1, sx(r.n_ge10_knotted) - L), height: h, rx: 2, fill: "var(--teal)", opacity: 0.72}}));
        if (r.n_rosetta_ready > 0) {{
          svg.appendChild(el("rect", {{x: L, y: y, width: Math.max(2, sx(r.n_rosetta_ready) - L), height: h, rx: 2, fill: "var(--copper)", opacity: 0.92}}));
        }}
        svg.appendChild(el("text", {{x: sx(r.n_khipus) + 5, y: y + h * 0.72, "font-size": 9.3, fill: "var(--muted)"}}, r.n_khipus + " (" + r.n_rosetta_ready + " ready)"));
      }});
      svg.appendChild(el("text", {{x: (L + R) / 2, y: 318, "text-anchor": "middle", "font-size": 10.2, fill: "var(--muted)"}}, "Top digitization targets for colonial revisitas: Pachacamac (35), Incahuasi (23), Ica (18), Leymebamba (9), Nazca (9)"));
    }}
  }}
  btns.forEach(function(b){{
    b.addEventListener("click", function(){{
      btns.forEach(function(x){{ x.classList.remove("is-on"); x.style.background = "transparent"; x.style.color = "var(--ink)"; }});
      b.classList.add("is-on"); b.style.background = "var(--copper)"; b.style.color = "#fff";
      draw(b.getAttribute("data-k"));
    }});
  }});
  draw("santa");
}})();
</script>
</figure>
"""
    (OUT / "santa_and_census.html").write_text(html_out, encoding="utf-8")


def main() -> None:
    s = json.loads((RES / "khipu_summary.json").read_text(encoding="utf-8"))
    make_tiles(s)
    make_rosetta_twins(s)
    make_santa_and_census(s)
    print(f"Wrote 3 figures to {OUT}")


if __name__ == "__main__":
    main()
