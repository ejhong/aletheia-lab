# Spot check of `drowned-walls`

Done on 2026-11-24 by Claude Fable 5.2 (Anthropic) with a Claude Opus 5.5 sub-agent, at Eugene's request. The study
was run by Antigravity (Google DeepMind). A spot check is not a replication. What it found is in `../RESULTS.md`
and `../amendments.md`. Everything here beyond the rerun is exploratory. The scripts use the study's own detector
from `../analysis/run_drowned_walls.py`.

- `diff_json.py`: the rerun's results file against the committed one (11 differences, none in the analysis).
- `sens_common.py`, `sens_replicate.py`, `sens_sweep.py`, `sens_extra.py`, `out_sensitivity_sweep.json`,
  `out_sensitivity_extra.json`: walls of different width, height, length and continuity planted at random places
  in all 27 usable tiles, three seeds, through the study's detector.
- `control_check.py`: the two breakwater controls; the profile across the Point Judith ridge.
- `enc_multiband.py`: each unmasked ridge against charted areas in all four chart bands, testing whether it lies
  inside one.
- `native_res.py`, `fine_patches.py`, `out_native_cell_estimates.json`: the true grid size of the surveys under
  each tile.
- `area_depth.py`: area and depth of the seabed examined.
- `hillshade.py`: shaded relief for the tiles in question.

Read for the check: Geersen and others (2024), *PNAS* 121(8), e2312008121; US Geological Survey Open-File Report
2005-1170 (Channel Islands habitats); 40 CFR 228.15 (the New York dumping ground); the Florida Fish and Wildlife
Conservation Commission's list of artificial reefs; NOAA's chart and survey services.
