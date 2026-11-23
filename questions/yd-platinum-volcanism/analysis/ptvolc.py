#!/usr/bin/env python3
"""Pre-registered analysis for Issue #76 (yd-platinum-volcanism):
"Did the GISP2 platinum spike precede the Younger Dryas cooling—or follow it during a volcanic cluster?"

Part 1: GISP2 platinum depth/timing (1712.375-1712.000 m, peak 1712.1875 m) tested on
        synchronized GICC05 (Svensson 2020 + Rasmussen 2008) and directly inside GISP2
        depth stratigraphy (d18O, Ca2+, Na+, SO4^2-).
Part 2: 51,000-year Greenland & bipolar volcanic sulfate context (Lin et al. 2022, 60-9 ka)
        + Monte Carlo association across all 19 abrupt coolings (10-60 ka).

Usage (from questions/yd-platinum-volcanism/):
  python3 analysis/ptvolc.py --decoy   # Pre-lock verification excluding YD target
  python3 analysis/ptvolc.py           # Locked run writing results/
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import math
import pathlib
import sys
import xml.etree.ElementTree as ET
import zipfile
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

if "/usr/lib/python3/dist-packages" not in sys.path:
    sys.path.append("/usr/lib/python3/dist-packages")
import xlrd  # type: ignore[import-not-found]

PT_ONSET_M = 1712.375
PT_PEAK_M = 1712.1875
PT_END_M = 1712.000
GS1_ONSET_B2K = 12896.0


def _parse_float(s: object) -> Optional[float]:
    if s is None:
        return None
    if isinstance(s, (int, float)):
        return float(s) if math.isfinite(float(s)) else None
    st = str(s).strip()
    if not st:
        return None
    try:
        v = float(st)
    except ValueError:
        return None
    return v if math.isfinite(v) else None


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------
def load_svensson2020_ties(zip_path: pathlib.Path) -> List[Dict[str, object]]:
    """Read Table S2 from Svensson et al. (2020) .xlsx using stdlib XML."""
    with zipfile.ZipFile(zip_path) as zf:
        xraw = zf.read("Bipolar supplementary tables ver 2020-07-16.xlsx")
    with zipfile.ZipFile(io.BytesIO(xraw)) as xzf:
        ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
        wb_xml = ET.fromstring(xzf.read("xl/workbook.xml"))
        sheets = [(s.attrib["name"], i + 1) for i, s in enumerate(wb_xml.findall(".//m:sheet", ns))]
        ss: List[str] = []
        if "xl/sharedStrings.xml" in xzf.namelist():
            ss_xml = ET.fromstring(xzf.read("xl/sharedStrings.xml"))
            for si in ss_xml.findall(".//m:si", ns):
                ss.append("".join(t.text or "" for t in si.findall(".//m:t", ns)))
        t2_idx = next(idx for name, idx in sheets if name == "Table S2")
        sh_xml = ET.fromstring(xzf.read(f"xl/worksheets/sheet{t2_idx}.xml"))

        def _col_to_i(ref: str) -> int:
            letters = "".join(ch for ch in ref if ch.isalpha())
            n = 0
            for ch in letters:
                n = n * 26 + (ord(ch.upper()) - ord("A") + 1)
            return n - 1

        ties = []
        for r in sh_xml.findall(".//m:row", ns)[1:]:
            row_vals: Dict[int, str] = {}
            for c in r.findall("m:c", ns):
                ci = _col_to_i(c.attrib["r"])
                t = c.attrib.get("t")
                v = c.find("m:v", ns)
                val = v.text if v is not None else ""
                if t == "s" and val.isdigit():
                    val = ss[int(val)]
                row_vals[ci] = val
            # col 1=NGRIP depth, 4=GISP2 depth, 8=GICC05 age(b2k), 9=WD2014 age(b2k), 10=Comments
            gisp2_d = _parse_float(row_vals.get(4))
            gicc_a = _parse_float(row_vals.get(8))
            if gisp2_d is not None and gicc_a is not None:
                ties.append({
                    "gisp2_depth_m": gisp2_d,
                    "ngrip_depth_m": _parse_float(row_vals.get(1)),
                    "gicc05_b2k": gicc_a,
                    "wd2014_b2k": _parse_float(row_vals.get(9)),
                    "comment": row_vals.get(10, "").strip(),
                })
        ties.sort(key=lambda x: float(x["gisp2_depth_m"]))
        return ties


def load_g3_gisp2(path: pathlib.Path) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return (gisp2_depth_m, gicc05_age_b2k, gisp2_d18o, gisp2_ca) sorted ascending by depth."""
    depths, ages, d18s, cas = [], [], [], []
    for ln in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        p = ln.strip().split()
        if len(p) >= 11:
            a = _parse_float(p[0])
            d = _parse_float(p[8])
            o = _parse_float(p[9])
            c = _parse_float(p[10])
            if a is not None and d is not None and o is not None:
                depths.append(d)
                ages.append(a)
                d18s.append(o)
                cas.append(c if c is not None else np.nan)
    arr_d = np.asarray(depths, dtype=float)
    order = np.argsort(arr_d)
    return (
        arr_d[order],
        np.asarray(ages, dtype=float)[order],
        np.asarray(d18s, dtype=float)[order],
        np.asarray(cas, dtype=float)[order],
    )


def load_gispd18o_2m(path: pathlib.Path) -> Tuple[np.ndarray, np.ndarray]:
    """Return (midpoint_depth_m = top + 1.0, d18o) from gispd18o.txt."""
    depths, vals = [], []
    for ln in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        p = ln.strip().split()
        if len(p) >= 3:
            d = _parse_float(p[0])
            o = _parse_float(p[1])
            a = _parse_float(p[2])
            if d is not None and o is not None and a is not None and o < 0.0:
                depths.append(d + 1.0)
                vals.append(o)
    arr_d = np.asarray(depths, dtype=float)
    order = np.argsort(arr_d)
    return arr_d[order], np.asarray(vals, dtype=float)[order]


def load_gisp2_ions(path: pathlib.Path) -> Dict[str, np.ndarray]:
    """Return midpoint depth and Na, NH4, Ca, SO4 (ppb) from iond.txt."""
    mids, tops, bots, nas, nh4s, cas, so4s = [], [], [], [], [], [], []
    for ln in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        p = ln.strip().split()
        if len(p) >= 12:
            t = _parse_float(p[0])
            b = _parse_float(p[1])
            na = _parse_float(p[2])
            nh4 = _parse_float(p[3])
            ca = _parse_float(p[6])
            so4 = _parse_float(p[9])
            if t is not None and b is not None and b >= t:
                mids.append(0.5 * (t + b))
                tops.append(t)
                bots.append(b)
                nas.append(na if na is not None else np.nan)
                nh4s.append(nh4 if nh4 is not None else np.nan)
                cas.append(ca if ca is not None else np.nan)
                so4s.append(so4 if so4 is not None else np.nan)
    m_arr = np.asarray(mids, dtype=float)
    order = np.argsort(m_arr)
    return {
        "mid_m": m_arr[order],
        "top_m": np.asarray(tops, dtype=float)[order],
        "bot_m": np.asarray(bots, dtype=float)[order],
        "na": np.asarray(nas, dtype=float)[order],
        "nh4": np.asarray(nh4s, dtype=float)[order],
        "ca": np.asarray(cas, dtype=float)[order],
        "so4": np.asarray(so4s, dtype=float)[order],
    }


def load_lin2022(zip_path: pathlib.Path) -> Tuple[List[Dict[str, float]], List[Dict[str, object]]]:
    """Load Greenland Table S3 (1,113 eruptions) and Bipolar Table S5 (85 eruptions) from Lin et al. 2022."""
    with zipfile.ZipFile(zip_path) as zf:
        raw = zf.read("Supplementary tables.xls")
    wb = xlrd.open_workbook(file_contents=raw)

    # Table S3: col 12 = Age (b2k), col 13 = Average deposition (kg km-2)
    sh3 = wb.sheet_by_name("Table S3")
    gl_events: List[Dict[str, float]] = []
    for r in range(2, sh3.nrows):
        age = _parse_float(sh3.cell_value(r, 12))
        dep = _parse_float(sh3.cell_value(r, 13))
        if age is not None and dep is not None and dep >= 0.0:
            gl_events.append({
                "age_b2k": age,
                "dep_kg_km2": dep,
                "ngrip_dep": _parse_float(sh3.cell_value(r, 0)) or float("nan"),
                "gisp2_dep": _parse_float(sh3.cell_value(r, 4)) or float("nan"),
                "neem_dep": _parse_float(sh3.cell_value(r, 8)) or float("nan"),
            })
    gl_events.sort(key=lambda e: e["age_b2k"])

    # Table S5: col 1 = GICC05 Age (a b2k), col 26 = Average stratospheric aerosol loading (Tg)
    sh5 = wb.sheet_by_name("Table S5")
    bi_events: List[Dict[str, object]] = []
    for r in range(2, sh5.nrows):
        age = _parse_float(sh5.cell_value(r, 1))
        load = _parse_float(sh5.cell_value(r, 26))
        if age is not None and load is not None and load >= 0.0:
            bi_events.append({
                "age_b2k": age,
                "aerosol_tg": load,
                "forcing_wm2": _parse_float(sh5.cell_value(r, 28)),
                "comment": str(sh5.cell_value(r, 3)).strip(),
                "site_pred": str(sh5.cell_value(r, 31)).strip(),
            })
    bi_events.sort(key=lambda e: float(e["age_b2k"]))
    return gl_events, bi_events


def load_sigl2021(path: pathlib.Path) -> List[Dict[str, object]]:
    """Load Sigl et al. (2021) PANGAEA.930557 table."""
    lines = path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    hdr_idx = next(i for i, ln in enumerate(lines) if ln.startswith("Age [ka BP]"))
    out = []
    for ln in lines[hdr_idx + 1:]:
        p = ln.split("\t")
        if len(p) >= 7:
            a_ka = _parse_float(p[0])
            gl_d = _parse_float(p[1])
            ant_d = _parse_float(p[3])
            vssi = _parse_float(p[5])
            if a_ka is not None and vssi is not None:
                out.append({
                    "age_bp_gicc05": round(a_ka * 1000.0, 1),
                    "age_b2k_gicc05": round(a_ka * 1000.0 + 50.0, 1),
                    "gl_dep_kg_km2": gl_d,
                    "ant_dep_kg_km2": ant_d,
                    "type": p[4].strip(),
                    "vssi_tg": vssi,
                    "vssi_sd": _parse_float(p[6]),
                })
    return out


def load_stadial_onsets_60ka(path: pathlib.Path) -> List[Dict[str, object]]:
    all_ev = []
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
        t = float(e["age_b2k"])
        if e["kind"] == "stadial onset" and e["unc"] in ("4yr", "a", "b"):
            if 10500.0 <= t <= 59500.0:
                if not any((t - 200.0) < a < (t + 100.0) and a != t for a in all_ages):
                    qual.append(e)
    return qual


# ---------------------------------------------------------------------------
# Core algorithms (Part 1 & Part 2)
# ---------------------------------------------------------------------------
def interp_depth_to_age(depths: np.ndarray, ages: np.ndarray, target_d: float) -> Tuple[float, Dict[str, float]]:
    """Linearly interpolate age at target_d from ascending depths, returning (age, bracket_info)."""
    if target_d < depths[0] or target_d > depths[-1]:
        raise ValueError(f"target_d={target_d} outside [{depths[0]}, {depths[-1]}]")
    idx = int(np.searchsorted(depths, target_d, side="left"))
    if depths[idx] == target_d:
        return float(ages[idx]), {
            "d_lo": float(depths[idx]), "a_lo": float(ages[idx]),
            "d_hi": float(depths[idx]), "a_hi": float(ages[idx]),
        }
    d_lo, d_hi = float(depths[idx - 1]), float(depths[idx])
    a_lo, a_hi = float(ages[idx - 1]), float(ages[idx])
    w = (target_d - d_lo) / (d_hi - d_lo)
    return a_lo + w * (a_hi - a_lo), {"d_lo": d_lo, "a_lo": a_lo, "d_hi": d_hi, "a_hi": a_hi}


def step_changepoint(
    depths: np.ndarray,
    vals: np.ndarray,
    d_lo: float,
    d_hi: float,
    shallower_higher: bool,
    min_side: int = 5,
) -> Optional[Dict[str, float]]:
    """Two-piece step changepoint minimizing SSE(deeper) + SSE(shallower) over [d_lo, d_hi]."""
    mask = (depths >= d_lo) & (depths <= d_hi) & np.isfinite(vals)
    d = depths[mask]
    y = vals[mask]
    order = np.argsort(d)
    d = d[order]
    y = y[order]
    n = len(d)
    if n < 2 * min_side:
        return None
    best_sse = float("inf")
    best = None
    # Split between index i-1 (shallower) and i (deeper)
    for i in range(min_side, n - min_side + 1):
        y_sh = y[:i]
        y_dp = y[i:]
        m_sh = float(np.mean(y_sh))
        m_dp = float(np.mean(y_dp))
        if shallower_higher and not (m_sh > m_dp):
            continue
        if (not shallower_higher) and not (m_dp > m_sh):
            continue
        sse = float(np.sum((y_sh - m_sh) ** 2) + np.sum((y_dp - m_dp) ** 2))
        if sse < best_sse:
            best_sse = sse
            best = {
                "split_depth_m": round(0.5 * (float(d[i - 1]) + float(d[i])), 4),
                "shallower_mean": round(m_sh, 4),
                "deeper_mean": round(m_dp, 4),
                "delta": round(m_sh - m_dp, 4),
                "n_pts": int(n),
            }
    return best


def cooling_init_depth(
    depths: np.ndarray,
    d18o: np.ndarray,
    base_lo: float = 1717.0,
    base_hi: float = 1725.0,
    search_lo: float = 1700.0,
) -> Optional[Dict[str, float]]:
    """Find deepest depth < base_lo where d18O < mean_base - 1.0*sd_base for 2 consecutive shallower points."""
    bmask = (depths >= base_lo) & (depths <= base_hi) & np.isfinite(d18o)
    if int(bmask.sum()) < 3:
        return None
    mu = float(np.mean(d18o[bmask]))
    sd = float(np.std(d18o[bmask], ddof=0))
    thresh = mu - 1.0 * sd

    smask = (depths >= search_lo) & (depths < base_lo) & np.isfinite(d18o)
    d = depths[smask]
    y = d18o[smask]
    # Sort deepest -> shallowest (descending depth = forward in time)
    order = np.argsort(-d)
    d = d[order]
    y = y[order]
    for i in range(len(d) - 1):
        if y[i] < thresh and y[i + 1] < thresh:
            return {
                "init_depth_m": round(float(d[i]), 4),
                "init_d18o": round(float(y[i]), 4),
                "base_mean": round(mu, 4),
                "base_sd": round(sd, 4),
                "threshold": round(thresh, 4),
            }
    return None


def score_volcanic_windows(
    ages_b2k: np.ndarray,
    weights: np.ndarray,
    a0: float = GS1_ONSET_B2K,
    width: float = 150.0,
    span_lo: float = 9296.0,
    span_hi: float = 59996.0,
    gap: Optional[Tuple[float, float]] = None,
    target_k: int = 0,
    drop_ks: Sequence[int] = (),
) -> Dict[str, object]:
    """Sum weights in non-overlapping windows [a0 + width*k, a0 + width*(k+1)) across [span_lo, span_hi)."""
    k_start = math.ceil((span_lo - a0) / width - 1e-9)
    k_end = math.floor((span_hi - a0) / width + 1e-9)
    drop = set(drop_ks)
    win_sum: Dict[int, float] = {}
    win_cnt: Dict[int, int] = {}
    for k in range(k_start, k_end):
        if k in drop:
            continue
        w_lo = a0 + k * width
        w_hi = a0 + (k + 1) * width
        if gap is not None and not (w_hi <= gap[0] or w_lo >= gap[1]):
            continue
        mask = (ages_b2k >= w_lo) & (ages_b2k < w_hi)
        win_sum[k] = float(np.sum(weights[mask]))
        win_cnt[k] = int(np.sum(mask))

    n = len(win_sum)
    tval = win_sum.get(target_k)
    tcnt = win_cnt.get(target_k)
    if tval is None or n == 0:
        return {"target_k": target_k, "value": None, "count": None, "rank": None, "n": n, "in_top5": False}
    greater = sum(1 for k, v in win_sum.items() if k != target_k and v > tval)
    ties = sum(1 for k, v in win_sum.items() if k != target_k and v == tval)
    rank = 1 + greater
    top5_cut = max(1, math.floor(0.05 * n))
    ordered = sorted(win_sum.items(), key=lambda kv: (-kv[1], kv[0]))
    top10 = [
        {
            "rank": 1 + sum(1 for _, vv in win_sum.items() if vv > v),
            "k": k,
            "start_b2k": round(a0 + k * width, 1),
            "end_b2k": round(a0 + (k + 1) * width, 1),
            "value": round(v, 3),
            "count": win_cnt[k],
        }
        for k, v in ordered[:10]
    ]
    return {
        "target_k": int(target_k),
        "target_range_b2k": [round(a0 + target_k * width, 1), round(a0 + (target_k + 1) * width, 1)],
        "value": round(tval, 3),
        "count": int(tcnt),
        "rank": int(rank),
        "ties": int(ties),
        "n": int(n),
        "frac": round((rank + ties) / n, 4),
        "top5_cut": int(top5_cut),
        "in_top5": bool(rank <= top5_cut),
        "median_all": round(float(np.median(list(win_sum.values()))), 3),
        "mean_all": round(float(np.mean(list(win_sum.values()))), 3),
        "top10": top10,
        "all_windows": [{"k": k, "start_b2k": round(a0 + k * width, 1), "end_b2k": round(a0 + (k + 1) * width, 1), "value": round(v, 3), "count": win_cnt[k]} for k, v in sorted(win_sum.items())],
    }


def volcanic_cooling_mc(
    volc_ages: np.ndarray,
    volc_deps: np.ndarray,
    onset_ages: Sequence[float],
    pre_window: float = 50.0,
    n_iter: int = 10000,
    seed: int = 76,
    lo_b2k: float = 10500.0,
    hi_b2k: float = 59500.0,
) -> Dict[str, float]:
    """Monte Carlo test of mean volcanic sulfate in [t, t + pre_window) before abrupt coolings."""
    m = len(onset_ages)
    # Prefix-sum / searchsorted for fast exact window sums
    order = np.argsort(volc_ages)
    va = volc_ages[order]
    vd = volc_deps[order]
    csum = np.concatenate([[0.0], np.cumsum(vd)])

    def _mean_sum(ts: np.ndarray) -> np.ndarray:
        i0 = np.searchsorted(va, ts, side="left")
        i1 = np.searchsorted(va, ts + pre_window, side="left")
        return csum[i1] - csum[i0]

    obs_arr = _mean_sum(np.asarray(onset_ages, dtype=float))
    obs_mean = float(np.mean(obs_arr))
    rng = np.random.default_rng(seed)
    rand_ts = rng.uniform(lo_b2k, hi_b2k, size=(n_iter, m))
    null_means = np.mean(_mean_sum(rand_ts), axis=1)
    p_val = (1 + int(np.sum(null_means >= obs_mean))) / (n_iter + 1)
    return {
        "n_coolings": int(m),
        "pre_window_yr": float(pre_window),
        "obs_mean_dep": round(obs_mean, 3),
        "null_mean_dep": round(float(np.mean(null_means)), 3),
        "null_p95_dep": round(float(np.percentile(null_means, 95)), 3),
        "p_value": round(float(p_val), 5),
    }


def verdict_platinum(
    age_pt_onset_gicc05: float,
    d_d18o_init: Optional[float],
    d_d18o_step: Optional[float],
    d_ca_step: Optional[float],
) -> str:
    if age_pt_onset_gicc05 >= (GS1_ONSET_B2K - 10.0) and d_d18o_init is not None and PT_ONSET_M >= d_d18o_init:
        return "Consistent with trigger"
    deeper_in_gisp2 = (
        (d_d18o_step is not None and d_d18o_step > PT_ONSET_M)
        or (d_ca_step is not None and d_ca_step > PT_ONSET_M)
    )
    if age_pt_onset_gicc05 < (GS1_ONSET_B2K - 15.0) and deeper_in_gisp2:
        return "Post-dates cooling onset (cannot be the initial trigger)"
    return "Ambiguous / within uncertainty"


def verdict_volcanism(gl_top5: bool, bi_top5: bool) -> str:
    if gl_top5 and bi_top5:
        return "Unusually strong volcanic cluster"
    if gl_top5 or bi_top5:
        return "Elevated in one archive only"
    return "Ordinary background volcanism"


# ---------------------------------------------------------------------------
# Full pipeline
# ---------------------------------------------------------------------------
def run_pipeline(base_dir: pathlib.Path, decoy: bool = False) -> Dict[str, object]:
    noaa = base_dir / "data" / "noaa"
    cop = base_dir / "data" / "copernicus"
    pang = base_dir / "data" / "pangaea"

    ties = load_svensson2020_ties(cop / "svensson2020-supplement.zip")
    g3_d, g3_a, g3_o, g3_ca = load_g3_gisp2(noaa / "gicc05-calcium-20yr.txt")
    d2m_d, d2m_o = load_gispd18o_2m(noaa / "gispd18o.txt")
    ions = load_gisp2_ions(noaa / "iond.txt")
    gl_ev, bi_ev = load_lin2022(cop / "lin2022-supplement.zip")
    sigl = load_sigl2021(pang / "930557.tab")
    stadials = load_stadial_onsets_60ka(base_dir / "events.tsv")

    gl_ages = np.asarray([e["age_b2k"] for e in gl_ev], dtype=float)
    gl_deps = np.asarray([e["dep_kg_km2"] for e in gl_ev], dtype=float)
    bi_ages = np.asarray([float(e["age_b2k"]) for e in bi_ev], dtype=float)
    bi_loads = np.asarray([float(e["aerosol_tg"]) for e in bi_ev], dtype=float)

    if decoy:
        # Strictly exclude [12,600, 13,200] b2k (k in {-2,-1,0,1,2}) and GISP2 [1705, 1720] m
        drop_ks = (-2, -1, 0, 1, 2)
        rng = np.random.default_rng(76)
        # Pick decoy window outside gap and outside YD
        cand_ks = [k for k in range(-20, 200) if k not in drop_ks and not (16500 <= GS1_ONSET_B2K + 150 * k <= 24600)]
        target_k = int(rng.choice(cand_ks))
        v_gl = score_volcanic_windows(gl_ages, gl_deps, target_k=target_k, drop_ks=drop_ks)
        v_bi = score_volcanic_windows(bi_ages, bi_loads, gap=(16500.0, 24500.0), target_k=target_k, drop_ks=drop_ks)
        # Remove GS-1 from MC test in decoy mode
        non_yd = [float(e["age_b2k"]) for e in stadials if e["event"] != "GS-1"]
        mc50 = volcanic_cooling_mc(gl_ages, gl_deps, non_yd, pre_window=50.0, seed=76)
        mc150 = volcanic_cooling_mc(gl_ages, gl_deps, non_yd, pre_window=150.0, seed=76)
        # Test changepoint on a decoy GISP2 stadial (e.g., GS-3 around 2040-2070 m)
        tie_d = np.asarray([float(t["gisp2_depth_m"]) for t in ties], dtype=float)
        tie_a = np.asarray([float(t["gicc05_b2k"]) for t in ties], dtype=float)
        decoy_d = float(np.interp(27540.0, tie_a, tie_d))
        decoy_cp = step_changepoint(g3_d, g3_o, decoy_d - 15.0, decoy_d + 15.0, shallower_higher=False)
        return {
            "mode": "decoy",
            "target_k": target_k,
            "volc_verdict": verdict_volcanism(bool(v_gl["in_top5"]), bool(v_bi["in_top5"])),
            "VOLC_GL": {k: v for k, v in v_gl.items() if k != "all_windows"},
            "VOLC_BI": {k: v for k, v in v_bi.items() if k != "all_windows"},
            "mc_50yr_non_yd": mc50,
            "mc_150yr_non_yd": mc150,
            "decoy_gisp2_gs3_cp": decoy_cp,
        }

    # --- LOCKED MODE ---
    tie_d = np.asarray([float(t["gisp2_depth_m"]) for t in ties], dtype=float)
    tie_a = np.asarray([float(t["gicc05_b2k"]) for t in ties], dtype=float)

    # 1A: Synchronized GICC05 age of Pt onset, peak, end
    sven_onset, br_onset = interp_depth_to_age(tie_d, tie_a, PT_ONSET_M)
    sven_peak, _ = interp_depth_to_age(tie_d, tie_a, PT_PEAK_M)
    sven_end, _ = interp_depth_to_age(tie_d, tie_a, PT_END_M)

    g3_onset, _ = interp_depth_to_age(g3_d, g3_a, PT_ONSET_M)
    g3_peak, _ = interp_depth_to_age(g3_d, g3_a, PT_PEAK_M)
    g3_end, _ = interp_depth_to_age(g3_d, g3_a, PT_END_M)

    # 1B: Within-GISP2 depth stratigraphy [1700, 1730] m
    cp_d18o_20 = step_changepoint(g3_d, g3_o, 1700.0, 1730.0, shallower_higher=False)
    cp_d18o_2m = step_changepoint(d2m_d, d2m_o, 1700.0, 1730.0, shallower_higher=False)
    cp_ca = step_changepoint(ions["mid_m"], np.log(np.maximum(ions["ca"], 1e-6)), 1700.0, 1730.0, shallower_higher=True)
    cp_na = step_changepoint(ions["mid_m"], np.log(np.maximum(ions["na"], 1e-6)), 1700.0, 1730.0, shallower_higher=True)
    init_d18o = cooling_init_depth(g3_d, g3_o, base_lo=1717.0, base_hi=1725.0, search_lo=1700.0)

    # Local GISP2 SO4 spikes inside [1708, 1720] m exceeding median + 3*MAD over [1695, 1735] m
    bg_m = (ions["mid_m"] >= 1695.0) & (ions["mid_m"] <= 1735.0) & np.isfinite(ions["so4"])
    so4_med = float(np.median(ions["so4"][bg_m]))
    so4_mad = float(np.median(np.abs(ions["so4"][bg_m] - so4_med)))
    so4_thresh = so4_med + 3.0 * so4_mad
    loc_m = (ions["mid_m"] >= 1708.0) & (ions["mid_m"] <= 1720.0) & np.isfinite(ions["so4"])
    so4_spikes = []
    for i in np.where(loc_m)[0]:
        if float(ions["so4"][i]) > so4_thresh:
            d_mid = float(ions["mid_m"][i])
            a_sven, _ = interp_depth_to_age(tie_d, tie_a, d_mid)
            so4_spikes.append({
                "top_m": round(float(ions["top_m"][i]), 3),
                "bot_m": round(float(ions["bot_m"][i]), 3),
                "mid_m": round(d_mid, 3),
                "so4_ppb": round(float(ions["so4"][i]), 1),
                "ca_ppb": round(float(ions["ca"][i]), 1) if math.isfinite(ions["ca"][i]) else None,
                "nh4_ppb": round(float(ions["nh4"][i]), 1) if math.isfinite(ions["nh4"][i]) else None,
                "gicc05_b2k_interp": round(a_sven, 1),
            })

    v_pt = verdict_platinum(
        sven_onset,
        init_d18o["init_depth_m"] if init_d18o else None,
        cp_d18o_20["split_depth_m"] if cp_d18o_20 else None,
        cp_ca["split_depth_m"] if cp_ca else None,
    )

    # Part 2A: 51-kyr volcanic windows
    v_gl = score_volcanic_windows(gl_ages, gl_deps, a0=GS1_ONSET_B2K, width=150.0, target_k=0)
    v_bi = score_volcanic_windows(bi_ages, bi_loads, a0=GS1_ONSET_B2K, width=150.0, gap=(16500.0, 24500.0), target_k=0)
    v_gl_straddle = score_volcanic_windows(gl_ages, gl_deps, a0=GS1_ONSET_B2K - 100.0, width=150.0, target_k=0)
    v_bi_straddle = score_volcanic_windows(bi_ages, bi_loads, a0=GS1_ONSET_B2K - 100.0, width=150.0, gap=(16500.0, 24500.0), target_k=0)
    v_gl_300 = score_volcanic_windows(gl_ages, gl_deps, a0=GS1_ONSET_B2K - 150.0, width=300.0, target_k=0)
    v_bi_300 = score_volcanic_windows(bi_ages, bi_loads, a0=GS1_ONSET_B2K - 150.0, width=300.0, gap=(16500.0, 24500.0), target_k=0)

    v_volc = verdict_volcanism(bool(v_gl["in_top5"]), bool(v_bi["in_top5"]))

    # Part 2B: Monte Carlo across all 19 coolings (and 18 non-YD coolings)
    all_19 = [float(e["age_b2k"]) for e in stadials]
    non_yd_18 = [float(e["age_b2k"]) for e in stadials if e["event"] != "GS-1"]
    mc_all_50 = volcanic_cooling_mc(gl_ages, gl_deps, all_19, pre_window=50.0, seed=76)
    mc_all_150 = volcanic_cooling_mc(gl_ages, gl_deps, all_19, pre_window=150.0, seed=76)
    mc_non_50 = volcanic_cooling_mc(gl_ages, gl_deps, non_yd_18, pre_window=50.0, seed=76)
    mc_non_150 = volcanic_cooling_mc(gl_ages, gl_deps, non_yd_18, pre_window=150.0, seed=76)

    # Extract GISP2 depth profile [1705, 1723] m for transparent output & figures
    prof_d18o = [
        {"depth_m": round(float(d), 3), "gicc05_b2k": round(float(a), 1), "d18o": round(float(o), 3)}
        for d, a, o in zip(g3_d, g3_a, g3_o)
        if 1705.0 <= d <= 1723.0
    ]
    prof_ions = [
        {
            "mid_m": round(float(ions["mid_m"][i]), 3),
            "ca": round(float(ions["ca"][i]), 2) if math.isfinite(ions["ca"][i]) else None,
            "na": round(float(ions["na"][i]), 2) if math.isfinite(ions["na"][i]) else None,
            "nh4": round(float(ions["nh4"][i]), 2) if math.isfinite(ions["nh4"][i]) else None,
            "so4": round(float(ions["so4"][i]), 2) if math.isfinite(ions["so4"][i]) else None,
        }
        for i in range(len(ions["mid_m"]))
        if 1705.0 <= ions["mid_m"][i] <= 1723.0
    ]
    # Bipolar eruptions in [12,700, 13,200] b2k
    bi_yd = [e for e in bi_ev if 12700.0 <= float(e["age_b2k"]) <= 13200.0]
    gl_yd = [e for e in gl_ev if 12700.0 <= float(e["age_b2k"]) <= 13200.0]

    summary = {
        "mode": "locked",
        "verdicts": {
            "platinum_trigger": v_pt,
            "volcanic_cluster_51ka": v_volc,
        },
        "part1_platinum": {
            "published_depths_m": {"onset": PT_ONSET_M, "peak": PT_PEAK_M, "end": PT_END_M},
            "gs1_onset_b2k": GS1_ONSET_B2K,
            "svensson2020_gicc05": {
                "age_onset_b2k": round(sven_onset, 1),
                "age_peak_b2k": round(sven_peak, 1),
                "age_end_b2k": round(sven_end, 1),
                "lag_onset_yr_after_gs1": round(GS1_ONSET_B2K - sven_onset, 1),
                "lag_peak_yr_after_gs1": round(GS1_ONSET_B2K - sven_peak, 1),
                "bracketing_ties": br_onset,
            },
            "rasmussen2008_gicc05": {
                "age_onset_b2k": round(g3_onset, 1),
                "age_peak_b2k": round(g3_peak, 1),
                "age_end_b2k": round(g3_end, 1),
                "lag_onset_yr_after_gs1": round(GS1_ONSET_B2K - g3_onset, 1),
                "lag_peak_yr_after_gs1": round(GS1_ONSET_B2K - g3_peak, 1),
            },
            "gisp2_internal_stratigraphy": {
                "d_d18o_step_20yr": cp_d18o_20,
                "d_d18o_step_2m": cp_d18o_2m,
                "d_d18o_init_20yr": init_d18o,
                "d_ca_step": cp_ca,
                "d_na_step": cp_na,
                "so4_bg_median_ppb": round(so4_med, 1),
                "so4_bg_mad_ppb": round(so4_mad, 1),
                "so4_spike_thresh_ppb": round(so4_thresh, 1),
                "so4_spikes_1708_1720m": so4_spikes,
            },
        },
        "part2_volcanism": {
            "primary_150yr_pre_onset": {
                "VOLC_GL": {k: v for k, v in v_gl.items() if k != "all_windows"},
                "VOLC_BI": {k: v for k, v in v_bi.items() if k != "all_windows"},
            },
            "alongside_windows": {
                "straddle_150yr_GL": {k: v for k, v in v_gl_straddle.items() if k != "all_windows"},
                "straddle_150yr_BI": {k: v for k, v in v_bi_straddle.items() if k != "all_windows"},
                "wide_300yr_GL": {k: v for k, v in v_gl_300.items() if k != "all_windows"},
                "wide_300yr_BI": {k: v for k, v in v_bi_300.items() if k != "all_windows"},
            },
            "monte_carlo_coolings": {
                "all_19_50yr": mc_all_50,
                "all_19_150yr": mc_all_150,
                "non_yd_18_50yr": mc_non_50,
                "non_yd_18_150yr": mc_non_150,
            },
            "eruptions_around_yd_gl": gl_yd,
            "eruptions_around_yd_bi": bi_yd,
            "sigl2021_vssi_table": sigl,
        },
        "profiles_gisp2": {"d18o_20yr": prof_d18o, "ions": prof_ions},
    }

    out_dir = base_dir / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    with open(out_dir / "volc_windows_150yr_gl.tsv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["k", "start_b2k", "end_b2k", "dep_kg_km2", "count"])
        for row in v_gl["all_windows"]:
            w.writerow([row["k"], row["start_b2k"], row["end_b2k"], row["value"], row["count"]])

    with open(out_dir / "volc_windows_150yr_bi.tsv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["k", "start_b2k", "end_b2k", "aerosol_tg", "count"])
        for row in v_bi["all_windows"]:
            w.writerow([row["k"], row["start_b2k"], row["end_b2k"], row["value"], row["count"]])

    return summary


def _print_report(s: Dict[str, object]) -> None:
    if s["mode"] == "decoy":
        print(f"=== yd-platinum-volcanism (DECOY MODE) | decoy k={s['target_k']} ===")
        print(f"Volc verdict: {s['volc_verdict']}")
        print(f"  VOLC_GL: val={s['VOLC_GL']['value']} rank={s['VOLC_GL']['rank']}/{s['VOLC_GL']['n']} (top5<={s['VOLC_GL']['top5_cut']})")
        print(f"  VOLC_BI: val={s['VOLC_BI']['value']} rank={s['VOLC_BI']['rank']}/{s['VOLC_BI']['n']} (top5<={s['VOLC_BI']['top5_cut']})")
        print(f"  MC 50yr (18 non-YD):  obs={s['mc_50yr_non_yd']['obs_mean_dep']} vs null={s['mc_50yr_non_yd']['null_mean_dep']} p={s['mc_50yr_non_yd']['p_value']}")
        print(f"  MC 150yr (18 non-YD): obs={s['mc_150yr_non_yd']['obs_mean_dep']} vs null={s['mc_150yr_non_yd']['null_mean_dep']} p={s['mc_150yr_non_yd']['p_value']}")
        print(f"  Decoy GISP2 GS-3 d18O changepoint: {s['decoy_gisp2_gs3_cp']}")
        return

    v = s["verdicts"]
    p1 = s["part1_platinum"]
    p2 = s["part2_volcanism"]
    print("=== yd-platinum-volcanism (LOCKED MODE) ===")
    print(f"Verdict 1 (Platinum trigger):  {v['platinum_trigger']}")
    print(f"Verdict 2 (51-kyr volcanism):  {v['volcanic_cluster_51ka']}\n")
    sv = p1["svensson2020_gicc05"]
    r8 = p1["rasmussen2008_gicc05"]
    g = p1["gisp2_internal_stratigraphy"]
    print("--- Part 1: GISP2 Platinum (1712.375 - 1712.000 m, peak 1712.1875 m) ---")
    print(f"  Svensson 2020 GICC05: onset={sv['age_onset_b2k']} b2k (+{sv['lag_onset_yr_after_gs1']} yr AFTER GS-1), peak={sv['age_peak_b2k']} (+{sv['lag_peak_yr_after_gs1']} yr)")
    print(f"  Rasmussen 2008 GICC05: onset={r8['age_onset_b2k']} b2k (+{r8['lag_onset_yr_after_gs1']} yr AFTER GS-1), peak={r8['age_peak_b2k']} (+{r8['lag_peak_yr_after_gs1']} yr)")
    print(f"  GISP2 internal d18O step (20yr): {g['d_d18o_step_20yr']}")
    print(f"  GISP2 internal d18O step (2m):   {g['d_d18o_step_2m']}")
    print(f"  GISP2 internal d18O init (20yr): {g['d_d18o_init_20yr']}")
    print(f"  GISP2 internal Ca2+ step:        {g['d_ca_step']}")
    print(f"  GISP2 internal Na+ step:         {g['d_na_step']}")
    print(f"  GISP2 SO4 spikes (> {g['so4_spike_thresh_ppb']} ppb) in 1708-1720 m: {len(g['so4_spikes_1708_1720m'])}")
    for sp in g["so4_spikes_1708_1720m"]:
        print(f"    {sp['top_m']}-{sp['bot_m']} m (GICC05 ~{sp['gicc05_b2k_interp']} b2k): SO4={sp['so4_ppb']} ppb, Ca={sp['ca_ppb']}, NH4={sp['nh4_ppb']}")

    print("\n--- Part 2: 51,000-Year Volcanism (Lin et al. 2022, 60-9 ka) ---")
    gl = p2["primary_150yr_pre_onset"]["VOLC_GL"]
    bi = p2["primary_150yr_pre_onset"]["VOLC_BI"]
    print(f"  Pre-onset [12896,13046) VOLC_GL: {gl['value']} kg/km2 ({gl['count']} events) | rank={gl['rank']}/{gl['n']} (top5<={gl['top5_cut']}, met={gl['in_top5']}) | med={gl['median_all']}")
    print(f"  Pre-onset [12896,13046) VOLC_BI: {bi['value']} Tg ({bi['count']} events) | rank={bi['rank']}/{bi['n']} (top5<={bi['top5_cut']}, met={bi['in_top5']}) | med={bi['median_all']}")
    for k, r in p2["alongside_windows"].items():
        print(f"  {k:20s}: val={r['value']} ({r['count']} ev) | rank={r['rank']}/{r['n']} (top5={r['in_top5']})")
    print("\n--- Monte Carlo: Volcanic sulfate before abrupt coolings (10-60 ka) ---")
    for k, r in p2["monte_carlo_coolings"].items():
        print(f"  {k:16s}: obs={r['obs_mean_dep']} vs null={r['null_mean_dep']} (p95={r['null_p95_dep']}) | p={r['p_value']}")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Pre-registered analysis for yd-platinum-volcanism (Issue #76).")
    parser.add_argument("--decoy", action="store_true", help="Exclude YD target and run decoy verification.")
    parser.add_argument("--dir", type=pathlib.Path, default=pathlib.Path("."), help="Question folder (default: .)")
    args = parser.parse_args(argv)
    s = run_pipeline(args.dir.resolve(), decoy=args.decoy)
    _print_report(s)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
