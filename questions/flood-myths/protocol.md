# Protocol — Do Flood Myths Cluster Where Land Drowned? (#44)

- **Issue:** #44 (`lane:data`)
- **Topic:** Deep memory (`site/topics/deep-memory.md`)
- **Date:** 2026-11-24
- **Budget:** $0 (open Harvard Dataverse + NOAA NCEI datasets; local Python computation)

## 1. Exact Question

Across 958 world oral traditions in Yuri Berezkin's Folklore and Mythology Catalog, are non-biblical flood and deluge motifs systematically more common among **coastal peoples whose homelands lost large areas of continental shelf to post-glacial sea-level rise** (~120 m rise between ~20,000 and 7,000 BP) than among coastal peoples whose homelands lost little land—after controlling for coastline proximity, river and seismic/tsunami exposure, ethnographic sampling effort, missionary Noah diffusion, language-family shared descent, and spatial autocorrelation?

## 2. Primary Public Datasets (`MANIFEST.md`)

1. **Berezkin Folklore & Mythology Catalog (Michalopoulos & Xue 2021 *QJE* replication package, Harvard Dataverse `doi:10.7910/DVN/IXOHKB`):**
   - `Motif_Master.dta`: 2,564 Berezkin motifs with English and Russian titles/descriptions.
   - `Motifs_Berezkin_groups.dta`: binary motif presence across 958 global oral traditions.
   - `Berezkin_groups_Regressions_Ready.dta`: society coordinates (`latitude_forgeo`, `longitude_forgeo`), 75 language families (`language1`), continents (`continent_bere`), ethnographic sampling controls (`lnnmbr_title`, `lnyear_firstpub`, `motifs_total`), river distance (`lnriver_dist_bere`), seismic/tsunami distance (`lnbdisttoquake1000`), climate (`avtemp200_bere`), and Michalopoulos & Xue concept shares (`flood_related`, `earthquake_related`, `sea_related`, `ocean_related`, `fire_related`).
2. **NOAA ETOPO 2022 60-arc-second Global Bedrock Relief Model (`ETOPO_2022_v1_60s_N90W180_bed.nc`, `doi:10.25921/fd45-gt74`):**
   - `10,800 × 21,600` 1-arc-minute global bathymetry/topography grid, block-averaged to 5-arc-minute (`2,160 × 4,320`, ~9.3 km at equator) with exact spherical cell areas `A(lat) = (R Δφ)(R Δλ cos φ)` for fast, exact radial integration around all 958 ethnographic centroids.

## 3. Pre-Registered Exposure, Outcomes, and Controls

### 3.1 Post-glacial drowned-land exposure (from ETOPO 2022)
For every society centroid `(lat_i, lon_i)`:
- **`dist_coast_km`:** Great-circle distance to the nearest modern ocean grid cell (`z < 0 m`).
- **Coastal subsample (primary like-with-like test):** Societies with `dist_coast_km ≤ 150 km` (comparing coastal peoples on wide drowned continental shelves—e.g., Sahul/Australia, Sundaland, North Sea/Doggerland, Beringia, East China Sea, Patagonia—against coastal peoples on steep narrow shelves).
- **Primary exposure — `log_drowned_120m_250km`:** `log(1 + Area_km2)` of grid cells within a `250 km` great-circle disk around `(lat_i, lon_i)` with bedrock elevation **`−120 m ≤ z < 0 m`** (dry land at the ~20 ka Last Glacial Maximum, drowned by post-glacial sea-level rise).
- **Secondary exposures (pre-registered sensitivity checks):**
  - **`drowned_frac_ocean_250km`:** Fraction of ocean cells within `250 km` lying between `−120 m` and `0 m` (pure shelf-width index, decoupled from whether a society sits on an island vs. peninsula!).
  - **`log_drowned_60m_250km`:** Area within `250 km` at **`−60 m ≤ z < 0 m`** (specifically the final ~12–7 ka Holocene inundation window linked to Australian coastal oral histories).
  - **`log_drowned_120m_500km`:** Wider `500 km` radius sensitivity check.

### 3.2 Flood-myth outcomes (fixed before examining correlations)
1. **Primary Outcome A (`non_biblical_flood_share` & binary `any_non_biblical_flood`):** Constructed directly from `Motifs_Berezkin_groups.dta` using the **17 pre-registered Berezkin non-biblical deluge/flood motifs** (strictly excluding Noah's Ark `c3` and Genesis dove/raven bird-scouts `c5a`):
   `{c2, c4, c7, c9a, c10, c10a, c12a, c12b, c13, c14, b7b, b7d, b52a, g9a, i81a, k38d, l28a}`.
   - `non_biblical_flood_share = count_of_17_motifs / motifs_total` (standardized to z-score for regression comparison), and `any_non_biblical_flood = 1[count ≥ 1]`.
2. **Primary Outcome B (`flood_related`):** Michalopoulos & Xue's (2021) pre-built share of all Berezkin motifs per society mentioning flood/deluge terms (external researcher-defined outcome, zero author discretion), tested both on all coastal societies and on the **strict Noah-free subsample** (excluding societies possessing `c3` or `c5a`).

### 3.3 Calibration gate (positive and negative controls)
Before interpreting flood results, verify on the same 958 societies:
- **Positive Control 1:** `earthquake_related` correlates strongly with proximity to earthquake zones (`−lnbdisttoquake1000`, replicating Michalopoulos & Xue 2021) with language-family clustered and Conley spatial SEs (`p < 0.01`).
- **Positive Control 2:** `sea_related` correlates strongly with coastal proximity (`−log(1 + dist_coast_km)`, `p < 0.001`).
- **Negative Control:** `fire_related` shows **no** spurious significant positive association with `log_drowned_120m_250km` among coastal societies after controls (`p > 0.05`).

### 3.4 Confound, phylogeny, and spatial-autocorrelation models
For each primary outcome (`non_biblical_flood_share`, `any_non_biblical_flood`, `flood_related`), estimate a progressive ladder of OLS linear probability / share models on the **coastal subsample (`dist_coast_km ≤ 150 km`)** and on the **full global sample (`N = 958`)**:
- **M1 (Baseline + sampling effort):** `drowned_exposure + log(1 + dist_coast_km) + lnnmbr_title + lnyear_firstpub + log(1 + motifs_total)`
- **M2 (+ geophysical & non-glacial flood controls):** M1 `+ lnriver_dist_bere + lnbdisttoquake1000 + avtemp200_bere + abs(latitude)`
- **M3 (+ continent fixed effects):** M2 `+ continent FE`
- **M4 (PRIMARY CONFIRMATORY MODEL — Language-family FE + Spatial/Cluster SEs):** M2 `+ language_family FE` (controlling for shared linguistic descent / Galton's problem across all 75 language families!)

For **every** model M1–M4, report:
1. **Language-family cluster-robust standard errors** (Liang–Zeger / Cameron–Gelbach–Miller CR1 clustered on `language1`),
2. **Conley (1999) spatial-HAC standard errors** with Bartlett kernel at **`500 km`** and **`1,000 km`** distance cutoffs (exact great-circle distances),
3. **Residual Moran's I** (inverse-distance weights within `1,000 km`), and
4. **Spatial-block / within-continent permutation p-value** (2,000 permutations of exposure within continent, preserving spatial/continental structure, plus a 1,000-km spatial-grid block bootstrap).

### 3.5 Regional breakdown & Australia/Sahul check
Report regional slopes separately across macro-regions (Australia/Sahul & Oceania, Eurasia, Americas, Africa) to check whether any global pattern is worldwide or confined to a single shelf system (e.g., Sahul/Australia).

## 4. Pre-Registered Verdict Criteria

- **Positive (Global drowned-land memory signal):** On the primary coastal subsample (`dist_coast_km ≤ 150 km`) in **M4** (controlling for sampling effort, coast/river/seismic/climate controls, and language-family FE), `log_drowned_120m_250km` has a positive coefficient (`β > 0`) with **`p < 0.01`** under **BOTH** language-family clustered SEs AND `1,000 km` Conley spatial-HAC SEs for **at least one** primary outcome (`non_biblical_flood_share` or Noah-free `flood_related`), retains positive direction in M3 (continent FE) and under `−60 m` Holocene shelf exposure, AND passes all calibration controls (earthquakes positive, fire negative).
- **Null (No global clustering where land drowned):** In **M4** (and M3) on the coastal subsample, the association between drowned continental shelf area (`−120 m` and `−60 m`) and non-biblical flood motifs is statistically indistinguishable from zero (`p ≥ 0.05` under Conley `1,000 km` or language-family clustered SEs) or negative, while Positive Controls 1 & 2 succeed decisively (`p < 0.01`).
- **Inconclusive / Regional only:** A positive association (`p < 0.05`) survives M1–M2 but collapses under language-family FE or Conley spatial-HAC SEs (Galton's problem / regional clustering), OR holds strongly in one macro-region (e.g., Australia/Sahul) with null/opposite signs elsewhere.

## 5. Verification

Synthetic unit tests (`analysis/test_flood_myths.py`) verifying exact spherical grid cell area integration, coastal-distance calculation, Conley spatial-HAC variance estimation under planted spatial autocorrelation, and language-family clustered SEs before inspecting real regressions.
