---
summary: Computational audit of the 2026 Central Semitic decipherment of Linear A (kaphtor) against Mycenaean Greek Linear B and sign-value permutations; no statistical Semitic signal above chance collisions.
verdict: Not supported — Linear A matches Semitic roots at the exact same rate as Mycenaean Greek
result: Once 29 Semitic consonants are collapsed into Linear A's 9 coarse sound classes, 5,189 Proto-Semitic roots occupy 100% of 2-consonant slots and 65% of 3-consonant slots, causing Mycenaean Greek (Linear B) to match Semitic roots 84.3% of the time on 3-consonant words. Linear A hits 85.0% overall (p = 0.85 vs Greek) and 82.1% on held-out words (p = 0.79), while randomly shuffling the decipherment's 27 newly proposed consonant sign values gives the exact same match rate (p = 0.57).
dek: In 2026 an open-source project (kaphtor) claimed to decipher Minoan Linear A as a Central Semitic language. Does the mapping survive held-out words, sign permutations, and a Mycenaean Greek control?
updated: 2026-11-24
---

{{figure: linear-a/tiles}}

## The claim

In June–October 2026, AI engineer Tom Di Mino (with Plasma AI) released `kaphtor`, an open CC-BY 4.0 record of **1,719 Linear A inscriptions** paired with a proposed **Central Semitic decipherment**: 86 sign values (including 27 newly proposed or revised consonant assignments), 5 consonant neutralization classes, a 736-entry lexicon, and a bank of 5,189 Proto-Semitic roots.

Because the entire dataset is open, we locked a pre-registered statistical test before running a single comparison: pass Linear A through Di Mino's exact neutralization grid (`K={k,g,q}`, `P={p,b}`, `T={t,d,ṭ,ṯ,ḏ}`, `S={s,z,š,ṣ}`, `R={r,l}`, plus `M, N, W, Y`), split out **held-out words not in his lexicon**, randomly permute his **27 newly assigned consonant signs**, and run the **exact same Semitic matcher on Linear B (Mycenaean Greek)** — an unrelated Indo-European language written in the exact same Aegean CV syllabary.

## What we found

**Linear A is statistically indistinguishable from Mycenaean Greek at every word length.**

At first glance, across all clean words with ≥ 3 consonants, Linear A matches Proto-Semitic roots at `58.6%` vs `48.9%` for Linear B. That gap turns out to be **100% Simpson's paradox from word length** (Linear A has a higher share of 3-consonant words than Linear B). Stratifying by exact consonant-skeleton length wipes the difference out completely:

- **2 consonants (`L = 2`):** **100.0%** Linear A (`86/86`) vs **100.0%** Mycenaean Greek (`401/401`, `p = 1.00`).
- **3 consonants (`L = 3`):** **85.0%** Linear A all (`209/246`) and **82.1%** Linear A held-out (`23/28`) vs **84.3%** Mycenaean Greek (`897/1,064`, `p = 0.85` all / `p = 0.79` held-out).
- **4+ consonants (`L ≥ 4`):** **7.1%** Linear A all (`9/126`) and **5.9%** Linear A held-out (`2/34`) vs **5.6%** Mycenaean Greek (`49/872`, `p = 0.54` all / `p = 1.00` held-out).

Holding all standard Linear B-inherited signs fixed and **randomly shuffling only Di Mino's 27 newly assigned consonant signs** (`1,000` permutations) produces **`49.9%`** mean matches vs **`49.2%`** observed (`z = −0.17, p = 0.574`) on all affected words, and **`22.3%`** vs **`24.0%`** on held-out words (`p = 0.522`).

{{figure: linear-a/length_and_novel_signs}}

## Why so many "Semitic matches" appear anyway

The calibration gate also caught a crucial statistical trap: **even Mycenaean Greek "passes" a naive consonant-permutation test against Semitic roots at `p = 0.001`** (`48.9%` vs `38.0%` shuffled), because unrelated languages share universal consonant-frequency rankings (`R, T, K, S, N, P, M` common; `W, Y` rare). Worse, once 29 Proto-Semitic consonants are merged into Linear A's 9 coarse syllabic classes, the 5,189-root dictionary saturates the phonetic space:

{{figure: linear-a/collision_audit}}

Every 2-consonant string in any language is guaranteed to match a Semitic root (`81/81`), two-thirds of all 3-consonant strings are occupied (`476/729`, hitting `84.3%` of real Mycenaean Greek triconsonantal words), and the average Linear A skeleton in `lexicon.json` collides with **15.7 distinct Proto-Semitic roots**. Meanwhile, `86.7%` of the 736 lexicon entries are self-rated `CANDIDATE` or `SPECULATIVE`, and only `42.2%` of clean single-root ≥3-sign entries strictly satisfy the stated 9-class neutralization rules without extra ad-hoc shifts or deletions.

## What this does not settle

- **Whether Minoan could still be Semitic or hold Semitic loanwords.** Because coarse CV-syllabary consonant mergers saturate a 5,189-root dictionary so thoroughly that even true Bronze Age Amarna Canaanite (`48.9%`) does not separate from Mycenaean Greek (`48.9%`) on raw skeleton lookup alone, a null here does not disprove a Semitic affiliation—it shows that root-dictionary matching cannot prove one.
- **Philological reading of the libation formula.** A genuine decipherment of Linear A will need productive grammatical paradigms, cross-tablet accounting predictions, or blind semantic predictions that survive strict held-out tests.
- **Independent replication.** Code and pinned data hashes are reproducible with zero amendments; second-vendor replication is pending.

Read the full pre-registered [protocol](https://github.com/ejhong/aletheia-lab/blob/main/questions/linear-a/protocol.md) and [results](https://github.com/ejhong/aletheia-lab/blob/main/questions/linear-a/RESULTS.md).
