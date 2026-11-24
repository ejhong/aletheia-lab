# Adds a small CI-chondrite component to Hall's Cave's own background and reports the locked CLR class and mixing delta RMSE, to see whether the classifier can detect a dilute impact signal. Run: python spotcheck/dilution_test.py [data_dir] [results/summary.json]
import json
import pathlib
import sys

import numpy as np

from _common import QDIR, load_program

m = load_program()
data = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else QDIR / "data"
d = json.loads((pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else QDIR / "results" / "summary.json").read_text())
ref = d["reference_endmembers"]
ci = m.hse_vec(m.CI_CHONDRITE_PPT)
ucc = m.hse_vec(ref["ucc_ppt"])
iron = m.hse_vec(ref["iron_steelman_ppt"])
volc = [m.hse_vec(v) for v in ref["volcanic_condensates_ppt"].values()]
kpg = m.parse_kpg2025_benchmark(data / "kpg2025_MOESM4.xlsx")  # Petriccio is not in the program's centroid either (row lacks two elements)
protos = {
    "chondrite": m.ci_clr(ci),
    "kpg_impact": np.median([m.ci_clr(m.hse_vec(s)) for s in kpg], axis=0),
    "volcanic": np.mean([m.ci_clr(v) for v in volc], axis=0),
    "ucc": m.ci_clr(ucc),
}
hc = d["pillar1a_full_hse"]["halls_cave"]
bg, bg_r = m.hse_vec(hc["bg_ppt"]), hc["bg_os_iso"]
print(f"K-Pg control samples used for the centroid: {[s['sample'] for s in kpg]}")
print("Hall's Cave background (ppt):", {e: round(float(v), 1) for e, v in zip(m.HSE_ORDER, bg)}, "187Os/188Os", bg_r)
for add_ir in (5, 10, 20, 50, 100, 200, 500):
    f = add_ir / ci[1]
    x = (1 - f) * bg + f * ci
    r = ((1 - f) * bg[0] * bg_r + f * ci[0] * m.CI_187OS_188OS) / ((1 - f) * bg[0] + f * ci[0])
    cls, _ = m.clr_classify(x, protos)
    cosmic = min(m.mixing_rmse(x, r, bg, bg_r, ci, m.CI_187OS_188OS)["rmse"],
                 m.mixing_rmse(x, r, bg, bg_r, iron, m.CI_187OS_188OS)["rmse"])
    volcanic = min(m.mixing_rmse(x, r, bg, bg_r, v, 0.15)["rmse"] for v in volc)
    print(f"+{add_ir:3d} ppt Ir from CI (f={f:.1e}): Ir={x[1]:5.0f} Pt={x[3]:5.0f} Os={x[0]:5.0f} "
          f"187Os/188Os={r:.2f}  CLR class={cls:10s} dRMSE={cosmic - volcanic:+.3f}")
