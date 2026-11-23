#!/usr/bin/env python3
"""Unit tests for audit.py, on made-up data only (nothing under data/ is read).

    python analysis/test_audit.py            # from questions/gcp-audit, with the repository's .venv

Plain functions, no pytest. Each test prints its name and "ok" (or FAIL with the reason); the script exits
non-zero if any test fails. Every random draw uses a fixed seed.

Tolerances. Where a test compares a simulated mean or SD with its expected value, the tolerance is 4 standard
errors: SE(mean) = sd / sqrt(N) and SE(sd) ~= sd / sqrt(2N) for N simulated windows. A correct program fails such a
check with probability about 6e-5 per check, and with fixed seeds the outcome is reproducible anyway.
"""
import itertools
import math
import sys
import time

import numpy as np

sys.dont_write_bytecode = True  # keep analysis/ free of __pycache__

import audit

DAY = audit.DAY
SD = audit.SD
T0 = audit.ts("2020-03-01 00:00:00")  # a made-up day; any UTC midnight would do


def noise(rng, shape):
    """Trial sums of a perfect egg: binomial(200, 1/2), mean 100, SD sqrt(50)."""
    return rng.binomial(200, 0.5, shape).astype(np.float32)


def marker(t, egg):
    """A recognisable value for Unix second t and egg number e. It stays within 44.7 of 100 (never wild) and is
    exactly representable in float32 (an integer plus a multiple of 1/64), so equality checks are exact."""
    return 100.0 + ((np.asarray(t, dtype=np.int64) * 7) % 89 - 44) + egg / 64.0


def check(cond, msg):
    if not cond:
        raise AssertionError(msg)


# ---------------------------------------------------------------- 1. clean
def test_clean():
    x = np.array([[100, 55, 54.5, 145, 144.9, np.nan], [56, 144, 0, 200, 100, np.nan]], dtype=np.float32)
    before = x.copy()
    y = audit.clean(x)
    expect = np.array([[100, np.nan, np.nan, np.nan, 144.9, np.nan], [56, 144, np.nan, np.nan, 100, np.nan]], dtype=np.float32)
    check(np.array_equal(np.isnan(y), np.isnan(expect)), f"NaN pattern wrong: {y}")
    check(np.array_equal(y[~np.isnan(y)], expect[~np.isnan(expect)]), "kept values changed")
    check(np.array_equal(x, before, equal_nan=True), "clean modified its input")
    # boundaries exactly: 55 and 145 are wild (|x-100| = 45), 55.0001 and 144.9999 are not
    z = audit.clean(np.array([55.0, 145.0, 55.0001, 144.9999]))
    check(np.isnan(z[:2]).all() and not np.isnan(z[2:]).any(), f"boundary wrong: {z}")


# ---------------------------------------------------------------- 2. window
def make_reader(eggs_of_day, wild=()):
    """A reader whose day d has the egg numbers eggs_of_day(d) (in the given column order) and marker values;
    egg e is missing (NaN) at seconds t with (t + e) % 13 == 0; `wild` lists (t, egg) cells set to 150."""
    calls = []

    def reader(day):
        calls.append(day)
        t0 = audit.ts(day + " 00:00:00")
        eggs = eggs_of_day(day)
        t = t0 + np.arange(DAY)
        x = np.empty((DAY, len(eggs)), dtype=np.float32)
        for k, e in enumerate(eggs):
            x[:, k] = marker(t, e)
            x[(t + e) % 13 == 0, k] = np.nan
        for tw, e in wild:
            if t0 <= tw < t0 + DAY and e in eggs:
                x[tw - t0, eggs.index(e)] = 150
        return t0, list(eggs), x
    return reader, calls


def expected_window(start, seconds, eggs, present):
    """What window() should return given present(t, e) -> bool."""
    t = start + np.arange(seconds)
    out = np.full((seconds, len(eggs)), np.nan)
    for k, e in enumerate(eggs):
        m = present(t, e) & ((t + e) % 13 != 0)
        out[m, k] = marker(t[m], e)
    return out


def same(a, b):
    return a.shape == b.shape and np.array_equal(np.isnan(a), np.isnan(b)) and np.array_equal(a[~np.isnan(a)], b[~np.isnan(b)])


def test_window():
    # (a) inside one day
    reader, calls = make_reader(lambda d: [5, 2, 9])
    eggs, x = audit.window(T0 + 5000, 600, reader)
    check(eggs == [2, 5, 9], f"eggs {eggs}")
    check(calls == ["2020-03-01"], f"days read {calls}")
    check(x.dtype == np.float32, "dtype")
    check(same(x, expected_window(T0 + 5000, 600, eggs, lambda t, e: np.ones(t.size, bool))), "single-day values wrong")

    # (b) across midnight, different eggs on each side, unsorted column order in the reader
    day1, day2 = ["3", "7", "12"], ["7", "12", "20", "1"]
    reader, calls = make_reader(lambda d: [int(e) for e in (day1 if d == "2020-03-01" else day2)])
    start = T0 + DAY - 100
    eggs, x = audit.window(start, 300, reader)
    check(eggs == [1, 3, 7, 12, 20], f"eggs {eggs}")
    check(calls == ["2020-03-01", "2020-03-02"], f"days read {calls}")
    present = lambda t, e: ((t < T0 + DAY) & (str(e) in day1)) | ((t >= T0 + DAY) & (str(e) in day2))
    check(same(x, expected_window(start, 300, eggs, present)), "midnight-crossing values or columns wrong")
    check(np.isnan(x[100:, eggs.index(3)]).all() and np.isnan(x[:100, eggs.index(20)]).all(), "missing eggs not NaN")

    # (c) three days long, starting at noon: touches four days, egg sets change daily
    sets = {"2020-03-01": [1, 2], "2020-03-02": [2, 3], "2020-03-03": [3, 4, 1], "2020-03-04": [4]}
    reader, calls = make_reader(lambda d: sets[d])
    start, n = T0 + DAY // 2, 3 * DAY
    eggs, x = audit.window(start, n, reader)
    check(eggs == [1, 2, 3, 4] and calls == sorted(sets), f"eggs {eggs}, days {calls}")
    day_of = lambda t: np.array(["2020-03-0%d" % (1 + (v - T0) // DAY) for v in t])
    present = lambda t, e: np.array([e in sets[d] for d in day_of(t)])
    check(same(x, expected_window(start, n, eggs, present)), "three-day window wrong")

    # (d) the right seconds: first and last rows are exactly the markers of start and start+seconds-1,
    #     and a wild cell placed at a known second is removed
    reader, _ = make_reader(lambda d: [4], wild=[(T0 + 7777, 4)])
    eggs, x = audit.window(T0 + 7000, 1000, reader)
    check(x[0, 0] == marker(T0 + 7000, 4) and x[-1, 0] == marker(T0 + 7999, 4), "first/last second misaligned")
    check(np.isnan(x[777, 0]) and not np.isnan(x[776, 0]) and not np.isnan(x[778, 0]), "wild trial not removed at its second")


# ---------------------------------------------------------------- 3. sums and passes
def test_sums_passes():
    x = np.array([[101, np.nan], [97, 100], [np.nan, 104]], dtype=np.float32)
    n, tot, ss = audit.sums(x)
    check(list(n) == [2, 2] and list(tot) == [-2, 4] and list(ss) == [10, 16], f"sums {n} {tot} {ss}")

    rng = np.random.default_rng(3)
    for seconds in (600, DAY):
        good = noise(rng, (seconds, 1))
        few = good.copy()
        few[: seconds // 2 + 1] = np.nan                       # n = seconds/2 - 1 < seconds/2
        exactly_half = good.copy()
        exactly_half[: seconds // 2] = np.nan                  # n = seconds/2 : allowed
        # mean shifted by 8 SE of the window mean (limit is 5)
        shifted = good + np.float32(8 * SD / math.sqrt(seconds))
        # variance off: limit is |ss/n/50 - 1| <= 5 / sqrt(n/2); use 2.5 times the limit
        f = 1 + 2.5 * 5 / math.sqrt(seconds / 2)
        wide = (100 + (good - 100) * np.float32(math.sqrt(f)))
        empty = np.full((seconds, 1), np.nan, dtype=np.float32)
        x = np.hstack([good, few, exactly_half, shifted, wide, empty])
        got = audit.passes(*audit.sums(x), seconds)
        check(list(got) == [True, False, True, False, False, False], f"seconds={seconds}: passes gave {list(got)}")

    # ordinary noise passes in nearly all windows: 200 eggs x 600 s; the two-sided 5-sigma check on mean and on
    # variance rejects a perfect egg with probability ~1e-6, so all 200 should pass
    got = audit.passes(*audit.sums(noise(rng, (600, 200))), 600)
    check(got.all(), f"{(~got).sum()} of 200 noise eggs failed")


# ---------------------------------------------------------------- 4. score under noise
def simulate_null(seconds, windows, eggs, rng, missing=0.05):
    zs = np.empty(windows)
    for i in range(windows):
        x = noise(rng, (seconds, eggs))
        x[rng.random(x.shape) < missing] = np.nan
        zs[i] = audit.score(x, SD, seconds)["z"]
    return zs


NULL_REPORT = {}


def test_score_null():
    rng = np.random.default_rng(4)
    for seconds, windows in ((60, 20000), (600, 6000), (21600, 600)):
        zs = simulate_null(seconds, windows, 8, rng)
        m, s = zs.mean(), zs.std(ddof=1)
        NULL_REPORT[seconds] = (windows, m, s, (zs > 1.645).mean(), (zs > 2.326).mean())
        print(f"    {seconds:>6} s, {windows} windows: mean {m:+.4f}  sd {s:.4f}  "
              f"P(z>1.645) {(zs > 1.645).mean():.4f} (0.05)  P(z>2.326) {(zs > 2.326).mean():.4f} (0.01)")
        check(abs(m) <= 4 / math.sqrt(windows), f"{seconds} s: mean {m}")
        check(abs(s - 1) <= 4 / math.sqrt(2 * windows), f"{seconds} s: sd {s}")


# ---------------------------------------------------------------- 5. score with a shared signal
def test_score_shared():
    rng = np.random.default_rng(5)
    seconds, eggs = 3600, 10
    x = noise(rng, (seconds, eggs)) + rng.normal(0, 1.0, (seconds, 1)).astype(np.float32)
    # each pair of eggs now has correlation ~1/51, so E[Z^2] ~ 1 + 9/51 and the expected score is about
    # (1.176^(1/3) - 1 + k)/sqrt(k), k = 2/(9*3600): ~7.0. Require > 4, far beyond chance (noise SD is 1).
    z = audit.score(x, SD, seconds)["z"]
    print(f"    shared wobble (SD 1 trial unit), 10 eggs, 3600 s: score {z:.2f}")
    check(z > 4, f"score {z}")


# ---------------------------------------------------------------- 6. evaluability
def test_score_evaluable():
    rng = np.random.default_rng(6)
    x = noise(rng, (100, 3))
    y = x.copy(); y[80:] = np.nan                               # 80 of 100 seconds: evaluable
    r = audit.score(y, SD, 100)
    check(r is not None and r["df"] == 80, f"80% gave {r}")
    y = x.copy(); y[79:] = np.nan                               # 79 of 100: not evaluable
    check(audit.score(y, SD, 100) is None, "79% should be None")
    # seconds with only NaN are not counted; seconds with one egg are; hand-computed chi-square
    x = np.array([[107, 93], [np.nan, np.nan], [114, np.nan], [100, 100], [np.nan, 86]], dtype=np.float32)
    r = audit.score(x, np.array([7.0, 7.0]), 5)
    # z: (1,-1) -> Z=0 ; (2) -> Z=2 ; (0,0) -> 0 ; (-2) -> -2 : chi2 = 8, df = 4
    check(r["df"] == 4 and abs(r["chi2"] - 8) < 1e-12 and r["eggs_median"] == 1.5, f"hand case {r}")
    check(abs(r["z"] - audit.wilson_hilferty(8.0, 4)) < 1e-12, "z not WH of chi2")
    check(audit.score(np.array([[100.0]]), SD, 1) is None, "df < 2 must be None")


# ---------------------------------------------------------------- 7. cross_part
def test_cross_part():
    rng = np.random.default_rng(7)
    seconds, eggs, windows = 3600, 10, 200
    res = {}
    for name in ("noise", "one wide egg", "shared wobble"):
        sc, cr = [], []
        for _ in range(windows):
            x = noise(rng, (seconds, eggs))
            if name == "one wide egg":
                x[:, 0] = 100 + (x[:, 0] - 100) * 1.2          # variance x1.44 in one egg only
            if name == "shared wobble":
                x += rng.normal(0, 1.0, (seconds, 1)).astype(np.float32)
            sc.append(audit.score(x, SD, seconds)["z"])
            cr.append(audit.cross_part(x, SD))
        res[name] = (np.mean(sc), np.mean(cr), np.std(cr, ddof=1))
        print(f"    {name:>13}: mean score {res[name][0]:+.3f}  mean cross {res[name][1]:+.3f}  sd cross {res[name][2]:.3f}")
    se = 1.1 / math.sqrt(windows)   # cross_part has SD 1 under noise and ~1.04 with one wide egg (computed); 1.1 covers both
    m, c, s = res["noise"]
    check(abs(m) < 4 / math.sqrt(windows) and abs(c) < 4 * se and abs(s - 1) < 4 / math.sqrt(2 * windows), f"noise {res['noise']}")
    m, c, _ = res["one wide egg"]
    # expected score ~ ((1 + 0.44/10)^(1/3) - 1 + k)/sqrt(k) ~ 1.85; cross stays centred on 0
    check(m > 1.0 and abs(c) < 4 * se, f"wide egg {res['one wide egg']}")
    # expected cross ~ 3600 * 9 * (1/50) / sqrt(3600 * 2 * 9/10) ~ 8.0
    check(res["shared wobble"][1] > 5, f"wobble {res['shared wobble']}")
    check(audit.cross_part(np.array([[100.0, np.nan]]), SD) is None, "no second with 2 eggs should give None")


# ---------------------------------------------------------------- 8. pool_of_day
def test_pool_of_day():
    eggs = [11, 4]
    x = np.full((DAY, 2), 101, dtype=np.float32)                # deviation 1 everywhere ...
    x[1000:2000] = 103                                          # ... 3 inside the first blocked stretch
    x[0:100] = 103                                              # ... 3 inside the stretch that starts before the day
    x[DAY - 50:] = 103                                          # ... 3 inside the stretch that runs past the day
    x[5000:5010, 0] = 150                                       # 10 wild trials in egg 11 (outside any block)
    x[6000:6020, 1] = 54                                        # 20 wild trials in egg 4
    x[7000:7030, 1] = np.nan                                    # 30 missing in egg 4
    reader = lambda d: (T0, eggs, x)
    blocked = [(T0 + 1000, T0 + 1999),                          # inside, inclusive ends: 1000 s
               (T0 - 500, T0 + 99),                             # starts the day before: 100 s
               (T0 + DAY - 50, T0 + DAY + 1000),                # runs into the next day: 50 s
               (T0 - 2000, T0 - 1),                             # entirely before
               (T0 + DAY, T0 + DAY + 99)]                       # entirely after
    p = audit.pool_of_day("2020-03-01", blocked, reader)
    kept = DAY - 1150
    check(p == {11: (kept - 10, float(kept - 10)), 4: (kept - 50, float(kept - 50))}, f"pool {p}")
    check(audit.pool_of_day("2020-03-01", [], reader)[11][0] == DAY - 10, "no blocks: all non-wild trials")


# ---------------------------------------------------------------- 9. score_window end to end
def wide_reader(seed, eggs, var):
    """Days of float trial sums with true variance `var` (not 50)."""
    cache = {}

    def reader(day):
        if day not in cache:
            t0 = audit.ts(day + " 00:00:00")
            rng = np.random.default_rng([seed, t0 // DAY])
            cache[day] = (t0, list(eggs), (100 + rng.standard_normal((DAY, len(eggs))) * math.sqrt(var)).astype(np.float32))
        return cache[day]
    return reader


SW_REPORT = {}


def test_score_window():
    eggs, seconds, sims = list(range(1, 7)), 3600, 300
    main, theory, dropped = [], [], 0
    for i in range(sims):
        reader = wide_reader(1000 + i, eggs, 1.03 * 50)
        pool = {}
        for d in ("2020-03-01", "2020-03-03"):                  # reference days, not the window's day
            for e, (n, ss) in audit.pool_of_day(d, [], reader).items():
                a, b = pool.get(e, (0, 0.0)); pool[e] = (a + n, b + ss)
        r = audit.score_window(T0 + DAY + 40000, seconds, pool, {}, reader)
        dropped += 6 - r["eggs_passing"]                        # eggs failing the 5-sigma egg check by chance
        main.append(r["main"]["z"]); theory.append(r["theory"]["z"])
    k = 2 / (9 * seconds)
    expect_theory = (1.03 ** (1 / 3) - 1 + k) / math.sqrt(k)
    mm, mt = np.mean(main), np.mean(theory)
    SW_REPORT.update(sims=sims, main=(mm, np.std(main, ddof=1)), theory=(mt, np.std(theory, ddof=1)), expect=expect_theory)
    print(f"    variance 1.03x theory, {sims} windows of {seconds} s, 6 eggs: main mean {mm:+.3f} sd {np.std(main, ddof=1):.3f}; "
          f"theory mean {mt:+.3f} sd {np.std(theory, ddof=1):.3f} (expected {expect_theory:.3f})")
    print(f"    eggs dropped by the egg check: {dropped} of {6 * sims}")
    # with true variance 1.03 x 50 the variance statistic is centred at 0.03*sqrt(1800) = 1.27, so the 5-sigma limit
    # drops ~1e-4 of eggs (more with the chi-square skew); more than 10 of 1800 would mean the check misbehaves
    check(dropped <= 10, f"{dropped} eggs dropped")
    check(abs(mm) < 4 / math.sqrt(sims), f"main biased: {mm}")
    check(abs(mt - expect_theory) < 4 / math.sqrt(sims), f"theory mean {mt} vs {expect_theory}")

    # an egg with too small a pool is not used, and the score equals the score of the other eggs alone
    reader = wide_reader(7, [1, 2, 3], 50)
    start = T0 + 1000
    _, x = audit.window(start, seconds, reader)
    pool = {1: (200000, 200000 * 50.0), 2: (200000, 200000 * 60.0), 3: (86399, 86399 * 50.0)}
    r = audit.score_window(start, seconds, pool, {}, reader)
    alone = audit.score(x[:, :2], np.sqrt(np.array([50.0, 60.0])), seconds)
    check(r["eggs_passing"] == 2 and r["eggs_seen"] == 3 and abs(r["main"]["chi2"] - alone["chi2"]) < 1e-9, f"small pool {r}")
    pool[3] = (86400, 86400 * 50.0)                             # exactly REF_TRIALS: used
    check(audit.score_window(start, seconds, pool, {}, reader)["eggs_passing"] == 3, "pool of exactly 86400 should count")
    # an egg missing from the pool entirely is not used
    check(audit.score_window(start, seconds, {1: pool[1], 2: pool[2]}, {}, reader)["eggs_passing"] == 2, "egg absent from pool used")

    # own trials are taken out of the reference: pool = window's own trials (~3600) + 84,000 others (variance 200):
    # 87,600 in all, enough only if the window's own trials are counted.
    n, _, ss = audit.sums(x)
    own = {e: (int(a), float(b)) for e, a, b in zip([1, 2, 3], n, ss)}
    pool = {e: (own[e][0] + 84000, own[e][1] + 84000 * 200.0) for e in own}
    r = audit.score_window(start, seconds, pool, own, reader)
    check(r["eggs_passing"] == 0 and r["main"] is None, f"pool only big enough thanks to the window: {r}")
    check(audit.score_window(start, seconds, pool, {}, reader)["eggs_passing"] == 3, "without own the eggs should count")
    # with 90,000 others (variance 200), the reference SD must be exactly sqrt(200) -- the window's trials removed
    pool = {e: (own[e][0] + 90000, own[e][1] + 90000 * 200.0) for e in own}
    r = audit.score_window(start, seconds, pool, own, reader)
    ref = audit.score(x, np.full(3, math.sqrt(200.0)), seconds)
    check(r["eggs_passing"] == 3 and abs(r["main"]["chi2"] - ref["chi2"]) < 1e-6 * ref["chi2"], f"reference not window-free: {r['main']} vs {ref}")
    # and a window with too few eggs gives None for every score
    r = audit.score_window(start, seconds, {1: pool[1]}, {}, reader)
    check(r["main"] is None and r["theory"] is None and r["cross"] is None, "one egg should give no scores")


# ---------------------------------------------------------------- 10. wilson_hilferty against exact values
def chi2_cdf_even(x, df):
    """(P(chi2 <= x), P(chi2 > x)) for even df = 2m, exactly, via the Poisson identity
    P(chi2_{2m} > x) = P(N <= m-1), N ~ Poisson(x/2). Terms are built as ratios to the Poisson mode (no lgamma),
    and both tails are summed directly so neither suffers cancellation."""
    assert df % 2 == 0
    m, lam = df // 2, x / 2
    mode = int(lam)
    width = int(60 * math.sqrt(lam + 1) + 100)
    lo, hi = max(0, mode - width), mode + width
    logr = {mode: 0.0}
    acc = 0.0
    for k in range(mode + 1, hi + 1):
        acc += math.log(lam / k); logr[k] = acc
    acc = 0.0
    for k in range(mode, lo, -1):
        acc += math.log(k / lam); logr[k - 1] = acc
    terms = {k: math.exp(v) for k, v in logr.items() if v > -745}
    total = math.fsum(terms.values())
    upper = math.fsum(v for k, v in terms.items() if k <= m - 1) / total   # P(chi2 > x)
    lower = math.fsum(v for k, v in terms.items() if k >= m) / total       # P(chi2 <= x)
    return lower, upper


def normal_quantile(lower, upper):
    """z with Phi(z) = lower, using whichever tail is smaller; bisection on math.erfc."""
    p, sign = (lower, 1) if lower < upper else (upper, -1)
    a, b = -40.0, 0.0                                           # Phi(t) = p <= 1/2 has t <= 0
    for _ in range(200):
        c = (a + b) / 2
        if 0.5 * math.erfc(-c / math.sqrt(2)) < p:
            a = c
        else:
            b = c
    return sign * (a + b) / 2


WH_REPORT = []


def test_wilson_hilferty():
    # the exact method checked against closed forms first: df=2 survival exp(-x/2); df=10 survival
    # exp(-x/2) sum_{k<5} (x/2)^k / k!
    for x in (0.5, 2.0, 7.3):
        lo, up = chi2_cdf_even(x, 2)
        check(abs(up - math.exp(-x / 2)) < 1e-14 and abs(lo + up - 1) < 1e-14, f"df=2 exact check at {x}")
    for x in (3.0, 10.0, 25.0):
        up10 = math.exp(-x / 2) * sum((x / 2) ** k / math.factorial(k) for k in range(5))
        check(abs(chi2_cdf_even(x, 10)[1] - up10) < 1e-14, f"df=10 exact check at {x}")
    # the reference point mentioned in the brief, derived here: df = 1000 at chi2 = 1000
    z1000 = normal_quantile(*chi2_cdf_even(1000.0, 1000))
    print(f"    exact normal equivalent of chi2 = df = 1000: {z1000:+.6f}  (WH {audit.wilson_hilferty(1000.0, 1000):+.6f})")

    # Bounds on |WH - exact|: (within 2 SD of the mean, anywhere from -2 to +4 SD). They record the accuracy
    # observed with the exact method above (error shrinks roughly like 1/df and grows in the tails); a change to
    # wilson_hilferty that is not the textbook formula would break them by orders of magnitude.
    bounds = {2: (0.02, 0.02), 10: (0.15, 0.15), 600: (2e-4, 2e-3), 86400: (1e-6, 2e-5)}
    for df in (2, 10, 600, 86400):
        worst, worst_central = 0.0, 0.0
        for c in (-2.0, -1.0, 0.0, 1.0, 2.0, 3.0, 4.0):
            x = df + c * math.sqrt(2 * df)
            if x <= 0:
                continue
            exact = normal_quantile(*chi2_cdf_even(x, df))
            wh = audit.wilson_hilferty(x, df)
            WH_REPORT.append((df, c, x, exact, wh))
            worst = max(worst, abs(wh - exact))
            if abs(c) <= 2:
                worst_central = max(worst_central, abs(wh - exact))
            print(f"    df {df:>6}  chi2 {x:>12.3f} (mean{c:+.0f} sd)  exact z {exact:+.6f}  WH {wh:+.6f}  error {wh - exact:+.2e}")
        check(worst_central < bounds[df][0] and worst < bounds[df][1], f"df {df}: worst WH error {worst_central}, {worst}")


# ---------------------------------------------------------------- 11. sign_flip
def test_sign_flip():
    # all positive, n=20: exact p = 2^-20 ~ 1e-6; the estimator gives (hits+1)/200001 with hits ~ 0.2, so ~5e-6
    p = audit.sign_flip(np.arange(1, 21, dtype=float))
    check(p < 2e-5, f"all positive p {p}")
    # n=8 all positive: exact 1/256 = 0.0039; binomial SE at 200,000 draws ~1.4e-4; tolerance 4 SE
    p = audit.sign_flip(np.ones(8) * 3.0)
    check(abs(p - 1 / 256) < 6e-4, f"n=8 p {p}")
    # symmetric differences: obs = 0, p = P(S >= 0) = (1 + P(S=0))/2, enumerated exactly; SE <= 0.0012, tol 0.005
    for d in ([1.0, -1.0, 2.0, -2.0, 3.0, -3.0], [0.37, -0.37, 1.9, -1.9, 2.6, -2.6, 0.81, -0.81]):
        d = np.array(d)
        exact = np.mean([np.dot(s, d) >= d.sum() - 1e-12 for s in itertools.product((-1, 1), repeat=d.size)])
        p = audit.sign_flip(d)
        print(f"    symmetric {d.size} differences: p {p:.4f}, exact {exact:.4f}")
        check(abs(p - exact) < 0.005 and p >= 0.5, f"symmetric p {p} vs {exact}")
    # same seed, same answer; another seed differs only by Monte Carlo noise
    d = np.random.default_rng(11).normal(0.2, 1, 30)
    check(audit.sign_flip(d) == audit.sign_flip(d), "not reproducible")
    check(abs(audit.sign_flip(d) - audit.sign_flip(d, seed=1)) < 0.01, "seed changes p by more than MC noise")


# ---------------------------------------------------------------- 12. combine and verdicts
def test_combine_verdicts():
    c = audit.combine([1.0, None, 2.0, 3.0])
    check(c["n"] == 3 and abs(c["z"] - 6 / math.sqrt(3)) < 1e-12 and c["mean"] == 2.0 and abs(c["sd"] - 1.0) < 1e-12, f"{c}")
    check(audit.combine([None]) == {"n": 0, "z": None, "mean": None, "sd": None}, "empty")
    check(audit.combine([2.0])["sd"] is None and audit.combine([2.0])["z"] == 2.0, "single")

    rep = lambda r, a, b: {"r": r, "combined_ours": a, "combined_published": b}
    ok_rep = rep(0.95, 3.0, 3.5)
    co_ok = {"z": 0.0, "sd": 1.0}
    V = lambda ev=1.0, co=co_ok, p=0.5, r=ok_rep: audit.verdicts({"z": ev}, co, p, r)
    # reproduction (values chosen to be exact in binary floating point at the boundaries)
    check(V(r=rep(0.9, 3.0, 2.0))["reproduction"] == "reproduces closely", "r=0.9, diff=1.0 boundary")
    check(V(r=rep(0.9, 3.0, 1.75))["reproduction"] == "reproduces roughly", "diff 1.25")
    check(V(r=rep(0.89, 3.0, 3.0))["reproduction"] == "reproduces roughly", "r 0.89")
    check(V(r=rep(0.7, 3.0, 1.0))["reproduction"] == "reproduces roughly", "r=0.7, diff=2.0 boundary")
    check(V(r=rep(0.69, 3.0, 3.0))["reproduction"] == "does not reproduce", "r 0.69")
    check(V(r=rep(0.99, 3.0, 0.75))["reproduction"] == "does not reproduce", "diff 2.25")
    # events
    check(V(ev=3.09)["events"] == "departure" and V(ev=3.0899)["events"] == "suggestive", "3.09 boundary")
    check(V(ev=1.645)["events"] == "suggestive" and V(ev=1.6449)["events"] == "no positive excess detected", "1.645 boundary")
    # controls
    for co, lab in (({"z": 2.58, "sd": 1.0}, "calibration in doubt"), ({"z": -2.58, "sd": 1.0}, "calibration in doubt"),
                    ({"z": 2.5799, "sd": 1.0}, "controls look like chance"), ({"z": 0.0, "sd": 0.75}, "controls look like chance"),
                    ({"z": 0.0, "sd": 1.3}, "controls look like chance"), ({"z": 0.0, "sd": 0.7499}, "calibration in doubt"),
                    ({"z": 0.0, "sd": 1.3001}, "calibration in doubt")):
        check(V(co=co)["controls"] == lab, f"controls {co}")
    # overall
    check(V(ev=3.09, p=0.01)["overall"] == "the excess is in the event windows", "events boundary")
    check(V(ev=3.09, p=0.0101)["overall"] == "mixed", "p just above 0.01")
    check(V(ev=3.5, p=0.001, co={"z": 0.0, "sd": 1.4})["overall"] == "mixed", "calibration doubt blocks the events label")
    check(V(ev=1.0, p=0.0501, co={"z": 2.58, "sd": 1.0})["overall"] == "the excess is not specific to the events", "controls high")
    check(V(ev=3.5, p=0.05, co={"z": 2.58, "sd": 1.0})["overall"] == "mixed", "p = 0.05 is not > 0.05")
    check(V(ev=1.0, p=0.05, co={"z": 2.58, "sd": 1.0})["overall"] == "no excess found", "falls through to no excess")
    check(V(ev=1.6449)["overall"] == "no excess found" and V(ev=1.645)["overall"] == "mixed", "1.645 overall boundary")


# ---------------------------------------------------------------- documented behaviours (not failures)
def test_documented_behaviour():
    """Things a reader of the results should know; each assertion states what audit.py does now."""
    # (a) the egg variance check tightens with window length: a 3%-wide egg passes in a 3600 s window but fails in a
    #     day-long one (limit 5/sqrt(n/2) = 0.024 at n = 86400). Deterministic construction: exact 3% excess.
    rng = np.random.default_rng(12)
    for seconds, expect in ((3600, True), (DAY, False)):
        g = rng.standard_normal(seconds)
        g = (g - g.mean()) / g.std()                            # mean exactly 0, variance exactly 1
        x = (100 + g * math.sqrt(51.5)).reshape(-1, 1)
        check(bool(audit.passes(*audit.sums(x), seconds)[0]) == expect, f"3% egg, {seconds} s")
    # (b) verdicts raise TypeError when a needed number is missing (fewer than 3 scored events -> r is None,
    #     a single control -> sd is None). summarise() can produce these for small subsets, but main() only calls
    #     verdicts() on the full set, so this matters only if the full set is that small.
    for args in (({"z": 1.0}, {"z": 0.0, "sd": None}, 0.5, {"r": 0.9, "combined_ours": 1, "combined_published": 1}),
                 ({"z": 1.0}, {"z": 0.0, "sd": 1.0}, 0.5, {"r": None, "combined_ours": 1, "combined_published": 1})):
        try:
            audit.verdicts(*args)
            raise AssertionError("expected TypeError")
        except TypeError:
            pass
    # (c) own-subtraction assumes every trial in `own` is also in the pool. If part of the control window lies in a
    #     blocked stretch, pool_of_day left those trials out but score_window still subtracts them, so n_ref and
    #     ss_ref are too small (here: reference variance comes out wrong). Demonstrated with a made-up blocked stretch.
    reader = wide_reader(21, [1, 2], 50)
    start, seconds = T0 + 3000, 3600
    blocked = [(start, start + 1799)]                           # first half of the control window is blocked
    pool = {}
    for d in ("2020-03-01", "2020-03-02"):
        for e, (n, ss) in audit.pool_of_day(d, blocked, reader).items():
            a, b = pool.get(e, (0, 0.0)); pool[e] = (a + n, b + ss)
    _, x = audit.window(start, seconds, reader)
    n, _, ss = audit.sums(x)
    own = {e: (int(a), float(b)) for e, a, b in zip([1, 2], n, ss)}
    first, second = (~np.isnan(x[:1800, 0])).sum(), (~np.isnan(x[1800:, 0])).sum()
    correct_n_ref = pool[1][0] - int(second)                    # only the unblocked half was ever in the pool
    n_ref_used = pool[1][0] - own[1][0]
    check(n_ref_used == correct_n_ref - int(first), "n_ref under-counts by the blocked part of the window")


TESTS = [test_clean, test_window, test_sums_passes, test_score_null, test_score_shared, test_score_evaluable,
         test_cross_part, test_pool_of_day, test_score_window, test_wilson_hilferty, test_sign_flip, test_combine_verdicts,
         test_documented_behaviour]


def main():
    failed = []
    t_all = time.time()
    for t in TESTS:
        t1 = time.time()
        try:
            t()
            print(f"{t.__name__} ok ({time.time() - t1:.1f} s)", flush=True)
        except Exception as exc:  # report and carry on
            failed.append(t.__name__)
            print(f"{t.__name__} FAIL: {type(exc).__name__}: {exc}", flush=True)
    print(f"{len(TESTS) - len(failed)} of {len(TESTS)} passed in {time.time() - t_all:.1f} s")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
