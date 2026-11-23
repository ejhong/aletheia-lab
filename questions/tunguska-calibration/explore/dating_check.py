#!/usr/bin/env python3
"""Blind checks made before the lock, after the first review. Nothing here reads ammonium, nitrate or black carbon
dated 1905 to 1912.

1. How many sample values are zero or below (dropped by the ingest step), per core and chemical, counted in the files.
2. Dating: for each core, the correlation of its yearly sulphur with NEEM-S1's (a chronology tied to historical
   eruptions) over 1850 to 1950, with the core moved by -2 to +2 years. The best lag says whether a core runs early
   or late. Sulphur is detrended by its 21-year running median, in logs.
3. The same between the four cores at Tunu, for sulphur and for ammonium with 1905 to 1912 removed.
Run from questions/tunguska-calibration:  .venv/bin/python -I explore/dating_check.py
"""
import json
import sys

import numpy as np

sys.path.insert(0, "analysis")
import tunguska as t

out = {}
# 1. values at or below zero in the downloaded files
neg = {}
for core, (site, rel, fmt, age, colmap) in t.CORES.items():
    cols, rows = t.read_table(t.D / rel, fmt)
    for sp, c in colmap.items():
        i = cols.index(c)
        vals = [t.num(r[i]) for r in rows if len(r) > i]
        vals = [v for v in vals if v is not None]
        neg[f"{core}.{sp}"] = [sum(v <= 0 for v in vals), len(vals)]
out["values_at_or_below_zero"] = {k: v for k, v in neg.items() if v[0]}
print("at or below zero (count, of):", out["values_at_or_below_zero"])


def detrended(series, lo=1850, hi=1950, blind=False):
    ys = [y for y in range(lo - 10, hi + 11) if y in series]
    logs = {y: np.log(series[y]) for y in ys}
    res = {}
    for y in range(lo, hi + 1):
        if y in logs and not (blind and 1905 <= y <= 1912):
            nb = [logs[k] for k in range(y - 10, y + 11) if k in logs]
            if len(nb) >= 12:
                res[y] = logs[y] - float(np.median(nb))
    return res


def lagcorr(a, b, lags=(-2, -1, 0, 1, 2)):
    """Correlation of a moved by lag against b: a positive best lag means a's dates run late by that many years."""
    r = {}
    for L in lags:
        ys = [y for y in b if (y + L) in a]
        if len(ys) >= 40:
            r[L] = round(float(np.corrcoef([a[y + L] for y in ys], [b[y] for y in ys])[0, 1]), 2)
    return r


ref = detrended(t.annual("neem_s1", "s"))
out["sulphur_against_neem"] = {}
for core in t.CORES:
    if core != "neem_s1" and "s" in t.CORES[core][4]:
        r = lagcorr(detrended(t.annual(core, "s")), ref)
        out["sulphur_against_neem"][core] = {"by_lag": r, "best": max(r, key=r.get) if r else None}
        print(f"sulphur {core:11s} vs neem_s1:", r, "best lag", out["sulphur_against_neem"][core]["best"])
out["tunu_pairs"] = {}
tunu = ["tunu2013", "tunu2022a", "tunu2022b", "tunu_n"]
for sp in ("s", "nh4"):
    d = {c: detrended(t.annual(c, sp), blind=(sp != "s")) for c in tunu}
    for i, a in enumerate(tunu):
        for b in tunu[:i]:
            r = lagcorr(d[a], d[b])
            out["tunu_pairs"][f"{sp}: {a} vs {b}"] = {"by_lag": r, "best": max(r, key=r.get)}
            print(f"{sp:3s} {a} vs {b}:", r, "best", max(r, key=r.get))
# ammonium of every test core against the mean of the others, 1905 to 1912 removed
out["ammonium_against_neem"] = {}
refa = detrended(t.annual("neem_s1", "nh4"), blind=True)
for core in t.CORES:
    if core != "neem_s1":
        r = lagcorr(detrended(t.annual(core, "nh4"), blind=True), refa)
        out["ammonium_against_neem"][core] = {"by_lag": r, "best": max(r, key=r.get) if r else None}
        print(f"ammonium {core:11s} vs neem_s1:", r, "best lag", out["ammonium_against_neem"][core]["best"])
json.dump(out, open("explore/dating_check.json", "w"), indent=1)
