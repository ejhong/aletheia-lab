#!/usr/bin/env python3
"""
Pre-lock synthetic verification tests for ydb-site-synchrony (Issue #113).
Verifies IntCal20 calibration, forward-simulation calibration, Type-I/Type-II
behavior on synchronous vs. diachronous synthetic datasets, and Pillar 2
placebo-year overlap metrics — WITHOUT touching real YDB datasets.
"""

from pathlib import Path
import numpy as np

from site_synchrony import (
    C14Date,
    KennettSite,
    CAL_GRID_MIN,
    DATA_DIR,
    calibrate_single,
    load_intcal20,
    run_pillar2_audit,
    run_synchrony_panel,
)


def test_intcal20_calibration() -> None:
    grid, mu_c, sig_c = load_intcal20(DATA_DIR / "intcal20.14c")
    assert len(grid) == 5001
    # Known reference: 11,066 ± 11 14C BP (Laacher See Tephra) calibrates near ~13,000 cal BP on IntCal20
    cal = calibrate_single(11066.0, 11.0, grid, mu_c, sig_c)
    assert 12920.0 <= cal["median"] <= 13060.0, f"Unexpected LST calibration median: {cal['median']}"
    assert cal["hpd95_lower"] < cal["median"] < cal["hpd95_upper"]
    print(f"[PASS] IntCal20 calibration: 11066±11 -> median {cal['median']:.1f} cal BP (95% HPD {cal['hpd95_lower']:.0f}-{cal['hpd95_upper']:.0f})")


def test_synchronous_vs_diachronous_synthetic() -> None:
    grid, mu_c, sig_c = load_intcal20(DATA_DIR / "intcal20.14c")
    rng = np.random.default_rng(42)
    sigmas = [30.0, 35.0, 40.0, 45.0, 50.0, 50.0, 60.0, 70.0, 80.0]

    # 1. True synchronous single-year event at 12,850 cal BP
    idx_sync = int(12850 - CAL_GRID_MIN)
    mu0, sc0 = float(mu_c[idx_sync]), float(sig_c[idx_sync])
    sync_dates = [
        C14Date(
            site=f"SyncSite_{i}",
            lab_id=f"SYN-{i}",
            rcybp=float(rng.normal(mu0, np.sqrt(s**2 + sc0**2))),
            sigma=s,
            material="charcoal",
            is_wood_or_charcoal=True,
            source="synthetic",
        )
        for i, s in enumerate(sigmas)
    ]
    res_sync = run_synchrony_panel("Synthetic_Sync", sync_dates, grid, mu_c, sig_c, [12800, 12850, 12900], n_sim=400, seed=101)
    assert res_sync["M0"]["p_T_best"] >= 0.05 and res_sync["M0"]["p_SD_best"] >= 0.05, f"Synchronous false reject: {res_sync['M0']}"
    print(f"[PASS] Synthetic single-year event passes M0 (p_T={res_sync['M0']['p_T_best']}, p_SD={res_sync['M0']['p_SD_best']})")

    # 2. Staggered 300-yr diachronous event (12,700..13,000 cal BP) -> rejected under M0
    true_years_300 = np.linspace(12700, 13000, len(sigmas))
    diach_300 = []
    for i, (ty, s) in enumerate(zip(true_years_300, sigmas)):
        idx = int(round(ty) - CAL_GRID_MIN)
        diach_300.append(C14Date(
            site=f"Diach300_{i}",
            lab_id=f"D300-{i}",
            rcybp=float(rng.normal(mu_c[idx], np.sqrt(s**2 + sig_c[idx]**2))),
            sigma=s,
            material="charcoal",
            is_wood_or_charcoal=True,
            source="synthetic",
        ))
    res_d300 = run_synchrony_panel("Synthetic_Diach300", diach_300, grid, mu_c, sig_c, [12750, 12850, 12950], n_sim=400, seed=102)
    assert res_d300["M0"]["p_T_best"] < 0.01, f"Expected M0 rejection for 300-yr stagger, got p_T={res_d300['M0']['p_T_best']}"
    print(f"[PASS] Synthetic 300-yr staggered catalogue rejected under M0 (T={res_d300['ward_wilson_T']}, p_T={res_d300['M0']['p_T_best']})")

    # 3. Staggered 600-yr diachronous event (12,550..13,150 cal BP) -> rejected even under M1 (inter-lab + old wood)
    true_years_600 = np.linspace(12550, 13150, len(sigmas))
    diach_600 = []
    for i, (ty, s) in enumerate(zip(true_years_600, sigmas)):
        idx = int(round(ty) - CAL_GRID_MIN)
        diach_600.append(C14Date(
            site=f"Diach600_{i}",
            lab_id=f"D600-{i}",
            rcybp=float(rng.normal(mu_c[idx], np.sqrt(s**2 + sig_c[idx]**2))),
            sigma=s,
            material="charcoal",
            is_wood_or_charcoal=True,
            source="synthetic",
        ))
    res_d600 = run_synchrony_panel("Synthetic_Diach600", diach_600, grid, mu_c, sig_c, [12750, 12850, 12950], n_sim=400, seed=103)
    assert res_d600["M1"]["p_T_best"] < 0.01 and res_d600["M1"]["p_SD_best"] < 0.01, f"Expected M1 rejection for 600-yr stagger: {res_d600['M1']}"
    print(f"[PASS] Synthetic 600-yr staggered catalogue rejected even under M1 (p_T={res_d600['M1']['p_T_best']}, p_SD={res_d600['M1']['p_SD_best']})")


def test_pillar2_placebo_overlap() -> None:
    # Tight (±100 yr) synthetic sites -> W_50 == 200 yr
    tight_sites = [
        KennettSite(f"T{i}", 12800.0, 50.0, 12900.0, 12700.0, 10, 0, 10, "High", True)
        for i in range(9)
    ] + [
        KennettSite(f"M{i}", 12800.0, 50.0, 12900.0, 12700.0, 10, 0, 10, "Med", True)
        for i in range(8)
    ] + [
        KennettSite(f"L{i}", 12800.0, 50.0, 12900.0, 12700.0, 10, 0, 10, "Low", True)
        for i in range(6)
    ]
    res_t = run_pillar2_audit(tight_sites)
    assert res_t["W_50"]["width_yr"] == 200.0, f"Expected W_50=200, got {res_t['W_50']}"

    # Wide (±600 yr) synthetic sites -> W_50 == 1200 yr
    wide_sites = [
        KennettSite(f"W{i}", 12800.0, 300.0, 13400.0, 12200.0, 10, 2, 8, "High" if i < 9 else ("Med" if i < 17 else "Low"), False)
        for i in range(23)
    ]
    res_w = run_pillar2_audit(wide_sites)
    assert res_w["W_50"]["width_yr"] == 1200.0, f"Expected W_50=1200, got {res_w['W_50']}"
    print(f"[PASS] Pillar 2 placebo overlap: tight W_50={res_t['W_50']['width_yr']} yr, wide W_50={res_w['W_50']['width_yr']} yr")


if __name__ == "__main__":
    test_intcal20_calibration()
    test_synchronous_vs_diachronous_synthetic()
    test_pillar2_placebo_overlap()
    print("ALL PRE-LOCK SYNTHETIC TESTS PASSED.")
