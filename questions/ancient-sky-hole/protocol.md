# Protocol — The hole in the ancient sky (`ancient-sky-hole`)

- **Issue:** [#85](https://github.com/ejhong/aletheia-lab/issues/85)
- **Lane:** `data`
- **Date drafted:** 2026-11-23
- **Budget:** $0 (public astronomical archives, local Python 3.12 + NumPy 2.3.5 computation)
- **Blinding statement:** Prior to locking this protocol, only blind structural checks (`explore/structure.py`) were run on headers, row counts, identification quality flags, constellation names, and the northern-sky (`dec_J2000 > +20°`) magnitude completeness curve. No southern-sky declinations, southern void coordinates, or `(epoch, latitude)` fits were computed or inspected.

---

## 1. Exact Question

The 48 classical constellations preserved in Ptolemy's *Almagest* (c. 137 CE) leave a roughly circular patch of the southern sky empty — the zone of avoidance that never rose high enough above the southern horizon for their creators to see and organize into star-pictures. Because Earth's axial precession carries the South Celestial Pole around a 23.4° circle every ~25,772 years, the **location** of the empty patch encodes an epoch `t`, and its **angular radius** encodes an observer latitude `φ` (coupled with near-horizon atmospheric extinction).

**Primary questions:**
1. What epoch `t` and northern latitude `φ` best explain the empty southern patch in Ptolemy's 48 constellations under a physically grounded, pre-registered visibility model?
2. How wide is the **honest uncertainty** once we account for **both** (a) spatial clustering of stars into constellations/void patches and (b) systematic sensitivity to constellation subsets, magnitude limits, atmospheric extinction, and model formulation?
3. Does the honest combined uncertainty range **exclude** an origin date before **3000 BCE** (astronomical year `-2999`)?

---

## 2. Prior Literature (Context Only — Not Tuned Against)

Earlier studies analyzed the southern sky void and/or verbal descriptions in Aratus's *Phaenomena*:
- Ovenden, M. W. (1966), *The Origin of the Constellations*, Philosophical Journal 3, 1–18 (unverified full text; secondary summary reports ~2600 ± 800 BCE, ~36° N from Aratus).
- Roy, A. E. (1984), *The Origin of the Constellations*, Vistas in Astronomy 27, 171–197 (unverified full text).
- Schaefer, B. E. (2002), *The Latitude and Epoch for the Origin of the Astronomical Lore of Eudoxus*, JHA 33, 313–350 (unverified full text); Schaefer, B. E. (2006), *The Origin of the Greek Constellations*, Scientific American 295(5), 96–101 (verified open PDF excerpt: discusses Mesopotamian + Greek patchwork origins and Farnese Atlas epoch 125 ± 55 BCE from Schaefer 2005, JHA 36).

Because earlier conclusions are known qualitatively, every analytical choice below is fixed *a priori* from physics, astronomy, and documented historical strata before running on the real southern sky.

---

## 3. Data and Sample Definitions

All files are documented with URLs and SHA-256 hashes in `MANIFEST.md`:
1. **Ptolemy's *Almagest* (Verbunt & van Gent 2012, *A&A* 544, A31; VizieR `J/A+A/544/A31/ptolema`):** 1,028 entries across 48 constellations with Hipparcos (`HIP`) identifications, quality flag `I ∈ {1..6}`, and outside-figure (`informes`) flag `f_N ∈ {'', 'a'}`.
2. **ESA Hipparcos Main Catalogue (ESA 1997; VizieR `I/239/hip_main`, `Vmag <= 7.0`):** 15,537 stars with valid ICRS coordinates `(RAICRS, DEICRS)` at epoch J1991.25, Johnson `Vmag`, and proper motions `(pmRA, pmDE)` in mas/yr.
3. **Yale Bright Star Catalogue 5th Rev. Ed. (Hoffleit & Warren 1991; VizieR `V/50/catalog`):** Used strictly for human-readable Bayer/Flamsteed star labels joined via `HD` number (never used in likelihood calculations).

**Star universe:** All Hipparcos stars with valid position and `Vmag <= 5.5` (primary cutoff; sensitivity cutoffs `Vmag <= 4.0`, `4.5`, `5.0`, `5.5`). Missing `pmRA`/`pmDE` are treated as `0.0 mas/yr`.

**Catalogued indicator `y_i ∈ {0, 1}` across four pre-registered catalogue definitions:**
- **`all48` (Primary):** `y_i = 1` iff `HIP_i` is matched in Verbunt & van Gent (2012) with quality flag `I ∈ {1, 2, 3}` (1,020 unique Hipparcos stars).
- **`in_figure`:** `y_i = 1` iff `I ∈ {1, 2, 3}` AND `f_N == ''` (excludes the 108 *informes* stars lying outside the classical constellation figures).
- **`aratus_core`:** `y_i = 1` iff `I ∈ {1, 2, 3}`, `f_N == ''`, AND `cst ∉ {'=Equ', '=CrA'}` (excludes the two constellations of documented late origin omitted as named figures in the Aratus/Eratosthenes tradition: Equuleus and Corona Australis).
- **`strict_id`:** `y_i = 1` iff `I ∈ {1, 2}` (strictly secure Hipparcos identifications only).

---

## 4. Astrometry and Precession Model

1. **Proper motion:** For star `i` with J1991.25 ICRS unit vector `u_0`, tangent basis vectors `e_α, e_δ`, and Hipparcos proper motions `(pmRA, pmDE)` (where `pmRA = μ_α cos δ` in mas/yr), the J2000-frame unit direction at astronomical Julian year `t` (`Δt = t - 1991.25`) is:
   `u_i(t) = normalize(u_0 + Δt * (π / (180 * 3.6e6)) * (pmRA * e_α + pmDE * e_δ))`.
   Note: Astronomical year `t` relates to BCE as `year_BCE = 1 - t` (so `t = 0` is `1 BCE`, `t = -2999` is `3000 BCE`, `t = +137` is `137 CE`).
2. **Long-term precession:** The North Celestial Pole unit vector `p_N(t)` in J2000 Cartesian coordinates is computed using the exact **Vondrák, Capitaine & Wallace (2011, *A&A* 534, A22; Corrigendum 2012, *A&A* 541, C1)** long-term equator-pole expression (`eraLtpequ`), valid over `±200,000 years` to arcsecond precision.
3. **Declination and maximum southern altitude:**
   - `δ_i(t) = arcsin(u_i(t) · p_N(t))`
   - For a northern observer at latitude `φ > 0°`, maximum culmination altitude is `h_max,i(t, φ) = 90° - |φ - δ_i(t)|`.
   - Near-horizon atmospheric refraction is included via Bennett's (1982) formula (applied for `h_max > -0.6°`, lifting a geometric `h_max = 0°` star to `h_app ≈ +0.57°`). Stars with `h_app <= 0°` never rise above the refracted sea horizon.

---

## 5. Statistical Models

### 5.1 Precession-Invariant Northern Calibration Cap
The ecliptic latitude `β_i` of every star is invariant to axial precession (changing by `< 0.5°` over 10,000 yr via planetary ecliptic precession). Every star with **`β_i > +30°`** stays well above the southern horizon (`δ(t) > +6°`) at every epoch in `[-10000, +2000]` for all northern latitudes `φ <= 50° N`.

On all stars with `β_i > +30°` and `Vmag <= 5.5`, we fit the 2-parameter logistic zenith completeness function by maximum likelihood:
$$p_{\text{base}}(V) = \frac{1}{1 + \exp\bigl((V - V_{50}) / s_V\bigr)}$$
Parameters `(V_50, s_V)` are frozen from this northern ecliptic cap (separately for each catalogue definition `all48`, `in_figure`, `aratus_core`, `strict_id`) and **never** refit on the southern sky.

### 5.2 Model M1 — Physical Atmospheric-Extinction Likelihood (Primary Model)
Evaluated over all stars outside the calibration cap (**test region `β_i <= +30°`**, `Vmag <= 5.5`):
- For `h_app,i > 0°`, optical airmass is given by **Kasten & Young (1989)**:
  $$X(h_{\text{app}}) = \frac{1}{\sin(h_{\text{app}}) + 0.50572 \cdot (h_{\text{app}}^\circ + 6.07995)^{-1.6364}}$$
- Excess visual extinction relative to zenith (`X = 1`) dims the star to effective magnitude:
  $$V_{\text{eff},i}(t, \phi; k_V) = V_i + k_V \cdot \bigl(X(h_{\text{app},i}) - 1\bigr)$$
- Primary extinction coefficient: **`k_V = 0.25 mag/airmass`** (typical clear sea-level Mediterranean/Mesopotamian night sky; Schaefer 1993). Sensitivity grid: **`k_V ∈ {0.15, 0.20, 0.25, 0.30, 0.35}`** mag/airmass (from pristine highland/desert air to humid coastal haze).
- Catalogue inclusion probability with fixed lapse floor `ε = 0.002`:
  $$P_i(t, \phi; k_V) = \begin{cases} \epsilon & \text{if } h_{\text{app},i} \le 0^\circ \\ (1 - 2\epsilon)\, p_{\text{base}}\!\bigl(V_{\text{eff},i}\bigr) + \epsilon & \text{if } h_{\text{app},i} > 0^\circ \end{cases}$$
- Log-likelihood:
  $$\ln L(t, \phi; k_V) = \sum_{i : \beta_i \le +30^\circ} \Bigl[ y_i \ln P_i + (1 - y_i) \ln(1 - P_i) \Bigr]$$
- Search domain: coarse grid `t ∈ [-10000, +1000]` step `50 yr`, `φ ∈ [15°, 50°]` step `0.5°`, followed by refined grid around the global maximum (`±600 yr` step `10 yr`, `±4°` step `0.2°`).

### 5.3 Model M2 — Joint Profile Likelihood over `(t, φ, k_V)`
Same likelihood as M1, but jointly maximizing over `k_V ∈ [0.10, 0.50]` in steps of `0.02 mag/airmass`. Explicitly tests the degeneracy between observer latitude `φ` and atmospheric haze `k_V`.

### 5.4 Model M3 — Pure Geometric Spherical Cap (Extinction-Free Cross-Check)
Tests whether the epoch depends on the atmospheric extinction law. For any epoch `t`, let `θ_i(t) = 90° + δ_i(t)` be star `i`'s angular distance from the South Celestial Pole at epoch `t`. Fit a smooth circular empty cap of angular radius `R_cap ∈ [20°, 65°]` (step `0.5°`, fixed transition width `w = 2.0°`):
$$P_i(t, R_{\text{cap}}) = (1 - 2\epsilon)\, p_{\text{base}}(V_i)\, \sigma\!\left(\frac{\theta_i(t) - R_{\text{cap}}}{w}\right) + \epsilon, \qquad \sigma(z) = \frac{1}{1 + e^{-z}}$$
Because `R_cap` combines latitude `φ` plus an effective horizon cutoff `h_eff`, M3 measures the **epoch `t` purely from the center of the empty circle**, independent of extinction assumptions.

### 5.5 Model M4 — Unconstrained Free-Pole Diagnostic
Replaces the precession-constrained South Celestial Pole `-p_N(t)` in Model M3 (and in Model M1 via replacing `δ_i(t)` with `arcsin(-u_i(t_0) · p_free)`) with a **completely free unit vector `p_free`** anywhere in the southern ecliptic hemisphere (`β_pole <= -40°`, coarse grid 2° + refined grid 0.25°).
- Computes:
  1. Angular separation `Δθ_offtrack` (degrees) between `p_free` and the closest point on the 26,000-year Vondrák precession path of the South Celestial Pole.
  2. Likelihood-ratio statistic `2 Δln L_offtrack = 2 (ln L_free - ln L_precession)` (`df = 1`).
- **Diagnostic interpretation:** If `Δθ_offtrack > 6.0°`, the empty patch is substantially displaced off the Earth's precession track (indicating severe multi-epoch distortion or asymmetric incompleteness), and no single epoch can be reliably claimed.

---

## 6. Honest Uncertainty Quantification

Stars in the same constellation or unconstellated sky region are spatially correlated; treating stars as independent coin flips yields falsely tight confidence intervals. We compute and report **four** uncertainty measures:

1. **Star-level profile likelihood 95% CI (`2 Δln L <= 5.99`, 2 df):** Reported for reference only as the optimistic independent-star lower bound.
2. **Spatial Block Bootstrap 95% CI (Primary Statistical Uncertainty):** Partition the test sky (`β <= +30°`) into deterministic equal-area spatial tiles of ~`15° × 15°` (using latitude bands of `15°` in ecliptic latitude `β` from `-90°` to `+30°`, subdivided in ecliptic longitude `λ` into `round(24 * cos(β_mid))` equal-width sectors — ~130 spatial tiles total). Draw **`B = 500`** bootstrap resamples of whole spatial tiles with replacement (fixed PRNG seed `20261123`), refit Model M1 (`k_V = 0.25`, `all48`, `V <= 5.5`) on each resample, and take the 2.5th–97.5th percentile for `t` and `φ` (plus 16th–84th percentile for 68% CI).
3. **Leave-One-Constellation-Out (LOCO) Jackknife:** For every Ptolemy constellation with at least one star south of `δ_J2000 = -15°`, drop all stars of that constellation (treating them as excluded from the likelihood, NOT as uncatalogued `y = 0`, so dropping a constellation tests its positive pull on the boundary!) and refit M1. Report the full min–max range and identify the single most influential constellation.
4. **Systematic Model Envelope:** Full min–max range of best-fit `(t, φ)` across all pre-registered variants:
   - Extinction `k_V ∈ {0.15, 0.20, 0.25, 0.30, 0.35}` (M1),
   - Free-extinction profile model (M2),
   - Geometric spherical cap model (M3, for epoch `t`),
   - Catalogue subsets (`all48`, `in_figure`, `aratus_core`, `strict_id`),
   - Magnitude cutoffs (`Vmag <= 4.0, 4.5, 5.0, 5.5`).

**Combined Honest Uncertainty Range (Headline Range):** The union `[min(boot_lo, sys_lo), max(boot_hi, sys_hi)]` of the primary Spatial Block Bootstrap 95% CI and the Systematic Model Envelope.

---

## 7. Pre-Registered Simulated-Sky Validation (Run Before Locking)

Before running on the real southern sky, `analysis/test_skyhole.py` must pass 100%, including:
1. **Astrometric verification:** Check `eraLtpequ` North/South Celestial Pole positions at J2000 (`dec = +90°`), 2750 BCE (near Thuban `α Dra`), 12,000 BCE (near Vega `α Lyr`), and obliquity `~23.44°` at J2000 and `~24.0°` at 3000 BCE.
2. **4-epoch synthetic sky recovery:** Using real Hipparcos `(RA, Dec, Vmag, pmRA, pmDE)`, simulate synthetic catalogues from known ground-truth `(t_true, φ_true)` at:
   - `(-9600, 37.0° N)`
   - `(-2500, 36.0° N)`
   - `(-1200, 33.0° N)`
   - `(+137, 31.2° N)`
   Verify Model M1 recovers `t_true` within `±350 yr` and `φ_true` within `±1.5°` across all 4 epochs!
3. **Correlated/patchy sky calibration check:** Generate synthetic catalogues with random `18°` angular sky patches dropped/perturbed near the southern rim (mimicking real constellation-level patchiness) and verify that the Spatial Block Bootstrap 95% CI is substantially wider than the naive star-level CI and covers `t_true`.
4. **Decoy run (`--decoy`):** Execute the full `analysis/skyhole.py --decoy` end-to-end pipeline on a synthetic decoy sky (known `(t = -1800, φ = 35.0° N)`) to verify all outputs, JSON schemas, and runtimes without ever reading real southern-sky `y_i`.

---

## 8. Decision Rule (Answering Issue #85)

Let `[t_lo, t_hi]` be the **Combined Honest Uncertainty Range** for the epoch `t` (in astronomical years, where `3000 BCE = -2999`), and `Δθ_offtrack` be the M4 free-pole offset from the precession path:

1. **Excludes pre-3000 BCE:** `t_lo > -2999` AND `Δθ_offtrack <= 6.0°`.
   - Plain-language verdict: The empty patch dates the classical sky boundary to **after 3000 BCE** (within the Bronze Age / Classical Mediterranean–Mesopotamian window) and excludes an origin before 3000 BCE.
2. **Requires pre-3000 BCE:** `t_hi < -2999` AND `Δθ_offtrack <= 6.0°`.
   - Plain-language verdict: The empty patch points to an origin **before 3000 BCE** even after accounting for spatial clustering and systematic model choices.
3. **Undetermined / Spans 3000 BCE (or off-track):** `t_lo <= -2999 <= t_hi` OR `Δθ_offtrack > 6.0°`.
   - Plain-language verdict: The empty patch **cannot reliably exclude (or establish) a pre-3000 BCE origin** — either because honest uncertainty spans 3000 BCE, or because the empty patch does not cleanly sit on a single precession epoch.

Note on latitude `φ`: Regardless of epoch verdict, we report the best-fit latitude, its Spatial Block Bootstrap 95% CI, and the full `(φ, k_V)` extinction trade-off range honestly.
