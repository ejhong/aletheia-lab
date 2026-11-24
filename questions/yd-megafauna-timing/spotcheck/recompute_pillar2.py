"""Independent recomputation of the Pillar 2 headline numbers (spot check, not part of the locked run).

Computes, from the raw Broughton & Weitzel (2018) spreadsheet and IntCal20 with code written
separately from analysis/megafauna_timing.py:
  - spreadsheet row counts by score and method;
  - M_yd (share of SPD mass in 12,700-11,700 cal BP) and R_pre (mean SPD 13,500-12,900 over
    14,700-13,500) for all dates and for Score 12 AMS dates, using the protocol's subset rule
    (6,000-35,000 14C BP, >= 50% of the posterior inside 20,000-9,000 cal BP);
  - the M_yd excess expressed as a number of dates;
  - every Score 12 AMS date with P(cal age < 12,750) > 0.95, its median, and years after 12,850 and
    12,750, both from this calibration and from the study's results/megafauna_calibrated.tsv;
  - the Bonner Springs and Pyramid Lake rows exactly as they appear in the spreadsheet.
Calibration: 1-year grid 9,000-25,000 cal BP, full Gaussian likelihood (see common.calibrate).

Needs (see ../MANIFEST.md): data/intcal20.14c and data/broughton2018_s1.xlsx.
Run:  python -I -B questions/yd-megafauna-timing/spotcheck/recompute_pillar2.py [DATA_DIR]
"""
import collections
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

from common import RESULTS, calibrate, data_dir, load_broughton, load_intcal  # noqa: E402

d = data_dir()
recs = load_broughton(d)
print("== Spreadsheet")
print(f"rows with numeric RCYBP and Error: {len(recs)}")
print("score x method:", dict(collections.Counter((r["score"], r["method"]) for r in recs)))

ic = load_intcal(d)
g = np.arange(9000, 25001, 1.0)
mu, sg = np.interp(g, ic[:, 0], ic[:, 1]), np.interp(g, ic[:, 0], ic[:, 2])
print(f"IntCal20 14C age at 12,850 cal BP: {np.interp(12850, ic[:, 0], ic[:, 1]):.0f}")

sel = [r for r in recs if 6000 <= r["rc"] <= 35000 and r["err"] > 0]
P = calibrate([r["rc"] for r in sel], [r["err"] for r in sel], mu, sg)
win = (g >= 9000) & (g <= 20000)
for r, p in zip(sel, P):
    r["p"], r["in_window"], r["p_lt_12750"] = p, p[win].sum(), p[g < 12750].sum()
    r["median"] = g[np.searchsorted(np.cumsum(p), 0.5)]
allin = [r for r in sel if r["in_window"] >= 0.5]
ams = [r for r in allin if r["method"] in ("MS", "AMS")]
print(f"dates in 6,000-35,000 14C BP: {len(sel)}; >=50% inside 20-9 ka: all {len(allin)}, Score 12 AMS {len(ams)}")

print("\n== SPD statistics (study's value in brackets)")
gw = g[win]
study = {"all": ("5.61%", "1.900"), "score12_ams": ("4.95%", "1.917")}
for name, sub in (("all", allin), ("score12_ams", ams)):
    spd = sum(r["p"][win] for r in sub)
    spd = spd / spd.sum()
    m_yd = spd[(gw >= 11700) & (gw <= 12700)].sum()
    r_pre = spd[(gw >= 12900) & (gw <= 13500)].mean() / spd[(gw > 13500) & (gw <= 14700)].mean()
    print(f"{name:12s} n={len(sub)}  M_yd={100 * m_yd:.2f}% [{study[name][0]}]  R_pre={r_pre:.3f} [{study[name][1]}]"
          f"  M_yd x n = {m_yd * len(sub):.1f} dates = {100 * m_yd:.1f}% of the subset's dates")

their = {}
with open(RESULTS / "megafauna_calibrated.tsv", newline="") as f:
    for row in csv.DictReader(f, delimiter="\t"):
        their[(row["lab_id"].strip(), float(row["rcybp"]))] = float(row["cal_median"])

surv = sorted((r for r in ams if r["p_lt_12750"] > 0.95), key=lambda r: r["rc"])
print(f"\n== Score 12 AMS dates with P(cal age < 12,750) > 0.95: {len(surv)}")
print("taxon        site                        lab                  14C       P(<12750) | this calibration: median, yrs after 12850/12750 | study median, yrs after 12850/12750")
for r in surv:
    tm = their.get((r["lab"], r["rc"]))
    tm_txt = f"{tm:8.0f} {12850 - tm:6.0f} {12750 - tm:6.0f}" if tm is not None else "   (not found)"
    print(f"{r['taxon']:12s} {r['site'][:27]:27s} {r['lab'][:20]:20s} {r['rc']:5.0f}±{r['err']:<4.0f} {r['p_lt_12750']:.4f}"
          f"   | {r['median']:8.0f} {12850 - r['median']:6.0f} {12750 - r['median']:6.0f}"
          f"                    | {tm_txt}")
for label, taxa in (("all survivors", None), ("mammoths and mastodons", ("Mammuthus", "Mammut"))):
    sub = [r for r in surv if taxa is None or r["taxon"] in taxa]
    mine = [12850 - r["median"] for r in sub]
    st = [12850 - their[(r["lab"], r["rc"])] for r in sub if (r["lab"], r["rc"]) in their]
    print(f"years after 12,850, {label}: this calibration {min(mine):.0f}-{max(mine):.0f}; study medians {min(st):.0f}-{max(st):.0f}")

print("\n== Spreadsheet rows for site 'Bonner Springs' and site 'Pyramid Lake' (exact site name), as given")
print("   (the Camelops row 'Harrelson 2, Pyramid Lake' is a different site and is not listed)")
print("taxon | state | site | lab | RCYBP | Error | material | method | score")
for r in recs:
    if r["site"] in ("Bonner Springs", "Pyramid Lake"):
        print(" | ".join([r["taxon"], r["state"], r["site"], r["lab"], f"{r['rc']:.0f}", f"{r['err']:.0f}",
                          r["material"], r["method"], r["score"]]))
