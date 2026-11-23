#!/usr/bin/env python3
"""Draw the figures for the site page from the results files. Reads results only; recomputes nothing.

    cd questions/gcp-audit && python analysis/make_figures.py      # writes site/figures/gcp-audit/*.html
"""
import csv
import html
import json
import pathlib

Q = pathlib.Path(__file__).resolve().parent.parent
ROOT = Q.parent.parent
OUT = ROOT / "site" / "figures" / "gcp-audit"
S = json.load(open(Q / "results" / "summary.json"))
ALL = list(csv.DictReader(open(Q / "results" / "windows.tsv"), delimiter="\t"))
# The events we could score, in date order (registry number breaks ties).
ROWS = sorted((r for r in ALL if r["event_z"]), key=lambda r: (r["begin_utc"], int(r["num"])))
esc = lambda s: html.escape(str(s), quote=True)
num = lambda x, d=2: f"{x:+.{d}f}".replace("-", "−")
tick = lambda t: str(t).replace("-", "−")


def figure(name, title, svg, caption):
    (OUT / f"{name}.html").write_text(f'<figure class="fig" aria-label="{esc(title)}">\n<div class="fig-scroll">\n{svg}\n</div>\n'
                                      f'<figcaption>{caption}</figcaption>\n</figure>\n')


def tiles():
    a, rep = S["all"], S["all"]["reproduction"]
    t = [(str(rep["n"]), "of the project's formal events, re-scored from the raw one-second data"),
         (f"{rep['r']:.2f}", "the correlation between our scores and the published ones"),
         (num(a["events"]["z"]), f"the combined score of the events; the project's own figure for the same events is {num(rep['combined_published'])}"),
         (num(a["controls"]["z"]), "the combined score of the same hours a week away")]
    (OUT / "tiles.html").write_text('<div class="tiles">\n' + "\n".join(
        f'<div class="tile"><p class="tile-value">{esc(v)}</p><p class="tile-label">{esc(l)}</p></div>' for v, l in t) + "\n</div>\n")


def reproduction():
    rep = S["all"]["reproduction"]
    pts = [(float(r["published_z"]), float(r["event_z"])) for r in ROWS]
    lim = 3.5
    W, left, top, side = 720, 52, 14, 330
    H = top + side + 48
    sx = lambda v: left + (v + lim) / (2 * lim) * side
    sy = lambda v: top + (lim - v) / (2 * lim) * side
    title = f"Our score against the published score for {len(pts)} events"
    o = [f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(title)}" xmlns="http://www.w3.org/2000/svg">']
    for t in range(-3, 4):
        cls = "c-grid"
        o.append(f'<line class="{cls}" x1="{left}" x2="{left + side}" y1="{sy(t):.1f}" y2="{sy(t):.1f}"/>')
        o.append(f'<line class="{cls}" x1="{sx(t):.1f}" x2="{sx(t):.1f}" y1="{top}" y2="{top + side}"/>')
        o.append(f'<text class="c-tick" x="{left - 6}" y="{sy(t) + 4:.1f}" text-anchor="end">{tick(t)}</text>')
        o.append(f'<text class="c-tick" x="{sx(t):.1f}" y="{top + side + 16}" text-anchor="middle">{tick(t)}</text>')
    o.append(f'<line class="c-ref" x1="{sx(-lim):.1f}" y1="{sy(-lim):.1f}" x2="{sx(lim):.1f}" y2="{sy(lim):.1f}"/>')
    for x, y in pts:
        o.append(f'<circle class="c-dot c-ctx" cx="{sx(x):.1f}" cy="{sy(y):.1f}" r="2.6"/>')
    o.append(f'<text class="c-axis" x="{left + side / 2:.1f}" y="{H - 8}" text-anchor="middle">Published score</text>')
    o.append(f'<text class="c-axis" transform="translate(14 {top + side / 2:.1f}) rotate(-90)" text-anchor="middle">Our score from the raw data</text>')
    o.append(f'<text class="c-label-sm" x="{sx(lim) + 6:.1f}" y="{sy(lim) + 4:.1f}">same score</text>')
    notes = ["The copper line marks where the two", "scores agree exactly. Dots above it are",
             "events we scored higher than the project", "did; dots below, lower.", "",
             f"{rep['share_within_0.25']:.0%} of events differ by less than 0.25;",
             f"{rep['share_within_0.5']:.0%} by less than 0.5."]
    for k, s in enumerate(notes):
        o.append(f'<text class="c-sub" x="{left + side + 40}" y="{top + 40 + 17 * k}">{esc(s)}</text>')
    o.append("</svg>")
    figure("reproduction", title, "\n".join(o),
           "Each dot is one of the project's formal events. Our score, recomputed from the raw one-second data, against the "
           f"score the project published. The correlation is {rep['r']:.2f}; half the events differ by less than "
           f"{rep['median_abs_difference']:.2f}.")


def cumulative():
    n = len(ROWS)
    series = {"ours": [], "pub": [], "ctl": []}
    tot = {k: 0.0 for k in series}
    for r in ROWS:
        for k, col in (("ours", "event_z"), ("pub", "published_z"), ("ctl", "control_z")):
            tot[k] += float(r[col]) if r[col] else 0.0
            series[k].append(tot[k])
    hi = max(max(v) for v in series.values())
    lo = min(min(v) for v in series.values())
    y_hi, y_lo = 40 * (int(hi // 40) + 1), -40 * (int(-lo // 40) + 1)
    W, left, right, top, ph = 720, 46, 560, 18, 300
    sx = lambda k: left + k / n * (right - left)
    sy = lambda v: top + (y_hi - v) / (y_hi - y_lo) * ph
    H = top + ph + 48
    title = f"Running total of scores over the {n} events"
    o = [f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(title)}" xmlns="http://www.w3.org/2000/svg">']
    for t in range(y_lo, y_hi + 1, 40):
        o.append(f'<line class="{"c-zero" if t == 0 else "c-grid"}" x1="{left}" x2="{right}" y1="{sy(t):.1f}" y2="{sy(t):.1f}"/>')
        o.append(f'<text class="c-tick" x="{left - 6}" y="{sy(t) + 4:.1f}" text-anchor="end">{tick(t)}</text>')
    years, last = {}, -99.0
    for k, r in enumerate(ROWS):
        years.setdefault(r["begin_utc"][:4], k)
    for y, k in years.items():
        if sx(k) - last >= 34 and right - sx(k) >= 24:  # keep year labels from colliding
            o.append(f'<text class="c-tick" x="{sx(k):.1f}" y="{top + ph + 16}" text-anchor="start">{y}</text>')
            last = sx(k)
    o.append(f'<text class="c-axis" x="{left}" y="{H - 6}">The {n} events in date order. Each step adds one event&#39;s score to the running total.</text>')
    line = lambda v: f"M{sx(0):.1f},{sy(0):.1f} L" + " L".join(f"{sx(k + 1):.1f},{sy(x):.1f}" for k, x in enumerate(v))
    o.append(f'<path class="c-line-ctx" d="{line(series["ctl"])}"/>')
    o.append(f'<path class="c-path-open" style="stroke-width:1.5;stroke-dasharray:3 4" d="{line(series["pub"])}"/>')
    o.append(f'<path class="c-line" d="{line(series["ours"])}"/>')
    ends = sorted([(sy(series["pub"][-1]), "published scores"), (sy(series["ours"][-1]), "our scores")])
    if ends[1][0] - ends[0][0] < 15:  # push the two event labels apart if their lines end close together
        mid = (ends[0][0] + ends[1][0]) / 2
        ends = [(mid - 7.5, ends[0][1]), (mid + 7.5, ends[1][1])]
    for y, s in ends:
        o.append(f'<text class="c-label-sm" x="{right + 6}" y="{y + 4:.1f}">events, {s}</text>')
    o.append(f'<text class="c-label-sm" x="{right + 6}" y="{sy(series["ctl"][-1]) + 4:.1f}">a week away</text>')
    o.append("</svg>")
    figure("cumulative", title, "\n".join(o),
           "Adding up the scores event by event, in date order. The events climb steadily, in our figures (solid copper) "
           "as in the published ones (dotted). The same hours a week away (grey) wander around zero.")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    tiles()
    reproduction()
    cumulative()
    print("wrote", ", ".join(sorted(p.name for p in OUT.iterdir())))


if __name__ == "__main__":
    main()
