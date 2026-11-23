# The Australasian signal in the Amazon: results

Issue #31 · Lane: data · Protocol locked 2026-11-23T04:50:31Z · Two amendments (2026-11-23)

## Answer

**The signal is real in public genomes, and it is weaker and less specific than its reputation.**

1. **It is there.** Present-day Suruí and Karitiana share more alleles with Papuans than the Mixe do. The locked
   primary test gives Z = 4.2. On the exact comparison published in 2015, we get D = 0.017 against the paper's
   0.021.
2. **It holds up to changes of method and of donors.** It appears with every outgroup, Australasian group and SNP
   class tried, in each community alone, with any one donor removed, in 26 donors the original study did not use,
   and in two independently processed versions of the same genomes.
3. **It is only partly specific to Australasians.** Compared with the Mixe, about three quarters of the excess is
   beyond what the Amazonians also share with Han Chinese (Z = 2.8). Compared with the Pima, the Amazonians are
   closer to East Asians in general, and the part specific to Papuans is not significant (Z = 1.4).
4. **It does not point at Pacific islanders.** The excess is the same toward Onge as toward Papuans, and it is
   just as strong toward Tianyuan, a man who lived near Beijing 40,000 years ago (Z = 4.0). That is the pattern
   of an old Asian lineage, not of contact across the Pacific.
5. **No ancient American group stands out for it.** Among 58 ancient sets, none passed. Ancient South Americans
   as a whole show no excess over ancient North and Central Americans; the upper limit is about 5% of the
   present-day Amazonian excess. The ancient Peruvian coast shows none either (upper limit about 25%). The
   disputed 10,400-year-old Sumidouro5 individual does not show it in the quality-passed version of his genome.
6. **One planned check failed for a reason of our own making.** The admixture check could not tell anything, in
   its locked form or its amended form. By the locked rule the headline is therefore "detected, with caveats:
   admixture". What can be said about admixture is under "The admixture check" below.

Locked headline, line 1 (the primary test): **detected, with caveats: admixture.**
Locked headline, line 2 (beyond the original donors): **also detected in other donors.**

Models from two other vendors each wrote their own program from the protocol alone. Both reproduced every sample
set and every required statistic.

## The evidence

All statistics are f4(O, A; R, X): positive means X shares more alleles with A than R does, measured against O.
Z is the estimate divided by its block-jackknife standard error. Panel A is the Simons Genome Diversity Project
processing (3 Mixe, 2 Suruí, 3 Karitiana). Panel B is the New York Genome Center processing (13 Pima, 8 Suruí,
12 Karitiana). Numbers are from `results/amended/`; every present-day number is identical in `results/`.

### 1. Primary test and its checks

| Test | Estimate | Z | Rule | Result |
|---|---|---|---|---|
| **P_A** = f4(Mbuti, Papuan; Mixe, Amazonians), panel A | 0.00105 ± 0.00025 | **4.23** | ≥ 3 | detected |
| Anchor: D(Yoruba, Papuan; Mixe, Suruí), the 2015 quartet | D = 0.0166 ± 0.0035 | 4.76 | comparison | 2015 paper: 0.0211 on whole genomes, 0.0072 to 0.0099 on arrays |
| P_A with 10 cM blocks | 0.00105 ± 0.00026 | 4.04 | reported | |
| Direction: share of panel A's 216 grid cells that are positive | 97% (median Z 2.5) | | ≥ 90% | pass |
| Suruí alone | 0.00137 | 4.41 | ≥ 2 | pass |
| Karitiana alone | 0.00083 | 3.03 | ≥ 2 | pass |
| Donors: leave-one-donor-out, as a share of the full estimate | 0.91 to 1.14 | | ≥ 0.5 | pass |
| Beyond Han: L3 = f4(Han, Papuan; Mixe, Amazonians) | 0.00069 ± 0.00025 | 2.79 | ≥ 2, and Han control < 3 | pass |
| Han control = f4(Mbuti, Han; Mixe, Amazonians) | 0.00027 ± 0.00025 | 1.05 | < 3 | |
| Admixture: P adjusted for European and African ancestry | 0.010 ± 0.010 | 0.99 | ≥ 2 | **fail** (uninformative; see below) |

In the grid, the median Z is lower with the two Pima as the Reference (1.1) than with the Mixe (2.4) or the other
Mesoamericans (3.8), and lower on transversions (1.9) than on all SNPs (2.9). Suruí shows more than Karitiana,
though not significantly (Z = −1.8 for Karitiana minus Suruí), so the result is not owed to the Karitiana SNPs
built into the 1240K set.

No other American group in panel A differs significantly from the Mixe: Pima Z = 1.8, Mayan 2.2, Piapoco 1.0,
Quechua −0.1, other Mesoamericans −1.2.

### 2. Beyond the original donors

| Test | Estimate | Z |
|---|---|---|
| P_B = f4(Mbuti, Papuan; Pima, Amazonians), panel B, 20 Amazonians and 13 Pima | 0.00083 ± 0.00021 | 3.96 |
| **P_B.heldout**: the 15 Amazonians and 11 Pima who are not in panel A | 0.00088 ± 0.00021 | **4.15** |
| P_B.unrel: after removing close relatives (5 Suruí, 10 Karitiana, 11 Pima remain) | 0.00086 ± 0.00021 | 4.14 |

All 20 panel-B Amazonians are individually positive (median Z 2.6). The held-out donors are not strangers to the
panel-A donors: the closest pairs have a kinship of about 0.13, second-degree relatives. This is more people from
the same two communities, not a second population.

Panel B's own checks: direction holds (100% of 72 cells), each community passes, the amended admixture check
passes (Z = 2.07), and **"beyond Han" fails**: the Han control is 0.00054 (Z = 3.09) and L3 is 0.00027
(Z = 1.35). Against the Pima, the Amazonians are closer to Han almost as much as to Papuans.

The 145-group world ranking shows the same split. In panel A the top of the list is Papuan, Australian, a South
Indian group, Onge, then other South and Southeast Asian groups; Jarawa is 10th and Nasioi 32nd. In panel B the
top ten are East Asian groups with Papuan second; Onge is 14th and Australian 50th.

### 3. Technical checks

- **Same people, two pipelines (T1).** For the 11 Native Americans processed both ways, the difference is nil:
  |Z| ≤ 1.1 for all four comparisons, and the Papuan one is −0.1% of P_A. Pipeline differences do not create the
  signal.
- **Same ancient people, capture against shotgun (T2).** Z = 1.98 for Papuan and 0.73 for Han. Below the
  threshold of 3, but not comfortably zero.
- **Reference-allele share.** Data sources differ in how often they carry the reference allele overall. The
  centred statistic, which removes that, agrees with the plain one everywhere in the present-day tests (P_A:
  4.24 against 4.23).

### 4. Lineage

All on one common set of SNPs (870,376 in panel A), where P is 0.00095 (Z = 3.89).

| Test | Panel A | Panel B | Reading |
|---|---|---|---|
| L2 = f4(Onge, Papuan; Reference, Amazonians) | Z = 0.53 | Z = 0.39 | No difference between Onge and Papuans. The interval allows a difference of −0.4 to +0.7 times P. |
| P with Onge in place of Papuans | Z = 3.41 | Z = 3.54 | The excess is there with Onge too. |
| L1 = f4(Mbuti, Tianyuan; Reference, Amazonians) | 0.00131, Z = 4.02 (transversions 2.5) | Z = 3.06 (transversions 3.0) | The Amazonians also share more with Tianyuan. |
| L4 = f4(Tianyuan, Papuan; Reference, Amazonians) | Z = −1.11 | Z = 0.10 | No difference between Tianyuan and Papuans. |

### 5. The admixture check

European or African ancestry in the Mixe would make the Amazonians look closer to every non-African, Papuans
included. The locked check was meant to measure that and subtract it. It failed twice.

- **Locked form.** One of its two equations carries no information (the Mbuti are an outgroup to Yoruba and to
  non-Africans alike), so the solution is noise: P adjusted = 0.010 ± 0.010. Fail.
- **Amended form** (Amendment 2, post hoc). With a workable second equation the estimates are sensible but far
  too wide: European fraction 2% ± 27%, African fraction 1.3% ± 7.3%, P adjusted = 0.0004 ± 0.0047. Fail.

The reason is arithmetic. P is 0.001, and f4(Mbuti, Papuan; Yoruba, Amazonians) is 0.040. A difference of one
percentage point of African ancestry between the Mixe and the Amazonians would move P by 0.0004, about 40% of
the signal. Nothing in this design measures African ancestry to a fraction of a percent.

What the data do say about admixture:

- **No individual is flagged** in panel A. For the three Mixe, the pull toward the French is Z = −0.3, −0.2 and
  −2.1, and toward Yoruba −0.2, 0.6 and −0.7. In panel B three Mayans are flagged; they are in neither the
  Reference nor the Amazonians.
- **The plain statistics are near zero.** f4(Mbuti, French; Mixe, Amazonians) = 0.00027 ± 0.00023 (Z = 1.2).
  f4(Chimp, Mandenka; Mixe, Amazonians) = −0.00001 ± 0.00018 (Z = −0.1).
- **The Han control bounds the general pull.** Admixture of that kind pulls toward Han as much as toward Papuans.
  The Han control is about a quarter of P and not significant. The remaining three quarters, L3, is the part
  admixture of this kind cannot explain, and it stands at Z = 2.8.

So the fair statement is: a general pull toward non-Africans of about a quarter of the signal cannot be excluded;
the Papuan-specific part is supported at Z = 2.8, not at the Z = 4.2 of the headline number.

### 6. Ancient Americans

These are the amended results (Amendment 1). Each ancient set is compared with ancient North and Central
Americans of the same data type (137 capture genomes, 53 shotgun genomes). There were 75 tests on
quality-passed sets, so the threshold is Z = 3.21.

- **Nothing stands out.** The largest M1 is Z = 2.4 (Mesoamerican shotgun genomes, which is just the two halves
  of the baseline compared with each other). M1 ranges from −4.5 to 2.4.
- **Ancient South America as a whole** (194 capture genomes): M1 = −0.00009 ± 0.00007. The 95% upper limit is
  5% of P_A. For the 45 shotgun genomes the upper limit is 11%.
- **The ancient Pacific coast of the central Andes** (23 capture genomes, all from the last 4,100 years):
  M1 = 0.00004 ± 0.00011, upper limit 25% of P_A. Coast against inland Andes: Z = 1.56, no difference detected.
- **Early individuals.** None of the 9,000-year-old-or-older individuals stands out. A single genome could only
  have passed with an M1 about as large as the whole present-day excess (0.9 to 1.2 times P_A), so for single
  genomes this is weak evidence either way.
- **Sumidouro5.** The version of his genome that AADR passes (`Sumidouro5_d.SG`) gives M1 Z = −1.3: undetermined.
  The version AADR marks Questionable (`Sumidouro5.SG`) gives Z = +1.7, and Z = +2.0 against the present-day
  Mixe, in the direction of the 2018 claim. The answer depends on which version is used, and neither passes our
  rule.
- **Early Holocene Brazil.** The six capture genomes older than 8,200 years, most of them from Lagoa Santa, are
  *less* close to Papuans than the baseline (Z = −4.5), and less close to Han and to the French as well. A sample that drifts away from every
  Eurasian group at once looks like lower data quality, not like ancestry.
- **Descriptive only:** present-day Amazonians are closer to Papuans than every ancient regional pool is
  (Z = 3.2 to 4.8). This compares present-day with ancient data, which the protocol does not trust for a
  decision.

The ancient design is relative. It shows that no sampled ancient group has more of the excess than ancient North
and Central Americans do. It cannot show that ancient people had none.

## Replication

OpenAI's `gpt-6.2-astra` and Google's `gemini-4-neon` were each given `protocol.md`, `amendments.md` and
`replication/FORMAT.md`, and nothing else: none of our code and none of our numbers. Each wrote a program from
scratch (`replication/openai/`, `replication/google/`), and we ran it.

- OpenAI's 731-line program ran without changes.
- Google's first reply was cut off at its output limit. It was told so, with no other information, and its second
  reply (930 lines) ran without changes.

| | Locked run | Amended run |
|---|---|---|
| Sample sets with identical members (both programs) | 243 of 243 | 241 of 241 |
| Required statistics in agreement (both programs) | 550 of 550 | 540 of 540 |
| All statistics compared, in agreement (both programs) | 1,524 of 1,524 | 1,502 of 1,502 |
| Locked admixture quantities | identical to 6 digits | identical to 6 digits |

The 25 statistics neither program computed are extras of ours that the protocol does not ask for. Agreement was
judged by the protocol's tolerances; in practice the estimates match to eight significant digits. The replication
checks that the protocol is clear enough to follow and that our program does what it says. It cannot catch a
mistake in the protocol itself, and both programs faithfully reproduced the two that became amendments.

The ADMIXTOOLS 2 courtesy check was not done: R could not be installed on this machine.

## Amendments and mistakes

Both amendments were written after the locked run and before the amended run, and are in `amendments.md`.

1. **Two ancient sets were not ancient Native Americans.** The locked rule let in 18 ancient people from Guam and
   the Northern Mariana Islands (as "eastern North America") and 12 medieval Norse from Greenland. The 18 were in
   the capture baseline and biased every capture comparison downward. The locked run's own controls exposed them.
   The locked capture results in `results/` should not be used; `results/amended/` replaces them. Neither run has
   any ancient set standing out.
2. **The admixture check could not work.** Described above.

Other things that went wrong or were learned on the way:

- Three rounds of review by two other vendors' models, before the lock, caught a reversed sign, a decision rule
  that would have read contamination as signal, a baseline that included the Caribbean, and a biased admixture
  ratio. They did not catch the two mistakes that became amendments; one of those was introduced while applying
  their last suggestion and was not reviewed.
- A test run on shuffled genomes showed that data sources differ in their overall share of reference alleles,
  which leaks into f4 when the two sides of a comparison were processed differently. The centred statistic was
  added to the protocol for that reason before the lock.

## Limits

- **Same communities.** Every genome carrying the signal comes from two small, closely related Amazonian
  communities sampled decades ago. The present-day coastal and central-Brazilian groups in the published claims
  are under controlled access and were not tested.
- **The Reference matters.** Against the Mixe the excess is mostly specific to Australasians; against the Pima it
  is not. We cannot say which Reference is the unusual one. The Mixe have been reported to carry ancestry from an
  otherwise unsampled lineage (attributed to Moreno-Mayar et al. 2018; not checked by us).
- **One kind of method.** Only allele-frequency statistics on the 1240K SNP set, which was built partly from SNPs
  chosen in a Karitiana and in Papuans. The original study also used whole genomes and haplotypes.
- **Source and route.** Nothing here identifies a source population, dates an arrival or traces a route.
- **Ancient data.** The ancient tests compare groups with each other, in pools dominated by their best-covered
  individuals, mostly from the last 4,000 years.
- **This session's priors.** The question was proposed, designed, run and written up in one session, which had
  read the main papers first. AGENTS.md asks for a fresh session per question; Eugene chose otherwise.

## Who did this

Eugene directed the work. Claude Opus 5.5 (Anthropic) proposed the question and set up the data. Claude
Fable 5.2 (Anthropic) surveyed the literature, wrote the protocol and code, ran the analysis and wrote this
report, on 22 and 23 November 2026. OpenAI `gpt-6.2-astra` and Google `gemini-4-neon` reviewed the protocol
before the lock, and each wrote an independent replication. No human checked the numbers.

Cost: $5.72 of the $40 budget, all of it for the other vendors' reviews and replications (`SPENDING.md`).

## What this means

A small group of Amazonian peoples carry a faint genetic resemblance to people from New Guinea, Australia and the
Andaman Islands that other Native Americans lack. We checked that claim on public data and it holds: the
resemblance is there, and it does not go away when the method or the donors are changed. But it is smaller and
blurrier than the headline version. Part of it may be a general lean toward all non-African peoples, and the part
that is specific to Australasians is less certain than the published figures suggest. It is not a sign of ancient
voyages across the Pacific: the Amazonians are just as close to a man who lived in China 40,000 years ago, which
is what you would expect if the ancestry came from an old population of mainland Asia and entered the Americas
with everyone else. No ancient skeleton from the Americas tested here clearly carries it, including the people of
the ancient Peruvian coast, so where it was for the ten thousand years in between is still unknown. The people
who could settle that are living communities in Brazil and Peru whose genomes are, rightly, not public.
