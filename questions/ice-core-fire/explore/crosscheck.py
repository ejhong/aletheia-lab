#!/usr/bin/env python3
"""Exploratory, before the lock: does the NGRIP 10-year file agree with 10-year means made from the 1 mm file?

Checks the column order, the depth-age link and the meaning of the age label, on ages outside 12,000-14,000 only.
"""
import sys

import numpy as np

sys.path.insert(0, "analysis")
import fire

dec = fire.read_pangaea(fire.D / "pangaea" / "935814.tab")
age10 = dec[:, 0] * 1000
mm = fire.raw("ngrip_mm")
ok = ~np.isnan(mm[:, 0])
for label, offset in (("label = young edge, row covers [a, a+10)", 0.0), ("label = centre, [a-5, a+5)", -5.0), ("label = old edge, [a-10, a)", -10.0)):
    j = np.floor((mm[ok, 0] - offset) / 10).astype(int)
    v = mm[ok, 1]
    n = np.bincount(j)
    have = np.bincount(j, weights=(~np.isnan(v)).astype(float))
    tot = np.bincount(j, weights=np.nan_to_num(v))
    with np.errstate(invalid="ignore", divide="ignore"):
        m = np.where(have >= np.maximum(n, 1) * 0.9, tot / have, np.nan)
    idx = np.rint(age10 / 10).astype(int)
    mine = np.where(idx < len(m), m[np.minimum(idx, len(m) - 1)], np.nan)
    keep = ~np.isnan(mine) & ~np.isnan(dec[:, 4]) & ~((age10 >= 12000) & (age10 <= 14000)) & (age10 < 59900)
    for col, name in ((4, "NH4 column"), (5, "NO3 column")):
        k2 = keep & ~np.isnan(dec[:, col])
        r = np.corrcoef(np.log(mine[k2]), np.log(dec[k2, col]))[0, 1]
        ratio = np.median(mine[k2] / dec[k2, col])
        within = np.mean(np.abs(mine[k2] / dec[k2, col] - 1) < 0.05)
        print(f"{label:42s} vs file {name}: n {k2.sum()}, log correlation {r:.4f}, median ratio {ratio:.3f}, within 5% {within:.2f}")
