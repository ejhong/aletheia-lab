#!/usr/bin/env python3
"""Exploratory, after the locked run: the shape of the rise. Not part of the protocol; not evidence.

Writes explore/after.json. Run from questions/cooling-ammonium. Standard library only.
"""
import csv
import json
import statistics

rows = list(csv.DictReader(open("results/events.tsv"), delimiter="\t"))
D = {(r["ion"], r["core"], r["event"]): float(r["D"]) for r in rows if r["D"]}
events = sorted({r["event"] for r in rows}, key=lambda e: next(int(r["age"]) for r in rows if r["event"] == e))
out = {}

# 1. Ammonium D averaged over the two cores, ranked.
both = {e: (D[("ammonium", "NGRIP", e)] + D[("ammonium", "NEEM", e)]) / 2 for e in events if ("ammonium", "NGRIP", e) in D and ("ammonium", "NEEM", e) in D}
out["two_core_mean_D"] = sorted(([e, round(v, 3)] for e, v in both.items()), key=lambda t: -t[1])

# 2. Ammonium against nitrate: both are raised by thinner snow; the difference is what ammonium did beyond that.
for core in ("NGRIP", "NEEM"):
    diff = {e: D[("ammonium", core, e)] - D[("nitrate", core, e)] for e in events if ("ammonium", core, e) in D and ("nitrate", core, e) in D}
    out[f"ammonium_minus_nitrate_{core}"] = sorted(([e, round(v, 3)] for e, v in diff.items()), key=lambda t: -t[1])

# 3. The average shape: each event's 20-year means divided by its own mean over the 100 years before; the median across the other 24.
prof = {}
for r in csv.DictReader(open("results/profiles.tsv"), delimiter="\t"):
    if r["mean"]:
        prof.setdefault((r["ion"], r["core"], r["event"]), {})[int(r["bin_starts_years_after_onset"])] = float(r["mean"])
shape = {}
for ion in ("ammonium", "calcium"):
    for core in ("NGRIP", "NEEM"):
        rel = {}
        for e in events:
            p = prof.get((ion, core, e), {})
            before = [p[k] for k in (-100, -80, -60, -40, -20) if k in p]
            if len(before) >= 4:
                base = sum(before) / len(before)
                rel[e] = {k: v / base for k, v in p.items()}
        ks = list(range(-300, 300, 20))
        others = [e for e in rel if e != "GS-1"]
        shape[f"{ion}_{core}"] = {"bin": ks,
                                  "median_others": [round(statistics.median([rel[e][k] for e in others if k in rel[e]]), 3) for k in ks],
                                  "quartile_low": [round(statistics.quantiles([rel[e][k] for e in others if k in rel[e]], n=4)[0], 3) for k in ks],
                                  "quartile_high": [round(statistics.quantiles([rel[e][k] for e in others if k in rel[e]], n=4)[2], 3) for k in ks],
                                  "GS-1": [round(rel["GS-1"].get(k, float("nan")), 3) for k in ks],
                                  "n_others": [sum(1 for e in others if k in rel[e]) for k in ks]}
out["shape"] = shape
json.dump(out, open("explore/after.json", "w"), indent=1)
print("two-core mean D:", out["two_core_mean_D"][:8])
for core in ("NGRIP", "NEEM"):
    r = out[f"ammonium_minus_nitrate_{core}"]
    print(core, "ammonium minus nitrate: top", r[:5], "| GS-1 rank", 1 + [e for e, _ in r].index("GS-1"), "of", len(r), "| median others", round(statistics.median([v for e, v in r if e != "GS-1"]), 2))
for key in ("ammonium_NGRIP", "ammonium_NEEM", "calcium_NGRIP"):
    s = shape[key]
    print(key, "after bins 0..280:", [(k, a, b) for k, a, b in zip(s["bin"], s["median_others"], s["GS-1"]) if k >= -40][:17])

# 4. A longer baseline: years 40-160 after against the 200 years before, for coolings whose warm phase lasted that long.
ev_ages = sorted(int(r["age_b2k"]) for r in csv.DictReader(open("events.tsv"), delimiter="\t"))
age = {r["event"]: int(r["age"]) for r in rows}
import math
long_base = {}
for core in ("NGRIP", "NEEM"):
    vals = {}
    for e in events:
        if any(age[e] < a < age[e] + 200 for a in ev_ages):
            continue
        p = prof.get(("ammonium", core, e), {})
        before = [p[k] for k in range(-200, 0, 20) if k in p]
        after = [p[k] for k in range(40, 160, 20) if k in p]
        if len(before) >= 8 and len(after) >= 5:
            vals[e] = math.log((sum(after) / len(after)) / (sum(before) / len(before)))
    long_base[core] = sorted(([e, round(v, 3)] for e, v in vals.items()), key=lambda t: -t[1])
out["D_with_200_year_baseline"] = long_base
json.dump(out, open("explore/after.json", "w"), indent=1)
for core in ("NGRIP", "NEEM"):
    r = long_base[core]
    print(core, "200-year baseline:", len(r), "coolings; top", r[:5], "| GS-1 rank", 1 + [e for e, _ in r].index("GS-1"))
