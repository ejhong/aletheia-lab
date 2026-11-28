#!/usr/bin/env python3
"""Draw the figures for the site page from the results file. Reads results only; recomputes nothing.

    cd questions/indus-script && python analysis/make_figures.py      # writes site/figures/indus-script/*.html
"""
import html
import json
import pathlib

Q = pathlib.Path(__file__).resolve().parent.parent
ROOT = Q.parent.parent
OUT = ROOT / "site" / "figures" / "indus-script"
S = json.load(open(Q / "results" / "contest_summary.json", encoding="utf-8"))
L, A = S["lists"], S["answers"]
esc = lambda s: html.escape(str(s), quote=True)
num = lambda x, d=0: f"{x:+.{d}f}".replace("-", "−")

NAMES = {"tamil_preprint": "Old Tamil, the preprint's own list", "sanskrit_preprint": "Vedic Sanskrit, the preprint's list",
         "akkadian_preprint": "Akkadian, the preprint's list", "tamil_fresh_a": "Old Tamil, fresh list A",
         "tamil_fresh_b": "Old Tamil, fresh list B", "japanese": "Old Japanese", "greek": "Homeric Greek",
         "old_english": "Old English", "hebrew": "Biblical Hebrew", "nahuatl": "Classical Nahuatl",
         "sumerian": "Sumerian", "hawaiian": "Hawaiian", "finnish": "Finnish"}
FRESH = [k for k in ("tamil_fresh_a", "tamil_fresh_b") if k in L]
CONTROLS = [k for k in A.get("controls_run", []) if k in L]
PREPRINT = ["tamil_preprint", "sanskrit_preprint", "akkadian_preprint"]
SHOWN = [k for k in PREPRINT + FRESH + CONTROLS if k in L]


def figure(name, title, svg, caption):
    (OUT / f"{name}.html").write_text(f'<figure class="fig" aria-label="{esc(title)}">\n<div class="fig-scroll">\n{svg}\n</div>\n'
                                      f'<figcaption>{caption}</figcaption>\n</figure>\n', encoding="utf-8")


def tiles():
    passes = A.get("passes", {})
    passing = [k for k in CONTROLS if passes.get(k)]
    top = max(passing, key=lambda k: L[k]["main"]["mean"]) if passing else None
    t = [("80 of 80", "of the preprint's archived runs reproduced exactly by a program written afresh from its method", False),
         (f"{len(passing)} of {len(CONTROLS)}", "languages with no claim on the Indus seals that pass the preprint's own contest: "
          + " and ".join(NAMES[k] for k in sorted(passing, key=lambda k: -L[k]["main"]["mean"])), False)]
    if top:
        t.append((f"{num(L[top]['main']['mean'])} → {num(L[top]['jar sign left unread']['mean'])}",
                  f"{NAMES[top]}'s score with the commonest sign read, and with that one sign left unread", False))
    word = "Incomplete" if A.get("overall", "").startswith("INCOMPLETE") else A.get("overall", "").split(":")[0].capitalize()
    t.append((word, "by the plan's own rule: no fresh Tamil list passed its check, so the main question was not answered as planned", True))
    (OUT / "tiles.html").write_text('<div class="tiles">\n' + "\n".join(
        f'<div class="tile"><p class="tile-value{" is-word" if w else ""}">{esc(v)}</p><p class="tile-label">{esc(l)}</p></div>'
        for v, l, w in t) + "\n</div>\n", encoding="utf-8")


def bars(name, analysis, title, axis_label, caption, count_label):
    """One horizontal bar a list, sorted by mean, for one analysis."""
    rows = sorted(SHOWN, key=lambda k: -L[k][analysis]["mean"])
    vals = [L[k][analysis]["mean"] for k in rows]
    lo, hi = min(0, min(vals)), max(vals)
    step = 50 if hi - lo <= 400 else 100
    x_lo, x_hi = step * int(lo // step) - (step if lo < 0 and lo % step else 0), step * (int(hi // step) + 1)
    if lo < 0 and x_lo > lo:
        x_lo -= step
    W, left, right, top, rh = 720, 236, 600, 26, 26
    H = top + rh * len(rows) + 44
    sx = lambda v: left + (v - x_lo) / (x_hi - x_lo) * (right - left)
    o = [f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(title)}" xmlns="http://www.w3.org/2000/svg">']
    for t in range(x_lo, x_hi + 1, step):
        o.append(f'<line class="{"c-zero" if t == 0 else "c-grid"}" x1="{sx(t):.1f}" x2="{sx(t):.1f}" y1="{top - 6}" y2="{top + rh * len(rows)}"/>')
        o.append(f'<text class="c-tick" x="{sx(t):.1f}" y="{top + rh * len(rows) + 15}" text-anchor="middle">{num(t) if t else "0"}</text>')
    if analysis == "main" and "floor" in A:
        fx = sx(A["floor"])
        o.append(f'<line class="c-ref" x1="{fx:.1f}" x2="{fx:.1f}" y1="{top - 6}" y2="{top + rh * len(rows)}"/>')
        o.append(f'<text class="c-label-sm" x="{fx + 4:.1f}" y="{top - 10}">pass line</text>')
    for i, k in enumerate(rows):
        m = L[k][analysis]
        y = top + rh * i
        tamil = k in FRESH or k == "tamil_preprint"
        x0, x1 = sorted((sx(0), sx(m["mean"])))
        o.append(f'<text class="c-label-sm" x="{left - 8}" y="{y + 17}" text-anchor="end">{esc(NAMES.get(k, k))}</text>')
        o.append(f'<rect class="c-bar{" is-on" if tamil else ""}" x="{x0:.1f}" y="{y + 5}" width="{max(1.0, x1 - x0):.1f}" height="15" rx="2"/>')
        o.append(f'<text class="c-sub" x="{right + 8}" y="{y + 17}">{num(m["mean"])} · {m["runs_above_control"]} {count_label}</text>')
    o.append(f'<text class="c-axis" x="{left}" y="{H - 6}">{esc(axis_label)}</text>')
    o.append("</svg>")
    figure(name, title, "\n".join(o), caption)


def carried():
    """For each list: the main score, the score with the jar sign unread, and with the pictures shuffled."""
    rows = sorted([k for k in SHOWN if k not in ("sanskrit_preprint", "akkadian_preprint")], key=lambda k: -L[k]["main"]["mean"])
    series = [("main", "as the contest is run", "c-dot"), ("jar sign left unread", "commonest sign left unread", "c-dot c-ctx"),
              ("pictures shuffled", "pictures moved to wrong signs", "c-dot c-hollow")]
    vals = [L[k][a]["mean"] for k in rows for a, _, _ in series]
    lo, hi = min(0, min(vals)), max(vals)
    step = 50 if hi - lo <= 400 else 100
    x_lo, x_hi = step * (int(lo // step) - (1 if lo < 0 else 0)), step * (int(hi // step) + 1)
    W, left, right, top, rh = 720, 236, 660, 44, 26
    H = top + rh * len(rows) + 40
    sx = lambda v: left + (v - x_lo) / (x_hi - x_lo) * (right - left)
    title = "What carries each list's score"
    o = [f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(title)}" xmlns="http://www.w3.org/2000/svg">']
    for j, (_, label, cls) in enumerate(series):
        x = (left - 150) + (0, 160, 370)[j]
        o.append(f'<circle class="{cls}" style="opacity:1" cx="{x}" cy="14" r="5"/>')
        o.append(f'<text class="c-label-sm" x="{x + 10}" y="18">{esc(label)}</text>')
    for t in range(x_lo, x_hi + 1, step):
        o.append(f'<line class="{"c-zero" if t == 0 else "c-grid"}" x1="{sx(t):.1f}" x2="{sx(t):.1f}" y1="{top - 6}" y2="{top + rh * len(rows)}"/>')
        o.append(f'<text class="c-tick" x="{sx(t):.1f}" y="{top + rh * len(rows) + 15}" text-anchor="middle">{num(t) if t else "0"}</text>')
    for i, k in enumerate(rows):
        y = top + rh * i + 13
        pts = [sx(L[k][a]["mean"]) for a, _, _ in series]
        o.append(f'<line class="c-grid" x1="{min(pts):.1f}" x2="{max(pts):.1f}" y1="{y}" y2="{y}"/>')
        o.append(f'<text class="c-label-sm" x="{left - 8}" y="{y + 4}" text-anchor="end">{esc(NAMES.get(k, k))}</text>')
        for (a, _, cls), x in zip(series, pts):
            o.append(f'<circle class="{cls}" style="opacity:1" cx="{x:.1f}" cy="{y}" r="5"/>')
    o.append(f'<text class="c-axis" x="{left}" y="{H - 6}">Score: real names minus the same names scrambled (mean)</text>')
    o.append("</svg>")
    figure("what_carries", title, "\n".join(o),
           "Each list scored three ways. Solid copper: the contest as the preprint runs it. Grey: with the commonest sign, the jar, "
           "left unread. Ring: with each sign given another sign's picture words. Where the ring sits near the solid dot, the "
           "score does not come from what the signs show. Where the grey dot falls far below, one sign carries the score.")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    tiles()
    bars("contest", "main", "The contest: real names against scrambled names, list by list",
         "Score: real names minus the same names scrambled (mean of 100 rounds)",
         "Every list in the locked run through the preprint's contest. Copper: the preprint's own Old Tamil list, sampled to 600 "
         "names. Grey: the preprint's Sanskrit and Akkadian lists and the seven control languages built for this study. After each "
         "bar: the mean score, and the number of the 100 rounds in which real names beat scrambled ones. A list passes at 80 rounds "
         "and a score right of the pass line.",
         "of 100")
    bars("shuffled", "pictures shuffled", "The same contest with the pictures on the wrong signs",
         "Score with each sign given another sign's picture words (mean of 200 runs)",
         "The same lists with every sign's picture words dealt to another sign, 20 shuffles of 10 rounds each. If the readings "
         "depended on what the signs depict, these scores would fall to nothing.",
         "of 200")
    carried()
    print("wrote figures to", OUT)


if __name__ == "__main__":
    main()
