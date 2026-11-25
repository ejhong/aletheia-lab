"""Sensitivity sweep with the study's own detector: random wall position and azimuth on all eligible
background tiles, several seeds, realistic wall cross-sections."""
import math, json, sys
import numpy as np
from scipy import ndimage
from sens_common import rdw, load_tiles, background_tiles, plant, hit, A
specs, tiles = load_tiles()
bg = background_tiles(specs, tiles, "program")
SPECS = {
 "S0 study: gauss FWHM4m x0.70m x250m":        dict(kind="gauss", width=4, height=0.70, length=250),
 "S1 gauss FWHM2m x0.50m x250m":               dict(kind="gauss", width=2, height=0.50, length=250),
 "S2 box 2m x0.50m x250m (pixel-avg)":          dict(kind="box_avg", width=2, height=0.50, length=250),
 "S3 box 2m x0.30m x250m (pixel-avg)":          dict(kind="box_avg", width=2, height=0.30, length=250),
 "S4 box 1m x0.50m x250m (pixel-avg)":          dict(kind="box_avg", width=1, height=0.50, length=250),
 "S5 box 2m x0.70m x250m (pixel-avg)":          dict(kind="box_avg", width=2, height=0.70, length=250),
 "S6 box 2m x0.50m x971m (pixel-avg)":          dict(kind="box_avg", width=2, height=0.50, length=971),
 "S7 box 2m x0.50m x250m dashed 10m/5m":        dict(kind="box_avg", width=2, height=0.50, length=250, gap_on=10, gap_off=5),
 "S8 study gauss 4m x0.70m but 100m long":      dict(kind="gauss", width=4, height=0.70, length=100),
 "S9 study gauss 4m x0.70m x250m dashed 10/5":  dict(kind="gauss", width=4, height=0.70, length=250, gap_on=10, gap_off=5),
 "S10 study gauss 4m x0.50m x250m":             dict(kind="gauss", width=4, height=0.50, length=250),
 "S11 study gauss 4m x0.40m x250m":             dict(kind="gauss", width=4, height=0.40, length=250),
}
which = sys.argv[1:] or list(SPECS)
results = {}
for name in SPECS:
    if not any(name.startswith(w + " ") for w in which) and which != list(SPECS): continue
    p = SPECS[name]; per_seed = []
    for seed in (1, 2, 3):
        rng = np.random.default_rng(seed)
        n = hs = ha = 0; by_region = {}
        for sp, z, v in bg:
            interior = ndimage.binary_erosion(v, iterations=70)
            ys, xs = np.nonzero(interior)
            for k in range(4):
                j = rng.integers(len(ys)); cy, cx = int(ys[j]), int(xs[j])
                while True:
                    az = float(rng.uniform(0, 180))
                    if min(az % 90, 90 - az % 90) > 5: break
                kw = {kk: p[kk] for kk in ("gap_on", "gap_off") if kk in p}
                zw = plant(z, v, cx, cy, az, p["length"], p["width"], p["height"], p["kind"], **kw)
                d = rdw.detect_structures(zw, sp["bbox"], enc_features=[], is_control=False)
                a = hit(d, cx, cy, az, p["length"], "any"); s = hit(d, cx, cy, az, p["length"], "study")
                n += 1; hs += s; ha += a
                r = sp["region"].split(" ")[0] + " " + sp["region"].split(" ")[1]
                by_region.setdefault(r, [0, 0]); by_region[r][0] += a; by_region[r][1] += 1
        per_seed.append(dict(seed=seed, n=n, study_crit=hs, any_crit=ha, by_region_any=by_region))
    results[name] = per_seed
    print(name, [(r["seed"], f'{r["study_crit"]}/{r["n"]}', f'{r["any_crit"]}/{r["n"]}') for r in per_seed], per_seed[0]["by_region_any"], flush=True)
out = A / "out/sensitivity_sweep.json"
old = json.loads(out.read_text()) if out.exists() else {}
old.update(results); out.write_text(json.dumps(old, indent=1))
