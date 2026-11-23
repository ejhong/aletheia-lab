# Review of the plan before it was locked

Two models from other vendors read `protocol.md` before any real date had been calibrated: OpenAI
`gpt-6.2-astra` and Google `gemini-4-neon`, on 2026-11-23. Their replies are in `round1/` and `round2/`, with the
text they saw. Cost: $1.78 at list price.

## Round 1

The first plan compared the real summed curve with made-up records of single dates drawn from an exponential
trend, and called a region "no drop, and a halving would have shown" when nothing was detected and power was 0.8.

| Point (who) | Done |
|---|---|
| The made-up records did not match the real ones: real bins average several dates; made-up ones were single dates (OpenAI) | Made-up records now keep the real bins, with each bin's number of dates and their errors. |
| Real dates are selected on radiocarbon age; made-up ones were not (both) | The same cut is applied to made-up dates; a bin left empty is drawn again. |
| One exponential over 5,000 years is too stiff a reference (both) | A parabola in the log; the straight line is kept as a variant. |
| The p-value is for a fitted reference; check the false-alarm rate of the whole procedure (both) | `crash.py --calibrate`: 100 made-up histories with no crash, North America's real bins and errors, the whole procedure applied to each. |
| "No drop" from non-detection plus 80% power overstates (both) | Replaced by "a halving is excluded", which needs the real step to be above 99% of halving records. Otherwise "cannot tell". |
| Power was not computed with the detection rule (OpenAI) | It is now. |
| Aquatic materials carry old carbon (both) | Screened by name; variant with them kept. |
| Who contributes the weight near the target? (OpenAI) | Reported for both sides, with the largest site left out as a variant. |
| A crash displaced from the detector (OpenAI) | Power reported for halvings starting 100 years later and earlier. |
| Wording on the earlier studies, the ice date, the DNA lines (OpenAI) | Corrected. |
| More made-up records at the decision thresholds (OpenAI) | 2,000 crash-free and 500 halving records for the main run. |

Not done: sub-regions and a geographic jackknife; a spline or logistic reference; re-forming bins with a
different origin; a model of research intensity; curve errors shared across bins and regions; a literature survey
of work after 2011.

## Round 2: errors only

Fixed before the lock: made-up records were losing the bins whose dates fell outside the admitted span, so they
had fewer bins than the real record (Google); the aquatic screen caught nutshell, eggshell and the fisher (both);
the overall verdicts overlapped (both); the p-value formula was written for 2,000 records only (OpenAI); the column
list (both); several statements that claimed too much, about the parabola, about power, about a "shorter" crash,
about what the false-alarm check proves, about "the largest" database, about which continents need which curve.

The false-alarm check was rerun with the final program. There was no third round.
