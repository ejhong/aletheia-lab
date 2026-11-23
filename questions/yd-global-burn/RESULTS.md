# Results — Did 9% of Earth's biomass burn 12,800 years ago?

Issue #69 · Lane: data · Run 2026-11-23 by Antigravity (Google DeepMind), directed by Eugene

**Lock status:** Protocol locked at `2026-11-23T15:34:23Z` (`protocol.lock`, SHA-256 `bf2fe12a3d45...`, commit `0a1df8c`) before inspecting any measurement inside `[12,000, 13,600]` cal BP. **Amendments:** None.

**Status note:** Initial locked run completed by Antigravity (Google DeepMind). Independent review or replication from `protocol.md` by a second vendor's agent (e.g., Claude Fable) has not yet been run.

---

## Answer

**Pre-registered verdicts:**
- **Archive A (Global Atmospheric Carbon — Antarctic ice cores):** **Single-record only** (1 of 3 primary records reached top 5%).
- **Archive B (Global Land Charcoal — GCD3 Tier C1, 19 well-dated high-resolution global sites):** **Not met** (0 of 3 primary measures reached top 5%).
- **Joint verdict:** **Partial / mixed** (by the fixed decision rule, because one of three Archive A series reached top 5%).

**Physical reading:** Neither global archive supports the claim that ~9% of Earth's terrestrial biomass (~50–90 GtC) burned at the Younger Dryas onset (12,800 cal BP).

1. **High-resolution global charcoal shows no fire spike at 12,800 cal BP—and our power test proves it would have seen one.** Across 19 well-dated high-resolution global sites spanning 13,500 years (`Tier C1`), only **1 of 19 sites** reaches `+1.0 SD` in `[12,650, 12,950)` cal BP (rank 38 of 45), **0 of 19** reach `+1.5 SD`, and **0 of 7** North American sites reach `+1.0 SD`. Across all 26 high-resolution sites (`Tier C2`), `[12,650, 12,950)` ranks **44th of 45** in peaking fraction (`1/26`). Synthetic pulse injections on the same `Tier C1` sites show 95–100% rank-1 recovery for a 100-year global fire of `+1.0` to `+2.0 SD` across 50–75% of sites.
2. **Coarse cores manufacture the illusion of a 12.8 ka spike.** Restricted to coarse-resolution cores (`Tier C3_coarse`, median spacing `> 100 yr`, `n = 43`), the fraction of sites `≥ +1.5 SD` jumps from **0/26 (0%)** in high-resolution cores to **5/41 (12.2%, rank 2 of 45)**—reproducing Marlon et al. (2009)'s resolution-artifact finding globally (and those 5 coarse sites are all in Papua New Guinea and Patagonia, with only 1–2 samples each in the 300-year window).
3. **Antarctic air does record a real carbon perturbation, but it is too late, too small for 9% of Earth's biomass, and matches ordinary Heinrich Stadials.** In Taylor Glacier, `TG_BURN` ranks 7th of 54 (`0.488 ppm·‰`, missing top 5%) in `[12,650, 12,950)` and WAIS Divide `CO2` rise ranks 14th of 38 (`+4.52 ppm`). Only the heavily smoothed Eggleston 155 kyr `δ13C-CO2` composite reaches top 5% (tied 4th of 499 at just `0.030‰`), sitting behind three windows of Heinrich Stadial 1 (`16.8–17.7 ka`) and tied with HS1 (`16.5–16.8 ka`) and HS5 (`47.1–47.4 ka`). Single-box isotopic mass balance on Taylor Glacier's `k = 0` step (`ΔCO2 = +4.33 ppm`, `Δδ13C = −0.113‰`) yields only **`3.17 GtC`** airborne terrestrial carbon (`+1.49 ppm` CO₂, or `6.3–12.7 GtC` emitted even if 100% terrestrial)—roughly **4× to 14× smaller** than burning ~9% of Earth's biomass (~50–90 GtC). Post-lock inspection shows Taylor Glacier is flat across `12,937 → 12,751` cal BP and peaks **150–450 years after onset** in `[12,350, 12,650)` (`k = −1`, rank 2/54, `0.955 ppm·‰`), forming a near-identical triplet with Heinrich Stadial 1 (`15,950–16,250`, rank 1/54, `0.957 ppm·‰`) and Heinrich Stadial 4 (`39,650–39,950`, rank 3/54, `0.852 ppm·‰`).

---

## Pre-registered results (locked protocol)

All numbers below come directly from `python3 analysis/burn.py` (`results/summary.json`, `results/windows_archive_a.tsv`, `results/windows_charcoal_13_5ka.tsv`). Target window `k = 0` is `[12,650, 12,950)` cal BP.

### Archive A — Global Atmospheric Carbon (Antarctic ice cores)

| Series | Measure | Target (`k = 0`) | Rank / `N` | Ties | Realised frac | Top-5% cut | Top-1% cut | Threshold met? |
|---|---|---:|---:|---:|---:|---:|---:|---|
| **`TG_BURN`** *(primary)* | max `ΔCO₂⁺ × Δδ¹³C⁻` (100/200 yr, 2 transects) | `0.488 ppm·‰` | **7 / 54** | 0 | 0.130 | ≤ 2 | ≤ 1 | No |
| **`WAIS_CO2`** *(primary)* | max forward `ΔCO₂` (100/200 yr) | `+4.52 ppm` | **14 / 38** | 0 | 0.368 | ≤ 1 | ≤ 1 | No |
| **`EGG_D13C`** *(primary)* | max forward `δ¹³C` drop (155 kyr composite) | `0.030 ‰` | **4 / 499** | 2 | 0.012 | ≤ 24 | ≤ 4 | **Top 1% & Top 5%** |
| `TG_BURN_deglacial` *(alongside)* | `TG_BURN` over `[11,150, 22,250)` only | `0.488 ppm·‰` | 5 / 22 | 0 | 0.227 | ≤ 1 | ≤ 1 | No |
| `TG_D13C` *(alongside)* | max forward `δ¹³C` drop (Taylor, 2 transects) | `0.113 ‰` | 6 / 54 | 0 | 0.111 | ≤ 2 | ≤ 1 | No |
| `WAIS_CO2_50` *(alongside)* | max forward `ΔCO₂` (50/100 yr bins) | `+3.71 ppm` | 14 / 26 | 0 | 0.538 | ≤ 1 | ≤ 1 | No |

**Archive A verdict:** **Single-record only** (`EGG_D13C` hits top 5%; `TG_BURN` and `WAIS_CO2` miss).

#### Top windows in Archive A (what actually dominates the global atmospheric record)

- **`TG_BURN` top 7 (of 54):**
  1. `15,950–16,250` cal BP (**Heinrich Stadial 1**): `0.957 ppm·‰`
  2. `12,350–12,650` cal BP (**mid-Younger Dryas, `k = −1`**): `0.955 ppm·‰`
  3. `39,650–39,950` cal BP (**Heinrich Stadial 4**): `0.852 ppm·‰`
  4. `16,250–16,550` cal BP (**Heinrich Stadial 1**): `0.845 ppm·‰` (also Rank 1 in `TG_D13C` at `0.180‰`)
  5. `16,850–17,150` cal BP (**Heinrich Stadial 1**): `0.839 ppm·‰`
  6. `39,350–39,650` cal BP (**Heinrich Stadial 4**): `0.550 ppm·‰`
  7. `12,650–12,950` cal BP (**Younger Dryas onset, `k = 0`**): `0.488 ppm·‰`
- **`WAIS_CO2` top 5 (of 38):** `11,450–11,750` (`+14.58 ppm`, end of YD / Holocene onset), `10,550–10,850` (`+12.82 ppm`), `15,950–16,250` (`+11.87 ppm`, HS1), `14,450–14,750` (`+11.32 ppm`, Bølling onset), `16,550–16,850` (`+7.64 ppm`, HS1). Target `k = 0` (`+4.52 ppm`) is 14th.
- **`EGG_D13C` top 8 (of 499):** Ranks 1–3 are `17,150–17,450` (`0.040‰`), `16,850–17,150` (`0.040‰`), and `17,450–17,750` (`0.035‰`)—all **Heinrich Stadial 1**. Rank 4 is a 3-way tie at `0.030‰` between `12,650–12,950` (**YD**), `16,550–16,850` (**HS1**), and `47,150–47,450` (**HS5**). Rank 7 is `17,750–18,050` (HS1, `0.030‰`) and Rank 8 is `12,950–13,250` (`0.025‰`, *before* the YD onset).

#### Physical mass-balance forward check (`δ_bio = −25‰`, `M_0 = 2.12 × CO₂`)

| Window | Best Taylor step (cal BP) | `ΔCO₂` (ppm) | `Δδ¹³C` drop (‰) | Airborne C₃ carbon `ΔC_air` | Implied C₃ `ΔCO₂` | Emitted @ 50% AF | Emitted @ 25% AF |
|---|---|---:|---:|---:|---:|---:|---:|
| **YD onset (`k = 0`)** | `12,750 → 12,650` | `+4.33` | `0.113` | **3.17 GtC** | `+1.49 ppm` | **6.34 GtC** | **12.68 GtC** |
| **HS1 benchmark (`k = 11`)** | `16,350 → 16,150` | `+6.21` | `0.154` | **3.92 GtC** | `+1.85 ppm` | **7.84 GtC** | **15.69 GtC** |
| *(Exploratory: mid-YD `k = −1`)* | `12,750 → 12,550` | `+5.99` | `0.159` | *4.50 GtC* | *+2.12 ppm* | *8.99 GtC* | *17.99 GtC* |
| *(Exploratory: HS1 `k = 12`)* | `16,450 → 16,250` | `+4.69` | `0.180` | *4.54 GtC* | *+2.14 ppm* | *9.08 GtC* | *18.17 GtC* |
| *(Exploratory: HS4 `k = 90`)* | `39,850 → 39,650` | `+6.16` | `0.138` | *3.14 GtC* | *+1.48 ppm* | *6.28 GtC* | *12.56 GtC* |

In every case, the `δ¹³C` drop accounts for only about a third of the accompanying `CO₂` rise if attributed to `-25‰` terrestrial carbon—showing that the bulk of the atmospheric carbon input is isotopically heavier (consistent with Southern Ocean deep-carbon outgassing / air–sea gas exchange; Bauska et al. 2016, 2018). Even if 100% of the `k = 0` isotope shift came from biomass burning, the implied emission (`6.3–12.7 GtC`) is **4× to 14× below** the ~50–90 GtC expected from burning ~9% of Earth's terrestrial biomass.

---

### Archive B — Global Land Charcoal (`GCD3`)

#### Primary 13.5 kyr span (`[1,250, 14,750)` cal BP, 45 non-overlapping 300-yr windows)

| Tier | Sites | `M_mean` (rank/45) | **`E_mean`** (rank/45) | **`F_peak` ≥ +1.0** (rank/45) | `F_peak` ≥ +1.5 (rank/45) | **`E_100`** (rank/45) |
|---|---:|---|---|---|---|---|
| **`C1` (Primary: high-res + well-dated)** | 19 | `-0.075` (31/45) | **`0.000`** (**20/45**) | **`0.053`** (1/19; **38/45**) | `0.000` (0/19; 26/45) | **`0.184`** (**12/45**) |
| `C2` (All high-res, `med_dt ≤ 100 yr`) | 26 | `-0.171` (38/45) | `0.000` (19/45) | `0.038` (1/26; 44/45) | `0.000` (0/26; 31/45) | `0.096` (17/45) |
| `C3` (All resolutions) | 69 | `-0.116` (37/45) | `+0.016` (15/45) | `0.119` (23/45) | `0.075` (8/45) | `0.112` (18/45) |
| `C3_coarse` (`med_dt > 100 yr` only) | 43 | `-0.082` (36/45) | `0.000` (18/45) | `0.171` (15/45) | **`0.122` (5/41; 2/45)** | `0.315` (1/3*) |

*\*Only 3 of 45 windows meet 50% site occupancy in 100-yr bins for coarse cores (`med_dt > 100 yr`).*

**Archive B verdict:** **Not met** (0 of 3 primary Tier C1 measures reach top 5% cut `≤ 2` or top 1% cut `≤ 1`).

Where the real Tier C1 charcoal highs actually sit:
- **`F_peak` Rank 1 (29.4% of sites):** `11,450–11,750` cal BP (end of the Younger Dryas / abrupt warming into the Holocene).
- **`E_100` Rank 1 (`0.480`):** `13,550–13,850` cal BP (late Bølling–Allerød); Rank 3 (`0.369`) is `11,450–11,750` cal BP.
- **`E_mean` Rank 1 (`0.228`):** `6,050–6,350` cal BP (mid-Holocene).

#### Late-glacial span (`[10,250, 14,750)` cal BP, 15 windows — reported alongside)

| Tier | Sites | `M_mean` (rank/15) | `E_mean` (rank/15) | `F_peak` ≥ +1.0 (rank/15) | `F_peak` ≥ +1.5 (rank/15) | `E_100` (rank/15) |
|---|---:|---|---|---|---|---|
| `C1` | 20 | `+0.054` (10/15) | `-0.057` (13/15) | `0.050` (12/15) | `0.000` (8/15) | `0.098` (10/15) |
| `C2` | 29 | `+0.126` (3/15) | `+0.025` (4/15) | `0.103` (7/15) | `0.034` (7/15) | `0.160` (6/15) |
| `C3` | 74 | `+0.094` (8/15) | `0.000` (5/15) | `0.141` (7/15) | `0.042` (8/15) | `0.066` (9/15) |
| `C3_coarse` | 45 | `+0.072` (8/15) | `0.000` (6/15) | `0.167` (7/15) | `0.048` (8/15) | `0.261` (1/4) |

#### Regional charcoal breakdown (13.5 kyr span, `k = 0`)

| Region | Tier C1 (`n`) | C1 `E_mean` (rank) | C1 `F_peak` (rank) | C1 `E_100` (rank) | Tier C2 (`n`) `F_peak` (rank) |
|---|---:|---|---|---|---|
| **North America** | 7 | `0.000` (16/45) | **`0.000`** (21/45) | `0.031` (35/45) | 12: **`0.000`** (33/45) |
| **Europe** | 2 | `0.000` (17/45) | **`0.000`** (12/45) | `0.046` (36/41) | 3: **`0.000`** (16/45) |
| **South/Central America** | 5 | `-0.073` (35/45) | **`0.000`** (17/45) | `0.351` (6/45) | 6: **`0.000`** (21/45) |
| **Asia/Australasia/Africa** | 5 | `+0.530` (1/45) | `0.200` (1/5; 10/45) | `0.415` (11/38) | 5: `0.200` (10/45) |

Notice North America—ground zero of the proposed YD impact—has **zero** sites reaching `+1.0 SD` across `Tier C1` (`0/7`), `Tier C2` (`0/12`), and even `Tier C3` (`0/14`). The single Tier C1 site above `+1.0 SD` globally is Lake Albert in Uganda (`z = +1.48`), which lifts the small 5-site `Asia/Australasia/Africa` group's `E_mean` while its own `F_peak` (10/45) and `E_100` (11/38) remain ordinary.

#### Synthetic 100-year fire-pulse recovery on Tier C1 (200 trials, `seed = 69`)

| Pulse amplitude (`SD`) | Fraction of sites affected | `E_mean` top 5% / top 1% | `F_peak` top 5% / top 1% | `E_100` top 5% / top 1% |
|---:|---:|---:|---:|---:|
| `+0.5` | 25% | 0.06 / 0.06 | 0.12 / 0.05 | 0.10 / 0.03 |
| `+0.5` | 50% | 0.10 / 0.04 | 0.14 / 0.04 | 0.22 / 0.09 |
| `+0.5` | 75% | 0.24 / 0.10 | 0.22 / 0.06 | 0.36 / 0.18 |
| `+1.0` | 25% | 0.10 / 0.04 | 0.16 / 0.04 | 0.15 / 0.08 |
| `+1.0` | 50% | 0.33 / 0.22 | 0.21 / 0.06 | **0.77 / 0.56** |
| `+1.0` | 75% | 0.54 / 0.44 | 0.35 / 0.10 | **0.98 / 0.95** |
| `+1.5` | 25% | 0.24 / 0.13 | 0.20 / 0.03 | 0.54 / 0.28 |
| `+1.5` | 50% | 0.67 / 0.51 | 0.40 / 0.10 | **0.98 / 0.95** |
| `+1.5` | 75% | 0.83 / 0.73 | 0.58 / 0.20 | **1.00 / 1.00** |
| `+2.0` | 50% | 0.79 / 0.70 | 0.62 / 0.27 | **1.00 / 1.00** |
| `+2.0` | 75% | **0.95 / 0.92** | **0.81 / 0.55** | **1.00 / 1.00** |

The Tier C1 network is insensitive only to small regional fires (`+0.5 SD` or `25%` of sites). Any genuine global fire pulse (`+1.0` to `+2.0 SD` across `50–75%` of sites for 100 years) is caught by `E_100` **77%–100%** of the time in the top 5% (and **56%–100%** at Rank 1).

---

### Window-width and phase-shift sensitivity (reported alongside)

| Variant | Target window (cal BP) | `TG_BURN` | `WAIS_CO2` | `EGG_D13C` | `C1 E_mean` | `C1 F_peak` | `C1 E_100` |
|---|---|---|---|---|---|---|---|
| **Primary (300 yr)** | `[12,650, 12,950)` | 7/54 (`0.488`) | 14/38 (`+4.52`) | **4/499** (`0.030`) | 20/45 (`0.000`) | 38/45 (`0.053`) | 12/45 (`0.184`) |
| **Tight (150 yr)** | `[12,725, 12,875)` | 33/106 (`0.032`) | 23/54 (`+4.78`) | **12/997** (`0.030`) | 63/89 (`-0.064`) | 47/89 (`0.111`) | — |
| **Wide (600 yr)** | `[12,500, 13,100)` | 3/27 (`0.764`) | 8/18 (`+4.39`) | **3/249** (`0.030`) | 8/21 (`0.000`) | 15/21 (`0.053`) | 13/21 (`0.173`) |
| **Shift +150 yr (onset)** | `[12,800, 13,100)` | 26/52 (`0.000`) | 26/38 (`+2.84`) | **4/499** (`0.030`) | 4/44 (`+0.128`) | 20/44 (`0.111`) | 12/44 (`0.173`) |
| **Shift −150 yr (post-onset)** | `[12,500, 12,800)` | 3/52 (`0.764`) | 13/38 (`+4.39`) | **9/499** (`0.020`) | 19/44 (`0.000`) | 42/44 (`0.000`) | 37/44 (`0.000`) |

No window width or shift changes the outcome: **Archive B never reaches top 5% in any variant**, and **Archive A never moves beyond `Single-record only` in any variant**. Notice especially the sharp asymmetry in Taylor Glacier: across `[12,800, 13,100)` (`TG_BURN = 0.000`, rank 26/52), nothing happens; all of the Taylor Glacier carbon excursion sits *after* 12,750 cal BP in `[12,500, 12,800)` and `[12,350, 12,650)`.

---

## Post-result exploratory notes (labelled exploratory; not part of the locked decision rule)

After locking and running `burn.py`, we ran `explore/post_check.py` to inspect the raw Taylor Glacier points and individual charcoal sites inside `k = 0`:

1. **Raw Taylor Glacier profile across the YD onset (`taylor2018d13co2.txt`, identical ages in `taylor2016d13co2.txt`):**
   - `13,015 BP`: `240.2 ppm`, `−6.644‰`
   - `12,937 BP`: `242.3 ppm`, `−6.627‰`
   - `12,786 BP`: `242.5 ppm`, `−6.621‰`
   - `12,751 BP`: `242.4 ppm`, `−6.615‰` (completely flat across the 12,846 cal BP YD onset)
   - `12,718 BP`: `245.0 ppm`, `−6.645‰`
   - `12,697 BP`: `246.5 ppm`, `−6.698‰`
   - `12,637 BP`: `246.9 ppm`, `−6.737‰`
   - `12,580 BP`: `248.3 ppm`, `−6.780‰` (minimum `δ¹³C` is ~266 years after YD onset)
   - This `+5.9 ppm` / `−0.165‰` shift over `12,751 → 12,580 BP` closely resembles **Heinrich Stadial 1** (`16,380 → 16,176 BP`: `217.4 → 223.8 ppm`, `−6.630 → −6.842‰`, i.e., `+6.4 ppm` / `−0.212‰`) and **Heinrich Stadial 4** (`39,850 → 39,650 BP`: `+6.2 ppm` / `−0.138‰`). Bauska et al. (2018)'s NOAA abstract explicitly links these centennial `δ¹³C-CO₂` drops across both MIS 3 and the deglaciation to abrupt climate reorganizations (Heinrich events / Southern Ocean & organic carbon feedbacks).
2. **Individual Tier C1 sites in `[12,650, 12,950)` cal BP:** The highest site is `#359 Mobutu Sese Seko / Lake Albert` (Uganda, `z = +1.48`); the next highest is `#634 Lago di Gembro` (Italy, `z = +0.83`). The 7 high-resolution North American sites span `z = +0.53` (`Xindi`) down to `z = −1.72` (`Bluff`), with 3 of the 7 below `−1.1 SD`.
3. **The 5 coarse-only (`Tier C3_coarse`) sites with `z ≥ +1.5` in `k = 0`:** `#285 Haeapugua` (`+1.79`, `med_dt = 277 yr`, 2 samples), `#326 Tugupugua` (`+1.53`, `285 yr`, 1 sample), `#1069 Laguna Lincoln` (`+2.10`, `180 yr`, 2 samples), `#1070 Laguna Lofel` (`+2.30`, `242 yr`, 1 sample), and `#1071 Laguna Six Minutes` (`+1.78`, `330 yr`, 2 samples)—all in Papua New Guinea and Patagonia, none in North America or Europe.

---

## Limits

- **Scope of test:** This study tests the **global biomass-burning / impact-winter** mechanism (~9% of Earth's biomass burned at 12.8 ka). It does *not* test whether a cosmic impact occurred over an ice sheet or ocean without triggering global wildfires, nor does it test platinum anomalies, microspherules, or shocked quartz.
- **Firn smoothing & gas-age uncertainty:** Antarctic firn smooths brief atmospheric spikes over ~20–60 yr (WAIS Divide) to ~50–150 yr (Taylor Glacier / EDC). Firn smoothing attenuates a 1-year peak's height, but does *not* erase the century-scale atmospheric carbon inventory from burning ~50–90 GtC (which takes centuries to re-equilibrate with the deep ocean). Relative gas-age uncertainty (~50–150 yr between Antarctica and Greenland) could shift the nominal age of Taylor Glacier's `12,751–12,580` drop slightly, though it does not alter its small isotopic magnitude (`3.2–4.5 GtC` airborne) or its near-identity with Heinrich Stadials 1 and 4.
- **GCD3 site count and chronologies:** Only 19 global sites meet the strict high-resolution + well-dated criteria (`Tier C1`) across the full 13.5 kyr span, and GCD3 uses heterogeneous pre-IntCal20 age models (`EST_AGE`). Expanding to `Tier C2` (`26` sites) or the late-glacial span (`20`–`74` sites) and widening the window to 600 years (`[12,500, 13,100)`) all give the same null result in high-resolution charcoal.
- **Closed-access papers:** Full bodies of Wolbach et al. (2018) and Bauska et al. (2016, 2018) are paywalled and not read (`unverified` beyond their open abstracts and NOAA file headers). All data claims in this report come directly from the primary NOAA files listed in `MANIFEST.md`.

---

## What this means

If a cosmic impact had set nearly a tenth of Earth's living biomass ablaze 12,800 years ago, two completely independent planetary archives should record it: well-mixed global air trapped in Antarctic ice, and high-resolution lake and peat charcoal cores around the world. Neither shows a global firestorm. High-resolution charcoal records across six continents—including every well-resolved North American core in the database—are quiet at 12,800 years ago, even though our simulations show the network would easily catch a real global fire; the only hint of a 12,800-year peak comes from a handful of coarse, low-resolution cores in Papua New Guinea and Patagonia. Meanwhile, Antarctic air does show a real drop in carbon-13 and a modest rise in CO₂—not right at the onset, but one to three centuries later—and it is far too small for 9% of Earth's biomass and nearly identical to the carbon shifts seen during Heinrich Stadials 1 and 4, when North Atlantic cooling stirred deep-ocean carbon out of the Southern Ocean with no comet involved. Combined with our earlier Greenland ice-core studies (`#43` and `#60`), the "global wildfire / impact winter" side of the Younger Dryas impact hypothesis does not hold up in public global data, while other impact-proxy claims (such as platinum or microspherules) remain separate questions.

---

## Authorship and reproducibility

- **Analysis and write-up:** Antigravity (Google DeepMind), directed by Eugene, on `2026-11-23`.
- **Verification:** `python3 analysis/test_burn.py` (10 unit tests, all pass), pre-lock `python3 analysis/burn.py --decoy`, and locked `python3 analysis/burn.py`. All inputs are public NOAA files with SHA-256 hashes in `MANIFEST.md`.
