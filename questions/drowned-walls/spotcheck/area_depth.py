"""Recompute valid area and depth distribution from the cached tiles."""
import math, json
import numpy as np
from sens_common import load_tiles, A
specs, tiles = load_tiles()
tot = tot104 = 0; allz = []; reg = {}
for sp in specs:
    if sp["is_control"]: continue
    _, z = tiles[sp["id"]]
    lon0, lat0, lon1, lat1 = sp["bbox"]; latc = (lat0 + lat1) / 2
    # WGS84 metres per degree
    mlat = 111132.92 - 559.82 * math.cos(2 * math.radians(latc)) + 1.175 * math.cos(4 * math.radians(latc))
    mlon = 111412.84 * math.cos(math.radians(latc)) - 93.5 * math.cos(3 * math.radians(latc))
    area = (lat1 - lat0) * mlat * (lon1 - lon0) * mlon / 1e6
    v = np.isfinite(z) & (z >= -120) & (z <= -2)
    frac = v.mean() if v.mean() >= 0.03 else v.mean()
    tot += area * frac; tot104 += 1.04 * frac
    r = sp["region"]; reg.setdefault(r, [0, 0, []]); reg[r][0] += area * frac; reg[r][1] += 1.04 * frac
    if v.any(): allz.append(z[v]); reg[r][2].append(z[v])
    if sp["id"] == "CA_ANACAPA_01": print("tile area km2 example", round(area, 4), "px size m", round((lat1-lat0)*mlat/512, 3), round((lon1-lon0)*mlon/512, 3))
z = np.concatenate(allz)
print("valid area km2 (exact tile area):", round(tot, 3), " with program's 1.04 km2/tile:", round(tot104, 3))
print("NOTE includes tiles below 3% valid counted at their tiny fraction")
print("depth range of valid pixels:", round(float(z.min()), 2), round(float(z.max()), 2), "median", round(float(np.median(z)), 2))
for lo, hi in ((-120, -80), (-80, -10), (-10, -2)):
    print(f"  fraction of valid pixels in [{lo},{hi}):", round(float(((z >= lo) & (z < hi)).mean()), 4))
for r, (a, a104, zz) in reg.items():
    zz = np.concatenate(zz); print(r, round(a, 2), round(a104, 2), "depth", round(float(zz.min()), 1), round(float(np.percentile(zz, 50)), 1), round(float(zz.max()), 1))
