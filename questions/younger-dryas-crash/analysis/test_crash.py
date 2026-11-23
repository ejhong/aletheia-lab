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
S, n = crash.summed(ages, errs, ["a", "a", "b", "a"], mu, sig)
assert n == 3 and abs(S.sum() - 3) < 1e-9
S1, n1 = crash.summed(ages[:2], errs[:2], ["a", "a"], mu, sig)
assert n1 == 1 and abs(S1.sum() - 1) < 1e-9

# 3. The step: negative when there is less after T (younger) than before.
S = np.where(G < 12850, 1.0, 2.0)
assert abs(crash.step(S, 12850) - np.log(0.5)) < 1e-12 and abs(crash.step(S, 11000)) < 1e-12
assert abs(crash.step(np.stack([S, S[::-1] * 0 + 1]), 12850)[0] - np.log(0.5)) < 1e-12

# 4. The trend: recovers an exponential and gives a density summing to 1 inside 9,500-16,500.
dens, slope = crash.trend(np.exp(-0.0003 * G))
assert abs(slope + 0.0003) < 1e-9 and abs(dens.sum() - 1) < 1e-12 and dens[G < 9500].sum() == 0 and dens[G > 16500].sum() == 0
c = crash.crash_density(dens, 0.5)
inside = (G >= 12550) & (G < 12850)
assert abs(c.sum() - 1) < 1e-12 and abs((c[inside] / dens[inside]).mean() / (c[~inside & (dens > 0)] / dens[~inside & (dens > 0)]).mean() - 0.5) < 1e-9

# 5. End to end on made-up records, with a plain curve (no flat stretch): no crash is not flagged; a halving is,
#    most of the time. Reduced numbers of records to keep the test quick.
plain = 0.9 * G - 500.0
rng = np.random.default_rng(5)
errs_pool = np.array([40.0, 60.0, 80.0, 120.0])


def record(curve, factor, n):
    d = crash.crash_density(dens, factor) if factor < 1 else dens
    t = rng.choice(len(G), size=n, p=d)
    e = rng.choice(errs_pool, size=n)
    a = np.rint(curve[t] + rng.normal(0, 1, n) * sig[t] + rng.normal(0, 1, n) * e)
    keep = (a >= 9000) & (a <= 13800)
    return crash.analyse(a[keep], e[keep], [f"s{i}" for i in range(int(keep.sum()))], curve, sig, rng, n_null=150, n_crash=40, full=False)[0]


flags, ps, powers = [], [], []
for trial in range(5):
    out = record(plain, 0.5, 4000)
    flags.append(out["verdict"] == "drop detected")
    powers.append(out["power_halving"])
    ps.append(record(plain, 1.0, 4000)["p_at_target"])
assert sum(flags) >= 4 and min(powers) > 0.7, (flags, powers)   # a halving is caught, and the program knows it could be
assert sum(1 for p in ps if p <= 0.01) <= 1, ps                  # no crash is rarely flagged

# 6. With a flat stretch of the curve lying right over the crash, the crash cannot be seen, and the program says so:
#    power is low and the verdict is "cannot tell", not "no drop".
out = record(mu, 0.5, 1500)
assert out["power_halving"] < 0.6 and out["verdict"] in ("cannot tell", "drop detected"), out
assert crash.overall({"North America": "drop detected", "Europe": "cannot tell", "Asia": "drop detected"}) == "supported as widespread"
assert crash.overall({"North America": "drop detected", "Europe": "cannot tell", "Asia": "cannot tell"}) == "supported"
assert crash.overall({"North America": "no drop, and a halving would have shown", "Europe": "drop detected", "Asia": "x"}) == "not supported"
assert crash.overall({"North America": "cannot tell", "Europe": "drop detected", "Asia": "x"}) == "undetermined"
print("all tests pass")
