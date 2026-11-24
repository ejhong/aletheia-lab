# Spot-check of the NEEM fire-spike study (#114)

An outside check by Claude Opus 5.5 (Anthropic), 2026-11-24, directed by Eugene. It is not part of the locked protocol and is not new evidence.

- `spotcheck.py` reuses the study's locked code (`../analysis/neem_spikes.py`) and prints the checks behind the spot-check numbers: the running-median denominator, swapping plumes between baselines, absolute plume thresholds with a 95% interval, the flux control with mean versus median layer thickness, layer thickness and samples per year, spike widths, sensitivity to the onset date, and the Pillar 2 stadials.
- `output.txt` is what it printed on the MANIFEST data. The SHA-256 of all three files matched `../MANIFEST.md`.
- Data are not in git. Download the three PANGAEA files listed in `../MANIFEST.md` into `../data/`, or pass another folder as the first argument.
- Run it from the repo root: `.venv/bin/python -I questions/yd-neem-spikes/spotcheck/spotcheck.py [DATA_DIR]`. It writes no files.
- Rerunning the study's own pipeline from the same data reproduced `../results/` byte for byte.
- Main point: the >5x drop comes from the baseline. The running median it divides by rose 4.0×, and swapping plumes between baselines accounts for all of the drop. The absolute counts (>30 to >100 µg/kg) lean slightly upward, with none significant.
