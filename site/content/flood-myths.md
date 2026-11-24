---
summary: Global test of 927 oral traditions against Ice Age seafloor maps; flood myths are no more common where wide continental shelves drowned.
verdict: Not found — no global cluster where land drowned
result: Across 396 coastal cultures in Berezkin's catalog, non-biblical flood myths are just as common beside steep, narrow coastlines (36%) as beside the widest drowned Ice Age shelves (34%), and slightly more common inland (39%). On the same data and model, earthquake myths track seismic zones strongly (p = 0.0005), while drowned-shelf area shows no link to flood stories (p = 0.85).
dek: Do worldwide Great Flood stories preserve a collective memory of coastal plains swallowed by rising Ice Age seas, or are they just as common where almost no land was lost?
updated: 2026-11-24
---

{{figure: flood-myths/tiles}}

## The question

At the peak of the last Ice Age, roughly 20,000 years ago, sea level stood about 120 metres lower than today. As the ice sheets melted between 20,000 and 7,000 years ago, vast coastal plains—Doggerland under the North Sea, Sundaland across Southeast Asia, the Sahul shelf around Australia, and Beringia between Asia and Alaska—went underwater.

Because Great Flood myths appear in hundreds of cultures around the world, a long-running hypothesis holds that they preserve a shared ancestral memory of post-glacial drowning. That idea makes a testable geographical prediction: **coastal peoples living beside wide submerged continental shelves should preserve non-biblical flood myths at higher rates than coastal peoples living beside steep, narrow coastlines where almost no land disappeared.**

We locked that test in advance using two open datasets: **Yuri Berezkin's global folklore catalog** (as archived by Michalopoulos & Xue 2021, covering 927 societies with full covariates and 2,564 motifs across 94 language families) and **NOAA's ETOPO 2022 global seafloor elevation model**. To avoid missionary contamination, our primary outcome counts **17 non-biblical flood and deluge motifs** while strictly excluding Noah's Ark and the Genesis dove/raven scout motifs, alongside Michalopoulos & Xue's external `flood_related` index and a strictly Noah-free coastal subsample (`n = 340`).

## What we found

**There is no global signal.** Non-biblical flood stories appear in **37.9%** of all societies worldwide, and are slightly *less* common within 150 km of the coast (**35.9%**, `n = 396`) than inland (**39.4%**, `n = 531`).

Dividing the 396 coastal societies into four equal quartiles by how much continental shelf (`−120 m` to `0 m`) drowned within 250 km gives a completely flat line: **36.4%** on the narrowest shelves (`Q1`), **37.4%** (`Q2`), **35.4%** (`Q3`), and **34.3%** on the widest drowned shelves (`Q4`).

{{figure: flood-myths/coastal_quartiles_and_models}}

Controlling for ethnographic sampling effort, distance to coast and rivers, seismic exposure, climate, latitude, and shared linguistic ancestry across 58 coastal language families (**Model M4**, our pre-registered primary test), drowned shelf area has an estimated effect of **`−0.010 SD`** (`p = 0.87` clustered by language family; `p = 0.85` with 1,000 km Conley spatial-HAC standard errors; `p = 0.85` by within-continent permutation). Removing every society with Noah motifs gives **`−0.015 SD`** (`p = 0.79`). Switching to the final Holocene drowning window (`−60 m`, 12–7 ka) or a 500 km radius gives the same null (`−0.017 SD`, `p = 0.71`; `−0.083 SD`, `p = 0.22`).

Crucially, **the catalog is sensitive enough to catch real geological memory**: on the exact same societies and language-family model, **earthquake myths** track seismic proximity strongly (**`+0.157 SD`**, `p = 0.0005` Conley 1,000 km), **sea myths** track coastal proximity (`+0.087 SD`), and our negative control (**fire myths** vs. drowned shelf) is null (`−0.070 SD`, `p = 0.23`).

## Where flood myths actually sit

{{figure: flood-myths/world_map}}

Looking continent by continent, no macro-region shows a statistically significant positive link between drowned shelf area and flood myths (`p ≥ 0.066` in Asia, `0.33` in North America, `0.38` in South America; negative tilts in Africa, Europe, and Oceania). In fact, when exposure is measured as the *shallow-shelf fraction* of nearby ocean, the relationship turns **significantly negative** (`−0.16 SD`, `p = 0.019` on non-biblical flood share; `p = 0.0048` on `flood_related`)—likely because steep, deep-water subduction coastlines around the Pacific Rim have narrow shelves but frequent tsunamis and coastal quakes.

## What this does not settle

- **Local named-bay memories vs. world-ending myths.** Nunn & Reid (2016) documented 21 Aboriginal Australian stories describing specific islands, bays, and channels going underwater during Holocene sea-level rise. Berezkin's catalog indexes broad universal-deluge motifs (and codes only 16 coastal Australian groups, with 18.8% deluge prevalence). A global null on Great Flood myths does not rule out site-specific coastal memories among long-resident peoples.
- **Holocene migrations.** Modern ethnographic locations do not always match where a group's ancestors lived 12,000 years ago—though that mobility is itself a major reason why global myth distributions fail to preserve Ice Age shorelines.
- **Rebound in formerly glaciated regions.** Global −120 m bathymetry approximates average sea-level rise and does not adjust for post-glacial crustal rebound at high latitudes; restricting to ice-free tropical and mid-latitude shelves yields the same null.
- **Independent replication.** The analysis is fully reproducible from open data with zero amendments, but has not yet been replicated independently by a second AI vendor's agent.

Read the full pre-registered [protocol](https://github.com/ejhong/aletheia-lab/blob/main/questions/flood-myths/protocol.md) and [results table](https://github.com/ejhong/aletheia-lab/blob/main/questions/flood-myths/RESULTS.md).
