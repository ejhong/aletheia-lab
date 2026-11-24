#!/usr/bin/env python3
"""Generate interactive HTML/SVG + real multibeam hillshade figures for #84 (drowned-walls)."""
from __future__ import annotations

import base64
import html
import io
import json
import pathlib

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
RES = ROOT / "results"
PREV = ROOT / "data" / "previews"
OUT = ROOT.parent.parent / "site" / "figures" / "drowned-walls"
OUT.mkdir(parents=True, exist_ok=True)


def esc(s: object) -> str:
    return html.escape(str(s), quote=True)


def encode_preview_jpeg(png_path: pathlib.Path, max_w: int = 860, quality: int = 82) -> str:
    im = Image.open(png_path).convert("RGB")
    if im.width > max_w:
        nh = int(round(im.height * (max_w / im.width)))
        im = im.resize((max_w, nh), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=quality, optimize=True)
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/jpeg;base64,{b64}"


def make_tiles(s: dict) -> None:
    cal = s["calibration"]
    ov = s["search_overview"]
    items = [
        (f"{ov['total_valid_seafloor_km2']:.0f} km²", "of seabed examined, in 40 tiles on four stretches of the US shelf that were dry land in the Ice Age", False),
        ("0", "ridges left unexplained: bedrock ledges, bedforms, dumped spoil and a charted wreck account for all that were found", False),
        ("under 1 in 20", "is how often the detector finds a planted wall of the size of the one real example, the Baltic's Blinkerwall", False),
        ("Too coarse", "Nothing found, by a method that would miss the kind of wall it was looking for", True),
    ]
    body = ['<div class="tiles">']
    for v, lbl, is_w in items:
        cls = "tile-value is-word" if is_w else "tile-value"
        body.append(f'<div class="tile"><p class="{cls}">{esc(v)}</p><p class="tile-label">{esc(lbl)}</p></div>')
    body.append("</div>\n")
    (OUT / "tiles.html").write_text("\n".join(body), encoding="utf-8")


def make_sonar_gallery() -> None:
    slides = [
        {
            "btn": "1. Point Judith breakwater",
            "title": "Point Judith breakwater, Rhode Island (a modern structure used as a control)",
            "note": "What the detector marked (yellow) is the harbour-side slope of the breakwater beside a gap in the data, not a wall with two sides. It passed because a filter was skipped where one side has no data. The second control site, in Delaware, has no data at all.",
            "img": encode_preview_jpeg(PREV / "CTRL_PTJUDITH.png"),
        },
        {
            "btn": "2. A planted wall",
            "title": "A synthetic wall, 250 m long, 4 m wide and 0.7 m high, added to a real tile",
            "note": "The planted wall is the diagonal line left of centre. In this tile the detector did not find it; it found 8 of the 10 planted. A wall of the size of the real Baltic one (under 2 m wide, about 0.5 m high) is found less than one time in twenty.",
            "img": encode_preview_jpeg(PREV / "CALIB_PLANTED_WALL.png"),
        },
        {
            "btn": "3. Anacapa Passage, California",
            "title": "CA_ANACAPA_01, north of Anacapa Island, about 45 m deep",
            "note": "Parallel ledges of bedrock curving across the whole tile. A US Geological Survey report describes ridges of Monterey Formation rock of this kind in the passage. Most of the 32 California ridges that passed the filters are here.",
            "img": encode_preview_jpeg(PREV / "TOP_1_CA_ANACAPA_01.png"),
        },
        {
            "btn": "4. A ship off Key West",
            "title": "FL_KEYS_04, Florida Keys, about 48 m deep",
            "note": "A sunken ship about 60 m long. It lies inside a fish haven marked on the nautical chart, which the program's chart filter failed to apply. It is probably one of the vessels of the Key West Tournament Reef, not the one first named.",
            "img": encode_preview_jpeg(PREV / "TOP_3_FL_KEYS_04.png"),
        },
        {
            "btn": "5. Block Island Sound",
            "title": "NE_BLOCK_10, Block Island Sound, about 28 m deep",
            "note": "A low bar about 110 m long among curved bedforms. Labelled a tidal sandbar in the first report; that reading is likely and was not checked against a sediment map.",
            "img": encode_preview_jpeg(PREV / "TOP_7_NE_BLOCK_10.png"),
        },
        {
            "btn": "6. New York Bight",
            "title": "NY_HUDSON_02, off New York, about 32 m deep",
            "note": "Pitted, hummocky ground inside the charted spoil ground of the former Mud Dump Site, where dredged material was dumped and later capped.",
            "img": encode_preview_jpeg(PREV / "AUDIT_NY_HUDSON_02.png"),
        },
    ]
    data_json = json.dumps(slides)
    btns_html = "\n".join(
        f'  <button type="button" class="dw-g-btn{" is-on" if i == 0 else ""}" data-idx="{i}" '
        f'style="font-size:11.5px;padding:4px 8px;border:1px solid var(--rule);border-radius:4px;'
        f'background:{"var(--copper)" if i == 0 else "transparent"};color:{"#fff" if i == 0 else "var(--ink)"};cursor:pointer">'
        f'{esc(sl["btn"])}</button>'
        for i, sl in enumerate(slides)
    )
    html_out = f"""<figure class="fig" aria-label="Interactive 2 m NOAA multibeam sonar shaded-relief and BPI visual audit gallery">
<div class="fig-controls" style="display:flex;flex-wrap:wrap;gap:5px;margin-bottom:10px;align-items:center">
  <span style="font-size:12px;color:var(--muted);margin-right:2px">Sonar tile:</span>
{btns_html}
</div>
<div style="border:1px solid var(--rule);border-radius:6px;overflow:hidden;background:#0f172a">
  <img id="dw-g-img" src="{slides[0]['img']}" alt="{esc(slides[0]['title'])}" style="display:block;width:100%;height:auto" />
  <div style="padding:10px 12px;background:var(--paper);border-top:1px solid var(--rule)">
    <div id="dw-g-title" style="font-size:12.5px;font-weight:700;color:var(--ink);margin-bottom:3px">{esc(slides[0]['title'])}</div>
    <div id="dw-g-note" style="font-size:11.5px;color:var(--muted)">{esc(slides[0]['note'])}</div>
  </div>
</div>
<figcaption><strong>Seabed tiles from NOAA&rsquo;s survey grids, as shaded relief (left) and local height (right).</strong> Yellow lines are ridges the detector kept; cyan lines are ridges its filters removed. These six previews, and no close-ups of single ridges, are what the first run produced; ten of the 39 ridges it called natural or modern are in tiles it never drew.</figcaption>
<script>
(function(){{
  var SLIDES = {data_json};
  var img = document.getElementById("dw-g-img");
  var title = document.getElementById("dw-g-title");
  var note = document.getElementById("dw-g-note");
  var btns = document.querySelectorAll(".dw-g-btn");
  btns.forEach(function(b){{
    b.addEventListener("click", function(){{
      var i = parseInt(b.getAttribute("data-idx"), 10);
      var s = SLIDES[i];
      btns.forEach(function(x){{ x.classList.remove("is-on"); x.style.background = "transparent"; x.style.color = "var(--ink)"; }});
      b.classList.add("is-on"); b.style.background = "var(--copper)"; b.style.color = "#fff";
      img.src = s.img;
      img.alt = s.title;
      title.textContent = s.title;
      note.textContent = s.note;
    }});
  }});
}})();
</script>
</figure>
"""
    (OUT / "sonar_gallery.html").write_text(html_out, encoding="utf-8")


def make_pipeline_funnel(s: dict) -> None:
    ov = s["search_overview"]
    funnel = [
        {"lbl": "Raw linear ridges (L ≥ 60 m, lin ≥ 0.90, BPI ≥ 0.35 m)", "n": ov["n_candidates_total"], "col": "#64748b"},
        {"lbl": "Rejected: Step seams / periodic sandwaves / ENC charted", "n": ov["n_candidates_total"] - ov["n_unmasked_total"], "col": "#94a3b8"},
        {"lbl": "Surviving automated filters (entering visual hillshade audit)", "n": ov["n_unmasked_total"], "col": "var(--teal)"},
        {"lbl": "Visual audit: CA Santarosae dipping Miocene bedrock strata", "n": 32, "col": "#475569"},
        {"lbl": "Visual audit: NE tidal sandbars (3) + NY dredge mounds (3)", "n": 6, "col": "#475569"},
        {"lbl": "Visual audit: FL Key West 60 m sunken steel ship (modern wreck)", "n": 1, "col": "var(--copper)"},
        {"lbl": "Unmapped prehistoric stone walls, corners, or ring enclosures", "n": 0, "col": "var(--copper)"},
    ]
    regs = [
        {"reg": k, "area": v["valid_area_km2"], "tiles": v["n_tiles"], "raw": v["n_cand_total"], "unm": v["n_unmasked"]}
        for k, v in ov["by_region"].items()
    ]
    payload = {"funnel": funnel, "regs": regs}
    data_json = json.dumps(payload)
    html_out = f"""<figure class="fig" aria-label="Automated filtering and visual audit funnel across 40 NOAA 2 m sonar tiles">
<div class="fig-controls" style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px;align-items:center">
  <span style="font-size:12px;color:var(--muted);margin-right:4px">View:</span>
  <button type="button" class="dw-f-btn is-on" data-k="funnel" style="font-size:12px;padding:4px 9px;border:1px solid var(--rule);border-radius:4px;background:var(--copper);color:#fff;cursor:pointer">Detection &amp; Visual Audit Funnel (72 &rarr; 0)</button>
  <button type="button" class="dw-f-btn" data-k="regions" style="font-size:12px;padding:4px 9px;border:1px solid var(--rule);border-radius:4px;background:transparent;color:var(--ink);cursor:pointer">4 Drowned Ice Age Shelves (34.2 km&sup2;)</button>
</div>
<div class="fig-scroll">
<svg id="dw-f-svg" class="chart" viewBox="0 0 720 325" role="img" aria-label="Anomaly funnel and regional seafloor coverage" xmlns="http://www.w3.org/2000/svg"></svg>
</div>
<figcaption><strong>From 72 ridges to none unexplained.</strong> The detector marked 72 straight ridges in 34 km&sup2; of seabed. Its filters removed 33. The remaining 39 were labelled by region: bedrock ledges off California, bedforms in Block Island Sound, dumped dredge spoil off New York, and a sunken ship off Key West that the nautical chart already marks. No corners and no rings were found. The detector sees continuous ridges at least half a metre high and about four metres wide; a wall like the one known from the Baltic would be too slight for it.</figcaption>
<script>
(function(){{
  var D = {data_json};
  var svg = document.getElementById("dw-f-svg");
  var btns = document.querySelectorAll(".dw-f-btn");
  function el(tag, attrs, txt){{
    var n = document.createElementNS("http://www.w3.org/2000/svg", tag);
    for (var k in attrs) n.setAttribute(k, attrs[k]);
    if (txt !== undefined) n.textContent = txt;
    return n;
  }}
  function draw(k){{
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    if (k === "funnel") {{
      var L = 345, R = 675, T = 34, B = 284;
      function sx(v){{ return L + (v / 80) * (R - L); }}
      svg.appendChild(el("text", {{x: 16, y: 19, "font-size": 12, "font-weight": 600, fill: "var(--ink)"}}, "Candidate classification funnel across 40 Ice Age paleo-shoreline tiles (34.23 km²)"));
      svg.appendChild(el("line", {{x1: L, x2: R, y1: B, y2: B, stroke: "var(--rule)"}}));
      svg.appendChild(el("line", {{x1: L, x2: L, y1: T, y2: B, stroke: "var(--rule)"}}));
      [0, 20, 40, 60, 80].forEach(function(v){{
        var x = sx(v);
        svg.appendChild(el("text", {{x: x, y: B + 15, "text-anchor": "middle", "font-size": 9.5, fill: "var(--muted)"}}, String(v)));
      }});
      var step = (B - T) / D.funnel.length;
      D.funnel.forEach(function(f, i){{
        var y = T + i * step + 6, h = step - 12;
        var isLast = (i === D.funnel.length - 1);
        svg.appendChild(el("text", {{x: L - 8, y: y + h * 0.7, "text-anchor": "end", "font-size": 10.2, "font-weight": isLast ? 700 : 400, fill: isLast ? "var(--copper)" : "var(--ink)"}}, f.lbl));
        var w = f.n === 0 ? 3 : Math.max(4, sx(f.n) - L);
        svg.appendChild(el("rect", {{x: L, y: y, width: w, height: h, rx: 2.5, fill: f.col, opacity: f.n === 0 ? 0.35 : 0.88}}));
        svg.appendChild(el("text", {{x: L + w + 6, y: y + h * 0.7, "font-size": 10.5, "font-weight": 700, fill: f.col}}, String(f.n)));
      }});
      svg.appendChild(el("text", {{x: (L + R) / 2, y: 315, "text-anchor": "middle", "font-size": 10.2, fill: "var(--muted)"}}, "Rectilinear corners (75°–105°): 0  ·  Closed ring enclosures (25–200 m): 0"));
    }} else {{
      var L = 215, R = 670, T = 40, B = 265;
      function sx(v){{ return L + (v / 14) * (R - L); }}
      svg.appendChild(el("text", {{x: 16, y: 20, "font-size": 12, "font-weight": 600, fill: "var(--ink)"}}, "Valid 2 m multibeam seafloor area scanned per Ice Age shelf region (km²)"));
      svg.appendChild(el("line", {{x1: L, x2: R, y1: B, y2: B, stroke: "var(--rule)"}}));
      svg.appendChild(el("line", {{x1: L, x2: L, y1: T, y2: B, stroke: "var(--rule)"}}));
      [0, 3, 6, 9, 12].forEach(function(v){{
        var x = sx(v);
        svg.appendChild(el("text", {{x: x, y: B + 15, "text-anchor": "middle", "font-size": 9.5, fill: "var(--muted)"}}, v + " km²"));
      }});
      var step = (B - T) / D.regs.length;
      D.regs.forEach(function(r, i){{
        var y = T + i * step + 10, h = step - 20;
        svg.appendChild(el("text", {{x: L - 8, y: y + h * 0.65, "text-anchor": "end", "font-size": 10.8, fill: "var(--ink)"}}, r.reg));
        var w = Math.max(4, sx(r.area) - L);
        svg.appendChild(el("rect", {{x: L, y: y, width: w, height: h, rx: 3, fill: "var(--teal)", opacity: 0.85}}));
        svg.appendChild(el("text", {{x: L + w + 6, y: y + h * 0.65, "font-size": 10.2, fill: "var(--ink)"}}, r.area.toFixed(2) + " km² (" + r.tiles + " tiles · " + r.unm + " unmasked → 0 walls)"));
      }});
      svg.appendChild(el("text", {{x: (L + R) / 2, y: 306, "text-anchor": "middle", "font-size": 10.2, fill: "var(--muted)"}}, "Total valid 2 m multibeam coverage: 34.23 km² across 40 pre-registered tiles (depth −10 m to −80 m)"));
    }}
  }}
  btns.forEach(function(b){{
    b.addEventListener("click", function(){{
      btns.forEach(function(x){{ x.classList.remove("is-on"); x.style.background = "transparent"; x.style.color = "var(--ink)"; }});
      b.classList.add("is-on"); b.style.background = "var(--copper)"; b.style.color = "#fff";
      draw(b.getAttribute("data-k"));
    }});
  }});
  draw("funnel");
}})();
</script>
</figure>
"""
    (OUT / "pipeline_funnel.html").write_text(html_out, encoding="utf-8")


def main() -> None:
    s = json.loads((RES / "drowned_walls_summary.json").read_text(encoding="utf-8"))
    make_tiles(s)
    make_sonar_gallery()
    make_pipeline_funnel(s)
    print(f"Wrote 3 figures to {OUT}")


if __name__ == "__main__":
    main()
