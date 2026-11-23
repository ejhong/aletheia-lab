<!-- {"vendor": "google", "model": "gemini-4-neon", "utc": "2026-11-23T20:02:25.195015+00:00", "input_tokens": 4155, "output_tokens": 30068, "cost_usd_list_price": 0.4635} -->

Here is a critical review of the pre-registration, organized by the six areas you requested.

---

### 1. Flaws that could produce a false positive or a false negative

* **Overlapping-window self-competition and double-counting in the rank test `[must fix]`**
  Because windows are two years wide (`y, y+1`) and advance by one year, every single-year spike creates **two** high-scoring windows (as already seen in the blind run, where **1894 and 1895** are both in the top five). Worse, if 1908 has a real signal, window **1907** (`1907–1908`) contains the exact same 1908 spike across all aligned sites and competes directly against window **1908** in the reference set. Roughly half the time, a tiny shift in the 30-year background (`1892` vs. `1909/1923`) will make window 1907 score *strictly higher* than window 1908. Thus, even the **2nd largest ammonium year in 191 years** can finish **4th** (behind 1894, 1895, and 1907), giving `4/191 = 0.0209 > 0.02` and failing "Exceptional" (**false negative**).
  * Compounding this, the **sensitivity simulation underestimates this penalty**: it assigns the injected pulse to `y` or `y+1` *independently per core*, so window `y` gets 100% of cores pulsed while `y−1` and `y+1` only get ~50% each and rarely beat `y`. For a real synchronous 1908 event, `1907` gets ~100% of sites too, so true power for "Exceptional" is lower than the reported 24% / 71%.

* **Shifting entire 190-year cores from a noisy, one-sided 1911–1915 sulphur maximum `[must fix]`**
  This rule has four distinct failure modes:
  1. **False positive via null-distribution dilution:** Applying a constant −1 or −2 year shift across *all* of 1800–1990 to `tunu2022b`, `ht95`, and `tunu_n` based solely on 1911–1915 assumes a uniform offset everywhere. If the offset is local drift around 1912 (or a misidentified Katmai peak), shifting the entire series **misaligns** those cores during real Greenland-wide fire years elsewhere in 1800–1990 (e.g., 1895, 1888, 1862), shrinking the reference upper tail and artificially inflating 1908's rank.
  2. **False positive via the 1910 "Big Burn":** August 1910 was one of the largest North American wildfire seasons in recorded history (Idaho/Montana/Canada). Shifting a core back 1 or 2 years moves nominal **1910 directly into 1909 or 1908** (inside the target window). If any of the three shifted cores was not truly late (e.g., if `tunu2022b` peaked in 1914 because of early-20th-century industrial sulphur pollution rather than Katmai), this pulls a massive 1910 fire into the Tunguska window.
  3. **False negative via one-sidedness:** The rule never shifts a core *forward*. Any core running 1 year *early* puts Katmai in 1911 and summer 1908 in 1907, missing the `1908–1909` window entirely.
  4. **Unaligned NEGIS:** NEGIS has no sulphur and is left unaligned, risking a false negative if its depth-age interpolation is off by 1+ years.

* **Varying site count `N` across the 1800–1990 reference windows `[must fix]`**
  The network score is defined whenever *"at least 5 test sites have one"* (out of 7). Because the variance of a mean decreases with `N` (even with spatially correlated sites), windows with 5 sites have wider tails than windows with 7 sites. If 1908 has all 7 sites while early-1800s or late-1900s windows (e.g., after `ht95` or `ngrip1` end) only have 5 sites, those 5-site windows will disproportionately occupy the extreme ranks, systematically pushing 1908 down (**false negative**). Conversely, if 1908 has fewer sites than most reference windows, its variance is inflated (**false positive**).

* **Dropping `<= 0` sample values before computing yearly means `[should fix]`**
  Ingesting values as *"empty where missing or not above zero"* truncates the lower tail of baseline-corrected CFA/IC data. In clean winter seasons near the detection limit, analytical noise produces occasional zeros or slightly negative values; deleting them rather than clamping to a small positive floor (or averaging raw values before logging) biases low-concentration years upward, compresses the background MAD `s`, and distorts z-scores.

* **Missing-data bias across a strong seasonal cycle `[should fix]`**
  Ammonium has a strong summer peak and winter trough. The half-present rule accepts a calendar year when up to 50% of its samples are missing, with no requirement that both halves of the year be represented. A year missing its winter half will appear artificially high (and one missing its summer half artificially low), injecting spurious spikes into both the target and reference periods.

* **Unequal variance across sites and inclusion of a known-biased core `[should fix]`**
  Tunu is averaged across 4 cores (reducing random measurement noise), while the other 6 sites have 1 core each—including `ht95` (~4 samples/yr) and `ngrip1` (~5 samples/yr, carrying an explicit author warning of ammonium bias). In an unweighted mean of site z-scores, a noisy single-core site (or biased NGRIP1) carries the same weight as all four Tunu cores combined.

* **Non-stationary 20th-century trends inflating `s` for nitrate, black carbon, and sulphur `[should fix]`**
  The 30-year background MAD `s` is computed around a flat median `m` with no detrending. During rapid anthropogenic rises (industrial coal BC around 1880–1920; NO3 and S around 1950–1980), trend slope inflates `s` and suppresses z-scores during high-trend eras relative to flat pre-industrial eras, distorting the 1800–1990 rank comparison for those secondary tracers (and for BC specifically right around 1908).

* **Yearly averaging dilutes a short plume `[minor]`**
  Tunguska occurred on 30 June 1908. Averaging a days-to-weeks tropospheric plume over 12 months dilutes its signal against a full year of summer ammonium background (**false negative** risk). The plan acknowledges this trade-off, which is reasonable for flux estimation, but it means a null result only rules out a large *annual-equivalent* deposit, not a sharp brief spike.

* **Year-boundary conventions across laboratories `[minor]`**
  If some cores place `.0` at winter minimum (Jan 1) and others at summer maximum (July 1)—or if GICC05 b2k annual layer markers sit at winter/spring—a June 30, 1908 spike can either sit cleanly inside 1908 or get split right across a year boundary, reducing its single-year peak by up to half.

---

### 2. Decision rules that are unfair, miscalibrated, or do not test what they claim

* **The "Ordinary" verdict is wrongly converted into a hard upper bound of `1` typical year `[must fix]`**
  In the Younger Dryas section, an "Ordinary" verdict (`fraction > 0.10`) is interpreted as *"Tunguska left less than [one typical year's worth]"* because `k = 1` is called Elevated in 82% of trials. That is statistically invalid:
  1. An 82% detection rate still leaves an **18% false-negative rate** at `k = 1`, and much higher for `k = 0.6–0.9`.
  2. It ignores the actual observed outcome: a fraction of `0.11` (borderline Elevated) and a fraction of `0.85` produce the exact same claimed bound!
  3. It assumes all 7 sites receive the pulse; in the plan's own half-site simulation, even `k = 2` is only Elevated 64% of the time.
  Instead, derive a proper upper confidence limit on `k` conditioned on the **observed** network score (or observed `E` and its cross-site uncertainty).

* **"What would count" does not test "airburst vs. forest fire" and contradicts ice-core chemistry `[must fix]`**
  The section states that *"exceptional [NH4], in most sites, with nitrate elevated too"* counts toward *"an airburst marks the ice"*, while *"exceptional in ammonium with a large rise in black carbon"* is *"in between"*. Both halves are flawed:
  1. **North American boreal fire plumes routinely elevate BOTH ammonium and nitrate** in Greenland ice. Seeing elevated nitrate alongside exceptional ammonium does *not* distinguish an airburst from a major 1908 boreal fire (1908 saw major fires in British Columbia, Minnesota, and Michigan).
  2. **Around 1908, Greenland black carbon was near its early-20th-century industrial coal peak** (several times above pre-industrial levels). That elevated industrial background makes a real 1908 forest fire produce a much smaller relative BC anomaly than a pre-industrial fire would. Thus, a genuine 1908 wildfire can easily look like "high NH4 + unremarkable BC"—leading to a false conclusion in favor of an airburst.
  3. Furthermore, *"in most sites"* and *"a large rise in black carbon"* are left undefined.

* **Primary verdict tests only ammonium, despite Melott et al.'s primary mechanism being nitrate `[should fix]`**
  Melott et al. (2010) proposed atmospheric shock-heating ($N_2 + O_2 \to NO_x \to$ **nitrate**) as the airburst mechanism and explicitly called the GISP2 ammonium spike *"unexplained"*. Testing ammonium as the sole primary variable is well-motivated by the lab's Younger Dryas ammonium finding (#43/#60), **not** as a direct test of the shock-nitrate airburst mechanism. The plan should explicitly frame the primary test as testing whether 1908 shows a *Greenland-wide ammonium anomaly* (for the YD comparison), rather than claiming ammonium alone validates an airburst signature.

* **Overly harsh "Exceptional" threshold (`<= 0.02`) under overlapping windows `[should fix]`**
  Because of the double-counting/self-competition flaw in §1, the nominal 2% threshold effectively requires beating all but at most *one* historical fire year in 191 years (and sometimes zero, if 1907 beats 1908). Even a 2× annual pulse across all 7 sites only passes 71% of the time in the (already optimistic) simulation. Declustering or using non-overlapping windows fixes this cleanly.

---

### 3. Ambiguities where an independent programmer could compute something different

* **Reference window endpoints: inclusive or exclusive? `[must fix]`**
  *"every window from 1800 to 1990"* and *"about 190 windows"*. A programmer using `range(1800, 1990)` gets 190 windows; `range(1800, 1991)` gets 191 windows. This directly changes the denominator of `fraction` and can flip a borderline rank (e.g., `4/190 = 0.021` vs `3/190 = 0.0158`, or `19/190 = 0.100` vs `20/191 = 0.1047`).

* **Sensitivity simulation specification is under-specified `[must fix]`**
  In item 7 (*Sensitivity*), an independent programmer must guess:
  1. Are **all** window scores recomputed after injecting the pulse (including `y−1`, `y+1`, and windows whose 30-year background contains the pulsed year), or only window `y`'s score?
  2. What is the exact pool of eligible windows *"outside 1890 to 1925"* (inclusive or exclusive? Restricted to windows that already have a valid network score?)?
  3. What happens if the randomly selected year (`y` or `y+1`) is **missing** in a core (skip core, inject into the other year, or set to `0 + pulse`)?
  4. Is the `1880 to 1930` median computed inclusive of endpoints and after date-shifting?
  5. For exact reproducibility with `default_rng(100)`, the exact draw order is unspecified (if only statistical agreement is expected, say so explicitly).

* **Reference window set for single-site, core-by-core, and subset ranks `[must fix]`**
  For items 1 (per-site rank/fraction), 3 (leave-one-out, 5 DRI sites, 2 other sites), 4 (Summit and B20), and 5 (sulphur):
  1. Is a site's (or core's) rank computed over all 1800–1990 windows where *that site/core* has a score, or only windows where the *full network* has a score?
  2. What is the minimum-site threshold for the subset network scores? The main rule requires `>= 5` sites, which is impossible for *"the two other sites alone"* (NEGIS + NGRIP) and potentially restrictive for leave-one-out or the 5 DRI sites.

* **Katmai shift formula (`1913` vs. `1912` target) `[should fix]`**
  *"Katmai in June 1912... If that year is 1914 or 1915, the core's dates are taken to run late by one or two years"*. Only by reading the example (`b20` had 1915 and moved back 2) can a programmer deduce that 1914 shifts by `−1` (target = 1913) and 1915 shifts by `−2` (target = 1913), rather than `peak − 1912`. State the formula explicitly (`shift = peak_year - 1913` if `peak_year in {1914, 1915}` else `0`) and specify tie-breaking.

* **Denominator of the half-present rule `[should fix]`**
  *"at least one of its samples has one and at least half of them do."* Confirm explicitly that the denominator is **all rows in `<core>.tsv` with `floor(date) == year`** (including rows where that chemical is empty, or all chemicals are empty), and that "at least half" is `>=` (`2 * n_valid >= n_total`). Also state explicitly that if *both* `y` and `y+1` are missing, the window has no score.

* **Definition of `E` (size): raw median vs. geometric median, and missing-background cores `[should fix]`**
  In item 2, *"the median of its background years"* could be implemented as `median(raw_background_values)` or `exp(m)` (geometric median of logs); for an even number of background years (e.g., 30), they differ slightly. Also specify whether cores failing the `>= 20` background years or `s > 0` check are excluded from `E`.

* **Minor ambiguities `[minor]`**
  * Confirm standard even-`n` median (`numpy.median`, arithmetic average of the two middle values).
  * Confirm whether *"in its own top tenth"* means `fraction <= 0.10` (matching Elevated).
  * Confirm whether `sulphate` (NGRIP1, B20) occupies the same column name as `sulphur` (DRI cores) in the standard TSVs.
  * Note a minor transparency discrepancy in "What has been seen before the lock": it says *"No ammonium... value dated 1895 to 1920"* has been seen, yet the blind run computed scores for windows `1894` and `1895` (which directly use 1895 and 1896 values!). Clarify that *raw values* in 1895–1920 were not inspected, while *scores* outside 1905–1912 were.

---

### 4. Important missing checks (in order of importance, feasible with the named public data)

1. **Multi-eruption dating verification (1815 Tambora, 1883 Krakatoa, 1912 Katmai) and pre-lock Tunu inter-core alignment check `[must fix]`**
   Before shifting `tunu2022b`, `ht95`, and `tunu_n` across 1800–1990, check where the 1815–1816 and 1883–1884 sulphur peaks land in *every* core with sulphur (not just B20), and check whether any core runs **early** (Katmai in 1911). Crucially, using the 4 co-located Tunu cores outside 1905–1912 (possible *before* unblinding!), compute lag-correlations (−2, −1, 0, +1, +2 yr) between `tunu2022b`/`tunu_n` and `tunu2013`/`tunu2022a` in ammonium and sulphur. This directly tests whether shifting them by 1–2 years fixes a real constant offset or breaks an already-aligned chronology.

2. **Common-overlap / matched-site-set sensitivity check `[must fix]`**
   Re-run the rank test restricted strictly to the exact subset of sites that have a valid score in 1908 (and only across reference windows where *all* of those same sites have valid scores), eliminating the unequal-`N` variance distortion.

3. **Independent audit of the ingestion step (`data/standard/*.tsv`) `[must fix]`**
   The plan notes that raw-file ingestion is not replicated. For 13 heterogeneously formatted files—especially NEGIS and NGRIP1 depth-to-age interpolation (where GICC05 b2k-to-CE conversion can easily introduce a 1-year off-by-one error)—have the second model or an independent script verify raw-to-standard conversion on spot-checked depths/years outside 1905–1912 (including 1815, 1883, 1912, and 1895).

4. **Chemical-ratio fire fingerprinting (`NH4 / BC` and `NO3 / NH4` excess) `[should fix]`**
   On the 4 test sites that have both NH4 and BC (NEEM, Tunu, Humboldt, Hans Tausen), compare the excess `NH4 / excess BC` and `excess NO3 / excess NH4` of 1908–1909 directly against the top known boreal-fire windows (1894/1895, 1888, 1862, 1836) *and* against industrial-era fires (e.g., 1910–1930) where BC background is similarly elevated. This is far more informative than reporting raw BC ranks alone.

5. **Sub-annual peak & timing check (post-June 30, 1908) `[should fix]`**
   For the high-resolution cores (`>= 6` samples/yr: NEEM, Tunu, Humboldt, ACT11d, NEGIS), check the **annual maximum sample** (or 2nd-half-year mean, `.50` to `.99`) as a pre-registered secondary diagnostic. This tests (a) whether a sharp, brief plume was washed out by 12-month averaging, and (b) whether any 1908 spike actually falls *after* 1908.5 (a spike in spring 1908 cannot be Tunguska).

6. **Inspect 1906–1912 core-by-core (specifically checking for 1910 "Big Burn" leakage) `[should fix]`**
   Tabulate/plot yearly ammonium and BC for 1906–1912 (both unshifted and shifted) to ensure that a large 1910 fire signal is not leaking into 1909 or 1908 through dating error or the Katmai shift.

7. **Positive-control coherence check on `summit2010`/`summit2023` and on a known Greenland-wide fire year `[minor]`**
   Verify (a) whether `summit2010` and `summit2023` actually reproduce the GISP2 1908–1910 ammonium spike (if they do not, the motivating GISP2 spike may be a GISP2-specific artifact or a 1910 fire caught in its 2-year 1908–1910 sample), and (b) whether NEGIS (unaligned) and NGRIP1 (biased NH4) show coherent peaks during the known 1894/1895 Greenland-wide ammonium event.

8. **Sensitivity to `<= 0` clamping and seasonal coverage `[minor]`**
   Check how many samples are dropped as `<= 0` per core, compare clamping to half the minimum positive value vs. dropping, and check whether any year in 1907–1910 is missing a seasonal block under the half-present rule.

---

### 5. Soundness of the Younger Dryas conversion, and how to word its limits

**Verdict: Not sound as currently formulated `[must fix]`.**

The arithmetic for NGRIP's YD flux ratio is right ($29.7 \times 0.069 / (11.0 \times 0.081) = 2.30$, so $F = 1.3$ pre-YD years' worth extra). However, the conversion from `E` to airbursts per year has **four major flaws** beyond the caveats already listed:

1. **Unnecessary and likely biased dimensionless mixing of sites and eras:** You assume a typical year around 1900 brought the same ammonium flux as a typical pre-YD year, *and* you divide NGRIP's dimensionless `F` by the 7-site median dimensionless `E`. Yet NGRIP's ~1900 snowfall (~0.19 m ice/yr) is **~2.3× higher** than pre-YD NGRIP (0.081 m/yr), and the 7 test sites have very different accumulation rates and baseline concentrations. You already have NGRIP1's ~1900 ammonium concentration *and* GICC05 annual layer thickness (accumulation rate) in your dataset—you can compute the **actual ~1900 NGRIP ammonium flux** ($\mu\text{g m}^{-2}\text{yr}^{-1}$) directly (and similarly for any core with accumulation data) rather than assuming equality.
2. **Physical mismatch between tropospheric lifetime and a "raised steady level":** Ammonium has a tropospheric lifetime of days to ~1–2 weeks and no multi-year stratospheric reservoir. Even 1–2 Tunguska-like airbursts per year would produce **intermittent sharp spikes**, not *"a raised steady level with few short spikes"* (unless the YD NGRIP sampling/diffusion completely smoothed out annual spikes, or the airbursts were far more frequent and smaller—or the YD baseline rise is instead driven by climate/ecosystem/biomass-burning/dust-transport changes).
3. **Single-location transport geometry (1–2+ orders of magnitude uncertainty):** Tunguska occurred in central Siberia (~4,500–5,000 km from Greenland, largely cross-wind/downwind of Greenland's dominant North American airmass pathways). An identical airburst over Canada or the Arctic would deposit far more in Greenland; one in the tropics or Southern Hemisphere would deposit near zero. Extrapolating from one Siberian site to global annual impact rates carries **at least 1–2 orders of magnitude** of geometric/meteorological uncertainty alone.
4. **Invalid upper bound in the "Ordinary" case:** As noted in §2, using the 82%-power point (`k = 1`) as a hard upper bound ignores the observed score and its uncertainty.

**How I would word its limits:**
> "This conversion is a back-of-the-envelope order-of-magnitude illustration, not a rate measurement. Comparing 1908 in central Siberia to a 150-year Younger Dryas plateau requires assuming (i) that absolute ammonium flux per event scales linearly without saturation, (ii) that atmospheric transport and wet/dry scavenging in glacial Younger Dryas circulation match ~1900, and (iii) that Tunguska's Siberian location represents the average Greenland deposition of global airbursts—a geometric assumption uncertain by at least an order of magnitude on its own. Moreover, because tropospheric ammonium lasts days to weeks, ~1–2 airbursts per year would leave episodic spikes rather than the steady baseline elevation seen in #43 unless obscured by thin glacial layers and sampling resolution. Where possible, fluxes are compared in absolute mass per unit area per year (using ~1900 accumulation rates) rather than dimensionless ratios, and any upper bound under an 'Ordinary' result reflects a statistical confidence bound on the observed excess rather than the nominal 82% power threshold."

---

### 6. Errors or questionable accounts of the literature and ice-core practice

* **Omission of the ice-core literature refuting Melott et al. (2010) `[should fix]` — *Confidence: High***
  Relying only on the abstract of Melott et al. (2010) misses subsequent ice-core work (notably **Wolff et al. 2012, *GRL***; **Duderstadt et al. 2014, 2016, *JGR***; and **Legrand et al. 2016** on Greenland biomass-burning tracers) showing that sharp nitrate+ammonium spikes in GISP2H/GISP2 previously attributed to ionization/shock events (including solar proton events and airbursts) are standard signatures of **North American boreal biomass-burning plumes**. Also note that the motivating GISP2 sample *"spanning 1908 to 1910"* is a ~2-year biannual sample with ±1–2 yr dating uncertainty—meaning it could easily capture either 1908 North American fires or the massive **1910 Big Burn**.

* **Characterization of DRI chronologies as hand-counted and drifting by 1–2 years at 1912 `[must fix]` — *Confidence: High***
  Modern DRI cores (`neem_s1`, `tunu2013`, `tunu2022a`, `tunu2022b`, `humboldt`, `summit2010`, `summit2023`) are **not** left as free-running hand counts that drift 1–2 years at 1912; they are normally synchronized to exact historical volcanic tie-points including **Katmai (1912)**, **Krakatoa (1883)**, and **Tambora (1815)**. Seeing `tunu2022b` (a modern 2022 DRI core) peak in 1914 sulphur is therefore a major diagnostic red flag: either its file is preliminary/unanchored, there is an ingestion bug, or **early-20th-century industrial coal sulphur** (which rose steeply through 1910–1920 in Greenland) exceeded a split 1912/1913 Katmai yearly mean in 1914. Using raw total sulphur `argmax` instead of non-sea-salt / baseline-subtracted volcanic sulphur is not standard ice-core practice around 1912.

* **Overstating black carbon's ability to separate fires from airbursts in 1908 `[must fix]` — *Confidence: High***
  As shown by McConnell et al. (2007, *Science*), Greenland black carbon around **1880–1920 was dominated by North American industrial coal combustion** (elevated several-fold above pre-industrial levels). In 1908, a boreal forest fire sits on top of a huge industrial BC baseline (and smoldering boreal fires also have high NH4/BC ratios), making BC a weak discriminator for a 1908 wildfire.

* **Treating elevated nitrate alongside ammonium as supporting an airburst `[should fix]` — *Confidence: High***
  Boreal wildfire plumes in Greenland ice elevate **both** ammonium and nitrate together, while nitrate at low-accumulation sites (Tunu, Hans Tausen, B20) also suffers post-depositional photolytic loss/smoothing. Elevated nitrate + ammonium is therefore consistent with *either* an airburst or a wildfire, not uniquely diagnostic of an airburst.

* **Layer counting with ammonium `[minor]` — *Confidence: Medium-High***
  Greenland multi-parameter layer counting relies primarily on seasonal dust/Ca, sea-salt Na/Cl, $H_2O_2$, $\delta^{18}O$, and $nssS$ / $NO_3^-$; ammonium is generally recognized as spike-dominated and is not used on its own to place year boundaries in modern DRI chronologies (though an unflagged spike can occasionally cause a counting error in simpler schemes).

* **Using raw total sulphur vs. sulphate without sea-salt correction `[minor]` — *Confidence: High***
  DRI ICP-MS measures total S while NGRIP1/B20 IC measure $SO_4^{2-}$; both include sea-salt sulphur (significant at lower-elevation/coastal sites like ACT11d and Hans Tausen) as well as industrial pollution S. That explains why raw yearly sulphur is a noisier volcanic marker than standard baseline-subtracted `nssS`.

---

### The three changes I would make first

1. **Fix the rank test's overlapping-window self-competition and unequal-site-count bias** (and align the sensitivity simulation with synchronous 1908 timing). Exclude `1907` and `1909` from the reference set and decluster historical overlapping windows (or test non-overlapping 2-year windows / single-year peaks), and restrict the reference windows to the exact same site subset that is valid in 1908.
2. **Audit the Katmai lining-up rule and the un-replicated ingestion before shifting any core.** Check 1815 (Tambora), 1883 (Krakatoa), and 1912 (Katmai) using baseline-subtracted sulphur across all cores, allow forward as well as backward checks, verify `tunu2022b`/`tunu_n` against `tunu2013`/`tunu2022a` via pre-lock lag correlations, and spot-check raw-to-standard ingestion (especially NEGIS and NGRIP1 depth-age interpolation).
3. **Lock down the specification ambiguities and fix the fire/YD interpretation rules.** Explicitly specify inclusive window bounds (`1800..1990`), the sensitivity-test recomputation rules, subset site thresholds, raw vs. log median for `E`, and clamping (rather than dropping) `<= 0` values; add a fire-ratio check (`NH4/BC` and `NO3/NH4` vs. known fire years) acknowledging 1908 industrial BC; and compute the Younger Dryas comparison in absolute fluxes with a statistical confidence bound derived from the observed result rather than the 82%-power threshold.
