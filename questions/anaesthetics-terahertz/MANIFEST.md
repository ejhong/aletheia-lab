# Data Manifest — `anaesthetics-terahertz` (Issue #115)

All input structures, molecular parameters, and docked 3D poses come from open public archives and the locked `#48` (`anaesthetics-microtubules`) pipeline. No proprietary datasets or paid APIs are used.

## 1. Protein Structures (RCSB Protein Data Bank, CC0 / Public Domain)

Downloaded `2026-11-23` from `https://files.rcsb.org/download/<PDB>.pdb` (stored git-ignored under `questions/anaesthetics-microtubules/data/pdb/` and re-downloadable directly by `analysis/terahertz_modes.py`):

| PDB ID | Protein | Role | Chains | Aromatics (`Trp/Tyr/Phe`) | Resolution | SHA-256 |
|---|---|---|---|---:|---:|---|
| `1JFF` | Bovine αβ-tubulin | Primary Orch OR target | `A, B` | `81` (`8 / 34 / 39`) | `3.50 Å` | `8fcc2ee63f39ee86e7854128e9b2251bedc78e4cc552ab6ac6180c3a0b9e6798` |
| `4I4T` | Bovine αβ-tubulin (high-res) | High-res replication | `A, B` | `83` (`8 / 33 / 42`) | `1.80 Å` | `b9ddfc0829b183e5b09b5ff0ff3a6a0deced432109e9104ee631140abee4b964` |
| `6X3T` | Human α1β2γ2 `GABA_A` receptor | Rival ion channel | `A–E` | `234` (`35 / 94 / 105`) | `2.55 Å` | `a28d55a230662ffb08a4207b8f82f511409017ea888480bbb9bbb75465c9ac19` |
| `3P4W` | *Gloeobacter* `GLIC` channel | Rival ion channel | `A–E` | `215` (`25 / 75 / 115`) | `3.15 Å` | `945f25ee0f220bbecaa924178b9503f8b0f2432b7250d27f58c77199f99024b0` |
| `1E7B` | Human Serum Albumin | Non-conscious soluble control | `A` | `50` (`1 / 18 / 31`) | `2.38 Å` | `4cea6a1ab2bf589e4311906c6837170d1fa2307b2933ee8b683b00737b0d8565` |
| `1BA3` | Firefly Luciferase | Non-conscious soluble control | `A` | `51` (`2 / 19 / 30`) | `2.20 Å` | `a304920ee2ad14ce94511d5ce711d5ffb07b5d37ab6fd1bfa2b76bfb75e7f1de` |
| `1DPX` | Hen Egg-White Lysozyme | Negative globular control | `A` | `12` (`6 / 3 / 3`) | `1.65 Å` | `00582ec39810fe609df85ae65a3c7a61af3b9b39a0472a72caf194918a5c7ef3` |
| `1UBQ` | Human Ubiquitin | Minimal negative control | `A` | `3` (`0 / 1 / 2`) | `1.80 Å` | `d4a6812d8951cf6594e6a0763f089e35f5a80b62acb3c117b2c5565228a7b161` |

## 2. Compound Panel & Locked Docked Poses (from Issue #48)

- **Metadata & pharmacological values (`n = 35` volatile compounds):** Loaded directly from the locked `#48` output `questions/anaesthetics-microtubules/results/summary.json` (`sha256: f0fffcec0569bf65effaf088e50cb19f76f3153f07a81ce00f33f838feeda635`, primary sources: Craddock et al. 2017 Table S1, Fang et al. 1996 Tables 1–5, Koblin et al. 1994, Steffey et al. 1998, PubChem).
  - `27` true volatile anaesthetics (`9` clinical human MAC + `18` Fang 1996 rat MAC aromatics/cycloalkanes)
  - `7` confirmed Meyer–Overton non-immobilizers (`F6`, `F8`, `TFMB`, `cyclooctane`, `perfluoropentane`, `perfluorocyclobutane`, `2-chloroheptafluoropropane`)
  - `1` annotated convulsant (`flurothyl`)
- **Docked 3D poses (`24 pockets × 35 ligands × 2 scoring functions`):** Deterministic top-ranked (`MODEL 1`) docked geometries from `questions/anaesthetics-microtubules/analysis/dock_anaesthetics.py` (`AutoDock Vina v1.2.5`, `Open Babel 3.1.1`, seed `20261123`), reproducible from scratch using `#48`'s script.

## 3. Primary Physics Parameters & Equations

- **Collective dipole Hamiltonian & aromatic amino-acid polarizability tensors:**
  - Craddock, T. J. A., Kurian, P., Preto, J., Sahu, K., Hameroff, S. R., Klobukowski, M., & Tuszynski, J. A. (2017). *Anesthetic alterations of collective terahertz oscillations in tubulin correlate with clinical potency.* **Scientific Reports** 7:9877 (`PMC5575257`, CC-BY-4.0), Methods Eqs. (1)–(4) and Supplementary Table S1 (`41598_2017_9992_MOESM1_ESM.doc`).
  - Kurian, P., Capolupo, A., Craddock, T. J. A., & Vitiello, G. (2018). *Water-mediated correlations in DNA–enzyme interactions.* **Physics Letters A** 382:33–43 (`PMC5796540`, `arXiv:1608.08097`), Eqs. (3)–(7), Fig. 4, Tables III & IV (`Trp: 119.5, 91.6, 29.4`; `Tyr: 89.5, 43.0, 82.9`; `Phe: 79.0, 79.0, 38.6` a.u., where `1 a.u. = 1.64878 × 10⁻⁴¹ C² m² J⁻¹`).
- **Molecular 3×3 anisotropic polarizability tensors for volatile gases:**
  - Thole (1981, *Chem. Phys.* 59:341) / van Duijnen & Swart (1998, *J. Phys. Chem. A* 102:2399–2406, Table 5 exponential damping `a = 2.089`, atomic polarizabilities in `Bohr³`: `H = 2.7927`, `C = 8.6959`, `N = 6.5406`, `O = 5.7494`, `F = 3.0013`, `Cl = 16.1979`, `Br = 23.5714`). Pre-lock calibration against all 11 Craddock (2017) Table S1 `CAM-B3LYP/PolX` DFT values gives `r = 0.9937`, `ρ = 0.9182`, mean `|rel error| = 3.78%`.
  - Exact Craddock (2017) Table S1 DFT mean polarizability values (`Å³`) are also retained verbatim for an exact Table S1 sensitivity check on the 11 overlapping gases.

## 4. Pinned Software Versions

- Python `3.12.16`, `NumPy 2.3.5`, `SciPy 1.18.1`, `Open Babel 3.1.1`.
