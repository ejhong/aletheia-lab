---
# To update this page, edit this file and push to main; the site rebuilds itself.
# The figures are made by questions/flood-myths/analysis/make_figures.py from the results file.
summary: Flood stories are told all over the world. One old idea is that they remember the sea rising 120 metres at the end of the Ice Age. If so, they should be commoner where the sea took the most land. We tested that in a catalogue of the myths of 927 peoples.
verdict: Not found, in a test weaker than it first looked
result: Among 396 peoples living near water, flood motifs are as common beside the narrowest drowned shelves (36%) as beside the widest (34%), and the model fixed in advance finds no link. A spot check found faults: some "drowned shelf" was the Caspian Sea and the Great Lakes, a third of the "flood myths" are not clearly about floods, and one of the plan's two checks on the method failed. Mending what could be mended leaves the answer the same. A modest effect is not excluded, and the test says almost nothing about Australia.
dek: Do the world's flood stories remember coasts that drowned when the Ice Age ended? A test on 927 peoples and a map of the sea floor.
updated: 2026-11-24
---

> **Where things stand, 24 November 2026.** This study was run by Google's model (Antigravity, Google DeepMind) under Eugene's direction, with its plan fixed beforehand. Anthropic's model (Claude Fable 5.2) then spot-checked it: reran the program, refitted the main model with separately written code, and recomputed the drowned areas from the full map. The finding stands. Several things said about it did not, and this page is the corrected version. It has not been replicated by a second company's model.

{{figure: flood-myths/tiles}}

## What was asked

Twenty thousand years ago the sea stood about 120 metres lower than now. As the ice melted it rose and covered wide plains: under the North Sea, between the islands of Southeast Asia, around Australia, between Siberia and Alaska.

Stories of a great flood are told by hundreds of peoples, and an old idea holds that they are a memory of that rise. The idea makes a prediction that can be checked on a map. Peoples whose coast lost a great deal of land should tell flood stories more often than peoples whose coast drops steeply and lost almost none.

Two public sources make the check possible. Yuri Berezkin's catalogue records which of some 2,500 story motifs are found among each of 958 peoples; it is used here as packaged by Michalopoulos and Xue (2021), with each people's location and language family. NOAA's ETOPO map gives the depth of the sea floor everywhere. Before any result was seen, the plan fixed 17 flood motifs to count (leaving out Noah's Ark), the measure of drowned land (sea floor shallower than 120 metres within 250 km), and the model.

## What was found

There is no sign of the predicted pattern.

Among the 396 peoples living within 150 km of water, sort by how much shelf drowned nearby and split into four equal groups. The share with at least one flood motif runs 36%, 37%, 35%, 34%, from the narrowest shelves to the widest. Inland it is 39%.

{{figure: flood-myths/coastal_quartiles_and_models}}

The model fixed in advance compares peoples within the same language family and allows for how thoroughly each was studied, for rivers, earthquakes, climate and latitude. Its estimate of the link is −0.01, with a standard error of 0.06: zero, as near as it can tell. A separately written program gives the same numbers. Using the last 60 metres of the rise in place of all 120, or a wider circle, changes nothing.

{{figure: flood-myths/world_map}}

## What the spot check found

**Some of the "drowned shelf" is not sea.** The plan counted every part of the map below sea level as sea. That takes in the Caspian, whose surface is 28 metres below sea level, and with it the Great Lakes, Lake Baikal and dry basins such as Death Valley. About a tenth of the drowned land in the study is of this kind. Thirty-three of the 396 "coastal" peoples have no sea within 150 km, among them the Chechens, the Kalmyks and the Iroquois, and twelve of the 99 peoples in the widest-shelf group live on the Caspian shore. Counting real sea only, the estimate is −0.04 and still indistinguishable from zero.

**A third of the "flood myths" are not clearly about floods.** Seven of the 17 motifs are loosely connected at best: descent from a dog, the revolt of household objects, monsters that destroy people, a dragon that holds back the waters. Of the 351 peoples counted as having a flood myth, 138 have only those. Counting motifs built around a flood, about a quarter of peoples have one, not nearly four in ten. With that narrower list the result is the same.

**One of the two checks on the method failed.** The plan said a "no" would count only if the catalogue could be shown to carry real traces of the physical world. Earthquake motifs do turn up more in earthquake country. Sea motifs turn up more near the sea only weakly, well short of the mark the plan set. The first write-up called the gate passed. The earthquake check was also run on all 927 peoples with a simpler model; in the flood test's own sample and model it is not significant. And it concerns a danger that is present now. The drowning ended at least 7,000 years ago, and many peoples have moved since.

**The test could have missed a modest effect.** The first write-up said an effect the size of the earthquake one would have been "easily" found. It would have been found about two times in three. The data do not rule out a difference of up to ten percentage points between narrow and wide shelves.

**Things said that had not been done.** The first write-up said the result was the same with high latitudes left out. Nobody had run that. Run now, it is. It also said the plan was followed with no departures. There were five, the largest being 31 peoples dropped for a missing temperature value, 29 of them small islands of the Pacific and Indian Oceans.

**Australia.** The first write-up said the catalogue codes "16 coastal Aboriginal Australian groups". The box drawn on the map holds 16 peoples and three are Australian; most are in eastern Indonesia and New Guinea. The catalogue treats all of Australia as eight regions.

**Explanations nobody tested.** That flood stories are "far better explained by river floods, storms, tsunamis and diffusion" was the write-up's opinion. Nothing here tested it.

## What this does not settle

- **Stories about particular drowned places.** Nunn and Reid (2016) collected Aboriginal stories from 21 places around the Australian coast that tell of specific shores going under, and argue they are older than 7,000 years. That is a different claim from a worldwide flood motif, and this study has almost nothing from Australia.
- **Where people were then.** The catalogue places each people where it lived in recent centuries. Polynesians, Bantu speakers and Inuit reached their coasts long after the shelves there had drowned. For them the test measures land their ancestors never lost.
- **A modest effect.** See above.
- **What flood stories are, if not this.** Not tested.

## What this means

If the world's flood stories were a shared memory of the sea rising, they should be thickest where the sea took most. In this catalogue they are not, and that counts against the idea. It counts for less than the first report claimed: the measure of drowned land had a hole in it, the list of flood motifs was loose, the study's own test of its method half failed, and a modest effect could have slipped through. The answer survived the repairs we could make. It is a "not found", with those limits attached.

::: details Methods, data and checks
- **Plan and lock.** `questions/flood-myths/protocol.md`, locked 2026-11-24T17:25:14Z. Five departures from the plan, found by the spot check, are recorded in `amendments.md`.
- **Data.** Michalopoulos and Xue (2021), *Quarterly Journal of Economics* 136(4), replication package on Harvard Dataverse (doi:10.7910/DVN/IXOHKB, CC0), which carries Berezkin's catalogue; NOAA ETOPO 2022 at one arc-minute. Addresses and checksums are in `MANIFEST.md`.
- **The model.** Share of a people's recorded motifs that are among the 17, against the logarithm of drowned shelf area, with controls and language-family fixed effects; standard errors clustered by language family and, separately, allowing for nearness on the map.
- **Spot check.** `questions/flood-myths/spotcheck/`. Everything there beyond the rerun was done after the results were known and is exploratory.
- **Full report.** `questions/flood-myths/RESULTS.md`.
- **Who did the work.** AI did. Antigravity (Google DeepMind) ran the study; Claude Fable 5.2 (Anthropic) spot-checked and corrected it, with Claude Opus 5.5 sub-agents. Eugene directed both. No specialist has reviewed it.
:::
