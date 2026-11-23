#!/usr/bin/env python3
"""Strictly blind exploratory inspection of Study 2 (yd-platinum-volcanism) datasets.

Inspects ONLY headers, zip contents, column names, row counts, and non-target spans;
NEVER prints values inside GISP2 depth [1705, 1720] m or age [12,600, 13,200] b2k.
"""
import pathlib
import zipfile
import xml.etree.ElementTree as ET

DATA = pathlib.Path("data")

for z in sorted((DATA / "copernicus").glob("*.zip")):
    print(f"=== ZIP: {z.name} ({z.stat().st_size:,} bytes) ===")
    with zipfile.ZipFile(z) as zf:
        for info in zf.infolist():
            print(f"  {info.filename} ({info.file_size:,} bytes)")

for f in sorted((DATA / "noaa").iterdir()) + sorted((DATA / "pangaea").iterdir()):
    lines = f.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    print(f"\n=== {f.relative_to(DATA)} ({len(lines)} lines) ===")
    for i, ln in enumerate(lines[:60]):
        s = ln.strip()
        if s and any(k in s.lower() for k in ("col", "depth", "age", "d18o", "so4", "ca", "na", "nh4", "gisp2", "ngrip", "grip", "title", "citation", "missing", "sulf", "ssi")):
            print(f"  L{i+1}: {s[:130]}")
    # Show first 3 numeric lines (guaranteed outside 1705..1720 m / 12600..13200 b2k)
    shown = 0
    for i, ln in enumerate(lines):
        p = ln.strip().split()
        if len(p) >= 2:
            try:
                v0 = float(p[0])
                float(p[1])
                if not (1700 <= v0 <= 1725) and not (12500 <= v0 <= 13300):
                    if shown == 0 and i > 0:
                        print(f"  Hdr L{i}: {lines[i-1].strip()[:130]}")
                    print(f"  Row L{i+1}: {ln.strip()[:130]}")
                    shown += 1
                    if shown >= 2:
                        break
            except ValueError:
                pass
