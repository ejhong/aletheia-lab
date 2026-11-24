"""Coverage of Neotoma pollen datasets reaching >=12 ka / >=18 ka, by region, latitude band, database, site."""
import json, sys, pathlib, collections
sys.path.insert(0, sys.argv[1]); import run_ice_age_farming as iaf
C = pathlib.Path(sys.argv[2])
rows = {}
units = collections.Counter()
for p in sorted(C.glob("ds_all_pollen_off*.json")):
    for item in json.loads(p.read_text())["data"]:
        s = item["site"]; lon, lat = iaf.parse_lon_lat(s.get("geography"))
        for ds in s.get("datasets") or []:
            if ds.get("datasettype") != "pollen": continue
            ao = None
            for ar in ds.get("agerange") or []:
                units[ar.get("units")] += 1
                if ar.get("ageold") is None: continue
                v, _ = iaf.normalize_age_cal_bp(ar["ageold"], ar.get("units") or "")
                ao = v if ao is None else max(ao, v)
            rows[ds["datasetid"]] = dict(site=s["siteid"], name=s["sitename"], lat=lat, lon=lon, db=ds.get("database"), ao=ao)
print("datasets", len(rows), "units", dict(units))
print("no agerange:", sum(1 for r in rows.values() if r["ao"] is None))
def region(r):
    la, lo = r["lat"], r["lon"]
    if la is None: return "unknown"
    if lo < -30: return "N America" if la >= 15 else ("C America/Caribbean" if la >= 7 else "S America")
    if lo < 60 and la >= 35 and lo <= 45 and la <= 72: return "Europe"
    if 34 <= lo <= 60 and 12 <= la < 42: return "SW Asia/Near East"
    if lo < 55 and la < 35: return "Africa"
    if lo >= 110 and la < -10 or lo > 150: return "Australasia/Pacific"
    if 60 <= lo and la < 35 and la >= -11: return "S/SE Asia"
    return "N/C/E Asia"
for thr in (12000, 18000):
    sel = [r for r in rows.values() if r["ao"] is not None and r["ao"] >= thr]
    print(f"\n>= {thr}: datasets {len(sel)}, unique sites {len({r['site'] for r in sel})}")
    print(" by region:", collections.Counter(region(r) for r in sel).most_common())
    bands = collections.Counter()
    for r in sel:
        la = r["lat"]
        b = "unk" if la is None else ("tropics |lat|<23.5" if abs(la) < 23.5 else ("subtrop 23.5-35" if abs(la) < 35 else ("35-50" if abs(la) < 50 else ">=50")))
        bands[b] += 1
    print(" by |lat| band:", bands.most_common())
    print(" by database:", collections.Counter(r["db"] for r in sel).most_common(12))
    ne = [r for r in sel if r["lat"] and 29 <= r["lat"] <= 42 and 34 <= r["lon"] <= 50]
    print(" Fertile Crescent box (29-42N, 34-50E):", len(ne), sorted({(r['name']) for r in ne}))
json.dump(rows, open(sys.argv[3], "w"))
