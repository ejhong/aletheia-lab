#!/usr/bin/env python3
"""Exploratory, before the lock: the layout, coverage and resolution of each file.

Deliberately prints no concentration from 12,000 to 14,000 years ago, so the protocol can be written without knowing
how the Younger Dryas onset looks. Run from questions/ice-core-fire with the shared venv (needs numpy).
"""
import numpy as np

D = "data/"


def pangaea(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.startswith("*/"):
                break
        header = next(f).rstrip("\n").split("\t")
        for line in f:
            rows.append([float(x) if x else np.nan for x in line.rstrip("\n").split("\t")] + [np.nan] * 6)
    return header, np.array([r[:6] for r in rows])


for name, fid in (("NGRIP", "935814"), ("NEEM", "935831")):
    h, a = pangaea(D + f"pangaea/{fid}.tab")
    age = a[:, 0] * 1000
    print(f"{name} decadal: {len(a)} rows, {age.min():.0f} to {age.max():.0f} yr b2k, step {np.median(np.diff(age)):.0f}; columns {h}")
    out = ~((age >= 12000) & (age <= 14000))
    print(f"  medians outside 12-14 ka: NH4 {np.nanmedian(a[out, 4]):.2f}, NO3 {np.nanmedian(a[out, 5]):.1f} ug/kg")
    edges = np.arange(0, 131000, 10000)
    print("  NH4 coverage by 10 kyr:", " ".join(f"{np.mean(~np.isnan(a[(age >= lo) & (age < lo + 10000), 4])):.2f}" if ((age >= lo) & (age < lo + 10000)).any() else "--" for lo in edges[:-1]))
    w = (age >= 12750) & (age < 13050)
    print(f"  rows in 12,750-13,050: {w.sum()}, NH4 present {int((~np.isnan(a[w, 4])).sum())}, NO3 present {int((~np.isnan(a[w, 5])).sum())}")

# NGRIP depth-age (GICC05, 20-year steps to 60 ka)
da = []
for line in open(D + "noaa/gicc05-60ka-20yr.txt", encoding="latin-1"):
    p = line.split()
    if len(p) == 4:
        try:
            da.append((float(p[0]), float(p[1])))
        except ValueError:
            pass
da = np.array(da)
print(f"GICC05 20-yr file: {len(da)} rows, age {da[0, 0]:.0f}-{da[-1, 0]:.0f} b2k, depth {da[0, 1]}-{da[-1, 1]} m")
lam = np.diff(da[:, 1]) / np.diff(da[:, 0]) * 100
for lo in range(10000, 60000, 5000):
    m = (da[1:, 0] > lo) & (da[1:, 0] <= lo + 5000)
    print(f"  layer thickness {lo // 1000}-{lo // 1000 + 5} ka: median {np.median(lam[m]):.2f} cm/yr, min {lam[m].min():.2f}")
print("  depth at 12,750 / 12,900 / 13,050 b2k:", np.interp([12750, 12900, 13050], da[:, 0], da[:, 1]).round(2))

# NGRIP 1 mm: depth range and missing share only
dep, nh4 = [], []
with open(D + "pangaea/935818.tab", encoding="utf-8") as f:
    for line in f:
        if line.startswith("*/"):
            break
    next(f)
    for line in f:
        p = line.rstrip("\n").split("\t")
        dep.append(float(p[0]))
        nh4.append(float(p[4]) if len(p) > 4 and p[4] else np.nan)
dep, nh4 = np.array(dep), np.array(nh4)
age = np.interp(dep, da[:, 1], da[:, 0], left=np.nan, right=np.nan)
print(f"NGRIP 1 mm: {len(dep)} rows, depth {dep.min()}-{dep.max()} m, step {np.median(np.diff(dep)) * 1000:.1f} mm, NH4 present {np.mean(~np.isnan(nh4)):.2f}")
print(f"  rows with a GICC05 age (to 60 ka): {int((~np.isnan(age)).sum())}; age range {np.nanmin(age):.0f}-{np.nanmax(age):.0f}")
for lo in range(10000, 60000, 5000):
    m = (age >= lo) & (age < lo + 5000)
    print(f"  NH4 coverage {lo // 1000}-{lo // 1000 + 5} ka: {np.mean(~np.isnan(nh4[m])):.2f}")
deep = (dep > 2000) & (dep < 2100)
print(f"  median NH4 2000-2100 m: {np.nanmedian(nh4[deep]):.2f} ug/kg (a check on the column order)")

# GISP2 discrete ions
rows = []
started = False
for line in open(D + "noaa/iond.txt", encoding="latin-1"):
    p = line.rstrip("\n").split("\t")
    if p[0] == "Top":
        started = True
        continue
    if started and len(p) >= 12:
        try:
            rows.append([float(x) if x.strip() else np.nan for x in p[:12]])
        except ValueError:
            pass
g = np.array(rows)
dur = g[:, 11] - g[:, 10]
print(f"GISP2: {len(g)} samples, depth {g[0, 0]}-{g[-1, 1]} m, age {g[0, 10]:.0f} to {np.nanmax(g[:, 11]):.0f} yr BP")
for lo in list(range(0, 20000, 2500)) + list(range(20000, 110000, 15000)):
    hi = lo + (2500 if lo < 20000 else 15000)
    m = (g[:, 10] >= lo) & (g[:, 10] < hi)
    if m.any():
        print(f"  {lo:6d}-{hi:6d} BP: {m.sum():5d} samples, years per sample median {np.nanmedian(dur[m]):.1f}, 90th pct {np.nanpercentile(dur[m], 90):.1f}, max {np.nanmax(dur[m]):.1f}; NH4 present {np.mean(~np.isnan(g[m, 3])):.2f}")
m = (g[:, 0] < 1712.3) & (g[:, 1] > 1712.0)
for r in g[m]:
    print(f"  near the platinum depth: {r[0]}-{r[1]} m = {r[10]:.1f}-{r[11]:.1f} yr BP")
m = (g[:, 10] >= 12000) & (g[:, 11] <= 14000)
print(f"  12-14 ka: {m.sum()} samples, years per sample median {np.nanmedian(dur[m]):.2f}, max {np.nanmax(dur[m]):.2f}")
