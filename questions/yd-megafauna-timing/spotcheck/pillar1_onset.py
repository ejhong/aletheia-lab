"""RESULTS.md Table 1 (Sporormiella timing tests) recomputed against three onset ages, plus half-drop
sensitivity checks. (Spot check, not part of the locked run.)

Onset ages: 12,896 (the study's T_YD, given as cal BP), 12,846 cal BP (the same Greenland GS-1 onset,
12,896 b2k, converted to BP = b2k - 50), and 12,835 cal BP (Kennett et al. 2015, the study's second
reference). For each estimator (t_onset, t_50pct, t_2pct, t_cp) it prints n, median, IQR, median lead,
cores before onset, Wilcoxon signed-rank p (two-sided and one-sided "before") and exact binomial
sign-test p (two-sided), with the same conventions as the study (zero differences dropped for the
Wilcoxon). Then: half-drops more than 1,000 years before onset, and the half-drop tests without
Tulare Lake (4 nonzero samples, peak 0.86%) and without both sub-2% cores (Tulare, Triangle Lake Bog).

Input: the per-core decline ages in ../results/sporormiella_sites.tsv (committed in git; a clean
rerun of analysis/megafauna_timing.py on the MANIFEST data reproduced that file byte for byte).
No raw data needed.
Run:  python -I -B questions/yd-megafauna-timing/spotcheck/pillar1_onset.py
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
from scipy import stats  # noqa: E402

from common import RESULTS  # noqa: E402

with open(RESULTS / "sporormiella_sites.tsv", newline="") as f:
    sites = list(csv.DictReader(f, delimiter="\t"))
EST = ("t_onset", "t_50pct", "t_2pct", "t_cp")
REFS = (12896.0, 12846.0, 12835.0)


def vals(col, exclude=()):
    return [float(s[col]) for s in sites if s[col].strip() and s["site_name"] not in exclude]


def tests(v, ref):
    a = np.array(v)
    dif = a - ref
    nz = dif[dif != 0]
    nb = int((dif > 0).sum())
    return {
        "n": len(a), "median": np.median(a), "iqr": (np.percentile(a, 25), np.percentile(a, 75)),
        "lead": np.median(dif), "before": nb,
        "w2": stats.wilcoxon(nz, alternative="two-sided").pvalue,
        "w1": stats.wilcoxon(nz, alternative="greater").pvalue,
        "b2": stats.binomtest(nb, len(a), 0.5, alternative="two-sided").pvalue,
    }


print("Per-core decline ages (cal BP) from results/sporormiella_sites.tsv:")
for s in sites:
    print(f"  {s['site_name']:22s} " + "  ".join(f"{e}={s[e] or '-':>8s}" for e in EST))

table = {}
for ref in REFS:
    print(f"\n== Table 1 against onset {ref:,.0f} cal BP")
    print("estimator  n   median  IQR            lead     before     Wilcoxon 2-sided  1-sided  binomial 2-sided")
    for e in EST:
        t = tests(vals(e), ref)
        table[(ref, e)] = t
        print(f"{e:9s} {t['n']:2d}  {t['median']:7.0f}  {t['iqr'][0]:5.0f}-{t['iqr'][1]:5.0f}  {t['lead']:+6.0f}   "
              f"{t['before']:2d}/{t['n']:<2d} ({100 * t['before'] / t['n']:3.0f}%)   {t['w2']:.4f}            "
              f"{t['w1']:.4f}   {t['b2']:.4f}")

print("\n== What changes between 12,896 and 12,846 (counts and p-values; leads shift by exactly 50 years)")
changed = False
for e in EST:
    a, b = table[(12896.0, e)], table[(12846.0, e)]
    for k in ("before", "w2", "w1", "b2"):
        if round(a[k], 6) != round(b[k], 6):
            changed = True
            print(f"  {e} {k}: {a[k]:.4f} -> {b[k]:.4f}")
if not changed:
    print("  nothing: every count and p-value in Table 1 is identical")

print("\n== Half-drop (t_50pct) checks")
for ref in REFS:
    v = vals("t_50pct")
    n1000 = sum(x - ref > 1000 for x in v)
    print(f"onset {ref:,.0f}: half-drop more than 1,000 yr before onset in {n1000} of {len(v)} cores")
    for label, excl in (("all 11 cores", ()), ("without Tulare Lake", ("Tulare Lake",)),
                        ("without Tulare and Triangle Lake Bog", ("Tulare Lake", "Triangle Lake Bog"))):
        t = tests(vals("t_50pct", excl), ref)
        print(f"   {label:38s} n={t['n']:2d}  before {t['before']}/{t['n']}  Wilcoxon 2-sided p={t['w2']:.4f}"
              f"  sign test 2-sided p={t['b2']:.4f}")
