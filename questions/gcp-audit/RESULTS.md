# Audit the random-number network's original 500 events: results

Issue #74 · Lane: data · Protocol locked 2026-11-23T20:33:03Z (commit `e6cf1f2`) · No amendments

## Answer

**Yes, the published result is in the public data, and it is tied to the event windows. Our scores for 395 of
the project's formal events match its published scores closely. Those events combine to 6.08. The same windows a
week away combine to −0.42, which is what chance gives.**

By the rules fixed in advance:

| Question | Label | The numbers |
|---|---|---|
| Do the published scores reproduce? | **Reproduces closely** (under both ways of standardising) | Correlation 0.96 between our score and the published one; median difference 0.11; 93% of events within 0.5 |
| Is there an excess in the event windows? | **Departure** | Combined score of the 395 events: +6.08. "Departure" needed +3.09 |
| Do the controls look wrong? | **No calibration failure detected** | The 395 matched controls combine to −0.45, with a spread of 0.98 |
| Events against their own controls | | Mean difference +0.33 per pair (95% interval +0.19 to +0.46); events scored higher in 250 of 395 pairs; one-sided p = 5 × 10⁻⁶, the smallest the test can give |
| **Overall** | **The excess is in the event windows** | |

Two independent programs, written by OpenAI's and Google's models from the protocol alone, reproduce all 791
window scores to within 0.000001, every combined score and every label.

This does not say why. It rules out two dull explanations: that the published table cannot be got from the
public data, and that the devices or the arithmetic produce an excess whenever they are scored this way. It
leaves two others standing, and cannot choose between them: that something real happened to the network during
these events, or that the events and their windows were chosen, at least sometimes, with some knowledge of the
data. Question #47 bears on that choice: on 58 later events picked by rule, the same statistic showed nothing.

## What was tested

The Global Consciousness Project registered 500 formal events between 1998 and 2015 and reports a combined
score of 7.31 for them. Its registry and its table of published scores were saved and parsed; leaving out the 13
rows the project itself excludes gives exactly 500 events whose published scores combine to 7.312.

396 of those events could be audited by rules fixed from the tables alone: the project's standard recipe at
one-second resolution, a window that parses, registry and published dates that agree, and data files for the
event and for a control window. They supply 5.93 of the published 7.31. The other 104 (all of 1998, the New Year
analyses, events with special recipes, and a few rows with typing errors in their dates) were not audited.

Each event's window was scored from the raw one-second data with the project's standard statistic, and so was
the same window one week earlier (two weeks for six; later instead of earlier for 30), kept clear of every
registered event. An event and its control were standardised with the same reference data: about a month's
worth of ordinary days around them.

One event of the 396 could not be scored: during number 469 (5 November 2013) only one device reported for at
least half the window.

## The evidence

### Reproduction

| | Our main scores | With theoretical standardising |
|---|---|---|
| Events compared | 395 | 395 |
| Correlation with the published scores | 0.959 | 0.958 |
| Slope of ours on published | 0.956 | 0.955 |
| Mean difference (ours minus published) | −0.026 | −0.001 |
| Median absolute difference | 0.106 | 0.105 |
| Within 0.25 | 73% | 76% |
| Within 0.5 | 93% | 92% |
| Combined score, ours | 6.08 | 6.58 |
| Combined score, published, same events | 6.61 | 6.61 |

With theoretical standardising (every device assumed to have exactly its design variance) our combined score is
6.58 against the published 6.61, and the mean difference per event is −0.001. That suggests the published table
was built largely that way; it is an inference from the fit, not something the project's pages say. The six
largest disagreements are events 397 (ours −0.04, published 2.38), 45, 49, 155, 339 and 60; all but 339 and 397
are from 2000 to 2003.

### Events and controls

| | Events | Controls |
|---|---|---|
| Windows scored | 395 | 396 |
| Combined score | **+6.08** | −0.42 |
| Mean score per window | +0.306 | −0.021 |
| Spread of the scores | 1.04 | 0.98 |
| With theoretical standardising | +6.58 | +0.08 |
| Without the mean and variance egg check in the scored window | +5.92 | −0.49 |
| The cross-egg part alone | +5.85 | −0.37 |

- **The controls behave.** Their mean is −0.02 with a 95% half-width of 0.10, and their spread is 0.98. The
  procedure does not manufacture an excess on ordinary days.
- **Device variance is not the cause.** The project warns that uncorrected device variances push the statistic
  up. With no correction at all the controls come to +0.08. Whatever that bias is, it is far too small to
  matter here.
- **The excess is in devices moving together.** The cross-egg part, which one device's excess variance cannot
  move, carries nearly all of it: +5.85 for events, −0.37 for controls.
- **It does not depend on the egg check,** which looks at the data being scored: without it, +5.92.

### Events against their own controls

Mean difference +0.329 per pair, standard error 0.069; the event scored higher in 250 of 395 pairs (63%). Of
200,000 random sign flips none reached the observed sum, so p = 1/200,001.

| Set of pairs | Pairs | Events combined | Controls combined | Mean difference | One-sided p |
|---|---|---|---|---|---|
| All | 395 | +6.08 | −0.45 | +0.33 | 0.000005 |
| Events that do not overlap an earlier one | 393 | +6.19 | −0.28 | +0.33 | 0.000005 |
| Control earlier than the event | 365 | +5.81 | +0.23 | +0.29 | 0.000005 |
| Control later than the event | 30 | +1.80 | −2.34 | +0.75 | 0.000005 |
| Without the five events scored in #47 | 390 | +5.89 | −0.16 | +0.31 | 0.000005 |

The 30 pairs with a later control have controls that are low (−2.34 combined). With 30 windows that is within
what chance does about once in fifty times; it is noted, not explained.

### By window length

| Window | Events | Events combined | Controls combined | Mean difference | One-sided p |
|---|---|---|---|---|---|
| Under 1 hour | 30 | +1.37 | +0.30 | +0.20 | 0.25 |
| 1 to 6 hours | 207 | +3.19 | −0.43 | +0.25 | 0.003 |
| Over 6 hours, under a day | 65 | +4.32 | +1.40 | +0.37 | 0.012 |
| A day or more | 93 | +3.39 | −1.59 | +0.52 | 0.0007 |

Every class is positive. The excess is not carried by one kind of window.

### By year

| Year | Events | Ours | Published, same events | Controls |
|---|---|---|---|---|
| 1999 | 1 | −0.91 | −0.84 | +0.76 |
| 2000 | 15 | +1.07 | +1.37 | +1.06 |
| 2001 | 22 | +1.95 | +2.48 | +0.87 |
| 2002 | 23 | −0.61 | −0.50 | −0.29 |
| 2003 | 33 | +1.12 | +1.25 | +0.54 |
| 2004 | 26 | +1.31 | +1.11 | +0.20 |
| 2005 | 18 | +3.55 | +3.30 | +0.29 |
| 2006 | 16 | +2.59 | +2.78 | −0.92 |
| 2007 | 21 | +1.99 | +1.96 | +0.13 |
| 2008 | 22 | +2.25 | +2.27 | +1.57 |
| 2009 | 32 | +1.67 | +1.94 | +1.01 |
| 2010 | 30 | +1.45 | +1.78 | −1.64 |
| 2011 | 40 | +2.19 | +2.49 | −2.79 |
| 2012 | 31 | +1.39 | +1.65 | +1.23 |
| 2013 | 32 | +1.61 | +1.53 | −1.91 |
| 2014 | 18 | +0.76 | +0.48 | +0.34 |
| 2015 | 15 | +0.48 | +0.94 | −0.51 |

Combined scores of each year's events. Fifteen of the seventeen years are positive for the events; the controls
scatter on both sides of zero, as they should.

## Replication

OpenAI `gpt-6.2-astra` and Google `gemini-4-neon` each wrote a program from `protocol.md`, `windows.tsv`,
`sources/blocked.tsv` and the format notes, without our code or numbers. Both ran first time. Against ours
(`replication/*/comparison.txt`): all 395 event scores and 396 control scores agree to within 0.000001; the
degrees of freedom and the number of devices used agree exactly for every window; the combined scores, the
agreement measures, the sign-flip p and all four labels are the same.

Both programs start from the same `windows.tsv`, so this checks the scoring. It does not check the reading of
the project's two tables, which was done by one sub-agent's script and spot-checked by eye.

## Limits

- **The audit cannot see how events were chosen.** By the project's account, events and windows were specified
  before the data were examined; for sudden events that means after the event happened. A note in the source of
  the registry page, commented out so that the page does not display it, says that from 1 June 2005 "the GCP
  website now includes a realtime index display that integrates the data in a fashion related to one of our
  primary analysis methods", and that surprise events "will be identified algorithmically, to preclude influence
  from the GC Index display". So the project itself saw the risk. If windows were
  sometimes set, moved or kept with some knowledge of how the data looked, the result would be exactly what is
  found here: a real excess in the chosen windows and nothing in windows a week away. Nothing in the two saved
  pages time-stamps when each row was written.
- **#47 points one way without settling it.** On 58 events of 2016 to 2025 chosen by rule, with the same
  statistic, the combined score was −1.83. A real effect of the size reported should have shown there, unless it
  needs the kind of event, the choice of window or the larger network of the earlier years.
- **104 of the 500 published events were not audited.**
- **Not the project's own pipeline.** The device checks and the standardising are ours. Agreement is close but
  not exact, and six events differ from the published score by more than 0.9.
- **No placebo calendar.** Both reviewers asked for made-up events on other ordinary days scored the same way.
  The 396 controls are the calibration there is. They look right, and they would not reveal a subtle fault.
- **Controls are one or two weeks from their events,** mostly earlier.
- **The p-values are nominal.** Windows share reference data, and two events overlap earlier ones.
- **The literature was not read.** The project's own technical papers, and its critics, may already contain
  every number here.
- **One AI session** designed, ran and wrote up the audit, and the same model wrote #47. Sub-agents of the same
  vendor parsed the tables, wrote the unit tests and adapted the review and replication scripts.

## Departures from the plan, and things to know

- No amendment was needed.
- The locked program parsed the day files one at a time and was slow. Part-way through the run a helper filled
  the same cache in parallel, using the program's own reader and writing each file under a temporary name. The
  scores are unaffected; both replications, which never used that cache, match them.
- Before our run had finished I saw one line of the OpenAI replication's log, with its agreement measures. The
  protocol was locked and our program was already running.
- My guess before the run (in `log.md`) was 60% for this outcome.

## Spending

$3.37: $1.90 for two rounds of review before the lock, $1.47 for the two replication programs (`SPENDING.md`).

## Who did the work

AI did this work. Claude Fable 5.2 (Anthropic) designed the audit, wrote the scoring program, ran it and wrote
this report on 2026-11-23. Sub-agents (Claude Opus 5.5) parsed the project's tables, wrote the unit tests and
adapted the review and replication scripts. OpenAI `gpt-6.2-astra` and Google `gemini-4-neon` reviewed the plan
before the lock and each wrote an independent replication. Eugene directed it: he asked for the audit.

## What this means

For seventeen years a project recorded the output of dozens of random-number generators around the world and
claimed that the numbers went slightly non-random during big world events. Its headline figure, odds of about a
trillion to one, comes from 500 events. We took the 396 we could check, went back to the raw numbers, and
recomputed each one. Our figures match theirs, and the effect is there: clearly present during the events, and
absent in the same hours a week earlier or later. So the published result is not an arithmetic mistake, and it
is not a quirk of the machines. What we cannot tell is how the events were picked. If someone chooses which
stretches of time to count while able to see, even roughly, how the numbers are behaving, an effect like this
appears whether or not anything unusual is going on. That is why our earlier test matters: when we chose events
by a fixed rule, after the project's series ended, the effect was not there. Taken together, the two results say
the original numbers are real and the explanation is still open, with the way the events were chosen as the
first thing to look at.
