---
# To update this page, edit this file and push to main; the site rebuilds itself.
# The figures are made by questions/indus-script/analysis/make_figures.py from the results file.
summary: In November 2026 a preprint, written with an AI model, claimed to read the Indus script as an early relative of Tamil. Its evidence for the language is a contest in which Tamil names fit the seal texts and other languages' names do not. We ran that contest on seven languages nobody thinks the Indus people spoke.
verdict: The language test passes Sumerian too; our own main test came out incomplete
result: The preprint's numbers reproduce exactly. But Sumerian and Nahuatl also pass its contest, and Sumerian passes for the same reason Tamil does: the commonest sign looks like a jar, and the word for a pot sounds like a word that names often end in. Our planned test, which needed a Tamil list built like the others, was incomplete, because both such lists failed a check we had set too strictly. In exploration afterwards, Tamil passed or failed according to which word for "pot" its translator chose.
dek: A preprint says the Indus script writes an early form of Tamil. A check of the test it uses to tell which language, run on seven languages with no claim on the seals.
updated: 2026-11-27
---

> **Where things stand, 27 November 2026.** Finished, and incomplete by its own rule. Anthropic's model (Claude Fable 5.2) designed and ran this study under Eugene's direction, with its plan fixed beforehand and reviewed by Google's model. The plan needed a fresh Tamil word-and-name list that passed a quality check. Both such lists failed the check, partly because we had set it more strictly for Tamil than the preprint's own. So the main question was not answered as planned. What the planned run does show, and what we found by exploring afterwards, is below, with the two kept apart.

{{figure: indus-script/tiles}}

## What was asked

The Indus civilisation, in what is now Pakistan and north-west India, left about 4,700 inscribed objects, most of them small stone seals. The texts are tiny, about four signs each, and nothing pairs them with a known script. Nobody has read them.

On 24 November 2026 Siva Raj announced a preprint, written with Anthropic's Claude, that reads the script as an early Dravidian language, through Old Tamil. It gives readings for 150 signs. The paper is unusual among claimed decipherments. Its test plans were fingerprinted before each test was run, its failed tests are listed, and its word lists and programs are public.

Three days later a group called Open Indus answered that the same method "reads" the seals in Japanese too. The author replied with further tests of his own.

The paper's case that the language is Dravidian rests on one test, which it calls a contest. This study checks that contest. It does not examine the 150 readings.

## How the contest works

1. An AI judge looks at each of 69 common signs and writes four English words for what it shows: "jar", "fish", "person with a yoke".
2. A translator turns each English word into words of the language being tested.
3. A list of that language's ancient names is cut into meaningful parts. "King-good" is two parts.
4. A sign may be read as any name part that sounds like one of its picture words. The program picks the readings that make the seal texts look most like names.
5. The same is done with the name parts shuffled. The score is real names minus shuffled names.

The preprint reports Old Tamil at +223, and Sanskrit and Akkadian at about zero.

## The numbers are real

The lab does not run programs it has downloaded, so we wrote the contest out again from the paper's method. On the paper's own lists it gives the published number in every one of 80 archived runs, to two decimal places. Google's model then wrote a second program from our description alone, without seeing ours. It matches too.

## Two unrelated languages pass

We had fresh AI sessions, told nothing of the purpose, build word and name lists for languages that nobody proposes for the Indus seals. Seven lists passed a quality check and were run.

{{figure: indus-script/contest}}

Sumerian and Classical Nahuatl pass the paper's own mark. The other five do not. Greek and Hebrew could hardly have passed: their lists left most names whole, and a name of one part gives the contest nothing to fit.

## Why Sumerian passes

One sign carries the score.

{{figure: indus-script/what_carries}}

- **In the paper's Tamil list,** the commonest sign of all looks like a jar. It usually ends a text. The contest reads it *kuṭi*, a word for a settlement that ends some Tamil names. It gets there because *kuṭi* sounds like *kuṭam*, pot. Leave that one sign unread and Tamil's score falls from +188 to +44.
- **In our Sumerian list,** the same sign is read *dug*. That is the Sumerian for pot. It is also the Sumerian for "good", which is the last part of 14 names of the kind "King-good". Leave the sign unread and Sumerian falls from +113 to −6.
- **In Nahuatl** it is a different sign, one that looks like an arrow and also tends to end a text. *Mitl* is arrow, and nine names end in it.

So the contest rewards one thing. A sign that ends many texts has to meet a word that ends many names, by way of what the sign looks like. Tamil has such a pair. So does Sumerian.

## Our main test was incomplete

The question we fixed in advance was whether Tamil stands out when its list is built in the same way as the controls' lists. The paper's own Tamil list was made inside the project; its control lists were made fresh by sessions that knew nothing. We planned two fresh Tamil lists.

Both failed the quality check on their picture words, twice, and by the plan's rule were dropped. So was Finnish. With no fresh Tamil list, the plan's verdict is "Incomplete".

Part of this is our own doing. A checker looked every word up and failed any word not found in the earliest Tamil poems. The paper's own check failed only modern words. Many of the words that failed ours are real Tamil words first recorded a few centuries later. In Finnish, the translator's instructions allowed very old loanwords and the checker's did not. Both faults were in instructions we wrote before the plan was fixed. We applied the rule as written and did not loosen it after watching lists fail.

## What exploring afterwards showed

This part was not planned and does not count as the study's answer.

We ran the dropped Tamil lists through the same program anyway. They scored +8 and 0, below Sumerian and Nahuatl.

Then we looked at why. Old Tamil has several words for a pot. Four translators had worked on our two Tamil lists. One offered *kuṭam*. The other three offered *kalam*, *tāḻi* or *pāṉai*.

| Tamil name list | Translator's words for "pot" | Score | Rounds won, of 100 |
|---|---|---|---|
| List A | *kuṭam*, *kalam* | +167 | 96 |
| List A, same names | *kalam*, *tāḻi* | +8 | 59 |
| List B | *kalam*, *tāḻi* | −26 | 40 |
| List B, same names | *kalam*, *pāṉai* | 0 | 54 |

The first two rows use the same names. With *kuṭam* on offer the jar sign is read *kuṭi* every time and Tamil passes easily. Without it, Tamil scores nothing. The translator the paper used also chose *kuṭam*.

## The pictures do not matter

The author's reply says Tamil still leads when every sign is given another sign's picture words. For his own list that is so: it scores +182 that way against +188 the proper way.

{{figure: indus-script/shuffled}}

That cuts against the contest more than for it. If the score is the same when the jar sign is given the picture of a fish, the score is not coming from what the signs show. We have not traced which signs carry his list's score once the pictures are moved; with them in place, it is the jar.

## What this does not settle

- **Whether the Indus language was Dravidian.** That is an old proposal with many supporters, argued on other grounds. Nothing here bears on it.
- **Whether the paper's 150 readings are right.** They rest on other tests, which we did not examine.
- **How often Tamil would pass.** Four translations is too few to say how often a translator would choose *kuṭam*.
- **The other controls.** Our Old Japanese list scored far below zero. The rebuttal's Japanese list scored +134 and the author's +81. One language, three lists, three answers. That is itself a reason to distrust any single score.
- **Our own mistakes.** The study is incomplete because of a check we set badly. A second study would word that check as the paper did, use several translators for each list, and fix in advance how finely names are cut.

## What this means

The paper deserves credit for making itself checkable, and its arithmetic is right. But its test for the language rewards a coincidence. The commonest Indus sign looks like a jar. If a language's word for a pot happens to sound like a common ending of its names, that language passes. Tamil passes this way, and so does Sumerian, which nobody thinks was spoken in the Indus cities. When Tamil's translators picked a different word for pot, Tamil failed. So a pass in this contest is not evidence about the language of the seals. We meant to show that with a test fixed in advance, and fell short of it through a fault of our own design. What we can show is the mechanism.

::: details Methods, data and checks
- **Plan and lock.** `questions/indus-script/protocol.md`, locked 2026-11-28T03:15:52Z, before any new list existed. Two amendments, both about spelling and file format, in `amendments.md`.
- **The work under test.** Siva Raj with Claude, *Indus Script Read as Early Dravidian, with AI Assistance*, v0.7, doi:10.5281/zenodo.24383779 (CC BY 4.0). Its seal texts come from the file `inscriptions.csv` in the public repository `yajnadevam/lipi`. Checksums are in `MANIFEST.md`.
- **The dispute.** Open Indus, announced by Harsha G. on 27 November 2026; the author's reply of 28 November. Their numbers are quoted in the plan and were not verified by us.
- **The lists.** For each language a translator, a name compiler, a labeler and a checker, each a fresh session of Claude Opus 5.5 given its instructions and nothing else. What each wrote, and every check, is in `questions/indus-script/lists/`.
- **The run.** 100 rounds a list. A list passes if real names beat shuffled names in 80 rounds and its score is at least a quarter of the preprint's Tamil list's.
- **Independent program.** Google's `gemini-4-neon` wrote its own from the plan and `analysis/METHOD.md`. It agrees with ours on all 700 list-rounds and with the preprint's archive on the 20 splits tried.
- **Exploration.** `questions/indus-script/explore/`. Labelled as such throughout.
- **Full report.** `questions/indus-script/RESULTS.md`.
- **Who did the work.** AI did. Claude Fable 5.2 (Anthropic) designed and ran it, with Claude Opus 5.5 sessions building the lists; Google's `gemini-4-neon` reviewed the plan and replicated the program. Eugene directed it. No specialist has reviewed it. The preprint's author and Open Indus had no part in it and have not been contacted.
:::
