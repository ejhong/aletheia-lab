---
# To update this page, edit this file and push to main; the site rebuilds itself.
# The interactive observatory plates are made by questions/ancient-sky-hole/analysis/make_figures.py from locked results.
summary: Ptolemy's 48 classical constellations leave a circular hole around the ancient South Celestial Pole. Because the pole drifts over 25,772 years, does that empty patch date the constellations before 3000 BCE, or to Classical Antiquity?
verdict: Excludes pre-3000 BCE; records the Classical Greco-Alexandrian sky (with wide model sensitivity)
result: Across all 13 pre-registered models, extinction settings, magnitude limits, and constellation subsets—plus all 500 spatial-block bootstrap resamples—the empty southern patch in Ptolemy's Almagest falls after 201 BCE (combined honest range 201 BCE–1000 CE, 21.5°–35.7° N), rejecting a 3000 BCE sky by Δln L = −106.2 (odds > 10^46 : 1). Bright stars (V ≤ 4.0: 121 BCE, 31.8° N), an extinction-free geometric circle (41 BCE), and a free-extinction model (160 CE, 35.7° N) converge on Hipparchus and Ptolemy, while our fixed-extinction primary model overshot to 910 CE—showing how sensitive star-void dates are to horizon haze.
dek: Ancient star-makers could not draw constellations in the part of the southern sky that never rose above their horizon. As Earth's axis wobbles over 25,772 years, that blank circle drifts across the stars. We locked an astronomical visibility test on Ptolemy's Almagest and ESA's Hipparcos catalogue to see when and where the hole points—and how honest the error bars really are.
updated: 2026-11-23
---

> **Where things stand, 23 November 2026.** Primary locked analysis finished (run by Antigravity / Google DeepMind, directed by Eugene; awaiting an independent replication from the written plan by a second AI vendor to complete the `data` lane). By the pre-registered decision rule, the empty southern patch **excludes an origin before 3000 BCE** (`201 BCE` earliest bound across 500 spatial-block bootstraps and all 13 locked models).

## What we figured out {menu: Findings}

Look at a map of the 48 classical constellations handed down in Claudius Ptolemy's *Almagest* (c. 137 CE), and an eerie blank disc stares back from the deep south. The constellations we inherited—Orion, Argo Navis, Centaurus, Ara, Eridanus—wrap snugly around an empty patch where modern atlases place Phoenix, Grus, Pavo, Tucana, Hydrus, and the Southern Triangle. Those missing regions were not named by Europeans until Dutch navigators sailed around the Cape of Good Hope in 1595–1597.

Because Earth's spin axis slowly precesses around a 23.4° circle every ~25,772 years, the South Celestial Pole was in a different spot among the stars thousands of years ago. A famous astronomical side-channel asks: **can that blank circle act as a prehistoric timestamp?** If an unknown Ice Age or pre-3000 BCE civilization drew the sky and handed it down untouched, the hole should be centered on the pole of their era.

We cross-matched all **1,028 entries** of Ptolemy's *Almagest* (Verbunt & van Gent 2012) against **15,537 modern stars** from ESA's Hipparcos catalogue, calibrated Ptolemy's brightness cutoff strictly on the precession-invariant northern ecliptic sky (`β > +30°`), and locked every precession equation (Vondrák et al. 2011), atmospheric extinction model, spatial-block bootstrap, and decision rule before looking at a single southern-sky fit.

{{figure: ancient-sky-hole/tiles}}

{{figure: ancient-sky-hole/verdict}}

Four things came out.

1. **A pre-3000 BCE sky is overwhelmingly excluded.** Every single one of all 13 pre-registered models, all 21 leave-one-constellation-out jackknife runs, and all 500 spatial-block bootstrap draws lands **after 201 BCE**. At **3000 BCE**, the empty patch is misaligned with the southern horizon by **`Δln L = −106.2`** in Primary M1 (**`−125.6`** under clear skies, **`−96.5`** in the pre-Hipparchan Aratus core)—odds of more than **10^46 to 1 against**. At **9600 BCE** (the era of Göbekli Tepe), the mismatch explodes to **`Δln L = −350.0`**.
2. **The hole in the *Almagest* records the Classical Greco-Alexandrian sky—not a Bronze Age time capsule.** Strip away overly steep faint-star extinction assumptions and three independent pre-registered tests snap straight onto Hipparchus (Rhodes, 36.4° N, c. 128 BCE) and Ptolemy (Alexandria, 31.2° N, c. 137 CE):
   - Bright constellation-defining stars (`V ≤ 4.0`): **`121 BCE`, `31.8° N`**.
   - Pure extinction-free circular void (`M3`, highest log-likelihood of all models at `LL = −874.3`, beating M1 by `2Δln L = +123.0`): **`41 BCE`**, void radius **`41.7°`**.
   - Free-extinction profile (`M2`, `k_V = 0.10`, beating M1 by `2Δln L = +74.7`): **`160 CE`, `35.7° N`**.
3. **Individual rim stars carry the unmistakable fingerprint of Rhodes in 128 BCE.** At Rhodes (`36.4° N`, `128 BCE`), every one of Ptolemy's southernmost landmark stars—Canopus (`+0.9°`), Acrux (`+2.2°`), Alpha Centauri (`+2.8°`), Gamma Arae (`+3.1°`), and Acamar (`+3.5°`)—rose above the sea horizon, while **11 of the 12 brightest missing stars** (including Alnair, Tiaki, Ankaa, Peacock, Atria, Miaplacidus, and Achernar) never rose at all. At Alexandria in 137 CE, four of those missing stars rose 3.4°–6.4° high yet stayed uncatalogued—echoing historical studies arguing that Ptolemy's southern limit largely inherits Hipparchus's sky at Rhodes.
4. **Locking the plan caught a major methodological trap in real time.** Our pre-registered primary model (`M1`, fixed `k_V = 0.25 mag/airmass`, all stars down to `V = 5.5`) overshot to **`910 CE, 25.8° N`**—**773 years after the *Almagest* was written**. Why? Because ancient astronomers selectively hunted down faint 3rd–5th magnitude stars low on the horizon *inside* named figures (Ara, Argo, Centaurus) while leaving brighter 2nd-magnitude stars unrecorded in blank sky (Grus, Phoenix). Forcing a uniform haze penalty onto that asymmetric rim pushes the optimizer south and centuries into the future.

## Spin the ancient sky yourself {menu: Time machine}

Before reading another table, look directly at the stars. Drag the **Epoch** slider below—or press **Orbit Precession**—to carry Earth's South Celestial Pole around its 25,772-year circle. Watch the glowing copper horizon ring sweep across Ptolemy's golden constellations and lock cleanly onto the sapphire-blue void right around **Hipparchus (128 BCE)** and **Ptolemy (137 CE)**—and watch how badly it misses at **3000 BCE** or **9600 BCE**.

{{figure: ancient-sky-hole/sky_dome}}

## Where the likelihood points—and why extinction shifts it {menu: Likelihood map}

Earlier studies using the southern sky void (Ovenden 1966; Roy 1984; Schaefer 2002, 2006) often disagreed by centuries or millennia, partly because some analyzed *verbal* constellation descriptions in Aratus's *Phaenomena* rather than the *Almagest* star list, and partly because single-model error bars treat every star as an independent coin flip.

The interactive observatory map below shows our exact locked 2D likelihood surface across epoch and observer latitude. Toggle between **Clear Sky (`k_V = 0.15`)**, **Primary M1 (`k_V = 0.25`)**, **Aratus Core** (excluding Equuleus, Corona Australis, and all 108 *informes* stars outside the figures), and **In-Figure Only**—and flip on **Deep Time** to see how utterly empty the probability landscape is before 3000 BCE.

{{figure: ancient-sky-hole/contour}}

| Pre-registered variant | Group | Best epoch | Best latitude | `ln L_max` | What it tests |
|---|---|---:|---:|---:|---|
| `M1_kv_0.25` *(Primary)* | Extinction | **910 CE** | **25.8° N** | `−935.8` | Fixed haze `k_V = 0.25`, all 48, `V ≤ 5.5` *(anachronistic overshoot)* |
| `M1_kv_0.15` | Extinction | **210 CE** | **33.2° N** | `−916.3` | Clear dry sky (`+19.5` LL over primary) |
| `M1_kv_0.20` | Extinction | **880 CE** | **28.0° N** | `−928.1` | Phase jump occurs between `k_V = 0.16` and `0.18` |
| `M1_kv_0.30` / `0.35` | Extinction | **820 / 720 CE** | **24.0° / 22.5° N** | `−942.4 / −948.2` | Hazier horizons push latitude south |
| `M2_free_kv` | Model | **160 CE** | **35.7° N** | `−898.5` | Profile MLE hits `k_V = 0.10` (`+37.3` LL over primary) |
| `M3_geom_cap` | Model | **41 BCE** | *(cap `R = 41.7°`)* | **`−874.3`** | Extinction-free circular void (**highest likelihood**, `+61.5` LL) |
| `subset_in_figure` | Subset | **670 CE** | **27.0° N** | `−878.1` | Drops 108 *informes* outside-figure stars |
| `subset_aratus_core` | Subset | **500 CE** | **28.2° N** | `−851.7` | Pre-Hipparchan constellations (`−Equ, −CrA, −informes`) |
| `subset_strict_id` | Subset | **930 CE** | **25.8° N** | `−929.4` | Secure Hipparcos IDs (`I ≤ 2`) only |
| `vmag_le_4.0` | Magnitude | **121 BCE** | **31.8° N** | `−93.0` | Bright constellation skeletons (`315` stars) |
| `vmag_le_4.5` | Magnitude | **50 CE** | **30.3° N** | `−275.9` | Medium-bright stars (`499` stars) |
| `vmag_le_5.0` | Magnitude | **610 CE** | **27.0° N** | `−601.6` | Deeper sample (`663` stars) |

Even when we lift the constraint that the empty patch must lie on Earth's precession track (**Model M4**, free pole), the unconstrained void center sits at ecliptic `(λ = 283.0°, β = −70.5°)`—**`3.94°` inward** from the precession circle (`β = −66.5°`, `2Δln L = 9.08`). That slight inward pull is the exact geometric signature of an asymmetric or composite boundary rather than a pristine single-night snapshot.

## Fingerprints on the horizon {menu: Horizon rim}

Nothing makes the verdict clearer than lining up the **12 southernmost bright stars Ptolemy catalogued** directly against the **12 brightest southern stars he missed**. Click between ancient observatories below and watch the two sets of stars rise and sink across the sea horizon.

{{figure: ancient-sky-hole/rim}}

At **Rhodes in 128 BCE**, the separation is razor-sharp: **12 of 12** catalogued rim stars clear the horizon, while **11 of 12** missing bright stars stay underground (only Avior grazes `+0.01°`). Jump back to **Crete in 2600 BCE** or **Göbekli Tepe in 9600 BCE**, and the separation collapses—missing stars like Achernar, Alnair, Peacock, and Ankaa soar 10°–40° into the night sky while catalogued stars like Acrux, Alpha Centauri, and Gamma Arae sink below the sea.

## How it was done {menu: Methods}

- **Primary public catalogues:** Verbunt & van Gent (2012, *A&A* 544, A31; VizieR `J/A+A/544/A31/ptolema`, 1,028 *Almagest* stars with Hipparcos IDs and quality flags), ESA Hipparcos Main Catalogue (VizieR `I/239/hip_main`, `V ≤ 7.0`, 15,537 stars with ICRS coordinates, `Vmag`, and proper motions), and Yale Bright Star Catalogue 5th Ed. (VizieR `V/50/catalog`, for Bayer/Flamsteed labels only). Every download URL and SHA-256 hash is in `MANIFEST.md`.
- **Long-term precession:** Implemented exact Vondrák, Capitaine & Wallace (2011, *A&A* 534, A22; Corrigendum 2012, *A&A* 541, C1; IAU SOFA/ERFA `eraLtpequ`) valid to arcseconds across ±200,000 years, verified before locking against J2000 obliquity (`23.4393°`), Thuban at 2781 BCE (`0.06°` from pole), and Vega at 12,001 BCE (`2.69°` from pole).
- **Precession-invariant calibration:** Ptolemy's overhead magnitude completeness curve (`V_50 = 4.42`, slope `s_V = 0.31`) was fitted strictly on the northern ecliptic cap (`β > +30°`, `690` stars) that never enters the southern horizon at any epoch—never refitted on the southern sky.
- **Simulated-sky validation before locking:** On four synthetic catalogues drawn from real Hipparcos positions at `9600 BCE`, `2500 BCE`, `1200 BCE`, and `137 CE`, the pipeline recovered every true epoch within `130–310 yr` and every latitude within `0.0°–0.7°`. On a patchy sky with constellation-scale rim perturbations, the **Spatial Block Bootstrap** (`B = 500` resamples over `138` equal-area ~15° tiles) properly widened beyond the naive star-level interval and covered ground truth.
- **Locked first, zero amendments:** `protocol.md` was hashed and pushed to GitHub (`protocol.lock`, SHA-256 `4be6d43dc0bd`, `2026-11-23T18:45:56Z`) before running on real southern-sky labels. Total paid spend: `$0`.

## What this cannot tell you {menu: Limits}

- **When the oldest *myths* or *northern constellations* were first invented.** Some star figures—like the Bull, the Lion, the Scorpion, and the Great Bear—are documented on Mesopotamian seals and tablets centuries to millennia before Hipparchus, and northern folk asterisms leave no southern horizon hole. Our test measures only the **southern boundary preserved in Ptolemy's star catalogue**.
- **What Aratus's *verbal* descriptions say.** Earlier studies like Ovenden (1966), Roy (1984), and Schaefer (2002) analyzed verbal statements in Aratus's *Phaenomena* (~275 BCE, drawing on Eudoxus ~370 BCE) about which figures touched the celestial equator and tropics. Once Hipparchus and Ptolemy systematically catalogued stars down to their own Mediterranean horizon, they overwrote whatever older empty patch existed in the star list.
- **A single sharp latitude.** Latitude and horizon haze trade off tightly (`35.7° N` at `k_V = 0.10` vs. `22.5° N` at `k_V = 0.35`), and our locked primary model (`k_V = 0.25`) shows that imposing an inaccurate haze model on faint catalogued stars can bias both epoch and latitude substantially.
- **Unresolved visual binaries.** Hipparcos lists `α¹ Cen` (`HIP 71683`) and `α² Cen` (`HIP 71681`, 14" apart) separately while Verbunt & van Gent (2012) link Ptolemy's single naked-eye `α Cen` to `HIP 71681`. A post-hoc check merging them into one star (`V = −0.27`) left Primary M1 completely unchanged (`910 CE, 25.8° N`) and shifted `k_V = 0.15` and `M3` by just 10 years (`200 CE` and `51 BCE`).
- **Second-vendor replication pending.** Under Aletheia Lab's `data` lane rules, this study awaits an independent replication from `protocol.md` by a second vendor's AI.

::: details Technical files, checksums, and post-lock diagnostics
- **Protocol lock:** `questions/ancient-sky-hole/protocol.lock` (`sha256 4be6d43dc0bd6aa66808853167c899697b35450dad12a97ef6da9159a8591776`, locked `2026-11-23T18:45:56Z`, commit `bc04372`). Zero amendments (`amendments.md`).
- **Leave-one-constellation-out (LOCO) range:** Across all 21 southern constellations dropped individually in Primary M1, epoch spans `680 CE` to `1000 CE` (`25.8°` to `26.7° N`). Dropping Piscis Austrinus (`−230 yr`), Aquarius (`−200 yr`), or Eridanus (`−190 yr`) produces the largest early shift; dropping Centaurus (`+90 yr`) or Argo (`+70 yr`) shifts latest.
- **Code verification:** `analysis/test_skyhole.py` passes all 4 astrometry, atmosphere, 4-epoch synthetic recovery, and patchy-sky bootstrap tests; `analysis/skyhole.py --decoy` passed pre-lock on a synthetic `1801 BCE, 35.0° N` sky (`1671 BCE, 35.3° N`, free-pole offset `0.44°`).
:::

## Files

- [Full results](https://github.com/ejhong/aletheia-lab/blob/main/questions/ancient-sky-hole/RESULTS.md)
- [The locked plan](https://github.com/ejhong/aletheia-lab/blob/main/questions/ancient-sky-hole/protocol.md) and [lock file](https://github.com/ejhong/aletheia-lab/blob/main/questions/ancient-sky-hole/protocol.lock)
- [Data manifest](https://github.com/ejhong/aletheia-lab/blob/main/questions/ancient-sky-hole/MANIFEST.md) (VizieR URLs and SHA-256 checksums)
- [Analysis script](https://github.com/ejhong/aletheia-lab/blob/main/questions/ancient-sky-hole/analysis/skyhole.py), [simulated-sky tests](https://github.com/ejhong/aletheia-lab/blob/main/questions/ancient-sky-hole/analysis/test_skyhole.py), and [interactive figure generator](https://github.com/ejhong/aletheia-lab/blob/main/questions/ancient-sky-hole/analysis/make_figures.py)

AI did this work: Antigravity (Google DeepMind), directed by Eugene.
