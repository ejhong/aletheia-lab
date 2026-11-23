"""Independent replication of the Göbekli Tepe star map judging analysis.

Usage (run from questions/gobekli-star-map/):
    python replicate.py OUTDIR

Choices made where the protocol / format notes leave minor details open:
1. `judges_excluded` wording: reasons are formatted concisely to report any
   Task A figures with fewer than 3 valid rankings and/or failure of the
   competence check (mean rank of S01 for A01 > 2.0). If A01 has 0 valid
   rankings, only the coverage failure is reported (competence mean is
   undefined); if A01 has 1-2 valid rankings, both checks are reported if
   both fail.
2. Trial validation: although `results/rankings.tsv` omits invalid trials,
   each `(vendor, trial_id)` group is verified to have a single `(task,
   target_id)` and an exact permutation of expected options at positions
   1..N; any malformed group is ignored while its vendor is still tracked.
3. Deterministic key order: vendor keys in `judges_excluded` and
   `without_scorpion.per_judge` are sorted alphabetically (as required for
   `judges_included`).
4. Exact threshold comparisons: the `pairing` label checks exact rational
   inequalities (`p <= 1/100`, `p <= 5/100`, `p > 5/100`) so boundary
   values (e.g. 252/5040 = 0.05) are classified without float rounding.
5. Output schema: `summary.json` contains only the keys defined in
   `replication/FORMAT.md` (omitting narrative extras from `protocol.md`
   such as inter-judge correlations and per-figure best-symbol lists).
"""

from __future__ import annotations

import bisect
from collections import defaultdict
import csv
from fractions import Fraction
import itertools
import json
import math
from pathlib import Path
import sys

import numpy as np

FIGURES = [f"A{i:02d}" for i in range(1, 9)]
SYMBOLS = [f"S{i:02d}" for i in range(1, 13)]
PILLAR = SYMBOLS[:8]

FIGURE_SET = set(FIGURES)
SYMBOL_SET = set(SYMBOLS)
PILLAR_SET = set(PILLAR)


def load_rankings(
    path: Path,
) -> tuple[set[str], dict[str, dict[str, dict[str, list[dict[str, int]]]]]]:
    all_vendors: set[str] = set()
    grouped: dict[tuple[str, str], list[tuple[str, str, int, str]]] = defaultdict(list)

    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            vendor = row["vendor"]
            all_vendors.add(vendor)
            grouped[(vendor, row["trial_id"])].append(
                (row["task"], row["target_id"], int(row["position"]), row["option_id"])
            )

    trials: dict[str, dict[str, dict[str, list[dict[str, int]]]]] = {
        v: {"A": {f: [] for f in FIGURES}, "B": {s: [] for s in PILLAR}}
        for v in all_vendors
    }

    for (vendor, _trial_id), rows in grouped.items():
        tasks = {r[0] for r in rows}
        targets = {r[1] for r in rows}
        if len(tasks) != 1 or len(targets) != 1:
            continue
        task = next(iter(tasks))
        target = next(iter(targets))

        if task == "A":
            valid_targets, expected_opts, n_opts = FIGURE_SET, SYMBOL_SET, 12
        elif task == "B":
            valid_targets, expected_opts, n_opts = PILLAR_SET, FIGURE_SET, 8
        else:
            continue

        if target not in valid_targets or len(rows) != n_opts:
            continue
        positions = {r[2] for r in rows}
        options = {r[3] for r in rows}
        if positions != set(range(1, n_opts + 1)) or options != expected_opts:
            continue

        trials[vendor][task][target].append({opt: pos for _, _, pos, opt in rows})

    return all_vendors, trials


def judge_table(
    target_trials: dict[str, list[dict[str, int]]],
    rows: list[str],
    cols: list[str],
    drop_option: str | None = None,
) -> list[list[Fraction]]:
    table: list[list[Fraction]] = []
    for row_id in rows:
        rankings = target_trials[row_id]
        n = len(rankings)
        sums = {c: 0 for c in cols}
        for r in rankings:
            if drop_option is None:
                for c in cols:
                    sums[c] += r[c]
            else:
                drop_pos = r[drop_option]
                for c in cols:
                    p = r[c]
                    sums[c] += p - 1 if p > drop_pos else p
        table.append([Fraction(sums[c], n) for c in cols])
    return table


def pool_tables(tables: list[list[list[Fraction]]]) -> list[list[Fraction]]:
    k = len(tables)
    nrows = len(tables[0])
    ncols = len(tables[0][0])
    return [
        [sum((t[i][j] for t in tables), Fraction(0)) / k for j in range(ncols)]
        for i in range(nrows)
    ]


def to_int_matrix(table: list[list[Fraction]]) -> list[list[int]]:
    denom = math.lcm(*(cell.denominator for row in table for cell in row))
    return [
        [cell.numerator * (denom // cell.denominator) for cell in row]
        for row in table
    ]


def count_assignments_le(mat: list[list[int]], target: int) -> int:
    """Count injective f: {0..m-1} -> {0..n-1} with sum_i mat[i][f(i)] <= target."""
    m = len(mat)
    n = len(mat[0])
    m1 = m // 2
    m2 = m - m1

    max_val = max(max(row) for row in mat)
    use_numpy = (m * max_val < (1 << 61)) and (abs(target) < (1 << 61))

    right_masks_list: list[int] = []
    right_vals_list: list[list[int]] = []
    for comb in itertools.combinations(range(n), m2):
        mask = 0
        for c in comb:
            mask |= 1 << c
        right_masks_list.append(mask)
        right_vals_list.append(
            [
                sum(mat[m1 + i][p[i]] for i in range(m2))
                for p in itertools.permutations(comb)
            ]
        )

    total = 0
    checked = 0
    if use_numpy:
        right_masks = np.array(right_masks_list, dtype=np.int32)
        right_vals = np.array(right_vals_list, dtype=np.int64)
        target_i64 = np.int64(target)
        for comb in itertools.combinations(range(n), m1):
            mask1 = 0
            for c in comb:
                mask1 |= 1 << c
            a_vals = np.sort(
                np.array(
                    [
                        sum(mat[i][p[i]] for i in range(m1))
                        for p in itertools.permutations(comb)
                    ],
                    dtype=np.int64,
                )
            )
            b_vals = right_vals[(right_masks & mask1) == 0].ravel()
            total += int(
                np.searchsorted(a_vals, target_i64 - b_vals, side="right").sum(
                    dtype=np.int64
                )
            )
            checked += a_vals.size * b_vals.size
    else:
        for comb in itertools.combinations(range(n), m1):
            mask1 = 0
            for c in comb:
                mask1 |= 1 << c
            a_vals = sorted(
                sum(mat[i][p[i]] for i in range(m1))
                for p in itertools.permutations(comb)
            )
            for mask2, b_list in zip(right_masks_list, right_vals_list):
                if (mask1 & mask2) == 0:
                    for b in b_list:
                        total += bisect.bisect_right(a_vals, target - b)
                    checked += len(a_vals) * len(b_list)

    assert checked == math.perm(n, m), f"Checked {checked} != {math.perm(n, m)}"
    return total


def share_as_good(table: list[list[Fraction]], n_cols: int) -> Fraction:
    sub = [row[:n_cols] for row in table]
    mat = to_int_matrix(sub)
    target = sum(mat[i][i] for i in range(len(mat)))
    count = count_assignments_le(mat, target)
    return Fraction(count, math.perm(n_cols, len(mat)))


def claimed_sole_best_count(table: list[list[Fraction]]) -> int:
    return sum(
        1
        for i, row in enumerate(table)
        if all(row[i] < val for j, val in enumerate(row) if j != i)
    )


def mean_rank_of_claimed(table: list[list[Fraction]]) -> float:
    m = len(table)
    return float(sum((table[i][i] for i in range(m)), Fraction(0)) / m)


def compute_p_plus_1(table: list[list[Fraction]]) -> int:
    prod = 1
    for i, row in enumerate(table):
        claimed = row[i]
        prod *= sum(1 for val in row if val <= claimed)
    return prod


def compute_labels(
    sole_best_7: int,
    p_pooled: Fraction,
    p_per_judge: dict[str, Fraction],
) -> dict[str, str]:
    if sole_best_7 >= 5:
        repro = "largely reproduce the paper's ranking"
    elif sole_best_7 >= 3:
        repro = "partly reproduce the paper's ranking"
    else:
        repro = "do not reproduce the paper's ranking"

    if p_pooled <= Fraction(1, 100) and all(
        p <= Fraction(5, 100) for p in p_per_judge.values()
    ):
        pair = "pair the pillar's animals with the claimed figures better than chance"
    elif p_pooled > Fraction(5, 100):
        pair = "pairing not better than chance in this test"
    else:
        pair = "weak or mixed"

    return {"reproduction": repro, "pairing": pair}


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python replicate.py OUTDIR")

    outdir = Path(sys.argv[1])
    outdir.mkdir(parents=True, exist_ok=True)

    all_vendors, trials = load_rankings(Path("results/rankings.tsv"))

    judges_included: list[str] = []
    judges_excluded: dict[str, str] = {}
    for vendor in sorted(all_vendors):
        a_trials = trials[vendor]["A"]
        missing = [fig for fig in FIGURES if len(a_trials[fig]) < 3]
        reasons: list[str] = []
        if missing:
            reasons.append(
                f"fewer than 3 valid Task A rankings for {', '.join(missing)}"
            )
        if a_trials["A01"]:
            s01_mean = Fraction(
                sum(r["S01"] for r in a_trials["A01"]), len(a_trials["A01"])
            )
            if s01_mean > 2:
                reasons.append(
                    f"failed competence check (A01/S01 mean rank {float(s01_mean):.3f} > 2.0)"
                )
        if reasons:
            judges_excluded[vendor] = "; ".join(reasons)
        else:
            judges_included.append(vendor)

    if len(judges_included) < 2:
        summary = {
            "judges_included": judges_included,
            "judges_excluded": judges_excluded,
            "without_scorpion": None,
            "all8": None,
            "task_b": None,
            "labels": {
                "reproduction": "not testable",
                "pairing": "not testable",
            },
        }
    else:
        tables_a_no_scorp = {
            v: judge_table(
                trials[v]["A"], FIGURES[1:], SYMBOLS[1:], drop_option="S01"
            )
            for v in judges_included
        }
        pooled_a_no_scorp = pool_tables([tables_a_no_scorp[v] for v in judges_included])

        sole_best_7 = claimed_sole_best_count(pooled_a_no_scorp)
        p_pillar_7 = share_as_good(pooled_a_no_scorp, 7)
        p_11 = share_as_good(pooled_a_no_scorp, 11)

        per_judge_p: dict[str, Fraction] = {}
        per_judge_out: dict[str, dict[str, int | float]] = {}
        for v in judges_included:
            p_j = share_as_good(tables_a_no_scorp[v], 7)
            per_judge_p[v] = p_j
            per_judge_out[v] = {
                "claimed_sole_best_count": claimed_sole_best_count(
                    tables_a_no_scorp[v]
                ),
                "p_among_pillar_7": float(p_j),
            }

        tables_a_all8 = [
            judge_table(trials[v]["A"], FIGURES, SYMBOLS) for v in judges_included
        ]
        pooled_a_all8 = pool_tables(tables_a_all8)

        task_b_judges = [
            v
            for v in judges_included
            if all(len(trials[v]["B"][sym]) >= 3 for sym in PILLAR)
        ]
        if len(task_b_judges) < 2:
            task_b_out = None
        else:
            pooled_b_no_scorp = pool_tables(
                [
                    judge_table(
                        trials[v]["B"], PILLAR[1:], FIGURES[1:], drop_option="A01"
                    )
                    for v in task_b_judges
                ]
            )
            pooled_b_all8 = pool_tables(
                [judge_table(trials[v]["B"], PILLAR, FIGURES) for v in task_b_judges]
            )
            task_b_out = {
                "without_scorpion": {
                    "claimed_sole_best_count": claimed_sole_best_count(
                        pooled_b_no_scorp
                    ),
                    "p_orderings": float(share_as_good(pooled_b_no_scorp, 7)),
                },
                "all8": {
                    "claimed_sole_best_count": claimed_sole_best_count(pooled_b_all8),
                    "p_orderings": float(share_as_good(pooled_b_all8, 8)),
                },
            }

        summary = {
            "judges_included": judges_included,
            "judges_excluded": judges_excluded,
            "without_scorpion": {
                "claimed_sole_best_count": sole_best_7,
                "mean_rank_of_claimed": mean_rank_of_claimed(pooled_a_no_scorp),
                "p_among_pillar_7": float(p_pillar_7),
                "p_among_11": float(p_11),
                "per_judge": per_judge_out,
            },
            "all8": {
                "claimed_sole_best_count": claimed_sole_best_count(pooled_a_all8),
                "mean_rank_of_claimed": mean_rank_of_claimed(pooled_a_all8),
                "p_among_pillar_8": float(share_as_good(pooled_a_all8, 8)),
                "p_among_12": float(share_as_good(pooled_a_all8, 12)),
                "P_plus_1": compute_p_plus_1(pooled_a_all8),
            },
            "task_b": task_b_out,
            "labels": compute_labels(sole_best_7, p_pillar_7, per_judge_p),
        }

    (outdir / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
