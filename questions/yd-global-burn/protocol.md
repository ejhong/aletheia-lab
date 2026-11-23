# Did 9% of Earth's biomass burn 12,800 years ago?

Issue #69 · Lane: data · Written 2026-11-23 by Antigravity (Google DeepMind), directed by Eugene

## Question

Supporters of the Younger Dryas impact hypothesis (Wolbach et al. 2018, Parts 1 & 2) argue that a cosmic impact around 12,800 years ago ignited global wildfires consuming ~10 million km² (~9% of Earth's terrestrial biomass) and triggering an "impact winter". Earlier lab questions (#43 `ice-core-fire` and #60 `cooling-ammonium`) tested Greenland ammonium—which mainly tracks North America—and found a century-long swell starting 30–40 years after the cold began, alongside smaller rises after most other abrupt coolings.

Here we test the **global** burning claim directly in two completely independent global archives, with every rule fixed before looking at `12,000–13,600` cal BP:

1. **Global atmospheric carbon (Antarctic ice cores):** In well-mixed global air trapped in Antarctic ice (Taylor Glacier `CO2` & `δ13C-CO2`, WAIS Divide `CO2`, and a 155 kyr Antarctic `δ13C-CO2` compilation), does the 300-year window around the Younger Dryas onset (`[12,650, 12,950)` cal BP) show an **exceptional terrestrial-carbon combustion pulse** (rapid `CO2` rise paired with a sharp negative `δ13C-CO2` excursion) compared against every other 300-year window in the same records?
2. **Global terrestrial fire (Global Charcoal Database v3):** Across well-dated, high-resolution sediment charcoal cores spanning the last 14,750 years across multiple continents, does `[12,650, 12,950)` cal BP stand out as an **exceptional global or multi-continent fire peak** against every other 300-year window?

Neither archive alone settles whether a cosmic impact happened (e.g., an impact on ice or ocean need not burn 9% of Earth's biomass). Together they directly test the "global impact wildfire / ~9% biomass burned / impact winter" mechanism.

## Why it matters

Greenland ammonium only sees North America and is confounded by local snowfall thinning and soil ammonia. Global atmospheric `CO2` and `δ13C-CO2` mix across both hemispheres within ~1–2 years: burning ~9% of Earth's terrestrial C₃ biomass (~50–90 GtC at `δ13C ≈ −25‰`) injects isotopically light carbon into the global atmosphere (`ΔCO2 > 0` and `Δδ13C < 0` simultaneously), regardless of wind direction. Meanwhile, the Global Charcoal Database v3 (Marlon et al. 2016) directly tests whether sediment charcoal peaks synchronously across continents once low-resolution binning artifacts are controlled.

What the literature says (verified from NOAA file headers and open abstracts; closed-access bodies noted):

- **For.** Wolbach et al. 2018 (*J. Geol.* 126:165–184 & 185–205; abstracts read via search, bodies paywalled/`unverified`) cite Taylor Glacier `CO2` and `δ13C-CO2` perturbations alongside multi-continent charcoal records to estimate ~10 million km² (~9% of Earth's biomass) burned at the YD onset.
- **Primary atmospheric data.** Bauska et al. 2016 (*PNAS*, doi:10.1073/pnas.1513868113; abstract read from NOAA file header) report century-scale `δ13C-CO2` perturbations at **both 16.3 ka and 12.9 ka** in Taylor Glacier, attributing them to rapid oxidation of organic land carbon or enhanced Southern Ocean air–sea gas exchange.
- **Primary charcoal context.** Marlon et al. 2009 (*PNAS* 106:2519–2524; abstract read) examined 35 North American charcoal records and found no continent-wide fire spike at 12.9 ka, noting that apparent peaks at 12.9 ka appeared only in low-resolution cores while climate-linked surges clustered at 13.9, 13.2, and 11.7 ka. Marlon et al. 2016 (*Biogeosciences*, GCD3 readme read) compiled 736 global charcoal records.

The target window `[12,650, 12,950)` cal BP is not chosen blind; this is a pre-locked test of a nominated horizon.

## Data and sources

All public from NOAA WDS Paleoclimatology. Exact URLs, retrieval dates, licences and SHA-256 hashes are in `MANIFEST.md`.

| Short name | File | What | Span (cal BP) |
|---|---|---|---|
| `TG` | `taylor2018d13co2.txt` | Taylor Glacier `CO2` (ppm) & `δ13C-CO2` (‰ VPDB); contains all 61 rows of Bauska et al. 2016 plus 48 glacial rows (Bauska et al. 2018) | 10,919–22,330 & 34,688–46,441 |
| `WAIS` | `antarctica2015co2wais-noaa.txt` | WAIS Divide high-resolution `CO2` (ppm), Marcott et al. 2014 / Bereiter et al. 2015 | 10–23,030 (24 yr median spacing in 10–22 ka) |
| `EGG` | `eggleston2016d13co2-noaa.txt` | 3-core Antarctic `δ13C-CO2` composite (EDC, EDML, Talos Dome), Eggleston et al. 2016 | 600–155,000 (100 yr uniform grid) |
| `GCD3` | `GCD3_PUBLIC_VERSION_2013_01-Oct-2013.mdb` | Global Charcoal Database v3 (Marlon et al. 2016), exported via `mdb-export` to `data/gcd_csv/` | 736 global sites |

**What was looked at before locking (`explore/structure.py`):** file headers, column names, age spans, sampling spacings, table row counts, regional site counts, and baseline medians/SDs strictly excluding `[12,000, 13,600]` cal BP. No `CO2`, `δ13C-CO2`, or charcoal measurement inside `[12,000, 13,600]` cal BP was printed, summarized or plotted before locking.

## Method

### Common target window and comparison grid

Ages in all four datasets are in **cal yr BP** (years before 1950 CE). The climatic onset of the Younger Dryas in Greenland is 12,896 yr b2k = **12,846 cal BP**; Wolbach et al. (2018) place the YDB around **12,800 cal BP**.

- **Target window (`k = 0`):** `[12,650, 12,950)` cal BP (`a0 = 12,650`, width `W = 300` yr, centred at `12,800` cal BP). This 300-year allowance deliberately accommodates Antarctic gas-age uncertainty (~50–150 yr) and terrestrial radiocarbon uncertainty without penalizing slight timing offsets.
- **Comparison windows:** non-overlapping 300-year windows `k` covering `[a0 + 300k, a0 + 300(k+1))`.
- **Rank definition:** For any measure where larger values indicate stronger burning, the target's rank is `1 + (number of other usable windows strictly greater than target)`. `N` is the number of usable windows including `k = 0`. *Top 5%* means `rank ≤ max(1, floor(0.05 * N))`; *Top 1%* means `rank ≤ max(1, floor(0.01 * N))`. Ties `q` and realised fraction `(rank + q) / N` are reported.

---

### Archive A — Global Atmospheric Carbon (Antarctic ice cores)

#### File reading
- **`TG` (`taylor2018d13co2.txt`):** Skip `#` lines and header line; tab-separated; read `age = col[1]`, `co2 = col[2]`, `d13c = col[4]`. Keep rows where `age`, `co2`, and `d13c` parse as finite floats. If duplicate ages exist, average their `co2` and `d13c` values. Sort ascending by `age`.
- **`WAIS` (`antarctica2015co2wais-noaa.txt`):** Skip `#` lines and header line; tab-separated; read `age = col[1]`, `co2 = col[2]`. Keep finite rows; average duplicate ages; sort ascending by `age`.
- **`EGG` (`eggleston2016d13co2-noaa.txt`):** Skip `#` lines and header line; tab-separated; read `age = col[0]`, `d13c = col[1]`. Keep finite rows; sort ascending by `age`.

#### Gridding and measures (forward-in-time change)
Because age runs backwards (larger age = older), a burning pulse moving forward in time from older age `t + Δ` to younger age `t` produces **positive** `ΔCO2(t, Δ) = CO2(t) − CO2(t + Δ)` and **positive** `D13_drop(t, Δ) = δ13C(t + Δ) − δ13C(t)` (i.e., `δ13C` becomes more negative).

For each series, construct values on a regular grid `t_j = a0 + j * step`:
- **`WAIS_CO2` (span `[10,250, 21,950)` cal BP, 39 windows, `step = 100` yr):** bin `j` is the arithmetic mean of all raw WAIS observations in `[t_j, t_j + 100)`. A bin is missing if it has 0 observations. For each bin `j` in window `k`, compute forward 100-yr rise `r1_j = x_j − x_{j+1}` and 200-yr rise `r2_j = x_j − x_{j+2}`. Window measure **`CO2_rise`** = maximum over the 3 bins in window `k` of `max(r1_j, r2_j)` (taking whichever of `r1_j, r2_j` is finite). A window is usable if at least 2 of its 3 bins have a finite score.
  - Also reported alongside: **`WAIS_CO2_50`** (`step = 50` yr, span `[10,250, 21,950)`, scoring `max(50-yr rise, 100-yr rise)` per 50-yr bin; usable if ≥ 4 of 6 bins have a score).
- **`TG_BURN` and `TG_D13C` (Taylor Glacier; span `[11,150, 22,250)` ∪ `[35,150, 46,250)` cal BP, `step = 100` yr):** linearly interpolate `co2` and `d13c` onto grid points `t_j = a0 + 100j`, marking `t_j` missing if `t_j` lies outside a segment or if the bracketing raw samples straddling `t_j` are more than `500` years apart (so nothing is ever interpolated across the 12 kyr gap or sparse stretches). At each grid point `t_j` in `[a0 + 300k, a0 + 300(k+1))` (`j = 3k, 3k+1, 3k+2`):
  - `dCO2_100 = CO2(t_j) − CO2(t_{j+1})`, `dCO2_200 = CO2(t_j) − CO2(t_{j+2})`
  - `d13drop_100 = δ13C(t_{j+1}) − δ13C(t_j)`, `d13drop_200 = δ13C(t_{j+2}) − δ13C(t_j)`
  - **Primary isotopic combustion score (`BURN`):** `max_{j in window, h in {100, 200}} [ max(0, dCO2_h) × max(0, d13drop_h) ]` (units: `ppm · ‰`). Nonzero *only* when atmospheric `CO2` rises and `δ13C-CO2` simultaneously drops toward light terrestrial carbon.
  - **Secondary isotope-only score (`D13_drop`):** `max_{j in window, h in {100, 200}} d13drop_h` (units: `‰`).
  - A window is usable if at least 2 of its 3 grid points have a finite score. Both full two-transect ranks (primary: `TG_BURN`, ~74 windows) and deglacial-only ranks (`[11,150, 22,250)`, ~37 windows) are reported.
- **`EGG_D13C` (Eggleston 155 kyr composite; span `[950, 154,850)` cal BP, ~513 windows, `step = 100` yr):** interpolate onto `t_j = a0 + 100j` (gap limit `300` yr; raw grid is already 100 yr). Measure: **`D13_drop`** = `max_{j in window, h in {100, 200}} (δ13C(t_{j+h/100}) − δ13C(t_j))`. Usable if at least 2 of 3 grid points have a finite score.

#### Physical forward check (reported alongside)
Using single-box isotopic mass balance against pre-event atmospheric inventory `M_0 = 2.12 × CO2_0` GtC and terrestrial C₃ signature `δ_bio = −25‰`, compute the implied airborne terrestrial carbon injection `ΔC_air` required to produce the observed `δ13C-CO2` drop in Taylor Glacier (and compare against both a 50% airborne fraction and Wolbach et al.'s ~9% global biomass claim, ~50–90 GtC), plus direct comparison against the 16.3 ka (Heinrich Stadial 1) event in the same file.

---

### Archive B — Global Land Charcoal (`GCD3`)

#### Table extraction and deterministic unit selection
Export `SITE`, `REGION`, `SAMPLE`, `CHARCOAL`, and `DATE_INFO` from `GCD3_PUBLIC_VERSION_2013_01-Oct-2013.mdb` via `mdb-export`.
- For each site `ID_SITE`, collect all rows in `CHARCOAL` with finite non-negative `QUANTITY` (`>= 0`) whose `ID_SAMPLE` has a finite `EST_AGE` in `SAMPLE`.
- If a site has multiple `ID_UNITS` values, select `ID_UNITS == SITE.PREF_UNITS` if that unit accounts for at least 50% of the site's valid charcoal rows; otherwise select the single `ID_UNITS` with the largest row count (tie-break: lowest integer `ID_UNITS`). If multiple rows still share the same `(ID_SAMPLE, ID_UNITS)`, take their mean `QUANTITY`.

#### Site inclusion tiers (fixed before looking at charcoal values)
All three tiers require a site to have at least 15 valid samples inside `[10,000, 15,000]` cal BP, non-zero variance inside its standardization span, and samples covering `[1,250, 14,750]` (at least one sample `<= 1,250` and at least one `>= 14,750` cal BP) for the primary **13.5 kyr span** (`[1,250, 14,750)`, 45 non-overlapping 300-yr windows).

- **Tier C1 (Primary — high-resolution & well-dated):** median sample spacing `<= 100` yr inside `[10,000, 15,000]` cal BP AND at least 2 entries in `DATE_INFO` with `AGE_CALIB` (or `AGE_C14` if `AGE_CALIB` missing) inside `[9,500, 15,500]` cal BP.
- **Tier C2 (High-resolution, all dating):** median sample spacing `<= 100` yr inside `[10,000, 15,000]` cal BP.
- **Tier C3 (All resolutions, including coarse cores):** any median sample spacing (explicit test of Marlon et al. 2009's warning that coarse cores can manufacture an apparent 12.8 ka peak).

Reported alongside: the same three tiers restricted to the **late-glacial span** `[10,250, 14,750)` (15 non-overlapping 300-yr windows, including sites that end before 1,250 BP so long as they span `[10,250, 14,750]`).

#### Within-site standardization and global composite
For each included site over its span (`[1,250, 14,750)` for primary; `[10,250, 14,750)` for late-glacial):
1. Let `c` be half the smallest strictly positive `QUANTITY` of that site inside the span (if all values are zero, drop site). Transform `y = log10(QUANTITY + c)`.
2. Compute `z = (y − mean(y)) / sd(y)` (population SD; drop site if `sd == 0`).
3. Bin each site into non-overlapping **300-year windows** `k` (`[12,650 + 300k, 12,950 + 300k)`): site window value `z_{s,k}` is the arithmetic mean of its `z` values in window `k` (missing if site has 0 samples in window `k`).
4. Across all sites present in window `k` (window usable if ≥ 50% of tier sites are present):
   - **`M_mean` (Global composite mean Z):** arithmetic mean of `z_{s,k}` across present sites.
   - **`E_mean` (Primary — local-background excess of composite mean Z):** `M_mean(k) − median(M_mean(k−2 … k+2))` (5-window centred median = ±600 yr local background, removing slow glacial-to-Holocene warming trends; requires ≥ 3 of 5 windows present).
   - **`F_peak` (Primary — synchronous peaking fraction):** fraction of present sites in window `k` with `z_{s,k} >= +1.0` (also report `+1.5` alongside).
5. Also compute a **100-year binned** version (`step = 100` yr, 135 bins across `[1,250, 14,750)` and 45 bins across `[10,250, 14,750)`) scoring the peak 100-year excess inside each 300-year window (`E_100`, using a ±300 yr / 7-bin local median) so a sharp sub-century fire cannot be washed out by 300-year averaging.

#### Synthetic fire-pulse sensitivity test (what the charcoal test can see)
Add a synthetic 100-year global fire pulse of amplitude `A ∈ {+0.5, +1.0, +1.5, +2.0}` SD affecting a fraction `p ∈ {0.25, 0.50, 0.75}` of Tier C1 sites simultaneously at 200 random placements (excluding `k = −1, 0, 1`, `numpy.random.default_rng(69)`), and report the fraction of placements reaching the top 5% and top 1% of `E_mean` and `F_peak`.

---

### Decision rule (fixed in advance)

Each archive receives its own pre-registered verdict, and both are combined transparently:

#### Archive A (Global Atmosphere)
Primary series: **`TG_BURN`** (Taylor Glacier isotopic combustion score, 2 transects), **`WAIS_CO2`** (WAIS Divide CO₂ rise), and **`EGG_D13C`** (Eggleston 155 kyr δ¹³C-CO₂ drop).
- **Exceptional:** `TG_BURN` is in the **top 1%** AND at least one of `WAIS_CO2` or `EGG_D13C` is in the **top 5%**.
- **Unusual:** At least two of `{TG_BURN, WAIS_CO2, EGG_D13C}` reach the **top 5%** (and not already Exceptional).
- **Single-record only:** Exactly one of the three primary series reaches the **top 5%**.
- **Not met:** Zero of the three primary series reach the **top 5%**.

#### Archive B (Global Charcoal, Tier C1 primary over `[1,250, 14,750)`)
Primary measures: **`E_mean`** (local excess of composite mean Z), **`F_peak`** (fraction of sites ≥ +1.0 SD), and **`E_100`** (peak 100-yr local excess inside the 300-yr window).
- **Exceptional:** At least two of `{E_mean, F_peak, E_100}` reach the **top 1%** (rank 1 of 45) in Tier C1.
- **Unusual:** At least two of `{E_mean, F_peak, E_100}` reach the **top 5%** (rank ≤ 2 of 45) in Tier C1.
- **Not met:** None of the above.

#### Joint summary
- **Strong support for global burning:** Both archives **Exceptional**, or one **Exceptional** and one **Unusual**.
- **Partial / mixed:** At least one archive is **Exceptional**, **Unusual**, or **Single-record only** (and not Strong support).
- **Not supported:** Both archives **Not met** (read together with the physical mass-balance check and synthetic charcoal pulse recovery).

### Reported alongside (not part of the rule)
1. **Window width sensitivity:** 150-yr (`[12,725, 12,875)`) and 600-yr (`[12,500, 13,100)`) windows, and half-window phase shift (`+150` yr).
2. **All three charcoal tiers (`C1`, `C2`, `C3`)** and **late-glacial-only span (`[10,250, 14,750)`)**, specifically comparing high-res (`C1`/`C2`) vs. coarse-only cores (`C3 \ C2`).
3. **Regional charcoal breakdown** (North America, Europe, South/Central America, Asia/Australasia/Africa).
4. **Top 10 windows** in every primary series (to see where 16.3 ka HS1, 14.6 ka Bølling, 13.9 ka, 13.2 ka, and 11.7 ka sit relative to 12.8 ka).
5. **Physical mass-balance estimate** of implied terrestrial carbon release (GtC) from Taylor Glacier `(ΔCO2, Δδ13C)` at `k = 0` vs. 16.3 ka.

### Checks before the lock
1. Unit tests (`analysis/test_burn.py`) on synthetic series verifying forward-in-time sign conventions (`CO2` rise + `δ13C` drop = positive `BURN`; ocean-warming `CO2` rise with flat `δ13C` = zero `BURN`), interpolation gap-masking, charcoal log-Z standardization, planted peak = rank 1, and every branch of the verdict logic.
2. A **decoy run** (`python3 analysis/burn.py --decoy`) that removes `k = 0` from every archive and substitutes a decoy window at least 3 windows away (seed 69), verifying the entire pipeline on real data without revealing `k = 0`.

## Known weaknesses

- **Firn smoothing in Antarctic ice:** Air diffuses in firn before bubble close-off, smoothing sub-decadal atmospheric spikes over ~20–60 yr at WAIS Divide and ~50–150 yr at Taylor Glacier / EDC. A brief 1-year CO₂/δ¹³C spike is attenuated and broadened, though its *integrated* century-scale carbon injection remains visible if ~50–90 GtC burned (which takes centuries to re-equilibrate with the deep ocean).
- **Oceanic vs. terrestrial δ¹³C ambiguity:** A negative δ¹³C-CO₂ excursion paired with rising CO₂ can come from either terrestrial organic carbon oxidation (fire/permafrost/soils) OR Southern Ocean upwelling of respired deep-ocean carbon (Bauska et al. 2016). So a positive atmospheric signal is *necessary* for burning 9% of Earth's biomass, not *sufficient* to prove fire over ocean upwelling.
- **GCD3 age-model heterogeneity:** Site chronologies in GCD3 use heterogeneous age models (`EST_AGE`) calibrated on older curves (pre-IntCal20), which can smear a truly synchronous peak across ±100–200 years. Using a 300-year target window and reporting a 600-year sensitivity check mitigates this at the cost of diluting sharp peaks.
- **Single-vendor initial run:** Written and run in one session by Antigravity (Google DeepMind); open to independent code/results review or full replication from this protocol by a second vendor's agent (Claude Fable) before closing the question.

## Budget

$10 (zero spend so far; reserved for optional second-vendor review or replication).
