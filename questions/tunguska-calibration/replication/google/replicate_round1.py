"""
Independent replication of the Tunguska Greenland ice-core analysis protocol.

Ambiguities resolved and choices made:
1. Reference window bounds for the 3-year window variant ("wholly within 1800 to 1990"):
   Consistent with the protocol's inclusive year ranges ("1905 to 1912" = 8 years,
   "1907 to 1909" = 3 years), a window of width W starting at y covers calendar years
   y .. y+W-1 and lies wholly within 1800..1990 iff y >= 1800 and y + W - 1 <= 1990,
   with (y - target) % W == 0. For W=2, target=1908 this gives 1800, 1802, ..., 1988
   (95 windows); for W=3, target=1907 this gives 1802, 1805, ..., 1988 (63 windows).
2. Background years for the 3-year window variant:
   15 years before the window (y-15 .. y-1) and 15 years after (y+3 .. y+17), still
   30 background years with at least 20 required to have a value.
3. Completeness rule for the largest-sample variant:
   The yearly completeness requirement (at least one sample with a value and
   2 * with >= all rows in that calendar year) is kept unchanged; only the aggregation
   changes from arithmetic mean to maximum.
4. Non-positive values in standard tables:
   Any empty cell or non-positive/non-finite numeric value is treated as missing for
   that chemical, while the row still counts toward total rows dated in that year.
5. Missing target year in excess (size) calculation:
   Analogous to the window score, if only one of the two target years (1908, 1909)
   has a yearly value for a core, that year is used; if neither has a value (or fewer
   than 20 background years have a value), the core is left out. Per-site excess is
   computed over all test sites with at least one eligible test core (which coincides
   with the sites used whenever background MAD > 0).
6. "Not testable" handling:
   For the main test, minimum sites are nh4=5, no3=4, bc=3, s=4; for "without <site>",
   max(1, min_sites - 1); for "DRI sites only" and "other laboratories only" ("no
   minimum number of sites"), at least 1 site with a score in the target window is
   required so a network mean is defined. Whenever fewer than the required minimum
   sites have a score in the target window, verdict is "not testable" and network is
   null (None).
7. Reported-apart cores:
   A reported-apart core is included for a chemical if it has at least one valid
   positive sample for that chemical anywhere in its standard table. If it has no
   valid window score or excess in 1908, that field is null (None).
8. Sensitivity (power) simulation RNG consumption:
   A single numpy.random.default_rng(100) instance is used across all 12 combinations
   in protocol order: share in (1.0, 0.5), then k in (0.1, 0.25, 0.5, 1.0, 2.0, 4.0),
   400 trials each. Eligible counted windows are sorted by start year and satisfy
   (w + 1 < 1890) or (w > 1925). Each trial draws the window index with rng.integers,
   draws the year offset in {0, 1} with rng.integers(2), and iterates over sites_used
   in alphabetical order: for share == 1.0 every site receives without drawing from
   the RNG; for share == 0.5 each site receives if rng.random() < 0.5.
"""

from collections import defaultdict
import json
import math
from pathlib import Path
import sys

import numpy as np


CHEMICALS = ("nh4", "no3", "bc", "s")
MIN_SITES = {"nh4": 5, "no3": 4, "bc": 3, "s": 4}

TEST_SITE_CORES = {
    "ACT11d": ("act11d",),
    "Humboldt": ("humboldt",),
    "NEEM": ("neem_s1",),
    "NEGIS": ("negis",),
    "NGRIP": ("ngrip1",),
    "Tunu": ("tunu2013", "tunu2022a"),
}
DRI_SITES = ("ACT11d", "Humboldt", "NEEM", "Tunu")
OTHER_SITES = ("NEGIS", "NGRIP")

REPORTED_APART_CORES = (
    "summit2010",
    "summit2023",
    "tunu2022b",
    "tunu_n",
    "ht95",
    "b20",
)

ALL_CORES = (
    "neem_s1",
    "tunu2013",
    "tunu2022a",
    "humboldt",
    "act11d",
    "negis",
    "ngrip1",
    "summit2010",
    "summit2023",
    "tunu2022b",
    "tunu_n",
    "ht95",
    "b20",
)


def r4(value):
    if value is None:
        return None
    rounded = round(float(value), 4)
    return 0.0 if rounded == 0.0 else rounded


def format_rank(obj):
    if obj is None:
        return None
    return {
        "value": r4(obj["value"]),
        "rank": int(obj["rank"]),
        "n": int(obj["n"]),
        "fraction": r4(obj["fraction"]),
    }


def load_standard_table(core_name):
    path = Path("data/standard") / f"{core_name}.tsv"
    total_rows = defaultdict(int)
    samples = {chem: defaultdict(list) for chem in CHEMICALS}
    measures = {chem: False for chem in CHEMICALS}

    with path.open("r", encoding="utf-8") as f:
        header_line = f.readline()
        if not header_line:
            raise ValueError(f"Empty standard table: {path}")
        header = header_line.rstrip("\r\n").split("\t")
        col_idx = {name: i for i, name in enumerate(header)}
        year_idx = col_idx["year"]
        chem_indices = {chem: col_idx[chem] for chem in CHEMICALS}

        for line in f:
            line = line.rstrip("\r\n")
            if not line:
                continue
            parts = line.split("\t")
            yr = math.floor(float(parts[year_idx]))
            total_rows[yr] += 1
            for chem, idx in chem_indices.items():
                if idx < len(parts):
                    cell = parts[idx].strip()
                    if cell:
                        val = float(cell)
                        if math.isfinite(val) and val > 0.0:
                            samples[chem][yr].append(val)
                            measures[chem] = True

    return total_rows, samples, measures


def compute_yearly(total_rows, samples_by_year, agg="mean"):
    yearly = {}
    for yr, vals in samples_by_year.items():
        n_with = len(vals)
        n_all = total_rows[yr]
        if n_with >= 1 and 2 * n_with >= n_all:
            if agg == "mean":
                yearly[yr] = sum(vals) / n_with
            elif agg == "max":
                yearly[yr] = max(vals)
            else:
                raise ValueError(f"Unsupported aggregation: {agg}")
    return yearly


def tiling_windows(target, width, start_min=1800, end_max=1990):
    first = start_min + ((target - start_min) % width)
    return list(range(first, end_max - width + 2, width))


def background_log_stats(yearly, w, width=2):
    bg_vals = [yearly[y] for y in range(w - 15, w) if y in yearly]
    bg_vals.extend(yearly[y] for y in range(w + width, w + width + 15) if y in yearly)
    if len(bg_vals) < 20:
        return None
    bg_logs = np.log(np.array(bg_vals, dtype=np.float64))
    m = float(np.median(bg_logs))
    mad = float(np.median(np.abs(bg_logs - m)))
    s = 1.4826 * mad
    if s == 0.0:
        return None
    return m, s


def core_window_score(yearly, w, width=2):
    win_vals = [yearly[y] for y in range(w, w + width) if y in yearly]
    if not win_vals:
        return None
    stats = background_log_stats(yearly, w, width=width)
    if stats is None:
        return None
    m, s = stats
    win_logs = np.log(np.array(win_vals, dtype=np.float64))
    return float(np.max((win_logs - m) / s))


def core_excess(yearly, target=1908, width=2):
    win_vals = [yearly[y] for y in range(target, target + width) if y in yearly]
    if not win_vals:
        return None
    bg_vals = [yearly[y] for y in range(target - 15, target) if y in yearly]
    bg_vals.extend(
        yearly[y] for y in range(target + width, target + width + 15) if y in yearly
    )
    if len(bg_vals) < 20:
        return None
    bg_med = float(np.median(np.array(bg_vals, dtype=np.float64)))
    if bg_med <= 0.0:
        return None
    return (max(win_vals) / bg_med) - 1.0


def rank_window(scores_by_window, target):
    if target not in scores_by_window:
        return None
    target_val = scores_by_window[target]
    n = len(scores_by_window)
    rank = 1 + sum(1 for v in scores_by_window.values() if v > target_val)
    return {
        "value": target_val,
        "rank": rank,
        "n": n,
        "fraction": rank / n,
    }


def verdict_from_fraction(fraction):
    if fraction <= 0.04:
        return "exceptional"
    if fraction <= 0.10:
        return "elevated"
    return "ordinary"


def evaluate_network(candidate_sites, yearly_by_core, target, width, min_sites):
    windows = tiling_windows(target, width)
    site_scores = {}
    core_scores = {}

    for site in sorted(candidate_sites):
        cores = TEST_SITE_CORES[site]
        for core in cores:
            c_scores = {}
            yearly = yearly_by_core[core]
            for w in windows:
                sc = core_window_score(yearly, w, width=width)
                if sc is not None:
                    c_scores[w] = sc
            core_scores[core] = c_scores

        s_scores = {}
        for w in windows:
            vals = [core_scores[c][w] for c in cores if w in core_scores[c]]
            if vals:
                s_scores[w] = sum(vals) / len(vals)
        site_scores[site] = s_scores

    sites_used = sorted(s for s in candidate_sites if target in site_scores[s])
    required = max(1, min_sites)

    counted_scores = {}
    if sites_used:
        for w in windows:
            if all(w in site_scores[s] for s in sites_used):
                counted_scores[w] = sum(site_scores[s][w] for s in sites_used) / len(
                    sites_used
                )

    if len(sites_used) < required or target not in counted_scores:
        network = None
        verdict = "not testable"
    else:
        network = rank_window(counted_scores, target)
        verdict = verdict_from_fraction(network["fraction"])

    return {
        "sites_used": sites_used,
        "site_scores": site_scores,
        "core_scores": core_scores,
        "counted_scores": counted_scores,
        "network": network,
        "verdict": verdict,
    }


def run_power(sites_used, yearly_by_core, site_scores, core_scores, counted_scores):
    eligible = [w for w in sorted(counted_scores) if (w + 1 < 1890) or (w > 1925)]
    if not sites_used or not eligible:
        return {}

    core_typical = {}
    bg_stats = {}
    for site in sites_used:
        for core in TEST_SITE_CORES[site]:
            yearly = yearly_by_core[core]
            vals = [yearly[y] for y in range(1880, 1931) if y in yearly]
            core_typical[core] = (
                float(np.median(np.array(vals, dtype=np.float64))) if vals else None
            )
            bg_stats[core] = {
                w: background_log_stats(yearly, w, width=2) for w in eligible
            }

    rng = np.random.default_rng(100)
    n_total = len(counted_scores)
    all_counted = list(counted_scores.items())
    n_eligible = len(eligible)
    n_sites = len(sites_used)

    power = {}
    for share in (1.0, 0.5):
        for k in (0.1, 0.25, 0.5, 1.0, 2.0, 4.0):
            elevated_count = 0
            exceptional_count = 0
            for _ in range(400):
                w = eligible[int(rng.integers(n_eligible))]
                yr = w + int(rng.integers(2))
                other_yr = w + 1 if yr == w else w

                net_sum = 0.0
                for site in sites_used:
                    receives = True if share == 1.0 else (rng.random() < share)
                    if not receives:
                        net_sum += site_scores[site][w]
                    else:
                        c_vals = []
                        for core in TEST_SITE_CORES[site]:
                            stats = bg_stats[core][w]
                            if stats is None:
                                continue
                            yearly = yearly_by_core[core]
                            if yr in yearly and core_typical[core] is not None:
                                m, s = stats
                                win_vals = [yearly[yr] + k * core_typical[core]]
                                if other_yr in yearly:
                                    win_vals.append(yearly[other_yr])
                                sc = float(
                                    np.max(
                                        (np.log(np.array(win_vals, dtype=np.float64)) - m)
                                        / s
                                    )
                                )
                                c_vals.append(sc)
                            elif w in core_scores[core]:
                                c_vals.append(core_scores[core][w])
                        net_sum += sum(c_vals) / len(c_vals)

                new_net = net_sum / n_sites
                rank = 1 + sum(1 for ow, sc in all_counted if ow != w and sc > new_net)
                frac = rank / n_total
                if frac <= 0.10:
                    elevated_count += 1
                if frac <= 0.04:
                    exceptional_count += 1

            power[f"share {share}, pulse {k}"] = {
                "elevated": r4(elevated_count / 400),
                "exceptional": r4(exceptional_count / 400),
            }

    return power


def main():
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: python replicate.py OUTDIR\n")
        sys.exit(1)

    outdir = Path(sys.argv[1])
    outdir.mkdir(parents=True, exist_ok=True)

    raw_data = {}
    for core in ALL_CORES:
        raw_data[core] = load_standard_table(core)

    yearly_mean = {chem: {} for chem in CHEMICALS}
    yearly_max = {chem: {} for chem in CHEMICALS}
    measures = {chem: {} for chem in CHEMICALS}
    for core in ALL_CORES:
        total_rows, samples, core_measures = raw_data[core]
        for chem in CHEMICALS:
            measures[chem][core] = core_measures[chem]
            yearly_mean[chem][core] = compute_yearly(
                total_rows, samples[chem], agg="mean"
            )
            yearly_max[chem][core] = compute_yearly(
                total_rows, samples[chem], agg="max"
            )

    all_test_sites = sorted(TEST_SITE_CORES.keys())
    summary = {}

    for chem in CHEMICALS:
        min_sites = MIN_SITES[chem]
        main_res = evaluate_network(
            all_test_sites, yearly_mean[chem], target=1908, width=2, min_sites=min_sites
        )
        sites_used = main_res["sites_used"]
        site_scores = main_res["site_scores"]
        counted_scores = main_res["counted_scores"]

        by_site = {
            site: format_rank(rank_window(site_scores[site], 1908))
            for site in sites_used
        }

        excess_by_site_raw = {}
        for site in all_test_sites:
            core_ex = []
            for core in TEST_SITE_CORES[site]:
                ex = core_excess(yearly_mean[chem][core], target=1908, width=2)
                if ex is not None:
                    core_ex.append(ex)
            if core_ex:
                excess_by_site_raw[site] = sum(core_ex) / len(core_ex)

        excess_over_typical_year = {
            site: r4(val) for site, val in sorted(excess_by_site_raw.items())
        }
        excess_median = (
            r4(float(np.median(np.array(list(excess_by_site_raw.values()), dtype=np.float64))))
            if excess_by_site_raw
            else None
        )

        top_windows = [
            [r4(score), int(w)]
            for w, score in sorted(
                counted_scores.items(), key=lambda kv: (-kv[1], kv[0])
            )[:10]
        ]

        variants = {}

        res_3yr = evaluate_network(
            all_test_sites, yearly_mean[chem], target=1907, width=3, min_sites=min_sites
        )
        variants["three-year window, 1907 to 1909"] = {
            "network": format_rank(res_3yr["network"]),
            "verdict": res_3yr["verdict"],
        }

        res_max = evaluate_network(
            all_test_sites, yearly_max[chem], target=1908, width=2, min_sites=min_sites
        )
        variants["largest sample of each year in place of its mean"] = {
            "network": format_rank(res_max["network"]),
            "verdict": res_max["verdict"],
        }

        for leave_out in sites_used:
            rem_sites = [s for s in all_test_sites if s != leave_out]
            res_loo = evaluate_network(
                rem_sites,
                yearly_mean[chem],
                target=1908,
                width=2,
                min_sites=max(1, min_sites - 1),
            )
            variants[f"without {leave_out}"] = {
                "network": format_rank(res_loo["network"]),
                "verdict": res_loo["verdict"],
            }

        res_dri = evaluate_network(
            DRI_SITES, yearly_mean[chem], target=1908, width=2, min_sites=1
        )
        variants["DRI sites only"] = {
            "network": format_rank(res_dri["network"]),
            "verdict": res_dri["verdict"],
        }

        res_other = evaluate_network(
            OTHER_SITES, yearly_mean[chem], target=1908, width=2, min_sites=1
        )
        variants["other laboratories only"] = {
            "network": format_rank(res_other["network"]),
            "verdict": res_other["verdict"],
        }

        tiling_2yr = tiling_windows(1908, 2)
        reported_apart = {}
        for core in REPORTED_APART_CORES:
            if not measures[chem][core]:
                continue
            yearly = yearly_mean[chem][core]
            c_scores = {}
            for w in tiling_2yr:
                sc = core_window_score(yearly, w, width=2)
                if sc is not None:
                    c_scores[w] = sc
            reported_apart[core] = {
                "rank": format_rank(rank_window(c_scores, 1908)),
                "excess": r4(core_excess(yearly, target=1908, width=2)),
            }

        chem_out = {
            "sites": sites_used,
            "windows": len(counted_scores),
            "network": format_rank(main_res["network"]),
            "verdict": main_res["verdict"],
            "by_site": by_site,
            "excess_over_typical_year": excess_over_typical_year,
            "excess_median_of_sites": excess_median,
            "top_windows": top_windows,
            "variants": variants,
            "reported_apart": reported_apart,
        }

        if chem == "s":
            katmai = (
                format_rank(rank_window(counted_scores, 1912))
                if main_res["verdict"] != "not testable" and 1912 in counted_scores
                else None
            )
            chem_out["katmai_window_1912"] = katmai

        if chem == "nh4":
            chem_out["power"] = run_power(
                sites_used,
                yearly_mean["nh4"],
                site_scores,
                main_res["core_scores"],
                counted_scores,
            )

        summary[chem] = chem_out

        net = chem_out["network"]
        if net is None:
            print(f"{chem}: {chem_out['verdict']}")
        else:
            print(
                f"{chem}: {chem_out['verdict']} "
                f"(rank {net['rank']}/{net['n']}, fraction {net['fraction']:.4f}, "
                f"score {net['value']:.4f}, E {excess_median:.4f})"
            )

    with (outdir / "summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
        f.write("\n")


if __name__ == "__main__":
    main()
