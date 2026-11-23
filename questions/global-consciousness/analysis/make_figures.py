#!/usr/bin/env python3
"""Draw the figures for the site page from the results files. Standard library only.

    python3 questions/global-consciousness/analysis/make_figures.py      # writes site/figures/global-consciousness/*.html
"""
import csv
import html
import json
import math
import pathlib

Q = pathlib.Path(__file__).resolve().parent.parent
ROOT = Q.parent.parent
OUT = ROOT / "site" / "figures" / "global-consciousness"
S = json.load(open(Q / "results" / "summary.json"))
ROWS = sorted(csv.DictReader(open(Q / "results" / "events.tsv"), delimiter="\t"), key=lambda r: r["start_utc"])
esc = lambda s: html.escape(str(s), quote=True)
num = lambda x, d=2: f"{x:+.{d}f}".replace("-", "−")


def figure(name, title, svg, caption, legend=""):
    (OUT / f"{name}.html").write_text(f'<figure class="fig" aria-label="{esc(title)}">\n{legend}<div class="fig-scroll">\n{svg}\n</div>\n'
                                      f'<figcaption>{caption}</figcaption>\n</figure>\n')


def cumulative():
    n = len(ROWS)
    ev, co, cum_e, cum_c = [], [], 0.0, 0.0
    for r in ROWS:
        cum_e += float(r["z"])
        cum_c += float(r["control_z"]) if r["control_z"] else 0.0
        ev.append(cum_e)
        co.append(cum_c)
    W, left, right, top, ph = 720, 46, 570, 18, 300
    y_lo, y_hi = -22.0, 22.0
    sx = lambda k: left + k / n * (right - left)
    sy = lambda v: top + (y_hi - v) / (y_hi - y_lo) * ph
    H = top + ph + 48
    o = [f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="Running total of scores over the 58 events" xmlns="http://www.w3.org/2000/svg">']
    for t in (-20, -10, 0, 10, 20):
        o.append(f'<line class="{"c-zero" if t == 0 else "c-grid"}" x1="{left}" x2="{right}" y1="{sy(t):.1f}" y2="{sy(t):.1f}"/>')
        o.append(f'<text class="c-tick" x="{left - 6}" y="{sy(t) + 4:.1f}" text-anchor="end">{str(t).replace("-", "−")}</text>')
    years = {}
    for k, r in enumerate(ROWS):
        years.setdefault(r["start_utc"][:4], k)
    for y, k in years.items():
        o.append(f'<text class="c-tick" x="{sx(k):.1f}" y="{top + ph + 16}" text-anchor="start">{y}</text>')
    o.append(f'<text class="c-axis" x="{left}" y="{H - 6}">The 58 events in date order. Each step adds one event&#39;s score to the running total.</text>')
    bench = f"M{sx(0):.1f},{sy(0):.1f} L{sx(n):.1f},{sy(0.33 * n):.1f}"
    o.append(f'<path class="c-path-open" d="{bench}"/>')
    line = lambda v: "M" + f"{sx(0):.1f},{sy(0):.1f} L" + " L".join(f"{sx(k + 1):.1f},{sy(x):.1f}" for k, x in enumerate(v))
    o.append(f'<path class="c-line-ctx" d="{line(co)}"/>')
    o.append(f'<path class="c-line" d="{line(ev)}"/>')
    o.append(f'<text class="c-label-sm" x="{right + 6}" y="{sy(0.33 * n) + 4:.1f}">what the project&#39;s</text>')
    o.append(f'<text class="c-label-sm" x="{right + 6}" y="{sy(0.33 * n) + 18:.1f}">record predicts</text>')
    o.append(f'<text class="c-label-sm" x="{right + 6}" y="{sy(ev[-1]) - 4:.1f}">events</text>')
    o.append(f'<text class="c-label-sm" x="{right + 6}" y="{sy(co[-1]) + 12:.1f}">control days</text>')
    for k, r in enumerate(ROWS):
        name = r["event"].split(" (NOAA")[0]
        tip = esc(f"{name}|Event score {num(float(r['z']))}|Control day {num(float(r['control_z'])) if r['control_z'] else 'not scored'}|Running total {num(ev[k], 1)}; controls {num(co[k], 1)}")
        o.append(f'<g class="c-mark" tabindex="0" data-tip="{tip}"><rect class="c-hit" x="{sx(k):.1f}" y="{top}" width="{sx(1) - sx(0):.1f}" height="{ph}"/></g>')
    o.append("</svg>")
    figure("cumulative", "Running total of scores over the 58 events", "\n".join(o),
           "If world events moved the network as the project reports, the copper line should climb along the dotted one. "
           "It drifts down instead, and the grey line, the same hours a week away from each event, drifts down with it. "
           "The two end within a whisker of each other. Hover or focus for each event.")


def tiles():
    v = S["all"]
    t = [(str(v["events"]["n"]), "events after the project's formal series ended, chosen by rule"),
         (num(v["events"]["z"]), f"their combined score; the project's record predicts {num(v['verdicts']['predicted_at_benchmark'], 1)}"),
         (num(v["controls"]["z"]), "the combined score of ordinary days a week away"),
         (f"{v['paired']['events_higher']} of {v['paired']['pairs']}", "events that scored higher than their control day: a coin toss")]
    (OUT / "tiles.html").write_text('<div class="tiles">\n' + "\n".join(
        f'<div class="tile"><p class="tile-value">{esc(a)}</p><p class="tile-label">{esc(b)}</p></div>' for a, b in t) + "\n</div>\n")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    tiles()
    cumulative()
    print("wrote", ", ".join(sorted(p.name for p in OUT.iterdir())))


if __name__ == "__main__":
    main()
