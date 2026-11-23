<!-- {"vendor": "google", "model": "gemini-4-neon", "utc": "2026-11-23T16:23:20.065226+00:00", "input_tokens": 3065, "output_tokens": 35410, "cost_usd_list_price": 0.5403} -->

### 1. Flaws that could produce a false positive or a false negative

1. **Radiocarbon truncation mismatch between real data and simulated null** — **must fix**
   - Real dates are truncated at `9,000 14C BP` (~10,150–10,200 cal BP), so virtually no real dates fall below ~10,150 cal BP. However, the null draws `N_bins` calendar ages over `9,500–16,500 cal BP` (where `9,500 cal BP ≈ 8,500 14C BP`) and **never applies the `9,000–13,800 14C BP` filter** to the simulated dates.
   - Because the exponential trend grows rapidly toward younger ages, roughly **25%–45% of all simulated bins** will be wasted in `9,500–10,150 cal BP`, leaving far fewer simulated bins around `12,850 cal BP` than actually exist in the real data.
   - **Effect:** Artificially inflates the null variance of `D(T*)`, producing **false negatives** and severely **underestimating power** (pushing results toward "Cannot tell"). It also biases the trend fit near `10,500` and the low-`T` z-scores near `10,800`, and clips/renormalizes simulated dates whose calibrated tails extend past `9,000 cal BP`.

2. **Exponential null fitted by OLS to `ln S(t)` over 10,500–15,500 cal BP** — **must fix**
   - The plan claims in *Known weaknesses* that the step `D(T)` is "insensitive to the long trend." **This is mathematically false.** For an exponential `S(t) ∝ exp(−rt)`, the expected step in the null is `E[D_null(T*)] ≈ +300r` (plus calibration-curve bias).
   - In North America, pre-Clovis dates (`13,500–15,500 cal BP`) are extremely sparse, followed by rapid Clovis-era expansion. Fitting OLS to `ln S(t)` over `10,500–15,500` gives equal log-scale weight to noisy near-zero bins in the `14,000–15,500` tail (and crashes with `ln(0) = -inf` if `S(t)` hits zero). That pulls the fitted growth slope `r` steeply upward, shifting `E[D_null(T*)]` strongly positive.
   - **Effect:** **False positive** if real population simply transitioned from fast Clovis expansion to a flat plateau with a tiny negative fluctuation (e.g., `D(T*) = -0.02` can yield `p <= 0.01` against a null centered at `+0.30`). Conversely, **false negative** if a real sustained crash depressed `S(t)` after `12,850`, because post-crash dates are inside the `10,500–15,500` fitting window and drag `r` downward. Finally, any mismatch between the exponential curve and the real local density around `12,850` corrupts the null variance of `D(T*)`.

3. **Three defects in the power simulation** — **must fix**
   - **Rule mismatch:** The actual decision rule requires **both** `D(T*) < 0` **and** `p <= 0.01`, whereas power only checks whether `D_crash(T*)` falls at or below the 1st percentile of the null. If `E[D_null(T*)]` is strongly positive, the 1st percentile can sit near or above 0, causing power to count positive steps that would never trigger "Drop detected."
   - **Threshold mismatch & Monte Carlo noise:** `p = (count + 1)/1001 <= 0.01` requires `count <= 9` (strictly below the 10th smallest null value, `x[9]` in 0-indexing), whereas standard linear-interpolated `percentile(..., 1)` lies between `x[9]` and `x[10]`, slightly overstating power. More importantly, estimating a 1% tail threshold from only 1,000 null draws and power from only 300 crash draws (`SE ≈ 0.023` near `0.80`) introduces enough Monte Carlo jitter to flip verdicts across the hard `0.80` cutoff.
   - **Rebound-notch artefact:** Multiplying density by `0.5` only over `[12,550, 12,850)` makes population snap instantly back to 100% at `12,545 cal BP` (at high exponential density). Radiocarbon errors smear those post-12,550 dates backward into `[12,550, 12,850)`, **underestimating power** for a sustained Younger Dryas–length (~1,150-year) decline.

4. **Fixed `floor(Age/200)` binning creates calibration-curve and cut-point artefacts absent from the null** — **should fix**
   - `10,800 14C BP` is an exact bin boundary (`floor(10800/200) = 54`) sitting right on the Younger Dryas onset (~12,750–12,850 cal BP). A single site occupation straddling `10,800 14C BP` gets split into two bins (double weight), whereas an identical site centered at `10,900` gets one bin.
   - Because 200 *radiocarbon* years spans ~400 calendar years on a plateau but ~100 calendar years on a steep stretch of IntCal20, binning in `14C` space collapses more site-years into fewer bins on plateaus and inflates bin counts on steep slopes. Because the null simulations do not simulate multi-date sites or apply `floor(Age/200)` binning, this calibration-curve × binning interaction is missing from the null (**false positive or false negative**).
   - Drawing `E` from all *dates* rather than *bins* over-represents small AMS errors from heavily dated sites, while simulating single unbinned dates fails to replicate the smoothing produced by averaging multiple dates within real bins.

5. **Uncorrected marine/freshwater reservoir offsets and unscreened materials in `p3k14c`** — **should fix**
   - `p3k14c` includes marine shell, marine mammal, and bulk sediment dates. Calibrating marine samples with atmospheric IntCal20 shifts them ~400–800+ years too old, moving coastal YD/Early Holocene dates backward across `12,850 cal BP` (**false positive** if it inflates pre-YD counts; **false negative** if it fills a post-12,850 trough).
   - Dates lacking both `SiteID` and `SiteName` (or using placeholder names) bypass binning; if a regional compilation lacks site metadata, a handful of sites can create an artificial spike. Similarly, `Error > 0` admits data-entry typos (e.g., `Error = 1` creating razor spikes) and very imprecise dates (`Error = 500+` smearing across the boundary).

6. **Archaeological selection bias and continental over-aggregation** — **should fix**
   - Clovis (`~13,050–12,750 cal BP`) is disproportionately targeted by archaeologists. Site binning prevents one site from dominating, but cannot remove preferential excavation and dating of *many* Clovis sites compared to post-Clovis sites (**false positive**).
   - Pooling entire continents risks severe aggregation bias: `North America` mixes the Clovis/YDB heartland (eastern/central NA) with Alaska/Beringia, western NA, Mexico, and Central America/Caribbean (**false negative** if a regional crash is diluted). `Asia` pools the heavily dated Levant (Natufian/PPNA) with Siberia, East Asia, and Southern Hemisphere Indonesia (which should not be calibrated with IntCal20 at all!).

7. **Strict single-point target `T* = 12,850` vs chronological uncertainty** — **should fix**
   - Rasmussen et al. (2014)'s 12,846 cal BP carries a ±138-year maximum counting error, GICC05–IntCal20 synchronization is uncertain by ~50–100 years, and recent dating of the Younger Dryas boundary and end of Clovis leans slightly younger (`~12,835–12,735 cal BP`). A real crash centered near `12,750–12,800` could straddle `T* = 12,850`, attenuating `D(12,850)` (**false negative**).

8. **Independent per-date `σ(t)` in forward simulation** — **minor**
   - Adding independent `N(0, σ(t)²)` noise to each simulated date treats calibration-curve uncertainty as i.i.d. sample noise rather than a shared curve uncertainty across dates at time `t`. This slightly over-smooths simulated precise AMS dates and fails to model correlated slope uncertainty in IntCal20 near `12,850`.

---

### 2. Critique of the decision rules

1. **"Drop detected" lacks a minimum effect size and an overdispersion/specificity check** — **must fix**
   - Requiring only `D(T*) < 0` and `p <= 0.01` allows a scientifically trivial drop (e.g., `-0.01`, a 1% dip) to trigger **"Drop detected -> Supported"** whenever `E[D_null(T*)]` is positive (see #1.2).
   - Moreover, real archaeological SPDs are heavily overdispersed relative to a smooth parametric null (due to real regional fluctuations, research clusters, and taphonomy); it is common for 10%–30% of all timestamps `T` to show `p <= 0.01`. Passing `p <= 0.01` at `12,850` without checking whether `12,850` stands out against the curve's own background volatility makes "Supported" far too easy to pass.

2. **"Not supported" overstates a null result tied to one large crash size at one exact date** — **should fix**
   - Failing to detect a drop where power is `>= 0.8` for a 50% crash at exactly `12,850` is labeled **"Not supported."** A real 30%–40% crash, a regional crash in eastern/central NA, or a 50% crash offset by 75–100 years (within ice-core/IntCal20 uncertainty) could easily yield "Not supported." Although *What would count* adds appropriate caveats, the headline verdict label is broader than what the rule actually tests.

3. **Uncorrected two-region "OR" rule for "Supported as widespread"** — **minor**
   - Testing both Europe and Asia at `p <= 0.01` and declaring "widespread" if *either* passes roughly doubles the conditional false-positive rate (to ~0.02, higher under overdispersion). A simple Bonferroni adjustment (`p <= 0.005` for secondary regions) fixes this.

4. **Verdict labels conflate "population drop at 12,850" with "support for the impact hypothesis"** — **minor**
   - Conventional Younger Dryas abrupt cooling (AMOC shutdown, no cosmic impact) starts at the exact same timestamp (`12,846 cal BP`) and also predicts possible human declines in North America and Europe. Calling a drop "Supported [for the hypothesis's prediction]" invites misreading even with the disclaimer in *What would count*.

---

### 3. Ambiguities for an independent programmer

1. **Data filtering and cleaning on `p3k14c_scrubbed_fuzzed.csv`** — **must fix**
   - Exact string matching for `Continent` (e.g., exact values, case, whitespace), handling of `NA`/blank/non-numeric `Age` or `Error`, and whether duplicate `LabID`s are kept or removed are unstated.
   - Filter-vs-bin order is implicit, not explicit: `Age = 13,800` is inclusive and falls in `floor(Age/200) = 69`, which would merge with dates at `13,801–13,999` if binning occurred before filtering.

2. **Site identifier rules (`SiteID` vs `SiteName`)** — **must fix**
   - "If present" is undefined for CSV edge cases (`""`, `"NA"`, whitespace-only, or generic placeholders like `"unknown"` / `"unnamed"` that would falsely merge unrelated sites).
   - Unclear whether `SiteID` should also be stripped/lowercased, and whether `SiteID` and `SiteName` are kept in separate namespaces so a numeric `SiteName` cannot collide with a `SiteID`.

3. **Source of the laboratory error pool `E` in the simulation** — **must fix**
   - "Drawn with replacement from the region's real errors" could reasonably be coded three different ways: (a) all filtered dates (`9,000–13,800`) in that region, (b) all unfiltered dates in that region in `p3k14c`, or (c) one representative error per bin.

4. **Grid endpoint inclusivity and zero-density / underflow handling** — **must fix**
   - Endpoints are specified for `[T − 300, T)` and `[12,550, 12,850)`, and can be inferred as inclusive for `10,800 to 15,200` ("89 times"), but are ambiguous for `10,500 to 15,500` (1,001 vs 1,000 points) and `9,500 to 16,500` (1,401 vs 1,400 points).
   - No fallback is defined if `S(t) == 0` in `[10,500, 15,500]` (`ln(0) = -inf`), if a window mean in `D(T)` is `0` at sparse older times (e.g., `T = 15,200` in NA), or if a simulated date's unnormalized Gaussian weights underflow to `0` across `[9,000, 17,000]` (log-sum-exp vs dropping the date).

5. **Quantile definition for "1st percentile" and SD degrees of freedom** — **should fix**
   - "1st percentile" differs across quantile methods (`np.percentile` linear interpolation vs lower/higher order statistics vs exact `count <= 9`). Also specify `ddof=1` vs `ddof=0` for `sd` in `z(T)` (small effect, easy to lock).

6. **Exact scope of sensitivity analyses (#3–#6 in *Reported alongside*)** — **should fix**
   - Unclear whether "The same" means re-running the full pipeline (refitting the trend, updating the `E` pool for `Error <= 200`, recomputing p-values, power, and verdicts) or only recomputing z-scores and top-5 lists.
   - For 500-year windows (#4), keeping `T = 10,800` pushes `[T − 500, T)` down to `10,300` (inside the `9,000 14C BP` edge), and it is unstated whether the crash duration in power stays 300 years or changes to 200/500 years. For #6 (30% crash), the number of simulated records (300?) is unstated.

7. **IntCal20 sorting, RNG draw structure, and replication tolerances** — **minor**
   - Explicitly require sorting IntCal20 ascending by calendar age before interpolation (prevents silent bugs in `np.interp` if rows are descending).
   - Clarify whether `N(0, σ(t)²) + N(0, E²)` is drawn as two normals or one `N(0, σ(t)² + E²)` (identical distribution, different RNG stream).
   - Define a numerical tolerance for "agree closely" on the deterministic replication (e.g., max absolute difference `< 1e-6` in `S(t)` and `D(T)`).

---

### 4. Missing checks (in order of importance, feasible with `p3k14c` + `IntCal20`)

1. **Alternative null models (flat/uniform null + logistic or smooth-spline null)** — **must fix**
   - Running the same step test against a flat null (tests whether activity dropped more than the calibration curve alone predicts, without demanding ongoing exponential growth) and a logistic or wide-bandwidth smooth null (appropriate for North American colonization) immediately distinguishes a real crash from a growth slowdown.

2. **Data-hygiene and reservoir-effect sensitivity checks** — **must fix**
   - Using `p3k14c`'s `Material`, `Taxon`, `LabID`, `SiteID`, `SiteName`, and `Error`: (a) exclude marine/estuarine/freshwater shell, marine fauna, and bulk sediment/humate dates; (b) deduplicate `LabID`s if any exist; (c) report the fraction of dates missing `SiteID`/`SiteName` and test excluding them; (d) exclude suspiciously small errors (e.g., `Error < 15`).

3. **Sub-regional decomposition and geographic jackknife** — **should fix**
   - Using `Country`, `Province`, and fuzzed `Lat`/`Long`: (a) exclude Southern Hemisphere dates (`Lat < 0`, e.g., Indonesia in `Asia`) from IntCal20; (b) split North America into Eastern/Central NA (Clovis/YDB heartland), Western NA, Arctic/Subarctic, and Mesoamerica/Caribbean; (c) split Asia into Southwest Asia (Levant) vs East/North/South Asia; (d) run a leave-one-state/country-out check to verify that one heavily dated jurisdiction does not drive the continental curve.

4. **Null-model diagnostics and empirical overdispersion check** — **should fix**
   - Explicitly report `E[D_null(T*)]`, `SD[D_null(T*)]`, the real vs average simulated bin counts inside `[12,550, 13,150)`, the empirical SD of `z(T)` across all 89 timestamps, and the fraction of the 89 timestamps with `p <= 0.01`. This reveals both calibration-curve/trend bias and whether `T*` is genuinely anomalous relative to background SPD volatility.

5. **Binning sensitivity checks** — **should fix**
   - Compare `floor(Age/200)` against: (a) shifted bin edges `floor((Age + 100)/200)` (directly checks whether the `10,800 14C BP` cut-point is creating an artefact); (b) agglomerative within-site clustering (e.g., `rcarbon::binPrep`-style `h = 200` with no fixed grid boundaries); and (c) unbinned dates.

6. **Sustained Younger Dryas crash power check** — **minor**
   - Compute power for a full-YD crash (`12,850–11,700 cal BP`) alongside the 300-year rebound notch, to separate detection power for a sustained YD decline from a brief 300-year dip.

---

### 5. Issues in the plan's literature summary

1. **"The database used here holds several times more [dates than ~1,500]"** — **should fix** (*Confidence: high*)
   - Buchanan, Collard & Edinborough (2008, *PNAS*) analyzed **1,506** North American Paleoindian dates. The plan's own exploratory count found only **2,562** North American dates in `8,500–14,000 14C BP`, so the filtered `9,000–13,800` window will contain roughly ~2,000–2,200 dates—about **1.3–1.5×**, not "several times more" (and with substantial overlap, since `p3k14c` draws heavily from CARD).

2. **Oversimplification of Anderson et al. (2011) and omission of post-2011 chronology/SPD literature** — **should fix** (*Confidence: high on post-2011 literature and chronologies; moderate-to-high on Anderson et al. 2011 details*)
   - Anderson et al. (2011, *Quaternary International*) relied heavily on fluted projectile point counts (PIDBA) alongside radiocarbon SPDs, and emphasized *regional* decline and settlement reorganization (particularly in eastern North America) rather than a simple continent-wide collapse.
   - Buchanan et al. (2008) pre-dated modern Monte Carlo calibration-curve null testing (popularized by Shennan et al. 2013 and Timpson et al. 2014).
   - Modern Bayesian re-dating places the YDB layer at `12,835–12,735 cal BP` (Kennett et al. 2015, *PNAS*) and the end of Clovis at `~12,750 cal BP` (Waters et al. 2020, *Science Advances*), slightly younger than `12,850 cal BP`.

3. **Presenting Rasmussen et al. (2014)'s 12,846 cal BP without its uncertainty** — **minor** (*Confidence: high on GICC05 MCE; moderate-to-high on GICC05–IntCal20 offset*)
   - The date conversion (`12,896 b2k = 12,846 cal BP`), as well as the citations to Reimer et al. (2020) and Bird et al. (2022), are accurate (*high confidence*). However, GS-1 onset in Rasmussen et al. (2014) carries a **±138-year** maximum counting error, and synchronizing GICC05 to IntCal20 introduces additional ~50–100-year uncertainty.

4. **Slightly overstated scoping dismissal of DNA evidence** — **minor** (*Confidence: high*)
   - Saying DNA histories "blur any change over thousands of years" is fair for coalescent skyline reconstructions from modern DNA, but directly radiocarbon-dated ancient DNA time series can detect abrupt population turnovers on centennial timescales.

---

### Three changes I would make first

1. **Fix the null model and the truncation mismatch:** Widen the real-data extraction window (e.g., `8,000–14,500 14C BP`) or apply the exact `9,000–13,800 14C BP` truncation to simulated dates so simulated bin counts near `12,850` match reality; replace OLS on `ln S(t)` with an MLE logistic/smooth null and add a flat-null comparison so sparse pre-Clovis dates cannot inflate the expected growth slope `r` and trigger false positives.
2. **Fix the power calculation and tighten the detection rule:** Enforce the exact detection rule (`D(T*) < 0` and exact `count <= 9` threshold) inside the power simulation, increase Monte Carlo draws (e.g., 5,000 null / 1,000 crash), and add a minimum drop size plus an empirical overdispersion check across the 89 timestamps so a tiny dip or ordinary SPD jaggedness cannot pass as a crash.
3. **Clean the dataset, replace fixed `floor(Age/200)` binning, and add sub-regional checks:** Exclude marine/freshwater shell dates and Southern Hemisphere (`Lat < 0`) records, lock down missing `SiteID`/`SiteName` and `Error`-pool rules, switch from fixed `14C` buckets (which cut right through `10,800 14C BP`) to agglomerative site clustering (or add a shifted-boundary check), and split North America and Asia into coherent sub-regions.
