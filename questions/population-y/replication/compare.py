#!/usr/bin/env python3
"""Compare an independent implementation's output with ours.

    python3 replication/compare.py THEIR_OUTDIR [--amended]

Sets are compared member by member. Each of our f4 statistics is matched to theirs by the four set names and the
SNP class; where several of theirs match (the same quartet on different masks), the one with the same SNP count
is taken, or failing that the nearest. Agreement per protocol: SNP counts equal, |f4 difference| no more than
max(1% of ours, 1e-7), |Z difference| no more than 0.1.
"""
import collections
import csv
import pathlib
import sys

Q = pathlib.Path(__file__).resolve().parent.parent
REQUIRED = ("P", "LOO", "T1", "T1person", "T2", "T2person", "L", "M", "C")


def main():
    theirs_dir = pathlib.Path(sys.argv[1])
    amended = "--amended" in sys.argv
    ours_sets_path = Q / "analysis" / ("sets_amended.tsv" if amended else "sets.tsv")
    ours_f4_path = Q / "results" / ("amended/f4.tsv" if amended else "f4.tsv")

    ours = collections.defaultdict(set)
    for r in csv.DictReader(open(ours_sets_path), delimiter="\t"):
        ours[r["set"]].add(r["genetic_id"])
    theirs = collections.defaultdict(set)
    for r in csv.DictReader(open(theirs_dir / "sets.tsv"), delimiter="\t"):
        theirs[r["set"]].add(r["genetic_id"])
    names = [n for n in ours if not n.endswith(".Mandenka")]
    same = [n for n in names if ours[n] == theirs.get(n, set())]
    print(f"SETS: {len(same)} of {len(names)} of our sets have identical members in theirs")
    for n in names:
        if ours[n] != theirs.get(n, set()):
            a, b = ours[n] - theirs.get(n, set()), theirs.get(n, set()) - ours[n]
            print(f"   {n}: ours {len(ours[n])}, theirs {len(theirs.get(n, set()))}; only ours {sorted(a)[:4]}; only theirs {sorted(b)[:4]}")
    extra = [n for n in theirs if n not in ours]
    if extra:
        print(f"   sets only in theirs: {len(extra)}, e.g. {extra[:6]}")

    idx = collections.defaultdict(list)
    ten = {}
    for r in csv.DictReader(open(theirs_dir / "f4.tsv"), delimiter="\t"):
        try:
            row = (int(r["n_snps"]), float(r["f4"]), float(r["se"]), float(r["Z"]))
        except ValueError:
            continue
        key = (r["P1"], r["P2"], r["P3"], r["P4"], r["snps"])
        if "10" in (r.get("mask") or "") and "cM" in (r.get("mask") or ""):
            ten[key] = row  # the block-size check: same quartet and SNPs, bigger blocks
        else:
            idx[key].append(row)
    stats = collections.defaultdict(lambda: collections.Counter())
    worst = []
    for r in csv.DictReader(open(ours_f4_path), delimiter="\t"):
        sec = r["section"].split(".")[0]
        if r["id"] == "P_B.unrel" or r["id"].startswith("Pong."):
            continue  # kinship-dependent, or an extra of ours that the protocol does not ask for
        key = (r["P1"], r["P2"], r["P3"], r["P4"], r["snps"])
        cand = [ten[key]] if r["id"] == "P_A.10cM" and key in ten else idx.get(key)
        if not cand:
            stats[sec]["missing"] += 1
            continue
        n, f, se, z = int(r["n_snps"]), float(r["f4"]), float(r["se"]), float(r["Z"])
        c = min(cand, key=lambda t: (abs(t[0] - n), abs(t[1] - f)))
        ok_n = c[0] == n
        ok_f = abs(c[1] - f) <= max(0.01 * abs(f), 1e-7)
        ok_z = abs(c[3] - z) <= 0.1
        stats[sec]["compared"] += 1
        stats[sec]["agree"] += ok_n and ok_f and ok_z
        stats[sec]["snp_count_differs"] += not ok_n
        stats[sec]["f4_differs"] += not ok_f
        stats[sec]["Z_differs"] += not ok_z
        if not (ok_n and ok_f and ok_z):
            worst.append((abs(c[3] - z), r["id"], n, c[0], f, c[1], z, c[3]))
    print("\nF4 STATISTICS by section (required sections marked *)")
    print(f"{'section':10s} {'ours':>5s} {'compared':>8s} {'agree':>6s} {'n differs':>9s} {'f4 differs':>10s} {'Z differs':>9s} {'missing':>7s}")
    for sec, c in stats.items():
        total = c["compared"] + c["missing"]
        print(f"{sec + ('*' if sec in REQUIRED else ''):10s} {total:5d} {c['compared']:8d} {c['agree']:6d} {c['snp_count_differs']:9d} "
              f"{c['f4_differs']:10d} {c['Z_differs']:9d} {c['missing']:7d}")
    req = [c for s, c in stats.items() if s in REQUIRED]
    print(f"\nrequired statistics: {sum(c['agree'] for c in req)} agree of {sum(c['compared'] + c['missing'] for c in req)}")
    if worst:
        print("largest disagreements (id, our n, their n, our f4, their f4, our Z, their Z):")
        for w in sorted(worst, reverse=True)[:12]:
            print(f"   {w[1]}: n {w[2]} vs {w[3]}; f4 {w[4]:.6g} vs {w[5]:.6g}; Z {w[6]:.2f} vs {w[7]:.2f}")
    comp = theirs_dir / "composites.tsv"
    if comp.exists():
        print("\ntheir composites.tsv:")
        print(comp.read_text().strip())


if __name__ == "__main__":
    main()
