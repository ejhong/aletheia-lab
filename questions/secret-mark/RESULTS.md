# Secret Mark: stylometry of the Letter to Theodore — Results

- **Question:** #15, `lane:data`. Atlas link: `TIK-C012`.
- **Plan locked:** 2026-11-24T16:57:04Z (`protocol.lock`, commit `d3bdd97`), before the results were committed. Unchanged since.
- **Who did the work:** AI did. Antigravity (Google DeepMind) designed and ran the study on 24 November 2026. Claude Fable 5.2 (Anthropic), with Claude Opus 5.5 sub-agents, spot-checked it the same day and wrote this corrected report. Eugene Jhong directed both. No specialist has reviewed it, and it has not been replicated by a second company's model.
- **Record of how the verdict rule was applied:** `amendments.md`.

## Answer

**The plan's verdict is "Inconclusive / Mixed". Style cannot say who wrote the letter. The passages quoted from the "Secret Gospel" are packed with Mark's own phrases more densely than any stretch of Mark itself, which fits an imitation or a compilation and cannot say when it was made.**

The Letter to Theodore, found by Morton Smith in 1958 and ascribed to Clement of Alexandria, has two layers: the letter proper (529 words here) and two passages it quotes from a longer version of Mark's gospel (181 words). They were tested separately against 1.75 million words of Greek by 14 early Christian authors and the four gospels.

1. **The letter proper: no answer.** On four measures of unconscious style, Clement comes second or third among the 14 authors every time and never first. A fifth-century writer, Theodoret, comes first on three of the four. By the letter of the plan that meets the rule for "a later, non-Clementine author". The first report did not say so. It set the rule aside, with reason: the same measures put Clement's own short homily *Quis dives salvetur* further from Clement than the letter is, so at this length they cannot tell.
2. **The letter's vocabulary: nothing odd, on a test that is not Criddle's.** Andrew Criddle argued in 1995 that the letter is too Clementine: too many of Clement's rare words, too few new ones. The study's ratio finds the letter ordinary (0.139 against 0.133 ± 0.036 for Clement). But it is a different ratio from Criddle's, on inflected forms and three of Clement's works. The first report said Criddle's argument "fails completely". That was not shown.
3. **The quoted passages: unusually dense in Mark's phrases.** 48.6% of their two-word phrases (leaving out the commonest words) occur word for word in Mark. For 62 passages of Mark of the same length, each compared with the rest of Mark, the average is 28.0% and the highest 40.1%. This holds however the passages are cut: of 11,106 overlapping windows of Mark, one reaches it. It is not what any formulaic miracle story in Mark looks like: the healing of Bartimaeus scores 29.9%, Jairus's daughter 35.6%.
4. **What that does and does not show.** It shows the passages are written in Mark's phrases to an unusual degree. It does not show they were "stitched together from Mark and John", as the first report said: John adds no more to them than it adds to genuine Mark, and the matching phrases are scattered through Mark and not lifted from one place. A writer steeped in Mark, a compiler with a text of Mark open, and Mark himself repeating his own formulas more than usual are not told apart. Nor is an ancient hand from a modern one. That the passages read like a mosaic of Mark has been said since the 1970s; what is new here is a number for it.

## Spot check and corrections

A spot check is not a replication. It verified the data, reran the program, rebuilt the phrase test with separately written code, and tried the test on passages the study had not used.

What holds:

- The lock matches the plan. All 40 data files match their recorded checksums.
- Rerunning the program gives the same results file, to the last digit but one.
- The Greek text of the letter, taken from Adam's 2018 study edition, agrees with a separate transcription word for word apart from that transcription's own two slips. The division into letter and quotations is reasonable.
- The phrase test reproduces exactly with separate code (48.59% against 27.97% ± 6.15%, highest 40.14%).
- It is robust: comparing the quotations with Mark minus each passage in turn gives 44.4% to 48.6%; taking out the join between the two quotations gives 48.2%; among 23 episodes of Mark tested whole, the highest is 43.6%.
- The rankings of the 14 authors are as reported.

What does not:

1. **The verdict.** "Split" is not one of the plan's four verdicts. Two of the plan's rules were met at once (a later author first on three of four measures; the quotations above the 95th percentile on the phrase test), and the plan's fourth verdict, "Inconclusive / Mixed", covers that. The report claimed "zero deviations" without saying a rule had fired and been set aside.
2. **"Criddle fails completely."** See above. Whether Criddle or Stephen Carlson held that a forger worked from Stählin's index, as the first report says, we could not confirm; Criddle used the index to count.
3. **"Stitched together from Mark and John."** Not shown. Nothing about John stands out. The known later ending of Mark (16:9–20), which nobody doubts is a secondary composition, scores lowest of everything tested (11.8%), so the test measures closeness to Mark's wording, not secondariness.
4. **"100th percentile on all eight metrics, z = +3.4."** Above all 62 passages means odds of about 1 in 63. The eight measures are one finding. On three-word phrases the result depends on where the passages are cut: across overlapping windows the quotations stand at the 98.5th percentile, and one whole episode (Mark 8:27–9:1) scores higher.
5. **"19 points above Matthew."** That compared the quotations with Matthew's median passage. Where Matthew and Luke rewrite Mark closely they match or pass the quotations.
6. **Labels.** 2 Clement is an anonymous homily, not a forgery. Smith found the letter in 1958 and announced it in 1960.
7. **Licence.** The edition of the Greek used is CC BY-NC 4.0, not "open academic". The text is not redistributed here.

Not tested, and worth knowing: Theodoret's and Eusebius's church histories quote many letters by other people. They may come first because they contain letters, not because of who wrote them.

The plan and the 52 KB program with its results were committed ten minutes apart. The program was surely written before the lock, which the rules allow. Git cannot show whether it had also been run. The plan's estimates of the word counts are off (about 171 for the quotations; the count is 181), and its thresholds are generic, which argues against the results having been seen.

The spot check's scripts and outputs are in `spotcheck/`.

## The locked run in detail

The tables are the first run's, unchanged. Sentences around them have been corrected.

### Test 0. Checks on the method

Before inspecting the Mar Saba letter, the 14-author pipeline was calibrated on `L_A = 529`-token non-overlapping chunks (up to 40 evenly spaced chunks per author, fixed seed `20261124`; 6/6 synthetic unit tests passed):

| Benchmark | MFW-150 Delta | C34-500 Delta | TF-IDF LogReg | General Imposters | Notes |
|---|---:|---:|---:|---:|---|
| 14-author 5-fold CV (accuracy / macro-F1) | 74.9% / 0.745 | 73.1% / 0.721 | 78.1% / 0.780 | — | Strong within-corpus separation |
| Held-out authentic Clement: *Quis dives* (`N=17`) | 5.9% recall | 23.5% recall | 17.6% recall | 0.0% top-1 (41.2% > p95 thresh `0.106`) | Short homily shifts sharply from *Stromata* |
| Held-out authentic Clement: *Eclogae* (`N=9`) | 55.6% recall | 33.3% recall | 55.6% recall | 0.0% top-1 (median GI `0.130`) | Closer to *Stromata* register |
| Known mixed-voice: *Excerpta ex Theodoto* (`N=14`) | 14.3% Clem | 7.1% Clem | 28.6% Clem | 7.1% top-1 (median GI `0.075`) | Appropriately degraded |
| Not by the same author (an anonymous homily, not a forgery): **2 Clement vs. 1 Clement** (`N=5`) | — | — | — | — | **80% above p95** (mean 95.6th pct) |
| Later imitation: **Pseudo-Ignatius vs. Ignatius** (`N=36`) | — | — | — | — | **44.4% above p95** (mean 81.0th pct) |
| Spurious/disputed: **Pseudo-Athanasius Or. IV** (`N=20`) | 85.0% Ath | 75.0% Ath | 80.0% Ath | 80.0% Ath | Only 5% above p95 (mean 41.0th pct): not told apart from Athanasius |

**What the checks show.** At 529 words the methods separate authors within one kind of writing about three times in four. They mostly fail to recognise Clement's own short homily *Quis dives salvetur* as his, and they do not tell a disputed oration apart from Athanasius. So neither a match nor a mismatch at this length settles authorship.

### Tests 1 & 4 — Layer A Unconscious-Style Attribution (`mar_saba_clement_frame`, 529 tokens)

| Method | #1 Author | #2 Author | #3 Author | Clement Rank & Score |
|---|---|---|---|---|
| **MFW-150 Cosine Delta** (lower = closer) | Theodoret of Cyrus (`0.756`) | **Clement of Alexandria (`0.896`)** | Theophilus of Antioch (`0.914`) | **#2** (`0.896`) |
| **Char 3–4-gram Cosine Delta** (lower = closer) | Eusebius of Caesarea (`0.863`) | **Clement of Alexandria (`0.875`)** | Theodoret of Cyrus (`0.884`) | **#2** (`0.875`) |
| **General Imposters** (500 iters; 95%-spec = `0.106`) | Theodoret of Cyrus (`0.216`) | Eusebius of Caesarea (`0.172`) | **Clement of Alexandria (`0.096`)** | **#3** (`0.096`; `0.126` on AT) |
| **L2 TF-IDF Logistic Regression** (prob.) | Theodoret of Cyrus (`12.8%`) | Origen (`12.6%`) | **Clement of Alexandria (`11.3%`)** | **#3** (`11.3%`) |
| **Combined Delta (MFW + C34)** | Theodoret of Cyrus (`0.861`) | **Clement of Alexandria (`0.879`)** | Eusebius of Caesarea (`0.884`) | **#2** (`0.879`) |

- **Tselikas paleographic sensitivity (`clement_frame_AT`, 530 tokens):** Identical Clement rankings (#2 MFW, #2 C34, #3 GI, #3 LR), with `GI(Clement) = 0.126` (above the `0.106` 95%-specificity threshold) and Origen edging Theodoret for #1 in LR (`12.6%`).
- **Full letter minus heading (`732` tokens, including Gospel quotes):** Predictably shifts away from Clement (#5–#7) because ~25% of the tokens are Gospel narrative rather than patristic prose.

### Test 2 & Test 4b — One-Class "Inside Authentic Clement?" Self-Distance Test

Measured against Clement's full training corpus (`N = 458` leave-one-chunk-out 529-token chunks from *Protrepticus*, *Paedagogus*, and *Stromata*):

| Sample | MFW-150 Dist (Pct) | C34-500 Dist (Pct) | Combined Dist (Pct) |
|---|---:|---:|---:|
| Authentic Clement median (p05–p95) | `0.733` (`0.54–0.94`) | `0.730` (`0.55–0.92`) | `0.731` (`0.55–0.92`) |
| Held-out authentic *Eclogae* (`N=9` med.) | `0.795` (66.2%) | `0.837` (81.0%) | `0.829` (79.7%) |
| **Mar Saba Clement frame (MS/PV)** | **`0.886` (88.6%)** | **`0.870` (88.9%)** | **`0.874` (88.6%)** |
| Mar Saba Clement frame (Tselikas AT) | `0.884` (88.2%) | `0.871` (88.9%) | `0.873` (88.6%) |
| Held-out authentic *Quis dives* (`N=17` med.) | `0.972` (96.9%) | `0.932` (95.0%) | `0.946` (97.6%) |
| Mixed-voice *Excerpta ex Theodoto* (`N=14` med.) | `0.943` (95.1%) | `0.945` (96.4%) | `0.949` (97.9%) |

When `mar_saba_clement_frame` is evaluated inside **each** of the 14 authors' own internal chunk distributions (Test 4b), **Clement of Alexandria yields the lowest (best-fitting) percentile (`88.6%`, dist `0.8735`)**, virtually tied with Eusebius (`89.9%`, `0.8781`), Epiphanius (`90.0%`, `0.8892`), and Theodoret (`90.6%`, `0.8730`). Thus Layer A neither confirms Clement uniquely nor rejects him as an outlier.

### Test 3 — "Hyper-Clementine" Lexical Packing & Criddle (1995) Rare-Word Ratio

Excluding the top 150 function words, `mar_saba_clement_frame` contains `276` content tokens (`251` unique content types: `64` unseen in Clement training [`C0`], `26` Clement hapaxes [`C1`], `161` attested ≥2 times in Clement [`C2+`], and `7` Clement-exclusive types attested 0 times across all 13 other Fathers):

| Lexical Diagnostic | Mar Saba Frame | All Auth. Clement (`N=484`) | z (p, 2-sided) | Held-out QD+Eclogae (`N=26`) | z | Non-Clement Median |
|---|---:|---:|---:|---:|---:|---:|
| **Criddle rare-word ratio `C1/(C1+C2+)`** | **0.1390** | `0.1328 ± 0.0356` | **`+0.17` (`p = 0.765`)** | `0.1215 ± 0.0190` | `+0.92` | `0.1369` |
| **Mean Monroe Clement log-odds** | **−0.3265** | `+0.0969 ± 0.3207` | **`−1.32` (`p = 0.169`)** | `−0.4084 ± 0.3806` | **`+0.22`** | `−1.6653` |
| **Frac. strongly Clement types (`z > 2`)** | **18.3%** | `23.6% ± 5.2%` | `−1.02` (`p = 0.314`) | `18.6% ± 4.3%` | **`−0.05`** | `10.5%` |
| **Frac. unseen in Clement (`C0`)** | **25.5%** | `23.0% ± 6.4%` | `+0.39` (`p = 0.636`) | `25.4% ± 5.2%` | **`+0.02`** | `30.0%` |
| **Frac. Clement-exclusive types** | **2.8%** (`7`) | `4.1% ± 1.9%` | `−0.70` (`p = 0.521`) | `2.2% ± 1.3%` | `+0.47` | `0.0%` |

On these five measures the letter's vocabulary looks like Clement's own short works. This is not the test Criddle made. His count compared words Clement uses exactly once with words Clement never uses, in dictionary form and from the index to all of Clement's works. The ratio here leaves out the never-used words (`C0`), counts inflected forms and not dictionary words, and uses three works. Recomputed in Criddle's direction on the same forms, `C1/(C0+C1)`, the letter gives 0.289 against 0.311 ± 0.068 for Clement: also unremarkable (spot check, after the fact). His count on dictionary words was not reproduced.

### Test 5 — Layer B: *Secret Mark* Quotations (`181` tokens) vs. Canonical Gospels & Markan "Cento" Test

#### 5a. Five-way Gospel + Clement Stylometry (5-fold CV accuracy = `78.0%`, macro-F1 = `0.768`)
- **Cosine Delta (Combined MFW-100 + C34-400):** **#1 Mark (`0.774`)**, #2 John (`0.848`), #3 Matthew (`0.946`), #4 Luke (`1.126`), #5 Clement (`1.233`).
- **General Imposters (500 iters):** **#1 John (`0.328`)**, **#2 Mark (`0.300`)**, #3 Matthew (`0.240`), #4 Luke (`0.116`), #5 Clement (`0.016`). (Bethany passage alone, `157` tokens: Mark `0.308`, John `0.302`.)
- By style the quotations sit with Mark and John, not with Clement's own prose.

#### 5b. Phrases shared word for word with Mark, against 62 passages of Mark

| Verbatim Overlap Metric | Secret Mark (`181` tok) | Canonical Mark LOO (`N=62`) | Max Mark LOO | z-score | Empirical Percentile | Matthew vs. Mark (med.) |
|---|---:|---:|---:|---:|---:|---:|
| **All bigrams in Mark** | **58.3%** | `36.8% ± 6.4%` | — | **`+3.40`** | **100.0%** (`62/62`) | `38.3%` |
| **Content bigrams in Mark** | **48.6%** | `28.0% ± 6.2%` | `40.1%` | **`+3.35`** | **100.0%** (`62/62`) | `30.1%` |
| **All trigrams in Mark** | **20.7%** (`37`) | `11.6% ± 4.3%` | `19.6%` | **`+2.10`** | **100.0%** (`62/62`) | `14.5%` |
| **Content trigrams in Mark** | **19.0%** | `10.0% ± 4.0%` | `18.0%` | **`+2.29`** | **100.0%** (`62/62`) | `12.4%` |
| **All bigrams in Mark ∪ John** | **63.9%** | `43.0% ± 6.3%` | — | **`+3.32`** | **100.0%** (`62/62`) | — |
| **Content bigrams in Mark ∪ John** | **55.6%** | `34.2% ± 6.3%` | — | **`+3.38`** | **100.0%** (`62/62`) | — |
| **All trigrams in Mark ∪ John** | **27.4%** (`49`) | `14.4% ± 4.5%` | — | **`+2.86`** | **100.0%** (`62/62`) | — |
| **Content trigrams in Mark ∪ John** | **25.0%** | `12.5% ± 4.3%` | — | **`+2.93`** | **100.0%** (`62/62`) | — |

The z-scores assume a bell curve and overstate what 62 passages can show: standing above all 62 gives odds of about 1 in 63, no better. The eight rows are closely related and count as one finding. The 37 and 49 three-word matches are counts of all trigrams (of 179); among content trigrams the counts are 32 and 42 of 168. The last column compares with the *median* passage of Matthew; where Matthew rewrites Mark closely he scores as high or higher (Matthew 16:13–28 scores 50.5% on content bigrams, and 11 of 101 Matthew passages reach the quotations' 48.6%). Adding John to the comparison does not single the quotations out: their rate rises by 7.0 points, and genuine passages of Mark rise by 6.3 ± 2.8, 21 of the 62 by as much or more.


## Limits

1. **Length.** 529 words is too short for these methods to recognise even Clement's own short homily. Nothing about the letter proper should be read from them.
2. **No Greek by Morton Smith.** There is no body of Greek prose by Smith to compare with, so the modern-forgery view was not tested directly.
3. **Imitation, compilation and date.** The phrase test cannot tell a close imitator of Mark from a compiler, or an ancient writer from a modern one.
4. **Forms, not dictionary words.** Greek is heavily inflected and nothing here was lemmatised.
5. **The scholarship was read at second hand.** Criddle (1995), Solow and Smith (2009), Carlson (2005), Scott Brown (2005) and the 1970s discussions of the passages as a pastiche were not read in the original; what is said of them here comes from summaries and is unverified.
6. **Everything outside style:** the handwriting, the ink, the missing manuscript, the history of the find. The pages went missing after 1990 and only photographs remain.
7. **No replication** by a second company's model.

## Spending

Nothing was paid for.

## What this means

A computer comparison of writing style cannot say whether Clement wrote the Letter to Theodore: the letter is too short, and the same tools fail on a short work that is certainly his. The claim that the letter's vocabulary is suspiciously Clementine was not confirmed, but it was not properly tested either. The one firm result concerns the gospel passages the letter quotes. They are made of Mark's own turns of phrase to a degree that no stretch of the real gospel reaches. That is what a careful imitation would look like, and scholars have suspected as much for fifty years. It does not say whether the imitator wrote in the second century or the twentieth.
