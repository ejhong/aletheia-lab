"""Extra checks: (a) the study's exact 10-trial gate under 20 other seeds; (b) protocol background rule;
(c) small-gap dashed walls and other heights."""
import json
import numpy as np
from sens_common import rdw, load_tiles, background_tiles, plant, hit, A
from scipy import ndimage
specs, tiles = load_tiles()
out = {}
for rule in ("program", "protocol"):
    bg = background_tiles(specs, tiles, rule)[:10]
    counts = []
    for seed in [20261124] + list(range(1, 21)):
        rng = np.random.default_rng(seed); rec = 0
        for sp, z, v in bg:
            az = float(rng.choice([25.0, 38.0, 52.0, 67.0, 118.0, 134.0, 149.0]))
            zw, (cx, cy) = rdw.inject_synthetic_wall(z, v, 250.0, 4.0, 0.70, az)
            d = rdw.detect_structures(zw, sp["bbox"], enc_features=[], is_control=False)
            rec += hit(d, cx, cy, az, 250.0, "study")
        counts.append(rec)
    out[f"gate_{rule}"] = counts
    print(rule, "first-10 tiles:", [b[0]["id"] for b in bg]); print("  recovered/10 for seed 20261124 then seeds 1..20:", counts)
bg = background_tiles(specs, tiles, "program")
EXTRA = {"E1 gauss 4m x0.70 x250 dashed 20m/2m": dict(kind="gauss", width=4, height=0.7, length=250, gap_on=20, gap_off=2),
         "E2 box 2m x0.50 x250 dashed 20m/2m": dict(kind="box_avg", width=2, height=0.5, length=250, gap_on=20, gap_off=2),
         "E3 box 2m x0.60 x250": dict(kind="box_avg", width=2, height=0.6, length=250),
         "E4 box 3m x0.50 x250": dict(kind="box_avg", width=3, height=0.5, length=250),
         "E5 box 2m x1.00 x250": dict(kind="box_avg", width=2, height=1.0, length=250)}
for name, p in EXTRA.items():
    rng = np.random.default_rng(7); n = ha = hs = 0
    for sp, z, v in bg:
        interior = ndimage.binary_erosion(v, iterations=70); ys, xs = np.nonzero(interior)
        for k in range(4):
            j = rng.integers(len(ys)); cy, cx = int(ys[j]), int(xs[j])
            while True:
                az = float(rng.uniform(0, 180))
                if min(az % 90, 90 - az % 90) > 5: break
            kw = {kk: p[kk] for kk in ("gap_on", "gap_off") if kk in p}
            zw = plant(z, v, cx, cy, az, p["length"], p["width"], p["height"], p["kind"], **kw)
            d = rdw.detect_structures(zw, sp["bbox"], enc_features=[], is_control=False)
            n += 1; ha += hit(d, cx, cy, az, p["length"], "any"); hs += hit(d, cx, cy, az, p["length"], "study")
    out[name] = dict(n=n, study=hs, any=ha); print(name, f"study {hs}/{n}  any {ha}/{n}")
json.dump(out, open(A / "out/sensitivity_extra.json", "w"), indent=1)
