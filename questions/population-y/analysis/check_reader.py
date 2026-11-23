#!/usr/bin/env python3
"""Technical checks that the genotype file is being read correctly. Uses no Native American sample.

    .venv/bin/python analysis/check_reader.py        # run from questions/population-y

What it checks:
  1. The header agrees with the .ind and .snp files.
  2. Single-read ("pseudo-haploid") ancient samples have no heterozygous calls; diploid genomes have many.
  3. Men have no heterozygous calls on the X chromosome but do on chromosome 22, and the change happens exactly at
     the first X-chromosome SNP. This pins down the order of SNPs inside each byte.
  4. Women have no data on the Y chromosome; men do.
  5. Two f4 statistics with a known answer come out as expected, in both pipelines:
     f4(Mbuti, Papuan; French, Han) is strongly positive (Han are closer to Papuans than the French are), and
     f4(Mbuti, Yoruba; French, Han) is small by comparison.
"""
import csv
import pathlib

import numpy as np

import f4lib

HERE = pathlib.Path(__file__).resolve().parent
D = HERE.parent / "data" / "aadr_v66.p1"
PREFIX = "v66.p1_1240K.aadr.patch.PUB"


def main():
    snps = f4lib.Snps(D / f"{PREFIX}.snp")
    geno = f4lib.Geno(D / f"{PREFIX}.geno", snps)
    ind = [line.split() for line in open(D / f"{PREFIX}.ind")]
    assert geno.n_ind == len(ind) and geno.n_snp == snps.n_total
    print(f"1. header ok: {geno.n_ind} individuals, {geno.n_snp} SNPs, {snps.index.size} autosomal, {snps.n_blocks} blocks")

    # Block map: genetic positions should be in Morgans (chromosome 1 spans about 2.9), giving a few hundred blocks.
    worst = 0
    for c in range(1, 23):
        sel = snps.chrom == c
        span = snps.gpos[sel].max() - snps.gpos[sel].min()
        nb = len(np.unique(snps.block[sel]))
        worst = max(worst, np.bincount(snps.block[sel]).max())
        if c in (1, 2, 21, 22):
            print(f"   chr{c}: {int(sel.sum())} SNPs, genetic span {span:.2f} Morgans, {nb} blocks")
        assert 0.3 < span < 3.5 and nb >= 8
    print(f"   largest block holds {worst} SNPs ({100 * worst / snps.index.size:.2f}% of all); "
          f"{int((snps.gpos == 0).sum())} autosomal SNPs have genetic position 0")
    assert 400 < snps.n_blocks < 900

    chrom = np.array([int(line.split()[1]) for line in open(D / f"{PREFIX}.snp")])
    row = {r[0]: i for i, r in enumerate(ind)}
    csv.field_size_limit(10 ** 9)
    with open(D / "v66.p1_1240K.aadr.PUB.anno", encoding="utf-8", errors="replace", newline="") as f:
        r = csv.reader(f, delimiter="\t")
        header = next(r)
        assert header[30].startswith("Molecular Sex")
        sex = {x[0]: x[30] for x in r}

    # 2. heterozygous calls
    for gid in ("Loschbour.AG", "Tianyuan.AG.BY.AA", "ONG-1.SG"):
        g = geno.raw(row[gid])
        het = np.mean(g[g != 3] == 1)
        print(f"2. {gid}: heterozygous fraction {het:.5f} (expect 0)")
        assert het == 0
    french = [r[0] for r in ind if r[2] == "French" and r[0].endswith(".DG")]
    g = geno.genotypes(row[french[0]])
    het = np.mean(g[g != 3] == 1)
    print(f"2. {french[0]}: heterozygous fraction {het:.3f} (expect roughly 0.1 to 0.4)")
    assert 0.05 < het < 0.5

    # 3 and 4. sex chromosomes
    first_x = int(np.flatnonzero(chrom == 23)[0])
    first_y = int(np.flatnonzero(chrom == 24)[0])
    men = [g for g in french if sex.get(g) == "M"][:12]
    women = [g for g in french if sex.get(g) == "F"][:12]
    G = np.array([geno.raw(row[g]) for g in men])
    het_last22 = (G[:, first_x - 8:first_x] == 1).sum(0)
    het_firstx = (G[:, first_x:first_x + 8] == 1).sum(0)
    print(f"3. first X SNP at index {first_x} (index mod 4 = {first_x % 4}); {len(men)} men. The first two X SNPs lie in "
          f"the pseudo-autosomal region (below 2.7 Mb), where men can be heterozygous:")
    print(f"   heterozygous men at the last 8 chr22 SNPs: {het_last22.tolist()}")
    print(f"   heterozygous men at the first 8 chrX SNPs: {het_firstx.tolist()}")
    x_het = np.mean(G[:, first_x:first_y][G[:, first_x:first_y] != 3] == 1)
    a_het = np.mean(G[:, :first_x][G[:, :first_x] != 3] == 1)
    print(f"   men: heterozygous fraction on autosomes {a_het:.3f}, on X {x_het:.5f}")
    assert x_het < 0.01 < a_het
    W = np.array([geno.raw(row[g]) for g in women])
    y_w = np.mean(W[:, first_y:] != 3)
    y_m = np.mean(G[:, first_y:] != 3)
    print(f"4. fraction of Y SNPs with data: women {y_w:.4f}, men {y_m:.4f} (diploid calling leaves some calls in women)")
    assert y_m > 1.5 * y_w

    # 4b. Well-known variants land on the right SNP with the right allele (first allele of the .snp file):
    #     rs1426654 A (SLC24A5) is near 100% in Europeans and rare elsewhere; rs3827760 A (EDAR) is rare in Han;
    #     rs2814778 T (Duffy) is absent in West Africans; rs16891982 C (SLC45A2) is rare in Europeans.
    names = [line.split()[0] for line in open(D / f"{PREFIX}.snp")]
    where = {n: i for i, n in enumerate(names)}

    def f_first(group, i):
        rows_ = [k for k, r in enumerate(ind) if r[2] == group and r[0].endswith(".DG") and r[0].startswith("HGDP")]
        x = np.array([geno.raw(k)[i] for k in rows_])
        return x[x != 3].mean() / 2

    expect = {"rs1426654": {"French": (0.9, 1.0), "Han": (0.0, 0.1), "Yoruba": (0.0, 0.1)},
              "rs3827760": {"French": (0.9, 1.0), "Han": (0.0, 0.3), "Yoruba": (0.9, 1.0)},
              "rs2814778": {"French": (0.9, 1.0), "Han": (0.9, 1.0), "Yoruba": (0.0, 0.1)},
              "rs16891982": {"French": (0.0, 0.2), "Han": (0.9, 1.0), "Yoruba": (0.9, 1.0)}}
    for rs, groups in expect.items():
        got = {g: f_first(g, where[rs]) for g in groups}
        print(f"4b. {rs} (index mod 4 = {where[rs] % 4}): " + ", ".join(f"{g} {v:.2f}" for g, v in got.items()))
        assert all(lo <= got[g] <= hi for g, (lo, hi) in groups.items()), rs

    # 5. f4 sanity, no American samples
    def members(group, prefix):
        return [i for i, r in enumerate(ind) if r[2] == group and r[0].endswith(".DG") and r[0].startswith(prefix)]
    for name, prefix in (("SGDP", ("S_", "B_")), ("NYGC", ("HGDP",))):
        freq = {g: geno.frequency(members(g, prefix)) for g in ("Mbuti", "Yoruba", "French", "Han", "Papuan")}
        a = f4lib.f4(freq, "Mbuti", "Papuan", "French", "Han", snps)
        b = f4lib.f4(freq, "Mbuti", "Yoruba", "French", "Han", snps)
        print(f"5. {name}: f4(Mbuti, Papuan; French, Han) = {a['f4']:.5f} Z = {a['z']:.1f} (expect strongly positive); "
              f"f4(Mbuti, Yoruba; French, Han) = {b['f4']:.5f} Z = {b['z']:.1f}; SNPs {a['n_snps']}")
        assert a["z"] > 10 and abs(b["f4"]) < a["f4"] / 3
    print("reader checks passed")


if __name__ == "__main__":
    main()
