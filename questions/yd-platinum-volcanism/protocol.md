# Did the GISP2 platinum spike precede the Younger Dryas cooling—or follow it during a volcanic cluster?

Issue #76 · Lane: data · Written 2026-11-23 by Antigravity (Google DeepMind), directed by Eugene

## Question

The ~100-fold platinum (Pt) spike reported by Petaev et al. (2013, *PNAS* 110:12917–12920) in the GISP2 Greenland ice core (`1712.375–1712.000 m`, peaking at `1712.250–1712.125 m`, spanning ~21 years) is widely cited as the strongest geochemical evidence that a cosmic impact triggered the Younger Dryas (`GS-1`). Meanwhile, recent synchronized ice-core studies (Svensson et al. 2020; Abbott et al. 2021; Lin et al. 2022; Green et al. 2025) argue that on the modern `GICC05` chronology the platinum layer actually sits *decades after* cooling began, and that a cluster of large volcanic eruptions preceded the cooling onset instead.

Here we run two pre-registered tests directly on primary public ice-core datasets:

1. **Platinum timing (trigger test):** Does GISP2 `1712.375–1712.000 m` precede the Younger Dryas cooling onset, or follow it—tested **both** on the synchronized `GICC05` timescale (Svensson et al. 2020; Rasmussen et al. 2008) **and** directly inside GISP2's own depth column (`δ¹⁸O`, `Ca²⁺`, `Na⁺`, zero timescale error)?
2. **51,000-year volcanic context (volcanic-cluster test):** Across 51,000 years (`60–9 ka b2k`, Lin et al. 2022), how unusual is cumulative Greenland and bipolar volcanic sulfate deposition in the 150 years immediately preceding the Younger Dryas onset (`[12,896, 13,046)` b2k), and do large volcanic eruptions systematically precede abrupt ice-age coolings (`GS-1` through `GS-17.2`) more often than chance?

## Data and sources

All public from NOAA WDS Paleoclimatology, *Climate of the Past* (CC-BY-4.0), and PANGAEA (CC-BY-4.0); exact URLs and SHA-256 hashes in `MANIFEST.md`:

| Short name | File | What | Span |
|---|---|---|---|
| `GISP2_ION` | `noaa/iond.txt` | GISP2 deep-core major ions (`Na+`, `NH4+`, `Ca2+`, `SO4^2-`, etc.) vs. top/bottom depth (Mayewski et al. 1997) | 2.6–3,040 m (~2–4 yr resolution near 1,712 m) |
| `GISP2_D18O` | `noaa/gispd18o.txt` | GISP2 2-m `δ¹⁸O` vs. top depth (Grootes & Stuiver 1997) | 2–3,050 m |
| `G3_20YR` | `noaa/gicc05-calcium-20yr.txt` | Synchronized 20-yr `NGRIP`, `GRIP`, `GISP2` depths, `δ¹⁸O`, and `Ca²⁺` on `GICC05` (Rasmussen et al. 2008) | 11,620–32,440 yr b2k |
| `SVEN2020` | `copernicus/svensson2020-supplement.zip` (`Table S2`) | 88 bipolar volcanic synchronization tie-points with exact `NGRIP`, `NEEM`, `GRIP`, `GISP2` depths and `GICC05` ages (Svensson et al. 2020) | 12.1–60 ka b2k |
| `LIN2022` | `copernicus/lin2022-supplement.zip` (`Table S3`, `Table S5`) | 1,113 Greenland volcanic eruptions (`Table S3`) and 85 bipolar eruptions (`Table S5`) with sulfate deposition and global forcing (Lin et al. 2022) | 60–9 ka b2k |
| `SIGL2021` | `pangaea/930557.tab` | Reconstructed VSSI for 30 eruptions > 1 Tg S around YD inception (Sigl et al. 2021 / Abbott et al. 2021) | ~13.2–12.8 ka BP |
| `EVENTS` | `events.tsv` | Published `GICC05` stadial/interstadial onsets (Rasmussen et al. 2014, Table 2) | 11.4–119.1 ka b2k |

**Published platinum horizon:** Petaev et al. (2013, *PNAS* 110:12917–12920; paywalled body not read, depths confirmed via open-access Svensson et al. 2020 and Green et al. 2025 *PLOS One* `doi:10.1371/journal.pone.0331811`) locate the GISP2 Pt anomaly from `1712.375 m` (onset) to `1712.000 m` (end), peaking at `1712.250–1712.125 m` (midpoint `1712.1875 m`).

**What was looked at before locking:** Open abstracts/snippets of Svensson et al. (2020), Abbott et al. (2021), and Green et al. (2025) (which report ~45 yr lag for the Pt spike on `GICC05`), plus blind file headers/column schemas (`explore/structure.py`). Zero values inside GISP2 `[1705, 1720] m` or volcanic eruption lists inside `[12,600, 13,200]` b2k were read from the downloaded tables before locking.

## Method

### Part 1 — Stratigraphic depth & synchronized timing of GISP2 Pt (`1712.375–1712.000 m`)

#### 1A. Synchronized `GICC05` age interpolation
- **Primary (`SVEN2020` `Table S2`):** Extract all rows with finite `GISP2 depth(m)` and `GICC05 age(b2k)`, sort by depth, and linearly interpolate `age_GICC05` at `d_pt_onset = 1712.375 m`, `d_pt_peak = 1712.1875 m`, and `d_pt_end = 1712.000 m`. Report the exact bracketing bipolar volcanic tie-points.
- **Cross-check (`G3_20YR`):** Linearly interpolate `Age (years b2k)` vs. `GISP2 depth (m)` from `gicc05-calcium-20yr.txt` at the same three depths.
- Compute lag relative to the official `GICC05` `GS-1` onset (`12,896 yr b2k`, Rasmussen et al. 2014):
  - `lag_pt_onset = 12896 − age_GICC05(1712.375)` (yr; **positive = Pt occurs AFTER cooling onset**, negative = before)
  - `lag_pt_peak = 12896 − age_GICC05(1712.1875)` (yr)

#### 1B. Within-GISP2 depth stratigraphy (zero timescale error)
Restrict GISP2 records to `[1700.0, 1730.0] m` (deeper = older, shallower = younger; using midpoint depth `(top + bottom) / 2` for `GISP2_ION`, top + 1.0 m for 2-m `GISP2_D18O`, and listed `GISP2 depth (m)` for 20-yr `G3_20YR`):
- **Step changepoint (`d_step`):** For a series `y(d)` ordered by depth, find the split depth `d_s` minimizing total squared error `SSE(d > d_s) + SSE(d <= d_s)` subject to at least 5 points on each side and the physical cooling sign (`mean(deeper) > mean(shallower)` for `δ¹⁸O`; `mean(shallower) > mean(deeper)` for `ln(Ca²⁺)` and `ln(Na⁺)`).
  - Primary depth changepoints: **`d_d18o_step`** (on 20-yr GISP2 `δ¹⁸O` in `G3_20YR`; also cross-checked on 2-m `GISP2_D18O`), **`d_ca_step`** (on `ln(Ca²⁺)` in `GISP2_ION`), and **`d_na_step`** (on `ln(Na⁺)` in `GISP2_ION`).
- **Cooling initiation depth (`d_d18o_init`):** On 20-yr GISP2 `δ¹⁸O`, compute pre-onset baseline mean `μ_0` and SD `σ_0` over `[1717.0, 1725.0] m`; moving upward from deeper to shallower ice, `d_d18o_init` is the deepest depth `< 1717.0 m` where `δ¹⁸O < μ_0 − 1.0 σ_0` and the next shallower point is also `< μ_0 − 1.0 σ_0`.
- Also report all local `GISP2_ION` sulfate (`SO₄²⁻`) spikes exceeding `median + 3 × MAD` (computed over `[1695, 1735] m`) inside `[1708, 1720] m`, noting their exact depth relative to cooling onset and `1712.375–1712.000 m`.

### Part 2 — 51,000-year volcanic sulfate context (`LIN2022`, `60–9 ka`)

#### 2A. 150-year volcanic cluster rank across 60–9 ka
Tile `[9,296, 59,996)` yr b2k into `N = 338` non-overlapping **150-year windows** `k` (`[12,896 + 150k, 12,896 + 150(k+1))`), so **`k = 0` is `[12,896, 13,046)` yr b2k** (the 150 years immediately preceding `GS-1` onset):
- **`VOLC_GL` (Primary, Greenland `LIN2022 Table S3`):** For every row with finite `Age (b2k)` (col 12) and finite `Average deposition (kg km⁻²)` (col 13), sum `Average deposition` inside each 150-yr window (`N = 338`). Also report eruption count `N_GL`.
- **`VOLC_BI` (Primary, Bipolar `LIN2022 Table S5`):** For every row with finite `GICC05 Age (a b2k)` (col 1) and finite `Average stratospheric aerosol loading (Tg)` (col 26), sum aerosol loading inside each 150-yr window, excluding the `[16,500, 24,500)` b2k synchronization gap documented by Lin et al. (2022) (`N = 284` usable windows). Also report bipolar eruption count `N_BI`.
- **Rank definition:** `rank = 1 + count(other usable windows strictly greater than k = 0)`. *Top 5%* means `rank ≤ max(1, floor(0.05 * N))`.
- **Reported alongside:** straddling window `[12,796, 12,946)` (150 yr centered near onset), 300-yr window `[12,746, 13,046)`, top-10 windows across 60–9 ka, and the `SIGL2021` (`PANGAEA.930557`) VSSI eruption table around YD inception.

#### 2B. Volcanic-trigger association across all 19 abrupt coolings (`10–60 ka`)
Using the exact same 19 qualifying stadial onsets (`GS-1` through `GS-17.2`) from `events.tsv` (`kind == "stadial onset"`, `unc ∈ {"4yr", "a", "b"}`, no other event in `(t − 200, t + 100)`, `10,500 <= t <= 59,500`):
- Compute mean `VOLC_GL` deposition in `[t, t + 50)` (50 yr before onset) and `[t, t + 150)` (150 yr before onset) across all 19 coolings (and across the 18 non-YD coolings).
- Compare against **10,000 Monte Carlo null draws** (`numpy.random.default_rng(76)`, each drawing 19 uniform random ages in `[10,500, 59,500]`), reporting exact one-sided empirical `p = (1 + count(null >= obs)) / 10001`.

### Decision rules (fixed in advance)

#### Verdict 1 — Platinum-as-trigger test
- **Consistent with trigger:** `age_GICC05(1712.375) >= 12,886` yr b2k (within 10 yr of or before `GS-1` onset) AND `1712.375 >= d_d18o_init` (Pt onset is at or deeper than cooling initiation inside GISP2).
- **Post-dates cooling onset (cannot be the initial trigger):** `age_GICC05(1712.375) < 12,881` yr b2k (Pt onset is `> 15 yr` after `GS-1` onset on `GICC05`) AND at least one of `{d_d18o_step, d_ca_step}` is strictly deeper than `1712.375 m` inside GISP2.
- **Ambiguous / within uncertainty:** Any other outcome.

#### Verdict 2 — 51-kyr volcanic-cluster test (`[12,896, 13,046)` b2k)
- **Unusually strong volcanic cluster:** Both `VOLC_GL` AND `VOLC_BI` reach the **top 5%** of 150-yr windows across 60–9 ka.
- **Elevated in one archive only:** Exactly one of `{VOLC_GL, VOLC_BI}` reaches the **top 5%**.
- **Ordinary background volcanism:** Neither reaches the **top 5%**.

### Checks before the lock
1. Unit tests (`analysis/test_ptvolc.py`) verifying linear depth-to-age interpolation, two-piece step changepoint recovery on synthetic cooling/dust series, cooling-initiation depth detection, 150-yr window volcanic summation with gap exclusion, Monte Carlo null p-value calibration, and every branch of both verdict rules.
2. A **decoy run** (`python3 analysis/ptvolc.py --decoy`) excluding `[12,600, 13,200]` b2k and GISP2 `[1705, 1720] m`, scoring a deterministic decoy window (`seed = 76`) on the real 51-kyr volcanic catalog and a decoy stadial depth interval in GISP2 without inspecting the Younger Dryas target.

## Known weaknesses
- **Petaev et al. (2013) raw table not re-downloaded:** The paper body is paywalled; we use the exact published GISP2 depth boundaries (`1712.375–1712.000 m`, peak `1712.250–1712.125 m`) cross-verified in open-access Svensson et al. (2020) and Green et al. (2025), and test them against public raw GISP2 chemistry, `δ¹⁸O`, and `GICC05` tie-points.
- **What Pt timing does and does not rule out:** Showing that the Pt spike arrived *after* cooling started rules it out as the initial trigger of the Younger Dryas, but does not by itself identify the geochemical source of the platinum (whether a later impact, Icelandic/fissure volcanism, or another source).
- **Single-vendor initial run:** Written and run by Antigravity (Google DeepMind); open to second-vendor review or replication.

## Budget

$0 (all public NOAA / Copernicus / PANGAEA datasets, local computation).
