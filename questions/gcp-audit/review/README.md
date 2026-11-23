# Review of the plan before it was locked

Two models from other vendors read `protocol.md` before any event or control window had been read: OpenAI
`gpt-6.2-astra` and Google `gemini-4-neon`, on 2026-11-23. Their replies are in `round1/` and `round2/`, with the
text they saw. To run a round: `python3 review/run_review.py <round>` from `questions/gcp-audit` (add `--narrow`
for an errors-only round); keys come from `OPENAI_API_KEY` and `GEMINI_API_KEY`.

## Round 1

The first plan measured each egg's spread on the control days of the event's calendar year, with the event's own
control inside the event's pool and outside the control's; its labels could overlap; and it judged reproduction
by the correlation and the combined scores alone.

| Point (who) | Done |
|---|---|
| Event and control were not scored on an equal footing: the event's pool held its control and the control's did not (OpenAI) | Each pair now has one pool for both windows, and the days its own control touches are not in it. |
| The pool was not cleaned of faulty devices (Google) | An egg's day enters the pool only with 3,600 trials that pass the egg check. |
| A calendar-year pool collapses in a thin year such as 1999 (both) | The pool is now the control days of events within 183 days either side. |
| The window's end: the registry's words can be read as excluding the end time (both) | Stated: both ends included, as the registry's own example and its `:59` end times show. |
| The reproduction labels did not measure per-event agreement, and the combined-score gate was too tight (OpenAI) | Labels now use the correlation, the median absolute difference and the slope. Combined scores, mean difference and shares within 0.25 and 0.5 are reported. |
| Reproduction should be judged under theoretical standardising too, since the published table may use it (Google) | Both are reported and labelled. |
| The overall labels could overlap; no outcome for thin coverage (both) | Labels are now checked in a fixed order, starting with "insufficient coverage" (fewer than 300 pairs). |
| "Controls look like chance" claims more than a non-rejection shows; the allowed spread was too wide (OpenAI, Google) | Renamed "no calibration failure detected"; spread limits tightened to 0.85–1.2; the mean and interval are reported. |
| The sign-flip test was justified wrongly (OpenAI) | Reworded: it needs the two windows of a pair to be exchangeable under chance, which the common pool is there to provide; the p-value is called nominal. |
| The 396 events do not "carry 6.66 of 7.31" (OpenAI) | Corrected: they supply 5.93 of the 7.31; the 104 others are not audited. |
| Disputed events were kept out of the test but only their registry dates were kept clear of controls (OpenAI) | Their published dates are now blocked as well. One control moved. |
| The egg check looks at the window being scored (OpenAI) | Kept, and results without it are reported. |
| Most controls are earlier than their events (OpenAI) | Kept; earlier and later controls are reported separately. |
| Overlapping event windows are not independent (OpenAI) | Kept, as the project does; the non-overlapping subset is reported. |
| "45 or more" against "outside 55 to 145" (both) | The two project statements differ at the boundary; said so; kept the first, as in #47. |
| Short windows and the normal approximation (both) | Unit tests at 60 s, 600 s and 6 hours; errors of the formula stated. |
| Programmer's choices left open: correlation, divisors, pair order, pool cleaning (both) | Stated. |
| The cross-egg part is the project's own central claim in later papers (Google) | Noted as the reviewer's statement; the papers were not read. |
| "600 df weight" is unexplained (both) | Said so; marked `unverified`. |

Not done, and why:

- **A placebo calendar** of made-up events on other ordinary days, scored with the whole procedure (both
  reviewers; the strongest check they asked for). It needs several hundred more day files. Left out for time; the
  396 controls are the calibration there is, and the plan says so.
- **Balanced control directions**, or both flanking weeks (OpenAI). Would double the control data.
- **A reference pool from days that are not anyone's control** (OpenAI). The pair's own control days are left out
  of its pool; other pairs' control days are in it.
- **Tracing the historical statistic** behind each row, including the published degrees of freedom (OpenAI). The
  pages read do not give them.
- **Reading the literature** (Bancel and Nelson) to settle which standardising the table used (Google).
- **An independent rebuild of the tables and windows** by the replicator (OpenAI). The replication starts from
  `windows.tsv`; the plan says what that does and does not check.

## Round 2: errors only

Asked only for errors of logic, wrong facts and contradictions in the revised plan. Neither reviewer found an
error in the method. Google checked the arithmetic of the egg check's 2.4%, the cross-egg denominator and the
Wilson–Hilferty error and found them right. What was changed:

| Point (who) | Done |
|---|---|
| "What would count" drew conclusions the labels do not support, used an interval that was never defined, and could contradict the "mixed" label (both) | Rewritten to refer to the labels only. "No excess found", "mixed" and "insufficient coverage" are reported as they are. |
| The opening paragraph claimed more than a detection in events and none in controls shows (OpenAI) | Reworded around the paired comparison and around "this reconstruction". |
| The sign-flip p-value needs joint exchangeability, which the same pool does not prove (OpenAI) | Said so; the p-value is called nominal. |
| The egg check's 2.4% is a bound on the observed mean square, not on the device (OpenAI) | Reworded. |
| Theoretical standardising is "not part of the labels" yet gets a reproduction label (both) | Heading changed. |
| Yearly breakdowns: 1999 has one event, so spreads, correlations and slopes are undefined; the cross-egg part is undefined with no second of two eggs (both) | Stated; the program leaves them empty. |
| Conditions 5 and 6 are not read from the tables alone; six controls are two weeks away (OpenAI) | Corrected. |
| The exact chi-square conversion can be made finite with a log-tail method (OpenAI) | Reworded: the formula is used because it needs no tail probability. |
| "Pooled standardising is unbiased" is too strong (OpenAI) | "Shows no bias within the simulation's error". |

After round 2, and not seen by the reviewers: "reproduces closely" also requires the slope of our scores on the
published ones to lie between 0.8 and 1.25. The sub-agent that wrote the unit tests found that a 30% error of
scale would otherwise pass.

Cost of the two rounds: $1.90 at list price (OpenAI $0.81, Google $1.09).
