# Did populations crash at the Younger Dryas? Results

Issue #40 · Lane: data · Protocol locked 2026-11-23T17:17:16Z · No amendments · One of the issue's three lines of
evidence was tested: radiocarbon dates as a head count

## Answer

**No drop in dated human activity shows at the Younger Dryas onset, in North America, Europe or Asia. By the
rule fixed in advance the hypothesis's prediction is "not supported". But the test turned out weaker than
designed: around the onset the record is dominated by a distortion of the dating method that our reference did
not reproduce. The fair reading is "no sign of a crash, and no firm proof that there was none".**

The test compares the 300 years after 12,850 cal BP with the 300 years before, in a summed curve of calibrated
dates, against 2,000 made-up records with no sudden change.

| Region | Dates | After ÷ before | What the reference expects | p for a drop | Halving records as high as this | Verdict |
|---|---|---|---|---|---|---|
| **North America** | 1,803 | **1.35** | 1.13 (0.93 to 1.38) | 0.96 | 0 of 500 | **A halving is excluded** |
| Europe | 3,527 | 0.97 | 0.98 (0.85 to 1.13) | 0.45 | 4 of 500 | A halving is excluded |
| Asia | 1,447 | 1.19 | 1.04 (0.83 to 1.31) | 0.87 | 7 of 500 | Cannot tell |

**Overall, by the locked rule: not supported.** North America's record is 35% higher after the onset than
before, where a halving for three centuries would leave it about 7% lower.

Two independent programs, written by OpenAI's and Google's models from the protocol alone, reproduce the
summed curves and the steps exactly, and the overall verdict. On Asia, which sits on the 1% line, their random
draws put it just the other side ("a halving is excluded").

## What can be said firmly, and what cannot

**Firm.** No region shows a detected drop at the onset. This holds in the locked run, in every variant with the
target at 12,850 or 12,950 and a 200- or 300-year window, and in the afterwards check with inflated laboratory
errors.

**Not firm: "a halving is excluded".** The locked reference takes each date's stated error as its true
scatter. Stated errors on older dates are widely thought to be too small. An exploratory rerun
(`explore/error_check.py`) scattered the made-up dates by 1.5 and 2 times their stated error:

| | Halving records as high as the real record | | |
|---|---|---|---|
| True scatter | North America | Europe | Asia |
| as stated | 0.0% | 2.0% | 1.3% |
| 1.5 times stated | 0.7% | 19% | 7% |
| 2 times stated | 4% | 59% | 13% |

(These are 300 records each; the locked run's 500 gave 0.0%, 0.8% and 1.4%.) So in North America a halving stays
unlikely even if errors are twice what is stated, though it no longer passes the 1% rule. In Europe the
exclusion disappears. The reason is the calibration curve: just after the onset it runs steeply, and any extra
scatter in radiocarbon age makes dates pile up on a steep stretch. That piling-up lifts the "after" side of the
comparison and could hide a real loss.

## The spike and the fall: mostly the dating method

The protocol reports the most extreme steps at any time. They are not at the onset:

| Region | Sharpest fall | z-score | Sharpest rise | z-score |
|---|---|---|---|---|
| North America | 12,550 cal BP | −7.3 | 10,800 and 11,500 | +5.3, +4.0 |
| Europe | 12,550 | −10.9 | 11,500 and 14,300 | +6.0, +5.9 |
| Asia | 12,500 | −5.2 | 11,450 | +6.7 |

In all three regions the curve of dates spikes above its trend from about 12,850 to 12,600, by 40 to 80% at its
peak, then drops to 60 to 80% of the trend and stays there to about 11,800.

Plotted side by side (the figure on the site page), the three regions' curves have the same shape down to
their small wiggles. People on three continents did not rise and fall in step to the decade. The dating method
did that. From 12,850 to 12,600 the calibration curve is at its steepest, and from 12,450 on it is flat. Any
scatter in radiocarbon ages beyond what the stated errors allow makes dates pile up on the steep stretch and
thin out on the flat one, in every region at the same years.

Our made-up records were meant to carry this distortion, and they carry too little of it. The afterwards check
says how much is missing: with true scatter at twice the stated error, the made-up records expect a
steep-to-flat ratio of 1.1 to 1.4. The real ratios are 1.8 (North America), 2.3 (Europe) and 1.7 (Asia), and the
fall is still 3 to 8 standard deviations beyond the made-up ones. With the older IntCal13 curve the fall is
still there, a little smaller and about 50 years later (`explore/later_drop.py`).

What follows:

- **The spike and the fall are not evidence about people.** Most of their shape is shared across continents and
  tied to the curve. Whether some real thinning of people during the cold lies underneath cannot be told from
  this record by this method.
- **The test at the onset is compromised too.** The spike begins at the onset and lifts the "after" side of the
  comparison in every region. A real loss of people at that moment could be hidden under it. This is the same
  point as the table above, seen in the data.
- **Our reference world was wrong in a way the false-alarm check could not show**, because that check made its
  histories with the same assumption about errors.

## The evidence in detail

### The test at the onset

| | North America | Europe | Asia |
|---|---|---|---|
| Dates, bins, sites | 1,803; 1,169; 540 | 3,527; 2,642; 1,396 | 1,447; 841; 345 |
| Dates screened out as aquatic | 212 | 46 | 48 |
| z-score of the step at 12,850 | +1.74 | −0.15 | +1.18 |
| Rank of 12,850 among 89 times (1 = sharpest fall) | 68 | 32 | 70 |
| Power to detect a halving | 0.35 | 0.70 | 0.14 |
| Power for a drop of 30% | 0.11 | 0.26 | 0.08 |
| Power for a halving 100 years later | 0.45 | 0.79 | 0.22 |
| Power for a halving 100 years earlier | 0.04 | 0.08 | 0.03 |

Power is low. The onset sits where the calibration curve turns from flat to steep, and a halving of people there
shows up as a fall of only about 18% in the summed curve. This is why the rule asks a second question, whether
the real record is too high for a halving, and why that question matters more than the first.

### Who contributes

No site dominates. In North America the 300 years after the onset draw weight from 189 sites and the 300 years
before from 146; the largest site gives 2% of either side and the largest five about 10%. Europe: 357 and 333
sites, the largest five 5%. Asia: 112 and 101 sites, the largest five 16%.

### Variants set in advance

Verdict, with after ÷ before in brackets:

| Variant | North America | Europe | Asia |
|---|---|---|---|
| Locked run | excluded (1.35) | excluded (0.97) | cannot tell (1.19) |
| Straight-line trend | excluded (1.35) | cannot tell (0.97) | cannot tell (1.19) |
| Aquatic materials kept | excluded (1.47) | excluded (0.97) | cannot tell (1.15) |
| Errors over 200 left out | excluded (1.50) | excluded (1.00) | excluded (1.31) |
| Largest site left out | excluded (1.36) | excluded (0.97) | excluded (1.17) |
| 200-year windows | excluded (1.53) | excluded (1.19) | excluded (1.36) |
| 500-year windows | cannot tell (1.25) | **drop detected (0.78)** | cannot tell (1.03) |
| Target at 12,750 | cannot tell (1.07) | **drop detected (0.76)** | cannot tell (1.07) |
| Target at 12,950 | excluded (1.40) | excluded (1.01) | excluded (1.14) |

The two "drop detected" entries for Europe are the later fall coming into view: a 500-year window, or a target
100 years later, reaches into the centuries after 12,550.

### The procedure's false alarms

Before the lock, 100 made-up histories with no crash, given North America's real bins and errors, were put
through the whole procedure. Five had a p-value of 0.05 or less and two of 0.01 or less, where 5 and 1 are
expected (`explore/calibration.json`).

## Replication

OpenAI `gpt-6.2-astra` (227 lines) and Google `gemini-4-neon` (383 lines) each wrote a program from
`protocol.md` and `replication/FORMAT.md`. Both ran at the first attempt.

| | Both replications against ours |
|---|---|
| Dates and bins per region | identical |
| Summed curves, 3,603 points | within 0.004% |
| Step at the target | identical to four decimals |
| p-values (their own random draws) | 0.94, 0.43, 0.87 against our 0.96, 0.45, 0.87 |
| Power for a halving | 0.33, 0.63, 0.19 against 0.35, 0.70, 0.14 |
| Verdicts | North America and Europe the same; Asia 1.0% against our 1.4%, either side of the 1% line |
| Overall | not supported |

The two replications give the same random results as each other: both followed the protocol's order of draws
with the same seed. They are independent as programs, not as random samples. Neither covered the variants or
the checks made afterwards.

## Deviations and mistakes

- No amendment. The program is unchanged since the lock.
- **The plan did not allow for stated errors being too small.** Neither reviewer nor we raised it before the
  lock. It was found afterwards, while chasing the later fall, and it weakens the verdict's second half. It is
  reported above and not folded into the verdict.
- The first plan's made-up records did not match the real ones in structure; both reviewers caught it and it was
  rebuilt before the lock (`review/README.md`).
- Only one of the issue's three lines of evidence was tested. The genetic lines were not attempted.
- The earlier studies of this question (Buchanan and colleagues 2008; Anderson and colleagues 2011) are cited
  from memory and were not re-read.

## Limits

- **Dates are not people.** They follow where and what archaeologists choose to date.
- **The calibration curve is at its worst here.** The onset falls at a turn from flat to steep; the summed
  curve is distorted on both sides, and how much depends on the true scatter of the dates, which is not known.
- **Low power** for the direct test, as above.
- **A crash shorter than three centuries** was not tested.
- **The reference is fitted to the record it judges**, as a smooth parabola.
- **Site binning is crude**, and aquatic materials are screened by name only.
- **Movement is not death.**
- **One session** proposed, designed, ran and wrote up the question, knowing the results of #43, #60 and #69.

## Who did this

Eugene directed the work. Claude Fable 5.2 (Anthropic) designed and ran the analysis and wrote this report on
23 November 2026. OpenAI `gpt-6.2-astra` and Google `gemini-4-neon` reviewed the plan twice before the lock and
each wrote an independent replication. No human checked the numbers.

Cost: $2.71 of the $40 budget (`SPENDING.md`).

Data: the p3k14c database, release 2025.07 (Bird et al. 2022; CC-BY-4.0); the IntCal20 calibration curve
(Reimer et al. 2020). See `MANIFEST.md`.

## What this means

If a comet had wiped out much of North America's people 12,850 years ago, the dated remains of their camps and
hearths should thin out at that moment. We counted, using nearly seven thousand radiocarbon dates from three
continents. They do not thin out then; in North America there are more dated traces in the three centuries
after than in the three before. That would be a point against a sudden catastrophe, except for one thing we
found on the way. Radiocarbon dating is at its most treacherous in exactly those centuries, and it bends the
count of dates into the same spike and the same hollow on all three continents at once. Our test allowed for
that bending and did not allow for enough of it. So the honest answer is a modest one. There is no sign in the
dates that people crashed when the cold began. There is also no proof from the dates that they did not. To do
better needs a different method, one that models the errors of the dates and does not take them on trust.
