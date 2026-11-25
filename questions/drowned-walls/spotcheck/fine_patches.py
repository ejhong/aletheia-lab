"""Download small 0.5 m/px patches inside each study tile and estimate the native source cell size
from run lengths of identical values (nearest-neighbour export of a coarser grid repeats values)."""
import sys, json, math, time, io, urllib.parse, urllib.request, pathlib
import numpy as np
from PIL import Image
A = pathlib.Path(sys.argv[1])
summ = json.load(open(A / "out/committed_summary.json"))
tiles = [(r["id"], r["bbox"]) for r in summ["calibration"]["real_breakwater_controls"]] + [(t["id"], t["bbox"]) for t in summ["tiles"]]
out = {}
UA = {"User-Agent": "Mozilla/5.0 (generic research client)"}
def runs_mean(z, v):
    rl = []
    for arr, vm in ((z, v), (z.T, v.T)):
        for r in range(arr.shape[0]):
            row, vr = arr[r], vm[r]; n = 1; start_ok = False
            for c in range(1, arr.shape[1]):
                if vr[c] and vr[c-1] and row[c] == row[c-1]: n += 1
                else:
                    if vr[c-1] and start_ok: rl.append(n)
                    start_ok = vr[c]; n = 1
    return float(np.mean(rl)) if rl else None, len(rl)
for tid, (lon0, lat0, lon1, lat1) in tiles:
    res = []
    for fx, fy in ((0.5, 0.5), (0.25, 0.75), (0.75, 0.25)):
        clon = lon0 + fx * (lon1 - lon0); clat = lat0 + fy * (lat1 - lat0)
        dlat = 256 * 0.5 / 111320.0; dlon = dlat / math.cos(math.radians(clat))
        bb = (clon - dlon/2, clat - dlat/2, clon + dlon/2, clat + dlat/2)
        fp = A / "data/fine" / f"{tid}_{fx}_{fy}.tif"
        if not fp.exists():
            q = urllib.parse.urlencode({"bbox": ",".join(f"{x:.7f}" for x in bb), "bboxSR": "4326", "imageSR": "4326", "size": "256,256",
                 "format": "tiff", "pixelType": "F32", "noData": "-999999", "interpolation": "RSP_NearestNeighbor", "f": "image"})
            with urllib.request.urlopen(urllib.request.Request("https://gis.ngdc.noaa.gov/arcgis/rest/services/bag_bathymetry/ImageServer/exportImage?" + q, headers=UA), timeout=60) as r:
                fp.write_bytes(r.read())
            time.sleep(0.4)
        if fp.stat().st_size < 4096:
            res.append(None); continue
        z = np.array(Image.open(fp), dtype=np.float64)
        v = np.isfinite(z) & (z > -1000) & (z < 5)
        if v.mean() < 0.2: res.append(None); continue
        m, n = runs_mean(z, v)
        res.append({"valid": round(float(v.mean()), 2), "mean_run_px_at_0.5m": round(m, 2), "est_native_cell_m": round(0.5 * m, 2)})
    out[tid] = res
    print(tid, [r and r["est_native_cell_m"] for r in res], flush=True)
json.dump(out, open(A / "out/native_cell_estimates.json", "w"), indent=1)
