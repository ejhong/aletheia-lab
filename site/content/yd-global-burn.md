---
# To update this page, edit this file and push to main; the site rebuilds itself.
# The figures are made by questions/yd-global-burn/analysis/make_figures.py from the results files.
summary: Supporters of the Younger Dryas impact hypothesis argue ~9% of Earth's biomass burned 12,800 years ago. Do Antarctic air and global lake charcoal agree?
verdict: No global firestorm; atmospheric carbon shift is small, late, and matches Heinrich Stadials
result: Across 19 well-dated high-resolution global charcoal records (GCD3), only 1 site exceeds +1 SD at 12,800 years ago (rank 38 of 45; zero in North America), even though simulations show the network catches a real global fire 95–100% of the time; apparent peaks appear only in coarse, low-resolution cores. In Antarctic ice, the CO₂ and δ¹³C-CO₂ shift is flat at the onset, peaks 150–450 years later, is 4×–14× too small for burning 9% of Earth's biomass, and matches Heinrich Stadials 1 and 4.
dek: Earlier lab tests looked at Greenland ammonium—a regional record of North America. Here we test the global burning claim directly in two independent planetary archives—Antarctic air and the Global Charcoal Database—with every rule locked before looking at 12,800 years ago.
updated: 2026-11-23
---

> **Where things stand, 23 November 2026.** Finished (run by Antigravity / Google DeepMind, directed by Eugene; independently replicated by Claude Fable 5.2 from the written plan, with the same results). By the pre-registered rule, global charcoal is **Not met** (0 of 3 primary measures) and Antarctic air is **Single-record only** (1 of 3 primary measures), giving a joint label of **Partial / mixed**. Physically, neither archive supports burning ~9% of Earth's biomass at 12,800 years ago.

## What we figured out

Supporters of the Younger Dryas impact hypothesis (Wolbach et al. 2018) argue that a cosmic impact 12,800 years ago burned ~10 million km²—about 9% of Earth's terrestrial biomass—and triggered an "impact winter". Two earlier questions here ([`ice-core-fire`](../ice-core-fire/) and [`cooling-ammonium`](../cooling-ammonium/)) checked Greenland ammonium and found a century-long swell starting 30–40 years *after* the cold began, alongside smaller rises after most other sudden coolings of the ice age.

Greenland ice mainly sees North America. So we tested the **global** burning claim directly in two completely independent public NOAA archives, locking every formula and threshold before looking at any value between 12,000 and 13,600 years ago:

1. **Global air (Antarctic ice cores):** Well-mixed global CO₂ and its carbon-13 ratio (`δ¹³C-CO₂`) in Taylor Glacier, WAIS Divide, and a 155,000-year three-core Antarctic compilation. Burning ~9% of Earth's land biomass (~50–90 GtC of isotopically light C₃ carbon at `−25‰`) must raise CO₂ and pull `δ¹³C-CO₂` sharply downward at the same time.
2. **Global land charcoal (Global Charcoal Database v3):** 736 sediment charcoal cores worldwide, filtered before looking to well-dated, high-resolution cores spanning the past 13,500 years (`Tier C1`, 19 sites across six continents), alongside coarser cores (`Tier C3_coarse`, 43 sites) to test whether low-resolution binning creates false spikes.

{{figure: yd-global-burn/ranks}}

Five things came out.

1. **High-resolution global charcoal is quiet at 12,800 years ago.** In `Tier C1` (19 well-dated high-resolution sites), only **1 site out of 19** exceeds `+1.0 SD` in `[12,650, 12,950)` cal BP (Lake Albert in Uganda; rank 38 of 45), **0 of 19** exceed `+1.5 SD`, local excess `E_mean` is `0.000` (rank 20/45), and peak 100-year excess `E_100` ranks 12th of 45. Across all 26 high-resolution sites (`Tier C2`), `[12,650, 12,950)` ranks **44th of 45**—the second quietest 300-year stretch in 13,500 years. In North America—supposed ground zero—**zero** high-resolution sites reach `+1.0 SD` (`0/7` in C1, `0/12` in C2, `0/14` in C3).
2. **The charcoal network would easily have caught a real global fire.** In 200 simulated placements on the exact same 19 `Tier C1` sites, a 100-year fire pulse of `+1.5 SD` across half of global sites hits the top 5% of `E_100` **98% of the time** and **Rank 1** 95% of the time (and `+1.0 SD` across 75% of sites hits Rank 1 **95% of the time**). The absence of a signal is real, not lack of sensitivity.
3. **Coarse cores manufacture the illusion of a 12,800-year peak.** Restricted to low-resolution cores (`median spacing > 100 yr`, 43 sites), the share of sites exceeding `+1.5 SD` jumps from **0/26 (0%)** in high-resolution cores to **5/41 (12.2%, rank 2 of 45)**—reproducing Marlon et al. (2009)'s resolution-artifact warning on a global dataset. All five of those coarse sites lie in Papua New Guinea and Patagonia, with just 1 or 2 samples each inside the 300-year window.
4. **Antarctic air fails the primary combustion test at the onset and matches ordinary Heinrich Stadials.** In `[12,650, 12,950)` cal BP, Taylor Glacier's combined combustion score (`TG_BURN`) ranks **7th of 54** (`0.488 ppm·‰`, missing top 5%) and WAIS Divide `CO₂` rise ranks **14th of 38** (`+4.52 ppm`). Only the smoothed 155,000-year Eggleston `δ¹³C-CO₂` composite hits top 5% (tied 4th of 499 at just `0.030‰`), sitting behind three windows of Heinrich Stadial 1 (`16.8–17.7 ka`) and tied with Heinrich Stadial 1 (`16.5–16.8 ka`) and Heinrich Stadial 5 (`47.1–47.4 ka`).
5. **The carbon shift is too late and an order of magnitude too small for 9% of Earth's biomass.** Single-box isotopic mass balance on Taylor Glacier's `k = 0` step (`ΔCO₂ = +4.33 ppm`, `Δδ¹³C = −0.113‰`) yields only **`3.17 GtC`** of airborne terrestrial carbon (`+1.49 ppm` CO₂—about a third of the observed CO₂ rise, indicating mostly heavier oceanic carbon). Even assuming 100% came from burning land biomass, that implies only `6.3–12.7 GtC` emitted—**4× to 14× smaller** than burning ~9% of Earth's biomass (~50–90 GtC).

## Antarctic air: Younger Dryas vs. Heinrich Stadials

{{figure: yd-global-burn/atmosphere}}

Post-lock inspection of the raw Taylor Glacier data (`taylor2018d13co2.txt`) makes the physics unmistakable. Across the Younger Dryas onset (`12,937 → 12,786 → 12,751` cal BP), both `CO₂` (`242.3 → 242.5 → 242.4 ppm`) and `δ¹³C-CO₂` (`−6.627 → −6.621 → −6.615‰`) are completely flat.

Only **100 to 270 years later** (`12,751 → 12,580` cal BP) does `CO₂` climb `+5.9 ppm` while `δ¹³C-CO₂` drops `−0.165‰`, pushing the *next* window (`[12,350, 12,650)`, `k = −1`) to Rank 2 of 54 (`0.955 ppm·‰`). That delayed drop is a near-identical twin of **Heinrich Stadial 1** (`15,950–16,250` BP, Rank 1 at `0.957 ppm·‰`; `16,450 → 16,250` BP, `−0.180‰`) and **Heinrich Stadial 4** (`39,650–39,950` BP, Rank 3 at `0.852 ppm·‰`, `−0.138‰`). Whenever North Atlantic overturning shuts down, the Southern Ocean warms and vents isotopically light deep carbon over several centuries—no comet required.

## Global charcoal and detection power

{{figure: yd-global-burn/charcoal}}

Across 13,500 years of well-dated, high-resolution charcoal (`Tier C1`), fire activity does surge synchronously—just **not** at the Younger Dryas cold onset. The #1 peaking window (`29.4%` of sites `≥ +1.0 SD`) is **`11,450–11,750` cal BP**, the abrupt *warming* that ended the Younger Dryas, and the #1 peak in 100-year excess `E_100` is `13,550–13,850` cal BP.

## What this does—and does not—settle

Taken together with [`ice-core-fire`](../ice-core-fire/) and [`cooling-ammonium`](../cooling-ammonium/), the "global wildfire / 9% of Earth's biomass burned / impact winter" mechanism of the Younger Dryas impact hypothesis does not hold up in public global records:

- Greenland ammonium swells 30–140 years *after* the cold starts and is an extreme case of a common cooling response.
- High-resolution global charcoal—including every well-resolved North American core in GCD3—shows no fire peak at 12,800 years ago, despite 95–100% power to detect one.
- Global atmospheric `CO₂` and `δ¹³C-CO₂` in Antarctica are flat at onset, drop centuries later by an amount 4×–14× too small for burning 9% of Earth's biomass, and mirror Heinrich Stadials 1 and 4.

This study does **not** test whether a cosmic impact occurred without triggering global wildfires (for example, over an ice sheet or ocean), nor does it evaluate platinum anomalies, microspherules, meltglass, or shocked quartz.

::: details Methods, data, and sensitivity checks
- **Protocol and lock:** `questions/yd-global-burn/protocol.md`, locked at `2026-11-23T15:34:23Z` (`protocol.lock`, SHA-256 `bf2fe12a3d45...`) before viewing any value inside `[12,000, 13,600]` cal BP. Zero amendments.
- **Public NOAA datasets:** Taylor Glacier `taylor2018d13co2.txt` (Bauska et al. 2016, 2018), WAIS Divide `antarctica2015co2wais-noaa.txt` (Marcott et al. 2014 / Bereiter et al. 2015), Antarctic 155 kyr composite `eggleston2016d13co2-noaa.txt` (Eggleston et al. 2016), and Global Charcoal Database v3 `GCD3_PUBLIC_VERSION_2013_01-Oct-2013.mdb` (Marlon et al. 2016). Full URLs and SHA-256 hashes in `questions/yd-global-burn/MANIFEST.md`.
- **Sensitivity checks:** Testing 150-year (`[12,725, 12,875)`), 600-year (`[12,500, 13,100)`), and ±150-year shifted windows leaves every verdict unchanged: Archive B never reaches the top 5% in any variant, and Archive A never moves beyond `Single-record only`.
- **Full report and code:** `questions/yd-global-burn/RESULTS.md`, `questions/yd-global-burn/analysis/burn.py`, and `questions/yd-global-burn/analysis/test_burn.py` (10 unit tests passing).
:::
