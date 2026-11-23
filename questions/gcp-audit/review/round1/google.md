<!-- {"vendor": "google", "model": "gemini-4-neon", "utc": "2026-11-23T20:18:17.357856+00:00", "input_tokens": 5413, "output_tokens": 32897, "cost_usd_list_price": 0.5097} -->

Here is a critical pre-lock review of the analysis plan. Each item is tagged with a severity (**must fix**, **should fix**, or **minor**).

---

### 1. Flaws that could produce a false positive or a false negative

1. **The in-window egg check hardcodes theoretical variance (`50`) and SD (`7.0711`), causing selective upper-tail censoring and discarding healthy eggs in long windows — `must fix`**
   - Cleaning rule 2 drops an egg in a scored window of length $L$ with $n$ trials if $|\bar{x} - 100| / (7.0711/\sqrt{n}) > 5$ or $|\overline{(x - 100)^2}/50 - 1| \sqrt{n/2} > 5$.
   - This directly contradicts the premise of empirical standardising. Suppose a stable, healthy egg has a true variance of $51.25$ ($+2.5\%$, SD $7.16$ vs $7.07$ — the exact kind of device offset empirical standardising is meant to correct). In a 24-hour window ($n = 86{,}400$, $\sqrt{n/2} = 207.8$), its expected test statistic is $0.025 \times 207.8 = 5.20 > 5$, so it gets rejected. In a 34-hour window ($n = 122{,}400$), even a $+2.0\%$ variance ($51.0$) sits at $4.95$, meaning **random upward fluctuations cross 5 and get dropped while downward fluctuations are kept**. That systematically biases $Z_\text{window}$ **downward** in long windows (false negative) and causes avoidable discrepancies with GCP's published scores.
   - Similarly, a tiny constant mean bias of $0.15$ ($0.02\sigma$) gives $6.24 > 5$ in a 24-hour window and gets dropped in long windows while being kept in short windows.
   - Even for a perfectly calibrated egg ($\sigma^2 = 50$), in a 60-second window ($n = 60$), $\chi^2_{60}$ is strongly right-skewed: the upper cutoff $\chi^2_{60} > 114.8$ has $p \approx 2.8 \times 10^{-5}$ (nearly $100\times$ higher than two-sided $5\sigma$), while the lower cutoff $\chi^2_{60} < 5.2$ has $p \approx 0$, creating asymmetric upper-tail truncation.
   - Finally, filtering on the scored window's *own* mean and variance can censor a genuine signal if a real excursion occurs in a long window. An egg-health check should either test against each egg's empirical reference $s^2$ (using an exact chi-square tail, not a normal approximation) or be evaluated strictly *outside* the scored window (e.g., on surrounding/reference data).

2. **The reference pool is not cleaned for hardware failures inside `[56, 144]`, risking massive bias in `s²` — `must fix`**
   - Cleaning rule 1 only strips $|x - 100| \ge 45$, and cleaning rule 2 is only applied *"in the window being scored"*, not to the reference pool.
   - If an egg fails inside $[56, 144]$ during a pool day — e.g., stuck at $130$ ($\overline{(x-100)^2} = 900$) or stuck at $100$ (variance $0$) — it passes rule 1 and corrupts $s^2$ for that egg across the entire year. A single day stuck at $130$ out of 25 pool days inflates $s^2$ from $50$ to $84$ ($+68\%$), shrinking $z^2$ toward $0$ all year (false negative and negative control bias); a week stuck at $100$ deflates $s^2$ by $28\%$, inflating $z^2$ all year (false positive / calibration failure).
   - You need a day-level (or block-level) bad-egg filter applied to the reference pool before computing $s^2$.

3. **The 1999 reference pool will collapse (and the 86,400-trial minimum breaks sparse years) — `must fix`**
   - The plan states there is **1 event in 1999** (`By year: 1 (1999), 15, ...`).
   - Its reference pool is *"every second of every UTC day touched by a control window of that year's events, except seconds inside a blocked stretch, and, when the window being scored is itself a control, except that window's own seconds."* An egg with $< 86{,}400$ trials in the pool is dropped.
   - If that single 1999 control window falls inside one UTC day ($86{,}400$ seconds), then **when scoring the 1999 control**, the pool has at most $86{,}400 - L < 86{,}400$ seconds — so **every egg is guaranteed to be dropped**, making the 1999 control inevaluable. Even for the 1999 event, any egg missing even 1 second out of the day is dropped. (And even if the control crosses UTC midnight, blocked stretches or minor downtime still threaten it.)
   - More generally, near the $86{,}400$ cutoff (e.g., an egg added late in a year), subtracting $L$ seconds only when scoring a control can cause an egg to be included for an event and dropped for its control. The pool for each year (or rolling window around each event) needs enough non-event days that every active egg has well over $86{,}400$ trials — e.g., a fixed rolling window of $\pm 30$ or $\pm 60$ non-blocked days, or all non-blocked days of the year (or full multi-year database, closer to GCP's stated method).

4. **Off-by-one contradiction in window length (`end − begin + 1` vs GCP's `[begin, end)`) — `must fix`**
   - The plan quotes GCP's registry verbatim: *"By convention the period includes the second that begins at the begin time, up to the last second prior to the end time."* That is half-open `[begin, end)`, length `end − begin`.
   - Yet Method Rule 3 defines window length as `end − begin + 1` seconds.
   - If registry rows use `00:00:00` to `04:00:00` (or `00:00:00` next day), adding `+1` shifts every window by 1 second (a $1.7\%$ mismatch on 60-second windows) and causes windows ending at `00:00:00` to spill 1 second into the next UTC day — pulling in an extra day file, expanding blocked stretches, and adding an extra day to the control reference pool. Conversely, if `pred_formal.html` actually writes `23:59:59` (inclusive) for some rows and `00:00:00` for others, a single formula cannot fit both. You must check how `pred_formal.html` formats end times (e.g., against the 6 pilot events or GCP's documented `df`) and reconcile this before locking.

5. **Asymmetry between controls and events in the reference pool (same-day leakage) — `should fix`**
   - Because the reference pool is built exclusively from UTC days touched by *control* windows, when scoring a 6-hour control window on day $D$, the **other 18 hours of day $D$** are inside its reference pool. When scoring a 6-hour event window on day $D+7$, the other 18 hours of day $D+7$ are generally *not* in the pool.
   - If egg variance drifts day-to-day or seasonally, $s^2$ is systematically better matched to the control windows' local variance than to the event windows' local variance (strongly so in years with few events). Excluding the **entire UTC day(s)** of a control when scoring it — or using a symmetric pool built from non-blocked days outside *both* event and control days (or symmetrically including non-blocked seconds of both event and control days, always excluding the scored window's own day) — removes this asymmetry.

6. **Overlapping event windows vs non-overlapping control windows invalidate the sign-flip independence assumption — `should fix`**
   - Event windows are permitted to overlap each other (creating positive correlation among their scores and inflating the variance of $Z_\text{all}$ under the null), whereas control windows are forbidden from overlapping each other.
   - The paired sign-flip test flips each pair independently, which assumes the paired differences are independent/exchangeable. Overlapping events share the same random fluctuations, making independent sign flips **anti-conservative** (false-positive prone). At minimum, report how many of the 396 events overlap (and by how many seconds), and either cluster-flip overlapping events together or include a deduplicated sensitivity check.

7. **Controls are 92% shifted backward (`−7` days) and single-matched, losing power and exposing the paired test to secular drift — `should fix`**
   - 363 of 396 controls are at $-7$ days and only 28 at $+7$, giving a mean lag of $-6.3$ days. Any gradual network trend (egg installations, hardware ageing, or year-boundary shifts where Jan 1–7 events get late-December controls pulled into the next year's pool) affects events and controls asymmetrically.
   - Using only one control per event doubles the variance of the paired difference compared to a multi-control baseline (reducing paired $Z$ by $1/\sqrt{2}$). An event excess that genuinely passes `departure` ($Z = 3.2$) with zero control bias has an expected paired $z$ of only $2.26$ — less than a 50% chance of passing `paired p ≤ 0.01` ($z \ge 2.33$). Balancing shifts (e.g., averaging $-7$ and $+7$, or alternating $-7/+7$ when only one is used) removes temporal drift and increases paired-test power.

8. **No empirical mean centering (`x − 100` vs `x − μ_egg`) — `should fix`**
   - Standardising uses `z = (x − 100)/s` with $s^2 = \overline{(x - 100)^2}$ rather than subtracting each egg's empirical mean. If multiple eggs share a small same-signed mean bias (e.g., from hardware or XOR-mask quirks), `Z = Σ z / √N` acquires a non-zero mean $\propto \sqrt{N}$, inflating both $Z^2$ and the cross-egg statistic `Z² − (Σ z²)/N` (since $E[z_i z_j] = \mu_i \mu_j \ne 0$). Checking each egg's empirical mean in the pool and testing sensitivity to mean-centering is essential.

9. **Wilson–Hilferty accuracy claim is false for small `df` — `minor`**
   - The plan claims Wilson–Hilferty agrees with exact $\chi^2 \to Z$ to within $0.002$ for `df` of `2, 12, 600, 86,400`. That is wrong for `df = 2`: at $\chi^2 = 2$ (the mean), exact $Z = 0.3375$ vs WH $= 0.3333$ (error $0.0042$); at $\chi^2 = 10$, error is $0.008$; at $\chi^2 = 0.05$, exact $Z = -1.965$ vs WH $= -1.789$ (error $0.176$); and WH floors at $-2.667$ as $\chi^2 \to 0$.
   - Because the shortest actual window in the test is 60 seconds (`df ≥ 48`), Wilson–Hilferty is reasonably accurate in practice (~$0.002$–$0.005$ in the bulk), so this won't change conclusions, but using exact `chi2` survival/CDF in log space (`scipy.stats.chi2.logsf` / `logcdf` mapped via `scipy.special.ndtri`) is trivial, stays finite in both tails, and matches GCP's exact conversion.

---

### 2. Decision rules that are unfair, too easy/hard, or misaligned

1. **The "Overall" decision table has overlapping conditions and can label a negative/null event result as an "excess" — `must fix`**
   - Row 2 (*"The excess is not specific to the events"*: `Z_controls ≥ 2.58` and `paired p > 0.05`) and Row 3 (*"No excess found"*: `Z_events < 1.645`) are **not mutually exclusive**, and no precedence order is specified.
   - If `Z_events = 1.0` (or even `-1.0`), `Z_controls = 2.8`, and `paired p = 0.90`, **both** Row 2 and Row 3 hold. Moreover, Row 2 does not even require `Z_events ≥ 1.645`, so it can declare *"The excess is not specific to the events"* when there is no excess in the events at all. Row 2 should require an event excess (e.g., `Z_events ≥ 1.645` or `≥ 3.09`), and all four rows must be made mutually exclusive and exhaustive.

2. **Rule 1 ("Does it reproduce?") is simultaneously too strict on combined-Z offset, too loose on per-event agreement, and blind to direction and evaluability — `should fix`**
   - With $n = 396$, $|\Delta Z_\text{all}| \le 1.0$ corresponds to a mean per-event bias of only **$0.050$**, and $|\Delta Z_\text{all}| \le 2.0$ is only **$0.100$** per event. Because the plan explicitly uses a different masking and standardising pipeline than GCP, a benign $0.11$-per-event pipeline shift could produce $r = 0.98$, median $|\Delta| = 0.12$, and yet get labelled **"Does not reproduce"** (which "What would count" interprets as evidence *against* the published table following from the public data).
   - Worse, the threshold is symmetric: if our pipeline yields `Z_all = 8.7` vs published `6.66` with $r = 0.95$, it triggers **"Does not reproduce"** even though the public data show an *even stronger* excess than published.
   - Conversely, $r = 0.70$ means half the variance of the published scores ($1 - r^2 = 0.51$) is unexplained, and Pearson $r$ is invariant to arbitrary scale/slope errors (e.g., `Z_ours = 0.5 * Z_pub` can have $r = 1.0$), yet it can pass as **"Reproduces roughly"**. Include RMSE / MAE and regression slope/intercept alongside $r$, distinguish systematic downward vs upward shifts, and evaluate reproduction against **both** empirical and theoretical standardising (see Section 5).
   - Finally, Rule 1 has **no minimum evaluability requirement**: if 150 events fail evaluability due to pool/cleaning issues, Rule 1 still scores reproduction on whatever subset remains. Lock a minimum evaluability fraction (e.g., $\ge 90\%$ or $\ge 95\%$ of the 396 events).

3. **The control-SD calibration band `[0.75, 1.3]` is too loose to protect `Z_all ≥ 3.09`, yet too rigid when paired against a huge event signal — `should fix`**
   - For $n = 396$, the sampling SD of the sample SD under $\sigma = 1$ is $1/\sqrt{790} \approx 0.036$. Allowing `SD(Z_controls)` up to $1.30$ permits a **$69\%$ variance inflation** ($\sigma^2 = 1.69$) while still declaring *"controls look like chance"*. Under $\sigma = 1.30$, the `Z_all ≥ 3.09` ($p = 0.001$) threshold is actually $2.38\sigma$ ($p = 0.0087$, nearly a $9\times$ false-positive inflation). A tighter band (e.g., $[0.88, 1.12]$, roughly $\pm 3.3$ SE) actually tests whether $\sigma = 1$.
   - Conversely, if `Z_events = 6.5`, `Z_controls = 0.1`, `paired p < 0.0001`, and `SD(Z_controls) = 1.32`, the current Overall rule refuses to call *"The excess is in the event windows"* and dumps it into *"Mixed"*, even though the distribution-free paired test and empirical-SD-adjusted $Z$ ($6.5/1.32 = 4.92$) overwhelmingly show an event-specific excess. Consider whether a mild SD excursion with near-zero control mean and a strong paired $p$ (and empirically rescaled `Z_events / SD(Z_controls) ≥ 3.09`) should still be distinguishable from genuine calibration failure.

4. **Contradiction possible in "What would count" — `minor`**
   - If Rule 1 returns *"Does not reproduce"* (e.g., `r = 0.95` but `|ΔZ_all| = 2.1`) while Overall returns *"The excess is in the event windows"*, the "What would count" section classifies the same outcome under *"Against the published table following from the public data"* while the primary label affirms an event-specific excess. Clarify how Rule 1 and Overall interact when they diverge.

---

### 3. Ambiguities where an independent programmer could compute something different

1. **Window definition (`[begin, end]` vs `[begin, end)`) — `must fix`**
   - As noted in 1.4, the plan quotes `[begin, end)` from GCP, writes `end − begin + 1` in Rule 3, and says *"the given number of Unix seconds from its begin time"* under The data. Lock explicitly whether a window is $\{t_0, t_0+1, \dots, t_0+L-1\}$ and confirm how `L` is computed from `pred_formal.html` timestamps (and how overlap with blocked stretches is defined on integer second sets).

2. **Cleaning Rule 1 boundary (`>= 45` vs `> 45`) and malformed field handling — `should fix`**
   - GCP's quoted rule (*"outside the range 55 to 145"*) excludes $x < 55$ or $x > 145$ ($|x - 100| > 45$), whereas Cleaning Rule 1 (*"differs from 100 by 45 or more"*) excludes $x \le 55$ or $x \ge 145$ ($|x - 100| \ge 45$). State exact inequalities and specify how non-integer, negative, `>200`, or whitespace fields are parsed.

3. **Whether Cleaning Rule 2 applies to the reference pool, and exact constants (`7.0711` vs `√50`) — `must fix`**
   - Under Standardising, *"that egg's cleaned trials in the reference pool"* could be read by one programmer as Cleaning Rule 1 only and by another as Rules 1 and 2.
   - Lock whether `7.0711` is literally `7.0711` or `math.sqrt(50)` (both in Cleaning Rule 2 and in theoretical standardising).
   - Lock exact float vs integer comparisons for `n < L/2` (e.g., odd $L$: `n < L / 2.0` vs `n < L // 2`) and `df < 0.8 * L`.

4. **Exact definition of the reference pool (membership, year boundaries, deduplication) — `should fix`**
   - Explicitly specify that *"a control window of that year's events"* means all events *in the test* (from `windows.tsv`, before evaluability filtering — otherwise it is circular), and confirm that multiple control windows touching the same UTC day contribute each second **once** (set union).
   - Confirm that for a Jan 1–7 event whose `-7` day control lands in late December of the prior year, those December days go into the *event's* year pool, and confirm whether *other* control windows of that same year remain inside the pool when scoring a given control (currently implied by *"except that window's own seconds"*).
   - Confirm how multi-day windows handle eggs that appear in the `12,` header of one day file and are absent from another (treated as missing trials on the absent day, summing `n` over the full window).

5. **File-parsing error handling for `13,` lines — `minor`**
   - *"anything else stops the program"* is attached only to the `12,` header sentence. Specify what happens if a `13,` line has a timestamp outside the file's UTC day, or has a different column count than the `12,` header.

6. **Window-length bin boundaries — `should fix`**
   - *"under 1 hour; 1 to 6 hours; over 6 hours and under a day; a day or more"* leaves exact `3600 s`, `21,600 s` (the median length!), and `86,400 s` open to interpretation — especially if `end − begin + 1` makes nominal 6-hour windows `21,601 s` and 1-day windows `86,401 s`. Specify exact half-open or closed inequalities in seconds.

7. **Cross-egg statistic edge cases and inputs — `minor`**
   - Specify whether the cross-egg statistic uses empirically standardised `z` (and only evaluable windows / usable eggs from the main analysis).
   - Handle the edge case where a window is evaluable (`≥ 2` usable eggs, `df ≥ 0.8L`, each egg `n ≥ L/2`) yet has **0 seconds** with `N ≥ 2` (two eggs reporting on disjoint halves of the window), which currently divides by zero.

8. **Ordering of pairs in the sign-flip test, SD denominator, and replication tolerance — `minor`**
   - Lock the exact sort order of `pairs` (e.g., ascending event number) so the fixed RNG seed (`74`) produces an identical sequence of flips in replication.
   - Specify `ddof=1` (sample SD) vs `ddof=0` for `SD(Z_controls)`.
   - Tighten the replication tolerance from `0.01` to e.g. `1e-6` for deterministic per-window scores: `0.01` is loose enough to hide real bugs (`7.0711` vs `√50`, off-by-one endpoints, `>= 45` vs `> 45`).

---

### 4. Important checks that are missing (in order of importance, feasible with the public data)

1. **Reproduction metrics under BOTH empirical and theoretical standardising, plus event-level discrepancy forensics — `must fix`**
   - Compute the full Rule 1 metrics (`r`, RMSE, median $|\Delta|$, regression slope/intercept, and paired test of `Z_published − Z_ours`) for **both** empirical and theoretical standardising. (The pilot of 6 events already hit `1.013` vs `1.013` under *theoretical* standardising — see Section 5.)
   - Inspect and report the 10–20 largest per-event discrepancies `|Z_pub − Z_ours|` and check whether discrepancies correlate with year, window length, or number of eggs rejected by the egg check.

2. **Diagnostic audit of the egg check and reference pool — `must fix`**
   - Report per-egg $s^2$ distributions (min, median, max, outliers) and empirical means $\bar{x}$ in each year's pool, plus egg rejection rates by window length and by event vs control.
   - Run a sensitivity check (a) with a per-day pool cleaner and (b) without the in-window variance/mean egg check (or testing against empirical $s^2$ instead of $50$), and (c) with empirical mean-centering `(x − μ_egg)/s_egg`, to verify that neither pool corruption, in-window censoring, nor mean bias drives the headline result.

3. **Lag-1 autocorrelation check of `Z_t` and `Z_t²` in control windows — `should fix`**
   - The chi-square statistic assumes consecutive seconds are independent. Positive lag-1 autocorrelation in `Z_t` or `Z_t²` inflates the variance of `χ²` (and `SD(Z_window)`) even when every egg has exact mean $100$ and variance $50$. Computing lag-1 autocorrelation across control windows is trivial on the already-downloaded files and directly diagnoses any failure of the independence assumption.

4. **Published-score audit of the 116 excluded registry rows — `should fix`**
   - Using `registry.tsv` and `published.tsv` (already parsed), report the combined published $Z$ and mean $Z$ for each exclusion category (especially the 13 `Include = No` rows, the 16 date-mismatched/renumbered rows, and the 91 non-standard-recipe rows). Confirm nothing anomalously negative sits in the `Include = No` group and quantify how representative the 396 tested events are.

5. **Overlapping-event deduplication and outlier/influence robustness — `should fix`**
   - Report the number of overlapping event pairs and recompute `Z_all` and the paired test (a) deduplicating overlapping events (or cluster-flipping overlapping pairs), (b) using a Wilcoxon signed-rank test on paired differences, and (c) checking whether the combined score survives dropping the top 5 extreme events or any single high-leverage egg (leave-one-egg-out sensitivity).

6. **Balanced / multi-shift controls (`−7` and `+7` days) — `should fix`**
   - Adding the `+7` day control alongside `−7` (only downloading one extra set of public day files, or testing symmetry on existing shifts) removes the $-6.3$-day temporal lag, reduces paired-difference variance, and checks whether control calibration is stable across shifts.

---

### 5. Potential errors in the plan's summary of the literature

1. **Mismatch with GCP's stated trial-exclusion range — `minor` (Confidence: High)**
   - The plan quotes `results.html` (*"outside the range 55 to 145"*, i.e., `< 55` or `> 145`) and then paraphrases this as *"differs from 100 by 45 or more"* (`<= 55` or `>= 145`), misstating the boundary by 1 on both sides.

2. **Mismatch with GCP's stated window endpoint convention — `must fix` (Confidence: High)**
   - The plan quotes `pred_formal.html` (*"up to the last second prior to the end time"*, i.e., `[begin, end)`) and then adopts `end − begin + 1` (`[begin, end]`) without reconciling the contradiction.

3. **Assuming `results.html` uses empirical variance standardising (and equating a 1-year control-day pool to GCP's full-database empirical variance) — `should fix` (Confidence: Moderate-to-High)**
   - In the GCP literature (e.g., Bancel & Nelson, 2008, *JSE*; Nelson & Bancel, 2011), the official formal event table (`results.html`) was originally accumulated using **theoretical** expectations ($\mu = 100, \sigma^2 = 50$) — at least for a substantial portion of the formal series — while empirical variance normalization from each egg's full multi-year database was used primarily in later technical re-analyses (and in some later formal updates). The plan's own quote from `results.html` (*"Basic statistical evaluations are based on theoretical expectations, while more precise analyses use an empirical estimate of variance..."*) and its own pilot validation (getting an exact `1.013` vs `1.013` match on `2015-12-12` using **theoretical** standardising!) point in the same direction. Treating empirical standardising as the sole yardstick for *"Does the published table reproduce?"* risks conflating a difference in normalization choice with a failure to reproduce.
   - Additionally, equating a pool of control days from a single year (which is 1–2 days in 1999) to GCP's *"full database of trials"* is inaccurate; a full-database (or multi-month) pool behaves very differently in sparse years.

4. **Ignoring the label `"Chisquare 600 df weight"` without verification — `should fix` (Confidence: High that it is unverified; Low-to-Moderate on its exact GCP meaning)**
   - Rule 2 filters specifically to `Statistic == "Chisquare 600 df weight"` and then computes an unweighted 1-second `Σ Z²` without ever explaining what `"600 df weight"` refers to in GCP's registry (e.g., whether it is merely a display/graphing or historical table annotation, or whether it implies a weighting/blocking convention in any subset of events). This should be verified from GCP's documentation before locking.

5. **Understating the literature role of the cross-egg decomposition — `minor` (Confidence: High)**
   - The plan relegates the cross-egg statistic (`Z² − Σ z²/N`) to *"Reported alongside, not part of the labels"* as a generic check against single-egg variance. In the published GCP literature (notably Bancel's technical papers), this pair-correlation decomposition is actually GCP's central positive claim — that the formal excess comes specifically from inter-egg correlations rather than excess single-egg variance. That doesn't require changing the primary labels, just accurate framing.

---

### Top three changes to make first

1. **Fix the egg check and reference pool together:** Clean bad egg-days *inside* the reference pool before computing $s^2$; fix the 1999/sparse-year pool collapse and control day-sharing asymmetry (e.g., use a symmetric rolling window of non-blocked days outside the scored window's own UTC day(s), rather than only that year's control days); and stop hardcoding theoretical `50` and `7.0711` inside the scored-window egg check (evaluate egg health against empirical pool parameters or outside the scored window).
2. **Resolve the window endpoint contradiction (`end − begin` vs `end − begin + 1`) and clarify all boundary rules:** Verify against `pred_formal.html` (and the 6 pilot events) whether end times are inclusive or exclusive, align Cleaning Rule 1 (`> 45` vs `>= 45`), lock window-length bin boundaries in seconds, and tighten replication tolerance to `1e-6`.
3. **Fix the decision rules:** Make the four Overall labels strictly mutually exclusive (require an event excess in Row 2), tighten the control-SD calibration check while allowing strong distribution-free paired results to remain interpretable, and evaluate Rule 1 reproduction metrics (including slope/RMSE, not just $r$ and $|\Delta Z_\text{all}|$) under **both** empirical and theoretical standardising with a minimum evaluability floor.
