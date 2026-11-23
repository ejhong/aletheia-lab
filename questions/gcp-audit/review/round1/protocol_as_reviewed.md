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
   resolution. It leaves out the early "Sum Variance" events at 15-minute resolution (the superseded algorithm),
   the New Year analyses, which average over time zones, and a few events with special recipes.
3. Its begin and end times parse as single times, the end is not before the begin, and the window (end − begin
   + 1 seconds) is at most 7 days.
4. A published row has the same event number, its score is a number, and the registry's begin date and the
   published date are the same or one day apart. (Twelve rows disagree by more, up to four years, which are
   typing errors in one page or the other; four rows near number 345 are numbered differently on the two pages.
   All are left out and not guessed at.)
5. Every UTC day the window touches has a day file.
6. It has a control window (below).

`analysis/build_windows.py` applies these rules and writes `windows.tsv`, with the reason for every row left
out. **396 events are in the test.** Their published scores sum to 132.613 and combine to 6.664 (mean 0.335 per
event), so they carry most of the published 7.31. Their windows run from 60 seconds to 34 hours, with a median
of 6 hours. By year: 1 (1999), 15, 22, 23, 33, 26, 18, 16, 21, 22, 32, 30, 40, 31, 33, 18, 15 (2015). There is
none from 1998, when the superseded recipe was in use. Reasons for the 116 left out (a row can have several):
not the standard recipe 91; not one-second resolution 58; times do not parse 16; dates disagree or no match 16;
not included by the project 13; no published score 4; longer than 7 days 3; no data file 2; end before begin 1.

Windows in the test may overlap one another (the registry has a few overlapping pairs). Each is scored as
registered, and all are combined, as the project does.

### The control windows

For each event in the test, in registry order: the same window shifted by −7 days; failing that +7, −14, +14,
−21, +21, −28, +28 days. A shift fails if a UTC day the shifted window touches has no day file, or if the
shifted window overlaps a *blocked stretch* or a control window already assigned. An event with no control is
left out (none was).

The blocked stretches (`sources/blocked.tsv`, 518 of them) are every stretch of time that any event occupies,
whether or not it is in the test: the window of every registry row whose times parse; for the 16 rows whose
times do not parse, the whole UTC days from the first to the last date written in the row if those are at most
7 days apart, and otherwise each date written; and the two days 2010-10-13 to 2010-10-14 and 2015-09-21 to
2015-09-22, for the two events that are in the published table and not in the registry.

Controls used: 363 at −7 days, 28 at +7, 3 at −14, 2 at +14. A shift of whole weeks keeps the time of day and
the day of the week.

### The data

A day file is comma-separated. Exactly one line begins `12,` and gives the egg numbers in fields four onward,
with no number repeated; anything else stops the program. Lines beginning `13,` give one second each: field two
is the Unix time, which must fall in that UTC day, and fields four onward are the trial sums in the order of the
egg numbers, empty where an egg did not report. Other lines are ignored. If a second appears twice, the later
line stands. A window is the given number of Unix seconds from its begin time; a second absent from the files
has no data.

**Cleaning.**

1. A trial sum that differs from 100 by 45 or more is removed (the project's rule).
2. *Egg check, standing in for the project's unpublished stability criteria.* For an egg in the window being
   scored, of `L` seconds, with `n` trials left there: the egg is not used in that window if `n < L/2`, or
   `|mean − 100| / (7.0711/√n) > 5`, or `|mean((x − 100)²)/50 − 1| × √(n/2) > 5`.

### The statistic

For a window, with the eggs that pass:

- **Standardising.** An egg's trial `x` becomes `z = (x − 100)/s`. `s²` is the mean of `(x − 100)²` over that
  egg's cleaned trials in the *reference pool* of the event's year (the year of the event's begin time; a control
  belongs to its event's year). The pool is every second of every UTC day touched by a control window of that
  year's events, except seconds inside a blocked stretch, and, when the window being scored is itself a control,
  except that window's own seconds. An egg with fewer than 86,400 trials in the pool is not used. (`s²` is the
  mean square about 100: the variance plus the square of any offset of the mean.) The project says it
  standardises each egg by an empirical variance "calculated from its full database of trials"; this is the
  same idea with a year of ordinary days outside every event.
- **Each second.** With `N ≥ 1` usable eggs reporting that second: `Z = Σ z / √N`.
- **The window.** `χ² = Σ Z²` over the seconds used, with `df` their number. The window is *not evaluable* if
  fewer than 2 eggs are usable, or `df < 0.8 × L`, or `df < 2`.
- **The window's score** is the normal equivalent of `χ²` by the Wilson–Hilferty formula:
  `Z_window = ((χ²/df)^(1/3) − (1 − 2/(9·df))) / √(2/(9·df))`. It agrees with the exact chi-square conversion to
  within 0.002 for the cases tried (df of 2, 12, 600, 86,400), and unlike the exact conversion it stays finite in
  the far lower tail. A positive score means the composite's mean square is above what chance typically gives,
  which is the direction the project reports.

Every event window and every control window is scored this way.

**Combined score.** `Z_all = Σ Z_window / √n` over the `n` evaluable events; the same over the evaluable
controls.

### What is reported, and the labels fixed in advance

**1. Do the published scores reproduce?** Over the evaluable events: the correlation `r` between our score and
the published score; the median absolute difference; the share within 0.25 and within 0.5; our combined score
and the combined published score for the same events.

| Label | Condition |
|---|---|
| **Reproduces closely** | `r ≥ 0.9` and the two combined scores differ by at most 1.0 |
| **Reproduces roughly** | otherwise, `r ≥ 0.7` and the combined scores differ by at most 2.0 |
| **Does not reproduce** | otherwise |

Exact agreement is not expected: the project's masking of faulty devices and its standardising are not published
in full.

**2. Is there an excess in the event windows?** Our combined score of the events against the standard normal,
one-sided: **departure** if `Z_all ≥ 3.09`; **suggestive** if `1.645 ≤ Z_all < 3.09`; otherwise **no positive
excess detected**.

**3. Do the controls look like chance?** **Calibration in doubt** if the controls' combined score has an
absolute value of 2.58 or more, or the standard deviation of their scores lies outside 0.75 to 1.3. Otherwise
**controls look like chance**.

**4. Events against their own controls.** For every event whose control is also evaluable, the event's score
minus the control's. The mean difference, with a one-sided p from 200,000 random sign flips
(`numpy.random.default_rng(74)`, in 20 batches of 10,000, each an array of signs drawn by
`integers(0, 2, (10000, pairs)) * 2 − 1`; p is `(hits + 1)/200,001`, where a hit is a flipped sum at least the
observed sum). This asks only that the difference be as likely negative as positive under chance.

**Overall**, one of:

| Label | Condition |
|---|---|
| **The excess is in the event windows** | events "departure", paired p ≤ 0.01, and calibration not in doubt |
| **The excess is not specific to the events** | controls' combined score ≥ 2.58 and paired p > 0.05 |
| **No excess found** | events' combined score < 1.645 |
| **Mixed** | anything else; reported with the numbers and no further label |

The p-values are nominal: they assume the chi-square holds after standardising, and windows of one year share
measured egg spreads, which ties their scores together slightly. Some event windows overlap one another.

### Reported alongside, not part of the labels

1. **Theoretical standardising** (`s = 7.0711` for every egg), for events and controls. The project says
   uncorrected device variances push the statistic upward; the controls under this recipe show by how much.
2. **The cross-egg part.** `Z²` splits into each egg's own squares and the products of pairs of eggs. The second
   part, `Σ over seconds with N ≥ 2 of [Z² − (Σ z²)/N]`, divided by `√(Σ over those seconds of 2(N − 1)/N)`,
   measures eggs moving together; one egg's excess variance does not move its expected value. Combined across
   windows like the main score, for events and for controls.
3. Everything in 1 to 4 above by year of the event, and by window length (under 1 hour; 1 to 6 hours; over 6
   hours and under a day; a day or more).
4. Each window's scores, degrees of freedom and eggs used and seen (`results/windows.tsv`).
5. The events and controls that were not evaluable, by number.

### Checks on the program, before the lock

- **Unit tests on made-up data** (`analysis/test_audit.py`, written by a sub-agent from the description of the
  program): cleaning; windows across days; the egg check; pure noise gives scores that look standard normal at
  window lengths of 60 s, 600 s and 6 hours; a shared wobble gives a large score; evaluability; the cross-egg
  part; the pool and its blocked stretches; pooled standardising is unbiased where theoretical standardising is
  biased; the Wilson–Hilferty formula against exact values; the sign-flip test; the labels.
- **Against the project's own numbers:** the six events scored in #47, listed above. Nothing further was scored
  for this plan.

### Replication

A model from another vendor writes its own program from this protocol, `windows.tsv`, `sources/blocked.tsv` and
the format notes (`replication/FORMAT.md`). Its per-window scores and combined scores are compared with ours.
Scores are compared to within 0.01.

## What would count

- **For the project's reported result being in the public data and tied to its event windows:** "reproduces"
  (closely or roughly) together with "the excess is in the event windows".
- **For an artefact of the devices or the method:** "the excess is not specific to the events", or "calibration
  in doubt" with a paired difference near zero.
- **Against the published table following from the public data:** "does not reproduce" or "no excess found".
- **Mixed** outcomes are reported as they are.

None of these says whether minds affect random-number generators. If the excess is in the event windows, the
audit still cannot say how the events and their windows were chosen: by the project's account, before the data
were examined, by judgement, and for sudden events after they happened. A real excess produced by choosing
windows after seeing data would look the same here. That question is addressed only by tests on events chosen by
rule, such as #47.

## Known weaknesses

- **Not the project's exact pipeline.** The statistic is the project's. The egg check and the way variances are
  measured are ours, because the project's are not published in full. Differences of a few tenths per event are
  expected.
- **116 of 512 registry rows are left out by rule,** among them all of 1998, every New Year analysis and every
  event with a non-standard recipe. The audit says nothing about those. The events in the test carry 6.66 of the
  published 7.31.
- **The controls are one week away.** A device that misbehaves for weeks would affect both; that is what the egg
  check and the comparison of controls with chance are for. A slow change in the network between event and
  control (new eggs, failing eggs) adds noise to the paired difference and should not bias it.
- **Very short windows.** A 60-second window has 60 degrees of freedom, and the egg check has little power in
  it. Scores are still close to normal there (the unit tests report how close), and such windows are few: 30 of the 396
  events in the test are under an hour.
- **Overlapping event windows** are scored separately, as the project does; their scores are not independent.
- **Selection after the fact** cannot be seen from here, as said above.
- **The main labels trust the chi-square.** The controls and the paired check are there to show whether that
  holds.
- **One session** designs, runs and writes up the question, and the same model wrote #47. Sub-agents of the
  same vendor parsed the tables and wrote the unit tests. The outside check is the review before the lock and the
  replication after it.

## Budget

$10. Expected spend under $5: design review by two other vendors' models, and replication.
