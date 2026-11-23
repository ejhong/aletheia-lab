# Pre-lock design review

One round, before the lock and before any statistic was computed on unshuffled genomes. OpenAI `gpt-6.2-astra`
(`round1/openai.md`) and Google `gemini-4-neon` (`round1/google.md`) were each given the draft protocol
(`round1/protocol_as_reviewed.md`) and the prompt in `run_review.py`. Claude Fable 5.2 (Anthropic) checked each
point and rewrote the protocol. The rewrite was not sent back for a second round; that is a known gap.

Cost at list price: OpenAI $0.27, Google $0.81.

## What they found and what changed

| Finding | Who | Verdict | Change |
|---|---|---|---|
| The main test compares a person with their neighbours, so a foreign community buried together looks normal. The Greenland Norse, the plan's own check, would have failed it. | both | Correct. | Everyone now also gets an absolute test that uses no neighbours. Neighbours must come from a different site. |
| The fallback test on the American side could not see an African at all, and would miss most part-European people. | both | Correct: against an outgroup-like person both statistics are zero. | Replaced by a comparison with a clean baseline of ancient Americans, for four foreign references. |
| Centring is not harmless: the reference genome is itself closer to some peoples than others, so the centred statistic is not zero under the usual null, and it shrinks true signals. | Google; OpenAI on allele coding | Correct in general. It is unbiased when the person and their baseline are the same population, which is the null here, and it shrinks real signals. | The plain f4 decides. The centred value is a guard: it must be at least half the plain one. |
| One low-coverage genome (MA1) as a control loses 30% of SNPs and adds noise | Google | Correct. | Replaced by 15 Karelian hunter-gatherers, who are removed from the tested people. |
| Geography: Rapa Nui, the Aleutians and east Greenland would land on the wrong side | both | Correct. Checked against the metadata: none is in this release, but the rule was wrong. | Rule rewritten; the boundary cases are printed by `build_people.py`. |
| A burial dated around 1450 can postdate Columbus | both | Correct. | A date flag for every hit; "possibly later than 1492" is one of the descriptions. |
| "Neighbourhood" and outlier-suffix classes would dismiss real evidence | both | Correct. | Flags are recorded and never remove a hit. A group of hits at one site can stand as a group. |
| Contamination cannot be excluded from the file, especially in females | Google | Correct. | Sex and haplogroups are recorded for every hit; the limit is stated. |
| The made-up strangers overstated power: real admixture comes in contiguous tracts | Google | Correct. | Foreign DNA is now dropped in by whole 5 cM blocks, a 0% control is included, and the conclusion drawn from it is narrower. |
| "No one carries more than X%" does not follow from average recovery rates | OpenAI | Correct. | Removed. The negative statement is "no outlier of this kind among the tested people". |
| Two separate 5% budgets | both | Correct. | One family, one threshold. |
| The centre pools (a union with members removed) did not match each centre's make-up | both | Correct. | Each member is compared with their own neighbours and the block sums are added. Outlier labels are excluded. The labels' coarseness is stated. |
| Transversion check needed a floor; second reference undefined for some tests; whether u is refitted | both | Correct. | Specified. |
| Ambiguities: ties, masks, the trimming rule, the centring under deletion, radius | both | Correct. | Specified. |
| Literature: an Indus city genome exists (Rakhigarhi); Pacific contact has published genetic evidence | OpenAI | The first is right as far as we know and the genome does not pass these filters; the second matches what we recalled. Neither paper was read. | Wording changed; the Pacific studies are cited as context. |

Not adopted, with reasons:

- Constraining the fit, fitting by region, or propagating its uncertainty (both). The fit is kept simple and its
  limits are stated; the coefficients and the residual distributions are reported.
- Removing close relatives from pools, matching library chemistry in pools, coherent-segment simulations beyond
  block replacement, more donor kinds (both). Left as stated weaknesses to keep the scan small enough to finish.
- A frozen site-by-site roster for each centre with a rationale (OpenAI). The centres half is thin in this
  release whatever is done; the coarseness is stated instead.
