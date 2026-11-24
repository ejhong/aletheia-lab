# Protocol — Did extraterrestrial Helium-3 cosmic dust rise across the Younger Dryas deglaciation?

**Issue:** `#121` (`yd-cosmic-dust-he3`)  
**Lane:** `data`  
**Budget:** `$0` (open public-domain / CC-BY geochemical archives, local CPU only)  
**Status:** Pre-registered prior to inspecting or computing any `³He_ET` flux values across the Younger Dryas / deglaciation.

---

## 1. Exact Question

The drawn-out Taurid comet-breakup version of the Younger Dryas Impact Hypothesis (Clube & Napier 1984; Napier 2010) proposes that a giant comet fragmented in the inner solar system over the past ~20,000 years, flooding Earth's orbit with debris and micron-sized dust. Unlike fire, cooling, or platinum anomalies—which terrestrial processes can mimic or shift—**extraterrestrial Helium-3 (`³He_ET`)** carried by solar-wind-implanted interplanetary dust particles (IDPs, typically `< 50 µm`) has a `³He/⁴He` ratio roughly **10,000× higher** (`~4 × 10⁻⁴`) than terrestrial rocks or volcanic ash (`~2 × 10⁻⁸`). Neither wildfires, volcanism, nor ocean circulation can fabricate an extraterrestrial `³He_ET` flux surge.

We ask:

> **Across independently dated, ice-free pelagic ocean cores with dilution- and focusing-invariant `²³⁰Th_xs,0`-normalized `³He_ET` flux records—benchmarked against real documented Cenozoic cosmic-breakup dust showers on the exact same `³He_ET` tracer—did Earth's global extraterrestrial `³He_ET` dust flux rise during the Younger Dryas (`13.5–11.5 ka`), the Late Deglaciation (`15.0–10.0 ka`), or the broad giant-comet breakup epoch (`20.0–10.0 ka`) relative to Holocene (`< 10 ka`) and glacial (`> 20 ka`) baselines?**

---

## 2. Primary Data & Physics

All 9 primary files are listed in [MANIFEST.md](MANIFEST.md) with URLs, licences, byte sizes, and SHA-256 checksums.

### 2.1 Pillar 0 — Real Cosmic-Breakup Positive Controls (`n = 208` samples, 2 oceans)
To prove our detector reliably catches real extraterrestrial dust showers on `³He_ET` flux:
- **Farley, Vokrouhlický, Bottke & Nesvorný (2006, *Nature*):**
  1. `ODP Hole 121-757B` (South Indian Ocean, `PANGAEA.769829`, `n = 135`, `3.06–38.05 Ma`): tests BOTH the **Late Miocene `8.2 Ma` Veritas asteroid-family breakup** (`8.35–7.50 Ma` vs. `10.50–8.50` & `7.20–6.20 Ma` baseline) AND the **Late Eocene `~35.5 Ma` comet/asteroid shower** (`36.50–34.50 Ma` vs. `33.50–25.00 Ma` baseline).
  2. `ODP Hole 154-926B` (Equatorial Atlantic, `PANGAEA.769830`, `n = 73`, `6.21–10.50 Ma`): independently replicates the **`8.2 Ma` Veritas breakup** (`8.35–7.50 Ma` vs. `10.50–8.50` & `7.20–6.20 Ma`) in a second ocean basin.

### 2.2 Pillar 1 — Primary Gold-Standard `²³⁰Th_xs,0`-Normalized `³He_ET` Flux (`7` ice-free Pacific pelagic cores, `2` independent labs, `n = 187` paired samples)
In marine sediments, raw `[³He_ET]` (`pcc g⁻¹`) varies inversely with terrestrial dust, carbonate, or opal dilution, while chronostratigraphic burial rates vary with lateral sediment focusing/winnowing by bottom currents. Normalizing `[³He_ET]` by **`²³⁰Th_xs,0`-derived vertical mass accumulation rate (`vMAR_Th = β · z / [²³⁰Th_xs,0]`)** cancels BOTH dilution AND lateral focusing identically, isolating the true vertical cosmic dust rain rate `F_{3He}` (in `pcc STP cm⁻² kyr⁻¹ = 10⁻¹² cm³ STP cm⁻² kyr⁻¹`):
$$F_{^3\text{He,ET}} = [^3\text{He}_{\text{ET}}] \times \text{vMAR}_{^{230}\text{Th}}$$

1. **Subarctic North Pacific — Core `SO202-07-6`** (`51.27°N, 167.70°E`, `2,345 m`; **Serno, Winckler, Anderson et al. 2015**, Lamont-Doherty, `PANGAEA.845998` + `42` AMS `¹⁴C` dates in `PANGAEA.845972`, `20` inside `11.5–13.5 ka`):
   - `n = 51` paired samples spanning `3.89–27.07 ka BP` (`7` in `0–10 ka`, `22` in `10–15 ka` including `8` in `11.5–13.5 ka`, `18` in `15–25 ka`, `4` in `25–27 ka`).
   - Extraterrestrial fraction deconvolved via the standard McGee & Mukhopadhyay (2013) two-endmember equation (`R_ET = 4.0 × 10⁻⁴`, `R_terr = 2.0 × 10⁻⁸`; plus sensitivity check at `R_terr = 2.0 × 10⁻⁷`):
     $$[^3\text{He}_{\text{ET}}] = [^3\text{He}_{\text{meas}}] \times \frac{1 - R_{\text{terr}}/R_{\text{meas}}}{1 - R_{\text{terr}}/R_{\text{ET}}}$$
   - Unit conversion from PANGAEA columns (`3He` in `10⁻¹⁰ cm³/g = 100 pcc/g`, `²³⁰Th`-normalized `MAR` in `g m⁻² yr⁻¹ = 0.1 g cm⁻² kyr⁻¹`):
     $$F_{^3\text{He,ET}}\;[\text{pcc cm}^{-2}\text{ kyr}^{-1}] = 10 \times [^3\text{He}_{\text{ET}},\,10^{-10}\text{ cm}^3/\text{g}] \times \text{MAR}_{^{230}\text{Th}}\;[\text{g m}^{-2}\text{ yr}^{-1}]$$
2. **Eastern Equatorial Pacific (Cocos Ridge) — Cores `CR01`, `CR02`, `CR03`, `CR05`** (`~5–6°N, 86–87°W`; **Tomchovska, Pavia & Farley 2025/2026**, Caltech, `Figshare 30340705`, `67` AMS `¹⁴C` dates):
   - `n = 76` paired `²³⁰Th_xs,0` + `[³He_ET]` samples (`CR01: 18`, `CR02: 23`, `CR03: 17`, `CR05: 18`) matched 1-to-1 to radiocarbon-calibrated `Calendar Age (Kyr)` (`0.00–21.44 ka BP`: `49` in `0–10 ka`, `12` in `10–15 ka`, `15` in `15–25 ka`).
   - Exact flux: `F_{3He} = [³He_ET, pcc/g] × Th-based MAR [g cm⁻² kyr⁻¹]`.
3. **Central Equatorial Pacific — Cores `MANOP_B18` & `MANOP_B25`** (`~1°N, 139°W`; **Marcantonio, Anderson, Higgins et al. 2001**, Lamont-Doherty, `PANGAEA.846689`):
   - `n = 60` paired `²³⁰Th`-normalized `³He_ET` flux rows spanning `0.3–325 ka BP` (`5` in `0–10 ka`, `5` in `10–25 ka`, `50` across `25–325 ka` anchoring the deep Late Quaternary glacial/interglacial baseline).

### 2.3 Pillar 2 — Secondary North Atlantic Replication (`n = 117` samples) & Polar Ice-Core Reference (`n = 18` samples)
4. **Central North Atlantic (Mid-Atlantic Ridge) — Cores `KN207-2-GGC3` (`26.14°N, 44.80°W`, `n = 42`, `2.2–49.5 ka`) & `KN207-2-GGC6` (`29.21°N, 43.23°W`, `n = 75`, `0.5–68.8 ka`)** (**Middleton et al. 2018**, *EPSL* / NOAA Study `25870`, UC Davis / Harvard):
   - Because `²³⁰Th` is not tabulated in the NOAA file, we compute chronostratigraphic relative burial rate `B_{3He} ∝ [³He_ET] × (Δz / Δt)` (using centered local linear sedimentation rate `LSR` from the published `depth_cm`–`age_calkaBP` sequence, where constant bulk density cancels in within-core ratios) alongside raw `[³He_ET]` concentration. Analysed separately as a secondary Atlantic check (explicitly noting potential bottom-current focusing).
5. **Polar Ice-Core Reference — `GISP2` Greenland (`0.4 ka`) & `Vostok` Antarctica (`1–4 ka` & `75–97 ka`)** (**Brook et al. 2000**, *GRL* / NOAA Study `2454`, `n = 18`):
   - Anchors the direct ice-core absolute `³He_ET` flux baseline (`pcc STP cm⁻² kyr⁻¹`) against our pelagic marine records (explicitly noting its `4–75 ka` gap).

---

## 3. Exact Pre-Registered Windows & Statistical Tests

### 3.1 Three Pre-Registered Target Windows
To test every proposed timescale of the Taurid breakup / YDIH cosmic-dust hypothesis fairly:
- **Window W1 — Narrow Younger Dryas / YDB (`13.5–11.5 ka BP`):** Centered on `12.85 ka` with `±1 kyr` margin for marine radiocarbon reservoir uncertainty and pelagic bioturbation mixing. Baseline = all samples outside `13.5–11.5 ka` (`< 11.5 ka` or `> 13.5 ka`).
- **Window W2 — Full Late Deglacial (`15.0–10.0 ka BP`):** Spans Bølling–Allerød through Younger Dryas into earliest Preboreal. Baseline = all samples outside `15.0–10.0 ka` (`< 10.0 ka` or `> 15.0 ka`).
- **Window W3 — Broad Giant-Comet Breakup Epoch (`20.0–10.0 ka BP`):** Tests Clube & Napier's multi-millennial deglacial giant-comet fragmentation window. Baseline = Holocene (`< 10.0 ka`) + pre-20 ka glacial (`> 20.0 ka`). *(We also report `W3` split separately against Holocene `< 10 ka` and Glacial `> 20 ka` to verify no hidden glacial-interglacial baseline drift.)*

### 3.2 Core-Normalized Pooling & Statistics (Fixed RNG Seed `20261124`)
Because minor site-specific winnowing or scavenging offsets can shift a core's absolute baseline mean (e.g. `0.5` vs `0.9 pcc cm⁻² kyr⁻¹`), for each window we normalize every sample inside each core by that core's **own baseline median**:
$$\tilde{F}_{c,i} = \frac{F_{c,i}}{\text{median}(F_{c,\text{baseline}})}$$
(only cores with `n_baseline ≥ 3` enter a given window's core-normalized pool; all cores are also reported in raw `pcc STP cm⁻² kyr⁻¹`).

For each window (`W1`, `W2`, `W3`) in Pillar 1 (pooled across all 7 Pacific cores, plus separately for **Subarctic North Pacific `SO202-07-6`**, **Cocos Ridge `CR01–CR05`**, and **Central Equatorial Pacific `B18/B25`**) and Pillar 2 (**Mid-Atlantic Ridge `GGC3 + GGC6`**):
1. **Median Flux Ratio (`M_ratio`) & Bootstrap 95% CI (`10,000` stratified resamples):** `median(F_tilde_target) / median(F_tilde_baseline)` (`1.00` under constant flux), with 2.5th and 97.5th percentiles `[CI_lo, CI_hi]`. The upper bound `CI_hi` defines the **95% upper limit on any sustained cosmic-dust surge**.
2. **Stratified Within-Core Permutation Test (`10,000` permutations):** Randomly permutes target/baseline labels *within each core* (preserving exact core-level sample counts and variance), computing one-sided `p_perm = (1 + #{M_sim ≥ M_obs}) / 10001` for `H_1: F_target > F_baseline`.
3. **Mean Ratio & Nugget-Outlier Blind Peak Scan:** Reports arithmetic mean ratio alongside the nugget-resistant median ratio, AND ranks the **top 10% highest core-normalized `³He_ET` flux samples** across the entire Pillar 1 database without boundary labels to test whether cosmic-dust spikes cluster inside `13.5–11.5 ka` / `15–10 ka` (hypergeometric / Fisher exact test).
4. **Endmember Sensitivity Check:** Re-runs `SO202-07-6` using `R_terr = 2.0 × 10⁻⁷` (10× higher terrestrial `³He/⁴He`) to verify results are insensitive to terrestrial endmember choice.

---

## 4. Pre-Registered Verdict Rules (Mutually Exclusive)

1. **`cosmic_dust_surge_detected`**:
   - All 3 Pillar 0 positive controls pass (`Farley 2006` Veritas `8.2 Ma` in `ODP 757B`, Veritas `8.2 Ma` in `ODP 926B`, and Late Eocene `35.5 Ma` in `ODP 757B`: each `M_ratio ≥ 2.00` and `p_perm < 0.01`); AND
   - In Pillar 1 (pooled core-normalized `²³⁰Th`-calibrated `³He_ET` flux), **at least one** of `W1` (`13.5–11.5 ka`), `W2` (`15.0–10.0 ka`), or `W3` (`20.0–10.0 ka`) yields **`M_ratio ≥ 1.50`** AND one-sided stratified permutation **`p_perm < 0.01`**, replicated with `M_ratio > 1.25` in **both** the Subarctic North Pacific (`SO202-07-6`) **and** the Equatorial Pacific Cocos Ridge stack (`CR01–CR05`).
2. **`no_cosmic_dust_surge`**:
   - All 3 Pillar 0 positive controls pass (`M_ratio ≥ 2.00` and `p_perm < 0.01`); AND
   - In Pillar 1 (pooled `²³⁰Th`-normalized `³He_ET` flux), **all three** windows (`W1`, `W2`, `W3`) fail to show a significant elevation (`p_perm ≥ 0.05` OR `M_ratio < 1.20`), **AND** the bootstrap 95% upper confidence bound on `M_ratio` is **`< 1.50`** for `W2` (`15–10 ka`) and **`< 1.80`** for `W1` (`13.5–11.5 ka`).
3. **`ambiguous_or_mixed`**:
   - Any outcome not cleanly satisfying (1) or (2) — including if any positive control fails, if one ocean basin shows a large elevation while the other does not, or if scatter leaves the 95% upper bound too wide to exclude a `≥ 1.50×` (`W2`) / `≥ 1.80×` (`W1`) surge.

---

## 5. Pre-Lock Synthetic Verification

Before locking `protocol.lock` and before running on real data, `analysis/test_cosmic_dust_he3.py` must pass all synthetic verification tests:
1. **Exact physics & unit conversion:** Verify McGee & Mukhopadhyay (2013) `³He_ET` deconvolution recovers exact synthetic extraterrestrial fractions (`>99%` at `R_meas = 10⁻⁴`, `0%` at `R_meas = R_terr`) and `SO202-07-6` unit conversion gives `0.80 pcc cm⁻² kyr⁻¹` for `[³He_ET] = 0.01 × 10⁻¹⁰ cm³/g` and `MAR = 8.0 g m⁻² yr⁻¹`.
2. **Synthetic flat constant-flux null (`7` cores matching exact real sample counts & ages, `25%` log-normal IDP scatter):** Cleanly triggers `no_cosmic_dust_surge` (`M_ratio ≈ 1.0`, `p_perm > 0.1`, `CI_hi < 1.50`).
3. **Synthetic `2.5×` narrow Younger Dryas (`13.5–11.5 ka`) cosmic-dust surge:** Cleanly triggers `cosmic_dust_surge_detected` (`M_ratio ≈ 2.5`, `p_perm < 0.001`).
4. **Synthetic `2.5×` broad deglacial (`20–10 ka`) Taurid breakup dust cloud:** Cleanly triggers `cosmic_dust_surge_detected` (`M_ratio ≈ 2.5`, `p_perm < 0.001`).
5. **Nugget-outlier resistance:** Injecting two isolated `8×` single-sample IDP nuggets into an otherwise flat `13.5–11.5 ka` window does NOT falsely trigger `cosmic_dust_surge_detected` on the median estimator.
