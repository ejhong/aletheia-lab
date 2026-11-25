#!/usr/bin/env python3
"""Unit tests for the sub-meter Lake Huron & Western Baltic sonar wall detector (#143)."""
from __future__ import annotations

import math
import unittest

import numpy as np

from run_submeter_scan import (
    detect_baltic_slope_block,
    detect_huron_structures,
    inject_baltic_wall_slope,
    inject_huron_step_seam,
    inject_huron_wall,
    make_metric_bbox,
    utm33n_to_latlon,
)


class TestSubmeterDetector(unittest.TestCase):
    def test_utm33n_meckelnburg_bay_conversion(self):
        # Test2 origin is in Mecklenburg Bay near Blinkerwall (~54.17N, 11.36E)
        lat, lon = utm33n_to_latlon(262463.0, 6008889.0)
        self.assertAlmostEqual(lat, 54.173, places=2)
        self.assertAlmostEqual(lon, 11.360, places=2)

    def test_huron_recovers_50cm_wall_and_rejects_step_seam(self):
        rng = np.random.default_rng(143)
        z = (-15.0 + rng.normal(0.0, 0.04, (512, 512))).astype(np.float32)
        valid = np.ones_like(z, dtype=bool)
        bbox = make_metric_bbox(45.10, -83.25, 256.0)

        # Plant 60 m x 2.5 m x 0.50 m stone drive-lane at 38 deg
        z_wall, (wcx, wcy) = inject_huron_wall(z, valid, length_m=60.0, width_m=2.5, height_m=0.50, az_deg=38.0, px_m=0.5)
        res_w = detect_huron_structures(z_wall, bbox, [], px_m=0.5)
        unm = [c for c in res_w["candidates"] if c["unmasked"]]
        self.assertGreaterEqual(len(unm), 1)
        dist_m = math.hypot(unm[0]["px_centroid"][0] - wcx, unm[0]["px_centroid"][1] - wcy) * 0.5
        self.assertLess(dist_m, 10.0)
        self.assertGreater(unm[0]["length_m"], 45.0)

        # Plant 0.50 m one-sided step seam at same azimuth -> must NOT produce unmasked hit
        z_seam = inject_huron_step_seam(z, valid, step_m=0.50, az_deg=38.0, px_m=0.5)
        res_s = detect_huron_structures(z_seam, bbox, [], px_m=0.5)
        unm_s = [c for c in res_s["candidates"] if c["unmasked"]]
        self.assertEqual(len(unm_s), 0)

    def test_huron_detects_caribou_v_funnel_and_hollow_blind(self):
        rng = np.random.default_rng(7)
        z = (-20.0 + rng.normal(0.0, 0.03, (512, 512))).astype(np.float32)
        yy, xx = np.mgrid[0:512, 0:512]
        # Build a V-funnel of two 40 m x 2.5 m boulder walls converging near (256, 256) at 45 deg
        for az in (20.0, 65.0):
            rad = math.radians(az)
            vx, vy = math.sin(rad), -math.cos(rad)
            nx, ny = -vy, vx
            dx = (xx - 256.0) * 0.5
            dy = (yy - 256.0) * 0.5
            along = dx * vx + dy * vy
            across = dx * nx + dy * ny
            mask = (along >= 6.0) & (along <= 50.0)
            z += (0.55 * np.exp(-0.5 * (across / 1.1) ** 2) * mask).astype(np.float32)
        # Build a hollow stone hunting blind ring (diam ~18 m) centered at (120, 120)
        rr = np.hypot((xx - 120.0) * 0.5, (yy - 120.0) * 0.5)
        z += (0.55 * np.exp(-0.5 * ((rr - 9.0) / 1.1) ** 2)).astype(np.float32)

        bbox = make_metric_bbox(45.00, -83.20, 256.0)
        res = detect_huron_structures(z, bbox, [], px_m=0.5)
        self.assertGreaterEqual(len(res["v_funnels"]), 1)
        self.assertGreaterEqual(len(res["rings"]), 1)

    def test_baltic_temporal_persistence_rejects_transient_trawl_keeps_wall(self):
        rng = np.random.default_rng(99)
        s24 = rng.normal(25.0, 4.0, (512, 512)).clip(0, 255).astype(np.float32)
        s25 = rng.normal(25.0, 4.0, (512, 512)).clip(0, 255).astype(np.float32)
        valid = np.ones((512, 512), dtype=bool)

        # Transient 2024-only trawl scar at 30 deg -> dropped by min(s24, s25)
        s24_tr, _ = inject_baltic_wall_slope(s24, valid, 80.0, 2.5, 80.0, 30.0, 0.5)
        sp_tr = np.minimum(s24_tr, s25)
        r_tr = detect_baltic_slope_block(sp_tr, valid, 225000.0, 6055000.0, 0.5, [], mode="persist_50cm")
        self.assertEqual(sum(1 for c in r_tr["candidates"] if c["unmasked"]), 0)

        # Persistent 2024 & 2025 stone wall at 55 deg -> recovered!
        s24_w, (wcx, wcy) = inject_baltic_wall_slope(s24, valid, 60.0, 2.5, 70.0, 55.0, 0.5)
        s25_w, _ = inject_baltic_wall_slope(s25, valid, 60.0, 2.5, 70.0, 55.0, 0.5)
        sp_w = np.minimum(s24_w, s25_w)
        r_w = detect_baltic_slope_block(sp_w, valid, 225000.0, 6055000.0, 0.5, [], mode="persist_50cm")
        unm = [c for c in r_w["candidates"] if c["unmasked"]]
        self.assertGreaterEqual(len(unm), 1)
        dist_m = math.hypot(unm[0]["px_centroid"][0] - wcx, unm[0]["px_centroid"][1] - wcy) * 0.5
        self.assertLess(dist_m, 10.0)


if __name__ == "__main__":
    unittest.main()
