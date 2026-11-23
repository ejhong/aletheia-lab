#!/usr/bin/env python3
"""Draw the inline SVG figures for site/content/yd-global-burn.md from results/ and explore/post_check.json.

Standard library only.
Usage (from repo root or questions/yd-global-burn/):
    python3 questions/yd-global-burn/analysis/make_figures.py
"""
from __future__ import annotations

import csv
import html
import json
import math
import pathlib

Q = pathlib.Path(__file__).resolve().parent.parent
ROOT = Q.parent.parent
OUT = ROOT / "site" / "figures" / "yd-global-burn"
OUT.mkdir(parents=True, exist_ok=True)

S = json.load(open(Q / "results" / "summary.json", encoding="utf-8"))
POST = json.load(open(Q / "explore" / "post_check.json", encoding="utf-8"))
esc = lambda s: html.escape(str(s), quote=True)


def figure(name: str, title: str, svg: str, caption: str, legend: str = "") -> None:
    (OUT / f"{name}.html").write_text(
        f'<figure class="fig" aria-label="{esc(title)}">\n'
        f'{legend}<div class="fig-scroll">\n{svg}\n</div>\n'
        f'<figcaption>{caption}</figcaption>\n</figure>\n',
        encoding="utf-8",
    )


def key_dot(text: str, hollow: bool = False, ctx: bool = False) -> str:
    cls = "k-dot"
    if hollow:
        cls += " k-hollow"
    if ctx:
        cls += " c-ctx"
    return (
        f'<span class="key"><svg viewBox="0 0 12 12" width="12" height="12" aria-hidden="true">'
        f'<circle class="{cls}" cx="6" cy="6" r="{3.8 if hollow else 4.5}"/></svg> {esc(text)}</span>'
    )


def fig_ranks() -> None:
    """Percentile rank dot-strip across Archive A, Archive B (primary), and the coarse-core contrast."""
    rows = [
        ("ARCHIVE A · GLOBAL ATMOSPHERE (ANTARCTIC ICE)", None),
        ("Taylor Glacier CO₂ × δ¹³C (TG_BURN)", S["archive_a"]["TG_BURN"], "primary", "0.488 ppm·‰"),
        ("WAIS Divide CO₂ rise (WAIS_CO2)", S["archive_a"]["WAIS_CO2"], "primary", "+4.52 ppm"),
        ("Eggleston 155 kyr δ¹³C (EGG_D13C)", S["archive_a"]["EGG_D13C"], "primary", "0.030 ‰"),
        ("ARCHIVE B · GLOBAL CHARCOAL (TIER C1, 19 HIGH-RES WELL-DATED SITES)", None),
        ("Composite local excess (E_mean)", S["archive_b_primary_13_5ka"]["C1"]["E_mean"], "primary", "0.000 SD"),
        ("Sites ≥ +1.0 SD (F_peak)", S["archive_b_primary_13_5ka"]["C1"]["F_peak"], "primary", "1 / 19 (5.3%)"),
        ("Peak 100-yr excess (E_100)", S["archive_b_primary_13_5ka"]["C1"]["E_100"], "primary", "+0.184 SD"),
        ("RESOLUTION CHECK · HIGH-RES VS. COARSE CHARCOAL CORES (≥ +1.5 SD)", None),
        ("High-res sites ≥ +1.5 SD (Tier C2, n=26)", S["archive_b_primary_13_5ka"]["C2"]["F_peak_15"], "ctx", "0 / 26 (0.0%)"),
        ("Coarse cores ≥ +1.5 SD (C3_coarse, n=43)", S["archive_b_primary_13_5ka"]["C3_coarse"]["F_peak_15"], "ctx", "5 / 41 (12.2%)"),
    ]

    W, label_w, left, right, top = 720, 260, 270, 610, 22
    row_h, hdr_h = 26, 26
    y = top
    layout = []
    for item in rows:
        if item[1] is None:
            y += 10 if layout else 0
            layout.append(("hdr", y, item[0]))
            y += hdr_h
        else:
            layout.append(("row", y, item[0], item[1], item[2], item[3]))
            y += row_h
    bottom = y + 8
    H = bottom + 40

    # x-axis: percentile from 0% (bottom / lowest) on left to 100% (Rank 1 / top) on right
    sx = lambda pct: left + (pct / 100.0) * (right - left)
    x_95 = sx(95.0)
    x_99 = sx(99.0)

    o = [
        f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" '
        f'aria-label="Percentile rank of the 12,800-year Younger Dryas window across all pre-registered measures" '
        f'xmlns="http://www.w3.org/2000/svg">'
    ]
    # Shaded top-5% zone
    o.append(f'<rect class="c-band" x="{x_95:.1f}" y="{top}" width="{right - x_95:.1f}" height="{bottom - top}"/>')
    for pct, lab in ((0, "lowest"), (25, "25th"), (50, "median"), (75, "75th"), (95, "top 5%"), (100, "rank 1")):
        x = sx(pct)
        cls = "c-ref" if pct == 95 else ("c-zero" if pct == 50 else "c-grid")
        o.append(f'<line class="{cls}" x1="{x:.1f}" x2="{x:.1f}" y1="{top}" y2="{bottom}"/>')
        o.append(f'<text class="c-tick" x="{x:.1f}" y="{bottom + 15}" text-anchor="middle">{lab}</text>')
    o.append(
        f'<text class="c-axis" x="{left}" y="{bottom + 33}">'
        f'Position of [12,650, 12,950) cal BP among all 300-year comparison windows (right = stronger burning signal)</text>'
    )

    for entry in layout:
        if entry[0] == "hdr":
            _, yy, title = entry
            o.append(f'<text class="c-group" x="0" y="{yy + 15}">{esc(title)}</text>')
        else:
            _, yy, label, rec, kind, val_txt = entry
            cy = yy + row_h / 2
            rank = rec["rank"]
            n = rec["n_usable"]
            # Upper-tail percentile: rank 1 of N -> 100*(1 - 0/N) = 100; rank N -> 100*(1 - (N-1)/N)
            pct = 100.0 * (1.0 - (rank - 1) / max(1, n - 1)) if n > 1 else 50.0
            cx = sx(pct)
            met = bool(rec["in_top5"])
            rank_txt = f"rank {rank}/{n}"
            tip = esc(
                f"{label}|Value: {val_txt}|Rank {rank} of {n} usable windows"
                f" (top-5% cutoff: ≤ {rec['top5_cut']}; {'MET' if met else 'not met'})"
            )
            dot_cls = "c-dot" if kind == "primary" else "c-dot c-ctx"
            if kind == "primary" and not met:
                dot_cls = "c-dot c-hollow"
            o.append(
                f'<g class="c-mark" tabindex="0" data-tip="{tip}">'
                f'<rect class="c-hit" x="0" y="{yy}" width="{W}" height="{row_h}"/>'
                f'<text class="{"c-label-sm" if kind == "primary" else "c-sub"}" x="0" y="{cy + 4:.1f}">{esc(label)}</text>'
                f'<line class="c-grid" x1="{left}" x2="{right}" y1="{cy:.1f}" y2="{cy:.1f}"/>'
                f'<circle class="{dot_cls}" cx="{cx:.1f}" cy="{cy:.1f}" r="{5 if kind == "primary" else 4.2}"/>'
                f'<text class="c-value" style="font-size:11.5px" x="{right + 10}" y="{cy + 4:.1f}">{esc(rank_txt)}</text>'
                f'</g>'
            )
    o.append("</svg>")

    legend = (
        f'<p class="fig-legend">'
        f'{key_dot("Primary measure hitting top 5% (only EGG_D13C)")}'
        f'{key_dot("Primary measure missing top 5%", hollow=True)}'
        f'{key_dot("Resolution-artifact check (high-res vs. coarse)", ctx=True)}'
        f'</p>\n'
    )
    figure(
        "ranks",
        "Pre-registered ranks across global atmosphere and charcoal",
        "\n".join(o),
        "Every pre-registered measure scored for the 300-year Younger Dryas onset window [12,650, 12,950) cal BP. "
        "Only one of six primary measures (Eggleston 155 kyr δ¹³C-CO₂) enters the shaded top-5% zone, and high-resolution "
        "global charcoal sits near the middle or bottom of 13,500 years. Bottom two rows show the resolution artifact: "
        "0 of 26 high-resolution charcoal cores exceed +1.5 SD, versus 5 of 41 coarse cores (rank 2/45). Hover or focus a row for details.",
        legend,
    )


def fig_atmosphere() -> None:
    """Two-panel figure: top-8 TG_BURN windows (HS1, mid-YD, HS4 triplet) + raw Taylor Glacier YD trace."""
    W = 720
    # Panel 1: Horizontal bar chart of Top 8 TG_BURN windows
    top8 = S["archive_a"]["TG_BURN"]["top10"][:8]
    labels = {
        11: "15,950–16,250 BP · Heinrich Stadial 1",
        -1: "12,350–12,650 BP · Mid-Younger Dryas (k = −1)",
        90: "39,650–39,950 BP · Heinrich Stadial 4",
        12: "16,250–16,550 BP · Heinrich Stadial 1",
        14: "16,850–17,150 BP · Heinrich Stadial 1",
        89: "39,350–39,650 BP · Heinrich Stadial 4",
        0: "12,650–12,950 BP · Younger Dryas onset (k = 0)",
        -4: "11,450–11,750 BP · End of YD / Holocene onset",
    }

    p1_top, row_h, left1, right1 = 26, 23, 278, 650
    p1_h = row_h * len(top8)
    p1_bot = p1_top + p1_h

    # Panel 2: Exploratory raw Taylor Glacier d13C-CO2 across 13,550 -> 12,050 BP (oldest on left, youngest on right)
    p2_top = p1_bot + 62
    p2_h = 155
    p2_bot = p2_top + p2_h
    left2, right2 = 64, 680
    H = p2_bot + 44

    sx1 = lambda v: left1 + (v / 1.05) * (right1 - left1)
    # Age axis left=13600 (older), right=12000 (younger) so time flows left -> right!
    sx2 = lambda age: left2 + (13600.0 - age) / (13600.0 - 12000.0) * (right2 - left2)
    # d13C y-axis: -6.55 top, -6.82 bottom
    sy2 = lambda d: p2_top + (-6.55 - d) / (-6.55 - (-6.82)) * p2_h

    o = [
        f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" '
        f'aria-label="Taylor Glacier atmospheric combustion score top windows and Younger Dryas profile" '
        f'xmlns="http://www.w3.org/2000/svg">'
    ]
    # Panel 1 header
    o.append(f'<text class="c-group" x="0" y="{p1_top - 10}">A · TOP 8 WINDOWS IN TAYLOR GLACIER TG_BURN (OF 54 USABLE)</text>')
    for tick in (0.0, 0.25, 0.5, 0.75, 1.0):
        x = sx1(tick)
        o.append(f'<line class="{"c-zero" if tick == 0 else "c-grid"}" x1="{x:.1f}" x2="{x:.1f}" y1="{p1_top - 2}" y2="{p1_bot + 2}"/>')
        o.append(f'<text class="c-tick" x="{x:.1f}" y="{p1_bot + 16}" text-anchor="middle">{tick:.2f}</text>')
    o.append(f'<text class="c-sub" x="{left1}" y="{p1_bot + 32}">TG_BURN = max(0, ΔCO₂) × max(0, −Δδ¹³C) in ppm·‰</text>')

    for i, row in enumerate(top8):
        yy = p1_top + i * row_h
        cy = yy + row_h / 2
        k = row["k"]
        val = row["value"]
        is_k0 = (k == 0)
        is_km1 = (k == -1)
        lab = labels.get(k, f"{row['start_bp']:.0f}–{row['end_bp']:.0f} BP")
        bar_cls = "c-bar is-on" if is_k0 else "c-bar"
        tip = esc(f"#{row['rank']} {lab}|TG_BURN = {val:.3f} ppm·‰")
        o.append(
            f'<g class="c-mark" tabindex="0" data-tip="{tip}">'
            f'<rect class="c-hit" x="0" y="{yy}" width="{W}" height="{row_h}"/>'
            f'<text class="{"c-label-sm" if (is_k0 or is_km1) else "c-sub"}" x="0" y="{cy + 4:.1f}">#{row["rank"]} {esc(lab)}</text>'
            f'<rect class="{bar_cls}" x="{left1}" y="{yy + 4}" width="{max(1.0, sx1(val) - left1):.1f}" height="{row_h - 8}" rx="2"'
            f'{" style=\"opacity:.85\"" if is_km1 else ""}/>'
            f'<text class="c-value" style="font-size:11px" x="{sx1(val) + 6:.1f}" y="{cy + 4:.1f}">{val:.2f}</text>'
            f'</g>'
        )

    # Panel 2: Raw Taylor Glacier d13C-CO2 across 13,600 -> 12,000 BP
    o.append(f'<text class="c-group" x="0" y="{p2_top - 10}">B · RAW TAYLOR GLACIER δ¹³C-CO₂ ACROSS THE YOUNGER DRYAS (EXPLORATORY; TIME FLOWS LEFT → RIGHT)</text>')
    # Target window k=0 band [12650, 12950)
    o.append(
        f'<rect class="c-band" x="{sx2(12950.0):.1f}" y="{p2_top}" '
        f'width="{sx2(12650.0) - sx2(12950.0):.1f}" height="{p2_h}"/>'
    )
    for d_tick in (-6.55, -6.60, -6.65, -6.70, -6.75, -6.80):
        y = sy2(d_tick)
        o.append(f'<line class="c-grid" x1="{left2}" x2="{right2}" y1="{y:.1f}" y2="{y:.1f}"/>')
        o.append(f'<text class="c-tick" x="{left2 - 8}" y="{y + 4:.1f}" text-anchor="end">{d_tick:.2f}‰</text>')
    for a_tick in (13500, 13200, 12900, 12600, 12300, 12000):
        x = sx2(a_tick)
        o.append(f'<line class="c-grid" x1="{x:.1f}" x2="{x:.1f}" y1="{p2_top}" y2="{p2_bot}"/>')
        o.append(f'<text class="c-tick" x="{x:.1f}" y="{p2_bot + 16}" text-anchor="middle">{a_tick:,}</text>')
    o.append(f'<text class="c-axis" x="{left2}" y="{p2_bot + 35}">Calendar years before 1950 (older on left, younger on right) · shaded band = target window [12,650, 12,950)</text>')

    # YD onset line at 12,846 cal BP
    x_yd = sx2(12846.0)
    o.append(f'<line class="c-onset" x1="{x_yd:.1f}" x2="{x_yd:.1f}" y1="{p2_top}" y2="{p2_bot}"/>')
    o.append(f'<text class="c-label-sm" x="{x_yd - 5:.1f}" y="{p2_top + 13}" text-anchor="end">YD cold onset (12,846)</text>')

    pts = [p for p in POST["tg_yd"] if 12000.0 <= p["age"] <= 13600.0]
    pts.sort(key=lambda p: -p["age"])  # oldest to youngest (left to right)
    path_d = " L".join(f"{sx2(p['age']):.1f},{sy2(p['d13c']):.1f}" for p in pts)
    o.append(f'<path class="c-line" d="M{path_d}"/>')
    for p in pts:
        cx, cy = sx2(p["age"]), sy2(p["d13c"])
        tip = esc(f"{p['age']:.0f} cal BP|CO₂ = {p['co2']:.1f} ppm|δ¹³C-CO₂ = {p['d13c']:.3f} ‰")
        o.append(
            f'<g class="c-mark" tabindex="0" data-tip="{tip}">'
            f'<circle class="c-dot" cx="{cx:.1f}" cy="{cy:.1f}" r="4.2"/>'
            f'</g>'
        )
    # Annotations for flat onset & delayed trough
    o.append(f'<text class="c-sub" x="{sx2(12845):.1f}" y="{sy2(-6.59):.1f}" text-anchor="start">flat at onset</text>')
    o.append(f'<text class="c-label-sm" x="{sx2(12575) + 8:.1f}" y="{sy2(-6.78) + 4:.1f}" text-anchor="start">trough 12,580 BP (−0.165‰, ~266 yr later)</text>')
    o.append("</svg>")

    figure(
        "atmosphere",
        "Taylor Glacier atmospheric carbon across the Younger Dryas and Heinrich Stadials",
        "\n".join(o),
        "Top: the 8 strongest 300-year windows in Taylor Glacier's combined CO₂-rise × δ¹³C-drop score (TG_BURN). "
        "The Younger Dryas onset window (copper, rank 7 of 54) trails Heinrich Stadials 1 and 4 and the mid-Younger Dryas window "
        "150–450 years later (rank 2). Bottom (exploratory): raw Taylor Glacier δ¹³C-CO₂ samples showing a flat plateau across "
        "12,937–12,751 cal BP before dropping to −6.780‰ at 12,580 cal BP—matching the size and timing of Southern Ocean carbon release during Heinrich Stadial 1.",
    )


def fig_charcoal() -> None:
    """Two-panel Archive B figure: 13.5 kyr Tier C1 peaking fraction + synthetic 100-yr fire pulse power."""
    rows = []
    with open(Q / "results" / "windows_charcoal_13_5ka.tsv", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            rows.append({
                "k": int(r["k"]),
                "start": int(r["start_bp"]),
                "end": int(r["end_bp"]),
                "mid": int(r["mid_bp"]),
                "c1_f": float(r["C1_F_peak"]),
                "c1_n": int(r["C1_n"]),
                "c1_e": float(r["C1_E_mean"]),
            })
    # Order oldest -> youngest (left -> right)
    rows.sort(key=lambda r: -r["mid"])

    W = 720
    p1_top, p1_h, left1, right1 = 26, 130, 56, 685
    p1_bot = p1_top + p1_h

    # Panel 2: Synthetic pulse recovery (E_100 top 5% & rank 1 for 50% and 75% of sites)
    p2_top = p1_bot + 64
    p2_h = 115
    p2_bot = p2_top + p2_h
    H = p2_bot + 40

    sx1 = lambda mid: left1 + (14750.0 - mid) / (14750.0 - 1250.0) * (right1 - left1)
    sy1 = lambda v: p1_bot - (v / 0.35) * p1_h
    bar_w = (right1 - left1) / len(rows) - 2.0

    o = [
        f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" '
        f'aria-label="Global Charcoal Database Tier C1 peaking fraction over 13,500 years and synthetic pulse detection power" '
        f'xmlns="http://www.w3.org/2000/svg">'
    ]
    o.append(f'<text class="c-group" x="0" y="{p1_top - 10}">A · GLOBAL CHARCOAL TIER C1 (19 WELL-DATED HIGH-RES SITES): FRACTION OF SITES ≥ +1.0 SD</text>')
    for tick in (0.0, 0.10, 0.20, 0.30):
        y = sy1(tick)
        o.append(f'<line class="{"c-zero" if tick == 0 else "c-grid"}" x1="{left1}" x2="{right1}" y1="{y:.1f}" y2="{y:.1f}"/>')
        o.append(f'<text class="c-tick" x="{left1 - 8}" y="{y + 4:.1f}" text-anchor="end">{int(round(tick * 100))}%</text>')
    for a_tick in (14000, 12000, 10000, 8000, 6000, 4000, 2000):
        x = sx1(a_tick)
        o.append(f'<text class="c-tick" x="{x:.1f}" y="{p1_bot + 16}" text-anchor="middle">{a_tick:,}</text>')
    o.append(f'<text class="c-axis" x="{left1}" y="{p1_bot + 34}">Calendar years before 1950 (300-year windows, oldest on left)</text>')

    for r in rows:
        cx = sx1(r["mid"])
        x = cx - bar_w / 2
        y = sy1(r["c1_f"])
        h = max(1.5, p1_bot - y)
        is_k0 = (r["k"] == 0)
        is_rk1 = (r["k"] == -4)
        cls = "c-bar is-on" if is_k0 else "c-bar"
        n_pk = int(round(r["c1_f"] * r["c1_n"]))
        tip = esc(
            f"[{r['start']:,}, {r['end']:,}) cal BP|Sites ≥ +1.0 SD: {n_pk}/{r['c1_n']} ({r['c1_f']*100:.1f}%)"
            f"|Composite local excess E_mean: {r['c1_e']:+.3f} SD"
        )
        o.append(
            f'<g class="c-mark" tabindex="0" data-tip="{tip}">'
            f'<rect class="c-hit" x="{x - 1:.1f}" y="{p1_top}" width="{bar_w + 2:.1f}" height="{p1_h}"/>'
            f'<rect class="{cls}" x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{h:.1f}" rx="1.5"'
            f'{" style=\"fill:var(--ink);opacity:.78\"" if is_rk1 else ""}/>'
            f'</g>'
        )
    # Callouts on Panel 1
    x_k0 = sx1(12800.0)
    o.append(f'<line class="c-leader" x1="{x_k0:.1f}" x2="{x_k0:.1f}" y1="{sy1(0.053) - 4:.1f}" y2="{p1_top + 22}"/>')
    o.append(f'<text class="c-label-sm" x="{x_k0 + 4:.1f}" y="{p1_top + 18}" text-anchor="start">YD onset: 1/19 sites (rank 38/45)</text>')
    x_rk1 = sx1(11600.0)
    o.append(f'<text class="c-label-sm" x="{x_rk1 + 10:.1f}" y="{sy1(0.294) + 8:.1f}" text-anchor="start">Rank 1: 11,450–11,750 BP (end-YD warming, 29%)</text>')

    # Panel 2: Synthetic pulse recovery on Tier C1 (E_100 rank-1 & top-5% recovery)
    o.append(f'<text class="c-group" x="0" y="{p2_top - 10}">B · COULD TIER C1 HAVE MISSED A REAL GLOBAL FIRE? (200 SYNTHETIC 100-YR PULSES, E_100 RECOVERY)</text>')
    synth_sub = [r for r in S["synthetic_pulse_c1"] if r["fraction_sites"] in (0.5, 0.75)]
    # 8 grouped bars: (A=0.5,50%), (0.5,75%), (1.0,50%), (1.0,75%), (1.5,50%), (1.5,75%), (2.0,50%), (2.0,75%)
    sy2 = lambda v: p2_bot - v * p2_h
    for tick in (0.0, 0.25, 0.50, 0.75, 1.0):
        y = sy2(tick)
        o.append(f'<line class="{"c-zero" if tick == 0 else "c-grid"}" x1="{left1}" x2="{right1}" y1="{y:.1f}" y2="{y:.1f}"/>')
        o.append(f'<text class="c-tick" x="{left1 - 8}" y="{y + 4:.1f}" text-anchor="end">{int(tick * 100)}%</text>')
    slot_w = (right1 - left1) / len(synth_sub)
    for i, r in enumerate(synth_sub):
        x0 = left1 + i * slot_w + 10
        bw = slot_w - 20
        top5 = r["E_100_top5"]
        top1 = r["E_100_top1"]
        lab = f"+{r['amplitude_sd']:.1f} SD · {int(r['fraction_sites']*100)}%"
        tip = esc(
            f"Synthetic 100-yr fire pulse: +{r['amplitude_sd']:.1f} SD across {int(r['fraction_sites']*100)}% of Tier C1 sites"
            f"|E_100 hits top 5%: {top5*100:.0f}%|E_100 hits Rank 1: {top1*100:.0f}%"
            f"|E_mean hits top 5%: {r['E_mean_top5']*100:.0f}%"
        )
        o.append(
            f'<g class="c-mark" tabindex="0" data-tip="{tip}">'
            f'<rect class="c-hit" x="{x0 - 4:.1f}" y="{p2_top}" width="{bw + 8:.1f}" height="{p2_h}"/>'
            f'<rect class="c-bar" x="{x0:.1f}" y="{sy2(top5):.1f}" width="{bw:.1f}" height="{max(1.0, p2_bot - sy2(top5)):.1f}" rx="2"/>'
            f'<rect class="c-bar is-on" x="{x0:.1f}" y="{sy2(top1):.1f}" width="{bw:.1f}" height="{max(1.0, p2_bot - sy2(top1)):.1f}" rx="2"/>'
            f'<text class="c-tick" x="{x0 + bw / 2:.1f}" y="{p2_bot + 15}" text-anchor="middle">{esc(lab)}</text>'
            f'<text class="c-value" style="font-size:10.5px" x="{x0 + bw / 2:.1f}" y="{sy2(top5) - 4:.1f}" text-anchor="middle">{int(round(top1 * 100))}%</text>'
            f'</g>'
        )
    o.append(f'<text class="c-axis" x="{left1}" y="{p2_bot + 33}">Injected pulse amplitude (SD) and share of global sites affected · copper = Rank 1 recovery, grey cap = top-5% recovery</text>')
    o.append("</svg>")

    figure(
        "charcoal",
        "Global charcoal across 13,500 years and synthetic fire-pulse detection power",
        "\n".join(o),
        "Top: share of well-dated, high-resolution global charcoal sites (Tier C1, n = 19) exceeding +1.0 SD in each 300-year "
        "window from 14,750 to 1,250 cal BP. At the Younger Dryas onset (copper, [12,650, 12,950)), only 1 of 19 sites peaks "
        "(rank 38 of 45); the actual Rank-1 peak is at the abrupt warming ending the Younger Dryas (11,450–11,750 BP, 29%). "
        "Bottom: fraction of 200 simulated 100-year global fire pulses recovered by E_100 on the same 19 sites (labels show Rank-1 recovery; 95–100% for a ≥ +1.0 SD fire across 75% of sites or ≥ +1.5 SD across half of sites).",
    )


if __name__ == "__main__":
    fig_ranks()
    fig_atmosphere()
    fig_charcoal()
    print(f"wrote 3 figures to {OUT}")
