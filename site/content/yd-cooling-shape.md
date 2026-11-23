---
# To update this page, edit this file and push to main; the site rebuilds itself.
# The figures are made by questions/yd-cooling-shape/analysis/make_figures.py from the results files.
summary: A core argument for a Younger Dryas comet impact is that the sudden freeze 12,800 years ago was too abrupt to happen naturally. How does its cooling shape actually compare with the 24 other abrupt coolings of the last 100,000 years?
verdict: Indistinguishable from natural coolings—in fact slower to start
result: Across 100,000 years of Greenland ice cores, the Younger Dryas meets 0 of 4 pre-registered criteria for a catastrophic-trigger signature. Its initial 60-year drop is among the slowest on record (rank 17 of 19 in δ¹⁸O, 22 of 25 in temperature, and 25 of 25 dead last in initial dust jump), its full cold amplitude is dead average (5.0 °C, rank 9 of 25), and Antarctica warms slightly (+0.04 °C across 7 cores) instead of cooling in an impact winter.
dek: Earlier lab tests looked at fire and biomass burning. Here we test the climate-transition shape itself across 100,000 years of Greenland and Antarctic ice, with every rule locked before looking at the Younger Dryas.
updated: 2026-11-23
---

> **Where things stand, 23 November 2026.** Initial locked run finished (by Antigravity / Google DeepMind, directed by Eugene; open to second-vendor review or replication). By the pre-registered decision rule, the Younger Dryas cooling is **Indistinguishable from natural coolings** (0 of 4 criteria met). Surprisingly, it did not drop faster than ordinary ice-age coolings—it started *more slowly* than almost all of them.

## What we figured out

One of the strongest intuitions behind the Younger Dryas impact hypothesis (YDIH) is that the sudden return to glacial cold 12,800 years ago looks too sharp and strange to be ordinary climate variability. Yet the last 100,000 years of Greenland ice hold two dozen other abrupt drops into cold stadials (`GS-2` through `GS-25`), none of which are blamed on comets.

We took the published list of every well-defined abrupt cooling onset from Rasmussen et al. (2014) and compared the Younger Dryas (`GS-1`, 12,896 yr b2k) against all of them across four pre-registered dimensions—abruptness, total amplitude & dust jump, pre-onset flatness ("out of the blue"), and Antarctic bipolar temperature response—with every formula locked before inspecting `GS-1`.

{{figure: yd-cooling-shape/ranks}}

Five things came out.

1. **The Younger Dryas started *more slowly* than almost every other abrupt ice-age cooling.** Over the first 60 years after onset, Greenland NGRIP `δ¹⁸O` drops by only `0.93 ‰`—ranking **17th of 19** (the third slowest drop in 60,000 years; the other 18 coolings drop a median `1.94 ‰`, more than twice as fast). In Kindler et al. (2014)'s 100,000-year reconstructed surface temperature, the first 60 years drop by `1.71 °C` (**rank 22 of 25**, versus `3.30 °C` median). All three Greenland cores (`NGRIP`, `GRIP`, `GISP2`) agree closely (`0.93–1.04 ‰`).
2. **Its initial 60-year dust jump is literally dead last out of 25 coolings.** During a typical ice-age cooling, Greenland `Ca²⁺` dust more than doubles (`×2.23`) in the first 60 years. At the Younger Dryas onset it barely budges (`×1.13`, **rank 25 of 25**).
3. **Once settled into cold, it is completely average.** Over `40–200` years after onset, the Younger Dryas reaches a total cooling of `5.01 °C` (**rank 9 of 25**, IQR `2.66–5.53 °C`), a dust jump of `×3.12` (**rank 10 of 25**, median `×2.87`), and a snow-accumulation drop of `×0.73` (**rank 10 of 25**). Eight ordinary glacial coolings cooled Greenland *more* than the Younger Dryas.
4. **Antarctica warms slightly instead of freezing.** Across Buizert et al. (2021)'s 7-core Antarctic temperature reconstruction (40,000 years, 10 stadials), Antarctica shows **`+0.042 °C` warming** in the 200 years after Younger Dryas onset (cool rank **8 of 10**; WAIS Divide ranks **10 of 10** at `+0.044 °C`). Five of the seven Antarctic cores are flat or warming—classic North-to-South AMOC bipolar seesaw, not a global impact winter.
5. **The pre-onset warming slope is not unique.** Because the late Allerød (`GI-1a`) was recovering from a brief prior dip (`GI-1b`), Greenland `δ¹⁸O` trends slightly upward (`+0.93 ‰/century`) in the 200 years before onset—ranking **5th of 19** (missing top 10%), behind four ordinary MIS 2–3 stadials (`GS-15.1`, `GS-17.2`, `GS-2.2`, `GS-2.1c`).

## The shape of the cooling, side by side

{{figure: yd-cooling-shape/profiles}}

Look at the shaded 60-year zone just to the right of the onset line in panels A and B. In an ordinary abrupt ice-age cooling (grey line and band), Greenland plunges rapidly into cold and dust doubles immediately. The Younger Dryas (copper line) lags behind the grey band during its first 60–80 years before settling cleanly into the middle of the distribution—the exact opposite of an instant cosmic-impact cliff.

## All 25 coolings over 100,000 years

{{figure: yd-cooling-shape/ladder}}

Sorting all 25 coolings by how steeply Greenland cooled in the first 60 years puts the Younger Dryas near the very bottom (22nd of 25), even though its full stadial amplitude on the right (9th of 25) is right in the upper middle of the ice-age range.

## What this does—and does not—settle

This test directly undercuts the argument that the Younger Dryas climate transition itself was physically too sharp, too large, or too globally synchronous to be a natural North Atlantic overturning slowdown. On its own, however, climate-transition shape does not evaluate terrestrial or ice-core geochemical impact markers (such as the GISP2 platinum spike—tested separately in Issue #76).

::: details Methods, data, and cross-checks
- **Protocol and lock:** `questions/yd-cooling-shape/protocol.md`, locked at `2026-11-23T17:16:23Z` (`protocol.lock`, SHA-256 `a1b8ae6f4aa5...`) before viewing `GS-1`. Zero amendments.
- **Public datasets:** NGRIP 20-yr `δ¹⁸O` (`gicc05-60ka-20yr.txt`), synchronized 3-core 20-yr `NGRIP/GRIP/GISP2` (`gicc05-calcium-20yr.txt`), Kindler et al. (2014) NGRIP 10–120 ka temperature (`ngrip2014temp.txt`), Erhardt et al. (2021) NGRIP 10-yr `Ca²⁺` (`PANGAEA.935814`), Buizert et al. (2021) 7-core Antarctic temperature (`buizert2021-temp.txt`), and Rasmussen et al. (2014) Table 2 event onsets (`events.tsv`). Full URLs and SHA-256 hashes in `questions/yd-cooling-shape/MANIFEST.md`.
- **Sensitivity checks:** Using an alternative 100-yr post-onset / 150-yr pre-onset baseline gives rank **17/19** (unchanged); peak single 20-yr cooling step gives rank **13/19** (`1.63 ‰` vs. `2.10 ‰` median).
- **Full report and code:** `questions/yd-cooling-shape/RESULTS.md`, `questions/yd-cooling-shape/analysis/shape.py`, and `questions/yd-cooling-shape/analysis/test_shape.py` (5/5 unit tests passing).
:::
