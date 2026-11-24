#!/usr/bin/env python3
"""
ydb-site-synchrony (Issue #113)
-------------------------------
Reproducible IntCal20 radiocarbon calibration, forward-simulated single-year
plateau synchrony testing (with Laacher See Tephra real single-year positive
control), and precision / placebo-year overlap audit of claimed Younger Dryas
Boundary (YDB) sites.

Strictly adheres to questions/ydb-site-synchrony/protocol.md.
"""

from __future__ import annotations

import csv
import json
import math
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
from pypdf import PdfReader
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"

CAL_GRID_MIN = 10500
CAL_GRID_MAX = 15500
RNG_SEED = 20261124
N_SIM = 2000


@dataclass
class C14Date:
    site: str
    lab_id: str
    rcybp: float
    sigma: float
    material: str
    is_wood_or_charcoal: bool
    source: str
    note: str = ""


@dataclass
class KennettSite:
    site: str
    modeled_age: Optional[float]
    sigma_68: Optional[float]
    ci95_upper: Optional[float]
    ci95_lower: Optional[float]
    n_total: int
    n_rejected: int
    n_accepted: int
    quality: str  # High, Med, Low, Unmodeled
    direct_on_proxies: bool


# ---------------------------------------------------------------------------
# 1. IntCal20 loading and exact Bayesian calibration
# ---------------------------------------------------------------------------

def load_intcal20(path: Path) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Load intcal20.14c and interpolate onto a 1-yr grid [CAL_GRID_MIN, CAL_GRID_MAX]."""
    cal_bp: List[float] = []
    c14_age: List[float] = []
    c14_sig: List[float] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            parts = [p for p in re.split(r"[,\s]+", s) if p]
            if len(parts) < 3:
                continue
            cal_bp.append(float(parts[0]))
            c14_age.append(float(parts[1]))
            c14_sig.append(float(parts[2]))

    cal_arr = np.asarray(cal_bp, dtype=float)
    age_arr = np.asarray(c14_age, dtype=float)
    sig_arr = np.asarray(c14_sig, dtype=float)
    order = np.argsort(cal_arr)
    cal_arr, age_arr, sig_arr = cal_arr[order], age_arr[order], sig_arr[order]

    grid = np.arange(CAL_GRID_MIN, CAL_GRID_MAX + 1, 1.0, dtype=float)
    mu_grid = np.interp(grid, cal_arr, age_arr)
    sig_grid = np.interp(grid, cal_arr, sig_arr)
    return grid, mu_grid, sig_grid


def calibrate_single(
    rcybp: float,
    sigma: float,
    grid: np.ndarray,
    mu_c: np.ndarray,
    sig_c: np.ndarray,
) -> Dict[str, object]:
    """Exact 1-yr grid Bayesian calibration under a flat prior."""
    var = sigma * sigma + sig_c * sig_c
    logp = -0.5 * ((rcybp - mu_c) ** 2) / var - 0.5 * np.log(var)
    logp -= np.max(logp)
    p = np.exp(logp)
    p /= np.sum(p)

    cdf = np.cumsum(p)
    median = float(grid[np.searchsorted(cdf, 0.5)])
    mean = float(np.sum(grid * p))
    sd = float(math.sqrt(max(0.0, float(np.sum(((grid - mean) ** 2) * p)))))

    # Exact 95.4% HPD set (minimum-width subset with cumulative prob >= 0.954)
    idx_desc = np.argsort(p)[::-1]
    cum_hpd = np.cumsum(p[idx_desc])
    n_keep = int(np.searchsorted(cum_hpd, 0.954)) + 1
    hpd_mask = np.zeros_like(p, dtype=bool)
    hpd_mask[idx_desc[:n_keep]] = True
    hpd_years = grid[hpd_mask]
    hpd_min = float(np.min(hpd_years))
    hpd_max = float(np.max(hpd_years))

    # Extract contiguous HPD sub-intervals
    intervals: List[List[float]] = []
    in_seg = False
    seg_start = 0.0
    for j, flag in enumerate(hpd_mask):
        if flag and not in_seg:
            seg_start = float(grid[j])
            in_seg = True
        elif not flag and in_seg:
            intervals.append([seg_start, float(grid[j - 1])])
            in_seg = False
    if in_seg:
        intervals.append([seg_start, float(grid[-1])])

    return {
        "median": median,
        "mean": mean,
        "sd": sd,
        "hpd95_lower": hpd_min,
        "hpd95_upper": hpd_max,
        "hpd95_span": hpd_max - hpd_min,
        "hpd95_intervals": intervals,
        "hpd95_mask": hpd_mask,
        "pdf": p,
    }


def calibrate_batch_medians(
    rcybp_mat: np.ndarray,
    sigmas: np.ndarray,
    grid: np.ndarray,
    mu_c: np.ndarray,
    sig_c: np.ndarray,
    batch_size: int = 200,
) -> np.ndarray:
    """
    Exact 1-yr IntCal20 calibrated medians for shape (N_sim, n_dates).
    Because the calibrated median for a fixed sigma is a smooth 1D function of
    uncalibrated 14C age y, we evaluate the exact 1-yr IntCal20 grid posterior
    on a 1-14C-yr table spanning the simulated y range for each unique sigma
    and linearly interpolate (<0.2 cal yr discrepancy, >1000x speedup).
    """
    n_sim, n_dates = rcybp_mat.shape
    medians = np.empty((n_sim, n_dates), dtype=float)
    y_min = math.floor(float(np.min(rcybp_mat))) - 2
    y_max = math.ceil(float(np.max(rcybp_mat))) + 2
    y_tab = np.arange(y_min, y_max + 1, 1.0, dtype=float)
    n_y = len(y_tab)

    unique_sigs = np.unique(sigmas)
    sig_lookup: Dict[float, np.ndarray] = {}
    for s in unique_sigs:
        var = s * s + sig_c * sig_c
        inv_2var = 0.5 / var
        half_log_var = 0.5 * np.log(var)
        med_tab = np.empty(n_y, dtype=float)
        for st in range(0, n_y, batch_size):
            en = min(st + batch_size, n_y)
            diff = y_tab[st:en, None] - mu_c[None, :]
            logp = -(diff * diff) * inv_2var[None, :] - half_log_var[None, :]
            logp -= np.max(logp, axis=1, keepdims=True)
            p = np.exp(logp)
            p /= np.sum(p, axis=1, keepdims=True)
            cdf = np.cumsum(p, axis=1)
            med_tab[st:en] = grid[np.argmax(cdf >= 0.5, axis=1)]
        sig_lookup[float(s)] = med_tab

    for j in range(n_dates):
        medians[:, j] = np.interp(rcybp_mat[:, j], y_tab, sig_lookup[float(sigmas[j])])
    return medians


# ---------------------------------------------------------------------------
# 2. Statistical tests & forward-simulated single-year plateau benchmark
# ---------------------------------------------------------------------------

def ward_wilson_T(rcybp: np.ndarray, sigmas: np.ndarray) -> Tuple[float, float, float, float]:
    """Ward & Wilson (1978) pooled weighted mean, combined sigma, T statistic, and chi2 p-value."""
    w = 1.0 / (sigmas ** 2)
    w_sum = float(np.sum(w))
    y_bar = float(np.sum(w * rcybp) / w_sum)
    s_bar = float(1.0 / math.sqrt(w_sum))
    T = float(np.sum(w * ((rcybp - y_bar) ** 2)))
    df = len(rcybp) - 1
    p_chi2 = float(stats.chi2.sf(T, df)) if df > 0 else 1.0
    return y_bar, s_bar, T, p_chi2


def ward_wilson_T_batch(rcybp_mat: np.ndarray, sigmas: np.ndarray) -> np.ndarray:
    """Vectorized Ward & Wilson T for shape (N_sim, n_dates)."""
    w = 1.0 / (sigmas ** 2)
    w_sum = np.sum(w)
    y_bar = np.sum(rcybp_mat * w[None, :], axis=1, keepdims=True) / w_sum
    return np.sum(((rcybp_mat - y_bar) ** 2) * w[None, :], axis=1)


def run_synchrony_panel(
    name: str,
    dates: List[C14Date],
    grid: np.ndarray,
    mu_c: np.ndarray,
    sig_c: np.ndarray,
    t0_grid: List[int],
    n_sim: int = N_SIM,
    seed: int = RNG_SEED,
) -> Dict[str, object]:
    """Run Ward-Wilson T, IntCal20 calibration, simultaneous HPD overlap, and M0/M1 forward simulation."""
    rcybp = np.array([d.rcybp for d in dates], dtype=float)
    sigmas = np.array([d.sigma for d in dates], dtype=float)
    is_wood = np.array([1.0 if d.is_wood_or_charcoal else 0.0 for d in dates], dtype=float)
    n = len(dates)

    y_bar, s_bar, T_obs, p_chi2 = ward_wilson_T(rcybp, sigmas)

    cal_rows = []
    hpd_masks = []
    meds = []
    for d in dates:
        cal = calibrate_single(d.rcybp, d.sigma, grid, mu_c, sig_c)
        meds.append(cal["median"])
        hpd_masks.append(cal["hpd95_mask"])
        cal_rows.append({
            "site": d.site,
            "lab_id": d.lab_id,
            "rcybp": d.rcybp,
            "sigma": d.sigma,
            "material": d.material,
            "is_wood_or_charcoal": d.is_wood_or_charcoal,
            "source": d.source,
            "note": d.note,
            "cal_median": round(float(cal["median"]), 1),
            "cal_mean": round(float(cal["mean"]), 1),
            "cal_sd": round(float(cal["sd"]), 1),
            "hpd95_lower": round(float(cal["hpd95_lower"]), 1),
            "hpd95_upper": round(float(cal["hpd95_upper"]), 1),
            "hpd95_span": round(float(cal["hpd95_span"]), 1),
            "hpd95_intervals": cal["hpd95_intervals"],
        })

    meds_arr = np.array(meds, dtype=float)
    sd_cal_obs = float(np.std(meds_arr, ddof=1)) if n > 1 else 0.0
    iqr_cal_obs = float(np.percentile(meds_arr, 75) - np.percentile(meds_arr, 25)) if n > 1 else 0.0
    span_cal_obs = float(np.max(meds_arr) - np.min(meds_arr)) if n > 1 else 0.0

    # Maximum simultaneous 95.4% HPD overlap across 12,000-13,500 cal BP
    mask_stack = np.vstack(hpd_masks)  # (n, len(grid))
    win = (grid >= 12000) & (grid <= 13500)
    overlap_counts = np.sum(mask_stack[:, win], axis=0)
    best_idx = int(np.argmax(overlap_counts))
    max_hpd_overlap_n = int(overlap_counts[best_idx])
    best_overlap_years = grid[win][overlap_counts == max_hpd_overlap_n]
    best_overlap_range = [float(np.min(best_overlap_years)), float(np.max(best_overlap_years))]

    rng = np.random.default_rng(seed)

    def simulate_model(extra_lab_sd: float, old_wood_mean: float) -> Dict[str, object]:
        sweep = []
        best_p_T = -1.0
        best_p_SD = -1.0
        best_t0_T = t0_grid[0]
        best_t0_SD = t0_grid[0]
        best_sim_T_med = 0.0
        best_sim_SD_med = 0.0
        best_sim_T_q95 = 0.0
        best_sim_SD_q95 = 0.0

        for t0 in t0_grid:
            g_idx = int(t0 - CAL_GRID_MIN)
            mu0 = float(mu_c[g_idx])
            sc0 = float(sig_c[g_idx])
            tot_sd = np.sqrt(sigmas ** 2 + sc0 ** 2 + extra_lab_sd ** 2)
            y_sim = rng.normal(loc=mu0, scale=tot_sd[None, :], size=(n_sim, n))
            if old_wood_mean > 0.0:
                ow = rng.exponential(scale=old_wood_mean, size=(n_sim, n)) * is_wood[None, :]
                y_sim = y_sim + ow

            T_sim = ward_wilson_T_batch(y_sim, sigmas)
            med_sim = calibrate_batch_medians(y_sim, sigmas, grid, mu_c, sig_c)
            sd_sim = np.std(med_sim, axis=1, ddof=1)

            p_T = float((1 + np.sum(T_sim >= T_obs)) / (n_sim + 1))
            p_SD = float((1 + np.sum(sd_sim >= sd_cal_obs)) / (n_sim + 1))
            sweep.append({
                "t0_cal_bp": int(t0),
                "intcal20_rcybp": round(mu0, 1),
                "sim_T_median": round(float(np.median(T_sim)), 2),
                "sim_T_q95": round(float(np.quantile(T_sim, 0.95)), 2),
                "p_T": round(p_T, 5),
                "sim_SD_median": round(float(np.median(sd_sim)), 1),
                "sim_SD_q95": round(float(np.quantile(sd_sim, 0.95)), 1),
                "p_SD": round(p_SD, 5),
            })
            if p_T > best_p_T:
                best_p_T = p_T
                best_t0_T = int(t0)
                best_sim_T_med = float(np.median(T_sim))
                best_sim_T_q95 = float(np.quantile(T_sim, 0.95))
            if p_SD > best_p_SD:
                best_p_SD = p_SD
                best_t0_SD = int(t0)
                best_sim_SD_med = float(np.median(sd_sim))
                best_sim_SD_q95 = float(np.quantile(sd_sim, 0.95))

        return {
            "extra_lab_sd": extra_lab_sd,
            "old_wood_mean": old_wood_mean,
            "p_T_best": round(best_p_T, 5),
            "best_t0_for_T": best_t0_T,
            "sim_T_median_at_best": round(best_sim_T_med, 2),
            "sim_T_q95_at_best": round(best_sim_T_q95, 2),
            "p_SD_best": round(best_p_SD, 5),
            "best_t0_for_SD": best_t0_SD,
            "sim_SD_median_at_best": round(best_sim_SD_med, 1),
            "sim_SD_q95_at_best": round(best_sim_SD_q95, 1),
            "sweep": sweep,
        }

    m0 = simulate_model(extra_lab_sd=0.0, old_wood_mean=0.0)
    m1 = simulate_model(extra_lab_sd=20.0, old_wood_mean=50.0)

    return {
        "panel": name,
        "n_dates": n,
        "weighted_mean_rcybp": round(y_bar, 1),
        "weighted_mean_sigma": round(s_bar, 1),
        "ward_wilson_T": round(T_obs, 2),
        "ward_wilson_df": n - 1,
        "ward_wilson_p_chi2": float(p_chi2),
        "cal_median_mean": round(float(np.mean(meds_arr)), 1),
        "cal_median_sd": round(sd_cal_obs, 1),
        "cal_median_iqr": round(iqr_cal_obs, 1),
        "cal_median_span": round(span_cal_obs, 1),
        "max_hpd95_overlap_n": max_hpd_overlap_n,
        "max_hpd95_overlap_frac": round(max_hpd_overlap_n / n, 4),
        "max_hpd95_overlap_years": best_overlap_range,
        "M0": m0,
        "M1": m1,
        "dates": cal_rows,
    }


# ---------------------------------------------------------------------------
# 3. Primary data parsers (programmatic extraction from downloaded PDFs/CSVs)
# ---------------------------------------------------------------------------

def parse_reinig_lst(pdf_path: Path) -> List[C14Date]:
    """Parse Reinig et al. (2023) Nature Reply Extended Data Table 1 (p. 9)."""
    r = PdfReader(str(pdf_path))
    txt = r.pages[8].extract_text() or ""
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    out: List[C14Date] = []
    # Join wrapped site names like "Near Laacher\nSee monastery ..."
    joined: List[str] = []
    buf = ""
    for l in lines:
        if re.search(r"\d{5}\s*±\s*\d+", l):
            joined.append((buf + " " + l).strip())
            buf = ""
        elif l.startswith("Site ") or l.startswith("Laacher See") or l.isdigit():
            buf = ""
        else:
            buf = (buf + " " + l).strip()

    pat = re.compile(
        r"^(?P<site>.+?)\s+(?:~?\s*[\d.<]+\s*km\s*[NSEW]*)\s+(?P<rest>.+?)\s+"
        r"(?P<lab>(?:Hd|KN|ETH|UtC)-\d+\*?)\s+(?P<age>\d{5})\s*±\s*(?P<sig>\d+)"
    )
    for row in joined:
        m = pat.search(row)
        if not m:
            raise ValueError(f"Failed to parse Reinig LST row: {row}")
        site = re.sub(r"\s+", " ", m.group("site")).strip()
        lab = m.group("lab").rstrip("*")
        age = float(m.group("age"))
        sig = float(m.group("sig"))
        out.append(C14Date(
            site=site,
            lab_id=lab,
            rcybp=age,
            sigma=sig,
            material="wood/poplar/bark",
            is_wood_or_charcoal=True,
            source="Reinig et al. 2023 Nature Reply, Extended Data Table 1",
            note=m.group("rest").strip(),
        ))
    assert len(out) == 16, f"Expected 16 LST dates, parsed {len(out)}"
    return out


def parse_arlington_kennett2008(pdf_path: Path) -> List[C14Date]:
    """Parse Kennett et al. (2008) QSR Table 4 — 12 direct YDB (392-503 cm) AMS 14C dates."""
    r = PdfReader(str(pdf_path))
    txt = r.pages[8].extract_text() or ""
    out: List[C14Date] = []
    pat = re.compile(
        r"^(?P<lab>(?:UCIAMS|Beta)-\d+)\s+(?P<d1>\d+)[–-](?P<d2>\d+)\s+(?P<mid>.+?)\s+"
        r"(?P<age>1[012],\d{3})\s+(?P<sig>\d{2,3})\s+"
    )
    for line in txt.splitlines():
        m = pat.search(line.strip())
        if not m:
            continue
        d1 = int(m.group("d1"))
        d2 = int(m.group("d2"))
        # Kennett et al. (2015) defines the Arlington Canyon YDB horizon as 392-503 cmbs (12 dates)
        if d1 >= 392 and d2 <= 503:
            age = float(m.group("age").replace(",", ""))
            sig = float(m.group("sig"))
            out.append(C14Date(
                site="Arlington Canyon, CA",
                lab_id=m.group("lab"),
                rcybp=age,
                sigma=sig,
                material=m.group("mid").strip(),
                is_wood_or_charcoal=True,
                source="Kennett et al. 2008 QSR, Table 4",
                note=f"{d1}-{d2} cmbs",
            ))
    assert len(out) == 12, f"Expected 12 Arlington Canyon YDB dates (392-503 cmbs), parsed {len(out)}"
    return out


def parse_aalsterhut_vanhoesel2012(pdf_path: Path) -> List[C14Date]:
    """Parse van Hoesel et al. (2012) PNAS Table 1 — all 14 Aalsterhut AMS 14C dates."""
    r = PdfReader(str(pdf_path))
    txt = r.pages[1].extract_text() or ""
    out: List[C14Date] = []
    pat = re.compile(
        r"^(?P<sample>AH-\d+[a-z])\s+(?P<depth>[−\-0-9.–\- ]+?)\s+(?P<lab>GrA-\d+)\s+"
        r"(?P<age>1[01],\d{3})\s*±\s*(?P<sig>\d{2,3})"
    )
    for line in txt.splitlines():
        m = pat.search(line.strip())
        if not m:
            continue
        out.append(C14Date(
            site="Aalsterhut, Netherlands",
            lab_id=m.group("lab"),
            rcybp=float(m.group("age").replace(",", "")),
            sigma=float(m.group("sig")),
            material="charcoal (Usselo horizon)",
            is_wood_or_charcoal=True,
            source="van Hoesel et al. 2012 PNAS, Table 1",
            note=f"{m.group('sample')} ({m.group('depth').strip()} cm)",
        ))
    assert len(out) == 14, f"Expected 14 Aalsterhut dates, parsed {len(out)}"
    return out


def parse_abuhureyra_moore2020(pdf_path: Path) -> C14Date:
    """Parse Moore et al. (2020) Sci. Rep. SI Table S1 — Level 445 direct YDB date UCIAMS-105429."""
    r = PdfReader(str(pdf_path))
    txt = r.pages[30].extract_text() or ""
    m = re.search(r"445\s+2\s+E301\s+[\d.]+\s+405\s+(\d{5})\s+(\d{2,3})\s+\d+\s+\d+\s+(UCIAMS-\d+)", txt)
    assert m, "Failed to parse Abu Hureyra Level 445 UCIAMS-105429 from Moore et al. 2020 Table S1"
    return C14Date(
        site="Abu Hureyra, Syria",
        lab_id=m.group(3),
        rcybp=float(m.group(1)),
        sigma=float(m.group(2)),
        material="charcoal (Level 445 meltglass peak)",
        is_wood_or_charcoal=True,
        source="Moore et al. 2020 Sci. Rep. SI Table S1 (Bunch et al. 2012)",
        note="405 cmbs, Level 445",
    )


def parse_lakehind_csv(csv_path: Path) -> Dict[str, C14Date]:
    """Parse Lake Hind AMS 14C dates from Teller et al. (2019) Table 1 CSV."""
    rows: Dict[str, C14Date] = {}
    with csv_path.open("r", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            lid = row["labID"].strip()
            rows[lid] = C14Date(
                site="Lake Hind, Manitoba",
                lab_id=lid,
                rcybp=float(row["age"]),
                sigma=float(row["error"]),
                material="plant/charcoal (YDB horizon)",
                is_wood_or_charcoal=True,
                source="Teller et al. 2019 Q. Res. Table 1 (LakeHindDates.csv)",
                note=f"depth={row['depth']} cm",
            )
    assert "UCIAMS-29317" in rows and "PSUAMS-1572" in rows, "Missing key Lake Hind YDB lab IDs"
    return rows


def parse_waters2007_clovis(pdf_path: Path) -> Dict[str, C14Date]:
    """Parse Waters & Stafford (2007) Science Table 1 for Murray Springs, Sheriden Cave, Indian Creek, Blackwater Draw."""
    r = PdfReader(str(pdf_path))
    txt = r.pages[3].extract_text() or ""
    targets = {
        "Murray Springs, AZ": (r"Murray Springs,\s*AZ\s*\(n\s*=\s*8\)\s*(1[01],\d{3})\s*±\s*(\d+)", "Unit F1 Clovis hearth mean (n=8)"),
        "Sheriden Cave, OH": (r"Sheriden Cave,\s*OH\s*\(below artifacts,\s*n\s*=\s*2\)\s*(1[01],\d{3})\s*±\s*(\d+)", "Below Clovis/YDB artifacts (n=2)"),
        "Indian Creek, MT": (r"Indian Creek,\s*MT\s*\(n\s*=\s*1\)\s*(1[01],\d{3})\s*±\s*(\d+)", "Clovis-age horizon (n=1)"),
        "Blackwater Draw, NM": (r"Blackwater Draw,\s*NM\s*\(n\s*=\s*3\)\s*(1[01],\d{3})\s*±\s*(\d+)", "Clovis / basal black mat (n=3)"),
    }
    out: Dict[str, C14Date] = {}
    for site, (pat, note) in targets.items():
        m = re.search(pat, txt)
        assert m, f"Failed to parse {site} from Waters & Stafford 2007 Table 1"
        out[site] = C14Date(
            site=site,
            lab_id=f"WS2007-{site.split(',')[0].replace(' ', '')}",
            rcybp=float(m.group(1).replace(",", "")),
            sigma=float(m.group(2)),
            material="charcoal/bone (Clovis/YDB)",
            is_wood_or_charcoal=True,
            source="Waters & Stafford 2007 Science, Table 1",
            note=note,
        )
    return out


def parse_bullcreek_holliday2023(pdf_path: Path) -> C14Date:
    """Parse Bull Creek BC21 (298-307 cmbs) direct YDB 14C date from Holliday et al. (2023) Table 5 (Bement et al. 2014)."""
    r = PdfReader(str(pdf_path))
    txt = r.pages[29].extract_text() or ""
    m = re.search(r"BC21\s+298[–-]307\d*\s+100\s+100\s+1\.9\s+(1[01],\d{3})\s*±\s*(\d+)", txt)
    assert m, "Failed to parse Bull Creek BC21 from Holliday et al. 2023 Table 5"
    return C14Date(
        site="Bull Creek, OK",
        lab_id="Bement2014-BC21",
        rcybp=float(m.group(1).replace(",", "")),
        sigma=float(m.group(2)),
        material="soil organic carbon (nanodiamond peak)",
        is_wood_or_charcoal=True,
        source="Bement et al. 2014 PNAS (transcribed in Holliday et al. 2023 Table 5)",
        note="298-307 cmbs, BC21",
    )


def parse_kennett2015_fig2(pdf_path: Path) -> List[KennettSite]:
    """Parse all 32 YDB sites (23 modeled + 9 unmodeled) from Kennett et al. (2015) PNAS Fig. 2 (p. 3)."""
    r = PdfReader(str(pdf_path))
    txt = r.pages[2].extract_text() or ""
    lines = [l.strip() for l in txt.splitlines() if l.strip()]

    start_idx = next(i for i, l in enumerate(lines) if l.startswith("LOCATION AGE"))
    end_idx = next(i for i, l in enumerate(lines) if l.startswith("Fig. 2."))
    table_lines = lines[start_idx + 1 : end_idx]

    sites: List[KennettSite] = []
    # Modeled line regex:
    # e.g. "Abu Hureyra 12825 55 12935 12705 37 8 29 High ●●● ..."
    # or   "Lingen 12735 85 12910 12520 202HIgh● ..."
    mod_pat = re.compile(
        r"^(?P<site>[A-Za-z .]+?)\s+(?P<age>\d{5})\s+(?P<sig>\d{2,4})\s+"
        r"(?P<hi>\d{5})\s+(?P<lo>\d{4,5})\s+(?P<counts>[\d ]+?)\s*"
        r"(?P<qual>High|HIgh|Med|Low)\s*(?P<dots>[●· ]+)$"
    )
    unmod_pat = re.compile(
        r"^(?P<site>[A-Za-z .]+?)\s+[· ]*(?P<ntot>\d+)?[· ]*x\s*(?P<dots>[●· ]+)$"
    )

    for line in table_lines:
        m = mod_pat.match(line)
        if m:
            c_str = m.group("counts").strip()
            parts = c_str.split()
            if len(parts) == 3:
                n_tot, n_rej, n_acc = int(parts[0]), int(parts[1]), int(parts[2])
            elif len(parts) == 1 and len(parts[0]) == 3:
                # e.g. "202" -> 2, 0, 2; "523" -> 5, 2, 3
                n_tot, n_rej, n_acc = int(parts[0][0]), int(parts[0][1]), int(parts[0][2])
            else:
                raise ValueError(f"Ambiguous date counts '{c_str}' in line: {line}")
            assert n_tot == n_rej + n_acc, f"Date count mismatch in {line}: {n_tot} != {n_rej}+{n_acc}"
            qual_raw = m.group("qual").lower()
            qual = {"high": "High", "med": "Med", "low": "Low"}[qual_raw]
            first_sym = m.group("dots").replace(" ", "")[0]
            sites.append(KennettSite(
                site=m.group("site").strip(),
                modeled_age=float(m.group("age")),
                sigma_68=float(m.group("sig")),
                ci95_upper=float(m.group("hi")),
                ci95_lower=float(m.group("lo")),
                n_total=n_tot,
                n_rejected=n_rej,
                n_accepted=n_acc,
                quality=qual,
                direct_on_proxies=(first_sym == "●"),
            ))
            continue

        mu = unmod_pat.match(line)
        if mu:
            ntot = int(mu.group("ntot")) if mu.group("ntot") else 0
            first_sym = mu.group("dots").replace(" ", "")[0]
            sites.append(KennettSite(
                site=mu.group("site").strip(),
                modeled_age=None,
                sigma_68=None,
                ci95_upper=None,
                ci95_lower=None,
                n_total=ntot,
                n_rejected=0,
                n_accepted=0,
                quality="Unmodeled",
                direct_on_proxies=(first_sym == "●"),
            ))
            continue

        raise ValueError(f"Unparsed Kennett Fig. 2 line: {line}")

    modeled = [s for s in sites if s.quality != "Unmodeled"]
    unmodeled = [s for s in sites if s.quality == "Unmodeled"]
    assert len(modeled) == 23, f"Expected 23 modeled sites, parsed {len(modeled)}"
    assert len(unmodeled) == 9, f"Expected 9 unmodeled sites, parsed {len(unmodeled)}"
    return sites


# ---------------------------------------------------------------------------
# 4. Pillar 2: Precision & Placebo-Year Overlap Audit
# ---------------------------------------------------------------------------

def run_pillar2_audit(sites: List[KennettSite]) -> Dict[str, object]:
    """Compute precision inventory, outlier rejection audit, and placebo-year overlap curve."""
    modeled = [s for s in sites if s.quality != "Unmodeled"]
    unmodeled = [s for s in sites if s.quality == "Unmodeled"]

    widths = np.array([s.ci95_upper - s.ci95_lower for s in modeled], dtype=float)
    n_direct_all = sum(1 for s in sites if s.direct_on_proxies)
    n_direct_mod = sum(1 for s in modeled if s.direct_on_proxies)
    n_tight_direct = sum(
        1 for s in modeled if s.direct_on_proxies and (s.ci95_upper - s.ci95_lower) <= 300.0
    )
    n_gt_500 = int(np.sum(widths > 500.0))
    n_gt_1000 = int(np.sum(widths > 1000.0))
    n_gt_2000 = int(np.sum(widths > 2000.0))
    n_le_300 = int(np.sum(widths <= 300.0))

    total_dates = sum(s.n_total for s in modeled)
    total_rej = sum(s.n_rejected for s in modeled)
    total_acc = sum(s.n_accepted for s in modeled)

    tier_summary = {}
    for tier in ["High", "Med", "Low"]:
        sub = [s for s in modeled if s.quality == tier]
        sub_w = [s.ci95_upper - s.ci95_lower for s in sub]
        tier_summary[tier] = {
            "n_sites": len(sub),
            "n_direct": sum(1 for s in sub if s.direct_on_proxies),
            "median_ci95_width": round(float(np.median(sub_w)), 1),
            "mean_ci95_width": round(float(np.mean(sub_w)), 1),
            "max_ci95_width": round(float(np.max(sub_w)), 1),
            "total_dates": sum(s.n_total for s in sub),
            "rejected_dates": sum(s.n_rejected for s in sub),
            "rejection_pct": round(100.0 * sum(s.n_rejected for s in sub) / max(1, sum(s.n_total for s in sub)), 1),
        }

    # Placebo-year sweep across 14,000 down to 11,500 cal BP in 10-yr steps
    test_years = np.arange(11500, 14001, 10, dtype=float)
    curve = []
    fracs_all = []
    for T in test_years:
        c_all = sum(1 for s in modeled if s.ci95_lower <= T <= s.ci95_upper)
        c_high = sum(1 for s in modeled if s.quality == "High" and s.ci95_lower <= T <= s.ci95_upper)
        c_med = sum(1 for s in modeled if s.quality == "Med" and s.ci95_lower <= T <= s.ci95_upper)
        c_low = sum(1 for s in modeled if s.quality == "Low" and s.ci95_lower <= T <= s.ci95_upper)
        f_all = c_all / len(modeled)
        fracs_all.append(f_all)
        curve.append({
            "year_cal_bp": int(T),
            "n_all": c_all,
            "frac_all": round(f_all, 4),
            "n_high": c_high,
            "frac_high": round(c_high / 9.0, 4),
            "n_med": c_med,
            "frac_med": round(c_med / 8.0, 4),
            "n_low": c_low,
            "frac_low": round(c_low / 6.0, 4),
        })

    fracs_arr = np.array(fracs_all)
    def specificity_window(thresh: float) -> Dict[str, object]:
        hits = test_years[fracs_arr >= thresh]
        if len(hits) == 0:
            return {"width_yr": 0.0, "min_bp": None, "max_bp": None}
        return {
            "width_yr": float(np.max(hits) - np.min(hits)),
            "min_bp": float(np.min(hits)),
            "max_bp": float(np.max(hits)),
        }

    w50 = specificity_window(0.50)
    w80 = specificity_window(0.80)
    w90 = specificity_window(0.90)

    # Specific placebo checkpoints
    by_yr = {row["year_cal_bp"]: row for row in curve}
    checkpoints = {}
    for yr in [13800, 13300, 13050, 12850, 12800, 12550, 12300, 11800]:
        checkpoints[str(yr)] = by_yr[yr]

    return {
        "n_total_sites": len(sites),
        "n_modeled_sites": len(modeled),
        "n_unmodeled_sites": len(unmodeled),
        "n_direct_on_proxies_all": n_direct_all,
        "n_direct_on_proxies_modeled": n_direct_mod,
        "n_tight_direct_le300": n_tight_direct,
        "frac_tight_direct_of_32": round(n_tight_direct / len(sites), 4),
        "ci95_width_median": round(float(np.median(widths)), 1),
        "ci95_width_mean": round(float(np.mean(widths)), 1),
        "ci95_width_min": round(float(np.min(widths)), 1),
        "ci95_width_max": round(float(np.max(widths)), 1),
        "n_width_le_300": n_le_300,
        "n_width_gt_500": n_gt_500,
        "n_width_gt_1000": n_gt_1000,
        "n_width_gt_2000": n_gt_2000,
        "total_dates_modeled_sites": total_dates,
        "total_dates_accepted": total_acc,
        "total_dates_rejected": total_rej,
        "overall_rejection_pct": round(100.0 * total_rej / total_dates, 1),
        "tier_summary": tier_summary,
        "W_50": w50,
        "W_80": w80,
        "W_90": w90,
        "placebo_checkpoints": checkpoints,
        "placebo_curve": curve,
        "sites": [
            {
                **asdict(s),
                "ci95_width": round(s.ci95_upper - s.ci95_lower, 1) if s.ci95_upper is not None else None,
            }
            for s in sites
        ],
    }


# ---------------------------------------------------------------------------
# 5. Pre-registered verdict evaluator
# ---------------------------------------------------------------------------

def evaluate_verdict(
    lst_site_res: Dict[str, object],
    p1_primary: Dict[str, object],
    p1_favorable: Dict[str, object],
    p2: Dict[str, object],
) -> Dict[str, object]:
    """Strictly evaluate the four mutually exclusive verdicts locked in protocol.md §4."""
    lst_pass = (lst_site_res["M1"]["p_T_best"] >= 0.05) and (lst_site_res["M1"]["p_SD_best"] >= 0.05)

    if not lst_pass:
        return {
            "verdict": "ambiguous_or_mixed",
            "reason": "Laacher See Tephra positive control failed M1; test over-rejects real single-year events.",
            "lst_positive_control_pass": False,
        }

    # Verdict 1: synchronous_single_event
    v1 = (
        p1_primary["M0"]["p_T_best"] >= 0.05
        and p1_primary["M0"]["p_SD_best"] >= 0.05
        and p1_primary["max_hpd95_overlap_n"] >= 7
        and p2["W_80"]["width_yr"] <= 400.0
    )
    if v1:
        return {
            "verdict": "synchronous_single_event",
            "reason": "Primary direct-14C YDB panel passes M0 synchrony and Pillar 2 shows tight specificity (W_80 <= 400 yr).",
            "lst_positive_control_pass": True,
        }

    # Verdict 2: asynchronous_diachronous_scatter
    v2 = (
        p1_primary["M1"]["p_T_best"] < 0.01
        and p1_primary["M1"]["p_SD_best"] < 0.01
        and p1_favorable["M1"]["p_T_best"] < 0.01
        and p1_favorable["M1"]["p_SD_best"] < 0.01
    )
    if v2:
        return {
            "verdict": "asynchronous_diachronous_scatter",
            "reason": "Both primary and YDIH-favorable direct-14C panels reject single-year synchrony even under M1 (inter-lab + old wood), while LST positive control passes.",
            "lst_positive_control_pass": True,
        }

    # Verdict 3: underconstrained_not_synchronous
    v3_p1 = (p1_primary["M0"]["p_T_best"] < 0.01) or (p1_primary["M0"]["p_SD_best"] < 0.01)
    v3_p2 = (p2["W_50"]["width_yr"] >= 1000.0) and (p2["frac_tight_direct_of_32"] < 0.25)
    if v3_p1 and v3_p2:
        return {
            "verdict": "underconstrained_not_synchronous",
            "reason": "Primary direct-14C panel rejects strict single-year synchrony under M0, and Pillar 2 confirms an uncertainty-width overlap illusion (W_50 >= 1000 yr, <25% tightly directly dated).",
            "lst_positive_control_pass": True,
        }

    return {
        "verdict": "ambiguous_or_mixed",
        "reason": "Results split across pre-registered thresholds without meeting a clean positive or negative criterion.",
        "lst_positive_control_pass": True,
    }


def collapse_by_site(dates: List[C14Date], label_suffix: str) -> List[C14Date]:
    """Inverse-variance weighted mean per site."""
    by_site: Dict[str, List[C14Date]] = {}
    for d in dates:
        by_site.setdefault(d.site, []).append(d)
    out: List[C14Date] = []
    for site, grp in by_site.items():
        y = np.array([g.rcybp for g in grp], dtype=float)
        s = np.array([g.sigma for g in grp], dtype=float)
        ym, sm, _, _ = ward_wilson_T(y, s)
        out.append(C14Date(
            site=site,
            lab_id=f"{site.split(',')[0].replace(' ', '')}_mean_n{len(grp)}",
            rcybp=round(ym, 1),
            sigma=round(sm, 1),
            material=grp[0].material,
            is_wood_or_charcoal=any(g.is_wood_or_charcoal for g in grp),
            source=grp[0].source,
            note=f"{label_suffix} (n={len(grp)})",
        ))
    return out


# ---------------------------------------------------------------------------
# 6. Main execution
# ---------------------------------------------------------------------------

def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    grid, mu_c, sig_c = load_intcal20(DATA_DIR / "intcal20.14c")

    # Positive Control: Laacher See Tephra (Reinig et al. 2023 Extended Data Table 1)
    lst_all = parse_reinig_lst(DATA_DIR / "reinig_lst_edtable1.pdf")
    lst_by_site = collapse_by_site(lst_all, "weighted locality mean")
    lst_t0 = list(range(12950, 13101, 25))
    lst_all_res = run_synchrony_panel("LST_all_16", lst_all, grid, mu_c, sig_c, lst_t0, seed=RNG_SEED + 1)
    lst_site_res = run_synchrony_panel("LST_sites_5", lst_by_site, grid, mu_c, sig_c, lst_t0, seed=RNG_SEED + 2)

    # Pillar 1: Primary raw direct-YDB 14C dates across 9 Northern Hemisphere sites
    arl_all = parse_arlington_kennett2008(DATA_DIR / "kennett2008_arlington.pdf")
    aal_all = parse_aalsterhut_vanhoesel2012(DATA_DIR / "vanhoesel2012.pdf")
    abu = parse_abuhureyra_moore2020(DATA_DIR / "moore2020_abuhureyra_sm.pdf")
    lh_dict = parse_lakehind_csv(DATA_DIR / "lakehind_dates.csv")
    ws_dict = parse_waters2007_clovis(DATA_DIR / "waters2007_clovis.pdf")
    bc = parse_bullcreek_holliday2023(DATA_DIR / "holliday2023_esr.pdf")

    # Arlington Canyon site summaries
    arl_y = np.array([d.rcybp for d in arl_all])
    arl_s = np.array([d.sigma for d in arl_all])
    arl_ym, arl_sm, _, _ = ward_wilson_T(arl_y, arl_s)
    arl_mean = C14Date(
        site="Arlington Canyon, CA",
        lab_id="AC003_YDB_mean_n12",
        rcybp=round(arl_ym, 1),
        sigma=round(arl_sm, 1),
        material="wood/charcoal (392-503 cmbs)",
        is_wood_or_charcoal=True,
        source="Kennett et al. 2008 QSR, Table 4",
        note="Inverse-variance mean of 12 YDB dates",
    )
    arl_youngest = min(arl_all, key=lambda d: d.rcybp)  # Beta-161032: 10860 ± 70

    # Aalsterhut site summaries
    aal_y = np.array([d.rcybp for d in aal_all])
    aal_s = np.array([d.sigma for d in aal_all])
    aal_ym, aal_sm, _, _ = ward_wilson_T(aal_y, aal_s)
    aal_mean = C14Date(
        site="Aalsterhut, Netherlands",
        lab_id="Usselo_mean_n14",
        rcybp=round(aal_ym, 1),
        sigma=round(aal_sm, 1),
        material="charcoal (Usselo horizon)",
        is_wood_or_charcoal=True,
        source="van Hoesel et al. 2012 PNAS, Table 1",
        note="Inverse-variance mean of 14 Usselo charcoal dates",
    )
    # Kennett et al. (2015) isolated the 3 deepest (4.0-5.5 cm) nanodiamond-bearing dates
    aal_bottom3 = [d for d in aal_all if d.lab_id in {"GrA-49515", "GrA-49509", "GrA-49524"}]
    assert len(aal_bottom3) == 3
    ab3_ym, ab3_sm, _, _ = ward_wilson_T(
        np.array([d.rcybp for d in aal_bottom3]),
        np.array([d.sigma for d in aal_bottom3]),
    )
    aal_fav = C14Date(
        site="Aalsterhut, Netherlands",
        lab_id="Usselo_basal_mean_n3",
        rcybp=round(ab3_ym, 1),
        sigma=round(ab3_sm, 1),
        material="charcoal (basal 4.0-5.5 cm ND layer)",
        is_wood_or_charcoal=True,
        source="van Hoesel et al. 2012 Table 1 (Kennett 2015 subset)",
        note="Inverse-variance mean of GrA-49515, GrA-49509, GrA-49524",
    )

    panel_1a_primary = [
        abu,
        arl_mean,
        aal_mean,
        lh_dict["UCIAMS-29317"],
        bc,
        ws_dict["Murray Springs, AZ"],
        ws_dict["Sheriden Cave, OH"],
        ws_dict["Indian Creek, MT"],
        ws_dict["Blackwater Draw, NM"],
    ]

    panel_1a_favorable = [
        abu,
        arl_youngest,
        aal_fav,
        lh_dict["PSUAMS-1572"],
        bc,
        ws_dict["Murray Springs, AZ"],
        ws_dict["Sheriden Cave, OH"],
        ws_dict["Indian Creek, MT"],
        ws_dict["Blackwater Draw, NM"],
    ]

    panel_1b_allraw = (
        [abu]
        + arl_all
        + aal_all
        + [lh_dict["UCIAMS-29317"], bc]
        + [
            ws_dict["Murray Springs, AZ"],
            ws_dict["Sheriden Cave, OH"],
            ws_dict["Indian Creek, MT"],
            ws_dict["Blackwater Draw, NM"],
        ]
    )
    assert len(panel_1b_allraw) == 33, f"Expected 33 raw direct dates (1+12+14+1+1+4), got {len(panel_1b_allraw)}"

    ydb_t0 = list(range(12700, 12951, 25))
    p1_primary_res = run_synchrony_panel("YDB_1A_Primary_9sites", panel_1a_primary, grid, mu_c, sig_c, ydb_t0, seed=RNG_SEED + 10)
    p1_favorable_res = run_synchrony_panel("YDB_1A_Favorable_9sites", panel_1a_favorable, grid, mu_c, sig_c, ydb_t0, seed=RNG_SEED + 11)
    p1_allraw_res = run_synchrony_panel("YDB_1B_AllRaw_33dates", panel_1b_allraw, grid, mu_c, sig_c, ydb_t0, seed=RNG_SEED + 12)

    # Pillar 2: Kennett et al. (2015) Fig. 2 precision & placebo-year overlap audit
    k_sites = parse_kennett2015_fig2(DATA_DIR / "kennett2015_main.pdf")
    p2_res = run_pillar2_audit(k_sites)

    # Pre-registered verdict
    verdict_info = evaluate_verdict(lst_site_res, p1_primary_res, p1_favorable_res, p2_res)

    summary = {
        "question": "ydb-site-synchrony",
        "issue": 113,
        "verdict": verdict_info["verdict"],
        "verdict_reason": verdict_info["reason"],
        "lst_positive_control_pass": verdict_info["lst_positive_control_pass"],
        "positive_control_lst_sites5": lst_site_res,
        "positive_control_lst_all16": lst_all_res,
        "pillar1_primary_9sites": p1_primary_res,
        "pillar1_favorable_9sites": p1_favorable_res,
        "pillar1_allraw_33dates": p1_allraw_res,
        "pillar2_kennett32_audit": p2_res,
    }

    (RESULTS_DIR / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    # Save tidy CSV tables
    with (RESULTS_DIR / "pillar1_dates.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["panel", "site", "lab_id", "rcybp", "sigma", "cal_median", "hpd95_lower", "hpd95_upper", "hpd95_span", "source"])
        for pname, pres in [
            ("LST_sites5", lst_site_res),
            ("YDB_Primary", p1_primary_res),
            ("YDB_Favorable", p1_favorable_res),
            ("YDB_AllRaw", p1_allraw_res),
        ]:
            for row in pres["dates"]:
                w.writerow([pname, row["site"], row["lab_id"], row["rcybp"], row["sigma"],
                            row["cal_median"], row["hpd95_lower"], row["hpd95_upper"], row["hpd95_span"], row["source"]])

    with (RESULTS_DIR / "pillar2_sites.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["site", "quality", "direct_on_proxies", "modeled_age", "sigma_68", "ci95_lower", "ci95_upper", "ci95_width", "n_total", "n_rejected", "n_accepted"])
        for s in p2_res["sites"]:
            w.writerow([s["site"], s["quality"], s["direct_on_proxies"], s["modeled_age"], s["sigma_68"],
                        s["ci95_lower"], s["ci95_upper"], s["ci95_width"], s["n_total"], s["n_rejected"], s["n_accepted"]])

    with (RESULTS_DIR / "placebo_curve.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["year_cal_bp", "n_all", "frac_all", "n_high", "frac_high", "n_med", "frac_med", "n_low", "frac_low"])
        for r in p2_res["placebo_curve"]:
            w.writerow([r["year_cal_bp"], r["n_all"], r["frac_all"], r["n_high"], r["frac_high"],
                        r["n_med"], r["frac_med"], r["n_low"], r["frac_low"]])

    print(f"VERDICT: {verdict_info['verdict']}")
    print(f"Reason:  {verdict_info['reason']}")
    print(f"LST (5 sites):  T={lst_site_res['ward_wilson_T']} (p_M0={lst_site_res['M0']['p_T_best']}, p_M1={lst_site_res['M1']['p_T_best']}), SD_cal={lst_site_res['cal_median_sd']} (p_M0={lst_site_res['M0']['p_SD_best']}, p_M1={lst_site_res['M1']['p_SD_best']})")
    print(f"LST (16 dates): T={lst_all_res['ward_wilson_T']} (p_M0={lst_all_res['M0']['p_T_best']}, p_M1={lst_all_res['M1']['p_T_best']}), SD_cal={lst_all_res['cal_median_sd']} (p_M0={lst_all_res['M0']['p_SD_best']}, p_M1={lst_all_res['M1']['p_SD_best']})")
    print(f"YDB Primary (9):   T={p1_primary_res['ward_wilson_T']} (p_M0={p1_primary_res['M0']['p_T_best']}, p_M1={p1_primary_res['M1']['p_T_best']}), SD_cal={p1_primary_res['cal_median_sd']} (p_M0={p1_primary_res['M0']['p_SD_best']}, p_M1={p1_primary_res['M1']['p_SD_best']}), HPD overlap={p1_primary_res['max_hpd95_overlap_n']}/9")
    print(f"YDB Favorable (9): T={p1_favorable_res['ward_wilson_T']} (p_M0={p1_favorable_res['M0']['p_T_best']}, p_M1={p1_favorable_res['M1']['p_T_best']}), SD_cal={p1_favorable_res['cal_median_sd']} (p_M0={p1_favorable_res['M0']['p_SD_best']}, p_M1={p1_favorable_res['M1']['p_SD_best']}), HPD overlap={p1_favorable_res['max_hpd95_overlap_n']}/9")
    print(f"YDB AllRaw (33):   T={p1_allraw_res['ward_wilson_T']} (p_M0={p1_allraw_res['M0']['p_T_best']}, p_M1={p1_allraw_res['M1']['p_T_best']}), SD_cal={p1_allraw_res['cal_median_sd']} (p_M0={p1_allraw_res['M0']['p_SD_best']}, p_M1={p1_allraw_res['M1']['p_SD_best']}), HPD overlap={p1_allraw_res['max_hpd95_overlap_n']}/33")
    print(f"Pillar 2 (32 sites): modeled={p2_res['n_modeled_sites']}, direct={p2_res['n_direct_on_proxies_all']}, tight_direct(<=300yr)={p2_res['n_tight_direct_le300']}/32 ({100*p2_res['frac_tight_direct_of_32']:.1f}%), W_50={p2_res['W_50']['width_yr']} yr, W_80={p2_res['W_80']['width_yr']} yr")


if __name__ == "__main__":
    main()
