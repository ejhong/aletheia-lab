# Spot check of `yd-megafauna-timing` (not part of the locked run)

These scripts back the numbers in a second-vendor spot check of this study, done by Claude (Anthropic, Opus 5.5) on 2026-11-24 at Eugene's request. They are exploratory checks written after the results were published, not evidence filed under the protocol. `output.txt` is what they printed.

- `recompute_pillar2.py`: recomputes M_yd, R_pre and the 10 late survivors from the raw spreadsheet with an independent reader and calibration. It also gives the excess as a number of dates and the survivors' ages as years after 12,850 and 12,750 BP. Last, it lists the Bonner Springs and Pyramid Lake rows as they appear in the spreadsheet.
- `null_shapes.py`: tests how much Younger Dryas mass an instant wipeout at 12,850 BP can leak under three population shapes: uniform, a copy of the observed pre-onset surge, and every true age in 12,850–13,000 BP.
- `pillar1_onset.py`: reruns RESULTS.md Table 1 against onset ages of 12,896, 12,846 (Rasmussen's 12,896 b2k, converted to BP) and 12,835 BP. It also runs the half-drop checks: how many cores fall more than 1,000 years before onset, and the tests without Tulare Lake.
- `common.py`: shared helpers (the .xlsx reader, IntCal20 loader and calibration).

Data: the first two scripts need `data/intcal20.14c` and `data/broughton2018_s1.xlsx` as listed in `../MANIFEST.md` (default `../data/`; another folder can be given as the first argument). `pillar1_onset.py` reads only `../results/sporormiella_sites.tsv`.
Run from the repo root: `python -I -B questions/yd-megafauna-timing/spotcheck/<script>.py [DATA_DIR]`. All results are deterministic.

Why the two scripts give slightly different M_yd values (4.92% and 4.95%): `recompute_pillar2.py` uses a 1-year grid and the full Gaussian likelihood. `null_shapes.py` uses the study's 5-year grid and leaves out the 1/sqrt(var) term, as the study's own code does.
