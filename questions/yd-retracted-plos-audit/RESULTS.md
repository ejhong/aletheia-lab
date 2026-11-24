# Results — Did the raw data in the two retracted 2025 PLOS One Younger Dryas papers warrant retraction?

**Question:** `yd-retracted-plos-audit` (Issue `#127`, lane `data`)  
**Protocol locked:** `2026-11-24T14:38:16Z` (`protocol.lock`, SHA-256 `98b48ef3274a2d701f78295ff4918d40014fd7e391936f3ace99bd0faca5300d`)  
**Amendments:** `1` (pure parser & verbatim raster-table transcription fixes in `amendments.md`; zero changes to `protocol.md`, thresholds, or verdict rules).  
**Authorship:** Designed, coded, executed, and written by **Antigravity (Google DeepMind)** under the direction of **Eugene Jhong** on `2026-11-24`. Open to independent second-vendor replication from `protocol.md`.

---

## Short Answer

Auditing the authors' own open spreadsheets and Supporting Information PDFs produces a **split verdict** across the two papers *PLOS One* retracted on February 11, 2026:

1. **Paper A — Baffin Bay Ocean Cores (`Moore et al. 2025, e0328347` → retracted `e0342613`):** **Pre-registered verdict: `retraction_strongly_supported` (`4 of 5` major checks verified in the raw data).** Beyond *PLOS One*'s published notice, our recalibration caught an exact mathematical bug in `SI Table S1`: Moore et al. **flipped the sign of `ΔR` in OxCal** for Cores 64, 67, and 77 (reproducing all 17 published ages to `±1 yr` when `−ΔR` is used instead of `+ΔR`) and accidentally calibrated **Core 52** marine foraminifera on the **terrestrial `IntCal20` curve**, artificially inflating their published ages by **`+297 to +769 years`**. On correct `Marine20` calibration—even *before* adding high-latitude deglacial sea-ice offsets—Core 52 (`12,404 cal BP`) and Core 77 (`11,889 cal BP`) already miss the Younger Dryas onset (`12,900–12,700 cal BP`); under moderate `+500 yr` deglacial sea-ice offsets, **all four cores** have `P(YDB onset) = 0.000`, and under `+800 yr` **all four fall younger than the entire Younger Dryas (`< 11,700 cal BP`)**. Direct inspection of `SI Figs S30–S34` also confirms textbook calcareous marine foraminifera (`92.5–96.5 wt%` Ca+C+O, `0%` Fe, `1–2 µm` wall pores) labeled as cosmic spherule fragments—taken from an Early Holocene (`9.5 ka`) level. Meanwhile, `100%` (`18/18`) of LA-ICP-MS microspherules have terrestrial crustal `Fe/Ni > 200`, and the authors' `×100` Ni/Cr multiplier pushes **100% pure terrestrial Earth crust and USGS basalt `BIR-1G`** straight into the "Comet Wild 2" field.
2. **Paper B — Shocked Quartz (`Kennett et al. 2025, e0319840` → retracted `e0342620`):** **Pre-registered verdict: `retraction_mixed_or_harsh`.** Both methodological critiques in *PLOS One*'s notice are **100% verified** in the raw SI tables: (a) the authors' headline synchrony test (`χ² = 0.057, p = 0.972`) cherry-picked Arlington Canyon's `482.5 cm` date (`18.5 cm` *above* the `501 cm` shocked-quartz layer)—swapping in their own `500.5 cm` date raises `χ²` 66-fold (`4.21`), and using all `25` published direct YDB-stratum dates across those three sites shatters single-year synchrony (`T = 90.94, p < 10⁻⁹`); and (b) only **`13 of 66` strata (`19.7%`)** were analyzed for shocked quartz, with **zero strata below the YDB checked at Arlington Canyon** (`ARL-1B` is the bottom row of `Table S5`), only `1` above and `1` below at Blackwater Draw, zero tabulated control grain counts, and no sedimentation-rate model. **Yet *PLOS One*'s retraction notice raises zero challenge to the TEM/SEM/EBSD/CL quartz microscopy images themselves** (nor to the hydrocode modeling). Under standard journal practice, verified chronology and control-sampling flaws without any documented error in the primary microscopy data normally call for an Expression of Concern or Major Correction rather than outright retraction.

---

## 1. Pillar 1 — Baffin Bay Radiocarbon Audit (`Paper A`)

### 1.1 Exact Diagnosis of the `SI Table S1` Calibration Bug

Comparing Moore et al.'s 27 raw marine `¹⁴C` dates in `SI Table S1` (`baffin_bay_si.pdf`, p. 5) against exact `Marine20` and `IntCal20` calibrations reveals why *PLOS One*'s experts reported younger ages falling outside the Younger Dryas:

- **Cores 64, 67, and 77 (`17` dates):** Calibrating with **`Marine20` and the OPPOSITE sign (`−ΔR` instead of `+ΔR`)** reproduces every single published `SI Table S1` calibrated mean across all three cores to a mean difference of **`+1 year`** (median absolute error `1.5 yr`). Because `ΔR` is positive in Baffin Bay (`+218 ± 135 yr` in Zone 3, `+103 ± 106 yr` at Zone 3/2 border; Pearce et al. 2023), flipping its sign shifted every date artificially older by **`+414 to +590 yr`** in Cores 64 & 67 and **`+250 to +327 yr`** in Core 77.
- **Core 52 (`10` dates):** Calibrating marine foraminifera on **`IntCal20` (the terrestrial atmosphere curve, omitting the ~500–600 yr global marine reservoir) with flipped `ΔR = −71`** matches `574–579 cm` to `+1.0 yr` (`9,539` vs `9,538`) and `635–640 cm` to `+0.3 yr` (`13,296.3` vs `13,296`). On correct `Marine20` with `ΔR = +71`, Core 52's claimed YDB (`625–630 cm`, `UGAMS-50555`, `11,120 ± 40`) drops by **`−608 years`** (`12,992 → 12,384` mean / `12,404` median cal BP).

### 1.2 Exact `Marine20` Recalibration Across Holocene and Deglacial `ΔR` Scenarios

| Core & claimed YDB | Lab ID & raw `¹⁴C ± 1σ` | Moore et al. `SI Table S1` `μ` | **S0: Correct `Marine20` (Holocene `ΔR`)** | **S1: `+200 yr` deglacial** | **S2: `+500 yr` sea-ice** | **S3: `+800 yr` stadial** |
|---|---|---:|---:|---:|---:|---:|
| **Core 52** (`625–630 cm`) | `UGAMS-50555` `11,120 ± 40` | `12,992` *(IntCal20 bug)* | **`12,404`** `[12,130–12,620]` (`P_YDB=0.001`) | `12,116` (`P_YDB=0.000`) | **`11,642`** (`58%` post-YD) | **`11,222`** (`93%` post-YD) |
| **Core 64** (`312–318 cm`) | `UGAMS-61104` `11,489 ± 45` | `13,025` *(−ΔR sign flip)* | **`12,627`** `[12,450–12,780]` (`P_YDB=0.174`) | `12,411` (`P_YDB=0.009`) | **`11,993`** (`P_YDB=0.000`) | **`11,543`** (`68%` post-YD) |
| **Core 67** (`32–35 cm`) | `UGAMS-61105` `11,495 ± 30` | `13,030` *(−ΔR sign flip)* | **`12,633`** `[12,465–12,770]` (`P_YDB=0.178`) | `12,422` (`P_YDB=0.009`) | **`12,003`** (`P_YDB=0.000`) | **`11,551`** (`68%` post-YD) |
| **Core 77** (`161–162 cm`) | `UGAMS-51366` `10,810 ± 30` | `12,198` *(−ΔR sign flip)* | **`11,889`** `[11,620–12,185]` (`P_YDB=0.000`) | `11,570` (`74%` post-YD) | **`11,155`** (`99%` post-YD) | **`10,742`** (`100%` post-YD) |

*(Note also that Core 67's actual spherule peak in `SI Table S6` is at `30–32 cm`, `UGAMS-51985: 11,280 ± 30`, which calibrates to **`12,364 cal BP`** even under `S0` Holocene `ΔR`!)* Furthermore, `SI Table S1` contains **4 major stratigraphic radiocarbon age inversions** (`>2σ` older sediment overlying younger sediment), including **`2,860 ¹⁴C yr`** directly above Core 64's YDB (`275–280 cm: 13,850` above `290–293 cm: 10,990`) and **`640 ¹⁴C yr`** directly above Core 52's YDB (`615–620 cm: 11,760` above `625–630 cm: 11,120`).

**Fairness check on foraminifera metadata (`SI Table S17`, p. 220):** *PLOS One*'s notice stated that foraminifera type and specimen counts were missing. In fact, `SI Table S17` (p. 220 of `baffin_bay_si.pdf`) *does* list approximate specimen counts (`400–4,400`) and broad group (`hyaline calcite mixed benthics` vs. `planktics`) for **17 of 21 samples** (4 left blank), though without species-level proportions of each dated pick. Ironically, `SI Table S17` exposes a separate dating problem: **Cores 64 and 67 mixed benthic and planktic foraminifera inside the same AMS targets**, even though surface and deep water masses in Baffin Bay carry different reservoir ages.

---

## 2. Pillar 2 — Foraminifera (`SI Figs S30–S34`), Core Coverage (`SI Table S6`), and Nanoparticles (`Table S7`)

### 2.1 Direct Inspection of `SI Figs S30–S34` (`baffin_bay_si.pdf`, pp. 32–35)
Extracting the embedded SEM-EDS images directly verifies *PLOS One*'s misidentification claim:

| Figure (Core 52, `574–579 cm`) | `C (wt%)` | `O (wt%)` | `Ca (wt%)` | `Ca+C+O (wt%)` | `Fe (wt%)` | Morphology observed |
|---|---:|---:|---:|---:|---:|---|
| `SI Fig S30` (Point 001) | `20.37` | `57.18` | `18.97` | **`96.52%`** | `0.0%` | Regular `1–2 µm` wall pores, chamber septa, prismatic wall |
| `SI Fig S31` (Point 002) | `13.75` | `48.63` | `32.14` | **`94.52%`** | `0.0%` | Broken radial calcite wall rim of same foram test |
| `SI Fig S33` (MAP 1 of S32) | `24.94` | `50.50` | `17.09` | **`92.53%`** | `0.0%` | Ca-C-O elemental map matching entire broken test |
| `SI Fig S34` (Point 001) | `20.21` | `51.18` | `24.04` | **`95.43%`** | `0.0%` | Broken porous calcareous test fragment |

Two additional findings emerge directly from the PDF:
- **Wrong epoch:** `Core 52 (574–579 cm)` is dated in `SI Table S1` (`UGAMS-45600: 8,480 ± 30`) to **`9,538 cal BP`** (`8,785 cal BP` on correct `Marine20`) — **Early Holocene, 3,300–4,000 years AFTER the Younger Dryas!** Yet main-text Fig. 6(b) and 6(e–f) also showcase claimed "YDB meltglass" from that exact Early Holocene `574–579 cm` depth.
- **Fairness boundary:** Checking `Table S8a/S8b` shows **`0 of 18`** LA-ICP-MS microspherules had `CaO > 15 wt%` (and only `1 of 143` MDP analyses in `Table S10` had `Ca > 15 wt%`), so calcareous foraminifera did **not** contaminate the 18 LA-ICP-MS microspherule measurements—the misidentification is documented in the SEM plates (`SI Figs S30–S34`) and creates unquantified risk in visual spherule counts/Ca curves.

### 2.2 Core Coverage & Core 64 vs. Core 67 Non-Uniqueness (`SI Table S6`, `n = 28` rows)
- **Narrow sampling coverage:** Across all 4 cores (`2,756.5 cm` total length), `SI Table S6` spans just **`16.7%`** of the core length—and only **`2.1%` (`11 / 519 cm`, 7 samples)** in Core 67 and **`7.2%` (`51 / 713 cm`, 7 samples)** in Core 64.
- **Exact verification of *PLOS One*'s Core 64 vs. Core 67 critique:** Core 64's single-point **out-of-YDB** peak at `290–293 cm` (`680 CDPs/kg`) is **`1.062×` Core 67's claimed YDB peak** at `32–35 cm` (`640 CDPs/kg`).
- **Core 77 mismatch & arithmetic error:** Core 77's Fig. 2 dated YDB level (`161–162 cm`) contains **`0` spherules (`0/kg`)**; the peak row marked with footnote `a` is `6 cm` deeper (`167–168 cm`, undated), where `10` spherules in `0.14 g` is tabulated as `965/kg` instead of `10 / 0.00014 kg = 71,429/kg` (a `74×` discrepancy suggesting either a sample-mass typo for `~10.4 g` or an arithmetic error).

### 2.3 Blind Nanoparticle Depth-Profile Audit (`Table S7`, SP-ICP-TOF-MS)
Testing all `10` nanoparticle metrics (`Pt`, `Ir`, `Pd`, `Ni`, `Co`, `Cr`, `Pt/Ir`, `Pt/Pd`, `Pt/Fe`, `Ni/Fe`) blindly across the `6` sampled depths in each core:
- **Core 64 (`312–318 cm` claimed YDB):** **`9 of 10`** metrics peak **OUTSIDE** the claimed YDB (`272–297 cm`, up to `40 cm` above it!) in both Total Mass and Mass Concentration. The single metric peaking inside `312–318 cm` (`Pt/Pd = 0.76`) is below `1.0`, failing Moore et al.'s own `Pt/Pd > 1.0` extraterrestrial criterion.
- **Core 67 (`30–35 cm` claimed YDB):** **`6 of 10`** metrics (`Pt`, `Ir`, `Pt/Ir`, `Pt/Pd`, `Pt/Fe`, `Ni/Fe`) *do* peak inside `30–35 cm` (`Pt` reaches `1.52×` median mass and `7.15×` median concentration at `30–32 cm`, `Pt/Ir = 1.70–3.59`), while `Co` (`5.55×`), `Cr` (`3.31×`), `Pd` (`2.38×`), and `Ni` peak shallower at `25–28 cm`. Thus Core 67 shows a genuine local Pt-nanoparticle concentration peak—just not replicated at the YDB depth in Core 64, and dated ~450–1,200 yr too young under correct `Marine20` calibration.

---

## 3. Pillar 3 — The `×100` Geochemical Math Artifact (`Table S8a/S8b`), Bulk `Δ¹⁷O*`, and Citations

1. **Raw LA-ICP-MS microspherules (`n = 18`: `6` in `Table S8a`, `12` glassy spots in `Table S8b`):**
   - **`100.0%` (`18/18`)** have raw `Fe/Ni > 200` (terrestrial crustal/oxide; median `Fe/Cr = 1,031`, median `Fe/Ni = 1,556`—more Ni/Cr-depleted than average Upper Continental Crust `426 / 834`).
   - **`0.0%` (`0/18`)** fall in the chondritic / Comet Wild 2 field (`Fe/Cr ≤ 150, Fe/Ni ≤ 80`) raw.
   - Across the `4` `Table S8a` spherules with positive `Pt` and `Ir`, median **`Pt/Ir = 556.3`** (vs. CI chondrite `~2.1`—**265× off chondritic**).
2. **Pure-terrestrial false-positive test of Moore et al.'s `×100` formula:**
   - Moore et al. multiplied total measured `Ni` and `Cr` by `100` (assuming `1 wt%` ET admixture *without subtracting the `99 wt%` terrestrial Ni and Cr first*), dividing `Fe/Cr` and `Fe/Ni` by `100` and pushing **`88.9%` (`16/18`)** into the Comet Wild 2 / cosmic box.
   - Passing **100% pure terrestrial Upper Continental Crust** (`0%` cosmic material; Rudnick & Gao 2003) through the exact same `×100` formula drops `Fe/Cr` from **`426.1 → 4.26`** and `Fe/Ni` from **`834.0 → 8.34`**—landing straight inside the cosmic box! Passing **100% pure USGS terrestrial basalt `BIR-1G`** through it drops `Fe/Cr` from **`202.1 → 2.02`** and `Fe/Ni` from **`475.9 → 4.76`**—also straight inside the cosmic box!
   - When `99 wt%` Fe-scaled terrestrial crustal background is properly subtracted first, **`0.0%` (`0/18`)** Baffin Bay microspherules show `≥ 1 wt%` CI chondrite Ni and Cr excess (`33.3%` vs unscaled UCC, mostly due to Fe-oxide concentration).
3. **Bulk oxygen isotopes (`Appendix Table A1`, Open University):** Across all 10 Baffin Bay bulk sediment analyses (`4` Core 64, `6` Core 67), **`0` samples** show an extraterrestrial `Δ¹⁷O*` anomaly. In fact, claimed YDB samples (`mean Δ¹⁷O* = −0.040‰`) lie slightly *closer* to terrestrial zero than background sediments (`mean −0.063‰`; range `−0.02 to −0.11‰`, ordinary terrestrial clay/quartz weathering).
4. **Offline XML reference audit (`187` references):** Structural offline parsing detected `28` missing DOIs, `1` duplicated DOI (`Holliday et al. 2023` listed identically at both `ref109` and `ref149`), and `2` format anomalies (`3` structural flags, below our pre-registered `≥ 10` offline threshold—so criterion `A5` logged `False`, since verifying the ~43 wrong-paper DOI mismatches cited on PubPeer requires live Crossref lookups outside our offline script).

---

## 4. Pillar 4 — Shocked Quartz Audit (`Paper B: e0319840` → retracted `e0342620`)

### 4.1 Selective & Unattributed Radiocarbon Dates (`SI Tables S2–S4`)
Extracting the raster table screenshots (`quartz_p2_img1..4`) directly confirms *PLOS One*'s chronology critique:
- **Arlington Canyon (`Table S2`):** Lists only `2` dates (`10,860 ± 70` at `482.5 cm` and `11,020 ± 25` at `500.5 cm`) with **zero lab IDs**, omitting the `11` published direct AMS charcoal dates (`10,960` to `11,440 ¹⁴C BP`, Kennett et al. 2008 Table 4). Crucially, `482.5 cm` lies **`18.5 cm` ABOVE** the `501.0 cm` shocked-quartz layer (`ARL-1B`), while `500.5 cm` calibrates to **`12,955 ± 60 cal BP`** (`13,070–12,840`, older than `12,800`).
- **Blackwater Draw (`Table S3`):** Lists `3` dates (`AA-89168`, `SMU-1880`, `AA-1362`) with **uncalibrated `¹⁴C` ages completely omitted** (calibrated `mu ± sigma` only) and omits `6` published Clovis/YDB-contact dates (`10,490` to `11,630 ¹⁴C BP`).
- **Murray Springs (`Table S4`):** Lists only **1 pre-averaged pooled value** (`Haynes: 10,885 ± 50`), omitting all `8` individual lab IDs (`10,710` to `11,230 ¹⁴C BP`).
- **Recomputing the headline `χ² = 0.057` (`p = 0.972`) synchrony test:**
  - Authors' 3 cherry-picked calibrated dates (`12,810 ± 60` from `482.5 cm` *above* ARL quartz + `12,825 ± 65` + `12,805 ± 45`): **`χ² = 0.064, df = 2, p = 0.968`**.
  - Simply replacing Arlington `482.5 cm` with the authors' **own `500.5 cm` quartz-horizon date (`12,955 ± 60`)**: **`χ²` jumps 66-fold to `4.209` (`p = 0.122`)**.
  - All `6` SI rows in `Tables S2–S4`: `χ² = 6.99, df = 5, p = 0.221`.
  - All **`25` published direct YDB-stratum dates** across those exact three sites: **Ward–Wilson `T = 90.94, df = 24, p < 10⁻⁹`** (decisively rejecting single-year synchrony).

### 4.2 Vertical Background Control Sampling (`SI Tables S5, S6, S8`)
Extracting the raster proxy tables (`quartz_p3_img1`, `p4_img1`, `p5_img1`) directly confirms *PLOS One*'s sampling critique:

| Site (SI Table) | Total strata in table | Strata analyzed for shocked quartz | Above YDB (`0` grains) | In YDB (grains) | Below YDB (`0` grains) | Control grain denominators tabulated? |
|---|---:|---:|---:|---:|---:|---|
| **Arlington Canyon** (`Table S5`) | `31` (`97–501 cm`) | **`4` (`12.9%`)** | `3` (`489–497 cm`) | `1` (`501 cm`: `5`) | **`0` (`ARL-1B` is bottom row!)** | No |
| **Blackwater Draw** (`Table S6`) | `16` (`1239.6–1237.8 m`) | **`3` (`18.8%`)** | `1` (`1238.40 m`) | `1` (`1238.37 m`: `7`) | `1` (`1238.17 m`) | No |
| **Murray Springs** (`Table S8`) | `19` (`16–63 cm`) | **`6` (`31.6%`)** | `3` (`26–44.8 cm`) | `1` (`46.5 cm`: `4`) | `2` (`52, 63 cm`) | No |
| **Combined** | **`66`** | **`13` (`19.7%`)** | `7` | `3` (`16` grains) | `3` | **None (`0/10` controls)** |

Nor does `kennett2025_shocked_quartz.xml` or `kennett2025_si.pdf` contain any age-depth or sedimentation-rate model.

### 4.3 Why Paper B's Verdict Is `retraction_mixed_or_harsh`
Verifying `retraction_shocked_quartz.xml` verbatim confirms that *PLOS One* cited **only** `(a)` radiocarbon date selection/scatter and `(b)` incomplete vertical sampling / missing sedimentation-rate models. It made **zero allegation** of image manipulation, fabrication, or mineralogical misidentification against the paper's core TEM/SEM/CL/EBSD microscopy of the 16 glass-filled fractured quartz grains, nor against the hydrocode model. Both editorial critiques are genuinely verified and invalidate the paper's claim of a proven, synchronous, layer-unique 12.8 ka horizon—but retracting the entire article without showing error in its primary microscopy observations is noticeably harsher than standard journal practice (Expression of Concern or Major Correction).

---

## 5. Limits & What This Audit Cannot Settle

1. **Physical microscopy of the 16 quartz grains in Paper B (`e0319840`):** No spreadsheet or PDF audit can determine whether the glass-filled fractures imaged in those 16 quartz grains formed by cosmic airbursts, lightning, tectonic/metamorphic stress, or sample preparation. Settling that requires blind re-examination of the original thin sections and FIB-TEM foils by independent shock-metamorphism laboratories—alongside full-column control slides (including *below* `501 cm` at Arlington Canyon) with pre-registered grain denominators.
2. **Visual microspherule counts in Paper A (`SI Table S6`):** While `SI Figs S30–S34` are unambiguously calcareous marine foraminifera and `0/18` LA-ICP-MS spherules were high-Ca, the raw per-grain classification log for all `144` counted spherules and MDPs in `SI Table S6` is not published, so we cannot measure the exact fraction of visually counted spherules that were foraminifera.
3. **Crossref DOI resolution:** Our offline XML audit checked syntax and duplicates without making live Crossref API calls, so it did not independently count all ~43 wrong-paper DOI mismatches reported on PubPeer (keeping criterion `A5` formally `False`, which did not change Paper A's `4/5` `retraction_strongly_supported` verdict).

---

## 6. What This Means

Reading the actual spreadsheets and Supporting Information behind the two February 2026 *PLOS One* retractions separates genuine data breakdowns from harsh editorial judgment. **The Baffin Bay ocean-core retraction was strongly warranted:** the published Younger Dryas ages were created by a flipped `ΔR` sign in three cores and accidental use of the terrestrial `IntCal20` curve in the fourth (`+297` to `+769` years too old before any polar sea-ice correction), four "cosmic spherule" SEM figures are visibly porous calcareous foraminifera from a `9.5 ka` Early Holocene level, `9` of `10` Core 64 nanoparticle metrics peak outside the claimed boundary, and the `×100` chemistry formula turns 100% pure Earth crust into "comet dust." **The Shocked Quartz retraction is much closer to a borderline call:** *PLOS One*'s criticisms of cherry-picked radiocarbon dates and thin vertical background controls (`0` strata checked below the boundary at Arlington Canyon; only `19.7%` of strata checked overall) are completely verified and undercut the claim of a synchronous 12.8 ka event—yet the retraction notice never challenged the quartz electron-microscopy images themselves, leaving the physical nature of those 16 fractured grains an open question for independent mineralogical labs.
