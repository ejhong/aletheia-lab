#!/usr/bin/env python3
"""Draw the figures for the site page from the results files. Standard library only.

    python3 questions/cooling-ammonium/analysis/make_figures.py      # writes site/figures/cooling-ammonium/*.html
"""
import csv
import html
import json
import math
import pathlib

Q = pathlib.Path(__file__).resolve().parent.parent
ROOT = Q.parent.parent
OUT = ROOT / "site" / "figures" / "cooling-ammonium"
S = json.load(open(Q / "results" / "summary.json"))
X = json.load(open(Q / "explore" / "after.json"))
esc = lambda s: html.escape(str(s), quote=True)
times = lambda d: f"×{math.exp(d):.1f}"


def figure(name, title, svg, caption, legend=""):
    (OUT / f"{name}.html").write_text(f'<figure class="fig" aria-label="{esc(title)}">\n{legend}<div class="fig-scroll">\n{svg}\n</div>\n'
                                      f'<figcaption>{caption}</figcaption>\n</figure>\n')


def key(cls, text, hollow=False):
    return (f'<span class="key"><svg viewBox="0 0 12 12" width="12" height="12" aria-hidden="true"><circle class="k-dot{" k-hollow" if hollow else ""}" '
            f'cx="6" cy="6" r="{3.8 if hollow else 4.5}"/></svg> {esc(text)}</span>')


def ladder():
    ev = {c: {r["event"]: r for r in S["ammonium"]["events"][c]} for c in ("NGRIP", "NEEM")}
    order = [e for e, _ in X["two_core_mean_D"]]
    W, label_w, right, row_h, top = 720, 150, 660, 21, 26
    lo, hi = math.log(0.4), math.log(5)
    sx = lambda d: label_w + (min(max(d, lo), hi) - lo) / (hi - lo) * (right - label_w)
    H = top + row_h * len(order) + 44
    bottom = top + row_h * len(order) + 4
    o = [f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="Ammonium after each abrupt cooling" xmlns="http://www.w3.org/2000/svg">']
    for f, lab in ((0.5, "half"), (1, "no change"), (2, "×2"), (4, "×4")):
        x = sx(math.log(f))
        o.append(f'<line class="{"c-zero" if f == 1 else "c-grid"}" x1="{x:.1f}" x2="{x:.1f}" y1="{top - 6}" y2="{bottom}"/>')
        o.append(f'<text class="c-tick" x="{x:.1f}" y="{bottom + 16}" text-anchor="middle">{lab}</text>')
    o.append(f'<text class="c-axis" x="{label_w}" y="{bottom + 36}">Ammonium 40 to 160 years after the cooling, against the century before</text>')
    for i, e in enumerate(order):
        cy = top + row_h * i + row_h / 2
        a, b = ev["NGRIP"][e]["D"], ev["NEEM"][e]["D"]
        yd = e == "GS-1"
        name = "Younger Dryas" if yd else e
        fade = "" if yd else ' opacity=".3"'
        tip = esc(f"{name}, onset {ev['NGRIP'][e]['age']:,} years ago|NGRIP {times(a)}|NEEM {times(b)}")
        o.append(f'<g class="c-mark" tabindex="0" data-tip="{tip}"><rect class="c-hit" x="0" y="{cy - row_h / 2:.1f}" width="{W}" height="{row_h}"/>'
                 f'<text class="{"c-label" if yd else "c-sub"}" x="0" y="{cy + 4:.1f}">{esc(name)}</text>'
                 f'<text class="c-tick" x="{label_w - 10}" y="{cy + 4:.1f}" text-anchor="end">{ev["NGRIP"][e]["age"]:,}</text>'
                 f'<line class="c-whisker" x1="{sx(a):.1f}" x2="{sx(b):.1f}" y1="{cy:.1f}" y2="{cy:.1f}"{fade}/>'
                 f'<circle class="c-dot{"" if yd else " c-ctx"}" cx="{sx(a):.1f}" cy="{cy:.1f}" r="{5 if yd else 4}"/>'
                 f'<circle class="c-dot c-hollow{"" if yd else " c-ctx-hollow"}" cx="{sx(b):.1f}" cy="{cy:.1f}" r="{5 if yd else 4}"/></g>')
    o.append("</svg>")
    legend = f'<p class="fig-legend">{key("", "NGRIP core")}{key("", "NEEM core", True)}<span class="key">Copper: the Younger Dryas. Grey: the 24 other coolings, with the age of each.</span></p>\n'
    figure("ladder", "Ammonium after each abrupt cooling", "\n".join(o),
           "Each row is one abrupt cooling of the last ice age, ordered by the average of the two cores. To the right of "
           "&ldquo;no change&rdquo;, ammonium ran higher in the delayed century than before the cooling. Most rows are to the right; "
           "the Younger Dryas is at the top, with two others close behind. Hover or focus a row for the numbers.", legend)


def shape():
    W, left, right, ph, gap, top = 720, 44, 692, 150, 50, 26
    H = top + 2 * ph + gap + 44
    sx = lambda k: left + (k + 300) / 600 * (right - left)
    o = [f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="The shape of ammonium around a cooling" xmlns="http://www.w3.org/2000/svg">']
    for p, core in enumerate(("NGRIP", "NEEM")):
        d = X["shape"][f"ammonium_{core}"]
        y0 = top + p * (ph + gap)
        sy = lambda v: y0 + ph - min(v, 5) / 5 * ph
        for t in (0, 1, 2, 3, 4, 5):
            o.append(f'<line class="{"c-zero" if t == 0 else "c-grid"}" x1="{left}" x2="{right}" y1="{sy(t):.1f}" y2="{sy(t):.1f}"/>')
            o.append(f'<text class="c-tick" x="{left - 6}" y="{sy(t) + 4:.1f}" text-anchor="end">{"×" + str(t) if t else "0"}</text>')
        o.append(f'<text class="c-group" x="{left}" y="{y0 - 9}">{core}</text>')
        o.append(f'<text class="c-sub" x="{right}" y="{y0 - 9}" text-anchor="end">ammonium, as a multiple of its level in the century before</text>')
        mid = [k + 10 for k in d["bin"]]
        band = " L".join(f"{sx(k):.1f},{sy(v):.1f}" for k, v in zip(mid, d["quartile_high"])) + " L" + " L".join(
            f"{sx(k):.1f},{sy(v):.1f}" for k, v in reversed(list(zip(mid, d["quartile_low"]))))
        o.append(f'<path class="c-area-ctx" d="M{band} Z"/>')
        o.append(f'<path class="c-line-ctx" d="M{" L".join(f"{sx(k):.1f},{sy(v):.1f}" for k, v in zip(mid, d["median_others"]))}"/>')
        o.append(f'<path class="c-line" d="M{" L".join(f"{sx(k):.1f},{sy(v):.1f}" for k, v in zip(mid, d["GS-1"]) if v == v)}"/>')
        o.append(f'<line class="c-onset" x1="{sx(0):.1f}" x2="{sx(0):.1f}" y1="{y0 - 2}" y2="{y0 + ph}"/>')
        for k, v, m, lowq, hiq in zip(d["bin"], d["GS-1"], d["median_others"], d["quartile_low"], d["quartile_high"]):
            when = f"{abs(k)} to {abs(k) - 20} years before" if k < 0 else f"{k} to {k + 20} years after"
            tip = esc(f"{core}, {when}|Younger Dryas ×{v:.1f}|Other coolings, middle half ×{lowq:.1f} to ×{hiq:.1f}")
            o.append(f'<g class="c-mark" tabindex="0" data-tip="{tip}"><rect class="c-hit" x="{sx(k):.1f}" y="{y0}" width="{sx(20) - sx(0):.1f}" height="{ph}"/></g>')
        for t in (-300, -200, -100, 0, 100, 200, 300):
            lab = "cooling" if t == 0 else f"{abs(t)} {'before' if t < 0 else 'after'}"
            o.append(f'<text class="c-tick" x="{sx(t):.1f}" y="{y0 + ph + 15}" text-anchor="middle">{lab}</text>')
        if p == 0:
            o.append(f'<text class="c-label-sm" x="{sx(128):.1f}" y="{sy(4.6):.1f}" text-anchor="start">Younger Dryas</text>')
            o.append(f'<text class="c-label-sm" x="{sx(210):.1f}" y="{sy(0.62):.1f}" text-anchor="start">the 24 other coolings</text>')
    o.append(f'<text class="c-axis" x="{left}" y="{H - 6}">Years from the start of the cooling, in 20-year means</text>')
    o.append("</svg>")
    figure("shape", "The shape of ammonium around a cooling", "\n".join(o),
           "Exploratory. The grey line is the middle value across the 24 other coolings and the band holds the middle half of them: "
           "ammonium steps up by a quarter to three-quarters when the cold begins and stays there. The copper line is the Younger Dryas: "
           "the same step, and then a further climb to three or four times the earlier level, 60 to 160 years in. Hover or focus for the numbers.")


def tiles():
    q = S["ammonium"]["D"]
    n1, n2 = q["q1"]["NGRIP"], q["q1"]["NEEM"]
    t = [(f"{n1['in_top_quarter']} and {n2['in_top_quarter']}", f"of 24 other coolings show a rise in ammonium, in the two ice cores"),
         (f"{times(n1['median'])} and {times(n2['median'])}", "the typical rise after a cooling"),
         (f"{times(q['q2']['NGRIP']['value'])} and {times(q['q2']['NEEM']['value'])}", "the rise after the Younger Dryas began"),
         (f"{q['q2']['NGRIP']['rank']}nd and {q['q2']['NEEM']['rank']}rd", "of 25: where the Younger Dryas ranks")]
    (OUT / "tiles.html").write_text('<div class="tiles">\n' + "\n".join(
        f'<div class="tile"><p class="tile-value">{esc(v)}</p><p class="tile-label">{esc(l)}</p></div>' for v, l in t) + "\n</div>\n")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    tiles()
    ladder()
    shape()
    print("wrote", ", ".join(sorted(p.name for p in OUT.iterdir())))


if __name__ == "__main__":
    main()
