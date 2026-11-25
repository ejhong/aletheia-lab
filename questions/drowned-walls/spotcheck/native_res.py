"""Estimate whether 2 m exported pixels are independent or duplicated (upsampled from coarser grids)."""
import sys, pathlib, json
import numpy as np
from PIL import Image
tdir = pathlib.Path(sys.argv[1])
rows = []
for tp in sorted(tdir.glob("*.tif")):
    if tp.stat().st_size < 4096:
        rows.append((tp.stem, None)); continue
    z = np.array(Image.open(tp), dtype=np.float64)
    v = np.isfinite(z) & (z > -1000) & (z < 5)
    if v.mean() < 0.03:
        rows.append((tp.stem, None)); continue
    vh = v[:, 1:] & v[:, :-1]; vv = v[1:, :] & v[:-1, :]
    eqh = (z[:, 1:] == z[:, :-1]) & vh
    eqv = (z[1:, :] == z[:-1, :]) & vv
    nearh = (np.abs(z[:, 1:] - z[:, :-1]) <= 0.011) & vh & ~eqh
    fh = eqh.sum() / vh.sum(); fv = eqv.sum() / vv.sum(); fn = nearh.sum() / vh.sum()
    # run lengths of identical values along rows (valid only)
    runs = []
    for r in range(0, z.shape[0], 8):
        row = z[r]; vr = v[r]; n = 1
        for c in range(1, z.shape[1]):
            if vr[c] and vr[c-1] and row[c] == row[c-1]: n += 1
            else:
                if vr[c-1]: runs.append(n)
                n = 1
    runs = np.array(runs)
    # pixel-weighted mean run length
    pw = (runs**2).sum() / runs.sum()
    # fraction of pixels in a pixel that has an identical 4-neighbour
    dup = np.zeros_like(v)
    dup[:, 1:] |= eqh; dup[:, :-1] |= eqh; dup[1:, :] |= eqv; dup[:-1, :] |= eqv
    fdup = dup[v].mean()
    # value quantization
    vals = np.unique(np.round(z[v], 6))
    step = np.median(np.diff(vals)) if len(vals) > 1 else 0
    rows.append((tp.stem, dict(eq_h=round(fh, 3), eq_v=round(fv, 3), near_h=round(fn, 3), pix_with_identical_nbr=round(float(fdup), 3), mean_run_px=round(float(pw), 2), median_value_step=float(step), n_unique=int(len(vals)))))
for k, d in rows: print(k, d)
json.dump(rows, open(sys.argv[2], "w"), indent=1)
