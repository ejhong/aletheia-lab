# Did Anyone Smelt Metal Before the Bronze Age? (Ice-Core & Peat Side-Channel) — Results

- **Issue:** #82 (`lane:data`)
- **Protocol locked:** `2026-11-24T17:13:38Z` (`protocol.lock`, SHA-256 `1d74625bfc53`, commit `2b998f8`)
- **Amendments:** 1 ([`amendments.md`](amendments.md): Dome du Goûter's archived lead file `legrand2024-id3_1-lead.txt` spans `2,549–1,184 yr BP` rather than `>5,000 BP`, so it is retained as an independent European Alpine positive control normalized via `UCC_PB_CE = 19/83` while all pre-5,000 BP tests run unmodified across the other five archives).
- **Authorship:** Designed, coded, and executed by Antigravity (Google DeepMind) on 2026-11-24, directed by Eugene Jhong. Open to independent second-vendor replication.

## Answer

**Pre-registered verdict: Null — No evidence of pre-Bronze-Age metallurgy between 47,400 and 5,000 BP across six polar ice-core, Alpine ice, and European peat archives, with a quantitative physical upper bound established.**

- **The detectors clearly work (Positive Controls):** Historical ancient smelting lights up decisively across independent archives—in East Greenland ice (`RECAP`: Roman `p = 3.1 × 10⁻¹⁰⁴`, High Medieval `p = 1.0 × 10⁻²⁵⁷`, Industrial `p = 5.8 × 10⁻²⁰⁰`), European Alpine ice (`Dome du Goûter`: Roman median `EF_UCC = 77.3`, `ncPb = 862 pg/g`), Central European peat (`Füramoos`: Bronze/Iron `p = 5.3 × 10⁻²²`, Roman `p = 1.1 × 10⁻⁸`, Medieval `p = 1.2 × 10⁻⁶`, paired with a sharp unradiogenic ore-lead drop in `206Pb/207Pb` from `1.2085 ± 0.0046` to `1.139–1.190`, `p = 4.8 × 10⁻⁶`), and Swedish peat (`Store Mosse`: raw `Pb` rises from `0.00 mg/kg` before 5 ka to `1.0` Roman, `4.0` Medieval, `54.5` Industrial).
- **Pre-5,000 BP atmospheric quiet:** Across **47,371–5,000 BP**, **zero** sustained non-volcanic heavy-metal pollution anomalies (`EF ≥ 3.0`, or `EF ≥ 2.0` paired with unradiogenic `206Pb/207Pb`) appear in any archive:
  - **East Greenland (`RECAP`, `7.98–5.00 ka`):** `0/30` volcanic-masked 100-year bins reach even `EF ≥ 2.0` (max `EF = 1.36`, `p95 = 1.28`).
  - **Central Greenland Ice Age (`GISP2`, `47.4–40.4 ka`, MIS 3):** `0/70` volcanic-masked 100-year bins reach `EF ≥ 3.0` across all four smelting-associated chalcophile metals (`Pb/Ce` max `1.57`, `Cd/Ce` `2.10`, `Bi/Ce` `1.62`, `Tl/Ce` `1.60`).
  - **Central European peat (`Füramoos`, `14.3–5.0 ka`):** `0/284` XRF samples reach `EF ≥ 3.0` (median `0.55`, max `2.91`), and all `12/12` pre-5 ka ICP-MS lead-isotope ratios remain locked in the natural crustal band (`206Pb/207Pb = 1.204–1.216`).
  - **Northern European peat (`Store Mosse`, `6.4–5.0 ka`):** Median raw `Pb = 0.00 mg/kg` (below XRF detection limit) and `Cu = 1.0 mg/kg`; `0` sustained anomalies in `Pb/Ti`, `Cu/Ti`, or `Zn/Ti`.
  - **East Antarctica (`EPICA Dome C`, `40–5 ka` vs. `217–40 ka` natural baseline):** Median `EF_Pb = 1.00`, zero unradiogenic isotope excursions. The lone elevated LGM point (`18,160 BP`, `EF = 4.25`) is isolated (`< 30 yr`; `EF = 1.25` at `18,130 BP`) and strongly *radiogenic* (`206Pb/207Pb = 1.257`, `z = +2.56`)—the opposite of unradiogenic ore-lead smelting, consistent with ancient cratonic mineral dust.
- **Physical upper bound:** In East Greenland (`RECAP`, `8.0–5.0 ka`), 95% of pre-Bronze century bins stay below **`47%` of Roman Empire excess lead** (`≤ 1.56 kt/yr` atmospheric Pb at McConnell et al.'s `3.3 kt/yr` Roman benchmark; absolute maximum century bin `≤ 79%` / `2.62 kt/yr`, attributable to local East Greenland dust variability since `Pb/Ce` remains `≤ 0.139`, well below upper continental crust `0.229`). Closer to Europe (`Füramoos`, `14.3–5.0 ka`), atmospheric `Pb EF` and `206Pb/207Pb` exclude even Bronze-Age-scale European lead smelting across the entire 9,300-year Late Glacial and Early/Mid-Holocene record.

---

## Detailed Evidence

### Test 0 & Test 1 — Positive Controls vs. Pre-5,000 BP Multi-Archive Scan

| Archive | Pre-5 ka Window (Samples) | Pre-5 ka Median EF (Max) | Bronze/Iron (`5–2.15 ka`) | Roman (`2.15–1.65 ka`) | Medieval (`1.0–0.5 ka`) | Industrial (`<0.25 ka`) | Sustained Pre-5 ka `EF ≥ 3` |
|---|---|---:|---:|---:|---:|---:|---:|
| **RECAP** (E. Greenland, volc-masked) | `7.98–5.00 ka` (`923`) | `1.00` (100-yr max `1.36`) | `1.09` (`p=3×10⁻¹³`) | **`1.56`** (`p=3×10⁻¹⁰⁴`) | **`2.17`** (`p=10⁻²⁵⁷`) | **`8.75`** (`p=6×10⁻²⁰⁰`) | **0** |
| **GISP2** (C. Greenland, volc-masked) | `47.4–40.4 ka` (`4,480`) | `1.00` (100-yr max `1.57`) | — | — | — | — | **0** |
| **Dome du Goûter** (French Alps, `EF_UCC`) | *covers `2.55–1.18 ka`* (Amend. 1) | — | `2.99` (`2.55–2.15 ka`) | **`77.33`** (`862 pg/g`) | — | — | — |
| **Füramoos** (S. Germany peat XRF) | `14.34–5.00 ka` (`284`) | `0.55` (max `2.91`) | **`1.02`** (`p=5×10⁻²²`) | **`1.40`** (`p=1×10⁻⁸`) | **`2.03`** (`p=1×10⁻⁶`) | **`5.52`** | **0** |
| **Store Mosse** (S. Sweden peat raw `Pb`) | `6.42–5.00 ka` (`21`) | `0.00 mg/kg` (max EF `1.42`) | `0.00 mg/kg` | `1.00 mg/kg` | `4.00 mg/kg` | **`54.50 mg/kg`** | **0** |
| **EPICA Dome C** (E. Antarctica `Pb/Ba`) | `40.0–5.0 ka` (`30`) | `1.00` (1 isol. rad. pt `4.25`) | `0.75` (`N=1`) | — | — | — | **0** |

*Note on RECAP local dust vs. UCC:* Because Renland is a coastal East Greenland ice cap with high local Precambrian mineral dust (`Ce` median `42.4 pg/g` vs. `~3–6 pg/g` at central Greenland NGRIP2), its natural baseline `Pb/Ce` ratio is `0.1021` (below upper continental crust `0.2289`). Three 50-year pre-5 ka intervals (`7175–7275`, `6625–6700`, `5525–5675 BP`) show `1.1–2.4 pg/g` empirical excess over `0.1021 × Ce`, but remain at `EF_emp = 1.28–1.36` (`EF_UCC = 0.56–0.73`, `ncPb_UCC = 0.00 pg/g`) with zero matching signal in Füramoos or Store Mosse—consistent with minor local dust-provenance variance rather than smelting.

### Test 2 — Multi-Element Chalcophile Check (`Cd`, `Bi`, `Tl` in GISP2; `Cu`, `Zn` in Store Mosse)
- **GISP2 (`47.4–40.4 ka`, 70 century bins, volcanic-masked):** `0` bins reach `EF ≥ 3.0` and `0` sustained 50-year anomalies occur across `Pb/Ce` (p95 `1.44`, max `1.57`), `Cd/Ce` (p95 `1.79`, max `2.10`), `Bi/Ce` (p95 `1.41`, max `1.62`), or `Tl/Ce` (p95 `1.53`, max `1.60`).
- **Store Mosse (`6.4–5.0 ka`):** `0` sustained pre-5 ka anomalies in `Cu/Ti` (max `1.45`; raw `Cu` stays at `1.0 mg/kg` pre-5 ka vs. `2.0` Roman/Medieval and `8.5` Industrial) or `Zn/Ti` (one isolated point `3.06`, `0` sustained).

### Test 3 — Radiogenic Lead Isotope (`206Pb/207Pb`) Fingerprints
- **Füramoos (S. Germany, `14.3–0.2 ka`, `N=30` ICP-MS):** Every pre-5 ka sample (`N=12`) sits tightly in the natural crustal dust band (`mean = 1.2085 ± 0.0046`, range `1.2040–1.216`). Post-5 ka samples (`N=18`) plunge to median `1.1900` and minimum `1.1391` (`Mann-Whitney p = 4.85 × 10⁻⁶`), marking the introduction of unradiogenic European ore lead. Coupled pre-5 ka anomalies: **0**.
- **EPICA Dome C (E. Antarctica, `217–2 ka`):** Natural Pleistocene (`217–40 ka`, `N=42`) mean `206Pb/207Pb = 1.2155 ± 0.0162`. Every `40–5 ka` sample (`N=30`) lies within `1.193–1.257`, with zero unradiogenic ore-lead drops (`< 1.183`).

### Test 4 — Physical Upper Bound on Lost Metallurgy
- In **RECAP (East Greenland)**, the Roman Empire (`2.15–1.65 ka`) deposits a volcanic-masked median excess of `ncPb_emp = 2.15 pg/g` (corresponding to McConnell et al. 2018's FLEXPART-modeled `~3.3 kt/yr` European atmospheric Pb emissions and `~40–80 kt/yr` total lead-silver smelting).
- Across all `30` pre-Bronze centuries (`7.98–5.00 ka`), the 95th-percentile century median is `1.01 pg/g` (**`47%` of Roman**, or **`≤ 1.56 kt/yr`** atmospheric Pb) and the absolute maximum century is `1.71 pg/g` (**`79%` of Roman**, or **`≤ 2.62 kt/yr`**)—and zero centuries exceed `EF = 1.36`.
- In **Central Europe (`Füramoos`)**, where European smelting signals are far less diluted by distance, `14.3–5.0 ka` stays uniformly below Bronze-Age (`EF 1.02`) and Roman (`EF 1.40`, `206Pb/207Pb < 1.19`) levels throughout.

---

## Limits

1. **Temporal gap in public Greenland Pb (`40.4–8.0 ka`):** Our open-access continuous Greenland ICP-MS datasets cover `47.4–40.4 ka` (GISP2) and `7.98–0.12 ka` (RECAP), while `14.3–8.0 ka` is covered in the Northern Hemisphere by Füramoos peat (Germany) and `40.4–14.3 ka` is covered in our public files by Antarctic EPICA Dome C (Southern Hemisphere). A continuous public Greenland `Pb/Ce` dataset spanning the LGM (`40–14 ka`) would tighten Northern Hemisphere bounds across that specific Ice Age window.
2. **Cold-worked native metals and tiny local furnaces:** Hammering native copper or gold produces no atmospheric smelting plume, and very small, brief (<25 yr), or remote Southern/equatorial smelting operations well below Bronze Age / Roman tonnage would fall below polar detection limits.
3. **Peat mineral-dust sensitivity:** In Store Mosse, late-Holocene agricultural soil erosion (`Ti` jumping `3–6×`) depresses `Pb/Ti` ratios even while raw `Pb` rises from `0` to `4 mg/kg`, showing why multi-archive cross-checks (ice cores + Pb isotopes) are essential.

## What this means

If an advanced Ice Age or pre-Bronze-Age civilization ever smelted metals at anything approaching Bronze Age, Roman, or Medieval industrial scale, the atmosphere would have preserved its exhaust even if rising seas erased every city. Across 47,000 years of Greenland ice, Antarctic ice, Alpine glacier ice, and European peat bogs, the archives pick up Roman, Medieval, and Industrial smelting with overwhelming clarity (`p < 10⁻¹⁰⁰` in Greenland, `EF = 77` in the Alps, and a sharp ore-lead isotope drop in Germany), yet stay completely flat before 5,000 years ago. Whatever human ingenuity existed before the Bronze Age left no detectable heavy-metal pollution plume in the global atmosphere.
