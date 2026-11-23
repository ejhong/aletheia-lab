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

# 5. Cross-standardising removes a variance bias that theoretical standardising does not; a wild egg is dropped.
sd = np.full(12, math.sqrt(50)) * 1.004                              # every egg 0.8% over in variance, in both windows
days = {"2021-05-01": (list(range(12)), noise(12, sd)), "2021-05-08": (list(range(12)), noise(12, sd))}
p = netvar.pair("2021-05-08 00:00:00", "2021-05-01 00:00:00", make_reader(days))
assert p["eggs_passing"] == 12 and p["event_theory"]["z"] - p["event"]["z"] > 0.8 and abs(p["event"]["z"]) < 3.5, p
bad = noise(12)
bad[:, 4] = 100 + (bad[:, 4] - 100) * 1.1                             # one egg 21% over in variance in the control window only
days = {"2021-06-01": (list(range(12)), bad), "2021-06-08": (list(range(12)), noise(12))}
p = netvar.pair("2021-06-08 00:00:00", "2021-06-01 00:00:00", make_reader(days))
assert p["eggs_passing"] == 11
few = noise(12)
few[:50000, 0] = np.nan                                               # too few trials: dropped
assert netvar.passes(*netvar.egg_stats(few)).tolist() == [False] + [True] * 11

# 6. Too few seconds: not evaluable. Seconds with under five eggs are not used.
x = noise(6)
x[:50000] = np.nan
assert netvar.score(x, math.sqrt(50)) is None
x = noise(6)
x[:10000, :3] = np.nan                                               # three eggs for the first 10,000 seconds
assert netvar.score(x, math.sqrt(50))["df"] == 76400

# 7. Combining and verdicts.
c = netvar.combine([1.0, -1.0, 2.0, None])
assert c["n"] == 3 and abs(c["z"] - 2 / math.sqrt(3)) < 1e-12
v = netvar.verdicts(3.2, 58, 0.4, 2.0)
assert v["departure"] == "departure" and v["size"] == "compatible with the reported size"
v = netvar.verdicts(0.2, 58, -0.4, 0.4)
assert v["departure"] == "no departure" and v["size"] == "smaller than reported" and abs(v["predicted_at_reported_size"] - 2.513) < 1e-3
v = netvar.verdicts(1.0, 58, 0.1, 0.6)
assert v["departure"] == "no departure" and v["size"] == "compatible with the reported size"
v = netvar.verdicts(3.5, 58, 2.7, 0.57)
assert v["departure"] == "no departure" and "difference" in v["based_on"]
print("all tests pass")
