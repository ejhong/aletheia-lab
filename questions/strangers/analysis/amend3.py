#!/usr/bin/env python3
"""Amendment 3: is the lean of PIE069 carried by her short DNA molecules too, or only by long ones?

    .venv/bin/python analysis/amend3.py check      # reproduce her locked statistic from the release's genotypes (no reads needed)
    .venv/bin/python analysis/amend3.py run        # the amended test, from the public reads; writes results/corrected/amended3/

Run from questions/strangers. Uses scan.py and the corrected run unchanged. See amendments.md for the rules.
"""
import json
import pathlib
import sys

import numpy as np

import corrected_run
import f4lib
import reads
import scan

Q = pathlib.Path(__file__).resolve().parent.parent
BAM = Q / "data" / "ena_PRJEB62503" / "PIE069.A0101.TF1.1_trim2.bam"
GID = "PIE069.AG"
CODE = {"A": 1, "C": 2, "G": 4, "T": 8}
SEED = 41


def setup():
    corrected_run.patch()
    store, people = scan.Store(), scan.load_people()
    p = next(q for q in people if q["gid"] == GID)
    summary = json.loads((Q / "results" / "corrected" / "summary.json").read_text())
    u = [summary["fit_coefficients"][k] for k in scan.CONTROLS]
    L, valid = scan.left_sides(store, ["NA"] + scan.CONTROLS)
    LH, vH = scan.left_sides(store, ["Han", "French"])
    pool = store.pool(p["pool"])

    def stats(x):
        blk = scan.contrast_sums(store, L, valid, x, pool)
        S, A = scan.residual(blk, u), scan.one(blk, 0, 1 + len(scan.CONTROLS))
        bh = scan.contrast_sums(store, LH, vH, x, pool)
        return {"S": S, "A": A, "toward_Han": scan.one(bh, 0, 2), "toward_French": scan.one(bh, 1, 2), "snps": int((~np.isnan(x)).sum())}

    return store, p, stats


def snp_table(store):
    """For each chromosome: sorted positions, index of each SNP in the store's order, and its two alleles as base codes."""
    snps = f4lib.Snps(scan.D / f"{scan.PREFIX}.snp")
    order = np.argsort(snps.block, kind="stable")
    where = np.empty(order.size, dtype=np.int64)
    where[order] = np.arange(order.size)                       # autosomal SNP number -> index in the store
    chrom, pos, a1, a2 = [], [], [], []
    with open(scan.D / f"{scan.PREFIX}.snp") as f:
        for line in f:
            t = line.split()
            if 1 <= int(t[1]) <= 22:
                chrom.append(int(t[1]))
                pos.append(int(t[3]))
                a1.append(CODE.get(t[4], 0))
                a2.append(CODE.get(t[5], 0))
    chrom, pos, a1, a2 = map(np.array, (chrom, pos, a1, a2))
    assert chrom.size == order.size == store.n_snp
    first, second = np.zeros(order.size, dtype=np.uint8), np.zeros(order.size, dtype=np.uint8)
    first[where], second[where] = a1, a2
    table = {}
    for c in range(1, 23):
        m = np.flatnonzero(chrom == c)
        o = np.argsort(pos[m], kind="stable")
        table[str(c)] = (pos[m][o], where[m][o])
    return table, first, second


def genotype(n_snp, snp, base, first, second, keep, rng):
    """One randomly chosen read per SNP among the observations marked keep; 1 = first allele, 0 = second, NaN = none."""
    idx = np.flatnonzero(keep & ((base == first[snp]) | (base == second[snp])))
    idx = idx[rng.permutation(idx.size)]
    _, pick = np.unique(snp[idx], return_index=True)
    idx = idx[pick]
    x = np.full(n_snp, np.nan, dtype=np.float32)
    x[snp[idx]] = (base[idx] == first[snp[idx]]).astype(np.float32)
    return x


def show(label, s):
    print(f"{label:34s} SNPs {s['snps']:7d} | S {s['S']['f4']:+.5f} (Z {s['S']['z']:+.2f}) | raw lean {s['A']['f4']:+.5f} (Z {s['A']['z']:+.2f})"
          f" | Han Z {s['toward_Han']['z']:+.2f} | French Z {s['toward_French']['z']:+.2f}")


def main():
    store, p, stats = setup()
    released = stats(store.x(p["row"]))
    show("release genotypes", released)
    if sys.argv[1:] == ["check"]:
        return
    sys.exit("the run step is added after the amendment is written")


if __name__ == "__main__":
    main()
