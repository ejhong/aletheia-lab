#!/usr/bin/env python3
"""Independent spot check of lost-metallurgy (#82). Reads data/ as untrusted input; run with python -I.

Usage: python -I spot_check.py <question_dir> <out_dir>
"""
import csv
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.stats import mannwhitneyu

Q = Path(sys.argv[1])
OUT = Path(sys.argv[2])
D = Q / "data"
sys.path.insert(0, str(Q / "analysis"))  # study's own helpers (code we have read), not data
from run_metallurgy import volcanic_mask_sulfur, bin_medians, parse_float  # noqa: E402

UCC = 19.0 / 83.0
R = {}


def per_millennium(ages, lo=0, hi=50000):
    out = {}
    for k in range(int(lo // 1000), int(math.ceil(hi / 1000))):
        n = int(((ages >= k * 1000) & (ages < (k + 1) * 1000)).sum())
        if n:
            out[f"{k}-{k+1}ka"] = n
    return out


# ---------------- RECAP ----------------
ages, pb, ce, s, mn, sr, ca = [], [], [], [], [], [], []
with open(D / "recap_8kyr.csv", encoding="utf-8", errors="replace") as f:
    r = csv.reader(f)
    next(r)
    for row in r:
        if len(row) < 15:
            continue
        a, p, c = parse_float(row[2]), parse_float(row[14]), parse_float(row[13])
        if a is None or p is None or c is None or p <= 0 or c <= 0:
            continue
        ages.append(a); pb.append(p); ce.append(c)
        sv = parse_float(row[9]); s.append(sv if sv and sv > 0 else np.nan)
        for lst, idx in ((mn, 11), (sr, 12), (ca, 10)):
            v = parse_float(row[idx]); lst.append(v if v and v > 0 else np.nan)
ages, pb, ce, s, mn, sr, ca = map(np.array, (ages, pb, ce, s, mn, sr, ca))
vm = volcanic_mask_sulfur(ages, s)
nv = ~vm
ratio = pb / ce
pre = ages >= 5000
k = float(np.median(ratio[nv & pre]))
ef = ratio / k
nc = np.maximum(0, pb - k * ce)
rec = {"k_base": k, "k_base_over_ucc": k / UCC,
       "pre5ka_median_ef_emp_by_construction": float(np.median(ef[nv & pre])),
       "pre5ka_median_ef_ucc": float(np.median(ratio[nv & pre] / UCC)),
       "ce_median_pg_g_pre5ka": float(np.median(ce[pre]) * 1000), "ce_median_pg_g_all": float(np.median(ce) * 1000),
       "n_all": int(len(ages)), "n_per_millennium_all": per_millennium(ages, 0, 8000),
       "n_per_millennium_nonvolc": per_millennium(ages[nv], 0, 8000)}
# sample spacing
srt = np.sort(ages)
rec["median_spacing_yr_by_millennium"] = {
    f"{m}-{m+1}ka": float(np.median(np.diff(srt[(srt >= m * 1000) & (srt < (m + 1) * 1000)]))) for m in range(0, 8)}
# volcanic mask fraction by era
eras = {"pre5": (5000, 9000), "bronze_iron": (2150, 5000), "roman": (1650, 2150), "medieval": (500, 1000), "industrial": (-100, 250)}
rec["volc_masked_frac_by_era"] = {e: float(vm[(ages >= lo) & (ages < hi)].mean()) for e, (lo, hi) in eras.items()}
rec["volc_masked_frac_total"] = float(vm.mean())
# Does S correlate with Pb excess in Roman era (smelting emits SO2 from sulfide ores)?
rm = (ages >= 1650) & (ages < 2150)
rec["roman_ef_median_all_samples_unmasked"] = float(np.median(ef[rm]))
rec["roman_ef_median_masked_out_samples"] = float(np.median(ef[rm & vm]))
rec["roman_ef_median_kept_samples"] = float(np.median(ef[rm & nv]))
# century bins for whole record (masked)
b100 = bin_medians(ages[nv], ef[nv], 100.0, 100.0, 8000.0)
b100nc = bin_medians(ages[nv], nc[nv] * 1000, 100.0, 100.0, 8000.0)
pre_ef = [b["median"] for b in b100 if b["age_lo"] >= 5000]
pre_nc = [b["median"] for b in b100nc if b["age_lo"] >= 5000]
roman_nc = float(np.median(nc[rm & nv]) * 1000)
rec["roman_ncpb_median_pg_g"] = roman_nc
rec["pre5_century_ncpb_max"] = max(pre_nc)
rec["pre5_century_ncpb_p95"] = float(np.quantile(pre_nc, 0.95))
rec["pre5_century_frac_roman_max"] = max(pre_nc) / roman_nc
rec["pre5_century_frac_roman_p95"] = float(np.quantile(pre_nc, 0.95)) / roman_nc
rec["pre5_centuries_ge_50pct_roman"] = [(b["age_lo"], b["age_hi"], round(b["median"], 3)) for b in b100nc if b["age_lo"] >= 5000 and b["median"] >= 0.5 * roman_nc]
rec["pre5_century_ef_max"] = max(pre_ef)
rec["pre5_century_ef_p95"] = float(np.quantile(pre_ef, 0.95))
# Bronze Age sensitivity: which later centuries exceed the pre-5ka century max?
later = []
for be, bn in zip(b100, b100nc):
    if be["age_lo"] < 5000:
        later.append({"bin": f"{int(be['age_lo'])}-{int(be['age_hi'])}", "ef": round(be["median"], 3), "ncpb_pg_g": round(bn["median"], 3),
                      "ef_gt_pre_max": be["median"] > max(pre_ef), "nc_gt_pre_max": bn["median"] > max(pre_nc)})
rec["post5_centuries"] = later
for lab, lo, hi in (("5-4ka", 4000, 5000), ("4-3ka", 3000, 4000), ("3-2.15ka", 2100, 3000), ("roman", 1600, 2100)):
    sel = [c for c in later if lo <= int(c["bin"].split("-")[0]) < hi]
    rec[f"centuries_{lab}"] = {"n": len(sel), "n_ef_gt_pre5_max": sum(c["ef_gt_pre_max"] for c in sel),
                               "n_nc_gt_pre5_max": sum(c["nc_gt_pre_max"] for c in sel),
                               "median_ef": float(np.median([c["ef"] for c in sel])) if sel else None,
                               "median_nc": float(np.median([c["ncpb_pg_g"] for c in sel])) if sel else None}
# Bronze Age 5-3 ka vs pre-5 ka: sample-level and century-level
ba = nv & (ages >= 3000) & (ages < 5000)
rec["bronze_5_3ka_ef_median"] = float(np.median(ef[ba]))
rec["bronze_5_3ka_ncpb_median_pg_g"] = float(np.median(nc[ba]) * 1000)
rec["mwu_samples_bronze_5_3_vs_pre"] = float(mannwhitneyu(ef[ba], ef[nv & pre], alternative="greater").pvalue)
ba_c = [b["median"] for b in b100 if 3000 <= b["age_lo"] < 5000]
rec["mwu_centuries_bronze_5_3_vs_pre"] = float(mannwhitneyu(ba_c, pre_ef, alternative="greater").pvalue)
# Roman: sample-level vs century-level vs 25-yr bins
rom_c = [b["median"] for b in b100 if 1650 <= b["age_lo"] < 2150]
rec["roman_centuries_ef"] = [round(x, 3) for x in rom_c]
rec["mwu_samples_roman_vs_pre"] = float(mannwhitneyu(ef[rm & nv], ef[nv & pre], alternative="greater").pvalue)
rec["mwu_centuries_roman_vs_pre"] = float(mannwhitneyu(rom_c, pre_ef, alternative="greater").pvalue)
b25 = bin_medians(ages[nv], ef[nv], 25.0, 100.0, 8000.0)
r25 = [b["median"] for b in b25 if 1650 <= b["age_lo"] < 2150]
p25 = [b["median"] for b in b25 if b["age_lo"] >= 5000]
rec["mwu_25yr_roman_vs_pre"] = float(mannwhitneyu(r25, p25, alternative="greater").pvalue)
rec["n_25yr_bins_roman_pre"] = [len(r25), len(p25)]
# lag-1 autocorrelation of log EF in pre-5ka nonvolc samples
x = np.log(ef[nv & pre][np.argsort(ages[nv & pre])])
rec["lag1_autocorr_logEF_pre5"] = float(np.corrcoef(x[:-1], x[1:])[0, 1])
xr = np.log(ef[rm & nv][np.argsort(ages[rm & nv])])
rec["lag1_autocorr_logEF_roman"] = float(np.corrcoef(xr[:-1], xr[1:])[0, 1])
# Flagged pre-5ka intervals: is dust (Ce) different? other dust ratios
flag_iv = [(5525, 5575), (5625, 5675), (6625, 6700), (7175, 7275)]
fl = {}
pre_nv = nv & pre
for lo, hi in flag_iv:
    m = nv & (ages >= lo) & (ages < hi)
    fl[f"{lo}-{hi}"] = {"n": int(m.sum()), "ce_med_pg_g": float(np.median(ce[m]) * 1000), "pb_med_pg_g": float(np.median(pb[m]) * 1000),
                         "pb_ce": float(np.median(ratio[m])), "pb_mn_rel": float(np.nanmedian(pb[m] / mn[m]) / np.nanmedian(pb[pre_nv] / mn[pre_nv])),
                         "pb_sr_rel": float(np.nanmedian(pb[m] / sr[m]) / np.nanmedian(pb[pre_nv] / sr[pre_nv]))}
fl["pre5_all"] = {"ce_med_pg_g": float(np.median(ce[pre_nv]) * 1000), "pb_med_pg_g": float(np.median(pb[pre_nv]) * 1000), "pb_ce": k}
rec["flagged_intervals"] = fl
# Max Pb/Ce in pre-5 century bins
rb = bin_medians(ages[nv], ratio[nv], 100.0, 5000.0, 8000.0)
rec["pre5_century_pbce_max"] = max(b["median"] for b in rb)
# Detection floor: smallest constant century excess that would exceed every pre-5ka century (approx: need nc median > pre max)
rec["detect_floor_frac_roman"] = max(pre_nc) / roman_nc
# Coverage note
rec["age_range"] = [float(ages.min()), float(ages.max())]
R["recap"] = rec

# ---------------- GISP2 ----------------
cols = {"age": 1, "S": 12, "Ce": 20, "Pb": 24, "Cd": 17, "Bi": 25, "Tl": 23}
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
m = ~gvm & np.isfinite(g["Pb"]) & np.isfinite(g["Ce"])
gk = float(np.median(g["Pb"][m] / g["Ce"][m]))
gis = {"k_base_pb_ce": gk, "k_over_ucc": gk / UCC, "baseline_window": "median of entire 47.4-40.4 ka test window itself",
       "ce_median_pg_g": float(np.nanmedian(g["Ce"][m]) * 1000), "pb_median_pg_g": float(np.nanmedian(g["Pb"][m]) * 1000),
       "n_per_millennium": per_millennium(g["age"][m], 40000, 48000)}
# What EF would a RECAP-Roman-size excess (2.15 pg/g) produce on top of GISP2 median crustal Pb?
gis["ef_if_add_recap_roman_ncpb"] = float((np.nanmedian(g["Pb"][m]) * 1000 + roman_nc) / (np.nanmedian(g["Pb"][m]) * 1000))
# Century-bin maxima of ncPb
gnc = np.maximum(0, g["Pb"][m] - gk * g["Ce"][m]) * 1000
gb = bin_medians(g["age"][m], gnc, 100.0, 40400.0, 47400.0)
gis["century_ncpb_max_pg_g"] = max(b["median"] for b in gb)
gis["century_ncpb_max_frac_recap_roman"] = max(b["median"] for b in gb) / roman_nc
gis["stadial_interstadial_ce_range_century_pg_g"] = [min(b["median"] for b in bin_medians(g["age"][m], g["Ce"][m] * 1000, 100.0, 40400.0, 47400.0)),
                                                      max(b["median"] for b in bin_medians(g["age"][m], g["Ce"][m] * 1000, 100.0, 40400.0, 47400.0))]
R["gisp2"] = gis

# ---------------- EPICA Dome C ----------------
lines = (D / "edc_217kyr_pb_ba.txt").read_text(encoding="latin-1").splitlines()
st = next(i for i, l in enumerate(lines) if l.strip().startswith("Depth") and "206Pb/207Pb" in l) + 1
e = []
for l in lines[st:]:
    ps = l.split()
    if len(ps) >= 12:
        e.append([float(ps[1]) * 1000, float(ps[3]), float(ps[9]), float(ps[10]), float(ps[11])])
e = np.array(e)
ea, e206, epb, eba, epba = e.T
win = (ea >= 5000) & (ea < 40000)
ice_age = (ea >= 11600) & (ea < 20000)
# distinct sampling events: samples within 100 yr grouped
def events(a):
    a = np.sort(a); ev = []
    for x in a:
        if ev and x - ev[-1][-1] < 100:
            ev[-1].append(x)
        else:
            ev.append([x])
    return ev
ev_win = events(ea[win]); ev_ia = events(ea[ice_age])
R["epica"] = {"n_40_5ka": int(win.sum()), "events_40_5ka": len(ev_win), "event_ages_ka": [round(np.mean(v) / 1000, 2) for v in ev_win],
              "max_gap_between_events_yr": float(np.max(np.diff([np.mean(v) for v in ev_win]))),
              "n_20_11.6ka": int(ice_age.sum()), "events_20_11.6ka": len(ev_ia),
              "pb_ba_distinct_values_40_5ka": sorted(set(np.round(epba[win], 3).tolist())),
              "k_base": float(np.median(epba[ea >= 40000])),
              "youngest_sample_bp": float(ea.min()),
              "n_samples_younger_than_5ka": int((ea < 5000).sum()),
              "pb_conc_distinct_values_holocene": sorted(set(epb[(ea < 11600)].tolist()))}

# ---------------- Füramoos ----------------
xl = (D / "furamoos_xrf_929755.tab").read_text(encoding="utf-8").splitlines()
xs = next(i for i, l in enumerate(xl) if l.strip() == "*/") + 2
X = np.array([[float(v) for v in l.split("\t")[:4]] for l in xl[xs:] if l.strip() and len(l.split("\t")) >= 4 and all(l.split("\t")[j] for j in range(4))])
xd, xa, xpn, xef = X[:, 0], X[:, 1] * 1000, X[:, 2], X[:, 3]
o = np.argsort(xa); xa, xef, xpn, xd = xa[o], xef[o], xpn[o], xd[o]
pre_x = xa >= 5000
med_pre = float(np.median(xef[pre_x]))
ren = xef / med_pre
def runs(a, v, thr, sel):
    idx = np.where(sel)[0]; out = []; cur = []
    for i in idx:
        if v[i] >= thr:
            cur.append(i)
        else:
            if len(cur) >= 2: out.append((float(a[cur[0]]), float(a[cur[-1]]), len(cur), float(v[cur].max())))
            cur = []
    if len(cur) >= 2: out.append((float(a[cur[0]]), float(a[cur[-1]]), len(cur), float(v[cur].max())))
    return out
fu = {"n_xrf": int(len(xa)), "age_range": [float(xa.min()), float(xa.max())],
      "n_per_millennium": per_millennium(xa, 0, 15000),
      "median_spacing_yr_pre5": float(np.median(np.diff(xa[pre_x]))),
      "pub_ef_pre5_median": med_pre,
      "pub_ef_pre5_n_ge_2": int((xef[pre_x] >= 2).sum()), "pub_ef_pre5_n_ge_1_5": int((xef[pre_x] >= 1.5).sum()),
      "renorm_ef_pre5_n_ge_3": int((ren[pre_x] >= 3).sum()),
      "renorm_ef_pre5_runs_ge3_consecutive": runs(xa, ren, 3.0, pre_x),
      "renorm_ef_pre5_max": float(ren[pre_x].max()),
      "renorm_era_medians": {}, "pub_era_medians": {}}
for nm, (lo, hi) in {"bronze_iron": (2150, 5000), "bronze_5_3ka": (3000, 5000), "roman": (1650, 2150), "medieval": (500, 1000)}.items():
    mm = (xa >= lo) & (xa < hi)
    fu["renorm_era_medians"][nm] = float(np.median(ren[mm])); fu["pub_era_medians"][nm] = float(np.median(xef[mm]))
    fu.setdefault("era_n", {})[nm] = int(mm.sum())
# Bronze-age points vs pre-5ka max
bz = (xa >= 3000) & (xa < 5000)
fu["bronze_5_3ka_n_points_gt_pre5_max_pub"] = int((xef[bz] > xef[pre_x].max()).sum())
fu["bronze_5_3ka_n_points"] = int(bz.sum())
fu["bronze_5_3ka_runs_pub_ge3"] = runs(xa, xef, 3.0, bz)
fu["bronze_iron_runs_pub_ge3"] = runs(xa, xef, 3.0, (xa >= 2150) & (xa < 5000))
fu["roman_runs_pub_ge3"] = runs(xa, xef, 3.0, (xa >= 1650) & (xa < 2150))
fu["medieval_runs_pub_ge3"] = runs(xa, xef, 3.0, (xa >= 500) & (xa < 1000))
fu["pub_ef_by_millennium_median"] = {f"{q}-{q+1}ka": round(float(np.median(xef[(xa >= q * 1000) & (xa < (q + 1) * 1000)])), 3) for q in range(0, 15) if ((xa >= q * 1000) & (xa < (q + 1) * 1000)).any()}
# isotopes
il = (D / "furamoos_icpms_929751.tab").read_text(encoding="utf-8").splitlines()
ist = next(i for i, l in enumerate(il) if l.strip() == "*/") + 2
rows = [l.split("\t") for l in il[ist:] if l.strip()]
fu["icpms_rows_total"] = len(rows)
fu["icpms_rows_with_depth"] = sum(1 for p in rows if parse_float(p[2]) is not None)
fu["icpms_rows_with_206_207"] = sum(1 for p in rows if parse_float(p[2]) is not None and parse_float(p[11]) is not None)
fu["icpms_rows_with_206_207_and_pb"] = sum(1 for p in rows if parse_float(p[2]) is not None and parse_float(p[11]) is not None and len(p) > 15 and parse_float(p[15]) is not None)
iso = [(float(p[2]), float(p[11])) for p in rows if parse_float(p[2]) is not None and parse_float(p[11]) is not None]
idp = np.array([v[0] for v in iso]); i206 = np.array([v[1] for v in iso])
od = np.argsort(xd)
iage = np.interp(idp, xd[od], xa[od])
p_all = mannwhitneyu(i206[iage < 5000], i206[iage >= 5000], alternative="less").pvalue
fu["iso_all_rows_n_pre_post"] = [int((iage >= 5000).sum()), int((iage < 5000).sum())]
fu["iso_all_rows_mwu_p"] = float(p_all)
fu["iso_points_age_206"] = sorted([(round(float(a)), round(float(b), 4)) for a, b in zip(iage, i206)])
bz_i = (iage >= 3000) & (iage < 5000)
fu["iso_5_3ka"] = [(round(float(a)), round(float(b), 4)) for a, b in zip(iage[bz_i], i206[bz_i])]
fu["iso_pre5_mean_sd"] = [float(np.mean(i206[iage >= 5000])), float(np.std(i206[iage >= 5000], ddof=1))]
R["furamoos"] = fu

# ---------------- PANGAEA.903892 (labelled "Store Mosse") ----------------
ll = (D / "kylander_peat_903892.tab").read_text(encoding="utf-8").splitlines()
hdr_site = [l for l in ll[:5] if "Citation" in l][0]
ls = next(i for i, l in enumerate(ll) if l.strip() == "*/") + 2
P = [l.split("\t") for l in ll[ls:] if l.strip()]
pa = np.array([float(p[0]) * 1000 for p in P])
def col(j):
    return np.array([parse_float(p[j]) if parse_float(p[j]) is not None else np.nan for p in P])
pti, ppb, pcu, pzn = col(9), col(11), col(12), col(13)
pre_p = pa >= 5000
sm = {"citation_line": hdr_site[:250], "n": int(len(pa)), "age_range": [float(pa.min()), float(pa.max())], "n_pre5": int(pre_p.sum()),
      "pb_pre5_values": ppb[pre_p].tolist(), "cu_pre5_values": pcu[pre_p].tolist(), "zn_pre5_values": pzn[pre_p].tolist(),
      "ti_example_values": pti[:5].tolist(), "pb_distinct_values_all": sorted(set(ppb[np.isfinite(ppb)].tolist())),
      "n_pre5_pb_zero": int((ppb[pre_p] == 0).sum()), "n_pre5_pb_positive": int((ppb[pre_p] > 0).sum())}
for nm, (lo, hi) in {"bronze_iron": (2150, 5000), "roman": (1650, 2150), "medieval": (500, 1000), "industrial": (-100, 250)}.items():
    mm = (pa >= lo) & (pa < hi)
    sm.setdefault("era", {})[nm] = {"n": int(mm.sum()), "pb_values": ppb[mm].tolist()}
R["laphroaig_903892"] = sm

# ---------------- Dome du Goûter ----------------
def noaa(fn):
    rows = []
    for l in (D / fn).read_text(encoding="utf-8", errors="replace").splitlines():
        if l.startswith("#") or not l.strip() or l.startswith("depth"):
            continue
        rows.append(l.split("\t") if "\t" in l else l.split())
    return rows
ch = noaa("ddg_alps_chem.txt"); ld = noaa("ddg_alps_lead.txt"); ag = noaa("ddg_alps_age.txt")
ldd = np.array([0.5 * (float(r[0]) + float(r[1])) for r in ld])
ce_int = [(float(r[0]), float(r[1]), float(r[8])) for r in ch if parse_float(r[8]) is not None]
covering = sorted({(a, b, c) for a, b, c in ce_int if b > ldd.min() - 1 and a < ldd.max() + 1})
R["ddg"] = {"lead_depth_range_m": [float(ldd.min()), float(ldd.max())], "n_lead": int(len(ldd)),
            "ce_intervals_overlapping_lead_section": covering,
            "lead_file_label": "NOAA 'ID3_1 Lead Roman Antiquity Data'",
            "study_citation_in_file": "Legrand et al. 2025, PNAS Nexus, doi:10.1093/pnasnexus/pgaf186; dataset doi:10.25921/j1yp-qg62"}

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "spot_check.json").write_text(json.dumps(R, indent=1, default=float))
print(json.dumps(R, indent=1, default=float)[:200000])
