# Secret Mark: Authorship Stylometry and Pastiche Audit — Results

- **Issue:** #15 (`lane:data`)
- **Aletheia link:** `TIK-C012`
- **Protocol locked:** `2026-11-24T16:57:04Z` (`protocol.lock`, SHA-256 `d5d938ba5ad35e091b7a0a21bde70e9eaab800f934f609aba12b7cd8283a46fc`, commit `d3bdd97`)
- **Amendments:** None (zero deviations from locked protocol)
- **Authorship:** Designed, coded, and executed by Antigravity (Google DeepMind) on 2026-11-24, directed by Eugene Jhong. Open to independent second-vendor replication.

## Answer

**Pre-registered verdict: Split / Mixed.** Quantitative stylometry on 1,749,008 Greek tokens across 14 Christian and Alexandrian authors (1st–5th c. CE) and all four Canonical Gospels splits the Mar Saba *Letter to Theodore* sharply between its two layers:

1. **Layer A (Clement's 529-word epistolary frame) is inconclusive for attribution, and refutes the "hyper-Clementine" lexical-packing claim.**
   - Across four pre-registered unconscious-style methods (MFW-150 Cosine Delta, Char 3–4-gram Cosine Delta, General Imposters, and L2 TF-IDF Logistic Regression), Clement of Alexandria ranks **#2 or #3 on every method**—never #1—edged out by 4th–5th century ecclesiastical prose (Theodoret of Cyrus, Eusebius of Caesarea, and Origen).
   - However, calibration on **held-out authentic Clement** (*Quis dives salvetur*, a short homily on Mark 10) reveals severe cross-genre variance at 529 words: *Quis dives* itself achieves only 5.9%–23.5% top-1 recall and sits at the **97.6th percentile** of Clement's training centroid—*farther* from Clement than the Mar Saba letter (**88.6th percentile**, the lowest one-class percentile of any of the 14 authors).
   - Crucially, the famous Criddle (1995) / Carlson (2005) modern-forgery argument—that the letter is "hyper-Clementine" because a forger packed it using Stählin's lexicon—**fails completely** on empirical calibration against 484 length-matched authentic Clement chunks. The Mar Saba frame's rare-to-common Clement word ratio (`R_criddle = 0.139`) sits dead center of authentic Clement (`0.133 ± 0.036`, `z = +0.17, p = 0.765`), and its Clement-distinctive log-odds (`−0.327`) match held-out Clement (`−0.408 ± 0.381`, `z = +0.22`) rather than showing excess packing (vs. non-Clement median `−1.665`).
2. **Layer B (the 181-word *Secret Mark* Gospel quotations) shows a striking 100th-percentile Mark+John verbatim "cento" signature.**
   - Every single one of all eight pre-registered verbatim n-gram overlap metrics sits at the **100.0th percentile**—higher than **all 62 of 62** genuine 181-word passages of Canonical Mark (leave-one-chunk-out).
   - **48.6%** of content-bearing bigrams in *Secret Mark* occur verbatim in Canonical Mark (vs. Canonical Mark LOO `28.0% ± 6.2%`, max `40.1%`, **`z = +3.35`**), and **55.6%** occur verbatim in Canonical Mark ∪ John (vs. `34.2% ± 6.3%`, **`z = +3.38`**).
   - **19.0%** of content-bearing trigrams match Canonical Mark verbatim (`37` trigrams; `z = +2.29`) and **25.0%** match Canonical Mark ∪ John (`49` trigrams: `37` Mark + `12` John-only; vs. `12.5% ± 4.3%`, **`z = +2.93`**).
   - This is strong quantitative evidence that the quoted *Secret Mark* passages were composed secondarily by stitching together verbatim Greek phrases from Canonical Mark and John—not an independent early Markan pericope. Whether that Mark+John pastiche was assembled in antiquity (2nd–4th c.) or in the 20th century cannot be settled by stylometry alone.

---

## Detailed Evidence

### Test 0 — Calibration Gate (Known-Authorship & Known-Forgery Controls)

Before inspecting the Mar Saba letter, the 14-author pipeline was calibrated on `L_A = 529`-token non-overlapping chunks (up to 40 evenly spaced chunks per author, fixed seed `20261124`; 6/6 synthetic unit tests passed):

| Benchmark | MFW-150 Delta | C34-500 Delta | TF-IDF LogReg | General Imposters | Notes |
|---|---:|---:|---:|---:|---|
| 14-author 5-fold CV (accuracy / macro-F1) | 74.9% / 0.745 | 73.1% / 0.721 | 78.1% / 0.780 | — | Strong within-corpus separation |
| Held-out authentic Clement: *Quis dives* (`N=17`) | 5.9% recall | 23.5% recall | 17.6% recall | 0.0% top-1 (41.2% > p95 thresh `0.106`) | Short homily shifts sharply from *Stromata* |
| Held-out authentic Clement: *Eclogae* (`N=9`) | 55.6% recall | 33.3% recall | 55.6% recall | 0.0% top-1 (median GI `0.130`) | Closer to *Stromata* register |
| Known mixed-voice: *Excerpta ex Theodoto* (`N=14`) | 14.3% Clem | 7.1% Clem | 28.6% Clem | 7.1% top-1 (median GI `0.075`) | Appropriately degraded |
| Known forgery: **2 Clement vs. 1 Clement** (`N=5`) | — | — | — | — | **80% above p95** (mean 95.6th pct) — caught |
| Known forgery: **Pseudo-Ignatius vs. Ignatius** (`N=36`) | — | — | — | — | **44.4% above p95** (mean 81.0th pct) — partially caught |
| Spurious/disputed: **Pseudo-Athanasius Or. IV** (`N=20`) | 85.0% Ath | 75.0% Ath | 80.0% Ath | 80.0% Ath | Only 5% above p95 (mean 41.0th pct) — **fools stylometry** |

**Calibration lesson:** 529-word Greek stylometry has real resolving power within matching genres, catches crude pseudepigrapha (2 Clement), and partially catches 4th-century interpolations (Pseudo-Ignatius), but (a) suffers steep recall drops across genre boundaries (*Quis dives salvetur*) and (b) can be fooled by an authorially close contemporary imitator (Pseudo-Athanasius *Oratio IV*). Any strong claim from Layer A alone would therefore be unwarranted unless all methods converged cleanly.

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

Every single metric refutes the "hyper-Clementine" Stählin-concordance packing hypothesis: the letter's vocabulary sits right on top of Clement's genuine held-out short treatises (*Quis dives* + *Eclogae*) while remaining decisively more Clementine than non-Clement Fathers (`−0.327` vs. `−1.665`, `18.3%` vs. `10.5%` high-z types, `2.8%` vs. `0.0%` Clement-exclusive types).

### Test 5 — Layer B: *Secret Mark* Quotations (`181` tokens) vs. Canonical Gospels & Markan "Cento" Test

#### 5a. Five-way Gospel + Clement Stylometry (5-fold CV accuracy = `78.0%`, macro-F1 = `0.768`)
- **Cosine Delta (Combined MFW-100 + C34-400):** **#1 Mark (`0.774`)**, #2 John (`0.848`), #3 Matthew (`0.946`), #4 Luke (`1.126`), #5 Clement (`1.233`).
- **General Imposters (500 iters):** **#1 John (`0.328`)**, **#2 Mark (`0.300`)**, #3 Matthew (`0.240`), #4 Luke (`0.116`), #5 Clement (`0.016`). (Bethany passage alone, `157` tokens: Mark `0.308`, John `0.302`.)
- Layer B is written unmistakably in a Mark/John narrative gospel voice—not Clement's own prose style.

#### 5b. Verbatim Phrase-Stitching ("Cento") Test vs. 62 Leave-One-Out Canonical Mark Chunks

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

The 49 verbatim 3-word matches split cleanly into `37` Markan narrative phrases (e.g., `και ερχονται εισ`, `και λεγει αυτω`, `οι δε μαθηται`, `δε μαθηται επετιμησαν`, `τησ θυρασ του`, `θυρασ του μνημειου`, `του μνημειου και`) and `12` Johannine-only phrases (e.g., `ησ ο αδελφοσ`, `ην το μνημειον`, `εκ του μνημειου`, `οπου ην ο`, `η αδελφη του`, `και η μητηρ`). Even compared to Matthew—which famously copied extensively from Mark—*Secret Mark*'s verbatim Markan content-bigram density (`48.6%`) is nearly 19 percentage points higher (`30.1%`).

---

## Limits

1. **No public Morton Smith Greek corpus:** Because no open digital corpus of continuous Ancient Greek literary prose by Morton Smith exists, this study cannot directly classify the text against Smith's own Greek idiolect.
2. **Short-text and genre variance in Layer A:** At 529 words, Clement's own undisputed short homily *Quis dives salvetur* falls farther from Clement's treatise centroid than the Mar Saba letter does, and Pseudo-Athanasius *Oratio IV* fools all four unconscious-style methods—bounding how strongly any 529-word Greek text can be attributed or excluded on style alone.
3. **Dating a cento:** The 100th-percentile Mark+John verbatim phrase-stitching in Layer B strongly points to secondary pastiche composition rather than an independent early Markan pericope, **but** an ancient (2nd–4th c.) apocryphal gospel redactor stitching together Mark and John leaves the same n-gram cento signature as a modern 20th-century forger.
4. **Non-stylometric evidence:** Handwriting/ink paleography of the vanished Mar Saba manuscript (only photographs survive), historical provenance, and theological/patristic content lie outside this stylometric study and belong to the broader Aletheia case (`TIK-C012`).

## What this means

Quantitative Greek stylometry undercuts the simplest claims on both sides of the *Secret Mark* debate. Critics who argued the Mar Saba letter betrays Morton Smith through "hyper-Clementine" vocabulary stuffed from a modern index do not survive an empirical check: the letter's rare-word rate and Clementine vocabulary sit squarely inside authentic Clement's short works. At the same time, the letter's unconscious prose habits do not cleanly single out Clement—4th- and 5th-century Church Fathers edge him out on every attribution test, though 529 words is short enough that genuine short Clementine works also drift. The sharpest positive signal is inside the quoted *Secret Mark* passages themselves: over half of their content two-word phrases and a quarter of their three-word phrases are lifted verbatim from Canonical Mark and John—higher than every single genuine 181-word passage in the Gospel of Mark (`62/62`). Whatever the origin of the letter framing them, the *Secret Mark* excerpts read quantitatively like a secondary Mark-and-John mosaic rather than an independent early Gospel episode.
