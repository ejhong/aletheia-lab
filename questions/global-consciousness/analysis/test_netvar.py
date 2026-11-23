#!/usr/bin/env python3
"""Tests of netvar.py on made-up data. Run: python test_netvar.py (from questions/global-consciousness/analysis)."""
import datetime
import gzip
import math
import os
import tempfile

import numpy as np

import netvar

rng = np.random.default_rng(3)
UTC = datetime.timezone.utc


def t0_of(day):
    return int(datetime.datetime.strptime(day, "%Y-%m-%d").replace(tzinfo=UTC).timestamp())


def make_reader(days):
    return lambda d: (t0_of(d), days[d][0], days[d][1])


def noise(n_eggs, sd=None):
    sd = np.full(n_eggs, math.sqrt(50)) if sd is None else sd
    return (100 + rng.normal(0, 1, (86400, n_eggs)) * sd).astype(np.float32)


# 1. Reading a made-up day file: egg numbers, seconds, empty fields, lines of other types.
tmp = tempfile.mkdtemp()
netvar.DATA = __import__("pathlib").Path(tmp)
day = "2020-03-01"
with gzip.open(os.path.join(tmp, f"basketdata-{day}.csv.gz"), "wt") as f:
    f.write('10,1,10,"Samples per record"\n11,1,3,"Eggs reporting"\n12,"gmtime",,7,1,42\n')
    f.write(f"13,{t0_of(day)},,101,,99\n13,{t0_of(day) + 2},,150,98,\n13,{t0_of(day) + 86399},,100,100,100\n")
t0, eggs, x = netvar.read_day(day)
assert t0 == t0_of(day) and eggs == [7, 1, 42] and x.shape == (86400, 3)
assert x[0, 0] == 101 and np.isnan(x[0, 1]) and x[0, 2] == 99 and x[2, 0] == 150 and np.isnan(x[1]).all() and x[86399, 1] == 100
t0b, eggs_b, xb = netvar.read_day(day)                              # second call comes from the cache
assert eggs_b == eggs and np.array_equal(np.isnan(x), np.isnan(xb))

# 2. A window across two days, with eggs that differ between the days; wild trials removed.
A, B = noise(3), noise(3)
A[10, 0], B[5, 1] = 150.0, 55.0                                      # 45 or more from 100: removed
days = {"2020-01-01": ([1, 2, 3], A), "2020-01-02": ([2, 3, 9], B)}
eggs_w, w = netvar.window("2020-01-01 18:00:00", make_reader(days))
assert eggs_w == [1, 2, 3, 9] and w.shape == (86400, 4)
assert w[0, 0] == A[64800, 0] and np.isnan(w[0, 3]) and w[21600, 3] == B[0, 2] and np.isnan(w[21600, 0]) and w[21600, 1] == B[0, 0]
assert np.isnan(w[21605, 2])                                         # B[5, 1] is egg 3 on day two
eggs_d, d = netvar.window("2020-01-01 00:00:00", make_reader(days))
assert eggs_d == [1, 2, 3] and np.isnan(d[10, 0])

# 3. Pure noise: scores look standard normal. Forty made-up windows of 12 eggs.
zs = []
for _ in range(40):
    zs.append(netvar.score(noise(12), math.sqrt(50))["z"])
zs = np.array(zs)
assert abs(zs.mean()) < 0.5 and 0.7 < zs.std(ddof=1) < 1.35, (zs.mean(), zs.std(ddof=1))
r = netvar.score(noise(12), math.sqrt(50))
assert r["df"] == 86400 and r["eggs_median"] == 12 and abs(r["chi2"] / r["df"] - 1) < 0.03

# 4. A common signal across eggs raises the score; so does nothing else here.
x = noise(12)
x += rng.normal(0, 0.5, (86400, 1)).astype(np.float32)               # every egg shares a small wobble each second
assert netvar.score(x, math.sqrt(50))["z"] > 10

# 5. The egg check: an egg far over in variance is dropped; so is one with too few trials.
bad = noise(12)
bad[:, 4] = 100 + (bad[:, 4] - 100) * 1.1                             # one egg 21% over in variance
assert netvar.passes(*netvar.egg_stats(bad)).tolist() == [True] * 4 + [False] + [True] * 7
few = noise(12)
few[:50000, 0] = np.nan
assert netvar.passes(*netvar.egg_stats(few)).tolist() == [False] + [True] * 11

# 6. Too few seconds: not evaluable (80% are needed). Seconds with under five eggs are not used.
x = noise(6)
x[:20000] = np.nan
assert netvar.score(x, math.sqrt(50)) is None
x = noise(6)
x[:10000, :3] = np.nan                                               # three eggs for the first 10,000 seconds
assert netvar.score(x, math.sqrt(50))["df"] == 76400

# 7. The cross-egg part: near zero for noise, large for a shared wobble, and blind to an egg's own extra variance.
x = noise(12)
assert abs(netvar.cross_part(x, math.sqrt(50))) < 4
loud = x.copy()
loud[:, 0] = 100 + (loud[:, 0] - 100) * 1.05
assert abs(netvar.cross_part(loud, math.sqrt(50)) - netvar.cross_part(x, math.sqrt(50))) < 0.5
assert netvar.score(loud, math.sqrt(50))["z"] - netvar.score(x, math.sqrt(50))["z"] > 1.0
assert netvar.cross_part(x + rng.normal(0, 0.5, (86400, 1)).astype(np.float32), math.sqrt(50)) > 10

# 8. The whole procedure at one tenth scale, on made-up eggs with unequal variances: 30 events and 30 controls in
#    one year. Scores should look standard normal, events and controls alike, with theoretical standardising biased.
save = (netvar.WINDOW, netvar.MIN_TRIALS, netvar.MIN_SECONDS, netvar.REF_TRIALS)
netvar.WINDOW, netvar.MIN_TRIALS, netvar.MIN_SECONDS, netvar.REF_TRIALS = 8640, 4320, 6912, 8640
bias = np.full(20, math.sqrt(50)) * np.sqrt(1 + rng.normal(0.004, 0.002, 20))    # every egg a little over in variance
sim = {}


def small_reader(d):
    if d not in sim:
        sim[d] = (100 + rng.normal(0, 1, (8640, 20)) * bias).astype(np.float32)
    return t0_of(d), list(range(20)), sim[d]


base = datetime.date(2019, 1, 1)
ev = [(base + datetime.timedelta(days=4 * k)).isoformat() + " 00:00:00" for k in range(30)]
co = [(base + datetime.timedelta(days=4 * k + 2)).isoformat() + " 00:00:00" for k in range(30)]
stats = netvar.year_variances(co, small_reader)
ze, zc, zt = [], [], []
for e, c in zip(ev, co):
    r = netvar.score_window(e, [stats[k] for k in co], small_reader)
    ze.append(r["main"]["z"])
    zt.append(r["theory"]["z"])
    zc.append(netvar.score_window(c, [stats[k] for k in co if k != c], small_reader)["main"]["z"])
ze, zc, zt = map(np.array, (ze, zc, zt))
assert abs(ze.mean()) < 0.45 and abs(zc.mean()) < 0.45 and 0.7 < ze.std(ddof=1) < 1.35 and 0.7 < zc.std(ddof=1) < 1.35, (ze.mean(), zc.mean(), ze.std(), zc.std())
assert zt.mean() - ze.mean() > 0.15, (zt.mean(), ze.mean())           # theoretical standardising carries the variance bias
netvar.WINDOW, netvar.MIN_TRIALS, netvar.MIN_SECONDS, netvar.REF_TRIALS = save

# 9. Combining, the paired check and the verdicts.
c = netvar.combine([1.0, -1.0, 2.0, None])
assert c["n"] == 3 and abs(c["z"] - 2 / math.sqrt(3)) < 1e-12
assert netvar.sign_flip([1.0] * 12) < 0.001 and 0.3 < netvar.sign_flip([1.0, -1.0, 0.5, -0.5, 0.2, -0.2, 0.1]) < 0.7
v = netvar.verdicts(3.2, 58)
assert v["departure"] == "departure" and v["size"] == "not shown smaller than the benchmark"
v = netvar.verdicts(0.2, 58)
assert v["departure"] == "no positive excess detected" and v["size"] == "smaller than the benchmark" and abs(v["predicted_at_benchmark"] - 2.513) < 1e-3
v = netvar.verdicts(1.0, 58)
assert v["departure"] == "no positive excess detected" and v["size"] == "not shown smaller than the benchmark"
assert netvar.verdicts(2.0, 58)["departure"] == "suggestive"
print("all tests pass")
