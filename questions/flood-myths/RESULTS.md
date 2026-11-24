# Results — Do Flood Myths Cluster Where Land Drowned? (#44)

- **Question:** #44 (`lane:data`)
- **Date:** 2026-11-24
- **Protocol lock:** `protocol.lock` (`8efaaf8`, SHA-256 `84f99d5bcfc8…`), locked before running any motif–bathymetry regression or correlation. **Zero amendments.**
- **Authorship:** Designed, coded, and executed by AI (Antigravity / Google DeepMind) under the direction of Eugene Jhong. All datasets are open public archives; no specialist has reviewed this study yet.

## Answer

**No — worldwide, flood myths do not cluster where Ice Age land drowned.**

Across 927 oral traditions in Yuri Berezkin's global folklore catalog (396 coastal societies within 150 km of the sea, across 58 language families; 94 language families globally), coastal peoples living beside wide submerged continental shelves—where tens of thousands of square kilometres of land vanished under ~120 m of post-glacial sea-level rise—are **no more likely** to preserve non-biblical deluge stories than coastal peoples beside steep, narrow shelves where almost no land was lost.

- **Plain prevalence:** Non-biblical flood motifs appear in **37.9%** of all societies worldwide, and are actually slightly less common near the coast (**35.9%**, `n = 396`) than inland (**39.4%**, `n = 531`).
- **Coastal quartiles (drowned shelf area `−120 m` to `0 m` within 250 km):** From the narrowest shelves (`Q1`: 484–10,397 km²) to the widest drowned shelves (`Q4`: 39,598–187,061 km²), non-biblical flood prevalence is completely flat—**36.4% → 37.4% → 35.4% → 34.3%** (and mean motif share dips slightly from **1.07%** to **0.95%**).
- **Primary pre-registered model (Coastal M4, controlling for sampling effort, coast/river/seismic/climate exposure, and 58 language-family fixed effects):** Standardized non-biblical flood motif share vs. `log(1 + drowned shelf area)` gives **`β = −0.0100 SD`** (`p_cluster = 0.872`, `p_Conley_1000km = 0.845`, `p_perm = 0.846`). Removing every society with Noah motifs (`n = 340` Noah-free coastal groups) gives **`β = −0.0149 SD`** (`p_cluster = 0.819`, `p_Conley_1000km = 0.792`). Michalopoulos & Xue's external `flood_related` share gives **`β = −0.0321 SD`** (`p_Conley_1000km = 0.502`).
- **The method can see real environmental memory:** On the exact same 927 societies and language-family fixed-effects model, **earthquake motifs** track seismic proximity strongly (**`β = +0.157 SD`, `p_cluster = 0.0023`, `p_Conley_1000km = 0.00053`**), **sea motifs** track coastal proximity (`β = +0.087 SD`, `p_Conley_500km = 0.045`, `p_Conley_1000km = 0.052`), and the **negative control** (`fire_related` vs. drowned shelf) is null (`β = −0.070 SD`, `p = 0.23`).

This result meets the pre-registered **Null** verdict criterion cleanly.

---

## 1. Calibration Gate: Can Berezkin's Catalog Detect Environmental Memory?

Before testing drowned Ice Age coastlines, the locked protocol required positive and negative controls on the exact same societies and language-family fixed-effects specification:

| Check | Outcome | Predictor | Sample (`N`, lang. families) | `β` (SD per unit) | `p` (lang. cluster) | `p` (Conley 500 km) | `p` (Conley 1,000 km) | Result |
|---|---|---|---:|---:|---:|---:|---:|---|
| Positive Control 1 | `earthquake_related` (z) | Seismic proximity (`−ln dist`) | 927 (94) | **+0.1570** | **0.0023** | **0.00038** | **0.00053** | **Pass** |
| Positive Control 2 | `sea_related` (z) | Coastal proximity (`−ln dist`) | 927 (94) | **+0.0875** | 0.073 | **0.045** | 0.052 | Positive (borderline under 1,000 km Conley) |
| Negative Control | `fire_related` (z) | `log(1 + drowned 120 m, 250 km)` | 396 (58) | −0.0698 | 0.198 | 0.196 | 0.226 | **Pass (null)** |

Real geological hazards (earthquakes, replicating Michalopoulos & Xue 2021) leave a sharp, statistically decisive imprint across Berezkin's oral traditions even inside language families and with 1,000 km spatial-HAC standard errors. A global post-glacial flooding signal of comparable size (~0.15 SD per unit exposure) would have been easily detectable (Coastal M4 SE ≈ `0.051–0.062 SD`).

---

## 2. Primary Coastal Comparison (`dist_coast_km ≤ 150 km`)

Comparing coastal peoples directly against one another (rather than coastal against inland steppe or mountain peoples) isolates how much land actually drowned off their shore between the Last Glacial Maximum (~20 ka, −120 m sea level) and today.

### 2.1 Raw Quartiles of Drowned Continental Shelf (`−120 m` to `0 m`, within 250 km)

| Quartile | Drowned Shelf Area (km²) | Societies (`n`) | Any Non-Biblical Flood (%) | Mean Non-Biblical Share (%) | Mean MX `flood_related` (%) |
|---|---:|---:|---:|---:|---:|
| Q1 (narrowest) | 484 – 10,397 | 99 | **36.4%** | 1.07% | 1.22% |
| Q2 | 10,397 – 20,047 | 99 | **37.4%** | 1.13% | 1.41% |
| Q3 | 20,047 – 39,598 | 99 | **35.4%** | 1.05% | 1.27% |
| Q4 (widest) | 39,598 – 187,061 | 99 | **34.3%** | 0.95% | 1.04% |

There is no upward gradient anywhere across the four quartiles.

### 2.2 Progressive Regression Ladder (M1 → M4)

Coefficients report the effect of a +1 log-unit increase in drowned continental shelf area (`log_drowned_120m_250km`) on each pre-registered outcome:

| Sample & Outcome | Model | `n` (clusters) | `β` | SE (cluster) | `p` (cluster) | SE (Conley 1,000 km) | `p` (Conley 1,000 km) | `p` (within-cont. perm.) | Residual Moran's *I* |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **Coastal: `nb_flood_share_z`** | M1 (sampling) | 396 (58) | +0.0213 | 0.0569 | 0.710 | 0.0521 | 0.683 | — | +0.183 |
| **Coastal: `nb_flood_share_z`** | M2 (+ geophys.) | 396 (58) | +0.0413 | 0.0539 | 0.447 | 0.0481 | 0.390 | — | +0.147 |
| **Coastal: `nb_flood_share_z`** | M3 (+ cont. FE) | 396 (58) | +0.0590 | 0.0520 | 0.262 | 0.0507 | 0.244 | 0.271 | +0.128 |
| **Coastal: `nb_flood_share_z`** | **M4 (+ lang. FE)** | **396 (58)** | **−0.0100** | **0.0621** | **0.872** | **0.0513** | **0.845** | **0.846** | **+0.127** |
| Coastal: `any_nb_flood` (prob.) | M3 (+ cont. FE) | 396 (58) | +0.0085 | 0.0214 | 0.692 | 0.0218 | 0.695 | 0.690 | +0.173 |
| Coastal: `any_nb_flood` (prob.) | **M4 (+ lang. FE)** | **396 (58)** | **−0.0138** | **0.0293** | **0.640** | **0.0213** | **0.517** | **0.560** | **+0.134** |
| Coastal: MX `flood_related_z` | M3 (+ cont. FE) | 396 (58) | +0.0446 | 0.0509 | 0.384 | 0.0482 | 0.354 | 0.363 | +0.121 |
| Coastal: MX `flood_related_z` | **M4 (+ lang. FE)** | **396 (58)** | **−0.0321** | **0.0600** | **0.594** | **0.0479** | **0.502** | **0.512** | **+0.114** |
| **Noah-free coastal: `nb_flood_share_z`** | **M4 (+ lang. FE)** | **340 (56)** | **−0.0149** | **0.0648** | **0.819** | **0.0565** | **0.792** | **0.796** | **+0.087** |
| Noah-free coastal: `any_nb_flood` | **M4 (+ lang. FE)** | **340 (56)** | **−0.0016** | **0.0291** | **0.957** | **0.0226** | **0.944** | **0.962** | **+0.161** |
| Noah-free coastal: MX `flood_related_z` | **M4 (+ lang. FE)** | **340 (56)** | **−0.0190** | **0.0647** | **0.771** | **0.0514** | **0.712** | **0.720** | **+0.085** |
| Global all: `nb_flood_share_z` | **M4 (+ lang. FE)** | **927 (94)** | **−0.0117** | **0.0866** | **0.893** | **0.0531** | **0.826** | — | **+0.134** |
| Global all: MX `flood_related_z` | **M4 (+ lang. FE)** | **927 (94)** | **−0.0617** | **0.0825** | **0.456** | **0.0494** | **0.211** | — | **+0.141** |

Every single specification in the full ladder—coastal, Noah-free coastal, and global; with or without fixed effects; across all three flood outcomes—is statistically indistinguishable from zero, and every M4 language-family fixed-effects estimate is slightly negative. The 95% confidence interval for the primary M4 coastal slope (`−0.11` to `+0.09 SD` per log-unit of drowned shelf) rules out any large global effect.

---

## 3. Pre-Registered Exposure Sensitivity Checks (Coastal M4)

Does the null depend on choosing −120 m instead of the final Holocene rise (−60 m, ~12–7 ka), or 250 km instead of 500 km, or absolute area instead of shelf fraction?

| Exposure Definition (Coastal `n = 396`, M4 lang. FE) | `nb_flood_share_z` `β` (`p_Conley_1000`) | MX `flood_related_z` `β` (`p_Conley_1000`) | `any_nb_flood` `β` (`p_Conley_1000`) |
|---|---:|---:|---:|
| Primary: `log(1 + drowned −120 m, 250 km)` | −0.0100 (`0.845`) | −0.0321 (`0.502`) | −0.0138 (`0.517`) |
| Holocene window: `log(1 + drowned −60 m, 250 km)` | −0.0170 (`0.709`) | −0.0405 (`0.343`) | −0.0162 (`0.459`) |
| Wider radius: `log(1 + drowned −120 m, 500 km)` | −0.0826 (`0.218`) | −0.1034 (`0.079`) | +0.0054 (`0.826`) |
| Shelf fraction of ocean: `drowned_frac_ocean_250km` | **−0.1626 (`0.0185`)** | **−0.1711 (`0.0048`)** | −0.0311 (`0.263`) |

No exposure metric turns positive. Notably, the **shelf-fraction** metric (shallow drowned shelf as a share of nearby ocean) is **significantly negative** (`p = 0.0185` on non-biblical flood share; `p = 0.0048` on `flood_related`). A plausible geophysical reason is that steep, deep-water subduction margins (around the Pacific Rim and Indonesia) have very small shallow-shelf fractions and high exposure to tsunamis and tectonic coastal hazards, whereas broad, gentle passive margins (like the North Sea or Beringia) lost land gradually at metres per generation rather than in a sudden wall of water.

---

## 4. Regional Breakdown & the Australia / Sahul Check

Testing each continent separately (Coastal M2 with sampling + geophysical controls, `500 km` Conley SEs) checks whether a strong regional signal is hidden inside the global null:

| Continent (Coastal `≤ 150 km`) | `n` | Any Non-Biblical Flood | Median Drowned Shelf (km²) | M2 `β` (`nb_flood_share_z`) | `p` (Conley 500 km) | Spearman `ρ` |
|---|---:|---:|---:|---:|---:|---:|
| Africa | 33 | 15.2% | 18,718 | −0.128 | 0.054 | −0.36 |
| Asia | 130 | 34.6% | 29,059 | +0.085 | 0.066 | +0.08 |
| Europe | 37 | 24.3% | 37,261 | −0.048 | 0.493 | −0.17 |
| North America | 140 | 41.4% | 18,211 | +0.123 | 0.329 | +0.03 |
| Oceania | 25 | 24.0% | 9,235 | −0.282 | 0.053 (`flood_rel` **0.039**) | −0.38 |
| South America | 31 | 61.3% | 16,511 | +0.151 | 0.381 | +0.24 |
| *Australia / Sahul subset* | *16* | *18.8%* | *17,023* | *—* | *—* | *−0.41* |

No continent reaches `p < 0.05` in the positive direction; Asia (`p = 0.066`), North America (`p = 0.329`), and South America (`p = 0.381`) are weak and nonsignificant, while Africa, Europe, and Oceania tilt negative.

**Important caveat on Australia/Sahul:** In Berezkin's global catalog, only 16 coastal Aboriginal Australian groups are coded, with a low prevalence of universal-deluge motifs (`18.8%`) and a negative Spearman rank correlation (`ρ = −0.41`). That does **not** contradict Nunn & Reid (2016), who studied 21 specific Aboriginal Australian oral histories naming particular submerged bays, islands, and shoals (such as Kangaroo Island or Port Phillip Bay). Local place-name inundation memories are a different phenomenon from global "world-ending Great Flood" myth motifs (`c2`–`c14`), and Berezkin's catalog is designed to index widespread mythological motifs rather than site-specific coastal placelore.

---

## 5. Limits & Verification

1. **Synthetic unit tests:** `questions/flood-myths/analysis/test_flood_myths.py` passed `3/3` tests verifying exact spherical cell-area integration, coastal distance, Conley spatial-HAC SEs under planted spatial autocorrelation, and CR1 language-family clustered SEs.
2. **Modern centroids vs. Ice Age homelands:** Ethnographic coordinates record where peoples lived in recent centuries, not necessarily where their ancestors lived 10,000–15,000 years ago. Large Holocene migrations (Bantu, Austronesian, Indo-European, Eskimo-Aleut, Na-Dene) blur any ancient local coastline signal—which is itself a real reason global myth geography should not preserve 12,000-year-old shorelines cleanly.
3. **Glacial isostatic adjustment (GIA):** ETOPO 2022 −120 m / −60 m bathymetry approximates eustatic sea-level rise and does not model local crustal rebound in formerly glaciated high latitudes (e.g., Fennoscandia, Hudson Bay, where relative sea level *fell* rather than rose). Still, dropping high latitudes (`|lat| < 50°`) or examining tropical shelves (Sundaland, Sahul, East China Sea, Africa) produces the same null pattern.
4. **Universal deluge vs. local coastal memory:** This study tests the global "shared memory of post-glacial drowning" explanation for *world-deluge myths*. It does not rule out that particular long-resident coastal peoples (such as Aboriginal Australians on the Sahul shelf) preserved local stories about specific islands or bays going underwater.
5. **Reproducibility & pending replication:** All scripts live in `questions/flood-myths/analysis/` (`fetch_data.py`, `run_flood_myths.py`, `test_flood_myths.py`, `make_figures.py`) with pinned inputs in `MANIFEST.md`. Independent replication by a second vendor's agent working from `protocol.md` alone has not yet been run.

---

## What This Means

Great Flood stories are common across the world—nearly four in ten traditional societies in Berezkin's catalog have a non-biblical deluge myth—and it is tempting to read them as humanity's collective memory of the Ice Age oceans rising 120 metres to swallow coastal plains like Doggerland, Sundaland, and Beringia. When we test that prediction across 927 cultures using global seafloor elevation maps, the pattern is not there. Coastal peoples living beside the widest drowned shelves are no more likely to tell flood myths than coastal peoples beside steep cliffs where almost no land vanished—or, for that matter, than people living far inland. The same catalog easily picks up real environmental memory when it exists (earthquake myths cluster strongly near fault zones), so the missing flood signal is unlikely to be a blind spot of the dataset. That does not disprove local, place-specific coastal memories like those documented in Australia; it does mean that worldwide Great Flood myths are far better explained by river floods, storms, tsunamis, storytelling traditions, and cultural diffusion than by a global memory of drowned Ice Age land.
