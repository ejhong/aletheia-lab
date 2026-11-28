"""Summarise huron_catalog.json: non-overview sources under each tile, whether the claimed survey is among them,
and value-quantisation / duplication statistics of the exported tile.
usage: python -I catalog_summary.py <huron_catalog.json> <huron_tiles_dir> <out.json>"""
import json, sys, pathlib
import numpy as np
from PIL import Image
cat = json.load(open(sys.argv[1])); tdir = pathlib.Path(sys.argv[2]); out = {}
for tid, r in cat.items():
    src = [s for s in r["sources"] if s.get("Name") and not s["Name"].startswith("Ov_")]
    names = sorted({s["Name"] for s in src})
    claimed = r["survey_claimed"]
    rec = {"px_claimed": r["px_m_claimed"], "survey_claimed": claimed, "surveys_under_tile": names,
           "claimed_survey_present": any(n.startswith(claimed) for n in names), "dup_frac": r.get("frac_pixels_with_identical_neighbour")}
    tp = tdir / f"{tid}.tif"
    if tp.exists() and tp.stat().st_size > 4096:
        z = np.array(Image.open(tp), dtype=np.float64); v = np.isfinite(z) & (z > -1000) & (z < 5)
        if v.mean() > 0.03:
            vals = np.unique(z[v]); d = np.diff(vals)
            rec["median_value_step_m"] = float(np.median(d)) if len(d) else None
            rec["n_unique"] = int(len(vals))
            # equal-run lengths along rows and columns
            def runlen(a, vm):
                eq = (a[:, 1:] == a[:, :-1]) & vm[:, 1:] & vm[:, :-1]
                return float(eq.sum() / max(1, (vm[:, 1:] & vm[:, :-1]).sum()))
            rec["eq_along_rows"] = round(runlen(z, v), 3); rec["eq_along_cols"] = round(runlen(z.T, v.T), 3)
    out[tid] = rec
json.dump(out, open(sys.argv[3], "w"), indent=1)
for tid, r in out.items():
    print(tid, r["px_claimed"], r["survey_claimed"], "present" if r["claimed_survey_present"] else "ABSENT", r["surveys_under_tile"], r.get("median_value_step_m"), r.get("eq_along_rows"), r.get("eq_along_cols"))
