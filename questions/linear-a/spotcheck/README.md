# Spot check of `linear-a`

Done on 2026-11-24 by Claude Fable 5.2 (Anthropic) with a Claude Opus 5.5 sub-agent, at Eugene's request. The study
was run by Antigravity (Google DeepMind). A spot check is not a replication. What it found is in `../RESULTS.md`
and `../amendments.md`. Everything here beyond the rerun is exploratory. The scripts import the study's own
functions from `../analysis/run_linear_a.py`.

- `sensitivity.py`, `out_sensitivity.json`: Amarna Canaanite, Hebrew, Akkadian and Proto-Semitic stems through the
  study's length-matched comparison with Linear B; the smallest detectable difference; the novel-sign shuffle run on
  words spelled with the proposal's own values; the shuffle restricted to the 22 signs that are new; the
  seven-class row; the length mix.
- `lexicon_audit.py`, `lexicon_classify.py`, `out_lexicon_classify.txt`, `lexicon_audit_sample.tsv`: the 325
  lexicon entries against their cited roots, with each mismatch sorted by cause.
- `controls.py`, `lb_sites.py`, `out_controls.txt`, `out_lb_sites.txt`: where the Linear B words come from; what the
  "held-out" words are; roots per skeleton.
- `sign_table.py`, `out_sign_table.txt`: the 86 sign values and which are new.

The proposal's own account of its evidence was read in the pinned copy of `plasma-ai/kaphtor`: `README.md`,
`docs/shoresh-preregistration.md`, `docs/confidence.md`, `models/language-id-kernel/README.md`. None of its
programs was run.
