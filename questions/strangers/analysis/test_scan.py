#!/usr/bin/env python3
"""Checks of scan.py's arithmetic on made-up data. Run: .venv/bin/python analysis/test_scan.py"""
import numpy as np

import f4lib
import scan


def main():
    rng = np.random.default_rng(7)
    n, nb = 30000, 300
    block = np.sort(rng.integers(0, nb, n))
    starts = np.flatnonzero(np.r_[True, block[1:] != block[:-1]])
    f = {k: rng.uniform(0.05, 0.95, n).astype(np.float32) for k in "MAPX"}
    f["X"][rng.random(n) < 0.3] = np.nan
    f["P"][rng.random(n) < 0.05] = np.nan
    # 1. centred() from block sums equals f4lib's centred f4 and standard error on the same data.
    snps = f4lib.Snps.__new__(f4lib.Snps)
    snps.block, snps.n_blocks, snps.transversion = block, int(block.max()) + 1, np.ones(n, dtype=bool)
    ref = f4lib.f4(f, "M", "A", "P", "X", snps)
    ok = ~np.isnan(f["X"]) & ~np.isnan(f["P"])
    left = np.where(ok, f["M"] - f["A"], 0).astype(np.float64)
    right = np.where(ok, f["P"] - f["X"], 0).astype(np.float64)
    red = lambda v: np.add.reduceat(v, starts)
    j = scan.jack(red(ok.astype(float)), red(left * right), red(left), red(right))
    assert abs(j["f4"] - ref["f4"]) < 1e-9 and abs(j["se"] - ref["se"]) < 1e-9, (j, ref)
    assert abs(j["c"] - ref["f4c"]) < 1e-9 and abs(j["c_se"] - ref["f4c_se"]) < 1e-9, (j, ref)
    # 2. residual(): the residual's block sums are the weighted sums of the parts.
    k = 3
    s, l = rng.normal(size=(k, starts.size)), rng.normal(size=(k, starts.size))
    blk = np.vstack([red(ok.astype(float))[None, :], red(right)[None, :], s, l])
    u = np.array([0.4, -1.3])
    direct = scan.jack(blk[0], s[0] - 0.4 * s[1] + 1.3 * s[2], l[0] - 0.4 * l[1] + 1.3 * l[2], blk[1])
    close = lambda a, b: all(abs(a[k] - b[k]) <= 1e-9 * max(1.0, abs(b[k])) for k in ("f4", "se", "c", "c_se"))
    assert close(scan.residual(blk, u), direct) and close(scan.one(blk, 1, 3), scan.jack(blk[0], s[1], l[1], blk[1]))
    # 3. robust_fit() recovers the coefficients despite a few gross outliers.
    B = rng.normal(size=(2000, 2))
    A = B @ np.array([0.7, -0.2]) + rng.normal(scale=0.05, size=2000)
    A[:10] += 50
    uu, kept = scan.robust_fit(A, B)
    assert np.allclose(uu, [0.7, -0.2], atol=0.01) and kept <= 1990
    print("scan checks passed")


if __name__ == "__main__":
    main()
