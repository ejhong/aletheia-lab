---
# To update this page, edit this file and push to main; the site rebuilds itself.
# The figures are made by questions/yd-retracted-plos-audit/analysis/make_figures.py from the results files.
summary: On 11 February 2026, PLOS One retracted two 2025 Younger Dryas papers by the Comet Research Group—one on Baffin Bay ocean cores and one on shocked quartz at three US sites. Because all underlying spreadsheets and Supporting Information PDFs remain openly archived, we audited every data-verifiable claim in both retraction notices and the authors' defense.
verdict: Split verdict—Baffin Bay retraction strongly supported by raw data; Shocked Quartz retraction mixed/harsh
result: On the Baffin Bay ocean-core paper (e0328347), four of five pre-registered checks support retraction: its SI Table S1 Younger Dryas ages resulted from a flipped ΔR sign in Cores 64, 67, and 77 (reproducing all 17 ages to ±1 yr) and terrestrial IntCal20 in Core 52 (+297 to +769 yr too old; on correct Marine20 + deglacial ΔR, all four cores shift off 12.8 ka), SI Figs S30–S34 are visibly porous Ca+C+O marine foraminifera (92.5–96.5 wt%) from a 9.5 ka Holocene layer, Core 64's out-of-YDB peak exceeds Core 67's YDB peak (680 vs. 640 CDPs/kg), and the ×100 Ni/Cr formula pushes 100% pure Earth crust into the comet field. On the Shocked Quartz paper (e0319840), both dating and control-sampling critiques hold (the headline χ² = 0.057 used a date 18.5 cm above Arlington Canyon's quartz; all 25 published direct dates give T = 90.9, p < 10⁻⁹; only 13 of 66 strata were checked, with zero below the boundary at Arlington Canyon), yet the retraction notice never challenged the electron-microscopy quartz images themselves.
dek: Testing PLOS One's two February 2026 Younger Dryas retractions—and the authors' objections—directly against the archived spreadsheets, radiocarbon dates, and SEM plates.
updated: 2026-11-24
---

> **Where things stand, 24 November 2026.** Initial locked run finished with one pure parser/transcription amendment (by Antigravity / Google DeepMind, directed by Eugene; open to second-vendor replication). Pre-registered verdicts: **Baffin Bay (`e0328347`) — Retraction strongly supported (`4/5` checks verified)**; **Shocked Quartz (`e0319840`) — Mixed / harsh (`chronology & controls fail`, `microscopy unchallenged by notice`)**.

{{figure: yd-retracted-plos-audit/tiles}}

## Why audit two retractions directly?

On 11 February 2026, *PLOS One* retracted two high-profile 2025 papers by the Comet Research Group: **Moore et al. (2025, `e0328347`)** claiming cometary dust, microspherules, and platinum nanoparticles in four Baffin Bay ocean cores, and **Kennett et al. (2025, `e0319840`)** claiming glass-filled shocked quartz at Arlington Canyon (CA), Blackwater Draw (NM), and Murray Springs (AZ). The authors publicly objected, arguing the criticisms were procedural rather than scientific and should have been handled through corrections.

Because every underlying Excel workbook (`Zenodo 14681287`), the `227`-page Baffin Bay Supporting Information PDF (`Zenodo 15330698`), and the `22`-page Shocked Quartz Supporting Information PDF (`pone.0319840.s001.pdf`) remain openly downloadable, we locked a four-pillar audit before examining the data—testing both *PLOS One*'s editorial claims and the authors' defense fairly.

## Paper A: Baffin Bay ocean cores (`e0328347` → strongly supported)

### 1. A `+297` to `+769`-year radiocarbon calibration bug—before any polar sea-ice shift

Recalibrating all 27 raw marine `¹⁴C` dates from `SI Table S1` on official **`Marine20`** uncovered an exact mathematical error behind *PLOS One*'s chronology critique:

- In **Cores 64, 67, and 77** (`17` dates), Moore et al. **flipped the sign of `ΔR`** in OxCal—calibrating with `−218` and `−103` instead of `+218` and `+103`. Recomputing `Marine20` with `−ΔR` reproduces all 17 published `SI Table S1` means to **`±1 year`**, proving the published ages were artificially inflated by **`+414 to +590 yr`** in Cores 64 & 67 and **`+250 to +327 yr`** in Core 77.
- In **Core 52** (`10` dates), marine foraminifera were accidentally calibrated on the **terrestrial `IntCal20` curve** (omitting the ~500–600 yr global marine reservoir, plus a flipped `−71` offset), inflating Core 52's claimed YDB (`625–630 cm`, `11,120 ± 40`) by **`+608 years`** (`12,992` vs. `12,384` mean / `12,404` median cal BP).

Use the buttons below to step from Pearce et al.'s (2023) modern Holocene `ΔR` (`S0`) to plausible high-latitude deglacial sea-ice offsets (`S1–S3`):

{{figure: yd-retracted-plos-audit/baffin_14c_sensitivity}}

Even under Holocene `ΔR` (`S0`), **Core 52 (`12,404 cal BP`)** and **Core 77 (`11,889 cal BP`)** already miss the Younger Dryas onset (`12,900–12,700 cal BP`, `P ≤ 0.001`). Under a moderate `+500 yr` polar deglacial offset (`S2`), **all four cores** have `P(YDB onset) = 0.000`; under `+800 yr` (`S3`), **all four fall younger than the entire Younger Dryas (`< 11,700 cal BP`)**. The cores also contain **four major stratigraphic age inversions** (including `2,860 ¹⁴C yr` directly above Core 64's YDB and `640 ¹⁴C yr` above Core 52's YDB).

*(Fairness note: *PLOS One* stated foraminifera type and specimen counts were missing. In fact, `SI Table S17` on p. 220 does report broad groups and approximate specimen counts `400–4,400` for `17` of `21` samples—though without species percentages, and showing that Cores 64 and 67 mixed benthic and planktic foraminifera in the same AMS targets.)*

### 2. Foraminifera labeled as cosmic spherules, thin sampling, and Core 64 vs. Core 67

- **`SI Figs S30–S34` (`baffin_bay_si.pdf`, pp. 32–35):** Extracting the embedded SEM-EDS images confirms *PLOS One*'s identification verbatim. All four EDS readouts are **`92.5–96.5 wt%` Ca + C + O (`0%` Fe/Ni/Cr)** on broken tests with textbook `1–2 µm` foraminiferal wall pores and radial prismatic walls—taken from Core 52 (`574–579 cm`), which `SI Table S1` itself dates to **`9,538 cal BP` (Early Holocene, 3,300 yr post-YD)**, where main-text Fig. 6(b, e–f) also drew claimed "YDB meltglass." *(Fairness note: `0/18` LA-ICP-MS spherules in `Table S8a/S8b` were high-Ca, so those foraminifera did not contaminate the LA-ICP-MS chemistry table.)*
- **Core coverage & non-uniqueness (`SI Table S6`):** Sampling covers just **`16.7%`** of the four cores (`2.1%` in Core 67, `7.2%` in Core 64). Core 64's out-of-YDB peak (`290–293 cm`: `680 CDPs/kg`) is **`1.06×`** Core 67's YDB peak (`32–35 cm`: `640 CDPs/kg`), confirming *PLOS One*'s exact comparison. In Core 77, the dated `161–162 cm` layer has `0` spherules, while the undated `167–168 cm` peak row (`0.14 g`, `10` spherules) lists `965/kg` instead of `71,429/kg`.
- **Nanoparticles (`Table S7`):** In Core 64, **`9 of 10`** nanoparticle metrics (`Pt`, `Ir`, `Pd`, `Ni`, `Co`, `Cr`, `Pt/Ir`, `Pt/Fe`, `Ni/Fe`) peak **outside** the `312–318 cm` YDB; the only one peaking inside (`Pt/Pd = 0.76`) fails Moore et al.'s own `> 1.0` extraterrestrial rule. Core 67 *does* show a local `Pt`/`Ir` peak at `30–35 cm` (`6/10` metrics), though dated centuries too young under correct `Marine20`.

### 3. The `×100` mixing math artifact (`Table S8a/S8b`) and terrestrial bulk `Δ¹⁷O*`

All **`18 of 18` (`100%`)** Baffin Bay LA-ICP-MS microspherules have raw `Fe/Ni > 200` (terrestrial crustal/oxide; median `Fe/Cr = 1,031`, `Fe/Ni = 1,556`, and `Pt/Ir = 556` vs. `2.1` in chondrites), with **`0/18`** inside the cosmic field. To argue for `1 wt%` cometary admixture, Moore et al. multiplied total measured Ni and Cr by **`100×` without first subtracting `99 wt%` terrestrial Ni and Cr**. Toggle the chart below to see what that formula does to **100% pure terrestrial Earth crust and USGS basalt `BIR-1G`**:

{{figure: yd-retracted-plos-audit/baffin_x100_math}}

Pure terrestrial crust (`0%` cosmic material) jumps from `Fe/Cr = 426, Fe/Ni = 834` straight to `4.26, 8.34`—right inside the "Comet Wild 2" box. Proper `99%` Fe-scaled crustal subtraction leaves **`0 of 18`** microspherules with `≥ 1 wt%` CI chondrite Ni and Cr excess. Meanwhile, the Open University bulk oxygen-isotope table (`Appendix Table A1`) shows **`0` extraterrestrial deviations** (claimed YDB mean `Δ¹⁷O* = −0.040‰` is closer to terrestrial zero than background `−0.063‰`).

## Paper B: Shocked quartz (`e0319840` → mixed / harsh)

Auditing Kennett et al.'s raster SI tables (`Tables S2–S8`) shows that **both** criticisms in *PLOS One*'s retraction notice are factually verified in the raw data:

{{figure: yd-retracted-plos-audit/quartz_audit}}

1. **Cherry-picked radiocarbon synchrony (`SI Tables S2–S4`):** Only `6` rows (missing all Arlington Canyon lab IDs, all Blackwater Draw uncalibrated `¹⁴C` ages, and all 8 individual Murray Springs lab IDs) were tabulated out of `25` published direct dates across those three sites. Their headline **`χ² = 0.057` (`p = 0.972`)** selected Arlington Canyon's **`482.5 cm`** date (`12,810 ± 60`), which sits **`18.5 cm` ABOVE** the `501.0 cm` shocked-quartz layer (`ARL-1B`). Swapping in their own `Table S2` `500.5 cm` date (`12,955 ± 60`) raises `χ²` **66-fold (`4.21`)**; including all `25` published direct dates rejects single-year synchrony decisively (**`T = 90.94, p < 10⁻⁹`**).
2. **Thin vertical background controls (`SI Tables S5, S6, S8`):** Only **`13 of 66` strata (`19.7%`)** were checked for shocked quartz. At Arlington Canyon, `ARL-1B` (`501 cm`, `5` grains) is the **bottom row of `Table S5`—zero strata below the YDB were checked**, and `391 cm` of overlying core (`97–488 cm`) went unchecked. Blackwater Draw checked only `1` slide above and `1` below. No control-slide grain denominators or sedimentation-rate models are reported.

**Why the verdict is mixed / harsh:** Despite those real flaws in dating and vertical controls, *PLOS One*'s retraction notice (`e0342620`) makes **zero claim** of error, fabrication, or misidentification in the actual TEM/SEM/CL/EBSD microscopy of the 16 glass-filled fractured quartz grains. Retracting the entire paper without showing error in its centerpiece microscopy observations is harsher than standard journal practice (where an Expression of Concern or Major Correction is typical), and leaves the physical origin of those 16 grains unresolved until independent mineralogists examine the slides blind.

## What this means

Checking the primary files directly separates a clear scientific breakdown from an unusually strict editorial call. **The Baffin Bay ocean-core retraction was strongly warranted:** its Younger Dryas dates rested on flipped `ΔR` signs and a terrestrial calibration curve, four "cosmic spherule" SEM figures are visibly porous calcareous foraminifera from an Early Holocene layer, Core 64's nanoparticles peak outside the claimed boundary, and its `×100` geochemistry trick turns ordinary Earth crust into comet dust. **The Shocked Quartz retraction is more nuanced:** *PLOS One* was right that the paper's synchrony test was cherry-picked and its vertical background controls were too thin (including zero strata checked beneath Arlington Canyon's quartz layer), which undercuts the headline claim of a proven 12.8 ka event—yet because the notice never challenged the quartz microscopy itself, full retraction looks harsher than a correction or Expression of Concern, and independent blind laboratory re-examination of those grains remains the only way to settle what fractured them.

::: details Methods, data, and verification
- **Protocol and lock:** `questions/yd-retracted-plos-audit/protocol.md`, locked at `2026-11-24T14:38:16Z` (`protocol.lock`, SHA-256 `98b48ef3274a`). One pure parser/transcription amendment (`amendments.md`, zero changes to `protocol.md`, thresholds, or verdict rules) for raster-screenshot PDF tables (`SI Table S1`, `kennett2025_si` `Tables S2–S8`) and header indexing.
- **Public datasets:** `Zenodo 14681287` (`Tables S7, S8a, S8b, S10, S13`), `Zenodo 15330698` (`Baffin Bay Supporting Information.pdf`), PLOS One JATS XML manuscripts & retraction notices (`e0328347`, `e0342613`, `e0319840`, `e0342620`), `pone.0319840.s001.pdf`, `marine20.14c` (Heaton et al. 2020), and `intcal20.14c` (Reimer et al. 2020). Full URLs, licences, and SHA-256 hashes in `questions/yd-retracted-plos-audit/MANIFEST.md`.
- **Full report and code:** `questions/yd-retracted-plos-audit/RESULTS.md`, `questions/yd-retracted-plos-audit/analysis/audit_plos_retractions.py`, and `questions/yd-retracted-plos-audit/analysis/test_audit_plos_retractions.py` (`5/5` synthetic verification tests passing).
:::
