"""(1) Wreck controls: where the BPI peak is relative to the chart point, and whether any candidate is linked to a
charted wreck (CHARTED_MODERN), the way the plan words the gate. (2) Step seams: for the study's own 12 seam
trials, whether the seam was rejected by SEAM_STEP or simply never produced a candidate.
usage: python -I controls_seams.py <analysis_dir> <data_dir> <scan_summary.json> <out.json>"""
import json, math, pathlib, sys
import numpy as np
from PIL import Image
sys.path.insert(0, sys.argv[1]); import run_submeter_scan as m
data = pathlib.Path(sys.argv[2]); summ = json.load(open(sys.argv[3])); out = {"controls": {}, "seams": []}
enc = json.load(open(data / "huron_enc_general.json")); enc_pts = [(x, y, f["layer"]) for f in enc for x, y in f["pts"]]
specs = {s["id"]: s for s in m.build_huron_specs()}
for cid in ("CTRL_HURON_WRECK_H13652", "CTRL_HURON_WRECK_F00862", "CTRL_HURON_WRECK_W00499"):
    s = specs[cid]; z = np.array(Image.open(data / "huron_tiles" / f"{cid}.tif"), dtype=np.float32)
    r = m.detect_huron_structures(z, s["bbox"], enc_pts, px_m=s["px_m"], is_control=True)
    bpi = r["bpi"]; iy, ix = np.unravel_index(np.nanargmax(bpi), bpi.shape); h, w = bpi.shape
    lon0, lat0, lon1, lat1 = s["bbox"]
    plon = lon0 + ix / (w - 1) * (lon1 - lon0); plat = lat1 - iy / (h - 1) * (lat1 - lat0)
    clon, clat = (lon0 + lon1) / 2, (lat0 + lat1) / 2
    wrecks = [(x, y) for x, y, l in enc_pts if l == "Wreck_pt"]
    near = min(wrecks, key=lambda p: m.haversine_m(clon, clat, p[0], p[1]))
    out["controls"][cid] = {
        "peak_bpi_m": round(float(bpi[iy, ix]), 2), "peak_lat": round(plat, 6), "peak_lon": round(plon, 6),
        "peak_dist_from_chart_wreck_m": round(m.haversine_m(plon, plat, near[0], near[1]), 1),
        "peak_offset_px_from_centre": [int(ix - w // 2), int(iy - h // 2)],
        "inside_70m_box": bool(abs(ix - w // 2) * s["px_m"] <= 70 and abs(iy - h // 2) * s["px_m"] <= 70),
        "candidates": [{k: c[k] for k in ("length_m", "width_m", "max_bpi_m", "flags", "nearest_enc_m", "unmasked")} for c in r["candidates"]],
        "rings": [{k: c[k] for k in ("diam_m", "max_bpi_m", "flags")} for c in r["rings"]],
        "any_candidate_flagged_charted_wreck": any(any("Wreck" in f for f in c["flags"]) for c in r["candidates"] + r["rings"]),
    }
# seams, replicating the study's host choice and azimuths
tiles = summ["arm1_huron"]["tiles"]; hosts = []
for pt in (0.5, 1.0, 2.0):
    ct = sorted([t for t in tiles if abs(t["px_m"] - pt) < 0.05 and t["valid_pct"] >= 85.0], key=lambda t: (t["n_unmasked"], -t["valid_pct"]))
    hosts += ct[:4]
azs = [27.0, 53.0, 118.0, 146.0] * 3
for i, t in enumerate(hosts[:12]):
    s = specs[t["id"]]; z = np.array(Image.open(data / "huron_tiles" / f"{t['id']}.tif"), dtype=np.float32); px = s["px_m"]
    v = np.isfinite(z) & (z >= -120) & (z <= -1.5)
    zs = m.inject_huron_step_seam(z, v, 0.5, azs[i], px)
    r = m.detect_huron_structures(zs, s["bbox"], [], px_m=px)
    near = [c for c in r["candidates"] if math.hypot(c["px_centroid"][0] - 256, c["px_centroid"][1] - 256) * px <= 80
            and min(abs(c["azimuth_deg"] - azs[i]), 180 - abs(c["azimuth_deg"] - azs[i])) <= 12]
    out["seams"].append({"tile": t["id"], "px_m": px, "az": azs[i], "n_seam_candidates": len(near),
                         "flags": [c["flags"] for c in near],
                         "outcome": ("not_detected" if not near else ("rejected_by_SEAM_STEP" if all("SEAM_STEP" in c["flags"] for c in near) and not any(c["unmasked"] for c in near)
                                     else ("rejected_by_other_flag" if not any(c["unmasked"] for c in near) else "passed_as_unmasked")))})
json.dump(out, open(sys.argv[4], "w"), indent=1)
for k, v in out["controls"].items(): print(k, {kk: vv for kk, vv in v.items() if kk not in ("candidates",)}); [print("   ", c) for c in v["candidates"][:14]]
from collections import Counter; print(Counter(s["outcome"] for s in out["seams"])); [print(s) for s in out["seams"]]
