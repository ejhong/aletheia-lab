# Work Log — `anaesthetics-microtubules` (Issue #48)

## 2026-11-23 — Pre-lock setup, primary source extraction, and crystallographic redocking validation

- Branched `q/anaesthetics-microtubules` cleanly from `origin/main` (`2d13ede`).
- Installed version-pinned open docking stack on Ubuntu 24.04:
  - `AutoDock Vina v1.2.5` (`autodock-vina 1.2.5-2build1`)
  - `Open Babel 3.1.1` (`openbabel 3.1.1+dfsg-9ubuntu5`)
- Read primary open-access sources in full text:
  - **Craddock et al. (2012, *PLoS ONE* 7:e37251, `PMC3382613`):** Extracted exact residue lists (Tables 2 & 3) for all 8 persistent (>70%) single-dimer tubulin pockets (`sites 1, 4, 5, 7, 21, 23, 37, 38`).
  - **Craddock et al. (2017, *Sci. Rep.* 7:9877, `PMC5575257` + Supplementary `41598_2017_9992_MOESM1_ESM.doc`):** Verified Table S1 (8 clinical volatile anaesthetics, 2 non-anaesthetics `F6` and `TFMB` = 1,3,5-tris(trifluoromethyl)benzene, 1 convulsant `flurothyl`) and Table S2 MOE docking scores.
  - **Fang et al. (1996, *Anesth. Analg.* 83:1097–1104):** Read full PDF (Tables 1–5) to obtain experimentally measured rat `MAC` and 37°C olive-oil/gas partition coefficients (`λ_oil`) for 18 aromatic/cycloalkane volatile anaesthetics plus 2 non-immobilizers (`TFMB`, `cyclooctane`).
  - **Koblin et al. (1994, *Anesth. Analg.* 79:1043–1048 [PubMed 7978424]) & Steffey et al. (1998, *Anesth. Analg.* 86:145–150):** Verified non-immobilizer classification and `λ_oil` values for `F6` (`43.5`), `F8` (`25`), `perfluoropentane` (`0.662`), `perfluorocyclobutane`, and `CF3CClFCF3`.
- Downloaded 8 public RCSB PDB structures (`1JFF`, `4I4T`, `6X3T`, `3P4W`, `1E7B`, `1BA3`, `1DPX`, `1UBQ`), verified 100% presence of all Craddock tubulin residues on both `1JFF` and `4I4T`, and verified PubChem CIDs & canonical SMILES for all 35 panel compounds + 2 redocking controls.
- Ran blind crystallographic self-redocking check on the 4 co-crystallized native ligands (`desflurane → 3P4W`: `0.30/0.67 Å`; `propofol → 6X3T`: `0.72/0.28 Å`; `bromoform → 1BA3`: `0.38/0.76 Å`; `halothane → 1E7B`: `1.22/1.31 Å` under `vina`/`vinardo`). No test-panel dockings or potency/separation analyses were run prior to locking.
- Wrote `protocol.md`, `MANIFEST.md`, `analysis/dock_anaesthetics.py`, and `analysis/test_docking.py`.

## 2026-11-23 — Lock, pre-results Amendment 1, full 1,680-docking run, and write-up

- Committed pre-lock files (`93d690c`) and locked `protocol.md` via `python3 scripts/lock.py questions/anaesthetics-microtubules` in its own commit (`4a6b0ed`, `sha256: 9d2201031fe2c6685bd257bf51b46e68d3d44d2959e56499d86a811e5bacb7c2`).
- Cancelled the initial `exhaustiveness = 16` run during pocket 1 without inspecting any outputs, deleted `data/dock_work/out/`, verified `≤ 0.011 kcal/mol` convergence on pre-lock crystallographic positive controls (`1E7B+halothane`: `0.000 kcal/mol`; `3P4W+desflurane`: `0.011 kcal/mol`), and committed **Amendment 1** (`fbc8a25`, `exhaustiveness = 16 → 4`) before running the test panel.
- Added resumable per-pocket caching and exact NumPy vectorization of the permutation/bootstrap routines to `analysis/dock_anaesthetics.py` (all unit and synthetic checks in `analysis/test_docking.py` pass).
- Completed all `24 pockets × 35 molecules × 2 scoring functions = 1,680` dockings cleanly (`results/affinities.tsv`, `results/summary.json`, `results/poses_3d.json`).
- Pre-registered verdict: **`no_potency_or_selectivity`** (`1JFF` `Vina` `ρ = +0.285`, `p = 0.146`, `AUC = 0.212`, `p = 0.017`; `4I4T` `ρ = +0.347`, `p = 0.074`, `AUC = 0.079`; `1JFF` `Vinardo` `ρ = +0.284`, `AUC = 0.455`; negative-control `Ubiquitin` hits `ρ = +0.512` Vina / `+0.596` Vinardo, `AUC = 0.794` Vinardo).
- Generated 5 interactive site figures (`site/figures/anaesthetics-microtubules/{tiles,verdict,potency,matrix,pockets}.html`), verified all embedded JS with `node --check`, wrote `RESULTS.md`, `site/content/anaesthetics-microtubules.md`, and updated `site/topics/minds-and-machines.md`.
- 2026-11-23 (Claude, review): the tiles and the verdict panel were reworded in plain language, with the reading changed from "no tubulin signal" to "the method cannot tell an anaesthetic target from any other protein", and the proteins given plain names in the figures. The generator now stops if the results cease to support that wording. No number changed. A fuller plain-language pass on the three interactive figures was begun by a subagent and stopped partway by a safety classifier; their axis and button labels are as the original author wrote them.
