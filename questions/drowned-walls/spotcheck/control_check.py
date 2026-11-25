"""Point Judith control: flank sampling of the recovered ridge, and rerun with the search-tile depth mask."""
import math
import numpy as np
from sens_common import rdw, load_tiles
specs, tiles = load_tiles()
sp, z = tiles["CTRL_PTJUDITH"]
for is_ctrl in (True, False):
    d = rdw.detect_structures(z, sp["bbox"], enc_features=[], is_control=is_ctrl)
    print("is_control", is_ctrl, "valid", d["valid_pct"], [(c["length_m"], c["max_bpi_m"], c["linearity"], c["flank_step_m"], c["flags"]) for c in d["candidates"]])
d = rdw.detect_structures(z, sp["bbox"], enc_features=[], is_control=True)
c = d["candidates"][0]
valid = np.isfinite(z) & (z >= -120) & (z <= 1.5)
x1, y1, x2, y2 = c["px_endpoints"]; cx, cy = c["px_centroid"]
L = math.hypot(x2 - x1, y2 - y1); vx, vy = (x2 - x1) / L, (y2 - y1) / L; nx, ny = -vy, vx
nl = nr = 0; zl = []; zr = []
for t in np.linspace(-L / 2 * 0.8, L / 2 * 0.8, 15):
    bx, by = cx + t * vx, cy + t * vy
    for off in (5, 7, 9):
        for sgn in (1, -1):
            sx, sy = int(round(bx + sgn * off * nx)), int(round(by + sgn * off * ny))
            ok = 0 <= sx < 512 and 0 <= sy < 512 and valid[sy, sx]
            if ok: (zl if sgn > 0 else zr).append(float(z[sy, sx]))
print("flank samples side A:", len(zl), "side B:", len(zr), "of 45 each; medians", np.median(zl) if zl else None, np.median(zr) if zr else None)
# profile across the ridge at its centre
prof = []
for off in range(-15, 16):
    sx, sy = int(round(cx + off * nx)), int(round(cy + off * ny))
    prof.append((off * 2, round(float(z[sy, sx]), 2) if valid[sy, sx] else None))
print("cross profile (m offset, depth):", prof)
