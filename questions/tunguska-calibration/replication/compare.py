#!/usr/bin/env python3
"""Compare a replication's summary.json with ours.   python3 replication/compare.py replication/work/google"""
import json
import sys

ours = json.load(open("results/summary.json"))
theirs = json.load(open(sys.argv[1] + "/summary.json"))
bad = 0


def same(a, b, tol=2e-3):
    if a is None or b is None:
        return a is None and b is None
    return all(abs(a[k] - b[k]) <= (tol if k in ("value", "fraction") else 0) for k in ("value", "rank", "n", "fraction"))


for sp in ("nh4", "no3", "bc", "s"):
    o, t = ours[sp], theirs[sp]
    line = [f"{sp}: verdict {o['verdict']} / {t['verdict']}", f"network {o['network']} / {t['network']}", f"sites same: {o['sites'] == t['sites']}",
            f"windows {o['windows']} / {t['windows']}"]
    ok = o["verdict"] == t["verdict"] and same(o["network"], t["network"]) and o["sites"] == t["sites"]
    site_bad = [s for s in o["by_site"] if not same(o["by_site"][s], t["by_site"].get(s))]
    ex_bad = [s for s in o["excess_over_typical_year"] if abs(o["excess_over_typical_year"][s] - t["excess_over_typical_year"].get(s, 9e9)) > 2e-3]
    var_bad = [k for k in t["variants"] if k in o["variants"] and (o["variants"][k]["verdict"] != t["variants"][k]["verdict"] or not same(o["variants"][k]["network"], t["variants"][k]["network"]))]
    var_missing = [k for k in o["variants"] if k not in t["variants"] and "doubtful" not in k]
    apart_bad = [c for c in o["reported_apart"] if c in t["reported_apart"] and not same(o["reported_apart"][c]["rank"], t["reported_apart"][c]["rank"])]
    top_same = [w[1] for w in o["top_windows"][:5]] == [w[1] for w in t["top_windows"][:5]]
    print(" | ".join(line))
    print(f"   by-site differences: {site_bad or 'none'}; size differences: {ex_bad or 'none'}; variant differences: {var_bad or 'none'}"
          f"; variants missing: {var_missing or 'none'}; apart differences: {apart_bad or 'none'}; top five windows same: {top_same}")
    bad += (not ok) + bool(site_bad) + bool(ex_bad) + bool(var_bad) + bool(apart_bad) + (not top_same)
    if sp == "s":
        print("   Katmai window:", o["katmai_window_1912"], "/", t.get("katmai_window_1912"))
    if sp == "nh4":
        for k in o["power"]:
            if k in t.get("power", {}):
                print(f"   power {k}: ours {o['power'][k]} theirs {t['power'][k]}")
print("ALL AGREE" if not bad else f"{bad} kinds of difference")
