"""Shared helpers: load the study's own detector (from the copied, read-through program) and the cached tiles."""
import sys, math, json, pathlib
import numpy as np
from PIL import Image
A = pathlib.Path(__import__("os").environ.get("SPOTCHECK_AREA", "."))  # a folder holding work/questions/drowned-walls with its data cache
STUDY = A / "work/questions/drowned-walls"
sys.path.insert(0, str(STUDY / "analysis"))
import run_drowned_walls as rdw  # noqa: E402

def load_tiles():
    specs = rdw.build_tile_specs()
    out = {}
    for sp in specs:
        tp = STUDY / "data/bag_tiles" / f"{sp['id']}.tif"
        if tp.stat().st_size < 4096:
            z = np.full((512, 512), np.nan, dtype=np.float32)
        else:
            z = np.array(Image.open(tp), dtype=np.float32)
        out[sp["id"]] = (sp, z)
    return specs, out

def background_tiles(specs, tiles, rule="program"):
    """rule='program': valid>=60% and median depth in [-55,-12] (run_drowned_walls.py line 607).
    rule='protocol': median depth in [-45,-15] (protocol.md line 20), valid>=60%."""
    bg = []
    for sp in specs:
        if sp["is_control"]: continue
        _, z = tiles[sp["id"]]
        v = np.isfinite(z) & (z >= -120) & (z <= -2)
        if v.mean() < 0.6: continue
        med = float(np.median(z[v]))
        lo, hi = (-55.0, -12.0) if rule == "program" else (-45.0, -15.0)
        if lo <= med <= hi:
            bg.append((sp, z, v))
    return bg

def wall_profile(across, kind, width, height, px=2.0):
    """Cross-section height at signed distance `across` (m) from the wall axis.
    gauss: study's Gaussian with FWHM=width. box_avg: rectangular wall of given width averaged over a px-wide pixel footprint."""
    if kind == "gauss":
        return height * np.exp(-0.5 * (across / (width / 2.355)) ** 2)
    if kind == "box_avg":
        lo = np.maximum(across - px / 2, -width / 2); hi = np.minimum(across + px / 2, width / 2)
        return height * np.clip(hi - lo, 0, None) / px
    raise ValueError(kind)

def plant(z, v, cx, cy, az_deg, length, width, height, kind="gauss", gap_on=None, gap_off=None, bends=None, px=2.0):
    """Plant a wall centred at pixel (cx, cy). Optional dashed pattern (gap_on m of wall, gap_off m of gap).
    bends: list of (fraction_along, delta_az_deg) not used for simplicity; zigzag handled by plant_zigzag."""
    h, w = z.shape
    rad = math.radians(az_deg); vx, vy = math.sin(rad), -math.cos(rad); nx, ny = -vy, vx
    yy, xx = np.mgrid[0:h, 0:w]
    dx = (xx - cx) * px; dy = (yy - cy) * px
    along = dx * vx + dy * vy; across = dx * nx + dy * ny
    m = np.abs(along) <= length / 2
    if gap_on:
        m &= np.mod(along + length / 2, gap_on + gap_off) < gap_on
    wall = wall_profile(across, kind, width, height, px) * m
    return np.where(v, z + wall.astype(np.float32), z)

def hit(det, cx, cy, az, length, crit="study", px=2.0):
    """study: unmasked candidate within 35 px of centre, az within 12 deg, L>=120 m (run_drowned_walls.py 622-632).
    any: any unmasked candidate whose centroid is within 6 px of the wall axis and within its along-extent, az within 12 deg."""
    rad = math.radians(az); vx, vy = math.sin(rad), -math.cos(rad); nx, ny = -vy, vx
    for c in det["candidates"]:
        if not c["unmasked"]: continue
        da = abs(c["azimuth_deg"] - az); da = min(da, 180 - da)
        if da > 12: continue
        x, y = c["px_centroid"]
        if crit == "study":
            if math.hypot(x - cx, y - cy) <= 35 and c["length_m"] >= 120: return True
        else:
            al = ((x - cx) * vx + (y - cy) * vy) * px; ac = ((x - cx) * nx + (y - cy) * ny) * px
            if abs(ac) <= 12 and abs(al) <= length / 2 + 20: return True
    return False
