#!/usr/bin/env python3
"""Generate interactive HTML/SVG + real sub-meter sonar gallery figures for #143 (drowned-walls-submeter)."""
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
OUT = ROOT.parent.parent / "site" / "figures" / "drowned-walls-submeter"
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
    h = s["arm1_huron"]
    b = s["arm2_baltic"]
    total_km2 = h["valid_km2"] + b["total_valid_km2"]
    # Tiles 2 and 3 are spot-check numbers (spotcheck/out_controls_seams.json, out_sens_huron.json,
    # out_sens_baltic.json), not fields of scan_summary.json.
    items = [
        (
            f"{total_km2:.1f} km²",
            f"of lake and sea floor searched: {h['valid_km2']:.1f} km² of NOAA grids in western Lake Huron and {b['total_valid_km2']:.1f} km² of Baltic slope grids (the finest are 1 m surveys)",
            False,
        ),
        (
            "9 of 12",
            "planted false steps rejected by the filter the plan names, where it required 11. By the plan's own rule the result is inconclusive",
            False,
        ),
        (
            "1 in 569",
            "rows of stones like the Blinkerwall found when planted at random in the Lake Huron grids (none of 120 in the Baltic). A smooth bank half a metre high is found most of the time",
            False,
        ),
        (
            "Inconclusive",
            "no unexplained continuous bank of stone in these grids; the method cannot see a row of separate stones, and no known structure lies in the area searched",
            True,
        ),
    ]
    body = ['<div class="tiles">']
    for v, lbl, is_w in items:
        cls = "tile-value is-word" if is_w else "tile-value"
        body.append(f'<div class="tile"><p class="{cls}">{esc(v)}</p><p class="tile-label">{esc(lbl)}</p></div>')
    body.append("</div>\n")
    (OUT / "tiles.html").write_text("\n".join(body), encoding="utf-8")


def make_sonar_gallery() -> None:
    # Slides 2 and 5 use pictures made by no committed code (first run only); the published
    # sonar_gallery.html was patched by hand on 2026-11-27 with the texts below.
    slides = [
        {
            "btn": "1. A charted wreck",
            "title": "Lake Huron, Thunder Bay: a charted shipwreck in survey H13652 (45.1055° N, 83.2184° W)",
            "note": "A charted wreck in a 0.5 m NOAA grid. It stands about 1.3 m above its surroundings, and the detector marks it and links it to the chart (red). The 5.9 m in the first report is the distance from the centre of the tile, which was placed on the charted position, not from the wreck.",
            "img": encode_preview_jpeg(PREV / "CTRL_HURON_WRECK_H13652.png"),
        },
        {
            "btn": "2. Planted smooth wall",
            "title": "A smooth synthetic wall, 60 m × 2.5 m × 0.5 m, added to a real 0.5 m tile",
            "note": "An unbroken ridge, unlike any real structure: the real ones are rows of separate stones. The detector found 11 of 12 such walls on the quietest tiles. Rows of stones of the real sizes, planted in these grids, were found once in about 570 tries. This picture was made by code that is not in the repository.",
            "img": encode_preview_jpeg(PREV / "CALIB_HURON_PLANTED_50CM.png"),
        },
        {
            "btn": "3. Mid-lake Huron, 2 m grid",
            "title": "Mid-lake Lake Huron, survey W00499 (tiles H3_RIDGE_11 and H3_RIDGE_17, 53 to 78 m deep)",
            "note": "Ground that was dry land about 9,000 years ago, in a 2 m grid. The first report read the curved benches as limestone ledges; that reading was not checked against a geological map. Red marks ridges removed by filters, not ridges shown to be natural. At this grid size the detector finds only half of the plan's own planted walls.",
            "img": encode_preview_jpeg(PREV / "HURON_H3_RIDGE_17.png"),
        },
        {
            "btn": "4. Huron: the top-ranked ridge",
            "title": "Lake Huron, near shore (tile H2_H12964_08, 1 m grid, 45.1342° N, 83.1881° W, 9.9 m deep)",
            "note": "The highest-scoring ridge the filters kept (88 m long). The first report read it as a limestone ledge; that is a reading of this picture, not checked against a map.",
            "img": encode_preview_jpeg(PREV / "HURON_H2_H12964_08.png"),
        },
        {
            "btn": "5. Kiel Bay: a charted wreck",
            "title": "Kiel Bay, Baltic (Test4, 54.5531° N, 10.2373° E): a 1 m survey interpolated to 0.25 m",
            "note": "A 54 m ridge with a broad tail of disturbed seabed. Chart data (read through OpenStreetMap) show a submerged wreck 69 m away and foul ground 59 m away; the study checked no chart. Black areas are trawl marks masked out. This picture was made by code that is not in the repository.",
            "img": encode_preview_jpeg(PREV / "BALTIC_2A_BALTIC_Test4_01.png"),
        },
        {
            "btn": "6. Fehmarn: two years of trawl marks",
            "title": "Fehmarn Belt, Baltic, in 2024 and 2025 (54.5666° N, 10.7743° E)",
            "note": "Left 2024, centre 2025, right the smaller of the two. Trawl marks cover the sea floor and many last more than a year, so comparing the years does not clear them. The 67 lines kept here were all labelled trawl marks; 7 were looked at. The planted one-year marks vanish by construction, so that check tests nothing.",
            "img": encode_preview_jpeg(PREV / "BALTIC_2B_01_Fehmarn.png"),
        },
    ]

    btns = []
    panels = []
    for i, sl in enumerate(slides):
        active = " is-active" if i == 0 else ""
        btns.append(f'<button type="button" class="sg-btn{active}" data-idx="{i}">{esc(sl["btn"])}</button>')
        disp = "" if i == 0 else ' style="display:none"'
        panels.append(
            f'<div class="sg-panel" data-idx="{i}"{disp}>'
            f'<p class="sg-title">{esc(sl["title"])}</p>'
            f'<img src="{sl["img"]}" alt="{esc(sl["title"])}" loading="lazy">'
            f'<p class="sg-note">{esc(sl["note"])}</p>'
            f'</div>'
        )

    uid = "dws143_gallery"
    html_out = f"""<div class="sg-wrap" id="{uid}">
<style>
#{uid} {{ margin: 1.2rem 0 1.6rem; font-family: inherit; }}
#{uid} .sg-tabs {{ display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 10px; }}
#{uid} .sg-btn {{
  padding: 6px 10px; border: 1px solid #cbd5e1; background: #f8fafc; color: #1e293b;
  border-radius: 6px; font-size: 12.5px; cursor: pointer; font-weight: 500;
}}
#{uid} .sg-btn.is-active {{ background: #0f172a; color: #f8fafc; border-color: #0f172a; }}
#{uid} .sg-panel {{ border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; background: #ffffff; }}
#{uid} .sg-title {{ font-weight: 600; font-size: 14px; margin: 0 0 8px; color: #0f172a; }}
#{uid} .sg-panel img {{ width: 100%; height: auto; border-radius: 4px; display: block; }}
#{uid} .sg-note {{ font-size: 13px; color: #334155; margin: 8px 0 0; line-height: 1.45; }}
</style>
<div class="sg-tabs">{"".join(btns)}</div>
{"".join(panels)}
<script>
(function() {{
  var root = document.getElementById("{uid}");
  if (!root) return;
  var btns = root.querySelectorAll(".sg-btn");
  var panels = root.querySelectorAll(".sg-panel");
  btns.forEach(function(b) {{
    b.addEventListener("click", function() {{
      var idx = b.getAttribute("data-idx");
      btns.forEach(function(x) {{ x.classList.toggle("is-active", x.getAttribute("data-idx") === idx); }});
      panels.forEach(function(p) {{ p.style.display = p.getAttribute("data-idx") === idx ? "" : "none"; }});
    }});
  }});
}})();
</script>
</div>
"""
    (OUT / "sonar_gallery.html").write_text(html_out, encoding="utf-8")


def make_calibration_summary(s: dict, va: dict) -> None:
    cal = s["calibration"]
    rows = [
        ("Lake Huron: charted wrecks (program's own test)", cal["arm1_wreck_controls_passed"], cal["arm1_wreck_controls_total"], 66.7, "#0ea5e9"),
        ("Lake Huron: planted smooth walls, quietest tiles", cal["arm1_synth_walls_recovered"], cal["arm1_synth_walls_total"], 83.3, "#10b981"),
        ("Lake Huron: planted false steps not passed", cal["arm1_synth_seams_rejected"], cal["arm1_synth_seams_total"], 91.7, "#6366f1"),
        # as the plan words the check ("via SEAM_STEP"): spotcheck/out_controls_seams.json
        ("Lake Huron: false steps, as the plan words it", 9, 12, 91.7, "#dc2626"),
        ("Baltic: planted slope bumps (no height)", cal["arm2_synth_walls_recovered"], cal["arm2_synth_walls_total"], 80.0, "#10b981"),
        ("Baltic: one-year trawl marks (cannot fail)", cal["arm2_transient_trawl_rejected"], cal["arm2_transient_trawl_total"], 90.0, "#6366f1"),
    ]
    w_svg, h_svg = 760, 300
    bar_x0, bar_w = 345, 312
    parts = [
        f'<svg viewBox="0 0 {w_svg} {h_svg}" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:760px;height:auto;display:block;margin:1rem 0;font-family:system-ui,-apple-system,sans-serif;">',
        '<rect width="760" height="300" rx="8" fill="#ffffff" stroke="#e2e8f0"/>',
        '<text x="18" y="28" font-size="14" font-weight="700" fill="#0f172a">The plan&#39;s checks on the method: one fails as worded</text>',
        '<text x="18" y="45" font-size="11.5" fill="#475569">Dashed marks show the plan&#39;s pass line. As the plan words the false-step check, 9 of 12 fails.</text>',
    ]
    for idx, (lbl, num, den, gate_pct, col) in enumerate(rows):
        y = 72 + idx * 36
        pct = 100.0 * num / max(1, den)
        fw = bar_w * (pct / 100.0)
        gx = bar_x0 + bar_w * (gate_pct / 100.0)
        parts.append(f'<text x="18" y="{y + 14}" font-size="12" fill="#1e293b">{esc(lbl)}</text>')
        parts.append(f'<rect x="{bar_x0}" y="{y}" width="{bar_w}" height="20" rx="4" fill="#f1f5f9"/>')
        parts.append(f'<rect x="{bar_x0}" y="{y}" width="{fw:.1f}" height="20" rx="4" fill="{col}"/>')
        parts.append(f'<line x1="{gx:.1f}" y1="{y - 3}" x2="{gx:.1f}" y2="{y + 23}" stroke="#0f172a" stroke-width="1.6" stroke-dasharray="3,2"/>')
        parts.append(f'<text x="{bar_x0 + bar_w + 10}" y="{y + 14}" font-size="12" font-weight="600" fill="#0f172a">{num}/{den} ({pct:.0f}%)</text>')
    parts.append("</svg>")
    (OUT / "calibration_gates.html").write_text("\n".join(parts) + "\n", encoding="utf-8")


def main() -> None:
    s = json.loads((RES / "scan_summary.json").read_text(encoding="utf-8"))
    va = json.loads((RES / "visual_audit.json").read_text(encoding="utf-8"))
    make_tiles(s)
    make_sonar_gallery()
    make_calibration_summary(s, va)
    print("Generated figures in", OUT)


if __name__ == "__main__":
    main()
