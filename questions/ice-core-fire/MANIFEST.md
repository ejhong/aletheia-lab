# Data manifest

All files were downloaded on 2026-11-23 (UTC) into the git-ignored `data/` folder: PANGAEA files into
`data/pangaea/<number>.tab`, NOAA files into `data/noaa/`.

| Name | URL | Retrieved (UTC) | Licence | SHA-256 | Notes |
|---|---|---|---|---|---|
| NGRIP 10-year impurity means (`935814.tab`) | <https://doi.pangaea.de/10.1594/PANGAEA.935814?format=textfile> | 2026-11-23 | CC-BY-4.0 | `b3ce78cce77d663875fd4ce664ab2831397752d636d70672094fb1bbd2841bba` | Erhardt et al. 2021. The file's change note says its ammonium and nitrate columns were swapped until 2026-05-29. |
| NGRIP 1 mm impurity data (`935818.tab`) | <https://doi.pangaea.de/10.1594/PANGAEA.935818?format=textfile> | 2026-11-23 | CC-BY-4.0 | `be17fdbaa8866995ce9493faf0c82af41c98589cd0c77189339c8ee32e78c949` | 77 MB |
| NEEM 10-year impurity means (`935831.tab`) | <https://doi.pangaea.de/10.1594/PANGAEA.935831?format=textfile> | 2026-11-23 | CC-BY-4.0 | `22fc97d7c50af6badda2de4cfbe66a66fad5c6552c754575916ea8c24b1ab03f` | |
| NEEM 1 mm impurity data (`935837.tab`) | <https://doi.pangaea.de/10.1594/PANGAEA.935837?format=textfile> | 2026-11-23 | CC-BY-4.0 | `28b8aceefbb1370748e2ded65c799e401f94cf0c275ec61b921b2e2097a69973` | Downloaded, not used: no NEEM depth–age file was fetched. |
| GICC05 timescale, NGRIP depth every 20 years to 60 ka (`gicc05-60ka-20yr.txt`) | <https://www.ncei.noaa.gov/pub/data/paleo/icecore/greenland/summit/ngrip/gicc05-60ka-20yr.txt> | 2026-11-23 | NOAA WDS Paleoclimatology: public, cite contributors | `054011355f9562ea2550387ef7212895b8f8cdbb31c7a1af9a78d47684557ddd` | |
| GISP2 ions, deep core (`iond.txt`) | <https://www.ncei.noaa.gov/pub/data/paleo/icecore/greenland/summit/gisp2/chem/iond.txt> | 2026-11-23 | NOAA WDS Paleoclimatology: public, cite contributors | `a7a448cb5c22ea44c983ea2168391a6a35d337706d815fce5105305349c68f7f` | Mayewski et al. 1997 |

The PANGAEA collection is doi:10.1594/PANGAEA.935838 (Erhardt et al. 2021), described in Erhardt et al. 2022,
*Earth System Science Data* 14:1215–1231.

Tools: Python 3.12 and numpy 2.3.5, in the virtual environment shared with question #31.

## Programs as locked

| File | SHA-256 |
|---|---|
| `analysis/fire.py` | `d7ccdce54e60248600c85e9bc85891620bc859f6e3668b05bfb4ff73f0f0e21b` |
| `analysis/test_fire.py` | `3da951403d64de6813d543a19412238888db97aa10f59ab138eefb29a765c8e4` |
