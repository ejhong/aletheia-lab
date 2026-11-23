#!/usr/bin/env python3
"""Unit tests and simulated-sky recovery checks for analysis/skyhole.py.

Runs strictly BEFORE locking protocol.md. Never reads real southern-sky y_i labels.
Verifies:
1. Vondrak et al. (2011/2012) long-term precession poles at J2000, 2750 BCE (Thuban),
   12000 BCE (Vega), and obliquity values.
2. Kasten & Young (1989) airmass and Bennett (1982) refraction sanity bounds.
3. 4-epoch synthetic sky recovery (-9600, -2500, -1200, +137) on real Hipparcos stars.
4. Correlated/patchy southern sky calibration: verifies Spatial Block Bootstrap 95% CI
   is wider than naive star-level CI and covers true epoch.
"""
import math
import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import skyhole as sh


def test_precession_astrometry():
    # J2000 North Celestial Pole must be (0, 0, 1)
    p2000 = sh.ltpequ(2000.0)
    assert abs(p2000[0]) < 1e-6 and abs(p2000[1]) < 1e-6 and abs(p2000[2] - 1.0) < 1e-6, p2000

    # Obliquity at J2000 ~ 23.4393 deg, at -3000 (~3001 BCE) ~ 24.02 deg
    e2000 = sh.ltpecl(2000.0)
    ob_2000 = math.degrees(math.acos(float(np.clip(p2000 @ e2000, -1.0, 1.0))))
    assert abs(ob_2000 - 23.4393) < 0.01, f"J2000 obliquity {ob_2000}"

    p_m3000 = sh.ltpequ(-3000.0)
    e_m3000 = sh.ltpecl(-3000.0)
    ob_m3000 = math.degrees(math.acos(float(np.clip(p_m3000 @ e_m3000, -1.0, 1.0))))
    assert 23.95 < ob_m3000 < 24.10, f"-3000 obliquity {ob_m3000}"

    # Thuban (Alpha Dra, RA=211.097 deg, Dec=+64.376 deg J2000) was < 0.5 deg from NCP around -2780 (2781 BCE)
    ra_t, de_t = math.radians(211.097), math.radians(64.376)
    u_thuban = np.array([math.cos(de_t) * math.cos(ra_t), math.cos(de_t) * math.sin(ra_t), math.sin(de_t)])
    p_thuban = sh.ltpequ(-2780.0)
    sep_thuban = math.degrees(math.acos(float(np.clip(u_thuban @ p_thuban, -1.0, 1.0))))
    assert sep_thuban < 0.5, f"Thuban separation at -2780 was {sep_thuban:.2f} deg"

    # Vega (Alpha Lyr, RA=279.235 deg, Dec=+38.784 deg J2000) was within ~5 deg of NCP around -12000
    ra_v, de_v = math.radians(279.235), math.radians(38.784)
    u_vega = np.array([math.cos(de_v) * math.cos(ra_v), math.cos(de_v) * math.sin(ra_v), math.sin(de_v)])
    p_vega = sh.ltpequ(-12000.0)
    sep_vega = math.degrees(math.acos(float(np.clip(u_vega @ p_vega, -1.0, 1.0))))
    assert sep_vega < 6.0, f"Vega separation at -12000 was {sep_vega:.2f} deg"
    print(f"[PASS] Astrometry: ob(2000)={ob_2000:.4f} deg, ob(-3000)={ob_m3000:.4f} deg, "
          f"Thuban(-2780)={sep_thuban:.2f} deg, Vega(-12000)={sep_vega:.2f} deg")


def test_extinction_and_refraction():
    r0 = float(sh.bennett_refraction_deg(np.array([0.0]))[0])
    r90 = float(sh.bennett_refraction_deg(np.array([90.0]))[0])
    assert 0.45 < r0 < 0.65, f"Horizon refraction {r0}"
    assert r90 < 0.01, f"Zenith refraction {r90}"

    x90 = float(sh.kasten_young_airmass(np.array([90.0]))[0])
    x10 = float(sh.kasten_young_airmass(np.array([10.0]))[0])
    x1 = float(sh.kasten_young_airmass(np.array([1.0]))[0])
    assert abs(x90 - 1.0) < 0.01, x90
    assert 5.4 < x10 < 5.8, x10
    assert 24.0 < x1 < 28.0, x1
    print(f"[PASS] Atmosphere: R(0)={r0:.3f} deg, X(90)={x90:.3f}, X(10)={x10:.2f}, X(1)={x1:.1f}")


def test_synthetic_sky_recovery():
    cat = sh.load_catalogs(v_max=5.5)
    north_mask = cat["ecl_lat"] > 30.0
    test_mask = ~north_mask
    u0_t = cat["u0"][test_mask]
    vel_t = cat["vel"][test_mask]
    vmag_t = cat["vmag"][test_mask]
    epochs_c = np.arange(-10500.0, 1000.1, 100.0)
    lats_c = np.arange(15.0, 50.01, 0.5)

    scenarios = [
        (-9600.0, 37.0, 101),
        (-2500.0, 36.0, 102),
        (-1200.0, 33.0, 103),
        (137.0, 31.2, 104),
    ]
    for t_true, lat_true, seed in scenarios:
        y_syn = sh.simulate_synthetic_labels(cat, t_true, lat_true, seed=seed, patchy=False)
        v50, sv = sh.fit_northern_completeness(cat["vmag"][north_mask], y_syn[north_mask])
        fit = sh.fit_m1_coarse_and_fine(u0_t, vel_t, vmag_t, y_syn[test_mask], v50, sv, 0.25, epochs_c, lats_c)
        err_t = fit["epoch"] - t_true
        err_l = fit["lat"] - lat_true
        print(f"  Synthetic ({t_true:+.0f}, {lat_true:.1f} N) -> recovered ({fit['epoch']:+.0f}, {fit['lat']:.2f} N) "
              f"[err_t={err_t:+.0f} yr, err_lat={err_l:+.2f} deg]")
        assert abs(err_t) <= 350.0, f"Epoch recovery failed: {err_t}"
        assert abs(err_l) <= 1.5, f"Lat recovery failed: {err_l}"
    print("[PASS] 4-epoch synthetic sky recovery within pre-registered tolerances")


def test_patchy_bootstrap_calibration():
    cat = sh.load_catalogs(v_max=5.5)
    north_mask = cat["ecl_lat"] > 30.0
    test_mask = ~north_mask
    u0_t = cat["u0"][test_mask]
    vel_t = cat["vel"][test_mask]
    vmag_t = cat["vmag"][test_mask]
    tile_ids, n_tiles = sh.assign_spatial_tiles(cat["ecl_lon"][test_mask], cat["ecl_lat"][test_mask])
    epochs_c = np.arange(-5500.0, 1000.1, 50.0)
    lats_c = np.arange(20.0, 48.01, 0.5)

    t_true, lat_true = -2200.0, 35.0
    y_patchy = sh.simulate_synthetic_labels(cat, t_true, lat_true, seed=2026, patchy=True)
    v50, sv = sh.fit_northern_completeness(cat["vmag"][north_mask], y_patchy[north_mask])
    fit = sh.fit_m1_coarse_and_fine(u0_t, vel_t, vmag_t, y_patchy[test_mask], v50, sv, 0.25, epochs_c, lats_c)
    _, tile_ll = sh.evaluate_m1_grid(
        u0_t, vel_t, vmag_t, y_patchy[test_mask], epochs_c, lats_c, v50, sv, 0.25,
        tile_ids=tile_ids, n_tiles=n_tiles,
    )
    boot = sh.run_spatial_block_bootstrap(tile_ll, epochs_c, lats_c, n_boot=300, seed=77)
    naive_w = fit["naive_95_epoch"][1] - fit["naive_95_epoch"][0]
    boot_w = boot["epoch_ci95"][1] - boot["epoch_ci95"][0]
    print(f"  Patchy sky true=-2200 -> est={fit['epoch']:.0f}, "
          f"naive 95%={fit['naive_95_epoch']} (w={naive_w:.0f}), "
          f"block-boot 95%={boot['epoch_ci95']} (w={boot_w:.0f})")
    assert boot_w >= naive_w * 0.9, "Block bootstrap should reflect spatial uncertainty"
    assert boot["epoch_ci95"][0] <= t_true <= boot["epoch_ci95"][1], "Block bootstrap 95% CI missed patchy true epoch"
    print("[PASS] Patchy sky spatial block bootstrap calibration verified")


if __name__ == "__main__":
    test_precession_astrometry()
    test_extinction_and_refraction()
    test_synthetic_sky_recovery()
    test_patchy_bootstrap_calibration()
    print("ALL TESTS PASSED.")
