"""Inspect one cached Neotoma download: metadata, chronology controls, crop/weed series."""
import json, sys, pathlib
sys.path.insert(0, sys.argv[1])  # study analysis dir (the copy in work/)
import run_ice_age_farming as iaf
cache = pathlib.Path(sys.argv[2]); dsid = sys.argv[3]
lo = float(sys.argv[4]) if len(sys.argv) > 4 else 0; hi = float(sys.argv[5]) if len(sys.argv) > 5 else 1e9
dl = json.loads((cache / f"core_{dsid}.json").read_text())
site = dl["data"][0]["site"]; cu = site["collectionunit"]; ds = cu["dataset"]
print("site:", site.get("sitename"), "| geog:", site.get("geography"), "| alt:", site.get("altitude"))
print("collunit:", cu.get("handle"), cu.get("collectionunit"), "| db:", ds.get("database"), "| defaultchron:", cu.get("defaultchronology"))
for k in ("pi", "datasetpi", "doi", "publications", "notes", "datasetnotes"):
    if k in ds: print(k, ":", str(ds[k])[:600])
for cw in cu.get("chronologies") or []:
    ch = cw.get("chronology", cw)
    meta = ch.get("chronology") if isinstance(ch.get("chronology"), dict) else ch
    print("CHRON", ch.get("chronologyid"), {k: meta.get(k) for k in ("chronologyname", "isdefault", "modelagetype", "agemodel", "dateprepared", "notes")})
    for c in ch.get("chroncontrols") or []:
        print("   ctrl depth", c.get("depth"), "age", c.get("chroncontrolage"), c.get("agelimityounger"), c.get("agelimitolder"), c.get("chroncontroltype"))
core = iaf.extract_core_samples(dl)
print("n valid samples", core["n_samples_valid"], "age range", core["age_min_cal"], core["age_max_cal"])
for r in core["samples"]:
    if lo <= r["age_cal"] <= hi:
        print(f'd={r["depth"]} raw={r["age_raw"]:.0f} cal={r["age_cal"]:.0f} {r["age_type"][:12]} S={r["terrestrial_sum"]} crop={r["crop_val"]}({r["crop_pct"]:.2f}%) weed={r["weed_pct"]:.2f}% PL={r["plantago_lan_pct"]:.2f}% AP={r["ap_pct"]} crops={r["crop_taxa"]} weeds={r["weed_taxa"]}')
