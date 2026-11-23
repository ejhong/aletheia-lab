#!/usr/bin/env python3
"""Exploratory, after the locked run: what the flagged feature looks like. Not part of the protocol; not evidence.

Writes explore/bins20.tsv (series for the figures) and explore/after.json. Run from questions/ice-core-fire.
"""
import json
import sys

import numpy as np

sys.path.insert(0, "analysis")
import fire

out = {}

# 2. The largest 20-year excesses anywhere (not tied to the window grid), keeping one per 300 years.
for name in ("N20", "E20", "G20"):
    b = fire.build(name)
    m_, e, *_ = fire.scores(b.x, 20)
    lo, hi = fire.SERIES[name][4:]
    age = b.a0 + (b.j0 + np.arange(len(e))) * 20
    ok = ~np.isnan(e) & (age >= lo) & (age < hi)
    order = [i for i in np.argsort(-np.where(ok, e, -np.inf)) if ok[i]]
    picked = []
    for i in order:
        if all(abs(age[i] - age[p]) >= 300 for p in picked):
            picked.append(i)
        if len(picked) == 12:
            break
    out[f"largest_20yr_excesses_{name}"] = [{"age": float(age[i]), "excess": round(float(e[i]), 2), "value": round(float(b.x[i]), 2)} for i in picked]

# 3. Where the late-glacial windows stand: the share of each tier series' top ten that starts between 10,300 and 15,000.
s = json.load(open("results/summary.json"))
out["top10_in_10300_to_15000"] = {n: sum(1 for r in rows if r["start"] < 15000) for n, rows in s["alongside"]["top10"].items()}
out["windows_in_10300_to_15000"] = {n: sum(1 for r in fire.windows(n) if r["start"] < 15000) for n in fire.TIER_SERIES}

# 4. Snowfall. NGRIP layer thickness from the depth-age file: the same smoke in half the snow doubles the concentration.
g_age, g_depth = fire.read_gicc05()
lam = lambda a, b: float(np.interp(b, g_age, g_depth) - np.interp(a, g_age, g_depth)) / (b - a) * 100
out["ngrip_layer_cm_per_year"] = {"12750-12890 (after the onset)": round(lam(12750, 12890), 2), "12900-13050 (before the onset)": round(lam(12900, 13050), 2),
                                  "13650-13950": round(lam(13650, 13950), 2), "12150-12450": round(lam(12150, 12450), 2), "11400-11700": round(lam(11400, 11700), 2)}
rows = [r for r in fire.windows("N20") if r["start"] < 15000 and not np.isnan(r["E"])]
flux = sorted(((r["E"] * lam(r["E_age"] - 40, r["E_age"] + 60), r["start"], r["E"], r["E_age"]) for r in rows), reverse=True)
out["N20_excess_times_layer_thickness_10300_to_15000"] = [{"start": st, "E": round(E, 1), "E_age": a, "E_x_layer": round(fl, 1)} for fl, st, E, a in flux]

# 5. The target window bin by bin, 20-year series.
for name in ("N20", "E20", "G20"):
    b = fire.build(name)
    m_, e, *_ = fire.scores(b.x, 20)
    out[f"target_bins_{name}"] = [{"start": b.a0 + j * 20, "value": round(float(b.get(j, j + 1)[0]), 2), "excess": round(float(b.get(j, j + 1, e)[0]), 2)} for j in range(-10, 25)]
json.dump(out, open("explore/after.json", "w"), indent=1)
for k in ("largest_20yr_excesses_N20", "largest_20yr_excesses_E20", "largest_20yr_excesses_G20"):
    print(k, [(int(r["age"]), r["excess"]) for r in out[k]])
print(out["top10_in_10300_to_15000"], out["windows_in_10300_to_15000"])
print(out["ngrip_layer_cm_per_year"])
print("flux-like order:", [(int(r["start"]), r["E"], r["E_x_layer"]) for r in out["N20_excess_times_layer_thickness_10300_to_15000"]])
for n in ("N20", "E20", "G20"):
    print(n, [(int(r["start"]), r["value"]) for r in out[f"target_bins_{n}"]])

# 6. Twenty-year bins from 10,300 to 16,000 years, all three cores, for the figures.
with open("explore/bins20.tsv", "w") as f:
    f.write("series\tstart\tvalue\n")
    for name in ("N20", "E20", "G20"):
        b = fire.build(name)
        for j in range(int(np.ceil((10300 - b.a0) / 20)), int((16000 - b.a0) // 20)):
            v = b.get(j, j + 1)[0]
            f.write(f"{name}\t{b.a0 + j * 20:.0f}\t{'' if np.isnan(v) else round(float(v), 2)}\n")
