#!/usr/bin/env python3
"""Exploratory, before the lock: the layout and coverage of the radiocarbon database.

Counts dates and sites by continent over a broad span of radiocarbon ages. No calibration, no curve of dates
through time, nothing finer than the totals below. Run from questions/younger-dryas-crash.
"""
import collections
import csv

rows = list(csv.DictReader(open("data/p3k14c_scrubbed_fuzzed.csv", encoding="utf-8")))
print(len(rows), "dates; columns:", list(rows[0].keys()))
ok = []
bad = collections.Counter()
for r in rows:
    try:
        a, e = float(r["Age"]), float(r["Error"])
    except ValueError:
        bad["age or error not a number"] += 1
        continue
    if e <= 0:
        bad["error not positive"] += 1
        continue
    ok.append((r, a, e))
print("unusable:", dict(bad))
span = [(r, a, e) for r, a, e in ok if 8500 <= a <= 14000]
print(len(span), "dates with radiocarbon ages 8,500 to 14,000")
by = collections.defaultdict(list)
for r, a, e in span:
    by[r["Continent"]].append((r, a, e))
for c, v in sorted(by.items(), key=lambda kv: -len(kv[1])):
    errs = sorted(e for _, _, e in v)
    sites = {(r["SiteID"] or r["SiteName"]) for r, _, _ in v}
    nosite = sum(1 for r, _, _ in v if not (r["SiteID"] or r["SiteName"]))
    print(f"{c:16s} dates {len(v):6d}  sites {len(sites):5d}  no site name {nosite:4d}  error median {errs[len(errs) // 2]:.0f}, 90th pct {errs[int(len(errs) * 0.9)]:.0f}, over 200: {sum(1 for e in errs if e > 200)}")
na = collections.Counter(r["Country"] for r, _, _ in by.get("North America", []))
print("North America by country:", na.most_common(8))
print("SiteID present:", sum(1 for r, _, _ in span if r["SiteID"]), "SiteName present:", sum(1 for r, _, _ in span if r["SiteName"]))
print("materials (top):", collections.Counter(r["Material"] for r, _, _ in span).most_common(6))
