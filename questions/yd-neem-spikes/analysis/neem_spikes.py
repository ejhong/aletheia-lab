#!/usr/bin/env python3
"""Pre-registered locked replication of Greenland fire-spike decomposition in NEEM 1-mm CFA (Issue #114).

Implements questions/yd-neem-spikes/protocol.md:
  - Pillar 1: Exact replication of NGRIP's 10,400-15,000 yr b2k 150-year window decomposition
              in NEEM (relative >3x/5x/10x running median), PLUS additive excess (>30/50/100 ug/kg)
              and accumulation-flux-scaled (>50 ug/kg-eq) anti-denominator-artifact controls.
  - Pillar 2: Comparison of GS-1 (Younger Dryas, 12,896 b2k) against all earlier Rasmussen et al. (2014)
              abrupt stadial onsets in 10.4-45.0 ka where NEEM resolves >= 10 samples/yr.

Usage:
    python3 questions/yd-neem-spikes/analysis/neem_spikes.py
"""
from __future__ import annotations

import csv
import json
import math
import pathlib
from typing import Any

import numpy as np
from scipy import stats

HERE = pathlib.Path(__file__).resolve().parent
QDIR = HERE.parent
DATA = QDIR / "data"
RESULTS = QDIR / "results"

ONSET = 12896
LO, HI, W = 10400, 15000, 150


# ===========================================================================
# Pure Core Engine (tested on synthetic series before lock)
# ===========================================================================

def compute_yearly_stats(
    ages: np.ndarray,
    vals: np.ndarray,
    lo_yr: int,
    hi_yr: int,
    min_samples: int = 15,
    layer_thick_fn=None,
) -> dict[str, np.ndarray]:
    """Aggregate sub-annual 1-mm NH4+ samples into yearly median, mean, max, running median, and ratios."""
    years = np.arange(lo_yr, hi_yr, dtype=int)
    n_yr = len(years)
    med = np.full(n_yr, np.nan)
    mean = np.full(n_yr, np.nan)
    top = np.full(n_yr, np.nan)
    counts = np.zeros(n_yr, dtype=int)

    ok = np.isfinite(ages) & np.isfinite(vals) & (ages >= lo_yr) & (ages < hi_yr)
    yr_idx = np.floor(ages[ok]).astype(int) - lo_yr
    v_ok = vals[ok]

    order = np.argsort(yr_idx, kind="stable")
    ys, vs = yr_idx[order], v_ok[order]
    cuts = np.searchsorted(ys, np.arange(0, n_yr + 1))

    for i in range(n_yr):
        seg = vs[cuts[i] : cuts[i + 1]]
        counts[i] = len(seg)
        if len(seg) >= min_samples:
            med[i] = float(np.median(seg))
            mean[i] = float(np.mean(seg))
            top[i] = float(np.max(seg))

    run = np.full(n_yr, np.nan)
    for i in range(n_yr):
        w = med[max(0, i - 25) : min(n_yr, i + 26)]
        if np.isfinite(w).sum() >= 30:
            run[i] = float(np.nanmedian(w))

    ratio = np.where((run > 0) & np.isfinite(top) & np.isfinite(run), top / run, np.nan)
    excess = np.where(np.isfinite(top) & np.isfinite(run), top - run, np.nan)

    if layer_thick_fn is not None:
        lam = np.asarray(layer_thick_fn(years + 0.5), dtype=float)
        lam_ref = float(np.nanmedian(lam))
        flux_excess = excess * (lam / lam_ref)
    else:
        lam = np.ones(n_yr, dtype=float)
        flux_excess = excess.copy()

    return {
        "years": years,
        "med": med,
        "mean": mean,
        "top": top,
        "run": run,
        "ratio": ratio,
        "excess": excess,
        "flux_excess": flux_excess,
        "lambda_m_yr": lam,
        "counts": counts,
    }


def summarize_windows(
    yr_stats: dict[str, np.ndarray],
    onset: int = ONSET,
    lo_yr: int = LO,
    hi_yr: int = HI,
    win_len: int = W,
    min_valid_frac: float = 0.80,
) -> dict[str, Any]:
    """Group yearly stats into 150-yr windows anchored at onset and compute ranks & tests."""
    years = yr_stats["years"]
    med = yr_stats["med"]
    mean = yr_stats["mean"]
    ratio = yr_stats["ratio"]
    excess = yr_stats["excess"]
    flux_ex = yr_stats["flux_excess"]

    wins: list[dict[str, Any]] = []
    k = int(math.floor((onset - hi_yr) / win_len))
    while onset - win_len * (k + 1) >= lo_yr:
        w_lo = onset - win_len * (k + 1)
        w_hi = onset - win_len * k
        if w_hi <= hi_yr:
            m = (years >= w_lo) & (years < w_hi) & np.isfinite(ratio) & np.isfinite(med)
            if int(m.sum()) >= int(min_valid_frac * win_len):
                lvl = float(np.nanmean(med[m]))
                sp = float(np.nanmean((mean - med)[m]))
                wins.append({
                    "k": k,
                    "from_b2k": w_hi,
                    "to_b2k": w_lo,
                    "years": int(m.sum()),
                    "samples_per_yr_med": float(np.median(yr_stats["counts"][m])),
                    "level": round(lvl, 3),
                    "spike_part": round(sp, 3),
                    "total_mean": round(lvl + sp, 3),
                    "spike_years_x3": int(np.sum(ratio[m] > 3.0)),
                    "spike_years_x5": int(np.sum(ratio[m] > 5.0)),
                    "spike_years_x10": int(np.sum(ratio[m] > 10.0)),
                    "spike_years_add30": int(np.sum(excess[m] > 30.0)),
                    "spike_years_add50": int(np.sum(excess[m] > 50.0)),
                    "spike_years_add100": int(np.sum(excess[m] > 100.0)),
                    "spike_years_flux50": int(np.sum(flux_ex[m] > 50.0)),
                    "largest_ratio": round(float(np.nanmax(ratio[m])), 2),
                    "largest_excess": round(float(np.nanmax(excess[m])), 2),
                })
        k += 1

    by_k = {w["k"]: w for w in wins}
    metrics = [
        "level", "spike_part", "total_mean",
        "spike_years_x3", "spike_years_x5", "spike_years_x10",
        "spike_years_add30", "spike_years_add50", "spike_years_add100",
        "spike_years_flux50", "largest_ratio", "largest_excess",
    ]
    ranks: dict[str, Any] = {}
    medians: dict[str, float] = {}
    for mk in metrics:
        vals = [w[mk] for w in wins]
        medians[mk] = float(np.median(vals)) if vals else float("nan")
        if 0 in by_k and -1 in by_k:
            ranks[mk] = {
                "after_rank_desc": 1 + sum(v > by_k[0][mk] for v in vals),
                "after_rank_asc": 1 + sum(v < by_k[0][mk] for v in vals),
                "n_windows": len(vals),
                "after_val": by_k[0][mk],
                "before_val": by_k[-1][mk],
                "median_val": medians[mk],
            }

    a, b = by_k[0], by_k[-1]
    level_ratio = a["level"] / b["level"] if b["level"] > 0 else float("nan")
    tot_delta = a["total_mean"] - b["total_mean"]
    share_from_level = (a["level"] - b["level"]) / tot_delta if abs(tot_delta) > 1e-9 else float("nan")

    # Exact two-sided binomial / Poisson rate-ratio test on spike years (Window 0 vs Window -1)
    def rate_test(c0: int, n0: int, cm1: int, nm1: int) -> dict[str, float]:
        tot = c0 + cm1
        if tot == 0:
            return {"rate_ratio": 1.0, "p_two_sided": 1.0}
        p0 = n0 / (n0 + nm1)
        pval = float(stats.binomtest(c0, tot, p=p0, alternative="two-sided").pvalue)
        rr = (c0 / n0) / (cm1 / nm1) if cm1 > 0 else float("inf")
        return {"rate_ratio": float(rr), "p_two_sided": pval}

    tests = {
        "x5_after_vs_before": rate_test(a["spike_years_x5"], a["years"], b["spike_years_x5"], b["years"]),
        "x3_after_vs_before": rate_test(a["spike_years_x3"], a["years"], b["spike_years_x3"], b["years"]),
        "add50_after_vs_before": rate_test(a["spike_years_add50"], a["years"], b["spike_years_add50"], b["years"]),
        "flux50_after_vs_before": rate_test(a["spike_years_flux50"], a["years"], b["spike_years_flux50"], b["years"]),
    }

    return {
        "n_windows": len(wins),
        "windows": wins,
        "window_after": a,
        "window_before": b,
        "level_after_over_before": round(level_ratio, 3),
        "spike_part_after_over_before": round(a["spike_part"] / b["spike_part"], 3) if b["spike_part"] > 0 else float("nan"),
        "share_of_rise_from_level": round(share_from_level, 3),
        "ranks": ranks,
        "medians": medians,
        "rate_tests": tests,
    }


def decide_verdict(summary: dict[str, Any]) -> str:
    """Pre-registered mutually exclusive verdict rule from protocol.md Section 4."""
    a = summary["window_after"]
    b = summary["window_before"]
    lvl_ratio = summary["level_after_over_before"]
    share = summary["share_of_rise_from_level"]
    med_x5 = summary["medians"]["spike_years_x5"]
    n_win = summary["n_windows"]

    x5_drop = (a["spike_years_x5"] < b["spike_years_x5"]) and (a["spike_years_x5"] < med_x5)
    x5_rise = (a["spike_years_x5"] > b["spike_years_x5"]) and (a["spike_years_x5"] > med_x5)

    add50_ratio = a["spike_years_add50"] / max(b["spike_years_add50"], 1)
    add50_rank_desc = summary["ranks"]["spike_years_add50"]["after_rank_desc"]
    add50_surge = (add50_ratio >= 1.5) and (add50_rank_desc <= max(1, int(math.floor(0.10 * n_win))))

    if lvl_ratio >= 1.5 and share >= 0.70 and x5_drop and not add50_surge:
        return "replicated_steady_not_spiky"
    if lvl_ratio >= 1.5 and x5_drop and add50_surge:
        return "replicated_relative_but_additive_spikes_rise"
    if x5_rise:
        return "failed_to_replicate_more_spikes"
    return "inconclusive_or_mixed"


# ===========================================================================
# Data Loaders (PANGAEA NEEM 5-cm GICC05 + 1-mm CFA + Rasmussen 2014 events)
# ===========================================================================

def load_neem_gicc05(path: pathlib.Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Load NEEM 5-cm GICC05 depth (m), age (yr b2k), and d18O (permil)."""
    depths, ages, d18o = [], [], []
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        in_hdr = True
        for line in f:
            if in_hdr:
                if line.startswith("*/"):
                    in_hdr = False
                    next(f)
                continue
            p = line.rstrip("\n").split("\t")
            if len(p) >= 2 and p[0] and p[1]:
                depths.append(float(p[0]))
                ages.append(float(p[1]) * 1000.0)
                d18o.append(float(p[5]) if len(p) > 5 and p[5] else np.nan)
    return np.array(depths), np.array(ages), np.array(d18o)


def load_neem_nh4_range(
    cfa_path: pathlib.Path,
    g_depths: np.ndarray,
    g_ages: np.ndarray,
    min_age: float,
    max_age: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Stream 1-mm NEEM [NH4]+ within [min_age, max_age] yr b2k and interpolate exact GICC05 ages."""
    d_lo = float(np.interp(min_age, g_ages, g_depths)) - 0.5
    d_hi = float(np.interp(max_age, g_ages, g_depths)) + 0.5
    ds, vals = [], []
    with cfa_path.open("r", encoding="utf-8", errors="ignore") as f:
        in_hdr = True
        for line in f:
            if in_hdr:
                if line.startswith("*/"):
                    in_hdr = False
                    next(f)
                continue
            p = line.rstrip("\n").split("\t")
            if not p[0]:
                continue
            d = float(p[0])
            if d < d_lo:
                continue
            if d > d_hi:
                break
            if len(p) > 4 and p[4]:
                ds.append(d)
                vals.append(float(p[4]))
    d_arr = np.array(ds, dtype=float)
    v_arr = np.array(vals, dtype=float)
    a_arr = np.interp(d_arr, g_depths, g_ages)
    return a_arr, v_arr


def load_stadial_onsets(events_path: pathlib.Path) -> list[dict[str, Any]]:
    out = []
    with events_path.open("r", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            if r.get("kind") == "stadial onset":
                out.append({"event": r["event"], "age_b2k": float(r["age_b2k"])})
    return out


def run_pipeline() -> dict[str, Any]:
    RESULTS.mkdir(parents=True, exist_ok=True)
    g_depths, g_ages, _ = load_neem_gicc05(DATA / "neem_gicc05_5cm.tab")

    # Local annual layer thickness function lambda(age) = dz / dt (m/yr) smoothed over 20-yr window
    def layer_thick_fn(age_arr: np.ndarray) -> np.ndarray:
        z_hi = np.interp(age_arr + 10.0, g_ages, g_depths)
        z_lo = np.interp(age_arr - 10.0, g_ages, g_depths)
        return (z_hi - z_lo) / 20.0

    # Pillar 1: 10,400 - 15,000 yr b2k exact NGRIP replication + additive/flux controls
    ages_p1, vals_p1 = load_neem_nh4_range(DATA / "neem_cfa_1mm.tab", g_depths, g_ages, LO - 30, HI + 30)
    ys_p1 = compute_yearly_stats(ages_p1, vals_p1, LO, HI, min_samples=15, layer_thick_fn=layer_thick_fn)
    p1_sum = summarize_windows(ys_p1, onset=ONSET, lo_yr=LO, hi_yr=HI, win_len=W)
    verdict = decide_verdict(p1_sum)

    # Pillar 2: All abrupt stadial onsets in 10.4 - 45.0 ka where NEEM resolves >= 10 samples/yr
    events = [e for e in load_stadial_onsets(QDIR / "events.tsv") if 12000 <= e["age_b2k"] <= 45000]
    ages_p2, vals_p2 = load_neem_nh4_range(DATA / "neem_cfa_1mm.tab", g_depths, g_ages, 10400, 45500)
    ys_p2 = compute_yearly_stats(ages_p2, vals_p2, 10400, 45500, min_samples=10, layer_thick_fn=layer_thick_fn)

    stadial_rows = []
    for ev in events:
        t0 = int(round(ev["age_b2k"]))
        yrs = ys_p2["years"]
        m_bef = (yrs >= t0) & (yrs < t0 + 150) & np.isfinite(ys_p2["ratio"])
        m_aft = (yrs >= t0 - 150) & (yrs < t0) & np.isfinite(ys_p2["ratio"])
        if int(m_bef.sum()) < 100 or int(m_aft.sum()) < 100:
            continue
        lvl_b = float(np.nanmean(ys_p2["med"][m_bef]))
        lvl_a = float(np.nanmean(ys_p2["med"][m_aft]))
        sp_b = float(np.nanmean((ys_p2["mean"] - ys_p2["med"])[m_bef]))
        sp_a = float(np.nanmean((ys_p2["mean"] - ys_p2["med"])[m_aft]))
        x5_b = int(np.sum(ys_p2["ratio"][m_bef] > 5.0))
        x5_a = int(np.sum(ys_p2["ratio"][m_aft] > 5.0))
        add50_b = int(np.sum(ys_p2["excess"][m_bef] > 50.0))
        add50_a = int(np.sum(ys_p2["excess"][m_aft] > 50.0))
        stadial_rows.append({
            "event": ev["event"],
            "age_b2k": t0,
            "years_before": int(m_bef.sum()),
            "years_after": int(m_aft.sum()),
            "samples_per_yr_after": round(float(np.median(ys_p2["counts"][m_aft])), 1),
            "level_before": round(lvl_b, 2),
            "level_after": round(lvl_a, 2),
            "level_ratio": round(lvl_a / lvl_b, 2) if lvl_b > 0 else float("nan"),
            "spike_part_before": round(sp_b, 2),
            "spike_part_after": round(sp_a, 2),
            "x5_before": x5_b,
            "x5_after": x5_a,
            "x5_delta": x5_a - x5_b,
            "add50_before": add50_b,
            "add50_after": add50_a,
            "add50_delta": add50_a - add50_b,
        })

    # Annual time series around YD onset (13,500 -> 12,000 b2k) for interactive plotting
    yd_annual = []
    for i, y in enumerate(ys_p1["years"]):
        if 12000 <= y <= 13500 and np.isfinite(ys_p1["med"][i]):
            yd_annual.append({
                "year_b2k": int(y),
                "med": round(float(ys_p1["med"][i]), 2),
                "top": round(float(ys_p1["top"][i]), 2),
                "run": round(float(ys_p1["run"][i]), 2) if np.isfinite(ys_p1["run"][i]) else None,
                "ratio": round(float(ys_p1["ratio"][i]), 2) if np.isfinite(ys_p1["ratio"][i]) else None,
                "excess": round(float(ys_p1["excess"][i]), 2) if np.isfinite(ys_p1["excess"][i]) else None,
            })

    summary = {
        "question": "yd-neem-spikes",
        "issue": 114,
        "verdict": verdict,
        "pillar1_neem_104_150ka": {
            "years_with_data": int(np.isfinite(ys_p1["med"]).sum()),
            "samples_per_year_median": float(np.median(ys_p1["counts"][np.isfinite(ys_p1["med"])])),
            "ngrip_exploratory_reference": {
                "source": "questions/ice-core-fire/explore/repeated_fires.json (exploratory, single core)",
                "level_after_over_before": 2.7,
                "spike_years_x5_after": 4,
                "spike_years_x5_before": 18,
                "spike_years_x5_median": 19,
            },
            **p1_sum,
        },
        "pillar2_stadial_onsets": {
            "n_events": len(stadial_rows),
            "n_with_x5_drop": sum(1 for r in stadial_rows if r["x5_delta"] < 0),
            "n_with_level_rise": sum(1 for r in stadial_rows if r["level_ratio"] > 1.0),
            "events": stadial_rows,
        },
        "yd_annual_series": yd_annual,
    }

    (RESULTS / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    with (RESULTS / "windows.tsv").open("w", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        cols = ["k", "from_b2k", "to_b2k", "years", "samples_per_yr_med", "level", "spike_part", "total_mean", "spike_years_x3", "spike_years_x5", "spike_years_x10", "spike_years_add30", "spike_years_add50", "spike_years_add100", "spike_years_flux50", "largest_ratio", "largest_excess"]
        w.writerow(cols)
        for row in p1_sum["windows"]:
            w.writerow([row[c] for c in cols])

    with (RESULTS / "stadials.tsv").open("w", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        cols = ["event", "age_b2k", "years_before", "years_after", "samples_per_yr_after", "level_before", "level_after", "level_ratio", "x5_before", "x5_after", "x5_delta", "add50_before", "add50_after", "add50_delta"]
        w.writerow(cols)
        for row in stadial_rows:
            w.writerow([row[c] for c in cols])

    return summary


if __name__ == "__main__":
    out = run_pipeline()
    p1 = out["pillar1_neem_104_150ka"]
    a, b = p1["window_after"], p1["window_before"]
    print(f"Verdict: {out['verdict']}")
    print(f"NEEM 10.4-15.0 ka: {p1['n_windows']} windows, med samples/yr = {p1['samples_per_year_median']:.1f}")
    print(f"Steady level: after={a['level']} vs before={b['level']} ({p1['level_after_over_before']}x, share={p1['share_of_rise_from_level']:.2f}, rank={p1['ranks']['level']['after_rank_desc']}/{p1['n_windows']})")
    print(f"Spike years >5x: after={a['spike_years_x5']} vs before={b['spike_years_x5']} (med={p1['medians']['spike_years_x5']}, p={p1['rate_tests']['x5_after_vs_before']['p_two_sided']:.4g})")
    print(f"Additive >50 ug/kg: after={a['spike_years_add50']} vs before={b['spike_years_add50']} (med={p1['medians']['spike_years_add50']}, rank={p1['ranks']['spike_years_add50']['after_rank_desc']}/{p1['n_windows']}, p={p1['rate_tests']['add50_after_vs_before']['p_two_sided']:.4g})")
    print(f"Flux >50 ug/kg-eq: after={a['spike_years_flux50']} vs before={b['spike_years_flux50']} (med={p1['medians']['spike_years_flux50']}, p={p1['rate_tests']['flux50_after_vs_before']['p_two_sided']:.4g})")
    print(f"Pillar 2 stadials: {out['pillar2_stadial_onsets']['n_events']} events, x5_drop={out['pillar2_stadial_onsets']['n_with_x5_drop']}")
