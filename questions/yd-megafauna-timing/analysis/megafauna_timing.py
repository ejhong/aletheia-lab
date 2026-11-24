#!/usr/bin/env python3
"""
Locked analysis for Issue #116 (yd-megafauna-timing):
Did North American megafauna collapse before the Younger Dryas?

Implements both pre-registered pillars in full fidelity to protocol.md:
  Pillar 1 — Lake-sediment Sporormiella dung-fungus spores (11 Neotoma cores)
  Pillar 2 — Direct megafauna radiocarbon dates (Broughton & Weitzel 2018)
             recalibrated on IntCal20 with forward Monte Carlo H_impact plateau
             testing and per-taxon Signor-Lipps extinction estimators (OLE, GRIWM).

All raw data live in ../data/ (git-ignored; documented in ../MANIFEST.md).
Outputs are written to ../results/.
"""
from __future__ import annotations

import json
import math
import re
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

import numpy as np
from scipy import stats
from scipy.special import gammaln

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RESULTS_DIR = BASE_DIR / "results"

T_YD = 12896.0    # Greenland GICC05 Younger Dryas onset (Rasmussen et al. 2014)
T_YDB = 12835.0   # Claimed YDB impact layer age (Kennett et al. 2015)
T_IMPACT = 12850.0  # Midpoint benchmark used in H_impact forward simulation
SEED = 20261123

# 11 qualifying Neotoma pollen datasets (selected pre-lock from metadata/counts only)
QUALIFYING_NEOTOMA = [
    (14957, "Appleman Lake", "IN"),
    (17717, "Silver Lake", "OH"),
    (19937, "Spicer Lake", "IN"),
    (45695, "Triangle Lake Bog", "OH"),
    (61900, "Mono Lake", "CA"),
    (16175, "Binnewater Pond", "NY"),
    (16179, "Otisville", "NY"),
    (46645, "Lower Paintrock Lake", "WY"),
    (47259, "Hall's Cave", "TX"),
    (3056, "Como Lake", "CO"),
    (15876, "Tulare Lake", "CA"),
]

CARNIVORES = {
    "Smilodon",
    "Canis dirus",
    "Arctodus",
    "Panthera leo atrox",
    "Homotherium",
}


# ---------------------------------------------------------------------------
# IntCal20 Calibration Curve & Radiocarbon Utilities
# ---------------------------------------------------------------------------

def load_intcal20(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Load 3-column IntCal20 file (calBP, 14C_BP, sigma), sorted ascending by calBP."""
    arr = np.loadtxt(path)
    if arr.ndim != 2 or arr.shape[1] < 3:
        raise ValueError(f"Unexpected IntCal20 shape: {arr.shape}")
    order = np.argsort(arr[:, 0])
    cal_bp = arr[order, 0].astype(float)
    c14_bp = arr[order, 1].astype(float)
    sigma = arr[order, 2].astype(float)
    return cal_bp, c14_bp, sigma


def interpolate_intcal20(
    cal_bp: np.ndarray,
    c14_bp: np.ndarray,
    sigma: np.ndarray,
    t_grid: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Linearly interpolate IntCal20 mean and 1-sigma onto calendar grid t_grid."""
    mu = np.interp(t_grid, cal_bp, c14_bp)
    sig = np.interp(t_grid, cal_bp, sigma)
    return mu, sig


def calibrate_dates_matrix(
    rc_ages: np.ndarray,
    rc_errs: np.ndarray,
    mu_grid: np.ndarray,
    sig_grid: np.ndarray,
) -> np.ndarray:
    """
    Calibrate an array of (rc_age, rc_err) dates onto a calendar grid.
    Returns an (N, G) array of normalized posterior probability vectors summing to 1 per row.
    """
    rc = np.asarray(rc_ages, dtype=float)[:, None]
    se = np.asarray(rc_errs, dtype=float)[:, None]
    var = se ** 2 + sig_grid[None, :] ** 2
    logp = -0.5 * ((rc - mu_grid[None, :]) ** 2) / var
    logp -= np.max(logp, axis=1, keepdims=True)
    p = np.exp(logp)
    row_sums = np.sum(p, axis=1, keepdims=True)
    row_sums = np.where(row_sums > 0, row_sums, 1.0)
    return p / row_sums


def surovell_taphonomy(t_bp: np.ndarray) -> np.ndarray:
    """Surovell et al. (2009) volcanic/terrestrial taphonomic preservation curve f_taph(t)."""
    t = np.asarray(t_bp, dtype=float)
    return 5.726442e6 * np.power(t + 2176.4, -1.3925309)


def posterior_quantiles(t_grid: np.ndarray, p: np.ndarray) -> tuple[float, float, float]:
    """Return (q2.5_younger, median, q97.5_older) from a normalized posterior on ascending t_grid."""
    cdf = np.cumsum(p)
    cdf /= cdf[-1]
    q025 = float(np.interp(0.025, cdf, t_grid))
    q500 = float(np.interp(0.500, cdf, t_grid))
    q975 = float(np.interp(0.975, cdf, t_grid))
    return q025, q500, q975


# ---------------------------------------------------------------------------
# Pillar 1: Neotoma Sporormiella Dung-Fungus Analysis
# ---------------------------------------------------------------------------

def parse_neotoma_core(path: Path) -> dict:
    """Parse a downloaded Neotoma v2 JSON and extract Sporormiella % upland pollen in 17-10 ka."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    rec = raw["data"][0]
    site = rec["site"]
    cu = site["collectionunit"]
    default_chron = cu.get("defaultchronology")
    ds = cu["dataset"]
    samples = ds["samples"]

    # Extract coordinates from GeoJSON string if present
    lon, lat = None, None
    geo = site.get("geography")
    if isinstance(geo, str):
        try:
            g = json.loads(geo)
            coords = g.get("coordinates")
            if g.get("type") == "Point" and isinstance(coords, list) and len(coords) >= 2:
                lon, lat = float(coords[0]), float(coords[1])
            elif g.get("type") == "Polygon" and coords:
                ring = coords[0]
                lon = float(np.mean([pt[0] for pt in ring]))
                lat = float(np.mean([pt[1] for pt in ring]))
        except Exception:
            pass

    age_buckets: dict[float, list[tuple[float, float]]] = {}
    chron_name = None
    for s in samples:
        ages = s.get("ages") or []
        chosen = None
        for a in ages:
            if a.get("chronologyid") == default_chron and a.get("agetype") == "Calibrated radiocarbon years BP":
                chosen = a
                break
        if chosen is None:
            for a in ages:
                if a.get("agetype") == "Calibrated radiocarbon years BP":
                    chosen = a
                    break
        if chosen is None or chosen.get("age") is None:
            continue
        age = float(chosen["age"])
        if chron_name is None:
            chron_name = chosen.get("chronologyname") or f"chron_{chosen.get('chronologyid')}"
        if not (10000.0 <= age <= 17000.0):
            continue

        n_upland = 0.0
        n_spo = 0.0
        for d in s.get("datum") or []:
            val = d.get("value")
            if val is None:
                continue
            units = d.get("units")
            eg = d.get("ecologicalgroup")
            vname = d.get("variablename")
            etype = d.get("elementtype")
            if units == "NISP" and eg in ("TRSH", "UPHE"):
                n_upland += float(val)
            if vname == "Sporormiella" and units == "NISP" and etype == "spore":
                n_spo += float(val)
        if n_upland <= 0:
            continue
        age_buckets.setdefault(age, []).append((n_spo, n_upland))

    # Deduplicate identical ages by averaging percentages, sort oldest to youngest
    ages_sorted = sorted(age_buckets.keys(), reverse=True)
    t_arr = []
    s_arr = []
    n_spo_arr = []
    n_up_arr = []
    for age in ages_sorted:
        pairs = age_buckets[age]
        pcts = [100.0 * sp / up for sp, up in pairs]
        t_arr.append(age)
        s_arr.append(float(np.mean(pcts)))
        n_spo_arr.append(float(np.sum([sp for sp, _ in pairs])))
        n_up_arr.append(float(np.sum([up for _, up in pairs])))

    return {
        "site_name": site.get("sitename", ""),
        "lat": lat,
        "lon": lon,
        "chronology": chron_name,
        "ages": np.array(t_arr, dtype=float),
        "pct": np.array(s_arr, dtype=float),
        "n_spo": np.array(n_spo_arr, dtype=float),
        "n_upland": np.array(n_up_arr, dtype=float),
    }


def rolling_median_3(y: np.ndarray) -> np.ndarray:
    """3-point rolling median with edge replication."""
    n = len(y)
    if n < 3:
        return y.copy()
    padded = np.concatenate(([y[0]], y, [y[-1]]))
    out = np.empty(n, dtype=float)
    for i in range(n):
        out[i] = float(np.median(padded[i : i + 3]))
    return out


def compute_sporormiella_metrics(ages: np.ndarray, pct: np.ndarray) -> dict:
    """
    Compute the three pre-registered decline-age estimators on a single core
    (ages sorted descending: oldest to youngest, inside 17,000-10,000 cal BP).
    """
    t = np.asarray(ages, dtype=float)
    s = np.asarray(pct, dtype=float)
    n = len(t)
    if n < 4:
        raise ValueError("Core has fewer than 4 samples")
    if not np.all(np.diff(t) < 0):
        order = np.argsort(t)[::-1]
        t = t[order]
        s = s[order]

    # 1. t_2pct & t_onset
    mask_pre_115 = t >= 11500.0
    max_s_pre = float(np.max(s[mask_pre_115])) if np.any(mask_pre_115) else float(np.max(s))
    t_2pct = None
    t_onset = None
    if max_s_pre >= 2.0:
        # Restrict evaluation through 10,500 cal BP (or end of 17-10 ka window if no samples < 10,500)
        idx_win = np.where(t >= 10500.0)[0]
        if len(idx_win) < 2:
            idx_win = np.arange(n)
        t_w = t[idx_win]
        s_w = s[idx_win]
        above = np.where(s_w >= 2.0)[0]
        if len(above) > 0:
            k_star = int(above[-1])
            if k_star < len(s_w) - 1:
                # Linearly interpolate between (t_w[k_star], s_w[k_star]) and (t_w[k_star+1], s_w[k_star+1])
                s0, s1 = s_w[k_star], s_w[k_star + 1]
                t0, t1 = t_w[k_star], t_w[k_star + 1]
                if s0 == s1:
                    t_2pct = float(0.5 * (t0 + t1))
                else:
                    frac = (s0 - 2.0) / (s0 - s1)
                    t_2pct = float(t0 + frac * (t1 - t0))
                # Pre-collapse peak preceding k_star
                peak_idx = int(np.argmax(s_w[: k_star + 1]))
                t_onset = float(t_w[peak_idx])

    # 2. t_50pct (threshold-free half-drop)
    s_sm = rolling_median_3(s) if n >= 15 else s.copy()
    mask_peak = (t <= 17000.0) & (t >= 12500.0)
    if np.any(mask_peak):
        cand_idx = np.where(mask_peak)[0]
        i_peak = int(cand_idx[int(np.argmax(s_sm[cand_idx]))])
    else:
        i_peak = int(np.argmax(s_sm))
    s_max = float(s_sm[i_peak])
    t_peak = float(t[i_peak])
    t_50pct = None
    if s_max > 0:
        half = 0.5 * s_max
        for j in range(i_peak + 1, n):
            if s_sm[j] < half:
                s0, s1 = s_sm[j - 1], s_sm[j]
                t0, t1 = t[j - 1], t[j]
                if s0 == s1:
                    t_50pct = float(0.5 * (t0 + t1))
                else:
                    frac = (s0 - half) / (s0 - s1)
                    t_50pct = float(t0 + frac * (t1 - t0))
                break

    # 3. t_cp (exact 2-regime step-drop changepoint MLE on [16000, 11000])
    sst = float(np.sum((s - np.mean(s)) ** 2))
    best_ssr = math.inf
    t_cp = None
    mean_old = None
    mean_yng = None
    for k in range(1, n - 2):
        # Split between k (inclusive, older) and k+1 (younger): need >=2 on each side
        if (k + 1) < 2 or (n - (k + 1)) < 2:
            continue
        tc = 0.5 * (t[k] + t[k + 1])
        if not (11000.0 <= tc <= 16000.0):
            continue
        m_old = float(np.mean(s[: k + 1]))
        m_yng = float(np.mean(s[k + 1 :]))
        if m_old <= m_yng:
            continue
        ssr = float(np.sum((s[: k + 1] - m_old) ** 2) + np.sum((s[k + 1 :] - m_yng) ** 2))
        if ssr < best_ssr:
            best_ssr = ssr
            t_cp = float(tc)
            mean_old = m_old
            mean_yng = m_yng

    r2_step = (1.0 - best_ssr / sst) if (t_cp is not None and sst > 0) else None

    return {
        "n_samples": int(n),
        "n_nonzero": int(np.sum(s > 0)),
        "age_max": float(t[0]),
        "age_min": float(t[-1]),
        "max_pct_17_115": max_s_pre,
        "mean_pct": float(np.mean(s)),
        "t_onset": t_onset,
        "t_2pct": t_2pct,
        "t_peak_sm": t_peak,
        "s_max_sm": s_max,
        "t_50pct": t_50pct,
        "t_cp": t_cp,
        "mean_old_cp": mean_old,
        "mean_yng_cp": mean_yng,
        "r2_step": r2_step,
    }


def timing_tests_against(values: list[float], ref_age: float) -> dict:
    """Wilcoxon signed-rank (two-sided + greater) and exact binomial sign test of (val - ref_age)."""
    arr = np.array([v for v in values if v is not None], dtype=float)
    n = len(arr)
    if n == 0:
        return {"n": 0}
    diffs = arr - ref_age
    n_before = int(np.sum(diffs > 0))
    n_after = int(np.sum(diffs < 0))
    res = {
        "n": int(n),
        "ref_age": float(ref_age),
        "median": float(np.median(arr)),
        "iqr_lo": float(np.percentile(arr, 25)),
        "iqr_hi": float(np.percentile(arr, 75)),
        "mean": float(np.mean(arr)),
        "median_lead_yr": float(np.median(diffs)),
        "n_before": n_before,
        "n_after": n_after,
        "frac_before": float(n_before / n),
    }
    nonzero = diffs[diffs != 0]
    if len(nonzero) >= 1:
        w2 = stats.wilcoxon(nonzero, alternative="two-sided")
        wg = stats.wilcoxon(nonzero, alternative="greater")
        res["wilcoxon_stat"] = float(w2.statistic)
        res["wilcoxon_p_two_sided"] = float(w2.pvalue)
        res["wilcoxon_p_greater"] = float(wg.pvalue)
    else:
        res["wilcoxon_stat"] = None
        res["wilcoxon_p_two_sided"] = None
        res["wilcoxon_p_greater"] = None
    bt2 = stats.binomtest(n_before, n, p=0.5, alternative="two-sided")
    btg = stats.binomtest(n_before, n, p=0.5, alternative="greater")
    res["binom_p_two_sided"] = float(bt2.pvalue)
    res["binom_p_greater"] = float(btg.pvalue)
    return res


def run_pillar1(rng: np.random.Generator) -> dict:
    """Execute Pillar 1 across all 11 qualifying Neotoma cores."""
    sites_out = []
    grid_bp = np.arange(16400.0, 10200.0, -200.0)  # 16,400 to 10,400 in 200-yr bins
    norm_matrix = []

    for dsid, label, state in QUALIFYING_NEOTOMA:
        path = DATA_DIR / "neotoma" / f"ds_{dsid}.json"
        parsed = parse_neotoma_core(path)
        metrics = compute_sporormiella_metrics(parsed["ages"], parsed["pct"])

        # Normalize by 17-10 ka mean and interpolate onto 200-yr grid within core age range
        t_asc = parsed["ages"][::-1]
        s_asc = parsed["pct"][::-1]
        mean_s = metrics["mean_pct"]
        s_norm = s_asc / mean_s if mean_s > 0 else np.zeros_like(s_asc)
        row = np.full(len(grid_bp), np.nan)
        in_range = (grid_bp >= t_asc[0]) & (grid_bp <= t_asc[-1])
        row[in_range] = np.interp(grid_bp[in_range], t_asc, s_norm)
        norm_matrix.append(row)

        sites_out.append({
            "dataset_id": dsid,
            "site_name": label,
            "neotoma_name": parsed["site_name"],
            "state": state,
            "lat": parsed["lat"],
            "lon": parsed["lon"],
            "chronology": parsed["chronology"],
            **metrics,
            "series": [
                {
                    "age": round(float(a), 1),
                    "pct": round(float(p), 4),
                    "n_spo": round(float(sp), 1),
                    "n_upland": round(float(up), 1),
                }
                for a, p, sp, up in zip(parsed["ages"], parsed["pct"], parsed["n_spo"], parsed["n_upland"])
            ],
        })

    # Continental composite + 5,000 site-bootstrap 95% CIs
    mat = np.vstack(norm_matrix)  # (11, G)
    n_sites_arr = np.sum(~np.isnan(mat), axis=0)
    comp_med = np.nanmedian(mat, axis=0)
    comp_mean = np.nanmean(mat, axis=0)

    n_boot = 5000
    n_cores = mat.shape[0]
    boot_idx = rng.integers(0, n_cores, size=(n_boot, n_cores))
    boot_meds = np.empty((n_boot, len(grid_bp)), dtype=float)
    boot_means = np.empty((n_boot, len(grid_bp)), dtype=float)
    for b in range(n_boot):
        sub = mat[boot_idx[b]]
        boot_meds[b] = np.nanmedian(sub, axis=0)
        boot_means[b] = np.nanmean(sub, axis=0)

    composite = []
    for i, age in enumerate(grid_bp):
        composite.append({
            "age": float(age),
            "n_sites": int(n_sites_arr[i]),
            "median": None if np.isnan(comp_med[i]) else round(float(comp_med[i]), 4),
            "median_ci_lo": None if np.isnan(comp_med[i]) else round(float(np.nanpercentile(boot_meds[:, i], 2.5)), 4),
            "median_ci_hi": None if np.isnan(comp_med[i]) else round(float(np.nanpercentile(boot_meds[:, i], 97.5)), 4),
            "mean": None if np.isnan(comp_mean[i]) else round(float(comp_mean[i]), 4),
            "mean_ci_lo": None if np.isnan(comp_mean[i]) else round(float(np.nanpercentile(boot_means[:, i], 2.5)), 4),
            "mean_ci_hi": None if np.isnan(comp_mean[i]) else round(float(np.nanpercentile(boot_means[:, i], 97.5)), 4),
        })

    # Formal tests against T_YD (12,896) and T_YDB (12,835)
    tests = {}
    for key in ("t_2pct", "t_50pct", "t_cp", "t_onset"):
        vals = [s[key] for s in sites_out if s[key] is not None]
        tests[key] = {
            "vs_12896": timing_tests_against(vals, T_YD),
            "vs_12835": timing_tests_against(vals, T_YDB),
        }

    return {
        "n_cores": len(sites_out),
        "sites": sites_out,
        "composite": composite,
        "tests": tests,
    }


# ---------------------------------------------------------------------------
# Pillar 2: Direct Megafauna 14C Dates on IntCal20
# ---------------------------------------------------------------------------

def _excel_col_idx(ref: str) -> int:
    m = re.match(r"([A-Z]+)", ref)
    idx = 0
    for ch in m.group(1):
        idx = idx * 26 + (ord(ch) - ord("A") + 1)
    return idx - 1


def read_xlsx_sheet1(path: Path) -> list[list[str]]:
    """Minimal stdlib XML/ZIP reader for sheet1.xml that respects sparse cell coordinates."""
    ns = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    t_tag = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t"
    with zipfile.ZipFile(path) as z:
        ss = []
        if "xl/sharedStrings.xml" in z.namelist():
            root = ET.fromstring(z.read("xl/sharedStrings.xml"))
            for si in root.findall("s:si", ns):
                ss.append("".join(el.text or "" for el in si.iter(t_tag)))
        sheet = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
        rows = []
        for row in sheet.findall(".//s:sheetData/s:row", ns):
            vals: dict[int, str] = {}
            for c in row.findall("s:c", ns):
                ci = _excel_col_idx(c.attrib["r"])
                ctype = c.attrib.get("t")
                v = c.find("s:v", ns)
                if v is None:
                    is_el = c.find("s:is", ns)
                    val = "".join(el.text or "" for el in is_el.iter(t_tag)) if is_el is not None else ""
                elif ctype == "s":
                    val = ss[int(v.text)]
                else:
                    val = v.text or ""
                vals[ci] = val
            if vals:
                mx = max(vals) + 1
                rows.append([vals.get(i, "") for i in range(mx)])
        return rows


def parse_broughton2018(path: Path) -> list[dict]:
    """Parse Broughton & Weitzel (2018) Table S1 direct megafauna radiocarbon dates."""
    rows = read_xlsx_sheet1(path)
    out = []
    for r in rows[2:]:
        if len(r) < 12:
            continue
        try:
            rc = float(r[4])
            err = float(r[5])
        except ValueError:
            continue
        if not (6000.0 <= rc <= 35000.0) or err <= 0:
            continue
        taxon = r[0].strip()
        state = r[1].strip()
        site = r[2].strip()
        lab_id = r[3].strip()
        material = r[9].strip()
        method = r[10].strip().upper()
        try:
            score = int(round(float(r[11])))
        except ValueError:
            score = 0
        ref = r[12].strip() if len(r) > 12 else ""
        is_ams = method in ("MS", "AMS")
        is_labrea = "brea" in site.lower()
        is_carnivore = taxon in CARNIVORES
        out.append({
            "taxon": taxon,
            "state": state,
            "site": site,
            "lab_id": lab_id,
            "rcybp": rc,
            "error": err,
            "material": material,
            "method": method,
            "score": score,
            "is_ams": is_ams,
            "is_labrea": is_labrea,
            "is_carnivore": is_carnivore,
            "reference": ref,
        })
    return out


def compute_spd_metrics(t_grid: np.ndarray, spd: np.ndarray) -> dict:
    """Compute R_pre (13.5-12.9 vs 14.7-13.5 ka) and M_yd (mass in 12.7-11.7 ka)."""
    total = float(np.sum(spd))
    if total <= 0:
        return {"r_pre": None, "m_yd": None}
    spd_norm = spd / total
    mask_pre = (t_grid >= 12900.0) & (t_grid <= 13500.0)
    mask_ba = (t_grid > 13500.0) & (t_grid <= 14700.0)
    mask_yd = (t_grid >= 11700.0) & (t_grid <= 12700.0)
    mean_pre = float(np.mean(spd_norm[mask_pre]))
    mean_ba = float(np.mean(spd_norm[mask_ba]))
    r_pre = float(mean_pre / mean_ba) if mean_ba > 0 else None
    m_yd = float(np.sum(spd_norm[mask_yd]))
    return {"r_pre": r_pre, "m_yd": m_yd}


def simulate_h_impact(
    n_obs: int,
    empirical_errs: np.ndarray,
    t_grid: np.ndarray,
    mu_grid: np.ndarray,
    sig_grid: np.ndarray,
    cal_bp_raw: np.ndarray,
    c14_raw: np.ndarray,
    sig_raw: np.ndarray,
    rng: np.random.Generator,
    n_sims: int = 2000,
    pool_size: int = 40000,
    taph_weighted: bool = False,
) -> dict:
    """
    Forward-simulate H_impact (instant extinction at T_IMPACT = 12,850 cal BP) through IntCal20.
    Generates a bank of `pool_size` exact independent forward-simulated calibrated dates on
    [18,000, 12,850] cal BP, then forms `n_sims` catalogs of size `n_obs` (sampled without
    replacement within each catalog) to obtain exact Monte Carlo distributions of SPD(t),
    R_pre, and M_yd under pure calibration-curve smearing.
    """
    # Sample true calendar ages in [12850, 18000]
    if not taph_weighted:
        t_true = rng.uniform(T_IMPACT, 18000.0, size=pool_size)
    else:
        t_dense = np.linspace(T_IMPACT, 18000.0, 5151)
        w = surovell_taphonomy(t_dense)
        w /= np.sum(w)
        t_true = rng.choice(t_dense, size=pool_size, p=w)

    errs = rng.choice(empirical_errs, size=pool_size, replace=True)
    mu_true = np.interp(t_true, cal_bp_raw, c14_raw)
    sig_true = np.interp(t_true, cal_bp_raw, sig_raw)
    r_sim = rng.normal(mu_true, np.sqrt(errs ** 2 + sig_true ** 2))

    # Calibrate pool in batches to keep memory bounded
    g_len = len(t_grid)
    pool_p = np.empty((pool_size, g_len), dtype=np.float32)
    batch = 2000
    for start in range(0, pool_size, batch):
        end = min(start + batch, pool_size)
        pool_p[start:end] = calibrate_dates_matrix(
            r_sim[start:end], errs[start:end], mu_grid, sig_grid
        ).astype(np.float32)

    # Precompute scalar masks and taphonomy weights
    taph_inv = (1.0 / surovell_taphonomy(t_grid)).astype(np.float32)
    mask_pre = (t_grid >= 12900.0) & (t_grid <= 13500.0)
    mask_ba = (t_grid > 13500.0) & (t_grid <= 14700.0)
    mask_yd = (t_grid >= 11700.0) & (t_grid <= 12700.0)

    # Also compute scalar summaries per pool member for fast catalog aggregation
    pool_pre = np.mean(pool_p[:, mask_pre], axis=1)
    pool_ba = np.mean(pool_p[:, mask_ba], axis=1)
    pool_yd = np.sum(pool_p[:, mask_yd], axis=1)

    pool_taph = pool_p * taph_inv[None, :]
    pool_taph /= np.sum(pool_taph, axis=1, keepdims=True)
    pool_taph_pre = np.mean(pool_taph[:, mask_pre], axis=1)
    pool_taph_ba = np.mean(pool_taph[:, mask_ba], axis=1)
    pool_taph_yd = np.sum(pool_taph[:, mask_yd], axis=1)

    # Downsample calendar grid to 25-yr steps for storing SPD envelopes cleanly
    ds_idx = np.arange(0, g_len, 5)
    sim_spds = np.empty((n_sims, len(ds_idx)), dtype=np.float32)
    sim_spds_taph = np.empty((n_sims, len(ds_idx)), dtype=np.float32)
    r_pre_raw = np.empty(n_sims, dtype=float)
    m_yd_raw = np.empty(n_sims, dtype=float)
    r_pre_taph = np.empty(n_sims, dtype=float)
    m_yd_taph = np.empty(n_sims, dtype=float)

    for b in range(n_sims):
        idx = rng.choice(pool_size, size=n_obs, replace=False)
        # Raw SPD (sum of normalized date posteriors / n_obs)
        spd_ds = np.mean(pool_p[idx][:, ds_idx], axis=0)
        sim_spds[b] = spd_ds
        r_pre_raw[b] = float(np.mean(pool_pre[idx]) / np.mean(pool_ba[idx]))
        m_yd_raw[b] = float(np.mean(pool_yd[idx]))

        # Taphonomy-corrected SPD
        spd_full_t = np.mean(pool_p[idx], axis=0) * taph_inv
        spd_full_t /= np.sum(spd_full_t)
        sim_spds_taph[b] = spd_full_t[ds_idx]
        r_pre_taph[b] = float(np.mean(spd_full_t[mask_pre]) / np.mean(spd_full_t[mask_ba]))
        m_yd_taph[b] = float(np.sum(spd_full_t[mask_yd]))

    return {
        "n_sims": n_sims,
        "taph_weighted_truth": taph_weighted,
        "t_grid_25yr": t_grid[ds_idx].tolist(),
        "raw": {
            "r_pre_p025": float(np.percentile(r_pre_raw, 2.5)),
            "r_pre_p500": float(np.percentile(r_pre_raw, 50.0)),
            "r_pre_p975": float(np.percentile(r_pre_raw, 97.5)),
            "m_yd_p025": float(np.percentile(m_yd_raw, 2.5)),
            "m_yd_p500": float(np.percentile(m_yd_raw, 50.0)),
            "m_yd_p950": float(np.percentile(m_yd_raw, 95.0)),
            "m_yd_p975": float(np.percentile(m_yd_raw, 97.5)),
            "m_yd_p990": float(np.percentile(m_yd_raw, 99.0)),
            "m_yd_max": float(np.max(m_yd_raw)),
            "spd_p025": np.percentile(sim_spds, 2.5, axis=0).tolist(),
            "spd_p500": np.percentile(sim_spds, 50.0, axis=0).tolist(),
            "spd_p975": np.percentile(sim_spds, 97.5, axis=0).tolist(),
        },
        "taph_corrected": {
            "r_pre_p025": float(np.percentile(r_pre_taph, 2.5)),
            "r_pre_p500": float(np.percentile(r_pre_taph, 50.0)),
            "r_pre_p975": float(np.percentile(r_pre_taph, 97.5)),
            "m_yd_p025": float(np.percentile(m_yd_taph, 2.5)),
            "m_yd_p500": float(np.percentile(m_yd_taph, 50.0)),
            "m_yd_p950": float(np.percentile(m_yd_taph, 95.0)),
            "m_yd_p975": float(np.percentile(m_yd_taph, 97.5)),
            "m_yd_p990": float(np.percentile(m_yd_taph, 99.0)),
            "m_yd_max": float(np.max(m_yd_taph)),
            "spd_p025": np.percentile(sim_spds_taph, 2.5, axis=0).tolist(),
            "spd_p500": np.percentile(sim_spds_taph, 50.0, axis=0).tolist(),
            "spd_p975": np.percentile(sim_spds_taph, 97.5, axis=0).tolist(),
        },
        "_m_yd_raw_arr": m_yd_raw,
        "_r_pre_raw_arr": r_pre_raw,
        "_m_yd_taph_arr": m_yd_taph,
        "_r_pre_taph_arr": r_pre_taph,
    }


# ---------------------------------------------------------------------------
# Signor-Lipps Extinction Estimators: Solow (2005) OLE & Bradshaw (2012) GRIWM
# ---------------------------------------------------------------------------

def ole_estimate(t_bp: np.ndarray) -> float:
    """
    Solow (2005) / Cooke (1980) Optimal Linear Estimation (OLE) on k youngest BP dates.
    Works in forward time x = -t_bp so extinction is the upper endpoint, then maps back T = -X.
    Uses exact 2-constraint minimum-variance unbiased weights (e^T a = 1, lam^T a = 0).
    """
    t = np.sort(np.asarray(t_bp, dtype=float))
    k = len(t)
    if k < 4:
        return float(t[0])
    x = -t  # x[0] > x[1] > ... > x[k-1] (x[0] is most recent)
    span = x[0] - x[k - 1]
    if span <= 1e-6:
        return float(t[0])
    denom = np.maximum(x[0] - x[1 : k - 1], 1e-6)
    v = float(np.sum(np.log(span / denom)) / (k - 2))
    v = float(np.clip(v, 0.1, 3.0))

    # Second-moment matrix Lambda_ij for i<=j (1-indexed):
    # Gamma(2v + j) * Gamma(v + i) / (Gamma(v + j) * Gamma(i))
    lam_mat = np.empty((k, k), dtype=float)
    for i in range(1, k + 1):
        g_vi = gammaln(v + i) - gammaln(i)
        for j in range(i, k + 1):
            val = math.exp(gammaln(2.0 * v + j) - gammaln(v + j) + g_vi)
            lam_mat[i - 1, j - 1] = val
            lam_mat[j - 1, i - 1] = val

    lam_vec = np.array([math.exp(gammaln(i + v) - gammaln(i)) for i in range(1, k + 1)])
    m_mat = np.column_stack([np.ones(k), lam_vec])
    try:
        linv_m = np.linalg.solve(lam_mat, m_mat)
    except np.linalg.LinAlgError:
        linv_m = np.linalg.pinv(lam_mat) @ m_mat
    try:
        w = np.linalg.solve(m_mat.T @ linv_m, np.array([1.0, 0.0]))
    except np.linalg.LinAlgError:
        return float(t[0])
    a = linv_m @ w
    x_hat = float(a @ x)
    t_hat = -x_hat
    # Guard against extreme numerical blowup when nearly all youngest dates are tied
    if not np.isfinite(t_hat) or t_hat < 0.0 or t_hat > t[0] + 1e-6:
        t_hat = min(float(t[0]), max(0.0, t_hat)) if np.isfinite(t_hat) else float(t[0])
    return float(t_hat)


def griwm_estimate(t_bp: np.ndarray) -> float:
    """
    Bradshaw et al. (2012) Gaussian-Resampled Inverse-Weighted McInerny (GRIWM) estimator
    on k youngest BP dates (t[0] <= t[1] <= ... <= t[k-1]).
    """
    t = np.sort(np.asarray(t_bp, dtype=float))
    k = len(t)
    if k < 3:
        return float(t[0])
    d = np.maximum(t[1:] - t[0], 1.0)
    idx = np.arange(1, k, dtype=float)
    w = 1.0 / d
    t_i = t[0] - d / idx
    return float(max(0.0, np.sum(w * t_i) / np.sum(w)))


def estimate_taxon_extinction(
    posteriors: np.ndarray,
    t_grid: np.ndarray,
    rng: np.random.Generator,
    n_draws: int = 1000,
    k_max: int = 10,
) -> dict:
    """
    Sample `n_draws` calendar realizations from each specimen's IntCal20 posterior,
    take the k = min(k_max, n) youngest ages in each draw, and compute LAD, OLE, and GRIWM.
    """
    n_spec = posteriors.shape[0]
    k = min(k_max, n_spec)
    cdfs = np.cumsum(posteriors, axis=1)
    cdfs /= cdfs[:, -1:]

    # Vectorized inverse-CDF sampling: (n_spec, n_draws)
    u = rng.random((n_spec, n_draws))
    draws = np.empty((n_spec, n_draws), dtype=float)
    for i in range(n_spec):
        idx = np.searchsorted(cdfs[i], u[i])
        idx = np.clip(idx, 0, len(t_grid) - 1)
        # Add small continuous jitter within the 5-yr bin to avoid artificial zero gaps
        draws[i] = t_grid[idx] + rng.uniform(-2.5, 2.5, size=n_draws)

    lads = np.empty(n_draws, dtype=float)
    oles = np.empty(n_draws, dtype=float)
    griwms = np.empty(n_draws, dtype=float)
    for d in range(n_draws):
        youngest = np.sort(draws[:, d])[:k]
        lads[d] = youngest[0]
        oles[d] = ole_estimate(youngest)
        griwms[d] = griwm_estimate(youngest)

    def summ(arr: np.ndarray) -> dict:
        return {
            "median": round(float(np.median(arr)), 1),
            "ci95_lo": round(float(np.percentile(arr, 2.5)), 1),   # younger bound
            "ci95_hi": round(float(np.percentile(arr, 97.5)), 1),  # older bound
            "p_before_12896": round(float(np.mean(arr > T_YD)), 4),
            "p_after_12835": round(float(np.mean(arr < T_YDB)), 4),
            "p_after_12750": round(float(np.mean(arr < 12750.0)), 4),
        }

    return {
        "n_dates": int(n_spec),
        "k_used": int(k),
        "lad": summ(lads),
        "ole": summ(oles),
        "griwm": summ(griwms),
    }


def run_pillar2(rng: np.random.Generator) -> tuple[dict, list[dict], list[dict]]:
    """Execute Pillar 2 on Broughton & Weitzel (2018) recalibrated on IntCal20."""
    cal_bp_raw, c14_raw, sig_raw = load_intcal20(DATA_DIR / "intcal20.14c")
    t_grid_full = np.arange(0.0, 50005.0, 10.0)
    mu_full, sig_full = interpolate_intcal20(cal_bp_raw, c14_raw, sig_raw, t_grid_full)

    t_grid_spd = np.arange(9000.0, 20005.0, 5.0)
    mu_spd, sig_spd = interpolate_intcal20(cal_bp_raw, c14_raw, sig_raw, t_grid_spd)

    t_grid_tax = np.arange(9000.0, 25005.0, 5.0)
    mu_tax, sig_tax = interpolate_intcal20(cal_bp_raw, c14_raw, sig_raw, t_grid_tax)

    records = parse_broughton2018(DATA_DIR / "broughton2018_s1.xlsx")
    rc_all = np.array([r["rcybp"] for r in records], dtype=float)
    err_all = np.array([r["error"] for r in records], dtype=float)

    # Full-range calibration for window-membership filtering & exact per-specimen stats
    p_full = calibrate_dates_matrix(rc_all, err_all, mu_full, sig_full)
    mask_20_9 = (t_grid_full >= 9000.0) & (t_grid_full <= 20000.0)
    mask_25_9 = (t_grid_full >= 9000.0) & (t_grid_full <= 25000.0)
    mask_lt_12750 = t_grid_full < 12750.0
    mask_lt_12835 = t_grid_full < T_YDB
    mask_lt_12896 = t_grid_full < T_YD

    calibrated_rows = []
    for i, r in enumerate(records):
        q025, q500, q975 = posterior_quantiles(t_grid_full, p_full[i])
        p_in_20_9 = float(np.sum(p_full[i, mask_20_9]))
        p_in_25_9 = float(np.sum(p_full[i, mask_25_9]))
        row = {
            **r,
            "cal_ci95_lo": round(q025, 1),
            "cal_median": round(q500, 1),
            "cal_ci95_hi": round(q975, 1),
            "p_in_20_9": round(p_in_20_9, 4),
            "p_in_25_9": round(p_in_25_9, 4),
            "p_lt_12750": round(float(np.sum(p_full[i, mask_lt_12750])), 4),
            "p_lt_12835": round(float(np.sum(p_full[i, mask_lt_12835])), 4),
            "p_lt_12896": round(float(np.sum(p_full[i, mask_lt_12896])), 4),
        }
        calibrated_rows.append(row)

    # Calibrate on 5-yr SPD grid [9000, 20000]
    p_spd_all = calibrate_dates_matrix(rc_all, err_all, mu_spd, sig_spd)
    taph_inv = 1.0 / surovell_taphonomy(t_grid_spd)
    ds_idx = np.arange(0, len(t_grid_spd), 5)  # 25-yr reporting grid

    subsets_def = {
        "all": lambda r: r["p_in_20_9"] >= 0.50,
        "score12_ams": lambda r: r["p_in_20_9"] >= 0.50 and r["score"] >= 12 and r["is_ams"],
        "herbivores_all": lambda r: r["p_in_20_9"] >= 0.50 and not r["is_carnivore"],
        "herbivores_s12": lambda r: r["p_in_20_9"] >= 0.50 and not r["is_carnivore"] and r["score"] >= 12 and r["is_ams"],
        "no_labrea_all": lambda r: r["p_in_20_9"] >= 0.50 and not r["is_labrea"],
        "no_labrea_s12": lambda r: r["p_in_20_9"] >= 0.50 and not r["is_labrea"] and r["score"] >= 12 and r["is_ams"],
    }

    subsets_out = {}
    for name, pred in subsets_def.items():
        idxs = [i for i, r in enumerate(calibrated_rows) if pred(r)]
        n_obs = len(idxs)
        sub_p = p_spd_all[idxs]
        spd_raw = np.mean(sub_p, axis=0)
        spd_raw /= np.sum(spd_raw)
        spd_taph = spd_raw * taph_inv
        spd_taph /= np.sum(spd_taph)

        obs_raw = compute_spd_metrics(t_grid_spd, spd_raw)
        obs_taph = compute_spd_metrics(t_grid_spd, spd_taph)

        errs_sub = err_all[idxs]
        # Primary H_impact: uniform population on [18000, 12850]
        sim_unif = simulate_h_impact(
            n_obs, errs_sub, t_grid_spd, mu_spd, sig_spd,
            cal_bp_raw, c14_raw, sig_raw, rng,
            n_sims=2000, pool_size=40000, taph_weighted=False,
        )
        # Secondary H_impact: taphonomy-weighted truth (constant true pop with Surovell preservation)
        sim_taph_truth = simulate_h_impact(
            n_obs, errs_sub, t_grid_spd, mu_spd, sig_spd,
            cal_bp_raw, c14_raw, sig_raw, rng,
            n_sims=2000, pool_size=40000, taph_weighted=True,
        )

        # Empirical p-values against H_impact
        p_myd_raw = float(np.mean(sim_unif["_m_yd_raw_arr"] >= obs_raw["m_yd"]))
        p_rpre_raw_lo = float(np.mean(sim_unif["_r_pre_raw_arr"] <= obs_raw["r_pre"]))
        p_myd_taph = float(np.mean(sim_taph_truth["_m_yd_taph_arr"] >= obs_taph["m_yd"]))
        p_rpre_taph_lo = float(np.mean(sim_taph_truth["_r_pre_taph_arr"] <= obs_taph["r_pre"]))

        # Strip private arrays before JSON serialization
        for sd in (sim_unif, sim_taph_truth):
            for k in list(sd.keys()):
                if k.startswith("_"):
                    del sd[k]

        # Survivor counts within this subset
        surv_95 = [calibrated_rows[i] for i in idxs if calibrated_rows[i]["p_lt_12750"] > 0.95]
        surv_99 = [calibrated_rows[i] for i in idxs if calibrated_rows[i]["p_lt_12750"] > 0.99]

        subsets_out[name] = {
            "n_dates": n_obs,
            "obs_raw": obs_raw,
            "obs_taph": obs_taph,
            "p_myd_exceeds_unif": round(p_myd_raw, 4),
            "p_rpre_below_unif": round(p_rpre_raw_lo, 4),
            "p_myd_exceeds_taph_truth": round(p_myd_taph, 4),
            "p_rpre_below_taph_truth": round(p_rpre_taph_lo, 4),
            "n_surv_p95": len(surv_95),
            "n_surv_p99": len(surv_99),
            "t_grid_25yr": t_grid_spd[ds_idx].tolist(),
            "obs_spd_raw_25yr": spd_raw[ds_idx].tolist(),
            "obs_spd_taph_25yr": spd_taph[ds_idx].tolist(),
            "h_impact_uniform": sim_unif,
            "h_impact_taph_truth": sim_taph_truth,
        }

    # Detailed list of all post-impact survivors (P(t < 12,750) > 0.95)
    survivors_95 = sorted(
        [r for r in calibrated_rows if r["p_lt_12750"] > 0.95],
        key=lambda x: x["cal_median"],
    )
    survivors_s12_95 = [r for r in survivors_95 if r["score"] >= 12 and r["is_ams"]]
    survivors_s12_99 = [r for r in survivors_s12_95 if r["p_lt_12750"] > 0.99]

    # Per-taxon Signor-Lipps OLE & GRIWM on [9000, 25000]
    p_tax_all = calibrate_dates_matrix(rc_all, err_all, mu_tax, sig_tax)
    taxa_counts: dict[str, list[int]] = {}
    for i, r in enumerate(calibrated_rows):
        if r["p_in_25_9"] >= 0.50:
            taxa_counts.setdefault(r["taxon"], []).append(i)

    qualifying_taxa = sorted(
        [(tx, idxs) for tx, idxs in taxa_counts.items() if len(idxs) >= 12],
        key=lambda x: -len(x[1]),
    )
    taxa_results = []
    for tx, idxs in qualifying_taxa:
        res_all = estimate_taxon_extinction(p_tax_all[idxs], t_grid_tax, rng, n_draws=1000, k_max=10)
        idxs_s12 = [i for i in idxs if calibrated_rows[i]["score"] >= 12 and calibrated_rows[i]["is_ams"]]
        res_s12 = (
            estimate_taxon_extinction(p_tax_all[idxs_s12], t_grid_tax, rng, n_draws=1000, k_max=10)
            if len(idxs_s12) >= 10
            else None
        )
        # Classify OLE 95% CI relative to YD onset (12,896) and post-impact (12,750)
        ole = res_all["ole"]
        if ole["ci95_lo"] > T_YD:
            ole_cat = "strictly_before_yd"
        elif ole["ci95_hi"] < 12750.0:
            ole_cat = "strictly_after_impact"
        else:
            ole_cat = "spans_yd_boundary"

        # Individual calibrated medians for plotting
        spec_medians = sorted([calibrated_rows[i]["cal_median"] for i in idxs])
        n_surv_tx = sum(1 for i in idxs if calibrated_rows[i]["p_lt_12750"] > 0.95)
        n_surv_tx_s12 = sum(1 for i in idxs_s12 if calibrated_rows[i]["p_lt_12750"] > 0.95)

        taxa_results.append({
            "taxon": tx,
            "is_carnivore": tx in CARNIVORES,
            "n_all_25_9": len(idxs),
            "n_s12_25_9": len(idxs_s12),
            "n_surv_p95_all": n_surv_tx,
            "n_surv_p95_s12": n_surv_tx_s12,
            "all": res_all,
            "score12_ams": res_s12,
            "ole_category": ole_cat,
            "specimen_medians_bp": spec_medians,
        })

    # Sort taxa chronologically from oldest OLE median to youngest OLE median
    taxa_results.sort(key=lambda x: -x["all"]["ole"]["median"])

    ole_medians = [x["all"]["ole"]["median"] for x in taxa_results]
    griwm_medians = [x["all"]["griwm"]["median"] for x in taxa_results]
    cross_taxon = {
        "n_taxa": len(taxa_results),
        "ole_oldest_median": max(ole_medians) if ole_medians else None,
        "ole_youngest_median": min(ole_medians) if ole_medians else None,
        "ole_span_yr": round(max(ole_medians) - min(ole_medians), 1) if ole_medians else None,
        "griwm_span_yr": round(max(griwm_medians) - min(griwm_medians), 1) if griwm_medians else None,
        "n_ole_strictly_before_yd": sum(1 for x in taxa_results if x["ole_category"] == "strictly_before_yd"),
        "n_ole_spans_yd": sum(1 for x in taxa_results if x["ole_category"] == "spans_yd_boundary"),
        "n_ole_strictly_after_impact": sum(1 for x in taxa_results if x["ole_category"] == "strictly_after_impact"),
        "n_ole_median_before_12896": sum(1 for m in ole_medians if m > T_YD),
        "n_ole_median_after_12835": sum(1 for m in ole_medians if m < T_YDB),
    }

    # Quick cross-check against Stewart et al. (2021) table row count / overlap
    stewart_path = DATA_DIR / "stewart2021_s1.xlsx"
    stewart_check = {}
    if stewart_path.exists():
        s_rows = read_xlsx_sheet1(stewart_path)
        stewart_check["total_rows"] = len(s_rows) - 1

    pillar2_out = {
        "n_parsed_valid": len(calibrated_rows),
        "n_in_20_9": subsets_out["all"]["n_dates"],
        "n_s12_in_20_9": subsets_out["score12_ams"]["n_dates"],
        "subsets": subsets_out,
        "survivors": {
            "n_all_p95": len(survivors_95),
            "n_all_p99": sum(1 for r in survivors_95 if r["p_lt_12750"] > 0.99),
            "n_s12_p95": len(survivors_s12_95),
            "n_s12_p99": len(survivors_s12_99),
            "taxa_represented_all_p95": sorted({r["taxon"] for r in survivors_95}),
            "taxa_represented_s12_p95": sorted({r["taxon"] for r in survivors_s12_95}),
            "specimens_p95": [
                {
                    "taxon": r["taxon"],
                    "state": r["state"],
                    "site": r["site"],
                    "lab_id": r["lab_id"],
                    "rcybp": r["rcybp"],
                    "error": r["error"],
                    "method": r["method"],
                    "score": r["score"],
                    "cal_median": r["cal_median"],
                    "cal_ci95_lo": r["cal_ci95_lo"],
                    "cal_ci95_hi": r["cal_ci95_hi"],
                    "p_lt_12750": r["p_lt_12750"],
                }
                for r in survivors_95
            ],
        },
        "taxa": taxa_results,
        "cross_taxon": cross_taxon,
        "stewart2021_crosscheck": stewart_check,
    }
    return pillar2_out, calibrated_rows, taxa_results


# ---------------------------------------------------------------------------
# Pre-Registered Verdict Classifier (protocol.md §4)
# ---------------------------------------------------------------------------

def classify_verdict(p1: dict, p2: dict) -> dict:
    """Apply exact pre-registered verdict rules from protocol.md section 4."""
    t_cp = p1["tests"]["t_cp"]["vs_12896"]
    t_2p = p1["tests"]["t_2pct"]["vs_12896"]
    t_50 = p1["tests"]["t_50pct"]["vs_12896"]

    # Pillar 1 checks
    p1_cp_pre = t_cp["median"] > 13200.0
    p1_other_pre = (t_2p.get("median", 0) > 13200.0) or (t_50.get("median", 0) > 13200.0)
    p1_wilc_sig = (t_cp.get("wilcoxon_p_two_sided") or 1.0) < 0.05
    p1_frac_70 = t_cp["frac_before"] >= 0.70
    p1_pre_begin = (t_cp["median"] > 13200.0) or (t_cp["frac_before"] >= 0.60)
    p1_at_yd = (
        abs(t_cp["median"] - T_YD) <= 300.0
        and (
            abs(t_50["median"] - T_YD) <= 300.0
            or (t_2p.get("median") is not None and abs(t_2p["median"] - T_YD) <= 300.0)
        )
    )

    # Pillar 2 checks (evaluated on both all and score12_ams)
    sub_all = p2["subsets"]["all"]
    sub_s12 = p2["subsets"]["score12_ams"]
    n_surv_s12 = p2["survivors"]["n_s12_p95"]
    myd_exceeds_p99_all = sub_all["obs_raw"]["m_yd"] > sub_all["h_impact_uniform"]["raw"]["m_yd_p990"]
    myd_exceeds_p99_s12 = sub_s12["obs_raw"]["m_yd"] > sub_s12["h_impact_uniform"]["raw"]["m_yd_p990"]
    myd_within_p95_s12 = sub_s12["obs_raw"]["m_yd"] <= sub_s12["h_impact_uniform"]["raw"]["m_yd_p975"]
    rpre_below_p025_all = sub_all["obs_raw"]["r_pre"] < sub_all["h_impact_uniform"]["raw"]["r_pre_p025"]

    ct = p2["cross_taxon"]
    taxa_span_gt_1000 = (
        (ct["ole_span_yr"] or 0.0) > 1000.0
        and ct["n_ole_median_before_12896"] >= 1
        and ct["n_ole_median_after_12835"] >= 1
    )

    p2_clear_survivors = (n_surv_s12 >= 5) and (myd_exceeds_p99_s12 or myd_exceeds_p99_all)

    # Check conditions in logical priority
    cond_staggered = (p1_pre_begin and p2_clear_survivors) or taxa_span_gt_1000
    cond_collapsed_before = (
        p1_cp_pre and p1_other_pre and p1_wilc_sig and p1_frac_70
        and (rpre_below_p025_all or n_surv_s12 < 5)
        and not p2_clear_survivors
    )
    cond_abrupt_at_yd = p1_at_yd and myd_within_p95_s12 and (n_surv_s12 < 5)

    if cond_collapsed_before:
        verdict = "collapsed_before_yd"
    elif cond_staggered:
        verdict = "staggered_spanning_yd"
    elif cond_abrupt_at_yd:
        verdict = "abrupt_at_yd_onset"
    else:
        verdict = "inconclusive_or_divergent"

    return {
        "verdict": verdict,
        "checks": {
            "p1_cp_median_gt_13200": p1_cp_pre,
            "p1_2pct_or_50pct_gt_13200": p1_other_pre,
            "p1_cp_wilcoxon_p_lt_005": p1_wilc_sig,
            "p1_cp_frac_before_ge_70": p1_frac_70,
            "p1_pre_yd_decline_begins": p1_pre_begin,
            "p1_at_yd_onset_pm_300": p1_at_yd,
            "p2_n_surv_s12_p95": n_surv_s12,
            "p2_myd_exceeds_p99_all": myd_exceeds_p99_all,
            "p2_myd_exceeds_p99_s12": myd_exceeds_p99_s12,
            "p2_myd_within_p95_s12": myd_within_p95_s12,
            "p2_rpre_below_p025_all": rpre_below_p025_all,
            "p2_clear_post_impact_survival": p2_clear_survivors,
            "p2_taxa_ole_span_gt_1000_across_yd": taxa_span_gt_1000,
        },
    }


# ---------------------------------------------------------------------------
# Writers & Main Entry Point
# ---------------------------------------------------------------------------

def write_outputs(p1: dict, p2: dict, cal_rows: list[dict], taxa_rows: list[dict], verdict: dict) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    summary = {
        "question": "yd-megafauna-timing",
        "issue": 116,
        "t_yd_gicc05": T_YD,
        "t_ydb_kennett": T_YDB,
        "t_impact_sim": T_IMPACT,
        "seed": SEED,
        "verdict": verdict,
        "pillar1_sporormiella": p1,
        "pillar2_radiocarbon": p2,
    }
    (RESULTS_DIR / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    # 1. results/sporormiella_sites.tsv
    lines = [
        "\t".join([
            "dataset_id", "site_name", "state", "lat", "lon", "n_samples", "n_nonzero",
            "age_max", "age_min", "max_pct_17_115", "t_onset", "t_2pct", "t_50pct", "t_cp",
            "r2_step", "lead_cp_vs_12896",
        ])
    ]
    for s in p1["sites"]:
        fmt = lambda v: "" if v is None else f"{v:.1f}"
        lead = "" if s["t_cp"] is None else f"{s['t_cp'] - T_YD:+.1f}"
        r2 = "" if s["r2_step"] is None else f"{s['r2_step']:.3f}"
        lines.append("\t".join([
            str(s["dataset_id"]), s["site_name"], s["state"],
            "" if s["lat"] is None else f"{s['lat']:.3f}",
            "" if s["lon"] is None else f"{s['lon']:.3f}",
            str(s["n_samples"]), str(s["n_nonzero"]),
            f"{s['age_max']:.1f}", f"{s['age_min']:.1f}", f"{s['max_pct_17_115']:.2f}",
            fmt(s["t_onset"]), fmt(s["t_2pct"]), fmt(s["t_50pct"]), fmt(s["t_cp"]),
            r2, lead,
        ]))
    (RESULTS_DIR / "sporormiella_sites.tsv").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # 2. results/megafauna_calibrated.tsv
    clines = [
        "\t".join([
            "taxon", "state", "site", "lab_id", "rcybp", "error", "method", "score",
            "is_carnivore", "is_labrea", "cal_ci95_lo", "cal_median", "cal_ci95_hi",
            "p_lt_12750", "p_lt_12835", "p_lt_12896", "p_in_20_9",
        ])
    ]
    for r in sorted(cal_rows, key=lambda x: x["cal_median"]):
        clines.append("\t".join([
            r["taxon"], r["state"], r["site"], r["lab_id"],
            f"{r['rcybp']:.1f}", f"{r['error']:.1f}", r["method"], str(r["score"]),
            str(int(r["is_carnivore"])), str(int(r["is_labrea"])),
            f"{r['cal_ci95_lo']:.1f}", f"{r['cal_median']:.1f}", f"{r['cal_ci95_hi']:.1f}",
            f"{r['p_lt_12750']:.4f}", f"{r['p_lt_12835']:.4f}", f"{r['p_lt_12896']:.4f}",
            f"{r['p_in_20_9']:.4f}",
        ]))
    (RESULTS_DIR / "megafauna_calibrated.tsv").write_text("\n".join(clines) + "\n", encoding="utf-8")

    # 3. results/taxon_extinctions.tsv
    tlines = [
        "\t".join([
            "taxon", "is_carnivore", "n_all", "n_s12", "n_surv_p95_all", "n_surv_p95_s12",
            "lad_med", "lad_lo", "lad_hi",
            "ole_med", "ole_lo", "ole_hi", "ole_category",
            "griwm_med", "griwm_lo", "griwm_hi",
            "s12_ole_med", "s12_ole_lo", "s12_ole_hi",
        ])
    ]
    for tx in taxa_rows:
        a = tx["all"]
        s12 = tx["score12_ams"]
        tlines.append("\t".join([
            tx["taxon"], str(int(tx["is_carnivore"])), str(tx["n_all_25_9"]), str(tx["n_s12_25_9"]),
            str(tx["n_surv_p95_all"]), str(tx["n_surv_p95_s12"]),
            f"{a['lad']['median']:.1f}", f"{a['lad']['ci95_lo']:.1f}", f"{a['lad']['ci95_hi']:.1f}",
            f"{a['ole']['median']:.1f}", f"{a['ole']['ci95_lo']:.1f}", f"{a['ole']['ci95_hi']:.1f}",
            tx["ole_category"],
            f"{a['griwm']['median']:.1f}", f"{a['griwm']['ci95_lo']:.1f}", f"{a['griwm']['ci95_hi']:.1f}",
            "" if s12 is None else f"{s12['ole']['median']:.1f}",
            "" if s12 is None else f"{s12['ole']['ci95_lo']:.1f}",
            "" if s12 is None else f"{s12['ole']['ci95_hi']:.1f}",
        ]))
    (RESULTS_DIR / "taxon_extinctions.tsv").write_text("\n".join(tlines) + "\n", encoding="utf-8")


def main() -> None:
    rng = np.random.default_rng(SEED)
    print("Running Pillar 1: Neotoma Sporormiella analysis (11 qualifying cores)...")
    p1 = run_pillar1(rng)
    print("Running Pillar 2: Direct megafauna 14C IntCal20 + H_impact + OLE/GRIWM...")
    p2, cal_rows, taxa_rows = run_pillar2(rng)
    verdict = classify_verdict(p1, p2)
    write_outputs(p1, p2, cal_rows, taxa_rows, verdict)

    print(f"\n=== VERDICT: {verdict['verdict']} ===")
    for k in ("t_cp", "t_2pct", "t_50pct"):
        t = p1["tests"][k]["vs_12896"]
        print(
            f"  Pillar 1 {k:7s}: n={t['n']}, median={t['median']:.0f} cal BP "
            f"(lead {t['median_lead_yr']:+.0f} yr vs 12,896), before={t['n_before']}/{t['n']}, "
            f"Wilcoxon p={t['wilcoxon_p_two_sided']:.4g}"
        )
    s_all = p2["subsets"]["all"]
    s_12 = p2["subsets"]["score12_ams"]
    print(
        f"  Pillar 2 all (n={s_all['n_dates']}): R_pre={s_all['obs_raw']['r_pre']:.3f} "
        f"(H_impact 95%: {s_all['h_impact_uniform']['raw']['r_pre_p025']:.3f}–{s_all['h_impact_uniform']['raw']['r_pre_p975']:.3f}), "
        f"M_yd={s_all['obs_raw']['m_yd']:.4f} (H_impact 99%: {s_all['h_impact_uniform']['raw']['m_yd_p990']:.4f}, p={s_all['p_myd_exceeds_unif']:.4f})"
    )
    print(
        f"  Pillar 2 S12 (n={s_12['n_dates']}): R_pre={s_12['obs_raw']['r_pre']:.3f} "
        f"(H_impact 95%: {s_12['h_impact_uniform']['raw']['r_pre_p025']:.3f}–{s_12['h_impact_uniform']['raw']['r_pre_p975']:.3f}), "
        f"M_yd={s_12['obs_raw']['m_yd']:.4f} (H_impact 99%: {s_12['h_impact_uniform']['raw']['m_yd_p990']:.4f}, p={s_12['p_myd_exceeds_unif']:.4f})"
    )
    print(
        f"  Post-impact survivors P(t<12,750)>0.95: all={p2['survivors']['n_all_p95']} "
        f"(S12 AMS={p2['survivors']['n_s12_p95']}; >0.99 S12={p2['survivors']['n_s12_p99']})"
    )
    ct = p2["cross_taxon"]
    print(
        f"  Per-taxon OLE ({ct['n_taxa']} genera): oldest={ct['ole_oldest_median']:.0f}, "
        f"youngest={ct['ole_youngest_median']:.0f}, span={ct['ole_span_yr']:.0f} yr"
    )


if __name__ == "__main__":
    main()
