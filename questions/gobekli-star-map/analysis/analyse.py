#!/usr/bin/env python3
"""Analyse the blind rankings of the paper's pictures (protocol.md).

    python analysis/analyse.py            # run from questions/gobekli-star-map; reads results/rankings.tsv,
                                          # writes results/summary.json and results/mean_ranks.tsv

Needs numpy (the repository's .venv: Python 3.12, numpy 2.3.5).
"""
import csv
import json
import math
import pathlib

import numpy as np

Q = pathlib.Path(__file__).resolve().parent.parent
FIGURES = [f"A{k:02d}" for k in range(1, 9)]
SYMBOLS = [f"S{k:02d}" for k in range(1, 13)]
CLAIMED = {f"A{k:02d}": f"S{k:02d}" for k in range(1, 9)}        # the paper's pairing
MIN_VALID = 0.8
Q_NO_REPEATS, Q_REPEATS = 19958400, 12 ** 8


def read_rankings(path):
    """{vendor: {task: {target: [ranking, ...]}}}; a ranking is a list of option ids, best first. Valid trials only."""
    out, seen = {}, {}
    for r in csv.DictReader(open(path, encoding="utf-8"), delimiter="\t"):
        seen.setdefault((r["vendor"], r["task"], r["target_id"], r["trial_id"]), []).append((int(r["position"]), r["option_id"]))
    for (vendor, task, target, _), items in seen.items():
        out.setdefault(vendor, {}).setdefault(task, {}).setdefault(target, []).append([o for _, o in sorted(items)])
    return out


def mean_rank_table(rankings, rows, cols):
    """M[row][col] = mean rank (1 = best) of option `col` for target `row`, over that target's rankings."""
    M = np.full((len(rows), len(cols)), np.nan)
    for i, row in enumerate(rows):
        rs = rankings.get(row, [])
        if rs:
            M[i] = [np.mean([r.index(c) + 1 for r in rs]) for c in cols]
    return M


def exact_p(M, claimed_cols):
    """Share of assignments of distinct columns to the rows whose total is at most the claimed total.
    M: [rows, cols]; claimed_cols: the claimed column of each row. Enumerates every injective assignment."""
    rows, cols = M.shape
    obs = float(sum(M[i, c] for i, c in enumerate(claimed_cols)))
    sums, masks = np.zeros(1), np.zeros(1, dtype=np.int64)
    for i in range(rows):
        new_s, new_m = [], []
        for c in range(cols):
            free = (masks & (1 << c)) == 0
            new_s.append(sums[free] + M[i, c])
            new_m.append(masks[free] | (1 << c))
        sums, masks = np.concatenate(new_s), np.concatenate(new_m)
    return {"statistic": obs / rows, "assignments": int(sums.size), "as_good_or_better": int((sums <= obs + 1e-9).sum()),
            "p": float((sums <= obs + 1e-9).sum() / sums.size), "chance_mean": float(M.mean())}


def papers_formula(M, claimed_cols):
    """The paper's P+1: the product over rows of (1 + number of columns with a strictly better mean rank)."""
    better = [int((M[i] < M[i, c] - 1e-9).sum()) for i, c in enumerate(claimed_cols)]
    p1 = math.prod(1 + b for b in better)
    return {"better_symbols_per_figure": better, "P_plus_1": p1, "first_place_count": sum(b == 0 for b in better),
            "formula_no_repeats": 2 * p1 / Q_NO_REPEATS, "formula_repeats": 2 * p1 / Q_REPEATS}


def label(pooled_p, judge_ps):
    if pooled_p <= 0.001 and all(p <= 0.01 for p in judge_ps):
        return "blind judges see the claimed matches"
    if pooled_p > 0.05:
        return "blind judges do not see them"
    return "weak or mixed"


def analyse_table(M_a, M_b):
    cl = [SYMBOLS.index(CLAIMED[a]) for a in FIGURES]
    out = {"all8": {**exact_p(M_a, cl), **papers_formula(M_a, cl)}}
    keep = [j for j in range(12) if j != 0]                                   # without the scorpion: figures 2-8, symbols 2-12
    M7 = M_a[1:][:, keep]
    out["without_scorpion"] = {**exact_p(M7, list(range(7))), **papers_formula(M7, list(range(7)))}
    if M_b is not None and not np.isnan(M_b).any():
        out["task_b"] = exact_p(M_b, list(range(8)))                          # rows: symbols S01-S08; columns: figures A01-A08
    out["per_figure"] = {a: {"claimed_rank": float(M_a[i, cl[i]]), "top_symbol": SYMBOLS[int(np.argmin(M_a[i]))]} for i, a in enumerate(FIGURES)}
    return out


def main():
    data = read_rankings(Q / "results" / "rankings.tsv")
    n_trials = len(json.load(open(Q / "judging" / "trials.json"))["trials"])
    judges, tables_a, tables_b, out = [], {}, {}, {"judges": {}, "excluded": {}}
    for vendor in sorted(data):
        valid = sum(len(v) for task in data[vendor].values() for v in task.values())
        M_a = mean_rank_table(data[vendor].get("A", {}), FIGURES, SYMBOLS)
        M_b = mean_rank_table(data[vendor].get("B", {}), SYMBOLS[:8], FIGURES)
        if valid < MIN_VALID * n_trials or np.isnan(M_a).any():
            out["excluded"][vendor] = {"valid_trials": valid, "of": n_trials}
            continue
        judges.append(vendor)
        tables_a[vendor], tables_b[vendor] = M_a, M_b
        out["judges"][vendor] = {"valid_trials": valid, "of": n_trials, **analyse_table(M_a, M_b)}
    if len(judges) < 2:
        out["labels"] = {"all8": "not testable", "without_scorpion": "not testable"}
    else:
        P_a = np.mean([tables_a[v] for v in judges], axis=0)
        b_ok = [tables_b[v] for v in judges if not np.isnan(tables_b[v]).any()]
        P_b = np.mean(b_ok, axis=0) if b_ok else None
        out["pooled"] = analyse_table(P_a, P_b)
        out["labels"] = {k: label(out["pooled"][k]["p"], [out["judges"][v][k]["p"] for v in judges]) for k in ("all8", "without_scorpion")}
        with open(Q / "results" / "mean_ranks.tsv", "w", encoding="utf-8") as f:
            f.write("table\tfigure\t" + "\t".join(SYMBOLS) + "\n")
            for name, M in [("pooled", P_a)] + [(v, tables_a[v]) for v in judges]:
                for i, a in enumerate(FIGURES):
                    f.write(f"{name}\t{a}\t" + "\t".join(f"{x:.3f}" for x in M[i]) + "\n")
    out["paper"] = {"P_plus_1": 2, "formula_no_repeats": 4 / Q_NO_REPEATS, "formula_repeats": 4 / Q_REPEATS}
    json.dump(out, open(Q / "results" / "summary.json", "w"), indent=1)
    print(json.dumps({k: out[k] for k in ("labels", "pooled", "excluded") if k in out}, indent=1))


if __name__ == "__main__":
    main()
