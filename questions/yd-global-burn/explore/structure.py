#!/usr/bin/env python3
"""Strictly blind exploratory inspection of dataset structures, coverage, and resolution.

Excludes ALL target-window values inside [12000, 13600] cal BP so no outcome is seen before locking.
Run from questions/yd-global-burn/.
"""
import csv
import pathlib
import subprocess
import numpy as np

DATA = pathlib.Path("data/noaa")
GCD_DIR = pathlib.Path("data/gcd_csv")
GCD_DIR.mkdir(parents=True, exist_ok=True)
MDB = DATA / "GCD3_PUBLIC_VERSION_2013_01-Oct-2013.mdb"

# 1. Export key GCD3 tables once (pure data export via mdb-export)
TABLES = ["SITE", "REGION", "SAMPLE", "CHARCOAL", "CHARCOAL_UNITS", "DATE_INFO", "METHOD", "DEPO_CONTEXT"]
for t in TABLES:
    out = GCD_DIR / f"{t}.csv"
    if not out.exists():
        with open(out, "wb") as f:
            subprocess.run(["mdb-export", str(MDB), t], stdout=f, check=True)

print("=== GCD3 table columns & row counts ===")
for t in TABLES:
    with open(GCD_DIR / f"{t}.csv", encoding="utf-8", errors="replace") as f:
        r = csv.reader(f)
        hdr = next(r)
        n = sum(1 for _ in r)
    print(f"  {t:16s}: {n:7d} rows | cols: {', '.join(hdr[:12])}" + (" ..." if len(hdr) > 12 else ""))

# 2. Blind inspection of Antarctic ice-core sampling spacing and spans (NO values in [12000, 13600])
print("\n=== Antarctic ice cores: sampling spacing & ranges (values masked in 12000-13600) ===")
def inspect_ice(fn, age_col, val_cols, delim="\t", skip_bom_header=False):
    lines = (DATA / fn).read_text(encoding="utf-8-sig", errors="replace").splitlines()
    non_c = [l for l in lines if l.strip() and not l.startswith("#")]
    hdr = non_c[0].split(delim)
    ages = []
    out_vals = {c: [] for c in val_cols}
    for l in non_c[1:]:
        p = l.split(delim)
        if len(p) <= max([age_col] + val_cols):
            continue
        try:
            a = float(p[age_col])
        except ValueError:
            continue
        ages.append(a)
        if not (12000 <= a <= 13600):
            for c in val_cols:
                try:
                    v = float(p[c])
                    if not np.isnan(v) and abs(v) < 9999:
                        out_vals[c].append(v)
                except ValueError:
                    pass
    ages = np.sort(np.array(ages))
    diffs = np.diff(ages)
    in_deglac = ages[(ages >= 10000) & (ages <= 22000)]
    d_deg = np.diff(in_deglac) if len(in_deglac) > 1 else np.array([np.nan])
    n_target_band = int(((ages >= 12500) & (ages <= 13300)).sum())
    print(f"  {fn}: N={len(ages)}, range=[{ages.min():.0f}, {ages.max():.0f}] BP, "
          f"median dt={np.median(diffs):.1f} yr (10-22k median dt={np.median(d_deg):.1f} yr, p90={np.percentile(d_deg, 90):.1f}), "
          f"n_samples_in_12500_13300={n_target_band}")
    for c in val_cols:
        arr = np.array(out_vals[c])
        print(f"    col {c} ({hdr[c] if c < len(hdr) else c}): outside-window n={len(arr)}, median={np.median(arr):.3f}, sd={np.std(arr):.3f}")

inspect_ice("taylor2016d13co2.txt", 1, [2, 3])
inspect_ice("taylor2018d13co2.txt", 1, [2, 4])
inspect_ice("antarctica2015co2wais-noaa.txt", 1, [2])
inspect_ice("eggleston2016d13co2-noaa.txt", 0, [1])

# 3. Blind inspection of GCD3 site coverage across [10000, 15000] cal BP (NO charcoal values read!)
print("\n=== GCD3 site coverage across 10,000 - 15,000 cal BP (charcoal values NOT read) ===")
sites = {}
with open(GCD_DIR / "SITE.csv", encoding="utf-8", errors="replace") as f:
    for row in csv.DictReader(f):
        sites[row["ID_SITE"]] = row

regions = {}
with open(GCD_DIR / "REGION.csv", encoding="utf-8", errors="replace") as f:
    for row in csv.DictReader(f):
        regions[row["ID_REGION"]] = row.get("REGION_NAME", row.get("REGION", ""))

# Count dating points per site in [9500, 15500]
dates_by_site = {}
with open(GCD_DIR / "DATE_INFO.csv", encoding="utf-8", errors="replace") as f:
    for row in csv.DictReader(f):
        sid = row.get("ID_SITE")
        if not sid:
            continue
        dates_by_site.setdefault(sid, []).append(row)

# Sample ages per site (strictly reading ONLY ID_SITE, EST_AGE from SAMPLE; never reading CHARCOAL values!)
sample_ages = {}
with open(GCD_DIR / "SAMPLE.csv", encoding="utf-8", errors="replace") as f:
    for row in csv.DictReader(f):
        sid = row.get("ID_SITE")
        age_s = row.get("EST_AGE", "")
        if sid and age_s:
            try:
                a = float(age_s)
                if 9000 <= a <= 16000:
                    sample_ages.setdefault(sid, []).append(a)
            except ValueError:
                pass

# Check how many sites have charcoal rows at all (just presence boolean, no values!)
has_charcoal_sample = set()
with open(GCD_DIR / "CHARCOAL.csv", encoding="utf-8", errors="replace") as f:
    for row in csv.DictReader(f):
        if row.get("QUANTITY", "") != "":
            has_charcoal_sample.add(row["ID_SAMPLE"])

# Re-read SAMPLE restricted to samples that have charcoal quantity
char_ages = {}
with open(GCD_DIR / "SAMPLE.csv", encoding="utf-8", errors="replace") as f:
    for row in csv.DictReader(f):
        if row.get("ID_SAMPLE") not in has_charcoal_sample:
            continue
        sid = row.get("ID_SITE")
        age_s = row.get("EST_AGE", "")
        if sid and age_s:
            try:
                a = float(age_s)
                char_ages.setdefault(sid, []).append(a)
            except ValueError:
                pass

# Summarize sites spanning [10500, 14500] and [10000, 15000] with various resolution cutoffs
for span_lo, span_hi in [(10500, 14500), (10000, 15000)]:
    covering = []
    for sid, ages in char_ages.items():
        arr = np.sort(np.array(ages))
        in_span = arr[(arr >= span_lo) & (arr <= span_hi)]
        if len(in_span) >= 5 and arr.min() <= span_lo + 200 and arr.max() >= span_hi - 200:
            med_dt = float(np.median(np.diff(in_span)))
            # count samples in 12000..13500 just for coverage check
            n_mid = int(((in_span >= 12000) & (in_span <= 13500)).sum())
            covering.append((sid, len(in_span), med_dt, n_mid))
    print(f"  Sites covering [{span_lo}, {span_hi}]: total={len(covering)}, "
          f"med_dt<=150yr: {sum(1 for _, _, d, _ in covering if d <= 150)}, "
          f"med_dt<=100yr: {sum(1 for _, _, d, _ in covering if d <= 100)}, "
          f"med_dt<=50yr: {sum(1 for _, _, d, _ in covering if d <= 50)}")
    if (span_lo, span_hi) == (10500, 14500):
        # Regional breakdown for med_dt <= 100 yr and all covering
        for tag, sub in [("all covering", covering), ("med_dt<=100yr", [x for x in covering if x[2] <= 100]),
                         ("med_dt<=50yr", [x for x in covering if x[2] <= 50])]:
            by_reg = {}
            for sid, _, _, _ in sub:
                st = sites.get(sid, {})
                lat = float(st["LAT"]) if st.get("LAT") else np.nan
                lon = float(st["LONG"]) if st.get("LONG") else np.nan
                if np.isnan(lat):
                    reg = "unknown"
                elif lat > 15 and -170 <= lon <= -50:
                    reg = "North America"
                elif lat > 35 and -15 <= lon <= 60:
                    reg = "Europe"
                elif lat <= 15 and -90 <= lon <= -30:
                    reg = "South/Central America"
                elif lat < -10 and lon >= 100:
                    reg = "Australasia"
                else:
                    reg = "Asia/Africa/Other"
                by_reg[reg] = by_reg.get(reg, 0) + 1
            print(f"    {tag} ({len(sub)}): {dict(sorted(by_reg.items(), key=lambda x: -x[1]))}")
