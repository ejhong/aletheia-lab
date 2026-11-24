#!/usr/bin/env python3
"""Synthetic unit tests for #84 (drowned-walls) before trusting NOAA BAG sonar outputs."""
import numpy as np
from run_drowned_walls import (
    detect_structures,
    inject_synthetic_step_seam,
    inject_synthetic_wall,
)


def make_flat_shelf(h: int = 512, w: int = 512, depth: float = -25.0) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(42)
    z = depth + rng.normal(0.0, 0.04, size=(h, w)).astype(np.float32)
    return z, np.ones((h, w), dtype=bool)


def test_planted_blinkerwall_detected():
    z, vm = make_flat_shelf()
    z_w, (cx, cy) = inject_synthetic_wall(z, vm, length_m=250.0, width_m=4.0, height_m=0.70, az_deg=42.0)
    res = detect_structures(z_w, (-71.50, 41.10, -71.49, 41.11))
    unm = [c for c in res["candidates"] if c["unmasked"]]
    assert len(unm) == 1, f"Expected 1 unmasked wall, got {len(unm)}: {res['candidates']}"
    assert 200.0 <= unm[0]["length_m"] <= 280.0
    assert abs(unm[0]["azimuth_deg"] - 42.0) <= 3.0
    print("PASS: test_planted_blinkerwall_detected")


def test_step_seam_rejected():
    z, vm = make_flat_shelf()
    z_s = inject_synthetic_step_seam(z, vm, step_m=0.70, az_deg=35.0)
    res = detect_structures(z_s, (-71.50, 41.10, -71.49, 41.11))
    unm = [c for c in res["candidates"] if c["unmasked"]]
    assert len(unm) == 0, f"Step seam slipped through unmasked: {unm}"
    print("PASS: test_step_seam_rejected")


def test_periodic_sandwaves_rejected():
    z, vm = make_flat_shelf()
    yy, xx = np.mgrid[0:512, 0:512]
    # Periodic 30 m wavelength sandwave train (amplitude 0.65 m) along 30 deg
    coord = (xx * np.cos(np.radians(30.0)) + yy * np.sin(np.radians(30.0))) * 2.0
    z_sw = z + (0.65 * np.sin(2.0 * np.pi * coord / 30.0)).astype(np.float32)
    res = detect_structures(z_sw, (-71.50, 41.10, -71.49, 41.11))
    unm = [c for c in res["candidates"] if c["unmasked"]]
    assert len(unm) == 0, f"Periodic sandwaves slipped through unmasked: {unm[:2]}"
    print("PASS: test_periodic_sandwaves_rejected")


def test_rectilinear_corner_detected():
    z, vm = make_flat_shelf()
    # Two orthogonal walls meeting near (256, 256) with small 6 px gap so they label as 2 segments
    yy, xx = np.mgrid[0:512, 0:512]
    w1 = 0.80 * np.exp(-0.5 * ((yy - 256) / 1.0) ** 2) * ((xx >= 262) & (xx <= 360))
    w2 = 0.80 * np.exp(-0.5 * ((xx - 256) / 1.0) ** 2) * ((yy >= 156) & (yy <= 250))
    z_c = z + (w1 + w2).astype(np.float32)
    res = detect_structures(z_c, (-71.50, 41.10, -71.49, 41.11))
    assert len(res["corners"]) >= 1, f"Expected >=1 rectilinear corner, got {res['corners']} (cands={res['candidates']})"
    print("PASS: test_rectilinear_corner_detected")


if __name__ == "__main__":
    test_planted_blinkerwall_detected()
    test_step_seam_rejected()
    test_periodic_sandwaves_rejected()
    test_rectilinear_corner_detected()
    print("ALL 4 DROWNED-WALLS UNIT TESTS PASSED!")
