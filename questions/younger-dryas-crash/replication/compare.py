#!/usr/bin/env python3
"""Compare a replication's curves and summary with ours.

    python replication/compare.py THEIR_OUTDIR      # run from questions/younger-dryas-crash
"""
import csv
import json
import pathlib
import sys

Q = pathlib.Path(__file__).resolve().parent.parent
theirs = pathlib.Path(sys.argv[1])
key = lambda r: (r["region"], int(float(r["cal_bp"])))
a = {key(r): float(r["summed"]) for r in csv.DictReader(open(Q / "results" / "curves.tsv"), delimiter="\t")}
b = {key(r): float(r["summed"]) for r in csv.DictReader(open(theirs / "curves.tsv"), delimiter="\t")}
both = set(a) & set(b)
worst = max(abs(a[k] - b[k]) / max(a[k], 1e-9) for k in both)
print(f"summed curves: {len(both)} shared points of {len(a)}; worst relative difference {worst:.2g}")
o, t = json.load(open(Q / "results" / "summary.json")), json.load(open(theirs / "summary.json"))
print("overall: ours", repr(o["overall"]), "theirs", repr(t.get("overall")))
for r, x in o["regions"].items():
    y = t.get("regions", {}).get(r, {})
    print(f"{r}: dates {x['dates']}/{y.get('dates')}, bins {x['bins']}/{y.get('bins')}, step {x['step_at_target']:+.4f}/{y.get('step_at_target', float('nan')):+.4f}, "
          f"p {x['p_at_target']:.4f}/{y.get('p_at_target')}, power {x['power_halving']:.2f}/{y.get('power_halving')}, "
          f"halvings at or above {x['share_of_halvings_with_step_at_or_above_real']:.3f}/{y.get('share_of_halvings_with_step_at_or_above_real')}, "
          f"verdict {x['verdict']!r}/{y.get('verdict')!r}")
