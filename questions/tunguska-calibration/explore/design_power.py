#!/usr/bin/env python3
"""Blind comparison of designs before the lock (1905 to 1912 removed from every series).

For each design: the number of reference windows, and how often a pulse added to every test core is ranked first
or in the top tenth. Designs differ in the window (three years from 1907, or two from 1908) and in how sites are
combined: 'site-max' takes each site's largest yearly score in the window and averages the sites; 'year-mean'
averages the sites year by year and takes the largest year. A second scenario lets each site's pulse fall a year
early or late with probability 0.15 each. Run from questions/tunguska-calibration.
"""
import json
import sys

import numpy as np

sys.path.insert(0, "analysis")
import tunguska as t

H, MINBG = t.HALF, t.MIN_BG


def year_scores(series, y, width):
    bg = [np.log(series[k]) for k in list(range(y - H, y)) + list(range(y + width, y + width + H)) if k in series]
    if len(bg) < MINBG:
        return None
    med = float(np.median(bg))
    sc = 1.4826 * float(np.median(np.abs(np.array(bg) - med)))
    if sc <= 0:
        return None
    return {k: (np.log(series[k]) - med) / sc for k in range(y, y + width) if k in series}


def window_score(base, y, width, how):
    sites = sorted({t.CORES[c][0] for c in base})
    per_site = {}
    for site in sites:
        ys = [year_scores(base[c], y, width) for c in base if t.CORES[c][0] == site]
        ys = [d for d in ys if d]
        if not ys:
            return None
        per_site[site] = {k: float(np.mean([d[k] for d in ys if k in d])) for k in range(y, y + width) if any(k in d for d in ys)}
        if not per_site[site]:
            return None
    if how == "site-max":
        return float(np.mean([max(v.values()) for v in per_site.values()]))
    years = [k for k in range(y, y + width) if all(k in v for v in per_site.values())]
    return max(float(np.mean([v[k] for v in per_site.values()])) for k in years) if years else None


rng = np.random.default_rng(7)
base = t.get_series("nh4", t.TEST_CORES, blind=True)
typical = {c: float(np.median([v for y, v in s.items() if 1880 <= y <= 1930])) for c, s in base.items()}
out = {}
for target, width in ((1907, 3), (1908, 2)):
    for how in ("site-max", "year-mean"):
        net = {y: window_score(base, y, width, how) for y in t.starts(target, width)}
        net = {y: v for y, v in net.items() if v is not None}
        pool = sorted(y for y in net if y + width - 1 < 1890 or y > 1925)
        res = {"windows": len(net)}
        for jitter in (0.0, 0.15):
            for k in (0.5, 1.0, 2.0, 4.0):
                first = top = 0
                for _ in range(300):
                    y0 = int(rng.choice(pool))
                    tt = y0 + int(rng.integers(0, width))
                    mod = {}
                    for site in sorted({t.CORES[c][0] for c in base}):
                        d = 0 if rng.random() > 2 * jitter else int(rng.choice([-1, 1]))
                        for c in [c for c in base if t.CORES[c][0] == site]:
                            s2 = dict(base[c])
                            if tt + d in s2:
                                s2[tt + d] += k * typical[c]
                            mod[c] = s2
                    val = window_score(mod, y0, width, how)
                    rank = 1 + sum(v > val for yy, v in net.items() if yy != y0)
                    first += rank == 1
                    top += rank / len(net) <= 0.10
                res[f"jitter {jitter}, pulse {k}"] = [round(first / 300, 2), round(top / 300, 2)]
        out[f"{width}-year from {target}, {how}"] = res
        print(f"{width}-year from {target}, {how}:", json.dumps(res))
json.dump(out, open("explore/design_power.json", "w"), indent=1)
