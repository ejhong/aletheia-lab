# Was there an exceptional fire 12,800 years ago?

Issue #43 · Lane: data · Written 2026-11-23 by Claude Fable 5.2 (Anthropic), directed by Eugene

## Question

Greenland ice records the smoke of northern wildfires as spikes of ammonium. Supporters of the Younger Dryas
impact hypothesis point to an ammonium peak at the start of the Younger Dryas cold period, about 12,900 years
ago, as the trace of continent-wide fires set off by a cosmic impact.

**Is the ammonium peak at the Younger Dryas onset exceptional against the rest of each ice-core record, or one
of many like it?**

"Exceptional" is defined below, before any value near the onset has been looked at.

## Why it matters

Nobody disputes that the ice holds a peak. The dispute is whether it stands out. That is a question about a
comparison set, which can be fixed in advance and computed from public data.

What each side says:

- **For.** Wolbach et al. 2018 (*Journal of Geology* 126:165–184, doi:10.1086/695703), abstract, as returned by a
  web search; the article is closed-access and **we have not read it**: "The YD onset also exhibits increased
  dust concentrations, synchronous with the onset of a remarkably high peak in ammonium, a biomass-burning
  aerosol. In four ice-core sequences from Greenland, Antarctica, and Russia, similar anomalous peaks in other
  combustion aerosols occur, including nitrate, oxalate, acetate, and formate, reflecting one of the largest
  biomass-burning episodes in more than 120,000 y." Status: `unverified` wording, verified title and journal
  (Crossref). Search summaries also say the paper ties the GISP2 ammonium peak to 1712.20–1712.30 m depth;
  `unverified`.
- **Against, or at least not for.** Fischer et al. 2015 (*Nature Geoscience* 8:723–727, doi:10.1038/ngeo2495;
  read in the accepted manuscript at <https://nora.nerc.ac.uk/id/eprint/511166/>) counted fire peaks in the NGRIP
  ammonium record from 10,000 to 110,000 years ago. They write that the average size of fire peaks "shows only a
  minor decrease during the Younger Dryas (YD)", and that fire peak frequency "shows a rather immediate response
  to the BA climate variations and a clear YD minimum". They do not test the onset itself.
- Holliday et al. 2023 (*Earth-Science Reviews* 247:104502) criticise the ice-core claims; we could not read the
  relevant passages (publisher blocks automated access) and do not rely on them.
- Petaev et al. 2013 (*PNAS* 110:12917–12920), abstract read via Crossref, report a platinum anomaly in GISP2 ice
  "at the YDB" and mention "the ammonium and nitrate spike due to the biomass destruction" as a separate event in
  the same ice. The depth of the platinum peak (about 1712.0–1712.125 m) is from memory and `unverified`.

We know of no published test that ranks the onset against every other stretch of the record with a rule fixed in
advance. If one exists, this is a replication of it.

## Data and sources

All public. Hashes in `MANIFEST.md`.

| Short name | What | Source |
|---|---|---|
| NGRIP 10-yr | NGRIP decadal means of ammonium and nitrate, 10,270–107,620 yr b2k | PANGAEA doi:10.1594/PANGAEA.935814, CC-BY-4.0 |
| NGRIP 1 mm | NGRIP ammonium every millimetre, 1404.7–2930.4 m | PANGAEA doi:10.1594/PANGAEA.935818, CC-BY-4.0 |
| NEEM 10-yr | NEEM decadal means, −10 to 121,440 yr b2k | PANGAEA doi:10.1594/PANGAEA.935831, CC-BY-4.0 |
| GICC05 | NGRIP depth against age, every 20 years to 60,000 yr b2k | NOAA, `gicc05-60ka-20yr.txt` |
| GISP2 ions | GISP2 discrete samples, ammonium and nitrate, with each sample's top and bottom age | NOAA, `gisp2/chem/iond.txt` (Mayewski et al. 1997) |

The first three are described in Erhardt et al. 2022 (*Earth Syst. Sci. Data* 14:1215–1231, read). They were
measured by continuous flow analysis; the usable depth resolution is about 1 cm. "b2k" means years before
2000 CE. The GISP2 file gives ages in years before present on the GISP2 timescale; we use them as given and
never compare a GISP2 age with a GICC05 age.

**What was looked at before this plan was written** (`explore/structure.py`): column layouts, age and depth
ranges, missing-value shares, sample durations, annual layer thickness, and medians computed with the interval
12,000–14,000 years excluded. No concentration from 12,000 to 14,000 years ago has been printed or plotted.
The author knows from the literature that a peak is claimed and that the claim is disputed, and does not know
how it ranks.

## Method

### The series

Seven ammonium series, each a set of equal time bins.

| Series | Core | Bin length T | Span compared (years) | Role |
|---|---|---|---|---|
| N10 | NGRIP 10-yr file | 10 | 10,300–107,620 b2k | long record |
| E10 | NEEM 10-yr file | 10 | 0–121,440 b2k | long record |
| G60 | GISP2 ions | 60 | 0–110,000 BP | long record |
| G20 | GISP2 ions | 20 | 0–50,000 BP | long record for measure Z only; otherwise fine |
| N3 | NGRIP 1 mm | 3 | 10,300–60,000 b2k | fine |
| N1 | NGRIP 1 mm | 1 | 10,300–20,000 b2k | fine |
| G10 | GISP2 ions | 10 | 0–15,000 BP | fine |

Old ice is thinner per year and GISP2's samples get longer with depth, so a spike of a given size looks smaller
the older it is. Each series therefore uses one bin length across its whole span, chosen so that the coarsest
part of the span still resolves it: GISP2 samples last at most 7.8 years before 15,000 BP, 18.6 years before
50,000 BP and 57.3 years before 110,000 BP; NGRIP layers are at least 1.9 cm per year to 20,000 b2k and 0.9 cm
per year to 60,000 b2k, against a 1 cm resolution.

**Bins.** Let `a0` be the start of the target window (below). Bin `j` (any integer) covers ages
`[a0 + j·T, a0 + (j+1)·T)`. Bins are made wherever a file has data, also outside the span; the span only limits
which windows are compared.

- *N10, E10.* A file row with age `a` (in ka, times 1000) covers `[a, a+10)`. It is bin `j = round((a − a0)/10)`.
  The value is the file's ammonium value; an empty field is missing.
- *N1, N3.* Each 1 mm row gets an age by linear interpolation of age on depth in the GICC05 file (its columns are
  age b2k, NGRIP depth in m, δ18O, counting error; data rows are those with four numeric fields). Rows outside
  the file's depth range get no age. A row belongs to bin `j = floor((age − a0)/T)`. The bin value is the mean of
  the non-missing ammonium values among its rows. The bin is missing if it has no rows or if fewer than half of
  its rows have a value.
- *G10, G20, G60.* Data rows follow the header line that starts with `Top`; fields are tab-separated: top depth,
  bottom depth, Na, NH4, K, Mg, Ca, Cl, NO3, SO4, top age, bottom age. Use rows whose top and bottom ages are
  both below 999,999 and bottom age above top age. A sample overlaps a bin by the length of the intersection of
  `[top age, bottom age)` with the bin. The bin value is the overlap-weighted mean of the samples' values. The
  bin is missing if the total overlap is less than `T/2`.

### The target window and the comparison windows

The target is a 300-year window centred on the Younger Dryas onset in each core's own timescale.

- **NGRIP and NEEM:** `[12,750, 13,050)` yr b2k, so `a0 = 12,750`. The onset of Greenland Stadial 1 is at
  12,896 ± 4 yr b2k (maximum counting error 138 yr) and NGRIP depth 1526.52 m (Rasmussen et al. 2014, *Quat. Sci.
  Rev.* 106:14–28, Table 2, read).
- **GISP2:** `[12,735, 13,035)` yr BP, so `a0 = 12,735`. The centre, 12,885 yr BP, is the file's age for
  1712.0–1712.3 m, the depths that supporters cite for the platinum and ammonium peaks.

A width of 300 years is meant to be generous to the hypothesis: the event may fall anywhere within 150 years of
the onset and still be counted at full height.

**Comparison windows.** Window `k` covers `[a0 + 300k, a0 + 300(k+1))`; the target is `k = 0`. A series uses
every window that lies wholly inside its span. A window is *usable* if at least 80% of its bins have a value. If
the target window is not usable in a series, that series is reported as not testable.

### Three measures of a peak

For each bin `j` with a value `x_j`, take the bins `j−n … j+n`, where `n = floor(150/T)` (150, 50, 15, 7, 2 for
T = 1, 3, 10, 20, 60). If fewer than half of those `2n+1` bins have values, the bin has no background.

- Background `m_j`: the median of the values in those bins.
- Excess `e_j = x_j − m_j`.
- Robust log score `z_j = (ln x_j − median(ln x)) / (1.4826 · MAD(ln x))`, with median and MAD (median absolute
  deviation from that median) over the same bins. Bins with `x ≤ 0` are left out of the logs. If the MAD is zero
  the score is missing. Not computed for T = 60. This follows the fire-peak detection of Fischer et al. 2015, who
  flag values of log ammonium above a running median plus a multiple of the MAD.

For each usable window:

- **H**, peak height: the largest `x_j` in the window (µg/kg).
- **E**, peak excess: the largest `e_j` in the window.
- **Z**, peak score: the largest `z_j` in the window.

Also recorded, for description only: the window mean of `x`, and the number of bins with `z_j ≥ 3`.

**Rank.** For a measure, the target's rank is 1 plus the number of other usable windows in the series with a
strictly larger value. `N` is the number of usable windows with that measure, target included.

### Decision rule

The rule uses the long-record series: N10, E10 and G60 for H and E; N10, E10 and G20 for Z. So each measure has
one series per core.

- *Top 1%* means rank ≤ max(1, floor(0.01·N)). *Top 5%* means rank ≤ floor(0.05·N).

| Verdict | Condition |
|---|---|
| **Exceptional** | On one and the same measure, the target is in the top 1% in at least two of the three cores. |
| **Unusual** | Not exceptional, and on one and the same measure the target is in the top 5% in at least two cores. |
| **One core only** | Neither of the above, and the target is in the top 1% in one core on some measure. |
| **Ordinary** | None of the above. |

If windows were exchangeable, "unusual" or better would arise by chance about 2% of the time and "one core only"
up to about 9%. Windows are not exchangeable (see weaknesses), so these are guides, not error rates.

The fine series (N1, N3, G10, and G20 for H and E) are reported with the same ranks. They do not change the
verdict, because the claim is about the whole record. If the target is rank 1 in N3 or G20, the answer says so
in its first lines, as "the largest peak in 50,000 to 60,000 years at fine resolution".

### Reported alongside, not part of the rule

1. **Other widths.** The same ranks with windows of 120 and 600 years (same centre: `a0` moves to 12,840 and
   12,600 for NGRIP and NEEM, 12,825 and 12,585 for GISP2; bins are re-anchored to the new `a0`; the background
   rule is unchanged).
2. **Nitrate.** H and E for nitrate in N10, E10 and G60 (same rules, nitrate column). Nitrate in ice has many
   sources and is a poor fire tracer on its own (our judgement, from memory); it is here because supporters cite
   it.
3. **What it would take.** For each long series and measure: the value a window needs to reach the top 1% and
   the top 5%, beside the target's value.
4. **The ten highest windows** of each long series on each measure, with their ages.
5. **The cited sample.** In the raw GISP2 file, the largest ammonium value among samples overlapping the target
   window: its depth, its value, and the share of all samples (bottom age ≤ 110,000) that it exceeds. This is not
   a fair comparison, since older samples are longer; it is given because a figure of this kind is quoted.

### Checks on the program, before the lock

- Unit tests on made-up series: a planted spike is rank 1 on all three measures; binning of made-up samples
  matches hand calculation.
- A **decoy run** (`--decoy`): the target is replaced by another usable window, chosen with a fixed random seed
  from windows at least ten windows away from the real target, and only the decoy's ranks are printed. This
  exercises every line of the program on the real files without showing the result.

### Replication

A model from another vendor writes its own program from this protocol and the format notes alone, and its
window values and ranks are compared with ours. Differences are traced and reported.

## What would count

- **For the claim:** verdict "exceptional". Ammonium at the onset would then be among the three or four highest
  peaks of about 100,000 years in two separate cores.
- **Partly for:** "unusual", or rank 1 in the fine series only.
- **Against:** "ordinary". A peak that many other 300-year stretches match or beat is not evidence of a unique
  event, whatever caused it.
- "One core only" is reported as not established: a single core can carry one large local plume.

Neither outcome settles whether an impact happened. An ordinary peak removes this line of evidence; an
exceptional one supports unusual fire at that time, not its cause.

## Known weaknesses

- **Concentration, not deposition.** Snowfall changes with climate, and the same smoke gives a higher
  concentration in a dry period. Measures E and Z allow for the background level; none corrects for snowfall.
- **Greenland sees mainly North American fires**, and nearer ones more strongly (Fischer et al. 2015). Burning
  elsewhere could go unrecorded.
- **Windows are not independent draws.** Warm periods have more ammonium and more fire peaks. Measure H will
  favour warm periods; the Younger Dryas onset sits at the end of one. Ranks are descriptions of the record, not
  probabilities.
- **A very short event is diluted.** A one-year pulse is a tenth of its size in a 10-year bin. All windows are
  diluted alike, so the ranking stays fair, but a pulse can sink into the noise. The fine series are there for
  this.
- **Layer thinning within a span.** Bins are equal in years, yet the same spike is smoothed slightly more in
  thinner layers. This works against older and colder ice, the Younger Dryas included, most in N1.
- **Timescales.** GISP2 ages below about 50,000 years are less certain; only window boundaries are affected.
- **Two of three cores share a laboratory and method** (NGRIP, NEEM). GISP2 was measured differently, on discrete
  samples.
- **A column mix-up was corrected in the NGRIP 10-yr file** in May 2026 (its PANGAEA change note). Medians now
  match the expected sizes (ammonium about 6, nitrate about 80 µg/kg). The 1 mm file carries no such note; its
  ammonium median at 2000–2100 m is 4.3 µg/kg, the size expected of ammonium.
- **The supporters' paper has not been read.** If their claim rests on a different record or measure, this test
  may not address it. The results will say what was and was not tested.
- **One session** proposed, designed, runs and writes up the question.

## Budget

$25. Expected spend under $5: one round of design review by two other vendors' models, and one replication.
