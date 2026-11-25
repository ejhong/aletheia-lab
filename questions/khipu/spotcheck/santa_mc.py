"""Santa Valley moiety Monte Carlo: free choice of 10 partitions (study) vs one partition fixed in advance."""
import itertools, numpy as np
rng = np.random.default_rng(7)
def comps(alpha, n):
    out = []
    for row in rng.dirichlet([alpha] * 6, size=n):
        raw = np.floor(row * 124).astype(int); d = 124 - raw.sum()
        if d > 0: raw[np.argsort(-(row * 124 - raw))[:d]] += 1
        out.append(raw + 1)
    return np.array(out)
subsets = [c for c in itertools.combinations(range(6), 3) if 0 in c]  # 10 partitions
def l1(a): return abs(a - 70) + abs(130 - a - 63)
print('L1 for a in 60..72:', {a: l1(a) for a in range(60, 73)})
for alpha in (1.0, 0.5):
    C = comps(alpha, 200000)
    sums = np.stack([C[:, list(s)].sum(1) for s in subsets], 1)  # 'A' side sums
    both = np.concatenate([sums, 130 - sums], 1)
    L = np.vectorize(l1)(both)
    free3 = (L.min(1) <= 3).mean(); free5 = (L.min(1) <= 5).mean()
    fixed = sums[:, 0]  # one fixed partition, fixed orientation (positions 1,2,3 = verso)
    fx3 = (np.vectorize(l1)(fixed) <= 3).mean(); fx5 = (np.vectorize(l1)(fixed) <= 5).mean()
    print(f"Dirichlet({alpha}): free best-of-10 (both orientations) L1<=3: {free3:.3f}, L1<=5: {free5:.3f} | "
          f"one partition fixed in advance, fixed orientation: L1<=3: {fx3:.3f}, L1<=5: {fx5:.3f}")
