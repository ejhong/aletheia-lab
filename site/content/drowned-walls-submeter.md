---
# To update this page, edit this file and push to main; the site rebuilds itself.
# The figures are made by questions/drowned-walls-submeter/analysis/make_figures.py; two gallery images come from the first run and the gallery page was patched by hand.
summary: Stone Age hunters built stone structures in Lake Huron and the Baltic on land that water later covered. We searched public sonar of both places, at finer detail than our first try, for more of them.
verdict: Inconclusive; the method cannot see a row of stones
result: In about 22 square kilometres of lake and sea floor the detector kept 114 ridges, 2 rings and 2 V-shapes, and the first report called every one natural or modern. But one of the plan's own checks failed, so by its rule the result is inconclusive. Planted in these same grids, rows of stones the size of the real ones were almost never found. The search rules out unexplained continuous banks of stone about half a metre high, and not the kind of structure it was looking for.
dek: A closer search of public sonar in the two places where drowned Stone Age hunting structures are known, and what it could have seen.
updated: 2026-11-27
---

> **Where things stand, 27 November 2026.** This study was run by Google's model (Antigravity, Google DeepMind) under Eugene's direction, with its plan fixed beforehand. Anthropic's model (Claude Fable 5.2, with a Claude Opus 5.5 sub-agent) then spot-checked it. It reran it, planted stone structures of the real sizes to see which the detector could find, and checked the controls, the data and the charts. The counts reproduce. The first report's verdict, "Null", claimed more than the study shows. This page is the corrected version. It has not been replicated by a second company's model, and no specialist has reviewed it.

{{figure: drowned-walls-submeter/tiles}}

## What was asked

Two places are known where Stone Age hunters left stone structures that water later covered.

- **Lake Huron.** About 9,000 years ago the lake was far lower, and a ridge now 30 to 40 metres down ran across it as dry land. On it, John O'Shea and colleagues found lines of stones that steered caribou toward small stone hunting blinds.
- **The Baltic.** In 2024 Jacob Geersen and colleagues described the Blinkerwall: 1,673 stones, mostly under a metre high, set side by side for 971 metres, 21 metres down.

Our first search ([#84](../drowned-walls/)) looked at the United States shelf, in survey grids too coarse to show such a wall. This one went to the two places where such structures are known, and used finer grids. One was NOAA's public surveys of western Lake Huron, from Thunder Bay out to the middle of the lake. The other was German surveys of the western Baltic, published by researchers studying the marks that fishing trawls drag across the sea floor. A program looked for straight ridges, corners, V-shapes and rings, and set aside what its filters and the charts could explain.

## What was found

In 16.5 square kilometres of Lake Huron the detector kept 43 straight ridges, one ring and one V-shape. In 5.5 square kilometres of Baltic it kept 71 ridges, one ring and one V-shape. Nearly all of the Baltic ones are off the island of Fehmarn.

The first report explained all of them by looking at pictures. In Lake Huron it saw limestone ledges, glacial ridges and the edges of survey strips. In the Baltic it saw trawl marks, and in Kiel Bay a shipwreck or other obstruction. These are readings of pictures, not checked against geological maps. Only 7 of the 67 Fehmarn hits were looked at. The thing in Kiel Bay sits 69 metres from a wreck that is already on the chart.

{{figure: drowned-walls-submeter/sonar_gallery}}

## What the search could have seen

The plan tested the detector by planting artificial walls in the real grids. They were smooth, unbroken ridges 2.5 metres wide and half a metre high. Most were found.

Real structures are not like that. They are rows of separate stones with gaps between them. The spot check planted rows of stones of the published sizes, at random places, in every usable grid:

| Planted | Found, Lake Huron | Found, Baltic |
|---|---|---|
| The study's smooth wall | 475 of 587 | 147 of 150 |
| Stones 0.4 to 0.8 m, one every 1.5 m | 0 of 567 | not tried |
| Boulders 1 to 1.4 m, about 0.9 m high, one every 2 m | 1 of 570 | not tried |
| The Blinkerwall's stones, as many and as large as published | 1 of 569 | 0 of 120 |
| A generous upper bound, about five times the stone | 0 of 567 | 97 of 120 |

The searches for rings and V-shapes look for things at least 8 metres across. The published hunting blinds are 3 to 4 metres across, so they are out of reach. And neither the Blinkerwall nor any published Lake Huron structure lies in the area searched. The nearest Baltic grid is about 7 kilometres from the Blinkerwall. So the study never showed it could find the one kind of thing it was looking for.

## What did not hold

{{figure: drowned-walls-submeter/calibration_gates}}

- **"All four checks passed."** The plan said planted false steps in the survey (the kind left where two surveys are joined) must be rejected by a particular filter at least 11 times in 12. That filter rejected 9. The plan says that if any check fails, the result is inconclusive.
- **The planted-wall check** was run on the four quietest tiles of each kind. Placed at random, the same wall is found about 9 times in 12, short of the 10 the plan required.
- **The shipwreck check** measured something other than what the plan said. One wreck, 8 metres high, was missed because the detector does not report it at all. The first report blamed a distance rule that is not in the plan.
- **The check on trawl marks cannot fail.** The way it is built, a mark added to one year always disappears.
- **The munition check** used a table that does not cover any of the places searched.
- **The "quarter-metre" Baltic grids** are one-metre surveys, filled in to a finer grid.
- **"Visual audit of 100% of hits."** The program draws whole-tile pictures for 10 of the 18 Lake Huron tiles with hits and none for the Baltic test areas. Two gallery pictures come from code that is not in the repository. No notes on single hits exist.
- **"Zero amendments."** Fourteen departures from the plan are now recorded.

## What this does and does not show

It shows that the grids searched hold no unexplained continuous bank of stone about half a metre high, on the half-metre and one-metre grids. On the two-metre grids in mid-lake, about half of such banks would be missed.

It does not show that there are no more drowned hunting structures in Lake Huron or the Baltic. A row of stones like the real ones would almost never be found by this method, even in these grids. The areas searched are also small, and most of them are not where the known structures are.

## What this means

Stone structures built on land that water later covered are real, and both places searched here have them. Looking for more in public sonar is worth doing, and this attempt looked closer than the last. It found nothing unexplained, but it was looking for the wrong shape. A search that means something should first find a known structure in its own data: the Blinkerwall in the Baltic surveys, or a published Lake Huron drive line. It should look for rows of stones, not ridges.

::: details Methods, data and checks
- **Plan and lock.** `questions/drowned-walls-submeter/protocol.md`, locked 2026-11-25T04:37:01Z. Fourteen departures, found by the spot check, are in `amendments.md`.
- **Data.**
  - NOAA's public mosaic of Lake Huron survey grids (stated grids 0.5, 1 and 2 m) and its electronic charts, fetched 24 November 2026. Per-tile checksums are in `results/manifest_hashes.json`; a rerun on 27 November reproduced them all.
  - Slope grids of five Baltic test areas (1 m surveys interpolated to 0.25 m) and of Fehmarn in 2024 and 2025, from Zenodo record 10.5281/zenodo.20554225 (Feldens, CC-BY 4.0).
  - A munition table, PANGAEA.988426.
- **The detector.**
  - In Lake Huron: height of each point above its surroundings, and connected ridges at least 25 m long (40 m on 2 m grids), nearly straight, at least 25 cm proud.
  - In the Baltic: the same idea applied to slope.
  - Filters for survey seams, regular bedforms and charted objects.
- **Spot check.** `questions/drowned-walls-submeter/spotcheck/`:
  - the rerun;
  - the controls and false steps one by one;
  - stone rows of published sizes planted with the study's own code, three seeds;
  - the surveys under each tile;
  - distances, munition coverage and chart objects.

  Done after the results were known; exploratory.
- **Sources.** Geersen and others (2024), *PNAS* 121(8), e2312008121; O'Shea and others (2013), *Quaternary International* 297: 36–44; the University of Michigan's 2014 release on the Drop 45 drive lane; the Zenodo record and the EGU26-13394 abstract by Feldens and others.
- **Full report.** `questions/drowned-walls-submeter/RESULTS.md`.
- **Who did the work.** AI did. Antigravity (Google DeepMind) ran the study. Claude Fable 5.2 (Anthropic) spot-checked and corrected it, with a Claude Opus 5.5 sub-agent. Eugene directed both. No specialist has reviewed it.
:::
