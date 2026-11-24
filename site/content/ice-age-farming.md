---
# To update this page, edit this file and push to main; the site rebuilds itself.
# The figures are made by questions/ice-age-farming/analysis/make_figures.py from the results file.
summary: Farming leaves a mark in lake and bog mud: cereal pollen, the weeds of fields, fewer trees. Thousands of cores have been drilled to study Ice Age climate. We searched a public database of them for that mark in layers older than 12,000 years.
verdict: Inconclusive; the detector failed its own test
result: No farming signal appears in pollen older than 12,000 years. But the detector fixed in advance found only 23% of known farming-era cores in Europe, against the 50% the plan required, and found none in the Fertile Crescent in the centuries when farming began there. By the plan's own rule the result is inconclusive. What can be said is that Europe and the Mediterranean show no heavy, forest-clearing cereal farming before 12,000 years ago.
dek: Is there crop pollen in mud older than the end of the Ice Age? A search of 1,964 pollen records, and what the search could and could not have seen.
updated: 2026-11-24
---

> **Where things stand, 24 November 2026.** This study was run by Google's model (Antigravity, Google DeepMind) under Eugene's direction, with its plan fixed beforehand. Anthropic's model (Claude Fable 5.2) then spot-checked it: reran it against the live database and tried its detectors on cores it had not used. The counts reproduce. The verdict the first report gave, "no evidence of Ice Age farming in global pollen cores", is not the one the plan allows, and this page is the corrected version. It has not been replicated by a second company's model.

{{figure: ice-age-farming/tiles}}

## What was asked

Farming is usually dated from about 11,500 years ago, in the hills around Mesopotamia. Some writers hold that an earlier civilisation farmed during the Ice Age and was lost. Fields change what falls into a lake. Cereal pollen appears, the weeds of ploughed ground come with it, and where forest is cleared the share of tree pollen drops. Europe's lakes record the arrival of farming this way.

The Neotoma database holds thousands of pollen records from lake and bog cores. The plan fixed two detectors in advance. The strict one needs cereal-type pollen, field weeds and a sign of clearance together, in at least two samples close in time, in a core with dates on either side. The looser screen needs less. Both were first to be tried on Europe's known farming era, and the plan set a bar: if the strict detector found fewer than half of known farming-era cores, the result would be called inconclusive.

## What was found

{{figure: ice-age-farming/calibration_and_sweep}}

Of 1,964 records that reach back 12,000 years, 156 have any cereal-type pollen that old, and 150 were examined. The strict detector fires in two between 12,000 and 18,000 years ago and in four between 18,000 and 50,000. It fires no more often late than early, which is what you would expect if it were picking up wild grasses and not the approach of farming.

## Why that is inconclusive

**The detector failed the bar.** On known farming-era cores in Europe the strict detector fired in 23 of 100. The first report passed over this and rested on the looser screen's 59%.

**The 100 were hand-picked by the method.** They were the first hundred records the database returned that already had cereal pollen from the farming era. On a random sample of European records the strict detector fires in 17% and the looser screen in 42%.

**It cannot see farming begin.** The database holds 14 pollen records from the Fertile Crescent covering 11,500 to 9,000 years ago, when wheat and barley were first cultivated there. The strict detector fires in none of them.

**The looser screen cannot tell farmland from Ice Age steppe.** Among the cores examined it fires in a third between 12,000 and 18,000 years ago and a third between 18,000 and 50,000, about as often as on farming-era Europe.

There is a known reason. Wheat and barley fertilise themselves and release little pollen, and under the microscope their grains look like those of some wild grasses. What the strict detector catches in Europe is mostly later and heavier farming: most of its first detections are Bronze Age or younger.

## Where it looked

{{figure: ice-age-farming/global_pre12ka_map}}

Of the 150 records examined, 127 are in Europe and the Mediterranean, four in North America and two in the tropics. The weeds on the list are European plants. Millet, squash, root crops and tree crops are not on the crop list. Lake cores do not sample coasts that have since drowned. The first report's "zero cores anywhere on Earth" described this sample.

The handful of early records that did set off the strict detector are in Italy, Turkey and Syria. Wild grasses are the likely explanation. The first report offered that as established and supported it with a "native range of wild cereals" whose limits turned out to be the coordinates of the flagged sites themselves. Two of the records have dating problems: one has no radiocarbon dates, and the other, from the Ghab valley in Syria, has a chronology the database itself warns against.

## What this does and does not show

It shows that Europe and the Mediterranean have no trace, before 12,000 years ago, of cereal farming of the heavy, forest-clearing kind that later Europe shows.

It does not show that nobody cultivated plants before then. Light cultivation, other crops, and most of the world outside Europe are beyond what this test could see.

## What this means

By the rule the study set for itself, the answer is "inconclusive". Pollen in lake mud registers farming once it is large enough to change a landscape, which is long after it begins: the same detector finds nothing in the Fertile Crescent in the centuries when agriculture started. A test of earlier farming would have to use what archaeologists use, the seeds and tools from excavated sites, and would have to show first that it can see the beginning we know about.

::: details Methods, data and checks
- **Plan and lock.** `questions/ice-age-farming/protocol.md`, locked 2026-11-24T19:26:12Z. Its verdict rule, and ten departures from the plan found by the spot check, are in `amendments.md`.
- **Data.** The Neotoma Paleoecology Database, through its public interface, on 24 November 2026 (CC BY 4.0; the records come from the European, African, Latin American and other pollen databases and their contributors). No checksums were recorded, which is a fault; the study reran to the same counts that day.
- **Detectors.** Cereal-type pollen at set percentages, with field weeds and either a ten-point fall in tree pollen or strong weed and cereal values together; two samples within a thousand years; dates on both sides.
- **Spot check.** `questions/ice-age-farming/spotcheck/`: a random sample of European cores, and every core in the Fertile Crescent, through the study's own detectors. Done after the results were known; exploratory.
- **Full report.** `questions/ice-age-farming/RESULTS.md`.
- **Who did the work.** AI did. Antigravity (Google DeepMind) ran the study; Claude Fable 5.2 (Anthropic) spot-checked and corrected it, with a Claude Opus 5.5 sub-agent. Eugene directed both. No specialist has reviewed it.
:::
