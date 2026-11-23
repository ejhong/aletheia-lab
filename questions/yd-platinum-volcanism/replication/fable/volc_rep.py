#!/usr/bin/env python3
"""Independent re-derivation of the tie-point ages and Part 2 of questions/yd-platinum-volcanism, written from
protocol.md alone by Claude Fable 5.2 without using analysis/ptvolc.py. Needs xlrd==2.0.1 for the .xls tables.

    python -I volc_rep.py "<Supplementary tables.xls>" "<Bipolar supplementary tables.xlsx>" <events.tsv>
"""
import csv
import io
import json
import math
import random
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

import xlrd

XLS, XLSX, EV = sys.argv[1:4]
wb = xlrd.open_workbook(XLS)
num = lambda v: float(v) if isinstance(v, (int, float)) and not (isinstance(v, float) and math.isnan(v)) else None
out = {}

# ---- Table S2 of Svensson et al. 2020: GISP2 depth against GICC05 age
ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
z = zipfile.ZipFile(XLSX)
names = [s.attrib["name"] for s in ET.fromstring(z.read("xl/workbook.xml")).findall(".//m:sheet", ns)]
strings = ["".join(t.text or "" for t in si.findall(".//m:t", ns)) for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall(".//m:si", ns)]
sheet = ET.fromstring(z.read("xl/worksheets/sheet%d.xml" % (names.index("Table S2") + 1)))
rows = []
for r in sheet.findall(".//m:row", ns):
    cells = {}
    for c in r.findall("m:c", ns):
        v = c.find("m:v", ns)
        if v is None:
            continue
        col = re.match(r"[A-Z]+", c.attrib["r"]).group(0)
        cells[col] = strings[int(v.text)] if c.attrib.get("t") == "s" else v.text
    rows.append(cells)
head = next(r for r in rows if any("GISP2" in str(v) for v in r.values()))
gcol = next(k for k, v in head.items() if "GISP2" in str(v))
acol = next(k for k, v in head.items() if "GICC05" in str(v))
out["s2_header"] = {gcol: head[gcol], acol: head[acol]}
ties = []
for r in rows:
    try:
        ties.append((float(r[gcol]), float(r[acol])))
    except (KeyError, ValueError):
        pass
ties.sort()
out["ties"] = len(ties)
for name, d in (("onset", 1712.375), ("peak", 1712.1875), ("end", 1712.0)):
    for (d0, a0), (d1, a1) in zip(ties, ties[1:]):
        if d0 <= d <= d1:
            age = a0 + (a1 - a0) * (d - d0) / (d1 - d0)
            out["pt_" + name] = {"age_b2k": round(age, 1), "years_after_onset": round(12896 - age, 1), "between": [d0, round(a0, 1), d1, round(a1, 1)]}

# ---- Lin et al. 2022, Tables S3 (Greenland) and S5 (bipolar)
s3, s5 = wb.sheet_by_name("Table S3"), wb.sheet_by_name("Table S5")
out["s3_cols"] = {i: str(s3.cell_value(1, i))[:40] or str(s3.cell_value(0, i))[:40] for i in (12, 13)}
out["s5_cols"] = {i: str(s5.cell_value(1, i))[:50] or str(s5.cell_value(0, i))[:50] for i in (1, 26)}
gl = [(num(s3.cell_value(r, 12)), num(s3.cell_value(r, 13))) for r in range(2, s3.nrows)]
gl = [(a, d) for a, d in gl if a is not None and d is not None]
bi = [(num(s5.cell_value(r, 1)), num(s5.cell_value(r, 26))) for r in range(2, s5.nrows)]
bi = [(a, d) for a, d in bi if a is not None and d is not None]
out["n_gl"], out["n_bi"] = len(gl), len(bi)


def windows(evs, gap=None, width=150, start=12896):
    res = {}
    k = math.ceil((9296 - start) / width)
    while start + width * (k + 1) <= 59996:
        lo, hi = start + width * k, start + width * (k + 1)
        if lo >= 9296 and not (gap and lo < gap[1] and hi > gap[0]):
            inside = [d for a, d in evs if lo <= a < hi]
            res[k] = (sum(inside), len(inside), lo)
        k += 1
    return res


for name, evs, gap in (("VOLC_GL", gl, None), ("VOLC_BI", bi, (16500, 24500))):
    w = windows(evs, gap)
    v = w[0][0]
    vals = sorted(x[0] for x in w.values())
    out[name] = {"value": round(v, 1), "count": w[0][1], "rank": 1 + sum(x[0] > v for x in w.values()), "n": len(w),
                 "top5_cut": max(1, len(w) // 20), "median": round(vals[len(vals) // 2], 1),
                 "count_rank": 1 + sum(x[1] > w[0][1] for x in w.values()),
                 "zero_windows": sum(x[0] == 0 for x in w.values())}
    # a check the protocol did not ask for: the same rank among windows of the deglaciation and Holocene only
    near = {k: x for k, x in w.items() if x[2] < 16500}
    out[name]["rank_among_windows_younger_than_16500"] = [1 + sum(x[0] > v for x in near.values()), len(near)]
    out[name]["eruptions_per_1000yr"] = {"9.3-16.5 ka": round(sum(1 for a, _ in evs if a < 16500) / 7.2, 1),
                                         "24.5-60 ka": round(sum(1 for a, _ in evs if a >= 24500) / 35.5, 1)}

# ---- 2B: sulphate before the 19 coolings, against random times
events = [(r["event"], float(r["age_b2k"]), r["kind"], r["definition_uncertainty"]) for r in csv.DictReader(open(EV), delimiter="\t")]
cool = [t for n, t, k, u in events if k == "stadial onset" and u in ("4yr", "a", "b") and 10500 <= t <= 59500
        and not any(t - 200 < x < t + 100 for m, x, _, _ in events if m != n)]
out["coolings"] = len(cool)
dep = lambda t, w: sum(d for a, d in gl if t <= a < t + w)
rng = random.Random(76)
for w in (50, 150):
    for label, ts in (("all", cool), ("non_yd", [t for t in cool if t != 12896])):
        obs = sum(dep(t, w) for t in ts) / len(ts)
        null = [sum(dep(rng.uniform(10500, 59500), w) for _ in ts) / len(ts) for _ in range(10000)]
        out[f"mc_{label}_{w}"] = {"obs": round(obs, 1), "null_mean": round(sum(null) / len(null), 1), "p": round((1 + sum(x >= obs for x in null)) / 10001, 3)}
print(json.dumps(out, indent=1))
