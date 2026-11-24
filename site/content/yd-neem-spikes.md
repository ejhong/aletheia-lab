---
# To update this page, edit this file and push to main; the site rebuilds itself.
# The figures are made by questions/yd-neem-spikes/analysis/make_figures.py from the results files.
summary: An earlier, exploratory look at one Greenland ice core (NGRIP) found that the Younger Dryas rise in ammonium was a raised background with few sharp spikes, where a century of repeated fires should leave many. Here the same test, with two added counts of plumes in absolute terms, was fixed in advance and run on a second core (NEEM).
verdict: A raised background in a second core, and no large surge of big plumes; a modest one is not ruled out
result: In the 150 years after the cold began, the ordinary yearly level of ammonium in the NEEM core is 2.6 times what it was before, the highest of 28 such stretches, and that accounts for the whole rise. Years with a large plume above that level are 18 against 14 before, which rules out a tripling of big fires and not a smaller rise. The count of spikes relative to the background fell from 31 to 8, but a spot check showed that this is what a fourfold higher background does by arithmetic, so it says nothing about fire. The test bears on a century of repeated fires, a version of the hypothesis we built ourselves; its authors describe a single day.
dek: The lab's one-core check against a century of repeated airburst fires, fixed in advance and run on a second core. Spot-checked afterwards; not replicated.
updated: 2026-11-24
---

> **Where things stand, 24 November 2026.** The locked run finished with no amendments (by Antigravity, Google DeepMind, directed by Eugene). The verdict by the rule fixed in advance is **replicated: steady background, not spiky fires**. A spot check by Claude Fable 5.2 (Anthropic) reran the program and got the same numbers, and found that the write-up claimed more than they show: see the next section. No model from a second company has replicated the study, and none is planned for now.

{{figure: yd-neem-spikes/tiles}}

## Spot check: what holds and what does not

Anthropic's model checked this study after it was published and reran its program. Every number came out the same. Three of the claims made from them did not hold up, and the page has been corrected. The figures on this page are as first made.

- **The raised background holds.** The ordinary level of ammonium is 2.6 times higher after the cold began, the highest of 28 stretches.
- **"Fewer fire spikes" does not hold.** That count divides each year's peak by a running background. The background rose about fourfold, so far fewer peaks clear a bar set at five times it. Put the earlier plumes on the later background and 5 years pass; put the later plumes on the earlier background and 52 do. The drop from 31 to 8 is arithmetic, not a change in fire.
- **"No hidden surge" holds only for a large one.** Years with a plume more than 50 µg/kg above the background number 18 after and 14 before: a ratio of 1.33, anywhere from 0.63 to 2.9. A tripling is ruled out. A rise of a half is not. A count the plan also fixed, plumes above 30 µg/kg, went from 23 to 37 and was left out of the first report.
- **The test cannot see a short plume directly.** A year of ice at this depth is about two centimetres thick and the sharpest spikes are about that wide, so smoke that arrived over a few days is spread across most of a year.

The full list is in the study's `RESULTS.md`, and the checking script is in `questions/yd-neem-spikes/spotcheck/`.

## What we tested and found

Earlier work in the lab found that the single-day comet impact failed on timing and global charcoal, leaving a harder-to-test alternative: a **century of repeated Taurid comet airbursts** lighting fires year after year. An exploratory check on one Greenland ice core (NGRIP) suggested the opposite—that the Younger Dryas ammonium rise sat entirely in the *steady* background level while short smoke spikes actually became scarcer.

Two honest doubts remained: first, an exploratory single-core check is never definitive; second, if the steady baseline jumped `2.5×`, dividing peak concentrations by that higher baseline (`peak / baseline > 5`) could hide constant-amplitude fire plumes through a pure denominator effect.

We locked both the exact NGRIP test and two denominator-free controls (absolute plume excess `> 50 µg/kg` above baseline and snowfall-flux-scaled plumes using NEEM's 5-cm GICC05 layer thickness) before opening a single Younger Dryas value in **NEEM**—a second deep core about 350 km northwest of NGRIP (`1 mm` continuous-flow resolution, ~25 samples per year).

{{figure: yd-neem-spikes/verdict}}

## Twenty-eight 150-year stretches compared

Across all `28` valid 150-year stretches from `14,696` to `10,496` years before 2000 CE, NEEM gives the same picture as NGRIP:

- **Steady baseline (`#1` of `28`):** Yearly median ammonium jumps **`2.58×`** (`11.30 → 29.15 µg/kg`), carrying **`102%`** of the total ammonium rise—while the short-plume excess (`mean − median`) actually shrinks from `0.87` to `0.59 µg/kg`.
- **Relative spikes drop nearly fourfold (an effect of the higher background, as the spot check shows):** Years with a peak `> 5×` the 51-year running median fall from **`31`** in the 150 years before onset (median `29.5`) down to **`8`** after onset (`p = 0.00032`), and extreme `> 10×` spikes drop from **`18`** to **`0`**.
- **No large surge in plumes counted in absolute terms:** Plumes exceeding `50 µg/kg` above baseline stay ordinary (**`18`** after vs. **`14`** before, rank `11` of `28`, `p = 0.48`), as do snowfall-flux-scaled plumes (**`16`** vs. **`13`**, `p = 0.58`). In the early Holocene (`11.7–10.5 ka`) every one of these counts is higher (`32–57` relative `>5×` years, `19–36` plumes above `50 µg/kg`, and `spike_part = 2.6–4.4 µg/kg`), but that ice has 34 to 44 samples a year against 21 to 25 here, so the comparison is not like for like.

{{figure: yd-neem-spikes/decomposition}}

## Year by year across the onset

Plotting every year from `13,500` to `12,000` years ago shows the structure at a glance: after `12,896` b2k, the smooth yearly median lifts onto a high shelf for over a century while extreme multi-day plume stems shrink (the largest plume after onset, `162 µg/kg`, is less than half the largest plume before onset, `337 µg/kg`).

{{figure: yd-neem-spikes/annual}}

## What this means

Two Greenland ice cores about 350 km apart agree that whatever raised the ammonium after the Younger Dryas began raised the smooth background level. Neither shows a large increase in big smoke plumes. That counts against a century of repeated airburst fires, which is a version of the hypothesis that we built to give it its best chance and that its authors do not propose; they describe a single day. The test cannot rule out a modest rise in fires, and it was not built to find one day's burst.

::: details Methods, data, and verification
- **Protocol and lock:** `questions/yd-neem-spikes/protocol.md`, locked at `2026-11-24T05:26:51Z` (`protocol.lock`, SHA-256 `787ad4de9a5d`). Zero amendments.
- **Public datasets:** Erhardt et al. (2021/2022) NEEM 1-mm CFA (`PANGAEA.935837`, CC-BY-4.0), NEEM 10-yr CFA (`PANGAEA.935831`, used for blinded `16–17 ka` column-identity verification confirming no `NH4+`/`NO3-` swap), Gkinis et al. (2021) / Rasmussen et al. (2013) 5-cm `GICC05modelext-NEEM-1` timescale (`PANGAEA.925552`), and Rasmussen et al. (2014) stadial onsets (`events.tsv`). Full SHA-256 hashes in `questions/yd-neem-spikes/MANIFEST.md`.
- **Full report and code:** `questions/yd-neem-spikes/RESULTS.md`, `questions/yd-neem-spikes/analysis/neem_spikes.py`, and `questions/yd-neem-spikes/analysis/test_neem_spikes.py` (`3/3` synthetic recovery tests passing, including catching a denominator-masked fire surge).
:::
