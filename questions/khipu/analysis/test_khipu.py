#!/usr/bin/env python3
"""Synthetic unit tests for #13 (khipu) before trusting OKR khipu.db outputs."""
import numpy as np
from run_khipu import (
    best_contiguous_match,
    best_moiety_partition_error,
    decode_cord_locke_ascher,
    score_aligned_window,
)


def test_locke_ascher_decoder():
    # 2 single knots (100s) + 3 single knots (10s) + 1 long knot with 7 turns = 237
    cl_237 = [
        [("S", 0, 8.0), ("S", 0, 8.5)],
        [("S", 0, 14.0), ("S", 0, 14.5), ("S", 0, 15.0)],
        [("L", 7, 21.0)],
    ]
    assert decode_cord_locke_ascher(cl_237) == 237
    # 1 single knot (10s) + 1 figure-eight knot = 11
    cl_11 = [[("S", 0, 10.0)], [("E", 0, 18.0)]]
    assert decode_cord_locke_ascher(cl_11) == 11
    # Empty = 0
    assert decode_cord_locke_ascher([]) == 0
    print("PASS: test_locke_ascher_decoder")


def test_planted_copy_and_reversed_mirror_recovery():
    v1 = np.array([0, 0, 15, 42, 8, 103, 27, 64, 19, 5, 0], dtype=np.int64)
    # Planted reversed near-copy (1-knot rounding difference on 103->104) with leading noise
    v2 = np.array([99, 5, 19, 64, 27, 104, 8, 42, 15, 77], dtype=np.int64)
    m = best_contiguous_match(v1, v2, allow_reverse=True)
    assert m is not None, "Failed to recover planted reversed copy!"
    assert m["orient"] == "rev"
    assert m["L"] == 8
    assert m["tier"] == "A"
    # Reject trivial all-1s vector
    t1 = np.array([1, 1, 1, 1, 1, 1, 1, 1], dtype=np.int64)
    t2 = np.array([1, 1, 1, 1, 1, 1, 1, 1], dtype=np.int64)
    assert score_aligned_window(t1, t2) is None
    print("PASS: test_planted_copy_and_reversed_mirror_recovery")


def test_exact_moiety_partition():
    # 1670 San Pedro de Corongo pachacas: Namus 18, Corongo 23, Cuyuchin 9, Cusca 7, Guauyan 41, Ucore 32
    pachacas = [18, 23, 9, 7, 41, 32]
    # Against (70, 63): FitzPatrick {18, 9, 41}=68 vs {23, 7, 32}=62 gives L1 = |68-70| + |62-63| = 3
    l1, dv, pair = best_moiety_partition_error(pachacas, 70, 63)
    assert pair == (68, 62), f"Expected (68, 62), got {pair}"
    assert l1 == 3 and dv == 2
    print("PASS: test_exact_moiety_partition")


if __name__ == "__main__":
    test_locke_ascher_decoder()
    test_planted_copy_and_reversed_mirror_recovery()
    test_exact_moiety_partition()
    print("ALL 3 KHIPU UNIT TESTS PASSED!")
