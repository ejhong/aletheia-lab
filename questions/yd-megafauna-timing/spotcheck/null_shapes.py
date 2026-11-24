"""How much Younger Dryas probability mass (M_yd) can an instant wipeout at 12,850 cal BP leak, under
three shapes of the true population before the wipeout? (Spot check, not part of the locked run.)

For the Score 12 AMS subset (same subset rule as the study), each null draws true calendar ages,
adds the subset's own lab errors and IntCal20 noise, recalibrates, and records M_yd (share of mass in
12,700-11,700 cal BP) for 1,000 catalogues of the observed size:
  1. uniform on 12,850-18,000 cal BP (close to the study's H_impact);
  2. shaped like the observed SPD itself, truncated at 12,850 (copies the pre-onset surge in dates);
  3. worst case: every true age in 12,850-13,000 cal BP.
Calibration: 5-year grid, likelihood without the 1/sqrt(var) term, as in the study's own code.
Seeded (numpy default_rng(1)); results are exact on rerun.

Needs (see ../MANIFEST.md): data/intcal20.14c and data/broughton2018_s1.xlsx.
Run:  python -I -B questions/yd-megafauna-timing/spotcheck/null_shapes.py [DATA_DIR]     (a few seconds)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

from common import calibrate, data_dir, load_broughton, load_intcal  # noqa: E402

d = data_dir()
ic = load_intcal(d)
recs = [r for r in load_broughton(d)
        if 6000 <= r["rc"] <= 35000 and r["err"] > 0 and r["method"] in ("MS", "AMS")]

# Subset rule: >= 50% of the posterior inside 20,000-9,000 cal BP (posterior on 9,000-25,000).
gf = np.arange(9000, 25001, 5.0)
pf = calibrate([r["rc"] for r in recs], [r["err"] for r in recs],
               np.interp(gf, ic[:, 0], ic[:, 1]), np.interp(gf, ic[:, 0], ic[:, 2]), full_likelihood=False)
keep = pf[:, (gf >= 9000) & (gf <= 20000)].sum(axis=1) >= 0.5
rc = np.array([r["rc"] for r in recs])[keep]
er = np.array([r["err"] for r in recs])[keep]
n = len(rc)

g = np.arange(9000, 20001, 5.0)
mu, sg = np.interp(g, ic[:, 0], ic[:, 1]), np.interp(g, ic[:, 0], ic[:, 2])
spd = calibrate(rc, er, mu, sg, full_likelihood=False).mean(axis=0)
yd = (g >= 11700) & (g <= 12700)
m_obs = spd[yd].sum()
print(f"Score 12 AMS dates in subset: {n}")
print(f"observed M_yd = {100 * m_obs:.2f}%  (= {m_obs * n:.1f} dates' worth of mass, {100 * m_obs:.1f}% of the dates)")

rng = np.random.default_rng(1)


def simulate(weights, n_sims=1000, pool=20000):
    t = rng.choice(g, size=pool, p=weights) + rng.uniform(-2.5, 2.5, pool)
    e = rng.choice(er, size=pool)
    r = rng.normal(np.interp(t, ic[:, 0], ic[:, 1]), np.sqrt(e ** 2 + np.interp(t, ic[:, 0], ic[:, 2]) ** 2))
    pool_yd = np.empty(pool)
    for s in range(0, pool, 2000):
        pool_yd[s:s + 2000] = calibrate(r[s:s + 2000], e[s:s + 2000], mu, sg, full_likelihood=False)[:, yd].sum(axis=1)
    m = np.array([pool_yd[rng.choice(pool, n, replace=False)].mean() for _ in range(n_sims)])
    return np.percentile(m, 50), np.percentile(m, 99), m.max(), int((m >= m_obs).sum()), n_sims


nulls = {
    "1 uniform 12,850-18,000": np.where((g >= 12850) & (g <= 18000), 1.0, 0.0),
    "2 observed SPD shape, truncated at 12,850": np.where(g >= 12850, spd, 0.0),
    "3 all true ages in 12,850-13,000": np.where((g >= 12850) & (g <= 13000), 1.0, 0.0),
}
print("\nnull                                         median   99th pct   max     sims >= observed")
for name, w in nulls.items():
    med, p99, mx, k, ns = simulate(w / w.sum())
    print(f"{name:44s} {100 * med:5.2f}%   {100 * p99:5.2f}%   {100 * mx:5.2f}%   {k} of {ns}")
