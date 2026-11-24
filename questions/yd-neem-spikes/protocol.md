# Protocol — Does a second Greenland ice core (NEEM) confirm fewer fire spikes at the Younger Dryas onset?

- **Question:** Issue `#114` (`yd-neem-spikes`)
- **Lane:** `data`
- **Date drafted:** 2026-11-24 (UTC)
- **Budget:** `$0` (public PANGAEA CC-BY-4.0 data; local Python computation)
- **Blinding status:** At the time of drafting and locking this protocol, **zero NEEM ammonium values inside `10,400–15,000 yr b2k` or across any stadial onset have been inspected**. Only PANGAEA metadata headers and a blinded `16,000–17,000 yr b2k` control check confirming column identity (`NH4+` vs `NO3-`) and depth–age alignment were viewed.

---

## 1. Exact scientific question

In Aletheia Lab's Younger Dryas synthesis (`site/topics/younger-dryas.md`), an **exploratory** check in one Greenland ice core (NGRIP 1-mm CFA, `questions/ice-core-fire/explore/repeated_fires.py`) found that during the `150` years after Younger Dryas onset (`12,896–12,746 yr b2k`), the *steady* annual median ammonium level rose `2.7×` (highest of 29 stretches in `10.4–15.0 ka`), whereas *short fire spikes* (`> 5×` running baseline) actually became **rarer** (`4` spike years vs. `18` in the 150 years before and a typical `19`). Because repeated Taurid comet airbursts over a century should leave sharp multi-day fire plumes (`#100`), that finding was a key strike against the drawn-out comet-stream hypothesis—but remained exploratory and single-core.

This study runs a **pre-registered, locked replication** on a second, independent high-resolution Greenland ice core (**NEEM**, `77.45°N, 51.06°W`, ~365 km northwest of NGRIP), testing both the exact NGRIP metric AND two denominator-free controls (additive plume excess and accumulation-flux scaling) to rule out the risk that a rising baseline artificially masks real fire spikes.

---

## 2. Datasets & depth–age mapping (`MANIFEST.md`)

1. **NEEM 1-mm CFA impurities (`data/neem_cfa_1mm.tab`, PANGAEA `10.1594/PANGAEA.935837`, Erhardt et al. 2021/2022):** `[NH4]+` (`µg/kg`, column 5) vs. `Depth ice/snow [m]`.
2. **NEEM 5-cm GICC05 timescale (`data/neem_gicc05_5cm.tab`, PANGAEA `10.1594/PANGAEA.925552`, Gkinis et al. 2021 / Rasmussen et al. 2013 `GICC05modelext-NEEM-1`):** `Depth [m]` vs. `Age [ka b2k]` (GICC05) from `8,000.2` to `60,197.9 yr b2k`. Each 1-mm depth in `neem_cfa_1mm.tab` is linearly interpolated onto GICC05 age (yr b2k) from the 5-cm depth–age table, and local annual layer thickness $\lambda(y) = \Delta z / \Delta t$ (m/yr) is computed directly from the 5-cm table.
3. **Stadial onset catalogue (`events.tsv`, Rasmussen et al. 2014 Table 2):** GICC05 onset ages for `GS-1` (Younger Dryas, `12,896 yr b2k`) and all earlier stadial onsets (`GS-2` through `GS-12` within `10.4–45.0 ka`).

---

## 3. Pre-registered measurements & statistical tests

### Pillar 1 — Exact replication of NGRIP's `10,400–15,000 yr b2k` decomposition in NEEM

For every integer calendar year $y \in [10400, 15000)$ with at least `15` finite 1-mm `[NH4]+` samples:
- $\text{med}_y = \text{median}(x)$ (ordinary steady level for year $y$)
- $\text{mean}_y = \text{mean}(x)$; $\text{spike\_part}_y = \text{mean}_y - \text{med}_y$
- $\text{top}_y = \max(x)$ (annual peak concentration, capturing multi-day wildfire plumes)
- $\text{run}_y = \text{median}\{\text{med}_{y'} : |y' - y| \le 25\}$ (51-year running median of yearly medians, requiring $\ge 30$ valid years)
- **Relative spike ratio (exact NGRIP replication):** $r_y = \text{top}_y / \text{run}_y$; count years with $r_y > 3, 5, 10$ (`spike_years_x3`, `spike_years_x5`, `spike_years_x10`).
- **Additive excess plume control (immune to denominator inflation):** $\Delta_y = \text{top}_y - \text{run}_y$ (`µg/kg`); count years with $\Delta_y > 30, 50, 100\ \mu\text{g/kg}$ (`spike_years_add30`, `spike_years_add50`, `spike_years_add100`).
- **Accumulation-flux plume control (immune to the ~2× snowfall drop at YD onset):** $\Phi_y = \Delta_y \cdot (\lambda_y / \bar{\lambda}_{10.4-15\text{ka}})$ (`µg/kg`-equivalent at mean deglacial layer thickness); count years with $\Phi_y > 50\ \mu\text{g/kg}$ (`spike_years_flux50`).

Group years into contiguous non-overlapping **`150`-year windows** laid out from `ONSET = 12,896 yr b2k`:
- Window `k`: $[\text{ONSET} - 150(k+1),\ \text{ONSET} - 150k)$, requiring $\ge 80\%$ (`120`) valid years.
- **Window `0`** (`12,896 → 12,746 yr b2k`): first 150 years *after* Younger Dryas onset.
- **Window `-1`** (`13,046 → 12,896 yr b2k`): 150 years *before* Younger Dryas onset.

Compute for every window:
1. `level` = mean of $\text{med}_y$; `spike_part` = mean of $(\text{mean}_y - \text{med}_y)$; `share_of_rise_from_level` $= (\text{level}_0 - \text{level}_{-1}) / [(\text{level}_0 + \text{spike\_part}_0) - (\text{level}_{-1} + \text{spike\_part}_{-1})]$.
2. Counts & ranks (out of all valid `150`-year windows in `10.4–15.0 ka`) of `spike_years_x5` (primary relative replication), `spike_years_x3`, `spike_years_x10`, `spike_years_add50` (primary additive control), `spike_years_add30`, `spike_years_add100`, and `spike_years_flux50` (flux control).
3. Two-sided Poisson / Fisher rate-ratio test comparing Window `0` vs. Window `-1` for `spike_years_x5` and `spike_years_add50`, plus empirical percentile of Window `0` across all `10.4–15.0 ka` windows.

### Pillar 2 — Comparison against earlier abrupt stadial coolings (`10.4–45.0 ka`)

Across all Rasmussen et al. (2014) `stadial onset` events between `12.896 ka` (`GS-1`) and `45.0 ka` where NEEM has $\ge 10$ samples/yr in both the `150`-year pre-onset and post-onset windows (and $\ge 100$ valid years per window):
- Compute `level_after / level_before`, `spike_years_x5` before vs. after, and `spike_years_add50` before vs. after.
- Test whether a drop in `spike_years_x5` (or steady-level dominance) is unique to the Younger Dryas or is a general feature of Greenland abrupt coolings!

---

## 4. Pre-registered decision rules (mutually exclusive verdicts)

1. **`replicated_steady_not_spiky`** (confirms NGRIP and rules out denominator artifact):
   - `level_0 / level_{-1} >= 1.5` **AND** `share_of_rise_from_level >= 0.70`, **AND**
   - `spike_years_x5[0] < spike_years_x5[-1]` **AND** `spike_years_x5[0] < median(spike_years_x5)` across `10.4–15.0 ka`, **AND**
   - Additive plume control does **not** surge (`spike_years_add50[0] / max(spike_years_add50[-1], 1) < 1.5` OR rank of `spike_years_add50[0]` is outside the top 10% of windows).
2. **`replicated_relative_but_additive_spikes_rise`** (denominator artifact caught by our control!):
   - `level_0 / level_{-1} >= 1.5` AND `spike_years_x5[0] < spike_years_x5[-1]` AND `< median`, **YET**
   - Additive plumes surge strongly (`spike_years_add50[0] / max(spike_years_add50[-1], 1) >= 1.5` AND `spike_years_add50[0]` ranks in the top 10% of `10.4–15.0 ka` windows).
3. **`failed_to_replicate_more_spikes`** (contradicts NGRIP; supports repeated fires):
   - `spike_years_x5[0] > spike_years_x5[-1]` **AND** `spike_years_x5[0] > median(spike_years_x5)`.
4. **`inconclusive_or_mixed`**:
   - Any intermediate outcome not matching (1)–(3).

---

## 5. Pre-lock verification

`analysis/test_neem_spikes.py` verifies before locking that:
1. Synthetic steady-baseline step (`2.7×` rise, constant low fire-plume rate) triggers `replicated_steady_not_spiky`.
2. Synthetic denominator-masked fire surge (both baseline AND absolute fire plumes jump `3×`) triggers `replicated_relative_but_additive_spikes_rise` or `failed_to_replicate_more_spikes`.
3. Synthetic repeated-airburst century (`4×` jump in `>5×` plume frequency) triggers `failed_to_replicate_more_spikes`.
