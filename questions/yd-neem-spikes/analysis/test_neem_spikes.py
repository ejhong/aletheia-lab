#!/usr/bin/env python3
"""Pre-lock synthetic recovery unit tests for neem_spikes.py (zero real data touched)."""

import numpy as np

from neem_spikes import LO, HI, ONSET, W, compute_yearly_stats, decide_verdict, summarize_windows


def _make_synthetic(mode: str, seed: int = 114) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    n_years = HI - LO
    per_yr = 30
    ages = np.repeat(np.arange(LO, HI), per_yr) + np.tile(np.linspace(0.01, 0.99, per_yr), n_years)
    vals = np.full(len(ages), 8.0) + rng.normal(0, 0.8, size=len(ages))

    # Background occasional wildfire plumes: 12% of years have a +55 ug/kg plume (so ~18 spike yrs / 150 yr)
    for y in range(LO, HI):
        i0 = (y - LO) * per_yr
        in_yd = (ONSET - W <= y < ONSET)
        if in_yd:
            if mode in {"steady_only", "denominator_masked"}:
                vals[i0 : i0 + per_yr] += 14.0  # baseline rises 8 -> 22 (~2.75x)
            if mode == "steady_only":
                # Same modest background fire rate (+55 ug/kg = 2.5x new baseline -> fails >5x, constant additive)
                if rng.random() < 0.12:
                    vals[i0 + 15] += 55.0
            elif mode == "denominator_masked":
                # Huge surge of +70 ug/kg plumes (50% of years!): 70+22=92 < 5*22=110 (looks like fewer >5x!),
                # YET additive >50 jumps to ~75/150 years!
                if rng.random() < 0.50:
                    vals[i0 + 15] += 70.0
            elif mode == "repeated_fires":
                # Repeated airburst fires: 40% of years get +160 ug/kg plume (>5x even if baseline unchanged)
                if rng.random() < 0.40:
                    vals[i0 + 15] += 160.0
        else:
            if rng.random() < 0.12:
                vals[i0 + 15] += 55.0
    return ages, np.clip(vals, 0.5, None)


def test_steady_not_spiky_recovery():
    ages, vals = _make_synthetic("steady_only", seed=1)
    ys = compute_yearly_stats(ages, vals, LO, HI)
    s = summarize_windows(ys)
    v = decide_verdict(s)
    assert v == "replicated_steady_not_spiky", f"Expected replicated_steady_not_spiky, got {v}: {s['window_after']} vs {s['window_before']}"
    print("PASS: test_steady_not_spiky_recovery")


def test_denominator_artifact_caught():
    ages, vals = _make_synthetic("denominator_masked", seed=2)
    ys = compute_yearly_stats(ages, vals, LO, HI)
    s = summarize_windows(ys)
    v = decide_verdict(s)
    assert v == "replicated_relative_but_additive_spikes_rise", f"Expected denominator artifact catch, got {v}"
    print("PASS: test_denominator_artifact_caught")


def test_repeated_fires_recovery():
    ages, vals = _make_synthetic("repeated_fires", seed=3)
    ys = compute_yearly_stats(ages, vals, LO, HI)
    s = summarize_windows(ys)
    v = decide_verdict(s)
    assert v == "failed_to_replicate_more_spikes", f"Expected failed_to_replicate_more_spikes, got {v}"
    print("PASS: test_repeated_fires_recovery")


if __name__ == "__main__":
    test_steady_not_spiky_recovery()
    test_denominator_artifact_caught()
    test_repeated_fires_recovery()
    print("ALL 3 SYNTHETIC PRE-LOCK TESTS PASSED.")
