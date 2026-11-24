# Spot check of `yd-platinum-fingerprint` (2026-11-24)

An outside check of this study by Claude (Anthropic), done after its results were published. It led to
Amendment 2 (see `../amendments.md`). These scripts reproduce the numbers in that check. Each one starts with a
comment line saying what it computes and how to run it. Run them from the study folder,
`questions/yd-platinum-fingerprint/`. Scripts that need the raw data take the data folder as their first argument
(default `data/`, filled from `MANIFEST.md`). Each `.txt` file is the saved output of the script of the same name.

| Script | What it shows |
|---|---|
| `kpg_control_rows.py` | Rows of the K–Pg workbook with Ir ≥ 0.1 ppb, and which passed the control filter before the fix. Four were `RSD%` rows of the reference rocks, not samples. |
| `mixing_tally.py` | The locked mixing test (ΔRMSE) counted site by site from `results/summary.json`. At Hall's Cave it favours cosmic over volcanic in 11 of 16 targets (median −0.058). At Page-Ladson every complete sample, background included, is classed `volcanic`. |
| `dilution_test.py` | Adds a small chondrite component to Hall's Cave's own background. The mixing test favours cosmic from +5 ppt Ir. Dilute mixtures are classed `kpg_impact` from about +50 ppt Ir and never `chondrite`, so "0 chondritic" says little on its own. |
| `halls_cave_dropped_rows.py` | Pillar 2 with the 8 Hall's Cave rows that the parser drops (one blank cell each) put back. Among them is the largest Os spike (HC15_07, 13.24 ka). Global extremes inside the window go to 0/8 under both windows (p = 1.0). |
| `carry_white_pond.py` | Copies the first run's White Pond block into the rerun's results. Tesseract 5.5.4 reads one more White Pond row than 5.3.4 did. |
| `_common.py` | Helper that loads `analysis/pt_fingerprint.py`. |

The first run's outputs are kept in `../results/first_run/`.
