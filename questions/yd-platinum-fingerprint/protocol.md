# Protocol — Do Younger Dryas platinum and HSE anomalies fingerprint a comet—or volcanic/crustal sources?

- **Question:** Issue `#120` (`yd-platinum-fingerprint`)
- **Lane:** `data`
- **Date drafted:** 2026-11-24 (UTC)
- **Budget:** `$0` (all primary datasets are open-access; analysis runs locally in Python)
- **Blinding status:** At the time of writing and locking this protocol, **no geochemical sample values, element ratios, source-classification distances, or blind stratigraphic peak counts have been inspected** in Hall's Cave (Sun et al. 2020), Page-Ladson (Nana Yobo et al. 2026), Moore et al. (2017), Moore et al. (2019), Wonderkrater (2026), Laacher See Tephra (Green et al. 2025), or Chicxulub K–Pg (`kpg2025_MOESM4.xlsx`). Only file existence, table captions, column headers, and row counts were checked.

---

## 1. Exact scientific question

After nine prior locked studies in Aletheia Lab on the Younger Dryas impact hypothesis (YDIH), **platinum and highly siderophile element (HSE) anomalies** around `~12.9–12.8 ka` remain the strongest physical evidence still cited for an extraterrestrial input. Earlier study `#76` (`yd-platinum-volcanism`) tested only the *timing* of the Greenland GISP2 platinum layer (finding it ~18–26 years after the published start of Younger Dryas cooling) and did not test its geochemical *origin* or the wider terrestrial HSE record.

This study asks two quantitative questions using primary public geochemical tables from both YDIH proponents and independent geochemists, benchmarked directly against confirmed Chicxulub K–Pg impact layers and real volcanic gas condensates:

1. **Pillar 1 — Geochemical source fingerprinting & cross-site coherence:** When measured across the full suite of six highly siderophile elements (`Os, Ir, Ru, Pt, Pd, Re`) plus osmium isotopes (`¹⁸⁷Os/¹⁸⁸Os`), do Younger Dryas Boundary (YDB) anomalous horizons match **extraterrestrial / confirmed-impact** compositions (CI chondrites, iron meteorites, and real Chicxulub K–Pg impactites/boundary clays), or do they match **volcanic gas condensates / aerosols** and **upper continental crust (UCC)**? And do different claimed YDB sites across continents share a consistent impactor ratio (`Pt/Ir`, `Pt/Pd`), or do they scatter by orders of magnitude?
2. **Pillar 2 — Blind stratigraphic peak-uniqueness audit:** When continuous stratigraphic columns spanning above and below the YDB are scanned **blindly** (without using author boundary labels) by a fixed statistical peak detector, are platinum, `Pt/Pd`, and unradiogenic-`Os` spikes uniquely concentrated at the `~12.9–12.8 ka` horizon, or do comparable excursions recur elsewhere in the same cores?

---

## 2. Datasets (all verified in `MANIFEST.md`)

### Tier 1 — Native machine-readable primary tables (zero OCR)
1. **Hall's Cave, Texas (Sun et al. 2020, *Science Advances* 6:eaax8587, `data/sun2020_sm.pdf` Table S1):** Continuous bulk stratigraphic profile (`~15–11 ka`) with `Depth (cm BDT)`, `Age (cal ka BP)`, `¹⁸⁷Os/¹⁸⁸Os ± 2σ`, and all six HSEs (`Os, Ir, Ru, Pt, Pd, Re` in `ppt`).
2. **Page-Ladson, Florida (Nana Yobo et al. 2026, *Science Advances* 12:eaec9030, `data/nanayobo2026_sm.pdf` Table S2):** Continuous bulk stratigraphic profile across Units 4d–5 (`~13.7–10.8 ka`, YDB at 4e/5 interface `851 cm`, `12.82 ± 0.05 ka`) with `Depth (cm)`, `¹⁸⁷Os/¹⁸⁸Os ± 2σ`, and all six HSEs (`Os, Ir, Ru, Pt, Pd, Re` in `ppb`).
3. **Confirmed Chicxulub K–Pg Impact Benchmark (`data/kpg2025_MOESM4.xlsx`, *Nature Communications* 2025 `10.1038/s41467-025-58112-x`):**
   - `Data 2` (IODP M0077 Chicxulub peak-ring core: full 6 HSEs + `¹⁸⁷Os/¹⁸⁸Os`).
   - `Data 3` (Mexican K–Pg boundary sections, e.g., Bochil: full 6 HSEs).
   - `Data 5` (Global pelagic K–Pg compilation: `Os, Ir, Pt, Re, ¹⁸⁷Os/¹⁸⁸Os`).
   - Plus **Petriccio K–Pg boundary clay** (`data/sun2020_sm.pdf` Table S2).
4. **Volcanic & Crustal Reference Benchmarks:**
   - **Volcanic gas condensates** (`data/sun2020_sm.pdf` Table S2, citing Yudovskaya et al. 2008 Kudryavy, Chaplygin et al. Tolbachik, Zelenski et al. Erta Ale) + **Niuatahi-Motutahi Tonga submarine volcanic sulfur condensates** (Park et al. 2016, *GCA* 174, Table 1 midpoints: `Pt = 597, Pd = 545, Ru = 26.5, Ir = 0.5, Re = 13400 ppt`).
   - **Laacher See Tephra** (`data/green2025_s001.docx` Table 3: 17 pumice/lithic/bulk volcanic tephra samples, `Pt` and `Ir` in `ppb`).
   - **Upper Continental Crust (UCC)** (`data/sun2020_sm.pdf` Table S2: `Os = 31, Ir = 22, Ru = 30, Pt = 510, Pd = 520, Re = 198 ppt`; `¹⁸⁷Os/¹⁸⁸Os = 1.26`, Peucker-Ehrenbrink & Jahn 2001).
   - **Chondrite & Iron Meteorite end-members** (CI chondrite: `Os = 490, Ir = 460, Ru = 710, Pt = 990, Pd = 560, Re = 37 ppb`, `¹⁸⁷Os/¹⁸⁸Os = 0.126`, Wasson & Kallemeyn 1988 / Horan et al. 2003; plus chondrite & iron meteorite classes parsed from `data/sun2020_sm.pdf` Table S3).
5. **Wonderkrater, South Africa (Thackeray et al. 2026, *F1000Research* 15:1089, `data/wonderkrater2026.html` Table 1):** YDB vs. Non-YDB PGE nanoparticle ratio averages (`Pt/Pd, Pt/Ir, Pt/Rh, Pt/Ru`).

### Tier 2 — Proponent continuous `Pt / Pd` profiles (programmatic OCR with strict sanity checks)
6. **Moore et al. (2017, *Scientific Reports* 7:44031, `data/moore2017_s1.pdf` Tables 1 & 2):** Continuous depth profiles of bulk `Pt`, `Pd`, and `Pt/Pd` across 11 North American sites (7 Eastern, 4 Western/Midwestern).
7. **Moore et al. (2019, *Scientific Reports* 9:15121, `data/moore2019_s1.pdf` Tables 2 & 3):** Continuous lake-core `Pt`, `Pd`, and `Pt/Pd` with Bayesian calibrated ages at White Pond, South Carolina.

**Programmatic OCR quality gate (fixed before running):** Every OCR-parsed row from `moore2017_s1.pdf` and `moore2019_s1.pdf` is accepted only if (a) `Pt` and `Pd` parse as valid non-negative floats within physically valid bounds (`0 ≤ Pt ≤ 200 ppb`, `0 ≤ Pd ≤ 200 ppb`), and (b) whenever `Pt > 0`, `Pd > 0`, and a tabulated `Pt/Pd` column is present, the parsed ratio agrees with `Pt / Pd` within `15%` relative tolerance (eliminating decimal-drop OCR glitches automatically). Any site column retaining `< 6` verified depth levels after QA is excluded from Pillar 2 and logged transparently.

---

## 3. Pre-registered analysis plan

### Pillar 1A — Full 6-HSE Compositional Fingerprinting & Two-Component Mixing Model

All full-HSE samples (`Os, Ir, Ru, Pt, Pd, Re` all `> 0`) from **Hall's Cave** (`sun2020_sm.pdf` Table S1) and **Page-Ladson** (`nanayobo2026_sm.pdf` Table S2) are partitioned objectively into:
- **Target anomalous/YDB-onset samples:** Any sample whose calibrated age lies in `13.1–12.6 ka` (or Page-Ladson Unit 4e/5 interface `847–860 cm` spanning the YD onset) **OR** whose `¹⁸⁷Os/¹⁸⁸Os` drops strictly below `local_median - 0.15` (capturing all unradiogenic excursions claimed as either impact or volcanic inputs). We report results for **both** (i) the strict YDB-onset age window (`13.1–12.6 ka`) AND (ii) all unradiogenic-Os excursion samples separately.
- **Local background samples:** Remaining radiogenic samples outside the unradiogenic excursions.

For every sample vector $x = (\text{Os}, \text{Ir}, \text{Ru}, \text{Pt}, \text{Pd}, \text{Re})$ (converted to uniform `ppt` units):
1. **CI-normalized Centered Log-Ratio (CLR) distance (`d_CLR`):**
   Define $z_j = \log_{10}(x_j / \text{CI}_j)$ and center $\tilde{z}_j = z_j - \frac{1}{6}\sum_{k=1}^6 z_k$. Compute the Euclidean distance $d_{\text{CLR}}(x, p) = \|\tilde{z}(x) - \tilde{z}(p)\|_2$ to each of the four pre-registered reference class centroids:
   - `chondrite`: CI chondrite ($\tilde{z} = 0$) and mean chondrites from Table S3.
   - `kpg_impact`: median CLR vector of confirmed Chicxulub K–Pg impact-layer samples (`Ir ≥ 0.5 ppb` in `kpg2025_MOESM4.xlsx` Data 2 & Data 3, plus Petriccio K–Pg).
   - `volcanic`: geometric-mean CLR vector of volcanic gas condensates (Kudryavy, Tolbachik, Erta Ale from Table S2; we also evaluate each individual volcano separately as a sensitivity check).
   - `ucc`: Upper Continental Crust vector from Table S2.
   Centering removes absolute dilution effects and tests purely whether the *inter-element proportions* match extraterrestrial vs. volcanic vs. crustal reservoirs.

2. **Continuous Two-Component Mixing Fit (`RMSE_mix`, 6 HSEs + `¹⁸⁷Os/¹⁸⁸Os`):**
   Because real sediments are mixtures of local crustal background $C_{\text{bg}}$ and an exogenous source $C_{\text{src}}$, we fit for each sample:
   $$C_{\text{mix}}(f) = (1 - f)\,C_{\text{bg}} + f\,C_{\text{src}}, \qquad f \in \{0\} \cup 10^{\text{linspace}(-6, 0, 601)}$$
   together with exact mass-balance osmium isotope mixing:
   $$\left(\frac{^{187}\text{Os}}{^{188}\text{Os}}\right)_{\text{mix}}(f) = \frac{(1 - f)\,\text{Os}_{\text{bg}}\,R_{\text{bg}} + f\,\text{Os}_{\text{src}}\,R_{\text{src}}}{(1 - f)\,\text{Os}_{\text{bg}} + f\,\text{Os}_{\text{src}}}$$
   where $C_{\text{bg}}, R_{\text{bg}}$ are the site's own empirical radiogenic background medians (and UCC as a pre-registered sensitivity check), and $C_{\text{src}}, R_{\text{src}}$ are tested across **three competing exogenous source classes**:
   - **Cosmic — CI Chondrite:** $R_{\text{src}} = 0.126$, CI 6-HSE vector.
   - **Cosmic — Low-Ir Differentiated Iron Meteorite (Petaev 2013 hypothesis):** $R_{\text{src}} = 0.126$, using the highest-`Pt/Ir` iron meteorite class parsed from Table S3 (e.g., IVB/IIIAB/low-Ir iron) as the strongest possible cosmic steelman!
   - **Volcanic — Gas Condensate / Aerosol:** $R_{\text{src}} = 0.15$ (mantle/arc volcanic range `0.13–0.18`), tested across Kudryavy, Tolbachik, and Erta Ale condensates (taking the best-fitting volcanic condensate, and also reporting Kudryavy alone so model-selection degrees of freedom are transparent).
   Objective function: combined log-concentration + Os-isotope RMSE:
   $$\text{RMSE}_{\text{mix}}(f) = \sqrt{\frac{1}{7}\left[\sum_{j=1}^6 \left(\log_{10} C_j - \log_{10} C_{\text{mix},j}(f)\right)^2 + \left(\frac{R - R_{\text{mix}}(f)}{0.20}\right)^2\right]}$$
   (scaling `¹⁸⁷Os/¹⁸⁸Os` by `0.20` puts a 0.20 isotope shift on equal footing with a 1-order-of-magnitude elemental mismatch).
   Define $\Delta\text{RMSE} = \min(\text{RMSE}_{\text{CI}}, \text{RMSE}_{\text{iron}}) - \text{RMSE}_{\text{volcanic}}$: **negative** favors a cosmic impactor (either chondrite or iron); **positive** favors a volcanic condensate. We test `median(ΔRMSE)` with a two-sided Wilcoxon signed-rank test and `2,000`-draw bootstrap 95% CI.

3. **Mandatory Positive Control — Real Chicxulub K–Pg Impact Samples:**
   Apply the exact same CLR classifier and two-component mixing fit (with `UCC` as background) to all confirmed K–Pg impact-horizon samples in `kpg2025_MOESM4.xlsx` (`Data 2` M0077 & `Data 3` Mexican K–Pg sections with `Ir ≥ 0.5 ppb` and all 6 HSEs finite). **Pre-registered validity threshold:** At least **`75%`** of confirmed Chicxulub K–Pg samples MUST classify closer to `chondrite / kpg_impact` than to `volcanic / ucc` on CLR distance AND have `ΔRMSE < 0` (favoring cosmic over volcanic). If the positive control fails, Pillar 1 is declared invalid (`ambiguous_or_mixed`).

---

### Pillar 1B — Diagnostic Ratios & Cross-Site Coherence Test

Across ALL YDB target sites in our corpus (Hall's Cave, Page-Ladson, Moore 2017 sites, White Pond 2019, Wonderkrater 2026, and published GISP2 Petaev 2013 peak `Pt/Ir`), tabulate diagnostic ratios (`Pt/Ir`, `Pt/Pd`, `Os/Ir`, `Re/Os`, `¹⁸⁷Os/¹⁸⁸Os`) alongside confirmed K–Pg impact layers (`kpg2025_MOESM4.xlsx`), Laacher See Tephra (`green2025_s001.docx`), volcanic gas condensates (`sun2020_sm.pdf` Table S2 + Park et al. 2016), CI chondrite, and UCC.
- Measure **cross-site dispersion** (`log10` IQR and full range in orders of magnitude = `log10(max / min)`) of `Pt/Ir` and `Pt/Pd` across claimed YDB sites vs. across confirmed Chicxulub K–Pg boundary samples (`kpg2025_MOESM4.xlsx`).
- Compare YDB sites against the **Chondritic/K–Pg diagnostic box** (`0.5 ≤ Pt/Ir ≤ 6.0`, `0.5 ≤ Pt/Pd ≤ 4.0`, `Os/Ir ≤ 3.0`, `Re/Os ≤ 0.5`).

---

### Pillar 2 — Blind Stratigraphic Peak-Uniqueness Audit

Every continuous stratigraphic column with `n ≥ 6` verified levels (Hall's Cave TX, Page-Ladson FL, each QA-passing Moore 2017 site, and White Pond 2019) is scanned **blindly** without using author YDB labels:
1. For each series `x = (x_1, ..., x_n)` (`Pt`, `Pt/Pd`, `Os`, `Ir`, and `-¹⁸⁷Os/¹⁸⁸Os` where available):
   - Baseline $M = \text{median}(x)$, robust scale $S = \text{MAD}(x) = \text{median}(|x - M|)$. If $S = 0$, fall back to $\text{IQR}(x)/1.349$; if still $0$, fall back to $0.1\,M$ (or $0.05$ for `¹⁸⁷Os/¹⁸⁸Os`).
   - Modified z-score: $z_i = 0.6745\,(x_i - M) / S$ (or $z_i = 0.6745\,(M - x_i) / S$ for unradiogenic `¹⁸⁷Os/¹⁸⁸Os` drops).
   - **Blind peak criterion:**
     - Concentration / ratio series (`Pt`, `Pt/Pd`, `Os`, `Ir`): $x_i \ge 3.0\,M$ **AND** $z_i \ge 3.5$.
     - Osmium isotope drop (`¹⁸⁷Os/¹⁸⁸Os`): $M - x_i \ge 0.15$ **AND** $z_i \ge 3.5$.
   - Contiguous flagged levels (separated by `≤ 1` sample step) are merged into a single stratigraphic **excursion event** represented by its peak level.
2. **Unmasking against the target YDB window:**
   - For calibrated-age columns (Hall's Cave, Page-Ladson, White Pond): target window is **`13.0–12.6 ka`** (or Page-Ladson Unit 4e/5 boundary `848–855 cm`).
   - For depth-only columns (Moore 2017 Tables 1–2): target window is the **author-marked YDB horizon (`± 1` adjacent sample step)** as published in Moore et al. (2017) Supplementary Tables 1–2 / Figures 2–3.
3. **Summary statistics (reported separately for Independent Full-HSE Columns vs. Proponent `Pt/Pd` Columns, and pooled):**
   - Total blind excursion events **inside** vs. **outside** the YDB window (`f_inside = N_inside / N_total`).
   - **Non-uniqueness rate:** Fraction of columns having `≥ 1` blind excursion strictly *outside* the YDB window.
   - **Exact global-maximum permutation test:** Let $p_k = m_k / n_k$ be the fraction of levels in column $k$ that fall inside the target YDB window. Under the null hypothesis that the column's single highest anomaly (`argmax`) lands uniformly at random among its $n_k$ levels, compute the exact Poisson-binomial probability $P(\text{hits} \ge H_{\text{obs}})$ by exact dynamic programming (and verify against 10,000 Monte Carlo draws).

---

## 4. Pre-registered decision rules (mutually exclusive verdicts)

1. **`cosmic_impact_fingerprint`**:
   - Chicxulub K–Pg positive control passes (`≥ 75%` classify as cosmic/K–Pg on CLR and `ΔRMSE < 0`), **AND**
   - Pillar 1A: `> 50%` of full-HSE YDB target samples classify closest to `chondrite` or `kpg_impact` on CLR distance AND have `median ΔRMSE < 0` (favoring cosmic over volcanic), **AND**
   - Pillar 1B: `median Pt/Ir ≤ 6.0` across YDB sites with measured `Pt/Ir`.
2. **`non_cosmic_and_non_unique`**:
   - Chicxulub K–Pg positive control passes (`≥ 75%`), **AND**
   - Pillar 1A: `≥ 60%` of full-HSE YDB target samples classify closer to `volcanic` or `ucc` than to `chondrite`/`kpg_impact` on CLR distance AND `median ΔRMSE > 0` (favoring volcanic over cosmic), **AND**
   - Pillar 2: Across independent full-HSE columns, either `≥ 50%` of blind excursions fall *outside* the YDB window OR the blind global-maximum permutation test is non-significant (`p ≥ 0.01`).
3. **`non_cosmic_with_ydb_anomaly`**:
   - Chicxulub K–Pg positive control passes (`≥ 75%`), **AND**
   - Pillar 1A: `≥ 60%` of full-HSE YDB target samples classify closer to `volcanic` or `ucc` than to `chondrite`/`kpg_impact` AND `median ΔRMSE > 0`, **AND**
   - Pillar 2: Independent full-HSE columns show statistically significant, predominantly unique YDB boundary clustering (`permutation p < 0.01` AND `> 50%` of blind excursions inside YDB).
4. **`ambiguous_or_mixed`**:
   - Chicxulub K–Pg positive control fails (`< 75%`), **OR** Pillar 1A falls in the indeterminate band (`40–60%` cosmic vs. volcanic/UCC, or CLR and mixing RMSE disagree in sign).

---

## 5. What would count for and against each claim

- **For a cosmic impactor (comet or meteorite):** Full 6-HSE patterns at Hall's Cave and Page-Ladson track the `UCC + CI chondrite` (or iron meteorite) mixing trajectory with `Ir` and `Ru` rising alongside `Os` and `Pt`, low `Re/Os`, `Pt/Ir` near `~1–5` across sites, matching real Chicxulub K–Pg boundary clays; and blind stratigraphic scans isolate one unique excursion at `12.9–12.8 ka`.
- **For volcanic aerosols / terrestrial fractionation:** Unradiogenic `¹⁸⁷Os/¹⁸⁸Os` and/or `Pt` excursions appear *without* proportionate refractory `Ir` or `Ru`, carry steep `Re`- and `Pt`-enriched volcanic-condensate slopes (`Pt/Ir >> 10`, high `Re/Os`), scatter by orders of magnitude across sites (unlike K–Pg impactites), and/or recur blindly at non-YDB stratigraphic horizons.

---

## 6. Verification & replication criteria

- Unit tests (`analysis/test_pt_fingerprint.py`) verify before lock that:
  1. Synthetic `UCC + 1% CI chondrite` mixtures classify as `chondrite` (`ΔRMSE < 0`), synthetic `UCC + volcanic condensate` mixtures classify as `volcanic` (`ΔRMSE > 0`), and pure `UCC` classifies as `ucc`.
  2. The blind peak detector recovers a synthetic single-horizon spike (`100%` inside, `p < 0.01`) and flags multi-peak noise columns (`< 50%` inside).
  3. The exact Poisson-binomial permutation `p`-value matches Monte Carlo to `< 0.005`.
- Because this is a `lane:data` study, all raw inputs are public and hashed in `MANIFEST.md`; a second-vendor agent can re-run the entire protocol from scratch without inspecting `results/`.
