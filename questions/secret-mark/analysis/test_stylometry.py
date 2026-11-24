#!/usr/bin/env python3
"""Synthetic unit tests for #15 (Secret Mark) stylometry pipeline."""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from fetch_data import extract_greek_tokens, strip_diacritics_greek
from run_stylometry import (
    cosine_distance,
    general_imposters_scores,
    load_mar_saba_texts,
    monroe_log_odds,
    ngram_overlap_rates,
)


def test_greek_normalization():
    s = "Καλῶς ἐποίησας ἐπιστομίσας τὰς ἀῤῥήτους ὕψους!"
    assert strip_diacritics_greek(s) == "καλωσ εποιησασ επιστομισασ τασ αρρητουσ υψουσ!"
    toks = extract_greek_tokens(s)
    assert toks == ["καλωσ", "εποιησασ", "επιστομισασ", "τασ", "αρρητουσ", "υψουσ"]


def test_cosine_distance_properties():
    u = np.array([1.0, -2.0, 3.0])
    assert abs(cosine_distance(u, u)) < 1e-12
    assert abs(cosine_distance(u, -u) - 2.0) < 1e-12
    assert abs(cosine_distance(np.array([1.0, 0.0]), np.array([0.0, 1.0])) - 1.0) < 1e-12


def test_monroe_log_odds_polarity():
    c_t = Counter({"alpha": 80, "beta": 20, "common": 500})
    c_o = Counter({"alpha": 10, "beta": 90, "common": 500})
    lo = monroe_log_odds(c_t, c_o, alpha_0=50.0)
    assert lo["alpha"][0] > 0 and lo["alpha"][1] > 2.0
    assert lo["beta"][0] < 0 and lo["beta"][1] < -2.0
    assert abs(lo["common"][0]) < 1e-9


def test_general_imposters_identifies_planted_author():
    rng = np.random.default_rng(42)
    author_z = {
        "A": rng.normal(loc=2.0, scale=0.3, size=(20, 40)),
        "B": rng.normal(loc=-2.0, scale=0.3, size=(20, 40)),
        "C": rng.normal(loc=0.0, scale=0.3, size=(20, 40)),
    }
    target = rng.normal(loc=2.0, scale=0.3, size=40)
    scores = general_imposters_scores(target, author_z, n_iter=200, rng=rng)
    assert scores["A"] > 0.95


def test_ngram_cento_detection():
    ref = ["α", "β", "γ", "δ", "ε", "ζ", "η", "θ"]
    ref_bgs = {(ref[i], ref[i + 1]) for i in range(len(ref) - 1)}
    ref_tgs = {(ref[i], ref[i + 1], ref[i + 2]) for i in range(len(ref) - 2)}
    cento = ["α", "β", "γ", "δ", "ε", "ζ"]
    novel = ["κ", "λ", "μ", "ν", "ξ", "ο"]
    r_c = ngram_overlap_rates(cento, ref_bgs, ref_tgs, stopwords=set())
    r_n = ngram_overlap_rates(novel, ref_bgs, ref_tgs, stopwords=set())
    assert r_c["all_bigram_rate"] == 1.0 and r_c["all_trigram_rate"] == 1.0
    assert r_n["all_bigram_rate"] == 0.0 and r_n["all_trigram_rate"] == 0.0


def test_mar_saba_segmentation_integrity():
    ms = load_mar_saba_texts()
    assert len(ms["heading"]) == 9
    assert ms["clement_frame"][0] == "καλωσ"
    assert ms["secret_mark_bethany"][:4] == ["και", "ερχονται", "εισ", "βηθανιαν"]
    assert ms["secret_mark_jericho"][:4] == ["και", "ησαν", "εκει", "η"]
    assert len(ms["clement_frame"]) > 500
    assert len(ms["secret_mark_quotes"]) > 160


if __name__ == "__main__":
    for fn in [
        test_greek_normalization,
        test_cosine_distance_properties,
        test_monroe_log_odds_polarity,
        test_general_imposters_identifies_planted_author,
        test_ngram_cento_detection,
        test_mar_saba_segmentation_integrity,
    ]:
        fn()
        print("PASS:", fn.__name__)
    print("All 6 synthetic unit tests passed.")
