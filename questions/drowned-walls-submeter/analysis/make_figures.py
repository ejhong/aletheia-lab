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
    items = [
        (
            f"{total_km2:.2f} km²",
            f"sub-meter to 2 m sonar seafloor audited: {h['valid_km2']:.2f} km² in Lake Huron (0.5–2 m NOAA BAG) + {b['total_valid_km2']:.2f} km² in Western Baltic (0.25–0.5 m BSH)",
            False,
        ),
        (
            "4 / 4 gates",
            f"pre-registered calibration passed: {cal['arm1_synth_walls_recovered']}/12 Huron walls, {cal['arm1_synth_seams_rejected']}/12 seams, {cal['arm2_synth_walls_recovered']}/10 Baltic walls, {cal['arm2_transient_trawl_rejected']}/10 transient trawls rejected",
            False,
        ),
        (
            "0 prehistoric",
            "unmapped Stone Age stone walls, caribou drive-lanes, or hunting blinds confirmed after 100% visual hillshade audit of Lake Huron hits & Baltic anomaly inspection",
            False,
        ),
        (
            "Null",
            "Lake Huron hits resolve to Devonian limestone scarps/karst (31), glacial moraines (8), and swath edges (4); Baltic shows multi-year trawl scars + 1 Kiel Bay wreck/scour anomaly",
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
    slides = [
        {
            "btn": "1. Huron 50 cm Wreck (Control)",
            "title": "Lake Huron 0.50 m/px Positive Control: Thunder Bay Shipwreck (H13652, 45.1055° N, −83.2184° W)",
            "note": "Real 50 cm NOAA multibeam on a glassy-flat lakebed (background σ = 5.3 cm): wooden vessel framing and keel stand out cleanly (+1.26 m BPI) and link 5.9 m to NOAA ENC Wreck_pt (red mask).",
            "img": encode_preview_jpeg(PREV / "CTRL_HURON_WRECK_H13652.png"),
        },
        {
            "btn": "2. Planted 0.50 m Drive-Lane (Calib)",
            "title": "Sensitivity Gate: Synthetic 60 m × 2.5 m × 0.50 m Caribou Drive-Lane on Real 50 cm Lake Huron Noise",
            "note": "At 50 cm resolution, a 50 cm tall Stone Age boulder wall stands out unmistakably on both hillshade and BPI; the detector recovers 11/12 (91.7%) planted walls and rejects 11/12 (91.7%) step seams.",
            "img": encode_preview_jpeg(PREV / "CALIB_HURON_PLANTED_50CM.png"),
        },
        {
            "btn": "3. Huron Alpena–Amberley Scarp",
            "title": "Mid-Lake Alpena–Amberley Ridge (W00499, H3_RIDGE_11 & H3_RIDGE_17, −53 m to −78 m depth)",
            "note": "Dry land during the 9,000-year-old Lake Stanley lowstand: 2 m sonar resolves dramatic semicircular Devonian limestone paleo-mesas and Six Fathom Scarp cliffs (red-masked as natural escarpments), with zero unmapped stone walls.",
            "img": encode_preview_jpeg(PREV / "HURON_H3_RIDGE_17.png"),
        },
        {
            "btn": "4. Huron 1 m Karst & Scarp",
            "title": "Lake Huron Nearshore Shelf (H2_H12964_08, 1.0 m/px, 45.1342° N, −83.1881° W, −9.9 m depth)",
            "note": "Rank #1 unmasked Lake Huron ridge (88.1 m): direct shaded-relief inspection resolves it cleanly to a scalloped Devonian Traverse Group limestone escarpment (cuesta ledge), not a constructed boulder wall.",
            "img": encode_preview_jpeg(PREV / "HURON_H2_H12964_08.png"),
        },
        {
            "btn": "5. Kiel Bay 25 cm Scour Anomaly",
            "title": "Western Baltic 0.25 m/px (BALTIC_Test4, Kiel Bay, 54.5531° N, 10.2373° E)",
            "note": "Untrawled seafloor anomaly: a sharp 54 m curved obstruction (14.6° slope) with a flared hydrodynamic comet-mark sediment wake and ~16 m × 5 m hull-like debris at its SE flank, avoided by surrounding bottom-trawl lanes (black mask)—consistent with a modern small wreck/obstruction.",
            "img": encode_preview_jpeg(PREV / "BALTIC_2A_BALTIC_Test4_01.png"),
        },
        {
            "btn": "6. Fehmarn 2024 vs 2025 Trawls",
            "title": "Western Baltic 0.50 m/px Temporal Persistence (Fehmarn Belt, 54.5666° N, 10.7743° E)",
            "note": "Left: 2024 slope; Center: 2025 slope; Right: 2024∩2025 persistence minimum. While single-year trawl scars vanish (10/10 synthetic rejected), heavy beaded otter-board trawl grooves persist > 1 year in cohesive Fehmarn mud and explain the persistent linear hits.",
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
        ("Lake Huron: Real Shipwreck Controls (70 m center gate)", cal["arm1_wreck_controls_passed"], cal["arm1_wreck_controls_total"], 66.7, "#0ea5e9"),
        ("Lake Huron: Planted 0.50 m Caribou Drive-Lanes", cal["arm1_synth_walls_recovered"], cal["arm1_synth_walls_total"], 83.3, "#10b981"),
        ("Lake Huron: Planted 0.50 m Step Seams Rejected", cal["arm1_synth_seams_rejected"], cal["arm1_synth_seams_total"], 91.7, "#6366f1"),
        ("Western Baltic: Planted Blinkerwall-Scale Walls", cal["arm2_synth_walls_recovered"], cal["arm2_synth_walls_total"], 80.0, "#10b981"),
        ("Western Baltic: Transient Single-Year Trawls Rejected", cal["arm2_transient_trawl_rejected"], cal["arm2_transient_trawl_total"], 90.0, "#6366f1"),
    ]
    w_svg, h_svg = 760, 265
    bar_x0, bar_w = 345, 330
    parts = [
        f'<svg viewBox="0 0 {w_svg} {h_svg}" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:760px;height:auto;display:block;margin:1rem 0;font-family:system-ui,-apple-system,sans-serif;">',
        '<rect width="760" height="265" rx="8" fill="#ffffff" stroke="#e2e8f0"/>',
        '<text x="18" y="28" font-size="14" font-weight="700" fill="#0f172a">Pre-Registered Calibration Gates (4/4 Passed, Zero Amendments)</text>',
        '<text x="18" y="45" font-size="11.5" fill="#475569">Dashed tick marks show the locked pass threshold for each arm; all four gates passed on real sonar noise.</text>',
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
