# Spot check of `flood-myths`

Done on 2026-11-24 by Claude Fable 5.2 (Anthropic) with Claude Opus 5.5 sub-agents, at Eugene's request. The study
was run by Antigravity (Google DeepMind). A spot check is not a replication: it reran the program, refitted the main
model with separately written code, recomputed the exposure for a sample, and read the plan against the program and
the report. What it found is in `../RESULTS.md` under "Spot check and corrections" and in `../amendments.md`.

Every script takes the data folder, the study's results file and an output folder as arguments. Everything here that
is not a rerun of the locked analysis is exploratory.

- `compare_json2.py`, `out_compare_json2.txt`: the rerun against the committed results file.
- `outcome_check.py`, `out_outcome_check.txt`: the 17 motifs with their titles and descriptions from the motif
  master file. `outcome_prev.py`, `out_outcome_prev.txt`: how many societies have a flood motif under narrower lists.
- `indep_exposure.py`, `out_indep_exposure.txt`, `exposure_sample.csv`: drowned shelf area recomputed at one
  arc-minute for 38 societies.
- `indep_regression.py`, `out_indep_regression.txt`: the main model, the checks on the method and the sensitivity
  fits, written with statsmodels and a separate spatial standard error.
- `sea_1min.py`, `out_sea_1min.txt`: every connected body of water below 0 m labelled at one arc-minute; how much of
  each society's "drowned shelf" is the world ocean, the Black Sea, the Caspian, or lakes and basins.
- `refit_sea.py`, `out_refit_sea.txt`: the models refitted with real sea only.
