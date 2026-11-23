---
# To update this page, edit this file and push to main; the site rebuilds itself.
# The figures are made by questions/gobekli-star-map/analysis/make_figures.py from the results files.
summary: A paper reads the animals carved on a pillar at Göbekli Tepe as constellations, with odds of one in 5 million against coincidence. The odds rest on the authors' own ranking of what looks like what. We asked three vision models to do the ranking blind.
verdict: Could not be tested this way
result: None of the three vision models could match even the scorpion carving to the scorpion constellation, the check we had set for trusting them, so by our own rule the test gives no verdict. For what it is worth, they did not reproduce any of the paper's other matches and they disagreed with one another. A panel of people who have not heard of the theory is the test this needs.
dek: Sweatman and Tsikritsis (2017) say Pillar 43 records the sky of 10,950 BCE, and put the chance of coincidence at one in 5 million. That number comes from a table in which the authors rank how well each carved animal fits each constellation. We gave the same pictures to three vision models and asked them to rank the resemblances without being told what anything was.
updated: 2026-11-23
---

> **Where things stand, 23 November 2026.** Finished, without a verdict. The judges failed the check we set in advance: none of them ranked the scorpion carving as a close match for the Scorpius stick figure. Their other rankings do not reproduce the paper's either, but judges that fail the check, and that disagree with one another, are not a fair test of it.

## What we figured out

On Pillar 43 at Göbekli Tepe, carved some 11,000 years ago, there is a vulture, a scorpion, several birds and other animals. A 2017 paper reads them as constellations and the pillar as a date: the sky of 10,950 BCE, close to the start of the Younger Dryas cold spell. It gives the odds of the match being a coincidence as about one in 5 million.

That number comes from one table. For each of eight constellations the authors rank 12 animal symbols by how well they fit its stick figure, and they rank their own match first seven times out of eight. The ranking is the authors' judgement. Later papers by the same author name the table as the place to challenge the number, so we tried.

- **The paper's own pictures.** The 12 photographs of carvings and the 8 stick figures from that table, the figures reduced to plain black lines.
- **Three judges told nothing.** Vision models from OpenAI, Google and xAI each ranked the 12 photographs against each figure, five times, in shuffled order. The instructions said only that the photographs show shapes carved in stone.
- **A check on the judges, set in advance.** The scorpion is the reading's starting point. A judge had to rank the scorpion photograph first or second for the scorpion figure, or its rankings would not count.
- **None passed.** The scorpion photograph came 6th, 8th and 11th of 12 on average. By our rule that leaves no judges, and no verdict.
- **What they did instead.** For none of the other seven figures was the judges' best match the paper's animal. The paper's pairing did no better than a shuffled one.
- **They disagreed with one another.** Each model was consistent with itself and had its own favourites. All three leaned towards the clearest photographs whatever the figure.

In short: the test did not work, and it failed in a way that tells us something. The matches the paper counts are not plain enough for these machines to find unprompted, even the scorpion.

{{figure: gobekli-star-map/tiles}}

## The picture

{{figure: gobekli-star-map/matches}}

{{figure: gobekli-star-map/ranks}}

## Why this is not a result against the paper

**The check may have asked for knowledge, not eyesight.** A scorpion carving matches Scorpius for anyone who knows it is a scorpion. A judge told nothing compares a faint relief with a bent line ending in three prongs. We chose the scorpion as the test of a competent judge; that choice now looks like the weak point of the design.

**The judges do not agree.** If three judges measured the same resemblance their rankings would line up. The agreement between them runs from 0.14 to 0.51 on a scale where 1 is identical. Their favourites, the lion, the vulture and the boar, are the sharpest photographs of whole animals.

**Knowing the theory did not help them.** Asked afterwards, all three named Göbekli Tepe and described the 2017 paper. One said the first drawing "looks like a scorpion with a curled tail", having ranked the scorpion photograph sixth for it.

## What it does show

**The number depends entirely on whose ranks go in.** Put the judges' ranks into the paper's formula in place of the authors' and one in 5 million becomes roughly one in two. That is no proof the authors' ranks are wrong. It shows the figure is a measure of their judgement, and has never been checked against anyone else's.

**The larger question was never in reach.** The eight constellations, their stick figures and which way up they go were chosen by the authors after seeing the carvings, from a sky with 88 constellations. No ranking test touches that choice.

## What would settle it

A panel of people who have not heard of the theory, shown the same pictures and asked the same question, with decoy constellations drawn in the same style. That needs people and a little money, and is a study to propose, not one an AI lab can run.

## How it was done

- **The plan was fixed first.** Pictures, prompts, the 80 trials per judge, the check on the judges and the labels were locked on 23 November 2026 before any picture from the paper was shown to a judge.
- **Reviewed before the lock** by models from OpenAI and Google. They separated three questions the first draft had mixed and asked for the check on the judges.
- **Replicated.** Google's model wrote its own analysis program from the plan alone. It leaves out the same three judges for the same reason.
- **Checked for our own mistakes.** The pictures sent match the paper's printed table, the replies decode to the right pictures, and the same pipeline ranked made-up shapes correctly.

## What went wrong

- The check on the judges failed for all three, which the plan had not expected. Everything under "what they did instead" was worked out afterwards and is a description, not a scored result.
- xAI's model took about three minutes a trial, mostly hidden reasoning, and cost more than the other two together.

## Files

- [Results](https://github.com/ejhong/aletheia-lab/blob/main/questions/gobekli-star-map/RESULTS.md) and the [locked plan](https://github.com/ejhong/aletheia-lab/blob/main/questions/gobekli-star-map/protocol.md)
- [Every ranking](https://github.com/ejhong/aletheia-lab/blob/main/questions/gobekli-star-map/results/rankings.tsv), the [pictures](https://github.com/ejhong/aletheia-lab/tree/main/questions/gobekli-star-map/stimuli) and the [review before the lock](https://github.com/ejhong/aletheia-lab/tree/main/questions/gobekli-star-map/review)
- Source: Sweatman and Tsikritsis, "Decoding Göbekli Tepe with archaeoastronomy: What does the fox say?", *Mediterranean Archaeology and Archaeometry* 17(1), 2017, [doi:10.5281/zenodo.400780](https://doi.org/10.5281/zenodo.400780)

AI did this work: Claude Fable 5.2 (Anthropic) designed and ran it, with OpenAI, Google and xAI models as judges, at Eugene's direction.
