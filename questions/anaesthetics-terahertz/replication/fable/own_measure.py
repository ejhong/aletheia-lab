"""The paper's own measure on the wider panel, from the study's results table. Written by Claude; exploratory.

Craddock 2017 scored each gas by "the maximum frequency decrease" in the 613 THz band. The study recorded that as
d_down_613_ghz but judged the question on a different column (the signed largest shift). This script asks how well
the paper's measure sorts 27 anaesthetics from 7 look-alike gases on each target, whether that is only molecular
size, and how tubulin compares with the others. Run: python own_measure.py ../../results/shifts.tsv
"""
import csv, sys
from collections import defaultdict
import numpy as np

SPLIT = 9.86   # cubic angstroms: where an isolated gas sits at 613 THz in this model


def auc(pos, neg):
    pos, neg = np.asarray(pos), np.asarray(neg)
    return float(((pos[:, None] > neg[None, :]).sum() + 0.5 * (pos[:, None] == neg[None, :]).sum()) / (len(pos) * len(neg)))


def main(path):
    rows = list(csv.DictReader(open(path), delimiter="\t"))
    rng = np.random.default_rng(1)
    for src, model in (("vina", "A"), ("vinardo", "A"), ("vina", "A_phys")):
        by = defaultdict(dict)
        for r in rows:
            if r["pose_source"] == src and r["model"] == model and r["mol_class"] in ("anaesthetic", "non_immobilizer"):
                by[r["target_id"]][r["mol_id"]] = (float(r["d_down_613_ghz"]), r["mol_class"] == "anaesthetic",
                                                   float(r["alpha_iso_a3"]))
        mols = sorted(by["tubulin_1jff"])
        ref = np.array([by["tubulin_1jff"][m][0] for m in mols])
        a = np.array([by["tubulin_1jff"][m][1] for m in mols])
        big = np.array([by["tubulin_1jff"][m][2] for m in mols]) > SPLIT
        print(f"\ngas positions from {src}, model {model}: {int(a.sum())} anaesthetics, {int((~a).sum())} look-alikes; "
              f"{int((a & big).sum())} and {int((~a & big).sum())} of them large")
        print(f"{'target':24s}{'all':>6s}{'p':>8s}{'large':>7s}{'small':>7s}   tubulin 1JFF minus this, 95% interval")
        for t, d in by.items():
            v = np.array([d[m][0] for m in mols])
            A = auc(v[a], v[~a])
            perm = np.array([auc(v[p], v[~p]) for p in (rng.permutation(a) for _ in range(4000))])
            p = float((np.abs(perm - 0.5) >= abs(A - 0.5)).mean())
            diff = []
            for _ in range(3000):
                i = rng.integers(0, len(mols), len(mols))
                if a[i].all() or not a[i].any():
                    continue
                diff.append(auc(ref[i][a[i]], ref[i][~a[i]]) - auc(v[i][a[i]], v[i][~a[i]]))
            lo, hi = np.percentile(diff, [2.5, 97.5])
            tail = "" if t == "tubulin_1jff" else f"   {lo:+.2f} to {hi:+.2f}"
            print(f"{t:24s}{A:6.2f}{p:8.3f}{auc(v[a & big], v[~a & big]):7.2f}{auc(v[a & ~big], v[~a & ~big]):7.2f}{tail}")


if __name__ == "__main__":
    main(sys.argv[1])
