# Protocol — Did the raw data in the two retracted 2025 PLOS One Younger Dryas papers warrant retraction?

**Issue:** `#127` (`yd-retracted-plos-audit`)  
**Lane:** `data`  
**Budget:** `$0` (open CC-BY 4.0 PLOS One / Zenodo archives & public IntCal20/Marine20 curves, local CPU only)  
**Status:** Pre-registered prior to extracting or computing audit results on the underlying tables, radiocarbon dates, geochemistry spreadsheets, or `SI Figs S30–S34`.

---

## 1. Exact Question

On February 11, 2026, *PLOS One* simultaneously retracted two 2025 papers by the Comet Research Group (CRG) supporting the Younger Dryas Impact Hypothesis (YDIH):

1. **Paper A — Baffin Bay Marine Cores:** Moore et al. (Aug 6, 2025, `e0328347`; retracted in `e0342613`), claiming a synchronous 12,800-year-old layer of cometary dust, impact microspherules, and platinum-enriched nanoparticles across four Baffin Bay piston cores (`52`, `64`, `67`, `77`).
2. **Paper B — Shocked Quartz:** Kennett et al. (Sep 10, 2025, `e0319840`; retracted in `e0342620`), claiming glass-filled shocked quartz grains at three North American Clovis/Younger Dryas sites (Arlington Canyon CA, Blackwater Draw NM, Murray Springs AZ).

Lead/corresponding author Christopher Moore and coauthors publicly disagreed with both retractions, calling the editorial objections procedural rather than scientific and maintaining that their underlying data and conclusions stand. Conversely, *PLOS One* cited specific chronological, identification, baseline-sampling, and citation flaws in its two retraction notices.

Because **all underlying spreadsheets and Supporting Information PDFs remain openly downloadable** (`Zenodo 14681287`, `Zenodo 15330698`, `pone.0319840.s001.pdf`, plus full JATS XML manuscripts), we do not have to take either *PLOS One* or the authors on trust. We ask:

> **When each specific, data-verifiable claim in *PLOS One*'s two February 2026 retraction notices—and the authors' counter-claims—is tested directly against the authors' own published spreadsheets, Supporting Information tables, microscopy plates, and official `Marine20` / `IntCal20` radiocarbon curves, which editorial criticisms hold up quantitatively, which do not, and was full retraction warranted for each paper independently?**

---

## 2. Primary Data & Blinded Scope

All 13 primary source files are catalogued in [MANIFEST.md](MANIFEST.md) with URLs, licences, byte sizes, and SHA-256 checksums. Before locking, we verified only file integrity, Excel sheet/column headers, and PDF page indices—without extracting or evaluating audit outcomes.

**Explicit Scope Boundary:** A reproducible data audit can verify radiocarbon calibrations, date selection, depth-profile sampling coverage, microspherule/nanoparticle chemistry, mathematical rescaling formulas, bulk oxygen isotopes (`Δ¹⁷O`), reference integrity, and visual/EDS inspection of `SI Figs S30–S34`. It **cannot** physically re-examine the glass-filled quartz thin sections or FIB-TEM foils from Paper B (`e0319840`); deciding whether those specific quartz grains represent genuine hypervelocity/airburst PDFs vs. tectonic/metamorphic/polishing artifacts requires blind physical re-examination by independent shock-metamorphism laboratories.

---

## 3. Four Pre-Registered Quantitative Audit Pillars

### Pillar 1 — Baffin Bay Radiocarbon Calibration & Polar Reservoir Sensitivity (`Paper A: e0328347 / e0342613`)
*PLOS claims tested:* (i) missing foraminifera species/count reporting and ambiguity between calibrated vs. Bayesian-modeled ages; (ii) applying recommended high-latitude deglacial calibration shifts ages younger and outside the Younger Dryas (`12,900–11,700 cal BP` / YDB onset `12,875–12,775 cal BP`).

1. **Metadata audit:** Extract `SI Table S1` (`baffin_bay_si.pdf`, p. 5) and the `Foraminifera: Radiocarbon Dating` section (pp. 219–222) to check verbatim whether dated foraminifera taxa, benthic vs. planktic habits, specimen counts, and 5 cm thickness uncertainties are specified for new and previously published dates.
2. **Exact `Marine20` recalibration across four `ΔR` regimes:** Using official `marine20.14c` (Heaton et al. 2020), calibrate every raw marine `¹⁴C` date in `SI Table S1` (`Cores 52, 64, 67, 77`) via exact numerical integration (`5-yr` grid) with combined variance $\sigma_{\text{tot}}^2 = \sigma_{\text{lab}}^2 + \sigma_{\text{curve}}^2 + \sigma_{\Delta R}^2$ under four pre-registered `ΔR` scenarios:
   - **S0 (Authors' modern Holocene `ΔR`, Pearce et al. 2023):** `Core 52 = +71 ± 50`, `Core 64/67 = +218 ± 50`, `Core 77 = +103 ± 50`.
   - **S1 (Modest deglacial sea-ice offset, `+200 yr` above Holocene):** `ΔR_S0 + 200 ± 100 yr`.
   - **S2 (Moderate deglacial polar offset, `+500 yr` above Holocene, Heaton et al. 2020/2023):** `ΔR_S0 + 500 ± 150 yr`.
   - **S3 (Strong stadial polar reservoir offset, `+800 yr` above Holocene, Olsen et al. 2014 / Heaton et al. 2020):** `ΔR_S0 + 800 ± 200 yr`.
3. **Core-level metrics:** For every date directly inside or immediately bracketing each core's claimed YDB layer (`Core 52: 625–630 cm`, `Core 64: 312–318 cm`, `Core 67: 32–35 cm`, `Core 77: 161–162 cm`), compute calibrated median, `68.3%` and `95.4%` HPD intervals, probability mass in the narrow YDB onset (`12,900–12,700 cal BP`), probability mass across the entire Younger Dryas (`12,900–11,700 cal BP`), and probability younger than `12,700` or `11,700 cal BP`.

### Pillar 2 — Baffin Bay Microspherules, Foraminifera (`SI Figs S30–S34`), and Core 64 vs. Core 67 Background Audit (`Paper A`)
*PLOS claims tested:* (i) `SI Figs S30–S34` show marine foraminifera (`Ca, C, O` + visible micropores) misidentified as cosmic spherule fragments; (ii) sampling coverage cannot assess long-term variability, and an out-of-YDB single-point peak in Core 64 matches the YDB peak in Core 67.

1. **Direct extraction & inspection of `SI Figs S30–S34` (`baffin_bay_si.pdf`, pp. 32–35):** Extract full caption text, EDS elemental tables/labels, and embedded SEM images from `SI Figs S30–S34` into `results/si_figs_s30_s34/` for direct visual and compositional verification (`Ca`, `C`, `O` dominance and foraminiferal pores/chambers). Cross-check `Table S8a` (`CaO wt%`) and `Table S10` (`Ca wt%`) to quantify what fraction of analyzed microspherules/MDPs are Ca-rich (`CaO > 15 wt%`).
2. **Core coverage & non-uniqueness (`SI Table S6`, p. 16):** Parse all depth rows across all four cores (`52, 64, 67, 77`). Compute (a) sampled depth span as a percentage of total core length (`519–875 cm`), (b) peak-to-background contrast within each core, and (c) the exact ratio of **Core 64's highest out-of-YDB peak** to **Core 67's claimed YDB peak** (directly testing *PLOS One*'s Core 64 vs. Core 67 claim).
3. **Blind nanoparticle depth-profile & `Pt/Ir` audit (`Table S7`):** Parse all depth rows in `table_s7_nanoparticles.xlsx` (`Cores 64 and 67`, `Total Mass of NPs` and `Mass Concentration` blocks). For `Pt`, `Ir`, `Pd`, `Ni`, `Co`, `Cr`, and ratios `Pt/Ir`, `Pt/Pd`, `Pt/Fe`, `Ni/Fe`, `Cr/Fe`, `Co/Fe`:
   - Test blindly (without boundary labels) whether the maximum value falls inside the authors' claimed YDB interval (`Core 64: 312–318 cm`, `Core 67: 32–35 cm`) or outside it.
   - Compare nanoparticle `Pt/Ir` and `Pt/Pd` ratios against CI chondrites (`Pt/Ir ≈ 1.9–2.1`, `Pt/Pd ≈ 1.6–1.8`) vs. terrestrial upper continental crust (`Pt/Ir ≈ 14–25`, `Pt/Pd ≈ 1.0`).

### Pillar 3 — Baffin Bay Geochemical Math (`×100` Mixing Formula), Bulk `Δ¹⁷O`, and Citation Audit (`Paper A`)
1. **`×100` Ni/Cr rescaling audit (`Table S8a` & `Table S8b`):** Extract `Fe`, `Cr`, `Ni`, `Co`, `Ir`, `Pt`, `Pd` for every valid Baffin Bay microspherule in `Table S8a` and `Table S8b`. Compute:
   - Fraction of raw microspherules whose `Fe/Cr` and `Fe/Ni` fall in the **terrestrial upper crustal range** (`Fe/Cr > 200`, `Fe/Ni > 200`; Rudnick & Gao 2003 UCC: `Fe/Cr = 426`, `Fe/Ni = 834`) vs. the **chondritic/Comet Wild 2 range** (`Fe/Cr ≤ 150`, `Fe/Ni ≤ 80`; CI chondrite `Fe/Cr = 70, Fe/Ni = 17`).
   - **Pure-terrestrial false-positive control:** Pass 100% terrestrial **Upper Continental Crust (UCC)** (`0%` cosmic material) and **USGS terrestrial basalt `BIR-1G`** (`Fe = 79,000, Cr = 391, Ni = 166 ppm`) through Moore et al.'s exact stated procedure (*multiply total measured Ni and Cr by `100` without first subtracting `99 wt%` terrestrial Ni and Cr*).
   - **Correct mass-balance mixing check:** Subtract `99 wt%` of the sample's own silicate/UCC baseline (`Ni_excess = Ni_meas − 0.99 × Ni_UCC`, `Cr_excess = Cr_meas − 0.99 × Cr_UCC`; also checked with Fe-scaled crustal background `0.99 × (Fe_meas/Fe_UCC) × Ni_UCC`) and count what fraction of microspherules actually show positive excess Ni and Cr consistent with `1 wt%` chondritic admixture (`+108 ppm` Ni, `+26.5 ppm` Cr).
2. **Bulk oxygen isotope check (`moore2025_baffin_bay.xml`, Appendix Table A1):** Extract every Baffin Bay sediment `δ¹⁷O`, `δ¹⁸O`, `Δ¹⁷O*` measurement and test whether any sample deviates from the Terrestrial Fractionation Line (`|Δ¹⁷O*| > 0.06‰`, `3×` the reported `0.02‰` `2SD` obsidian precision).
3. **XML reference & DOI integrity audit (`moore2025_baffin_bay.xml`):** Parse all 187 `<ref>` entries in the published PLOS XML to quantify missing DOIs, duplicated DOIs assigned to different papers, syntactically malformed DOIs, and mismatched citation years/metadata.

### Pillar 4 — Shocked Quartz Chronology, Date Selection & Control-Sampling Audit (`Paper B: e0319840 / e0342620`)
*PLOS claims tested:* (i) selective omission of available radiocarbon dates, untraceable date provenance, and multi-century date scatter around the YD onset; (ii) failure to sample the full core/stratigraphic section above and below, and absence of sedimentation-rate / age-depth models; (iii) zero allegation in the notice against the quartz microscopy images themselves.

1. **Radiocarbon provenance, omission & `χ²` synchrony audit (`kennett2025_si.pdf`, `Tables S1–S4`):**
   - Extract every radiocarbon date listed in `SI Tables S2–S4` for **Arlington Canyon (CA)**, **Blackwater Draw (NM)**, and **Murray Springs (AZ)**, noting lab ID, material, depth/stratum, uncalibrated `¹⁴C` age ± `1σ`, and cited source.
   - Cross-check against the complete published site date inventories verified in Issue `#113` (`Kennett et al. 2008` Table 4 for Arlington Canyon AC-003; `Waters & Stafford 2007` + `Haynes` for Blackwater Draw and Murray Springs). Quantify how many published direct/bracketing dates were omitted and whether each included date's original source is traceable.
   - Recompute the exact **Ward–Wilson `T` (`χ²`) homogeneity statistic** and **IntCal20** calibrated `95.4%` HPD overlap on:
     - **(a)** the authors' exact `3`-date / site-summary selection (testing their reported `χ² = 0.057, p = 0.972`), vs.
     - **(b)** ALL direct YDB-stratum radiocarbon dates at those exact three sites (both raw uncalibrated `¹⁴C` `T`-test and IntCal20 calibrated span).
2. **Vertical background sampling & sedimentation-rate model audit (`SI Tables S5–S8` & `kennett2025_shocked_quartz.xml`):**
   - Extract every depth/stratum row in `SI Tables S5` (Arlington Canyon), `S6` (Blackwater Draw), and `S8` (Murray Springs) for shocked quartz and co-occurring proxies.
   - Quantify for each site: (a) how many strata above and below the YDB were actually analyzed for shocked quartz (vs. `"--"` not quantified), (b) whether the **total quartz grain denominator** (e.g., `~3,000` or `~18,000` grains inspected) is actually reported for every control stratum above and below, and (c) whether any age-depth / sedimentation-rate model is reported anywhere in the manuscript or SI.
3. **Retraction notice scope check (`retraction_shocked_quartz.xml`):** Classify every allegation in `e0342620` by domain (chronology / vertical sampling / microscopy / modeling / misconduct) to assess proportionality directly.

---

## 4. Pre-Registered Verdict Rules (Evaluated Separately for Paper A and Paper B)

Each paper receives an independent, mutually exclusive verdict:

1. **`retraction_strongly_supported`**:
   - **Paper A (Baffin Bay):** At least **3 of 5** substantive pillars/checks fail against the authors' claims in the raw data:
     - (A1) Under moderate deglacial polar reservoir correction (**S2: `+500 yr`**), `≥ 2 of 4` cores shift their calibrated YDB median younger than `12,500 cal BP` (or `< 10%` probability inside `12,900–12,700 cal BP`);
     - (A2) `SI Figs S30–S34` confirm Ca-C-O microfossil/foraminifera morphology & spectra labeled as cosmic spherule fragments;
     - (A3) Core 64 has an out-of-YDB microspherule/MDP peak `≥ 0.80×` Core 67's YDB peak, OR `< 20%` of total core length was sampled across the 4 cores;
     - (A4) Pure terrestrial UCC pushed through Moore et al.'s `×100` Ni/Cr multiplier lands inside the cosmic/Comet Wild 2 box (`Fe/Cr ≤ 150, Fe/Ni ≤ 80`) while `> 50%` of raw microspherules have terrestrial crustal `Fe/Ni > 200`;
     - (A5) Bulk `Δ¹⁷O*` shows `0` extraterrestrial deviations (`|Δ¹⁷O*| ≤ 0.06‰`) AND `≥ 10` XML bibliography DOI/citation integrity errors exist.
   - **Paper B (Shocked Quartz):** **Both** of the following hold AND undermine the paper's core scientific evidence:
     - (B1) Recomputing synchrony with all published direct YDB-stratum dates at those three sites rejects single-year synchrony (`p < 0.01`, overturning the authors' `χ² = 0.057, p = 0.972`) with `≥ 3` omitted direct dates; AND
     - (B2) Quantitative background quartz-grain denominators above and below the YDB are missing or cover `< 3` control strata per site, AND `retraction_shocked_quartz.xml` documents a direct flaw in the quartz microscopy identification itself.
2. **`retraction_mixed_or_harsh`**:
   - At least one major methodological/chronological critique in the retraction notice is verified directly in the raw data (e.g., `(B1)` or `(B2)` chronology/sampling flaws hold for Paper B, OR only 1–2 checks hold for Paper A), **yet** the paper's primary analytical observation (e.g., Paper B's TEM/SEM/EBSD quartz microscopy, which the notice does not even challenge, or Paper A's nanoparticle/microspherule records if core critiques fail) is not shown to be invalid by the verified checks—indicating that while the headline conclusions are overclaimed, full retraction is borderline/harsh relative to Major Correction or Expression of Concern.
3. **`retraction_unsupported`**:
   - Fewer than 1 major critique in the notice verifies against the raw data (for Paper A: `≤ 1 of 5` checks hold; for Paper B: neither `(B1)` nor `(B2)` holds).

---

## 5. Pre-Lock Synthetic Verification

Before locking `protocol.lock` and before running on real data, `analysis/test_audit_plos_retractions.py` must pass all 5 synthetic unit tests:
1. **`Marine20` calibration & `ΔR` shift test:** Verify `calibrate_14c()` integrates to `1.000 ± 1e-6` and that increasing `ΔR` by `+500 yr` shifts a synthetic `11,800 ± 50 ¹⁴C yr BP` marine date strictly younger by `~450–650 cal yr`.
2. **`IntCal20` & Ward–Wilson `T` test:** Verify identical synthetic `10,900 ± 30 ¹⁴C yr BP` dates give `T = 0.0, p = 1.0`, while dates offset by `±150 ¹⁴C yr` give `T > 20, p < 0.001`.
3. **Pure-terrestrial `×100` mixing artifact test:** Verify applying Moore et al.'s `×100` Ni/Cr multiplier to pure 100% terrestrial UCC (`Fe=39,200, Cr=92, Ni=47 ppm`) drops `Fe/Cr` from `426.1 → 4.26` and `Fe/Ni` from `834.0 → 8.34` (false cosmic box!), while subtracting `99%` UCC gives `0.0 ppm` excess Ni/Cr.
4. **Core non-uniqueness detector test:** Verify synthetic isolated YDB spike (`out/ydb = 0.10`) passes uniqueness, while equal out-of-YDB peak (`out/ydb = 1.05`) flags non-uniqueness.
5. **Verdict rule-engine test:** Verify all 3 mutually exclusive verdicts (`retraction_strongly_supported`, `retraction_mixed_or_harsh`, `retraction_unsupported`) trigger accurately for both Paper A and Paper B on synthetic summaries.
