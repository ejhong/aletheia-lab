"""For each Huron tile, list the BAG ImageServer source rasters under it (name, cell size, survey) and estimate
whether exported pixels are independent (fraction of pixels equal to a 4-neighbour; run length of equal values).
usage: python -I huron_catalog.py <scan_summary.json> <huron_tiles_dir> <out.json>"""
import json, sys, time, pathlib, urllib.parse, urllib.request
import numpy as np
from PIL import Image
summ = json.load(open(sys.argv[1])); tdir = pathlib.Path(sys.argv[2])
tiles = [(c["id"], c["bbox"], c["px_m"], c["survey"]) for c in summ["calibration"]["arm1_controls"]] + [(t["id"], t["bbox"], t["px_m"], t["survey"]) for t in summ["arm1_huron"]["tiles"]]
UA = {"User-Agent": "bathymetry-audit/1.0"}
out = {}
for tid, bbox, px, survey in tiles:
    q = urllib.parse.urlencode({"geometry": ",".join(map(str, bbox)), "geometryType": "esriGeometryEnvelope", "inSR": "4326",
        "spatialRel": "esriSpatialRelIntersects", "outFields": "*", "returnGeometry": "false", "f": "json"})
    try:
        with urllib.request.urlopen(urllib.request.Request("https://gis.ngdc.noaa.gov/arcgis/rest/services/bag_bathymetry/ImageServer/query?" + q, headers=UA), timeout=60) as r:
            feats = [f["attributes"] for f in json.loads(r.read().decode()).get("features", [])]
    except Exception as e:
        feats = [{"error": str(e)}]
    rec = {"px_m_claimed": px, "survey_claimed": survey,
           "sources": [{k: a.get(k) for k in ("Name", "LowPS", "HighPS", "Category", "MinPS", "MaxPS") if k in a} for a in feats]}
    tp = tdir / f"{tid}.tif"
    if tp.exists() and tp.stat().st_size > 4096:
        z = np.array(Image.open(tp), dtype=np.float64); v = np.isfinite(z) & (z > -1000) & (z < 5)
        if v.mean() > 0.03:
            eqh = (z[:, 1:] == z[:, :-1]) & v[:, 1:] & v[:, :-1]; eqv = (z[1:] == z[:-1]) & v[1:] & v[:-1]
            dup = np.zeros_like(v); dup[:, 1:] |= eqh; dup[:, :-1] |= eqh; dup[1:] |= eqv; dup[:-1] |= eqv
            rec["frac_pixels_with_identical_neighbour"] = round(float(dup[v].mean()), 3)
            rec["frac_eq_h"] = round(float(eqh.sum() / (v[:, 1:] & v[:, :-1]).sum()), 3)
            rec["frac_eq_v"] = round(float(eqv.sum() / (v[1:] & v[:-1]).sum()), 3)
    out[tid] = rec
    time.sleep(0.3)
json.dump(out, open(sys.argv[3], "w"), indent=1)
for tid, r in out.items():
    names = sorted({(s.get("Name"), s.get("LowPS")) for s in r["sources"]}, key=lambda x: str(x))
    print(tid, r["px_m_claimed"], r.get("frac_pixels_with_identical_neighbour"), r.get("frac_eq_h"), r.get("frac_eq_v"), names[:6])
