# Results — Does a second Greenland ice core (NEEM) confirm fewer fire spikes at the Younger Dryas onset?

- **Question:** Issue `#114` (`yd-neem-spikes`)
- **Lane:** `data`
- **Authorship & provenance:** Designed, executed, and written by **Antigravity (Google DeepMind)** under Eugene's direction, on **2026-11-24 (UTC)**. Protocol locked at `2026-11-24T05:26:51Z` (`protocol.lock`, SHA-256 `787ad4de9a5d`) before inspecting any NEEM data inside `10.4–15.0 ka` or across any stadial onset. Zero amendments. Open to second-vendor replication.

---

## The short answer

**Yes—NEEM cleanly replicates NGRIP's exploratory result and rules out a denominator artifact.**

- **Formal pre-registered verdict:** **`replicated_steady_not_spiky`** (`0` amendments).
- **Exact NGRIP replication (`10.4–15.0 ka`, `28` valid 150-year stretches, median `25.0` 1-mm samples/year):**
  1. **Steady level jumps to `#1 of 28`:** In the 150 years after Younger Dryas onset (`12,896–12,746 yr b2k`), NEEM's ordinary yearly median ammonium jumps **`2.58×`** (`29.15` vs. `11.30 µg/kg` in the 150 years before), accounting for **`102%`** of the total ammonium increase (the excess spike component `mean − median` actually *drops* from `0.87` to `0.59 µg/kg`).
  2. **Sharp `>5×` fire spikes drop nearly fourfold:** Years with an annual peak `> 5×` the 51-year running median fall from **`31`** in the 150 years before onset (median across all `28` stretches = **`29.5`**) down to **`8`** after onset (exact two-sided binomial **`p = 0.00032`**). Extreme **`> 10×`** fire-spike years fall from **`18`** before onset to **`0`** after onset.
  3. **Denominator-free controls confirm no hidden fire surge:** Because a rising baseline could mask constant-amplitude plumes under a relative ratio, we pre-registered two denominator-free checks:
     - **Additive plume excess (`peak − running median > 50 µg/kg`):** **`18`** years after onset vs. **`14`** before (median `14.5`, ordinary rank **`11 of 28`**, **`p = 0.481`**). The single largest plume excess after onset (`162 µg/kg`) is *half* the largest plume before onset (`337 µg/kg`), and well below real warm early-Holocene boreal wildfire centuries (`28–36` plumes per 150 yr, `spike_part = 2.7–4.4 µg/kg`).
     - **Snowfall-flux-scaled plumes (`> 50 µg/kg-eq` using NEEM's 5-cm GICC05 layer thickness):** **`16`** years after onset vs. **`13`** before (median `12.5`, **`p = 0.580`**), vs. `34–58` per 150 yr in the early Holocene.
- **Earlier glacial stadials (Pillar 2):** Only `3` stadials in NEEM retain `≥ 10` samples/yr (`GS-1`, `GS-2.1c` at `22.9 ka`, `GS-4` at `28.6 ka`; deeper ice thins below `10 mm/yr`). All three show steady-level jumps (`2.50×`, `1.48×`, `3.46×`) with zero fire-spike surges.

---

## Core comparison: NGRIP (exploratory) vs. NEEM (locked confirmatory)

| Metric (150-yr window after vs. before `12,896 b2k`) | NGRIP exploratory (`#43` explore) | NEEM locked replication (`#114`) |
|---|---:|---:|
| Steady level jump (`after / before`) | `2.70×` (rank `1/29`) | **`2.58×`** (rank **`1/28`**) |
| Share of total rise from steady level | `>95%` | **`102%`** (`spike_part` fell `0.87 → 0.59 µg/kg`) |
| Relative `>5×` spike years (`after` vs. `before`, median) | `4` vs. `18` (med `19`) | **`8` vs. `31`** (med `29.5`, `p = 0.00032`) |
| Extreme `>10×` spike years (`after` vs. `before`) | — | **`0` vs. `18`** |
| Additive `>50 µg/kg` plume years (`after` vs. `before`) | — | **`18` vs. `14`** (rank `11/28`, `p = 0.48`) |
| Flux-scaled `>50 µg/kg-eq` plume years (`after` vs. `before`) | — | **`16` vs. `13`** (`p = 0.58`) |

---

## Limits

- Annual layer thinning limits 1-mm sub-annual spike resolution in NEEM older than `~29 ka` (`< 10` samples/yr), so Pillar 2 covers only `3` abrupt stadials (`GS-1`, `GS-2.1c`, `GS-4`).
- As noted in `#43`, a hypothetical fire source that burned every single year continuously at constant intensity in every season could mimic a steady baseline; however, real boreal fire regimes (seen clearly in the early Holocene right above the YD in NEEM) and the known 1908 Tunguska airburst (`#100`) arrive in Greenland as sharp, episodic multi-day plumes (`spike_part = 2.7–4.4 µg/kg`), not as a smooth 150-year baseline shelf with `0` extreme `>10×` spikes.

---

## What this means

A key objection to our earlier ice-core evidence against a century of repeated Taurid comet airbursts was that it came from an exploratory look at a single Greenland core (NGRIP)—and that dividing by a higher Younger Dryas baseline might have artificially hidden real fire spikes. Locking the exact test in advance on a second, independent Greenland core 365 km away (NEEM) confirms both parts of the story: the entire Younger Dryas ammonium surge sits in the steady background level (highest of 28 stretches, `102%` of the rise), relative fire spikes drop nearly fourfold (`8` vs. `31`, with zero `>10×` spikes), and even denominator-free absolute and snowfall-adjusted plume counts stay completely ordinary (`p = 0.48` and `0.58`)—nowhere near the genuine wildfire spike rates seen a millennium later in the warm early Holocene. The exploratory single-core strike against the drawn-out airburst hypothesis is now a locked two-core replication.
