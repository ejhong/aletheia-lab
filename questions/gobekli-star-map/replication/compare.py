#!/usr/bin/env python3
"""Compare a replication's summary.json with ours, key by key as listed in replication/FORMAT.md.

    python replication/compare.py THEIR_OUTDIR [OURS_SUMMARY]     # run from questions/gobekli-star-map

OURS_SUMMARY (or the environment variable OURS_SUMMARY) points at another summary.json in place of
results/summary.json; it is for testing. Numbers are "same" within 1e-9; lists and labels by equality (labels
ignoring case, curly apostrophes and a leading "blind judges "). Judges' exclusion reasons are free text: only
the set of excluded judges is compared, and the reasons are printed.
"""
import json
import os
import pathlib
import sys

Q = pathlib.Path(__file__).resolve().parent.parent
theirs = pathlib.Path(sys.argv[1])
ours_path = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else os.environ.get("OURS_SUMMARY", Q / "results" / "summary.json"))
o, t = json.load(open(ours_path)), json.load(open(theirs / "summary.json"))


def get(d, *path):
    for k in path:
        if not isinstance(d, dict) or k not in d:
            return None
        d = d[k]
    return d


def label(x):
    if not isinstance(x, str):
        return x
    x = x.strip().lower().replace("’", "'")
    return x[len("blind judges "):] if x.startswith("blind judges ") else x


def same(x, y):
    num = (int, float)
    if isinstance(x, num) and isinstance(y, num) and not isinstance(x, bool) and not isinstance(y, bool):
        return "same" if abs(x - y) <= 1e-9 else "DIFFERENT"
    return "same" if x == y else "DIFFERENT"


rows = []                                              # (key, ours, theirs)
rows.append(("judges_included", sorted(o.get("judges", {})), t.get("judges_included")))
rows.append(("judges_excluded (vendors)", sorted(o.get("excluded", {})), sorted((t.get("judges_excluded") or {}))))
A = ("pooled", "task_a")
for key, ours in [("claimed_sole_best_count", get(o, *A, "without_scorpion", "claimed_sole_best_count")),
                  ("mean_rank_of_claimed", get(o, *A, "without_scorpion", "mean_rank_of_claimed")),
                  ("p_among_pillar_7", get(o, *A, "without_scorpion", "among_pillar_7", "p")),
                  ("p_among_11", get(o, *A, "without_scorpion", "among_11", "p"))]:
    rows.append((f"without_scorpion.{key}", ours, get(t, "without_scorpion", key)))
for v in sorted(set(o.get("judges", {})) | set(get(t, "without_scorpion", "per_judge") or {})):
    ws = ("judges", v, "task_a", "without_scorpion")
    rows.append((f"without_scorpion.per_judge.{v}.claimed_sole_best_count", get(o, *ws, "claimed_sole_best_count"),
                 get(t, "without_scorpion", "per_judge", v, "claimed_sole_best_count")))
    rows.append((f"without_scorpion.per_judge.{v}.p_among_pillar_7", get(o, *ws, "among_pillar_7", "p"),
                 get(t, "without_scorpion", "per_judge", v, "p_among_pillar_7")))
for key, ours in [("claimed_sole_best_count", get(o, *A, "all8", "claimed_sole_best_count")),
                  ("mean_rank_of_claimed", get(o, *A, "all8", "mean_rank_of_claimed")),
                  ("p_among_pillar_8", get(o, *A, "all8", "among_pillar_8", "p")),
                  ("p_among_12", get(o, *A, "all8", "among_12", "p")),
                  ("P_plus_1", get(o, *A, "all8", "papers_formula", "P_plus_1"))]:
    rows.append((f"all8.{key}", ours, get(t, "all8", key)))
for part in ("without_scorpion", "all8"):
    B = ("pooled", "task_b", part)
    rows.append((f"task_b.{part}.claimed_sole_best_count", get(o, *B, "claimed_sole_best_count"),
                 get(t, "task_b", part, "claimed_sole_best_count")))
    rows.append((f"task_b.{part}.p_orderings", get(o, *B, "orderings", "p"), get(t, "task_b", part, "p_orderings")))
for key in ("reproduction", "pairing"):
    rows.append((f"labels.{key}", label(get(o, "labels", key)), label(get(t, "labels", key))))

w = max(len(k) for k, _, _ in rows)
for key, x, y in rows:
    print(f"{key:<{w}}  ours {x!r:<28} theirs {y!r:<28} {same(x, y)}")
print("exclusion reasons, ours:", o.get("excluded", {}))
print("exclusion reasons, theirs:", t.get("judges_excluded", {}))
print(f"{sum(same(x, y) == 'DIFFERENT' for _, x, y in rows)} of {len(rows)} keys differ")
