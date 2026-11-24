---
# To update this page, edit this file and push to main; the site rebuilds itself.
# The figures are made by questions/ydb-site-synchrony/analysis/make_figures.py from the results files.
summary: Proponents argue that Younger Dryas "impact layers" at 23–32 sites across four continents were laid down on the same day ~12,800 years ago. Here we recalibrate raw direct radiocarbon dates from 9 Northern Hemisphere sites on IntCal20 against a real single-year catastrophe (the Laacher See volcanic eruption), and audit dating precision and placebo-year overlap across all 32 claimed sites.
verdict: Mixed—raw direct dates fail single-year synchrony, and 88% of sites are too loosely or indirectly dated to test it
result: Against a real single-year Late Glacial benchmark—the Laacher See volcanic eruption across 5 localities (T = 0.42, p > 0.97, 5/5 overlap, 44-year spread)—raw direct radiocarbon dates from 9 Northern Hemisphere YDB sites scatter across 544 years (T = 630.6, p = 0.0005 under measurement+curve error and p = 0.0015 even with ±20 yr lab scatter and 50 yr old-wood offset; only 5/9 overlap). Choosing the most impact-favorable dates at three sites lowers T to 28.1 (still failing pure synchrony, p = 0.009, but passing the 50-year old-wood model, p = 0.157). Across all 32 claimed sites in Kennett et al. (2015), only 4 (12.5%) have both a direct proxy-layer date and a 95% interval ≤ 300 yr; the median interval is 940 years wide, and half the modeled sites still "overlap" arbitrary placebo dates spanning 930 years.
dek: Benchmarking claimed Younger Dryas impact layers against a real single-year Late Glacial catastrophe—and testing how tightly all 32 sites actually pin down one year.
updated: 2026-11-24
---

> **Where things stand, 24 November 2026.** Initial locked run finished with zero amendments (by Antigravity / Google DeepMind, directed by Eugene; open to second-vendor replication). Pre-registered verdict: **Mixed / underconstrained** (`ambiguous_or_mixed`—raw dates reject synchrony, favorable old-wood subset passes `M1`, and `W_50 = 930 yr` sits 70 years shy of the `1,000 yr` pre-registered threshold).

{{figure: ydb-site-synchrony/tiles}}

## What we tested and found

A centerpiece claim of the Younger Dryas Impact Hypothesis is that thin layers carrying microspherules, nanodiamonds, meltglass, or platinum at 23 to 32 sites on four continents all date to the same single event around `12,835–12,735` years ago (Kennett et al. 2015, *PNAS*). Critics reply that Bayesian single-phase age models and wide error bars create an illusion of synchrony across layers that were actually laid down centuries apart.

We locked a two-pillar test before computing a single statistic on the real dates:

1. **Direct-`¹⁴C` synchrony on IntCal20 with a real single-year positive control.** We took raw uncalibrated radiocarbon dates directly from claimed impact layers at `9` Northern Hemisphere sites (`3` continents), recalibrated every date on **IntCal20** with a flat prior, and tested whether their scatter fits a single calendar year under pure measurement + curve error (**M0**) or with generous inter-lab (`±20 yr`) and old-wood (`50 yr` mean) tolerances (**M1**). To make sure the test does not falsely reject real single-year deposits next to the Younger Dryas radiocarbon plateau, we ran the exact same test on `16` dates from `5` localities tied to the **Laacher See volcanic eruption (`13,006 ± 9 cal BP`)**.
2. **Precision and placebo-year audit across all 32 claimed sites.** We parsed every site in Kennett et al. (2015, Fig. 2) to count how many actually have direct dates and tight (`≤ 300 yr`) intervals—and swept a fake "placebo impact year" across `14,000–11,500 cal BP` to measure how many sites still overlap centuries away from `12,800 BP`.

## Direct dates vs. a real single-year catastrophe

The **Laacher See Tephra** positive control passes cleanly: across five localities up to 335 km apart, its calibrated medians span just **`44 years`** (`12,967–13,011 cal BP`, `SD = 20.0 yr`), Ward–Wilson `T = 0.42` (`p_M0 = 0.998`, `p_M1 = 1.000`), and **`5 of 5` (`100%`)** overlap simultaneously (`16/16` across all raw dates).

The 9 YDB sites behave very differently. On unfiltered primary YDB dates, calibrated medians span **`544 years`** (`12,653` at Lake Hind to `13,197` at Blackwater Draw), `T = 630.6` (`p_M0 = 0.0005`, `p_M1 = 0.0015`), and only **`5 of 9`** share any calendar year at 95.4% HPD. Across all 33 raw direct dates, `T = 833.4` (`p_M1 = 0.0005`) and calibrated median `SD = 165.2 yr` (`p_M1 = 0.0095`).

Use the toggle below to switch between the unfiltered primary dates and a **YDIH-favorable old-wood-mitigated selection** (taking Arlington Canyon's youngest wood date, Aalsterhut's 3 basal dates, and Lake Hind's overlying `32 cm` date):

{{figure: ydb-site-synchrony/pillar1_calibration}}

Even under that favorable selection, **Abu Hureyra (`12,895–13,094 cal BP`) and Lake Hind (`12,736–12,830 cal BP`) still do not overlap**, and pure single-year synchrony (**M0**) still fails (`T = 28.07`, `p = 0.009`). Only when we add `±20 yr` inter-lab error plus a `50-year` mean old-wood offset (**M1**) does the favorable subset become statistically consistent with one year (`p_T,M1 = 0.157`).

{{figure: ydb-site-synchrony/simulation_benchmark}}

## How tightly do all 32 claimed sites pin down one year?

Auditing every row of Kennett et al. (2015, Fig. 2) shows why "23 sites overlap 12,800 BP" sounds far sharper than the underlying dates actually are:

{{figure: ydb-site-synchrony/precision_funnel}}

- **`9 of 32` (`28.1%`)** cannot be modeled at all.
- **`22 of 32` (`68.8%`)** lack any direct date on the proxy layer itself.
- Only **`4 of 32` (`12.5%`)** combine a direct proxy-layer date with a `95% CI ≤ 300 yr` (Aalsterhut, Abu Hureyra, Arlington Canyon, Bull Creek).
- Across the 23 modeled sites, the median 95% interval is **`940 years` wide** (ranging up to `9,475 yr` at Melrose, PA), and OxCal rejected **`46 of 354` dates (`13.0%`)**, climbing to **`28.8%`** in the Low quality tier.

Drag the slider below to move the target year away from `12,800 cal BP`. Even **`±250 years`** away (`13,050` or `12,550 cal BP`), **`17 of 23` sites (`74%`)**—including every Medium and Low site—still overlap. Half or more of the modeled sites overlap arbitrary placebo dates across a **`930-year` span** (`12,260–13,190 cal BP`).

{{figure: ydb-site-synchrony/placebo_overlap}}

## What this means

When a real single-year catastrophe hits the Late Glacial landscape—like the Laacher See eruption just two centuries before the Younger Dryas—radiocarbon dates across distant sites snap onto the same narrow window (`T = 0.42`, `100%` overlap). The claimed Younger Dryas impact layers do not. Unfiltered direct dates scatter across more than five centuries (`T = 631`), while nearly nine out of ten of the 32 claimed sites lack a tightly constrained direct date on the proxy layer, leaving intervals so broad that three-quarters of modeled sites match dates 250 years off in either direction. Because selective old-wood filtering lets the tightest 9-site subset pass a generous `50-year` old-wood model (`p = 0.157`), the dates cannot *prove* that no single event occurred—but they fall far short of proving that 23 to 32 sites across four continents were laid down on the same day.

::: details Methods, data, and verification
- **Protocol and lock:** `questions/ydb-site-synchrony/protocol.md`, locked at `2026-11-24T05:54:16Z` (`protocol.lock`, SHA-256 `30d43acacdd3`). Zero amendments.
- **Public datasets:** `intcal20.14c` (Reimer et al. 2020), Reinig et al. (2023 *Nature*, Extended Data Table 1 — Laacher See positive control), Kennett et al. (2015 *PNAS*, Fig. 1–2), Meltzer et al. (2014 *PNAS*), Kennett et al. (2008 *QSR*, Arlington Canyon), van Hoesel et al. (2012 *PNAS*, Aalsterhut), Moore et al. (2020 *Sci. Rep.* SI, Abu Hureyra), Teller et al. (2019 *Q. Res.*, Lake Hind CSV), Waters & Stafford (2007 *Science*, Clovis sites), and Holliday et al. (2023 *ESR*, Bull Creek transcription of Bement et al. 2014). Full URLs, licences, and SHA-256 hashes in `questions/ydb-site-synchrony/MANIFEST.md`.
- **Full report and code:** `questions/ydb-site-synchrony/RESULTS.md`, `questions/ydb-site-synchrony/analysis/site_synchrony.py`, and `questions/ydb-site-synchrony/analysis/test_site_synchrony.py` (`5/5` synthetic verification tests passing).
:::
