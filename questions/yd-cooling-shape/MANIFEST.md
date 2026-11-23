# Data manifest

All files were downloaded on 2026-11-23 (UTC) into the git-ignored `data/` folder (`data/noaa/` and `data/pangaea/`).

| Name | URL | Retrieved (UTC) | Licence | SHA-256 | Notes |
|---|---|---|---|---|---|
| GICC05 NGRIP 20-yr `δ¹⁸O` (`data/noaa/gicc05-60ka-20yr.txt`) | <https://www.ncei.noaa.gov/pub/data/paleo/icecore/greenland/summit/ngrip/gicc05-60ka-20yr.txt> | 2026-11-23 | NOAA WDS Paleoclimatology: public, cite contributors | `054011355f9562ea2550387ef7212895b8f8cdbb31c7a1af9a78d47684557ddd` | NGRIP dating group (2008). 3,000 rows, 20–60,000 yr b2k (20-yr grid). |
| GICC05 NGRIP/GRIP/GISP2 20-yr `δ¹⁸O` & `Ca²⁺` (`data/noaa/gicc05-calcium-20yr.txt`) | <https://www.ncei.noaa.gov/pub/data/paleo/icecore/greenland/summit/ngrip/gicc05-calcium-20yr.txt> | 2026-11-23 | NOAA WDS Paleoclimatology: public, cite contributors | `b78ed8921793f8404e9cc0aaffedca3dba75ec32a2793902c9f424fe1debab32` | Rasmussen et al. (2008). 1,042 rows, 11,620–32,440 yr b2k (20-yr grid), 3 Greenland cores synchronized on GICC05. |
| NGRIP 10–120 kyr temperature & accumulation (`data/noaa/ngrip2014temp.txt`) | <https://www.ncei.noaa.gov/pub/data/paleo/icecore/greenland/summit/ngrip/ngrip2014temp.txt> | 2026-11-23 | NOAA WDS Paleoclimatology: public, cite contributors | `5f6637d5c27f422817f399c6f911e856cf8cd48fc3d16962fad603723f1f5777` | Kindler et al. (2014, *Clim. Past* 10:887–902). 5,651 rows on `ageGICC05` (10–120 ka). |
| Antarctic 40 kyr 7-core surface temperature (`data/noaa/buizert2021-temp.txt`) | <https://www.ncei.noaa.gov/pub/data/paleo/icecore/antarctica/buizert2021/buizert2021-temp.txt> | 2026-11-23 | NOAA WDS Paleoclimatology: public, cite contributors | `0f2c7d653665b7ef81b4048ac43834135b0ff7aef0186c3493c43505b3ef489c` | Buizert et al. (2021, *Science* 372:1097–1101). 1,001 rows, 0–40,000 yr BP1950 (40-yr grid) across WD, EDML, EDC, TAL, SDM, SP, DF. |
| NGRIP 10-yr impurity means (`data/pangaea/935814.tab`) | <https://doi.pangaea.de/10.1594/PANGAEA.935814?format=textfile> | 2026-11-23 | CC-BY-4.0 | `b3ce78cce77d663875fd4ce664ab2831397752d636d70672094fb1bbd2841bba` | Erhardt et al. (2021, *ESSD* 14:1215–1231). 10,270–107,620 yr b2k (`Ca²⁺`, `Na⁺`, `NH₄⁺`, `NO₃⁻`). |

## Published event table (committed in folder)

- `events.tsv` (`7b9c572a5f6ae8e423ca71e443dec7f01bc4370b6fe5cf037dd8485da14ab3a6`): Identical copy of `questions/cooling-ammonium/events.tsv`, transcribed from Rasmussen et al. (2014), *Quaternary Science Reviews* 106:14–28, Table 2 (111 stadial/interstadial onsets on GICC05 from 11.4 ka to GS-26).

Tools: Python 3.12, `numpy==2.3.5`.

## Analysis scripts (frozen at lock)

| File | SHA-256 |
|---|---|
| `analysis/shape.py` | `08475608c8d310fc9e4ec7c167a92ad3c33ffe51aa9d5f727074dd74c1242ddc` |
| `analysis/test_shape.py` | `7348c6254b580dbfc811f99736276f961335f9a9e0a04d82a656f567aff2f1c0` |
