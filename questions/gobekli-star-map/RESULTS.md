# Göbekli Tepe's star map: results

Issue #92 · Lane: data · Protocol locked 2026-11-23T21:03:35Z (commit `ea1f7bd`) · No amendments

## Answer

**Not testable this way. None of the three vision models passed the check we set in advance: shown the paper's
own pictures blind, not one ranked the scorpion carving as a close match for the Scorpius stick figure. By our own
rule that leaves no judges to count, so the test gives no verdict on the paper's one-in-5-million figure.**

| Question fixed in advance | Label | Why |
|---|---|---|
| Do blind judges reproduce the paper's ranking? | **Not testable** | No judge passed the competence check |
| Is the claimed pairing better than a shuffled one? | **Not testable** | Same |

The check was that a judge must give the scorpion photograph a mean rank of 2.0 or better, out of 12, for the
scorpion figure. The three judges gave it 6.4 (OpenAI), 7.8 (xAI) and 10.8 (Google). Chance is 6.5.

What the judges did do is described below. It is a description made after the result was known, and it is not
evidence under the plan: with the check switched off, the judges' best match was the paper's animal for none of
the seven other figures, the paper's pairing did no better than a shuffled one, and the three judges agreed
little with one another. That last point is the main reason not to read their rankings as a finding against the
paper. A judge that prefers the clearest photograph whatever the figure is not measuring resemblance.

## What was tested

Sweatman and Tsikritsis (2017) read the animals on Pillar 43 at Göbekli Tepe as constellations, and the pillar as
a record of the sky in 10,950 BCE. Their chance of a coincidence, about one in 5 million, comes from a table in
which the authors themselves rank how well each of 12 animal symbols fits each of 8 constellation stick figures.
They rank their own match first for seven of the eight and equal second for the eighth. Later papers by Sweatman
name that table as the place to challenge the number.

We took the 20 pictures of that table (12 photographs of carvings, 8 stick figures reduced to black lines) and
asked three vision models to do the ranking blind: OpenAI `gpt-6.2-astra`, Google `gemini-4-neon` and xAI
`grok-4.7`. Each saw one stick figure and the 12 photographs in a random order and ranked the photographs by
resemblance of shape, five times per figure; and the reverse, one photograph and the 8 figures, five times per
pillar symbol. The prompts said only that the photographs show shapes carved in stone. All 240 rankings came back
valid at the first attempt.

## The evidence

### The locked result

| Judge | Mean rank of the scorpion photograph for the scorpion figure (1 best, 12 worst) | Needed | Counted |
|---|---|---|---|
| OpenAI `gpt-6.2-astra` | 6.4 | 2.0 or better | no |
| xAI `grok-4.7` | 7.8 | 2.0 or better | no |
| Google `gemini-4-neon` | 10.8 | 2.0 or better | no |

Fewer than two judges count, so both labels are "not testable" and nothing else in the plan is computed.

Before accepting that, I checked for a mistake on our side. The pictures sent are the ones in the paper's table:
the scorpion photograph, its white patch included, is as printed (rendered page compared with the extracted
picture). The letters in a reply decode to the right pictures (one trial worked by hand from the raw reply and
the trial list). The same pipeline, on made-up shapes before the lock, ranked a triangle first for a triangle
outline with all three models. I found no fault.

### What the judges did (a description made afterwards; not evidence)

With the competence check switched off and everything else as locked (`explore/no_gate.py`):

| | All three pooled | OpenAI | Google | xAI |
|---|---|---|---|---|
| Figures, of 7, where the judge's best match is the paper's animal | **0** | 0 | 1 (Sagittarius and the vulture) | 0 |
| Mean rank of the paper's animal, of 11 (chance 6.0) | 6.55 | 7.29 | 6.26 | 6.11 |
| Share of the 5,040 shuffled pairings that do as well as the paper's | **0.61** | 0.83 | 0.25 | 0.61 |
| The reverse task: share of shuffled pairings that do as well | 0.24 | 0.53 | 0.05 | 0.45 |

Scorpion set aside in every row, as the plan specifies. Under the locked labels these numbers would read "do not
reproduce the paper's ranking" and "pairing not better than chance in this test".

| Stick figure | The paper's animal | Its place by the judges | The judges' best match |
|---|---|---|---|
| Scorpius | scorpion | 9th of 12 | lion or leopard |
| Pisces | bending bird | 9th of 11 | lion or leopard |
| Libra | duck or goose | 11th of 11 | boar |
| Lupus | dog or wolf | 11th of 11 | vulture and lion, tied |
| Sagittarius | eagle or vulture | 4th of 11 | boar |
| Ophiuchus | bending bird with fish | 6th of 11 | lion or leopard |
| Virgo | frog | 5th of 11 | eagle or vulture |
| Gemini | ibex or rat | 4th of 11 | boar |

The paper's own formula, given the judges' ranks in place of the authors', returns 0.46 where the paper has one
in 5 million. As the plan says, that is not a probability of anything; it shows how completely the paper's number
depends on whose ranks go in.

Three things say the judges were not measuring what the paper's authors saw, or anything stable:

- **They disagree with one another.** The correlation between two judges' tables of mean ranks is 0.51 (OpenAI and
  Google), 0.19 (Google and xAI) and 0.14 (OpenAI and xAI). Each judge is consistent with itself: Google put the
  lion first for the scorpion figure in all five repetitions.
- **They have favourites whatever the figure.** Averaged over all eight figures the lion, the vulture and the boar
  get mean ranks of 4.2, 4.7 and 4.8, and the frog, the scorpion and the bending bird 8.3, 8.1 and 7.9. The
  favourites are the clearest photographs of whole animals; the frog is 64 by 82 pixels and the scorpion is a
  faint relief. This looks like photograph quality as much as shape.
- **Knowing the answer did not help.** Asked afterwards, all three named Göbekli Tepe and described the 2017
  paper's claim. OpenAI's model, shown the eight drawings, said the first "looks like a scorpion with a curled
  tail". It had still ranked the scorpion photograph sixth on average for that drawing.

## Replication

Google `gemini-4-neon` wrote an analysis program from the protocol and format notes, before any ranking had been
analysed. On the real rankings it excludes the same three judges for the same reason and gives the same two
labels (`replication/google/comparison.txt`). On made-up rankings, where judges pass, it agrees with our program
on all 23 numbers. The description above was computed by our program only.

## Limits

- **The competence check rested on my assumption,** that the scorpion match is plain to see. It is plain to
  someone who knows the carving is a scorpion and the stars are Scorpius. A judge told nothing compares a faint
  relief with a bent line and three prongs. The check may ask for knowledge, not eyesight. The reviewers asked
  for a competence floor; choosing the scorpion for it was my decision.
- **A failed instrument is not a negative result.** The test cannot tell "these models cannot judge this kind of
  resemblance" from "the resemblance is not in the pictures". The disagreement between judges points to the
  first.
- **The pictures are small.** They are the paper's own, from 64 to 277 pixels across, enlarged for the judges.
- **Three models, five repetitions,** shared trial orders, twelve pictures in one request.
- **The larger question was never in reach.** The eight constellations, their stick figures and their
  orientations were chosen by the authors after seeing the carvings. No ranking test addresses that.
- **Sources read in part.** The 2017 paper and the 2017 exchange with the excavators were read by a sub-agent
  for the statistical argument; *Prehistory Decoded* and the version of record of the 2024 paper were not
  obtained.

## Departures from the plan, and things to know

- No amendment.
- After the lock and before any judging, one line of the analysis program's input check was loosened (commit
  `f1d805a`). It checks the shape of a ranking, not its content.
- While checking xAI's token use I printed one of its replies, a string of letters, without its key.
- The "what the judges did" section, the figures on the site page and `explore/` were made after the result was
  known.
- My guesses before the run (`log.md`): 70% that judges would not see the matches once the scorpion was set
  aside, 25% mixed, 5% that they would. I did not expect the scorpion check to fail.

## Spending

About $16.20 of $20: $0.73 for the review before the lock, $0.41 for the replication program, $3.06 for OpenAI's
judging, $4.52 for Google's, about $7.30 for xAI's, and $0.20 for plumbing tests. xAI's figure is an estimate:
one test request reported its own cost ($0.086, mostly hidden reasoning), multiplied by the number of requests
(`SPENDING.md`).

## Who did the work

AI did this work. Claude Fable 5.2 (Anthropic) designed the test, ran it and wrote this report on 2026-11-23.
Sub-agents (Claude Opus 5.5) read the papers, built the stimuli and the judging script, wrote the unit tests and
adapted the review, replication and figure scripts. OpenAI `gpt-6.2-astra`, Google `gemini-4-neon` and xAI
`grok-4.7` were the judges; the first two also reviewed the plan before the lock, and Google's wrote the
replication. Eugene directed it: he asked for the question to be run.

## What this means

A well-known paper says the animals carved on a pillar at Göbekli Tepe are constellations, and that the odds of
the match being an accident are about one in 5 million. That number comes from the authors' own judgement of how
much each carving looks like each constellation. We tried to check the judgement by asking three AI vision
systems to make the same comparisons without being told what anything was. It did not work: the systems could not
even pair the scorpion carving with the scorpion constellation, which we had set as the minimum for trusting
them, and they disagreed with each other about nearly everything. So this test says nothing firm either way. What
it does show is that the resemblances the paper counts are not obvious enough for these machines to find
unprompted, and that the paper's number collapses if anyone else's rankings are put into its formula. Whether
people who have never heard of the theory would see the matches is the question that matters, and it needs a
panel of human judges.
