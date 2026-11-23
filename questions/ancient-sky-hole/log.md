# Lab Log — The hole in the ancient sky (`ancient-sky-hole`)

## 2026-11-23 — Data Acquisition, Blind Structural Check, and Pre-Lock Validation

- Branched `q/ancient-sky-hole` from `main`.
- Downloaded three primary public astronomical catalogs from CDS/VizieR via the Harvard-Smithsonian CfA mirror (`vizier.cfa.harvard.edu`) into git-ignored `data/` and recorded exact URLs, licences, and SHA-256 hashes in `MANIFEST.md`:
  - Verbunt & van Gent (2012) *Almagest* (`J/A+A/544/A31/ptolema`, 1,028 rows, 48 constellations, 1,020 unique Hipparcos IDs with `I <= 3`).
  - ESA Hipparcos Main Catalogue (`I/239/hip_main`, `Vmag <= 7.0`, 15,544 rows, 15,537 with valid positions).
  - Yale Bright Star Catalogue 5th Rev. Ed. (`V/50/catalog`, 9,110 rows, for Bayer/Flamsteed labels only).
- Ran blind structural script `explore/structure.py`: confirmed northern-sky (`dec_J2000 > +20°`) completeness is 100.0% for `V < 2.0`, 97.4% for `[2.0, 3.0)`, 100.0% for `[3.0, 3.5)`, 87.5% for `[3.5, 4.0)`, 65.5% for `[4.0, 4.5)`, 31.1% for `[4.5, 5.0)`, 9.4% for `[5.0, 5.5)`, and 1.0% for `[5.5, 6.0)`. No southern-sky declinations or hole fits were inspected.
- Drafted pre-registered `protocol.md` specifying Vondrák et al. (2011/2012) long-term precession (`eraLtpequ`), precession-invariant northern ecliptic calibration (`β > +30°`), Model M1 (Kasten & Young 1989 airmass + Bennett 1982 refraction, `k_V = 0.25`), Model M2 (joint `k_V` profile), Model M3 (pure geometric spherical cap), Model M4 (unconstrained free-pole diagnostic), Spatial Block Bootstrap (`B = 500`, ~15° tiles), Leave-One-Constellation-Out jackknife, systematic envelope, and 3000 BCE decision rule.
- Ran `analysis/test_skyhole.py`: ALL TESTS PASSED (astrometry verified against Thuban at 2781 BCE `0.06°` and Vega at 12,001 BCE `2.69°`; 4-epoch synthetic sky recovery `-9600, -2500, -1200, +137` all within tolerance; patchy-sky spatial block bootstrap 95% CI properly covered true epoch).
- Ran `analysis/skyhole.py --decoy` (true synthetic `-1800, 35.0° N`): recovered `-1670 (1671 BCE), 35.30° N`, block-bootstrap 95% CI `[-2000, -1350]`, M4 free-pole off-track `0.44°`.
- Ready to commit pre-lock files, lock `protocol.lock` in its own commit, push to GitHub, and then run the locked analysis.

## 2026-11-23 — Locked Analysis Run and Post-Hoc Binary Check

- Committed pre-lock files (`703489f`), locked `protocol.md` (`4be6d43dc0bd`, commit `bc04372`), pushed `origin q/ancient-sky-hole`, verified `scripts/check.py`, and paused 2 seconds.
- Executed locked `python3 questions/ancient-sky-hole/analysis/skyhole.py`:
  - Primary M1 (`k_V = 0.25`, `all48`, `V <= 5.5`): `910 CE, 25.80° N`, `LL = −935.79` (anachronistic overshoot past `137 CE` caused by harsh extinction penalty on faint catalogued stars in Ara/Argo/Centaurus vs. omitted bright stars in Grus/Phoenix).
  - Spatial Block Bootstrap 95% CI (`B = 500`, `138` tiles): `201 BCE to 1000 CE`, `21.50° to 30.50° N`.
  - M2 profile-extinction MLE (`k_V = 0.10`): `160 CE, 35.70° N`, `LL = −898.45` (`+37.3` LL over M1).
  - M3 pure geometric spherical cap (no extinction): `41 BCE`, `R = 41.7°`, `LL = −874.31` (`+61.5` LL over M1).
  - Bright-star subset (`V <= 4.0`): `121 BCE, 31.80° N`; `V <= 4.5`: `50 CE, 30.30° N`.
  - Aratus/Eratosthenes pre-Hipparchan core (`aratus_core`): `500 CE, 28.20° N`.
  - M4 unconstrained free pole: `3.94°` inward off the precession track (`β = −70.5°`, `2Δln L = 9.08`).
  - Combined honest uncertainty range: `201 BCE to 1000 CE`, `21.50° to 35.70° N`.
  - Pre-registered verdict: `excludes_pre_3000_bce` (`3000 BCE` rejected by `Δln L = −106.2` in M1, `−125.6` at `k_V = 0.15`, `−96.5` in Aratus core).
- Ran post-hoc robustness check merging the 14" visual binary `α¹ Cen` (`HIP 71683`) into `α² Cen` (`HIP 71681`, `V = −0.27`): `M1 (k_V = 0.25)` unchanged (`910 CE, 25.80° N`), `M1 (k_V = 0.15)` `200 CE, 33.20° N`, `M3` `51 BCE, R = 41.7°`.
- Wrote `RESULTS.md`. Next: build interactive observatory figures (`analysis/make_figures.py` -> `site/figures/ancient-sky-hole/*.html`) and site page (`site/content/ancient-sky-hole.md`).
- 2026-11-23: Restyled the figures (`analysis/make_figures.py` -> `site/figures/ancient-sky-hole/*.html`) to the site's fonts and plain wording, with a night-blue panel and the site's copper accents; rewrote the tile and verdict text. No number changed.
- **2026-11-23 (Claude Fable 5.2, review):** The rim figure's twelve "left-out" stars had been picked by hand and left out Mu Velorum, which rises at every date tried. Replaced with the twelve brightest in `results/rim_stars.tsv` (Alpha-1 Centauri omitted as the companion of a listed star). The live count at Rhodes is now 9 of 12 that never rise, not the 11 of 12 the caption used to state; the caption and the site page now give the counts from the results file (23 of the 30 brightest left-out stars never rose at Rhodes, 14 at Alexandria). No number in `results/` changed.
