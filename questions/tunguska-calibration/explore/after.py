#!/usr/bin/env python3
"""Exploratory, after the locked result: where inside the years do the 1908 spikes fall, and is there soot with them?

For each core with a clear ammonium spike in 1906 to 1910: the date of its largest sample in those years, how many
times the core's typical sample that is, how wide the spike is (samples above three times typical around the
peak), black carbon and nitrate at the peak against their typical values, and the gap in years to the core's
sulphur peak from Katmai (1911 to 1915). Dates inside a year are interpolated between yearly markers and are good
to perhaps a season. Not part of the protocol; not evidence. Run from questions/tunguska-calibration.
"""
import json
import sys

import numpy as np

sys.path.insert(0, "analysis")
import tunguska as t

out = {}
for core in t.CORES:
    a = t.load(core)
    yr, nh4 = a[:, 0], a[:, 1]
    m = (yr >= 1906) & (yr < 1911) & np.isfinite(nh4)
    ref = (yr >= 1880) & (yr < 1930) & np.isfinite(nh4)
    if m.sum() < 5:
        continue
    typ = float(np.median(nh4[ref]))
    i = np.where(m)[0][np.argmax(nh4[m])]
    lo = hi = i
    while lo - 1 >= 0 and np.isfinite(nh4[lo - 1]) and nh4[lo - 1] > 3 * typ:
        lo -= 1
    while hi + 1 < len(a) and np.isfinite(nh4[hi + 1]) and nh4[hi + 1] > 3 * typ:
        hi += 1
    rec = {"site": t.CORES[core][0], "peak_date": round(float(yr[i]), 2), "peak_over_typical_sample": round(float(nh4[i] / typ), 1),
           "spike_from": round(float(yr[lo]), 2), "spike_to": round(float(yr[hi]), 2), "samples_in_spike": int(hi - lo + 1)}
    for sp, col in (("no3", 2), ("bc", 3)):
        v = a[:, col]
        if np.isfinite(v[ref]).sum() > 50:
            seg = v[lo:hi + 1]
            if np.isfinite(seg).any():
                rec[sp + "_in_spike_over_typical"] = round(float(np.nanmax(seg) / np.nanmedian(v[ref])), 1)
    s = a[:, 4]
    k = (yr >= 1911) & (yr < 1916) & np.isfinite(s)
    if k.sum():
        rec["years_to_katmai_sulphur_peak"] = round(float(yr[np.where(k)[0][np.argmax(s[k])]] - yr[i]), 1)
    # the largest sample in each year 1906..1910, as a multiple of the typical sample
    rec["largest_sample_by_year"] = {int(y): round(float(np.nanmax(nh4[(yr >= y) & (yr < y + 1)]) / typ), 1)
                                     for y in range(1906, 1911) if np.isfinite(nh4[(yr >= y) & (yr < y + 1)]).any()}
    out[core] = rec
    print(core, json.dumps(rec))
json.dump(out, open("explore/after.json", "w"), indent=1)
