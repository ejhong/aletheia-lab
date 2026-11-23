# Does Tunguska show in the ice?

Issue #100 · Lane: data · Budget: $20 · Written 2026-11-23 by Claude Fable 5.2 (Anthropic), directed by Eugene

## Question

On 30 June 1908 an object burst in the air over the Tunguska river in Siberia. It is the one large airburst of
which we are certain.

**In Greenland ice cores other than those from Summit, do the layers of 1908 and 1909 hold more ammonium than
the years around them, beyond what such records do by chance? If so, by how much?**

Nitrate and black carbon (soot) are measured the same way and reported beside the answer.

## Why it matters

The Younger Dryas impact hypothesis has a form in which the Earth met many airbursts like Tunguska over years
(Napier 2010; abstract read). Questions #43 and #60 found a century of high ammonium in Greenland ice after the
Younger Dryas cold began, and an exploratory check in #43 found that it is a raised steady level with few
short spikes. What that says about airbursts depends on what one airburst leaves in the ice, which nobody in this
lab has measured.

Melott et al. 2010 (*Geology* 38:355–358; abstract read on arXiv:0907.1067) report, for Tunguska, a "nitrate
enhancement in GISP2H and GISP2 ice cores, plus an unexplained ammonium spike", and say that the forest fire at
Tunguska "was far too small to account for this". Both of those cores are from Summit, in central Greenland. A
mark made by something in the air over the whole Arctic should show at other sites too. A mark made by smoke that
happened to drift over Summit need not.

Either outcome is useful. If 1908 stands out across Greenland, its size can be compared with the Younger Dryas
rise. If it does not, then either Tunguska left no general mark, or these records cannot see one of its size, and
the plan says in advance how large a mark they could see.

## Data and sources

Thirteen ice cores from nine sites, all public; files, URLs, licences and hashes are in `MANIFEST.md`.

| Core | Site | Laboratory | Ammonium | Nitrate | Black carbon | Sulphur | Samples a year near 1900 |
|---|---|---|---|---|---|---|---|
| `neem_s1` | NEEM, north-west | DRI | yes | yes | yes | yes | about 12 |
| `tunu2013`, `tunu2022a`, `tunu2022b` | Tunu, north-east | DRI | yes | yes | yes | yes | 6 to 9 each |
| `tunu_n` | Tunu | DRI | yes | yes | no | yes | about 12 |
| `humboldt` | Humboldt, north-west | DRI | yes | yes | yes | yes | about 12 |
| `act11d` | ACT11d, south-west | DRI | yes | yes | no | yes | about 20 |
| `ht95` | Hans Tausen, far north | DRI | yes | yes | yes | yes | about 4 |
| `negis` | NEGIS, north-east | Copenhagen | yes | no | no | no | about 150 |
| `ngrip1` | NGRIP, central north | Copenhagen and others | yes | yes | no | sulphate | about 5 |
| `b20` | B20, north | AWI | yes | yes | no | sulphate | about 2 |
| `summit2010`, `summit2023` | Summit, central | DRI | yes | yes | yes | yes | 12 to 16 |

`analysis/tunguska.py ingest` turns each downloaded file into `data/standard/<core>.tsv`: one row per sample, with
the sample's date as a decimal year CE and the four chemicals in the file's own units (empty where missing or not
above zero). Dates are the file's own, except that NEGIS and NGRIP give depths only; their dates are found by
straight-line interpolation in the published depths of each year (the NEGIS age file; the GICC05 annual layer
depths for NGRIP1, using each sample's mid-depth). Everything below starts from those standard tables.

**The test sites** are NEEM, Tunu, Humboldt, ACT11d, Hans Tausen, NEGIS and NGRIP: seven sites.

**Two sites are reported apart and take no part in the verdict:**

- *Summit*, because its 1908 layer has been seen. In exploring this question we looked at the GISP2 ion record
  (not one of the cores above), where the sample spanning 1908 to 1910 holds ammonium about 13 times its
  neighbours. That observation and the paper above are why the question was asked, so Summit cannot test it.
- *B20*, because its dating is too loose for a two-year window: its sulphur peaks for the eruptions of 1815, 1883
  and 1912 fall in 1814, 1887 and 1915, and it has two samples a year.

### What has been seen before the lock

- The GISP2 sample just described.
- No ammonium, nitrate or black-carbon value dated 1895 to 1920 in any of the thirteen cores. The data were found
  and downloaded by an agent instructed not to open those years, and the program was developed in a mode that
  removes 1905 to 1912 from every series.
- Sulphur in every year, used only to check and line up the dating (below).
- The number of samples in each year, from the date columns.
- With 1905 to 1912 removed: the scores of all other windows, so the largest ammonium windows elsewhere in the
  record are known (they begin in 1894, 1895, 1888, 1836 and 1862), and the sensitivity figures below.

## Method

### Yearly values

For a core and a chemical, the value of a calendar year is the mean of the samples dated in that year (decimal
year rounded down) that have a value. A year has a value only if at least one of its samples has one and at least
half of them do.

### Lining the cores up

Annual layers were counted by hand and a core's dates can run a year or two out. The eruption of Katmai in June
1912, four years after Tunguska, left sulphur across Greenland in 1912 and 1913. For each core with sulphur, find
the year from 1911 to 1915 with the largest yearly sulphur value. If that year is 1914 or 1915, the core's dates
are taken to run late by one or two years, and every year of that core is moved back by that amount (for all
chemicals) before anything else is done. Otherwise the core is left alone. NEGIS has no sulphur and is left alone.

This was worked out before the lock, from sulphur only: `tunu2022b` and `ht95` move back one year, `tunu_n` two
(and `b20` two). All other cores are unmoved.

### The score of a window

A *window* is two consecutive years, `y` and `y+1`, named by `y`. For one core and one chemical:

- The *background years* are the fifteen before the window and the fifteen after it: `y−15 … y−1` and
  `y+2 … y+16`. At least 20 of these 30 must have a value, or the window has no score.
- Take natural logs of the yearly values. Let `m` be the median of the logs of the background years and
  `s = 1.4826 ×` the median of their absolute differences from `m`. If `s` is zero the window has no score.
- A year's score is `(ln value − m) / s`. The window's score is the larger of the scores of its two years, or the
  one it has if a year is missing.

**Site score:** the mean of the window scores of the site's cores that have one.
**Network score:** the mean of the site scores over the test sites that have one, defined only where at least
5 test sites have one for ammonium (4 for nitrate, 3 for black carbon, 4 for sulphur).

### The test

The target is the window 1908 (the years 1908 and 1909). The reference is every window from 1800 to 1990 that has
a network score, the target included. The target's **rank** is 1 plus the number of windows with a strictly
larger network score; its **fraction** is rank divided by the number of windows.

| Verdict, for ammonium | Condition |
|---|---|
| **Exceptional** | Fraction 0.02 or less (among the top three or so of about 190 windows). |
| **Elevated** | Not that; fraction 0.10 or less. |
| **Ordinary** | Anything else. |
| **Not testable** | The target window has no network score. |

Neighbouring windows share a year, so one unusual year puts two windows high. The ranks are of windows and are
read with that in mind. Under no effect the chance of "exceptional" is about 2% and of "elevated or better" about
10%; no further probability is claimed.

The same ranks and verdict words are computed for nitrate and for black carbon and reported, without deciding
anything.

### Reported alongside, not part of the verdict

1. For each test site: its own score, rank and fraction for the target window, and whether it is in its own top
   tenth. The number of sites in their own top tenth.
2. **Size.** For each core, the larger of its two target years divided by the median of its background years,
   minus one: the extra ammonium in units of a typical year's. Per site (mean of its cores) and the median over
   sites, called `E`.
3. Windows 1907 and 1909, as a check on dating; the dates as published, without the lining-up; each site left
   out in turn; the five DRI sites alone and the two other sites alone.
4. Summit and B20, core by core, by the same measures.
5. Sulphur by the same measures (a check that the method sees Katmai in the window 1912).
6. The ten largest windows in the whole record for each chemical.
7. **Sensitivity.** Add to every core, in one randomly chosen window outside 1890 to 1925 (in either of its two
   years, at random for each core), a pulse of `k` times that core's median yearly ammonium for 1880 to 1930, for
   `k` = 0.1, 0.25, 0.5, 1 and 2; and the same with each site receiving the pulse with probability one half.
   400 trials each (`numpy.random.default_rng(100)`). Report how often the window is then called elevated and
   exceptional. Run before the lock with 1905 to 1912 removed: a pulse of one typical year's ammonium at every
   site is called elevated in 82% of trials and exceptional in 24%; of two typical years' worth, 100% and 71%;
   of half a typical year's, 39% and 5%. If only half the sites receive it, a pulse of two years' worth is
   called elevated in 64%.

### What the result would say about the Younger Dryas

A rough conversion, reported with the verdict and labelled as rough.

In NGRIP ice (exploratory check in #43), the steady yearly level of ammonium was 11.0 µg/kg in the 150 years
before the Younger Dryas cold began and 29.7 in the 150 years after. Snowfall there fell from 0.081 to 0.069 m of
ice a year (Kindler et al. 2014, the same windows). So the ammonium reaching the ice each year rose by a factor of
about 2.3: every year of that century and a half brought about `F = 1.3` typical earlier years' worth extra.

- If the verdict is exceptional or elevated: one Tunguska left `E` typical years' worth. Matching the Younger
  Dryas rise would take about `F / E` such events **every year** for 150 years.
- If the verdict is ordinary: the records could have seen a pulse of about one typical year's worth at every site
  (called elevated in 82% of trials), so Tunguska left less than that, and matching the rise would take **more
  than** about `F / 1 ≈ 1.3` such events every year, with no upper limit set by this test.

This assumes that marks add up in proportion, that a typical year around 1900 brought about as much ammonium as a
typical year before the Younger Dryas, and that the comparison of yearly means is fair between ice of very
different layer thickness. It is an order of magnitude, not a measurement.

### Checks on the program

Unit tests on made-up series (yearly values and the half-present rule, the window score by hand, the lining-up
rule, site and network scores, rank and verdict words). The blind run above. Sulphur at Katmai, in the locked run.

### Replication

A model from another vendor writes its own program from this protocol and a note on the format of the standard
tables, and its ranks, verdicts and sizes are compared with ours. The step from the downloaded files to the
standard tables is not replicated.

## What would count

- **Toward "an airburst marks the ice":** exceptional, in most sites, with nitrate elevated too. The paper's
  reading would then extend beyond Summit, though smoke from a large fire year could do the same to ammonium, and
  black carbon is reported to help tell the two apart.
- **Toward "the Summit spike was local":** ordinary, with the test able to see a pulse of the size found at
  Summit many times over.
- **In between:** elevated, or exceptional in ammonium with a large rise in black carbon. Reported as it falls.

Whatever the verdict, this is one event. It cannot show what a different kind of object, or thousands of them,
would do.

## Known weaknesses

- **A fire year looks the same.** Ammonium rises after large northern forest fires, several times a century.
  If 1908 ranks high, the ice cannot say whether the cause was the airburst, the forest it burned, or other fires
  that year. The date fixed in advance is the only protection, and it is a partial one.
- **Dating.** The window is two years wide and the cores are lined up on an eruption four years away. A core
  that is still a year out can miss. The neighbouring windows are reported.
- **The lining-up rule uses the largest yearly sulphur value,** which is a noisy marker, and it only ever moves
  a core back.
- **Five of the seven test sites share a laboratory and a family of chronologies.** They are not independent
  witnesses. The two other sites are reported alone.
- **Yearly means blur a short event.** A plume lasting days is averaged with the rest of its year. This suits a
  comparison of total amounts and costs sensitivity.
- **Layer counting used ammonium and nitrate** in some cores to place the year boundaries, so a large spike could
  itself shift a boundary.
- **Some records are marked preliminary** by their authors (Humboldt, Tunu-N, ACT11d), and the NGRIP ammonium
  measured in Copenhagen carries a stated warning of bias.
- **The standard tables are our reading of thirteen differently laid-out files.** A mistake there would not be
  caught by the replication.
- **The conversion to the Younger Dryas** rests on the assumptions listed above.
- **One session** proposed, designed, runs and writes up the question, knowing the Summit observation.

## Budget

$20. Expected spend under $4: review of this plan by two other vendors' models, and replication.
