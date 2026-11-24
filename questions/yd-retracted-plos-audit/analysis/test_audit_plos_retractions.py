#!/usr/bin/env python3
"""Pre-lock synthetic verification tests for yd-retracted-plos-audit (Issue #127)."""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import audit_plos_retractions as mod


def test_1_marine20_delta_r_shift() -> None:
    marine20 = mod.load_cal_curve(mod.DATA / "marine20.14c")
    c0 = mod.calibrate_14c(11800.0, 50.0, marine20, delta_r=218.0, delta_r_err=50.0)
    c2 = mod.calibrate_14c(11800.0, 50.0, marine20, delta_r=718.0, delta_r_err=150.0)
    assert abs(c0["prob_sum"] - 1.0) < 1e-5
    assert abs(c2["prob_sum"] - 1.0) < 1e-5
    shift = c0["median_cal_bp"] - c2["median_cal_bp"]
    assert 400.0 <= shift <= 800.0, f"Unexpected Marine20 shift: {shift}"
    print(f"[PASS] Test 1: Marine20 +500 yr Delta-R shifts synthetic date younger by {shift:.1f} cal yr ({c0['median_cal_bp']} -> {c2['median_cal_bp']})")


def test_2_intcal20_and_ward_wilson() -> None:
    intcal20 = mod.load_cal_curve(mod.DATA / "intcal20.14c")
    c = mod.calibrate_14c(10900.0, 30.0, intcal20)
    assert 12700.0 <= c["median_cal_bp"] <= 12950.0, f"Unexpected IntCal20 median: {c['median_cal_bp']}"
    ww_sync = mod.ward_wilson_t([10900, 10900, 10900], [30, 30, 30])
    assert ww_sync["T"] == 0.0 and ww_sync["p_value"] == 1.0
    ww_async = mod.ward_wilson_t([10750, 10900, 11100], [30, 30, 30])
    assert ww_async["T"] > 50.0 and ww_async["p_value"] < 0.001
    print(f"[PASS] Test 2: IntCal20 10900+-30 -> {c['median_cal_bp']} cal BP; Ward-Wilson sync T=0.0 vs async T={ww_async['T']} (p={ww_async['p_value']})")


def test_3_pure_terrestrial_x100_artifact() -> None:
    ucc = mod.evaluate_x100_mixing_artifact(mod.UCC_REF["Fe_ppm"], mod.UCC_REF["Cr_ppm"], mod.UCC_REF["Ni_ppm"])
    assert abs(ucc["raw_Fe_Cr"] - 426.09) < 0.5
    assert abs(ucc["raw_Fe_Ni"] - 834.04) < 0.5
    assert abs(ucc["moore_x100_Fe_Cr"] - 4.26) < 0.05
    assert abs(ucc["moore_x100_Fe_Ni"] - 8.34) < 0.05
    assert ucc["moore_x100_enters_cosmic_box"] is True
    assert ucc["ni_excess_ucc_ppm"] < 1.0 and ucc["cr_excess_ucc_ppm"] < 1.5
    print(f"[PASS] Test 3: Pure 100% terrestrial UCC x100 artifact drops Fe/Cr 426->4.26, Fe/Ni 834->8.34 (false cosmic box); proper 99% subtraction -> excess Ni={ucc['ni_excess_ucc_ppm']} ppm")


def test_4_core_uniqueness_detector() -> None:
    synth = {
        "64": [
            {"depth_mid": 290.0, "count": 500.0},
            {"depth_mid": 315.0, "count": 480.0},
            {"depth_mid": 340.0, "count": 10.0},
        ],
        "67": [
            {"depth_mid": 20.0, "count": 20.0},
            {"depth_mid": 33.5, "count": 470.0},
            {"depth_mid": 50.0, "count": 15.0},
        ],
    }
    res = mod.evaluate_core_uniqueness(synth, {"64": (312.0, 318.0), "67": (32.0, 35.0)})
    assert res["67"]["out_to_ydb_ratio"] < 0.1
    assert res["64"]["out_to_ydb_ratio"] > 1.0
    assert res["64"]["out_of_ydb_max"] / res["67"]["ydb_max"] > 1.0
    print(f"[PASS] Test 4: Uniqueness detector separates clean spike (ratio={res['67']['out_to_ydb_ratio']}) from non-unique core (ratio={res['64']['out_to_ydb_ratio']})")


def test_5_verdict_rule_engine() -> None:
    v1 = mod.evaluate_verdicts(
        {"A1_polar_14c": True, "A2_foram_s30_s34": True, "A3_core64_or_coverage": True, "A4_x100_math": False, "A5_d17O_and_refs": False},
        {"B1_chronology_overturned": True, "B2_missing_controls": True, "B_notice_challenges_microscopy": False},
    )
    assert v1["paper_a_baffin_bay"]["verdict"] == "retraction_strongly_supported"
    assert v1["paper_b_shocked_quartz"]["verdict"] == "retraction_mixed_or_harsh"

    v2 = mod.evaluate_verdicts(
        {"A1_polar_14c": False, "A2_foram_s30_s34": False, "A3_core64_or_coverage": False, "A4_x100_math": True, "A5_d17O_and_refs": False},
        {"B1_chronology_overturned": False, "B2_missing_controls": False, "B_notice_challenges_microscopy": False},
    )
    assert v2["paper_a_baffin_bay"]["verdict"] == "retraction_unsupported"
    assert v2["paper_b_shocked_quartz"]["verdict"] == "retraction_unsupported"

    v3 = mod.evaluate_verdicts(
        {"A1_polar_14c": True, "A2_foram_s30_s34": True, "A3_core64_or_coverage": False, "A4_x100_math": False, "A5_d17O_and_refs": False},
        {"B1_chronology_overturned": True, "B2_missing_controls": True, "B_notice_challenges_microscopy": True},
    )
    assert v3["paper_a_baffin_bay"]["verdict"] == "retraction_mixed_or_harsh"
    assert v3["paper_b_shocked_quartz"]["verdict"] == "retraction_strongly_supported"
    print("[PASS] Test 5: Verdict rule engine accurately distinguishes all 3 outcomes for Paper A and Paper B.")


if __name__ == "__main__":
    test_1_marine20_delta_r_shift()
    test_2_intcal20_and_ward_wilson()
    test_3_pure_terrestrial_x100_artifact()
    test_4_core_uniqueness_detector()
    test_5_verdict_rule_engine()
    print("ALL 5 PRE-LOCK SYNTHETIC TESTS PASSED.")
