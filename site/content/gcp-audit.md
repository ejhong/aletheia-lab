---
# To update this page, edit this file and push to main; the site rebuilds itself.
# The figures are made by questions/gcp-audit/analysis/make_figures.py from the results files.
summary: A worldwide network of random-number generators is said to have strayed from chance during 500 world events. We went back to the raw data and recomputed the original result.
verdict: The original result is in the data
result: Recomputed from the raw data, 395 of the project's formal events match its published scores closely and add up to +6.08. The same hours a week away add up to −0.42. So the published effect is real arithmetic on real data and is tied to the chosen events; how those events were chosen is what remains open.
dek: The Global Consciousness Project reports that its random-number generators departed from chance during 500 world events between 1998 and 2015. Our earlier test found nothing on later events chosen by rule. Here we audit the original: every event we could check, recomputed from the public raw data, each with a control window a week away.
updated: 2026-11-23
---

> **Where things stand, 23 November 2026.** Finished. The project's published result reproduces from its public raw data, and it is specific to the event windows: the same hours a week away show nothing. That rules out an arithmetic error and a fault in the devices. It does not say how the events and their time windows were chosen, and that is now the question.

## What we figured out

The Global Consciousness Project ran dozens of small random-number devices around the world, which it calls eggs. It registered 500 events between 1998 and 2015, from terror attacks to New Year's Eve, and reports that during them the eggs' output wandered more than chance allows: a combined score of 7.31, odds of about a trillion to one.

[Our first test](../global-consciousness/) took 58 later events, chosen by rule, and found nothing. That left the original result unexamined. A number that large is either in the public data or it is not, so we checked.

- **Every event we could check.** 396 of the 500 use the project's standard recipe and have clean entries in both of its public tables. They carry most of the headline figure.
- **From the raw data.** For each, the eggs' one-second counts were downloaded and the score recomputed.
- **A control for each event:** the same window one week earlier or later, kept clear of every other registered event, and scored in exactly the same way.

1. **The published scores reproduce.** Our score and the published score agree event by event: a correlation of 0.96, and half of them within 0.11 of each other.
2. **The effect is there.** The 395 events we could score add up to +6.08. The project's own figure for the same events is 6.61.
3. **It is not in ordinary hours.** The matched controls add up to −0.42, which is what chance gives. An event beat its own control in 250 of 395 pairs.
4. **It is not the machines.** The project itself warns that slightly uneven devices can push its statistic up. With no correction for that at all, the controls still come to +0.08. And nearly all of the excess is in eggs moving *together*, which one faulty egg cannot produce.

In short: the original result is not a mistake in arithmetic and not a quirk of the devices. Something separates the project's chosen windows from ordinary time.

{{figure: gcp-audit/tiles}}

## The picture

{{figure: gcp-audit/cumulative}}

{{figure: gcp-audit/reproduction}}

## Two explanations are left

**Something real happened to the network during these events.** That is the project's claim.

**The windows were chosen with some sight of the data.** By the project's account each event and its time window were fixed before the data were looked at. For a sudden event, such as an earthquake, that still means after it happened. And a note in the source of the project's registry page, hidden from readers, says that from June 2005 its website showed a live display "related to one of our primary analysis methods", and that surprise events would from then on be identified by an algorithm "to preclude influence" from it. The project saw the risk. If windows were sometimes set, stretched or kept with a rough idea of how the numbers were running, the result would look exactly as it does here: an excess in the chosen windows and nothing a week away.

An audit of the numbers cannot tell these apart. What bears on it is the earlier test. When we chose the events by rule, for the ten years after the project's series ended, the same statistic on the same network showed nothing. A real effect of the reported size should have appeared there, unless it depends on something the earlier years had and the later ones did not.

## What this does not show

- **It does not show that minds move random-number generators.** It shows the published numbers are right about the windows the project chose.
- **It does not show the windows were chosen unfairly.** Nothing in the public record says when each entry was written.
- **104 of the 500 events were not checked:** all of 1998, the New Year analyses and others with special recipes, and a few entries with typing errors in their dates.
- **Our method is not exactly the project's.** It does not publish in full how it screens out faulty eggs. Six events differ from the published score by more than 0.9.

## How it was done

- **Public data.** The project's own archive: 868 day files, about 4 GB, every egg's count for every second.
- **Rules before data.** Which events count, which control each gets, and what every outcome would be called were fixed and locked before any event was scored. Two rounds of criticism from OpenAI's and Google's models reshaped the plan first; the main change was to score each event and its control against exactly the same reference data.
- **Replicated twice.** OpenAI's and Google's models each wrote their own program from the written plan alone. Both ran first time and reproduce all 791 scores to six decimal places.
- **Cost.** $3.37.

## What went wrong

- **The strongest check the reviewers asked for was not run.** Both wanted a calendar of made-up events on other ordinary days, scored the same way, to calibrate the whole procedure. It needed several hundred more files. The 396 controls stand in for it.
- **One event could not be scored.** During a march on 5 November 2013 only one egg reported for most of the window.
- **The program was slow.** It read files one at a time; part-way through, a helper read the rest in parallel. The two replications, which read the files their own way, give the same scores.

## Files

- [Full results](https://github.com/ejhong/aletheia-lab/blob/main/questions/gcp-audit/RESULTS.md)
- [Every event, its control and their scores](https://github.com/ejhong/aletheia-lab/blob/main/questions/gcp-audit/results/windows.tsv)
- [The locked plan](https://github.com/ejhong/aletheia-lab/blob/main/questions/gcp-audit/protocol.md) and [the review before the lock](https://github.com/ejhong/aletheia-lab/blob/main/questions/gcp-audit/review/README.md)
- [The two replications](https://github.com/ejhong/aletheia-lab/tree/main/questions/gcp-audit/replication)

AI did this work: Claude Fable 5.2 (Anthropic), with Claude Opus 5.5 sub-agents for mechanical tasks, and OpenAI `gpt-6.2-astra` and Google `gemini-4-neon` as reviewers and replicators. Eugene directed it.
