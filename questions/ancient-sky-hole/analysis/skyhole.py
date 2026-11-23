#!/usr/bin/env python3
"""Pre-registered analysis of the empty southern patch in Ptolemy's Almagest.

Implements:
- Exact Vondrak, Capitaine & Wallace (2011, A&A 534, A22; 2012, A&A 541, C1)
  long-term precession (IAU SOFA / ERFA eraLtpequ & eraLtpecl).
- Linear Hipparcos proper motion propagation from J1991.25.
- Precession-invariant northern ecliptic calibration cap (beta > +30 deg).
- Model M1: Physical atmospheric-extinction visibility likelihood (Kasten & Young 1989
  airmass + Bennett 1982 refraction, primary k_V = 0.25 mag/airmass).
- Model M2: Joint profile likelihood over (epoch, latitude, k_V).
- Model M3: Pure geometric spherical cap (extinction-free cross-check).
- Model M4: Unconstrained free-pole 3D spherical cap diagnostic (off-track test).
- Spatial block bootstrap (B = 500 equal-area ~15 deg tiles), Leave-One-Constellation-Out
  (LOCO) jackknife, and full systematic variant envelope.

Usage:
  python3 analysis/skyhole.py --decoy   # Pre-lock verification on synthetic decoy sky
  python3 analysis/skyhole.py           # Post-lock full analysis -> results/
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"

DAS2R = math.pi / (180.0 * 3600.0)
D2PI = 2.0 * math.pi
EPS0_J2000 = 84381.406 * DAS2R  # IAU 2006 obliquity at J2000.0 (rad)
LAPSE_EPS = 0.002
BOOT_SEED = 20261123
N_BOOT = 500

# Vondrak, Capitaine & Wallace (2011, A&A 534, A22; 2012, A&A 541, C1)
# Exact IAU SOFA / ERFA eraLtpequ coefficients (North Celestial Pole in J2000 ICRS)
_XYPOL = np.array([
    [5453.282155, 0.4252841, -0.00037173, -0.000000152],
    [-73750.930350, -0.7675452, -0.00018725, 0.000000231],
], dtype=np.float64)

_XYPER = np.array([
    [256.75, -819.940624, 75004.344875, 81491.287984, 1558.515853],
    [708.15, -8444.676815, 624.033993, 787.163481, 7774.939698],
    [274.20, 2600.009459, 1251.136893, 1251.296102, -2219.534038],
    [241.45, 2755.175630, -1102.212834, -1257.950837, -2523.969396],
    [2309.00, -167.659835, -2660.664980, -2966.799730, 247.850422],
    [492.20, 871.855056, 699.291817, 639.744522, -846.485643],
    [396.10, 44.769698, 153.167220, 131.600209, -1393.124055],
    [288.90, -512.313065, -950.865637, -445.040117, 368.526116],
    [231.10, -819.415595, 499.754645, 584.522874, 749.045012],
    [1610.00, -538.071099, -145.188210, -89.756563, 444.704518],
    [620.00, -189.793622, 558.116553, 524.429630, 235.934465],
    [157.87, -402.922932, -23.923029, -13.549067, 374.049623],
    [220.30, 179.516345, -165.405086, -210.157124, -171.330180],
    [1200.00, -9.814756, 9.344131, -44.919798, -22.899655],
], dtype=np.float64)

# Exact IAU SOFA / ERFA eraLtpecl coefficients (North Ecliptic Pole in J2000 ICRS)
_PQPOL = np.array([
    [5851.607687, -0.1189000, -0.00028913, 0.000000101],
    [-1600.886300, 1.1689818, -0.00000020, -0.000000437],
], dtype=np.float64)

_PQPER = np.array([
    [708.15, -5486.751211, -684.661560, 667.666730, -5523.863691],
    [2309.00, -17.127623, 2446.283880, -2354.886252, -549.747450],
    [1620.00, -617.517403, 399.671049, -428.152441, -310.998056],
    [492.20, 413.442940, -356.652376, 376.202861, 421.535876],
    [1183.00, 78.614193, -186.387003, 184.778874, -36.776172],
    [622.00, -180.732815, -316.800070, 335.321713, -145.278396],
    [882.00, -87.676083, 198.296701, -185.138669, -34.744450],
    [547.00, 46.140315, 101.135679, -120.972830, 22.885731],
], dtype=np.float64)


def ltpequ(epj: float) -> np.ndarray:
    """North Celestial Pole unit vector in J2000 ICRS at Julian epoch epj."""
    t = (epj - 2000.0) / 100.0
    ang = (D2PI * t) / _XYPER[:, 0]
    c = np.cos(ang)
    s = np.sin(ang)
    x = float(np.sum(c * _XYPER[:, 1] + s * _XYPER[:, 3]))
    y = float(np.sum(c * _XYPER[:, 2] + s * _XYPER[:, 4]))
    w = 1.0
    for i in range(4):
        x += float(_XYPOL[0, i]) * w
        y += float(_XYPOL[1, i]) * w
        w *= t
    x *= DAS2R
    y *= DAS2R
    z2 = max(0.0, 1.0 - x * x - y * y)
    vec = np.array([x, y, math.sqrt(z2)], dtype=np.float64)
    return vec / np.linalg.norm(vec)


def ltpecl(epj: float) -> np.ndarray:
    """North Ecliptic Pole unit vector in J2000 ICRS at Julian epoch epj."""
    t = (epj - 2000.0) / 100.0
    ang = (D2PI * t) / _PQPER[:, 0]
    c = np.cos(ang)
    s = np.sin(ang)
    p = float(np.sum(c * _PQPER[:, 1] + s * _PQPER[:, 3]))
    q = float(np.sum(c * _PQPER[:, 2] + s * _PQPER[:, 4]))
    w = 1.0
    for i in range(4):
        p += float(_PQPOL[0, i]) * w
        q += float(_PQPOL[1, i]) * w
        w *= t
    p *= DAS2R
    q *= DAS2R
    w2 = math.sqrt(max(0.0, 1.0 - p * p - q * q))
    se = math.sin(EPS0_J2000)
    ce = math.cos(EPS0_J2000)
    vec = np.array([p, -q * ce - w2 * se, -q * se + w2 * ce], dtype=np.float64)
    return vec / np.linalg.norm(vec)


def format_year(epj: float) -> str:
    """Format astronomical year (t=0 -> 1 BCE, t=-2999 -> 3000 BCE, t=137 -> 137 CE)."""
    y = int(round(epj))
    if y <= 0:
        return f"{1 - y} BCE"
    return f"{y} CE"


def parse_vizier_tsv(path: Path) -> List[Dict[str, str]]:
    rows = []
    headers = None
    sep_seen = False
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = [p.strip() for p in line.rstrip("\n").split("\t")]
            if headers is None:
                headers = parts
                continue
            if not sep_seen:
                if all(set(p) <= {"-", " "} and "-" in p for p in parts if p):
                    sep_seen = True
                continue
            if len(parts) < len(headers):
                parts += [""] * (len(headers) - len(parts))
            rows.append(dict(zip(headers, parts)))
    return rows


def load_catalogs(v_max: float = 5.5) -> Dict[str, np.ndarray]:
    """Load Hipparcos, Ptolemy (Verbunt & van Gent 2012), and BSC5 names."""
    p_rows = parse_vizier_tsv(DATA_DIR / "ptolemy_verbunt2012.tsv")
    h_rows = parse_vizier_tsv(DATA_DIR / "hipparcos_v70.tsv")
    b_rows = parse_vizier_tsv(DATA_DIR / "bsc5.tsv")

    hd_to_name: Dict[int, str] = {}
    for r in b_rows:
        if r["HD"] and r["Name"]:
            try:
                hd_to_name[int(r["HD"])] = " ".join(r["Name"].split())
            except ValueError:
                pass

    # Map HIP -> Ptolemy records (a star can appear twice in 3 duplicate entries)
    ptol_all48 = set()
    ptol_infig = set()
    ptol_aratus = set()
    ptol_strict = set()
    ptol_cst: Dict[int, List[str]] = {}
    ptol_vp: Dict[int, str] = {}

    for r in p_rows:
        if not r["HIP"]:
            continue
        hid = int(r["HIP"])
        q = r["I"]
        fn = r["f_N"]
        cst = r["cst"]
        if q in {"1", "2", "3"}:
            ptol_all48.add(hid)
            ptol_cst.setdefault(hid, []).append(cst)
            ptol_vp[hid] = r["VP"] + r["q_VP"]
            if fn == "":
                ptol_infig.add(hid)
                if cst not in {"=Equ", "=CrA"}:
                    ptol_aratus.add(hid)
        if q in {"1", "2"}:
            ptol_strict.add(hid)

    hips, ras, decs, vmags, pmras, pmdes, bvs = [], [], [], [], [], [], []
    names, csts, vps = [], [], []
    y_all48, y_infig, y_aratus, y_strict = [], [], [], []

    for r in h_rows:
        try:
            hid = int(r["HIP"])
            ra = float(r["RAICRS"])
            de = float(r["DEICRS"])
            vmag = float(r["Vmag"])
        except ValueError:
            continue
        if vmag > v_max:
            continue
        pmra = float(r["pmRA"]) if r["pmRA"] else 0.0
        pmde = float(r["pmDE"]) if r["pmDE"] else 0.0
        bv = float(r["B-V"]) if r["B-V"] else 0.5
        hd = int(r["HD"]) if r["HD"] else None

        hips.append(hid)
        ras.append(ra)
        decs.append(de)
        vmags.append(vmag)
        pmras.append(pmra)
        pmdes.append(pmde)
        bvs.append(bv)
        names.append(hd_to_name.get(hd, f"HIP {hid}") if hd else f"HIP {hid}")
        csts.append(ptol_cst.get(hid, [""])[0])
        vps.append(ptol_vp.get(hid, ""))
        y_all48.append(1 if hid in ptol_all48 else 0)
        y_infig.append(1 if hid in ptol_infig else 0)
        y_aratus.append(1 if hid in ptol_aratus else 0)
        y_strict.append(1 if hid in ptol_strict else 0)

    ra_r = np.deg2rad(np.array(ras, dtype=np.float64))
    de_r = np.deg2rad(np.array(decs, dtype=np.float64))
    u0 = np.column_stack([np.cos(de_r) * np.cos(ra_r),
                          np.cos(de_r) * np.sin(ra_r),
                          np.sin(de_r)])
    e_ra = np.column_stack([-np.sin(ra_r), np.cos(ra_r), np.zeros_like(ra_r)])
    e_de = np.column_stack([-np.sin(de_r) * np.cos(ra_r),
                            -np.sin(de_r) * np.sin(ra_r),
                            np.cos(de_r)])
    # Proper motion velocity vector in rad/yr
    mas_to_rad = DAS2R / 1000.0
    pmra_arr = np.array(pmras, dtype=np.float64)
    pmde_arr = np.array(pmdes, dtype=np.float64)
    vel = (pmra_arr[:, None] * e_ra + pmde_arr[:, None] * e_de) * mas_to_rad

    # J2000 ecliptic coordinates (lambda, beta)
    ce, se = math.cos(EPS0_J2000), math.sin(EPS0_J2000)
    x_ecl = u0[:, 0]
    y_ecl = u0[:, 1] * ce + u0[:, 2] * se
    z_ecl = -u0[:, 1] * se + u0[:, 2] * ce
    ecl_lat = np.rad2deg(np.arcsin(np.clip(z_ecl, -1.0, 1.0)))
    ecl_lon = np.mod(np.rad2deg(np.arctan2(y_ecl, x_ecl)), 360.0)

    return {
        "hip": np.array(hips, dtype=np.int64),
        "ra": np.array(ras, dtype=np.float64),
        "dec": np.array(decs, dtype=np.float64),
        "vmag": np.array(vmags, dtype=np.float64),
        "pmra": pmra_arr,
        "pmde": pmde_arr,
        "bv": np.array(bvs, dtype=np.float64),
        "u0": u0,
        "vel": vel,
        "ecl_lat": ecl_lat,
        "ecl_lon": ecl_lon,
        "name": np.array(names, dtype=object),
        "cst": np.array(csts, dtype=object),
        "vp": np.array(vps, dtype=object),
        "all48": np.array(y_all48, dtype=np.int8),
        "in_figure": np.array(y_infig, dtype=np.int8),
        "aratus_core": np.array(y_aratus, dtype=np.int8),
        "strict_id": np.array(y_strict, dtype=np.int8),
    }


def star_declinations_at_epoch(u0: np.ndarray, vel: np.ndarray, epj: float) -> np.ndarray:
    """Exact declination in degrees for each star at Julian epoch epj."""
    dt = epj - 1991.25
    u = u0 + dt * vel
    u = u / np.linalg.norm(u, axis=1, keepdims=True)
    p_n = ltpequ(epj)
    return np.rad2deg(np.arcsin(np.clip(u @ p_n, -1.0, 1.0)))


def bennett_refraction_deg(h_true_deg: np.ndarray) -> np.ndarray:
    """Bennett (1982) atmospheric refraction in degrees for true altitude h_true_deg."""
    h = np.maximum(h_true_deg, -1.0)
    # Refraction in arcminutes: 1 / tan(h + 7.31 / (h + 4.4))
    arg = np.deg2rad(h + 7.31 / (h + 4.4))
    r_arcmin = 1.0 / np.tan(arg)
    return np.where(h_true_deg > -0.6, np.maximum(0.0, r_arcmin) / 60.0, 0.0)


def kasten_young_airmass(h_app_deg: np.ndarray) -> np.ndarray:
    """Kasten & Young (1989) optical airmass for apparent altitude h_app_deg > 0."""
    h = np.maximum(h_app_deg, 1e-4)
    denom = np.sin(np.deg2rad(h)) + 0.50572 * np.power(h + 6.07995, -1.6364)
    return 1.0 / denom


def fit_northern_completeness(vmag_north: np.ndarray, y_north: np.ndarray) -> Tuple[float, float]:
    """Fit logistic p_base(V) = 1 / (1 + exp((V - V50)/sV)) on beta > +30 deg by Newton-Raphson."""
    # Parameterize a = -V50 / sV, b = 1 / sV  so logit(p) = -(a + b * V) -> p = 1/(1 + exp(b*V + c))
    v = vmag_north.astype(np.float64)
    y = y_north.astype(np.float64)
    # Grid init then Newton refinement
    b, c = 2.8, -13.0
    for _ in range(30):
        z = np.clip(b * v + c, -30.0, 30.0)
        p = 1.0 / (1.0 + np.exp(z))
        # d/d(b,c) logL where logL = sum(y log p + (1-y) log(1-p))
        # d/dz logL = -(y - p)
        g_b = -np.sum((y - p) * v)
        g_c = -np.sum(y - p)
        w = p * (1.0 - p)
        h_bb = -np.sum(w * v * v)
        h_bc = -np.sum(w * v)
        h_cc = -np.sum(w)
        det = h_bb * h_cc - h_bc * h_bc
        if abs(det) < 1e-12:
            break
        db = (h_cc * g_b - h_bc * g_c) / det
        dc = (-h_bc * g_b + h_bb * g_c) / det
        b -= db
        c -= dc
        if abs(db) < 1e-9 and abs(dc) < 1e-9:
            break
    s_v = 1.0 / b
    v_50 = -c / b
    return float(v_50), float(s_v)


def compute_m1_probs(
    dec_deg: np.ndarray,
    vmag: np.ndarray,
    lat_deg: np.ndarray,
    v50: float,
    sv: float,
    k_v: float,
    eps: float = LAPSE_EPS,
) -> np.ndarray:
    """Compute inclusion probabilities P(y=1) for dec_deg (N,) x lat_deg (L,).

    Returns array of shape (L, N).
    """
    h_max = 90.0 - np.abs(lat_deg[:, None] - dec_deg[None, :])
    h_app = h_max + bennett_refraction_deg(h_max)
    vis = h_app > 0.0
    x_air = np.where(vis, kasten_young_airmass(np.where(vis, h_app, 1.0)), 100.0)
    v_eff = vmag[None, :] + k_v * (x_air - 1.0)
    z = np.clip((v_eff - v50) / sv, -40.0, 40.0)
    p_base = 1.0 / (1.0 + np.exp(z))
    p = np.where(vis, (1.0 - 2.0 * eps) * p_base + eps, eps)
    return p


def evaluate_m1_grid(
    u0: np.ndarray,
    vel: np.ndarray,
    vmag: np.ndarray,
    y: np.ndarray,
    epochs: np.ndarray,
    lats: np.ndarray,
    v50: float,
    sv: float,
    k_v: float,
    tile_ids: np.ndarray | None = None,
    n_tiles: int = 0,
) -> Tuple[np.ndarray, np.ndarray | None]:
    """Evaluate log-likelihood grid (E, L), optionally also per-tile LL (T, E, L)."""
    E, L = len(epochs), len(lats)
    ll_grid = np.empty((E, L), dtype=np.float64)
    tile_ll = np.zeros((n_tiles, E, L), dtype=np.float64) if tile_ids is not None else None
    yf = y.astype(np.float64)
    y1 = 1.0 - yf

    for ei, epj in enumerate(epochs):
        dec = star_declinations_at_epoch(u0, vel, float(epj))
        p = compute_m1_probs(dec, vmag, lats, v50, sv, k_v)
        # per-star LL: (L, N)
        ll_star = yf[None, :] * np.log(p) + y1[None, :] * np.log(1.0 - p)
        ll_grid[ei, :] = np.sum(ll_star, axis=1)
        if tile_ll is not None:
            for ti in range(n_tiles):
                mask = tile_ids == ti
                if np.any(mask):
                    tile_ll[ti, ei, :] = np.sum(ll_star[:, mask], axis=1)
    return ll_grid, tile_ll


def fit_m1_coarse_and_fine(
    u0: np.ndarray,
    vel: np.ndarray,
    vmag: np.ndarray,
    y: np.ndarray,
    v50: float,
    sv: float,
    k_v: float,
    epochs_coarse: np.ndarray,
    lats_coarse: np.ndarray,
) -> Dict:
    ll_c, _ = evaluate_m1_grid(u0, vel, vmag, y, epochs_coarse, lats_coarse, v50, sv, k_v)
    ei, li = np.unravel_index(int(np.argmax(ll_c)), ll_c.shape)
    t_c, lat_c = float(epochs_coarse[ei]), float(lats_coarse[li])

    t_lo = max(float(epochs_coarse[0]), t_c - 600.0)
    t_hi = min(float(epochs_coarse[-1]), t_c + 600.0)
    l_lo = max(float(lats_coarse[0]), lat_c - 4.0)
    l_hi = min(float(lats_coarse[-1]), lat_c + 4.0)
    epochs_f = np.arange(t_lo, t_hi + 0.1, 10.0)
    lats_f = np.arange(l_lo, l_hi + 1e-6, 0.2)
    ll_f, _ = evaluate_m1_grid(u0, vel, vmag, y, epochs_f, lats_f, v50, sv, k_v)
    fi, fli = np.unravel_index(int(np.argmax(ll_f)), ll_f.shape)
    ll_max = float(ll_f[fi, fli])

    # Naive star-level 68% (2*dLL <= 2.30) and 95% (2*dLL <= 5.99) profile CIs on coarse+fine
    d2_c = 2.0 * (ll_max - ll_c)
    in95_c = d2_c <= 5.991
    in68_c = d2_c <= 2.296
    e_idx95, l_idx95 = np.where(in95_c)
    e_idx68, l_idx68 = np.where(in68_c)

    return {
        "epoch": float(epochs_f[fi]),
        "lat": float(lats_f[fli]),
        "ll_max": ll_max,
        "k_v": float(k_v),
        "naive_68_epoch": [float(epochs_coarse[e_idx68.min()]), float(epochs_coarse[e_idx68.max()])] if len(e_idx68) else [t_c, t_c],
        "naive_95_epoch": [float(epochs_coarse[e_idx95.min()]), float(epochs_coarse[e_idx95.max()])] if len(e_idx95) else [t_c, t_c],
        "naive_68_lat": [float(lats_coarse[l_idx68.min()]), float(lats_coarse[l_idx68.max()])] if len(l_idx68) else [lat_c, lat_c],
        "naive_95_lat": [float(lats_coarse[l_idx95.min()]), float(lats_coarse[l_idx95.max()])] if len(l_idx95) else [lat_c, lat_c],
        "ll_coarse": ll_c,
    }


def fit_m3_geometric_cap(
    u0: np.ndarray,
    vel: np.ndarray,
    vmag: np.ndarray,
    y: np.ndarray,
    v50: float,
    sv: float,
    epochs: np.ndarray,
    r_caps: np.ndarray,
    width_deg: float = 2.0,
) -> Dict:
    """Model M3: Pure geometric circular void around South Celestial Pole (no extinction physics)."""
    p_base = 1.0 / (1.0 + np.exp(np.clip((vmag - v50) / sv, -40.0, 40.0)))
    yf = y.astype(np.float64)
    y1 = 1.0 - yf
    ll = np.empty((len(epochs), len(r_caps)), dtype=np.float64)
    for ei, epj in enumerate(epochs):
        dec = star_declinations_at_epoch(u0, vel, float(epj))
        theta_s = 90.0 + dec  # angular distance from South Celestial Pole (deg)
        z = np.clip((theta_s[None, :] - r_caps[:, None]) / width_deg, -40.0, 40.0)
        sig = 1.0 / (1.0 + np.exp(-z))
        p = (1.0 - 2.0 * LAPSE_EPS) * p_base[None, :] * sig + LAPSE_EPS
        ll[ei, :] = np.sum(yf[None, :] * np.log(p) + y1[None, :] * np.log(1.0 - p), axis=1)
    ei, ri = np.unravel_index(int(np.argmax(ll)), ll.shape)
    t_c, r_c = float(epochs[ei]), float(r_caps[ri])

    # Fine refinement
    ep_f = np.arange(max(float(epochs[0]), t_c - 600.0), min(float(epochs[-1]), t_c + 600.0) + 0.1, 10.0)
    rc_f = np.arange(max(float(r_caps[0]), r_c - 4.0), min(float(r_caps[-1]), r_c + 4.0) + 1e-6, 0.2)
    ll_f = np.empty((len(ep_f), len(rc_f)), dtype=np.float64)
    for fi, epj in enumerate(ep_f):
        dec = star_declinations_at_epoch(u0, vel, float(epj))
        theta_s = 90.0 + dec
        z = np.clip((theta_s[None, :] - rc_f[:, None]) / width_deg, -40.0, 40.0)
        sig = 1.0 / (1.0 + np.exp(-z))
        p = (1.0 - 2.0 * LAPSE_EPS) * p_base[None, :] * sig + LAPSE_EPS
        ll_f[fi, :] = np.sum(yf[None, :] * np.log(p) + y1[None, :] * np.log(1.0 - p), axis=1)
    fi, rfi = np.unravel_index(int(np.argmax(ll_f)), ll_f.shape)
    return {
        "epoch": float(ep_f[fi]),
        "r_cap_deg": float(rc_f[rfi]),
        "ll_max": float(ll_f[fi, rfi]),
    }


def fit_m4_free_pole(
    u0: np.ndarray,
    vel: np.ndarray,
    vmag: np.ndarray,
    y: np.ndarray,
    v50: float,
    sv: float,
    k_v: float,
    ref_epoch: float,
    ll_precession_best: float,
) -> Dict:
    """Model M4: Unconstrained free South Pole anywhere in southern ecliptic hemisphere."""
    # Propagate star unit vectors to ref_epoch (proper motion is <0.3 deg over 2 kyr for 99% of stars)
    dt = ref_epoch - 1991.25
    u = u0 + dt * vel
    u = u / np.linalg.norm(u, axis=1, keepdims=True)
    yf = y.astype(np.float64)
    y1 = 1.0 - yf

    # Build grid of candidate South Poles in ecliptic coords (beta_s in [-90, -40], lambda in [0, 360))
    ce, se = math.cos(EPS0_J2000), math.sin(EPS0_J2000)

    def ecl_to_eq(lam_deg: float, bet_deg: float) -> np.ndarray:
        lr, br = math.radians(lam_deg), math.radians(bet_deg)
        xe = math.cos(br) * math.cos(lr)
        ye = math.cos(br) * math.sin(lr)
        ze = math.sin(br)
        # Inverse of ecliptic rotation: y_eq = y_e cos e - z_e sin e, z_eq = y_e sin e + z_e cos e
        return np.array([xe, ye * ce - ze * se, ye * se + ze * ce], dtype=np.float64)

    lats_c = np.arange(15.0, 50.01, 1.0)
    best_ll = -1e18
    best_lb = (0.0, -66.5)
    best_lat = 35.0
    for bet in np.arange(-88.0, -40.0 + 0.1, 2.0):
        n_lam = max(1, int(round(180 * math.cos(math.radians(bet)))))
        for lam in np.linspace(0.0, 360.0, n_lam, endpoint=False):
            p_s = ecl_to_eq(float(lam), float(bet))
            # dec relative to free North Pole (-p_s)
            dec = np.rad2deg(np.arcsin(np.clip(u @ (-p_s), -1.0, 1.0)))
            p = compute_m1_probs(dec, vmag, lats_c, v50, sv, k_v)
            lls = np.sum(yf[None, :] * np.log(p) + y1[None, :] * np.log(1.0 - p), axis=1)
            li = int(np.argmax(lls))
            if float(lls[li]) > best_ll:
                best_ll = float(lls[li])
                best_lb = (float(lam), float(bet))
                best_lat = float(lats_c[li])

    # Fine refinement around best_lb (0.25 deg steps)
    lats_f = np.arange(max(15.0, best_lat - 3.0), min(50.0, best_lat + 3.0) + 1e-6, 0.25)
    lam0, bet0 = best_lb
    best_ps = ecl_to_eq(lam0, bet0)
    for bet in np.arange(max(-89.75, bet0 - 4.0), min(-40.0, bet0 + 4.0) + 1e-6, 0.5):
        dlam = 0.5 / max(0.15, math.cos(math.radians(bet)))
        for lam in np.arange(lam0 - 4.0 / max(0.15, math.cos(math.radians(bet))),
                             lam0 + 4.0 / max(0.15, math.cos(math.radians(bet))) + 1e-6, dlam):
            p_s = ecl_to_eq(float(lam % 360.0), float(bet))
            dec = np.rad2deg(np.arcsin(np.clip(u @ (-p_s), -1.0, 1.0)))
            p = compute_m1_probs(dec, vmag, lats_f, v50, sv, k_v)
            lls = np.sum(yf[None, :] * np.log(p) + y1[None, :] * np.log(1.0 - p), axis=1)
            li = int(np.argmax(lls))
            if float(lls[li]) > best_ll:
                best_ll = float(lls[li])
                best_lb = (float(lam % 360.0), float(bet))
                best_lat = float(lats_f[li])
                best_ps = p_s

    # Distance from best_ps to nearest point on 26,000-yr Vondrak South Celestial Pole track
    track_epochs = np.arange(-24000.0, 2001.0, 25.0)
    track_ps = np.array([-ltpequ(float(t)) for t in track_epochs])
    dots = np.clip(track_ps @ best_ps, -1.0, 1.0)
    angles_deg = np.rad2deg(np.arccos(dots))
    idx_min = int(np.argmin(angles_deg))
    offset_deg = float(angles_deg[idx_min])
    nearest_epoch = float(track_epochs[idx_min])

    # RA/Dec of free South Pole in J2000
    ra_s = math.degrees(math.atan2(best_ps[1], best_ps[0])) % 360.0
    dec_s = math.degrees(math.asin(max(-1.0, min(1.0, float(best_ps[2])))))

    # Signed radial offset relative to South Ecliptic Pole (positive = farther from SEP than precession track)
    sep_j2000 = -ltpecl(ref_epoch)
    r_free = math.degrees(math.acos(max(-1.0, min(1.0, float(best_ps @ sep_j2000)))))
    r_track = math.degrees(math.acos(max(-1.0, min(1.0, float(track_ps[idx_min] @ sep_j2000)))))

    return {
        "free_ra_j2000_deg": ra_s,
        "free_dec_j2000_deg": dec_s,
        "free_ecl_lon_deg": best_lb[0],
        "free_ecl_lat_deg": best_lb[1],
        "free_lat_deg": best_lat,
        "free_ll_max": best_ll,
        "offset_from_precession_deg": offset_deg,
        "radial_offset_deg": r_free - r_track,
        "nearest_precession_epoch": nearest_epoch,
        "two_delta_ll_offtrack": float(2.0 * (best_ll - ll_precession_best)),
    }


def assign_spatial_tiles(ecl_lon: np.ndarray, ecl_lat: np.ndarray) -> Tuple[np.ndarray, int]:
    """Deterministic ~15x15 deg equal-area tiles for beta <= +30 deg."""
    # Latitude bands: [-90,-75), [-75,-60), [-60,-45), [-45,-30), [-30,-15), [-15,0), [0,15), [15,30]
    band_edges = [-90.0, -75.0, -60.0, -45.0, -30.0, -15.0, 0.0, 15.0, 30.001]
    tile_ids = np.full(len(ecl_lat), -1, dtype=np.int32)
    next_id = 0
    for bi in range(len(band_edges) - 1):
        lo, hi = band_edges[bi], band_edges[bi + 1]
        mid = 0.5 * (lo + min(hi, 30.0))
        n_sec = max(1, int(round(24.0 * math.cos(math.radians(mid)))))
        in_band = (ecl_lat >= lo) & (ecl_lat < hi)
        if np.any(in_band):
            sec = np.floor(ecl_lon[in_band] / (360.0 / n_sec)).astype(np.int32) % n_sec
            tile_ids[in_band] = next_id + sec
        next_id += n_sec
    # Reindex occupied tiles compactly
    uniq = np.unique(tile_ids[tile_ids >= 0])
    remap = {int(u): i for i, u in enumerate(uniq)}
    compact = np.array([remap[int(t)] for t in tile_ids], dtype=np.int32)
    return compact, len(uniq)


def run_spatial_block_bootstrap(
    tile_ll: np.ndarray,
    epochs: np.ndarray,
    lats: np.ndarray,
    n_boot: int = N_BOOT,
    seed: int = BOOT_SEED,
) -> Dict:
    """Fast exact spatial block bootstrap using precomputed per-tile LL tensor (T, E, L)."""
    rng = np.random.default_rng(seed)
    n_tiles, E, L = tile_ll.shape
    flat_tile = tile_ll.reshape(n_tiles, E * L)
    boot_epochs = np.empty(n_boot, dtype=np.float64)
    boot_lats = np.empty(n_boot, dtype=np.float64)

    for b in range(n_boot):
        counts = rng.multinomial(n_tiles, np.full(n_tiles, 1.0 / n_tiles))
        total_ll = counts.astype(np.float64) @ flat_tile
        idx = int(np.argmax(total_ll))
        ei, li = divmod(idx, L)
        boot_epochs[b] = epochs[ei]
        boot_lats[b] = lats[li]

    return {
        "n_tiles": int(n_tiles),
        "n_boot": int(n_boot),
        "seed": int(seed),
        "epoch_median": float(np.median(boot_epochs)),
        "epoch_mean": float(np.mean(boot_epochs)),
        "epoch_sd": float(np.std(boot_epochs, ddof=1)),
        "epoch_ci68": [float(np.percentile(boot_epochs, 16.0)), float(np.percentile(boot_epochs, 84.0))],
        "epoch_ci95": [float(np.percentile(boot_epochs, 2.5)), float(np.percentile(boot_epochs, 97.5))],
        "lat_median": float(np.median(boot_lats)),
        "lat_mean": float(np.mean(boot_lats)),
        "lat_sd": float(np.std(boot_lats, ddof=1)),
        "lat_ci68": [float(np.percentile(boot_lats, 16.0)), float(np.percentile(boot_lats, 84.0))],
        "lat_ci95": [float(np.percentile(boot_lats, 2.5)), float(np.percentile(boot_lats, 97.5))],
        "samples_epoch": boot_epochs.tolist(),
        "samples_lat": boot_lats.tolist(),
    }


def simulate_synthetic_labels(
    cat: Dict[str, np.ndarray],
    t_true: float,
    lat_true: float,
    v50: float = 4.65,
    sv: float = 0.36,
    k_v: float = 0.25,
    seed: int = 42,
    patchy: bool = False,
) -> np.ndarray:
    """Generate synthetic catalogued labels y_i for a known (t_true, lat_true)."""
    rng = np.random.default_rng(seed)
    dec = star_declinations_at_epoch(cat["u0"], cat["vel"], t_true)
    p = compute_m1_probs(dec, cat["vmag"], np.array([lat_true]), v50, sv, k_v)[0]
    if patchy:
        # Perturb random 18-deg sky patches near the rim to mimic constellation-level clustering
        dt = t_true - 1991.25
        u = cat["u0"] + dt * cat["vel"]
        u = u / np.linalg.norm(u, axis=1, keepdims=True)
        # Drop/boost 10 random patches around the southern rim (h_max in [2, 22] deg)
        h_max = 90.0 - np.abs(lat_true - dec)
        rim_idx = np.where((h_max > 1.0) & (h_max < 25.0))[0]
        if len(rim_idx) > 0:
            centers = rng.choice(rim_idx, size=min(8, len(rim_idx)), replace=False)
            for ci in centers:
                dots = u @ u[ci]
                in_patch = dots > math.cos(math.radians(12.0))
                mult = 0.15 if rng.random() < 0.5 else 1.8
                p = np.where(in_patch, np.clip(p * mult, LAPSE_EPS, 1.0 - LAPSE_EPS), p)
    return (rng.random(len(p)) < p).astype(np.int8)


def run_pipeline(decoy: bool = False) -> Dict:
    cat = load_catalogs(v_max=5.5)
    out_dir = Path("/tmp/ancient_sky_decoy") if decoy else RESULTS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    # In decoy mode, replace all y arrays with synthetic data so real southern sky is never read
    if decoy:
        y_syn = simulate_synthetic_labels(cat, t_true=-1800.0, lat_true=35.0, seed=999, patchy=False)
        for key in ("all48", "in_figure", "aratus_core", "strict_id"):
            cat[key] = y_syn.copy()

    north_mask = cat["ecl_lat"] > 30.0
    test_mask = ~north_mask

    # Calibrate northern ecliptic completeness for each catalogue definition
    calibrations = {}
    for key in ("all48", "in_figure", "aratus_core", "strict_id"):
        v50, sv = fit_northern_completeness(cat["vmag"][north_mask], cat[key][north_mask])
        calibrations[key] = {
            "v50": round(v50, 4),
            "sv": round(sv, 4),
            "n_north_total": int(np.sum(north_mask)),
            "n_north_catalogued": int(np.sum(cat[key][north_mask])),
            "n_test_total": int(np.sum(test_mask)),
            "n_test_catalogued": int(np.sum(cat[key][test_mask])),
        }

    u0_t = cat["u0"][test_mask]
    vel_t = cat["vel"][test_mask]
    vmag_t = cat["vmag"][test_mask]
    y_prim = cat["all48"][test_mask]
    v50_p, sv_p = calibrations["all48"]["v50"], calibrations["all48"]["sv"]

    epochs_c = np.arange(-10000.0, 1000.1, 50.0)
    lats_c = np.arange(15.0, 50.01, 0.5)

    # Primary M1 fit (k_V = 0.25, all48, V <= 5.5)
    prim_fit = fit_m1_coarse_and_fine(u0_t, vel_t, vmag_t, y_prim, v50_p, sv_p, 0.25, epochs_c, lats_c)

    # Spatial block bootstrap for Primary M1
    tile_ids, n_tiles = assign_spatial_tiles(cat["ecl_lon"][test_mask], cat["ecl_lat"][test_mask])
    ll_c_check, tile_ll = evaluate_m1_grid(
        u0_t, vel_t, vmag_t, y_prim, epochs_c, lats_c, v50_p, sv_p, 0.25,
        tile_ids=tile_ids, n_tiles=n_tiles,
    )
    assert np.allclose(ll_c_check, prim_fit["ll_coarse"])
    boot = run_spatial_block_bootstrap(tile_ll, epochs_c, lats_c, n_boot=N_BOOT, seed=BOOT_SEED)

    # Model M2: Joint profile likelihood over k_V in [0.10, 0.50] step 0.02
    kv_grid = np.round(np.arange(0.10, 0.501, 0.02), 2)
    m2_profile = []
    best_m2 = None
    for kv in kv_grid:
        f_kv = fit_m1_coarse_and_fine(u0_t, vel_t, vmag_t, y_prim, v50_p, sv_p, float(kv), epochs_c, lats_c)
        rec = {
            "k_v": float(kv),
            "epoch": f_kv["epoch"],
            "lat": f_kv["lat"],
            "ll_max": f_kv["ll_max"],
        }
        m2_profile.append(rec)
        if best_m2 is None or rec["ll_max"] > best_m2["ll_max"]:
            best_m2 = rec

    # Model M3: Pure geometric spherical cap
    r_caps = np.arange(20.0, 65.01, 0.5)
    m3_fit = fit_m3_geometric_cap(u0_t, vel_t, vmag_t, y_prim, v50_p, sv_p, epochs_c, r_caps)

    # Model M4: Unconstrained free-pole diagnostic
    m4_fit = fit_m4_free_pole(
        u0_t, vel_t, vmag_t, y_prim, v50_p, sv_p, 0.25,
        ref_epoch=prim_fit["epoch"], ll_precession_best=prim_fit["ll_max"],
    )

    # Pre-registered systematic variants
    variants = []
    # (a) Extinction grid k_V in {0.15, 0.20, 0.25, 0.30, 0.35}
    for kv in (0.15, 0.20, 0.25, 0.30, 0.35):
        f = fit_m1_coarse_and_fine(u0_t, vel_t, vmag_t, y_prim, v50_p, sv_p, kv, epochs_c, lats_c)
        variants.append({
            "name": f"M1_kv_{kv:.2f}",
            "group": "extinction",
            "epoch": f["epoch"],
            "lat": f["lat"],
            "ll_max": f["ll_max"],
            "n_cat": int(np.sum(y_prim)),
            "note": f"k_V={kv:.2f} mag/airmass, all48, V<=5.5",
        })
    # (b) M2 free-extinction MLE
    variants.append({
        "name": "M2_free_kv",
        "group": "model",
        "epoch": best_m2["epoch"],
        "lat": best_m2["lat"],
        "ll_max": best_m2["ll_max"],
        "n_cat": int(np.sum(y_prim)),
        "note": f"Profile MLE k_V={best_m2['k_v']:.2f}",
    })
    # (c) M3 geometric cap
    variants.append({
        "name": "M3_geom_cap",
        "group": "model",
        "epoch": m3_fit["epoch"],
        "lat": None,
        "r_cap_deg": m3_fit["r_cap_deg"],
        "ll_max": m3_fit["ll_max"],
        "n_cat": int(np.sum(y_prim)),
        "note": f"Geometric void cap R={m3_fit['r_cap_deg']:.1f} deg (no extinction)",
    })
    # (d) Catalogue subsets (in_figure, aratus_core, strict_id)
    for key, desc in (
        ("in_figure", "In-figure stars only (excludes 108 informes)"),
        ("aratus_core", "Pre-Hipparchan Aratus/Eratosthenes core (excludes Equ, CrA & informes)"),
        ("strict_id", "Strictly secure Hipparcos IDs (I <= 2)"),
    ):
        yk = cat[key][test_mask]
        v50k, svk = calibrations[key]["v50"], calibrations[key]["sv"]
        fk = fit_m1_coarse_and_fine(u0_t, vel_t, vmag_t, yk, v50k, svk, 0.25, epochs_c, lats_c)
        variants.append({
            "name": f"subset_{key}",
            "group": "subset",
            "epoch": fk["epoch"],
            "lat": fk["lat"],
            "ll_max": fk["ll_max"],
            "n_cat": int(np.sum(yk)),
            "note": desc,
        })
    # (e) Magnitude cutoffs (V <= 4.0, 4.5, 5.0)
    for vcut in (4.0, 4.5, 5.0):
        vm = vmag_t <= vcut
        fv = fit_m1_coarse_and_fine(
            u0_t[vm], vel_t[vm], vmag_t[vm], y_prim[vm], v50_p, sv_p, 0.25, epochs_c, lats_c
        )
        variants.append({
            "name": f"vmag_le_{vcut:.1f}",
            "group": "magnitude",
            "epoch": fv["epoch"],
            "lat": fv["lat"],
            "ll_max": fv["ll_max"],
            "n_cat": int(np.sum(y_prim[vm])),
            "note": f"Bright stars V <= {vcut:.1f}, all48, k_V=0.25",
        })

    # Leave-One-Constellation-Out (LOCO) jackknife for all southern constellations (min dec_J2000 < -15)
    loco_results = []
    if not decoy:
        cst_t = cat["cst"][test_mask]
        dec_t = cat["dec"][test_mask]
        south_csts = sorted({str(c) for c, d, yv in zip(cst_t, dec_t, y_prim) if yv == 1 and c and d < -15.0})
        for sc in south_csts:
            keep = cst_t != sc
            fl = fit_m1_coarse_and_fine(
                u0_t[keep], vel_t[keep], vmag_t[keep], y_prim[keep], v50_p, sv_p, 0.25, epochs_c, lats_c
            )
            loco_results.append({
                "dropped_cst": sc,
                "n_dropped_stars": int(np.sum(~keep)),
                "epoch": fl["epoch"],
                "delta_epoch": fl["epoch"] - prim_fit["epoch"],
                "lat": fl["lat"],
                "delta_lat": fl["lat"] - prim_fit["lat"],
            })
        loco_results.sort(key=lambda r: abs(r["delta_epoch"]), reverse=True)

    # Systematic envelope & Combined Honest Uncertainty Range
    var_epochs = [v["epoch"] for v in variants]
    var_lats = [v["lat"] for v in variants if v["lat"] is not None]
    sys_epoch_range = [min(var_epochs), max(var_epochs)]
    sys_lat_range = [min(var_lats), max(var_lats)]

    comb_epoch_range = [min(boot["epoch_ci95"][0], sys_epoch_range[0]),
                        max(boot["epoch_ci95"][1], sys_epoch_range[1])]
    comb_lat_range = [min(boot["lat_ci95"][0], sys_lat_range[0]),
                      max(boot["lat_ci95"][1], sys_lat_range[1])]

    # Pre-registered decision rule (3000 BCE = astronomical year -2999)
    offtrack = m4_fit["offset_from_precession_deg"] > 6.0
    if offtrack:
        verdict_code = "undetermined_offtrack"
        excludes_pre3000 = False
    elif comb_epoch_range[0] > -2999.0:
        verdict_code = "excludes_pre_3000_bce"
        excludes_pre3000 = True
    elif comb_epoch_range[1] < -2999.0:
        verdict_code = "requires_pre_3000_bce"
        excludes_pre3000 = False
    else:
        verdict_code = "spans_3000_bce_undetermined"
        excludes_pre3000 = False

    # Rim diagnostic table: southernmost Ptolemy stars & brightest uncatalogued southern stars
    dec_best = star_declinations_at_epoch(cat["u0"], cat["vel"], prim_fit["epoch"])
    dec_ptol = star_declinations_at_epoch(cat["u0"], cat["vel"], 137.0)
    dec_hipp = star_declinations_at_epoch(cat["u0"], cat["vel"], -128.0)
    dec_j2000 = cat["dec"]

    rim_ptolemy = []
    rim_missing = []
    for i in range(len(cat["hip"])):
        h_best = 90.0 - abs(prim_fit["lat"] - dec_best[i])
        h_alex = 90.0 - abs(31.2 - dec_ptol[i])
        h_rhod = 90.0 - abs(36.4 - dec_hipp[i])
        rec = {
            "hip": int(cat["hip"][i]),
            "name": str(cat["name"][i]),
            "cst": str(cat["cst"][i]),
            "vmag": round(float(cat["vmag"][i]), 2),
            "vp": str(cat["vp"][i]),
            "bv": round(float(cat["bv"][i]), 2),
            "ra_j2000": round(float(cat["ra"][i]), 4),
            "dec_j2000": round(float(dec_j2000[i]), 3),
            "dec_best": round(float(dec_best[i]), 2),
            "h_max_best": round(float(h_best), 2),
            "h_max_rhodes_128bce": round(float(h_rhod), 2),
            "h_max_alexandria_137ce": round(float(h_alex), 2),
            "catalogued": int(cat["all48"][i]),
        }
        if cat["all48"][i] == 1 and dec_best[i] < -40.0:
            rim_ptolemy.append(rec)
        elif cat["all48"][i] == 0 and cat["vmag"][i] <= 3.5 and cat["ecl_lat"][i] < -10.0:
            rim_missing.append(rec)

    rim_ptolemy.sort(key=lambda r: r["dec_best"])
    rim_missing.sort(key=lambda r: r["vmag"])

    summary = {
        "decoy": decoy,
        "calibrations": calibrations,
        "primary_m1": {
            "epoch": prim_fit["epoch"],
            "epoch_label": format_year(prim_fit["epoch"]),
            "lat_deg": prim_fit["lat"],
            "k_v": prim_fit["k_v"],
            "ll_max": prim_fit["ll_max"],
            "naive_68_epoch": prim_fit["naive_68_epoch"],
            "naive_95_epoch": prim_fit["naive_95_epoch"],
            "naive_68_lat": prim_fit["naive_68_lat"],
            "naive_95_lat": prim_fit["naive_95_lat"],
        },
        "bootstrap_m1": {k: v for k, v in boot.items() if not k.startswith("samples_")},
        "m2_free_extinction": {
            "best": best_m2,
            "profile": m2_profile,
        },
        "m3_geometric_cap": m3_fit,
        "m4_free_pole": m4_fit,
        "variants": variants,
        "loco_jackknife": loco_results,
        "loco_epoch_range": [min(r["epoch"] for r in loco_results), max(r["epoch"] for r in loco_results)] if loco_results else None,
        "loco_lat_range": [min(r["lat"] for r in loco_results), max(r["lat"] for r in loco_results)] if loco_results else None,
        "systematic_epoch_range": sys_epoch_range,
        "systematic_lat_range": sys_lat_range,
        "combined_honest_epoch_range": comb_epoch_range,
        "combined_honest_epoch_labels": [format_year(comb_epoch_range[0]), format_year(comb_epoch_range[1])],
        "combined_honest_lat_range": comb_lat_range,
        "verdict_code": verdict_code,
        "excludes_pre_3000_bce": excludes_pre3000,
        "southernmost_ptolemy_stars": rim_ptolemy[:25],
        "brightest_missing_southern_stars": rim_missing[:25],
    }

    # Save summary.json
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    # Save 2D log-likelihood grids for primary M1, aratus_core, and extinction sensitivity (for interactive figures!)
    grid_data = {
        "epochs": epochs_c.tolist(),
        "lats": lats_c.tolist(),
        "m1_all48_kv025": np.round(prim_fit["ll_coarse"] - prim_fit["ll_max"], 3).tolist(),
    }
    for label, key, kv in (
        ("m1_aratus_kv025", "aratus_core", 0.25),
        ("m1_infig_kv025", "in_figure", 0.25),
        ("m1_all48_kv015", "all48", 0.15),
        ("m1_all48_kv035", "all48", 0.35),
    ):
        yk = cat[key][test_mask]
        v50k, svk = calibrations[key]["v50"], calibrations[key]["sv"]
        ll_g, _ = evaluate_m1_grid(u0_t, vel_t, vmag_t, yk, epochs_c, lats_c, v50k, svk, kv)
        grid_data[label] = np.round(ll_g - float(np.max(ll_g)), 3).tolist()
    grid_data["boot_epochs"] = boot["samples_epoch"]
    grid_data["boot_lats"] = boot["samples_lat"]
    (out_dir / "likelihood_grids.json").write_text(json.dumps(grid_data) + "\n", encoding="utf-8")

    # Save TSV tables for transparency
    with (out_dir / "variants.tsv").open("w", encoding="utf-8") as f:
        f.write("name\tgroup\tepoch\tepoch_label\tlat_deg\tll_max\tn_cat\tnote\n")
        for v in variants:
            lat_s = f"{v['lat']:.2f}" if v["lat"] is not None else "NA"
            f.write(f"{v['name']}\t{v['group']}\t{v['epoch']:.1f}\t{format_year(v['epoch'])}\t{lat_s}\t{v['ll_max']:.2f}\t{v['n_cat']}\t{v['note']}\n")

    with (out_dir / "loco.tsv").open("w", encoding="utf-8") as f:
        f.write("dropped_cst\tn_dropped_stars\tepoch\tdelta_epoch\tlat_deg\tdelta_lat\n")
        for r in loco_results:
            f.write(f"{r['dropped_cst']}\t{r['n_dropped_stars']}\t{r['epoch']:.1f}\t{r['delta_epoch']:+.1f}\t{r['lat']:.2f}\t{r['delta_lat']:+.2f}\n")

    with (out_dir / "rim_stars.tsv").open("w", encoding="utf-8") as f:
        f.write("group\thip\tname\tcst\tvmag\tvp\tdec_j2000\tdec_best\th_max_best\th_max_rhodes_128bce\th_max_alexandria_137ce\n")
        for r in rim_ptolemy[:30]:
            f.write(f"ptolemy_south\t{r['hip']}\t{r['name']}\t{r['cst']}\t{r['vmag']:.2f}\t{r['vp']}\t{r['dec_j2000']:.2f}\t{r['dec_best']:.2f}\t{r['h_max_best']:.2f}\t{r['h_max_rhodes_128bce']:.2f}\t{r['h_max_alexandria_137ce']:.2f}\n")
        for r in rim_missing[:30]:
            f.write(f"missing_bright\t{r['hip']}\t{r['name']}\t{r['cst']}\t{r['vmag']:.2f}\t{r['vp']}\t{r['dec_j2000']:.2f}\t{r['dec_best']:.2f}\t{r['h_max_best']:.2f}\t{r['h_max_rhodes_128bce']:.2f}\t{r['h_max_alexandria_137ce']:.2f}\n")

    return summary


def main():
    parser = argparse.ArgumentParser(description="Analyze the southern sky void in Ptolemy's Almagest.")
    parser.add_argument("--decoy", action="store_true", help="Run on synthetic decoy sky (blind pre-lock test)")
    args = parser.parse_args()
    summary = run_pipeline(decoy=args.decoy)
    mode = "DECOY" if args.decoy else "LOCKED"
    p = summary["primary_m1"]
    b = summary["bootstrap_m1"]
    c = summary["combined_honest_epoch_range"]
    cl = summary["combined_honest_lat_range"]
    m4 = summary["m4_free_pole"]
    print(f"[{mode}] Primary M1: epoch = {p['epoch']:.0f} ({p['epoch_label']}), lat = {p['lat_deg']:.2f} N")
    print(f"[{mode}] Block-bootstrap 95% CI: epoch [{b['epoch_ci95'][0]:.0f}, {b['epoch_ci95'][1]:.0f}], lat [{b['lat_ci95'][0]:.2f}, {b['lat_ci95'][1]:.2f}] N")
    print(f"[{mode}] Combined honest range:  epoch [{c[0]:.0f}, {c[1]:.0f}] ({format_year(c[0])} to {format_year(c[1])}), lat [{cl[0]:.2f}, {cl[1]:.2f}] N")
    print(f"[{mode}] M4 free-pole off-track: {m4['offset_from_precession_deg']:.2f} deg (2*dLL={m4['two_delta_ll_offtrack']:.2f})")
    print(f"[{mode}] Verdict: {summary['verdict_code']} (excludes_pre_3000_bce={summary['excludes_pre_3000_bce']})")


if __name__ == "__main__":
    main()
