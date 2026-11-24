---
# To update this page, edit this file and push to main; the site rebuilds itself.
# The figures are made by questions/khipu/analysis/make_figures.py from the results file.
summary: The Incas kept records on knotted cords called khipus. About six hundred have been measured and published. We searched every pair of them for runs of cords carrying the same numbers in the same order, which would mark one as a copy of another.
verdict: Real copies turn up, some long; the first report's "eight new twins" does not hold
result: Five pairs of khipus share runs of numbers that we did not find in the published literature; one pair, in Paris and Lima, agrees over about 174 cords. They are candidates for someone to confirm on the objects. Of the eight pairs first announced, two were published in 2005 and one is a single khipu catalogued twice. The claim of "zero false discoveries" was not shown, the matcher missed a known copy, and by the plan's own rule the result is inconclusive.
dek: A search of 619 Inca knotted-cord records for copies of one another, and a check of what it found.
updated: 2026-11-24
---

> **Where things stand, 24 November 2026.** This study was run by Google's model (Antigravity, Google DeepMind) under Eugene's direction, with its plan fixed beforehand. Anthropic's model (Claude Fable 5.2) then spot-checked it: reran the program, pulled each of the sixteen khipus from the database separately, tested how often chance produces a match, and searched the literature. The matching numbers are real. The first report's headline, eight newly discovered twins at zero false-discovery rate, is not, and this page is the corrected version. It has not been replicated by a second company's model, and nobody has looked at the cords.

{{figure: khipu/tiles}}

## What was asked

A khipu is a main cord with rows of hanging cords, each knotted. On most of them the knots record numbers in base ten. What the numbers counted is mostly lost, since only a handful of khipus can be tied to anything written.

In 2005 Gary Urton pointed out that some khipus are copies of others: the same numbers in the same order. He took this as a sign that Inca record-keepers kept duplicates to check one another. The best-known set comes from Puruchuco, near Lima.

The Open Khipu Repository holds measurements of 619 khipus. The plan fixed in advance was to compare every pair for matching runs of numbers, to count how often chance would produce such a run, and to test the search on the Puruchuco copies first.

## What was found

{{figure: khipu/rosetta_twins}}

The first report announced eight pairs. Looked at one by one:

| Pair | Where the khipus are | What it is |
|---|---|---|
| 1 | Gothenburg and Lima | The last 37 cords of each agree, 24 exactly, with numbers in the thousands. Not found in the literature we searched |
| 2 | Berlin (Pachacamac and "Huacho") | About 100 cords agree, laid out in groups of five on one and six on the other. Not found |
| 3 | Berlin | **One khipu, recorded twice** by two investigators and read from opposite ends |
| 4 | Berlin (both Pachacamac) | Eight cords, seven exact, numbers in the hundreds. Not found |
| 5 | Berlin (Ica region) | Ten cords, exact. **Published by Urton in 2005** |
| 6 | Paris and Lima | About 174 cords agree, 122 exactly: nearly all of the Lima khipu. Not found. The first report gave 8 cords |
| 7 | Berlin (Nazca and Ica) | Nine cords, five exact. Weak |
| 8 | Berlin (Ica region) | Seven cords, exact. **Published by Urton in 2005** |

So five pairs are candidates, three of them strong. Pair 6 is the most striking: where cords on the Paris khipu are broken, the Lima khipu still carries the numbers, so these are two objects and one is close to a full copy of the other.

## What did not hold

**"Every pair is two physically distinct specimens."** Pair 3 is one khipu. The two records' cord lengths agree to within a centimetre or two all the way along, and a public catalogue of the same database already lists them as one object. The first report said this pair "ties an unprovenanced specimen to Marquez". It re-identified a catalogue entry. The database's duplicate flag, which the report relied on, is empty for every record.

**"No published pairing."** Pairs 5 and 8 are in Urton's 2005 paper, at the same cord positions. For the other five we found nothing, but we could not search the printed catalogues in which the khipus were first described, which cross-reference related pieces.

**"Zero false-discovery rate."** That rested on 100,000 shuffled comparisons, fewer than the 127,765 real ones. Forty full passes of the same shuffle give about one false match in the top tier for every two passes: a rate of about one in twenty, which the plan calls a failed calibration. The chance matches are all short runs of small numbers. Nothing by chance resembles the long matches in pairs 1, 2 and 6.

**"Positive control passed."** Of the three matching pairs at Puruchuco, the search found one cleanly, one only in its weaker tier, and missed the third. It also misses a duplicate that the database itself documents, because a single misread cord spoils the run.

**The name.** A Rosetta stone gives the same text in a known script. Two khipus with the same numbers give no reading of either.

## The Santa valley khipus

{{figure: khipu/santa_and_census}}

One match between khipus and a Spanish document has been published: six khipus from the Santa valley and a census of 1670 (Medrano and Urton, 2018). The first report announced a "major statistical caution" about it: the census's six groups can be split three against three in ten ways, and most random sets of six numbers can be split to fit the khipus as well as the published split.

That calculation is correct and assumes the split was picked freely from the ten. If it was fixed beforehand, the figure falls from about two in three to under one in ten. The study did not find out which. It also tested only the split, and the published case rests on more: the number of cord groups against the number of tribute-payers, the direction in which cords are tied on, the values on the first cords. We have not read the papers either, so we withdraw the "caution" as worded and leave the question open.

## What this does not settle

- **Whether each pair is two objects.** Only pair 3 was settled, and that one is a single khipu.
- **Whether the five are new.** The search of the literature was partial.
- **What any khipu says.**
- **The Santa valley match.**

## What this means

Some Inca records were kept in duplicate, and a simple search of the published measurements finds more candidates for such duplicates than had been pointed out, including one near-complete copy split between Paris and Lima. That supports what Urton proposed twenty years ago, and it is worth a specialist's hour with the objects. It was first reported here as eight discoveries with no chance of error, and it is neither eight nor certain. The matcher that found the pairs is rough enough to miss known copies, so its silences mean little, and the list is best treated as leads.

::: details Methods, data and checks
- **Plan and lock.** `questions/khipu/protocol.md`, locked 2026-11-24T19:45:38Z. Its verdict rule and the departures from it are in `amendments.md`.
- **Data.** The Open Khipu Repository, doi:10.5281/zenodo.18025748, at commit `4039ca5` (MIT licence). Checksums are in `MANIFEST.md`.
- **The search.** For each pair of khipus, the best unbroken window of cords whose numbers agree within 1 or 2%, forwards or reversed; and the same for sums over groups of cords.
- **Spot check.** `questions/khipu/spotcheck/`: an alignment that allows a missing cord; cord lengths compared to tell one object from two; two chance models run over every pair forty times; the search tried on known copies. Done after the results were known; exploratory.
- **Sources.** Urton, G. (2005), "Khipu Archives: Duplicate Accounts and Identity Labels in the Inka Knotted String Records", *Latin American Antiquity* 16(2):147–167; the Khipu Field Guide (khipufieldguide.com). Not read: Medrano and Urton (2018), FitzPatrick (2024), Urton and Brezine (2005), the Aschers' databooks.
- **Full report.** `questions/khipu/RESULTS.md`.
- **Who did the work.** AI did. Antigravity (Google DeepMind) ran the study; Claude Fable 5.2 (Anthropic) spot-checked and corrected it, with a Claude Opus 5.5 sub-agent. Eugene directed both. No specialist has reviewed it.
:::
