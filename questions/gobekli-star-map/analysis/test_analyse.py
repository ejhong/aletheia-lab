#!/usr/bin/env python3
"""Unit tests for analyse.py, on made-up data only.

    python analysis/test_analyse.py       # from questions/gobekli-star-map

Expected values are derived independently (brute force with itertools, exact fractions, re-ranking by hand).
Temporary files go under /tmp/claude-501/ and are removed. No bytecode is written.
"""
import sys

sys.dont_write_bytecode = True                         # no __pycache__ next to analyse.py

import contextlib
import io
import itertools
import json
import math
import pathlib
import shutil
import tempfile
import traceback
from fractions import Fraction

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import analyse as A  # noqa: E402

FIG, SYM, PIL = A.FIGURES, A.SYMBOLS, A.PILLAR
SCRATCH = pathlib.Path("/tmp/claude-501")
HEADER = "vendor\ttrial_id\ttask\ttarget_id\tposition\toption_id\n"


# ---------------------------------------------------------------- helpers

def write_tsv(path, data, rng=None):
    """data: {vendor: {task: {target: [ranking, ...]}}}. Rows are written in shuffled order if rng is given."""
    rows = []
    for v, tasks in data.items():
        for task, targets in tasks.items():
            for target, rankings in targets.items():
                for k, r in enumerate(rankings):
                    for pos, o in enumerate(r, 1):
                        rows.append(f"{v}\t{v}-{task}-{target}-{k}\t{task}\t{target}\t{pos}\t{o}\n")
    if rng is not None:
        rng.shuffle(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(HEADER + "".join(rows), encoding="utf-8")


def run_main(data):
    """Run analyse.main() on a temporary folder; return (summary, mean_ranks.tsv text or None, stdout)."""
    SCRATCH.mkdir(parents=True, exist_ok=True)
    d = pathlib.Path(tempfile.mkdtemp(prefix="gobekli-test-", dir=SCRATCH))
    old = A.Q
    try:
        write_tsv(d / "results" / "rankings.tsv", data, np.random.default_rng(1))
        A.Q = d
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            A.main()
        out = json.loads((d / "results" / "summary.json").read_text())
        mr = d / "results" / "mean_ranks.tsv"
        return out, (mr.read_text() if mr.exists() else None), buf.getvalue()
    finally:
        A.Q = old
        shutil.rmtree(d, ignore_errors=True)


def brute_p(T, claimed, cols=None):
    """Independent: enumerate every assignment of distinct columns with itertools.permutations."""
    cols = list(range(len(T[0]))) if cols is None else cols
    obs = sum(T[i][c] for i, c in enumerate(claimed))
    n = hits = 0
    for perm in itertools.permutations(cols, len(T)):
        n += 1
        hits += sum(T[i][c] for i, c in enumerate(perm)) <= obs
    return n, hits


def brute_p_np(T, claimed):
    """Independent for 8 x 12: every 8-subset of columns (combinations) times every ordering of it (permutations)."""
    T = np.asarray(T)
    m, n = T.shape
    obs = sum(T[i, c] for i, c in enumerate(claimed))
    perms = np.array(list(itertools.permutations(range(m))))
    total = hits = 0
    for comb in itertools.combinations(range(n), m):
        cols = np.array(comb)[perms]                     # (m!, m)
        s = T[np.arange(m), cols].sum(axis=1)
        total += s.size
        hits += int((s <= obs).sum())
    return total, hits


def mean_table(rankings_by_target, rows, cols, drop=None):
    """Independent exact means with Fraction. Without-drop ranks are 1 + position; with `drop`, the rank is
    the position minus one if the dropped option stood earlier (re-ranking by hand)."""
    out = []
    for row in rows:
        rs = rankings_by_target[row]
        line = []
        for c in cols:
            tot = 0
            for r in rs:
                pos = r.index(c) + 1
                if drop is not None and r.index(drop) < r.index(c):
                    pos -= 1
                tot += pos
            line.append(Fraction(tot, len(rs)))
        out.append(line)
    return out


def avg_tables(ts):
    return [[sum(t[i][j] for t in ts) / len(ts) for j in range(len(ts[0][0]))] for i in range(len(ts[0]))]


def perfect_a(i):
    return [SYM[i]] + [s for s in SYM if s != SYM[i]]


def perfect_b(i):
    return [FIG[i]] + [f for f in FIG if f != FIG[i]]


def reversed_a(i):
    return [s for s in SYM if s != SYM[i]] + [SYM[i]]


def reversed_b(i):
    return [f for f in FIG if f != FIG[i]] + [FIG[i]]


def judge(fa, fb, reps=5):
    return {"A": {FIG[i]: [fa(i) for _ in range(reps)] for i in range(8)},
            "B": {PIL[i]: [fb(i) for _ in range(reps)] for i in range(8)}}


def random_judge(rng, reps=5):
    a = {}
    for i, f in enumerate(FIG):
        rs = []
        for _ in range(reps):
            if i == 0:                                    # scorpion first for the scorpion figure: passes the gate
                rest = list(rng.permutation(SYM[1:]))
                rs.append(["S01"] + [str(x) for x in rest])
            else:
                rs.append([str(x) for x in rng.permutation(SYM)])
        a[f] = rs
    b = {s: [[str(x) for x in rng.permutation(FIG)] for _ in range(reps)] for s in PIL}
    return {"A": a, "B": b}


# ---------------------------------------------------------------- 1. read_rankings

def test_read_rankings():
    SCRATCH.mkdir(parents=True, exist_ok=True)
    d = pathlib.Path(tempfile.mkdtemp(prefix="gobekli-test-", dir=SCRATCH))
    try:
        p = d / "r.tsv"
        p.write_text(HEADER + "".join([
            "v2\tt2\tA\tA01\t2\tS01\n",
            "v1\tt1\tA\tA01\t3\tS01\n",
            "v1\tt1\tA\tA01\t1\tS03\n",
            "v1\tt2\tA\tA01\t2\tS03\n",
            "v1\tt1\tA\tA01\t2\tS02\n",
            "v1\tt3\tB\tS01\t1\tA02\n",
            "v2\tt2\tA\tA01\t1\tS02\n",
            "v1\tt2\tA\tA01\t1\tS02\n",
            "v1\tt2\tA\tA01\t3\tS01\n",
            "v1\tt3\tB\tS01\t2\tA01\n",
        ]), encoding="utf-8")
        got = A.read_rankings(p)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    assert got == {"v1": {"A": {"A01": [["S03", "S02", "S01"], ["S02", "S03", "S01"]]}, "B": {"S01": [["A02", "A01"]]}},
                   "v2": {"A": {"A01": [["S02", "S01"]]}}}, got


# ---------------------------------------------------------------- 2. scaled_table

def test_scaled_table_exact():
    o = ["a", "b", "c", "d"]
    r = {"x3": [["a", "b", "c", "d"], ["b", "a", "c", "d"], ["b", "c", "d", "a"]],             # a: 1,2,4 -> 7/3
         "x4": [["a", "b", "c", "d"], ["a", "b", "c", "d"], ["b", "a", "c", "d"], ["b", "c", "a", "d"]],  # 1,1,2,3 -> 7/4
         "x5": [["a", "b", "c", "d"], ["b", "a", "c", "d"], ["c", "a", "b", "d"], ["b", "c", "a", "d"], ["c", "d", "a", "b"]]}  # 1,2,2,3,3 -> 11/5
    T = A.scaled_table(r, ["x3", "x4", "x5"], o)
    assert T.dtype == np.int64
    assert T[0, 0] == 140 and T[1, 0] == 105 and T[2, 0] == 132, T
    want = mean_table(r, ["x3", "x4", "x5"], o)
    assert [[Fraction(int(x), 60) for x in row] for row in T] == want


def test_scaled_table_too_few():
    o = ["a", "b"]
    r = {"x": [["a", "b"]] * 3, "y": [["a", "b"]] * 2}
    assert A.scaled_table(r, ["x", "y"], o) is None
    assert A.scaled_table(r, ["x", "z"], o) is None                   # missing target
    assert A.scaled_table(r, ["x"], o) is not None


def test_scaled_table_drop():
    r = {"x": [["b", "a", "c", "d"], ["c", "d", "b", "a"], ["a", "b", "c", "d"]]}
    T = A.scaled_table(r, ["x"], ["b", "c", "d"], drop=("a",))
    # by hand, a removed: [b,c,d] [c,d,b] [b,c,d] -> b: 1,3,1 = 5/3; c: 2,1,2 = 5/3; d: 3,2,3 = 8/3
    assert T.tolist() == [[100, 100, 160]], T


def test_scaled_table_more_than_five_rankings_DOCUMENTS():
    """Documents behaviour: 6 rankings work, but 7 or more valid rankings give None (SCALE % 7 != 0), and
    main() would then exclude the judge with the misleading reason 'fewer than 3 valid rankings'."""
    o = ["a", "b"]
    assert A.scaled_table({"x": [["a", "b"]] * 6}, ["x"], o).tolist() == [[60, 120]]
    assert A.scaled_table({"x": [["a", "b"]] * 7}, ["x"], o) is None


def test_invalid_ranking_not_validated_DOCUMENTS():
    """Documents behaviour: read_rankings does not check that a trial lists every option exactly once. A ranking
    missing an option crashes scaled_table (ValueError); a duplicated row silently shifts later ranks."""
    o = ["a", "b", "c"]
    try:
        A.scaled_table({"x": [["a", "b"], ["a", "b", "c"], ["a", "b", "c"]]}, ["x"], o)
        raise AssertionError("expected ValueError")
    except ValueError:
        pass
    T = A.scaled_table({"x": [["a", "a", "b", "c"], ["a", "b", "c"], ["a", "b", "c"]]}, ["x"], o)
    assert T.tolist() == [[60, 140, 200]]                              # b gets rank 3 once although it was second


# ---------------------------------------------------------------- 3. assignment_p

def _check_assign(T, claimed, cols=None):
    got = A.assignment_p(np.asarray(T, dtype=np.int64), claimed, cols)
    n, hits = brute_p(np.asarray(T).tolist(), claimed, cols)
    assert got["assignments"] == n and got["as_good_or_better"] == hits and got["p"] == hits / n, (got, n, hits)


def test_assignment_p_brute_force():
    rng = np.random.default_rng(7)
    for _ in range(20):
        _check_assign(rng.integers(0, 10, (4, 6)), [0, 1, 2, 3])
        _check_assign(rng.integers(0, 10, (4, 6)), list(rng.permutation(6)[:4]))
        _check_assign(rng.integers(0, 10, (5, 7)), [0, 1, 2, 3, 4], cols=[0, 1, 2, 3, 4])
        _check_assign(rng.integers(0, 10, (4, 6)), [0, 2, 4, 5], cols=[5, 0, 2, 4])
        _check_assign(rng.integers(0, 3, (4, 5)), [0, 1, 2, 3])        # many ties


def test_assignment_p_ties():
    T = np.array([[1, 1, 5], [1, 1, 5], [5, 5, 1]])
    got = A.assignment_p(T, [0, 1, 2])
    assert got == {"assignments": 6, "as_good_or_better": 2, "p": 2 / 6}, got    # the swap of rows 0 and 1 ties
    got = A.assignment_p(np.full((4, 6), 3), [0, 1, 2, 3])
    assert got["as_good_or_better"] == got["assignments"] == 360 and got["p"] == 1.0


def test_assignment_p_counts_and_unique_best():
    got = A.assignment_p(np.zeros((8, 12), dtype=np.int64), list(range(8)))
    assert got["assignments"] == 19958400 == math.perm(12, 8) and got["p"] == 1.0
    got = A.assignment_p(np.zeros((7, 11), dtype=np.int64), list(range(7)))
    assert got["assignments"] == 1663200 == math.perm(11, 7)
    T = np.ones((8, 12), dtype=np.int64)
    np.fill_diagonal(T, 0)
    got = A.assignment_p(T, list(range(8)))
    assert got["as_good_or_better"] == 1 and got["p"] == 1 / 19958400
    got = A.assignment_p(T, list(range(8)), cols=list(range(8)))
    assert got == {"assignments": 40320, "as_good_or_better": 1, "p": 1 / 40320}


# ---------------------------------------------------------------- 4. describe

def test_describe():
    T = np.array([[60, 120, 180],     # claimed 0 sole best
                  [60, 60, 180],      # claimed 0 tied for best: not sole best
                  [120, 60, 120],     # claimed 0 tied with 2, beaten by 1
                  [90, 90, 90]])      # all tied
    d = A.describe(T, [0, 0, 0, 0], 60)
    assert [r["claimed_is_sole_best"] for r in d] == [True, False, False, False]
    assert [r["others_at_least_as_good"] for r in d] == [0, 1, 2, 2]
    assert [r["best"] for r in d] == [[0], [0, 1], [1], [0, 1, 2]]
    assert [r["claimed_mean_rank"] for r in d] == [1.0, 1.0, 2.0, 1.5]
    d = A.describe(np.full((2, 12), 390), [3, 7], 60)
    assert all(r["others_at_least_as_good"] == 11 and not r["claimed_is_sole_best"] for r in d)


# ---------------------------------------------------------------- 5a. perfect key

def test_perfect_key():
    data = {v: judge(perfect_a, perfect_b) for v in ("j1", "j2", "j3")}
    out, mr, _ = run_main(data)
    assert out["excluded"] == {} and out["pooled"]["judges"] == ["j1", "j2", "j3"]
    a = out["pooled"]["task_a"]
    assert a["all8"]["claimed_sole_best_count"] == 8 and a["without_scorpion"]["claimed_sole_best_count"] == 7
    assert a["all8"]["mean_rank_of_claimed"] == 1.0 and a["without_scorpion"]["mean_rank_of_claimed"] == 1.0
    assert a["all8"]["among_12"] == {"assignments": 19958400, "as_good_or_better": 1, "p": 1 / 19958400}
    assert a["all8"]["among_pillar_8"] == {"assignments": 40320, "as_good_or_better": 1, "p": 1 / 40320}
    assert a["without_scorpion"]["among_11"] == {"assignments": 1663200, "as_good_or_better": 1, "p": 1 / 1663200}
    assert a["without_scorpion"]["among_pillar_7"] == {"assignments": 5040, "as_good_or_better": 1, "p": 1 / 5040}
    assert a["all8"]["papers_formula"]["P_plus_1"] == 1
    assert a["all8"]["papers_formula"]["no_repeats"] == 2 / 19958400
    b = out["pooled"]["task_b"]
    assert out["pooled"]["task_b_judges"] == ["j1", "j2", "j3"]
    assert b["all8"]["claimed_sole_best_count"] == 8 and b["without_scorpion"]["claimed_sole_best_count"] == 7
    assert b["all8"]["orderings"]["p"] == 1 / 40320 and b["without_scorpion"]["orderings"]["p"] == 1 / 5040
    assert out["labels"] == {"reproduction": "blind judges largely reproduce the paper's ranking",
                             "pairing": "pair the pillar's animals with the claimed figures better than chance"}
    assert all(abs(x - 1.0) < 1e-12 for x in out["agreement_between_judges"].values())
    assert out["judges"]["j1"]["scorpion_mean_rank"] == 1.0
    assert mr is not None and mr.count("\n") == 1 + 8 * 4


# ---------------------------------------------------------------- 5b. reversed key

def test_reversed_key_fails_gate():
    data = {v: judge(reversed_a, reversed_b) for v in ("j1", "j2", "j3")}
    out, mr, _ = run_main(data)
    assert out["judges"] == {} and "pooled" not in out and mr is None
    assert all(r.startswith("competence check failed: scorpion mean rank 12.00") for r in out["excluded"].values())
    assert sorted(out["excluded"]) == ["j1", "j2", "j3"]
    assert out["labels"] == {"reproduction": "not testable", "pairing": "not testable"}
    # The tables themselves, analysed directly, show what the gate hides:
    t = A.tables(data["j1"])
    r = A.analyse_a(t["A12"], t["A11"])
    assert r["all8"]["claimed_sole_best_count"] == 0 and r["without_scorpion"]["claimed_sole_best_count"] == 0
    assert r["all8"]["among_pillar_8"]["p"] == 1.0 and r["without_scorpion"]["among_pillar_7"]["p"] == 1.0
    assert r["all8"]["among_12"]["p"] == 1.0 and r["without_scorpion"]["among_11"]["p"] == 1.0
    assert A.reproduction_label(r["without_scorpion"]["claimed_sole_best_count"]) == "do not reproduce the paper's ranking"


def test_reversed_key_scorpion_first():
    fa = lambda i: perfect_a(0) if i == 0 else reversed_a(i)
    data = {v: judge(fa, reversed_b) for v in ("j1", "j2", "j3")}
    out, _, _ = run_main(data)
    assert out["excluded"] == {} and out["judges"]["j2"]["scorpion_mean_rank"] == 1.0
    a = out["pooled"]["task_a"]
    assert a["without_scorpion"]["claimed_sole_best_count"] == 0 and a["all8"]["claimed_sole_best_count"] == 1
    assert a["without_scorpion"]["among_pillar_7"]["p"] == 1.0 and a["without_scorpion"]["among_11"]["p"] == 1.0
    assert a["without_scorpion"]["mean_rank_of_claimed"] == 11.0
    T = A.tables(data["j1"])["A12"] * 3
    n, hits = brute_p(T.tolist(), list(range(8)), list(range(8)))
    assert a["all8"]["among_pillar_8"] == {"assignments": n, "as_good_or_better": hits, "p": hits / n}
    assert out["pooled"]["task_b"]["all8"]["orderings"]["p"] == 1.0
    assert out["labels"] == {"reproduction": "blind judges do not reproduce the paper's ranking",
                             "pairing": "pairing not better than chance in this test"}


# ---------------------------------------------------------------- 5c. all tied

def tied_judge(scorpion_first=False):
    """4 repetitions: forward, reversed, forward, reversed. Every symbol's rank sum is 2 x 13 = 26, mean 6.5;
    with S01 removed, 2 x 12 = 24, mean 6. (With 5 repetitions an exact tie is impossible: 5 x 6.5 is not an
    integer rank sum.)"""
    a = {}
    for i, f in enumerate(FIG):
        if i == 0 and scorpion_first:
            a[f] = [SYM] * 4
        else:
            a[f] = [SYM, SYM[::-1], SYM, SYM[::-1]]
    b = {s: [FIG, FIG[::-1], FIG, FIG[::-1]] for s in PIL}
    return {"A": a, "B": b}


def test_all_tied_tables():
    t = A.tables(tied_judge())
    assert (t["A12"] == 390).all() and (t["A11"] == 360).all() and (t["B8"] == 270).all() and (t["B7"] == 240).all()
    r = A.analyse_a(t["A12"], t["A11"])
    assert r["all8"]["claimed_sole_best_count"] == 0 and r["without_scorpion"]["claimed_sole_best_count"] == 0
    for k in ("among_12", "among_pillar_8"):
        assert r["all8"][k]["p"] == 1.0
    for k in ("among_11", "among_pillar_7"):
        assert r["without_scorpion"][k]["p"] == 1.0
    pf = r["all8"]["papers_formula"]
    assert pf["P_plus_1"] == 12 ** 8                                    # least impressive, not 1
    assert pf["repeats"] == 2.0 and pf["no_repeats"] == 2 * 12 ** 8 / 19958400   # note: > 1, not a probability
    rb = A.analyse_b(t["B8"], t["B7"])
    assert rb["all8"]["orderings"]["p"] == 1.0 and rb["without_scorpion"]["claimed_sole_best_count"] == 0


def test_all_tied_end_to_end():
    out, _, _ = run_main({v: tied_judge() for v in ("j1", "j2", "j3")})
    assert all("scorpion mean rank 6.50" in r for r in out["excluded"].values()) and len(out["excluded"]) == 3
    assert out["labels"]["reproduction"] == "not testable"
    out, _, _ = run_main({v: tied_judge(scorpion_first=True) for v in ("j1", "j2", "j3")})
    a = out["pooled"]["task_a"]
    assert out["excluded"] == {}
    assert a["without_scorpion"]["claimed_sole_best_count"] == 0 and a["all8"]["claimed_sole_best_count"] == 1
    assert a["without_scorpion"]["among_pillar_7"]["p"] == 1.0 and a["without_scorpion"]["among_11"]["p"] == 1.0
    assert a["all8"]["papers_formula"]["P_plus_1"] == 12 ** 7
    assert out["labels"] == {"reproduction": "blind judges do not reproduce the paper's ranking",
                             "pairing": "pairing not better than chance in this test"}


# ---------------------------------------------------------------- 5d. random

def test_random_rankings():
    rng = np.random.default_rng(20261123)
    data = {v: random_judge(rng) for v in ("j1", "j2", "j3")}
    out, mr, _ = run_main(data)
    assert out["excluded"] == {}
    J = len(data)
    # Independent exact tables (Fractions), averaged over judges.
    a12 = avg_tables([mean_table(data[v]["A"], FIG, SYM) for v in data])
    a11 = avg_tables([mean_table(data[v]["A"], FIG[1:], SYM[1:], drop="S01") for v in data])
    b8 = avg_tables([mean_table(data[v]["B"], PIL, FIG) for v in data])
    b7 = avg_tables([mean_table(data[v]["B"], PIL[1:], FIG[1:], drop="A01") for v in data])
    # The program's pooled tables equal SCALE x judges x the average of the judges' means.
    tabs = {v: A.tables(data[v]) for v in data}
    for k, ref in (("A12", a12), ("A11", a11), ("B8", b8), ("B7", b7)):
        pooled = sum(tabs[v][k] for v in data)
        assert [[Fraction(int(x), 60 * J) for x in row] for row in pooled] == ref, k
    # mean_ranks.tsv pooled rows
    lines = [l.split("\t") for l in mr.strip().split("\n")[1:] if l.startswith("pooled\t")]
    assert len(lines) == 8
    for i, l in enumerate(lines):
        assert l[1] == FIG[i] and l[2:] == [f"{float(x):.3f}" for x in a12[i]]
    # Brute-force p values from the independent tables (Fractions are exact).
    pa = out["pooled"]["task_a"]
    n, h = brute_p(a12, list(range(8)), list(range(8)))
    assert pa["all8"]["among_pillar_8"] == {"assignments": n, "as_good_or_better": h, "p": h / n}
    n, h = brute_p(a11, list(range(7)), list(range(7)))
    assert pa["without_scorpion"]["among_pillar_7"] == {"assignments": n, "as_good_or_better": h, "p": h / n}
    n, h = brute_p(a11, list(range(7)))
    assert pa["without_scorpion"]["among_11"] == {"assignments": n, "as_good_or_better": h, "p": h / n}
    a12i = [[int(x * 60 * J) for x in row] for row in a12]
    n, h = brute_p_np(a12i, list(range(8)))
    assert pa["all8"]["among_12"] == {"assignments": n, "as_good_or_better": h, "p": h / n}
    pb = out["pooled"]["task_b"]
    n, h = brute_p(b8, list(range(8)))
    assert pb["all8"]["orderings"] == {"assignments": n, "as_good_or_better": h, "p": h / n}
    n, h = brute_p(b7, list(range(7)))
    assert pb["without_scorpion"]["orderings"] == {"assignments": n, "as_good_or_better": h, "p": h / n}
    # Per-judge pillar-7 p, mean ranks, sole-best counts and the paper's formula.
    for v in data:
        t = mean_table(data[v]["A"], FIG[1:], SYM[1:], drop="S01")
        n, h = brute_p(t, list(range(7)), list(range(7)))
        assert out["judges"][v]["task_a"]["without_scorpion"]["among_pillar_7"]["p"] == h / n
    assert abs(pa["all8"]["mean_rank_of_claimed"] - float(sum(a12[i][i] for i in range(8)) / 8)) < 1e-12
    assert abs(pa["without_scorpion"]["mean_rank_of_claimed"] - float(sum(a11[i][i] for i in range(7)) / 7)) < 1e-12
    for i, f in enumerate(FIG[1:]):
        assert abs(pa["without_scorpion"]["per_figure"][f]["claimed_mean_rank"] - float(a11[i][i])) < 1e-12
    sole = sum(all(a11[i][i] < a11[i][j] for j in range(11) if j != i) for i in range(7))
    assert pa["without_scorpion"]["claimed_sole_best_count"] == sole
    p1 = math.prod(sum(a12[i][j] <= a12[i][i] for j in range(12)) for i in range(8))
    assert pa["all8"]["papers_formula"]["P_plus_1"] == p1
    # Labels follow from the reported numbers.
    ps = [out["judges"][v]["task_a"]["without_scorpion"]["among_pillar_7"]["p"] for v in data]
    assert out["labels"]["pairing"] == A.pairing_label(pa["without_scorpion"]["among_pillar_7"]["p"], ps)
    assert out["labels"]["reproduction"] == "blind judges " + A.reproduction_label(sole)


# ---------------------------------------------------------------- 5e. missing data

def test_missing_data():
    rng = np.random.default_rng(5)
    data = {v: random_judge(rng) for v in ("j1", "j2", "j3", "j4")}
    data["j1"]["A"]["A03"] = data["j1"]["A"]["A03"][:2]               # only 2 valid rankings for one figure
    data["j4"]["B"]["S05"] = data["j4"]["B"]["S05"][:2]               # complete A, incomplete B
    out, _, _ = run_main(data)
    assert out["excluded"] == {"j1": "fewer than 3 valid rankings for some figure in task A"}
    assert out["pooled"]["judges"] == ["j2", "j3", "j4"]
    assert out["pooled"]["task_b_judges"] == ["j2", "j3"]
    assert out["judges"]["j4"]["task_b"] is None and out["judges"]["j2"]["task_b"] is not None
    b8 = avg_tables([mean_table(data[v]["B"], PIL, FIG) for v in ("j2", "j3")])
    assert abs(out["pooled"]["task_b"]["all8"]["mean_rank_of_claimed"] - float(sum(b8[i][i] for i in range(8)) / 8)) < 1e-12
    a12 = avg_tables([mean_table(data[v]["A"], FIG, SYM) for v in ("j2", "j3", "j4")])
    assert abs(out["pooled"]["task_a"]["all8"]["mean_rank_of_claimed"] - float(sum(a12[i][i] for i in range(8)) / 8)) < 1e-12
    # Only one judge left: not testable.
    out, mr, _ = run_main({"j1": data["j1"], "j2": data["j2"]})
    assert out["excluded"] == {"j1": "fewer than 3 valid rankings for some figure in task A"}
    assert list(out["judges"]) == ["j2"] and "pooled" not in out and mr is None
    assert out["labels"] == {"reproduction": "not testable", "pairing": "not testable"}
    # Two judges with A but neither has complete B: pooled A only.
    d2 = {v: random_judge(rng) for v in ("k1", "k2")}
    d2["k1"]["B"]["S02"] = d2["k1"]["B"]["S02"][:1]
    out, _, _ = run_main(d2)
    assert "task_b" not in out["pooled"] and "task_b_judges" not in out["pooled"]


def test_competence_boundary():
    base = judge(perfect_a, perfect_b)
    ok = json.loads(json.dumps(base))
    ok["A"]["A01"] = [perfect_a(0), perfect_a(0), SYM[1:4] + ["S01"] + SYM[4:]]          # 1,1,4 -> 2.0 passes
    bad = json.loads(json.dumps(base))
    bad["A"]["A01"] = [perfect_a(0), SYM[1:2] + ["S01"] + SYM[2:], SYM[1:4] + ["S01"] + SYM[4:]]  # 1,2,4 -> 7/3
    out, _, _ = run_main({"ok": ok, "bad": bad, "j3": base})
    assert out["judges"]["ok"]["scorpion_mean_rank"] == 2.0
    assert out["excluded"] == {"bad": "competence check failed: scorpion mean rank 2.33 for the scorpion figure"}


# ---------------------------------------------------------------- 5f. unequal counts

def test_unequal_counts():
    u1 = judge(perfect_a, perfect_b)
    u2 = judge(perfect_a, perfect_b)
    u1["A"]["A02"] = [perfect_a(1)] * 3                                  # 3 rankings, S02 first: mean 1
    third = ["S04", "S03", "S02"] + [s for s in SYM if s not in ("S02", "S03", "S04")]
    u2["A"]["A02"] = [third] * 5                                         # 5 rankings, S02 third: mean 3
    out, mr, _ = run_main({"u1": u1, "u2": u2})
    pf = out["pooled"]["task_a"]
    assert pf["all8"]["per_figure"]["A02"]["claimed_mean_rank"] == 2.0        # equal weight; by rankings: 18/8 = 2.25
    assert pf["without_scorpion"]["per_figure"]["A02"]["claimed_mean_rank"] == 2.0
    assert pf["all8"]["per_figure"]["A02"]["best"] == ["S02"]
    row = [l.split("\t") for l in mr.split("\n") if l.startswith("pooled\tA02\t")][0]
    assert row[2 + 1] == "2.000"                                         # S02 = (1 + 3) / 2
    assert row[2 + 2] == "2.500" and row[2 + 3] == "2.500"             # S03: (3 + 2) / 2; S04: (4 + 1) / 2
    assert row[2 + 0] == "3.000"                                         # S01: u1 rank 2, u2 rank 4 -> 3
    assert abs(pf["all8"]["mean_rank_of_claimed"] - (7 * 1 + 2) / 8) < 1e-12


# ---------------------------------------------------------------- 6. labels

def test_reproduction_label():
    for c, want in [(7, "largely"), (5, "largely"), (4, "partly"), (3, "partly"), (2, "do not"), (0, "do not")]:
        assert A.reproduction_label(c).startswith(want), (c, A.reproduction_label(c))


def test_pairing_label():
    better, none, weak = ("pair the pillar's animals with the claimed figures better than chance",
                          "pairing not better than chance in this test", "weak or mixed")
    cases = [((0.01, [0.05, 0.05]), better), ((0.0, [0.0]), better), ((0.001, []), better),
             ((0.01, [0.05, 0.0500001]), weak), ((0.0100001, [0.0, 0.0]), weak), ((0.05, [1.0]), weak),
             ((0.03, [0.01]), weak), ((0.0500001, [0.0]), none), ((1.0, [0.0, 0.0]), none)]
    for args, want in cases:
        assert A.pairing_label(*args) == want, (args, A.pairing_label(*args))


# ---------------------------------------------------------------- runner

def main():
    import time
    tests = [(k, v) for k, v in globals().items() if k.startswith("test_") and callable(v)]
    failed = 0
    t0 = time.time()
    for name, fn in tests:
        try:
            fn()
            print(f"{name} ok")
        except Exception:
            failed += 1
            print(f"{name} FAILED")
            traceback.print_exc()
    print(f"{len(tests) - failed}/{len(tests)} passed in {time.time() - t0:.1f}s")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
