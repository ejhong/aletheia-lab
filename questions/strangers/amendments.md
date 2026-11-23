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

## Completion, not an amendment (2026-11-23): robustness of the centre statistics

The protocol says a centre statistic counts only if it is robust by the two rules (transversions; second
reference). The locked code computed the centre statistics and not their robustness. `analysis/amend.py` computes
it as the protocol specifies, for every centre statistic past the centre threshold.
