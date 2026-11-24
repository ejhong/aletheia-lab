# Amendments — `yd-retracted-plos-audit` (Issue #127)

None.

## Amendment 1 — 2026-11-24 (Pure Parser & Raster-Table Transcription Fixes; Zero Protocol Changes)

Upon executing the locked script (`0ebea37`) on the real Zenodo and PLOS One archives, five pure file-parsing issues surfaced because we remained strictly blinded to internal PDF/spreadsheet layouts before locking:

1. **Raster-image tables in both Supporting Information PDFs:** Both `baffin_bay_si.pdf` (`SI Table S1`, p. 5, `27` raw marine `¹⁴C` dates) and `kennett2025_si.pdf` (`SI Tables S1–S8`, pp. 2–5, radiocarbon dates & vertical shocked-quartz counts) embed their tables as **raster screenshot images** (`baffin_p5_img1.jpg`, `quartz_p2_img1..4`, `quartz_p3..p5_img*.png`) rather than selectable PDF text. We extracted every table image (`results/extracted_table_images/`) and transcribed all rows verbatim into structured dictionaries in `analysis/audit_plos_retractions.py`, cross-checked cell-for-cell against the images.
2. **`SI Table S6` (`baffin_bay_si.pdf`, p. 16) regex:** Sample rows begin directly with core numbers (`83023-052`, `2013029-064`, `2008029-067`, `2013029-077`) or a leading footnote marker (`a83023-052`, `a2013029-064`, etc.) rather than the word `"Core"`. Updated the line parser to parse all 28 rows cleanly, preserving both `Spherules/kg` and `CDPs/kg`.
3. **`SI Figs S30–S34` (`baffin_bay_si.pdf`, pp. 32–35) EDS spectra:** Elemental mass% readouts (`Ca`, `C`, `O`, `Si`, `Al`, `Mg`, `Na`) are rendered inside the embedded SEM-EDS `.jpg` images (`results/si_figs_s30_s34/p32_img1.jpg` through `p35_img1.jpg`) rather than PDF caption text. Transcribed the exact instrument-printed EDS mass% tables from `SI Figs S30, S31, S33, S34` verbatim alongside automated caption extraction.
4. **`Table S7` (`Mass Concentration` block, row 57) duplicate `'Pt'` column header:** The rightmost ratio headers (`Pt/Ir`, `Pt/Pd`, `Pt/Fe`) were truncated to `'Pt'` in row 57, overwriting the elemental `'Pt'` mass-concentration column. Fixed `header_map` to keep the first occurrence (`setdefault`) for elemental columns and index ratios explicitly by position.
5. **`Appendix Table A1` (`moore2025_baffin_bay.xml`) column index:** Rows have 7 cells (`sample, δ¹⁷O, 1SD, δ¹⁸O, 1SD, Δ¹⁷O*, 1SD`), so `Δ¹⁷O*` is `cells[-2]` rather than `cells[-1]` (`1SD`). Also evaluate `Δ¹⁷O*` both raw and relative to each core's own background mean (since terrestrial clay/quartz sediments sit at `−0.05 to −0.11‰`, and `Core 64/67` YDB values are less negative than background).

**No pre-registered question, target window, `ΔR` scenario, threshold, or verdict rule in `protocol.md` was changed.**

## Amendment 2 — 2026-11-24 (after a spot check; written before the changed parts were rerun)

A spot check by Claude Fable 5.2 (Anthropic), with Claude Opus 5.5 sub-agents, found faults in the first run. They
are recorded here before anything is rerun. The first run's outputs are kept in `results/first_run/`. The protocol,
its thresholds and its verdict rules are unchanged. The spot check had already computed most of the corrected
numbers when this was written, so nothing below is blind; where a choice had to be made, the literal reading of the
protocol is taken and the alternatives are reported beside it.

1. **The list of "published direct YDB-stratum dates" (Pillar 4, check B1) was wrong.** It was typed in by hand
   before the lock and described as "verified in Issue #113". It was not. All eleven Arlington Canyon entries
   disagree with the table they cite (Kennett et al. 2008, Table 4): four laboratory numbers are not in that table
   (UCIAMS-36309, -42817, -42818, -42819), the others carry another sample's age, and the depths and materials are
   wrong. The two dates the paper's own SI lists (Beta-161032 and UCIAMS-36304) were missing from it. At Murray
   Springs the laboratory numbers "A-805A" to "A-805F" could not be found in any source, and Tx-1413 is
   11,080 ± 180 in the primary list (Valastro et al. 1975), not 10,760 ± 100. **Change:** the Arlington Canyon
   list is replaced by the twelve rows of Kennett et al. 2008 Table 4 between 392 and 503 cm, the interval
   Kennett et al. 2015 model as the boundary section, typed from the table with its old-wood flags. The per-date
   lists for Murray Springs and Blackwater Draw are removed: they could not be verified, and they date Clovis
   camps, not the sampled layer. Those two sites enter only through the pooled values in Waters and Stafford 2007,
   Table 1, in a three-site comparison reported as context. B1 is evaluated on the twelve Arlington Canyon dates,
   the literal reading of "all published direct YDB-stratum dates"; the same test on the dates the source does not
   flag as old wood is reported beside it. The first run's T = 90.94 and "25 of 25 omitted" are withdrawn.
2. **The ages in the paper's own χ² test were misidentified.** The first run assumed the test used three single
   calibrated dates from SI Tables S2 to S4. The paper's reported mean (12,801.6) and χ² (0.057) are reproduced
   exactly by the three Bayesian-modelled ages it quotes from Kennett et al. 2015 (12,805 ± 55, 12,775 ± 365,
   12,750 ± 235), and not by the first run's three. **Change:** the program reproduces the test with the modelled
   ages. The first run's comparisons are kept, labelled as tests of our own making.
3. **Check B2 as coded differed from B2 as written, and the code changed after the lock without a record.** The
   locked program tested for the absence of the words "sedimentation rate"; the first run added "or any site with
   no sample below the boundary". **Change:** B2's sampling half is evaluated as the protocol words it: grain
   counts for the control samples are missing, or fewer than three control samples at a site. The word search and
   the count of sites with nothing sampled below are still reported.
4. **The nanoparticle test (Pillar 2.3) used 10 of the 12 locked measures and, for Core 67, a window 2 cm wider
   on each side than the locked interval.** Neither was recorded. **Change:** all 12 measures, on the locked
   intervals (Core 64: 312 to 318 cm; Core 67: 32 to 35 cm), with the number of sampled depths inside and outside
   so the result can be set against chance. The widened window is reported as a secondary result.
5. **Amendment 1, item 5, changed the oxygen-isotope test while describing itself as a parser fix.** The locked
   rule is |Δ¹⁷O*| > 0.06‰; the first run counted only boundary samples further from zero than their core's
   background. **Change:** the locked rule is applied. The other is reported as secondary.
6. **Check A2 is a reading of five figures by eye, not a computation;** the program records the reading. It stays
   that way and is described as such.
7. **Core coverage (check A3)** was the span between the shallowest and deepest samples. The summed thickness of
   the samples themselves is now reported beside it.

Verdict rules are applied to the rerun exactly as locked.

## Record added with the rerun — 2026-11-24

Amendment 2 was applied and the program rerun on 2026-11-24. No check changed its outcome and neither label
changed. Three further departures of the first run from the plan came to light after Amendment 2 was written. They
change nothing that was rerun and are recorded here so the list is complete.

- The finding that the printed ages match the stated method with the sign of the reservoir correction reversed
  (and, in Core 52, the land curve) was made after the lock by a search that is in no committed program. It is not
  part of the locked plan. A separate program in `spotcheck/radiocarbon/` reproduces it.
- The first run added a fifth calibration scenario using the errors printed in SI Table S1, and a detector of age
  reversals with depth. Neither is in the protocol. Both are kept and reported as additions.
- The Core 64 and Core 67 comparison in check A3 was made in metallic dust particles per kilogram. In spherules
  per kilogram the ratio is 0.31 and that branch fails. The protocol's wording ("microspherule/MDP peak") allows
  either, and the other branch of A3 (under 20% sampled) holds regardless.

