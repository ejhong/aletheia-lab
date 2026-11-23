# Results — Do Anaesthetics Pick Out Microtubules? (`anaesthetics-microtubules`, Issue #48)

**Short answer (`no_potency_or_selectivity`):** No. Across 1,680 open molecular dockings covering 35 volatile compounds and 8 proteins, predicted binding on microtubule αβ-tubulin (`1JFF` and high-resolution `4I4T`) **neither tracks clinical/experimental anaesthetic potency nor rejects fat-soluble non-anaesthetics**. Tubulin shows no specificity advantage over rival ion channels (`GABA_A`, `GLIC`), non-conscious anaesthetic-binding soluble proteins (`Human Serum Albumin`, `Firefly Luciferase`), or unrelated globular negative controls (`Lysozyme`, `Ubiquitin`). In fact, negative-control **Ubiquitin** — a small 76-residue cellular protein with no role in anaesthesia — outperforms tubulin on potency tracking under both `Vina` (`ρ = +0.512` vs `+0.285`) and `Vinardo` (`ρ = +0.596` vs `+0.284`), and is the only protein in the panel to separate anaesthetics above non-immobilizers under `Vinardo` (`AUC = 0.794`, `p = 0.015`).

The primary reason is also clear from the data: empirical docking scores (`Vina`) are overwhelmingly driven by heavy-atom count (`ρ = +0.79` to `+0.97` across seven of the eight proteins). Bulky perfluorinated non-immobilizers (`TFMB`, `perfluoropentane`, `F8`, `F6`) score *tighter* than true clinical anaesthetics on almost every protein, including both tubulin structures and `GABA_A`. Even after removing heavy-atom size bias or switching to `Vinardo`, tubulin still fails to separate itself from bystander proteins.

---

## 1. Pre-Registered Verdict & Protocol Compliance

- **Protocol lock:** `questions/anaesthetics-microtubules/protocol.lock` (`sha256: 9d2201031fe2c6685bd257bf51b46e68d3d44d2959e56499d86a811e5bacb7c2`, locked `2026-11-23T20:03:18Z`, committed in `4a6b0ed` before any test-panel dockings were run).
- **Pre-lock crystallographic self-redocking validation (4 native co-crystal ligands):** All 4 positive-control native ligands redocked well below the `2.0 Å` heavy-atom RMSD threshold under both `vina` and `vinardo`: `GLIC 3P4W + desflurane` (`0.30 / 0.67 Å`), `GABA_A 6X3T + propofol` (`0.72 / 0.28 Å`), `Firefly Luciferase 1BA3 + bromoform` (`0.38 / 0.76 Å`), and `Human Serum Albumin 1E7B + halothane` (`1.22 / 1.31 Å`).
- **Amendments reported (1 pre-results amendment):**
  - **Amendment 1 (`2026-11-23`, committed in `fbc8a25` before any results were produced or inspected):** Reduced AutoDock Vina `--exhaustiveness` from `16` to `4` for operational runtime on a 2-CPU VM after confirming on pre-lock crystallographic controls that top-mode affinities agreed to `0.000 kcal/mol` (`1E7B + halothane`: `−4.456` at `ex = 4, 8, 16`) and `0.011 kcal/mol` (`3P4W + desflurane`: `−5.503` vs `−5.492 kcal/mol`). The partial `ex = 16` output directory from pocket 1 was deleted uninspected before amending. All 8 proteins, 24 pockets (`18 × 18 × 18 Å`), 35 ligands, both scoring functions (`vina` and `vinardo`), fixed random seed (`20261123`), and all statistical tests and verdict criteria remained unchanged. Resumable on-disk caching and exact NumPy vectorization of the permutation/bootstrap loops were added to `analysis/dock_anaesthetics.py` without changing any mathematical calculation (verified by `analysis/test_docking.py`).
- **Pre-registered verdict rule result (`summary.json` → `verdict`):**
  - **`verdict_code`:** `no_potency_or_selectivity`
  - **`tubulin_1jff` primary potency tracking (`ρ > 0`, `p < 0.05`):** **FAILED** (`ρ = +0.285`, `p = 0.146`)
  - **`tubulin_4i4t` replication potency tracking (`ρ > 0`, `p < 0.05`):** **FAILED** (`ρ = +0.347`, `p = 0.074`)
  - **`tubulin_1jff` Vinardo potency tracking (`ρ > 0`, `p < 0.05`):** **FAILED** (`ρ = +0.284`, `p = 0.151`)
  - **`tubulin_1jff` non-immobilizer rejection (`AUC > 0.65` or `r_non_oil < 0`, `p < 0.05`):** **FAILED** (`AUC = 0.212`, `p = 0.0165`; `r_non_oil = +1.34 kcal/mol`, `p = 0.0072`)
  - **`tubulin_4i4t` non-immobilizer rejection:** **FAILED** (`AUC = 0.079`, `p = 0.0005`; `r_non_oil = +1.66 kcal/mol`, `p = 0.0001`)
  - **Outperforms all 4 controls (`Albumin`, `Luciferase`, `Lysozyme`, `Ubiquitin`):** **FAILED** (only exceeds `Lysozyme` on `Δρ_pot`; ties `Albumin` and `Luciferase`; trails `Ubiquitin` on both `Δρ_pot` and `ΔAUC_sep`).

---

## 2. Primary Results Across All Eight Proteins (`AutoDock Vina v1.2.5`, `B_best`)

Each compound's affinity score is `B = −ΔG` (in `kcal/mol`, higher = tighter predicted binding), taking the strongest pocket (`B_best`) for multi-site targets. Potency is `P = −log10(MAC)` across `n = 27` volatile anaesthetics (9 clinical + 18 Fang 1996 aromatics/cycloalkanes); non-immobilizer separation compares those 27 anaesthetics against `n = 7` confirmed Meyer–Overton non-immobilizers (`F6`, `F8`, `TFMB`, `cyclooctane`, `perfluoropentane`, `perfluorocyclobutane`, `2-chloroheptafluoropropane`). Two-sided permutation `p`-values use `10,000` permutations; 95% CIs use `5,000` molecule bootstraps.

| Target (PDB) | Role | Median `−ΔG` Anaes / Non-Imm (kcal/mol) | Potency `ρ` (`p`, 95% CI) | Partial `ρ\|Size` (`p`) | Partial `ρ\|Oil` (`p`) | Size Confound `ρ(B, N_heavy)` | Non-Imm `AUC` (`p`) | Oil Resid `r_non_oil` (`p`) | Size Resid `r_non_heavy` (`p`) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **Tubulin (`1JFF`, 8 sites)** | Primary Orch OR | `5.50 / 6.05` | `+0.285` (`0.146`, `−0.11..+0.62`) | `+0.436` (`0.027`) | `+0.156` (`0.439`) | `+0.898` | `0.212` (`0.017`) | `+1.34` (`0.007`) | `−0.76` (`0.0007`) |
| **Tubulin (`4I4T`, 1.80 Å, 8 sites)** | High-res replication | `4.89 / 5.89` | `+0.347` (`0.074`, `−0.06..+0.65`) | `+0.441` (`0.023`) | `+0.013` (`0.952`) | `+0.800` | `0.079` (`0.0005`) | `+1.66` (`0.0001`) | `−0.08` (`0.650`) |
| **`GABA_A` (`6X3T`, 2 sites)** | Rival ion channel | `5.16 / 6.54` | `+0.415` (`0.030`, `+0.00..+0.71`) | `+0.548` (`0.004`) | `+0.073` (`0.715`) | `+0.794` | `0.079` (`0.0004`) | `+2.25` (`0.0004`) | `+0.06` (`0.762`) |
| **`GLIC` (`3P4W`, 1 site)** | Rival ion channel | `5.35 / 5.70` | `+0.380` (`0.050`, `−0.06..+0.70`) | `+0.534` (`0.003`) | `+0.145` (`0.472`) | `+0.835` | `0.302` (`0.115`) | `+1.25` (`0.012`) | `−0.90` (`0.0005`) |
| **Albumin (`1E7B`, 2 sites)** | Soluble control | `5.24 / 6.64` | `+0.279` (`0.153`, `−0.12..+0.60`) | `+0.373` (`0.054`) | `+0.050` (`0.804`) | `+0.862` | `0.085` (`0.0002`) | `+2.04` (`0.0004`) | `−0.32` (`0.143`) |
| **Luciferase (`1BA3`, 1 site)** | Soluble control | `4.97 / 6.05` | `+0.212` (`0.290`, `−0.20..+0.57`) | `+0.313` (`0.116`) | `+0.092` (`0.644`) | `+0.930` | `0.116` (`0.0007`) | `+1.86` (`0.0008`) | `−0.34` (`0.025`) |
| **Lysozyme (`1DPX`, 1 site)** | Negative control | `4.26 / 5.03` | `+0.099` (`0.623`, `−0.31..+0.50`) | `−0.015` (`0.942`) | `+0.188` (`0.344`) | `+0.968` | `0.169` (`0.007`) | `+1.41` (`0.004`) | `−0.48` (`0.0002`) |
| **Ubiquitin (`1UBQ`, 1 site)** | Negative control | `3.51 / 3.52` | **`+0.512` (`0.006`, `+0.11..+0.80`)** | **`+0.519` (`0.009`)** | `−0.134` (`0.502`) | `+0.422` | `0.460` (`0.772`) | `+0.64` (`0.018`) | `−0.43` (`0.059`) |

*Note on `r_non_oil` and `r_non_heavy`*: Positive values mean non-immobilizers bind **tighter** than expected for an anaesthetic of equal olive-oil solubility (`n = 5` non-immobilizers with measured `λ_oil`) or equal heavy-atom count (`n = 7`); negative values mean non-immobilizers bind **weaker** than expected (the rejection direction).

### Paired Head-to-Head Comparisons (`Tubulin 1JFF` minus Comparator, 5,000 Molecule Bootstraps)

| Comparison (`1JFF − Comparator`) | `Vina Δρ_pot` (95% CI) | `Vina ΔAUC_sep` (95% CI) | `Vinardo Δρ_pot` (95% CI) | `Vinardo ΔAUC_sep` (95% CI) |
|---|---:|---:|---:|---:|
| `1JFF − Tubulin 4I4T` | `−0.062` (`−0.254, +0.112`) | `+0.132` (`+0.021, +0.275`) | `−0.217` (`−0.618, +0.157`) | `+0.188` (`−0.011, +0.418`) |
| `1JFF − GABA_A 6X3T` | `−0.130` (`−0.349, +0.057`) | `+0.132` (`+0.011, +0.291`) | **`−0.287` (`−0.621, −0.005`)** | `+0.188` (`−0.069, +0.437`) |
| `1JFF − GLIC 3P4W` | `−0.095` (`−0.274, +0.061`) | `−0.090` (`−0.238, +0.021`) | `−0.068` (`−0.261, +0.117`) | `−0.122` (`−0.355, +0.095`) |
| `1JFF − Albumin 1E7B` | `+0.006` (`−0.172, +0.197`) | `+0.127` (`+0.026, +0.254`) | `−0.224` (`−0.539, +0.066`) | `+0.191` (`−0.069, +0.455`) |
| `1JFF − Luciferase 1BA3` | `+0.073` (`−0.063, +0.249`) | `+0.095` (`+0.011, +0.201`) | `−0.216` (`−0.553, +0.091`) | `+0.175` (`−0.027, +0.392`) |
| `1JFF − Lysozyme 1DPX` | `+0.187` (`+0.012, +0.402`) | `+0.042` (`+0.000, +0.116`) | `+0.159` (`−0.146, +0.475`) | `+0.116` (`−0.053, +0.307`) |
| `1JFF − Ubiquitin 1UBQ` | `−0.227` (`−0.555, +0.105`) | **`−0.249` (`−0.481, −0.021`)** | **`−0.312` (`−0.638, −0.007`)** | **`−0.339` (`−0.534, −0.143`)** |

*Important context on `ΔAUC_sep`*: Because `1JFF`, `4I4T`, `GABA_A`, `Albumin`, `Luciferase`, and `Lysozyme` all have inverted `AUC` values far *below* `0.50` (`0.08–0.21`), a small positive `ΔAUC` for `1JFF` over `Albumin` (`0.212` vs `0.085`) simply means `1JFF` is slightly less inverted than `Albumin` — **neither rejects non-immobilizers**.

---

## 3. Alternative Scoring Function (`Vinardo`), Single-Site Controls, and Subsets

### 3.1 `Vinardo` Scoring Function (`B_best`)

`Vinardo` places substantially less weight on raw heavy-atom counts (`ρ(B, N_heavy)` drops from `0.79–0.97` down to `0.19–0.59`). Even with size bias dramatically reduced, primary tubulin (`1JFF`) still fails both potency tracking and non-immobilizer separation, while `Ubiquitin` takes first place on every metric:

| Target (PDB) | Median `−ΔG` Anaes / Non-Imm | Potency `ρ` (`p`, 95% CI) | Partial `ρ\|Size` (`p`) | Size Confound `ρ(B, N_heavy)` | Non-Imm `AUC` (`p`) | Size Resid `r_non_heavy` (`p`) |
|---|---:|---:|---:|---:|---:|---:|
| **Tubulin (`1JFF`)** | `4.42 / 4.11` | `+0.284` (`0.151`, `−0.13..+0.64`) | `+0.272` (`0.176`) | `+0.550` | `0.455` (`0.732`) | `−0.57` (`0.012`) |
| **Tubulin (`4I4T`)** | `4.05 / 4.30` | `+0.501` (`0.008`, `+0.08..+0.82`) | `+0.493` (`0.011`) | `+0.190` | `0.267` (`0.061`) | `+0.09` (`0.614`) |
| **`GABA_A` (`6X3T`)** | `4.39 / 4.66` | `+0.571` (`0.003`, `+0.16..+0.85`) | `+0.578` (`0.002`) | `+0.389` | `0.267` (`0.062`) | `−0.05` (`0.843`) |
| **`GLIC` (`3P4W`)** | `4.15 / 3.73` | `+0.352` (`0.073`, `−0.09..+0.70`) | `+0.344` (`0.076`) | `+0.459` | `0.577` (`0.551`) | `−0.76` (`0.008`) |
| **Albumin (`1E7B`)** | `4.35 / 4.77` | `+0.508` (`0.007`, `+0.11..+0.80`) | `+0.542` (`0.004`) | `+0.553` | `0.265` (`0.061`) | `−0.32` (`0.237`) |
| **Luciferase (`1BA3`)** | `3.68 / 4.10` | `+0.500` (`0.008`, `+0.12..+0.78`) | `+0.512` (`0.009`) | `+0.461` | `0.280` (`0.079`) | `−0.07` (`0.703`) |
| **Lysozyme (`1DPX`)** | `3.69 / 3.89` | `+0.126` (`0.527`, `−0.30..+0.56`) | `+0.079` (`0.696`) | `+0.592` | `0.339` (`0.206`) | `−0.10` (`0.569`) |
| **Ubiquitin (`1UBQ`)** | `3.52 / 2.75` | **`+0.596` (`0.002`, `+0.20..+0.85`)** | **`+0.606` (`0.0008`)** | `+0.392` | **`0.794` (`0.015`)** | **`−1.00` (`0.0001`)** |

Note that even on `4I4T` under `Vinardo` (`ρ = +0.501`), its potency correlation is virtually identical to `Albumin` (`+0.508`, paired `Δρ = −0.007`) and `Luciferase` (`+0.500`, `Δρ = +0.001`), behind `GABA_A` (`+0.571`) and `Ubiquitin` (`+0.596`), and its non-immobilizer separation remains inverted (`AUC = 0.267`, `r_non_heavy = +0.09`).

### 3.2 Equal-Pocket (`B_single`) & Boltzmann Aggregation Controls

Because tubulin has 8 pre-registered pockets while single-site controls have 1, we pre-registered a strict 1-site-vs-1-site comparison (`B_single`, using Craddock's primary `site_7` on tubulin) and a Boltzmann-weighted multi-site free energy (`B_boltz` at `310 K`). Removing tubulin's 8-site maximum advantage makes tubulin perform **worse**:

- **`1JFF` single-site (`site_7`) under `Vina`:** `ρ = +0.116` (`p = 0.558`), `ρ|Size = +0.060` (`p = 0.763`), `AUC = 0.254` (`p = 0.052`). Under `Vinardo`: `ρ = +0.128` (`p = 0.523`), `AUC = 0.468`.
- **`4I4T` single-site (`site_7`) under `Vina`:** `ρ = +0.199` (`p = 0.319`), `AUC = 0.111` (`p = 0.0003`). Under `Vinardo`: `ρ = +0.532` (`p = 0.0057`), `AUC = 0.360`.
- **Boltzmann aggregation (`Vina`):** `1JFF` `ρ = +0.230` (`p = 0.253`), `AUC = 0.185` (`p = 0.011`); `4I4T` `ρ = +0.303` (`p = 0.120`), `AUC = 0.127`.

### 3.3 Clinical (`n = 9`, Human MAC) vs. Fang 1996 (`n = 18`, Rat MAC) Subsets

Splitting the 27 anaesthetics by source reveals *why* correlations vary across targets and scoring functions:

| Target | `Vina` Clinical (`n = 9`) | `Vina` Fang 1996 (`n = 18`) | `Vinardo` Clinical (`n = 9`) | `Vinardo` Fang 1996 (`n = 18`) |
|---|---:|---:|---:|---:|
| **Tubulin (`1JFF`)** | `−0.133` (`p = 0.746`) | `+0.440` (`p = 0.067`) | `−0.083` (`p = 0.838`) | `+0.655` (`p = 0.004`) |
| **Tubulin (`4I4T`)** | `−0.200` (`p = 0.615`) | `+0.478` (`p = 0.048`) | `−0.383` (`p = 0.307`) | `+0.761` (`p = 0.0004`) |
| **`GABA_A` (`6X3T`)** | `−0.067` (`p = 0.885`) | `+0.533` (`p = 0.024`) | `−0.167` (`p = 0.675`) | `+0.883` (`p = 0.0001`) |
| **`GLIC` (`3P4W`)** | `+0.033` (`p = 0.949`) | `+0.642` (`p = 0.005`) | `−0.159` (`p = 0.684`) | `+0.732` (`p = 0.0006`) |
| **Albumin (`1E7B`)** | `−0.117` (`p = 0.772`) | `+0.384` (`p = 0.111`) | `−0.283` (`p = 0.455`) | `+0.759` (`p = 0.0007`) |
| **Luciferase (`1BA3`)** | `+0.033` (`p = 0.948`) | `+0.400` (`p = 0.096`) | `−0.117` (`p = 0.779`) | `+0.636` (`p = 0.006`) |
| **Lysozyme (`1DPX`)** | `−0.267` (`p = 0.495`) | `+0.353` (`p = 0.148`) | `−0.400` (`p = 0.292`) | `+0.765` (`p = 0.0003`) |
| **Ubiquitin (`1UBQ`)** | `+0.000` (`p = 1.000`) | `+0.707` (`p = 0.002`) | `+0.267` (`p = 0.489`) | `+0.854` (`p = 0.0001`) |

Two striking facts jump straight out of that split:
1. **On the 9 clinical anaesthetics alone, rigid docking fails on *every* protein.** Potent halogenated agents like methoxyflurane (`MAC = 0.0016 atm`, 8 heavy atoms, `1JFF = 4.83 kcal/mol`) and halothane (`0.0077 atm`, 7 heavy atoms, `4.75 kcal/mol`) have fewer heavy atoms than weaker fluorinated ethers like sevoflurane (`0.020 atm`, 12 heavy atoms, `5.93 kcal/mol`) and desflurane (`0.060 atm`, 10 heavy atoms, `5.67 kcal/mol`). Both `Vina` and `Vinardo` score the weaker, heavier fluorinated ethers tighter than the more potent halogenated agents.
2. **On the 18 homologous aromatics/cycloalkanes (Fang 1996), *every single protein* tracks potency under `Vinardo` (`ρ = +0.64` to `+0.88`)**, including `Lysozyme` (`+0.765`) and `Ubiquitin` (`+0.854`). Because xylenes and toluene have both higher aromatic lipophilicity and higher potency than cyclopentane/cyclohexane, *any* hydrophobic surface patch picks up that trend indiscriminately.

---

## 4. Per-Site Tubulin Breakdown, Craddock (2017) MOE Comparison, and Flurothyl

### 4.1 All 8 Craddock Tubulin Pockets (`Vina`)

Across the 8 persistent single-dimer pockets from Craddock et al. (2012, Tables 2 & 3), `site_5` (β-tubulin colchicine-adjacent cavity) and `site_23` (αβ interface pocket) dominate `B_best`:

| Pocket | `1JFF` Median Anaes / Non-Imm | `1JFF` `ρ_pot` (`p`) | `1JFF` `AUC` | `4I4T` Median Anaes / Non-Imm | `4I4T` `ρ_pot` (`p`) | `4I4T` `AUC` |
|---|---:|---:|---:|---:|---:|---:|
| `site_1` | `3.99 / 5.08` | `+0.167` (`0.397`) | `0.132` | `4.30 / 5.34` | `+0.097` (`0.635`) | `0.153` |
| `site_4` | `4.17 / 4.52` | `+0.109` (`0.580`) | `0.259` | `4.78 / 5.77` | `+0.196` (`0.323`) | `0.053` |
| `site_5` | `5.50 / 5.94` | `+0.300` (`0.127`) | `0.238` | `4.84 / 5.80` | `+0.467` (`0.015`) | `0.169` |
| `site_7` (primary) | `4.51 / 5.43` | `+0.116` (`0.561`) | `0.254` | `4.08 / 5.00` | `+0.199` (`0.321`) | `0.111` |
| `site_21` | `4.30 / 5.10` | `+0.317` (`0.110`) | `0.159` | `4.33 / 5.28` | `+0.109` (`0.586`) | `0.138` |
| `site_23` | `5.43 / 6.05` | `+0.346` (`0.073`) | `0.196` | `4.78 / 5.77` | `+0.480` (`0.013`) | `0.169` |
| `site_37` | `3.18 / 3.32` | `+0.194` (`0.328`) | `0.439` | `3.11 / −0.24` | `+0.193` (`0.325`) | `0.873` |
| `site_38` | `4.42 / 4.59` | `+0.120` (`0.547`) | `0.561` | `3.32 / −2.40` | `+0.034` (`0.868`) | `0.974` |

*(Note: On tightly packed high-resolution `4I4T`, the narrow cavities `site_37` and `site_38` sterically clash with the bulky perfluorinated non-immobilizers, giving negative `−ΔG` values; however, those same sites have near-zero potency tracking [`ρ = +0.193` and `+0.034`] and weak binding even for anaesthetics [`3.1–3.3 kcal/mol`], so molecules prefer the deeper pockets `site_5` and `site_23` by `>1.5 kcal/mol`.)*

### 4.2 Direct Comparison Against Craddock et al. (2017) Table S2 (MOE Docking)

Comparing our `AutoDock Vina` `1JFF` best-site scores directly against the published `MOE` docking scores in Craddock et al. (2017, *Sci. Rep.* 7:9877, Supplementary Table S2) across the 10 shared clinical anaesthetics and non-immobilizers (`desflurane`, `diethyl ether`, `enflurane`, `halothane`, `isoflurane`, `methoxyflurane`, `nitrous oxide`, `sevoflurane`, `F6`, `TFMB`):

- **Cross-software agreement:** Spearman **`ρ = +0.891`** between our open `Vina` scores and Craddock et al.'s commercial `MOE` scores. Our docking faithfully reproduces the binding-rank landscape of their published study.
- **Craddock et al.'s own MOE scores fail both potency and non-immobilizer tests:** Across their 8 anaesthetics, their published MOE best-site scores have **`ρ = +0.048`** against `−log10(MAC)`. Against their 2 non-immobilizers (`F6`: `2.06 kcal/mol`; `TFMB`: `2.64 kcal/mol` — the *tightest* binding molecule in their entire Table S2!), their MOE scores give **`AUC = 0.250`**. That matches our open `Vina` finding (`TFMB = 8.27 kcal/mol`, the tightest-binding compound in our entire panel on `1JFF`).

### 4.3 Annotated Convulsant Control (`Flurothyl`)

`Flurothyl` (`bis(2,2,2-trifluoroethyl) ether`, 11 heavy atoms, `λ_oil = 47`, potent convulsant rather than anaesthetic) binds tightly to `1JFF` (`5.93 kcal/mol` Vina / `4.74 kcal/mol` Vinardo) — tighter than the median anaesthetic (`5.50 / 4.42`) — and also binds `GLIC` (`5.32`), `Luciferase` (`5.25`), `Albumin` (`5.22`), `GABA_A` (`5.19`), `4I4T` (`4.86`), and `Lysozyme` (`4.73`), while binding weakly only to `Ubiquitin` (`3.06 kcal/mol`).

---

## 5. Limits & What This Study Does Not Rule Out

1. **Rigid-receptor docking measures binding energy, not downstream function.** Notice that `GABA_A` (`6X3T`) and `GLIC` (`3P4W`) — well-established pharmacological targets of volatile anaesthetics — also failed to reject perfluorinated non-immobilizers in rigid docking (`GABA_A AUC = 0.079`, `GLIC AUC = 0.302`). That is an important sanity check: rigid-protein empirical docking predicts whether a hydrophobic gas can sit inside a pocket, not whether it stabilizes an open or closed conformational state of an ion channel or alters protein dynamics.
2. **Craddock et al. (2017)'s post-binding optical/terahertz hypothesis is a separate claim.** Craddock et al. (2017) did not claim that MOE binding affinity alone tracks `MAC`; they used docked poses as inputs to a collective tryptophan dipole-coupling model and reported that anaesthetics shifted a predicted `~613 THz` collective oscillation mode in proportion to potency, whereas non-immobilizers did not. Testing that post-binding dipole-network claim requires reproducing their excitonic Hamiltonian calculation (a separate computational study), not docking affinity alone.
3. **Static crystal/cryo-EM snapshots and absence of induced fit or explicit water.** Both `1JFF` (electron crystallography, `3.50 Å`) and `4I4T` (X-ray, `1.80 Å`) are static snapshots without dynamic pocket breathing, explicit water displacement, or polymerized microtubule lattice contacts (inter-protofilament seams).
4. **Pending independent replication.** As a `lane:data` question in Aletheia Lab, full completion requires an independent replication by a second vendor's AI agent working from `protocol.md` and `MANIFEST.md` alone.

---

## 6. What This Means

A striking claim of the Orchestrated Objective Reduction (Orch OR) theory of consciousness is that general anaesthetics erase consciousness by selectively targeting hydrophobic pockets inside neuronal microtubules (αβ-tubulin), rather than acting primarily on synaptic ion channels. When we tested that claim using open, reproducible molecular docking across 35 volatile compounds and 8 proteins — comparing tubulin head-to-head against classic ion-channel targets (`GABA_A`, `GLIC`), non-conscious proteins known to bind anaesthetics (`Albumin`, `Luciferase`), and unrelated everyday proteins (`Lysozyme`, `Ubiquitin`) — microtubules did not stand out at all. Predicted binding on tubulin neither followed how strong each anaesthetic actually is nor rejected look-alike fat-soluble gases that do not cause anaesthesia. In fact, those non-anaesthetic gases scored *tighter* than real clinical anaesthetics on almost every protein because standard docking rewards larger molecules with more atoms, and a tiny bystander protein (`Ubiquitin`) beat tubulin on both scoring methods we tested. That does not prove microtubules play zero role in anaesthesia — rigid docking cannot measure what a drug does *after* it lands in a pocket, including the quantum-dipole shifts proposed by Orch OR researchers or the allosteric gating of ion channels — but it shows plainly that standard molecular docking offers no evidence that anaesthetics pick out microtubules.

---

## 7. Files & Provenance

- **Protocol & Lock:** [`protocol.md`](./protocol.md), [`protocol.lock`](./protocol.lock), [`amendments.md`](./amendments.md), [`MANIFEST.md`](./MANIFEST.md), [`log.md`](./log.md)
- **Code & Tests:** [`analysis/dock_anaesthetics.py`](./analysis/dock_anaesthetics.py), [`analysis/test_docking.py`](./analysis/test_docking.py), [`analysis/make_figures.py`](./analysis/make_figures.py)
- **Locked Outputs:** [`results/affinities.tsv`](./results/affinities.tsv), [`results/summary.json`](./results/summary.json), [`results/poses_3d.json`](./results/poses_3d.json)
- **Interactive Figures:** `site/figures/anaesthetics-microtubules/{tiles,verdict,potency,matrix,pockets}.html`
- **Spending:** `$0.00` (open public RCSB PDB + PubChem data, open-source `AutoDock Vina v1.2.5` and `Open Babel 3.1.1`, run on local CPU).
- **Authorship:** AI did this work. **Antigravity (Google DeepMind)** extracted the primary literature tables, wrote the pre-registered protocol and docking pipeline, ran the 1,680 dockings, built the interactive visualisations, and wrote this report on `2026-11-23`. **Eugene** directed the study. No human biophysicist has reviewed these results, and independent second-vendor replication is pending.
