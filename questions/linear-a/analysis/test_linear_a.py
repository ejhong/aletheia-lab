#!/usr/bin/env python3
"""Synthetic unit tests for Linear A decipherment audit (#12)."""
import random
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import run_linear_a as la


def test_projection_and_neutralization():
    # K covers k/g/q, P covers p/b, T covers t/d/ṭ/ṯ, S covers s/z/š/ṣ, R covers r/l
    assert la.project_phoneme_string("baʕl", drop_wy=False) == "PR"
    assert la.project_phoneme_string("b-ṭ-n", drop_wy=False) == "PTN"
    assert la.project_phoneme_string("q-d-š", drop_wy=False) == "KTS"
    assert la.project_phoneme_string("n-w-y", drop_wy=False) == "NWY"
    assert la.project_phoneme_string("n-w-y", drop_wy=True) == "N"
    assert la.project_phoneme_string("*ṣih(V)r-", drop_wy=False) == "SR"
    print("PASS: test_projection_and_neutralization")


def test_regime_b_affix_stripping():
    roots = {"KTP", "SMR", "PRK"}
    assert la.match_skeleton("KTP", roots, "A1") is True
    assert la.match_skeleton("MKTP", roots, "A1") is False
    assert la.match_skeleton("MKTP", roots, "B") is True   # M- prefix
    assert la.match_skeleton("KTPT", roots, "B") is True   # -T suffix
    assert la.match_skeleton("YSMRN", roots, "B") is True  # Y-...-N circumfix
    assert la.match_skeleton("RKT", roots, "B") is False
    print("PASS: test_regime_b_affix_stripping")


def test_planted_semitic_vs_random_permutation():
    # Build a synthetic sparse 3-consonant root bank (80 roots out of 729)
    rng = random.Random(99)
    all_3 = [a + b + c for a in la.CLASSES_9 for b in la.CLASSES_9 for c in la.CLASSES_9]
    roots = set(rng.sample(all_3, 80))
    # Planted true Semitic corpus: 60% drawn from roots, 40% random
    planted = rng.sample(sorted(roots), 60) + rng.sample(all_3, 40)
    res_true = la.consonant_permutation_test(planted, [1] * len(planted), roots, "A1", la.CLASSES_9, n_perm=300, seed=1)
    assert res_true["obs_type_rate"] > 0.55 and res_true["p_perm_type"] < 0.01, f"Planted failed: {res_true}"
    # Random unrelated corpus
    rand_corpus = rng.sample(all_3, 100)
    res_null = la.consonant_permutation_test(rand_corpus, [1] * len(rand_corpus), roots, "A1", la.CLASSES_9, n_perm=300, seed=2)
    assert res_null["p_perm_type"] > 0.05, f"Random unexpectedly significant: {res_null}"
    print("PASS: test_planted_semitic_vs_random_permutation")


if __name__ == "__main__":
    test_projection_and_neutralization()
    test_regime_b_affix_stripping()
    test_planted_semitic_vs_random_permutation()
    print("ALL 3 LINEAR A UNIT TESTS PASSED!")
