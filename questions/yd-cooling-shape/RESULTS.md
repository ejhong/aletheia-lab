# Results — Was the Younger Dryas cooling different from other abrupt ice-age coolings?

Issue #75 · Lane: data · Run 2026-11-23 by Antigravity (Google DeepMind), directed by Eugene

**Lock status:** Protocol locked at `2026-11-23T17:16:23Z` (`protocol.lock`, SHA-256 `a1b8ae6f4aa5...`, commit `98273da`) before inspecting any `GS-1` values. **Amendments:** None.

**Status note:** Initial locked run completed by Antigravity (Google DeepMind); open to second-vendor review or replication from `protocol.md`.

---

## Answer

**Pre-registered verdict:** **Indistinguishable from natural coolings** (**0 of 4** pre-registered criteria met: `D1 = False`, `D2 = False`, `D3 = False`, `D4 = False`).

Far from being an unusually sudden, catastrophic "impact winter" cliff compared to the 24 other abrupt coolings of the last 100,000 years, **the Younger Dryas (`GS-1`, onset 12,896 yr b2k) actually began more gradually than almost any other ice-age cooling—and then settled into a completely ordinary stadial while Antarctica warmed:**

1. **Initial cooling speed is among the *slowest* on record.** Over the first 60 years after onset, Greenland NGRIP `δ¹⁸O` drops by only **`0.93 ‰`**—ranking **17th of 19** (the third slowest drop in 60,000 years; median of the other 18 coolings is **`1.94 ‰`**, more than twice as fast). In Kindler et al. (2014)'s 100,000-year reconstructed temperature, the first 60 years drop by **`1.71 °C`** (rank **22 of 25**; median `3.30 °C`).
2. **Initial dust surge is literally dead last out of 25 coolings.** In the first 60 years after onset, NGRIP `Ca²⁺` dust barely moves (`×1.13`, `ln = +0.123`)—ranking **25th of 25** across 100,000 years (median of the other 24 coolings is **`×2.23`**, `ln = +0.802`).
3. **Full stadial amplitude and dust are dead average.** Once the Younger Dryas reaches full cold (`40–200` years after onset), total temperature drop (**`5.01 °C`**, rank **9 of 25**, IQR `2.66–5.53 °C`), total dust jump (**`×3.12`**, rank **10 of 25**, median `×2.87`), and snow-accumulation drop (`×0.73`, rank **10 of 25**) all sit squarely inside the middle of natural Dansgaard–Oeschger coolings.
4. **No global impact winter in Antarctica.** Across Buizert et al. (2021)'s 7-core Antarctic temperature reconstruction (40 kyr, `n = 10` stadials), Antarctica **warms** slightly (`+0.042 °C`) in the 200 years after Younger Dryas onset (rank **8 of 10** in cooling; WAIS Divide ranks **10 of 10** at `+0.044 °C`), matching the standard North-to-South AMOC bipolar seesaw rather than a global impact winter.
5. **Pre-onset slope is ordinary.** In the 200 years before onset (`GI-1a`, recovering from the brief Intra-Allerød Cold Period), Greenland `δ¹⁸O` rises slightly (`+0.93 ‰/century`, rank **5 of 19**, missing top 10% cut `≤ 1`); four natural MIS 2–3 stadials (`GS-15.1`, `GS-17.2`, `GS-2.2`, `GS-2.1c`) had even stronger pre-onset warming slopes.

---

## Pre-registered results (locked protocol)

All values come directly from `python3 analysis/shape.py` (`results/summary.json`, `results/coolings_*.tsv`). Higher values always indicate a sharper / larger / more impact-like cooling.

### Primary criteria (`D1`–`D4`)

| Criterion | Measure & dataset | Pool (`N`) | `GS-1` (YD) | Median of others (IQR) | `GS-1` rank | Top-10% cut | Met? |
|---|---|---:|---:|---|---:|---:|---|
| **`D1` (Abruptness)** | `abrupt_60` (`NGRIP δ¹⁸O`, 60 kyr) | 19 | `+0.93 ‰` | `+1.94 ‰` (`1.34–2.66`) | **17 / 19** | ≤ 1 | **No** |
| **`D2` (Amplitude)** | `amp_temp` (`NGRIP T`, 100 kyr) | 25 | `+5.01 °C` | `+3.51 °C` (`2.66–5.53`) | **9 / 25** | ≤ 2 | **No** |
| **`D2` (Dust jump)** | `dust_jump` (`NGRIP ln Ca²⁺`, 100 kyr) | 25 | `+1.14` (`×3.12`) | `+1.05` (`0.81–1.25`) | **10 / 25** | ≤ 2 | **No** |
| **`D3` ("Out of the blue")** | `pre_slope` (`NGRIP δ¹⁸O`, 60 kyr) | 19 | `+0.93 ‰/100yr` | `−0.53` (`−0.91 to +0.37`) | **5 / 19** | ≤ 1 | **No** |
| **`D4` (Global cooling)** | `ΔT_ant` (`ANT 7-core mean`, 40 kyr) | 10 | **`+0.042 °C`** *(warming)* | `−0.097 °C` (`−0.22 to +0.004`) | **8 / 10** *(cool)* | #1 & `< 0` | **No** |

### Reported alongside (not part of the decision rule)

| Measure | Pool (`N`) | `GS-1` (YD) | Median of others (IQR) | `GS-1` rank |
|---|---:|---:|---|---:|
| `peak_rate_20` (max single 20-yr `δ¹⁸O` drop, 60 kyr) | 19 | `+1.63 ‰` | `+2.10 ‰` (`1.39–2.45`) | **13 / 19** |
| `amp_d18o` (full `δ¹⁸O` drop, 60 kyr) | 19 | `+1.80 ‰` | `+2.05 ‰` (`1.37–2.87`) | **11 / 19** |
| `abrupt_100_alt` (100-yr post vs. 150-yr pre `δ¹⁸O`, 60 kyr) | 19 | `+0.84 ‰` | `+1.95 ‰` (`1.28–2.42`) | **17 / 19** |
| `abrupt_temp_60` (first 60-yr `T` drop, 100 kyr) | 25 | `+1.71 °C` | `+3.30 °C` (`2.05–4.52`) | **22 / 25** |
| `dust_abrupt_60` (first 60-yr `ln Ca²⁺` jump, 100 kyr) | 25 | `+0.123` (`×1.13`) | `+0.802` (`0.635–0.954`) | **25 / 25** |
| `pre_slope_temp` (200-yr pre-onset `T` slope, 100 kyr) | 25 | `+1.13 °C/100yr` | `−2.21` (`−3.24 to −0.17`) | **6 / 25** |
| `accum_log_drop` (`ln` accumulation drop, 100 kyr) | 25 | `+0.311` (`×0.73`) | `+0.238` (`0.142–0.370`) | **10 / 25** |

#### Three-core Greenland cross-check (`gicc05-calcium-20yr.txt`, 11.6–32.4 ka)
- **NGRIP:** `abrupt_60` = `+0.93 ‰` (rank 5/6), `amp_d18o` = `+1.14 ‰` (rank 6/7), `pre_slope` = `+0.93` (rank 3/7).
- **GRIP:** `abrupt_60` = `+1.04 ‰` (rank 5/6), `amp_d18o` = `+2.00 ‰` (rank 4/7), `pre_slope` = `+0.70` (rank 2/7).
- **GISP2:** `abrupt_60` = `+0.93 ‰` (rank 3/6), `amp_d18o` = `+1.64 ‰` (rank 3/7), `pre_slope` = `+0.30` (rank 2/7).

All three Greenland cores agree closely on the slow initial drop (`0.93–1.04 ‰` in the first 60 years).

#### Individual Antarctic ice cores (40 kyr pool, `n = 10`, 200-yr post minus 200-yr pre)
- **WAIS Divide (`TS_WD`):** `+0.044 °C` (cool rank **10/10** — warmest response)
- **EDML (`TS_EDML`):** `+0.058 °C` (cool rank **8/10**)
- **Siple Dome (`TS_SDM`):** `+0.450 °C` (cool rank **9/10**)
- **South Pole (`TS_SP`):** `+0.002 °C` (cool rank **7/10**)
- **Dome Fuji (`TS_DF`):** `0.000 °C` (cool rank **6/10**)
- **Talos Dome (`TS_TAL`):** `−0.080 °C` (cool rank **5/10**)
- **EPICA Dome C (`TS_EDC`):** `−0.178 °C` (cool rank **5/10**)

None of the seven Antarctic cores shows an anomalous synchronous cooling; five are flat or warming immediately after `GS-1` onset, and the two East Antarctic sites with tiny negative values sit right at the median (5th of 10).

---

## Limits

- **Resolution:** `gicc05-60ka-20yr.txt` is 20-year binned and `buizert2021-temp.txt` is 40-year binned, so sub-decadal fluctuations are smoothed. However, a major climate transition lasting ~1,200 years cannot hide an instantaneous collapse across 60-year temperature and dust averages—if anything, our finding that the Younger Dryas ramps down *more slowly* over its first 60 years than 16 of 18 (or 21 of 24) other coolings is directly strengthened at 20-year resolution.
- **Deglacial context:** `GS-1` occurred during deglaciation (higher insolation and less ice volume than mid-glacial MIS 3 coolings), so the baseline climate state differs from `GS-3 .. GS-25`; even so, its stadial amplitude and dust jump sit squarely inside the glacial distribution.
- **Scope:** Showing that the Younger Dryas cooling transition looks like an ordinary (in fact unusually gradual-onset) Dansgaard–Oeschger stadial undercuts the claim that the climate event itself demands a cosmic-impact trigger, but does not by itself test terrestrial geochemical impact proxies (see Issue #76 `yd-platinum-volcanism`).

---

## What this means

A major motivation for the Younger Dryas impact hypothesis is the intuition that the sudden return to Ice Age cold 12,800 years ago was too extreme and too abrupt to happen naturally. Putting the Younger Dryas side by side with the 24 other abrupt coolings of the last 100,000 years shows the opposite: its initial 60-year temperature drop is one of the *slowest* in the record (17th of 19 in `δ¹⁸O`, 22nd of 25 in temperature), its initial 60-year dust jump is literally the *smallest* of all 25 coolings, its full cold amplitude is dead average (9th of 25), and Antarctica warms slightly instead of plunging into a global impact winter. Whatever triggered the Younger Dryas, the climate shift itself looks like a textbook—even sluggish-starting—North Atlantic overturning slowdown, not a singular cosmic-impact cliff.

---

## Authorship and reproducibility

- **Analysis and write-up:** Antigravity (Google DeepMind), directed by Eugene, on `2026-11-23`.
- **Verification:** `python3 analysis/test_shape.py` (5/5 unit tests pass), pre-lock `python3 analysis/shape.py --decoy`, and locked `python3 analysis/shape.py`. All inputs are public NOAA/PANGAEA datasets with SHA-256 hashes in `MANIFEST.md`.
