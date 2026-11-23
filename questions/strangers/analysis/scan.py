#!/usr/bin/env python3
"""The scan of protocol.md: every ancient person against their neighbours.

    .venv/bin/python analysis/scan.py cache [--blind]      # unpack the genotypes needed into data/cache/
    .venv/bin/python analysis/scan.py work I N [--blind]   # block sums for people I mod N (run N of these)
    .venv/bin/python analysis/scan.py final [--blind]      # fit, thresholds, hits, checks, centres, made-up strangers
    .venv/bin/python analysis/scan.py all [--blind]        # the three steps, with 12 workers

--blind shuffles every genome's SNPs independently (a pipeline test that cannot show a real result) and writes to
results_blind/. Run from questions/strangers.
"""
import collections
import csv
import json
import math
import pathlib
import statistics
import subprocess
import sys

import numpy as np

import f4lib

HERE = pathlib.Path(__file__).resolve().parent
Q = HERE.parent
D = Q / "data" / "aadr_v66.p1"
PREFIX = "v66.p1_1240K.aadr.patch.PUB"
BLIND = "--blind" in sys.argv
TAG = "blind" if BLIND else "real"
CACHE = Q / "data" / "cache" / f"strangers_{TAG}"
OUT = Q / ("results_blind" if BLIND else "results")

CONTROLS = ["EHG", "Han", "Sardinian", "Papuan", "Yoruba"]          # for people elsewhere
FOREIGN = ["French", "Yoruba", "Han", "Papuan"]                      # for people on the American side
SECOND = {"French": "Sardinian", "Yoruba": "Mandenka", "Han": "Japanese", "Papuan": "Australian"}
EUROPE = {"United Kingdom", "Hungary", "Italy", "Austria", "Spain", "Germany", "Denmark", "France", "Poland", "Czechia"}
CENTRES = {
    "EGYPT": ("elsewhere", lambda p: p["group"].startswith("Egypt_")),
    "MESOPOTAMIA": ("elsewhere", lambda p: p["group"].startswith("Iraq_") or p["group"].startswith("Syria_EMBA")),
    "CHINA_EARLY": ("elsewhere", lambda p: p["group"].startswith("China_") and any(
        w in p["group"] for w in ("Longshan", "Shang", "Yangshao", "Dawenkou", "Erlitou")) and "-o" not in p["group"]),
    "MESOAMERICA": ("american", lambda p: p["group"] in ("Mexico_LateClassic", "Honduras_Copan_Classic_Maya")),
    "ANDES": ("american", lambda p: (p["group"].startswith("Peru_") or p["group"].startswith("Bolivia_")) and p["date"] < 4200),
}


# ---------------------------------------------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------------------------------------------

def load_people():
    people = []
    with open(HERE / "people.tsv") as f:
        for p in csv.DictReader(f, delimiter="\t"):
            p["row"], p["nsnp"], p["date"] = int(p["row"]), int(p["nsnp"]), float(p["date"])
            p["date_sd"] = float(p["date_sd"]) if p["date_sd"] not in ("", "None") else None
            p["pool"] = [int(x) for x in p["pool"].split(",")] if p["pool"] else []
            people.append(p)
    return people


def load_refs():
    refs = collections.OrderedDict()
    with open(HERE / "refs.tsv") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            refs.setdefault(r["set"], []).append(int(r["row"]))
    return refs


class Store:
    """The unpacked genotypes of every ancient person (block-sorted SNP order), and reference frequencies."""

    def __init__(self):
        meta = json.loads((CACHE / "meta.json").read_text())
        self.n_snp, self.rows = meta["n_snp"], meta["rows"]
        self.pos = {r: i for i, r in enumerate(self.rows)}
        self.G = np.memmap(CACHE / "geno.u8", dtype=np.uint8, mode="r", shape=(len(self.rows), self.n_snp))
        z = np.load(CACHE / "refs.npz")
        self.freq = {k: z[k] for k in z.files if k not in ("starts", "tv")}
        self.starts, self.tv = z["starts"], z["tv"]
        self.n_blocks = self.starts.size

    def x(self, row):
        """A person's allele frequency (0, 0.5, 1) with NaN where missing."""
        g = np.asarray(self.G[self.pos[row]])
        return np.where(g == 3, np.nan, g * 0.5).astype(np.float32)

    def pool(self, rows):
        tot = np.zeros(self.n_snp, dtype=np.float32)
        cnt = np.zeros(self.n_snp, dtype=np.float32)
        for r in rows:
            g = np.asarray(self.G[self.pos[r]])
            ok = g != 3
            tot += np.where(ok, g, 0)
            cnt += ok
        with np.errstate(invalid="ignore", divide="ignore"):
            return np.where(cnt > 0, tot / (2 * cnt), np.nan).astype(np.float32)

    def sums(self, v):
        """Per-block sums of an array (zeros where a SNP is not used)."""
        return np.add.reduceat(v, self.starts, axis=-1)


def build_cache():
    people, refs = load_people(), load_refs()
    snps = f4lib.Snps(D / f"{PREFIX}.snp")
    geno = f4lib.Geno(D / f"{PREFIX}.geno", snps)
    order = np.argsort(snps.block, kind="stable")                  # SNPs grouped by jackknife block
    block = snps.block[order]
    starts = np.flatnonzero(np.r_[True, block[1:] != block[:-1]])
    CACHE.mkdir(parents=True, exist_ok=True)

    def read(row):
        g = geno.genotypes(row)[order]
        if BLIND:
            g = np.random.default_rng(1000 + row).permutation(g)
        return g

    rows = [p["row"] for p in people]
    G = np.memmap(CACHE / "geno.u8", dtype=np.uint8, mode="w+", shape=(len(rows), order.size))
    for i, r in enumerate(rows):
        G[i] = read(r)
        if i % 2000 == 0:
            print(f"cache {i}/{len(rows)}", flush=True)
    G.flush()
    freq = {}
    for name, rws in refs.items():
        tot = np.zeros(order.size)
        cnt = np.zeros(order.size)
        for r in rws:
            g = read(r)
            ok = g != 3
            tot += np.where(ok, g, 0)
            cnt += ok
        with np.errstate(invalid="ignore", divide="ignore"):
            freq[name] = np.where(cnt > 0, tot / (2 * cnt), np.nan).astype(np.float32)
    np.savez(CACHE / "refs.npz", starts=starts, tv=snps.transversion[order], **freq)
    (CACHE / "meta.json").write_text(json.dumps({"n_snp": int(order.size), "rows": rows}))
    print("cache written:", len(rows), "people,", order.size, "SNPs,", starts.size, "blocks")


# ---------------------------------------------------------------------------------------------------------------
# Statistics from block sums
# ---------------------------------------------------------------------------------------------------------------

def jack(n_b, s_b, l_b, d_b):
    """Plain and centred f4 with weighted block-jackknife standard errors, from per-block sums.

    n_b: SNPs per block; s_b: sum of left*right; l_b: sum of left; d_b: sum of right. Blocks with no SNPs are dropped.
    The centred value is the mean of the products minus the product of the means, recomputed for every deletion.
    Returns {"f4", "se", "z", "c", "c_se", "c_z", "n"}.
    """
    keep = n_b > 0
    n_b, s_b, l_b, d_b = n_b[keep], s_b[keep], l_b[keep], d_b[keep]
    g, n = n_b.size, n_b.sum()
    nan = float("nan")
    if g < 2:
        return {"f4": nan, "se": nan, "z": nan, "c": nan, "c_se": nan, "c_z": nan, "n": int(n)}
    S, L, Dd = s_b.sum(), l_b.sum(), d_b.sum()
    nm, h = n - n_b, n / n_b
    out = {"n": int(n)}
    for name, theta, tm in (("f4", S / n, (S - s_b) / nm),
                            ("c", S / n - (L / n) * (Dd / n), (S - s_b) / nm - ((L - l_b) / nm) * ((Dd - d_b) / nm))):
        tj = g * theta - np.sum((1 - n_b / n) * tm)
        tau = h * theta - (h - 1) * tm
        se = math.sqrt(np.sum((tau - tj) ** 2 / (h - 1)) / g)
        out[name], out[("se" if name == "f4" else "c_se")] = float(theta), float(se)
        out[("z" if name == "f4" else "c_z")] = float(theta / se) if se > 0 else nan
    return out


def left_sides(store, names):
    """Left-hand differences (reference - Mbuti is the direction of interest; stored as Mbuti - reference) and
    the SNPs where Mbuti and every named reference have data."""
    m = store.freq["Mbuti"]
    valid = ~np.isnan(m)
    for k in names:
        valid &= ~np.isnan(store.freq[k])
    L = np.stack([np.where(valid, m - store.freq[k], 0).astype(np.float32) for k in names])
    return L, valid


def contrast_sums(store, L, valid, x, base, extra_mask=None):
    """Block sums for f4(Mbuti, ref_k; base, x), one row per reference: array [n, d, s_1..s_k, l_1..l_k]."""
    ok = valid & ~np.isnan(x) & ~np.isnan(base)
    if extra_mask is not None:
        ok &= extra_mask
    diff = np.where(ok, base - x, 0).astype(np.float32)
    n = store.sums(ok.astype(np.float32))
    return np.vstack([n[None, :], store.sums(diff)[None, :], store.sums(L * diff), store.sums(np.where(ok, L, 0))]).astype(np.float64)


def likeness_sums(store, x, na="NA", extra_mask=None):
    """Block sums for D1 = f4(Mbuti, X; Han, NA) and D2 = f4(Mbuti, X; EHG, NA): two arrays [n, s, l, d]."""
    m, ref = store.freq["Mbuti"], store.freq[na]
    out = []
    for other in ("Han", "EHG"):
        w = store.freq[other] - ref
        ok = ~np.isnan(m) & ~np.isnan(w) & ~np.isnan(x)
        if extra_mask is not None:
            ok &= extra_mask
        left = np.where(ok, m - x, 0).astype(np.float32)
        right = np.where(ok, w, 0).astype(np.float32)
        out.append(np.vstack([store.sums(ok.astype(np.float32)), store.sums(left * right), store.sums(left),
                              store.sums(right)]).astype(np.float64))
    return out


def one(blk, k, total):
    """The k-th contrast of a contrast_sums array holding `total` references."""
    return jack(blk[0], blk[2 + k], blk[2 + total + k], blk[1])


def residual(blk, u):
    """S = A - sum u_k B_k from a contrast_sums array whose first reference is NA and the rest are the controls."""
    k = 1 + len(u)
    w = np.r_[1.0, -np.asarray(u)]
    return jack(blk[0], w @ blk[2:2 + k], w @ blk[2 + k:2 + 2 * k], blk[1])


class Baselines:
    """Clean ancient American baselines per data type, with a person's own genotype taken out when they belong."""

    def __init__(self, store, refs):
        self.store, self.members, self.tot, self.cnt = store, {}, {}, {}
        for t in ("AG", "SG", "TW"):
            rows = refs.get(f"BASE_AM.{t}", [])
            self.members[t] = set(rows)
            tot = np.zeros(store.n_snp, dtype=np.float32)
            cnt = np.zeros(store.n_snp, dtype=np.float32)
            for r in rows:
                g = np.asarray(store.G[store.pos[r]])
                ok = g != 3
                tot += np.where(ok, g, 0)
                cnt += ok
            self.tot[t], self.cnt[t] = tot, cnt

    def freq(self, t, row):
        tot, cnt = self.tot[t], self.cnt[t]
        if row in self.members[t]:
            g = np.asarray(self.store.G[self.store.pos[row]])
            ok = g != 3
            tot, cnt = tot - np.where(ok, g, 0), cnt - ok
        with np.errstate(invalid="ignore", divide="ignore"):
            return np.where(cnt > 0, tot / (2 * cnt), np.nan).astype(np.float32)


# ---------------------------------------------------------------------------------------------------------------
# Workers
# ---------------------------------------------------------------------------------------------------------------

def work(part, n_parts):
    store, people, refs = Store(), load_people(), load_refs()
    LE, vE = left_sides(store, ["NA"] + CONTROLS)
    LA, vA = left_sides(store, FOREIGN)
    base = Baselines(store, refs)
    flat = {}
    mine = [p for i, p in enumerate(people) if i % n_parts == part]
    for j, p in enumerate(mine):
        x, row = store.x(p["row"]), p["row"]
        if p["side"] == "elsewhere":
            d1, d2 = likeness_sums(store, x)
            flat[f"{row}.d1"], flat[f"{row}.d2"] = d1, d2
            if p["pool"]:
                flat[f"{row}.b"] = contrast_sums(store, LE, vE, x, store.pool(p["pool"]))
        else:
            flat[f"{row}.g"] = contrast_sums(store, LA, vA, x, base.freq(p["baseline"], row))
            if p["pool"]:
                flat[f"{row}.b"] = contrast_sums(store, LA, vA, x, store.pool(p["pool"]))
        if j % 200 == 0:
            print(f"part {part}: {j}/{len(mine)}", flush=True)
    (CACHE / "parts").mkdir(exist_ok=True)
    np.savez(CACHE / "parts" / f"part{part}.npz", **flat)


# ---------------------------------------------------------------------------------------------------------------
# Final stage
# ---------------------------------------------------------------------------------------------------------------

def robust_fit(A, B):
    """Least squares A ~ B.u with no intercept. Refit up to three times, each time on the people whose residual is
    within 4 robust standard deviations of zero (1.4826 x the median absolute residual of those fitted last)."""
    keep = np.ones(A.size, dtype=bool)
    u = np.zeros(B.shape[1])
    for _ in range(4):
        u, *_ = np.linalg.lstsq(B[keep], A[keep], rcond=None)
        res = A - B @ u
        sd = 1.4826 * np.median(np.abs(res[keep]))
        new = np.abs(res) <= 4 * sd
        if np.array_equal(new, keep):
            break
        keep = new
    return u, int(keep.sum())


def passes(j, zstar):
    """The decision rule for one statistic: plain Z at least Z*, and the centred estimate at least half the plain one."""
    return bool(j["z"] >= zstar and j["c"] >= 0.5 * j["f4"])


def contam_flag(p):
    def interval(txt):
        try:
            a, b = txt.strip("[]").split(",")
            return float(a), float(b)
        except ValueError:
            return None
    flags = []
    for key in ("angsd", "hapconx"):
        iv = interval(p[key])
        if iv and iv[0] > 0.02:
            flags.append(f"X {iv[0]:.3f}-{iv[1]:.3f}")
    iv = interval(p["mt"])
    if iv and iv[1] < 0.95:
        flags.append(f"mt {iv[0]:.2f}-{iv[1]:.2f}")
    if "contam" in p["warn"].lower():
        flags.append("warning")
    return "; ".join(flags)


def final():
    store, people, refs = Store(), load_people(), load_refs()
    OUT.mkdir(exist_ok=True)
    blocks = {}
    for f in sorted((CACHE / "parts").glob("part*.npz")):
        z = np.load(f)
        for k in z.files:
            blocks[k] = z[k]
    kE, kA = 1 + len(CONTROLS), len(FOREIGN)
    elsewhere = [p for p in people if p["side"] == "elsewhere"]
    american = [p for p in people if p["side"] == "american"]
    else_b = [p for p in elsewhere if f"{p['row']}.b" in blocks]
    amer_b = [p for p in american if f"{p['row']}.b" in blocks]

    # Fit the controls on the plain estimates of everyone elsewhere who has neighbours.
    est = np.array([[one(blocks[f"{p['row']}.b"], k, kE)["f4"] for k in range(kE)] for p in else_b])
    u, n_fit = robust_fit(est[:, 0], est[:, 1:])
    # One family: neighbour tests and absolute tests together.
    n_tests = len(else_b) + kA * len(amer_b) + len(elsewhere) + kA * len(american)
    zstar = statistics.NormalDist().inv_cdf(1 - 0.05 / n_tests)

    res, hits = {}, []
    for p in people:
        row, r = p["row"], {}
        if p["side"] == "elsewhere":
            r["D1"], r["D2"] = jack(*blocks[f"{row}.d1"]), jack(*blocks[f"{row}.d2"])
            if passes(r["D1"], zstar) and passes(r["D2"], zstar):
                hits.append((p, "absolute", "NA"))
            if f"{row}.b" in blocks:
                r["S"] = residual(blocks[f"{row}.b"], u)
                r["A"] = one(blocks[f"{row}.b"], 0, kE)
                if passes(r["S"], zstar):
                    hits.append((p, "neighbours", "NA"))
        else:
            for k, name in enumerate(FOREIGN):
                r[f"G_{name}"] = one(blocks[f"{row}.g"], k, kA)
                if passes(r[f"G_{name}"], zstar):
                    hits.append((p, "absolute", name))
                if f"{row}.b" in blocks:
                    r[f"E_{name}"] = one(blocks[f"{row}.b"], k, kA)
                    if passes(r[f"E_{name}"], zstar):
                        hits.append((p, "neighbours", name))
        res[row] = r
    hit_rows = {p["row"] for p, _, _ in hits}
    site_hits = collections.Counter(p["site"] for p in people if p["row"] in hit_rows and p["site"])

    # ---- robustness of each hit: transversions only, and a second reference ----
    base = Baselines(store, refs)

    def recompute(p, test, ref, na="NA", mask=None, second=None):
        """The statistic behind a hit, optionally on transversions or with the second reference."""
        x = store.x(p["row"])
        if p["side"] == "elsewhere":
            if test == "absolute":
                return [jack(*b) for b in likeness_sums(store, x, na=na, extra_mask=mask)]
            L, valid = left_sides(store, [na] + CONTROLS)
            return [residual(contrast_sums(store, L, valid, x, store.pool(p["pool"]), mask), u)]
        L, valid = left_sides(store, [second or ref])
        b = store.pool(p["pool"]) if test == "neighbours" else base.freq(p["baseline"], p["row"])
        return [one(contrast_sums(store, L, valid, x, b, mask), 0, 1)]

    hit_table = []
    for p, test, ref in hits:
        r = res[p["row"]]
        if p["side"] == "elsewhere":
            main = [r["D1"], r["D2"]] if test == "absolute" else [r["S"]]
            tv = recompute(p, test, ref, mask=store.tv)
            alt = recompute(p, test, ref, na="ANCIENT_AMERICAN")
        else:
            main = [r[("G_" if test == "absolute" else "E_") + ref]]
            tv = recompute(p, test, ref, mask=store.tv)
            alt = recompute(p, test, ref, second=SECOND[ref])
        tv_ok = all(t["f4"] >= 0.5 * m["f4"] and t["z"] >= 2 for t, m in zip(tv, main))
        alt_ok = all(a["f4"] >= 0.5 * m["f4"] for a, m in zip(alt, main))
        late = p["date"] - 2 * (p["date_sd"] or 0) < 458
        hit_table.append({
            "genetic_id": p["gid"], "group": p["group"], "entity": p["entity"], "lat": p["lat"], "lon": p["lon"], "site": p["site"],
            "date_bp": int(p["date"]), "date_sd": p["date_sd"], "date_method": p["method"], "type": p["type"], "side": p["side"],
            "snps": p["nsnp"], "test": test, "toward": ref,
            "estimate": "; ".join(f"{m['f4']:.6f}" for m in main), "Z": "; ".join(f"{m['z']:.1f}" for m in main),
            "centred_Z": "; ".join(f"{m['c_z']:.1f}" for m in main),
            "tv_ratio": "; ".join(f"{t['f4'] / m['f4']:.2f}" for t, m in zip(tv, main)), "tv_Z": "; ".join(f"{t['z']:.1f}" for t in tv),
            "second_ratio": "; ".join(f"{a['f4'] / m['f4']:.2f}" for a, m in zip(alt, main)),
            "robust": bool(tv_ok and alt_ok), "flag_label": bool("Norse" in p["group"] or "-o" in p["group"] or "_o" in p["group"]),
            "flag_date_may_postdate_1492": bool(late), "flag_contamination": contam_flag(p),
            "pool_hits": sum(1 for q in p["pool"] if q in hit_rows), "site_hits": site_hits.get(p["site"], 1) if p["site"] else 1,
            "sex": p["sex"], "mt_haplogroup": p["mt_hg"], "y_haplogroup": p["y_hg"], "library": p["library"],
            "mt_match": p["mt"], "x_contam_angsd": p["angsd"], "x_contam_hapconx": p["hapconx"], "warnings": p["warn"],
            "publication": p["pub"]})

    # ---- the centres: member-by-member contrasts added up ----
    centres = {}
    for name, (side, test) in CENTRES.items():
        members = [p for p in people if p["side"] == side and test(p)]
        entry = {"people": len(members), "with_neighbours": 0, "tests": {}}
        with_b = [p for p in members if f"{p['row']}.b" in blocks]
        entry["with_neighbours"] = len(with_b)
        if len(with_b) >= 2:
            total = sum(blocks[f"{p['row']}.b"] for p in with_b)
            if side == "elsewhere":
                j = residual(total, u)
                entry["tests"]["S"] = {"estimate": j["f4"], "Z": round(j["z"], 2), "centred_Z": round(j["c_z"], 2)}
            else:
                for k, ref in enumerate(FOREIGN):
                    j = one(total, k, kA)
                    entry["tests"][f"E_{ref}"] = {"estimate": j["f4"], "Z": round(j["z"], 2), "centred_Z": round(j["c_z"], 2)}
                for oname, (oside, otest) in CENTRES.items():
                    orows = [q["row"] for q in people if q["side"] == "elsewhere" and oside == "elsewhere" and otest(q)]
                    if len(orows) < 2:
                        continue
                    store.freq["_centre"] = store.pool(orows)
                    L, valid = left_sides(store, ["_centre"])
                    tot = sum(contrast_sums(store, L, valid, store.x(p["row"]), store.pool(p["pool"])) for p in with_b)
                    j = one(tot, 0, 1)
                    entry["tests"][f"toward_{oname}"] = {"estimate": j["f4"], "Z": round(j["z"], 2), "centred_Z": round(j["c_z"], 2),
                                                         "people_in_old_centre": len(orows)}
        centres[name] = entry
    n_centre_tests = sum(len(c["tests"]) for c in centres.values())
    z_centre = statistics.NormalDist().inv_cdf(1 - 0.05 / max(1, n_centre_tests))

    # ---- made-up strangers: foreign ancestry dropped in by whole 5 cM blocks ----
    rng = np.random.default_rng(41)
    lengths = np.diff(np.r_[store.starts, store.n_snp])
    donors_am = {t: [r for r in refs.get(f"BASE_AM.{t}", []) if next(q for q in people if q["row"] == r)["nsnp"] >= 500000]
                 for t in ("AG", "SG", "TW")}
    donors_eu = {t: [p["row"] for p in elsewhere if p["type"] == t and p["nsnp"] >= 500000 and p["entity"] in EUROPE]
                 for t in ("AG", "SG", "TW")}
    LE, vE = left_sides(store, ["NA"] + CONTROLS)
    LF, vF = left_sides(store, ["French"])
    power = {}
    for label, group, donors in (("native_american_ancestry_elsewhere", else_b, donors_am),
                                 ("european_ancestry_on_american_side", amer_b, donors_eu)):
        order = rng.permutation(len(group))[:200]
        pick = [group[i] for i in sorted(order)]
        power[label] = {"people": len(pick)}
        for f in (0.0, 0.05, 0.10, 0.25, 1.0):
            got = []
            for p in pick:
                if not donors.get(p["type"]):   # no donor of this data type (changed after the lock; see amendments.md)
                    continue
                x = store.x(p["row"])
                dn = store.x(int(rng.choice(donors[p["type"]])))
                swap = np.repeat(rng.random(lengths.size) < f, lengths) & ~np.isnan(dn)
                xm = np.where(swap, dn, x)
                pool = store.pool(p["pool"])
                if label.startswith("native"):
                    j = residual(contrast_sums(store, LE, vE, xm, pool), u)
                else:
                    j = one(contrast_sums(store, LF, vF, xm, pool), 0, 1)
                got.append((passes(j, zstar), j["z"]))
            power[label][f"share_{f}"] = {"tested": len(got), "detected": round(float(np.mean([g[0] for g in got])), 3),
                                          "median_Z": round(float(np.median([g[1] for g in got])), 2)}

    # ---- write ----
    stat_names = ["S", "A", "D1", "D2"] + [f"E_{n}" for n in FOREIGN] + [f"G_{n}" for n in FOREIGN]
    cols = ["genetic_id", "group", "entity", "lat", "lon", "date_bp", "type", "side", "snps", "has_neighbours"]
    with open(OUT / "scan.tsv", "w") as f:
        f.write("\t".join(cols + [f"{s}_{k}" for s in stat_names for k in ("f4", "Z", "centred_Z", "n_snps")]) + "\n")
        for p in people:
            r = res[p["row"]]
            vals = [p["gid"], p["group"], p["entity"], p["lat"], p["lon"], int(p["date"]), p["type"], p["side"], p["nsnp"],
                    int(bool(p["pool"]))]
            for s in stat_names:
                j = r.get(s)
                vals += ["", "", "", ""] if j is None else [f"{j['f4']:.7g}", f"{j['z']:.3f}", f"{j['c_z']:.3f}", j["n"]]
            f.write("\t".join(str(v) for v in vals) + "\n")
    hcols = list(hit_table[0].keys()) if hit_table else ["genetic_id"]
    with open(OUT / "hits.tsv", "w") as f:
        f.write("\t".join(hcols) + "\n")
        for row in sorted(hit_table, key=lambda r: (r["side"], r["entity"], r["group"], r["genetic_id"], r["test"], r["toward"])):
            f.write("\t".join(str(row.get(c, "")).replace("\t", " ") for c in hcols) + "\n")

    def dist(values):
        v = np.array([x for x in values if not math.isnan(x)])
        return {"n": int(v.size), "mean": round(float(v.mean()), 3), "sd": round(float(v.std()), 3), "min": round(float(v.min()), 2),
                "max": round(float(v.max()), 2), "above_3": int((v >= 3).sum()), "below_minus_3": int((v <= -3).sum())}

    people_hit = {r["genetic_id"] for r in hit_table}
    robust_people = {r["genetic_id"] for r in hit_table if r["robust"]}
    summary = {
        "people": len(people), "elsewhere": len(elsewhere), "american_side": len(american),
        "with_neighbours": {"elsewhere": len(else_b), "american_side": len(amer_b)},
        "tests_in_family": n_tests, "threshold": round(zstar, 3),
        "controls": CONTROLS, "fit_coefficients": {c: round(float(x), 4) for c, x in zip(CONTROLS, u)}, "fit_people": n_fit,
        "Z_distributions": {"S": dist(res[p["row"]]["S"]["z"] for p in else_b),
                            "S_centred": dist(res[p["row"]]["S"]["c_z"] for p in else_b),
                            "D1": dist(res[p["row"]]["D1"]["z"] for p in elsewhere),
                            "D2": dist(res[p["row"]]["D2"]["z"] for p in elsewhere),
                            **{f"E_{n}": dist(res[p["row"]][f"E_{n}"]["z"] for p in amer_b) for n in FOREIGN},
                            **{f"G_{n}": dist(res[p["row"]][f"G_{n}"]["z"] for p in american) for n in FOREIGN}},
        "hit_rows": len(hit_table), "people_hit": len(people_hit), "people_hit_robustly": len(robust_people),
        "hits_by_side_and_test": dict(collections.Counter(f"{r['side']}/{r['test']}/{r['toward']}" for r in hit_table)),
        "norse": {"people": sum(1 for p in people if "Norse" in p["group"]),
                  "hit": len({r["genetic_id"] for r in hit_table if "Norse" in r["group"]})},
        "centres": centres, "centre_tests": n_centre_tests, "centre_threshold": round(z_centre, 3),
        "made_up_strangers": power}
    (OUT / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(json.dumps({k: summary[k] for k in summary if k not in ("centres", "made_up_strangers", "Z_distributions")}, indent=1))
    print("Z distributions:", json.dumps(summary["Z_distributions"]))
    print("centres:", json.dumps(centres)[:2500])
    print("made-up strangers:", json.dumps(power))


def main():
    cmd = sys.argv[1]
    if cmd == "cache":
        build_cache()
    elif cmd == "work":
        work(int(sys.argv[2]), int(sys.argv[3]))
    elif cmd == "final":
        final()
    elif cmd == "all":
        extra = ["--blind"] if BLIND else []
        subprocess.run([sys.executable, __file__, "cache"] + extra, check=True)
        n = 12
        procs = [subprocess.Popen([sys.executable, __file__, "work", str(i), str(n)] + extra, stdout=subprocess.DEVNULL)
                 for i in range(n)]
        assert all(p.wait() == 0 for p in procs), "a worker failed"
        subprocess.run([sys.executable, __file__, "final"] + extra, check=True)


if __name__ == "__main__":
    main()
