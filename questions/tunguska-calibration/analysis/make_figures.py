#!/usr/bin/env python3
"""Draw the figures for the site page from the results files. Standard library only.

    python3 questions/tunguska-calibration/analysis/make_figures.py     # writes site/figures/tunguska-calibration/*.html
"""
import csv
import html
import json
import pathlib
import statistics

Q = pathlib.Path(__file__).resolve().parent.parent
ROOT = Q.parent.parent
OUT = ROOT / "site" / "figures" / "tunguska-calibration"
S = json.load(open(Q / "results" / "summary.json"))
esc = lambda s: html.escape(str(s), quote=True)
NAMES = {"neem_s1": "NEEM", "humboldt": "Humboldt", "tunu2013": "Tunu 2013", "tunu2022a": "Tunu 2022a", "ngrip1": "NGRIP",
         "negis": "NEGIS", "act11d": "ACT11d", "summit2010": "Summit 2010", "summit2023": "Summit 2023"}
WHERE = {"neem_s1": "north-west", "humboldt": "north-west", "tunu2013": "north-east", "tunu2022a": "north-east", "ngrip1": "central north",
         "negis": "north-east", "act11d": "south-west", "summit2010": "not in the test", "summit2023": "not in the test"}


def figure(name, title, svg, caption, legend=""):
    (OUT / f"{name}.html").write_text(f'<figure class="fig" aria-label="{esc(title)}">\n{legend}<div class="fig-scroll">\n{svg}\n</div>\n'
                                      f'<figcaption>{caption}</figcaption>\n</figure>\n')


def tiles():
    n = S["nh4"]["network"]
    ex = S["nh4"]["excess_over_typical_year"]
    apart = S["nh4"]["reported_apart"]
    t = [(f"{n['rank']}th of {n['n']}", "where 1908 and 1909 rank for ammonium across six Greenland sites: ordinary", True),
         (f"×{1 + ex['NEGIS']:.0f}", "ammonium at NEGIS in 1908 against a typical year: the largest mark among the test sites", False),
         (f"×{1 + apart['summit2010']['excess']:.0f} to ×{1 + apart['summit2023']['excess']:.0f}", "at Summit, in two cores, confirming the spike that prompted the question", True),
         ("None", "at NEEM and Humboldt in the north-west: the mark is patchy, as smoke is", True)]
    (OUT / "tiles.html").write_text('<div class="tiles">\n' + "\n".join(
        f'<div class="tile"><p class="tile-value{" is-word" if w else ""}">{esc(v)}</p><p class="tile-label">{esc(l)}</p></div>' for v, l, w in t) + "\n</div>\n")


def ranks():
    rows = [(int(r["window_start"]), float(r["score"])) for r in csv.DictReader(open(Q / "results" / "window_scores.tsv"), delimiter="\t")
            if r["species"] == "nh4" and r["site"] == "network"]
    W, H, left, right, top, bottom = 720, 250, 44, 706, 26, 200
    lo, hi = min(y for y, _ in rows), max(y for y, _ in rows) + 2
    vmax = max(v for _, v in rows) * 1.08
    sx = lambda y: left + (y - lo) / (hi - lo) * (right - left)
    sy = lambda v: bottom - max(v, 0) / vmax * (bottom - top)
    order = sorted(rows, key=lambda r: -r[1])
    o = [f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="Network ammonium score of each two-year window from {lo} to {hi - 1}" xmlns="http://www.w3.org/2000/svg">']
    o.append(f'<line class="c-zero" x1="{left}" x2="{right}" y1="{bottom}" y2="{bottom}"/>')
    cut = order[max(0, round(0.10 * len(rows)) - 1)][1]
    o.append(f'<line class="c-tickmark" x1="{left}" x2="{right}" y1="{sy(cut):.1f}" y2="{sy(cut):.1f}" stroke-dasharray="3 4"/>')
    o.append(f'<text class="c-sub" x="{left + 4}" y="{sy(cut) - 5:.1f}">the top tenth starts here</text>')
    bw = (sx(lo + 2) - sx(lo)) - 2
    for y, v in rows:
        rank = 1 + sum(w > v for _, w in rows)
        tip = esc(f"{y} and {y + 1}|score {v:.2f}, rank {rank} of {len(rows)}")
        o.append(f'<g class="c-mark" tabindex="0" data-tip="{tip}"><rect class="c-hit" x="{sx(y):.1f}" y="{top}" width="{bw + 2:.1f}" height="{bottom - top}"/>'
                 f'<rect class="c-bar{" is-on" if y == 1908 else ""}" x="{sx(y) + 1:.1f}" y="{sy(v):.1f}" width="{bw:.1f}" height="{bottom - sy(v):.1f}" rx="2"/></g>')
    for y, v in order[:3]:
        o.append(f'<text class="c-label-sm" x="{sx(y) + bw / 2 + 1:.1f}" y="{sy(v) - 5:.1f}" text-anchor="middle">{y}</text>')
    v08 = dict(rows)[1908]
    o.append(f'<text class="c-label-sm" x="{sx(1908) + bw / 2 + 1:.1f}" y="{sy(v08) - 5:.1f}" text-anchor="middle">1908</text>')
    for y in range(1860, 1961, 20):
        o.append(f'<text class="c-tick" x="{sx(y):.1f}" y="{bottom + 16}" text-anchor="middle">{y}</text>')
    o.append(f'<text class="c-axis" x="{left}" y="{H - 8}">Each bar is two years. Height: how far ammonium stood above the surrounding thirty years, averaged over six sites.</text>')
    o.append("</svg>")
    n = S["nh4"]["network"]
    figure("ranks", "How 1908 and 1909 compare with every other pair of years", "\n".join(o),
           f"The copper bar is 1908 and 1909, ranked {n['rank']} of {n['n']}. The pairs of years that stand out across Greenland begin in 1894, 1888 and 1862. "
           "A pulse of two typical years' ammonium at every site would have reached the top tenth nine times in ten. Hover or focus a bar for its numbers.")


def sites():
    data = {}
    for r in csv.DictReader(open(Q / "results" / "annual_nh4.tsv"), delimiter="\t"):
        data.setdefault(r["core"], {})[int(r["year"])] = float(r["mean"])
    cores = ["neem_s1", "humboldt", "ngrip1", "tunu2013", "tunu2022a", "negis", "act11d", "summit2010", "summit2023"]
    Y0, Y1 = 1900, 1916
    W, cw, ch, gx, gy, left, top = 720, 214, 96, 26, 58, 14, 30
    H = top + 3 * ch + 2 * gy + 42
    o = [f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="Yearly ammonium from {Y0} to {Y1} in nine ice cores, as multiples of a typical year" xmlns="http://www.w3.org/2000/svg">']
    for i, c in enumerate(cores):
        s = data[c]
        typ = statistics.median([s[y] for y in list(range(1893, 1908)) + list(range(1910, 1925)) if y in s])
        x0, y0 = left + (i % 3) * (cw + gx), top + (i // 3) * (ch + gy)
        vals = {y: s[y] / typ for y in range(Y0, Y1 + 1) if y in s}
        vmax = max(4.0, max(vals.values()) * 1.3)
        bw = cw / (Y1 - Y0 + 1)
        sy = lambda v: y0 + ch - v / vmax * ch
        o.append(f'<rect class="c-band" x="{x0 + (1908 - Y0) * bw:.1f}" y="{y0}" width="{2 * bw:.1f}" height="{ch}"/>')
        o.append(f'<text class="c-group" x="{x0}" y="{y0 - 10}">{esc(NAMES[c])}</text>')
        o.append(f'<text class="c-sub" x="{x0 + cw}" y="{y0 - 10}" text-anchor="end">{esc(WHERE[c])}</text>')
        o.append(f'<line class="c-tickmark" x1="{x0}" x2="{x0 + cw}" y1="{sy(1):.1f}" y2="{sy(1):.1f}" stroke-dasharray="3 4"/>')
        o.append(f'<line class="c-zero" x1="{x0}" x2="{x0 + cw}" y1="{y0 + ch}" y2="{y0 + ch}"/>')
        for y, v in vals.items():
            tip = esc(f"{NAMES[c]}, {y}|{v:.1f} times a typical year")
            o.append(f'<g class="c-mark" tabindex="0" data-tip="{tip}"><rect class="c-hit" x="{x0 + (y - Y0) * bw:.1f}" y="{y0}" width="{bw:.1f}" height="{ch}"/>'
                     f'<rect class="c-bar{" is-on" if y in (1908, 1909) else ""}" x="{x0 + (y - Y0) * bw + 1.5:.1f}" y="{sy(v):.1f}" width="{bw - 3:.1f}" height="{y0 + ch - sy(v):.1f}" rx="1.5"/></g>')
        big = max(vals, key=vals.get)
        if vals[big] >= 2:
            o.append(f'<text class="c-label-sm" x="{x0 + (big - Y0 + 0.5) * bw:.1f}" y="{sy(vals[big]) - 4:.1f}" text-anchor="middle">×{vals[big]:.1f}</text>')
        for y in (1900, 1908, 1916):
            o.append(f'<text class="c-tick" x="{x0 + (y - Y0 + 0.5) * bw:.1f}" y="{y0 + ch + 14}" text-anchor="middle">{y}</text>')
    o.append(f'<text class="c-axis" x="{left}" y="{H - 8}">Each year\'s ammonium as a multiple of a typical year (dashed). Shaded: 1908 and 1909. Scales differ.</text>')
    o.append("</svg>")
    figure("sites", "Yearly ammonium around 1908, core by core", "\n".join(o),
           "A large spike in 1908 at NEGIS and at Summit, a smaller one in 1909 at ACT11d, and little or nothing in the north-west. "
           "A mark this uneven from one site to the next is what a plume of smoke leaves. The two Summit cores were not part of the test, "
           "because the spike there was already known. Hover or focus a bar for its value.")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    tiles()
    ranks()
    sites()
    print("wrote", ", ".join(sorted(p.name for p in OUT.iterdir())))


if __name__ == "__main__":
    main()
