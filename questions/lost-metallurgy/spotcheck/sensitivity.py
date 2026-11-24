#!/usr/bin/env python3
"""Second-pass checks for lost-metallurgy (#82): injection-recovery of the locked rules, coverage,
Füramoos protocol-EF anomalies and chance coincidence, Laphroaig ('Store Mosse') raw Pb, volcanic mask.
Reads data as untrusted input; run with python -I.  Usage: python -I sensitivity.py <question_dir> <out_json>
"""
import csv
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.stats import mannwhitneyu

Q = Path(sys.argv[1]); OUT = Path(sys.argv[2]); D = Q / "data"
sys.path.insert(0, str(Q / "analysis"))  # the study's own helpers, already read
from run_metallurgy import volcanic_mask_sulfur, bin_medians, parse_float  # noqa: E402

R = {}

# ---------------- RECAP load ----------------
ages, pb, ce, s = [], [], [], []
with open(D / "recap_8kyr.csv", encoding="utf-8", errors="replace") as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row) < 15:
            continue
        a, p, c, sv = (parse_float(row[i]) for i in (2, 14, 13, 9))
        if a is None or p is None or c is None or p <= 0 or c <= 0:
            continue
        ages.append(a); pb.append(p); ce.append(c); s.append(sv if sv and sv > 0 else np.nan)
ages, pb, ce, s = map(np.array, (ages, pb, ce, s))
vm = volcanic_mask_sulfur(ages, s); nv = ~vm


def locked_rule_recap(pb_arr):
    """Apply the study's RECAP pipeline to a (possibly modified) Pb array; return what the locked rules say."""
    ratio = pb_arr / ce
    k = float(np.median(ratio[nv & (ages >= 5000)]))
    ef = ratio / k
    nc = np.maximum(0.0, pb_arr - k * ce)
    rom = nv & (ages >= 1650) & (ages < 2150)
    rom_nc = float(np.median(nc[rom]))
    b25e = [b for b in bin_medians(ages[nv], ef[nv], 25.0, 100.0, 8000.0) if b["age_lo"] >= 5000]
    b25n = [b for b in bin_medians(ages[nv], nc[nv], 25.0, 100.0, 8000.0) if b["age_lo"] >= 5000]
    ef3 = [(b25e[i]["age_lo"], b25e[i + 1]["age_hi"]) for i in range(len(b25e) - 1)
           if b25e[i]["median"] >= 3 and b25e[i + 1]["median"] >= 3]
    r50 = [(b25n[i]["age_lo"], b25n[i + 1]["age_hi"]) for i in range(len(b25n) - 1)
           if b25n[i]["median"] >= 0.5 * rom_nc and b25n[i + 1]["median"] >= 0.5 * rom_nc]
    b100 = [b for b in bin_medians(ages[nv], ef[nv], 100.0, 100.0, 8000.0) if b["age_lo"] >= 5000]
    # Positive (locked): sustained EF>=3 AND (>=50% Roman OR replication). Replication not available here,
    # so report EF>=3 sustained and the 50%-Roman arm separately.
    return {"k": k, "n_sust_ef3": len(ef3), "n_sust_50rom": len(r50), "max_century_ef": max(b["median"] for b in b100),
            "pre5_median_ef": float(np.median(ef[nv & (ages >= 5000)])), "roman_nc_pg": rom_nc * 1000}


base = locked_rule_recap(pb)
k0 = base["k"]
nc0 = np.maximum(0, pb - k0 * ce)
rom_nc0 = float(np.median(nc0[nv & (ages >= 1650) & (ages < 2150)]))  # ng/g
R["recap_baseline"] = base

# Injection: add X * (Roman median ncPb) to every sample in a pulse window; test locked rules.
inj = []
for dur, (lo, hi) in (("100yr", (6400, 6500)), ("300yr", (6300, 6600)), ("1000yr", (6000, 7000)), ("whole_window_3000yr", (5000, 8000))):
    for X in (0.5, 1, 2, 3, 4, 5, 6, 8):
        pbx = pb.copy()
        m = (ages >= lo) & (ages < hi)
        pbx[m] = pbx[m] + X * rom_nc0
        out = locked_rule_recap(pbx)
        inj.append({"pulse": dur, "x_roman": X, "sust_ef3_pairs": out["n_sust_ef3"], "sust_50rom_pairs": out["n_sust_50rom"],
                    "max_century_ef": round(out["max_century_ef"], 2), "pre5_median_ef": round(out["pre5_median_ef"], 2)})
R["recap_injection"] = inj

# What multiple of the Roman median excess makes EF>=3 at a typical pre-5ka sample?
ce_pre = float(np.median(ce[nv & (ages >= 5000)]))
R["recap_ef3_requires_excess_pg_g"] = 2 * k0 * ce_pre * 1000
R["recap_ef3_requires_x_roman"] = 2 * k0 * ce_pre / rom_nc0
R["recap_roman_median_ef_ucc"] = float(np.median((pb / ce)[nv & (ages >= 1650) & (ages < 2150)]) / (19 / 83))

# Upper bound with McConnell 2018's actual figure (1.1 kt/a average at the 1st-century apogee; factor 2 uncertainty)
b100n = [b for b in bin_medians(ages[nv], nc0[nv], 100.0, 100.0, 8000.0) if b["age_lo"] >= 5000]
vals = [b["median"] for b in b100n]
fmax, fp95 = max(vals) / rom_nc0, float(np.quantile(vals, 0.95)) / rom_nc0
R["upper_bound"] = {"frac_max": fmax, "frac_p95": fp95,
                    "kt_at_3.3": [fp95 * 3.3, fmax * 3.3], "kt_at_1.1": [fp95 * 1.1, fmax * 1.1],
                    "kt_at_1.1_x2_uncert": [fp95 * 0.55, fp95 * 2.2, fmax * 0.55, fmax * 2.2]}

# Volcanic mask: how many pre-5ka samples, and are masked samples Pb-rich?
ratio0 = pb / ce
for nm, lo, hi in (("pre5", 5000, 9000), ("bronze_5_3", 3000, 5000), ("roman", 1650, 2150), ("medieval", 500, 1000), ("industrial", -100, 250)):
    m = (ages >= lo) & (ages < hi)
    R.setdefault("volc_mask", {})[nm] = {"n": int(m.sum()), "n_masked": int((m & vm).sum()), "frac": round(float((m & vm).sum() / m.sum()), 3),
                                         "ef_masked_median": round(float(np.median(ratio0[m & vm]) / k0), 3) if (m & vm).any() else None,
                                         "ef_kept_median": round(float(np.median(ratio0[m & nv]) / k0), 3)}
# 100-yr bins in the pre-5 ka window that lose >25% of samples to the mask
b_all = bin_medians(ages, ratio0, 100.0, 5000.0, 8000.0)
b_nv = {b["age_lo"]: b for b in bin_medians(ages[nv], ratio0[nv], 100.0, 5000.0, 8000.0)}
R["volc_pre5_bins_gt25pct_masked"] = [(b["age_lo"], b["n"], b_nv.get(b["age_lo"], {"n": 0})["n"]) for b in b_all
                                      if b["age_lo"] >= 5000 and b_nv.get(b["age_lo"], {"n": 0})["n"] < 0.75 * b["n"]]

# Flagged pre-5 ka intervals: excess Pb relative to dust tracers other than Ce (Mn, Sr, nssCa)
extra = {}
with open(D / "recap_8kyr.csv", encoding="utf-8", errors="replace") as f:
    r = csv.reader(f); next(r)
    rows = [row for row in r if len(row) >= 15]
def colv(idx):
    out = []
    for row in rows:
        a, p, c = parse_float(row[2]), parse_float(row[14]), parse_float(row[13])
        if a is None or p is None or c is None or p <= 0 or c <= 0:
            continue
        v = parse_float(row[idx]); out.append(v if v is not None and v > 0 else np.nan)
    return np.array(out)
mn, sr, ca = colv(11), colv(12), colv(10)
pre_nv = nv & (ages >= 5000)
for lo, hi in ((5525, 5675), (6625, 6700), (7175, 7275)):
    m = nv & (ages >= lo) & (ages < hi)
    extra[f"{lo}-{hi}"] = {"n": int(m.sum()), "Pb_rel": float(np.median(pb[m]) / np.median(pb[pre_nv])),
                           "Ce_rel": float(np.median(ce[m]) / np.median(ce[pre_nv])),
                           "Mn_rel": float(np.nanmedian(mn[m]) / np.nanmedian(mn[pre_nv])),
                           "Sr_rel": float(np.nanmedian(sr[m]) / np.nanmedian(sr[pre_nv])),
                           "nssCa_rel": float(np.nanmedian(ca[m]) / np.nanmedian(ca[pre_nv]))}
    # how unusual: fraction of all 150-yr windows in 5-8 ka with Pb_rel at least this high
R["recap_flagged_tracers"] = extra
# distribution of 100-yr median Pb relative to pre5 median, to see whether 1.5x Pb is unusual
bp = [b["median"] / np.median(pb[pre_nv]) for b in bin_medians(ages[nv], pb[nv], 100.0, 5000.0, 8000.0)]
R["recap_pre5_century_pb_rel_sorted"] = sorted(round(x, 2) for x in bp)

# Coverage (samples per millennium) RECAP non-volcanic
def per_ka(a, lo, hi):
    return {f"{k}-{k+1}": int(((a >= k * 1000) & (a < (k + 1) * 1000)).sum()) for k in range(lo, hi)}
R["coverage_recap_nonvolc"] = per_ka(ages[nv], 0, 8)

# ---------------- GISP2: injection ----------------
cols = {"age": 1, "S": 12, "Ce": 20, "Pb": 24}
g = {kk: [] for kk in cols}
with open(D / "gisp2_do10_12.csv", encoding="utf-8", errors="replace") as f:
    rr = csv.reader(f); next(rr)
    for row in rr:
        if len(row) < 26:
            continue
        a = parse_float(row[1])
        if a is None or a <= 0:
            continue
        for kk, idx in cols.items():
            v = parse_float(row[idx]); g[kk].append(v if v is not None and v > 0 else np.nan)
g = {kk: np.array(v, float) for kk, v in g.items()}
gvm = volcanic_mask_sulfur(g["age"], g["S"])
gm = ~gvm & np.isfinite(g["Pb"]) & np.isfinite(g["Ce"])
ga, gpb, gce = g["age"][gm], g["Pb"][gm], g["Ce"][gm]
ginj = []
for X in (1, 2, 5, 10, 20):
    for lo, hi in ((44000, 44100), (44000, 45000), (40400, 47400)):
        p2 = gpb.copy(); mm = (ga >= lo) & (ga < hi); p2[mm] += X * rom_nc0
        rat = p2 / gce; kk = np.median(rat); ef = rat / kk
        b25 = bin_medians(ga, ef, 25.0, 40400.0, 47400.0)
        sust = sum(1 for i in range(len(b25) - 1) if b25[i]["median"] >= 3 and b25[i + 1]["median"] >= 3)
        b100 = bin_medians(ga, ef, 100.0, 40400.0, 47400.0)
        ginj.append({"x_recap_roman": X, "pulse": f"{lo}-{hi}", "sust_pairs_ef3": sust, "max_century_ef": round(max(b['median'] for b in b100), 2)})
R["gisp2_injection"] = ginj
R["gisp2_pb_median_pg_g"] = float(np.median(gpb) * 1000)
R["gisp2_k_base"] = float(np.median(gpb / gce))
R["coverage_gisp2"] = per_ka(ga, 40, 48)

# ---------------- Füramoos: protocol EF (renormalised) ----------------
xl = (D / "furamoos_xrf_929755.tab").read_text(encoding="utf-8").splitlines()
xs = next(i for i, l in enumerate(xl) if l.strip() == "*/") + 2
X_ = []
for l in xl[xs:]:
    p = l.split("\t")
    if len(p) >= 4 and all(parse_float(v) is not None for v in p[:4]):
        X_.append([float(v) for v in p[:4]])
X_ = np.array(X_); X_ = X_[np.argsort(X_[:, 1])]
xa, xpn, xef = X_[:, 1] * 1000, X_[:, 2], X_[:, 3]
pre = xa >= 5000
kmed = float(np.median(xef[pre]))
ren = xef / kmed
R["furamoos"] = {"n_rows_used": int(len(xa)), "n_pre5": int(pre.sum()), "pub_pre5_median": kmed,
                 "renorm_pre5_n_ge3": int((ren[pre] >= 3).sum()),
                 "renorm_pre5_ge3_ages": [round(a) for a in xa[pre & (ren >= 3)]],
                 "pub_pre5_max": float(xef[pre].max()),
                 "roman_pub_max": float(xef[(xa >= 1650) & (xa < 2150)].max()),
                 "roman_n_gt_pre5_max": int((xef[(xa >= 1650) & (xa < 2150)] > xef[pre].max()).sum()),
                 "roman_n": int(((xa >= 1650) & (xa < 2150)).sum()),
                 "coverage": per_ka(xa, 0, 15),
                 "median_spacing_yr_by_ka": {f"{k}-{k+1}": (float(np.median(np.diff(xa[(xa >= k*1000) & (xa < (k+1)*1000)]))) if ((xa >= k*1000) & (xa < (k+1)*1000)).sum() > 1 else None) for k in range(0, 15)}}
# consecutive runs of renormalised EF>=3 before 5 ka
runs, cur = [], []
for i in np.where(pre)[0]:
    if ren[i] >= 3:
        cur.append(i)
    else:
        if len(cur) >= 2: runs.append([round(xa[cur[0]]), round(xa[cur[-1]]), len(cur), round(float(ren[cur].max()), 2)])
        cur = []
if len(cur) >= 2: runs.append([round(xa[cur[0]]), round(xa[cur[-1]]), len(cur), round(float(ren[cur].max()), 2)])
R["furamoos"]["renorm_pre5_runs_ge3"] = runs
# Mann-Whitney eras: pre-5 restricted to the mid-Holocene 5-8 ka vs Bronze 5-3.6 ka
mid = (xa >= 5000) & (xa < 8000)
for nm, lo, hi in (("bronze_5_3.6", 3600, 5000), ("bronze_iron_5_2.15", 2150, 5000), ("roman", 1650, 2150)):
    m = (xa >= lo) & (xa < hi)
    R["furamoos"][f"mwu_{nm}_vs_pre5_all"] = float(mannwhitneyu(xef[m], xef[pre], alternative="greater").pvalue)
    R["furamoos"][f"mwu_{nm}_vs_5_8ka"] = float(mannwhitneyu(xef[m], xef[mid], alternative="greater").pvalue)
    R["furamoos"][f"median_{nm}"] = float(np.median(xef[m]))
R["furamoos"]["median_5_8ka"] = float(np.median(xef[mid]))
R["furamoos"]["median_8_14.3ka"] = float(np.median(xef[xa >= 8000]))

# Chance coincidence: fraction of 5-8 ka lying within +/-300 yr of any Füramoos pre-5 ka sample with renorm EF >= 3
hi_ages = xa[pre & (ren >= 3)]
grid = np.arange(5000, 8000, 1.0)
cov = np.mean([np.any(np.abs(hi_ages - t) <= 300) for t in grid])
R["furamoos"]["frac_5_8ka_within_300yr_of_renorm_ge3_point"] = float(cov)
# RECAP flagged intervals vs nearest Füramoos renorm>=3 point
R["furamoos"]["nearest_renorm_ge3_to_recap_flags"] = {f"{lo}-{hi}": round(float(np.min(np.abs(hi_ages - (lo + hi) / 2)))) for lo, hi in ((5525, 5675), (6625, 6700), (7175, 7275))}

# Isotopes: all rows with depth and 206/207 (not only rows with Pb conc.)
il = (D / "furamoos_icpms_929751.tab").read_text(encoding="utf-8").splitlines()
ist = next(i for i, l in enumerate(il) if l.strip() == "*/") + 2
rows_i = [l.split("\t") for l in il[ist:] if l.strip()]
iso_all = [(float(p[2]), float(p[11]), parse_float(p[15]) if len(p) > 15 else None) for p in rows_i
           if parse_float(p[2]) is not None and parse_float(p[11]) is not None]
idp = np.array([v[0] for v in iso_all]); i206 = np.array([v[1] for v in iso_all]); has_pb = np.array([v[2] is not None for v in iso_all])
xd = X_[:, 0]; od = np.argsort(xd)
iage = np.interp(idp, xd[od], xa[od])
p5 = iage >= 5000
mu, sd = float(np.mean(i206[p5 & has_pb])), float(np.std(i206[p5 & has_pb], ddof=1))
R["furamoos_iso"] = {"n_rows_depth_206": int(len(idp)), "n_with_pb": int(has_pb.sum()),
                     "study_subset_pre_post": [int((p5 & has_pb).sum()), int((~p5 & has_pb).sum())],
                     "study_mwu": float(mannwhitneyu(i206[~p5 & has_pb], i206[p5 & has_pb], alternative="less").pvalue),
                     "study_pre_mean_sd": [mu, sd],
                     "all_rows_pre_post": [int(p5.sum()), int((~p5).sum())],
                     "all_rows_pre_range": [float(i206[p5].min()), float(i206[p5].max())],
                     "points_3.6_5ka": sorted((round(float(a)), round(float(b), 4)) for a, b in zip(iage, i206) if 3600 <= a < 5000),
                     "points_3.6_5ka_below_pre_mean_minus_2sd": int(sum(1 for a, b in zip(iage, i206) if 3600 <= a < 5000 and b < mu - 2 * sd)),
                     "first_age_below_pre_mean_minus_2sd": round(float(max(a for a, b in zip(iage, i206) if b < mu - 2 * sd)))}
# MWU 3.6-5 ka vs pre-5 (study subset)
bz = (iage >= 3600) & (iage < 5000) & has_pb
R["furamoos_iso"]["mwu_3.6_5ka_lt_pre5"] = float(mannwhitneyu(i206[bz], i206[p5 & has_pb], alternative="less").pvalue) if bz.sum() > 1 else None
R["furamoos_iso"]["n_3.6_5ka_with_pb"] = int(bz.sum())

# ---------------- PANGAEA.903892 (Laphroaig, Islay, Scotland) raw Pb ----------------
ll = (D / "kylander_peat_903892.tab").read_text(encoding="utf-8").splitlines()
ls = next(i for i, l in enumerate(ll) if l.strip() == "*/") + 2
P_ = [l.split("\t") for l in ll[ls:] if l.strip()]
pa = np.array([float(p[0]) * 1000 for p in P_])
col = lambda j: np.array([parse_float(p[j]) if parse_float(p[j]) is not None else np.nan for p in P_])
pti, ppb, pcu = col(9), col(11), col(12)
lap = {"site_line": [l for l in ll[:4] if "Citation" in l][0][:200]}
for nm, (lo, hi) in {"pre5": (5000, 9000), "bronze_iron": (2150, 5000), "roman": (1650, 2150), "medieval": (500, 1000), "industrial": (-100, 250)}.items():
    m = (pa >= lo) & (pa < hi)
    lap[nm] = {"n": int(m.sum()), "pb_median_raw": float(np.median(ppb[m])), "pb_values": ppb[m].tolist(),
               "n_pb_le0": int((ppb[m] <= 0).sum()), "pb_over_ti_median_pos_only": float(np.median((ppb[m] / pti[m])[ppb[m] > 0])) if (ppb[m] > 0).any() else None,
               "cu_median": float(np.median(pcu[m]))}
pos_pre = (pa >= 5000) & (ppb > 0)
lap["pre5_pb_ti_baseline_pos_only"] = float(np.median(ppb[pos_pre] / pti[pos_pre]))
lap["roman_ef_pbti"] = lap["roman"]["pb_over_ti_median_pos_only"] / lap["pre5_pb_ti_baseline_pos_only"]
lap["medieval_ef_pbti"] = lap["medieval"]["pb_over_ti_median_pos_only"] / lap["pre5_pb_ti_baseline_pos_only"]
lap["ti_top_samples_age"] = sorted([(round(float(a)), float(t)) for a, t in zip(pa, pti)], key=lambda x: -x[1])[:5]
R["laphroaig"] = lap

# ---------------- EPICA: Roman-age samples & spacing ----------------
lines = (D / "edc_217kyr_pb_ba.txt").read_text(encoding="latin-1").splitlines()
st = next(i for i, l in enumerate(lines) if l.strip().startswith("Depth") and "206Pb/207Pb" in l) + 1
E = np.array([[float(p[1]), float(p[3]), float(p[9]), float(p[11])] for p in (l.split() for l in lines[st:]) if len(p) >= 12])
R["epica"] = {"lt5ka_rows": E[E[:, 0] < 5].tolist(), "k_base": float(np.median(E[E[:, 0] >= 40, 3])),
              "n_11.6_20ka": int(((E[:, 0] >= 11.6) & (E[:, 0] < 20)).sum()),
              "ages_5_40ka": E[(E[:, 0] >= 5) & (E[:, 0] < 40), 0].tolist()}

OUT.write_text(json.dumps(R, indent=1, default=float))
print(json.dumps(R, indent=1, default=float))
