# Protocol — Does the Taurid comet stream hide a swarm of large fragments? (`taurid-swarm`)

- **Issue:** [#103](https://github.com/ejhong/aletheia-lab/issues/103)
- **Lane:** `data`
- **Date drafted:** 2026-11-23
- **Budget:** $0 (public NASA/JPL APIs, local Python 3.12 + NumPy 2.3.5)
- **Blinding statement:** Prior to locking this protocol, only blind structural checks (`explore/structure.py`) were executed on JSON schemas, total NEO/fireball counts, `2P/Encke`'s reference orbit, global `H`-magnitude totals, and the fireball coverage year span (`1988–2026`, identifying continuous full-year coverage from `1994–2025`). No Taurid-box `ϖ` distributions, no `7:2` resonance counts, and no calendar/swarm-year fireball rates were computed or inspected.

---

## 1. Exact Question

The strongest surviving variant of the Younger Dryas impact hypothesis replaces a single-day catastrophe with a giant comet (50–100 km) that fragmented 20–30 kyr ago into the **Taurid Complex** — Comet `2P/Encke`, the Taurid meteoroid streams, and a postulated **7:2 Jovian mean-motion resonant swarm** of large fragments (Clube & Napier 1984; Asher & Clube 1993; Napier 2010, *MNRAS* 405, 1901). Napier (2010) reported that 19 bright near-Earth asteroids (`H < 16.5`) in an Encke-like `(a, e, i)` box align in longitude of perihelion (`ϖ = Ω + ω`) with `2P/Encke` (`ϖ_E ≈ 161°`), implying a major population of kilometer- and sub-kilometer-scale cometary remnants. Recent optical fireball networks confirm dm-to-meter debris in the 7:2 resonance during swarm return years (Spurný et al. 2017; Egal et al. 2022), while targeted telescopic searches (ZTF/CFHT 2022; Ye et al. 2025 `arXiv:2509.22602`; Wiegert et al. 2025 `arXiv:2506.03327`) found no large swarm asteroids directly.

**Primary questions tested on two independent 2026 NASA/JPL archives:**
1. **Archive A (43,165 Near-Earth Asteroids):** Does the 2026 NASA/JPL NEO catalog still show a statistically significant longitude-of-perihelion alignment (`ϖ ≈ 161.3°`) in Napier's (2010) `(a, e, i)` corridor — **above both a uniform circle AND adjacent Jupiter secular-dynamics control boxes** — and is there a statistically significant excess of sub-kilometer/kilometer NEAs inside the **7:2 Jupiter mean-motion resonance (`2.21 ≤ a ≤ 2.30 AU`)**?
2. **Archive B (32 complete years of US satellite bolides, 1994–2025):** Do satellite-detected meter-to-decameter airbursts in NASA CNEOS spike in rate or impact energy during the **Autumn Taurid (`Oct 15–Nov 30`)** or **Daytime β-Taurid (`Jun 10–Jul 10`)** seasons, or specifically during the published **7:2 resonant swarm return years (`1998, 2005, 2015, 2018, 2022, 2025`)**?

---

## 2. Data and Sample Definitions

All files and SHA-256 hashes are recorded in `MANIFEST.md`:

1. **Archive A — NASA/JPL SBDB Near-Earth Objects (`data/jpl_neos.json`, `43,374` rows):**
   - Filtered strictly to near-Earth asteroids (`class ∈ {'AMO', 'APO', 'ATE', 'IEO'}`) with valid numerical `a, e, i, om, w, H` (`43,156` NEAs). Comets (`JFc`, `JFC`, `HTC`, `ETc`) are excluded from NEA tests so `2P/Encke` is not counted in its own test.
   - Reference parent orbit (`data/jpl_encke.json`, Comet `2P/Encke`): `a_E = 2.218 AU`, `e_E = 0.8470`, `i_E = 11.34°`, `Ω_E = 334.01°`, `ω_E = 187.28°`, giving **`ϖ_E = (Ω_E + ω_E) mod 360° = 161.29°`**.
   - For every NEA `j`, compute longitude of perihelion `ϖ_j = (om_j + w_j) mod 360°`, signed angular separation `Δϖ_j = ((ϖ_j - ϖ_E + 180) mod 360) - 180 ∈ [-180°, +180°)`, and standard approximate diameter (assuming cometary albedo `p_V = 0.05` vs. stony `p_V = 0.14`: `D_km = 1329 / sqrt(p_V) * 10^(-H/5)`).
   - **Pre-registered orbital boxes:**
     - **Napier (2010) Taurid Box (`Box_T`):** `1.83 ≤ a ≤ 2.70 AU`, `0.63 ≤ e ≤ 1.00`, `0° ≤ i ≤ 14°`.
     - **Control Box 1 — Moderate-eccentricity Jupiter secular control (`Ctrl_LowE`):** `1.83 ≤ a ≤ 2.70 AU`, `0.40 ≤ e < 0.63`, `0° ≤ i ≤ 14°`. Shares identical semi-major axis and low inclination (hence same Jupiter secular perihelion forcing and ecliptic survey geometry) without Encke's high-eccentricity orbit.
     - **Control Box 2 — Higher-inclination high-eccentricity control (`Ctrl_HighI`):** `1.83 ≤ a ≤ 2.70 AU`, `0.63 ≤ e ≤ 1.00`, `14° < i ≤ 35°`. Shares high eccentricity and `a`, outside the Taurid plane.
   - **Pre-registered magnitude tiers:**
     - `H < 16.5` (exact Napier 2010 replication tier; `D ≳ 1.8–3.0 km`),
     - **`H < 18.0` (Primary Test A1 tier; near-complete km-scale Spaceguard tier, `D ≳ 0.9–1.5 km`)**,
     - **`H < 20.0` (Primary Test A2 tier; sub-km `D ≳ 350–600 m`)**,
     - `H < 22.0` (`D ≳ 140–240 m`, sensitivity),
     - `All H` (sensitivity).

2. **Archive B — NASA/JPL CNEOS Fireballs (`data/cneos_fireballs.json`, `1,074` rows):**
   - **Primary sample:** All bolides occurring in the **32 complete continuous-coverage calendar years `1994-01-01` through `2025-12-31`** (excluding sparse pre-1994 sensor years `1988–1993` with only 1–2 events/yr and incomplete `2026` which ends `2026-10-04` right before the Autumn Taurids).
   - **Sensitivity sample:** All years `1988–2026` (explicitly noting incomplete 2026).
   - **Pre-registered calendar windows (from Egal et al. 2022, *MNRAS* 512, 2318):**
     - **Autumn Taurids (`NTA + STA`):** Day-of-year matching **Oct 15 – Nov 30** inclusive (`47` days; expected uniform fraction `f_aut = 47 / 365.25 = 0.12868`).
     - **Daytime β-Taurids / ζ-Perseids (`BTA + ZPE`):** **Jun 10 – Jul 10** inclusive (`31` days; expected uniform fraction `f_day = 31 / 365.25 = 0.08487`).
   - **Published 7:2 Resonant Swarm Autumn Return Years inside `1994–2025` (Egal et al. 2022; Wiegert et al. 2025 `arXiv:2506.03327`):**
     - **Primary 6-year swarm set:** `{1998, 2005, 2015, 2018, 2022, 2025}` vs. `26` non-swarm years in `1994–2025`.
     - **Strict 4-year core sensitivity set:** `{1998, 2005, 2015, 2022}` (excluding 2018's `-48°` mean-anomaly offset and 2025).

---

## 3. Exact Pre-Registered Tests and Thresholds

All Monte Carlo and permutation tests use fixed PRNG seed **`20261123`** and **`N_PERM = 10,000`** iterations.

### Test A1 — Perihelion Alignment (`ϖ ≈ 161.29°`) Above Uniform AND Above Secular Controls
For a given sample of `N` NEAs, define the Encke-directed circular alignment score (mean cosine toward `ϖ_E = 161.29°`):
$$\bar{C} = \frac{1}{N} \sum_{j=1}^{N} \cos(\varpi_j - \varpi_E), \qquad u = \sqrt{2N}\,\bar{C}$$
and the Taurid-corridor fraction `f_45 = (count with |Δϖ_j| ≤ 45°) / N` (expected `0.250` under uniform `ϖ`).
1. **Uniformity test (`p_unif`):** One-sided Monte Carlo p-value (`10,000` uniform circular draws of size `N`) for `u ≥ u_obs`.
2. **Secular-control excess (`p_ctrl_LowE`, `p_ctrl_HighI`):** Two-sample one-sided permutation test (`10,000` shuffles of box labels) testing whether `ΔC = C_bar(Box_T) - C_bar(Control) > 0`.
3. **Pass criterion A1 (Primary on `H < 18.0`; exact replication also reported on `H < 16.5`, `H < 20.0`, `H < 22.0`):**
   - `p_unif < 0.01` **AND** `p_ctrl_LowE < 0.05` (alignment is both non-uniform toward Encke AND strictly stronger than the adjacent moderate-eccentricity Jupiter secular control).

### Test A2 — 7:2 Jupiter Mean-Motion Resonance (`2.21 ≤ a ≤ 2.30 AU`) Excess
Inside `Box_T`, define the **Taurid-aligned corridor** `|Δϖ| ≤ 45°` (`116.3° ≤ ϖ ≤ 206.3°`) and the **7:2 Jupiter resonance band** `2.21 ≤ a ≤ 2.30 AU` (`width = 0.09 AU` centered on `a_7:2 = 2.256 AU`, vs. flanking background `[1.83, 2.21) ∪ (2.30, 2.70]` of total width `0.78 AU`).
- At **`H < 20.0`** (primary; also reported at `H < 18.0`, `H < 22.0`, and `All H`):
  1. **Within-corridor `a`-density excess (`p_res_a`):** Exact one-sided binomial test of `N_res` out of `N_aligned` against geometric band share `0.09 / 0.87 = 0.10345` (and also compared against the empirical `7:2` fraction observed in `Ctrl_LowE`, `p_res_ctrl` via exact Fisher/permutation test!).
  2. **Alignment × resonance interaction (`p_res_anti`):** Compare the `7:2` fraction inside Taurid-aligned `Box_T` (`|Δϖ| ≤ 45°`) vs. anti-Taurid `Box_T` (`|Δϖ| > 45°`) via one-sided permutation test (`10,000` shuffles).
- **Pass criterion A2 (Primary on `H < 20.0`):** Enrichment ratio `≥ 2.0×` over anti-Taurid `7:2` fraction **AND** `p_res_anti < 0.01` **AND** `p_res_ctrl < 0.01`.
- **Direct census:** List every catalogued `H < 20.0` NEA inside the 7:2 Taurid resonant zone (`2.21 ≤ a ≤ 2.30`, `e ≥ 0.63`, `i ≤ 14°`, `|Δϖ| ≤ 45°`), plus the tighter `D_SH`-like Encke cluster (`e ≥ 0.75`, `i ≤ 12°`, `|Δϖ| ≤ 30°`)!

### Test B1 — Calendar Seasonality of NASA CNEOS Satellite Airbursts (`1994–2025`)
Over all bolides in `1994–2025`:
1. **All bolides count:** Exact one-sided binomial test of `N_aut` (`Oct 15–Nov 30`) vs. `f_aut = 47 / 365.25`, and `N_day` (`Jun 10–Jul 10`) vs. `f_day = 31 / 365.25`.
2. **Large bolides (`impact-e ≥ 1.0 kt`):** Exact one-sided binomial test in Autumn Taurids and Daytime β-Taurids.
3. **Impact energy (`sum(impact-e)` and `mean(log10(impact-e))`):** Circular calendar-shift permutation test (`10,000` random day-of-year shifts preserving clustering) for Autumn Taurids and Daytime β-Taurids.
- **Pass criterion B1:** One-sided `p < 0.01` in either Autumn Taurids or Daytime β-Taurids for total count OR `≥ 1.0 kt` count.

### Test B2 — 7:2 Resonant Swarm Return-Year Excess (`1994–2025`)
To eliminate any secular trend in US satellite detection sensitivity from 1994 to 2025, for each year `y ∈ [1994, 2025]` compute:
- **Within-year Autumn Taurid count share:** `s_cnt(y) = N_aut(y) / N_year(y)`
- **Raw Autumn Taurid count:** `N_aut(y)`
- **Large (`≥ 1.0 kt`) Autumn Taurid count:** `N_aut_1kt(y)`
- **Within-year Autumn Taurid energy share:** `s_eng(y) = E_aut(y) / E_year(y)`

Test whether the mean of `s_cnt(y)` (primary) or `N_aut_1kt(y)` across the **6 published swarm years (`1998, 2005, 2015, 2018, 2022, 2025`)** exceeds the `26` non-swarm years using an exact one-sided permutation test (`10,000` random subsets of 6 years out of 32).
- **Pass criterion B2:** One-sided permutation `p < 0.01` for `s_cnt(y)` OR `N_aut_1kt(y)` (with `s_eng(y)`, raw `N_aut(y)`, and the 4-year core subset reported alongside).

---

## 4. Pre-Registered Joint Verdict Rule

- **Macro-fragment Taurid swarm supported:** At least one Archive A criterion (`A1` or `A2`) passes **AND** at least one Archive B criterion (`B1` or `B2`) passes.
- **Partial / mixed (one archive only):** Exactly one archive passes (e.g., orbital perihelion alignment in NEAs with zero airburst excess, or vice versa — interpreted plainly according to which signal is present).
- **No macro-fragment swarm signal (`0 of 4`):** Neither Archive A (`A1, A2`) nor Archive B (`B1, B2`) passes.

---

## 5. Pre-Lock Validation (`analysis/test_taurid.py` & `--decoy`)

Before locking `protocol.md`, `analysis/test_taurid.py` must pass 100%, verifying:
1. Circular alignment V-test calibration under uniform synthetic angles (`type-I error ~ 0.05` at `α = 0.05`) and high detection power (`> 95%`) for an injected Taurid cluster of 20 aligned NEAs on top of 80 uniform background NEAs.
2. Secular-control difference test correctly rejects a fake signal when BOTH `Box_T` and `Ctrl_LowE` share the same artificial `ϖ` bias (proving our control catches Jupiter/survey bias!).
3. Calendar-window day-of-year logic handles leap years accurately (`Oct 15–Nov 30` = 47 days; `Jun 10–Jul 10` = 31 days) and detects an injected `2×` swarm-year fireball surge cleanly.
4. Full end-to-end `--decoy` run executes cleanly on synthetic shuffled `ϖ` and shuffled fireball dates without ever touching real Taurid statistics.
