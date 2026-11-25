# Spot check of `khipu`

Done on 2026-11-24 by Claude Fable 5.2 (Anthropic) with a Claude Opus 5.5 sub-agent, at Eugene's request. The study
was run by Antigravity (Google DeepMind). A spot check is not a replication. What it found is in `../RESULTS.md`
and `../amendments.md`. Everything here beyond the rerun is exploratory.

- `khipu_lib.py`: a separate loader for `khipu.db` (opened read-only).
- `pair_dump.py`: the eight pairs' cords, values, colours and lengths side by side.
- `align_same_object.py`, `print_alignment.py`, `out_align_same_object.txt`: a local alignment that allows a
  missing cord, and the cord-length comparison used to tell one object recorded twice from two objects. The known
  duplicate KH0140/KH0483 and the Puruchuco copies are included for scale.
- `sensitivity.py`, `puruchuco_check.py`, `out_sensitivity.txt`, `out_puruchuco_check.txt`: the study's matcher on
  the documented duplicate and on the Puruchuco pairs.
- `null_scan.py`, `null_summary.py`, `out_null_summary.txt`: the study's within-khipu shuffle, and a relabelling
  that keeps zeros, repeats and digit counts, each run over every eligible pair 40 times.
- `santa_mc.py`, `out_santa_mc.txt`: the Santa Valley calculation with a free split and with a fixed one.
- `locke_mismatch.py`, `out_locke_mismatch.txt`: the cords on which the knot check disagrees with the database.

Read for the check: Urton, G. (2005), "Khipu Archives: Duplicate Accounts and Identity Labels in the Inka Knotted
String Records", *Latin American Antiquity* 16(2):147–167, doi:10.2307/30042809 (open copy in Harvard DASH); the
Khipu Field Guide (khipufieldguide.com) catalogue pages for the sixteen khipus and its notes on duplicates and on
Puruchuco; the OKR concordance file.
