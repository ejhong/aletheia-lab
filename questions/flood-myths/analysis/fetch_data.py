#!/usr/bin/env python3
"""Reproducible downloader & manifest generator for #44 (flood-myths)."""
from __future__ import annotations

import hashlib
import urllib.request
import zipfile
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

SOURCES = [
    {
        "file": "Replication_Data_Folklore.zip",
        "name": "Berezkin Folklore & Mythology Catalog (Michalopoulos & Xue 2021 QJE Replication Package)",
        "citation": "Michalopoulos & Xue (2021), QJE 136(4):1993-2046; Harvard Dataverse doi:10.7910/DVN/IXOHKB (958 groups, 2,564 Berezkin motifs)",
        "licence": "CC0 / Academic Replication Archive (Harvard Dataverse)",
        "url": "https://dataverse.harvard.edu/api/access/datafile/5149043",
    },
    {
        "file": "ETOPO_2022_v1_60s_N90W180_bed.nc",
        "name": "ETOPO 2022 60-arc-second Global Bedrock Relief Model (NetCDF4)",
        "citation": "NOAA National Centers for Environmental Information (2022), doi:10.25921/fd45-gt74",
        "licence": "Public domain (U.S. Government / NOAA NCEI)",
        "url": "https://www.ngdc.noaa.gov/thredds/fileServer/global/ETOPO2022/60s/60s_bed_elev_netcdf/ETOPO_2022_v1_60s_N90W180_bed.nc",
    },
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    lines = [
        "# Data Manifest — Do Flood Myths Cluster Where Land Drowned? (#44)",
        "",
        "Retrieved: 2026-11-24. Raw archives live in gitignored `data/` and are re-downloadable via `python3 questions/flood-myths/analysis/fetch_data.py`.",
        "",
        "| File | Dataset | Citation | Licence | Bytes | URL | SHA-256 |",
        "|---|---|---|---|---:|---|---|",
    ]
    for s in SOURCES:
        p = DATA_DIR / s["file"]
        if not p.exists():
            req = urllib.request.Request(s["url"], headers={"User-Agent": "aletheia-lab/1.0"})
            with urllib.request.urlopen(req, timeout=180) as r, open(p, "wb") as out:
                while True:
                    buf = r.read(1 << 20)
                    if not buf:
                        break
                    out.write(buf)
        sha = sha256_file(p)
        sz = p.stat().st_size
        print(f"OK {s['file']:36s} {sz:12,d} B  sha256={sha}")
        lines.append(f"| `{s['file']}` | {s['name']} | {s['citation']} | {s['licence']} | {sz:,} | {s['url']} | `{sha}` |")

    # Ensure extracted .dta files are present
    zf = zipfile.ZipFile(DATA_DIR / "Replication_Data_Folklore.zip")
    for member in [
        "Replication_Data_Folklore/Original_Files/Motif_Master.dta",
        "Replication_Data_Folklore/Original_Files/Motifs_Berezkin_groups.dta",
        "Replication_Data_Folklore/Replication_Tables_Figures/Berezkin_groups_Regressions_Ready.dta",
    ]:
        out = DATA_DIR / Path(member).name
        if not out.exists():
            out.write_bytes(zf.read(member))

    (BASE_DIR / "MANIFEST.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("Wrote MANIFEST.md")


if __name__ == "__main__":
    main()
