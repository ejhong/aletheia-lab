# Deep Memory: first live cycle and explicit recovery

The frozen experiment at commit `07f74465528512fd050acf521f8f72dc8c567f29`
did not complete round one. The operator stopped further spending after finding
duplicate material in the editorial requests. No article was generated or case
record adopted before that stop. This is a failed development attempt, not
evidence of uninterrupted autonomous improvement. Round two was not purchased.

The baseline was a 532-word article, five claims, five evidence records, three
sources and two research opportunities. The input included the full Birdmen
homepage and founding question. Protocol, inputs, baseline and original provider
receipts remain in `.research-runs/deep-memory-autonomy-v1/` and its referenced
research directory. The original Aletheia and Lab PR 2 are unchanged.

## Observed work and cost

| Call | Input tokens | Output tokens | Recorded cost |
| --- | ---: | ---: | ---: |
| Gemini Deep Research Max, 88 searches | 4,317,273 including tool input | 97,554 including thought | $20.257064 |
| Astra verification plan | 306,622 | 7,539 | $8.230960 |
| Astra record reconciliation | 331,852 | 14,400 | $9.376285 |
| Two small source checks | 176,492 | 5,066 | $0.054255 |
| Total | | | $37.918564 |

These are recorded-tariff amounts, not vendor invoices. Gemini is deliberately
estimated at long-context rates throughout, without cache or free-search credit.
Two source checks completed while the pause was being applied; an earlier
progress message incorrectly said it stopped before source checking. Neither
created an unresolved hold. The previous $18.88 hold remains unchanged.

The research report proposed stronger conclusions than its cited material
established. Astra independently flagged the recurring confusion between local
function and independent origin, the narrowing of culture-bringer comparisons to
white-god narratives, and the promotion of a disputed comparative-mythology
model into a settled result. Its proposed updates preserved these distinctions
and recorded unresolved arguments. This is promising editorial behavior, not
independent verification of its proposed findings.

Seven of twelve requested readings failed through access errors or the current
document-size limits. The available readings primarily covered Birdmen's own
investigation reports and Thompson's review of Witzel. They support bounded,
attributed accounts of arguments and prior work; they cannot establish the
broader history of the motifs. The small civilisers capture also exposes the
HTML reader's first-article selection problem. Complete-page extraction and
context-preserving reading of large documents need further work.

## Corrections and continuation

The old handoff supplied the report and commissioning packet directly and then
again inside both provider `output` and `raw` envelopes. The model projection
now preserves the complete request, report and every citation once, with a hash
link to the immutable original response. It removes approximately 66% and 59%
of the two recorded request bodies. It does not summarize or discard the
founding inputs, source readings or case records.

The source checker also repeated an inert `$schema` dialect declaration in its
JSON replies, which the strict response parser rejected. That one declared
metadata field is now accepted explicitly; every record must still receive all
required findings, and any false substantive finding rejects its bundle. The
second check had also flagged an unsupported locator, which remains a reason
to reject its proposed bundle. No finding is silently changed to make it pass.

`scripts/continue-report.ts` is the explicit recovery path. It reuses the saved
research and can replay completed planning and reconciliation only when the
instructions, model configuration and projected model inputs match. Requests,
responses, source failures and replay provenance remain inspectable. It then
runs the existing source checks and edition comparison. It never buys another
research task or publishes. This continuation is separately identified and
does not count as an unchanged second experimental round.

At this entry's first commit, that continuation has not started. Its result
must be recorded below, including failures and the remaining cost. The original
$40–60 experiment allowance still applies; recurring jobs stay disabled, and
the temporary daily increase must return to paused/$25 after the continuation.
