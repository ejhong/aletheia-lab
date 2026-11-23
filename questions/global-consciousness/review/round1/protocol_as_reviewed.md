# Did random-number generators twitch at world events?

Issue #47 · Lane: data · Written 2026-11-23 by Claude Fable 5.2 (Anthropic), directed by Eugene

## Question

The Global Consciousness Project (GCP) has run a worldwide network of hardware random-number generators since
1998. It reports that the network's output departed from chance during events that engaged many people at once:
over 500 events fixed in advance, a combined score of 7.31 standard deviations. That formal series ended in
December 2015. The network kept running and its data stayed public.

**On events after the formal series ended, chosen by a mechanical rule and analysed by the project's own
standard recipe, does the network depart from chance?**

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
file from 2001. No data from 2016 onward has been parsed. One 2016 file was fetched to time the server and
deleted unread.

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

**Control windows.** For each event, the same 24 hours 7 days earlier. If that has no data file, or lies within
24 hours of any event window in the list, then 7 days later, then 14 days earlier, then 14 days later.

**In the test.** An event is in the test if it lies between 2016-01-01 and 2025-10-31, every UTC day its window
touches has a data file, and a control window is found. `analysis/build_events.py` applies these rules to the
files in `sources/` and writes `events.tsv`: 65 candidates, of which 58 are in the test (37 calendar days, 21
earthquakes; 7 have no data). The list was built without reading any network data.

### The data

A day file is comma-separated. Lines beginning `12,` give the egg numbers: fields four onward. Lines beginning
`13,` give one second each: field two is the Unix time, fields four onward the trial sums in the order of the
egg numbers, empty where an egg did not report. Other lines are ignored. A window's seconds are the 86,400 Unix
times from its start; a second absent from the files has no data.

**Cleaning.**

1. A trial sum that differs from 100 by 45 or more is removed (the project's rule).
2. *Egg check, standing in for the project's unpublished stability criteria.* For an egg in a window, with `n`
   trials left: the egg is dropped from the event if `n < 43,200`, or `|mean − 100| / (7.0711/√n) > 5`, or
   `|mean((x − 100)²)/50 − 1| × √(n/2) > 5`, in either the event window or its control window.

### The statistic

For an event, with the eggs that pass:

- **Standardising.** In the event window an egg's trial `x` becomes `z = (x − 100)/s`, where `s` is the root
  mean square of `(x − 100)` over that egg's trials in the *control* window. In the control window `s` comes
  from the *event* window. So each window is standardised by variances measured outside it, which corrects the
  devices' small variance biases without using a window's own data.
- **Each second.** With `N` eggs reporting that second, `N ≥ 5`: `Z = Σ z / √N`. Seconds with fewer than 5 eggs
  are not used.
- **The window.** `χ² = Σ Z²` over the seconds used, with `df` their number. If `df < 43,200` the event is *not
  evaluable* and is left out, with its control, and named.
- **The event's score** is the normal equivalent of `χ²` by the Wilson–Hilferty formula:
  `Z_event = ((χ²/df)^(1/3) − (1 − 2/(9·df))) / √(2/(9·df))`. Positive means more variance in the network's
  composite than chance gives, which is the direction the project reports.

The same is computed for every control window.

**Combined score.** `Z_all = Σ Z_event / √n` over the `n` evaluable events. Likewise for the controls.

### Decision rules

**Did the network depart from chance?** One-sided, in the project's direction.

| Verdict | Condition |
|---|---|
| **Departure** | `Z_all ≥ 3.09` (one-sided p ≤ 0.001) |
| **Suggestive** | `1.645 ≤ Z_all < 3.09` |
| **No departure** | `Z_all < 1.645` |

**Is the result compatible with the size the project reports?** The project's formal mean is 0.33 per event, so
`n` events predict a combined score of `0.33 × √n` (2.5 for 58). The sampling error of `Z_all` is 1.

| Verdict | Condition |
|---|---|
| **Smaller than reported** | `Z_all ≤ 0.33 × √n − 1.645` |
| **Compatible with the reported size** | otherwise |

The two verdicts are reported together. "No departure" with "compatible" would mean the test could not tell.

**Calibration.** The controls' combined score should look like chance. If its absolute value is 2.58 or more,
the verdicts are instead taken from the difference, `(Σ Z_event − Σ Z_control) / √(2n)`, with the same
thresholds, and the result says so.

### Reported alongside, not part of the rules

1. Each class by itself: calendar days, earthquakes.
2. Each event's score, its control's, the number of eggs and seconds used.
3. The difference score, whatever the calibration shows.
4. The same with theoretical standardising (`s = 7.0711` for every egg), the recipe as the project first
   described it.
5. Earthquakes with 1,000 or more deaths, as a subset.
6. For context, from the project's published table: its own scores for these four calendar days (19 events) and
   for earthquakes (29 events) in 1998–2015.

### Checks on the program, before the lock

- Unit tests on made-up data: reading a made-up day file; pure noise gives scores that look standard normal over
  many made-up windows; a planted common signal across eggs gives a large positive score; an egg with inflated
  variance in both windows is corrected by the standardising; an egg that fails the check is dropped; a window
  spanning two days is assembled correctly.
- A **control-only run** (`--controls`): every control window scored with theoretical standardising, reading
  only the control days' files. It exercises the reader and the statistic on real files without touching an
  event window.

### Replication

A model from another vendor writes its own program from this protocol, `events.tsv` and the format notes. Its
per-event scores and combined scores are compared with ours.

## What would count

- **For the project's claim:** "departure". A combined score of 3.09 or more on fresh events fixed by rule.
- **Weakly for:** "suggestive".
- **Against, at the reported size:** "no departure" together with "smaller than reported".
- **Uninformative:** "no departure" together with "compatible".

A departure here would not say what causes it. A null would not show that no effect of any size exists.

## Known weaknesses

- **The events are ours, not the project's.** Its experimenters chose events as they happened, by judgement.
  Mechanical rules may pick days that would not have moved them. The two classes were chosen because the project
  used them repeatedly and its published scores for them (means of 0.42 and 0.51 per event) are above its
  overall mean.
- **Calendar days are a mixed bag.** The registry attached them to particular observances (Earth Day, the
  International Day of Peace, meditations on Valentine's Day, Women's Day). Whether those were held in later
  years with the same force we do not know.
- **Small earthquakes by world standards.** A hundred deaths in a remote region may hold little of the world's
  attention. The 1,000-death subset is reported.
- **The egg check is ours.** The project's criteria for masking unstable devices are not published in full. Ours
  is applied the same way to event and control windows.
- **Standardising from one control window is noisy:** each egg's variance is known to about half a percent. This
  adds a little noise to every score, in both directions, and none on average.
- **The network after 2015** has fewer eggs and more gaps than in its prime, and seven events fall in gaps.
- **Power.** At the project's reported mean, 58 events predict a combined score of 2.5: a "departure" would then
  be reached about 28% of the time, "suggestive" or better about 80%, and "smaller than reported" would be
  wrongly declared 5% of the time.
- **One session** proposed, designed, runs and writes up the question.

## Budget

$20. Expected spend under $4: design review by two other vendors' models, and replication.
