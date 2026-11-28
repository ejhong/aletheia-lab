# Does the Indus preprint's language contest pick out Tamil?

Issue #145 · Lane: data · Budget: $10 · Written 2026-11-27 by Claude Fable 5.2 (Anthropic), directed by the lab's director

## Question

A preprint of November 2026 reads the Indus script as an early Dravidian language, through Old Tamil (Siva Raj
with Claude, *Indus Script Read as Early Dravidian, with AI Assistance*, v0.7, doi:10.5281/zenodo.24383779, not
peer reviewed). Its case that the language is Dravidian rests on one test, which it calls a contest: Old Tamil
names fit the seal texts far better than the same names scrambled, and Vedic Sanskrit and Akkadian names do not.

**When Tamil and eight languages with no claim on the Indus seals are each given name lists built the same way,
by sessions told nothing of the purpose, does Tamil stand out in that contest?**

## Why it matters

The preprint is unusual among claimed decipherments: its plans were fingerprinted before each test, its failures
are listed, and its lists and programs are public. That makes its central test checkable by someone else, and
within three days someone had.

What each side now says, as read on 27 November 2026. We have not verified either side's numbers.

- **The rebuttal** (the Open Indus project, announced by Harsha G.;
  <https://x.com/harshaog/status/2126184882095177897>, repository `HarshInvader/open-indus`, file
  `experiments/raj_check/RESULTS.md` at commit `1c1da07`). It reports the preprint's 40 headline runs reproduced
  exactly; Japanese family names scoring +134 against Tamil's +223, above their control in 7 of 10 splits;
  Sumerian +104 (9 of 10), Egyptian +78 (7 of 10), Finnish +64 (10 of 10); Tamil scoring the same with each
  sign's picture words moved to a random wrong sign (+224); and two Old Tamil lists it rebuilt from the same
  kinds of source scoring +4 and +49.
- **The author's reply** (<https://x.com/jaravis/status/2126493377537704405>, a table marked "not yet in the
  paper"). His own runs give Sumerian +263 (above its control in 10 of 10 splits), Old Japanese +81 (9 of 10)
  and Finnish +19 (8 of 10), beside Tamil's +223. With the pictures shuffled onto other signs he reports Tamil
  +311 and the other three +49 to +87. He holds that the contest was meant to choose among relevant candidates,
  that unrelated languages can share structure, that Tamil "is structurally aligned with the way the Indus
  script is written", and that the rebuilt Tamil lists are skewed, being about 70% personal names where his is a
  broad mix.

So both sides agree that languages unrelated to the Indus score above their scrambled controls. What they
dispute is whether Tamil still stands out, and each side's evidence on that uses lists it built itself: the
preprint's Tamil list is the project's own, and the rebuttal's rebuilt lists are, on the author's account,
built with the wrong mix. Neither has put Tamil and the controls through one list-building procedure fixed in
advance. That is what this study does, with the mix of name kinds set to the preprint's own.

If Tamil, built like the others, comes out clearly on top, the contest is doing what the preprint says and the
rebuttal's rebuilt lists were unlucky or badly mixed. If Tamil lands among the controls, the published result
depends on how the preprint's own list was made, and the contest does not show the language.

## What the contest is

From the preprint's section 6 and its archived test REP-1 (plan, program, inputs, outputs). The exact
procedure is in `analysis/METHOD.md`, which is part of this plan.

1. **Signs and picture words.** 69 common signs. For each, an AI judge that saw only the sign wrote four English
   words for what it shows ("jar", "fish", "person with a yoke"): 171 different English words in all.
2. **Picture words in the language.** A translator turns each English word into at most two native words of the
   language being tested.
3. **Names.** A list of ancient proper names of that language, each split into its meaningful parts, each part
   given one of 22 categories (animal, place word, title, grammatical ending, and so on).
4. **Reading.** A sign may take any name part that sounds like one of its picture words (same first letter,
   sound distance at most 0.5 on the preprint's table). The seals and the names are each split in half at
   random. On the first halves, each sign is given the candidate that most improves the fit of the seal texts to
   a model of how names are built (which part follows which, and which category follows which). The readings
   are then scored on the second halves.
5. **Control.** The same is done with the name parts shuffled among the names. The score is real minus shuffled.

The preprint reports Old Tamil +223 (above its shuffled control in 10 of 10 random splits), Vedic Sanskrit −13
(4 of 10) and Akkadian −2 (5 of 10).

## Data and sources

| Short name | What | Source |
|---|---|---|
| Preprint | The paper, its test archive (plans, programs, word and name lists, per-split outputs), rules and register | Zenodo, doi:10.5281/zenodo.24383779, v0.7, CC BY 4.0 |
| Seal texts | The corpus file the preprint used: `inscriptions.csv`, 5,679 rows of sign numbers with site, object type and reading direction | GitHub `yajnadevam/lipi`, commit `fc8813a52e183d19c441631dc26c33a4dccbea39`; its SHA-256 equals the one in the preprint's manifest |
| New lists | Picture words, names and labels for ten lists, built after the lock by the prompts in `prompts/` | Made by this study; kept in `lists/` |

Checksums, dates and licences are in `MANIFEST.md`. The preprint's files and the corpus stay out of the
repository (`data/`); the 69 signs' English picture words are copied to `inputs/sign_english_words.json` under
the preprint's CC BY 4.0 licence.

## What was seen before the lock

Everything in this section used the preprint's own archived lists and nothing else. No new list had been built.
Programs and outputs are in `explore/` and are exploratory.

1. **Our program reproduces the archive.** The lab does not run downloaded programs, so the contest was written
   out again from a line-by-line reading of the preprint's (`analysis/contest.py`). On the preprint's lists it
   gives the same number, to two decimal places, and the same readings in all 80 archived runs checked: Tamil and
   Sanskrit, splits 0 to 9, and Tamil and Akkadian, splits 20 to 29, real and shuffled. Tamil +223.0 (10 of 10),
   Sanskrit −13.3 (4 of 10), Akkadian −2.1 (5 of 10), as published.
2. **One sign carries most of the Tamil score.** Sign 740, the commonest sign, usually ends a text. Its picture
   words are "jar, pot, vessel, handle". In 9 of 10 splits it is read *kuṭi*, a word for a settlement or clan
   that sounds like *kuṭam*, pot. With that one sign left unread, Tamil falls from +223 to +87.
3. **The labels carry most of it too.** With every name part given the same label, Tamil falls to +62 (8 of 10).
   *kuṭi* is in about a dozen of the 1,125 names; it scores as text-final because it carries the label "place
   word", which it shares with *ūr*, town, the ending of 74 names.
4. **The pictures do not matter to the score.** With the signs' picture words dealt out again among the signs
   (20 shuffles), the preprint's Tamil list scores +182 against +188 unshuffled, at the size used below. Both
   sides of the dispute report the same.
5. **The two published controls had little to work with.** 57% of the Sanskrit names are a single unsplit word,
   against 20% of the Tamil ones, and a name of one part has no structure to fit. Akkadian had 0.5 candidate
   readings a sign against Tamil's 2.5. In the Akkadian run, 229 of 505 name parts and 88 of 177 picture words
   contain letters (š, ḫ, q, w, z) that the contest's sound table does not know and silently drops.
6. **The Tamil list was not built like the controls' lists.** It is the project's own file, with names split
   down to grammatical endings and the category scheme designed on it. The Sanskrit and Akkadian lists were
   built new by agents told nothing of the project. The preprint's REP-1 plan says as much.
7. **At the size this plan uses** (600 names drawn for each round, 100 rounds) the preprint's Tamil list scores
   +188 and is above its control in 89 rounds; Sanskrit −23 (30 rounds); Akkadian −32 (20 rounds), and −33 (15
   rounds) with its letters mapped into the table. With the jar sign unread, Tamil scores +44 (73 rounds).

## Method

### The lists

Ten lists are built after the lock, each by the same four prompts with only the language's details changed
(`prompts/translator.txt`, `names.txt`, `labeler.txt`, `checker.txt`; details in `prompts/languages.json`). The
prompts are the preprint's REP-1 prompts with these changes: the target is about 650 names, not 1,400; the
examples are language-neutral; the mix of name kinds is asked for; the translator also gives eight number
words; the sessions list the sources they consulted.

| List | Language | Early sources named in the prompt |
|---|---|---|
| Fresh Tamil A, Fresh Tamil B | Old Tamil | Sangam poems, Tamil-Brahmi inscriptions |
| Control 1 | Old Japanese | Kojiki, Nihon shoki, Man'yōshū |
| Control 2 | Ancient Greek | Homer and Hesiod |
| Control 3 | Old English | Texts before 1100 |
| Control 4 | Biblical Hebrew | The Hebrew Bible |
| Control 5 | Classical Nahuatl | Sixteenth-century sources |
| Control 6 | Sumerian | Third-millennium texts |
| Control 7 | Hawaiian | Traditional sources recorded in the nineteenth century |
| Control 8 | Finnish | Kalevala, Kanteletar, old native names in early documents |

**Why these eight.** None is a language that the preprint, or the literature it cites, proposes for the seals.
Sumerian was spoken by trading partners of the Indus cities, as Akkadian was, and the preprint used Akkadian as
a control on that ground. All eight have a stock of early names built from several meaningful parts and analysed
by scholars, so each has a fair chance of fitting a name model, which the preprint's two controls lacked. They
come from seven language families and five parts of the world. Old Japanese, Sumerian and Finnish have been run
by both sides of the dispute on their own lists. The choice was made without trying any word of any of them
against the signs.

**Why two Tamil lists.** Whether Tamil stands out depends on its list as much as on the controls'. Two lists,
each with its own translator, name compiler, labeler and checker, show how much one list differs from another.

**The mix of name kinds.** The preprint's Tamil list is 47% people, 21% places, 9% gods, 8% groups, and the
rest lineages, hills, stars, rivers and others. The author's objection to the rebuttal's rebuilt Tamil lists is
their mix. Every list here is asked for the preprint's mix (`prompts/names.txt`), and a list in which people
are under 35% or over 60% of the names is built again.

**Who builds them.** Each role is a fresh session of Claude Opus 5.5 (Anthropic) given its prompt and nothing
else: no mention of the Indus, seals, signs or this study. For each list: a translator; a name compiler, with
web access; a labeler, which sees only name parts and their glosses; a checker, with web access. The preprint
used the same model family in the same roles. A session whose note shows it consulted the preprint, the
rebuttal or their repositories is discarded and run again.

**The check.** The checker gets 50 names and 50 word pairs (one pair for each English word and each word given
for it), drawn by `analysis/build_inputs.py samples` (seed 20261127) from the list as the compiler wrote it, and
marks each ok, wrong or cannot verify. A sample fails if more than 5 of the 50 are wrong or fewer than 40 are
ok. If the names fail, the name compiler and labeler are run again; if the words fail, the translator is run
again; each once, by new sessions with the same prompts, and checked again. A list that fails twice is dropped
and reported.

**Size.** Names with the same parts in the same order count once. A list with fewer than 550 different names is
built again once; if still short it is run at its size and marked. A list with more than 600 is cut to 600
names, once, at random (seed 20261127), so that every new list enters at one size.

**Spelling.** The contest has one table of sounds, made for Tamil and Sanskrit, and drops any letter it does not
know. Each control language therefore has a fixed letter map (`prompts/languages.json`, written before the
lock), applied by program, in order, to its name parts, picture words and number words alike, so that the two
sides of every comparison are spelled the same way. `build_inputs.py` stops if any letter is still outside the
table. The letter is then mapped to the table's nearest sound by place and manner (a missing sibilant to `s`
or `ś`, a missing stop to the stop of the same place, a missing vowel to the nearest of a e i o u), and the
change is recorded in `amendments.md` before any contest run for that language.

**No hand edits.** Nobody edits a list. From the sessions' files to the contest's inputs, only
`analysis/build_inputs.py` touches them. A part with no valid label is labelled "other"; if more than 2% of a
list's parts have none, the labeler is run again, once.

### The contest

`analysis/contest.py`, as checked against the archive, with the preprint's settings: pictures required, each
name counted once, sound distance at most 0.5, number signs read as the language's number words.

- **Main analysis.** 100 rounds (seeds 0 to 99) for every list. A new list is used whole (600 names). The
  preprint's own lists are longer, and 600 of their names are drawn in each round, as the preprint did to bring
  lists to one size.
- **Lists run.** The ten new lists, and the preprint's own Tamil, Sanskrit and Akkadian lists.
- **A list's result** is the mean over the 100 rounds of real minus shuffled, and the number of rounds in which
  that difference is above zero. The median, standard deviation and quartiles are reported too. The rounds
  reuse the same seals and names, so their spread measures the splitting and is not a standard error of the
  language's score; no significance test is made from it.

### The rules

**A list passes** if it is above its shuffled control in at least 80 of 100 rounds and its mean is at least a
quarter of the mean of the preprint's Tamil list in the same analysis. (The preprint's own mark was 8 of 10
splits, and 80 of 100 in its Munda test. The quarter keeps a small steady excess from counting.)

Two answers are given, then one overall reading.

**Answer 1. Do unrelated languages pass?** "Yes" if two or more controls pass; "one does" if exactly one;
"no" if none.

**Answer 2. Does Tamil stand out when built like the others?**

- "Yes" if both fresh Tamil lists pass and each has a higher mean than every control.
- "No" if any control's mean is at least the average of the two fresh Tamil means, or if neither fresh Tamil
  list passes.
- "Partly" otherwise.

If Tamil were no different from the controls, the chance of both its lists outranking all eight would be 1 in
45.

**Overall**, checked in this order:

1. **Calibration failed** if the preprint's own Tamil list is not above its control in 80 of 100 rounds. (It
   was in the run before the lock; this guards against a fault in the run.)
2. **Incomplete** if fewer than six controls, or no fresh Tamil list, could be run. With one fresh Tamil list,
   "both" and "the average" above mean that list.
3. **Supports the preprint** if Answer 2 is "yes", at most one control passes, and no control's mean reaches
   half the fresh Tamil average.
4. **Does not show the language** if Answer 2 is "no".
5. **Mixed** otherwise.

### Also reported, not part of the rules

For every list:

- **Pictures shuffled.** The signs' picture words dealt out again among the signs, 20 shuffles, each over rounds
  0 to 9. If a list scores as well with the wrong pictures, its score does not come from what the signs show.
  The author's position is that Tamil leads here; the ranking of the lists under shuffling is reported.
- **The jar sign (740) left unread**, 100 rounds, and the reading chosen for it.
- **Every name part given the same label**, 100 rounds.
- For the preprint's lists, the whole list in rounds 0 to 9, the preprint's own layout.
- Names of one part, candidate readings a sign, signs read, name parts found in two or more names, the mix of
  name kinds, and the checker's counts.

For every list that passes, and the preprint's Tamil list: each sign left unread in turn (rounds 0 to 9), to
show whether one sign carries the score. The preprint's Akkadian list is also run with its letters mapped into
the sound table.

## What would count for and against

- **For the preprint's contest:** both fresh Tamil lists pass and outrank every control, and no control comes
  within half of them. Stronger if that holds with the jar sign unread.
- **Against it:** a control scores as high as fresh Tamil, or fresh Tamil does not pass. Then the published
  Tamil score reflects how one list was made.
- **Neither clearly:** Tamil ahead on average with a control passing, or one fresh Tamil list high and one low.

## Limits known now

- **This tests the language contest only.** The preprint's 150 sign readings rest on other tests (fit to text
  structure, blind judges matching pictures and meanings). Those are not examined. A reading may be right even
  if the contest cannot show the language.
- **One model family built every list**, the preprint's and ours, and checked them. It may make the same
  mistakes in building as in checking, most of all for Sumerian, Nahuatl and Hawaiian.
- **One list per control language.** A list of 600 names is a sample of a naming tradition and another sample
  could score differently, as the two Tamil lists will show for Tamil.
- **The category scheme was designed on Tamil names.** It may describe other naming traditions less well, which
  would count against the controls.
- **How finely names are split is left to each session**, as it was in the preprint's controls. A session that
  splits off endings gives the contest more to fit. The share of one-part names is reported.
- **The spelling maps are rough.** They put eight languages into a sound table made for two others. Hawaiian
  and Japanese have few distinct sounds, which gives the contest more sound-alikes to choose from; that is a
  property of those languages under the contest's own rule.
- **Web access.** The name compilers and checkers can search the web and could meet the preprint or the
  rebuttal. They are asked to list what they consulted.
- **Eight controls and two Tamil lists are small numbers.** The 1-in-45 figure assumes the lists are
  exchangeable, which they are only roughly.
- **The new lists are 600 names; the preprint's Tamil list is 1,125.** Scores grow with list size, so the new
  lists are compared with each other and with the preprint's list sampled to 600.
- **The name lists come from texts**, most of them later than the seals, as the preprint says of its own.

## Checks by another company's model

Before the lock, Google's `gemini-4-neon` reviews this plan (`review/`). After the run, the same model writes its
own program from this plan and `analysis/METHOD.md` alone, checks it against the preprint's archived outputs,
and its numbers for every list are compared with ours (`replication/`).

## Budget

$10 for the uses of Google's model. The list-building sessions run inside the lab's Claude session and are not
billed separately.

## Authorship

AI did this work. Claude Fable 5.2 (Anthropic) designed and ran it, with Claude Opus 5.5 sessions building the
lists; Google's `gemini-4-neon` reviews and replicates. the lab's director directed it. The preprint under test was
itself written with Claude, by Siva Raj, who has no part in this study and has not been contacted. Nor has the
Open Indus project.
