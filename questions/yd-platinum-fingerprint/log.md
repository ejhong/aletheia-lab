# Lab log — `yd-platinum-fingerprint`

- **2026-11-24 (UTC):** Opened Issue `#120` (`lane:data`, `status:active`), created branch `q/yd-platinum-fingerprint` from `origin/main` (after merging PR `#119` for `#116`).
- **2026-11-24 (UTC):** Downloaded verified primary open-access datasets into git-ignored `data/`: Sun et al. (2020) `sun2020_sm.pdf`, Nana Yobo et al. (2026) `nanayobo2026_sm.pdf`, Chicxulub K–Pg `kpg2025_MOESM4.xlsx`, Green et al. (2025) `green2025_s001.docx`, Yudovskaya et al. (2008) `yudovskaya2008_kudryavy.pdf`, Moore et al. (2017) `moore2017_s1.pdf`, Moore et al. (2019) `moore2019_s1.pdf`, and Wonderkrater (2026) `wonderkrater2026.html`. Recorded SHA-256 checksums in `MANIFEST.md`.
- **2026-11-24 (UTC):** Performed strictly blinded schema & table-header verification only (no geochemical sample values, ratios, or peak counts inspected). Wrote `protocol.md`, `analysis/pt_fingerprint.py`, and `analysis/test_pt_fingerprint.py`.
