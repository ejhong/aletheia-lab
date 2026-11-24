# Protocol — Did Anyone Smelt Metal Before the Bronze Age? (Ice-Core & Peat Side-Channel, #82)

- **Issue:** #82 (`lane:data`)
- **Date:** 2026-11-24
- **Budget:** $0 (public NOAA, NSF Arctic Data Center, and PANGAEA datasets; local Python computation)

## 1. Exact Question

Between **47,000 and 5,000 years BP** (prior to established Bronze Age metallurgy), do polar ice cores (Greenland and Antarctica), European Alpine glacier ice, and European ombrotrophic peat bogs show *any* sustained, non-crustal, non-volcanic heavy-metal pollution anomaly (`Pb/Ce`, `Pb/Ba`, `Pb EF`, `Cu/Ti`, `Zn/Ti`, `Cd/Ce`, `Bi/Ce`, `Tl/Ce`, or unradiogenic `206Pb/207Pb` isotope excursions) that could mark forgotten prehistoric smelting or mining? If not, what hard physical upper bound—calibrated directly against Roman Empire smelting in the same cores—do these atmospheric archives place on any hypothetical lost metallurgical civilization?

## 2. Public Datasets (Catalogued in `MANIFEST.md`)

Six independent primary archives spanning both hemispheres, three archive types (Arctic ice, Alpine ice, Antarctic ice, and ombrotrophic peat), and 217,000 years of atmospheric history:

1. **RECAP Ice Core (East Greenland, McConnell et al. 2024, `doi:10.18739/A2N87320M`):** 14,041 continuous ICP-MS measurements spanning `7,977–116 yr BP` (`Pb`, `Ce` crustal normalizer, `S` volcanic tracer, `nssCa`, `Mn`, `Sr`). Covers both the pre-Bronze test window (`7,977–5,000 BP`) and Bronze Age / Roman / Medieval / Industrial positive controls (`5,000–116 BP`). Uses the continuous `v.1/3-2018` age scale across the full 8 kyr core (and `DRI_NGRIP2` age scale for `< 3,000 BP` cross-check).
2. **GISP2 Ice Core (Central Greenland, McConnell et al. 2020, `doi:10.18739/A2445HD27`):** 5,240 continuous ICP-MS measurements across Dansgaard–Oeschger 10–12 (`47,371–40,439 yr BP`, GICC05) with `Pb`, `Ce`, `Al`, `Cd`, `Tl`, `Bi`, and `S` (volcanic tracer). Provides an ultra-high-resolution Ice Age Greenland test window and multi-element natural baseline.
3. **Dome du Goûter Ice Core (French Alps, Legrand & McConnell 2024, NOAA Study `80979`):** European mid-latitude glacier archive (`9,751 BP–1997 CE`, inside the European/Mediterranean atmospheric basin) with `Pb`, `Ce`, `Al`, `Fe`, `Dust`, and an interpolated depth-age model.
4. **EPICA Dome C Ice Core (East Antarctica, Vallelonga et al. 2010, NOAA Study `10033`):** Continuous Southern Hemisphere `Pb`, `Ba` (crustal dust normalizer), `Pb/Ba`, and `206Pb/207Pb` & `208Pb/207Pb` isotope ratios spanning `217,050–2,010 yr BP`, covering the entire `40,000–5,000 BP` window against a `217,000–40,000 BP` Pleistocene natural baseline.
5. **Füramoos Peat Bog (Southern Germany, Kern et al. 2021, `PANGAEA.929755` & `PANGAEA.929751`):** Central European ombrotrophic peat bog with 536 XRF-CS `Pb norm` and crustal `EF` measurements spanning `14,336–200 cal BP`, plus 47 ICP-MS `Pb` concentration and `206Pb/207Pb` isotope measurements.
6. **Store Mosse Peat Bog (Southern Sweden, Kylander et al. 2019, `PANGAEA.903892`):** 71 Northern European ombrotrophic peat samples spanning `6,420–95 cal BP` measuring `Pb`, `Cu`, `Zn`, `Ti`, and `Al` (adding copper and zinc smelting tracers alongside lead).

*Data hygiene rule:* Negative/zero sentinel values (e.g., `-1.0` missing flags in DRI CSVs) and missing (`na`/`NaN`) entries are excluded prior to ratio and flux computation.

## 3. Pre-Registered Analysis Plan

### Test 0 — Positive-Control Calibration (Can the archives detect ancient smelting?)
In each archive extending into historical antiquity (`RECAP`, `Dome du Goûter`, `Füramoos`, `Store Mosse`), compare crustal-normalized lead enrichment factor (`EF_Pb`) and non-crustal excess lead (`ncPb`) across fixed archaeological windows:
- **Pre-Bronze test baseline:** `> 5,000 yr BP` (strictly `5,000–47,400 BP` across archives)
- **Bronze / Iron Age:** `5,000–2,150 yr BP` (`3050–200 BCE`)
- **Roman Empire positive control:** `2,150–1,650 yr BP` (`200 BCE–300 CE`)
- **High Medieval positive control:** `1,000–500 yr BP` (`950–1450 CE`)
- **Industrial positive control:** `< 250 yr BP` (`> 1700 CE`)

Compute `EF_Pb = (Pb / Ref) / k_base` where `Ref` is the archive's conservative crustal dust tracer (`Ce` in RECAP, GISP2, Dome du Goûter; `Ba` in EPICA Dome C; published `EF` in Füramoos; `Ti` in Store Mosse) and `k_base` is the empirical median `(Pb/Ref)` during the pre-5,000 BP volcanic-masked baseline (with upper continental crust `(Pb/Ce)_UCC = 19/83 = 0.2289` from Rudnick & Gao 2003 / McConnell et al. 2018 also reported for RECAP/GISP2/DDG!). Compute non-crustal lead excess `ncPb = max(0, Pb − k_base × Ref)`. Verify via one-sided Mann–Whitney U test that the Roman Empire positive control shows statistically significant elevation (`p < 10⁻⁴` and median `EF_Pb ≥ 2.0`) above the pre-5,000 BP baseline.

### Test 1 — Volcanic-Masked Pre-Bronze-Age (`47,000–5,000 BP`) Anomaly Scan
1. **In-core volcanic masking:** In continuous ICP-MS cores with co-measured sulfur (`RECAP`, `GISP2`), flag volcanic samples where `S > median_local(S) + 5 × MAD_local(S)` (computed in 500-yr rolling windows, expanded by ±2 yr) so volcanic chalcophile degassing (`Pb`, `Cd`, `Bi`, `Tl`) is cleanly separated from sustained anthropogenic smelting. Report both raw and volcanic-masked statistics.
2. **Sustained century-scale and quarter-century binning:** Aggregate continuous cores (`RECAP`, `GISP2`) into non-overlapping **100-year** and **25-year** bins using bin medians (which reject single-point drilling/break contamination spikes while preserving multi-decade smelting episodes like Phoenician, Carthaginian, or Roman mining).
3. **Anomaly criterion:** Flag any sustained interval (`≥ 50 yr` or `≥ 2` consecutive discrete samples) in `47,000–5,000 BP` where non-volcanic `EF_Pb ≥ 3.0` (or `≥ 2.0` paired with a `> 2σ` unradiogenic `206Pb/207Pb` drop) OR where century-median `ncPb` reaches `≥ 50%` of the Roman Empire median `ncPb` in that archive. Check for cross-archive replication within `±300 yr`.

### Test 2 — Multi-Element Smelting Side-Channels (`Cu`, `Zn`, `Cd`, `Bi`, `Tl`)
- In **Store Mosse peat (`6,420–5,000 BP` vs. `< 5,000 BP`)**, compute `EF_Cu = (Cu/Ti) / median_pre5ka(Cu/Ti)` and `EF_Zn = (Zn/Ti) / median_pre5ka(Zn/Ti)` and test for sustained pre-5 ka anomalies (`EF ≥ 3.0`) as well as historical positive controls.
- In **GISP2 Ice Age (`47,371–40,439 BP`)**, compute volcanic-masked 100-year and 25-year bin medians of `EF_Cd`, `EF_Bi`, and `EF_Tl` (normalized to `Ce`) to test for non-crustal, non-volcanic chalcophile metallurgy during MIS 3.

### Test 3 — Radiogenic Lead Isotope (`206Pb/207Pb`) Ore-Lead Check
- In **EPICA Dome C (`40,000–5,000 BP` vs. `217,050–40,000 BP`)**, test whether `Pb/Ba` enrichment or `206Pb/207Pb` exhibits any excursion `> 2 SD` outside the natural Pleistocene (`217–40 ka`) envelope.
- In **Füramoos peat (`14,336–5,000 BP` vs. `< 5,000 BP`)**, verify the downward shift in `206Pb/207Pb` during Bronze/Roman/Medieval pollution (`< 5,000 BP`) and test whether any pre-5,000 BP horizon shows a coupled unradiogenic isotope drop (`< mean_pre5ka − 2 SD`) and `EF_Pb ≥ 2.0`.

### Test 4 — Hard Physical Upper Bound on Lost Pre-Bronze-Age Metallurgy
In both high-resolution Northern Hemisphere ice cores with direct Roman Empire positive controls (`RECAP` East Greenland `7.98–5.0 ka`, and `Dome du Goûter` French Alps `9.75–5.0 ka`), compute:
1. The maximum and 95th-percentile volcanic-masked century-scale `ncPb` excess during `> 5,000 BP` divided by the Roman Empire (`2,150–1,650 BP`) median `ncPb` excess (`UpperBound_Roman_equiv`).
2. Scale to approximate Northern Hemisphere atmospheric Pb emission rate (metric tons/yr) using McConnell et al. (2018, *PNAS* 115:5726) FLEXPART-calibrated Roman peak European atmospheric emissions (`~3.3 kt/yr` Pb emitted to air, ~40–80 kt/yr total lead-silver production). Also compute the GISP2 MIS 3 (`47.4–40.4 ka`) `ncPb` upper bound relative to RECAP's Roman signal (noting glacial dust/transport caveats).

## 4. Pre-Registered Verdict Rules

- **Positive (Pre-Bronze-Age metallurgy signal):** At least one volcanic-masked, sustained (`≥ 50 yr` or `≥ 2` consecutive samples) non-crustal heavy-metal anomaly in `47,000–5,000 BP` achieving `EF ≥ 3.0` (or `≥ 2.0` with a coupled `> 2σ` unradiogenic `206Pb/207Pb` shift) that either reaches `≥ 50%` of the Roman Empire `ncPb` excess or replicates across `≥ 2` independent archives within `±300 yr`.
- **Null (No evidence of pre-Bronze-Age metallurgy; quantitative upper bound established):** Positive controls (Roman Empire & Medieval) clearly detected above pre-5 ka background (`p < 10⁻⁴`, `EF ≥ 2.0`), while **zero** pre-5 ka non-volcanic anomalies meet the positive threshold, establishing a hard physical upper bound on hypothetical lost smelting.
- **Inconclusive:** Positive controls fail to rise significantly above background, or a single-archive pre-5 ka excursion exceeds the threshold without volcanic, dust-provenance, or bog-trophic explanation.

## 5. Verification

Synthetic unit tests (`analysis/test_metallurgy.py`) verifying crustal enrichment factor arithmetic, volcanic sulfur MAD masking, century-bin median resistance to single-point contamination spikes, and upper-bound scaling before evaluating real archives.
