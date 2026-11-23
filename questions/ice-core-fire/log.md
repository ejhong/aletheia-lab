# Log: ice-core fire (#43)

## 2026-11-23: start to lock (Claude Fable 5.2)

- Eugene asked for #41 and then #43 to be run end to end overnight. #43 marked active after #41 merged.
- **Data found.** NGRIP and NEEM ammonium at 1 mm and 10 years (Erhardt et al. 2021, PANGAEA, CC-BY); GISP2
  discrete ions (NOAA); GICC05 depth–age for NGRIP (NOAA). The NEEM 1 mm file was downloaded and not used.
- **Sources.** Read: Fischer et al. 2015 (accepted manuscript), Erhardt et al. 2022, Rasmussen et al. 2014
  Table 2, abstracts of Petaev et al. 2013. Not read: Wolbach et al. 2018 (closed access; hosts refused
  automated fetches) and Holliday et al. 2023. The supporters' claim is quoted from a search result and marked
  unverified.
- **Kept blind.** `explore/structure.py` and `explore/crosscheck.py` print nothing from 12,000–14,000 years.
  The decoy run removes the target window.
- **Cross-check.** Ten-year means made from the 1 mm file match the NGRIP 10-year ammonium column (4,245 of 4,245
  rows within 5%) when a row labelled `a` covers `[a, a+10)`.
- **Review.** Two rounds, two vendors (`review/README.md`). The first design was rebuilt.
- **Decoy run.** Works; verdict for the decoy window "not met". Made-up pulses: a one-year pulse of about
  500–1,000 µg/kg·yr is needed to reach the top 1% of windows in the 10-year series.

## 2026-11-23: locked run, replication, write-up (Claude Fable 5.2)

- **Lock:** 2026-11-23T07:50:14Z, commit `f9f6e9f`. Results committed after it.
- **Locked run:** verdict "unusual". The 20-year and 60-year tiers pass at 5% in all three cores (ranks 3 to 7 of
  131 to 323); none passes at 1%. Fine series ordinary.
- **Replication:** OpenAI and Google programs both ran first time and match every window, rank and the verdict.
- **Exploratory, after the result** (`explore/after.py`): the high starts 30 to 40 years after the onset and
  lasts about a century; ammonium is low at the onset itself; late-glacial ice holds several highs of similar
  size.
- **No amendments.**
- **Spent:** $2.74 of $25.
- **Not done:** reading Wolbach et al. 2018 in the original (closed access). Filing with Aletheia.

## 2026-11-23: explanations compared, after the result (Claude Fable 5.2)

- Eugene asked whether the airburst form of the hypothesis fits the ammonium, and how the critics' alternatives
  (volcanism) compare.
- Exploratory (`explore/volcanic.py`): calcium and sulphate beside ammonium. Ammonium rises with the dust in all
  three cores over the century after the abrupt shift. GISP2 has two large sulphate spikes about 50 and 150
  years before the dust rise; sulphate around the onset is not unusual by the window test.
- Read: Melott et al. 2010 abstract (arXiv); Rasmussen et al. 2014 on how the onset is defined. Not read:
  Reinig et al. 2021 (search summary only).
- Added "How the main explanations fit" to `RESULTS.md` and a section and figure to the site page.
