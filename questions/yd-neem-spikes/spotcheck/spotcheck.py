#!/usr/bin/env python3
"""Spot-check of the locked NEEM fire-spike study (#114). Not part of the locked protocol; not new evidence.

Written by Claude Opus 5.5 (Anthropic) on 2026-11-24 as an outside spot-check of a study run by another vendor's
agent. It reuses the study's own locked code (../analysis/neem_spikes.py) for loading data and for the yearly and
window statistics, and adds checks the study did not report:

  1. The 51-year running median (the denominator of the >5x test) before and after onset, and its ratio.
  2. Denominator swap: pre-onset plume sizes put on the post-onset baseline, and post-onset plumes put on the
     pre-onset baseline, counted at >5x and >10x.
  3. Absolute plume counts at 30-150 ug/kg above baseline, with the study's exact conditional binomial test, and
     a 95% interval for the >50 ug/kg rate ratio.
  4. The flux control as the protocol words it (mean layer thickness) against the code (median).
  5. Mean layer thickness and samples per year in the onset windows and in the early Holocene windows; the early
     Holocene plume and spike_part ranges.
  6. Width at half height of the ten largest spikes, and autocorrelation of the 1-mm series (smoothing).
  7. Verdict when the onset is moved by -50, -25, +25 and +50 years.
  8. Spike counts at the earlier stadial onsets (Pillar 2), recomputed with the study's rules.

Data (not in git; download per ../MANIFEST.md and check the SHA-256 there):
  neem_cfa_1mm.tab     https://doi.pangaea.de/10.1594/PANGAEA.935837?format=textfile
  neem_gicc05_5cm.tab  https://doi.pangaea.de/10.1594/PANGAEA.925552?format=textfile
  neem_cfa_10yr.tab    https://doi.pangaea.de/10.1594/PANGAEA.935831?format=textfile   (step cross-check only)

Run from the repo root (DATA_DIR defaults to questions/yd-neem-spikes/data):
  .venv/bin/python -I questions/yd-neem-spikes/spotcheck/spotcheck.py [DATA_DIR]
Writes nothing; prints the numbers in output.txt.
"""
from __future__ import annotations

import pathlib
import sys

sys.dont_write_bytecode = True  # keep the analysis/ folder untouched

import numpy as np
from scipy import stats

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "analysis"))
import neem_spikes as ns  # noqa: E402  (the study's locked code, SHA-256 in ../MANIFEST.md)

DATA = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parent / "data"


def window_mask(years, ys, k, onset=ns.ONSET):
    lo, hi = onset - ns.W * (k + 1), onset - ns.W * k
    return (years >= lo) & (years < hi) & np.isfinite(ys["ratio"]) & np.isfinite(ys["med"])


def binom_p(a, b, na, nb):
    """The study's test: exact two-sided binomial on a of a+b, expected share na/(na+nb)."""
    return stats.binomtest(a, a + b, p=na / (na + nb)).pvalue if a + b else 1.0


def fwhm_widths(v, n=10, base_len=201, guard=20):
    """Width at half height (in samples) of the n largest peaks above a 201-sample running mean."""
    ex = v - np.convolve(v, np.ones(base_len) / base_len, mode="same")
    used = np.zeros(len(v), bool)
    widths = []
    for i in np.argsort(ex)[::-1]:
        if used[max(0, i - guard): i + guard + 1].any():
            continue
        half, l, r = ex[i] / 2, i, i
        while l > 0 and ex[l] > half:
            l -= 1
        while r < len(v) - 1 and ex[r] > half:
            r += 1
        widths.append(int(r - l))
        used[i] = True
        if len(widths) == n:
            break
    return widths


def main():
    gd, ga, _ = ns.load_neem_gicc05(DATA / "neem_gicc05_5cm.tab")

    def lam(age):  # same 20-year layer thickness as run_pipeline() in neem_spikes.py
        return (np.interp(age + 10.0, ga, gd) - np.interp(age - 10.0, ga, gd)) / 20.0

    ages, vals = ns.load_neem_nh4_range(DATA / "neem_cfa_1mm.tab", gd, ga, ns.LO - 30, ns.HI + 30)
    ys = ns.compute_yearly_stats(ages, vals, ns.LO, ns.HI, min_samples=15, layer_thick_fn=lam)
    yr = ys["years"]
    s = ns.summarize_windows(ys)
    m0, m1 = window_mask(yr, ys, 0), window_mask(yr, ys, -1)
    n0, n1 = int(m0.sum()), int(m1.sum())
    print(f"Reproduced study: verdict {ns.decide_verdict(s)}; windows {s['n_windows']}; "
          f"years after/before {n0}/{n1}")

    print("\n1. Denominator of the >5x test (51-yr running median of yearly medians), window mean")
    run0, run1 = np.nanmean(ys["run"][m0]), np.nanmean(ys["run"][m1])
    lvl0, lvl1 = s["window_after"]["level"], s["window_before"]["level"]
    print(f"   running median: before {run1:.2f}  after {run0:.2f}  ratio {run0 / run1:.2f}")
    print(f"   (study's 'level' = mean of yearly medians: before {lvl1:.2f}  after {lvl0:.2f}  "
          f"ratio {lvl0 / lvl1:.2f})")

    print("\n2. Denominator swap (top/run > t  <=>  excess > (t-1)*run; window-mean run of the target window)")
    ex0, ex1 = ys["excess"][m0], ys["excess"][m1]
    print(f"   observed            >5x: after {int(np.sum(ys['ratio'][m0] > 5))}  before "
          f"{int(np.sum(ys['ratio'][m1] > 5))};  >10x: after {int(np.sum(ys['ratio'][m0] > 10))}  "
          f"before {int(np.sum(ys['ratio'][m1] > 10))}")
    print(f"   before-plumes on after-baseline:  >5x {int(np.sum(ex1 > 4 * run0))}   >10x {int(np.sum(ex1 > 9 * run0))}")
    print(f"   after-plumes on before-baseline:  >5x {int(np.sum(ex0 > 4 * run1))}   >10x {int(np.sum(ex0 > 9 * run1))}")
    for t in (3, 4, 5, 6, 8, 10):
        print(f"   ratio >{t:>2}: after {int(np.sum(ys['ratio'][m0] > t)):>2}  before {int(np.sum(ys['ratio'][m1] > t)):>2}")

    print("\n3. Absolute plume years (peak minus running median > t ug/kg); p = study's exact binomial test")
    for t in (30, 40, 50, 60, 75, 100, 150):
        a, b = int(np.sum(ex0 > t)), int(np.sum(ex1 > t))
        tag = "  (pre-registered secondary)" if t in (30, 100) else "  (pre-registered primary)" if t == 50 else ""
        print(f"   >{t:>3}: after {a:>2}  before {b:>2}  p = {binom_p(a, b, n0, n1):.3f}{tag}")
    a, b = int(np.sum(ex0 > 50)), int(np.sum(ex1 > 50))
    ci = stats.binomtest(a, a + b).proportion_ci(0.95, method="exact")
    to_rr = lambda p: (p / (1 - p)) * (n1 / n0)  # noqa: E731
    print(f"   >50 rate ratio {(a / n0) / (b / n1):.2f}, 95% CI {to_rr(ci.low):.2f}-{to_rr(ci.high):.2f} "
          f"(exact Clopper-Pearson interval on a/(a+b), conditional on a+b, converted to a rate ratio with "
          f"the valid years {n0} and {n1})")

    print("\n4. Flux control (excess x lambda / lambda_ref > 50)")
    L = ys["lambda_m_yr"]
    for name, ref in (("protocol, mean lambda", np.nanmean(L)), ("code, median lambda", np.nanmedian(L))):
        fx = ys["excess"] * L / ref
        print(f"   {name:<22} ref {100 * ref:.2f} cm/yr: after {int(np.sum(fx[m0] > 50))}  before {int(np.sum(fx[m1] > 50))}")

    print("\n5. Layer thickness, samples per year, early Holocene")
    for name, m in (("before (-1)", m1), ("after (0)", m0)):
        print(f"   {name:<11} mean layer {100 * np.nanmean(L[m]):.2f} cm/yr, samples/yr median "
              f"{np.median(ys['counts'][m]):.0f} mean {ys['counts'][m].mean():.1f}")
    hol = [w for w in s["windows"] if w["k"] >= 8]
    rng = lambda key: (min(w[key] for w in hol), max(w[key] for w in hol))  # noqa: E731
    print(f"   early Holocene windows k=8..15 ({hol[0]['from_b2k']}-{hol[-1]['to_b2k']} b2k):")
    for key in ("samples_per_yr_med", "spike_years_x5", "spike_years_add50", "spike_years_flux50", "spike_part"):
        print(f"     {key:<20} {rng(key)[0]} - {rng(key)[1]}")
    print(f"     mean add50 {np.mean([w['spike_years_add50'] for w in hol]):.2f}, "
          f"mean flux50 {np.mean([w['spike_years_flux50'] for w in hol]):.2f}")
    t10 = ys["counts"]
    print(f"   onset windows samples/yr median: before {np.median(t10[m1]):.0f}, after {np.median(t10[m0]):.0f}")

    print("\n6. Smoothing in the 1-mm series (depth from the 5-cm GICC05 table)")
    o = np.argsort(ages)
    a_s, v_s = ages[o], vals[o]
    d_s = np.interp(a_s, ga, gd)
    for name, lo, hi in (("Allerod  -1", 12896, 13046), ("YD        0", 12746, 12896), ("Holocene 12", 10946, 11096)):
        m = (a_s >= lo) & (a_s < hi)
        v, d = v_s[m], d_s[m]
        w = fwhm_widths(v)
        x = np.log(v[v > 0])
        x = x - np.convolve(x, np.ones(101) / 101, mode="same")
        ac = [np.corrcoef(x[:-g], x[g:])[0, 1] for g in (1, 3, 5, 8, 12, 20)]
        print(f"   {name}: spacing {1000 * np.median(np.diff(d)):.2f} mm; FWHM of 10 largest peaks (samples=mm) "
              f"{w}, median {np.median(w):.0f}")
        print(f"      autocorrelation of detrended log NH4 at 1,3,5,8,12,20 mm: " + " ".join(f"{c:.2f}" for c in ac))

    print("\n7. Onset shift (verdict by the locked rule)")
    for sh in (-50, -25, 0, 25, 50):
        ss = ns.summarize_windows(ys, onset=ns.ONSET + sh)
        a_, b_ = ss["window_after"], ss["window_before"]
        print(f"   onset {ns.ONSET + sh} ({sh:+d}): {ns.decide_verdict(ss):<28} x5 {a_['spike_years_x5']}/{b_['spike_years_x5']}  "
              f"add50 {a_['spike_years_add50']}/{b_['spike_years_add50']}  level x{ss['level_after_over_before']:.2f}")

    print("\n8. Earlier stadial onsets (Pillar 2 rules: >=10 samples/yr, >=100 valid years each side)")
    a2, v2 = ns.load_neem_nh4_range(DATA / "neem_cfa_1mm.tab", gd, ga, 10400, 45500)
    y2 = ns.compute_yearly_stats(a2, v2, 10400, 45500, min_samples=10, layer_thick_fn=lam)
    for ev in ns.load_stadial_onsets(HERE.parent / "events.tsv"):
        if not 12000 <= ev["age_b2k"] <= 45000:
            continue
        t0 = int(round(ev["age_b2k"]))
        mb = (y2["years"] >= t0) & (y2["years"] < t0 + 150) & np.isfinite(y2["ratio"])
        ma = (y2["years"] >= t0 - 150) & (y2["years"] < t0) & np.isfinite(y2["ratio"])
        used = "used" if mb.sum() >= 100 and ma.sum() >= 100 else "skipped"
        print(f"   {ev['event']:<8} {t0}: valid yrs before/after {int(mb.sum()):>3}/{int(ma.sum()):>3} ({used}); "
              f">5x {int(np.sum(y2['ratio'][mb] > 5))}/{int(np.sum(y2['ratio'][ma] > 5))}  "
              f">50 ug/kg {int(np.sum(y2['excess'][mb] > 50))}/{int(np.sum(y2['excess'][ma] > 50))}")

    p10 = DATA / "neem_cfa_10yr.tab"
    if p10.exists():
        print("\n9. Cross-check with the published 10-yr NEEM averages (Erhardt et al.)")
        rows, cols, hdr = [], None, True
        for line in p10.open(encoding="utf-8", errors="ignore"):
            if hdr:
                hdr = not line.startswith("*/")
                continue
            parts = line.rstrip("\n").split("\t")
            if cols is None:
                cols = parts
                continue
            rows.append(parts)
        ai = next(i for i, c in enumerate(cols) if c.startswith("Age"))
        ni = next(i for i, c in enumerate(cols) if "NH4" in c)
        age10 = np.array([float(r[ai]) * 1000 if r[ai] else np.nan for r in rows])
        nh10 = np.array([float(r[ni]) if len(r) > ni and r[ni] else np.nan for r in rows])
        for lo, hi in ((12896, 13046), (12746, 12896)):
            m = (age10 >= lo) & (age10 < hi)
            print(f"   {hi}-{lo} b2k: mean NH4 {np.nanmean(nh10[m]):.2f} ug/kg (n={int(m.sum())})")


if __name__ == "__main__":
    main()
