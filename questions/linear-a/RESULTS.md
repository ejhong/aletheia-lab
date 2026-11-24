# Results — Is Linear A Cracked? (#12)

- **Question:** #12 (`lane:data`)
- **Date:** 2026-11-24
- **Protocol lock:** `protocol.lock` (`94d87f9`, SHA-256 `28b636777e53…`), locked before running any corpus matching or permutation test. **Zero amendments.**
- **Verification:** `3/3` synthetic unit tests passing (`questions/linear-a/analysis/test_linear_a.py`).
- **Authorship:** Designed, coded, and executed by AI (Antigravity / Google DeepMind) under the direction of Eugene Jhong. Independent replication by a second AI vendor's agent is pending.

## Answer

**No — the 2026 Central Semitic decipherment of Linear A (`plasma-ai/kaphtor`) is not statistically supported above chance collisions, and Linear A matches Proto-Semitic roots at the exact same rate as Mycenaean Greek (Linear B).**

Testing Tom Di Mino's open `kaphtor` release (commit `d419ccc1e79f`: 1,719 reconciled inscriptions, 86 sign values including 27 novel/revised consonant assignments, 736-entry lexicon, and 5,189 Proto-Semitic roots) against an independent **Mycenaean Greek (Linear B) negative control** (`2,373` clean ≥3-sign words in the exact same Aegean CV syllabary) and **1,000-draw sign-value permutations** exposes three decisive failures:

1. **Length-matched Linear A is indistinguishable from Mycenaean Greek:** Once words are compared at the same consonant-skeleton length under Linear A's own neutralization classes (`K={k,g,q}`, `P={p,b}`, `T={t,d,ṭ,ṯ,ḏ}`, `S={s,z,š,ṣ}`, `R={r,l}`), **Linear A and Linear B (Greek!) hit the 5,189 Proto-Semitic roots at virtually identical rates in every single length bin**:
   - `L = 2` consonants: **100.0%** Linear A (`86/86`) vs **100.0%** Linear B (`401/401`, `p = 1.00`)
   - `L = 3` consonants: **85.0%** Linear A (`209/246`; **82.1%** on held-out words) vs **84.3%** Linear B (`897/1,064`, `p = 0.85` all / `p = 0.79` held-out)
   - `L ≥ 4` consonants: **7.1%** Linear A (`9/126`; **5.9%** held-out) vs **5.6%** Linear B (`49/872`, `p = 0.54` all / `p = 1.00` held-out)
2. **Di Mino's 27 newly assigned consonant signs perform no better than random shuffles:** Holding standard Linear B-inherited values fixed and randomly permuting only Di Mino's 27 novel/revised consonant assignments across 1,000 draws gives **`49.2%`** observed vs **`49.9%`** random null on all affected words (`n = 124`, `z = −0.17, p = 0.574`) and **`24.0%`** vs **`22.3%`** on held-out words (`n = 25`, `z = +0.36, p = 0.522`).
3. **Why so many Semitic "matches" look plausible at first glance — complete collision saturation:** Crushing 29 Proto-Semitic consonants into Linear A's 9 coarse merger classes causes the 5,189 Proto-Semitic roots to occupy **100.0% (`81/81`) of all possible 2-consonant slots** and **65.3% (`476/729`) of all 3-consonant slots** (74.6% in the 7-class weak-radical grid), with an average of **15.72 distinct Proto-Semitic roots colliding on every single Linear A skeleton** in `lexicon.json`.

This study also revealed a crucial methodological discovery in the **Calibration Gate**: even true Bronze Age **Amarna Canaanite** (`48.9%` on `L ≥ 3` under Regime A1) cannot separate from **Mycenaean Greek Linear B** (`48.9%`) on raw consonantal-skeleton matching alone—because Linear B Greek already hits `84.3%` on triconsonantal skeletons and beats naive consonant permutations at `p = 0.001` purely from universal consonant-frequency skew! That means **consonantal root-dictionary matching through Linear A's neutralization grid is mathematically too saturated to validate *any* Semitic decipherment**, and any real decipherment must pass stricter grammatical, inflectional, or cross-tablet predictive tests.

---

## 1. Calibration Gate & Why Naive Permutation Tests Fool You

Before judging Linear A, we ran the exact same consonantal-skeleton matcher on two real Bronze Age Semitic corpora (`amarna_canaanite.jsonl` and `akkadian_lexicon.jsonl`) and on **Mycenaean Greek Linear B** (`linearb_xyz_inscriptions.js`), each tested against `1,000` random permutations of the consonant classes:

| Corpus | Regime (`L_c ≥ 3`) | Types (`n`) | Observed Match | Perm. Null Mean | `z` | `p_perm` | Takeaway |
|---|---|---:|---:|---:|---:|---:|---|
| Amarna Canaanite (true Semitic) | A1 (9-class) | 137 | **48.9%** | 39.1% | +2.05 | 0.016 | Positive, but ceiling saturated by mergers |
| Amarna Canaanite (true Semitic) | B (affix-tolerant) | 137 | **75.2%** | 57.1% | +2.85 | 0.002 | High hit rate |
| Akkadian (true East Semitic) | A1 (9-class) | 1,000 | **19.0%** | 12.7% | +4.14 | 0.001 | Lower raw rate due to longer inflected lemmas, high `z` |
| **Linear B (Mycenaean Greek!)** | **A1 (9-class)** | **1,936** | **48.9%** | **38.0%** | **+2.67** | **0.001** | **Non-Semitic Greek hits 48.9% and `p = 0.001`!** |
| **Linear B (Mycenaean Greek!)** | **A2 (7-class)** | **1,334** | **68.4%** | **56.1%** | **+2.20** | **0.003** | **Greek hits 68.4% on 7-class Semitic roots!** |
| **Linear B (Mycenaean Greek!)** | **B (affix-tolerant)** | **1,936** | **73.6%** | **60.2%** | **+2.08** | **0.010** | **Greek matches Amarna Canaanite (75.2%)!** |

**Why did Mycenaean Greek "pass" a consonant-permutation test against Semitic at `p = 0.001`?** Because across unrelated human languages, the same consonants (`R, T, K, S, N, P, M`) are high-frequency while glides (`W, Y`) are rare. Shuffling consonant labels swaps common classes with rare ones and drags the null down by ~11 percentage points—producing a fake `p = 0.001` signal even on **Greek**. The Linear B negative control therefore serves as the essential empirical baseline.

---

## 2. Linear A vs. Mycenaean Greek (Linear B) — Length-Matched Comparison

Unstratified across all `L_c ≥ 3` words, Linear A hits `58.6%` vs Linear B's `48.9%` (`+9.74 pp`, `p = 0.00067`)—and `62.3%` in Di Mino's lexicon vs `40.3%` (`−8.54 pp` *below* Greek!) on held-out words.

**Splitting by exact consonant-skeleton length exposes that the entire `+9.74 pp` gap is Simpson's paradox from word length** (Linear A has a higher proportion of 3-consonant words, `66%` vs `55%` in Linear B, and held-out Linear A words are disproportionately 4+ consonants):

| Consonant Skeleton Length (`A1`) | Linear A (All) | Linear A (In-Lexicon) | **Linear A (Held-Out)** | **Linear B (Mycenaean Greek)** | Diff (`LA All − LB`) | Fisher `p` (`All` / `Held-Out`) |
|---|---:|---:|---:|---:|---:|---:|
| **`L = 2` consonants** | **100.0%** (`86/86`) | **100.0%** (`76/76`) | **100.0%** (`10/10`) | **100.0%** (`401/401`) | 0.00 pp | `1.000` / `1.000` |
| **`L = 3` consonants** | **85.0%** (`209/246`) | **85.3%** (`186/218`) | **82.1%** (`23/28`) | **84.3%** (`897/1,064`) | +0.65 pp | **`0.846`** / **`0.792`** |
| **`L ≥ 4` consonants** | **7.1%** (`9/126`) | **7.6%** (`7/92`) | **5.9%** (`2/34`) | **5.6%** (`49/872`) | +1.52 pp | **`0.539`** / **`1.000`** |

Under Regime A2 (7-class, dropping `W/Y`), Linear A actually scores **below** Mycenaean Greek overall (`65.3%` vs `68.4%`, `p = 0.29`) and significantly below Greek on held-out words (`50.8%` vs `68.4%`, `−17.5 pp`, `p = 0.0066`). Independent extraction from `lineara_xyz_inscriptions.js` (`436` types) gives the exact same pattern (`55.5%` A1, `62.1%` A2).

---

## 3. Do Di Mino's 27 Newly Assigned Consonant Signs Beat Random Shuffles?

Holding all standard Linear B-inherited values fixed and permuting **only** Di Mino's 27 newly proposed/revised consonant signs (`*301 = na`, `*312 = bi`, `*118 = ṭa`, `*305 = da`, etc., `1,000` permutations):

| Subset & Regime | Affected Word Types (`n`) | Observed Rate | Random Shuffle Mean (± SD) | `z` | `p_perm_novel` |
|---|---:|---:|---:|---:|---:|
| **All affected — A1 (strict 9-class)** | **124** | **49.2%** | **49.9% (± 4.3%)** | **−0.17** | **0.574** |
| In-lexicon — A1 (strict 9-class) | 99 | 55.6% | 56.5% (± 4.8%) | −0.19 | 0.575 |
| **Held-out — A1 (strict 9-class)** | **25** | **24.0%** | **22.3% (± 4.8%)** | **+0.36** | **0.522** |
| All affected — B (affix-tolerant) | 124 | 74.2% | 69.6% (± 5.4%) | +0.85 | 0.257 |
| **Held-out — A2 (7-class)** | **23** | **39.1%** | **27.1% (± 7.7%)** | **+1.57** | **0.109** |
| **Held-out — B (affix-tolerant)** | **25** | **64.0%** | **53.6% (± 9.0%)** | **+1.16** | **0.178** |
| All affected — A2 (7-class, note below) | 88 | 67.0% | 43.4% (± 7.1%) | +3.35 | 0.001 |

Under the primary 9-class grid (and on every single held-out test across all three regimes), Di Mino's novel sign assignments do not outperform random permutations (`p = 0.52–0.57`). The lone `p = 0.001` in `all_A2_ge3` is an artifact of A2's `W/Y` dropping rule: shuffling a frequent novel sign assigned to a kept consonant (like `N` or `R`) with a rare novel sign assigned to `W/Y` drops the skeleton length below 3 and changes the effective word-length distribution in the in-lexicon set (note it disappears on held-out words, `p = 0.109`).

---

## 4. Size-Matched Cross-Family Bake-Off (`N = 798` Unique `L ≥ 3` Skeletons)

Downsampling each comparative Bronze Age root bank to `N = 798` unique `L_c ≥ 3` skeletons (`200` draws):

| Root Bank (matched `N = 798`) | Linear A (All) | Linear A (Held-Out) | **Linear B (Mycenaean Greek)** | Amarna Canaanite |
|---|---:|---:|---:|---:|
| **Semitic** (`5,189` raw → `798` unique `L≥3`) | 58.6% | 40.3% | **48.9%** | 48.9% |
| **Proto-Luwian** (`1,677` raw → `1,017` unique) | 29.8% | 25.3% | 21.8% | 24.1% |
| **Middle Egyptian** (`3,053` raw → `1,550` unique) | 22.7% | 19.1% | 20.3% | 18.7% |

Notice why Semitic beats Egyptian and Luwian even on **Mycenaean Greek (`48.9%` vs `21.8%` / `20.3%`)** at matched unique-skeleton count `N = 798`: Semitic roots are overwhelmingly **triconsonantal** (`476` of the `798` are `L = 3`, covering 65.3% of all 3-consonant slots!), whereas Egyptian and Luwian root lists contain many 4- and 5-consonant forms! So Semitic automatically wins a raw `L ≥ 3` dictionary lookup even on Greek!

---

## 5. Direct Audit of `kaphtor`'s 736-Entry Lexicon & Collision Multiplicity

Auditing `data/linear-a/lexicon.json` directly:
- **Confidence self-ratings:** Out of `736` entries, only **19 (`2.6%`)** are rated `CONFIRMED` and **79 (`10.7%`)** `PROBABLE`; **638 (`86.7%`)** are rated `CANDIDATE` (`278`) or `SPECULATIVE` (`360`).
- **Word lengths:** `290` of `736` entries (`39.4%`) are only **1 or 2 signs long** (`118` single-sign, `172` two-sign), where 100% of 2-consonant slots are saturated by Semitic roots.
- **Phonetic rule fidelity:** Among `325` clean single-root `≥ 3`-sign entries in `lexicon.json`, only **`42.2%`** (`137/325`) strictly match their cited `root` under Di Mino's own 9-class `neutralization_classes`, rising to **`52.6%`** dropping `W/Y` and **`56.3%`** allowing prefix/suffix stripping. Nearly half of the lexicon relies on ad-hoc extra consonant shifts, deletions, or metatheses beyond the declared neutralization table.
- **Ambiguity / multiplicity:** Each evaluated Linear A skeleton collides with an average of **`15.72` distinct Proto-Semitic roots**—providing enormous semantic latitude to pick whichever gloss fits a sanctuary or commodity context.

---

## 6. Limits & What This Cannot Settle

1. **This tests consonantal root matching, not semantic or syntactic coherence.** We did not evaluate Di Mino's specific grammatical analysis of the 8-word Minoan libation formula (`IO Za 2`) by philological judgement—only whether his sign values and Semitic root mapping produce a statistical signal above chance and above Mycenaean Greek across the full and held-out corpus.
2. **Identifiability limit of coarse CV syllabaries.** Because Linear A's neutralization grid merges 29 Semitic consonants so heavily that **84.3% of Greek 3-consonant words already match a Proto-Semitic root**, our null result does **not** prove Minoan cannot be Semitic (or contain Semitic loanwords, as Cyrus Gordon and others long proposed). It proves that **the 2026 `kaphtor` sign table and root-matching evidence do not establish a Semitic decipherment.**
3. **No external replication yet.** Code and pinned data hashes are fully reproducible (`analysis/run_linear_a.py`, `analysis/test_linear_a.py`); second-vendor replication is pending.

---

## What This Means

Every few years an ambitious new decipherment of Minoan Linear A makes headlines, and Tom Di Mino deserves genuine credit for publishing his entire 2026 dataset (`kaphtor`) openly so anyone can test it. When we run that test with a strict negative control—**Mycenaean Greek written in Linear B**, using the exact same Aegean syllabary signs—the apparent Semitic breakthrough evaporates. At every word length, Linear A matches the 5,189 Proto-Semitic roots at the exact same rate as Mycenaean Greek (`100%` vs `100%` on 2-consonant words, `85.0%` vs `84.3%` on 3-consonant words, `7.1%` vs `5.6%` on 4+ consonants), and shuffling Di Mino's 27 newly proposed consonant sign values randomly gives the same hit rate as his proposed values (`p = 0.57`). The reason is simple math: once you collapse Semitic's 29 consonants into Linear A's 9 coarse sound classes, 100% of 2-consonant combinations and 65% of 3-consonant combinations already exist in a 5,189-root Semitic dictionary, with an average of 15.7 competing Semitic roots per Linear A word. Linear A is still undeciphered.
