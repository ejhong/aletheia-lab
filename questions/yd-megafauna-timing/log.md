# Work Log — `yd-megafauna-timing` (Issue #116)

## 2026-11-23 — Pre-lock data discovery, blinded schema checks, and protocol design

- Marked Issue #116 `status:active` and branched `q/yd-megafauna-timing` from `origin/main` (`5d3b1a2`).
- Downloaded open primary datasets into git-ignored `data/`:
  - `IntCal20` (`3Col_intcal20.14C`, Reimer et al. 2020)
  - Broughton & Weitzel (2018, *Nat. Commun.* 9:5441, CC-BY-4.0) Supplementary Data 1 (`broughton2018_s1.xlsx`, 521 direct North American megafauna `¹⁴C` dates) + Stewart et al. (2021) cross-check table (`stewart2021_s1.xlsx`)
  - All `19` North American Late-Glacial *Sporormiella* pollen datasets from the Neotoma v2 REST API (`CC-BY-4.0`).
- Ran strictly blinded schema/coverage checks (ZERO spore curves, decline dates, or calibrated megafauna ages inspected):
  - Verified all 505 Neotoma `Sporormiella` entries use uniform `units='NISP'`, `elementtype='spore'`.
  - Applied pre-registered objective inclusion filter (`calibrated chronology`, `≥ 10` samples in `17–10 ka`, `≥ 4` nonzero *Sporormiella* samples in `17–10 ka`), yielding **11 qualifying cores** across 7 US states (`IN, OH, NY, TX, CO, WY, CA`), all with `100%` upland pollen (`TRSH+UPHE`) denominators.
  - Verified `23` extinct megafauna taxa in `broughton2018_s1.xlsx` (`9` with `n ≥ 16`).
- Wrote `MANIFEST.md`, `protocol.md`, `amendments.md`, `analysis/megafauna_timing.py`, and `analysis/test_megafauna.py`.
