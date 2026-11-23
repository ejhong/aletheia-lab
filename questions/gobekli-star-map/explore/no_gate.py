#!/usr/bin/env python3
"""EXPLORATORY, run after the locked result was known. Not evidence.

The locked analysis left out all three judges, because none passed the competence check (scorpion photograph at
mean rank 2.0 or better for the scorpion figure). This runs the same program with that one check switched off, to
describe what the judges did. Everything else is the locked program, unchanged.

    python explore/no_gate.py        # from questions/gobekli-star-map; writes explore/results/
"""
import pathlib
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "analysis"))
import analyse  # noqa: E402

shutil.copy(HERE.parent / "results" / "rankings.tsv", HERE / "results" / "rankings.tsv")
analyse.Q = HERE
analyse.COMPETENCE = 12.0          # the check can no longer fail
analyse.main()
