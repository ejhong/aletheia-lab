"""Plant walls in the real Baltic 0.25 m test-area slope grids (Test1-Test5) and run the study's own detector
exactly as its scan does (real untrawled mask, 'deg_25cm' mode).

usage: python -I sens_baltic.py <analysis_dir> <Test_Areas.zip> <out.json> [seeds=2] [trials=6]

Elevation walls are rendered at 5 cm, block-averaged to a 1 m grid (the BSH survey resolution stated on the
Zenodo record: "1 m resolution (interpolated to 0.25 m)"), bilinearly interpolated to 0.25 m, turned into a
gradient and added to a background gradient of the grid's own slope magnitude with one random direction per
trial: slope_new = atan(|tan(slope_bg) u + grad(wall)|). The study's own planted wall (+12 deg added straight
to the slope grid, Gaussian 2.5 m wide) is also placed at random untrawled positions for comparison.
A wall is found when an unmasked candidate not present before planting has its centroid within 5 m of the
axis and within its length, azimuth within 15 deg.
"""
import io, json, math, pathlib, sys, time, zipfile
import numpy as np
from PIL import Image
from scipy import ndimage
sys.path.insert(0, sys.argv[1]); sys.path.insert(0, str(pathlib.Path(__file__).parent))
import run_submeter_scan as m
import walls

zpath, outp = sys.argv[2], sys.argv[3]
seeds = int(sys.argv[4]) if len(sys.argv) > 4 else 2; trials = int(sys.argv[5]) if len(sys.argv) > 5 else 6

areas = {}
with zipfile.ZipFile(zpath) as zf:
    for i in range(1, 6):
        tfw = [float(x) for x in zf.read(f"Test{i}.tfw").decode().split()]
        arr = np.array(Image.open(io.BytesIO(zf.read(f"Test{i}.tif"))), dtype=np.float32)
        mk = np.array(Image.open(io.BytesIO(zf.read(f"Test{i}_mask.tif")))); mk = mk[..., 0] if mk.ndim == 3 else mk
        h, w = min(arr.shape[0], mk.shape[0]), min(arr.shape[1], mk.shape[1]); arr, mk = arr[:h, :w], mk[:h, :w]
        valid = np.isfinite(arr) & (arr >= 0) & (arr < 89) & ~ndimage.binary_dilation(mk == 76, iterations=2)
        areas[f"Test{i}"] = (arr, valid, tfw)

def wall_slope_elev(fun, half_px, az, rng):
    """Gradient (gx, gy) at 0.25 m of a wall gridded at 1 m then bilinearly interpolated to 0.25 m."""
    half_1m = int(math.ceil(half_px * 0.25)) + 2
    off = tuple(rng.uniform(-0.5, 0.5, 2))
    e1 = walls.render(fun, 1.0, half_1m, az, sub=0.05, offset=off)
    e25 = ndimage.zoom(e1, 4, order=1, mode="nearest", grid_mode=True)
    c = e25.shape[0] // 2
    e25 = e25[c - half_px:c + half_px, c - half_px:c + half_px]
    gy, gx = np.gradient(e25, 0.25)
    return gx, gy, float(e1.max())

def found(cands, base, cx, cy, az, L, px):
    rad = math.radians(az); vx, vy = math.sin(rad), -math.cos(rad)
    for c in cands:
        if not c["unmasked"]: continue
        x, y = c["px_centroid"]
        if any(math.hypot(x - b[0], y - b[1]) * px <= 5.0 for b in base): continue
        dx, dy = (x - cx) * px, (y - cy) * px
        al = dx * vx + dy * vy; ac = -dx * vy + dy * vx
        daz = abs(c["azimuth_deg"] - az) % 180; daz = min(daz, 180 - daz)
        if abs(ac) <= 5.0 and abs(al) <= L / 2 + 5 and daz <= 15: return True
    return False

def variants(rng):
    return {
        "study_+12deg_slope_bump_60m_random_untrawled": (60.0, None, {}),
        "ridge_2.5m_x_0.6m_60m_(protocol_dims_as_elevation)": (60.0, walls.gaussian_ridge(60, 2.5, 0.6), {}),
        "ridge_2m_x_0.5m_150m": (150.0, walls.gaussian_ridge(150, 2.0, 0.5), {}),
        "blinkerwall_volume_matched_150m": (150.0, *walls.blinkerwall(150, rng)),
        "blinkerwall_upper_bound_150m": (150.0, *walls.blinkerwall_upper(150, rng)),
        "blinkerwall_volume_matched_single_file_150m": (150.0, *walls.blinkerwall_single_file(150, rng)),
    }

res, meta, t0 = {}, {}, time.time()
px = 0.25
for seed in range(seeds):
    rng = np.random.default_rng(2000 + seed)
    for aid, (arr, valid, tfw) in areas.items():
        base_r = m.detect_baltic_slope_block(arr, valid, tfw[4], tfw[5], px, [], mode="deg_25cm")
        base = [c["px_centroid"] for c in base_r["candidates"] if c["unmasked"]]
        for k in range(trials):
            for name, (L, fun, info) in variants(rng).items():
                half = int(math.ceil((L / 2 + 6) / px))
                if 2 * half >= min(arr.shape): 
                    continue
                placed = False
                for _ in range(3000):
                    az = rng.uniform(0, 180)
                    if min(az % 90, 90 - az % 90) < 5: continue
                    cy, cx = int(rng.integers(half, arr.shape[0] - half)), int(rng.integers(half, arr.shape[1] - half))
                    rad = math.radians(az); vx, vy = math.sin(rad), -math.cos(rad)
                    pts = [(cy - 0.5 + s * vy * L / 2 / px, cx - 0.5 + s * vx * L / 2 / px) for s in np.linspace(-1, 1, 41)]
                    if np.mean([valid[int(round(r)), int(round(c))] for r, c in pts]) >= 0.9:
                        placed = True; break
                if not placed:
                    res.setdefault(f"{name}|{aid}", {"n": 0, "found": 0, "not_placeable": 0})["not_placeable"] = res.get(f"{name}|{aid}", {}).get("not_placeable", 0) + 1
                    continue
                sl = (slice(cy - half, cy + half), slice(cx - half, cx + half))
                a2 = arr.copy()
                if fun is None:  # the study's own method: add a +12 deg Gaussian bump to the slope grid
                    sub, (wcx, wcy) = m.inject_baltic_wall_slope(arr[sl], np.ones_like(valid[sl]), 60.0, 2.5, 12.0, az, px)
                    # inject_baltic_wall_slope centres the wall on an interior pixel; recentre our bookkeeping
                    a2[sl] = sub; ccx, ccy = cx - half + wcx, cy - half + wcy
                    gmax = None
                else:
                    gx, gy, gmax = wall_slope_elev(fun, half, az, rng)
                    th = rng.uniform(0, 2 * math.pi); tb = np.tan(np.radians(arr[sl]))
                    a2[sl] = np.degrees(np.arctan(np.hypot(tb * math.cos(th) + gx, tb * math.sin(th) + gy))).astype(np.float32)
                    ccx, ccy = cx - 0.5, cy - 0.5
                r = m.detect_baltic_slope_block(a2, valid, tfw[4], tfw[5], px, [], mode="deg_25cm")
                f = found(r["candidates"], base, ccx, ccy, az, L, px)
                d = res.setdefault(f"{name}|{aid}", {"n": 0, "found": 0, "not_placeable": 0}); d["n"] += 1; d["found"] += int(f)
                if info and name not in meta: meta[name] = info
                if gmax is not None: meta.setdefault(f"{name}|max_relief_on_1m_grid_m", []).append(gmax)
                if fun is not None:
                    meta.setdefault(f"{name}|max_slope_added_deg", []).append(float(np.degrees(np.arctan(np.hypot(gx, gy))).max()))
    print(f"seed {seed} {time.time()-t0:.0f}s", flush=True)
tot = {}
for k, v in res.items():
    nm = k.split("|")[0]; t = tot.setdefault(nm, {"n": 0, "found": 0}); t["n"] += v["n"]; t["found"] += v["found"]
for k in list(meta):
    if isinstance(meta[k], list): meta[k] = [round(float(np.median(meta[k])), 3), round(float(np.max(meta[k])), 3)]
json.dump({"per_area": res, "totals": {k: dict(v, rate=round(v["found"] / max(1, v["n"]), 3)) for k, v in tot.items()}, "model_info": meta}, open(outp, "w"), indent=1)
for k, v in sorted(res.items()): print(k, v)
for k, v in tot.items(): print("TOTAL", k, v)
for k, v in meta.items(): print(k, v)
