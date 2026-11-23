<!-- {"vendor": "google", "model": "gemini-4-neon", "utc": "2026-11-23T14:49:55.835289+00:00", "input_tokens": 3209, "output_tokens": 33640, "cost_usd_list_price": 0.5142} -->

### 1. Flaws That Could Produce a False Positive or a False Negative

- **Metric `P` tests for an isolated 20-year spike, not a century-long rise, and cannot separate a transient pulse from a permanent stadial step — [must fix]**
  - Question #43 found ammonium elevated *for about a century*. Yet the deciding metric `P = ln(max(after) / median(before))` looks only at the **single highest 20-year bin** out of 10.
  - *False positive for "general"*: A permanent step-up into the stadial (e.g., from reduced snowfall or background shift) or a single 20-year boreal wildfire plume anywhere in the 200 years produces a high `P` even when nothing resembles the YD's ~100-year elevated interval.
  - *False negative for "general" and distorted rank for GS-1*: Greenland $\text{NH}_4^+$ is punctuated by sharp, heavy-tailed fire spikes. In quiet ice, random single-bin fire spikes inflate the 75th percentile of a 10-bin maximum, burying a real, sustained +40–60% century-long rise. Worse, a single massive wildfire in one 20-year bin of *any* other cooling can beat GS-1's sustained 100-year high on `P`.
  - Additionally, non-overlapping 20-year bins suffer from **phase aliasing**: a 20-year peak split evenly across two adjacent bins loses up to half its excess relative to one aligned with the grid, arbitrarily shifting individual event values and GS-1's rank.

- **Unbuffered `before` window `[t, t+100)` is contaminated by both gradual stadial onsets and preceding abrupt warmings — [must fix]**
  - *Onset smearing (false negative for non-GS-1 coolings; artificial rank boost for GS-1)*: Class `b` stadial onsets have 40–60 years of definition uncertainty (and NGRIP-to-NEEM synchronization adds further decades of offset in deep glacial ice). With `[t, t+100)` directly abutting `t`, the first 2–3 before-bins (`[t, t+60)`) frequently sit *inside* the cooling transition itself, biasing `median(before)` toward post-onset levels and muting `P`. GS-1 has only 4 years of definition uncertainty and a sharp onset, so it escapes this attenuation—making GS-1 look artificially larger than the other 24 coolings.
  - *Preceding warming contamination (false negative for short interstadials)*: Rule 2 only excludes other events strictly inside `(t, t+100)`, allowing an abrupt interstadial *warming* (GI onset) right at `t + 100` (zero buffer). Several of the 25 selected coolings follow short interstadials of ~100–250 years (e.g., GI-5.1, GI-9, GI-10, GI-15.1, GI-15.2, GI-17.2, GI-18). Since Fischer et al. (2015) report that fire activity and $\text{NH}_4^+$ spike at abrupt warmings, the `before` window of short interstadials sits on the warming-induced high, inflating `median(before)` and depressing `P`.
  - *Why the calcium control does not clear this flaw*: Dust ($\text{Ca}^{2+}$) jumps by 5–10× and stays permanently high throughout a stadial, so contaminating 1–2 before-bins barely dents calcium's `P`. A modest, transient ammonium peak is far more vulnerable to before-window contamination than a 10× dust step.

- **Regime-mismatched and non-stationary "quiet times" null — [must fix]**
  - Every cooling event compares a **stadial** `after` window against an **interstadial** `before` window. By contrast, the ~3,072 quiet times pool the entire 97 kyr record and are heavily dominated by long glacial stadials (e.g., GS-2, GS-3, GS-22), where `before` and `after` share the same climate state.
  - If biogenic $\text{NH}_4^+$ background generally *drops* from interstadial to stadial, `P` at coolings is systematically shifted downward relative to quiet times (false negative for a transient peak riding on a falling baseline). Conversely, if relative variance (log-scale spikiness) or noise floor differs across MIS 2–5 or between stadials and interstadials, the true null probability of exceeding the pooled 75th percentile is not 0.25 in either direction (false positive or false negative).

- **Missing-bin and single-row-bin bias in the `max` estimator — [should fix]**
  - Requiring "at least 8 of 10 after bins" introduces systematic order-statistic bias: $\mathbb{E}[\max(X_1,\dots,X_8)] < \mathbb{E}[\max(X_1,\dots,X_{10})]$, penalizing windows with missing bins.
  - Conversely, forming a 20-year bin from a single surviving 10-year row doubles its sampling variance (and inflates extreme fire-spike values) relative to a two-row mean, biasing `max` *upward*.
  - Excluding windows with any `<= 0` bin selectively truncates low-concentration stadial quiet times, shifting the empirical 75th percentile.

- **Overlapping quiet times invalidate the nominal binomial variance — [should fix]**
  - The 3,072 quiet times use 300-year windows stepped every 20 years (~15× overlap, plus multi-century climate autocorrelation), so the effective sample size behind the empirical 75th percentile $\hat{q}_{0.75}$ is far smaller (~200 or fewer). Estimation error in $\hat{q}_{0.75}$ induces positive correlation across the 24 binary exceedance indicators, making the $\text{Binomial}(24, 0.25)$ test anticonservative (inflated false-positive rate for "Often").

---

### 2. Problems with the Decision Rules

- **"Stands out" = Rank 1 in both cores is far too fragile for a genuine anomaly, yet blind to effect size — [must fix]**
  - Suppose GS-1 is genuinely anomalous at the **97th percentile** of quiet ice (a 1-in-33 event), and all 24 other coolings are pure null noise. Even in a *single* core, the probability that at least one of the 24 other coolings beats GS-1 purely by chance is $1 - 0.97^{24} = 52\%$. Requiring Rank 1 in *both* imperfectly correlated cores pushes the false-negative rate for a genuine anomaly even higher—especially under a heavy-tailed 10-bin maximum where one isolated wildfire spike in either core destroys "Stands out".
  - Conversely, Rank 1 ignores the **gap**: a trivial 0.01 edge over Rank 2 counts the same as a 3× separation, and GS-1 doesn't even need a high quiet-time percentile to win Rank 1. Meanwhile, Rank 1 in NGRIP + Rank 8 in NEEM collapses to "Ordinary among coolings", the same label as Rank 25 of 25.

- **Dichotomizing at the 75th percentile throws away power and can misclassify in both directions; the 2/3 cutoff for "General" is calibrated for dust, not ammonium — [must fix]**
  - *False negative*: If every single one of the 24 coolings rises consistently to the 65th–74th percentile (an unmistakable universal effect), the count $\ge 0.75$ is **0/24 → "Not seen"**. Even a real, universal $+0.8\sigma$ shift at every cooling only crosses the 75th percentile ~55% of the time (~13/24), failing "General" ($\ge 16/24$ in both cores).
  - *False positive*: Eleven coolings at the 76th percentile and thirteen at the 5th percentile (median cooling *below* quiet ice!) still passes **"Often"** (11/24, exact $p = 0.021$).
  - Testing the continuous location/distribution of percentiles (or `P` values) avoids both pathologies.

- **"Not seen" + "Stands out" conflates failure to reject $H_0$ with evidence of absence — [should fix]**
  - With $n = 24$, **10 of 24** coolings in the top quarter (vs. 6 expected by chance) gives exact $p = 0.0547$, which fails the $p < 0.05$ cutoff. Getting 10/24 in both cores—or 13/24 in NGRIP and 10/24 in NEEM—yields **"Not seen"**, which the plan interprets (when paired with Rank 1) as evidence that the YD is an anomaly. Hard AND-gates across two cores amplify this cliff-edge fragility.

- **The verdict table ignores deglacial climate-state confounding that is acknowledged in Known Weaknesses — [should fix]**
  - Mapping "Not seen + Stands out" directly to "an anomaly among coolings" does not test whether GS-1 simply reflects a warmer, higher-vegetation deglacial baseline (as opposed to full-glacial MIS 2–4 coolings), even though the dataset contains warmer MIS 5 coolings (GS-20 to GS-23.2) and major interstadials (GI-8, GI-12) that allow a direct check.

---

### 3. Ambiguities for an Independent Programmer

- **Exact vs. normal-approximation binomial test (flips the verdict at $k = 10/24$) — [must fix]**
  - The plan says "one-sided binomial test against 0.25, p < 0.05" without specifying *exact* upper-tailed. At $k = 10, n = 24$, an exact upper-tailed binomial test gives $p = 0.0547$ (fails), whereas a normal $z$-test gives $p = 0.0297$ (passes) and a continuity-corrected $z$-test gives $p = 0.0495$ (passes). Two competent programmers can produce different verdicts from identical numbers.

- **Handling of non-positive values ("all positive") — [must fix]**
  - "The measures need at least 8 of the 10 after bins and 4 of the 5 before bins, all positive" has three reasonable implementations when a `<= 0` value appears: (a) disqualify the entire window if any non-missing bin is `<= 0`, (b) treat `<= 0` bins as missing and check if $\ge 8$ / $\ge 4$ positive bins remain, or (c) drop `<= 0` 10-year rows before forming bins.

- **Rounding rule for `t`, Rule 2 boundary evaluation, and `"other"` events — [should fix]**
  - "Rounded to the nearest 10 years" does not specify tie-breaking for ages ending in `5` (Python's round-half-to-even `round(x, -1)` vs. round-half-up).
  - Unspecified whether Rule 2's strict windows `(t - 200, t)` and `(t, t + 100)` use raw onset ages or rounded `t` (both for the candidate event and for neighboring events), and whether `"other"` rows (GS-2.1a, GS-2.1b) count as "listed events" in Rule 2.
  - Clarify whether the independent programmer should derive the 25 events from Rules 1–3 (and assert exact match) and specify the exact column values in `events.tsv` that identify stadial onsets and GS-1.

- **How missing events affect `n`, cutoffs, rank ties, and quiet-time filtering — [should fix]**
  - If 1–2 of the 24 other coolings fail the completeness check in one core, is `n` for "two-thirds", the binomial test, and `ceiling(n/4)` the number of *valid* coolings in that core, or fixed at 24/25 (treating missing as failures)?
  - How are ties in GS-1's rank broken (competition `1,1,3`, average `1.5,1.5,3`, or max)?
  - The calcium control reports one single number (`3,072 quiet times`), leaving it ambiguous whether quiet times are filtered *per core* (as "in the same core" suggests) or restricted to timestamps valid in *both* cores.

- **Unit conversion (`ka` to integer `yr b2k`) — [minor]**
  - The PANGAEA age column is in floating-point `ka` (e.g., `10.29`), while formulas use integer `yr b2k`. Naive `int(age_ka * 1000)` triggers IEEE-754 truncation errors (e.g. `10289`) unless `round(age_ka * 1000)` is specified.

- **Unspecified details in "Reported alongside" items #2–#4 — [minor]**
  - Item #2 (300-yr after-window): does the quiet-time exclusion window widen from `[t - 300, t + 200]` to `[t - 400, t + 200]`, or stay fixed (leaving zero buffer at `t - 300`)?
  - Item #3: is "size of the peak" raw concentration, `max / median`, or `max - median`? Is "years after the onset" the start (`20k`), midpoint (`20k + 10`), or end (`20k + 20`) of bin `k`, relative to raw or rounded `t`?
  - Item #4: GI-1d lasted only ~121 years, so the second half of a 200-year after-window falls back inside warm GI-1c; clarify whether it is still evaluated over the full 200 years.

---

### 4. Important Missing Checks (in Order of Importance; Feasible with Named Data)

1. **Century-scale window + transient-pulse vs. permanent-step test — [must fix]**
   - Compute the maximum overlapping **80- or 100-year mean** within `[t - 200, t)` relative to `before` (matching #43's actual ~100-year signal).
   - For stadials lasting $\ge 400$ years, also compare `[t - 200, t)` against the **subsequent stadial baseline** `[t - 400, t - 200)`. This directly distinguishes a century-long transient pulse (rises then falls back down) from a permanent stadial step-change.

2. **Additional chemical controls already in the PANGAEA files ($\text{NO}_3^-$, $\text{Na}^+$, conductivity) — [should fix]**
   - Nitrate and sodium are columns in the exact same NGRIP and NEEM files. Running the same analysis on $\text{NO}_3^-$ (another nitrogen species much less tied to biomass burning than $\text{NH}_4^+$) and $\text{Na}^+$ (sea salt / transport + accumulation) tests whether any "general" rise—or any GS-1 anomaly—is specific to ammonium (fires/soils) rather than generic snowfall dilution or atmospheric transport.

3. **Null stationarity, regime-matched quiet times, and a continuous distribution test — [should fix]**
   - Stratify quiet times by climate regime (interstadial quiet times vs. stadial quiet times) and glacial epoch (MIS 2–5) to check whether `P`'s null distribution is stationary.
   - Supplement the dichotomized 0.75 count with a **continuous test** of the 24 coolings' median or mean `P` (and percentiles) against quiet times using block-resampling or non-overlapping quiet windows.

4. **Confounder and sensitivity diagnostics across the 24–25 coolings — [should fix]**
   - Shift the `before` window back by 40–60 years (e.g., `[t + 60, t + 160)`) to test onset-smearing sensitivity, and compare class `a` vs. class `b` coolings.
   - Correlate `P` and `R` across the 24 coolings against: (a) preceding interstadial duration (checks GI-warming contamination of `before`), (b) event age `t` (checks thinning/climate drift), (c) `before` baseline $\text{NH}_4^+$ (checks dependence on ambient vegetation/climate state), and (d) number of missing/single-row bins.
   - Check the **inter-core correlation** of `P`, `R`, and peak timing `k` between NGRIP and NEEM across the 24 events: a genuine Greenland-wide response should produce correlated rankings and aligned peak lags across both cores.

5. **Superposed epoch composite profile and effect-size gap for GS-1 — [should fix]**
   - Compute the lag-by-lag composite (median and IQR of `ln(bin_k / median_before)` across the 24 coolings from `t + 100` to `t - 200`) plotted/tabulated alongside GS-1. This immediately shows whether other coolings exhibit a delayed hump, a step at lag 0, a sawtooth trend, or flat noise.
   - Report how far GS-1 sits above the distribution of the other 24 coolings (e.g., standardized gap / IQR distance above median and above Rank 2), not just its integer rank.

6. **Overlapping 20-year bins (10-year step) — [minor]**
   - Compute `P` on overlapping 20-year means shifted by 10 years (using the 10-year rows directly) to confirm that neither GS-1's rank nor the "general" count is an artifact of 20-year grid alignment.

---

### 5. Issues in the Literature Summary

- **Fischer et al. (2015, *Nature Geoscience* 8:723–727): scope and background/peak decomposition — [should fix] (High confidence)**
  - Calling Fischer et al.'s data "this record" (right after referencing three cores and before listing NGRIP and NEEM) is imprecise: Fischer et al. analyzed high-resolution (annual/sub-annual) **NGRIP** CFA data only, not NEEM and not 10-year averages.
  - More importantly, Fischer et al. explicitly decomposed NGRIP $\text{NH}_4^+$ into **low-frequency biogenic soil background** versus **short-lived (1–few year) biomass-burning peaks**, and accounted for wet vs. dry deposition / accumulation changes. Their finding that fire activity rose at rapid warmings and was low in stadials (YD included) applies specifically to *isolated high-frequency fire peaks* separated from background—whereas this plan's decadal averages lump background and fire peaks together.

- **Snowfall drop raising $\text{NH}_4^+$ concentration "for the same fallout" — [minor] (High confidence)**
  - In Known Weaknesses, saying lower snowfall "raises concentrations for the same fallout" is mathematically true by definition ($C = F/A$) but physically oversimplified for Greenland $\text{NH}_4^+$. Unlike dust ($\text{Ca}^{2+}$), $\text{NH}_4^+$ in Greenland is **predominantly wet-deposited** (Alley et al. 1995; Fuhrer et al. 1996; Fischer et al. 2015), meaning wet fallout scales roughly with snowfall for constant atmospheric concentration rather than doubling ice concentration (though dry deposition contributes a partial inverse-accumulation boost in low-accumulation stadials).

- **Timescale equivalence for NEEM and exclusion rationale for GISP2 — [minor] (High confidence)**
  - Saying "two cores ... on one timescale" glosses over the fact that Rasmussen et al. (2014) Table 2's onset ages and definition uncertainties (`a`, `b`, `GS-1: 4 yr`) were defined primarily on NGRIP/GRIP; transferring GICC05modelext to NEEM via volcanic tie-points (Rasmussen et al. 2013) adds synchronization uncertainty of up to several decades between tie-points in deeper glacial ice.
  - Saying GISP2 is excluded because "its ages are on another timescale" is true of the older public Mayewski GISP2 chemistry file, not of GISP2 in general: GISP2 was explicitly synchronized onto GICC05modelext in the companion paper to Rasmussen et al. (2014) (Seierstad et al. 2014, *Quat. Sci. Rev.* 106:29–46), and Rasmussen et al. Table 2 lists GISP2 depths alongside NGRIP. Leaving GISP2 out is a reasonable scope choice given the files already on hand, just slightly overstated as stated.

---

### Three Changes to Make First

1. **Match the primary metric to the actual hypothesis:** Replace (or co-primary-register alongside `P`) the single 20-year max with a **maximum overlapping 80- or 100-year mean** within `[t - 200, t)`, plus a check against the **post-200-year stadial baseline** `[t - 400, t - 200)`, so the test actually detects a century-long transient rise rather than a single 20-year wildfire spike or a permanent stadial step.
2. **Fix `before`-window contamination and the null comparison:** Buffer the `before` window away from both `t` (for class `b` onset smearing) and preceding GI warmings (or stratify/check short interstadials and add $\text{NO}_3^-$/$\text{Na}^+$ controls from the same files), and replace the dichotomized $\text{Binomial}(24, 0.25)$ test with a **continuous location test** against climate-matched/non-overlapping quiet times.
3. **Replace the brittle "Rank 1 in both cores" rule and lock down code ambiguities:** Evaluate whether GS-1 stands out using its **effect-size gap** (e.g., distance above the distribution of the 24 other coolings) alongside rank so one lucky wildfire spike cannot erase a real anomaly, and explicitly specify exact upper-tailed binomial (if retained), `<= 0` handling, half-way rounding, and missing-event `n` rules before locking.
