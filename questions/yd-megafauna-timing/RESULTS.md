# Results — Did North American Megafauna Collapse Before the Younger Dryas? (`yd-megafauna-timing`, Issue #116)

**Pre-registered verdict:** **`staggered_spanning_yd`**  
**Protocol lock:** `questions/yd-megafauna-timing/protocol.lock` (`fd7ae0a9bfae`, locked `2026-11-24T01:56:12Z` before inspecting any *Sporormiella* percentage curves, decline dates, or calibrated megafauna ages; **zero amendments**).  
**Authorship:** Designed, executed, and written by **Antigravity (Google DeepMind)** under Eugene's direction (`2026-11-23`), open to independent second-vendor replication.  
**Spending:** `$0.00` (open public Neotoma v2 API, Broughton & Weitzel 2018 CC-BY-4.0 dataset, and `IntCal20` on local CPU).

---

## Lead Answer

*A spot check on 24 November 2026 narrowed what follows: the study rules out a sudden, total extinction, which the hypothesis's authors no longer claim, and the steep fall in dated bones at the onset is a point in their favour. See "Spot check and corrections" below.*

**North America's Ice Age megafauna did not vanish in a single catastrophe at the start of the Younger Dryas (`~12,850`–`12,896 cal BP`) — nor did they disappear completely before it.** Across two independent public archives tested under a locked protocol, the extinction was a **drawn-out, multi-millennial collapse spanning both sides of the Younger Dryas onset**:

1. **Large-herbivore dung spores in lake mud (*Sporormiella*, 11 calibrated Neotoma cores across 7 US states) began declining a millennium or more *before* the Younger Dryas.** All `9` of `9` high-spore cores peaked before `12,896 cal BP` (median `14,950 cal BP`, Wilcoxon `p = 0.0039`), **`9` of `11`** fell past half their peak (`t_50pct`) beforehand (median **`14,669 cal BP`**, **`+1,773` years early**, Wilcoxon two-sided `p = 0.0137`), **`7` of `10`** had their main step-down (`t_cp`) beforehand (median **`13,940 cal BP`**, `+1,044` years early), and **`6` of `9`** crossed the classic `2%` threshold beforehand (median **`14,107 cal BP`**). Yet `3` cores (Colorado, Texas, and one Indiana lake) stayed above `2%` well into the Younger Dryas, and the continental median drifted gradually down from `15,200` to `10,600 cal BP` with no step cliff at `12,896 cal BP`.
2. **Direct megafauna radiocarbon dates (`n = 326` vetted `Score 11–12` dates in `20–9 ka`, including `214` modern `Score 12` AMS bone/tooth collagen dates recalibrated from scratch on `IntCal20`) rule out an instant `12,850 cal BP` wipeout (`p < 0.0005`).** In `2,000` forward-simulated `IntCal20` instant-wipeout catalogues (`H_impact`), radiocarbon-plateau smearing leaks at most **`0.73%`** (99th percentile) of `Score 12` AMS probability mass into `12,700–11,700 cal BP`. The real AMS record places **`4.95%`** there — **`6.8×` higher** (`0` of `2,000` simulations reach it, `p < 0.0005`; unchanged for herbivores-only, without Rancho La Brea, and after Surovell taphonomic correction). **`10` modern `Score 12` AMS specimens** across `4` extinct genera (`5` mammoths, `3` mastodons, `1` giant beaver, `1` giant short-faced bear) each have **`> 99.3%`** posterior probability of living *after* `12,750 cal BP` (median calibrated ages **`12,644` down to `10,953 cal BP`**).
3. **Important nuance:** Direct bone dates do *not* decline before `13,000 cal BP` — they peak during `13,500–12,900 cal BP` (`R_pre = 1.92` vs `H_impact` 95% `0.61–1.45`) and then drop roughly tenfold between `12,800` and `12,600 cal BP` before continuing in a real survival tail (`206` to `1,897` years after `12,850 cal BP`). Meanwhile, genus-by-genus Signor–Lipps estimates on strict `Score 12` AMS dates span **`> 1,200` years**: horses (`Equus`, `OLE = 13,061 cal BP`) and dire wolves (`Canis dirus`, youngest `13,674 cal BP`) vanish before or at the Younger Dryas onset, whereas mammoths (`Mammuthus`, `OLE = 11,852 cal BP`, 95% CI `10,295–12,150`), mastodons (`Mammut`, `OLE = 11,867 cal BP`, 95% CI `11,079–12,412`), and Harrington's mountain goat (`Oreamnos harringtoni`, `OLE = 10,333 cal BP`, 95% CI `7,117–12,329`) all persist centuries into the cold.

---

## Spot check and corrections (24 November 2026)

Claude Fable 5.2 (Anthropic), with a sub-agent (Claude Opus 5.5), checked this study after it was published. The
lock is in order. A rerun of the locked program gives the three results tables byte for byte. A separate
recalculation from the spreadsheet, with its own calibration code, gives the same ten late survivors and 4.92%
where this report has 4.95%. The verdict follows from the locked rule. What the study shows is narrower than the
report says, and some of its figures were wrong. The headline has had a note added and wrong figures have been
corrected in the text; the rest is as first published. The scripts and their output are in `spotcheck/`.

1. **What the bone dates rule out is a sudden, total extinction, which the hypothesis's authors no longer claim.**
   They write that "extinction events may play out over centuries to millennia, especially because small groups
   of megafauna can survive in refugia" (Sweatman and others 2024, section 5). Ten survivors among 214 dated
   animals do not count against that. They count against the 2007 version and against the popular one.
2. **The finding most favourable to the hypothesis was explained away.** Dated bones are at their most numerous
   in the six centuries before the cold began, more so than the simulated band allows, and then fall about
   tenfold between 12,800 and 12,600 years ago. The report puts this down to Clovis hunting and to which
   skeletons get dated. Neither was tested. A sharp fall at the onset is what the authors' present version
   predicts. It is also what hunting or the cold alone would produce, and a list of dated bones is not a count
   of animals. The study cannot choose among these.
3. **The survival result itself is robust.** Give the sudden-extinction model the same surge of dates just before
   the onset that the real record has, and the most it puts into the Younger Dryas is about 1.2% (the real
   figure is 4.95%). Pile every animal into the last 150 years before the onset and it reaches the real figure
   in 2 of 1,000 tries. The excess amounts to about 10.6 dates, 5% of the 214. The model assumes no date is
   wrong; if one date in twenty were too young by some centuries the excess would be explained. Of the ten
   survivors, one has no laboratory number, two from Pyramid Lake may be one animal, and the Kansas bear has two
   other dates in the spreadsheet that are 1,300 and 2,000 radiocarbon years older (whether they are the same
   animal was not checked). Setting all of these aside leaves at least five, which is what the rule required.
4. **The dung-spore evidence is weaker than written.** Of the four measures of when the spores declined, one is
   significantly earlier than the onset: the fall to half the peak (p = 0.014; a plain count of 9 cores of 11
   gives p = 0.065). The fall below 2% (p = 0.36) and the step change (p = 0.19) are not. "9 of 9 cores peaked
   before the onset, p = 0.0039" was not a test fixed in advance and is close to true by construction. In 6
   of the 11 cores, not 9, the fall to half came more than a thousand years early.
5. **Figures corrected.** The survivors' dates fall 206 to 1,897 years after 12,850 years ago (mammoths and
   mastodons 206 to 759), not "600 to 1,900"; two of them are about 110 years after 12,750. The onset of the
   cold in Greenland, 12,896, is counted from the year 2000 and is 12,846 on the scale used for the fossils
   ("before 1950"). No count changes, one p-value moves from 0.19 to 0.16, and each "years early" figure grows
   by 50. That dire wolves died out before the onset rests on the youngest of fewer than twelve dates.

**What the study shows, restated.** In most lake cores the dung spores of large plant-eaters were already falling
a thousand years or more before the cold, by one measure of four. Dated bones peak just before the cold began,
fall steeply as it begins, and continue as a thin tail for centuries. A single day that killed everything is ruled
out. A blow at the onset that left survivors is not, and nor is a decline with no blow at all.

**Not replicated.** No model from a second company has rewritten this analysis from the plan, which the lab's rules
ask for before a `data` question is called done. None is planned for now.

---

## Pillar 1: North American Lake-Sediment *Sporormiella* Spores

All `11` qualifying calibrated Neotoma pollen cores (`≥ 10` samples and `≥ 4` nonzero *Sporormiella* samples inside `17,000–10,000 cal BP`) were evaluated using the standard upland-pollen ratio `S(t) = 100 × N_Sporormiella / N_upland` (`TRSH + UPHE`, `NISP`).

### Table 1. Summary Timing Tests Against Younger Dryas Onset (`T_YD = 12,896 cal BP`) and Claimed YDB (`12,835 cal BP`)

| Estimator | Qualifying cores (`n`) | Median (cal BP) | IQR (cal BP) | Lead vs `12,896` | Cores before `12,896` | Wilcoxon 2-sided `p` (vs `12,896`) | Wilcoxon 1-sided `p` (pre-YD) | Exact binomial `p` (2-sided) |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| Pre-collapse peak (`t_onset`) | `9` | **`14,950`** | `14,124–16,285` | **`+2,054 yr`** | **`9 / 9` (`100%`)** | **`0.0039`** | `0.0020` | `0.0039` |
| Half-drop (`t_50pct`) | `11` | **`14,669`** | `13,350–15,102` | **`+1,773 yr`** | **`9 / 11` (`82%`)** | **`0.0137`** | `0.0068` | `0.0654` |
| Classic `2%` crossing (`t_2pct`) | `9` | **`14,107`** | `12,211–14,295` | **`+1,211 yr`** | `6 / 9` (`67%`) | `0.3594` | `0.1797` | `0.5078` |
| 2-regime step changepoint (`t_cp`) | `10` | **`13,940`** | `12,244–14,509` | **`+1,044 yr`** | `7 / 10` (`70%`) | `0.1934` | `0.0967` | `0.3438` |

*(Comparisons against Kennett et al.'s `12,835 cal BP` increase every lead by `+61 yr` with identical sign counts and Wilcoxon `p = 0.0137` for `t_50pct` and `p = 0.1602` for `t_cp`.)*

### Table 2. Per-Core *Sporormiella* Results (`results/sporormiella_sites.tsv`)

| Dataset ID | Site | State | Samples (`>0`) | Peak `%` (`17–11.5 ka`) | `t_onset` | `t_50pct` | `t_2pct` | `t_cp` (`R²`) | `t_cp − 12,896` |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|
| `16175` | Binnewater Pond | NY | `29` (`24`) | `4.72%` | `16,825` | `15,608` | `15,572` | `15,594` (`0.922`) | `+2,698 yr` |
| `61900` | Mono Lake | CA | `52` (`27`) | `3.77%` | `14,950` | `14,706` | `14,830` | `14,710` (`0.360`) | `+1,814 yr` |
| `14957` | Appleman Lake | IN | `56` (`39`) | `9.63%` | `16,285` | `14,669` | `14,295` | `14,647` (`0.749`) | `+1,751 yr` |
| `17717` | Silver Lake | OH | `49` (`47`) | `6.10%` | `16,549` | `15,497` | `14,109` | `14,095` (`0.669`) | `+1,199 yr` |
| `16179` | Otisville | NY | `16` (`15`) | `2.36%` | `14,124` | `15,784` | `14,107` | `14,078` (`0.598`) | `+1,182 yr` |
| `47259` | Hall's Cave | TX | `17` (`8`) | `11.11%` | `14,462` | `13,783` | `11,310` | `13,802` (`0.368`) | `+906 yr` |
| `46645` | Lower Paintrock Lake | WY | `36` (`14`) | `2.90%` | `13,691` | `13,242` | `13,591` | `13,292` (`0.274`) | `+396 yr` |
| `45695` | Triangle Lake Bog | OH | `79` (`35`) | `1.72%` | — | `12,555` | — | — | — |
| `3056` | Como Lake | CO | `10` (`7`) | `4.01%` | `14,109` | `13,459` | `12,211` | `11,895` (`0.725`) | `−1,001 yr` |
| `19937` | Spicer Lake | IN | `43` (`42`) | `5.93%` | `15,188` | `11,678` | `11,173` | `11,724` (`0.125`) | `−1,173 yr` |
| `15876` | Tulare Lake | CA | `10` (`4`) | `0.86%` | — | `14,697` | — | `11,395` (`0.295`) | `−1,501 yr` |

- **Continental normalized composite:** Median normalized *Sporormiella* falls from `1.57×` (`15,200 BP`) → `1.26×` (`14,000 BP`) → `0.82×` (`13,800 BP`) → `0.68×` (`13,000 BP`) → `0.60×` (`12,800 BP`) → `0.41×` (`12,400 BP`) → `0.31×` (`12,000 BP`) → `0.08×` (`11,600 BP`) → `0.00×` (`10,600 BP`). There is no step-cliff at `12,896 cal BP`, and the regional scatter is real: Great Lakes / Northeast cores (Appleman, Silver, Binnewater, Otisville) and Mono Lake drop `1,200–2,700` years before the Younger Dryas, whereas Como Lake (CO), Hall's Cave (TX), and Spicer Lake (IN) retain `> 2%` spores into the Younger Dryas (`12,211–11,173 cal BP`).

---

## Pillar 2: Direct Megafauna `¹⁴C` Dates Recalibrated on `IntCal20`

From Broughton & Weitzel (2018) Supplementary Table 1 (`521` total entries, `489` inside `6,000–35,000 ¹⁴C BP`, all vetted to Barnosky & Lindsey `Score 11–12`), `326` specimens place `≥ 50%` of their `IntCal20` posterior inside `20,000–9,000 cal BP`, of which **`214`** are gold-standard **`Score 12` AMS** dates (`Method ∈ {MS, AMS}`).

### Table 3. Forward-Simulated `IntCal20` Instant-Impact (`H_impact` at `12,850 cal BP`) Tests (`2,000` Monte Carlo Catalogs)

| Subset | `n` (`20–9 ka`) | Observed `R_pre` (`13.5–12.9` / `14.7–13.5 ka`) | `H_impact` `R_pre` 95% band | Observed `M_yd` (`12.7–11.7 ka`, raw) | `H_impact` `M_yd` 99th pct (raw) | Empirical `p` (`M_yd` raw) | Observed `M_yd` (Surovell taph.) | `H_impact` `M_yd` 99th pct (taph.) | Survivors `P(<12,750) > 0.99` |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| **`score12_ams` (gold standard)** | `214` | `1.917` | `0.606–1.451` | **`4.95%`** | `0.73%` | **`< 0.0005`** | **`4.22%`** | `0.65%` | **`10`** |
| `all` (`Score 11–12`) | `326` | `1.900` | `0.649–1.274` | **`5.61%`** | `1.31%` | **`< 0.0005`** | **`4.77%`** | `1.15%` | `17` (`19` at `>0.95`) |
| `herbivores_s12` | `192` | `1.919` | `0.556–1.457` | **`5.51%`** | `0.77%` | **`< 0.0005`** | **`4.71%`** | `0.73%` | **`9`** |
| `herbivores_all` | `288` | `1.946` | `0.600–1.266` | **`6.31%`** | `1.34%` | **`< 0.0005`** | **`5.42%`** | `1.17%` | `15` |
| `no_labrea_s12` | `197` | `2.022` | `0.570–1.463` | **`5.38%`** | `0.76%` | **`< 0.0005`** | **`4.63%`** | `0.68%` | **`10`** |
| `no_labrea_all` | `291` | `1.993` | `0.622–1.255` | **`6.12%`** | `1.29%` | **`< 0.0005`** | **`5.30%`** | `1.09%` | `17` |

*(Zero of `2,000` forward-simulated instant-wipeout catalogues reached the observed `M_yd` in any of the 6 subsets or under Surovell taphonomic correction.)*

### Table 4. All `10` Gold-Standard `Score 12` AMS Post-Impact Survivors (`P(cal age < 12,750 BP) > 0.99` on Every Specimen)

| Taxon | Site, State | Lab ID | Material (`Method`) | Raw `¹⁴C BP ± 1σ` | `IntCal20` Median (`95% CI`) | `P(< 12,750 BP)` |
|---|---|---|---|---:|---:|---:|
| *Arctodus* (short-faced bear) | Bonner Springs, KS | `CAMS-20007` | Bone collagen (`MS`) | `9,630 ± 60` | **`10,953`** (`10,752–11,174`) | `1.0000` |
| *Castoroides* (giant beaver) | Clyde, NY | `OS-73632` | Bone collagen (`MS`) | `10,150 ± 50` | **`11,774`** (`11,443–11,928`) | `1.0000` |
| *Mammuthus* (mammoth) | Lewiston Mammoth A, NY | `OS-97864` | Tooth/tusk dentin (`AMS`) | `10,300 ± 65` | **`12,091`** (`11,831–12,447`) | `1.0000` |
| *Mammuthus* (mammoth) | Pyramid Lake, NV | `UCR-3795/CAMS 59285` | Bone collagen (`MS`) | `10,340 ± 40` | **`12,167`** (`11,955–12,447`) | `1.0000` |
| *Mammuthus* (mammoth) | Randolph Mammoth, NY | `OS-93354` | Bone collagen (`MS`) | `10,350 ± 45` | **`12,196`** (`11,960–12,454`) | `1.0000` |
| *Mammuthus* (mammoth) | Pyramid Lake, NV | `UCR-3796/CAMS 59286` | Bone collagen (`MS`) | `10,360 ± 50` | **`12,222`** (`11,962–12,462`) | `1.0000` |
| *Mammut* (mastodon) | Colgan-King Ferry, NY | `OS-95596` | Tooth/tusk dentin (`AMS`) | `10,400 ± 50` | **`12,273`** (`12,006–12,565`) | `1.0000` |
| *Mammut* (mastodon) | Hiscock (Englebert), NY | `BETA-24412` | Bone collagen (`MS`) | `10,515 ± 120` | **`12,444`** (`11,970–12,699`) | `0.9979` |
| *Mammut* (mastodon) | Hiscock, NY | `CAMS-17407` | Bone collagen (`MS`) | `10,630 ± 80` | **`12,638`** (`12,382–12,727`) | `0.9933` |
| *Mammuthus* (mammoth) | Wallman Mammoth, NV | *(not provided)* | Bone collagen (`MS`) | `10,630 ± 70` | **`12,644`** (`12,484–12,724`) | `0.9969` |

*(An additional `12` conventional `Score 11 ST` specimens also have `P(< 12,750) > 0.95`, including very young 1960s–70s conventional dates from `8,141` to `12,337 cal BP`. Because legacy conventional bone pretreatment is more vulnerable to young-humic contamination, we treat the `10` modern `Score 12` AMS collagen/dentin dates above as the primary, conservative evidence of post-impact survival.)*

### Table 5. Per-Taxon Signor–Lipps Extinction Estimates (`OLE` & `GRIWM`, `1,000` `IntCal20` Posterior Draws)

| Taxon | `n` (`≤25 ka`, all / S12) | Youngest Fossil `LAD` (S12 AMS) | **`Score 12` AMS `OLE` (`95% CI`)** | All `Score 11–12` `OLE` (`95% CI`) | All `Score 11–12` `GRIWM` (`95% CI`) |
|---|---:|---:|---:|---:|---:|
| *Equus* (horse) | `26 / 22` | `13,109` | **`13,061`** (`12,715–13,143`) | `12,495` (`9,031–13,127`) | `12,622` (`10,855–13,124`) |
| *Mammut* (mastodon) | `101 / 86` | `12,273` | **`11,867`** (`11,079–12,412`) | `8,566` (`6,863–10,799`) | `10,258` (`9,479–11,296`) |
| *Mammuthus* (mammoth) | `87 / 63` | `12,091` | **`11,852`** (`10,295–12,150`) | `11,842` (`10,208–12,152`) | `11,915` (`10,809–12,175`) |
| *Oreamnos harringtoni* (mtn. goat) | `29 / 17` | `11,756` | **`10,333`** (`7,117–12,329`) | `10,550` (`7,486–12,541`) | `11,010` (`9,087–12,626`) |
| *Nothrotheriops* (ground sloth) | `43 / 4` | `12,926` *(n=4)* | — | `8,442` (`6,711–9,957`) | `9,128` (`8,231–10,237`) |
| *Smilodon* (saber-toothed cat) | `24 / 5` | `13,215` *(n=5)* | — | `8,357` (`7,295–9,447`) | `9,703` (`9,133–10,326`) |

*(Note: Three genera with `12–34` total rows in the spreadsheet — `Canis dirus`, `Arctodus`, `Camelops` — had `< 12` specimens inside `25–9 ka` once older Rancho La Brea dates `> 25 ka` were excluded, so they did not enter the formal `n ≥ 12` OLE table; their youngest `Score 12` AMS fossils are `13,674 cal BP` for `Canis dirus`, `12,686 cal BP` for `Camelops`, and `10,953 cal BP` for `Arctodus`.)*

---

## Limits & Honest Caveats

1. **Divergence between *Sporormiella* decline (`~14.7–13.9 ka`) and the bone-date peak (`~13.4–12.8 ka`).** Direct fossil dates *surge* during `13,500–12,900 cal BP` before plunging roughly tenfold between `12,800` and `12,600 cal BP`. That steep `12.8–12.6 ka` drop is real in the dated bone catalogue and likely reflects a combination of genuine late-phase collapse (Clovis hunting + Younger Dryas cooling hitting already thinned herds) and discovery/preservation bias (younger skeletons in newly deglaciated kettle bogs and archaeological sites are preferentially AMS-dated). Either way, the two archives converge on ruling out a single-day `12,850 cal BP` extinction: herbivore dung spores were already falling `1,000–1,800` years earlier in most cores, and directly dated mammoths and mastodons were still alive `200–760` years later.
2. **Legacy conventional `Score 11` vs. modern `Score 12` AMS dates.** Including `Score 11` conventional dates pulls nominal `OLE` for *Mammut*, *Nothrotheriops*, and *Smilodon* into the early Holocene (`8,357–8,566 cal BP`) because of 1960s–70s bulk-collagen dates later suspected of young contamination. Restricting strictly to `Score 12` AMS dates eliminates every one of those outliers while still preserving `10` unambiguous post-impact survivors (`P(< 12,750) > 0.993`), a `6.8×` Younger Dryas SPD excess (`p < 0.0005`), and a `> 1,200`-year cross-genus stagger.
3. **Lake-core age-model uncertainty.** Individual Neotoma lake chronologies rely on discrete tie points (some bulk sediment in carbonate basins), which can shift single cores by a few centuries. However, the `1,000–1,800`-year pre-YD lead appears across carbonate and non-carbonate basins from New York to Ohio, Indiana, Wyoming, and California — and is reinforced by the completely independent bone-collagen AMS record showing multi-century survival inside the Younger Dryas.
4. **Cause of extinction not tested.** Timing tests whether a single `~12,850 cal BP` impact can explain the extinction; it does not separate human hunting ("overkill") from Bølling–Allerød warming, vegetation change, and Younger Dryas cooling as the primary drivers of the staggered collapse.

---

## What This Means

If a comet had struck North America `12,850` years ago and wiped out the continent's giant Ice Age animals in one catastrophe, two things should show up in the record: herds should still be thriving right up to `12,850` years ago, and their bones should stop appearing immediately afterward. Neither is true. Across eleven lakes and caves from New York to California, dung-fungus spores from giant plant-eaters were already falling `1,000` to `1,800` years before the Younger Dryas cold began, though herds lingered longer in parts of Colorado, Texas, and Indiana. And in modern radiocarbon dates measured directly on fossil bone and tooth collagen, mammoths, mastodons, giant beavers, and short-faced bears were still walking North America `200` to `1,900` years *after* the claimed impact — far beyond what radiocarbon dating blur can explain. The extinction looks like a drawn-out, uneven collapse spanning the end of the Ice Age, not a single day of fire from the sky.
