# Amendments — Stone walls in finer public sonar: Lake Huron and the western Baltic (#143)

## Record added after the spot check — 2026-11-27

Nothing in the locked analysis, in `analysis/` or in `results/` was changed or rerun for this record. The
spot check reran the program unchanged and got the same counts. Line numbers refer to
`analysis/run_submeter_scan.py`.

Departures from the locked plan that the first report did not record:

1. **Shipwreck check.**
   - **The plan** (§4.1): the detector must "detect" two of three charted wrecks with a height of at least 0.80 m and link them to the chart.
   - **The program** (l.1030–1046) takes instead the highest point in a 140 m square at the tile centre and the distance from the tile centre to the charted wreck. The tiles were centred on the wrecks, so the second test cannot fail.
   - **The 70 m half-width** is not in the plan.
2. **Hosts for the planted walls.**
   - **The plan:** "real Lake Huron tiles".
   - **The program** (l.1090–1095) takes, for each grid size, the four tiles with at least 85% data and the fewest natural detections. It plants at a fixed position (l.557–565) along four fixed directions (l.1095).
3. **What counts as found.** "An unmasked ridge within 30 m of the planted centre" (l.1110–1113; 25 m in the Baltic, l.1217–1220 and l.1358–1361) is not in the plan.
4. **False steps.**
   - **The plan** (§4.3): steps must be rejected "via `SEAM_STEP`".
   - **The program** (l.1119–1128) counts a step as rejected whenever no unmasked ridge lies near it, including when no ridge was detected at all. Via `SEAM_STEP` the count is 9 of 12, which fails the plan's 11.
   - **The planted step** also carries a 0.12 m ridge along its edge (l.591) that the plan does not describe.
5. **Baltic planted walls in the test areas.**
   - **The plan:** walls 0.60 m high whose slopes form a "double-flank" signal, in untrawled seabed.
   - **The program** (l.1211–1216, l.856–858) adds a single bump of +12° straight to the slope grid, unrelated to any height. It does this on a 90 m crop with the trawl mask replaced by "all valid", unlike the scan itself.
6. **Baltic planted walls off Fehmarn.** They are +65 grey levels in a picture of slope with no physical scale (l.1354–1355). The plan gives them a height of 0.60 m.
7. **V-shapes and corners off Fehmarn.** These are never searched for. The summary writes them as 0 (l.1321–1322). The plan (§5) requires every V-shape to be inspected.
8. **Scope of the visual audit.**
   - **The plan** (§5): close-up "contact sheets" of the top 15 Lake Huron and top 10 Baltic hits, and of every ring and V-shape.
   - **Lake Huron.** The program draws whole-tile previews for 10 of the 18 Lake Huron tiles with hits (l.1071–1085).
   - **Baltic.** It draws no picture of a test-area hit, the Kiel Bay ring-and-V area included (l.1370–1388). The first report describes six of the top ten Fehmarn hits.
9. **Classes.** The audit's labels are not the plan's five: for example "multiyear_persistent_trawl_or_anchor_scar", "untrawled_obstruction_with_scour_comet_mark" and "raster_border_edge_artifact" (`results/visual_audit.json`).
10. **Fehmarn hits never looked at.** 60 of the 67 Fehmarn hits were classed as trawl marks without being looked at (`results/visual_audit.json`: 7 inspected, 67 classified).
11. **Aligning 2024 with 2025.**
    - **The plan:** "exact UTM 33N coordinates".
    - **The program** (l.1239–1240) rounds the shift to whole pixels, dropping offsets of 0.43 and 0.27 pixel (about 0.2 m).
12. **Munition check.** The munition table the plan names covers 54.03–54.50° N, 10.28–11.00° E. It does not reach any Baltic area searched, so the flag (l.669–676) could never fire.
13. **Distance to the Blinkerwall.** The plan (§2) puts Test2 "~3–5 km from Blinkerwall". Its nearest corner is 7.1 km from the discoverers' core beside the wall. The program's label says "~4 km" (l.1145).
14. **Gallery pictures.** Two pictures in the published gallery are made by no committed code: the Kiel Bay close-up and the planted-wall picture (`analysis/make_figures.py` l.82 and l.100). The scanner names its files differently (l.1378).

Also recorded:

- **The verdict rule.** Plan §5 says the result is "Inconclusive" if any calibration check fails. As worded, the false-step check fails (item 4). `RESULTS.md` now reports "Inconclusive".
- **The thresholds were set after exploration had measured the controls.** `explore/README.md` records the three wrecks' heights (+1.25, +8.09, +12.93 m) before the lock. The plan then set the threshold at 0.80 m.
- **A fault in the plan itself.**
  - **The planted walls** are continuous ridges, unlike any real structure (lines of separate stones).
  - **The rings and V-shapes** the plan searches for are at least 8 m across (20 m on two-metre grids), with arms of at least 25 m (40 m). Published hunting blinds are 3–4 m across.
  - **The trawl-scar check** cannot fail by construction (l.1340–1341).
- **The program names the lab** in the `User-Agent` it sends to NOAA (l.194, l.235), a fault already fixed in #84. It has not been changed here; whoever next runs the program should change it.
- **Analyses added by the spot check, outside the plan:**
  - structures of published sizes planted at random positions, three seeds;
  - the controls and false steps examined one by one;
  - the survey sources under each tile;
  - the distances, munition coverage and chart objects.

  All are in `spotcheck/` and all are exploratory.
