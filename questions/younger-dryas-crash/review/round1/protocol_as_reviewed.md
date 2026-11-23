# Did populations crash at the Younger Dryas?

Issue #40 · Lane: data · Written 2026-11-23 by Claude Fable 5.2 (Anthropic), directed by Eugene

## Question

The Younger Dryas impact hypothesis holds that a cosmic impact about 12,850 years ago devastated North America
and beyond, and that human populations fell sharply at that moment. Archaeologists use the number of radiocarbon
dates from human sites through time as a rough head count: more people leave more dated hearths, bones and
shelters.

**In the largest public database of archaeological radiocarbon dates, does the record of human activity drop at
the Younger Dryas onset, in North America and in Europe and Asia, by more than the dating method and chance
produce?**

## Scope

The issue names three lines of evidence. This plan tests one: radiocarbon dates as a head count. The other two,
population histories read from the DNA of large animals and of people, are not attempted. Such histories blur
any change over thousands of years and cannot say whether a decline took one century or thirty. They are left
for a question of their own.

## Why it matters

A sudden, continent-wide loss of people is one of the hypothesis's sharpest predictions. The counter-view is
that people adjusted to the cold with little loss, or that declines were local and gradual.

Two earlier tests on North American dates are known to us from memory, neither re-read for this plan, both
`unverified`: Buchanan, Collard and Edinborough (2008, *PNAS*) reported no decline at the onset; Anderson and
colleagues (2011, *Quaternary International*) reported one. They used a few hundred to about 1,500 dates. The
database used here holds several times more.

The difficulty all such tests share is the calibration curve. Radiocarbon ages are converted to calendar ages
by a curve that has flat stretches and steep ones. A flat stretch spreads dates out and a steep one bunches
them, which draws false dips and peaks in any curve of dates through time. There is such structure near the
Younger Dryas. The test below builds that effect into its yardstick.

## Data and sources

| Short name | What | Source |
|---|---|---|
| p3k14c | 173,946 archaeological radiocarbon dates worldwide, with site and continent | <https://github.com/people3k/p3k14c>, release 2025.07, `inst/p3k14c_scrubbed_fuzzed.csv`; data CC-BY-4.0. Bird et al. 2022, *Scientific Data* 9:27 (not read) |
| IntCal20 | The Northern Hemisphere calibration curve | <https://intcal.org/curves/intcal20.14c>; Reimer et al. 2020, *Radiocarbon* 62 |

Columns used from p3k14c: `Age` (radiocarbon years BP), `Error`, `SiteID`, `SiteName`, `Continent`. In IntCal20,
the first three fields of each data line: calendar age (cal BP), radiocarbon age, and its error.

**What has been seen** (`explore/structure.py`): the columns, and the number of dates and sites per continent
with radiocarbon ages from 8,500 to 14,000 (Europe 4,334 dates, North America 2,562, Asia 1,975). No date has
been calibrated and no curve of dates through time has been made.

## Method

### Dates and regions

Three regions, by the `Continent` field: **North America** (the main test), **Europe** and **Asia**. Southern
continents need a different calibration curve and are left out.

A date is used if its `Age` is from 9,000 to 13,800 radiocarbon years inclusive and its `Error` is above zero.

### Calibration

The calendar grid runs from 9,000 to 17,000 cal BP in steps of 5 years (1,601 points). The curve's radiocarbon
age `μ(t)` and error `σ(t)` are interpolated linearly onto it.

A date with age `A` and error `E` has weight at grid point `t` proportional to
`exp(−(A − μ(t))² / (2(E² + σ(t)²))) / √(E² + σ(t)²)`, scaled so that its weights sum to 1 over the grid.

### Bins and the summed curve

Sites with many dates would otherwise dominate. Dates from one site whose ages fall in the same 200-year span
(`floor(Age/200)`) form a *bin*, and the bin's curve is the average of its dates' curves. The site is `SiteID`
if present, otherwise `SiteName` in lower case with surrounding spaces removed; a date with neither is a bin by
itself. Sites are told apart within a continent only.

The **summed curve** `S(t)` of a region is the sum of its bins' curves.

### The measure

For a time `T`, the *step* is

`D(T) = ln( mean of S over [T − 300, T) / mean of S over [T, T + 300) )`,

the 300 years after `T` against the 300 years before it (ages run backwards, so "after" is the smaller numbers).
A negative step is a drop. The target is `T* = 12,850` cal BP. The Younger Dryas begins at 12,846 cal BP in the
Greenland ice (12,896 years before 2000; Rasmussen et al. 2014, read for #43).

### What chance and the calibration curve produce

A reference world with no sudden change, run through the same dating process:

1. **The smooth trend.** A straight line fitted by least squares to `ln S(t)` against `t` over 10,500 to 15,500
   cal BP gives an exponential trend. Its density over the grid points from 9,500 to 16,500 is the reference.
2. **One made-up record:** as many calendar ages as the region has bins, drawn from the reference density (grid
   points, with replacement). Each gets a radiocarbon age: `μ(t)` plus a normal error of standard deviation
   `σ(t)`, plus a normal laboratory error of standard deviation `E`, where `E` is drawn with replacement from
   the region's real errors. Each is rounded to the nearest year, calibrated as above (no binning; each is its
   own bin) and summed.
3. **1,000 made-up records** per region (`numpy.random.default_rng(40)`, used for the regions in the order
   North America, Europe, Asia). Anything that rests on random draws is compared between programs only loosely.

From these, for every `T` from 10,800 to 15,200 in steps of 50: the mean and standard deviation of the made-up
steps, and the **z-score** of the real step, `z(T) = (D(T) − mean)/sd`.

The **p-value at the target** is the share of made-up records whose step at `T*` is at or below the real one,
counted as `(number + 1)/(1,001)`.

### Could a crash have been seen?

The same made-up process with a crash put in: the reference density multiplied by 0.5 over the 300 years after
`T*` (grid points from 12,550 up to but not including 12,850), then rescaled to sum to 1. 300 such records per
region. **Power** is the share of them whose step at `T*` is at or below the 1st percentile of the 1,000
crash-free steps.

### Decision rules

For each region:

| Verdict | Condition |
|---|---|
| **Drop detected** | The step at `T*` is negative and its p-value is 0.01 or less. |
| **No drop, and a halving would have shown** | Not detected, and power is 0.8 or more. |
| **Cannot tell** | Not detected, and power is under 0.8. |

Overall, for the hypothesis's prediction:

- **Supported** if a drop is detected in North America.
- **Supported as widespread** if detected in North America and in at least one of Europe and Asia.
- **Not supported** if North America is "no drop, and a halving would have shown".
- **Undetermined** if North America is "cannot tell".

### Reported alongside, not part of the rules

1. For each region: the summed curve, the reference trend, the real step and z-score at every `T`, and where the
   target ranks among the 89 times by z-score (1 = the most negative).
2. The five most negative and five most positive z-scores and their times, per region.
3. The same with dates of `Error` above 200 left out.
4. The same with 200-year windows and with 500-year windows in the step.
5. The same with the target moved to 12,750 and to 12,950.
6. Power for a crash of 30% (density multiplied by 0.7).
7. The numbers of dates, bins and sites per region.

### Checks on the program, before the lock

Unit tests on made-up data: a single date calibrates to the right calendar age; binning by site; a made-up
record drawn from a smooth trend gives a step whose p-value is unremarkable, repeated many times; the same with
a halving planted is detected most of the time; the step has the right sign. No real date is calibrated before
the lock.

### Replication

A model from another vendor writes its own program from this protocol and the format notes. The real summed
curves and steps must agree closely (they involve no random draws). Its z-scores, p-values and power will
differ by random variation and are compared loosely.

## What would count

- **For the hypothesis:** "supported", and more so "supported as widespread".
- **Against, within limits:** "not supported": North America's record shows no drop where a halving lasting
  three centuries would have been seen.
- **Neither:** "undetermined".

A drop would not show what caused it: sudden cold alone could reduce or move people. No drop would not show
that nothing happened to people, only that their dated traces did not thin by the amount tested.

## Known weaknesses

- **Dates are not people.** They follow archaeologists' interests and funding as well as past populations. The
  Younger Dryas boundary has been dated intensively because of this very debate, which could raise or lower the
  count on either side of it.
- **A crash shorter or smaller than the one tested** could go unseen. The power figures say how much.
- **The reference is a smooth exponential.** Real populations were not. The step compares neighbouring
  centuries, which makes it insensitive to the long trend, but a real gradual change in those centuries would
  count as a step.
- **Site binning is crude.** Sites with several names, or several sites sharing a name within a continent, are
  mis-grouped. Coordinates are fuzzed in this release and are not used.
- **Lab errors are taken as reported**, and old dates with large errors smear across the onset.
- **Marine and freshwater offsets are ignored;** every date is calibrated as atmospheric.
- **Movement is not death.** Fewer dates in one region can mean people went elsewhere.
- **One session** proposed, designed, runs and writes up the question, knowing the results of #43 and #60.

## Budget

$40. Expected spend under $5: design review by two other vendors' models, and replication.
