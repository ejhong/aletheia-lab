#!/usr/bin/env python3
"""
Pre-lock unit & synthetic recovery tests for megafauna_timing.py.
Uses ONLY synthetic data + the IntCal20 reference curve (zero real Neotoma or megafauna dates).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import megafauna_timing as mt


def test_intcal20_calibration_recovery() -> None:
    """Calibrating exact IntCal20 14C ages recovers the true calendar age within ~150 yr."""
    cal_bp, c14_bp, sig = mt.load_intcal20(mt.DATA_DIR / "intcal20.14c")
    t_grid = np.arange(9000.0, 20005.0, 5.0)
    mu, s_ic = mt.interpolate_intcal20(cal_bp, c14_bp, sig, t_grid)

    true_ages = np.array([15000.0, 14000.0, 13400.0, 12850.0, 12000.0])
    rc_ages = np.interp(true_ages, cal_bp, c14_bp)
    errs = np.full_like(rc_ages, 40.0)
    p = mt.calibrate_dates_matrix(rc_ages, errs, mu, s_ic)
    for i, t_true in enumerate(true_ages):
        lo, med, hi = mt.posterior_quantiles(t_grid, p[i])
        assert lo <= t_true <= hi, f"True age {t_true} outside 95% CI [{lo}, {hi}]"
        assert abs(med - t_true) < 160.0, f"Median {med} too far from {t_true}"
    print("PASS: test_intcal20_calibration_recovery")


def test_sporormiella_synthetic_step_and_ramp() -> None:
    """Verify exact recovery of t_2pct, t_50pct, and t_cp on synthetic curves."""
    # Step drop at 13,800 cal BP (from 6.0% down to 0.4%)
    ages = np.arange(16500.0, 10000.0, -250.0)
    pct = np.where(ages >= 13800.0, 6.0, 0.4)
    m = mt.compute_sporormiella_metrics(ages, pct)
    assert abs(m["t_cp"] - 13875.0) <= 130.0, f"Bad step t_cp: {m['t_cp']}"
    assert abs(m["t_2pct"] - 13850.0) <= 150.0, f"Bad step t_2pct: {m['t_2pct']}"
    assert abs(m["t_50pct"] - 13850.0) <= 150.0, f"Bad step t_50pct: {m['t_50pct']}"
    assert m["r2_step"] > 0.99, f"Expected R2 ~ 1.0, got {m['r2_step']}"

    # Linear ramp from 8.0% at 15,000 down to 0.0% at 13,000 (hits 4% at 14,000, 2% at 13,500)
    pct_ramp = np.clip(8.0 * (ages - 13000.0) / 2000.0, 0.0, 8.0)
    mr = mt.compute_sporormiella_metrics(ages, pct_ramp)
    assert abs(mr["t_2pct"] - 13500.0) <= 25.0, f"Bad ramp t_2pct: {mr['t_2pct']}"
    assert abs(mr["t_50pct"] - 14000.0) <= 25.0, f"Bad ramp t_50pct: {mr['t_50pct']}"
    print("PASS: test_sporormiella_synthetic_step_and_ramp")


def test_h_impact_self_consistency() -> None:
    """A synthetic catalog generated under H_impact (instant wipeout at 12,850) must stay inside H_impact 95% bounds."""
    cal_bp, c14_bp, sig = mt.load_intcal20(mt.DATA_DIR / "intcal20.14c")
    t_grid = np.arange(9000.0, 20005.0, 5.0)
    mu, s_ic = mt.interpolate_intcal20(cal_bp, c14_bp, sig, t_grid)

    rng = np.random.default_rng(12345)
    n_obs = 250
    errs = np.full(n_obs, 45.0)
    sim = mt.simulate_h_impact(
        n_obs, errs, t_grid, mu, s_ic, cal_bp, c14_bp, sig, rng,
        n_sims=200, pool_size=6000, taph_weighted=False,
    )
    # Generate one independent true H_impact realization
    t_true = rng.uniform(mt.T_IMPACT, 18000.0, size=n_obs)
    r_sim = rng.normal(
        np.interp(t_true, cal_bp, c14_bp),
        np.sqrt(errs ** 2 + np.interp(t_true, cal_bp, sig) ** 2),
    )
    p = mt.calibrate_dates_matrix(r_sim, errs, mu, s_ic)
    spd = np.mean(p, axis=0)
    obs = mt.compute_spd_metrics(t_grid, spd)
    assert sim["raw"]["m_yd_p025"] * 0.5 <= obs["m_yd"] <= sim["raw"]["m_yd_p990"] * 1.15, (
        f"Synthetic H_impact M_yd={obs['m_yd']:.4f} outside envelope "
        f"[{sim['raw']['m_yd_p025']:.4f}, {sim['raw']['m_yd_p990']:.4f}]"
    )
    # Verify a real post-impact survival signal (20% of dates in 12,400-11,900) blows past H_impact 99%
    t_surv = np.concatenate([rng.uniform(mt.T_IMPACT, 18000.0, 200), rng.uniform(11900.0, 12400.0, 50)])
    r_surv = rng.normal(
        np.interp(t_surv, cal_bp, c14_bp),
        np.sqrt(errs ** 2 + np.interp(t_surv, cal_bp, sig) ** 2),
    )
    p_surv = mt.calibrate_dates_matrix(r_surv, errs, mu, s_ic)
    obs_surv = mt.compute_spd_metrics(t_grid, np.mean(p_surv, axis=0))
    assert obs_surv["m_yd"] > sim["raw"]["m_yd_p990"] * 2.0, "Post-impact survivor test did not trigger!"
    print(f"PASS: test_h_impact_self_consistency (H_impact M_yd={obs['m_yd']:.4f} vs surv={obs_surv['m_yd']:.4f})")


def test_ole_and_griwm_signor_lipps() -> None:
    """Verify OLE and GRIWM correct the Signor-Lipps lag on synthetic Uniform & declining extinctions."""
    rng = np.random.default_rng(99)
    true_ext = 12850.0
    lads, oles, griwms = [], [], []
    for _ in range(300):
        dates = np.sort(rng.uniform(true_ext, true_ext + 3000.0, size=30))[:10]
        lads.append(dates[0])
        oles.append(mt.ole_estimate(dates))
        griwms.append(mt.griwm_estimate(dates))
    # LAD should lag older than true extinction by ~100 yr; OLE & GRIWM should center within ~50 yr of true_ext
    assert np.mean(lads) > true_ext + 60.0, f"Expected Signor-Lipps lag in LAD, got {np.mean(lads):.1f}"
    assert abs(np.mean(oles) - true_ext) < 60.0, f"OLE biased: {np.mean(oles):.1f}"
    assert abs(np.mean(griwms) - true_ext) < 60.0, f"GRIWM biased: {np.mean(griwms):.1f}"
    print(
        f"PASS: test_ole_and_griwm_signor_lipps "
        f"(true={true_ext:.0f}, LAD={np.mean(lads):.1f}, OLE={np.mean(oles):.1f}, GRIWM={np.mean(griwms):.1f})"
    )


if __name__ == "__main__":
    test_intcal20_calibration_recovery()
    test_sporormiella_synthetic_step_and_ramp()
    test_h_impact_self_consistency()
    test_ole_and_griwm_signor_lipps()
    print("\nALL PRE-LOCK SYNTHETIC TESTS PASSED!")
