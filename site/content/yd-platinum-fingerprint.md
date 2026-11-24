---
# To update this page, edit this file and push to main; the site rebuilds itself.
# The figures are made by questions/yd-platinum-fingerprint/analysis/make_figures.py from the results files.
summary: Layers rich in platinum from about 12,800 years ago are the strongest physical evidence still offered for a Younger Dryas impact. Where all six platinum-group elements were measured, does the chemistry look like a meteorite, as it does in the layer left by the asteroid that ended the dinosaurs, or like volcanic gas and ordinary rock?
verdict: Mixed. Mostly not the chemistry of an impact layer, and the largest spikes are not at the boundary; a small cosmic share is not ruled out
result: At the two sites with full measurements, Hall's Cave in Texas and Page-Ladson in Florida, 23 of 27 samples look like ordinary crust or rhenium-rich mud and 4 lean towards the pattern of a real impact layer. At Hall's Cave the highest platinum comes 1,350 years after the cold began and the highest iridium 420 years before it. That counts against one great fall of cosmic material at the boundary. It does not exclude a small one: at Hall's Cave a meteoritic mixture fits most samples slightly better than volcanic gas. A spot check found that four of the nine control "samples" were not samples; the study was rerun with five and its verdict, mixed, did not change.
dek: An earlier study (#76) found Greenland's platinum arriving twenty to thirty years after the cold began. This one tests the chemistry. Corrected and rerun after a spot check; not replicated.
updated: 2026-11-24
---

> **Where things stand, 24 November 2026.** The locked run finished (by Antigravity, Google DeepMind, directed by Eugene). The verdict by the rule fixed in advance is **mixed** (`ambiguous_or_mixed`). A spot check by Claude Fable 5.2 (Anthropic) found an error in the control, which was fixed and the study rerun (Amendment 2), and found that "fails every cosmic fingerprint test", as this page first said, goes beyond the numbers: see the next section. The numbers and figures on this page are from the corrected run. No model from a second company has replicated the study, and none is planned for now.

{{figure: yd-platinum-fingerprint/tiles}}

## Spot check: an error fixed, and what holds

Anthropic's model checked this study after it was published and reran its program.

- **Four of the nine control samples were not samples.** They were rows of a spreadsheet giving the percentage scatter of repeat measurements on reference rocks. The control is five real samples from Mexican sections of the Chicxulub boundary, and none from the crater core. With the error fixed the control still passes, by one sample on one of its two measures, and the count of Younger Dryas samples that lean towards the impact pattern goes from 2 of 27 to 4.
- **"Zero of 27 look like a meteorite" means little.** A sediment with a small meteoritic share never gets that label in this test; from about 50 parts per trillion of added iridium it reads as "nearest the impact pattern". Four samples do, all at Hall's Cave: two from the boundary and one each from 13,300 and 11,000 years ago.
- **One of the two tests does not go against a cosmic source.** At Hall's Cave a meteoritic mixture fits better than the volcanic one in 11 of 16 samples.
- **What holds:** the largest excursions in platinum, iridium and osmium at Hall's Cave are not at the boundary, and Page-Ladson shows no platinum or iridium peak at all.
- **Weaker than first written:** the hundredfold spread of platinum-to-iridium ratios between sites compares sediment, ice and single nanoparticles; and "93% of spikes outside the boundary" used a window that missed Hall's Cave's own boundary samples by eight years. The fairer figure is 65% to 71%.

The full list is in the study's `RESULTS.md`, and the checking scripts are in `questions/yd-platinum-fingerprint/spotcheck/`.

## What we tested and found

After nine earlier tests in this lab—on Greenland fire chemicals, global charcoal, cooling shape, platinum timing, Tunguska, the Taurid comet stream, megafauna timing and human dates—the platinum anomalies around `~12,800` years ago remained the strongest physical clue still standing for something arriving from space.

A real meteorite or comet impact does not drop platinum by itself. It delivers the whole family of six **highly siderophile elements** (`Os, Ir, Ru, Pt, Pd, Re`) together in nearly flat cosmic proportions, alongside mantle-like unradiogenic osmium (`¹⁸⁷Os/¹⁸⁸Os ≈ 0.126`) and very low `Pt/Ir` (`~1–4`) and `Re/Os` (`~0.08`). Volcanic gas plumes and wetland chemistry behave differently: hot chlorine- and sulphur-rich volcanic vapours carry volatile `Re`, `Os` and `Pt` far more readily than refractory `Ir` and `Ru`, stretching `Pt/Ir` from `10` to over `1,000` and pushing `Re/Os` orders of magnitude above meteorites.

With every formula, control gate and decision threshold locked before opening any geochemical table, we ran two tests:

1. **Multi-element geochemical fingerprinting:** Benchmarking complete 6-element + `¹⁸⁷Os/¹⁸⁸Os` profiles from **Hall's Cave, Texas** (Sun et al. 2020) and **Page-Ladson, Florida** (Nana Yobo et al. 2026) directly against **confirmed Chicxulub K–Pg impact layers** (`n = 5`, Mexican sections), **CI chondrites**, **low-Ir iron meteorites**, **volcanic gas condensates** (Kudryavy and Tolbachik; Tonga submarine condensates for the platinum-to-iridium ratio), **Laacher See Tephra** (Green et al. 2025) and **upper continental crust**.
2. **Blind stratigraphic peak-uniqueness audit:** Scanning continuous cores from Hall's Cave, Page-Ladson and proponent **White Pond, South Carolina** (Moore et al. 2019) with a fixed statistical peak finder **without telling the detector where the Younger Dryas boundary sits**.

{{figure: yd-platinum-fingerprint/verdict}}

## Pillar 1A: Chicxulub passes; Younger Dryas sites mostly do not

First, the positive control. Across `5` confirmed Chicxulub K–Pg impact samples from Mexican boundary sections, **`4` of `5`** classify closer to pure CI chondrite than to volcanic gas or continental crust on the six-element pattern (the bar was three in four), and **`5` of `5`** beat volcanic condensates in two-component mixing (`ΔRMSE < 0`), with tight `Pt/Ir` (median `1.72`, interquartile range `0.13 dex`).

Applied to the `27` complete 6-element target samples across Hall's Cave and Page-Ladson, the picture is different:

- **Most samples are not near the impact pattern.** **`23 of 27` (`85%`)** classify as either **upper continental crust (`12`)** or **volcanic gas condensate (`11`)**; `4` fall nearest to K–Pg, all at Hall's Cave.
- **Page-Ladson, Florida (`11/11` volcanic):** Every complete sample in the YDB zone (`847–860 cm`) classifies as `volcanic` (`Pt/Ir = 30–58`, `Re/Os = 61–1,679`), as does the YDB-base unradiogenic aliquot `36-30` (`851 cm`, `¹⁸⁷Os/¹⁸⁸Os = 0.51`, `Ru` below detection) on a 5-element check (`distance 1.46` to volcanic vs. `4.10` to chondrite). Its sharpest unradiogenic spike (`36-39`, `860 cm`, `¹⁸⁷Os/¹⁸⁸Os = 0.40`) beats cosmic mixing by `ΔRMSE = +0.401`. Neither platinum (`138–567 ppt`) nor iridium (`4.6–13.7 ppt`, half of crustal average) shows any cosmic anomaly.
- **Hall's Cave, Texas (why the locked verdict is `ambiguous_or_mixed`):** At the YDB onset (`155 cm`, `13.008 ka`), the strongest unradiogenic layer (`HC16_03`, `¹⁸⁷Os/¹⁸⁸Os = 0.15`, `Os = 830 ppt`) shows **no platinum spike (`125 ppt`, `4×` below average crust)** and **no iridium spike (`23 ppt`, right at crust)**, and volcanic mixing beats both chondrite and low-Ir iron meteorite (`ΔRMSE = +0.114`). Yet two *non-YDB* unradiogenic horizons in Hall's Cave (`13.31 ka` and `10.99 ka`) carry modest iridium (`72–94 ppt`) without Kudryavy's extreme rhenium (`84,640 ppt`), giving large mixing errors for **both** chondrites (`0.60–0.72`) and Kudryavy gas (`0.82–0.88`). Pooled across all `27` targets, `median ΔRMSE = 0.000` (`p = 0.14`)—honestly keeping the formal verdict at `ambiguous_or_mixed` rather than declaring Kudryavy volcanic gas a universal fit.

{{figure: yd-platinum-fingerprint/fingerprint}}

## Pillar 1B: A hundredfold scatter across continents

A single comet or asteroid scattering ejecta across continents should leave a recognizable platinum-to-iridium ratio. The five Chicxulub K–Pg samples lie between `1.1` and `3.2` (`0.48` orders of magnitude, median `1.72`). Claimed Younger Dryas sites scatter across **two orders of magnitude (`100×`, `2.00 dex`)**, with a median of **`26.2`**, fifteen times higher than Chicxulub. The comparison is rough: it sets bulk sediment beside ice and, at Wonderkrater, ratios measured on single nanoparticles, and the range quoted for the Greenland ice could not be found in the source cited.

- **Wonderkrater, South Africa** (Thackeray et al. 2026): YDB `Pt/Ir = 3.58`—but non-YDB background in the same peat is already `2.91` (only `1.23×` enrichment).
- **Hall's Cave, Texas** (Sun et al. 2020): YDB median `Pt/Ir = 8.53` (individual samples span `2.7` to `55.8`).
- **Page-Ladson, Florida** (Nana Yobo et al. 2026): YDB median `Pt/Ir = 43.9` (`30.0` to `58.1`).
- **GISP2 Greenland ice core** (Petaev et al. 2013): `Pt/Ir = 100` to `1,264` (midpoint `356`), matching submarine volcanic sulfur condensates (`~1,194` at Niuatahi-Motutahi, Tonga) rather than meteorites or proximal Laacher See pumice (which Green et al. 2025 confirm is platinum-poor, `≤ 0.4 ppb`).

{{figure: yd-platinum-fingerprint/coherence}}

## Pillar 2: Blind scans find most spikes away from the boundary

When the peak detector scans continuous columns with zero knowledge of where the Younger Dryas begins:

- **Hall's Cave, Texas:** The **highest platinum in the entire core (`965.6 ppt`) lies at `11.54 ka`**—`1,350` years *after* the Younger Dryas began. The **highest iridium (`93.7 ppt`) lies at `13.31 ka`**—`420` years *before*. Four separate unradiogenic osmium drops recur across `2,400` years (`13.31`, `13.24`, `13.01`, and `10.90–10.99 ka`).
- **Page-Ladson, Florida:** Zero blind peaks appear in platinum, osmium, or iridium; the largest osmium isotope drop (`0.40`) lies `9 cm` *below* the YDB (`860 cm`), ahead of a smaller drop (`0.51`) at the boundary (`851 cm`).
- **Pooled across all `8` independent full-HSE series:** **`13 of 14` (`92.9%`)** blind excursions fall outside the locked `13.0–12.6 ka` / `848–855 cm` window (`0/8` global maxima inside, `p = 1.0`). Widening Hall's Cave by 8 years to `13.1–12.6 ka` (to include the `13.008 ka` cluster) still leaves **`10 of 14` (`71.4%`)** blind excursions outside (`2/8` global maxima inside, `p = 0.601`).
- **Proponent White Pond, South Carolina (Moore et al. 2019):** Blind scanning confirms a sharp, unique **`Pt/Pd` spike (`4.67`, `z = 15.3`) at `221 cm`** (Moore's YDB horizon). Yet **bulk platinum alone is not unique**: a second blind `Pt` peak of **`3.8 ppb` (`z = 4.1`)**—`90%` as large—occurs `15 cm` higher in younger peat at `206 cm`, showing how organic/redox shifts can elevate platinum inside the same lake core.

{{figure: yd-platinum-fingerprint/profiles}}

## What this does—and does not—settle

Taken with `#76`, which placed Greenland's platinum layer `20–30` years after the cooling began, these tests weaken platinum-group chemistry as evidence for one great fall of cosmic material at the boundary: most samples look like crust or rhenium-rich mud, and the continuous records show spikes as large or larger centuries before and after. They do not show that nothing cosmic arrived. A small meteoritic share would not be labelled as such by this test, four samples do lean towards the impact pattern, and at Hall's Cave a meteoritic mixture fits most samples slightly better than the volcanic gas it was compared with. White Pond's sharp spike in platinum against palladium is at the boundary and remains unexplained. Whether the Chicxulub layer, left by an asteroid ten kilometres across, is the right yardstick for comet fragments bursting in the air is also open.

::: details Methods, data, and amendments
- **Protocol and lock:** `questions/yd-platinum-fingerprint/protocol.md`, locked at `2026-11-24T04:35:27Z` (`protocol.lock`, SHA-256 `c9ec33ecd9ad`) before viewing any geochemical numbers or peak counts.
- **Amendment 2 (24 November 2026, after a spot check):** the control parser had counted four `RSD%` rows of the source spreadsheet as Chicxulub samples. Fixed, and the whole program rerun; the first run's outputs are kept in `results/first_run/`.
- **Amendment 1 (logged in `amendments.md`):** Fixed the regex in `parse_moore2019_white_pond()` for leading relative-depth intervals (`+44 to +46 165 ...`) while keeping the locked `15%` `Pt/Pd` OCR QA gate; documented the OCR QA exclusion of Moore et al.'s (2017) compressed 21-column raster tables; and added side-by-side sensitivity outputs for Hall's Cave's `13.1–12.6 ka` window and Page-Ladson's `Ru = bdl` sample `36-30`. Zero primary locked rules or thresholds were altered.
- **Primary public datasets:** Sun et al. (2020) *Science Advances* `eaax8587` (`sun2020_sm.pdf` Tables S1–S4), Nana Yobo et al. (2026) *Science Advances* `eaec9030` (`nanayobo2026_sm.pdf` Table S2), Chicxulub K–Pg HSE compilation *Nature Communications* 2025 `10.1038/s41467-025-58112-x` (`kpg2025_MOESM4.xlsx`), Green et al. (2025) *PLOS ONE* `10.1371/journal.pone.0331811` (`green2025_s001.docx` Table 3), Moore et al. (2019) *Scientific Reports* 9:15121 (`moore2019_s1.pdf` Table 3), Thackeray et al. (2026) *F1000Research* 15:1089 (`wonderkrater2026.html` Table 1), Park et al. (2016) *GCA* 174 (Tonga submarine condensates), and Wasson & Kallemeyn (1988) / Horan et al. (2003) CI chondrite. Full URLs and SHA-256 checksums in `questions/yd-platinum-fingerprint/MANIFEST.md`.
- **Full report and code:** `questions/yd-platinum-fingerprint/RESULTS.md`, `questions/yd-platinum-fingerprint/analysis/pt_fingerprint.py`, and `questions/yd-platinum-fingerprint/analysis/test_pt_fingerprint.py` (5/5 tests passing).
:::
