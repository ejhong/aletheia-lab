#!/usr/bin/env python3
"""Pre-registered dual-archive test of the Taurid Comet Resonant Swarm hypothesis.

Archive A: NASA/JPL Small-Body Database (43,156 NEAs)
  - Test A1: Napier (2010) orbital box longitude-of-perihelion alignment toward 2P/Encke
    (varpi_E = 161.29 deg), tested against uniform circle AND adjacent Jupiter secular
    controls (Ctrl_LowE: 0.40<=e<0.63; Ctrl_HighI: 14<i<=35 deg).
  - Test A2: 7:2 Jupiter mean-motion resonance excess (2.21<=a<=2.30 AU) inside the
    Taurid-aligned corridor (|d_varpi|<=45 deg) vs. anti-Taurid and secular control.

Archive B: NASA/JPL CNEOS Fireball & Bolide Catalog (1994-2025, 32 complete years)
  - Test B1: Calendar seasonality during Autumn Taurids (Oct 15-Nov 30) and
    Daytime Beta-Taurids (Jun 10-Jul 10) for total bolides, >=1 kt bolides, and energy.
  - Test B2: 7:2 Resonant Swarm return years (1998, 2005, 2015, 2018, 2022, 2025)
    vs. 26 non-swarm years using sensor-drift-immune within-year Autumn shares.

Usage:
  python3 analysis/taurid.py --decoy   # Blind pre-lock test on synthetic/shuffled sky
  python3 analysis/taurid.py           # Post-lock full analysis -> results/
"""
from __future__ import annotations

import argparse
import datetime
import json
import math
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"

SEED = 20261123
N_PERM = 10000

NEA_CLASSES = {"AMO", "APO", "ATE", "IEO"}
SWARM_YEARS_6 = {1998, 2005, 2015, 2018, 2022, 2025}
SWARM_YEARS_4 = {1998, 2005, 2015, 2022}

AUTUMN_DAYS = 47.0   # Oct 15 - Nov 30 inclusive
DAYTIME_DAYS = 31.0  # Jun 10 - Jul 10 inclusive
YEAR_DAYS = 365.25


def ang_diff_deg(a_deg: np.ndarray, ref_deg: float) -> np.ndarray:
    """Signed angular difference in [-180, 180) degrees."""
    return ((a_deg - ref_deg + 180.0) % 360.0) - 180.0


def exact_binom_sf(k: int, n: int, p: float) -> float:
    """Exact one-sided upper tail P(X >= k) for X ~ Binomial(n, p)."""
    if k <= 0:
        return 1.0
    if k > n:
        return 0.0
    # Compute stably via log-gamma
    total = 0.0
    lp = math.log(p)
    lq = math.log(1.0 - p)
    ln_n_fac = math.lgamma(n + 1)
    for j in range(k, n + 1):
        log_pmf = ln_n_fac - math.lgamma(j + 1) - math.lgamma(n - j + 1) + j * lp + (n - j) * lq
        total += math.exp(log_pmf)
    return min(1.0, total)


def circular_v_test(varpi_deg: np.ndarray, ref_deg: float, n_mc: int = N_PERM, seed: int = SEED) -> Dict:
    """Encke-directed circular V-test with exact Monte Carlo uniform p-value."""
    n = len(varpi_deg)
    if n == 0:
        return {"n": 0, "c_bar": 0.0, "u": 0.0, "f_45": 0.0, "mean_abs_diff": 90.0, "p_unif": 1.0, "circ_mean": None}
    diff = ang_diff_deg(varpi_deg, ref_deg)
    cos_d = np.cos(np.deg2rad(diff))
    c_bar = float(np.mean(cos_d))
    u_obs = math.sqrt(2.0 * n) * c_bar
    f_45 = float(np.mean(np.abs(diff) <= 45.0))
    mean_abs = float(np.mean(np.abs(diff)))

    # Circular mean direction
    rad = np.deg2rad(varpi_deg)
    s_mean = float(np.mean(np.sin(rad)))
    c_mean = float(np.mean(np.cos(rad)))
    circ_mean = math.degrees(math.atan2(s_mean, c_mean)) % 360.0
    r_bar = math.hypot(s_mean, c_mean)

    rng = np.random.default_rng(seed)
    rand_ang = rng.uniform(0.0, 2.0 * math.pi, size=(n_mc, n))
    c_sim = np.mean(np.cos(rand_ang), axis=1)
    p_unif = float((1 + np.sum(c_sim >= c_bar)) / (n_mc + 1))

    return {
        "n": int(n),
        "c_bar": round(c_bar, 5),
        "u": round(u_obs, 4),
        "r_bar": round(r_bar, 5),
        "circ_mean_deg": round(circ_mean, 2),
        "f_45": round(f_45, 4),
        "n_45": int(np.sum(np.abs(diff) <= 45.0)),
        "mean_abs_diff_deg": round(mean_abs, 2),
        "p_unif": round(p_unif, 6),
    }


def perm_diff_mean(x: np.ndarray, y: np.ndarray, n_perm: int = N_PERM, seed: int = SEED) -> Tuple[float, float]:
    """One-sided permutation test for mean(x) - mean(y) > 0."""
    nx, ny = len(x), len(y)
    if nx == 0 or ny == 0:
        return 0.0, 1.0
    obs = float(np.mean(x) - np.mean(y))
    pooled = np.concatenate([x, y]).astype(np.float64)
    total = float(np.sum(pooled))
    rng = np.random.default_rng(seed)
    # Vectorized sampling without replacement via argsort of random keys in chunks
    ge = 0
    chunk = 1000
    done = 0
    while done < n_perm:
        m = min(chunk, n_perm - done)
        idx = np.argpartition(rng.random((m, nx + ny)), nx, axis=1)[:, :nx]
        sx = np.sum(pooled[idx], axis=1)
        diff_sim = sx / nx - (total - sx) / ny
        ge += int(np.sum(diff_sim >= obs - 1e-12))
        done += m
    return obs, float((1 + ge) / (n_perm + 1))


def load_neos() -> Tuple[Dict[str, np.ndarray], Dict[str, float]]:
    encke_raw = json.loads((DATA_DIR / "jpl_encke.json").read_text(encoding="utf-8"))
    ef = {k: i for i, k in enumerate(encke_raw["fields"])}
    er = encke_raw["data"][0]
    encke = {
        "a": float(er[ef["a"]]),
        "e": float(er[ef["e"]]),
        "i": float(er[ef["i"]]),
        "om": float(er[ef["om"]]),
        "w": float(er[ef["w"]]),
        "q": float(er[ef["q"]]),
        "ad": float(er[ef["ad"]]),
        "diameter": float(er[ef["diameter"]]),
        "albedo": float(er[ef["albedo"]]),
    }
    encke["varpi"] = (encke["om"] + encke["w"]) % 360.0

    raw = json.loads((DATA_DIR / "jpl_neos.json").read_text(encoding="utf-8"))
    fi = {k: i for i, k in enumerate(raw["fields"])}

    pdes, names, cls = [], [], []
    a, e, inc, om, w, ma, q, H, diam, alb, moid = [], [], [], [], [], [], [], [], [], [], []
    for r in raw["data"]:
        c = r[fi["class"]]
        if c not in NEA_CLASSES:
            continue
        vals = [r[fi[k]] for k in ("a", "e", "i", "om", "w", "H")]
        if any(v is None for v in vals):
            continue
        a.append(float(vals[0]))
        e.append(float(vals[1]))
        inc.append(float(vals[2]))
        om.append(float(vals[3]))
        w.append(float(vals[4]))
        H.append(float(vals[5]))
        ma.append(float(r[fi["ma"]]) if r[fi["ma"]] is not None else 0.0)
        q.append(float(r[fi["q"]]) if r[fi["q"]] is not None else float(vals[0]) * (1.0 - float(vals[1])))
        diam.append(float(r[fi["diameter"]]) if r[fi["diameter"]] is not None else float("nan"))
        alb.append(float(r[fi["albedo"]]) if r[fi["albedo"]] is not None else float("nan"))
        moid.append(float(r[fi["moid"]]) if r[fi["moid"]] is not None else float("nan"))
        pdes.append(str(r[fi["pdes"]]).strip())
        names.append(str(r[fi["full_name"]]).strip())
        cls.append(str(c))

    om_arr = np.array(om, dtype=np.float64)
    w_arr = np.array(w, dtype=np.float64)
    varpi = (om_arr + w_arr) % 360.0
    H_arr = np.array(H, dtype=np.float64)
    # Approximate diameter (km) at dark cometary albedo p_V=0.05 and stony p_V=0.14
    d_dark = (1329.0 / math.sqrt(0.05)) * np.power(10.0, -H_arr / 5.0)
    d_stony = (1329.0 / math.sqrt(0.14)) * np.power(10.0, -H_arr / 5.0)

    cat = {
        "pdes": np.array(pdes, dtype=object),
        "name": np.array(names, dtype=object),
        "cls": np.array(cls, dtype=object),
        "a": np.array(a, dtype=np.float64),
        "e": np.array(e, dtype=np.float64),
        "i": np.array(inc, dtype=np.float64),
        "om": om_arr,
        "w": w_arr,
        "ma": np.array(ma, dtype=np.float64),
        "q": np.array(q, dtype=np.float64),
        "H": H_arr,
        "diam": np.array(diam, dtype=np.float64),
        "albedo": np.array(alb, dtype=np.float64),
        "moid": np.array(moid, dtype=np.float64),
        "varpi": varpi,
        "d_dark_km": d_dark,
        "d_stony_km": d_stony,
    }
    return cat, encke


def is_autumn_taurid(month: int, day: int) -> bool:
    return (month == 10 and day >= 15) or (month == 11 and day <= 30)


def is_daytime_taurid(month: int, day: int) -> bool:
    return (month == 6 and day >= 10) or (month == 7 and day <= 10)


def load_fireballs() -> List[Dict]:
    raw = json.loads((DATA_DIR / "cneos_fireballs.json").read_text(encoding="utf-8"))
    fi = {k: i for i, k in enumerate(raw["fields"])}
    out = []
    for r in raw["data"]:
        ds = r[fi["date"]]
        ie = r[fi["impact-e"]]
        if not ds or ie is None:
            continue
        dt = datetime.datetime.strptime(ds, "%Y-%m-%d %H:%M:%S")
        # Fractional day of year in [0, 365.25)
        doy = (dt - datetime.datetime(dt.year, 1, 1)).total_seconds() / 86400.0
        vel = float(r[fi["vel"]]) if r[fi["vel"]] is not None else None
        out.append({
            "date": ds,
            "year": dt.year,
            "month": dt.month,
            "day": dt.day,
            "doy": doy,
            "impact_kt": float(ie),
            "vel": vel,
            "autumn": is_autumn_taurid(dt.month, dt.day),
            "daytime": is_daytime_taurid(dt.month, dt.day),
        })
    return out


def analyze_archive_a(cat: Dict[str, np.ndarray], encke: Dict[str, float]) -> Dict:
    varpi_e = encke["varpi"]
    a, e, inc, H, varpi = cat["a"], cat["e"], cat["i"], cat["H"], cat["varpi"]
    d_varpi = ang_diff_deg(varpi, varpi_e)
    cos_align = np.cos(np.deg2rad(d_varpi))

    in_a = (a >= 1.83) & (a <= 2.70)
    box_t = in_a & (e >= 0.63) & (e <= 1.00) & (inc <= 14.0)
    ctrl_lowe = in_a & (e >= 0.40) & (e < 0.63) & (inc <= 14.0)
    ctrl_highi = in_a & (e >= 0.63) & (e <= 1.00) & (inc > 14.0) & (inc <= 35.0)
    in_res72 = (a >= 2.21) & (a <= 2.30)
    aligned45 = np.abs(d_varpi) <= 45.0

    tiers = [("H_lt_16.5", 16.5), ("H_lt_18.0", 18.0), ("H_lt_20.0", 20.0), ("H_lt_22.0", 22.0), ("all_H", 99.0)]
    a1_results = {}
    a2_results = {}

    for idx_t, (tname, hcut) in enumerate(tiers):
        hm = H < hcut
        mt = box_t & hm
        ml = ctrl_lowe & hm
        mh = ctrl_highi & hm

        vt = circular_v_test(varpi[mt], varpi_e, n_mc=N_PERM, seed=SEED + idx_t * 10)
        vl = circular_v_test(varpi[ml], varpi_e, n_mc=N_PERM, seed=SEED + idx_t * 10 + 1)
        vh = circular_v_test(varpi[mh], varpi_e, n_mc=N_PERM, seed=SEED + idx_t * 10 + 2)

        dc_l, p_l = perm_diff_mean(cos_align[mt], cos_align[ml], n_perm=N_PERM, seed=SEED + idx_t * 10 + 3)
        dc_h, p_h = perm_diff_mean(cos_align[mt], cos_align[mh], n_perm=N_PERM, seed=SEED + idx_t * 10 + 4)

        # Also store 18-bin (20 deg) histogram of varpi for Box_T and Ctrl_LowE (for radar chart!)
        edges = np.arange(0.0, 360.1, 20.0)
        hist_t, _ = np.histogram(varpi[mt], bins=edges)
        hist_l, _ = np.histogram(varpi[ml], bins=edges)

        a1_results[tname] = {
            "h_cut": hcut,
            "box_t": vt,
            "ctrl_lowe": vl,
            "ctrl_highi": vh,
            "delta_c_vs_lowe": round(dc_l, 5),
            "p_vs_lowe": round(p_l, 6),
            "delta_c_vs_highi": round(dc_h, 5),
            "p_vs_highi": round(p_h, 6),
            "hist20_box_t": hist_t.tolist(),
            "hist20_ctrl_lowe": hist_l.tolist(),
        }

        # Test A2: 7:2 Jupiter resonance band [2.21, 2.30] inside Taurid-aligned Box_T
        m_al = mt & aligned45
        m_an = mt & (~aligned45)
        n_al = int(np.sum(m_al))
        n_al_res = int(np.sum(m_al & in_res72))
        n_an = int(np.sum(m_an))
        n_an_res = int(np.sum(m_an & in_res72))
        n_cl = int(np.sum(ml))
        n_cl_res = int(np.sum(ml & in_res72))

        f_al = n_al_res / n_al if n_al else 0.0
        f_an = n_an_res / n_an if n_an else 0.0
        f_cl = n_cl_res / n_cl if n_cl else 0.0
        geom_share = 0.09 / 0.87

        p_geom = exact_binom_sf(n_al_res, n_al, geom_share) if n_al else 1.0
        _, p_anti = perm_diff_mean(in_res72[m_al].astype(float), in_res72[m_an].astype(float),
                                   n_perm=N_PERM, seed=SEED + idx_t * 10 + 5)
        _, p_ctrl = perm_diff_mean(in_res72[m_al].astype(float), in_res72[ml].astype(float),
                                   n_perm=N_PERM, seed=SEED + idx_t * 10 + 6)
        enrich_anti = f_al / f_an if f_an > 0 else (float("inf") if f_al > 0 else 1.0)
        enrich_ctrl = f_al / f_cl if f_cl > 0 else (float("inf") if f_al > 0 else 1.0)

        a2_results[tname] = {
            "n_aligned": n_al,
            "n_aligned_res72": n_al_res,
            "frac_aligned_res72": round(f_al, 4),
            "n_anti": n_an,
            "n_anti_res72": n_an_res,
            "frac_anti_res72": round(f_an, 4),
            "n_ctrl_lowe": n_cl,
            "n_ctrl_lowe_res72": n_cl_res,
            "frac_ctrl_lowe_res72": round(f_cl, 4),
            "geom_expected_frac": round(geom_share, 4),
            "enrichment_vs_anti": round(enrich_anti, 3) if math.isfinite(enrich_anti) else None,
            "enrichment_vs_ctrl": round(enrich_ctrl, 3) if math.isfinite(enrich_ctrl) else None,
            "p_vs_geom": round(p_geom, 6),
            "p_vs_anti": round(p_anti, 6),
            "p_vs_ctrl": round(p_ctrl, 6),
        }

    # Direct census of ALL H < 20.0 NEAs inside the 7:2 Taurid resonant zone
    res_mask = box_t & aligned45 & in_res72 & (H < 20.0)
    tight_mask = in_res72 & (e >= 0.75) & (inc <= 12.0) & (np.abs(d_varpi) <= 30.0) & (H < 20.0)
    res_idxs = np.where(res_mask)[0]
    res_idxs = res_idxs[np.argsort(H[res_idxs])]
    census = []
    for i in res_idxs:
        census.append({
            "pdes": str(cat["pdes"][i]),
            "name": str(cat["name"][i]),
            "a": round(float(a[i]), 4),
            "e": round(float(e[i]), 4),
            "i": round(float(inc[i]), 2),
            "varpi": round(float(varpi[i]), 2),
            "d_varpi": round(float(d_varpi[i]), 2),
            "H": round(float(H[i]), 2),
            "d_stony_km": round(float(cat["d_stony_km"][i]), 2),
            "d_dark_km": round(float(cat["d_dark_km"][i]), 2),
            "measured_diam_km": None if math.isnan(cat["diam"][i]) else round(float(cat["diam"][i]), 2),
            "measured_albedo": None if math.isnan(cat["albedo"][i]) else round(float(cat["albedo"][i]), 3),
            "tight_encke": bool(tight_mask[i]),
        })

    # Pass rules
    p18 = a1_results["H_lt_18.0"]
    pass_a1 = (p18["box_t"]["p_unif"] < 0.01) and (p18["p_vs_lowe"] < 0.05) and (p18["delta_c_vs_lowe"] > 0)

    r20 = a2_results["H_lt_20.0"]
    enr_ok = (r20["enrichment_vs_anti"] is not None) and (r20["enrichment_vs_anti"] >= 2.0)
    pass_a2 = enr_ok and (r20["p_vs_anti"] < 0.01) and (r20["p_vs_ctrl"] < 0.01)

    return {
        "n_total_neas": int(len(a)),
        "encke_ref": encke,
        "test_a1_alignment": a1_results,
        "test_a2_resonance72": a2_results,
        "census_res72_H_lt_20": census,
        "n_res72_H_lt_18": int(np.sum(box_t & aligned45 & in_res72 & (H < 18.0))),
        "n_res72_H_lt_20": int(len(census)),
        "n_res72_tight_H_lt_20": int(np.sum(tight_mask)),
        "pass_a1": bool(pass_a1),
        "pass_a2": bool(pass_a2),
    }


def analyze_archive_b(fireballs: List[Dict], yr_lo: int = 1994, yr_hi: int = 2025) -> Dict:
    sub = [f for f in fireballs if yr_lo <= f["year"] <= yr_hi]
    n_tot = len(sub)
    f_aut = AUTUMN_DAYS / YEAR_DAYS
    f_day = DAYTIME_DAYS / YEAR_DAYS

    doys = np.array([f["doy"] for f in sub], dtype=np.float64)
    kts = np.array([f["impact_kt"] for f in sub], dtype=np.float64)
    log_kts = np.log10(np.maximum(kts, 1e-4))
    is_aut = np.array([f["autumn"] for f in sub], dtype=bool)
    is_day = np.array([f["daytime"] for f in sub], dtype=bool)
    is_1kt = kts >= 1.0

    n_aut = int(np.sum(is_aut))
    n_day = int(np.sum(is_day))
    n_1kt = int(np.sum(is_1kt))
    n_aut_1kt = int(np.sum(is_aut & is_1kt))
    n_day_1kt = int(np.sum(is_day & is_1kt))

    p_aut_cnt = exact_binom_sf(n_aut, n_tot, f_aut)
    p_day_cnt = exact_binom_sf(n_day, n_tot, f_day)
    p_aut_1kt = exact_binom_sf(n_aut_1kt, n_1kt, f_aut)
    p_day_1kt = exact_binom_sf(n_day_1kt, n_1kt, f_day)

    # Circular calendar-shift permutation test for total energy & mean log-energy
    rng = np.random.default_rng(SEED + 500)
    shifts = rng.uniform(0.0, YEAR_DAYS, size=N_PERM)

    def window_shift_p(obs_sum_e: float, obs_mean_le: float, width_days: float) -> Tuple[float, float]:
        ge_e = 0
        ge_le = 0
        for sh_d in shifts:
            d_sh = (doys + sh_d) % YEAR_DAYS
            m = d_sh < width_days
            if np.sum(m) > 0:
                if float(np.sum(kts[m])) >= obs_sum_e - 1e-12:
                    ge_e += 1
                if float(np.mean(log_kts[m])) >= obs_mean_le - 1e-12:
                    ge_le += 1
        return float((1 + ge_e) / (N_PERM + 1)), float((1 + ge_le) / (N_PERM + 1))

    e_aut = float(np.sum(kts[is_aut]))
    e_day = float(np.sum(kts[is_day]))
    le_aut = float(np.mean(log_kts[is_aut])) if n_aut else -99.0
    le_day = float(np.mean(log_kts[is_day])) if n_day else -99.0
    p_aut_e, p_aut_le = window_shift_p(e_aut, le_aut, AUTUMN_DAYS)
    p_day_e, p_day_le = window_shift_p(e_day, le_day, DAYTIME_DAYS)

    # Monthly breakdown (12 calendar months) for visualization
    monthly = []
    for mo in range(1, 13):
        mm = [f for f in sub if f["month"] == mo]
        monthly.append({
            "month": mo,
            "count": len(mm),
            "count_1kt": sum(1 for f in mm if f["impact_kt"] >= 1.0),
            "energy_kt": round(sum(f["impact_kt"] for f in mm), 2),
        })

    # Test B2: Swarm years vs non-swarm years (within-year Autumn share + raw counts)
    years = list(range(yr_lo, yr_hi + 1))
    yearly = []
    for y in years:
        fy = [f for f in sub if f["year"] == y]
        fa = [f for f in fy if f["autumn"]]
        ny = len(fy)
        na = len(fa)
        ey = sum(f["impact_kt"] for f in fy)
        ea = sum(f["impact_kt"] for f in fa)
        na1 = sum(1 for f in fa if f["impact_kt"] >= 1.0)
        yearly.append({
            "year": y,
            "swarm6": y in SWARM_YEARS_6,
            "swarm4": y in SWARM_YEARS_4,
            "n_year": ny,
            "n_aut": na,
            "s_cnt": round(na / ny, 4) if ny else 0.0,
            "n_aut_1kt": na1,
            "e_year_kt": round(ey, 2),
            "e_aut_kt": round(ea, 2),
            "s_eng": round(ea / ey, 4) if ey > 0 else 0.0,
        })

    def eval_swarm_set(flag_key: str, seed_off: int) -> Dict:
        sw = [r for r in yearly if r[flag_key]]
        ns = [r for r in yearly if not r[flag_key]]
        out_s = {"n_swarm_years": len(sw), "n_nonswarm_years": len(ns)}
        for metric, m_off in (("s_cnt", 0), ("n_aut", 1), ("n_aut_1kt", 2), ("s_eng", 3)):
            x = np.array([r[metric] for r in sw], dtype=np.float64)
            y = np.array([r[metric] for r in ns], dtype=np.float64)
            diff, pval = perm_diff_mean(x, y, n_perm=N_PERM, seed=SEED + seed_off + m_off)
            out_s[metric] = {
                "mean_swarm": round(float(np.mean(x)), 4),
                "mean_nonswarm": round(float(np.mean(y)), 4),
                "diff": round(diff, 4),
                "p_perm": round(pval, 6),
            }
        return out_s

    b2_6 = eval_swarm_set("swarm6", 700)
    b2_4 = eval_swarm_set("swarm4", 800)

    pass_b1 = min(p_aut_cnt, p_day_cnt, p_aut_1kt, p_day_1kt) < 0.01
    pass_b2 = min(b2_6["s_cnt"]["p_perm"], b2_6["n_aut_1kt"]["p_perm"]) < 0.01

    return {
        "years": [yr_lo, yr_hi],
        "n_bolides": n_tot,
        "n_bolides_1kt": n_1kt,
        "total_energy_kt": round(float(np.sum(kts)), 2),
        "test_b1_seasonality": {
            "autumn_taurids": {
                "window": "Oct 15 - Nov 30",
                "expected_frac": round(f_aut, 5),
                "count": n_aut,
                "expected_count": round(n_tot * f_aut, 2),
                "rate_ratio": round((n_aut / n_tot) / f_aut, 3) if n_tot else 0.0,
                "p_count": round(p_aut_cnt, 6),
                "count_1kt": n_aut_1kt,
                "expected_1kt": round(n_1kt * f_aut, 2),
                "p_1kt": round(p_aut_1kt, 6),
                "energy_kt": round(e_aut, 2),
                "p_energy": round(p_aut_e, 6),
                "mean_log10_kt": round(le_aut, 4),
                "p_mean_log_kt": round(p_aut_le, 6),
            },
            "daytime_taurids": {
                "window": "Jun 10 - Jul 10",
                "expected_frac": round(f_day, 5),
                "count": n_day,
                "expected_count": round(n_tot * f_day, 2),
                "rate_ratio": round((n_day / n_tot) / f_day, 3) if n_tot else 0.0,
                "p_count": round(p_day_cnt, 6),
                "count_1kt": n_day_1kt,
                "expected_1kt": round(n_1kt * f_day, 2),
                "p_1kt": round(p_day_1kt, 6),
                "energy_kt": round(e_day, 2),
                "p_energy": round(p_day_e, 6),
                "mean_log10_kt": round(le_day, 4),
                "p_mean_log_kt": round(p_day_le, 6),
            },
        },
        "test_b2_swarm_years_6": b2_6,
        "test_b2_swarm_years_4_core": b2_4,
        "monthly": monthly,
        "yearly": yearly,
        "pass_b1": bool(pass_b1),
        "pass_b2": bool(pass_b2),
    }


def run_pipeline(decoy: bool = False) -> Dict:
    cat, encke = load_neos()
    fireballs = load_fireballs()
    out_dir = Path("/tmp/taurid_swarm_decoy") if decoy else RESULTS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    if decoy:
        # Strictly blind decoy: randomize varpi and randomize fireball dates across years/DOYs
        rng = np.random.default_rng(12345)
        cat["varpi"] = rng.uniform(0.0, 360.0, size=len(cat["varpi"]))
        for f in fireballs:
            d_rand = float(rng.uniform(0.0, 365.0))
            dt = datetime.datetime(f["year"], 1, 1) + datetime.timedelta(days=d_rand)
            f["month"], f["day"], f["doy"] = dt.month, dt.day, d_rand
            f["autumn"] = is_autumn_taurid(dt.month, dt.day)
            f["daytime"] = is_daytime_taurid(dt.month, dt.day)

    arch_a = analyze_archive_a(cat, encke)
    arch_b = analyze_archive_b(fireballs, 1994, 2025)
    arch_b_all = analyze_archive_b(fireballs, 1988, 2026)

    pass_a = arch_a["pass_a1"] or arch_a["pass_a2"]
    pass_b = arch_b["pass_b1"] or arch_b["pass_b2"]
    if pass_a and pass_b:
        verdict = "macro_swarm_supported"
    elif pass_a or pass_b:
        verdict = "partial_one_archive_only"
    else:
        verdict = "no_macro_swarm_detected"

    summary = {
        "decoy": decoy,
        "archive_a_neos": arch_a,
        "archive_b_fireballs_1994_2025": arch_b,
        "archive_b_fireballs_1988_2026_sensitivity": {
            "n_bolides": arch_b_all["n_bolides"],
            "test_b1_seasonality": arch_b_all["test_b1_seasonality"],
            "test_b2_swarm_years_6": arch_b_all["test_b2_swarm_years_6"],
        },
        "criteria_passed": {
            "A1_perihelion_alignment_H18": arch_a["pass_a1"],
            "A2_resonance72_excess_H20": arch_a["pass_a2"],
            "B1_fireball_seasonality": arch_b["pass_b1"],
            "B2_fireball_swarm_years": arch_b["pass_b2"],
            "total_passed": int(arch_a["pass_a1"]) + int(arch_a["pass_a2"]) + int(arch_b["pass_b1"]) + int(arch_b["pass_b2"]),
        },
        "verdict": verdict,
    }

    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    # Export clean TSVs for transparency
    with (out_dir / "neo_alignment_tiers.tsv").open("w", encoding="utf-8") as f:
        f.write("tier\tn_box_t\tc_bar_t\tp_unif_t\tf45_t\tn_lowe\tc_bar_lowe\tdelta_c_lowe\tp_vs_lowe\tn_highi\tc_bar_highi\tp_vs_highi\n")
        for tname, d in arch_a["test_a1_alignment"].items():
            f.write(
                f"{tname}\t{d['box_t']['n']}\t{d['box_t']['c_bar']:.4f}\t{d['box_t']['p_unif']:.5f}\t{d['box_t']['f_45']:.3f}\t"
                f"{d['ctrl_lowe']['n']}\t{d['ctrl_lowe']['c_bar']:.4f}\t{d['delta_c_vs_lowe']:+.4f}\t{d['p_vs_lowe']:.5f}\t"
                f"{d['ctrl_highi']['n']}\t{d['ctrl_highi']['c_bar']:.4f}\t{d['p_vs_highi']:.5f}\n"
            )

    with (out_dir / "res72_census_H20.tsv").open("w", encoding="utf-8") as f:
        f.write("pdes\tname\ta\te\ti\tvarpi\td_varpi\tH\td_stony_km\td_dark_km\tmeasured_diam_km\ttight_encke\n")
        for r in arch_a["census_res72_H_lt_20"]:
            md = "NA" if r["measured_diam_km"] is None else f"{r['measured_diam_km']:.2f}"
            f.write(f"{r['pdes']}\t{r['name']}\t{r['a']:.4f}\t{r['e']:.4f}\t{r['i']:.2f}\t{r['varpi']:.2f}\t{r['d_varpi']:+.2f}\t{r['H']:.2f}\t{r['d_stony_km']:.2f}\t{r['d_dark_km']:.2f}\t{md}\t{r['tight_encke']}\n")

    with (out_dir / "fireballs_yearly_1994_2025.tsv").open("w", encoding="utf-8") as f:
        f.write("year\tswarm6\tswarm4\tn_year\tn_aut\ts_cnt\tn_aut_1kt\te_year_kt\te_aut_kt\ts_eng\n")
        for r in arch_b["yearly"]:
            f.write(f"{r['year']}\t{r['swarm6']}\t{r['swarm4']}\t{r['n_year']}\t{r['n_aut']}\t{r['s_cnt']:.4f}\t{r['n_aut_1kt']}\t{r['e_year_kt']:.2f}\t{r['e_aut_kt']:.2f}\t{r['s_eng']:.4f}\n")

    return summary


def main():
    parser = argparse.ArgumentParser(description="Test the Taurid Comet Resonant Swarm in NASA JPL NEO and CNEOS Fireball catalogs.")
    parser.add_argument("--decoy", action="store_true", help="Run on blind randomized decoy data")
    args = parser.parse_args()
    s = run_pipeline(decoy=args.decoy)
    mode = "DECOY" if args.decoy else "LOCKED"
    a1 = s["archive_a_neos"]["test_a1_alignment"]["H_lt_18.0"]
    a1_16 = s["archive_a_neos"]["test_a1_alignment"]["H_lt_16.5"]
    a2 = s["archive_a_neos"]["test_a2_resonance72"]["H_lt_20.0"]
    b1a = s["archive_b_fireballs_1994_2025"]["test_b1_seasonality"]["autumn_taurids"]
    b2 = s["archive_b_fireballs_1994_2025"]["test_b2_swarm_years_6"]
    print(f"[{mode}] A1 (H<16.5 Napier box): N={a1_16['box_t']['n']}, c_bar={a1_16['box_t']['c_bar']:+.3f} (p_unif={a1_16['box_t']['p_unif']:.4f}), vs LowE dC={a1_16['delta_c_vs_lowe']:+.3f} (p={a1_16['p_vs_lowe']:.4f})")
    print(f"[{mode}] A1 (H<18.0 Primary):    N={a1['box_t']['n']}, c_bar={a1['box_t']['c_bar']:+.3f} (p_unif={a1['box_t']['p_unif']:.4f}), vs LowE dC={a1['delta_c_vs_lowe']:+.3f} (p={a1['p_vs_lowe']:.4f}) -> pass={s['criteria_passed']['A1_perihelion_alignment_H18']}")
    print(f"[{mode}] A2 (7:2 Res, H<20.0):   {a2['n_aligned_res72']}/{a2['n_aligned']} ({100*a2['frac_aligned_res72']:.1f}%) vs anti {100*a2['frac_anti_res72']:.1f}% (p={a2['p_vs_anti']:.4f}), ctrl {100*a2['frac_ctrl_lowe_res72']:.1f}% (p={a2['p_vs_ctrl']:.4f}) -> pass={s['criteria_passed']['A2_resonance72_excess_H20']}")
    print(f"[{mode}] B1 (Autumn Fireballs):  {b1a['count']}/{s['archive_b_fireballs_1994_2025']['n_bolides']} (exp {b1a['expected_count']:.1f}, ratio={b1a['rate_ratio']:.2f}, p={b1a['p_count']:.4f}), >=1kt: {b1a['count_1kt']} (p={b1a['p_1kt']:.4f}) -> pass={s['criteria_passed']['B1_fireball_seasonality']}")
    print(f"[{mode}] B2 (6 Swarm Years):     s_cnt={b2['s_cnt']['mean_swarm']:.3f} vs {b2['s_cnt']['mean_nonswarm']:.3f} (p={b2['s_cnt']['p_perm']:.4f}), >=1kt/yr: {b2['n_aut_1kt']['mean_swarm']:.2f} vs {b2['n_aut_1kt']['mean_nonswarm']:.2f} (p={b2['n_aut_1kt']['p_perm']:.4f}) -> pass={s['criteria_passed']['B2_fireball_swarm_years']}")
    print(f"[{mode}] VERDICT: {s['verdict']} ({s['criteria_passed']['total_passed']}/4 passed)")


if __name__ == "__main__":
    main()
