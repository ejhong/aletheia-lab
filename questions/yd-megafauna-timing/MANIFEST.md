# Data Manifest — `yd-megafauna-timing` (Issue #116)

All datasets are public, open-access, and re-downloadable directly from the URLs below. Raw downloaded files live git-ignored under `questions/yd-megafauna-timing/data/`.

## 1. Radiocarbon Calibration Curve (`IntCal20`)

- **File:** `data/intcal20.14c`
- **Source:** Reimer, P. J., et al. (2020). *The IntCal20 Northern Hemisphere radiocarbon age calibration curve (0–55 cal kBP).* **Radiocarbon** 62(4):725–757. Distributed via `rintcal` (`https://raw.githubusercontent.com/Maarten14C/rintcal/master/inst/extdata/3Col_intcal20.14C`).
- **Retrieval date:** `2026-11-23`
- **Licence:** Public scientific reference curve / GPL-2+ (`rintcal`).
- **SHA-256:** `0e03064baac546e7b67fca62b8e2365deabd8ee0a66881ad93aeb83e1c423eed`

## 2. Direct North American Megafauna Radiocarbon Dates

- **Primary file:** `data/broughton2018_s1.xlsx` (`521` directly dated individual extinct Late Pleistocene megafauna from contiguous US & adjacent southern Canada, all vetted to Barnosky & Lindsey quality `Score 11–12`: `343` AMS `Score 12` and `178` conventional `Score 11`, with material dated and raw `RCYBP ± Error`).
  - **Source:** Broughton, J. M., & Weitzel, E. M. (2018). *Population reconstructions for humans and megafauna suggest mixed causes for North American Pleistocene extinctions.* **Nature Communications** 9:5441 (`PMC6303330`), Supplementary Data 1 (`https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-018-07897-1/MediaObjects/41467_2018_7897_MOESM4_ESM.xlsx`).
  - **Retrieval date:** `2026-11-23`
  - **Licence:** CC-BY-4.0
  - **SHA-256:** `1cbc3096acd912714ef3f5f0c063ccc33a39e5e2dde7ec40a800a47c7fa7dc80`
- **Cross-check file:** `data/stewart2021_s1.xlsx` (`520` rows; Stewart, Carleton & Groucutt 2021, *Nature Communications* 12:965, `PMC7886903`, `https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-021-21201-8/MediaObjects/41467_2021_21201_MOESM4_ESM.xlsx`).
  - **Retrieval date:** `2026-11-23`
  - **Licence:** CC-BY-4.0
  - **SHA-256:** `6be3b1700283a324bf7cef3718ce19631a3f3be5d67547886fdfebd6c5a598c8`

## 3. North American Lake-Sediment *Sporormiella* Dung-Fungus Records (Neotoma v2 API)

- **Endpoint:** `https://api.neotomadb.org/v2.0/data/downloads/<datasetid>` (Neotoma Paleoecology Database, CC-BY-4.0; retrieved `2026-11-23`, stored git-ignored in `data/neotoma/ds_<datasetid>.json`).
- **Pre-registered selection query:** All North American (`24–72°N`, `−168 to −52°E`) pollen datasets containing `Sporormiella` (`units = NISP`, `elementtype = spore`) whose metadata age span covers `≥ 14,500` to `≤ 11,500 BP` (`19` downloaded), filtered objectively before inspecting any spore percentages to datasets with a calibrated chronology, `≥ 10` samples inside `17,000–10,000 cal BP`, and `≥ 4` nonzero *Sporormiella* samples inside `17,000–10,000 cal BP` (**11 qualifying cores** across 7 US states):

| Dataset ID | Site Name | Location | Samples (`17–10 ka`) | Nonzero *Sporormiella* (`17–10 ka`) |
|---:|---|---|---:|---:|
| `14957` | Appleman Lake | Indiana (`41.62°N, 85.21°W`) | `56` | `39` |
| `17717` | Silver Lake | Ohio (`40.35°N, 83.81°W`) | `49` | `47` |
| `19937` | Spicer Lake | Indiana (`41.76°N, 86.52°W`) | `43` | `42` |
| `45695` | Triangle Lake Bog | Ohio (`41.12°N, 81.26°W`) | `79` | `35` |
| `61900` | Mono Lake | California (`37.99°N, 119.05°W`) | `52` | `27` |
| `16175` | Binnewater Pond | New York (`41.41°N, 74.55°W`) | `29` | `24` |
| `16179` | Otisville | New York (`41.47°N, 74.53°W`) | `16` | `15` |
| `46645` | Lower Paintrock Lake | Wyoming (`44.39°N, 107.38°W`) | `36` | `14` |
| `47259` | Hall's Cave | Texas (`29.93°N, 99.42°W`) | `17` | `8` |
| `3056` | Como Lake | Colorado (`37.57°N, 105.51°W`) | `10` | `7` |
| `15876` | Tulare Lake | California (`36.03°N, 119.82°W`) | `10` | `4` |

*(The remaining 8 downloaded North American Late-Glacial Neotoma datasets — `517` Crane Lake, `3054` Head Lake, `3060` Bechan Cave, `15088` Anderson Pond, `16054` Little Willow Lake, `16177` Hyde Park, `16181` Pawelski Farm, `40111` White Pond — fail the pre-registered sample-density or calibrated-chronology cutoff and are excluded from primary statistics while documented transparently.)*

## 4. Pinned Software Versions

- Python `3.12.16`, `NumPy 2.3.5`, `SciPy 1.18.1` (standard-library XML/ZIP parsing for `.xlsx` — zero external spreadsheet dependencies).
