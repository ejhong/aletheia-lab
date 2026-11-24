# Amendments — Do flood myths cluster where land drowned? (#44)

## Record added after the spot check — 2026-11-24

The first write-up said the locked plan was run with no amendments. A spot check on the same day (Claude Fable 5.2,
Anthropic, with Claude Opus 5.5 sub-agents) found five departures from the plan that had not been recorded. They are
recorded here after the fact. Nothing in the program or in `results/` was changed or rerun for this record; the
results are those of the first run.

1. **Sample.** The plan says 958 societies. The program drops 31 with a missing temperature value
   (`avtemp200_bere`), leaving 927. Of the 31, 29 are small islands of the Pacific and Indian Oceans (Tonga, the
   Marquesas, the Tuamotus, the Marshalls, Yap, Palau, the Marianas, Easter Island, the Maldives and others).
2. **Checks on the method.** The plan says the positive checks are run "on the same 958 societies". They were run on
   the 927 with a lighter model than the flood test (sampling controls, latitude and language-family fixed effects),
   not with the M4 controls.
3. **Block bootstrap.** The plan's 1,000 km spatial block bootstrap (§3.4, item 4) was not written.
4. **Permutation tests.** The plan asks for them on every model M1 to M4. They were run on coastal M3 and M4 only.
5. **Regions.** The plan asks for four macro-regions (Australia/Sahul and Oceania, Eurasia, the Americas, Africa).
   The program uses the dataset's six continents and a latitude and longitude box for "Australia/Sahul" that is
   mostly eastern Indonesia and New Guinea.

Also recorded:

- **The verdict rule.** The plan's Null verdict requires both positive checks to succeed (§4), and the second
  (sea motifs against nearness to the coast) was required to reach `p < 0.001` (§3.3). It reached `p = 0.073` with
  clustered standard errors and `p = 0.052` with spatial ones. None of the plan's three verdicts applies as written.
  `RESULTS.md` now reports the result as "no association found; the check on the method partly failed".
- **A fault in the plan itself.** §3.1 defines sea as any map cell below 0 m. That counts the Caspian Sea, the Great
  Lakes, Lake Baikal and dry basins below sea level as drowned shelf. The program follows the plan. The spot check
  refitted the main model with real sea only (`spotcheck/refit_sea.py`); this is labelled as done after the fact
  wherever it is reported.
- **The plan says 75 language families.** The data have 94 (58 among the coastal societies).
- **Analyses added by the spot check, outside the plan:** real-sea exposure; flood-centred motifs only; latitude
  limits; the earthquake check in the flood test's own sample and model; excluding only the Noah's Ark motif. All are
  in `spotcheck/` and all are exploratory.
