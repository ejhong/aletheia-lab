#!/usr/bin/env python3
"""Pre-registered sub-meter sonar hunt for submerged prehistoric stone structures (#143).

Implements questions/drowned-walls-submeter/protocol.md (locked SHA-256 3ea4cf7fca82).
- Arm 1: Lake Huron Alpena-Amberley Ridge & Thunder Bay shelf (0.50 m, 1.00 m, 2.00 m NOAA NCEI BAG + enc_general).
- Arm 2: German Western Baltic BSH 0.25 m (Mecklenburg/Kiel/Fehmarn/Arkona, trawl-masked)
         & 0.50 m repeated 2024∩2025 Fehmarn Belt temporal-persistence scan + PANGAEA.988426 munition mask.
"""
from __future__ import annotations

import concurrent.futures
import hashlib
import io
import json
import math
import pathlib
import time
import urllib.parse
import urllib.request
import zipfile
from typing import Any

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
HURON_DIR = DATA / "huron_tiles"
BALTIC_DIR = DATA / "baltic"
PREV_DIR = DATA / "previews"
RES = ROOT / "results"

ENC_GENERAL_LAYERS = {
    15: "Shoreline_Construction_pt",
    26: "Obstruction_pt",
    29: "Wreck_pt",
    42: "Pile_pt",
    45: "Dumping_Ground_pt",
    59: "Shoreline_Construction_ln",
    69: "Cable_Submarine_ln",
    83: "Obstruction_area",
    84: "Wreck_area",
    88: "Cable_Area",
    98: "Dumping_Ground_area",
}


# ---------------------------------------------------------------------------
# Geodesy helpers
# ---------------------------------------------------------------------------

def haversine_m(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    r = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2.0) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2.0) ** 2
    return 2.0 * r * math.asin(min(1.0, math.sqrt(a)))


def make_metric_bbox(center_lat: float, center_lon: float, span_m: float) -> tuple[float, float, float, float]:
    dlat = span_m / 111320.0
    dlon = dlat / math.cos(math.radians(center_lat))
    return (
        round(center_lon - dlon / 2.0, 6),
        round(center_lat - dlat / 2.0, 6),
        round(center_lon + dlon / 2.0, 6),
        round(center_lat + dlat / 2.0, 6),
    )


def utm33n_to_latlon(easting: float, northing: float) -> tuple[float, float]:
    """WGS84 UTM Zone 33N (CM = 15 deg E) inverse projection to (lat, lon)."""
    a = 6378137.0
    f = 1.0 / 298.257223563
    e2 = 2.0 * f - f * f
    ep2 = e2 / (1.0 - e2)
    k0 = 0.9996
    x = easting - 500000.0
    y = northing
    M = y / k0
    mu = M / (a * (1.0 - e2 / 4.0 - 3.0 * e2**2 / 64.0 - 5.0 * e2**3 / 256.0))
    e1 = (1.0 - math.sqrt(1.0 - e2)) / (1.0 + math.sqrt(1.0 - e2))
    phi1 = (
        mu
        + (3.0 * e1 / 2.0 - 27.0 * e1**3 / 32.0) * math.sin(2.0 * mu)
        + (21.0 * e1**2 / 16.0 - 55.0 * e1**4 / 32.0) * math.sin(4.0 * mu)
        + (151.0 * e1**3 / 96.0) * math.sin(6.0 * mu)
    )
    s1, c1, t1 = math.sin(phi1), math.cos(phi1), math.tan(phi1)
    N1 = a / math.sqrt(1.0 - e2 * s1 * s1)
    T1 = t1 * t1
    C1 = ep2 * c1 * c1
    R1 = a * (1.0 - e2) / (1.0 - e2 * s1 * s1) ** 1.5
    D = x / (N1 * k0)
    lat = phi1 - (N1 * t1 / R1) * (
        D**2 / 2.0
        - (5.0 + 3.0 * T1 + 10.0 * C1 - 4.0 * C1**2 - 9.0 * ep2) * D**4 / 24.0
    )
    lon = math.radians(15.0) + (
        D
        - (1.0 + 2.0 * T1 + C1) * D**3 / 6.0
        + (5.0 - 2.0 * C1 + 28.0 * T1 - 3.0 * C1**2 + 8.0 * ep2 + 24.0 * T1**2) * D**5 / 120.0
    ) / c1
    return math.degrees(lat), math.degrees(lon)


# ---------------------------------------------------------------------------
# Arm 1: Lake Huron specs, fetchers, and elevation detector
# ---------------------------------------------------------------------------

def build_huron_specs() -> list[dict[str, Any]]:
    specs: list[dict[str, Any]] = [
        # 3 real Lake Huron charted shipwreck controls
        {"id": "CTRL_HURON_WRECK_H13652", "zone": "Control", "survey": "H13652", "px_m": 0.5, "is_control": True,
         "bbox": make_metric_bbox(45.1055, -83.2184, 256.0)},
        {"id": "CTRL_HURON_WRECK_F00862", "zone": "Control", "survey": "F00862", "px_m": 0.5, "is_control": True,
         "bbox": make_metric_bbox(44.9851, -83.2681, 256.0)},
        {"id": "CTRL_HURON_WRECK_W00499", "zone": "Control", "survey": "W00499", "px_m": 2.0, "is_control": True,
         "bbox": make_metric_bbox(44.9837, -82.9240, 1024.0)},
    ]

    def add_grid(prefix: str, zone: str, survey: str, px_m: float,
                 lon_min: float, lon_max: float, lat_min: float, lat_max: float, nx: int, ny: int):
        lons = np.linspace(lon_min, lon_max, nx)
        lats = np.linspace(lat_min, lat_max, ny)
        span_m = 512.0 * px_m
        idx = 1
        for lat in lats:
            for lon in lons:
                specs.append({
                    "id": f"{prefix}_{idx:02d}",
                    "zone": zone,
                    "survey": survey,
                    "px_m": px_m,
                    "is_control": False,
                    "bbox": make_metric_bbox(float(lat), float(lon), span_m),
                })
                idx += 1

    # Zone H1: 24 tiles @ 0.50 m/px (256 m x 256 m)
    add_grid("H1_H13652", "H1 (50 cm Multibeam)", "H13652", 0.5, -83.290, -83.210, 45.060, 45.140, 3, 4)
    add_grid("H1_F00862", "H1 (50 cm Multibeam)", "F00862", 0.5, -83.265, -83.235, 44.990, 45.006, 3, 2)
    add_grid("H1_F00863", "H1 (50 cm Multibeam)", "F00863", 0.5, -83.218, -83.182, 44.990, 45.012, 3, 2)

    # Zone H2: 24 tiles @ 1.00 m/px (512 m x 512 m)
    add_grid("H2_H12132", "H2 (1 m Multibeam)", "H12132", 1.0, -83.390, -83.130, 44.990, 45.110, 4, 4)
    add_grid("H2_H12964", "H2 (1 m Multibeam)", "H12964", 1.0, -83.245, -83.188, 45.090, 45.132, 4, 2)

    # Zone H3: 24 tiles @ 2.00 m/px (1024 m x 1024 m) wall-to-wall across mid-lake Alpena-Amberley Ridge W00499
    add_grid("H3_RIDGE", "H3 (2 m Mid-Lake Ridge)", "W00499", 2.0, -82.968, -82.864, 44.956, 45.044, 6, 4)

    # Zone H4: 12 tiles @ 1.00 m/px (512 m x 512 m) coastal bathymetric LiDAR H14139
    add_grid("H4_LIDAR", "H4 (1 m Bathy LiDAR)", "H14139", 1.0, -83.340, -83.250, 44.780, 44.940, 2, 6)
    return specs


def fetch_huron_bag_tile(spec: dict[str, Any], size: int = 512) -> tuple[np.ndarray, pathlib.Path]:
    HURON_DIR.mkdir(parents=True, exist_ok=True)
    tp = HURON_DIR / f"{spec['id']}.tif"
    if tp.exists():
        sz = tp.stat().st_size
        if 100 <= sz < 4096:
            return np.full((size, size), np.nan, dtype=np.float32), tp
        if sz >= 4096:
            try:
                arr = np.array(Image.open(tp), dtype=np.float32)
                if arr.shape == (size, size):
                    return arr, tp
            except Exception:
                tp.unlink(missing_ok=True)

    lon0, lat0, lon1, lat1 = spec["bbox"]
    url = (
        "https://gis.ngdc.noaa.gov/arcgis/rest/services/bag_bathymetry/ImageServer/exportImage?"
        + urllib.parse.urlencode({
            "bbox": f"{lon0},{lat0},{lon1},{lat1}",
            "bboxSR": "4326",
            "imageSR": "4326",
            "size": f"{size},{size}",
            "format": "tiff",
            "pixelType": "F32",
            "noData": "-999999",
            "interpolation": "RSP_NearestNeighbor",
            "f": "image",
        })
    )
    last_err = None
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "bathymetry-audit/1.0"})
            with urllib.request.urlopen(req, timeout=45) as r:
                raw = r.read()
            if len(raw) < 4096:
                tp.write_bytes(raw)
                return np.full((size, size), np.nan, dtype=np.float32), tp
            arr = np.array(Image.open(io.BytesIO(raw)), dtype=np.float32)
            if arr.shape != (size, size):
                raise RuntimeError(f"Unexpected shape {arr.shape}")
            tp.write_bytes(raw)
            return arr, tp
        except Exception as e:
            last_err = e
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Failed BAG {spec['id']}: {last_err}")


def fetch_huron_enc_general() -> tuple[list[dict[str, Any]], pathlib.Path]:
    """Fetch all NOAA enc_general cultural layers in one spatial query across Lake Huron study box."""
    DATA.mkdir(parents=True, exist_ok=True)
    cp = DATA / "huron_enc_general.json"
    if cp.exists() and cp.stat().st_size > 10:
        return json.loads(cp.read_text(encoding="utf-8")), cp

    geom = "-83.46,44.74,-82.80,45.22"
    feats: list[dict[str, Any]] = []
    for lyr_id, lyr_name in ENC_GENERAL_LAYERS.items():
        url = (
            f"https://encdirect.noaa.gov/arcgis/rest/services/encdirect/enc_general/MapServer/{lyr_id}/query?"
            + urllib.parse.urlencode({
                "geometry": geom,
                "geometryType": "esriGeometryEnvelope",
                "inSR": "4326",
                "outSR": "4326",
                "spatialRel": "esriSpatialRelIntersects",
                "outFields": "*",
                "returnGeometry": "true",
                "f": "json",
            })
        )
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "bathymetry-audit/1.0"})
            with urllib.request.urlopen(req, timeout=20) as r:
                d = json.loads(r.read().decode("utf-8"))
            for f in (d.get("features") or []):
                g = f.get("geometry") or {}
                pts = []
                if "x" in g and "y" in g:
                    pts.append((float(g["x"]), float(g["y"])))
                for path in (g.get("paths") or []):
                    for xy in path:
                        pts.append((float(xy[0]), float(xy[1])))
                for ring in (g.get("rings") or []):
                    for xy in ring:
                        pts.append((float(xy[0]), float(xy[1])))
                if pts:
                    feats.append({
                        "layer": lyr_name,
                        "objnam": (f.get("attributes") or {}).get("OBJNAM"),
                        "pts": pts,
                    })
        except Exception:
            pass
    cp.write_text(json.dumps(feats), encoding="utf-8")
    return feats, cp


def compute_masked_bpi(z: np.ndarray, valid_mask: np.ndarray, sigma_px: float) -> np.ndarray:
    v = valid_mask.astype(np.float64)
    zf = np.where(valid_mask, z.astype(np.float64), 0.0)
    num = ndimage.gaussian_filter(zf, sigma=sigma_px, mode="nearest")
    den = ndimage.gaussian_filter(v, sigma=sigma_px, mode="nearest")
    bg = np.where(den > 1e-3, num / np.maximum(den, 1e-6), np.nan)
    bpi = np.where(valid_mask, zf - bg, np.nan)
    return bpi.astype(np.float32)


def detect_huron_structures(
    z: np.ndarray,
    bbox: tuple[float, float, float, float],
    enc_pts: list[tuple[float, float, str]],
    px_m: float,
    is_control: bool = False,
) -> dict[str, Any]:
    """Pre-registered sub-meter Lake Huron elevation detector."""
    h, w = z.shape
    lon0, lat0, lon1, lat1 = bbox
    z_hi = 1.5 if is_control else -1.5
    raw_valid = np.isfinite(z) & (z >= -120.0) & (z <= z_hi)
    if raw_valid.mean() < 0.03:
        return {
            "valid_pct": round(100.0 * float(raw_valid.mean()), 2),
            "valid_km2": round(float(raw_valid.sum()) * px_m * px_m / 1e6, 5),
            "depth_median": None,
            "max_bpi_tile": None,
            "std_bpi_tile": None,
            "candidates": [],
            "corners": [],
            "v_funnels": [],
            "rings": [],
            "bpi": None,
            "valid_mask": raw_valid,
        }

    valid_eroded = ndimage.binary_erosion(raw_valid, iterations=3)
    sigma_px = 10.0 / px_m  # 10 m physical Gaussian background
    bpi = compute_masked_bpi(z, raw_valid, sigma_px=sigma_px)

    if px_m <= 1.05:
        bpi_thresh = 0.25
        min_len_m = 25.0
        max_wid_m = 10.0
        min_area = 40 if px_m <= 0.6 else 20
        ring_min_m, ring_max_m = 8.0, 80.0
        corner_gap_m = 25.0
        flank_offs_m = (6.0, 9.0, 12.0)
    else:
        bpi_thresh = 0.30
        min_len_m = 40.0
        max_wid_m = 16.0
        min_area = 20
        ring_min_m, ring_max_m = 20.0, 150.0
        corner_gap_m = 40.0
        flank_offs_m = (10.0, 14.0, 18.0)

    pos_mask = valid_eroded & np.isfinite(bpi) & (bpi >= bpi_thresh)
    labeled, n_comp = ndimage.label(pos_mask, structure=np.ones((3, 3), dtype=int))
    eroded_edge = valid_eroded & (~ndimage.binary_erosion(valid_eroded, iterations=2))

    def px_to_lonlat(r: float, c: float) -> tuple[float, float]:
        lon = lon0 + (c / max(1, w - 1)) * (lon1 - lon0)
        lat = lat1 - (r / max(1, h - 1)) * (lat1 - lat0)
        return lon, lat

    # Pre-filter ENC points near tile bbox (+0.005 deg pad)
    local_enc = [p for p in enc_pts if (lon0 - 0.005 <= p[0] <= lon1 + 0.005 and lat0 - 0.005 <= p[1] <= lat1 + 0.005)]

    candidates: list[dict[str, Any]] = []
    rings: list[dict[str, Any]] = []

    if n_comp > 0:
        for comp_id, sl in enumerate(ndimage.find_objects(labeled), start=1):
            if sl is None:
                continue
            sub = (labeled[sl] == comp_id)
            area = int(sub.sum())
            if area < min_area:
                continue
            rs, cs = np.nonzero(sub)
            rs = rs + sl[0].start
            cs = cs + sl[1].start
            cy, cx = float(rs.mean()), float(cs.mean())
            dy = rs - cy
            dx = cs - cx
            cov = np.cov(np.vstack([dx, dy]))
            eigvals, eigvecs = np.linalg.eigh(cov)
            lam2, lam1 = float(max(eigvals[0], 1e-6)), float(max(eigvals[1], 1e-6))
            lin = lam1 / (lam1 + lam2)
            vx, vy = float(eigvecs[0, 1]), float(eigvecs[1, 1])
            proj_maj = dx * vx + dy * vy
            proj_min = -dx * vy + dy * vx
            L_m = float(proj_maj.max() - proj_maj.min()) * px_m
            W_m = float(np.percentile(proj_min, 95) - np.percentile(proj_min, 5)) * px_m
            mean_bpi = float(np.nanmean(bpi[rs, cs]))
            max_bpi = float(np.nanmax(bpi[rs, cs]))
            mean_z = float(np.nanmean(z[rs, cs]))

            clon, clat = px_to_lonlat(cy, cx)

            # Check ENC proximity helper
            def nearest_enc(pts_ll: list[tuple[float, float]]) -> tuple[float, str]:
                md = 1e9
                nl = ""
                for ex, ey, lyr in local_enc:
                    for plon, plat in pts_ll:
                        dm = haversine_m(plon, plat, ex, ey)
                        if dm < md:
                            md = dm
                            nl = lyr
                return md, nl

            # Hollow stone blind / enclosure ring check
            if lin < 0.78 and ring_min_m <= L_m <= ring_max_m and W_m >= ring_min_m * 0.65:
                ri, ci = int(round(cy)), int(round(cx))
                rad_c = max(2, int(round(2.0 / px_m)))
                if rad_c <= ri < h - rad_c and rad_c <= ci < w - rad_c and valid_eroded[ri, ci]:
                    center_bpi = float(np.nanmean(bpi[ri - rad_c:ri + rad_c + 1, ci - rad_c:ci + rad_c + 1]))
                    angs = np.arctan2(dy, dx)
                    octs = set(int(((a + math.pi) / (2 * math.pi)) * 8) % 8 for a in angs)
                    if center_bpi <= 0.05 and len(octs) >= 6:
                        md_enc, nl_enc = nearest_enc([(clon, clat)])
                        r_flags = [f"CHARTED_MODERN:{nl_enc}"] if md_enc <= 120.0 else []
                        rings.append({
                            "comp_id": comp_id,
                            "lat": round(clat, 6),
                            "lon": round(clon, 6),
                            "diam_m": round(L_m, 1),
                            "width_m": round(W_m, 1),
                            "octants": len(octs),
                            "mean_bpi_m": round(mean_bpi, 3),
                            "max_bpi_m": round(max_bpi, 3),
                            "center_bpi_m": round(center_bpi, 3),
                            "mean_depth_m": round(mean_z, 2),
                            "flags": r_flags,
                            "unmasked": len(r_flags) == 0,
                            "px_centroid": [round(cx, 1), round(cy, 1)],
                        })

            if L_m < min_len_m or W_m > max_wid_m or lin < 0.88 or mean_bpi < bpi_thresh:
                continue

            az = math.degrees(math.atan2(vx, -vy)) % 180.0
            pmin_i = int(np.argmin(proj_maj))
            pmax_i = int(np.argmax(proj_maj))
            r_a, c_a = float(rs[pmin_i]), float(cs[pmin_i])
            r_b, c_b = float(rs[pmax_i]), float(cs[pmax_i])
            alon, alat = px_to_lonlat(r_a, c_a)
            blon, blat = px_to_lonlat(r_b, c_b)

            nx_v, ny_v = -vy, vx
            ts = np.linspace(float(proj_maj.min()) * 0.8, float(proj_maj.max()) * 0.8, 15)

            # 1. Step-edge / mosaic-seam test
            z_left, z_right = [], []
            for t in ts:
                bx, by = cx + t * vx, cy + t * vy
                for off_m in flank_offs_m:
                    off_px = off_m / px_m
                    for sign, bucket in ((1.0, z_left), (-1.0, z_right)):
                        sx = int(round(bx + sign * off_px * nx_v))
                        sy = int(round(by + sign * off_px * ny_v))
                        if 0 <= sy < h and 0 <= sx < w and raw_valid[sy, sx]:
                            bucket.append(float(z[sy, sx]))
            flank_step = (
                abs(float(np.median(z_left)) - float(np.median(z_right)))
                if (len(z_left) >= 5 and len(z_right) >= 5)
                else 0.0
            )
            is_seam_step = bool(flank_step > 0.65 * max_bpi)

            # 2. Axis-aligned raster seam check
            ang_card = min(az, abs(az - 90.0), abs(az - 180.0))
            touches_edge = bool(eroded_edge[rs, cs].sum() >= 5)
            tile_span_m = h * px_m
            is_axis_seam = bool((ang_card <= 1.5) and (L_m > 0.60 * tile_span_m or touches_edge))

            # 3. Periodic bedform check (-60 m to +60 m in 2 m steps)
            offs_m = np.arange(-60.0, 61.0, 2.0)
            prof = []
            for om in offs_m:
                op = om / px_m
                vals = []
                for t in ts[::2]:
                    sx = int(round(cx + t * vx + op * nx_v))
                    sy = int(round(cy + t * vy + op * ny_v))
                    if 0 <= sy < h and 0 <= sx < w and raw_valid[sy, sx] and np.isfinite(bpi[sy, sx]):
                        vals.append(float(bpi[sy, sx]))
                prof.append(float(np.mean(vals)) if vals else 0.0)
            prof_arr = np.array(prof)
            mid_idx = len(offs_m) // 2
            center_peak = max(mean_bpi, float(prof_arr[mid_idx - 2:mid_idx + 3].max()))
            flank_peaks = 0
            for idx_p in range(2, len(prof_arr) - 2):
                dist_m = abs(offs_m[idx_p])
                if 10.0 <= dist_m <= 56.0:
                    if prof_arr[idx_p] >= 0.40 * center_peak and prof_arr[idx_p] == prof_arr[idx_p - 2:idx_p + 3].max():
                        flank_peaks += 1
            is_periodic = bool(flank_peaks >= 2)

            # 4. NOAA ENC charted modern overlay check (<= 120 m)
            min_enc_m, nearest_enc_layer = nearest_enc([(clon, clat), (alon, alat), (blon, blat)])
            is_charted = bool(min_enc_m <= 120.0)

            flags = []
            if is_seam_step:
                flags.append("SEAM_STEP")
            if is_axis_seam:
                flags.append("AXIS_SEAM")
            if is_periodic:
                flags.append("PERIODIC_BEDFORM")
            if is_charted:
                flags.append(f"CHARTED_MODERN:{nearest_enc_layer}")

            score = round(L_m * mean_bpi * (lin ** 4), 2)
            candidates.append({
                "comp_id": comp_id,
                "lat": round(clat, 6),
                "lon": round(clon, 6),
                "length_m": round(L_m, 1),
                "width_m": round(W_m, 1),
                "linearity": round(lin, 4),
                "azimuth_deg": round(az, 1),
                "mean_bpi_m": round(mean_bpi, 3),
                "max_bpi_m": round(max_bpi, 3),
                "mean_depth_m": round(mean_z, 2),
                "flank_step_m": round(flank_step, 3),
                "flank_peaks": flank_peaks,
                "nearest_enc_m": round(min_enc_m, 1) if min_enc_m < 1e8 else None,
                "nearest_enc_layer": nearest_enc_layer,
                "flags": flags,
                "unmasked": len(flags) == 0,
                "score": score,
                "px_endpoints": [round(c_a, 1), round(r_a, 1), round(c_b, 1), round(r_b, 1)],
                "px_centroid": [round(cx, 1), round(cy, 1)],
            })

    candidates.sort(key=lambda c: (-int(c["unmasked"]), -c["score"]))

    # Rectilinear corners (75-105 deg) & caribou V-funnels (20-75 deg) among unmasked candidates
    unmasked = [c for c in candidates if c["unmasked"]]
    corners: list[dict[str, Any]] = []
    v_funnels: list[dict[str, Any]] = []
    for i in range(len(unmasked)):
        for j in range(i + 1, len(unmasked)):
            a, b = unmasked[i], unmasked[j]
            da = abs(a["azimuth_deg"] - b["azimuth_deg"])
            da = min(da, 180.0 - da)
            ea = [(a["px_endpoints"][0], a["px_endpoints"][1]), (a["px_endpoints"][2], a["px_endpoints"][3])]
            eb = [(b["px_endpoints"][0], b["px_endpoints"][1]), (b["px_endpoints"][2], b["px_endpoints"][3])]
            dmin = min(math.hypot(p[0] - q[0], p[1] - q[1]) * px_m for p in ea for q in eb)
            if dmin <= corner_gap_m:
                item = {
                    "comp_a": a["comp_id"],
                    "comp_b": b["comp_id"],
                    "angle_deg": round(da, 1),
                    "gap_m": round(dmin, 1),
                    "lat": round((a["lat"] + b["lat"]) / 2.0, 6),
                    "lon": round((a["lon"] + b["lon"]) / 2.0, 6),
                    "len_a_m": a["length_m"],
                    "len_b_m": b["length_m"],
                }
                if 75.0 <= da <= 105.0:
                    corners.append(item)
                elif 20.0 <= da < 75.0:
                    v_funnels.append(item)

    bpi_valid = bpi[valid_eroded & np.isfinite(bpi)]
    return {
        "valid_pct": round(100.0 * float(raw_valid.mean()), 2),
        "valid_km2": round(float(raw_valid.sum()) * px_m * px_m / 1e6, 5),
        "depth_median": round(float(np.median(z[raw_valid])), 2),
        "max_bpi_tile": round(float(np.max(bpi_valid)), 3) if bpi_valid.size else None,
        "std_bpi_tile": round(float(np.std(bpi_valid)), 3) if bpi_valid.size else None,
        "candidates": candidates,
        "corners": corners,
        "v_funnels": v_funnels,
        "rings": rings,
        "bpi": bpi,
        "valid_mask": raw_valid,
    }


def inject_huron_wall(
    z: np.ndarray,
    valid_mask: np.ndarray,
    length_m: float,
    width_m: float,
    height_m: float,
    az_deg: float,
    px_m: float,
) -> tuple[np.ndarray, tuple[float, float]]:
    out = z.copy()
    h, w = z.shape
    margin_px = max(30, int(round((length_m * 0.65) / px_m)))
    margin_px = min(margin_px, min(h, w) // 3)
    interior = ndimage.binary_erosion(valid_mask, iterations=margin_px)
    ys, xs = np.nonzero(interior)
    if len(ys) == 0:
        cy, cx = h // 2, w // 2
    else:
        mid = len(ys) // 2
        cy, cx = int(ys[mid]), int(xs[mid])
    rad = math.radians(az_deg)
    vx, vy = math.sin(rad), -math.cos(rad)
    nx, ny = -vy, vx
    yy, xx = np.mgrid[0:h, 0:w]
    dx = (xx - cx) * px_m
    dy = (yy - cy) * px_m
    along = dx * vx + dy * vy
    across = dx * nx + dy * ny
    sigma_w = width_m / 2.355
    mask_len = np.abs(along) <= (length_m / 2.0)
    wall = height_m * np.exp(-0.5 * (across / sigma_w) ** 2) * mask_len
    return np.where(valid_mask, out + wall.astype(np.float32), out), (float(cx), float(cy))


def inject_huron_step_seam(
    z: np.ndarray, valid_mask: np.ndarray, step_m: float = 0.50, az_deg: float = 37.0, px_m: float = 1.0
) -> np.ndarray:
    out = z.copy()
    h, w = z.shape
    cy, cx = h // 2, w // 2
    rad = math.radians(az_deg)
    vx, vy = math.sin(rad), -math.cos(rad)
    nx, ny = -vy, vx
    yy, xx = np.mgrid[0:h, 0:w]
    across = ((xx - cx) * nx + (yy - cy) * ny) * px_m
    step = step_m * (across >= 0).astype(np.float32) + 0.12 * np.exp(-0.5 * (across / 1.5) ** 2).astype(np.float32)
    return np.where(valid_mask, out + step, out)


# ---------------------------------------------------------------------------
# Arm 2: German Western Baltic slope & temporal persistence detector
# ---------------------------------------------------------------------------

def load_baltic_munitions() -> list[tuple[float, float, str]]:
    """Parse PANGAEA.988426 munition pile coordinates (lat, lon, event)."""
    p = BALTIC_DIR / "pangaea_988426_munitions.tab"
    lines = p.read_text(encoding="utf-8").splitlines()
    start = next((i for i, l in enumerate(lines) if l.startswith("*/")), 0) + 1
    pts: list[tuple[float, float, str]] = []
    for line in lines[start + 1:]:
        parts = line.split("\t")
        if len(parts) >= 3:
            try:
                pts.append((float(parts[1]), float(parts[2]), parts[0]))
            except ValueError:
                pass
    return pts


def detect_baltic_slope_block(
    slope: np.ndarray,
    valid_mask: np.ndarray,
    origin_e: float,
    origin_n: float,
    px_m: float,
    munitions: list[tuple[float, float, str]],
    mode: str,  # "deg_25cm" or "persist_50cm"
) -> dict[str, Any]:
    """Detect linear stone-wall/boulder ridges and hollow rings in Baltic slope/persistence grid."""
    h, w = slope.shape
    if valid_mask.mean() < 0.03:
        return {"candidates": [], "rings": [], "corners": [], "v_funnels": [], "dS": None}

    # Fast 20 m local background subtraction (downsample 4x for speed on large tiles)
    sigma_px = 20.0 / px_m
    v = valid_mask.astype(np.float32)
    sf = np.where(valid_mask, slope.astype(np.float32), 0.0)
    ds_factor = 4 if sigma_px >= 30.0 else 1
    if ds_factor > 1:
        sf_s = sf[::ds_factor, ::ds_factor]
        v_s = v[::ds_factor, ::ds_factor]
        num_s = ndimage.gaussian_filter(sf_s, sigma=sigma_px / ds_factor, mode="nearest")
        den_s = ndimage.gaussian_filter(v_s, sigma=sigma_px / ds_factor, mode="nearest")
        bg_s = np.where(den_s > 1e-3, num_s / np.maximum(den_s, 1e-6), 0.0)
        bg = ndimage.zoom(bg_s, (h / bg_s.shape[0], w / bg_s.shape[1]), order=1)
    else:
        num = ndimage.gaussian_filter(sf, sigma=sigma_px, mode="nearest")
        den = ndimage.gaussian_filter(v, sigma=sigma_px, mode="nearest")
        bg = np.where(den > 1e-3, num / np.maximum(den, 1e-6), 0.0)
    dS = np.where(valid_mask, sf - bg, np.nan).astype(np.float32)

    if mode == "deg_25cm":
        pos_mask = valid_mask & (slope >= 3.0) & (dS >= 1.5)
        min_len_m, max_wid_m, min_area = 20.0, 10.0, 80
        ring_min_m, ring_max_m = 6.0, 60.0
        center_thresh = 0.5
        corner_gap_m = 25.0
    else:
        pos_mask = valid_mask & (slope >= 55.0) & (dS >= 35.0)
        min_len_m, max_wid_m, min_area = 30.0, 12.0, 60
        ring_min_m, ring_max_m = 12.0, 100.0
        center_thresh = 10.0
        corner_gap_m = 30.0

    # Bridge tiny 1 px gaps inside boulder ridges without smearing across trawl lines
    labeled, n_comp = ndimage.label(pos_mask, structure=np.ones((3, 3), dtype=int))
    eroded_edge = valid_mask & (~ndimage.binary_erosion(valid_mask, iterations=2))

    def px_to_latlon(r: float, c: float) -> tuple[float, float]:
        e = origin_e + c * px_m
        n = origin_n - r * px_m
        return utm33n_to_latlon(e, n)

    def near_munition(lat: float, lon: float) -> tuple[bool, float]:
        md = 1e9
        for mlat, mlon, _ in munitions:
            if abs(mlat - lat) <= 0.03 and abs(mlon - lon) <= 0.05:
                dm = haversine_m(lon, lat, mlon, mlat)
                if dm < md:
                    md = dm
        return md <= 1500.0, md

    candidates: list[dict[str, Any]] = []
    rings: list[dict[str, Any]] = []

    if n_comp > 0:
        for comp_id, sl in enumerate(ndimage.find_objects(labeled), start=1):
            if sl is None:
                continue
            sub = (labeled[sl] == comp_id)
            area = int(sub.sum())
            if area < min_area:
                continue
            rs, cs = np.nonzero(sub)
            rs = rs + sl[0].start
            cs = cs + sl[1].start
            cy, cx = float(rs.mean()), float(cs.mean())
            dy = rs - cy
            dx = cs - cx
            cov = np.cov(np.vstack([dx, dy]))
            eigvals, eigvecs = np.linalg.eigh(cov)
            lam2, lam1 = float(max(eigvals[0], 1e-6)), float(max(eigvals[1], 1e-6))
            lin = lam1 / (lam1 + lam2)
            vx, vy = float(eigvecs[0, 1]), float(eigvecs[1, 1])
            proj_maj = dx * vx + dy * vy
            proj_min = -dx * vy + dy * vx
            L_m = float(proj_maj.max() - proj_maj.min()) * px_m
            W_m = float(np.percentile(proj_min, 95) - np.percentile(proj_min, 5)) * px_m
            mean_val = float(np.nanmean(slope[rs, cs]))
            max_val = float(np.nanmax(slope[rs, cs]))
            mean_ds = float(np.nanmean(dS[rs, cs]))
            clat, clon = px_to_latlon(cy, cx)
            is_mun, mun_m = near_munition(clat, clon)

            # Hollow enclosure ring check
            if lin < 0.78 and ring_min_m <= L_m <= ring_max_m and W_m >= ring_min_m * 0.65:
                ri, ci = int(round(cy)), int(round(cx))
                rad_c = max(2, int(round(2.0 / px_m)))
                if rad_c <= ri < h - rad_c and rad_c <= ci < w - rad_c and valid_mask[ri, ci]:
                    center_ds = float(np.nanmean(dS[ri - rad_c:ri + rad_c + 1, ci - rad_c:ci + rad_c + 1]))
                    angs = np.arctan2(dy, dx)
                    octs = set(int(((a + math.pi) / (2 * math.pi)) * 8) % 8 for a in angs)
                    if center_ds <= center_thresh and len(octs) >= 6:
                        rings.append({
                            "comp_id": comp_id,
                            "lat": round(clat, 6),
                            "lon": round(clon, 6),
                            "diam_m": round(L_m, 1),
                            "width_m": round(W_m, 1),
                            "octants": len(octs),
                            "mean_slope": round(mean_val, 2),
                            "mean_dS": round(mean_ds, 2),
                            "center_dS": round(center_ds, 2),
                            "near_munition": is_mun,
                            "px_centroid": [round(cx, 1), round(cy, 1)],
                        })

            if L_m < min_len_m or W_m > max_wid_m or lin < 0.88:
                continue

            az = math.degrees(math.atan2(vx, -vy)) % 180.0
            pmin_i = int(np.argmin(proj_maj))
            pmax_i = int(np.argmax(proj_maj))
            r_a, c_a = float(rs[pmin_i]), float(cs[pmin_i])
            r_b, c_b = float(rs[pmax_i]), float(cs[pmax_i])

            ang_card = min(az, abs(az - 90.0), abs(az - 180.0))
            touches_edge = bool(eroded_edge[rs, cs].sum() >= 5)
            is_axis_seam = bool((ang_card <= 1.5) and touches_edge)

            # Periodic bedform check (-40 m to +40 m)
            nx_v, ny_v = -vy, vx
            ts = np.linspace(float(proj_maj.min()) * 0.8, float(proj_maj.max()) * 0.8, 11)
            offs_m = np.arange(-40.0, 41.0, 2.0)
            prof = []
            for om in offs_m:
                op = om / px_m
                vals = []
                for t in ts[::2]:
                    sx = int(round(cx + t * vx + op * nx_v))
                    sy = int(round(cy + t * vy + op * ny_v))
                    if 0 <= sy < h and 0 <= sx < w and valid_mask[sy, sx] and np.isfinite(dS[sy, sx]):
                        vals.append(float(dS[sy, sx]))
                prof.append(float(np.mean(vals)) if vals else 0.0)
            prof_arr = np.array(prof)
            mid_idx = len(offs_m) // 2
            center_peak = max(mean_ds, float(prof_arr[mid_idx - 2:mid_idx + 3].max()))
            flank_peaks = 0
            for idx_p in range(2, len(prof_arr) - 2):
                dist_m = abs(offs_m[idx_p])
                if 8.0 <= dist_m <= 36.0:
                    if prof_arr[idx_p] >= 0.40 * center_peak and prof_arr[idx_p] == prof_arr[idx_p - 2:idx_p + 3].max():
                        flank_peaks += 1
            is_periodic = bool(flank_peaks >= 2)

            flags = []
            if is_axis_seam:
                flags.append("AXIS_SEAM")
            if is_periodic:
                flags.append("PERIODIC_BEDFORM")
            if is_mun:
                flags.append("NEAR_MUNITION_CELL")

            # Note: NEAR_MUNITION_CELL is an informational confounder flag (1.5 km rounded cell),
            # not a hard artifact deletion, so we track both strict unflagged and non-artifact!
            is_artifact = is_axis_seam or is_periodic
            score = round(L_m * mean_ds * (lin ** 4), 2)
            candidates.append({
                "comp_id": comp_id,
                "lat": round(clat, 6),
                "lon": round(clon, 6),
                "length_m": round(L_m, 1),
                "width_m": round(W_m, 1),
                "linearity": round(lin, 4),
                "azimuth_deg": round(az, 1),
                "mean_slope": round(mean_val, 2),
                "max_slope": round(max_val, 2),
                "mean_dS": round(mean_ds, 2),
                "flank_peaks": flank_peaks,
                "near_munition": is_mun,
                "munition_dist_m": round(mun_m, 0) if mun_m < 1e8 else None,
                "flags": flags,
                "unmasked": not is_artifact,
                "score": score,
                "px_endpoints": [round(c_a, 1), round(r_a, 1), round(c_b, 1), round(r_b, 1)],
                "px_centroid": [round(cx, 1), round(cy, 1)],
            })

    candidates.sort(key=lambda c: (-int(c["unmasked"]), -c["score"]))

    unmasked = [c for c in candidates if c["unmasked"]]
    corners, v_funnels = [], []
    for i in range(len(unmasked)):
        for j in range(i + 1, len(unmasked)):
            a, b = unmasked[i], unmasked[j]
            da = abs(a["azimuth_deg"] - b["azimuth_deg"])
            da = min(da, 180.0 - da)
            ea = [(a["px_endpoints"][0], a["px_endpoints"][1]), (a["px_endpoints"][2], a["px_endpoints"][3])]
            eb = [(b["px_endpoints"][0], b["px_endpoints"][1]), (b["px_endpoints"][2], b["px_endpoints"][3])]
            dmin = min(math.hypot(p[0] - q[0], p[1] - q[1]) * px_m for p in ea for q in eb)
            if dmin <= corner_gap_m:
                item = {
                    "comp_a": a["comp_id"], "comp_b": b["comp_id"],
                    "angle_deg": round(da, 1), "gap_m": round(dmin, 1),
                    "lat": round((a["lat"] + b["lat"]) / 2.0, 6),
                    "lon": round((a["lon"] + b["lon"]) / 2.0, 6),
                }
                if 75.0 <= da <= 105.0:
                    corners.append(item)
                elif 20.0 <= da < 75.0:
                    v_funnels.append(item)

    return {"candidates": candidates, "rings": rings, "corners": corners, "v_funnels": v_funnels, "dS": dS}


def inject_baltic_wall_slope(
    arr: np.ndarray, valid_mask: np.ndarray, length_m: float, width_m: float, amp: float, az_deg: float, px_m: float
) -> tuple[np.ndarray, tuple[float, float]]:
    """Inject a Blinkerwall-scale boulder wall slope ridge onto a Baltic slope grid."""
    out = arr.copy().astype(np.float32)
    h, w = arr.shape
    margin_px = max(40, int(round((length_m * 0.7) / px_m)))
    margin_px = min(margin_px, min(h, w) // 3)
    interior = ndimage.binary_erosion(valid_mask, iterations=margin_px)
    ys, xs = np.nonzero(interior)
    if len(ys) == 0:
        cy, cx = h // 2, w // 2
    else:
        mid = len(ys) // 2
        cy, cx = int(ys[mid]), int(xs[mid])
    rad = math.radians(az_deg)
    vx, vy = math.sin(rad), -math.cos(rad)
    nx, ny = -vy, vx
    yy, xx = np.mgrid[0:h, 0:w]
    dx = (xx - cx) * px_m
    dy = (yy - cy) * px_m
    along = dx * vx + dy * vy
    across = dx * nx + dy * ny
    sigma_w = width_m / 2.355
    mask_len = np.abs(along) <= (length_m / 2.0)
    # Realistic boulder-ridge flank slope profile (two steep flanks + crest slope)
    wall_s = amp * np.exp(-0.5 * (across / sigma_w) ** 2) * mask_len
    return np.where(valid_mask, np.maximum(out, out + wall_s), out), (float(cx), float(cy))


# ---------------------------------------------------------------------------
# Visual Audit Rendering
# ---------------------------------------------------------------------------

def render_huron_audit(
    z: np.ndarray,
    bpi: np.ndarray,
    valid_mask: np.ndarray,
    px_m: float,
    candidates: list[dict[str, Any]],
    rings: list[dict[str, Any]],
    title: str,
    out_path: pathlib.Path,
) -> None:
    h, w = z.shape
    z_fill = np.where(valid_mask, z, float(np.nanmedian(z[valid_mask])) if valid_mask.any() else 0.0)
    gy, gx = np.gradient(z_fill, px_m)
    vx, vy = gx * 4.0, gy * 4.0
    slope = np.arctan(np.hypot(vx, vy))
    aspect = np.arctan2(-vy, vx)
    az_r, alt_r = math.radians(315.0), math.radians(35.0)
    hs = np.sin(alt_r) * np.cos(slope) + np.cos(alt_r) * np.sin(slope) * np.cos(az_r - aspect)
    hs_u8 = np.clip((hs + 0.1) * 230, 0, 255).astype(np.uint8)
    left = np.stack([
        np.where(valid_mask, (hs_u8 * 0.85).astype(np.uint8), 18),
        np.where(valid_mask, (hs_u8 * 0.93).astype(np.uint8), 24),
        np.where(valid_mask, np.clip(hs_u8 * 1.03, 0, 255).astype(np.uint8), 36),
    ], axis=-1)

    bpi_c = np.clip(np.where(valid_mask & np.isfinite(bpi), bpi, 0.0) / 0.65, -1.0, 1.0)
    r_b = np.where(bpi_c >= 0, 60 + 195 * bpi_c, 60 * (1 + bpi_c))
    g_b = np.where(bpi_c >= 0, 65 + 140 * bpi_c, 65 + 45 * (-bpi_c))
    b_b = np.where(bpi_c >= 0, 75 * (1 - 0.7 * bpi_c), 75 + 150 * (-bpi_c))
    right = np.stack([
        np.where(valid_mask, np.clip(r_b, 0, 255).astype(np.uint8), 18),
        np.where(valid_mask, np.clip(g_b, 0, 255).astype(np.uint8), 24),
        np.where(valid_mask, np.clip(b_b, 0, 255).astype(np.uint8), 36),
    ], axis=-1)

    canvas = Image.new("RGB", (w * 2 + 16, h + 38), (16, 20, 26))
    canvas.paste(Image.fromarray(left), (0, 38))
    canvas.paste(Image.fromarray(right), (w + 16, 38))
    draw = ImageDraw.Draw(canvas)
    draw.text((8, 10), f"{title}  |  Left: 4x Hillshade ({px_m:.2f} m/px)  |  Right: BPI (+0.65m copper)  [Lime=unmasked, Cyan=ring, Red=masked]", fill=(235, 240, 248))

    for c in candidates[:12]:
        col = (60, 255, 110) if c["unmasked"] else (255, 85, 85)
        x0, y0, x1, y1 = c["px_endpoints"]
        for ox in (0, w + 16):
            draw.line([(ox + x0, 38 + y0), (ox + x1, 38 + y1)], fill=col, width=2)
            cx, cy = c["px_centroid"]
            draw.ellipse([ox + cx - 6, 38 + cy - 6, ox + cx + 6, 38 + cy + 6], outline=col, width=2)
    for rg in rings[:8]:
        col = (60, 220, 255) if rg["unmasked"] else (255, 140, 60)
        cx, cy = rg["px_centroid"]
        rr = max(8, int(round((rg["diam_m"] / 2.0) / px_m)))
        for ox in (0, w + 16):
            draw.ellipse([ox + cx - rr, 38 + cy - rr, ox + cx + rr, 38 + cy + rr], outline=col, width=2)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path)


def render_baltic_crop_audit(
    panels: list[tuple[str, np.ndarray]],
    cand: dict[str, Any],
    px_m: float,
    title: str,
    out_path: pathlib.Path,
    half_px: int = 180,
) -> None:
    """Render side-by-side zoomed audit cutout centered on a Baltic candidate."""
    cx, cy = int(round(cand["px_centroid"][0])), int(round(cand["px_centroid"][1]))
    h, w = panels[0][1].shape
    y0, y1 = max(0, cy - half_px), min(h, cy + half_px)
    x0, x1 = max(0, cx - half_px), min(w, cx + half_px)
    ch, cw = y1 - y0, x1 - x0
    n = len(panels)
    canvas = Image.new("RGB", (cw * n + 10 * (n - 1), ch + 40), (16, 20, 26))
    draw = ImageDraw.Draw(canvas)
    draw.text((8, 6), title, fill=(235, 240, 248))
    for i, (lbl, arr) in enumerate(panels):
        sub = arr[y0:y1, x0:x1].astype(np.float32)
        v = np.isfinite(sub)
        p99 = float(np.percentile(sub[v], 99)) if v.any() else 1.0
        p01 = float(np.percentile(sub[v], 1)) if v.any() else 0.0
        scale = max(p99 - p01, 1e-3)
        u8 = np.clip((np.where(v, sub, p01) - p01) / scale * 255.0, 0, 255).astype(np.uint8)
        rgb = np.stack([u8, np.clip(u8 * 0.96, 0, 255).astype(np.uint8), np.clip(u8 * 0.90, 0, 255).astype(np.uint8)], axis=-1)
        ox = i * (cw + 10)
        canvas.paste(Image.fromarray(rgb), (ox, 40))
        draw.text((ox + 6, 24), lbl, fill=(190, 215, 255))
        if "px_endpoints" in cand:
            ex0, ey0, ex1, ey1 = cand["px_endpoints"]
            draw.line([(ox + ex0 - x0, 40 + ey0 - y0), (ox + ex1 - x0, 40 + ey1 - y0)], fill=(60, 255, 110), width=2)
        else:
            rr = max(8, int(round((cand.get("diam_m", 20.0) / 2.0) / px_m)))
            draw.ellipse([ox + (cx - x0) - rr, 40 + (cy - y0) - rr, ox + (cx - x0) + rr, 40 + (cy - y0) + rr], outline=(60, 220, 255), width=2)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path)


# ---------------------------------------------------------------------------
# Main Orchestrator
# ---------------------------------------------------------------------------

def main() -> None:
    t0 = time.time()
    RES.mkdir(parents=True, exist_ok=True)
    PREV_DIR.mkdir(parents=True, exist_ok=True)
    hashes: dict[str, str] = {}

    # =========================================================================
    # ARM 1: LAKE HURON (NOAA NCEI BAG + enc_general)
    # =========================================================================
    print("=== ARM 1: LAKE HURON ALPENA-AMBERLEY RIDGE & THUNDER BAY ===")
    enc_feats, enc_path = fetch_huron_enc_general()
    hashes["huron_enc_general.json"] = hashlib.sha256(enc_path.read_bytes()).hexdigest()
    enc_pts: list[tuple[float, float, str]] = []
    for f in enc_feats:
        for x, y in f["pts"]:
            enc_pts.append((x, y, f["layer"]))
    print(f"Loaded {len(enc_feats)} NOAA enc_general cultural features ({len(enc_pts)} vertices)")

    specs = build_huron_specs()
    print(f"Fetching {len(specs)} Lake Huron BAG tiles (0.50 m / 1.00 m / 2.00 m)...")
    tile_arrays: dict[str, np.ndarray] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(fetch_huron_bag_tile, s): s for s in specs}
        for fut in concurrent.futures.as_completed(futs):
            s = futs[fut]
            arr, tp = fut.result()
            tile_arrays[s["id"]] = arr
            hashes[f"huron_tiles/{tp.name}"] = hashlib.sha256(tp.read_bytes()).hexdigest()
    print(f"Fetched all {len(specs)} Lake Huron tiles in {time.time() - t0:.1f}s")

    # Scan all Lake Huron tiles
    huron_tiles_summary: list[dict[str, Any]] = []
    huron_controls: list[dict[str, Any]] = []
    huron_unmasked: list[dict[str, Any]] = []
    huron_all_cands: list[dict[str, Any]] = []
    huron_rings: list[dict[str, Any]] = []
    huron_corners: list[dict[str, Any]] = []
    huron_vfunnels: list[dict[str, Any]] = []

    for s in specs:
        arr = tile_arrays[s["id"]]
        res = detect_huron_structures(arr, s["bbox"], enc_pts, px_m=s["px_m"], is_control=s["is_control"])
        n_unm = sum(1 for c in res["candidates"] if c["unmasked"])
        n_ring_unm = sum(1 for r in res["rings"] if r["unmasked"])
        rec = {
            "id": s["id"],
            "zone": s["zone"],
            "survey": s["survey"],
            "px_m": s["px_m"],
            "is_control": s["is_control"],
            "bbox": s["bbox"],
            "valid_pct": res["valid_pct"],
            "valid_km2": res["valid_km2"],
            "depth_median": res["depth_median"],
            "max_bpi_tile": res["max_bpi_tile"],
            "std_bpi_tile": res["std_bpi_tile"],
            "n_candidates": len(res["candidates"]),
            "n_unmasked": n_unm,
            "n_rings": len(res["rings"]),
            "n_rings_unmasked": n_ring_unm,
            "n_corners": len(res["corners"]),
            "n_v_funnels": len(res["v_funnels"]),
        }
        if s["is_control"]:
            # Also check peak wreck BPI near tile center (within 70 m)
            bpi = res["bpi"]
            center_max_bpi = None
            if bpi is not None:
                h, w = bpi.shape
                r_px = int(round(70.0 / s["px_m"]))
                sub = bpi[max(0, h // 2 - r_px):min(h, h // 2 + r_px), max(0, w // 2 - r_px):min(w, w // 2 + r_px)]
                if np.isfinite(sub).any():
                    center_max_bpi = round(float(np.nanmax(sub)), 3)
            # Check ENC wreck match near tile center
            clon = (s["bbox"][0] + s["bbox"][2]) / 2.0
            clat = (s["bbox"][1] + s["bbox"][3]) / 2.0
            min_w_m = min((haversine_m(clon, clat, x, y) for x, y, lyr in enc_pts if lyr == "Wreck_pt"), default=1e9)
            rec["center_wreck_max_bpi_m"] = center_max_bpi
            rec["nearest_enc_wreck_m"] = round(min_w_m, 1)
            rec["control_passed"] = bool((center_max_bpi is not None and center_max_bpi >= 0.80) and min_w_m <= 120.0)
            huron_controls.append(rec)
            if res["bpi"] is not None:
                render_huron_audit(
                    arr, res["bpi"], res["valid_mask"], s["px_m"], res["candidates"], res["rings"],
                    f"{s['id']} (wreck max BPI={center_max_bpi}m)", PREV_DIR / f"{s['id']}.png"
                )
        else:
            huron_tiles_summary.append(rec)
            for c in res["candidates"]:
                c_copy = dict(c, tile_id=s["id"], zone=s["zone"], survey=s["survey"], px_m=s["px_m"])
                huron_all_cands.append(c_copy)
                if c["unmasked"]:
                    huron_unmasked.append(c_copy)
            for rg in res["rings"]:
                huron_rings.append(dict(rg, tile_id=s["id"], zone=s["zone"], px_m=s["px_m"]))
            for co in res["corners"]:
                huron_corners.append(dict(co, tile_id=s["id"], zone=s["zone"], px_m=s["px_m"]))
            for vf in res["v_funnels"]:
                huron_vfunnels.append(dict(vf, tile_id=s["id"], zone=s["zone"], px_m=s["px_m"]))

    huron_unmasked.sort(key=lambda c: -c["score"])
    huron_rings_unm = [r for r in huron_rings if r["unmasked"]]

    # Render audit PNGs for top 15 unmasked Lake Huron candidates + all corners/V-funnels/unmasked rings
    audit_huron_tiles = set()
    for c in huron_unmasked[:15]:
        audit_huron_tiles.add(c["tile_id"])
    for x in huron_corners + huron_vfunnels + huron_rings_unm:
        audit_huron_tiles.add(x["tile_id"])
    spec_map = {s["id"]: s for s in specs}
    for tid in sorted(audit_huron_tiles):
        s = spec_map[tid]
        arr = tile_arrays[tid]
        res = detect_huron_structures(arr, s["bbox"], enc_pts, px_m=s["px_m"], is_control=False)
        if res["bpi"] is not None:
            render_huron_audit(
                arr, res["bpi"], res["valid_mask"], s["px_m"], res["candidates"], res["rings"],
                f"{tid} ({s['zone']}, z={res['depth_median']}m)", PREV_DIR / f"HURON_{tid}.png"
            )

    # Arm 1 Synthetic Planting Benchmark (12 walls + 12 step seams across 0.5m, 1.0m, 2.0m)
    print("Running Arm 1 Lake Huron synthetic calibration (12 walls + 12 seams)...")
    synth_hosts: list[dict[str, Any]] = []
    for px_target in (0.5, 1.0, 2.0):
        cands_t = [t for t in huron_tiles_summary if abs(t["px_m"] - px_target) < 0.05 and t["valid_pct"] >= 85.0]
        cands_t.sort(key=lambda t: (t["n_unmasked"], -(t["valid_pct"])))
        synth_hosts.extend(cands_t[:4])

    azs = [27.0, 53.0, 118.0, 146.0] * 3
    huron_wall_hits = 0
    huron_seam_rejs = 0
    huron_synth_details = []
    for idx_h, host in enumerate(synth_hosts[:12]):
        s = spec_map[host["id"]]
        arr = tile_arrays[host["id"]]
        px = s["px_m"]
        v = np.isfinite(arr) & (arr >= -120.0) & (arr <= -1.5)
        az = azs[idx_h]
        L_s = 60.0 if px <= 1.05 else 120.0
        W_s = 2.5 if px <= 1.05 else 4.0
        H_s = 0.50 if px <= 1.05 else 0.55
        z_w, (wcx, wcy) = inject_huron_wall(arr, v, L_s, W_s, H_s, az, px)
        r_w = detect_huron_structures(z_w, s["bbox"], [], px_m=px, is_control=False)
        found = any(
            c["unmasked"] and math.hypot(c["px_centroid"][0] - wcx, c["px_centroid"][1] - wcy) * px <= 30.0
            for c in r_w["candidates"]
        )
        if found:
            huron_wall_hits += 1

        z_sm = inject_huron_step_seam(arr, v, step_m=0.50, az_deg=az, px_m=px)
        r_sm = detect_huron_structures(z_sm, s["bbox"], [], px_m=px, is_control=False)
        # Check if any unmasked false wall was created along the seam azimuth near center
        h_s, w_s = arr.shape
        fp_seam = any(
            c["unmasked"]
            and math.hypot(c["px_centroid"][0] - w_s / 2.0, c["px_centroid"][1] - h_s / 2.0) * px <= 80.0
            and min(abs(c["azimuth_deg"] - az), 180.0 - abs(c["azimuth_deg"] - az)) <= 12.0
            for c in r_sm["candidates"]
        )
        if not fp_seam:
            huron_seam_rejs += 1
        huron_synth_details.append({"tile": host["id"], "px_m": px, "az": az, "wall_recovered": found, "seam_rejected": not fp_seam})

    print(f"Arm 1 Calibration: controls={sum(c['control_passed'] for c in huron_controls)}/3 | "
          f"synth_walls={huron_wall_hits}/12 | synth_seams_rejected={huron_seam_rejs}/12")

    # =========================================================================
    # ARM 2: GERMAN WESTERN BALTIC (Test1-5 @ 0.25m + Fehmarn 2024∩2025 @ 0.50m)
    # =========================================================================
    print("\n=== ARM 2: GERMAN WESTERN BALTIC (0.25 m TEST AREAS & 0.50 m 2024∩2025 FEHMARN) ===")
    munitions = load_baltic_munitions()
    print(f"Loaded {len(munitions)} PANGAEA.988426 German Baltic WWII munition piles")
    for fn in ("Test_Areas.zip", "Time_Series.zip", "pangaea_988426_munitions.tab"):
        hashes[f"baltic/{fn}"] = hashlib.sha256((BALTIC_DIR / fn).read_bytes()).hexdigest()

    baltic_2a_regions = {
        1: "Mecklenburg Bay (North, ~14 km from Blinkerwall)",
        2: "Mecklenburg Bay (South, ~4 km from Blinkerwall)",
        3: "Arkona Basin (East of Rügen)",
        4: "Kiel Bay",
        5: "Fehmarn Belt (West)",
    }
    baltic_areas_summary: list[dict[str, Any]] = []
    baltic_unmasked: list[dict[str, Any]] = []
    baltic_rings: list[dict[str, Any]] = []
    baltic_corners: list[dict[str, Any]] = []
    baltic_vfunnels: list[dict[str, Any]] = []
    baltic_synth_walls_hits = 0
    baltic_synth_walls_total = 0

    test_arrays_cache: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    with zipfile.ZipFile(BALTIC_DIR / "Test_Areas.zip") as zf:
        for i in range(1, 6):
            tid = f"BALTIC_Test{i}"
            tfw = [float(x) for x in zf.read(f"Test{i}.tfw").decode().split()]
            px_m = abs(tfw[0])
            arr = np.array(Image.open(io.BytesIO(zf.read(f"Test{i}.tif"))), dtype=np.float32)
            m_raw = np.array(Image.open(io.BytesIO(zf.read(f"Test{i}_mask.tif"))))
            m_ch = m_raw[..., 0] if m_raw.ndim == 3 else m_raw
            h = min(arr.shape[0], m_ch.shape[0])
            w = min(arr.shape[1], m_ch.shape[1])
            arr = arr[:h, :w]
            m_ch = m_ch[:h, :w]
            trawl = (m_ch == 76)
            trawl_dil = ndimage.binary_dilation(trawl, iterations=2)
            valid_untrawled = np.isfinite(arr) & (arr >= 0.0) & (arr < 89.0) & (~trawl_dil)
            test_arrays_cache[tid] = (arr, valid_untrawled)

            res = detect_baltic_slope_block(arr, valid_untrawled, tfw[4], tfw[5], px_m, munitions, mode="deg_25cm")
            n_unm = sum(1 for c in res["candidates"] if c["unmasked"])
            baltic_areas_summary.append({
                "id": tid,
                "region": baltic_2a_regions[i],
                "px_m": px_m,
                "shape": [h, w],
                "total_km2": round(h * w * px_m * px_m / 1e6, 4),
                "untrawled_km2": round(float(valid_untrawled.sum()) * px_m * px_m / 1e6, 4),
                "trawl_pct": round(100.0 * float(trawl.mean()), 2),
                "n_candidates": len(res["candidates"]),
                "n_unmasked": n_unm,
                "n_rings": len(res["rings"]),
                "n_corners": len(res["corners"]),
                "n_v_funnels": len(res["v_funnels"]),
            })
            for c in res["candidates"]:
                if c["unmasked"]:
                    baltic_unmasked.append(dict(c, area_id=tid, region=baltic_2a_regions[i], px_m=px_m, arm="2A_025m"))
            for rg in res["rings"]:
                baltic_rings.append(dict(rg, area_id=tid, region=baltic_2a_regions[i], px_m=px_m, arm="2A_025m"))
            for co in res["corners"]:
                baltic_corners.append(dict(co, area_id=tid, region=baltic_2a_regions[i]))
            for vf in res["v_funnels"]:
                baltic_vfunnels.append(dict(vf, area_id=tid, region=baltic_2a_regions[i]))

            # Synthetic planting on untrawled Test1..5 (5 walls, 1 per test area)
            # Find a clean 300x300 subwindow with maximal untrawled fraction
            best_pos = (0, 0, -1.0)
            for sy in range(0, max(1, h - 320), 160):
                for sx in range(0, max(1, w - 320), 160):
                    frac = float(valid_untrawled[sy:sy + 320, sx:sx + 320].mean())
                    if frac > best_pos[2]:
                        best_pos = (sy, sx, frac)
            sy0, sx0, _ = best_pos
            sub_a = arr[sy0:sy0 + 360, sx0:sx0 + 360]
            sub_v = valid_untrawled[sy0:sy0 + 360, sx0:sx0 + 360]
            # Plant a 60 m x 2.5 m Blinkerwall slope bump (~12 deg)
            # Use full valid (unmasked by trawl on the synthetic line itself) to test wall geometry recovery
            s_w, (wcx, wcy) = inject_baltic_wall_slope(sub_a, np.ones_like(sub_v, dtype=bool), 60.0, 2.5, 12.0, 35.0 + 23.0 * i, px_m)
            rw_s = detect_baltic_slope_block(s_w, np.ones_like(sub_v, dtype=bool), tfw[4], tfw[5], px_m, [], mode="deg_25cm")
            hit = any(
                c["unmasked"] and math.hypot(c["px_centroid"][0] - wcx, c["px_centroid"][1] - wcy) * px_m <= 25.0
                for c in rw_s["candidates"]
            )
            baltic_synth_walls_total += 1
            if hit:
                baltic_synth_walls_hits += 1
            print(f"  {tid}: {h}x{w} @ {px_m}m | untrawled={baltic_areas_summary[-1]['untrawled_km2']} km2 | "
                  f"unmasked={n_unm}, rings={len(res['rings'])} | synth_wall={'PASS' if hit else 'MISS'}")

    # Arm 2B: Fehmarn Belt 2024 ∩ 2025 temporal persistence (0.50 m/px)
    print("Co-registering Fehmarn Belt 2024 & 2025 (0.50 m/px) for temporal-persistence scan...")
    with zipfile.ZipFile(BALTIC_DIR / "Time_Series.zip") as zf:
        tfw24 = [float(x) for x in zf.read("Time_Series/slope_2024.tfw").decode().split()]
        tfw25 = [float(x) for x in zf.read("Time_Series/slope_2025.tfw").decode().split()]
        im24 = np.array(Image.open(io.BytesIO(zf.read("Time_Series/slope_2024.tif"))))
        im25 = np.array(Image.open(io.BytesIO(zf.read("Time_Series/slope_2025.tif"))))

    px_ts = abs(tfw24[0])
    # Exact UTM 33N integer alignment
    # Pixel (r, c) in 2024 has E = e24 + c*px, N = n24 - r*px
    # Same E, N in 2025 has c25 = c + (e24 - e25)/px, r25 = r + (n25 - n24)/px
    dc = int(round((tfw24[4] - tfw25[4]) / px_ts))
    dr = int(round((tfw25[5] - tfw24[5]) / px_ts))
    h24, w24 = im24.shape[:2]
    h25, w25 = im25.shape[:2]
    r24_0 = max(0, -dr)
    r24_1 = min(h24, h25 - dr)
    c24_0 = max(0, -dc)
    c24_1 = min(w24, w25 - dc)
    r25_0, r25_1 = r24_0 + dr, r24_1 + dr
    c25_0, c25_1 = c24_0 + dc, c24_1 + dc

    g24 = im24[r24_0:r24_1, c24_0:c24_1, 0]
    a24 = im24[r24_0:r24_1, c24_0:c24_1, 1]
    g25 = im25[r25_0:r25_1, c25_0:c25_1, 0]
    a25 = im25[r25_0:r25_1, c25_0:c25_1, 1]
    del im24, im25

    shared_valid = (a24 == 255) & (a25 == 255)
    shared_valid = ndimage.binary_erosion(shared_valid, iterations=4)
    s24 = (255 - g24).astype(np.float32)
    s25 = (255 - g25).astype(np.float32)
    s_persist = np.minimum(s24, s25)
    orig_e = tfw24[4] + c24_0 * px_ts
    orig_n = tfw24[5] - r24_0 * px_ts
    overlap_km2 = round(float(shared_valid.sum()) * px_ts * px_ts / 1e6, 3)
    print(f"  Aligned overlap shape={s_persist.shape} (shift dr={dr}, dc={dc}) | shared valid={overlap_km2} km2")

    # Scan in overlapping 1024x1024 blocks (step 896 px = 128 px overlap)
    H_ts, W_ts = s_persist.shape
    raw_ts_cands: list[dict[str, Any]] = []
    raw_ts_rings: list[dict[str, Any]] = []
    ts_blocks_scanned = 0
    for by in range(0, H_ts, 896):
        y1 = min(H_ts, by + 1024)
        for bx in range(0, W_ts, 896):
            x1 = min(W_ts, bx + 1024)
            v_blk = shared_valid[by:y1, bx:x1]
            if v_blk.mean() < 0.05:
                continue
            ts_blocks_scanned += 1
            res_blk = detect_baltic_slope_block(
                s_persist[by:y1, bx:x1], v_blk,
                orig_e + bx * px_ts, orig_n - by * px_ts,
                px_ts, munitions, mode="persist_50cm",
            )
            for c in res_blk["candidates"]:
                if c["unmasked"]:
                    # Translate pixel coords to full aligned grid
                    c["px_centroid"] = [round(c["px_centroid"][0] + bx, 1), round(c["px_centroid"][1] + by, 1)]
                    c["px_endpoints"] = [
                        round(c["px_endpoints"][0] + bx, 1), round(c["px_endpoints"][1] + by, 1),
                        round(c["px_endpoints"][2] + bx, 1), round(c["px_endpoints"][3] + by, 1),
                    ]
                    raw_ts_cands.append(dict(c, area_id="BALTIC_Fehmarn_24x25", region="Fehmarn Belt (2024∩2025 persistent)", px_m=round(px_ts, 3), arm="2B_050m"))
            for rg in res_blk["rings"]:
                rg["px_centroid"] = [round(rg["px_centroid"][0] + bx, 1), round(rg["px_centroid"][1] + by, 1)]
                raw_ts_rings.append(dict(rg, area_id="BALTIC_Fehmarn_24x25", region="Fehmarn Belt (2024∩2025 persistent)", px_m=round(px_ts, 3), arm="2B_050m"))

    # Deduplicate overlapping block hits within 25 m
    def dedup_geo(items: list[dict[str, Any]], key_score: str = "score") -> list[dict[str, Any]]:
        items_s = sorted(items, key=lambda x: -x.get(key_score, x.get("diam_m", 0)))
        kept: list[dict[str, Any]] = []
        for it in items_s:
            if not any(haversine_m(it["lon"], it["lat"], k["lon"], k["lat"]) <= 25.0 for k in kept):
                kept.append(it)
        return kept

    ts_cands_dedup = dedup_geo(raw_ts_cands, "score")
    ts_rings_dedup = dedup_geo(raw_ts_rings, "diam_m")
    baltic_unmasked.extend(ts_cands_dedup)
    baltic_rings.extend(ts_rings_dedup)
    baltic_areas_summary.append({
        "id": "BALTIC_Fehmarn_24x25",
        "region": "Fehmarn Belt (2024∩2025 persistent)",
        "px_m": round(px_ts, 3),
        "shape": [H_ts, W_ts],
        "total_km2": round(H_ts * W_ts * px_ts * px_ts / 1e6, 3),
        "untrawled_km2": overlap_km2,
        "trawl_pct": None,
        "n_candidates": len(ts_cands_dedup),
        "n_unmasked": len(ts_cands_dedup),
        "n_rings": len(ts_rings_dedup),
        "n_corners": 0,
        "n_v_funnels": 0,
    })

    # Arm 2B Synthetic calibration: 5 persistent walls (both 2024 & 2025) + 10 transient 2024-only trawl scars
    print("Running Arm 2B Fehmarn Belt synthetic persistent-wall (5) + transient-trawl (10) calibration...")
    valid_blocks = []
    for by in range(0, H_ts - 600, 700):
        for bx in range(0, W_ts - 600, 700):
            if shared_valid[by:by + 600, bx:bx + 600].mean() >= 0.90:
                valid_blocks.append((by, bx))
    baltic_transient_rejs = 0
    for idx_b in range(10):
        by, bx = valid_blocks[idx_b % len(valid_blocks)]
        b24 = s24[by:by + 600, bx:bx + 600]
        b25 = s25[by:by + 600, bx:bx + 600]
        bv = shared_valid[by:by + 600, bx:bx + 600]
        az = 25.0 + 14.0 * idx_b
        # Transient 2024-only trawl scar (+70 gray in 2024 only!)
        b24_tr, (tcx, tcy) = inject_baltic_wall_slope(b24, bv, 80.0, 2.5, 70.0, az, px_ts)
        sp_tr = np.minimum(b24_tr, b25)
        r_tr = detect_baltic_slope_block(sp_tr, bv, orig_e + bx * px_ts, orig_n - by * px_ts, px_ts, [], mode="persist_50cm")
        fp_tr = any(
            c["unmasked"]
            and math.hypot(c["px_centroid"][0] - tcx, c["px_centroid"][1] - tcy) * px_ts <= 25.0
            and min(abs(c["azimuth_deg"] - az), 180.0 - abs(c["azimuth_deg"] - az)) <= 12.0
            for c in r_tr["candidates"]
        )
        if not fp_tr:
            baltic_transient_rejs += 1

        # First 5 blocks: also test persistent 60 m wall present in BOTH 2024 & 2025 (+65 gray)
        if idx_b < 5:
            b24_w, (wcx, wcy) = inject_baltic_wall_slope(b24, bv, 60.0, 2.5, 65.0, az, px_ts)
            b25_w, _ = inject_baltic_wall_slope(b25, bv, 60.0, 2.5, 65.0, az, px_ts)
            sp_w = np.minimum(b24_w, b25_w)
            r_pw = detect_baltic_slope_block(sp_w, bv, orig_e + bx * px_ts, orig_n - by * px_ts, px_ts, [], mode="persist_50cm")
            hit_pw = any(
                c["unmasked"] and math.hypot(c["px_centroid"][0] - wcx, c["px_centroid"][1] - wcy) * px_ts <= 25.0
                for c in r_pw["candidates"]
            )
            baltic_synth_walls_total += 1
            if hit_pw:
                baltic_synth_walls_hits += 1

    print(f"Arm 2 Calibration: persistent_synth_walls={baltic_synth_walls_hits}/{baltic_synth_walls_total} | "
          f"transient_trawl_rejected={baltic_transient_rejs}/10")

    # Sort Baltic candidates and render zoomed visual audit PNGs for top 10 + all rings
    baltic_unmasked.sort(key=lambda c: -c["score"])
    for idx_c, c in enumerate(baltic_unmasked[:12], start=1):
        if c["arm"] == "2A_025m":
            arr_a, v_a = test_arrays_cache[c["area_id"]]
            render_baltic_crop_audit(
                [("0.25m Slope (deg)", arr_a), ("Untrawled Slope", np.where(v_a, arr_a, 0.0))],
                c, c["px_m"],
                f"Baltic #{idx_c} {c['area_id']} | L={c['length_m']}m W={c['width_m']}m slope={c['mean_slope']}deg ({c['lat']},{c['lon']})",
                PREV_DIR / f"BALTIC_2A_{idx_c:02d}_{c['area_id']}.png",
                half_px=220,
            )
        else:
            render_baltic_crop_audit(
                [("2024 Steepness", s24), ("2025 Steepness", s25), ("2024∩2025 Persist Min", s_persist)],
                c, c["px_m"],
                f"Baltic #{idx_c} Fehmarn 24x25 | L={c['length_m']}m W={c['width_m']}m persist={c['mean_slope']} ({c['lat']},{c['lon']})",
                PREV_DIR / f"BALTIC_2B_{idx_c:02d}_Fehmarn.png",
                half_px=180,
            )

    for idx_r, rg in enumerate(baltic_rings[:10], start=1):
        if rg["arm"] == "2A_025m":
            arr_a, v_a = test_arrays_cache[rg["area_id"]]
            render_baltic_crop_audit(
                [("0.25m Slope (deg)", arr_a), ("Untrawled Slope", np.where(v_a, arr_a, 0.0))],
                rg, rg["px_m"],
                f"Baltic Ring #{idx_r} {rg['area_id']} | diam={rg['diam_m']}m oct={rg['octants']}/8 ({rg['lat']},{rg['lon']})",
                PREV_DIR / f"BALTIC_RING_{idx_r:02d}_{rg['area_id']}.png",
                half_px=180,
            )
        else:
            render_baltic_crop_audit(
                [("2024 Steepness", s24), ("2025 Steepness", s25), ("2024∩2025 Persist Min", s_persist)],
                rg, rg["px_m"],
                f"Baltic Ring #{idx_r} Fehmarn 24x25 | diam={rg['diam_m']}m oct={rg['octants']}/8 ({rg['lat']},{rg['lon']})",
                PREV_DIR / f"BALTIC_RING_{idx_r:02d}_Fehmarn.png",
                half_px=160,
            )

    # Save full structured outputs
    huron_valid_km2 = round(sum(t["valid_km2"] for t in huron_tiles_summary), 3)
    baltic_2a_km2 = round(sum(a["untrawled_km2"] for a in baltic_areas_summary if a["id"] != "BALTIC_Fehmarn_24x25"), 3)
    baltic_total_km2 = round(baltic_2a_km2 + overlap_km2, 3)

    summary = {
        "issue": 143,
        "protocol_lock_sha256": "3ea4cf7fca82a8c03df2c7ac8d7dc1de24c0d2d0334585282e673bf3007df88c",
        "elapsed_sec": round(time.time() - t0, 1),
        "calibration": {
            "arm1_wreck_controls_passed": sum(1 for c in huron_controls if c["control_passed"]),
            "arm1_wreck_controls_total": len(huron_controls),
            "arm1_synth_walls_recovered": huron_wall_hits,
            "arm1_synth_walls_total": 12,
            "arm1_synth_seams_rejected": huron_seam_rejs,
            "arm1_synth_seams_total": 12,
            "arm2_synth_walls_recovered": baltic_synth_walls_hits,
            "arm2_synth_walls_total": baltic_synth_walls_total,
            "arm2_transient_trawl_rejected": baltic_transient_rejs,
            "arm2_transient_trawl_total": 10,
            "all_gates_passed": bool(
                sum(1 for c in huron_controls if c["control_passed"]) >= 2
                and huron_wall_hits >= 10
                and huron_seam_rejs >= 11
                and baltic_synth_walls_hits >= 8
                and baltic_transient_rejs >= 9
            ),
            "arm1_controls": huron_controls,
            "arm1_synth_details": huron_synth_details,
        },
        "arm1_huron": {
            "tiles_scanned": len(huron_tiles_summary),
            "valid_km2": huron_valid_km2,
            "enc_cultural_features": len(enc_feats),
            "total_linear_raw": len(huron_all_cands),
            "total_linear_unmasked": len(huron_unmasked),
            "total_rings_unmasked": len(huron_rings_unm),
            "total_corners": len(huron_corners),
            "total_v_funnels": len(huron_vfunnels),
            "tiles": huron_tiles_summary,
            "top_unmasked": huron_unmasked[:30],
            "rings_unmasked": huron_rings_unm[:20],
            "corners": huron_corners[:20],
            "v_funnels": huron_vfunnels[:20],
        },
        "arm2_baltic": {
            "areas": baltic_areas_summary,
            "untrawled_2a_km2": baltic_2a_km2,
            "fehmarn_24x25_overlap_km2": overlap_km2,
            "total_valid_km2": baltic_total_km2,
            "munition_piles_loaded": len(munitions),
            "total_linear_unmasked": len(baltic_unmasked),
            "total_rings": len(baltic_rings),
            "total_corners": len(baltic_corners),
            "total_v_funnels": len(baltic_vfunnels),
            "top_unmasked": baltic_unmasked[:30],
            "rings": baltic_rings[:20],
            "corners": baltic_corners[:20],
            "v_funnels": baltic_vfunnels[:20],
        },
    }
    (RES / "scan_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (RES / "manifest_hashes.json").write_text(json.dumps(hashes, indent=2, sort_keys=True), encoding="utf-8")

    print("\n================ DONE ================")
    print(f"Elapsed: {summary['elapsed_sec']}s | ALL 4 CALIBRATION GATES PASSED: {summary['calibration']['all_gates_passed']}")
    print(f"ARM 1 (Lake Huron): {huron_valid_km2} km2 valid | {len(huron_unmasked)} unmasked linear | "
          f"{len(huron_rings_unm)} unmasked rings | {len(huron_corners)} corners | {len(huron_vfunnels)} V-funnels")
    print(f"ARM 2 (Western Baltic): {baltic_total_km2} km2 valid | {len(baltic_unmasked)} unmasked persistent linear | "
          f"{len(baltic_rings)} rings | {len(baltic_corners)} corners | {len(baltic_vfunnels)} V-funnels")


if __name__ == "__main__":
    main()
