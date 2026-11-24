import json, sys
d = json.load(open(sys.argv[1]))
print("eu pool", d["eu_pool_size"], "cohort spanning 11-3 ka by metadata:", d["cohort_span_11k_3k"], "/", len(d["calibration_cohort"]))
def summ(rows, w):
    el = [r for r in rows if r.get(w) and r[w]["eligible"]]
    rel = sum(r[w]["relaxed"] for r in el); st = sum(r[w]["strict"] for r in el)
    crop = sum(1 for r in el if r[w]["n_crop_any"] > 0)
    return len(el), rel, st, crop
eu = d["eu_fair"]
print("EU fair sample:", len(eu), "errors", sum(1 for r in eu if "error" in r), "in cal cohort", sum(1 for r in eu if r.get("in_cal_cohort")))
for w in ("holo_8500_2000", "meso_11500_9000"):
    n, rel, st, crop = summ(eu, w); print(f"  {w}: eligible {n}, relaxed {rel} ({100*rel/max(1,n):.0f}%), strict {st} ({100*st/max(1,n):.0f}%), any crop pollen {crop}")
el = [r for r in eu if r.get("holo_8500_2000") and r["holo_8500_2000"]["eligible"] and not r.get("in_cal_cohort")]
print("  holo excluding cohort members: n", len(el), "relaxed", sum(r["holo_8500_2000"]["relaxed"] for r in el), "strict", sum(r["holo_8500_2000"]["strict"] for r in el))
meso = [r for r in eu if r.get("meso_11500_9000") and r["meso_11500_9000"]["eligible"] and r["lat"] and r["lat"] >= 46]
print("  meso lat>=46: n", len(meso), "relaxed", sum(r["meso_11500_9000"]["relaxed"] for r in meso), "strict", sum(r["meso_11500_9000"]["strict"] for r in meso))
print("NEAR EAST:")
for w in ("ppn_11500_9000", "neo_9000_6000", "holo_8500_2000", "all_11500_2000"):
    n, rel, st, crop = summ(d["near_east"], w); print(f"  {w}: eligible {n}, relaxed {rel}, strict {st}, any crop pollen {crop}")
for r in d["near_east"]:
    if "error" in r: print("  ERR", r); continue
    def f(w):
        x = r.get(w)
        if not x: return "-"
        return f"{'E' if x['eligible'] else 'ne'} n={x['n_win']} R={int(x['relaxed'])} S={int(x['strict'])} crop={x['n_crop_any']} max={x['max_crop_pct']} bAP={x['baseline_ap']} eR={x['earliest_relaxed']} eS={x['earliest_strict']}"
    print(f"  {r['datasetid']} {r['sitename']} ({r['lat']:.2f},{r['lon']:.2f}) | PPN: {f('ppn_11500_9000')} | 9-6: {f('neo_9000_6000')} | 8.5-2: {f('holo_8500_2000')}")
