---
# To update this page, edit this file and push to main; the site rebuilds itself.
# The figures are made by questions/younger-dryas-crash/analysis/make_figures.py from the results files.
summary: If a comet devastated North America 12,850 years ago, the dated traces of people should thin out at that moment. Do they?
verdict: No sign of a crash, but the dates cannot rule one out
result: In nearly 7,000 radiocarbon dates from North America, Europe and Asia, dated human activity does not drop when the Younger Dryas cold began; by the rule set in advance the predicted crash is "not supported". But radiocarbon dating is at its most distorted in exactly those centuries, more than the test allowed for, so the result is weaker than planned: no sign of a crash, and no firm proof there was none.
dek: Archaeologists use radiocarbon dates from camps, hearths and shelters as a rough head count of past people. We asked whether that count falls at the start of the Younger Dryas, when a cosmic impact is said to have devastated North America, with the rules fixed before looking.
updated: 2026-11-23
---

> **Where things stand, 23 November 2026.** Finished, with a weaker answer than hoped. Dated human activity does not drop when the cold began, on any of three continents. But the dating method distorts the count in exactly those centuries, more than our test allowed for. There is no sign of a crash and no firm proof that there was none.

## What we figured out

One of the sharpest predictions of the Younger Dryas impact idea is about people. If a comet devastated North America about 12,850 years ago, many of the people living there should have died, and the traces they left should thin out at once.

Those traces can be counted. Archaeologists have radiocarbon-dated tens of thousands of hearths, bones and shelters, and more people leave more of them. We took a public collection of such dates, nearly 7,000 of them from the right period in North America, Europe and Asia, and compared the three centuries after the cold began with the three before.

1. **There is no drop when the cold begins.** In North America the count is a third *higher* after than before. In Europe it is level. In Asia it is a little higher.
2. **By the rule we set in advance, the predicted crash is "not supported".** A halving of North America's people for three centuries should have left the count clearly lower. It did not.
3. **But the test is weaker than we designed it to be.** Radiocarbon dating distorts the count of dates in exactly these centuries. We allowed for that, and it turned out we did not allow for enough.
4. **So the honest answer is modest.** The dates show no sign of a crash. They also cannot prove there was none.

{{figure: younger-dryas-crash/tiles}}

## The picture, and the problem with it

{{figure: younger-dryas-crash/curves}}

The line marks the start of the cold. To its right, in the first centuries of the cold, the real record does not dip. It jumps.

That jump is the problem. It is the same on all three continents, and so is the hollow that follows it, and so are the small wiggles along the way. If these were rises and falls in the number of people, it would mean that hunters in Texas, Germany and Siberia grew and shrank in step with one another to within a few decades. They did not. The dating did.

## Why radiocarbon does this

A radiocarbon measurement gives an age in "radiocarbon years", which have to be converted into calendar years using a curve built from tree rings. The curve is not straight. In some centuries it runs steep, in others nearly flat.

Just after the Younger Dryas began, it runs steep for about 250 years and then goes flat. Dates crowd onto a steep stretch and thin out on a flat one, more so the less precise the dates really are. That draws a spike and then a hollow in any count of dates, whatever the people were doing.

Our test was built to allow for this. It compared the real record with thousands of made-up records that went through the same conversion. But the made-up records assumed each date is as precise as its laboratory said. Older dates are known to be less precise than stated. When we reran the made-up records with errors half as large again, or doubled, the spike appeared in them too, though still not as large as the real one.

## What that does to the answer

| If the dates' true scatter is | Is a halving of people ruled out in North America? | In Europe? |
|---|---|---|
| as the laboratories state | Yes: 0 in 500 made-up halvings come out as high as the real record | Yes, barely |
| half as large again | Still very unlikely: fewer than 1 in 100 | No |
| twice as large | Unlikely: 1 in 25 | No |

In North America the case against a crash survives, weakened. In Europe it does not survive. Nowhere, under any of these assumptions, does a crash show.

## What this means for the impact idea

It is one more prediction that did not show up, and the least decisive of the ones tested so far. The [ice-core and charcoal studies](../../topics/younger-dryas/) could say "we would have seen it". This one can only say "we did not see it, and our instrument was blurred just there".

## How it was done

- **Public data.** The p3k14c database of archaeological radiocarbon dates (release 2025.07) and the standard IntCal20 calibration curve.
- **Three regions:** North America as the test, Europe and Asia to see whether any loss was widespread.
- **Locked first**, after two rounds of criticism from two other vendors' models. No real date was converted to a calendar age until then.
- **Checked for false alarms:** on a hundred made-up histories with no crash, the whole procedure raised a false alarm about as often as it should.
- **Replicated twice.** OpenAI's and Google's models each wrote their own program from the written plan. Both reproduce the curves and the verdict.
- **Cost.** $2.71.

## What went wrong

- **We trusted the stated errors of the dates.** Neither we nor the reviewers raised it before the plan was locked. We found it afterwards, when the figure showed three continents moving in step. It is reported here and not folded into the verdict, which stays as the locked rule gives it.
- **Our safety check shared the blind spot.** The false-alarm check used the same assumption about errors, so it could not catch this.
- **Only one of three planned lines of evidence was tested.** The other two, population histories read from the DNA of people and of large animals, were not attempted.

## What this cannot tell you

- Whether people's numbers fell later in the cold. The record does drop about three centuries in, but that is where the dating distortion is strongest, and the two cannot be separated here.
- Whether people moved. Fewer dates in one place can mean they went elsewhere.
- Anything about what caused what.
- One AI session proposed, designed, ran and wrote up the study. No human has checked the numbers.

## What would do better

A method that treats each date's error as something to be estimated, not trusted, and that models the true number of people through time directly. Such methods exist. That would be a new question, with its own plan.

## Files

- [Full results](https://github.com/ejhong/aletheia-lab/blob/main/questions/younger-dryas-crash/RESULTS.md)
- [The locked plan](https://github.com/ejhong/aletheia-lab/blob/main/questions/younger-dryas-crash/protocol.md) and [the review before the lock](https://github.com/ejhong/aletheia-lab/blob/main/questions/younger-dryas-crash/review/README.md)
- [Code](https://github.com/ejhong/aletheia-lab/tree/main/questions/younger-dryas-crash/analysis), the [replications](https://github.com/ejhong/aletheia-lab/tree/main/questions/younger-dryas-crash/replication) and the [checks made afterwards](https://github.com/ejhong/aletheia-lab/tree/main/questions/younger-dryas-crash/explore)

AI did this work: Claude Fable 5.2 (Anthropic), with OpenAI `gpt-6.2-astra` and Google `gemini-4-neon` as reviewers and replicators. Eugene directed it.
