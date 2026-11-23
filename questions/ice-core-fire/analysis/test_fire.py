#!/usr/bin/env python3
"""Tests of fire.py on made-up data. Run: python test_fire.py (from questions/ice-core-fire/analysis)."""
import numpy as np

import fire

# 1. Binning discrete samples: hand calculation.
top = np.array([0.0, 4.0, 10.0, 30.0])
bot = np.array([4.0, 10.0, 16.0, 34.0])
val = np.array([1.0, 2.0, 4.0, 8.0])
b = fire.bin_samples(top, bot, val, 0.0, 10)
assert abs(b.get(0, 1)[0] - (4 * 1 + 6 * 2) / 10) < 1e-12          # bin 0: two samples
assert abs(b.get(1, 2)[0] - 4.0) < 1e-12                           # bin 1: 6 of 10 years covered
assert np.isnan(b.get(2, 3)[0])                                    # bin 2: nothing
assert np.isnan(b.get(3, 4)[0])                                    # bin 3: 4 of 10 years, under half
b5 = fire.bin_samples(top, bot, val, -5.0, 10)                     # shifted anchor: bin 0 covers [-5, 5)
assert abs(b5.get(0, 1)[0] - (4 * 1 + 1 * 2) / 5) < 1e-12

# 2. Binning 1 mm rows: mean of present values; missing when under half are present.
age = np.array([0.1, 0.5, 0.9, 1.1, 1.2, 1.3, 1.4, 2.5, np.nan])
v = np.array([1.0, np.nan, 3.0, np.nan, np.nan, np.nan, 5.0, 7.0, 9.0])
r = fire.bin_rows(age, v, 0.0, 1)
assert abs(r.get(0, 1)[0] - 2.0) < 1e-12 and np.isnan(r.get(1, 2)[0]) and abs(r.get(2, 3)[0] - 7.0) < 1e-12

# 3. Decadal rows: the right bin at T = 10; means and the half rule at T = 20 and 60.
ages = np.array([12740, 12750, 12760, 12770, 12790, 12800, 12810, 12820, 12830, 12840, 12850, 12860, 13040])
vals = np.array([1.0, 2.0, 4.0, np.nan, 5.0, 1.0, np.nan, np.nan, np.nan, 3.0, 9.0, 9.0, 7.0])
d = fire.bin_decadal(ages, vals, 12750, 10)
assert d.get(-1, 0)[0] == 1.0 and d.get(0, 1)[0] == 2.0 and d.get(29, 30)[0] == 7.0 and np.isnan(d.get(2, 3)[0])
d = fire.bin_decadal(ages, vals, 12750, 20)
assert d.get(0, 1)[0] == 3.0 and np.isnan(d.get(1, 2)[0]) and d.get(2, 3)[0] == 3.0   # bin 1: one row empty, one absent
assert np.isnan(d.get(3, 4)[0]) and d.get(4, 5)[0] == 3.0                             # bin 4: 1 of 2 present is enough
d = fire.bin_decadal(ages, vals, 12750, 60)
assert abs(d.get(0, 1)[0] - 3.0) < 1e-12                                              # 2, 4, 5, 1: four of six rows
assert abs(d.get(1, 2)[0] - 7.0) < 1e-12                                              # 3, 9, 9: three of six is enough
assert np.isnan(d.get(2, 3)[0])                                                       # no rows

# 4. A planted spike is rank 1; the scores match a direct calculation.
rng = np.random.default_rng(1)
x = np.exp(rng.normal(1.5, 0.3, 3000))
x[1510] = 60.0
m, e, z, num, mad = fire.scores(x, 10)
i = 1510
w = x[i - 15:i + 16]
assert abs(e[i] - (x[i] - np.median(w))) < 1e-12
lw = np.log(w)
assert abs(z[i] - (np.log(x[i]) - np.median(lw)) / (1.4826 * np.median(np.abs(lw - np.median(lw))))) < 1e-9
for variant, f in (("higher", max), ("lower", min)):
    m2, e2, *_ = fire.scores(x, 10, variant)
    assert abs(e2[i] - (x[i] - f(np.median(x[i - 15:i]), np.median(x[i + 1:i + 16])))) < 1e-12
m3, e3, *_ = fire.scores(x[:40], 10)
assert not np.isnan(e3[0]) and not np.isnan(e3[39])                # 16 of 31 bins exist at the very edge
m4, e4, *_ = fire.scores(x[:40], 10, "higher")
assert abs(m4[0] - np.median(x[1:16])) < 1e-12                     # only the later side exists

fire.SERIES["TEST"] = ("x", "test", "gicc05", 10, -14000, 14000)
bb = fire.Binned(0.0, 10, -1500, x)                                # bin j = index - 1500; the spike is bin 10, in window 0
fire._built[("TEST", 300, "NH4", 0.0)] = bb
rows = fire.windows("TEST")
assert len(rows) == 92 and rows[0]["start"] == -13800.0, (len(rows), rows[0]["start"])   # k = -46 .. 45
for meas in ("H", "E", "Z"):
    rk = fire.rank(rows, meas)
    assert rk["rank"] == 1 and rk["N"] == 92 and rk["top1_rank"] == 1 and rk["top5_rank"] == 4 and rk["age"] == 100.0, rk
assert rows[46]["E_value"] == 60.0 and abs(rows[46]["E_background"] - np.median(w)) < 1e-12

# 5. Windows with too few values are dropped.
x2 = x.copy()
x2[1530:1540] = np.nan                                             # 10 of 30 bins of window 1 missing: 67% < 80%
fire._built[("TEST", 300, "NH4", 0.0)] = fire.Binned(0.0, 10, -1500, x2)
assert 1 not in [r["k"] for r in fire.windows("TEST")]
x2[1530:1540] = x[1530:1540]
x2[1530:1536] = np.nan                                             # 6 of 30 missing: exactly 80% present, kept
fire._built[("TEST", 300, "NH4", 0.0)] = fire.Binned(0.0, 10, -1500, x2)
assert 1 in [r["k"] for r in fire.windows("TEST")]

# 6. Made-up fires: a huge pulse always reaches the top; a tiny one never does.
fire._built[("TEST", 300, "NH4", 0.0)] = bb
rows = fire.windows("TEST")
rk = fire.rank(rows, "E", 5)
rec = fire.pulses("TEST", rows, np.random.default_rng(0), 0, (rk["value_needed_top1"], rk["value_needed_top5"]), n_place=50)
assert rec[5000]["top1"] == 1.0 and rec[1000]["top1"] == 1.0 and rec[200]["top1"] == 0.0 and rec[20]["top1"] == 0.0, rec   # the top-1% value is the planted spike, about 55: a pulse of 1000 adds 100 to a bin
rec = fire.pulses("TEST", rows, np.random.default_rng(0), 0, (20.0, 5.0), n_place=50)
assert rec[1000]["top1"] == 1.0 and rec[20]["top1"] == 0.0 and rec[100]["top5"] == 1.0, rec

# 7. Verdict rule, with timing.
mk = lambda t1, t5, age=12900.0: {"in_top1": t1, "in_top5": t5, "age": age}
no = mk(False, False)
R = lambda **kw: {s: kw.get(s, no) for s in fire.TIER_SERIES}
assert fire.verdict(R())[0] == "not met"
assert fire.verdict(R(N10=mk(True, True)))[0] == "not corroborated"
assert fire.verdict(R(N10=mk(True, True), E20=mk(True, True)))[0] == "not corroborated"           # different tiers
assert fire.verdict(R(N10=mk(True, True), E10=mk(True, True, 12850.0)))[0] == "exceptional"       # 50 years apart
v, notes = fire.verdict(R(N10=mk(True, True), E10=mk(True, True, 12800.0)))                       # 100 years apart
assert v == "not corroborated" and notes["T10.in_top1"] == "high windows, different peaks", (v, notes)
v, notes = fire.verdict(R(N20=mk(False, True), G20=mk(False, True)))
assert v == "unusual" and notes["T20.in_top5"] == "timing not checkable"
v, notes = fire.verdict(R(N60=mk(True, True), E60=mk(True, True, 12760.0), G60=mk(True, True)))   # GISP2 rescues the pair
assert v == "exceptional" and notes["T60.in_top1"].startswith("timing not checkable; NGRIP and NEEM"), notes
none = {s: None for s in fire.TIER_SERIES}
assert fire.verdict(none)[0] == "not testable"
assert fire.verdict({**none, "N10": no, "E10": no})[0] == "not met"
assert fire.verdict({**none, "N10": mk(True, True)})[0] == "not testable"                         # checked first
rk = fire.rank([{"k": 0, "E": 5.0, "E_age": 1.0}, {"k": 1, "E": 5.0, "E_age": 2.0}, {"k": 2, "E": 1.0, "E_age": 3.0}], "E")
assert rk["rank"] == 1 and rk["ties"] == 1 and abs(rk["fraction"] - 2 / 3) < 1e-12 and rk["top5_rank"] == 1 and rk["in_top5"]
print("all tests pass")
