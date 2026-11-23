#!/usr/bin/env python3
"""Does the record of dated human activity drop at the Younger Dryas onset? (protocol.md)

    python analysis/crash.py        # the locked run; writes results/

Run from questions/younger-dryas-crash. Needs numpy (the shared venv: numpy 2.3.5, Python 3.12).
"""
import csv
import json
import math
import pathlib

import numpy as np

Q = pathlib.Path(__file__).resolve().parent.parent
GRID = np.arange(9000, 17001, 5)
REGIONS = ["North America", "Europe", "Asia"]
TARGET, TIMES = 12850, np.arange(10800, 15201, 50)
N_NULL, N_CRASH = 1000, 300


def read_curve(path=Q / "data" / "intcal20.14c"):
    rows = [line.split(",") for line in open(path) if line.strip() and not line.startswith("#")]
    t = np.array([float(r[0]) for r in rows])
    order = np.argsort(t)
    mu = np.interp(GRID, t[order], np.array([float(r[1]) for r in rows])[order])
    sig = np.interp(GRID, t[order], np.array([float(r[2]) for r in rows])[order])
    return mu, sig


def read_dates(path=Q / "data" / "p3k14c_scrubbed_fuzzed.csv"):
    """{region: (ages, errors, site keys)} for the dates the protocol admits."""
    out = {r: ([], [], []) for r in REGIONS}
    with open(path, encoding="utf-8") as f:
        for k, r in enumerate(csv.DictReader(f)):
            if r["Continent"] not in out:
                continue
            a, e = float(r["Age"]), float(r["Error"])
            if 9000 <= a <= 13800 and e > 0:
                site = r["SiteID"].strip() or r["SiteName"].strip().lower() or f"\0row{k}"
                ages, errs, sites = out[r["Continent"]]
                ages.append(a)
                errs.append(e)
                sites.append(site)
    return {r: (np.array(a), np.array(e), s) for r, (a, e, s) in out.items()}


def calibrate(ages, errs, mu, sig):
    """One row per date: weights over the grid, each row summing to 1."""
    var = errs[:, None] ** 2 + sig[None, :] ** 2
    w = np.exp(-(ages[:, None] - mu[None, :]) ** 2 / (2 * var)) / np.sqrt(var)
    return w / w.sum(axis=1, keepdims=True)


def summed(ages, errs, sites, mu, sig):
    """The summed curve of a region, with dates of one site in one 200-year span of radiocarbon age averaged first."""
    w = calibrate(ages, errs, mu, sig)
    keys = {}
    for i, (a, s) in enumerate(zip(ages, sites)):
        keys.setdefault((s, int(a // 200)), []).append(i)
    S = np.zeros(len(GRID))
    for idx in keys.values():
        S += w[idx].mean(axis=0)
    return S, len(keys)


def step(S, T, width=300):
    """ln(mean of S over [T - width, T) / mean over [T, T + width)). Negative = fewer dates after T. Works on [.., grid] arrays."""
    after = (GRID >= T - width) & (GRID < T)
    before = (GRID >= T) & (GRID < T + width)
    return np.log(S[..., after].mean(axis=-1) / S[..., before].mean(axis=-1))


def trend(S):
    """The exponential trend through the summed curve, as a density over the grid points from 9,500 to 16,500."""
    fit = (GRID >= 10500) & (GRID <= 15500)
    slope, intercept = np.polyfit(GRID[fit], np.log(S[fit]), 1)
    dens = np.where((GRID >= 9500) & (GRID <= 16500), np.exp(intercept + slope * GRID), 0.0)
    return dens / dens.sum(), float(slope)


def made_up(dens, n, errs, mu, sig, rng, records, chunk=50):
    """Summed curves of made-up records drawn from a calendar density and passed through the dating process."""
    out = np.empty((records, len(GRID)))
    for start in range(0, records, chunk):
        m = min(chunk, records - start)
        t = rng.choice(len(GRID), size=(m, n), p=dens)
        e = rng.choice(errs, size=(m, n))
        age = np.rint(mu[t] + rng.normal(0, 1, (m, n)) * sig[t] + rng.normal(0, 1, (m, n)) * e)
        for k in range(m):
            out[start + k] = calibrate(age[k], e[k], mu, sig).sum(axis=0)
    return out


def crash_density(dens, factor, T=TARGET):
    d = dens.copy()
    d[(GRID >= T - 300) & (GRID < T)] *= factor
    return d / d.sum()


def analyse(ages, errs, sites, mu, sig, rng, width=300, target=TARGET, n_null=N_NULL, n_crash=N_CRASH, full=True):
    S, n_bins = summed(ages, errs, sites, mu, sig)
    dens, slope = trend(S)
    null = made_up(dens, n_bins, errs, mu, sig, rng, n_null)
    times = sorted(set(TIMES.tolist()) | {target})
    real = np.array([step(S, T, width) for T in times])
    sim = np.stack([step(null, T, width) for T in times], axis=1)                 # [records, times]
    z = (real - sim.mean(axis=0)) / sim.std(axis=0, ddof=1)
    k = times.index(target)
    p = (int((sim[:, k] <= real[k]).sum()) + 1) / (n_null + 1)
    grid_z = {T: float(z[i]) for i, T in enumerate(times) if T in set(TIMES.tolist())}
    order = sorted(grid_z, key=grid_z.get)
    out = {"dates": int(len(ages)), "bins": int(n_bins), "sites": len(set(sites)), "trend_slope_per_year": slope,
           "step_at_target": float(real[k]), "made_up_mean_at_target": float(sim[:, k].mean()), "made_up_sd_at_target": float(sim[:, k].std(ddof=1)),
           "z_at_target": float(z[k]), "p_at_target": p,
           "rank_of_target_among_times": (1 + sum(1 for T in grid_z if grid_z[T] < z[k])) if target in grid_z else None, "times": len(grid_z),
           "most_negative": [[T, round(grid_z[T], 2)] for T in order[:5]], "most_positive": [[T, round(grid_z[T], 2)] for T in order[::-1][:5]]}
    cut = float(np.percentile(sim[:, k], 1))
    for factor, name in ((0.5, "power_halving"), (0.7, "power_30_percent")):
        if full or factor == 0.5:
            crashed = made_up(crash_density(dens, factor, target), n_bins, errs, mu, sig, rng, n_crash)
            out[name] = float((step(crashed, target, width) <= cut).mean())
    detected = out["step_at_target"] < 0 and p <= 0.01
    out["verdict"] = "drop detected" if detected else "no drop, and a halving would have shown" if out["power_halving"] >= 0.8 else "cannot tell"
    curves = {"S": S, "trend": dens * S[(GRID >= 9500) & (GRID <= 16500)].sum(), "times": times, "real": real, "z": z,
              "lo": np.percentile(sim, 2.5, axis=0), "hi": np.percentile(sim, 97.5, axis=0),
              "null_lo": np.percentile(null, 2.5, axis=0), "null_hi": np.percentile(null, 97.5, axis=0)}
    return out, curves


def overall(v):
    na = v["North America"]
    if na == "drop detected":
        return "supported as widespread" if "drop detected" in (v["Europe"], v["Asia"]) else "supported"
    return "not supported" if na == "no drop, and a halving would have shown" else "undetermined"


def main():
    mu, sig = read_curve()
    dates = read_dates()
    rng = np.random.default_rng(40)
    out, curves = {}, {}
    for r in REGIONS:
        out[r], curves[r] = analyse(*dates[r], mu, sig, rng)
        print(r, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in out[r].items() if k not in ("most_negative", "most_positive")}, flush=True)
    result = {"regions": out, "overall": overall({r: out[r]["verdict"] for r in REGIONS}), "target": TARGET, "alongside": {}}
    side = result["alongside"]
    for name, kw in (("errors_200_or_less", {}), ("window_200", {"width": 200}), ("window_500", {"width": 500}),
                     ("target_12750", {"target": 12750}), ("target_12950", {"target": 12950})):
        side[name] = {}
        for r in REGIONS:
            a, e, s = dates[r]
            if name == "errors_200_or_less":
                keep = e <= 200
                a, e, s = a[keep], e[keep], [x for x, k in zip(s, keep) if k]
            o, _ = analyse(a, e, s, mu, sig, rng, full=False, **kw)
            side[name][r] = {k: o[k] for k in ("dates", "bins", "step_at_target", "z_at_target", "p_at_target", "power_halving", "verdict")}
        print(name, {r: (round(side[name][r]["z_at_target"], 2), side[name][r]["p_at_target"], side[name][r]["verdict"]) for r in REGIONS}, flush=True)
    (Q / "results").mkdir(exist_ok=True)
    json.dump(result, open(Q / "results" / "summary.json", "w"), indent=1)
    with open(Q / "results" / "curves.tsv", "w") as f:
        f.write("region\tcal_bp\tsummed\ttrend\tmade_up_2.5\tmade_up_97.5\n")
        for r in REGIONS:
            c = curves[r]
            for i, t in enumerate(GRID):
                if 10000 <= t <= 16000:
                    f.write(f"{r}\t{t}\t{c['S'][i]:.5f}\t{c['trend'][i]:.5f}\t{c['null_lo'][i]:.5f}\t{c['null_hi'][i]:.5f}\n")
    with open(Q / "results" / "steps.tsv", "w") as f:
        f.write("region\tT\tstep\tz\tmade_up_2.5\tmade_up_97.5\n")
        for r in REGIONS:
            c = curves[r]
            for i, T in enumerate(c["times"]):
                f.write(f"{r}\t{T}\t{c['real'][i]:.5f}\t{c['z'][i]:.4f}\t{c['lo'][i]:.5f}\t{c['hi'][i]:.5f}\n")
    print("OVERALL:", result["overall"])


if __name__ == "__main__":
    main()
