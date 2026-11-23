# Amendments

Changes after the lock, dated, each with its reason, written before the changed part runs.

The locked protocol was run once as written on 2026-11-23 (`results/`). The amendment below was written after
seeing those results. The locked results are kept and reported.

## Amendment 1 (2026-11-23): telling "Native American" from "relative of Native Americans"

**What the locked run showed.** 174 people were flagged. On the American side the 15 flagged are the 11 Greenland
Norse and 4 Arctic people. Elsewhere, 159 people were flagged as leaning toward Native Americans. Nearly all are
from Siberia, Mongolia, Xinjiang and the Kazakh steppe: the Altai and Yenisei hunter-gatherers, Chukotka, the
Okhotsk coast, Botai, Okunevo, the Tarim Basin. A few are elsewhere: eight people at Roopkund Lake in India, and
single early farmers in Italy, Spain, Serbia, Romania and Morocco.

**The problem.** The protocol warned that ancient north Eurasians who resemble Native Americans without having
come from America would show as hits "and have to be explained", but it gave no test for telling the two apart.
Native Americans and these Siberian groups share ancestors. A statistic that asks "more like Native Americans
than your neighbours, beyond what five controls predict" cannot distinguish a person with ancestry from America
from a person with more of that shared Siberian ancestry than their neighbours. Reading labels one by one for
159 people would be judgement after the fact.

**The added test.** For every robust hit elsewhere, one more statistic, with a reference for the Siberian
relatives: **SIB** = the tested people labelled `Russia_AltaiKrai_N` or `Russia_AltaiKrai_Eneolithic` (the
best-covered such group in the release; they are themselves among the hits). When the person tested belongs to
SIB, they and everyone at their site are left out of it.

- For a neighbours hit: **T = f4(SIB, NA; P, X)**. Positive means X shares more with Native Americans than with
  the Siberian relatives, compared with X's neighbours.
- For an absolute hit: **T = f4(Mbuti, X; SIB, NA)**. Positive means X is closer to Native Americans than to the
  Siberian relatives.

A hit **points to Native Americans specifically** if T passes the protocol's decision rule (plain Z at least the
threshold, centred estimate at least half the plain one) at the one-sided 5% level, Bonferroni-corrected for the
number of people tested this way. Otherwise it is described as **shared north Eurasian ancestry or an unlike
baseline, not specific to Native Americans**. For a person flagged by both tests, both T's are computed and
either passing counts.

**Checks.** The mislabelled Cuban individual (`CDE003.AG`) is a Native American and must pass. The Chukotka
people may pass: gene flow back across the Bering Strait is published, and passing would be consistent with it.

**What stays the same.** Everything in the locked protocol, its thresholds, and the locked results. This is an
added description of the hits, post hoc. Computed by `analysis/amend.py` into `results/amended/`.

## Amendment 2 (2026-11-23): 219 people the locked code left out of the neighbours test

**What went wrong.** The protocol sorts people into four data types (capture, shotgun, Twist, other) and gives
everyone neighbours "of the same side and data type". The locked code built neighbour pools for the first three
types only, so 219 people of type "other" (mostly merged capture-and-Twist data) got the absolute test but not the
neighbours test. The independent replication followed the protocol's wording, tested them, and its output showed
the difference. The mistake is in our code, not in the protocol.

**Change.** The neighbours test is run for those people exactly as the protocol states, with neighbours of type
"other". The family of tests grows by one for each such person elsewhere and four for each on the American side,
and the threshold is recomputed for the larger family. The fitted control weights are kept from the locked run
(these people were not in the fit). Any original hit that falls below the recomputed threshold is reported. New
hits get the same robustness checks and the Amendment 1 test. Computed by `analysis/amend.py`.

### Amendment 2, revised the same day: rerun the whole scan with those people included

The first version of this amendment kept the control weights from the locked run. That was wrong too: the protocol
fits the controls "over everyone elsewhere with neighbours", which includes these 219 people. The independent
replication, which followed the protocol, got slightly different weights and two more borderline hits for that
reason. So the whole scan is rerun with neighbours for the "other" type, using the locked `scan.py` unchanged on
`analysis/people_amended.tsv` (the locked list plus those neighbour pools). Output goes to `results/corrected/`.
This run is the protocol as written; the locked run in `results/` is kept as it was. Amendment 1's test and the
centre checks are then recomputed on the corrected run.

To make that rerun possible, one line of the locked `scan.py` was changed: in the made-up strangers step, a
recipient whose data type has no donors is now skipped (as the protocol's wording implies) where the locked code
stopped with an error. The change cannot affect the locked run, which had no such recipient.

One smaller departure of our code from the protocol is left as it is and reported: for the American-side
statistics our code uses the SNPs where all four foreign references have data, where the protocol gives each
statistic its own mask.

## Completion, not an amendment (2026-11-23): robustness of the centre statistics

The protocol says a centre statistic counts only if it is robust by the two rules (transversions; second
reference). The locked code computed the centre statistics and not their robustness. `analysis/amend.py` computes
it as the protocol specifies, for every centre statistic past the centre threshold.

## Amendment 3 (2026-11-23): a check on contamination for the standing hit, from her public reads

**Why.** `RESULTS.md` first called contamination a likely cause of the lean of `PIE069.AG` and said nothing in
the public data could test it. Eugene asked why a real anomaly had been set aside. The text has been corrected.
Her sequence reads turn out to be public, so a check is possible. This amendment is written, committed and pushed
before the check is run.

**What has been looked at.** The result of the scan for this person (it is why she is being examined). The
structure of the reads file: 1,390,660 mapped reads, all with mapping quality 30 or more, no duplicates; lengths
30 to 76 bases, median 61, and 25% at the maximum of 76; the two bases at each end masked. `amend3.py check`
reproduces her locked statistic from the release's genotypes (S: Z = 5.65). No statistic has been computed from
the reads.

**Data.** European Nucleotide Archive, study PRJEB62503, run ERR11495483, file `PIE069.A0101.TF1.1_trim2.bam`
(72,916,233 bytes, MD5 `f650805de9dd54b9f41a7549f2c8d0a6` as the archive records it), fetched by
`analysis/fetch_reads.py`.

**The test that cannot be done.** The standard check keeps only reads that carry the chemical damage of old
DNA. In this library the damage survives only in the end bases, and the file masks them. It would need the raw
reads to be mapped afresh, and even then few reads would qualify: a real signal would be expected to reach only
about Z = 2. Not done.

**The test.** DNA from a long-dead person is in short pieces. DNA from a modern person who handled the bone is
mostly in longer ones. A read 76 bases long comes from a piece of 76 bases or more. So:

- *Short* reads: 60 bases or fewer (about half the reads). *Long* reads: exactly 76 (about a quarter). *Middle*:
  61 to 75.
- Alleles: for each of the 1240K autosomal SNPs, take the reads of a class that cover it (base A, C, G or T,
  base quality 30 or more), pick one at random (`numpy.random.default_rng(41)`), and record which of the SNP's
  two alleles it shows; a read showing neither is dropped.
- Statistic: S, exactly as in the corrected run (same neighbours, same fitted weights, same code), computed from
  all reads and from each class. Also reported: the raw lean toward Native Americans, the lean toward Han and
  toward the French, and S on transversions only.

If 3% of the reads were modern contamination sitting mostly among the long reads, about an eighth of the long
class would be contaminant: S would be several times larger in the long class than overall, and near zero in the
short class. If the lean belongs to her own genome, the classes agree.

**Rule, fixed now.** Let E be the estimate of S and Z its Z-score.

| Outcome | Condition |
|---|---|
| The lean is in her short molecules too | E(short) ≥ half of E(all reads), and Z(short) ≥ 2 |
| The lean sits in the long molecules | E(short) < half of E(all reads), and E(long) − E(short) has Z ≥ 2 |
| Inconclusive | anything else |

The Z of the difference uses the root of the summed squared standard errors, which is cautious, since both
classes come from one genome.

**Check on the calls.** Alleles from all reads must agree with the release's genotypes at 98% or more of the SNPs
both cover, and S from all reads must have Z ≥ 4. If not, the outcome is "not testable" and the cause is
reported.

**Expected strength.** Each class covers roughly 100,000 SNPs, against 260,114 in the release. If the lean is
the same in every class, each should reach about Z = 3.5.

**What the test cannot tell.** It separates contamination by long modern molecules from a property of her own
genome. It cannot separate real ancestry from a chance oddity of her genome, since both would show in every
class. It would also miss contamination by modern DNA that was itself broken into short pieces.
