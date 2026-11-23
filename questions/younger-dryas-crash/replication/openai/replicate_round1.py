#!/usr/bin/env python3
# Usage: python replicate.py OUTDIR
#
# Implementation choices:
# - Strip whitespace from Continent. A whitespace-only site field is blank;
#   otherwise SiteID is verbatim and SiteName is stripped and lowercased.
#   No nonblank string is interpreted as a missing-value code.
# - The aquatic regexes match substrings, without word boundaries; optional
#   spaces include whitespace. Missing material/taxon text contributes "".
# - Preserve first-occurrence order of bins and input order within each bin.
#   Use one RNG stream: null then halving for each successive region. Draw
#   calendar ages, shared curve errors, then lab errors in vector batches;
#   on retry redraw only empty bins. Use nearest-even rounding. Count the
#   initial attempt among the 50; fail rather than silently lose a bin.
# - Fit the quadratic in centered, rescaled years (same polynomial space).
#   Compute all null step statistics but write only the specified outputs.
# - For speed, commute the linear sums: for common errors, cache the masses
#   of normalized date curves in 50-year blocks by integer simulated age.
#   Weight each survivor by 1/(survivors in its bin). This gives the same
#   window sums as first constructing the entire simulated summed curve.

import csv
import json
import re
import sys
from pathlib import Path

import numpy as np


REGIONS = ("North America", "Europe", "Asia")
GRID = np.arange(9000, 17001, 5)
FIT = (GRID >= 10500) & (GRID <= 15500)
SUP = np.flatnonzero((GRID >= 9500) & (GRID <= 16500))
TIMES = np.arange(10800, 15201, 50)
STAR = int(np.flatnonzero(TIMES == 12850)[0])
LOW, HIGH = 9000, 13800
B, H = 2000, 500
CHUNK = 192
EXEMPT = re.compile(r"(?:nut|egg)\s*shell", re.I)
AQUATIC = re.compile(r"shell|marine|fish(?!er)|mollus|whale|seal|otolith|coral", re.I)


def read_bins():
    regions = {r: {} for r in REGIONS}
    with open("data/p3k14c_scrubbed_fuzzed.csv", encoding="utf-8-sig", newline="") as f:
        for i, row in enumerate(csv.DictReader(f)):
            r = row["Continent"].strip()
            if r not in regions:
                continue
            a, e = float(row["Age"]), float(row["Error"])
            if not (LOW <= a <= HIGH and e > 0):
                continue
            text = (row["Material"] or "") + " " + (row["Taxa"] or "")
            if AQUATIC.search(EXEMPT.sub("", text)):
                continue
            sid, name = row["SiteID"], row["SiteName"].strip().lower()
            if sid.strip():
                site = ("id", sid)
            elif name:
                site = ("name", name)
            else:
                site = ("row", i)
            regions[r].setdefault((site, int(a // 200)), []).append((a, e))
    return regions


def read_curve():
    t, m, s = np.loadtxt("data/intcal20.14c", delimiter=",", comments="#",
                         usecols=(0, 1, 2), unpack=True)
    order = np.argsort(t)
    return tuple(np.interp(GRID, t[order], x[order]) for x in (m, s))


def blocks(s):
    # 100 blocks [10500,10550), ..., [15450,15500); 10 grid points each.
    return s[..., 300:1300].reshape(s.shape[:-1] + (100, 10)).sum(axis=-1)


def steps(mass):
    windows = np.convolve(mass, np.ones(6), mode="valid")
    return np.log(windows[:-6] / windows[6:])


def trend(s):
    x = (GRID - 13000) / 1000.0
    if not np.all(s[FIT] > 0):
        raise ValueError("Undefined log summed curve in fit interval")
    coef = np.polyfit(x[FIT], np.log(s[FIT]), 2)
    logp = np.polyval(coef, x[SUP])
    p = np.exp(logp - logp.max())
    return p / p.sum()


class Calibration:
    def __init__(self, mu, sigma, errors):
        self.mu = mu
        e, self.codes, self.freq = np.unique(errors, return_inverse=True,
                                              return_counts=True)
        self.codes = self.codes.ravel()
        var = e[:, None] ** 2 + sigma ** 2
        self.quad = -0.5 / var
        self.const = -0.5 * np.log(var)

    def profiles(self, ages, codes):
        x = ages[:, None] - self.mu
        np.square(x, out=x)
        x *= self.quad[codes]
        x += self.const[codes]
        x -= x.max(axis=1, keepdims=True)
        np.exp(x, out=x)
        x /= x.sum(axis=1, keepdims=True)
        return x

    def summed(self, ages, codes, weights):
        s = np.zeros(len(GRID))
        for i in range(0, len(ages), CHUNK):
            j = slice(i, i + CHUNK)
            p = self.profiles(ages[j], codes[j])
            s += np.einsum("i,ij->j", weights[j], p)
        return s

    def build_cache(self):
        hot = np.argsort(-self.freq)[:48]
        hot = hot[self.freq[hot] >= 2]
        self.slot = np.full(len(self.freq), -1)
        self.slot[hot] = np.arange(len(hot))
        ages = np.arange(LOW, HIGH + 1)
        self.table = np.empty((len(hot), len(ages), 100))
        for h, c in enumerate(hot):
            for i in range(0, len(ages), CHUNK):
                j = slice(i, i + CHUNK)
                self.table[h, j] = blocks(self.profiles(ages[j], c))

    def simulated_mass(self, ages, codes, weights):
        slots = self.slot[codes]
        hot = slots >= 0
        rows = self.table[slots[hot], ages[hot].astype(np.intp) - LOW]
        mass = np.einsum("i,ij->j", weights[hot], rows)
        cold = ~hot
        if cold.any():
            mass += blocks(self.summed(ages[cold], codes[cold], weights[cold]))
        return mass


def analyze(groups, mu, sigma, rng):
    sizes = np.array([len(g) for g in groups.values()], dtype=np.intp)
    nb = len(sizes)
    bin_id = np.repeat(np.arange(nb), sizes)
    age, err = np.array([d for g in groups.values() for d in g]).T
    cal = Calibration(mu, sigma, err)
    s = cal.summed(age, cal.codes, 1.0 / sizes[bin_id])
    if not np.isclose(s.sum(), nb):
        raise ArithmeticError("Bin normalization failed")
    real = steps(blocks(s))
    density = trend(s)
    half = density.copy()
    half[(GRID[SUP] >= 12550) & (GRID[SUP] < 12850)] *= 0.5
    half /= half.sum()
    cal.build_cache()

    def record(p):
        need = np.ones(nb, dtype=bool)
        center = np.empty(nb)
        a = np.empty_like(err)
        for _ in range(50):
            t = rng.choice(SUP, size=np.count_nonzero(need), p=p)
            center[need] = mu[t] + rng.normal(0.0, sigma[t])
            active = need[bin_id]
            a[active] = np.rint(center[bin_id[active]] + rng.normal(0.0, err[active]))
            keep = (a >= LOW) & (a <= HIGH)
            surviving_bins = bin_id[keep]
            counts = np.bincount(surviving_bins, minlength=nb)
            need = counts == 0
            if not need.any():
                mass = cal.simulated_mass(a[keep], cal.codes[keep],
                                          1.0 / counts[surviving_bins])
                return steps(mass)
        raise RuntimeError("Simulated bin empty after 50 attempts")

    null = np.stack([record(density) for _ in range(B)])
    mean, sd = null.mean(axis=0), null.std(axis=0, ddof=1)
    z = np.divide(real - mean, sd, out=np.full_like(real, np.nan), where=sd > 0)
    ordered = np.sort(null[:, STAR])

    def lower_p(x):
        return (1 + np.searchsorted(ordered, x, side="right")) / (B + 1)

    d = float(real[STAR])
    p = float(lower_p(d))
    planted = np.array([record(half)[STAR] for _ in range(H)])
    power = float(np.mean((planted < 0) & (lower_p(planted) <= 0.01)))
    share = float(np.mean(planted >= d))
    verdict = ("drop detected" if d < 0 and p <= 0.01 else
               "a halving is excluded" if share <= 0.01 else "cannot tell")
    return s, dict(dates=len(age), bins=nb, step_at_target=d, p_at_target=p,
                   power_halving=power, share_of_halvings_with_step_at_or_above_real=share,
                   verdict=verdict)


def main(out):
    regions = read_bins()
    mu, sigma = read_curve()
    rng = np.random.default_rng(40)
    out.mkdir(parents=True, exist_ok=True)
    results = {}
    with (out / "curves.tsv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n")
        writer.writerow(("region", "cal_bp", "summed"))
        for r in REGIONS:
            s, results[r] = analyze(regions[r], mu, sigma, rng)
            writer.writerows((r, t, format(v, ".17g")) for t, v in zip(GRID, s)
                             if 10000 <= t <= 16000)
    na, eu, asia = (results[r]["verdict"] for r in REGIONS)
    if na == "drop detected":
        overall = "supported as widespread" if na in (eu, asia) else "supported"
    else:
        overall = "not supported" if na == "a halving is excluded" else "undetermined"
    with (out / "summary.json").open("w", encoding="utf-8") as f:
        json.dump(dict(overall=overall, regions=results), f, indent=2, allow_nan=False)
        f.write("\n")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python replicate.py OUTDIR")
    main(Path(sys.argv[1]))
