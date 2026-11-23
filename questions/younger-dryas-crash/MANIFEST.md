# Data manifest

Downloaded on 2026-11-23 (UTC) into the git-ignored `data/` folder.

| Name | URL | Retrieved (UTC) | Licence | SHA-256 | Notes |
|---|---|---|---|---|---|
| p3k14c archaeological radiocarbon database, release 2025.07 (`p3k14c_scrubbed_fuzzed.csv`) | <https://raw.githubusercontent.com/people3k/p3k14c/2025.07/inst/p3k14c_scrubbed_fuzzed.csv> | 2026-11-23 | Data CC-BY-4.0 (the repository's README); code MIT | `5c92b7ae96959bc2924409cf66a8919aac955a4abac5545fad26f3fb209eca0c` | 173,946 dates; 25.9 MB. Bird et al. 2022, *Scientific Data* 9:27; doi:10.5281/zenodo.6633635 |
| IntCal20 Northern Hemisphere calibration curve (`intcal20.14c`) | <https://intcal.org/curves/intcal20.14c> | 2026-11-23 | Published for use with citation: Reimer et al. 2020, *Radiocarbon* 62, doi:10.1017/RDC.2020.41 | `974a66649f2ac8a53e6c99e256b019ac6982f999b12dcf7193162d4c1c09168e` | 9,501 points, 0–55,000 cal BP |

Tools: Python 3.12 and numpy 2.3.5, in the virtual environment shared with question #31.

## Files as locked

| File | SHA-256 |
|---|---|
| `analysis/crash.py` | `476aa184f857911376353760a1fd2b32e3507bced714700469203249df9f522e` |
| `analysis/test_crash.py` | `9012630cf682152a221fe07805a294bafc928c2622017fdb97c3184f78e29a15` |

Used only in a check made after the result (`explore/later_drop.py`): the IntCal13 curve, <https://intcal.org/curves/intcal13.14c>, retrieved 2026-11-23 (Reimer et al. 2013).
