# Spot-check of yd-cosmic-dust-he3 (#121)

An independent check of the merged study, done on 2026-11-24 by Claude Opus 5.5 (Anthropic) at Eugene's request. It
re-parses the raw sources itself instead of trusting the study's parsers. This is a spot-check, not a full replication.

- `spotcheck_he3.py` recomputes every spot-check number: data hashes, an independent parse of all 181 Pacific rows
  (0 mismatches), dropped and duplicated rows, samples per window, sedimentation rates and smoothing times, the
  13.5–11.5 ka window with and without the Cocos Ridge samples, the SO202-07-6 radiocarbon count, the unit factor at
  `analysis/cosmic_dust_he3.py` line 371, the blind top-18 scan, core medians against Brook's ice values, and the Late
  Eocene diagnostic. The script's top comment lists what each section does.
- `output.txt` is what the script prints.
- Data: the nine files in `../MANIFEST.md`, under their manifest names, in one folder (default `../data/`, which git
  ignores). Run from the repo root:
  `.venv/bin/python -I questions/yd-cosmic-dust-he3/spotcheck/spotcheck_he3.py [DATA_DIR] > output.txt`
- Assumptions: the 5 cm and 10 cm mixed-layer depths used for smoothing times are assumed, not measured at these sites.
  Calendar ages for SO202-07-6 are the published ones (CALIB 7.0.4), not recalibrated here.
- Sections 6, 8 and 9 call the study's own functions, so their intervals match its bootstrap and seeds.
