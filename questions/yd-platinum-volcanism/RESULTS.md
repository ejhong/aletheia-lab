# Results — Did the GISP2 platinum spike precede the Younger Dryas cooling—or follow it during a volcanic cluster?

Issue #76 · Lane: data · Run 2026-11-23 by Antigravity (Google DeepMind), directed by Eugene

**Lock status:** Protocol locked at `2026-11-23T17:25:43Z` (`protocol.lock`, SHA-256 `3d7df72a5989...`, commit `98972d6`) before inspecting GISP2 `[1705, 1720] m` or volcanic tables inside `[12,600, 13,200]` b2k. **Amendments:** None.

**Status note:** Initial locked run completed by Antigravity (Google DeepMind); open to second-vendor review or replication from `protocol.md`.

---

## Answer

**Pre-registered verdicts:**
- **Verdict 1 (GISP2 Platinum as trigger):** **Ambiguous / within uncertainty**
- **Verdict 2 (51,000-year volcanic cluster before YD onset):** **Unusually strong volcanic cluster** (both Greenland and bipolar archives reach top 5%)

**What the ice actually shows (combining both tests transparently):**

1. **On the synchronized `GICC05` timescale, the GISP2 platinum spike arrives *after* the Younger Dryas cooling began.** Interpolating Petaev et al. (2013)'s exact published GISP2 depth span (`1712.375–1712.000 m`, peak `1712.1875 m`) onto `GICC05` via Svensson et al. (2020)'s bracketing bipolar volcanic tie-points (`1713.915 m` at `12,917.3 b2k` and `1708.640 m` at `12,754.8 b2k`) places **Pt onset at `12,869.9 b2k` (`+26.1 yr` *after* the official `GS-1` onset at `12,896 b2k`)** and **Pt peak at `12,864.1 b2k` (`+31.9 yr` after)**. Cross-checking against Rasmussen et al. (2008)'s 20-yr table gives **`12,878.4 b2k` (`+17.6 yr` after)** for onset and **`12,872.8 b2k` (`+23.2 yr` after)** for peak.
2. **Inside GISP2 itself, however, platinum sits *between* the initial cooling start and the main cold/dust plunge—hence the locked verdict "Ambiguous."** In GISP2's own depth column, `δ¹⁸O` begins easing downward from `−38.36‰` (`1713.98 m`, `12,920 b2k`) to `−39.08‰` (`1712.43 m`, `12,880 b2k`) *before* the Pt layer (`1712.375 m`), matching the slow initial ramp found in Issue #75 (`yd-cooling-shape`). Yet GISP2's steepest two-piece step-changepoints in 20-yr `δ¹⁸O` (**`1710.81 m`**), `Na⁺` (**`1710.90 m`**), and `Ca²⁺` dust (**`1709.90 m`**) all sit **1.5–2.5 m shallower** (40–70 years *younger*) than the Pt layer, and the 2-m `δ¹⁸O` step sits right at **`1712.00 m`**. Meanwhile, GISP2 shows **no large volcanic sulfate (`SO₄²⁻ > 237 ppb`) spike directly at `1712.375–1712.000 m`**.
3. **The 150 years immediately *before* the Younger Dryas onset hold the #3 largest bipolar volcanic cluster in 51,000 years.** Across Lin et al. (2022)'s 60–9 ka catalog, `[12,896, 13,046)` b2k records **4 major bipolar eruptions** (`13,028`, `12,995`, `12,961`, and `12,917 b2k`) totaling **`526.6 Tg`** of stratospheric aerosol loading—ranking **3rd of 284** non-overlapping 150-year windows (**top 1.1%**; median window is `0.0 Tg`) and **#1 in bipolar eruption count**. In Greenland sulfate deposition (`Table S3`), the same window totals **`595.9 kg km⁻²`**—ranking **12th of 338** (**top 3.6%**, nearly 4× the median `162.0 kg km⁻²`). The final mega-eruption (`12,917.3 b2k`, `200.8 Tg`, `GISP2 SO₄ = 462 ppb` at `1713.8–1714.0 m`) occurs just **21 years before `GS-1` onset**.
4. **Volcanism is NOT a general trigger of other ice-age coolings.** Across all 19 qualifying abrupt coolings (`10–60 ka`), mean Greenland volcanic sulfate in the 50 yr or 150 yr before onset is indistinguishable from random timing (`p = 0.35` at 50 yr, `p = 0.93` at 150 yr; excluding `GS-1`, `p = 0.53` and `p = 0.99`). So while volcanism does not explain Dansgaard–Oeschger coolings in general, the Younger Dryas specifically was preceded by one of the strongest volcanic clusters of the entire last glacial cycle.

---

## Pre-registered results (locked protocol)

All numbers come directly from `python3 analysis/ptvolc.py` (`results/summary.json`, `results/volc_windows_150yr_*.tsv`).

### Part 1 — GISP2 Platinum timing & internal stratigraphy

#### 1A. Synchronized `GICC05` ages of `1712.375–1712.000 m` (vs. `GS-1` onset `12,896 b2k`)

| Synchronization | Pt onset (`1712.375 m`) | Lag after `GS-1` | Pt peak (`1712.1875 m`) | Lag after `GS-1` | Pt end (`1712.000 m`) |
|---|---:|---:|---:|---:|---:|
| **Svensson et al. (2020) `Table S2`** *(primary)* | **`12,869.9 b2k`** | **`+26.1 yr`** *(after)* | **`12,864.1 b2k`** | **`+31.9 yr`** *(after)* | `12,858.3 b2k` |
| **Rasmussen et al. (2008) `gicc05-calcium-20yr`** *(cross-check)* | **`12,878.4 b2k`** | **`+17.6 yr`** *(after)* | **`12,872.8 b2k`** | **`+23.2 yr`** *(after)* | `12,867.2 b2k` |

*Svensson et al. (2020) bracketing bipolar volcanic tie-points: `1713.915 m` = `12,917.3 b2k` (youngest eruption of pre-YD quadruplet) and `1708.640 m` = `12,754.8 b2k` (post-onset bipolar eruption).*

#### 1B. Within-GISP2 depth stratigraphy (`[1700, 1730] m`; deeper = older, shallower = younger)

| Feature inside GISP2 | Depth (m) | Position vs. Pt onset (`1712.375 m`) | Approx. `GICC05` age |
|---|---:|---|---:|
| Volcanic `SO₄²⁻` spike (`649 ppb`, `iond.txt`) | `1718.6–1718.8` | **6.3 m deeper** (older) | `~13,029 b2k` |
| Volcanic `SO₄²⁻` spike (`462 ppb`, `iond.txt`) | `1713.8–1714.0` | **1.5 m deeper** (older) | `~12,917 b2k` |
| Official `GS-1` onset (`12,896 b2k` in `G3_20YR`) | `~1713.2` | **~0.8 m deeper** (older) | `12,896 b2k` |
| **Petaev et al. (2013) Platinum anomaly** | **`1712.375–1712.000`** | **Reference horizon** | **`12,870–12,858 b2k`** |
| 2-m `δ¹⁸O` step changepoint (`gispd18o.txt`) | `1712.00` | `0.38 m` shallower (at Pt top) | `~12,858 b2k` |
| `Na⁺` sea-salt step changepoint (`iond.txt`) | `1710.90` | **1.48 m shallower** (younger) | `~12,824 b2k` |
| 20-yr `δ¹⁸O` step changepoint (`G3_20YR`) | `1710.81` | **1.57 m shallower** (younger) | `~12,822 b2k` |
| 20-yr `δ¹⁸O` `−1 SD` cooling init (`G3_20YR`) | `1709.91` | **2.47 m shallower** (younger) | `~12,800 b2k` |
| `Ca²⁺` dust step changepoint (`iond.txt`) | `1709.90` | **2.48 m shallower** (younger) | `~12,794 b2k` |
| Volcanic `SO₄²⁻` spike (`394 ppb`, `iond.txt`) | `1708.6–1708.7` | **3.7 m shallower** (younger) | `~12,755 b2k` |

**Why Verdict 1 is `Ambiguous / within uncertainty`:** The first condition of *"Post-dates cooling onset"* is clearly met (`12,869.9 b2k` is `26.1 yr` after `12,896 b2k`, exceeding the `> 15 yr` threshold), but the second pre-registered condition required GISP2's own *step changepoint* in `δ¹⁸O` or `Ca²⁺` to lie deeper than `1712.375 m`. Because the Younger Dryas begins with a sluggish initial ramp (Study #75), the global/NGRIP cooling onset precedes the Pt spike by ~20–30 yr, while GISP2's steepest step into full stadial cold and dust arrives 1.5–2.5 m *shallower* than the Pt spike.

---

### Part 2 — 51,000-year volcanic sulfate context (`Lin et al. 2022`, `60–9 ka`)

#### 2A. Target window ranks across `60–9 ka b2k`

| Window (b2k) | Archive | Sum (events) | Rank / `N` | Top-5% cut | Median window | Top 5% met? |
|---|---|---:|---:|---:|---:|---|
| **`[12,896, 13,046)`** *(primary 150 yr pre-onset)* | **`VOLC_GL` (Greenland sulfate)** | **`595.9 kg km⁻²`** (4) | **12 / 338** | ≤ 16 | `162.0` | **Yes (top 3.6%)** |
| **`[12,896, 13,046)`** *(primary 150 yr pre-onset)* | **`VOLC_BI` (Bipolar aerosol)** | **`526.6 Tg`** (4) | **3 / 284** | ≤ 14 | `0.0` | **Yes (top 1.1%)** |
| `[12,796, 12,946)` *(alongside 150 yr straddle)* | `VOLC_GL` | `268.7 kg km⁻²` (2) | 85 / 337 | ≤ 16 | `162.0` | No |
| `[12,796, 12,946)` *(alongside 150 yr straddle)* | `VOLC_BI` | `200.8 Tg` (1) | 17 / 282 | ≤ 14 | `0.0` | No |
| `[12,746, 13,046)` *(alongside 300 yr wide)* | `VOLC_GL` | `824.5 kg km⁻²` (8) | 14 / 168 | ≤ 8 | `395.9` | No |
| `[12,746, 13,046)` *(alongside 300 yr wide)* | `VOLC_BI` | `630.3 Tg` (5) | **3 / 140** | ≤ 7 | `0.0` | **Yes (top 2.1%)** |

**Top 5 bipolar 150-year windows across all 51,000 years (`n = 284`):**
1. `[55,346, 55,496)` b2k: `653.4 Tg` (1 eruption — NAAZ II)
2. `[45,446, 45,596)` b2k: `544.7 Tg` (1 eruption)
3. **`[12,896, 13,046)` b2k (pre-YD quadruplet): `526.6 Tg` (4 eruptions)**
4. `[38,096, 38,246)` b2k: `504.1 Tg` (2 eruptions)
5. `[41,996, 42,146)` b2k: `406.7 Tg` (2 eruptions)

**The four bipolar eruptions in `[12,896, 13,046)` b2k (`Lin et al. 2022 Table S5`):**
- `13,028.2 b2k`: `220.5 Tg` aerosol (`−44.1 W m⁻²`, Northern Hemisphere high-latitude)
- `12,995.1 b2k`: `77.1 Tg` aerosol (`−15.4 W m⁻²`, low-latitude / SH)
- `12,961.3 b2k`: `28.3 Tg` aerosol (`−5.7 W m⁻²`, low-latitude / SH)
- `12,917.3 b2k`: `200.8 Tg` aerosol (`−40.2 W m⁻²`, Northern Hemisphere high-latitude; 21 yr before `GS-1` onset)

#### 2B. Monte Carlo volcanic-trigger test across abrupt ice-age coolings (`10–60 ka`, 10,000 draws)

| Cooling set & pre-onset window | Observed mean `VOLC_GL` | Null mean (95th pct) | One-sided `p` |
|---|---:|---:|---:|
| All 19 coolings, 50 yr before onset | `72.3 kg km⁻²` | `67.1` (`105.9`) | `0.353` |
| All 19 coolings, 150 yr before onset | `149.6 kg km⁻²` | `201.1` (`265.9`) | `0.928` |
| 18 non-YD coolings, 50 yr before onset | `62.5 kg km⁻²` | `67.1` (`106.8`) | `0.534` |
| 18 non-YD coolings, 150 yr before onset | `124.8 kg km⁻²` | `201.1` (`268.5`) | `0.989` |

---

## Limits

- **Geochemical origin of Pt not directly tested:** Because Petaev et al. (2013)'s raw ICP-MS trace-element table is paywalled and Greenland platinum has not been measured continuously across other ice-age stadials or volcanic eruptions, this test evaluates **stratigraphic timing and volcanic context**, not the elemental source of the Pt itself. The absence of a major GISP2 `SO₄²⁻` peak directly at `1712.375–1712.000 m` means a sulfur-poor source (either a later sulfur-poor volcanic fissure eruption as Green et al. 2025 propose, or a later small Pt-rich extraterrestrial dust injection that did *not* initiate the Younger Dryas) cannot be distinguished from GISP2 sulfate alone.
- **20-yr resolution of `G3_20YR` vs. annual NGRIP:** Svensson et al. (2020) and Green et al. (2025) compare GISP2 Pt against *annual* NGRIP `δ¹⁸O` and report ~45 yr from the volcanic quadruplet / cooling onset to the Pt peak; our linear interpolation between the exact bracketing Svensson tie-points (`1713.915 m` and `1708.640 m`) puts Pt onset at `+26.1 yr` and peak at `+31.9 yr` after the official `12,896 b2k` `GS-1` onset (and `47.4–53.2 yr` after the `12,917.3 b2k` eruption), in close agreement.
- **Synchronization gap in bipolar catalog:** Lin et al. (2022)'s bipolar catalog excludes `16.5–24.5 ka b2k` (where Greenland–Antarctica volcanic matching is incomplete); Greenland's `Table S3` (`338` windows) has no gap and independently confirms top-5% loading (rank 12/338).

---

## What this means

The GISP2 platinum spike is the single most intriguing anomaly in the Younger Dryas impact debate, and testing it transparently turns up a genuinely nuanced answer rather than a slogan for either side:

- **Against platinum as the *trigger* of the Younger Dryas:** On the synchronized Greenland chronology (`GICC05`), the platinum layer (`12,870–12,858 b2k`) arrives **18 to 32 years *after*** the Younger Dryas cooling had already started (`12,896 b2k`), and **47 to 53 years after** a massive bipolar eruption at `12,917 b2k` that capped the **#3 strongest 150-year bipolar volcanic cluster in 51,000 years** (`526.6 Tg` across 4 major eruptions). An event that arrives decades after cooling starts cannot be its initial trigger.
- **Why platinum remains an open puzzle (not simply "debunked"):** Inside GISP2 itself, cooling began slowly (`#75`), so the platinum layer still sits *before* GISP2's steepest cold, sea-salt, dust, and ammonium steps (`1.5–2.5 m` shallower), and there is no large GISP2 volcanic sulfate spike right at the platinum depth itself (`1712.375–1712.000 m`). What deposited that 21-year platinum-rich layer ~20–30 years into the cooling—whether a sulfur-poor Icelandic/subglacial fissure eruption or a later small extraterrestrial dust input—still awaits continuous platinum measurements across other Greenland ice cores and glacial intervals.

---

## Authorship and reproducibility

- **Analysis and write-up:** Antigravity (Google DeepMind), directed by Eugene, on `2026-11-23`.
- **Verification:** `python3 analysis/test_ptvolc.py` (6/6 unit tests pass), pre-lock `python3 analysis/ptvolc.py --decoy`, and locked `python3 analysis/ptvolc.py`. All inputs are public NOAA, *Climate of the Past* (CC-BY-4.0), and PANGAEA (CC-BY-4.0) datasets with SHA-256 hashes in `MANIFEST.md`.
