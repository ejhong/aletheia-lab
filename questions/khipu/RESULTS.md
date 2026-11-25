# Results — The khipu Rosetta hunt (#13)

- **Question:** #13, `lane:data`.
- **Plan locked:** 2026-11-24T19:45:38Z (`protocol.lock`, commit `1febf81`), before the results were committed. Unchanged since.
- **Who did the work:** AI did. Antigravity (Google DeepMind) designed and ran the study on 24 November 2026. Claude Fable 5.2 (Anthropic), with a Claude Opus 5.5 sub-agent, spot-checked it the same day and wrote this corrected report. Eugene Jhong directed both. No specialist has reviewed it, and it has not been replicated by a second company's model.
- **Data:** the Open Khipu Repository (OKR), doi:10.5281/zenodo.18025748, at commit `4039ca5`.
- **Departures from the plan:** recorded in `amendments.md`.
- **Spending:** nothing was paid for.

## Answer

**The search turned up real copies: khipus in different museums that carry the same runs of numbers, some far longer than the first report noticed. But it did not find "eight new twins at zero false-discovery rate". Two of the eight were published in 2005, one is a single khipu catalogued twice, and by the plan's own rule the result is inconclusive.**

A khipu is an Inca record made of knotted cords. The knots on most of them encode numbers. The study compared every pair among 619 khipus for runs of cords carrying the same numbers in the same order.

- **What is there.** Five pairs carry matching runs that we did not find in the literature we could search. Three are strong and longer than reported:
  - a khipu in Paris and one in Lima agree on about 174 cords, 122 of them exactly, nearly the whole of the Lima khipu (the first report gave 8 cords);
  - a Pachacamac khipu and one labelled Huacho, both in Berlin, agree on about 100 cords in two different layouts;
  - a khipu in Gothenburg and one in Lima agree on their last 37 cords, with four-figure numbers.
- **What is not new.** Two of the eight pairs are in Gary Urton's 2005 paper on duplicate khipus, at the same cord positions. The first report listed one of them among pairs with "no published pairing".
- **What is not a pair.** One "pair" is the same khipu recorded by two investigators and read from opposite ends. Its cord lengths agree to within a centimetre or two, and the Khipu Field Guide already lists the two records as one object. The first report said every pair was "two physically distinct museum specimens" and that this one "ties an unprovenanced specimen to Marquez".
- **"Zero false discoveries" was not shown.** The claim rested on 100,000 shuffled comparisons, fewer than the 127,765 real ones. Run at full scale, the study's own shuffle produces about one false top-tier match for every two scans of the collection, a false-discovery rate of about 5%, which the plan calls calibration failure. The chance matches are short runs of small numbers; nothing by chance looks like the long matches above.
- **The check on the method failed.** The plan required the matcher to recover the known copies from Puruchuco. Of the three matching pairs in that set it found one cleanly, one only in its weaker tier, and missed the third. It also failed to recover the set's summing hierarchy, and it misses a documented duplicate in the collection because one misread cord spoils the run.
- **The "caution" about the Santa Valley khipus tested something its authors did not argue.** See below.

By the plan's rule the verdict is "inconclusive, calibration failure". As an exploratory result: several khipus now in different museums are copies of one another in whole or in part, which fits what Urton proposed in 2005, that Inca record-keepers kept duplicate accounts. Whether the pairs above are distinct objects needs someone to look at them.

## The eight pairs

"Aligned" and "exact" are from the spot check's own alignment, which allows a missing cord.

| | Khipus (investigators' numbers; museum) | Reported run | What the spot check found | Standing |
|---|---|---|---|---|
| 1 | KH0362 (UR122; Gothenburg) and KH0049 (AS038; MNAAHP, Lima) | 23 cords, 19 exact | 37 cords aligned, 24 exact: the last 37 of both. Some subsidiary cords match too. Cord lengths differ, so probably two objects | Not found in the literature searched. Strong |
| 2 | KH0192 (AS175; Berlin, Pachacamac) and KH0470 (UR233; Berlin, "Huacho") | 6 group sums, exact | About 101 cords aligned, 71 exact. A second record with the same accession number (KH0469) matches another stretch of KH0192 | Not found. Strong. The records for this accession are muddled and need a museum check |
| 3 | KH0121 (AS107; Berlin, Marquez) and KH0473 (UR237; Berlin) | 17 cords, reversed | All 29 cords; cord lengths correlate at 0.98 with a median difference of 1.5 cm | **One khipu recorded twice.** Listed as aliases in the Khipu Field Guide |
| 4 | KH0132 (AS118) and KH0456 (UR218), both Berlin, Pachacamac | 8 cords, 7 exact | As reported; three-figure numbers | Not found. Strong but short |
| 5 | KH0128 (AS114) and KH0137 (AS123), Berlin, Ica region | 10 cords, exact | As reported | **Published:** Urton 2005, p. 150 and fig. 3 |
| 6 | KH0097 (AS084; Quai Branly, Paris) and KH0586 (HP055; MNAAHP, Lima) | 8 cords | 174 cords aligned, 122 exact. Where the Paris khipu's cords are broken, the Lima one carries values, so two objects | Not found. The strongest result |
| 7 | KH0156 (AS140; Berlin, Nazca) and KH0432 (UR194; Berlin, Ica) | 9 cords, reversed | 5 exact, 4 off by one or two. The run is one instance of a pattern repeated within AS140 | Not found. Weak |
| 8 | KH0175 (AS159) and KH0190 (AS173), Berlin, Ica region | 7 cords, exact | As reported; the numbers alone are no better than chance matches of the same length | **Published:** Urton 2005, p. 150 and fig. 2 |

The collection's duplicate flag is empty for all 619 records, including a pair that its own concordance file describes as duplicates, so it could not have shown that pairs are distinct. Different catalogue numbers do not show it either.

Not searched: the Aschers' printed databooks, which cross-reference related khipus; Urton (2017); Clindaniel (2019); Medrano and Khosla (2024). Any of the five "not found" pairs may be noted there.

## How often chance does this

| Null | Comparisons | False top-tier matches | Per scan of the collection | Implied false-discovery rate |
|---|---:|---:|---:|---:|
| The study's: shuffle within each khipu, 100,000 comparisons | 100,000 | 0 | (less than one scan) | reported as 0.000 |
| The same shuffle, 40 full scans | 5,110,600 | 20 | 0.50 | about 0.05 |
| Values replaced by others of the same length, zeros and repeats kept, 40 scans | 4,836,054 | 5 | 0.12 | about 0.013 |

No chance match is longer than 8 cords, and the largest number in any chance match is 220. The plan's null was different again (values permuted across khipus), and the group-sum mode that produced pair 2 had no null at all in the first run; in 80 scans the spot check found no chance match in that mode.

## The Santa Valley khipus

Six khipus from the Santa valley have been matched by Medrano and Urton (2018) to a Spanish census of 1670 listing 132 tribute-payers in six lineage groups. The first report announced a "major statistical caution": if six groups are split three against three, there are ten ways to do it, and 62% to 72% of random sets of six numbers can be split to match the khipus' two halves as well as the published match does.

The arithmetic is right. What it shows is narrower than was claimed.

- **It assumes the split was chosen freely from the ten.** If the split was fixed beforehand, by the document or by the khipus, the same calculation gives 4% to 9%. The study did not find out which. In the order the groups are listed, the split used by FitzPatrick (2024) takes alternate groups, which does not look like a free choice. We could not read either paper, so this is unresolved.
- **The published case does not rest on the split alone.** As summarised by others, it also rests on the number of six-cord groups (133) against the number of tribute-payers (132), on the direction in which cords are attached, and on the values of the first cords. The study's own test of the count and the total together found no random set of six khipus that matched (0 of 10,000); the first report's page did not mention it.
- **Numbers without a source.** "About 467 pesos under FitzPatrick's reading" is in neither the program nor the results. The manifest's own figures for the tribute do not agree with each other. The comparison of 756 with 367 pesos uses the study's mechanical grouping, not the published one.

The fair statement: the three-against-three split would be weak evidence by itself if it was chosen after the fact; whether it was is not known to us; the rest of the published argument was not tested. "Major caution" and "far less unique than often assumed" are withdrawn.

## Spot check and corrections

A spot check is not a replication. It verified the data, reran the program, pulled all sixteen khipus from the database with separate queries, aligned them allowing gaps, ran two nulls at full scale, and searched the literature it could reach.

What holds: the lock; both data checksums; the rerun, byte for byte; every number in the first report's tables; the aligned values of all eight pairs.

What does not: the count of new pairs; "physically distinct"; "no published pairing"; "FDR = 0.000"; "positive control passed"; the Santa Valley caution as worded; and the name. A matching pair of khipus is not a Rosetta stone. It gives no reading of either. "Trans-continental twin" describes where collectors took the objects in the twentieth century, and "across the empire" describes khipus that all come, by museum attribution, from the central and south coast of Peru.

Other points:

- **The knot check.** The first report said an independent decoding agrees with the database on 82.5% of cords. The other 17.5% were not examined. Most come from limits of the checking code and some from inconsistencies in the database.
- **"157 Rosetta-ready khipus"** is a rule that exists only in the program: ten knotted cords, three equal groups, a named provenance.
- **"No open corpus of colonial censuses exists"** was asserted, not checked.

## Limits

1. **The matcher is crude.** It takes one unbroken window per pair and gives up on a single bad cord. It should be mended and checked against the documented duplicates before anyone relies on a "no match".
2. **Same object or copy?** Only pair 3 was settled. The others need the objects.
3. **The literature search was partial,** as listed above.
4. **Provenances are museum attributions,** some of them vague or muddled.
5. **Not read:** Medrano and Urton (2018), FitzPatrick (2024), Urton (2017), Urton and Brezine (2005). The Puruchuco pairs were taken from the Khipu Field Guide's account of that paper.
6. **No replication** by a second company's model.

## What this means

Among the six hundred Inca knotted-cord records that have been measured and published, a handful are copies of each other: the same numbers in the same order, on cords now held in different cities. One pair, split between Paris and Lima, matches along nearly its whole length. This is not a new idea. Gary Urton showed two such pairs in 2005 and argued that Inca accountants kept duplicates as a check on each other. The search here adds candidates to his list and should be read as that: candidates, found by a rough tool, to be confirmed by people who can examine the cords. It does not read any khipu, and its attempt to cast doubt on the one published match between khipus and a Spanish document tested a simpler argument than the one its authors made.
