---
# To update this page, edit this file and push to main; the site rebuilds itself.
# The figures are made by questions/ydb-site-synchrony/analysis/make_figures.py from the results files.
summary: The hypothesis's authors say that thin layers at 23 to 32 sites on four continents were laid down by one event about 12,800 years ago. We took the radiocarbon dates from nine of those sites and asked whether they could be one age, using a real one-year event, the Laacher See eruption, to check the method. We also counted how many of the 32 sites are dated well enough to say.
verdict: Mixed. The precise dates are not one age, though old wood could explain that; only 4 of 32 sites are dated tightly on the layer itself
result: Dates from nine claimed sites do not fit a single radiocarbon age, and that holds whichever site is left out. With the dates most favourable to the hypothesis the misfit is small enough that charcoal a few decades older than the layer could explain it. A spot check found that four of the nine were dates of Clovis camps, not of the layer, and that the headline misfit was inflated by the way dates were averaged. The count that does not depend on any of this: of 32 claimed sites, four have a date on the layer itself that is good to 300 years. Three-quarters of the modelled sites would equally "match" an event 250 years earlier or later.
dek: Are the claimed impact layers the same age, and how many of the 32 sites are dated well enough to tell? Spot-checked afterwards; not replicated.
updated: 2026-11-24
---

> **Where things stand, 24 November 2026.** The locked run finished with no amendments (by Antigravity, Google DeepMind, directed by Eugene). The verdict by the rules fixed in advance is **mixed** (`ambiguous_or_mixed`). A spot check by Claude Fable 5.2 (Anthropic) reran the program, got the same numbers, and found the nine-site part weaker than first written: see the next section. No model from a second company has replicated the study, and none is planned for now.

{{figure: ydb-site-synchrony/tiles}}

## Spot check: what holds and what does not

Anthropic's model checked this study after it was published and reran its program. Every number came out the same, and 37 dates compared with the source papers all match. The page has been corrected in these places. The figures are as first made.

- **Four of the nine sites are not dated on the layer.** Murray Springs, Sheriden Cave, Indian Creek and Blackwater Draw enter with dates of the Clovis occupation. The hypothesis's own authors mark all four as having no date on the layer. With only the five sites that do, the result is the same.
- **The headline misfit, T = 631, is inflated.** Nearly all of it comes from three sites, and at one of them twelve dates that disagree among themselves were averaged into a single very precise value. Done more carefully the figure is 170 to 210, and at least 141 with any one site left out. That is still far from one age (a true single age would give about 8).
- **The comparison with the eruption is not like for like.** The eruption's dates are on trees it killed, most of them rings of one tree. The claimed layers are dated mostly on charcoal found in or near them, which can be older than the layer. The comparison shows the method works on ideal material and no more.
- **The audit of all 32 sites holds,** and is the part to rely on.

The hypothesis's authors hold that radiocarbon dates can make one day look like centuries, and that scatter of this kind cannot count against them. If so, the same dates cannot show the layers are one age either.

The full list is in the study's `RESULTS.md`, and the checking script is in `questions/ydb-site-synchrony/spotcheck/`.

## What we tested and found

A centerpiece claim of the Younger Dryas Impact Hypothesis is that thin layers carrying microspherules, nanodiamonds, meltglass, or platinum at 23 to 32 sites on four continents all date to the same single event around `12,835–12,735` years ago (Kennett et al. 2015, *PNAS*). Critics reply that Bayesian single-phase age models and wide error bars create an illusion of synchrony across layers that were actually laid down centuries apart.

We locked a two-pillar test before computing a single statistic on the real dates:

1. **Direct-`¹⁴C` synchrony on IntCal20 with a real single-year positive control.** We took raw uncalibrated radiocarbon dates from `9` Northern Hemisphere sites (`3` continents; at five of them the date is on the claimed layer, at four it is the date of a Clovis occupation), recalibrated every date on **IntCal20** with a flat prior, and tested whether their scatter fits a single calendar year under pure measurement + curve error (**M0**) or with generous inter-lab (`±20 yr`) and old-wood (`50 yr` mean) tolerances (**M1**). To make sure the test does not falsely reject real single-year deposits next to the Younger Dryas radiocarbon plateau, we ran the exact same test on `16` dates from `5` localities tied to the **Laacher See volcanic eruption (`13,006 ± 9 cal BP`)**.
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

Drag the slider below to move the target year away from `12,800 cal BP`. Even **`±250 years`** away (`13,050` or `12,550 cal BP`), **`17 of 23` sites (`74%`)**—including every Medium and Low site—still overlap; at `±500 years` about half do (`10` and `12` of `23`). Half or more of the modeled sites overlap arbitrary placebo dates across a **`930-year` span** (`12,260–13,190 cal BP`).

{{figure: ydb-site-synchrony/placebo_overlap}}

## What this means

A real one-year event of the same period, the Laacher See eruption, gives radiocarbon dates at five places that agree closely. The dates from the claimed Younger Dryas layers do not agree: the precise ones differ by more than their errors allow, whichever site is left out. That could mean the layers are of different ages. It could also mean that some of the charcoal dated is older than the layer it lies in, and with the dates most favourable to the hypothesis a few decades of that would be enough. These dates cannot tell the two apart. What can be said without that argument is how little the claim rests on: of 32 sites said to hold the same layer, four have a date on the layer itself that is good to 300 years, and three-quarters of the modelled sites would "match" an event 250 years earlier or later just as well.

::: details Methods, data, and verification
- **Protocol and lock:** `questions/ydb-site-synchrony/protocol.md`, locked at `2026-11-24T05:54:16Z` (`protocol.lock`, SHA-256 `30d43acacdd3`). Zero amendments.
- **Public datasets:** `intcal20.14c` (Reimer et al. 2020), Reinig et al. (2023 *Nature*, Extended Data Table 1 — Laacher See positive control), Kennett et al. (2015 *PNAS*, Fig. 1–2), Meltzer et al. (2014 *PNAS*), Kennett et al. (2008 *QSR*, Arlington Canyon), van Hoesel et al. (2012 *PNAS*, Aalsterhut), Moore et al. (2020 *Sci. Rep.* SI, Abu Hureyra), Teller et al. (2019 *Q. Res.*, Lake Hind CSV), Waters & Stafford (2007 *Science*, Clovis sites), and Holliday et al. (2023 *ESR*, Bull Creek transcription of Bement et al. 2014). Full URLs, licences, and SHA-256 hashes in `questions/ydb-site-synchrony/MANIFEST.md`.
- **Full report and code:** `questions/ydb-site-synchrony/RESULTS.md`, `questions/ydb-site-synchrony/analysis/site_synchrony.py`, and `questions/ydb-site-synchrony/analysis/test_site_synchrony.py` (`5/5` synthetic verification tests passing).
:::
