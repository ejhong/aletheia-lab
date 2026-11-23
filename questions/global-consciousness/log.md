# Log: random-number generators and world events (#47)

## 2026-11-23: start (Claude Fable 5.2)

- Eugene asked for #47 to be run after #60. Marked active.
- **Data.** The project's archive is public at global-mind.org: one file per UTC day, every egg's trial sum each
  second. Days exist from 1999 to 2025-10-31, with gaps after 2015 (most of 2024; the ends of 2018, 2021, 2023).
  The server is slow; files are fetched in ranged pieces.
- **The project's recipe and registry** read from its own pages. The formal series ran to December 2015: 500
  events, combined score 7.31, a mean of 0.33 per event.
- **Events by rule.** Four calendar days the registry used three or more times as full UTC days, each year
  2016–2025; and every earthquake with 100 or more deaths in NOAA's database. 65 candidates, 58 with data.
  Built without reading network data.
- **Program and tests** written; tests pass on made-up data. No 2016–2025 network data parsed yet.
- **Review, two rounds, two vendors** (`review/README.md`). The standardising was rebuilt (egg spreads from a
  year of control windows), the control-triggered switch of tests removed, overlap rules added.
- **Validation** on six of the project's own formal events of 2011–2015: our scores are within about 0.4 of the
  published ones, one exact (`explore/validation.json`).
- **Download** of the 156 day files finished; each has the server's stated length and decompresses fully.
