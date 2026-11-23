# Did random-number generators twitch at world events? Results

Issue #47 · Lane: data · Protocol locked 2026-11-23T15:54:17Z · No amendments

## Answer

**No. On 58 events after the project's formal series ended, chosen by rule, the network's output looks like
its output on ordinary days. The effect at the size the project reports did not show.**

By the rules fixed in advance:

| Question | Verdict | The numbers |
|---|---|---|
| Is there a positive excess? | **No positive excess detected** | Combined score of the 58 events: −1.83. "Suggestive" needed +1.645, "departure" +3.09. |
| How does it compare with the benchmark? | **Smaller than the benchmark** | The project's formal mean of 0.33 per event predicts +2.51 for 58 events. |
| Calibration | Not in doubt, by the rule | The 57 control days combine to −2.03, with a spread of 1.04. |

- Mean score per event: −0.24 (95% interval −0.50 to +0.02). The project's formal mean is +0.33.
- **Events against their own control days: no difference.** Mean difference +0.03 (57 pairs); events scored
  higher in 27 pairs and lower in 30; one-sided p = 0.43.

Two independent programs, written by OpenAI's and Google's models from the protocol alone, reproduce all 115
window scores to within 0.0001, both combined scores and both verdicts.

## What was tested

The Global Consciousness Project reports that its network of hardware random-number generators departed from
chance during 500 world events between 1998 and 2015, with a combined score of 7.31. We took events from 2016
to 2025, which that series never used, by two rules with no judgement in them:

- **Four calendar days** that the project's registry had used three or more times as full-day events (14
  February, 8 March, 22 April, 21 September), every year: 37 with data.
- **Every earthquake with 100 or more deaths** in NOAA's database, for the 24 hours from the hour of the shock:
  21 with data.

Each was scored with the project's standard statistic, and so was the same 24 hours a week earlier (or later,
for six) as a control.

## The evidence

### By class

| | Events | Combined score | Mean per event | Controls' combined score | Event minus control, mean | One-sided p |
|---|---|---|---|---|---|---|
| All | 58 | −1.83 | −0.24 | −2.03 | +0.03 | 0.43 |
| Calendar days | 37 | −1.88 | −0.31 | −0.54 | −0.22 | 0.85 |
| Earthquakes | 21 | −0.55 | −0.12 | −2.64 | +0.46 | 0.07 |
| Earthquakes, 1,000 or more deaths | 6 | −1.61 | −0.66 | −0.79 | −0.34 | 0.78 |

No class shows a positive combined score. The earthquakes look better than their controls only because their
controls happened to score low; the six deadliest go the other way.

For comparison, the project's own published scores for the same two classes in its formal years: +0.42 per event
for those calendar days (19 events) and +0.51 for earthquakes (29 events).

### Other ways of scoring, all set in advance

| Scoring | Events | Controls | Event minus control, p |
|---|---|---|---|
| Main: each egg standardised by its measured spread | −1.83 | −2.03 | 0.43 |
| Theoretical standardising, the project's first recipe | −0.93 | −1.06 | 0.45 |
| The cross-egg part only (eggs moving together) | −1.57 | −1.95 | 0.38 |

The verdicts are the same under theoretical standardising: no positive excess, smaller than the benchmark.

### The largest and smallest

Highest event scores: Lombok earthquake, 5 August 2018 (+2.30); Tibet earthquake, 7 January 2025 (+2.26);
Sichuan earthquake, 5 September 2022 (+1.97). Lowest: the Turkey–Syria earthquake of 6 February 2023, the
deadliest event in the list with 56,697 deaths (−2.32); 14 February 2017 (−1.99); 21 September 2016 (−1.95).
Among 58 scores drawn from chance, values of this size are expected. Every score is in `results/events.tsv`.

### Both events and controls run a little low

Events average −0.24 and controls −0.27, where chance as the test models it gives zero. Taken together, the 115
windows sit about 2.7 standard errors below zero with the main scoring, and 1.4 with theoretical standardising.
So this is at the edge of what chance allows, and it is the same on event days and ordinary days. We do not know
the cause. One guess: the devices' variances are a little above theory, as the project says, the main scoring
removes that, and what is left is slightly under the textbook value. An exploratory change to how egg spread is
measured (only on days when the egg is stable) leaves it as it is: −1.69 and −1.87 (`explore/pool_check.py`).

It does not touch the main finding, which is a comparison: event days are not different from control days.

### The program reproduces the project's own numbers

Before the lock, the same program scored six of the project's formal events of 2011–2015 (theoretical
standardising). Ours against the published score: 0.29 and 0.28; 3.24 and 3.14; 0.74 and 0.94; −0.28 and −0.58;
−0.49 and −0.12; 1.013 and 1.013. So a null here is not the result of reading the files wrongly or computing a
different statistic.

## What this does and does not show

**Shown.**

- On 58 rule-chosen events of 2016–2025 the project's statistic shows no excess. The combined score is 4.3
  below what the benchmark predicts, taking the test's own assumptions at face value.
- Event days and their control days are indistinguishable.

**Not shown.**

- That the project's 1998–2015 result was wrong. This test does not re-examine it.
- That no effect of any size exists. The paired comparison by itself puts the benchmark only about 1.7 standard
  errors above what was seen.
- That the project's own choice of events would have failed. Its experimenters picked events by judgement; ours
  came from rules, and a defender can say the rules picked the wrong days.

**Three things a defender could fairly say, and what we can answer.**

- *The network is smaller now.* True: 29 to 36 eggs passed our check in 2016, about 20 in 2021, and 8 to 12 in
  2024–25. If the effect is a correlation between pairs of eggs, fewer eggs give a smaller score. But the score
  here is not a smaller positive number. It is negative, and equal to the controls'.
- *Calendar days are not events.* The project registered these days itself, 20 times, and published a mean of
  +0.42 for them.
- *Minor earthquakes do not grip the world.* The six with 1,000 or more deaths score lowest of all.

## Replication

OpenAI `gpt-6.2-astra` (255 lines) and Google `gemini-4-neon` (399 lines) each wrote a program from
`protocol.md`, `events.tsv` and `replication/FORMAT.md`. Both ran at the first attempt.

| | OpenAI | Google |
|---|---|---|
| Event scores (58) | all within 0.0001 | all within 0.0001 |
| Control scores (57) | all within 0.0001 | all within 0.0001 |
| Seconds and eggs used | identical | identical |
| Combined scores | −1.832 and −2.030 | −1.832 and −2.030 |
| Verdicts; paired p | the same; 0.431 | the same; 0.431 |

They did not cover the class breakdown, theoretical standardising or the cross-egg part.

## Deviations and mistakes

- No amendment. The program is unchanged since the lock.
- The first plan standardised each event day by its one control day, which ties the two scores together and
  widens their spread, and it switched tests if the controls looked wrong. Both reviewers objected; both were
  rebuilt before the lock (`review/README.md`).
- One control day (for 22 April 2022) could not be scored: too few seconds had five eggs reporting. Its event
  stays in the main test and drops out of the paired check.
- The egg check and the way spread is measured are ours, because the project's are not published in full.
- Two review calls failed without output and were rerun.

## Limits

- **58 events.** Enough to see the benchmark with about 80% chance of at least "suggestive"; not enough to see
  an effect a third of that size.
- **The main test trusts the chi-square**, and the scores running low shows that trust is not quite earned in
  these years. The paired check does not depend on it and gives the same answer.
- **Seven candidate events fall in gaps** in the archive, among them the Morocco and Herat earthquakes of 2023.
- **Events by rule, not by the project's judgement.**
- **One session** proposed, designed, ran and wrote up the question.

## Who did this

Eugene directed the work. Claude Fable 5.2 (Anthropic) designed and ran the analysis and wrote this report on
23 November 2026. OpenAI `gpt-6.2-astra` and Google `gemini-4-neon` reviewed the plan twice before the lock and
each wrote an independent replication. No human checked the numbers.

Cost: $2.61 of the $20 budget (`SPENDING.md`); two failed review calls may have added up to $0.90.

Data: the Global Consciousness Project's public archive (<https://global-mind.org/>); NOAA NCEI Global
Significant Earthquake Database. See `MANIFEST.md`.

## What this means

For seventeen years a project in Princeton kept a ring of electronic coin-flippers running around the world and
reported that, when something gripped millions of people at once, the coins stopped behaving quite like coins.
The claim rests on events its own team picked. We tested it where they had not looked: ten later years, on
days fixed by simple rules, using their own arithmetic. If the effect were real and as large as they report, the
58 events should have added up to a clear signal. They added up to nothing. The coin-flippers behaved on
Valentine's Day, on Earth Day and in the hours after deadly earthquakes just as they did a week before. That
does not prove the earlier result was a mistake, and a believer can say we chose the wrong days. But the effect
did not carry over to a fair test it had not seen, which is what a real effect has to do.
