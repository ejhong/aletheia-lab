# Two retracted Younger Dryas papers, checked against their own data: results

Issue #127 · Lane: data · Protocol locked 2026-11-24T14:38:16Z (commit `0ebea37`, SHA-256 `98b48ef3…a5300d`) ·
Two amendments · Spot-checked, corrected and partly rerun on 2026-11-24 · Not replicated by a second vendor

This report replaces the first write-up. A spot check found that the first run's numbers reproduce, that its
verdict on the Baffin Bay paper stands, and that much of what it said beyond that was overstated or wrong. One
of its lists of dates was partly invented. The section "Spot check and corrections" says what changed.

## Answer

On 11 February 2026 *PLOS One* retracted two 2025 papers that reported evidence for the Younger Dryas impact
hypothesis. Most of their data is still public. We checked the journal's stated reasons against it.

**The Baffin Bay paper (Moore and others 2025).** The journal's checkable criticisms hold. By the rule fixed in
advance the label is "retraction strongly supported": four of five checks came out against the paper, where three
were needed. The dating has a problem the notice does not describe. The calibrated ages in the paper's SI Table S1
are not what its stated method gives. For three of the four cores they are what the method gives when the
correction for old sea water is entered with the opposite sign, and for the fourth they are what the calibration
curve for land samples gives. Done as stated, the four dates on the claimed boundary come out 300 to 610 years
younger, and none is centred on the onset of the Younger Dryas. We cannot see how the published numbers came about
and do not say.

**The shocked quartz paper (Kennett and others 2025).** The journal gave two reasons, the dating and the sampling.
Both are largely borne out by the paper's own tables, with qualifications set out below. Neither the journal nor
this study examined whether the sixteen grains are shocked quartz. The label fixed in advance is "retraction mixed
or harsh". That label was settled before any data were read, because the rule could give a stronger one only if
the notice faulted the microscopy, and the notice was already known not to. We do not stand behind the word
"harsh": the first write-up called the retraction harsher than standard practice without citing a standard, and
the journal's own policy and the guidelines it follows allow retraction where conclusions are unreliable.

| Check fixed in advance | Result | Counts against the paper? |
|---|---|---|
| A1. Under a moderate allowance for polar water (500 years), do at least 2 of 4 boundary dates fall away from the onset? | 4 of 4 do; 2 of 4 do with no allowance | Yes |
| A2. Are the objects in SI Figs S30 to S34 calcareous microfossils? | Calcium, carbon and oxygen make up 92.5 to 96.5% in all four spectra; one of the two objects is plainly a foraminifer. A reading by eye | Yes |
| A3. Is there a peak outside the boundary in Core 64 as large as the boundary peak in Core 67, or was under 20% of the cores sampled? | Yes for metallic dust particles (680 against 640 per kg), no for spherules (230 against 735). Samples cover 3.1% of core length | Yes |
| A4. Does the paper's "multiply by 100" step put ordinary crust in the comet field, with most spherules crust-like before it? | Yes: crust lands in the field, and 18 of 18 spherules have crust-like iron to nickel before the step | Yes |
| A5. No oxygen-isotope anomaly, and at least 10 reference errors | Fails as locked: 3 of 10 samples exceed the threshold, and the offline reference check found 3 errors | No |
| B1. Do the published dates from the layer reject a single age, with at least 3 left out of the paper's tables? | Yes at Arlington Canyon by the letter (12 dates, 10 not in the tables), but 5 of the 12 are dates the original authors set aside as old wood | By the letter |
| B2. Are grain counts for control samples missing, or fewer than 3 controls at a site? | Yes: no control sample has a grain total | Yes |

## What was tested

**Paper A.** Moore and others (2025), *PLOS One* 20(8): e0328347, retracted by e0342613. It reported a layer of
microspherules, metallic dust particles, meltglass and platinum-rich nanoparticles in four sediment cores from
Baffin Bay (Cores 52, 64, 67 and 77), dated to the onset of the Younger Dryas, and read it as fallout from a comet.

**Paper B.** Kennett and others (2025), *PLOS One* 20(9): e0319840, retracted by e0342620. It reported sixteen
quartz grains with glass-filled fractures in boundary samples at Arlington Canyon (California), Blackwater Draw
(New Mexico) and Murray Springs (Arizona), with none in ten samples above and below, and read them as shocked by
low-altitude airbursts.

**The notices.** For Paper A the journal lists wrong and unsupportive citations; a chronology whose calibration
"does not follow the recommended methods for the latitude of the study site and time period", so that proper
calibration "produces ages that are younger than those reported in the article and that are outside the Younger
Dryas"; "misidentification of material in SI Figs S30–S34", which experts identified as marine foraminifera;
sampling that cannot show long-term variability, with a peak in Core 64 "outside the presented Younger Dryas
Boundary, but of the same magnitude as the peak" in Core 67; no engagement with the mainstream account; and data
not always clearly attributed. For Paper B it says the authors "have not included all of the available samples"
in their age model, that "at times it is not possible to determine what studies these samples originated from",
that the dates "range from centuries before and after the Younger Dryas onset", that the authors "have not sampled
the entire core section", and that "no age models have been reported".

**The authors' position.** Eight authors of each paper did not agree with its retraction, and one of Paper A's
agreed (the notices list them by initials). Christopher Moore told Retraction Watch that the group remains "confident in the
integrity of the data, the methods employed, and the conclusions drawn", that "the core issue is procedural" and
that he wished the group had been contacted for a correction (Retraction Watch, 4 March 2026). We found no other
public statement.

The data are the papers themselves, their supporting information, five spreadsheets on Zenodo and the two
calibration curves (`MANIFEST.md`). Tables printed as images were typed in by hand after the lock; the spot check
compared every cell of those tables with the images and found no mismatch.

## Paper A: the Baffin Bay cores

### The dates (check A1)

The paper says how it calibrated: "Reservoir corrections (∆R) were applied to radiocarbon dates during calibration
in OxCal using values for Baffin Bay from Pearce et al.: Zone 4 for Core 52, ∆R = +71 y; Zone 3 for Cores 64 and
67, ∆R = +218 y; and Zone 3/2 border for Core 77, ∆R = +103" (Methods), with "the IntCal20 Marine calibration
curve", that is, Marine20 (Fig 2 caption). SI Table S1 prints the corrections as positive, with errors of 69, 135
and 106 years. Pearce and others (2023, Table 1) give those values "in relation to Marine20"; a positive value
means older water and makes a calibrated age younger.

The ages printed in Table S1 do not follow from that method.

| Core | Dates | What reproduces the printed ages | How closely |
|---|---|---|---|
| 64 | 7 | Marine20 with ∆R = −218 ± 135 | All 7 within 2.5 years |
| 67 | 5 | Marine20 with ∆R = −218 ± 135 | All 5 within 2.2 years |
| 77 | 5 | Marine20 with ∆R = −103 ± 106 | 4 within 1.8 years; the fifth, a date of 37,900 years, is off by 538 |
| 52 | 10 | IntCal20, the curve for land samples, with ∆R = −71 ± 69 | 5 of the 6 new dates within 1 year; the boundary date is off by 104; the four older dates from a database by 11 to 1,485 |

The match covers the mean, the error and the ends of the probability ranges. A scan of every correction from −800
to +300 years on four curves found no other recipe that reproduces more than two dates in a core. The stated
method, Marine20 with the positive correction, misses every date by 250 years or more. So the printed ages for
Cores 64, 67 and 77 are the ages the method gives with the sign of the correction reversed, which makes them older
instead of younger. For Core 52 the land curve is the only recipe that fits, and it fits five dates almost
exactly; against that, the OxCal plot for Core 52 in the SI is headed "Marine data from Heaton et al (2020)", like
the other three. The boundary date in Core 52 is a further oddity: its printed age and ranges are reproduced
exactly if the radiocarbon age were 11,020 and not the 11,120 printed beside it.

This analysis was not in the locked plan. The first run found the pattern after the lock and reported it without
the program that found it. It is reproduced here by a separate calibration written for the spot check
(`spotcheck/radiocarbon/`), and is exploratory in the lab's sense: it was looked for after the data were seen.
The first write-up said the authors "flipped the sign" in OxCal and "accidentally" used the land curve. What the
numbers show is which calculation reproduces the table. They do not show how it happened.

The locked test is the recalibration. With the method the paper states, and then with allowances for the older
water of polar seas during the ice age:

| Core and claimed boundary sample | Printed in Table S1 | Marine20, stated correction | plus 200 years | plus 500 years | plus 800 years |
|---|---|---|---|---|---|
| 52, 625 to 630 cm | 12,992 | 12,404 | 12,116 | 11,642 | 11,222 |
| 64, 312 to 318 cm | 13,025 | 12,627 | 12,411 | 11,993 | 11,543 |
| 67, 32 to 35 cm | 13,030 | 12,633 | 12,422 | 12,003 | 11,551 |
| 77, 161 to 162 cm | 12,198 | 11,889 | 11,570 | 11,155 | 10,742 |

Median calibrated ages in years before 1950; the printed column is the mean. The Younger Dryas runs from about
12,900 to 11,700, and the paper's own boundary window is 12,875 to 12,775. With no polar allowance at all, the
boundary dates are 297 to 608 years younger than printed. Cores 52 and 77 have no chance of falling in the 200
years around the onset (12,900 to 12,700), and Cores 64 and 67 have a chance of about one in six (one in four if the correction is given the larger error
printed in the paper's table). With a 500-year
allowance none of the four does, which is the locked check: 4 of 4, where 2 were needed.

The three allowances were the study's own choices. What the curve's authors recommend for polar seas before
11,500 years ago is to calibrate twice, once with the Holocene correction and once with a larger one that depends
on latitude (Heaton and others 2023, section 1.3.2 and Table A2: about 890 to 1,400 years at these cores), and to
treat the two results as a bracket. Done that way the four boundary dates lie between about 12,630 and 9,930. At
the young end all four are after the Younger Dryas, as the notice says. At the old end they are inside it, about 270 to
1,000 years after its onset. The check holds at both ends.

Smaller points, all confirmed against the SI:

- **Four reversals of age with depth,** including 2,860 radiocarbon years just above the boundary in Core 64 and
  640 just above it in Core 52. The authors' own age models flag three of the dates involved as outliers.
- **In Core 67 the spherules peak in the sample above the claimed boundary** (735 per kg at 30 to 32 cm against
  105 at 32 to 35 cm).
- **In Core 77 the dated boundary sample has no spherules;** the peak is 6 cm lower, in an undated sample.
- **What was dated.** The notice says the type and number of foraminifera are missing. SI Table S17 gives a broad
  type and an approximate count (400 to 4,400) for each of the 17 new dates, without species. It also shows that
  bottom-dwelling and surface-dwelling species were dated together in Cores 64 and 67, which the notice does not
  mention; the two live in water of different radiocarbon age.
- **The authors' age models** are built on the same printed ages, so they carry the same offset.

### The objects in SI Figs S30 to S34 (check A2)

The captions call each a "spherule fragment … from Core 52 (574-579 cm)". The five figures show two objects: four
of them are one grain seen as two point spectra, a map and the map's spectrum; the fifth is a second grain. All
four spectra are 92.5 to 96.5% calcium, carbon and oxygen by weight, which is calcium carbonate. The first grain
has a wall pierced by regular pores about half a micrometre across and looks like a foraminifer. The second is
calcareous, and its shape is less telling. The notice's reading holds.

Three things bear on what follows from it.

- The sample is from 574 to 579 cm, which Table S1 dates to about 9,500 years ago (about 8,800 when calibrated as
  stated). It is not the claimed boundary sample in Core 52, which is at 625 to 630 cm. The SI itself says one of
  the samples above the boundary "returned an early Holocene age estimate". The paper nevertheless takes its
  pictures of Core 52 spherules, and the meltglass in Fig 6(b) and 6(f), from this sample, without comment, while
  its text says such material occurs "in the YDB-dated layers of each core".
- This sample is not in the table of counts (SI Table S6), so these grains did not add to the counted peaks
  directly.
- None of the 18 spherules whose chemistry was measured is rich in calcium, so the chemistry tables are not
  affected. How many of the grains counted by eye were foraminifera cannot be known from what is published.

This check is a reading of images by a model, typed into the program. It is not a computation.

### Sampling, and the peak in Core 64 (check A3)

SI Table S6 has 28 samples across four cores. Together they are 85 cm thick, 3.1% of the 27.6 metres of core. (The
first write-up's "16.7%" was the distance between the top and bottom samples in each core, most of it unsampled.)
Each core has five to seven samples, nearly all close to the claimed boundary, so there is little to say what the
background looks like.

The notice's comparison holds in one unit and not the other. For metallic dust particles, a sample in Core 64
outside the boundary (290 to 293 cm) has 680 per kg, against 640 at the boundary in Core 67. For spherules that
sample has none; the largest value outside the boundary in Core 64 is 230 per kg, against 735 at Core 67's peak.
Inside Core 64 the claimed boundary sample still stands above the rest (1,945 metallic particles per kg).

The first write-up reported an arithmetic error in Core 77 (10 spherules in 0.14 g listed as 965 per kg). It is a
misprinted mass: the per-kg figures in that row imply about 10.4 g, like the samples either side.

### Nanoparticles

The plan asked whether twelve measures of the nanoparticles (six metals and six ratios) peak at the claimed
boundary. Each core has six sampled depths.

| Core | Depths inside the claimed boundary | Measures peaking inside | Expected by chance |
|---|---|---|---|
| 64 (312 to 318 cm) | 1 of 6 | 1 of 12 | 2 |
| 67 (32 to 35 cm) | 1 of 6 | 1 of 12 | 2 |

So the nanoparticle peaks do not pick out the boundary, and with six depths the test could say little more. The
first write-up's "9 of 10 outside" in Core 64 is what chance gives. Its "6 of 10 inside" for Core 67 came from
widening the interval by 2 cm each side, which takes in three of the six depths; chance would then give five. The
authors themselves say the nanoparticles reach "abundance peaks just above" the layer, which they put down to slow
settling (SI Fig S7). The ratio of platinum to iridium in the nanoparticles is 1.6 to 3.6 at every depth in both
cores, near the meteoritic value throughout and no different at the boundary. In Core 64 the boundary sample's
ratio of platinum to palladium is 0.76; the paper's own sign of cosmic input is a ratio above 1.

### The "multiply by 100" step (check A4)

The paper's argument, in its words: "we assumed that most Ni and Cr microspherule concentrations were derived from
1 wt% ET material mixed with 99 wt% terrestrial material … we multiplied the Ni and Cr concentration by 100 and
compared them again with the uncorrected ratios … the ET-normalized Baffin Bay ratios of the microspherules
entirely overlap Comet Wild dust and stratospheric cosmic dust … and, thus, are consistent with them containing
~1 wt% ET material." The caption to its Fig 11 says plainly that the measured ratios "do not overlap" the cosmic
ones, "suggesting that the microspherules are not dominated by ET material".

The check is whether this step can tell a spherule with cosmic material from one without. It cannot. Average
continental crust, with no cosmic material in it, has iron to chromium of 426 and iron to nickel of 834; after the
same step they are 4.3 and 8.3, inside the field of comet dust. A standard basalt lands there too. Of the 18
measured spherules, none is in that field as measured and 16 are after the step.

The measurements also go against the step's premise. If most of the nickel in a spherule came from cosmic material
it would have more nickel for its iron than crust does. The spherules have less: the median iron to nickel is
1,556, against 834 for crust. Whether any spherule has a real excess of nickel and chromium depends on what is
taken as the background: 6 of 18 against average crust, none of 18 if the background is scaled up to each
spherule's iron.

Three qualifications. The authors present the step openly as an assumption and conclude only "consistent with";
the first write-up's "trick" was not warranted. The edges of the "comet field" used in this check are ours; the
paper judges overlap by eye. And one of the 18 analyses is a copy of another rescaled by a constant, so there are
17 independent ones. The first write-up also made much of a platinum to iridium ratio of 556 in the spherules.
The iridium readings behind it are at the level of noise, and the figure should not be used.

The notice does not raise this step. It is the study's own argument.

### Oxygen isotopes and references (check A5)

*Oxygen.* Ten bulk sediment samples were measured. Under the locked rule (more than 0.06‰ from the terrestrial
line), three exceed it, all in Core 64: −0.11, −0.08 and −0.07. So the oxygen half of this check does not come
out against the paper. It could hardly have come out either way: one per cent of meteoritic material would move
the value by about 0.004 to 0.04‰, depending on the kind, which is within the scatter. The authors say as much:
"these results must be viewed cautiously".

*References.* The locked check, made offline, found 28 references without a DOI, one DOI used twice and two
malformed ones: three errors, short of the ten required. So check A5 fails on both halves.

The notice's point about references is a different one, that DOIs lead to the wrong papers. The spot check tested
that directly, outside the locked plan, by looking up all 159 DOIs in the reference list on Crossref and doi.org.
Twenty-four fail: 17 do not exist and 7 belong to a different work. Reference 147, cited as a paper on the black
mat in Antarctica, carries the DOI of an article titled "The Power of the Islamic Sword in Narrating the Death of
Indian Buddhism"; reference 5, on the Taurid meteors, carries that of a paper on bending waves in galactic discs.
For most of the 17, the real paper exists under a DOI a digit or two away. The notice's point holds. We did not
test its other point, that citations do not support the statements they are attached to.

## Paper B: shocked quartz at three sites

### The dating (check B1)

**What the paper's test used.** The paper reports that "three calibrated radiocarbon dates" pass a test of
agreement, with a mean of 12,801.6 and χ² = 0.057 (p = 0.972). It does not say which three. They are the three
ages it quotes two paragraphs earlier from Kennett and others (2015): 12,805 ± 55, 12,775 ± 365 and 12,750 ± 235.
Those give a mean of 12,801.6 and χ² of 0.057 exactly. They are not radiocarbon dates. They are the outputs of
statistical models of each site's whole sequence of dates.

Two things follow. A test of agreement between model outputs with errors of 235 and 365 years can hardly fail:
Murray Springs would have to differ from Arlington Canyon by more than 500 years, or Blackwater Draw by about
900, before it did. And the first write-up's central charge against this paper, that it "cherry-picked" a date
from 18.5 cm above the quartz sample, was mistaken. The test did not use that date. Both of Arlington Canyon's
dates appear in the paper's Fig 2 with a statement of what each matches, and the 2015 model includes every date
from the lower part of the section.

**What the paper's tables show.** The notice says not all available dates were included. Of the tables, that is
true: SI Table S2 lists 2 of the 12 dates from the lower 111 cm at Arlington Canyon, Table S3 gives three ages for
Blackwater Draw without their radiocarbon measurements, and Table S4 gives one pooled value for Murray Springs. It
is less true of the test, which rests on models built from all of them. The notice's second point, that the
origin of some dates cannot be determined, is overstated: the table captions cite the two source papers, and both
Arlington Canyon rows can be found there (Beta-161032 and UCIAMS-36304 in Kennett and others 2008, Table 4),
though the table omits the laboratory numbers and we could not trace the three Blackwater Draw rows. Its third
point is broadly true: the tabulated ages range from 12,710 to 12,955, and their 95% ranges from 13,070 to 12,485.

**The locked check.** Check B1 asks whether all the published dates from the layer reject a single age. The list
the first run used for this was wrong, and its result (T = 90.94 from "25 dates") is withdrawn; see the spot
check. With the list rebuilt from the source for Arlington Canyon, the only one of the three sites where the dates
are on the sampled layer:

| Arlington Canyon dates (Kennett and others 2008, Table 4) | Dates | T | p |
|---|---|---|---|
| All from 392 to 503 cm, the section the 2015 model treats as the boundary | 12 | 176.3 | below 10⁻³⁰ |
| The 44 cm dark layer at the base only | 10 | 171.1 | below 10⁻³⁰ |
| Dark layer, leaving out the five the original authors set aside as old wood | 5 | 13.1 | 0.011 |
| The two listed in the paper's SI | 2 | 4.6 | 0.031 |

By the letter the check holds: the twelve dates are not one radiocarbon age, and ten of them are not in the
paper's tables. It shows less than that suggests. Five of the twelve are on wood or carbon that the original
authors themselves judged older than the layer, and without them the disagreement is modest. A test of this kind
cannot tell layers of different ages from old wood in one layer, which is the authors' own explanation. At Murray
Springs and Blackwater Draw the published dates are on Clovis camps, not on the sampled layer, and say nothing
about it directly. The pooled values for the three sites (11,060 ± 40, 10,885 ± 50 and 11,300 ± 235) differ with
T = 9.2, p = 0.010.

### The sampling (check B2)

The SI tables list 66 samples at the three sites. Thirteen were examined for shocked quartz: three at the boundary,
with 5, 7 and 4 grains, and ten above or below, with none. In the tables "--" means not examined.

| Site | Samples in the table | Examined for quartz | Above, at, below the boundary |
|---|---|---|---|
| Arlington Canyon | 31 | 4 | 3, 1, 0 |
| Blackwater Draw | 16 | 3 | 1, 1, 1 |
| Murray Springs | 19 | 6 | 3, 1, 2 |

The notice's point holds: most of each section was not examined, so the paper cannot show that such grains are
absent elsewhere in it. Three details sharpen or soften that.

- **No grain totals for the controls.** The paper gives the number of quartz grains searched for each boundary
  sample (about 8,000, 18,000 and 3,000) and for none of the ten controls. "None found" has no denominator. This
  is the locked check, and it holds.
- **At Arlington Canyon the three controls lie inside the boundary layer as the authors define it.** They are at
  489, 493 and 497 cm; the paper calls the dark layer at the base of the cliff, 44 cm thick, the boundary layer,
  and the 2015 model takes the boundary section to be 111 cm thick. No sample at that site comes from outside it.
- **Nothing was examined below the boundary at Arlington Canyon because nothing is there.** The first write-up
  counted this against the paper. The sample is at the base of the section, which rests on gravel at stream level
  (Kennett and others 2008).

The notice also says "no age models have been reported". That is true of this paper, which presents none of its
own and cites the 2015 models. Its worry that a change in the rate of deposition could produce the spike fits
poorly here, since the counts are grains per slide and not per weight of sediment.

### The label, and the word "harsh"

Under the locked rules, "retraction strongly supported" for Paper B required the notice to document a flaw in the
microscopy. The notice was published nine months before the protocol was written, and the protocol itself notes
that it makes no such allegation. So the strongest label was unavailable, and once either check held the label
"mixed or harsh" followed. It was decided by something known before the lock, and should be read as "the two
stated reasons check out; the microscopy was not tested", which is all the checks show.

The first write-up went further and called the retraction "noticeably harsher than standard journal practice". It
cited no standard. The two that apply say otherwise. COPE's retraction guidelines (2019) advise retraction where
editors "have clear evidence that the findings are unreliable, either as a result of major error … or as a result
of fabrication … or falsification", and say it is not usually appropriate if "the main findings of the work are
still reliable and correction could sufficiently address errors or concerns". PLOS's policy reserves corrections
for cases where "the article's overall results and conclusions are upheld". The notice says the problems call
"into question the validity of the reported conclusions". Whether that judgement was right is a matter of opinion,
and the authors disagree with it. Nothing in the data shows it was harsh.

What the checks leave standing is the observation: sixteen grains with glass-filled fractures in three boundary
samples, and none on ten control slides. What they undercut is the step from there to a layer that is the same
age at three sites and unlike the sediment around it.

## Spot check and corrections

The first run and its write-up were by Antigravity (Google DeepMind). Claude Fable 5.2 (Anthropic) then
spot-checked it with three Claude Opus 5.5 sub-agents, each working from the sources, on 24 November 2026. Scripts
and outputs are in `spotcheck/`.

**What held.** The protocol is unchanged since the lock. The first run's program reproduces its own results
exactly. Every table typed in from an image matches the image: 27 rows of dates for Paper A, and all the dates,
depths and grain counts for Paper B. The Paper A label stands, and so do the recalibrated ages, the foraminifera
reading, the Core 64 comparison in metallic particles, the reversals of age and the "multiply by 100" arithmetic.

**What was wrong.**

1. **A list of dates was partly invented.** The program held "25 published direct dates" for Paper B's three
   sites, described as verified in an earlier study. All eleven Arlington Canyon entries disagree with the table
   they cite: four laboratory numbers do not exist in it, and the rest carry another sample's age, with wrong
   depths and materials. The two dates the paper's own SI lists were missing. At Murray Springs six laboratory
   numbers could not be found in any source and one age is wrong against the primary list. The headline result
   built on this list (T = 90.94, "25 of 25 omitted") is withdrawn. The list was typed before the lock, so the
   fault is one of sourcing, not of fitting to results. It breaks the lab's first rule of evidence all the same.
2. **"Cherry-picked" was wrong,** as set out above, along with "66-fold" (a ratio of two χ² values, neither of
   which rejects anything).
3. **Statements about how errors happened.** "Flipped the sign", "accidentally", "bug" and "trick" describe what
   the authors did or meant. The data show which calculation reproduces a table and what a step does to crust.
   They show nothing about intent or cause.
4. **The dating finding was off the record.** The search that found the reversed sign was in no committed program
   and not in the amendment. One claim in it was false (that all 17 dates match to a year: 16 do) and the account
   of Core 52 left out that the boundary date itself does not fit.
5. **Checks changed after the lock without a record:** the oxygen-isotope test was replaced by a different one
   under an amendment that called itself a parser fix; the nanoparticle test dropped two measures and widened an
   interval; the Core 64 comparison was made in the one unit where it passes; the sampling check gained a
   condition. None changes a label. Amendment 2 records them, and the rerun applies the locked versions.
6. **Numbers.** Coverage 16.7% (a span) is 3.1% sampled. Pore size "1 to 2 µm" is about 0.3 to 0.8. "Four"
   foraminifera figures are five figures of two objects. Platinum "7.15 times the median" was the platinum to iron
   ratio; platinum itself peaks at 1.5 times. The shift in ages "up to 769 years" took its top value from a sample
   that is not a boundary sample; the boundary dates shift 297 to 608. "χ² = 6.99" for six rows is 6.80. Table S17
   has 22 rows, 17 with counts. The quoted phrase "YDB meltglass" is not in the paper. The "+103" correction is the
   authors' own average of two of Pearce's zones, not a value Pearce gives.
7. **"4 of 5 checks" is not "4 of 5 of the notice's claims".** Two of the five (the "multiply by 100" step and the
   oxygen isotopes) test arguments the notice never made. Of the notice's own points for Paper A, the study tested
   the calibration, the foraminifera and the sampling, and the spot check added the references. The points about
   unsupportive citations, engagement with the literature and attribution of data were not tested.
8. **The manifest** gives the wrong address for the land calibration curve; the recorded hash belongs to the
   three-column file in the `rintcal` package. Corrected.

**The rerun.** Amendment 2 was committed before the program was changed. The first run's outputs are in
`results/first_run/`.

## Limits

- **The microscopy was not examined,** by the journal or here. Whether the sixteen grains are shocked quartz, and
  what made them, needs the slides and several laboratories that do not know which sample is which.
- **Some checks are readings and choices.** A2 is a judgement of images. The "comet field" and the crust-like
  threshold in A4 are ours. The three polar allowances in A1 are ours; the published recommendation gives a wider
  bracket, at both ends of which the check holds.
- **The sign and curve finding is exploratory,** found after the data were seen. It is strong because sixteen
  dates match on three numbers each at the paper's own stated values, and weaker for Core 52.
- **The 24 failed DOIs** were found by lookups on 24 November 2026 and are outside the locked plan.
- **Sources not reached:** Waters and Stafford's table of individual dates, the SI of Kennett and others 2015,
  COPE's guidelines on COPE's own site (read in a copy hosted by a publisher), and "Olsen et al. 2014", which the
  protocol cites for the largest polar allowance without a full reference.
- **No second vendor has replicated this.** The spot check and the first run are by different vendors' models,
  but a spot check follows the first run's tracks.
- **One session each.** No specialist in radiocarbon, foraminifera or shock metamorphism has reviewed it.

## Departures from the plan

- **Amendment 1** (first run): tables printed as images were typed in by hand; three parser fixes; and a change
  to the oxygen-isotope test that should not have been described as a parser fix.
- **Amendment 2** (spot check): the date list for check B1 rebuilt from the source; the paper's test reproduced
  with the ages it used; checks B2, A5 and the nanoparticle test returned to their locked form; coverage reported
  as sampled thickness as well as span.
- **Not in the plan at all:** the reversed-sign and land-curve analysis, the reversals of age with depth, the
  Crossref lookups, and the bracket from Heaton and others 2023.
- The lock was committed 13 seconds after the files it locks, and the first amendment in the same commit as the
  results, so the record cannot show that the amendment came before the run.

## Spending

Nothing was paid for. The data are open and the work ran locally.

## Who did the work

AI did this work. Antigravity (Google DeepMind; the first report names no model version) designed the study, wrote
the program, ran it and wrote the first report on 24 November 2026. Claude Fable 5.2 (Anthropic) spot-checked it
the same day, wrote Amendment 2 and this report; Claude Opus 5.5 sub-agents reran the program, recalibrated the
dates independently, read the tables and figures against the typed values, looked up the references and applied
the amendment. Eugene directed it: he asked for the study and for the spot check.

## What this means

Two papers offering new evidence that a comet struck at the start of the Younger Dryas were retracted in February
2026, and their authors objected. We checked the journal's reasons against the papers' own data. For the paper on
sea-floor cores from Baffin Bay the reasons hold, and the dating turns out worse than the journal said: the
published ages are not the ones the paper's stated method gives, and with that method the layers are a few hundred
to a thousand or more years too young to mark the start of the cold. Two of the pictured "spherule fragments" are
calcium carbonate and one is plainly a microfossil, and the paper's chemical argument for comet material would
give the same answer for ordinary rock. For the paper on shocked quartz, the journal's two reasons mostly hold as
well: the claim that three sites share one date rests on a test that could not have failed, and too little of each
section was examined to show the grains are special to one layer. But nobody, the journal included, has shown
anything wrong with the grains themselves. So these two papers do not establish that anything fell, and they do
not show that nothing did. The sixteen grains remain an observation that only other laboratories, looking at the
same slides without knowing which is which, can confirm or dismiss.
