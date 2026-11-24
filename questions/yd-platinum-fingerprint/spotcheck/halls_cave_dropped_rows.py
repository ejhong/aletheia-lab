# Reruns the Pillar 2 blind-peak audit with the 8 Hall's Cave rows that the parser drops (one blank cell each) put back, under the locked 13.0-12.6 ka window and the 13.1-12.6 ka sensitivity window. Run: python spotcheck/halls_cave_dropped_rows.py [data_dir]
import pathlib
import sys

import numpy as np

from _common import QDIR, load_program

m = load_program()
data = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else QDIR / "data"
hc = m.parse_sun2020_table_s1(data / "sun2020_sm.pdf")
pl = m.parse_nanayobo2026_table_s2(data / "nanayobo2026_sm.pdf")
N = None
# Rows of Sun et al. (2020) Table S1 with one blank cell, read from the rendered PDF page 12:
# sample, depth cm, age ka, 187Os/188Os, Os, Ir, Ru, Pt, Pd, Re (ppt)
DROPPED = [
    ("HC15_18", 116, 9.865, 1.24, 50.5, N, 23.9, 434.4, 51.5, 441.8),
    ("HC15_42", 149, 12.642, 2.19, 32.5, N, 14.9, 157.7, 304.1, 268.4),
    ("HC15_11", 151, 13.008, 1.49, 37.0, 29.4, 25.8, 64.3, N, 262.1),
    ("HC15_15", 158, 13.160, 2.08, 22.6, N, 28.7, 312.1, 58.4, 290.4),
    ("HC15_09", 160, 13.173, 2.07, 23.1, 20.6, 32.8, 132.4, N, 259.1),
    ("HC16_09", 167, 13.220, 2.07, 25.2, 15.5, 31.6, 136.6, N, 298.3),
    ("HC15_07", 171, 13.241, 0.12, 4477.8, 17.7, 65.8, 67.0, N, 348.2),
    ("HC15_05", 184, 13.412, 2.05, 23.0, 37.6, 21.6, 243.5, N, 707.7),
]
full = list(hc)
for sample, depth, age, iso, *hse in DROPPED:
    rec = {"sample": sample, "depth_cm": float(depth), "age_ka": age, "os_iso": iso}
    rec.update(dict(zip(m.HSE_ORDER, hse)))
    full.append(rec)
full.sort(key=lambda r: r["depth_cm"])


def audit(hc_rows, window):
    inside = outside = hits = 0
    probs = []
    for proxy, mode in (("Pt", "high"), ("Os", "high"), ("Ir", "high"), ("os_iso", "low_iso")):
        for site, rows, pred in (
            ("HC", hc_rows, lambda r: r.get("age_ka") is not None and window[0] <= r["age_ka"] <= window[1]),
            ("PL", pl, lambda r: 848.0 <= r["depth_cm"] <= 855.0),
        ):
            valid = [r for r in rows if r.get(proxy) is not None and np.isfinite(r[proxy])]
            res = m.detect_blind_peaks([float(r[proxy]) for r in valid], mode=mode)
            mask = [bool(pred(r)) for r in valid]
            n_in = sum(1 for ev in res["events"] if any(mask[i] for i in ev["indices"]))
            g = res["global_extreme_idx"]
            hit = bool(mask[g]) if g is not None else False
            inside, outside, hits = inside + n_in, outside + len(res["events"]) - n_in, hits + hit
            probs.append(sum(mask) / len(valid))
            if site == "HC":
                print(f"   HC {proxy:6s} levels={len(valid):2d} in-window levels={sum(mask)} events in/out={n_in}/"
                      f"{len(res['events']) - n_in}  global extreme at {valid[g]['age_ka']} ka = {valid[g][proxy]}")
    p = m.poisson_binomial_tail(probs, hits)
    print(f"  window {window[1]}-{window[0]} ka: events inside={inside} outside={outside} "
          f"({outside / (inside + outside):.1%} outside), global extremes inside={hits}/8, p={p:.3f}")


for rows, label in ((hc, f"as parsed ({len(hc)} Hall's Cave rows)"), (full, f"with dropped rows restored ({len(full)})")):
    print("==", label)
    audit(rows, (12.6, 13.0))
    audit(rows, (12.6, 13.1))
