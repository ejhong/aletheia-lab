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
