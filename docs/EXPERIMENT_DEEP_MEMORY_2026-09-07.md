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
second check had also flagged an unsupported locator. Such a finding rejects
its proposed bundle; no finding is silently changed to make it pass. The
continuation below records the outcome of fresh checks, including disagreement
with that first response.

`scripts/continue-report.ts` is the explicit recovery path. It reuses the saved
research and can replay completed planning and reconciliation only when the
instructions, model configuration and projected model inputs match. Requests,
responses, source failures and replay provenance remain inspectable. It then
runs the existing source checks and edition comparison. It never buys another
research task or publishes. This continuation is separately identified and
does not count as an unchanged second experimental round.

At this entry's first commit, that continuation had not started. The following
records its completed result, within the original $40–60 experiment allowance.

## Continuation result

The explicit continuation ran at code commit `92ae780` and prepared
[`edition-2026-09-08-e6ab426e-fded-4791-8a11-bae9f03d5805-revision`](../content/cases/deep-memory/editions/edition-2026-09-08-e6ab426e-fded-4791-8a11-bae9f03d5805-revision.yaml).
The saved research, captures, planning and reconciliation were reused with
recorded equivalence checks. No second research task was bought. The records,
article and assessment were produced by the code without interactive editing.

| Measure | Baseline | Prepared candidate |
| --- | ---: | ---: |
| Article words, whitespace count | 532 | 1,486 |
| Claims / evidence records | 5 / 5 | 10 / 10 |
| Sources / research opportunities | 3 / 2 | 7 / 6 |
| Documentary plates in the article | 1 | 2 |
| Case assessment | Unresolved | Unresolved |

Four of five proposed record bundles passed source checking and loader
validation. They retain the teaching–departure correspondence, image-pilot
disagreement, a reported catalogue null, and Thompson's specific criticisms of
Witzel. These are attributed reports of arguments and prior investigations, not
independent confirmation of the underlying histories or experiments. The
revised essay also integrates the existing Met and Atakuman records, preserves
serious inheritance arguments and alternatives, and identifies work still
needed. Greater word or record counts are not the success criterion.

Both Astra article candidates validated. Four independent comparison seats
returned votes; all four ranked both candidates above the incumbent and marked
both constitutionally compliant. Anthropic, xAI and Venice preferred the
revision; Gemini preferred the recomposition. The OpenAI seat was blocked before
its API request because its conservative reservation did not fit the remaining
temporary allowance alongside concurrent holds. This is a missing vote, not
concurrence. The existing selection rule advanced the revision with four valid
seats; publication and assessment ratification remain separate requirements.

| Continuation work | Recorded cost |
| --- | ---: |
| Five fresh source checks | $0.141233 |
| Two Astra article and assessment drafts | $4.252061 |
| Four independent article comparisons | $1.929782 |
| Continuation total | $6.323076 |
| Original attempt plus continuation | **$44.241640** |

The final allowance receipt confirms paused calls, daily $25, monthly $150 and
the unchanged $30 review reserve. No new unresolved holds remain; the earlier
$18.88 hold is preserved. Monthly accounted-or-held usage is $86.828809,
including earlier work and that hold. These remain tariff estimates, not
invoices. The first revised article request used 145,342 input tokens after the
duplicate-envelope fix, below the previous long-context threshold.

The durable continuation directory is
`.research-runs/report-continuation-2026-09-08-d0cbe3c4-80d9-4f11-b65e-2c2fc10dab27/`.
Public proposal, adoption and comparison history is retained under
`proposals/intake/`; full retrieved documents and provider receipts stay in the
ignored local run directories. The final allowance snapshot is
`deep-memory-autonomy-v1/after-explicit-continuation-1788826208148.json`.

## What must improve before another experiment

1. **Preserve whole-page context.** The civilisers page uses 46 article cards
   inside a main region. The old reader retained just the first, 478 characters.
   After this run, `html-text-v2` was introduced: prefer the complete main region;
   use an article only when there is one; otherwise retain the body/document.
   The local source now yields 31,318 characters, including later qualifications.
   Existing experimental captures and locators remain `html-text-v1` and have
   not been reinterpreted as full-page readings. Regression tests cover later
   null results, surrounding caveats and nested articles. Empty and oversized
   readings now report different errors with actual character counts.
2. **Check each record according to its role.** The flood bundle failed because
   the checker demanded a page/paragraph locator on its Source container even
   while supporting the actual claim and evidence locators. This is a workflow
   false rejection, not evidence against flood inheritance. A future check
   should distinguish bibliographic metadata from located assertions. The
   failed bundle has not been overridden. The fresh image-pilot check also
   accepted a proposal whose first check questioned its locator; final text
   anchors are computed from the actual captured quote. This disagreement
   needs a fixture and review, not a claim that a cheap checker is infallible.
3. **Improve access before buying more breadth.** Seven failed readings limited
   what could enter the ledger. Large documents need explicit section/page
   reading with context, and unavailable primary sources need legitimate
   alternate access paths. A derivative report remains derivative even when
   several models agree with it. The next paid test should check whether better
   readings produce substantive new support, criticism or correction, rather
   than another summary of the same project reports.
4. **Reserve the whole comparison before dispatch.** Per-call maximum-context
   reservations can exclude a seat even when final charges would fit. Plan the
   intended review set using the actual packet and queue it transparently if
   necessary; do not lower the required concurrence or buy retries silently.
5. **Repeat on a frozen implementation.** Keep the founding question, complete
   input, current records and considered/deferred findings in the next packet.
   Then test another update without changing code or rescuing content during
   the run. Record useful corrections, coverage, rediscovery and cost. The
   current result is a promising development recovery, not a successful pair
   of unchanged autonomous rounds or proof that more AI time always helps.

Validation after the generated changes and reader correction: 385 tests passed,
lint and TypeScript passed, the webpack production export succeeded, and all
internal links across 594 pages resolved. Desktop and phone previews loaded
the artwork and both documentary plates with no horizontal overflow. The
candidate remains explicitly labeled as an AI assessment awaiting review.
