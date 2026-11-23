# Log

- **2026-11-23:** Opened Issue #75 and created branch `q/yd-cooling-shape` at Eugene's request to test whether the Younger Dryas (`GS-1`) cooling transition itself is physically distinct from the other ~20–24 abrupt stadial coolings of the last ice age across Greenland (`δ¹⁸O`, surface temperature, `Ca²⁺` dust) and Antarctica (7-core temperature reconstruction).
- **2026-11-23:** Downloaded all five primary public files (NOAA WDS Paleoclimatology and PANGAEA) into git-ignored `data/`, verified SHA-256 hashes in `MANIFEST.md`, and ran blind schema/span check (`explore/structure.py`) with zero Younger Dryas values viewed.
- **2026-11-23:** Wrote `protocol.md`, `analysis/shape.py`, and `analysis/test_shape.py`. All 5 unit tests passed (`0.002s`). Ran `python3 analysis/shape.py --decoy` (excluding `GS-1`, scoring decoy `GS-5.2`; pools `18`, `24`, `9` excluding `GS-1`). Freezing and locking `protocol.md` before viewing `GS-1`.
