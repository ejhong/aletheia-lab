#!/usr/bin/env python3
"""Synthetic unit tests for #88 (ice-age-farming)."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import run_ice_age_farming as iaf


def make_synthetic_core(samples, controls):
    return {
        "datasetid": 99999,
        "sitename": "Synthetic Lake",
        "database": "Test",
        "lon": 15.0,
        "lat": 48.0,
        "altitude": 300,
        "n_samples_valid": len(samples),
        "age_min_cal": min(s["age_cal"] for s in samples),
        "age_max_cal": max(s["age_cal"] for s in samples),
        "chron_controls": controls,
        "samples": samples,
    }


def test_planted_neolithic_detection():
    # Forested baseline (AP=80%) at 14-15 ka, then clearance (AP=55%) + Cerealia 1.5% + Plantago 1.2% at 13.0 & 12.6 ka
    samples = [
        {"depth": 100.0, "age_raw": 12600, "age_cal": 12600.0, "age_type": "Calibrated radiocarbon years BP", "is_14c": False, "terrestrial_sum": 400, "is_pct_units": False, "crop_val": 6.0, "crop_pct": 1.5, "weed_pct": 1.2, "plantago_lan_pct": 1.0, "ap_pct": 55.0, "crop_taxa": {"Poaceae (Cerealia)": 6}, "weed_taxa": {"Plantago lanceolata": 4}},
        {"depth": 120.0, "age_raw": 13000, "age_cal": 13000.0, "age_type": "Calibrated radiocarbon years BP", "is_14c": False, "terrestrial_sum": 400, "is_pct_units": False, "crop_val": 5.0, "crop_pct": 1.25, "weed_pct": 1.0, "plantago_lan_pct": 0.75, "ap_pct": 58.0, "crop_taxa": {"Poaceae (Cerealia)": 5}, "weed_taxa": {"Plantago lanceolata": 3}},
        {"depth": 160.0, "age_raw": 14200, "age_cal": 14200.0, "age_type": "Calibrated radiocarbon years BP", "is_14c": False, "terrestrial_sum": 400, "is_pct_units": False, "crop_val": 0.0, "crop_pct": 0.0, "weed_pct": 0.0, "plantago_lan_pct": 0.0, "ap_pct": 80.0, "crop_taxa": {}, "weed_taxa": {}},
    ]
    controls = [{"depth": 80.0, "age": 11500}, {"depth": 150.0, "age": 14000}]
    core = make_synthetic_core(samples, controls)
    res = iaf.evaluate_window(core, 12000.0, 13800.0, require_chron=True)
    assert res["farm_relaxed"] is True
    assert res["farm_strict"] is True
    assert res["chron"]["chron_ok"] is True
    print("PASS: test_planted_neolithic_detection")


def test_wild_grass_without_weeds_rejected():
    # High Cerealia-type wild grass (3%) with ZERO anthropogenic weeds -> must NOT trigger RELAXED or STRICT
    samples = [
        {"depth": 100.0, "age_raw": 13000, "age_cal": 13000.0, "age_type": "Calibrated radiocarbon years BP", "is_14c": False, "terrestrial_sum": 400, "is_pct_units": False, "crop_val": 12.0, "crop_pct": 3.0, "weed_pct": 0.0, "plantago_lan_pct": 0.0, "ap_pct": 30.0, "crop_taxa": {"Poaceae (Cerealia-type)": 12}, "weed_taxa": {}},
        {"depth": 110.0, "age_raw": 13400, "age_cal": 13400.0, "age_type": "Calibrated radiocarbon years BP", "is_14c": False, "terrestrial_sum": 400, "is_pct_units": False, "crop_val": 10.0, "crop_pct": 2.5, "weed_pct": 0.25, "plantago_lan_pct": 0.0, "ap_pct": 28.0, "crop_taxa": {"Poaceae (Cerealia-type)": 10}, "weed_taxa": {}},
    ]
    controls = [{"depth": 80.0, "age": 11500}, {"depth": 150.0, "age": 15000}]
    core = make_synthetic_core(samples, controls)
    res = iaf.evaluate_window(core, 12000.0, 15000.0, require_chron=True)
    assert res["farm_relaxed"] is False
    assert res["farm_strict"] is False
    print("PASS: test_wild_grass_without_weeds_rejected")


def test_unbracketed_or_inverted_chronology_rejected():
    # Same strong farming package, but only 1 shallow date (unbracketed extrapolation!)
    samples = [
        {"depth": 100.0, "age_raw": 12600, "age_cal": 12600.0, "age_type": "Calibrated radiocarbon years BP", "is_14c": False, "terrestrial_sum": 400, "is_pct_units": False, "crop_val": 6.0, "crop_pct": 1.5, "weed_pct": 1.2, "plantago_lan_pct": 1.0, "ap_pct": 55.0, "crop_taxa": {}, "weed_taxa": {}},
        {"depth": 120.0, "age_raw": 13000, "age_cal": 13000.0, "age_type": "Calibrated radiocarbon years BP", "is_14c": False, "terrestrial_sum": 400, "is_pct_units": False, "crop_val": 5.0, "crop_pct": 1.25, "weed_pct": 1.0, "plantago_lan_pct": 0.75, "ap_pct": 58.0, "crop_taxa": {}, "weed_taxa": {}},
        {"depth": 160.0, "age_raw": 14200, "age_cal": 14200.0, "age_type": "Calibrated radiocarbon years BP", "is_14c": False, "terrestrial_sum": 400, "is_pct_units": False, "crop_val": 0.0, "crop_pct": 0.0, "weed_pct": 0.0, "plantago_lan_pct": 0.0, "ap_pct": 80.0, "crop_taxa": {}, "weed_taxa": {}},
    ]
    controls = [{"depth": 50.0, "age": 5000}]
    core = make_synthetic_core(samples, controls)
    res = iaf.evaluate_window(core, 12000.0, 13800.0, require_chron=True)
    assert res["farm_strict_unfiltered"] is True
    assert res["farm_strict"] is False
    print("PASS: test_unbracketed_or_inverted_chronology_rejected")


if __name__ == "__main__":
    test_planted_neolithic_detection()
    test_wild_grass_without_weeds_rejected()
    test_unbracketed_or_inverted_chronology_rejected()
    print("ALL 3 ICE-AGE-FARMING UNIT TESTS PASSED!")
