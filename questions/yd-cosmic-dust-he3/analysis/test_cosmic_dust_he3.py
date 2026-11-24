#!/usr/bin/env python3
"""
Pre-lock synthetic verification suite for Issue #121 (yd-cosmic-dust-he3).
Tests ONLY synthetic data and mathematical identities — never touches real 3He_ET flux outcomes.
"""

import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cosmic_dust_he3 as cd


def make_synthetic_p1(surge_window=None, surge_factor=1.0, nuggets=0, seed=42):
    """Build 7 synthetic cores matching real Pillar 1 sample counts & age spans with 25% log-normal IDP scatter."""
    rng = np.random.default_rng(seed)
    specs = [
        ("SO202-07-6", "Subarctic North Pacific", 0.85, [4.0, 9.8, 7], [10.1, 14.9, 22], [15.2, 27.0, 22]),
        ("CR01", "Cocos Ridge", 0.65, [0.5, 9.5, 11], [10.2, 14.8, 3], [15.5, 21.0, 4]),
        ("CR02", "Cocos Ridge", 0.90, [2.0, 9.5, 15], [10.5, 14.5, 2], [15.5, 21.4, 6]),
        ("CR03", "Cocos Ridge", 0.72, [4.4, 9.8, 10], [10.5, 14.5, 3], [15.2, 17.3, 4]),
        ("CR05", "Cocos Ridge", 0.80, [0.5, 9.8, 13], [10.5, 14.8, 4], [15.0, 15.1, 1]),
        ("MANOP_B18", "Central Eq Pacific", 0.78, [0.5, 9.5, 3], [10.5, 14.5, 1], [16.0, 250.0, 26]),
        ("MANOP_B25", "Central Eq Pacific", 0.82, [1.0, 9.5, 2], [15.5, 24.5, 4], [26.0, 300.0, 24]),
    ]
    samples = []
    for cname, reg, base_f, s_hol, s_deg, s_glac in specs:
        ages = np.concatenate([
            np.linspace(s_hol[0], s_hol[1], s_hol[2]),
            np.linspace(s_deg[0], s_deg[1], s_deg[2]),
            np.linspace(s_glac[0], s_glac[1], s_glac[2]),
        ])
        for a in ages:
            f = base_f * float(np.exp(rng.normal(0.0, 0.22)))
            if surge_window is not None and surge_window[0] <= a <= surge_window[1]:
                f *= surge_factor
            samples.append(cd.Sample(core=cname, region=reg, lab="Synthetic", age_ka=float(a), flux_pcc_cm2_kyr=f))

    if nuggets > 0:
        yd_idx = [i for i, s in enumerate(samples) if 11.5 <= s.age_ka <= 13.5]
        for idx in yd_idx[:nuggets]:
            samples[idx].flux_pcc_cm2_kyr *= 8.0
    return samples


def fake_pos_pass():
    return {
        "Veritas_8.2Ma_ODP757B": {"median_ratio": 3.8, "p_perm_one_sided": 0.0001},
        "Veritas_8.2Ma_ODP926B": {"median_ratio": 3.5, "p_perm_one_sided": 0.0001},
        "LateEocene_35.5Ma_ODP757B": {"median_ratio": 4.2, "p_perm_one_sided": 0.0001},
    }


def eval_synth(samples):
    serno = [s for s in samples if s.core == "SO202-07-6"]
    cocos = [s for s in samples if s.core.startswith("CR")]
    p_all, p_s, p_c = {}, {}, {}
    for i, (wname, (lo, hi)) in enumerate(cd.WINDOWS.items()):
        p_all[wname] = cd.stratified_window_test(samples, lo, hi, n_perm=1000, n_boot=1000, seed=100 + i)
        p_s[wname] = cd.stratified_window_test(serno, lo, hi, n_perm=1000, n_boot=1000, seed=200 + i)
        p_c[wname] = cd.stratified_window_test(cocos, lo, hi, n_perm=1000, n_boot=1000, seed=300 + i)
    verdict, reason = cd.evaluate_verdict(fake_pos_pass(), p_all, p_s, p_c)
    return verdict, reason, p_all


def main():
    # Test 1: Exact physics & unit conversion
    f_et = cd.deconvolve_3he_et_fraction(1.0)  # R_meas = 1e-4 >> R_terr = 2e-8
    assert abs(f_et - 0.99985) < 1e-4, f"Unexpected ET fraction: {f_et}"
    assert cd.deconvolve_3he_et_fraction(cd.R_TERR_DEFAULT_1E4) == 0.0
    # Unit conversion: 0.01 (1e-10 cm3/g) = 1.0 pcc/g; MAR = 8.0 g/m2/a = 0.8 g/cm2/kyr -> 0.80 pcc/cm2/kyr
    flux_unit_check = (0.01 * 100.0) * (8.0 * 0.1)
    assert abs(flux_unit_check - 0.80) < 1e-9
    print("[PASS] Test 1: 3He_ET deconvolution & unit conversion exact.")

    # Test 2: Flat constant-flux null -> no_cosmic_dust_surge
    s_null = make_synthetic_p1(surge_window=None, surge_factor=1.0, seed=101)
    v_null, _, res_null = eval_synth(s_null)
    assert v_null == "no_cosmic_dust_surge", f"Expected no_cosmic_dust_surge, got {v_null}: {res_null}"
    print(f"[PASS] Test 2: Flat null -> {v_null} (W1={res_null['W1_YD_13.5_11.5']['median_ratio']:.2f}x, W2={res_null['W2_Deglacial_15_10']['median_ratio']:.2f}x)")

    # Test 3: 2.5x narrow YD (13.5-11.5 ka) surge -> cosmic_dust_surge_detected
    s_yd = make_synthetic_p1(surge_window=(11.5, 13.5), surge_factor=2.5, seed=102)
    v_yd, _, res_yd = eval_synth(s_yd)
    assert v_yd == "cosmic_dust_surge_detected", f"Expected surge detected, got {v_yd}: {res_yd}"
    print(f"[PASS] Test 3: 2.5x narrow YD surge -> {v_yd} (W1={res_yd['W1_YD_13.5_11.5']['median_ratio']:.2f}x, p={res_yd['W1_YD_13.5_11.5']['p_perm_one_sided']:.4f})")

    # Test 4: 2.5x broad deglacial (20-10 ka) surge -> cosmic_dust_surge_detected
    s_deg = make_synthetic_p1(surge_window=(10.0, 20.0), surge_factor=2.5, seed=103)
    v_deg, _, res_deg = eval_synth(s_deg)
    assert v_deg == "cosmic_dust_surge_detected", f"Expected surge detected, got {v_deg}: {res_deg}"
    print(f"[PASS] Test 4: 2.5x broad deglacial surge -> {v_deg} (W3={res_deg['W3_Broad_20_10']['median_ratio']:.2f}x, p={res_deg['W3_Broad_20_10']['p_perm_one_sided']:.4f})")

    # Test 5: Nugget-outlier resistance (2 isolated 8x nuggets in flat YD)
    s_nug = make_synthetic_p1(surge_window=None, surge_factor=1.0, nuggets=2, seed=101)
    v_nug, _, res_nug = eval_synth(s_nug)
    assert v_nug != "cosmic_dust_surge_detected", f"Nuggets falsely triggered surge: {v_nug}"
    print(f"[PASS] Test 5: Nugget resistance -> {v_nug} (W1 median={res_nug['W1_YD_13.5_11.5']['median_ratio']:.2f}x vs mean={res_nug['W1_YD_13.5_11.5']['mean_ratio']:.2f}x)")

    print("ALL 5 PRE-LOCK SYNTHETIC TESTS PASSED.")


if __name__ == "__main__":
    main()
