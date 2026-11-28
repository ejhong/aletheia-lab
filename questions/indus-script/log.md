# Log

Dated entries, newest last: what was tried, what happened, what next.

## 2026-11-27: design (Claude Fable 5.2, Anthropic; directed by Eugene)

- Eugene sent Siva Raj's announcement of the preprint and asked why the lab had not tried such a thing. I
  proposed two questions: check this claim now, then make an attempt of our own with the same controls as its
  gate. He said yes. Opened #145 (active) and #146 (proposed; target for him to pick).
- Downloaded the preprint's files from Zenodo (every MD5 matched) and the corpus file it used. The corpus file's
  SHA-256 equals the one in the preprint's manifests.
- Read the paper's section 6, the plans and results of REP-1 (Tamil against Sanskrit), REP-3 (Akkadian) and the
  Munda contest, and the three program files of the contest, line by line.
- Tried to run the preprint's program on its own inputs. The session's safeguards refused, under the lab's rule
  against running downloaded programs. Wrote the procedure out again as `analysis/contest.py` and checked it
  against the archive: 80 of 80 runs identical, readings included.
- Priors, before any control exists. The preprint is careful and I expect its numbers to be what it says they
  are, which they were. On the question itself: I give about 30% to "not specific", 25% to "mixed", 25% to
  "specific" and 20% to "rests on the preprint's own Tamil list". I lean towards a control passing because the
  exploration showed how the Tamil score arises: one very common final sign, one name ending that sounds like
  its picture word. A language needs one such coincidence to score. I have a stake of a kind: the preprint was
  written with a Claude model, and so is this check.
- Exploration on the preprint's own lists (`explore/`): leaving the jar sign unread takes Tamil from +223 to
  +87; giving every name part one label takes it to +62; the Akkadian lists lose letters the sound table does
  not know. Chose eight control languages with names built from several parts, a fresh Tamil list built by the
  same prompts, 600 names a round and 100 rounds. Wrote the prompts, the letter maps, `build_inputs.py` and
  `run_all.py`. Dry run with no control inputs: the preprint's Tamil list passes at this size (+188, 89 of 100).
- A sub-agent (Claude Opus 5.5) traced the public dispute. Both sides have run control languages themselves. Open
  Indus reports Japanese surnames +134 (7 of 10), Sumerian +104, Egyptian +78, Finnish +64, and two rebuilt Old
  Tamil lists at +4 and +49. The author's reply table gives Sumerian +263 (10 of 10), Old Japanese +81 (9 of 10)
  and Finnish +19 (8 of 10), and says Tamil leads when the pictures are shuffled. I read his table and the Open
  Indus results file myself. So "do controls pass" is largely answered by the parties; what is in dispute is
  whether Tamil stands out when its list is built like the others. Rewrote the question and rules around that:
  two fresh Tamil lists, eight controls, one set of prompts, the preprint's own mix of name kinds, and the
  shuffled-pictures analysis for every list.
- Revised priors: about 45% that fresh Tamil does not stand out ("does not show the language"), 35% mixed, 20%
  that it stands out cleanly.
- Google's `gemini-4-neon` reviewed the plan twice (`review/`). Changes are listed there. Wrote
  `analysis/METHOD.md` so that the replication can be programmed from the plan alone.
- Dry run of the final `run_all.py` with no new list present: the preprint's Tamil list scores +182 with the
  pictures shuffled against +188 unshuffled; leaving the jar sign unread takes it to +44.
- Spending so far: $0.75 (two review calls).

## 2026-11-27, after the lock (03:15 UTC on the 28th)

- Locked and pushed (`90d86d6`).
- Started ten translators and ten name compilers, each a fresh Claude Opus 5.5 session. Each was given one
  sentence pointing at a task file that holds its filled prompt from `prompts/`, and the instruction to read
  no other file. The ten translators have finished: entries filled, of 171: Tamil A 153, Tamil B 148,
  Japanese 132, Greek 128, Old English 152, Hebrew 152, Nahuatl 108, Sumerian 106, Hawaiian 151, Finnish 150.
  Their files are in `lists/<language>/words.json` and `numbers.json`.
- One letter outside the sound table (the Tamil āytam): amendment 1.
- Replication: Google's `gemini-4-neon` wrote its own program from `protocol.md`, `analysis/METHOD.md` and
  `replication/FORMAT.md` alone (`replication/google/replicate_round1.py`, 482 lines, one request, $0.64). Run
  on the preprint's Tamil and Sanskrit lists, splits 0 to 9, it gives the archive's numbers to two decimals and
  the same readings in 20 of 20 splits. So two programs written independently of the preprint's agree with its
  archive.
- The ten name compilers finished over about 45 minutes. Sources they reported: Sumerian from the ePSD2 name
  glossaries; Greek from the Perseus treebank of Homer and Hesiod; Nahuatl from the Visual Lexicon of Aztec
  Hieroglyphs; Old Japanese mostly from the compiler's knowledge, spot-checked on Wikipedia and a Man'yōshū
  text; Old English from the compiler's knowledge with a few Bosworth-Toller look-ups; Hebrew from the
  compiler's knowledge alone; Hawaiian looked up in the Pukui-Elbert and Place Names dictionaries; Finnish from
  the Kalevala, the Kanteletar and Forsman 1891; Tamil A checked against the Project Madurai Sangam texts;
  Tamil B from the Wikipedia list of Sangam poets and the compiler's knowledge. None reported meeting the
  preprint or the rebuttal.
- How finely names were split differs a great deal between lists (25% to 80% of names left as one part). Left
  as built, as the plan says.
- Hebrew's parts came as one string joined by " + ": amendment 2. The first Hebrew labeler session was given
  single letters and said so; discarded and rerun.
- Finnish came out short twice once names with the same parts were merged (529, then 469).
- Checks. Passed at once: Greek, Nahuatl, Old English, Sumerian, Hawaiian, Hebrew. Japanese failed on its words
  (6 wrong), was retranslated and passed (2 wrong). Finnish, Tamil A and Tamil B each failed on their words
  twice and are dropped. In every case the names passed. Details and the reason in `lists/README.md`. Two of
  the three failures trace to prompts I wrote before the lock: a check on Tamil stricter than the preprint's
  own, and a Finnish translator's prompt that allowed what the checker's prompt forbids. I told Eugene as each
  failed and offered to amend the check before any contest result existed; with no instruction to do so, the
  locked rule was applied.
- The Hawaiian checker read a dictionary site through the Chrome browser because the site refuses scripted
  access. I had not asked for that and told Eugene. Later checkers were told not to use a browser.
- So the locked run has seven controls and no fresh Tamil list. By the plan's rules its overall reading will be
  "Incomplete". The three dropped lists will be run separately, as labelled exploration.
- No contest has been run on any new list up to this point.

## 2026-11-27, results

- Locked run (`analysis/run_all.py`): seven controls and the preprint's three lists. Overall "Incomplete" by the
  plan's rule. Sumerian +112.7 (99 of 100) and Nahuatl +49.1 (84 of 100) pass; the pass floor is 46.9. Sumerian's
  score is the jar sign read *dug* (pot, and "good" at the end of 14 names); without that sign it is −6.2.
- Google's program run on the seven control lists: all 700 list-rounds agree with ours to two decimals.
- Exploration after the results (`explore/`): the three dropped lists through the same program (Tamil A +7.7,
  Tamil B −0.1, Finnish −16.8); the two Tamil name lists with their first translators' words (Tamil A +166.9
  with *kuṭam* on offer, Tamil B −26.0 without); the jar sign's readings when the pictures are shuffled.
- Against my priors: I gave 45% to "Tamil does not stand out", 35% mixed, 20% stands out. The locked run could
  not say. The exploration points to "does not stand out", and for a reason sharper than I expected: one word.
  I did not foresee that the study would fail on its own check.
- Wrote `RESULTS.md`, the figures (`analysis/make_figures.py`), the site page, and the Deep memory topic entry.
- Spending in all: $1.39 (Google's model: two review rounds, one replication program).
