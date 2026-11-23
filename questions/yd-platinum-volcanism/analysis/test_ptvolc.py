#!/usr/bin/env python3
"""Unit tests for questions/yd-platinum-volcanism/analysis/ptvolc.py."""

from __future__ import annotations

import unittest
import numpy as np
import ptvolc


class TestPtVolc(unittest.TestCase):
    def test_interp_depth_to_age(self):
        d = np.array([1700.0, 1710.0, 1720.0])
        a = np.array([12400.0, 12700.0, 13000.0])
        age, br = ptvolc.interp_depth_to_age(d, a, 1712.5)
        self.assertAlmostEqual(age, 12775.0, places=5)
        self.assertEqual(br["d_lo"], 1710.0)
        self.assertEqual(br["d_hi"], 1720.0)

    def test_step_changepoint_cooling_and_dust(self):
        d = np.arange(1700.0, 1730.0, 1.0)
        # Warm deeper (>1715: -36), cold shallower (<=1715: -41)
        o18 = np.where(d > 1715.0, -36.0, -41.0)
        cp = ptvolc.step_changepoint(d, o18, 1700.0, 1730.0, shallower_higher=False)
        self.assertAlmostEqual(cp["split_depth_m"], 1715.5, places=4)
        # Dusty shallower (<=1714: 4.5), clean deeper (>1714: 2.0)
        ca = np.where(d <= 1714.0, 4.5, 2.0)
        cp_ca = ptvolc.step_changepoint(d, ca, 1700.0, 1730.0, shallower_higher=True)
        self.assertAlmostEqual(cp_ca["split_depth_m"], 1714.5, places=4)

    def test_cooling_init_depth(self):
        d = np.arange(1700.0, 1726.0, 1.0)
        o18 = np.full_like(d, -36.0)
        o18[d >= 1717.0] += np.linspace(-0.2, 0.2, int((d >= 1717.0).sum()))
        o18[d <= 1714.0] = -39.0
        res = ptvolc.cooling_init_depth(d, o18, base_lo=1717.0, base_hi=1725.0)
        self.assertAlmostEqual(res["init_depth_m"], 1714.0, places=4)

    def test_volcanic_window_sum_and_gap(self):
        ages = np.array([12950.0, 12980.0, 18000.0, 30000.0])
        weights = np.array([50.0, 60.0, 500.0, 10.0])
        res = ptvolc.score_volcanic_windows(ages, weights, gap=(16500.0, 24500.0), target_k=0)
        self.assertAlmostEqual(res["value"], 110.0, places=4)
        self.assertEqual(res["count"], 2)
        self.assertEqual(res["rank"], 1)
        self.assertTrue(res["in_top5"])

    def test_mc_detects_planted_volcanic_trigger(self):
        onsets = [15000.0, 20000.0, 25000.0, 30000.0, 35000.0, 40000.0]
        # Plant a huge eruption 20 yr before every onset
        ages = np.array([t + 20.0 for t in onsets] + [12000.0, 45000.0])
        deps = np.array([200.0] * len(onsets) + [10.0, 10.0])
        mc = ptvolc.volcanic_cooling_mc(ages, deps, onsets, pre_window=50.0, n_iter=2000, seed=76)
        self.assertLess(mc["p_value"], 0.005)

    def test_verdict_branches(self):
        self.assertEqual(ptvolc.verdict_platinum(12900.0, 1712.0, 1712.0, 1712.0), "Consistent with trigger")
        self.assertEqual(ptvolc.verdict_platinum(12840.0, 1714.0, 1713.5, 1713.0), "Post-dates cooling onset (cannot be the initial trigger)")
        self.assertEqual(ptvolc.verdict_platinum(12883.0, 1712.0, 1712.0, 1712.0), "Ambiguous / within uncertainty")
        self.assertEqual(ptvolc.verdict_volcanism(True, True), "Unusually strong volcanic cluster")
        self.assertEqual(ptvolc.verdict_volcanism(True, False), "Elevated in one archive only")
        self.assertEqual(ptvolc.verdict_volcanism(False, False), "Ordinary background volcanism")


if __name__ == "__main__":
    unittest.main(verbosity=2)
