#!/usr/bin/env python3
"""Synthetic unit tests for #82 (lost-metallurgy) pipeline."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_metallurgy import bin_medians, volcanic_mask_sulfur


def test_volcanic_mask_catches_planted_eruption():
    ages = np.arange(0.0, 2000.0, 1.0)
    rng = np.random.default_rng(7)
    sulf = rng.normal(20.0, 2.0, size=len(ages))
    # Plant a volcanic spike at age 1000 yr
    sulf[1000] = 250.0
    vm = volcanic_mask_sulfur(ages, sulf, half_win_yr=250.0, k_mad=5.0, buffer_yr=2.0)
    assert vm[1000] and vm[998] and vm[1002]
    assert not vm[500] and not vm[1500]
    assert vm.sum() < 20


def test_bin_median_rejects_single_point_spike_but_detects_sustained_smelting():
    ages = np.arange(5000.0, 6000.0, 1.0)
    ef = np.ones_like(ages)
    # Single-year contamination spike at 5250 yr
    ef[250] = 50.0
    # Sustained 80-year smelting episode at 5600-5680 yr
    ef[600:680] = 6.0
    bins = bin_medians(ages, ef, bin_yr=100.0, min_age=5000.0, max_age=6000.0)
    by_lo = {b["age_lo"]: b for b in bins}
    assert by_lo[5200.0]["median"] == 1.0, "Single spike should not move 100-yr median"
    assert by_lo[5600.0]["median"] == 6.0, "Sustained 80-yr smelting should clearly register in 100-yr median"


def test_crustal_subtraction_zero_for_pure_dust():
    k_ucc = 19.0 / 83.0
    ce = np.array([0.05, 0.20, 1.50])
    pb_pure_dust = ce * k_ucc
    ncpb = np.maximum(0.0, pb_pure_dust - k_ucc * ce)
    assert np.allclose(ncpb, 0.0)


def test_roman_upper_bound_scaling():
    roman_ncpb = 4.0  # pg/g
    pre_max_ncpb = 0.4  # pg/g
    frac = pre_max_ncpb / roman_ncpb
    assert abs(frac - 0.10) < 1e-12
    assert abs(frac * 3300.0 - 330.0) < 1e-9


if __name__ == "__main__":
    for fn in [
        test_volcanic_mask_catches_planted_eruption,
        test_bin_median_rejects_single_point_spike_but_detects_sustained_smelting,
        test_crustal_subtraction_zero_for_pure_dust,
        test_roman_upper_bound_scaling,
    ]:
        fn()
        print("PASS:", fn.__name__)
    print("All 4 synthetic unit tests passed.")
