# Protocol — Do Anaesthetics Selectively Shift Collective Tryptophan/Aromatic Dipole Modes in Tubulin? (`anaesthetics-terahertz`, Issue #115)

**Lane:** `data`  
**Budget:** `$0.00` (open PDB structures, locked `#48` docked poses, open-source Python/NumPy/SciPy/Open Babel on local CPU).  
**Pre-registration status:** Locked *before* running the collective dipole Hamiltonian on any ligand-bound protein (only the baseline unperturbed `1JFF` spectrum was checked to verify exact reproduction of Craddock et al. 2017's published `480–700 THz` range, and the Thole polarizability model was checked against Craddock Table S1's 11 reference polarizabilities).

---

## 1. Exact Question

In Issue `#48`, standard molecular docking (`AutoDock Vina` and `Vinardo`) showed that microtubule αβ-tubulin neither tracks anaesthetic potency nor rejects fat-soluble non-immobilizers. However, **Craddock et al. (2017, *Sci. Rep.* 7:9877)** did not claim binding affinity alone explains general anaesthesia. Instead, they proposed a **post-binding** mechanism: binding an anaesthetic into tubulin's pockets couples the drug's induced dipole to tubulin's network of aromatic amino acids (`Trp`, `Tyr`, `Phe`), shifting a collective oscillation band near **`613 ± 8 THz`** downward in proportion to clinical potency (`1/MAC`), whereas fat-soluble non-anesthetics (`F6`, `TFMB`) shift that band *upward* instead.

Craddock et al. (2017) explicitly left open whether this effect is unique to tubulin (*"further tests on other candidate sites of anesthetic action ... are warranted to determine if this anesthetic effect is universal or unique to tubulin"*), and they tested only `8` clinical anaesthetics and `2` non-immobilizers (`F6`, `TFMB`).

We test five pre-registered questions using the exact Kurian (2018) / Craddock (2017) coupled-dipole Hamiltonian (`Model A`) and a rotationally invariant full 3D tensor Drude-oscillator Hamiltonian (`Model B`):

1. **Original 8-vs-2 Reproduction:** On `1JFF` tubulin across Craddock's original `8` clinical anaesthetics and `2` non-immobilizers (`F6`, `TFMB`), does the model reproduce a downward shift at `613 ± 8 THz` for clinical anaesthetics (`Δf < 0`), an upward shift for `F6` and `TFMB` (`Δf > 0`), and a strong potency correlation (`R²` / Spearman `ρ`)?
2. **Expanded 35-Compound Generalization:** Does that separation and potency tracking hold across the full `#48` volatile panel (`27` volatile anaesthetics: `9` clinical + `18` Fang 1996 aromatics/cycloalkanes; `7` confirmed Meyer–Overton non-immobilizers including compact low-polarizability `perfluorocyclobutane` and `2-chloroheptafluoropropane` alongside bulky `F6`, `F8`, `TFMB`, `cyclooctane`, `perfluoropentane`; plus convulsant `flurothyl`)?
3. **Polarizability / Level-Repulsion Confound:** In Kurian–Craddock's Drude equation $\bar{\omega} = \sqrt{e^2 / (m_e \bar{\alpha})}$, a molecule's natural frequency falls strictly as $\bar{\alpha}^{-1/2}$. Does the downward-vs-upward sign split at `613 ± 8 THz` simply reflect two-oscillator **level repulsion** (molecules with isolated Drude frequency `f_iso > 613 THz` push the band down; molecules with `f_iso < 613 THz` push it up), and does potency tracking survive controlling for isolated molecular polarizability $\bar{\alpha}$?
4. **Target Specificity Across Eight Proteins + Shuffled Geometry:** Running the exact same Hamiltonian on `1JFF`, high-resolution `4I4T` (`1.80 Å`), rival ion channels (`GABA_A 6X3T`, `GLIC 3P4W`), non-conscious soluble controls (`Albumin 1E7B`, `Luciferase 1BA3`), unrelated globular negative controls (`Lysozyme 1DPX`, `Ubiquitin 1UBQ`), and a randomized aromatic cloud (`1JFF_shuffled`), does tubulin outperform non-conscious control proteins?
5. **Physical & Structural Robustness:** Is Kurian–Craddock's diagonal-only tensor truncation (`Model A`) even rotationally invariant under rigid 3D `SO(3)` rotations of the protein–ligand complex, and do the results hold under the rotationally invariant full `3N × 3N` Drude tensor model (`Model B`), `4I4T`, and `Vinardo` docked poses?

---

## 2. Models & Exact Mathematical Specification

### 2.1 Aromatic Network Extraction (All 8 Proteins + Shuffled Control)
From each PDB structure (`MANIFEST.md`), extract every complete `TRP`, `TYR`, and `PHE` side chain on the active chains using Kurian et al. (2018, Fig. 4) exact ring centers and local orthonormal frames $\mathbf{R}_s = [\hat{\mathbf{x}}_s, \hat{\mathbf{y}}_s, \hat{\mathbf{z}}_s]$:
- **`TRP` (indole):** Center = midpoint of `CD2–CE2`; `x` toward `NE1`, `z` = ring normal (`x × (CZ2 − CG)`), `y = z × x`.
- **`TYR` (phenol):** Center = centroid of 6-ring (`CG, CD1, CD2, CE1, CE2, CZ`); `y` along `CZ → CG`, `z` = ring normal (`((CD1+CE1)−(CD2+CE2)) × y`), `x = y × z`.
- **`PHE` (benzene):** Center = centroid of 6-ring; `y` along `CG → CZ`, `z` = ring normal (`((CD2+CE2)−(CD1+CE1)) × y`), `x = y × z`.

Polarizability tensors in atomic units (`1 a.u. = 1.64877727436 × 10⁻⁴¹ C² m² J⁻¹`):
- **Kurian (2018) Table III verbatim (used in `Model A`):** `TRP = (119.5, 91.6, 29.4)`, `TYR = (89.5, 43.0, 82.9)`, `PHE = (79.0, 79.0, 38.6)`.
- **Physical plane-aligned (used in `Model B` and `Model A_phys` sensitivity check):** `TYR = (89.5, 82.9, 43.0)` (putting the out-of-plane `43.0` component on the ring normal `z`), with `TRP` and `PHE` identical.
- **`1JFF_shuffled` synthetic control:** Same `81` aromatic residue types (`8 Trp, 34 Tyr, 39 Phe`) placed uniformly at random (minimum separation `≥ 4.5 Å`, fixed seed `20261123`) inside the bounding ellipsoid of `1JFF` with random uniform `SO(3)` orientations, with 8 random pockets placed `4.5–7.5 Å` from randomly sampled aromatic residues.

### 2.2 Ligand Geometry & Polarizability Tensor
For every `(target, pocket, molecule)` docked pose (`MODEL 1` from `#48` `Vina` primary; `Vinardo` secondary), recover all-atom coordinates (adding hydrogens via Open Babel `3.1.1` for molecules with `n_H > 0`, asserting 100% exact molecular formula match for all 35 molecules) and compute:
- Centroid $\mathbf{r}_m$ (mean of all atomic coordinates in `Å`).
- Full `3×3` molecular polarizability tensor $\boldsymbol{\alpha}_m$ in the docked lab frame via **Thole (1981) / van Duijnen & Swart (1998, Table 5)** exponential-damped interacting-dipole relay matrix (`a = 2.089`, zero free parameters).
- **Table S1 Exact Calibration Check (on the 11 Craddock gases):** Isotropical scaling of $\boldsymbol{\alpha}_m$ so its trace/3 matches Craddock Table S1's exact `CAM-B3LYP/PolX` mean polarizability to 4 significant figures.

### 2.3 Model A — Exact Kurian (2018) / Craddock (2017) `N × N` Scalar-Oscillator Hamiltonian
For each oscillator $s \in \{1,\dots,N\}$ with lab-frame polarizability tensor $\mathbf{A}_s = \mathbf{R}_s \boldsymbol{\alpha}_s \mathbf{R}_s^T$ (or $\boldsymbol{\alpha}_m$ for the docked ligand):
1. Extract diagonal vector $\mathbf{d}_s = (A_{s,xx}, A_{s,yy}, A_{s,zz})$, norm $\bar{\alpha}_s = \|\mathbf{d}_s\|_2$, and unit dipole direction $\hat{\mathbf{u}}_s = \mathbf{d}_s / \bar{\alpha}_s$.
2. Uncoupled squared angular frequency $\bar{\omega}_s^2 = e^2 / (m_e \bar{\alpha}_s \cdot \text{AU\_SI})$.
3. Symmetric dynamical matrix $\mathbf{M} = \mathbf{V}/m_e$ (`(rad/s)²`):
   - $M_{ss} = \bar{\omega}_s^2$
   - $M_{st} = \frac{e^2}{4\pi\varepsilon_0 m_e r_{st}^3}\left[\hat{\mathbf{u}}_s \cdot \hat{\mathbf{u}}_t - 3(\hat{\mathbf{u}}_s \cdot \hat{\mathbf{r}}_{st})(\hat{\mathbf{u}}_t \cdot \hat{\mathbf{r}}_{st})\right]$ for $s \neq t$.
4. Solve eigenvalues $\Omega_n^2$ via `numpy.linalg.eigh(M)` and convert to linear frequency $f_n = \sqrt{\max(\Omega_n^2, 0)} / (2\pi \cdot 10^{12})\text{ THz}$ (recording any negative eigenvalue count `n_neg` as a diagnostic).

### 2.4 Model B — Rotationally Invariant Full `3N × 3N` Coupled 3D Drude Oscillator Hamiltonian
Each oscillator has 3 displacement components $\mathbf{r}_s \in \mathbb{R}^3$ with exact restoring stiffness tensor $\mathbf{K}_s = e^2 (\mathbf{A}_s \cdot \text{AU\_SI})^{-1}$:
- Diagonal `3×3` block: $\mathbf{M}_{ss} = (e^2 / m_e) (\mathbf{A}_s \cdot \text{AU\_SI})^{-1}$.
- Off-diagonal `3×3` block ($s \neq t$): $\mathbf{M}_{st} = \frac{e^2}{4\pi\varepsilon_0 m_e r_{st}^3}(\mathbf{I}_3 - 3\hat{\mathbf{r}}_{st}\hat{\mathbf{r}}_{st}^T)$.
- Strictly invariant under arbitrary rigid `SO(3)` rotations of the protein + ligand coordinate frame (`max |Δf| < 10⁻¹² THz`).

### 2.5 Exact Eigenvector-Overlap Mode Matching
When adding one ligand (`1` mode in Model A; `3` modes in Model B) to an unperturbed protein (`N` or `3N` modes):
1. Identify the **agent-dominated new mode(s)** as the mode(s) with largest squared amplitude on the ligand coordinate(s): $f_{\text{new}}$ (Model A: 1 mode; Model B: 3 modes, summarized by lowest and mean).
2. Match the remaining $N$ (or $3N$) perturbed modes 1-to-1 to the unperturbed protein modes by maximizing total squared eigenvector overlap $|\langle \mathbf{v}_i^{(0)} | \mathbf{v}_j^{(1),\text{prot}} \rangle|^2$ via `scipy.optimize.linear_sum_assignment`.
3. Compute each protein mode's exact frequency shift $\Delta f_i = f_{\text{matched}(i)}^{(1)} - f_i^{(0)}$ in **GHz** (`1 THz = 1,000 GHz`).

---

## 3. Primary & Secondary Observables

For every protein $T$ and molecule $m$:
1. **`D_613(T, m)` (Primary Craddock Fig. 4 metric, in GHz):** In each pocket $k$, find the unperturbed mode $i^*$ inside `[605, 621] THz` (`613 ± 8 THz`) with maximum $|\Delta f_i|$; take the pocket $k^*$ with maximum $|\Delta f_{i^*}|$; set `D_613 = −Δf_{i^*}` so **positive = downward shift** (Craddock's reported anaesthetic direction) and **negative = upward shift** (Craddock's reported non-anesthetic direction). (If a minimal protein like `1UBQ` has zero unperturbed modes in `[605, 621] THz`, report `NA` for `D_613` and evaluate `D_all`.)
2. **`D_down_613(T, m)` (Strict downward-only metric, in GHz):** $\max_k \max_{i \in [605, 621]} (-\Delta f_i)$ (crisp direct check of Craddock's *"maximum frequency decrease in this range"*).
3. **`f_new(T, m)` (Craddock Fig. 3 metric, in THz):** Mean frequency of the agent-dominated new mode across pockets (and isolated ligand Drude frequency $f_{\text{iso}} = \frac{1}{2\pi}\sqrt{e^2/(m_e \bar{\alpha}_m)}$ for direct comparison).
4. **`D_all(T, m)` & `RMS_shift(T, m)` (Band-agnostic metrics, in GHz):** Largest signed downward shift (`−Δf` of the mode with largest `|Δf|` anywhere in the spectrum) and RMS shift across all protein modes, so no protein is penalized for having its aromatic peak slightly outside `613 ± 8 THz`.
5. **`D_3d_all(T, m)` & `RMS_3d(T, m)` (`Model B`):** Same band-agnostic signed peak shift and RMS shift under the rotationally invariant `3N × 3N` Drude tensor model.

---

## 4. Statistical Tests & Pre-Registered Verdict Rule

All permutation `p`-values use `10,000` two-sided label permutations (`seed = 20261123`); all confidence intervals and paired target differences (`Tubulin 1JFF − Comparator`) use `5,000` molecule bootstrap resamples.

1. **Test 1 (Craddock 8-vs-2 Reproduction on `1JFF`):** Spearman `ρ(D_613, −log10 MAC)` across the 8 original clinical anaesthetics, exact `D_613 > 0` vs `D_613 < 0` sign classification of the 8 anaesthetics vs `F6`/`TFMB`, and `f_new` vs `−log10 MAC` (plus exact Table S1-calibrated version).
2. **Test 2 (Expanded 27-vs-7 Generalization on `1JFF` & `4I4T`):**
   - Potency tracking: Spearman `ρ_pot(D_613, −log10 MAC)` (`n = 27`), plus partial correlations controlling for isolated molecular polarizability `ρ_pot|α` and olive-oil solubility `ρ_pot|oil`.
   - Non-immobilizer separation: ROC `AUC(D_613)` (`27` anaesthetics above `7` non-immobilizers), sign-split accuracy (`D_613 > 0` for anaesthetics vs `D_613 < 0` for non-immobilizers), and polarizability-adjusted residual `r_non|α`.
3. **Test 3 (Cross-Protein Specificity):** Paired bootstrap `Δρ_pot` and `ΔAUC` (`1JFF` minus `4I4T`, `GABA_A`, `GLIC`, `Albumin`, `Luciferase`, `Lysozyme`, `Ubiquitin`, and `1JFF_shuffled`) on both `D_613` and `D_all` (and `Model B`).
4. **Test 4 (Level-Repulsion Mechanism Test):** Fraction of all `35 × 8` protein-molecule pairs whose `D_613` sign (`> 0` vs `< 0`) is predicted solely by `sign(f_iso − 613 THz)` (isolated molecule polarizability alone, zero protein information!).
5. **Test 5 (SO(3) Rotational Invariance Audit):** Apply 20 random rigid 3D rotations to `1JFF + isoflurane` (site 7) and `1JFF + TFMB` (site 5) and record the spread (`range` and `SD` in GHz) of `D_613` under `Model A` vs `Model B`.

### Pre-Registered Verdict Categories
- **`tubulin_selective_terahertz`**: `1JFF` (replicated on `4I4T`) tracks potency across the expanded `n = 27` volatile anaesthetics (`ρ_pot > 0, p < 0.05`) **even after controlling for isolated polarizability** (`ρ_pot|α > 0, p < 0.05`), separates the `27` anaesthetics above the `7` non-immobilizers (`AUC > 0.70, p < 0.05`), **and** significantly beats all non-conscious controls (`Albumin`, `Luciferase`, `Lysozyme`, `1JFF_shuffled`, paired bootstrap 95% CI strictly `> 0`).
- **`level_repulsion_artifact_not_tubulin_specific`**: Craddock's 8-vs-2 sign split reproduces (partially or fully) via coupled-oscillator level repulsion (`sign(D_613)` tracks `sign(f_iso − 613 THz)` on `≥ 80%` of cases), **but** fails on the expanded `27`-vs-`7` panel (`ρ_pot|α ≤ 0` or `p ≥ 0.05`, OR `AUC ≤ 0.65`) **and/or** occurs equally in non-conscious control proteins (`Albumin`, `Luciferase`, `Lysozyme`, `1JFF_shuffled` with no tubulin advantage).
- **`generic_across_proteins`**: Expanded `27`-vs-`7` potency tracking (`ρ_pot > 0, p < 0.05`) and non-immobilizer separation (`AUC > 0.70, p < 0.05`) succeed on tubulin, **but** also succeed comparably in non-conscious control proteins with no tubulin specificity advantage.
- **`fails_reproduction`**: Fails both on Craddock's `8`-vs-`2` benchmark and on the expanded `27`-vs-`7` panel.

---

## 5. Known Limits (Declared Before Running)

- **Point-dipole classical/harmonic Drude approximation:** Following Craddock et al. (2017) and Kurian et al. (2018), aromatic rings and volatile gases are represented as point dipoles (`r⁻³` coupling) without quantum-chemical excited-state CI/TD-DFT coupling, solvent dielectric screening ($\varepsilon = 1$ in vacuum as in Craddock 2017), or thermal decoherence. Our study directly evaluates whether Craddock et al.'s published model holds up mathematically and across proteins; it does not test unrelated quantum-optical mechanisms (e.g. UV tryptophan superradiance in polymerized lattices, Kalra et al. 2023).
- **Static crystal snapshots & Thole polarizabilities:** We use crystal/cryo-EM structures (`1JFF`, `4I4T`, etc.) rather than Craddock's proprietary MD snapshot, and Thole (van Duijnen & Swart 1998) interacting-dipole tensors (`r = 0.994` vs Craddock's `CAM-B3LYP/PolX`), supplemented by an exact Table S1-calibrated check on all 11 Craddock gases.
- **No permanent-dipole term in the linearized normal-mode matrix:** Just as in Craddock et al. (2017) Eq. (3)–(4), static permanent dipoles do not appear in the quadratic harmonic Hessian $\mathbf{V}$ of induced electronic displacements.
