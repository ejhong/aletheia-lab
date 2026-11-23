#!/usr/bin/env python3
"""Checks of f4lib on made-up data (no real genotypes). Run: .venv/bin/python analysis/test_f4lib.py"""
import pathlib
import tempfile

import numpy as np

import f4lib


def write_fake(tmp, geno, chrom, gpos, alleles):
    """geno: (n_ind, n_snp) array of codes 0..3. Writes .snp and TGENO files."""
    n_ind, n_snp = geno.shape
    snp = tmp / "x.snp"
    with open(snp, "w") as f:
        for i in range(n_snp):
            f.write(f"rs{i} {chrom[i]} {gpos[i]:.6f} {i + 1} {alleles[i][0]} {alleles[i][1]}\n")
    rec = (n_snp + 3) // 4
    path = tmp / "x.geno"
    with open(path, "wb") as f:
        f.write(f"TGENO {n_ind} {n_snp} 0 0".encode().ljust(48, b"\0"))
        for r in range(n_ind):
            padded = np.full(rec * 4, 3, dtype=np.uint8)
            padded[:n_snp] = geno[r]
            b = (padded[0::4] << 6) | (padded[1::4] << 4) | (padded[2::4] << 2) | padded[3::4]
            f.write(b.astype(np.uint8).tobytes())
    return snp, path


def simulate(rng, n_snp, admix):
    """Four populations on the tree ((O, A), (R, X)); X gets a fraction `admix` from A's branch."""
    anc = rng.uniform(0.1, 0.9, n_snp)
    def drift(p, s):
        return np.clip(p + rng.normal(0, s, n_snp) * np.sqrt(p * (1 - p)), 0.01, 0.99)
    o = drift(anc, 0.3)
    non = drift(anc, 0.2)
    a = drift(non, 0.15)
    am = drift(non, 0.15)
    r = drift(am, 0.1)
    x = drift(am, 0.1)
    x = (1 - admix) * x + admix * a
    return o, a, r, x


def main():
    rng = np.random.default_rng(1)
    n_snp, n_per = 60000, 12
    chrom = np.repeat(np.arange(1, 23), n_snp // 22 + 1)[:n_snp]
    chrom[-500:] = 23  # some non-autosomal SNPs that must be ignored
    gpos = np.zeros(n_snp)
    for c in np.unique(chrom):
        m = chrom == c
        gpos[m] = np.sort(rng.uniform(0, 1.5, m.sum()))
    alleles = [("A", "G") if i % 3 else ("A", "C") for i in range(n_snp)]
    with tempfile.TemporaryDirectory() as t:
        tmp = pathlib.Path(t)
        null_z = []
        for trial, admix in enumerate([0.0] * 8 + [0.3]):
            freqs = simulate(rng, n_snp, admix)
            geno = np.vstack([rng.binomial(2, p, (n_per, n_snp)) for p in freqs]).astype(np.uint8)
            geno[rng.random(geno.shape) < 0.1] = 3  # missing data
            geno[2 * n_per:, :][geno[2 * n_per:, :] == 1] = 2 * rng.integers(0, 2, (geno[2 * n_per:, :] == 1).sum())  # R, X pseudo-haploid
            snp_path, geno_path = write_fake(tmp, geno, chrom, gpos, alleles)
            snps = f4lib.Snps(snp_path)
            g = f4lib.Geno(geno_path, snps)
            # 1. The reader returns exactly what was written.
            for r in (0, 5, geno.shape[0] - 1):
                assert np.array_equal(g.raw(r), geno[r]), "reader mismatch"
            assert snps.index.size == n_snp - 500
            freq = {name: g.frequency(range(k * n_per, (k + 1) * n_per)) for k, name in enumerate("OARX")}
            # 2. Frequencies match a direct calculation.
            sub = geno[:n_per, : n_snp - 500].astype(float)
            ok = sub != 3
            direct = np.where(ok.sum(0) > 0, np.where(ok, sub, 0).sum(0) / (2 * ok.sum(0).clip(1)), np.nan)
            assert np.allclose(freq["O"], direct, equal_nan=True, atol=1e-6)
            res = f4lib.f4(freq, "O", "A", "R", "X", snps)
            # 3. The estimate equals the plain mean of the products.
            a, b, c, d = (freq[k].astype(float) for k in "OARX")
            m = ~(np.isnan(a) | np.isnan(b) | np.isnan(c) | np.isnan(d))
            assert abs(res["f4"] - np.mean((a[m] - b[m]) * (c[m] - d[m]))) < 1e-12
            # 3b. Centred f4 equals the mean of products minus the product of means, and "balance" is mean(p3 - p4).
            assert abs(res["f4c"] - (np.mean((a[m] - b[m]) * (c[m] - d[m])) - np.mean(a[m] - b[m]) * np.mean(c[m] - d[m]))) < 1e-12
            assert abs(res["balance"] - np.mean(c[m] - d[m])) < 1e-12
            # 4. Symmetries: swapping a pair flips the sign; swapping the pairs changes nothing.
            assert abs(f4lib.f4(freq, "A", "O", "R", "X", snps)["f4"] + res["f4"]) < 1e-12
            assert abs(f4lib.f4(freq, "R", "X", "O", "A", snps)["f4"] - res["f4"]) < 1e-12
            # 5. The jackknife standard error agrees with a delete-one recomputation done the slow way.
            est = []
            w = []
            for blk in range(snps.n_blocks):
                mm = m & (snps.block != blk)
                if mm.sum() < m.sum():
                    est.append(np.mean((a[mm] - b[mm]) * (c[mm] - d[mm])))
                    w.append(m.sum() - mm.sum())
            est, w = np.array(est), np.array(w, dtype=float)
            n = w.sum()
            h = n / w
            tj = len(est) * res["f4"] - np.sum((1 - w / n) * est)
            tau = h * res["f4"] - (h - 1) * est
            se_slow = np.sqrt(np.sum((tau - tj) ** 2 / (h - 1)) / len(est))
            assert abs(se_slow - res["se"]) < 1e-12, (se_slow, res["se"])
            # 5b. composite() with a single term reproduces f4 and its standard error; a ratio of a term to
            #     itself is exactly 1 with zero error.
            c_est, c_se, c_n = f4lib.composite(freq, [("O", "A", "R", "X")], lambda v: v[0], snps)
            assert abs(c_est - res["f4"]) < 1e-12 and abs(c_se - res["se"]) < 1e-12 and c_n == res["n_snps"]
            r_est, r_se, _ = f4lib.composite(freq, [("O", "A", "R", "X"), ("O", "A", "R", "X")], lambda v: v[0] / v[1], snps)
            assert abs(r_est - 1) < 1e-12 and r_se < 1e-9
            # 5c. Bigger blocks give a similar standard error on data without linkage.
            big = f4lib.f4(freq, "O", "A", "R", "X", snps.with_block_size(0.10))
            assert abs(big["f4"] - res["f4"]) < 1e-12 and 0.7 < big["se"] / res["se"] < 1.4 and big["n_blocks"] < res["n_blocks"]
            # 6. Transversion filter uses only A/C SNPs here.
            tv = f4lib.f4(freq, "O", "A", "R", "X", snps, only_transversions=True)
            assert tv["n_snps"] == int((m & snps.transversion).sum()) < res["n_snps"]
            # 7. No admixture gives |Z| small; 10% admixture from A's branch gives a clearly positive Z.
            print(f"admix={admix}: f4={res['f4']:.6f} se={res['se']:.6f} Z={res['z']:.2f} D={res['D']:.5f} DZ={res['D_z']:.2f} blocks={res['n_blocks']}")
            if admix == 0:
                null_z.append(res["z"])
            else:
                assert res["z"] > 5 and res["D_z"] > 5
        # With no admixture the Z-scores should look like draws from a standard normal.
        null_z = np.array(null_z)
        print("null Z-scores:", np.round(null_z, 2), "mean", round(null_z.mean(), 2), "sd", round(null_z.std(ddof=1), 2))
        assert abs(null_z.mean()) < 1.2 and 0.4 < null_z.std(ddof=1) < 1.9 and np.abs(null_z).max() < 3.5
    # Sign convention on one made-up SNP: f4(O, A; R, X) is positive when X shares A's allele and R does not.
    one = f4lib.Snps.__new__(f4lib.Snps)
    one.block = np.array([0, 1]); one.n_blocks = 2; one.transversion = np.array([True, True])
    fq = {k: np.array(v, dtype=np.float32) for k, v in
          {"O": [0, 0], "A": [1, 1], "R": [0, 0], "X": [1, 1], "ONG": [0, 0], "PAP": [1, 1]}.items()}
    assert f4lib.f4(fq, "O", "A", "R", "X", one)["f4"] == 1.0
    # f4(ONG, Papuan; R, X) is positive when X shares the Papuan allele: positive = Papuan side.
    assert f4lib.f4(fq, "ONG", "PAP", "R", "X", one)["f4"] == 1.0
    assert f4lib.f4(fq, "PAP", "ONG", "R", "X", one)["f4"] == -1.0
    # A uniform lean of X toward the first allele changes f4 but not the centred f4.
    rng = np.random.default_rng(5)
    base = {k: rng.uniform(0.2, 0.8, 5000).astype(np.float32) for k in "OARX"}
    lean = dict(base, X=(base["X"] + 0.05).astype(np.float32))
    sn = f4lib.Snps.__new__(f4lib.Snps)
    sn.block = np.repeat(np.arange(50), 100); sn.n_blocks = 50; sn.transversion = np.ones(5000, dtype=bool)
    r0, r1 = f4lib.f4(base, "O", "A", "R", "X", sn), f4lib.f4(lean, "O", "A", "R", "X", sn)
    assert abs(r0["f4c"] - r1["f4c"]) < 1e-6 and abs(r0["f4"] - r1["f4"]) > 1e-5
    # Kinship: identical genomes give 0.5; unrelated draws from the same frequencies give about 0.
    rng = np.random.default_rng(3)
    p = rng.uniform(0.1, 0.9, 200000)
    g1, g2 = rng.binomial(2, p).astype(np.uint8), rng.binomial(2, p).astype(np.uint8)
    child = (rng.binomial(1, g1 / 2) + rng.binomial(1, g2 / 2)).astype(np.uint8)
    k_self, k_unrel, k_po = f4lib.kinship(g1, g1), f4lib.kinship(g1, g2), f4lib.kinship(g1, child)
    print(f"kinship: self {k_self:.3f} (0.5), unrelated {k_unrel:.3f} (0), parent-child {k_po:.3f} (0.25)")
    assert abs(k_self - 0.5) < 1e-9 and abs(k_unrel) < 0.02 and abs(k_po - 0.25) < 0.02
    print("all checks passed")


if __name__ == "__main__":
    main()
