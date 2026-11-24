"""Find crop-keyword taxon IDs used in downloaded cores but absent from the study's 32 IDs; query Neotoma
occurrences (12-50 ka) for them and count pollen datasets not already among the study's 156."""
import json, sys, pathlib, time, urllib.request, collections
sys.path.insert(0, sys.argv[1]); import run_ice_age_farming as iaf
caches = [pathlib.Path(p) for p in sys.argv[2:4]]; OUT = pathlib.Path(sys.argv[4]); OUTDIR = pathlib.Path(sys.argv[5])
ids = {}
for c in caches:
    for p in c.glob("core_*.json"):
        for s in json.loads(p.read_text())["data"][0]["site"]["collectionunit"]["dataset"].get("samples") or []:
            for d in s.get("datum") or []:
                if iaf.is_crop_taxon(d.get("taxonid"), d.get("variablename")) and d.get("taxonid") not in iaf.CROP_ID_SET:
                    ids[d.get("taxonid")] = d.get("variablename")
print("extra crop-keyword taxon IDs:", ids)
study = set()
for p in caches[0].glob("occ_pre12_t*.json"):
    for r in json.loads(p.read_text()).get("data") or []:
        s = r.get("site") or {}
        if s.get("datasettype") == "pollen" and (r.get("sample") or {}).get("value") not in (None, 0): study.add(s["datasetid"])
new = collections.defaultdict(list)
for tid, name in sorted(ids.items(), key=lambda x: str(x[0])):
    if tid is None: continue
    cp = OUTDIR / f"occ_extra_t{tid}.json"
    if not cp.exists():
        url = f"https://api.neotomadb.org/v2.0/data/occurrences?taxonid={tid}&ageold=50000&ageyoung=12000&limit=500"
        raw = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; research-client/1.0)"}), timeout=60).read()
        cp.write_bytes(raw); time.sleep(0.5)
    rows = json.loads(cp.read_text()).get("data") or []
    for r in rows:
        s = r.get("site") or {}
        if s.get("datasettype") == "pollen" and (r.get("sample") or {}).get("value") not in (None, 0) and s["datasetid"] not in study:
            new[s["datasetid"]].append((name, s.get("sitename"), (r.get("age") or {}).get("age"), r["sample"]["value"]))
    print(tid, name, "rows", len(rows))
print("datasets with pre-12 ka crop-type occurrences under non-listed IDs and not in the study's 156:", len(new))
for k, v in new.items(): print(" ", k, v[0][1], len(v), v[:3])
OUT.write_text(json.dumps({"extra_ids": {str(k): v for k, v in ids.items()}, "new": {str(k): v for k, v in new.items()}}, indent=1))
