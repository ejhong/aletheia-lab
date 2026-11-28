# Data Manifest — Sub-Meter Drowned Walls Hunt (#143)

Large raster files live in `data/` (gitignored). Every dataset below is publicly downloadable with zero authentication or payment, and exact SHA-256 digests are recorded here (and in `results/manifest_hashes.json` for dynamically tiled NOAA BAG exports).

## 1. Arm 1 — Lake Huron Alpena–Amberley Ridge & Thunder Bay Shelf (NOAA NCEI)

| Dataset | Source URL | Retrieval Date | Licence | Resolution & Coverage | Integrity / Pinning |
|---|---|---|---|---|---|
| **NOAA NCEI Bathymetric Attributed Grid (`bag_bathymetry`) ImageServer** | `https://gis.ngdc.noaa.gov/arcgis/rest/services/bag_bathymetry/ImageServer/exportImage` | 2026-11-24 | U.S. Government Public Domain (NOAA/NCEI) | Native `0.50 m` (`H13652`, `F00862`, `F00863`), `1.00 m` (`H12132`, `H12964`, `H14139_LI`), `2.00 m` (`W00499_2of2`) | 87 pre-registered `512×512` F32 GeoTIFF tiles; per-tile SHA-256 recorded in `results/manifest_hashes.json` |
| **NOAA ENC Direct (`enc_general`) Cultural & Hazard Layers** | `https://encdirect.noaa.gov/arcgis/rest/services/encdirect/enc_general/MapServer/{15,26,29,42,45,59,69,83,84,88,98}/query` | 2026-11-24 | U.S. Government Public Domain (NOAA/NOS) | Vector points, lines & polygons (wrecks, obstructions, submarine cables, piles, dumping grounds, shoreline constructions) | Per-tile JSON cache SHA-256 recorded in `results/manifest_hashes.json` |

## 2. Arm 2 — German Western Baltic Sea (`0.25 m` & `0.50 m` BSH Multibeam Slope + WWII Munition Inventory)

| Dataset | Source URL | Retrieval Date | Licence | Size & Coverage | SHA-256 |
|---|---|---|---|---|---|
| **Feldens et al. (2026) — `Test_Areas.zip`** (Zenodo `10.5281/zenodo.19131526` / version record `20554225`) | `https://zenodo.org/api/records/20554225/files/Test_Areas.zip/content` | 2026-11-24 | CC-BY 4.0 | `52,339,239` bytes; 5 BSH `0.25 m/px` float32 slope GeoTIFFs + expert trawl masks (`0.717 km²`, Mecklenburg Bay, Arkona Basin, Kiel Bay, Fehmarn Belt) | `ddb6d258cc8a6ba4619c176f9fc5616eac7e4fedd2b89f1229b680c187c46847` |
| **Feldens et al. (2026) — `Time_Series.zip`** (Zenodo `10.5281/zenodo.19131526` / version record `20554225`) | `https://zenodo.org/api/records/20554225/files/Time_Series.zip/content` | 2026-11-24 | CC-BY 4.0 | `64,437,269` bytes; repeated 2024 & 2025 `0.50 m/px` BSH Fehmarn Belt slope GeoTIFFs (`~5.26 km²` valid seabed) | `e100714d5b7eb362a6567c92bd6cff04dd029b3fd3db5c76e6e1208639cd4754` |
| **PANGAEA Munition Pile Inventory in the German Baltic Sea (2017–2024)** (`10.1594/PANGAEA.988426`) | `https://doi.pangaea.de/10.1594/PANGAEA.988426?format=textfile` | 2026-11-24 | CC-BY 4.0 | `178,449` bytes; 484 georeferenced WWII munition-pile records (`0.01°` rounded) | `9d6f588bdde77a8025560c2f10c8d13527d03f40a425ecaad8393110c89f9a47` |



**Added after the spot check (2026-11-27).**

- **Checksums.** The checksums above match fresh downloads, and the Zenodo MD5s match the record. The 87 NOAA tiles and the chart file have per-file SHA-256s in `results/manifest_hashes.json`, not here; a rerun on 2026-11-27 reproduced every one.
- **The Baltic test-area grids are not sub-metre.** The Zenodo record says the data "were collected … at 1 m resolution (interpolated to 0.25 m)". Its authors' conference abstract (EGU26-13394) also describes 1 m grids.
- **The Fehmarn grids of 2024 and 2025** are 8-bit grey pictures of slope (grey palette, alpha band), with no physical scale.
- **The Zenodo record's manuscript.** It is titled "Spatial extent of trawl marks in the German Baltic Sea Basins based on bathymetric grids" and is described as submitted to *Anthropocene*. It is not a published paper, so "Feldens et al. (2026)" refers to the dataset, not to a peer-reviewed source.
- **The munition table** (PANGAEA.988426) covers 54.03–54.50° N, 10.28–11.00° E. It does not reach any Baltic area searched: the nearest pile is 8.9 km from Test4 and 24 km or more from the others.
- **The NOAA image service is a mosaic.** The export names no survey, so the service chooses which one shows. Its catalogue names several surveys as resampled to the stated grid (F00863 to 0.5 m, H12132 to 1 m, W00499 to 2 m), and the true detail may be coarser in places.
- **The Blinkerwall is in none of these grids.** Test2, the nearest, is about 7 km from the discoverers' sediment core beside the wall, not 3–5 km.
