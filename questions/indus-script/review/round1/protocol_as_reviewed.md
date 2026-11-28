# Does the Indus preprint's language contest tell Tamil from languages with no link to the Indus?

Issue #145 · Lane: data · Budget: $10 · Written 2026-11-27 by Claude Fable 5.2 (Anthropic), directed by the lab's director

## Question

A preprint of November 2026 reads the Indus script as an early Dravidian language, through Old Tamil (Siva Raj
with Claude, *Indus Script Read as Early Dravidian, with AI Assistance*, v0.7, doi:10.5281/zenodo.24383779, not
peer reviewed). Its case that the language is Dravidian rests on one test, which it calls a contest: Old Tamil
names fit the seal texts far better than the same names scrambled, and Vedic Sanskrit and Akkadian names do not.

**Put through that same contest, do languages with no possible link to the Indus fail it, as Sanskrit and
Akkadian did, or do some of them pass, as Tamil did?**

## Why it matters

The preprint is unusual among claimed decipherments: its plans were fingerprinted before each test, its failures
are listed, and its lists and programs are public. That makes its central test checkable by someone else.

A public rebuttal (Harsha G., 27 November 2026) says the paper's code, given Japanese in place of Tamil, also
"decoded" the seals. A fluent-looking reading in another language does not by itself answer the preprint, which
already scores each language against its own scrambled names. The question that does answer it is whether an
unrelated language can pass the contest's own pass mark. The preprint ran two such controls. Both had little
chance of passing for reasons that have nothing to do with language (see "What was seen before the lock"). This
study runs eight more, chosen to have a fair chance.

If no control passes, the contest does what the preprint says it does, and the rebuttal does not reach it. If
controls pass, a pass does not show the language, and the Tamil result is not evidence for Dravidian.

## What the contest is

From the preprint's section 6 and its archived test REP-1 (plan, program, inputs, outputs):

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
| Control lists | Picture words, names and labels for nine lists, built after the lock by the prompts in `prompts/` | Made by this study; kept in `lists/` |

Checksums, dates and licences are in `MANIFEST.md`. The preprint's files and the corpus stay out of the
repository (`data/`); the 69 signs' English picture words are copied to `inputs/sign_english_words.json` under
the preprint's CC BY 4.0 licence.

## What was seen before the lock

Everything in this section used the preprint's own archived lists and nothing else. No control language had
been built. Programs and outputs are in `explore/` and are exploratory.

1. **Our program reproduces the archive.** The lab does not run downloaded programs, so the contest was written
   out again from a line-by-line reading of the preprint's (`analysis/contest.py`). On the preprint's lists it
   gives the same number, to two decimal places, and the same readings in all 80 archived runs checked: Tamil and
   Sanskrit, splits 0 to 9, and Tamil and Akkadian, splits 20 to 29, real and shuffled. Tamil +223.0 (10 of 10),
   Sanskrit −13.3 (4 of 10), Akkadian −2.1 (5 of 10), as published.
2. **One sign carries most of the Tamil score.** Sign 740, the commonest sign, usually ends a text. Its picture
   words are "jar, pot, vessel, handle". In 9 of 10 splits it is read *kuṭi*, a word for a settlement or clan
   that sounds like *kuṭam*, pot. With that one sign left unread, Tamil falls from +223 to +87.
3. **The labels carry most of it too.** With every name part given the same label, Tamil falls to +62 (8 of 10).
   *kuṭi* is in about a dozen of the 1,125 names; it scores as text-final because it carries the label "place word",
   which it shares with *ūr*, town, the ending of 74 names.
4. **The two controls had little to work with.** 57% of the Sanskrit names are a single unsplit word, against
   20% of the Tamil ones, and a name of one part has no structure to fit. Akkadian had 0.5 candidate readings a
   sign against Tamil's 2.5. In the Akkadian run, 229 of 505 name parts and 88 of 177 picture words contain
   letters (š, ḫ, q, w, z) that the contest's sound table does not know and silently drops.
5. **The Tamil list was not built like the controls' lists.** It is the project's own file, made while the
   readings were being worked out, with names split down to grammatical endings and with the category scheme
   designed on it. The Sanskrit and Akkadian lists were built new by agents told nothing of the project.
6. **At the size this plan uses** (600 names drawn for each round, 100 rounds) the preprint's Tamil list scores
   +188 and is above its control in 89 rounds; Sanskrit −23 (30 rounds); Akkadian −32 (20 rounds), and −33 (15
   rounds) with its letters mapped into the table. With the jar sign unread, Tamil scores +44 (73 rounds).

Points 2 to 5 are why the control languages below were chosen as they were, and why Tamil gets a fresh list.

## Method

### The lists

Nine lists are built after the lock, each by the same four prompts with only the language's details changed
(`prompts/translator.txt`, `names.txt`, `labeler.txt`, `checker.txt`; details in `prompts/languages.json`). The
prompts are the preprint's REP-1 prompts with three changes: the target is about 650 names, not 1,400; the
examples are language-neutral; the translator also gives eight number words.

| List | Language | Early sources named in the prompt |
|---|---|---|
| Fresh Tamil | Old Tamil | Sangam poems, Tamil-Brahmi inscriptions |
| Control 1 | Old Japanese | Kojiki, Nihon shoki, Man'yōshū |
| Control 2 | Ancient Greek | Homer and Hesiod |
| Control 3 | Old English | Texts before 1100 |
| Control 4 | Biblical Hebrew | The Hebrew Bible |
| Control 5 | Classical Nahuatl | Sixteenth-century sources |
| Control 6 | Sumerian | Third-millennium texts |
| Control 7 | Hawaiian | Traditional sources recorded in the nineteenth century |
| Control 8 | Old Irish | Early literature, genealogies and annals |

**Why these eight.** None has any proposed connection with the Indus cities. All have a large stock of early
names that are built from several meaningful parts and have been analysed by scholars, so each has a fair chance
of fitting a name model, which the preprint's two controls lacked. They come from six language families and
five parts of the world. Old Japanese is the language of the public rebuttal. The choice was made before any
list existed and without trying any word of any of them against the signs.

**Who builds them.** Each role is a fresh session of Claude Opus 5.5 (Anthropic) given its prompt and nothing
else: no mention of the Indus, seals, signs or this study. For each list: a translator; a name compiler, with
web access; a labeler, which sees only name parts and their glosses; a checker, with web access. The preprint
used the same model family in the same roles.

**The check.** The checker gets 50 names and 50 word pairs drawn by `analysis/build_inputs.py samples` (seed
20261127) and marks each ok, wrong or cannot verify. If more than 5 of either 50 are wrong, that list is built
again once by a new session with the same prompt. If it fails again the language is dropped and reported.

**Spelling.** The contest has one table of sounds, made for Tamil and Sanskrit, and drops any letter it does not
know. Each control language therefore has a fixed letter map (`prompts/languages.json`, written before the
lock), applied by program to its name parts, picture words and number words alike, so that the two sides of
every comparison are spelled the same way. `build_inputs.py` stops if any letter is still outside the table. If
that happens the map is extended for that letter, and the change is recorded in `amendments.md`, before any
contest run for that language.

**No hand edits.** Nobody edits a list. From the agents' files to the contest's inputs, only
`analysis/build_inputs.py` touches them. Names with identical parts count once. A part with no valid label is
labelled "other"; if more than 2% of a list's parts have none, the labeler is run again.

### The contest

`analysis/contest.py`, unchanged from the version checked against the archive, with the preprint's settings:
pictures required, each name counted once, sound distance at most 0.5, number signs read as the language's
number words.

- **Rounds.** 100 rounds (seeds 0 to 99) for every list. In each round 600 names are drawn at random from the
  list, as the preprint did to bring lists to one size, so that every language is tested at the same size.
- **Lists run.** The nine new lists, and the preprint's own Tamil, Sanskrit and Akkadian lists.
- **A list's result** is the mean over rounds of real minus shuffled, its standard error, and the number of
  rounds above zero.

### The rule

**A list passes** if it is above its shuffled control in at least 80 of 100 rounds and its mean is more than
two standard errors above zero. (The preprint's own mark for Tamil was 8 of 10 splits, and 80 of 100 in its
Munda test.)

Verdict, checked in this order:

1. **Calibration failed** if the preprint's own Tamil list does not pass. (It did in the run before the lock.)
2. **Incomplete** if fewer than six control languages could be run.
3. **Not specific** if two or more control languages pass, or if one passes with a mean at least half that of
   the preprint's Tamil list. The contest then passes languages with no link to the Indus, and a pass is not
   evidence of the language.
4. **Mixed** if exactly one control passes, with a mean under half of Tamil's. With eight controls, one could
   pass by luck.
5. **Specific** if no control passes and fresh Tamil passes. The contest then tells Tamil from all eight, and
   the rebuttal does not reach it.
6. **Rests on the preprint's own Tamil list** if no control passes and fresh Tamil does not pass either. The
   lists built the controls' way then cannot see Tamil, so the controls' failure shows nothing, and the
   published result depends on how the preprint's list was made.

### Also reported, not part of the verdict

For every list: the result with the jar sign (740) left unread; the result with every name part given the same
label; the result on the whole list in rounds 0 to 9, the preprint's own layout; the number of candidate
readings a sign, signs read, and name parts found in two or more names; and the reading chosen for the jar
sign. For any list that passes, which sign's removal costs it most. The preprint's Akkadian list is also run
with its letters mapped into the sound table.

## What would count for and against

- **For the preprint's contest:** no control passes and fresh Tamil does. Stronger still if fresh Tamil passes
  with the jar sign unread.
- **Against it:** two or more controls pass, or one passes strongly. Worse if a control's pass comes, as Tamil's
  mostly does, from one common sign meeting one common name ending.
- **Neither:** one weak pass among eight, or fresh Tamil failing with every control.

## Limits known now

- **This tests the language contest only.** The preprint's 150 sign readings rest on other tests (fit to text
  structure, blind judges matching pictures and meanings). Those are not examined. The picture test asks whether
  a word names what the sign shows, which a word of any language can do.
- **One model family built every list**, the preprint's and ours. A different family's translator might choose
  different words.
- **One translator and one name compiler per list.** A list of 650 names is a sample of a naming tradition and
  another sample could score differently. The rounds measure the splits, not a new list.
- **The spelling maps are rough.** They put eight languages into a sound table made for two others.
- **Eight controls give a coarse rate.** None passing would put the chance of an unrelated language passing
  below about one in three with 95% confidence, no lower.
- **Both name traditions are later than the seals**, as the preprint says of its own.

## Checks by another company's model

Before the lock, Google's `gemini-4-neon` reviews this plan (`review/`). After the run, the same model writes its
own program from this plan alone and its numbers are compared with ours (`replication/`).

## Budget

$10 for the two uses of Google's model. The list-building sessions run inside the lab's Claude session and are
not billed separately.

## Authorship

AI did this work. Claude Fable 5.2 (Anthropic) designed and ran it, with Claude Opus 5.5 sessions building the
lists; Google's `gemini-4-neon` reviews and replicates. the lab's director directed it. The preprint under test was
itself written with Claude, by Siva Raj, who has no part in this study and has not been contacted.
