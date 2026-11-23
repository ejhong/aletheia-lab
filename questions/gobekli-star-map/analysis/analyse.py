#!/usr/bin/env python3
"""Analyse the blind rankings of the paper's pictures (protocol.md).

    python analysis/analyse.py            # run from questions/gobekli-star-map; reads results/rankings.tsv,
                                          # writes results/summary.json and results/mean_ranks.tsv

All comparisons are exact: mean ranks are kept as integers (rank sums scaled to a common denominator).
Standard library and numpy (the repository's .venv: Python 3.12, numpy 2.3.5).
"""
import csv
import itertools
import json
import math
import pathlib

import numpy as np

Q = pathlib.Path(__file__).resolve().parent.parent
FIGURES = [f"A{k:02d}" for k in range(1, 9)]
SYMBOLS = [f"S{k:02d}" for k in range(1, 13)]
PILLAR = SYMBOLS[:8]                                   # the eight symbols on Pillar 43; A0k is claimed to be S0k
MIN_VALID, SCALE = 3, 60                               # valid rankings needed per target; 60 = lcm(3, 4, 5)
COMPETENCE = 2.0                                       # a judge must give the scorpion a mean rank of at most 2 for the scorpion figure
Q_NO_REPEATS, Q_REPEATS = 19958400, 12 ** 8


def read_rankings(path):
    """{vendor: {task: {target: [ranking, ...]}}}; a ranking is a list of option ids, best first (valid trials only)."""
    seen = {}
    for r in csv.DictReader(open(path, encoding="utf-8"), delimiter="\t"):
        seen.setdefault((r["vendor"], r["task"], r["target_id"], r["trial_id"]), []).append((int(r["position"]), r["option_id"]))
    out = {}
    for (vendor, task, target, trial), items in sorted(seen.items()):
        ranking = [o for _, o in sorted(items)]
        want = 12 if task == "A" else 8
        assert sorted(p for p, _ in items) == list(range(1, want + 1)) and len(set(ranking)) == want, f"bad ranking in trial {trial} ({vendor})"
        out.setdefault(vendor, {}).setdefault(task, {}).setdefault(target, []).append(ranking)
    return out


def scaled_table(rankings, rows, cols, drop=()):
    """T[row][col] = SCALE x (mean rank of `col` for target `row`), an exact integer, or None if any row has fewer
    than MIN_VALID rankings. Options in `drop` are removed from every ranking first, closing the gaps."""
    T = np.zeros((len(rows), len(cols)), dtype=np.int64)
    for i, row in enumerate(rows):
        rs = [[o for o in r if o not in drop] for r in rankings.get(row, [])]
        if len(rs) < MIN_VALID or SCALE % len(rs):
            return None
        for j, c in enumerate(cols):
            T[i, j] = sum(r.index(c) + 1 for r in rs) * (SCALE // len(rs))
    return T


def assignment_p(T, claimed, cols=None):
    """Exact share of assignments of distinct columns to the rows whose total is at most the claimed total.
    `cols` restricts the columns that may be assigned (default: all)."""
    cols = list(range(T.shape[1])) if cols is None else cols
    obs = int(sum(T[i, c] for i, c in enumerate(claimed)))
    sums, masks = np.zeros(1, dtype=np.int64), np.zeros(1, dtype=np.int64)
    for i in range(T.shape[0]):
        new_s, new_m = [], []
        for c in cols:
            free = (masks & (1 << c)) == 0
            new_s.append(sums[free] + T[i, c])
            new_m.append(masks[free] | (1 << c))
        sums, masks = np.concatenate(new_s), np.concatenate(new_m)
    hits = int((sums <= obs).sum())
    return {"assignments": int(sums.size), "as_good_or_better": hits, "p": hits / sums.size}


def describe(T, claimed, scale):
    """Per row: the claimed column's mean rank, the columns with the best mean rank, and how many columns are at
    least as good as the claimed one (ties count against the claim)."""
    rows = []
    for i, c in enumerate(claimed):
        best = int(T[i].min())
        rows.append({"claimed_mean_rank": T[i, c] / scale, "best": [int(j) for j in np.flatnonzero(T[i] == best)],
                     "claimed_is_sole_best": bool(T[i, c] == best and (T[i] == best).sum() == 1),
                     "others_at_least_as_good": int((T[i] <= T[i, c]).sum()) - 1})
    return rows


def analyse_a(TA12, TA11):
    """Task A. TA12: figures x 12 symbols. TA11: figures 2-8 x symbols 2-12, re-ranked without the scorpion."""
    out = {}
    cl8 = list(range(8))
    d8 = describe(TA12, cl8, SCALE)
    out["all8"] = {
        "mean_rank_of_claimed": float(np.mean([r["claimed_mean_rank"] for r in d8])), "chance_mean_rank": 6.5,
        "claimed_sole_best_count": sum(r["claimed_is_sole_best"] for r in d8),
        "among_12": assignment_p(TA12, cl8), "among_pillar_8": assignment_p(TA12, cl8, cols=list(range(8))),
        "per_figure": {FIGURES[i]: {**r, "best": [SYMBOLS[j] for j in r["best"]]} for i, r in enumerate(d8)}}
    p1 = math.prod(1 + r["others_at_least_as_good"] for r in d8)
    out["all8"]["papers_formula"] = {"P_plus_1": p1, "no_repeats": 2 * p1 / Q_NO_REPEATS, "repeats": 2 * p1 / Q_REPEATS}
    cl7 = list(range(7))
    d7 = describe(TA11, cl7, SCALE)
    sym11 = SYMBOLS[1:]
    out["without_scorpion"] = {
        "mean_rank_of_claimed": float(np.mean([r["claimed_mean_rank"] for r in d7])), "chance_mean_rank": 6.0,
        "claimed_sole_best_count": sum(r["claimed_is_sole_best"] for r in d7),
        "among_11": assignment_p(TA11, cl7), "among_pillar_7": assignment_p(TA11, cl7, cols=list(range(7))),
        "per_figure": {FIGURES[i + 1]: {**r, "best": [sym11[j] for j in r["best"]]} for i, r in enumerate(d7)}}
    return out


def analyse_b(TB8, TB7):
    """Task B. TB8: pillar symbols x 8 figures. TB7: symbols 2-8 x figures 2-8, re-ranked without the scorpion figure."""
    d8, d7 = describe(TB8, list(range(8)), SCALE), describe(TB7, list(range(7)), SCALE)
    return {"all8": {"mean_rank_of_claimed": float(np.mean([r["claimed_mean_rank"] for r in d8])), "chance_mean_rank": 4.5,
                     "claimed_sole_best_count": sum(r["claimed_is_sole_best"] for r in d8), "orderings": assignment_p(TB8, list(range(8)))},
            "without_scorpion": {"mean_rank_of_claimed": float(np.mean([r["claimed_mean_rank"] for r in d7])), "chance_mean_rank": 4.0,
                                 "claimed_sole_best_count": sum(r["claimed_is_sole_best"] for r in d7),
                                 "orderings": assignment_p(TB7, list(range(7)))}}


def tables(r):
    """The four scaled tables of one judge, or None where a task lacks coverage."""
    a, b = r.get("A", {}), r.get("B", {})
    return {"A12": scaled_table(a, FIGURES, SYMBOLS), "A11": scaled_table(a, FIGURES[1:], SYMBOLS[1:], drop=("S01",)),
            "B8": scaled_table(b, PILLAR, FIGURES), "B7": scaled_table(b, PILLAR[1:], FIGURES[1:], drop=("A01",))}


def reproduction_label(count):
    return ("largely reproduce the paper's ranking" if count >= 5 else "partly reproduce the paper's ranking" if count >= 3
            else "do not reproduce the paper's ranking")


def pairing_label(p, judge_ps):
    if p <= 0.01 and all(q <= 0.05 for q in judge_ps):
        return "pair the pillar's animals with the claimed figures better than chance"
    if p > 0.05:
        return "pairing not better than chance in this test"
    return "weak or mixed"


def main():
    data = read_rankings(Q / "results" / "rankings.tsv")
    out = {"judges": {}, "excluded": {}}
    tabs = {}
    for vendor in sorted(data):
        t = tables(data[vendor])
        if t["A12"] is None or t["A11"] is None:
            out["excluded"][vendor] = "fewer than 3 valid rankings for some figure in task A"
            continue
        scorpion = t["A12"][0, 0] / SCALE
        if scorpion > COMPETENCE:
            out["excluded"][vendor] = f"competence check failed: scorpion mean rank {scorpion:.2f} for the scorpion figure"
            continue
        tabs[vendor] = t
        out["judges"][vendor] = {"scorpion_mean_rank": scorpion, "task_a": analyse_a(t["A12"], t["A11"]),
                                 "task_b": analyse_b(t["B8"], t["B7"]) if t["B8"] is not None and t["B7"] is not None else None}
    judges = sorted(tabs)
    if len(judges) < 2:
        out["labels"] = {"reproduction": "not testable", "pairing": "not testable"}
    else:
        pooled = {k: sum(tabs[v][k] for v in judges) for k in ("A12", "A11")}          # equal weight per judge; scale is SCALE x judges
        out["pooled"] = {"judges": judges, "task_a": analyse_a_pooled(pooled, len(judges))}
        with_b = [v for v in judges if tabs[v]["B8"] is not None and tabs[v]["B7"] is not None]
        if len(with_b) >= 2:
            out["pooled"]["task_b"] = analyse_b_pooled({k: sum(tabs[v][k] for v in with_b) for k in ("B8", "B7")}, len(with_b))
            out["pooled"]["task_b_judges"] = with_b
        ws = out["pooled"]["task_a"]["without_scorpion"]
        out["labels"] = {"reproduction": "blind judges " + reproduction_label(ws["claimed_sole_best_count"]),
                         "pairing": pairing_label(ws["among_pillar_7"]["p"], [out["judges"][v]["task_a"]["without_scorpion"]["among_pillar_7"]["p"] for v in judges])}
        with open(Q / "results" / "mean_ranks.tsv", "w", encoding="utf-8") as f:
            f.write("table\tfigure\t" + "\t".join(SYMBOLS) + "\n")
            for name, T, scale in [("pooled", pooled["A12"], SCALE * len(judges))] + [(v, tabs[v]["A12"], SCALE) for v in judges]:
                for i, a in enumerate(FIGURES):
                    f.write(f"{name}\t{a}\t" + "\t".join(f"{x / scale:.3f}" for x in T[i]) + "\n")
        out["agreement_between_judges"] = {f"{a} vs {b}": float(np.corrcoef(tabs[a]["A12"].ravel(), tabs[b]["A12"].ravel())[0, 1])
                                           for a, b in itertools.combinations(judges, 2)}
    out["paper"] = {"P_plus_1": 2, "no_repeats": 4 / Q_NO_REPEATS, "repeats": 4 / Q_REPEATS, "claimed_rank_1_count": 7}
    json.dump(out, open(Q / "results" / "summary.json", "w"), indent=1)
    print(json.dumps({k: out[k] for k in ("labels", "excluded", "agreement_between_judges") if k in out}, indent=1))
    if "pooled" in out:
        a = out["pooled"]["task_a"]
        print(json.dumps({"all8": {k: a["all8"][k] for k in ("mean_rank_of_claimed", "claimed_sole_best_count", "among_12", "among_pillar_8", "papers_formula")},
                          "without_scorpion": {k: a["without_scorpion"][k] for k in ("mean_rank_of_claimed", "claimed_sole_best_count", "among_11", "among_pillar_7")}}, indent=1))


def _rescale(d, judges):
    """Pooled tables are sums over judges; divide the reported mean ranks by the number of judges."""
    for part in d.values():
        part["mean_rank_of_claimed"] /= judges
        for r in part.get("per_figure", {}).values():
            r["claimed_mean_rank"] /= judges
    return d


def analyse_a_pooled(p, judges):
    return _rescale(analyse_a(p["A12"], p["A11"]), judges)


def analyse_b_pooled(p, judges):
    return _rescale(analyse_b(p["B8"], p["B7"]), judges)


if __name__ == "__main__":
    main()
