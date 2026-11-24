"""(1) Re-create the study's 10-trial gate exactly; (2) check what the protocol's background-depth rule would pick."""
import math, time
import numpy as np
from sens_common import rdw, load_tiles, background_tiles, plant, hit
specs, tiles = load_tiles()
for rule in ("program", "protocol"):
    bg = background_tiles(specs, tiles, rule)
    print(rule, "eligible background tiles:", len(bg), [b[0]["id"] for b in bg])
bg = background_tiles(specs, tiles, "program")
rng = np.random.default_rng(20261124)
t0 = time.time(); rec = 0
for i in range(10):
    sp, z, v = bg[i]
    az = float(rng.choice([25.0, 38.0, 52.0, 67.0, 118.0, 134.0, 149.0]))
    zw, (cx, cy) = rdw.inject_synthetic_wall(z, v, 250.0, 4.0, 0.70, az)
    d = rdw.detect_structures(zw, sp["bbox"], enc_features=[], is_control=False)
    hh = hit(d, cx, cy, az, 250.0, "study"); rec += hh
    print(sp["id"], az, (cx, cy), hh)
print("recovered", rec, "/10  time", round(time.time() - t0, 1), "s")
