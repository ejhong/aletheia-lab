# Data manifest

| Name | URL | Retrieved (UTC) | Licence | SHA-256 | Notes |
|---|---|---|---|---|---|
| GCP registry of formal events (`sources/pred_formal.html`) | <https://global-mind.org/pred_formal.html> | 2026-11-23 | © Roger Nelson 1998–2020, all rights reserved; kept here as the record of what was read | `ee5479c1b987e26d1a62d50e45c2c20dc5461f9fda32bf9a17cc15a240817820` | 512 rows in the rendered table; three more rows are inside HTML comments and are ignored |
| GCP published results (`sources/results.html`) | <https://global-mind.org/results.html> | 2026-11-23 | as above | `e13d7abe3365296fc58679c2b7cf8635618e35f25e4632b91883fee2bd1cb064` | 513 rows |
| GCP directory listings, 1998–2016, reduced to the days that have a file (`sources/available_days.txt`) | <https://global-mind.org/data/eggsummary/YYYY/> | 2026-11-23 | Not stated on the pages read; the project publishes the data for public use | `0181b88a4c27ba62d62f43d8bdb4db2c17d5556f553a2c6968b78be7967a54d7` | 6,696 days, from 1998-08-05 |
| GCP day files (`data/basketdata-YYYY-MM-DD.csv.gz`), the 868 days in `sources/days_needed.txt` | <https://global-mind.org/data/eggsummary/YYYY/basketdata-YYYY-MM-DD.csv.gz> | 2026-11-23 | as above | one per file in `sources/files.sha256` | Fetched by `analysis/fetch_data.py`; about 4 GB; not in git |

Pages of the project read for the method, on 2026-11-23: `results.html`, `pred_formal.html`, `analysis_chi.html`
under <https://global-mind.org/>. `gcpdata.html` was read for question #47.

Made from the two saved pages by `analysis/build_registry.py`:

| File | SHA-256 |
|---|---|
| `sources/registry.tsv` | `e52bc2b35d63a3c90ee6f9208d2766fcbaf210ec0763120cfd7bbd88f73150e3` |
| `sources/published.tsv` | `241f478fbd3e5584867a33a694d173fdcab186da21884d1091f635d48971de22` |
| `sources/matched.tsv` | `c8f6c6fe8181171b239eecc067b4303211f85b4bfd159b2df57dce1b71965c1c` |

Made from `sources/matched.tsv` and `sources/available_days.txt` by `analysis/build_windows.py`:

| File | SHA-256 |
|---|---|
| `windows.tsv` | `1a3cbf7f73ee8a563a739c01b67ef622510487c97a9fd0268270816bbbffdbd9` |
| `sources/blocked.tsv` | `2c0e74614dba509607c032ad5fd529dba8bd02d749ee2fdf7cc6d03de239970d` |
| `sources/days_needed.txt` | `9f47ac026acb5cb154cc9ae657900b29fa8a076b67500501cb720c22fd02696d` |

Software: Python 3.12.16, numpy 2.3.5 (the repository's `.venv`). The table-building scripts and the download
script use the standard library only.
