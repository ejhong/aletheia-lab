"""Plant walls of published dimensions in the real Lake Huron tiles and run the study's own detector.

usage: python -I sens_huron.py <analysis_dir> <scan_summary.json> <huron_tiles_dir> <out.json> [seeds=2] [trials=3] [footprint_sigma_m=0]
footprint_sigma_m > 0 smooths each rendered wall with a Gaussian of that sigma (a crude sonar-footprint blur).
Tiles: every non-control tile with at least 50% valid data. Positions and azimuths random (avoiding +-5 deg of
the cardinal axes). A wall counts as found when an unmasked linear candidate that was not there before planting
has its centroid within 5 m of the planted axis (and within its length) and an azimuth within 15 deg.
The study's own rule (any unmasked candidate within 30 m of the centre) is also reported.
"""
import json, math, pathlib, sys, time
import numpy as np
from PIL import Image
from scipy import ndimage
sys.path.insert(0, sys.argv[1]); sys.path.insert(0, str(pathlib.Path(__file__).parent))
import run_submeter_scan as m
import walls

summ = json.load(open(sys.argv[2])); tdir = pathlib.Path(sys.argv[3]); outp = sys.argv[4]
seeds = int(sys.argv[5]) if len(sys.argv) > 5 else 2; trials = int(sys.argv[6]) if len(sys.argv) > 6 else 3
fp_sigma = float(sys.argv[7]) if len(sys.argv) > 7 else 0.0
tiles = [t for t in summ["arm1_huron"]["tiles"] if t["valid_pct"] >= 50.0]

def variants(px, rng):
    L = 150.0
    study = (60.0, 2.5, 0.50) if px <= 1.05 else (120.0, 4.0, 0.55)
    return {
        "study_wall_random_place": (study[0], walls.gaussian_ridge(*study), {}),
        "ridge_2m_x_0.3m": (L, walls.gaussian_ridge(L, 2.0, 0.3), {}),
        "ridge_1m_x_0.5m": (L, walls.gaussian_ridge(L, 1.0, 0.5), {}),
        "boulder_line_d0.4-0.8_h0.7d_every1.5m": (L, *walls.boulder_line(L, rng, 0.4, 0.8, 0.7, 1.5)),
        "boulder_line_d1.0-1.4_h0.9m_every2m": (L, *walls.boulder_line(L, rng, 1.0, 1.4, 0.75, 2.0)),
        "blinkerwall_volume_matched": (L, *walls.blinkerwall(L, rng)),
        "blinkerwall_volume_matched_single_file": (L, *walls.blinkerwall_single_file(L, rng)),
        "blinkerwall_upper_bound": (L, *walls.blinkerwall_upper(L, rng)),
    }

def found(cands, base, cx, cy, az, L, px):
    rad = math.radians(az); vx, vy = math.sin(rad), -math.cos(rad)
    ok_line = ok_study = False
    for c in cands:
        if not c["unmasked"]:
            continue
        x, y = c["px_centroid"]
        if any(math.hypot(x - b[0], y - b[1]) * px <= 5.0 for b in base):
            continue
        dx, dy = (x - cx) * px, (y - cy) * px
        al = dx * vx + dy * vy; ac = -dx * vy + dy * vx
        daz = abs(c["azimuth_deg"] - az) % 180; daz = min(daz, 180 - daz)
        if abs(ac) <= 5.0 and abs(al) <= L / 2 + 5 and daz <= 15:
            ok_line = True
        if math.hypot(dx, dy) <= 30.0:
            ok_study = True
    return ok_line, ok_study

res = {}; meta = {}; t0 = time.time()
for seed in range(seeds):
    rng = np.random.default_rng(1000 + seed)
    for t in tiles:
        z = np.array(Image.open(tdir / f"{t['id']}.tif"), dtype=np.float32); px = t["px_m"]
        raw = np.isfinite(z) & (z >= -120) & (z <= -1.5)
        base_r = m.detect_huron_structures(z, tuple(t["bbox"]), [], px_m=px)
        base = [c["px_centroid"] for c in base_r["candidates"] if c["unmasked"]]
        inner = ndimage.binary_erosion(raw, iterations=8)
        for k in range(trials):
            vs = variants(px, rng)
            for name, (L, fun, info) in vs.items():
                half = int(math.ceil((L / 2 + 6) / px))
                placed = False
                for _ in range(400):
                    az = rng.uniform(0, 180)
                    if min(az % 90, 90 - az % 90) < 5: continue
                    cy, cx = rng.integers(half, z.shape[0] - half), rng.integers(half, z.shape[1] - half)
                    rad = math.radians(az); vx, vy = math.sin(rad), -math.cos(rad)
                    pts = [(cy - 0.5 + s * vy * L / 2 / px, cx - 0.5 + s * vx * L / 2 / px) for s in np.linspace(-1, 1, 25)]
                    if all(inner[int(round(r)), int(round(c))] for r, c in pts if 0 <= r < z.shape[0] and 0 <= c < z.shape[1]) and \
                       all(0 <= r < z.shape[0] and 0 <= c < z.shape[1] for r, c in pts):
                        placed = True; break
                if not placed:
                    continue
                wall = walls.render(fun, px, half, az)
                if fp_sigma > 0:
                    wall = ndimage.gaussian_filter(wall, fp_sigma / px)
                zz = z.copy()
                sl = (slice(cy - half, cy + half), slice(cx - half, cx + half))
                zz[sl] = np.where(raw[sl], zz[sl] + wall.astype(np.float32), zz[sl])
                r = m.detect_huron_structures(zz, tuple(t["bbox"]), [], px_m=px)
                fl, fs = found(r["candidates"], base, cx - 0.5, cy - 0.5, az, L, px)
                key = f"{name}|{px}"
                d = res.setdefault(key, {"n": 0, "found_line": 0, "found_study_rule": 0, "per_seed": {}})
                d["n"] += 1; d["found_line"] += fl; d["found_study_rule"] += fs
                ps = d["per_seed"].setdefault(str(seed), [0, 0]); ps[0] += 1; ps[1] += fl
                if info and name not in meta: meta[name] = info
                meta.setdefault(f"{name}|{px}|max_gridded_relief_m", []).append(float(wall.max()))
    print(f"seed {seed} done {time.time()-t0:.0f}s", flush=True)
summary = {k: dict(v, rate_line=round(v["found_line"] / v["n"], 3), rate_study_rule=round(v["found_study_rule"] / v["n"], 3)) for k, v in sorted(res.items())}
for k in list(meta):
    if k.endswith("max_gridded_relief_m"):
        meta[k] = [round(float(np.median(meta[k])), 3), round(float(np.max(meta[k])), 3)]
json.dump({"footprint_sigma_m": fp_sigma, "tiles_used": len(tiles), "seeds": seeds, "trials_per_tile": trials, "results": summary, "model_info": meta}, open(outp, "w"), indent=1)
for k, v in summary.items(): print(k, v["n"], v["found_line"], v["rate_line"], v["rate_study_rule"])
for k, v in meta.items(): print(k, v)
