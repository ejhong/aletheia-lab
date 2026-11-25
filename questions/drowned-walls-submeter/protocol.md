# Protocol — Sub-Meter Sonar Hunt for Prehistoric Submerged Walls: Lake Huron & Western Baltic (#143)

- **Issue:** #143 (`lane:data`)
- **Follow-up to:** #84 (`drowned-walls`, 2 m U.S. marine shelf scan — null result)
- **Date drafted:** 2026-11-24
- **Budget:** $0.00 (100% public NOAA NCEI, NOAA ENC, Zenodo CC-BY 4.0, and PANGAEA CC-BY 4.0 data)

---

## 1. Exact Research Question

Do public **sub-meter to 2 m** multibeam and bathymetric LiDAR grids over the two basins where genuine ~9,000–11,000-year-old submerged Stone Age boulder structures are already archaeologically proven —

1. **Arm 1 — Lake Huron's Alpena–Amberley Ridge & Thunder Bay shelf** (`0.50 m`, `1.00 m`, and `2.00 m` NOAA NCEI BAG elevation grids, dry land during the Lake Stanley lowstand ~9,900–7,500 cal BP, where O'Shea & Lemke documented 9,000-year-old caribou stone drive-lanes and hunting blinds), and
2. **Arm 2 — German Western Baltic Sea** (`0.25 m` and `0.50 m` BSH multibeam slope grids across Mecklenburg Bay, Kiel Bay, Fehmarn Belt, and Arkona Basin, dry land during the Preboreal/Ancylus lowstand ~11,000–8,500 cal BP, immediately surrounding Geersen et al.'s 2024 *Blinkerwall*) —

contain any **unmapped, non-artifact, non-modern geometric stone structures** (linear boulder walls/drive-lanes, V-shaped hunting funnels or right-angle corners, or hollow stone hunting blinds/enclosures)?

---

## 2. Pre-Registered Target Regions & Tile Grids

### Arm 1: Lake Huron — 87 Pre-Registered `512×512` F32 Elevation Tiles (`~36.2 km²` nominal)

All tiles are exported directly from NOAA NCEI `bag_bathymetry/ImageServer/exportImage` (`pixelType=F32`, `RSP_NearestNeighbor`, EPSG:4326) at each survey's native pixel resolution:

| Zone | NOAA Surveys | Native Pixel Size | Tile Footprint | Tiles | Bounding Grid (`lon`, `lat`) | Depth / Paleo Context |
|---|---|---:|---:|---:|---|---|
| **Controls** | `H13652`, `F00862`, `W00499_2of2` | `0.50 m` / `2.00 m` | `256 m` / `1024 m` | **3** | Centered on 3 NOAA ENC charted Thunder Bay wrecks: `(-83.2184, 45.1055)`, `(-83.2681, 44.9851)`, `(-82.9240, 44.9837)` | Real freshwater anthropogenic positive controls |
| **H1 (50 cm Multibeam)** | `H13652_MB_50cm` (12), `F00862_MB_50cm` (6), `F00863_MB_50cm` (6) | **`0.50 m`** | `256 m × 256 m` | **24** | `H13652`: `[-83.29,-83.21]×[45.06,45.14]` (3×4); `F00862`: `[-83.265,-83.235]×[44.990,45.006]` (3×2); `F00863`: `[-83.218,-83.182]×[44.990,45.012]` (3×2) | Ultra-low-noise (`5–11 cm` σ) Thunder Bay / Middle Island shelf (`−3` to `−29 m`) |
| **H2 (1 m Multibeam)** | `H12132_MB_1m` (16), `H12964_MB_1m` (8) | **`1.00 m`** | `512 m × 512 m` | **24** | `H12132`: `[-83.39,-83.13]×[44.99,45.11]` (4×4); `H12964`: `[-83.245,-83.188]×[45.090,45.132]` (4×2) | Wide Thunder Bay / North Point paleo-shoreline (`−4` to `−24 m`) |
| **H3 (2 m Mid-Lake Ridge)** | `W00499_MB_2of2_interp2m` | **`2.00 m`** | `1024 m × 1024 m` | **24** | `[-82.968,-82.864]×[44.956,45.044]` (6×4 wall-to-wall) | **Mid-lake Alpena–Amberley Ridge / Six Fathom Scarp** (`−38` to `−82 m`, prime Lake Stanley caribou causeway) |
| **H4 (1 m Bathy LiDAR)** | `H14139_LI_1m` | **`1.00 m`** | `512 m × 512 m` | **12** | `[-83.34,-83.25]×[44.78,44.94]` (2×6 coastal strip) | Nearshore limestone paleo-bench south of Alpena (`−4` to `−24 m`) |

### Arm 2: German Western Baltic — 6 Pre-Registered High-Resolution BSH Slope Datasets (`~5.98 km²` valid seabed)

All grids are CC-BY 4.0 BSH multibeam slope rasters from `10.5281/zenodo.19131526` (UTM Zone 33N), cross-checked against `10.1594/PANGAEA.988426` (484 WWII munition-pile records):

1. **Arm 2A — `Test1`–`Test5` (`0.25 m/px` float32 slope in degrees, `0.717 km²`):**
   - `Test1` (Mecklenburg Bay, `54.273°N, 11.490°E`, `0.097 km²`)
   - `Test2` (Mecklenburg Bay, `54.173°N, 11.360°E`, `0.289 km²`, ~3–5 km from *Blinkerwall*)
   - `Test3` (Arkona Basin, `54.663°N, 13.793°E`, `0.189 km²`)
   - `Test4` (Kiel Bay, `54.553°N, 10.238°E`, `0.112 km²`)
   - `Test5` (Fehmarn Belt, `54.541°N, 10.713°E`, `0.030 km²`)
   - **Trawl-scar exclusion:** Expert-annotated trawl-mark pixels (`mask == 76`, dilated by `2 px = 0.50 m`) are explicitly masked out before anomaly extraction.
2. **Arm 2B — `Time_Series/slope_2024.tif` + `slope_2025.tif` (`0.50 m/px`, `~5.26 km²` overlapping seabed in Fehmarn Belt, `54.55°N, 10.77°E`):**
   - **Temporal Persistence Filter:** Co-register 2024 and 2025 grids in exact UTM 33N coordinates using `.tfw` transforms, invert grayscale to steepness (`S = 255 - gray`), and compute **`S_persist = min(S_2024, S_2025)`** inside their shared valid mask (`alpha_2024 == 255 & alpha_2025 == 255`, eroded `4 px` from noData borders).
   - Transient fishing trawl scars that appear or heal between 2024 and 2025 drop out of `S_persist`, isolating **temporally static** seafloor features (stone walls, boulder alignments, bedrock ledges, wrecks, cables/pipelines).

---

## 3. Detection Metrics & Artifact / Confounder Filters

### Arm 1 (Lake Huron Elevation Grids)
1. **Valid depth domain:** `-120.0 m <= z <= -1.5 m` (`<= +1.5 m` for positive controls); valid mask eroded `3 px` away from noData borders.
2. **Scale-matched Bathymetric Position Index (BPI):** Normalized Gaussian background subtraction with physical scale `sigma_m = 10.0 m` (`20 px` at `0.50 m`, `10 px` at `1.00 m`, `5 px` at `2.00 m`).
3. **Linear wall / drive-lane criteria:** Connected positive-BPI components with:
   - At `0.50–1.00 m/px`: `BPI >= 0.25 m`, `length >= 25.0 m`, `width <= 10.0 m`, PCA linearity `lam1/(lam1+lam2) >= 0.88`, `area >= 40 px` (at `0.50 m`) or `>= 20 px` (at `1.00 m`).
   - At `2.00 m/px`: `BPI >= 0.30 m`, `length >= 40.0 m`, `width <= 16.0 m`, PCA linearity `>= 0.88`, `area >= 20 px`.
4. **Hunting-blind / enclosure rings:** Non-linear (`linearity < 0.78`) hollow positive-BPI structures with diameter `8–80 m` (at `0.50–1.00 m/px`) or `20–150 m` (at `2.00 m/px`), `>= 6/8` octants occupied around centroid, and depressed/flat interior (`center_BPI <= 0.05 m`).
5. **V-funnels & rectilinear corners:** Pairs of unmasked linear candidates whose nearest endpoints lie within `<= 25 m` (`<= 40 m` at `2.00 m/px`) meeting at either **rectilinear corners (`75°–105°`)** or **caribou V-funnel convergence angles (`20°–75°`)**.
6. **Mandatory artifact & modern masks:**
   - `SEAM_STEP`: median elevation difference between parallel flanks (`±6..12 m` at `0.5–1 m/px`; `±10..18 m` at `2 m/px`) exceeds `0.65 × max_BPI`.
   - `AXIS_SEAM`: azimuth within `±1.5°` of N–S or E–W AND either touches eroded noData border (`>= 5 px`) or spans `> 60%` of tile width.
   - `PERIODIC_BEDFORM`: `>= 2` flanking cross-axis BPI peaks (`>= 0.40 × center_peak`) within `±60 m` (rejects sand ripples, glacial fluting, periodic limestone bedding ribs).
   - `CHARTED_MODERN`: within `120 m` of any NOAA `enc_general` cultural feature (Layers `15, 26, 29, 42, 45, 59, 69, 83, 84, 88, 98`).

### Arm 2 (Western Baltic Slope Grids)
1. **Arm 2A (`0.25 m/px` float32 degrees, untrawled seabed):**
   - Local residual slope `dS = slope - gaussian(slope, sigma=20 m)` computed inside untrawled valid pixels (`mask != 76`, eroded `2 px` around trawl mask).
   - Positive ridge threshold: `slope >= 3.0°` AND `dS >= 1.5°`.
   - Linear stone-wall / boulder-line criteria: `length >= 20.0 m`, `width <= 10.0 m`, linearity `>= 0.88`, `area >= 80 px` (`>= 5 m²`).
   - Circular/enclosure boulder ring criteria: `diameter 6–60 m`, `>= 6/8` octants occupied, hollow center (`center_slope <= local_median + 0.5°`).
   - Artifact filters: `AXIS_SEAM` (`±1.5°` of cardinal axes touching border), `PERIODIC_BEDFORM` (`>= 2` parallel flanking slope peaks).
   - Confounder flag: `NEAR_MUNITION_CELL` if within `1.5 km` of any `PANGAEA.988426` munition pile (noting `0.01°` rounding).
2. **Arm 2B (`0.50 m/px` Fehmarn Belt 2024∩2025 persistent steepness):**
   - Compute `S_persist = min(255 - gray_2024, 255 - gray_2025)` and local residual `dS_p = S_persist - gaussian(S_persist, sigma=20 m)`.
   - Threshold: `dS_p >= 35.0` gray levels (and `S_persist >= 55.0`), scanned in tiled `512 m × 512 m` blocks (with `64 m` overlap, deduplicated within `25 m`).
   - Linear persistent-wall criteria: `length >= 30.0 m`, `width <= 12.0 m`, linearity `>= 0.88`, `area >= 60 px` (`>= 15 m²`).
   - Persistent ring criteria: `diameter 12–100 m`, `>= 6/8` octants, hollow center (`center_dS <= 10.0`).
   - Artifact & confounder flags: `AXIS_SEAM`, `PERIODIC_BEDFORM`, `NEAR_MUNITION_CELL`.

---

## 4. Pre-Registered Calibration & Validation Gates

Before trusting any scan result, the pipeline must pass **all four** quantitative calibration checks:

1. **Arm 1 Real Wreck Controls:** Detect `>= 2/3` charted Lake Huron shipwrecks (`CTRL_HURON_WRECK_*`) with `max_BPI >= 0.80 m` and correctly link them to NOAA `enc_general` Layer 29 (`CHARTED_MODERN`).
2. **Arm 1 Synthetic Stone Drive-Lane Recovery:** Plant `12` realistic Stone Age boulder drive-lanes (`length = 60 m`, `width = 2.5 m`, `height = 0.50 m` on `0.50–1.00 m/px` tiles; `length = 120 m`, `width = 4.0 m`, `height = 0.55 m` on `2.00 m/px` tiles; off-axis azimuths) onto real Lake Huron tiles → **must recover `>= 10/12` (`>= 83%`) as unmasked linear hits.**
3. **Arm 1 Synthetic Mosaic Step-Seam Rejection:** Plant `12` `0.50 m` one-sided datum step seams onto real Lake Huron tiles → **must reject `>= 11/12` (`>= 92%`) via `SEAM_STEP`.**
4. **Arm 2 Synthetic Persistent Wall vs. Transient Trawl-Scar Benchmark:**
   - Plant `10` synthetic *Blinkerwall*-scale boulder walls (`length = 60 m`, `width = 2.5 m`, `height = 0.60 m` → double-flank slope bump present in untrawled `Test1`–`Test5` and in *both* `2024` & `2025` Fehmarn Belt grids) → **must recover `>= 8/10` (`>= 80%`).**
   - Plant `10` synthetic transient single-year trawl scars (present in `2024` only, absent in `2025`) on Fehmarn Belt → **must reject `>= 9/10` (`>= 90%`) via temporal persistence.**

---

## 5. Mandatory Visual Hillshade / Slope Audit & Decision Rules

Every unmasked top-ranked linear candidate (top `15` in Arm 1, top `10` in Arm 2) and **100%** of detected V-funnels, corners, and hollow rings must be rendered as high-resolution visual audit contact sheets (shaded-relief hillshade + BPI for Lake Huron; untrawled slope + 2024 vs. 2025 comparison for Western Baltic) and directly inspected by eye before final classification into:
- `geological_bedform` (sand ripples, glacial drumlins, moraine ridges),
- `bedrock_scarp_or_ledge` (dolomite/limestone escarpments, karst shelves),
- `uncharted_wreck_or_modern_debris` (hull geometry, dredge/anchor/cable/pipeline/munition signature),
- `sonar_or_mosaic_artifact` (swath nadir stripes, patch-test seams), or
- `candidate_archaeological_structure` (sharp, non-geological, unmapped stone wall / drive-lane / hunting blind / rectilinear or V-funnel enclosure warranting underwater archaeological follow-up).

### Verdict Rules
- **Candidate prehistoric structure(s) found:** All 4 calibration gates pass AND `>= 1` unmasked feature survives visual audit as `candidate_archaeological_structure` (with exact coordinates, dimensions, and hillshade/slope cutouts reported for independent specialist verification).
- **Null (no unmapped prehistoric walls found):** All 4 calibration gates pass AND `0` features survive visual audit as `candidate_archaeological_structure` (reporting any interesting uncharted modern wrecks/geological features separately and transparently).
- **Inconclusive:** Any calibration gate fails.
