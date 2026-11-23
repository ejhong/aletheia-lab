"""Independent replication of the Younger Dryas population crash analysis.

Ambiguities in protocol.md and choices made:
1. Blank SiteID/SiteName: treated as empty after stripping whitespace; literal
   "NA" is not treated as blank because no missing-value sentinel is specified.
   SiteID is stripped of surrounding spaces (preserving case); Continent is also
   stripped when matching region names.
2. Aquatic material screen: "optional spaces" before "shell" is matched with
   `\\s*` and removed by replacing with ""; aquatic keywords are matched as
   case-insensitive substrings (`fish(?!er)` uses a negative lookahead).
3. Empty-bin redraws: "up to 50 tries" is implemented as 50 total attempts per
   bin (1 initial draw plus up to 49 redraws). Any bin still empty after 50
   attempts would contribute zero weight (negligible probability).
4. Rounding simulated radiocarbon ages: uses numpy.rint (round half to even;
   exact .5 has zero probability for continuous normal draws).
5. RNG order: a single numpy.random.default_rng(40) is used across regions in
   the order North America, Europe, Asia; within each region, the 2,000
   crash-free records are drawn first, followed by the 500 halving records.
6. Halving-exclusion share: computed literally as count / 500 (no +1 continuity
   correction), matching "the share of the 500" and "at most 1% of halving
   records", while p_at_target and power_halving use (k + 1) / (2000 + 1).
7. curves.tsv formatting: regions in protocol order, integer cal_bp from 10000
   to 16000 in steps of 5, summed formatted with `:.12g`.
"""

import csv
import json
import math
import re
import sys
from pathlib import Path

import numpy as np

REGIONS = ("North America", "Europe", "Asia")
GRID_START, GRID_END, GRID_STEP = 9000, 17000, 5
AGE_MIN, AGE_MAX = 9000, 13800
TARGET_T = 12850
WINDOW = 300
N_NULL = 2000
N_HALVING = 500
MAX_TRIES = 50
RNG_SEED = 40

AQUATIC_REMOVE_RE = re.compile(r"(?:nut|egg)\s*shell", re.IGNORECASE)
AQUATIC_FAIL_RE = re.compile(
    r"shell|marine|fish(?!er)|mollus|whale|seal|otolith|coral",
    re.IGNORECASE,
)


def load_intcal20(path: Path, grid: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    cal, c14, err = [], [], []
    with path.open("r", encoding="utf-8-sig") as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            parts = s.split(",")
            cal.append(float(parts[0]))
            c14.append(float(parts[1]))
            err.append(float(parts[2]))
    cal_a = np.asarray(cal, dtype=np.float64)
    c14_a = np.asarray(c14, dtype=np.float64)
    err_a = np.asarray(err, dtype=np.float64)
    order = np.argsort(cal_a)
    return np.interp(grid, cal_a[order], c14_a[order]), np.interp(
        grid, cal_a[order], err_a[order]
    )


def load_region_bins(path: Path) -> dict[str, list[list[tuple[float, float]]]]:
    bins_by_region: dict[str, dict[object, list[tuple[float, float]]]] = {
        r: {} for r in REGIONS
    }
    solo_id = 0
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            region = (row["Continent"] or "").strip()
            if region not in bins_by_region:
                continue
            age = float(row["Age"])
            err = float(row["Error"])
            if not (AGE_MIN <= age <= AGE_MAX and err > 0.0):
                continue
            text = f"{row['Material'] or ''} {row['Taxa'] or ''}"
            if AQUATIC_FAIL_RE.search(AQUATIC_REMOVE_RE.sub("", text)):
                continue
            sid = (row["SiteID"] or "").strip()
            sname = (row["SiteName"] or "").strip().lower()
            if sid:
                site_key: object = ("id", sid)
            elif sname:
                site_key = ("name", sname)
            else:
                site_key = ("solo", solo_id)
                solo_id += 1
            bin_key = (site_key, math.floor(age / 200.0))
            bins_by_region[region].setdefault(bin_key, []).append((age, err))
    return {r: list(d.values()) for r, d in bins_by_region.items()}


def pack_region(
    bins: list[list[tuple[float, float]]],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    ages, errs, bin_of_date, bin_starts, bin_ends = [], [], [], [], []
    pos = 0
    for b_idx, dates in enumerate(bins):
        bin_starts.append(pos)
        for a, e in dates:
            ages.append(a)
            errs.append(e)
            bin_of_date.append(b_idx)
            pos += 1
        bin_ends.append(pos)
    return (
        np.asarray(ages, dtype=np.float64),
        np.asarray(errs, dtype=np.float64),
        np.asarray(bin_of_date, dtype=np.int32),
        np.asarray(bin_starts, dtype=np.int32),
        np.asarray(bin_ends, dtype=np.int32),
    )


def calibrate_summed_curve(
    ages: np.ndarray,
    errors: np.ndarray,
    bin_of_date: np.ndarray,
    bin_counts: np.ndarray,
    mu: np.ndarray,
    sigma2: np.ndarray,
) -> np.ndarray:
    summed = np.zeros(mu.size, dtype=np.float64)
    chunk = 256
    for s in range(0, ages.size, chunk):
        e = min(s + chunk, ages.size)
        v = errors[s:e, None] ** 2 + sigma2[None, :]
        diff = ages[s:e, None] - mu[None, :]
        u = np.exp(-0.5 * (diff * diff) / v) / np.sqrt(v)
        w = 1.0 / (bin_counts[bin_of_date[s:e]] * u.sum(axis=1))
        summed += w @ u
    return summed


def build_window_tables(
    unique_errors: np.ndarray,
    mu: np.ndarray,
    sigma2: np.ndarray,
    after_sl: slice,
    before_sl: slice,
) -> tuple[np.ndarray, np.ndarray]:
    # Exact lookup of normalized window sums for every (unique Error, integer Age).
    u_count = unique_errors.size
    n_ages = AGE_MAX - AGE_MIN + 1
    ages_int = np.arange(AGE_MIN, AGE_MAX + 1, dtype=np.float64)
    v_u = unique_errors[:, None] ** 2 + sigma2[None, :]
    inv_2v_u = -0.5 / v_u
    inv_sqrt_v_u = 1.0 / np.sqrt(v_u)
    after_tbl = np.empty((u_count, n_ages), dtype=np.float64)
    before_tbl = np.empty((u_count, n_ages), dtype=np.float64)
    chunk = 256
    buf = np.empty((chunk, mu.size), dtype=np.float64)
    for s in range(0, n_ages, chunk):
        e = min(s + chunk, n_ages)
        b = buf[: e - s]
        diff = ages_int[s:e, None] - mu[None, :]
        diff2 = diff * diff
        for u_i in range(u_count):
            np.multiply(diff2, inv_2v_u[u_i], out=b)
            np.exp(b, out=b)
            np.multiply(b, inv_sqrt_v_u[u_i], out=b)
            denom = b.sum(axis=1)
            after_tbl[u_i, s:e] = b[:, after_sl].sum(axis=1) / denom
            before_tbl[u_i, s:e] = b[:, before_sl].sum(axis=1) / denom
    return after_tbl, before_tbl


def direct_window_sums(
    ages: np.ndarray,
    errors: np.ndarray,
    inv_cnt: np.ndarray,
    mu: np.ndarray,
    sigma2: np.ndarray,
    after_sl: slice,
    before_sl: slice,
) -> tuple[float, float]:
    total_after = 0.0
    total_before = 0.0
    chunk = 256
    for s in range(0, ages.size, chunk):
        e = min(s + chunk, ages.size)
        v = errors[s:e, None] ** 2 + sigma2[None, :]
        diff = ages[s:e, None] - mu[None, :]
        u = np.exp(-0.5 * (diff * diff) / v) / np.sqrt(v)
        w = inv_cnt[s:e] / u.sum(axis=1)
        total_after += float(np.dot(w, u[:, after_sl].sum(axis=1)))
        total_before += float(np.dot(w, u[:, before_sl].sum(axis=1)))
    return total_after, total_before


def fit_reference_density(
    grid: np.ndarray, summed: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    fit_mask = (grid >= 10500) & (grid <= 15500)
    ref_mask = (grid >= 9500) & (grid <= 16500)
    u_fit = (grid[fit_mask] - 13000.0) / 2500.0
    coeffs = np.polyfit(u_fit, np.log(summed[fit_mask]), 2)
    u_ref = (grid[ref_mask] - 13000.0) / 2500.0
    log_ref = np.polyval(coeffs, u_ref)
    ref_density = np.exp(log_ref - np.max(log_ref))
    ref_density /= ref_density.sum()
    return ref_mask, grid[ref_mask], ref_density


def simulate_steps(
    n_records: int,
    density: np.ndarray,
    ref_mu: np.ndarray,
    ref_sigma: np.ndarray,
    date_errors: np.ndarray,
    e_idx: np.ndarray,
    bin_of_date: np.ndarray,
    bin_starts: np.ndarray,
    bin_ends: np.ndarray,
    rng: np.random.Generator,
    after_tbl: np.ndarray | None,
    before_tbl: np.ndarray | None,
    mu: np.ndarray,
    sigma2: np.ndarray,
    after_sl: slice,
    before_sl: slice,
) -> np.ndarray:
    n_bins = bin_starts.size
    cdf = np.cumsum(density)
    cdf[-1] = 1.0
    steps = np.empty(n_records, dtype=np.float64)
    for r in range(n_records):
        j = np.searchsorted(cdf, rng.random(n_bins))
        bases = ref_mu[j] + rng.normal(0.0, ref_sigma[j])
        sim_ages = np.rint(bases[bin_of_date] + rng.normal(0.0, date_errors))
        surv = (sim_ages >= AGE_MIN) & (sim_ages <= AGE_MAX)
        bin_counts = np.bincount(bin_of_date[surv], minlength=n_bins)
        for _ in range(MAX_TRIES - 1):
            empty = np.flatnonzero(bin_counts == 0)
            if empty.size == 0:
                break
            j_e = np.searchsorted(cdf, rng.random(empty.size))
            bases_e = ref_mu[j_e] + rng.normal(0.0, ref_sigma[j_e])
            for b, base in zip(empty, bases_e):
                s, e = int(bin_starts[b]), int(bin_ends[b])
                ages_b = np.rint(base + rng.normal(0.0, date_errors[s:e]))
                ok = (ages_b >= AGE_MIN) & (ages_b <= AGE_MAX)
                if ok.any():
                    sim_ages[s:e] = ages_b
                    surv[s:e] = ok
                    bin_counts[b] = int(ok.sum())
        surv_idx = np.flatnonzero(surv)
        inv_cnt = 1.0 / bin_counts[bin_of_date[surv_idx]]
        if after_tbl is not None and before_tbl is not None:
            a_i = sim_ages[surv_idx].astype(np.int32) - AGE_MIN
            e_i = e_idx[surv_idx]
            total_after = float(np.dot(inv_cnt, after_tbl[e_i, a_i]))
            total_before = float(np.dot(inv_cnt, before_tbl[e_i, a_i]))
        else:
            total_after, total_before = direct_window_sums(
                sim_ages[surv_idx], date_errors[surv_idx], inv_cnt,
                mu, sigma2, after_sl, before_sl,
            )
        steps[r] = math.log(total_after / total_before)
    return steps


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("Usage: python replicate.py OUTDIR")
    outdir = Path(sys.argv[1])
    outdir.mkdir(parents=True, exist_ok=True)

    grid = np.arange(GRID_START, GRID_END + 1, GRID_STEP, dtype=np.float64)
    mu, sigma = load_intcal20(Path("data/intcal20.14c"), grid)
    sigma2 = sigma * sigma

    after_idx = np.flatnonzero((grid >= TARGET_T - WINDOW) & (grid < TARGET_T))
    before_idx = np.flatnonzero((grid >= TARGET_T) & (grid < TARGET_T + WINDOW))
    after_sl = slice(int(after_idx[0]), int(after_idx[-1]) + 1)
    before_sl = slice(int(before_idx[0]), int(before_idx[-1]) + 1)

    raw_bins = load_region_bins(Path("data/p3k14c_scrubbed_fuzzed.csv"))
    packed = {r: pack_region(raw_bins[r]) for r in REGIONS}

    unique_errors = np.unique(np.concatenate([packed[r][1] for r in REGIONS]))
    if unique_errors.size <= 2500:
        after_tbl, before_tbl = build_window_tables(
            unique_errors, mu, sigma2, after_sl, before_sl
        )
    else:
        after_tbl = before_tbl = None

    rng = np.random.default_rng(RNG_SEED)
    curves: dict[str, np.ndarray] = {}
    region_summaries: dict[str, dict[str, object]] = {}
    verdicts: dict[str, str] = {}

    for region in REGIONS:
        ages, errors, bin_of_date, bin_starts, bin_ends = packed[region]
        bin_counts = bin_ends - bin_starts
        e_idx = np.searchsorted(unique_errors, errors).astype(np.int32)

        curve = calibrate_summed_curve(ages, errors, bin_of_date, bin_counts, mu, sigma2)
        curves[region] = curve
        real_step = float(np.log(curve[after_sl].mean() / curve[before_sl].mean()))

        ref_mask, ref_grid, ref_density = fit_reference_density(grid, curve)
        ref_mu, ref_sigma = mu[ref_mask], sigma[ref_mask]

        halving_density = ref_density.copy()
        crash_mask = (ref_grid >= TARGET_T - WINDOW) & (ref_grid < TARGET_T)
        halving_density[crash_mask] *= 0.5
        halving_density /= halving_density.sum()

        null_steps = simulate_steps(
            N_NULL, ref_density, ref_mu, ref_sigma, errors, e_idx,
            bin_of_date, bin_starts, bin_ends, rng, after_tbl, before_tbl,
            mu, sigma2, after_sl, before_sl,
        )
        halving_steps = simulate_steps(
            N_HALVING, halving_density, ref_mu, ref_sigma, errors, e_idx,
            bin_of_date, bin_starts, bin_ends, rng, after_tbl, before_tbl,
            mu, sigma2, after_sl, before_sl,
        )

        p_val = (int(np.sum(null_steps <= real_step)) + 1) / (N_NULL + 1)
        detected = (real_step < 0.0) and (p_val <= 0.01)
        null_sorted = np.sort(null_steps)
        p_halv = (np.searchsorted(null_sorted, halving_steps, side="right") + 1) / (N_NULL + 1)
        power = float(np.mean((halving_steps < 0.0) & (p_halv <= 0.01)))
        share_ge = float(np.mean(halving_steps >= real_step))

        if detected:
            verdict = "drop detected"
        elif share_ge <= 0.01:
            verdict = "a halving is excluded"
        else:
            verdict = "cannot tell"

        verdicts[region] = verdict
        region_summaries[region] = {
            "dates": int(ages.size),
            "bins": int(bin_starts.size),
            "step_at_target": real_step,
            "p_at_target": float(p_val),
            "power_halving": power,
            "share_of_halvings_with_step_at_or_above_real": share_ge,
            "verdict": verdict,
        }

    na = verdicts["North America"]
    if na == "drop detected":
        overall = (
            "supported as widespread"
            if (verdicts["Europe"] == "drop detected" or verdicts["Asia"] == "drop detected")
            else "supported"
        )
    elif na == "a halving is excluded":
        overall = "not supported"
    else:
        overall = "undetermined"

    out_mask = (grid >= 10000) & (grid <= 16000)
    out_cal = grid[out_mask].astype(int)
    with (outdir / "curves.tsv").open("w", encoding="utf-8", newline="") as f:
        f.write("region\tcal_bp\tsummed\n")
        for region in REGIONS:
            for cal_bp, val in zip(out_cal, curves[region][out_mask]):
                f.write(f"{region}\t{cal_bp}\t{val:.12g}\n")

    with (outdir / "summary.json").open("w", encoding="utf-8") as f:
        json.dump({"overall": overall, "regions": region_summaries}, f, indent=2)
        f.write("\n")


if __name__ == "__main__":
    main()
