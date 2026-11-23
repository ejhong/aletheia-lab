# Did random-number generators twitch at world events?

Issue #47 · Lane: data · Written 2026-11-23 by Claude Fable 5.2 (Anthropic), directed by Eugene

## Question

The Global Consciousness Project (GCP) has run a worldwide network of hardware random-number generators since
1998. It reports that the network's output departed from chance during events that engaged many people at once:
across 500 events specified before their data were examined, a combined score of 7.31 standard deviations. That formal series ended in
December 2015. The network kept running and its data stayed public.

**On events after the formal series ended, chosen by a mechanical rule and scored with the project's standard
statistic, does the network depart from chance?**

## Why it matters

The dispute over the project's result is about freedom of choice: which events, which time window, which
statistic. Here all three are fixed before the data for the events are opened, the events come from rules with
no judgement in them, and the years tested are ones the project's formal series never used. A clear departure
would be an out-of-sample confirmation of a very large claim. A null on a test with enough power would say that
the effect, at the size reported, did not continue.

What the project states, read on its website on 2026-11-23:

- The formal result: "Rigorously Defined Events … 500 … Stouffer Z 7.310", probability 1.3 × 10⁻¹³
  (<https://global-mind.org/results.html>). That is a mean of 0.33 per event.
- The standard analysis (<https://global-mind.org/analysis_chi.html>): "The 200-bit trial sums have expected
  mean = 100 and standard deviation = 7.071 … A composite (Stouffer) Z-score across Eggs is computed for each
  second … This is squared, yielding a Chisquare-distributed quantity with one degree of freedom … we may sum
  across seconds … The total Chisquare represents the deviation for the predicted period of time". The Stouffer Z
  is "Zs = Sum(Zi)/Sqrt(i)". The devices are called eggs.
- Cleaning (<https://global-mind.org/gcpdata.html>): "All trialsums that deviate by 45 or more from the
  theoretical mean of 100 are removed"; "Sections of reg data that do not pass stability criteria are masked",
  by criteria that are not published in full; and trial variances, which are biased by "about 1 part in 10,000"
  and up to about 0.25% for some devices, "are corrected by standardization of the trialsums".
- Event choice (<https://global-mind.org/pred_formal.html>): "events that repeat, such as New Years, Kumbh Mela,
  or Earth Day, are registered with the same specifications in each instance".

We have not read the published critiques or defences for this plan. The test stands on the project's own
recipe.

## Data and sources

| Short name | What | Source |
|---|---|---|
| Day files | One file per UTC day: for every second, each egg's sum of 200 random bits | <https://global-mind.org/data/eggsummary/YYYY/basketdata-YYYY-MM-DD.csv.gz> |
| Registry | The project's formal events, 1998–2015, with windows and recipes | <https://global-mind.org/pred_formal.html> |
| Earthquakes | NOAA NCEI Global Significant Earthquake Database, events of 2016–2025 with 100 or more deaths | <https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/earthquakes?minYear=2016&maxYear=2025&minDeaths=100> |

The archive's directory listings on 2026-11-23 hold day files for 3,058 days from 2016-01-01 to 2025-10-31, with
gaps (most of 2024, the ends of 2018, 2021 and 2023). `sources/available_days.txt` lists them. The licence of
the GCP data is not stated on the pages we read; the project invites public use ("data access" pages). The NOAA
database is a US government work.

**What has been seen.** The registry and the project's published results for 1998–2015. The layout of one day
file from 2001, and six day files of 2011–2015 used to validate the program (below). No data from 2016 onward
has been parsed. One 2016 file was fetched to time the server and deleted unread.

## Method

### The events

Two classes, both from rules. Every window is 24 hours, the most common length in the registry (100 of its 421
standard-recipe events).

**Calendar days.** The registry used four calendar days three or more times each as a full UTC day: 14 February
(4 times), 8 March (3), 22 April (6) and 21 September (7). Each of these days in each year from 2016 to 2025 is
an event, from 00:00:00 to 23:59:59 UTC.

**Earthquakes.** Every earthquake in the NOAA database from 2016 to 2025 with 100 or more deaths (25 of them).
The window is the 24 hours starting at the top of the hour of the origin time (an origin at 19:57:27 gives
19:00:00). The registry's later earthquake windows start up to an hour or so before the shock and mostly run 24
hours.

**Overlap.** Two 24-hour windows overlap if their starts are less than 24 hours apart. Taking the candidates in
date order, an event that overlaps an earlier event already kept is left out.

**Control windows.** For each event kept, in date order: the same 24 hours 7 days earlier; failing that, 7 days
later, then 14 days earlier, then 14 days later. A control fails if a UTC day it touches has no data file, or if
it overlaps any candidate event window (kept or not) or any control already assigned. An event with no control
is left out.

**In the test.** An event is in the test if its window lies wholly between 2016-01-01 00:00:00 and 2025-10-31
23:59:59 UTC, every UTC day it touches has a data file, and it has a control. `analysis/build_events.py` applies
these rules to the two files in `sources/` and writes `events.tsv`: 65 candidates, 58 in the test (37 calendar
days, 21 earthquakes); 7 have no data file; none overlap. 52 controls are 7 days earlier and 6 are 7 days later.
No two of the 116 windows overlap. The list was built without reading any network data. The earthquake list is
NOAA's as returned on 2026-11-23, by its `deaths` field, frozen in `sources/`.

### The data

A day file is comma-separated. Exactly one line begins `12,` and gives the egg numbers in fields four onward,
with no number repeated; anything else stops the program. Lines beginning `13,` give one second each: field two
is the Unix time, which must fall in that UTC day, and fields four onward are the trial sums in the order of the
egg numbers, empty where an egg did not report. Other lines are ignored. If a second appears twice, the later
line stands. A window is the 86,400 Unix seconds from its start; a second absent from the files has no data.

**Cleaning.**

1. A trial sum that differs from 100 by 45 or more is removed (the project's rule).
2. *Egg check, standing in for the project's unpublished stability criteria.* For an egg in the window being
   scored, with `n` trials left there: the egg is not used in that window if `n < 43,200`, or
   `|mean − 100| / (7.0711/√n) > 5`, or `|mean((x − 100)²)/50 − 1| × √(n/2) > 5`.

### The statistic

For a window, with the eggs that pass:

- **Standardising.** An egg's trial `x` becomes `z = (x − 100)/s`. `s²` is the mean of `(x − 100)²` over that
  egg's cleaned trials in all the *control windows of the same year* (the year of the event's start; a control
  belongs to its event's year), leaving out the window being scored if it is itself a control. An egg with
  fewer than 86,400 such trials is not used. This follows the project's practice of standardising each device by
  its own measured variance, using only data from outside the event windows.
- **Each second.** With `N` usable eggs reporting that second, `N ≥ 5`: `Z = Σ z / √N`. Seconds with fewer are
  not used.
- **The window.** `χ² = Σ Z²` over the seconds used, with `df` their number. If `df < 69,120` (80% of the day),
  or fewer than 5 eggs are usable, the window is *not evaluable*.
- **The window's score** is the normal equivalent of `χ²` by the Wilson–Hilferty formula:
  `Z_window = ((χ²/df)^(1/3) − (1 − 2/(9·df))) / √(2/(9·df))`. Positive means more variance in the network's
  composite than chance gives, which is the direction the project reports.

Every event window and every control window is scored this way.

**Combined score.** `Z_all = Σ Z_event / √n` over the `n` evaluable events. The same sum over the evaluable
controls gives the controls' combined score.

### Decision rules

One test decides: the combined score of the events against the standard normal, one-sided in the project's
direction. That is the project's own form of inference, and the claim under test is defined by it.

**Is there a positive excess?**

| Verdict | Condition |
|---|---|
| **Departure** | `Z_all ≥ 3.09` (one-sided p ≤ 0.001) |
| **Suggestive** | `1.645 ≤ Z_all < 3.09` |
| **No positive excess detected** | `Z_all < 1.645` |

**How does it compare with a benchmark?** The benchmark is the project's formal mean of 0.33 per event. It is a
yardstick, not a prediction: the formal mean is an average over many kinds of event, window and network size.
`n` events at the benchmark give a combined score of `0.33 × √n` (2.5 for 58).

| Verdict | Condition |
|---|---|
| **Smaller than the benchmark** | `Z_all ≤ 0.33 × √n − 1.645` |
| **Not shown smaller than the benchmark** | otherwise |

Reported with both: the mean score per event with a 95% interval (`± 1.96/√n`).

**Calibration, as a label only.** The controls should look like chance. If their combined score has an absolute
value of 2.58 or more, or the standard deviation of their scores lies outside 0.75 to 1.3, the result carries the
label "calibration in doubt". The label does not change the verdicts; it tells the reader to lean on the paired
check.

### Reported alongside, not part of the rules

1. **The paired check.** For every event whose control is also evaluable, the event's score minus its control's.
   The mean difference, with a one-sided p from 200,000 random sign flips (`numpy.random.default_rng(47)`,
   in 20 batches of 10,000, each an array of signs drawn by `integers(0, 2, (10000, pairs)) * 2 − 1`; p is
   `(hits + 1)/(200,001)` where a hit is a flipped sum at least the observed sum). This needs no assumption
   about the devices, only that an event day and its control day are alike under chance. It has less power:
   at the benchmark, 58 pairs give an expected score of 1.8 where the main test gives 2.5.
2. Each class by itself: calendar days, earthquakes. Earthquakes with 1,000 or more deaths.
3. **Theoretical standardising** (`s = 7.0711` for every egg), the recipe as the project first described it.
4. **The cross-egg part.** `Z²` splits into each egg's own squares and the products of pairs of eggs. The second
   part, `Σ over seconds of [Z² − (Σ z²)/N]`, divided by `√(Σ over seconds of 2(N − 1)/N)`, measures eggs moving
   together and is blind to any one egg's variance. Combined across events like the main score.
5. Each event's scores, its control's, the eggs usable and seen, and the seconds used.
6. For context, from the project's published table: its own scores for these four calendar days (19 of the 20
   registered have a score) and for earthquakes (29 events) in 1998–2015.

### Checks on the program, before the lock

- **Against the project's own numbers.** `analysis/validate.py` scores six of the project's formal full-day
  events of 2011–2015 with theoretical standardising and our egg check. Ours against the published score: 0.29
  and 0.28; 3.24 and 3.14; 0.74 and 0.94; −0.28 and −0.58; −0.49 and −0.12; 1.013 and 1.013. The reader and the
  statistic reproduce the project's results to within about 0.4, the gaps being its unpublished masking and
  standardising. Nothing was tuned to close them.
- **Unit tests on made-up data:** reading a made-up day file; a window across two days; pure noise gives scores
  that look standard normal over many made-up windows; a shared wobble across eggs gives a large score; the egg
  check; the cross-egg part ignores one egg's extra variance; and the whole procedure at one-tenth scale on 30
  made-up events and controls with unequal egg variances, where event and control scores both look standard
  normal and theoretical standardising is visibly biased.

No event or control window of the test has been read.

### Replication

A model from another vendor writes its own program from this protocol, `events.tsv` and the format notes. Its
per-window scores and combined scores are compared with ours. Scores are compared to within 0.01.

## What would count

- **For the project's claim:** "departure": a combined score of 3.09 or more on fresh events fixed by rule.
- **Weakly for:** "suggestive".
- **Against, at the benchmark size:** "no positive excess detected" together with "smaller than the benchmark".
- **Uninformative:** "no positive excess detected" together with "not shown smaller".

A departure here would not say what causes it. A null would not show that no effect of any size exists, and
"no positive excess" does not distinguish a score near zero from a negative one; the score itself is reported.

## Known weaknesses

- **Not an exact replication.** The statistic is the project's. The egg check, the way variances are measured
  and the verdict thresholds are ours, because the project's are not published in full.
- **The events are ours, not the project's.** Its experimenters chose events as they happened, by judgement, and
  for sudden events after the fact (though before looking at the data, by its account). Mechanical rules may
  pick days that would not have moved them. The two classes were chosen because the project used them
  repeatedly and its published scores for them (means of 0.42 and 0.51 per event) are above its overall mean.
- **Calendar days are a mixed bag.** The registry attached them to particular observances (Earth Day, the
  International Day of Peace, meditations on Valentine's Day, Women's Day). Whether those were held in later
  years with the same force we do not know.
- **Small earthquakes by world standards.** A hundred deaths in a remote region may hold little of the world's
  attention, and attention may peak days later than a 24-hour window. The 1,000-death subset is reported.
- **The main test trusts the chi-square.** It assumes that, after standardising, seconds are independent and
  the devices are free of shared faults. The controls and the paired check are there to show whether that holds;
  58 controls can show a gross failure, not a subtle one.
- **Fewer eggs, smaller score?** If the effect is a correlation between pairs of eggs, a network with fewer eggs
  gives a smaller score for the same effect. The network after 2015 is smaller than in its prime, so the
  benchmark may overstate what the claim predicts here. Egg counts are reported.
- **Seven events fall in gaps** in the archive, among them three of the deadliest earthquakes of 2023.
- **Power, at the benchmark and under the test's own assumptions:** 58 events predict a combined score of 2.5.
  "Departure" would be reached about 28% of the time, "suggestive" or better about 80%, and "smaller than the
  benchmark" would be wrongly declared 5% of the time.
- **One session** proposed, designed, runs and writes up the question.

## Budget

$20. Expected spend under $5: design review by two other vendors' models, and replication.
