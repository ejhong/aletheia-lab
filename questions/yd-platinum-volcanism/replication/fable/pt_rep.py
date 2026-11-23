#!/usr/bin/env python3
"""Independent re-derivation of Part 1 (cross-check and within-GISP2 parts) of questions/yd-platinum-volcanism,
written from protocol.md alone by Claude Fable 5.2 without reading analysis/ptvolc.py. Standard library only.

    python3 -I pt_rep.py <data dir>
"""
import json
import math
import statistics
import sys

D = sys.argv[1]
PT = {"onset": 1712.375, "peak": 1712.1875, "end": 1712.0}


def interp(x, xs, ys):
    for (x0, y0), (x1, y1) in zip(zip(xs, ys), zip(xs[1:], ys[1:])):
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0), (x0, y0, x1, y1)
    raise ValueError(x)


g3 = []
for line in open(D + "/noaa/gicc05-calcium-20yr.txt", encoding="latin1"):
    p = line.split()
    if len(p) == 11:
        try:
            g3.append([float(v) for v in p])
        except ValueError:
            pass
g3.sort(key=lambda r: r[8])
out = {"g3_rows": len(g3)}
for k, d in PT.items():
    age, br = interp(d, [r[8] for r in g3], [r[0] for r in g3])
    out["g3_age_" + k] = round(age, 1)
    out["g3_lag_" + k] = round(12896 - age, 1)


def step(pts, cooler_shallow_is_lower):
    """pts: (depth, value) sorted by depth. Returns the split with least squared error, sign as the protocol asks."""
    best = None
    for i in range(5, len(pts) - 4):
        sh, dp = [v for _, v in pts[:i]], [v for _, v in pts[i:]]
        if (statistics.mean(dp) > statistics.mean(sh)) != cooler_shallow_is_lower:
            continue
        sse = sum((v - statistics.mean(sh)) ** 2 for v in sh) + sum((v - statistics.mean(dp)) ** 2 for v in dp)
        if best is None or sse < best[0]:
            best = (sse, pts[i - 1][0], pts[i][0])
    return {"between_shallow": best[1], "and_deep": best[2]}


iso = sorted((r[8], r[9]) for r in g3 if 1700 <= r[8] <= 1730 and not math.isnan(r[9]))
out["d18o_points_1700_1730"] = len(iso)
out["d_d18o_step"] = step(iso, True)
base = [v for d, v in iso if 1717 <= d <= 1725]
mu, sd = statistics.mean(base), statistics.stdev(base)
out["baseline"] = [round(mu, 3), round(sd, 3), len(base)]
below = [(d, v) for d, v in iso if d < 1717]
init = None
for i in range(len(below) - 1, 0, -1):          # from deeper to shallower
    if below[i][1] < mu - sd and below[i - 1][1] < mu - sd:
        init = below[i][0]
        break
out["d_d18o_init"] = init
ions = []
for line in open(D + "/noaa/iond.txt", encoding="latin1"):
    p = line.rstrip("\n").split("\t")
    if len(p) >= 10:
        try:
            top, bot = float(p[0]), float(p[1])
        except ValueError:
            continue
        f = lambda s: float(s) if s.strip() not in ("", "NaN", "nan") else float("nan")
        try:
            ions.append(((top + bot) / 2, f(p[2]), f(p[6]), f(p[9])))
        except ValueError:
            continue
ions.sort()
win = [r for r in ions if 1700 <= r[0] <= 1730]
out["ion_points_1700_1730"] = len(win)
out["d_ca_step"] = step([(d, math.log(ca)) for d, na, ca, so in win if ca > 0], False)
out["d_na_step"] = step([(d, math.log(na)) for d, na, ca, so in win if na > 0], False)
ref = [so for d, na, ca, so in ions if 1695 <= d <= 1735 and not math.isnan(so)]
med = statistics.median(ref)
mad = statistics.median(abs(v - med) for v in ref)
out["so4_median_mad_threshold"] = [round(med, 1), round(mad, 1), round(med + 3 * mad, 1)]
out["so4_spikes_1708_1720"] = [(round(d, 2), so) for d, na, ca, so in ions if 1708 <= d <= 1720 and so > med + 3 * mad]
out["so4_max_in_pt_interval"] = max(so for d, na, ca, so in ions if 1712.0 <= d <= 1712.375)
print(json.dumps(out, indent=1))
