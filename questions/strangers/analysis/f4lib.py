"""f4 and D statistics with a weighted block jackknife, read straight from an AADR "TGENO" genotype file.

Needs numpy only. The definitions are the ones in protocol.md, "Statistic".

File format (EIGENSOFT transposed packed format, as distributed in AADR v66.p1):
  bytes 0..47   header: ASCII "TGENO <n_individuals> <n_snps> <hash> <hash>", zero-padded
  then one record per individual, in .ind order, each ceil(n_snps / 4) bytes long;
  each SNP takes 2 bits, first SNP in the two highest bits of the first byte;
  value 0, 1 or 2 = number of copies of the first allele listed in the .snp file; 3 = missing.
"""
import math

import numpy as np

HEADER_BYTES = 48
BLOCK_MORGANS = 0.05
TRANSITIONS = {("A", "G"), ("G", "A"), ("C", "T"), ("T", "C")}


class Snps:
    """The .snp file: which SNPs are autosomal, which are transversions, and their jackknife block."""

    def __init__(self, path):
        chrom, gpos, a1, a2 = [], [], [], []
        with open(path) as f:
            for line in f:
                p = line.split()
                chrom.append(int(p[1]))
                gpos.append(float(p[2]))
                a1.append(p[4])
                a2.append(p[5])
        self.n_total = len(chrom)
        chrom = np.array(chrom)
        gpos = np.array(gpos)
        self.autosomal = (chrom >= 1) & (chrom <= 22)
        self.index = np.flatnonzero(self.autosomal)  # positions of the autosomal SNPs in the file
        tv = np.array([(x, y) not in TRANSITIONS for x, y in zip(a1, a2)])
        self.transversion = tv[self.index]
        # Block = (chromosome, floor(genetic position / 5 cM)), numbered 0..B-1 in file order.
        key = chrom[self.index] * 100000 + np.floor(gpos[self.index] / BLOCK_MORGANS).astype(np.int64)
        _, self.block = np.unique(key, return_inverse=True)
        self.n_blocks = int(self.block.max()) + 1
        self.chrom = chrom[self.index]
        self.gpos = gpos[self.index]

    def with_block_size(self, morgans):
        """A copy of this object whose jackknife blocks have another size (for the block-size check)."""
        other = Snps.__new__(Snps)
        other.__dict__.update(self.__dict__)
        key = self.chrom * 100000 + np.floor(self.gpos / morgans).astype(np.int64)
        _, other.block = np.unique(key, return_inverse=True)
        other.n_blocks = int(other.block.max()) + 1
        return other


class Geno:
    def __init__(self, path, snps):
        with open(path, "rb") as f:
            head = f.read(HEADER_BYTES).split(b"\0")[0].decode().split()
        assert head[0] == "TGENO", head
        self.n_ind, self.n_snp = int(head[1]), int(head[2])
        assert self.n_snp == snps.n_total
        self.rec = (self.n_snp + 3) // 4
        self.mm = np.memmap(path, dtype=np.uint8, mode="r", offset=HEADER_BYTES, shape=(self.n_ind, self.rec))
        self.snps = snps

    def genotypes(self, row):
        """Genotype codes (0, 1, 2, 3 = missing) of one individual at the autosomal SNPs."""
        bits = np.unpackbits(self.mm[row])  # most significant bit first
        g = (bits[0::2] << 1) | bits[1::2]
        return g[: self.n_snp][self.snps.index]

    def raw(self, row):
        bits = np.unpackbits(self.mm[row])
        return ((bits[0::2] << 1) | bits[1::2])[: self.n_snp]

    def frequency(self, rows):
        """Allele frequency of a set of individuals at each autosomal SNP; NaN where nobody has data."""
        total = np.zeros(self.snps.index.size, dtype=np.float64)
        count = np.zeros(self.snps.index.size, dtype=np.float64)
        for r in rows:
            g = self.genotypes(r)
            ok = g != 3
            total += np.where(ok, g, 0)
            count += 2 * ok
        with np.errstate(invalid="ignore", divide="ignore"):
            return np.where(count > 0, total / count, np.nan).astype(np.float32)


def jackknife(num_b, den_b):
    """Weighted block jackknife (Busing et al. 1999) for the ratio sum(num) / sum(den).

    num_b, den_b: per-block sums. Blocks with den == 0 are dropped. Returns (estimate, standard error, blocks used).
    The estimate is the full-data value; the standard error is the weighted jackknife one.
    """
    keep = den_b > 0
    num_b, den_b = num_b[keep], den_b[keep]
    g = num_b.size
    n = den_b.sum()
    theta = num_b.sum() / n
    theta_minus = (num_b.sum() - num_b) / (n - den_b)
    h = n / den_b
    theta_j = g * theta - np.sum((1 - den_b / n) * theta_minus)
    tau = h * theta - (h - 1) * theta_minus
    var = np.sum((tau - theta_j) ** 2 / (h - 1)) / g
    return float(theta), float(math.sqrt(var)), int(g)


def f4(freq, p1, p2, p3, p4, snps, only_transversions=False, mask=None):
    """f4(P1, P2; P3, P4) = mean over SNPs of (p1 - p2)(p3 - p4), and the matching D statistic.

    A SNP is used if all four sets have data there (and, if given, `mask` is true there).
    Positive means P4 shares more alleles with P2 than P3 does.
    """
    a, b, c, d = (freq[k].astype(np.float64) for k in (p1, p2, p3, p4))
    ok = ~(np.isnan(a) | np.isnan(b) | np.isnan(c) | np.isnan(d))
    if only_transversions:
        ok &= snps.transversion
    if mask is not None:
        ok &= mask
    blk = snps.block[ok]
    a, b, c, d = a[ok], b[ok], c[ok], d[ok]
    num = (a - b) * (c - d)
    den = (a + b - 2 * a * b) * (c + d - 2 * c * d)
    nb = snps.n_blocks
    cnt_b = np.bincount(blk, minlength=nb).astype(np.float64)
    num_b = np.bincount(blk, weights=num, minlength=nb)
    den_b = np.bincount(blk, weights=den, minlength=nb)
    est, se, g = jackknife(num_b, cnt_b)
    # Centred f4: mean of products minus product of means (removes a uniform difference in reference-allele share).
    ab_b = np.bincount(blk, weights=a - b, minlength=nb)
    cd_b = np.bincount(blk, weights=c - d, minlength=nb)
    kp = cnt_b > 0
    m_, s_, x_, y_ = cnt_b[kp], num_b[kp], ab_b[kp], cd_b[kp]
    n_ = m_.sum()
    c_est = s_.sum() / n_ - (x_.sum() / n_) * (y_.sum() / n_)
    c_minus = (s_.sum() - s_) / (n_ - m_) - ((x_.sum() - x_) / (n_ - m_)) * ((y_.sum() - y_) / (n_ - m_))
    h_ = n_ / m_
    c_j = g * c_est - np.sum((1 - m_ / n_) * c_minus)
    c_tau = h_ * c_est - (h_ - 1) * c_minus
    c_se = math.sqrt(np.sum((c_tau - c_j) ** 2 / (h_ - 1)) / g)
    # D: ratio of sums; jackknife over the same blocks, weighting blocks by their SNP count.
    keep = cnt_b > 0
    nB, dB, cB = num_b[keep], den_b[keep], cnt_b[keep]
    d_est = nB.sum() / dB.sum()
    d_minus = (nB.sum() - nB) / (dB.sum() - dB)
    n = cB.sum()
    h = n / cB
    d_j = g * d_est - np.sum((1 - cB / n) * d_minus)
    tau = h * d_est - (h - 1) * d_minus
    d_se = math.sqrt(np.sum((tau - d_j) ** 2 / (h - 1)) / g)
    return {"n_snps": int(ok.sum()), "n_blocks": g, "f4": est, "se": se, "z": est / se if se > 0 else float("nan"),
            "f4c": float(c_est), "f4c_se": float(c_se), "f4c_z": float(c_est / c_se) if c_se > 0 else float("nan"),
            "balance": float(y_.sum() / n_),
            "D": float(d_est), "D_se": float(d_se), "D_z": float(d_est / d_se) if d_se > 0 else float("nan")}


def kinship(g1, g2):
    """KING-robust kinship between two diploid genomes (Manichaikul et al. 2010), from genotype codes 0/1/2/3."""
    ok = (g1 != 3) & (g2 != 3)
    a, b = g1[ok], g2[ok]
    het_a, het_b = int((a == 1).sum()), int((b == 1).sum())
    hethet = int(((a == 1) & (b == 1)).sum())
    opposite = int(((a == 0) & (b == 2)).sum() + ((a == 2) & (b == 0)).sum())
    lo = min(het_a, het_b)
    return (hethet - 2 * opposite) / (2 * lo) + 0.5 - (het_a + het_b) / (4 * lo)


def composite(freq, quartets, fn, snps, mask=None):
    """Jackknife for a quantity built from several f4 values, fn(list of f4 values), on one common mask.

    quartets: list of (P1, P2, P3, P4). The same block is removed from every term.
    Returns (estimate, standard error, number of SNPs).
    """
    names = sorted({p for q in quartets for p in q})
    ok = np.ones(snps.block.size, dtype=bool) if mask is None else mask.copy()
    for k in names:
        ok &= ~np.isnan(freq[k])
    blk = snps.block[ok]
    f = {k: freq[k][ok].astype(np.float64) for k in names}
    m = np.bincount(blk, minlength=snps.n_blocks).astype(np.float64)
    sums = [np.bincount(blk, weights=(f[a] - f[b]) * (f[c] - f[d]), minlength=snps.n_blocks) for a, b, c, d in quartets]
    keep = m > 0
    m = m[keep]
    sums = [x[keep] for x in sums]
    n, g = m.sum(), m.size
    theta = fn([x.sum() / n for x in sums])
    theta_minus = np.array([fn([(x.sum() - x[j]) / (n - m[j]) for x in sums]) for j in range(g)])
    h = n / m
    theta_j = g * theta - np.sum((1 - m / n) * theta_minus)
    tau = h * theta - (h - 1) * theta_minus
    se = math.sqrt(np.sum((tau - theta_j) ** 2 / (h - 1)) / g)
    return float(theta), float(se), int(n)
