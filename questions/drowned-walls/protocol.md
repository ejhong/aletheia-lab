# Protocol — Unmapped Stone Structures in Public Ice Age Seafloor Sonar (#84)

- **Issue:** #84 (`lane:data`)
- **Date:** 2026-11-24
- **Budget:** $0 (public NOAA NCEI BAG 2 m multibeam ImageServer + NOAA ENC Direct REST overlays; local Python computation)

## 1. Exact Question

Running a pre-registered, calibrated geometric ridge-and-enclosure detector across **40 high-resolution (`~2 m/pixel`, `~42 km²`) public NOAA NCEI multibeam sonar (BAG) tiles** spanning four drowned Ice Age paleo-shorelines (`−10 m` to `−80 m` depth, dry land `15,000–8,000 BP`), after explicitly rejecting multibeam swath/mosaic seams, periodic sandwave trains, and charted modern wrecks/cables/pipelines/obstructions from NOAA ENC Direct, do any **unmapped rectilinear walls, stone hunting drive-lanes, or geometric enclosures** survive automated filtering and direct shaded-relief visual audit?

## 2. Pre-Registered Calibration & Search Grid

All tiles are exported at `512 × 512` pixels (`Δlat = 0.0092°`, `Δlon = 0.0092° / cos(lat)` → `~1.02 km × 1.02 km`, **`~2.0 m/pixel`**) using `format=tiff`, `pixelType=F32`, `interpolation=RSP_NearestNeighbor`, `noData=-999999`. Valid shelf pixels satisfy `z ∈ [−120 m, −2 m]` eroded by `3` pixels from any `noData` boundary to eliminate mosaic-edge cliffs.

### 2.1 Positive Controls (Calibration Gate)
1. **Real-Sonar Breakwater Controls (2 tiles):**
   - `CTRL_DELAWARE`: Delaware Outer Breakwater / Harbor of Refuge (`center 38.814° N, −75.108° W`) — known submerged/emergent linear granite stone wall in NOAA BAG.
   - `CTRL_PTJUDITH`: Point Judith Harbor of Refuge Outer Breakwater (`center 41.363° N, −71.500° W`) — known linear submerged stone wall toe in NOAA BAG.
2. **Real-Noise Planted "Blinkerwall" Sensitivity Gate (`10` trials):**
   - Parameterized directly to Geersen et al. (2024, *PNAS* `e2312008121`): inject a synthetic linear stone hunting drive-lane (`length = 250 m`, `width = 4 m`, `height = 0.70 m` Gaussian ridge cross-section, random non-cardinal azimuth) onto real 2 m NOAA shelf background tiles (`z ∈ [−45 m, −15 m]`).
   - **Calibration requirement:** Must recover **≥ 1 of 2 real breakwater walls** AND **≥ 80% (`≥ 8/10`)** of planted `0.70 m`-high Blinkerwall-scale drive-lanes on real NOAA multibeam seafloor noise, while rejecting `100%` of planted `0.70 m` step-function mosaic seams!

### 2.2 Pre-Registered Ice Age Paleo-Shoreline Search Grid (`40` Tiles, `~42 km²`)
- **Region A — California Channel Islands (`Santarosae` Ice Age mega-island shelf, `12` tiles):**
  - `3 × 2` grid in Anacapa Passage / East Santa Cruz shelf (`lon ∈ [−119.50, −119.43]`, `lat ∈ [33.99, 34.03]`, `6` tiles) + `3 × 2` grid on East Santa Rosa shelf (`lon ∈ [−120.00, −119.93]`, `lat ∈ [33.92, 33.96]`, `6` tiles).
- **Region B — New England Drowned Glacial Moraine Shelf (`Block Island Sound`, `10` tiles):**
  - `5 × 2` grid (`lon ∈ [−71.58, −71.48]`, `lat ∈ [41.13, 41.17]`, `−15 m` to `−45 m` depth).
- **Region C — New York Bight / Drowned Hudson Paleo-River Shelf (`10` tiles):**
  - `5 × 2` grid (`lon ∈ [−73.85, −73.75]`, `lat ∈ [40.39, 40.43]`, `−15 m` to `−45 m` depth).
- **Region D — Florida Keys Submerged Karst Shelf (`8` tiles):**
  - `4 × 2` grid (`lon ∈ [−81.85, −81.77]`, `lat ∈ [24.45, 24.49]`, `−10 m` to `−60 m` depth).

## 3. Pre-Registered Geometric Detector & False-Positive Rejection Pipeline

1. **Local Bathymetric Position Index (`BPI`):**
   - `BPI(x, y) = z(x, y) − GaussianBlur_masked(z, σ = 12 px ≈ 24 m)` computed strictly over valid shelf pixels.
   - Positive ridge mask: `BPI ≥ +0.35 m` (suppressing tiny sonar ping noise `< 0.25 m` and broad regional slopes).
2. **Connected Ridge Component & Geometry Extraction:**
   - Label 8-connected components with area `≥ 40` pixels (`≥ 160 m²`), PCA major-axis span `L ≥ 60 m` (`≥ 30 px`), minor-axis width `W ≤ 20 m`, **linearity** `lin = λ_1 / (λ_1 + λ_2) ≥ 0.90`, and mean ridge prominence `mean_BPI ≥ 0.35 m`.
3. **Automated Artifact & Natural-Bedform Rejection Filters:**
   - **Step-edge / mosaic-seam rejection:** Measure median depth in parallel `8–20 m` flank strips on the left (`z_L`) and right (`z_R`) of the ridge axis. Flag as `SEAM_STEP` if `|z_L − z_R| > 0.65 * ridge_prominence` (a true freestanding wall has matching seafloor elevation on both flanks; a sonar datum offset/mosaic seam is a one-sided step!).
   - **Axis-aligned raster seam rejection:** Flag as `AXIS_SEAM` if azimuth is within `± 1.5°` of exact `0°` or `90°` AND extends across `> 60%` of the tile or touches a `noData` mask boundary.
   - **Periodic sandwave-train rejection:** Compute the 1D cross-axis BPI profile (`± 80 m` perpendicular to the ridge). Flag as `SANDWAVE_PERIODIC` if `≥ 2` secondary parallel crests of height `≥ 0.40 * peak` appear on the flanks at regular spacing `12–60 m`.
   - **NOAA ENC Chart Overlay Masking:** Query `enc_approach` layers (`36, 39, 89, 103, 118, 119, 143, 161, 163, 169, 172`) for every tile; flag any candidate whose centroid/segment falls within `150 m` of a charted wreck, obstruction, submarine cable, pipeline, or shoreline construction as `CHARTED_MODERN`.
4. **Right-Angle Corner / Enclosure Check:**
   - Flag any pair of surviving non-artifact linear ridges within `40 m` whose axes intersect at `75°–105°` as `RECTILINEAR_CORNER`, and any closed ring component (`BPI ≥ +0.35 m`, bounding diameter `25–200 m`, hollow center `BPI ≤ 0.05 m`) as `RING_ENCLOSURE`.
5. **Visual Shaded-Relief Audit (Mandatory):**
   - Render shaded-relief + BPI overlay PNGs for the positive controls and the **top 8 highest-scoring unmasked candidates**, and inspect every PNG visually to distinguish genuine anthropogenic-candidate geometry from geological bedrock strike ridges, reef ledges, or subtle multibeam swath artifacts.

## 4. Pre-Registered Verdict Criteria

- **Unmapped Candidate Flagged for Marine-Archaeology Follow-Up:** Calibration gate passes (`≥ 1/2` real breakwaters AND `≥ 8/10` planted Blinkerwall walls recovered, `100%` step seams rejected), AND `≥ 1` unmasked (`not CHARTED_MODERN`, `not SEAM_STEP`, `not AXIS_SEAM`, `not SANDWAVE_PERIODIC`) linear wall (`L ≥ 60 m`, `lin ≥ 0.90`, `prominence ≥ 0.35 m`), rectilinear corner, or ring enclosure survives direct visual shaded-relief inspection as inconsistent with natural geological strata/bedforms or sonar artifacts.
- **Null (No unmapped stone structures detected in the 42 km² scan):** Calibration gate passes decisively, while zero unmasked candidates survive automated artifact/bedform filtering and visual shaded-relief audit (all surviving ridges trace to natural bedrock strata, glacial moraine crests, reef ledges, or charted/modern features).
- **Inconclusive / Calibration Failure:** Detector fails to recover `< 8/10` planted Blinkerwall ridges or fails to recover real breakwater controls.

## 5. Verification

Synthetic unit tests (`analysis/test_drowned_walls.py`) verifying (1) recovery of a planted `250 m × 4 m × 0.70 m` linear wall at arbitrary azimuth, (2) rejection of a `0.70 m` one-sided mosaic step seam (`SEAM_STEP`), (3) rejection of a periodic sandwave field (`SANDWAVE_PERIODIC`), and (4) detection of a planted `90°` rectilinear corner (`RECTILINEAR_CORNER`) before running on real NOAA BAG tiles.
