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

## 2026-11-23 — Lock, full 9-target dipole-mode run, physics audits, and write-up

- Committed pre-lock protocol, manifest, solver, and passing unit tests (`14e0738`) and locked `protocol.md` in its own commit (`1936be2`, `sha256: 750113e2a758`) before running any ligand-bound protein calculations. Zero amendments required.
- Executed `analysis/terahertz_modes.py` across all 9 targets (`1JFF`, `4I4T`, `GABA_A 6X3T`, `GLIC 3P4W`, `Albumin 1E7B`, `Luciferase 1BA3`, `Lysozyme 1DPX`, `Ubiquitin 1UBQ`, and `1JFF_shuffled`) × `35` volatile compounds × `Model A` (`Vina` + `Vinardo` + Table S1 calibrated), `Model A_phys`, and rotationally invariant `Model B` (`3N × 3N`), plus `20`-rotation `SO(3)` invariance audit (`449.5 s` total).
- Pre-registered verdict: **`level_repulsion_artifact_not_tubulin_specific`**:
  - Craddock's 8-vs-2 sign split reproduces on `1JFF` (`7/8` down, `2/2` up, `AUC = 0.938`), **and identically on `Lysozyme 1DPX` (`7/8, 2/2, AUC = 0.938`) and `1JFF_shuffled` (`7/8, 2/2, AUC = 0.875`)**.
  - Pure two-oscillator level repulsion (`sign(f_iso − 613 THz)`) explains `303 / 315` (`96.2%`) of all protein–gas pairs (`100%` on `4I4T`, `GLIC`, `Lysozyme`, `Ubiquitin`, `1JFF_shuffled`).
  - On the expanded `27`-vs-`7` panel, `1JFF` collapses to `ρ = −0.080` (`p = 0.705`), `AUC = 0.698` (`p = 0.115`), tied identically with `1JFF_shuffled` (`ΔAUC = 0.000`, 95% CI `[−0.132, +0.127]`).
  - `SO(3)` audit exposed broken rotational symmetry in the published Kurian–Craddock diagonal-only model: rotating `1JFF + TFMB` rigidly in empty space flips its `613 THz` shift sign (`−3,703` to `+2,722 GHz`), whereas `Model B` drifts by `1 × 10⁻⁹ GHz` and still shows no tubulin potency tracking (`ρ = −0.120`).
- Generated 5 interactive site figures (`site/figures/anaesthetics-terahertz/{tiles,verdict,repulsion,proteins,spectrum}.html`), verified all embedded JS with `node --check`, wrote `RESULTS.md`, `site/content/anaesthetics-terahertz.md`, and updated `site/topics/minds-and-machines.md`.
