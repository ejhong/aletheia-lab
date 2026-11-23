# Results — Does the Taurid comet stream hide a swarm of large fragments? (`taurid-swarm`)

- **Issue:** [#103](https://github.com/ejhong/aletheia-lab/issues/103)
- **Lane:** `data`
- **Protocol lock:** `a526349cbc5c566bee97ad2213a543f150e201e6ba134499a3ff873e54364c1a` (locked `2026-11-23T19:42:27Z`, commit `23c76b3`)
- **Amendments:** None.
- **Authorship:** Conducted and written by Antigravity (Google DeepMind) on 2026-11-23, directed by Eugene Jhong.
- **Spending:** $0 (public NASA/JPL APIs, local Python 3.12 + NumPy 2.3.5).

---

## 1. Headline Answer

**No detectable macro-fragment Taurid swarm in either NASA archive (`0 of 4` pre-registered criteria passed: `no_macro_swarm_detected`).**

Testing **43,156 near-Earth asteroids** from NASA/JPL's Small-Body Database (2026-11-23) and **1,045 US government satellite bolides** across 32 complete years (`1994–2025`) from NASA/JPL CNEOS yields a sharp, consistent picture:

1. **Napier's (2010) famous alignment collapses the moment you step past `H < 16.5`:** At Napier's exact 2010 cutoff (`H < 16.5`, `N = 17` giant asteroids), longitude-of-perihelion alignment with Comet `2P/Encke` (`ϖ_E = 161.29°`) still appears (`c_bar = +0.557`, `11/17 = 64.7%` within `±45°`, `p_unif = 0.0005`). Yet the instant we move just 1.5 magnitudes deeper to **1 km asteroids (`H < 18.0`, `N = 64`, Primary Test A1)**, the alignment **vanishes completely to zero** (`c_bar = −0.001`, `p_unif = 0.504`, matching the inclined control `p = 0.373`). At `H < 20.0` (`N = 331`), `H < 22.0` (`N = 848`), and `All H` (`N = 2,470`), alignment stays slightly *negative* (`c_bar = −0.068`, `f_45 = 19.6%–21.7%`, below uniform `25%`). That **size inversion** is the exact opposite of a cometary fragmentation cascade (`N(>D) ∝ D^(-3.5)`), which would produce *far more* aligned 300 m–1 km fragments than 2–5 km fragments.
2. **Only a handful of sub-km objects sit in the 7:2 Jupiter resonance (`Test A2` failed):** Across the entire 2026 NASA catalog, only **3** `H < 18.0` asteroids (two of which have bright rocky albedos `0.21–0.37`) and **13** `H < 20.0` asteroids (`18.1%` vs. `11.2%` anti-Taurid, `1.61×`, `p = 0.095`; vs. `15.1%` secular control, `p = 0.302`) occupy the `2.21–2.30 AU` 7:2 Taurid resonant zone — only **6** of which meet tight Encke-like bounds (`e ≥ 0.75, i ≤ 12°, |Δϖ| ≤ 30°`). A modest sub-200 m excess appears only at our sensitivity tier `H < 22.0` (`36/174 = 20.7%` vs. `11.7%` anti-Taurid, `p = 0.0025`, `p_ctrl = 0.051`), representing ~15 excess ~150 m bodies rather than a dense swarm of km-scale fragments.
3. **Zero signal in 32 years of US satellite airbursts (`Tests B1 & B2` failed):** Across `1,045` satellite-detected bolides (`1994–2025`, `1,182 kt` total energy), the Autumn Taurid window (`Oct 15–Nov 30`) shows **133 bolides vs. 134.5 expected** (`0.99×`, `p = 0.568`; `≥ 1 kt`: `12` vs. `14.8` expected, `p = 0.820`), and the Daytime β-Taurid window (`Jun 10–Jul 10`) shows **81 vs. 88.7 expected** (`0.91×`, `p = 0.818`). During the **6 published 7:2 resonant swarm return years (`1998, 2005, 2015, 2018, 2022, 2025`)**, the within-year Autumn bolide share is **`12.7%` vs. `13.0%` in the 26 non-swarm years (`p = 0.520`)**, with `0.33` vs. `0.38` large (`≥ 1 kt`) bolides/year (`p = 0.688`).

---

## 2. Pre-Registered Criteria Scorecard

| Criterion | Archive & Sample | Observed | Threshold | Result |
|---|---|---|---|---|
| **A1** | JPL NEAs (`H < 18.0`, `N = 64` in Napier box) | `c_bar = −0.001` (`p_unif = 0.504`), vs. `Ctrl_LowE` `p = 0.0014` | `p_unif < 0.01` AND `p_ctrl < 0.05` | **Not met** |
| **A2** | JPL NEAs (`H < 20.0`, `7:2` resonance `2.21–2.30 AU`) | `13/72` (`18.1%`) vs. `11.2%` anti (`1.61×, p = 0.095`), `15.1%` ctrl (`p = 0.302`) | `≥ 2.0×` AND `p_anti < 0.01` AND `p_ctrl < 0.01` | **Not met** |
| **B1** | CNEOS bolides (`1994–2025`, `N = 1,045`) | Autumn `133` vs. `134.5` (`p = 0.568`); Daytime `81` vs. `88.7` (`p = 0.818`) | Any `p < 0.01` in count or `≥ 1 kt` | **Not met** |
| **B2** | CNEOS 6 swarm years vs. 26 non-swarm years | Within-year Autumn share `12.7%` vs. `13.0%` (`p = 0.520`); `≥ 1 kt`: `0.33` vs. `0.38/yr` (`p = 0.688`) | `p < 0.01` in `s_cnt` or `≥ 1 kt` | **Not met** |

**Joint pre-registered verdict:** `no_macro_swarm_detected` (`0 of 4` criteria passed).

---

## 3. Archive A — NASA/JPL Near-Earth Asteroids (`43,156` NEAs)

### 3.1 Perihelion Alignment Across Magnitude Tiers (`Test A1`)

Reference parent: Comet `2P/Encke` (`a = 2.218 AU, e = 0.8470, i = 11.34°, ϖ_E = 161.29°`).

| Magnitude Tier | Approx. Size (`p_V = 0.14–0.05`) | `Box_T` `N` | `Box_T` `c_bar` | `Box_T` `f_45` | `p_unif` | `Ctrl_LowE` `c_bar` (`N`) | `Ctrl_HighI` `c_bar` (`N`) | `p` vs. `LowE` | `p` vs. `HighI` |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `H < 16.5` *(Napier 2010 cutoff)* | `≳ 1.8–3.0 km` | 17 | **`+0.557`** | `64.7%` | **`0.0005`** | `−0.356` (37) | `−0.022` (26) | `0.0001` | `0.0059` |
| **`H < 18.0` *(Primary A1)*** | `≳ 0.9–1.5 km` | 64 | **`−0.001`** | `31.2%` | **`0.5036`** | `−0.324` (169) | `−0.041` (80) | `0.0014` | `0.3727` |
| `H < 20.0` | `≳ 0.35–0.60 km` | 331 | `−0.068` | `21.7%` | `0.9603` | `−0.337` (827) | `−0.025` (301) | `0.0001` | `0.7813` |
| `H < 22.0` | `≳ 0.14–0.24 km` | 848 | `−0.068` | `20.5%` | `0.9975` | `−0.323` (2,255) | `−0.041` (520) | `0.0001` | `0.7538` |
| `All H` | all sizes | 2,470 | `−0.068` | `19.6%` | `1.0000` | `−0.185` (10,254) | `−0.071` (653) | `0.0001` | `0.4710` |

**Why `Ctrl_LowE` is strongly negative (`c_bar ≈ −0.33`):** Moderate-eccentricity asteroids (`0.40 ≤ e < 0.63`) are strongly aligned with **Jupiter's perihelion (`ϖ_J = 14.7°`)** — their circular mean sits at `331°–352°`, nearly opposite Comet Encke (`161.3°`). High-eccentricity planet-crossers (`e ≥ 0.63`) decouple from Jupiter's apsidal alignment in *both* the low-inclination Taurid plane (`Box_T`) and the inclined control (`Ctrl_HighI`, `14° < i ≤ 35°`), producing nearly flat `ϖ` distributions (`c_bar ≈ −0.04` to `−0.07`, `p = 0.37–0.78` between them across every tier `H < 18` through `All H`).

**The incremental size test makes the `H < 16.5` collapse unmistakable:**
- `H < 16.5`: `11 / 17` (`64.7%`) lie within `±45°` of Encke.
- `16.5 ≤ H < 18.0`: only **`9 / 47` (`19.1%`)** lie within `±45°` of Encke (below uniform `25%`).
- `18.0 ≤ H < 20.0`: only **`52 / 267` (`19.5%`)** lie within `±45°` of Encke.
- `20.0 ≤ H < 22.0`: only **`102 / 517` (`19.7%`)** lie within `±45°` of Encke.

### 3.2 7:2 Jupiter Mean-Motion Resonance (`2.21 ≤ a ≤ 2.30 AU`, `Test A2`)

| Tier | Aligned `Box_T` in `7:2` | Anti-Taurid `Box_T` in `7:2` | `Ctrl_LowE` in `7:2` | Enrich. vs. Anti | `p_vs_anti` | `p_vs_ctrl` |
|---|---:|---:|---:|---:|---:|---:|
| `H < 16.5` | `3 / 11` (`27.3%`) | `0 / 6` (`0.0%`) | `5 / 37` (`13.5%`) | — | `0.241` | `0.253` |
| `H < 18.0` | `3 / 20` (`15.0%`) | `5 / 44` (`11.4%`) | `22 / 169` (`13.0%`) | `1.32×` | `0.490` | `0.509` |
| **`H < 20.0` *(Primary A2)*** | **`13 / 72` (`18.1%`)** | **`29 / 259` (`11.2%`)** | **`125 / 827` (`15.1%`)** | **`1.61×`** | **`0.095`** | **`0.302`** |
| `H < 22.0` *(sensitivity)* | `36 / 174` (`20.7%`) | `79 / 674` (`11.7%`) | `351 / 2,255` (`15.6%`) | `1.77×` | `0.0025` | `0.051` |
| `All H` *(sensitivity)* | `69 / 483` (`14.3%`) | `222 / 1,987` (`11.2%`) | `1,194 / 10,254` (`11.6%`) | `1.28×` | `0.035` | `0.047` |

### 3.3 Complete Census of All 13 `H < 20.0` NEAs in the 7:2 Taurid Resonant Zone

| Designation | `a` (AU) | `e` | `i` (°) | `ϖ` (°) | `Δϖ` (°) | `H` | Measured Diam. / Albedo | Tight Encke (`e≥0.75, i≤12°, |Δϖ|≤30°`) |
|---|---:|---:|---:|---:|---:|---:|---|---|
| `4197 Morpheus (1982 TA)` | 2.296 | 0.773 | 12.6° | 129.6° | −31.7° | 14.97 | `1.80 km` / `0.37` *(bright rocky)* | No |
| `5731 Zeus (1988 VP4)` | 2.265 | 0.653 | 11.2° | 139.0° | −22.3° | 15.47 | `5.23 km` / `0.031` *(dark)* | No |
| `6063 Jason (1984 KB)` | 2.220 | 0.763 | 5.0° | 146.7° | −14.6° | 16.02 | `1.40 km` / `0.21` *(bright rocky)* | Yes |
| `452639 (2005 UY6)` | 2.249 | 0.873 | 12.2° | 164.5° | +3.2° | 18.14 | `2.25 km` / `0.018` *(very dark)* | No |
| `506859 (2007 VW137)` | 2.236 | 0.735 | 5.8° | 184.9° | +23.6° | 18.25 | — | No |
| `477327 (2009 TB8)` | 2.275 | 0.706 | 10.2° | 144.9° | −16.4° | 18.32 | — | No |
| `885322 (2018 TY2)` | 2.289 | 0.842 | 4.6° | 162.1° | +0.8° | 19.04 | — | **Yes** |
| `(2018 UN1)` | 2.252 | 0.793 | 5.3° | 156.5° | −4.8° | 19.40 | — | **Yes** |
| `(2016 PZ39)` | 2.268 | 0.787 | 4.3° | 198.0° | +36.7° | 19.42 | — | No |
| `828534 (2004 TG10)` | 2.237 | 0.861 | 4.2° | 162.5° | +1.2° | 19.47 | `1.32 km` / `0.018` *(very dark)* | **Yes** |
| `619920 (2006 KY86)` | 2.293 | 0.649 | 7.5° | 183.9° | +22.6° | 19.74 | — | No |
| `(2008 ON13)` | 2.224 | 0.812 | 5.7° | 190.8° | +29.5° | 19.90 | — | **Yes** |
| `(2010 LU108)` | 2.229 | 0.823 | 9.5° | 176.7° | +15.4° | 19.95 | `0.82 km` / `0.026` *(very dark)* | **Yes** |

Notice that **two of the three `H < 16.5` objects** (`Morpheus` and `Jason`) have bright stony albedos (`0.37` and `0.21`), inconsistent with dark cometary nuclei (`~0.02–0.05`), while a genuine small group of very dark sub-km bodies (`2005 UY6`, `2004 TG10`, `2010 LU108`, plus `2018 TY2`, `2018 UN1`) really does orbit near `2P/Encke` — totaling at most a **handful** of sub-km bodies, not dozens or hundreds.

---

## 4. Archive B — NASA/JPL CNEOS Satellite Bolides (`1994–2025`, `1,045` Airbursts)

### 4.1 Calendar Seasonality (`Test B1`)

| Window | Observed Count | Expected Count | Rate Ratio | `p_count` | `≥ 1 kt` Obs / Exp | `p_1kt` | Total Energy (kt) | `p_energy` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **Autumn Taurids (`Oct 15–Nov 30`)** | 133 | 134.5 | **`0.99×`** | `0.568` | `12 / 14.8` | `0.820` | `68.8` | `0.906` |
| **Daytime β-Taurids (`Jun 10–Jul 10`)** | 81 | 88.7 | **`0.91×`** | `0.818` | `10 / 9.8` | `0.516` | `48.7` | `0.730` |

### 4.2 7:2 Resonant Swarm Return Years (`Test B2`)

| Swarm Subset | Metric | Swarm Years Mean | Non-Swarm Years Mean | Difference | `p_perm` |
|---|---|---:|---:|---:|---:|
| **Primary 6-yr (`1998, 2005, 2015, 2018, 2022, 2025`)** | Within-year Autumn share `s_cnt` | **`12.70%`** | **`12.96%`** | `−0.26%` | **`0.520`** |
| Primary 6-yr | Raw Autumn bolides/yr `N_aut` | `4.50` | `4.08` | `+0.42` | `0.370` |
| Primary 6-yr | Large (`≥ 1 kt`) Autumn bolides/yr | **`0.33`** | **`0.38`** | `−0.05` | **`0.688`** |
| Primary 6-yr | Within-year Autumn energy share `s_eng` | `13.08%` | `8.59%` | `+4.50%` | `0.171` |
| Sensitivity 4-yr core (`1998, 2005, 2015, 2022`) | Within-year Autumn share `s_cnt` | `12.93%` | `12.91%` | `+0.02%` | `0.485` |
| Sensitivity 4-yr core | Large (`≥ 1 kt`) Autumn bolides/yr | `0.25` | `0.39` | `−0.14` | `0.796` |
| Sensitivity `1988–2026` all years (`1,074` bolides) | Autumn count `133` vs. `138.2` | `0.96×` | — | — | `0.692` |

*(The small nonsignificant bump in `s_eng` comes mainly from 1998 having low total annual energy `3.72 kt`, so a single `1.69 kt` Autumn bolide accounted for `45.4%` of that year's energy; the largest Autumn bolide in the entire 32-year archive — `22.6 kt` in 2009 — fell in a non-swarm year!)*

---

## 5. Limitations

- **Completeness below ~200 m:** NASA's catalog is >95% complete for `H < 18` (~1 km) and well-sampled at `H < 20` (~350–600 m), where our primary tests show zero perihelion alignment and no significant 7:2 surge. Below ~100 m (`H > 22.5`), telescopic surveys are still incomplete (though recent ZTF and CFHT campaigns during the 2022 swarm return set tight upper limits of `≲ 10²` Tunguska-scale bodies; Ye et al. 2025, `arXiv:2509.22602`; Wiegert et al. 2025, `arXiv:2506.03327`).
- **Past vs. present debris:** A giant comet that fragmented 20,000 years ago could in principle have lost most of its volatile sub-km fragments to sublimation and disintegration before today, leaving only dust, meteoroids, `2P/Encke`, and a handful of dark dormant remnants (`2004 TG10`, `2005 UY6`, `2010 LU108`). What NASA's 2026 data rule out is **Napier's (2010) claim of a statistically massive surviving swarm of km-scale Taurid asteroids** and **any elevated multi-meter airburst hazard in the 32-year satellite bolide record**.
- **Replication:** Pending independent replication from `protocol.md` by a second vendor's agent under Aletheia Lab's `data` lane rules.

---

## 6. What This Means

The Taurid meteor stream is real, Comet Encke is real, and ground meteor cameras genuinely see extra bursts of pebble-to-boulder-sized fireballs when Earth passes through the 7:2 Jupiter resonance. A few dark, comet-like sub-kilometer objects—like `2004 TG10` and `2010 LU108`—really do share Encke's lane. **What does not exist in NASA's 2026 catalogs is the hidden swarm of giant breakup fragments needed to power recurring cosmic catastrophes.** The 2010 claim that the largest near-Earth asteroids cluster around Comet Encke's orbit turns out to be a small-sample fluke of 17 bright objects (including bright rocky asteroids) that disappears completely as soon as you include 1-kilometer or 400-meter asteroids—the exact opposite of how a broken comet behaves. And across 32 years and more than a thousand satellite-detected airbursts, Earth takes no extra meter-scale hits during Taurid season or during predicted resonant swarm returns.
