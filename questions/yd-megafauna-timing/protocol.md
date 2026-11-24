# Protocol — Did North American Megafauna Collapse Before the Younger Dryas? (`yd-megafauna-timing`, Issue #116)

**Lane:** `data`  
**Budget:** `$0.00` (open public Neotoma v2 API, Broughton & Weitzel 2018 CC-BY-4.0 supplementary table, and IntCal20 on local CPU).  
**Pre-registration status:** Locked *before* inspecting any *Sporormiella* percentage curves, decline dates, calibrated megafauna radiocarbon ages, or extinction-interval estimates. Only file schemas, variable names, sample counts, and chronology types were checked beforehand.

---

## 1. Exact Question

A central pillar of the Younger Dryas Impact Hypothesis (Firestone et al. 2007, *PNAS*) is that a cosmic impact or airburst event at **`~12,850 cal BP`** (immediately adjacent to the Greenland `GICC05` Younger Dryas cold onset at **`T_YD = 12,896 cal BP`**, Rasmussen et al. 2014; Kennett et al. 2015 YDB estimate **`12,835 cal BP`**) caused or abruptly triggered the terminal Pleistocene extinction of North American megafauna.

We test that timing claim across **two independent, continent-wide public archives**:

1. **Pillar 1 — Landscape Herbivore Biomass (*Sporormiella* dung-fungus spores in 11 North American lake/cave cores from Neotoma):** Did North American megaherbivore abundance collapse *before* the Younger Dryas (during the Bølling–Allerød warming, `> 13,200 cal BP`, outside the `12.9 ka` radiocarbon plateau), abruptly *at* the Younger Dryas onset (`12,896 ± 300 cal BP`), or *after* it?
2. **Pillar 2 — Direct Megafauna Radiocarbon Dates (`n = 521` directly dated extinct North American megafauna from Broughton & Weitzel 2018, recalibrated on `IntCal20`):** Accounting explicitly for both the **`12.9 ka` `IntCal20` radiocarbon plateau** (via forward Monte Carlo calibration-curve simulation) and the **Signor–Lipps sampling lag** (via Optimal Linear Estimation `OLE` and `GRIWM`), does the direct fossil record match an abrupt single-event wipeout at `12,850 cal BP`, a pre-Younger Dryas decline, or a staggered extinction with reliable survivors well inside the Younger Dryas (`< 12,750 cal BP`)?

---

## 2. Pillar 1 Specification: Lake-Sediment *Sporormiella* Spores

### 2.1 Inclusion Criteria & Metric
- Include all North American (`24–72°N`, `−168 to −52°E`) Neotoma pollen datasets with `Sporormiella` (`units = NISP`, `elementtype = spore`), calibrated chronology (`Calibrated radiocarbon years BP`, using `defaultchronology` when present), `≥ 10` samples in `17,000–10,000 cal BP`, and `≥ 4` nonzero *Sporormiella* samples in `17,000–10,000 cal BP` (`11` qualifying cores listed in `MANIFEST.md`).
- For every sample $k$ with calibrated age $t_k$, compute the standard Gill et al. (2009) / Robinson et al. (2005) upland percentage:
  $$S(t_k) = 100 \times \frac{N_{\text{Sporormiella}}(t_k)}{N_{\text{upland}}(t_k)}, \quad N_{\text{upland}} = \sum_{d \in \{\text{TRSH},\,\text{UPHE}\},\,\text{NISP}} \text{value}_d.$$
  Samples where `Sporormiella` is absent from `datum` (while upland pollen is counted) have $N_{\text{Sporormiella}} = 0$.

### 2.2 Three Pre-Registered Decline-Age Estimators (computed on `17,000–10,000 cal BP`)
For each qualifying core (sorted oldest to youngest, deduplicating identical ages by averaging):
1. **`t_2pct` (Classic functional-extinction crossing, Robinson 2005 / Gill 2009):** Defined on every core whose maximum $S(t)$ inside `17,000–11,500 cal BP` reaches `≥ 2.0%`. Identify the **last sample** $k^*$ with $S(t_{k^*}) \ge 2.0\%$ that is followed by younger samples remaining `< 2.0%` through `10,500 cal BP` (or the end of the `17–10 ka` window); linearly interpolate `t_2pct` between $t_{k^*}$ and $t_{k^*+1}$. (We also report the **onset of sustained decline** `t_onset`, defined as the age of the pre-collapse peak immediately preceding `t_2pct`.)
2. **`t_50pct` (Threshold-free half-drop age):** Defined on **all 11 cores**. Let $S_{\max}$ be the peak of a 3-point median-smoothed (or raw if `< 15` samples) curve inside `17,000–12,500 cal BP` at age $t_{\text{peak}}$; find the first younger crossing below $0.5 \cdot S_{\max}$ (linearly interpolated).
3. **`t_cp` (Exact 2-regime step-drop changepoint MLE):** Across all candidate split points $t_c \in [16,000, 11,000]\text{ cal BP}$ (midpoints between consecutive samples with `≥ 2` samples on each side), find the split minimizing total sum of squared residuals $\text{SSR}(t_c)$ subject to $\bar{S}_{\text{older}} > \bar{S}_{\text{younger}}$. Report the variance explained $R^2_{\text{step}} = 1 - \text{SSR}(t_{\text{cp}}) / \text{SST}$.

### 2.3 Continental Composite & Hypothesis Tests
- **Normalized multi-core composite:** Divide each core's $S(t)$ by its own `17,000–10,000 cal BP` mean, interpolate onto a `200`-year grid (`16,400` to `10,400 cal BP`), and compute the cross-site median and mean with `5,000` site-bootstrap 95% CIs.
- **Formal timing test against `T_YD = 12,896 cal BP` (and `12,835 cal BP`):** Two-sided Wilcoxon signed-rank test and exact binomial sign test of `t_decline − T_YD` across sites for `t_2pct`, `t_50pct`, and `t_cp` (`+` = collapsed *before* YD onset; `−` = collapsed *after* YD onset).

---

## 3. Pillar 2 Specification: Direct Megafauna `¹⁴C` Dates on `IntCal20`

### 3.1 Calibration & Subsets
- Parse all direct radiocarbon dates from `broughton2018_s1.xlsx` (`RCYBP` and `Error` numeric, `6,000 ≤ RCYBP ≤ 35,000`; every entry in Broughton & Weitzel's vetted table already passes Barnosky & Lindsey `Score ≥ 11`, split cleanly into `Score 11` conventional `ST` and `Score 12` AMS `MS`/`AMS`).
- Calibrate every date from scratch against `IntCal20` (`intcal20.14c`, linearly interpolated to `5`-year calendar bins `t ∈ [9,000, 20,000]` cal BP for SPD analysis, and `t ∈ [9,000, 25,000]` cal BP for per-taxon OLE/GRIWM):
  $$p_i(t) \propto \exp\!\left(-\frac{(r_i - \mu_{\text{IC20}}(t))^2}{2(\sigma_i^2 + \sigma_{\text{IC20}}(t)^2)}\right), \quad \sum_t p_i(t) = 1.$$
  Dates whose calibrated posterior places `< 50%` probability mass inside `[9,000, 20,000]` cal BP are excluded from the `20–9 ka` continental SPD (and similarly `< 50%` inside `[9,000, 25,000]` for per-taxon analysis).
- Evaluate all statistics on **five pre-registered subsets**:
  1. **`all`** (all vetted `Score ≥ 11` direct dates in `20–9 ka`)
  2. **`score12_ams`** (gold-standard `Score == 12` AMS direct dates, `Method ∈ {'MS', 'AMS'}`)
  3. **`herbivores_all`** (`Score ≥ 11` excluding carnivores `Smilodon`, `Canis dirus`, `Arctodus`, `Panthera leo atrox`, `Homotherium`)
  4. **`herbivores_s12`** (`Score == 12` AMS herbivores only)
  5. **`no_labrea_all`** (`Score ≥ 11` excluding Rancho La Brea tar-pit sites, matched case-insensitively on `"brea"`, plus `no_labrea_s12` for AMS-only non-La-Brea)

### 3.2 Forward-Simulated `IntCal20` Impact-Step Benchmark (`2,000` Monte Carlo Catalogs)
To separate genuine population changes from `IntCal20` calibration-curve wiggles and the `12.9 ka` radiocarbon plateau:
1. Build observed continental `SPD(t)` (both raw and **Surovell et al. 2009** taphonomy-corrected: divide by $f_{\text{taph}}(t) = 5.726442 \times 10^6 (t + 2176.4)^{-1.3925309}$).
2. **Forward simulation (`H_impact`):** Draw `N_obs` true calendar ages uniformly from `[18,000, 12,850] cal BP` (constant population right up to an instant extinction at `12,850 cal BP`; plus a taphonomy-weighted variant `∝ f_taph(t)` on `[18,000, 12,850]`), sample realistic lab errors from the empirical error distribution of that subset, generate noisy simulated `¹⁴C` measurements $r_i^* \sim \mathcal{N}(\mu_{\text{IC20}}(t_i^*), \sigma_i^2 + \sigma_{\text{IC20}}(t_i^*)^2)$, and recalibrate each simulated catalog through `IntCal20`. Repeat `2,000` times (`seed = 20261123`).
3. **Three sharp tests against `H_impact`:**
   - **Pre-YD drop ratio (`R_pre`):** Ratio of mean SPD density in `13,500–12,900 cal BP` to `14,700–13,500 cal BP` (Bølling–Allerød), compared to `H_impact`'s 95% envelope.
   - **Post-impact Younger Dryas mass (`M_yd`):** Fraction of calibrated SPD probability mass lying inside `12,700–11,700 cal BP` (more than `150` years *after* `12,850 cal BP`), compared to `H_impact`'s 95% and 99% upper bounds (pure calibration-smear leakage!).
   - **High-confidence post-impact survivors (`N_surv`):** Exact count of `Score ≥ 11` and `Score == 12` (AMS) directly dated specimens whose individual calibrated posterior satisfies $P(t < 12,750\text{ cal BP}) > 0.95$ (and $> 0.99$).

### 3.3 Per-Taxon Signor–Lipps Extinction Estimators (`OLE` & `GRIWM`)
For every extinct taxon with `≥ 12` valid dates inside `25,000–9,000 cal BP` (`9` major genera: `Mammut`, `Mammuthus`, `Smilodon`, `Nothrotheriops`, `Oreamnos harringtoni`, `Equus`, `Canis dirus`, `Arctodus`, `Camelops`; also repeated on `Score == 12` AMS-only where `n ≥ 10`):
1. Draw `1,000` posterior calendar-age realizations from each specimen's `IntCal20` posterior.
2. On each realization, take the $k = \min(10, n)$ youngest specimen ages $t_{(1)} \le t_{(2)} \le \dots \le t_{(k)}$ (sorted youngest to oldest; for `OLE` we work in forward time $x_i = -t_{(i)}$ so extinction is the upper endpoint, then map back $T = -X$) and compute:
   - **Youngest dated fossil (`LAD`):** $t_{(1)}$ (median & 95% CI).
   - **Solow (2005) Optimal Linear Estimation (`OLE`):** Exact Weibull extreme-value Signor–Lipps extinction estimator $\hat{T}_{\text{OLE}}$ (median & 95% CI across `1,000` calibrated draws).
   - **GRIWM (Bradshaw et al. 2012):** Inverse-distance-weighted McInerny extinction estimator $\hat{T}_{\text{GRIWM}}$ (median & 95% CI across `1,000` draws).
3. **Cross-taxon synchrony test:** Check how many taxa have `OLE` 95% CIs strictly **older** than `12,896 cal BP` (extinct before YD), **spanning** `12,896–12,835 cal BP`, or strictly **younger** than `12,750 cal BP` (survived past YD onset), plus the cross-taxon spread (`oldest − youngest` median `OLE`).

---

## 4. Pre-Registered Verdict Rule

1. **`collapsed_before_yd`**:
   - Pillar 1 (*Sporormiella*): multi-core median of `t_cp` AND at least one of (`t_2pct`, `t_50pct`) precedes `13,200 cal BP`, with Wilcoxon `p < 0.05` against `12,896 cal BP` and `≥ 70%` of qualifying cores declining before `12,896 cal BP`, **AND**
   - Pillar 2 (`¹⁴C` dates): does *not* show an abrupt `12,850 cal BP` step wipeout (either SPD drops significantly before `12,900 cal BP`, or taxon extinctions precede YD with `< 5` `Score == 12` AMS post-`12,750 cal BP` survivors).
2. **`staggered_spanning_yd`**:
   - Megafauna decline begins before the Younger Dryas in *Sporormiella* (median `> 13,200 cal BP` or `≥ 60%` of cores declining before `12,896 cal BP`) **AND** Pillar 2 shows clear post-impact survival (`≥ 5` `Score == 12` AMS specimens with `P(t < 12,750) > 0.95` AND observed `M_yd` exceeds `H_impact`'s 99th percentile), **OR** taxon `OLE` median extinction dates span `> 1,000` years across both pre-YD (`> 12,896 cal BP`) and inside-YD (`< 12,835 cal BP`) intervals.
3. **`abrupt_at_yd_onset`**:
   - Pillar 1 median decline (`t_cp` and `t_50pct`/`t_2pct`) lies inside `12,896 ± 300 cal BP`, **AND** Pillar 2 matches `H_impact` (`M_yd` within `H_impact`'s 95% envelope and `< 5` `Score == 12` AMS post-`12,750 cal BP` survivors).
4. **`inconclusive_or_divergent`**:
   - Pillar 1 and Pillar 2 fail to meet any of the three criteria above (e.g., wide dating scatter spanning pre-YD and post-YD with no significant lead or clear survivor cluster).

---

## 5. Known Limits (Declared Before Running)

- **Lake-core age-model uncertainty:** Individual Neotoma lake chronologies rely on discrete radiocarbon tie points (some on bulk sediment, which can carry hard-water / old-carbon reservoir offsets of a few centuries in carbonate basins, while terrestrial macrofossil dates do not). Reporting site-by-site dates alongside the independent direct bone-collagen `¹⁴C` archive checks whether hard-water errors distort the picture.
- **Local vs. continental *Sporormiella*:** *Sporormiella* spores disperse only tens to hundreds of metres (Davis & Shafer 2006), so a drop at one lake records local herbivore loss; pooling 11 cores across 7 states tests whether pre-YD decline is regional or continental.
- **Sampling & taphonomic bias in direct `¹⁴C` dates:** Direct megafauna dates are not a random census of North American animals; Rancho La Brea and heavily studied Great Lakes mastodons/mammoths are over-represented, which is why we test both `no_labrea_hq`, `herbivores_hq`, taphonomy-corrected SPDs, and per-taxon `OLE`/`GRIWM` estimators separately.
