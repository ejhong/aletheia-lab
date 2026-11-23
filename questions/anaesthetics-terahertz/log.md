# Work Log — `anaesthetics-terahertz` (Issue #115)

## 2026-11-23 — Pre-lock primary-source extraction, equation verification, and polarizability calibration

- Created branch `q/anaesthetics-terahertz` cleanly from `origin/main` (`d5c5340`, after PR #111 and #112 merged).
- Extracted exact Hamiltonian equations verbatim from open-access primary XML/LaTeX sources:
  - Craddock et al. (2017, *Sci. Rep.* 7:9877, `PMC5575257`) Eqs. (1)–(4) + Supplementary Table S1 (`41598_2017_9992_MOESM1_ESM.doc`).
  - Kurian et al. (2018, *Phys. Lett. A* 382:33–43, `PMC5796540` / `arXiv:1608.08097` LaTeX source & Figure 4) Eqs. (3)–(7) and Tables III & IV (`Trp`, `Tyr`, `Phe` polarizability tensors and ring axes).
- Verified unperturbed baseline `1JFF` tubulin spectrum (`81` aromatic residues) with zero free parameters: `468.0–695.5 THz` (`n_neg = 0`, 16 normal modes inside `613 ± 8 THz`), matching Craddock et al. (2017)'s published `480–700 THz` range.
- Benchmarked polarizability tensor methods on Craddock Table S1's 11 reference gases (`CAM-B3LYP/PolX`):
  - `PySCF` finite-field DFT and analytical `CPHF/def2-SVPD` proved too slow on 2 CPUs (`~206 s` on `F6` alone).
  - Exact Thole (1981) / van Duijnen & Swart (1998, Table 5 exponential damping `a = 2.089`) interacting-dipole tensor model matched all 11 Craddock Table S1 DFT values with Pearson `r = 0.9937`, Spearman `ρ = 0.9182`, mean `|rel error| = 3.78%` in milliseconds, with zero free parameters.
- Zero ligand-bound protein calculations or cross-protein comparisons were run before writing and locking `protocol.md`.
