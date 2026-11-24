# Spot check of `secret-mark`

Done on 2026-11-24 by Claude Fable 5.2 (Anthropic) with Claude Opus 5.5 sub-agents, at Eugene's request. The study
was run by Antigravity (Google DeepMind). A spot check is not a replication. What it found is in `../RESULTS.md`
under "Spot check and corrections" and in `../amendments.md`. Everything here beyond the rerun is exploratory.

- `compare_json.py`: the rerun's results file against the committed one (no difference at a relative tolerance of
  1e-12).
- `dump_layers.py`, `diff_khazarzar.py`: the study's Greek text, token by token, against Khazarzar's separate
  transcription.
- `cento_lib.py`, `cento_check.py`, `out_cento_check.json`: the phrase test written again from the SBLGNT files;
  the 62 passages; every one of the 11,106 overlapping windows; the 181 ways of placing the 62-passage grid.
- `cento_controls.py`, `out_cento_controls.json`: the same statistic for whole episodes of Mark (miracle stories
  and doublets among them), passages of Matthew and Luke that rewrite Mark, John 11, and Mark 16:9–20.
- `cento_extra.py`, `out_cento_extra.json`: what adding John, Matthew or Luke to the comparison does; how
  concentrated the matched phrases are in one place.
- `criddle_check.py`, `out_criddle_check.json`: the study's rare-word ratio, and the ratio in Criddle's direction,
  on forms and on a crude stand-in for dictionary words (first five letters).
