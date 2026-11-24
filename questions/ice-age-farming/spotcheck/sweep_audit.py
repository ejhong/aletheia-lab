"""Audit the study's pre-12 ka sweep and calibration cohort from its own cache, with its own functions."""
import json, sys, pathlib, collections
sys.path.insert(0, sys.argv[1]); import run_ice_age_farming as iaf
C = pathlib.Path(sys.argv[2]); R = json.load(open(sys.argv[3])); S2 = json.load(open(sys.argv[4]))
cand = R["pre12ka_sweep"]["all_pre12ka_candidates_summary"]
crop_names, weed_names = collections.Counter(), collections.Counter()
relaxed_sites = []
for e in cand:
    core = iaf.extract_core_samples(json.loads((C / f"core_{e['datasetid']}.json").read_text()))
    for r in core["samples"]:
        if 12000 <= r["age_cal"] <= 50000:
            for k in r["crop_taxa"]: crop_names[k] += 1
            for k in r["weed_taxa"]: weed_names[k] += 1
    lg = iaf.evaluate_window(core, 12000, 18000, True); lgm = iaf.evaluate_window(core, 18000, 50000, True)
    if lg["farm_relaxed"] or lgm["farm_relaxed"]:
        relaxed_sites.append((e["datasetid"], e["sitename"], e["lat"], e["lon"], lg["farm_relaxed"], lgm["farm_relaxed"]))
print("crop taxon names in 12-50 ka samples (sample counts):", crop_names.most_common())
print("\nweed taxon names in 12-50 ka samples:", weed_names.most_common(40))
print("\nrelaxed hits (any window):", len(relaxed_sites))
reg = collections.Counter()
for d in relaxed_sites:
    lat, lon = d[2], d[3]
    reg["Europe/Med (lat34-72, lon-10..45)" if lat and 34 <= lat <= 72 and -12 <= lon <= 45 else ("other: %s" % d[1])] += 1
print(reg.most_common())
lats = [e["lat"] for e in cand if e["lat"] is not None]
print("\n150 candidates by region: Europe/Med box", sum(1 for e in cand if e['lat'] and 34<=e['lat']<=72 and -12<=e['lon']<=45), "| tropics", sum(1 for l in lats if abs(l)<23.5), "| N America", sum(1 for e in cand if e['lon'] is not None and e['lon']<-30 and e['lat']>15))
print("unique sites among 150:", len({e['sitename'] for e in cand}))
# calibration cohort
coh = S2["calibration_cohort"]
print("\ncohort n", len(coh), "unique site names", len({iaf.extract_core_samples(json.loads((C / f'core_{d}.json').read_text()))['sitename'] for d in coh}))
print("cohort spanning 11-3 ka by metadata:", S2.get("cohort_span_11k_3k"))
