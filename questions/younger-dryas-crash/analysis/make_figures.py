#!/usr/bin/env python3
"""Draw the figures for the site page from the results files. Standard library only.

    python3 questions/younger-dryas-crash/analysis/make_figures.py      # writes site/figures/younger-dryas-crash/*.html
"""
import csv
import html
import json
import pathlib

Q = pathlib.Path(__file__).resolve().parent.parent
ROOT = Q.parent.parent
OUT = ROOT / "site" / "figures" / "younger-dryas-crash"
S = json.load(open(Q / "results" / "summary.json"))
esc = lambda s: html.escape(str(s), quote=True)
ONSET, LO, HI = 12850, 11300, 14300


def figure(name, title, svg, caption, legend=""):
    (OUT / f"{name}.html").write_text(f'<figure class="fig" aria-label="{esc(title)}">\n{legend}<div class="fig-scroll">\n{svg}\n</div>\n'
                                      f'<figcaption>{caption}</figcaption>\n</figure>\n')


def curves():
    data = {}
    for r in csv.DictReader(open(Q / "results" / "curves.tsv"), delimiter="\t"):
        t = int(r["cal_bp"])
        if LO <= t <= HI:
            data.setdefault(r["region"], []).append((t, float(r["summed"]), float(r["made_up_mean"]), float(r["made_up_2.5"]), float(r["made_up_97.5"])))
    W, left, right, ph, gap, top = 720, 44, 692, 132, 46, 26
    H = top + 3 * ph + 2 * gap + 44
    sx = lambda t: left + (HI - t) / (HI - LO) * (right - left)
    o = [f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="Dated human activity across the Younger Dryas onset in three regions" xmlns="http://www.w3.org/2000/svg">']
    for p, region in enumerate(("North America", "Europe", "Asia")):
        rows = data[region]
        ymax = max(r[1] for r in rows) * 1.12
        y0 = top + p * (ph + gap)
        sy = lambda v: y0 + ph - v / ymax * ph
        o.append(f'<rect class="c-band" x="{sx(ONSET + 300):.1f}" y="{y0}" width="{sx(ONSET - 300) - sx(ONSET + 300):.1f}" height="{ph}"/>')
        o.append(f'<line class="c-zero" x1="{left}" x2="{right}" y1="{y0 + ph}" y2="{y0 + ph}"/>')
        o.append(f'<text class="c-group" x="{left}" y="{y0 - 9}">{region}</text>')
        o.append(f'<text class="c-sub" x="{right}" y="{y0 - 9}" text-anchor="end">dated activity (summed calibrated dates)</text>')
        band = " L".join(f"{sx(t):.1f},{sy(hi):.1f}" for t, _, _, _, hi in rows) + " L" + " L".join(f"{sx(t):.1f},{sy(lo):.1f}" for t, _, _, lo, _ in reversed(rows))
        o.append(f'<path class="c-area-ctx" d="M{band} Z"/>')
        o.append(f'<path class="c-line-ctx" d="M{" L".join(f"{sx(t):.1f},{sy(m):.1f}" for t, _, m, _, _ in rows)}"/>')
        o.append(f'<path class="c-line" d="M{" L".join(f"{sx(t):.1f},{sy(v):.1f}" for t, v, _, _, _ in rows)}"/>')
        o.append(f'<line class="c-onset" x1="{sx(ONSET):.1f}" x2="{sx(ONSET):.1f}" y1="{y0 - 2}" y2="{y0 + ph}"/>')
        for t in (14000, 13500, 13000, 12500, 12000, 11500):
            o.append(f'<text class="c-tick" x="{sx(t):.1f}" y="{y0 + ph + 15}" text-anchor="middle">{t:,}</text>')
        step = 20
        for i in range(0, len(rows) - step, step):
            t, v, m = rows[i][0], sum(r[1] for r in rows[i:i + step]) / step, sum(r[2] for r in rows[i:i + step]) / step
            tip = esc(f"{region}, {t:,} to {t + 100:,} years ago|{v / m:.2f} times the smooth trend")
            o.append(f'<g class="c-mark" tabindex="0" data-tip="{tip}"><rect class="c-hit" x="{sx(t + 100):.1f}" y="{y0}" width="{sx(t) - sx(t + 100):.1f}" height="{ph}"/></g>')
        if p == 0:
            o.append(f'<text class="c-label-sm" x="{sx(ONSET + 12):.1f}" y="{y0 + 11}" text-anchor="end">the cold begins</text>')
            o.append(f'<text class="c-label-sm" x="{sx(12560):.1f}" y="{y0 + 11}" text-anchor="start">spike, then hollow</text>')
    o.append(f'<text class="c-axis" x="{left}" y="{H - 6}">Calendar years before 1950. Older on the left. The shaded band is the 600 years the test compares.</text>')
    o.append("</svg>")
    legend = ('<p class="fig-legend"><span class="key"><svg viewBox="0 0 16 12" width="16" height="12" aria-hidden="true"><line x1="0" x2="16" y1="6" y2="6" stroke="var(--copper)" stroke-width="2"/></svg>'
              ' The real record</span><span class="key"><svg viewBox="0 0 16 12" width="16" height="12" aria-hidden="true"><rect x="0" y="1" width="16" height="10" fill="var(--faint)" opacity=".25"/>'
              '<line x1="0" x2="16" y1="6" y2="6" stroke="var(--faint)" stroke-width="2"/></svg> Made-up records with no sudden change (middle and 95% range)</span></p>\n')
    figure("curves", "Dated human activity across the Younger Dryas onset in three regions", "\n".join(o),
           "When the cold begins, the real record does not fall below the made-up ones in any region. But look at the shapes: "
           "the same spike after the onset and the same hollow after it, on three continents at once, down to the small wiggles. "
           "People did not move in step like that. The radiocarbon calibration curve goes from steep to flat in those years and "
           "bends counts of dates in just this way, and the made-up records carry too little of the effect. Hover or focus for the numbers.", legend)


def tiles():
    na = S["regions"]["North America"]
    t = [(f"{sum(r['dates'] for r in S['regions'].values()):,}", "radiocarbon dates from human sites on three continents"),
         ("No drop", "in dated human activity when the cold began, in any region"),
         (f"{na['ratio_after_to_before']:.2f}×", "North America: the 300 years after against the 300 before; a halving of people would give about 0.93"),
         ("Same shape", "on all three continents, spike and hollow alike: the mark of the dating method, which weakens the test")]
    (OUT / "tiles.html").write_text('<div class="tiles">\n' + "\n".join(
        f'<div class="tile"><p class="tile-value{" is-word" if not v[0].isdigit() and "×" not in v else ""}">{esc(v)}</p><p class="tile-label">{esc(l)}</p></div>' for v, l in t) + "\n</div>\n")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    tiles()
    curves()
    print("wrote", ", ".join(sorted(p.name for p in OUT.iterdir())))


if __name__ == "__main__":
    main()
