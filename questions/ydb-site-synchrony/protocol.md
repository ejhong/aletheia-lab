# Protocol — Are the claimed Younger Dryas "impact layer" sites actually the same age?

**Issue:** `#113` (`ydb-site-synchrony`)
**Lane:** `data`
**Budget:** `$0` (all public open-access datasets, local computation only)
**Status:** Pre-registered prior to running any statistical calculations on real data.

---

## 1. Exact Question

Proponents of the Younger Dryas Impact Hypothesis (YDIH) argue that thin sediment layers ("Younger Dryas Boundary", YDB) containing microspherules, nanodiamonds, meltglass, or platinum at 23–32 sites across four continents were deposited synchronously by a single cosmic event around `12,835–12,735 cal BP` (Kennett et al. 2015, *PNAS*, calibrated on IntCal13; shifted ~40 yr older on IntCal20). Critics (Meltzer et al. 2014, *PNAS*; Jorgeson et al. 2020, *Quaternary Research*) argue that most sites lack direct dating on the proxy horizon, carry century-to-millennium uncertainties, or scatter wider than a single synchronous event allows.

We ask two tightly defined, independently reproducible questions:

1. **Direct-`¹⁴C` Synchrony on IntCal20 (with Positive Control and Radiocarbon-Plateau Forward Simulation):** When every available raw uncalibrated `¹⁴C` measurement (`¹⁴C BP ± σ`) from directly within claimed YDB layers across 9 Northern Hemisphere sites on 3 continents is recalibrated on **IntCal20** without circular single-phase priors, is the cross-site dispersion consistent with a **single synchronous calendar year** $t_0 \in [12700, 12950]$ cal BP (both under pure measurement + curve uncertainty **M0** and under a generous inter-laboratory + old-wood tolerance model **M1**), and how does it compare to a **real, independently proven single-year volcanic catastrophe** right next to the Younger Dryas — the **Laacher See Tephra (`LST`, `13,006 ± 9 cal BP`)**?
2. **Precision & Placebo-Year Overlap Audit across All 32 Claimed YDB Sites:** Across all 32 YDB sites tabulated in Kennett et al. (2015, Fig. 2: 23 Bayesian-modeled + 9 unmodeled), how many sites actually have both direct dates on the proxy layer and tight (`≤ 300 yr`) 95% credible intervals, and how strongly does Kennett et al.'s 23-site "95% CI overlap" discriminate `12,800 cal BP` from arbitrary **placebo years** `±250`, `±500`, and `±1,000` years away?

---

## 2. Primary Data

Every dataset is listed in [MANIFEST.md](MANIFEST.md) with URL, retrieval date, licence, byte size, and SHA-256 hash. All raw tables are extracted programmatically from the primary open-access PDFs/CSVs in `data/` by `analysis/site_synchrony.py`:

- **Calibration curve:** `intcal20.14c` (Reimer et al. 2020), interpolated onto a 1-year grid spanning `10,500–15,500 cal BP`.
- **Positive Control (`Laacher See Tephra`, `LST`):** `reinig_lst_edtable1.pdf` (Reinig et al. 2023 *Nature*, Extended Data Table 1, p. 9) — `16` high-precision raw `¹⁴C` dates directly tied to the single-year Laacher See eruption (`13,006 ± 9 cal BP`) across `5` localities up to `335 km` apart (`Krumpa`, `Miesenheim 2`, `Miesenheim 4`, `Kruft`, `Near Laacher See monastery`). Tested both as all `16` dates and collapsed to `5` locality inverse-variance weighted means.
- **Pillar 1 Direct-YDB Uncalibrated `¹⁴C` Database (`9` Northern Hemisphere sites across North America, Europe, and the Middle East):**
  1. **Arlington Canyon, CA** (`kennett2008_arlington.pdf`, Table 4, p. 9): all `12` AMS `¹⁴C` dates from the `392–503 cmbs` YDB proxy horizon (`UCIAMS-47239` through `UCIAMS-36304`, including `Beta-161032`).
  2. **Aalsterhut, Netherlands** (`vanhoesel2012.pdf`, Table 1, p. 2): all `14` AMS `¹⁴C` dates (`GrA-49570` through `GrA-49524`) from the Usselo horizon charcoal layer, plus the `3` basal nanodiamond-bearing dates (`GrA-49515`, `GrA-49509`, `GrA-49524`) isolated by Kennett et al. (2015).
  3. **Abu Hureyra, Syria** (`moore2020_abuhureyra_sm.pdf`, Table S1, p. 31): direct Level 445 YDB meltglass-peak date (`UCIAMS-105429: 11,070 ± 40 ¹⁴C BP`).
  4. **Lake Hind, Manitoba** (`lakehind_dates.csv`, Teller et al. 2019 Table 1): direct YDB-layer date `UCIAMS-29317` (`10,610 ± 25 ¹⁴C BP` at `33 cm`, the exact date plotted in Kennett et al. 2015 Fig. 1) and overlying `PSUAMS-1572` (`10,850 ± 35 ¹⁴C BP` at `32 cm`).
  5. **Bull Creek, OK** (`holliday2023_esr.pdf`, Table 5, p. 30, transcribing Bement et al. 2014 *PNAS*): direct YDB nanodiamond-peak date `BC21` (`298–307 cmbs: 11,070 ± 60 ¹⁴C BP`).
  6. **Murray Springs, AZ** (`waters2007_clovis.pdf`, Table 1, p. 4): direct Clovis / Unit F1 YDB-equivalent hearth mean (`n = 8: 10,885 ± 50 ¹⁴C BP`).
  7. **Sheriden Cave, OH** (`waters2007_clovis.pdf`, Table 1, p. 4): direct Clovis/YDB layer below artifacts (`n = 2: 10,920 ± 50 ¹⁴C BP`).
  8. **Indian Creek, MT** (`waters2007_clovis.pdf`, Table 1, p. 4): direct Clovis-age / YDB horizon (`n = 1: 10,980 ± 110 ¹⁴C BP`).
  9. **Blackwater Draw, NM** (`waters2007_clovis.pdf`, Table 1, p. 4): direct Clovis / basal black mat horizon (`n = 3: 11,300 ± 235 ¹⁴C BP`).
- **Pillar 2 Full Site Catalog (`32` YDB sites):** `kennett2015_main.pdf` Fig. 2 (p. 3: all 23 Bayesian-modeled sites + 9 unmodeled sites with modeled age, ±68% CI, 95% CI upper/lower bounds, total/rejected/accepted date counts, quality ranking, and `Date on proxies` direct-dating flag) and Fig. 1 (p. 2: Kennett et al.'s 9 highlighted direct-on-proxy dates), cross-referenced with `meltzer2014_main.pdf` Table 1 (29 sites).

---

## 3. Exact Methods & Test Statistics

### 3.1 Exact IntCal20 Calibration (No Circular Phase Priors)

For any uncalibrated measurement $(y_i, \sigma_i)$, the posterior probability density on the 1-year calendar grid $t \in [10500, 15500]$ cal BP under a flat prior is:
$$p_i(t) \propto \frac{1}{\sqrt{\sigma_i^2 + \sigma_c(t)^2}} \exp\!\left( -\frac{(y_i - \mu_c(t))^2}{2(\sigma_i^2 + \sigma_c(t)^2)} \right)$$
where $\mu_c(t)$ and $\sigma_c(t)$ are the linearly interpolated IntCal20 mean and $1\sigma$ curve error at calendar year $t$. From each normalized posterior $p_i(t)$ we compute:
- Calibrated median $m_i$ (`50th` percentile of cumulative posterior),
- Calibrated mean and standard deviation,
- Exact **95.4% Highest Posterior Density (HPD)** interval(s) (minimum-width set summing to $\ge 0.954$).

### 3.2 Pillar 1 — Direct-`¹⁴C` Synchrony & Forward-Simulated Plateau Benchmark

We evaluate **three pre-registered YDB panels** alongside the **Laacher See Tephra (`LST`) positive control**:
- **Panel 1A-Primary (9 sites, 1 primary YDB `¹⁴C` value per site):** Uses the full inverse-variance weighted mean within the YDB horizon for multi-date sites (`Arlington Canyon` 12 dates; `Aalsterhut` 14 dates), Kennett Fig. 1's direct `UCIAMS-29317` at `Lake Hind`, and the direct YDB `¹⁴C` dates for the remaining 6 sites.
- **Panel 1A-Favorable (9 sites, YDIH-favorable old-wood-mitigated selection):** Gives the impact hypothesis the maximum benefit of the doubt on old wood and stratigraphy: replaces Arlington Canyon's 12-date average with its youngest direct YDB wood date (`Beta-161032: 10,860 ± 70`), replaces Aalsterhut's 14-date average with Kennett et al.'s 3 basal nanodiamond-layer dates (`GrA-49515/49509/49524` weighted mean), and replaces Lake Hind `UCIAMS-29317` with `PSUAMS-1572` (`10,850 ± 35` at `32 cm`).
- **Panel 1B-AllRaw (all 32 individual direct-YDB `¹⁴C` measurements across the 9 sites):** Every raw uncalibrated `¹⁴C` date directly from the YDB layers, without collapsing sites or discarding outliers.

On each panel (and on `LST`), we compute:
1. **Ward & Wilson (1978) Uncalibrated Homogeneity Statistic $T$:**
   $$T = \sum_{i=1}^{n} \frac{(y_i - \bar{y}_w)^2}{\sigma_i^2}, \qquad \bar{y}_w = \frac{\sum_{i=1}^n y_i / \sigma_i^2}{\sum_{i=1}^n 1/\sigma_i^2}$$
   with analytical $\chi^2_{n-1}$ p-value $p_{\chi^2}$.
2. **Calibrated Cross-Site Dispersion:** Sample standard deviation `SD_cal` and interquartile range `IQR_cal` of the IntCal20 calibrated medians $\{m_i\}$, plus the **maximum simultaneous 95.4% HPD overlap** across all candidate calendar years $t \in [12000, 13500]$ cal BP.
3. **Forward-Simulated Single-Year Plateau Benchmark (`N = 2,000` iterations per candidate year, fixed RNG seed `20261124`):**
   We sweep candidate true impact calendar years $t_0 \in \{12700, 12725, \dots, 12950\}$ cal BP (`11` grid points; for `LST`, $t_0 \in \{12950, 12975, \dots, 13100\}$ cal BP). At each $t_0$, we generate `2,000` synthetic single-year datasets matching the exact sample size $n$ and exact published errors $\{\sigma_i\}$ under two generative models:
   - **Model M0 (pure measurement + IntCal20 curve uncertainty):**
     $$y_i^{\text{sim}} \sim \mathcal{N}\!\left(\mu_c(t_0),\; \sigma_i^2 + \sigma_c(t_0)^2\right)$$
   - **Model M1 (realistic inter-laboratory + old-wood tolerance):**
     $$y_i^{\text{sim}} \sim \mathcal{N}\!\left(\mu_c(t_0),\; \sigma_i^2 + \sigma_c(t_0)^2 + 20^2\right) + \mathbf{1}_{\text{wood/charcoal}} \cdot \text{Exp}(\text{mean}=50\text{ yr})$$
     where an extra $20\text{ ¹⁴C yr}$ ($1\sigma$) accounts for inter-laboratory scatter and a one-sided exponential offset with mean $50\text{ yr}$ models inbuilt old-wood age on wood/charcoal samples (applied to every wood/charcoal sample in YDB and `LST`; zero for short-lived/non-wood samples where flagged, and applied to all 9 site-level charcoal/wood dates in Panel 1A).
   For each simulated catalogue, we compute both $T^{\text{sim}}$ and calibrated median dispersion $\text{SD}_{\text{cal}}^{\text{sim}}$ on IntCal20, and take the **most generous** (largest) one-sided p-value across the entire candidate year sweep:
   $$p_{T,\text{best}} = \max_{t_0} \frac{1 + \#\{T^{\text{sim}}(t_0) \ge T_{\text{obs}}\}}{N + 1}, \qquad p_{\text{SD},\text{best}} = \max_{t_0} \frac{1 + \#\{\text{SD}_{\text{cal}}^{\text{sim}}(t_0) \ge \text{SD}_{\text{cal,obs}}\}}{N + 1}$$
   Taking $\max_{t_0}$ guarantees that no single assumed calendar year can unfairly penalize the single-event hypothesis.

### 3.3 Pillar 2 — Precision & Placebo-Year Overlap Audit (`32` YDB Sites)

Parsing Kennett et al. (2015) Fig. 2 directly from `kennett2015_main.pdf`:
1. **Dating & Precision Inventory:** Count total claimed sites (`32`), unmodeled sites (`x`), modeled sites (`23`), sites with a direct date on the proxy layer (`Date on proxies = yes`), distribution of `95% CI` widths (`range_upper - range_lower`), and the fraction of all 32 sites achieving **both** a direct date on the proxy layer **and** a `95% CI width ≤ 300 yr` (matching the ±150 yr target width).
2. **Placebo-Year Overlap Curve:** Sweep a hypothetical target year $T$ across `14,000` to `11,500 cal BP` in `10-yr` steps (`251` test years). At each $T$, record the fraction of Kennett et al.'s `23` modeled sites (and separately for High `n=9`, Medium `n=8`, and Low `n=6` quality tiers) whose published `95% CI` covers $T$.
   - Compare overlap at `12,800 cal BP` against placebo years at `±250 yr` (`13,050`, `12,550`), `±500 yr` (`13,300`, `12,300`), and `±1,000 yr` (`13,800`, `11,800`).
   - Compute the **Effective Specificity Windows** `W_50` and `W_80`: total calendar-year span over which `≥ 50%` (and `≥ 80%`) of Kennett's 23 modeled sites simultaneously overlap a single arbitrary calendar year.
3. **Outlier-Rejection Audit:** Sum total, accepted, and OxCal-rejected dates across all 23 modeled sites and by quality tier.

---

## 4. Pre-Registered Verdict Rules (Mutually Exclusive)

The final verdict is determined strictly by the following hierarchy:

1. **`synchronous_single_event`**:
   - Positive control `LST` passes `M1` (`p_T,M1 ≥ 0.05` and `p_SD,M1 ≥ 0.05`); AND
   - Pillar 1 **Panel 1A-Primary** is consistent with a single year under pure measurement + curve error (`p_T,M0 ≥ 0.05` AND `p_SD,M0 ≥ 0.05`) with `≥ 7/9` sites' unmodeled IntCal20 95.4% HPDs overlapping a single common year; AND
   - Pillar 2 shows tight chronological specificity (`W_80 ≤ 400 yr` centered within `12,850 ± 100 cal BP`).
2. **`asynchronous_diachronous_scatter`**:
   - Positive control `LST` passes `M1` (`p_T,M1 ≥ 0.05` and `p_SD,M1 ≥ 0.05`); AND
   - Pillar 1 rejects a single synchronous year even under the realistic inter-lab + old-wood model **M1** on **BOTH** Panel 1A-Primary **AND** Panel 1A-Favorable (`p_T,M1 < 0.01` AND `p_SD,M1 < 0.01` across the entire `12,700–12,950 cal BP` sweep).
3. **`underconstrained_not_synchronous`**:
   - Positive control `LST` passes `M1` (`p_T,M1 ≥ 0.05` and `p_SD,M1 ≥ 0.05`); AND
   - Pillar 1 rejects pure single-year synchrony on Panel 1A-Primary (`p_T,M0 < 0.01` OR `p_SD,M0 < 0.01`), **while** Panel 1A-Favorable either fails `M0` or only passes `M1` after selective old-wood filtering/widening; AND
   - Pillar 2 confirms an **uncertainty-width overlap illusion**: `W_50 ≥ 1,000 yr` (i.e., `≥ 50%` of Kennett's 23 modeled sites overlap arbitrary placebo years spanning at least a full millennium) AND `< 25%` of all 32 claimed YDB sites have both a direct date on the proxy layer and a `95% CI ≤ 300 yr`.
4. **`ambiguous_or_mixed`**:
   - Any outcome not cleanly satisfying (1), (2), or (3) — including if the real single-year `Laacher See Tephra` positive control fails `M1` (which would indicate that our synchrony test over-rejects real single-year Late Glacial deposits).

---

## 5. Pre-Lock Synthetic Verification

Before locking `protocol.lock` and before running on real data, `analysis/test_site_synchrony.py` must pass all synthetic verification checks:
1. IntCal20 calibration curve loads cleanly and recovers known single-date calibrated medians within `±5 yr`.
2. A synthetic 9-site single-year synchronous catalogue generated at `12,850 cal BP` passes Pillar 1 (`p_T,M0 ≥ 0.05` and `p_SD,M0 ≥ 0.05`).
3. A synthetic 9-site diachronous catalogue staggered uniformly across `300 calendar years` (`12,700–13,000 cal BP`) is cleanly rejected under `M0` (`p < 0.01`), and a `600-yr` staggered catalogue is cleanly rejected under `M1` (`p < 0.01`).
4. Pillar 2's placebo-year overlap calculator returns `W_50 ≈ 200 yr` for synthetic tight (`±100 yr`) intervals and `W_50 ≥ 1,000 yr` for synthetic wide (`±600 yr`) intervals.
