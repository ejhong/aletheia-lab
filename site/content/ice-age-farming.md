---
summary: Global audit of 1,964 pre-12,000 BP Neotoma fossil pollen cores using a multi-proxy farming detector calibrated on the European Neolithic spread; zero pre-Holocene farming signal above deep-glacial wild-grass background.
verdict: Null — no evidence of Ice Age farming in global fossil pollen cores
result: Calibrated on 100 European Holocene cores, our pre-registered cereal-plus-weed detector catches Neolithic farming at 59% (relaxed) / 23% (strict) while recovering the real southeast-to-northwest Neolithic wave (p = 0.0029) and firing in only 2.5% / 0% of Mesolithic northern European controls. Across all 1,964 global Neotoma cores reaching ≥12,000 cal BP, Late Glacial layers (12–18 ka) trigger at a lower rate than the deep Ice Age negative control (18–50 ka): 0.10% vs. 0.31% strict (p = 0.95) and 2.39% vs. 2.82% relaxed (p = 0.77). Every single pre-12 ka strict hit lies in Italy, Turkey, or Syria—the native Pleistocene habitat of wild large-grained cereal grasses—with zero strict hits anywhere else on Earth.
dek: Thousands of lake and bog mud cores were collected to track Ice Age climate. Do any layers older than 12,000 years preserve crop pollen, field weeds, and forest clearance from an unknown Ice Age farming culture?
updated: 2026-11-24
---

{{figure: ice-age-farming/tiles}}

## The idea

Fossil pollen in lake and bog sediment is a natural side channel: scientists cored thousands of lakes to reconstruct Ice Age temperature and forest cover, not to look for lost civilisations. Yet when Neolithic farmers later arrived in Europe, they left an unmistakable botanical footprint in those same cores—cereal-type pollen rising together with agricultural field weeds (*Plantago lanceolata*, *Rumex*, *Urtica*, *Centaurea cyanus*) and falling tree cover.

Because harmonized global pollen syntheses like `LegacyPollen 2.0` lump `Cerealia`, `Triticum`, `Hordeum`, and `Secale` into family-level `Poaceae`, we queried **un-lumped fossil pollen counts and chronologies** directly from the **Neotoma Paleoecology Database v2.0** (`6,948` total pollen datasets; **1,964** reaching `≥ 12,000 cal BP`, **639** reaching `≥ 18,000 cal BP`) across **32 pre-registered crop/cereal taxon IDs**, locking our rules in advance before running the global sweep.

## What we found

**Zero evidence of pre-12,000 BP farming anywhere in the global Neotoma archive.**

First, the calibration check shows the detector works on real agriculture. Across 100 European and Mediterranean Holocene cores (`8,500–2,000 cal BP`), `FARM_RELAXED` fires in **59.0%** of cores vs. **2.5%** (`1/40`) in pre-Neolithic Mesolithic northern/central Europe (`11,500–9,000 cal BP`, `p < 10⁻¹¹`). `FARM_STRICT` is more conservative (`23.0%` Holocene recall, `0.0%` Mesolithic false positives), yet its 23 detected onsets cleanly trace the real **southeast-to-northwest Neolithic wave of advance** from Anatolia and the Balkans (`7,000–8,000 BP`) into northern Europe (onset age vs. latitude Spearman `ρ = −0.59, p = 0.0029`; vs. longitude `ρ = +0.57, p = 0.0046`).

Second, across all **1,964** global cores reaching `≥ 12,000 cal BP`, Late Glacial layers (`12,000–18,000 cal BP`) trigger **less often** than the deep Last Glacial Maximum / MIS 3 negative control (`18,000–50,000 cal BP`):

- **Chronology-verified `FARM_STRICT`:** **`2 / 1,964` (`0.10%`)** in `12–18 ka` vs. **`2 / 639` (`0.31%`)** in `18–50 ka` (one-sided Fisher `p = 0.95`).
- **Sensitive `FARM_RELAXED`:** **`47 / 1,964` (`2.39%`)** in `12–18 ka` vs. **`18 / 639` (`2.82%`)** in `18–50 ka` (`p = 0.77`).

{{figure: ice-age-farming/calibration_and_sweep}}

## Why four Mediterranean cores still triggered the strict rule

Every single chronology-verified pre-12,000 BP `FARM_STRICT` hit (`4/4` verified; `6/6` unfiltered) sits inside one narrow ecological belt—**Italy, Turkey, and Syria (`35.7°–43.0° N, 10.9°–42.8° E`)**, the exact native Ice Age range of wild large-grained grasses (*Triticum boeoticum*, *Hordeum spontaneum*, *Secale montanum*, *Aegilops*, wetland *Glyceria*) and native open-steppe *Rumex* and *Plantago*:

- **Lago Grande di Monticchio (`DS 26608`, Southern Italy, `22.5 ka`):** varve-dated deep Last Glacial Maximum crater lake (`1,393` age controls) triggering the exact same `Cerealia-type + Plantago + Rumex` package 10,000 years before the Ice Age ended.
- **Ghab (`DS 4065`, Syria, `36.6 ka`):** MIS 3 Levantine valley core confirming continuous wild-cereal pollen rain tens of millennia before domestication.
- **Lake Van (`DS 45165`, Eastern Anatolia, `14.3–13.9 ka`):** `Poaceae (Cerealia)` runs unbroken in 100% of samples from `19,560 BP` straight through the Holocene in the heart of wild einkorn/barley territory.
- **Lago dell'Accesa (`DS 22978`, Tuscany, `14.8 ka`):** `Poaceae (Cerealia)` tracks open Ice Age steppe (`16,964–9,859 BP`) alongside abundant wild `Poaceae` and then **vanishes to zero at `9,715 BP`** when Holocene forest closes—the opposite of farming.

{{figure: ice-age-farming/global_pre12ka_map}}

Outside that Mediterranean/Anatolian wild-cereal belt—across Northern/Western Europe, the Americas, Asia, Africa, and Oceania—**zero cores** pass `FARM_STRICT` before 12,000 BP. Even the handful of pre-12 ka `Zea mays` occurrences in Neotoma (`15` records) fail both rules and are dominated by a clear morphotype-coding artifact in South Africa (`Braamhoek`, `16,350–12,235 BP`, centuries millennia before New World maize reached Africa).

## What this does not settle

- **Drowned coastal plains and under-sampled tropics.** Neotoma is densest in Europe and North America; Amazonia, South Asia, tropical Africa, and submerged Ice Age continental shelves are thinly sampled.
- **Small-scale wild-cereal tending.** Light-microscope pollen cannot distinguish wild *Triticum*/*Hordeum* stands from tiny Epipaleolithic foraging plots inside the Fertile Crescent; this test rules out widespread landscape-altering Ice Age agriculture across sampled continental basins.
- **Independent replication.** Code and Neotoma snapshot hashes are reproducible with zero amendments; second-vendor replication is pending.

Read the full pre-registered [protocol](https://github.com/ejhong/aletheia-lab/blob/main/questions/ice-age-farming/protocol.md) and [results](https://github.com/ejhong/aletheia-lab/blob/main/questions/ice-age-farming/RESULTS.md).
