#!/usr/bin/env python3
"""Independent replication of the Population Y (Ypykuera) analysis protocol.

Usage: python replicate.py OUTDIR [--amended]  (run from questions/population-y/)

Protocol ambiguities and choices made:
1. ONG/JAR assessment: Protocol says "everyone labelled ONG and JAR" without
   "with a Pass", so exact .ind labels ONG/JAR are taken without ASSESSMENT filter.
2. World panel W deduplication: Eligible rows are deduplicated globally by
   Individual ID (prefer S_/B_*.DG, then highest SNP count, ties earlier line)
   before the >=2 people/label rule. Missing Individual ID ("..") falls back to Genetic ID.
3. Panel A/B sets: Only sets listed in the protocol tables are built.
4. 10 cM block-size test: Emitted in f4.tsv with mask="10cM".
5. Section R "other American groups": Panel A uses A.Mayan, A.Piapoco, A.Quechua,
   A.Pima, A.MesoOther; Panel B uses B.Mayan, B.Piapoco.
6. Section N transversion M1: Computed for both A.Papuan and ONG to cover both readings.
7. Section A per-individual diagnostic: Emitted in f4.tsv using <panel>.ind.<gid>
   and <set>-<gid>; group-level admixture uses the LOCKED protocol equations
   (even under --amended), writing composites.tsv and component f4s (mask="admix_A"/"admix_B").
8. Section N baseline exclusion: B = BASE_t excludes members sharing Individual ID with G.
9. Coastline sampling: Each Natural Earth segment of great-circle length d km is
   sampled at max(1, ceil(d/5)) evenly spaced steps linearly in (lon, lat); min
   great-circle distance uses Earth radius 6371 km.
10. Missing coordinates: Individuals missing lat/lon where needed (including Argentina)
    are left out of ancient region sets.
11. Amendment 1 (--amended): Applied to all ancient sets (CELL, REGION, ANC, EARLY,
    VER); excludes labels containing "Norse" and given longitudes outside [-170, -30].
12. Exact duplicate (P1, P2, P3, P4, snps, mask) rows across sections are emitted once.
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

IND_PATH = "data/aadr_v66.p1/v66.p1_1240K.aadr.patch.PUB.ind"
SNP_PATH = "data/aadr_v66.p1/v66.p1_1240K.aadr.patch.PUB.snp"
GENO_PATH = "data/aadr_v66.p1/v66.p1_1240K.aadr.patch.PUB.geno"
ANNO_PATH = "data/aadr_v66.p1/v66.p1_1240K.aadr.PUB.anno"
COAST_PATH = "data/naturalearth/ne_50m_coastline.geojson"

PASS_VALS = {"Pass", "PROVISIONAL_PASS", "MERGE_PASS"}
CARIB = {
    "Cuba", "Dominican Republic", "Puerto Rico", "Bahamas", "Haiti", "Jamaica",
    "Curacao", "Guadeloupe", "Saint Lucia", "Barbados", "Sint Maarten",
    "Trinidad and Tobago",
}
AMERICAS = CARIB | {
    "USA", "Canada", "Greenland", "Mexico", "Belize", "Guatemala", "Honduras",
    "El Salvador", "Nicaragua", "Costa Rica", "Panama", "Colombia", "Venezuela",
    "Ecuador", "Peru", "Bolivia", "Brazil", "Chile", "Argentina", "Uruguay",
    "Paraguay", "Guyana", "Suriname", "French Guiana",
}
MESO = {"Mexico", "Belize", "Guatemala", "Honduras", "El Salvador", "Nicaragua"}
ISTHMO = {"Costa Rica", "Panama", "Colombia", "Venezuela", "Guyana", "Suriname", "French Guiana"}
EAST_SA = {"Brazil", "Paraguay", "Uruguay"}
SA_REGIONS = {"ANDES_COAST", "ANDES_INLAND", "EAST_SA", "SOUTH_CONE", "ISTHMO_NSA"}
NC_REGIONS = {"NAM_WEST", "NAM_EAST", "MESO"}

PANEL_A_LABELS = [
    "Mbuti", "Yoruba", "Mixe", "Pima", "Surui", "Karitiana", "Papuan",
    "Australian", "Han", "French", "Sardinian", "Mayan", "Piapoco", "Quechua",
]
MESO_OTHER = {"Mexico_Zapotec", "Nahua", "Mixtec_1", "Mixtec_2"}
PANEL_B_LABELS = [
    "Mbuti", "Yoruba", "Pima", "Surui", "Karitiana", "Papuan", "Nasioi",
    "Han", "French", "Sardinian", "Mayan", "Piapoco",
]
DUP_LABELS = ("Surui", "Karitiana", "Pima", "Mayan", "Piapoco")
W_EXCL_SUB = ("-o", "_o", "Ignore", "QCremove", "Discovery", "outlier")
W_EXCL_EXACT = {"Mbuti", "MbutiPygmy"}
W_DTYPES = {"Shotgun.diploid", "Shotgun"}
EARTH_R = 6371.0


@dataclass(slots=True)
class Rec:
    idx: int
    gid: str
    pid: str
    date: float | None
    label: str
    entity: str
    lat: float | None
    lon: float | None
    dtype: str
    snps: int
    is_pass: bool


def clean(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        s = s[1:-1].replace('""', '"').strip()
    return s


def pfloat(s: str) -> float | None:
    s = clean(s)
    if not s or s == ".." or s.lower() in ("na", "n/a", "nan"):
        return None
    try:
        v = float(s)
        return v if math.isfinite(v) else None
    except ValueError:
        return None


def pint(s: str) -> int:
    s = clean(s).replace(",", "")
    if not s or s == "..":
        return -1
    try:
        return int(s)
    except ValueError:
        try:
            return int(float(s))
        except ValueError:
            return -1


def parse_metadata() -> list[Rec]:
    ind = []
    with open(IND_PATH, "r", encoding="utf-8") as f:
        for line in f:
            p = line.split()
            if p:
                ind.append((p[0], p[2]))
    csv.field_size_limit(100_000_000)
    recs: list[Rec] = []
    with open(ANNO_PATH, "r", encoding="utf-8-sig", errors="replace") as f:
        hdr = f.readline().rstrip("\r\n").split("\t")
        nc = len(hdr)

        def ci(default: int, pfx: str) -> int:
            if default < nc and clean(hdr[default]).startswith(pfx):
                return default
            for i, h in enumerate(hdr):
                if clean(h).startswith(pfx):
                    return i
            return default

        c_gid, c_pid = ci(0, "Genetic ID"), ci(2, "Individual ID")
        c_date, c_ent = ci(10, "Date mean in BP"), ci(16, "Political Entity")
        c_lat, c_lon = ci(17, "Latitude"), ci(18, "Longitude")
        c_dt, c_snp = ci(21, "Data type"), ci(26, "SNPs hit on autosomal targets")
        c_ass = ci(47, "ASSESSMENT")

        i = 0
        for raw in f:
            s = raw.rstrip("\r\n")
            if not s:
                continue
            cols = s.split("\t")
            if len(cols) != nc:
                parsed = next(csv.reader([s], delimiter="\t"))
                if len(parsed) == nc:
                    cols = parsed
            gid, lbl = ind[i]
            if clean(cols[c_gid]) != gid:
                raise RuntimeError(f"ind/anno mismatch at {i}: {gid} vs {cols[c_gid]}")
            pid = clean(cols[c_pid]) if c_pid < len(cols) else ""
            if not pid or pid == "..":
                pid = gid
            recs.append(Rec(
                idx=i, gid=gid, pid=pid,
                date=pfloat(cols[c_date]) if c_date < len(cols) else None,
                label=lbl,
                entity=clean(cols[c_ent]) if c_ent < len(cols) else "",
                lat=pfloat(cols[c_lat]) if c_lat < len(cols) else None,
                lon=pfloat(cols[c_lon]) if c_lon < len(cols) else None,
                dtype=clean(cols[c_dt]) if c_dt < len(cols) else "",
                snps=pint(cols[c_snp]) if c_snp < len(cols) else -1,
                is_pass=(clean(cols[c_ass]) in PASS_VALS) if c_ass < len(cols) else False,
            ))
            i += 1
    if i != len(ind):
        raise RuntimeError(f"Row mismatch: ind={len(ind)} anno={i}")
    return recs


def load_coast_xyz() -> np.ndarray:
    with open(COAST_PATH, "r", encoding="utf-8") as f:
        gj = json.load(f)
    lines = []
    for feat in gj.get("features", []):
        g = feat.get("geometry") or {}
        t, c = g.get("type"), g.get("coordinates", [])
        if t == "LineString" and len(c) >= 2:
            lines.append(c)
        elif t == "MultiLineString":
            lines.extend(x for x in c if len(x) >= 2)
    lon_c, lat_c = [], []
    for line in lines:
        a = np.asarray([[p[0], p[1]] for p in line], dtype=np.float64)
        lon_c.append(a[:, 0])
        lat_c.append(a[:, 1])
        r1, r2 = np.radians(a[:-1]), np.radians(a[1:])
        dlon, dlat = r2[:, 0] - r1[:, 0], r2[:, 1] - r1[:, 1]
        h = np.sin(dlat * 0.5) ** 2 + np.cos(r1[:, 1]) * np.cos(r2[:, 1]) * np.sin(dlon * 0.5) ** 2
        dkm = 2.0 * EARTH_R * np.arcsin(np.sqrt(np.clip(h, 0.0, 1.0)))
        for j in np.flatnonzero(dkm > 5.0):
            k = int(math.ceil(dkm[j] / 5.0))
            if k > 1:
                t = np.arange(1, k, dtype=np.float64) / k
                lon_c.append(a[j, 0] + t * (a[j + 1, 0] - a[j, 0]))
                lat_c.append(a[j, 1] + t * (a[j + 1, 1] - a[j, 1]))
    lons, lats = np.radians(np.concatenate(lon_c)), np.radians(np.concatenate(lat_c))
    cl = np.cos(lats)
    return np.column_stack([cl * np.cos(lons), cl * np.sin(lons), np.sin(lats)])


def coast_distances(coords: list[tuple[float, float]], cxyz: np.ndarray) -> dict[tuple[float, float], float]:
    uniq = list(dict.fromkeys(coords))
    if not uniq:
        return {}
    a = np.radians(np.asarray(uniq, dtype=np.float64))
    cl = np.cos(a[:, 0])
    sxyz = np.column_stack([cl * np.cos(a[:, 1]), cl * np.sin(a[:, 1]), np.sin(a[:, 0])])
    out = {}
    for s in range(0, len(uniq), 64):
        dots = sxyz[s:s + 64] @ cxyz.T
        dists = EARTH_R * np.arccos(np.clip(dots.max(axis=1), -1.0, 1.0))
        for j, d in enumerate(dists):
            out[uniq[s + j]] = float(d)
    return out


def is_pa(gid: str) -> bool:
    return (gid.startswith("S_") or gid.startswith("B_")) and gid.endswith(".DG")


def is_pb(gid: str) -> bool:
    return gid.startswith("HGDP") and gid.endswith(".DG")


def anc_type(gid: str) -> str | None:
    if gid.endswith(".AG"):
        return "AG"
    if gid.endswith(".SG") and ".AG" not in gid:
        return "SG"
    return None


def ok_amend1(r: Rec, amended: bool) -> bool:
    if not amended:
        return True
    if "Norse" in r.label:
        return False
    if r.lon is not None and not (-170.0 <= r.lon <= -30.0):
        return False
    return True


def assign_region(r: Rec, cdists: dict[tuple[float, float], float]) -> str | None:
    e, lat, lon = r.entity, r.lat, r.lon
    if e in ("Greenland", "Canada"):
        return "NORTH"
    if e == "USA":
        if lat is None:
            return None
        if lat >= 50.0:
            return "NORTH"
        return None if lon is None else ("NAM_WEST" if lon < -100.0 else "NAM_EAST")
    if e in MESO:
        return "MESO"
    if e in CARIB:
        return "CARIB"
    if e in ISTHMO:
        return "ISTHMO_NSA"
    if e in EAST_SA:
        return "EAST_SA"
    if e == "Chile":
        if lat is None:
            return None
        if lat <= -30.0:
            return "SOUTH_CONE"
        if lon is None:
            return None
        return "ANDES_INLAND" if cdists[(lat, lon)] > 75.0 else "ANDES_COAST"
    if e == "Argentina":
        if lat is None or lon is None:
            return None
        return "ANDES_INLAND" if (-30.0 < lat < -21.0 and lon < -64.0) else "SOUTH_CONE"
    if e == "Bolivia":
        return "ANDES_INLAND"
    if e in ("Peru", "Ecuador"):
        if lat is None or lon is None:
            return None
        return "ANDES_INLAND" if cdists[(lat, lon)] > 75.0 else "ANDES_COAST"
    return None


def build_sets(recs: list[Rec], cxyz: np.ndarray, amended: bool):
    sets: dict[str, list[int]] = {}

    for lbl in PANEL_A_LABELS:
        sets[f"A.{lbl}"] = [r.idx for r in recs if r.label == lbl and is_pa(r.gid) and r.is_pass]
    sets["A.MesoOther"] = [r.idx for r in recs if r.label in MESO_OTHER and is_pa(r.gid) and r.is_pass]
    sets["A.Amazon"] = sorted(sets["A.Surui"] + sets["A.Karitiana"])

    for lbl in PANEL_B_LABELS:
        sets[f"B.{lbl}"] = [r.idx for r in recs if r.label == lbl and is_pb(r.gid) and r.is_pass]
    sets["B.Amazon"] = sorted(sets["B.Surui"] + sets["B.Karitiana"])

    sets["ONG"] = [r.idx for r in recs if r.label == "ONG"]
    sets["JAR"] = [r.idx for r in recs if r.label == "JAR"]
    sets["Chimp"] = [r.idx for r in recs if r.gid == "Chimp.REF"]
    sets["Tianyuan"] = [r.idx for r in recs if r.gid == "Tianyuan.AG.BY.AA"]

    # DUP and heldout
    pa_dup: dict[str, Rec] = {}
    pb_dup: dict[str, Rec] = {}
    for lbl in DUP_LABELS:
        for i in sets[f"A.{lbl}"]:
            r = recs[i]
            if r.pid not in pa_dup or (r.snps, -r.idx) > (pa_dup[r.pid].snps, -pa_dup[r.pid].idx):
                pa_dup[r.pid] = r
        for i in sets[f"B.{lbl}"]:
            r = recs[i]
            if r.pid not in pb_dup or (r.snps, -r.idx) > (pb_dup[r.pid].snps, -pb_dup[r.pid].idx):
                pb_dup[r.pid] = r
    dup_pids = sorted(pa_dup.keys() & pb_dup.keys(), key=lambda p: pa_dup[p].idx)
    dup_pairs = [
        (p, pa_dup[p].idx, pb_dup[p].idx, pa_dup[p].label in ("Surui", "Karitiana"))
        for p in dup_pids
    ]
    sets["DUP.SGDP"] = [a for _, a, _, _ in dup_pairs]
    sets["DUP.NYGC"] = [b for _, _, b, _ in dup_pairs]
    dup_set = set(dup_pids)
    sets["B.Amazon.heldout"] = [i for i in sets["B.Amazon"] if recs[i].pid not in dup_set]
    sets["B.Pima.heldout"] = [i for i in sets["B.Pima"] if recs[i].pid not in dup_set]

    # World panel W
    w_best: dict[str, Rec] = {}
    for r in recs:
        if (
            r.date != 0.0 or r.entity in AMERICAS or r.dtype not in W_DTYPES
            or r.snps < 900_000 or not r.is_pass or r.label in W_EXCL_EXACT
            or any(sub in r.label for sub in W_EXCL_SUB)
        ):
            continue
        k = (1 if is_pa(r.gid) else 0, r.snps, -r.idx)
        prev = w_best.get(r.pid)
        if prev is None or k > (1 if is_pa(prev.gid) else 0, prev.snps, -prev.idx):
            w_best[r.pid] = r
    w_lbl: dict[str, list[int]] = {}
    for r in w_best.values():
        w_lbl.setdefault(r.label, []).append(r.idx)
    world_names = []
    for lbl in sorted(w_lbl):
        if len(w_lbl[lbl]) >= 2:
            sets[f"W.{lbl}"] = sorted(w_lbl[lbl])
            world_names.append(f"W.{lbl}")

    # Ancient Americans
    anc_best: dict[str, Rec] = {}
    for r in recs:
        if (
            r.entity not in AMERICAS or r.date is None or r.date < 500.0
            or r.snps < 100_000 or not r.is_pass or not ok_amend1(r, amended)
        ):
            continue
        prev = anc_best.get(r.pid)
        if prev is None or (r.snps, -r.idx) > (prev.snps, -prev.idx):
            anc_best[r.pid] = r
    need_c = [
        (r.lat, r.lon) for r in anc_best.values()
        if r.lat is not None and r.lon is not None
        and (r.entity in ("Peru", "Ecuador") or (r.entity == "Chile" and r.lat > -30.0))
    ]
    cdists = coast_distances(need_c, cxyz)
    cells: dict[tuple[str, str], list[int]] = {}
    regs: dict[str, list[int]] = {}
    anc_sa, anc_nc = [], []
    for r in sorted(anc_best.values(), key=lambda x: x.idx):
        reg = assign_region(r, cdists)
        if reg is None:
            continue
        per = "EARLY" if r.date >= 8200.0 else ("MID" if r.date >= 4200.0 else "LATE")
        cells.setdefault((reg, per), []).append(r.idx)
        regs.setdefault(reg, []).append(r.idx)
        if reg in SA_REGIONS:
            anc_sa.append(r.idx)
        if reg in NC_REGIONS:
            anc_nc.append(r.idx)
    anc_names = []
    for reg, per in sorted(cells):
        sets[f"CELL.{reg}.{per}"] = sorted(cells[(reg, per)])
        anc_names.append(f"CELL.{reg}.{per}")
    for reg in sorted(regs):
        sets[f"REGION.{reg}"] = sorted(regs[reg])
        anc_names.append(f"REGION.{reg}")
    sets["ANC.SA"] = sorted(anc_sa)
    sets["ANC.NC"] = sorted(anc_nc)
    anc_names.extend(["ANC.SA", "ANC.NC"])

    # Early individuals
    for r in recs:
        if (
            r.entity in AMERICAS and r.date is not None and r.date >= 9000.0
            and r.snps >= 250_000 and ok_amend1(r, amended)
        ):
            sets[f"EARLY.{r.gid}"] = [r.idx]
            anc_names.append(f"EARLY.{r.gid}")

    # VER.AG / VER.SG
    v_ag: dict[str, Rec] = {}
    v_sg: dict[str, Rec] = {}
    for r in recs:
        if (
            r.entity not in AMERICAS or r.date is None or r.date < 500.0
            or not r.is_pass or r.snps < 400_000 or not ok_amend1(r, amended)
        ):
            continue
        dt = anc_type(r.gid)
        target = v_ag if dt == "AG" else (v_sg if dt == "SG" else None)
        if target is not None:
            prev = target.get(r.pid)
            if prev is None or (r.snps, -r.idx) > (prev.snps, -prev.idx):
                target[r.pid] = r
    ver_pids = sorted(v_ag.keys() & v_sg.keys(), key=lambda p: v_ag[p].idx)
    ver_pairs = [(p, v_ag[p].idx, v_sg[p].idx) for p in ver_pids]
    sets["VER.AG"] = [a for _, a, _ in ver_pairs]
    sets["VER.SG"] = [b for _, _, b in ver_pairs]
    return sets, dup_pairs, ver_pairs, anc_names, world_names


def parse_snp():
    aidx, chrom, gpos, tv = [], [], [], []
    tot = 0
    with open(SNP_PATH, "r", encoding="utf-8") as f:
        for line in f:
            p = line.split()
            if not p:
                continue
            i = tot
            tot += 1
            try:
                c = int(p[1])
            except ValueError:
                continue
            if 1 <= c <= 22:
                aidx.append(i)
                chrom.append(c)
                gpos.append(float(p[2]))
                a1, a2 = p[4].upper(), p[5].upper()
                tv.append((a1, a2) not in (("A", "G"), ("G", "A"), ("C", "T"), ("T", "C")))
    auto_idx = np.asarray(aidx, dtype=np.int32)
    ch = np.asarray(chrom, dtype=np.int64)
    gp = np.asarray(gpos, dtype=np.float64)
    is_tv = np.asarray(tv, dtype=np.bool_)

    def mkblk(w: float):
        b = np.floor(gp / w).astype(np.int64)
        u, inv = np.unique(ch * 10_000_000 + (b + 1_000_000), return_inverse=True)
        return inv.astype(np.int32), int(u.size)

    b5, nb5 = mkblk(0.05)
    b10, nb10 = mkblk(0.10)
    return tot, auto_idx, is_tv, b5, nb5, b10, nb10


def load_genos(n_ind: int, n_snps: int, auto_idx: np.ndarray,
               accum: dict[str, list[int]], keep_ind: set[int], keep_sc: set[str]):
    n_auto = int(auto_idx.size)
    rlen = (n_snps + 3) // 4
    i2s: dict[int, list[str]] = {}
    for sn, mem in accum.items():
        for i in mem:
            i2s.setdefault(i, []).append(sn)
    needed = sorted(set(i2s) | keep_ind)
    sums = {sn: np.zeros(n_auto, dtype=np.int32) for sn in accum}
    cnts = {sn: np.zeros(n_auto, dtype=np.int32) for sn in accum}
    igeno: dict[int, np.ndarray] = {}

    if os.path.getsize(GENO_PATH) != 48 + n_ind * rlen:
        raise RuntimeError("Unexpected TGENO file size")
    with open(GENO_PATH, "rb") as f:
        hdr = f.read(48).split(b"\x00", 1)[0].decode("ascii").split()
        if hdr[0] != "TGENO" or int(hdr[1]) != n_ind or int(hdr[2]) != n_snps:
            raise RuntimeError(f"Bad TGENO header: {hdr}")
        for idx in needed:
            f.seek(48 + idx * rlen)
            arr = np.frombuffer(f.read(rlen), dtype=np.uint8)
            unp = np.empty((arr.size, 4), dtype=np.uint8)
            unp[:, 0] = (arr >> 6) & 3
            unp[:, 1] = (arr >> 4) & 3
            unp[:, 2] = (arr >> 2) & 3
            unp[:, 3] = arr & 3
            g = unp.ravel()[:n_snps][auto_idx].copy()
            if idx in keep_ind:
                igeno[idx] = g
            snames = i2s.get(idx)
            if snames:
                ok = g != 3
                gv = np.where(ok, g, 0)
                for sn in snames:
                    np.add(sums[sn], gv, out=sums[sn])
                    np.add(cnts[sn], ok, out=cnts[sn])
    freqs, ksum, kcnt = {}, {}, {}
    for sn in list(accum):
        s, c = sums.pop(sn), cnts.pop(sn)
        p = np.full(n_auto, np.nan, dtype=np.float64)
        v = c > 0
        p[v] = s[v] / (2.0 * c[v])
        freqs[sn] = p
        if sn in keep_sc:
            ksum[sn], kcnt[sn] = s, c
    return freqs, igeno, ksum, kcnt


class MaskCtx:
    def __init__(self, valid: np.ndarray, blocks: np.ndarray, nb: int):
        self.valid, self.nb = valid, nb
        self.n = int(valid.sum())
        if self.n > 0:
            self.b = blocks[valid]
            m = np.bincount(self.b, minlength=nb)
            self.keep = m > 0
            self.mj = m[self.keep].astype(np.float64)
            self.g = int(self.mj.size)
            self.nf = float(self.n)
            self.hj = self.nf / self.mj
            self.w = 1.0 - self.mj / self.nf
            self.dj = self.nf - self.mj
        else:
            self.g = 0

    def bsums(self, p1: np.ndarray, p2: np.ndarray, p3: np.ndarray, p4: np.ndarray) -> np.ndarray:
        return np.bincount(self.b, weights=(p1 - p2) * (p3 - p4), minlength=self.nb)[self.keep]

    def jk(self, theta: float, tj: np.ndarray) -> tuple[float, float]:
        if self.g <= 1 or not math.isfinite(theta) or not np.all(np.isfinite(tj)):
            return theta, float("nan")
        tJ = self.g * theta - float(np.sum(self.w * tj))
        tau = self.hj * theta - (self.hj - 1.0) * tj
        se2 = float(np.sum(((tau - tJ) ** 2) / (self.hj - 1.0))) / self.g
        return theta, math.sqrt(max(se2, 0.0))

    def f4_sl(self, p1: np.ndarray, p2: np.ndarray, p3: np.ndarray, p4: np.ndarray):
        if self.n == 0:
            return 0, float("nan"), float("nan"), float("nan")
        sj = self.bsums(p1, p2, p3, p4)
        s = float(sj.sum())
        th = s / self.nf
        est, se = self.jk(th, (s - sj) / self.dj)
        z = est / se if (math.isfinite(se) and se > 0.0) else float("nan")
        return self.n, est, se, z


def f4_direct(p1, p2, p3, p4, blocks, nb, smask=None):
    v = np.isfinite(p1) & np.isfinite(p2) & np.isfinite(p3) & np.isfinite(p4)
    if smask is not None:
        v &= smask
    ctx = MaskCtx(v, blocks, nb)
    if ctx.n == 0:
        return 0, float("nan"), float("nan"), float("nan")
    return ctx.f4_sl(p1[v], p2[v], p3[v], p4[v])


def d_stat(p1, p2, p3, p4, blocks, nb):
    v = np.isfinite(p1) & np.isfinite(p2) & np.isfinite(p3) & np.isfinite(p4)
    ctx = MaskCtx(v, blocks, nb)
    if ctx.n == 0:
        return 0, float("nan"), float("nan"), float("nan")
    q1, q2, q3, q4 = p1[v], p2[v], p3[v], p4[v]
    nj = np.bincount(ctx.b, weights=(q1 - q2) * (q3 - q4), minlength=nb)[ctx.keep]
    dj = np.bincount(ctx.b, weights=(q1 + q2 - 2 * q1 * q2) * (q3 + q4 - 2 * q3 * q4), minlength=nb)[ctx.keep]
    nt, dt = float(nj.sum()), float(dj.sum())
    if dt == 0.0:
        return ctx.n, float("nan"), float("nan"), float("nan")
    est, se = ctx.jk(nt / dt, (nt - nj) / (dt - dj))
    return ctx.n, est, se, (est / se if (math.isfinite(se) and se > 0.0) else float("nan"))


def ind_freq(g: np.ndarray) -> np.ndarray:
    p = np.full(g.size, np.nan, dtype=np.float64)
    ok = g != 3
    p[ok] = g[ok] * 0.5
    return p


def sub_freq(ps: np.ndarray, pc: np.ndarray, gs: list[np.ndarray]) -> np.ndarray:
    s = ps.copy()
    c = pc.copy()
    for g in gs:
        ok = g != 3
        s -= np.where(ok, g, 0)
        c -= ok
    p = np.full(s.size, np.nan, dtype=np.float64)
    v = c > 0
    p[v] = s[v] / (2.0 * c[v])
    return p


def paired_freqs(pairs: list[tuple[int, int]], igeno: dict[int, np.ndarray], n_auto: int):
    sa = np.zeros(n_auto, dtype=np.int32)
    sb = np.zeros(n_auto, dtype=np.int32)
    cnt = np.zeros(n_auto, dtype=np.int32)
    for ia, ib in pairs:
        ga, gb = igeno[ia], igeno[ib]
        both = (ga != 3) & (gb != 3)
        sa += np.where(both, ga, 0)
        sb += np.where(both, gb, 0)
        cnt += both
    pa = np.full(n_auto, np.nan, dtype=np.float64)
    pb = np.full(n_auto, np.nan, dtype=np.float64)
    v = cnt > 0
    d = 2.0 * cnt[v]
    pa[v], pb[v] = sa[v] / d, sb[v] / d
    return pa, pb


def common_valid(arrs: list[np.ndarray], extra: np.ndarray | None = None) -> np.ndarray:
    v = np.isfinite(arrs[0]).copy()
    for a in arrs[1:]:
        v &= np.isfinite(a)
    if extra is not None:
        v &= extra
    return v


def ffmt(x: float) -> str:
    return f"{x:.12g}" if math.isfinite(x) else "nan"


def main() -> None:
    t0 = time.time()
    ap = argparse.ArgumentParser()
    ap.add_argument("outdir")
    ap.add_argument("--amended", action="store_true")
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    recs = parse_metadata()
    cxyz = load_coast_xyz()
    sets, dup_pairs, ver_pairs, anc_names, world_names = build_sets(recs, cxyz, args.amended)
    print(f"[rep] sets={len(sets)} W={len(world_names)} anc={len(anc_names)} "
          f"DUP={len(dup_pairs)} VER={len(ver_pairs)} ({time.time()-t0:.1f}s)", file=sys.stderr)

    with open(os.path.join(args.outdir, "sets.tsv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("set\tgenetic_id\n")
        for sn, mem in sets.items():
            for i in mem:
                f.write(f"{sn}\t{recs[i].gid}\n")

    n_snps, auto_idx, is_tv, b5, nb5, b10, nb10 = parse_snp()
    n_auto = int(auto_idx.size)

    accum: dict[str, list[int]] = dict(sets)
    base_mem = {dt: [i for i in sets["ANC.NC"] if anc_type(recs[i].gid) == dt] for dt in ("AG", "SG")}
    accum["BASE.AG"], accum["BASE.SG"] = base_mem["AG"], base_mem["SG"]
    anc_typed: dict[tuple[str, str], list[int]] = {}
    for g in anc_names:
        for dt in ("AG", "SG"):
            mem = [i for i in sets[g] if anc_type(recs[i].gid) == dt]
            if mem:
                accum[f"{g}@{dt}"] = mem
                anc_typed[(g, dt)] = mem

    keep_ind: set[int] = set(base_mem["AG"]) | set(base_mem["SG"])
    pa_amer = ["A.Mixe", "A.MesoOther", "A.Pima", "A.Surui", "A.Karitiana", "A.Mayan", "A.Piapoco", "A.Quechua"]
    pb_amer = ["B.Pima", "B.Surui", "B.Karitiana", "B.Mayan", "B.Piapoco"]
    for s in pa_amer + pb_amer:
        keep_ind.update(sets[s])
    for _, ia, ib, _ in dup_pairs:
        keep_ind.update((ia, ib))
    for _, ia, ib in ver_pairs:
        keep_ind.update((ia, ib))

    keep_sc = {"A.Mixe", "A.Amazon", "B.Pima", "B.Amazon", "BASE.AG", "BASE.SG"}
    freqs, igeno, ksum, kcnt = load_genos(len(recs), n_snps, auto_idx, accum, keep_ind, keep_sc)
    print(f"[rep] loaded genos ({time.time()-t0:.1f}s)", file=sys.stderr)

    pyri = freqs["B.Yoruba"]
    is_yri = np.isfinite(pyri) & (pyri > 0.05) & (pyri < 0.95)
    smasks = {"all": None, "tv": is_tv, "yri": is_yri}
    ifreq_cache = {i: ind_freq(g) for i, g in igeno.items()}

    f4_rows: list[tuple[str, str, str, str, str, str, int, float, float, float]] = []
    seen: set[tuple[str, str, str, str, str, str]] = set()
    comp_rows: list[tuple[str, str, float, float]] = []

    def add(p1n, p2n, p3n, p4n, snps, mask, res):
        key = (p1n, p2n, p3n, p4n, snps, mask)
        if key not in seen:
            seen.add(key)
            f4_rows.append((p1n, p2n, p3n, p4n, snps, mask, *res))

    def run_direct(p1n, p2n, p3n, p4n, p1=None, p2=None, p3=None, p4=None,
                   snps="all", mask="-", blocks=b5, nb=nb5):
        key = (p1n, p2n, p3n, p4n, snps, mask)
        if key in seen:
            return
        res = f4_direct(
            freqs[p1n] if p1 is None else p1,
            freqs[p2n] if p2 is None else p2,
            freqs[p3n] if p3 is None else p3,
            freqs[p4n] if p4 is None else p4,
            blocks, nb, smasks[snps],
        )
        add(p1n, p2n, p3n, p4n, snps, mask, res)

    # --- P & Support ---
    run_direct("A.Mbuti", "A.Papuan", "A.Mixe", "A.Amazon")
    run_direct("B.Mbuti", "B.Papuan", "B.Pima", "B.Amazon")
    run_direct("B.Mbuti", "B.Papuan", "B.Pima.heldout", "B.Amazon.heldout")
    for p, ref in (("A", "A.Mixe"), ("B", "B.Pima")):
        for comm in ("Surui", "Karitiana"):
            run_direct(f"{p}.Mbuti", f"{p}.Papuan", ref, f"{p}.{comm}")
        # LOO on Reference and Amazon
        for i in sets[ref]:
            p_loo = sub_freq(ksum[ref], kcnt[ref], [igeno[i]])
            run_direct(f"{p}.Mbuti", f"{p}.Papuan", f"{ref}-{recs[i].gid}", f"{p}.Amazon", p3=p_loo)
        for i in sets[f"{p}.Amazon"]:
            p_loo = sub_freq(ksum[f"{p}.Amazon"], kcnt[f"{p}.Amazon"], [igeno[i]])
            run_direct(f"{p}.Mbuti", f"{p}.Papuan", ref, f"{p}.Amazon-{recs[i].gid}", p4=p_loo)
    # 10 cM block-size check on P_A
    run_direct("A.Mbuti", "A.Papuan", "A.Mixe", "A.Amazon", mask="10cM", blocks=b10, nb=nb10)
    # Anchor D
    d_n, d_est, d_se, d_z = d_stat(freqs["A.Yoruba"], freqs["A.Papuan"], freqs["A.Mixe"], freqs["A.Surui"], b5, nb5)
    print(f"[rep] Anchor D(A.Yoruba,A.Papuan;A.Mixe,A.Surui): n={d_n} D={d_est:.6f} SE={d_se:.6f} Z={d_z:.3f}", file=sys.stderr)

    # --- A. Admixture check (LOCKED protocol) ---
    for p, ref, amer_list in (("A", "A.Mixe", pa_amer), ("B", "B.Pima", pb_amer)):
        amaz = f"{p}.Amazon"
        amaz_set = set(sets[amaz])
        seen_ind: set[int] = set()
        for sn in amer_list:
            for i in sets[sn]:
                if i in seen_ind:
                    continue
                seen_ind.add(i)
                gid = recs[i].gid
                if i in amaz_set:
                    u_name = f"{amaz}-{gid}"
                    p_u = sub_freq(ksum[amaz], kcnt[amaz], [igeno[i]])
                else:
                    u_name, p_u = amaz, freqs[amaz]
                pi = ifreq_cache[i]
                run_direct(f"{p}.Mbuti", f"{p}.French", u_name, f"{p}.ind.{gid}", p3=p_u, p4=pi)
                run_direct("Chimp", f"{p}.Yoruba", u_name, f"{p}.ind.{gid}", p3=p_u, p4=pi)

        # Group-level LOCKED equations
        m_names = [f"{p}.Mbuti", "Chimp", f"{p}.Papuan", f"{p}.French", f"{p}.Sardinian", f"{p}.Yoruba", ref, amaz]
        v = common_valid([freqs[k] for k in m_names])
        ctx = MaskCtx(v, b5, nb5)
        sl = {k: freqs[k][v] for k in m_names}
        mb, ch, pap, fr, sar, yor, rf, am = (sl[k] for k in m_names)
        mk = f"admix_{p}"

        def term(n1, n2, n3, n4, a1, a2, a3, a4):
            sj = ctx.bsums(a1, a2, a3, a4)
            s = float(sj.sum())
            th = s / ctx.nf
            tj = (s - sj) / ctx.dj
            est, se = ctx.jk(th, tj)
            z = est / se if (math.isfinite(se) and se > 0.0) else float("nan")
            add(n1, n2, n3, n4, "all", mk, (ctx.n, est, se, z))
            return th, tj

        g_ref, g_ref_j = term(f"{p}.Mbuti", f"{p}.Sardinian", amaz, ref, mb, sar, am, rf)
        g_fr, g_fr_j = term(f"{p}.Mbuti", f"{p}.Sardinian", amaz, f"{p}.French", mb, sar, am, fr)
        g_yor, g_yor_j = term(f"{p}.Mbuti", f"{p}.Sardinian", amaz, f"{p}.Yoruba", mb, sar, am, yor)
        h_ref, h_ref_j = term("Chimp", f"{p}.Mbuti", amaz, ref, ch, mb, am, rf)
        h_fr, h_fr_j = term("Chimp", f"{p}.Mbuti", amaz, f"{p}.French", ch, mb, am, fr)
        h_yor, h_yor_j = term("Chimp", f"{p}.Mbuti", amaz, f"{p}.Yoruba", ch, mb, am, yor)
        p_val, p_val_j = term(f"{p}.Mbuti", f"{p}.Papuan", ref, amaz, mb, pap, rf, am)
        pf, pf_j = term(f"{p}.Mbuti", f"{p}.Papuan", f"{p}.French", amaz, mb, pap, fr, am)
        py, py_j = term(f"{p}.Mbuti", f"{p}.Papuan", f"{p}.Yoruba", amaz, mb, pap, yor, am)

        det = g_fr * h_yor - g_yor * h_fr
        det_j = g_fr_j * h_yor_j - g_yor_j * h_fr_j
        ae = (g_ref * h_yor - g_yor * h_ref) / det
        ae_j = (g_ref_j * h_yor_j - g_yor_j * h_ref_j) / det_j
        aa = (g_fr * h_ref - g_ref * h_fr) / det
        aa_j = (g_fr_j * h_ref_j - g_ref_j * h_fr_j) / det_j
        padj = (p_val - ae * pf - aa * py) / (1.0 - ae - aa)
        padj_j = (p_val_j - ae_j * pf_j - aa_j * py_j) / (1.0 - ae_j - aa_j)
        for cname, est_v, vj in (("alpha_eur", ae, ae_j), ("alpha_afr", aa, aa_j), ("P_adj", padj, padj_j)):
            comp_rows.append((p, cname, *ctx.jk(est_v, vj)))

    # --- T. Technical checks ---
    pa_all, pb_all = paired_freqs([(a, b) for _, a, b, _ in dup_pairs], igeno, n_auto)
    pa_am, pb_am = paired_freqs([(a, b) for _, a, b, am in dup_pairs if am], igeno, n_auto)
    for L in ("A.Papuan", "ONG", "A.Han", "A.French"):
        run_direct("A.Mbuti", L, "DUP.SGDP", "DUP.NYGC", p3=pa_all, p4=pb_all)
        run_direct("A.Mbuti", L, "DUP.SGDP.Amazon", "DUP.NYGC.Amazon", p3=pa_am, p4=pb_am)
        for pid, ia, ib, _ in dup_pairs:
            run_direct("A.Mbuti", L, f"DUP.SGDP:{pid}", f"DUP.NYGC:{pid}", p3=ifreq_cache[ia], p4=ifreq_cache[ib])

    vag_all, vsg_all = paired_freqs([(a, b) for _, a, b in ver_pairs], igeno, n_auto)
    for L in ("A.Papuan", "A.Han"):
        run_direct("A.Mbuti", L, "VER.AG", "VER.SG", p3=vag_all, p4=vsg_all)
        for pid, ia, ib in ver_pairs:
            run_direct("A.Mbuti", L, f"VER.AG:{pid}", f"VER.SG:{pid}", p3=ifreq_cache[ia], p4=ifreq_cache[ib])

    # --- R. Robustness grid & extras ---
    for O in ("A.Mbuti", "A.Yoruba", "Chimp"):
        for A in ("A.Papuan", "A.Australian", "ONG", "JAR"):
            for R in ("A.Mixe", "A.MesoOther", "A.Pima"):
                for X in ("A.Surui", "A.Karitiana"):
                    for sc in ("all", "tv", "yri"):
                        run_direct(O, A, R, X, snps=sc)
    for O in ("B.Mbuti", "B.Yoruba", "Chimp"):
        for A in ("B.Papuan", "B.Nasioi", "ONG", "JAR"):
            for X in ("B.Surui", "B.Karitiana"):
                for sc in ("all", "tv", "yri"):
                    run_direct(O, A, "B.Pima", X, snps=sc)
    for p, ref, others in (
        ("A", "A.Mixe", ("A.Mayan", "A.Piapoco", "A.Quechua", "A.Pima", "A.MesoOther")),
        ("B", "B.Pima", ("B.Mayan", "B.Piapoco")),
    ):
        for i in sets[f"{p}.Amazon"]:
            run_direct(f"{p}.Mbuti", f"{p}.Papuan", ref, f"{p}.ind.{recs[i].gid}", p4=ifreq_cache[i])
        for X in others:
            run_direct(f"{p}.Mbuti", f"{p}.Papuan", ref, X)
        for sc in ("all", "yri"):
            run_direct(f"{p}.Mbuti", f"{p}.Papuan", f"{p}.Surui", f"{p}.Karitiana", snps=sc)

    # --- S. World ranking ---
    for w in world_names:
        run_direct("A.Mbuti", w, "A.Mixe", "A.Amazon")
        run_direct("B.Mbuti", w, "B.Pima", "B.Amazon")

    # --- L. Specificity and lineage ---
    for p, ref in (("A", "A.Mixe"), ("B", "B.Pima")):
        l_names = [f"{p}.Mbuti", f"{p}.Papuan", "ONG", f"{p}.Han", "Tianyuan", ref, f"{p}.Amazon"]
        mk = f"L_{p}"
        for sc, ex in (("all", None), ("tv", is_tv)):
            v = common_valid([freqs[k] for k in l_names], ex)
            ctx = MaskCtx(v, b5, nb5)
            sl = {k: freqs[k][v] for k in l_names}
            pairs_l = (
                [
                    (f"{p}.Mbuti", f"{p}.Papuan"), (f"{p}.Mbuti", f"{p}.Han"),
                    (f"{p}.Han", f"{p}.Papuan"), ("ONG", f"{p}.Papuan"),
                    (f"{p}.Mbuti", "Tianyuan"), ("Tianyuan", f"{p}.Papuan"),
                ]
                if sc == "all"
                else [(f"{p}.Mbuti", "Tianyuan"), ("Tianyuan", f"{p}.Papuan")]
            )
            for n1, n2 in pairs_l:
                add(n1, n2, ref, f"{p}.Amazon", sc, mk, ctx.f4_sl(sl[n1], sl[n2], sl[ref], sl[f"{p}.Amazon"]))

    # --- N. Ancient Americans ---
    p5_names = ("A.Mbuti", "A.Papuan", "ONG", "A.Han", "A.French")
    p5_valid = common_valid([freqs[k] for k in p5_names])
    base_pids = {dt: {recs[i].pid: i for i in base_mem[dt]} for dt in ("AG", "SG")}

    for g in anc_names:
        g_pids = {recs[i].pid for i in sets[g]}
        for dt in ("AG", "SG"):
            if (g, dt) not in anc_typed:
                continue
            ov = [base_pids[dt][pid] for pid in g_pids if pid in base_pids[dt]]
            if len(base_mem[dt]) - len(ov) < 10:
                continue
            b_name, g_name = f"BASE.{dt}-{g}", f"{g}@{dt}"
            p_b = sub_freq(ksum[f"BASE.{dt}"], kcnt[f"BASE.{dt}"], [igeno[i] for i in ov]) if ov else freqs[f"BASE.{dt}"]
            p_g = freqs[g_name]
            v_all = p5_valid & np.isfinite(p_b) & np.isfinite(p_g)
            mk = f"M:{g_name}"
            for sc, ex in (("all", None), ("tv", is_tv)):
                v = v_all if ex is None else (v_all & ex)
                ctx = MaskCtx(v, b5, nb5)
                mb, pap, ong, han, fr = (freqs[k][v] for k in p5_names)
                qb, qg = p_b[v], p_g[v]
                add("A.Mbuti", "A.Papuan", b_name, g_name, sc, mk, ctx.f4_sl(mb, pap, qb, qg))
                add("A.Mbuti", "ONG", b_name, g_name, sc, mk, ctx.f4_sl(mb, ong, qb, qg))
                if sc == "all":
                    add("A.Han", "A.Papuan", b_name, g_name, sc, mk, ctx.f4_sl(han, pap, qb, qg))
                    add("A.Mbuti", "A.French", b_name, g_name, sc, mk, ctx.f4_sl(mb, fr, qb, qg))

    # Coast vs inland (capture only)
    inl, cst = "REGION.ANDES_INLAND@AG", "REGION.ANDES_COAST@AG"
    if inl in freqs and cst in freqs:
        v_all = p5_valid & np.isfinite(freqs[inl]) & np.isfinite(freqs[cst])
        for sc, ex in (("all", None), ("tv", is_tv)):
            v = v_all if ex is None else (v_all & ex)
            ctx = MaskCtx(v, b5, nb5)
            mb, pap, _ong, han, fr = (freqs[k][v] for k in p5_names)
            qi, qc = freqs[inl][v], freqs[cst][v]
            add("A.Mbuti", "A.Papuan", inl, cst, sc, "C", ctx.f4_sl(mb, pap, qi, qc))
            if sc == "all":
                add("A.Han", "A.Papuan", inl, cst, sc, "C", ctx.f4_sl(han, pap, qi, qc))
                add("A.Mbuti", "A.French", inl, cst, sc, "C", ctx.f4_sl(mb, fr, qi, qc))

    # Descriptive ancient vs present-day
    p7_valid = p5_valid & np.isfinite(freqs["A.Mixe"]) & np.isfinite(freqs["A.Amazon"])
    for g in anc_names:
        v_all = p7_valid & np.isfinite(freqs[g])
        mk = f"N_desc:{g}"
        for sc, ex in (("all", None), ("tv", is_tv)):
            v = v_all if ex is None else (v_all & ex)
            ctx = MaskCtx(v, b5, nb5)
            mb, pap, ong, han, fr = (freqs[k][v] for k in p5_names)
            mx, am, qg = freqs["A.Mixe"][v], freqs["A.Amazon"][v], freqs[g][v]
            add("A.Mbuti", "A.Papuan", "A.Mixe", g, sc, mk, ctx.f4_sl(mb, pap, mx, qg))
            if sc == "all":
                add("A.Mbuti", "ONG", "A.Mixe", g, sc, mk, ctx.f4_sl(mb, ong, mx, qg))
                add("A.Mbuti", "A.Han", "A.Mixe", g, sc, mk, ctx.f4_sl(mb, han, mx, qg))
                add("A.Mbuti", "A.French", "A.Mixe", g, sc, mk, ctx.f4_sl(mb, fr, mx, qg))
                add("A.Mbuti", "A.Papuan", g, "A.Amazon", sc, mk, ctx.f4_sl(mb, pap, qg, am))

    # Write outputs
    with open(os.path.join(args.outdir, "f4.tsv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("P1\tP2\tP3\tP4\tsnps\tmask\tn_snps\tf4\tse\tZ\n")
        for p1n, p2n, p3n, p4n, sc, mk, ns, val, se, z in f4_rows:
            f.write(f"{p1n}\t{p2n}\t{p3n}\t{p4n}\t{sc}\t{mk}\t{ns}\t{ffmt(val)}\t{ffmt(se)}\t{ffmt(z)}\n")

    with open(os.path.join(args.outdir, "composites.tsv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("panel\tname\testimate\tse\n")
        for p, nm, est, se in comp_rows:
            f.write(f"{p}\t{nm}\t{ffmt(est)}\t{ffmt(se)}\n")

    print(f"[rep] Done: {len(f4_rows)} f4 rows, {len(comp_rows)} composites ({time.time()-t0:.1f}s)", file=sys.stderr)


if __name__ == "__main__":
    main()
