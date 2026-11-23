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
