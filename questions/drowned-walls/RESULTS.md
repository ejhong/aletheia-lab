# Results — Unmapped Stone Structures in Public Ice Age Seafloor Sonar (#84)

- **Issue:** #84 (`lane:data`)
- **Date:** 2026-11-24
- **Protocol lock:** `protocol.lock` (`0d14fc451820`, zero amendments)
- **Models & authorship:** Designed, coded, executed, and visually audited by Antigravity (Google DeepMind) on 2026-11-24, directed by Eugene Jhong. Independent second-vendor replication is pending (no second-vendor API keys in this environment).
- **Budget spent:** $0 (Public Domain NOAA NCEI `bag_bathymetry` ImageServer + NOAA ENC Direct `enc_approach` REST API)
- **Verification:** `4/4` synthetic unit tests passing (`analysis/test_drowned_walls.py`); cached NOAA 2 m GeoTIFF + ENC JSON archive SHA-256 `1de01f07d6d0c4c909cf5827183a0c385875c3cac5b25493838c252597efa661`.

---

## Plain-Language Verdict

**Null — no unmapped Ice Age stone walls, rectilinear corners, or ring enclosures detected across `34.23 km²` of real `2 m/pixel` public NOAA multibeam seafloor sonar.**

1. **Calibration gate passed cleanly on real `2 m` NOAA sonar:**
   - Recovered the real submerged stone toe of **Point Judith Harbor of Refuge Outer Breakwater** (`CTRL_PTJUDITH`: `L = 192.7 m`, `+1.45 m` local relief, `linearity = 0.9973`, unmasked; `CTRL_DELAWARE` had `0%` BAG coverage).
   - On `10` real noisy `2 m` NOAA shelf background tiles, recovered **`8 / 10` (`80%`)** planted **Blinkerwall-scale stone hunting walls** (`250 m × 4 m × 0.70 m`, parameterized to Geersen et al. 2024, *PNAS* `e2312008121`) while rejecting **`10 / 10` (`100%`)** planted `0.70 m` multibeam step-function mosaic seams.
   - As an unscripted real-world positive control, the detector also blindly locked onto a crisp **60 m long, 13.4 m tall sunken steel ship** at `−47.7 m` depth off Key West (`FL_KEYS_04`, `24.4539° N, −81.7711° W`, consistent with the 57 m *Cayman Salvage Master* artificial reef wreck, `343 m` from the nearest NOAA ENC obstruction polygon vertex).
2. **Zero prehistoric walls, corners, or rings across all 4 drowned Ice Age shelves (`40` tiles, `34.23 km²` valid seabed, `−10 m` to `−80 m` depth):**
   - Automated detection extracted `72` raw linear ridges (`L ≥ 60 m`, `lin ≥ 0.90`, `BPI ≥ +0.35 m`), **`0` rectilinear corners**, and **`0` closed ring enclosures**.
   - Pre-registered automated filters removed `33` of `72` ridges (`25` `SEAM_STEP`, `15` `SANDWAVE_PERIODIC`, `4` `AXIS_SEAM`, `1` `CHARTED_MODERN`).
   - Direct visual shaded-relief + BPI inspection of the remaining `39` unmasked ridges resolved **100% (`39/39`)** to natural geology or modern human activity: **`32`** dipping Miocene sedimentary bedrock strata (Monterey Formation hogbacks) on California's Santarosae shelf, **`3`** tidal sandbars in Block Island Sound, **`3`** historic dredged-material disposal hummocks in the NY Hudson Paleo-Channel, and **`1`** modern 60 m shipwreck off Key West.

---

## 1. Calibration Gate Results

| Calibration Test | Pre-Registered Target | Observed Result | Status |
|---|---:|---:|---|
| Real submerged stone breakwaters (`CTRL_DELAWARE`, `CTRL_PTJUDITH`) | `≥ 1 / 2` | **`1 / 2`** (`CTRL_PTJUDITH` recovered: `L = 192.7 m`, `max BPI = +1.45 m`, `lin = 0.9973`; `CTRL_DELAWARE` had `0%` BAG coverage) | **PASS** |
| Planted `250 m × 4 m × 0.70 m` Blinkerwall on real `2 m` NOAA seafloor noise | `≥ 8 / 10` (`≥ 80%`) | **`8 / 10` (`80.0%`)** recovered | **PASS** |
| Planted `0.70 m` step-function mosaic seams on real `2 m` NOAA noise | `10 / 10` (`100%`) rejected | **`10 / 10` (`100.0%`)** rejected by `SEAM_STEP` | **PASS** |
| Bonus blind recovery in search grid (`FL_KEYS_04`) | — | Crisp **60 m × 10 m × 13.4 m** sunken steel ship recovered at `24.4539° N, −81.7711° W` (`−47.7 m`) | **Verified sensitivity** |

---

## 2. Regional Scan & Visual Shaded-Relief Audit (`40` Tiles, `34.23 km²`)

| Drowned Ice Age Shelf Region | Tiles | Valid Seafloor (`km²`) | Raw Linear Ridges | Filtered (Seam / Sandwave / ENC) | Unmasked Ridges | Corners / Rings | Direct Visual Shaded-Relief Audit Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| **CA Santarosae (Channel Islands)** (`33.92°–34.03° N`) | 12 | `11.39` | 63 | 31 | 32 | `0 / 0` | **100% dipping Miocene bedrock strata:** sweeping parallel E–W Monterey Formation bedding-plane hogbacks and folded anticline noses (`CA_ANACAPA_01..04`, `CA_SROSA_05..06`). |
| **NY Hudson Paleo-Channel** (`40.39°–40.43° N`) | 10 | `10.39` | 3 | 0 | 3 | `0 / 0` | **Historic dredge-spoil disposal mounds:** irregular barge-dump craters and spoil berms adjacent to a multibeam survey boundary (`NY_HUDSON_02`). |
| **NE Block Island Sound** (`41.13°–41.17° N`) | 10 | `6.27` | 4 | 1 | 3 | `0 / 0` | **Natural tidal bedforms:** isolated `112 m` lens-shaped sand/gravel bar (`+0.61 m` relief) inside sweeping curved glacial moraine and tidal sand ribbons (`NE_BLOCK_10`). |
| **FL Keys Submerged Shelf** (`24.45°–24.49° N`) | 8 | `6.18` | 2 | 1 | 1 | `0 / 0` | **Modern 60 m sunken steel ship:** pointed bow, midships superstructure, and scour moat (`+13.4 m` relief at `−47.7 m`, consistent with the 57 m *Cayman Salvage Master* artificial reef wreck, `343 m` from nearest ENC polygon vertex) (`FL_KEYS_04`). |
| **Total** | **40** | **`34.23`** | **72** | **33** | **39** | **`0 / 0`** | **`0` unmapped prehistoric stone walls, corners, or enclosures** |

---

## 3. Key Methodological Lesson: Why Visual Hillshade Audit Matters

Automated 1D/connected-component geometric detectors are remarkably sensitive—our pipeline caught an `80%` share of `0.70 m`-high Blinkerwall-scale walls, the submerged Point Judith granite breakwater, and an unmasked 60 m Florida Keys shipwreck while rejecting `100%` of one-sided mosaic step seams. Yet in tectonically active coastal shelves like California's Channel Islands (`Santarosae`), **parallel dipping sedimentary rock strata spaced `50–150 m` apart** generate sharp, razor-straight linear ridges (`L = 200–550 m`, `linearity = 0.998`, `+1–3 m` relief) that fool automated linearity metrics and fall outside `12–60 m` sandwave filters. Rendering 3× vertically exaggerated hillshades + local BPI maps resolves those strata unambiguously in seconds—and demonstrates why any claim of "underwater walls or roads" on sonar must publish full contextual shaded-relief tiles rather than cropped zooms.

---

## 4. Limits & What This Does Not Settle

1. **Sampled fraction of drowned Ice Age shelves:** `34.23 km²` of `2 m` NOAA multibeam sonar is a tiny fraction of the ~20 million km² of continental shelf exposed at the Last Glacial Maximum. A null here rules out dense, prominent wall/enclosure networks across these four specific US shelf windows, not isolated sites elsewhere (such as the Western Baltic Sea's *Blinkerwall* or Lake Huron's Alpena–Amberley Ridge, which sit in low-energy basins with minimal wave erosion and sediment burial).
2. **Sediment burial & resolution floor:** Holocene marine muds and mobile sands bury low-relief (`< 0.5 m`) stone features across large parts of open Atlantic and Pacific shelves; sub-bottom seismic profiling and `< 0.5 m` AUV multibeam sonar are required to detect buried or cobble-scale features below `0.35 m` relief.
3. **Replication:** Code, NOAA REST query parameters, and GeoTIFF/ENC cache SHA-256 are reproducible with zero amendments; independent second-vendor replication is pending.

---

## What This Means

We built and calibrated an automated `2 m` seafloor sonar detector that reliably finds real submerged stone breakwaters, `70 cm`-tall Stone Age hunting walls planted on real multibeam noise (`8/10`), and even blindly rediscovered a `60 m` sunken steel ship at `−48 m` off Key West—while rejecting `100%` of multibeam mosaic step seams. Scanning `34.23 km²` of drowned Ice Age coastline across California's Santarosae shelf, Block Island Sound, the Hudson Paleo-Channel, and the Florida Keys turned up **zero unmapped prehistoric walls, rectilinear corners, or ring enclosures**. Every unmasked linear ridge resolved cleanly on shaded-relief sonar to dipping Miocene bedrock layers, tidal sandbars, historic dredge-spoil mounds, or a modern shipwreck.
