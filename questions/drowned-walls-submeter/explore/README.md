# Exploratory Notes (Non-Evidence) — #143 (`drowned-walls-submeter`)

> **Label: EXPLORATORY ONLY — NOT EVIDENCE.** Per `AGENTS.md` §3, this folder documents pre-protocol data availability, format, coordinate, and noise-floor checks performed on 2026-11-24 before locking `protocol.md`. No candidate scanning was performed here.

## Summary of Pre-Protocol Checks

1. **Lake Huron NOAA NCEI `bag_bathymetry` ImageServer:**
   - Spatial query over Alpena–Amberley Ridge / Thunder Bay (`lon [-83.6, -81.8], lat [44.0, 45.5]`) verified 18 non-overview surveys, including native `0.50 m` (`H13652`, `F00862`, `F00863`), `1.00 m` (`H12132`, `H12133`, `H12964`, `H14139_LI`), and `2.00 m` mid-lake Alpena–Amberley Ridge (`W00499_2of2`, depths `-38 m` to `-82 m`).
   - Background noise floor on 3 quick wreck-control previews (`H13652`, `F00862`, `W00499`): `std(BPI) = 0.053 m` to `0.110 m` at `0.50–1.0 m/px`, with charted wrecks spiking `+1.25 m`, `+8.09 m`, and `+12.93 m`.
   - NOAA Great Lakes charted cultural features live in `enc_general` (not `enc_approach`): Layer 29 (`General.Wreck_point`) returned 47 charted wrecks in the Lake Huron box, including wrecks directly inside `H13652`, `F00862`, `H12132`, `W00499`, and `H14139`.

2. **Western Baltic Open Multibeam Data:**
   - `download.pangaea.de` binary GeoTIFF links currently return `HTTP 503` (`Please wait...` wait gate) and were therefore excluded.
   - Open CC-BY 4.0 Zenodo archive `10.5281/zenodo.19131526` (Feldens et al., 2026, direct ungated download) provides:
     - `Test_Areas.zip` (52.3 MB): 5 float32 `0.25 m/px` BSH multibeam slope GeoTIFFs (UTM 33N) in Mecklenburg Bay (`Test1` at `54.27°N, 11.49°E`; `Test2` at `54.17°N, 11.36°E`, ~3–5 km from *Blinkerwall*), Arkona Basin (`Test3`), Kiel Bay (`Test4`), and Fehmarn Belt (`Test5`), totaling `0.717 km²`, each paired with a human-annotated trawl-mark mask (`pixel == 76` = trawl mark, `255` = untrawled seabed).
     - `Time_Series.zip` (64.4 MB): repeated `0.50 m/px` Fehmarn Belt (`54.55°N, 10.77°E`) BSH slope GeoTIFFs from 2024 and 2025 (`~5.26 km²` valid seabed; `mode=PA` inverted grayscale where flat = light ~200–240, steep = dark ~0–130, alpha = 255 valid / 0 noData).
   - `10.1594/PANGAEA.988426` (`?format=textfile`, HTTP 200) provides 484 German Baltic WWII munition-pile coordinates (2017–2024, rounded to `0.01°`) for confounder flagging.
