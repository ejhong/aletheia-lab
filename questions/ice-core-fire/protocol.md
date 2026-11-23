# Was there an exceptional fire 12,800 years ago?

Issue #43 · Lane: data · Written 2026-11-23 by Claude Fable 5.2 (Anthropic), directed by Eugene

## Question

Greenland ice records the smoke of northern wildfires as spikes of ammonium. Supporters of the Younger Dryas
impact hypothesis point to an ammonium peak at the start of the Younger Dryas cold period, about 12,900 years
ago, as a trace of fires set off by a cosmic impact.

**In three Greenland ice cores, is the largest ammonium spike in a 300-year window around the Younger Dryas
onset exceptional against the other 300-year windows of the same record, or one of many like it?**

"Exceptional" is defined below, before any value near the onset has been looked at.

This is a question about Greenland ammonium only. It is narrower than the supporters' case, which draws on
several chemicals and several archives.

## Why it matters

A peak "stands out" only against a comparison set. That set can be fixed in advance and computed from public
data.

What the literature says, and how far we have checked it:

- **For.** Wolbach et al. 2018 (*Journal of Geology* 126:165–184, doi:10.1086/695703), abstract, as returned by a
  web search; the article is closed-access and **we have not read it**: "The YD onset also exhibits increased
  dust concentrations, synchronous with the onset of a remarkably high peak in ammonium, a biomass-burning
  aerosol. In four ice-core sequences from Greenland, Antarctica, and Russia, similar anomalous peaks in other
  combustion aerosols occur, including nitrate, oxalate, acetate, and formate, reflecting one of the largest
  biomass-burning episodes in more than 120,000 y." Wording `unverified`; title and journal verified (Crossref).
  The NGRIP and NEEM files used here were released in 2021, after the paper; we do not know which of those
  measurements its authors had seen. NGRIP ammonium had been analysed by Fischer et al. in 2015.
- **Context.** Fischer et al. 2015 (*Nature Geoscience* 8:723–727, doi:10.1038/ngeo2495; read in the accepted
  manuscript at <https://nora.nerc.ac.uk/id/eprint/511166/>) counted fire peaks in annual NGRIP ammonium from
  10,000 to 110,000 years ago. They report that the average size of fire peaks "shows only a minor decrease
  during the Younger Dryas (YD)" and that fire peak frequency shows "a clear YD minimum". This concerns the cold
  period as a whole. It is compatible with one very large peak at its onset and is not evidence against one.
- Petaev et al. 2013 (*PNAS* 110:12917–12920), abstract read via Crossref, report a platinum anomaly in GISP2 ice
  "at the YDB" and mention "the ammonium and nitrate spike due to the biomass destruction" as an event with
  different timing. A reviewer of this plan states, with high confidence, that the paper puts the platinum about
  30 years before that spike; we have not read the paper's body. `unverified`.
- Holliday et al. 2023 (*Earth-Science Reviews* 247:104502) criticise the ice-core claims; we could not read the
  passages and do not rely on them. Reviewers of this plan also named Melott et al. 2010 (*Geology*) as having
  compared the GISP2 peak with the rest of that record; not read, `unverified`.

We have not found a published test that ranks the onset against every other stretch of these records with a
rule fixed in advance. We did not search exhaustively.

The target was not chosen blind. It was chosen because a peak has been reported there. The test is of a
nominated feature.

## Data and sources

All public. Hashes in `MANIFEST.md`.

| Short name | What | Source |
|---|---|---|
| NGRIP 10-yr | NGRIP decadal means of ammonium and nitrate, 10,270–107,620 yr b2k | PANGAEA doi:10.1594/PANGAEA.935814, CC-BY-4.0 |
| NGRIP 1 mm | NGRIP ammonium every millimetre, 1404.700–2930.400 m | PANGAEA doi:10.1594/PANGAEA.935818, CC-BY-4.0 |
| NEEM 10-yr | NEEM decadal means, −10 to 121,440 yr b2k | PANGAEA doi:10.1594/PANGAEA.935831, CC-BY-4.0 |
| GICC05 | NGRIP depth against age, every 20 years to 60,000 yr b2k | NOAA, `gicc05-60ka-20yr.txt` |
| GISP2 ions | GISP2 discrete samples, ammonium and nitrate, with each sample's top and bottom age | NOAA, `gisp2/chem/iond.txt` (Mayewski et al. 1997) |

The first three are described in Erhardt et al. 2022 (*Earth Syst. Sci. Data* 14:1215–1231, read): continuous
flow analysis, usable depth resolution about 1 cm, concentrations in µg/kg. "b2k" means years before 2000 CE.
The GISP2 file gives concentrations in ppb (the same unit) and ages in years BP on the GISP2 timescale; we use
them as given and never compare a GISP2 age with a GICC05 age.

**What was looked at before this plan was locked** (`explore/`): column layouts, ranges, missing shares, sample
durations, layer thickness, and medians computed with 12,000–14,000 years excluded. A cross-check outside
12,000–14,000 showed that 10-year means made from the 1 mm file and the GICC05 file reproduce the NGRIP 10-yr
ammonium column (all 4,245 rows within 5%) when a row labelled `a` covers `[a, a+10)`, and do not match its
nitrate column. No concentration from 12,000 to 14,000 years ago has been printed or plotted, and the decoy run
(below) leaves the target window out.

## Method

### File reading

- **PANGAEA files.** Data start after the line beginning `*/`; the next line is the header; fields are
  tab-separated; an empty field is missing. Columns in the 10-yr files, in order: `Age [ka b2k]`, `EC [µS/cm]`,
  `Na+ [µg/kg]`, `Ca2+ [µg/kg]`, `[NH4]+ [µg/kg]`, `[NO3]- [µg/kg]`. The 1 mm file has `Depth ice/snow [m]`
  first and the same five after it. Age in years is the ka value times 1000, rounded to the nearest integer;
  every age is a multiple of 10. A 10-yr row labelled `a` covers `[a, a+10)`. The 1 mm file has one row for
  every millimetre of its range, with empty fields where nothing was measured. Negative concentrations, if any,
  are kept as they are.
- **GICC05 file.** Data rows are the lines with exactly four whitespace-separated numeric fields: age b2k, NGRIP
  depth (m), δ18O, counting error. There are 3,000, with age and depth both increasing.
- **GISP2 file.** Data rows follow the header line whose first field is `Top`; fields are tab-separated: top
  depth, bottom depth, Na, NH4, K, Mg, Ca, Cl, NO3, SO4, top age, bottom age. Use rows whose top and bottom ages
  are both below 999,999 and whose bottom age is above its top age (11,038 rows; the rest have no age). No
  ammonium or nitrate value is missing in those rows. Samples do not overlap one another; there are gaps between
  some.

### Bins

Let `a0` be the start of the target window (below) and `T` the bin length in years. Bin `j` (any integer) covers
ages `[a0 + j·T, a0 + (j+1)·T)`. Bins are made wherever a file has data, also outside the span a series compares.

- **From a 10-yr file** (T = 10, 20 or 60): the bin value is the mean of the non-missing values of the rows whose
  age `a` satisfies `a0 + j·T ≤ a < a0 + (j+1)·T`. The bin is missing if fewer than half of the `T/10` rows it
  should hold have a value (so: 1 of 1, 1 of 2, 3 of 6 are enough).
- **From the 1 mm file** (T = 1 or 3): each row gets an age by linear interpolation of age on depth between the
  GICC05 rows; rows outside the GICC05 depth range get no age. A row belongs to bin `j = floor((age − a0)/T)`.
  The bin value is the mean of the non-missing ammonium values among its rows. The bin is missing if it has no
  rows or fewer than half of its rows have a value.
- **From GISP2 samples** (T = 10, 20 or 60): a sample overlaps a bin by the length of the intersection of
  `[top age, bottom age)` with the bin. The bin value is the sum of overlap × value divided by the sum of
  overlaps. The bin is missing if the sum of overlaps is less than `T/2`.

### The target window and the comparison windows

The target is a 300-year window centred near the Younger Dryas onset in each core's own timescale.

- **NGRIP and NEEM:** `[12,750, 13,050)` yr b2k; `a0 = 12,750`. The onset of Greenland Stadial 1 is at
  12,896 ± 4 yr b2k and NGRIP depth 1526.52 m, with a maximum counting error of 138 yr on the absolute age
  (Rasmussen et al. 2014, *Quat. Sci. Rev.* 106:14–28, Table 2, read).
- **GISP2:** `[12,735, 13,035)` yr BP; `a0 = 12,735`. The centre, 12,885 yr BP, is the file's age for depths
  1712.0–1712.3 m, which the platinum paper and the supporters' paper are reported to discuss (`unverified`). We
  have not fixed the GISP2 climatic onset independently. The window is meant to be wide enough to hold it; the
  600-year variant below is the check.

Within NGRIP the onset is located to a few years on the core's own timescale (the 138 years concern its
absolute age, which does not matter here), so ±150 years is far wider than needed there. The width is a
deliberate allowance in the claim's favour: the largest spike anywhere in the window is credited to
the onset. The cost is that the winning spike may not be at the onset at all; the timing rule below and the
reported ages deal with that.

**Comparison windows.** Window `k` covers `[a0 + 300k, a0 + 300(k+1))`; the target is `k = 0`. A series uses
every window with `a0 + 300k ≥ span start` and `a0 + 300(k+1) ≤ span end`. A window is *usable* if at least 80%
of its bins have a value (`5 × present ≥ 4 × bins`).

### The series

Three **tiers** carry the decision. Within a tier every core has the same bin length and the same nominal span,
so like is compared with like.

| Tier | Bin length | Span (years, each core's timescale) | Series | Windows (about) |
|---|---|---|---|---|
| T10 | 10 | 10,300–107,620 | N10 (NGRIP 10-yr), E10 (NEEM 10-yr) | 320 |
| T20 | 20 | 10,300–50,000 | N20, E20 (from the 10-yr files), G20 (GISP2) | 130 |
| T60 | 60 | 10,300–107,620 | N60, E60, G60 | 320 |

GISP2's samples last at most 18.6 years at ages up to 50,000 BP and 57.3 years up to 110,000 BP, which is why
it enters at 20 and 60 years. NEEM ice older than about 108,000 years is folded (Erhardt et al. 2022) and is left
out by the span. The tiers leave out the last 10,300 years, most of the Holocene, because the NGRIP files do not cover them.

Reported with the same statistics, outside the decision:

| Series | Source | Bin length | Span | Why |
|---|---|---|---|---|
| N3 | NGRIP 1 mm | 3 | 10,300–60,000 | finest look that old layers still resolve (≥ 0.9 cm per year) |
| N1 | NGRIP 1 mm | 1 | 10,300–20,000 | annual (layers ≥ 1.9 cm per year) |
| G10 | GISP2 | 10 | 10,300–15,000 | GISP2 at its finest (samples ≤ 7.8 years) |
| E10h | NEEM 10-yr | 10 | 0–107,620 | with the Holocene |
| G20h | GISP2 | 20 | 0–50,000 | with the Holocene |
| G60h | GISP2 | 60 | 0–110,000 | with the Holocene |

### Measures

For bin `j` with value `x_j`, let `n = floor(150/T)` (150, 50, 15, 7, 2 for T = 1, 3, 10, 20, 60) and take the
`2n+1` bins `j−n … j+n`. Bins that do not exist count as missing.

- **Background** `m_j`: the median of the values present among those bins (the mean of the two middle values
  when their number is even). If fewer than half of the `2n+1` bins have a value (`2 × present < 2n+1`), bin `j`
  has no background.
- **Excess** `e_j = x_j − m_j`.

For each usable window:

- **E, peak excess** (the measure the decision uses): the largest `e_j` among its bins, in µg/kg; and the age at
  which that bin starts (if bins tie, the youngest). E is missing if fewer than 80% of the window's bins have an
  excess.
- **H, peak height:** the largest `x_j`. Reported. H mostly tracks climate: warm periods have higher ammonium
  throughout.
- **Z, peak score:** the largest `z_j`, where `z_j = (ln x_j − median(ln x)) / (1.4826 · MAD(ln x))`, median and
  MAD taken over the bins among the same `2n+1` that have `x > 0`. It is missing if bin `j` has no background,
  `x_j ≤ 0`, or the MAD is zero. Not computed for T = 60. Reported with its numerator and MAD. This is modelled
  on the detector of Fischer et al. 2015 but is not a replication of it: they worked at annual resolution.
- The window mean of `x` over present bins. Reported.

**Rank.** The target's rank on a measure is 1 plus the number of other usable windows in the series with a
strictly larger value. `N` counts the usable windows that have the measure, target included. The number `q` of
windows tied with the target is reported, and the realised fraction is `(rank + q)/N`.

### Decision rule

Only measure E decides. In a series, *top 1%* means rank ≤ max(1, floor(0.01·N)) and *top 5%* means
rank ≤ max(1, floor(0.05·N)). The realised fractions are reported beside every verdict.

A tier **passes at 1%** (or 5%) if two of its cores both have the target in the top 1% (or 5%) on E and that
pair is not ruled out by timing.

**Timing.** NGRIP and NEEM are both on GICC05. As a pair they count only if their winning bins start within 60
years of each other. A pair that includes GISP2 cannot be checked this way, since its timescale differs; it
counts, and the pass is labelled "timing not checkable". So if only NGRIP and NEEM qualify and their peaks are
more than 60 years apart, the tier does not pass, and the note "high windows, different peaks" is attached.

The verdicts, checked in this order:

| Verdict | Condition |
|---|---|
| **Not testable** | In two or more of the three cores, the target window has no E in any tier series. |
| **Exceptional** | Some tier passes at 1%. |
| **Unusual** | Some tier passes at 5%. |
| **Not corroborated** | The target is in the top 1% in at least one tier series, but no tier passes. |
| **Not met** | None of the above. |

"Not met" means the criterion was not met. It is read together with the made-up fires below, which show what
size of added ammonium pulse reaches each series' threshold.

No chance levels are claimed for these verdicts. The cores share climate, transport and, for two of them, a
timescale and a laboratory; the windows are not exchangeable.

In the first lines of the results, beside the verdict: the rank of the target on E in every series of the three
tiers, and in N3, N1 and G10, with the age of each winning bin and how far it lies from the onset (12,896 b2k)
in NGRIP and NEEM.

### What the test can see: made-up fires

To learn what size of event the rule would catch, a made-up one-year pulse is added to the real series and the
window is scored again.

- A pulse of size `A` (µg/kg·yr) at year `[t, t+1)` adds `A × overlap / T` to each bin of a 10-yr-file or 1 mm
  series, where overlap is the part of the year inside the bin. In GISP2 each sample gets
  `A × (part of the year inside the sample) / (the sample's duration)`, and the bins are remade; the part of the
  year that falls in a gap between samples is lost.
- Sizes: 20, 50, 100, 200, 500, 1,000, 2,000 and 5,000 µg/kg·yr. For scale, the median ammonium outside
  12,000–14,000 years is about 6 µg/kg, so a pulse of 100 is roughly 17 years' worth arriving in one year.
- For each series of the three tiers and for N3 and N1: 300 placements, each a random usable window other than
  `k = −1, 0, 1` and a random year in it (one generator, `numpy.random.default_rng(43)`, used for the series in
  the order N10, E10, N20, E20, G20, N60, E60, G60, N3, N1; for each placement draw the window index, then the
  year as an integer offset from the window start).
- Reported: for each size, the share of placements in which the window's E reaches the series' top-1% value, and
  the same for top 5%. About 1% of placements land in a window that was already there.

This measures one series at a time. It does not measure the two-core rule, and it says nothing about how much
forest a pulse of a given size stands for.

The pulse is added after the ice and the instrument have smoothed the real signal, so recovery in the 1 mm
series is somewhat optimistic.

### Reported alongside, not part of the rule

1. **Other widths.** Ranks on E with windows of 120 and 600 years about the same centre (`a0` = 12,840 and
   12,600 for NGRIP and NEEM; 12,825 and 12,585 for GISP2; bins re-anchored to the new `a0`).
2. **Grid phase.** Ranks on E with `a0` moved by half a bin (`T/2`), which moves bins and windows together (for
   T = 10 from the 10-yr files this cannot be done and is skipped).
3. **One-sided backgrounds.** The onset is a climate step, and a centred median straddles it. E is recomputed
   with the background taken as the higher, and then as the lower, of two medians: bins `j−n … j−1` and bins
   `j+1 … j+n` (each needs at least half its bins present; if only one side qualifies it is used alone). The
   higher is the cautious version, the lower the generous one. Every other abrupt climate step in the record
   gets the same treatment.
4. **Nitrate.** E and H for nitrate in N10, E10 and G60. Nitrate has many sources and is a poor fire tracer on
   its own (our judgement, from memory); supporters cite it for fire and, a reviewer notes, for nitrogen oxides
   made by the shock of an impact.
5. **The winning bins.** For the target and the five highest windows on E in every tier series: the age of the
   winning bin, its value and background. For N1 and N3, the NGRIP depth and annual layer thickness at the
   target's winning bin.
6. **The ten highest windows** on E in each tier series, with ages.
7. **The cited GISP2 samples.** Every GISP2 sample between 1711.5 and 1713.0 m: depths, ages, ammonium. And the
   largest ammonium sample in the target window, with the share of all aged samples it exceeds. The last figure
   is not a fair comparison (older samples are longer) and is given because figures of this kind are quoted.
8. **Do the cores move together?** The rank correlation of E across windows between N10 and E10, which share a
   timescale.

### Checks on the program, before the lock

- Unit tests on made-up series: binning against hand calculation; a planted spike is rank 1; windows with too
  few values are dropped; the verdict rule returns each verdict on constructed inputs, including the timing
  rule.
- A **decoy run** (`--decoy`): the target window `k = 0` is removed from every table, another usable window at
  least ten windows away (chosen with seed 43) stands in for it, and the ranks, the verdict and the made-up fires
  are computed and printed. The items "reported alongside" are not run in decoy mode. It exercises the main code
  on the real files without showing the result.

### Replication

A model from another vendor writes its own program from this protocol and the format notes alone. Its window
values, ranks and verdict are compared with ours; differences are traced and reported. The made-up fires need
not be replicated.

## What would count

- **For the claim:** "exceptional". In two cores, measured alike, the window around the onset would rank among
  the top one to three windows of roughly 40,000 or 100,000 years.
- **Partly for:** "unusual".
- **Not established:** "not corroborated". A single core can carry one large local plume.
- **Against, within limits:** "not met", provided the made-up fires show that a large pulse would have reached
  the thresholds. A spike that many other windows match or beat is not evidence of a unique fire.

A rank of 1 on E in N3 or N1 is reported by name beside the verdict, with its core, span and bin length. It is a
single-core result and does not change the verdict.

Neither outcome settles whether an impact happened. An exceptional spike supports unusual northern fire near
that time, not its cause. An ordinary one leaves the supporters' other lines of evidence untouched.

## Known weaknesses

- **Concentration, not deposition.** Snowfall changes with climate; the same smoke gives a higher concentration
  in a dry period. E allows for the background level but not for snowfall. Snowfall dropped at the onset, which
  favours the claim.
- **Greenland sees mainly North American fires**, and nearer ones more strongly (Fischer et al. 2015). Burning
  elsewhere could go unrecorded.
- **A short event is diluted by the bin**, and more by a 60-year bin than a 10-year one. Within a tier the
  nominal bin is the same for all windows, but a pulse can sink into the noise, and the coarse tiers favour
  sustained rises over sharp spikes. In GISP2 the dilution also varies with sample length and with where a pulse
  falls among samples. The made-up fires measure this.
- **Equal bins are not equal resolution.** Within a span, older ice has thinner layers and GISP2 has longer
  samples, so the same spike is smoothed more there. Against much older ice the target is at an advantage;
  against younger ice, at a disadvantage.
- **The background straddles a climate step** at the onset; see the one-sided variant.
- **The winning spike may not be the cited one,** and may sit a century from the onset. Ages are reported so the
  reader can see.
- **Timescales.** GISP2 is not tied to GICC05 here, and its anchor depth is unverified.
- **Shared method.** NGRIP and NEEM were measured by the same group with the same technique.
- **A column mix-up was corrected in the NGRIP 10-yr file** in May 2026 (its PANGAEA change note). The
  cross-check above confirms the present columns. The NEEM file carries no such note and was not cross-checked;
  its medians (ammonium 5.9, nitrate 80 µg/kg) match NGRIP's.
- **The supporters' paper has not been read.**
- **One session** proposed, designed, runs and writes up the question.

## Budget

$25. Expected spend under $5: design review by two other vendors' models, and one replication.
