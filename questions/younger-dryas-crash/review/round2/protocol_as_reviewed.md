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
population histories read from the DNA of large animals and of people, are not attempted. They need other data
and methods, and most such histories are too smooth to place a change within a few centuries. They are left for
a question of their own.

## Why it matters

A sudden, continent-wide loss of people is one of the hypothesis's sharpest predictions. The counter-view is
that people adjusted to the cold with little loss, or that declines were local and gradual.

Two earlier tests on North American dates are known to us from memory, neither re-read for this plan, both
`unverified`: Buchanan, Collard and Edinborough (2008, *PNAS*) reported no evidence of the proposed bottleneck;
Anderson and colleagues (2011, *Quaternary International*) reported signs of a possible decline or
reorganisation early in the Younger Dryas. There is later work we have not surveyed.

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
with radiocarbon ages from 8,500 to 14,000 (Europe 4,334 dates, North America 2,562, Asia 1,975). For the
false-alarm check below, North America's bins and errors were used to shape made-up records. No real date has
been calibrated and no real curve of dates through time has been made.

## Method

### Dates and regions

Three regions, by the `Continent` field: **North America** (the one pre-set test of the hypothesis), **Europe**
and **Asia** (for the claim that the loss was widespread). Southern continents need a different calibration
curve and are left out.

A date is used if its `Age` is from 9,000 to 13,800 radiocarbon years inclusive, its `Error` is above zero, and
its `Material` and `Taxa` fields together do not contain any of the strings `shell`, `marine`, `fish`, `mollus`,
`whale`, `seal`, `otolith`, `coral` (in any letter case). Those materials take up old carbon from water and
need corrections the database does not give.

### Calibration

The calendar grid runs from 9,000 to 17,000 cal BP in steps of 5 years (1,601 points). The curve's radiocarbon
age `μ(t)` and error `σ(t)` are interpolated linearly onto it.

A date with age `A` and error `E` has weight at grid point `t` proportional to
`exp(−(A − μ(t))² / (2(E² + σ(t)²))) / √(E² + σ(t)²)`, scaled so that its weights sum to 1 over the grid.

### Bins and the summed curve

Sites with many dates would otherwise dominate. Dates from one site whose ages fall in the same 200-year span
(`floor(Age/200)`) form a *bin*, and the bin's curve is the average of its dates' curves. The site is `SiteID`
if that field is not blank, otherwise `SiteName` in lower case with surrounding spaces removed (the two kinds
never match each other); a date with neither is a bin by itself. Sites are told apart within a continent only.

The **summed curve** `S(t)` of a region is the sum of its bins' curves.

### The measure

For a time `T`, the *step* is

`D(T) = ln( mean of S over [T − 300, T) / mean of S over [T, T + 300) )`,

the 300 years after `T` against the 300 years before it (ages run backwards, so "after" is the smaller numbers;
each interval takes the grid points from its lower bound up to but not including its upper). A negative step is
a drop; `exp(D)` is the ratio of after to before. The target is `T* = 12,850` cal BP. The Younger Dryas begins
at 12,846 cal BP in the Greenland ice (12,896 years before 2000; Rasmussen et al. 2014, read for #43). That is
an ice-core date; supporters place the impact layer in sediments within about a century of it. The 300-year
windows are meant to cover that slack, and targets of 12,750 and 12,950 are reported.

### What chance and the calibration curve produce

A reference world with no sudden change, run through the same dating process and given the same make-up as the
real record:

1. **The smooth trend.** A parabola fitted by least squares to `ln S(t)` against `t` over the grid points from
   10,500 to 15,500 inclusive. Its exponential, over the grid points from 9,500 to 16,500 inclusive and scaled
   to sum to 1, is the reference density. A parabola can bend, so a slow turn in the record is not mistaken for
   a step.
2. **One made-up record.** It has the real record's bins, each with as many dates as the real bin and those
   dates' real errors. Each bin gets one calendar age drawn from the reference density, and one curve error:
   normal with standard deviation `σ(t)`. Each of its dates gets radiocarbon age `μ(t)` plus the bin's curve
   error plus a normal laboratory error of that date's own `E`, rounded to the nearest year. A date whose
   radiocarbon age falls outside 9,000 to 13,800 is dropped, as a real one would be; a bin left empty
   disappears. The rest are calibrated, averaged within bins and summed as above.
3. **2,000 made-up records** per region (`numpy.random.default_rng(40)`, used for the regions in the order
   North America, Europe, Asia). Anything that rests on random draws is compared between programs only loosely.

From these, for every `T` from 10,800 to 15,200 in steps of 50: the mean and standard deviation (with `n − 1`)
of the made-up steps, and the **z-score** of the real step, `z(T) = (D(T) − mean)/sd`.

The **p-value at the target** is `(k + 1)/2,001`, where `k` is the number of made-up records whose step at `T*`
is at or below the real one.

A step counts as a **detected drop** if it is negative and its p-value is 0.01 or less.

### What a crash would look like

The same made-up process with a crash put in: the reference density multiplied by 0.5 over the 300 years after
`T*` (grid points from 12,550 up to but not including 12,850) and rescaled to sum to 1. 500 such records per
region.

- **Power** is the share of them that would count as a detected drop, by the same rule and the same 2,000
  crash-free records.
- **Is a halving ruled out?** The share of the 500 whose step at `T*` is at or above the real step. If it is
  0.01 or less, the real record is higher after the onset than a halving would leave it.

### Decision rules

For each region:

| Verdict | Condition |
|---|---|
| **Drop detected** | The real step at `T*` is a detected drop. |
| **A halving is excluded** | Not that, and at most 1% of halving records have a step at or above the real one. |
| **Cannot tell** | Anything else. |

Overall, for the hypothesis's prediction of a sharp loss of people in North America:

- **Supported** if a drop is detected in North America.
- **Supported as widespread** if detected in North America and in at least one of Europe and Asia.
- **Not supported** if a halving is excluded in North America.
- **Undetermined** if North America is "cannot tell".

"Drop detected" means the dated record is unusually low just after the onset against a smooth trend. It does
not show that the fall was abrupt, how large the loss of people was, or its cause. The halving for three
centuries is a yardstick we chose, not a figure taken from the impact literature.

### Reported alongside, not part of the rules

1. For each region: the ratio of after to before, the ratio the reference expects and its 95% range; the
   z-score at every `T`; where the target ranks among the 89 times (1 = most negative); the five most negative
   and most positive.
2. **Other crashes, same detector:** power for a drop of 30%; for a halving that starts 100 years later
   (12,450–12,750) and 100 years earlier (12,650–12,950).
3. **Who contributes.** For the 300 years on each side of the target: the summed weight, the number of sites
   with weight above 0.05, and the share of the weight from the largest site and the largest five.
4. **Variants**, each rerun in full with 1,000 crash-free and 300 halving records: a straight-line trend in
   place of the parabola; aquatic materials kept; dates with `Error` above 200 left out; the site with the most
   dates left out; windows of 200 and of 500 years in the step (the planted halving stays 300 years); the target
   at 12,750 and at 12,950 (the planted halving moves with it).
5. The numbers of dates, bins and sites per region, and of aquatic dates left out.

### Checks on the program, before the lock

- **Unit tests on made-up data:** a single date calibrates to the right calendar age; binning by site; the step
  has the right sign; the trend recovers a known curve; a planted halving is detected about as often as the
  program's own power figure says; with a flat stretch of the calibration curve laid over the crash, the
  program reports low power.
- **False alarms of the whole procedure** (`crash.py --calibrate`): 100 made-up records drawn from a known
  smooth trend with no crash, given North America's real bins and errors (and nothing else of the real data),
  each put through the whole procedure with 200 crash-free reference records. Result (`explore/calibration.json`): 2 of the 100 had a
  p-value at or below 0.05 and 1 at or below 0.01, where 5 and 1 are expected; 1 was flagged as a detected drop;
  3 had a p-value at or above 0.95; the median was 0.55. The procedure does not raise false alarms more often
  than its nominal rate, as far as 100 records can show.

No real date is calibrated and no real curve through time is made before the lock.

### Replication

A model from another vendor writes its own program from this protocol and the format notes. The real summed
curves and steps involve no random draws and must agree to within 0.001 in the step. Its z-scores, p-values and
power rest on its own random draws and are compared loosely; the verdicts are compared.

## What would count

- **For the hypothesis:** "supported", and more so "supported as widespread".
- **Against, within limits:** "not supported": North America's dated record is higher just after the onset than
  a halving lasting three centuries would leave it.
- **Neither:** "undetermined".

A drop would not show what caused it: sudden cold alone could reduce or move people. A record with no drop would
not show that nothing happened to people, only that their dated traces did not thin by the amount tested.

## Known weaknesses

- **Dates are not people.** They follow archaeologists' interests and funding as well as past populations. The
  Younger Dryas boundary has been dated intensively because of this very debate, which could raise or lower the
  count on either side of it. Nothing in these files can separate that from a change in population.
- **The reference is fitted to the record it judges.** The trend and the make-up of the made-up records come
  from the real record. The false-alarm check above measures what that costs.
- **A crash shorter, smaller or later than the one tested** could go unseen. The power figures say how much.
- **A smooth parabola is not history.** A real gradual change inside those six centuries would count as a step.
- **Site binning is crude.** Sites with several names, or several sites sharing a name within a continent, are
  mis-grouped; fixed 200-year spans split close dates that fall either side of a boundary. A site with many
  bins is treated as so many independent moments.
- **Old-carbon and context problems remain.** Aquatic materials are screened by name only; dates on old wood,
  or on bone of animals unconnected with people, are taken as they come.
- **One curve error per bin** is a simplification of how the calibration curve's uncertainty is shared.
- **Movement is not death.** Fewer dates in one region can mean people went elsewhere.
- **Europe and Asia give two chances** at "widespread".
- **One session** proposed, designed, runs and writes up the question, knowing the results of #43 and #60.

## Budget

$40. Expected spend under $5: design review by two other vendors' models, and replication.
