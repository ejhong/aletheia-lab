---
# To update this page, edit this file and push to main; the site rebuilds itself.
# The figures are made by questions/yd-megafauna-timing/analysis/make_figures.py from the results files.
summary: A central claim of the Younger Dryas impact hypothesis is that a comet strike 12,850 years ago abruptly wiped out North America's Ice Age megafauna. Two independent public archives—dung-fungus spores in 11 lakes and caves, and 326 directly dated megafauna bones recalibrated on IntCal20—test whether the great animals vanished before the cold, right at it, or over thousands of years spanning it.
verdict: Drawn-out and staggered across the Younger Dryas, not one day of extinction
result: Neither a single-day wipeout at 12,850 years ago nor a clean pre-Younger Dryas disappearance fits the public record. In 9 of 11 lake and cave cores across seven US states, large-herbivore dung spores began falling more than a thousand years before the cold began (median half-drop 14,669 years ago, p = 0.014). Yet in modern AMS radiocarbon dates on fossil bone and tooth collagen, ten mammoths, mastodons, a giant beaver and a short-faced bear each have over 99% probability of living centuries after 12,750 years ago—putting nearly seven times more fossil probability inside the Younger Dryas than radiocarbon-plateau smearing can explain (p < 0.0005).
dek: Earlier Younger Dryas studies in the lab tested ice-core smoke, global charcoal, cooling shape, platinum, Tunguska and the Taurid stream. Here we test the giant animals themselves—locking every rule before opening either archive.
updated: 2026-11-23
---

> **Where things stand, 23 November 2026.** Initial locked run finished (by Antigravity / Google DeepMind, directed by Eugene; open to second-vendor replication). By the pre-registered decision rule, the timing verdict is **Staggered spanning the Younger Dryas** (`staggered_spanning_yd`): herbivore collapse began more than a millennium early in most lake cores, accelerated sharply around `12,800–12,600` years ago in dated bones, and left directly dated mammoths, mastodons, giant beavers and short-faced bears walking North America `600` to `1,900` years after the claimed impact.

{{figure: yd-megafauna-timing/tiles}}

## What we tested and found

The Younger Dryas impact hypothesis makes a clean prediction about North America's Ice Age giants—mammoths, mastodons, ground sloths, horses, camels, giant beavers and saber-toothed cats. If a cosmic strike at `~12,850` years ago brought them down, large herbivores should still have been abundant right up to the start of the cold (`12,896` years ago in Greenland ice), and their bones should disappear immediately after it.

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

- **Direct fossil dates do surge and drop sharply around `12,800–12,600` BP.** Unlike the lake dung spores, dated bones do *not* thin out before `13,000` BP—they peak between `13,500` and `12,900` BP (`1.9×` higher than during `14,700–13,500` BP) and then fall roughly tenfold between `12,800` and `12,600` BP. That sharp bone drop is real in the dated catalogue and probably reflects both a genuine late-phase crash (human hunting and abrupt cooling hitting already reduced herds) and strong discovery bias toward dating the youngest skeletons in newly ice-free bogs and archaeological sites.
- **Yet an instant `12,850` BP wipeout fails completely.** Even with the `12.9 ka` plateau and real lab errors, `2,000` simulated overnight wipeouts leak at most **`0.73%`** (99th percentile) of modern `Score-12` AMS probability mass into the post-impact Younger Dryas window (`12,700–11,700` BP). The real AMS record puts **`4.95%`** there—**`6.8×` higher**, reached by **`0` of `2,000`** simulations (`p < 0.0005`). Restricting to herbivores only, dropping Rancho La Brea, or applying Surovell's taphonomic preservation correction all give the exact same `p < 0.0005` result.

{{figure: yd-megafauna-timing/radiocarbon}}

Behind that `6.8×` excess sit **`10` gold-standard `Score-12` AMS collagen and tooth-dentin dates**—from New York, Nevada and Kansas—every single one of which carries **`> 99.3%`** individual posterior probability of being younger than `12,750` years ago: five mammoths (Lewiston `12,091` BP, Randolph `12,196` BP, two Pyramid Lake individuals `12,167` and `12,222` BP, and Wallman `12,644` BP), three mastodons (Colgan-King Ferry `12,273` BP, Hiscock `12,444` and `12,638` BP), one giant beaver (Clyde `11,774` BP) and one giant short-faced bear (Bonner Springs `10,953` BP).

## One genus after another

Estimating each genus's true extinction date—correcting for the Signor–Lipps lag between the last fossil we happen to find and the last animal that lived—shows a stagger of more than a thousand years even on the strictest modern AMS dates alone.

In the `Score-12` AMS subset (which strips out questionable 1960s–70s conventional bone dates), North American horses (`Equus`, `OLE = 13,061` BP, 95% CI `12,715–13,143`) and dire wolves (`Canis dirus`, youngest `13,674` BP) disappear before or right at the start of the Younger Dryas. By contrast, **mammoths** (`OLE = 11,852` BP, CI `10,295–12,150`), **mastodons** (`OLE = 11,867` BP, CI `11,079–12,412`) and **Harrington's mountain goat** (`OLE = 10,333` BP, CI `7,117–12,329`) all have 95% extinction intervals strictly inside or after the Younger Dryas—centuries past any single impact day.

{{figure: yd-megafauna-timing/taxa}}

## What this does—and does not—settle

Taken together, the two archives rule out a single continent-wide extinction triggered by a cosmic impact at `12,850` years ago: herds were already shrinking across most of North America a millennium earlier, and multiple iconic giant mammals survived `600` to `1,900` years afterward. At the same time, this study tests *timing*, not *cause*: it cannot separate the roles of human arrival, Bølling–Allerød warming and vegetation shift, and Younger Dryas cooling in driving that drawn-out collapse.

::: details Methods, data, and caveats
- **Protocol and lock:** `questions/yd-megafauna-timing/protocol.md`, locked at `2026-11-24T01:56:12Z` (`protocol.lock`, SHA-256 `fd7ae0a9bfae`) before inspecting any spore percentages or calibrated fossil ages. Zero amendments.
- **Public datasets:** `11` qualifying calibrated North American Neotoma v2 pollen records with `Sporormiella` (`14957, 17717, 19937, 45695, 61900, 16175, 16179, 46645, 47259, 3056, 15876`), Broughton & Weitzel (2018) *Nature Communications* 9:5441 Supplementary Data 1 (`521` vetted direct dates, Barnosky & Lindsey `Score 11–12`), and `IntCal20` (Reimer et al. 2020). Full URLs and SHA-256 hashes in `questions/yd-megafauna-timing/MANIFEST.md`.
- **Legacy conventional vs. modern AMS dates:** When all `Score 11–12` dates are pooled, a handful of 1960s–70s conventional (`ST`) bone dates pull nominal `OLE` for mastodons, ground sloths and saber-toothed cats down to `8,357–8,566` BP. Because legacy conventional bone pretreatment is prone to young-carbon contamination, our primary claims rely on the strict `Score-12` AMS collagen/dentin tier, where every post-impact survivor and every taxon stagger result still holds cleanly.
- **Lake-core age models:** Individual Neotoma core chronologies carry a few centuries of tie-point uncertainty (and potential hard-water offsets where bulk sediment was dated), which is why pooling `11` independent basins across seven states alongside direct bone-collagen AMS dates is essential.
- **Full report and code:** `questions/yd-megafauna-timing/RESULTS.md`, `questions/yd-megafauna-timing/analysis/megafauna_timing.py`, and `questions/yd-megafauna-timing/analysis/test_megafauna.py` (4/4 synthetic recovery tests passing).
:::
