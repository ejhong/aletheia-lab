# Pre-lock design review

Before the protocol was locked, models from two other vendors were asked to criticise it. Each got the full
protocol and the prompt in `run_review.py`. No result existed and no Native American genotype had been read.

- Round 1 (2026-11-23 UTC): `round1/openai.md` (OpenAI `gpt-6.2-astra`) and `round1/google.md` (Google
  `gemini-4-neon`), on `round1/protocol_as_reviewed.md`.
- Round 2: the same two models on the revised protocol, `round2/`.
- Round 3: a narrow last check by the same two models, for errors of sign, algebra or logic only, `round3/`.

The reviews were worth having. Each of the first two rounds found errors that would have changed a conclusion.
The reviewers disagree with each other in places, and a reviewer's claim is not a fact until checked; the
"Verdict" columns say what was checked and how.

## Round 1: what they found and what changed

Both reviewers independently found the first two items. Claude Fable 5.2 (Anthropic) checked each point and made
the changes.

| Finding | Who | Verdict | Change |
|---|---|---|---|
| The sign of the Onge-versus-Papuan test (L2) was stated backwards | both | Correct. | Text fixed; a one-SNP sign check added to the protocol and to `analysis/test_f4lib.py`. |
| The ancient decision statistic f4(Han, Onge; Mixe, G) is not bias-free: contamination by modern Europeans, or extra West Eurasian ancestry, pushes it up and would be read as the signal. The draft said the opposite. | Google; OpenAI in general terms | Correct. Checked by hand: f4(Han, Onge; Native American, European) is positive. | Ancient design rebuilt. Ancient groups are now compared with an ancient baseline of the same data type, and "stands out" needs three statistics to agree, each guarding against one artefact. |
| N3 = N1 − N2 holds only on the same SNPs | both | Correct. | Ancient statistics are computed on a stated common mask. |
| Early individuals were included whatever their quality assessment, and could decide a conclusion | Google | Correct. | Versions without a Pass are reported but cannot support a conclusion. Sumidouro5 is judged on its Pass version only. |
| The primary rule gave two chances and let one panel carry the result alone | both | Correct. | One primary test (P_A). Panel B became supporting evidence, with a held-out-donor version. |
| Onge and Jarawa genomes come from a third pipeline, so "within one pipeline" was wrong | both | Correct. | P_A now uses Papuans, so all four sets share a pipeline. Onge is a robustness axis. |
| Present-day Reference groups (Pima, Mixe, others) may carry European or African admixture, which fakes the signal | both | Plausible; not checked against a source. | Added a blind admixture screen for every present-day American individual (step 1), a group-level check, and the share of P that admixture could explain. |
| The headline did not require specificity | Google | Correct. | Headline now needs the Han control and L3 in the same panel. |
| Donor structure: relatives, one donor driving the result, shared donors between panels | both | Correct. | Leave-one-donor-out, held-out donors, kinship and an unrelated-subset run added. |
| Ranking 145 world groups by Z is a picture, not a test | both | Correct. | The world ranking is now descriptive. Specificity is decided by direct contrasts. |
| Ascertainment: 1240K includes SNPs chosen in a Karitiana | Google | Plausible; the panel membership of SNPs is not in the public files, so it cannot be tested directly. | Added a Yoruba-polymorphic SNP class; Suruí-only cells and leave-one-donor-out act as guards. Listed as a weakness. |
| "Not detected" is not "absent"; nonsignificant is not "equal" | OpenAI | Correct. | Intervals reported; "against the published size" needs the anchor's interval to exclude it; the L2 interval is given as a fraction of P. |
| Ambiguities: set definitions, deduplication keys, boundaries, distance method, jackknife formula, tolerance near zero | both | Correct. | All specified. `analysis/sets.tsv` is the locked list, with its hash in `MANIFEST.md`. |
| Literature: quote Posth exactly; add Raghavan 2015 and Yang 2017; soften "every published reading" and "extra strand in the founding ancestry" | both | Correct. | Posth quoted from the article; the two papers added and marked as not read; wording softened. |
| The same individuals should be compared SNP by SNP in the technical checks | OpenAI | Reasonable. | Per-person versions of T1 and T2 added. |
| Detectability of the modern signal at ancient coverage | OpenAI | Reasonable. | Added as a descriptive calibration for the early individuals. |

Not adopted, with reasons:

- A pre-colonial ancient genome as the unadmixed baseline for the admixture screen (Google). It would compare
  ancient with present-day data inside the screen. The panel's own Amazonians are used instead, leaving the
  individual out.
- Splitting every ancient pool by archaeological site and showing per-site deletions (OpenAI). Too large for the
  budget; pools are reported with their composition, and the limitation is stated.
- A Denisovan check (Google, minor). Left out to keep the family of tests small.

## Round 2: what they found and what changed

| Finding | Who | Verdict | Change |
|---|---|---|---|
| The ancient baseline included the Caribbean, whose ancient people descend largely from South America; that would hide a South American signal | Google | Plausible and standard in the literature; not checked against a source by us. | The Caribbean is out of the baseline (now ancient North America and Mesoamerica) and is tested as its own region. |
| "Falls short of the Amazonian level" compared ancient with present-day genomes, which the design says is unsafe | both | Correct. | The label is gone. Those statistics are descriptive. The coastal question is now a type-matched contrast of ancient coast against ancient inland Andes. |
| The admixture screen picked donors using a statistic correlated with the outcome, used an unscreened baseline, and could put flagged donors back | both | Correct. | The primary test now uses the locked sets as they stand. The per-individual screen is a diagnostic, with one sensitivity run that leaves flagged donors out. |
| The admixture estimate had a finite-sample bias: French appeared twice in its denominator | both | Correct (a repeated population adds its sampling variance). | The ratio now uses Sardinians and French as two samples of the source, so no set repeats. An African term was added. Everything is jackknifed jointly on one mask. The "clean" rule became: the adjusted P must stay at Z of 2 or more. |
| The Han control should be one-sided; real Papuan-related ancestry would make it slightly negative | Google | Reasonable. | One-sided. |
| L identities need a common mask; Tianyuan covers fewer SNPs | OpenAI | Correct. | All L statistics share one mask; P is recomputed on it for scale. |
| The pooled paired checks (T1, T2) could compare different people at a SNP | OpenAI | Correct. | Only people with data in both versions count at each SNP. |
| Pacific islands (Rapa Nui, Hawaii) could be swept into coastal regions | Google | Checked against the metadata: none are among the eligible individuals. | Stated in the protocol. |
| The headline had no case for an inconclusive primary and ignored the other donors | both | Correct. | Headline is now two lines: the primary with its checks, and the donors outside panel A. |
| The "counts against the published size" rule compared D values from different SNP sets | both | Correct. | The anchor is a comparison, not a test. |
| The robustness rule mixed sign, precision and the Onge-versus-Papuan question | both | Fair. | The rule is now sign consistency plus a separate requirement that each community shows the excess alone. Medians are reported by axis. |
| Leave-one-out judged by Z penalises the smaller sample | OpenAI | Correct. | Judged by effect size: every leave-one-out estimate at least half the full one. |
| The multiple-testing family and formula were not stated | both | Correct. | Bonferroni, formula given; the family is the tested (set, type) pairs whose members all have a Pass. |
| The power check did not match the ancient decision | both | Correct. | Replaced by the smallest detectable effect for each tested set, in units of the present-day excess. |
| Capture and shotgun types hide library differences (damage treatment, Twist capture) | Google | Checked: by suffix, capture is 1240k capture and shotgun is plain shotgun; Twist and merged data carry other suffixes and are excluded. Library chemistry does vary within type. | Stands-out now needs the transversion estimate to be at least half the all-SNP one. Listed as a weakness. |
| Literature: the Mixe are reported to carry an unsampled lineage; Yang's finding is about differential sharing; Raghavan should not be folded into a consensus | both | Not checked by us (papers unread). | Wording changed; the Mixe point is listed as a weakness and attributed. |
| Ambiguities: labels, ties, coastline sampling, kinship formula | both | Correct. | Specified. |

Not adopted, with reasons:

- Stratifying ancient pools by archaeological site, leave-one-site-out, and a temporally matched baseline (both).
  Beyond the budget. The limitation is stated, and any set that stands out will be reported with its members.
- San-polymorphic SNPs, archaic controls, Ust'-Ishim and Hoabinhian controls, every other present-day American
  group (Google). Left out to keep the family of tests from growing further.
- Rerunning the screen iteratively (Google). Moot now that the primary is unscreened.

## Round 3: last check for errors of sign, algebra and logic

| Finding | Who | Verdict | Change |
|---|---|---|---|
| The European and African admixture fractions must be solved together; each ratio alone is thrown off by the other kind of ancestry | both | Correct. | The two mixture equations are now solved jointly. |
| The sign rule should say "measured against O" | OpenAI | Correct. | Added. |
| "No genotype was read" is not true of the shuffled test run, which reads genotypes in order to shuffle them | OpenAI | Correct. | Reworded: none was looked at, and no statistic was computed on unshuffled ones. |
| P_B.unrel depends on kinship, which the replication does not require | Google | Correct. | P_B.unrel is not required either. |
| The tolerance formula failed for negative values; two Z ranges overlapped at 3; the label list omitted four labels | OpenAI | Correct. | Fixed. |
| Several sentences claimed more than the rule delivers ("specific", "smallest detectable effect", "not owed to damage-prone SNPs", the coast "otherwise" case, "nothing would stand out") | OpenAI | Correct. | Reworded; the check is now called "beyond Han"; the coast rule has a case for a difference of unclear cause. |
| Array-design annotations that identify ascertainment panels are public | OpenAI | Not checked by us. | The weakness now says they were not used, instead of saying they do not exist. |
| The coastline distance is to sampled points, an upper bound | OpenAI | Correct; the error is at most about 2.5 km. | Stated. |

No further round was run. Changes made after round 3 were not reviewed by another vendor. There was one: the
centred f4 (see the protocol, "Statistic"), added after the run on shuffled genomes showed that data sources
differ in their overall share of reference alleles. It is reported beside every f4 and is a condition in the
ancient "stands out" rule and the coast rule.

## Cost

At list price from logged token counts: round 1 $1.09, round 2 $1.14, round 3 $1.11. One OpenAI call in round 1
timed out after 20 minutes with no response; whether it was billed is unknown, and it is entered in `SPENDING.md`
as an estimate.
