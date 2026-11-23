#!/usr/bin/env python3
"""Compare a replication's per-window scores and summary with ours.

    python replication/compare.py THEIR_OUTDIR      # run from questions/global-consciousness
"""
import csv
import json
import pathlib
import sys

Q = pathlib.Path(__file__).resolve().parent.parent
theirs = pathlib.Path(sys.argv[1])
a = {r["start_utc"]: r for r in csv.DictReader(open(Q / "results" / "events.tsv"), delimiter="\t")}
b = {r["start_utc"]: r for r in csv.DictReader(open(theirs / "windows.tsv"), delimiter="\t")}
print(f"events: ours {len(a)}, theirs {len(b)}, shared {len(set(a) & set(b))}")
for ours_col, their_col in (("z", "z"), ("control_z", "control_z"), ("seconds_used", "seconds_used"), ("control_seconds_used", "control_seconds_used"),
                            ("eggs_passing", "eggs_usable"), ("control_eggs_passing", "control_eggs_usable")):
    n = bad = 0
    worst = 0.0
    for k in set(a) & set(b):
        x, y = a[k].get(ours_col, ""), b[k].get(their_col, "")
        if x == "" and y in ("", "nan", "None"):
            continue
        n += 1
        if (x == "") != (y in ("", "nan", "None")):
            bad += 1
            continue
        d = abs(float(x) - float(y))
        worst = max(worst, d)
        bad += d > 0.01
    print(f"  {ours_col}: {n - bad}/{n} agree" + (f" (worst difference {worst:.3g})" if bad else f" (worst difference {worst:.2g})"))
o, t = json.load(open(Q / "results" / "summary.json")), json.load(open(theirs / "summary.json"))
v = o["all"]
print(f"events: ours n {v['events']['n']} z {v['events']['z']:+.3f}; theirs n {t.get('n_events')} z {t.get('z_all')}")
print(f"controls: ours n {v['controls']['n']} z {v['controls']['z']:+.3f} sd {v['controls']['sd']:.3f}; theirs n {t.get('n_controls')} z {t.get('z_controls')} sd {t.get('sd_controls')}")
print("departure: ours", repr(v["verdicts"]["departure"]), "theirs", repr(t.get("departure")))
print("size: ours", repr(v["verdicts"]["size"]), "theirs", repr(t.get("size")))
print("calibration in doubt: ours", o["calibration_in_doubt"], "theirs", t.get("calibration_in_doubt"))
print("paired: ours", {k: (round(x, 4) if isinstance(x, float) else x) for k, x in v.get("paired", {}).items()}, "theirs", t.get("paired"))
