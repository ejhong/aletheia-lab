#!/usr/bin/env python3
"""
Spot-check of ydb-site-synchrony (#113): sensitivity of the headline numbers.

What it computes, from the study's own committed outputs only
(../results/pillar1_dates.csv and ../results/pillar2_sites.csv; no downloads):

  1. Each site's contribution to the Ward-Wilson T of the 9-site Primary panel (T = 630.62).
  2. Leave-one-site-out T with chi-square p (df = n - 1), for Primary and Favorable panels.
  3. Internal scatter (Ward-Wilson T within the site) of the Arlington Canyon 12-date pool
     and the Aalsterhut 14-date pool.
  4. Primary T with alternative Arlington values:
       a. Kennett et al. 2008 (QSR 27:2528-2543), Fig. 4 caption: "Five dates from the lowest
          dark layer were used to establish the Santarosae wildfire 11,060 +/- 40 14C years".
       b. The spot-checker's own construction: weighted mean of the 7 dates in the study's
          392-503 cm window that Kennett 2008 Table 4 footnote f does NOT exclude as old wood.
  5. Primary T with the two pooled-site errors widened by the Birge ratio sqrt(T_within / df)
     (applied only when > 1), i.e. scaled to match each pool's internal scatter.
  6. The five panel sites Kennett 2015 Fig. 2 marks as dated on the proxy layer (dropping the
     four Clovis-occupation sites), under the Primary and Favorable choices.
  7. Span of calibrated medians (from the study's IntCal20 calibration) without Blackwater Draw.
  8. Placebo-year overlap of Kennett 2015's 23 modeled 95% intervals, and W_50 / W_80 at 1-yr steps.
  9. A table for the four Clovis-occupation sites: Kennett 2015 Fig. 2 "date on proxies" flag
     (as parsed into pillar2_sites.csv) and Waters & Stafford 2007 (Science 315:1122) Table 1 heading.

All p-values printed here are analytic chi-square p-values of Ward-Wilson T, not the
study's simulated p_T (which needs IntCal20 and is not recomputed here).

Run from the repo root:
    .venv/bin/python questions/ydb-site-synchrony/spotcheck/spotcheck.py
Needs numpy and scipy (the repo venv has both). Output is deterministic; see output.txt.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

import numpy as np
from scipy import stats

RESULTS = Path(__file__).resolve().parent.parent / "results"

CLOVIS_SITES = ["Murray Springs, AZ", "Sheriden Cave, OH", "Indian Creek, MT", "Blackwater Draw, NM"]
# Name used for the same site in Kennett 2015 Fig. 2 (pillar2_sites.csv)
FIG2_NAME = {
    "Murray Springs, AZ": "Murray Spgs",
    "Sheriden Cave, OH": "Sheriden Cave",
    "Indian Creek, MT": "Indian Creek",
    "Blackwater Draw, NM": "Blackwater",
}
# Waters & Stafford 2007, Science 315:1122-1126, Table 1: section heading and row as printed
WATERS_STAFFORD = {
    "Murray Springs, AZ": ("Clovis sites (credible ages and Clovis diagnostics)", "Murray Springs, AZ (n = 8) 10,885 ± 50"),
    "Sheriden Cave, OH": ("Problematic Clovis and Clovis-age sites", "Sheriden Cave, OH (below artifacts, n = 2) 10,920 ± 50"),
    "Indian Creek, MT": ("Clovis-age sites (credible ages but no Clovis diagnostics)", "Indian Creek, MT (n = 1) 10,980 ± 110"),
    "Blackwater Draw, NM": ("Problematic Clovis and Clovis-age sites", "Blackwater Draw, NM (n = 3) 11,300 ± 235"),
}
# Kennett 2008 Table 4 footnote f: "Not included in average age of lowest stratigraphic unit due to 'old wood' effect."
K2008_FOOTNOTE_F = {"UCIAMS-36306", "UCIAMS-36960", "UCIAMS-36961", "UCIAMS-36962", "UCIAMS-36305"}
# The five lowest-unit (blue-gray mud/silt) dates not under footnote f, i.e. the five behind 11,060 +/- 40
K2008_LOWEST_FIVE = {"UCIAMS-36308", "UCIAMS-36307", "UCIAMS-36959", "Beta-161032", "UCIAMS-36304"}
K2008_PUBLISHED = (11060.0, 40.0)


def read_csv(name):
    with (RESULTS / name).open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def ww(rows):
    """Ward & Wilson (1978): weighted mean, its error, T, df, chi-square p. rows = [(label, y, sigma)]."""
    y = np.array([r[1] for r in rows], float)
    s = np.array([r[2] for r in rows], float)
    w = 1.0 / s**2
    ybar = float((w * y).sum() / w.sum())
    T = float((w * (y - ybar) ** 2).sum())
    df = len(rows) - 1
    return ybar, 1.0 / math.sqrt(w.sum()), T, df, float(stats.chi2.sf(T, df))


def fmt_p(p):
    return f"{p:.2g}" if p < 0.001 else f"{p:.3f}"


def line(label, rows):
    _, _, T, df, p = ww(rows)
    return f"  {label:<58s} T = {T:7.2f}  df = {df:2d}  p = {fmt_p(p)}"


def replace(rows, site, y, s):
    return [(r[0], y, s) if r[0] == site else r for r in rows]


def main():
    p1 = read_csv("pillar1_dates.csv")
    panel = lambda name: [(r["site"], float(r["rcybp"]), float(r["sigma"])) for r in p1 if r["panel"] == name]
    primary, favorable = panel("YDB_Primary"), panel("YDB_Favorable")
    allraw = [r for r in p1 if r["panel"] == "YDB_AllRaw"]
    med = {r["site"]: float(r["cal_median"]) for r in p1 if r["panel"] == "YDB_Primary"}

    print("ydb-site-synchrony spot-check (inputs: results/pillar1_dates.csv, results/pillar2_sites.csv)")
    print("All p below are analytic chi-square p of Ward-Wilson T (df = n - 1), not simulated p_T.\n")

    # 1. Contributions
    ybar, sbar, T, df, p = ww(primary)
    print(f"1. Primary panel: weighted mean {ybar:.1f} ± {sbar:.1f} 14C BP, T = {T:.2f}, df = {df}, p = {fmt_p(p)}")
    print("   Contribution of each site to T, (y - mean)^2 / sigma^2:")
    contrib = {site: (y - ybar) ** 2 / s**2 for site, y, s in primary}
    for site, y, s in primary:
        print(f"     {site:<26s} {y:8.1f} ± {s:5.1f}   {contrib[site]:6.1f}")
    top3 = ["Lake Hind, Manitoba", "Arlington Canyon, CA", "Aalsterhut, Netherlands"]
    print(f"   Lake Hind + Arlington + Aalsterhut = {sum(contrib[k] for k in top3):.1f} of {T:.1f}\n")

    # 2. Leave-one-site-out
    for name, rows in (("Primary", primary), ("Favorable", favorable)):
        print(f"2. Leave-one-site-out, {name} panel (full panel: T = {ww(rows)[2]:.2f}, p = {fmt_p(ww(rows)[4])}):")
        outs = []
        for i, (site, _, _) in enumerate(rows):
            rest = rows[:i] + rows[i + 1:]
            outs.append(ww(rest)[2])
            print(line(f"drop {site}", rest))
        print(f"   minimum leave-one-out T = {min(outs):.2f}\n")

    # 3. Internal scatter of the pooled sites
    print("3. Internal scatter of pooled sites (all dates the study pooled into one value):")
    pools = {}
    for site in ("Arlington Canyon, CA", "Aalsterhut, Netherlands"):
        rows = [(r["lab_id"], float(r["rcybp"]), float(r["sigma"])) for r in allraw if r["site"] == site]
        yb, sb, Tw, dfw, pw = ww(rows)
        birge = max(1.0, math.sqrt(Tw / dfw))
        pools[site] = (yb, sb, birge)
        print(f"  {site:<26s} n = {len(rows):2d}  mean {yb:.1f} ± {sb:.1f}  within-site T = {Tw:.1f}  df = {dfw}  "
              f"p = {fmt_p(pw)}  Birge ratio sqrt(T/df) = {birge:.2f}")
    print()

    # 4. Alternative Arlington values
    arl = [(r["lab_id"], float(r["rcybp"]), float(r["sigma"])) for r in allraw if r["site"] == "Arlington Canyon, CA"]
    five = [r for r in arl if r[0] in K2008_LOWEST_FIVE]
    seven = [r for r in arl if r[0] not in K2008_FOOTNOTE_F]
    y5, s5 = ww(five)[:2]
    y7, s7 = ww(seven)[:2]
    print("4. Primary panel with other Arlington Canyon values:")
    print(f"   (check: weighted mean of the 5 lowest-unit dates not under footnote f = {y5:.1f} ± {s5:.1f};"
          f" Kennett 2008 publishes {K2008_PUBLISHED[0]:.0f} ± {K2008_PUBLISHED[1]:.0f})")
    print(line(f"a. Kennett 2008 Fig. 4 published average {K2008_PUBLISHED[0]:.0f} ± {K2008_PUBLISHED[1]:.0f}",
               replace(primary, "Arlington Canyon, CA", *K2008_PUBLISHED)))
    print(line(f"b. 7 non-footnote-f dates in 392-503 cm, {y7:.1f} ± {s7:.1f}",
               replace(primary, "Arlington Canyon, CA", y7, s7)))
    print()

    # 5. Birge-widened pooled errors
    prim_y = {site: y for site, y, _ in primary}
    widened = primary
    for site, (_, sb, birge) in pools.items():
        widened = replace(widened, site, prim_y[site], sb * birge)
    print("5. Primary panel with pooled-site errors widened by the Birge ratio:")
    for site, (_, sb, birge) in pools.items():
        print(f"     {site:<26s} sigma {sb:.1f} -> {sb * birge:.1f}")
    print(line("Primary, Arlington and Aalsterhut errors widened", widened))
    print()

    # 6. Five Kennett-direct sites
    clovis = set(CLOVIS_SITES)
    print("6. The five panel sites Kennett 2015 Fig. 2 marks as dated on the proxy layer")
    print("   (Abu Hureyra, Arlington Canyon, Aalsterhut, Lake Hind, Bull Creek; Clovis-occupation sites dropped):")
    print(line("Primary choices", [r for r in primary if r[0] not in clovis]))
    print(line("Favorable choices", [r for r in favorable if r[0] not in clovis]))
    print(line("(for comparison) the four Clovis-occupation sites alone", [r for r in primary if r[0] in clovis]))
    print()

    # 7. Span
    span_all = max(med.values()) - min(med.values())
    rest = {k: v for k, v in med.items() if k != "Blackwater Draw, NM"}
    lo_site, hi_site = min(rest, key=rest.get), max(rest, key=rest.get)
    print("7. Span of IntCal20 calibrated medians, Primary panel (study's own calibration):")
    print(f"   all 9 sites: {span_all:.0f} yr;  without Blackwater Draw: {rest[hi_site] - rest[lo_site]:.0f} yr "
          f"({hi_site} {rest[hi_site]:.0f} to {lo_site} {rest[lo_site]:.0f} cal BP)\n")

    # 8. Placebo overlap and W_50 / W_80
    p2 = read_csv("pillar2_sites.csv")
    modeled = [r for r in p2 if r["quality"] != "Unmodeled"]
    lo = np.array([float(r["ci95_lower"]) for r in modeled])
    hi = np.array([float(r["ci95_upper"]) for r in modeled])
    print(f"8. Placebo-year overlap of Kennett 2015's {len(modeled)} modeled 95% intervals:")
    for yr in (13300, 13050, 12800, 12550, 12300):
        print(f"     {yr} cal BP ({yr - 12800:+5d} yr): {int(((lo <= yr) & (yr <= hi)).sum()):2d} of {len(modeled)}")
    years = np.arange(10000, 15001)
    frac = ((lo[None, :] <= years[:, None]) & (years[:, None] <= hi[None, :])).mean(axis=1)
    for thr in (0.5, 0.8):
        hits = years[frac >= thr]
        print(f"   W_{int(thr * 100)} at 1-yr steps: {hits.min()}-{hits.max()} cal BP = {hits.max() - hits.min()} yr "
              f"(study, 10-yr steps: {'930' if thr == 0.5 else '300'} yr)")
    print()

    # 9. Clovis table
    fig2 = {r["site"]: r for r in p2}
    print("9. The four Clovis-occupation sites in the 9-site panel:")
    print(f"   {'Site':<21s}| {'Kennett 2015 Fig. 2: date on proxies (tier)':<44s}| Waters & Stafford 2007 Table 1 heading; row")
    print(f"   {'-' * 21}|{'-' * 45}|{'-' * 60}")
    for site in CLOVIS_SITES:
        r = fig2[FIG2_NAME[site]]
        flag = "yes" if r["direct_on_proxies"] == "True" else "no"
        head, row = WATERS_STAFFORD[site]
        print(f"   {site:<21s}| {flag + ' (' + r['quality'] + ')':<44s}| {head}; \"{row}\"")


if __name__ == "__main__":
    main()
