# Did anyone smelt metal before the Bronze Age? Ice and peat as a side-channel — Results

- **Question:** #82, `lane:data`.
- **Plan locked:** 2026-11-24T17:13:38Z (`protocol.lock`, commit `2b998f8`), before the results were committed. Unchanged since.
- **Amendments:** two. The first (one archive's lead file covers only 2,549 to 1,184 BP) was written by the study. The second records what the spot check found.
- **Who did the work:** AI did. Antigravity (Google DeepMind) designed and ran the study on 24 November 2026. Claude Fable 5.2 (Anthropic), with Claude Opus 5.5 sub-agents, spot-checked it the same day and wrote this corrected report. Eugene Jhong directed both. No specialist has reviewed it, and it has not been replicated by a second company's model.

## Answer

**Nothing unusual shows before 5,000 years ago. But these records are too coarse to carry the conclusion the first report drew. They do not register metalworking that archaeology shows did happen, and the test as locked would have missed the Roman Empire.**

- **What was found.** In East Greenland ice (8,000 to 5,000 years ago), central Greenland ice (47,400 to 40,400), a peat bog in southern Germany (14,300 to 5,000) and scattered samples of Antarctic ice, no stretch of 50 years or more has lead at three times its usual level against dust. The program reruns to the same numbers.
- **What the records can see.** The same rule, applied to the periods when we know people were smelting, fires in none of them in Greenland before the industrial age: not the Bronze Age, not the Iron Age, not Rome, not the Middle Ages. Adding artificial pollution to the real Greenland record shows that the rule needs four to five times Rome's lead to fire.
- **What they demonstrably miss.** Copper was being smelted in the Balkans by about 5000 BC, 7,000 years ago (Belovode, Serbia). A Serbian bog records lead pollution from about 3600 BC. None of the six records here shows any of it. So "no evidence of metallurgy before the Bronze Age" cannot be the conclusion: there was metallurgy before the Bronze Age, and these records are blind to it.
- **The plan's own check failed.** A null was to count only if Roman and medieval lead stood out at twice the earlier level. In the Greenland record the Roman figure is 1.56.
- **The "upper bound" is not one.** The first report said lost smelting before 5,000 years ago is bounded at 47% of Rome's, or 1.56 thousand tonnes of lead a year. That number is the ordinary scatter of the record; a steady source, however large, would be absorbed into the baseline it is measured against; and the conversion to tonnes used a Roman figure (3.3 thousand tonnes a year) that is not in the paper cited for it, which gives an average of 1.1.
- **One of the six records was misidentified.** The "Store Mosse bog, southern Sweden" is the Laphroaig bog on Islay, Scotland, sampled for a study of storms. Its lead readings are at the floor of the instrument and show nothing either way.
- **Where and when there is no data.** For the northern hemisphere there is nothing at all between 40,400 and 14,300 years ago. The period usually proposed for a lost Ice Age civilisation, 20,000 to 11,600 years ago, is covered by one German bog from 14,300 on and 13 samples of Antarctic ice, and the Antarctic record does not register Rome.

What the data support: no lead industry of medieval European size or larger, lasting a century or more and placed where its smoke would reach Greenland or southern Germany, in the stretches of time sampled. That is worth knowing and is much less than was claimed.

## Spot check and corrections

A spot check is not a replication. It verified the data files, reran the program, applied the locked rule to the known periods, added artificial signals to the real record, and read the cited papers.

What holds:

- The lock matches the plan. All nine data files match their recorded checksums, and eight are what the manifest says they are.
- Rerunning the program gives the same results file (3,722 numbers, to sixteen figures).
- The numbers in the tables below match the results file, with the exceptions noted.
- The isotope shift in the German bog is real and recomputes exactly (`p = 4.85×10⁻⁶`); it begins at about 3,550 BP.

What does not:

1. **Sensitivity.** Described above. In the German bog, none of the 147 readings from 5,000 to 3,000 BP exceeds the highest reading from before 5,000 BP, and only one of 21 Roman readings does.
2. **The 5,000 BP line.** It was called the start of metallurgy. Smelting is some 2,000 years older, and the Bronze Age began at different times in different places (around 2200 BC in western Europe).
3. **The Roman control.** Below the plan's threshold in Greenland (1.56 against 2.0) and in the German bog as published (1.40). In the Scottish bog the known periods fail outright, and the report switched there to raw lead, a measure the plan did not name.
4. **The upper bound.** Circular baseline; noise level; wrong emission figure. With the paper's 1.1 thousand tonnes the numbers would be 0.5 and 0.9, give or take a factor of two, for sources in Europe. McConnell and others (2018) say transport to Greenland from sources such as China is "nearly an order of magnitude less efficient", and Antarctica shows nothing even for Rome, so there is no bound for Asia worth the name and none for the southern hemisphere.
5. **Three stretches of raised lead in Greenland before 5,000 BP** were explained away as local dust. The dust tracers do not rise with the lead. They are small, about the size of the weaker Roman centuries, and unexplained.
6. **A choice not disclosed.** For the German bog the plan defines enrichment against the pre-5,000 BP median. The program computed that and then tested the authors' published figure instead. On the plan's definition, 12 readings before 5,000 BP reach three times the baseline, two of them consecutive (7,481 to 7,496 BP), which meets the plan's wording for "sustained". The baseline there includes the end of the Ice Age, when the basin was a lake turning into a bog, so this is more likely a flaw in the definition than a signal. It should have been reported.
7. **The statistics.** `p = 10⁻¹⁰⁴` and `10⁻²⁵⁷` come from treating thousands of closely spaced measurements as independent. Century by century the Roman and medieval periods still stand out, at about `10⁻⁵`.
8. **The misidentified bog,** above. The rise in titanium that the first report put down to farming falls at the dates the bog's own authors identify as storms.
9. **"47,000 years ... completely flat."** About 26 of those 42 thousand years have no northern data.
10. **Smaller things.** Smelter smoke travels in the lower atmosphere, not the stratosphere. The crustal ratio 19/83 is credited to the wrong source. The Antarctic samples labelled "Bronze/Iron" are Roman in date. The Alpine core's paper is Legrand and others (2025), *PNAS Nexus*. A required output of the plan, the bound from the Ice Age Greenland core, was not reported (it is 124% of the Roman level, which says how little that core constrains). A line in the log written before the lock, describing the Alpine core as covering 9,750 years, was changed in the results commit without a note.

The plan and the program with its results were committed seven minutes apart, and the first amendment, said to have been written before the analysis, was committed with the results. Git cannot show the order. Nothing in the plan needs knowledge of the results.

The spot check's scripts and outputs are in `spotcheck/`.

## The locked run in detail

The tables are the first run's. Sentences and labels around them have been corrected.

### Tests 0 and 1. The known periods and the scan before 5,000 BP

| Archive | Pre-5 ka Window (Samples) | Pre-5 ka Median EF (Max) | Bronze/Iron (`5–2.15 ka`) | Roman (`2.15–1.65 ka`) | Medieval (`1.0–0.5 ka`) | Industrial (`<0.25 ka`) | Sustained Pre-5 ka `EF ≥ 3` |
|---|---|---:|---:|---:|---:|---:|---:|
| **RECAP** (E. Greenland, volc-masked) | `7.98–5.00 ka` (`923`) | `1.00` (100-yr max `1.36`) | `1.09` (`p=3×10⁻¹³`) | **`1.56`** (`p=3×10⁻¹⁰⁴`) | **`2.17`** (`p=10⁻²⁵⁷`) | **`8.75`** (`p=6×10⁻²⁰⁰`) | **0** |
| **GISP2** (C. Greenland, volc-masked) | `47.4–40.4 ka` (`4,480`) | `1.00` (100-yr max `1.57`) | — | — | — | — | **0** |
| **Dome du Goûter** (French Alps, `EF_UCC`) | *covers `2.55–1.18 ka`* (Amend. 1) | — | `2.99` (`2.55–2.15 ka`) | **`77.33`** (`862 pg/g`) | — | — | — |
| **Füramoos** (S. Germany peat XRF) | `14.34–5.00 ka` (`284`) | `0.55` (max `2.91`) | **`1.02`** (`p=5×10⁻²²`) | **`1.40`** (`p=1×10⁻⁸`) | **`2.03`** (`p=1×10⁻⁶`) | **`5.52`** | **0** |
| **Laphroaig bog**, Islay, Scotland (called "Store Mosse, Sweden" in the plan; raw `Pb`, at the instrument's floor) | `6.42–5.00 ka` (`21`) | `0.00 mg/kg` (max EF `1.42`) | `0.00 mg/kg` | `1.00 mg/kg` | `4.00 mg/kg` | **`54.50 mg/kg`** | **0** |
| **EPICA Dome C** (E. Antarctica `Pb/Ba`) | `40.0–5.0 ka` (`30`) | `1.00` (1 isol. rad. pt `4.25`) | — | `1.00`, `0.75` (`N=2`) | — | — | **0** |

*Notes.* The p-values in this table treat each closely spaced measurement as independent, which they are not; compared century by century, Roman against pre-5,000 BP is `p = 2×10⁻⁵` and Medieval `p = 3×10⁻⁶`. In RECAP and GISP2 the enrichment factor is measured against the median of the pre-5,000 BP data themselves, so a pre-5,000 BP median of `1.00` is true by construction. The Roman median of 1.56 in RECAP is below the 2.0 that the plan required of the known periods. The Laphroaig numbers in this row are raw lead in whole mg/kg and do not come from the committed program; 13 of the 21 values before 5,000 BP are zero or below and the rest are 1. Three stretches in RECAP before 5,000 BP (5,525–5,675, 6,625–6,700 and 7,175–7,275 BP) have lead 1.3 to 1.6 times the usual level while the dust tracers cerium, manganese and strontium are at 0.9 to 1.15 times theirs. The first report put them down to local dust; the data do not support that, and they are best called unexplained. They are about the size of the weaker Roman centuries.

### Test 2. Other metals (cadmium, bismuth, thallium in GISP2; copper, zinc in the Laphroaig bog)
- **GISP2 (`47.4–40.4 ka`, 70 century bins, volcanic-masked):** `0` bins reach `EF ≥ 3.0` and `0` sustained 50-year anomalies occur across `Pb/Ce` (p95 `1.44`, max `1.57`), `Cd/Ce` (p95 `1.79`, max `2.10`), `Bi/Ce` (p95 `1.41`, max `1.62`), or `Tl/Ce` (p95 `1.53`, max `1.60`).
- **Laphroaig bog (`6.4–5.0 ka`; the known periods fail here too, Roman copper `EF` 0.44):** `0` sustained pre-5 ka anomalies in `Cu/Ti` (max `1.45`; raw `Cu` stays at `1.0 mg/kg` pre-5 ka vs. `2.0` Roman/Medieval and `8.5` Industrial) or `Zn/Ti` (one isolated point `3.06`, `0` sustained).

### Test 3. Lead isotopes (`206Pb/207Pb`)
- **Füramoos (S. Germany, `14.3–0.2 ka`, `N=30` ICP-MS):** Every pre-5 ka sample (`N=12`) sits tightly in the natural crustal dust band (`mean = 1.2085 ± 0.0046`, range `1.2040–1.216`). Post-5 ka samples (`N=18`) plunge to median `1.1900` and minimum `1.1391` (`Mann-Whitney p = 4.85 × 10⁻⁶`), marking the introduction of unradiogenic European ore lead. Coupled pre-5 ka anomalies: **0**.
- **EPICA Dome C (E. Antarctica, `217–2 ka`):** Natural Pleistocene (`217–40 ka`, `N=42`) mean `206Pb/207Pb = 1.2155 ± 0.0162`. Every `40–5 ka` sample (`N=30`) lies within `1.193–1.257`, with zero unradiogenic ore-lead drops (`< 1.183`).

### Test 4. The "upper bound" (see the corrections above: it is the archive's noise level, and the 3.3 kt/yr figure is not in the cited paper)
- In **RECAP (East Greenland)**, the Roman Empire (`2.15–1.65 ka`) deposits a volcanic-masked median excess of `ncPb_emp = 2.15 pg/g` (corresponding to McConnell et al. 2018's FLEXPART-modeled `~3.3 kt/yr` European atmospheric Pb emissions and `~40–80 kt/yr` total lead-silver smelting).
- Across all `30` pre-Bronze centuries (`7.98–5.00 ka`), the 95th-percentile century median is `1.01 pg/g` (**`47%` of Roman**, or **`≤ 1.56 kt/yr`** atmospheric Pb) and the absolute maximum century is `1.71 pg/g` (**`79%` of Roman**, or **`≤ 2.62 kt/yr`**)—and zero centuries exceed `EF = 1.36`.
- In **Füramoos**, the record before 5,000 BP stays below its Roman and later levels. It also shows no change through the Bronze Age until about 3,600 BP, the date the bog's own authors give for the first human lead there, so it does not exclude Bronze-Age-scale smelting.

## Limits

1. **Sensitivity,** as above. This is the main limit and it is severe.
2. **Coverage.** Northern hemisphere: 47,400 to 40,400 and 14,300 to 5,000 BP only, and before 8,000 BP only one bog, sampled every 55 to 145 years. Southern hemisphere: 30 Antarctic samples in 15 clusters over 35,000 years.
3. **Place.** Greenland ice hears Europe best. A source in Asia, Africa or the Americas would have to be far larger to be heard, and one in the south would not be heard at all.
4. **Lead only, in effect.** Copper smelting without lead-bearing ore, and the working of native copper and gold, leave little or nothing in these records.
5. **A steady source is invisible** where the baseline is taken from the period under test.
6. **Not read in full:** Radivojević and others (2010); Kern and others (2021) and Preunkert and others (2019) beyond their abstracts; the supplement to McConnell and others (2018).
7. **No replication** by a second company's model.

## Spending

Nothing was paid for.

## What this means

The idea was a good one: cities can drown, but smoke from smelting settles in ice and peat far away, so the ice might show whether anyone worked metal on a large scale before recorded history. The answer from these records is that nothing on the scale of medieval Europe's lead industry shows up in the stretches of time they cover. That is as far as it goes. The same records fail to show the copper smelting of 7,000 years ago that archaeologists have dug up, and they barely show Rome, so they could not have shown a smaller or more distant industry either. For most of the Ice Age in the northern half of the world, the study had no data. It does not support the sentence the first report ended on, that whatever people did before the Bronze Age "left no detectable heavy-metal pollution plume in the global atmosphere".
