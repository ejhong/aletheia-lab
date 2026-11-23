#!/usr/bin/env python3
"""Exploratory, after the locked run: what if laboratories' reported errors are too small?

The locked reference world takes each date's reported error at face value. Here the made-up dates are scattered by
k times the reported error (k = 1, 1.5, 2) and then calibrated with the reported error, as real ones would be.
For each k: what the made-up summed curve does on the steep and flat parts of the calibration curve, what ratio of
after to before it expects at the target, where the real record then stands, and whether a halving is still ruled
out. Not part of the protocol; not evidence. Writes explore/error_check.json. Run from questions/younger-dryas-crash.
"""
import json
import sys

import numpy as np

sys.path.insert(0, "analysis")
import crash

G = crash.GRID
mu, sig = crash.read_curve()
dates, _ = crash.read_dates()


def made_up(dens, errs, bins, n_bins, rng, records, k):
    out = np.empty((records, len(G)))
    for r in range(records):
        age = np.empty(len(bins))
        todo = np.ones(n_bins, dtype=bool)
        for _ in range(50):
            if not todo.any():
                break
            t = rng.choice(len(G), size=n_bins, p=dens)
            new = np.rint(mu[t][bins] + (rng.normal(0, 1, n_bins) * sig[t])[bins] + rng.normal(0, 1, len(bins)) * errs * k)
            age[todo[bins]] = new[todo[bins]]
            todo = ~(np.bincount(bins[(age >= crash.AGE_LO) & (age <= crash.AGE_HI)], minlength=n_bins) > 0)
        keep = (age >= crash.AGE_LO) & (age <= crash.AGE_HI)
        size = np.bincount(bins[keep], minlength=n_bins)
        out[r] = (crash.calibrate(age[keep], errs[keep], mu, sig) / size[bins[keep]][:, None]).sum(axis=0)
    return out


out = {}
rng = np.random.default_rng(77)
band = lambda S, lo, hi: S[..., (G >= lo) & (G < hi)].mean(axis=-1)
for region in crash.REGIONS:
    a, e, s = dates[region]
    bins, n_bins = crash.bin_index(a, s)
    S = crash.summed(a, e, bins, mu, sig)
    dens = crash.trend(S)
    real = float(crash.step(S, crash.TARGET))
    res = {"real_ratio_after_to_before": round(float(np.exp(real)), 3),
           "real_steep_over_flat": round(float(band(S, 12600, 12850) / band(S, 12200, 12450)), 3)}
    for k in (1.0, 1.5, 2.0):
        null = made_up(dens, e, bins, n_bins, rng, 400, k)
        halved = made_up(crash.crash_density(dens, 0.5), e, bins, n_bins, rng, 300, k)
        st, sh = crash.step(null, crash.TARGET), crash.step(halved, crash.TARGET)
        res[f"k={k}"] = {"expected_ratio_after_to_before": round(float(np.exp(st.mean())), 3),
                         "expected_steep_over_flat": round(float((band(null, 12600, 12850) / band(null, 12200, 12450)).mean()), 3),
                         "z_of_real_step": round(float((real - st.mean()) / st.std(ddof=1)), 2),
                         "z_of_real_at_12550": round(float((crash.step(S, 12550) - crash.step(null, 12550).mean()) / crash.step(null, 12550).std(ddof=1)), 2),
                         "share_of_halvings_at_or_above_real": round(float((sh >= real).mean()), 3),
                         "halving_expected_ratio": round(float(np.exp(sh.mean())), 3)}
    out[region] = res
    print(region, json.dumps(res))
json.dump(out, open("explore/error_check.json", "w"), indent=1)
