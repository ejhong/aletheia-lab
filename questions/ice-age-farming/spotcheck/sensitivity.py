"""Sensitivity checks of the study's own detectors (evaluate_window, unchanged) on
(a) a random sample of European pollen datasets spanning 8.5-2 ka, NOT selected on cereal pollen;
(b) all Near Eastern (Fertile Crescent box) pollen datasets reaching >= 9 ka.
Downloads go to data/neotoma_cache2 (sequential, generic UA). Reads the study's dataset listing cache."""
import json, sys, pathlib, random, time, urllib.request, collections
sys.path.insert(0, sys.argv[1]); import run_ice_age_farming as iaf
C = pathlib.Path(sys.argv[2]); C2 = pathlib.Path(sys.argv[3]); OUT = pathlib.Path(sys.argv[4])
N_EU = int(sys.argv[5]) if len(sys.argv) > 5 else 60

def fetch(dsid):
    for cdir in (C, C2):
        p = cdir / f"core_{dsid}.json"
        if p.exists() and p.stat().st_size > 2:
            return json.loads(p.read_text())
    req = urllib.request.Request(f"https://api.neotomadb.org/v2.0/data/downloads/{dsid}", headers={"User-Agent": "Mozilla/5.0 (compatible; research-client/1.0)"})
    raw = urllib.request.urlopen(req, timeout=60).read()
    (C2 / f"core_{dsid}.json").write_bytes(raw); time.sleep(0.5)
    return json.loads(raw)

idx = {}
for p in sorted(C.glob("ds_all_pollen_off*.json")):
    for item in json.loads(p.read_text())["data"]:
        s = item["site"]; lon, lat = iaf.parse_lon_lat(s.get("geography"))
        for ds in s.get("datasets") or []:
            if ds.get("datasettype") != "pollen": continue
            ao = ay = None
            for ar in ds.get("agerange") or []:
                u = ar.get("units") or ""
                if "AD/BC" in u: continue
                if ar.get("ageold") is not None: ao = iaf.normalize_age_cal_bp(ar["ageold"], u)[0]
                if ar.get("ageyoung") is not None: ay = float(ar["ageyoung"])
            idx[ds["datasetid"]] = dict(site=s["siteid"], name=s["sitename"], lat=lat, lon=lon, ao=ao, ay=ay, db=ds.get("database"))

# reconstruct the study's calibration cohort exactly as the program did
eu_cal, seen = [], set()
for tid in [1947, 416, 427, 497]:
    for off in range(0, 4000, 500):
        p = C / f"eu_holo_occ_t{tid}_off{off}.json"
        if not p.exists(): break
        batch = json.loads(p.read_text()).get("data") or []
        for r in batch:
            s = r.get("site") or {}
            if s.get("datasettype") != "pollen": continue
            d = s.get("datasetid")
            if d in seen: continue
            lon, lat = iaf.parse_lon_lat(s.get("location"))
            if lon is not None and lat is not None and -10 <= lon <= 45 and 34 <= lat <= 62:
                seen.add(d); eu_cal.append(d)
                if len(eu_cal) >= 100: break
        if len(eu_cal) >= 100 or len(batch) < 500: break
    if len(eu_cal) >= 100: break

def evalcore(dsid, windows):
    core = iaf.extract_core_samples(fetch(dsid))
    out = {"datasetid": dsid, "sitename": core.get("sitename"), "lat": core.get("lat"), "lon": core.get("lon"), "n_valid": core.get("n_samples_valid")}
    for name, lo, hi, nmin in windows:
        if not core.get("samples"):
            out[name] = None; continue
        r = iaf.evaluate_window(core, lo, hi, require_chron=False)
        ok = r["has_data"] and r["n_win"] >= nmin
        out[name] = {"eligible": ok, "n_win": r["n_win"], "relaxed": r["farm_relaxed"], "strict": r["farm_strict_unfiltered"], "n_crop_any": r["n_crop_any"], "max_crop_pct": r["max_crop_pct"], "baseline_ap": r["baseline_ap"], "earliest_relaxed": r["earliest_relaxed_age"], "earliest_strict": r["earliest_strict_age"]}
    return out

res = {"calibration_cohort": eu_cal}
# cohort facts
coh = [idx.get(d) for d in eu_cal]
res["cohort_span_11k_3k"] = sum(1 for r in coh if r and r["ao"] and r["ao"] >= 11000 and r["ay"] is not None and r["ay"] <= 3000)

# (a) fair European sample
eu_pool = sorted(d for d, r in idx.items() if r["lat"] is not None and -10 <= r["lon"] <= 45 and 34 <= r["lat"] <= 62 and r["ao"] and r["ao"] >= 8500 and r["ay"] is not None and r["ay"] <= 2000)
random.seed(20261124); eu_sample = random.sample(eu_pool, N_EU)
res["eu_pool_size"] = len(eu_pool)
W_EU = [("holo_8500_2000", 2000, 8500, 5), ("meso_11500_9000", 9000, 11500, 2)]
res["eu_fair"] = []
for d in eu_sample:
    try: res["eu_fair"].append(evalcore(d, W_EU) | {"in_cal_cohort": d in eu_cal})
    except Exception as e: res["eu_fair"].append({"datasetid": d, "error": str(e)})
    print("eu", d, flush=True)
# (b) Near East
ne = sorted(d for d, r in idx.items() if r["lat"] is not None and 29 <= r["lat"] <= 42 and 34 <= r["lon"] <= 50 and r["ao"] and r["ao"] >= 9000)
W_NE = [("ppn_11500_9000", 9000, 11500, 2), ("neo_9000_6000", 6000, 9000, 2), ("holo_8500_2000", 2000, 8500, 5), ("all_11500_2000", 2000, 11500, 5)]
res["near_east"] = []
for d in ne:
    try: res["near_east"].append(evalcore(d, W_NE))
    except Exception as e: res["near_east"].append({"datasetid": d, "error": str(e)})
    print("ne", d, flush=True)
OUT.write_text(json.dumps(res, indent=1, default=str))
