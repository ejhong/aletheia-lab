# Data manifest

| Name | URL | Retrieved (UTC) | Licence | SHA-256 | Notes |
|---|---|---|---|---|---|
| GCP day files (`data/basketdata-YYYY-MM-DD.csv.gz`), the days in `sources/days_needed.txt` | <https://global-mind.org/data/eggsummary/YYYY/basketdata-YYYY-MM-DD.csv.gz> | 2026-11-23 | Not stated on the pages read; the project publishes the data for public use | one per file in `sources/files.sha256` | Fetched by `analysis/fetch_data.py`; each file accepted only at the server's stated length and if it decompresses to the end. About 3 MB each; not in git. |
| GCP directory listings, 2016–2025, reduced to the days that have a file (`sources/available_days.txt`) | <https://global-mind.org/data/eggsummary/YYYY/> | 2026-11-23 | as above | in git | 3,058 days |
| NOAA NCEI Global Significant Earthquake Database, 2016–2025, 100 or more deaths (`sources/noaa_earthquakes_2016_2025_deaths_100_or_more.json`) | <https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/earthquakes?minYear=2016&maxYear=2025&minDeaths=100> | 2026-11-23 | US government work, public domain | in git | 25 events; fields kept: id, date and time, magnitude, deaths, country, location. doi:10.7289/V5TD9V7K |

Pages of the project read for the method and the registry, on 2026-11-23: `results.html`, `pred_formal.html`,
`analysis_chi.html`, `gcpdata.html`, `procedures.html`, `basket_CSV_v2.html` under <https://global-mind.org/>.

`events.tsv` is made from the two files in `sources/` by `analysis/build_events.py`.

Tools: Python 3.12 and numpy 2.3.5, in the virtual environment shared with question #31.

## Files as locked

| File | SHA-256 |
|---|---|
| `events.tsv` | `6a6ac1c23e549263b5f72fa101118d875de167c6e79845976117620807d11019` |
| `sources/files.sha256` | `5cbdda503626b254df4adfdd19631b882b78650cee663195d4228186b1cdab86` |
| `sources/available_days.txt` | `6be7e65ebe3404ad3cac18f7e11be65c11149c5a9e576224cb55b2b91a34cc96` |
| `sources/noaa_earthquakes_2016_2025_deaths_100_or_more.json` | `4d6bb97ddb5b2ead84a926500a49b6bb8e82c06fc955675f12c4ffe14cc11e51` |
| `analysis/netvar.py` | `089a9f828b43bdc85e1f80c84e333704e5fcc2ecf68df3f871ec3c106758f5b3` |
| `analysis/build_events.py` | `1660a8aed91f702e6f193eaa83c523120f99c3d43a49bb6cef9142ab8e262edb` |
| `analysis/test_netvar.py` | `27fc816d0cd25bd4e828ef8ee4934e0e5f1a8d40d3ed5fa0337e0c85db3ec08e` |
