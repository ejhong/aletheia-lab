# Does ammonium rise after every abrupt cooling?

Issue #60 · Lane: data · Written 2026-11-23 by Claude Fable 5.2 (Anthropic), directed by Eugene

## Question

Question #43 found that ammonium in Greenland ice ran high for about a century beginning 30 to 40 years after
the Younger Dryas cold set in, in three ice cores. Ammonium comes from fires, soils and plants.

**After the other abrupt coolings of the last ice age, does ammonium rise in the same way? And where does the
Younger Dryas rank among them?**

Two answers are wanted: whether a rise after cooling is general, and whether the Younger Dryas stands out among
coolings.

## Why it matters

If every abrupt cooling is followed by a rise in ammonium, the Younger Dryas high is what land and air do when
the climate turns cold, and it is not evidence of anything unusual at that time. If the other coolings show
nothing of the kind, the Younger Dryas high is an anomaly that wants its own explanation. #43 could not tell
these apart and listed it as a limit.

Fischer et al. 2015 (*Nature Geoscience* 8:723–727; accepted manuscript read) studied fire peaks in this record
across the warmings and stadials of the ice age. They report that fire activity rose at rapid warmings and was
low in stadials, the Younger Dryas included. They do not report a test of the century after each cooling onset.
We have not searched further for one.

## Data and sources

The same public files as #43 (hashes in `MANIFEST.md`), and one table.

| Short name | What | Source |
|---|---|---|
| NGRIP 10-yr | NGRIP decadal means of ammonium and calcium, 10,270–107,620 yr b2k | PANGAEA doi:10.1594/PANGAEA.935814, CC-BY-4.0 |
| NEEM 10-yr | NEEM decadal means, −10 to 121,440 yr b2k | PANGAEA doi:10.1594/PANGAEA.935831, CC-BY-4.0 |
| Events | Onsets of Greenland stadials and interstadials with their ages | Rasmussen et al. 2014, *Quat. Sci. Rev.* 106:14–28, Table 2 (read), transcribed to `events.tsv` |

"b2k" means years before 2000 CE. In the 10-yr files a row labelled `a` covers `[a, a+10)` (checked in #43).
Columns, in order: age (ka), conductivity, sodium, calcium, ammonium, nitrate; an empty field is missing.

`events.tsv` holds the 111 onsets from the start of the 11.4 ka event to the start of GS-26: name, NGRIP depth,
age, kind and, for stadial onsets, the paper's class of definition uncertainty (a: 20 years; b: 40–60 years;
c: 200 years; d: 100 years; f: 20–40 years on one data series only; GS-1: 4 years). GS-2.1a and GS-2.1b divide
one long stadial and are marked "other", not as onsets of cooling.

GISP2 is left out: its ages are on another timescale, and this test needs the published onset ages.

**What has been seen.** For #43: ammonium in detail from 12,400 to 13,400 years ago; 20-year means of ammonium
from 10,300 to 16,000; and, for the whole record, only the ages of the ten 300-year windows with the largest
excess. Ammonium around the other onsets has not been looked at. Before this plan was locked the program was run
on calcium alone (below).

## Method

### Which coolings

A stadial onset from `events.tsv` enters the test if all of these hold:

1. Its definition uncertainty is class a or b, or it is GS-1.
2. No other listed event lies strictly inside the 100 years before it (ages between `t` and `t + 100`) or
   strictly inside the 200 years after it (between `t − 200` and `t`). So the warm phase before it lasted at
   least 100 years and the cold phase after it at least 200.
3. With `t` rounded to the nearest 10 years, `t − 200 ≥ 10,300` and `t + 100 ≤ 107,620`.

That gives 25: GS-1, 2.1c, 2.2, 3, 4, 5.1, 5.2, 6, 7, 8, 9, 10, 11, 12, 15.1, 15.2, 16.1, 17.1, 17.2, 18, 19.1,
20, 21.2, 22 and 23.2. The rule was written without looking at ammonium at any of them but GS-1.

### The measure

For a time `t` (a multiple of 10) in one core:

- *After bins:* ten 20-year means, bin `k` (0 to 9) from the rows labelled `t − 20k − 20` and `t − 20k − 10`.
- *Before bins:* five 20-year means, bin `k` (0 to 4) from the rows labelled `t + 20k` and `t + 20k + 10`.
- A bin is the mean of those of its two rows that have a value, and is missing if neither has.
- The measures need at least 8 of the 10 after bins and 4 of the 5 before bins, all positive.

Then:

- **P, the peak:** `ln(largest after bin / median of the before bins)`. This decides. A peak anywhere in the 200
  years counts, so it does not depend on the exact date of an onset.
- **R, the level:** `ln(mean of the after bins / mean of the before bins)`. Reported.

For GS-1, `t` is 12,900. The windows are the same for every event. They were chosen knowing that the Younger
Dryas high falls within 200 years of its onset; see weaknesses.

### What the measure looks like where nothing happened

P is positive even in quiet ice, because it sets a maximum against a median. So each event is placed against
*quiet times*: every `t` that is a multiple of 20, from 10,500 to 107,520, with no listed event of any kind
between `t − 300` and `t + 200` inclusive, and with the measure defined.

An event's **percentile** is the share of quiet times, in the same core, with a strictly smaller value.

### Decision rules

Both use P for ammonium, in NGRIP and NEEM.

**Is a rise general?** Among the coolings other than GS-1, count those with a percentile of 0.75 or more. By
chance a quarter would be.

| Verdict | Condition |
|---|---|
| **General** | At least two-thirds, in both cores. |
| **Often** | Not general; in both cores the count is more than chance allows (one-sided binomial test against 0.25, p < 0.05). |
| **Not seen** | Anything else. |

**Does the Younger Dryas stand out?** Rank GS-1 among all the coolings in each core (1 = largest P).

| Verdict | Condition |
|---|---|
| **Stands out** | Rank 1 in both cores. |
| **Among the largest** | Not rank 1 in both; in the top quarter (rank ≤ ceiling of n/4) in both. |
| **Ordinary among coolings** | Anything else. |

How the two combine:

- *General*, and the Younger Dryas *ordinary* or *among the largest*: its high is the usual response to cooling.
- *Not seen*, and the Younger Dryas *stands out*: its high is an anomaly among coolings.
- Anything else is reported as it falls, without forcing it into one of those two.

### Control

Calcium, a measure of dust, is known to rise at every stadial onset. The same measures and rules are applied to
calcium. If dust does not come out "general", the event dates or the windows are not doing their job and the
ammonium result is not to be trusted.

This control was run before the lock (`swell.py control`, calcium only): 25 coolings, 3,072 quiet times; dust
rises into the top quarter after 24 of 24 other coolings in NGRIP and 23 of 24 in NEEM.

### Reported alongside, not part of the rules

1. The same verdicts on R.
2. The same with 300 years after the onset (15 after bins, at least 12 present), for the coolings whose cold
   phase lasted that long.
3. For each cooling: P, R, percentiles, the size of the peak and how many years after the onset it falls.
4. The stadial onsets left out by rule 1 or 2, and three smaller coolings (GI-1d, GI-1b and the 11.4 ka event):
   their P and R, for the reader. No rule uses them.

### Checks on the program

Unit tests on made-up series (bins and measures by hand, the 80% rule, which coolings enter, which times are
quiet, each verdict). The calcium run above.

### Replication

A model from another vendor writes its own program from this protocol, `events.tsv` and the format notes. Its
per-event values, percentiles and verdicts are compared with ours.

## What would count

- **The Younger Dryas high is ordinary:** "general", with the Younger Dryas not standing out.
- **The Younger Dryas high is an anomaly:** "not seen", with the Younger Dryas standing out.
- **In between:** "often", or a Younger Dryas that is among the largest of a general pattern. Reported as such.

Neither end says what caused the Younger Dryas. An anomaly would say that the century after its onset was
unlike the aftermath of other coolings in northern sources of ammonium, and nothing about why.

## Known weaknesses

- **The Younger Dryas is not a fresh case.** It was picked because its high was already seen, and the 200-year
  window was chosen to contain it. Its own percentile is therefore no surprise. What is new is how the other 24
  behave and where it ranks among them.
- **The onsets are dated unequally.** GS-1 is fixed to 4 years; the others to 20–60 years, and transitions into
  stadials are gradual. A misplaced onset blurs R more than P. The dust control shows whether the windows still
  catch the transition.
- **Snowfall drops at every cooling**, which raises concentrations for the same fallout. This helps a rise appear
  at any cooling, the Younger Dryas included, and is part of what "the usual response in the ice" means here.
  It is not corrected.
- **Older ice is thinner.** A 20-year mean is resolved throughout, but older peaks are smoothed somewhat more.
- **The climates differ.** The Younger Dryas came during deglaciation, with ice sheets retreating and forests
  advancing; most of the others came in full glacial conditions with far less vegetation to burn or to emit.
  A Younger Dryas that stands out could reflect that setting and nothing sudden.
- **Quiet times overlap** and are not independent; percentiles are descriptions.
- **Two cores, one laboratory and method**, on one timescale.
- **25 events.** Rank 1 of 25 in two correlated cores is suggestive, not proof.
- **One session** proposed, designed, runs and writes up the question, knowing #43's results.

## Budget

$15. Expected spend under $3: one round of design review by two other vendors' models, and replication.
