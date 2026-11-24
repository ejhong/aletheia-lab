"""For every unmasked candidate, check ENC features in all four scale bands (incl. dumping grounds and
fish havens), using polygon containment as well as distance to vertices/lines."""
import json, math, time, sys, urllib.parse, urllib.request, pathlib
A = pathlib.Path(sys.argv[1])
s = json.load(open(A / "out/rerun_summary.json"))
LAYERS = {"enc_approach": {70: "Dumping_Ground_pt", 196: "Dumping_Ground_area", 161: "Obstruction_area", 163: "Wreck_area", 36: "Obstruction_pt", 39: "Wreck_pt", 35: "Fishing_Facility_pt", 160: "Fishing_Facility_area", 233: "Dredged_Area", 118: "Cable_ln", 89: "ShorelineConstr_ln"},
          "enc_coastal": {54: "Dumping_Ground_pt", 136: "Dumping_Ground_area", 118: "Obstruction_area", 120: "Wreck_area", 30: "Obstruction_pt", 33: "Wreck_pt", 71: "ShorelineConstr_ln"},
          "enc_harbour": {66: "Dumping_Ground_pt", 191: "Dumping_Ground_area", 156: "Obstruction_area", 158: "Wreck_area", 33: "Obstruction_pt", 36: "Wreck_pt", 85: "ShorelineConstr_ln"},
          "enc_general": {45: "Dumping_Ground_pt", 98: "Dumping_Ground_area", 83: "Obstruction_area", 84: "Wreck_area", 26: "Obstruction_pt", 29: "Wreck_pt"}}
def pip(x, y, ring):
    ins = False
    for i in range(len(ring)):
        x1, y1 = ring[i]; x2, y2 = ring[(i + 1) % len(ring)]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1): ins = not ins
    return ins
def seg_dist_m(px, py, a, b):
    k = math.cos(math.radians(py)) * 111320; m = 110900
    ax, ay = (a[0] - px) * k, (a[1] - py) * m; bx, by = (b[0] - px) * k, (b[1] - py) * m
    dx, dy = bx - ax, by - ay; L = dx * dx + dy * dy
    t = 0 if L == 0 else max(0, min(1, -(ax * dx + ay * dy) / L))
    return math.hypot(ax + t * dx, ay + t * dy)
tiles = {t["id"]: t for t in s["tiles"]}
targets = sorted({t["id"] for t in s["tiles"] if t["n_unmasked"] > 0})
report = {}
for tid in targets:
    lon0, lat0, lon1, lat1 = tiles[tid]["bbox"]; pad = 0.003
    feats = []
    for band, lyrs in LAYERS.items():
        for lid, lname in lyrs.items():
            fp = A / "data/enc_multi" / f"{tid}_{band}_{lid}.json"
            if not fp.exists():
                q = urllib.parse.urlencode({"geometry": f"{lon0-pad},{lat0-pad},{lon1+pad},{lat1+pad}", "geometryType": "esriGeometryEnvelope", "inSR": "4326", "outSR": "4326",
                    "spatialRel": "esriSpatialRelIntersects", "outFields": "*", "returnGeometry": "true", "f": "json"})
                url = f"https://encdirect.noaa.gov/arcgis/rest/services/encdirect/{band}/MapServer/{lid}/query?" + q
                with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (generic research client)"}), timeout=60) as r:
                    fp.write_bytes(r.read())
                time.sleep(0.3)
            d = json.loads(fp.read_text())
            if "error" in d: print("ERROR", tid, band, lid, d["error"])
            for f in d.get("features", []):
                feats.append((band, lname, f["attributes"], f["geometry"]))
    rows = []
    for c in tiles[tid]["candidates"]:
        if not c["unmasked"]: continue
        best = (1e9, None); inside = []
        for band, lname, attr, g in feats:
            if "x" in g:
                dm = seg_dist_m(c["lon"], c["lat"], (g["x"], g["y"]), (g["x"], g["y"]))
            else:
                dm = 1e9
                for key in ("paths", "rings"):
                    for pa in g.get(key, []):
                        for i in range(len(pa) - 1):
                            dm = min(dm, seg_dist_m(c["lon"], c["lat"], pa[i], pa[i + 1]))
                for ring in g.get("rings", []):
                    if pip(c["lon"], c["lat"], ring): inside.append(f"{band}:{lname}:{attr.get('CATOBS') or attr.get('CATDPG') or attr.get('OBJNAM') or ''}"); dm = 0
            if dm < best[0]: best = (dm, f"{band}:{lname}:{attr.get('CATOBS') or attr.get('CATDPG') or attr.get('OBJNAM') or ''}")
        rows.append(dict(lat=c["lat"], lon=c["lon"], L=c["length_m"], nearest_m=round(best[0], 1), nearest=best[1], inside=sorted(set(inside))))
    report[tid] = dict(n_feats=len(feats), layers_with_feats=sorted({f"{b}:{l}" for b, l, _, _ in feats}), candidates=rows)
    print(tid, "features:", len(feats), report[tid]["layers_with_feats"])
    for r in rows: print("    ", r)
json.dump(report, open(A / "out/enc_multiband_check.json", "w"), indent=1)
