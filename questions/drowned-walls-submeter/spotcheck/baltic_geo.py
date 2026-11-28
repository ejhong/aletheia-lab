"""Extents of the Baltic grids, distance to the Blinkerwall core site, nearest munition pile, image modes.
usage: python -I baltic_geo.py <analysis_dir> <baltic_dir> <out.json>"""
import io, json, math, pathlib, sys, zipfile
import numpy as np
from PIL import Image
sys.path.insert(0, sys.argv[1]); import run_submeter_scan as m
bd = pathlib.Path(sys.argv[2]); m.BALTIC_DIR = bd
mun = m.load_baltic_munitions()
# Core L0923-07 (Geersen et al. 2024, Methods) lies in the basin beside the Blinkerwall
CORE = (54.1609, 11.4728)
out = {"munition_bbox": [min(p[0] for p in mun), max(p[0] for p in mun), min(p[1] for p in mun), max(p[1] for p in mun)], "n_munitions": len(mun), "areas": {}}
def info(name, tfw, shape):
    e0, n0, px = tfw[4], tfw[5], abs(tfw[0]); h, w = shape
    corners = [m.utm33n_to_latlon(e0 + c * px, n0 - r * px) for r, c in ((0, 0), (0, w), (h, 0), (h, w))]
    lat_c, lon_c = m.utm33n_to_latlon(e0 + w * px / 2, n0 - h * px / 2)
    dmin_core = min(m.haversine_m(lo, la, CORE[1], CORE[0]) for la, lo in corners + [(lat_c, lon_c)])
    dmun = min(m.haversine_m(lon_c, lat_c, p[1], p[0]) for p in mun)
    out["areas"][name] = dict(px_m=px, shape=[h, w], extent_m=[round(w * px), round(h * px)], center=[round(lat_c, 5), round(lon_c, 5)],
        lat_range=[round(min(c[0] for c in corners), 5), round(max(c[0] for c in corners), 5)], lon_range=[round(min(c[1] for c in corners), 5), round(max(c[1] for c in corners), 5)],
        km_to_blinkerwall_core_nearest_corner=round(dmin_core / 1000, 2), km_center_to_nearest_munition_pile=round(dmun / 1000, 2))
with zipfile.ZipFile(bd / "Test_Areas.zip") as zf:
    for i in range(1, 6):
        tfw = [float(x) for x in zf.read(f"Test{i}.tfw").decode().split()]
        im = Image.open(io.BytesIO(zf.read(f"Test{i}.tif")))
        a = np.array(im, dtype=np.float32)
        info(f"Test{i}", tfw, a.shape)
        out["areas"][f"Test{i}"].update(mode=im.mode, slope_p50=float(np.nanpercentile(a, 50)), slope_p99=float(np.nanpercentile(a, 99)), n_nan=int(np.isnan(a).sum()), n_neg=int((a < 0).sum()), aux=(zf.read(f"Test{i}.tif.aux.xml").decode()[:300] if f"Test{i}.tif.aux.xml" in zf.namelist() else None))
with zipfile.ZipFile(bd / "Time_Series.zip") as zf:
    for y in (2024, 2025):
        tfw = [float(x) for x in zf.read(f"Time_Series/slope_{y}.tfw").decode().split()]
        im = Image.open(io.BytesIO(zf.read(f"Time_Series/slope_{y}.tif")))
        info(f"slope_{y}", tfw, (im.size[1], im.size[0]))
        pal = im.getpalette() if im.mode in ("P", "PA") else None
        out["areas"][f"slope_{y}"].update(mode=im.mode, palette_is_gray_identity=(None if pal is None else all(pal[3*k] == pal[3*k+1] == pal[3*k+2] == k for k in range(256))), tags={str(k): str(v)[:200] for k, v in im.tag_v2.items()} if hasattr(im, "tag_v2") else None)
json.dump(out, open(sys.argv[3], "w"), indent=1); print(json.dumps(out, indent=1))
