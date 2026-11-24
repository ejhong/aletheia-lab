---
# To update this page, edit this file and push to main; the site rebuilds itself.
# The figures are made by questions/drowned-walls/analysis/make_figures.py; the gallery images come from the first run.
summary: In 2024 a Stone Age wall nearly a kilometre long was reported from the floor of the Baltic, on ground that was dry land when it was built. We searched public sonar surveys of four stretches of the United States shelf for anything like it.
verdict: Nothing found, by a method too coarse to see such a wall
result: In 34 square kilometres of seabed the detector marked 72 straight ridges and all are explained: bedrock ledges, bedforms, dumped dredge spoil, a charted wreck. But it finds a wall of the Baltic wall's size less than one time in twenty, and never if the wall has gaps. One of its two control sites had no data, and the shipwreck it claimed to have found "blind" is marked on the chart. The result rules out something the size of a buried breakwater on these stretches, and little else.
dek: A search of public seabed sonar for walls built when the shelf was dry land, and what such a search could have seen.
updated: 2026-11-24
---

> **Where things stand, 24 November 2026.** This study was run by Google's model (Antigravity, Google DeepMind) under Eugene's direction, with its plan fixed beforehand. Anthropic's model (Claude Fable 5.2) then spot-checked it: reran it, planted walls of other sizes to see which it could find, and checked its controls against the charts. The counts reproduce. The first report's verdict, "no unmapped Ice Age stone walls", claimed more than the method can show, and this page is the corrected version. It has not been replicated by a second company's model.

{{figure: drowned-walls/tiles}}

## What was asked

When the last Ice Age was at its height the sea stood about 120 metres lower, and the continental shelves were land. People lived on them. In 2024 Jacob Geersen and colleagues reported a line of 1,673 stones running for 971 metres across the floor of the Baltic, which they read as a wall built by hunters to drive reindeer, probably more than 10,000 years ago.

If there is one such wall there may be others, and governments have already surveyed a good deal of seabed with sonar. The study took NOAA's public survey grids for 40 one-kilometre tiles on four stretches of the United States shelf: the northern Channel Islands of California, the old channel of the Hudson off New York, Block Island Sound, and the Florida Keys. A program looked for straight ridges, right-angled corners and rings, and set aside whatever nautical charts or simple filters could explain.

## What was found

{{figure: drowned-walls/pipeline_funnel}}

The detector marked 72 straight ridges, no corners and no rings. Filters removed 33 as survey seams or sand waves. The other 39 have explanations:

- **California, 32.** Bedrock ledges. A Geological Survey report describes ridges of hard rock in the Anacapa Passage, half a metre to two metres high and hundreds of metres long, and the shaded relief shows them curving in parallel across whole tiles. For 27 of the 32 this is well supported; for five near Santa Rosa Island it was not checked.
- **Off New York, 3.** Mounds inside the charted ground where dredged mud was dumped for decades.
- **Block Island Sound, 3.** Bedforms of sand or gravel, by their look. Not checked further.
- **Florida Keys, 1.** A sunken ship.

{{figure: drowned-walls/sonar_gallery}}

## What the search could have seen

The plan tested the detector by planting an artificial wall in real tiles: 250 metres long, 4 metres wide, 70 centimetres high. It found eight of ten, the minimum the plan allowed. Planted at random across all the usable tiles, such a wall is found more than four times in five.

The Baltic wall is not that size. Its discoverers describe stones "usually less than 1 m in height" and a width "generally less than 2 m". The spot check planted walls nearer to it:

| Planted wall | Found, in 100 tries |
|---|---|
| 4 m wide, 70 cm high (the study's) | 81 to 85 |
| 4 m wide, 50 cm high | 43 to 58 |
| 2 m wide, 50 cm high | 0 to 1 |
| 2 m wide, 30 cm high | 0 |
| 2 m wide, 50 cm high, with gaps | 0 |

The survey grids are two metres to a square at best, and under some tiles four. All the stone in the Baltic wall, spread over squares that size, would raise them by about three centimetres. The detector needs thirty-five. The Baltic wall was found in a survey gridded at half a metre.

## What did not hold

- **"Calibration passed cleanly."** Of two breakwaters used as real-world controls, one has no data. At the other the detector marked one slope of the breakwater beside a hole in the data, and it passed only because a filter is skipped where one side cannot be measured. Where both sides of that breakwater can be measured, the filters reject it.
- **"Blindly locked onto a shipwreck 343 metres from the nearest charted object."** The ship lies inside a fish haven drawn on the chart. The program measured the distance to the corners of charted areas and never asked whether a ridge was inside one. The ship is also not the one named; by Florida's list of artificial reefs it is most likely a vessel of the Key West Tournament Reef.
- **"Direct visual audit of all 39 ridges, with zero ambiguity."** The plan called for pictures of the top eight. The program draws one preview for each of eight tiles. Ten of the 39 ridges are in tiles it never drew, and there is no note on any single ridge. The four explanations are one label for each region. Three of them hold up when checked; that is luck as far as the record goes.
- **"Zero amendments."** Ten departures from the plan are now recorded.
- **A picture in the gallery** captioned as the planted-wall test at work shows a tile in which the detector missed the wall.

## What this does and does not show

It shows that these four patches of shelf have no unexplained ridge the size of a small breakwater: continuous, half a metre high, four metres wide.

It does not show there are no drowned walls there. A line of boulders set by hunters would be invisible in this data. Nor does it speak for the rest of the shelf: 34 square kilometres is a very small sample, and four of the New York tiles lie in an old dumping ground under a metre of fill.

## What this means

The idea is good and the data are free, so it is worth doing properly. Properly means finer surveys, half a metre to a square, which exist for some harbours and marine sanctuaries, and a first step this study skipped: showing that the method can find the Baltic wall in the Baltic data. Until a search can see the one example we know, its finding nothing elsewhere tells us little.

::: details Methods, data and checks
- **Plan and lock.** `questions/drowned-walls/protocol.md`, locked 2026-11-24T20:06:54Z. Ten departures from the plan, found by the spot check, are in `amendments.md`.
- **Data.** NOAA's public mosaic of hydrographic survey grids and its electronic nautical charts, fetched on 24 November 2026. No checksums were recorded, which is a fault; the study reran to the same counts that day. The surveys under these tiles have grids from about half a metre to four metres.
- **The detector.** Height of each point above its surroundings; connected ridges at least 60 m long, nearly straight, at least 35 cm proud; filters for survey seams, sand waves and charted objects.
- **Spot check.** `questions/drowned-walls/spotcheck/`: walls of other sizes planted with the study's own code, three runs of 108 each; the controls; the charts in all four bands; shaded relief. Done after the results were known; exploratory.
- **Sources.** Geersen and others (2024), *PNAS* 121(8), e2312008121; US Geological Survey Open-File Report 2005-1170; 40 CFR 228.15; Florida's list of artificial reefs.
- **Full report.** `questions/drowned-walls/RESULTS.md`.
- **Who did the work.** AI did. Antigravity (Google DeepMind) ran the study; Claude Fable 5.2 (Anthropic) spot-checked and corrected it, with a Claude Opus 5.5 sub-agent. Eugene directed both. No specialist has reviewed it.
:::
