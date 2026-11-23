#!/usr/bin/env python3
"""Compare a replication's per-event values and verdicts with ours.

    python replication/compare.py THEIR_OUTDIR      # run from questions/cooling-ammonium
"""
import csv
import json
import pathlib
import sys

Q = pathlib.Path(__file__).resolve().parent.parent
theirs = pathlib.Path(sys.argv[1])
key = lambda r: (r["ion"], r["core"], r["event"])
a = {key(r): r for r in csv.DictReader(open(Q / "results" / "events.tsv"), delimiter="\t") if r["ion"] in ("ammonium", "calcium")}
b = {key(r): r for r in csv.DictReader(open(theirs / "events.tsv"), delimiter="\t")}
print(f"rows: ours {len(a)}, theirs {len(b)}, shared {len(set(a) & set(b))}")
for col in ("D", "D_pct", "P", "P_pct", "R", "R_pct", "H"):
    n = bad = 0
    worst = 0.0
    for k in set(a) & set(b):
        x, y = a[k].get(col, ""), b[k].get(col, "")
        if x == "" and y in ("", "nan", "None"):
            continue
        n += 1
        if (x == "") != (y in ("", "nan", "None")):
            bad += 1
            continue
        d = abs(float(x) - float(y))
        worst = max(worst, d)
        bad += d > 2e-3
    print(f"  {col}: {n - bad}/{n} agree" + (f" (worst difference {worst:.3g})" if bad else ""))
ours, th = json.load(open(Q / "results" / "summary.json")), json.load(open(theirs / "summary.json"))
print("coolings: same list" if ours["coolings"] == th.get("coolings") else f"coolings differ: {set(ours['coolings']) ^ set(th.get('coolings', []))}")
v = ours["ammonium"]["D"]
print("general: ours", repr(v["general"]), "theirs", repr(th.get("general")))
print("younger_dryas: ours", repr(v["younger_dryas"]), "theirs", repr(th.get("younger_dryas")))
print("rank: ours", {c: v["q2"][c]["rank"] for c in v["q2"]}, "theirs", th.get("rank"))
print("quiet times: ours", {i: {c: ours[i]["quiet"][c]["n"] for c in ("NGRIP", "NEEM")} for i in ("ammonium", "calcium")}, "theirs", th.get("quiet_times"))
