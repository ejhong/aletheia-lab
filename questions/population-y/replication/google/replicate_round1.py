```python
#!/usr/bin/env python3
"""
Independent replication of the Population Y ("Ypykuéra") analysis protocol.

Usage:
    python replicate.py OUTDIR [--amended]

Run from questions/population-y/. Writes sets.tsv, f4.tsv, and composites.tsv
into OUTDIR.

Protocol ambiguities and choices made:
1. ONG and JAR Pass filter: The protocol defines ONG and JAR as "everyone
   labelled ONG and JAR (Mondal et al. 2016)" without adding "with a Pass"
   (unlike Panel A, Panel B, World panel W, Ancient Americans, and VER). We
   match exact .ind group labels "ONG" and "JAR" without adding an unstated
   ASSESSMENT filter.
2. World panel W deduplication scope: Eligible rows (date 0, outside Americas,
   Shotgun.diploid or Shotgun, >= 900,000 SNPs, Pass, label not excluded) are
   deduplicated globally by Individual ID (preferring S_/B_*.DG, then highest
   SNP count, then earlier .ind line) before applying the >= 2 people per
   label rule, ensuring no person is counted in multiple W.* sets. If
   Individual ID is missing (".."), Genetic ID is used as a fallback person ID.
3. Panel A and Panel B set list: Only the sets listed in the protocol's Panel A
   and Panel B tables are constructed (so no empty A.Nasioi, B.Australian,
   B.Mixe, or B.Quechua sets).
4. Block-size support test (P_A with 10 cM blocks): Reported in f4.tsv with
   mask="10cM" so it does not collide with the standard 5 cM P_A (mask="-").
5. Section R "each other American group": In Panel A we compute f4(A.Mbuti,
   A.Papuan; A.Mixe, X) for A.Mayan, A.Piapoco, A.Quechua as well as the
   alternate references A.Pima and A.MesoOther; in Panel B for B.Mayan and
   B.Piapoco.
6. Section N transversion M1: The protocol states "M1 = f4(A.Mbuti, A.Papuan;
   B, G_t), and the same with ONG in place of A.Papuan, and on transversions".
   We compute transversions for both A.Papuan and ONG to cover both readings.
7. Section A per-individual admixture diagnostic: Included in f4.tsv using the
   documented derived set names (<panel>.ind.<gid> and <set>-<gid>) for all
   present-day American individuals in each panel; P.unflagged (if any donor
   is flagged) is printed to stdout rather than written with an undocumented
   set name to f4.tsv.
8. Section A group-level admixture: Always computed strictly per the LOCKED
   protocol (using h(S) = f4(Chimp, Mbuti; Amazon, S)), even when --amended is
   passed, as instructed. Its 9 component f4 statistics on the common mask are
   also written to f4.tsv (with mask="admix_A" / "admix_B").
9. Section N baseline exclusion: B = BASE_t without the people in G excludes by
   Individual ID (not just Genetic ID) so the same person can never appear in
   both B and G_t.
10. Coastline sampling and distance: Each coastline segment of great-circle
    length d km in Natural Earth 1:50m GeoJSON is sampled at
    k = max(1, ceil(d / 5.0)) evenly spaced sub-segments linearly in (lon, lat),
    and minimum great-circle distance on a 6,371 km sphere is taken over all
    sampled points.
11. Missing coordinates for Argentina: Individuals from Argentina lacking
    latitude or longitude cannot be assigned between SOUTH_CONE and
    ANDES_INLAND, so they are left out of ancient regions.
12. Amendment 1 (--amended): Applied to all ancient sets (CELL.*, REGION.*,
    ANC.*, EARLY.*, VER.*). Longitude bounds [-170, -30] are treated as
    inclusive and checked whenever Longitude is present; group labels
    containing "Norse" (case-sensitive) are excluded.
13. Deduplication in f4.tsv: Exact duplicate (P1, P2, P3, P4, snps, mask)
    entries occurring across sections (e.g., Surui/Karitiana alone in P and R)
    are emitted once.
14. Mask strings in f4.tsv: "-" when no common mask is required (including
    T1/T2 paired checks), "10cM" for the 10 cM block-size test, "admix_A" /
    "admix_B" for Section A, "L_A" / "L_B" for Section L, "M:<G>@<t>" for
    Section N type-matched tests, "C" for Section N coast contrast, and
    "N_desc:<G>" for Section N descriptive statistics.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys
import time
from dataclasses import dataclass

import numpy as np

# Input paths (relative to questions/population-y/)
IND_PATH = "data/aadr_v66.p1/v66.p1_1240K.aadr.patch.PUB.ind"
SNP_PATH = "data/aadr_v66.p1/v66.p1_1240K.aadr.patch.PUB.snp"
GENO_PATH = "data/aadr_v66.p1/v66.p1_1240K.aadr.patch.PUB.geno"
ANNO_PATH = "data/aadr_v66.p1/v66.p1_1240K.aadr.PUB.anno"
COAST_PATH = "data/naturalearth/ne_50m_coastline.geojson"

PASS_ASSESSMENTS = {"Pass", "PROVISIONAL_PASS", "MERGE_PASS"}

CARIBBEAN_ENTITIES = {
    "Cuba",
    "Dominican Republic",
    "Puerto Rico",
    "Bahamas",
    "Haiti",
    "Jamaica",
    "Curacao",
    "Guadeloupe",
    "Saint Lucia",
    "Barbados",
    "Sint Maarten",
    "Trinidad and Tobago",
}

AMERICAS_MAIN_ENTITIES = {
    "USA",
    "Canada",
    "Greenland",
    "Mexico",
    "Belize",
    "Guatemala",
    "Honduras",
    "El Salvador",
    "Nicaragua",
    "Costa Rica",
    "Panama",
    "Colombia",
    "Venezuela",
    "Ecuador",
    "Peru",
    "Bolivia",
    "Brazil",
    "Chile",
    "Argentina",
    "Uruguay",
    "Paraguay",
    "Guyana",
    "Suriname",
    "French Guiana",
}

AMERICAS_ENTITIES = AMERICAS_MAIN_ENTITIES | CARIBBEAN_ENTITIES

MESO_ENTITIES = {
    "Mexico",
    "Belize",
    "Guatemala",
    "Honduras",
    "El Salvador",
    "Nicaragua",
}
ISTHMO_NSA_ENTITIES = {
    "Costa Rica",
    "Panama",
    "Colombia",
    "Venezuela",
    "Guyana",
    "Suriname",
    "French Guiana",
}
EAST_SA_ENTITIES = {"Brazil", "Paraguay", "Uruguay"}

PANEL_A_SINGLE_LABELS = [
    "Mbuti",
    "Yoruba",
    "Mixe",
    "Pima",
    "Surui",
    "Karitiana",
    "Papuan",
    "Australian",
    "Han",
    "French",
    "Sardinian",
    "Mayan",
    "Piapoco",
    "Quechua",
]
MESO_OTHER_LABELS = {"Mexico_Zapotec", "Nahua", "Mixtec_1", "Mixtec_2"}

PANEL_B_SINGLE_LABELS = [
    "Mbuti",
    "Yoruba",
    "Pima",
    "Surui",
    "Karitiana",
    "Papuan",
    "Nasioi",
    "Han",
    "French",
    "Sardinian",
    "Mayan",
    "Piapoco",
]

DUP_LABELS = {"Surui", "Karitiana", "Pima", "Mayan", "Piapoco"}
WORLD_EXCLUDED_SUBSTRINGS = ("-o", "_o", "Ignore", "QCremove", "Discovery", "outlier")
WORLD_EXCLUDED_EXACT = {"Mbuti", "MbutiPygmy"}
WORLD_DATA_TYPES = {"Shotgun.diploid", "Shotgun"}

SA_REGIONS = {"ANDES_COAST", "ANDES_INLAND", "EAST_SA", "SOUTH_CONE", "ISTHMO_NSA"}
NC_REGIONS = {"NAM_WEST", "NAM_EAST", "MESO"}

EARTH_RADIUS_KM = 6371.0


@dataclass(slots=True)
class IndividualRecord:
    idx: int
    gid: str
    person_id: str
    date_bp: float | None
    label: str
    entity: str
    lat: float | None
    lon: float | None
    data_type: str
    snp_count: int
    assessment: str
    is_pass: bool


def _clean_field(val: str) -> str:
    s = val.strip()
    if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        s = s[1:-1].replace('""', '"').strip()
    return s


def _parse_float(val: str) -> float | None:
    s = _clean_field(val)
    if not s or s == ".." or s.lower() in ("na", "n/a", "nan"):
        return None
    try:
        v = float(s)
        return v if math.isfinite(v) else None
    except ValueError:
        return None


def _parse_int(val: str) -> int:
    s = _clean_field(val).replace(",", "")
    if not s or s == "..":
        return -1
    try:
        return int(s)
    except ValueError:
        try:
            return int(float(s))
        except ValueError:
            return -1


def parse_ind(path: str) -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.split()
            if not parts:
                continue
            rows.append((parts[0], parts[1], parts[2]))
    return rows


def parse_anno(path: str, ind_rows: list[tuple[str, str, str]]) -> list[IndividualRecord]:
    csv.field_size_limit(100_000_000)
    records: list[IndividualRecord] = []
    with open(path, "r", encoding="utf-8-sig", errors="replace") as f:
        header_line = f.readline()
        if not header_line:
            raise RuntimeError("Empty .anno file")
        header = header_line.rstrip("\r\n").split("\t")
        n_cols = len(header)

        def col_idx(default_idx: int, prefix: str) -> int:
            if default_idx < n_cols and _clean_field(header[default_idx]).startswith(prefix):
                return default_idx
            for i, h in enumerate(header):
                if _clean_field(h).startswith(prefix):
                    return i
            return default_idx

        idx_gid = col_idx(0, "Genetic ID")
        idx_person = col_idx(2, "Individual ID")
        idx_date = col_idx(10, "Date mean in BP")
        idx_entity = col_idx(16, "Political Entity")
        idx_lat = col_idx(17, "Latitude")
        idx_lon = col_idx(18, "Longitude")
        idx_dtype = col_idx(21, "Data type")
        idx_snps = col_idx(26, "SNPs hit on autosomal targets")
        idx_assess = col_idx(47, "ASSESSMENT")

        line_idx = 0
        for raw_line in f:
            stripped = raw_line.rstrip("\r\n")
            if not stripped:
                continue
            fields = stripped.split("\t")
            if len(fields) != n_cols:
                parsed = next(csv.reader([stripped], delimiter="\t"))
                if len(parsed) == n_cols:
                    fields = parsed
            if line_idx >= len(ind_rows):
                raise RuntimeError(".anno has more rows than .ind")
            ind_gid, _sex, ind_label = ind_rows[line_idx]
            anno_gid = _clean_field(fields[idx_gid]) if idx_gid < len(fields) else ""
            if anno_gid != ind_gid:
                raise RuntimeError(
                    f"Order mismatch at line {line_idx}: .ind={ind_gid!r} vs .anno={anno_gid!r}"
                )
            person_id = _clean_field(fields[idx_person]) if idx_person < len(fields) else ""
            if not person_id or person_id == "..":
                person_id = ind_gid
            date_bp = _parse_float(fields[idx_date]) if idx_date < len(fields) else None
            entity = _clean_field(fields[idx_entity]) if idx_entity < len(fields) else ""
            lat = _parse_float(fields[idx_lat]) if idx_lat < len(fields) else None
            lon = _parse_float(fields[idx_lon]) if idx_lon < len(fields) else None
            data_type = _clean_field(fields[idx_dtype]) if idx_dtype < len(fields) else ""
            snp_count = _parse_int(fields[idx_snps]) if idx_snps < len(fields) else -1
            assessment = _clean_field(fields[idx_assess]) if idx_assess < len(fields) else ""
            is_pass = assessment in PASS_ASSESSMENTS

            records.append(
                IndividualRecord(
                    idx=line_idx,
                    gid=ind_gid,
                    person_id=person_id,
                    date_bp=date_bp,
                    label=ind_label,
                    entity=entity,
                    lat=lat,
                    lon=lon,
                    data_type=data_type,
                    snp_count=snp_count,
                    assessment=assessment,
                    is_pass=is_pass,
                )
            )
            line_idx += 1

    if line_idx != len(ind_rows):
        raise RuntimeError(f"Row count mismatch: .ind={len(ind_rows)} vs .anno={line_idx}")
    return records


def load_coastline_xyz(path: str) -> np.ndarray:
    """Sample all Natural Earth coastline segments at <= 5 km spacing -> (N, 3) unit vectors."""
    with open(path, "r", encoding="utf-8") as f:
        gj = json.load(f)

    polylines: list[list[list[float]]] = []
    for feat in gj.get("features", []):
        geom = feat.get("geometry")
        if not geom:
            continue
        gtype = geom.get("type")
        coords = geom.get("coordinates", [])
        if gtype == "LineString":
            if len(coords) >= 2:
                polylines.append(coords)
        elif gtype == "MultiLineString":
            for line in coords:
                if len(line) >= 2:
                    polylines.append(line)

    lon_chunks: list[np.ndarray] = []
    lat_chunks: list[np.ndarray] = []

    for line in polylines:
        arr = np.asarray([[pt[0], pt[1]] for pt in line], dtype=np.float64)
        lon1 = arr[:-1, 0]
        lat1 = arr[:-1, 1]
        lon2 = arr[1:, 0]
        lat2 = arr[1:, 1]

        # Great-circle length of each segment
        r_lon1 = np.radians(lon1)
        r_lat1 = np.radians(lat1)
        r_lon2 = np.radians(lon2)
        r_lat2 = np.radians(lat2)
        dlat = r_lat2 - r_lat1
        dlon = r_lon2 - r_lon1
        a = np.sin(dlat * 0.5) ** 2 + np.cos(r_lat1) * np.cos(r_lat2) * (np.sin(dlon * 0.5) ** 2)
        seg_km = 2.0 * EARTH_RADIUS_KM * np.arcsin(np.sqrt(np.clip(a, 0.0, 1.0)))

        # Always include polyline vertices
        lon_chunks.append(arr[:, 0])
        lat_chunks.append(arr[:, 1])

        # Add evenly spaced intermediate points for segments > 5 km
        long_idx = np.flatnonzero(seg_km > 5.0)
        if long_idx.size > 0:
            extra_lon: list[np.ndarray] = []
            extra_lat: list[np.ndarray] = []
            for i in long_idx:
                k = int(math.ceil(seg_km[i] / 5.0))
                if k > 1:
                    t = np.arange(1, k, dtype=np.float64) / k
                    extra_lon.append(lon1[i] + t * (lon2[i] - lon1[i]))
                    extra_lat.append(lat1[i] + t * (lat2[i] - lat1[i]))
            if extra_lon:
                lon_chunks.append(np.concatenate(extra_lon))
                lat_chunks.append(np.concatenate(extra_lat))

    lons = np.radians(np.concatenate(lon_chunks))
    lats = np.radians(np.concatenate(lat_chunks))
    cos_lat = np.cos(lats)
    xyz = np.empty((lons.size, 3), dtype=np.float64)
    xyz[:, 0] = cos_lat * np.cos(lons)
    xyz[:, 1] = cos_lat * np.sin(lons)
    xyz[:, 2] = np.sin(lats)
    return xyz


def compute_coast_distances(
    coords: list[tuple[float, float]], coast_xyz: np.ndarray
) -> dict[tuple[float, float], float]:
    """Return min great-circle distance (km) to sampled coastline for unique (lat, lon) pairs."""
    unique = list(dict.fromkeys(coords))
    if not unique:
        return {}
    arr = np.asarray(unique, dtype=np.float64)
    lats = np.radians(arr[:, 0])
    lons = np.radians(arr[:, 1])
    cos_lat = np.cos(lats)
    sites_xyz = np.column_stack([cos_lat * np.cos(lons), cos_lat * np.sin(lons), np.sin(lats)])

    out: dict[tuple[float, float], float] = {}
    batch = 64
    for start in range(0, len(unique), batch):
        end = min(start + batch, len(unique))
        dots = sites_xyz[start:end] @ coast_xyz.T
        max_dots = np.clip(dots.max(axis=1), -1.0, 1.0)
        dists = EARTH_RADIUS_KM * np.arccos(max_dots)
        for j, d in enumerate(dists):
            out[unique[start + j]] = float(d)
    return out


def is_panel_a_gid(gid: str) -> bool:
    return (gid.startswith("S_") or gid.startswith("B_")) and gid.endswith(".DG")


def is_panel_b_gid(gid: str) -> bool:
    return gid.startswith("HGDP") and gid.endswith(".DG")


def ancient_data_type(gid: str) -> str | None:
    if gid.endswith(".AG"):
        return "AG"
    if gid.endswith(".SG") and ".AG" not in gid:
        return "SG"
    return None


def passes_amendment1(rec: IndividualRecord, amended: bool) -> bool:
    if not amended:
        return True
    if "Norse" in rec.label:
        return False
    if rec.lon is not None and not (-170.0 <= rec.lon <= -30.0):
        return False
    return True


def assign_ancient_period(date_bp: float) -> str:
    if date_bp >= 8200.0:
        return "EARLY"
    if date_bp >= 4200.0:
        return "MID"
    return "LATE"


def assign_ancient_region(
    rec: IndividualRecord, coast_dists: dict[tuple[float, float], float]
) -> str | None:
    ent = rec.entity
    lat = rec.lat
    lon = rec.lon

    # NORTH: Greenland; Canada; USA at latitude >= 50
    if ent in ("Greenland", "Canada"):
        return "NORTH"
    if ent == "USA":
        if lat is None:
            return None
        if lat >= 50.0:
            return "NORTH"
        if lon is None:
            return None
        return "NAM_WEST" if lon < -100.0 else "NAM_EAST"

    if ent in MESO_ENTITIES:
        return "MESO"
    if ent in CARIBBEAN_ENTITIES:
        return "CARIB"
    if ent in ISTHMO_NSA_ENTITIES:
        return "ISTHMO_NSA"
    if ent in EAST_SA_ENTITIES:
        return "EAST_SA"

    # SOUTH_CONE: Chile at lat <= -30; Argentina except (-30 < lat < -21 and lon < -64)
    if ent == "Chile":
        if lat is None:
            return None
        if lat <= -30.0:
            return "SOUTH_CONE"
        if lon is None:
            return None
        d = coast_dists[(lat, lon)]
        return "ANDES_INLAND" if d > 75.0 else "ANDES_COAST"

    if ent == "Argentina":
        if lat is None or lon is None:
            return None
        if -30.0 < lat < -21.0 and lon < -64.0:
            return "ANDES_INLAND"
        return "SOUTH_CONE"

    if ent == "Bolivia":
        return "ANDES_INLAND"

    if ent in ("Peru", "Ecuador"):
        if lat is None or lon is None:
            return None
        d = coast_dists[(lat, lon)]
        return "ANDES_INLAND" if d > 75.0 else "ANDES_COAST"

    return None


def build_sample_sets(
    records: list[IndividualRecord],
    coast_xyz: np.ndarray,
    amended: bool,
):
    sets_out: dict[str, list[int]] = {}

    # 1. Present-day Panel A and Panel B
    for lbl in PANEL_A_SINGLE_LABELS:
        sets_out[f"A.{lbl}"] = [
            r.idx for r in records if r.label == lbl and is_panel_a_gid(r.gid) and r.is_pass
        ]
    sets_out["A.MesoOther"] = [
        r.idx
        for r in records
        if r.label in MESO_OTHER_LABELS and is_panel_a_gid(r.gid) and r.is_pass
    ]
    sets_out["A.Amazon"] = sorted(sets_out["A.Surui"] + sets_out["A.Karitiana"])

    for lbl in PANEL_B_SINGLE_LABELS:
        sets_out[f"B.{lbl}"] = [
            r.idx for r in records if r.label == lbl and is_panel_b_gid(r.gid) and r.is_pass
        ]
    sets_out["B.Amazon"] = sorted(sets_out["B.Surui"] + sets_out["B.Karitiana"])

    # Shared present-day / outgroup / archaic
    sets_out["ONG"] = [r.idx for r in records if r.label == "ONG"]
    sets_out["JAR"] = [r.idx for r in records if r.label == "JAR"]
    sets_out["Chimp"] = [r.idx for r in records if r.gid == "Chimp.REF"]
    sets_out["Tianyuan"] = [r.idx for r in records if r.gid == "Tianyuan.AG.BY.AA"]

    # 2. DUP.SGDP / DUP.NYGC and heldout sets
    # Pick best version per person in Panel A and Panel B across DUP_LABELS
    panel_a_dup_by_person: dict[str, IndividualRecord] = {}
    panel_b_dup_by_person: dict[str, IndividualRecord] = {}
    for lbl in ("Surui", "Karitiana", "Pima", "Mayan", "Piapoco"):
        for idx in sets_out[f"A.{lbl}"]:
            r = records[idx]
            prev = panel_a_dup_by_person.get(r.person_id)
            if prev is None or (r.snp_count, -r.idx) > (prev.snp_count, -prev.idx):
                panel_a_dup_by_person[r.person_id] = r
        for idx in sets_out[f"B.{lbl}"]:
            r = records[idx]
            prev = panel_b_dup_by_person.get(r.person_id)
            if prev is None or (r.snp_count, -r.idx) > (prev.snp_count, -prev.idx):
                panel_b_dup_by_person[r.person_id] = r

    common_dup_persons = sorted(
        set(panel_a_dup_by_person.keys()) & set(panel_b_dup_by_person.keys()),
        key=lambda pid: panel_a_dup_by_person[pid].idx,
    )
    dup_pairs: list[tuple[str, int, int, bool]] = []
    for pid in common_dup_persons:
        ra = panel_a_dup_by_person[pid]
        rb = panel_b_dup_by_person[pid]
        is_amaz = ra.label in ("Surui", "Karitiana") or rb.label in ("Surui", "Karitiana")
        dup_pairs.append((pid, ra.idx, rb.idx, is_amaz))

    sets_out["DUP.SGDP"] = [ra_idx for _, ra_idx, _, _ in dup_pairs]
    sets_out["DUP.NYGC"] = [rb_idx for _, _, rb_idx, _ in dup_pairs]

    dup_person_set = set(common_dup_persons)
    sets_out["B.Amazon.heldout"] = [
        idx for idx in sets_out["B.Amazon"] if records[idx].person_id not in dup_person_set
    ]
    sets_out["B.Pima.heldout"] = [
        idx for idx in sets_out["B.Pima"] if records[idx].person_id not in dup_person_set
    ]

    # 3. World panel W
    world_best_by_person: dict[str, IndividualRecord] = {}
    for r in records:
        if r.date_bp is None or r.date_bp != 0.0:
            continue
        if r.entity in AMERICAS_ENTITIES:
            continue
        if r.data_type not in WORLD_DATA_TYPES:
            continue
        if r.snp_count < 900_000:
            continue
        if not r.is_pass:
            continue
        if r.label in WORLD_EXCLUDED_EXACT:
            continue
        if any(sub in r.label for sub in WORLD_EXCLUDED_SUBSTRINGS):
            continue

        key = (1 if is_panel_a_gid(r.gid) else 0, r.snp_count, -r.idx)
        prev = world_best_by_person.get(r.person_id)
        if prev is None:
            world_best_by_person[r.person_id] = r
        else:
            prev_key = (1 if is_panel_a_gid(prev.gid) else 0, prev.snp_count, -prev.idx)
            if key > prev_key:
                world_best_by_person[r.person_id] = r

    world_by_label: dict[str, list[int]] = {}
    for r in world_best_by_person.values():
        world_by_label.setdefault(r.label, []).append(r.idx)

    world_set_names: list[str] = []
    for lbl in sorted(world_by_label.keys()):
        members = sorted(world_by_label[lbl])
        if len(members) >= 2:
            sname = f"W.{lbl}"
            sets_out[sname] = members
            world_set_names.append(sname)

    # 4. Ancient Americans (cells, regions, ANC.SA, ANC.NC)
    anc_best_by_person: dict[str, IndividualRecord] = {}
    for r in records:
        if r.entity not in AMERICAS_ENTITIES:
            continue
        if r.date_bp is None or r.date_bp < 500.0:
            continue
        if r.snp_count < 100_000:
            continue
        if not r.is_pass:
            continue
        if not passes_amendment1(r, amended):
            continue
        prev = anc_best_by_person.get(r.person_id)
        if prev is None or (r.snp_count, -r.idx) > (prev.snp_count, -prev.idx):
            anc_best_by_person[r.person_id] = r

    # Compute coastline distances for Peru, Ecuador, northern Chile
    need_coast_coords: list[tuple[float, float]] = []
    for r in anc_best_by_person.values():
        if r.lat is not None and r.lon is not None:
            if r.entity in ("Peru", "Ecuador") or (r.entity == "Chile" and r.lat > -30.0):
                need_coast_coords.append((r.lat, r.lon))
    coast_dists = compute_coast_distances(need_coast_coords, coast_xyz)

    cells: dict[tuple[str, str], list[int]] = {}
    regions: dict[str, list[int]] = {}
    anc_sa: list[int] = []
    anc_nc: list[int] = []

    for r in sorted(anc_best_by_person.values(), key=lambda x: x.idx):
        reg = assign_ancient_region(r, coast_dists)
        if reg is None:
            continue
        assert r.date_bp is not None
        per = assign_ancient_period(r.date_bp)
        cells.setdefault((reg, per), []).append(r.idx)
        regions.setdefault(reg, []).append(r.idx)
        if reg in SA_REGIONS:
            anc_sa.append(r.idx)
        if reg in NC_REGIONS:
            anc_nc.append(r.idx)

    ancient_set_names: list[str] = []
    for (reg, per) in sorted(cells.keys()):
        sname = f"CELL.{reg}.{per}"
        sets_out[sname] = sorted(cells[(reg, per)])
        ancient_set_names.append(sname)
    for reg in sorted(regions.keys()):
        sname = f"REGION.{reg}"
        sets_out[sname] = sorted(regions[reg])
        ancient_set_names.append(sname)

    sets_out["ANC.SA"] = sorted(anc_sa)
    sets_out["ANC.NC"] = sorted(anc_nc)
    ancient_set_names.extend(["ANC.SA", "ANC.NC"])

    # 5. Early individuals (every version >= 9000 BP, >= 250k SNPs, any assessment)
    for r in records:
        if r.entity not in AMERICAS_ENTITIES:
            continue
        if r.date_bp is None or r.date_bp < 9000.0:
            continue
        if r.snp_count < 250_000:
            continue
        if not passes_amendment1(r, amended):
            continue
        sname = f"EARLY.{r.gid}"
        sets_out[sname] = [r.idx]
        ancient_set_names.append(sname)

    # 6. VER.AG / VER.SG
    ver_ag_by_person: dict[str, IndividualRecord] = {}
    ver_sg_by_person: dict[str, IndividualRecord] = {}
    for r in records:
        if r.entity not in AMERICAS_ENTITIES:
            continue
        if r.date_bp is None or r.date_bp < 500.0:
            continue
        if not r.is_pass:
            continue
        if r.snp_count < 400_000:
            continue
        if not passes_amendment1(r, amended):
            continue
        dt = ancient_data_type(r.gid)
        if dt == "AG":
            prev = ver_ag_by_person.get(r.person_id)
            if prev is None or (r.snp_count, -r.idx) > (prev.snp_count, -prev.idx):
                ver_ag_by_person[r.person_id] = r
        elif dt == "SG":
            prev = ver_sg_by_person.get(r.person_id)
            if prev is None or (r.snp_count, -r.idx) > (prev.snp_count, -prev.idx):
                ver_sg_by_person[r.person_id] = r

    common_ver_persons = sorted(
        set(ver_ag_by_person.keys()) & set(ver_sg_by_person.keys()),
        key=lambda pid: ver_ag_by_person[pid].idx,
    )
    ver_pairs: list[tuple[str, int, int]] = [
        (pid, ver_ag_by_person[pid].idx, ver_sg_by_person[pid].idx) for pid in common_ver_persons
    ]
    sets_out["VER.AG"] = [ag_idx for _, ag_idx, _ in ver_pairs]
    sets_out["VER.SG"] = [sg_idx for _, _, sg_idx in ver_pairs]

    return sets_out, dup_pairs, ver_pairs, ancient_set_names, world_set_names


def parse_snp(path: str):
    auto_idx_list: list[int] = []
    chrom_list: list[int] = []
    gpos_list: list[float] = []
    tv_list: list[bool] = []
    total_snps = 0

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.split()
            if not parts:
                continue
            snp_i = total_snps
            total_snps += 1
            try:
                c = int(parts[1])
            except ValueError:
                continue
            if 1 <= c <= 22:
                auto_idx_list.append(snp_i)
                chrom_list.append(c)
                gpos_list.append(float(parts[2]))
                a1 = parts[4].upper()
                a2 = parts[5].upper()
                is_ti = (
                    (a1 == "A" and a2 == "G")
                    or (a1 == "G" and a2 == "A")
                    or (a1 == "C" and a2 == "T")
                    or (a1 == "T" and a2 == "C")
                )
                tv_list.append(not is_ti)

    auto_idx = np.asarray(auto_idx_list, dtype=np.int32)
    chrom = np.asarray(chrom_list, dtype=np.int32)
    gpos = np.asarray(gpos_list, dtype=np.float64)
    is_tv = np.asarray(tv_list, dtype=np.bool_)

    def make_blocks(block_morgans: float) -> tuple[np.ndarray, int]:
        b = np.floor(gpos / block_morgans).astype(np.int64)
        # Map unique (chrom, b) to contiguous 0..B-1
        keys = chrom.astype(np.int64) * 10_000_000 + (b + 1_000_000)
        uniq, inv = np.unique(keys, return_inverse=True)
        return inv.astype(np.int32), int(uniq.size)

    block5, n_blocks5 = make_blocks(0.05)
    block10, n_blocks10 = make_blocks(0.10)
    return total_snps, auto_idx, is_tv, block5, n_blocks5, block10, n_blocks10


def unpack_record(raw_bytes: bytes, n_total_snps: int, auto_idx: np.ndarray) -> np.ndarray:
    arr = np.frombuffer(raw_bytes, dtype=np.uint8)
    out = np.empty((arr.size, 4), dtype=np.uint8)
    out[:, 0] = (arr >> 6) & 3
    out[:, 1] = (arr >> 4) & 3
    out[:, 2] = (arr >> 2) & 3
    out[:, 3] = arr & 3
    return out.ravel()[:n_total_snps][auto_idx].copy()


def load_genotypes_and_freqs(
    geno_path: str,
    n_ind: int,
    n_total_snps: int,
    auto_idx: np.ndarray,
    accum_sets: dict[str, list[int]],
    keep_indiv_indices: set[int],
    keep_sum_cnt_sets: set[str],
):
    n_auto = int(auto_idx.size)
    rlen = (n_total_snps + 3) // 4

    ind_to_sets: dict[int, list[str]] = {}
    for sname, members in accum_sets.items():
        for idx in members:
            ind_to_sets.setdefault(idx, []).append(sname)

    needed_inds = sorted(set(ind_to_sets.keys()) | keep_indiv_indices)
    set_sums = {sname: np.zeros(n_auto, dtype=np.int32) for sname in accum_sets}
    set_cnts = {sname: np.zeros(n_auto, dtype=np.int32) for sname in accum_sets}
    ind_geno: dict[int, np.ndarray] = {}

    file_size = os.path.getsize(geno_path)
    expected_size = 48 + n_ind * rlen
    if file_size != expected_size:
        raise RuntimeError(f"TGENO size mismatch: got {file_size}, expected {expected_size}")

    with open(geno_path, "rb") as f:
        header_raw = f.read(48)
        header_str = header_raw.split(b"\x00", 1)[0].decode("ascii").strip()
        parts = header_str.split()
        if len(parts) < 3 or parts[0] != "TGENO":
            raise RuntimeError(f"Invalid TGENO header: {header_str!r}")
        if int(parts[1]) != n_ind or int(parts[2]) != n_total_snps:
            raise RuntimeError(
                f"TGENO header counts ({parts[1]}, {parts[2]}) != ({n_ind}, {n_total_snps})"
            )

        for idx in needed_inds:
            f.seek(48 + idx * rlen)
            buf = f.read(rlen)
            if len(buf) != rlen:
                raise RuntimeError(f"Short read at individual {idx}")
            g = unpack_record(buf, n_total_snps, auto_idx)
            if idx in keep_indiv_indices:
                ind_geno[idx] = g
            snames = ind_to_sets.get(idx)
            if snames:
                called = g != 3
                g_val = np.where(called, g, 0)
                for sname in snames:
                    np.add(set_sums[sname], g_val, out=set_sums[sname])
                    np.add(set_cnts[sname], called, out=set_cnts[sname])

    freqs: dict[str, np.ndarray] = {}
    kept_sums: dict[str, np.ndarray] = {}
    kept_cnts: dict[str, np.ndarray] = {}
    for sname in list(accum_sets.keys()):
        s_arr = set_sums.pop(sname)
        c_arr = set_cnts.pop(sname)
        p = np.full(n_auto, np.nan, dtype=np.float64)
        valid = c_arr > 0
        p[valid] = s_arr[valid] / (2.0 * c_arr[valid])
        freqs[sname] = p
        if sname in keep_sum_cnt_sets:
            kept_sums[sname] = s_arr
            kept_cnts[sname] = c_arr

    return freqs, ind_geno, kept_sums, kept_cnts


class MaskedContext:
    """Precomputed block jackknife state on a fixed SNP mask."""

    def __init__(self, valid: np.ndarray, blocks: np.ndarray, n_blocks: int):
        self.valid = valid
        self.n = int(valid.sum())
        self.n_blocks = n_blocks
        if self.n > 0:
            self.b = blocks[valid]
            m_all = np.bincount(self.b, minlength=n_blocks)
            self.keep = m_all > 0
            self.m_j = m_all[self.keep].astype(np.float64)
            self.g = int(self.m_j.size)
            self.nf = float(self.n)
            self.h_j = self.nf / self.m_j
            self.one_minus_w = 1.0 - self.m_j / self.nf
            self.denom_j = self.nf - self.m_j
        else:
            self.g = 0

    def slice_freqs(self, freq_dict: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
        return {k: v[self.valid] for k, v in freq_dict.items()}

    def block_sums_sliced(
        self, p1: np.ndarray, p2: np.ndarray, p3: np.ndarray, p4: np.ndarray
    ) -> np.ndarray:
        x = (p1 - p2) * (p3 - p4)
        return np.bincount(self.b, weights=x, minlength=self.n_blocks)[self.keep]

    def f4_sliced(
        self, p1: np.ndarray, p2: np.ndarray, p3: np.ndarray, p4: np.ndarray
    ) -> tuple[int, float, float, float]:
        if self.n == 0:
            return 0, float("nan"), float("nan"), float("nan")
        S_j = self.block_sums_sliced(p1, p2, p3, p4)
        S = float(S_j.sum())
        theta = S / self.nf
        if self.g <= 1:
            return self.n, theta, float("nan"), float("nan")
        theta_j = (S - S_j) / self.denom_j
        theta_J = self.g * theta - float(np.sum(self.one_minus_w * theta_j))
        tau_j = self.h_j * theta - (self.h_j - 1.0) * theta_j
        se2 = float(np.sum(((tau_j - theta_J) ** 2) / (self.h_j - 1.0))) / self.g
        se = math.sqrt(max(se2, 0.0))
        z = theta / se if se > 0.0 else float("nan")
        return self.n, theta, se, z

    def jackknife_from_thetas(self, theta: float, theta_j: np.ndarray) -> tuple[float, float]:
        if self.g <= 1 or not math.isfinite(theta) or not np.all(np.isfinite(theta_j)):
            return theta, float("nan")
        theta_J = self.g * theta - float(np.sum(self.one_minus_w * theta_j))
        tau_j = self.h_j * theta - (self.h_j - 1.0) * theta_j
        se2 = float(np.sum(((tau_j - theta_J) ** 2) / (self.h_j - 1.0))) / self.g
        se = math.sqrt(max(se2, 0.0))
        return theta, se


def compute_f4(
    p1: np.ndarray,
    p2: np.ndarray,
    p3: np.ndarray,
    p4: np.ndarray,
    blocks: np.ndarray,
    n_blocks: int,
    snp_mask: np.ndarray | None = None,
) -> tuple[int, float, float, float]:
    valid = np.isfinite(p1) & np.isfinite(p2) & np.isfinite(p3) & np.isfinite(p4)
    if snp_mask is not None:
        valid &= snp_mask
    n = int(valid.sum())
    if n == 0:
        return 0, float("nan"), float("nan"), float("nan")
    b = blocks[valid]
    x = (p1[valid] - p2[valid]) * (p3[valid] - p4[valid])
    m_all = np.bincount(b, minlength=n_blocks)
    keep = m_all > 0
    m_j = m_all[keep].astype(np.float64)
    S_j = np.bincount(b, weights=x, minlength=n_blocks)[keep]
    g = int(m_j.size)
    S = float(S_j.sum())
    nf = float(n)
    theta = S / nf
    if g <= 1:
        return n, theta, float("nan"), float("nan")
    theta_j = (S - S_j) / (nf - m_j)
    h_j = nf / m_j
    theta_J = g * theta - float(np.sum((1.0 - m_j / nf) * theta_j))
    tau_j = h_j * theta - (h_j - 1.0) * theta_j
    se2 = float(np.sum(((tau_j - theta_J) ** 2) / (h_j - 1.0))) / g
    se = math.sqrt(max(se2, 0.0))
    z = theta / se if se > 0.0 else float("nan")
    return n, theta, se, z


def compute_D(
    p1: np.ndarray,
    p2: np.ndarray,
    p3: np.ndarray,
    p4: np.ndarray,
    blocks: np.ndarray,
    n_blocks: int,
) -> tuple[int, float, float, float]:
    valid = np.isfinite(p1) & np.isfinite(p2) & np.isfinite(p3) & np.isfinite(p4)
    ctx = MaskedContext(valid, blocks, n_blocks)
    if ctx.n == 0:
        return 0, float("nan"), float("nan"), float("nan")
    q1 = p1[valid]
    q2 = p2[valid]
    q3 = p3[valid]
    q4 = p4[valid]
    num = (q1 - q2) * (q3 - q4)
    den = (q1 + q2 - 2.0 * q1 * q2) * (q3 + q4 - 2.0 * q3 * q4)
    num_j = np.bincount(ctx.b, weights=num, minlength=n_blocks)[ctx.keep]
    den_j = np.bincount(ctx.b, weights=den, minlength=n_blocks)[ctx.keep]
    num_tot = float(num_j.sum())
    den_tot = float(den_j.sum())
    if den_tot == 0.0:
        return ctx.n, float("nan"), float("nan"), float("nan")
    theta = num_tot / den_tot
    theta_j = (num_tot - num_j) / (den_tot - den_j)
    est, se = ctx.jackknife_from_thetas(theta, theta_j)
    z = est / se if (math.isfinite(se) and se > 0.0) else float("nan")
    return ctx.n, est, se, z


def indiv_freq(g: np.ndarray) -> np.ndarray:
    p = np.full(g.size, np.nan, dtype=np.float64)
    called = g != 3
    p[called] = g[called] * 0.5
    return p


def loo_freq(parent_sum: np.ndarray, parent_cnt: np.ndarray, g: np.ndarray) -> np.ndarray:
    called = g != 3
    s = parent_sum - np.where(called, g, 0)
    c = parent_cnt - called
    p = np.full(s.size, np.nan, dtype=np.float64)
    v = c > 0
    p[v] = s[v] / (2.0 * c[v])
    return p


def compute_paired_freqs(
    pairs: list[tuple[int, int]], ind_geno: dict[int, np.ndarray], n_auto: int
) -> tuple[np.ndarray, np.ndarray]:
    sum_a = np.zeros(n_auto, dtype=np.int32)
    sum_b = np.zeros(n_auto, dtype=np.int32)
    cnt = np.zeros(n_auto, dtype=np.int32)
    for idx_a, idx_b in pairs:
        ga = ind_geno[idx_a]
        gb = ind_geno[idx_b]
        both = (ga != 3) & (gb != 3)
        sum_a += np.where(both, ga, 0)
        sum_b += np.where(both, gb, 0)
        cnt += both
    p_a = np.full(n_auto, np.nan, dtype=np.float64)
    p_b = np.full(n_auto, np.nan, dtype=np.float64)
    v = cnt > 0
    denom = 2.0 * cnt[v]
    p_a[v] = sum_a[v] / denom
    p_b[v] = sum_b[v] / denom
    return p_a, p_b


def fmt_float(val: float) -> str:
    if not math.isfinite(val):
        return "nan"
    return f"{val:.12g}"


def main() -> None:
    t0 = time.time()
    parser = argparse.ArgumentParser(
        description="Independent replication of the Population Y analysis protocol."
    )
    parser.add_argument("outdir", help="Output directory for sets.tsv, f4.tsv, composites.tsv")
    parser.add_argument(
        "--amended",
        action="store_true",
        help="Apply Amendment 1's two corrections to ancient American set membership.",
    )
    args = parser.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    print(f"[replicate] Starting (amended={args.amended})", file=sys.stderr)

    ind_rows = parse_ind(IND_PATH)
    n_ind = len(ind_rows)
    records = parse_anno(ANNO_PATH, ind_rows)
    print(f"[replicate] Parsed {n_ind} individuals ({time.time() - t0:.1f}s)", file=sys.stderr)

    coast_xyz = load_coastline_xyz(COAST_PATH)
    print(
        f"[replicate] Sampled {coast_xyz.shape[0]} coastline points ({time.time() - t0:.1f}s)",
        file=sys.stderr,
    )

    sets_out, dup_pairs, ver_pairs, ancient_set_names, world_set_names = build_sample_sets(
        records, coast_xyz, args.amended
    )
    print(
        f"[replicate] Built {len(sets_out)} sets "
        f"(W={len(world_set_names)}, ancient={len(ancient_set_names)}, "
        f"DUP={len(dup_pairs)}, VER={len(ver_pairs)}) ({time.time() - t0:.1f}s)",
        file=sys.stderr,
    )

    # Write sets.tsv
    sets_path = os.path.join(args.outdir, "sets.tsv")
    with open(sets_path, "w", encoding="utf-8", newline="\n") as f:
        f.write("set\tgenetic_id\n")
        for sname, members in sets_out.items():
            for idx in members:
                f.write(f"{sname}\t{records[idx].gid}\n")

    # Parse .snp
    n_total_snps, auto_idx, is_tv, block5, n_blocks5, block10, n_blocks10 = parse_snp(SNP_PATH)
    n_auto = int(auto_idx.size)
    print(
        f"[replicate] Parsed {n_total_snps} SNPs ({n_auto} autosomal, "
        f"{n_blocks5} 5cM blocks, {n_blocks10} 10cM blocks) ({time.time() - t0:.1f}s)",
        file=sys.stderr,
    )

    # Prepare accumulation sets (all sets_out + ancient @AG/@SG subsets + BASE.AG/BASE.SG)
    accum_sets: dict[str, list[int]] = dict(sets_out)

    base_members: dict[str, list[int]] = {"AG": [], "SG": []}
    for idx in sets_out["ANC.NC"]:
        dt = ancient_data_type(records[idx].gid)
        if dt in base_members:
            base_members[dt].append(idx)
    accum_sets["BASE.AG"] = base_members["AG"]
    accum_sets["BASE.SG"] = base_members["SG"]

    ancient_typed_members: dict[tuple[str, str], list[int]] = {}
    for gname in ancient_set_names:
        for dt in ("AG", "SG"):
            mem = [idx for idx in sets_out[gname] if ancient_data_type(records[idx].gid) == dt]
            if mem:
                key = f"{gname}@{dt}"
                accum_sets[key] = mem
                ancient_typed_members[(gname, dt)] = mem

    # Individuals whose per-individual uint8 genotypes we retain in memory
    keep_indiv: set[int] = set()
    panel_a_amer_sets = [
        "A.Mixe",
        "A.MesoOther",
        "A.Pima",
        "A.Surui",
        "A.Karitiana",
        "A.Mayan",
        "A.Piapoco",
        "A.Quechua",
    ]
    panel_b_amer_sets = [
        "B.Pima",
        "B.Surui",
        "B.Karitiana",
        "B.Mayan",
        "B.Piapoco",
    ]
    for s in panel_a_amer_sets + panel_b_amer_sets:
        keep_indiv.update(sets_out[s])
    for _, ia, ib, _ in dup_pairs:
        keep_indiv.add(ia)
        keep_indiv.add(ib)
    for _, ia, ib in ver_pairs:
        keep_indiv.add(ia)
        keep_indiv.add(ib)
    keep_indiv.update(base_members["AG"])
    keep_indiv.update(base_members["SG"])

    keep_sum_cnt = {"A.Mixe", "A.Amazon", "B.Pima", "B.Amazon", "BASE.AG", "BASE.SG"}

    freqs, ind_geno, kept_sums, kept_cnts = load_genotypes_and_freqs(
        GENO_PATH, n_ind, n_total_snps, auto_idx, accum_sets, keep_indiv, keep_sum_cnt
    )
    print(
        f"[replicate] Loaded genotypes and frequencies for {len(freqs)} sets "
        f"and {len(ind_geno)} kept individuals ({time.time() - t0:.1f}s)",
        file=sys.stderr,
    )

    # SNP classes
    p_yri = freqs["B.Yoruba"]
    is_yri = np.isfinite(p_yri) & (p_yri > 0.05) & (p_yri < 0.95)
    snp_masks: dict[str, np.ndarray | None] = {
        "all": None,
        "tv": is_tv,
        "yri": is_yri,
    }

    # Result collectors (deduplicated by (P1, P2, P3, P4, snps, mask))
    f4_rows: list[