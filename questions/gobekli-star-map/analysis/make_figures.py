#!/usr/bin/env python3
"""Draw the figures for the site page from the results files. Reads results only; recomputes nothing.

    cd questions/gobekli-star-map && python analysis/make_figures.py
        # reads results/summary.json and results/mean_ranks.tsv
        # writes site/figures/gobekli-star-map/{tiles,matches,ranks}.html
        # and copies the 20 pictures, reduced to 160 px wide, to site/assets/figures/gobekli-star-map/

    --results DIR   read the results files from DIR instead (for testing)
    --out DIR       write the HTML fragments to DIR instead (for testing; the pictures still go to site/assets)

A question page sits at _site/questions/<slug>/index.html and the build copies site/assets/ to _site/assets/, so the
fragments refer to the pictures as ../../assets/figures/gobekli-star-map/<id>.png. Needs Pillow for the pictures.
"""
import argparse
import csv
import html
import json
import pathlib

from PIL import Image

Q = pathlib.Path(__file__).resolve().parent.parent
ROOT = Q.parent.parent
SLUG = "gobekli-star-map"
IMG_DIR = ROOT / "site" / "assets" / "figures" / SLUG
IMG_URL = f"../../assets/figures/{SLUG}/"
IMG_WIDTH = 160

FIGURES = [f"A{k:02d}" for k in range(1, 9)]
SYMBOLS = [f"S{k:02d}" for k in range(1, 13)]
CONSTELLATION = dict(zip(FIGURES, ["Scorpius", "Pisces", "Libra", "Lupus", "Sagittarius", "Ophiuchus", "Virgo", "Gemini"]))
ANIMAL = dict(zip(SYMBOLS, ["scorpion", "bending bird", "duck or goose", "dog or wolf", "eagle or vulture",
                            "bending bird with fish", "frog", "ibex or rat", "aurochs", "boar", "lion or leopard", "fox"]))
VENDOR = {"openai": "OpenAI", "google": "Google", "xai": "xAI"}
CREDIT = ("Pictures from Sweatman and Tsikritsis (2017), Table 1, CC BY 4.0; line drawings reduced to black lines by us.")

esc = lambda s: html.escape(str(s), quote=True)
r1 = lambda x: f"{x:.1f}"


def ordinal(n):
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def one_in(x):
    """A probability as "1 in N", N rounded to two significant figures (millions spelled out)."""
    n = 1 / x
    if n >= 1e6:
        return f"1 in {n / 1e6:.0f} million" if n >= 1e7 else f"1 in {n / 1e6:.1f} million".replace(".0 ", " ")
    if n >= 100:
        k = len(str(int(n))) - 2
        return f"1 in {int(round(n, -k)):,}"
    return f"1 in {n:.0f}" if n >= 10 else f"1 in {n:.1f}".replace(".0", "")


def words(n):
    return {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six"}.get(n, str(n))


# ---------------------------------------------------------------------------------------------------------------------
DESCRIBED, NOTE = False, ""


def tiles(S, out):
    pooled = S["pooled"]
    ws = pooled["task_a"]["without_scorpion"]
    pair = ws["among_pillar_7"]
    total, hits = pair["assignments"], pair["as_good_or_better"]
    formula = pooled["task_a"]["all8"]["papers_formula"]["no_repeats"]
    judges = pooled["judges"]
    vendors = ", ".join(VENDOR.get(v, v) for v in judges)
    if formula < 1:
        c_value, c_label = one_in(formula), ("the paper's chance of a coincidence, from its own formula fed the judges' "
                                             "ranks. The paper's figure is 1 in 5 million")
    else:
        c_value, c_label = "More than 1", (f"what the paper's own formula gives when fed the judges' ranks ({formula:,.1f}): "
                                           "no longer a chance of anything. The paper's figure is 1 in 5 million")
    n_out = len(S.get("excluded", {}))
    if DESCRIBED:      # no judge passed the competence check; the numbers describe the rankings with the check off
        passed = sum(j["scorpion_mean_rank"] <= 2.0 for j in S["judges"].values())
        items = [
            (f"{passed} of {len(judges)}", "judges put the scorpion photograph first or second for the scorpion figure, the check "
             "each had to pass. So by our own rule the test could not be scored", False),
            (f"{ws['claimed_sole_best_count']} of 7", "other figures for which the judges' best match is the paper's animal. "
             "The paper ranks six of these seven first", False),
            (f"{hits:,} in {total:,}", "shuffled pairings of figures and pillar animals do as well as the paper's pairing, "
             "by the judges' ranks. With no link, about half would", True),
            ("3 of 3", "judges, asked afterwards, named the site and knew of the paper's claim. None reproduced it", False)]
    else:
        items = [
            (f"{ws['claimed_sole_best_count']} of 7", "constellation figures for which the judges' best match is the paper's "
             "animal, scorpion set aside. The paper ranks six of these seven first", False),
            (f"{hits:,} in {total:,}", f"shuffled pairings of these figures with the pillar's animals that do as well as the "
             f"paper's. With no link, about half would; {int(0.01 * total):,} or fewer beats chance", True),
            (c_value, c_label, True),
            (str(len(judges)), f"vision models counted as judges ({vendors})"
             + (f"; {n_out} left out" if n_out else ""), False)]
    (out / "tiles.html").write_text('<div class="tiles">\n' + "\n".join(
        f'<div class="tile"><p class="tile-value{" is-word" if word else ""}">{esc(v)}</p><p class="tile-label">{esc(l)}</p></div>'
        for v, l, word in items) + "\n</div>\n")


# ---------------------------------------------------------------------------------------------------------------------
STYLE = """<style>
.gsm-rows { min-width: 30rem; }
.gsm-row { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) minmax(0, 1fr) 6.5rem; gap: 0 1rem;
  align-items: center; padding: .8rem .25rem; border-top: 1px solid var(--line); }
.gsm-row:first-child { border-top: 0; }
.gsm-head { padding-block: 0 .5rem; font: 500 10.5px/1.4 var(--mono); letter-spacing: .12em; text-transform: uppercase; color: var(--faint); }
.gsm-row.is-premise { background: color-mix(in oklab, var(--paper-deep) 70%, transparent); }
.gsm-cell { display: flex; align-items: center; gap: .7rem; min-width: 0; }
.gsm-pics { display: flex; flex: none; gap: .3rem; }
.gsm-pics.is-many img { width: 3.6rem; height: 3.6rem; }
.gsm-cell img { flex: none; width: 5.5rem; height: 5.5rem; object-fit: contain; background: #fff; border: 1px solid var(--line); }
.gsm-text { min-width: 0; font-size: .84rem; line-height: 1.4; color: var(--ink-soft); }
.gsm-name { display: block; font: 400 1.02rem/1.25 var(--serif); color: var(--ink); }
.gsm-tag { display: inline-block; margin-top: .3rem; font: 500 10px/1.35 var(--mono); letter-spacing: .1em; text-transform: uppercase; color: var(--faint); }
.gsm-mark { font: 500 10.5px/1.35 var(--mono); letter-spacing: .1em; text-transform: uppercase; }
.gsm-mark span { display: inline-block; width: 1.3rem; font: 600 1.05rem/1 var(--sans); letter-spacing: 0; }
.gsm-mark.is-yes { color: var(--verdigris); }
.gsm-mark.is-tie { color: var(--ochre); }
.gsm-mark.is-no { color: var(--copper); }
.gsm-ranks { min-width: 44rem; table-layout: fixed; font-size: .8rem; font-variant-numeric: tabular-nums; }
.gsm-ranks col.gsm-first { width: 6.6rem; }
.gsm-ranks th { padding: .45rem .2rem; text-align: center; vertical-align: bottom; letter-spacing: .06em; line-height: 1.3; font-size: 9.5px; }
.gsm-ranks th:first-child, .gsm-ranks td:first-child { text-align: left; padding-left: .5rem; }
.gsm-ranks td { padding: .5rem .2rem; text-align: center; vertical-align: middle; color: var(--ink); }
.gsm-ranks td.is-best { font-weight: 700; }
.gsm-ranks td.is-claim { outline: 2px solid var(--ink); outline-offset: -3px; }
.gsm-ranks tr.is-premise td:first-child { color: var(--faint); }
@media (max-width: 40rem) {
  .gsm-rows { min-width: 0; }
  .gsm-row { grid-template-columns: repeat(3, minmax(0, 1fr)) 3.6rem; gap: 0 .6rem; align-items: start; }
  .gsm-cell { flex-direction: column; align-items: flex-start; gap: .35rem; }
  .gsm-cell img { width: 4.5rem; height: 4.5rem; }
  .gsm-pics { flex-wrap: wrap; }
  .gsm-pics.is-many img { width: 2.6rem; height: 2.6rem; }
  .gsm-text { font-size: .76rem; }
  .gsm-name { font-size: .92rem; }
  .gsm-head { font-size: 9.5px; letter-spacing: .08em; }
  .gsm-mark { font-size: 9.5px; letter-spacing: .06em; padding-top: 1.6rem; }
}
</style>
"""


def read_pooled(path):
    rows = {r["figure"]: {s: float(r[s]) for s in SYMBOLS}
            for r in csv.DictReader(open(path, encoding="utf-8"), delimiter="\t") if r["table"] == "pooled"}
    assert sorted(rows) == FIGURES, "mean_ranks.tsv must have a pooled row for each of A01..A08"
    return rows


def copy_pictures():
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    for folder, ids in (("figures", FIGURES), ("symbols_512", SYMBOLS)):
        for i in ids:
            im = Image.open(Q / "stimuli" / folder / f"{i}.png").convert("RGB")
            im = im.resize((IMG_WIDTH, round(im.height * IMG_WIDTH / im.width)), Image.LANCZOS)
            im.save(IMG_DIR / f"{i}.png", optimize=True)


def img(i, alt):
    return f'<img src="{IMG_URL}{i}.png" width="{IMG_WIDTH}" height="{IMG_WIDTH}" loading="lazy" alt="{esc(alt)}">'


def symbol_alt(s):
    return f"Photograph of the carved {ANIMAL[s]}"


def matches(S, out):
    """Scorpion row from the 12-photograph table; the other seven from the main count (scorpion photograph dropped,
    11 photographs), so the marks agree with that count by construction."""
    a8 = S["pooled"]["task_a"]["all8"]["per_figure"]
    ws = S["pooled"]["task_a"]["without_scorpion"]
    o = [f'<figure class="fig" aria-label="The paper\'s match and the judges\' best match for each constellation figure">',
         STYLE + '<div class="fig-scroll">\n<div class="gsm-rows" role="table" aria-label="Paper\'s match and judges\' best match">',
         '<div class="gsm-row gsm-head" role="row"><span role="columnheader">Constellation figure</span>'
         '<span role="columnheader">The paper\'s match</span><span role="columnheader">The judges\' best match</span>'
         '<span role="columnheader">Same?</span></div>']
    n_same = 0
    for a in FIGURES:
        premise = a == "A01"
        info, of = (a8[a], 12) if premise else (ws["per_figure"][a], 11)
        claim, best = "S" + a[1:], info["best"]
        if info["claimed_is_sole_best"]:
            mark, cls = ("✓", "Same"), "is-yes"
            n_same += not premise
        elif claim in best:
            mark, cls = ("=", "Tied best"), "is-tie"
        else:
            mark, cls = ("×", "Different"), "is-no"
        where = f"mean rank {r1(info['claimed_mean_rank'])} of {of}; {ordinal(info['others_at_least_as_good'] + 1)} of {of}"
        names = " and ".join(ANIMAL[s] for s in best)
        o.append(
            f'<div class="gsm-row{" is-premise" if premise else ""}" role="row">'
            f'<div class="gsm-cell" role="cell">{img(a, f"Line drawing of the stick figure of {CONSTELLATION[a]}")}'
            f'<span class="gsm-text"><span class="gsm-name">{CONSTELLATION[a]}</span>'
            + ('<span class="gsm-tag">The starting point, set aside</span>' if premise else "") + '</span></div>'
            f'<div class="gsm-cell" role="cell">{img(claim, symbol_alt(claim))}<span class="gsm-text">'
            f'<span class="gsm-name">{esc(ANIMAL[claim].capitalize())}</span>{where}</span></div>'
            f'<div class="gsm-cell" role="cell"><span class="gsm-pics{" is-many" if len(best) > 1 else ""}">'
            + "".join(img(s, symbol_alt(s)) for s in best) + '</span><span class="gsm-text">'
            f'<span class="gsm-name">{esc(names.capitalize())}</span>{"tied best" if len(best) > 1 else ""}</span></div>'
            f'<p class="gsm-mark {cls}" role="cell" style="margin:0"><span aria-hidden="true">{mark[0]}</span>{mark[1]}</p></div>')
    assert n_same == ws["claimed_sole_best_count"], "matches figure disagrees with the main count"
    o.append("</div>\n</div>")
    o.append(f"<figcaption>{NOTE}For each constellation stick figure, the animal the paper matches to it and the one the judges "
             f"ranked most like it. The scorpion was the paper's starting point, so the main count sets it aside and "
             f"drops its photograph from every ranking, leaving 11; the other seven rows are on that count, and the "
             f"judges' best is the paper's animal for {words(n_same)} of them. A mean rank is the average place over "
             f"every ranking by every judge: 1 means always first; chance gives 6 among 11 (6.5 among 12). The place "
             f"counts ties against the paper. {esc(CREDIT)}</figcaption>\n</figure>\n")
    (out / "matches.html").write_text("\n".join(o))


def ranks(S, M, out):
    o = ['<figure class="fig" aria-label="Mean rank of each photograph for each constellation figure">',
         STYLE + '<div class="fig-scroll">\n<table class="gsm-ranks"><colgroup><col class="gsm-first"></colgroup>',
         "<thead><tr><th scope=\"col\">Figure</th>"
         + "".join(f'<th scope="col">{esc(ANIMAL[s])}</th>' for s in SYMBOLS) + "</tr></thead>\n<tbody>"]
    for a in FIGURES:
        row = M[a]
        low = min(row.values())
        cells = []
        for s in SYMBOLS:
            v = row[s]
            # Shade by how far the mean rank beats chance (6.5): strong for 1, faint at chance, palest when worse.
            pct = round(10 + (6.5 - v) / 5.5 * 55) if v < 6.5 else round(10 - (v - 6.5) / 5.5 * 10)
            cls = " ".join(c for c, on in (("is-best", abs(v - low) < 1e-9), ("is-claim", s == "S" + a[1:])) if on)
            label = f"{CONSTELLATION[a]}, {ANIMAL[s]}: mean rank {r1(v)}" + (", the paper's match" if s == "S" + a[1:] else "")
            cells.append(f'<td{f" class={chr(34)}{cls}{chr(34)}" if cls else ""} '
                         f'style="background:color-mix(in oklab, var(--copper) {pct}%, transparent)" '
                         f'aria-label="{esc(label)}">{r1(v)}</td>')
        o.append(f'<tr{" class=" + chr(34) + "is-premise" + chr(34) if a == "A01" else ""}>'
                 f'<th scope="row" style="text-align:left;vertical-align:middle;font-size:10px">{CONSTELLATION[a]}</th>'
                 + "".join(cells) + "</tr>")
    o.append("</tbody>\n</table>\n</div>")
    o.append("<figcaption>" + NOTE + "The judges' average place for each photograph (columns) against each stick figure (rows): 1 means "
             "always most similar, 12 always least, 6.5 is chance. The stronger the colour, the better the rank; the paper's match is "
             "outlined and the best in each row is in bold. This table includes the scorpion photograph, so places can differ by one from the picture above.</figcaption>\n</figure>\n")
    (out / "ranks.html").write_text("\n".join(o))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--results", type=pathlib.Path, default=Q / "results")
    ap.add_argument("--out", type=pathlib.Path, default=ROOT / "site" / "figures" / SLUG)
    args = ap.parse_args()
    global DESCRIBED, NOTE
    S = json.load(open(args.results / "summary.json"))
    if "pooled" not in S:        # the locked analysis counted fewer than two judges: draw the description in explore/
        args.results = Q / "explore" / "results"
        S = json.load(open(args.results / "summary.json"))
        DESCRIBED = True
        NOTE = ("No judge passed the scorpion check, so this is a description of what the three judges did, with that "
                "check switched off. It is not a scored result. ")
    M = read_pooled(args.results / "mean_ranks.tsv")
    args.out.mkdir(parents=True, exist_ok=True)
    copy_pictures()
    tiles(S, args.out)
    matches(S, args.out)
    ranks(S, M, args.out)
    print("wrote", ", ".join(sorted(p.name for p in args.out.iterdir())), "and", len(list(IMG_DIR.iterdir())), "pictures in",
          IMG_DIR.relative_to(ROOT))


if __name__ == "__main__":
    main()
