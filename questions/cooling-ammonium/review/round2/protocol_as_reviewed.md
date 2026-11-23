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

Fischer et al. 2015 (*Nature Geoscience* 8:723–727; accepted manuscript read) studied fire peaks in annual
NGRIP ammonium across the ice age. They report that the frequency of fire peaks rose at rapid warmings and was
low in stadials, the Younger Dryas included. That is a different quantity from the one here (total ammonium in
20-year means), and a low count of fire peaks over a whole stadial does not say what its first two centuries
did. We have not found a published test of the century after each cooling onset, and have not searched far.

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
one long stadial and are marked "other", not as onsets of cooling. Ages are the table's, in whole years.

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
3. `t − 200 ≥ 10,300` and `t + 100 ≤ 107,620`.

Rules 2 and 3 use the published ages. Every onset that passes is a multiple of 20 years except GS-1 (12,896),
which is taken as 12,900 from then on.

That gives 25: GS-1, 2.1c, 2.2, 3, 4, 5.1, 5.2, 6, 7, 8, 9, 10, 11, 12, 15.1, 15.2, 16.1, 17.1, 17.2, 18, 19.1,
20, 21.2, 22 and 23.2. The rule was written without looking at ammonium at any of them but GS-1.

### The measures

For a time `t` (a multiple of 20 for every event here; GS-1 is taken at 12,900) in one core:

- *After bins:* 20-year means, bin `k` (0, 1, 2, …) from the rows labelled `t − 20k − 20` and `t − 20k − 10`. Bin
  0 is the first 20 years after the onset.
- *Before bins:* five 20-year means, bin `k` (0 to 4) from the rows labelled `t + 20k` and `t + 20k + 10`.
- A bin is the mean of those of its two rows that have a value, and is missing if neither has.

All four measures are natural logs of ratios of means of bins:

- **D, the delayed century** (this decides): the mean of after bins 2 to 7, which is years 40 to 160 after the
  onset, over the mean of the before bins. It needs at least 5 of those 6 after bins and 4 of the 5 before bins,
  and every bin used must be positive; otherwise the event is *not evaluable* in that core and is left out of
  the counts and ranks there, and named.
- **P, the peak:** the largest of after bins 0 to 9 over the median of the before bins (needs 8 of the 10).
- **R, the level:** the mean of after bins 0 to 9 over the mean of the before bins (needs 8 of the 10).
- **H, the fall-back:** the mean of after bins 2 to 7 over the mean of after bins 10 to 14 (years 200 to 300;
  needs 4 of the 5), only for coolings with no other listed event strictly inside the 300 years after them.

D is a template taken from the Younger Dryas: #43 found its ammonium low for the first decades and high from
about 40 to 150 years after the onset. Using it on the other coolings is a fair test of whether they do the
same. For the Younger Dryas itself it is not an independent test; see weaknesses.

The onsets are defined in the source "at the first data point of the steep part that clearly deviates from the
base-line level preceding the transition", so the 100 years before an onset are meant to be baseline.

### What the measures look like where nothing happened

Each event is placed against *quiet times*: every `t` that is a multiple of 20, from 10,500 to 107,520, with no
listed event of any kind between `t − 300` and `t + 200` inclusive, and with D defined, in that core and for
that chemical. An event's **percentile** is the share of quiet times with a strictly smaller value.

Quiet times overlap one another and sit mostly in long uninterrupted stretches of stadial or interstadial. They
show how much D wanders with no transition; they are not a model of what a cooling should do. No probabilities
are computed from them.

### Decision rules

Both use D for ammonium, in NGRIP and NEEM.

**Is a delayed rise general?** Among the evaluable coolings other than GS-1, the share whose percentile is 0.75
or more:

| Verdict | Condition |
|---|---|
| **General** | At least two-thirds, in both cores. |
| **Not seen** | At most one-third, in both cores. |
| **Mixed** | Anything else. |

"Not seen" is read with the sensitivity figure below. It means that ammonium does not usually rise into the top
quarter, not that it never rises at all.

**Where does the Younger Dryas rank?** Rank GS-1 among all evaluable coolings in each core (1 plus the number
with a strictly larger D).

| Verdict | Condition |
|---|---|
| **The largest** | Rank 1 in both cores. |
| **Among the largest** | Not that; rank ≤ ceiling of n/4 in both. |
| **Not among the largest** | Anything else. |

The two answers are reported separately and not merged into one. With them, always: D for GS-1 beside the
largest and the median D of the others, in each core; which coolings pass in both cores, in one, in neither.

### Controls

**Calcium**, a measure of dust, rises at stadial onsets; the stratigraphy itself was defined partly from it. It
is run through the same measures as a check on the program, the dates and the windows. It is not a check on how
sensitive the ammonium test is. It was run before the lock (`swell.py control`, calcium only): 25 coolings,
3,072 quiet times; by D, dust is in the top quarter after 24 of 24 other coolings in NGRIP and 23 of 24 in NEEM,
with a median D near +1.0 (dust 2.7 times higher); GS-1 ranks 13th and 7th of 25.

**Nitrate and sodium** are run the same way and reported, to show what other chemicals in the same ice do in
the delayed century.

### Reported alongside, not part of the rules

1. The same two verdicts on P and R; H for the coolings that have it.
2. **Sensitivity.** D is a log ratio, so a rise by a factor `f` in the delayed century adds `ln f` to it. For
   `f` = 1.25, 1.5, 2 and 3: the share of quiet times that would then reach the top quarter.
3. **Onsets moved.** Every onset but GS-1 moved by 40 and by 20 years in each direction: the verdicts and counts.
4. **Nearby reference.** Percentiles against only the quiet times within 10,000 years of the event (needs 100).
5. For each cooling in each core: D, P, R, H, percentiles, the two means behind D, and the 20-year means from 300
   years before to 300 years after (`results/profiles.tsv`).
6. The stadial onsets left out by rule 1 or 2, and three smaller coolings (GI-1d, GI-1b and the 11.4 ka event):
   their D and percentile, for the reader. No rule uses them.

### Checks on the program

Unit tests on made-up series (bins and measures by hand, the coverage rules, non-positive values, which coolings
enter, which times are quiet, each verdict). The calcium run above.

### Replication

A model from another vendor writes its own program from this protocol, `events.tsv` and the format notes. Its
per-event values, percentiles and verdicts are compared with ours.

## What would count

- **The Younger Dryas high is the usual thing:** "general", with the Younger Dryas not the largest.
- **The Younger Dryas high is unlike other coolings:** "not seen", with the Younger Dryas the largest by a clear
  margin in both cores.
- **Anything else** is reported as it falls: for instance a common rise of which the Younger Dryas is an extreme
  case.

All of this is about ammonium concentration in the ice. It does not say what the sources did, and neither end
says what caused the Younger Dryas.

## Known weaknesses

- **The Younger Dryas is not a fresh case.** It was picked because its high was already seen, and D was shaped
  on it. Its own value and rank are therefore flattered. What is new is how the other 24 behave.
- **The onsets are dated unequally.** The onset of GS-1 is defined to within 4 years; the others to within 20 to
  60 years (the paper's "definition uncertainty", which is about where the transition starts in the ice, not
  about calendar age). A misplaced onset moves the window. The moved-onset runs show how much that matters.
- **Concentration is not deposition.** Snowfall tends to drop at a cooling, which raises concentrations for the
  same fallout. That would help a rise appear at any cooling. It is not corrected.
- **Older ice is thinner**, so older features are smoothed more, even in 20-year means. This favours the
  Younger Dryas, the youngest cooling, in any ranking.
- **The climates differ.** The Younger Dryas came during deglaciation, with ice sheets retreating and forests
  advancing; most of the others came in full glacial conditions. A Younger Dryas that ranks first could reflect
  that setting. There is no second deglacial cooling of its kind to compare it with.
- **The coolings tested are a selection:** well-defined, isolated onsets with at least 100 warm years before and
  200 cold years after. The result is about those.
- **Two cores, one laboratory and method**, on one timescale. They are not independent witnesses.
- **One round of review rebuilt the measure.** The first plan scored any single 20-year peak; both reviewers
  pointed out that this is not a century-long rise.
- **One session** proposed, designed, runs and writes up the question, knowing #43's results.

## Budget

$15. Expected spend under $4: design review by two other vendors' models, and replication.
