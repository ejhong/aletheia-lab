#!/usr/bin/env python3
"""Exploratory, after the locked run: why are event and control scores both a little below zero?

The locked plan measures each egg's spread over all its trials in the year's control windows, including windows where
that egg would fail the egg check. Here the spread is measured only over control windows where the egg passes.
Not part of the protocol; not evidence. Writes explore/pool_check.json. Run from questions/global-consciousness.
"""
import json
import math
import sys

import numpy as np

sys.path.insert(0, "analysis")
import netvar

events = netvar.read_events()
year = lambda e: e["start_utc"][:4]
stats = {}
for e in events:
    eggs, x = netvar.window(e["control_start_utc"])
    n, mean, ms = netvar.egg_stats(x)
    ok = netvar.passes(n, mean, ms)
    stats[e["control_start_utc"]] = {eg: (int(a), float(a * b)) for eg, a, b, good in zip(eggs, n, ms, ok) if good}
dropped = sum(1 for e in events for _ in [0])
rows = []
for e in events:
    same = [f["control_start_utc"] for f in events if year(f) == year(e)]
    ev = netvar.score_window(e["start_utc"], [stats[c] for c in same])
    co = netvar.score_window(e["control_start_utc"], [stats[c] for c in same if c != e["control_start_utc"]])
    rows.append((e["event"], (ev["main"] or {}).get("z"), (co["main"] or {}).get("z")))
ze = [r[1] for r in rows if r[1] is not None]
zc = [r[2] for r in rows if r[2] is not None]
d = [r[1] - r[2] for r in rows if r[1] is not None and r[2] is not None]
out = {"events": netvar.combine(ze), "controls": netvar.combine(zc), "paired_mean_difference": float(np.mean(d)),
       "paired_t": float(np.mean(d) / (np.std(d, ddof=1) / math.sqrt(len(d)))), "paired_p": netvar.sign_flip(d)}
json.dump(out, open("explore/pool_check.json", "w"), indent=1)
print(out)
