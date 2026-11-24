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
