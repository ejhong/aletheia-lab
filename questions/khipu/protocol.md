# Protocol — The Khipu Rosetta Hunt (#13)

- **Issue:** #13 (`lane:data`)
- **Date:** 2026-11-24
- **Budget:** $0 (open MIT-licensed Open Khipu Repository SQLite archive; local Python computation)

## 1. Exact Question

Across all **619** Andean khipus (`54,403` cords, `110,677` knots) in the Open Khipu Repository (`khipu.db`):

1. **External Rosetta Audit & Calibration:** When independently decoded from raw knot tables, how strongly does the famous **six-khipu Santa Valley match** (`KH0323`–`KH0328` / `UR087`–`UR092`) fit the **1670 San Pedro de Corongo *revisita*** (`132` tributaries in `6` *pachacas*, `367` pesos tribute), and what is the **exact combinatorial and corpus-wide false-positive rate** of matching a khipu archive's moiety split and numeric totals to a colonial census?
2. **Corpus-Wide Internal Rosetta Hunt (`191,271` khipu pairs):** After verifying blind recovery of Urton & Brezine's (2005, *Science*) **Puruchuco accounting hierarchy** (`ARCHIVE_NUM = 301`) without provenance labels, do systematic sequence-matching and parent–child summation scans across all `619` khipus uncover **previously unlinked numerical copies, mirror khipus, multi-level accounting trees, or provenance matches for the `218` unprovenanced khipus** at false-discovery rate `FDR < 0.01`?
3. **Archival Rosetta-Readiness Census:** Which provenanced khipu archives (`Pachacamac`, `Incahuasi`, `Ica`, `Leymebamba`, `Huaquerones`, `Puruchuco`, `Nazca`, `Santa`, etc.) carry structured multi-group numerical accounts with attachment/color-band metadata capable of supporting new colonial-document matches once archival *revisitas* are digitized?

## 2. Pre-Registered Numerical Decoding Rules

For every level-1 pendant cord (`cord.CORD_LEVEL = 1`, ordered by `cord_cluster.ORDINAL`, `cord.CLUSTER_ORDINAL`, `cord.CORD_ORDINAL`) and subsidiary/top cords (`CORD_LEVEL ≠ 1`):

- **Primary knot-value decoding:** Sum `knot.knot_value_type` across all knots attached to `CORD_ID` (non-null, numeric `> 0`; `110,465 / 110,677` knots = `99.81%` populated in `khipu.db`).
- **Independent Locke (1912) / Ascher cross-check:** On a verification pass, recompute positional base-10 knot values directly from `(TYPE_CODE, NUM_TURNS, cluster ORDINAL/START_POS)` (`L` = `NUM_TURNS` in units `2–9`, `E` = `1` in units, `S` = `1` per knot in `10^k` positions) and log exact agreement rate against `knot.knot_value_type`.
- **Cord vector per khipu:** Ordered integer list `V(k) = [v_1, v_2, ..., v_n]` of level-1 pendant cord values (`0` for unknotted cords), plus `V_nz(k)` (non-zero subsequence) and **cluster-sum vector** `G(k)` (sum of pendant values inside each `cord_cluster`).

## 3. Pre-Registered Statistical Tests & Positive Controls

### Test 1 — Santa Valley 1670 *Revisita* Audit & False-Positive Calibration
1. Independently reconstruct for `PROVENANCE = 'Santa'` (`KH0323`–`KH0328` / `UR087`–`UR092`):
   - Total pendant cords, number of color-banded 6-cord groups (and cluster structure),
   - `R` (recto) vs. `V` (verso) cord/group attachment counts,
   - Sum of first-cord values across groups, sum of all pendant values, and per-moiety (`V` vs. `R`) tribute distributions.
2. **Combinatorial Moiety Partition Null (`N = 20,000` Monte Carlo draws):**
   - Draw `6` random positive integer *pachaca* sizes summing to `130` (under both uniform simplex/Dirichlet(`1,...,1`) and empirical overdispersed Dirichlet(`0.5,...,0.5`)).
   - Over all `10 = C(6,3)/2` three-vs-three moiety partitions, measure how often the best partition matches an arbitrary `(70, 63)` target within `L1 ≤ 5` (Medrano & Urton 2018: `71/59`, `|71-70|+|59-63|=5`) and `L1 ≤ 3` (FitzPatrick 2024: `68/62`, `|68-70|+|62-63|=3`), AND how often `min_partition |S_1 - 70|` is `≤ 2`.
3. **Corpus-Wide Spurious Bundle Calibration:** Sample `10,000` random 6-khipu subsets (and single khipus) from the non-Santa OKR corpus and record the probability of matching an arbitrary `(132 ± 5%, 367 ± 30%)` pair of count + sum targets by pure numerical chance.

### Test 2 — Corpus-Wide Internal Rosetta Hunt (`C(619, 2) = 191,271` Pairs)
1. **Positive Control Gate (Blind Puruchuco Recovery):**
   - Without supplying `ARCHIVE_NUM` or `PROVENANCE`, scan all `191,271` khipu pairs for **contiguous sequence matches** (both forward and reversed reading orientation):
     - Require `≥ 6` aligned positions (in full pendant vector `V` or cluster-sum vector `G`) containing **`≥ 4` distinct non-zero integer values** and **sum `≥ 20`** (filtering trivial all-1s/all-0s or tiny counting cords).
     - Score exact match fraction `f_exact`, near match fraction `f_near` (`|a - b| ≤ max(1, 0.02 * max(a,b))`), and normalized L1 discrepancy `err_L1 = Σ|a_i - b_i| / Σ max(a_i, b_i)`.
     - Declare a **Copy / Mirror Candidate** when `L ≥ 6`, `n_distinct_nz ≥ 4`, `f_near ≥ 0.85`, and `err_L1 ≤ 0.05` (tier A: exact/near-exact `err_L1 ≤ 0.02` & `L ≥ 8` or `L ≥ 6` exact; tier B: strong partial `err_L1 ≤ 0.05`).
   - **Gate requirement:** Must blindly recover known Urton & Brezine (2005) Puruchuco pair links (`ARCHIVE_NUM = 301`) with `p < 10⁻⁴` vs. permutation null.
2. **Permutation Null & Discovery Audit (All 619 Khipus):**
   - Permute cord-value vectors across khipus (`1,000` corpus-wide random draws preserving length distribution) to compute exact expected false-positive counts at both Tier A and Tier B thresholds (`FDR < 0.01`).
   - Classify every surviving pair as: (i) known Puruchuco archive link, (ii) existing `DUPLICATE_ID` link in `khipu_main`, (iii) **novel same-provenance link**, (iv) **novel cross-provenance link**, or (v) **novel provenance link connecting an unprovenanced (`''`/`unknown`) khipu to a provenanced archive**.
3. **Cross-Khipu Parent–Child Summation Hunt (Generalizing Puruchuco):**
   - For every khipu `P` with `≥ 6` non-zero pendants (`≥ 4` distinct values, max value `≥ 10`), search within-archive (and among top-correlated global candidates) for `2`-child (`C_1 + C_2 ≈ P`) and `3`-child (`C_1 + C_2 + C_3 ≈ P`) element-wise aligned sums over contiguous windows of length `L ≥ 6` satisfying `err_L1 ≤ 0.02` and `f_near ≥ 0.90`, with every child contributing `≥ 10%` of the parent sum (excluding trivial `P + 0 = P`).
   - Calibrate against `500` random-triple null trials to compute exact false-positive rates, verify recovery of the known Puruchuco 3-level hierarchy, and report every novel non-Puruchuco summation tree!

### Test 3 — Rosetta-Readiness Census Across All 619 Khipus
- Tabulate by provenance: total khipus, khipus with `≥ 10` knotted pendants, median/max pendant sum, presence of repeated equal-size cord clusters (banding), and presence of mixed `R`/`V` attachments (`≥ 10%` minority type) — quantifying what fraction of the world's public khipu corpus is structurally ready for archival *revisita* matching.

## 4. Pre-Registered Verdict Criteria

- **New Internal Rosetta Discovery + Calibrated Santa Audit:** Positive control recovers Puruchuco links cleanly (`p < 10⁻⁴`), AND `≥ 1` previously unlinked non-Puruchuco copy/mirror pair, unprovenanced-to-provenanced match, or parent–child accounting hierarchy survives `FDR < 0.01` and individual cord-level audit.
- **Null beyond Puruchuco / Santa:** Positive control recovers Puruchuco cleanly, while zero previously unlinked khipu pairs or summation hierarchies survive `FDR < 0.01` outside Puruchuco and existing `DUPLICATE_ID` entries.
- **Inconclusive / Calibration Failure:** Automated matcher fails to recover known Puruchuco links or has high permutation false-positive rate (`FDR ≥ 0.05`).

## 5. Verification

Synthetic unit tests (`analysis/test_khipu.py`) testing (1) Locke/Ascher base-10 knot decoding vs `knot_value_type`, (2) forward & reversed sequence-copy recovery on planted synthetic khipus, (3) 2-child and 3-child summation hierarchy recovery while rejecting trivial `P + 0 = P` and all-1s vectors, and (4) exact combinatorial moiety-partition counting before running on `khipu.db`.
