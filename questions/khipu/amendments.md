# Amendments — The khipu Rosetta hunt (#13)

## Record added after the spot check — 2026-11-24

Nothing in the program or in `results/` was changed or rerun for this record.

1. **The verdict.** The plan (§4) gives "New internal Rosetta discovery" only if the positive control recovers the
   Puruchuco links "cleanly (`p < 10⁻⁴`)" and a new pair survives `FDR < 0.01` and an individual cord-level audit,
   and gives "Inconclusive / Calibration failure" if the matcher fails to recover known Puruchuco links or the
   permutation false-discovery rate is 0.05 or more. No per-link p-value was computed. Of the three matching pairs
   in the Puruchuco hierarchy (UR063/UR073, UR064/UR068, UR066/UR067), one was recovered at Tier A, one at Tier B
   only, and one was missed; the third link the first report counted (UR078/UR063) is not one of them. Test 2.3
   did not recover the hierarchy. Run at full scale, the study's shuffle gives about 0.5 false Tier A matches per
   scan (FDR about 0.05). The cord-level audit was not done. `RESULTS.md` now reports the plan's "Inconclusive"
   verdict and the copies as exploratory.
2. **The null.** The plan says to permute cord-value vectors across khipus, 1,000 corpus-wide draws. The program
   shuffles values within each khipu and tests 100,000 random pairs. The cluster-sum mode had no null.
3. **Test 2.3** used prefix offsets 0 to 4 only, with 50,000 random triples in place of 500.
4. **"Rosetta-ready"** is defined only in the program.
5. **Analyses added by the spot check, outside the plan:** gapped alignment of the eight pairs; a cord-length test
   for whether two records are one object; the matcher on known pairs and duplicates; two nulls at 40 full scans
   each; the Santa Valley calculation with the split fixed in advance. All are in `spotcheck/` and all are
   exploratory.
