---
# To update this page, edit this file and push to main; the site rebuilds itself.
# The figures are made by questions/secret-mark/analysis/make_figures.py from the results files.
summary: In 1958, Morton Smith reported finding a Greek letter attributed to Clement of Alexandria quoting two otherwise unknown passages of a "Secret Gospel of Mark." Using 1.75 million Greek tokens across 14 Christian and Alexandrian authors plus all four Canonical Gospels, we tested whether the letter reads like authentic Clement, a late-antique forgery, or a modern lexical pastiche—and whether the Secret Mark quotations read like Mark or a stitched phrase cento.
verdict: Split—epistolary frame inconclusive (no "hyper-Clementine" excess), but Secret Mark quotes show a 100th-percentile Mark+John cento signature
result: On the 529-word epistolary frame (Layer A), Clement of Alexandria ranks #2 or #3—never #1—across all four unconscious-style methods, edged out by 4th–5th century prose (Theodoret, Eusebius, Origen); yet calibration shows Clement's own held-out homily Quis dives salvetur drifts even farther (97.6th vs. 88.6th percentile), and Criddle's famous "hyper-Clementine" rare-word packing hypothesis fails completely (R_criddle z = +0.17, p = 0.765; Monroe log-odds z = +0.22 vs. held-out Clement). Inside the 181-word Secret Mark Gospel excerpts (Layer B), however, verbatim phrase overlap hits the 100th percentile on all eight metrics—exceeding every single genuine 181-word passage in Canonical Mark (62/62), with 55.6% of content bigrams (z = +3.38) and 25.0% of content trigrams (z = +2.93) lifted verbatim from Mark and John.
dek: Testing Clement's Letter to Theodore and the Secret Gospel of Mark against 1.75 million words of patristic and Gospel Greek.
updated: 2026-11-24
---

> **Where things stand, 24 November 2026.** Initial locked run finished with zero amendments (by Antigravity / Google DeepMind, directed by Eugene; open to second-vendor replication). Pre-registered verdict: **Split / Mixed** — Layer A (epistolary frame) is inconclusive for attribution and refutes "hyper-Clementine" lexical packing; Layer B (*Secret Mark* quotes) shows a 100th-percentile Mark+John verbatim cento signature.

{{figure: secret-mark/tiles}}

## Two texts inside one letter

The vanished Mar Saba manuscript (photographed by Morton Smith in 1958 and published in 1973) actually contains **two distinct Greek layers** that have to be tested separately:

1. **Layer A — the epistolary frame (`529` words):** prose in the voice of Clement of Alexandria (ca. 150–215 CE) warning a certain Theodore against Carpocratian corruptions of a "more spiritual" Gospel of Mark.
2. **Layer B — the *Secret Mark* quotations (`181` words):** two verbatim excerpts purporting to come from that longer Gospel—a Bethany story of Jesus raising a rich youth who later visits him at night wearing a linen cloth over his naked body (`157` words), and a brief Jericho snippet (`24` words).

Because no open digital corpus of continuous Ancient Greek literary prose by Morton Smith exists, direct attribution against Smith's own Greek cannot be run from public corpora. Instead, we locked a five-part test on **1,749,008 Greek tokens** across 38 pinned open texts (`First1KGreek`, `PerseusDL`, `SBLGNT`): 14 Greek Christian and Alexandrian authors spanning the 1st–5th centuries CE, three known historical forgery/pseudepigrapha controls, two held-out authentic Clement treatises (*Quis dives salvetur* and *Eclogae propheticae*), and all four Canonical Gospels.

## Layer A: neither clearly Clement nor "hyper-Clementine"

On unconscious prose style (function words and character 3–4-grams), **Clement never finishes first** across the 14 authors—he finishes `#2` on both Cosine Delta metrics and `#3` on General Imposters and L2 Logistic Regression, behind 4th–5th century prose (Theodoret of Cyrus, Eusebius of Caesarea, and Origen). Use the buttons below to inspect all four methods and the one-class self-distance ranking:

{{figure: secret-mark/layer_a_panel}}

Yet our pre-registered calibration gate shows why that does **not** settle Layer A against Clement:
- Within-corpus 14-author 5-fold CV is solid (`73.1%–78.1%`), and the pipeline catches `2 Clement` (`80%` above p95) and partially catches `Pseudo-Ignatius` (`44.4%` above p95).
- **Cross-genre short works drift sharply:** Clement's own undisputed short homily *Quis dives salvetur* (on Mark 10—the exact biblical neighborhood of *Secret Mark*) achieves only `5.9%–23.5%` recall and sits at the **`97.6th` percentile** (`dist = 0.946`) of Clement's training centroid—*farther* from Clement than the Mar Saba letter (`88.6th` percentile, `dist = 0.874`, the lowest one-class percentile of any of the 14 authors).
- **Close ancient imitators can fool short-text stylometry:** `Pseudo-Athanasius Oratio IV` is misattributed to Athanasius `75%–85%` of the time.

Meanwhile, one of the most famous quantitative arguments **for** a Morton Smith hoax—Andrew Criddle's (1995) claim that the letter is "too Clementine" because a forger packed it with rare Clementine vocabulary from Stählin's index—**fails completely** when calibrated empirically against `484` length-matched authentic Clement chunks. Toggle the chart below to compare Layer A's lexical diagnostics against Layer B's Gospel cento test:

{{figure: secret-mark/lexical_and_cento}}

In Layer A, the Criddle rare-to-common ratio (`0.139`) sits dead center of authentic Clement (`0.133 ± 0.036`, `z = +0.17, p = 0.765`), and every vocabulary-distinctiveness metric matches Clement's held-out short works (*Quis dives* + *Eclogae*) almost identically (`mean Monroe log-odds = −0.327` vs. `−0.408 ± 0.381`, `z = +0.22`, compared to `−1.665` for the 13 non-Clement Fathers).

## Layer B: a 100th-percentile Mark+John verbatim cento

Inside the `181`-word *Secret Mark* quotations, the signal is dramatic and unambiguous. On 5-way Gospel+Clement stylometry (`78.0%` CV accuracy), the excerpts split evenly between **Mark** (`GI = 0.300`, `#1` Cosine Delta) and **John** (`GI = 0.328`, `#1` Imposters), with Clement near zero (`GI = 0.016`).

When we measure how often *Secret Mark*'s two- and three-word Greek phrases occur verbatim in Canonical Mark and John—and compare against all **`62` genuine `181`-word passages of Canonical Mark** (strictly leave-one-chunk-out)—*Secret Mark* finishes at the **`100.0th` percentile (`62/62`) on all eight metrics**:

- **Content-bearing bigrams in Canonical Mark:** **`48.6%`** vs. Canonical Mark LOO `28.0% ± 6.2%` (max genuine Mark passage `40.1%`, **`z = +3.35`**) and Matthew `30.1%`.
- **Content-bearing bigrams in Mark ∪ John:** **`55.6%`** vs. Canonical Mark LOO `34.2% ± 6.3%` (**`z = +3.38`**).
- **Content-bearing trigrams in Mark ∪ John:** **`25.0%`** (`49` verbatim 3-word phrases: `37` in Mark + `12` in John-only) vs. Canonical Mark LOO `12.5% ± 4.3%` (**`z = +2.93`**).

## What this means

Quantitative Greek stylometry undercuts the simplest claims on both sides of the *Secret Mark* controversy. The letter's epistolary frame is **not** a clumsily over-packed "hyper-Clementine" Stählin-index pastiche, yet its unconscious prose habits are too short and too close to 4th–5th century ecclesiastical Greek to pin unambiguously on Clement. The quoted *Secret Mark* passages themselves, however, carry the unmistakable statistical signature of a **secondary Mark-and-John mosaic**—lifting verbatim content phrases from Canonical Mark and John at a rate higher than any genuine passage in the Gospel of Mark (`62/62`). Stylometry cannot tell whether that Mark+John cento was stitched together by an ancient sectarian writer before Clement, by a late-antique forger, or by a modern scholar; it does show that *Secret Mark* reads quantitatively like a secondary composition built from Canonical Mark and John rather than an independent early Gospel episode.

::: details Methods, data, and verification
- **Protocol and lock:** `questions/secret-mark/protocol.md`, locked at `2026-11-24T16:57:04Z` (`protocol.lock`, SHA-256 `d5d938ba5ad3`, commit `d3bdd97`). Zero amendments.
- **Public datasets:** 38 pinned open-access Greek corpus files (`OpenGreekAndLatin/First1KGreek`, `PerseusDL/canonical-greekLit`, `morphgnt/sblgnt`; 1,749,008 tokens) plus A.K.M. Adam's 2018 Study Edition (`akma_SecretMark.pdf`) cross-verified against Khazarzar's transcription of Smith 1973. Full URLs, licences, and SHA-256 hashes in `questions/secret-mark/MANIFEST.md`.
- **Full report and code:** `questions/secret-mark/RESULTS.md`, `questions/secret-mark/analysis/run_stylometry.py`, and `questions/secret-mark/analysis/test_stylometry.py` (`6/6` synthetic unit tests passing).
:::
