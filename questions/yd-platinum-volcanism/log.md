# Log

- **2026-11-23:** Opened Issue #76 and created branch `q/yd-platinum-volcanism` at Eugene's request to test (1) whether the GISP2 platinum anomaly (Petaev et al. 2013, `1712.375–1712.000 m`) precedes or follows the Younger Dryas cooling onset inside GISP2 itself and on the synchronized `GICC05` timescale, and (2) how unusual Greenland/bipolar volcanism around the Younger Dryas onset is across 51,000 years (`60–9 ka`, Lin et al. 2022).
- **2026-11-23:** Downloaded all 7 primary datasets (NOAA, Copernicus CC-BY, PANGAEA CC-BY) into git-ignored `data/`, recorded SHA-256 hashes in `MANIFEST.md`, and inspected schemas blindly without viewing target interval values.
- **2026-11-23:** Wrote `protocol.md`, `analysis/ptvolc.py`, and `analysis/test_ptvolc.py`. All 6 unit tests passed (`0.057s`). Ran `python3 analysis/ptvolc.py --decoy` (excluding `[12,600, 13,200]` b2k and GISP2 `[1705, 1720] m`). Freezing and locking `protocol.md` before viewing target interval.
