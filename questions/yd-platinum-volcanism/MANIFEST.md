# Data manifest

All primary public datasets were downloaded on 2026-11-23 (UTC) into the git-ignored `data/` folder.

| Name | URL | Retrieved (UTC) | Licence | SHA-256 | Notes |
|---|---|---|---|---|---|
| GISP2 deep-core major ions (`data/noaa/iond.txt`) | <https://www.ncei.noaa.gov/pub/data/paleo/icecore/greenland/summit/gisp2/chem/iond.txt> | 2026-11-23 | NOAA WDS Paleoclimatology: public, cite contributors | `a7a448cb5c22ea44c983ea2168391a6a35d337706d815fce5105305349c68f7f` | Mayewski et al. (1997, *JGR* 102:26345–26366). GISP2 `Na+`, `NH4+`, `K+`, `Mg2+`, `Ca2+`, `Cl-`, `NO3-`, `SO4^2-` vs. top/bottom depth (m). |
| GISP2 2-m `δ¹⁸O` (`data/noaa/gispd18o.txt`) | <https://www.ncei.noaa.gov/pub/data/paleo/icecore/greenland/summit/gisp2/isotopes/gispd18o.txt> | 2026-11-23 | NOAA WDS Paleoclimatology: public, cite contributors | `0f1a22aa1ad38ae08ddeedeb68a20bbcb8c8de75ac757fa977025dc5690c80c9` | Grootes & Stuiver (1997, *JGR* 102:26455–26470). GISP2 `δ¹⁸O` vs. top depth (m). |
| GICC05 synchronized 20-yr NGRIP/GRIP/GISP2 `δ¹⁸O` & `Ca²⁺` (`data/noaa/gicc05-calcium-20yr.txt`) | <https://www.ncei.noaa.gov/pub/data/paleo/icecore/greenland/summit/ngrip/gicc05-calcium-20yr.txt> | 2026-11-23 | NOAA WDS Paleoclimatology: public, cite contributors | `b78ed8921793f8404e9cc0aaffedca3dba75ec32a2793902c9f424fe1debab32` | Rasmussen et al. (2008). 11,620–32,440 yr b2k (20-yr grid) with GISP2, GRIP, and NGRIP2 depths on GICC05. |
| GICC05 NGRIP/GRIP/GISP2 match points (`data/noaa/gicc05-match-points.txt`) | <https://www.ncei.noaa.gov/pub/data/paleo/icecore/greenland/summit/ngrip/gicc05-match-points.txt> | 2026-11-23 | NOAA WDS Paleoclimatology: public, cite contributors | `08132900e2c7ff7760753cf5c5df29799c6306e44daad111c8f3a8c6665a9afe` | Volcanic/ECM match points linking NGRIP, GRIP, and GISP2 depths. |
| Lin et al. (2022) 60–9 ka polar volcanic sulfate catalog (`data/copernicus/lin2022-supplement.zip`) | <https://cp.copernicus.org/articles/18/485/2022/cp-18-485-2022-supplement.zip> | 2026-11-23 | CC-BY-4.0 | `3d9f86cc41b809aa7ca58a8d89dcbd280df8cd2e1286c34f27330e343614f486` | Lin et al. (2022, *Clim. Past* 18:485–506). Contains `Supplementary tables.xls` (Greenland, Antarctic, and bipolar volcanic eruptions 60–9 ka b2k). |
| Svensson et al. (2020) bipolar volcanic synchronization (`data/copernicus/svensson2020-supplement.zip`) | <https://cp.copernicus.org/articles/16/1565/2020/cp-16-1565-2020-supplement.zip> | 2026-11-23 | CC-BY-4.0 | `c971870ec58492d09f826a7a6b46ab1a3daee0e64d141cc9c12cace91f1fc43c` | Svensson et al. (2020, *Clim. Past* 16:1565–1580). Contains `Bipolar supplementary tables ver 2020-07-16.xlsx` (82 bipolar volcanic tie points across Greenland & Antarctica). |
| Sigl et al. (2021) YD volcanic stratospheric sulfur injection (`data/pangaea/930557.tab`) | <https://doi.pangaea.de/10.1594/PANGAEA.930557?format=textfile> | 2026-11-23 | CC-BY-4.0 | `15aa075f299f430b966da8da83abaf1eb5c90efed8a00ff2d2c30a62229e1d2a` | Sigl et al. (2021) / Abbott et al. (2021, *QSR*). Reconstructed VSSI for 30 eruptions > 1 Tg S around YD inception. |

## Published event table (committed in folder)

- `events.tsv` (`7b9c572a5f6ae8e423ca71e443dec7f01bc4370b6fe5cf037dd8485da14ab3a6`): Identical copy of `questions/cooling-ammonium/events.tsv`, transcribed from Rasmussen et al. (2014), *Quaternary Science Reviews* 106:14–28, Table 2.

## Published platinum horizon (from Petaev et al. 2013, *PNAS* 110:12917–12920; cited via open summaries/Green et al. 2025)

- GISP2 depth span of Pt anomaly: `1712.375` to `1712.000 m`, peak sample `1712.250–1712.125 m` (midpoint `1712.1875 m`, ~14 yr rise + ~7 yr decay; Petaev et al. 2013 body paywalled, exact depths cross-verified against open-access Svensson et al. 2020 and Green et al. 2025 *PLOS One* `doi:10.1371/journal.pone.0331811`).

Tools: Python 3.12, `numpy==2.3.5`, `xlrd` (`python3-xlrd`).

## Analysis scripts (frozen at lock)

| File | SHA-256 |
|---|---|
| `analysis/ptvolc.py` | `0a8982d4f74a4a85146c15404eff2aad00e0934a315b3e716047760d4479e00a` |
| `analysis/test_ptvolc.py` | `ac52d238b0651c2a4d9355c7527ccfccfaa1085e1bdcafa46310a684473fca47` |
