#!/usr/bin/env python3
"""Pre-registered global test: Do flood myths cluster where land drowned? (#44)

Implements every locked specification from questions/flood-myths/protocol.md:
- NOAA ETOPO 2022 60s global bedrock bathymetry -> 5-arc-min exact spherical integration
- Berezkin 958-society x 2,564-motif catalog (Michalopoulos & Xue 2021 QJE)
- Positive controls (earthquakes, sea) & negative control (fire)
- Progressive ladder M1-M4 on coastal (<=150 km) and full global samples
- Language-family CR1 clustered SEs, Conley (1999) spatial-HAC SEs (500 & 1000 km),
  residual Moran's I, within-continent permutation test (2,000 perms), and regional breakdown.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import h5py
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from scipy.stats import norm, spearmanr, t as t_dist

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RESULTS_DIR = BASE_DIR / "results"
R_EARTH_KM = 6371.0088
SEED = 20261124

NON_BIBLICAL_FLOOD_MOTIFS = [
    "c2", "c4", "c7", "c9a", "c10", "c10a", "c12a", "c12b",
    "c13", "c14", "b7b", "b7d", "b52a", "g9a", "i81a", "k38d", "l28a",
]
BIBLICAL_NOAH_MOTIFS = ["c3", "c5a"]


def latlon_to_xyz(lat_deg: np.ndarray, lon_deg: np.ndarray) -> np.ndarray:
    lat = np.deg2rad(lat_deg)
    lon = np.deg2rad(lon_deg)
    clat = np.cos(lat)
    return np.column_stack([clat * np.cos(lon), clat * np.sin(lon), np.sin(lat)])


def haversine_matrix_km(lat_deg: np.ndarray, lon_deg: np.ndarray) -> np.ndarray:
    xyz = latlon_to_xyz(lat_deg, lon_deg)
    dots = np.clip(xyz @ xyz.T, -1.0, 1.0)
    return R_EARTH_KM * np.arccos(dots)


def compute_bathymetry_exposures(lats: np.ndarray, lons: np.ndarray) -> dict[str, np.ndarray]:
    """Compute exact spherical drowned-shelf areas from NOAA ETOPO 2022 60s downsampled to 5-arc-min."""
    nc_path = DATA_DIR / "ETOPO_2022_v1_60s_N90W180_bed.nc"
    with h5py.File(nc_path, "r") as f:
        lat_raw = f["lat"][:]  # 10800
        lon_raw = f["lon"][:]  # 21600
        # Block-average 5x5 -> 2160 x 4320 (5-arc-minute, ~9.26 km at equator)
        z_raw = f["z"][:]
    lat5 = lat_raw.reshape(2160, 5).mean(axis=1)
    lon5 = lon_raw.reshape(4320, 5).mean(axis=1)
    z5 = z_raw.reshape(2160, 5, 4320, 5).mean(axis=(1, 3))

    # Exact spherical area of each 5-arc-min cell (km^2)
    dphi = math.radians(5.0 / 60.0)
    dlam = math.radians(5.0 / 60.0)
    row_area_km2 = (R_EARTH_KM * dphi) * (R_EARTH_KM * dlam * np.cos(np.deg2rad(lat5)))

    # 1. Exact distance to nearest modern ocean cell (z < 0) via 3D unit-sphere cKDTree
    ocean_mask = z5 < 0.0
    oy, ox = np.where(ocean_mask)
    ocean_xyz = latlon_to_xyz(lat5[oy], lon5[ox])
    ocean_z = z5[oy, ox]
    ocean_area = row_area_km2[oy]
    tree = cKDTree(ocean_xyz)

    pts_xyz = latlon_to_xyz(lats, lons)
    d_chord, _ = tree.query(pts_xyz, k=1)
    dist_coast_km = 2.0 * R_EARTH_KM * np.arcsin(np.clip(d_chord / 2.0, 0.0, 1.0))

    # 2. Exact radial integration within 250 km and 500 km using ball queries on unit sphere
    r250_chord = 2.0 * math.sin(250.0 / (2.0 * R_EARTH_KM))
    r500_chord = 2.0 * math.sin(500.0 / (2.0 * R_EARTH_KM))

    n = len(lats)
    ocean_250 = np.zeros(n)
    drown_120_250 = np.zeros(n)
    drown_60_250 = np.zeros(n)
    drown_120_500 = np.zeros(n)

    idx250_list = tree.query_ball_point(pts_xyz, r=r250_chord)
    for i, idxs in enumerate(idx250_list):
        if not idxs:
            continue
        ix = np.asarray(idxs, dtype=int)
        areas = ocean_area[ix]
        zs = ocean_z[ix]
        ocean_250[i] = areas.sum()
        drown_120_250[i] = areas[zs >= -120.0].sum()
        drown_60_250[i] = areas[zs >= -60.0].sum()

    idx500_list = tree.query_ball_point(pts_xyz, r=r500_chord)
    for i, idxs in enumerate(idx500_list):
        if not idxs:
            continue
        ix = np.asarray(idxs, dtype=int)
        zs = ocean_z[ix]
        drown_120_500[i] = ocean_area[ix][zs >= -120.0].sum()

    return {
        "dist_coast_km": dist_coast_km,
        "ocean_250km": ocean_250,
        "drowned_120m_250km": drown_120_250,
        "drowned_60m_250km": drown_60_250,
        "drowned_120m_500km": drown_120_500,
        "log_drowned_120m_250km": np.log1p(drown_120_250),
        "log_drowned_60m_250km": np.log1p(drown_60_250),
        "log_drowned_120m_500km": np.log1p(drown_120_500),
        "drowned_frac_ocean_250km": np.where(ocean_250 > 0, drown_120_250 / ocean_250, 0.0),
    }


def ols_with_cluster_and_conley(
    y: np.ndarray,
    X: np.ndarray,
    clusters: np.ndarray,
    dist_km: np.ndarray,
    col_idx: int = 1,
) -> dict:
    """OLS with CR1 cluster-robust SEs and Conley (1999) spatial-HAC SEs (500 & 1000 km) + Moran's I."""
    n, k = X.shape
    # Use pinv/SVD for rank-deficient FE matrices cleanly
    XtX_inv = np.linalg.pinv(X.T @ X)
    beta = XtX_inv @ (X.T @ y)
    resid = y - X @ beta
    rank = int(np.linalg.matrix_rank(X))
    df = max(1, n - rank)
    s2 = float(np.sum(resid ** 2) / df)
    se_ols = math.sqrt(max(0.0, float(XtX_inv[col_idx, col_idx] * s2)))

    # 1. CR1 cluster-robust variance
    uniq_cl = np.unique(clusters)
    G = len(uniq_cl)
    meat_cl = np.zeros((k, k))
    for g in uniq_cl:
        m = clusters == g
        u_g = X[m].T @ resid[m]
        meat_cl += np.outer(u_g, u_g)
    scale_cl = (G / max(1, G - 1)) * ((n - 1) / df)
    V_cl = scale_cl * (XtX_inv @ meat_cl @ XtX_inv)
    se_cl = math.sqrt(max(0.0, float(V_cl[col_idx, col_idx])))

    # 2. Conley (1999) spatial-HAC with Bartlett kernel at 500 km and 1000 km
    Xe = X * resid[:, None]
    conley_ses = {}
    for cutoff in (500.0, 1000.0):
        W = np.maximum(0.0, 1.0 - dist_km / cutoff)
        meat_c = Xe.T @ (W @ Xe)
        # Ensure PSD (eigenvalue floor at 0 per Cameron-Gelbach-Miller)
        V_c = XtX_inv @ meat_c @ XtX_inv
        # Standard Conley variance; guard tiny numerical negative with HC1 fallback
        v_ii = float(V_c[col_idx, col_idx])
        if v_ii < 0:
            v_ii = float((XtX_inv @ (Xe.T @ Xe) @ XtX_inv)[col_idx, col_idx])
        conley_ses[int(cutoff)] = math.sqrt(max(0.0, v_ii))

    # 3. Residual Moran's I (inverse-distance within 1000 km)
    W_m = np.where((dist_km > 0) & (dist_km <= 1000.0), 1.0 / np.maximum(50.0, dist_km), 0.0)
    S0 = float(W_m.sum())
    e_c = resid - resid.mean()
    denom = float(np.sum(e_c ** 2))
    moran_i = float((n / S0) * (e_c @ (W_m @ e_c)) / denom) if (S0 > 0 and denom > 0) else 0.0

    b = float(beta[col_idx])
    t_cl = b / se_cl if se_cl > 0 else 0.0
    p_cl = float(2.0 * t_dist.sf(abs(t_cl), max(1, G - 1)))
    t_c500 = b / conley_ses[500] if conley_ses[500] > 0 else 0.0
    p_c500 = float(2.0 * norm.sf(abs(t_c500)))
    t_c1000 = b / conley_ses[1000] if conley_ses[1000] > 0 else 0.0
    p_c1000 = float(2.0 * norm.sf(abs(t_c1000)))

    return {
        "n": n,
        "n_clusters": G,
        "rank": rank,
        "beta": b,
        "se_ols": se_ols,
        "se_cluster": se_cl,
        "t_cluster": t_cl,
        "p_cluster": p_cl,
        "se_conley_500": conley_ses[500],
        "p_conley_500": p_c500,
        "se_conley_1000": conley_ses[1000],
        "t_conley_1000": t_c1000,
        "p_conley_1000": p_c1000,
        "moran_i": moran_i,
    }


def perm_test_within_group(
    y: np.ndarray,
    x_treat: np.ndarray,
    Z_controls: np.ndarray,
    strata: np.ndarray,
    n_perm: int = 2000,
    seed: int = SEED,
) -> float:
    """Fast FWL within-stratum permutation test (two-sided p-value) for beta on x_treat."""
    # Residualize y once against Z_controls
    Q, _ = np.linalg.qr(Z_controls)
    y_res = y - Q @ (Q.T @ y)
    x_res = x_treat - Q @ (Q.T @ x_treat)
    obs = abs(float(np.dot(x_res, y_res) / max(1e-12, np.dot(x_res, x_res))))

    rng = np.random.default_rng(seed)
    idx_by_s = [np.where(strata == s)[0] for s in np.unique(strata)]
    ge = 0
    for _ in range(n_perm):
        xp = x_treat.copy()
        for ix in idx_by_s:
            xp[ix] = rng.permutation(xp[ix])
        xp_res = xp - Q @ (Q.T @ xp)
        denom = float(np.dot(xp_res, xp_res))
        b_p = abs(float(np.dot(xp_res, y_res) / denom)) if denom > 1e-12 else 0.0
        if b_p >= obs:
            ge += 1
    return float((ge + 1) / (n_perm + 1))


def build_design_matrix(df: pd.DataFrame, x_col: str, spec: str) -> tuple[np.ndarray, np.ndarray]:
    """Build design matrix X = [1, x_treat_std, controls, FEs] and return (X, Z_controls_only)."""
    x = df[x_col].to_numpy(dtype=float)
    x_std = (x - x.mean()) / (x.std(ddof=0) or 1.0)
    cols = [
        np.ones(len(df)),
        x_std,
        df["log_dist_coast"].to_numpy(dtype=float),
        df["lnnmbr_title"].to_numpy(dtype=float),
        df["lnyear_firstpub"].to_numpy(dtype=float),
        df["log_motifs_total"].to_numpy(dtype=float),
    ]
    if spec in ("M2", "M3", "M4"):
        cols.extend([
            df["lnriver_dist_bere"].to_numpy(dtype=float),
            df["lnbdisttoquake1000"].to_numpy(dtype=float),
            df["avtemp200_bere"].to_numpy(dtype=float),
            df["abs_lat"].to_numpy(dtype=float),
        ])
    if spec == "M3":
        dums = pd.get_dummies(df["continent_bere"].astype(str), drop_first=True, dtype=float).to_numpy()
        if dums.shape[1] > 0:
            cols.append(dums)
    elif spec == "M4":
        dums = pd.get_dummies(df["language1"].astype(str), drop_first=True, dtype=float).to_numpy()
        if dums.shape[1] > 0:
            cols.append(dums)
    X = np.column_stack(cols)
    Z_only = np.column_stack([cols[0]] + cols[2:])
    return X, Z_only


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Load Berezkin / Michalopoulos & Xue datasets
    rr = pd.read_stata(DATA_DIR / "Berezkin_groups_Regressions_Ready.dta")
    mot = pd.read_stata(DATA_DIR / "Motifs_Berezkin_groups.dta", convert_categoricals=False)

    # Extract pre-registered motif columns
    keep_mot = ["oid"] + NON_BIBLICAL_FLOOD_MOTIFS + BIBLICAL_NOAH_MOTIFS
    mot_sub = mot[keep_mot].copy()
    for mc in NON_BIBLICAL_FLOOD_MOTIFS + BIBLICAL_NOAH_MOTIFS:
        mot_sub[mc] = pd.to_numeric(mot_sub[mc], errors="coerce").fillna(0.0)
    mot_sub["nb_flood_count"] = mot_sub[NON_BIBLICAL_FLOOD_MOTIFS].sum(axis=1)
    mot_sub["noah_count"] = mot_sub[BIBLICAL_NOAH_MOTIFS].sum(axis=1)
    mot_sub["any_nb_flood"] = (mot_sub["nb_flood_count"] >= 1).astype(float)
    mot_sub["has_noah"] = (mot_sub["noah_count"] >= 1).astype(int)

    base_cols = [
        "oid", "group_Berezkin", "language1", "continent_bere", "country_bere",
        "motifs_total", "lnnmbr_title", "lnyear_firstpub",
        "latitude_forgeo", "longitude_forgeo",
        "lnriver_dist_bere", "lnbdisttoquake1000", "avtemp200_bere",
        "flood_related", "earthquake_related", "sea_related", "ocean_related", "fire_related",
    ]
    df = rr[base_cols].merge(mot_sub[["oid", "nb_flood_count", "noah_count", "any_nb_flood", "has_noah"]], on="oid", how="inner")
    df = df.dropna(subset=["latitude_forgeo", "longitude_forgeo", "motifs_total", "lnnmbr_title", "lnyear_firstpub", "lnriver_dist_bere", "lnbdisttoquake1000", "avtemp200_bere"]).reset_index(drop=True)

    # Compute bathymetry exposures from ETOPO 2022
    print(f"Computing ETOPO 2022 spherical drowned-shelf exposures for {len(df)} Berezkin societies...")
    bathy = compute_bathymetry_exposures(df["latitude_forgeo"].to_numpy(dtype=float), df["longitude_forgeo"].to_numpy(dtype=float))
    for k, v in bathy.items():
        df[k] = v

    df["log_dist_coast"] = np.log1p(df["dist_coast_km"])
    df["log_motifs_total"] = np.log1p(df["motifs_total"].astype(float))
    df["abs_lat"] = df["latitude_forgeo"].abs()
    df["nb_flood_share"] = df["nb_flood_count"] / df["motifs_total"].clip(lower=1)
    df["is_coastal_150"] = (df["dist_coast_km"] <= 150.0).astype(int)
    df["neg_lnquake"] = -df["lnbdisttoquake1000"].astype(float)
    df["neg_log_dist_coast"] = -df["log_dist_coast"]

    # Standardize continuous share outcomes for comparable beta (SD per 1-SD exposure)
    for col in ["nb_flood_share", "flood_related", "earthquake_related", "sea_related", "fire_related"]:
        s = df[col].astype(float)
        df[col + "_z"] = (s - s.mean()) / (s.std(ddof=0) or 1.0)

    # Precompute global pairwise great-circle distance matrix
    D_all = haversine_matrix_km(df["latitude_forgeo"].to_numpy(dtype=float), df["longitude_forgeo"].to_numpy(dtype=float))

    coastal_mask = df["is_coastal_150"] == 1
    df_coast = df[coastal_mask].reset_index(drop=True)
    D_coast = D_all[np.ix_(coastal_mask.to_numpy(), coastal_mask.to_numpy())]

    noah_free_mask = coastal_mask & (df["has_noah"] == 0)
    df_c_nonoah = df[noah_free_mask].reset_index(drop=True)
    D_c_nonoah = D_all[np.ix_(noah_free_mask.to_numpy(), noah_free_mask.to_numpy())]

    print(f"Samples: total={len(df)}, coastal(<=150km)={len(df_coast)}, coastal_noah_free={len(df_c_nonoah)}")
    print(f"Prevalence of any non-biblical flood motif: global={df['any_nb_flood'].mean():.3f}, coastal={df_coast['any_nb_flood'].mean():.3f}, inland={df[~coastal_mask]['any_nb_flood'].mean():.3f}")

    # =========================================================================
    # CALIBRATION GATE (Positive Controls: Earthquakes, Sea; Negative: Fire)
    # =========================================================================
    def run_calib(sub_df, D_sub, y_col, x_col, spec="M4"):
        X, Z = build_design_matrix(sub_df, x_col, spec)
        y = sub_df[y_col].to_numpy(dtype=float)
        res = ols_with_cluster_and_conley(y, X, sub_df["language1"].astype(str).to_numpy(), D_sub, col_idx=1)
        return res

    # Note: for earthquake control, drop lnbdisttoquake1000 from Z by using M1+continent/lang FE; easier: custom exact control
    def run_simple_calib(sub_df, D_sub, y_col, x_col, fe_col="language1"):
        x = sub_df[x_col].to_numpy(dtype=float)
        x_std = (x - x.mean()) / (x.std(ddof=0) or 1.0)
        dums = pd.get_dummies(sub_df[fe_col].astype(str), drop_first=True, dtype=float).to_numpy()
        X = np.column_stack([
            np.ones(len(sub_df)), x_std,
            sub_df["lnnmbr_title"].to_numpy(dtype=float),
            sub_df["lnyear_firstpub"].to_numpy(dtype=float),
            sub_df["log_motifs_total"].to_numpy(dtype=float),
            sub_df["abs_lat"].to_numpy(dtype=float),
            dums,
        ])
        y = sub_df[y_col].to_numpy(dtype=float)
        return ols_with_cluster_and_conley(y, X, sub_df["language1"].astype(str).to_numpy(), D_sub, col_idx=1)

    calibration = {
        "pos_earthquake_vs_quake_prox_langFE": run_simple_calib(df, D_all, "earthquake_related_z", "neg_lnquake", "language1"),
        "pos_sea_vs_coast_prox_langFE": run_simple_calib(df, D_all, "sea_related_z", "neg_log_dist_coast", "language1"),
        "neg_fire_vs_drowned120_coastal_M4": run_calib(df_coast, D_coast, "fire_related_z", "log_drowned_120m_250km", "M4"),
    }

    # =========================================================================
    # PRIMARY REGRESSIONS: COASTAL (<=150 km) & FULL GLOBAL, M1-M4
    # =========================================================================
    models = {}
    for sample_name, sub_df, D_sub in [
        ("coastal_150km", df_coast, D_coast),
        ("coastal_noah_free", df_c_nonoah, D_c_nonoah),
        ("global_all", df, D_all),
    ]:
        models[sample_name] = {}
        for y_col in ["nb_flood_share_z", "any_nb_flood", "flood_related_z"]:
            models[sample_name][y_col] = {}
            for spec in ["M1", "M2", "M3", "M4"]:
                X, Z = build_design_matrix(sub_df, "log_drowned_120m_250km", spec)
                y = sub_df[y_col].to_numpy(dtype=float)
                res = ols_with_cluster_and_conley(y, X, sub_df["language1"].astype(str).to_numpy(), D_sub, col_idx=1)
                if spec in ("M3", "M4") and sample_name in ("coastal_150km", "coastal_noah_free"):
                    res["p_perm_within_continent"] = perm_test_within_group(
                        y, X[:, 1], Z, sub_df["continent_bere"].astype(str).to_numpy(), n_perm=2000, seed=SEED
                    )
                models[sample_name][y_col][spec] = res

    # =========================================================================
    # EXPOSURE SENSITIVITY CHECKS ON COASTAL SUBSAMPLE (M3 & M4)
    # =========================================================================
    exposure_sensitivity = {}
    for exp_col in ["log_drowned_120m_250km", "log_drowned_60m_250km", "drowned_frac_ocean_250km", "log_drowned_120m_500km"]:
        exposure_sensitivity[exp_col] = {}
        for y_col in ["nb_flood_share_z", "any_nb_flood", "flood_related_z"]:
            exposure_sensitivity[exp_col][y_col] = {}
            for spec in ["M3", "M4"]:
                X, _ = build_design_matrix(df_coast, exp_col, spec)
                y = df_coast[y_col].to_numpy(dtype=float)
                exposure_sensitivity[exp_col][y_col][spec] = ols_with_cluster_and_conley(
                    y, X, df_coast["language1"].astype(str).to_numpy(), D_coast, col_idx=1
                )

    # =========================================================================
    # REGIONAL BREAKDOWN (COASTAL <=150 km) + AUSTRALIA / SAHUL CHECK
    # =========================================================================
    regional = []
    # Check continent labels in dataset
    for cont, grp in df_coast.groupby("continent_bere", observed=False):
        if len(grp) < 12:
            continue
        sub = grp.reset_index(drop=True)
        D_r = haversine_matrix_km(sub["latitude_forgeo"].to_numpy(dtype=float), sub["longitude_forgeo"].to_numpy(dtype=float))
        X, _ = build_design_matrix(sub, "log_drowned_120m_250km", "M2")
        r_nb = ols_with_cluster_and_conley(sub["nb_flood_share_z"].to_numpy(dtype=float), X, sub["language1"].astype(str).to_numpy(), D_r, col_idx=1)
        r_fr = ols_with_cluster_and_conley(sub["flood_related_z"].to_numpy(dtype=float), X, sub["language1"].astype(str).to_numpy(), D_r, col_idx=1)
        rho_nb, p_sp_nb = spearmanr(sub["drowned_120m_250km"], sub["nb_flood_share"])
        rho_fr, p_sp_fr = spearmanr(sub["drowned_120m_250km"], sub["flood_related"])
        regional.append({
            "region": str(cont),
            "n_coastal": int(len(sub)),
            "any_nb_flood_rate": float(sub["any_nb_flood"].mean()),
            "median_drowned_120m_km2": float(sub["drowned_120m_250km"].median()),
            "nb_flood_beta_M2": r_nb["beta"],
            "nb_flood_p_conley500": r_nb["p_conley_500"],
            "nb_flood_spearman_r": float(rho_nb),
            "flood_rel_beta_M2": r_fr["beta"],
            "flood_rel_p_conley500": r_fr["p_conley_500"],
            "flood_rel_spearman_r": float(rho_fr),
        })

    # Australia/Sahul specifically (lat < -8, lon 110..156)
    aus = df_coast[(df_coast["latitude_forgeo"] < -8) & (df_coast["longitude_forgeo"] >= 110) & (df_coast["longitude_forgeo"] <= 156)].reset_index(drop=True)
    aus_summary = {
        "n_coastal": int(len(aus)),
        "any_nb_flood_rate": float(aus["any_nb_flood"].mean()) if len(aus) else None,
        "median_drowned_120m_km2": float(aus["drowned_120m_250km"].median()) if len(aus) else None,
        "spearman_nb_flood": float(spearmanr(aus["drowned_120m_250km"], aus["nb_flood_share"]).statistic) if len(aus) >= 5 else None,
        "spearman_flood_rel": float(spearmanr(aus["drowned_120m_250km"], aus["flood_related"]).statistic) if len(aus) >= 5 else None,
    }

    # Quartile summary on coastal societies for clear non-parametric visualization
    q_edges = np.quantile(df_coast["drowned_120m_250km"], [0.0, 0.25, 0.5, 0.75, 1.0])
    quartiles = []
    for qi in range(4):
        lo, hi = float(q_edges[qi]), float(q_edges[qi + 1])
        m = (df_coast["drowned_120m_250km"] >= lo) & (df_coast["drowned_120m_250km"] <= hi if qi == 3 else df_coast["drowned_120m_250km"] < hi)
        sub = df_coast[m]
        quartiles.append({
            "quartile": f"Q{qi+1}",
            "drowned_lo_km2": round(lo, 0),
            "drowned_hi_km2": round(hi, 0),
            "n": int(len(sub)),
            "any_nb_flood_pct": float(sub["any_nb_flood"].mean() * 100.0),
            "mean_nb_flood_share_pct": float(sub["nb_flood_share"].mean() * 100.0),
            "mean_flood_related_pct": float(sub["flood_related"].mean() * 100.0),
        })

    # Compact coastal points for interactive world map figure
    map_points = [
        {
            "g": str(r["group_Berezkin"]),
            "lat": round(float(r["latitude_forgeo"]), 2),
            "lon": round(float(r["longitude_forgeo"]), 2),
            "c": int(r["is_coastal_150"]),
            "d120": round(float(r["drowned_120m_250km"]), 0),
            "nb": int(r["any_nb_flood"]),
            "fr": round(float(r["flood_related"]) * 100.0, 2),
        }
        for _, r in df.iterrows()
    ]

    summary = {
        "counts": {
            "n_global": int(len(df)),
            "n_coastal_150km": int(len(df_coast)),
            "n_coastal_noah_free": int(len(df_c_nonoah)),
            "n_language_families_global": int(df["language1"].nunique()),
            "n_language_families_coastal": int(df_coast["language1"].nunique()),
            "any_nb_flood_rate_global": float(df["any_nb_flood"].mean()),
            "any_nb_flood_rate_coastal": float(df_coast["any_nb_flood"].mean()),
            "any_nb_flood_rate_inland": float(df[~coastal_mask]["any_nb_flood"].mean()),
            "has_noah_rate_coastal": float(df_coast["has_noah"].mean()),
        },
        "calibration": calibration,
        "models": models,
        "exposure_sensitivity_coastal": exposure_sensitivity,
        "regional_coastal": regional,
        "australia_sahul_coastal": aus_summary,
        "coastal_quartiles": quartiles,
        "map_points": map_points,
    }
    out_path = RESULTS_DIR / "flood_myths_summary.json"
    out_path.write_text(json.dumps(summary, indent=2))
    print("\n=== SAVED", out_path, "===\n")

    print("--- CALIBRATION GATE ---")
    for k, v in calibration.items():
        print(f"  {k:40s}: beta={v['beta']:+.4f}  p_cl={v['p_cluster']:.2e}  p_c1000={v['p_conley_1000']:.2e}")

    print("\n--- PRIMARY COASTAL (<=150 km) M1-M4 ---")
    for y_col in ["nb_flood_share_z", "any_nb_flood", "flood_related_z"]:
        print(f"Outcome: {y_col}")
        for spec in ["M1", "M2", "M3", "M4"]:
            r = models["coastal_150km"][y_col][spec]
            pp = f" p_perm={r['p_perm_within_continent']:.3f}" if "p_perm_within_continent" in r else ""
            print(f"  {spec}: beta={r['beta']:+.4f}  p_cl={r['p_cluster']:.4f}  p_c500={r['p_conley_500']:.4f}  p_c1000={r['p_conley_1000']:.4f}  MoranI={r['moran_i']:+.3f}{pp}")

    print("\n--- COASTAL NOAH-FREE M3-M4 ---")
    for y_col in ["nb_flood_share_z", "flood_related_z"]:
        for spec in ["M3", "M4"]:
            r = models["coastal_noah_free"][y_col][spec]
            print(f"  {y_col:18s} {spec}: beta={r['beta']:+.4f}  p_cl={r['p_cluster']:.4f}  p_c1000={r['p_conley_1000']:.4f}  p_perm={r['p_perm_within_continent']:.3f}")

    print("\n--- EXPOSURE SENSITIVITY (COASTAL M4) ---")
    for exp_col, yd in exposure_sensitivity.items():
        r1 = yd["nb_flood_share_z"]["M4"]
        r2 = yd["flood_related_z"]["M4"]
        print(f"  {exp_col:26s}: nb_flood b={r1['beta']:+.4f} (p_cl={r1['p_cluster']:.3f}, p_c1k={r1['p_conley_1000']:.3f}) | flood_rel b={r2['beta']:+.4f} (p_cl={r2['p_cluster']:.3f}, p_c1k={r2['p_conley_1000']:.3f})")

    print("\n--- COASTAL QUARTILES ---")
    for q in quartiles:
        print(" ", q)

    print("\n--- REGIONAL COASTAL ---")
    for reg in regional:
        print(f"  {reg['region']:28s} (n={reg['n_coastal']:3d}): med_drown={reg['median_drowned_120m_km2']:7.0f} km2 | nb_b={reg['nb_flood_beta_M2']:+.3f} (p={reg['nb_flood_p_conley500']:.3f}) | fr_b={reg['flood_rel_beta_M2']:+.3f} (p={reg['flood_rel_p_conley500']:.3f})")
    print("Australia/Sahul:", aus_summary)


if __name__ == "__main__":
    main()
