#!/usr/bin/env python3
"""Synthetic unit tests for #44 (flood-myths) spatial econometrics and geometry."""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_flood_myths import R_EARTH_KM, haversine_matrix_km, ols_with_cluster_and_conley


def test_haversine_known_distances():
    # Equator 1 degree longitude = ~111.195 km; pole-to-equator = pi/2 * R
    lats = np.array([0.0, 0.0, 90.0])
    lons = np.array([0.0, 1.0, 0.0])
    D = haversine_matrix_km(lats, lons)
    assert abs(D[0, 1] - math.radians(1.0) * R_EARTH_KM) < 0.05
    assert abs(D[0, 2] - (math.pi / 2.0) * R_EARTH_KM) < 0.1


def test_conley_and_cluster_se_inflate_under_spatial_autocorrelation():
    rng = np.random.default_rng(123)
    # 10 tight spatial clusters of 20 societies each, sharing cluster-level shock
    n_cl, per_cl = 10, 20
    n = n_cl * per_cl
    lats, lons, clusters, x, y = [], [], [], [], []
    for c in range(n_cl):
        base_lat = -40.0 + c * 8.0
        base_lon = -100.0 + c * 20.0
        shock = rng.normal(0.0, 3.0)
        x_cl = rng.normal(0.0, 1.0)
        for _ in range(per_cl):
            lats.append(base_lat + rng.normal(0, 0.3))
            lons.append(base_lon + rng.normal(0, 0.3))
            clusters.append(f"fam_{c}")
            xi = x_cl + rng.normal(0, 0.2)
            x.append(xi)
            y.append(shock + rng.normal(0, 0.5))  # true beta = 0, strong cluster shock!
    X = np.column_stack([np.ones(n), np.array(x)])
    D = haversine_matrix_km(np.array(lats), np.array(lons))
    res = ols_with_cluster_and_conley(np.array(y), X, np.array(clusters), D, col_idx=1)
    assert res["se_cluster"] > res["se_ols"] * 1.8
    assert res["se_conley_500"] > res["se_ols"] * 1.8
    assert res["moran_i"] > 0.5


def test_ols_recovers_planted_signal():
    rng = np.random.default_rng(42)
    n = 300
    lats = rng.uniform(-50, 50, n)
    lons = rng.uniform(-170, 170, n)
    x = rng.normal(0, 1, n)
    y = 2.0 + 0.75 * x + rng.normal(0, 0.3, n)
    X = np.column_stack([np.ones(n), x])
    D = haversine_matrix_km(lats, lons)
    clusters = np.array([f"c{i % 30}" for i in range(n)])
    res = ols_with_cluster_and_conley(y, X, clusters, D, col_idx=1)
    assert abs(res["beta"] - 0.75) < 0.06
    assert res["p_cluster"] < 1e-10 and res["p_conley_1000"] < 1e-10


if __name__ == "__main__":
    for fn in [
        test_haversine_known_distances,
        test_conley_and_cluster_se_inflate_under_spatial_autocorrelation,
        test_ols_recovers_planted_signal,
    ]:
        fn()
        print("PASS:", fn.__name__)
    print("All 3 synthetic unit tests passed.")
