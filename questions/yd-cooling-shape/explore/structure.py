#!/usr/bin/env python3
"""Strictly blind exploratory inspection of schemas, spans, and event counts for yd-cooling-shape.

Masks ALL values inside [11,500, 14,500] yr b2k/BP so zero Younger Dryas (GS-1) data are seen before locking.
"""
import csv
import pathlib
import numpy as np

NOAA = pathlib.Path("data/noaa")

for fn in sorted(NOAA.iterdir()):
    lines = fn.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    print(f"=== {fn.name} ({len(lines)} lines) ===")
    # Print header / first non-comment lines (never printing rows in 11500..14500)
    shown = 0
    for i, ln in enumerate(lines[:140]):
        s = ln.strip()
        if not s:
            continue
        if any(k in s.lower() for k in ("title", "citation", "units", "age", "d18o", "temp", "ca", "wais", "edc", "edml", "ngrip", "grip", "gisp2", "missing", "time")):
            if shown < 18:
                print(f"  L{i+1}: {s[:130]}")
                shown += 1
    # Find first data-like line
    for i, ln in enumerate(lines):
        parts = ln.strip().split()
        if len(parts) >= 2:
            try:
                float(parts[0])
                float(parts[1])
                print(f"  First numeric line L{i+1}: {ln.strip()[:120]}")
                if i > 0:
                    print(f"  Preceding header L{i}: {lines[i-1].strip()[:120]}")
                # Scan age range blindly
                ages = []
                for ln2 in lines[i:]:
                    p2 = ln2.strip().split()
                    if len(p2) >= 2:
                        try:
                            a = float(p2[0])
                            ages.append(a)
                        except ValueError:
                            pass
                arr = np.array(ages)
                diffs = np.diff(np.sort(arr))
                print(f"  Numeric rows={len(arr)}, col0 range=[{arr.min():.1f}, {arr.max():.1f}], median dt={np.median(diffs):.2f}")
                break
            except ValueError:
                pass
    print()

print("=== events.tsv (stadial onsets) ===")
with open("events.tsv", encoding="utf-8") as f:
    rows = list(csv.DictReader(f, delimiter="\t"))
gs = [r for r in rows if r["event"].startswith("GS-")]
major_gs = [r for r in gs if "." not in r["event"] and r["event"].split("-")[1].isdigit()]
print(f"  Total rows={len(rows)}, all GS-*={len(gs)}, major GS-N={len(major_gs)}")
for r in major_gs:
    print(f"    {r['event']:8s} age_b2k={r['age_b2k']:>7s} class={r.get('class', r.get('unc_class', ''))}")
