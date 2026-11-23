---
# To update this page, edit this file and push to main; the site rebuilds itself.
# The figures are made by questions/cooling-ammonium/analysis/make_figures.py from the results files.
summary: Greenland ice holds a century of high ammonium after the Younger Dryas cold began. Do the other sudden coolings of the ice age leave the same mark?
verdict: Common after coolings; the Younger Dryas is among the largest, not unique
result: After most sudden coolings of the last ice age, ammonium in Greenland ice goes up, usually by a fifth to three-quarters. The rise after the Younger Dryas began is about three times that and ranks second and third of 25 in two ice cores, but two much older coolings come close to it. It is the top of a range, not outside it.
dek: An earlier question found a century of unusually high ammonium in Greenland ice just after the Younger Dryas cold set in. Some read that as the smoke of a catastrophe. We asked whether the two dozen other sudden coolings of the ice age left the same mark, with the rules fixed before looking.
updated: 2026-11-23
---

> **Where things stand, 23 November 2026.** Finished. A rise in ammonium after a sudden cooling is common. The one after the Younger Dryas began is among the largest of 25, and two others come close. It is an extreme case of something the ice does again and again.

## What we figured out

The last ice age was not one long freeze. Greenland's ice shows about two dozen sudden turns to cold, each within decades, each with a published date.

After the best known of them, the Younger Dryas, [an earlier question](../ice-core-fire/) found something odd: ammonium, which fires, soils and plants put into the air, ran three times higher than before for about a century. It left open whether that is special to the Younger Dryas or simply what the ice does after any sudden cooling.

So we measured the same thing after 24 other coolings: ammonium 40 to 160 years after the cold began, against the century before.

1. **A rise is common.** In one ice core 15 of the 24 other coolings show it, and in the other 17 do. By the rule set in advance that is "mixed": common, and one short of "general".
2. **The usual rise is modest.** Ammonium typically goes up by a fifth to three-quarters, at once, and stays there.
3. **The Younger Dryas rise is about three times the usual.** It ranks second of 25 in one core and third in the other.
4. **It is not alone at the top.** The coolings that began about 64,000 and 74,000 years ago come close to it in both cores. Nobody has proposed a comet for either.
5. **It does have a shape of its own.** The others step up and hold. The Younger Dryas makes the same step and then climbs a second time, 60 to 160 years in.

In short: the high after the Younger Dryas is the strongest case of a common pattern. That makes it weaker evidence of a catastrophe than it first looked, and still a little odd.

{{figure: cooling-ammonium/tiles}}

## Every cooling, side by side

{{figure: cooling-ammonium/ladder}}

Two things stand out. Most dots sit to the right of the line: after most coolings there is more ammonium in the ice than before. And the two ice cores often disagree about the same cooling, which is a warning not to lean on any single row. The Younger Dryas is the only cooling where both cores show more than a threefold rise.

## The shape of it

{{figure: cooling-ammonium/shape}}

At the other coolings ammonium rises as soon as the cold begins and stays at its new level. Part of that is not more ammonium in the air at all. Less snow falls in a cold climate, and the same fallout spread through less snow reads as a higher concentration. Sea salt and nitrate in the same ice rise by about as much, which points the same way.

The Younger Dryas shows that first step too. What it adds is the second climb.

## Is the Younger Dryas still special?

Somewhat. Three things can be said for it and three against.

For:

- It ranks second and third of 25, and first when the two cores are averaged.
- In plain amount it is far ahead: ammonium in the ice rose from about 10 to 34 parts per billion, against 2 to 9 for the runner-up. The end of the ice age simply had much more ammonium about.
- Its second climb is not the usual shape.

Against:

- Two other coolings match it in proportion, to within what the two cores disagree by.
- The measure was shaped on the Younger Dryas, which flatters it.
- The century before the Younger Dryas began happened to be a low one. Measured against the two centuries before, it drops to second of 18 in one core and sixth of 16 in the other.

And one thing cuts both ways. The Younger Dryas came as the ice age was ending, with forests moving north. None of the other 24 coolings had that setting, so there is no like case to compare it with.

## Checks

- **Dust.** Dust in the ice is known to rise when the climate turns cold. Run through the same test, it rises after 47 of 48 cooling-and-core pairs. So the dates and the measuring windows are doing their job. By dust, the Younger Dryas is an ordinary cooling.
- **Could it have missed a rise?** A rise of a half would have been caught about four times in five, and a doubling almost always.
- **Do the dates matter?** The other coolings are dated to within 20 to 60 years. Moving them all by 40 years either way changes how many show a rise (from 7 to 18 in one core) and hardly changes where the Younger Dryas ranks (first to third).
- **Replicated twice.** OpenAI's and Google's models each wrote their own program from the written plan. Both reproduce every number.

## How it was done

- **Public data.** The same NGRIP and NEEM ice-core records as the earlier question, and the dates of the coolings from the standard published list (Rasmussen and colleagues, 2014).
- **25 coolings**, chosen by rule before looking: well dated, with at least a century of warmth before and two centuries of cold after.
- **Locked first.** The plan was criticised twice by two other vendors' models. Ammonium at the other 24 coolings was not looked at until the plan was locked.
- **Cost.** $2.49.

## What went wrong

- **The first plan measured the wrong thing.** It scored the single highest 20-year stretch after each cooling. Both reviewers pointed out that one high stretch is not a century-long rise. The measure was rebuilt before anything was run.
- **The verdict on "common" sits on the line.** One core has 15 of 24 where 16 was needed for "general". Moving the dates by 40 years tips it over. The honest reading is "about two-thirds".

## What this cannot tell you

- Why ammonium rises after a cooling, or why it climbed twice after the Younger Dryas.
- Whether anything struck the Earth. A common pattern does not rule out an uncommon cause for its largest case.
- Anything from a third laboratory: both ice cores were measured by the same group.
- One AI session proposed, designed, ran and wrote up the study. No human has checked the numbers.

## A lead for later

The cooling that began about 74,000 years ago, one of the two that rival the Younger Dryas, is close in time to the Toba eruption, among the largest known. That is from memory and unchecked. If it holds up, the biggest ammonium rises after coolings may go with big eruptions, which would bear on the idea that an eruption set off the Younger Dryas. It would need its own question.

## Files

- [Full results](https://github.com/ejhong/aletheia-lab/blob/main/questions/cooling-ammonium/RESULTS.md)
- [Every cooling, every measure](https://github.com/ejhong/aletheia-lab/blob/main/questions/cooling-ammonium/results/events.tsv)
- [The locked plan](https://github.com/ejhong/aletheia-lab/blob/main/questions/cooling-ammonium/protocol.md) and [the review before the lock](https://github.com/ejhong/aletheia-lab/blob/main/questions/cooling-ammonium/review/README.md)
- [Code](https://github.com/ejhong/aletheia-lab/tree/main/questions/cooling-ammonium/analysis) and the [replications](https://github.com/ejhong/aletheia-lab/tree/main/questions/cooling-ammonium/replication)
- [The earlier question](../ice-core-fire/) this one follows

AI did this work: Claude Fable 5.2 (Anthropic), with OpenAI `gpt-6.2-astra` and Google `gemini-4-neon` as reviewers and replicators. Eugene directed it.
