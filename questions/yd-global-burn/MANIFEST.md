# Data manifest

All files were downloaded on 2026-11-23 (UTC) into the git-ignored `data/noaa/` folder.

| Name | URL | Retrieved (UTC) | Licence | SHA-256 | Notes |
|---|---|---|---|---|---|
| Taylor Glacier deglacial CO₂ & δ¹³C-CO₂ (`taylor2016d13co2.txt`) | <https://www.ncei.noaa.gov/pub/data/paleo/icecore/antarctica/taylor/taylor2016d13co2.txt> | 2026-11-23 | NOAA WDS Paleoclimatology: public, cite contributors | `02d834658dddd984d8c337526cd499236c3a4ff8edcf009aab7997d76a01ed6a` | Bauska et al. 2016 (*PNAS*, doi:10.1073/pnas.1513868113). 61 rows, 10,919–22,330 cal BP. |
| Taylor Glacier glacial & deglacial CO₂, N₂O & δ¹³C-CO₂ (`taylor2018d13co2.txt`) | <https://www.ncei.noaa.gov/pub/data/paleo/icecore/antarctica/taylor/taylor2018d13co2.txt> | 2026-11-23 | NOAA WDS Paleoclimatology: public, cite contributors | `84e81f0bcb5ef9f2f7ef559e2129f1d194caf5820103e8bd7099d58c0ee25abc` | Bauska et al. 2018. 114 rows: 10,919–22,330 cal BP (all 61 rows of 2016) + 34,688–46,441 cal BP. |
| WAIS Divide CO₂ (`antarctica2015co2wais-noaa.txt`) | <https://www.ncei.noaa.gov/pub/data/paleo/icecore/antarctica/antarctica2015co2wais-noaa.txt> | 2026-11-23 | NOAA WDS Paleoclimatology: public, cite contributors | `4f5adea49770cbbbad3439645439189d431c2df5e418e18fc587bc0bca81db0a` | Marcott et al. 2014 / Bereiter et al. 2015 (doi:10.1002/2014GL061957). 432 rows, 10–23,030 cal BP; 24 yr median spacing across 10–22 ka. |
| Antarctic 155 kyr δ¹³C-CO₂ compilation (`eggleston2016d13co2-noaa.txt`) | <https://www.ncei.noaa.gov/pub/data/paleo/icecore/antarctica/eggleston2016d13co2-noaa.txt> | 2026-11-23 | NOAA WDS Paleoclimatology: public, cite contributors | `c493a92102b38c04ee31183ea9e40be244341717837b4b17c06085c97f49e9c8` | Eggleston et al. 2016. Monte Carlo average of 3 Antarctic cores (EDC, EDML, Talos Dome), 1,506 rows on a 100 yr grid, 600–155,000 cal BP. |
| Global Charcoal Database v3 (`GCD3_PUBLIC_VERSION_2013_01-Oct-2013.mdb`) | <https://www.ncei.noaa.gov/pub/data/paleo/firehistory/charcoal/gcd/GCD3_PUBLIC_VERSION_2013_01-Oct-2013.mdb> | 2026-11-23 | NOAA WDS Paleoclimatology / GPWG: public, cite contributors | `f98ec9736b998c52f402a4406eed46c45802f8584a5bb85b3efd2131e8c6ce43` | Marlon et al. 2016 (*Biogeosciences*, doi:10.5194/bgd-12-18571-2015). 736 sites, 120,154 samples, 134,748 charcoal records, 4,998 dating points. |
| GCD3 readme (`readme_gcd.txt`) | <https://www.ncei.noaa.gov/pub/data/paleo/firehistory/charcoal/gcd/readme_gcd.txt> | 2026-11-23 | NOAA WDS Paleoclimatology | `469e7f3435397cb96c4f937dbe3b8b0d4e853ab65dfb278d3a32b5d6abd304a7` | Documentation and citation for GCD3. |

Tools: Python 3.12, `numpy==2.3.5`, and `mdbtools` (`mdb-export` 1.0.0) to export tables from the `.mdb` file into `data/gcd_csv/`.

## Analysis scripts (frozen at lock)

| File | SHA-256 |
|---|---|
| `analysis/burn.py` | `fc78e688927b654996573730057e2af461edf3760db273605d43f4e604a0a2ec` |
| `analysis/test_burn.py` | `af91d25474d5af8af968884e388905bceb13796256bdc5ab3bbf1f2f1eac41da` |
