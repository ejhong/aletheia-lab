#!/usr/bin/env python3
"""Draw the figures for the site page from the results files. Standard library only.

    python3 questions/population-y/analysis/make_figures.py      # writes site/figures/population-y/*.html

Each output is an HTML fragment (inline SVG plus a caption) that scripts/build_site.py drops into the page where
the content file says {{figure: population-y/<name>}}. Colours come from the site's CSS variables, so the figures
follow light and dark mode. Every value shown is also in RESULTS.md; hovering or focusing a mark shows its numbers.
"""
import csv
import html
import json
import pathlib

Q = pathlib.Path(__file__).resolve().parent.parent
ROOT = Q.parent.parent
OUT = ROOT / "site" / "figures" / "population-y"
F4 = {r["id"]: r for r in csv.DictReader(open(Q / "results" / "amended" / "f4.tsv"), delimiter="\t")}
V = json.load(open(Q / "results" / "amended" / "verdicts.json"))


def esc(s):
    return html.escape(str(s), quote=True)


def num(x, digits=2):
    return f"{x:.{digits}f}".replace("-", "−")


def tip(*lines):
    return esc("|".join(lines))


def interval_chart(rows, x0, x1, ticks, axis_title, value_fmt, refs=(), width=720, label_w=268, right_w=64, name="chart"):
    """Rows of dot-and-interval marks. rows: dicts with label, est, lo, hi, z, tip, and optional head/hollow/sub."""
    left, right = label_w + 14, width - right_w - 8
    row_h, top = 30, 34
    y, items = top, []
    for r in rows:
        if r.get("head"):
            y += 26 if items else 12
            items.append(("head", y, r))
            y += 14
        else:
            items.append(("row", y + row_h / 2, r))
            y += row_h
    plot_bottom = y + 4
    height = plot_bottom + 44
    sx = lambda v: left + (v - x0) / (x1 - x0) * (right - left)
    o = [f'<svg class="chart" viewBox="0 0 {width} {height}" role="img" aria-label="{esc(name)}" '
         f'xmlns="http://www.w3.org/2000/svg">']
    for t in ticks:
        o.append(f'<line class="c-grid" x1="{sx(t):.1f}" x2="{sx(t):.1f}" y1="{top - 6}" y2="{plot_bottom}"/>')
        o.append(f'<text class="c-tick" x="{sx(t):.1f}" y="{plot_bottom + 16}" text-anchor="middle">{num(t, 1 if t % 1 else 0)}</text>')
    for v, cls, text, anchor in refs:
        o.append(f'<line class="c-{cls}" x1="{sx(v):.1f}" x2="{sx(v):.1f}" y1="{top - 6}" y2="{plot_bottom}"/>')
        if text:
            dx = 6 if anchor == "start" else -6
            o.append(f'<text class="c-ref-label" x="{sx(v) + dx:.1f}" y="{top - 12}" text-anchor="{anchor}">{esc(text)}</text>')
    o.append(f'<text class="c-axis" x="{(left + right) / 2:.1f}" y="{plot_bottom + 36}" text-anchor="middle">{esc(axis_title)}</text>')
    o.append(f'<text class="c-col" x="{width - 6}" y="{top - 12}" text-anchor="end">Z</text>')
    for kind, cy, r in items:
        if kind == "head":
            o.append(f'<text class="c-group" x="0" y="{cy}">{esc(r["head"])}</text>')
            continue
        lo, hi, est = max(r["lo"], x0), min(r["hi"], x1), r["est"]
        o.append(f'<g class="c-mark" tabindex="0" data-tip="{r["tip"]}">')
        o.append(f'<rect class="c-hit" x="0" y="{cy - row_h / 2:.1f}" width="{width}" height="{row_h}"/>')
        o.append(f'<text class="c-label" x="0" y="{cy + 4:.1f}">{esc(r["label"])}</text>')
        if r.get("sub"):
            o.append(f'<text class="c-sub" x="{label_w}" y="{cy + 4:.1f}" text-anchor="end">{esc(r["sub"])}</text>')
        o.append(f'<line class="c-whisker" x1="{sx(lo):.1f}" x2="{sx(hi):.1f}" y1="{cy:.1f}" y2="{cy:.1f}"/>')
        cls = "c-dot c-hollow" if r.get("hollow") else "c-dot"
        o.append(f'<circle class="{cls}" cx="{sx(est):.1f}" cy="{cy:.1f}" r="5"/>')
        o.append(f'<text class="c-value" x="{width - 6}" y="{cy + 4:.1f}" text-anchor="end">{num(r["z"], 1)}</text>')
        o.append("</g>")
    o.append("</svg>")
    return "\n".join(o)


def figure(name, title, svg, caption):
    body = (f'<figure class="fig" aria-label="{esc(title)}">\n<div class="fig-scroll">\n{svg}\n</div>\n'
            f'<figcaption>{caption}</figcaption>\n</figure>\n')
    (OUT / f"{name}.html").write_text(body)


def tests_figure():
    def row(key, label, sub=None, hollow=False):
        r = F4[key]
        est, lo, hi, z = float(r["f4"]) * 1000, float(r["ci_lo"]) * 1000, float(r["ci_hi"]) * 1000, float(r["Z"])
        return {"label": label, "sub": sub, "est": est, "lo": lo, "hi": hi, "z": z, "hollow": hollow,
                "tip": tip(label, f"{num(est)} (95% interval {num(lo)} to {num(hi)})", f"Z = {num(z)}",
                           f"{int(r['n_snps']):,} SNPs")}

    rows = [
        {"head": "The excess toward Papuans"},
        row("P_A", "Suruí and Karitiana together", "primary test"),
        row("Pcommunity.A|A.Surui", "Suruí alone"),
        row("Pcommunity.A|A.Karitiana", "Karitiana alone"),
        row("P_B.heldout", "26 other donors", "vs Pima"),
        row("P_B.unrel", "Close relatives removed", "vs Pima"),
        {"head": "Swap Papuans for another group"},
        row("Pong.A", "Andaman Islanders (Onge)"),
        row("L1.A", "Tianyuan, China, 40,000 years old"),
        row("Han.A", "Han Chinese", "control", hollow=True),
        {"head": "After subtracting the Han control"},
        row("L3.A", "Compared with the Mixe"),
        row("L3.B", "Compared with the Pima"),
    ]
    svg = interval_chart(rows, -0.5, 2.25, [0, 0.5, 1, 1.5, 2], "Extra allele sharing with the Amazonians (f4 × 1,000), with 95% interval",
                         num, refs=[(0, "zero", "", "start")], name="Estimates of the excess, with intervals")
    figure("tests", "The excess, tested several ways",
           svg,
           "Each dot is one test; the bar is its 95% interval. A dot to the right of zero means the Amazonians share more "
           "alleles with that group than the comparison group does. Z is the estimate divided by its uncertainty; "
           "geneticists usually ask for 3 or more. The first eight tests compare with the Mixe unless marked. "
           "The hollow dot is a control that should sit near zero if the excess were specific to Australasians.")


def world_figure():
    width, left, right = 720, 14, 706
    x0, x1 = -0.8, 4.8
    sx = lambda v: left + (v - x0) / (x1 - x0) * (right - left)
    highlight = {"W.Papuan": "Papuan", "W.Australian": "Australian", "W.ONG": "Onge", "W.JAR": "Jarawa", "W.Nasioi": "Nasioi"}
    control = {"W.Han": "Han"}
    panels = [("A", "Compared with the Mixe"), ("B", "Compared with the Pima")]
    r_dot, step, bin_w = 3.1, 7.0, 0.12
    o, y = [], 0
    blocks = []
    for pn, title in panels:
        groups = sorted(((k.split("|")[1], float(F4[k]["Z"])) for k in F4 if k.startswith(f"S.{pn}|")), key=lambda t: t[1])
        stacks, placed = {}, []
        for name, z in groups:
            b = round(z / bin_w)
            lvl = stacks.get(b, 0)
            stacks[b] = lvl + 1
            placed.append((name, z, b * bin_w, lvl))
        blocks.append((pn, title, placed, max(stacks.values())))
    for pn, title, placed, tallest in blocks:
        labels = sorted(((n, z, xb, lvl) for n, z, xb, lvl in placed if n in highlight or n in control), key=lambda t: (t[2], t[3]))
        # One row of labels above the pile, pushed apart so none overlap, each joined to its dot by an elbow line.
        lab = []
        for n, z, xb, lvl in labels:
            text = highlight.get(n) or control[n]
            lab.append({"n": n, "text": text, "w": 6.3 * len(text) + 12, "x": sx(xb), "dot_x": sx(xb), "lvl": lvl})
        for _ in range(200):
            moved = False
            for a, b in zip(lab, lab[1:]):
                need = (a["w"] + b["w"]) / 2
                if b["x"] - a["x"] < need:
                    shift = (need - (b["x"] - a["x"])) / 2
                    a["x"] -= shift
                    b["x"] += shift
                    moved = True
            if not moved:
                break
        over = max(0, lab[-1]["x"] + lab[-1]["w"] / 2 - right)
        for l in lab:
            l["x"] -= over
        top = y + 26
        label_base = top + 12
        elbow = label_base + 16
        base = elbow + 10 + tallest * step
        o.append(f'<text class="c-group" x="0" y="{y + 12}">{esc(title)}</text>')
        for t in range(0, 5):
            o.append(f'<line class="c-grid" x1="{sx(t):.1f}" x2="{sx(t):.1f}" y1="{elbow + 4}" y2="{base + 6}"/>')
            o.append(f'<text class="c-tick" x="{sx(t):.1f}" y="{base + 20}" text-anchor="middle">{t}</text>')
        o.append(f'<line class="c-zero" x1="{sx(0):.1f}" x2="{sx(0):.1f}" y1="{elbow + 4}" y2="{base + 6}"/>')
        o.append(f'<line class="c-grid" x1="{left}" x2="{right}" y1="{base + 6}" y2="{base + 6}"/>')
        for n, z, xb, lvl in placed:
            cy = base - lvl * step
            cls = "c-dot" if n in highlight else ("c-dot c-hollow" if n in control else "c-dot c-ctx")
            r = 4.2 if n in highlight or n in control else r_dot
            nice = highlight.get(n) or control.get(n) or n[2:].replace("_", " ")
            o.append(f'<g class="c-mark" tabindex="0" data-tip="{tip(nice, "Z = " + num(z))}">'
                     f'<circle class="c-hit" cx="{sx(xb):.1f}" cy="{cy:.1f}" r="9"/>'
                     f'<circle class="{cls}" cx="{sx(xb):.1f}" cy="{cy:.1f}" r="{r}"/></g>')
        seen = {}
        for l in lab:
            cy = base - l["lvl"] * step
            k = seen.get(round(l["dot_x"]), 0)
            seen[round(l["dot_x"])] = k + 1
            dx = l["dot_x"] + 2.5 * k  # two labelled dots in one column get separate lines
            o.append(f'<polyline class="c-leader" points="{dx:.1f},{cy - 6:.1f} {dx:.1f},{elbow:.1f} {l["x"]:.1f},{label_base + 4:.1f}"/>')
            o.append(f'<text class="c-label-sm" x="{l["x"]:.1f}" y="{label_base}" text-anchor="middle">{esc(l["text"])}</text>')
        y = base + 38
    o.append(f'<text class="c-axis" x="{(left + right) / 2:.1f}" y="{y}" text-anchor="middle">'
             'Z-score: how strongly the Amazonians lean toward each population, relative to the comparison group</text>')
    height = y + 12
    svg = (f'<svg class="chart" viewBox="0 0 {width} {height}" role="img" aria-label="Lean of the Amazonians toward 145 world '
           f'populations" xmlns="http://www.w3.org/2000/svg">\n' + "\n".join(o) + "\n</svg>")
    figure("world", "Who the Amazonians lean toward: 145 world populations", svg,
           "Each dot is one present-day population from outside the Americas. Filled dots are the five Australasian "
           "groups; the hollow dot is Han Chinese. Compared with the Mixe, the Australasians sit at the top of the pile. "
           "Compared with the Pima, they are mixed in with East Asians. In both panels almost every population sits to "
           "the right of zero: part of what is measured is a general lean, not something specific to Australasians.")


def ancient_figure():
    pa = float(F4["P_A"]["f4"])
    sets = [("ANC.SA", "All of ancient South America"), ("REGION.ANDES_COAST", "Central Andes, Pacific coast"),
            ("REGION.ANDES_INLAND", "Central Andes, inland"), ("REGION.EAST_SA", "Brazil, Paraguay, Uruguay"),
            ("REGION.SOUTH_CONE", "Southern Cone"), ("REGION.ISTHMO_NSA", "Isthmus and northern South America"),
            ("REGION.CARIB", "Caribbean")]
    rows = [{"head": "Ancient groups"}]
    for key, label in sets:
        r = F4[f"M1|{key}@AG"]
        n = V["N"]["sets"][key]["types"]["AG"]["n"]
        est, lo, hi, z = float(r["f4"]) / pa, float(r["ci_lo"]) / pa, float(r["ci_hi"]) / pa, float(r["Z"])
        rows.append({"label": label, "sub": f"{n} people", "est": est, "lo": lo, "hi": hi, "z": z,
                     "tip": tip(label, f"{num(est)} of today's excess (95% interval {num(lo)} to {num(hi)})",
                                f"Z = {num(z)}", f"{n} capture genomes")})
    svg = interval_chart(rows, -0.6, 1.2, [-0.5, 0, 0.5, 1], "Excess over the ancient northern baseline, as a share of today's Amazonian excess",
                         num, refs=[(0, "zero", "no excess", "end"), (1, "ref", "today's Suruí and Karitiana", "end")],
                         label_w=300, name="Ancient groups compared with the ancient northern baseline")
    figure("ancient", "Ancient Americans: no group stands out", svg,
           "Each ancient group is compared with 137 ancient people from North America and Mesoamerica whose DNA was "
           "prepared the same way. Zero means no more of the excess than they have. One would be the full excess seen in "
           "today's Suruí and Karitiana. Every group sits near zero and well short of one. Scaled by the point estimate "
           "of today's excess; capture data only.")


def tiles():
    t = [("4.2", "Z-score of the primary test. The usual bar is 3."),
         ("97%", "of 216 method variants point the same way"),
         ("3", "independent programs, from three AI vendors, gave the same numbers"),
         ("0 of 58", "ancient American groups stand out for it")]
    body = '<div class="tiles">\n' + "\n".join(
        f'<div class="tile"><p class="tile-value">{esc(v)}</p><p class="tile-label">{esc(l)}</p></div>' for v, l in t) + "\n</div>\n"
    (OUT / "tiles.html").write_text(body)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    tiles()
    tests_figure()
    world_figure()
    ancient_figure()
    print("wrote", ", ".join(sorted(p.name for p in OUT.iterdir())))


if __name__ == "__main__":
    main()
