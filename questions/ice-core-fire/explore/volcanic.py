#!/usr/bin/env python3
"""Exploratory, after the result: sulphate (the mark of eruptions) and calcium (dust) beside ammonium in GISP2.

Not part of the protocol; not evidence. All three ions come from the same samples of one core, so their order in
depth needs no timescale. Writes explore/volcanic.json. Run from questions/ice-core-fire.
"""
import json
import sys

import numpy as np

sys.path.insert(0, "analysis")
import fire

g = fire.raw("gisp2")
COL = {"NH4": 3, "Ca": 6, "SO4": 9}
out = {}

# 1. Twenty-year means across the window, the three ions side by side.
a0 = fire.CENTRE["gisp2"] - 150
series = {ion: fire.bin_samples(g[:, 10], g[:, 11], g[:, c], a0, 20) for ion, c in COL.items()}
out["bins20"] = [{"start": a0 + 20 * j, **{ion: round(float(b.get(j, j + 1)[0]), 1) for ion, b in series.items()}} for j in range(-12, 28)]

# 2. The same window test, on sulphate: is the largest sulphate excess near the onset unusual?
for name in ("G20", "G60", "G10"):
    for width in (300, 120, 600):
        T = fire.SERIES[name][3]
        fire._built[(name, width, "SO4", 0.0)] = fire.bin_samples(g[:, 10], g[:, 11], g[:, 9], fire.CENTRE["gisp2"] - width / 2, T)
        r = fire.rank(fire.windows(name, width, "SO4"), "E")
        out[f"sulphate_{name}_{width}"] = {k: r[k] for k in ("value", "rank", "N", "age", "value_needed_top5", "value_needed_top1")}

# 3. Single samples: sulphate against the median of the 20 samples either side, from 12,500 to 13,300 on the file's scale.
so4 = g[:, 9]
med = np.array([np.median(so4[max(0, i - 20):i + 21]) for i in range(len(so4))])
ex = so4 - med
sel = np.flatnonzero((g[:, 10] >= 12500) & (g[:, 11] <= 13300))
big = sorted(sel, key=lambda i: -ex[i])[:8]
late = np.flatnonzero((g[:, 10] >= 10300) & (g[:, 11] <= 15000))
out["largest_sulphate_samples_12500_13300"] = [{"top_m": g[i, 0], "age": round(float(g[i, 10])), "SO4": so4[i], "background": round(float(med[i]), 1),
                                                "excess": round(float(ex[i]), 1), "NH4": g[i, 3], "Ca": g[i, 6],
                                                "share_of_10300_15000_samples_with_smaller_excess": round(float(np.mean(ex[late] < ex[i])), 4)} for i in sorted(big, key=lambda i: g[i, 10])]
json.dump(out, open("explore/volcanic.json", "w"), indent=1, default=float)
print("start   NH4    Ca   SO4   (20-year means, GISP2 years BP)")
for r in out["bins20"]:
    print(f"{r['start']:6.0f} {r['NH4']:5.1f} {r['Ca']:5.1f} {r['SO4']:6.1f}")
for k, v in out.items():
    if k.startswith("sulphate"):
        print(k, {a: (round(b, 1) if isinstance(b, float) else b) for a, b in v.items()})
for r in out["largest_sulphate_samples_12500_13300"]:
    print(r)

# 4. Dust (calcium) beside ammonium in NGRIP and NEEM, 20-year means from the 10-year files.
for name, src in (("NGRIP", "ngrip10"), ("NEEM", "neem10")):
    r = fire.raw(src)
    age = np.rint(r[:, 0] * 1000).astype(int)
    nh4, ca = fire.bin_decadal(age, r[:, 4], 12750, 20), fire.bin_decadal(age, r[:, 3], 12750, 20)
    out[f"bins20_{name}"] = [{"start": 12750 + 20 * j, "NH4": round(float(nh4.get(j, j + 1)[0]), 1), "Ca": round(float(ca.get(j, j + 1)[0]), 1)} for j in range(-12, 28)]
    lo = np.array([x["Ca"] for x in out[f"bins20_{name}"]])
    am = np.array([x["NH4"] for x in out[f"bins20_{name}"]])
    print(name, "start: NH4 / Ca  ", "  ".join(f"{x['start']}: {x['NH4']:.0f}/{x['Ca']:.0f}" for x in out[f"bins20_{name}"]))
json.dump(out, open("explore/volcanic.json", "w"), indent=1, default=float)
