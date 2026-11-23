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
