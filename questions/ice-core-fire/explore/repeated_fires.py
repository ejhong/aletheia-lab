#!/usr/bin/env python3
"""Exploratory, after the result: does the century of high ammonium look like many separate fires?

Asked by Eugene on 23 November 2026: what if a broken-up comet in the Taurid stream gave airbursts year after year
for a long time, and not one strike? Smoke from a fire reaches Greenland as a plume lasting days, so repeated
fires should show as short spikes standing above the year's ordinary level. A change in the steady output of
soils and plants raises the ordinary level itself.

NGRIP ammonium at 1 mm (about 30 samples a year here), 10,400 to 15,000 years before 2000. For each year: the
median sample (the ordinary level), the mean, and the largest sample. A "spike year" has its largest sample above
3, 5 or 10 times the running median, over 51 years, of the yearly medians. Years are grouped in 150-year windows
laid out from the onset (12,896), so window 0 is the 150 years after the cold began and window -1 the 150 before.

Not part of the locked protocol; not evidence. Yearly fires and a raised steady level cannot be told apart by this
if the fires came every year in the same season. Writes explore/repeated_fires.json.
Run from questions/ice-core-fire:  .venv/bin/python explore/repeated_fires.py
"""
import json
import sys

import numpy as np

sys.path.insert(0, "analysis")
import fire

ONSET, LO, HI, W = 12896, 10400, 15000, 150
r = fire.raw("ngrip_mm")
ok = ~np.isnan(r[:, 0]) & ~np.isnan(r[:, 1]) & (r[:, 0] >= LO) & (r[:, 0] < HI)
age, val = r[ok, 0], r[ok, 1]
year = np.floor(age).astype(int)
years = np.arange(LO, HI)
med = np.full(len(years), np.nan)
mean = np.full(len(years), np.nan)
top = np.full(len(years), np.nan)
order = np.argsort(year, kind="stable")
ys, vs = year[order], val[order]
cuts = np.searchsorted(ys, np.arange(LO, HI + 1))
for i in range(len(years)):
    v = vs[cuts[i]:cuts[i + 1]]
    if len(v) >= 15:
        med[i], mean[i], top[i] = np.median(v), v.mean(), v.max()
run = np.full(len(years), np.nan)
for i in range(len(years)):
    w = med[max(0, i - 25):i + 26]
    if np.isfinite(w).sum() >= 30:
        run[i] = np.nanmedian(w)
ratio = top / run
out = {"years_with_data": int(np.isfinite(med).sum()), "samples_per_year_median": float(np.median(np.diff(cuts)[np.isfinite(med)]))}
wins = []
k = int(np.floor((ONSET - HI) / W))
while ONSET - W * (k + 1) >= LO:
    lo, hi = ONSET - W * (k + 1), ONSET - W * k
    if hi <= HI:
        m = (years >= lo) & (years < hi) & np.isfinite(ratio)
        if m.sum() >= 0.8 * W:
            wins.append({"k": k, "from": hi, "to": lo, "years": int(m.sum()),
                         "level": round(float(np.nanmean(med[m])), 2), "spike_part": round(float(np.nanmean((mean - med)[m])), 2),
                         **{f"spike_years_x{t}": int((ratio[m] > t).sum()) for t in (3, 5, 10)},
                         "largest_ratio": round(float(np.nanmax(ratio[m])), 1)})
    k += 1
out["windows"] = wins
by = {w["k"]: w for w in wins}
for key in ("level", "spike_part", "spike_years_x3", "spike_years_x5", "spike_years_x10", "largest_ratio"):
    vals = [w[key] for w in wins]
    out["rank_" + key] = {name: [1 + sum(v > by[kk][key] for v in vals), len(vals), by[kk][key]] for name, kk in (("after", 0), ("before", -1))}
    out["median_" + key] = float(np.median(vals))
a, b = by[0], by[-1]
out["after_over_before"] = {"level": round(a["level"] / b["level"], 2), "spike_part": round(a["spike_part"] / b["spike_part"], 2)}
out["share_of_rise_from_level"] = round((a["level"] - b["level"]) / ((a["level"] + a["spike_part"]) - (b["level"] + b["spike_part"])), 2)
json.dump(out, open("explore/repeated_fires.json", "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "windows"}, indent=1))
for w in wins:
    if -3 <= w["k"] <= 4:
        print(w)
