#!/usr/bin/env python3
"""Generate 3 interactive inline SVG figures for site/content/yd-platinum-volcanism.md.

Standard library only.
Usage: python3 questions/yd-platinum-volcanism/analysis/make_figures.py
"""
from __future__ import annotations

import csv
import html
import json
import pathlib

Q = pathlib.Path(__file__).resolve().parent.parent
ROOT = Q.parent.parent
OUT = ROOT / "site" / "figures" / "yd-platinum-volcanism"
OUT.mkdir(parents=True, exist_ok=True)

S = json.load(open(Q / "results" / "summary.json", encoding="utf-8"))
esc = lambda s: html.escape(str(s), quote=True)


def figure(name: str, title: str, svg: str, caption: str, legend: str = "") -> None:
    (OUT / f"{name}.html").write_text(
        f'<figure class="fig" aria-label="{esc(title)}">\n'
        f'{legend}<div class="fig-scroll">\n{svg}\n</div>\n'
        f'<figcaption>{caption}</figcaption>\n</figure>\n',
        encoding="utf-8",
    )


def fig_stratigraphy() -> None:
    """Within-GISP2 depth stratigraphy (1720 -> 1707 m, oldest on left, youngest on right)
    showing d18O (Panel A) and SO4 + Ca2+ (Panel B) with Pt band, volcanic spikes, and changepoints.
    """
    d_lo, d_hi = 1707.0, 1720.0  # deeper (1720, older) on LEFT -> shallower (1707, younger) on RIGHT
    W, left, right = 720, 58, 688
    p1_top, p1_h = 46, 130
    p1_bot = p1_top + p1_h
    p2_top, p2_h = p1_bot + 54, 130
    p2_bot = p2_top + p2_h
    H = p2_bot + 44

    sx = lambda d: left + (d_hi - d) / (d_hi - d_lo) * (right - left)
    sy1 = lambda o: p1_top + (-37.0 - o) / (-37.0 - (-42.0)) * p1_h
    sy2 = lambda v: p2_bot - min(v, 700.0) / 700.0 * p2_h

    o = [
        f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" '
        f'aria-label="GISP2 ice-core depth stratigraphy around the platinum spike, cooling onset, dust jump, and volcanic sulfate spikes" '
        f'xmlns="http://www.w3.org/2000/svg">'
    ]

    # Platinum vertical band (1712.375 -> 1712.000 m) across both panels
    x_pt1, x_pt2 = sx(1712.375), sx(1712.000)
    o.append(f'<rect class="c-band" style="opacity:.22" x="{x_pt1:.1f}" y="{p1_top - 4}" width="{max(4.0, x_pt2 - x_pt1):.1f}" height="{p2_bot - p1_top + 4}"/>')
    o.append(f'<line class="c-ref" x1="{(x_pt1 + x_pt2)/2:.1f}" x2="{(x_pt1 + x_pt2)/2:.1f}" y1="{p1_top - 12}" y2="{p2_bot}"/>')
    o.append(f'<text class="c-label-sm" x="{(x_pt1 + x_pt2)/2:.1f}" y="{p1_top - 18}" text-anchor="middle" style="fill:var(--copper)">Pt spike (1712.375–1712.0 m · 12,870–12,858 b2k)</text>')

    # GS-1 onset line (~1713.2 m = 12,896 b2k)
    x_gs1 = sx(1713.2)
    o.append(f'<line class="c-onset" x1="{x_gs1:.1f}" x2="{x_gs1:.1f}" y1="{p1_top}" y2="{p2_bot}"/>')
    o.append(f'<text class="c-label-sm" x="{x_gs1 - 5:.1f}" y="{p1_top + 13}" text-anchor="end">GS-1 onset (12,896 b2k)</text>')

    # Main GISP2 Ca2+ / d18O step lines (~1710.8 m and 1709.9 m)
    x_step = sx(1710.81)
    o.append(f'<line class="c-path-open" x1="{x_step:.1f}" x2="{x_step:.1f}" y1="{p1_top}" y2="{p2_bot}"/>')
    o.append(f'<text class="c-sub" x="{x_step + 5:.1f}" y="{p1_top + 13}" text-anchor="start">GISP2 main cold/dust step (1710.8–1709.9 m)</text>')

    # Panel A: GISP2 20-yr d18O
    o.append(f'<text class="c-group" x="{left}" y="{p1_top - 30}">A · GISP2 TEMPERATURE PROXY (20-YR δ¹⁸O, ZERO TIMESCALE ERROR)</text>')
    for tk in (-37, -38, -39, -40, -41, -42):
        y = sy1(tk)
        o.append(f'<line class="c-grid" x1="{left}" x2="{right}" y1="{y:.1f}" y2="{y:.1f}"/>')
        o.append(f'<text class="c-tick" x="{left - 8}" y="{y + 4:.1f}" text-anchor="end">{tk}‰</text>')

    pts_o = [p for p in S["profiles_gisp2"]["d18o_20yr"] if d_lo <= p["depth_m"] <= d_hi]
    pts_o.sort(key=lambda p: -p["depth_m"])
    path_o = " L".join(f"{sx(p['depth_m']):.1f},{sy1(p['d18o']):.1f}" for p in pts_o)
    o.append(f'<path class="c-line" d="M{path_o}"/>')
    for p in pts_o:
        tip = esc(f"GISP2 {p['depth_m']:.2f} m (GICC05 {p['gicc05_b2k']:.0f} b2k)|δ¹⁸O = {p['d18o']:.2f} ‰")
        o.append(f'<g class="c-mark" tabindex="0" data-tip="{tip}"><circle class="c-dot" cx="{sx(p["depth_m"]):.1f}" cy="{sy1(p["d18o"]):.1f}" r="3.6"/></g>')

    # Panel B: GISP2 SO4 (bars) and Ca2+ dust (line)
    o.append(f'<text class="c-group" x="{left}" y="{p2_top - 12}">B · GISP2 VOLCANIC SULFATE (SO₄²⁻ BARS) &amp; DUST (Ca²⁺ LINE) IN THE SAME CORE</text>')
    for tk in (0, 200, 400, 600):
        y = sy2(tk)
        o.append(f'<line class="{"c-zero" if tk == 0 else "c-grid"}" x1="{left}" x2="{right}" y1="{y:.1f}" y2="{y:.1f}"/>')
        o.append(f'<text class="c-tick" x="{left - 8}" y="{y + 4:.1f}" text-anchor="end">{tk}</text>')
    o.append(f'<text class="c-sub" x="{right}" y="{p2_top - 12}" text-anchor="end">ppb (Mayewski et al. 1997)</text>')

    ions = [p for p in S["profiles_gisp2"]["ions"] if d_lo <= p["mid_m"] <= d_hi]
    ions.sort(key=lambda p: -p["mid_m"])
    for p in ions:
        if p["so4"] is None:
            continue
        x = sx(p["mid_m"])
        y = sy2(p["so4"])
        is_spk = p["so4"] > 236.9
        cls = "c-bar is-on" if is_spk else "c-bar"
        tip = esc(f"GISP2 {p['mid_m']:.2f} m|SO₄²⁻ = {p['so4']:.1f} ppb|Ca²⁺ = {p['ca']} ppb|NH₄⁺ = {p['nh4']} ppb")
        o.append(
            f'<g class="c-mark" tabindex="0" data-tip="{tip}">'
            f'<rect class="{cls}" x="{x - 2.0:.1f}" y="{y:.1f}" width="4.0" height="{max(1.0, p2_bot - y):.1f}"/>'
            f'</g>'
        )
    # Dust Ca2+ trace overlaid (scaled 2x so Ca2+ 20..250 ppb reads cleanly on 0..700 scale, or true ppb!)
    ca_pts = [(p["mid_m"], p["ca"]) for p in ions if p["ca"] is not None]
    path_ca = " L".join(f"{sx(d):.1f},{sy2(c):.1f}" for d, c in ca_pts)
    o.append(f'<path class="c-line-ctx" d="M{path_ca}"/>')

    # Label the three SO4 spikes
    o.append(f'<text class="c-label-sm" x="{sx(1718.7) + 5:.1f}" y="{sy2(649) + 10:.1f}">13,029 b2k (649 ppb)</text>')
    o.append(f'<text class="c-label-sm" x="{sx(1713.9) - 5:.1f}" y="{sy2(462) + 4:.1f}" text-anchor="end">12,917 b2k (462 ppb)</text>')
    o.append(f'<text class="c-label-sm" x="{sx(1708.65) - 5:.1f}" y="{sy2(394) + 4:.1f}" text-anchor="end">12,755 b2k (394 ppb)</text>')

    for d_tk in range(1720, 1706, -2):
        x = sx(float(d_tk))
        o.append(f'<text class="c-tick" x="{x:.1f}" y="{p2_bot + 16}" text-anchor="middle">{d_tk} m</text>')
    o.append(f'<text class="c-axis" x="{left}" y="{p2_bot + 35}">GISP2 ice depth (m) — deeper/older on left, shallower/younger on right · copper bars = SO₄²⁻ spikes &gt; 237 ppb · grey line = Ca²⁺ dust (ppb)</text>')
    o.append("</svg>")

    figure(
        "stratigraphy",
        "Within-GISP2 depth stratigraphy of platinum, temperature, dust, and volcanic sulfate",
        "\n".join(o),
        "Every curve comes from the exact same GISP2 ice core, plotted by depth (older on the left, younger on the right). "
        "Two giant volcanic sulfate spikes (13,029 and 12,917 b2k) precede the official GS-1 cooling onset (12,896 b2k, black line). "
        "Petaev et al.'s platinum spike (copper band, 1712.375–1712.000 m) arrives 18–32 years after GS-1 onset with no major GISP2 "
        "sulfate peak of its own, yet still sits 1.5–2.5 m deeper (older) than GISP2's steepest step into full stadial cold and dust (dashed line). Hover or focus points for details.",
    )


def fig_volcanism_51ka() -> None:
    """51,000-year bar charts (60-9 ka b2k) of 150-yr bipolar aerosol loading (Rank 3/284) and Greenland sulfate (Rank 12/338)."""
    gl_rows = []
    with open(Q / "results" / "volc_windows_150yr_gl.tsv", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            gl_rows.append({"k": int(r["k"]), "start": float(r["start_b2k"]), "end": float(r["end_b2k"]), "val": float(r["dep_kg_km2"]), "cnt": int(r["count"])})
    bi_rows = []
    with open(Q / "results" / "volc_windows_150yr_bi.tsv", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            bi_rows.append({"k": int(r["k"]), "start": float(r["start_b2k"]), "end": float(r["end_b2k"]), "val": float(r["aerosol_tg"]), "cnt": int(r["count"])})

    W, left, right = 720, 56, 688
    p1_top, p1_h = 26, 125
    p1_bot = p1_top + p1_h
    p2_top, p2_h = p1_bot + 54, 125
    p2_bot = p2_top + p2_h
    H = p2_bot + 42

    # Age axis: 60,000 (left) -> 9,000 (right)
    sx = lambda a: left + (60000.0 - a) / (60000.0 - 9000.0) * (right - left)
    sy1 = lambda v: p1_bot - min(v, 700.0) / 700.0 * p1_h
    sy2 = lambda v: p2_bot - min(v, 1100.0) / 1100.0 * p2_h

    o = [
        f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" '
        f'aria-label="51,000 years of bipolar and Greenland volcanic sulfate loading in 150-year windows" '
        f'xmlns="http://www.w3.org/2000/svg">'
    ]

    # Panel A: Bipolar aerosol loading (Tg)
    o.append(f'<text class="c-group" x="{left}" y="{p1_top - 10}">A · BIPOLAR STRATOSPHERIC AEROSOL LOADING (60–9 KA, 284 WINDOWS · PRE-YD = RANK 3 OF 284)</text>')
    # Shade synchronization gap 24.5-16.5 ka
    o.append(f'<rect class="c-area-ctx" x="{sx(24500):.1f}" y="{p1_top}" width="{sx(16500) - sx(24500):.1f}" height="{p1_h}"/>')
    o.append(f'<text class="c-sub" x="{sx(20500):.1f}" y="{p1_top + 64}" text-anchor="middle">no bipolar match (24.5–16.5 ka)</text>')
    for tk in (0, 200, 400, 600):
        y = sy1(tk)
        o.append(f'<line class="{"c-zero" if tk == 0 else "c-grid"}" x1="{left}" x2="{right}" y1="{y:.1f}" y2="{y:.1f}"/>')
        o.append(f'<text class="c-tick" x="{left - 8}" y="{y + 4:.1f}" text-anchor="end">{tk} Tg</text>')
    for r in bi_rows:
        if r["val"] <= 0:
            continue
        x = sx(r["end"])
        bw = max(2.2, sx(r["start"]) - sx(r["end"]))
        y = sy1(r["val"])
        is_k0 = (r["k"] == 0)
        cls = "c-bar is-on" if is_k0 else "c-bar"
        tip = esc(f"[{r['start']:,.0f}, {r['end']:,.0f}) b2k|Bipolar aerosol: {r['val']:.1f} Tg ({r['cnt']} eruptions)")
        o.append(f'<g class="c-mark" tabindex="0" data-tip="{tip}"><rect class="{cls}" x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{max(1.5, p1_bot - y):.1f}"/></g>')
    o.append(f'<text class="c-label-sm" x="{sx(13046) - 6:.1f}" y="{sy1(526.6) + 4:.1f}" text-anchor="end" style="fill:var(--copper)">Pre-YD quadruplet: 527 Tg (#3/284, 4 eruptions)</text>')

    # Panel B: Greenland sulfate deposition (kg/km2)
    o.append(f'<text class="c-group" x="{left}" y="{p2_top - 10}">B · GREENLAND VOLCANIC SULFATE DEPOSITION (60–9 KA, 338 WINDOWS · PRE-YD = RANK 12 OF 338)</text>')
    for tk in (0, 250, 500, 750, 1000):
        y = sy2(tk)
        o.append(f'<line class="{"c-zero" if tk == 0 else "c-grid"}" x1="{left}" x2="{right}" y1="{y:.1f}" y2="{y:.1f}"/>')
        o.append(f'<text class="c-tick" x="{left - 8}" y="{y + 4:.1f}" text-anchor="end">{tk}</text>')
    for r in gl_rows:
        if r["val"] <= 0:
            continue
        x = sx(r["end"])
        bw = max(1.8, sx(r["start"]) - sx(r["end"]))
        y = sy2(r["val"])
        is_k0 = (r["k"] == 0)
        cls = "c-bar is-on" if is_k0 else "c-bar"
        tip = esc(f"[{r['start']:,.0f}, {r['end']:,.0f}) b2k|Greenland sulfate: {r['val']:.1f} kg/km² ({r['cnt']} eruptions)")
        o.append(f'<g class="c-mark" tabindex="0" data-tip="{tip}"><rect class="{cls}" x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{max(1.0, p2_bot - y):.1f}"/></g>')
    o.append(f'<text class="c-label-sm" x="{sx(13046) - 6:.1f}" y="{sy2(595.9) - 2:.1f}" text-anchor="end" style="fill:var(--copper)">Pre-YD: 596 kg/km² (#12/338, top 3.6%)</text>')

    for a_tk in (60000, 50000, 40000, 30000, 20000, 12896, 10000):
        x = sx(a_tk)
        lab = "YD" if a_tk == 12896 else f"{a_tk // 1000} ka"
        o.append(f'<text class="c-tick" x="{x:.1f}" y="{p2_bot + 16}" text-anchor="middle">{lab}</text>')
    o.append(f'<text class="c-axis" x="{left}" y="{p2_bot + 35}">Age (ka b2k, non-overlapping 150-year windows from Lin et al. 2022) · copper = [12,896, 13,046) b2k pre-YD window</text>')
    o.append("</svg>")

    figure(
        "volcanism_51ka",
        "51,000 years of bipolar and Greenland volcanism highlighting the pre-Younger Dryas cluster",
        "\n".join(o),
        "Non-overlapping 150-year sums of volcanic aerosol loading from Lin et al. (2022) across 60–9 ka b2k. "
        "The 150 years immediately preceding the Younger Dryas onset (copper, [12,896, 13,046) b2k) rank 3rd of 284 windows "
        "in bipolar stratospheric aerosol loading (526.6 Tg across 4 eruptions—the highest count of bipolar eruptions in any window) "
        "and 12th of 338 in Greenland sulfate deposition (595.9 kg/km²). Hover any bar for values.",
    )


def fig_timeline() -> None:
    """Clean zoomed timeline (13,060 -> 12,730 b2k) aligning the 4 pre-YD bipolar eruptions, GS-1 onset, Pt spike, and GISP2 main step."""
    W, left, right, top, h = 720, 48, 688, 36, 170
    bot = top + h
    H = bot + 44
    a_lo, a_hi = 12730.0, 13060.0  # older (13,060) on left -> younger (12,730) on right
    sx = lambda a: left + (a_hi - a) / (a_hi - a_lo) * (right - left)
    sy = lambda tg: bot - (tg / 250.0) * h

    o = [
        f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" '
        f'aria-label="Zoomed timeline from 13,060 to 12,730 b2k showing the volcanic quadruplet, GS-1 onset, platinum spike, and GISP2 cold step" '
        f'xmlns="http://www.w3.org/2000/svg">'
    ]
    o.append(f'<text class="c-group" x="{left}" y="{top - 14}">EVENT SEQUENCE ON GICC05 (13,060 → 12,730 B2K): VOLCANIC QUADRUPLET → COOLING ONSET → PLATINUM → MAIN COLD STEP</text>')
    for tk in (0, 50, 100, 150, 200, 250):
        y = sy(tk)
        o.append(f'<line class="{"c-zero" if tk == 0 else "c-grid"}" x1="{left}" x2="{right}" y1="{y:.1f}" y2="{y:.1f}"/>')
        o.append(f'<text class="c-tick" x="{left - 8}" y="{y + 4:.1f}" text-anchor="end">{tk}</text>')
    o.append(f'<text class="c-sub" x="{right}" y="{top - 14}" text-anchor="end">bipolar aerosol (Tg)</text>')

    # Shaded Pt interval on Svensson 2020 (12,869.9 -> 12,858.3 b2k)
    o.append(f'<rect class="c-band" style="opacity:.25" x="{sx(12869.9):.1f}" y="{top}" width="{sx(12858.3) - sx(12869.9):.1f}" height="{h}"/>')
    o.append(f'<line class="c-ref" x1="{sx(12864.1):.1f}" x2="{sx(12864.1):.1f}" y1="{top}" y2="{bot}"/>')
    o.append(f'<text class="c-label-sm" x="{sx(12864.1) + 5:.1f}" y="{top + 48}" style="fill:var(--copper)">Pt peak: 12,864 b2k (+32 yr after onset)</text>')

    # GS-1 onset line (12,896 b2k)
    o.append(f'<line class="c-onset" x1="{sx(12896.0):.1f}" x2="{sx(12896.0):.1f}" y1="{top}" y2="{bot}"/>')
    o.append(f'<text class="c-label-sm" x="{sx(12896.0) + 5:.1f}" y="{top + 14}">GS-1 onset (12,896 b2k)</text>')

    # GISP2 main cold/dust step (~12,822-12,794 b2k)
    o.append(f'<line class="c-path-open" x1="{sx(12822.0):.1f}" x2="{sx(12822.0):.1f}" y1="{top}" y2="{bot}"/>')
    o.append(f'<text class="c-sub" x="{sx(12822.0) + 5:.1f}" y="{top + 82}">GISP2 main cold/dust step (~12,822–12,794)</text>')

    # Bipolar eruptions
    for e in S["part2_volcanism"]["eruptions_around_yd_bi"]:
        age = float(e["age_b2k"])
        tg = float(e["aerosol_tg"])
        if not (a_lo <= age <= a_hi):
            continue
        x = sx(age)
        y = sy(tg)
        tip = esc(f"Bipolar eruption at {age:.1f} b2k|Aerosol loading: {tg:.1f} Tg|Forcing: {e['forcing_wm2']:.1f} W/m²|Source latitude: {e['site_pred']}")
        o.append(
            f'<g class="c-mark" tabindex="0" data-tip="{tip}">'
            f'<rect class="c-bar is-on" x="{x - 4:.1f}" y="{y:.1f}" width="8" height="{bot - y:.1f}" rx="1.5"/>'
            f'<text class="c-tick" x="{x:.1f}" y="{y - 5:.1f}" text-anchor="middle">{tg:.0f} Tg</text>'
            f'</g>'
        )

    for a_tk in (13050, 13000, 12950, 12900, 12850, 12800, 12750):
        o.append(f'<text class="c-tick" x="{sx(float(a_tk)):.1f}" y="{bot + 16}" text-anchor="middle">{a_tk:,}</text>')
    o.append(f'<text class="c-axis" x="{left}" y="{bot + 35}">GICC05 age (years b2k, older on left) · bars = bipolar eruptions (Lin et al. 2022) · copper band = GISP2 Pt spike on Svensson et al. (2020)</text>')
    o.append("</svg>")

    figure(
        "timeline",
        "Event sequence from 13,060 to 12,730 b2k on GICC05",
        "\n".join(o),
        "Chronological alignment on GICC05. Four bipolar eruptions strike between 13,028 and 12,917 b2k (culminating in a 201 Tg "
        "Northern Hemisphere high-latitude eruption 21 years before GS-1 onset). Cooling begins at 12,896 b2k; the GISP2 platinum "
        "spike follows 26–32 years later (12,870–12,858 b2k); and GISP2's steepest cold and dust steps arrive another 40–70 years later.",
    )


if __name__ == "__main__":
    fig_stratigraphy()
    fig_volcanism_51ka()
    fig_timeline()
    print(f"wrote 3 figures to {OUT}")
