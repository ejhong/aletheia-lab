#!/usr/bin/env python3
"""Unit tests on made-up series. Run from questions/tunguska-calibration:  .venv/bin/python analysis/test_tunguska.py"""
import math
import sys
import unittest

sys.path.insert(0, "analysis")
import tunguska as t


class Tests(unittest.TestCase):
    def test_window_score_by_hand(self):
        s = {y: 1.0 for y in range(1880, 1930)}
        for i, y in enumerate(range(1880, 1930)):
            s[y] = math.exp(0.1 * (i % 3 - 1))           # logs cycle through -0.1, 0, +0.1
        s[1908] = math.exp(1.0)
        z = t.window_z(s, 1908)
        self.assertAlmostEqual(z, 1.0 / (1.4826 * 0.1), places=6)      # median 0, MAD 0.1
        self.assertAlmostEqual(t.window_z(s, 1907), z, places=6)       # 1908 is the second year of window 1907

    def test_background_needs_twenty_years(self):
        s = {y: 1.0 + 0.01 * (y % 5) for y in range(1900, 1919)}
        self.assertIsNone(t.window_z(s, 1908))

    def test_one_year_missing_uses_the_other(self):
        s = {y: math.exp(0.1 * (y % 3 - 1)) for y in range(1880, 1930)}
        del s[1909]
        self.assertIsNotNone(t.window_z(s, 1908))
        del s[1908]
        self.assertIsNone(t.window_z(s, 1908))

    def test_network_uses_the_same_sites_in_every_window(self):
        scores = {"a": {1906: 1.0, 1908: 3.0, 1910: 0.0}, "b": {1906: 2.0, 1908: 5.0}, "c": {1906: 9.0}}
        net, used = t.network(scores, 1908, 2)
        self.assertEqual(used, ["a", "b"])                      # c has no score in the target window
        self.assertEqual(net, {1906: 1.5, 1908: 4.0})           # 1910 dropped: b is missing there
        self.assertEqual(t.rank_of(net, 1908)["rank"], 1)
        self.assertEqual(t.network(scores, 1908, 3)[0], {})

    def test_windows_tile_without_overlap(self):
        s = t.starts(1908, 2)
        self.assertIn(1908, s)
        self.assertEqual(set(b - a for a, b in zip(s, s[1:])), {2})
        self.assertGreaterEqual(s[0], 1800)
        self.assertLessEqual(s[-1] + 1, 1990)
        self.assertEqual(len(s), 95)

    def test_verdict_words(self):
        r = lambda rank, n: {"rank": rank, "n": n, "fraction": round(rank / n, 4)}
        self.assertEqual(t.verdict(r(2, 55)), "exceptional")
        self.assertEqual(t.verdict(r(3, 55)), "elevated")
        self.assertEqual(t.verdict(r(5, 55)), "elevated")
        self.assertEqual(t.verdict(r(6, 55)), "ordinary")
        self.assertEqual(t.verdict(None), "not testable")

    def test_excess_is_in_typical_years(self):
        s = {y: 2.0 for y in range(1880, 1930)}
        s[1909] = 5.0
        self.assertEqual(t.excess({"neem_s1": s}), {"NEEM": 1.5})


if __name__ == "__main__":
    unittest.main()
