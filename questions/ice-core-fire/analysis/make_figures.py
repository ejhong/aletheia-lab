#!/usr/bin/env python3
"""Draw the figures for the site page from the results files. Standard library only.

    python3 questions/ice-core-fire/analysis/make_figures.py      # writes site/figures/ice-core-fire/*.html

Each output is an HTML fragment (inline SVG plus a caption) that scripts/build_site.py drops into the page where the
content file says {{figure: ice-core-fire/<name>}}. Colours come from the site's CSS variables.
"""
import csv
import html
import json
import pathlib

Q = pathlib.Path(__file__).resolve().parent.parent
ROOT = Q.parent.parent
OUT = ROOT / "site" / "figures" / "ice-core-fire"
S = json.load(open(Q / "results" / "summary.json"))
esc = lambda s: html.escape(str(s), quote=True)
num = lambda x, d=1: f"{x:,.{d}f}"
ONSET = 12896
CORES = [("N20", "NGRIP", "years before 2000 CE"), ("E20", "NEEM", "years before 2000 CE"), ("G20", "GISP2", "years BP, the core's own timescale")]
ordinal = lambda n: f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def bins():
    out = {}
    for r in csv.DictReader(open(Q / "explore" / "bins20.tsv"), delimiter="\t"):
        if r["value"]:
            out.setdefault(r["series"], []).append((float(r["start"]), float(r["value"])))
    return out


def figure(name, title, svg, caption, legend=""):
    (OUT / f"{name}.html").write_text(f'<figure class="fig" aria-label="{esc(title)}">\n{legend}<div class="fig-scroll">\n{svg}\n</div>\n'
                                      f'<figcaption>{caption}</figcaption>\n</figure>\n')


def panels(name, title, lo, hi, ymax, yticks, xticks, bars, caption, notes, legend=""):
    """Three stacked panels, one per core; age runs from old (left) to young (right)."""
    B = bins()
    W, left, right, ph, gap, top = 720, 44, 692, 118, 46, 26
    H = top + 3 * ph + 2 * gap + 44
    sx = lambda a: left + (hi - a) / (hi - lo) * (right - left)
    o = [f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(title)}" xmlns="http://www.w3.org/2000/svg">']
    for p, (series, core, scale) in enumerate(CORES):
        y0 = top + p * (ph + gap)
        sy = lambda v: y0 + ph - min(v, ymax) / ymax * ph
        a0 = 12750 if series != "G20" else 12735
        o.append(f'<rect class="c-band" x="{sx(a0 + 300):.1f}" y="{y0}" width="{sx(a0) - sx(a0 + 300):.1f}" height="{ph}"/>')
        for t in yticks:
            o.append(f'<line class="{"c-zero" if t == 0 else "c-grid"}" x1="{left}" x2="{right}" y1="{sy(t):.1f}" y2="{sy(t):.1f}"/>')
            o.append(f'<text class="c-tick" x="{left - 6}" y="{sy(t) + 4:.1f}" text-anchor="end">{t}</text>')
        o.append(f'<text class="c-group" x="{left}" y="{y0 - 9}">{core}</text>')
        o.append(f'<text class="c-sub" x="{right}" y="{y0 - 9}" text-anchor="end">{esc(scale)}</text>')
        data = [(a, v) for a, v in B[series] if lo <= a and a + 20 <= hi]
        if bars:
            bw = sx(0) - sx(20)
            for a, v in data:
                on = a0 <= a < a0 + 300
                tip = esc(f"{core}, {num(a, 0)} to {num(a + 20, 0)}|{num(v)} µg/kg")
                o.append(f'<g class="c-mark" tabindex="0" data-tip="{tip}"><rect class="c-hit" x="{sx(a + 20):.1f}" y="{y0}" width="{bw:.1f}" height="{ph}"/>'
                         f'<rect class="c-bar{" is-on" if on else ""}" x="{sx(a + 20) + 1:.1f}" y="{sy(v):.1f}" width="{bw - 2:.1f}" height="{y0 + ph - sy(v):.1f}" rx="1.5"/></g>')
        else:
            pts = []
            for a, v in sorted(data, reverse=True):
                pts += [f"{sx(a + 20):.1f},{sy(v):.1f}", f"{sx(a):.1f},{sy(v):.1f}"]
            o.append(f'<path class="c-step" d="M{sx(data and max(a for a, _ in data) + 20):.1f},{y0 + ph} L{" L".join(pts)} L{sx(min(a for a, _ in data)):.1f},{y0 + ph} Z"/>')
        for t in xticks:
            o.append(f'<text class="c-tick" x="{sx(t):.1f}" y="{y0 + ph + 15}" text-anchor="middle">{num(t, 0)}</text>')
        if series != "G20":
            o.append(f'<line class="c-onset" x1="{sx(ONSET):.1f}" x2="{sx(ONSET):.1f}" y1="{y0 - 2}" y2="{y0 + ph}"/>')
        for n_series, age, text, dy, anchor in notes:
            if n_series == series:
                if dy is None:                       # sit just above the bin that holds this age
                    dy = min(sy(v) for a, v in data if a <= age < a + 20) - 6 - y0
                elif dy < 0:                         # a label at the top with a leader down to the bars
                    dy = -dy
                    o.append(f'<line class="c-leader" x1="{sx(age):.1f}" x2="{sx(age):.1f}" y1="{y0 + dy + 4}" y2="{min(sy(v) for a, v in data if a <= age < a + 20) - 3:.1f}"/>')
                o.append(f'<text class="c-label-sm" x="{sx(age):.1f}" y="{y0 + dy:.1f}" text-anchor="{anchor}">{esc(text)}</text>')
    o.append(f'<text class="c-axis" x="{left}" y="{H - 6}">Ammonium, µg per kg of ice, in 20-year means. Older ice on the left.</text>')
    o.append("</svg>")
    figure(name, title, "\n".join(o), caption, legend)


def profile():
    notes = [("N20", ONSET + 8, "the cold begins, 12,896", 11, "end"), ("E20", ONSET + 8, "the cold begins", 11, "end"),
             ("N20", 12745, "the high", 11, "start"), ("G20", 12885, "depth said to be cited", -11, "middle")]
    panels("profile", "Ammonium across the start of the Younger Dryas in three ice cores", 12400, 13400, 60, (0, 25, 50),
           (13400, 13200, 13000, 12800, 12600, 12400), True,
           "Each bar is a 20-year mean. Copper bars are the 300-year window that was tested; the vertical line is the start of the cold "
           "in NGRIP and NEEM, which share a timescale. Ammonium is low when the cold begins and for some decades after. The high comes "
           "30 to 140 years later, in all three cores. GISP2 has its own timescale, so its ages cannot be lined up with the others to "
           "the decade. Hover or focus a bar for its value.", notes)


def long_view():
    notes = [("N20", 12900, "tested window", 11, "middle"), ("N20", 12190, "12,190", None, "middle"), ("N20", 15370, "15,370", None, "middle"),
             ("N20", 13870, "13,870", None, "middle"), ("E20", 13850, "13,850", None, "middle"), ("E20", 12900, "tested window", 11, "middle"),
             ("G20", 13875, "13,875", None, "middle"), ("G20", 12885, "tested window", 11, "middle"), ("G20", 11755, "11,755", None, "middle")]
    panels("long", "Ammonium from 16,000 to 10,300 years ago in three ice cores", 10300, 16000, 60, (0, 25, 50),
           (16000, 15000, 14000, 13000, 12000, 11000), False,
           "The same 20-year means over six thousand years, the end of the last ice age. The shaded band is the tested window. It "
           "holds one of the highest stretches, and not the only one: labelled ages mark other 20-year means that stand as far or "
           "further above their surroundings. The one near 13,870 years ago appears in all three cores.", notes)


def ranks():
    rows = [("10-year bins · 10,300 to 107,620 years", ["N10", "E10"]), ("20-year bins · 10,300 to 50,000 years", ["N20", "E20", "G20"]),
            ("60-year bins · 10,300 to 107,620 years", ["N60", "E60", "G60"])]
    core = {"N": "NGRIP", "E": "NEEM", "G": "GISP2"}
    W, label_w, right, xmax = 720, 78, 596, 1.5
    sx = lambda v: label_w + min(v, xmax) / xmax * (right - label_w)
    row_h, group_h, top = 30, 30, 8
    H = top + sum(group_h + row_h * len(ss) for _, ss in rows) + 44
    o = [f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="Where the tested window ranks among all windows" xmlns="http://www.w3.org/2000/svg">']
    bottom = H - 40
    for t, lab in ((0, "0"), (0.5, "half"), (1.0, "the top-1% line"), (1.5, "")):
        o.append(f'<line class="{"c-ref" if t == 1.0 else "c-zero" if t == 0 else "c-grid"}" x1="{sx(t):.1f}" x2="{sx(t):.1f}" y1="{top + 20}" y2="{bottom}"/>')
        o.append(f'<text class="c-tick" x="{sx(t):.1f}" y="{bottom + 16}" text-anchor="middle">{lab}</text>')
    o.append(f'<text class="c-axis" x="{label_w}" y="{bottom + 34}">Largest excess in each window, as a share of what the top 1% needs</text>')
    y = top
    for title, series in rows:
        o.append(f'<text class="c-group" x="0" y="{y + 20}">{esc(title)}</text>')
        y += group_h
        for s in series:
            r = S["ranks"]["E"][s]
            need = r["value_needed_top1"]
            cy = y + row_h / 2
            for w in csv.DictReader(open(Q / "results" / f"windows_{s}.tsv"), delimiter="\t"):
                if w["E"] != "nan" and int(w["k"]) != 0:
                    x = sx(max(float(w["E"]), 0) / need)
                    o.append(f'<line class="c-tickmark" x1="{x:.1f}" x2="{x:.1f}" y1="{cy - 7:.1f}" y2="{cy + 7:.1f}"/>')
            x5 = sx(r["value_needed_top5"] / need)
            o.append(f'<line class="c-line5" x1="{x5:.1f}" x2="{x5:.1f}" y1="{cy - 11:.1f}" y2="{cy + 11:.1f}"/>')
            tip = esc(f"{core[s[0]]}, {s[1:]}-year bins|Excess {num(r['value'])} µg/kg|Rank {r['rank']} of {r['N']}|Top 5% needs {num(r['value_needed_top5'])}, top 1% needs {num(need)}")
            o.append(f'<g class="c-mark" tabindex="0" data-tip="{tip}"><rect class="c-hit" x="0" y="{y}" width="{W}" height="{row_h}"/>'
                     f'<text class="c-label" x="0" y="{cy + 4:.1f}">{core[s[0]]}</text>'
                     f'<circle class="c-dot" cx="{sx(r["value"] / need):.1f}" cy="{cy:.1f}" r="5.5"/>'
                     f'<text class="c-value" x="{right + 14}" y="{cy + 4:.1f}">{ordinal(r["rank"])} of {r["N"]}</text></g>')
            y += row_h
    o.append("</svg>")
    legend = ('<p class="fig-legend"><span class="key"><svg viewBox="0 0 12 12" width="12" height="12" aria-hidden="true"><circle class="k-dot" cx="6" cy="6" r="4.5"/></svg>'
              ' The window at the start of the Younger Dryas</span><span class="key"><svg viewBox="0 0 12 12" width="12" height="12" aria-hidden="true">'
              '<line class="k-tick" x1="6" x2="6" y1="1" y2="11"/></svg> Every other 300-year window</span><span class="key">'
              '<svg viewBox="0 0 12 12" width="12" height="12" aria-hidden="true"><line class="k-line5" x1="6" x2="6" y1="0" y2="12"/></svg> The top-5% line</span></p>\n')
    figure("ranks", "Where the tested window ranks among all windows", "\n".join(o),
           "Each thin tick is one 300-year window of the record, placed by its largest ammonium excess; ticks at the right edge are "
           "that far or further. Measured over 20 or 60 years the tested window is past the top-5% line in every core and short of the "
           "top-1% line in every core. Over 10 years it falls just short of the 5% line. Hover or focus a row for the numbers.", legend)


def dust():
    """NGRIP: ammonium above, dust (calcium) below, across the onset. Exploratory series from explore/volcanic.json."""
    rows = json.load(open(Q / "explore" / "volcanic.json"))["bins20_NGRIP"]
    lo, hi = 12500, 13300
    W, left, right, ph, gap, top = 720, 44, 692, 112, 46, 26
    H = top + 2 * ph + gap + 44
    sx = lambda a: left + (hi - a) / (hi - lo) * (right - left)
    o = [f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="Ammonium and dust across the start of the Younger Dryas in NGRIP" xmlns="http://www.w3.org/2000/svg">']
    for p, (key, title, unit, ymax, yticks) in enumerate((("NH4", "Ammonium", "µg/kg", 60, (0, 25, 50)), ("Ca", "Dust (calcium)", "µg/kg", 340, (0, 150, 300)))):
        y0 = top + p * (ph + gap)
        sy = lambda v: y0 + ph - min(v, ymax) / ymax * ph
        o.append(f'<rect class="c-band" x="{sx(12850):.1f}" y="{y0}" width="{sx(12750) - sx(12850):.1f}" height="{ph}"/>')
        for t in yticks:
            o.append(f'<line class="{"c-zero" if t == 0 else "c-grid"}" x1="{left}" x2="{right}" y1="{sy(t):.1f}" y2="{sy(t):.1f}"/>')
            o.append(f'<text class="c-tick" x="{left - 6}" y="{sy(t) + 4:.1f}" text-anchor="end">{t}</text>')
        o.append(f'<text class="c-group" x="{left}" y="{y0 - 9}">{title}</text>')
        o.append(f'<text class="c-sub" x="{right}" y="{y0 - 9}" text-anchor="end">NGRIP, {unit}, 20-year means</text>')
        bw = sx(0) - sx(20)
        for r in rows:
            a, v = r["start"], r[key]
            if lo <= a and a + 20 <= hi:
                tip = esc(f"{title}, {num(a, 0)} to {num(a + 20, 0)}|{num(v)} {unit}")
                o.append(f'<g class="c-mark" tabindex="0" data-tip="{tip}"><rect class="c-hit" x="{sx(a + 20):.1f}" y="{y0}" width="{bw:.1f}" height="{ph}"/>'
                         f'<rect class="c-bar{" is-on" if a < ONSET else ""}" x="{sx(a + 20) + 1:.1f}" y="{sy(v):.1f}" width="{bw - 2:.1f}" height="{y0 + ph - sy(v):.1f}" rx="1.5"/></g>')
        for t in (13300, 13100, 12900, 12700, 12500):
            o.append(f'<text class="c-tick" x="{sx(t):.1f}" y="{y0 + ph + 15}" text-anchor="middle">{num(t, 0)}</text>')
        o.append(f'<line class="c-onset" x1="{sx(ONSET):.1f}" x2="{sx(ONSET):.1f}" y1="{y0 - 2}" y2="{y0 + ph}"/>')
        if p == 0:
            o.append(f'<text class="c-label-sm" x="{sx(ONSET + 8):.1f}" y="{y0 + 12}" text-anchor="end">abrupt shift, 12,896</text>')
            o.append(f'<text class="c-label-sm" x="{sx(12800):.1f}" y="{y0 + 12}" text-anchor="middle">both climb</text>')
            o.append(f'<text class="c-label-sm" x="{sx(12615):.1f}" y="{y0 + 12}" text-anchor="middle">ammonium falls back</text>')
        else:
            o.append(f'<text class="c-label-sm" x="{sx(12615):.1f}" y="{y0 + 12}" text-anchor="middle">dust stays high</text>')
    o.append(f'<text class="c-axis" x="{left}" y="{H - 6}">Years before 2000 CE. Older ice on the left. Copper bars come after the shift; shaded band is the ~100-year high.</text>')
    o.append("</svg>")
    figure("dust", "Ammonium and dust across the start of the Younger Dryas in NGRIP", "\n".join(o),
           "Exploratory. Dust rises as the climate turns cold, dry and windy, climbing for about a century after the abrupt shift "
           "and then staying high. Ammonium climbs alongside it during the shaded century, then drops back by roughly half while dust "
           "remains high. That decoupling is why thinner snow and drier winds alone cannot explain the peak; the other two cores show the same.")


def flux():
    """Late-glacial NGRIP 20-year windows: concentration excess vs snowfall-adjusted flux proxy (explore/after.json)."""
    rows = json.load(open(Q / "explore" / "after.json"))["N20_excess_times_layer_thickness_10300_to_15000"]
    by_e = sorted(rows, key=lambda r: -r["E"])
    by_f = sorted(rows, key=lambda r: -r["E_x_layer"])
    top_n = 8
    W, row_h, top = 720, 28, 38
    H = top + top_n * row_h + 36
    c1_lab, c1_x0, c1_x1 = 0, 92, 306
    c2_lab, c2_x0, c2_x1 = 362, 454, 668
    max_e = max(r["E"] for r in by_e)
    max_f = max(r["E_x_layer"] for r in by_f)
    o = [f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="Late-glacial NGRIP windows ranked by concentration excess and by snowfall-adjusted flux proxy" xmlns="http://www.w3.org/2000/svg">']
    o.append(f'<text class="c-group" x="{c1_x0}" y="16">Concentration excess</text>')
    o.append(f'<text class="c-sub" x="{c1_x1 + 36}" y="16" text-anchor="end">µg/kg</text>')
    o.append(f'<text class="c-group" x="{c2_x0}" y="16">Flux proxy</text>')
    o.append(f'<text class="c-sub" x="{c2_x1 + 44}" y="16" text-anchor="end">E × cm/yr</text>')
    o.append(f'<line class="c-zero" x1="{c1_x0}" x2="{c1_x0}" y1="{top - 6}" y2="{top + top_n * row_h - 4}"/>')
    o.append(f'<line class="c-zero" x1="{c2_x0}" x2="{c2_x0}" y1="{top - 6}" y2="{top + top_n * row_h - 4}"/>')
    for i in range(top_n):
        y = top + i * row_h
        cy = y + row_h / 2
        re, rf = by_e[i], by_f[i]
        for r, val, vmax, lx, x0, x1 in (
            (re, re["E"], max_e, c1_lab, c1_x0, c1_x1),
            (rf, rf["E_x_layer"], max_f, c2_lab, c2_x0, c2_x1),
        ):
            on = int(r["start"]) == 12750
            bw = val / vmax * (x1 - x0)
            st = int(r["start"])
            label = f"{st:,}" + (" · YD" if on else "")
            tip = esc(f"Window {st:,}–{st + 300:,} b2k|Peak bin {int(r['E_age']):,} b2k|Excess {num(r['E'])} µg/kg|Excess × layer thickness {num(r['E_x_layer'])}")
            o.append(f'<g class="c-mark" tabindex="0" data-tip="{tip}">'
                     f'<rect class="c-hit" x="{lx}" y="{y}" width="{x1 - lx + 48}" height="{row_h}"/>'
                     f'<text class="{"c-label" if on else "c-tick"}" x="{x0 - 8}" y="{cy + 4:.1f}" text-anchor="end">{esc(label)}</text>'
                     f'<rect class="c-bar{" is-on" if on else ""}" x="{x0}" y="{y + 5}" width="{bw:.1f}" height="{row_h - 10}" rx="1.5"/>'
                     f'<text class="c-value" x="{x0 + bw + 6:.1f}" y="{cy + 4:.1f}">{num(val, 1)}</text></g>')
    o.append(f'<text class="c-axis" x="0" y="{H - 8}">Top 8 of 16 NGRIP 20-year windows (10,300–15,000 b2k). Copper bar is the Younger Dryas onset window (12,750–13,050).</text>')
    o.append("</svg>")
    figure("flux", "Concentration excess versus snowfall-adjusted flux proxy in NGRIP late-glacial windows", "\n".join(o),
           "Exploratory. Because annual ice layers thin after the onset (from 4.01 to 3.01 cm/yr in NGRIP, and 2.75 cm/yr at the "
           "3-year peak), the same fallout produces a higher concentration. Scaling each late-glacial window's excess by its local "
           "layer thickness drops the Younger Dryas window from 2nd to 5th of 16. Hover or focus a bar for values.")


def gisp2():
    """Single-core depth stratigraphy in GISP2 (1719.5 m to 1703.5 m), no timescale conversion needed."""
    lo_m, hi_m = 1703.5, 1719.5  # older/deeper on the left (1719.5), younger/shallower on the right (1703.5)
    W, left, right = 720, 44, 692
    H = 212
    sx = lambda m: left + (hi_m - m) / (hi_m - lo_m) * (right - left)
    y_axis = 128
    o = [f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="Order of sulphate, cited platinum depth, and ammonium high inside the GISP2 ice core" xmlns="http://www.w3.org/2000/svg">']
    # Band for the century-long NH4 high (1710.7 to 1708.0 m)
    o.append(f'<rect class="c-band" x="{sx(1710.7):.1f}" y="28" width="{sx(1708.0) - sx(1710.7):.1f}" height="{y_axis - 28}"/>')
    o.append(f'<text class="c-group" x="{sx(1709.35):.1f}" y="20" text-anchor="middle">Century-long NH₄ high (1710.7–1708.0 m)</text>')
    o.append(f'<line class="c-zero" x1="{left}" x2="{right}" y1="{y_axis}" y2="{y_axis}"/>')
    for m in (1719, 1716, 1713, 1710, 1707, 1704):
        o.append(f'<line class="c-grid" x1="{sx(m):.1f}" x2="{sx(m):.1f}" y1="{y_axis}" y2="{y_axis + 6}"/>')
        o.append(f'<text class="c-tick" x="{sx(m):.1f}" y="{y_axis + 20}" text-anchor="middle">{m} m</text>')
    # Events: (depth, above/below, y_label, anchor, title, sub, is_highlight, tip)
    events = [
        (1718.6, "above", 52, "start", "Sulphate spike", "649 ppb · 13,031 BP", False,
         "1718.6 m (~13,031 BP)|Sulphate 649 ppb (background 58); NH4 9.7 ppb"),
        (1713.8, "above", 86, "end", "Sulphate spike", "462 ppb · 12,930 BP", False,
         "1713.8 m (~12,930 BP)|Sulphate 462 ppb (background 60); NH4 6.8 ppb"),
        (1712.25, "below", 174, "middle", "Cited depth (~1712.2 m)", "NH₄ 31.4 ppb · dust rises", False,
         "1712.2–1712.3 m (~12,888–12,890 BP)|Reported platinum depth (unverified); NH4 31.4 ppb, surrounded by 9–15 ppb"),
        (1708.85, "above", 56, "middle", "Peak NH₄ sample", "77.3 ppb · 12,771 BP", True,
         "1708.8–1708.9 m (~12,771–12,775 BP)|Largest NH4 sample in the window: 77.3 ppb (3.4 m above 1712.2 m)"),
        (1704.4, "below", 174, "end", "Largest sulphate", "986 ppb · 12,605 BP", False,
         "1704.4 m (~12,605 BP)|Sulphate 986 ppb (background 181); well inside the Younger Dryas"),
    ]
    # Bracket showing 3.4 m gap between 1712.25 m and 1708.85 m
    x_pt, x_pk = sx(1712.25), sx(1708.85)
    o.append(f'<line class="c-whisker" x1="{x_pt:.1f}" x2="{x_pk:.1f}" y1="{y_axis - 16}" y2="{y_axis - 16}"/>')
    o.append(f'<text class="c-label-sm" x="{(x_pt + x_pk) / 2:.1f}" y="{y_axis - 22}" text-anchor="middle">3.4 m higher (~115 yr later)</text>')
    for m, side, yl, anchor, title, sub, hi, tip in events:
        x = sx(m)
        y_end = yl + 16 if side == "above" else yl - 14
        o.append(f'<g class="c-mark" tabindex="0" data-tip="{esc(tip)}">'
                 f'<rect class="c-hit" x="{x - 14:.1f}" y="28" width="28" height="{H - 44}"/>'
                 f'<line class="{"c-ref" if hi else "c-leader"}" x1="{x:.1f}" x2="{x:.1f}" y1="{y_axis}" y2="{y_end}"/>'
                 f'<circle class="{"c-dot" if hi else "c-dot c-hollow"}" cx="{x:.1f}" cy="{y_axis}" r="{"5.5" if hi else "4.5"}"/>'
                 f'<text class="c-label-sm" x="{x:.1f}" y="{yl}" text-anchor="{anchor}">{esc(title)}</text>'
                 f'<text class="c-sub" x="{x:.1f}" y="{yl + 14}" text-anchor="{anchor}">{esc(sub)}</text></g>')
    o.append(f'<text class="c-axis" x="{left}" y="{H - 4}">GISP2 depth in metres (older ice on the left; ages from Mayewski et al. 1997). All ions come from the same samples.</text>')
    o.append("</svg>")
    figure("gisp2", "Order of sulphate spikes, cited platinum depth, and ammonium high inside GISP2", "\n".join(o),
           "Single-core stratigraphy in GISP2, needing no timescale comparison. At 1712.2–1712.3 m—the depth supporters are "
           "reported to cite for platinum and fire (unverified)—ammonium is a modest 31.4 ppb, bordered by 9–15 ppb samples. "
           "The century-long ammonium high sits 2 to 3.5 metres higher in the core, peaking at 77.3 ppb at 1708.8–1708.9 m.")


def verdict():
    rows = [
        ("The first claim · unusual high near the onset",
         "Greenland ice holds an unusual ammonium high near the start of the Younger Dryas.",
         "Ranks 3rd to 7th of 131–323 windows over 20–60 years in all three cores, and 1st to 3rd in raw concentration. Short of the 1% 'exceptional' bar.",
         "is-yes", "Unusual (top 5%)"),
        ("The second claim · an onset fire spike",
         "A cosmic impact or airburst lit a sudden firestorm (or made ammonia) when the cold began.",
         "Ammonium is low at the onset (12,896 b2k) and for 30–40 years after. Single years are ordinary; in GISP2 the big high sits 2–3.5 m above the cited platinum depth.",
         "is-no", "Poor fit"),
        ("The broader hypothesis · whether an impact happened",
         "A cosmic impact triggered the Younger Dryas.",
         "This study checks Greenland ammonium only. It removes onset fire smoke as supporting evidence, but cannot rule out an impact on ice or ocean, nor does it test platinum or terrestrial proxies.",
         "is-open", "Not settled here"),
    ]
    out = ['<div class="verdict" role="list" aria-label="Three claims and where each stands">']
    for kicker, text, note, cls, status in rows:
        out.append('<div class="verdict-row" role="listitem">')
        out.append(f'<div><p class="verdict-kicker">{esc(kicker)}</p><p class="verdict-text">{esc(text)}</p>'
                   f'<p class="verdict-note">{esc(note)}</p></div>')
        out.append(f'<p class="verdict-status {cls}"><span class="dot"></span>{esc(status)}</p>')
        out.append('</div>')
    out.append('</div>\n')
    (OUT / "verdict.html").write_text("\n".join(out))


def tiles():
    r = S["ranks"]["E"]
    rk = [r[s]["rank"] for s in ("N20", "E20", "G20", "N60", "E60", "G60")]
    t = [("Unusual", "the verdict by the rule fixed in advance: top 5% in every core, top 1% in none", True),
         (f"{ordinal(min(rk))} to {ordinal(max(rk))}", "largest ammonium high of 131 to 323 windows, measured over 20 or 60 years", False),
         ("3 of 3", "ice cores show it, from two laboratories", False),
         ("30–40 yr", "after the cold began before ammonium started to rise", False)]
    (OUT / "tiles.html").write_text('<div class="tiles">\n' + "\n".join(
        f'<div class="tile"><p class="tile-value{" is-word" if word else ""}">{esc(v)}</p><p class="tile-label">{esc(l)}</p></div>' for v, l, word in t) + "\n</div>\n")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    verdict()
    tiles()
    profile()
    long_view()
    ranks()
    dust()
    flux()
    gisp2()
    print("wrote", ", ".join(sorted(p.name for p in OUT.iterdir())), [p.stat().st_size for p in sorted(OUT.iterdir())])


if __name__ == "__main__":
    main()

