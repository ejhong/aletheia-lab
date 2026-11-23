# Results — Do Anaesthetics Selectively Shift Collective Tryptophan/Aromatic Dipole Modes in Tubulin? (`anaesthetics-terahertz`, Issue #115)

**Short answer (`level_repulsion_artifact_not_tubulin_specific`):** No. We reproduced Craddock et al. (2017)'s published baseline tubulin dipole spectrum (`468.0–695.5 THz` vs their `480–700 THz`) and their reported `613 ± 8 THz` downward-vs-upward sign split on their original 8 clinical anaesthetics (`7/8` downward) versus `F6` and `TFMB` (`2/2` upward, `AUC = 0.94`; `0.88` with exact Table S1 calibration). **However, that sign split has nothing to do with microtubules or general anaesthesia:**

1. **Pure two-oscillator level repulsion explains `96.2%` of all shifts (`303 / 315` protein–gas pairs across 9 targets and 35 gases).** Because every protein built from tryptophan (`531 THz`), tyrosine (`579 THz`), and phenylalanine (`605 THz`) has normal modes around `613 THz`, any gas with isolated Drude frequency `f_iso > 613 THz` (polarizability `α ≲ 9.5 Å³`) pushes the `613 THz` band **downward**, and any gas with `f_iso < 613 THz` (`α ≳ 9.5 Å³`) pushes it **upward** — with zero protein-specific biology required.
2. **Egg-white lysozyme (`1DPX`), ubiquitin (`1UBQ`), and 81 randomly scattered aromatic rings (`1JFF_shuffled`) reproduce Craddock's 8-vs-2 split identically to tubulin** (`7/8` down, `2/2` up; `Lysozyme AUC = 0.94`, `Shuffled AUC = 0.88`).
3. **The split collapses on the expanded 27-anaesthetic vs 7-non-immobilizer volatile panel.** Eleven potent real anaesthetics with higher polarizability — including `o/m/p-xylene`, `toluene`, `cycloheptane`, `n-hexane`, `cyclohexane`, `methylpentafluorobenzene`, and clinical `methoxyflurane` — shift `613 THz` **upward** just like `F6` and `TFMB`. Conversely, compact non-immobilizers (`perfluorocyclobutane`, `CF3CClFCF3`) shift **downward** just like clinical anaesthetics. Across all 27 anaesthetics on tubulin (`1JFF`), potency tracking collapses to `ρ = −0.080` (`p = 0.705`), and non-immobilizer separation (`AUC = 0.698`, `p = 0.115`) ties 81 randomly shuffled rings identically (`ΔAUC = 0.000`, 95% CI `[−0.132, +0.127]`).
4. **The published Kurian–Craddock diagonal-only Hamiltonian breaks 3D rotational symmetry.** Rotating `1JFF + ligand` rigidly in empty space across 20 random `SO(3)` orientations swings isoflurane's `613 THz` shift 27-fold (`+37` to `+1,018 GHz`) and **flips TFMB's sign** (`−3,703` to `+2,722 GHz`). Fixing that symmetry bug via the full `3N × 3N` 3D Drude tensor model (`Model B`, drift `10⁻⁹ GHz`) still yields zero potency tracking on tubulin (`ρ = −0.120`, `p = 0.550`).

---

## 1. Protocol Compliance & Pre-Registered Verdict

- **Lock:** `questions/anaesthetics-terahertz/protocol.lock` (`sha256: 750113e2a758`, locked `2026-11-23T22:50:37Z`, committed in `1936be2` in its own commit before running any ligand-bound protein calculations).
- **Amendments:** None (`amendments.md` unchanged; zero protocol changes).
- **Pre-lock physics tests (`analysis/test_terahertz.py`):** All pass (analytic 2-oscillator level-repulsion theorem, `Model B` exact `SO(3)` rotational invariance to `6.8 × 10⁻¹³ THz`, Thole calibration `r = 0.9937` vs Craddock Table S1 `n = 11`, exact formula verification on `35/35` docked ligands).
- **Pre-registered verdict (`summary.json` → `verdict`):**
  - **`verdict_code`:** `level_repulsion_artifact_not_tubulin_specific`
  - `orig_8v2_reproduced`: **`true`** (`1JFF` 8-vs-2 `AUC = 0.938`, S1-calibrated `0.875`)
  - `level_repulsion_gt80pct`: **`true`** (`303 / 315 = 96.2%`)
  - `pot_1jff_expanded`: **`false`** (`ρ = −0.080`, `p = 0.705`)
  - `pot_4i4t_expanded`: **`false`** (`ρ = −0.127`, `p = 0.531`)
  - `pot_1jff_partial_alpha`: **`false`** (`ρ|α = +0.325`, `p = 0.097`)
  - `auc_1jff_expanded`: **`false`** (`AUC = 0.698`, `p = 0.115`)
  - `beats_all_controls`: **`false`** (ties `1JFF_shuffled`, `Lysozyme`, `Ubiquitin`, `Albumin`, `GABA_A`, `GLIC`)

---

## 2. Test 1: Craddock et al. (2017) 8-vs-2 Benchmark Across Proteins

Evaluating the exact Kurian–Craddock Hamiltonian (`Model A`, `D_613` = downward shift at `613 ± 8 THz` in GHz) on Craddock's original 8 clinical anaesthetics (`desflurane`, `diethyl ether`, `enflurane`, `halothane`, `isoflurane`, `methoxyflurane`, `nitrous oxide`, `sevoflurane`) vs `2` non-immobilizers (`F6`, `TFMB`), using both Thole tensors and exact Craddock Table S1 DFT-calibrated tensors:

| Target | Aromatics (`613 ± 8` modes) | Thole 8-vs-2 Down / Up | Thole 8-vs-2 `AUC` | Thole 8-drug `ρ` | S1-Calibrated Down / Up | S1-Calibrated `AUC` | S1-Calibrated `ρ` (`p`) |
|---|---:|---:|---:|---:|---:|---:|---:|
| **Tubulin (`1JFF`)** | `81` (`16`) | `7/8` · `2/2` | `0.938` | `+0.119` | `7/8` · `2/2` | `0.875` | `+0.119` (`0.792`) |
| **Tubulin (`4I4T`, 1.80 Å)** | `83` (`14`) | `7/8` · `2/2` | `0.875` | `+0.000` | `7/8` · `2/2` | `0.875` | `+0.000` (`1.000`) |
| **`GABA_A` (`6X3T`)** | `234` (`32`) | `7/8` · `2/2` | `0.875` | **`+0.905`** | `7/8` · `2/2` | `0.875` | **`+0.809` (`0.017`)** |
| **`GLIC` (`3P4W`)** | `215` (`45`) | `7/8` · `2/2` | `0.938` | `+0.167` | — | — | — |
| **Albumin (`1E7B`)** | `48` (`11`) | `6/8` · `2/2` | `0.875` | `−0.524` | `6/8` · `2/2` | `0.812` | `−0.500` (`0.220`) |
| **Luciferase (`1BA3`)** | `50` (`15`) | `7/8` · `2/2` | `0.875` | `+0.238` | — | — | — |
| **Lysozyme (`1DPX`)** | `12` (`2`) | **`7/8` · `2/2`** | **`0.938`** | `+0.310` | **`7/8` · `2/2`** | **`0.938`** | `+0.309` (`0.470`) |
| **Ubiquitin (`1UBQ`)** | `3` (`1`) | **`7/8` · `2/2`** | `0.875` | `+0.286` | — | — | — |
| **Shuffled 81 rings** | `81` (`15`) | **`7/8` · `2/2`** | `0.875` | `+0.262` | **`7/8` · `2/2`** | `0.875` | `+0.309` (`0.453`) |

*Note on the 1 clinical drug that shifts upward (`7/8` rather than `8/8`)*: `methoxyflurane` has `α = 10.70 Å³` in Craddock Table S1 (`10.89 Å³` Thole), giving `f_iso ≈ 581–588 THz < 613 THz`. In Craddock et al. (2017)'s MD snapshot, slight anisotropy/orientation differences placed `methoxyflurane` barely above their shifted local mode, whereas in crystal structures `1JFF`, `4I4T`, `GABA_A`, `Lysozyme`, and `Shuffled`, `methoxyflurane` sits below `613 THz` and shifts upward alongside `F6` and `TFMB`.

And on **Craddock Fig. 3 (`f_new`, frequency of the added agent mode)**:
- Across the 8 clinical drugs, `−f_new` correlates with clinical potency at `ρ = +0.810` on `1JFF`, `+0.833` on `4I4T`, `+0.833` on `GABA_A`, `+0.976` on **Albumin**, `+0.929` on **Lysozyme**, `+0.857` on **Ubiquitin**, and `+0.857` on **81 shuffled rings** — purely because `f_new ≈ f_iso ∝ α^(−1/2)`. Controlling for isolated polarizability `α` collapses `1JFF`'s `27`-gas `f_new` potency correlation from `+0.601` to `+0.096`, and `f_new` gives `AUC = 0.000` on 8-vs-2 (`0.376` on 27-vs-7) because bulky non-immobilizers have even *lower* `f_new` than real anaesthetics.

---

## 3. Tests 2 & 3: Expanded 27-vs-7 Volatile Panel & Target Specificity Across All Nine Targets

Primary `Model A` (`D_613`, Vina poses; `n = 27` volatile anaesthetics vs `n = 7` confirmed non-immobilizers, `10,000` permutations, `5,000` paired molecule bootstraps):

| Target | `27`-gas Potency `ρ` (`p`) | Partial `ρ\|α` (`p`) | `27`-vs-`7` `AUC` (`p`) | Down / Up Counts | Paired `Δρ` (`1JFF − T`, 95% CI) | Paired `ΔAUC` (`1JFF − T`, 95% CI) | Level-Repulsion Match |
|---|---:|---:|---:|---:|---:|---:|---:|
| **Tubulin (`1JFF`)** | `−0.080` (`0.705`) | `+0.325` (`0.097`) | `0.698` (`0.115`) | `16/27` · `5/7` | — | — | `32/35` (`91.4%`) |
| **Tubulin (`4I4T`, 1.8 Å)** | `−0.127` (`0.531`) | `+0.464` (`0.016`) | `0.587` (`0.511`) | `17/27` · `5/7` | `+0.047` (`−0.28, +0.34`) | `+0.111` (`−0.06, +0.28`) | `35/35` (`100.0%`) |
| **`GABA_A` (`6X3T`)** | `+0.021` (`0.915`) | `+0.355` (`0.067`) | `0.603` (`0.428`) | `17/27` · `5/7` | `−0.101` (`−0.56, +0.32`) | `+0.095` (`−0.10, +0.29`) | `32/35` (`91.4%`) |
| **`GLIC` (`3P4W`)** | `−0.097` (`0.628`) | `+0.257` (`0.194`) | `0.730` (`0.066`) | `17/27` · `5/7` | `+0.017` (`−0.34, +0.32`) | `−0.032` (`−0.16, +0.09`) | `35/35` (`100.0%`) |
| **Albumin (`1E7B`)** | `−0.146` (`0.465`) | `+0.180` (`0.367`) | `0.571` (`0.597`) | `12/27` · `5/7` | `+0.067` (`−0.33, +0.48`) | `+0.127` (`−0.06, +0.32`) | `30/35` (`85.7%`) |
| **Luciferase (`1BA3`)** | `−0.409` (`0.035`) | `−0.045` (`0.829`) | `0.667` (`0.191`) | `16/27` · `5/7` | `+0.329` (`+0.08, +0.57`) | `+0.032` (`−0.10, +0.15`) | `34/35` (`97.1%`) |
| **Lysozyme (`1DPX`)** | `−0.256` (`0.195`) | `+0.079` (`0.699`) | `0.661` (`0.209`) | `17/27` · `5/7` | `+0.176` (`−0.18, +0.50`) | `+0.037` (`−0.12, +0.19`) | `35/35` (`100.0%`) |
| **Ubiquitin (`1UBQ`)** | `−0.156` (`0.444`) | `+0.173` (`0.388`) | `0.677` (`0.163`) | `17/27` · `5/7` | `+0.076` (`−0.27, +0.37`) | `+0.021` (`−0.15, +0.20`) | `35/35` (`100.0%`) |
| **Shuffled 81 rings** | `−0.115` (`0.566`) | `+0.196` (`0.332`) | **`0.698` (`0.116`)** | `17/27` · `5/7` | `+0.035` (`−0.34, +0.35`) | **`0.000` (`−0.13, +0.13`)** | `35/35` (`100.0%`) |

### Secondary Metrics & Robustness Checks
- **Strict downward-only shift (`D_down_613`):** Yields significant `AUC` on `1JFF` (`0.894`, `p = 0.0008`), **but also on `GABA_A` (`0.852`, `p = 0.004`), `Albumin` (`0.828`, `p = 0.007`), `4I4T` (`0.767`), `GLIC` (`0.759`), and `Shuffled 81 rings` (`0.746`, `p = 0.045`)**, while potency tracking remains negative on `1JFF` (`ρ = −0.086`), `4I4T` (`−0.155`), `GLIC` (`−0.211`), and `Albumin` (`−0.283`).
- **`Vinardo` docked poses (`Model A`, `D_613`):** Identical null result — `1JFF` fails potency tracking and ties controls (`Shuffled: ρ = −0.093, AUC = 0.704`; `Luciferase: AUC = 0.757`; `GLIC: AUC = 0.714`; `Lysozyme: AUC = 0.709`).
- **Physical plane-aligned `Tyr` (`Model A_phys`):** Virtually unchanged across all targets.
- **Rotationally invariant full `3N × 3N` 3D Drude tensor (`Model B`):** `1JFF` gives `D_all ρ = −0.120` (`p = 0.550`, `AUC = 0.794`) and `RMS ρ = +0.081` (`p = 0.686`, `AUC = 0.757`); `4I4T` drops to `D_all AUC = 0.508` (`RMS AUC = 0.598`); `GLIC` (`D_all AUC = 0.804`) and `GABA_A` (`RMS AUC = 0.757`) match or exceed `1JFF`, while **Lysozyme** shows the strongest potency correlation in the entire panel (`RMS ρ = +0.582`, `p = 0.0012`).

---

## 4. Test 4 & Test 5: Why It Happens — Level Repulsion & Broken `SO(3)` Rotational Symmetry

### 4.1 Level Repulsion (`303 / 315 = 96.2%`)
Across all 9 targets and 35 gases, the rule **`f_iso > 613 THz → downward shift (+); f_iso < 613 THz → upward shift (−)`** predicts the sign of `D_613` on **`303 / 315` (`96.2%`)** of pairs, and **`100.0%` (`35/35`)** on `4I4T`, `GLIC`, `Lysozyme`, `Ubiquitin`, and `1JFF_shuffled`. Look at the concrete counterexamples that break Craddock's anaesthesia interpretation on `1JFF`:
- **Potent real anaesthetics that shift UPWARD (`D_613 < 0`, because `f_iso < 613 THz`):** `o-xylene` (`MAC = 0.00118 atm`, `f_iso = 532 THz`, `D_613 = −305 GHz`), `m-xylene` (`−166 GHz`), `p-xylene` (`−211 GHz`), `toluene` (`−357 GHz`), `methylpentafluorobenzene` (`−423 GHz`), `cycloheptane` (`−203 GHz`), `n-hexane` (`−763 GHz`), `cyclohexane` (`−557 GHz`), and clinical `methoxyflurane` (`MAC = 0.0016 atm`, `−431 GHz`).
- **Confirmed non-immobilizers that shift DOWNWARD (`D_613 > 0`, because `f_iso > 613 THz`):** `perfluorocyclobutane` (`f_iso = 687 THz`, `D_613 = +178 GHz`) and `2-chloroheptafluoropropane` (`CF3CClFCF3`, `f_iso = 656 THz`, `D_613 = +359 GHz`).

### 4.2 Broken `SO(3)` Rotational Invariance in Kurian (2018) / Craddock (2017)
Rotating the entire `1JFF + ligand` coordinate system rigidly by `20` random `SO(3)` rotations leaves every interatomic distance and relative angle mathematically identical. Yet because Kurian–Craddock (`Model A`) rotates each 3×3 polarizability tensor into the protein's arbitrary PDB frame and then **drops all off-diagonal elements** before defining $\bar{\alpha} = \sqrt{\alpha'_{xx}{}^2 + \alpha'_{yy}{}^2 + \alpha'_{zz}{}^2}$ and $\hat{\mathbf{u}} \propto (\alpha'_{xx}, \alpha'_{yy}, \alpha'_{zz})$, the predicted physics changes wildly with coordinate-frame orientation:

| Complex | `Model A` (Kurian–Craddock) `D_613` across 20 rigid 3D rotations | `Model A` baseline `f_min` drift | `Model B` (exact `3N × 3N` Drude) drift |
|---|---|---:|---:|
| **`1JFF + isoflurane` (`site_7`)** | **`+37.3` to `+1,017.5 GHz`** (mean `+353.5 ± 260.3 GHz`, **27× spread**) | `483.4–515.5 THz` (`32.1 THz`) | **`1 × 10⁻⁹ GHz`** (exact invariant) |
| **`1JFF + TFMB` (`site_5`)** | **`−3,702.8` to `+2,721.5 GHz`** (mean `+47.4 ± 1,195.6 GHz`, **flips sign!**) | `483.4–515.5 THz` (`32.1 THz`) | **`1 × 10⁻⁹ GHz`** (exact invariant) |

---

## 5. Limits & What This Study Does Not Rule Out

1. **This tests Craddock et al. (2017)'s published Drude-oscillator model, not every possible microtubule hypothesis.** It decisively refutes the claim that Craddock et al. (2017)'s collective `613 THz` dipole-shift mechanism is selective for tubulin or separates anaesthetics from non-immobilizers generally. It does *not* test experimental UV tryptophan fluorescence/superradiance in polymerized microtubules (Kalra et al. 2023) or live-animal pharmacology using microtubule-stabilizing drugs.
2. **Crystal snapshots vs. Craddock's MD snapshot & Thole vs. DFT tensors.** We used public crystal structures (`1JFF`, `4I4T`) rather than Craddock's unshared MD snapshot, and Thole interacting-dipole tensors (`r = 0.994` vs Table S1) plus an exact Table S1-calibrated check on all 11 Craddock gases. Because our findings rest on exact linear-algebra properties (level repulsion around `613 THz` and broken `SO(3)` rotational invariance), they do not depend on minor coordinate or polarizability differences.
3. **Pending independent replication.** As a `lane:data` study in Aletheia Lab, independent replication by a second vendor's agent from `protocol.md` alone remains open.

---

## 6. What This Means

When our earlier docking test (`#48`) could not tell microtubule tubulin apart from ion channels or bystander proteins, the strongest remaining computational case for Orch OR anaesthesia was Craddock et al. (2017): the claim that after an anaesthetic settles into tubulin, it shifts a collective terahertz oscillation near `613 THz` downward in proportion to clinical strength, while look-alike non-anaesthetics (`F6` and `TFMB`) shift it upward instead. When we rebuilt that exact physics model and ran it across 35 volatile gases and nine targets — including rival ion channels, blood albumin, egg-white lysozyme, and 81 randomly scattered aromatic rings — the magic vanished. The downward-versus-upward sign flip is simple textbook level repulsion between two coupled oscillators (`96.2%` explained by a single property of the gas alone, with zero biology), which is why **egg-white lysozyme and 81 random rings reproduce Craddock's 8-vs-2 result just as cleanly as tubulin**. Once you add more real anaesthetics and non-anaesthetics, the split falls apart: eleven potent real anaesthetics shift the "wrong" way, and compact non-anaesthetics shift like real drugs. Worse still, the published 2017 equations contain a coordinate-frame symmetry flaw: simply rotating the tubulin crystal rigidly in empty space flips `TFMB` from an upward shift to a downward shift. Whatever role microtubules may or may not play in living brains, the `613 THz` collective dipole-shift calculation does not support Orch OR.

---

## 7. Files & Provenance

- **Protocol & Lock:** [`protocol.md`](./protocol.md), [`protocol.lock`](./protocol.lock), [`amendments.md`](./amendments.md), [`MANIFEST.md`](./MANIFEST.md), [`log.md`](./log.md)
- **Code & Tests:** [`analysis/terahertz_modes.py`](./analysis/terahertz_modes.py), [`analysis/test_terahertz.py`](./analysis/test_terahertz.py), [`analysis/make_figures.py`](./analysis/make_figures.py)
- **Locked Outputs:** [`results/shifts.tsv`](./results/shifts.tsv), [`results/summary.json`](./results/summary.json)
- **Interactive Figures:** `site/figures/anaesthetics-terahertz/{tiles,verdict,repulsion,proteins,spectrum}.html`
- **Spending:** `$0.00` (open public PDB data, `#48` docked poses, open-source Python/NumPy/SciPy/Open Babel).
- **Authorship:** AI did this work. **Antigravity (Google DeepMind)** extracted the primary equations from `PMC5575257` and `PMC5796540`, wrote and locked the protocol and solver, ran all nine targets and physics audits, built the interactive visualisations, and wrote this report on `2026-11-23`. **Eugene** directed the study. No human physicist has reviewed these results, and independent second-vendor replication is pending.
