# Manifest — Unmapped Stone Structures in Public Ice Age Seafloor Sonar (#84)

All primary bathymetry and hydrographic chart overlays retrieved on **2026-11-24** into gitignored `questions/drowned-walls/data/` from public U.S. federal (NOAA) geospatial REST APIs (Public Domain / U.S. Government Works; exact GeoTIFF & ENC JSON archive SHA-256 recorded in `results/drowned_walls_summary.json`).

| Source | Endpoint / Identifier | Licence | Role |
|---|---|---|---|
| **NOAA NCEI BAG Bathymetry Mosaic ImageServer** | `https://gis.ngdc.noaa.gov/arcgis/rest/services/bag_bathymetry/ImageServer/exportImage` (`format=tiff`, `pixelType=F32`, `interpolation=RSP_NearestNeighbor`, `~2.0 m/px`) | Public Domain (NOAA / U.S. Gov) | High-resolution multibeam sonar depth grids (`~2 m` resolution) across 2 positive-control breakwaters and 40 pre-registered Ice Age paleo-shoreline tiles (`~42 km²`) |
| **NOAA ENC Direct to GIS (`enc_approach` MapServer)** | `https://encdirect.noaa.gov/arcgis/rest/services/encdirect/enc_approach/MapServer/{36,39,89,103,118,119,143,161,163,169,172}/query` | Public Domain (NOAA / U.S. Gov) | Official nautical chart overlays of modern shipwrecks, obstructions, submarine cables, submarine pipelines, and breakwaters/shoreline constructions for automated false-positive masking |

### Reference Archaeological Benchmark
- **Blinkerwall (Bay of Mecklenburg, Western Baltic Sea):** Geersen et al. (2024), *PNAS* 121(8): e2312008121 (`https://doi.org/10.1073/pnas.2312008121`) — `971 m` long, `< 1 m` high (`~0.5–1.0 m`), `~2–3 m` wide submerged Stone Age reindeer hunting wall at `−21 m` water depth, used to parameterize our planted synthetic hunting-wall sensitivity test on real 2 m NOAA multibeam seafloor noise.
