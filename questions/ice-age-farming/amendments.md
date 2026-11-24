# Amendments — Farming before the Ice Age ended (#88)

## Record added after the spot check — 2026-11-24

Nothing in the analysis or in `results/` was changed or rerun for this record. One line of the program was changed:
the `User-Agent` it sends to the Neotoma API no longer names the project.

1. **The verdict.** The plan (§4) says the outcome is "Inconclusive / Calibration failure" if `FARM_STRICT` detects
   fewer than 50% of known Neolithic European cores, and allows "Null" only if the calibration gate "succeeds
   decisively". `FARM_STRICT` detected 23 of 100. The first report gave the verdict "Null" with "zero amendments",
   citing the 59% of `FARM_RELAXED`, which the plan (§3.3) defines as a sensitive screen and not as the gate.
   `RESULTS.md` now reports the plan's verdict.
2. **The calibration cores** are the first 100 European datasets the API returns that have a cereal-type occurrence
   between 8,500 and 2,000 BP, so they are selected on already showing cereal pollen. The plan (§3.4) required
   cores spanning 11,000 to 3,000 BP; 50 of the 100 do.
3. **The weed list.** The plan (§3.2) names *Plantago lanceolata*, *Rumex acetosa/acetosella*, *Urtica*, *Centaurea
   cyanus*, *Polygonum aviculare* and *Cannabis/Humulus*. The program matches by substring and so also counts
   *Plantago major* and *media*, every *Rumex*, the family Urticaceae and Urticaceae/Moraceae. The plan's
   requirement that a strict sample contain *P. lanceolata* or *Rumex/Urtica/Centaurea* is not coded.
4. **The clearance baseline.** The plan says a fall of ten points from the "pre-event forest mean". The program
   takes one median per window from the 3,000 years before the window's older bound; for the 18,000 to 50,000 BP
   window that is 50,000 to 53,000 BP.
5. **The chronology check.** The plan requires radiometric, tephra or varve dates on both sides of a hit. The
   program accepts any control, including core tops and pollen-zone ties. Lake Van (dataset 45165) has no
   radiometric date and was reported as verified.
6. **The top 150.** The plan ranks cores "by count and geographic coverage"; the program ranks by count only.
7. **Pollen sums.** Samples given as percentages are accepted with a sum of 50 or more, not 100.
8. **Tests reported but not in the program:** the Fisher tests for the Mesolithic control, the correlations of
   onset with latitude and longitude (hard-coded in the figure program), the per-core audit and the maize audit.
9. **The data record.** `MANIFEST.md` gives no checksum for any file. The one digest in the results file changes
   from run to run while every number stays the same. The study reran to identical counts on 24 November 2026
   because the API returned the same records that day.
10. **Analyses added by the spot check, outside the plan:** recall on a random sample of European cores; every
    Neotoma core in the Fertile Crescent; rates among the cores examined; coverage by region. All are in
    `spotcheck/` and all are exploratory.
