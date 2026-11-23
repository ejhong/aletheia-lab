#!/usr/bin/env python3
"""Exploratory, after the locked run: the drop about 300 years after the onset. Not part of the protocol; not evidence.

1. The summed curve around the onset, region by region, in 100-year means, beside the made-up reference.
2. The shape of the calibration curve over the same years.
3. The same steps with the older calibration curve (IntCal13) in place of IntCal20, for both the real record and
   its made-up reference. If the drop moves or goes when the curve changes, it leans on the curve.
Writes explore/later_drop.json. Run from questions/younger-dryas-crash.
"""
import csv
import json
import sys

import numpy as np

sys.path.insert(0, "analysis")
import crash

G = crash.GRID
out = {}
cur = {}
for r in csv.DictReader(open("results/curves.tsv"), delimiter="\t"):
    cur.setdefault(r["region"], []).append((int(r["cal_bp"]), float(r["summed"]), float(r["made_up_mean"]), float(r["made_up_2.5"]), float(r["made_up_97.5"])))
for region, rows in cur.items():
    a = np.array(rows)
    tab = []
    for lo in range(11800, 13600, 100):
        m = (a[:, 0] >= lo) & (a[:, 0] < lo + 100)
        tab.append({"from": lo, "real": round(float(a[m, 1].mean()), 3), "made_up_mean": round(float(a[m, 2].mean()), 3),
                    "ratio": round(float(a[m, 1].mean() / a[m, 2].mean()), 2)})
    out["curve_" + region] = tab
    print(region, " ".join(f"{t['from']}:{t['ratio']}" for t in tab))
mu20, sig20 = crash.read_curve()
out["intcal20_radiocarbon_age"] = {int(t): round(float(m)) for t, m in zip(G, mu20) if 12200 <= t <= 13000 and t % 50 == 0}
print("IntCal20:", out["intcal20_radiocarbon_age"])
mu13, sig13 = crash.read_curve(crash.Q / "data" / "intcal13_utf8.14c")
out["intcal13_radiocarbon_age"] = {int(t): round(float(m)) for t, m in zip(G, mu13) if 12200 <= t <= 13000 and t % 50 == 0}
print("IntCal13:", out["intcal13_radiocarbon_age"])
dates, _ = crash.read_dates()
rng = np.random.default_rng(13)
for region in crash.REGIONS:
    a, e, s = dates[region]
    bins, n_bins = crash.bin_index(a, s)
    res = {}
    for name, (mu, sig) in (("IntCal20", (mu20, sig20)), ("IntCal13", (mu13, sig13))):
        S = crash.summed(a, e, bins, mu, sig)
        null = crash.made_up(crash.trend(S), e, bins, n_bins, mu, sig, rng, 400)
        z = {}
        for T in range(12300, 13001, 50):
            sim = crash.step(null, T)
            z[T] = round(float((crash.step(S, T) - sim.mean()) / sim.std(ddof=1)), 2)
        res[name] = z
    out["z_by_curve_" + region] = res
    print(region, "IntCal20 z:", res["IntCal20"])
    print(region, "IntCal13 z:", res["IntCal13"])
json.dump(out, open("explore/later_drop.json", "w"), indent=1)
