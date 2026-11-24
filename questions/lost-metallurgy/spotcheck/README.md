# Spot check of `lost-metallurgy`

Done on 2026-11-24 by Claude Fable 5.2 (Anthropic) with Claude Opus 5.5 sub-agents, at Eugene's request. The study
was run by Antigravity (Google DeepMind). A spot check is not a replication. What it found is in `../RESULTS.md`
under "Spot check and corrections" and in `../amendments.md` (Amendment 2). Everything here beyond the rerun is
exploratory.

- `spot_check.py`, `out_spot_check.json`: the nine files re-read; baselines; the periods' medians; century-level
  tests; the isotope test.
- `rule_on_controls.py`, `out_rule_on_controls.txt`: the plan's anomaly rule (three times the baseline in two
  consecutive 25-year bins) applied to the Bronze Age, Iron Age, Roman, medieval and industrial periods.
- `sensitivity.py`, `out_sensitivity.json`: artificial pulses of 0.5 to 8 times the Roman excess, 100 to 3,000
  years long, added to the real RECAP record and run through the locked rule; samples per thousand years in each
  archive; the Füramoos enrichment on the plan's definition; the Laphroaig values; what the volcanic mask removes;
  the bound recomputed with 1.1 kt/a.

Papers read for the check: McConnell and others 2018 (*PNAS* 115:5726) and 2019; Longman and others 2018 (*PNAS*
115:E5661); Martínez Cortizas and others 2016 (*Sci. Total Environ.* 545–546:398); Radivojević and Rehren 2015
(*Cambridge Archaeol. J.*, abstract); Kern and others 2021 (abstract and data paper); Legrand and others 2025
(*PNAS Nexus*); Kylander and others 2020 (dataset record).
