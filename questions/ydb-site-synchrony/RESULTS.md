# Results — Are the claimed Younger Dryas "impact layer" sites actually the same age?

**Question:** `#113` (`ydb-site-synchrony`) · **Lane:** `data`  
**Protocol locked:** `2026-11-24T05:54:16Z` (`protocol.lock`, SHA-256 `30d43acacdd3`) · **Amendments:** `0`  
**Pre-registered verdict:** **`ambiguous_or_mixed`**  
**Authorship:** Designed, coded, run, and written by **Antigravity (Google DeepMind)** on `2026-11-24`, directed by **Eugene Jhong**. Open to independent second-vendor replication.

---

## Short answer

**The claimed Younger Dryas impact layers do not show tight single-year synchrony—and most sites cannot test it.** *(A spot check on 24 November 2026 found the nine-site part weaker than first written here; see "Spot check and corrections" below.)*

When we recalibrate raw uncalibrated radiocarbon dates directly from claimed Younger Dryas Boundary (YDB) layers across 9 Northern Hemisphere sites on **IntCal20** without circular single-phase priors, they scatter far too widely for a single calendar year: Ward–Wilson homogeneity `T = 630.62` (`df = 8`, `p = 6.1 × 10⁻¹³¹`), calibrated medians spanning **`544 years`** (`12,653` to `13,197 cal BP`), and only **`5 of 9`** sites sharing any single calendar year at 95.4% HPD. That fails both pure measurement + curve error (**M0**, `p_T = 0.0005`) and a generous inter-lab + 50-year old-wood model (**M1**, `p_T = 0.0015`). By contrast, a real single-year catastrophe right beside the Younger Dryas—the **Laacher See volcanic eruption (`13,006 ± 9 cal BP`)** across 5 localities up to 335 km apart—passes the exact same test cleanly (`T = 0.42`, `p_T,M0 = 0.9975`, `p_T,M1 = 0.9995`, `5/5` overlap, median `SD = 20.0 yr`).

However, two caveats keep the pre-registered formal verdict at **`ambiguous_or_mixed`** rather than an outright proof of asynchrony:

1. **Old-wood and stratigraphic selection rescue `M1` (but not `M0`).** When we substitute the most YDIH-favorable dates at three key sites (Arlington Canyon's youngest wood date, Aalsterhut's 3 basal nanodiamond dates, and Lake Hind's overlying `32 cm` date), `T` falls to **`28.07`**. That still fails pure single-year synchrony (**M0**, `p_T = 0.009`), but passes once we add `±20 ¹⁴C yr` inter-lab scatter and `50 yr` mean old-wood inbuilt age (**M1**, `p_T = 0.157`, `7/9` HPD overlap—though Abu Hureyra and Lake Hind still do not overlap).
2. **Most of the 32 claimed YDB sites are simply too poorly dated to discriminate a single year.** Auditing all 32 sites in Kennett et al. (2015, Fig. 2) shows that `9` (`28.1%`) cannot be modeled at all, only `10` (`31.3%`) have any direct date on the proxy layer, and only **`4 of 32` (`12.5%`)** combine a direct proxy-layer date with a `95% CI ≤ 300 yr`. Across the 23 modeled sites, the median 95% interval is **`940 years` wide** (max `9,475 yr`), and `≥ 50%` of sites simultaneously overlap arbitrary placebo years across a **`930-year` span** (`12,260–13,190 cal BP`)—just `70 years` shy of our pre-registered `1,000-year` cutoff for `underconstrained_not_synchronous`.

In plain terms: **a synchronous single-day event is not established by the YDB dating record.** Unfiltered direct dates reject it decisively, while the remaining sites' wide error bars mean that three-quarters of the modelled sites still overlap a date 250 years away (`17/23` at `13,050` or `12,550 BP`) and about half overlap one 500 years away (`10/23` and `12/23`).

---

## Spot check and corrections (24 November 2026)

Claude Fable 5.2 (Anthropic), with a sub-agent (Claude Opus 5.5), checked this study after it was published. The
lock is in order. A rerun of the locked program gives the three results tables byte for byte and every headline
number. The dates were read from the source papers by the program, not typed in; 37 of them were compared with
the sources and all match. The verdict `ambiguous_or_mixed` follows from the locked rules. The first part of the
study (the nine sites) is weaker than this report says, in the ways listed here. The rest of the report is as
first published. The script and its output are in `spotcheck/`.

1. **Four of the nine "dates on the impact layer" are not dates on the layer.** Murray Springs, Sheriden Cave,
   Indian Creek and Blackwater Draw enter with averages for the Clovis occupation from Waters and Stafford
   (2007). Kennett and others (2015, Fig. 2) mark all four as having no date on the proxies, and Waters and
   Stafford list Sheriden Cave and Blackwater Draw under "problematic". The plan and this report call them
   direct dates. They add little either way: with only the five sites that Kennett marks as dated on the layer,
   T is 616 on the first choice of dates and 24.3 on the favourable choice (chi-square p = 0.00007). Four other
   sites that Kennett counts as directly dated (Talega, Lingen, Barber Creek, Blackville) are not in the panel,
   and no rule for choosing the nine is given.
2. **T = 631 is three sites, and partly a matter of how dates were averaged.** Lake Hind supplies 276 of it,
   Arlington Canyon 182 and Aalsterhut 158. Arlington Canyon enters as the mean of 12 dates with an error of
   8.4 years, but those 12 disagree among themselves (T = 176 on 11 degrees of freedom) and include five that
   Kennett and others (2008) set aside as old wood. With the average Kennett and others publish (11,060 ± 40),
   T is 171. With the two averaged sites' errors widened to match their own scatter, T is 214. Leaving out any
   one site, T is at least 141. So the dates still do not fit one radiocarbon age. "631" overstates by how much.
3. **The favourable panel fails on one site.** Without Abu Hureyra its chi-square p is 0.051.
4. **The control is not like for like.** Nine of the 16 Laacher See dates are rings of one poplar, three of the
   five localities are within about 10 km of the volcano, and all are plants killed and buried by the eruption.
   The Younger Dryas dates are mostly charcoal found in or near a layer. Aalsterhut's own 14 charcoal dates,
   from one layer at one site, fail the same test (p = 0.009). The control shows that the method does not
   reject a true single year dated on ideal material. It does not show what one day would look like when dated
   on scattered charcoal.
5. **The simulated p-values are lenient, not harsh.** The simulation adds the calibration curve's error to each
   date separately. For samples of the same year that error is shared and cancels, so the simulation makes
   agreement look harder to reach than it is and passes more easily. The "p = 0.0005" is the smallest value 2,000
   simulations can give.
6. **Wording corrected in the text.** Overlap 500 years from 12,800 is about half the sites (10 or 12 of 23), not
   "nearly as easy". The 544-year span ends at Blackwater Draw, the least precise date; without it the span is
   436 years. Three of the nine sites are in Kennett's middle tier, not the top one. The change made to the
   program after the lock, for speed, moves calibrated ages by up to 1 year, not 0.2. This report also did not
   say that one condition for the verdict "synchronous" was met (four-fifths of the modelled sites overlap only
   within a 300-year window), or that the date of the Laacher See eruption is itself disputed.

**What the study shows, restated.** The precise radiocarbon dates from the claimed layers are not one radiocarbon
age. Whether that is because the layers differ in age, or because charcoal older than the layer was dated, these
dates cannot say. The count that does not depend on any of this is the second part: of 32 claimed sites, four have
a date on the layer itself that is good to 300 years.

**How the hypothesis's authors answer.** They hold that an instantaneous event "can appear to take place over
several thousand years" in radiocarbon dates taken at face value, and that such scatter cannot refute them
(Sweatman and others 2024, section 4). On that view no test of this kind can count against the hypothesis. The
second part of this study is the reply: if dates cannot show the layers differ in age, they cannot show the layers
are the same age either, and four sites of 32 is what the claim of one layer on four continents rests on.

**Not replicated.** No model from a second company has rewritten this analysis from the plan, which the lab's rules
ask for before a `data` question is called done. None is planned for now.

---

## 1. Positive Control — A real single-year catastrophe passes easily

Before judging the YDB, we ran the exact same IntCal20 calibration and forward-simulated radiocarbon-plateau pipeline on `16` high-precision raw `¹⁴C` dates directly tied to the **Laacher See Tephra (`LST`, `13,006 ± 9 cal BP`)** across `5` German localities up to `335 km` apart (Reinig et al. 2023 *Nature*, Extended Data Table 1). Because Laacher See erupted in a single year right next to the Younger Dryas radiocarbon plateau, it tests whether IntCal20 wiggles or laboratory noise cause false rejections.

| Positive-Control Panel | `n` | Weighted Mean (`¹⁴C BP`) | Ward–Wilson `T` (`df`) | `p_χ²` | Cal. Median `SD` / Span | 95.4% HPD Overlap | `p_T` (`M0` / `M1`) | `p_SD` (`M0` / `M1`) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **LST — 5 localities** | `5` | `11,060.2 ± 6.1` | `0.42` (`4`) | `0.981` | `20.0 yr` / `44 yr` | **`5 / 5` (`100%`)** (`12,923–13,076`) | **`0.9975`** / **`0.9995`** | **`0.977`** / **`0.993`** |
| **LST — all 16 raw dates** | `16` | `11,060.2 ± 6.1` | `14.80` (`15`) | `0.466` | `29.7 yr` / `132 yr` | **`16 / 16` (`100%`)** (`12,928–13,059`) | **`0.9735`** / **`1.0000`** | **`0.997`** / **`1.000`** |

**Positive control result:** **PASS.** Real single-year Late Glacial deposits across five sites show `T = 0.42` (`p > 0.97`), a `44-year` median span (`12,967–13,011 cal BP`), and `100%` simultaneous HPD overlap. The test does not over-reject genuine single-year events.

---

## 2. Pillar 1 — Direct-`¹⁴C` Synchrony Across 9 Northern Hemisphere YDB Sites

We recalibrated all raw uncalibrated `¹⁴C` measurements directly from claimed YDB horizons across `9` Northern Hemisphere sites (`3` continents) on **IntCal20** with a flat prior (no circular cross-site single-phase prior) and benchmarked each panel against `2,000` forward-simulated single-year catalogues per candidate impact year (`12,700–12,950 cal BP` in `25-yr` steps; reporting the **most generous** `p`-value across the entire sweep).

*(Minor transparency note: `protocol.md` §3.2 miscounted the prose total of individual raw rows across the 9 sites as `32`; the locked parser extracts all `33` raw rows (`1 + 12 + 14 + 1 + 1 + 1 + 1 + 1 + 1 = 33`) from the exact primary tables listed in `protocol.md` §2 and `MANIFEST.md`.)*

### Summary of Pillar 1 panels

| Panel | `n` | Weighted Mean (`¹⁴C BP`) | Ward–Wilson `T` (`df`) | `p_χ²` | Cal. Median `SD` / Span | Max 95.4% HPD Overlap | `p_T` (`M0` / `M1`) | `p_SD` (`M0` / `M1`) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **1A-Primary** (9 sites, unfiltered) | `9` | `11,025.0 ± 6.7` | **`630.62`** (`8`) | `6.1 × 10⁻¹³¹` | `172.6 yr` / **`544 yr`** | **`5 / 9` (`55.6%`)** (`12,756–13,091`) | **`0.0005`** / **`0.0015`** | `0.145` / `0.151` |
| **1B-AllRaw** (all 33 direct dates) | `33` | `11,024.5 ± 6.7` | **`833.36`** (`32`) | `1.7 × 10⁻¹⁵⁴` | `165.2 yr` / **`661 yr`** | **`18 / 33` (`54.5%`)** (`12,769–12,770`) | **`0.0005`** / **`0.0005`** | **`0.015`** / **`0.0095`** |
| **1A-Favorable** (9 sites, old-wood mitigated) | `9` | `10,934.0 ± 16.9` | **`28.07`** (`8`) | `4.6 × 10⁻⁴` | `141.3 yr` / **`428 yr`** | **`7 / 9` (`77.8%`)** (`12,756–12,890`) | **`0.0090`** / `0.1574` | `0.283` / `0.241` |

### Why `T` rejects `1A-Primary` decisively while `SD` is noisy

In **Panel 1A-Primary**, `T = 630.62` is **`61×`** higher than the simulated M0 median (`10.34`, 95th percentile `23.89`) and **`20×`** higher than the simulated M1 median (`31.87`, 95th percentile `147.95`). Across all `33` raw dates (**Panel 1B-AllRaw**), **both** `T` (`833.36`, `p_M1 = 0.0005`) and calibrated median `SD` (`165.2 yr`, `p_M1 = 0.0095`) reject a single year even under M1.

Why didn't `SD` alone hit `p < 0.01` on the 9-site panels (`p_SD,M1 = 0.151` on Primary; `0.241` on Favorable)? Because one of the 9 sites—**Blackwater Draw, NM** (`11,300 ± 235 ¹⁴C BP`)—carries an enormous `±235 ¹⁴C yr` laboratory error. In forward simulation, drawing one random Gaussian with `σ = 235 yr` across a steep part of IntCal20 routinely throws a single synthetic median 400–600 years away, inflating the simulated 9-site unweighted `SD` (`q95 = 221–229 yr`). Inverse-variance-weighted `T` is immune to that single imprecise date and directly captures the genuine conflict among the *precisely* dated sites:

### Site-by-site IntCal20 calibrations (9 sites)

| Site | Primary Lab ID (`¹⁴C BP ± σ`) | Primary IntCal20 Median `[95.4% HPD]` | Favorable Selection (if changed) | Favorable Median `[95.4% HPD]` |
|---|---|---|---|---|
| **Abu Hureyra, Syria** | `UCIAMS-105429` (`11,070 ± 40`) | `13,000` `[12,895–13,094]` | *(same)* | `13,000` `[12,895–13,094]` |
| **Arlington Canyon, CA** | 12-date YDB mean (`11,138.2 ± 8.4`) | `13,089` `[13,073–13,102]` | `Beta-161032` (`10,860 ± 70`) | `12,798` `[12,715–12,959]` |
| **Aalsterhut, Netherlands** | 14-date Usselo mean (`10,846.6 ± 14.2`) | `12,756` `[12,738–12,822]` | Basal 3-date mean (`10,898.7 ± 38.2`) | `12,802` `[12,748–12,890]` |
| **Lake Hind, Manitoba** | `UCIAMS-29317` (`10,610 ± 25`) | `12,653` `[12,504–12,707]` | `PSUAMS-1572` (`10,850 ± 35`) | `12,769` `[12,736–12,830]` |
| **Bull Creek, OK** | `BC21` (`11,070 ± 60`) | `12,990` `[12,840–13,098]` | *(same)* | `12,990` `[12,840–13,098]` |
| **Murray Springs, AZ** | 8-date Clovis/F1 mean (`10,885 ± 50`) | `12,801` `[12,739–12,894]` | *(same)* | `12,801` `[12,739–12,894]` |
| **Sheriden Cave, OH** | 2-date mean (`10,920 ± 50`) | `12,821` `[12,743–12,964]` | *(same)* | `12,821` `[12,743–12,964]` |
| **Indian Creek, MT** | Clovis/YDB (`10,980 ± 110`) | `12,912` `[12,749–13,091]` | *(same)* | `12,912` `[12,749–13,091]` |
| **Blackwater Draw, NM** | 3-date mean (`11,300 ± 235`) | `13,197` `[12,756–13,595]` | *(same)* | `13,197` `[12,756–13,595]` |

Look at the precise sites even *after* applying YDIH-favorable old-wood and stratigraphic choices:
- **Abu Hureyra's** direct Level 445 meltglass-peak date (`11,070 ± 40 ¹⁴C BP`, IntCal20 `12,895–13,094 cal BP`) and **Bull Creek's** nanodiamond-peak date (`11,070 ± 60 ¹⁴C BP`, `12,840–13,098 cal BP`) sit right at **13,000 cal BP** (nearly identical to the Laacher See eruption!).
- Meanwhile, **Aalsterhut's** 14-date Usselo charcoal mean (`12,738–12,822 cal BP`), **Murray Springs** (`12,739–12,894 cal BP`), and **Lake Hind** (`12,504–12,707` on `UCIAMS-29317`, or `12,736–12,830` even on `PSUAMS-1572`) sit **`150–350 years younger`**.
- Even in the most YDIH-favorable 9-site panel, **Abu Hureyra (`12,895–13,094`) and Lake Hind (`12,736–12,830`) fail to overlap by 65 years**, and pure measurement + curve error (**M0**) still rejects synchrony (`T = 28.07`, `p = 0.009`). Only adding an extra `±20 yr` lab error plus `50 yr` mean old-wood offset (**M1**) lets that favorable panel pass (`p = 0.157`).

---

## 3. Pillar 2 — Precision & Placebo-Year Overlap Audit Across All 32 Claimed Sites

Kennett et al. (2015, *PNAS*, Fig. 2) summarize **32 claimed YDB sites** across four continents—23 Bayesian-modeled sites (9 High, 8 Medium, 6 Low quality) and 9 unmodeled sites—and emphasize that all 23 modeled sites' 95% credible intervals overlap `12,835–12,735 cal BP`. Our programmatic audit of every row in Fig. 2 quantifies how much chronological specificity that overlap actually carries:

### Precision & Outlier-Rejection Breakdown

| Category / Quality Tier | Sites | Direct Date on Proxies | Median 95% CI Width | Mean 95% CI Width | Max 95% CI Width | Total Dates | OxCal Rejected (`%`) |
|---|---:|---:|---:|---:|---:|---:|---:|
| **High** | `9` | `6` | `355 yr` | `445 yr` | `1,270 yr` (Daisy Cave) | `173` | `22` (`12.7%`) |
| **Medium** | `8` | `2` | `1,068 yr` | `1,166 yr` | `2,080 yr` (Barber Creek) | `129` | `9` (`7.0%`) |
| **Low** | `6` | `2` | `2,650 yr` | `3,889 yr` | `9,475 yr` (Melrose) | `52` | `15` (`28.8%`) |
| **All Modeled** | **`23`** | **`10`** | **`940 yr`** | **`1,594 yr`** | **`9,475 yr`** | **`354`** | **`46` (`13.0%`)** |
| **Unmodeled (`x`)** | `9` | `0` | — | — | — | `22` | — |
| **All Claimed YDB Sites** | **`32`** | **`10` (`31.3%`)** | — | — | — | `376` | — |

Key precision counts across all 32 claimed sites:
- **`9 of 32` (`28.1%`)** cannot be age-modeled at all.
- **`22 of 32` (`68.8%`)** have **no direct radiocarbon date on the claimed impact-proxy layer** (relying on stratigraphic bracketing or interpolation).
- Only **`4 of 32` (`12.5%`)** combine a direct date on the proxy layer with a `95% CI width ≤ 300 yr`: **Aalsterhut** (`120 yr`), **Abu Hureyra** (`230 yr`), **Arlington Canyon** (`230 yr`), and **Bull Creek** (`285 yr`).
- Across the 23 modeled sites, **`16 of 23` (`69.6%`)** have 95% intervals wider than `500 yr`, **`11 of 23` (`47.8%`)** exceed `1,000 yr`, and **`7 of 23` (`30.4%`)** exceed `2,000 yr`.
- OxCal rejected **`46 of 354` dates (`13.0%`)** overall, climbing to **`28.8%`** in the Low tier (`50%` at Lake Cuitzeo and Daisy Cave, `40%` at Blackville, `33%` at Melrose, `22%` at Abu Hureyra).

### Placebo-Year Overlap Test (`14,000–11,500 cal BP`)

If 23 sites overlap `12,800 cal BP` only because a single catastrophic event occurred in that year, moving the target date centuries away should collapse the overlap sharply. Instead:

| Target / Placebo Calendar Year | Offset from `12,800 BP` | All 23 Modeled Sites Overlapping | High (`n=9`) | Medium (`n=8`) | Low (`n=6`) |
|---|---:|---:|---:|---:|---:|
| `13,800 cal BP` | `+1,000 yr` | **`5 / 23` (`21.7%`)** | `0 / 9` | `1 / 8` | `4 / 6` |
| `13,300 cal BP` | `+500 yr` | **`10 / 23` (`43.5%`)** | `1 / 9` | `3 / 8` | `6 / 6` |
| `13,050 cal BP` | `+250 yr` | **`17 / 23` (`73.9%`)** | `3 / 9` | **`8 / 8`** | **`6 / 6`** |
| `12,850 cal BP` | `+50 yr` | `22 / 23` (`95.7%`) | `8 / 9` | `8 / 8` | `6 / 6` |
| **`12,800 cal BP` (YDB target)** | **`0 yr`** | **`23 / 23` (`100.0%`)** | **`9 / 9`** | **`8 / 8`** | **`6 / 6`** |
| `12,550 cal BP` | `−250 yr` | **`17 / 23` (`73.9%`)** | `3 / 9` | **`8 / 8`** | **`6 / 6`** |
| `12,300 cal BP` | `−500 yr` | **`12 / 23` (`52.2%`)** | `1 / 9` | `5 / 8` | `6 / 6` |
| `11,800 cal BP` | `−1,000 yr` | **`5 / 23` (`21.7%`)** | `0 / 9` | `0 / 8` | `5 / 6` |

- **Effective Specificity Windows:**
  - **`W_50` (`≥ 50%` of sites overlap):** **`930 years`** (`12,260–13,190 cal BP`).
  - **`W_80` (`≥ 80%` of sites overlap):** **`300 years`** (`12,630–12,930 cal BP`).
  - **`W_90` (`≥ 90%` of sites overlap):** **`210 years`** (`12,710–12,920 cal BP`).
- Notice the split by tier: **100% of Medium (`8/8`) and Low (`6/6`) sites overlap both `13,050` and `12,550 cal BP`** (500 years apart!), and all 6 Low-tier sites overlap everywhere from `13,300` to `12,300 cal BP` (a full millennium). Only the 9 High-tier sites narrow the `W_80` window to `300 yr`—and as Pillar 1 shows, the raw IntCal20 dates at its nine sites (six of them High tier, three Medium) scatter across `544 years` (`436` without Blackwater Draw).

---

## 4. How the Pre-Registered Verdict Rules Applied

| Verdict Rule | Criteria in `protocol.md` §4 | Outcome |
|---|---|---|
| 1. `synchronous_single_event` | `LST` passes `M1`; Panel `1A-Primary` passes `M0` (`p_T ≥ 0.05` & `p_SD ≥ 0.05`) with `≥ 7/9` overlap; `W_80 ≤ 400 yr` | **FAIL** — `1A-Primary` fails `M0` (`p_T = 0.0005`) and achieves only `5/9` overlap |
| 2. `asynchronous_diachronous_scatter` | `LST` passes `M1`; BOTH `1A-Primary` AND `1A-Favorable` fail `M1` on BOTH `p_T < 0.01` AND `p_SD < 0.01` | **FAIL** — `1A-Favorable` passes `M1` (`p_T = 0.157`), and `SD` variance is inflated by Blackwater Draw's `±235 yr` error |
| 3. `underconstrained_not_synchronous` | `LST` passes `M1`; `1A-Primary` fails `M0`; `W_50 ≥ 1,000 yr` AND `< 25%` of 32 sites tightly directly dated | **NEAR MISS (`70 yr`)** — `1A-Primary` fails `M0` (`0.0005`) and only `12.5%` (`4/32`) are tightly directly dated, but `W_50 = 930 yr` (`< 1,000 yr` threshold) |
| 4. **`ambiguous_or_mixed`** | Any outcome not cleanly satisfying (1), (2), or (3) | **SELECTED** |

We report **`ambiguous_or_mixed`** strictly as pre-registered, without moving our `1,000 yr` goalpost down to `900 yr` after seeing `930 yr`.

---

## 5. Limits

- **Northern Hemisphere 9-site scope in Pillar 1.** Pillar 1 covers the 9 Northern Hemisphere sites whose raw uncalibrated direct-YDB `¹⁴C` measurements were openly accessible in primary tables; Southern Hemisphere sites (e.g., Pilauco in Chile, Wonderkrater in South Africa) require SHCal20 and were outside this locked table.
- **Old-wood ambiguity is real.** Charcoal dates at Arlington Canyon, Abu Hureyra, and Bull Creek could carry decades to a couple of centuries of inbuilt tree age (heartwood or deadwood). That is why Panel 1A-Favorable and Model M1 were built into the protocol—and why the favorable 9-site panel cannot rule out a single event once `50 yr` mean old-wood offset is allowed.
- **Kennett et al. (2015) intervals were calibrated on IntCal13.** Shifting the Pillar 2 OxCal models from IntCal13 to IntCal20 shifts absolute ages slightly (~20–40 yr older around 12.8–13.0 ka) without shrinking the 940-year median interval widths or closing the placebo overlap.
- **Single-vendor run so far.** Code and results were generated by Antigravity (Google DeepMind) and have not yet been independently replicated by a second vendor's agent.

---

## What this means

A real single-year Late Glacial catastrophe—the Laacher See volcanic eruption just two centuries before the Younger Dryas—leaves radiocarbon dates across five distant sites that lock onto the same age (`T = 0.42`, `100%` overlap, `44-year` spread). The claimed Younger Dryas impact layers do not. Their raw direct radiocarbon dates scatter across `544 years` (`T = 631`), failing even generous lab-error and old-wood tolerances, while nearly 9 out of 10 of the 32 claimed sites across four continents either lack a direct date on the proxy layer or carry error bars wider than 300 years—so broad that three-quarters of modeled sites still "overlap" dates 250 years too early or too late. Only if one discards older charcoal dates at key sites as old wood and allows a `50-year` old-wood model can the tightest subset be reconciled with a single year. The dating record neither proves a synchronous cosmic catastrophe nor rules out one hidden inside wide error bars and old wood—which means claims that 23–32 sites across four continents are proven to be the exact same age go well beyond what the dates can support.

---

## Reproducibility

- **Code:** `questions/ydb-site-synchrony/analysis/site_synchrony.py` (data extraction, IntCal20 calibration, forward simulation, Pillar 2 audit) and `analysis/make_figures.py` (interactive HTML figures).
- **Tests:** `python3 questions/ydb-site-synchrony/analysis/test_site_synchrony.py` (`5/5` synthetic verification tests passing).
- **Outputs:** `results/summary.json`, `results/pillar1_dates.csv`, `results/pillar2_sites.csv`, `results/placebo_curve.csv`.
- **Speedup note (zero protocol change):** After locking, `calibrate_batch_medians` in `analysis/site_synchrony.py` was accelerated by caching an exact per-`σ` 1-`¹⁴C`-year lookup table on the identical 1-yr IntCal20 grid `[10500, 15500]` (matching brute-force evaluation to within `1.0 cal yr` by the spot check; first reported as `< 0.2`, zero change to statistical model or `protocol.md`).
