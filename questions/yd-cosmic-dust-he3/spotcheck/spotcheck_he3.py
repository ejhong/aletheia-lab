#!/usr/bin/env python3
"""Spot-check of yd-cosmic-dust-he3 (#121): re-parses the raw sources independently and recomputes the numbers
quoted in spotcheck/README.md.

What it computes, in order:
  1. SHA-256 of each data file against MANIFEST.md.
  2. Independent parse of the 181 Pacific rows, compared row by row with results/pillar1_samples.csv.
  3. Rows dropped by the study and why; exact duplicate rows in the sources.
  4. Samples per core in each of the three windows.
  5. Sedimentation rate of each of the nine cores across 20-10 ka and the smoothing time for an ASSUMED mixed layer.
  6. The 13.5-11.5 ka window: SO202-07-6 alone vs pooled vs pooled without the three Cocos Ridge samples.
  7. SO202-07-6 radiocarbon dates: raw 14C ages vs published calendar ages inside 11.5-13.5 ka.
  8. The fmol -> pcc unit factor at analysis/cosmic_dust_he3.py line 371, and that ratios do not depend on it.
  9. Make-up of the blind top-18 peak scan.
 10. Pacific core medians and their spread against Brook et al. (2000) ice-core values.
 11. The post-hoc Late Eocene 4.00x diagnostic in ODP 757B, with sample counts.

Data: the nine files listed in ../MANIFEST.md, downloaded under their manifest names into one folder (default
../data/, which git ignores). Nothing is downloaded or stored by this script.

Run from the repo root:
    .venv/bin/python -I questions/yd-cosmic-dust-he3/spotcheck/spotcheck_he3.py [DATA_DIR] > output.txt

Items 6, 8 and 9 call the study's own functions (analysis/cosmic_dust_he3.py: stratified_window_test,
blind_peak_scan, parsers) so intervals use the same bootstrap and seeds as the study. Items 2, 3, 5, 7, 10 and 11
use the independent parsers below. Takes a few seconds.
"""
from __future__ import annotations

import csv
import hashlib
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
QDIR = HERE.parent
sys.dont_write_bytecode = True  # leave analysis/ untouched (no __pycache__)
sys.path.insert(0, str(QDIR / "analysis"))
import cosmic_dust_he3 as study  # noqa: E402

DATA = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else QDIR / "data"
WINDOWS = {"W1 13.5-11.5": (11.5, 13.5), "W2 15-10": (10.0, 15.0), "W3 20-10": (10.0, 20.0)}
MIXED_LAYER_CM = (5.0, 10.0)  # ASSUMED bioturbation mixed-layer depths; not measured at these sites
R_TERR, R_ET = 2e-8, 4e-4    # endmembers fixed in protocol.md section 2.2


def num(x):
    try:
        v = float(str(x).strip())
        return v if np.isfinite(v) else None
    except (TypeError, ValueError):
        return None


def pangaea(path):
    """Rows of a PANGAEA tab file as dicts keyed by column header (raw strings)."""
    t = path.read_text(encoding="utf-8")
    body = t[t.index("*/") + 2:].strip().splitlines()
    hdr = body[0].split("\t")
    return [dict(zip(hdr, r.split("\t"))) for r in body[1:]]


def xlsx_rows(path, sheet):
    """Rows of one xlsx sheet as {column letter: value} (stdlib only)."""
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    rid = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
    z = zipfile.ZipFile(path)
    ss = ["".join(t.text or "" for t in si.iter("{%s}t" % ns["m"]))
          for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", ns)]
    rmap = {r.attrib["Id"]: r.attrib["Target"] for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
    for sh in ET.fromstring(z.read("xl/workbook.xml")).findall(".//m:sheet", ns):
        if sh.attrib["name"] != sheet:
            continue
        tgt = rmap[sh.attrib[rid]].lstrip("/")
        tgt = tgt if tgt.startswith("xl/") else "xl/" + tgt
        out = []
        for row in ET.fromstring(z.read(tgt)).findall(".//m:sheetData/m:row", ns):
            d = {}
            for c in row.findall("m:c", ns):
                v = c.find("m:v", ns)
                if v is None or v.text is None:
                    continue
                d[re.match(r"[A-Z]+", c.attrib["r"]).group()] = ss[int(v.text)] if c.attrib.get("t") == "s" else v.text
            out.append(d)
        return out
    raise KeyError(sheet)


def section(title):
    print(f"\n== {title}")


# ---------------------------------------------------------------- 1. hashes
section("1. Data files vs MANIFEST.md SHA-256")
for line in (QDIR / "MANIFEST.md").read_text(encoding="utf-8").splitlines():
    m = re.match(r"\|\s*`([^`]+)`\s*\|.*`([0-9a-f]{64})`\s*\|\s*$", line)
    if m:
        f, want = m.groups()
        got = hashlib.sha256((DATA / f).read_bytes()).hexdigest()
        print(f"  {f:34s} {'OK' if got == want else 'MISMATCH ' + got}")

# ---------------------------------------------------------------- 2. independent Pacific parse
section("2. Independent parse of the Pacific (Pillar 1) rows vs results/pillar1_samples.csv")
mine = []          # (core, age_ka, flux pcc/cm2/kyr, depth_cm)
dropped = []
for r in pangaea(DATA / "serno2015_so202_07_6.tab"):
    he3, rat, mar = num(r["3He [10**-10 cm**3/g]"]), num(r["3He/4He [10**-4]"]), num(r["MAR [g/m**2/a]"])
    R = rat * 1e-4
    f_et = (1 - R_TERR / R) / (1 - R_TERR / R_ET)           # ET fraction, two-endmember
    mine.append(("SO202-07-6", num(r["Age [ka BP]"]), he3 * 100 * f_et * mar * 0.1, num(r["Depth sed [m]"]) * 100))

xl = DATA / "tomchovska2026_cocos_ridge.xlsx"
ages = {(int(d["N"][2:]), d["O"].strip()): num(d["P"]) for d in xlsx_rows(xl, "Table S1")
        if d.get("N", "").startswith("CR") and num(d.get("P")) is not None}       # Table S1.2 age model
thmar = {(int(d["A"]), d["B"].strip()): num(d.get("I")) for d in xlsx_rows(xl, "Table S2") if d.get("A", "").isdigit()}
for d in xlsx_rows(xl, "Table S5"):
    if not d.get("A", "").isdigit():
        continue
    k = (int(d["A"]), d["B"].strip())
    he = num(d.get("J"))                                    # [3He]ET pcc/g
    if k not in ages or thmar.get(k) is None or he is None:
        why = "no age" if k not in ages else "no Th-based MAR in Table S2" if thmar.get(k) is None else "no [3He]ET"
        dropped.append(f"CR0{k[0]} {k[1]} cm: {why}")
        continue
    lo, hi = (float(x) for x in k[1].split("-"))
    mine.append((f"CR0{k[0]}", ages[k], he * thmar[k], (lo + hi) / 2))

manop_raw = pangaea(DATA / "marcantonio2001_b18_b25.tab")
for r in manop_raw:
    a, fl = num(r["Age [ka BP]"]), num(r["3He flux [10**-12 cm**3/cm**2/ka]"])
    if a is None or fl is None:
        dropped.append(f"{r['Event']} {r['Age [ka BP]']} ka: no 3He flux value")
        continue
    mine.append((r["Event"], a, fl, num(r["Depth sed [m]"]) * 100))

theirs = sorted((r["core"], float(r["age_ka"]), float(r["flux_pcc_cm2_kyr"]))
                for r in csv.DictReader(open(QDIR / "results" / "pillar1_samples.csv")))
ms = sorted((c, a, f) for c, a, f, _ in mine)
bad = [(x, y) for x, y in zip(ms, theirs)
       if x[0] != y[0] or abs(x[1] - y[1]) > 1e-3 or abs(x[2] - y[2]) > 1e-4 * max(1, abs(x[2]))]
print(f"  rows: mine {len(ms)}, study {len(theirs)}; mismatches in core/age/flux: {len(bad) + abs(len(ms) - len(theirs))}")
print("  every 15th row (core, age ka, flux pcc cm-2 kyr-1) mine | study:")
for i in range(0, len(ms), 15):
    print(f"    {ms[i][0]:11s} {ms[i][1]:8.3f} {ms[i][2]:7.4f} | {theirs[i][1]:8.3f} {theirs[i][2]:7.4f}")

# ---------------------------------------------------------------- 3. dropped rows, duplicates
section("3. Rows the study drops, and duplicate rows")
for name in ("farley2006_odp757b.tab", "farley2006_odp926b.tab"):
    rows = pangaea(DATA / name)
    for r in rows:
        if num(r["Age [ka BP]"]) is None or num(r["3He ET flux [fmol/cm**2/ka]"]) is None:
            dropped.append(f"{name.split('_')[1].upper()} {r['Sample label']} ({r['Age [ka BP]']} ka): no 3He ET flux value")
    print(f"  {name}: {len(rows)} rows in source")
for x in dropped:
    print("  dropped:", x)
print(f"  total dropped: {len(dropped)}")
seen = {}
for r in manop_raw:
    key = tuple(r.values())
    seen[key] = seen.get(key, 0) + 1
for key, n in seen.items():
    if n > 1:
        print(f"  exact duplicate row in PANGAEA.846689, kept {n} times by the study: {' | '.join(key)}")

# ---------------------------------------------------------------- 4. samples per window
section("4. Samples per core in each window (inclusive bounds, as in the study)")
ggc = [(s.core, s.age_ka, s.flux_pcc_cm2_kyr, s.depth_cm)
       for f, c in (("middleton2018_kn207_ggc3.txt", "KN207-2-GGC3"), ("middleton2018_kn207_ggc6.txt", "KN207-2-GGC6"))
       for s in study.parse_middleton2018(DATA / f, c)]
allcores = mine + ggc
print(f"  {'core':13s} {'n':>4s} " + " ".join(f"{w:>13s}" for w in WINDOWS))
for core in sorted({c for c, *_ in allcores}):
    a = [x[1] for x in allcores if x[0] == core]
    print(f"  {core:13s} {len(a):4d} " + " ".join(f"{sum(lo <= t <= hi for t in a):13d}" for lo, hi in WINDOWS.values()))

# ---------------------------------------------------------------- 5. sedimentation rates
section(f"5. Sedimentation rate across 20-10 ka and smoothing time for ASSUMED mixed layers of {MIXED_LAYER_CM} cm")
print("  depth interpolated linearly between samples at the ends of the 10-20 ka span (or the core's own range if shorter)")
for core in sorted({c for c, *_ in allcores}):
    pts = sorted((x[1], x[3]) for x in allcores if x[0] == core)
    a, d = np.array([p[0] for p in pts]), np.array([p[1] for p in pts])
    t0, t1 = max(10.0, a.min()), min(20.0, a.max())
    rate = (np.interp(t1, a, d) - np.interp(t0, a, d)) / (t1 - t0)
    mix = "  ".join(f"{m:.0f} cm -> {m / rate:4.1f} kyr" for m in MIXED_LAYER_CM)
    print(f"  {core:13s} {t0:5.2f}-{t1:5.2f} ka  {rate:5.2f} cm/kyr   {mix}")

# ---------------------------------------------------------------- 6. YD window
section("6. 13.5-11.5 ka window: median ratio [95% bootstrap] and one-sided p, study's own function")
serno_s = study.parse_serno2015(DATA / "serno2015_so202_07_6.tab")
cocos_s = study.parse_tomchovska2026(xl)
manop_s = study.parse_marcantonio2001(DATA / "marcantonio2001_b18_b25.tab")
pool = serno_s + cocos_s + manop_s
S = study.RNG_SEED


def show(label, res):
    print(f"  {label:58s} n {res['n_target']:2d}/{res['n_baseline']:3d}  {res['median_ratio']:.3f} "
          f"[{res['boot_ci95'][0]:.3f}, {res['boot_ci95'][1]:.3f}]  p={res['p_perm_one_sided']:.3f}  cores {res['cores_used']}")


show("pooled 7 Pacific cores (study seed +10)", study.stratified_window_test(pool, 11.5, 13.5, seed=S + 10))
show("SO202-07-6 alone (study seed +20)", study.stratified_window_test(serno_s, 11.5, 13.5, seed=S + 20))
no_cocos_t = [s for s in pool if not (s.core.startswith("CR") and 11.5 <= s.age_ka <= 13.5)]
show("pooled without the 3 Cocos window samples (seed +10)", study.stratified_window_test(no_cocos_t, 11.5, 13.5, seed=S + 10))
print("  (the study's method drops cores with no sample in the window, so removing the 3 Cocos samples leaves\n"
      "   SO202-07-6 alone; MANOP has no 13.5-11.5 ka sample)")
# variant: keep the Cocos baselines in the pooled baseline (point estimate only)
t_n, b_n = [], []
for core in sorted({s.core for s in pool if s.core != "MANOP_B18" and s.core != "MANOP_B25"}):
    v = [(s.age_ka, s.flux_pcc_cm2_kyr) for s in pool if s.core == core]
    base = np.array([f for a, f in v if not 11.5 <= a <= 13.5])
    med = np.median(base)
    b_n += list(base / med)
    if core == "SO202-07-6":
        t_n += [f / med for a, f in v if 11.5 <= a <= 13.5]
print(f"  variant keeping Cocos baselines (CR01-CR05) in the pooled baseline: n {len(t_n)}/{len(b_n)}, "
      f"ratio {np.median(t_n) / np.median(b_n):.3f} (point estimate)")

# ---------------------------------------------------------------- 7. radiocarbon
section("7. SO202-07-6 radiocarbon tie points (PANGAEA.845972)")
c14 = pangaea(DATA / "serno2015_so202_07_6_ages.tab")
raw_col = next(k for k in c14[0] if k.startswith("Age dated [ka]"))
cal_col = next(k for k in c14[0] if k.startswith("Cal age [ka BP]"))
raw_in = [r for r in c14 if num(r[raw_col]) is not None and 11.5 <= num(r[raw_col]) <= 13.5]
cal = [r for r in c14 if num(r[cal_col]) is not None]
cal_in = [r for r in cal if 11.5 <= num(r[cal_col]) <= 13.5]
print(f"  rows: {len(c14)}; with a calendar age: {len(cal)}")
print(f"  raw 14C age in 11.5-13.5 (14C ka): {len(raw_in)}; their calendar ages span "
      f"{min(num(r[cal_col]) for r in raw_in if num(r[cal_col])):.2f}-{max(num(r[cal_col]) for r in raw_in if num(r[cal_col])):.2f} cal ka")
print(f"  calendar age in 11.5-13.5 cal ka: {len(cal_in)} ({', '.join(r[cal_col] for r in cal_in)})")
print("  calendar ages are the published ones (Serno et al. 2015, CALIB 7.0.4 per the PANGAEA header); not recalibrated here")

# ---------------------------------------------------------------- 8. unit factor
section("8. fmol -> pcc factor (analysis/cosmic_dust_he3.py line 371)")
src = (QDIR / "analysis" / "cosmic_dust_he3.py").read_text().splitlines()
print(f"  line 371 reads: {src[370].strip()}")
print(f"  1 fmol = 1e-15 mol x 22414 cm3/mol = {1e-15 * 22414:.4e} cm3 = {1e-15 * 22414 / 1e-12:.3f} pcc (1 pcc = 1e-12 cm3)")
odp757 = study.parse_farley2006(DATA / "farley2006_odp757b.tab", "ODP-757B", "South Indian Ocean")
fixed = [study.Sample(s.core, s.region, s.lab, s.age_ka, s.flux_pcc_cm2_kyr * 1000.0) for s in odp757]
for lab, ss in (("as coded (x0.022414)", odp757), ("corrected (x22.414)", fixed)):
    r = study.stratified_window_test(ss, 7500.0, 8350.0, base_lo=6200.0, base_hi=10500.0, seed=S + 1)
    print(f"  Veritas ODP 757B {lab:22s} ratio {r['median_ratio']:.3f}  p {r['p_perm_one_sided']:.5f}  "
          f"target median {r['target_median_raw']}")

# ---------------------------------------------------------------- 9. blind top-18
section("9. Blind top-10% scan (study's function)")
scan = study.blind_peak_scan(pool)
top = scan["top_samples"]
per = {}
for x in top:
    per[x["core"]] = per.get(x["core"], 0) + 1
print(f"  top {len(top)} of {scan['n_total']}, threshold {scan['threshold_norm_flux']}x core median; per core: {per}")
print(f"  older than 60 ka: {sum(x['age_ka'] > 60 for x in top)} (all MANOP); in the pool overall: "
      f"{sum(s.age_ka > 60 for s in pool)} of {len(pool)}")
print(f"  inside 10-20 ka (the union of the three windows): {sum(10 <= x['age_ka'] <= 20 for x in top)}; "
      f"older than 20 ka, so outside every window by age: {sum(x['age_ka'] > 20 for x in top)}")

# ---------------------------------------------------------------- 10. medians vs ice
section("10. Pacific core median flux vs Brook et al. (2000) ice")
meds = {c: np.median([f for cc, a, f in ms if cc == c]) for c in sorted({c for c, _, _ in ms})}
for c, m in meds.items():
    print(f"  {c:11s} {m:.3f} pcc cm-2 kyr-1")
print(f"  spread of core medians: {min(meds.values()):.3f}-{max(meds.values()):.3f} = {max(meds.values()) / min(meds.values()):.2f}x")
ice = []
for line in (DATA / "brook2000_ice_helium.txt").read_text(encoding="latin-1").splitlines()[44:]:
    p = line.split("\t")
    if len(p) >= 8 and num(p[1]) is not None and num(p[7].split("±")[0]) is not None:
        ice.append((num(p[1]), num(p[7].split("±")[0])))
iv = [f for _, f in ice]
print(f"  Brook file: {len(ice)} flux rows (replicates counted separately), median {np.median(iv):.2f}, "
      f"range {min(iv):.2f}-{max(iv):.2f}; rows between 4 and 75 ka: {sum(4 < a < 75 for a, _ in ice)}")
print("  Brook et al. 2000 abstract: late Holocene GISP2 0.62 +/- 0.27, Vostok 0.77 +/- 0.25 (x1e-12 cm3 STP cm-2 ka-1)")
print("  Cocos Ridge source, Table S7 (He- vs Th-derived MAR, core-level two-sided p):")
for d in xlsx_rows(xl, "Table S7")[3:7]:
    print(f"    CR0{d.get('A')}: n {d.get('B')}, z {d.get('C')}, p {d.get('D')}")

# ---------------------------------------------------------------- 11. Late Eocene
section("11. Late Eocene, ODP 757B (corrected units, pcc cm-2 kyr-1)")
eo = [(num(r["Age [ka BP]"]) / 1000, num(r["3He ET flux [fmol/cm**2/ka]"]) * 22.414)
      for r in pangaea(DATA / "farley2006_odp757b.tab") if num(r["3He ET flux [fmol/cm**2/ka]"]) is not None]


def win(*spans):
    return [f for a, f in eo if any(lo <= a <= hi for lo, hi in spans)]


for label, spans in (("locked target 34.5-36.5 Ma", [(34.5, 36.5)]), ("locked baseline 25.0-33.5 Ma", [(25.0, 33.5)]),
                     ("  of which 25.0-30.5 Ma", [(25.0, 30.5)]), ("  of which 30.5-33.5 Ma", [(30.5, 33.5)]),
                     ("post-hoc peak 35.3-36.1 Ma", [(35.3, 36.1)]),
                     ("post-hoc brackets 30.5-34.5 + 36.2-38.5 Ma", [(30.5, 34.5), (36.2, 38.5)])):
    v = win(*spans)
    print(f"  {label:44s} n {len(v):2d}  median {np.median(v):.3f}  max {max(v):.3f}")
pk, br = win((35.3, 36.1)), win((30.5, 34.5), (36.2, 38.5))
print(f"  post-hoc ratio {np.median(pk) / np.median(br):.2f}x (windows chosen after seeing the data); "
      f"single highest sample / bracket median = {max(pk) / np.median(br):.1f}x")
print(f"  locked ratio (simple medians) {np.median(win((34.5, 36.5))) / np.median(win((25.0, 33.5))):.3f}x")
pc = [(float(r["age_Ma"]), float(r["flux_pcc_cm2_kyr"])) for r in csv.DictReader(open(QDIR / "results" / "positive_controls.csv"))
      if r["core"] == "ODP-757B"]
pk_r = [f for a, f in pc if 35.3 <= a <= 36.1]
br_r = [f for a, f in pc if 30.5 <= a <= 34.5 or 36.2 <= a <= 38.5]
print(f"  same windows on results/positive_controls.csv (5 decimals, 1000x too small): "
      f"{np.median(pk_r):.5f} / {np.median(br_r):.5f} = {np.median(pk_r) / np.median(br_r):.2f}x "
      f"(the study's 4.00x; rounding, magnified by the unit factor)")
