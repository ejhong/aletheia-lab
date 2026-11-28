# The lists as the sessions wrote them

One folder a list. Every file here was written by a list-building session or made from one by
`analysis/build_inputs.py`; none was edited by hand.

- `words.json`, `numbers.json`: the translator's picture words and number words.
- `names.jsonl`: the name compiler's list.
- `parts.jsonl`, `labels.jsonl`: what the labeler was given and what it returned.
- `samples.json`, `verdicts.json`: the checker's 50 names and 50 word pairs, and its verdicts.
- `first_build/`: an earlier attempt that the plan's rules sent back, kept for the record.

Each session was a fresh Claude Opus 5.5 session given one sentence pointing at a task file that held its filled
prompt from `prompts/`, and told to read nothing else. The checkers started after the Hawaiian one were also
told not to use a web browser (see the log).

## What happened to each list (27 November 2026)

| List | Names written | Different names | One-part names | Picture words filled | Check, names (ok / wrong / cannot verify) | Check, words | Outcome |
|---|---|---|---|---|---|---|---|
| Old Japanese | 659 | 659 | 27% | 132, then 125 | 50 / 0 / 0 | first 44 / 6 / 0, fails; second 48 / 2 / 0 | Run. Second translator's words. |
| Homeric Greek | 655 | 635 | 80% | 128 | 50 / 0 / 0 | 49 / 1 / 0 | Run |
| Old English | 650 | 648 | 25% | 152 | 50 / 0 / 0 | 50 / 0 / 0 | Run |
| Biblical Hebrew | 683 | 660 | 67% | 152 | 49 / 1 / 0 | 49 / 1 / 0 | Run. Parts came as one string (amendment 2). |
| Classical Nahuatl | 662 | 650 | 36% | 108 | 50 / 0 / 0 | 49 / 1 / 0 | Run |
| Sumerian | 632 | 631 | 36% | 106 | 49 / 1 / 0 | 48 / 2 / 0 | Run |
| Hawaiian | 616 | 616 | 51% | 151 | 50 / 0 / 0 | 50 / 0 / 0 | Run |
| Finnish | 636, then 603 | 529, then 469 | 76%, then 71% | 150, then 156 | 49 / 0 / 1, then 49 / 0 / 1 | first 36 / 14 / 0, fails; second 36 / 12 / 2, fails | **Dropped**: words failed twice. Also short after one rebuild. |
| Old Tamil, fresh list A | 641 | 639 | 50% | 153, then 149 | 49 / 1 / 0, then 49 / 1 / 0 | first 42 / 8 / 0, fails; second 44 / 6 / 0, fails | **Dropped**: words failed twice. |
| Old Tamil, fresh list B | 643 | 643 | 34% | 148, then 151 | 50 / 0 / 0, then 50 / 0 / 0 | first 44 / 6 / 0, fails; second 39 / 11 / 0, fails | **Dropped**: words failed twice. |

The contest inputs of the seven lists that run are in `inputs/`. Those of the three dropped lists are in
`inputs_dropped/`, where the locked program does not look.

## Why the three were dropped

In all three it was the picture words, never the names. The checkers looked each word up and marked it wrong
when they could not find it, in the sense given, in the early texts named in the prompt. Most such words are
real words of the language that are first recorded later.

- **Old Tamil.** The preprint's own check failed a Tamil word only if it was "a modern word with no attestation
  in early or classical Tamil literature". This study's one prompt for all languages fails a word "not attested
  in early" texts, which is stricter. Words first cited in classical works some centuries after the Sangam poems
  pass the preprint's rule and fail this one. That difference was not intended.
- **Finnish.** The translator's prompt allowed loans made by the Proto-Finnic period; the checker's prompt fails
  any known loan from another language family. Both translators kept old Germanic and Baltic loans on the first
  reading and failed on the second. The two prompts were inconsistent.

Both faults are in prompts written before the lock. The rule was applied as locked.

## Things to know about lists that run

- **Hawaiian.** The labeler put every name part of unknown meaning (223) under "personal name". The other
  labelers used their own knowledge to sort such parts into places, gods and peoples. So Hawaiian's islands and
  gods carry the label "personal name".
- **Greek and Hebrew** leave most names whole (80% and 67%). A name of one part gives the contest nothing to fit.
- **Sources consulted** are in each session's closing note, summarised in `../log.md`. No session reported
  consulting the preprint, the rebuttal or their repositories.
