# Results — Stone walls in finer public sonar: Lake Huron and the western Baltic (#143)

- **Question:** #143, `lane:data`, a follow-up to #84 (`drowned-walls`).
- **Plan locked:** 2026-11-25T04:37:01Z (`protocol.lock`, commit `00b7b80`). The results were committed 15 minutes later (`7814b5d`). The plan has not changed since.
- **Who did the work:** AI did. Antigravity (Google DeepMind) designed and ran the study on 24 November 2026. Claude Fable 5.2 (Anthropic), with a Claude Opus 5.5 sub-agent, spot-checked it and wrote this corrected report on 27 November 2026. Eugene Jhong directed both. No specialist has reviewed it, and no second company's model has replicated it.
- **Departures from the plan:** recorded in `amendments.md`. The first report said there were none.
- **Spending:** nothing was paid for.

## Answer

**By the plan's own rule the verdict is "Inconclusive". What the study does show is narrower: these grids hold no unexplained continuous ridge about half a metre high. The method cannot see a line of separate stones, which is what every real structure of this kind is.**

There are two places where Stone Age hunters' stone structures are known under water:

- **Lake Huron.** Caribou drive lines and hunting blinds on the Alpena–Amberley Ridge (O'Shea and colleagues).
- **The western Baltic.** The Blinkerwall (Geersen and others, 2024).

The study searched public sonar grids in both basins: 16.5 km² of NOAA grids in western Lake Huron and 5.5 km² of German slope grids in the Baltic. A program looked for straight ridges, corners and rings. It set aside whatever its filters and the nautical charts could explain. The first report's reading of the pictures explained everything else.

- **What was found.** In Lake Huron: 43 straight ridges, 1 ring and 1 V-shape that the filters kept. In the Baltic: 71 ridges, 1 ring and 1 V-shape. The first report calls all of them natural or modern. The program reruns to the same counts.
- **The plan's checks on the method.** One of the four fails as the plan words it. The plan says planted false steps must be rejected "via `SEAM_STEP`" at least 11 times in 12. That filter rejected 9. Of the other three, two were never detected at all and one passed as a "wall". The plan says that if any check fails, the result is "Inconclusive".
- **What the detector can see.** It sees continuous ridges about half a metre high on grids of half a metre or one metre. On the two-metre grids of mid-lake Huron it finds only half of the plan's own planted wall.
- **What it cannot see.** It cannot see lines of separate stones of the published sizes, at any resolution, in either basin. The searches for rings and V-shapes cannot report anything as small as the published hunting blinds (3–4 m across).
- **No real example is in the data.** Neither the Blinkerwall nor any published Lake Huron feature lies in the area searched. So the study never showed that it can find the thing it is looking for.
- **The "visual audit of 100% of hits" left no record.** The committed program draws 10 of the 18 Lake Huron tiles with hits and no Baltic test-area hit at all. Two pictures in the published gallery come from code not in the repository. Of 67 Fehmarn hits called trawl scars, 7 were looked at.
- **The Baltic "0.25 m" grids are 1 m surveys interpolated to 0.25 m,** as the dataset's own record says.

## What holds

- **The lock.** `protocol.md` hashes to the value in `protocol.lock`. Nothing touched it after the lock.
- **The rerun.** The committed program, unmodified, run on the public data on 27 November 2026, gives every count in `results/scan_summary.json`. The only difference is the run time (`spotcheck/out_diff_scan_summary.txt`). All 87 NOAA tiles, the chart file, both Zenodo archives and the PANGAEA table hash identically to `results/manifest_hashes.json` (`spotcheck/out_diff_manifest_hashes.txt`). The four unit tests pass.
- **The counts and areas,** as tabled below: 16.485 km² in Lake Huron, 5.491 km² in the Baltic.
- **Coverage, stated fairly.** The first report says that O'Shea's sites lie outside NOAA's public mosaic. It also says that trawl marks off Fehmarn last longer than a year, so comparing two years does not clear them.

## What the spot check found

In order of seriousness. Line numbers refer to `analysis/run_submeter_scan.py`.

1. **The detector cannot see the real structures.**
   - **The planted walls.** The plan's walls are continuous smooth ridges: 60 m × 2.5 m × 0.5 m (120 × 4 × 0.55 m on two-metre grids). In the Baltic the planted wall is a bump added to the slope grid, with no height.
   - **The Blinkerwall** is "1,673 individual stones which are usually less than 1 m in height, placed side by side over a distance of 971 m". Its width is "generally less than 2 m", and its stones total 52.75 m³ (Geersen and others, 2024).
   - **The Lake Huron features** (O'Shea and others, 2013):
     - a drive line of "small rocks and boulders forming a line of 365 m";
     - the Dragon Blind, whose boulders are "1 to 1.4 m in length" and stand "about 90 cm high";
     - V-shaped blinds whose apex stones are "60–110 cm in height", with a core "three to 4 m" wide.

   The spot check planted structures of these sizes at random places in every usable tile and ran the study's own detector (table below). No line of stones was found more than once in about 120 to 230 tries, in either basin. The only exception is a Baltic upper bound with about five times the published stone volume per metre.

2. **One of the plan's four checks fails as worded** (above). The program counts a seam as rejected whenever no unmasked ridge lies near it (l.1119–1128), whether or not the filter fired (`spotcheck/out_controls_seams.json`).

3. **The planted-wall check passed on the quietest tiles.**
   - **How the hosts were chosen.** For each grid size the program picks the four tiles with the fewest natural detections (l.1091–1093) and plants at a fixed spot (l.557–565).
   - **At random places in all usable tiles,** the same wall is found 89%, 89% and 50% of the time on the half-metre, one-metre and two-metre grids (`spotcheck/out_sens_huron.json`). With four tiles of each, as in the check, that is about 9 of 12, short of the 10 required.

4. **No true positive control.**
   - **The Blinkerwall.** Test2 is the nearest Baltic grid. Its nearest corner is 7.1 km from the sediment core the discoverers took beside the wall (54.1609° N, 11.4728° E; `spotcheck/out_baltic_geo.json`). The plan's "about 3–5 km" and the first report's "about 4 km" are not supported.
   - **Drop 45.** It is reported to lie about 35 miles south-east of Alpena, south of the mid-lake tiles. Its coordinates are not published.

5. **The shipwreck check is not the one in the plan, and the first report gave the wrong reason for its one failure.**
   - **What the program measures** (l.1030–1046). It takes the highest point in a 140 m square at the tile centre, which is not a detection, and the 70 m half-width is not in the plan. It then measures the distance from the tile centre to the charted wreck. The tiles were centred on the charted wrecks, so that test cannot fail.
   - **Applied as written, the check still passes, 2 of 3.**
   - **The failure at F00862.** The wreck stands 8.1 m high, 93 m from the chart position, but the detector produced no candidate for it. The first report blamed a "pre-registered 70 m center gate radius".
   - **Set after the fact.** The heights of all three wrecks were measured in exploration before the plan was locked (`explore/README.md`). The 0.80 m threshold was set knowing they cleared it.

6. **The visual audit.**
   - **Lake Huron.** The program draws a whole-tile preview for 10 of the 18 tiles with hits (l.1071–1085). The other 8 hold 10 of the 43 ridges.
   - **The Baltic.** It draws the 12 highest-scoring Baltic hits, all off Fehmarn, so no Kiel Bay or Mecklenburg Bay hit is drawn. The gallery's Kiel Bay picture and its planted-wall picture are made by no committed code.
   - **What the plan required.** Pictures of the top 10 Baltic hits. The first report describes six of them. It labels all 67 Fehmarn hits after looking at 7.
   - **No record.** No picture of a single hit and no note giving reasons is committed.
   - **The geological labels.** "Devonian limestone", "Traverse Group", "karst", "Six Fathom Scarp" and "otter-board trawl scars" are the first report's reading of a picture. They were not checked against any map or source.

7. **The Baltic resolution.** The Zenodo record says the data "were collected … at 1 m resolution (interpolated to 0.25 m)". The Fehmarn grids of 2024 and 2025 are 8-bit grey pictures of slope with no physical scale. The thresholds and planted walls there are in grey levels.

8. **The munition filter could not fire.**
   - **What the table covers.** The PANGAEA munition table covers 54.03–54.50° N and 10.28–11.00° E.
   - **Where the study looked.** No Baltic area searched lies inside that box. The nearest pile is 8.9 km from Test4 and 24 to 191 km from the others (`spotcheck/out_baltic_geo.json`).
   - **Consequence.** "No munition flag" is not a test.

9. **The trawl-scar check cannot fail.** A scar is added to the 2024 grid only, and the program then takes the smaller of the two years (l.1340–1341). The scar can never show unless 2025 already has a ridge in the same place, so "10 of 10 rejected" tests nothing.

10. **The Kiel Bay "modern small shipwreck" is charted.**
    - **What the charts show.** OpenStreetMap's seamark data, imported from nautical charts, show a submerged wreck ("distributed remains") 69 m from the hit and a foul-ground obstruction 59 m from it (`spotcheck/out_osm_kielbay_near.txt`). An official German chart was not consulted.
    - **What the first report did.** It checked no chart. Its description of a "16 m × 5 m hull" and a "comet-mark wake" is a reading of a picture made by uncommitted code.

11. **The Lake Huron grid sizes.**
    - **Resampled surveys.** NOAA's catalogue names several of the surveys as resampled to the stated grid: F00863 to 0.5 m, H12132 to 1 m, W00499 to 2 m.
    - **Repeated values.** In many "0.5 m" tiles, 40–57% of side-by-side pixels have exactly the same value (`spotcheck/out_huron_catalog_summary.json`). The true detail is probably coarser than the stated grid in places.

12. **Housekeeping.**
    - **The program names the lab** in the `User-Agent` it sends to NOAA (l.194, l.235). This fault had already been fixed in #84.
    - **Chart-service errors are swallowed** (l.255–256), as in #84.
    - **Checksums.** The tile checksums are in `results/manifest_hashes.json`, not in `MANIFEST.md`.

13. **Wording.** Withdrawn:
    - "passed cleanly", "resolves every single feature unambiguously", "resolve unmistakably";
    - "proves our automated pipeline can genuinely see small submerged constructions";
    - "the only two basins on Earth where genuine … structures are proven" (no source);
    - "wall-to-wall" for the mid-lake zone. 13 of its 24 tiles hold less than half data, and 35 of the 84 tiles searched do.

    "Feldens et al. 2026" is a manuscript described as submitted. Its authors' conference abstract (EGU26-13394) reports "no substantial seafloor recovery after one year" off Fehmarn and new trawl marks. It does not mention cohesive mud.

### How often planted walls are found (spot check, after the fact)

Random places and directions in every usable tile; three seeds. Stones were modelled as half-ellipsoids. Baltic walls were gridded at 1 m and interpolated to 0.25 m, as the data were. Sources: `spotcheck/out_sens_huron.json`, `spotcheck/out_sens_baltic.json`.

| Planted | Lake Huron 0.5 m | Lake Huron 1 m | Lake Huron 2 m | Baltic 0.25 m (1 m data) |
|---|---|---|---|---|
| The study's wall | 203 of 228 | 212 of 239 | 60 of 120 | 147 of 150 |
| Continuous ridge 1 m wide, 0.5 m high | 211 of 219 | 191 of 229 | 0 of 120 | – |
| Continuous ridge 2 m wide, 0.3 m high | 96 of 217 | 22 of 229 | 0 of 120 | – |
| Continuous ridge 2 m wide, 0.5 m high, 150 m | – | – | – | 116 of 120 |
| Stones 0.4–0.8 m, one every 1.5 m | 0 of 217 | 0 of 230 | 0 of 120 | – |
| Boulders 1.0–1.4 m, about 0.9 m high, one every 2 m | 1 of 217 | 0 of 233 | 0 of 120 | – |
| The Blinkerwall's published stone count and volume | 0 of 218 | 1 of 231 | 0 of 120 | 0 of 120 |
| The same stones in single file | 0 of 216 | 0 of 232 | 0 of 120 | 0 of 120 |
| Upper bound: one stone per metre, 0.6–1.2 m, all under 1 m high | 0 of 217 | 0 of 230 | 0 of 120 | 97 of 120 |

A blur of half a metre, standing in for the sonar's footprint, leaves every line of stones at 0 or 1 found. It lowers the continuous ridges (`spotcheck/out_sens_huron_footprint0.5m.json`).

## The locked run

| Check (plan §4) | Required | Result as the program counts | As the plan words it |
|---|---|---|---|
| Charted Lake Huron wrecks found and linked to the chart | at least 2 of 3 | 2 of 3 | 2 of 3. The third, 8 m high, produced no candidate. The program's test is not the plan's |
| Planted walls, 60 × 2.5 × 0.5 m (120 × 4 × 0.55 m at 2 m) | at least 10 of 12 | 11 of 12 | Holds as run, on the four quietest tiles of each grid size. At random places about 9 of 12 |
| Planted false steps rejected via `SEAM_STEP` | at least 11 of 12 | 11 of 12 | **9 of 12. Fails** |
| Planted Baltic walls | at least 8 of 10 | 8 of 10 | Holds. The walls are bumps in slope or grey level with no height |
| Single-year trawl scars rejected | at least 9 of 10 | 10 of 10 | Cannot fail by construction |

### Lake Huron

| Zone | Surveys | Stated grid | Tiles | Seabed with data (km²) | Ridges kept | Rings / V-shapes | First report's reading of the pictures (not checked) |
|---|---|---:|---:|---:|---:|---:|---|
| H1 | H13652, F00862, F00863 | 0.5 m | 24 | 1.242 | 8 | 0 / 0 | Glacial cobble ridges (6), edges of survey swaths (2) |
| H2 | H12132, H12964 | 1 m | 24 | 3.908 | 6 | 0 / 0 | Limestone ledge (3), glacial swells (2), swath edge (1) |
| H3 | W00499 (mid-lake) | 2 m | 24 | 10.115 | 10 | 0 / 0 | Ledges and hummocks on the ridge |
| H4 | H14139 (laser survey) | 1 m | 12 | 1.220 | 19 | 1 / 1 | Broken limestone pavement (18, the ring and the V), shoreline edge (1) |
| Total | | | 84 | 16.485 | 43 | 1 / 1 | No record of single ridges. 10 of the 43 are in tiles the program never drew |

### Western Baltic

| Area | Grid (true survey grid) | Untrawled seabed with data (km²) | Ridges kept | Rings / V-shapes | First report's reading (not checked) |
|---|---:|---:|---:|---:|---|
| Test1, Mecklenburg Bay | 0.25 m (1 m) | 0.068 | 0 | 0 / 0 | – |
| Test2, Mecklenburg Bay, about 7 km from the Blinkerwall core | 0.25 m (1 m) | 0.222 | 2 | 0 / 0 | Both on the grid's edge. No picture made by committed code |
| Test3, Arkona Basin | 0.25 m (1 m) | 0.168 | 0 | 0 / 0 | – |
| Test4, Kiel Bay | 0.25 m (1 m) | 0.072 | 2 | 0 / 1 | A wreck or obstruction. A wreck is charted 69 m away |
| Test5, Fehmarn Belt | 0.25 m (1 m) | 0.014 | 0 | 0 / 0 | – |
| Fehmarn Belt, 2024 and 2025 compared | 0.5 m | 4.948 | 67 | 1 / not searched | Trawl marks. 7 of 67 looked at |
| Total | | 5.491 | 71 | 1 / 1 | |

## Limits

1. **Too blunt for the target.** The main limit, above.
2. **No real example in the data,** in either basin.
3. **Small and particular areas.** 16.5 km² of Lake Huron, mostly near shore in Thunder Bay or on the western flank of the ridge, and 5.5 km² of Baltic. Most of the Baltic area is off Fehmarn, where trawl marks fill the grid.
4. **The explanations rest on pictures,** some not made by committed code, with no notes.
5. **The Fehmarn arm cannot tell a wall from a trawl mark** that lasts more than a year, and the plan's tool for doing so did not work there.
6. **No replication** by a second company's model.

## Departures from the plan

`amendments.md` lists fourteen, found by the spot check. Among them:

- the shipwreck and false-step checks were not run as worded;
- the planted-wall hosts were chosen as the quietest tiles;
- the Baltic planted walls have no height;
- V-shapes were never searched for off Fehmarn;
- the visual audit covered less than the plan required.

## Spending

Nothing. All data are public. The spot check used no paid service.

## What this means

People did build in stone on land that lakes and seas later covered, and both of the places searched here hold real examples. Looking for more in public sonar is a sensible idea, and this study looked closer than the first attempt. It found nothing unexplained. But the reason to set that aside is simple. The real structures are lines of separate stones, most under a metre high, and the method finds such lines almost never, even when they are planted in the very grids it searched. It can find a continuous bank of stone half a metre high, and there is none unexplained here. A search that means something has to start by finding a known structure in its own data: the Blinkerwall in the Baltic surveys, or a published Lake Huron drive line. Then it needs a detector built for rows of stones, not ridges.
