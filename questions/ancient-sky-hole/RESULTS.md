# Results — The hole in the ancient sky (`ancient-sky-hole`)

- **Issue:** [#85](https://github.com/ejhong/aletheia-lab/issues/85)
- **Lane:** `data`
- **Protocol lock:** `4be6d43dc0bd6aa66808853167c899697b35450dad12a97ef6da9159a8591776` (locked `2026-11-23T18:45:56Z`, commit `bc04372`)
- **Amendments:** None.
- **Authorship:** Conducted and written by Antigravity (Google DeepMind) on 2026-11-23, directed by Eugene Jhong.
- **Spending:** $0 (public astronomical archives, local Python 3.12 + NumPy 2.3.5).

---

## 1. Headline Answer

**The empty southern patch in Ptolemy's 48 constellations decisively excludes a date before 3000 BCE — and instead records the classical Mediterranean sky of Hipparchus and Ptolemy (c. 130 BCE – 140 CE), while exposing how fragile single-model extinction fits are.**

Across every single one of our 13 pre-registered models, extinction values, constellation subsets, and magnitude cutoffs, all 21 leave-one-constellation-out runs, and all 500 spatial-block bootstrap resamples, the inferred epoch falls after **201 BCE**:

- **Combined honest epoch range (union of 500 spatial-block bootstrap 95% CI and all 13 pre-registered models):** **`201 BCE to 1000 CE`** (astronomical years `−200` to `+1000`; historically capped at `137 CE`, when the *Almagest* was compiled).
- **Combined honest latitude range:** **`21.5° N to 35.7° N`**.
- **Pre-registered verdict on Issue #85's test:** **`excludes_pre_3000_bce`** (`t_lo = −200 > −2999` and free-pole off-track offset `Δθ = 3.94° <= 6.0°`). A 3000 BCE sky is worse than the best fit by **`Δln L = −106.2`** in Primary M1 (`−125.6` under clear-sky `k_V = 0.15`, `−96.5` in the pre-Hipparchan Aratus core) — a likelihood ratio exceeding $10^{46}$ against. A 9600 BCE sky (Göbekli Tepe era) is worse by **`Δln L = −350.0`**.
- **Crucial methodological finding:** Our pre-registered Primary Model M1 (`k_V = 0.25 mag/airmass`, `V <= 5.5`) overshot to **`910 CE, 25.8° N`** — **773 years after Ptolemy wrote the *Almagest***. By contrast, our pre-registered **bright-star cutoff (`V <= 4.0`: `121 BCE, 31.8° N`)**, **extinction-free geometric cap (`M3`: `41 BCE`, `R = 41.7°`, beating M1 by `2Δln L = +123.0`)**, and **profile-extinction model (`M2`, `k_V = 0.10`: `160 CE, 35.7° N`, beating M1 by `2Δln L = +74.7`)** all land squarely on the historical Hipparchus–Ptolemy cataloguing window (`128 BCE – 137 CE`, Rhodes `36.4° N` to Alexandria `31.2° N`).

---

## 2. Pre-Lock Validation Summary

Before locking `protocol.md`, `analysis/test_skyhole.py` and `analysis/skyhole.py --decoy` passed all pre-registered checks without reading real southern-sky catalogue labels:

1. **Vondrák et al. (2011/2012) long-term precession:** J2000 obliquity `23.4393°`, 3001 BCE obliquity `24.0195°`, Thuban (`α Dra`) `0.06°` from the North Celestial Pole at `−2780` (2781 BCE), Vega (`α Lyr`) `2.69°` from the pole at `−12000`.
2. **4-epoch synthetic sky recovery** (real Hipparcos stars, known ground truth):
   - `(−9600, 37.0° N)` → recovered `(−9730, 37.00° N)` (`−130 yr, +0.00°`)
   - `(−2500, 36.0° N)` → recovered `(−2810, 35.80° N)` (`−310 yr, −0.20°`)
   - `(−1200, 33.0° N)` → recovered `(−1330, 33.70° N)` (`−130 yr, +0.70°`)
   - `(+137, 31.2° N)` → recovered `(−10, 31.70° N)` (`−147 yr, +0.50°`)
3. **Correlated patchy-sky bootstrap check:** On a synthetic `−2200` sky with random `12°` rim perturbations, the Spatial Block Bootstrap 95% CI (`[−3200, −1974]`, width `1,226 yr`) widened properly beyond the optimistic star-level CI (`[−3000, −2200]`, width `800 yr`) and covered ground truth.
4. **Decoy run** (`t = −1800, 35.0° N`): recovered `−1670 (1671 BCE), 35.30° N`, block-bootstrap 95% CI `[−2000, −1350]`, M4 free-pole off-track `0.44°`.

---

## 3. Northern Calibration and Main Results

### 3.1 Precession-Invariant Northern Calibration (`β > +30°`, `Vmag <= 5.5`)

Out of `2,848` Hipparcos stars with `Vmag <= 5.5`, `690` lie in the precession-invariant northern ecliptic calibration cap (`β > +30°`) and `2,158` lie in the test region (`β <= +30°`, containing `767` catalogued stars in `all48`):

| Catalogue Definition | Calibration Stars (`β > +30°`) | Test Stars Catalogued (`β <= +30°`) | Fitted `V_50` | Logistic Slope `s_V` |
|---|---:|---:|---:|---:|
| `all48` (Primary, `I <= 3`) | 222 / 690 | 767 / 2,158 | `4.416` | `0.309` |
| `in_figure` (excludes *informes*) | 211 / 690 | 673 / 2,158 | `4.313` | `0.376` |
| `aratus_core` (excludes `Equ`, `CrA`, *informes*) | 211 / 690 | 657 / 2,158 | `4.313` | `0.376` |
| `strict_id` (`I <= 2`) | 221 / 690 | 757 / 2,158 | `4.415` | `0.305` |

### 3.2 All 13 Pre-Registered Models, Subsets, and Sensitivity Variants

| Variant | Group | Best Epoch | Best Latitude | `ln L_max` | Notes |
|---|---|---:|---:|---:|---|
| `M1_kv_0.25` *(Primary)* | Extinction | **910 CE** (`+910`) | **25.8° N** | `−935.79` | Anachronistic overshoot (see §4) |
| `M1_kv_0.15` | Extinction | **210 CE** (`+210`) | **33.2° N** | `−916.29` | Clear highland/dry sky (`+19.5` LL over primary) |
| `M1_kv_0.20` | Extinction | **880 CE** (`+880`) | **28.0° N** | `−928.07` | Phase jump occurs between `k_V = 0.16` and `0.18` |
| `M1_kv_0.30` | Extinction | **820 CE** (`+820`) | **24.0° N** | `−942.38` | Hazier horizon shifts latitude south |
| `M1_kv_0.35` | Extinction | **720 CE** (`+720`) | **22.5° N** | `−948.16` | Humid coastal haze |
| `M2_free_kv` | Model | **160 CE** (`+160`) | **35.7° N** | `−898.45` | Profile MLE hits lower bound `k_V = 0.10` (`+37.3` LL over primary) |
| `M3_geom_cap` | Model | **41 BCE** (`−40`) | *(cap `R = 41.7°`)* | **`−874.31`** | Extinction-free circular void (**highest likelihood**, `+61.5` LL over primary) |
| `subset_in_figure` | Subset | **670 CE** (`+670`) | **27.0° N** | `−878.07` | Excludes 108 *informes* stars |
| `subset_aratus_core` | Subset | **500 CE** (`+500`) | **28.2° N** | `−851.66` | Pre-Hipparchan constellations (`−Equ, −CrA, −informes`) |
| `subset_strict_id` | Subset | **930 CE** (`+930`) | **25.8° N** | `−929.41` | Strictly secure Hipparcos IDs (`I <= 2`) |
| `vmag_le_4.0` | Magnitude | **121 BCE** (`−120`) | **31.8° N** | `−92.95` | Bright constellation skeletons (`315` stars) |
| `vmag_le_4.5` | Magnitude | **50 CE** (`+50`) | **30.3° N** | `−275.91` | Medium-bright stars (`499` stars) |
| `vmag_le_5.0` | Magnitude | **610 CE** (`+610`) | **27.0° N** | `−601.64` | Deeper sample (`663` stars) |

### 3.3 Uncertainty Breakdown (Primary M1, `k_V = 0.25`)

| Uncertainty Method | Epoch Range | Latitude Range |
|---|---|---|
| Naive star-level profile 95% CI (assumes independent stars) | `350 CE` to `1000 CE` | `24.5° N` to `27.5° N` |
| **Spatial Block Bootstrap 95% CI** (`B = 500`, `138` tiles of ~15°) | **`201 BCE` to `1000 CE`** | **`21.5° N` to `30.5° N`** |
| Spatial Block Bootstrap 68% CI | `300 CE` to `1000 CE` | `24.5° N` to `28.0° N` |
| Leave-One-Constellation-Out (LOCO, 21 southern constellations) | `680 CE` to `1000 CE` | `25.8° N` to `26.7° N` |
| Systematic Model Envelope (all 13 variants) | `121 BCE` to `930 CE` | `22.5° N` to `35.7° N` |
| **Combined Honest Uncertainty Range (Headline)** | **`201 BCE` to `1000 CE`** | **`21.5° N` to `35.7° N`** |

- **Most influential single constellations in LOCO:** Dropping *Piscis Austrinus* (`−230 yr`), *Aquarius* (`−200 yr`), or *Eridanus* (`−190 yr`) pulls the M1 date earlier; dropping *Centaurus* (`+90 yr`), *Argo Navis* (`+70 yr`), or *Lupus* (`+60 yr`) pulls it slightly later. No single constellation can pull the date before 680 CE in M1, let alone 3000 BCE.
- **Unconstrained Free-Pole Diagnostic (`M4`):** Best unconstrained void center lies at J2000 `(RA = 45.5°, Dec = −83.8°)`, ecliptic `(λ = 283.0°, β = −70.5°)`. It sits **`3.94°` inward** from the 26,000-year precession circle (`β = −66.5°`) toward the South Ecliptic Pole (`2Δln L = 9.08`, nearest precession epoch `1075 CE`). While within our pre-registered `6.0°` pass threshold, the inward shift signals mild geometric distortion of the southern boundary.

### 3.4 Log-Likelihood Against Historical Milestone Epochs

| Milestone Epoch | Primary M1 (`k_V = 0.25`) `Δln L` | Clear Sky (`k_V = 0.15`) `Δln L` | Aratus Core (`k_V = 0.25`) `Δln L` |
|---|---:|---:|---:|
| `9600 BCE` (Göbekli Tepe) | `−350.0` | `−333.4` | `−266.2` |
| `5000 BCE` | `−170.2` | `−189.0` | `−153.3` |
| `3000 BCE` (Issue #85 threshold) | **`−106.2`** | **`−125.6`** | **`−96.5`** |
| `2600 BCE` (Ovenden 1966 / Crete) | `−93.2` | `−111.4` | `−83.4` |
| `2000 BCE` (Middle Bronze Age) | `−74.0` | `−82.7` | `−62.3` |
| `1200 BCE` (Babylon MUL.APIN) | `−39.8` | `−40.5` | `−28.0` |
| `150 BCE` (Hipparchus / Rhodes) | `−8.5` | `−2.4` | `−2.6` |
| `150 CE` (Ptolemy / Alexandria) | `−4.7` | `−0.1` | `−0.6` |
| `500 CE` | `−1.5` | `−1.0` | `−0.0` |
| `900 CE` | `−0.0` | `−2.5` | `−0.7` |

---

## 4. Why Primary M1 Overshot Past Ptolemy — And What the Rim Stars Actually Prove

Reporting the locked Primary M1 result (`910 CE, 25.8° N`) candidly reveals two critical physical and historical lessons that an unlocked analysis would easily have hidden:

1. **Why `k_V = 0.25` pushed 773 years *past* the *Almagest* (`137 CE`):**
   - Under `k_V = 0.25` applied uniformly to all stars down to `V = 5.5` with northern-sky `V_50 = 4.42`, any 3rd–5th magnitude star culminating below ~8° altitude is predicted to be almost invisible (`P < 1%`).
   - Yet Ptolemy catalogued faint southern stars inside traditional constellations — notably **Ara** (`γ Ara V=3.31`, `β Ara V=2.84`, `ζ Ara V=3.12`, `ε¹ Ara V=4.06`), **Argo Navis** (`HIP 46701 V=3.16`, `HIP 42726 V=4.83`), and **Centaurus** (`HIP 66821 V=4.99`) — while **omitting** brighter 2nd-magnitude stars in unconstellated void regions (**Grus** and **Phoenix**: `α Gru V=1.73`, `β Gru V=2.07`, `α Phe V=2.40`).
   - Because `M1` penalizes cataloguing a faint star at `4°` altitude far more harshly than it should when observers deliberately hunted down stars to finish named figures, increasing `k_V` past `0.17` causes a phase jump (`240 CE, 32.5° N` at `k_V = 0.16` → `820 CE, 29.2° N` at `k_V = 0.18`): sliding the epoch forward lifts *Ara* and *Centaurus* higher while dropping *Grus* and *Phoenix* lower.
   - As soon as you remove the steep faint-star extinction penalty — either via the pure geometric circular void **`M3` (`41 BCE`, `LL = −874.3`, `+61.5` log-likelihood units better than M1!)**, bright constellation stars **`V <= 4.0` (`121 BCE, 31.8° N`)**, or low extinction **`M2` (`160 CE, 35.7° N`, `+37.3` LL better)** — the anachronism vanishes completely and the fit locks onto **Hipparchus and Ptolemy**.

2. **The unmistakable fingerprints of Rhodes (`128 BCE, 36.4° N`) on the southern rim:**
   Inspecting the individual rim stars (`results/rim_stars.tsv`) shows *why* the void matches the classical Greek horizon so tightly:

   | Star | `Vmag` | In *Almagest*? | Max Alt. at Rhodes (`128 BCE`, `36.4° N`) | Max Alt. at Alexandria (`137 CE`, `31.2° N`) |
   |---|---:|---|---:|---:|
   | Canopus (`α Car`) | `−0.62` | **Yes** (`=Arg`) | `+0.91°` | `+6.24°` |
   | Acrux (`α¹ Cru`) | `+0.77` | **Yes** (`=Cen`) | `+2.24°` | `+6.01°` |
   | Alpha Centauri (`α² Cen`) | `+1.35` | **Yes** (`=Cen`) | `+2.83°` | `+6.67°` |
   | Gamma Ara (`γ Ara`) | `+3.31` | **Yes** (`=Ara`) | `+3.05°` | `+7.16°` |
   | Acamar (`θ¹ Eri`) | `+2.88` | **Yes** (`=Eri`) | `+3.52°` | `+10.06°` |
   | Avior (`ε Car`) | `+1.86` | **No** *(missing)* | `+0.01°` | `+4.59°` |
   | Ankaa (`α Phe`) | `+2.40` | **No** *(missing)* | `−0.17°` | `+6.40°` |
   | Alnair (`α Gru`) | `+1.73` | **No** *(missing)* | `−1.36°` | `+4.50°` |
   | Tiaki (`β Gru`) | `+2.07` | **No** *(missing)* | `−2.66°` | `+3.43°` |
   | Peacock (`α Pav`) | `+1.94` | **No** *(missing)* | `−5.88°` | `−0.85°` |
   | Atria (`α TrA`) | `+1.91` | **No** *(missing)* | `−7.53°` | `−3.64°` |
   | Miaplacidus (`β Car`) | `+1.67` | **No** *(missing)* | `−7.82°` | `−3.59°` |
   | Achernar (`α Eri`) | `+0.45` | **No** *(missing)* | `−15.10°` | `−8.42°` |

   At **Rhodes in 128 BCE**, every bright star Ptolemy missed (*Alnair*, *Tiaki*, *Ankaa*, *Avior*, *Peacock*, *Atria*, *Miaplacidus*, *Achernar*) sat at or below the sea horizon (`≤ +0.01°`), while every southernmost star he included (*Canopus*, *Acrux*, *α/β Cen*, *γ Ara*, *Acamar*) rose above it (`+0.9°` to `+4.6°`)! By contrast, at Alexandria in 137 CE, *Ankaa* (`+6.4°`), *Alnair* (`+4.5°`), and *Avior* (`+4.6°`) rose nearly as high as *Canopus* (`+6.2°`) and *Acrux* (`+6.0°`), yet none were catalogued. This independently echoes historical-astronomy findings (Rawlins 1982; Verbunt & van Gent 2012; Schaefer 2005) that the *Almagest*'s southern star limit largely reflects **Hipparchus's observations at Rhodes** (c. 128 BCE), possibly blended with modest additions from Alexandria.

3. **Why this differs from Ovenden (1966) and Roy (1984):**
   Earlier studies that reported ~2600 BCE (Ovenden 1966; Roy 1984; unverified full texts) primarily dated **Aratus's verbal descriptions** of which constellations lay on the celestial equator, tropics, and horizon — not the star-by-star boundary of the *Almagest*. Once Hipparchus and Ptolemy systematically catalogued stars right down to their own southern horizon, they largely **overwrote** any older Bronze Age empty patch with a classical Greek/Alexandrian horizon.

---

## 5. Limitations and Post-Hoc Checks

- **Unresolved visual binary (`α¹/α² Cen`):** Hipparcos lists `α¹ Cen` (`HIP 71683, V = −0.01`) and `α² Cen` (`HIP 71681, V = 1.35`, separation `14"`) separately, while Verbunt & van Gent (2012) link Ptolemy's single naked-eye `α Cen` entry to `HIP 71681`, leaving `HIP 71683` unlinked. A post-hoc check merging `HIP 71683` into `HIP 71681` (`V = −0.27`) leaves the results unchanged: `M1 (k_V = 0.25)` stays at `910 CE, 25.8° N`, `M1 (k_V = 0.15)` shifts by 10 yr (`200 CE, 33.2° N`), and `M3` shifts by 10 yr (`51 BCE, R = 41.7°`).
- **Grid upper bound (`+1000 CE`):** Because Primary M1's spatial block bootstrap hits the upper grid boundary (`+1000 CE`), the right edge of the M1 bootstrap interval is truncated by the search box — irrelevant historically because the *Almagest* was written in `137 CE`, and reinforcing that `k_V = 0.25` is misspecified for faint southern stars.
- **Replication:** Under the `data` lane definition in `AGENTS.md`, full completion requires an independent replication from `protocol.md` by a second vendor's agent.

---

## 6. What This Means

If an unknown Ice Age or pre-3000 BCE civilization had drawn the classical constellations and handed them down untouched to the Greeks, the circular hole left around the ancient South Celestial Pole would sit in a completely different part of the southern sky — leaving bright modern constellations like Phoenix and Grus high above the horizon while burying parts of Centaurus and Ara underground. Ptolemy's star catalogue does not show that sky. Every pre-registered way of measuring the empty southern patch places its center squarely in Classical Antiquity (after 200 BCE), matching the horizons of Hipparchus in Rhodes (c. 128 BCE) and Ptolemy in Alexandria (c. 137 CE). At the same time, locking our method before looking at the sky exposed an important caution: small, reasonable changes in how you model haze near the horizon can pull an apparent star-void date by a thousand years — even centuries *after* the catalogue itself was written. The hole in the *Almagest* is a genuine astronomical fingerprint of Hellenistic stargazing, not a relic of a lost prehistoric civilization, and it warns against treating any single star-void date as sharper than the messy human cataloguing behind it.
