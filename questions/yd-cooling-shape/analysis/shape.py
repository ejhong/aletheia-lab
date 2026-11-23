#!/usr/bin/env python3
"""Pre-registered analysis for Issue #75 (yd-cooling-shape):
"Was the Younger Dryas cooling different from other abrupt ice-age coolings?"

Compares GS-1 (Younger Dryas, 12,896 yr b2k) against all other qualifying abrupt stadial
coolings in Rasmussen et al. (2014) across Greenland (NGRIP d18O, temperature, Ca2+ dust;
plus 3-core NGRIP/GRIP/GISP2 cross-check) and Antarctica (Buizert et al. 2021 7-core
temperature reconstruction).

Usage (from questions/yd-cooling-shape/):
  python3 analysis/shape.py --decoy   # Pre-lock check: removes GS-1, runs on decoy stadial
  python3 analysis/shape.py           # Locked run: writes results/summary.json & results/*.tsv
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import pathlib
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

ANT_SITES = ("TS_WD", "TS_EDML", "TS_EDC", "TS_TAL", "TS_SDM", "TS_SP", "TS_DF")


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


# ---------------------------------------------------------------------------
# Data loaders
# ---------------------------------------------------------------------------
def load_events(path: pathlib.Path) -> Tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    """Return (all_events, qualifying_stadial_onsets) per protocol.md."""
    all_ev: List[Dict[str, object]] = []
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            all_ev.append({
                "event": row["event"].strip(),
                "age_b2k": float(row["age_b2k"]),
                "kind": row["kind"].strip(),
                "unc": row["definition_uncertainty"].strip(),
            })
    all_ages = [float(e["age_b2k"]) for e in all_ev]
    qual = []
    for e in all_ev:
        if e["kind"] != "stadial onset":
            continue
        if e["unc"] not in ("4yr", "a", "b"):
            continue
        t = float(e["age_b2k"])
        # No other listed event strictly inside (t - 200, t + 100)
        conflict = any((t - 200.0) < a < (t + 100.0) and a != t for a in all_ages)
        if not conflict:
            qual.append(e)
    return all_ev, qual


def load_ngrip_d18o(path: pathlib.Path) -> Tuple[np.ndarray, np.ndarray]:
    """Return (midpoint_b2k, d18o) from gicc05-60ka-20yr.txt (bin a covers [a-20, a))."""
    mids, vals = [], []
    for ln in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        p = ln.strip().split()
        if len(p) >= 3:
            a = _parse_float(p[0])
            d = _parse_float(p[2])
            if a is not None and d is not None:
                mids.append(a - 10.0)
                vals.append(d)
    order = np.argsort(mids)
    return np.asarray(mids, dtype=float)[order], np.asarray(vals, dtype=float)[order]


def load_ngrip_temp(path: pathlib.Path) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return (age_b2k, temp_c, accum) from ngrip2014temp.txt."""
    ages, temps, accs = [], [], []
    lines = path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    for ln in lines:
        if not ln.strip() or ln.startswith("#"):
            continue
        p = ln.strip().split()
        if len(p) >= 5:
            a = _parse_float(p[2])
            ac = _parse_float(p[3])
            t = _parse_float(p[4])
            if a is not None and ac is not None and t is not None:
                ages.append(a)
                temps.append(t)
                accs.append(ac)
    order = np.argsort(ages)
    return (
        np.asarray(ages, dtype=float)[order],
        np.asarray(temps, dtype=float)[order],
        np.asarray(accs, dtype=float)[order],
    )


def load_ngrip_ca(path: pathlib.Path) -> Tuple[np.ndarray, np.ndarray]:
    """Return (midpoint_b2k, ca_ug_kg) from 935814.tab (row a covers [a, a+10))."""
    mids, vals = [], []
    in_data = False
    for ln in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        if not in_data:
            if ln.startswith("Age [ka b2k]"):
                in_data = True
            continue
        p = ln.split("\t")
        if len(p) >= 4:
            a_ka = _parse_float(p[0])
            ca = _parse_float(p[3])
            if a_ka is not None and ca is not None and ca > 0.0:
                mids.append(a_ka * 1000.0 + 5.0)
                vals.append(ca)
    order = np.argsort(mids)
    return np.asarray(mids, dtype=float)[order], np.asarray(vals, dtype=float)[order]


def load_ant_temp(path: pathlib.Path) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
    """Return (age_bp1950, {site_name: temp_c, 'TS_MEAN': 7-core mean}) from buizert2021-temp.txt."""
    lines = path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    hdr_idx = None
    for i, ln in enumerate(lines):
        if ln.startswith("age_yrBP1950"):
            hdr_idx = i
            break
    if hdr_idx is None:
        raise ValueError("Could not find header in buizert2021-temp.txt")
    hdr = lines[hdr_idx].strip().split("\t")
    col_idx = {name: hdr.index(name) for name in ANT_SITES}
    ages = []
    series: Dict[str, List[float]] = {name: [] for name in ANT_SITES}
    for ln in lines[hdr_idx + 1:]:
        p = ln.strip().split("\t")
        if len(p) <= max(col_idx.values()):
            continue
        a = _parse_float(p[0])
        if a is None:
            continue
        vals = [_parse_float(p[col_idx[name]]) for name in ANT_SITES]
        if any(v is None for v in vals):
            continue
        ages.append(a)
        for name, v in zip(ANT_SITES, vals):
            series[name].append(float(v))  # type: ignore[arg-type]
    age_arr = np.asarray(ages, dtype=float)
    order = np.argsort(age_arr)
    age_arr = age_arr[order]
    out = {name: np.asarray(series[name], dtype=float)[order] for name in ANT_SITES}
    out["TS_MEAN"] = np.mean(np.vstack([out[name] for name in ANT_SITES]), axis=0)
    return age_arr, out


def load_g3_20yr(path: pathlib.Path) -> Dict[str, Tuple[np.ndarray, np.ndarray]]:
    """Return synchronized 20-yr NGRIP, GRIP, GISP2 d18O from gicc05-calcium-20yr.txt."""
    mids = []
    cols = {"NGRIP": [], "GRIP": [], "GISP2": []}
    for ln in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        p = ln.strip().split()
        if len(p) >= 11:
            a = _parse_float(p[0])
            n_d = _parse_float(p[3])
            g_d = _parse_float(p[6])
            p2_d = _parse_float(p[9])
            if a is not None and n_d is not None and g_d is not None and p2_d is not None:
                mids.append(a - 10.0)
                cols["NGRIP"].append(n_d)
                cols["GRIP"].append(g_d)
                cols["GISP2"].append(p2_d)
    m_arr = np.asarray(mids, dtype=float)
    order = np.argsort(m_arr)
    m_arr = m_arr[order]
    return {k: (m_arr, np.asarray(v, dtype=float)[order]) for k, v in cols.items()}


# ---------------------------------------------------------------------------
# Metric computations
# ---------------------------------------------------------------------------
def _window_mean(ages: np.ndarray, vals: np.ndarray, lo: float, hi: float) -> Optional[float]:
    mask = (ages >= lo) & (ages < hi)
    if not np.any(mask):
        return None
    return float(np.mean(vals[mask]))


def cooling_metrics_series(
    ages: np.ndarray,
    vals: np.ndarray,
    t: float,
    pre_hi: float = 100.0,
    abrupt_w: float = 60.0,
    amp_lo: float = 40.0,
    amp_hi: float = 200.0,
    slope_hi: float = 200.0,
) -> Dict[str, Optional[float]]:
    """Compute abrupt_60, amp, pre_slope (per century), and peak_rate_20 for a cooling at onset t."""
    pre = _window_mean(ages, vals, t, t + pre_hi)
    post_abrupt = _window_mean(ages, vals, t - abrupt_w, t)
    post_amp = _window_mean(ages, vals, t - amp_hi, t - amp_lo)

    abrupt = (pre - post_abrupt) if (pre is not None and post_abrupt is not None) else None
    amp = (pre - post_amp) if (pre is not None and post_amp is not None) else None

    # Precursor OLS slope over [t, t + slope_hi) against forward time tau = (t - age) / 100 (centuries)
    pmask = (ages >= t) & (ages < t + slope_hi)
    pre_slope = None
    if int(pmask.sum()) >= 3:
        tau_c = (t - ages[pmask]) / 100.0  # -2.0 (older) -> 0.0 (onset)
        y = vals[pmask]
        x_m = float(np.mean(tau_c))
        y_m = float(np.mean(y))
        denom = float(np.sum((tau_c - x_m) ** 2))
        if denom > 0:
            pre_slope = float(np.sum((tau_c - x_m) * (y - y_m)) / denom)

    # Peak single 20-yr step drop inside [t - 80, t + 40)
    # Forward in time: older bin (b+20) minus younger bin (b) -> positive = cooling drop
    # Using exact 20-yr adjacent bins when step == 20
    rmask = (ages >= t - 80.0) & (ages < t + 40.0)
    idx = np.where(rmask)[0]
    peak_step = None
    steps = []
    for i in idx:
        if i + 1 < len(ages):
            dt = float(ages[i + 1] - ages[i])
            if 15.0 <= dt <= 25.0:
                steps.append(float(vals[i + 1] - vals[i]) * (20.0 / dt))
    if steps:
        peak_step = float(max(steps))

    return {
        "pre_mean": pre,
        "abrupt_60": abrupt,
        "amp": amp,
        "pre_slope": pre_slope,
        "peak_rate_20": peak_step,
    }


def dust_metrics(ages: np.ndarray, ca: np.ndarray, t: float) -> Dict[str, Optional[float]]:
    """Compute ln(Ca2+) jump into the stadial (higher = larger dust surge)."""
    log_ca = np.log(ca)
    pre = _window_mean(ages, log_ca, t, t + 100.0)
    post_amp = _window_mean(ages, log_ca, t - 200.0, t - 40.0)
    post_60 = _window_mean(ages, log_ca, t - 60.0, t)
    return {
        "dust_jump": (post_amp - pre) if (pre is not None and post_amp is not None) else None,
        "dust_abrupt_60": (post_60 - pre) if (pre is not None and post_60 is not None) else None,
    }


def antarctic_bipolar_metric(ages_bp: np.ndarray, temp: np.ndarray, t_b2k: float) -> Dict[str, Optional[float]]:
    """Compute delta_T_ant (post - pre; positive = warming/bipolar seesaw) and ant_cool = -delta_T_ant."""
    t_bp = t_b2k - 50.0
    pre = _window_mean(ages_bp, temp, t_bp, t_bp + 200.0)
    post = _window_mean(ages_bp, temp, t_bp - 200.0, t_bp)
    if pre is None or post is None:
        return {"delta_T_ant": None, "ant_cool": None}
    dt = post - pre
    return {"delta_T_ant": float(dt), "ant_cool": float(-dt)}


def score_event_rank(
    rows: Sequence[Dict[str, object]],
    target_event: str,
    key: str,
) -> Dict[str, object]:
    """Rank target_event on metric `key` (higher = rank 1)."""
    usable = [
        (str(r["event"]), float(r["age_b2k"]), float(r[key]))
        for r in rows
        if r.get(key) is not None and math.isfinite(float(r[key]))
    ]
    n = len(usable)
    t_entry = next((u for u in usable if u[0] == target_event), None)
    if t_entry is None or n == 0:
        return {
            "target": target_event,
            "value": None,
            "rank": None,
            "n": n,
            "top10_cut": max(1, math.floor(0.10 * n)) if n else None,
            "in_top10": False,
            "median_others": None,
            "iqr_others": None,
        }
    tval = t_entry[2]
    others = [u[2] for u in usable if u[0] != target_event]
    greater = sum(1 for v in others if v > tval)
    ties = sum(1 for v in others if v == tval)
    rank = 1 + greater
    top10_cut = max(1, math.floor(0.10 * n))
    ordered = sorted(usable, key=lambda u: (-u[2], u[1]))
    return {
        "target": target_event,
        "value": round(tval, 4),
        "rank": int(rank),
        "n": int(n),
        "ties": int(ties),
        "frac": round((rank + ties) / n, 4),
        "top10_cut": int(top10_cut),
        "in_top10": bool(rank <= top10_cut),
        "median_others": round(float(np.median(others)), 4) if others else None,
        "iqr_others": [round(float(np.percentile(others, 25)), 4), round(float(np.percentile(others, 75)), 4)] if others else None,
        "top5": [{"event": u[0], "age_b2k": int(u[1]), "value": round(u[2], 4)} for u in ordered[:5]],
    }


def evaluate_verdict(d1: bool, d2: bool, d3: bool, d4: bool) -> str:
    """Fixed verdict rule from protocol.md (partitions all 16 boolean combinations)."""
    n_green = int(d1) + int(d2) + int(d3)
    if n_green == 3 or (d4 and n_green >= 1):
        return "Distinct from natural coolings (catastrophic-trigger signature)"
    if n_green >= 1 or d4:
        return "Extreme case of a natural cooling"
    return "Indistinguishable from natural coolings"


def compute_composite_profile(
    ages: np.ndarray,
    vals: np.ndarray,
    events: Sequence[Dict[str, object]],
    target_event: str,
    step: float = 20.0,
    rel_lo: float = -300.0,
    rel_hi: float = 300.0,
    age_shift: float = 0.0,
    log_transform: bool = False,
) -> Dict[str, object]:
    """Compute baseline-centered profile (tau = t - age, negative = before onset, positive = after)
    for target_event vs. median & IQR of all other events.
    """
    bins = np.arange(rel_lo, rel_hi, step)
    mids = bins + step / 2.0
    v_use = np.log(vals) if log_transform else vals

    target_prof = None
    other_profs = []
    for e in events:
        t = float(e["age_b2k"]) - age_shift
        base = _window_mean(ages, v_use, t, t + 100.0)
        if base is None:
            continue
        prof = []
        for b in bins:
            # tau in [b, b+step) -> age = t - tau in (t - b - step, t - b]
            val = _window_mean(ages, v_use, t - b - step, t - b)
            prof.append((val - base) if val is not None else np.nan)
        arr = np.asarray(prof, dtype=float)
        if e["event"] == target_event:
            target_prof = arr
        else:
            other_profs.append(arr)

    mat = np.vstack(other_profs) if other_profs else np.empty((0, len(bins)))
    return {
        "tau_mid_yr": [float(m) for m in mids],
        "target": [round(float(x), 4) if math.isfinite(x) else None for x in target_prof] if target_prof is not None else [],
        "median_others": [round(float(np.nanmedian(mat[:, i])), 4) if np.any(np.isfinite(mat[:, i])) else None for i in range(len(bins))],
        "q25_others": [round(float(np.nanpercentile(mat[:, i], 25)), 4) if np.any(np.isfinite(mat[:, i])) else None for i in range(len(bins))],
        "q75_others": [round(float(np.nanpercentile(mat[:, i], 75)), 4) if np.any(np.isfinite(mat[:, i])) else None for i in range(len(bins))],
    }


# ---------------------------------------------------------------------------
# Full pipeline
# ---------------------------------------------------------------------------
def run_pipeline(base_dir: pathlib.Path, decoy: bool = False) -> Dict[str, object]:
    noaa = base_dir / "data" / "noaa"
    pang = base_dir / "data" / "pangaea"

    _, qual = load_events(base_dir / "events.tsv")
    d18_a, d18_v = load_ngrip_d18o(noaa / "gicc05-60ka-20yr.txt")
    t_a, t_v, acc_v = load_ngrip_temp(noaa / "ngrip2014temp.txt")
    ca_a, ca_v = load_ngrip_ca(pang / "935814.tab")
    ant_a, ant_dict = load_ant_temp(noaa / "buizert2021-temp.txt")
    g3 = load_g3_20yr(noaa / "gicc05-calcium-20yr.txt")

    if decoy:
        qual = [e for e in qual if e["event"] != "GS-1"]
        # Pick a deterministic decoy stadial present in all 3 pools (i.e., t + 200 <= 40000)
        cands = [e["event"] for e in qual if (float(e["age_b2k"]) - 50.0 + 200.0) <= 40000.0]
        rng = np.random.default_rng(75)
        target_ev = str(rng.choice(cands))
    else:
        target_ev = "GS-1"

    pool_60 = [e for e in qual if float(e["age_b2k"]) - 200.0 >= 10000.0 and float(e["age_b2k"]) + 200.0 <= 60000.0]
    pool_100 = [e for e in qual if float(e["age_b2k"]) - 200.0 >= 10300.0 and float(e["age_b2k"]) + 200.0 <= 107620.0]
    pool_40 = [e for e in qual if (float(e["age_b2k"]) - 50.0 - 200.0) >= 10000.0 and (float(e["age_b2k"]) - 50.0 + 200.0) <= 40000.0]

    # Pool 1: 60-kyr NGRIP d18O
    rows_60 = []
    for e in pool_60:
        t = float(e["age_b2k"])
        m = cooling_metrics_series(d18_a, d18_v, t)
        m_alt = cooling_metrics_series(d18_a, d18_v, t, pre_hi=150.0, abrupt_w=100.0)
        rows_60.append({
            "event": e["event"],
            "age_b2k": int(t),
            "abrupt_60": m["abrupt_60"],
            "amp_d18o": m["amp"],
            "pre_slope": m["pre_slope"],
            "peak_rate_20": m["peak_rate_20"],
            "abrupt_100_alt": m_alt["abrupt_60"],
        })

    # Pool 2: 100-kyr NGRIP temp, accumulation, Ca2+ dust
    rows_100 = []
    for e in pool_100:
        t = float(e["age_b2k"])
        mt = cooling_metrics_series(t_a, t_v, t)
        ma = cooling_metrics_series(t_a, np.log(np.maximum(acc_v, 1e-6)), t)
        mc = dust_metrics(ca_a, ca_v, t)
        rows_100.append({
            "event": e["event"],
            "age_b2k": int(t),
            "abrupt_temp_60": mt["abrupt_60"],
            "amp_temp": mt["amp"],
            "pre_slope_temp": mt["pre_slope"],
            "dust_jump": mc["dust_jump"],
            "dust_abrupt_60": mc["dust_abrupt_60"],
            "accum_log_drop": ma["amp"],
        })

    # Pool 3: 40-kyr Antarctic bipolar response
    rows_40 = []
    for e in pool_40:
        t = float(e["age_b2k"])
        row = {"event": e["event"], "age_b2k": int(t), "age_bp": int(t - 50.0)}
        for site in ("TS_MEAN",) + ANT_SITES:
            mb = antarctic_bipolar_metric(ant_a, ant_dict[site], t)
            row[f"{site}_dT"] = mb["delta_T_ant"]
            row[f"{site}_cool"] = mb["ant_cool"]
        rows_40.append(row)

    # 3-core Greenland cross-check (11.6 - 32.4 ka)
    pool_g3 = [e for e in qual if float(e["age_b2k"]) - 200.0 >= 11620.0 and float(e["age_b2k"]) + 200.0 <= 32440.0]
    rows_g3: Dict[str, List[Dict[str, object]]] = {c: [] for c in ("NGRIP", "GRIP", "GISP2")}
    for c in ("NGRIP", "GRIP", "GISP2"):
        ca_m, ca_d = g3[c]
        for e in pool_g3:
            t = float(e["age_b2k"])
            m = cooling_metrics_series(ca_m, ca_d, t)
            rows_g3[c].append({
                "event": e["event"],
                "age_b2k": int(t),
                "abrupt_60": m["abrupt_60"],
                "amp_d18o": m["amp"],
                "pre_slope": m["pre_slope"],
            })

    # Score primary and secondary measures
    s_abrupt_60 = score_event_rank(rows_60, target_ev, "abrupt_60")
    s_amp_d18o = score_event_rank(rows_60, target_ev, "amp_d18o")
    s_pre_slope = score_event_rank(rows_60, target_ev, "pre_slope")
    s_peak_20 = score_event_rank(rows_60, target_ev, "peak_rate_20")
    s_abrupt_100_alt = score_event_rank(rows_60, target_ev, "abrupt_100_alt")

    s_amp_temp = score_event_rank(rows_100, target_ev, "amp_temp")
    s_abrupt_temp = score_event_rank(rows_100, target_ev, "abrupt_temp_60")
    s_pre_slope_temp = score_event_rank(rows_100, target_ev, "pre_slope_temp")
    s_dust_jump = score_event_rank(rows_100, target_ev, "dust_jump")
    s_dust_abrupt = score_event_rank(rows_100, target_ev, "dust_abrupt_60")
    s_accum = score_event_rank(rows_100, target_ev, "accum_log_drop")

    s_ant_mean_cool = score_event_rank(rows_40, target_ev, "TS_MEAN_cool")
    s_ant_mean_dT = next((r["TS_MEAN_dT"] for r in rows_40 if r["event"] == target_ev), None)
    ant_by_site = {
        site: {
            "dT_target": next((round(float(r[f"{site}_dT"]), 4) for r in rows_40 if r["event"] == target_ev and r[f"{site}_dT"] is not None), None),
            "cool_rank": score_event_rank(rows_40, target_ev, f"{site}_cool"),
        }
        for site in ("TS_MEAN",) + ANT_SITES
    }

    # Evaluate D1..D4 and fixed verdict
    d1 = bool(s_abrupt_60["in_top10"])
    d2 = bool(s_amp_temp["in_top10"] or s_dust_jump["in_top10"])
    d3 = bool(s_pre_slope["in_top10"])
    d4 = bool(s_ant_mean_dT is not None and float(s_ant_mean_dT) < 0.0 and s_ant_mean_cool["rank"] == 1)
    verdict = evaluate_verdict(d1, d2, d3, d4)

    profiles = {}
    if not decoy:
        profiles = {
            "ngrip_d18o_60ka": compute_composite_profile(d18_a, d18_v, pool_60, target_ev, step=20.0),
            "ngrip_temp_100ka": compute_composite_profile(t_a, t_v, pool_100, target_ev, step=20.0),
            "ngrip_log_ca_100ka": compute_composite_profile(ca_a, ca_v, pool_100, target_ev, step=20.0, log_transform=True),
            "ant_mean_40ka": compute_composite_profile(ant_a, ant_dict["TS_MEAN"], pool_40, target_ev, step=40.0, age_shift=50.0),
            "ant_wd_40ka": compute_composite_profile(ant_a, ant_dict["TS_WD"], pool_40, target_ev, step=40.0, age_shift=50.0),
        }

    summary = {
        "mode": "decoy" if decoy else "locked",
        "target_event": target_ev,
        "pool_sizes": {"pool_60": len(pool_60), "pool_100": len(pool_100), "pool_40": len(pool_40), "pool_g3": len(pool_g3)},
        "criteria": {"D1_abruptness": d1, "D2_amp_or_dust": d2, "D3_out_of_blue": d3, "D4_ant_cooling": d4},
        "verdict": verdict,
        "primary": {
            "abrupt_60_d18o": s_abrupt_60,
            "amp_temp_100ka": s_amp_temp,
            "dust_jump_100ka": s_dust_jump,
            "pre_slope_d18o": s_pre_slope,
            "ant_mean_cool_40ka": s_ant_mean_cool,
            "ant_mean_dT_target": round(float(s_ant_mean_dT), 4) if s_ant_mean_dT is not None else None,
        },
        "alongside": {
            "amp_d18o_60ka": s_amp_d18o,
            "peak_rate_20_d18o": s_peak_20,
            "abrupt_100_alt_d18o": s_abrupt_100_alt,
            "abrupt_temp_60_100ka": s_abrupt_temp,
            "pre_slope_temp_100ka": s_pre_slope_temp,
            "dust_abrupt_60_100ka": s_dust_abrupt,
            "accum_log_drop_100ka": s_accum,
            "antarctica_sites": ant_by_site,
            "three_core_32ka": {
                c: {
                    "abrupt_60": score_event_rank(rows_g3[c], target_ev, "abrupt_60"),
                    "amp_d18o": score_event_rank(rows_g3[c], target_ev, "amp_d18o"),
                    "pre_slope": score_event_rank(rows_g3[c], target_ev, "pre_slope"),
                }
                for c in ("NGRIP", "GRIP", "GISP2")
            },
        },
        "profiles": profiles,
    }

    if not decoy:
        out_dir = base_dir / "results"
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

        def _write_tsv(fname: str, rlist: Sequence[Dict[str, object]]) -> None:
            if not rlist:
                return
            cols = list(rlist[0].keys())
            with open(out_dir / fname, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f, delimiter="\t")
                w.writerow(cols)
                for r in rlist:
                    w.writerow([f"{r[c]:.5f}" if isinstance(r[c], float) else ("" if r[c] is None else r[c]) for c in cols])

        _write_tsv("coolings_60ka_d18o.tsv", rows_60)
        _write_tsv("coolings_100ka_temp_dust.tsv", rows_100)
        _write_tsv("coolings_40ka_antarctica.tsv", rows_40)

    return summary


def _print_report(s: Dict[str, object]) -> None:
    print(f"=== yd-cooling-shape ({s['mode'].upper()} MODE) | Target: {s['target_event']} ===")
    print(f"Pools: 60ka={s['pool_sizes']['pool_60']}, 100ka={s['pool_sizes']['pool_100']}, 40ka_Ant={s['pool_sizes']['pool_40']}")
    print(f"Criteria: {s['criteria']}")
    print(f"Verdict:  {s['verdict']}\n")
    for k, r in s["primary"].items():
        if isinstance(r, dict):
            print(
                f"  {k:22s}: val={r['value']} | rank={r['rank']}/{r['n']} "
                f"(top10<={r['top10_cut']}, met={r['in_top10']}) | others med={r['median_others']} IQR={r['iqr_others']}"
            )
    print(f"  {'ant_mean_dT_target':22s}: {s['primary']['ant_mean_dT_target']} °C (+ = warming/bipolar seesaw, - = cooling)")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Pre-registered analysis for yd-cooling-shape (Issue #75).")
    parser.add_argument("--decoy", action="store_true", help="Exclude GS-1 and score a deterministic decoy cooling.")
    parser.add_argument("--dir", type=pathlib.Path, default=pathlib.Path("."), help="Question folder (default: .)")
    args = parser.parse_args(argv)
    summary = run_pipeline(args.dir.resolve(), decoy=args.decoy)
    _print_report(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
