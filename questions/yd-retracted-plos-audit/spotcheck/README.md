# Spot check of `yd-retracted-plos-audit`

Done on 2026-11-24 by Claude Fable 5.2 (Anthropic) with three Claude Opus 5.5 sub-agents, at Eugene's request. The
study was run by Antigravity (Google DeepMind). A spot check is not a replication: it reran the program, read the
hand-typed tables against their sources, and tested the main claims with separately written code.

What it found is in `../RESULTS.md` under "Spot check and corrections". The changes it led to are in
`../amendments.md` (Amendment 2) and the first run's outputs are kept in `../results/first_run/`.

## Contents

`radiocarbon/` — the Baffin Bay dates (Pillar 1).
- `mycal.py`: a calibration written for the spot check, not the study's.
- `table_s1_mine.csv`: SI Table S1 read from the image a second time; `compare_transcription.py` and
  `out_transcription.txt` compare it with the study's typed values (no mismatch in 27 rows).
- `recipe_grid.py`, `free_fit.py`, `core52_scan.py`: which curve and reservoir correction reproduce the printed
  ages. `out_all_dates_table.md` has all 27 dates under four recipes; `out_free_fit.txt` and `out_core52_scan.txt`
  scan every correction from −800 to +300 years on four curves.
- `scenarios.py`, `out_scenarios.txt`: the locked recalibration (S0 to S3) recomputed, and the bracket recommended
  by Heaton and others 2023 for polar seas.
- `out_inversions.txt`, `out_postlock_checks.txt`, `out_study_s0_offsets.txt`: the age reversals, the checks as
  locked against the checks as run, and the size of the shifts.

`baffin_grains_chemistry/` — Pillars 2 and 3.
- `check_s6.py`: SI Table S6 parsed again; coverage as span and as summed thickness; the Core 64 and Core 67
  comparison in both units; the Core 77 row.
- `check_s7.py`: the nanoparticle peaks on the locked intervals and the widened one, with what chance gives.
- `check_s8.py`: the 18 spherules, the "multiply by 100" step, the excess over crust on two backgrounds, the
  duplicated analysis.
- `check_d17o.py`: the ten oxygen-isotope values under the locked rule, and what 1% of meteoritic material would do.
- `measure_scale.py`, `measure_pores.py`: pore size in SI Fig S30 from its scale bar.
- `refs_extract.py`, `crossref_fetch.py`, `crossref_compare.py`, `doiorg_check.py`, `crossref_search.py`:
  every DOI in the reference list looked up on Crossref and doi.org on 2026-11-24. `doi_final_verdicts.csv` has
  the result for each of the 159. Outside the locked plan.

`shocked_quartz/` — Pillar 4.
- `transcription_check.py`, `out_transcription.txt`: SI Tables S2 to S8 against the typed values (no mismatch).
- `chi2_triples.py`, `out_chi2_triples.txt`: which three ages reproduce the paper's reported mean and χ².
- `t25.py`, `out_t25.txt`: the first run's list of 25 dates against Kennett and others 2008, Table 4, and the
  tests redone on the table's own rows.

The scripts were written to run from a scratch folder holding the study's `data/`, page images and extracted text;
paths inside them point there. The printed outputs are what the report relies on. Sources read but not stored here
(Pearce and others 2023, Heaton and others 2020 and 2023, Kennett and others 2008 and 2015, Waters and Stafford
2007, COPE's guidelines, PLOS's policy, Retraction Watch) are named in `../RESULTS.md`.
