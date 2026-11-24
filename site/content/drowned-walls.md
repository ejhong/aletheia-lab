---
summary: Automated 2 m/pixel NOAA multibeam sonar scan across 34.23 km² of drowned Ice Age shelves (CA Santarosae, Block Island Sound, Hudson Paleo-Channel, FL Keys), calibrated on real breakwaters and planted Blinkerwall walls; zero unmapped prehistoric walls found.
verdict: Null — zero unmapped Ice Age stone walls or enclosures across 34.2 km² of 2 m NOAA sonar
result: Calibrated on real 2 m NOAA multibeam noise, our geometric ridge detector recovers the Point Judith submerged stone breakwater (193 m), 8/10 planted 0.70 m Blinkerwall-scale hunting walls, and blindly locks onto a 60 m sunken steel ship off Key West while rejecting 10/10 mosaic step seams. Across 40 pre-registered Ice Age paleo-shoreline tiles (34.23 km² valid seabed, −10 m to −80 m depth) in California, New England, New York, and Florida, zero rectilinear corners, zero ring enclosures, and zero unmapped prehistoric stone walls survive automated filtering and direct shaded-relief visual audit; all 39 unmasked ridges resolve visually to dipping Miocene bedrock strata (32), tidal sandbars (3), dredge-spoil mounds (3), or the modern Key West wreck (1).
dek: Real submerged Stone Age walls like the Baltic Sea's 1 km Blinkerwall do exist underwater. Scanning 34 km² of public 2 m NOAA seafloor sonar across four drowned Ice Age coasts, do any unmapped stone walls or enclosures turn up?
updated: 2026-11-24
---

{{figure: drowned-walls/tiles}}

## The idea

During the Last Glacial Maximum, roughly 20 million km² of coastal shelf sat above sea level. In 2024, marine geophysicists discovered the **Blinkerwall**—a real 971-meter-long, `< 1 m`-high Stone Age reindeer hunting wall 21 meters underwater in the Baltic Sea—using multibeam sonar. Hydrographic agencies like NOAA have already published huge public mosaics of `1–2 m` multibeam bathymetry (`bag_bathymetry`) collected for navigation safety, not archaeology.

Before downloading a single search tile, we locked a geometric wall-and-enclosure detector (`BPI ≥ +0.35 m`, length `≥ 60 m`, width `≤ 20 m`, linearity `≥ 0.90`, plus rectilinear corner and ring-enclosure checks) paired with automated filters for one-sided sonar mosaic seams (`SEAM_STEP`), periodic sandwave trains (`SANDWAVE_PERIODIC`), and charted modern wrecks, cables, and pipelines from **NOAA ENC Direct**. We calibrated it on real stone breakwaters and 10 Blinkerwall-scale walls (`250 m × 4 m × 0.70 m`) planted directly onto real 2 m NOAA seafloor noise, then scanned **40 pre-registered tiles (`34.23 km²` valid seabed)** across four drowned Pleistocene shelves (`−10 m` to `−80 m` depth): California's **Santarosae** mega-island shelf, **Block Island Sound**, the **Hudson Paleo-Channel**, and the **Florida Keys**.

## What the real 2 m sonar images show

**The detector clearly sees real submerged walls and wrecks—and finds zero unmapped Ice Age stone structures across all 34.23 km².**

- **Calibration passed:** It cleanly recovered the submerged stone toe of **Point Judith Outer Breakwater** (`192.7 m`, `+1.45 m` relief, `linearity = 0.9973`), recovered **`8 / 10` (`80%`)** of planted `0.70 m` Blinkerwall drive-lanes on real 2 m NOAA noise, and rejected **`10 / 10` (`100%`)** of planted `0.70 m` step-function mosaic seams.
- **Bonus blind positive control:** In Florida (`FL_KEYS_04`, `24.4539° N, −81.7711° W`), the detector blindly locked onto a crisp **60 m long, 13.4 m tall sunken steel ship** at `−47.7 m` depth (bow, superstructure, and scour moat unmistakable on shaded relief—consistent with the 57 m *Cayman Salvage Master* artificial reef wreck, `343 m` from the nearest NOAA ENC polygon vertex).
- **Direct visual audit of all 39 unmasked ridges:** Inspecting the real 2 m shaded-relief + BPI imagery resolves every single candidate cleanly with zero ambiguity—**32** parallel dipping Miocene sedimentary rock ledges off California's Channel Islands (even showing an eroded anticline fold nose), **3** natural tidal sandbars in Block Island Sound, **3** historic NY Bight dredge-spoil dump hummocks, and **1** modern Key West wreck. Toggle through all six real sonar panels below:

{{figure: drowned-walls/sonar_gallery}}

## From 72 raw linear ridges to zero unmapped Ice Age walls

Automated filtering removed `33` of `72` raw linear ridges (`25` one-sided mosaic step seams, `15` periodic sandwaves, `4` raster-axis seams, `1` ENC-charted feature). Zero rectilinear corners (`75°–105°`) and zero closed ring enclosures (`25–200 m` diameter) appeared anywhere across the 40 tiles:

{{figure: drowned-walls/pipeline_funnel}}

## What this does not settle

- **Coverage scale.** `34.23 km²` is a pilot-scale transect across four US shelves, not an exhaustive scan of the world's 20 million km² of drowned Ice Age shelf. Low-energy inland seas like the Western Baltic and Great Lakes remain far better preservation environments than wave-swept open-ocean shelves.
- **Buried or cobble-scale features.** Open-shelf Holocene mud and sand readily bury stone features `< 0.5 m` tall; detecting buried paleolandscapes requires sub-bottom seismic profiling and `< 0.5 m` AUV multibeam sonar.
- **Independent replication.** Code, NOAA API queries, and GeoTIFF/ENC archive hashes are reproducible with zero amendments; second-vendor replication is pending.

Read the full pre-registered [protocol](https://github.com/ejhong/aletheia-lab/blob/main/questions/drowned-walls/protocol.md) and [results](https://github.com/ejhong/aletheia-lab/blob/main/questions/drowned-walls/RESULTS.md).
