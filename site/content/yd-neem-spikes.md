---
# To update this page, edit this file and push to main; the site rebuilds itself.
# The figures are made by questions/yd-neem-spikes/analysis/make_figures.py from the results files.
summary: An exploratory look in one Greenland ice core (NGRIP) found that the Younger Dryas ammonium surge was a smooth baseline rise with fewer short fire spikes—a key strike against repeated Taurid comet airbursts. Here we lock that exact test—plus denominator-free absolute and snowfall-flux plume controls—on a second independent Greenland core (NEEM, 1 mm resolution).
verdict: Replicated in NEEM—steady baseline surge (102% of rise), fewer relative spikes, ordinary absolute plumes
result: Locking the exact test in advance on Greenland's NEEM ice core confirms NGRIP and rules out a denominator artifact. In the 150 years after Younger Dryas onset, NEEM's steady yearly median ammonium jumps 2.58× to the highest level of all 28 stretches in 14.7–10.5 ka (carrying 102% of the total rise), while sharp >5× fire-spike years fall nearly fourfold (8 vs. 31 before onset, p = 0.00032; zero >10× spikes vs. 18 before). Crucially, denominator-free absolute plumes (>50 µg/kg above baseline) and snowfall-flux-scaled plumes remain completely ordinary (18 vs. 14, rank 11/28, p = 0.48; flux 16 vs. 13, p = 0.58)—half the rate seen in warm early-Holocene boreal wildfire centuries.
dek: Converting the lab's exploratory single-core check against repeated Taurid airbursts into a pre-registered, two-core replication—with built-in controls against baseline inflation and snowfall thinning.
updated: 2026-11-24
---

> **Where things stand, 24 November 2026.** Initial locked run finished with zero amendments (by Antigravity / Google DeepMind, directed by Eugene; open to second-vendor replication). Pre-registered verdict: **Replicated—steady baseline, not spiky fires** (`replicated_steady_not_spiky`).

{{figure: yd-neem-spikes/tiles}}

## What we tested and found

Earlier work in the lab found that the single-day comet impact failed on timing and global charcoal, leaving a harder-to-test alternative: a **century of repeated Taurid comet airbursts** lighting fires year after year. An exploratory check on one Greenland ice core (NGRIP) suggested the opposite—that the Younger Dryas ammonium rise sat entirely in the *steady* background level while short smoke spikes actually became scarcer.

Two honest doubts remained: first, an exploratory single-core check is never definitive; second, if the steady baseline jumped `2.5×`, dividing peak concentrations by that higher baseline (`peak / baseline > 5`) could hide constant-amplitude fire plumes through a pure denominator effect.

We locked both the exact NGRIP test and two denominator-free controls (absolute plume excess `> 50 µg/kg` above baseline and snowfall-flux-scaled plumes using NEEM's 5-cm GICC05 layer thickness) before opening a single Younger Dryas value in **NEEM**—a second independent deep core 365 km northwest of NGRIP (`1 mm` continuous-flow resolution, ~25 samples per year).

{{figure: yd-neem-spikes/verdict}}

## Twenty-eight 150-year stretches compared

Across all `28` valid 150-year stretches from `14,696` to `10,496` years before 2000 CE, NEEM reproduces NGRIP almost number for number:

- **Steady baseline (`#1` of `28`):** Yearly median ammonium jumps **`2.58×`** (`11.30 → 29.15 µg/kg`), carrying **`102%`** of the total ammonium rise—while the short-plume excess (`mean − median`) actually shrinks from `0.87` to `0.59 µg/kg`.
- **Relative fire spikes drop nearly fourfold:** Years with a peak `> 5×` the 51-year running median fall from **`31`** in the 150 years before onset (median `29.5`) down to **`8`** after onset (`p = 0.00032`), and extreme `> 10×` spikes drop from **`18`** to **`0`**.
- **No hidden fire surge under denominator-free controls:** Absolute plumes exceeding `50 µg/kg` above baseline stay completely ordinary (**`18`** after vs. **`14`** before, rank `11` of `28`, `p = 0.48`), as do snowfall-flux-scaled plumes (**`16`** vs. **`13`**, `p = 0.58`). By contrast, when North American boreal forests expand in the warm early Holocene (`11.7–10.5 ka`), real wildfires drive *every* fire metric upward at once (`32–57` relative `>5×` years, `19–36` additive `>50 µg/kg` plumes, and `spike_part = 2.7–4.4 µg/kg`).

{{figure: yd-neem-spikes/decomposition}}

## Year by year across the onset

Plotting every year from `13,500` to `12,000` years ago shows the structure at a glance: after `12,896` b2k, the smooth yearly median lifts onto a high shelf for over a century while extreme multi-day plume stems shrink (the largest plume after onset, `162 µg/kg`, is less than half the largest plume before onset, `337 µg/kg`).

{{figure: yd-neem-spikes/annual}}

## What this means

The lab's key ice-core test against the drawn-out Taurid comet-stream model is no longer an exploratory single-core observation. Two independent Greenland ice cores 365 km apart agree: whatever raised Greenland's ammonium after the Younger Dryas began—soil dust, wind shifts, and biological emissions during abrupt cooling—raised the smooth background level without filling the sky with repeated airburst wildfire plumes.

::: details Methods, data, and verification
- **Protocol and lock:** `questions/yd-neem-spikes/protocol.md`, locked at `2026-11-24T05:26:51Z` (`protocol.lock`, SHA-256 `787ad4de9a5d`). Zero amendments.
- **Public datasets:** Erhardt et al. (2021/2022) NEEM 1-mm CFA (`PANGAEA.935837`, CC-BY-4.0), NEEM 10-yr CFA (`PANGAEA.935831`, used for blinded `16–17 ka` column-identity verification confirming no `NH4+`/`NO3-` swap), Gkinis et al. (2021) / Rasmussen et al. (2013) 5-cm `GICC05modelext-NEEM-1` timescale (`PANGAEA.925552`), and Rasmussen et al. (2014) stadial onsets (`events.tsv`). Full SHA-256 hashes in `questions/yd-neem-spikes/MANIFEST.md`.
- **Full report and code:** `questions/yd-neem-spikes/RESULTS.md`, `questions/yd-neem-spikes/analysis/neem_spikes.py`, and `questions/yd-neem-spikes/analysis/test_neem_spikes.py` (`3/3` synthetic recovery tests passing, including catching a denominator-masked fire surge).
:::
