# Lab Log — Does the Taurid comet stream hide a swarm of large fragments? (`taurid-swarm`)

## 2026-11-23 — Data Acquisition, Blind Structural Check, and Pre-Lock Validation

- Opened Issue #103 (`taurid-swarm`, `status:active`) and Issue #104 (`taurid-holocene-cycles`, `status:proposed`); branched `q/taurid-swarm` from `main`.
- Downloaded three live official NASA/JPL archives into git-ignored `data/` and recorded URLs and SHA-256 hashes in `MANIFEST.md`:
  - `data/jpl_neos.json` (`43,374` NEOs; `43,156` NEAs with valid `H`).
  - `data/jpl_encke.json` (Comet `2P/Encke`: `a = 2.218 AU, e = 0.8470, i = 11.34°, ϖ_E = 161.29°`).
  - `data/cneos_fireballs.json` (`1,074` US satellite-detected bolides, `1988-04-15` to `2026-10-04`).
- Ran strictly blind `explore/structure.py`: confirmed continuous full-year CNEOS coverage runs `1994–2025` (`32` complete calendar years, median `33` bolides/yr; pre-1994 sparse 1–2/yr and `2026` truncated Oct 4 before Autumn Taurids). No Taurid `ϖ`, `7:2` resonance, or seasonal/swarm-year fireball rates were inspected.
- Drafted pre-registered `protocol.md` fixing four tests across both archives (`A1`: Napier 2010 box `ϖ` alignment above uniform AND above adjacent Jupiter secular control `Ctrl_LowE`; `A2`: 7:2 Jupiter resonance `2.21–2.30 AU` excess; `B1`: CNEOS calendar seasonality in Autumn Taurids `Oct 15–Nov 30` and Daytime β-Taurids `Jun 10–Jul 10`; `B2`: 6 published 7:2 swarm return years `1998, 2005, 2015, 2018, 2022, 2025` vs. 26 non-swarm years using drift-immune within-year Autumn shares).
- Ran `analysis/test_taurid.py`: ALL TESTS PASSED (circular V-test calibration FPR `0.065`, power `40/40`, secular control cleanly rejects shared bias `p_ctrl = 0.221`, calendar exact `47d/31d`, B2 detects injected swarm surge `p = 0.0001`).
- Ran `analysis/taurid.py --decoy`: clean end-to-end execution on randomized angles and dates (`0/4` passed).
- Ready to commit pre-lock files, lock `protocol.lock` in its own commit, push to GitHub, and run locked analysis.

## 2026-11-23 — Locked Analysis Run

- Committed pre-lock files (`d263665`), locked `protocol.md` (`a526349cbc5c`, commit `23c76b3`), pushed `origin q/taurid-swarm`, verified `scripts/check.py`, and paused 2 seconds.
- Executed locked `python3 questions/taurid-swarm/analysis/taurid.py`:
  - **Test A1 (`H < 18.0`, Primary):** `N = 64` in Napier box, `c_bar = −0.001` (`p_unif = 0.5036`), `f_45 = 31.2%`, vs. `Ctrl_HighI` `p = 0.3727` → **Not met**. Remarkably, Napier's `H < 16.5` anomaly (`N = 17, c_bar = +0.557, p_unif = 0.0005`) collapses completely once 1 km (`H < 18`) or 400 m (`H < 20, c_bar = −0.068, f_45 = 21.7%`) NEAs are added — a stark size inversion opposite a cometary fragmentation cascade! Meanwhile `Ctrl_LowE` (`c_bar = −0.324`) strongly aligns with Jupiter's perihelion (`14.7°`).
  - **Test A2 (`H < 20.0`, 7:2 resonance `2.21–2.30 AU`):** `13/72` (`18.1%`) vs. `11.2%` anti-Taurid (`1.61×, p = 0.0954`) and `15.1%` `Ctrl_LowE` (`p = 0.3024`) → **Not met**. Only `3` NEAs at `H < 18` (2 of which are bright stony asteroids `Morpheus` albedo `0.37` and `Jason` albedo `0.21`) and `6` tight Encke-like NEAs at `H < 20` (`2004 TG10`, `2010 LU108`, `2018 TY2`, `2018 UN1`, `2008 ON13`, `6063 Jason`). Sensitivity tier `H < 22.0` shows a modest excess (`36/174 = 20.7%` vs. `11.7%` anti, `p = 0.0025`, `p_ctrl = 0.051`).
  - **Test B1 (CNEOS seasonality, `1994–2025`, `N = 1,045`):** Autumn Taurids `133` vs. `134.5` expected (`0.99×, p = 0.5678`), `≥ 1 kt` `12` vs. `14.8` (`p = 0.8196`); Daytime β-Taurids `81` vs. `88.7` (`0.91×, p = 0.8178`) → **Not met**.
  - **Test B2 (6 swarm years vs. 26 non-swarm years):** Within-year Autumn share `12.70%` vs. `12.96%` (`p = 0.5201`), `≥ 1 kt` `0.33` vs. `0.38/yr` (`p = 0.6876`) → **Not met**.
  - **Joint verdict:** `no_macro_swarm_detected` (`0 of 4` passed).
- Wrote `RESULTS.md`. Next: build interactive Solar System Orrery, Perihelion Rose, and Satellite Airburst figures (`analysis/make_figures.py`) and site page (`site/content/taurid-swarm.md`).

## 2026-11-23: Figures restyled

- Restyled the orrery, rose and airburst figures, tiles and verdict panel (`analysis/make_figures.py`, `site/figures/taurid-swarm/`) to the site's type, palette and plain wording, matching the ancient-sky-hole figures; no number changed. Regenerated from a fresh NASA/JPL download: the fireball and Encke files matched the manifest hashes, and the NEO file differed but gave the same 331 orbits with identical values.
