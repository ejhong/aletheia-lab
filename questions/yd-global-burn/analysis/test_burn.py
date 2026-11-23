#!/usr/bin/env python3
"""Unit tests for questions/yd-global-burn/analysis/burn.py.

Verifies sign conventions, gap masking, physical mass balance, deterministic GCD3 unit
selection, log-Z standardization, planted peak recovery, tie ranking, and every verdict branch.
"""

from __future__ import annotations

import math
import unittest

import numpy as np

import burn


class TestArchiveA(unittest.TestCase):
    def test_burning_pulse_sign_and_rank1(self):
        # Synthetic age grid every 100 yr from 11,050 to 22,550 BP (deglacial transect)
        ages = np.arange(11050.0, 22650.0, 100.0)
        co2 = np.full_like(ages, 240.0)
        d13 = np.full_like(ages, -6.5)

        # Forward-in-time burning pulse entering k=0 [12650, 12950):
        # For ages <= 12750 (younger than 12850), CO2 jumps +12 ppm and d13C drops -0.4 permil
        younger = ages <= 12750.0
        co2[younger] += 12.0
        d13[younger] -= 0.4

        burn_map, d13_map, _ = burn.compute_taylor_windows(
            ages, co2, d13, spans=((11150.0, 22250.0),)
        )
        self.assertIn(0, burn_map)
        self.assertAlmostEqual(burn_map[0], 12.0 * 0.4, places=6)
        self.assertAlmostEqual(d13_map[0], 0.4, places=6)

        r_burn = burn.score_rank(burn_map, 0)
        r_d13 = burn.score_rank(d13_map, 0)
        self.assertEqual(r_burn["rank"], 1)
        self.assertEqual(r_d13["rank"], 1)
        self.assertTrue(r_burn["in_top1"])

    def test_ocean_warming_co2_rise_without_d13_drop_gives_zero_burn(self):
        ages = np.arange(11050.0, 22650.0, 100.0)
        co2 = np.full_like(ages, 240.0)
        d13 = np.full_like(ages, -6.5)

        # Forward CO2 rise (+15 ppm) with flat/slightly rising d13C (+0.1 permil): not terrestrial burning
        younger = ages <= 12750.0
        co2[younger] += 15.0
        d13[younger] += 0.1

        burn_map, d13_map, _ = burn.compute_taylor_windows(
            ages, co2, d13, spans=((11150.0, 22250.0),)
        )
        self.assertEqual(burn_map[0], 0.0)
        self.assertLessEqual(d13_map[0], 0.0)

    def test_reverse_direction_cooling_gives_zero_burn(self):
        ages = np.arange(11050.0, 22650.0, 100.0)
        co2 = np.full_like(ages, 240.0)
        d13 = np.full_like(ages, -6.5)

        # Forward CO2 drop (-15 ppm) and d13C rise (+0.3 permil)
        younger = ages <= 12750.0
        co2[younger] -= 15.0
        d13[younger] += 0.3

        burn_map, _, _ = burn.compute_taylor_windows(
            ages, co2, d13, spans=((11150.0, 22250.0),)
        )
        self.assertEqual(burn_map[0], 0.0)

    def test_gap_masking_across_12kyr_gap(self):
        ages = np.concatenate([
            np.arange(11050.0, 22450.0, 100.0),
            np.arange(35050.0, 46550.0, 100.0),
        ])
        vals = np.linspace(200.0, 260.0, len(ages))
        grid = np.array([15000.0, 25000.0, 30000.0, 35050.0, 40000.0])
        out = burn.interp_with_gap(ages, vals, grid, max_gap=500.0)
        self.assertTrue(math.isfinite(out[0]))
        self.assertTrue(math.isnan(out[1]))
        self.assertTrue(math.isnan(out[2]))
        self.assertTrue(math.isfinite(out[3]))
        self.assertTrue(math.isfinite(out[4]))

    def test_wais_planted_rise_rank1(self):
        ages = np.arange(10000.0, 22500.0, 25.0)
        co2 = np.full_like(ages, 240.0)
        co2[ages < 12800.0] += 10.0
        w_map = burn.compute_wais_windows(ages, co2, step=100.0)
        r = burn.score_rank(w_map, 0)
        self.assertEqual(r["rank"], 1)
        self.assertAlmostEqual(w_map[0], 10.0, places=5)

    def test_physical_mass_balance_exact_inversion(self):
        co2_0 = 240.0
        d0 = -6.5
        d_bio = -25.0
        m0 = 2.12 * co2_0
        dc_true = 25.0
        d1 = (m0 * d0 + dc_true * d_bio) / (m0 + dc_true)
        res = burn.physical_mass_balance(co2_0, d0, d1, d_bio=d_bio)
        self.assertAlmostEqual(res["delta_c_air_gtc"], dc_true, places=2)
        self.assertAlmostEqual(res["emitted_af50_gtc"], 50.0, places=2)
        self.assertAlmostEqual(res["emitted_af25_gtc"], 100.0, places=2)


class TestArchiveB(unittest.TestCase):
    def test_deterministic_unit_selection(self):
        # Case 1: PREF_UNITS >= 50% -> choose PREF_UNITS even if tied
        rows = [
            ("s1", 1000.0, "10", 5.0),
            ("s2", 2000.0, "10", 7.0),
            ("s3", 3000.0, "2", 9.0),
            ("s4", 4000.0, "2", 11.0),
        ]
        u, ages, qtys = burn.select_site_unit(rows, pref_units="10")
        self.assertEqual(u, "10")
        self.assertEqual(len(ages), 2)

        # Case 2: PREF_UNITS < 50%, tie between units "10" and "2" -> lowest integer "2"
        rows2 = rows + [("s5", 5000.0, "99", 1.0)]
        u2, _, _ = burn.select_site_unit(rows2, pref_units="99")
        self.assertEqual(u2, "2")

        # Case 3: Duplicate (ID_SAMPLE, unit) averaged
        rows3 = [
            ("s1", 1000.0, "5", 2.0),
            ("s1", 1000.0, "5", 6.0),
            ("s2", 2000.0, "5", 10.0),
        ]
        u3, ages3, qtys3 = burn.select_site_unit(rows3, pref_units="5")
        self.assertEqual(u3, "5")
        self.assertEqual(len(ages3), 2)
        self.assertAlmostEqual(qtys3[0], 4.0)

    def test_standardize_site_and_planted_peak(self):
        ages = np.arange(1275.0, 14750.0, 50.0)
        # All zeros -> dropped
        self.assertIsNone(burn.standardize_site(ages, np.zeros_like(ages), 1250.0, 14750.0))
        # Constant positive -> dropped
        self.assertIsNone(burn.standardize_site(ages, np.ones_like(ages) * 3.0, 1250.0, 14750.0))

        # 12 synthetic sites with low noise + planted global spike in [12750, 12850) (inside k=0)
        rng = np.random.default_rng(123)
        std_sites = []
        for i in range(12):
            q = np.exp(rng.normal(0.0, 0.2, size=len(ages)))
            spike_mask = (ages >= 12750.0) & (ages < 12850.0)
            q[spike_mask] *= 20.0
            a_std, z_std = burn.standardize_site(ages, q, 1250.0, 14750.0)
            self.assertAlmostEqual(float(np.mean(z_std)), 0.0, places=6)
            self.assertAlmostEqual(float(np.std(z_std, ddof=0)), 1.0, places=6)
            std_sites.append({"id_site": str(i), "ages": a_std, "z": z_std})

        m = burn.compute_charcoal_metrics(std_sites)
        for key in ("E_mean", "F_peak", "E_100"):
            r = burn.score_rank(m[key], 0)
            self.assertEqual(r["rank"], 1, f"{key} failed to recover planted peak at rank 1")
            self.assertTrue(r["in_top1"])


class TestRankingAndVerdicts(unittest.TestCase):
    def test_rank_ties(self):
        mp = {0: 5.0, 1: 10.0, 2: 5.0, 3: 1.0, 4: 0.0}
        r = burn.score_rank(mp, 0)
        self.assertEqual(r["rank"], 2)
        self.assertEqual(r["ties"], 1)
        self.assertAlmostEqual(r["frac"], 3.0 / 5.0, places=6)

    def test_verdict_branches(self):
        t1 = {"in_top1": True, "in_top5": True}
        t5 = {"in_top1": False, "in_top5": True}
        no = {"in_top1": False, "in_top5": False}

        # Archive A
        self.assertEqual(burn.verdict_archive_a(t1, t5, no), "Exceptional")
        self.assertEqual(burn.verdict_archive_a(t1, no, t5), "Exceptional")
        self.assertEqual(burn.verdict_archive_a(t1, no, no), "Single-record only")
        self.assertEqual(burn.verdict_archive_a(t5, t5, no), "Unusual")
        self.assertEqual(burn.verdict_archive_a(no, t5, t5), "Unusual")
        self.assertEqual(burn.verdict_archive_a(no, t5, no), "Single-record only")
        self.assertEqual(burn.verdict_archive_a(no, no, no), "Not met")

        # Archive B
        self.assertEqual(burn.verdict_archive_b(t1, t1, no), "Exceptional")
        self.assertEqual(burn.verdict_archive_b(t1, t5, no), "Unusual")
        self.assertEqual(burn.verdict_archive_b(t5, t5, no), "Unusual")
        self.assertEqual(burn.verdict_archive_b(t1, no, no), "Not met")
        self.assertEqual(burn.verdict_archive_b(no, no, no), "Not met")

        # Joint
        self.assertEqual(burn.verdict_joint("Exceptional", "Exceptional"), "Strong support for global burning")
        self.assertEqual(burn.verdict_joint("Exceptional", "Unusual"), "Strong support for global burning")
        self.assertEqual(burn.verdict_joint("Unusual", "Exceptional"), "Strong support for global burning")
        self.assertEqual(burn.verdict_joint("Unusual", "Unusual"), "Partial / mixed")
        self.assertEqual(burn.verdict_joint("Exceptional", "Not met"), "Partial / mixed")
        self.assertEqual(burn.verdict_joint("Single-record only", "Not met"), "Partial / mixed")
        self.assertEqual(burn.verdict_joint("Not met", "Not met"), "Not supported")


if __name__ == "__main__":
    unittest.main(verbosity=2)
