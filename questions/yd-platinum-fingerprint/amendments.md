# Amendments — `yd-platinum-fingerprint`

## Amendment 1 — 2026-11-24 (post-lock parser fix & sensitivity reporting)

- **Why:** After locking `protocol.md` (`c9ec33ecd9ad`) and running `analysis/pt_fingerprint.py`, inspection of parser row counts showed three purely technical issues:
  1. `parse_moore2019_white_pond()` returned `0` rows because `moore2019_s1.pdf` Table 3 (`p.43`) begins each row with a relative-depth interval string (`+44 to +46`, `-10 to -8`) ahead of the core midpoint depth (`165`–`248 cm`), which did not match the pre-lock regex `^(\d{2,3})`.
  2. `moore2017_s1.pdf` Tables 1–2 (`p.38–39`) are 21-column compressed raster images in which `tesseract-ocr` systematically drops decimal points (`0.3` → `03`). Rather than manually transcribing values (which would break programmatic reproducibility), these tables are excluded under the pre-registered OCR QA gate, leaving Moore et al. (2019) White Pond Table 3 (single-site, 6-column table) as our verified Tier-2 proponent continuous profile.
  3. In Pillar 2, Hall's Cave's nominal YDB-onset cluster (`151–155 cm`, `n = 6` samples including `HC16_03` at `¹⁸⁷Os/¹⁸⁸Os = 0.15`) carries calibrated age `13.008 ka`, missing the locked `13.0–12.6 ka` Pillar 2 window by `0.008 ka` (`8 years`), while Page-Ladson's YDB-base unradiogenic aliquot `36-30` (`851 cm`, `¹⁸⁷Os/¹⁸⁸Os = 0.51`) has `Ru = bdl` and was excluded from strict 6-HSE Pillar 1A.
- **What changed (before re-running):**
  1. Fixed the line-matching regex in `parse_moore2019_white_pond()` to parse the leading relative-depth interval and core midpoint depth (`165–248 cm`), retaining the exact locked `15%` `Pt/Pd` OCR QA gate.
  2. Added side-by-side **sensitivity outputs** (explicitly labelled `sensitivity` in `results/summary.json`, without changing ANY primary locked calculation or the locked verdict rule!):
     - Pillar 2 independent-column audit at `13.1–12.6 ka` for Hall's Cave (including the `13.008 ka` samples) alongside the locked `13.0–12.6 ka` primary audit.
     - Pillar 1A `5`-HSE (`Os, Ir, Pt, Pd, Re`) sensitivity for Page-Ladson sample `36-30` (`851 cm`, `¹⁸⁷Os/¹⁸⁸Os = 0.51`, `Ru = bdl`).
- **Effect on primary locked verdict:** None. All locked Pillar 1A/1B/2 primary numbers and the formal verdict (`ambiguous_or_mixed`) remain computed by the exact locked rules in `protocol.md`.
