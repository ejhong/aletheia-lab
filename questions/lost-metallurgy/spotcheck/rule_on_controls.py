#!/usr/bin/env python3
"""Would the locked Positive rule (sustained >=2 consecutive 25-yr bins with EF>=3) fire on the positive-control eras themselves?
Also: details of the Füramoos 7.48 ka renormalised run, EPICA Pb/Ba z-scores. Usage: python -I rule_on_controls.py <question_dir>"""
import sys, json
from pathlib import Path
import numpy as np
Q = Path(sys.argv[1]); sys.path.insert(0, str(Q / "analysis"))
import run_metallurgy as rm
from scipy.stats import mannwhitneyu
rm.DATA_DIR = Q / "data"
import csv
ages, pb, ce, s = [], [], [], []
with open(rm.DATA_DIR / "recap_8kyr.csv", encoding="utf-8", errors="replace") as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row) < 15: continue
        a, p, c, sv = (rm.parse_float(row[i]) for i in (2, 14, 13, 9))
        if a is not None and p and c and p > 0 and c > 0:
            ages.append(a); pb.append(p); ce.append(c); s.append(sv if sv and sv > 0 else np.nan)
ages, pb, ce, s = map(np.array, (ages, pb, ce, s))
nv = ~rm.volcanic_mask_sulfur(ages, s)
k = np.median((pb / ce)[nv & (ages >= 5000)]); ef = pb / ce / k
nc = np.maximum(0, pb - k * ce)
b25 = rm.bin_medians(ages[nv], ef[nv], 25.0, 100.0, 8000.0)
out = {}
for nm, lo, hi in (("bronze_5_3", 3000, 5000), ("iron_3_2.15", 2150, 3000), ("roman", 1650, 2150), ("medieval", 500, 1000), ("industrial", 100, 250)):
    bb = [b for b in b25 if lo <= b["age_lo"] < hi]
    pairs = [(bb[i]["age_lo"], bb[i + 1]["age_hi"]) for i in range(len(bb) - 1) if bb[i]["median"] >= 3 and bb[i + 1]["median"] >= 3]
    out[nm] = {"n25": len(bb), "max25_ef": round(max(b["median"] for b in bb), 3), "n25_ge3": sum(b["median"] >= 3 for b in bb), "sustained_pairs_ge3": pairs,
               "n25_ge2": sum(b["median"] >= 2 for b in bb)}
# medieval century-level MWU
b100 = rm.bin_medians(ages[nv], ef[nv], 100.0, 100.0, 8000.0)
pre = [b["median"] for b in b100 if b["age_lo"] >= 5000]
med = [b["median"] for b in b100 if 500 <= b["age_lo"] < 1000]
out["mwu_centuries_medieval_vs_pre"] = float(mannwhitneyu(med, pre, alternative="greater").pvalue)
out["medieval_centuries_ef"] = [round(x, 3) for x in med]
# Fraction of pre-5 ka samples with ncPb clipped to zero
out["pre5_frac_ncpb_zero"] = float((nc[nv & (ages >= 5000)] == 0).mean())
print(json.dumps({"recap_rule_on_controls": out}, indent=1))
# Füramoos renormalised run detail
xl = (rm.DATA_DIR / "furamoos_xrf_929755.tab").read_text(encoding="utf-8").splitlines()
xs = next(i for i, l in enumerate(xl) if l.strip() == "*/") + 2
X = []
for l in xl[xs:]:
    p = l.split("\t")
    if len(p) >= 4 and all(rm.parse_float(v) is not None for v in p[:4]): X.append([float(v) for v in p[:4]])
X = np.array(X); X = X[np.argsort(X[:, 1])]
med_pre = np.median(X[X[:, 1] >= 5, 3])
i = np.where((X[:, 1] > 7.40) & (X[:, 1] < 7.60))[0]
print("Füramoos XRF rows 7.40-7.60 ka (depth, age ka, Pb norm, EF_pub, EF_renorm):")
for j in i: print(" ", X[j, 0], X[j, 1], round(X[j, 2], 1), round(X[j, 3], 3), round(X[j, 3] / med_pre, 3))
pre_rows = X[X[:, 1] >= 5]
top = pre_rows[np.argsort(-pre_rows[:, 3])][:12]
print("Top-12 pre-5ka published EF (age ka, EF_pub, renorm):", [(round(a, 3), round(e, 2), round(e / med_pre, 2)) for a, e in zip(top[:, 1], top[:, 3])])
# EPICA Pb/Ba z
lines = (rm.DATA_DIR / "edc_217kyr_pb_ba.txt").read_text(encoding="latin-1").splitlines()
st = next(i for i, l in enumerate(lines) if l.strip().startswith("Depth") and "206Pb/207Pb" in l) + 1
E = np.array([[float(p[1]), float(p[3]), float(p[11])] for p in (l.split() for l in lines[st:]) if len(p) >= 12])
base = E[E[:, 0] >= 40]
mu, sd = base[:, 2].mean(), base[:, 2].std(ddof=1)
imu, isd = base[:, 1].mean(), base[:, 1].std(ddof=1)
w = E[(E[:, 0] >= 5) & (E[:, 0] < 40)]
print("EPICA baseline Pb/Ba mean, sd:", round(mu, 4), round(sd, 4), " iso mean sd", round(imu, 4), round(isd, 4))
print("EPICA 40-5 ka samples with |z|>2 in Pb/Ba or 206/207:", [(a, r206, pba, round((pba - mu) / sd, 2), round((r206 - imu) / isd, 2)) for a, r206, pba in w if abs((pba - mu) / sd) > 2 or abs((r206 - imu) / isd) > 2])
