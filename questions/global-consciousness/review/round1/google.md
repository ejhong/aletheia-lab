<!-- {"vendor": "google", "model": "gemini-4-neon", "utc": "2026-11-23T15:24:27.600176+00:00", "input_tokens": 3680, "output_tokens": 33297, "cost_usd_list_price": 0.5105} -->

Here is a critical review of the pre-registration, organized by the five areas requested.

---

### 1. Flaws that could produce a false positive or false negative

1. **Cross-standardising from a single 24-hour control window inflates variance and induces strong negative correlation between events and controls — `must fix`**
   - The plan states that standardising from one control window *"adds a little noise to every score, in both directions, and none on average."* That misses two large variance effects.
   - Let $T$ be the number of seconds in the event window, $n_c$ in the control window, and $N$ the number of eggs. For each egg $i$, the estimated variance $s_i^2 = \sigma_i^2(1+\epsilon_i)$ has $\mathrm{Var}(\epsilon_i) \approx 2/n_c$, and that single error $\epsilon_i$ multiplies all $T$ seconds of egg $i$'s diagonal contribution to $\chi^2$.
   - Under the null, the diagonal variance doubles when $n_c \approx T$, giving:
     $$\mathrm{Var}(Z_{\text{event}}) \approx 1 + \frac{T}{N n_c} \approx 1 + \frac{1}{N}$$
     (and up to $1 + 2/N$ when $n_c = 43{,}200$ and $T = 86{,}400$).
   - Worse, because the event is standardised by the control and the control by the event, their diagonal errors are exact negatives of each other ($\delta_i - \epsilon_i$ vs. $\epsilon_i - \delta_i$). This produces a **negative correlation** $\mathrm{Cov}(Z_{\text{event}}, Z_{\text{control}}) \approx -2/N$, which blows up the variance of the calibration fallback score $Z_{\text{diff}} = (\sum Z_{\text{event}} - \sum Z_{\text{control}})/\sqrt{2n}$:
     $$\mathrm{Var}(Z_{\text{diff}}) \approx 1 + \frac{3}{N}$$
   - In the shrunken post-2015 network ($N$ often 10–20, and permitted down to 5), $\mathrm{SD}(Z_{\text{diff}})$ is $1.07$–$1.26$, inflating the nominal $p=0.001$ false-positive rate by **2× to 7×** (and inflating $|Z_{\text{control}}| \ge 2.58$ trigger rates as well).
   - **Fix:** Estimate each egg's $s_i$ from a **multi-day external baseline** (e.g., $\pm 15$ to $\pm 30$ non-event, non-control days around the event) and apply that *same* $s_i$ to both the event and its control. That reduces the variance inflation by ~30×, eliminates the negative correlation, and causes any residual estimation error in $s_i$ to cancel out in $Z_{\text{event}} - Z_{\text{control}}$.

2. **Overlapping event windows and overlapping control windows violate independence — `must fix`**
   - **Event–event overlaps:** Nothing in the rules prevents two event windows from overlapping. In 2016–2025, multiple $\ge 100$-death earthquakes occurred within hours of each other (e.g., the February 6, 2023 Turkey–Syria M7.8 and M7.5 quakes, 9 hours apart; potentially the October 7, 2023 Herat quakes), and an earthquake can overlap one of the four fixed calendar days. Overlapping events double-count the same seconds, positively correlating their $Z_{\text{event}}$ scores and inflating the variance of $Z_{\text{all}}$.
   - **Control–control overlaps:** The control rule checks whether a candidate control lies within 24 hours of any *event* window, but **never checks whether it overlaps another *control* window**. Two earthquakes on the same day will get overlapping controls 7 days earlier; two events 14 days apart where the first falls back to $+7\text{d}$ and the second uses $-7\text{d}$ will share the exact same control day. This violates the independence assumption of $Z_{\text{control}}$ and $Z_{\text{diff}}$.

3. **Persistent hardware mean biases are not removed and can accumulate in off-diagonal terms — `should fix`**
   - Standardising via `z = (x - 100)/s` absorbs a single egg's constant mean offset $\delta_i = E[x_i] - 100$ into its diagonal term (since $s_i^2 \approx \sigma_i^2 + \delta_i^2$), **but not into the off-diagonal cross-terms**:
     $$E[Z_t^2] = 1 + \frac{1}{N}\sum_{i \neq j} \frac{\delta_i \delta_j}{s_i s_j}$$
   - An egg with a persistent mean shift of $+0.05$ (a 0.025% bit bias) has $|(\bar{x}-100)/(7.071/\sqrt{86400})| \approx 2.1 < 5$, so it sails through the $5\sigma$ egg check. If $N = 20$ eggs share even a $+0.05$ bias of the same sign (e.g., from a common RNG hardware model or XOR-mask flaw), that shifts $Z_{\text{event}}$ by $+0.20$ per event, or $+1.50$ over 58 events—potentially without triggering the $|Z_{\text{control}}| \ge 2.58$ check.
   - Note that subtracting each egg's *in-window* mean would suppress genuine sustained DC shifts during an event, so that should not be done; however, subtracting each egg's **external multi-day baseline mean** (or at least checking for persistent mean biases in non-event days) protects against hardware-bias false positives without removing event-specific signals.

4. **Unchecked temporal autocorrelation and stuck/oscillating eggs — `should fix`**
   - The $\chi^2_{df}$ null assumes $Z_t$ is uncorrelated across seconds. Any lag-$k$ autocorrelation $\rho_k$ (from hardware glitches, buffer repeats, or clock/logging artifacts) inflates $\mathrm{Var}(\chi^2)$ by a factor of $1 + 2\sum_{k \ge 1}\rho_k^2$, always upward regardless of sign.
   - Similarly, the daily mean/variance egg check misses an egg frozen at 100 for up to ~2,000 seconds (~33 minutes) or stuck oscillating around 100 with variance $\approx 50$.

5. **Conditioning egg exclusion on the event window's own data — `minor`**
   - Dropping an egg if its mean or variance exceeds $5\sigma$ in the *event* window peeks at the event data to decide inclusion. Under the null this fires at $p \approx 6 \times 10^{-7}$ (negligible), and under GCP's inter-egg covariance model single eggs shouldn't exceed $5\sigma$, so the bias is tiny—unless a genuine effect causes large single-egg excursions, in which case this would create a false negative. Checking how often the rule fires in non-event days (and logging any event-window exclusions) is worthwhile.

6. **Hardcoded `7.0711` instead of `sqrt(50)` — `minor`**
   - $\sqrt{50} = 7.0710678\dots$. Using `7.0711` in the theoretical-standardising secondary analysis introduces a small downward bias of $-0.0019$ per event ($-0.014$ over 58 events). Just use exact $\sqrt{50}$.

---

### 2. Decision rules that are unfair, miscalibrated, or misaligned

1. **The calibration fallback rule has a $\sqrt{2}$ mathematical error and a severe selection-bias distortion — `must fix`**
   - **Wrong compatibility threshold:** Under the project's reported mean ($\mu = 0.33$ per event, $0$ for controls), $E[Z_{\text{diff}}] = 0.33\sqrt{n/2}$ ($1.78$ for $n=58$), **not** $0.33\sqrt{n}$ ($2.51$). Applying *"the same thresholds"* (`Z_diff <= 0.33*sqrt(n) - 1.645 = 0.87`) rejects the project's reported effect size **18% of the time** when it is true (instead of 5%), while dropping power for "Departure" from 28% down to **9.5%**.
   - **Conditional selection bias:** Pivoting to $(Z_{\text{all}} - Z_{\text{control}})/\sqrt{2}$ *only when* $|Z_{\text{control}}| \ge 2.58$ adds a large shift of $\ge +1.82$ whenever $Z_{\text{control}} \le -2.58$ by chance (making a false-positive "Suggestive" result ~65% likely and "Departure" ~4–5% likely in that branch—amplified further by the $-2/N$ negative correlation!). Conversely, a fluke $Z_{\text{control}} \ge +2.58$ shifts $Z_{\text{diff}}$ down by $-1.82$, making a real effect nearly undetectable.
   - **Wrong remedy for overdispersion:** If $|Z_{\text{control}}| \ge 2.58$ occurs because $\mathrm{SD}(Z) > 1$ (e.g., autocorrelation or hardware correlation) rather than a constant additive bias, differencing against controls does **not** restore unit variance. If controls fail calibration, the verdict should be **"calibration failed — primary result invalidated pending root-cause diagnosis,"** rather than an automatic pivot to a mis-thresholded `Z_diff`.

2. **Testing compatibility against a fixed mean of `0.33` ignores how expected $Z$ scales with active egg count $N$ — `should fix`**
   - In GCP's own inter-egg correlation model (constant pairwise correlation $\rho$ between eggs), $\mathrm{Var}(Z_t) = 1 + (N-1)\rho$, so $E[Z_{\text{event}}] \propto (N-1)\sqrt{T}$.
   - During 1998–2015, the network typically had 40–65 active eggs; after 2015, egg counts declined substantially. If $N$ in 2016–2025 is half its 1998–2015 average, the *same* underlying pairwise correlation $\rho$ would produce $E[Z_{\text{event}}] \approx 0.16$, not $0.33$.
   - Declaring the result "smaller than reported" against an unadjusted $0.33$ therefore tests *"same $Z$ per event regardless of network size,"* not *"same underlying inter-egg correlation."* The plan should explicitly state which claim it is testing, and ideally compute an $N$-adjusted benchmark alongside `0.33`.

3. **Low power (28%) for "Departure" at the reported effect size, and sensitivity to `df` dropouts — `should fix`**
   - With $n=58$ and threshold $Z \ge 3.09$, even if the GCP anomaly existed at its full reported strength ($\mu = 0.33$), the test fails to reach "Departure" **72% of the time**. If 10–15 events drop out for `df < 43,200` (a real risk given post-2015 gaps), power for "Departure" drops below 20% and the "uninformative" middle zone widens.
   - Using $p \le 0.001$ is reasonable for an extraordinary claim, but the plan should acknowledge up front how sensitive power is to `df` dropouts—and consider whether additional mechanical event classes (or checking `df` attrition on non-event days first) are needed before locking.

4. **No negative-tail anomaly flag — `minor`**
   - A score of $Z_{\text{all}} = -3.5$ is currently classified identically to $Z_{\text{all}} = 0.0$ ("No departure" + "Smaller than reported"), even though a $-3.5\sigma$ result strongly indicates a pipeline bug, variance miscalibration, or an opposite-direction anomaly. Add a pre-specified diagnostic flag for $Z_{\text{all}} \le -2.58$.

5. **Minor rounding in `0.33` — `minor`**
   - $7.310/\sqrt{500} = 0.3269$, not $0.33$ (a 0.023 difference in the threshold at $n=58$). Using `7.310 / sqrt(500)` avoids arbitrary rounding.

---

### 3. Ambiguities that could cause an independent programmer to compute something different

1. **Asymmetric `df < 43,200` handling between an event and its control — `must fix`**
   - The plan says: *"If `df < 43,200` the event is not evaluable and is left out, with its control, and named. The same is computed for every control window."*
   - It does **not** specify what happens if the *event* has `df >= 43,200` while its *control* has `df < 43,200` (possible even when every egg has `n >= 43,200`, if reporting periods are staggered). One programmer will drop the pair; another will keep the event and drop only the control, changing $n$ and breaking pairing. State explicitly: an event–control pair is evaluable only if **both** windows have `df >= 43,200` (and $\ge 5$ eggs pass).

2. **CSV parsing details, column indexing, multi-day alignment, and multiple `12,` lines — `must fix`**
   - *"field two is the Unix time, fields four onward the trial sums"* does not explicitly state 1-based vs. 0-based indexing (clearly meant as 1-based: `col[1]` and `col[3:]`). Give 0-based indices and a literal example of a `12,` and `13,` line.
   - *"Lines beginning `12,`"* (plural): if a day file contains multiple `12,` header lines (e.g., mid-day roster change), specify that each `13,` line maps to the most recent preceding `12,` line.
   - Across a 2-day earthquake window, specify explicitly that eggs are matched across day files by **integer egg ID** (not column index), and that an egg absent from one day's `12,` line simply has missing values on that day.
   - Specify handling of: duplicate Unix timestamps (including midnight boundary rows or the 2016-12-31 leap second—keep first, keep last, or drop?), ragged rows (fewer fields than `12,`), whitespace, and non-integer values.

3. **"Lies within 24 hours of any event window in the list" — `should fix`**
   - Two reasonable readings exist:
     - **No overlap:** `[ctrl_start, ctrl_end)` does not intersect `[ev_start, ev_end)` (i.e., `|ctrl_start - ev_start| >= 86400`).
     - **24-hour buffer:** at least 24 hours of separation between endpoints (i.e., `|ctrl_start - ev_start| >= 172800`).
   - Also clarify whether "any event window in the list" means all 65 candidate events or only the 58 in-test events, and whether "has no data file" means missing *any* UTC day file touched by the 24-hour control window. (While the replicator receives `events.tsv`, anyone auditing or reproducing `build_events.py` from the plan needs this exact rule.)

4. **NOAA API query details & overlapping earthquakes — `should fix`**
   - The NOAA Hazard Service API is a live database whose death estimates can change, and it distinguishes direct earthquake deaths (`deaths`) from total deaths including tsunami/landslide (`deathsTotal`—relevant to events like 2018 Sulawesi). Confirm which field `minDeaths=100` filters on, archive the exact JSON response in `sources/`, and specify what happens if an entry lacks an hour/minute or if two earthquakes fall within 24 hours of each other.

5. **Exact formulas for standardising, egg check, and secondary analyses — `minor`**
   - Write `s = sqrt( (1/n_c) * sum((x - 100)^2) )` explicitly so no programmer uses `ddof=1` or subtracts the sample mean.
   - Write `56 <= x <= 144` (or `abs(x - 100) < 45`) explicitly to avoid `>` vs `>=` confusion.
   - In "Reported alongside #4" (theoretical standardising), explicitly state whether the **same** set of eggs that passed Cleaning Rule #2 is used, or all eggs.

---

### 4. Important checks that are missing (in order of importance)

All of the following are feasible using only the public files already named in the plan:

1. **Pre-lock empirical null calibration on hundreds of non-event, non-control days — `must fix`**
   - Currently, the only real-data pre-lock check (`--controls`) runs theoretical standardising on the 58 control windows themselves. That tests the wrong standardising method and risks tuning cleaning choices on the actual calibration controls.
   - With 3,058 day files available, excluding all event and control windows still leaves $>2{,}500$ untouched days. Run the **full, exact pipeline** on 200+ non-overlapping fake-event/fake-control pairs drawn across 2016–2025 before locking. Verify:
     - 2016–2025 CSV format matches the 2001 file (no silent schema changes);
     - empirical distribution of $Z$ is genuinely $\mathcal{N}(0,1)$ (mean $\approx 0$, **SD $\approx 1$**, no heavy tails);
     - actual egg counts $N$, egg-check dropout rates, and `df < 43,200` attrition by year.

2. **Pre-lock validation on a small sample of 1998–2015 formal registry events — `should fix`**
   - The same `global-mind.org/data/eggsummary/` archive holds 1998–2015 day files, and the plan has already inspected the 1998–2015 registry. Running the pipeline on 5–10 standard-recipe 24-hour formal events from 1998–2015 and comparing your $Z_{\text{event}}$ values against GCP's published table verifies that you have faithfully reproduced GCP's actual recipe (timestamps, egg IDs, sign, scaling) with zero risk of peeking at 2016–2025.

3. **Decompose $\chi^2$ into single-egg variance (diagonal) vs. inter-egg covariance (off-diagonal) — `should fix`**
   - $\chi^2 = \sum_t \frac{1}{N_t}\sum_i z_{i,t}^2 + \sum_t \frac{1}{N_t}\sum_{i \neq j} z_{i,t} z_{j,t}$.
   - Reporting both components (as GCP's own technical papers do) immediately distinguishes a single-egg variance/calibration artifact (diagonal) from cross-egg coherence (off-diagonal). This requires only a few lines of code.

4. **Check temporal autocorrelation of $Z_t$ and persistent per-egg mean biases on non-event days — `should fix`**
   - Compute lag-1 to lag-60 autocorrelations of $Z_t$ and $Z_t^2$, and check whether individual eggs show persistent multi-day mean offsets or long runs of identical values that evade the $5\sigma$ daily check.

5. **Audit `events.tsv` for overlaps and network-size ($N$) trends before locking — `should fix`**
   - Check `events.tsv` right now (without reading network data) for event–event and control–control overlaps. Once unblinded (or on non-event days pre-lock), report active egg count $N$ by year compared to 1998–2015 so the $N$-scaling caveat is quantified rather than guessed.

6. **Post-unblinding robustness diagnostics (outlier event / single-egg influence) — `minor`**
   - Report the sample SD and quantiles of the 58 $Z_{\text{event}}$ scores (to check whether the result is spread across events or driven by 1–2 outliers), and if $Z_{\text{all}} \ge 1.645$ or $\le -2.58$, check leave-one-egg-out sensitivity to ensure no single marginal device drove the result.

---

### 5. Errors or important omissions in the summary of the literature

1. **How GCP actually standardises trials — `should fix` (High confidence)**
   - The plan adopts single-control-day cross-standardising as *"the project's own standard recipe."* In reality, GCP empirically standardises each egg using **long-term historical variance estimates** (accumulated over large stretches of data, millions of trials per egg), not a single paired 24-hour control window. This is why GCP's actual recipe does not suffer the $1 + 1/N$ variance inflation or negative event–control correlation introduced by this plan.

2. **Framing the dispute solely around "freedom of choice" misses the central internal debate in the GCP literature — `should fix` (High confidence)**
   - The plan writes: *"The dispute over the project's result is about freedom of choice: which events, which time window, which statistic."*
   - While external critiques (e.g., May & Spottiswoode) did challenge window timing and post-onset event selection (notably on 9/11), the 500 formal events were pre-registered before data inspection. A major published debate—led by GCP's own lead analyst Peter Bancel (e.g., Bancel 2017, *Journal of Scientific Exploration*)—contrasts a **"global consciousness field" model** (Roger Nelson's view) against a **"selection / goal-oriented" (Decision Augmentation) model**, where the anomaly depends on experimenter choice rather than an objective physical field.
   - This matters directly for interpreting your test: a null on mechanically chosen events refutes a persistent, field-like effect of the reported size, **not** necessarily a selection-based account (nor do mechanical rules resolve whether experimenter judgment in 1998–2015 was picking genuinely larger events or introducing bias).

3. **Omission of GCP's key structural finding: inter-egg covariance and $N$-scaling — `should fix` (High confidence)**
   - Published analyses by Bancel & Nelson (2008) and Bancel (2011) report that the formal GCP signal resides almost entirely in **inter-egg pairwise covariance** (off-diagonal terms) rather than single-egg variance. As noted in Section 2, this directly bears on comparing post-2015 data (with fewer eggs) to 1998–2015 data.

4. **All 500 events vs. standard-recipe events, and Wilson–Hilferty vs. exact $\chi^2$ — `minor` (High confidence on the 421/500 split; medium-high confidence on exact $\chi^2$)**
   - The 7.310 Stouffer $Z$ (mean 0.327) combines all 500 formal events, including ~79 non-standard-recipe events (such as New Year's Eve, which used different variance/excursion statistics), whereas the plan tests only the standard Stouffer-$Z^2$ recipe (421 of 500 events).
   - GCP converts $\chi^2$ to $Z$ using the exact $\chi^2$ CDF rather than the Wilson–Hilferty approximation, though for `df >= 43,200` the two agree to more than 5 decimal places, so this has no practical impact.

---

### The three changes I would make first

1. **Replace 1-day cross-standardising with a multi-day external baseline** (e.g., $\pm 15$ to $\pm 30$ non-event, non-control days) applied identically to both the event and its control. This simultaneously eliminates the $1+1/N$ variance inflation in $Z_{\text{all}}$, eliminates the $-2/N$ negative event–control correlation, makes $s_i$ estimation error cancel in $Z_{\text{event}} - Z_{\text{control}}$, and brings the statistic in line with GCP's actual long-term standardisation.
2. **Fix the calibration fallback and run a large pre-lock empirical null check on untouched 2016–2025 days.** Remove the automatic, selection-biased pivot to a mis-thresholded `Z_diff` when $|Z_{\text{control}}| \ge 2.58$ (treat calibration failure as a diagnostic stop, and if `Z_diff` is ever evaluated for effect size, fix its threshold to $0.33\sqrt{n/2} - 1.645$). Before locking, run the exact pipeline on 200+ non-event, non-control day pairs from 2016–2025 to verify $\mathcal{N}(0,1)$ calibration, CSV schema stability, autocorrelation, and `df` attrition.
3. **Eliminate window overlaps and close all implementation ambiguities before freezing `events.tsv`.** Add explicit rules preventing both event–event overlaps (e.g., same-day earthquakes) and control–control overlaps, clarify the 24-hour separation rule, require **both** event and control to pass `df >= 43,200`, and write out exact 0-based CSV parsing rules (multiple `12,` headers, egg-ID alignment across days, duplicate timestamps) verified against a few 1998–2015 formal events.
