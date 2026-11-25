# Results — Unmapped stone structures in public Ice Age seafloor sonar (#84)

- **Question:** #84, `lane:data`.
- **Plan locked:** 2026-11-24T20:06:54Z (`protocol.lock`, commit `d85358f`), before the results were committed. Unchanged since.
- **Who did the work:** AI did. Antigravity (Google DeepMind) designed and ran the study on 24 November 2026. Claude Fable 5.2 (Anthropic), with a Claude Opus 5.5 sub-agent, spot-checked it the same day and wrote this corrected report. Eugene Jhong directed both. No specialist has reviewed it, and it has not been replicated by a second company's model.
- **Departures from the plan:** recorded in `amendments.md`. The first report said there were none.
- **Spending:** nothing was paid for.

## Answer

**Nothing unexplained was found in 34 square kilometres of seabed. But the detector would almost certainly miss a wall like the one real example it was modelled on, so the result says little about such walls.**

In 2024 a stone wall nearly a kilometre long was reported from the floor of the Baltic, built by hunters, probably more than 10,000 years ago, when the place was dry land (the Blinkerwall; Geersen and others). The study asked whether public sonar surveys of the United States shelf show anything similar. It took 40 tiles of NOAA seabed grids on four stretches of shelf that were dry in the Ice Age, ran a detector for straight ridges, corners and rings, and removed what filters and nautical charts could explain.

- **What was found.** 72 straight ridges, no corners, no rings. Filters removed 33. The other 39 are explained: bedrock ledges off California, bedforms in Block Island Sound, dumped dredge spoil off New York, a sunken ship off Key West. The program reruns to the same counts.
- **What the detector can see.** Continuous ridges at least half a metre high and about four metres wide. For the wall the study planted to test itself (4 m wide, 0.7 m high, 250 m long) it finds 81% to 85%.
- **What it cannot see.** The Blinkerwall is, in its discoverers' words, "generally less than 2 m" wide, of stones "usually less than 1 m in height", 1,673 of them along 971 m. Planted at 2 m wide and 0.5 m high, a wall is found between 0 and 5 times in a hundred. Planted with gaps between stretches of stone, it is never found. The real wall's stone, spread over the 2 m squares of these grids, would raise them by about 3 cm; the detector's threshold is 35 cm. The Blinkerwall itself was found in data gridded at half a metre.
- **The checks on the method were weaker than reported.** One of the two breakwaters used as controls has no data at all. At the other, what was "recovered" is one slope of the breakwater beside a hole in the data, and it passed only because a filter is skipped where one side cannot be measured. The planted-wall test scored exactly the minimum the plan allowed.
- **The "blind" find was on the chart.** The first report said the detector "blindly locked onto" a shipwreck 343 m from the nearest charted object. The ship lies inside a fish haven marked on the chart. The program compared ridges with the corners of charted areas and never asked whether a ridge lies inside one. The ship was also misidentified.
- **The "visual audit of all 39 ridges" left no record.** The plan called for images of the top eight. The program draws one preview for each of eight tiles and nothing closer. Ten of the 39 ridges are in tiles it never drew. The four explanations are one label per region.

What the data support: on these four stretches of shelf there are no unexplained continuous ridges half a metre high and four metres wide. That would rule out something like a buried breakwater. It does not bear on a line of boulders set by hunters.

## What the spot check confirmed about the explanations

| Region | Ridges | First report | What supports it |
|---|---:|---|---|
| California, Anacapa Passage | 27 | Dipping Monterey Formation bedrock | A US Geological Survey report (Open-File 2005-1170) says Monterey rocks "probably underlie" the passage and form "raised resistant ridges", "0.5-2 meters high and 3-5 meters wide that are up to several hundred meters long". The shaded relief shows parallel curving ledges. Plausible |
| California, Santa Rosa Island | 5 | The same | Nothing found. Unverified |
| Block Island Sound | 3 | Tidal sandbars | Shaded relief shows natural-looking bedforms. Not checked against a sediment map. Unverified |
| Off New York | 3 | Dredge-spoil mounds | All three lie inside the charted spoil ground of the former Mud Dump Site (40 CFR 228.15). Confirmed |
| Off Key West | 1 | A wreck, "the Cayman Salvage Master" | A ship about 60 m long, inside a charted fish haven. By Florida's list of artificial reefs it is about 40 m from the Key West Tournament Reef (a 260-foot ship at 180 feet) and about 480 m from the *Cayman Salvage Master*, which lies far shallower. Not that ship |

## The locked run

| Check (plan §3) | Required | Result | As it stands after the spot check |
|---|---|---|---|
| Two real breakwaters | at least 1 of 2 | 1 of 2 | One has no data. The other was passed by a skipped filter; where both sides of that breakwater can be measured, the filters reject it |
| Planted walls, 250 × 4 × 0.7 m, in 10 real tiles | at least 8 | 8 | The same two tiles fail whatever the seed. At random places in all 27 usable tiles: 81% to 85% |
| Planted false steps | 10 of 10 rejected | 10 of 10 | Holds |

| Region | Tiles | Seabed with data (km²) | Ridges | Removed by filters | Left |
|---|---:|---:|---:|---:|---:|
| California, northern Channel Islands | 12 | 11.39 | 63 | 31 | 32 |
| Off New York (Hudson channel) | 10 | 10.39 | 3 | 0 | 3 |
| Block Island Sound | 10 | 6.27 | 4 | 1 | 3 |
| Florida Keys | 8 | 6.18 | 2 | 1 | 1 |
| Total | 40 | 34.23 | 72 | 33 | 39 |

The first report gave the filters' work as 25, 15, 4 and 1, which add to 45. Those count flags, and a ridge can carry more than one. The chart filter removed no ridge that another filter had not already removed. Applied as the plan words it, it would also have removed the ship, leaving 38.

### How often planted walls are found (spot check, after the fact)

27 tiles, four random places and directions each, 108 trials for each of three seeds.

| Planted wall | Found, of 108 |
|---|---|
| The study's: 4 m wide, 0.70 m high, 250 m long | 92, 87, 88 |
| 4 m wide, 0.50 m high | 63, 46, 53 |
| 4 m wide, 0.40 m high | 3, 2, 2 |
| 2 m wide, 0.50 m high | 1, 0, 1 |
| 2 m wide, 0.50 m high, 971 m long | 1, 0, 1 |
| 2 m wide, 0.30 m high | 0, 0, 0 |
| 1 m wide, 0.50 m high | 0, 0, 0 |
| 2 m wide, 0.50 m high, in 10 m stretches with 5 m gaps | 0, 0, 0 |
| The study's wall, in 10 m stretches with 5 m gaps | 0, 0, 0 |

## Spot check and corrections

A spot check is not a replication. It reran the program against NOAA's services, planted walls of other sizes with the study's own code, checked the controls and the charts, drew shaded relief for the tiles in question, and read the Blinkerwall paper.

What holds: the lock; every count, on a rerun; the area (34.2 km²); the depths (97% of the seabed examined lies between 10 and 80 m down); the unit tests.

What does not:

1. **Sensitivity,** above. The plan's own stand-in for the Blinkerwall was about 55 times its cross-section. The manifest misdescribed the real wall as 2 to 3 m wide and 0.5 to 1 m high.
2. **The controls,** above. "Calibration gate passed cleanly" is withdrawn. The plan allows a null only if the gate passes "decisively".
3. **The ship,** above.
4. **The audit,** above. It was a judgement by a language model that left no images of single ridges and no notes. One picture in the published gallery, of the New York tile, is made by no committed program; another, captioned as showing the planted-wall test working, shows a tile where the detector missed the wall.
5. **"2 m per pixel."** The service stitches together surveys of different fineness. Under these tiles the true grid runs from about half a metre to about four. Three California tiles are 4 m data shown at 2 m.
6. **Ten departures from the plan** (`amendments.md`), among them: all 39 ridges "audited" where the plan said eight; the chart filter measuring distance to corners; errors from the chart service silently treated as "nothing charted".
7. **Where it looked.** Four of the ten New York tiles lie inside the old dumping ground, under a metre or more of capping material. Five of the 40 tiles have almost no data.
8. **Unsourced statements.** "About 20 million km² of shelf exposed at the glacial maximum" has no source here. The statement that the Blinkerwall survived because of "minimal wave erosion and sediment burial" contradicts the paper, which says the wall probably lay "in the swash zone for decades" and that sediment has "already blanketed similar-sized structures" elsewhere in the Baltic.
9. **No checksums** in the manifest for any downloaded tile. The program also named the project in the `User-Agent` it sent to NOAA; that line has been changed.
10. **Wording:** "remarkably sensitive", "verified sensitivity", "blindly locked onto", "zero ambiguity", "resolves unambiguously in seconds". Withdrawn.

## Limits

1. **Too coarse for the target.** The main limit.
2. **34 km²** on four stretches of one country's shelf.
3. **Burial.** Sand and mud cover low features on open shelves; sonar of the surface does not see through them.
4. **The explanations** for 8 of the 39 ridges are unverified.
5. **A dashed line** about 600 m long in one Block Island tile is on no chart and was not picked up by the detector. It may be a survey artefact or a cable trench. It is the kind of thing this method cannot assess.
6. **No replication** by a second company's model.

## What this means

People did build in places the sea later covered: the wall in the Baltic is real. Looking for more of the same in sonar data that is already public is a reasonable thing to try. This attempt found nothing, and the reason to hold the result lightly is simple. The data are too coarse and the detector too blunt for a wall a stone or two wide. It can find a breakwater. The one known Stone Age wall of this kind would have left about three centimetres of relief in grids like these. A real search needs the half-metre surveys that exist for some harbours and sanctuaries, and it should start by showing that the Baltic wall itself can be found in its own data.
