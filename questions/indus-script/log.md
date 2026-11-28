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
