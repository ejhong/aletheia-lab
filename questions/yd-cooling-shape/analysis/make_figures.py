#!/usr/bin/env python3
"""Generate 3 interactive inline SVG figures for site/content/yd-cooling-shape.md.

Standard library only.
Usage: python3 questions/yd-cooling-shape/analysis/make_figures.py
"""
from __future__ import annotations

import csv
import html
import json
import math
import pathlib

Q = pathlib.Path(__file__).resolve().parent.parent
ROOT = Q.parent.parent
OUT = ROOT / "site" / "figures" / "yd-cooling-shape"
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


def key_line(text: str, ctx: bool = False) -> str:
    cls = "c-line-ctx" if ctx else "c-line"
    return (
        f'<span class="key"><svg viewBox="0 0 18 10" width="18" height="10" aria-hidden="true">'
        f'<line class="{cls}" x1="1" y1="5" x2="17" y2="5"/></svg> {esc(text)}</span>'
    )


def fig_profiles() -> None:
    """Three-panel composite shape (-300 to +300 yr around onset) comparing GS-1 vs median & IQR of other coolings."""
    W, left, right, ph, gap, top = 720, 56, 688, 125, 48, 28
    panels = [
        ("A · GREENLAND TEMPERATURE (NGRIP, 25 COOLINGS OVER 100,000 YR)", "ngrip_temp_100ka", -9.0, 4.0, (-8, -4, 0, 4), lambda v: f"{v:+.0f}°C", "°C relative to 100 yr before onset"),
        ("B · GREENLAND DUST Ca²⁺ (NGRIP, 25 COOLINGS OVER 100,000 YR)", "ngrip_log_ca_100ka", -0.6, 2.0, (0, 0.693, 1.386), lambda v: f"×{math.exp(v):.0f}", "fold change vs. 100 yr before onset"),
        ("C · ANTARCTIC 7-CORE MEAN TEMPERATURE (10 COOLINGS OVER 40,000 YR)", "ant_mean_40ka", -0.6, 0.8, (-0.4, 0.0, 0.4, 0.8), lambda v: f"{v:+.1f}°C", "°C relative to 100 yr before onset"),
    ]
    H = top + len(panels) * ph + (len(panels) - 1) * gap + 46
    sx = lambda tau: left + (tau + 300.0) / 600.0 * (right - left)

    o = [
        f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" '
        f'aria-label="Composite shape of the Younger Dryas cooling versus other ice-age coolings in Greenland and Antarctica" '
        f'xmlns="http://www.w3.org/2000/svg">'
    ]
    for pi, (title, pkey, ylo, yhi, ticks, fmt, unit) in enumerate(panels):
        d = S["profiles"][pkey]
        y0 = top + pi * (ph + gap)
        sy = lambda v: y0 + ph - (min(max(v, ylo), yhi) - ylo) / (yhi - ylo) * ph

        o.append(f'<text class="c-group" x="{left}" y="{y0 - 10}">{esc(title)}</text>')
        o.append(f'<text class="c-sub" x="{right}" y="{y0 - 10}" text-anchor="end">{esc(unit)}</text>')
        # Shaded first-60-yr abruptness zone on Greenland panels
        if pi in (0, 1):
            o.append(f'<rect class="c-band" x="{sx(0):.1f}" y="{y0}" width="{sx(60) - sx(0):.1f}" height="{ph}"/>')
        for tk in ticks:
            y = sy(tk)
            o.append(f'<line class="{"c-zero" if abs(tk) < 1e-6 else "c-grid"}" x1="{left}" x2="{right}" y1="{y:.1f}" y2="{y:.1f}"/>')
            o.append(f'<text class="c-tick" x="{left - 8}" y="{y + 4:.1f}" text-anchor="end">{esc(fmt(tk))}</text>')
        o.append(f'<line class="c-onset" x1="{sx(0):.1f}" x2="{sx(0):.1f}" y1="{y0 - 2}" y2="{y0 + ph}"/>')

        taus = d["tau_mid_yr"]
        qhi = d["q75_others"]
        qlo = d["q25_others"]
        med = d["median_others"]
        tgt = d["target"]

        valid_band = [(t, hi, lo) for t, hi, lo in zip(taus, qhi, qlo) if hi is not None and lo is not None]
        if valid_band:
            pts_up = " L".join(f"{sx(t):.1f},{sy(hi):.1f}" for t, hi, _ in valid_band)
            pts_dn = " L".join(f"{sx(t):.1f},{sy(lo):.1f}" for t, _, lo in reversed(valid_band))
            o.append(f'<path class="c-area-ctx" d="M{pts_up} L{pts_dn} Z"/>')
        pts_med = " L".join(f"{sx(t):.1f},{sy(v):.1f}" for t, v in zip(taus, med) if v is not None)
        pts_tgt = " L".join(f"{sx(t):.1f},{sy(v):.1f}" for t, v in zip(taus, tgt) if v is not None)
        o.append(f'<path class="c-line-ctx" d="M{pts_med}"/>')
        o.append(f'<path class="c-line" d="M{pts_tgt}"/>')

        step = taus[1] - taus[0] if len(taus) > 1 else 20.0
        for t, vt, vm, vl, vh in zip(taus, tgt, med, qlo, qhi):
            if vt is None or vm is None:
                continue
            when = f"{int(abs(t))} yr before onset" if t < 0 else f"{int(t)} yr after onset"
            if pkey == "ngrip_log_ca_100ka":
                tip = esc(f"{when}|Younger Dryas: ×{math.exp(vt):.2f}|Other coolings median: ×{math.exp(vm):.2f} (IQR ×{math.exp(vl):.2f}–×{math.exp(vh):.2f})")
            else:
                tip = esc(f"{when}|Younger Dryas: {vt:+.2f} °C|Other coolings median: {vm:+.2f} °C (IQR {vl:+.2f} to {vh:+.2f} °C)")
            o.append(
                f'<g class="c-mark" tabindex="0" data-tip="{tip}">'
                f'<rect class="c-hit" x="{sx(t - step/2):.1f}" y="{y0}" width="{sx(step) - sx(0):.1f}" height="{ph}"/>'
                f'</g>'
            )

        for tx in (-300, -200, -100, 0, 100, 200, 300):
            lab = "onset" if tx == 0 else f"{abs(tx)} {'before' if tx < 0 else 'after'}"
            o.append(f'<text class="c-tick" x="{sx(tx):.1f}" y="{y0 + ph + 15}" text-anchor="middle">{lab}</text>')

        if pi == 0:
            o.append(f'<text class="c-label-sm" x="{sx(70):.1f}" y="{sy(-1.1):.1f}">Younger Dryas: slower initial drop (rank 22/25)</text>')
            o.append(f'<text class="c-sub" x="{sx(90):.1f}" y="{sy(-6.7):.1f}">other 24 coolings (median &amp; IQR)</text>')
        elif pi == 1:
            o.append(f'<text class="c-label-sm" x="{sx(66):.1f}" y="{sy(0.22):.1f}">YD dust barely moves in first 60 yr (rank 25/25)</text>')
        elif pi == 2:
            o.append(f'<text class="c-label-sm" x="{sx(75):.1f}" y="{sy(0.32):.1f}">Antarctica warms slightly (+0.04 °C) — no impact winter</text>')

    o.append(f'<text class="c-axis" x="{left}" y="{H - 6}">Years relative to published GICC05 stadial onset (Rasmussen et al. 2014) · shaded band = first 60 yr</text>')
    o.append("</svg>")
    legend = (
        f'<p class="fig-legend">'
        f'{key_line("Younger Dryas (GS-1)")}'
        f'{key_line("Median of other abrupt coolings (grey band = middle half / IQR)", ctx=True)}'
        f'</p>\n'
    )
    figure(
        "profiles",
        "Cooling trajectory of the Younger Dryas versus other abrupt ice-age coolings",
        "\n".join(o),
        "Baseline-centered trajectories from 300 years before to 300 years after each abrupt cooling onset. "
        "In both Greenland temperature (A) and dust (B), the Younger Dryas (copper) ramps into cold much more slowly during the "
        "shaded first 60 years than typical ice-age coolings before joining the middle of the grey band. In Antarctica (C), "
        "temperatures nudge upward rather than plunging into a global impact winter. Hover or focus any bin for exact numbers.",
        legend,
    )


def fig_ladder() -> None:
    """Two-column ladder of all 25 coolings: initial 60-yr dust jump (25/25) vs. full temperature drop (9/25)."""
    rows = []
    with open(Q / "results" / "coolings_100ka_temp_dust.tsv", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            rows.append({
                "event": r["event"],
                "age": int(float(r["age_b2k"])),
                "abrupt_t": float(r["abrupt_temp_60"]),
                "amp_t": float(r["amp_temp"]),
                "dust_60": float(r["dust_abrupt_60"]),
                "dust_amp": float(r["dust_jump"]),
            })
    # Order by initial 60-yr temperature drop (largest at top)
    rows.sort(key=lambda r: -r["abrupt_t"])

    W, row_h, top = 720, 20, 32
    H = top + row_h * len(rows) + 42
    bottom = top + row_h * len(rows) + 4
    l1, r1 = 128, 390
    l2, r2 = 438, 690
    sx1 = lambda v: l1 + (min(max(v, 0.0), 7.5) / 7.5) * (r1 - l1)
    sx2 = lambda v: l2 + (min(max(v, 0.0), 9.0) / 9.0) * (r2 - l2)

    o = [
        f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" '
        f'aria-label="All 25 abrupt coolings ranked by initial 60-year temperature drop alongside total cooling amplitude" '
        f'xmlns="http://www.w3.org/2000/svg">'
    ]
    o.append(f'<text class="c-group" x="{l1}" y="{top - 12}">INITIAL 60-YR COOLING DROP (°C)</text>')
    o.append(f'<text class="c-group" x="{l2}" y="{top - 12}">FULL STADIAL COOLING (°C)</text>')

    for tk in (0, 2, 4, 6):
        x = sx1(tk)
        o.append(f'<line class="{"c-zero" if tk == 0 else "c-grid"}" x1="{x:.1f}" x2="{x:.1f}" y1="{top - 4}" y2="{bottom}"/>')
        o.append(f'<text class="c-tick" x="{x:.1f}" y="{bottom + 15}" text-anchor="middle">{tk}°C</text>')
    for tk in (0, 2, 4, 6, 8):
        x = sx2(tk)
        o.append(f'<line class="{"c-zero" if tk == 0 else "c-grid"}" x1="{x:.1f}" x2="{x:.1f}" y1="{top - 4}" y2="{bottom}"/>')
        o.append(f'<text class="c-tick" x="{x:.1f}" y="{bottom + 15}" text-anchor="middle">{tk}°C</text>')

    for i, r in enumerate(rows):
        yy = top + i * row_h
        cy = yy + row_h / 2
        yd = (r["event"] == "GS-1")
        name = "Younger Dryas" if yd else r["event"]
        tip = esc(
            f"{name} ({r['age']:,} yr b2k)|First 60 yr drop: {r['abrupt_t']:.2f} °C (rank {i+1}/25)"
            f"|Full stadial drop (40–200 yr): {r['amp_t']:.2f} °C"
            f"|First 60 yr dust jump: ×{math.exp(r['dust_60']):.2f}"
        )
        o.append(
            f'<g class="c-mark" tabindex="0" data-tip="{tip}">'
            f'<rect class="c-hit" x="0" y="{yy}" width="{W}" height="{row_h}"/>'
            f'<text class="{"c-label-sm" if yd else "c-sub"}" x="0" y="{cy + 4:.1f}">{esc(name)}</text>'
            f'<text class="c-tick" x="{l1 - 8}" y="{cy + 4:.1f}" text-anchor="end">{r["age"] // 1000} ka</text>'
            f'<rect class="{"c-bar is-on" if yd else "c-bar"}" x="{l1}" y="{yy + 4}" width="{max(1.0, sx1(r["abrupt_t"]) - l1):.1f}" height="{row_h - 8}" rx="1.5"/>'
            f'<rect class="{"c-bar is-on" if yd else "c-bar"}" x="{l2}" y="{yy + 4}" width="{max(1.0, sx2(r["amp_t"]) - l2):.1f}" height="{row_h - 8}" rx="1.5"/>'
            f'</g>'
        )
    o.append(f'<text class="c-axis" x="{l1}" y="{bottom + 34}">All 25 qualifying abrupt coolings over 100,000 years (NGRIP Kindler et al. 2014), ordered by first-60-year drop</text>')
    o.append("</svg>")

    figure(
        "ladder",
        "All 25 abrupt ice-age coolings ranked by initial speed and full amplitude",
        "\n".join(o),
        "Every qualifying abrupt cooling over the last 100,000 years in NGRIP reconstructed surface temperature, "
        "sorted by how fast Greenland cooled in the first 60 years (left). The Younger Dryas (copper) sits near the very "
        "bottom at rank 22 of 25 (1.71 °C vs. 3.30 °C median), while its full 40–200 year stadial amplitude (right, 5.01 °C, "
        "rank 9 of 25) is completely ordinary. Hover or focus any cooling for numbers.",
    )


def fig_ranks() -> None:
    """Percentile dot-strip summarizing every primary and alongside metric."""
    p = S["primary"]
    a = S["alongside"]
    rows = [
        ("PRIMARY CRITERIA (PRE-REGISTERED DECISION RULE)", None),
        ("D1 · Initial 60-yr δ¹⁸O drop (60 kyr)", p["abrupt_60_d18o"], "+0.93 ‰"),
        ("D2 · Full stadial temp drop (100 kyr)", p["amp_temp_100ka"], "+5.01 °C"),
        ("D2 · Full stadial dust jump (100 kyr)", p["dust_jump_100ka"], "×3.12"),
        ("D3 · Pre-onset flatness / slope (60 kyr)", p["pre_slope_d18o"], "+0.93 ‰/100yr"),
        ("D4 · Antarctic 7-core cooling (40 kyr)", p["ant_mean_cool_40ka"], "+0.04 °C warm"),
        ("ALONGSIDE DIAGNOSTICS", None),
        ("First 60-yr temperature drop (100 kyr)", a["abrupt_temp_60_100ka"], "+1.71 °C"),
        ("First 60-yr dust surge Ca²⁺ (100 kyr)", a["dust_abrupt_60_100ka"], "×1.13"),
        ("Peak single 20-yr δ¹⁸O drop (60 kyr)", a["peak_rate_20_d18o"], "+1.63 ‰"),
        ("WAIS Divide Antarctic cooling (40 kyr)", a["antarctica_sites"]["TS_WD"]["cool_rank"], "+0.04 °C warm"),
    ]
    W, left, right, top, row_h, hdr_h = 720, 275, 610, 20, 26, 26
    y = top
    layout = []
    for item in rows:
        if item[1] is None:
            y += 10 if layout else 0
            layout.append(("hdr", y, item[0]))
            y += hdr_h
        else:
            layout.append(("row", y, item[0], item[1], item[2]))
            y += row_h
    bottom = y + 8
    H = bottom + 40
    sx = lambda pct: left + (pct / 100.0) * (right - left)

    o = [
        f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" '
        f'aria-label="Percentile rank of the Younger Dryas among abrupt ice-age coolings across every metric" '
        f'xmlns="http://www.w3.org/2000/svg">'
    ]
    o.append(f'<rect class="c-band" x="{sx(90):.1f}" y="{top}" width="{right - sx(90):.1f}" height="{bottom - top}"/>')
    for pct, lab in ((0, "lowest"), (25, "25th"), (50, "median"), (75, "75th"), (90, "top 10%"), (100, "rank 1")):
        x = sx(pct)
        cls = "c-ref" if pct == 90 else ("c-zero" if pct == 50 else "c-grid")
        o.append(f'<line class="{cls}" x1="{x:.1f}" x2="{x:.1f}" y1="{top}" y2="{bottom}"/>')
        o.append(f'<text class="c-tick" x="{x:.1f}" y="{bottom + 15}" text-anchor="middle">{lab}</text>')
    o.append(f'<text class="c-axis" x="{left}" y="{bottom + 33}">Position of Younger Dryas (GS-1) among all qualifying abrupt coolings (right = more impact-like)</text>')

    is_primary = True
    for entry in layout:
        if entry[0] == "hdr":
            _, yy, title = entry
            is_primary = title.startswith("PRIMARY")
            o.append(f'<text class="c-group" x="0" y="{yy + 15}">{esc(title)}</text>')
        else:
            _, yy, label, rec, vtxt = entry
            cy = yy + row_h / 2
            rk, n = rec["rank"], rec["n"]
            pct = 100.0 * (1.0 - (rk - 1) / max(1, n - 1)) if n > 1 else 50.0
            cx = sx(pct)
            tip = esc(f"{label}|Younger Dryas: {vtxt}|Rank {rk} of {n} coolings (others median: {rec['median_others']})")
            dot_cls = "c-dot c-hollow" if is_primary else "c-dot c-ctx"
            o.append(
                f'<g class="c-mark" tabindex="0" data-tip="{tip}">'
                f'<rect class="c-hit" x="0" y="{yy}" width="{W}" height="{row_h}"/>'
                f'<text class="{"c-label-sm" if is_primary else "c-sub"}" x="0" y="{cy + 4:.1f}">{esc(label)}</text>'
                f'<line class="c-grid" x1="{left}" x2="{right}" y1="{cy:.1f}" y2="{cy:.1f}"/>'
                f'<circle class="{dot_cls}" cx="{cx:.1f}" cy="{cy:.1f}" r="{5 if is_primary else 4.2}"/>'
                f'<text class="c-value" style="font-size:11.5px" x="{right + 10}" y="{cy + 4:.1f}">rank {rk}/{n}</text>'
                f'</g>'
            )
    o.append("</svg>")

    figure(
        "ranks",
        "Summary ranks of the Younger Dryas cooling across Greenland and Antarctica",
        "\n".join(o),
        "Every pre-registered criterion (hollow copper circles: none enter the shaded top-10% zone) and alongside diagnostic (grey). "
        "Notice how initial cooling speed (17/19 in δ¹⁸O, 22/25 in temperature) and initial dust jump (25/25 dead last) sit at the far left—slower, not faster, than typical ice-age coolings.",
    )


if __name__ == "__main__":
    fig_profiles()
    fig_ladder()
    fig_ranks()
    print(f"wrote 3 figures to {OUT}")
