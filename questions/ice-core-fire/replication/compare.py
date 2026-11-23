#!/usr/bin/env python3
"""Compare a replication's window tables and summary with ours.

    python replication/compare.py THEIR_OUTDIR      # run from questions/ice-core-fire
"""
import csv
import json
import math
import pathlib
import sys

Q = pathlib.Path(__file__).resolve().parent.parent
theirs = pathlib.Path(sys.argv[1])
SERIES = ["N10", "E10", "N20", "E20", "G20", "N60", "E60", "G60", "N3", "N1", "G10", "E10h", "G20h", "G60h"]
num = lambda s: float("nan") if s in ("", "nan", "NaN", "None") else float(s)


def table(path):
    return {int(float(r["k"])): r for r in csv.DictReader(open(path), delimiter="\t")}


for s in SERIES:
    p = theirs / f"windows_{s}.tsv"
    if not p.exists():
        print(f"{s}: no file from the replication")
        continue
    a, b = table(Q / "results" / f"windows_{s}.tsv"), table(p)
    line = [f"{s}: windows ours {len(a)}, theirs {len(b)}, shared {len(set(a) & set(b))}"]
    for col in ("E", "H", "Z", "mean", "E_age", "H_age", "Z_age"):
        worst, bad, n = 0.0, 0, 0
        for k in set(a) & set(b):
            x, y = num(a[k][col]), num(b[k].get(col, "nan"))
            if math.isnan(x) and math.isnan(y):
                continue
            n += 1
            if math.isnan(x) != math.isnan(y):
                bad += 1
                continue
            d = abs(x - y) / (1.0 if col.endswith("_age") else max(abs(x), 1e-9))
            worst = max(worst, d)
            if d > (0.5 if col.endswith("_age") else 1e-3):
                bad += 1
        line.append(f"{col} {n - bad}/{n} agree" + (f" (worst {worst:.2g})" if bad else ""))
    print("; ".join(line))
ours, th = json.load(open(Q / "results" / "summary.json")), json.load(open(theirs / "summary.json"))
print("verdict: ours", repr(ours["verdict"]), "theirs", repr(th.get("verdict")))
for m in ("E", "H", "Z"):
    for s in SERIES:
        x, y = ours["ranks"][m].get(s), (th.get("ranks", {}).get(m) or {}).get(s)
        if x is None and y is None:
            continue
        if x is None or y is None:
            print(f"  {m} {s}: ours {x and x['rank']}, theirs {y and y.get('rank')}  <-- differs")
            continue
        flag = "" if (x["rank"], x["N"]) == (y.get("rank"), y.get("N")) else "  <-- differs"
        print(f"  {m} {s}: rank ours {x['rank']}/{x['N']}, theirs {y.get('rank')}/{y.get('N')}{flag}")
