---
# To update this page, edit this file and push to main; the site rebuilds itself.
# The figures are made by questions/yd-platinum-volcanism/analysis/make_figures.py from the results files.
summary: The GISP2 Greenland platinum spike is the strongest remaining geochemical claim for a Younger Dryas comet impact. Did it arrive before the cooling started—or decades after, following an extraordinary cluster of volcanic eruptions?
verdict: Platinum arrives twenty to thirty years after the cold began; the eruptions just before it were unusually heavy
result: The platinum layer in Greenland ice, the best physical evidence offered for an impact, lies about 20 to 30 years after the published start of the cold, though before its steepest fall; by the rule set in advance its timing is "ambiguous". The 150 years before the cold hold one of the heaviest runs of volcanic fallout in 51,000 years. Eruptions are no commoner before the ice age's other coolings than at random times, so this is a coincidence in time and not a shown cause.
dek: Earlier lab tests looked at fire, global biomass burning, and cooling shape. Here we test the strongest remaining geochemical proxy—the GISP2 platinum spike—against GISP2's own stratigraphy, synchronized GICC05 ages, and 51,000 years of polar volcanism, with every rule locked first.
updated: 2026-11-23
---

> **Where things stand, 23 November 2026.** Initial locked run finished (by Antigravity / Google DeepMind, directed by Eugene; open to second-vendor review or replication). Pre-registered verdicts: **Platinum as trigger = Ambiguous / within uncertainty** (too late on `GICC05` to start the cooling, yet deeper than GISP2's main cold/dust step); **51,000-year pre-onset volcanism = Unusually strong volcanic cluster** (Rank 3 of 284 in bipolar aerosol loading and Rank 12 of 338 in Greenland sulfate). **Replicated the same day** by Claude Fable 5.2 (Anthropic) from the written plan alone, on freshly downloaded data: every number checked came out the same. Its review notes are in the [replication folder](https://github.com/ejhong/aletheia-lab/tree/main/questions/yd-platinum-volcanism/replication/fable): the dating is good to about ten years, and against its neighbours in time alone the Greenland sulphate total ranks 6th of 49, high but not extreme.

## What we figured out

After fire and global biomass-burning claims fall away ([`ice-core-fire`](../ice-core-fire/), [`cooling-ammonium`](../cooling-ammonium/), [`yd-global-burn`](../yd-global-burn/)), the ~100-fold platinum spike reported by Petaev et al. (2013) in the GISP2 Greenland ice core (`1712.375–1712.000 m`, spanning ~21 years) remains the single cleanest geochemical anomaly cited for the Younger Dryas impact hypothesis. Meanwhile, volcanic-forcing studies (Svensson et al. 2020; Abbott et al. 2021; Lin et al. 2022; Green et al. 2025) argue that on the modern synchronized Greenland chronology (`GICC05`) the platinum layer sits *after* cooling had already started, and that a striking cluster of large volcanic eruptions preceded the cooling instead.

We tested both halves directly in primary public data (NOAA GISP2 `δ¹⁸O` and major ions, Svensson et al. 2020 bipolar tie-points, Rasmussen et al. 2008 20-yr synchronization, and Lin et al. 2022's 51,000-year volcanic catalog), locking every formula before looking at the target interval.

{{figure: yd-platinum-volcanism/timeline}}

Four things came out—and the picture is genuinely nuanced rather than a one-line slogan for either side.

1. **On synchronized `GICC05`, the platinum spike arrives 18 to 32 years *after* cooling began.** Interpolating `1712.375–1712.000 m` between Svensson et al. (2020)'s bracketing bipolar volcanic tie-points (`1713.915 m` at `12,917.3 b2k` and `1708.640 m` at `12,754.8 b2k`) puts **platinum onset at `12,869.9 b2k` (`+26.1 yr` after `GS-1` onset at `12,896 b2k`)** and **peak at `12,864.1 b2k` (`+31.9 yr` after)**. Using Rasmussen et al. (2008)'s 20-year table gives `+17.6 yr` (onset) and `+23.2 yr` (peak). An anomaly arriving two to three decades after cooling begins cannot be its initial trigger.
2. **Inside GISP2 itself, platinum sits *between* the initial cooling ramp and the main cold/dust plunge—and has no large GISP2 sulfate peak of its own.** Because the Younger Dryas started sluggishly ([`yd-cooling-shape`](../yd-cooling-shape/)), GISP2 `δ¹⁸O` eases downward across `1713.98 → 1712.43 m` (`−38.36‰ → −39.08‰`) before the platinum layer, yet GISP2's steepest two-piece step-changepoints in 20-yr `δ¹⁸O` (`1710.81 m`), sea salt `Na⁺` (`1710.90 m`), and dust `Ca²⁺` (`1709.90 m`) all arrive **1.5–2.5 m shallower (40–70 yr younger)** than platinum. And GISP2's own `SO₄²⁻` record (`iond.txt`) shows no major spike (`> 237 ppb`) directly at `1712.375–1712.000 m`—which is why our locked trigger verdict stays honestly **Ambiguous / within uncertainty**, and why the source of the platinum remains an open geochemical question.
3. **The 150 years immediately *before* the Younger Dryas hold the #3 largest bipolar volcanic cluster in 51,000 years.** In Lin et al. (2022)'s 60–9 ka catalog, `[12,896, 13,046)` b2k contains **4 major bipolar eruptions** (`13,028`, `12,995`, `12,961`, and `12,917 b2k`) totaling **`526.6 Tg`** of stratospheric aerosol loading—ranking **3rd of 284** non-overlapping 150-year windows (**top 1.1%**; median window is `0.0 Tg`) and **#1 in bipolar eruption count**. In Greenland sulfate deposition (`Table S3`), the same window totals **`595.9 kg km⁻²`** (**rank 12 of 338**, top 3.6%, nearly 4× the median). The final mega-eruption (`12,917.3 b2k`, `200.8 Tg`, `GISP2 SO₄ = 462 ppb` at `1713.8–1714.0 m`) hits just **21 years before `GS-1` onset**.
4. **Volcanism does *not* explain most other ice-age coolings.** Testing all 19 abrupt coolings across `10–60 ka` against 10,000 random placements shows no general tendency for Greenland volcanic sulfate to spike before stadial onsets (`p = 0.35` at 50 yr; `p = 0.93` at 150 yr; excluding `GS-1`, `p = 0.53` and `p = 0.99`). The pre-Younger Dryas volcanic quadruplet is therefore a genuinely unusual coincidence with—or plausible contributor to—the Younger Dryas specifically, rather than a universal ice-age cooling trigger.

## Inside the GISP2 core itself (zero timescale needed)

{{figure: yd-platinum-volcanism/stratigraphy}}

Reading from left (deeper, older) to right (shallower, younger) inside the exact same ice core removes cross-core timescale disputes entirely. Two giant volcanic sulfate spikes (`1718.7 m` = `649 ppb` and `1713.9 m` = `462 ppb`) precede `GS-1` onset (`~1713.2 m`). The platinum layer (`1712.375–1712.000 m`, copper band) sits clearly *after* the `12,917 b2k` eruption and the official `12,896 b2k` onset, with flat GISP2 sulfate, yet *before* the main drop in GISP2 `δ¹⁸O` and jump in `Ca²⁺` dust (`1710.8–1709.9 m`) and well *before* the century-long ammonium high (`1710.7–1708.0 m`) measured in [`ice-core-fire`](../ice-core-fire/).

## 51,000 years of polar volcanism

{{figure: yd-platinum-volcanism/volcanism_51ka}}

Across 51,000 years (`60–9 ka b2k`), the 150-year window right before the Younger Dryas (`[12,896, 13,046)` b2k, copper bar) stands out starkly in both panels—especially in bipolar stratospheric aerosol loading (top, **#3 of 284 windows**, and the only window with four separate bipolar eruptions).

## What this does—and does not—settle

- **What it undercuts:** The claim that the GISP2 platinum spike *initiated* the Younger Dryas cooling—on `GICC05`, cooling began 18–32 years earlier, right on the heels of one of the strongest volcanic clusters of the entire last glacial cycle.
- **What stays open:** What actually deposited the 21-year platinum-rich layer at `1712.375–1712.000 m` ~20–30 years into the cooling. Because Petaev et al. (2013) only measured platinum across a narrow ~200-year stretch of GISP2, nobody yet knows how often similar Pt spikes appear during other deglacial Icelandic fissure eruptions or other glacial stadials. Continuous platinum profiles across multiple Greenland cores and other stadials would settle that cleanly.

::: details Methods, data, and sensitivity checks
- **Protocol and lock:** `questions/yd-platinum-volcanism/protocol.md`, locked at `2026-11-23T17:25:43Z` (`protocol.lock`, SHA-256 `3d7df72a5989...`) before viewing GISP2 `[1705, 1720] m` or volcanic lists in `[12,600, 13,200]` b2k. Zero amendments.
- **Public datasets:** GISP2 major ions (`iond.txt`, Mayewski et al. 1997), GISP2 2-m `δ¹⁸O` (`gispd18o.txt`, Grootes & Stuiver 1997), synchronized 20-yr `NGRIP/GRIP/GISP2` (`gicc05-calcium-20yr.txt`, Rasmussen et al. 2008), Svensson et al. (2020) bipolar volcanic tie-points (`Clim. Past` CC-BY), Lin et al. (2022) 60–9 ka polar volcanic catalog (`Clim. Past` CC-BY), Sigl et al. (2021) VSSI (`PANGAEA.930557` CC-BY), and Rasmussen et al. (2014) Table 2 (`events.tsv`). Full URLs and SHA-256 hashes in `questions/yd-platinum-volcanism/MANIFEST.md`.
- **Window sensitivity:** Widening the volcanic window to 300 yr (`[12,746, 13,046)` b2k) keeps bipolar aerosol loading at **Rank 3 of 140** (`630.3 Tg`, top 2.1%); shifting to a straddling 150-yr window (`[12,796, 12,946)`) drops ranks to 17/282 (bipolar) and 85/337 (Greenland) because 3 of the 4 quadruplet eruptions fall between `13,028` and `12,961 b2k`.
- **Full report and code:** `questions/yd-platinum-volcanism/RESULTS.md`, `questions/yd-platinum-volcanism/analysis/ptvolc.py`, and `questions/yd-platinum-volcanism/analysis/test_ptvolc.py` (6/6 unit tests passing).
:::
