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
