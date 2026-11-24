# Protocol — Is Linear A Cracked? (#12)

- **Issue:** #12 (`lane:data`)
- **Date:** 2026-11-24
- **Budget:** $0 (open CC-BY 4.0 / public corpora; local Python computation)

## 1. Exact Question

Does the 2026 Central Semitic decipherment of Linear A published by Tom Di Mino / Plasma AI (`kaphtor`, commit `d419ccc1e79f`: 86 sign values including 32 novel/revised assignments, 5 consonant neutralization classes, 736-entry lexicon, and 5,189 Proto-Semitic roots) produce a statistically genuine Semitic linguistic signal—above **random consonant/sign permutations**, above a **known non-Semitic language written in the exact same Aegean CV syllabary (Linear B Mycenaean Greek)**, above **size-matched non-Semitic Bronze Age root banks (Egyptian, Luwian)**, and specifically on **held-out Linear A words not included in the author's lexicon**?

## 2. Primary Datasets (`MANIFEST.md`)

1. **`plasma-ai/kaphtor` (`d419ccc1e79f`, CC-BY 4.0 data):**
   - `data/linear-a/corpus.json` (`1,719` reconciled Linear A inscriptions), `sign_values.json` (`86` sign entries + `5` neutralization classes), `lexicon.json` (`736` proposed readings with confidence tiers), `unread_words.json`.
   - `data/semitic-roots/semitic_roots.json` (`5,189` Proto-Semitic roots from SED).
   - Comparative root banks: `egyptian_roots.json` (`3,053`), `luwian_roots.json` (`1,677`), `hattic_roots.json` (`299`), `hurrian_roots.json` (`129`).
   - True Bronze Age Semitic positive controls: `data/contact/amarna_canaanite.jsonl` (`247` syllabic Canaanite glosses from Amarna letters) and `data/contact/akkadian_lexicon.jsonl` (`6,233` East Semitic lemmas).
2. **Independent Epigraphic Cross-Check:** `sigla_database.js` (SigLA) and `lineara_xyz_inscriptions.js` (`lineara.xyz`) to verify Linear A word extraction independently of `kaphtor`.
3. **Aegean CV Syllabary Negative Control:** `mwenge/linearb.xyz` (`84e0b00e`, `LinearBInscriptions.js`) — genuine Mycenaean Greek written in Linear B, sharing the core Aegean CV syllabary phonology (`K, P, T, S, R, M, N, W, Y` neutralizations) while encoding an Indo-European (non-Semitic) language.

## 3. Pre-Registered Projection, Controls, and Tests

### 3.1 Standardized Consonantal Skeleton Projection (Fixed in Advance)
Using `sign_values.json`'s own `neutralization_classes`:
- `K`: `k, g, q` (and labiovelar `qʷ`)
- `P`: `p, b`
- `T`: `t, d, ṭ, ṯ, ḏ`
- `S`: `s, z, š, ṣ, ś, ts, sh`
- `R`: `r, l`
- Unmerged sonorants/glides: `M` (`m`), `N` (`n`), `W` (`w`), `Y` (`j, y`).
- Laryngeals/pharyngeals/glottals (`ʾ, ʕ, ʿ, h, ḥ, ḫ`) and vowels (`a, e, i, o, u`) are treated as weak/unwritten in the core skeleton.

We lock **two strict matching regimes** and **one permissive regime**:
- **Regime A1 (Strict 9-class skeleton `{K, P, T, S, R, M, N, W, Y}`):** Exact ordered match between a word's strong-consonant skeleton (length `L_c ≥ 2` and separately **`L_c ≥ 3`**, the primary discriminator against chance collisions!) and the 9-class consonant skeleton of any root in the target root bank.
- **Regime A2 (Core 7-class skeleton `{K, P, T, S, R, M, N}` — Semitic weak-radical rule):** Same exact ordered match after dropping weak glides `W, Y` in addition to laryngeals/vowels, stratified by skeleton length `L_c = 2` and **`L_c ≥ 3`**.
- **Regime B (Permissive Semitic Affix-Stripping):** Allow stripping at most 1 common Semitic prefix consonant (`M, T, Y, N, S`) or 1 suffix consonant (`T, N, M, Y, W`), requiring the remaining matched root skeleton to have **`≥ 3` consonants** (to measure sensitivity to Semitic morphology without allowing trivial 1–2 consonant matches).

### 3.2 Word Extraction & Held-Out Split
- Extract all complete, unbroken syllabic words (`≥ 3` syllabic signs, no brackets `[` `]`, no pure logograms/numerals) from Linear A (`corpus.json`, cross-checked against `lineara_xyz_inscriptions.js`).
- Partition Linear A complete words into:
  - **In-Lexicon words:** present in `lexicon.json` (stratified by `CONFIRMED`/`PROBABLE` vs. `CANDIDATE`/`SPECULATIVE`).
  - **Held-Out / Unseen words (PRIMARY OUT-OF-SAMPLE TEST):** complete Linear A words (`≥ 3` syllabograms) **NOT** present in `lexicon.json` (including `unread_words.json`).
- Extract all complete syllabic words (`≥ 3` syllabic signs) from **Linear B** (`linearb_xyz_inscriptions.js`) using the exact same word-cleaning and neutralization pipeline.

### 3.3 Calibration Gate (Positive & Negative Controls)
Before judging Linear A, evaluate the exact same matcher (Regimes A1, A2, B on `L_c ≥ 3` skeletons) against `semitic_roots.json` on:
1. **Positive Control 1:** `amarna_canaanite.jsonl` (true Bronze Age Canaanite) — must beat `1,000` random consonant-class permutations (`p < 0.001`) AND exceed Linear B by a large margin (`≥ +15` percentage points on `L_c ≥ 3`).
2. **Positive Control 2:** `akkadian_lexicon.jsonl` (`1,000` distinct lemmas with `L_c ≥ 3`) — must beat `1,000` random consonant-class permutations (`p < 0.001`) AND exceed Linear B (`≥ +15 pp`).
3. **Negative Control:** **Linear B (Mycenaean Greek)** (`L_c ≥ 3` distinct words) — measures the exact empirical false-positive collision floor of an unrelated Aegean CV syllabary language against 5,189 Proto-Semitic roots.

### 3.4 Primary Confirmatory Tests on Linear A
1. **Test 1 — Consonant-Class Permutation Test (`1,000` permutations):** Randomly permute the 9 consonant classes `{K,P,T,S,R,M,N,W,Y}` (preserving word structure and sign-frequency distributions!) on Linear A (`All`, `In-Lexicon`, and **`Held-Out`**) for `L_c ≥ 3` (primary) and `L_c ≥ 2` (secondary), both type-weighted and token-weighted.
2. **Test 2 — Novel Sign-Value Permutation Test (`1,000` permutations):** Hold all standard Linear B-inherited sign values fixed and randomly permute **only Di Mino's 32 novel/revised sign assignments** among their assigned consonant values. Tests directly whether Di Mino's new sign proposals (e.g., `*301 = na`, `*312 = bi`, `*314 = ḥa`, `*118 = ṭa`, etc.) improve Semitic root matching on words containing those signs—both overall and on **held-out words**.
3. **Test 3 — Linear A vs. Linear B (Mycenaean Greek) Head-to-Head:** Length-matched (`L_c = 2, 3, 4+`) comparison of Semitic root match rates between Linear A (full and held-out) and Linear B (two-sided Fisher / chi-square test + difference in percentage points).
4. **Test 4 — Size-Matched Cross-Family Bake-Off:** Compare Linear A (`L_c ≥ 3`, Regime A1 & A2) against `semitic_roots.json` (`5,189`), `egyptian_roots.json` (`3,053`), and `luwian_roots.json` (`1,677`), **both at full dictionary size AND downsampled to matched size `N = 1,500` unique skeletons (`200` draws)** so raw dictionary coverage cannot bias the comparison.
5. **Test 5 — Direct Audit of `lexicon.json` (`736` entries):** Measure the distribution of confidence tiers, word lengths, and what fraction of claimed Semitic readings strictly satisfy Di Mino's own `neutralization_classes` (exact skeleton match vs. requiring extra unmodeled shifts, deletions, or metatheses), plus how many *distinct* Semitic roots match each Linear A skeleton on average (ambiguity / collision multiplicity).

## 4. Pre-Registered Verdict Criteria

- **Supported (Genuine Semitic decipherment signal):** Calibration gate passes (Amarna Canaanite & Akkadian exceed Linear B by `≥ +15 pp` and beat permutation nulls `p < 0.001`), AND on **`L_c ≥ 3` held-out Linear A words** (Regime A1 or A2), Linear A beats consonant-permutation nulls (`p < 0.01`), beats **Linear B** (`p < 0.01`, margin `≥ +5 pp`), AND Di Mino's novel sign assignments outperform random permutations of those signs (`p_perm_novel < 0.01`).
- **Not supported (Indistinguishable from chance collisions / Linear B Greek):** Calibration gate passes decisively, while on **`L_c ≥ 3` held-out Linear A words** (and full corpus), Linear A fails to beat consonant-permutation nulls (`p ≥ 0.05`) OR fails to exceed the **Linear B (Mycenaean Greek)** collision rate, AND novel sign assignments fail to beat random sign permutations (`p_perm_novel ≥ 0.05`).
- **Mixed / Suggestive only:** A genuine statistical excess appears in-lexicon or on `L_c = 2` / permissive Regime B or vs. permutation nulls, but fails on held-out `L_c ≥ 3` words, fails to beat Linear B, or fails size-matched cross-family comparison against Luwian/Egyptian.

## 5. Verification

Synthetic unit tests (`analysis/test_linear_a.py`) verifying exact consonant-skeleton projection, neutralization-class mapping, root-matching under Regimes A1/A2/B, and permutation p-values on planted Semitic vs. random synthetic corpora before inspecting real results.
