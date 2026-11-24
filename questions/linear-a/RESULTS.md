# Results — Is Linear A cracked? (#12)

- **Question:** #12, `lane:data`.
- **Plan locked:** 2026-11-24T19:16:02Z (`protocol.lock`, commit `94d87f9`), before the results were committed. Unchanged since.
- **Who did the work:** AI did. Antigravity (Google DeepMind) designed and ran the study on 24 November 2026. Claude Fable 5.2 (Anthropic), with a Claude Opus 5.5 sub-agent, spot-checked it the same day and wrote this corrected report. Eugene Jhong directed both. No specialist has reviewed it, and it has not been replicated by a second company's model.
- **Departures from the plan:** recorded in `amendments.md`. The first report said there were none.

## Answer

**This test cannot tell. Under the proposal's sound classes, Linear A words match Semitic roots as often as Mycenaean Greek words do. So do Hebrew and Canaanite words. A test that cannot tell Hebrew from Greek cannot judge whether Linear A is Semitic.**

In 2026 Tom di Mino published `kaphtor`, an open dataset and a proposal that Linear A, the undeciphered script of Minoan Crete, writes a Central Semitic language. The study asked whether Linear A words, read with his sign values and reduced to their consonants, match a list of 5,189 Proto-Semitic roots more often than chance, and more often than Mycenaean Greek written in the related script Linear B.

- **The numbers.** Compared at the same number of consonants, Linear A and Greek match the Semitic roots at about the same rate: 100% and 100% for two consonants, 85.0% and 84.3% for three, 7.1% and 5.6% for four or more. The program reruns to exactly these figures.
- **Why that settles nothing.** The spot check put known Semitic word lists through the same comparison. Hebrew three-consonant words match 85.7% of the time and Amarna Canaanite 84.4%, against Greek's 84.3%. By this test real Semitic is "indistinguishable from Greek" too.
- **The plan said as much.** It required the method first to show it could separate real Semitic from Greek by at least 15 percentage points, and allowed a verdict of "not supported" only if it did. It did not: Canaanite came out level with Greek and Akkadian 30 points below. The first report called this "a crucial methodological discovery" and gave the verdict anyway.
- **The shuffle test has no power either.** Shuffling the proposal's new sign values left the match rate unchanged (49.2% against 49.9%), which the first report read as showing the values are no better than random. But when Canaanite words are spelled out with those same values, so that the values are right by construction, the test gives the same result (`p = 0.99`).
- **The proposal's author already says this.** His repository states that matching consonant skeletons against a root list "is saturated" and "on its own is therefore not evidence", and reports his own null result for it. His case rests on other tests, which this study did not examine.

The first report's verdict, "not supported above chance", and its closing line, that the "breakthrough evaporates", are withdrawn. Nothing here supports the proposal and nothing here counts against it.

## What was tested

Linear A is a syllabic script: each sign is a consonant plus a vowel. Linear B, which descends from it, was deciphered in 1952 as Greek. Reading Linear A signs with Linear B values gives pronounceable words in an unknown language. Di Mino keeps most of those values, proposes new ones for some signs, and reads the result as Semitic.

Semitic words are built on roots of consonants, so the natural check is to strip a word to its consonants and look for a root. The difficulty is that the script, on his reading, does not distinguish many consonants that Semitic does: k, g and q fall together, as do p and b, the t and d sounds, the s sounds, and r and l. Twenty-nine Semitic consonants become nine classes. With nine classes there are 81 possible two-consonant skeletons and 729 three-consonant ones, and the root list fills all 81 and 476 of the 729. Almost anything matches something.

## The locked run

The tables are the first run's numbers.

### The check on the method (plan §3.3)

Required: real Semitic beats a shuffle of the consonant classes at `p < 0.001` and beats Greek by 15 points or more, on words of three or more consonants.

| Word list | Sound classes | Match rate | Greek (Linear B) | Margin | Shuffle `p` | Required |
|---|---|---:|---:|---:|---:|---|
| Amarna Canaanite | nine (A1) | 48.9% | 48.9% | 0.0 | 0.016 | fails both |
| Amarna Canaanite | affix-tolerant (B) | 75.2% | 73.6% | +1.6 | 0.002 | fails both |
| Akkadian | nine (A1) | 19.0% | 48.9% | −29.9 | 0.001 | fails both |
| Greek (Linear B) | nine (A1) | 48.9% | | | 0.001 | |

Greek beats the shuffle as strongly as Semitic does. The first report explained this by the commonness of certain consonants in all languages; that is a reasonable guess and was not tested.

The spot check found the Semitic lists were handled in a way that lowers their scores: doubled consonants in the cuneiform spellings were kept, and the spelling habits of Linear B were not applied. Handled more carefully, Akkadian rises from 19.0% to 64.0%. That is a fault in the control, and mending it does not rescue the headline comparison, below.

### Linear A against Greek, by number of consonants (plan §3.4, Test 3)

| Consonants | Linear A, all | Linear A, not in his lexicon | Greek (Linear B) | Fisher `p` (all; not in lexicon) |
|---|---:|---:|---:|---|
| 2 | 100.0% (86/86) | 100.0% (10/10) | 100.0% (401/401) | 1.00; 1.00 |
| 3 | 85.0% (209/246) | 82.1% (23/28) | 84.3% (897/1,064) | 0.85; 0.79 |
| 4 or more | 7.1% (9/126) | 5.9% (2/34) | 5.6% (49/872) | 0.54; 1.00 |

Without sorting by length, Linear A is ahead: 58.6% against 48.9% (`p = 0.0007`). The gap comes from the mix of word lengths (two thirds of Linear A's longer words have three consonants, against 55% of Greek's) and disappears when lengths are matched. Linear A is ahead of Greek by similar margins on Luwian, Egyptian, Hattic and Hurrian root lists, which points to word shape and not to Semitic.

What the same table looks like for known Semitic (spot check, after the fact):

| Word list | 3 consonants (Greek 84.3%) | 4 or more (Greek 5.6%) |
|---|---:|---:|
| Amarna Canaanite, handled as the study handled it | 84.4% (81/96), `p = 1.0` | 5.0%, `p = 1.0` |
| Hebrew lexicon, consonants only | 85.7% (1,827/2,132), `p = 0.31` | 6.1%, `p = 0.67` |
| Akkadian, respelled in Linear A with his values | 91.1% (n = 1,758), `p < 0.001` | 9.0%, `p = 0.007` |

With 246 Linear A words against 1,064 Greek ones and Greek already at 84%, the comparison could reliably detect a difference of six or seven points. Real Semitic lists differ from Greek by between −8 and +7.

### The new sign values, shuffled (Test 2)

| Words containing a "new" sign | n | Match rate | Shuffled, mean | `p` |
|---|---:|---:|---:|---:|
| All, nine classes | 124 | 49.2% | 49.9% | 0.57 |
| Not in his lexicon, nine classes | 25 | 24.0% | 22.3% | 0.52 |
| All, seven classes | 88 | 67.0% | 43.4% | 0.001 |

Three things limit this test.

- **It fails a planted truth.** Amarna Canaanite respelled with his values gives 49.0% against a shuffled 56.7%, `p = 0.99`. With 25 words, a correct reading is detected in none of 100 trials; with 124 words of Akkadian, in 38.
- **Half the "new" signs are not new.** The plan counted 32 novel signs; the program found 27. Of those, five either carry the standard Linear B value written differently (*ja* as *ya*) or do not change the sound class. Of the 124 words, 62 are affected only by those. Restricted to the 22 signs that are new, the result is 61.3% against 53.2%, `p = 0.015` (62 words), and `p = 0.24` on the 14 not in his lexicon. That is exploratory, and it is in-sample: he chose the values partly by how well they fit roots.
- **The one significant row** was put down to an artefact of the seven-class rule. The spot check partly bears that out: counting only words whose skeleton keeps its length under the shuffle, `p` rises to 0.053.

### Other root lists (Test 4)

On three-or-more-consonant skeletons, Linear A matches the Semitic list 58.6% of the time, Luwian 29.8%, Egyptian 22.7%. Greek matches the same lists 48.9%, 21.8% and 20.3%. Semitic comes out ahead for every text because its roots are mostly three consonants long and fill most of the 729 slots. The plan called for 1,500 skeletons per list and two sets of sound classes; the run used 798 and one.

### His lexicon (Test 5)

- Of 736 entries he rates 19 "confirmed", 79 "probable", 278 "candidate" and 360 "speculative". He writes that the ratings "describe support under this project's evaluation criteria" and "do not imply scholarly consensus".
- 290 entries are one or two signs long.
- Of 325 entries of three or more signs with a single cited root, 137 (42%) match that root exactly under his sound classes. The first report said the rest "rely on ad-hoc extra consonant shifts, deletions, or metatheses". Read one by one, about 130 of the 188 are ordinary Semitic word-building (a prefix or suffix, a weak consonant, a doubled one); 8 are the study's program misreading his notes as consonants; some 35 to 50, a tenth to a seventh of the 325, do conflict with his stated classes.
- The first report said 15.7 roots "collide on every single skeleton". That is an average: the median is 5 and a quarter of the entries match no root at all.

## Spot check and corrections

A spot check is not a replication. It verified the data, reran the program, put known Semitic word lists through the same tests, and read the proposal's own repository.

What holds: the lock; all four data checksums and the contents of the dataset as described; the rerun, byte for byte; every number in the tables; the length-matched comparison was in the locked plan; the saturation figures.

What does not:

1. **The verdict.** The plan permits "not supported" only if the check on the method passes. It failed. The plan has no verdict for that case; the honest one is that the test is uninformative.
2. **No power,** shown above for both the main comparison and the shuffle.
3. **The wrong target.** Di Mino's repository says of skeleton matching (`docs/shoresh-preregistration.md`): "Distance alone is saturated", "A distance on its own is therefore not evidence", and reports his own bulk test as "not Bonferroni-significant". His stated evidence is a set of ten statistical tests run "under strict Linear B values" with "Linear B Greek calibration gates", using words whose meaning is fixed by context (the totalling words on accounts, commodity signs), and a grammatical reading of a repeated religious formula. This study examined none of them, and we have not checked them either. The first report presented the saturation as its own discovery.
4. **The "held-out" words are not a fair hold-out.** They are the words he looked at and left out of his lexicon, so a lower match rate is expected whether he is right or not, and he had the whole corpus before him when he chose sign values.
5. **The Greek control is not all Greek.** A third of its words occur only at Knossos, where many of the names on the tablets are not Greek. Not quantified.
6. **Departures from the plan,** six of them, are in `amendments.md`. A second Linear A database that the plan said would be used as a cross-check was downloaded and never read.
7. **Tone.** The first report wrote of "decisive failures", a "fake" signal and a breakthrough that "evaporates", with exclamation marks, about the work of a named person who had published his data and his own negative results. Those words are gone.
8. **Facts.** Cyrus Gordon proposed in the 1960s that Minoan was a Northwest Semitic language, not that it had Semitic loanwords. "Linear A is still undeciphered" is the scholarly consensus and not a finding of this study. The licences in the manifest were wrong in places and are corrected.

The plan and the 36 KB program with its results were committed under six minutes apart. Git cannot show whether anything was run before the lock.

## Limits

1. **The method.** Matching consonant skeletons to a root list through nine sound classes cannot separate a Semitic language from Greek. That is the finding.
2. **Not tested:** his ten statistical tests; his reading of the libation formula; anything about grammar or meaning.
3. **The synthetic respellings** used in the spot check are rough. The conclusion is the same across four word lists; the exact percentages are indicative.
4. **Not read:** his essay and the paper on the formula; his program was read and not run.
5. **No replication** by a second company's model.

## Spending

Nothing was paid for.

## What this means

A new claim to have read Linear A deserves a test, and its author made one possible by publishing everything. This was not the right test. Reduced to consonants and sorted into the nine sound classes the script allows, nearly any word in any language finds a Semitic root: Greek does, and real Hebrew does no better than Greek. So the fact that Linear A does no better than Greek says nothing about what language it writes. The author of the proposal had already reached the same conclusion about this kind of matching and rests his case on other evidence, which nobody here has examined. Linear A remains undeciphered in the view of the field, and this study leaves his proposal where it found it: untested.
