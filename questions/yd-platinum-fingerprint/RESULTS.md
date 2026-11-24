# Results — Do Younger Dryas platinum and HSE anomalies fingerprint a comet—or volcanic/crustal sources?

- **Question:** Issue `#120` (`yd-platinum-fingerprint`)
- **Lane:** `data`
- **Authorship & provenance:** Designed, executed, and written by **Antigravity (Google DeepMind)** under Eugene's direction, on **2026-11-24 (UTC)**. Protocol locked at `2026-11-24T04:35:27Z` (`protocol.lock`, SHA-256 `c9ec33ecd9ad`) before inspecting any geochemical sample values, ratios, or blind peak counts. One post-lock technical amendment (`amendments.md`, Amendment 1) fixed the White Pond OCR regex, documented the OCR QA exclusion of Moore et al. (2017) compressed multi-column tables, and added side-by-side sensitivity checks without changing any primary locked metric or decision rule. Open to second-vendor replication.

---

## The short answer

**Younger Dryas platinum and highly siderophile element (HSE) layers fail every pre-registered test for a cosmic impactor—yet they do not fit a single simple volcanic gas condensate everywhere either.**

- **Formal pre-registered verdict:** **`ambiguous_or_mixed`** (not cosmic, and not a uniform match to Kudryavy-style volcanic gas condensates across all sites).
- **Against a cosmic impactor (clear and consistent across all four checks):**
  1. **Positive control passed:** Confirmed Chicxulub K–Pg asteroid-impact layers (`n = 9`, IODP M0077 crater core & Mexican boundary sections, `kpg2025_MOESM4.xlsx`) pass our classifier at **`88.9%` (`8/9`)** on pure CI-chondrite centered log-ratio (CLR) pattern and **`100.0%` (`9/9`)** on two-component mixing (`ΔRMSE < 0`), with tight **`median Pt/Ir = 1.29`** (`IQR = 0.24 dex`, full span `0.83 dex`).
  2. **Zero chondritic matches at Younger Dryas sites:** Across **`27` complete 6-HSE target samples** (`Os, Ir, Ru, Pt, Pd, Re`) spanning the YDB window and unradiogenic-Os excursions at **Hall's Cave, Texas** (Sun et al. 2020) and **Page-Ladson, Florida** (Nana Yobo et al. 2026), **`0 of 27` (`0.0%`)** classify as chondritic and **`25 of 27` (`92.6%`)** classify as **upper continental crust (`14`) or volcanic gas condensate (`11`)** (`2/27` nearest K–Pg).
  3. **Cross-site `Pt/Ir` scatters by `100×` (`2.00 dex`) — incompatible with one impactor:** Claimed YDB `Pt/Ir` ratios range from **`3.58`** at Wonderkrater, South Africa (where non-YDB background is already `2.91`, only `1.23×` enrichment) to **`8.53`** (range `2.7–55.8`) at Hall's Cave, **`43.9`** (`30–58`) at Page-Ladson, and **`100–1,264`** (geometric midpoint `356`) in Greenland GISP2 ice (Petaev et al. 2013). The cross-site median **`26.2`** sits **`20×` higher than Chicxulub K–Pg** and **`12×` higher than CI chondrite (`2.15`)**, overlapping continental crust (`23.2`) and fractionated volcanic condensates (Kudryavy `10.9`, Tonga submarine condensates `~1,194`).
  4. **Blind stratigraphic peaks are not unique to the YDB:** Scanning the `8` continuous full-HSE / Os-isotope series in Hall's Cave and Page-Ladson without author boundary labels flags **`13 of 14` (`92.9%`)** excursions **outside** the locked `13.0–12.6 ka` / `848–855 cm` window (`0/8` global extremes inside, exact permutation `p = 1.0`). Even widening Hall's Cave by 8 years to `13.1–12.6 ka` (Amendment 1 sensitivity) leaves **`10 of 14` (`71.4%`)** blind excursions outside (`2/8` global extremes inside, `p = 0.601`). Hall's Cave's **highest platinum (`965.6 ppt`) lies `1,350` years after YD onset (`11.54 ka`)**, its **highest iridium (`93.7 ppt`) lies `420` years before (`13.31 ka`)**, and Page-Ladson shows **zero** blind Pt or Ir spikes anywhere in its core.
- **Why the locked verdict is `ambiguous_or_mixed` rather than a blanket volcanic win:**
  - At **Page-Ladson, FL**, volcanic aerosol/condensate geochemistry wins decisively: **`11/11` (`100%`)** complete target samples—plus the `Ru = bdl` YDB-base unradiogenic aliquot `36-30` (`851 cm`, `¹⁸⁷Os/¹⁸⁸Os = 0.51`) on 5-HSE CLR—classify as `volcanic`, and its deep unradiogenic spike `36-39` (`860 cm`, `¹⁸⁷Os/¹⁸⁸Os = 0.40`) beats cosmic mixing by **`ΔRMSE = +0.401`** (`r_volc = 0.257` vs. `r_CI = 0.658`).
  - At **Hall's Cave, TX**, the YDB-onset unradiogenic spike `HC16_03` (`155 cm`, `13.008 ka`, `¹⁸⁷Os/¹⁸⁸Os = 0.15`, `Os = 829.7 ppt`, `Pt = 124.7 ppt`, `Ir = 22.7 ppt`, `Ru = 5.1 ppt`) also favors volcanic mixing over both CI chondrite and low-Ir iron meteorite (`ΔRMSE = +0.114`: `r_volc = 0.862`, `r_CI = 0.976`, `r_iron = 1.627`). **However**, across all `27` target samples pooled, `median ΔRMSE = 0.000` (95% bootstrap CI `[-0.054, +0.000]`, Wilcoxon `p = 0.140`), because (i) radiogenic samples inside `13.1–12.6 ka` sit at `f = 0` (`ΔRMSE = 0`), and (ii) two **non-YDB** unradiogenic horizons in Hall's Cave (`13.31 ka` `HC15_06`, `10.99 ka` `HC15_13`) carry modest `Ir` (`71.5–93.7 ppt`) without the extreme `Re` enrichment of Kudryavy fumarole gas (`84,640 ppt`), yielding large mixing misfits for *both* chondrites (`0.60–0.72`) and Kudryavy gas (`0.82–0.88`).
  - Finally, in the proponent continuous lake core at **White Pond, South Carolina** (Moore et al. 2019, `n = 30` QA-verified depths), blind scanning confirms a sharp, unique **`Pt/Pd` peak (`4.67`, `z = 15.3`) at `221 cm`** (Moore's YDB horizon), even though **bulk `Pt` is not unique** (`4.2 ppb` at `221 cm` vs. a nearly equal `3.8 ppb` peak 15 cm higher in peat at `206 cm`). Without `Ir`, `Os`, `Ru`, `Re`, or `¹⁸⁷Os/¹⁸⁸Os`, a single `Pt/Pd = 4.7` ratio cannot distinguish cosmic dust from volcanic fallout or peat-mud redox fractionation.

---

## 1. Positive control: real Chicxulub K–Pg impact layers (`kpg2025_MOESM4.xlsx`)

To prove our locked classifier recognizes a real extraterrestrial impact diluted into Earth sediments, we tested all `9` confirmed K–Pg boundary / impact-clay samples with complete 6-HSE measurements and `Ir ≥ 0.5 ppb` across IODP Site M0077 (Chicxulub crater) and Mexican K–Pg sections (Bochil and Gulf of Mexico profiles, *Nature Communications* 2025 `10.1038/s41467-025-58112-x`):

| Metric | Confirmed Chicxulub K–Pg (`n = 9`) | Pre-registered pass bar | Status |
|---|---|---|---|
| Pure CI-chondrite beats volcanic & UCC on 6-HSE CLR | **`88.9%` (`8 / 9`)** | `≥ 75%` | **PASS** |
| Cosmic mixing beats volcanic condensates (`ΔRMSE < 0`) | **`100.0%` (`9 / 9`)** | `≥ 75%` | **PASS** |
| Median `Pt/Ir` | **`1.29`** (CI chondrite `2.15`) | `0.5–6.0` | Tight cosmic |
| Cross-sample `log10(Pt/Ir)` IQR / full span | **`0.24 dex` / `0.83 dex`** | `< 0.5 / < 1.2 dex` | Coherent |

The classifier works: real impact layers stand out sharply from both continental crust and volcanic gas condensates.

---

## 2. Pillar 1A: Full 6-HSE fingerprinting (`Hall's Cave` & `Page-Ladson`)

| Subset | `n` | CLR class counts (`chondrite` / `kpg` / `volcanic` / `ucc`) | Non-cosmic CLR (`volc + ucc`) | Median `ΔRMSE` (`[95% CI]`, Wilcoxon `p`) | Median `Pt/Ir` | Median `Os/Ir` | Median `Re/Os` |
|---|---:|---|---:|---|---:|---:|---:|
| **All targets (YDB window or unradiogenic Os)** | `27` | `0 / 2 / 11 / 14` | **`92.6%`** | `0.000` (`[-0.054, +0.000]`, `p = 0.140`) | `30.0` | `7.13` | `12.39` |
| Strict YDB window (`13.1–12.6 ka` / `847–860 cm`) | `18` | `0 / 1 / 11 / 6` | **`94.4%`** | `0.000` (`[0.000, +0.003]`, `p = 0.340`) | `36.9` | `44.9` | `240.8` |
| Unradiogenic-Os excursions only (`¹⁸⁷Os/¹⁸⁸Os < med − 0.15`) | `12` | `0 / 2 / 1 / 9` | **`83.3%`** | `-0.098` (`[-0.149, +0.034]`, `p = 0.233`) | `14.9` | `5.53` | `4.47` |
| **Reference: CI Chondrite** | — | `chondrite` | — | — | `2.15` | `1.07` | `0.076` |
| **Reference: Kudryavy Volcanic Gas** | — | `volcanic` | — | — | `10.9` | `36.6` | `144.4` |
| **Reference: Upper Continental Crust** | — | `ucc` | — | — | `23.2` | `1.41` | `6.39` |

Key site-level findings:
- **Hall's Cave, TX (Sun et al. 2020, `n = 29` levels, `13.31–10.52 ka`):**
  - At the YDB onset (`151–155 cm`, `13.008 ka`), `4` of `6` aliquots are completely normal radiogenic crust (`¹⁸⁷Os/¹⁸⁸Os = 1.94–2.22`, `Os = 22.6–29.5 ppt`). The strongest unradiogenic aliquot `HC16_03` (`155 cm`, `¹⁸⁷Os/¹⁸⁸Os = 0.15`, `Os = 829.7 ppt`) has **no platinum spike (`124.7 ppt`, `4×` below UCC!)**, **no iridium spike (`22.7 ppt`, right at UCC!)**, and **depleted ruthenium (`5.1 ppt`)**; volcanic mixing beats both CI chondrite and iron meteorite (`ΔRMSE = +0.114`), though neither simple end-member achieves low RMSE (`r_volc = 0.862`, `r_CI = 0.976`, `r_iron = 1.627`).
  - Two **non-YDB** unradiogenic horizons—`HC15_06` (`13.314 ka`, `420 yr` before YD onset: `¹⁸⁷Os/¹⁸⁸Os = 0.16`, `Os = 643 ppt`, `Ir = 93.7 ppt`, `Pt = 139 ppt`) and `HC15_13` (`10.990 ka`, `1,900 yr` after YD onset: `¹⁸⁷Os/¹⁸⁸Os = 0.23`, `Os = 510 ppt`, `Ir = 71.5 ppt`, `Pt = 103 ppt`)—still lack Pt/Ru spikes, yet their low crustal `Re` (`356–379 ppt`) makes high-`Re` Kudryavy gas fit even worse than CI chondrite (`ΔRMSE = -0.155` and `-0.222`). This demonstrates why a simple binary "chondrite vs. Kudryavy" model is incomplete for Hall's Cave's episodic cave-sediment Os/Ir excursions.
- **Page-Ladson, FL (Nana Yobo et al. 2026, `n = 30` aliquots, `839–866 cm`):**
  - **Every complete sample (`22/22`, including `11/11` in `847–860 cm`) classifies as `volcanic` on 6-HSE CLR**, with crustal-to-low `Pt` (`138–567 ppt`), sub-crustal `Ir` (`4.6–13.7 ppt`), high `Pt/Ir` (`30–58`), and massive `Re` (`43,000–598,000 ppt`, `Re/Os = 61–1,679`).
  - Duplicate aliquots at both the YDB base (`851 cm`, `36-30`: `¹⁸⁷Os/¹⁸⁸Os = 0.51` vs. `0.75`) and `9 cm` deeper (`860 cm`, `36-39`: `0.40` vs. `0.73`) show strong micro-scale heterogeneity. On 5-HSE CLR (Amendment 1 sensitivity, dropping `Ru = bdl`), the YDB-base unradiogenic aliquot `36-30` (`¹⁸⁷Os/¹⁸⁸Os = 0.51`, `Pt/Ir = 47.8`, `Re/Os = 255`) classifies solidly as **`volcanic`** (`d_volc = 1.46` vs. `d_ucc = 2.99`, `d_kpg = 3.61`, `d_chondrite = 4.10`).

---

## 3. Pillar 1B: Cross-site coherence & volcanic tephra controls

- **Cross-site `Pt/Ir` scatter (`4` published YDB datasets across `3` continents):**
  - Wonderkrater, South Africa (Thackeray et al. 2026, HTML Table 1): YDB `Pt/Ir = 3.58` vs. Non-YDB `2.91` (only `1.23×` enrichment; `Au/Ir = 3.80` vs. `1.77`, `Pd/Ir = 16.6` vs. `9.68`).
  - Hall's Cave, TX (Sun et al. 2020): YDB median `Pt/Ir = 8.53` (range `2.70–55.78`).
  - Page-Ladson, FL (Nana Yobo et al. 2026): YDB median `Pt/Ir = 43.87` (range `30.0–58.1`).
  - GISP2 Greenland ice peak (Petaev et al. 2013): `Pt/Ir = 100–1,264` (geometric midpoint `355.5`).
  - **Result:** YDB sites span **`2.00` orders of magnitude (`100×`)** with median **`26.2`** (`20×` above Chicxulub K–Pg `1.29` and `2.4×` wider than K–Pg's `0.83 dex` span), contradicting a single uniform cosmic impactor.
- **Laacher See Tephra check (Green et al. 2025, `green2025_s001.docx` Table 3, `n = 18`):** Confirms Green et al.'s finding that proximal Laacher See pumice/tephra is Pt-poor (`12/17` tephra samples below the `0.1 ppb` detection limit; max tephra `Pt = 0.4 ppb`; `16/17` below `0.1 ppb` Ir; only modern roadside topsoil `LST1 TS` reaches `0.9 ppb` Pt). Whatever produced GISP2's `Pt/Ir ~ 100–1,264` ice spike was not ordinary silicic tephra, but a strongly gas-fractionated source such as submarine/subglacial volcanic condensates (e.g., Niuatahi-Motutahi Tonga, Park et al. 2016: `Pt/Ir ≈ 1,194`).

---

## 4. Pillar 2: Blind stratigraphic peak-uniqueness audit

| Archive & Tier | Series scanned | Blind excursions **inside** YDB | Blind excursions **outside** YDB | `% outside` | Global extremes inside YDB | Exact permutation `p` |
|---|---:|---:|---:|---:|---:|---:|
| **Independent full-HSE (locked `13.0–12.6 ka` / `848–855 cm`)** | `8` (`Pt, Os, Ir, ¹⁸⁷Os/¹⁸⁸Os` × 2 cores) | **`1`** | **`13`** | **`92.9%`** | `0 / 8` | `1.000` |
| **Independent full-HSE (Amendment 1 sensitivity `13.1–12.6 ka` at Hall's Cave)** | `8` | **`4`** | **`10`** | **`71.4%`** | `2 / 8` | `0.601` |
| **Proponent White Pond, SC (Moore et al. 2019, `n = 30` QA-verified depths)** | `2` (`Pt`, `Pt/Pd`) | `0` (in `222–232 cm`; `2` if `220–230 cm` includes `221 cm`) | `2` (`Pt` at `206` & `221 cm`); `1` (`Pt/Pd` at `221 cm`) | — | `221 cm` (`Pt = 4.2`, `Pt/Pd = 4.67`) | — |

Key stratigraphic takeaways:
1. **Hall's Cave, TX:** Blind scanning finds **four separate unradiogenic `¹⁸⁷Os/¹⁸⁸Os` drops** across 2,400 years (`13.31 ka`, `13.24 ka`, `13.01 ka`, and `10.90–10.99 ka`), **two blind `Pt` peaks** (`11.54 ka` at `965.6 ppt` — the core maximum — and `13.01 ka` radiogenic `HC17_01` at `435.1 ppt` with `¹⁸⁷Os/¹⁸⁸Os = 2.02`!), and **two blind `Ir` peaks** (`13.31 ka` at `93.7 ppt` — the core maximum — and `10.99 ka` at `71.5 ppt`, neither at the YDB!).
2. **Page-Ladson, FL:** Blind scanning finds **zero** `Pt`, `Os`, or `Ir` peaks anywhere in the 30-aliquot section (`839–866 cm`). Two unradiogenic `¹⁸⁷Os/¹⁸⁸Os` drops appear: `0.51` at `851 cm` (YDB base) and a larger drop `0.40` at `860 cm` (`9 cm` *below* the YDB).
3. **White Pond, SC (proponent core):** Blind scanning confirms Moore et al.'s sharp `Pt/Pd` spike at `221 cm` (`4.67`, `z = 15.3`, the sole blind `Pt/Pd` peak in the core). However, **bulk `Pt` is not unique to `221 cm`**: a second blind `Pt` peak of **`3.8 ppb` (`z = 4.1`)** occurs `15 cm` higher at `206 cm` (`+4 to +6 cm` into Holocene/YD peat, alongside `Pd = 8.6 ppb`), showing that sediment/organic redox shifts produce comparable platinum concentrations inside the same core.

---

## 5. Amendments & limitations

- **Amendment 1 (logged in `amendments.md` prior to re-running):** Fixed the White Pond Table 3 regex for leading relative-depth intervals (`+44 to +46 165 ...`), documented the OCR QA exclusion of Moore et al.'s (2017) 21-column rasterized tables where `tesseract-ocr` drops decimal points, and added side-by-side sensitivity outputs for Hall's Cave's `13.1–12.6 ka` window and Page-Ladson's `Ru = bdl` YDB sample `36-30`. None of these altered the locked primary metrics or formal verdict.
- **What public data still cannot settle:** Full 6-HSE + `¹⁸⁷Os/¹⁸⁸Os` measurements across continuous multi-millennial sections exist at only two open-access YDB sites (Hall's Cave and Page-Ladson), and Greenland GISP2 platinum has still never been measured continuously across earlier ice-age coolings or paired with `Os/Ru/Pd/Re` and `¹⁸⁷Os/¹⁸⁸Os` in the same ice samples.

---

## What this means

When a real asteroid hits Earth—like the Chicxulub impact that ended the dinosaurs—it leaves an unmistakable chemical fingerprint: platinum, iridium, osmium, and ruthenium rise together in tight meteorite proportions across distant sites, and our locked test picks up that signature nine times out of nine. Younger Dryas sediments do not pass that test. None of the 27 full-suite samples from Hall's Cave or Page-Ladson looks like a meteorite; platinum-to-iridium ratios scatter by a factor of a hundred across claimed impact sites on three continents; and when you scan the best continuous cores blindly without knowing where the Younger Dryas begins, seven to nine out of every ten chemical spikes land at the wrong depths—including higher platinum 1,350 years later and higher iridium 420 years earlier. At the same time, the test stays honest about the alternative: Page-Ladson matches volcanic aerosols cleanly, whereas Hall's Cave's episodic osmium drops do not fit high-rhenium volcanic gas condensates either, and South Carolina's White Pond really does carry a sharp platinum-to-palladium spike whose source remains untested without iridium or osmium isotopes. The platinum evidence no longer looks like the calling card of a single comet, even though local volcanic and wetland-chemistry explanations still have loose ends to tie up.
