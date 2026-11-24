#!/usr/bin/env python3
"""Pre-registered 2 m NOAA multibeam seafloor sonar scan for drowned Ice Age walls (#84).

Implements questions/drowned-walls/protocol.md (locked in protocol.lock).
1. Exports ~2.0 m/px F32 GeoTIFFs from NOAA NCEI bag_bathymetry ImageServer (cached locally).
2. Queries NOAA ENC Direct enc_approach layers (wrecks, obstructions, cables, pipelines, breakwaters).
3. Calibrates on 2 real submerged/emergent stone breakwaters + 10 planted Blinkerwall-scale walls
   and 10 planted mosaic step seams on real 2 m NOAA seafloor noise.
4. Scans 40 pre-registered Ice Age paleo-shoreline tiles (~42 km²) across 4 US shelves
   (California Santarosae, Block Island Sound, Hudson Paleo-Channel, Florida Keys).
5. Renders side-by-side hillshade + BPI audit PNGs for direct visual inspection.
"""
from __future__ import annotations

import collections
import concurrent.futures
import hashlib
import io
import json
import math
import pathlib
import time
import urllib.parse
import urllib.request
from typing import Any

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
TILES_DIR = DATA / "bag_tiles"
ENC_DIR = DATA / "enc_cache"
PREV_DIR = DATA / "previews"
RES = ROOT / "results"

ENC_LAYERS = {
    36: "Obstruction_pt",
    39: "Wreck_pt",
    89: "Shoreline_Construction_ln",
    103: "Obstruction_ln",
    118: "Cable_Submarine_ln",
    119: "Pipeline_Submarine_ln",
    143: "Shoreline_Construction_area",
    161: "Obstruction_area",
    163: "Wreck_area",
    169: "Cable_Area",
    172: "Pipeline_Area",
}


def make_tile_bbox(center_lat: float, center_lon: float, dlat: float = 0.0092) -> tuple[float, float, float, float]:
    dlon = dlat / math.cos(math.radians(center_lat))
    return (
        round(center_lon - dlon / 2.0, 6),
        round(center_lat - dlat / 2.0, 6),
        round(center_lon + dlon / 2.0, 6),
        round(center_lat + dlat / 2.0, 6),
    )


def build_tile_specs() -> list[dict[str, Any]]:
    specs: list[dict[str, Any]] = [
        # 2 real stone-breakwater positive controls
        {"id": "CTRL_DELAWARE", "region": "Positive Control", "is_control": True, "bbox": make_tile_bbox(38.814, -75.108)},
        {"id": "CTRL_PTJUDITH", "region": "Positive Control", "is_control": True, "bbox": make_tile_bbox(41.363, -71.500)},
    ]

    def add_grid(prefix: str, region: str, lon_min: float, lon_max: float, lat_min: float, lat_max: float, nx: int, ny: int):
        lons = np.linspace(lon_min, lon_max, nx)
        lats = np.linspace(lat_min, lat_max, ny)
        idx = 1
        for lat in lats:
            for lon in lons:
                specs.append({
                    "id": f"{prefix}_{idx:02d}",
                    "region": region,
                    "is_control": False,
                    "bbox": make_tile_bbox(float(lat), float(lon)),
                })
                idx += 1

    # Region A: California Channel Islands (Santarosae Ice Age mega-island, 12 tiles)
    add_grid("CA_ANACAPA", "CA Santarosae (Channel Islands)", -119.50, -119.43, 33.995, 34.025, 3, 2)
    add_grid("CA_SROSA", "CA Santarosae (Channel Islands)", -120.00, -119.93, 33.925, 33.955, 3, 2)
    # Region B: Block Island Sound (New England drowned moraine shelf, 10 tiles)
    add_grid("NE_BLOCK", "NE Block Island Sound", -71.58, -71.48, 41.135, 41.165, 5, 2)
    # Region C: NY Bight / Drowned Hudson Paleo-River Shelf (10 tiles)
    add_grid("NY_HUDSON", "NY Hudson Paleo-Channel", -73.85, -73.75, 40.395, 40.425, 5, 2)
    # Region D: Florida Keys Submerged Karst Shelf (8 tiles)
    add_grid("FL_KEYS", "FL Keys Submerged Shelf", -81.85, -81.77, 24.455, 24.485, 4, 2)
    return specs


def fetch_bag_tile(spec: dict[str, Any], size: int = 512) -> tuple[np.ndarray, pathlib.Path]:
    TILES_DIR.mkdir(parents=True, exist_ok=True)
    tp = TILES_DIR / f"{spec['id']}.tif"
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
                # ArcGIS ImageServer returns a ~954-byte sparse header-only TIFF when tile has 0% BAG coverage
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


def fetch_enc_features(spec: dict[str, Any]) -> list[dict[str, Any]]:
    """Query NOAA ENC Direct enc_approach layers for charted wrecks/obstructions/cables/pipelines/breakwaters."""
    ENC_DIR.mkdir(parents=True, exist_ok=True)
    cp = ENC_DIR / f"{spec['id']}_enc.json"
    if cp.exists() and cp.stat().st_size >= 2:
        return json.loads(cp.read_text(encoding="utf-8"))

    lon0, lat0, lon1, lat1 = spec["bbox"]
    # Expand by ~200 m buffer
    pad = 0.0022
    geom = f"{lon0 - pad},{lat0 - pad},{lon1 + pad},{lat1 + pad}"
    feats = []
    for lyr_id, lyr_name in ENC_LAYERS.items():
        url = (
            f"https://encdirect.noaa.gov/arcgis/rest/services/encdirect/enc_approach/MapServer/{lyr_id}/query?"
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
            with urllib.request.urlopen(req, timeout=15) as r:
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
                    feats.append({"layer": lyr_name, "pts": pts})
        except Exception:
            pass
    cp.write_text(json.dumps(feats), encoding="utf-8")
    return feats


def haversine_m(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    r = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2.0) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2.0) ** 2
    return 2.0 * r * math.asin(min(1.0, math.sqrt(a)))


def compute_masked_bpi(z: np.ndarray, valid_mask: np.ndarray, sigma_px: float = 12.0) -> np.ndarray:
    """Normalized Gaussian convolution for Bathymetric Position Index inside valid mask."""
    v = valid_mask.astype(np.float64)
    zf = np.where(valid_mask, z.astype(np.float64), 0.0)
    num = ndimage.gaussian_filter(zf, sigma=sigma_px, mode="nearest")
    den = ndimage.gaussian_filter(v, sigma=sigma_px, mode="nearest")
    bg = np.where(den > 1e-3, num / np.maximum(den, 1e-6), np.nan)
    bpi = np.where(valid_mask, zf - bg, np.nan)
    return bpi.astype(np.float32)


def detect_structures(
    z: np.ndarray,
    bbox: tuple[float, float, float, float],
    enc_features: list[dict[str, Any]] | None = None,
    px_m: float = 2.0,
    z_min: float = -120.0,
    z_max: float = -2.0,
    bpi_thresh: float = 0.35,
    erode_px: int = 3,
    is_control: bool = False,
) -> dict[str, Any]:
    """Run pre-registered geometric ridge, corner, and ring detection + artifact/ENC filtering."""
    h, w = z.shape
    lon0, lat0, lon1, lat1 = bbox
    # Allow shallower depth up to +1.0 m for partially emergent breakwater controls
    z_hi = 1.5 if is_control else z_max
    raw_valid = np.isfinite(z) & (z >= z_min) & (z <= z_hi)
    if raw_valid.mean() < 0.03:
        return {
            "valid_pct": round(100.0 * float(raw_valid.mean()), 2),
            "depth_median": None,
            "candidates": [],
            "corners": [],
            "rings": [],
            "bpi": None,
            "valid_mask": raw_valid,
        }

    # Erode valid mask away from noData borders to suppress mosaic step artifacts
    valid_eroded = ndimage.binary_erosion(raw_valid, iterations=erode_px) if erode_px > 0 else raw_valid.copy()
    # Keep border pixels inside tile edge (not touching noData)
    bpi = compute_masked_bpi(z, raw_valid, sigma_px=12.0)

    # Positive ridge mask
    pos_mask = valid_eroded & np.isfinite(bpi) & (bpi >= bpi_thresh)
    labeled, n_comp = ndimage.label(pos_mask, structure=np.ones((3, 3), dtype=int))

    # Pre-flatten ENC points for distance checks
    enc_pts = []
    for f in (enc_features or []):
        lyr = f["layer"]
        for x, y in f["pts"]:
            enc_pts.append((x, y, lyr))

    def px_to_lonlat(r: float, c: float) -> tuple[float, float]:
        lon = lon0 + (c / max(1, w - 1)) * (lon1 - lon0)
        lat = lat1 - (r / max(1, h - 1)) * (lat1 - lat0)
        return lon, lat

    candidates = []
    rings = []
    # Also compute border mask of valid_eroded for AXIS_SEAM touching check
    eroded_edge = valid_eroded & (~ndimage.binary_erosion(valid_eroded, iterations=2))

    if n_comp > 0:
        slices = ndimage.find_objects(labeled)
        for comp_id, sl in enumerate(slices, start=1):
            if sl is None:
                continue
            sub = (labeled[sl] == comp_id)
            area = int(sub.sum())
            if area < 40:
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
            # Major axis vector (vx, vy) in image coords (x=col right, y=row down)
            vx, vy = float(eigvecs[0, 1]), float(eigvecs[1, 1])
            proj_maj = dx * vx + dy * vy
            proj_min = -dx * vy + dy * vx
            L_m = float(proj_maj.max() - proj_maj.min()) * px_m
            W_m = float(np.percentile(proj_min, 95) - np.percentile(proj_min, 5)) * px_m
            mean_bpi = float(np.nanmean(bpi[rs, cs]))
            max_bpi = float(np.nanmax(bpi[rs, cs]))
            mean_z = float(np.nanmean(z[rs, cs]))

            # Check closed ring enclosure (non-linear hollow structure 25-200 m)
            if lin < 0.75 and 25.0 <= L_m <= 200.0 and W_m >= 20.0:
                # Check if centroid pixel (inside 3x3) has BPI <= 0.05 (hollow interior)
                ri, ci = int(round(cy)), int(round(cx))
                if 2 <= ri < h - 2 and 2 <= ci < w - 2 and valid_eroded[ri, ci]:
                    center_bpi = float(np.nanmean(bpi[ri - 2:ri + 3, ci - 2:ci + 3]))
                    # Check angular coverage around centroid (>= 7 of 8 octants occupied)
                    angs = np.arctan2(dy, dx)
                    octs = set(int(((a + math.pi) / (2 * math.pi)) * 8) % 8 for a in angs)
                    if center_bpi <= 0.05 and len(octs) >= 7:
                        clon, clat = px_to_lonlat(cy, cx)
                        rings.append({
                            "comp_id": comp_id,
                            "lat": round(clat, 6),
                            "lon": round(clon, 6),
                            "diam_m": round(L_m, 1),
                            "mean_bpi": round(mean_bpi, 3),
                            "center_bpi": round(center_bpi, 3),
                            "mean_z": round(mean_z, 2),
                        })

            if L_m < 60.0 or W_m > 20.0 or lin < 0.90 or mean_bpi < bpi_thresh:
                continue

            # Azimuth in [0, 180) degrees clockwise from North (vx=east, -vy=north)
            az = math.degrees(math.atan2(vx, -vy)) % 180.0
            # Endpoints in pixel coordinates
            pmin_i = int(np.argmin(proj_maj))
            pmax_i = int(np.argmax(proj_maj))
            r_a, c_a = float(rs[pmin_i]), float(cs[pmin_i])
            r_b, c_b = float(rs[pmax_i]), float(cs[pmax_i])

            # 1. Step-edge / mosaic-seam test: parallel flank strips 8..20 m (4..10 px) left and right
            nx_v, ny_v = -vy, vx  # unit normal
            # Sample 15 points along ridge axis
            ts = np.linspace(float(proj_maj.min()) * 0.8, float(proj_maj.max()) * 0.8, 15)
            z_left, z_right = [], []
            for t in ts:
                bx, by = cx + t * vx, cy + t * vy
                for off in (5.0, 7.0, 9.0):  # 10, 14, 18 m
                    for sign, bucket in ((1.0, z_left), (-1.0, z_right)):
                        sx = int(round(bx + sign * off * nx_v))
                        sy = int(round(by + sign * off * ny_v))
                        if 0 <= sy < h and 0 <= sx < w and raw_valid[sy, sx]:
                            bucket.append(float(z[sy, sx]))
            flank_step = abs(float(np.median(z_left)) - float(np.median(z_right))) if (len(z_left) >= 5 and len(z_right) >= 5) else 0.0
            is_seam_step = bool(flank_step > 0.65 * max_bpi)

            # 2. Axis-aligned raster seam check (within +/-1.5 deg of 0 or 90 AND (>60% tile or touches mask edge))
            ang_card = min(az, abs(az - 90.0), abs(az - 180.0))
            touches_edge = bool(eroded_edge[rs, cs].sum() >= 5)
            is_axis_seam = bool((ang_card <= 1.5) and (L_m > 600.0 or touches_edge))

            # 3. Periodic sandwave-train check: 1D cross-axis BPI profile (-80 m to +80 m, step 2 m)
            offs_px = np.arange(-40, 41, 1)  # -80 m to +80 m
            prof = []
            for op in offs_px:
                vals = []
                for t in ts[::2]:
                    sx = int(round(cx + t * vx + op * nx_v))
                    sy = int(round(cy + t * vy + op * ny_v))
                    if 0 <= sy < h and 0 <= sx < w and raw_valid[sy, sx] and np.isfinite(bpi[sy, sx]):
                        vals.append(float(bpi[sy, sx]))
                prof.append(float(np.mean(vals)) if vals else 0.0)
            prof_arr = np.array(prof)
            center_peak = max(mean_bpi, float(prof_arr[38:43].max()))
            # Count distinct flank peaks at |offset| in [6..38 px] (= 12..76 m) >= 0.40 * center_peak
            flank_peaks = 0
            for idx_p in range(2, len(prof_arr) - 2):
                dist_px = abs(offs_px[idx_p])
                if 6 <= dist_px <= 38:
                    if prof_arr[idx_p] >= 0.40 * center_peak and prof_arr[idx_p] == prof_arr[idx_p - 2:idx_p + 3].max():
                        flank_peaks += 1
            is_sandwave = bool(flank_peaks >= 2)

            # 4. NOAA ENC charted modern overlay check (<= 150 m from centroid or either endpoint)
            clon, clat = px_to_lonlat(cy, cx)
            alon, alat = px_to_lonlat(r_a, c_a)
            blon, blat = px_to_lonlat(r_b, c_b)
            min_enc_m = 1e9
            nearest_enc_layer = ""
            for ex, ey, lyr in enc_pts:
                for plon, plat in ((clon, clat), (alon, alat), (blon, blat)):
                    d_m = haversine_m(plon, plat, ex, ey)
                    if d_m < min_enc_m:
                        min_enc_m = d_m
                        nearest_enc_layer = lyr
            is_charted = bool(min_enc_m <= 150.0)

            flags = []
            if is_seam_step:
                flags.append("SEAM_STEP")
            if is_axis_seam:
                flags.append("AXIS_SEAM")
            if is_sandwave:
                flags.append("SANDWAVE_PERIODIC")
            if is_charted:
                flags.append(f"CHARTED_MODERN:{nearest_enc_layer}")

            # Composite wall score (favors long, straight, prominent ridges)
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

    # Check right-angle rectilinear corners among unmasked linear candidates
    unmasked_list = [c for c in candidates if c["unmasked"]]
    corners = []
    for i in range(len(unmasked_list)):
        for j in range(i + 1, len(unmasked_list)):
            a, b = unmasked_list[i], unmasked_list[j]
            da = abs(a["azimuth_deg"] - b["azimuth_deg"])
            da = min(da, 180.0 - da)
            if 75.0 <= da <= 105.0:
                # Min distance between their endpoints (in meters)
                ea = [(a["px_endpoints"][0], a["px_endpoints"][1]), (a["px_endpoints"][2], a["px_endpoints"][3])]
                eb = [(b["px_endpoints"][0], b["px_endpoints"][1]), (b["px_endpoints"][2], b["px_endpoints"][3])]
                dmin = min(math.hypot(p[0] - q[0], p[1] - q[1]) * px_m for p in ea for q in eb)
                if dmin <= 40.0:
                    corners.append({
                        "comp_a": a["comp_id"],
                        "comp_b": b["comp_id"],
                        "angle_deg": round(da, 1),
                        "gap_m": round(dmin, 1),
                    })

    return {
        "valid_pct": round(100.0 * float(raw_valid.mean()), 2),
        "depth_median": round(float(np.median(z[raw_valid])), 2),
        "depth_min": round(float(z[raw_valid].min()), 2),
        "depth_max": round(float(z[raw_valid].max()), 2),
        "candidates": candidates,
        "corners": corners,
        "rings": rings,
        "bpi": bpi,
        "valid_mask": raw_valid,
    }


def inject_synthetic_wall(z: np.ndarray, valid_mask: np.ndarray, length_m: float = 250.0, width_m: float = 4.0, height_m: float = 0.70, az_deg: float = 37.0, px_m: float = 2.0) -> tuple[np.ndarray, tuple[float, float]]:
    """Inject a Blinkerwall-scale linear stone wall onto a real bathymetry grid inside valid pixels."""
    out = z.copy()
    h, w = z.shape
    # Pick a well-interior valid pixel center (at least 90 px from edges)
    interior = ndimage.binary_erosion(valid_mask, iterations=75)
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
    out = np.where(valid_mask, out + wall.astype(np.float32), out)
    return out, (float(cx), float(cy))


def inject_synthetic_step_seam(z: np.ndarray, valid_mask: np.ndarray, step_m: float = 0.70, az_deg: float = 37.0, px_m: float = 2.0) -> np.ndarray:
    """Inject a 0.70 m one-sided multibeam mosaic datum offset step seam (negative control)."""
    out = z.copy()
    h, w = z.shape
    cy, cx = h // 2, w // 2
    rad = math.radians(az_deg)
    vx, vy = math.sin(rad), -math.cos(rad)
    nx, ny = -vy, vx
    yy, xx = np.mgrid[0:h, 0:w]
    across = ((xx - cx) * nx + (yy - cy) * ny) * px_m
    # Smooth 2 m step + slight positive edge bump to stress-test SEAM_STEP filter
    step = step_m * (across >= 0).astype(np.float32) + 0.15 * np.exp(-0.5 * (across / 2.0) ** 2).astype(np.float32)
    return np.where(valid_mask, out + step, out)


def render_hillshade_preview(z: np.ndarray, bpi: np.ndarray, valid_mask: np.ndarray, candidates: list[dict[str, Any]], title: str, out_path: pathlib.Path) -> None:
    """Render side-by-side shaded-relief hillshade (left) + BPI ridge map with candidate boxes (right)."""
    h, w = z.shape
    # Fill NaNs smoothly only for gradient calculation
    z_fill = np.where(valid_mask, z, np.nanmedian(z[valid_mask]) if valid_mask.any() else 0.0)
    gy, gx = np.gradient(z_fill, 2.0)
    # 3x vertical exaggeration hillshade from NW (315 deg, alt 35 deg)
    vx, vy = gx * 3.0, gy * 3.0
    slope = np.arctan(np.hypot(vx, vy))
    aspect = np.arctan2(-vy, vx)
    az_r = math.radians(315.0)
    alt_r = math.radians(35.0)
    hs = np.sin(alt_r) * np.cos(slope) + np.cos(alt_r) * np.sin(slope) * np.cos(az_r - aspect)
    hs_u8 = np.clip((hs + 0.1) * 230, 0, 255).astype(np.uint8)
    # Colorize hillshade slightly bathymetric slate-blue
    r_ch = np.where(valid_mask, (hs_u8 * 0.84).astype(np.uint8), 20)
    g_ch = np.where(valid_mask, (hs_u8 * 0.92).astype(np.uint8), 26)
    b_ch = np.where(valid_mask, np.clip(hs_u8 * 1.02, 0, 255).astype(np.uint8), 38)
    left = np.stack([r_ch, g_ch, b_ch], axis=-1)

    # Right panel: BPI heatmap (-0.8 m blue -> 0 gray -> +0.8 m bright copper/yellow)
    bpi_c = np.clip(np.where(valid_mask & np.isfinite(bpi), bpi, 0.0), -0.8, 0.8) / 0.8
    rr = np.where(valid_mask, np.clip(128 + bpi_c * 127, 0, 255).astype(np.uint8), 20)
    gg = np.where(valid_mask, np.clip(128 + np.where(bpi_c > 0, bpi_c * 40, bpi_c * 60), 0, 255).astype(np.uint8), 26)
    bb = np.where(valid_mask, np.clip(128 - bpi_c * 110, 0, 255).astype(np.uint8), 38)
    right = np.stack([rr, gg, bb], axis=-1)

    canvas = Image.new("RGB", (w * 2 + 12, h + 34), (15, 23, 42))
    canvas.paste(Image.fromarray(left), (0, 34))
    canvas.paste(Image.fromarray(right), (w + 12, 34))
    draw = ImageDraw.Draw(canvas)
    draw.text((10, 10), f"{title}   |   Left: 2 m Multibeam Hillshade (3x VE)   |   Right: Local BPI (±0.8 m) & Detected Ridges", fill=(241, 245, 249))

    for c in candidates[:12]:
        x1, y1, x2, y2 = c["px_endpoints"]
        col = (250, 204, 21) if c["unmasked"] else (56, 189, 248)  # yellow = unmasked, cyan = filtered/charted
        # Draw on both panels (subtle circle/line)
        for xoff in (0, w + 12):
            draw.line([(x1 + xoff, y1 + 34), (x2 + xoff, y2 + 34)], fill=col, width=2)
            cx, cy = c["px_centroid"]
            draw.ellipse([cx + xoff - 6, cy + 34 - 6, cx + xoff + 6, cy + 34 + 6], outline=col, width=2)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path)


def main() -> None:
    RES.mkdir(parents=True, exist_ok=True)
    PREV_DIR.mkdir(parents=True, exist_ok=True)
    specs = build_tile_specs()
    print(f"=== DOWNLOADING / LOADING {len(specs)} NOAA 2m BAG TILES + ENC OVERLAYS ===", flush=True)

    def load_one(sp):
        arr, tp = fetch_bag_tile(sp)
        enc = fetch_enc_features(sp)
        return sp["id"], arr, tp, enc

    loaded = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        for tid, arr, tp, enc in ex.map(load_one, specs):
            loaded[tid] = (arr, tp, enc)

    # Compute SHA-256 over all cached GeoTIFFs and ENC JSONs
    h = hashlib.sha256()
    for p in sorted(list(TILES_DIR.glob("*.tif")) + list(ENC_DIR.glob("*.json"))):
        h.update(p.name.encode())
        h.update(hashlib.sha256(p.read_bytes()).digest())
    data_digest = h.hexdigest()

    # === 1. EVALUATE ALL TILES ===
    ctrl_results = []
    search_results = []
    all_unmasked = []
    all_candidates = []
    valid_bg_tiles = []

    for sp in specs:
        arr, _, enc = loaded[sp["id"]]
        det = detect_structures(arr, sp["bbox"], enc_features=enc, is_control=sp["is_control"])
        rec = {
            "id": sp["id"],
            "region": sp["region"],
            "bbox": list(sp["bbox"]),
            "valid_pct": det["valid_pct"],
            "depth_median": det["depth_median"],
            "depth_min": det.get("depth_min"),
            "depth_max": det.get("depth_max"),
            "n_enc_features": len(enc),
            "n_candidates_total": len(det["candidates"]),
            "n_unmasked": sum(1 for c in det["candidates"] if c["unmasked"]),
            "n_corners": len(det["corners"]),
            "n_rings": len(det["rings"]),
            "candidates": det["candidates"],
            "corners": det["corners"],
            "rings": det["rings"],
        }
        if sp["is_control"]:
            ctrl_results.append(rec)
            if det["bpi"] is not None:
                render_hillshade_preview(arr, det["bpi"], det["valid_mask"], det["candidates"], sp["id"], PREV_DIR / f"{sp['id']}.png")
        else:
            search_results.append(rec)
            for c in det["candidates"]:
                c_full = {"tile_id": sp["id"], "region": sp["region"], **c}
                all_candidates.append(c_full)
                if c["unmasked"]:
                    all_unmasked.append(c_full)
            if det["valid_pct"] >= 60.0 and det["depth_median"] is not None and -55.0 <= det["depth_median"] <= -12.0:
                valid_bg_tiles.append((sp, arr, det["valid_mask"]))

    # === 2. PLANTED BLINKERWALL & STEP-SEAM SENSITIVITY GATE ON REAL 2 m NOAA NOISE ===
    print("\n=== RUNNING 10-TRIAL PLANTED BLINKERWALL & STEP-SEAM CALIBRATION ON REAL NOAA NOISE ===", flush=True)
    rng = np.random.default_rng(20261124)
    n_trials = min(10, len(valid_bg_tiles))
    wall_recovered = 0
    seam_rejected = 0
    planted_details = []
    for i in range(n_trials):
        sp, arr, vmask = valid_bg_tiles[i]
        az = float(rng.choice([25.0, 38.0, 52.0, 67.0, 118.0, 134.0, 149.0]))
        z_wall, (cx, cy) = inject_synthetic_wall(arr, vmask, length_m=250.0, width_m=4.0, height_m=0.70, az_deg=az)
        d_wall = detect_structures(z_wall, sp["bbox"], enc_features=[], is_control=False)
        # Check if an unmasked linear ridge was recovered near (cx, cy) with matching azimuth (+/- 10 deg) and length >= 120 m
        hit = False
        for c in d_wall["candidates"]:
            if not c["unmasked"]:
                continue
            dist_px = math.hypot(c["px_centroid"][0] - cx, c["px_centroid"][1] - cy)
            da = abs(c["azimuth_deg"] - az)
            da = min(da, 180.0 - da)
            if dist_px <= 35.0 and da <= 12.0 and c["length_m"] >= 120.0:
                hit = True
                break
        wall_recovered += int(hit)
        if i == 0 and d_wall["bpi"] is not None:
            render_hillshade_preview(z_wall, d_wall["bpi"], d_wall["valid_mask"], d_wall["candidates"], f"PLANTED_BLINKERWALL_{sp['id']}", PREV_DIR / "CALIB_PLANTED_WALL.png")

        # Step-seam negative control
        z_seam = inject_synthetic_step_seam(arr, vmask, step_m=0.70, az_deg=az)
        d_seam = detect_structures(z_seam, sp["bbox"], enc_features=[], is_control=False)
        # Did the injected center seam slip through unmasked?
        seam_fp = False
        for c in d_seam["candidates"]:
            if not c["unmasked"]:
                continue
            dist_px = math.hypot(c["px_centroid"][0] - 256.0, c["px_centroid"][1] - 256.0)
            da = abs(c["azimuth_deg"] - az)
            da = min(da, 180.0 - da)
            if dist_px <= 40.0 and da <= 10.0 and c["length_m"] >= 120.0:
                seam_fp = True
                break
        seam_rejected += int(not seam_fp)
        planted_details.append({"tile_id": sp["id"], "az_deg": az, "wall_recovered": hit, "seam_rejected": not seam_fp})

    # === 3. RENDER TOP-8 UNMASKED ANOMALY PREVIEWS FOR DIRECT VISUAL AUDIT ===
    all_unmasked.sort(key=lambda c: -c["score"])
    top_tiles_rendered = []
    seen_t = set()
    for c in all_unmasked:
        tid = c["tile_id"]
        if tid in seen_t:
            continue
        seen_t.add(tid)
        sp = next(s for s in specs if s["id"] == tid)
        arr, _, enc = loaded[tid]
        det = detect_structures(arr, sp["bbox"], enc_features=enc, is_control=False)
        out_png = PREV_DIR / f"TOP_{len(top_tiles_rendered)+1}_{tid}.png"
        render_hillshade_preview(arr, det["bpi"], det["valid_mask"], det["candidates"], f"TOP #{len(top_tiles_rendered)+1}: {tid} ({sp['region']})", out_png)
        top_tiles_rendered.append({"rank": len(top_tiles_rendered) + 1, "tile_id": tid, "png": str(out_png), "top_candidate": c})
        if len(top_tiles_rendered) >= 8:
            break

    # Region summary
    by_reg = collections.defaultdict(lambda: {"n_tiles": 0, "valid_area_km2": 0.0, "n_cand_total": 0, "n_unmasked": 0, "n_charted": 0, "n_seam_or_sandwave": 0, "n_corners": 0, "n_rings": 0})
    for r in search_results:
        b = by_reg[r["region"]]
        b["n_tiles"] += 1
        b["valid_area_km2"] += 1.04 * (r["valid_pct"] / 100.0)
        b["n_cand_total"] += r["n_candidates_total"]
        b["n_unmasked"] += r["n_unmasked"]
        b["n_corners"] += r["n_corners"]
        b["n_rings"] += r["n_rings"]
        for c in r["candidates"]:
            if any(f.startswith("CHARTED_MODERN") for f in c["flags"]):
                b["n_charted"] += 1
            elif c["flags"]:
                b["n_seam_or_sandwave"] += 1
    for b in by_reg.values():
        b["valid_area_km2"] = round(b["valid_area_km2"], 2)

    flag_counts = collections.Counter()
    for c in all_candidates:
        if c["unmasked"]:
            flag_counts["UNMASKED"] += 1
        else:
            for f in c["flags"]:
                flag_counts[f.split(":")[0]] += 1

    summary = {
        "data_archive_sha256": data_digest,
        "calibration": {
            "real_breakwater_controls": ctrl_results,
            "planted_blinkerwall_n": n_trials,
            "planted_blinkerwall_recovered": wall_recovered,
            "planted_step_seam_rejected": seam_rejected,
            "planted_details": planted_details,
        },
        "search_overview": {
            "n_tiles_scanned": len(search_results),
            "total_valid_seafloor_km2": round(sum(b["valid_area_km2"] for b in by_reg.values()), 2),
            "n_candidates_total": len(all_candidates),
            "n_unmasked_total": len(all_unmasked),
            "n_corners_unmasked": sum(r["n_corners"] for r in search_results),
            "n_rings_total": sum(r["n_rings"] for r in search_results),
            "flag_breakdown": dict(flag_counts),
            "by_region": dict(by_reg),
        },
        "top_unmasked_candidates": all_unmasked[:25],
        "top_tiles_rendered": top_tiles_rendered,
        "tiles": search_results,
    }
    out_json = RES / "drowned_walls_summary.json"
    out_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("\n=== CALIBRATION GATE SUMMARY ===", flush=True)
    for cr in ctrl_results:
        print(f"  {cr['id']}: valid={cr['valid_pct']}%, total_ridges={cr['n_candidates_total']}, top={[(c['length_m'], c['max_bpi_m'], c['linearity'], c['flags']) for c in cr['candidates'][:2]]}", flush=True)
    print(f"  Planted 0.70m Blinkerwall recall on real 2m NOAA noise: {wall_recovered}/{n_trials}", flush=True)
    print(f"  Planted 0.70m step-seam rejection on real 2m NOAA noise: {seam_rejected}/{n_trials}", flush=True)

    print("\n=== 40-TILE ICE AGE PALEO-SHORELINE SCAN SUMMARY ===", flush=True)
    print("Overview:", summary["search_overview"], flush=True)
    print("\nTop 12 Unmasked Linear Ridges (for direct visual hillshade audit):", flush=True)
    for idx, c in enumerate(all_unmasked[:12], start=1):
        print(
            f"  #{idx:2d} {c['tile_id']} ({c['region']}) | ({c['lat']}, {c['lon']}) | "
            f"L={c['length_m']}m W={c['width_m']}m lin={c['linearity']} az={c['azimuth_deg']}° "
            f"BPI={c['mean_bpi_m']}/{c['max_bpi_m']}m z={c['mean_depth_m']}m step={c['flank_step_m']}m score={c['score']}",
            flush=True,
        )
    print(f"\nSaved results to {out_json} and previews to {PREV_DIR}", flush=True)


if __name__ == "__main__":
    main()
