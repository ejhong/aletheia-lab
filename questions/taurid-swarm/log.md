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
