#!/usr/bin/env python3
"""Spot check of questions/anaesthetics-microtubules by a second vendor's model: the statistics, recomputed from the
committed table of docking scores. The docking itself is not re-run (AutoDock Vina is not installed here).

    python3 -I spot_check.py ../../results/affinities.tsv

Written by Claude Fable 5.2 from protocol.md, without using analysis/dock_anaesthetics.py. Standard library only.
For each protein and scoring method: each gas's best score over the protein's pockets; the rank correlation of
that score with potency over the 27 anaesthetics; the same after taking out the number of heavy atoms; how often an
anaesthetic outscores a non-immobilizer; the same correlation on the 9 clinical gases; and the correlation of the
score with the number of heavy atoms.
"""
import csv
import math
import sys

rows = list(csv.DictReader(open(sys.argv[1]), delimiter="\t"))


def rank(v):
    o = sorted(range(len(v)), key=lambda i: v[i])
    r = [0.0] * len(v)
    i = 0
    while i < len(v):
        j = i
        while j + 1 < len(v) and v[o[j + 1]] == v[o[i]]:
            j += 1
        for k in range(i, j + 1):
            r[o[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def pearson(a, b):
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / math.sqrt(sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b))


def resid(y, x):
    mx, my = sum(x) / len(x), sum(y) / len(y)
    s = sum((a - mx) * (b - my) for a, b in zip(x, y)) / sum((a - mx) ** 2 for a in x)
    return [b - my - s * (a - mx) for a, b in zip(x, y)]


spearman = lambda a, b: pearson(rank(a), rank(b))
for scoring in ("vina", "vinardo"):
    print("==", scoring)
    for target in sorted(set(r["target_id"] for r in rows)):
        best, meta = {}, {}
        for r in rows:
            if r["scoring"] == scoring and r["target_id"] == target:
                best[r["mol_id"]] = max(best.get(r["mol_id"], -9.0), float(r["B_neg_dG"]))
                meta[r["mol_id"]] = r
        an = [m for m in best if meta[m]["mol_class"] == "anaesthetic"]
        non = [m for m in best if meta[m]["mol_class"] == "non_immobilizer"]
        B = [best[m] for m in an]
        P = [-math.log10(float(meta[m]["mac_atm"])) for m in an]
        N = [float(meta[m]["n_heavy"]) for m in an]
        clin = [m for m in an if meta[m]["subset"] == "clinical"]
        auc = sum((best[a] > best[n]) + 0.5 * (best[a] == best[n]) for a in an for n in non) / (len(an) * len(non))
        print(f" {target:16s} anaesthetics {len(an)}, non-immobilizers {len(non)} | potency rho {spearman(B, P):+.3f}"
              f" | after size {pearson(resid(rank(B), rank(N)), resid(rank(P), rank(N))):+.3f} | AUC {auc:.3f}"
              f" | clinical only ({len(clin)}) rho {spearman([best[m] for m in clin], [-math.log10(float(meta[m]['mac_atm'])) for m in clin]):+.3f}"
              f" | score against size {spearman(B, N):+.2f}")
