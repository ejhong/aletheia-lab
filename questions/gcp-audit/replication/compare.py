#!/usr/bin/env python3
"""Compare a replication's per-window scores and summary with ours.

    python replication/compare.py THEIR_OUTDIR      # run from questions/gcp-audit
"""
import csv
import json
import pathlib
import sys

Q = pathlib.Path(__file__).resolve().parent.parent
theirs = pathlib.Path(sys.argv[1])
a = {r["num"]: r for r in csv.DictReader(open(Q / "results" / "windows.tsv"), delimiter="\t")}
b = {r["num"]: r for r in csv.DictReader(open(theirs / "windows.tsv"), delimiter="\t")}
print(f"events: ours {len(a)}, theirs {len(b)}, shared {len(set(a) & set(b))}")
for ours_col, their_col in (("event_z", "event_z"), ("control_z", "control_z"), ("event_df", "event_seconds_used"),
                            ("control_df", "control_seconds_used"), ("event_eggs", "event_eggs_usable"), ("control_eggs", "control_eggs_usable")):
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
    print(f"  {ours_col}: {n} compared, {bad} differ by more than 0.01 or in being evaluable, largest difference {worst:.2g}")


def same(x, y):
    """'same' if both are numbers within 0.01 or equal labels, else 'DIFFERENT'."""
    if isinstance(x, (int, float)) and isinstance(y, (int, float)):
        return "same" if abs(x - y) <= 0.01 else "DIFFERENT"
    return "same" if x == y else "DIFFERENT"


o, t = json.load(open(Q / "results" / "summary.json")), json.load(open(theirs / "summary.json"))
v = o["all"]
print(f"events: ours n {v['events']['n']} z {v['events']['z']}; theirs n {t.get('n_events')} z {t.get('z_all')}"
      f" -> n {same(v['events']['n'], t.get('n_events'))}, z {same(v['events']['z'], t.get('z_all'))}")
print(f"controls: ours n {v['controls']['n']} z {v['controls']['z']} sd {v['controls']['sd']}; theirs n {t.get('n_controls')}"
      f" z {t.get('z_controls')} sd {t.get('sd_controls')} -> n {same(v['controls']['n'], t.get('n_controls'))},"
      f" z {same(v['controls']['z'], t.get('z_controls'))}, sd {same(v['controls']['sd'], t.get('sd_controls'))}")
pp, tp = v["paired"], t.get("pairs", {})
for name, ours, key in [("pairs n", pp["n"], "n"), ("pairs events z", v["events_in_pairs"]["z"], "z_events"),
                        ("pairs controls z", v["controls_in_pairs"]["z"], "z_controls"), ("pairs controls sd", v["controls_in_pairs"]["sd"], "sd_controls"),
                        ("pairs mean difference", pp["mean_difference"], "mean_difference"), ("pairs sign-flip p", pp["p_one_sided"], "p_one_sided_sign_flip")]:
    print(f"{name}: ours {ours} theirs {tp.get(key)} -> {same(ours, tp.get(key))}")
rep, trep = v["reproduction"], t.get("reproduction", {})
for key in ("n", "r", "median_abs_difference", "combined_ours", "combined_published"):
    print(f"reproduction {key}: ours {rep.get(key)} theirs {trep.get(key)} -> {same(rep.get(key), trep.get(key))}")
for label in ("reproduction", "events", "controls", "overall"):
    x, y = o["verdicts"].get(label), t.get("verdicts", {}).get(label)
    print(f"verdict {label}: ours {x!r} theirs {y!r} -> {same(x, y)}")
