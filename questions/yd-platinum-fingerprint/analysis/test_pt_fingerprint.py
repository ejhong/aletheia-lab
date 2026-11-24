#!/usr/bin/env python3
"""Pre-lock unit & synthetic recovery tests for pt_fingerprint.py.

Runs strictly on synthetic mixtures and synthetic stratigraphic profiles (zero real data touched).
"""

import numpy as np

from pt_fingerprint import (
    CI_187OS_188OS,
    CI_CHONDRITE_PPT,
    UCC_187OS_188OS,
    UCC_PPT,
    ci_clr,
    clr_classify,
    decide_verdict,
    detect_blind_peaks,
    hse_vec,
    mixing_rmse,
    poisson_binomial_tail,
)


def test_synthetic_compositional_recovery():
    ci = hse_vec(CI_CHONDRITE_PPT)
    ucc = hse_vec(UCC_PPT)
    kudryavy = hse_vec({"Os": 586, "Ir": 16, "Ru": 5, "Pt": 174, "Pd": 219, "Re": 84_640})

    prototypes = {
        "chondrite": ci_clr(ci),
        "kpg_impact": ci_clr(0.99 * ucc + 0.01 * ci),
        "volcanic": ci_clr(kudryavy),
        "ucc": ci_clr(ucc),
    }

    # 1. Synthetic Chicxulub-like mixture (2% CI chondrite + 98% UCC)
    syn_kpg = 0.98 * ucc + 0.02 * ci
    syn_kpg_iso = (0.98 * ucc[0] * UCC_187OS_188OS + 0.02 * ci[0] * CI_187OS_188OS) / (0.98 * ucc[0] + 0.02 * ci[0])
    cls, _ = clr_classify(syn_kpg, prototypes)
    assert cls in {"chondrite", "kpg_impact"}, f"Expected cosmic class, got {cls}"
    f_ci = mixing_rmse(syn_kpg, syn_kpg_iso, ucc, UCC_187OS_188OS, ci, CI_187OS_188OS)
    f_v = mixing_rmse(syn_kpg, syn_kpg_iso, ucc, UCC_187OS_188OS, kudryavy, 0.15)
    assert f_ci["rmse"] < 1e-2 and f_ci["rmse"] < f_v["rmse"], f"Cosmic mix failed: {f_ci} vs {f_v}"

    # 2. Synthetic volcanic-aerosol mixture (20% Kudryavy + 80% UCC)
    syn_volc = 0.80 * ucc + 0.20 * kudryavy
    syn_volc_iso = (0.80 * ucc[0] * UCC_187OS_188OS + 0.20 * kudryavy[0] * 0.15) / (0.80 * ucc[0] + 0.20 * kudryavy[0])
    cls_v, _ = clr_classify(syn_volc, prototypes)
    assert cls_v == "volcanic", f"Expected volcanic class, got {cls_v}"
    fv_ci = mixing_rmse(syn_volc, syn_volc_iso, ucc, UCC_187OS_188OS, ci, CI_187OS_188OS)
    fv_v = mixing_rmse(syn_volc, syn_volc_iso, ucc, UCC_187OS_188OS, kudryavy, 0.15)
    assert fv_v["rmse"] < 1e-2 and fv_v["rmse"] < fv_ci["rmse"], f"Volcanic mix failed: {fv_v} vs {fv_ci}"

    # 3. Pure UCC background
    cls_u, _ = clr_classify(ucc, prototypes)
    assert cls_u == "ucc", f"Expected ucc class, got {cls_u}"
    print("PASS: test_synthetic_compositional_recovery")


def test_blind_peak_detector_recovery():
    # Single clean boundary spike at index 10 in a 20-level core
    rng = np.random.default_rng(42)
    single = 0.5 + rng.normal(0, 0.04, size=20)
    single[10] = 6.5
    res1 = detect_blind_peaks(single, mode="high")
    assert len(res1["events"]) == 1, f"Expected 1 event, got {res1['events']}"
    assert res1["events"][0]["peak_idx"] == 10
    assert res1["global_extreme_idx"] == 10

    # Multi-peak column (3 separated spikes at indices 3, 10, 17)
    multi = single.copy()
    multi[3] = 5.2
    multi[17] = 7.1
    res2 = detect_blind_peaks(multi, mode="high")
    assert len(res2["events"]) == 3, f"Expected 3 events, got {res2['events']}"
    assert res2["global_extreme_idx"] == 17

    # Unradiogenic 187Os/188Os drop detector
    iso = 1.25 + rng.normal(0, 0.03, size=20)
    iso[8] = 0.38
    iso[15] = 0.45
    res3 = detect_blind_peaks(iso, mode="low_iso")
    assert len(res3["events"]) == 2
    assert {e["peak_idx"] for e in res3["events"]} == {8, 15}
    print("PASS: test_blind_peak_detector_recovery")


def test_poisson_binomial_exact_vs_mc():
    probs = [0.10, 0.15, 0.20, 0.08, 0.12, 0.25, 0.05, 0.18]
    rng = np.random.default_rng(999)
    draws = rng.random((50_000, len(probs))) < np.array(probs)[None, :]
    sums = draws.sum(axis=1)
    for k in range(len(probs) + 1):
        exact = poisson_binomial_tail(probs, k)
        mc = float(np.mean(sums >= k))
        assert abs(exact - mc) < 0.005, f"Mismatch at k={k}: exact={exact}, mc={mc}"
    print("PASS: test_poisson_binomial_exact_vs_mc")


def test_decision_rules():
    assert decide_verdict(0.95, 0.90, 0.80, 0.20, -0.4, 2.5, 0.1, 0.001) == "cosmic_impact_fingerprint"
    assert decide_verdict(0.95, 0.90, 0.10, 0.90, +0.4, 35.0, 0.6, 0.20) == "non_cosmic_and_non_unique"
    assert decide_verdict(0.95, 0.90, 0.10, 0.90, +0.4, 35.0, 0.2, 0.001) == "non_cosmic_with_ydb_anomaly"
    assert decide_verdict(0.50, 0.90, 0.10, 0.90, +0.4, 35.0, 0.6, 0.20) == "ambiguous_or_mixed"
    print("PASS: test_decision_rules")


if __name__ == "__main__":
    test_synthetic_compositional_recovery()
    test_blind_peak_detector_recovery()
    test_poisson_binomial_exact_vs_mc()
    test_decision_rules()
    print("ALL 4 SYNTHETIC PRE-LOCK TESTS PASSED.")
