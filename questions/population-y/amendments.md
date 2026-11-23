# Amendments

Changes after the lock, dated, each with its reason, written before the changed part runs.

The locked protocol was run once, as written, on 2026-11-23 (results in `results/`). Both amendments below were
written after seeing those results. They are corrections of mistakes in the locked design, found because the
locked run's own controls behaved impossibly. The locked results are kept and reported beside the amended ones.

## Amendment 1 (2026-11-23): two ancient sets are not ancient Native Americans

**What went wrong.** The locked rule took "ancient Americans" to be everyone whose political entity is in the
Americas. Two groups got in who should not have:

- `REGION.NAM_EAST` (and `CELL.NAM_EAST.LATE`) is 18 ancient people from Guam and the Northern Mariana Islands
  (labels `USA_LateUnai` and `USA_NorthernMariana_Latte_Chamoru`, political entity USA, longitude about +145°).
  The rule "rest of the USA, longitude ≥ −100°" caught them. No ancient person from the eastern United States
  passes the filters, so the region was nothing but these 18.
- `REGION.NORTH` includes 12 medieval Norse from Greenland (labels containing `Norse`).

**How it was noticed.** In the locked run, `REGION.NAM_EAST` had Z(M1) = +7.6, Z(M3) = −12.0 and Z(MF) = −10.7:
far closer to Han and far less close to the French than any Native American group could be. The metadata then
showed who they were. A reviewer had warned about Pacific islands before the lock; the check made then looked for
Hawaii and Rapa Nui only and missed positive longitudes.

**Why it matters.** The 18 Marianas people were part of the capture baseline (18 of 155). They pull the baseline
toward Papuans and East Asians, which pushes M1 down for every capture set tested. The locked capture results in
N are therefore biased and should not be used. Shotgun results are unaffected (none of the 18 is shotgun data).
The Norse affect only the NORTH sets, which are not in the baseline.

**Change.** For the ancient sets only (cells, regions, ANC, early individuals, VER):

1. An individual whose coordinates are given must have a longitude between −170° and −30°. This removes the 18
   Marianas people and one Cuban individual whose longitude is recorded with the wrong sign (`CDE003.AG`).
2. An individual whose group label contains `Norse` is left out.

Everything else in the protocol stays as locked, including every threshold. `REGION.NAM_EAST` no longer exists;
the capture baseline becomes NAM_WEST and MESO (137 people). The amended list is `analysis/sets_amended.tsv`; the
locked `analysis/sets.tsv` is unchanged. The whole analysis is rerun on the amended list into `results/amended/`.
The present-day statistics do not involve these sets and must come out identical; that is checked.

## Amendment 2 (2026-11-23): the locked admixture check cannot work

**What went wrong.** The locked group-level admixture check solves two equations for the European and African
fractions. The second equation uses h(S) = f4(Chimp, Mbuti; Amazon, S). That statistic is close to zero for every
S, including Yoruba, because the Mbuti are an outgroup to Yoruba and non-Africans alike. So the two equations are
nearly the same equation and the solution is numerically meaningless: in the locked run α_eur = −2.0 ± 8.3 and
α_afr = −0.5 ± 2.3, and P_adj = 0.010 ± 0.010 against a P of 0.001. The check fails the locked rule
(Z(P_adj) = 0.99 < 2) because it carries no information, not because admixture was found. The error is this
session's: the reviewers proposed solving jointly, and the choice of h was made here and not reviewed.

**How it was confirmed.** `explore/admixture_terms.py` (exploratory, run after the lock) prints the nine terms:
h(Yoruba) = −0.0009, against g(Yoruba) = −0.036.

**Change.** The locked result stands as reported: the admixture check failed, so the locked headline for the
primary test is "detected, with caveats: admixture". Beside it we report an amended check, which is post hoc:

- Replace h by k(S) = f4(Chimp, Mandenka; Amazon, S), where Mandenka is a second West African group (panel-A or
  panel-B processing to match the panel; label `Mandenka`). k is large for a Yoruba-like source and near zero for
  a French-like one, so the two equations are independent.
- Solve g(Reference) = α_eur·g(French) + α_afr·g(Yoruba) and k(Reference) = α_eur·k(French) + α_afr·k(Yoruba),
  with g as locked, on the common mask of all the sets involved, and compute P_adj as locked.
- Same rule as locked: the amended check passes if Z(P_adj) ≥ 2.
- Also reported, as plain statistics that need no model: f4(Mbuti, French; Reference, Amazon) and
  f4(Chimp, Mandenka; Reference, Amazon). Each is zero if the Reference and the Amazonians do not differ in
  West Eurasian or African affinity.

Computed by `analysis/amend.py` into `results/amended/`.
