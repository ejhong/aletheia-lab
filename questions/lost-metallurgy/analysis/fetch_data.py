#!/usr/bin/env python3
"""Reproducible downloader & manifest verifier for #82 (lost-metallurgy)."""
from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DATASETS = [
    {
        "id": "recap_8kyr",
        "file": "recap_8kyr.csv",
        "archive": "RECAP Ice Core (East Greenland)",
        "citation": "McConnell et al. (2024), NSF Arctic Data Center, doi:10.18739/A2N87320M",
        "licence": "CC-BY-4.0 (NSF Arctic Data Center)",
        "url": "https://cn.dataone.org/cn/v2/resolve/urn:uuid:8cbe22e6-4c40-48a4-a4df-f82e8bcdb210",
    },
    {
        "id": "gisp2_do10_12",
        "file": "gisp2_do10_12.csv",
        "archive": "GISP2 Ice Core (Central Greenland, DO 10-12)",
        "citation": "McConnell et al. (2020), NSF Arctic Data Center, doi:10.18739/A2445HD27",
        "licence": "CC-BY-4.0 (NSF Arctic Data Center)",
        "url": "https://cn.dataone.org/cn/v2/resolve/urn:uuid:e05cc6cb-2dd4-4867-b0c1-e9ae137da721",
    },
    {
        "id": "edc_217kyr_pb_ba",
        "file": "edc_217kyr_pb_ba.txt",
        "archive": "EPICA Dome C Ice Core (East Antarctica, 217 kyr)",
        "citation": "Vallelonga et al. (2010), NOAA/WDS Paleoclimatology Study 10033",
        "licence": "Public domain (NOAA NCEI WDS)",
        "url": "https://www.ncei.noaa.gov/pub/data/paleo/icecore/antarctica/epica_domec/edc2010pb-ba.txt",
    },
    {
        "id": "ddg_alps_age",
        "file": "ddg_alps_age.txt",
        "archive": "Dome du Goûter Ice Core (French Alps) — Age Model",
        "citation": "Legrand & McConnell (2024), NOAA/WDS Paleoclimatology Study 80979",
        "licence": "Public domain (NOAA NCEI WDS)",
        "url": "https://www.ncei.noaa.gov/pub/data/paleo/icecore/europe/legrand2024/legrand2024-id1_1-age.txt",
    },
    {
        "id": "ddg_alps_lead",
        "file": "ddg_alps_lead.txt",
        "archive": "Dome du Goûter Ice Core (French Alps) — Lead",
        "citation": "Legrand & McConnell (2024), NOAA/WDS Paleoclimatology Study 80979",
        "licence": "Public domain (NOAA NCEI WDS)",
        "url": "https://www.ncei.noaa.gov/pub/data/paleo/icecore/europe/legrand2024/legrand2024-id3_1-lead.txt",
    },
    {
        "id": "ddg_alps_chem",
        "file": "ddg_alps_chem.txt",
        "archive": "Dome du Goûter Ice Core (French Alps) — Chemistry & Dust",
        "citation": "Legrand & McConnell (2024), NOAA/WDS Paleoclimatology Study 80979",
        "licence": "Public domain (NOAA NCEI WDS)",
        "url": "https://www.ncei.noaa.gov/pub/data/paleo/icecore/europe/legrand2024/legrand2024-id2-avg-chem.txt",
    },
    {
        "id": "furamoos_xrf",
        "file": "furamoos_xrf_929755.tab",
        "archive": "Füramoos Peat Bog (S. Germany, 14.3 kyr XRF Pb EF)",
        "citation": "Kern et al. (2021), Anthropocene 36:100310, doi:10.1594/PANGAEA.929755",
        "licence": "CC-BY-4.0 (PANGAEA)",
        "url": "https://doi.pangaea.de/10.1594/PANGAEA.929755?format=textfile",
    },
    {
        "id": "furamoos_icpms",
        "file": "furamoos_icpms_929751.tab",
        "archive": "Füramoos Peat Bog (S. Germany, ICP-MS Pb & Isotopes)",
        "citation": "Kern et al. (2021), Anthropocene 36:100310, doi:10.1594/PANGAEA.929751",
        "licence": "CC-BY-4.0 (PANGAEA)",
        "url": "https://doi.pangaea.de/10.1594/PANGAEA.929751?format=textfile",
    },
    {
        "id": "store_mosse_peat",
        "file": "kylander_peat_903892.tab",
        "archive": "Store Mosse Peat Bog (S. Sweden, 6.4 kyr Pb/Cu/Zn/Ti)",
        "citation": "Kylander et al. (2019), doi:10.1594/PANGAEA.903892",
        "licence": "CC-BY-4.0 (PANGAEA)",
        "url": "https://doi.pangaea.de/10.1594/PANGAEA.903892?format=textfile",
    },
]


def main():
    meta = []
    for ds in DATASETS:
        p = DATA_DIR / ds["file"]
        if not p.exists():
            req = urllib.request.Request(ds["url"], headers={"User-Agent": "aletheia-lab/1.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                p.write_bytes(r.read())
        b = p.read_bytes()
        sha = hashlib.sha256(b).hexdigest()
        meta.append({**ds, "bytes": len(b), "sha256": sha})
        print(f"OK {ds['file']:28s} {len(b):10,d} B  sha256={sha}")
    (DATA_DIR / "manifest_meta.json").write_text(json.dumps(meta, indent=2))

    # Write MANIFEST.md
    lines = [
        "# Data Manifest — Pre-Bronze-Age Metallurgy Side-Channel (#82)",
        "",
        "Retrieved: 2026-11-24. All raw files live in gitignored `data/` and are re-downloadable via `python3 questions/lost-metallurgy/analysis/fetch_data.py`.",
        "",
        "| File | Archive | Citation | Licence | Bytes | URL | SHA-256 |",
        "|---|---|---|---|---:|---|---|",
    ]
    for r in meta:
        lines.append(
            f"| `{r['file']}` | {r['archive']} | {r['citation']} | {r['licence']} | {r['bytes']:,} | {r['url']} | `{r['sha256']}` |"
        )
    (BASE_DIR / "MANIFEST.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("Wrote MANIFEST.md")


if __name__ == "__main__":
    main()
