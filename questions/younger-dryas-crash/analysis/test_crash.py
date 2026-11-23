#!/usr/bin/env python3
"""Tests of crash.py on made-up data. Run: python test_crash.py (from questions/younger-dryas-crash/analysis)."""
import numpy as np

import crash

G = crash.GRID
# A made-up calibration curve: radiocarbon age = 0.9 x calendar age - 500, error 20, with a flat stretch at 12,400-12,700.
mu = 0.9 * G - 500.0
flat = (G >= 12400) & (G <= 12700)
mu[flat] = mu[G == 12400][0]
mu[G > 12700] -= 0.9 * 300
sig = np.full(len(G), 20.0)

# 1. One date calibrates to the right place and its weights sum to 1.
w = crash.calibrate(np.array([0.9 * 11000 - 500.0]), np.array([30.0]), mu, sig)
assert abs(w.sum() - 1) < 1e-12 and abs(G[np.argmax(w[0])] - 11000) <= 5
m = (w[0] * G).sum()
assert abs(m - 11000) < 5 and 30 < np.sqrt((w[0] * (G - m) ** 2).sum()) < 50      # about sqrt(30^2 + 20^2) / 0.9 = 40 years

# 2. Bins: two dates of one site in one 200-year span count once; another site, or another span, counts again.
ages, errs = np.array([9000.0, 9050.0, 9050.0, 9250.0]), np.array([30.0, 30.0, 30.0, 30.0])
b, n = crash.bin_index(ages, ["a", "a", "b", "a"])
assert n == 3 and b.tolist() == [0, 0, 1, 2]
S = crash.summed(ages, errs, b, mu, sig)
assert abs(S.sum() - 3) < 1e-9
b1, n1 = crash.bin_index(ages[:2], ["a", "a"])
assert n1 == 1 and abs(crash.summed(ages[:2], errs[:2], b1, mu, sig).sum() - 1) < 1e-9

# 3. The step: negative when there is less after T (younger) than before.
S = np.where(G < 12850, 1.0, 2.0)
assert abs(crash.step(S, 12850) - np.log(0.5)) < 1e-12 and abs(crash.step(S, 11000)) < 1e-12
assert abs(crash.step(np.stack([S, S[::-1] * 0 + 1]), 12850)[0] - np.log(0.5)) < 1e-12

# 4. The trend: recovers a smooth curve and gives a density summing to 1 inside 9,500-16,500.
xx = (G - 13000.0) / 1000.0
truth = np.exp(-0.3 * xx - 0.04 * xx * xx)
dens = crash.trend(truth)
inside0 = (G >= 9500) & (G <= 16500)
assert abs(dens.sum() - 1) < 1e-12 and dens[~inside0].sum() == 0 and np.allclose(dens[inside0] / dens[inside0].sum(), truth[inside0] / truth[inside0].sum(), rtol=1e-9)
line = crash.trend(np.exp(-0.3 * xx), degree=1)
assert np.allclose(line[inside0], np.exp(-0.3 * xx)[inside0] / np.exp(-0.3 * xx)[inside0].sum(), rtol=1e-9)
c = crash.crash_density(dens, 0.5)
inside = (G >= 12550) & (G < 12850)
assert abs(c.sum() - 1) < 1e-12 and abs((c[inside] / dens[inside]).mean() / (c[~inside & (dens > 0)] / dens[~inside & (dens > 0)]).mean() - 0.5) < 1e-9
assert crash.p_low(np.array([0.1, 0.2, 0.3]), 0.15) == 2 / 4 and crash.detected(np.arange(1, 400) / 100.0, -0.5) and not crash.detected(np.arange(1, 400) / 100.0, 0.005)

# 5. End to end on made-up records, with a plain curve (no flat stretch): no crash is not flagged; a halving is,
#    most of the time. Reduced numbers of records to keep the test quick.
plain = 0.9 * G - 500.0
rng = np.random.default_rng(5)
errs_pool = np.array([40.0, 60.0, 80.0, 120.0])


def record(curve, factor, n):
    """A made-up record of n bins, a third of them holding two dates, drawn with or without a halving."""
    d = crash.crash_density(dens, factor) if factor < 1 else dens
    bins = np.concatenate([np.arange(n), np.arange(n // 3)])
    e = rng.choice(errs_pool, size=len(bins))
    t = rng.choice(len(G), size=n, p=d)
    a = np.rint(curve[t][bins] + (rng.normal(0, 1, n) * sig[t])[bins] + rng.normal(0, 1, len(bins)) * e)
    keep = (a >= 9000) & (a <= 13800)
    return crash.analyse(a[keep], e[keep], [f"s{k}" for k in bins[keep]], curve, sig, rng, n_null=300, n_crash=40, full=False)[0]


flags, ps, powers = [], [], []
for trial in range(4):
    out = record(plain, 0.5, 4000)
    flags.append(out["verdict"] == "drop detected")
    powers.append(out["power_halving"])
    ps.append(record(plain, 1.0, 4000)["p_at_target"])
assert sum(flags) >= 3 and min(powers) > 0.6, (flags, powers)   # a halving is caught, and the program knows it could be
assert sum(1 for p in ps if p <= 0.01) <= 1, ps                  # no crash is rarely flagged

# 6. With a flat stretch of the curve lying right over the crash, the crash cannot be seen, and the program says so:
#    its stated power is low.
out = record(mu, 0.5, 1500)
assert out["power_halving"] < 0.6, out                               # the verdict is then usually "cannot tell"
assert crash.overall({"North America": "drop detected", "Europe": "cannot tell", "Asia": "drop detected"}) == "supported as widespread"
assert crash.overall({"North America": "drop detected", "Europe": "cannot tell", "Asia": "cannot tell"}) == "supported"
assert crash.overall({"North America": "a halving is excluded", "Europe": "drop detected", "Asia": "x"}) == "not supported"
assert crash.overall({"North America": "cannot tell", "Europe": "drop detected", "Asia": "x"}) == "undetermined"
# 7. Made-up records keep every bin (a bin whose dates all fall outside the admitted span is drawn again), and the
#    aquatic screen spares nutshell, eggshell and the fisher.
bins7 = np.concatenate([np.arange(300), np.arange(100)])
rec = crash.made_up(dens, np.full(400, 60.0), bins7, 300, plain, sig, np.random.default_rng(1), 3)
assert np.allclose(rec.sum(axis=1), 300, atol=1e-6), rec.sum(axis=1)
hit = lambda text: bool(crash.WATER.search(crash.LAND_SHELL.sub("", text)))
assert hit("marine shell") and hit("Fish bone") and hit("Mollusc") and hit("seal bone") and hit("shell")
assert not hit("charred hazelnut shell") and not hit("eggshell") and not hit("Nutshell") and not hit("fisher (Pekania)") and not hit("charcoal")
print("all tests pass")
