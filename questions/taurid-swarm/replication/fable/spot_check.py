#!/usr/bin/env python3
"""Spot check of questions/taurid-swarm by a second vendor's model: the headline numbers, recomputed from fresh downloads.

    curl -s "https://ssd-api.jpl.nasa.gov/sbdb_query.api?fields=full_name,class,a,e,i,om,w,H&sb-group=neo" -o neos.json
    curl -s "https://ssd-api.jpl.nasa.gov/fireball.api?date-min=1994-01-01&date-max=2025-12-31" -o fireballs.json
    python3 -I spot_check.py neos.json fireballs.json

Written by Claude Fable 5.2 from protocol.md, without using analysis/taurid.py. Standard library only. It covers the
orbit box and its sizes, the alignment toward Encke, the rounder-orbit comparison group, and the airburst counts.
It does not cover the 7:2 resonance test, the permutation p-values or the figures.
"""
import datetime
import json
import math
import random
import sys

ENCKE = 161.29
d = json.load(open(sys.argv[1]))
ix = {k: i for i, k in enumerate(d["fields"])}
rows = []
for r in d["data"]:
    try:
        if r[ix["class"]] not in ("AMO", "APO", "ATE", "IEO"):
            continue
        a, e, i, om, w, H = [float(r[ix[k]]) for k in ("a", "e", "i", "om", "w", "H")]
        rows.append((a, e, i, (om + w) % 360, H))
    except (TypeError, ValueError):
        pass
print("near-Earth asteroids with full elements:", len(rows))


def stats(sel):
    n = len(sel)
    c = sum(math.cos(math.radians(x[3] - ENCKE)) for x in sel) / n
    f45 = sum(abs(((x[3] - ENCKE + 180) % 360) - 180) <= 45 for x in sel) / n
    return n, round(c, 3), round(f45, 3)


box = lambda x: 1.83 <= x[0] <= 2.70 and 0.63 <= x[1] <= 1.0 and 0 <= x[2] <= 14
ctrl = lambda x: 1.83 <= x[0] <= 2.70 and 0.40 <= x[1] < 0.63 and 0 <= x[2] <= 14
rng = random.Random(1)
for H in (16.5, 18.0, 20.0, 22.0, 99):
    s = [x for x in rows if box(x) and x[4] < H]
    n, cb, f = stats(s)
    u = math.sqrt(2 * n) * cb
    p = sum(math.sqrt(2 * n) * sum(math.cos(rng.uniform(0, 2 * math.pi)) for _ in range(n)) / n >= u for _ in range(4000)) / 4000
    print(f"H<{H}: Taurid-like orbits n={n} alignment={cb} share within 45 deg={f} p against uniform about {p:.4f}"
          f" | rounder-orbit comparison {stats([x for x in rows if ctrl(x) and x[4] < H])}")
fb = json.load(open(sys.argv[2]))
fi = {k: i for i, k in enumerate(fb["fields"])}
dates = [datetime.datetime.strptime(r[fi["date"]][:10], "%Y-%m-%d") for r in fb["data"]]
energy = [float(r[fi["impact-e"]]) if r[fi["impact-e"]] else 0 for r in fb["data"]]
aut = lambda t: (t.month == 10 and t.day >= 15) or t.month == 11
day = lambda t: (t.month == 6 and t.day >= 10) or (t.month == 7 and t.day <= 10)
n = len(dates)
print(f"airbursts 1994-2025: {n}; autumn weeks {sum(map(aut, dates))} (even spread gives {n * 47 / 365.25:.1f}); summer weeks {sum(map(day, dates))}"
      f" ({n * 31 / 365.25:.1f}); autumn, 1 kt and over: {sum(aut(t) and e >= 1 for t, e in zip(dates, energy))} ({sum(e >= 1 for e in energy) * 47 / 365.25:.1f})")
swarm = {1998, 2005, 2015, 2018, 2022, 2025}
share = lambda ys: sum(sum(aut(t) for t in dates if t.year == y) / max(1, sum(t.year == y for t in dates)) for y in ys) / len(ys)
print("share of a year's airbursts in the autumn weeks: swarm years", round(share(swarm), 4), "| other years", round(share(set(range(1994, 2026)) - swarm), 4))
