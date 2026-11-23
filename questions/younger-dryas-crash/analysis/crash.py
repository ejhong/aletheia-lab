#!/usr/bin/env python3
"""Does the record of dated human activity drop at the Younger Dryas onset? (protocol.md)

    python analysis/crash.py                 # the locked run; writes results/
    python analysis/crash.py --calibrate     # before the lock: false-alarm rate of the whole procedure on made-up records

Run from questions/younger-dryas-crash. Needs numpy (the shared venv: numpy 2.3.5, Python 3.12).
"""
import csv
import json
import pathlib
import re
import sys

import numpy as np

Q = pathlib.Path(__file__).resolve().parent.parent
GRID = np.arange(9000, 17001, 5)
REGIONS = ["North America", "Europe", "Asia"]
TARGET, TIMES = 12850, np.arange(10800, 15201, 50)
AGE_LO, AGE_HI = 9000, 13800
WATER = re.compile(r"shell|marine|fish(?!er)|mollus|whale|seal|otolith|coral", re.I)
LAND_SHELL = re.compile(r"(nut|egg)\s*shell", re.I)


def read_curve(path=Q / "data" / "intcal20.14c"):
    rows = [line.split(",") for line in open(path) if line.strip() and not line.startswith("#")]
    t = np.array([float(r[0]) for r in rows])
    order = np.argsort(t)
    mu = np.interp(GRID, t[order], np.array([float(r[1]) for r in rows])[order])
    sig = np.interp(GRID, t[order], np.array([float(r[2]) for r in rows])[order])
    return mu, sig


def read_dates(path=Q / "data" / "p3k14c_scrubbed_fuzzed.csv", water=False):
    """{region: (ages, errors, site keys)} for the dates the protocol admits. water=True keeps aquatic materials too."""
    out = {r: ([], [], []) for r in REGIONS}
    dropped = {r: 0 for r in REGIONS}
    with open(path, encoding="utf-8") as f:
        for k, r in enumerate(csv.DictReader(f)):
            if r["Continent"] not in out:
                continue
            a, e = float(r["Age"]), float(r["Error"])
            if not (AGE_LO <= a <= AGE_HI and e > 0):
                continue
            text = LAND_SHELL.sub("", r["Material"] + " " + r["Taxa"])
            if not water and WATER.search(text):
                dropped[r["Continent"]] += 1
                continue
            site = ("id:" + r["SiteID"].strip()) if r["SiteID"].strip() else ("name:" + r["SiteName"].strip().lower()) if r["SiteName"].strip() else f"row:{k}"
            ages, errs, sites = out[r["Continent"]]
            ages.append(a)
            errs.append(e)
            sites.append(site)
    return {r: (np.array(a), np.array(e), s) for r, (a, e, s) in out.items()}, dropped


def calibrate(ages, errs, mu, sig):
    """One row per date: weights over the grid, each row summing to 1."""
    var = errs[:, None] ** 2 + sig[None, :] ** 2
    logw = -(ages[:, None] - mu[None, :]) ** 2 / (2 * var) - 0.5 * np.log(var)
    w = np.exp(logw - logw.max(axis=1, keepdims=True))
    return w / w.sum(axis=1, keepdims=True)


def bin_index(ages, sites):
    """For each date, the number of its bin: dates of one site in one 200-year span of radiocarbon age share a bin."""
    keys, out = {}, np.empty(len(ages), dtype=np.int64)
    for i, (a, s) in enumerate(zip(ages, sites)):
        out[i] = keys.setdefault((s, int(a // 200)), len(keys))
    return out, len(keys)


def summed(ages, errs, bins, mu, sig):
    """The summed curve: each bin's curve is the average of its dates' curves."""
    w = calibrate(ages, errs, mu, sig)
    size = np.bincount(bins)
    return (w / size[bins][:, None]).sum(axis=0)


def step(S, T, width=300):
    """ln(mean of S over [T - width, T) / mean over [T, T + width)). Negative = fewer dates after T. Works on [.., grid] arrays."""
    after = (GRID >= T - width) & (GRID < T)
    before = (GRID >= T) & (GRID < T + width)
    return np.log(S[..., after].mean(axis=-1) / S[..., before].mean(axis=-1))


def trend(S, degree=2):
    """A smooth trend through the summed curve (a polynomial in ln S), as a density over the grid points 9,500-16,500."""
    fit = (GRID >= 10500) & (GRID <= 15500)
    x = (GRID - 13000.0) / 1000.0
    coef = np.polyfit(x[fit], np.log(S[fit]), degree)
    dens = np.where((GRID >= 9500) & (GRID <= 16500), np.exp(np.polyval(coef, x)), 0.0)
    return dens / dens.sum()


def crash_density(dens, factor, lo=TARGET - 300, hi=TARGET):
    d = dens.copy()
    d[(GRID >= lo) & (GRID < hi)] *= factor
    return d / d.sum()


def made_up(dens, errs, bins, n_bins, mu, sig, rng, records):
    """Summed curves of made-up records with the real record's make-up: the same bins, each with its dates' errors.

    Every bin gets one calendar age from the density; its dates are separate measurements of that moment. Dates whose
    radiocarbon age falls outside the admitted span are dropped, as real ones would be.
    """
    out = np.empty((records, len(GRID)))
    for k in range(records):
        age = np.empty(len(bins))
        todo = np.ones(n_bins, dtype=bool)                       # bins still without a surviving date are drawn again
        for _ in range(50):
            if not todo.any():
                break
            t = rng.choice(len(GRID), size=n_bins, p=dens)
            curve_err = rng.normal(0, 1, n_bins) * sig[t]
            new = np.rint(mu[t][bins] + curve_err[bins] + rng.normal(0, 1, len(bins)) * errs)
            age[todo[bins]] = new[todo[bins]]
            alive = np.bincount(bins[(age >= AGE_LO) & (age <= AGE_HI)], minlength=n_bins) > 0
            todo = ~alive
        keep = (age >= AGE_LO) & (age <= AGE_HI)
        size = np.bincount(bins[keep], minlength=n_bins)
        w = calibrate(age[keep], errs[keep], mu, sig)
        out[k] = (w / size[bins[keep]][:, None]).sum(axis=0)
    return out


def p_low(null_steps, value):
    """The share of crash-free records with a step at or below this one, counting the value itself."""
    return (int((null_steps <= value).sum()) + 1) / (len(null_steps) + 1)


def detected(null_steps, value):
    return bool(value < 0 and p_low(null_steps, value) <= 0.01)


def analyse(ages, errs, sites, mu, sig, rng, width=300, target=TARGET, n_null=2000, n_crash=500, degree=2, full=True):
    bins, n_bins = bin_index(ages, sites)
    S = summed(ages, errs, bins, mu, sig)
    dens = trend(S, degree)
    null = made_up(dens, errs, bins, n_bins, mu, sig, rng, n_null)
    times = sorted(set(TIMES.tolist()) | {target})
    real = np.array([step(S, T, width) for T in times])
    sim = np.stack([step(null, T, width) for T in times], axis=1)                 # [records, times]
    z = (real - sim.mean(axis=0)) / sim.std(axis=0, ddof=1)
    k = times.index(target)
    grid_z = {T: float(z[i]) for i, T in enumerate(times) if T in set(TIMES.tolist())}
    order = sorted(grid_z, key=grid_z.get)
    out = {"dates": int(len(ages)), "bins": int(n_bins), "sites": len(set(sites)),
           "step_at_target": float(real[k]), "ratio_after_to_before": float(np.exp(real[k])),
           "ratio_expected": float(np.exp(sim[:, k].mean())), "ratio_expected_95": [float(np.exp(np.percentile(sim[:, k], q))) for q in (2.5, 97.5)],
           "z_at_target": float(z[k]), "p_at_target": p_low(sim[:, k], real[k]),
           "rank_of_target_among_times": (1 + sum(1 for T in grid_z if grid_z[T] < z[k])) if target in grid_z else None, "times": len(grid_z),
           "most_negative": [[T, round(grid_z[T], 2)] for T in order[:5]], "most_positive": [[T, round(grid_z[T], 2)] for T in order[::-1][:5]]}
    cases = [("halving", 0.5, 0)] + ([("drop_of_30_percent", 0.7, 0), ("halving_100_years_later", 0.5, -100), ("halving_100_years_earlier", 0.5, 100)] if full else [])
    for name, factor, shift in cases:
        crashed = step(made_up(crash_density(dens, factor, target - 300 + shift, target + shift), errs, bins, n_bins, mu, sig, rng, n_crash), target, width)
        out["power_" + name] = float(np.mean([detected(sim[:, k], v) for v in crashed]))
        if name == "halving":
            out["share_of_halvings_with_step_at_or_above_real"] = float((crashed >= real[k]).mean())
    if detected(sim[:, k], real[k]):
        out["verdict"] = "drop detected"
    elif out["share_of_halvings_with_step_at_or_above_real"] <= 0.01:
        out["verdict"] = "a halving is excluded"
    else:
        out["verdict"] = "cannot tell"
    w = calibrate(ages, errs, mu, sig) / np.bincount(bins)[bins][:, None]
    audit = {}
    for label, m in (("after", (GRID >= target - width) & (GRID < target)), ("before", (GRID >= target) & (GRID < target + width))):
        mass = w[:, m].sum(axis=1)
        by_site = {}
        for s, v in zip(sites, mass):
            by_site[s] = by_site.get(s, 0.0) + float(v)
        top = sorted(by_site.values(), reverse=True)
        audit[label] = {"mass": float(mass.sum()), "sites_with_mass_over_0.05": sum(1 for v in top if v > 0.05),
                        "share_of_top_site": top[0] / mass.sum(), "share_of_top_5_sites": sum(top[:5]) / mass.sum()}
    out["who_contributes"] = audit
    curves = {"S": S, "trend": dens, "times": times, "real": real, "z": z, "lo": np.percentile(sim, 2.5, axis=0), "hi": np.percentile(sim, 97.5, axis=0),
              "null_lo": np.percentile(null, 2.5, axis=0), "null_hi": np.percentile(null, 97.5, axis=0), "null_mean": null.mean(axis=0)}
    return out, curves


def overall(v):
    na = v["North America"]
    if na == "drop detected":
        return "supported as widespread" if "drop detected" in (v["Europe"], v["Asia"]) else "supported"
    return "not supported" if na == "a halving is excluded" else "undetermined"


def calibration_check(mu, sig, n_sets=100, n_null=200):
    """Made-up records from a known smooth trend, with North America's real make-up of bins and errors: how often does
    the whole procedure (fit a trend, make reference records, apply the rule) raise a false alarm?"""
    (ages, errs, sites), _ = read_dates()[0]["North America"], None
    bins, n_bins = bin_index(ages, sites)
    x = (GRID - 13000.0) / 1000.0
    truth = np.where((GRID >= 9500) & (GRID <= 16500), np.exp(-0.35 * x - 0.05 * x * x), 0.0)
    truth /= truth.sum()
    rng = np.random.default_rng(4040)
    ps, flags = [], 0
    for i in range(n_sets):
        t = rng.choice(len(GRID), size=n_bins, p=truth)
        age = np.rint(mu[t][bins] + (rng.normal(0, 1, n_bins) * sig[t])[bins] + rng.normal(0, 1, len(bins)) * errs)
        keep = (age >= AGE_LO) & (age <= AGE_HI)                 # a pseudo-observed record: selected on radiocarbon age, like the real one
        b2 = np.unique(bins[keep], return_inverse=True)[1]
        S = summed(age[keep], errs[keep], b2, mu, sig)
        null = step(made_up(trend(S), errs[keep], b2, int(b2.max()) + 1, mu, sig, rng, n_null), TARGET)
        v = step(S, TARGET)
        ps.append(p_low(null, v))
        flags += detected(null, v)
        if (i + 1) % 20 == 0:
            print(f"  {i + 1} made-up records: p at or below 0.05 in {sum(1 for p in ps if p <= 0.05)}, at or below 0.01 in {sum(1 for p in ps if p <= 0.01)}, flagged {flags}", flush=True)
    return {"records": n_sets, "p_at_or_below_0.05": sum(1 for p in ps if p <= 0.05), "p_at_or_below_0.01": sum(1 for p in ps if p <= 0.01),
            "p_at_or_above_0.95": sum(1 for p in ps if p >= 0.95), "flagged": int(flags), "median_p": float(np.median(ps))}


def main():
    mu, sig = read_curve()
    if "--calibrate" in sys.argv:
        out = calibration_check(mu, sig)
        json.dump(out, open(Q / "explore" / "calibration.json", "w"), indent=1)
        print(out)
        return
    dates, dropped = read_dates()
    rng = np.random.default_rng(40)
    out, curves = {}, {}
    for r in REGIONS:
        out[r], curves[r] = analyse(*dates[r], mu, sig, rng)
        out[r]["aquatic_dates_left_out"] = dropped[r]
        print(r, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in out[r].items() if k not in ("most_negative", "most_positive", "who_contributes")}, flush=True)
    result = {"regions": out, "overall": overall({r: out[r]["verdict"] for r in REGIONS}), "target": TARGET, "alongside": {}}
    side = result["alongside"]
    all_dates, _ = read_dates(water=True)
    variants = [("straight_line_trend", {"degree": 1}), ("aquatic_materials_kept", {}), ("errors_200_or_less", {}), ("largest_site_left_out", {}),
                ("window_200", {"width": 200}), ("window_500", {"width": 500}), ("target_12750", {"target": 12750}), ("target_12950", {"target": 12950})]
    for name, kw in variants:
        side[name] = {}
        for r in REGIONS:
            a, e, s = all_dates[r] if name == "aquatic_materials_kept" else dates[r]
            if name == "errors_200_or_less":
                keep = e <= 200
                a, e, s = a[keep], e[keep], [x for x, k in zip(s, keep) if k]
            if name == "largest_site_left_out":
                big = max(set(s), key=s.count)
                keep = np.array([x != big for x in s])
                a, e, s = a[keep], e[keep], [x for x in s if x != big]
            o, _ = analyse(a, e, s, mu, sig, rng, n_null=1000, n_crash=300, full=False, **kw)
            side[name][r] = {k: o[k] for k in ("dates", "bins", "ratio_after_to_before", "ratio_expected", "z_at_target", "p_at_target", "power_halving", "verdict")}
        print(name, {r: (round(side[name][r]["z_at_target"], 2), side[name][r]["p_at_target"], side[name][r]["verdict"]) for r in REGIONS}, flush=True)
    (Q / "results").mkdir(exist_ok=True)
    json.dump(result, open(Q / "results" / "summary.json", "w"), indent=1)
    with open(Q / "results" / "curves.tsv", "w") as f:
        f.write("region\tcal_bp\tsummed\tmade_up_mean\tmade_up_2.5\tmade_up_97.5\n")
        for r in REGIONS:
            c = curves[r]
            for i, t in enumerate(GRID):
                if 10000 <= t <= 16000:
                    f.write(f"{r}\t{t}\t{c['S'][i]:.5f}\t{c['null_mean'][i]:.5f}\t{c['null_lo'][i]:.5f}\t{c['null_hi'][i]:.5f}\n")
    with open(Q / "results" / "steps.tsv", "w") as f:
        f.write("region\tT\tstep\tz\tmade_up_2.5\tmade_up_97.5\n")
        for r in REGIONS:
            c = curves[r]
            for i, T in enumerate(c["times"]):
                f.write(f"{r}\t{T}\t{c['real'][i]:.5f}\t{c['z'][i]:.4f}\t{c['lo'][i]:.5f}\t{c['hi'][i]:.5f}\n")
    print("OVERALL:", result["overall"])


if __name__ == "__main__":
    main()
