"""List OpenStreetMap seamark objects near a point from a saved Overpass JSON. usage: osm_near.py <json> <lat> <lon> [n]"""
import json, math, sys
d = json.load(open(sys.argv[1])); lat0, lon0 = float(sys.argv[2]), float(sys.argv[3]); n = int(sys.argv[4]) if len(sys.argv) > 4 else 25
rows = []
for e in d["elements"]:
    la = e.get("lat") or e.get("center", {}).get("lat"); lo = e.get("lon") or e.get("center", {}).get("lon")
    if la is None: continue
    dist = math.hypot((la - lat0) * 111320, (lo - lon0) * 111320 * math.cos(math.radians(lat0)))
    rows.append((round(dist), e["type"], e["id"], round(la, 5), round(lo, 5), {k: v for k, v in e.get("tags", {}).items() if k.startswith("seamark") or k == "name"}))
for r in sorted(rows)[:n]: print(r)
print(len(rows), "objects")
