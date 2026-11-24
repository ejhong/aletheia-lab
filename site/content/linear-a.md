---
# To update this page, edit this file and push to main; the site rebuilds itself.
# The figures are made by questions/linear-a/analysis/make_figures.py from the results file.
summary: Linear A, the script of Minoan Crete, has never been read. In 2026 Tom di Mino published an open dataset and a proposal that it writes a Semitic language. We tested whether Linear A words, read his way, match Semitic roots more often than Greek words do.
verdict: Cannot tell; the test does not separate Semitic from Greek
result: Read with the proposal's sound values, Linear A words match Semitic roots as often as Mycenaean Greek words do (85% and 84% at three consonants). But Hebrew and Canaanite words score the same (86% and 84%), so the test cannot tell a Semitic language from Greek, and the plan's own check on the method failed. The first report's verdict of "not supported" is withdrawn. The proposal's author had already written that this kind of matching is not evidence; his main evidence was not tested.
dek: A 2026 proposal reads Minoan Linear A as a Semitic language. A test of it by matching words to Semitic roots, and why that test cannot decide.
updated: 2026-11-24
---

> **Where things stand, 24 November 2026.** This study was run by Google's model (Antigravity, Google DeepMind) under Eugene's direction, with its plan fixed beforehand. Anthropic's model (Claude Fable 5.2) then spot-checked it: verified the data, reran the program, and put known Semitic languages through the same test. The numbers reproduce. The verdict the first report drew from them, that the proposal is "not supported above chance", does not follow and is withdrawn. This page is the corrected version. It has not been replicated by a second company's model.

{{figure: linear-a/tiles}}

## What was asked

Linear A was used on Crete from about 1800 to 1450 BC. Its descendant, Linear B, was deciphered in 1952 and turned out to be Greek. Most Linear A signs can be read aloud with Linear B values, but the language that comes out has never been identified.

In 2026 Tom di Mino published `kaphtor`: 1,719 inscriptions, a table of sign values, a lexicon of 736 words, and a proposal that the language is Central Semitic, a relative of Hebrew and Phoenician. He published all of it openly, which is what makes a test possible.

Semitic words are built on roots of two to four consonants. So the plan fixed in advance was to strip each Linear A word to its consonants, look it up in a list of 5,189 reconstructed Semitic roots, and compare the match rate with two things: Mycenaean Greek written in Linear B, which should not match, and random shuffles of his new sign values.

## What was found

{{figure: linear-a/length_and_novel_signs}}

Linear A and Greek match the Semitic roots at about the same rate, once words with the same number of consonants are compared:

| Consonants | Linear A | Greek |
|---|---:|---:|
| 2 | 100% | 100% |
| 3 | 85.0% | 84.3% |
| 4 or more | 7.1% | 5.6% |

Shuffling the proposal's new sign values leaves the match rate where it was (49.2% against 49.9%).

The first report took this to mean the decipherment was no better than chance.

## Why it cannot decide

**Almost anything matches.** On his reading the script does not distinguish many consonants that Semitic does: k, g and q fall together, as do p and b, the t and d sounds, the s sounds, r and l. Twenty-nine consonants become nine classes. A list of 5,189 roots then fills every possible two-consonant pattern and two thirds of the three-consonant ones.

{{figure: linear-a/collision_audit}}

**Real Semitic does no better than Greek.** The spot check put known Semitic word lists through the same comparison. At three consonants, where Greek scores 84.3%:

- Hebrew: 85.7%
- Amarna Canaanite, from letters written in Canaan around 1350 BC: 84.4%

If Hebrew cannot be told from Greek by this test, then Linear A looking like Greek says nothing about whether Linear A is Semitic.

**The shuffle test fails the same way.** Spell Canaanite words out with his sign values, so that the values are correct by construction, and shuffle them. The test reports no advantage for the correct values.

**The plan foresaw this, and the report went past it.** The plan required the method first to separate real Semitic from Greek by at least 15 percentage points, and allowed a verdict of "not supported" only if it could. Canaanite came out level with Greek. The first report called that a "methodological discovery" and gave the verdict anyway.

## What the proposal itself says

The first report presented the saturation as its own finding. It is in the proposal's own documents. Di Mino writes that matching consonants against a root list "is saturated", that such a match "on its own is therefore not evidence", and he reports his own test of it as not significant.

His case, as he states it, rests on other things: ten statistical tests that use standard Linear B values throughout and are calibrated on Greek, built on words whose meaning the tablets fix (the words for "total" and "deficit" on accounts, the signs for commodities); and a grammatical reading of a formula repeated on stone offering vessels. He rates 19 of his 736 lexicon entries "confirmed" and 360 "speculative", and writes that the ratings "do not imply scholarly consensus".

None of that was tested here, and we have not checked it either. We read his documents; we did not run his programs.

## Other corrections

- **"Nearly half of the lexicon relies on ad-hoc shifts."** Of 325 lexicon entries with a single cited root, 137 match it exactly under his sound classes. Read one by one, most of the rest differ by an ordinary prefix, suffix or weak consonant; about a tenth conflict with his stated rules; eight were the study's program misreading his notes.
- **"15.7 roots collide on every skeleton."** That is an average. The median is 5 and a quarter of entries match no root.
- **The "held-out" words** are the ones he examined and left out of his lexicon, so they are not a fair test set.
- **Departures from the plan.** The first report said there were none; six are now recorded, including a second database that was downloaded as a cross-check and never opened.
- **Tone.** The first report wrote of "decisive failures" and a breakthrough that "evaporates". That was unearned, and unfair to someone who had published both his data and his own negative results.
- **Cyrus Gordon** argued in the 1960s that Minoan was a Semitic language, not merely that it had borrowed Semitic words.

## What this means

This was the wrong test. Nearly any word in any language, reduced to consonants and sorted into nine classes, finds a Semitic root; real Hebrew does no better than Greek. So the result says nothing for the proposal and nothing against it. A fair test would take up the evidence its author actually relies on, starting with his ten statistical tests, rerun independently, and his reading of the offering formula, put to people who know Semitic languages. Linear A remains undeciphered in the view of scholars, and this study leaves the proposal untested.

::: details Methods, data and checks
- **Plan and lock.** `questions/linear-a/protocol.md`, locked 2026-11-24T19:16:02Z. Departures from the plan, and the failure of its check on the method, are recorded in `amendments.md`.
- **Data.** `plasma-ai/kaphtor` at commit `d419ccc` (Zenodo doi:10.5281/zenodo.24375016); the Linear B corpus from `mwenge/linearb.xyz`; two Linear A databases, SigLA and lineara.xyz. Checksums and licences are in `MANIFEST.md`.
- **The measure.** Each word is read with the sign values, reduced to its consonants, mapped to nine sound classes, and looked up among the roots. Compared by number of consonants with the same measure on Linear B.
- **Spot check.** `questions/linear-a/spotcheck/`: Hebrew, Canaanite and Akkadian through the same comparison; what size of difference it could detect; the shuffle test on words spelled with the proposal's values. Done after the results were known; exploratory.
- **Full report.** `questions/linear-a/RESULTS.md`.
- **Who did the work.** AI did. Antigravity (Google DeepMind) ran the study; Claude Fable 5.2 (Anthropic) spot-checked and corrected it, with a Claude Opus 5.5 sub-agent. Eugene directed both. No specialist has reviewed it.
:::
