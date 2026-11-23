#!/usr/bin/env python3
"""Independent re-derivation of the primary measures of questions/yd-cooling-shape, written from protocol.md alone.

    python3 -I shape_rep.py <data dir> <events.tsv>

Standard library only. Written by Claude Fable 5.2 without reading analysis/shape.py.
"""
import csv
import json
import math
import statistics
import sys

D, EV = sys.argv[1], sys.argv[2]
events = [(r["event"], float(r["age_b2k"]), r["kind"], r["definition_uncertainty"]) for r in csv.DictReader(open(EV), delimiter="\t")]


def pool(lo, hi, shift=0):
    out = []
    for name, t, kind, unc in events:
        if kind != "stadial onset" or unc not in ("4yr", "a", "b"):
            continue
        if any(t - 200 < u < t + 100 for n, u, _, _ in events if n != name):
            continue
        if t - shift - 200 >= lo and t - shift + 200 <= hi:
            out.append((name, t))
    return out


def d18o():
    rows = []
    for line in open(D + "/noaa/gicc05-60ka-20yr.txt", encoding="latin1"):
        p = line.split()
        if len(p) == 4:
            try:
                a, _, v, _ = map(float, p)
            except ValueError:
                continue
            rows.append((a - 10, v))
    return rows


def kindler():
    rows = []
    for line in open(D + "/noaa/ngrip2014temp.txt", encoding="latin1"):
        if line.startswith("#"):
            continue
        p = line.rstrip("\n").split("\t")
        try:
            rows.append((float(p[2]), float(p[4]), float(p[3])))
        except (ValueError, IndexError):
            continue
    return rows


def calcium():
    rows, on = [], False
    for line in open(D + "/pangaea/935814.tab", encoding="utf-8"):
        if line.startswith("*/"):
            on = True
            continue
        if not on or line.startswith("Age"):
            continue
        p = line.rstrip("\n").split("\t")
        if len(p) > 3 and p[3]:
            v = float(p[3])
            if v > 0:
                rows.append((round(float(p[0]) * 1000) + 5, math.log(v)))
    return rows


def antarctic():
    rows, head = [], None
    for line in open(D + "/noaa/buizert2021-temp.txt", encoding="latin1"):
        if line.startswith("#"):
            continue
        p = line.rstrip("\n").split("\t")
        if head is None:
            head = p
            continue
        rec = dict(zip(head, map(float, p)))
        cores = [rec[k] for k in ("TS_WD", "TS_EDML", "TS_EDC", "TS_TAL", "TS_SDM", "TS_SP", "TS_DF")]
        rows.append((rec["age_yrBP1950"], sum(cores) / 7, rec["TS_WD"]))
    return rows


mean = lambda rows, lo, hi, col=1: (lambda v: sum(v) / len(v) if v else float("nan"))([r[col] for r in rows if lo <= r[0] < hi])


def slope(rows, t):
    pts = [((t - a) / 100, v) for a, v in rows if t <= a < t + 200]
    mx, my = sum(x for x, _ in pts) / len(pts), sum(y for _, y in pts) / len(pts)
    return sum((x - mx) * (y - my) for x, y in pts) / sum((x - mx) ** 2 for x, _ in pts)


def rank(vals, name="GS-1"):
    v = vals[name]
    others = [x for n, x in vals.items() if n != name]
    q = statistics.quantiles(others, n=4, method="inclusive")
    return {"GS-1": round(v, 3), "rank": 1 + sum(x > v for x in others), "n": len(vals), "median_others": round(statistics.median(others), 3),
            "iqr_others": [round(q[0], 3), round(q[2], 3)], "top10_cut": max(1, len(vals) // 10)}


O, K, C, A = d18o(), kindler(), calcium(), antarctic()
p60, p100, p40 = pool(10000, 60000), pool(10300, 107620), pool(10000, 40000, shift=50)
res = {"pools": {"60kyr": len(p60), "100kyr": len(p100), "40kyr": len(p40)},
       "abrupt_60": rank({n: mean(O, t, t + 100) - mean(O, t - 60, t) for n, t in p60}),
       "amp_temp": rank({n: mean(K, t, t + 100) - mean(K, t - 200, t - 40) for n, t in p100}),
       "dust_jump": rank({n: mean(C, t - 200, t - 40) - mean(C, t, t + 100) for n, t in p100}),
       "dust_abrupt_60": rank({n: mean(C, t - 60, t) - mean(C, t, t + 100) for n, t in p100}),
       "abrupt_temp_60": rank({n: mean(K, t, t + 100) - mean(K, t - 60, t) for n, t in p100}),
       "pre_slope": rank({n: slope(O, t) for n, t in p60}),
       "ant_cool_mean": rank({n: -(mean(A, t - 50 - 200, t - 50) - mean(A, t - 50, t - 50 + 200)) for n, t in p40}),
       "ant_cool_WD": rank({n: -(mean(A, t - 50 - 200, t - 50, 2) - mean(A, t - 50, t - 50 + 200, 2)) for n, t in p40})}
print(json.dumps(res, indent=1))
