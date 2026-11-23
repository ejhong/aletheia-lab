#!/usr/bin/env python3
"""Unit tests for questions/yd-cooling-shape/analysis/shape.py."""

from __future__ import annotations

import math
import unittest

import numpy as np

import shape


class TestShape(unittest.TestCase):
    def test_step_cooling_signs_and_pre_slope(self):
        # 20-yr bins from 10,010 to 15,010 b2k
        ages = np.arange(10010.0, 15010.0, 20.0)
        t = 12896.0
        # Flat warm plateau before onset (-36), abrupt step down to -42 after onset
        vals = np.where(ages >= t, -36.0, -42.0)
        m = shape.cooling_metrics_series(ages, vals, t)
        self.assertAlmostEqual(m["abrupt_60"], 6.0, places=5)
        self.assertAlmostEqual(m["amp"], 6.0, places=5)
        self.assertAlmostEqual(m["pre_slope"], 0.0, places=5)
        self.assertAlmostEqual(m["peak_rate_20"], 6.0, places=5)

    def test_gradual_precooling_gives_negative_pre_slope(self):
        ages = np.arange(10010.0, 15010.0, 20.0)
        t = 12896.0
        # Cooling forward in time before t: older = warmer (-34), approaching t = cooler (-38)
        # Slope = -2 permil per century
        vals = np.where(ages >= t, -38.0 + 2.0 * (ages - t) / 100.0, -42.0)
        m = shape.cooling_metrics_series(ages, vals, t)
        self.assertAlmostEqual(m["pre_slope"], -2.0, places=4)

    def test_dust_jump_positive_when_stadial_dustier(self):
        ages = np.arange(10005.0, 15005.0, 10.0)
        t = 12896.0
        # Pre-onset Ca = 10, stadial Ca = 100 -> ln(10) = 2.302585
        ca = np.where(ages >= t, 10.0, 100.0)
        m = shape.dust_metrics(ages, ca, t)
        self.assertAlmostEqual(m["dust_jump"], math.log(10.0), places=5)
        self.assertAlmostEqual(m["dust_abrupt_60"], math.log(10.0), places=5)

    def test_antarctic_bipolar_warming_vs_global_cooling(self):
        ages_bp = np.arange(10000.0, 15000.0, 40.0)
        t_b2k = 12896.0
        t_bp = t_b2k - 50.0
        # Standard bipolar seesaw: Antarctica warms by +1.5 C after t_bp (ages < t_bp)
        t_warm = np.where(ages_bp >= t_bp, -40.0, -38.5)
        m1 = shape.antarctic_bipolar_metric(ages_bp, t_warm, t_b2k)
        self.assertAlmostEqual(m1["delta_T_ant"], 1.5, places=5)
        self.assertAlmostEqual(m1["ant_cool"], -1.5, places=5)
        # Global impact winter: Antarctica cools by -2.0 C after t_bp
        t_cool = np.where(ages_bp >= t_bp, -40.0, -42.0)
        m2 = shape.antarctic_bipolar_metric(ages_bp, t_cool, t_b2k)
        self.assertAlmostEqual(m2["delta_T_ant"], -2.0, places=5)
        self.assertAlmostEqual(m2["ant_cool"], 2.0, places=5)

    def test_verdict_all_branches(self):
        self.assertEqual(shape.evaluate_verdict(True, True, True, False), "Distinct from natural coolings (catastrophic-trigger signature)")
        self.assertEqual(shape.evaluate_verdict(True, False, False, True), "Distinct from natural coolings (catastrophic-trigger signature)")
        self.assertEqual(shape.evaluate_verdict(False, True, False, True), "Distinct from natural coolings (catastrophic-trigger signature)")
        self.assertEqual(shape.evaluate_verdict(True, True, False, False), "Extreme case of a natural cooling")
        self.assertEqual(shape.evaluate_verdict(False, True, False, False), "Extreme case of a natural cooling")
        self.assertEqual(shape.evaluate_verdict(False, False, False, True), "Extreme case of a natural cooling")
        self.assertEqual(shape.evaluate_verdict(False, False, False, False), "Indistinguishable from natural coolings")


if __name__ == "__main__":
    unittest.main(verbosity=2)
