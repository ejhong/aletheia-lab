#!/usr/bin/env python3
"""Pre-registered multi-archive heavy-metal side-channel audit (#82: lost-metallurgy).

Implements Tests 0-4 from questions/lost-metallurgy/protocol.md exactly as locked.
"""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import numpy as np
from scipy.stats import mannwhitneyu

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RESULTS_DIR = BASE_DIR / "results"
UCC_PB_CE = 19.0 / 83.0  # Rudnick & Gao (2003) / McConnell et al. (2018) PNAS


def parse_float(s: str) -> float | None:
    s = (s or "").strip()
    if not s or s.lower() in ("na", "nan", "n/a", "null", "-999", "-9999"):
        return None
    try:
        v = float(s)
        return v if math.isfinite(v) else None
    except ValueError:
        return None


def volcanic_mask_sulfur(ages: np.ndarray, sulfur: np.ndarray, half_win_yr: float = 250.0, k_mad: float = 5.0, buffer_yr: float = 2.0) -> np.ndarray:
    """Flag volcanic spikes where S > local_median + k_mad * local_MAD (±buffer_yr)."""
    n = len(ages)
    order = np.argsort(ages)
    a_s = ages[order]
    s_s = sulfur[order]
    raw_spike = np.zeros(n, dtype=bool)
    # Sliding window via searchsorted
    lefts = np.searchsorted(a_s, a_s - half_win_yr, side="left")
    rights = np.searchsorted(a_s, a_s + half_win_yr, side="right")
    for i in range(n):
        if not math.isfinite(s_s[i]) or s_s[i] <= 0:
            continue
        seg = s_s[lefts[i] : rights[i]]
        seg = seg[np.isfinite(seg) & (seg > 0)]
        if len(seg) < 10:
            continue
        med = np.median(seg)
        mad = np.median(np.abs(seg - med))
        if mad < 1e-9:
            mad = np.std(seg) * 0.6745
        if s_s[i] > med + k_mad * mad:
            raw_spike[i] = True
    # Expand by ±buffer_yr
    masked_s = raw_spike.copy()
    spike_ages = a_s[raw_spike]
    if len(spike_ages) > 0:
        for sa in spike_ages:
            lo = np.searchsorted(a_s, sa - buffer_yr, side="left")
            hi = np.searchsorted(a_s, sa + buffer_yr, side="right")
            masked_s[lo:hi] = True
    out = np.zeros(n, dtype=bool)
    out[order] = masked_s
    return out


def bin_medians(ages: np.ndarray, vals: np.ndarray, bin_yr: float, min_age: float, max_age: float) -> list[dict]:
    edges = np.arange(math.floor(min_age / bin_yr) * bin_yr, math.ceil(max_age / bin_yr) * bin_yr + bin_yr, bin_yr)
    bins = []
    for i in range(len(edges) - 1):
        lo, hi = float(edges[i]), float(edges[i + 1])
        m = (ages >= lo) & (ages < hi) & np.isfinite(vals)
        if np.any(m):
            v = vals[m]
            bins.append({
                "age_lo": lo,
                "age_hi": hi,
                "age_mid": 0.5 * (lo + hi),
                "n": int(len(v)),
                "median": float(np.median(v)),
                "p90": float(np.quantile(v, 0.90)),
                "max": float(np.max(v)),
            })
    return bins


def era_summary(ages: np.ndarray, ef: np.ndarray, ncpb: np.ndarray | None = None) -> dict:
    eras = {
        "pre_bronze_gt5ka": (5000.0, 50000.0),
        "bronze_iron_5_2.15ka": (2150.0, 5000.0),
        "roman_2.15_1.65ka": (1650.0, 2150.0),
        "medieval_1.0_0.5ka": (500.0, 1000.0),
        "industrial_lt0.25ka": (-100.0, 250.0),
    }
    out = {}
    pre_m = (ages >= 5000.0) & (ages <= 50000.0) & np.isfinite(ef)
    pre_ef = ef[pre_m]
    for name, (lo, hi) in eras.items():
        m = (ages >= lo) & (ages < hi) & np.isfinite(ef)
        v = ef[m]
        if len(v) == 0:
            out[name] = {"n": 0}
            continue
        rec = {
            "n": int(len(v)),
            "ef_median": float(np.median(v)),
            "ef_p90": float(np.quantile(v, 0.90)),
            "ef_p95": float(np.quantile(v, 0.95)),
            "ef_max": float(np.max(v)),
            "frac_ef_ge_2": float(np.mean(v >= 2.0)),
            "frac_ef_ge_3": float(np.mean(v >= 3.0)),
        }
        if len(pre_ef) >= 3 and name != "pre_bronze_gt5ka":
            stat, pval = mannwhitneyu(v, pre_ef, alternative="greater")
            rec["mwu_p_gt_pre5ka"] = float(pval)
        if ncpb is not None:
            nc = ncpb[m]
            nc = nc[np.isfinite(nc)]
            if len(nc):
                rec["ncpb_median"] = float(np.median(nc))
                rec["ncpb_p90"] = float(np.quantile(nc, 0.90))
                rec["ncpb_p95"] = float(np.quantile(nc, 0.95))
                rec["ncpb_max"] = float(np.max(nc))
        out[name] = rec
    return out


def analyze_recap() -> dict:
    ages, pb, ce, sulf = [], [], [], []
    with open(DATA_DIR / "recap_8kyr.csv", encoding="utf-8", errors="replace") as f:
        r = csv.reader(f)
        hdr = next(r)
        for row in r:
            if len(row) < 15:
                continue
            a = parse_float(row[2])  # continuous v.1/3-2018 yb1950
            p = parse_float(row[14])  # Pb ng/g
            c = parse_float(row[13])  # Ce ng/g
            s = parse_float(row[9])   # S ng/g
            if a is not None and p is not None and c is not None and p > 0 and c > 0:
                ages.append(a)
                pb.append(p)
                ce.append(c)
                sulf.append(s if (s is not None and s > 0) else np.nan)
    ages = np.array(ages)
    pb = np.array(pb)
    ce = np.array(ce)
    sulf = np.array(sulf)

    vmask = volcanic_mask_sulfur(ages, sulf)
    nv = ~vmask
    ratio = pb / ce
    pre_nv = nv & (ages >= 5000.0)
    k_base = float(np.median(ratio[pre_nv]))
    ef_emp = ratio / k_base
    ef_ucc = ratio / UCC_PB_CE
    ncpb_emp = np.maximum(0.0, pb - k_base * ce)
    ncpb_ucc = np.maximum(0.0, pb - UCC_PB_CE * ce)

    # 100-yr and 25-yr bins (volcanic-masked)
    b100_ef = bin_medians(ages[nv], ef_emp[nv], 100.0, 100.0, 8000.0)
    b100_nc = bin_medians(ages[nv], ncpb_emp[nv], 100.0, 100.0, 8000.0)
    b25_ef = bin_medians(ages[nv], ef_emp[nv], 25.0, 100.0, 8000.0)
    b25_nc = bin_medians(ages[nv], ncpb_emp[nv], 25.0, 100.0, 8000.0)

    # Check sustained pre-5ka anomalies
    pre_b100_ef = [b for b in b100_ef if b["age_lo"] >= 5000.0]
    pre_b100_nc = [b for b in b100_nc if b["age_lo"] >= 5000.0]
    pre_b25_ef = [b for b in b25_ef if b["age_lo"] >= 5000.0]
    pre_b25_nc = [b for b in b25_nc if b["age_lo"] >= 5000.0]

    # Roman positive control (2150-1650 BP)
    rom_nv = nv & (ages >= 1650.0) & (ages < 2150.0)
    roman_ncpb_med = float(np.median(ncpb_emp[rom_nv]))
    roman_ncpb_ucc_med = float(np.median(ncpb_ucc[rom_nv]))
    roman_ef_med = float(np.median(ef_emp[rom_nv]))
    roman_ef_ucc_med = float(np.median(ef_ucc[rom_nv]))

    # Consecutive 25-yr bins (>=50 yr) with EF >= 3.0 or ncPb >= 50% Roman
    sustained_ef3 = []
    for i in range(len(pre_b25_ef) - 1):
        if pre_b25_ef[i]["median"] >= 3.0 and pre_b25_ef[i + 1]["median"] >= 3.0:
            sustained_ef3.append((pre_b25_ef[i]["age_lo"], pre_b25_ef[i + 1]["age_hi"]))
    sustained_50rom = []
    for i in range(len(pre_b25_nc) - 1):
        if pre_b25_nc[i]["median"] >= 0.5 * roman_ncpb_med and pre_b25_nc[i + 1]["median"] >= 0.5 * roman_ncpb_med:
            sustained_50rom.append((pre_b25_nc[i]["age_lo"], pre_b25_nc[i + 1]["age_hi"], pre_b25_nc[i]["median"]))

    max_100yr_pre_nc = max(b["median"] for b in pre_b100_nc)
    p95_100yr_pre_nc = float(np.quantile([b["median"] for b in pre_b100_nc], 0.95))
    max_100yr_pre_ef = max(b["median"] for b in pre_b100_ef)

    return {
        "n_valid": int(len(ages)),
        "age_min_bp": float(ages.min()),
        "age_max_bp": float(ages.max()),
        "volcanic_frac_masked": float(vmask.mean()),
        "k_base_pb_ce_emp": k_base,
        "k_ucc_pb_ce": UCC_PB_CE,
        "eras_volc_masked_emp": era_summary(ages[nv], ef_emp[nv], ncpb_emp[nv]),
        "eras_volc_masked_ucc": era_summary(ages[nv], ef_ucc[nv], ncpb_ucc[nv]),
        "eras_unmasked_emp": era_summary(ages, ef_emp, ncpb_emp),
        "pre5ka_100yr_bins": {
            "n_bins": len(pre_b100_ef),
            "max_ef_emp": max_100yr_pre_ef,
            "p95_ef_emp": float(np.quantile([b["median"] for b in pre_b100_ef], 0.95)),
            "max_ncpb_pg_g": max_100yr_pre_nc * 1000.0,
            "p95_ncpb_pg_g": p95_100yr_pre_nc * 1000.0,
            "n_bins_ef_ge_2": sum(1 for b in pre_b100_ef if b["median"] >= 2.0),
            "n_bins_ef_ge_3": sum(1 for b in pre_b100_ef if b["median"] >= 3.0),
        },
        "sustained_50yr_pre5ka_ef_ge_3": sustained_ef3,
        "sustained_50yr_pre5ka_ge_50pct_roman": sustained_50rom,
        "roman_control": {
            "ef_emp_median": roman_ef_med,
            "ef_ucc_median": roman_ef_ucc_med,
            "ncpb_emp_median_pg_g": roman_ncpb_med * 1000.0,
            "ncpb_ucc_median_pg_g": roman_ncpb_ucc_med * 1000.0,
        },
        "upper_bound_vs_roman": {
            "max_100yr_frac_roman": max_100yr_pre_nc / roman_ncpb_med if roman_ncpb_med > 0 else None,
            "p95_100yr_frac_roman": p95_100yr_pre_nc / roman_ncpb_med if roman_ncpb_med > 0 else None,
            "max_100yr_pb_air_t_yr_at_3300t_roman": (max_100yr_pre_nc / roman_ncpb_med) * 3300.0 if roman_ncpb_med > 0 else None,
            "p95_100yr_pb_air_t_yr_at_3300t_roman": (p95_100yr_pre_nc / roman_ncpb_med) * 3300.0 if roman_ncpb_med > 0 else None,
        },
        "bins_100yr_ef": b100_ef,
        "bins_100yr_ncpb_pg_g": [{**b, "median": b["median"] * 1000.0, "p90": b["p90"] * 1000.0} for b in b100_nc],
    }


def analyze_gisp2() -> dict:
    cols_idx = {"age": 1, "S": 12, "Al": 15, "Cd": 17, "Ce": 20, "Tl": 23, "Pb": 24, "Bi": 25}
    rows_d = {k: [] for k in cols_idx}
    with open(DATA_DIR / "gisp2_do10_12.csv", encoding="utf-8", errors="replace") as f:
        r = csv.reader(f)
        next(r)
        for row in r:
            if len(row) < 26:
                continue
            a = parse_float(row[cols_idx["age"]])
            if a is None or a <= 0:
                continue
            for k, idx in cols_idx.items():
                v = parse_float(row[idx])
                rows_d[k].append(v if (v is not None and v > 0) else np.nan)
    arr = {k: np.array(v, dtype=float) for k, v in rows_d.items()}
    vmask = volcanic_mask_sulfur(arr["age"], arr["S"])
    nv = ~vmask

    out = {
        "n_rows": int(len(arr["age"])),
        "age_min_bp": float(np.nanmin(arr["age"])),
        "age_max_bp": float(np.nanmax(arr["age"])),
        "volcanic_frac_masked": float(vmask.mean()),
        "elements": {},
    }
    for el in ["Pb", "Cd", "Bi", "Tl"]:
        m = nv & np.isfinite(arr[el]) & np.isfinite(arr["Ce"]) & (arr["Ce"] > 0)
        ratio = arr[el][m] / arr["Ce"][m]
        k_base = float(np.median(ratio))
        ef = ratio / k_base
        b100 = bin_medians(arr["age"][m], ef, 100.0, 40400.0, 47400.0)
        b25 = bin_medians(arr["age"][m], ef, 25.0, 40400.0, 47400.0)
        sust = [
            (b25[i]["age_lo"], b25[i + 1]["age_hi"], b25[i]["median"])
            for i in range(len(b25) - 1)
            if b25[i]["median"] >= 3.0 and b25[i + 1]["median"] >= 3.0
        ]
        el_res = {
            "n_valid_nv": int(m.sum()),
            "k_base_vs_ce": k_base,
            "n_100yr_bins": len(b100),
            "b100_ef_median": float(np.median([b["median"] for b in b100])),
            "b100_ef_p95": float(np.quantile([b["median"] for b in b100], 0.95)),
            "b100_ef_max": float(max(b["median"] for b in b100)),
            "b100_n_ge_3": sum(1 for b in b100 if b["median"] >= 3.0),
            "sustained_50yr_ef_ge_3": sust,
        }
        if el == "Pb":
            ef_ucc = ratio / UCC_PB_CE
            ncpb_emp = np.maximum(0.0, arr["Pb"][m] - k_base * arr["Ce"][m])
            b100_nc = bin_medians(arr["age"][m], ncpb_emp, 100.0, 40400.0, 47400.0)
            el_res["ef_ucc_median"] = float(np.median(ef_ucc))
            el_res["ef_ucc_p95"] = float(np.quantile(ef_ucc, 0.95))
            el_res["b100_ncpb_max_pg_g"] = float(max(b["median"] for b in b100_nc)) * 1000.0
            el_res["b100_ncpb_p95_pg_g"] = float(np.quantile([b["median"] for b in b100_nc], 0.95)) * 1000.0
            el_res["bins_100yr_ef"] = b100
        out["elements"][el] = el_res
    return out


def analyze_ddg_alps() -> dict:
    # 1. Age-depth model
    ad_d, ad_age = [], []
    for line in (DATA_DIR / "ddg_alps_age.txt").read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip() or line.startswith("#") or line.startswith("depth"):
            continue
        ps = line.split()
        if len(ps) >= 2:
            d, yr_ce = parse_float(ps[0]), parse_float(ps[1])
            if d is not None and yr_ce is not None:
                ad_d.append(d)
                ad_age.append(1950.0 - yr_ce)  # yb1950
    ad_d = np.array(ad_d)
    ad_age = np.array(ad_age)

    # 2. Chemistry (Ce, Al, Dust)
    ch_d, ch_ce = [], []
    for line in (DATA_DIR / "ddg_alps_chem.txt").read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip() or line.startswith("#") or line.startswith("depth"):
            continue
        ps = line.split("\t")
        if len(ps) >= 9:
            d0, d1, ce = parse_float(ps[0]), parse_float(ps[1]), parse_float(ps[8])
            if d0 is not None and d1 is not None and ce is not None and ce > 0:
                ch_d.append(0.5 * (d0 + d1))
                ch_ce.append(ce)
    ch_d = np.array(ch_d)
    ch_ce = np.array(ch_ce)

    # 3. Lead
    pb_d, pb_v = [], []
    for line in (DATA_DIR / "ddg_alps_lead.txt").read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip() or line.startswith("#") or line.startswith("depth"):
            continue
        ps = line.split("\t")
        if len(ps) >= 3:
            d0, d1, p = parse_float(ps[0]), parse_float(ps[1]), parse_float(ps[2])
            if d0 is not None and d1 is not None and p is not None and p > 0:
                pb_d.append(0.5 * (d0 + d1))
                pb_v.append(p)
    pb_d = np.array(pb_d)
    pb_v = np.array(pb_v)

    pb_age = np.interp(pb_d, ad_d, ad_age)
    pb_ce = np.interp(pb_d, ch_d, ch_ce)
    # Only keep depths within chemistry & age model coverage
    in_rng = (pb_d >= ad_d.min()) & (pb_d <= ad_d.max()) & (pb_d >= ch_d.min()) & (pb_d <= ch_d.max())
    pb_age, pb_v, pb_ce = pb_age[in_rng], pb_v[in_rng], pb_ce[in_rng]

    ratio = pb_v / pb_ce
    ef_ucc = ratio / UCC_PB_CE
    ncpb_ucc = np.maximum(0.0, pb_v - UCC_PB_CE * pb_ce)
    order = np.argsort(pb_age)
    a_s, ef_s, nc_s = pb_age[order], ef_ucc[order], ncpb_ucc[order]

    return {
        "n_samples": int(len(pb_age)),
        "age_min_bp": float(pb_age.min()),
        "age_max_bp": float(pb_age.max()),
        "note": "Covers 2,549-1,184 BP (599 BCE-766 CE); European Alpine Iron/Roman positive-control benchmark (Amendment 1)",
        "eras_ucc": era_summary(pb_age, ef_ucc, ncpb_ucc),
        "series": [
            {"age_bp": float(a_s[i]), "pb_ng_g": float(pb_v[order[i]]), "ef_ucc": float(ef_s[i]), "ncpb_ucc_ng_g": float(nc_s[i])}
            for i in range(len(a_s))
        ],
    }


def analyze_edc() -> dict:
    ages, pb, ba, pba, iso206 = [], [], [], [], []
    lines = (DATA_DIR / "edc_217kyr_pb_ba.txt").read_text(encoding="utf-8", errors="replace").splitlines()
    start = next(i for i, l in enumerate(lines) if l.strip().startswith("Depth") and "206Pb/207Pb" in l) + 2
    for l in lines[start:]:
        ps = l.split()
        if len(ps) < 12:
            continue
        a = parse_float(ps[1])
        r206 = parse_float(ps[3])
        p = parse_float(ps[9])
        b = parse_float(ps[10])
        rpb = parse_float(ps[11])
        if a is not None and rpb is not None and r206 is not None:
            ages.append(a * 1000.0)
            pb.append(p if p is not None else np.nan)
            ba.append(b if b is not None else np.nan)
            pba.append(rpb)
            iso206.append(r206)
    ages = np.array(ages)
    pba = np.array(pba)
    iso206 = np.array(iso206)

    nat_base = ages >= 40000.0
    test_win = (ages >= 5000.0) & (ages < 40000.0)
    k_base = float(np.median(pba[nat_base]))
    ef = pba / k_base
    iso_mu = float(np.mean(iso206[nat_base]))
    iso_sd = float(np.std(iso206[nat_base], ddof=1))
    iso_z = (iso206 - iso_mu) / iso_sd

    # Check any sample in 40-5 ka with EF >= 3.0 or (EF >= 2.0 and iso_z < -2.0)
    anoms = []
    for i in np.where(test_win)[0]:
        if ef[i] >= 3.0 or (ef[i] >= 2.0 and iso_z[i] < -2.0):
            anoms.append({"age_bp": float(ages[i]), "ef": float(ef[i]), "iso206_207": float(iso206[i]), "iso_z": float(iso_z[i])})

    return {
        "n_total": int(len(ages)),
        "n_nat_baseline_40_217ka": int(nat_base.sum()),
        "n_test_40_5ka": int(test_win.sum()),
        "k_base_pb_ba_40_217ka": k_base,
        "nat_iso206_207_mean": iso_mu,
        "nat_iso206_207_sd": iso_sd,
        "test_40_5ka_ef_median": float(np.median(ef[test_win])),
        "test_40_5ka_ef_max": float(np.max(ef[test_win])),
        "test_40_5ka_iso206_min": float(np.min(iso206[test_win])),
        "test_40_5ka_iso206_max": float(np.max(iso206[test_win])),
        "test_40_5ka_anomalies": anoms,
        "series_0_50ka": [
            {"age_bp": float(ages[i]), "ef": float(ef[i]), "iso206_207": float(iso206[i]), "pb_pg_g": float(pb[i])}
            for i in np.where(ages <= 50000.0)[0]
        ],
    }


def analyze_furamoos() -> dict:
    # XRF file: Depth, Age [ka BP], Pb norm, EF
    x_lines = (DATA_DIR / "furamoos_xrf_929755.tab").read_text(encoding="utf-8", errors="replace").splitlines()
    x_start = next(i for i, l in enumerate(x_lines) if l.strip() == "*/") + 2
    xd, xa, xpb, xef = [], [], [], []
    for l in x_lines[x_start:]:
        ps = l.split("\t")
        if len(ps) >= 4:
            d, a, pn, ef = parse_float(ps[0]), parse_float(ps[1]), parse_float(ps[2]), parse_float(ps[3])
            if d is not None and a is not None and ef is not None:
                xd.append(d)
                xa.append(a * 1000.0)
                xpb.append(pn if pn is not None else np.nan)
                xef.append(ef)
    xd, xa, xef = np.array(xd), np.array(xa), np.array(xef)
    # Re-normalize EF to empirical pre-5ka median as sensitivity too, while reporting published EF directly
    pre_x = xa >= 5000.0
    pub_pre_med = float(np.median(xef[pre_x]))
    xef_renorm = xef / pub_pre_med

    # Check consecutive pre-5ka XRF samples with EF >= 3.0 (both published and renormalized)
    order = np.argsort(xa)
    xa_s, xef_s, xef_rn_s = xa[order], xef[order], xef_renorm[order]
    pre_idx = np.where(xa_s >= 5000.0)[0]
    sust_pub = []
    for k in range(len(pre_idx) - 1):
        i, j = pre_idx[k], pre_idx[k + 1]
        if xef_s[i] >= 3.0 and xef_s[j] >= 3.0:
            sust_pub.append((float(xa_s[i]), float(xa_s[j]), float(xef_s[i]), float(xef_s[j])))

    # ICP-MS file with 206Pb/207Pb isotopes
    i_lines = (DATA_DIR / "furamoos_icpms_929751.tab").read_text(encoding="utf-8", errors="replace").splitlines()
    i_start = next(i for i, l in enumerate(i_lines) if l.strip() == "*/") + 2
    id_d, id_206, id_pb = [], [], []
    for l in i_lines[i_start:]:
        ps = l.split("\t")
        if len(ps) >= 16:
            d, r206, pb = parse_float(ps[2]), parse_float(ps[11]), parse_float(ps[15])
            if d is not None and r206 is not None and pb is not None:
                id_d.append(d)
                id_206.append(r206)
                id_pb.append(pb)
    id_d = np.array(id_d)
    id_206 = np.array(id_206)
    id_pb = np.array(id_pb)
    # Map ICP-MS depth to XRF age & EF
    xd_ord = np.argsort(xd)
    id_age = np.interp(id_d, xd[xd_ord], xa[xd_ord])
    id_ef = np.interp(id_d, xd[xd_ord], xef[xd_ord])

    pre_i = id_age >= 5000.0
    post_i = id_age < 5000.0
    iso_pre_mu = float(np.mean(id_206[pre_i]))
    iso_pre_sd = float(np.std(id_206[pre_i], ddof=1))
    iso_post_min = float(np.min(id_206[post_i]))
    iso_post_med = float(np.median(id_206[post_i]))
    stat_iso, p_iso = mannwhitneyu(id_206[post_i], id_206[pre_i], alternative="less")

    # Coupled pre-5ka isotope drop + EF >= 2.0
    coupled = []
    for i in np.where(pre_i)[0]:
        if id_206[i] < iso_pre_mu - 2.0 * iso_pre_sd and id_ef[i] >= 2.0:
            coupled.append({"age_bp": float(id_age[i]), "iso206_207": float(id_206[i]), "ef": float(id_ef[i])})

    return {
        "n_xrf": int(len(xa)),
        "age_min_bp": float(xa.min()),
        "age_max_bp": float(xa.max()),
        "pub_ef_pre5ka_median": pub_pre_med,
        "eras_published_ef": era_summary(xa, xef),
        "eras_renorm_ef": era_summary(xa, xef_renorm),
        "sustained_consec_pre5ka_pub_ef_ge_3": sust_pub,
        "icpms_isotopes": {
            "n_total": int(len(id_age)),
            "n_pre5ka": int(pre_i.sum()),
            "n_post5ka": int(post_i.sum()),
            "pre5ka_206_207_mean": iso_pre_mu,
            "pre5ka_206_207_sd": iso_pre_sd,
            "pre5ka_206_207_min": float(np.min(id_206[pre_i])),
            "post5ka_206_207_median": iso_post_med,
            "post5ka_206_207_min": iso_post_min,
            "mwu_p_post_less_than_pre": float(p_iso),
            "coupled_pre5ka_anomalies": coupled,
            "points": [
                {"age_bp": float(id_age[i]), "iso206_207": float(id_206[i]), "pb_ug_kg": float(id_pb[i]), "ef": float(id_ef[i])}
                for i in np.argsort(id_age)
            ],
        },
        "xrf_series_downsampled": [
            {"age_bp": float(xa_s[i]), "ef": float(xef_s[i])}
            for i in range(0, len(xa_s), 2)
        ],
    }


def analyze_store_mosse() -> dict:
    lines = (DATA_DIR / "kylander_peat_903892.tab").read_text(encoding="utf-8", errors="replace").splitlines()
    start = next(i for i, l in enumerate(lines) if l.strip() == "*/") + 2
    ages, ti, pb, cu, zn = [], [], [], [], []
    for l in lines[start:]:
        ps = l.split("\t")
        if len(ps) >= 14:
            a = parse_float(ps[0])
            t = parse_float(ps[9])   # Ti [%]
            p = parse_float(ps[11])  # Pb [mg/kg]
            c = parse_float(ps[12])  # Cu [mg/kg]
            z = parse_float(ps[13])  # Zn [mg/kg]
            if a is not None and t is not None and t > 0:
                ages.append(a * 1000.0)
                ti.append(t)
                pb.append(p if p is not None else np.nan)
                cu.append(c if c is not None else np.nan)
                zn.append(z if z is not None else np.nan)
    ages = np.array(ages)
    ti = np.array(ti)
    out = {"n_samples": int(len(ages)), "age_min_bp": float(ages.min()), "age_max_bp": float(ages.max()), "elements": {}}
    for name, arr in [("Pb", np.array(pb)), ("Cu", np.array(cu)), ("Zn", np.array(zn))]:
        m = np.isfinite(arr) & (arr > 0)
        a_m = ages[m]
        ratio = arr[m] / ti[m]
        pre = a_m >= 5000.0
        k_base = float(np.median(ratio[pre]))
        ef = ratio / k_base
        order = np.argsort(a_m)
        a_s, ef_s = a_m[order], ef[order]
        pre_idx = np.where(a_s >= 5000.0)[0]
        sust = [
            (float(a_s[pre_idx[k]]), float(a_s[pre_idx[k + 1]]), float(ef_s[pre_idx[k]]), float(ef_s[pre_idx[k + 1]]))
            for k in range(len(pre_idx) - 1)
            if ef_s[pre_idx[k]] >= 3.0 and ef_s[pre_idx[k + 1]] >= 3.0
        ]
        out["elements"][name] = {
            "n_valid": int(m.sum()),
            "n_pre5ka": int(pre.sum()),
            "k_base_vs_ti": k_base,
            "eras": era_summary(a_m, ef),
            "sustained_consec_pre5ka_ef_ge_3": sust,
            "series": [{"age_bp": float(a_s[i]), "ef": float(ef_s[i])} for i in range(len(a_s))],
        }
    return out


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    recap = analyze_recap()
    gisp2 = analyze_gisp2()
    ddg = analyze_ddg_alps()
    edc = analyze_edc()
    fur = analyze_furamoos()
    sm = analyze_store_mosse()

    summary = {
        "recap_greenland_8kyr": recap,
        "gisp2_greenland_40_47ka": gisp2,
        "ddg_alps_10kyr": ddg,
        "edc_antarctica_217kyr": edc,
        "furamoos_germany_14kyr": fur,
        "store_mosse_sweden_6kyr": sm,
    }
    out_path = RESULTS_DIR / "metallurgy_summary.json"
    out_path.write_text(json.dumps(summary, indent=2))
    print("=== SAVED", out_path, "===\n")

    print("--- 1. RECAP GREENLAND (7.98 - 0.12 ka) ---")
    print("Volcanic masked frac:", round(recap["volcanic_frac_masked"], 4), "k_base Pb/Ce:", round(recap["k_base_pb_ce_emp"], 4), "vs UCC:", round(UCC_PB_CE, 4))
    for k, v in recap["eras_volc_masked_emp"].items():
        if v["n"]:
            print(f"  {k:22s}: n={v['n']:5d} EF_med={v['ef_median']:.2f} EF_p95={v['ef_p95']:.2f} ncPb_med={v.get('ncpb_median',0)*1000:.2f} pg/g p={v.get('mwu_p_gt_pre5ka')}")
    print("  Pre-5ka 100yr bins:", recap["pre5ka_100yr_bins"])
    print("  Sustained >=50yr EF>=3:", recap["sustained_50yr_pre5ka_ef_ge_3"])
    print("  Sustained >=50yr >=50% Roman:", recap["sustained_50yr_pre5ka_ge_50pct_roman"])
    print("  Upper bound vs Roman:", recap["upper_bound_vs_roman"])

    print("\n--- 2. GISP2 GREENLAND ICE AGE (47.4 - 40.4 ka) ---")
    print("Rows:", gisp2["n_rows"], "Volc masked:", round(gisp2["volcanic_frac_masked"], 4))
    for el, v in gisp2["elements"].items():
        print(f"  {el:3s}: n={v['n_valid_nv']} 100yr_max_EF={v['b100_ef_max']:.2f} p95_EF={v['b100_ef_p95']:.2f} n>=3:{v['b100_n_ge_3']} sust50yr:{v['sustained_50yr_ef_ge_3']}")

    print("\n--- 3. DOME DU GOUTER FRENCH ALPS (2.55 - 1.18 ka, Positive Control) ---")
    for k, v in ddg["eras_ucc"].items():
        if v["n"]:
            print(f"  {k:22s}: n={v['n']:4d} EF_ucc_med={v['ef_median']:.2f} EF_ucc_p95={v['ef_p95']:.2f} ncPb_med={v.get('ncpb_median',0):.4f} ng/g")

    print("\n--- 4. EPICA DOME C ANTARCTICA (217 - 2 ka) ---")
    print({k: v for k, v in edc.items() if k != "series_0_50ka"})

    print("\n--- 5. FURAMOOS GERMANY PEAT (14.3 - 0.2 ka) ---")
    for k, v in fur["eras_published_ef"].items():
        if v["n"]:
            print(f"  {k:22s}: n={v['n']:4d} EF_med={v['ef_median']:.2f} EF_p95={v['ef_p95']:.2f} EF_max={v['ef_max']:.2f} p={v.get('mwu_p_gt_pre5ka')}")
    print("  Sustained consec pre-5ka pub EF>=3:", fur["sustained_consec_pre5ka_pub_ef_ge_3"][:10], f"(total={len(fur['sustained_consec_pre5ka_pub_ef_ge_3'])})")
    print("  ICP-MS Pb isotopes:", {k: v for k, v in fur["icpms_isotopes"].items() if k != "points"})

    print("\n--- 6. STORE MOSSE SWEDEN PEAT (6.4 - 0.1 ka, Pb/Cu/Zn) ---")
    for el, v in sm["elements"].items():
        print(f"  {el}: pre5ka_med={v['eras']['pre_bronze_gt5ka']['ef_median']:.2f} max={v['eras']['pre_bronze_gt5ka']['ef_max']:.2f} | "
              f"roman_med={v['eras']['roman_2.15_1.65ka'].get('ef_median')} | mediev_med={v['eras']['medieval_1.0_0.5ka'].get('ef_median')} | sust_pre5ka={v['sustained_consec_pre5ka_ef_ge_3']}")


if __name__ == "__main__":
    main()
