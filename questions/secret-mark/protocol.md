# Protocol — Secret Mark: Authorship Stylometry and Pastiche Audit (#15)

- **Issue:** #15 (`lane:data`)
- **Aletheia link:** `TIK-C012`
- **Date:** 2026-11-24
- **Budget:** $0 (publicly licensed Greek text corpora, local Python computation)

## 1. Exact Question

Does the Greek text of the Mar Saba *Letter to Theodore* (discovered and published by Morton Smith, 1958/1973) exhibit the quantitative stylometric signature of:
1. **Authentic Clement of Alexandria** (late 2nd / early 3rd century CE),
2. **A late-antique / non-Clementine patristic author or forgery** (3rd–5th century CE, including Origen, Eusebius, Athanasius, Epiphanius, Gregory of Nazianzus, Theodoret, or Cyril of Alexandria), or
3. **An imitative lexical pastiche / modern forgery** (diverging from Clement on unconscious style while over-packing rare or distinctive Clementine vocabulary as hypothesized by Criddle 1995 and Carlson 2005, and/or stitching the quoted *Secret Mark* pericopes as a verbatim Markan cento)?

### Honest scope limitation on Morton Smith's own Greek

Issue #15 asks to test the letter "against Clement, and against Smith's own Greek." An inventory of open-access digital Greek repositories confirms that **no public digital corpus of continuous Ancient Greek prose composed by Morton Smith exists** (Smith's published scholarship is overwhelmingly in English, with one brief 1960 Greek manuscript inventory in *Nea Sion* 52 written in print-only modern Katharevousa catalog entries rather than literary Koine prose). Rather than substituting unverified text, this protocol tests the modern-forgery / Morton Smith hoax hypothesis via **corpus-independent structural predictions** that do not require a Smith Greek corpus:
- **Unconscious-style mismatch** against authentic Clement (function words and character n-grams), calibrated on held-out Clement (*Quis dives salvetur*, *Eclogae propheticae*) and known ancient forgeries (Pseudo-Athanasius, Pseudo-Ignatius, 2 Clement);
- **"Hyper-Clementine" lexical packing** (Criddle 1995 rare-to-common Clement word ratio and smoothed log-odds Clement-distinctive vocabulary density);
- **Layer B "Markan cento" verbatim phrase-stitching** in the two quoted *Secret Mark* passages.

## 2. Data and Text Segmentation

All 38 comparison/control files (1,749,008 Greek tokens) and both scholarly editions of the Mar Saba letter are catalogued with pinned URLs, licences, and SHA-256 hashes in [`MANIFEST.md`](MANIFEST.md).

### 2.1 Uniform Greek normalization

Every text (Mar Saba letter and all 38 corpus files) undergoes the identical normalization pipeline:
1. Strip TEI editorial apparatus/notes/headers (`note`, `head`, `label`, `bibl`, `ref`, `pb`, `lb`, `milestone`, `num`).
2. Lowercase, Unicode NFD decomposition, remove all combining diacritical marks (accents, breathings, iota subscripts), map final sigma `ς → σ`.
3. Tokenize words on `[α-ω]+`.

Diacritic stripping eliminates editorial convention differences across 19th/20th-century editions (e.g., Stählin GCS vs. Migne vs. Smith 1973 vs. SBLGNT).

### 2.2 Target text segmentation (Mar Saba Letter)

The Greek text is extracted programmatically from A.K.M. Adam's 2018 Study Edition (`akma_SecretMark.pdf`, collating Morton Smith [MS], Pantuck/Viklund [PV], and Agamemnon Tselikas [AT]), with PDF Type 1 ligatures (`m → γγ`, `v → λλ`, Latin `Kαλῶς → Καλῶς`, `µ → μ`) repaired and cross-verified word-for-word against Khazarzar's transcription of Smith 1973 (`khazarzar_secmark.htm`).
- **Excluded heading:** Folio I.1 scribal superscription (`εκ των επιστολων ... θεοδωρω`, 9 tokens).
- **Layer A (`mar_saba_clement_frame`):** Epistolary prose spoken in Clement's voice, excluding the heading, the three brief canonical Mark anchor citations (`ησαν δε εν τη οδω ... αναστησεται`, `και προσεπορευοντο ... ιωαννησ`, `και ερχεται εισ ιεριχω`), and the two *Secret Mark* quotations. Exact length `L_A` (~530–540 tokens).
- **Sensitivity variants for Layer A:**
  - `mar_saba_full_no_heading` (~732 tokens, entire letter body minus heading),
  - `mar_saba_clement_frame_AT` (substituting Agamemnon Tselikas's documented paleographic readings from Adam's apparatus: `επιστομισαι`, `λεγουσιν`, `το`, `τα ταυτου`, `δοξα`, `γυμνω`, `γυμνοι`).
- **Layer B (`secret_mark_quotes`):** Concatenation of the two quoted *Secret Mark* passages:
  1. Bethany raising of the rich youth (`και ερχονται εισ βηθανιαν ... εισ το περαν του ιορδανου`, ~149 tokens);
  2. Jericho snippet (`και ησαν εκει η αδελφη ... ουκ απεδεξατο αυτασ ο ιησουσ`, ~22 tokens).
  Total length `L_B` (~171 tokens); Bethany passage also tested alone.

### 2.3 Author corpora and calibration controls (14-author panel + 4 control sets)

- **Target author (training):** Clement of Alexandria (`Protrepticus`, `Paedagogus`, `Stromata` 1–8; 242,694 tokens).
- **Held-out authentic Clement positive controls (excluded from training during evaluation):**
  - `Quis dives salvetur` (9,200 tokens — short homily on Mark 10:17–31, same biblical pericope as Secret Mark),
  - `Eclogae propheticae` (5,002 tokens — short miscellaneous treatise).
- **Known mixed-voice control:** `Excerpta ex Theodoto` (7,553 tokens — Clement excerpting Valentinian Gnostic text).
- **13 comparison authors spanning 1st–5th c. CE:** Philo of Alexandria (1c), Justin Martyr (2c), Athenagoras (2c), Theophilus of Antioch (2c), Tatian (2c), Hippolytus (3c, anti-heretical), Origen (3c, Alexandrian), Eusebius of Caesarea (4c), Athanasius of Alexandria (4c, Alexandrian), Epiphanius of Salamis (4c, anti-Carpocratian *Panarion*), Gregory of Nazianzus (4c), Theodoret of Cyrus (5c), Cyril of Alexandria (5c, Alexandrian).
- **Known ancient forgery / pseudepigrapha controls (tested against their claimed authors):**
  - Pseudo-Athanasius (`Oratio IV contra Arianos [Sp.]`) vs. genuine Athanasius;
  - Pseudo-Ignatius (`Epistulae interpolatae et suppositiciae`) vs. genuine Ignatius;
  - 2 Clement (`Epistula II ad Corinthios`) vs. 1 Clement.
- **Canonical Gospels (SBLGNT):** Matthew, Mark, Luke, John (for Layer B).

All texts are partitioned into non-overlapping chunks of exact token length `L_A` (for Layer A tests) or `L_B` (for Layer B tests). To prevent corpus-size imbalance in supervised training, author training sets are capped at 40 evenly spaced non-overlapping chunks per author (all available chunks used when an author has fewer than 40; fixed random seed `20261124`).

## 3. Pre-Registered Statistical Tests

### Test 0 — Calibration Gate (Controls)
Before interpreting the Mar Saba results, measure:
1. 5-fold cross-validation macro-F1 across the 14 authors on `L_A`-token chunks;
2. Recall on held-out authentic Clement (`Quis dives salvetur` and `Eclogae propheticae`) when Clement is trained solely on `Protrepticus`, `Paedagogus`, and `Stromata`;
3. False-positive rejection rate on the three known historical forgery controls (Pseudo-Athanasius vs. Athanasius, Pseudo-Ignatius vs. Ignatius, 2 Clement vs. 1 Clement) and mixed-voice `Excerpta ex Theodoto`.

### Test 1 — Unconscious-Style Attribution of Layer A (4 Independent Methods)
Evaluate `mar_saba_clement_frame` (exact length `L_A`) across the 14-author panel using four independent stylometric methods designed to emphasize unconscious stylistic habits over topical content words:
1. **Cosine Delta — Function Words (MFW-150):** Evert et al. (2017) Cosine Delta (cosine distance of corpus-standardized z-score vectors) on the top 150 most frequent words across the balanced 14-author training corpus (articles, particles, prepositions, conjunctions, pronouns).
2. **Cosine Delta — Character 3–4-grams (C34-500):** Cosine Delta on the top 500 character 3- and 4-grams (with word-boundary spaces preserved, capturing Greek inflectional morphology, particle clusters, and clausulae).
3. **General Imposters (Koppel & Winter 2014):** 500 bootstrap iterations; each iteration draws a random 50% feature subset from combined MFW-150 + C34-500 z-scored features and a random imposter chunk from each of the 13 non-Clement authors plus one random Clement chunk, scoring how often the Clement chunk is strictly closer (Cosine distance) to `mar_saba_clement_frame` than all 13 imposters. Compute the exact Imposters score `GI(Clement)` and calibrate its 95% specificity threshold on held-out `Quis dives` chunks vs. non-Clement chunks. Also compute `GI(Author)` for every one of the 14 authors.
4. **L2-Regularized Logistic Regression (TF-IDF):** Multinomial logistic regression (`C=1.0`, balanced class weights) on L2-normalized TF-IDF of MFW-150 word unigrams + top 1,000 character 3–4-grams, reporting predicted probabilities across all 14 authors.

### Test 2 — One-Class "Inside Authentic Clement?" Self-Distance Test
Using Clement's training centroid (`Protrepticus`, `Paedagogus`, `Stromata`, computed from MFW-150 and C34-500 separately and combined), compute the empirical distribution of Cosine Delta distances from all authentic Clement `L_A`-token chunks (`N ≥ 400`, leave-one-chunk-out for training chunks, plus held-out `Quis dives` and `Eclogae`). Compute the exact percentile rank and empirical tail p-value of `mar_saba_clement_frame`. Benchmark against how far known ancient forgeries (Pseudo-Athanasius from Athanasius, Pseudo-Ignatius from Ignatius) sit from their claimed authors.

### Test 3 — "Hyper-Clementine" Lexical Packing & Criddle (1995) Rare-Word Ratio Test
Directly test the Criddle (1995) / Carlson (2005) modern-pastiche hypothesis (that a forger consulting Stählin's Clement lexicon packs in anomalously many rare or Clement-specific words):
- **3a. Clement-Distinctive Content-Word Density (Monroe et al. 2008 Log-Odds):** Exclude the top 150 MFW function words. Compute Dirichlet-smoothed log-odds (`alpha_0 = 500`) of every remaining word type in Clement's training corpus vs. the pooled 13 comparison authors. For `mar_saba_clement_frame` and for every authentic Clement `L_A`-token chunk (leave-one-chunk-out on training + held-out `Quis dives` and `Eclogae`), compute:
  - Mean Clement log-odds score across content tokens,
  - Fraction of content word types with log-odds `z > +2.0` ("strongly Clement-distinctive vocabulary").
  Report z-score and two-sided empirical p-value of `mar_saba_clement_frame` against authentic Clement chunks.
- **3b. Criddle Rare-to-Common Clement Word Ratio:** Using Clement's training corpus (`Protrepticus` + `Paedagogus` + `Stromata`), classify every unique content word type (excluding top 150 MFW) in a test chunk into:
  - `C1`: appears **exactly once** (hapax legomenon) in Clement's reference corpus,
  - `C2+`: appears **≥ 2 times** in Clement's reference corpus,
  - `C0`: appears **0 times** in Clement's reference corpus,
  - `C_excl`: appears in Clement's reference corpus and **0 times** across all 13 comparison authors.
  Compute `R_criddle = C1 / (C1 + C2+)` (the rare-word fraction among Clement-attested words, mirroring Criddle 1995's 1-occurrence vs. multi-occurrence diagnostic) and `F_excl = C_excl / N_unique_content` for `mar_saba_clement_frame` against the empirical distribution of authentic held-out Clement chunks (`Quis dives`, `Eclogae`) and leave-one-chunk-out `Protrepticus`/`Paedagogus`/`Stromata` chunks.

### Test 4 — Late-Antique / Origenian Forgery Check
Examine the full 14-author rankings across all four methods in Test 1, specifically checking Origen (3rd c. Alexandrian), Eusebius (4th c.), Athanasius (4th c. Alexandrian), Epiphanius (4th c. anti-Carpocratian *Panarion*), Gregory of Nazianzus (4th c.), Theodoret (5th c.), and Cyril of Alexandria (5th c. Alexandrian). Also test whether any non-Clement author's one-class self-distance distribution places `mar_saba_clement_frame` closer (lower percentile) than Clement's own distribution.

### Test 5 — Layer B: *Secret Mark* Quotations vs. Canonical Gospels & Markan "Cento" Test
- **5a. Gospel Stylometry (`L_B ≈ 171` tokens):** Partition Matthew, Mark, Luke, John (SBLGNT), and Clement into non-overlapping `L_B`-token chunks. Evaluate `secret_mark_quotes` (and Bethany alone) via Cosine Delta (MFW-100 and C34-400) and General Imposters (500 iterations) across the 5 candidates (Mark, Matthew, Luke, John, Clement).
- **5b. Verbatim Phrase-Stitching ("Cento") Test:** Compute the fraction of word bigrams and word trigrams in `secret_mark_quotes` that occur verbatim in Canonical Mark (and in Mark ∪ John). Compare against the empirical leave-one-chunk-out distribution of all `L_B`-token chunks of Canonical Mark (excluding each chunk itself from the reference n-gram table). Repeat excluding top-50 function-word-only bigrams ("content-bearing bigrams") to avoid trivial `και ο ιησουσ` inflation. A verbatim pastiche/cento predicts an upper-tail excess (`> 95th percentile` of genuine Markan chunks).

## 4. Pre-Registered Decision Criteria

- **Consistent with authentic Clement of Alexandria:**
  1. Clement ranks #1 across **≥ 3 of 4** unconscious-style methods (Test 1),
  2. `GI(Clement)` exceeds the calibrated 95%-specificity threshold from Test 0,
  3. `mar_saba_clement_frame` sits inside the central 90% (5th–95th percentile) of authentic Clement's one-class self-distance distribution (Test 2), AND
  4. No significant "hyper-Clementine" lexical packing anomaly (`|z| < 2.0` on Test 3a and `p ≥ 0.01` on Test 3b).
- **Consistent with late-antique / non-Clementine patristic forgery:**
  - A non-Clement author ranks #1 across **≥ 3 of 4** methods in Test 1, OR `mar_saba_clement_frame` lies beyond the 95th percentile of authentic Clement self-distances while lying within the 90th percentile of a later patristic author.
- **Consistent with modern / imitative pastiche (Stählin-lexicon forgery / Markan cento):**
  - Layer A diverges from authentic Clement on unconscious style (>95th percentile in Test 2 or fails calibrated Imposters) **while** showing elevated hyper-Clementine lexical packing (`z > +2.0` in Test 3a or upper-tail `p < 0.01` in Test 3b), **and/or** Layer B exhibits >95th-percentile verbatim Markan cento overlap in Test 5b.
- **Inconclusive / Mixed:**
  - Unconscious-style and lexical-packing tests conflict (e.g., authentic-looking unconscious style combined with hyper-Clementine vocabulary, or authentic-looking Clement frame combined with non-Markan/cento Layer B), or short-text variance (~535 tokens) leaves Clement and one or more peers statistically indistinguishable.

## 5. Verification and Reproducibility

- Synthetic unit tests (`analysis/test_stylometry.py`) verifying Greek normalization, chunking, Cosine Delta invariance, Monroe log-odds polarity, and leave-one-out n-gram cento math before interpreting real outputs.
- Fixed PRNG seed (`20261124`) for all sampling and General Imposters iterations.
- All results, metrics, and interactive figure data written to `results/` and summarized in `RESULTS.md`.
