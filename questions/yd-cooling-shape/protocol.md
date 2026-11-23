# Was the Younger Dryas cooling different from other abrupt ice-age coolings?

Issue #75 · Lane: data · Written 2026-11-23 by Antigravity (Google DeepMind), directed by Eugene

## Question

A central claim of the Younger Dryas impact hypothesis (YDIH) is that the Younger Dryas (`GS-1`, onset 12,896 yr b2k = 12,846 cal BP) was an extraordinary climate catastrophe triggered by an external cosmic impulse (an impact winter or catastrophic ice-dam rupture), distinct from natural glacial climate oscillations. Earlier lab studies tested the fire and biomass-burning claims (#43 `ice-core-fire`, #60 `cooling-ammonium`, #69 `yd-global-burn`).

Here we test the **climate-transition shape itself** across Greenland and Antarctica, comparing `GS-1` against every other well-defined abrupt stadial cooling (`GS-2.1c` through `GS-24`) of the last 100,000 years—with every measure and decision threshold fixed before inspecting `GS-1`:

1. **Abruptness:** Did Greenland cool faster or more sharply at the Younger Dryas onset than at other Dansgaard–Oeschger stadial transitions?
2. **Amplitude & dust jump:** Was the total Greenland temperature drop (`ΔT`) or atmospheric dust jump (`Δlog Ca²⁺`) unusually large?
3. **"Out of the blue" vs. gradual pre-cooling:** Did the Younger Dryas strike from a flat warm plateau (as expected for an external impulse), or after a gradual pre-onset cooling slope like internal AMOC slowdowns?
4. **Global cooling vs. Antarctic bipolar seesaw:** Did Antarctica cool synchronously with Greenland in the 200 years after onset (as expected for a global impact winter), or warm on the standard Southern Hemisphere bipolar-seesaw pattern seen during ordinary ice-age stadials?

## Data and sources

All public from NOAA WDS Paleoclimatology and PANGAEA (URLs, licences, SHA-256 hashes in `MANIFEST.md`):

| Short name | File | What | Span |
|---|---|---|---|
| `NGRIP_D18O` | `gicc05-60ka-20yr.txt` | NGRIP 20-yr `δ¹⁸O` (‰) on GICC05 (NGRIP dating group 2008) | 20–60,000 yr b2k |
| `NGRIP_TEMP` | `ngrip2014temp.txt` | NGRIP reconstructed surface temperature (°C) and accumulation (`m/yr`) on `ageGICC05` (Kindler et al. 2014) | 10–120 ka b2k |
| `NGRIP_CA` | `935814.tab` | NGRIP 10-yr `Ca²⁺` (µg/kg) on GICC05 (Erhardt et al. 2021) | 10,270–107,620 yr b2k |
| `ANT_TEMP` | `buizert2021-temp.txt` | 7-core Antarctic temperature reconstruction (°C) on 40-yr grid (Buizert et al. 2021: WD, EDML, EDC, TAL, SDM, SP, DF) | 0–40,000 yr BP1950 |
| `G3_20YR` | `gicc05-calcium-20yr.txt` | Synchronized 20-yr NGRIP, GRIP, GISP2 `δ¹⁸O` & `Ca²⁺` on GICC05 (Rasmussen et al. 2008) | 11,620–32,440 yr b2k |
| `EVENTS` | `events.tsv` | Published GICC05 stadial/interstadial onsets (Rasmussen et al. 2014, Table 2) | 11.4–119.1 ka b2k |

**Timebase convention:** `age_yrBP1950 = age_b2k − 50`. For `gicc05-60ka-20yr.txt`, row `a` covers `[a − 20, a)` b2k (file header: age refers to bottom of each 20-yr interval; bin midpoint = `a − 10`). For `935814.tab`, row `a` (in ka b2k, converted to `a * 1000` yr b2k) covers `[a, a + 10)` b2k (midpoint = `a + 5`). For `ngrip2014temp.txt` and `buizert2021-temp.txt`, each row is treated as a point sample at its listed `ageGICC05` or `age_yrBP1950`.

**What was looked at before locking (`explore/structure.py`):** file headers, column names, spans, spacings, and the published list of event ages in `events.tsv`. Zero values of `δ¹⁸O`, temperature, accumulation, or `Ca²⁺` inside `[11,500, 14,500]` yr b2k/BP were inspected before locking.

## Method

### Event selection (identical base rule to `#60` `cooling-ammonium`)

A stadial onset `t` (yr b2k) from `events.tsv` enters the comparison pool if all three hold:
1. `kind == "stadial onset"` and `definition_uncertainty ∈ {"4yr", "a", "b"}` (i.e., `GS-1` plus all stadial onsets whose onset age is defined to within ≤ 60 yr).
2. No other listed event in `events.tsv` lies strictly inside `(t − 200, t + 100)` b2k (ensuring at least 100 yr of prior warm interstadial and 200 yr of subsequent stadial).
3. The dataset covers `[t − 200, t + 200]` cleanly:
   - **60-kyr GICC05 pool (`NGRIP_D18O`):** `t − 200 >= 10,000` and `t + 200 <= 60,000` b2k.
   - **100-kyr pool (`NGRIP_TEMP`, `NGRIP_CA`):** `t − 200 >= 10,300` and `t + 200 <= 107,620` b2k.
   - **40-kyr Antarctic pool (`ANT_TEMP`):** `t_bp = t − 50` with `t_bp − 200 >= 10,000` and `t_bp + 200 <= 40,000` BP1950.

### Pre-registered measures (all oriented so larger = more impact-like / sharper / colder)

For each qualifying stadial onset `t` (remember age runs backwards: `t + Δ` is *before* onset, `t − Δ` is *after* onset):

1. **Initial cooling abruptness (`abrupt_60`, primary on `NGRIP_D18O`, 60-kyr pool):**
   - `abrupt_60 = mean(δ¹⁸O with midpoint in [t, t + 100)) − mean(δ¹⁸O with midpoint in [t − 60, t))` (‰; positive = sharper drop in the first 60 yr).
   - Reported alongside: **`peak_rate_20`** = maximum single 20-yr forward cooling drop `δ¹⁸O(b + 20) − δ¹⁸O(b)` across bins with midpoint in `[t − 80, t + 40)` (‰ per 20 yr); and **`abrupt_temp_60`** on `NGRIP_TEMP` across the 100-kyr pool (°C).
2. **Total cooling amplitude (`amp_temp`, primary on `NGRIP_TEMP`, 100-kyr pool) & dust jump (`dust_jump`, primary on `NGRIP_CA`, 100-kyr pool):**
   - `amp_temp = mean(T in [t, t + 100)) − mean(T in [t − 200, t − 40))` (°C; positive = larger cooling into the stadial, skipping the first 40 yr transition zone). Also reported on `NGRIP_D18O` (`amp_d18o`, 60-kyr pool).
   - `dust_jump = mean(ln(Ca²⁺) in [t − 200, t − 40)) − mean(ln(Ca²⁺) in [t, t + 100))` (natural log ratio; `exp(dust_jump)` = multiplicative dust jump). Also reported: `dust_abrupt_60` (`[t − 60, t)` vs `[t, t + 100)`).
3. **"Out of the blue" precursor slope (`pre_slope`, primary on `NGRIP_D18O`, 60-kyr pool):**
   - Ordinary least-squares slope of `δ¹⁸O` against forward time `τ = t − midpoint` (in centuries) over `[t, t + 200)` (the 200 yr *before* onset; units `‰ / century`).
   - Positive/zero slope = warm/flat plateau immediately before onset ("out of the blue"); negative slope = Greenland was already cooling down gradually before onset. Higher `pre_slope` = more "out of the blue". (Also report `pre_slope_temp` over `[t, t + 200)` on `NGRIP_TEMP` across 100 kyr.)
4. **Antarctic bipolar response (`ant_cool`, primary on `ANT_TEMP` WAIS Divide `TS_WD` and 7-core mean `TS_MEAN`, 40-kyr pool):**
   - `ΔT_ant = mean(T in [t_bp − 200, t_bp)) − mean(T in [t_bp, t_bp + 200))` (°C; positive = Antarctica **warms** after Greenland cooling onset, the standard AMOC bipolar seesaw; negative = Antarctica **cools** synchronously, as expected in a global impact winter).
   - Score `ant_cool = −ΔT_ant` (higher = more global cooling / less bipolar warming). Primary series is the 7-core Antarctic mean `TS_MEAN`; WAIS Divide `TS_WD` and all 7 individual Antarctic cores are reported alongside.

**Rank definition:** For any measure, `GS-1`'s rank is `1 + count(other qualifying coolings strictly greater than GS-1)` out of `N` usable coolings. *Top 10%* means `rank ≤ max(1, floor(0.10 * N))`.

### Decision rule (fixed in advance)

Four binary criteria test whether `GS-1` (Younger Dryas) stands out as physically distinct from natural Dansgaard–Oeschger coolings:
- **`D1` (Abruptness):** `abrupt_60` (`NGRIP_D18O`, 60-kyr pool) reaches the **top 10%**.
- **`D2` (Amplitude or dust):** `amp_temp` (`NGRIP_TEMP`, 100-kyr pool) OR `dust_jump` (`NGRIP_CA`, 100-kyr pool) reaches the **top 10%**.
- **`D3` ("Out of the blue"):** `pre_slope` (`NGRIP_D18O`, 60-kyr pool) reaches the **top 10%**.
- **`D4` (Global cooling instead of bipolar seesaw):** `ΔT_ant < 0` in `TS_MEAN` (Antarctica cools rather than warms during the 200 yr after onset) AND `GS-1` ranks **#1** in `ant_cool` in the 40-kyr pool.

**Verdict:**
- **Distinct from natural coolings (catastrophic-trigger signature):** All three of `{D1, D2, D3}` hold, OR `D4` holds together with at least one of `{D1, D2, D3}`.
- **Extreme case of a natural cooling:** 1 or 2 of `{D1, D2, D3}` hold while `D4` does **not** hold (Antarctica still responds via the bipolar seesaw), OR `D4` holds alone.
- **Indistinguishable from natural coolings:** 0 of `{D1, D2, D3, D4}` hold.

### Reported alongside (not part of the rule)
1. Three-core Greenland cross-check (`NGRIP`, `GRIP`, `GISP2` in `G3_20YR`, 11.6–32.4 ka) comparing `GS-1` against `GS-2.1c`, `GS-2.2`, `GS-3`, `GS-4`, `GS-5.1`, `GS-5.2`.
2. Sensitivity to alternative post-onset window `[t − 100, t)` and pre-onset baseline `[t, t + 150)`.
3. Full composite profile (`−300` to `+300` yr around onset) of `GS-1` vs. median & interquartile range of all other coolings in Greenland `δ¹⁸O`, `T`, `Ca²⁺`, and Antarctic `T`.
4. Accumulation-rate drop (`Δaccum` in `ngrip2014temp.txt`) across all 100-kyr coolings.

### Checks before the lock
1. Unit tests (`analysis/test_shape.py`) on synthetic cooling transitions verifying sign conventions (step drop = positive `abrupt_60` & `amp_temp`, flat pre-onset vs. pre-cooling slope, dust jump, Antarctic warming vs. cooling, and every verdict branch).
2. A **decoy run** (`python3 analysis/shape.py --decoy`) excluding `GS-1` completely and scoring a deterministic decoy stadial (`seed = 75`) across all pools without inspecting `GS-1`.

## Known weaknesses
- **20-yr / 40-yr binning resolution:** A 20-year Greenland bin cannot resolve a 1-year vs. 10-year drop, though it cleanly measures multi-decadal abruptness, 200-yr precursor trends, total cooling amplitude, and 200-yr bipolar response.
- **Interglacial baseline context:** `GS-1` occurred during deglaciation (higher insolation and warmer Bølling–Allerød baseline than mid-glacial MIS 3 interstadials), which can affect total amplitude and accumulation independently of the trigger mechanism.
- **Single-vendor initial run:** Written and run by Antigravity (Google DeepMind); open to second-vendor review or independent replication from this protocol.

## Budget

$0 (all public NOAA/PANGAEA datasets, local Python computation).
