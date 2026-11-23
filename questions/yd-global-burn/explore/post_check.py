#!/usr/bin/env python3
"""Post-result exploratory inspection (strictly after locking and running burn.py).

Reads raw Taylor Glacier and WAIS Divide rows around 12.0-13.5 ka and 15.8-17.2 ka,
plus per-site Tier C1 and C3_coarse charcoal values in k=0 [12650, 12950) cal BP,
to verify timing and physical interpretation for RESULTS.md and site figures.
"""

from __future__ import annotations

import json
import pathlib
import sys
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "analysis"))
import burn

BASE = pathlib.Path(__file__).resolve().parent.parent
NOAA = BASE / "data" / "noaa"
CSV_DIR = BASE / "data" / "gcd_csv"

tg_a, tg_c, tg_d = burn.load_taylor(NOAA / "taylor2018d13co2.txt")
print("=== Raw Taylor Glacier points 12,000 - 13,600 cal BP (oldest to youngest) ===")
mask = (tg_a >= 12000) & (tg_a <= 13600)
for a, c, d in reversed(list(zip(tg_a[mask], tg_c[mask], tg_d[mask]))):
    print(f"  {a:8.1f} BP | CO2={c:6.2f} ppm | d13C={d:7.3f} permil")

print("\n=== Raw Taylor Glacier points 15,800 - 17,200 cal BP (HS1, oldest to youngest) ===")
mask2 = (tg_a >= 15800) & (tg_a <= 17200)
for a, c, d in reversed(list(zip(tg_a[mask2], tg_c[mask2], tg_d[mask2]))):
    print(f"  {a:8.1f} BP | CO2={c:6.2f} ppm | d13C={d:7.3f} permil")

# Compute mass balance for k=-1 [12350, 12650) too
_, _, tg_diag = burn.compute_taylor_windows(tg_a, tg_c, tg_d)
for k_chk, label in [(0, "YD onset k=0 [12650,12950)"), (-1, "Mid-YD k=-1 [12350,12650)"), (12, "HS1 k=12 [16250,16550)"), (90, "HS4 k=90 [39650,39950)")]:
    if k_chk in tg_diag:
        bb = tg_diag[k_chk]["best_burn"]
        mb = burn.physical_mass_balance(bb["co2_old"], bb["d13_old"], bb["d13_young"])
        print(f"\n  {label}:")
        print(f"    step {bb['t_old_bp']:.0f} -> {bb['t_young_bp']:.0f} BP: dCO2={bb['dco2']:+.2f} ppm, d13drop={bb['d13_drop']:+.4f} permil, BURN={bb['burn']:.4f}")
        print(f"    mass balance: dC_air={mb['delta_c_air_gtc']} GtC (implied CO2={mb['implied_co2_rise_ppm']} ppm), emitted@50%={mb['emitted_af50_gtc']} GtC, emitted@25%={mb['emitted_af25_gtc']} GtC")

# Inspect Tier C1 sites in k=0 and Tier C3_coarse sites >= 1.5 SD in k=0
sites = burn.load_gcd3(CSV_DIR)
tiers = burn.select_gcd_tiers(sites, *burn.GCD_PRIMARY_SPAN)
print("\n=== Tier C1 sites in k=0 [12650, 12950) cal BP ===")
c1_rows = []
for s in tiers["C1"]:
    m = (s["ages"] >= 12650) & (s["ages"] < 12950)
    zv = float(np.mean(s["z"][m])) if np.any(m) else float("nan")
    c1_rows.append((zv, s["id_site"], s["site_name"], s["macro_region"], int(m.sum()), s["med_dt"]))
for zv, sid, name, reg, ns, dt in sorted(c1_rows, key=lambda x: -(x[0] if np.isfinite(x[0]) else -99)):
    print(f"  z={zv:+6.3f} | n_samp={ns:2d} | med_dt={dt:5.1f} | {reg:23s} | #{sid} {name}")

print("\n=== Tier C3_coarse sites with z >= 1.5 in k=0 [12650, 12950) ===")
for s in tiers["C3_coarse"]:
    m = (s["ages"] >= 12650) & (s["ages"] < 12950)
    if np.any(m):
        zv = float(np.mean(s["z"][m]))
        if zv >= 1.5:
            print(f"  z={zv:+6.3f} | n_samp={int(m.sum()):2d} | med_dt={s['med_dt']:6.1f} | {s['macro_region']:23s} | #{s['id_site']} {s['site_name']}")

# Save compact exploratory JSON for figures (raw TG/WAIS profiles around YD and HS1)
w_a, w_c = burn.load_wais(NOAA / "antarctica2015co2wais-noaa.txt")
w_yd = (w_a >= 11500) & (w_a <= 14000)
tg_yd = (tg_a >= 11500) & (tg_a <= 14000)
tg_hs1 = (tg_a >= 15200) & (tg_a <= 17700)
after = {
    "tg_yd": [{"age": float(a), "co2": float(c), "d13c": float(d)} for a, c, d in zip(tg_a[tg_yd], tg_c[tg_yd], tg_d[tg_yd])],
    "tg_hs1": [{"age": float(a), "co2": float(c), "d13c": float(d)} for a, c, d in zip(tg_a[tg_hs1], tg_c[tg_hs1], tg_d[tg_hs1])],
    "wais_yd": [{"age": float(a), "co2": float(c)} for a, c in zip(w_a[w_yd], w_c[w_yd])],
}
(BASE / "explore" / "post_check.json").write_text(json.dumps(after, indent=2) + "\n", encoding="utf-8")
