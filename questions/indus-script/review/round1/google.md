<!-- {"vendor": "google", "model": "gemini-4-neon", "utc": "2026-11-28T03:04:16.536651+00:00", "input_tokens": 4151, "output_tokens": 20691, "cost_usd_list_price": 0.3228} -->

### 1. Flaws that could produce a false positive or a false negative

* **Invalid "standard error" over correlated resamples (`must fix`)**
  * The plan scores each list across 100 rounds that reuse the *exact same* 5,679 seals and draw 600 names from the *same* ~650-name list (~92% name overlap per round), then requires the mean to be "more than two standard errors above zero."
  * Because Preprint Tamil passed before the lock with 89/100 rounds > 0 (where $\text{mean}/\text{SD} \approx 1.23 < 2$), the plan is almost certainly computing $\text{SE} = \text{SD}/\sqrt{100} = \text{SD}/10$. Treating 100 heavily overlapping splits of one fixed dataset as 100 independent draws is a statistical error: $\text{SD}/\sqrt{R}$ is only the *Monte Carlo* error of the split mean and shrinks artificially as you increase $R$.
  * Worse, whenever $\ge 80/100$ rounds are positive, $\text{mean}/(\text{SD}/10)$ is typically $\sim 8$, making the `> 2 SE` check almost vacuous and allowing tiny, scientifically meaningless positive biases (e.g., mean = +3 vs. Tamil's +188) to pass (**false positive**).

* **List-size and subsampling-fraction mismatch: 600 of ~650 vs. 600 of 1,125 (`must fix`)**
  * Drawing 600 names from ~650 gives ~92% overlap across rounds, whereas drawing 600 from Preprint Tamil's 1,125 names gives ~53% overlap. Much higher overlap sharply reduces cross-round variance for the new lists—pushing a weak positive score (or a single lucky sign-to-ending coincidence like *kuṭi*) over 80/100 (**false positive**) or pushing a borderline list below 80/100 (**false negative**).
  * Furthermore, because deduplication ("Names with identical parts count once") happens after generation, a compiler targeting "about 650 names" can easily drop below 600 unique names, breaking the 600-name draw altogether.
  * Finally, cutting the REP-1 prompt's target from 1,400 to ~650 gives Fresh Tamil less lexical coverage than the preprint's list (which already dropped from +223 to +188 when subsampled), risking a **false negative** for Fresh Tamil (and a spurious Verdict 6).

* **Huge loophole in the quality checker: `"cannot verify"` is uncapped (`must fix`)**
  * A list is rebuilt only if "more than 5 of either 50 are wrong." Items marked `"cannot verify"` are not penalized at all. If a compiler hallucinates or fabricates obscure Sumerian, Nahuatl, or Hawaiian names and the checker marks 30 of 50 as `"cannot verify"` and 2 as `"wrong"`, the list passes untouched.
  * Because the same model family (`Claude Opus 5.5`) both generates and checks the lists, shared blind spots in obscure historical languages can also pass bad etymologies or bad morpheme splits, biasing controls toward noise (**false negative**) or spurious regularity (**false positive**).

* **Web access during list building creates a direct leakage vector (`must fix`)**
  * The name compiler and checker have live web access. Even without mentioning "Indus," searching for Old Tamil Sangam/Tamil-Brahmi name lists with morpheme splits—or Old Japanese Kojiki/Nihon shoki name lists—could retrieve the Zenodo preprint, its GitHub files, or Harsha G.'s Japanese rebuttal. That could cause a **false positive** for Fresh Tamil or Old Japanese (or contaminate the replication).

* **Single-letter spelling maps into a Tamil/Sanskrit table distort phonology (`must fix`)**
  * The plan describes a fixed *letter* map into a sound table built for Tamil and Sanskrit, while the contest matches candidates by **same first letter** and **sound distance $\le 0.5$**.
  * **False positive risk (phoneme collapse / tiny inventory):** Hawaiian has only 8 consonants plus the glottal stop `ʻ` and simple CV syllables; Old Japanese also has a small consonant inventory. Collapsing unfamiliar phonemes (e.g., Hebrew gutturals/emphatics, Nahuatl `tl/tz/x/ch`, or dropping Hawaiian `ʻ`) inflates accidental homophony and candidate density per sign, raising the odds that a high-frequency sign like jar 740 hooks onto a common name category by sheer collision.
  * **False negative risk (orthographic mismatch & digraphs):** Old Irish orthography is deeply non-phonemic (silent palatalization vowels, silent `fh`, lenition digraphs `bh/mh/dh/gh/th/ch`). A character-by-character letter map will treat digraphs (`th`, `sh`, `tl`, `ph`, `bh`) as two separate sounds and mangle initial letters, destroying genuine sound similarity.

* **Uncontrolled morpheme-splitting granularity and Tamil-designed categories (`should fix`)**
  * The plan notes that Preprint Sanskrit failed largely because 57% of names were unsplit and that the 22 categories were designed on Tamil. Yet nothing ensures comparable splitting across the nine new lists—especially whether obligatory inflectional endings (Greek *-os/-ēs*, Nahuatl absolutive *-tl*, Sumerian *-ak*, Tamil *-aṉ*) are split off as a `grammatical ending` part.
  * If a control splits off an obligatory ending on most names and one common sign matches it, it can score a **false positive**; if a control's naming syntax (e.g., Greek/Old English dithematic modifier+head compounds, or Hebrew verb+theophoric clauses) maps poorly onto the Tamil-derived 22 labels so both parts get the same label or `"other"`, shuffling destroys little category structure, causing a **false negative**.

* **Single generation of Fresh Tamil (`should fix`)**
  * Verdict 5 vs. Verdict 6 hinges entirely on a single 650-name run of Fresh Tamil. Because Tamil's score is heavily driven by one sign (jar 740 -> *kuṭam*/*kuṭi*), if the single translator happens to translate "jar/pot" with a different synonym (e.g., *kalam*, *pāṉai*) rather than *kuṭam*, Fresh Tamil could fail by pure single-translator lexical variance (**false negative** for Tamil).

* **Sumerian is not an unrelated zero-contact control (`should fix`)**
  * Sumerian had documented Bronze Age trade and cultural contact with the Indus cities (see Section 5). If Sumerian happens to pass, the result will be contested as a confounded control rather than an unambiguous false positive.

* **Preprint's calibration check (Verdict 1) is vacuous (`minor`)**
  * Running the identical deterministic `contest.py` on the identical Preprint Tamil list with the identical seeds 0–99 that were already run before the lock cannot fail except via a software bug. It is a regression test, not a statistical calibration.

---

### 2. Decision rules: fairness and validity

* **No minimum effect size in the pass rule; incoherent asymmetry between 1 vs. 2 passing controls (`must fix`)**
  * **From the preprint authors' point of view (unfairly harsh):** A control scoring **+3** in 81/100 rounds (under 2% of Tamil's +188) counts as a full "pass." If two controls get +3 and +4 while Preprint Tamil gets +188 and Fresh Tamil gets +180, Verdict 3 triggers **"Not specific"**—even though Tamil towers over every control by ~50x! Meanwhile, a *single* control scoring **+90** (48% of Tamil) only triggers **"Mixed"** (Verdict 4). Requiring half of Tamil's score for one control to trigger "Not specific," yet requiring *zero* magnitude floor when two controls pass, is logically inconsistent and unfairly vulnerable to any small positive structural artifact in the scoring model.
  * **Also unfair to the preprint authors:** Cutting Fresh Tamil to ~650 names (less than half of REP-1's 1,400 target) and running only one Fresh Tamil draw makes it too easy to land on Verdict 6 ("Rests on the preprint's own Tamil list").

* **Verdict ordering ignores Fresh Tamil in Verdicts 3 & 4, and benchmarks controls against the wrong Tamil list (`must fix`)**
  * **From a sceptic's point of view (too forgiving):**
    1. Verdict 3's "at least half that of the **preprint's** Tamil list" compares a fresh, 650-name control against the hand-crafted 1,125-name list that the plan itself flags as built while developing the readings. If Fresh Tamil passes at +80 and Old Japanese passes at +85 (beating Fresh Tamil!), Verdict 4 still calls it **"Mixed"** because 85 < 188/2 (+94).
    2. If Fresh Tamil **fails** and one control passes weakly (+30), Verdict 4 fires before Verdict 6 and calls the study **"Mixed"**, hiding the fact that an unrelated language beat Fresh Tamil!
    3. Under Verdict 5 (**"Specific"**), if Fresh Tamil passes at +120 and five controls score +70 to +110 in **75–79 of 100 rounds** (just shy of the 80/100 cliff), the plan still declares the contest "Specific" and asserts that "the rebuttal does not reach it." A hard binary threshold with no continuous comparison between Tamil and the controls creates severe cliff artifacts.
    4. Calling one weak pass out of eight "Mixed" ("one could pass by luck") conflates split-level luck with language-level false positives. If 1 of 8 unrelated languages passes at 40% of Tamil's score (e.g., +75, which exceeds Preprint Tamil's +44 without the jar sign), that points to a ~12.5% cross-language false-positive rate—hardly benign "luck."

* **Verdict 3 ignores the magnitude gap between controls and Fresh Tamil (`should fix`)**
  * Even if two controls pass weakly, knowing whether Fresh Tamil passes strongly or fails completely is essential to interpreting *why* (broken specificity at large effects vs. tiny baseline positive drift across all languages). The verdict tree should not short-circuit before evaluating Fresh Tamil.

---

### 3. Ambiguities for an independent programmer

The plan states that `gemini-4-neon` will write its own program *"from this plan alone"* and compare its numbers with yours. As written, an independent programmer could not reproduce `contest.py` or `build_inputs.py` without guessing dozens of critical details:

* **The core contest algorithm is almost completely unspecified (`must fix`)**
  * **Sound distance:** No formula is given (weighted Levenshtein? feature distance? length normalization? exact sound table and cost matrix).
  * **Corpus filtering and direction:** Which rows of `inscriptions.csv` (5,679 rows) are kept? Are duplicates, single-sign texts, or certain object types excluded? Are right-to-left vs. left-to-right texts reversed?
  * **Train/test split & RNG:** Exact RNG implementation (`random.Random(seed)` vs. NumPy), order of random calls (seals first or names first?), and handling of odd counts (`n//2`).
  * **Name model & scoring metric:** Bigram vs. higher-order model, smoothing method and parameters, exact weighting between lexical-part bigrams and category bigrams, `<BOS>`/`<EOS>` boundary tokens, log base and scaling factor (to reproduce `+223.0`), and how unread signs are handled in bigrams (skipped/bridged, `<UNK>`, or sequence-breaking).
  * **Optimization procedure:** Independent per-sign argmax vs. iterative coordinate ascent, iteration count, sign update order, tie-breaking rule, and whether two signs may share a reading.
  * **Shuffling control:** Whether parts are shuffled globally across names (preserving name lengths) or within names, before or after the 50/50 split, whether labels move with parts or shuffle independently, and how the shuffle RNG is seeded.
  * **Number signs:** Which 8 numbers are requested, which sign IDs in `inscriptions.csv` are treated as number signs, what category label they receive, and whether they are fixed or participate in candidate selection.

* **Subsampling, deduplication, and `< 600` handling (`must fix`)**
  * Are the 600 names per round drawn **with or without replacement**? What happens if a list has **fewer than 600 unique names** after deduplication?
  * Are duplicates ("Names with identical parts count once") detected before or after applying the spelling map, and before or after drawing the 50-name check sample?

* **Statistical definitions (`must fix`)**
  * Whether "standard error" is `sd / sqrt(100)` (`ddof=1` or `ddof=0`) or `sd`, and whether "above zero" is strictly `> 0` or `>= 0`.

* **Checker, retry, and spelling-map amendment procedures (`should fix`)**
  * If only the 50 word pairs fail (`> 5 wrong`), is only the translator rebuilt, or the entire pipeline? If only the 50 names fail, is the translator kept?
  * What defines a "word pair" when an English picture word has two native translations (one pair per native word, or one per English word)?
  * For the `> 2%` unlabelled parts retry: how many retries are allowed, and what happens if it still exceeds 2%?
  * When `build_inputs.py` halts on an unmapped letter, what objective rule governs which table character it is mapped to (to avoid ad-hoc post-hoc choices)?

* **Secondary ("Also reported") computations (`minor`)**
  * Whether the no-jar-sign and single-label runs use the 100-round (600-name) protocol or the 10-round full-list protocol.
  * How "the reading chosen for the jar sign" is summarized across 100 rounds (modal reading? frequency table?).
  * Whether "candidate readings a sign," "signs read," and "parts in $\ge 2$ names" are computed on the full list or averaged across rounds, and whether "candidate readings a sign" averages over all 69 signs or only signs with $\ge 1$ candidate.
  * For "which sign's removal costs it most": whether "removal" means leaving the sign unread vs. deleting it from texts, and whether this ablation is run over all 100 rounds or rounds 0–9.

---

### 4. Important missing checks (in order of importance)

1. **Continuous comparison and relative effect-size check (`must fix`)**
   * Report full score distributions (mean, median, SD, IQR, rounds > 0) for all lists and directly compare Fresh Tamil and Preprint Tamil against the 8 controls (e.g., rank of Tamil among the 9 fresh lists, score ratio of top control to Fresh Tamil, and whether any control comes within a pre-specified fraction of Fresh Tamil's score).
2. **Pre-contest list-comparability diagnostics (`must fix`)**
   * Before running `contest.py`, compute and report for every list (including Preprint Tamil/Sanskrit/Akkadian): unique name count, fraction of single-part (unsplit) names, mean parts per name, candidate readings per sign, fraction of distinct raw morphemes colliding under the spelling map, entropy/top-3 share of the 22 category labels (especially `grammatical ending` and `place word`), and checker rates for `ok` / `wrong` / `cannot verify`. This immediately catches broken controls (like Preprint Sanskrit's 57% unsplit names) and spelling-map collapse.
3. **Second independent Fresh Tamil list—and/or a 1,400-name Fresh Tamil list (`should fix`)**
   * Because the list-building sessions have $0 marginal cost under the budget, generating either two independent Fresh Tamil lists (to measure translator/compiler variance) or one Fresh Tamil list at REP-1's original 1,400-name target protects against falsely triggering Verdict 6 due to a single unlucky lexical draw or half-size list.
4. **Permuted-picture-words control (`should fix`)**
   * For any passing list (and both Tamil lists), run one cheap diagnostic where the 69 signs' English picture words are randomly permuted across signs (keeping the real names and labels fixed). If a language still passes when signs have the *wrong* pictures, the score is coming from positional/frequency matching rather than pictorial rebus readings.
5. **Leave-top-sign-out check for *all* passing lists, including Fresh Tamil (`should fix`)**
   * The plan identifies the highest-leverage sign for each passing list; it should also explicitly report whether Fresh Tamil (and any passing control) still passes when its single highest-leverage sign is left unread.
6. **Web-access audit log (`should fix`)**
   * Log all search queries and URLs fetched by the name compiler and checker, and automatically flag/reject any session that accesses the preprint, Zenodo record, GitHub corpus, or rebuttal (or disable web access for the name compiler if feasible).
7. **Fresh Sanskrit control (`minor`)**
   * Running one properly split Fresh Sanskrit list alongside the eight unrelated controls would directly test the plan's pre-lock diagnosis that Preprint Sanskrit failed because 57% of its names were unsplit.

---

### 5. Statements of fact that appear wrong

* **"None [of the eight control languages] has any proposed connection with the Indus cities." (`must fix`, high confidence: >95%)**
  * **Sumerian** is included as Control 6. Mesopotamia/Sumer had well-documented Bronze Age trade and cultural contact with the Indus Valley Civilization (called *Meluhha* in Sumerian texts; Indus seals and weights have been excavated in Sumerian cities such as Ur, Kish, and Lagash, and texts mention Meluhhan interpreters). Moreover, numerous authors (from L. A. Waddell onward, plus modern loanword and Sumerian–Dravidian discussions) have proposed linguistic links between Sumerian and the Indus script/language.
* **"Both name traditions are later than the seals, as the preprint says of its own." (`minor`, high confidence: >95%)**
  * Two errors in one sentence: (1) there are *nine* languages, not two ("both" looks like a leftover edit); (2) **third-millennium Sumerian texts** (~3000–2000 BCE) are *not* later than the Mature Harappan Indus seals (~2600–1900 BCE)—they are contemporaneous with, and in early periods earlier than, the seals.
* **Implied statistical claim that the standard error across 100 overlapping rounds (`SD / sqrt(100)`) is a valid standard error for testing whether a list's score is above zero (`must fix`, high confidence: >95%)**
  * Because the 100 rounds share 100% of the seals and ~92% of the names, `SD / sqrt(100)` only measures Monte Carlo error of the resampling approximation, not statistical uncertainty of the language's score; calling it the list's standard error and applying a `> 2 SE` significance test is statistically invalid.

---

### Three changes I would make first

1. **Overhaul the pass rule, statistics, and verdict tree:** Drop the invalid `mean > 2 * (SD/sqrt(100))` test; add an explicit effect-size floor (anchored to **Fresh Tamil** as well as Preprint Tamil) and a continuous cross-language comparison so tiny positive biases (+3) cannot trigger "Not specific" while near-passes (78/100) cannot be ignored as "Specific"; evaluate Fresh Tamil in all verdict branches rather than short-circuiting on Verdicts 3 and 4.
2. **Fix list-building parity, quality gates, and controls before generating lists:** Close the checker's `"cannot verify"` loophole (e.g., require $\ge 40/50$ `ok`), log/restrict web access to block preprint/rebuttal leakage, replace Sumerian with a genuinely zero-contact language, handle `< 600` deduplicated names explicitly (or raise the list target so all lists match the sampling fraction and Fresh Tamil is tested at REP-1's full scale / with a second replicate), and upgrade the spelling maps from single letters to grapheme/phoneme-aware mappings with pre-contest collision diagnostics.
3. **Write a complete algorithmic specification of `contest.py` and `build_inputs.py` into the locked plan (or attach a formal spec):** Document the exact sound table, distance metric, corpus filter, RNG seeding, bigram model, smoothing, optimization loop, shuffling procedure, and number-sign rules so that `gemini-4-neon`'s independent replication is actually well-defined from the plan and input files alone.
