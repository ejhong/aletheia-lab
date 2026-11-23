#!/usr/bin/env python3
"""Pre-registered analysis for Issue #69 (yd-global-burn):
"Did 9% of Earth's biomass burn 12,800 years ago?"

Implements protocol.md across two independent NOAA WDS Paleoclimatology archives:
  Archive A: Global atmospheric carbon (Taylor Glacier CO2 & d13C-CO2, WAIS Divide CO2,
             Eggleston 155 kyr Antarctic d13C-CO2 composite).
  Archive B: Global terrestrial fire (Global Charcoal Database v3, GCD3).

Usage (from questions/yd-global-burn/):
  python3 analysis/burn.py --decoy   # Pre-lock verification: excludes k=0, runs on decoy window
  python3 analysis/burn.py           # Locked run: writes results/summary.json and results/*.tsv
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import pathlib
import subprocess
import sys
from collections import Counter, defaultdict
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

# ---------------------------------------------------------------------------
# Constants (matching protocol.md)
# ---------------------------------------------------------------------------
A0_DEFAULT = 12650.0
W_DEFAULT = 300.0
TG_SPANS = ((11150.0, 22250.0), (35150.0, 46250.0))
TG_DEGLAC_SPAN = ((11150.0, 22250.0),)
WAIS_SPAN = (10250.0, 21950.0)
EGG_SPAN = (950.0, 154850.0)
GCD_PRIMARY_SPAN = (1250.0, 14750.0)
GCD_LATE_GLACIAL_SPAN = (10250.0, 14750.0)
GCD_TABLES = ("SITE", "REGION", "SAMPLE", "CHARCOAL", "DATE_INFO")

REGION_MAP = {
    "WNA0": "North America",
    "ENA0": "North America",
    "EURO": "Europe",
    "CENA": "South/Central America",
    "SSA0": "South/Central America",
    "TSA0": "South/Central America",
    "ASIA": "Asia/Australasia/Africa",
    "AUST": "Asia/Australasia/Africa",
    "AFRI": "Asia/Australasia/Africa",
    "RUSS": "Asia/Australasia/Africa",
    "TROP": "Asia/Australasia/Africa",
}


# ---------------------------------------------------------------------------
# Generic helpers
# ---------------------------------------------------------------------------
def _parse_float(s: str) -> Optional[float]:
    if s is None:
        return None
    s = s.strip()
    if not s:
        return None
    try:
        v = float(s)
    except ValueError:
        return None
    return v if math.isfinite(v) else None


def _average_duplicate_ages(ages: np.ndarray, *arrays: np.ndarray) -> Tuple[np.ndarray, ...]:
    """Sort ascending by age and average values sharing identical ages."""
    order = np.argsort(ages, kind="mergesort")
    ages = ages[order]
    arrays = tuple(a[order] for a in arrays)
    uniq_ages, inv = np.unique(ages, return_inverse=True)
    if len(uniq_ages) == len(ages):
        return (ages,) + arrays
    out = []
    counts = np.bincount(inv).astype(float)
    for arr in arrays:
        sums = np.bincount(inv, weights=arr)
        out.append(sums / counts)
    return (uniq_ages,) + tuple(out)


def interp_with_gap(
    ages: np.ndarray,
    vals: np.ndarray,
    grid_t: np.ndarray,
    max_gap: float,
) -> np.ndarray:
    """Linearly interpolate vals(ages) onto grid_t, returning NaN outside [ages[0], ages[-1]]
    or wherever the bracketing raw samples straddling t are strictly more than max_gap apart.
    """
    out = np.full(len(grid_t), np.nan, dtype=float)
    if len(ages) < 2:
        return out
    idx = np.searchsorted(ages, grid_t, side="left")
    for i, t in enumerate(grid_t):
        if t < ages[0] or t > ages[-1]:
            continue
        k = int(idx[i])
        if k < len(ages) and ages[k] == t:
            out[i] = float(vals[k])
        elif 0 < k < len(ages):
            a_lo = float(ages[k - 1])
            a_hi = float(ages[k])
            if (a_hi - a_lo) <= max_gap:
                w = (t - a_lo) / (a_hi - a_lo)
                out[i] = float(vals[k - 1]) * (1.0 - w) + float(vals[k]) * w
    return out


def score_rank(
    window_map: Dict[int, float],
    target_k: int,
    a0: float = A0_DEFAULT,
    width: float = W_DEFAULT,
) -> Dict[str, object]:
    """Rank target_k among usable finite windows (higher = stronger)."""
    usable = {int(k): float(v) for k, v in window_map.items() if v is not None and math.isfinite(v)}
    n = len(usable)
    if target_k not in usable or n == 0:
        return {
            "target_k": int(target_k),
            "target_range": [a0 + target_k * width, a0 + (target_k + 1) * width],
            "value": None,
            "rank": None,
            "n_usable": n,
            "ties": None,
            "frac": None,
            "top5_cut": max(1, math.floor(0.05 * n)) if n else None,
            "top1_cut": max(1, math.floor(0.01 * n)) if n else None,
            "in_top5": False,
            "in_top1": False,
            "top10": [],
        }
    tval = usable[target_k]
    greater = sum(1 for k, v in usable.items() if k != target_k and v > tval)
    ties = sum(1 for k, v in usable.items() if k != target_k and v == tval)
    rank = 1 + greater
    top5_cut = max(1, math.floor(0.05 * n))
    top1_cut = max(1, math.floor(0.01 * n))
    ordered = sorted(usable.items(), key=lambda kv: (-kv[1], kv[0]))
    top10 = [
        {
            "rank": 1 + sum(1 for _, vv in usable.items() if vv > v),
            "k": k,
            "start_bp": a0 + k * width,
            "end_bp": a0 + (k + 1) * width,
            "mid_bp": a0 + (k + 0.5) * width,
            "value": round(v, 6),
        }
        for k, v in ordered[:10]
    ]
    return {
        "target_k": int(target_k),
        "target_range": [a0 + target_k * width, a0 + (target_k + 1) * width],
        "value": round(tval, 6),
        "rank": int(rank),
        "n_usable": int(n),
        "ties": int(ties),
        "frac": round((rank + ties) / n, 6),
        "top5_cut": int(top5_cut),
        "top1_cut": int(top1_cut),
        "in_top5": bool(rank <= top5_cut),
        "in_top1": bool(rank <= top1_cut),
        "top10": top10,
    }


def _windows_in_spans(
    spans: Sequence[Tuple[float, float]],
    a0: float,
    width: float,
) -> List[int]:
    ks: List[int] = []
    for lo, hi in spans:
        k_start = math.ceil((lo - a0) / width - 1e-9)
        k_end = math.floor((hi - a0) / width + 1e-9)
        for k in range(k_start, k_end):
            w_lo = a0 + k * width
            w_hi = a0 + (k + 1) * width
            if w_lo >= lo - 1e-9 and w_hi <= hi + 1e-9:
                ks.append(k)
    return sorted(set(ks))


# ---------------------------------------------------------------------------
# Archive A: Antarctic ice cores
# ---------------------------------------------------------------------------
def load_taylor(path: pathlib.Path) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    lines = path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    data_lines = [ln for ln in lines if ln.strip() and not ln.startswith("#")]
    ages, co2s, d13s = [], [], []
    for ln in data_lines[1:]:
        parts = ln.split("\t")
        if len(parts) < 5:
            continue
        a = _parse_float(parts[1])
        c = _parse_float(parts[2])
        d = _parse_float(parts[4])
        if a is not None and c is not None and d is not None:
            ages.append(a)
            co2s.append(c)
            d13s.append(d)
    return _average_duplicate_ages(
        np.asarray(ages, dtype=float),
        np.asarray(co2s, dtype=float),
        np.asarray(d13s, dtype=float),
    )


def load_wais(path: pathlib.Path) -> Tuple[np.ndarray, np.ndarray]:
    lines = path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    data_lines = [ln for ln in lines if ln.strip() and not ln.startswith("#")]
    ages, co2s = [], []
    for ln in data_lines[1:]:
        parts = ln.split("\t")
        if len(parts) < 3:
            continue
        a = _parse_float(parts[1])
        c = _parse_float(parts[2])
        if a is not None and c is not None:
            ages.append(a)
            co2s.append(c)
    return _average_duplicate_ages(np.asarray(ages, dtype=float), np.asarray(co2s, dtype=float))


def load_eggleston(path: pathlib.Path) -> Tuple[np.ndarray, np.ndarray]:
    lines = path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    data_lines = [ln for ln in lines if ln.strip() and not ln.startswith("#")]
    ages, d13s = [], []
    for ln in data_lines[1:]:
        parts = ln.split("\t")
        if len(parts) < 2:
            continue
        a = _parse_float(parts[0])
        d = _parse_float(parts[1])
        if a is not None and d is not None:
            ages.append(a)
            d13s.append(d)
    return _average_duplicate_ages(np.asarray(ages, dtype=float), np.asarray(d13s, dtype=float))


def compute_wais_windows(
    ages: np.ndarray,
    co2: np.ndarray,
    a0: float = A0_DEFAULT,
    width: float = W_DEFAULT,
    step: float = 100.0,
    span: Tuple[float, float] = WAIS_SPAN,
    horizons: Optional[Tuple[float, float]] = None,
) -> Dict[int, float]:
    """Compute forward-in-time CO2_rise per window for WAIS Divide."""
    if horizons is None:
        horizons = (step, 2.0 * step)
    ks = _windows_in_spans((span,), a0, width)
    if not ks:
        return {}
    m = int(round(width / step))
    min_bins = math.ceil(2 * m / 3)
    h_steps = [int(round(h / step)) for h in horizons]
    max_h = max(h_steps)

    j_min = min(ks) * m
    j_max = (max(ks) + 1) * m + max_h
    bin_vals: Dict[int, float] = {}
    for j in range(j_min, j_max + 1):
        t_lo = a0 + j * step
        t_hi = t_lo + step
        mask = (ages >= t_lo) & (ages < t_hi)
        if np.any(mask):
            bin_vals[j] = float(np.mean(co2[mask]))

    win_scores: Dict[int, float] = {}
    for k in ks:
        scores = []
        for offset in range(m):
            j = k * m + offset
            if j not in bin_vals:
                continue
            rises = []
            for hs in h_steps:
                if (j + hs) in bin_vals:
                    rises.append(bin_vals[j] - bin_vals[j + hs])
            if rises:
                scores.append(max(rises))
        if len(scores) >= min_bins:
            win_scores[k] = float(max(scores))
    return win_scores


def compute_taylor_windows(
    ages: np.ndarray,
    co2: np.ndarray,
    d13c: np.ndarray,
    a0: float = A0_DEFAULT,
    width: float = W_DEFAULT,
    step: float = 100.0,
    spans: Sequence[Tuple[float, float]] = TG_SPANS,
    max_gap: float = 500.0,
    horizons: Tuple[float, float] = (100.0, 200.0),
) -> Tuple[Dict[int, float], Dict[int, float], Dict[int, Dict[str, float]]]:
    """Compute TG_BURN (ppm * permil), TG_D13C (permil), and per-window diagnostics."""
    ks = _windows_in_spans(spans, a0, width)
    if not ks:
        return {}, {}, {}
    m = int(round(width / step))
    min_pts = math.ceil(2 * m / 3)
    h_steps = [int(round(h / step)) for h in horizons]

    # Collect every needed grid index j
    needed_j = set()
    for k in ks:
        for offset in range(m):
            j = k * m + offset
            needed_j.add(j)
            for hs in h_steps:
                needed_j.add(j + hs)
    j_list = sorted(needed_j)
    grid_t = np.asarray([a0 + j * step for j in j_list], dtype=float)
    co2_g = interp_with_gap(ages, co2, grid_t, max_gap)
    d13_g = interp_with_gap(ages, d13c, grid_t, max_gap)
    co2_map = {j: float(v) for j, v in zip(j_list, co2_g) if math.isfinite(v)}
    d13_map = {j: float(v) for j, v in zip(j_list, d13_g) if math.isfinite(v)}

    burn_map: Dict[int, float] = {}
    d13drop_map: Dict[int, float] = {}
    diag_map: Dict[int, Dict[str, float]] = {}

    for k in ks:
        burn_pts = []
        d13_pts = []
        best_burn_detail = None
        best_d13_detail = None
        for offset in range(m):
            j = k * m + offset
            if j not in co2_map or j not in d13_map:
                continue
            pt_burns = []
            pt_d13s = []
            for h, hs in zip(horizons, h_steps):
                if (j + hs) in co2_map and (j + hs) in d13_map:
                    dco2 = co2_map[j] - co2_map[j + hs]
                    d13drop = d13_map[j + hs] - d13_map[j]
                    b = max(0.0, dco2) * max(0.0, d13drop)
                    pt_burns.append(b)
                    pt_d13s.append(d13drop)
                    detail = {
                        "t_young_bp": a0 + j * step,
                        "t_old_bp": a0 + (j + hs) * step,
                        "h_yr": float(h),
                        "co2_old": co2_map[j + hs],
                        "co2_young": co2_map[j],
                        "dco2": dco2,
                        "d13_old": d13_map[j + hs],
                        "d13_young": d13_map[j],
                        "d13_drop": d13drop,
                        "burn": b,
                    }
                    if best_burn_detail is None or b > best_burn_detail["burn"]:
                        best_burn_detail = detail
                    if best_d13_detail is None or d13drop > best_d13_detail["d13_drop"]:
                        best_d13_detail = detail
            if pt_burns:
                burn_pts.append(max(pt_burns))
                d13_pts.append(max(pt_d13s))
        if len(burn_pts) >= min_pts:
            burn_map[k] = float(max(burn_pts))
            d13drop_map[k] = float(max(d13_pts))
            diag_map[k] = {
                "best_burn": best_burn_detail,
                "best_d13": best_d13_detail,
            }
    return burn_map, d13drop_map, diag_map


def compute_eggleston_windows(
    ages: np.ndarray,
    d13c: np.ndarray,
    a0: float = A0_DEFAULT,
    width: float = W_DEFAULT,
    step: float = 100.0,
    span: Tuple[float, float] = EGG_SPAN,
    max_gap: float = 300.0,
    horizons: Tuple[float, float] = (100.0, 200.0),
) -> Dict[int, float]:
    ks = _windows_in_spans((span,), a0, width)
    if not ks:
        return {}
    m = int(round(width / step))
    min_pts = math.ceil(2 * m / 3)
    h_steps = [int(round(h / step)) for h in horizons]

    needed_j = set()
    for k in ks:
        for offset in range(m):
            j = k * m + offset
            needed_j.add(j)
            for hs in h_steps:
                needed_j.add(j + hs)
    j_list = sorted(needed_j)
    grid_t = np.asarray([a0 + j * step for j in j_list], dtype=float)
    d13_g = interp_with_gap(ages, d13c, grid_t, max_gap)
    d13_map = {j: float(v) for j, v in zip(j_list, d13_g) if math.isfinite(v)}

    d13drop_map: Dict[int, float] = {}
    for k in ks:
        pts = []
        for offset in range(m):
            j = k * m + offset
            if j not in d13_map:
                continue
            drops = [d13_map[j + hs] - d13_map[j] for hs in h_steps if (j + hs) in d13_map]
            if drops:
                pts.append(max(drops))
        if len(pts) >= min_pts:
            d13drop_map[k] = float(max(pts))
    return d13drop_map


def physical_mass_balance(
    co2_before: float,
    d13c_before: float,
    d13c_after: float,
    d_bio: float = -25.0,
) -> Dict[str, float]:
    """Single-box isotopic mass balance for terrestrial C3 carbon injection into atmosphere."""
    m0_gtc = 2.12 * co2_before
    d13_drop = d13c_before - d13c_after
    if d13_drop <= 0.0:
        dc_air = 0.0
    else:
        denom = d13c_after - d_bio
        dc_air = m0_gtc * d13_drop / denom if denom > 0 else float("nan")
    return {
        "co2_before_ppm": round(co2_before, 3),
        "m0_gtc": round(m0_gtc, 2),
        "d13c_before_permil": round(d13c_before, 4),
        "d13c_after_permil": round(d13c_after, 4),
        "d13_drop_permil": round(d13_drop, 4),
        "delta_c_air_gtc": round(dc_air, 2),
        "implied_co2_rise_ppm": round(dc_air / 2.12, 2),
        "emitted_af50_gtc": round(dc_air / 0.50, 2),
        "emitted_af25_gtc": round(dc_air / 0.25, 2),
    }


# ---------------------------------------------------------------------------
# Archive B: Global Charcoal Database v3 (GCD3)
# ---------------------------------------------------------------------------
def ensure_gcd_csv(mdb_path: pathlib.Path, csv_dir: pathlib.Path) -> None:
    csv_dir.mkdir(parents=True, exist_ok=True)
    for table in GCD_TABLES:
        out = csv_dir / f"{table}.csv"
        if not out.exists():
            with open(out, "wb") as f:
                subprocess.run(["mdb-export", str(mdb_path), table], stdout=f, check=True)


def _macro_region(id_region: str, lat: Optional[float], lon: Optional[float]) -> str:
    code = (id_region or "").strip()
    if code in REGION_MAP:
        return REGION_MAP[code]
    if lat is not None and lon is not None:
        if lat > 15 and -170 <= lon <= -50:
            return "North America"
        if lat > 35 and -15 <= lon <= 60:
            return "Europe"
        if lat <= 15 and -90 <= lon <= -30:
            return "South/Central America"
        return "Asia/Australasia/Africa"
    return "Other/Unknown"


def select_site_unit(
    rows: Sequence[Tuple[str, float, str, float]],
    pref_units: str,
) -> Tuple[str, np.ndarray, np.ndarray]:
    """Deterministic unit selection per protocol.md.

    rows: sequence of (id_sample, est_age, id_units, quantity) with finite est_age and quantity >= 0.
    Returns (chosen_unit, ages_array, quantities_array) with duplicate (id_sample, unit) averaged.
    """
    unit_counts = Counter(r[2] for r in rows)
    total = len(rows)
    pref = (pref_units or "").strip()
    if pref and unit_counts.get(pref, 0) * 2 >= total:
        chosen = pref
    else:
        def _sort_key(item: Tuple[str, int]) -> Tuple[int, int, str]:
            u, cnt = item
            try:
                u_int = int(u)
            except ValueError:
                u_int = 10**9
            return (-cnt, u_int, u)

        chosen = min(unit_counts.items(), key=_sort_key)[0]

    by_sample: Dict[str, Tuple[float, List[float]]] = {}
    for sid, age, unit, qty in rows:
        if unit != chosen:
            continue
        if sid not in by_sample:
            by_sample[sid] = (age, [qty])
        else:
            by_sample[sid][1].append(qty)

    ages = []
    qtys = []
    for age, qlist in by_sample.values():
        ages.append(age)
        qtys.append(float(np.mean(qlist)))
    order = np.argsort(ages, kind="mergesort")
    return chosen, np.asarray(ages, dtype=float)[order], np.asarray(qtys, dtype=float)[order]


def load_gcd3(csv_dir: pathlib.Path) -> Dict[str, Dict[str, object]]:
    """Load GCD3 CSV tables into per-site structured records."""
    site_meta: Dict[str, Dict[str, object]] = {}
    with open(csv_dir / "SITE.csv", encoding="utf-8", errors="replace") as f:
        for row in csv.DictReader(f):
            sid = row.get("ID_SITE", "").strip()
            if not sid:
                continue
            lat = _parse_float(row.get("LATITUDE", ""))
            lon = _parse_float(row.get("LONGITUDE", ""))
            site_meta[sid] = {
                "id_site": sid,
                "site_name": row.get("SITE_NAME", "").strip(),
                "lat": lat,
                "lon": lon,
                "pref_units": row.get("PREF_UNITS", "").strip(),
                "id_region": row.get("ID_REGION", "").strip(),
                "macro_region": _macro_region(row.get("ID_REGION", ""), lat, lon),
            }

    # Dating points in [9500, 15500]
    dates_in_band: Counter = Counter()
    with open(csv_dir / "DATE_INFO.csv", encoding="utf-8", errors="replace") as f:
        for row in csv.DictReader(f):
            sid = row.get("ID_SITE", "").strip()
            if not sid:
                continue
            age = _parse_float(row.get("AGE_CALIB", ""))
            if age is None:
                age = _parse_float(row.get("AGE_C14", ""))
            if age is not None and 9500.0 <= age <= 15500.0:
                dates_in_band[sid] += 1

    # Sample ages
    sample_info: Dict[str, Tuple[str, float]] = {}
    with open(csv_dir / "SAMPLE.csv", encoding="utf-8", errors="replace") as f:
        for row in csv.DictReader(f):
            id_sample = row.get("ID_SAMPLE", "").strip()
            sid = row.get("ID_SITE", "").strip()
            age = _parse_float(row.get("EST_AGE", ""))
            if id_sample and sid and age is not None:
                sample_info[id_sample] = (sid, age)

    # Charcoal rows grouped by site
    char_rows: Dict[str, List[Tuple[str, float, str, float]]] = defaultdict(list)
    with open(csv_dir / "CHARCOAL.csv", encoding="utf-8", errors="replace") as f:
        for row in csv.DictReader(f):
            id_sample = row.get("ID_SAMPLE", "").strip()
            if id_sample not in sample_info:
                continue
            sid_s, age = sample_info[id_sample]
            qty = _parse_float(row.get("QUANTITY", ""))
            if qty is None or qty < 0.0:
                continue
            unit = row.get("ID_UNITS", "").strip()
            char_rows[sid_s].append((id_sample, age, unit, qty))

    sites_out: Dict[str, Dict[str, object]] = {}
    for sid, rows in char_rows.items():
        if sid not in site_meta or not rows:
            continue
        meta = dict(site_meta[sid])
        chosen_unit, ages, qtys = select_site_unit(rows, str(meta["pref_units"]))
        meta["chosen_unit"] = chosen_unit
        meta["ages"] = ages
        meta["quantities"] = qtys
        meta["n_dates_9500_15500"] = int(dates_in_band.get(sid, 0))
        sites_out[sid] = meta
    return sites_out


def standardize_site(
    ages: np.ndarray,
    quantities: np.ndarray,
    span_lo: float,
    span_hi: float,
) -> Optional[Tuple[np.ndarray, np.ndarray]]:
    """Log10(q + c) and Z-score over [span_lo, span_hi) per protocol.md."""
    mask = (ages >= span_lo) & (ages < span_hi)
    if not np.any(mask):
        return None
    a_sub = ages[mask]
    q_sub = quantities[mask]
    pos = q_sub[q_sub > 0.0]
    if len(pos) == 0 or float(np.max(q_sub)) == float(np.min(q_sub)):
        return None
    c = 0.5 * float(np.min(pos))
    y = np.log10(q_sub + c)
    sd = float(np.std(y, ddof=0))
    if not math.isfinite(sd) or sd <= 1e-12:
        return None
    z = (y - float(np.mean(y))) / sd
    return a_sub, z


def select_gcd_tiers(
    sites_data: Dict[str, Dict[str, object]],
    span_lo: float,
    span_hi: float,
) -> Dict[str, List[Dict[str, object]]]:
    """Select C1, C2, C3, and C3_coarse standardized sites for [span_lo, span_hi)."""
    tiers: Dict[str, List[Dict[str, object]]] = {"C1": [], "C2": [], "C3": [], "C3_coarse": []}
    for sid in sorted(sites_data.keys(), key=lambda s: (int(s) if s.isdigit() else 10**9, s)):
        rec = sites_data[sid]
        ages: np.ndarray = rec["ages"]  # type: ignore[assignment]
        qtys: np.ndarray = rec["quantities"]  # type: ignore[assignment]
        if len(ages) == 0:
            continue
        if float(ages[0]) > span_lo or float(ages[-1]) < span_hi:
            continue
        in_10_15 = ages[(ages >= 10000.0) & (ages <= 15000.0)]
        if len(in_10_15) < 15:
            continue
        std = standardize_site(ages, qtys, span_lo, span_hi)
        if std is None:
            continue
        a_std, z_std = std
        med_dt = float(np.median(np.diff(in_10_15)))
        n_dates = int(rec["n_dates_9500_15500"])  # type: ignore[arg-type]
        entry = {
            "id_site": sid,
            "site_name": rec["site_name"],
            "macro_region": rec["macro_region"],
            "lat": rec["lat"],
            "lon": rec["lon"],
            "chosen_unit": rec["chosen_unit"],
            "med_dt": med_dt,
            "n_samples_10_15k": int(len(in_10_15)),
            "n_dates_9500_15500": n_dates,
            "ages": a_std,
            "z": z_std,
        }
        tiers["C3"].append(entry)
        if med_dt <= 100.0:
            tiers["C2"].append(entry)
            if n_dates >= 2:
                tiers["C1"].append(entry)
        else:
            tiers["C3_coarse"].append(entry)
    return tiers


def compute_charcoal_metrics(
    std_sites: Sequence[Dict[str, object]],
    a0: float = A0_DEFAULT,
    width: float = W_DEFAULT,
    span_lo: float = GCD_PRIMARY_SPAN[0],
    span_hi: float = GCD_PRIMARY_SPAN[1],
    min_site_frac: float = 0.5,
    compute_100: bool = True,
) -> Dict[str, object]:
    """Compute M_mean, E_mean, F_peak (>=1.0), F_peak_15 (>=1.5), and E_100."""
    n_sites = len(std_sites)
    ks = _windows_in_spans(((span_lo, span_hi),), a0, width)
    min_present = math.ceil(min_site_frac * n_sites) if n_sites > 0 else 1

    # 300-yr (or custom width) binning
    m_mean: Dict[int, float] = {}
    f_peak: Dict[int, float] = {}
    f_peak_15: Dict[int, float] = {}
    n_present_map: Dict[int, int] = {}

    if n_sites > 0 and ks:
        site_win_vals: Dict[int, List[float]] = {k: [] for k in ks}
        for s in std_sites:
            ages: np.ndarray = s["ages"]  # type: ignore[assignment]
            z: np.ndarray = s["z"]  # type: ignore[assignment]
            w_idx = np.floor((ages - a0) / width).astype(int)
            for k in ks:
                mask = w_idx == k
                if np.any(mask):
                    site_win_vals[k].append(float(np.mean(z[mask])))
        for k in ks:
            vals = site_win_vals[k]
            n_present_map[k] = len(vals)
            if len(vals) >= min_present:
                arr = np.asarray(vals, dtype=float)
                m_mean[k] = float(np.mean(arr))
                f_peak[k] = float(np.mean(arr >= 1.0))
                f_peak_15[k] = float(np.mean(arr >= 1.5))

    # E_mean: M_mean(k) - median(M_mean(k-2..k+2)), requires >=3 of 5 windows present
    e_mean: Dict[int, float] = {}
    for k in ks:
        if k not in m_mean:
            continue
        nbrs = [m_mean[kk] for kk in range(k - 2, k + 3) if kk in m_mean]
        if len(nbrs) >= 3:
            e_mean[k] = float(m_mean[k] - float(np.median(nbrs)))

    # 100-yr binned excess E_100
    e_100_win: Dict[int, float] = {}
    m_100: Dict[int, float] = {}
    e_100_bin: Dict[int, float] = {}
    if compute_100 and n_sites > 0 and ks and int(round(width)) % 100 == 0:
        sub_per_w = int(round(width / 100.0))
        min_sub = math.ceil(2 * sub_per_w / 3)
        b_list = _windows_in_spans(((span_lo, span_hi),), a0, 100.0)
        bin_vals: Dict[int, List[float]] = {b: [] for b in b_list}
        for s in std_sites:
            ages = s["ages"]  # type: ignore[assignment]
            z = s["z"]  # type: ignore[assignment]
            b_idx = np.floor((ages - a0) / 100.0).astype(int)
            for b in b_list:
                mask = b_idx == b
                if np.any(mask):
                    bin_vals[b].append(float(np.mean(z[mask])))
        for b in b_list:
            vals = bin_vals[b]
            if len(vals) >= min_present:
                m_100[b] = float(np.mean(vals))
        for b in b_list:
            if b not in m_100:
                continue
            nbrs = [m_100[bb] for bb in range(b - 3, b + 4) if bb in m_100]
            if len(nbrs) >= 4:
                e_100_bin[b] = float(m_100[b] - float(np.median(nbrs)))
        for k in ks:
            subs = [e_100_bin[k * sub_per_w + o] for o in range(sub_per_w) if (k * sub_per_w + o) in e_100_bin]
            if len(subs) >= min_sub:
                e_100_win[k] = float(max(subs))

    return {
        "n_sites": n_sites,
        "ks": ks,
        "n_present": n_present_map,
        "M_mean": m_mean,
        "E_mean": e_mean,
        "F_peak": f_peak,
        "F_peak_15": f_peak_15,
        "E_100": e_100_win,
    }


def synthetic_pulse_sensitivity(
    std_sites: Sequence[Dict[str, object]],
    a0: float = A0_DEFAULT,
    span_lo: float = GCD_PRIMARY_SPAN[0],
    span_hi: float = GCD_PRIMARY_SPAN[1],
    amplitudes: Sequence[float] = (0.5, 1.0, 1.5, 2.0),
    fracs: Sequence[float] = (0.25, 0.50, 0.75),
    n_trials: int = 200,
    seed: int = 69,
    exclude_ks: Sequence[int] = (-1, 0, 1),
) -> List[Dict[str, object]]:
    """Inject a 100-yr global fire pulse of amplitude A into fraction p of Tier C1 sites
    at n_trials random placements (excluding exclude_ks) and measure top-5% and top-1% recovery.
    """
    n_sites = len(std_sites)
    ks = _windows_in_spans(((span_lo, span_hi),), a0, W_DEFAULT)
    b_list = _windows_in_spans(((span_lo, span_hi),), a0, 100.0)
    min_present = math.ceil(0.5 * n_sites)
    excl = set(exclude_ks)

    # Pre-index per-site per-100-yr-bin counts and sums for fast exact updates
    # site_bin_sum[s][b], site_bin_cnt[s][b]
    b_to_i = {b: i for i, b in enumerate(b_list)}
    n_b = len(b_list)
    k_to_i = {k: i for i, k in enumerate(ks)}
    n_k = len(ks)

    bin_sum = np.zeros((n_sites, n_b), dtype=float)
    bin_cnt = np.zeros((n_sites, n_b), dtype=int)
    for si, s in enumerate(std_sites):
        ages: np.ndarray = s["ages"]  # type: ignore[assignment]
        z: np.ndarray = s["z"]  # type: ignore[assignment]
        b_idx = np.floor((ages - a0) / 100.0).astype(int)
        for bi_val, z_val in zip(b_idx, z):
            bi = b_to_i.get(int(bi_val))
            if bi is not None:
                bin_sum[si, bi] += float(z_val)
                bin_cnt[si, bi] += 1

    # Also precompute baseline 300-yr window sums/counts per site
    win_sum = np.zeros((n_sites, n_k), dtype=float)
    win_cnt = np.zeros((n_sites, n_k), dtype=int)
    for ki, k in enumerate(ks):
        for o in range(3):
            bi = b_to_i.get(3 * k + o)
            if bi is not None:
                win_sum[:, ki] += bin_sum[:, bi]
                win_cnt[:, ki] += bin_cnt[:, bi]

    # Identify baseline usable windows excluding exclude_ks
    base_metrics = compute_charcoal_metrics(std_sites, a0=a0, width=W_DEFAULT, span_lo=span_lo, span_hi=span_hi)
    usable_ks = [
        k for k in ks
        if k not in excl and k in base_metrics["E_mean"] and k in base_metrics["F_peak"] and k in base_metrics["E_100"]
    ]
    if not usable_ks:
        return []

    # Helper to compute E_mean, F_peak, E_100 quickly from bin_sum/bin_cnt/win_sum/win_cnt
    def _eval_maps(w_sum, w_cnt, b_sum, b_cnt):
        # 300-yr
        w_pres = w_cnt > 0
        w_n = w_pres.sum(axis=0)
        w_z = np.divide(w_sum, w_cnt, out=np.full_like(w_sum, np.nan), where=w_pres)
        m_mean = np.full(n_k, np.nan)
        f_peak = np.full(n_k, np.nan)
        for ki in range(n_k):
            if w_n[ki] >= min_present:
                vals = w_z[w_pres[:, ki], ki]
                m_mean[ki] = float(np.mean(vals))
                f_peak[ki] = float(np.mean(vals >= 1.0))
        e_mean = np.full(n_k, np.nan)
        for ki in range(n_k):
            if math.isfinite(m_mean[ki]):
                lo = max(0, ki - 2)
                hi = min(n_k, ki + 3)
                nbrs = m_mean[lo:hi]
                nbrs = nbrs[np.isfinite(nbrs)]
                if len(nbrs) >= 3:
                    e_mean[ki] = m_mean[ki] - float(np.median(nbrs))
        # 100-yr
        b_pres = b_cnt > 0
        b_n = b_pres.sum(axis=0)
        b_z = np.divide(b_sum, b_cnt, out=np.full_like(b_sum, np.nan), where=b_pres)
        m_100 = np.full(n_b, np.nan)
        for bi in range(n_b):
            if b_n[bi] >= min_present:
                m_100[bi] = float(np.mean(b_z[b_pres[:, bi], bi]))
        e_100_b = np.full(n_b, np.nan)
        for bi in range(n_b):
            if math.isfinite(m_100[bi]):
                lo = max(0, bi - 3)
                hi = min(n_b, bi + 4)
                nbrs = m_100[lo:hi]
                nbrs = nbrs[np.isfinite(nbrs)]
                if len(nbrs) >= 4:
                    e_100_b[bi] = m_100[bi] - float(np.median(nbrs))
        e_100_w = np.full(n_k, np.nan)
        for ki, k in enumerate(ks):
            subs = []
            for o in range(3):
                bi = b_to_i.get(3 * k + o)
                if bi is not None and math.isfinite(e_100_b[bi]):
                    subs.append(e_100_b[bi])
            if len(subs) >= 2:
                e_100_w[ki] = float(max(subs))
        return e_mean, f_peak, e_100_w

    # Exclude k=0 from ranking pool if k=0 is in exclude_ks? Wait: in normal locked mode
    # k=0 is in the comparison pool (just not chosen as placement); in decoy mode k=0 is already
    # excluded via exclude_ks AND masked out from ranking if needed. Let's support masking k=0 in decoy.
    rng = np.random.default_rng(seed)
    results = []
    for amp in amplitudes:
        for p in fracs:
            n_aff = max(1, int(round(p * n_sites)))
            hits = {
                "E_mean_top5": 0, "E_mean_top1": 0,
                "F_peak_top5": 0, "F_peak_top1": 0,
                "E_100_top5": 0, "E_100_top1": 0,
            }
            for _ in range(n_trials):
                k_p = int(rng.choice(usable_ks))
                o_p = int(rng.integers(0, 3))
                b_p = 3 * k_p + o_p
                bi_p = b_to_i[b_p]
                ki_p = k_to_i[k_p]
                chosen = rng.choice(n_sites, size=n_aff, replace=False)

                # Add +amp to every sample of chosen sites falling in 100-yr bin b_p
                b_sum_mod = bin_sum.copy()
                w_sum_mod = win_sum.copy()
                delta = amp * bin_cnt[chosen, bi_p]
                b_sum_mod[chosen, bi_p] += delta
                w_sum_mod[chosen, ki_p] += delta

                e_m, f_p, e_100 = _eval_maps(w_sum_mod, win_cnt, b_sum_mod, bin_cnt)
                for name, arr in (("E_mean", e_m), ("F_peak", f_p), ("E_100", e_100)):
                    # Exclude k=0 only when running with 0 masked? Wait: we keep all non-excluded?
                    # No: during decoy check, mask k=0 so k=0 can't leak through rank!
                    valid = np.isfinite(arr)
                    if 0 in excl and 0 in k_to_i:
                        # Mask k=0 from rank calculation in synthetic test so k=0 never influences pre-lock output
                        valid[k_to_i[0]] = False
                    n_u = int(valid.sum())
                    if n_u == 0 or not valid[ki_p]:
                        continue
                    tval = arr[ki_p]
                    greater = int(np.sum(arr[valid] > tval))
                    rank = 1 + greater
                    if rank <= max(1, math.floor(0.05 * n_u)):
                        hits[f"{name}_top5"] += 1
                    if rank <= max(1, math.floor(0.01 * n_u)):
                        hits[f"{name}_top1"] += 1
            results.append({
                "amplitude_sd": amp,
                "fraction_sites": p,
                "n_affected": n_aff,
                "n_trials": n_trials,
                "E_mean_top5": round(hits["E_mean_top5"] / n_trials, 3),
                "E_mean_top1": round(hits["E_mean_top1"] / n_trials, 3),
                "F_peak_top5": round(hits["F_peak_top5"] / n_trials, 3),
                "F_peak_top1": round(hits["F_peak_top1"] / n_trials, 3),
                "E_100_top5": round(hits["E_100_top5"] / n_trials, 3),
                "E_100_top1": round(hits["E_100_top1"] / n_trials, 3),
            })
    return results


# ---------------------------------------------------------------------------
# Verdict logic (fixed in protocol.md)
# ---------------------------------------------------------------------------
def verdict_archive_a(
    tg_burn: Dict[str, object],
    wais_co2: Dict[str, object],
    egg_d13c: Dict[str, object],
) -> str:
    tg1 = bool(tg_burn.get("in_top1"))
    tg5 = bool(tg_burn.get("in_top5"))
    w5 = bool(wais_co2.get("in_top5"))
    e5 = bool(egg_d13c.get("in_top5"))
    if tg1 and (w5 or e5):
        return "Exceptional"
    n5 = int(tg5) + int(w5) + int(e5)
    if n5 >= 2:
        return "Unusual"
    if n5 == 1:
        return "Single-record only"
    return "Not met"


def verdict_archive_b(
    e_mean: Dict[str, object],
    f_peak: Dict[str, object],
    e_100: Dict[str, object],
) -> str:
    n1 = int(bool(e_mean.get("in_top1"))) + int(bool(f_peak.get("in_top1"))) + int(bool(e_100.get("in_top1")))
    n5 = int(bool(e_mean.get("in_top5"))) + int(bool(f_peak.get("in_top5"))) + int(bool(e_100.get("in_top5")))
    if n1 >= 2:
        return "Exceptional"
    if n5 >= 2:
        return "Unusual"
    return "Not met"


def verdict_joint(va: str, vb: str) -> str:
    if (va == "Exceptional" and vb in ("Exceptional", "Unusual")) or (
        va == "Unusual" and vb == "Exceptional"
    ):
        return "Strong support for global burning"
    if va == "Not met" and vb == "Not met":
        return "Not supported"
    return "Partial / mixed"


# ---------------------------------------------------------------------------
# Full pipeline
# ---------------------------------------------------------------------------
def _strip_k(d: Dict[int, float], drop_ks: Iterable[int]) -> Dict[int, float]:
    drop = set(drop_ks)
    return {k: v for k, v in d.items() if k not in drop}


def run_pipeline(base_dir: pathlib.Path, decoy: bool = False) -> Dict[str, object]:
    noaa_dir = base_dir / "data" / "noaa"
    csv_dir = base_dir / "data" / "gcd_csv"
    ensure_gcd_csv(noaa_dir / "GCD3_PUBLIC_VERSION_2013_01-Oct-2013.mdb", csv_dir)

    # Load Archive A
    tg_ages, tg_co2, tg_d13c = load_taylor(noaa_dir / "taylor2018d13co2.txt")
    wais_ages, wais_co2 = load_wais(noaa_dir / "antarctica2015co2wais-noaa.txt")
    egg_ages, egg_d13c = load_eggleston(noaa_dir / "eggleston2016d13co2-noaa.txt")

    # Compute primary Archive A window maps
    tg_burn_full, tg_d13_full, tg_diag = compute_taylor_windows(tg_ages, tg_co2, tg_d13c, spans=TG_SPANS)
    tg_burn_deg, tg_d13_deg, _ = compute_taylor_windows(tg_ages, tg_co2, tg_d13c, spans=TG_DEGLAC_SPAN)
    wais_100 = compute_wais_windows(wais_ages, wais_co2, step=100.0)
    wais_50 = compute_wais_windows(wais_ages, wais_co2, step=50.0)
    egg_map = compute_eggleston_windows(egg_ages, egg_d13c)

    # Load Archive B
    sites_data = load_gcd3(csv_dir)
    tiers_primary = select_gcd_tiers(sites_data, *GCD_PRIMARY_SPAN)
    tiers_lg = select_gcd_tiers(sites_data, *GCD_LATE_GLACIAL_SPAN)

    gcd_primary = {
        tname: compute_charcoal_metrics(tlist, span_lo=GCD_PRIMARY_SPAN[0], span_hi=GCD_PRIMARY_SPAN[1])
        for tname, tlist in tiers_primary.items()
    }
    gcd_lg = {
        tname: compute_charcoal_metrics(tlist, span_lo=GCD_LATE_GLACIAL_SPAN[0], span_hi=GCD_LATE_GLACIAL_SPAN[1])
        for tname, tlist in tiers_lg.items()
    }

    # Determine target_k and masking for decoy vs locked mode
    if decoy:
        # Remove k = -1, 0, 1 so nothing in [12,350, 13,250) can leak before locking
        drop_ks = (-1, 0, 1)
        common_ks = sorted(
            set(tg_burn_full) & set(wais_100) & set(egg_map)
            & set(gcd_primary["C1"]["E_mean"])
            & set(gcd_primary["C1"]["F_peak"])
            & set(gcd_primary["C1"]["E_100"])
        )
        candidates = [k for k in common_ks if abs(k) >= 3]
        rng = np.random.default_rng(69)
        target_k = int(rng.choice(candidates))
    else:
        drop_ks = ()
        target_k = 0

    def _m(mp: Dict[int, float]) -> Dict[int, float]:
        return _strip_k(mp, drop_ks) if drop_ks else mp

    # Score Archive A primary + secondary
    res_a = {
        "TG_BURN": score_rank(_m(tg_burn_full), target_k),
        "TG_BURN_deglacial": score_rank(_m(tg_burn_deg), target_k),
        "TG_D13C": score_rank(_m(tg_d13_full), target_k),
        "TG_D13C_deglacial": score_rank(_m(tg_d13_deg), target_k),
        "WAIS_CO2": score_rank(_m(wais_100), target_k),
        "WAIS_CO2_50": score_rank(_m(wais_50), target_k),
        "EGG_D13C": score_rank(_m(egg_map), target_k),
    }
    va = verdict_archive_a(res_a["TG_BURN"], res_a["WAIS_CO2"], res_a["EGG_D13C"])

    # Physical mass-balance check: target_k vs 16.3 ka (k = 12 -> [16250, 16550), also check k=11..13)
    phys_check: Dict[str, object] = {}
    if target_k in tg_diag and target_k not in drop_ks:
        bb = tg_diag[target_k]["best_burn"]
        bd = tg_diag[target_k]["best_d13"]
        phys_check["target_window"] = {
            "k": target_k,
            "best_burn_step": bb,
            "best_d13_step": bd,
            "mass_balance_at_best_burn": physical_mass_balance(bb["co2_old"], bb["d13_old"], bb["d13_young"]) if bb else None,
            "mass_balance_at_best_d13": physical_mass_balance(bd["co2_old"], bd["d13_old"], bd["d13_young"]) if bd else None,
        }
    # 16.3 ka HS1 benchmark: pick window in [15950, 16850) (k=11,12,13) with largest TG_BURN
    hs1_ks = [k for k in (11, 12, 13) if k in tg_burn_full and k not in drop_ks]
    if hs1_ks:
        k_hs1 = max(hs1_ks, key=lambda k: tg_burn_full[k])
        bb = tg_diag[k_hs1]["best_burn"]
        bd = tg_diag[k_hs1]["best_d13"]
        phys_check["hs1_16_3ka_benchmark"] = {
            "k": k_hs1,
            "range_bp": [A0_DEFAULT + k_hs1 * W_DEFAULT, A0_DEFAULT + (k_hs1 + 1) * W_DEFAULT],
            "best_burn_step": bb,
            "best_d13_step": bd,
            "mass_balance_at_best_burn": physical_mass_balance(bb["co2_old"], bb["d13_old"], bb["d13_young"]) if bb else None,
            "mass_balance_at_best_d13": physical_mass_balance(bd["co2_old"], bd["d13_old"], bd["d13_young"]) if bd else None,
        }

    # Score Archive B (all tiers, primary 13.5 kyr and late-glacial spans)
    res_b_primary: Dict[str, object] = {}
    for tname, mdict in gcd_primary.items():
        res_b_primary[tname] = {
            "n_sites": mdict["n_sites"],
            "M_mean": score_rank(_m(mdict["M_mean"]), target_k),
            "E_mean": score_rank(_m(mdict["E_mean"]), target_k),
            "F_peak": score_rank(_m(mdict["F_peak"]), target_k),
            "F_peak_15": score_rank(_m(mdict["F_peak_15"]), target_k),
            "E_100": score_rank(_m(mdict["E_100"]), target_k),
        }

    res_b_lg: Dict[str, object] = {}
    for tname, mdict in gcd_lg.items():
        res_b_lg[tname] = {
            "n_sites": mdict["n_sites"],
            "M_mean": score_rank(_m(mdict["M_mean"]), target_k),
            "E_mean": score_rank(_m(mdict["E_mean"]), target_k),
            "F_peak": score_rank(_m(mdict["F_peak"]), target_k),
            "F_peak_15": score_rank(_m(mdict["F_peak_15"]), target_k),
            "E_100": score_rank(_m(mdict["E_100"]), target_k),
        }

    vb = verdict_archive_b(
        res_b_primary["C1"]["E_mean"],
        res_b_primary["C1"]["F_peak"],
        res_b_primary["C1"]["E_100"],
    )
    vj = verdict_joint(va, vb)

    # Regional charcoal breakdown (on Tier C1 and Tier C2 over primary 13.5 kyr span)
    regional: Dict[str, Dict[str, object]] = {}
    for tname in ("C1", "C2", "C3"):
        regional[tname] = {}
        for reg in ("North America", "Europe", "South/Central America", "Asia/Australasia/Africa"):
            sub = [s for s in tiers_primary[tname] if s["macro_region"] == reg]
            if len(sub) < 2:
                regional[tname][reg] = {"n_sites": len(sub), "note": "fewer than 2 sites"}
                continue
            md = compute_charcoal_metrics(sub, span_lo=GCD_PRIMARY_SPAN[0], span_hi=GCD_PRIMARY_SPAN[1])
            regional[tname][reg] = {
                "n_sites": len(sub),
                "M_mean": score_rank(_m(md["M_mean"]), target_k),
                "E_mean": score_rank(_m(md["E_mean"]), target_k),
                "F_peak": score_rank(_m(md["F_peak"]), target_k),
                "E_100": score_rank(_m(md["E_100"]), target_k),
            }

    # Sensitivity checks: 150-yr, 600-yr, and +150-yr half-window shift
    sensitivity: Dict[str, object] = {}
    if not decoy:
        # 150-yr: [12725, 12875), step=50 yr
        tg_b_150, tg_d_150, _ = compute_taylor_windows(
            tg_ages, tg_co2, tg_d13c, a0=12725.0, width=150.0, step=50.0, spans=TG_SPANS, horizons=(100.0, 200.0)
        )
        wais_150 = compute_wais_windows(wais_ages, wais_co2, a0=12725.0, width=150.0, step=50.0, horizons=(100.0, 200.0))
        egg_150 = compute_eggleston_windows(egg_ages, egg_d13c, a0=12725.0, width=150.0, step=50.0, horizons=(100.0, 200.0))
        c1_150 = compute_charcoal_metrics(
            tiers_primary["C1"], a0=12725.0, width=150.0, span_lo=1325.0, span_hi=14675.0, compute_100=False
        )
        sensitivity["width_150yr"] = {
            "target_range": [12725.0, 12875.0],
            "TG_BURN": score_rank(tg_b_150, 0, a0=12725.0, width=150.0),
            "TG_D13C": score_rank(tg_d_150, 0, a0=12725.0, width=150.0),
            "WAIS_CO2": score_rank(wais_150, 0, a0=12725.0, width=150.0),
            "EGG_D13C": score_rank(egg_150, 0, a0=12725.0, width=150.0),
            "C1_E_mean": score_rank(c1_150["E_mean"], 0, a0=12725.0, width=150.0),
            "C1_F_peak": score_rank(c1_150["F_peak"], 0, a0=12725.0, width=150.0),
        }

        # 600-yr: [12500, 13100), step=100 yr
        tg_b_600, tg_d_600, _ = compute_taylor_windows(
            tg_ages, tg_co2, tg_d13c, a0=12500.0, width=600.0, step=100.0, spans=TG_SPANS
        )
        wais_600 = compute_wais_windows(wais_ages, wais_co2, a0=12500.0, width=600.0, step=100.0)
        egg_600 = compute_eggleston_windows(egg_ages, egg_d13c, a0=12500.0, width=600.0, step=100.0)
        c1_600 = compute_charcoal_metrics(
            tiers_primary["C1"], a0=12500.0, width=600.0, span_lo=1700.0, span_hi=14300.0, compute_100=True
        )
        sensitivity["width_600yr"] = {
            "target_range": [12500.0, 13100.0],
            "TG_BURN": score_rank(tg_b_600, 0, a0=12500.0, width=600.0),
            "TG_D13C": score_rank(tg_d_600, 0, a0=12500.0, width=600.0),
            "WAIS_CO2": score_rank(wais_600, 0, a0=12500.0, width=600.0),
            "EGG_D13C": score_rank(egg_600, 0, a0=12500.0, width=600.0),
            "C1_E_mean": score_rank(c1_600["E_mean"], 0, a0=12500.0, width=600.0),
            "C1_F_peak": score_rank(c1_600["F_peak"], 0, a0=12500.0, width=600.0),
            "C1_E_100": score_rank(c1_600["E_100"], 0, a0=12500.0, width=600.0),
        }

        # +150-yr half-window shift: [12800, 13100) and [12500, 12800)
        tg_b_sh, tg_d_sh, _ = compute_taylor_windows(
            tg_ages, tg_co2, tg_d13c, a0=12800.0, width=300.0, step=100.0, spans=TG_SPANS
        )
        wais_sh = compute_wais_windows(wais_ages, wais_co2, a0=12800.0, width=300.0, step=100.0)
        egg_sh = compute_eggleston_windows(egg_ages, egg_d13c, a0=12800.0, width=300.0, step=100.0)
        c1_sh = compute_charcoal_metrics(
            tiers_primary["C1"], a0=12800.0, width=300.0, span_lo=1400.0, span_hi=14600.0, compute_100=True
        )
        sensitivity["shift_plus150yr_12800_13100"] = {
            "target_range": [12800.0, 13100.0],
            "TG_BURN": score_rank(tg_b_sh, 0, a0=12800.0, width=300.0),
            "TG_D13C": score_rank(tg_d_sh, 0, a0=12800.0, width=300.0),
            "WAIS_CO2": score_rank(wais_sh, 0, a0=12800.0, width=300.0),
            "EGG_D13C": score_rank(egg_sh, 0, a0=12800.0, width=300.0),
            "C1_E_mean": score_rank(c1_sh["E_mean"], 0, a0=12800.0, width=300.0),
            "C1_F_peak": score_rank(c1_sh["F_peak"], 0, a0=12800.0, width=300.0),
            "C1_E_100": score_rank(c1_sh["E_100"], 0, a0=12800.0, width=300.0),
        }
        sensitivity["shift_minus150yr_12500_12800"] = {
            "target_range": [12500.0, 12800.0],
            "TG_BURN": score_rank(tg_b_sh, -1, a0=12800.0, width=300.0),
            "TG_D13C": score_rank(tg_d_sh, -1, a0=12800.0, width=300.0),
            "WAIS_CO2": score_rank(wais_sh, -1, a0=12800.0, width=300.0),
            "EGG_D13C": score_rank(egg_sh, -1, a0=12800.0, width=300.0),
            "C1_E_mean": score_rank(c1_sh["E_mean"], -1, a0=12800.0, width=300.0),
            "C1_F_peak": score_rank(c1_sh["F_peak"], -1, a0=12800.0, width=300.0),
            "C1_E_100": score_rank(c1_sh["E_100"], -1, a0=12800.0, width=300.0),
        }

    # Synthetic fire-pulse sensitivity test on Tier C1
    synth = synthetic_pulse_sensitivity(
        tiers_primary["C1"],
        a0=A0_DEFAULT,
        span_lo=GCD_PRIMARY_SPAN[0],
        span_hi=GCD_PRIMARY_SPAN[1],
        n_trials=200,
        seed=69,
        exclude_ks=(-1, 0, 1),
    )

    summary = {
        "mode": "decoy" if decoy else "locked",
        "target_k": target_k,
        "target_range_bp": [A0_DEFAULT + target_k * W_DEFAULT, A0_DEFAULT + (target_k + 1) * W_DEFAULT],
        "verdicts": {
            "archive_a": va,
            "archive_b": vb,
            "joint": vj,
        },
        "archive_a": res_a,
        "physical_mass_balance": phys_check,
        "archive_b_primary_13_5ka": res_b_primary,
        "archive_b_late_glacial": res_b_lg,
        "archive_b_regional_13_5ka": regional,
        "sensitivity": sensitivity,
        "synthetic_pulse_c1": synth,
        "site_counts": {
            "primary_13_5ka": {k: len(v) for k, v in tiers_primary.items()},
            "late_glacial": {k: len(v) for k, v in tiers_lg.items()},
        },
    }

    if not decoy:
        out_dir = base_dir / "results"
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

        # Write Archive A window table (union of k across TG, WAIS, EGG in [-39, 473])
        all_a_ks = sorted(set(tg_burn_full) | set(wais_100) | set(wais_50) | set(egg_map))
        with open(out_dir / "windows_archive_a.tsv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, delimiter="\t")
            w.writerow(["k", "start_bp", "end_bp", "mid_bp", "TG_BURN", "TG_D13C", "WAIS_CO2", "WAIS_CO2_50", "EGG_D13C"])
            for k in all_a_ks:
                def _fmt(mp):
                    return f"{mp[k]:.6f}" if k in mp else ""
                w.writerow([
                    k,
                    int(A0_DEFAULT + k * W_DEFAULT),
                    int(A0_DEFAULT + (k + 1) * W_DEFAULT),
                    int(A0_DEFAULT + (k + 0.5) * W_DEFAULT),
                    _fmt(tg_burn_full), _fmt(tg_d13_full), _fmt(wais_100), _fmt(wais_50), _fmt(egg_map),
                ])

        # Write Archive B primary 13.5 kyr window table across tiers
        all_b_ks = gcd_primary["C1"]["ks"]
        with open(out_dir / "windows_charcoal_13_5ka.tsv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, delimiter="\t")
            w.writerow([
                "k", "start_bp", "end_bp", "mid_bp",
                "C1_n", "C1_M_mean", "C1_E_mean", "C1_F_peak", "C1_F_peak_15", "C1_E_100",
                "C2_n", "C2_E_mean", "C2_F_peak", "C2_E_100",
                "C3_n", "C3_E_mean", "C3_F_peak", "C3_E_100",
                "coarse_n", "coarse_E_mean", "coarse_F_peak",
            ])
            for k in all_b_ks:
                def _fm(tier, key):
                    mp = gcd_primary[tier][key]
                    return f"{mp[k]:.6f}" if k in mp else ""
                w.writerow([
                    k,
                    int(A0_DEFAULT + k * W_DEFAULT),
                    int(A0_DEFAULT + (k + 1) * W_DEFAULT),
                    int(A0_DEFAULT + (k + 0.5) * W_DEFAULT),
                    gcd_primary["C1"]["n_present"].get(k, 0),
                    _fm("C1", "M_mean"), _fm("C1", "E_mean"), _fm("C1", "F_peak"), _fm("C1", "F_peak_15"), _fm("C1", "E_100"),
                    gcd_primary["C2"]["n_present"].get(k, 0),
                    _fm("C2", "E_mean"), _fm("C2", "F_peak"), _fm("C2", "E_100"),
                    gcd_primary["C3"]["n_present"].get(k, 0),
                    _fm("C3", "E_mean"), _fm("C3", "F_peak"), _fm("C3", "E_100"),
                    gcd_primary["C3_coarse"]["n_present"].get(k, 0),
                    _fm("C3_coarse", "E_mean"), _fm("C3_coarse", "F_peak"),
                ])

        # Write Tier C1/C2/C3 site roster
        c1_ids = {s["id_site"] for s in tiers_primary["C1"]}
        c2_ids = {s["id_site"] for s in tiers_primary["C2"]}
        with open(out_dir / "sites_13_5ka.tsv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, delimiter="\t")
            w.writerow([
                "id_site", "site_name", "macro_region", "lat", "lon",
                "chosen_unit", "med_dt_10_15k", "n_samples_10_15k", "n_dates_9500_15500", "tier",
            ])
            for s in tiers_primary["C3"]:
                sid = s["id_site"]
                tier = "C1" if sid in c1_ids else ("C2" if sid in c2_ids else "C3_coarse")
                w.writerow([
                    sid, s["site_name"], s["macro_region"], s["lat"], s["lon"],
                    s["chosen_unit"], f"{s['med_dt']:.2f}", s["n_samples_10_15k"], s["n_dates_9500_15500"], tier,
                ])

    return summary


def _print_report(summary: Dict[str, object]) -> None:
    mode = summary["mode"]
    tr = summary["target_range_bp"]
    v = summary["verdicts"]
    print(f"=== yd-global-burn ({mode.upper()} MODE) ===")
    print(f"Target window: k={summary['target_k']} [{tr[0]:.0f}, {tr[1]:.0f}) cal BP")
    print(f"Verdicts -> Archive A: {v['archive_a']} | Archive B: {v['archive_b']} | Joint: {v['joint']}\n")

    print("--- Archive A (Global Atmospheric Carbon) ---")
    for name in ("TG_BURN", "TG_BURN_deglacial", "TG_D13C", "WAIS_CO2", "WAIS_CO2_50", "EGG_D13C"):
        r = summary["archive_a"][name]
        print(
            f"  {name:18s}: val={r['value']} | rank={r['rank']}/{r['n_usable']} "
            f"(ties={r['ties']}, frac={r['frac']}, top5<={r['top5_cut']}, top1<={r['top1_cut']})"
        )

    print("\n--- Archive B (Global Charcoal, 13.5 kyr span) ---")
    for tier in ("C1", "C2", "C3", "C3_coarse"):
        td = summary["archive_b_primary_13_5ka"][tier]
        print(f"  Tier {tier} (n_sites={td['n_sites']}):")
        for m in ("M_mean", "E_mean", "F_peak", "F_peak_15", "E_100"):
            r = td[m]
            print(
                f"    {m:10s}: val={r['value']} | rank={r['rank']}/{r['n_usable']} "
                f"(ties={r['ties']}, frac={r['frac']}, top5<={r['top5_cut']}, top1<={r['top1_cut']})"
            )

    print("\n--- Synthetic 100-yr fire pulse recovery on Tier C1 (200 trials, seed 69) ---")
    print("  Amp(SD)  FracSites   E_mean(5%/1%)   F_peak(5%/1%)   E_100(5%/1%)")
    for row in summary["synthetic_pulse_c1"]:
        print(
            f"  {row['amplitude_sd']:6.1f}   {row['fraction_sites']:7.2f}    "
            f"{row['E_mean_top5']:5.2f} / {row['E_mean_top1']:4.2f}    "
            f"{row['F_peak_top5']:5.2f} / {row['F_peak_top1']:4.2f}    "
            f"{row['E_100_top5']:5.2f} / {row['E_100_top1']:4.2f}"
        )


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Pre-registered analysis for yd-global-burn (Issue #69).")
    parser.add_argument("--decoy", action="store_true", help="Exclude k=-1,0,1 and score a deterministic decoy window.")
    parser.add_argument("--dir", type=pathlib.Path, default=pathlib.Path("."), help="Question folder (default: .)")
    args = parser.parse_args(argv)

    summary = run_pipeline(args.dir.resolve(), decoy=args.decoy)
    _print_report(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
