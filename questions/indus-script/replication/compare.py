#!/usr/bin/env python3
"""Compare a replication's output with the archive or with our run.

usage: compare.py REPLICATION_OUT.json --archive ARCHIVE_OUTPUT_DIR PREFIX   (e.g. .../outputs/headline tamil)
       compare.py REPLICATION_OUT.json --ours results/contest_rounds.json LIST_KEY
"""
import json
import os
import sys

rep = json.load(open(sys.argv[1], encoding="utf-8"))
runs = {r["seed"]: r for r in rep["runs"]}
kind, src, key = sys.argv[2], sys.argv[3], sys.argv[4]
same = total = 0
worst = 0.0
for seed, r in sorted(runs.items()):
    if kind == "--archive":
        real = json.load(open(os.path.join(src, f"{key}_real_{seed}.json"), encoding="utf-8"))
        null = json.load(open(os.path.join(src, f"{key}_null_{seed}.json"), encoding="utf-8"))
        want = (real["heldout"], null["heldout"])
        readings_same = real["readings"] == r.get("readings")
    else:
        ours = [x for x in json.load(open(src, encoding="utf-8"))
                if x["list"] == key and x["analysis"] == "main" and x["round"] == seed][0]
        want = (ours["real"], ours["null"])
        readings_same = True
    d = max(abs(want[0] - r["real"]), abs(want[1] - r["null"]))
    worst = max(worst, d)
    total += 1
    same += d < 0.006 and readings_same
print(f"{key}: {same} of {total} seeds agree to two decimals; largest difference {worst:.3f}")
