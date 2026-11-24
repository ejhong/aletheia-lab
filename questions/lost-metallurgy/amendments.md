# Amendments — Pre-Bronze-Age Metallurgy Side-Channel (#82)

## Amendment 1 (2026-11-24, before executing analysis)

- **What changed:** Upon loading `legrand2024-id3_1-lead.txt` (Dome du Goûter, French Alps) against `legrand2024-id1_1-age.txt`, the archived lead sub-file spans depths `21.197–22.999 m` (`599 BCE to 766 CE`, i.e., `2,549–1,184 yr BP`), whereas the full `9,751 BP` depth range is only in the major-ion/dust file `legrand2024-id2-avg-chem.txt`. Consequently, `ddg_alps_lead.txt` contains zero samples older than `5,000 BP` and cannot compute a pre-5,000 BP empirical baseline or pre-5 ka upper bound.
- **How handled:** Dome du Goûter (`2,549–1,184 BP`) is retained as an independent **European Alpine Roman/Iron-Age positive-control benchmark** normalized to upper continental crust `(Pb/Ce)_UCC = 19/83 = 0.2289` (McConnell et al. 2018; Rudnick & Gao 2003). All pre-5,000 BP tests, cross-archive anomaly checks, and physical upper bounds are computed unmodified from the five remaining archives spanning `47,371–5,000 BP` (`RECAP`, `GISP2`, `EPICA Dome C`, `Füramoos`, and `Store Mosse`). No thresholds, binning windows, or verdict rules in `protocol.md` were altered.
