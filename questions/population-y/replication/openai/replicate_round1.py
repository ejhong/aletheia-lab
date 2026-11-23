#!/usr/bin/env python3
# replicate.py
#
# Interpretation choices:
# - Use the named panel sets in the panel table. The four MesoOther labels
#   contribute to the pooled set, not four additional reference populations.
#   ONG and JAR have no pipeline or assessment filter.
# - Person IDs are literal Individual IDs. Filter versions for eligibility
#   first, then select versions. For W, deduplicate globally across eligible
#   labels, then apply the two-person minimum. Among multiple preferred W
#   versions use SNP count. All residual version ties use annotation order.
# - DUP matches people within the specified community. If multiple versions
#   qualify on one side, take the highest-count one. Both paired pools are
#   ordered by the left-hand version, not independently by file order.
# - Missing numeric metadata cannot satisfy a numeric threshold. "Outside the
#   Americas" for W is nonmembership in the given political-entity list.
# - Greenland and Canada all go to NORTH; the 50-degree test is for USA.
#   Require coordinates only to the extent needed to resolve a regional
#   branch. Treat Hawaii and Rapa Nui as geographic island exclusions, not a
#   general longitude filter in the locked analysis. For the amendment, test
#   longitude whenever it is known; the bounds are inclusive.
# - Coastal segment subdivision counts use endpoint great-circle distance,
#   rounded up in units of 5 km. Interpolate across a longitude wrap by the
#   short way. Include the segment endpoints.
# - EARLY and VER apply their own eligibility rules, not the best-version or
#   region assignment of the cell analysis. BASE exclusions use person IDs
#   of the whole tested set, including when an EARLY version differs from the
#   version selected for the baseline.
# - R's supplementary American contrasts include alternate references and
#   the named community sets. Give both all and yri for the supplementary
#   contrasts. For N give both Papuan and ONG M1 on both all and tv; M3 and
#   MF are all-SNP statistics.
# - A common mask adds to, never replaces, the four-way data requirement.
#   Each T pool has its own paired-call rule, including for single persons.
# - Identical tests requested in several places share a row. The 10-cM test
#   is distinguished in the free-text mask field. Common mask text lists its
#   sets. P.unflagged uses ".unflagged" on both subset names.
# - Report the anchor's D and descriptive summaries to stderr so the three
#   TSV schemas remain fixed. Descending world ranks break exact ties by
#   label. Undefined estimates/SEs are nan; a nonzero value with exactly
#   zero SE has a signed infinite Z. No trimming/regularizing admixture
#   fractions or dropping ill-conditioned leave-block-out replicates.
# - No kinship or centring, and neither mode uses Amendment 2.

import argparse
import csv
import json
import math
import sys
from collections import defaultdict
from dataclasses import dataclass
from functools import lru_cache
from itertools import product
from pathlib import Path
from statistics import NormalDist

import numpy as np


ROOT = Path("data/aadr_v66.p1")
PATCH = ROOT / "v66.p1_1240K.aadr.patch.PUB"
ANNO = ROOT / "v66.p1_1240K.aadr.PUB.anno"
COAST = Path("data/naturalearth/ne_50m_coastline.geojson")
CARIB = set("Cuba|Dominican Republic|Puerto Rico|Bahamas|Haiti|Jamaica|Curacao|Guadeloupe|Saint Lucia|Barbados|Sint Maarten|Trinidad and Tobago".split("|"))
MESO = set("Mexico|Belize|Guatemala|Honduras|El Salvador|Nicaragua".split("|"))
ISTHMO = set("Costa Rica|Panama|Colombia|Venezuela|Guyana|Suriname|French Guiana".split("|"))
AMERICAS = CARIB | MESO | ISTHMO | set(
    "USA Canada Greenland Ecuador Peru Bolivia Brazil Chile Argentina Uruguay Paraguay".split()
)
PASS = {"Pass", "PROVISIONAL_PASS", "MERGE_PASS"}
MESO_LABELS = {"Mexico_Zapotec", "Nahua", "Mixtec_1", "Mixtec_2"}
PANEL_LABELS = {
    "A": "Mbuti Yoruba Han French Sardinian Papuan Australian Mixe Pima Mayan Piapoco Quechua Surui Karitiana".split(),
    "B": "Mbuti Yoruba Han French Sardinian Papuan Nasioi Pima Mayan Piapoco Surui Karitiana".split(),
}
SHARED = "Surui Karitiana Pima Mayan Piapoco".split()


def number(s):
    try:
        return float(s.replace(",", ""))
    except ValueError:
        return math.nan


@dataclass(slots=True)
class Record:
    gid: str
    person: str
    label: str
    date: float
    country: str
    lat: float
    lon: float
    data: str
    hits: float
    ok: bool

    def sgdp(self):
        return self.gid.startswith(("S_", "B_")) and self.gid.endswith(".DG")

    def typ(self):
        if self.gid.endswith(".AG"):
            return "AG"
        if self.gid.endswith(".SG") and ".AG" not in self.gid:
            return "SG"
        return ""


def metadata():
    with open(str(PATCH) + ".ind", encoding="utf-8-sig") as f:
        ind = [line.strip().split(None, 2) for line in f if line.strip()]
    csv.field_size_limit(16 * 1024 * 1024)
    rec = []
    with ANNO.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f, delimiter="\t")
        next(reader)
        for row in reader:
            if not row:
                continue
            gid, _, label = ind[len(rec)]
            if gid != row[0].strip():
                raise ValueError(f".ind/.anno order mismatch at {gid}")
            rec.append(Record(
                gid, row[2].strip(), label, number(row[10]), row[16].strip(),
                number(row[17]), number(row[18]), row[21].strip(),
                number(row[26]), row[47].strip() in PASS,
            ))
    if len(rec) != len(ind):
        raise ValueError("annotation length mismatch")
    return rec


def havpart(lat1, lon1, lat2, lon2):
    return (np.sin((lat2 - lat1) / 2) ** 2
            + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2)


def coast_classifier():
    with COAST.open(encoding="utf-8") as f:
        features = json.load(f)["features"]
    lats, lons = [], []
    for feature in features:
        geom = feature["geometry"]
        if geom["type"] == "LineString":
            lines = [geom["coordinates"]]
        elif geom["type"] == "MultiLineString":
            lines = geom["coordinates"]
        else:
            raise ValueError("unexpected coastline geometry")
        for line in lines:
            if not line:
                continue
            lon, lat = np.radians(np.asarray(line, dtype=float)[:, :2]).T
            h = havpart(lat[:-1], lon[:-1], lat[1:], lon[1:])
            dist = 12742.0 * np.arcsin(np.sqrt(np.clip(h, 0, 1)))
            steps = np.maximum(1, np.ceil(dist / 5).astype(np.int64))
            starts = steps.cumsum() - steps
            i = np.repeat(np.arange(steps.size), steps)
            t = (np.arange(i.size) - starts[i]) / steps[i]
            dl = (np.diff(lon) + np.pi) % (2 * np.pi) - np.pi
            lats.append(np.r_[lat[i] + t * np.diff(lat)[i], lat[-1]])
            lons.append(np.r_[lon[i] + t * dl[i], lon[-1]])
    lat = np.concatenate(lats)
    lon = np.concatenate(lons)
    angle = 75.0 / 6371.0

    @lru_cache(None)
    def coastal(y, x):
        y, x = math.radians(y), math.radians(x)
        near = np.abs(lat - y) <= angle + 1e-14
        return bool(np.any(havpart(y, x, lat[near], lon[near]) <= math.sin(angle / 2) ** 2))

    return coastal


def region(r, coastal):
    c, y, x = r.country, r.lat, r.lon
    if c in {"Greenland", "Canada"}:
        return "NORTH"
    if c == "USA":
        if 18 <= y <= 23 and -161 <= x <= -154:
            return None
        if y >= 50:
            return "NORTH"
        if y < 50 and math.isfinite(x):
            return "NAM_WEST" if x < -100 else "NAM_EAST"
    if c in MESO:
        return "MESO"
    if c in CARIB:
        return "CARIB"
    if c in ISTHMO:
        return "ISTHMO_NSA"
    if c in {"Brazil", "Paraguay", "Uruguay"}:
        return "EAST_SA"
    if c == "Argentina":
        if y <= -30 or y >= -21 or x >= -64:
            return "SOUTH_CONE"
        if -30 < y < -21 and x < -64:
            return "ANDES_INLAND"
    if c == "Bolivia":
        return "ANDES_INLAND"
    if c == "Chile" and -28 <= y <= -26 and -110 <= x <= -108:
        return None
    if c == "Chile" and y <= -30:
        return "SOUTH_CONE"
    if c in {"Ecuador", "Peru", "Chile"} and math.isfinite(y) and math.isfinite(x):
        return "ANDES_COAST" if coastal(y, x) else "ANDES_INLAND"
    return None


def build_sets(rec, amended):
    sets = {}
    ids = range(len(rec))

    def best(indices, prefer=False):
        chosen = {}
        scores = {}
        for i in indices:
            r = rec[i]
            score = (prefer and r.sgdp(), r.hits if math.isfinite(r.hits) else -math.inf, -i)
            if r.person not in scores or score > scores[r.person]:
                scores[r.person] = score
                chosen[r.person] = i
        return chosen

    for panel, labels in PANEL_LABELS.items():
        pool = [i for i, r in enumerate(rec) if r.ok and
                (r.sgdp() if panel == "A" else
                 r.gid.startswith("HGDP") and r.gid.endswith(".DG"))]
        for label in labels:
            sets[f"{panel}.{label}"] = tuple(i for i in pool if rec[i].label == label)
        if panel == "A":
            sets["A.MesoOther"] = tuple(i for i in pool if rec[i].label in MESO_LABELS)
        sets[panel + ".Amazon"] = tuple(i for i in pool if rec[i].label in {"Surui", "Karitiana"})
    for name in ("ONG", "JAR"):
        sets[name] = tuple(i for i in ids if rec[i].label == name)
    for name, gid in (("Chimp", "Chimp.REF"), ("Tianyuan", "Tianyuan.AG.BY.AA")):
        sets[name] = tuple(i for i in ids if rec[i].gid == gid)
    pairs = []
    for label in SHARED:
        a, b = (best(sets[f"{p}.{label}"]) for p in "AB")
        pairs.extend((a[k], b[k]) for k in a.keys() & b.keys())
    pairs.sort()
    sets["DUP.SGDP"] = tuple(a for a, b in pairs)
    sets["DUP.NYGC"] = tuple(b for a, b in pairs)
    dup_people = {rec[a].person for a, b in pairs}
    for name in ("B.Amazon", "B.Pima"):
        sets[name + ".heldout"] = tuple(i for i in sets[name] if rec[i].person not in dup_people)

    world = best((i for i, r in enumerate(rec)
                  if r.date == 0 and r.country not in AMERICAS and r.ok
                  and r.data in {"Shotgun", "Shotgun.diploid"} and r.hits >= 900000
                  and r.label not in {"Mbuti", "MbutiPygmy"}
                  and not any(s in r.label for s in
                              ("-o", "_o", "Ignore", "QCremove", "Discovery", "outlier"))),
                 prefer=True)
    groups = defaultdict(list)
    for i in sorted(world.values()):
        groups[rec[i].label].append(i)
    for label, members in groups.items():
        if len(members) >= 2:
            sets["W." + label] = tuple(members)

    eligible = [i for i, r in enumerate(rec) if r.country in AMERICAS and
                (not amended or ("Norse" not in r.label and
                                 (not math.isfinite(r.lon) or -170 <= r.lon <= -30)))]
    anc = [i for i in eligible if rec[i].ok and rec[i].date >= 500 and rec[i].hits >= 100000]
    coastal = coast_classifier()
    ancient = defaultdict(list)
    for i in sorted(best(anc).values()):
        r = rec[i]
        reg = region(r, coastal)
        if reg is None:
            continue
        period = "EARLY" if r.date >= 8200 else "MID" if r.date >= 4200 else "LATE"
        ancient[f"CELL.{reg}.{period}"].append(i)
        ancient["REGION." + reg].append(i)
        if reg in {"ANDES_COAST", "ANDES_INLAND", "EAST_SA", "SOUTH_CONE", "ISTHMO_NSA"}:
            ancient["ANC.SA"].append(i)
        elif reg in {"NAM_WEST", "NAM_EAST", "MESO"}:
            ancient["ANC.NC"].append(i)
    sets.update((k, tuple(v)) for k, v in ancient.items())
    for i in eligible:
        if rec[i].date >= 9000 and rec[i].hits >= 250000:
            sets["EARLY." + rec[i].gid] = (i,)
    ag, sg = (best(i for i in anc if rec[i].hits >= 400000 and rec[i].typ() == t)
              for t in ("AG", "SG"))
    people = sorted(ag.keys() & sg.keys(), key=ag.__getitem__)
    sets["VER.AG"] = tuple(ag[k] for k in people)
    sets["VER.SG"] = tuple(sg[k] for k in people)
    for name, members in sets.items():
        if not members:
            raise ValueError(f"empty required set: {name}")
    return sets


@dataclass(frozen=True, slots=True)
class Test:
    pops: tuple
    snps: str
    common: tuple
    cm: int
    kind: str


class Plan:
    def __init__(self):
        self.tests = {}
        self.paired = {}
        self.admix = {}
        self.grid = defaultdict(list)
        self.world = defaultdict(dict)
        self.lineage = defaultdict(dict)
        self.m1 = {}
        self.diagnostics = defaultdict(dict)
        self.primary = {}

    def add(self, p1, p2, p3, p4, snps="all", common=(), cm=5, kind="f4"):
        t = Test((p1, p2, p3, p4), snps, tuple(common), cm, kind)
        self.tests[t] = None
        return t


def design(rec, sets):
    plan = Plan()
    add = plan.add
    ancient = sorted(s for s in sets if s.startswith(("CELL.", "REGION.", "ANC.", "EARLY.")))
    worlds = sorted(s for s in sets if s.startswith("W."))
    for panel in "AB":
        def q(s):
            return f"{panel}.{s}"

        mb, pap, ref, am, fr, yor, sar, han = map(q, (
            "Mbuti", "Papuan", "Mixe" if panel == "A" else "Pima", "Amazon",
            "French", "Yoruba", "Sardinian", "Han",
        ))
        prim = (mb, pap, ref, am)
        plan.primary[panel] = add(*prim)
        if panel == "B":
            add(mb, pap, ref + ".heldout", am + ".heldout")
        else:
            add(*prim, cm=10)
            anchor = (yor, pap, ref, q("Surui"))
            plan.anchor = add(*anchor), add(*anchor, kind="Dden")
        for s in ("Surui", "Karitiana"):
            add(mb, pap, ref, q(s))

        for s in (ref, am):
            for i in sets[s]:
                drop = s + "-" + rec[i].gid
                sets[drop] = tuple(j for j in sets[s] if i != j)
                add(mb, pap, drop if s == ref else ref, drop if s == am else am)

        refs = [ref] + ([q("MesoOther"), q("Pima")] if panel == "A" else [])
        others = list(map(q, ["Mayan", "Piapoco", "Surui", "Karitiana"]
                          + (["Quechua"] if panel == "A" else [])))
        for i in sorted({i for s in refs + others for i in sets[s]}):
            one = q("ind." + rec[i].gid)
            sets[one] = (i,)
            u = am + "-" + rec[i].gid if i in sets[am] else am
            plan.diagnostics[panel][i] = add(mb, fr, u, one), add("Chimp", yor, u, one)
            if i in sets[am]:
                for cl in ("all", "yri"):
                    add(mb, pap, ref, one, cl)

        mask = (mb, "Chimp", pap, fr, sar, yor, ref, am)
        terms = [add(x, y, am, s, common=mask)
                 for x, y in ((mb, sar), ("Chimp", mb)) for s in (ref, fr, yor)]
        terms += [add(mb, pap, s, am, common=mask) for s in (ref, fr, yor)]
        plan.admix[panel] = terms

        for pops in product(
            (mb, yor, "Chimp"), (pap, q("Australian" if panel == "A" else "Nasioi"), "ONG", "JAR"),
            refs, (q("Surui"), q("Karitiana")),
        ):
            for cl in ("all", "tv", "yri"):
                plan.grid[panel].append(add(*pops, cl))
        for cl in ("all", "yri"):
            for x in refs[1:] + others + [am]:
                add(mb, pap, ref, x, cl)
            add(mb, pap, q("Surui"), q("Karitiana"), cl)
        for w in worlds:
            plan.world[panel][w] = add(mb, w, ref, am)

        mask = (mb, pap, "ONG", han, "Tianyuan", ref, am)
        for name, p1, p2 in (
            ("P_L", mb, pap), ("Han", mb, han), ("L3", han, pap),
            ("L2", "ONG", pap), ("L1", mb, "Tianyuan"), ("L4", "Tianyuan", pap),
        ):
            plan.lineage[panel][name] = add(p1, p2, ref, am, common=mask)
            if name in ("L1", "L4"):
                plan.lineage[panel][name + ".tv"] = add(p1, p2, ref, am, "tv", mask)

    for left, right, probes in (
        ("DUP.SGDP", "DUP.NYGC", ("A.Papuan", "ONG", "A.Han", "A.French")),
        ("VER.AG", "VER.SG", ("A.Papuan", "A.Han")),
    ):
        pairs = list(zip(sets[left], sets[right], strict=True))
        subgroups = [("", pairs)]
        if left.startswith("DUP"):
            subgroups.append((".Amazon", [(i, j) for i, j in pairs if i in sets["A.Amazon"]]))
        for i, j in pairs:
            if rec[i].person != rec[j].person:
                raise ValueError("unmatched pair")
            subgroups.append((":" + rec[i].person, [(i, j)]))
        for suffix, subset in subgroups:
            l, r = left + suffix, right + suffix
            sets[l] = tuple(i for i, j in subset)
            sets[r] = tuple(j for i, j in subset)
            plan.paired[l], plan.paired[r] = r, l
            for probe in probes:
                add("A.Mbuti", probe, l, r)

    mb, pap, ong, han, fr = modern = ("A.Mbuti", "A.Papuan", "ONG", "A.Han", "A.French")
    ref, am = "A.Mixe", "A.Amazon"
    for g in ancient:
        mask = modern + (ref, am, g)
        for probe in (pap, ong, han, fr):
            add(mb, probe, ref, g, common=mask)
        add(mb, pap, ref, g, "tv", mask)
        add(mb, pap, g, am, common=mask)
        people = {rec[i].person for i in sets[g]}
        for typ in ("AG", "SG"):
            subset = tuple(i for i in sets[g] if rec[i].typ() == typ)
            if not subset:
                continue
            gt = g + "@" + typ
            sets[gt] = subset
            base = tuple(i for i in sets["ANC.NC"] if rec[i].typ() == typ
                         and rec[i].person not in people)
            if len(base) < 10:
                continue
            b = "BASE." + typ + "-" + g
            sets[b] = base
            mask = modern + (b, gt)
            for cl in ("all", "tv"):
                test = add(mb, pap, b, gt, cl, mask)
                if cl == "all":
                    plan.m1[gt] = (all(rec[i].ok for i in subset), test)
                add(mb, ong, b, gt, cl, mask)
            add(han, pap, b, gt, common=mask)
            add(mb, fr, b, gt, common=mask)
    inland, coast = ("REGION.ANDES_" + x + "@AG" for x in ("INLAND", "COAST"))
    mask = modern + (inland, coast)
    add(mb, pap, inland, coast, common=mask)
    add(mb, pap, inland, coast, "tv", mask)
    add(han, pap, inland, coast, common=mask)
    add(mb, fr, inland, coast, common=mask)
    return plan


def snp_metadata():
    s = np.loadtxt(str(PATCH) + ".snp", usecols=(1, 2, 4, 5),
                   dtype=[("c", "i4"), ("pos", "f8"), ("a", "S4"), ("b", "S4")])
    c = s["c"]
    auto = (c >= 1) & (c <= 22)
    a, b = np.char.upper(s["a"]), np.char.upper(s["b"])
    tv = ~(((a == b"A") & (b == b"G")) | ((a == b"G") & (b == b"A")) |
           ((a == b"C") & (b == b"T")) | ((a == b"T") & (b == b"C")))
    blocks = {}
    for cm in (5, 10):
        bins = np.floor(s["pos"][auto] / (cm / 100.0)).astype(np.int64)
        keys = np.column_stack((c[auto], bins))
        pairs, inv = np.unique(keys, axis=0, return_inverse=True)
        ix = np.zeros(len(c), dtype=np.intp)
        ix[auto] = inv.reshape(-1)
        blocks[cm] = ix, len(pairs)
    return auto, tv, blocks


@dataclass(slots=True)
class Estimate:
    m: np.ndarray              # counts of nonempty blocks in global block order
    v: np.ndarray              # full estimate followed by leave-one-block-outs
    se: float

    @property
    def theta(self):
        return self.v[0]

    @property
    def z(self):
        with np.errstate(invalid="ignore", divide="ignore"):
            return float(np.divide(self.theta, self.se))


def jack(m, v):
    v = np.asarray(v, dtype=np.float64)
    g = m.size
    if g < 2:
        return Estimate(m, v, math.nan)
    n = float(m.sum())
    h = n / m
    t, loo = v[0], v[1:]
    with np.errstate(invalid="ignore", over="ignore"):
        tj = g * t - np.dot(1 - m / n, loo)
        tau = h * t - (h - 1) * loo
        se = np.sqrt(np.sum((tau - tj) ** 2 / (h - 1)) / g)
    return Estimate(m, v, float(se))


def frequencies(dose, obs, rows, mates):
    if mates is None:
        if len(rows) == 1:
            i = rows[0]
            return np.where(obs[i], 0.5 * dose[i], np.nan)
        count = obs[rows].sum(axis=0, dtype=np.uint32)
        total = dose[rows].sum(axis=0, dtype=np.uint32)
    else:
        both = obs[rows] & obs[mates]
        count = both.sum(axis=0, dtype=np.uint32)
        total = (dose[rows] * both).sum(axis=0, dtype=np.uint32)
    with np.errstate(invalid="ignore", divide="ignore"):
        return (0.5 * total) / count


def compute(tests, sets, paired, meta, nind):
    if not tests:
        return {}
    auto, tv, blocks = meta
    ns = auto.size
    groups = defaultdict(list)
    names = set()
    for t in tests:
        needed = tuple(sorted(set(t.pops).union(t.common)))
        groups[t.cm, t.snps, needed].append(t)
        names.update(needed)
        if t.snps == "yri":
            names.add("B.Yoruba")
    specs = {}
    for name in names:
        if name in paired:
            specs[name] = sets[name], sets[paired[name]]
        else:
            specs[name] = tuple(sorted(sets[name])), None
    indices = sorted({i for rows, mates in specs.values() for i in rows}
                     | {i for _, mates in specs.values() if mates is not None for i in mates})
    local = {i: j for j, i in enumerate(indices)}
    specids = {sp: j for j, sp in enumerate(dict.fromkeys(specs.values()))}
    name_id = {name: specids[sp] for name, sp in specs.items()}
    rowspec = [(np.asarray([local[i] for i in rows], dtype=np.intp),
                None if mates is None else np.asarray([local[i] for i in mates], dtype=np.intp))
               for rows, mates in specids]

    path = str(PATCH) + ".geno"
    with open(path, "rb") as f:
        header = f.read(48).split(b"\x00", 1)[0].split()
    if header[0] != b"TGENO" or (int(header[1]), int(header[2])) != (nind, ns):
        raise ValueError("unexpected TGENO header")
    record_bytes = (ns + 3) // 4
    mm = np.memmap(path, mode="r", offset=48, dtype=np.uint8, shape=(nind, record_bytes))
    packed = mm[np.asarray(indices, dtype=np.intp)]
    del mm
    lut = (np.arange(256, dtype=np.uint8)[:, None] >>
           np.array([6, 4, 2, 0], dtype=np.uint8)) & 3
    counts = {k: np.zeros(blocks[k[0]][1], dtype=np.int64) for k in groups}
    sums = {t: np.zeros(blocks[t.cm][1], dtype=np.float64) for t in tests}

    width = 16384
    for lo in range(0, ns, width):
        hi = min(ns, lo + width)
        sl = slice(lo, hi)
        if not np.any(auto[sl]):
            continue
        raw = lut[packed[:, lo // 4:(hi + 3) // 4]].reshape(len(indices), -1)[:, :hi-lo]
        obs = raw != 3
        dose = np.where(obs, raw, np.uint8(0))
        del raw
        vals = [frequencies(dose, obs, rows, mates) for rows, mates in rowspec]
        del dose, obs
        p = {name: vals[j] for name, j in name_id.items()}
        finite = [np.isfinite(v) for v in vals]
        ok = {name: finite[j] for name, j in name_id.items()}
        classes = {"all": auto[sl], "tv": auto[sl] & tv[sl]}
        if "B.Yoruba" in p:
            y = p["B.Yoruba"]
            classes["yri"] = auto[sl] & (y > 0.05) & (y < 0.95)

        for key, terms in groups.items():
            cm, snps, needed = key
            valid = classes[snps].copy()
            for name in needed:
                valid &= ok[name]
            block_ids, nb = blocks[cm]
            b = block_ids[sl][valid]
            if not b.size:
                continue
            counts[key] += np.bincount(b, minlength=nb)
            for t in terms:
                p1, p2, p3, p4 = (p[name] for name in t.pops)
                if t.kind == "f4":
                    v = (p1 - p2) * (p3 - p4)
                else:
                    v = (p1 + p2 - 2*p1*p2) * (p3 + p4 - 2*p3*p4)
                sums[t] += np.bincount(b, weights=v[valid], minlength=nb)
        del p, vals, finite, ok
    results = {}
    for k, terms in groups.items():
        used = counts[k] > 0
        m = counts[k][used]
        n = m.sum()
        for t in terms:
            s = sums[t][used]
            total = s.sum()
            with np.errstate(invalid="ignore", divide="ignore"):
                v = np.r_[total / n, (total - s) / (n - m)]
            results[t] = jack(m, v)
    return results


def composite_results(plan, results):
    rows = []
    for panel, terms in plan.admix.items():
        m = results[terms[0]].m
        if not all(np.array_equal(results[t].m, m) for t in terms):
            raise ValueError("admixture terms do not share block weights")
        gr, gf, gy, hr, hf, hy, prim, pf, py = (results[t].v for t in terms)
        with np.errstate(invalid="ignore", divide="ignore", over="ignore"):
            det = gf * hy - gy * hf
            eur = (gr * hy - gy * hr) / det
            afr = (gf * hr - gr * hf) / det
            adj = (prim - eur * pf - afr * py) / (1 - eur - afr)
        for name, v in (("alpha_eur", eur), ("alpha_afr", afr), ("P_adj", adj)):
            est = jack(m, v)
            rows.append((panel, name, est.theta, est.se))
    return rows


def unflagged(plan, rec, sets, results):
    new = []
    for panel, diagnostics in plan.diagnostics.items():
        flagged = {i for i, ts in diagnostics.items() if any(results[t].z >= 3 for t in ts)}
        if not flagged:
            continue
        mb, pap, ref, am = plan.primary[panel].pops
        r, a = ref + ".unflagged", am + ".unflagged"
        sets[r], sets[a] = (tuple(i for i in sets[s] if i not in flagged) for s in (ref, am))
        if sets[r] and sets[a]:
            new.append(plan.add(mb, pap, r, a))
    return new


def describe(plan, results):
    def report(*args):
        print(*args, sep="\t", file=sys.stderr)

    num, den = (results[t] for t in plan.anchor)
    with np.errstate(invalid="ignore", divide="ignore"):
        d = jack(num.m, num.v / den.v)
    report("anchor.D", d.theta, d.se, d.z)
    for panel in "AB":
        cells = plan.grid[panel]
        groups = defaultdict(list)
        groups["overall"].extend(cells)
        for t in cells:
            for axis, value in zip(("O", "A", "R", "X", "snps"), (*t.pops, t.snps)):
                groups[axis + "=" + value].append(t)
        for name, ts in groups.items():
            report("R.medians(Z,f4)", panel, name,
                   np.median([results[t].z for t in ts]),
                   np.median([results[t].theta for t in ts]))
        worlds = plan.world[panel]

        def ranks(by):
            def key(w):
                v = getattr(results[worlds[w]], by)
                return (math.isnan(v), -v if not math.isnan(v) else 0, w)
            return {w: rank for rank, w in enumerate(sorted(worlds, key=key), 1)}

        rz, rf = ranks("z"), ranks("theta")
        for w in sorted(worlds, key=rz.__getitem__):
            report("S.ranks(Z,f4)", panel, w, rz[w], rf[w])
        scale = results[plan.lineage[panel]["P_L"]].theta
        for name, t in plan.lineage[panel].items():
            est = results[t]
            ci = est.theta + np.array([-1.96, 1.96]) * est.se
            with np.errstate(divide="ignore", invalid="ignore"):
                report("L.CI,CI/P_L", panel, name, *ci, *(ci / scale))
    m = sum(ok for ok, _ in plan.m1.values())
    primary = results[plan.primary["A"]].theta
    if m and primary > 0:
        zstar = NormalDist().inv_cdf(1 - 0.05 / m)
        for name, (_, t) in plan.m1.items():
            report("N.detection_threshold", name, zstar * results[t].se / primary)


def write_table(path, columns, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n")
        writer.writerow(columns)
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("outdir", type=Path)
    parser.add_argument("--amended", action="store_true")
    args = parser.parse_args()
    out = args.outdir
    out.mkdir(parents=True, exist_ok=True)
    rec = metadata()
    sets = build_sets(rec, args.amended)
    write_table(out / "sets.tsv", ("set", "genetic_id"),
                ((s, rec[i].gid) for s in sorted(sets) for i in sets[s]))
    plan = design(rec, sets)
    meta = snp_metadata()
    results = compute(plan.tests, sets, plan.paired, meta, len(rec))
    extra = unflagged(plan, rec, sets, results)
    results.update(compute(extra, sets, plan.paired, meta, len(rec)))

    def f4rows():
        for t in plan.tests:
            if t.kind != "f4":
                continue
            mask = ",".join(t.common)
            if t.cm != 5:
                mask = (mask + ";" if mask else "") + f"{t.cm}cM"
            est = results[t]
            yield (*t.pops, t.snps, mask or "-", int(est.m.sum()), est.theta, est.se, est.z)

    write_table(out / "f4.tsv",
                ("P1", "P2", "P3", "P4", "snps", "mask", "n_snps", "f4", "se", "Z"),
                f4rows())
    write_table(out / "composites.tsv", ("panel", "name", "estimate", "se"),
                composite_results(plan, results))
    describe(plan, results)


if __name__ == "__main__":
    main()
