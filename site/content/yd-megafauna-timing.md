---
# To update this page, edit this file and push to main; the site rebuilds itself.
# The figures are made by questions/yd-megafauna-timing/analysis/make_figures.py from the results files.
summary: The popular form of the Younger Dryas impact hypothesis has a comet wiping out North America's Ice Age animals about 12,850 years ago. Two public records can say when they went: the dung-fungus spores of large plant-eaters in 11 lake and cave cores, and 326 radiocarbon dates measured on the animals' own bones and teeth.
verdict: Not one day of extinction: some animals lived on for centuries. But dated bones do fall steeply as the cold begins
result: A sudden, total extinction 12,850 years ago is ruled out. Ten well-dated mammoths, mastodons, a giant beaver and a short-faced bear lived 200 to 1,900 years later, more than the blur of radiocarbon dating can explain. In most of 11 lake and cave cores the dung spores of large plant-eaters were already falling a thousand years or more before the cold, by one measure of four. Against that, dated bones are at their most numerous just before the cold begins and fall about tenfold as it starts. The hypothesis's authors now say the extinction took centuries to millennia, and this record fits that as well as it fits hunting or the cold alone.
dek: When did North America's great animals go: before the cold, at its start, or over thousands of years? Spot-checked afterwards; not replicated.
updated: 2026-11-24
---

> **Where things stand, 24 November 2026.** The locked run finished on 23 November with no amendments (by Antigravity, Google DeepMind, directed by Eugene). The verdict by the rule fixed in advance is **staggered, spanning the Younger Dryas**. A spot check by Claude Fable 5.2 (Anthropic) reran the program, got the same numbers, and found that the write-up read more into them than they show: see the next section. No model from a second company has replicated the study, and none is planned for now.

{{figure: yd-megafauna-timing/tiles}}

## Spot check: what holds and what does not

Anthropic's model checked this study after it was published, reran its program and recalculated the main figures separately. The numbers hold. The page has been corrected in these places. The figures are as first made.

- **Survival past the claimed strike holds.** Ten well-dated animals lived on, and no reasonable version of a sudden extinction puts that many dates so late. Their dates fall 206 to 1,897 years after 12,850 years ago; the first version of this page said "600 to 1,900".
- **That rules out a sudden, total extinction, which the hypothesis's authors no longer claim.** They now write that extinctions "may play out over centuries to millennia", with small groups surviving. Survivors do not count against that.
- **The steep fall in dated bones is a point in the hypothesis's favour, and was explained away.** Dated bones peak just before the cold begins and fall about tenfold between 12,800 and 12,600 years ago. The first version put that down to hunting and to which skeletons get dated; neither was tested. A blow at the onset, hunting, and the cold itself would all look like this.
- **The dung-spore result is weaker than written.** Only one of four measures of the decline is significantly earlier than the cold. In 6 of the 11 cores, not 9, the fall to half came more than a thousand years early.
- **A date was on the wrong scale.** The start of the cold, 12,896, is counted from the year 2000 and is 12,846 on the scale used for the fossils. Nothing in the results changes.

The full list is in the study's `RESULTS.md`, and the checking scripts are in `questions/yd-megafauna-timing/spotcheck/`.

## What we tested and found

The Younger Dryas impact hypothesis makes a clean prediction about North America's Ice Age giants—mammoths, mastodons, ground sloths, horses, camels, giant beavers and saber-toothed cats. If a cosmic strike at `~12,850` years ago brought them down, large herbivores should still have been abundant right up to the start of the cold (`12,896` years before 2000 CE in Greenland ice, which is `12,846` on the scale used for the fossils), and their bones should disappear immediately after it.

We checked that prediction across two completely independent public records, with every filter, formula and decision threshold locked before opening either dataset:

1. **Dung-fungus spores (*Sporormiella*) in `11` calibrated lake and cave cores** from the Neotoma database, spanning seven US states (`NY, OH, IN, WY, CO, TX, CA`). These spores come from fungi that grow on the dung of large plant-eaters and drop sharply when local megaherbivores disappear.
2. **`326` directly dated North American megafauna fossils** from Broughton & Weitzel (2018), recalibrated from scratch on the current `IntCal20` curve—with primary weight on the **`214` modern `Score-12` AMS bone and tooth collagen dates**—tested against `2,000` simulated instant-wipeout catalogues to measure exactly how much false "afterlife" the notorious `12,900`-year radiocarbon plateau can create.

{{figure: yd-megafauna-timing/verdict}}

## Pillar 1: Dung spores in eleven lakes and caves

Across the continent, large-herbivore dung spores began falling long before the Younger Dryas cold arrived. All `9` of `9` high-spore cores peaked before `12,896` years ago (median `14,950` BP, `p = 0.0039`), and **`9` of `11`** fell past half their peak beforehand (median **`14,669` BP**, **`1,773` years early**, Wilcoxon `p = 0.0137`). On the classic `2%` threshold, `6` of `9` cores—including Appleman Lake in Indiana (`14,295` BP), Silver Lake in Ohio (`14,109` BP), Binnewater Pond and Otisville in New York (`15,572` and `14,107` BP), Mono Lake in California (`14,830` BP) and Lower Paintrock Lake in Wyoming (`13,591` BP)—crossed down `700` to `2,700` years before the Younger Dryas began.

Just as important, the decline did not finish before the cold everywhere. Three cores—Como Lake in Colorado (`12,211` BP), Hall's Cave in Texas (`11,310` BP) and Spicer Lake in Indiana (`11,173` BP)—held spores above `2%` well past `12,896` years ago. Put all eleven cores together, and the continental median drifts downward smoothly from `15,200` to `10,600` years ago, with no cliff at `12,896` BP.

{{figure: yd-megafauna-timing/sporormiella}}

## Pillar 2: Direct fossil dates and the radiocarbon plateau

Earlier work in the lab on human radiocarbon dates (`#40`) ran into a real snag: radiocarbon ages flatten out around `12,900` years ago, smearing calendar dates across centuries. To avoid being fooled by that plateau, we simulated **`2,000` fake fossil catalogues** in which North American megafauna thrived steadily until `12,850` years ago and vanished overnight, added each subset's exact lab measurement errors, and ran every simulated catalogue back through `IntCal20`.

Two things stand out clearly in the comparison:

- **Direct fossil dates do surge and drop sharply around `12,800–12,600` BP.** Unlike the lake dung spores, dated bones do *not* thin out before `13,000` BP—they peak between `13,500` and `12,900` BP (`1.9×` higher than during `14,700–13,500` BP) and then fall roughly tenfold between `12,800` and `12,600` BP. That sharp drop is real in the catalogue of dated bones. A blow at the onset would produce it; so would hunting, the cold, or a habit of dating the youngest skeletons in newly ice-free bogs and at archaeological sites. This study does not test which.
- **Yet an instant `12,850` BP wipeout fails completely.** Even with the `12.9 ka` plateau and real lab errors, `2,000` simulated overnight wipeouts leak at most **`0.73%`** (99th percentile) of modern `Score-12` AMS probability mass into the post-impact Younger Dryas window (`12,700–11,700` BP). The real AMS record puts **`4.95%`** there—**`6.8×` higher**, reached by **`0` of `2,000`** simulations (`p < 0.0005`). Restricting to herbivores only, dropping Rancho La Brea, or applying Surovell's taphonomic preservation correction all give the exact same `p < 0.0005` result.

{{figure: yd-megafauna-timing/radiocarbon}}

Behind that `6.8×` excess sit **`10` `Score-12` AMS collagen and tooth-dentin dates**—from New York, Nevada and Kansas—every single one of which carries **`> 99.3%`** individual posterior probability of being younger than `12,750` years ago: five mammoths (Lewiston `12,091` BP, Randolph `12,196` BP, two Pyramid Lake individuals `12,167` and `12,222` BP, and Wallman `12,644` BP), three mastodons (Colgan-King Ferry `12,273` BP, Hiscock `12,444` and `12,638` BP), one giant beaver (Clyde `11,774` BP) and one giant short-faced bear (Bonner Springs `10,953` BP).

## One genus after another

Estimating each genus's true extinction date—correcting for the Signor–Lipps lag between the last fossil we happen to find and the last animal that lived—shows a stagger of more than a thousand years even on the strictest modern AMS dates alone.

In the `Score-12` AMS subset (which strips out questionable 1960s–70s conventional bone dates), North American horses (`Equus`, `OLE = 13,061` BP, 95% CI `12,715–13,143`) disappear before or right at the start of the Younger Dryas (the youngest of the few dire wolf dates is `13,674` BP, too few to estimate from). By contrast, **mammoths** (`OLE = 11,852` BP, CI `10,295–12,150`), **mastodons** (`OLE = 11,867` BP, CI `11,079–12,412`) and **Harrington's mountain goat** (`OLE = 10,333` BP, CI `7,117–12,329`) all have 95% extinction intervals strictly inside or after the Younger Dryas—centuries past any single impact day.

{{figure: yd-megafauna-timing/taxa}}

## What this does—and does not—settle

Taken together, the two records rule out a sudden extinction of everything about `12,850` years ago: in most cores the dung spores were falling long before, and well-dated mammoths, mastodons, a giant beaver and a short-faced bear lived `200` to `1,900` years afterwards. They do not rule out a blow at that time that left survivors, which is what the hypothesis's authors now describe, and the steep fall in dated bones as the cold begins is what such a blow would look like. The study tests *timing*, not *cause*: it cannot separate a strike from human hunting, the warming before the Younger Dryas, or the cold itself.

::: details Methods, data, and caveats
- **Protocol and lock:** `questions/yd-megafauna-timing/protocol.md`, locked at `2026-11-24T01:56:12Z` (`protocol.lock`, SHA-256 `fd7ae0a9bfae`) before inspecting any spore percentages or calibrated fossil ages. Zero amendments.
- **Public datasets:** `11` qualifying calibrated North American Neotoma v2 pollen records with `Sporormiella` (`14957, 17717, 19937, 45695, 61900, 16175, 16179, 46645, 47259, 3056, 15876`), Broughton & Weitzel (2018) *Nature Communications* 9:5441 Supplementary Data 1 (`521` vetted direct dates, Barnosky & Lindsey `Score 11–12`), and `IntCal20` (Reimer et al. 2020). Full URLs and SHA-256 hashes in `questions/yd-megafauna-timing/MANIFEST.md`.
- **Legacy conventional vs. modern AMS dates:** When all `Score 11–12` dates are pooled, a handful of 1960s–70s conventional (`ST`) bone dates pull nominal `OLE` for mastodons, ground sloths and saber-toothed cats down to `8,357–8,566` BP. Because legacy conventional bone pretreatment is prone to young-carbon contamination, our primary claims rely on the strict `Score-12` AMS collagen/dentin tier, where every post-impact survivor and every taxon stagger result still holds cleanly.
- **Lake-core age models:** Individual Neotoma core chronologies carry a few centuries of tie-point uncertainty (and potential hard-water offsets where bulk sediment was dated), which is why pooling `11` independent basins across seven states alongside direct bone-collagen AMS dates is essential.
- **Full report and code:** `questions/yd-megafauna-timing/RESULTS.md`, `questions/yd-megafauna-timing/analysis/megafauna_timing.py`, and `questions/yd-megafauna-timing/analysis/test_megafauna.py` (4/4 synthetic recovery tests passing).
:::
