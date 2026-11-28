# Results — Does the Indus preprint's language contest pick out Tamil? (#145)

- **Question:** #145, `lane:data`.
- **Plan locked:** 2026-11-28T03:15:52Z (`protocol.lock`, commit `90d86d6`), before any new list existed. Two amendments, both before any contest run on a new list (`amendments.md`).
- **Who did the work:** AI did. Claude Fable 5.2 (Anthropic) designed and ran the study on 27 November 2026. Fresh sessions of Claude Opus 5.5 built and checked the lists. Google's `gemini-4-neon` reviewed the plan before the lock and wrote an independent program afterwards. Eugene Jhong directed it. No specialist has reviewed it.
- **The work under test:** Siva Raj with Claude, *Indus Script Read as Early Dravidian, with AI Assistance*, v0.7 (doi:10.5281/zenodo.24383779), not peer reviewed. Its author had no part in this study and has not been contacted.
- **Spending:** $1.39, all on Google's model.

## Answer

**By the plan's own rule the result is "Incomplete". The plan needed a fresh Old Tamil list built the same way as the control languages, and both fresh Tamil lists failed the plan's check on their picture words, twice, and were dropped. Part of the cause is a check that this study set stricter for Tamil than the preprint's own had been.**

What the locked run does show:

- **The preprint's numbers are real.** A program written afresh from its method reproduces all 80 archived runs checked, to two decimal places, with the same readings. A second program, written by Google's model from our description alone, does too.
- **Two languages with no claim on the Indus seals pass the preprint's contest.** Sumerian scores +113 and beats its scrambled control in 99 of 100 rounds. Classical Nahuatl scores +49, in 84 of 100. The preprint's own Tamil list, at the same size, scores +188 in 89 of 100. The other five controls do not pass.
- **Sumerian passes for the same reason Tamil does.** In the preprint's Tamil list the commonest sign, a jar, is read *kuṭi*, a settlement word that is in ten of the 1,125 names and sounds like *kuṭam*, pot. In the Sumerian list the same sign is read *dug*: the Sumerian for pot, and also the Sumerian for "good", which ends 14 of the 600 names. Leave that one sign unread and Sumerian falls from +113 to −6, and Tamil from +188 to +44.

What exploration after the results suggests, and it is exploration, not the plan's answer:

- **The two dropped Tamil lists score about nothing.** Run through the same program, they come out at +8 and 0, below Sumerian and Nahuatl.
- **One word switches Tamil's score on and off.** Old Tamil has several words for a pot. Of the four translators who worked on the two fresh lists, one offered *kuṭam*; the others offered *kalam*, *tāḻi* or *pāṉai*. With *kuṭam*, a fresh Tamil name list scores +167 (96 of 100 rounds). With the other words, the same name list scores +8.

So a pass in this contest shows that a language's word for a pot happens to sound like something its names often end in. Tamil has such a pair. So does Sumerian.

## What holds

- **Reproduction.** The lab does not run downloaded programs, so the contest was written out again from a line-by-line reading of the preprint's (`analysis/contest.py`). On the preprint's own lists it gives the archived number in every run checked: Tamil and Sanskrit, splits 0 to 9; Tamil and Akkadian, splits 20 to 29; real and scrambled. 80 of 80. Tamil +223.0 (10 of 10), Sanskrit −13.3 (4 of 10), Akkadian −2.1 (5 of 10), as published.
- **Independent program.** Google's `gemini-4-neon` wrote its own program from `protocol.md`, `analysis/METHOD.md` and `replication/FORMAT.md`, seeing none of our code or numbers. It matches the preprint's archive on the 20 splits tried, and matches our program on all 700 list-rounds of the seven control lists (`replication/`).
- **The preprint's care.** Its plans are fingerprinted, its failed tests are listed, and its inputs are archived. That is why this could be checked at all.

## The locked run

Every list through the contest for 100 rounds. The score is real names minus the same names scrambled; "rounds" is how many of the 100 had real above scrambled. A list passes with at least 80 rounds and a score of at least 46.9, a quarter of the preprint's Tamil list's.

| List | Score (mean) | Rounds above control | Passes | With the jar sign unread | With every part given one label | With pictures shuffled (runs above, of 200) | Candidate readings a sign | Names left as one part |
|---|---|---|---|---|---|---|---|---|
| Old Tamil, the preprint's list (600 of 1,125 a round) | +187.7 | 89 | yes | +44.3 (73) | +88.2 (79) | +182.4 (177) | 1.77 | 20% |
| Sumerian | +112.7 | 99 | **yes** | −6.2 (43) | +78.2 (99) | +19.6 (110) | 0.36 | 36% |
| Classical Nahuatl | +49.1 | 84 | **yes** | +44.0 (83) | +31.6 (83) | +17.6 (125) | 0.97 | 36% |
| Homeric Greek | −1.0 | 49 | no | −0.3 (52) | −0.9 (33) | +1.9 (109) | 0.13 | 80% |
| Old English | −9.0 | 42 | no | −3.8 (49) | +18.9 (79) | +54.9 (157) | 0.52 | 25% |
| Hawaiian | −19.9 | 46 | no | −19.8 (42) | −16.9 (46) | +5.8 (97) | 1.84 | 51% |
| Vedic Sanskrit, the preprint's list | −23.4 | 30 | no | −23.8 (24) | −12.7 (34) | −2.8 (85) | 0.29 | 57% |
| Biblical Hebrew | −26.6 | 23 | no | −14.6 (17) | −10.1 (31) | −8.9 (53) | 0.20 | 67% |
| Akkadian, the preprint's list | −31.9 | 20 | no | −26.6 (18) | −3.0 (42) | +21.8 (111) | 0.35 | not counted |
| Old Japanese | −110.8 | 33 | no | −13.6 (45) | −62.9 (34) | +8.5 (104) | 2.54 | 27% |

The preprint's Akkadian list with its letters mapped into the contest's sound table scores −32.9 (15 rounds), the same as unmapped. On their whole lists in rounds 0 to 9 the preprint's three lists give +223.0 (10 of 10), −13.3 (4 of 10) and +13.0 (7 of 10).

**The plan's two answers.**

- *Do unrelated languages pass?* Yes: two of seven.
- *Does Tamil stand out when built like the others?* Not answered. No fresh Tamil list was in the run.

**Overall, by the plan's rules:** Incomplete.

### What carries the passing scores

Each sign was left unread in turn, in rounds 0 to 9.

| List | Score, rounds 0 to 9 | Sign that matters most | Reading chosen for it | Score without it |
|---|---|---|---|---|
| Old Tamil, the preprint's | +131.4 | 740, the jar | *kuṭi* in 87 of 100 rounds | +1.4 |
| Sumerian | +105.3 | 740, the jar | *dug* in 100 of 100 | −16.2 |
| Classical Nahuatl | +47.1 | 520, an arrow or spear | *mitl* in 98 of 100 | +5.3 |

- **Sumerian.** The translator gave *dug* for jar, pot and vessel. In the name list *dug*, "good", is in 14 names and is the last part of every one (Lugalduga, "king + good"). Sign 740 is the last sign of 38% of seal texts, and four times in five that it appears it comes last. The two meet.
- **Nahuatl.** Here there is no sound-alike. *Mitl* is the Nahuatl for arrow, and it is the last part of nine names (Quetzalmitl, "quetzal plume + arrow"). Sign 520 comes last in 88% of its appearances.
- **Tamil.** *Kuṭam*, pot, sounds like *kuṭi*, which the preprint's list labels a "place word" along with *ūr*, town, the ending of 74 names.

In all three, one common text-final sign meets one name-final word.

### The other controls

- **Old Japanese scores −111**, far below zero, with a wide spread. Real names fit worse than scrambled ones. The public rebuttal reported +134 for a list of modern Japanese family names and the preprint's author +81 for his own Old Japanese list. Three lists of one language, three very different scores.
- **Greek and Hebrew** left most names whole (80% and 67%), as the preprint's Sanskrit list did (57%). They had almost nothing to fit and score near zero. They say little either way.
- **Negative scores are common.** Five of the seven controls, and both of the preprint's own, score below zero. The measure is not centred on zero for a language that does not fit.

### Pictures shuffled

The author's reply to the rebuttal says Tamil still leads when each sign is given another sign's picture words. For his own list that reproduces: +182 shuffled against +188 unshuffled, far above every control. It shows that the score does not depend on what the signs depict. Old English, which fails the contest proper, scores +55 with the pictures shuffled and beats its control in 157 of 200 runs.

## The lists, and why three were dropped

Ten lists were built after the lock by fresh sessions that were told nothing of the purpose. The record of each is in `lists/README.md`.

| List | Names check (ok of 50) | Words check, first try | Second try | Outcome |
|---|---|---|---|---|
| Greek | 50 | 49 ok | | run |
| Nahuatl | 50 | 49 ok | | run |
| Old English | 50 | 50 ok | | run |
| Sumerian | 49 | 48 ok | | run |
| Hawaiian | 50 | 50 ok | | run |
| Hebrew | 49 | 49 ok | | run |
| Old Japanese | 50 | 44 ok, 6 wrong: fails | 48 ok: passes | run, second translator's words |
| Finnish | 49 | 36 ok, 14 wrong: fails | 36 ok, 12 wrong: fails | dropped |
| Old Tamil A | 49 | 42 ok, 8 wrong: fails | 44 ok, 6 wrong: fails | dropped |
| Old Tamil B | 50 | 44 ok, 6 wrong: fails | 39 ok, 11 wrong: fails | dropped |

A words sample fails with more than 5 wrong. In every dropped list the names were sound. The words failed because the checkers looked each one up and could not find it, in the sense given, in the early texts the prompt named.

**Two of the three failures trace to prompts written for this study before the lock.**

- **Tamil.** The preprint's checker failed a Tamil word only if it was "a modern word with no attestation in early or classical Tamil literature". This study used one prompt for every language, and it fails a word "not attested in early" texts. Words first recorded in classical works some centuries after the Sangam poems pass the preprint's rule and fail this one. The preprint's own Tamil picture words passed its check 47 of 50; by this study's rule they might not, and that was not tested.
- **Finnish.** The translator's prompt allowed loans as old as Proto-Finnic. The checker's prompt fails any loan from another language family. Both translators kept old Germanic and Baltic loans and both failed.

Eugene was told as each list failed. The rule was applied as locked.

## Exploration after the results

Everything in this section was run after the locked results existed. It is exploratory. Programs and outputs are in `explore/`.

**The dropped lists, through the same program** (`explore/with_dropped_lists.py`).

| List | Score | Rounds above control | With the jar sign unread | With pictures shuffled (of 200) | Reading for the jar sign |
|---|---|---|---|---|---|
| Old Tamil A (second translator's words) | +7.7 | 59 | +12.6 (61) | +23.7 (122) | none |
| Old Tamil B (second translator's words) | −0.1 | 54 | −2.5 (52) | +30.5 (117) | *kal*, stone, in 66 rounds |
| Finnish (469 names) | −16.8 | 28 | −18.5 (19) | −6.0 (81) | none |

Had these counted, the plan's rules would have read: unrelated languages pass; Tamil does not stand out; "does not show the language". They did not count.

**The same Tamil name lists with their first translators' words** (`explore/tamil_first_translators.py`).

| Name list | Words given for "jar, pot, vessel, handle" | Score | Rounds above control | Reading for the jar sign | Score with the jar sign unread |
|---|---|---|---|---|---|
| Tamil A, first translator | *tāḻi, cāṭi; kuṭam, kalam; kalam; kāmpu, piṭi* | +166.9 | 96 | *kuṭi* in 100 of 100 | +18.2 (66) |
| Tamil A, second translator | *tāḻi; kalam, tāḻi; kalam; piṭi, kāmpu* | +7.7 | 59 | none | +12.6 (61) |
| Tamil B, first translator | *tāḻi, cāṭi; kalam, tāḻi; kalam; kāmpu, piṭi* | −26.0 | 40 | *kal* in 65 | −24.2 (32) |
| Tamil B, second translator | *tāḻi, kalam; kalam, pāṉai; kalam; piṭi, kāmpu* | −0.1 | 54 | *kal* in 66 | −2.5 (52) |

The name list and its labels are the same in the first two rows. One word differs that matters: *kuṭam*. The translator the preprint used for its replication also gave *kuṭam*.

**How this sits with what the two sides reported.** The rebuttal's two rebuilt Tamil lists scored +4 and +49. Ours scored 0, +8, −26 and +167. The author's reply attributes the low scores to the wrong mix of name kinds. Our lists were asked for his mix and came within the band set (51% and 56% people against his 47%). On this evidence the difference between a high and a low Tamil score is the word for pot, and the mix is not what decides it. That reading is ours and rests on four translations.

## Departures from the plan

1. **Amendment 1.** A Tamil letter the sound table does not know (ḵ) is mapped to ḥ.
2. **Amendment 2.** The Hebrew compiler wrote name parts as one string; the build program now splits it.
3. **One checker used a web browser.** The Hawaiian checker read a dictionary site through the Chrome browser because the site refuses scripted access. It was not asked to. Later checkers were told not to.
4. **How sessions were briefed.** Each got one sentence pointing at a file with its prompt, not the prompt pasted in. The content was the prompt.
5. **Working files.** Several sessions kept scripts or downloads outside the folder they were told to use and deleted them afterwards.

## Limits

- **The main question was not answered as planned.** The study is incomplete by its own rule, and the reason is partly its own design.
- **This is about the language contest only.** The preprint's 150 sign readings rest on other tests, which were not examined. A reading can be right even if the contest cannot show the language.
- **One model family built and checked every list,** the preprint's and ours.
- **One list a language, and lists differ.** Japanese shows how much: −111 here, +81 and +134 elsewhere. The same is true of Sumerian, which the author's own list put at +263 and the rebuttal's at +104.
- **Splitting was left to each session.** Lists that leave names whole cannot score. Only four of the seven controls (Sumerian, Nahuatl, Old English, Old Japanese) split names about as finely as a contest needs.
- **Labels differ between labelers.** Hawaiian's labeler put every part of unknown meaning under "personal name"; the others sorted such parts into places, gods and peoples.
- **The spelling maps are rough.** Dropping the index numbers from Sumerian words makes *dug* "pot" and *dug* "good" the same spelling. Sumerologists write them apart, and whether they sounded alike is not settled. The contest compares spellings, so for the contest they are the same.
- **The exploration is four translations of one language.** It shows what happened here. It does not measure how often a Tamil translator would choose *kuṭam*.
- **Seven controls is a small number.** Two of seven passing does not give a rate.

## What a proper second study would need

The check on picture words worded as the preprint's was; the Finnish prompts made consistent; several translators a list, so that the choice of one word can be seen for what it is; and a rule fixed in advance for how finely names are split.

## What this means

A preprint claims to have found the language of the Indus script: an early relative of Tamil. Its evidence for the language is a contest in which Tamil names fit the seal texts and Sanskrit and Akkadian names do not. We wrote the contest out again and it does what the paper says. We then gave it seven languages that nobody thinks the Indus people spoke. Two of them passed, and the stronger one, Sumerian, passed for the same reason Tamil does: the commonest sign looks like a jar, and the language's word for a pot happens to sound like a word its names often end in. When Tamil's translators chose a different word for pot, Tamil stopped passing. Our own main test, which needed a Tamil list built like the others, came out incomplete, because both such lists failed a check we had set more strictly than the paper's own. So this is not the clean, pre-registered refutation it was meant to be. What it does show is how the contest works: it rewards one coincidence on one sign. That is not evidence about what language the seals are written in. It says nothing about whether the paper's readings of individual signs are right.
