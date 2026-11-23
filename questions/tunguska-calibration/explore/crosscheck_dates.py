#!/usr/bin/env python3
"""Do the dates in data/standard/*.tsv agree with a second, independently written reader (explore/structure.py)?

Compares the number of samples dated in each calendar year from 1880 to 1935, core by core. Dates only: no
chemistry is read. Run from questions/tunguska-calibration:  .venv/bin/python -I explore/crosscheck_dates.py
"""
import collections
import importlib.util
import math
import os
import sys

sys.path.insert(0, "analysis")
import tunguska as t

spec = importlib.util.spec_from_file_location("structure", "explore/structure.py")
st = importlib.util.module_from_spec(spec)
spec.loader.exec_module(st)
reg = {f[0]: f for f in st.FILES}
bad = 0
for core, (site, rel, fmt, age, colmap) in t.CORES.items():
    if rel not in reg:
        print(core, "not in the second reader's list")
        bad += 1
        continue
    _, fmt2, agespec = reg[rel]
    path = os.path.join(st.DATA, rel)
    if fmt2 == "pangaea":
        _, cols, rows = st.read_pangaea(path)
    elif fmt2.startswith("csv"):
        _, cols, rows = st.read_csv(path)
    elif fmt2 == "xlsx":
        name, sheet = next(st.xlsx_sheets(path))
        cols, rows = [str(c).strip() for c in sheet[0]], sheet[1:]
    else:
        _, cols, rows = st.read_noaa(path, fmt2)
    ages = st.ages_for(rows, cols, agespec, lambda r: os.path.join(st.DATA, r))
    theirs = collections.Counter(math.floor(a) for a in ages if a is not None)
    mine = collections.Counter(math.floor(y) for y in t.load(core)[:, 0])
    diff = {y: (mine[y], theirs[y]) for y in range(1880, 1936) if mine[y] != theirs[y]}
    print(f"{core:11s} years 1880-1935 that differ: {len(diff)}", dict(list(diff.items())[:4]) if diff else "")
    bad += bool(diff)
print("all agree" if not bad else f"{bad} cores differ")
