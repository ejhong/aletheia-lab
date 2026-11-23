---
# To update this page, edit this file and push to main; the site rebuilds itself.
# The figures are made by questions/global-consciousness/analysis/make_figures.py from the results files.
summary: A worldwide network of random-number generators is said to depart from chance when events grip millions of people. We tested it on ten later years the project never used.
verdict: No effect on a fresh test
result: On 58 events from 2016 to 2025, chosen by rule and scored with the project's own statistic, the network behaved as it does on ordinary days. Event days and control days are indistinguishable, and the effect at the size the project reports did not show. This does not re-examine the project's original 1998–2015 result.
dek: Since 1998 the Global Consciousness Project has run random-number generators around the world, and reports that they stray from chance when something grips millions of people at once. Its formal test ended in 2015; the machines kept running. We tested the claim on the years since, with the events fixed by rule and the plan locked before looking.
updated: 2026-11-23
---

> **Where things stand, 23 November 2026.** Finished. On 58 fresh events the network shows nothing: its output on Valentine's Day, on Earth Day and after deadly earthquakes looks like its output a week before. The effect the project reports did not carry over to years it had not examined.

## What we figured out

The Global Consciousness Project keeps dozens of small electronic devices running in cities around the world. Each one flips 200 electronic coins a second and reports the count. The project calls them eggs. Its claim is that when a great many people are caught up in the same event, the eggs stop behaving quite like coins: taken together, their counts wander a little more than chance allows.

Between 1998 and 2015 the project named 500 events and reports a combined result of more than seven standard deviations, odds of about one in ten trillion. The standing objection is that its own team chose the events and the time windows. The team says each was fixed before the data were looked at. An outsider cannot check that.

But there is a way round the argument. The formal series stopped at the end of 2015, and the eggs kept running, with the data public. So we tested the ten years since:

- **Events by rule.** Four calendar days that the project itself had used again and again as events (14 February, 8 March, 22 April, 21 September), every year. And every earthquake that killed a hundred people or more, from a US government list.
- **The project's own arithmetic**, checked first against six of its published results.
- **A control for each event:** the same 24 hours a week away.

1. **Nothing.** The 58 events add up to a score of −1.83. If the effect were as large as the project reports, they should have added up to about +2.5.
2. **Events look like ordinary days.** The control days add up to −2.03. An event beat its control 27 times out of 57: a coin toss.
3. **No kind of event does better.** Not the calendar days, not the earthquakes, not the six deadliest earthquakes.

In short: on a fair test it had not seen, the effect is not there.

{{figure: global-consciousness/tiles}}

## The picture

{{figure: global-consciousness/cumulative}}

This is the project's own favourite kind of chart. In its formal years the line climbs steadily, and that climb is its evidence. Here it does not climb.

## What a defender could say

- **"The network is smaller now."** True. About 30 eggs passed our checks in 2016, about 20 in 2021, and only about 10 in 2024 and 2025. If the effect is eggs moving together, fewer eggs would show less of it. But the result here is not a smaller rise. It is no rise, the same as the controls.
- **"Those are not real events."** The project registered those four calendar days itself, twenty times, and published an above-average result for them. It registered 29 earthquakes and published a better one still.
- **"Small earthquakes do not grip the world."** The six that killed more than a thousand people score lowest of all. The Turkey–Syria earthquake of 2023, with over 56,000 dead, has the lowest score in the whole list.
- **"You chose the wrong days; we would have chosen better."** This one cannot be answered from outside, and it is the heart of the dispute. A result that appears only when its believers choose the days is not yet a result others can rely on.

## What this does not show

- **It does not show the 1998–2015 result was wrong.** We did not re-examine it.
- **It does not show there is no effect of any size.** With 58 events a much weaker effect could hide.
- One oddity: events and controls both score slightly below zero, at the edge of what chance allows. We do not know why. It is the same on event days and ordinary days, so it does not bear on the comparison.

## How it was done

- **Public data.** The project's own archive: one file per day, every egg's count for every second. 156 days were needed.
- **Checked against the project.** Before the test, our program scored six of the project's published events. It matched: 0.29 against their 0.28, 3.24 against 3.14, 1.013 against 1.013.
- **Locked first**, after two rounds of criticism from two other vendors' models. No event day or control day was read until then.
- **Replicated twice.** OpenAI's and Google's models each wrote their own program from the written plan. Both reproduce every score to four decimal places.
- **Cost.** About $2.60.

## What went wrong

- **The first plan had a flaw in its statistics.** It measured each egg's natural spread from a single other day, which quietly links an event's score to its control's. Both reviewers caught it. The plan was rebuilt before anything was run.
- **Seven events had no data.** The archive has gaps, most of 2024 among them, and three large earthquakes of late 2023 fall in one.
- **Parts of the method are ours.** The project does not publish in full how it screens out faulty eggs, so we used a rule of our own, the same for event and control days.

## Files

- [Full results](https://github.com/ejhong/aletheia-lab/blob/main/questions/global-consciousness/RESULTS.md)
- [Every event and its score](https://github.com/ejhong/aletheia-lab/blob/main/questions/global-consciousness/results/events.tsv)
- [The locked plan](https://github.com/ejhong/aletheia-lab/blob/main/questions/global-consciousness/protocol.md) and [the review before the lock](https://github.com/ejhong/aletheia-lab/blob/main/questions/global-consciousness/review/README.md)
- [Code](https://github.com/ejhong/aletheia-lab/tree/main/questions/global-consciousness/analysis) and the [replications](https://github.com/ejhong/aletheia-lab/tree/main/questions/global-consciousness/replication)
- [The project's own site](https://global-mind.org/)

AI did this work: Claude Fable 5.2 (Anthropic), with OpenAI `gpt-6.2-astra` and Google `gemini-4-neon` as reviewers and replicators. Eugene directed it.
