# Does Tunguska show in the ice?

Issue #100 · Lane: data · Budget: $20 · Written 2026-11-23 by Claude Fable 5.2 (Anthropic), directed by Eugene

## Question

On 30 June 1908 an object burst in the air over the Tunguska river in Siberia. It is the one large airburst of
which we are certain.

**In Greenland ice cores away from Summit, do the layers of 1908 and 1909 hold more ammonium than the years
around them, beyond what such records do by chance? If so, by how much?**

This asks whether 1908 left a Greenland-wide ammonium mark. It does not ask what made the mark: see "What this
cannot tell apart". Nitrate and black carbon (soot) are measured the same way and reported beside the answer.

## Why it matters

The Younger Dryas impact hypothesis has a form in which the Earth met many airbursts like Tunguska over years
(Napier 2010; abstract read). Questions #43 and #60 found a century of high ammonium in Greenland ice after the
Younger Dryas cold began, and an exploratory check in #43 found that it is a raised steady level with few
short spikes. What that says about airbursts depends on what one airburst leaves in the ice, which this lab has
not measured.

Melott et al. 2010 (*Geology* 38:355–358; abstract read on arXiv:0907.1067) report, for Tunguska, a "nitrate
enhancement in GISP2H and GISP2 ice cores, plus an unexplained ammonium spike", and say that the forest fire at
Tunguska "was far too small to account for this". Both cores are from Summit, in central Greenland. The reviewer
of this plan names later work arguing that such paired spikes in Summit ice are the ordinary mark of smoke from
North American forest fires (Wolff et al. 2012; Duderstadt et al. 2014, 2016; Legrand et al. 2016). We have not
read those papers and cite them as unverified.

A mark made by something spread through the Arctic air should show at other sites. Smoke that drifted over
Summit need not. Either outcome is useful. If 1908 stands out across Greenland, its size can be set beside the
Younger Dryas rise. If it does not, then Tunguska left no general mark that these records can see, and the plan
says in advance how large a mark they could see.

## Data and sources

Thirteen ice cores from nine sites, all public; files, URLs, licences and hashes are in `MANIFEST.md`.

| Core | Site | Laboratory | Ammonium | Nitrate | Black carbon | Sulphur | Samples a year near 1900 |
|---|---|---|---|---|---|---|---|
| `neem_s1` | NEEM, north-west | DRI | yes | yes | yes | yes | about 12 |
| `tunu2013` | Tunu, north-east | DRI | yes | yes | yes | yes | about 8 |
| `tunu2022a` | Tunu | DRI | yes | yes | yes | yes | about 6 |
| `humboldt` | Humboldt, north-west | DRI | yes | yes | yes | yes | about 12 |
| `act11d` | ACT11d, south-west | DRI | yes | yes | no | yes | about 20 |
| `negis` | NEGIS, north-east | Copenhagen | yes | no | no | no | about 150 |
| `ngrip1` | NGRIP, central north | Copenhagen and others | yes | yes | no | sulphate | about 5 |
| `summit2010`, `summit2023` | Summit, central | DRI | yes | yes | yes | yes | 12 to 16 |
| `tunu2022b`, `tunu_n` | Tunu | DRI | yes | yes | first only | yes | 7 and 12 |
| `ht95` | Hans Tausen, far north | DRI | yes | yes | yes | yes | about 4 |
| `b20` | B20, north | AWI | yes | yes | no | sulphate | about 2 |

`analysis/tunguska.py ingest` turns each downloaded file into `data/standard/<core>.tsv`: one row per sample, with
the sample's date as a decimal year CE and the four chemicals in the file's own units, in columns `year`, `nh4`,
`no3`, `bc`, `s` (sulphate goes in `s`). A cell is empty where the file has no value or a value of zero or less.
Such values are few (81 of 19,127 ammonium values in `neem_s1`; about 2% in `tunu2013`, where they fall in the
same rows for every chemical and look like a missing-value code). Dates are the file's own, except that NEGIS and
NGRIP give depths only; their dates come from straight-line interpolation in the published depth of each year
(the NEGIS age file; the GICC05 annual layer depths for NGRIP1, at each sample's mid-depth). Everything below
starts from those standard tables.

### Which cores

**The test cores** are the first seven rows of the table, at six sites: NEEM, Tunu (two cores), Humboldt,
ACT11d, NEGIS and NGRIP.

**Summit is reported apart**, because its 1908 layer has been seen. In exploring this question we looked at the
GISP2 ion record (not one of the cores above), where the sample spanning 1908 to 1910 holds ammonium about 13
times its neighbours. That observation and the paper above are why the question was asked, so Summit cannot test
it.

**Four cores are reported apart because their dating near 1900 is not supported** by a check made before the
lock on sulphur alone (`explore/dating_check.py`). Each core's yearly sulphur from 1850 to 1950, in logs and
with its 21-year running median taken off, was correlated with that of `neem_s1`, whose chronology is tied to
historical eruptions, with the core moved by −2 to +2 years. A core is kept if its correlation with no move is
at least 0.3 and within 0.05 of its best.

| Core | Correlation with no move | Best move | Kept |
|---|---|---|---|
| `tunu2013` | 0.35 | none | yes |
| `tunu2022a` | 0.41 | one year, 0.44 | yes |
| `humboldt` | 0.43 | none | yes |
| `act11d` | 0.35 | none | yes |
| `ngrip1` | 0.56 | none | yes |
| `tunu2022b` | 0.14 | one year, 0.25 | no |
| `tunu_n` | 0.18 | one year, 0.28 | no |
| `ht95` | 0.05 | no clear best | no |
| `b20` | −0.13 | no clear best | no |

NEGIS has no sulphur. It is kept on its published layer-counted chronology; its ammonium outside 1905 to 1912
correlates with `neem_s1` at 0.27 with no move and 0.27 moved one year. No core's dates are altered.

### What has been seen before the lock

- The GISP2 sample described above.
- No ammonium, nitrate or black-carbon value dated 1905 to 1912 in any of the thirteen cores. The data were
  found and downloaded by an agent told not to open 1895 to 1920, and the program was developed in a mode that
  removes 1905 to 1912 from every series. Outside those eight years, yearly values and window scores were
  computed and their extremes seen: the largest ammonium windows in the reference begin in 1894, 1888 and 1862.
- Sulphur in every year, used only for the dating check.
- The number of samples in each year, from the date columns. Every test core has at least 3 ammonium samples in
  each year from 1900 to 1915.
- A comparison of designs for sensitivity, with 1905 to 1912 removed (`explore/design_power.py`), which is why
  the window is two years and not three.

## Method

### Yearly values

For a core and a chemical, the value of a calendar year `Y` is the arithmetic mean of the samples whose decimal
year `d` satisfies `Y ≤ d < Y+1` and that have a value. The year has a value only if at least one such sample
has a value and at least half of all the rows of the standard table dated in that year do (`2 × with ≥ all`).

### Windows

A *window* is two consecutive years, `y` and `y+1`, named by `y`. The target is the window 1908. The reference
windows are the target and every other window whose start differs from 1908 by a multiple of 2 and that lies
wholly within 1800 to 1990: starts 1800, 1802, …, 1988, which is 95 windows. They do not overlap, so no year is
counted in two windows.

### The score of a window

For one core and one chemical, and the window `y`:

- The *background years* are the fifteen before the window and the fifteen after it: `y−15 … y−1` and
  `y+2 … y+16`. At least 20 of these 30 must have a value, or the window has no score for that core.
- Take natural logs of the yearly values. Let `m` be the median of the logs of the background years and
  `s = 1.4826 ×` the median of their absolute differences from `m` (medians of an even count are the mean of the
  two middle values). If `s` is zero the window has no score.
- A year's score is `(ln value − m) / s`. The window's score is the larger of the scores of its two years, or the
  one it has if a year has no value. If neither year has a value there is no score.

**Site score:** the mean of the window scores of the site's test cores that have one.

**The sites used** are the test sites that have a score in the target window. There must be at least 5 for
ammonium (4 for nitrate, 3 for black carbon, 4 for sulphur); otherwise the chemical is "not testable".

**Network score** of a window: the mean of the site scores of the sites used. A reference window counts only if
every one of the sites used has a score there, so that every window is a mean over the same sites.

### The test

The target's **rank** is 1 plus the number of counted windows with a strictly larger network score; its
**fraction** is its rank divided by the number of counted windows, the target included. With 1905 to 1912
removed there were 53 counted windows for ammonium, from 1856 to 1966, so about 55 are expected.

| Verdict, for ammonium | Condition |
|---|---|
| **Exceptional** | Fraction 0.04 or less (the largest or second largest of about 55). |
| **Elevated** | Not that; fraction 0.10 or less. |
| **Ordinary** | Anything else. |
| **Not testable** | Fewer than 5 sites have a score in the target window. |

Under no effect the chance of "exceptional" is about 4% and of "elevated or better" about 9 to 10%. No finer
probability is claimed. The same ranks and verdict words are computed for nitrate, black carbon and sulphur and
reported, without deciding anything.

### Reported alongside, not part of the verdict

1. For each site used: its own score, and its rank and fraction among the tiling windows where that site has a
   score. The sites whose own fraction is 0.10 or less.
2. **Size.** For each test core, the larger of its two target years divided by the median of its background
   years (the plain yearly values, not logs), minus one: the extra ammonium in units of a typical year's. Cores
   with fewer than 20 background years are left out. Per site (mean of its cores) and the median over sites,
   called `E`.
3. Yearly means from 1903 to 1913 for every core, so that the reader can see where any high value falls, and in
   particular whether it falls in 1910, the year of very large fires in North America.
4. Variants: a three-year window, 1907 to 1909, with its own tiling; the largest sample of each year in place of
   its mean; each site left out in turn (one fewer site required); the four DRI sites alone and the two other
   sites alone (no minimum number of sites); the four cores of doubtful dating added as extra cores.
5. Summit and the four cores of doubtful dating, core by core: rank among the tiling windows where that core has
   a score, size, and yearly means from 1903 to 1913.
6. Sulphur by the same measures. Katmai's sulphur should put the window 1912 at or near the top of the sulphur
   ranking; that window's rank is reported as a check that the method sees a known event.
7. The ten largest windows in the reference for each chemical.
8. **Sensitivity.** In each of 400 trials (`numpy.random.default_rng(100)`; draws in the order given here): pick
   one counted window, uniformly among those lying wholly before 1890 or starting after 1925; pick one of its two
   years; decide for each site, in alphabetical order, whether it receives the pulse (always, or with probability
   one half in the second version); for each core of a receiving site that has a value in that year, add `k`
   times the core's median yearly ammonium over 1880 to 1930 inclusive. Recompute that window's network score
   only, and rank it against the unchanged scores of the other counted windows. Report how often it is called
   elevated or better (fraction 0.10 or less) and exceptional (fraction 0.04 or less), for `k` = 0.1, 0.25, 0.5, 1,
   2 and 4, with the always-receiving version first and `k` in that order. Exact agreement between programs is not
   expected; agreement within a few percentage points is.

   Run before the lock with 1905 to 1912 removed: a pulse of two typical years' ammonium at every site is called
   elevated or better in 91% of trials and exceptional in 22%; of four, 100% and 96%; of one, 32% and 6%. If each
   site receives it with probability one half, a pulse of four is called elevated or better in 52%.

### What the result would say about the Younger Dryas

An illustration of scale, reported with the verdict and labelled as that. It is not a measurement of a rate.

In NGRIP ice (exploratory check in #43), the steady yearly level of ammonium was 11.0 µg/kg in the 150 years
before the Younger Dryas cold began and 29.7 in the 150 years after. Snowfall there fell from 0.081 to 0.069 m of
ice a year (Kindler et al. 2014, means over the same years). So the ammonium reaching the ice each year rose by a
factor of about 2.3: each year of that century and a half brought about `F = 1.3` typical earlier years' worth
extra.

- If the verdict is exceptional or elevated, with the median size `E` above zero: matching that rise would take
  about `F / E` events like Tunguska in **every year** for 150 years.
- If the verdict is ordinary: no number is derived from the size. The statement made is that the records would
  very probably have shown a pulse of two typical years' worth or more at every site, so if Tunguska left a mark
  across Greenland it was probably smaller than that, and matching the rise would then take more than about two
  such events every three years (`F / 2 = 0.65` a year). The observed `E` and its spread across sites are given beside it.

What this leaves out, each of which could change the answer by a large factor:

- **Where it happened.** Tunguska is in central Siberia, far from Greenland and not upwind of it. The same event
  over Canada would leave more. One event says little about the average over many.
- **Spikes against a level.** Ammonium stays in the air for days. Events once or twice a year would leave
  separate spikes, and #43 found few spikes in that century. A count of events per year from yearly totals does
  not answer that; it is a second, separate difficulty for the idea.
- **Different air and ice.** Winds, rain and snowfall in the Younger Dryas were not those of 1908, and yearly
  layers there are a third as thick.
- **A typical year is assumed to bring about the same ammonium then and now.** Around 1900 the typical level in
  these cores is 4 to 9 µg/kg, with snowfall two to three times higher than at NGRIP before the Younger Dryas
  (from memory; unverified), so the two are within a factor of about two.
- **Marks are assumed to add up in proportion.**

### Checks on the program

Unit tests on made-up series (yearly values, the window score by hand, the tiling, the rule that every window
uses the same sites, rank and verdict words, size). The blind runs above. Sulphur at Katmai in the locked run.
The dates in the standard tables were checked against a second, independently written reader
(`explore/crosscheck_dates.py`): counts of samples per year from 1880 to 1935 agree for every core except
`ngrip1`, where the second reader dates a sample by the top of its depth range and ours by the middle.

### Replication

A model from another vendor writes its own program from this protocol and a note on the layout of the standard
tables, and its ranks, verdicts and sizes are compared with ours. The step from the downloaded files to the
standard tables is not replicated.

## What would count

- **Toward "1908 left a mark across Greenland":** exceptional, with most of the sites used in their own top
  tenth.
- **Toward "the Summit spike was not Greenland-wide":** ordinary.
- **In between:** elevated, or a high rank carried by one or two sites.

## What this cannot tell apart

- **An airburst from a fire year.** Smoke from large northern forest fires raises ammonium and nitrate together,
  several times a century. Nitrate rising with ammonium does not point to an airburst. Black carbon does not
  settle it either: around 1908 Greenland's soot was dominated by coal smoke, so a forest fire adds
  proportionately little. If 1908 ranks high, the ice cannot say whether the cause was the airburst, the forest
  it burned, or other fires that year. The date fixed in advance is the only protection, and a partial one.
- **1908 from its neighbours,** if a core is a year out. The yearly means from 1903 to 1913 are published so
  that a peak in 1907 or 1910 can be seen for what it is.

## Known weaknesses

- **Few reference windows.** Requiring the same sites in every window leaves about 55, from the 1850s to the
  1960s. The verdict words are coarse for that reason.
- **Dating.** The window is two years wide. A core that runs a year early would put a mid-1908 event in 1907 and
  miss. The sulphur check is on the whole century, not on 1908 itself, and NEGIS could not be checked by it.
- **Four of the six test sites share a laboratory and a family of chronologies.** They are not independent
  witnesses. The two other sites are reported alone, and one of those, NGRIP, carries a published warning that
  its ammonium may be biased.
- **Yearly means blur a short event.** A plume lasting days is averaged with the rest of its year, so a null
  result rules out a large yearly total, not a brief spike. The largest-sample variant is reported for that.
- **Seasons.** Ammonium peaks in summer. A year with only part of its samples can read high or low. The rule
  asks for half the samples and no more.
- **Some records are marked preliminary** by their authors (Humboldt, ACT11d).
- **The standard tables are our reading of thirteen differently laid-out files.** A mistake there would not be
  caught by the replication. The dates were cross-checked; the chemical columns were not.
- **Choices made knowing the reference.** The window width, the verdict thresholds and the choice of cores were
  fixed after seeing scores outside 1905 to 1912, though not the target.
- **One session** proposed, designed, runs and writes up the question, knowing the Summit observation. One round
  of outside review rebuilt the test: the first plan used overlapping windows, moved three cores' dates by a rule
  the reviewer showed to be unsafe, and turned a null result into a bound it could not support.

## Budget

$20. Expected spend under $3: review of this plan and replication, by one other vendor's model.
