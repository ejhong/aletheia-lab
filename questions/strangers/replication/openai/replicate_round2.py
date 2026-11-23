#!/usr/bin/env python3
# Usage (from questions/strangers): python replicate.py OUTDIR
#
# Interpretations where a choice is needed:
# - Filter versions before deduplicating, use stripped case-sensitive Individual
#   IDs, and keep the winning records in input-line order (not dictionary order).
#   A missing Individual ID doesn't identify two records as the same person.
# - For EHG labels ignore terminal assay suffixes. Present-day reference labels
#   are matched exactly in .ind. Pool by reference set, deduplicate by Individual
#   ID, prefer panel A, and break ties within a panel by file order.
# - For EHG prefer the ordinary ancient eligibility/deduplication rules; if
#   only deduplication without the eligibility filters gives the specified 15,
#   use those 15. Exclude EHG identities from the tested roster.
# - Either coordinate absent means coordinates unavailable. Sites use Python
#   round on the parsed degree values. Longitude bounds are inclusive.
#   For type SG/TW, "no .AG" means nowhere in the Genetic ID.
# - Rank all candidates BEFORE applying the two 1500 limits, using unrounded
#   distances. A missing site cannot have neighbours.
# - Both clean-American sets are subsets of the tested roster. Baseline size
#   for fallback is measured after exclusion of self; exclude self also in
#   the fallback. Site mates are not excluded from a baseline.
# - D1/D2, the four E's, and the four G's have individual masks. Only A and
#   its five fitted controls require the joint mask. Centre S after combining
#   its left contrasts (equivalent to combining their centred estimates).
# - In clipping, test ALL finite fit candidates against the scale from the
#   last fit's inliers, allowing re-entry. Three refits after the initial fit.
# - Use raw full-mask estimates, not bias-corrected estimates, for reporting,
#   Z numerators, regression and the centring guard. Ignore empty blocks.
#   Undefined statistics cannot pass. Count applicable tests, not finite Z's,
#   for Bonferroni; the conjunction D1/D2 is one test in this count.
# - A hits row identifies a passing person/test/direction triple. Don't
#   suppress a second passing test or direction. Print the single threshold
#   to stderr, not to an extra output file.

import os
for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
           "BLIS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"

import csv
import math
import re
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from statistics import NormalDist

import numpy as np


ROOT = Path("data/aadr_v66.p1")
PREFIX = "v66.p1_1240K.aadr"
PATCH = ROOT / (PREFIX + ".patch.PUB")
AM = set(("USA|Canada|Greenland|Mexico|Belize|Guatemala|Honduras|El Salvador|"
          "Nicaragua|Costa Rica|Panama|Colombia|Venezuela|Ecuador|Peru|Bolivia|"
          "Brazil|Chile|Argentina|Uruguay|Paraguay|Guyana|Suriname|French Guiana|"
          "Cuba|Dominican Republic|Puerto Rico|Bahamas|Haiti|Jamaica|Curacao|"
          "Guadeloupe|Saint Lucia|Barbados|Sint Maarten|Trinidad and Tobago").split("|"))
NA = set("Karitiana Surui Mixe Pima Piapoco Quechua".split())
MODERN = NA | set("Mbuti Yoruba French Sardinian Han Papuan Mandenka Japanese Australian".split())
EHG = {"Russia_Karelia_Mesolithic", "Russia_Karelia_Mesolithic_HG"}
CONTROL = ("EHG", "Han", "Sardinian", "Papuan", "Yoruba")
FOREIGN = ("French", "Yoruba", "Han", "Papuan")
NAMES = ["S", "D1", "D2"] + [p + r for p in ("E_", "G_") for r in FOREIGN]
TYPES = ("AG", "SG", "TW", "other")
PASS = {"Pass", "PROVISIONAL_PASS", "MERGE_PASS"}
WORKERS = min(18, len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity")
              else (os.cpu_count() or 1))


def number(s):
    try:
        x = float(s.strip().replace(",", ""))
        return x if math.isfinite(x) else math.nan
    except ValueError:
        return math.nan


@dataclass(slots=True)
class Row:
    i: int
    gid: str
    pid: str
    pub: str
    group: str
    date: float
    lat: float
    lon: float
    site: tuple | None
    american: bool
    typ: str
    count: float
    qc: str


def read_rows():
    with open(str(PATCH) + ".ind", encoding="utf-8-sig") as f:
        inds = [line.split() for line in f if line.strip()]
    rows = []
    csv.field_size_limit(16 << 20)
    with (ROOT / (PREFIX + ".PUB.anno")).open(encoding="utf-8-sig", newline="") as f:
        rd = csv.reader(f, delimiter="\t")
        next(rd)
        for i, (ind, a) in enumerate(zip(inds, rd, strict=True)):
            gid, _, group = ind
            if a[0].strip() != gid:
                raise ValueError(f".anno/.ind mismatch at individual {i}: {gid}, {a[0]}")
            pid = a[2].strip()
            if pid in ("", "..", "NA", "n/a"):
                pid = "\0" + gid
            lat, lon = number(a[17]), number(a[18])
            site = ((round(lat, 2), round(lon, 2))
                    if math.isfinite(lat) and math.isfinite(lon) else None)
            c = a[16].strip()
            island = ((c == "Chile" and lon < -80) or (c == "Ecuador" and lon < -85)
                      or (lat < 30 and lon < -130))
            side = c in AM and (site is None or (c in {"USA", "Canada", "Greenland"}
                                                 and lat >= 50)
                                or (-170 <= lon <= -30 and not island))
            typ = "other"
            if gid.endswith(".AG"):
                typ = "AG"
            elif ".AG" not in gid and gid.endswith((".SG", ".TW")):
                typ = gid[-2:]
            rows.append(Row(i, gid, pid, a[6].strip(), group, number(a[10]), lat, lon,
                            site, side, typ, number(a[26]), a[47].strip()))
    return rows


def label(r):
    return re.sub(r"(?:\.(?:AG|SG|DG|TW))+$", "", r.group)


def eligible(r):
    return r.date >= 500 and r.qc in PASS and r.count >= 100000


def dedup(rs):
    best = {}
    for r in rs:
        p = best.get(r.pid)
        if p is None or (math.isfinite(r.count) and
                         (not math.isfinite(p.count) or r.count > p.count)):
            best[r.pid] = r
    return sorted(best.values(), key=lambda r: r.i)


def rosters(rows):
    ehg_all = [r for r in rows if label(r) in EHG]
    ehg = dedup(r for r in ehg_all if eligible(r))
    if len(ehg) != 15 and len(raw_ehg := dedup(ehg_all)) == 15:
        ehg = raw_ehg
    exclude = {r.pid for r in ehg_all}
    tested = dedup(r for r in rows if eligible(r) and r.pid not in exclude)

    modern = {}
    for r in rows:
        if r.group not in MODERN or r.qc not in PASS or not r.gid.endswith(".DG"):
            continue
        if r.gid.startswith(("S_", "B_")):
            rank = 0
        elif r.gid.startswith("HGDP"):
            rank = 1
        else:
            continue
        name = "NA" if r.group in NA else r.group
        key = (name, r.pid)
        if key not in modern or rank < modern[key][0]:
            modern[key] = (rank, name, r.i)
    refs = defaultdict(list)
    for _, name, i in sorted(modern.values(), key=lambda item: item[2]):
        refs[name].append(i)
    refs["EHG"] = [r.i for r in ehg]
    for name in (MODERN - NA) | {"NA", "EHG"}:
        if not refs[name]:
            raise ValueError(f"No members for reference {name}; check pipeline/label convention")
    clean = {t: [r.i for r in tested if r.american and r.lat < 50
                 and "Norse" not in r.group and r.typ == t] for t in TYPES}
    refs["ancient_NA"] = [i for i in clean["AG"] if rows[i].count >= 500000]
    return tested, dict(refs), clean


def neighbours(tested):
    pools = defaultdict(list)
    result = [[] for r in tested]
    for j, r in enumerate(tested):
        if r.site is not None:
            pools[r.american, r.typ].append(j)
    for pool in pools.values():
        if len(pool) < 21:
            continue
        group = [tested[j] for j in pool]
        lat = np.radians([r.lat for r in group])
        lon = np.radians([r.lon for r in group])
        coslat = np.cos(lat)
        date = np.array([r.date for r in group])
        sites = {p: k for k, p in enumerate(dict.fromkeys(r.site for r in group))}
        site = np.array([sites[r.site] for r in group])
        for k, j in enumerate(pool):
            h = (np.sin((lat - lat[k]) * .5)**2
                 + coslat * coslat[k] * np.sin((lon - lon[k]) * .5)**2)
            km = 12742.0 * np.arcsin(np.sqrt(np.clip(h, 0., 1.)))
            yrs = np.abs(date - date[k])
            score = km + yrs
            score[site == site[k]] = np.inf
            top = np.argsort(score, kind="stable")[:20]
            if np.isfinite(score[top[-1]]) and np.all(km[top] <= 1500) and np.all(yrs[top] <= 1500):
                result[j] = [group[q].i for q in top]
    return result


def snps():
    chrom, pos = np.loadtxt(str(PATCH) + ".snp", usecols=(1, 2), unpack=True)
    auto = np.flatnonzero((chrom >= 1) & (chrom <= 22))
    ch = chrom[auto].astype(np.int32)
    tile = np.floor(pos[auto] / .05).astype(np.int64)
    order = np.lexsort((tile, ch))
    ch, tile, auto = ch[order], tile[order], auto[order]
    starts = np.r_[0, 1 + np.flatnonzero((ch[1:] != ch[:-1]) | (tile[1:] != tile[:-1]))]
    # Split only between blocks; each local reduction then has ordinary
    # contiguous segments and no SNP-length bincount index is needed.
    chunks = []
    k = 0
    while k < len(starts):
        end = int(np.searchsorted(starts, starts[k] + 98304))
        stop = starts[end] if end < len(starts) else len(auto)
        chunks.append((slice(starts[k], stop), slice(k, end), starts[k:end] - starts[k]))
        k = end
    return len(chrom), auto, len(starts), chunks


def threaded(fn, it):
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        for _ in pool.map(fn, it):
            pass


def genotypes(needed, ni, ns, auto):
    path = Path(str(PATCH) + ".geno")
    with path.open("rb") as f:
        hdr = f.read(48).split(b"\0", 1)[0].split()
    stride = (ns + 3) // 4
    if (hdr[0] != b"TGENO" or tuple(map(int, hdr[1:3])) != (ni, ns)
            or path.stat().st_size != 48 + stride * ni):
        raise ValueError("Unexpected TGENO header/length")
    mm = np.memmap(path, mode="r", dtype="u1", shape=(ni, stride), offset=48)
    code = (np.arange(256)[:, None] >> np.array([6, 4, 2, 0])) & 3
    # Neighbour sum in uint16: high bits = call count, low 6 = ALT1 dosage
    # sum (at most 40). Zero is the missing code, including at haploid calls.
    lut = np.where(code == 3, 0, 64 + code).astype("u1")
    raw = np.empty((len(needed), len(auto)), dtype="u1")
    take = (slice(auto[0], auto[-1]+1) if np.all(np.diff(auto) == 1) else auto)

    def unpack(k):
        raw[k] = lut[mm[needed[k]]].reshape(-1)[take]

    threaded(unpack, range(len(needed)))
    return raw


def totals(raw, ix, chunks):
    al, n = np.empty((2, raw.shape[1]), dtype=np.int32)
    for s, _, _ in chunks:
        g = raw[ix, s]
        al[s] = np.sum(g & 3, axis=0, dtype=np.int32)
        n[s] = np.sum(g != 0, axis=0, dtype=np.int32)
    return al, n


def split_finite(x):
    ok = np.isfinite(x)
    return np.where(ok, x, 0.), ok


def red(a, starts):
    return np.add.reduceat(a, starts, axis=-1, dtype=np.float64)


def parts(out, a, b, ok, starts):
    # Both a and b are finite placeholders even outside ok.
    bm = b * ok
    out[0] = red(ok, starts)
    out[1] = red(a * ok, starts)
    out[2] = red(bm, starts)
    out[3] = red(a * bm, starts)


def summarize(sums):
    m, sa, sb, sp = sums[:, sums[0] > 0]
    g = len(m)
    if not g:
        return math.nan, math.nan, math.nan
    n, a, b, p = (v.sum() for v in (m, sa, sb, sp))
    plain = p / n
    cent = plain - (a/n) * (b/n)
    if g < 2:
        return plain, math.nan, cent
    rem = n - m
    leave = (p - sp) / rem
    leave_c = leave - ((a-sa)/rem) * ((b-sb)/rem)
    # theta_J = theta + sum((1-w)*(theta-leave)); tau = theta +
    # (h-1)*(theta-leave). Work relative to theta to limit cancellation.
    def se(theta, deleted):
        delta = theta - deleted
        hm1 = rem / m
        shift = np.sum((rem/n) * delta)
        return np.sqrt(np.mean(np.square(hm1 * delta - shift) / hm1))
    err = se(plain, leave)
    # The guard only uses the full centred estimate, not its jackknife Z.
    _cent_err = se(cent, leave_c)
    return plain, (plain / err if err > 0 else math.nan), cent


def fitted(mat):
    y, predictors = mat[:, 0], mat[:, 1:]
    finite = np.isfinite(mat).all(axis=1)
    use = finite.copy()
    if not np.any(use):
        raise ValueError("No valid fit candidates")
    for iteration in range(4):
        u = np.linalg.lstsq(predictors[use], y[use], rcond=None)[0]
        if iteration == 3:
            break
        d = np.abs(y - predictors @ u)
        new = finite & (d <= 4. * 1.4826 * np.median(d[use]))
        if np.array_equal(use, new) or not np.any(new):
            break
        use = new
    return u


def scan(tested, neigh, refs, clean, ni):
    ns, auto, nb, chunks = snps()
    needed = sorted({r.i for r in tested}.union(*refs.values()))
    ix = {i: k for k, i in enumerate(needed)}
    raw = genotypes(needed, ni, ns, auto)

    def indices(ids):
        return np.array([ix[i] for i in ids], dtype=np.intp)

    freq = {}
    for name, ids in refs.items():
        al, n = totals(raw, indices(ids), chunks)
        freq[name] = np.divide(.5 * al, n, out=np.full(n.shape, np.nan), where=n > 0)
    cleanids = {t: set(ids) for t, ids in clean.items()}
    basetot = {t: totals(raw, indices(ids), chunks) for t, ids in clean.items()}
    nearix = [indices(ids) for ids in neigh]
    old = [j for j, r in enumerate(tested) if not r.american and neigh[j]]
    slot = {j: k for k, j in enumerate(old)}
    # For each old-world fit row: block sums of 1, P-X, the six left
    # contrasts, and the six products. These suffice for EXACTLY the same
    # post-fit jackknife as forming the fixed-u residual at each SNP.
    cube = np.empty((len(old), 14, nb))
    mb = freq["Mbuti"]
    joint, jok = split_finite(np.stack([mb-freq[r] for r in ("NA",) + CONTROL]))
    jok = np.all(jok, axis=0)
    dl = [split_finite(freq[r]-freq["NA"]) for r in ("Han", "EHG")]
    fl = [split_finite(mb-freq[r]) for r in FOREIGN]
    mb, mok = split_finite(mb)
    result = np.full((len(tested), len(NAMES), 3), np.nan)

    def worker(j):
        r = tested[j]
        neigh_ix = nearix[j]
        has = len(neigh_ix) != 0
        buf = np.empty((len(NAMES), 4, nb))
        if r.american:
            t = r.typ
            if t == "other" or len(cleanids[t]) - (r.i in cleanids[t]) < 20:
                t = "AG"
            remove = r.i in cleanids[t]
            ba, bn = basetot[t]
        elif has:
            blocks = cube[slot[j]]
        for s, bs, starts in chunks:
            g = raw[ix[r.i], s]
            xc = g != 0
            dosage = g & 3
            x = .5 * dosage
            if has:
                total = np.sum(raw[neigh_ix, s], axis=0, dtype=np.uint16)
                count = total >> 6
                d = .5 * (total & 63) / np.maximum(1, count) - x
                valid = xc & (count > 0)
            if r.american:
                cnt = bn[s] - xc if remove else bn[s]
                al = ba[s] - dosage if remove else ba[s]
                base = .5 * al / np.maximum(1, cnt) - x
                bok = xc & (cnt > 0)
                for k, (f, fv) in enumerate(fl):
                    if has:
                        parts(buf[3+k, :, bs], f[s], d, fv[s] & valid, starts)
                    parts(buf[7+k, :, bs], f[s], base, fv[s] & bok, starts)
            else:
                left = mb[s] - x
                ok = xc & mok[s]
                for k, (f, fv) in enumerate(dl):
                    parts(buf[1+k, :, bs], left, f[s], ok & fv[s], starts)
                if has:
                    ok = jok[s] & valid
                    dm = d * ok
                    a = joint[:, s]
                    blocks[0, bs] = red(ok, starts)
                    blocks[1, bs] = red(dm, starts)
                    blocks[2:8, bs] = red(a * ok, starts)
                    blocks[8:14, bs] = red(a * dm, starts)
        which = range(3 if has else 7, 11) if r.american else (1, 2)
        for k in which:
            result[j, k] = summarize(buf[k])

    threaded(worker, range(len(tested)))
    n = cube[:, 0].sum(axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        u = fitted(cube[:, 8:14].sum(axis=2) / n[:, None])
    w = np.r_[1., -u]
    for j, c in zip(old, cube):
        result[j, 0] = summarize(np.stack((c[0], w @ c[2:8], c[1], w @ c[8:14])))
    return result, u


def write(path, header, records):
    with path.open("w", encoding="utf-8", newline="") as f:
        wr = csv.writer(f, delimiter="\t", lineterminator="\n")
        wr.writerow(header)
        wr.writerows(records)


def main(out):
    rows = read_rows()
    tested, refs, clean = rosters(rows)
    neigh = neighbours(tested)
    family = sum((1 + bool(ids)) * (4 if r.american else 1)
                 for r, ids in zip(tested, neigh))
    zstar = -NormalDist().inv_cdf(.05 / family)
    print(f"tested={len(tested)} american={sum(r.american for r in tested)} "
          f"family={family} Z*={zstar:.12g}", file=sys.stderr)
    result, u = scan(tested, neigh, refs, clean, len(rows))
    out.mkdir(parents=True, exist_ok=True)
    write(out/"people.tsv", ("genetic_id", "side", "type", "neighbours"),
          ((r.gid, "american" if r.american else "elsewhere", r.typ,
            ",".join(rows[i].gid for i in ids)) for r, ids in zip(tested, neigh)))
    write(out/"fit.tsv", ("control", "coefficient"), zip(CONTROL, u))
    header = ["genetic_id"] + [f"{name}_{col}" for name in NAMES for col in ("f4", "Z")]
    def scanrows():
        for r, stats, ns in zip(tested, result, neigh):
            active = (range(3 if ns else 7, 11) if r.american else range(0 if ns else 1, 3))
            yield [r.gid] + [format(val, ".15g") if k in active else ""
                             for k, triple in enumerate(stats) for val in triple[:2]]
    write(out/"scan.tsv", header, scanrows())
    passed = ((result[:, :, 1] >= zstar) & (result[:, :, 2] >= .5 * result[:, :, 0]))
    def hits():
        for r, p in zip(tested, passed):
            if r.american:
                for offset, test in ((3, "neighbours"), (7, "absolute")):
                    for k, toward in enumerate(FOREIGN):
                        if p[offset+k]:
                            yield r.gid, test, toward
            else:
                if p[0]:
                    yield r.gid, "neighbours", "NA"
                if p[1] and p[2]:
                    yield r.gid, "absolute", "NA"
    write(out/"hits.tsv", ("genetic_id", "test", "toward"), hits())


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: python replicate.py OUTDIR")
    main(Path(sys.argv[1]))
