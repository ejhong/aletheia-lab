# Spot check of `ice-age-farming`

Done on 2026-11-24 by Claude Fable 5.2 (Anthropic) with a Claude Opus 5.5 sub-agent, at Eugene's request. The study
was run by Antigravity (Google DeepMind). A spot check is not a replication. What it found is in `../RESULTS.md`
and `../amendments.md`. Everything here beyond the rerun is exploratory. The scripts use the study's own parsing
and detector functions from `../analysis/run_ice_age_farming.py`, unchanged.

- `compare.py`: the rerun's results file against the committed one (identical except the cache digest).
- `stats_check.py`: the Fisher and rank-correlation tests recomputed.
- `sensitivity.py`, `sens_summary.py`, `out_sensitivity.json`: both detectors on a random sample of 60 European
  cores not chosen for having cereal pollen (seed 20261124), and on every Neotoma pollen core in the Fertile
  Crescent (29–42° N, 34–50° E) that reaches 9,000 BP, in the windows 11,500–9,000, 9,000–6,000 and 8,500–2,000 BP.
- `coverage.py`: cores reaching 12,000 BP by region and latitude band; datasets against sites.
- `sweep_audit.py`, `inspect_core.py`: the flagged cores sample by sample (Accesa, Van, Ghab, Braamhoek).
- `missing_ids.py`: cereal taxon identifiers the locked list leaves out.
