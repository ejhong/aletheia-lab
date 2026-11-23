# Audit the random-number network's original 500 events

Issue #74 · Lane: data · Budget: $10 · Written 2026-11-23 by Claude Fable 5.2 (Anthropic), directed by Eugene

## Question

The Global Consciousness Project (GCP) ran a worldwide network of hardware random-number generators and reports
that its output departed from chance during 500 formally registered world events between 1998 and 2015, with a
combined score of 7.31 standard deviations. Question #47 tested the claim on later events chosen by rule and
found nothing. It did not re-examine the original result.

**From the project's public raw data, do the published scores of its formal events reproduce, and do the same
windows a week away, taken as controls, come out at chance?**

## Why it matters

A result of 7.31 either is in the public data or is not. If it is, and matched control windows show nothing,
then the excess is tied to the times the project registered, and what remains in dispute is how those times were
chosen. If the control windows show the same excess, the cause is the devices or the method. If the scores do
not reproduce, the published table does not follow from the public data by the published recipe. Each outcome
moves the question, and #47's null result reads differently under each.

What the project states, read on its website on 2026-11-23 (copies of the first two pages are in `sources/`):

- Results (<https://global-mind.org/results.html>): "Rigorously Defined Events … 500 … Stouffer Z 7.310". "Basic
  statistical evaluations are based on theoretical expectations, while more precise analyses use an empirical
  estimate of variance for each egg, calculated from its full database of trials. We exclude all bad data
  identified by standardized rules (e.g., trial scores outside the range 55 to 145 are considered to be
  errors)." The devices are called eggs.
- Registry (<https://global-mind.org/pred_formal.html>): each formal event has a begin and end time (UTC), a
  resolution and a recipe. "By convention the period includes the second that begins at the begin time, up to
  the last second prior to the end time." "For unexpected events like earthquakes and terror attacks, we
  typically identify a period beginning half an hour to an hour before the moment of occurrence, followed by
  several hours".
- The standard analysis (<https://global-mind.org/analysis_chi.html>): "The 200-bit trial sums have expected
  mean = 100 and standard deviation = 7.071 … A composite (Stouffer) Z-score across Eggs is computed for each
  second or block of time … This is squared, yielding a Chisquare-distributed quantity with one degree of
  freedom … Since Chisquares are additive, we may sum across seconds or across blocks of time … The total
  Chisquare represents the deviation for the predicted period of time". The Stouffer Z is "Zs = Sum(Zi)/Sqrt(i)".
  The same page says "The earliest analyses used a summation of Z2 across eggs, a different algorithm".

We have not read the published critiques or defences for this plan. The audit stands on the project's own
recipe and tables.

## Data and sources

| Short name | What | Source |
|---|---|---|
| Registry | The formal events, with windows, resolution and recipe (512 rows) | <https://global-mind.org/pred_formal.html>, saved as `sources/pred_formal.html` |
| Published scores | The project's score for each event (513 rows) | <https://global-mind.org/results.html>, saved as `sources/results.html` |
| Day files | One file per UTC day: for every second, each egg's sum of 200 random bits | <https://global-mind.org/data/eggsummary/YYYY/basketdata-YYYY-MM-DD.csv.gz> |

`analysis/build_registry.py` turns the two saved pages into `sources/registry.tsv`, `sources/published.tsv` and
`sources/matched.tsv` (registry rows joined to published rows by event number). The archive's directory listings
for 1998 to 2016, read on 2026-11-23, are reduced to `sources/available_days.txt` (6,696 days, from 1998-08-05).
Hashes are in `MANIFEST.md`. The licence of the GCP data is not stated on the pages read; the project invites
public use.

**A check on the tables, done before any network data was read.** Leaving out the 13 published rows the project
marks with an asterisk gives 500 events whose published scores combine to 7.312, against the 7.310 the page
states. So the published table is the source of the headline number, and the 13 marked rows are exactly the 13
registry rows whose Include column says No.

**What has been seen.** The two tables. In question #47, six formal events of 2011–2015 (full UTC days:
2011-04-22, 2011-09-21, 2013-03-08, 2014-02-14, 2015-12-03, 2015-12-12) were scored to validate that program,
with theoretical standardising; its scores came within 0.4 of the published ones (0.29 against 0.28; 3.24
against 3.14; 0.74 against 0.94; −0.28 against −0.58; −0.49 against −0.12; 1.013 against 1.013). Five of those
six are in this audit's test; the registry lists the sixth, 2015-12-03, with a date nine days from its
published one, so the rules below leave it out. No other day file of 1998–2015 has been parsed. The day files
this audit needs were downloaded before the lock and checked only for length and for decompressing to the end.

## Method

### The events

A registry row is **in the test** if all of these hold. Every condition is read from the two tables alone.

1. Its Include entry begins "Yes" (499 of 512 rows).
2. Its Recipe is exactly "Stouffer Z Meanshift" or "Stouffer Z", its Statistic is exactly "Chisquare 600 df
   weight", and its Resolution is exactly "1-sec". This is the project's standard analysis at one-second
   resolution, as far as the registry's labels say. It leaves out the early "Sum Variance" events at 15-minute
   resolution (the superseded algorithm), the New Year analyses, which average over time zones, and a few events
   with special recipes. What "600 df weight" means is not explained on the pages read; 493 of the 512 rows
   carry it. `unverified`.
3. Its begin and end times parse as single times, the end is not before the begin, and the window is at most 7
   days.
4. A published row has the same event number, its score is a number, and the registry's begin date and the
   published date are the same or one day apart. (Twelve rows disagree by more, up to four years; four rows near
   number 345 are numbered differently on the two pages. All are left out and not guessed at.)
5. Every UTC day the window touches has a day file.
6. It has a control window (below).

**The window** is every second from the begin time to the end time, both included: `end − begin + 1` seconds.
The registry writes end times as the last second of the window ("the first hour begins with 00:00:00 and ends
with 00:59:59"), and nearly all its entries end in `:59`, so that the first row, 07:15:00 to 10:14:59, is exactly three
hours.

`analysis/build_windows.py` applies these rules and writes `windows.tsv`, with the reason for every row left
out. **396 events are in the test.** Their published scores sum to 132.613, a mean of 0.335 per event, and
combine among themselves to 6.664. Of the published 7.31 over 500 events they supply 132.613/√500 = 5.93; the
other 104 published events supply the rest and are not audited here. Windows run from 60 seconds to 34 hours,
with a median of 6 hours; 30 are under an hour. By year: 1 (1999), 15, 22, 23, 33, 26, 18, 16, 21, 22, 32, 30,
40, 31, 33, 18, 15 (2015). There is none from 1998, when the superseded recipe was in use. Reasons for the 116
registry rows left out (a row can have several): not the standard recipe 91; not one-second resolution 58; times
do not parse 16; dates disagree or no match 16; not included by the project 13; no published score 4; longer
than 7 days 3; no data file 2; end before begin 1.

Windows in the test may overlap one another. Each is scored as registered, and all are combined, as the project
does. The same results are also given for the events that do not overlap an earlier event in the test.

### The control windows

For each event in the test, in registry order: the same window shifted by −7 days; failing that +7, −14, +14,
−21, +21, −28, +28 days. A shift fails if a UTC day the shifted window touches has no day file, or if the
shifted window overlaps a *blocked stretch* or a control window already assigned.

The blocked stretches (`sources/blocked.tsv`, 529 of them) are every stretch of time that any event occupies or
may occupy, whether or not it is in the test: the window of every registry row whose times parse; for the 16
rows whose times do not parse, the whole UTC days from the first to the last date written in the row if those
are at most 7 days apart, and otherwise each date written; for the rows whose registry and published dates
disagree, the published date and the day after as well; and the days 2010-10-13 to 2010-10-14 and 2015-09-21 to
2015-09-22, for the two events that are in the published table and not in the registry.

Controls used: 362 at −7 days, 28 at +7, 4 at −14, 2 at +14. A shift of whole weeks keeps the time of day and
the day of the week. Most controls are earlier than their events; results are also given separately for the
pairs whose control is earlier and those whose control is later.

### The data

A day file is comma-separated. Exactly one line begins `12,` and gives the egg numbers in fields four onward,
with no number repeated; anything else stops the program. Lines beginning `13,` give one second each: field two
is the Unix time, which must fall in that UTC day, and fields four onward are the trial sums in the order of the
egg numbers, empty where an egg did not report. Other lines are ignored. If a second appears twice, the later
line stands for the fields it fills. A window is the given number of Unix seconds from its begin time; a second
absent from the files has no data.

**Cleaning.**

1. A trial sum that differs from 100 by 45 or more is removed. (The project gives this rule twice, once as
   "deviate by 45 or more" and once as "outside the range 55 to 145"; they differ at exactly 55 and 145. We use
   the first, as in #47.)
2. *The egg check, standing in for the project's unpublished stability criteria.* For a set of `n` cleaned
   trials of one egg: the egg fails if `|mean − 100| / (7.0711/√n) > 5`, or
   `|mean((x − 100)²)/50 − 1| × √(n/2) > 5`. The project says device variances are off by "about 1 part in
   10,000" and at most about 0.25%; over a whole day this check allows about 2.4%, so it removes broken devices
   and not ordinary ones. It is applied in two places: to an egg's trials in the window being scored, where the
   egg must also have `n ≥ L/2` for a window of `L` seconds; and to an egg's trials on each day of a reference
   pool (below).

### The statistic

For an event and its control, a **pair**:

- **The pair's reference pool.** The control windows of all events in the test that begin within 183 days of
  this event (before or after) touch a set of UTC days. Leave out the days that this pair's own control window
  touches. On each remaining day, take every second that is not inside a blocked stretch. For each egg and day,
  the egg's cleaned trials in those seconds are used if there are at least 3,600 of them and they pass the egg
  check; each day counts once. An egg's pool is the union over days. The event and its control use the same
  pool, and neither window's own seconds are in it.
- **Standardising.** An egg's trial `x` becomes `z = (x − 100)/s`, where `s²` is the mean of `(x − 100)²` over
  the egg's pool (the variance plus the square of any offset of the mean). An egg with fewer than 86,400 trials
  in the pool is not used in either window of the pair. The project says it standardises each egg by an
  empirical variance "calculated from its full database of trials"; this is the same idea on about a year of
  ordinary days around the event.
- **Eggs used in a window:** those with enough pool that pass the egg check in that window.
- **Each second.** With `N ≥ 1` such eggs reporting that second: `Z = Σ z / √N`.
- **The window.** `χ² = Σ Z²` over the seconds used, with `df` their number. The window is *not evaluable* if
  fewer than 2 eggs are used, or `df < 0.8 × L`, or `df < 2`.
- **The window's score** is the normal equivalent of `χ²` by the Wilson–Hilferty formula:
  `Z_window = ((χ²/df)^(1/3) − (1 − 2/(9·df))) / √(2/(9·df))`. Against the exact conversion its error is below
  0.002 for df of 600 or more out to four standard deviations, and it stays finite in the far lower tail, where
  the exact conversion in double precision does not. The smallest window in the test has 60 seconds. A positive
  score means the composite's mean square is above what chance typically gives, the direction the project
  reports.

**Combined score.** `Z_all = Σ Z_window / √n` over `n` windows. Correlations are Pearson's; standard deviations
divide by `n − 1`; pairs are taken in registry order.

### What is reported, and the labels fixed in advance

**1. Do the published scores reproduce?** Over the evaluable events, our score against the published score: the
correlation `r`; the slope of ours on published; the mean and the median absolute difference; the share within
0.25 and within 0.5; and the two combined scores.

| Label | Condition |
|---|---|
| **Reproduces closely** | `r ≥ 0.9` and median absolute difference ≤ 0.25 |
| **Reproduces roughly** | otherwise, `r ≥ 0.7` and median absolute difference ≤ 0.5 |
| **Does not reproduce** | otherwise |

The label is given twice: for our main scores, and for the scores with theoretical standardising (item 1
below), since the project's table may have been built with either. Exact agreement is not expected: the
project's masking of faulty devices and its standardising are not published in full. "Does not reproduce" would
be a statement about this reconstruction; it would not show that the project's table cannot be derived from the
raw files by the project's own program.

**2 to 4, on the pairs in which both windows are evaluable.**

- *Events.* Their combined score against the standard normal, one-sided: **departure** if `Z ≥ 3.09`;
  **suggestive** if `1.645 ≤ Z < 3.09`; otherwise **no positive excess detected**.
- *Controls.* **Calibration failure detected** if the controls' combined score has an absolute value of 2.58 or
  more, or the standard deviation of their scores lies outside 0.85 to 1.2. Otherwise **no calibration failure
  detected**, which is weaker than saying the controls are at chance; their mean and its interval are given.
- *Events against their own controls.* The event's score minus the control's, pair by pair: the mean, its
  standard error, and a one-sided p from 200,000 random sign flips (`numpy.random.default_rng(74)`, in 20
  batches of 10,000, each an array of signs drawn by `integers(0, 2, (10000, pairs)) * 2 − 1`; p is
  `(hits + 1)/200,001`, where a hit is a flipped sum at least the observed sum). The p-value is right if, under
  chance, swapping which window of a pair is called the event leaves the distribution of the scores unchanged.
  An event and its control are scored with the same pool and the same rules, which is what that needs; it is
  still a nominal value, because pairs share pools and some events overlap.

**Overall**, the first of these that applies:

| Label | Condition |
|---|---|
| **Insufficient coverage** | fewer than 300 pairs with both windows evaluable |
| **No excess found** | events' combined score < 1.645 |
| **The excess is in the event windows** | events "departure", paired p ≤ 0.01, and no calibration failure detected |
| **The excess is not specific to the events** | controls' combined score ≥ 2.58 and paired p > 0.05 |
| **Mixed** | anything else; reported with the numbers and no further label |

The combined scores are descriptive in the project's own form. Their p-values are nominal: they assume the
chi-square holds after standardising and that windows are independent.

### Reported alongside, not part of the labels

1. **Theoretical standardising** (`s = 7.0711` for every egg), for events and controls, with the same eggs. The
   project says uncorrected device variances push the statistic upward; the controls under this recipe show by
   how much.
2. **Without the mean and variance parts of the egg check** in the scored window (every egg with `n ≥ L/2` and
   enough pool is used), for events and controls. The check looks at the very data being scored, so this shows
   how much it matters.
3. **The cross-egg part.** `Z²` splits into each egg's own squares and the products of pairs of eggs. The second
   part, `Σ over seconds with N ≥ 2 of [Z² − (Σ z²)/N]`, divided by `√(Σ over those seconds of 2(N − 1)/N)`,
   measures eggs moving together; one egg's excess variance does not move its expected value. Combined across
   windows like the main score, for events and for controls. (A reviewer says the project's later papers make
   this pair correlation their central claim. Those papers were not read.)
4. Everything above for: events that do not overlap an earlier event in the test; pairs with the control
   earlier, and later; the test without the five events already scored in #47; each year; and each window
   length (under 1 hour; 1 to 6 hours; over 6 hours and under a day; a day or more).
5. Each window's scores, degrees of freedom, eggs used and seen, the median number of eggs per second, and the
   number of days in its pool (`results/windows.tsv`).
6. The events and controls that were not evaluable, by number.

### Checks on the program, before the lock

- **Unit tests on made-up data** (`analysis/test_audit.py`, written by a sub-agent from a description of the
  program): cleaning; windows across days; the egg check; pure noise gives scores that look standard normal at
  window lengths of 60 s, 600 s and 6 hours (means within 0.02 of zero, standard deviations within 0.005 of
  one); a shared wobble gives a large score; evaluability; the cross-egg part; the pool, its blocked stretches
  and its egg-day rule; pooled standardising is unbiased where theoretical standardising is biased; the
  Wilson–Hilferty formula against exact values; the sign-flip test; the agreement measures and every label.
- **Against the project's own numbers:** the six events scored in #47, listed above. Nothing further was scored
  for this plan.

### Replication

A model from another vendor writes its own program from this protocol, `windows.tsv`, `sources/blocked.tsv` and
the format notes (`replication/FORMAT.md`). Its per-window scores and combined scores are compared with ours.
Scores are compared to within 0.01. Both programs start from the same `windows.tsv`, so the replication checks
the scoring and not the reading of the project's tables.

## What would count

- **For the project's reported result being in the public data and tied to its event windows:** "reproduces"
  (closely or roughly, under either standardising) together with "the excess is in the event windows".
- **For an artefact of the devices or the method:** "the excess is not specific to the events", or a
  calibration failure together with a paired difference whose interval includes zero.
- **Against this reconstruction matching the published table:** "does not reproduce" under both standardisings,
  or "no excess found".
- **Mixed** and **insufficient coverage** are reported as they are.

None of these says whether minds affect random-number generators. If the excess is in the event windows, the
audit still cannot say how the events and their windows were chosen: by the project's account, before the data
were examined, by judgement, and for sudden events after they happened. A real excess produced by choosing
windows after seeing data would look the same here. The two saved web pages are not a time-stamped record of
when each event was registered. A test on events fixed by rule, such as #47, is one way to address that.

## Known weaknesses

- **Not the project's exact pipeline.** The statistic is the project's. The egg check and the way variances are
  measured are ours, because the project's are not published in full, and we do not know which standardising its
  table used for which events. Differences of a few tenths per event are expected.
- **104 of the 500 published events are not audited,** among them all of 1998, every New Year analysis and every
  event with a non-standard recipe.
- **No placebo calendar.** A stronger calibration would score made-up "events" on ordinary days with the whole
  procedure. Both reviewers asked for it. It needs several hundred more day files and was left out for time; the
  396 controls are the calibration there is.
- **Controls are one week away, and mostly earlier.** A device that misbehaves for weeks would affect both
  windows. A steady drift in the network over a week could shift the paired difference slightly; the earlier
  and later controls are reported separately so that this can be seen.
- **The egg check looks at the window being scored.** It could remove a genuinely unusual egg. Results without
  it are reported.
- **Controls help set one another's scales,** since pools are built from control days. A pair's own control days
  are never in its pool.
- **Very short windows** have few degrees of freedom, and the egg check has little power in them. Under pure
  noise the scores are still close to standard normal at 60 seconds (unit tests).
- **Overlapping event windows** are scored separately, as the project does; the non-overlapping subset is
  reported.
- **Selection after the fact** cannot be seen from here, as said above.
- **The literature was not read.** In particular Bancel and Nelson's papers on the project's analysis, which the
  reviewers cite, might settle which standardising the published table used.
- **One session** designs, runs and writes up the question, and the same model wrote #47. Sub-agents of the
  same vendor parsed the tables, wrote the unit tests and adapted the review and replication scripts. The
  outside check is the review before the lock and the replication after it.

## Review before the lock

Two rounds by OpenAI `gpt-6.2-astra` and Google `gemini-4-neon`; the reviews are in `review/`, and
`review/README.md` lists what was changed and what was not.

## Budget

$10. Expected spend under $5: design review by two other vendors' models, and replication.
