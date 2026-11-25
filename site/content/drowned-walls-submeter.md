---
summary: Sub-meter to 2 m public sonar hunt across 21.98 km² of Lake Huron's Alpena–Amberley Ridge (0.50–2.0 m NOAA BAG) and the German Western Baltic (0.25–0.50 m BSH multibeam); all 4 calibration gates passed and zero unmapped prehistoric stone walls survived visual audit.
verdict: Null — zero unmapped prehistoric stone walls across 22.0 km² of sub-meter Lake Huron & Western Baltic sonar
result: Moving from 2 m ocean shelves (#84) to 0.25–2.0 m public sonar inside the exact two basins where genuine ~9,000–11,000-year-old submerged Stone Age boulder walls exist, our locked pipeline passed all 4 calibration gates with zero amendments—recovering real Thunder Bay shipwrecks at 50 cm, 11/12 (92%) planted 0.50 m Lake Huron caribou drive-lanes, 8/10 planted Baltic walls, and rejecting 11/12 mosaic seams and 10/10 single-year trawl scars. Across 16.49 km² of Lake Huron (100% of hit tiles visually audited) and 5.49 km² of Western Baltic seabed, zero unmapped prehistoric walls, drive-lanes, or hunting blinds survive; Lake Huron hits resolve to Devonian limestone scarps and karst (31), glacial moraines (8), and swath edges (4), while the Baltic scan flags multi-year persistent otter-board trawl scars in Fehmarn Belt plus one untrawled 54 m wreck-and-scour anomaly in Kiel Bay (54.5531° N, 10.2373° E).
dek: Real Stone Age hunting walls sit underwater in Lake Huron and the Western Baltic. Scanning 22 km² of public 25 cm to 2 m seafloor sonar right in those two basins, do any unmapped prehistoric stone structures turn up?
updated: 2026-11-24
---

{{figure: drowned-walls-submeter/tiles}}

## The idea

Our first seafloor scan (`#84`, 2 m NOAA sonar across four U.S. ocean shelves) found zero unmapped Ice Age walls, with one obvious caveat: wave-swept open-ocean shelves at `2 m/pixel` are a tough place to preserve or resolve `< 1 m`-tall Stone Age boulder alignments.

So we went straight to the **only two basins on Earth where genuine ~9,000–11,000-year-old submerged Stone Age stone hunting structures are already proven to exist**, at **4× to 64× finer pixel density**:

1. **Lake Huron — Alpena–Amberley Ridge & Thunder Bay Shelf (`16.49 km²` valid seabed, `0.50 m`, `1.00 m`, and `2.00 m` NOAA NCEI BAG elevation + bathymetric LiDAR):** Dry land during the Lake Stanley lowstand (~9,900–7,500 cal BP), where archaeologists John O'Shea and Ashley Lemke documented 9,000-year-old caribou stone drive-lanes and hunting blinds in cold freshwater preservation, masked against NOAA `enc_general` shipwrecks and hazards.
2. **German Western Baltic Sea (`5.49 km²` valid seabed, `0.25 m` and `0.50 m` BSH multibeam slope grids, CC-BY 4.0 `10.5281/zenodo.19131526`):** Dry land during the Preboreal/Ancylus lowstand right around Geersen et al.'s 2024 *Blinkerwall*, combining five `0.25 m/px` expert trawl-masked test areas (Mecklenburg Bay — one ~4 km from *Blinkerwall* — Kiel Bay, Arkona Basin, Fehmarn Belt) with **`4.95 km²` of repeated `2024` and `2025` Fehmarn Belt `0.50 m` sonar** where taking the temporal minimum `min(2024, 2025)` strips out single-year bottom-trawl scars while preserving static seafloor structures.

## Calibration: all four locked gates passed

Before trusting a single scan result, the pipeline passed all four pre-registered quantitative calibration gates on real seafloor noise with zero amendments:

{{figure: drowned-walls-submeter/calibration_gates}}

## What the real sub-meter sonar images show

Inspecting **100% of all 18 hit-bearing Lake Huron tiles** (`43` unmasked linear ridges, `1` hollow ring, `1` V-funnel) and all Western Baltic `0.25 m` anomalies plus top `0.50 m` `2024 ∩ 2025` persistent hits resolves every single detection visually:

- **Lake Huron (`16.49 km²`, `0.50–2.0 m`):** Real sunken wooden and steel shipwrecks stand out with razor clarity (`std(BPI) = 5.3 cm` on `50 cm` lakebed), and `11/12` planted `50 cm`-tall caribou drive-lanes jump straight off the seabed. Yet every unmasked natural detection resolves visually to **Devonian limestone escarpments, paleo-mesas, and fractured karst pavement (`31` ridges + the `61.6 m` karst hollow and `21.8°` joint V-funnel)**, **glacial cobble/moraine swells (`8`)**, or **sonar swath edges (`4`)**.
- **Western Baltic (`5.49 km²`, `0.25–0.50 m`):** `Test1`, `Test3`, and `Test5` are cleanly empty; `Test2` (~4 km from *Blinkerwall*) has only two raster-edge artifacts; and **`Test4` (Kiel Bay, `54.5531° N, 10.2373° E`)** turns up one genuine untrawled **`54 m` curved obstruction (`14.6°` slope) with a flared comet-mark sediment wake and `~16 m × 5 m` hull/debris object** avoided by surrounding trawlers (visually consistent with a modern small wreck or heavy obstruction). On the `4.95 km²` Fehmarn Belt `2024 ∩ 2025` overlap, single-year trawl marks vanish, but heavy beaded otter-board trawl grooves persist longer than one year in cohesive mud and explain the persistent linear tracks.

Toggle through six real sub-meter sonar panels below:

{{figure: drowned-walls-submeter/sonar_gallery}}

## What this does not settle

- **Targeted academic AUV zones:** On Lake Huron, public NOAA BAG covers Thunder Bay and the western flank of the Alpena–Amberley Ridge (`W00499`), whereas O'Shea & Lemke's main documented caribou sites (`Drop 45` / `Area 1` / `Area 3`) lie farther southeast along the central ridge in academic AUV surveys not hosted in NOAA's public mosaic.
- **Cobble-scale walls at 2 m:** Single-cobble rows `< 0.5 m` wide require `≤ 0.5 m` elevation-plus-backscatter grids across the central ridge crest, not `2 m` navigation bathymetry.
- **Baltic raw elevation archives:** National German and PANGAEA binary multibeam elevation grids remain partially gated or slope-only in open mirrors; broader untrawled Western Baltic elevation sweeps will require open release of raw `≤ 0.5 m` BSH/IOW bathymetry plus sub-bottom profiles.
- **Independent replication:** Code, exact tile bounds, and SHA-256 archive hashes are reproducible with zero amendments; second-vendor replication is pending.

Read the full pre-registered [protocol](https://github.com/ejhong/aletheia-lab/blob/main/questions/drowned-walls-submeter/protocol.md) and [results](https://github.com/ejhong/aletheia-lab/blob/main/questions/drowned-walls-submeter/RESULTS.md).
