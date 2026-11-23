#!/usr/bin/env python3
"""Draw the figures for the site page from the results files. Standard library only.

    python3 questions/strangers/analysis/make_figures.py      # writes site/figures/strangers/*.html

Each output is an HTML fragment (inline SVG plus a caption) that scripts/build_site.py drops into the page where the
content file says {{figure: strangers/<name>}}. Colours come from the site's CSS variables.
"""
import collections
import csv
import html
import json
import pathlib

Q = pathlib.Path(__file__).resolve().parent.parent
ROOT = Q.parent.parent
OUT = ROOT / "site" / "figures" / "strangers"
R = Q / "results" / "corrected"
esc = lambda s: html.escape(str(s), quote=True)
num = lambda x, d=1: f"{x:.{d}f}".replace("-", "−")

CLASS_TEXT = {"known": "already known to be there", "metadata error": "a recording error", "not specific": "shared Ice Age ancestry, not American",
              "unlike neighbours": "unlike the neighbours, not American", "not robust": "did not survive the checks", "standing": "unexplained"}


def figure(name, title, svg, caption, legend=""):
    (OUT / f"{name}.html").write_text(f'<figure class="fig" aria-label="{esc(title)}">\n{legend}<div class="fig-scroll">\n{svg}\n</div>\n'
                                      f'<figcaption>{caption}</figcaption>\n</figure>\n')


def world_map():
    W, lat0, lat1 = 720, 80.0, -58.0
    H = round(W * (lat0 - lat1) / 360)
    px = lambda lon: (lon + 180) / 360 * W
    py = lambda lat: (lat0 - lat) / (lat0 - lat1) * H
    o = [f'<svg class="chart" viewBox="0 0 {W} {H + 4}" role="img" aria-label="Map of the people tested and the people flagged" '
         f'xmlns="http://www.w3.org/2000/svg">']
    coast = json.load(open(Q / "data" / "naturalearth" / "ne_110m_coastline.geojson"))
    d = []
    for feat in coast["features"]:
        geom = feat["geometry"]
        for line in (geom["coordinates"] if geom["type"] == "MultiLineString" else [geom["coordinates"]]):
            seg, prev = [], None
            for pt in line:
                lon, lat = pt[0], max(min(pt[1], lat0), lat1)
                if prev is not None and abs(lon - prev) > 180:
                    if len(seg) > 1:
                        d.append("M" + "L".join(seg))
                    seg = []
                seg.append(f"{px(lon):.1f},{py(lat):.1f}")
                prev = lon
            if len(seg) > 1:
                d.append("M" + "L".join(seg))
    o.append(f'<path class="c-coast" d="{" ".join(d)}"/>')
    people = list(csv.DictReader(open(Q / "analysis" / "people_amended.tsv"), delimiter="\t"))
    cells = {(round(float(p["lon"])), round(float(p["lat"]))) for p in people if p["lat"] not in ("", "None") and p["lon"] not in ("", "None")}
    for lon, lat in sorted(cells):
        if lat1 <= lat <= lat0:
            o.append(f'<circle class="c-site" cx="{px(lon):.1f}" cy="{py(lat):.1f}" r="1.3"/>')
    hits = list(csv.DictReader(open(R / "hits_review.tsv"), delimiter="\t"))
    groups = collections.defaultdict(list)
    for h in hits:
        if h["lat"] in ("", "None"):
            continue
        groups[(round(float(h["lon"]), 1), round(float(h["lat"]), 1), h["class"])].append(h)
    standing = None
    for (lon, lat, cls), hs in sorted(groups.items(), key=lambda t: t[0][2] == "standing"):
        label = hs[0]["group"].replace("_", " ")
        tip = esc("|".join([label, f"{len(hs)} {'person' if len(hs) == 1 else 'people'} flagged", CLASS_TEXT[cls]]))
        if cls == "standing":
            standing = (px(lon), py(lat))
            o.append(f'<circle class="c-ring" cx="{px(lon):.1f}" cy="{py(lat):.1f}" r="7"/>')
        o.append(f'<g class="c-mark" tabindex="0" data-tip="{tip}"><circle class="c-hit" cx="{px(lon):.1f}" cy="{py(lat):.1f}" r="8"/>'
                 f'<circle class="c-dot" cx="{px(lon):.1f}" cy="{py(lat):.1f}" r="{3.2 if len(hs) < 5 else 4.4}"/></g>')

    def note(lon, lat, text, dx, dy, anchor="start"):
        x, y = px(lon), py(lat)
        tx, ty = x + dx, y + dy
        o.append(f'<line class="c-leader" x1="{x:.1f}" y1="{y:.1f}" x2="{tx:.1f}" y2="{ty:.1f}"/>')
        o.append(f'<text class="c-label-sm" x="{tx + (4 if anchor == "start" else -4):.1f}" y="{ty + 4:.1f}" text-anchor="{anchor}">{esc(text)}</text>')

    note(-45.4, 61.0, "Greenland Norse", -6, 34, "end")
    note(-170.4, 66.1, "Chukotka", 16, -22)
    note(84, 53.3, "Siberia and the steppe", 38, -40)
    note(77.8, 21.6, "A Cuban, mis-recorded here", 22, 46)
    note(26.2, 44.1, "Pietrele: one person unexplained", -34, 58, "end")
    o.append("</svg>")
    figure("map", "Where the tested people were buried, and who was flagged", "\n".join(o),
           "Small grey dots: places with at least one of the 12,977 people tested. Copper dots: people flagged by the scan; larger dots "
           "are five or more at one place. Nearly all lie across Siberia and the steppe, where ancient people share Ice Age ancestors "
           "with Native Americans. The ring marks the one person left unexplained. Hover or focus a dot for who it is.")


def profile():
    rows = list(csv.DictReader(open(R / "profile_PIE069.tsv"), delimiter="\t"))
    rows.sort(key=lambda r: -float(r["person_Z"]))
    W, label_w, right = 720, 250, 700
    x0, x1 = -3.0, 6.0
    sx = lambda v: label_w + 14 + (v - x0) / (x1 - x0) * (right - label_w - 14)
    row_h, top = 28, 20
    H = top + row_h * len(rows) + 48
    o = [f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="Whom the Pietrele woman leans toward" xmlns="http://www.w3.org/2000/svg">']
    bottom = top + row_h * len(rows) + 4
    for t in range(-2, 7, 2):
        o.append(f'<line class="{"c-zero" if t == 0 else "c-grid"}" x1="{sx(t):.1f}" x2="{sx(t):.1f}" y1="{top - 6}" y2="{bottom}"/>')
        o.append(f'<text class="c-tick" x="{sx(t):.1f}" y="{bottom + 16}" text-anchor="middle">{num(t, 0)}</text>')
    o.append(f'<text class="c-axis" x="{(sx(x0) + sx(x1)) / 2:.1f}" y="{bottom + 36}" text-anchor="middle">'
             'Lean toward each group, compared with the neighbours (Z-score)</text>')
    for i, r in enumerate(rows):
        cy = top + row_h * i + row_h / 2
        a, b = float(r["person_Z"]), float(r["made_up_3pct_median_Z"])
        tip = esc("|".join([r["reference"], f"She: Z = {num(a)}", f"Made-up strangers: Z = {num(b)}"]))
        o.append(f'<g class="c-mark" tabindex="0" data-tip="{tip}"><rect class="c-hit" x="0" y="{cy - row_h / 2:.1f}" width="{W}" height="{row_h}"/>'
                 f'<text class="c-label" x="0" y="{cy + 4:.1f}">{esc(r["reference"])}</text>'
                 f'<line class="c-whisker" x1="{sx(min(a, b)):.1f}" x2="{sx(max(a, b)):.1f}" y1="{cy:.1f}" y2="{cy:.1f}"/>'
                 f'<circle class="c-dot c-hollow" cx="{sx(b):.1f}" cy="{cy:.1f}" r="5"/>'
                 f'<circle class="c-dot" cx="{sx(a):.1f}" cy="{cy:.1f}" r="5"/></g>')
    o.append("</svg>")
    legend = ('<p class="fig-legend"><span class="key"><svg viewBox="0 0 12 12" width="12" height="12" aria-hidden="true"><circle class="k-dot" cx="6" cy="6" r="4.5"/></svg>'
              ' The woman from Pietrele</span><span class="key"><svg viewBox="0 0 12 12" width="12" height="12" aria-hidden="true">'
              '<circle class="k-dot k-hollow" cx="6" cy="6" r="3.8"/></svg> Her neighbours with 3% Native American ancestry added, for comparison</span></p>\n')
    figure("profile", "Whom the one unexplained person leans toward", "\n".join(o),
           "Exploratory. Each row is a reference group; a dot to the right of zero means a lean toward that group, compared with the "
           "20 nearest people from other sites. Her pattern is close to what 3% of Native American ancestry would look like. But she "
           "leans toward Japanese and Han almost as much, so it points to north-east Asia in general, not to the Americas.", legend)


def tiles():
    s = json.load(open(R / "summary.json"))
    t = [(f"{s['people']:,}", "ancient people tested, all buried before 1450 CE"), ("178", "flagged by the scan"),
         ("177", "explained: known groups, shared Ice Age ancestry, a recording error"), ("1", "left unexplained")]
    (OUT / "tiles.html").write_text('<div class="tiles">\n' + "\n".join(
        f'<div class="tile"><p class="tile-value">{esc(v)}</p><p class="tile-label">{esc(l)}</p></div>' for v, l in t) + "\n</div>\n")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    tiles()
    world_map()
    profile()
    print("wrote", ", ".join(sorted(p.name for p in OUT.iterdir())), [p.stat().st_size for p in sorted(OUT.iterdir())])


if __name__ == "__main__":
    main()
