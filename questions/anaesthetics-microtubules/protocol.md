# Protocol: Do anaesthetics pick out microtubules?

- **Question slug:** `anaesthetics-microtubules`
- **Issue:** #48
- **Lane:** `data`
- **Date locked:** 2026-11-23
- **Budget:** $0.00 (public RCSB PDB structures, PubChem structures, and local open-source molecular docking)

## 1. Exact Question

Penrose and Hameroff's Orchestrated Objective Reduction (Orch OR) hypothesis proposes that consciousness depends on quantum-coherent processes in neuronal microtubules and that general anaesthetics abolish consciousness by binding to hydrophobic pockets in αβ-tubulin rather than acting primarily on membrane ion channels (Craddock et al., 2012, *PLoS ONE* 7:e37251; Craddock et al., 2017, *Sci. Rep.* 7:9877).

This study tests the direct binding-affinity leg of that claim using open, version-pinned molecular docking (`AutoDock Vina 1.2.5` + `Open Babel 3.1.1`) across eight public protein structures:

> **Does predicted molecular docking binding affinity on αβ-tubulin (`1JFF` and high-resolution replication `4I4T`) track experimental volatile-anaesthetic potency (`−log10(MAC)`) and separate Meyer–Overton non-immobilizers (fat-soluble compounds that fail to produce anaesthesia) better than—or differently from—the same calculation on rival synaptic/ion-channel targets (`GABA_A`, `GLIC`), known non-conscious anaesthetic-binding soluble proteins (Human Serum Albumin, Firefly Luciferase), and unrelated globular negative-control proteins (Lysozyme, Ubiquitin)?**

## 2. Pre-Lock Blinding & Positive Validation

Prior to locking this protocol:
- Only structural inspection (PDB chain IDs, resolutions, missing-residue checks, and pocket centroid coordinates) and crystallographic self-redocking of four co-crystallized native ligands (`desflurane → 3P4W`, `halothane → 1E7B`, `propofol → 6X3T`, `bromoform → 1BA3`) were performed.
- All four crystallographic self-redocking controls recovered the experimental crystal binding position to within `0.28–1.31 Å` heavy-atom centroid shift under both `vina` and `vinardo` scoring functions:
  - `GLIC` (`3P4W`, desflurane `A:319`): `0.30 Å` (`vina`), `0.67 Å` (`vinardo`)
  - `GABA_A` (`6X3T`, propofol `B:601`): `0.72 Å` (`vina`), `0.28 Å` (`vinardo`)
  - `Firefly Luciferase` (`1BA3`, bromoform `A:991`): `0.38 Å` (`vina`), `0.76 Å` (`vinardo`)
  - `Human Serum Albumin` (`1E7B`, halothane `A:4003`): `1.22 Å` (`vina`), `1.31 Å` (`vinardo`)
- **Zero** dockings of the full molecule panel against tubulin, rival targets, or negative controls were run, and **zero** potency correlations or anaesthetic-vs-non-immobilizer comparisons were computed before locking.

## 3. Protein Targets and Fixed Binding-Site Boxes

All eight crystal/cryo-EM structures are downloaded directly from RCSB PDB (`https://files.rcsb.org/download/<PDB>.pdb`; SHA-256 hashes recorded in `MANIFEST.md`). For receptor preparation, only `ATOM` records belonging to the specified protein chains with alternate location `' '` or `'A'` are retained (all waters, detergents, lipids, ions, and co-crystallized ligands are removed), and protonation + PDBQT conversion are performed deterministically with `obabel <clean.pdb> -O <rec.pdbqt> -xr -p 7.4`.

Every binding site is docked with an identical **`18 × 18 × 18 Å`** cubic search box centered on coordinates fixed strictly from published residue definitions or co-crystallized ligand centroids:

| Target ID | Role | PDB | Res (Å) | Chains | Site ID | Center `(x, y, z)` Å | Site Definition |
|---|---|---|---|---|---|---|---|
| `tubulin_1jff` | **Primary Orch OR target** | `1JFF` | 3.50 | A, B | `site_1` | `(-13.09, -4.81, -0.86)` | Craddock 2012 Table 2: βC12, βV171, βV172, βP173, βV177, βD179 |
| `tubulin_1jff` | Primary Orch OR target | `1JFF` | 3.50 | A, B | `site_4` | `(11.44, -11.78, -1.97)` | Craddock 2012 Table 2: β295, βF296, βV315, βA316, βA317, βM332 |
| `tubulin_1jff` | Primary Orch OR target | `1JFF` | 3.50 | A, B | `site_5` | `(25.52, -5.34, 3.59)` | Craddock 2012 Table 3: αQ11, αA12, αI171, αV177, αS178, αT179, βQ247 |
| `tubulin_1jff` | Primary Orch OR target | `1JFF` | 3.50 | A, B | `site_7` | `(15.60, -5.03, 9.23)` | Craddock 2012 Table 2 (#1 site in Craddock 2017; colchicine-adjacent): βT240, βC241, βL248, βN249, βA354, βV355 |
| `tubulin_1jff` | Primary Orch OR target | `1JFF` | 3.50 | A, B | `site_21` | `(-9.66, -9.13, 3.69)` | Craddock 2012 Table 2: βV171, βI204, βN206, βY210, βY224, βV231 |
| `tubulin_1jff` | Primary Orch OR target | `1JFF` | 3.50 | A, B | `site_23` | `(26.45, -1.00, 9.18)` | Craddock 2012 Table 2: αQ11, αA12 |
| `tubulin_1jff` | Primary Orch OR target | `1JFF` | 3.50 | A, B | `site_37` | `(14.01, 0.64, -8.89)` | Craddock 2012 Table 3: αM398, βN258, βP261, βL313 |
| `tubulin_1jff` | Primary Orch OR target | `1JFF` | 3.50 | A, B | `site_38` | `(15.80, -0.07, -2.17)` | Craddock 2012 Table 3 (colchicine-adjacent): αA180, αV181, βK254, βV257, βT314 |
| `tubulin_4i4t` | **Replication tubulin (high-res)** | `4I4T` | 1.80 | A, B | `site_1` | `(12.86, 47.46, 23.42)` | Identical Craddock 2012 residue set mapped onto `4I4T` A/B |
| `tubulin_4i4t` | Replication tubulin | `4I4T` | 1.80 | A, B | `site_4` | `(7.52, 60.88, 44.05)` | Same as `1JFF` `site_4` |
| `tubulin_4i4t` | Replication tubulin | `4I4T` | 1.80 | A, B | `site_5` | `(19.26, 75.92, 50.13)` | Same as `1JFF` `site_5` |
| `tubulin_4i4t` | Replication tubulin | `4I4T` | 1.80 | A, B | `site_7` | `(13.07, 69.85, 40.09)` | Same as `1JFF` `site_7` |
| `tubulin_4i4t` | Replication tubulin | `4I4T` | 1.80 | A, B | `site_21` | `(8.71, 51.05, 24.30)` | Same as `1JFF` `site_21` |
| `tubulin_4i4t` | Replication tubulin | `4I4T` | 1.80 | A, B | `site_23` | `(22.91, 79.83, 48.48)` | Same as `1JFF` `site_23` |
| `tubulin_4i4t` | Replication tubulin | `4I4T` | 1.80 | A, B | `site_37` | `(21.29, 57.31, 48.74)` | Same as `1JFF` `site_37` |
| `tubulin_4i4t` | Replication tubulin | `4I4T` | 1.80 | A, B | `site_38` | `(21.87, 64.63, 45.84)` | Same as `1JFF` `site_38` |
| `gabaa_6x3t` | **Rival synaptic receptor** | `6X3T` | 2.55 | A–E | `site_B601` | `(134.05, 120.75, 156.36)` | Co-crystallized propofol `PFL B:601` (β2+/α1− TMD pocket 1; Kim et al. 2020) |
| `gabaa_6x3t` | Rival synaptic receptor | `6X3T` | 2.55 | A–E | `site_D601` | `(110.13, 136.34, 141.96)` | Co-crystallized propofol `PFL D:601` (β2+/α1− TMD pocket 2; Kim et al. 2020) |
| `glic_3p4w` | **Rival pentameric channel** | `3P4W` | 3.20 | A–E | `site_A319` | `(46.87, -8.76, 45.36)` | Co-crystallized desflurane `DSF A:319` (TMD anesthetic cavity; Nury et al. 2011) |
| `hsa_1e7b` | **Positive non-conscious control** | `1E7B` | 2.38 | A | `site_4003` | `(10.88, 3.29, -12.49)` | Co-crystallized halothane `HLT A:4003` (subdomain IIIA; Bhattacharya et al. 2000) |
| `hsa_1e7b` | Positive non-conscious control | `1E7B` | 2.38 | A | `site_4001_4002` | `(0.25, -20.40, -6.97)` | Midpoint of co-crystallized `HLT A:4001` & `A:4002` (subdomain IIA) |
| `luciferase_1ba3` | **Positive non-conscious control** | `1BA3` | 2.20 | A | `site_991` | `(16.58, 82.65, 48.82)` | Co-crystallized inner bromoform `MBR A:991` (luciferin pocket; Franks et al. 1998) |
| `lysozyme_1dpx` | **Negative globular control** | `1DPX` | 1.65 | A | `site_cleft` | `(2.99, 20.60, 25.68)` | Active-site cleft centroid: GLU35, ASP52, TRP62, TRP63, TRP108 |
| `ubiquitin_1ubq` | **Negative globular control** | `1UBQ` | 1.80 | A | `site_patch` | `(27.09, 35.30, 20.28)` | Hydrophobic patch centroid: LEU8, ILE44, HIS68, VAL70 |

For multi-pocket targets (`tubulin_1jff`, `tubulin_4i4t`, `gabaa_6x3t`, `hsa_1e7b`), we compute and report three target-level affinity summaries for every ligand:
1. **Best-pocket affinity (`B_best = max_k (−ΔG_k)`):** Primary target-level summary representing the strongest binding pocket available on the protein.
2. **Primary single-pocket affinity (`B_single`):** Strict 1-pocket-to-1-pocket comparison controlling for multi-pocket selection (`site_7` for `1JFF`/`4I4T`, `site_B601` for `6X3T`, `site_4003` for `1E7B`, and the single pocket on `3P4W`, `1BA3`, `1DPX`, `1UBQ`).
3. **Boltzmann ensemble affinity (`B_ens = RT ln((1/K) Σ_k exp(−ΔG_k / RT))` at `T = 310 K`, `RT = 0.6160 kcal/mol`):** Sensitivity summary across all docked pockets.

## 4. Molecule Panel (Fixed Before Docking)

All canonical SMILES and PubChem CIDs were verified directly from PubChem PUG REST API prior to locking. Every `MAC` (in atmospheres, `atm`) and olive-oil/gas partition coefficient (`λ_oil` at 37 °C) comes from primary peer-reviewed literature read directly in full text:
- **Subset A — Clinical volatile anaesthetics (`n = 9`):** Craddock et al. (2017, *Sci. Rep.* 7:9877, Supplementary Table S1) plus trichloroethylene (BJA 1986; Update in Anaesthesia Table 1).
- **Subset B — Experimental aromatic & cycloalkane volatile anaesthetics (`n = 18`):** Fang et al. (1996, *Anesth. Analg.* 83:1097–1104, Tables 4–5) and Liu et al. (1994, cited in Fang 1996 Table 5 for n-hexane).
- **Confirmed Meyer–Overton Non-Immobilizers (`n = 7`):** Compounds with substantial lipophilicity that fail to produce immobility or lower desflurane MAC in vivo (Koblin et al. 1994, *Anesth. Analg.* 79:1043–1048 [PubMed abstract]; Fang et al. 1996 Tables 2 & 5; Steffey et al. 1998, *Anesth. Analg.* 86:145–150 [Ovid full excerpt]; Craddock et al. 2017 Table S1). Five of the seven (`F6`, `F8`, `TFMB`, `cyclooctane`, `perfluoropentane`) have exact verified `λ_oil`; all seven have exact heavy-atom counts (`N_heavy`) and PubChem `XLogP3`.
- **Annotated transitional convulsant (`n = 1`):** `flurothyl` (Craddock et al. 2017 Table S1) — docked and reported descriptively, excluded from primary potency regression and binary anaesthetic-vs-non-immobilizer tests.

| ID | Class | Subset | PubChem CID | SMILES | `MAC` (atm) | `λ_oil` (37°C) | `N_heavy` | `XLogP` | Source |
|---|---|---|---|---|---:|---:|---:|---:|---|
| `methoxyflurane` | anaesthetic | clinical | 4116 | `COC(C(Cl)Cl)(F)F` | 0.00160 | 960.0 | 8 | 2.2 | Craddock 2017 S1 |
| `trichloroethylene` | anaesthetic | clinical | 6575 | `C(=C(Cl)Cl)Cl` | 0.00170 | 960.0 | 5 | 2.6 | BJA 1986 / UiA |
| `halothane` | anaesthetic | clinical | 3562 | `C(C(F)(F)F)(Cl)Br` | 0.00770 | 224.0 | 7 | 2.3 | Craddock 2017 S1 |
| `isoflurane` | anaesthetic | clinical | 3763 | `C(C(F)(F)F)(OC(F)F)Cl` | 0.01200 | 96.0 | 10 | 2.1 | Craddock 2017 S1 |
| `enflurane` | anaesthetic | clinical | 3226 | `C(C(OC(F)F)(F)F)(F)Cl` | 0.01700 | 98.0 | 10 | 2.1 | Craddock 2017 S1 |
| `diethyl_ether` | anaesthetic | clinical | 3283 | `CCOCC` | 0.01900 | 65.0 | 5 | 0.9 | Craddock 2017 S1 |
| `sevoflurane` | anaesthetic | clinical | 5206 | `C(OC(C(F)(F)F)C(F)(F)F)F` | 0.02000 | 53.0 | 12 | 2.8 | Craddock 2017 S1 |
| `desflurane` | anaesthetic | clinical | 42113 | `C(C(F)(F)F)(OC(F)F)F` | 0.06000 | 19.0 | 10 | 2.6 | Craddock 2017 S1 |
| `nitrous_oxide` | anaesthetic | clinical | 948 | `[N-]=[N+]=O` | 1.01000 | 0.39 | 3 | 0.5 | Craddock 2017 S1 |
| `o_xylene` | anaesthetic | fang1996 | 7237 | `CC1=CC=CC=C1C` | 0.00118 | 10800.0 | 8 | 3.1 | Fang 1996 T4–T5 |
| `ethylbenzene` | anaesthetic | fang1996 | 7500 | `CCC1=CC=CC=C1` | 0.00121 | 5450.0 | 8 | 3.1 | Fang 1996 T4–T5 |
| `m_xylene` | anaesthetic | fang1996 | 7929 | `CC1=CC(=CC=C1)C` | 0.00139 | 7780.0 | 8 | 3.2 | Fang 1996 T4–T5 |
| `p_xylene` | anaesthetic | fang1996 | 7809 | `CC1=CC=C(C=C1)C` | 0.00151 | 6300.0 | 8 | 3.2 | Fang 1996 T4–T5 |
| `toluene` | anaesthetic | fang1996 | 1140 | `CC1=CC=CC=C1` | 0.00450 | 2170.0 | 7 | 2.7 | Fang 1996 T4–T5 |
| `o_difluorobenzene` | anaesthetic | fang1996 | 9706 | `C1=CC=C(C(=C1)F)F` | 0.00610 | 853.0 | 8 | 2.4 | Fang 1996 T4–T5 |
| `p_difluorobenzene` | anaesthetic | fang1996 | 10892 | `C1=CC(=CC=C1F)F` | 0.00640 | 654.0 | 8 | 2.2 | Fang 1996 T4–T5 |
| `methylpentafluorobenzene` | anaesthetic | fang1996 | 69869 | `CC1=C(C(=C(C(=C1F)F)F)F)F` | 0.00640 | 1470.0 | 12 | 2.8 | Fang 1996 T4–T5 |
| `124_trifluorobenzene` | anaesthetic | fang1996 | 67773 | `C1=CC(=C(C=C1F)F)F` | 0.00970 | 621.0 | 9 | 2.4 | Fang 1996 T4–T5 |
| `benzene` | anaesthetic | fang1996 | 241 | `C1=CC=CC=C1` | 0.01010 | 565.0 | 6 | 2.1 | Fang 1996 T4–T5 |
| `fluorobenzene` | anaesthetic | fang1996 | 10008 | `C1=CC=C(C=C1)F` | 0.01120 | 661.0 | 7 | 2.3 | Fang 1996 T4–T5 |
| `pentafluorobenzene` | anaesthetic | fang1996 | 9696 | `C1=C(C(=C(C(=C1F)F)F)F)F` | 0.01250 | 393.0 | 11 | 2.5 | Fang 1996 T4–T5 |
| `cycloheptane` | anaesthetic | fang1996 | 9265 | `C1CCCCCC1` | 0.01370 | 2780.0 | 7 | 4.0 | Fang 1996 T4–T5 |
| `hexafluorobenzene` | anaesthetic | fang1996 | 9805 | `C1(=C(C(=C(C(=C1F)F)F)F)F)F` | 0.01610 | 251.0 | 12 | 2.5 | Fang 1996 T4–T5 |
| `135_trifluorobenzene` | anaesthetic | fang1996 | 9745 | `C1=C(C=C(C=C1F)F)F` | 0.02220 | 335.0 | 9 | 2.2 | Fang 1996 T4–T5 |
| `n_hexane` | anaesthetic | fang1996 | 8058 | `CCCCCC` | 0.03500 | 148.0 | 6 | 3.9 | Liu 1994 / Fang 1996 T5 |
| `cyclohexane` | anaesthetic | fang1996 | 8078 | `C1CCCCC1` | 0.04200 | 385.0 | 6 | 3.4 | Fang 1996 T4–T5 |
| `cyclopentane` | anaesthetic | fang1996 | 9253 | `C1CCCC1` | 0.05300 | 139.0 | 5 | 3.0 | Fang 1996 T4–T5 |
| `F6` | non_immobilizer | non_imm | 9643 | `C1(C(C(C1(F)Cl)(F)Cl)(F)F)(F)F` | — | 43.5 | 12 | 3.2 | Koblin 1994 / Steffey 1998 |
| `F8` | non_immobilizer | non_imm | 78982 | `C(C(C(F)(F)F)(F)Cl)(C(F)(F)F)(F)Cl` | — | 25.0 | 14 | 4.3 | Koblin 1994 / Steffey 1998 |
| `TFMB` | non_immobilizer | non_imm | 123085 | `C1=C(C=C(C=C1C(F)(F)F)C(F)(F)F)C(F)(F)F` | — | 264.0 | 18 | 4.6 | Fang 1996 T2, T5 |
| `cyclooctane` | non_immobilizer | non_imm | 9266 | `C1CCCCCCC1` | — | 7010.0 | 8 | 4.5 | Fang 1996 T2, T5 |
| `perfluoropentane` | non_immobilizer | non_imm | 12675 | `C(C(C(F)(F)F)(F)F)(C(C(F)(F)F)(F)F)(F)F` | — | 0.662 | 17 | 4.5 | Liu 1994 / Steffey 1998 |
| `perfluorocyclobutane` | non_immobilizer | non_imm | 8263 | `C1(C(C(C1(F)F)(F)F)(F)F)(F)F` | — | — | 12 | 1.6 | Koblin 1994 |
| `CF3CClFCF3` | non_immobilizer | non_imm | 66156 | `C(C(F)(F)F)(C(F)(F)F)(F)Cl` | — | — | 11 | 3.4 | Koblin 1994 |
| `flurothyl` | convulsant | annotated | 9528 | `C(C(F)(F)F)OCC(F)(F)F` | — | 47.0 | 11 | 2.3 | Craddock 2017 S1 |

## 5. Docking Procedure (Pinned Software & Parameters)

- **Software (version-pinned):**
  - `AutoDock Vina v1.2.5` (Ubuntu 24.04 package `autodock-vina 1.2.5-2build1`)
  - `Open Babel 3.1.1` (Ubuntu 24.04 package `openbabel 3.1.1+dfsg-9ubuntu5`)
  - `Python 3.12.16`, `NumPy` (pure-NumPy statistical routines; no unpinned external statistics libraries)
- **Ligand preparation:** Each SMILES is converted deterministically to a 3D minimized SDF via `obabel -:<SMILES> -O <lig>.sdf --gen3d --best` and then to PDBQT via `obabel <lig>.sdf -O <lig>.pdbqt`.
- **Docking parameters:**
  - Search box: `18 × 18 × 18 Å` centered on the exact fixed coordinates in Section 3.
  - Exhaustiveness: `16`
  - Fixed random seed: `20261123`
  - Scoring functions: **`vina`** (primary) and **`vinardo`** (pre-registered robustness check, identical command with `--scoring vinardo`).
  - Batch execution: `vina --receptor <rec.pdbqt> --batch <lig_1.pdbqt> ... <lig_35.pdbqt> --dir <out_dir> --center_x ... --size_x 18 --size_y 18 --size_z 18 --scoring <sf> --exhaustiveness 16 --seed 20261123 --cpu 2`.
  - Best-mode binding affinity `ΔG` (kcal/mol) is parsed from `REMARK VINA RESULT:` of `MODEL 1` in each output PDBQT.

## 6. Statistical Analysis Plan

Define binding strength `B = −ΔG` (kcal/mol; larger positive values mean stronger predicted binding) and clinical potency `P = −log10(MAC_atm)` (larger values mean higher potency). All tests are evaluated on the **primary scoring function (`vina`)** and repeated on **`vinardo`**, across the **full volatile panel (`n = 27` anaesthetics, `n = 7` non-immobilizers)** and separately on the **clinical-only subset (`n = 9` clinical anaesthetics, `n = 7` non-immobilizers)**.

1. **Potency tracking (within true anaesthetics, `n = 27` primary; `n = 9` clinical sensitivity):**
   - Spearman rank correlation `ρ_pot = corr_rank(B, P)` and Pearson `r_pot = corr(B, P)`.
   - Two-sided exact permutation p-value (`10,000` random permutations, RNG seed `20261123`) and `B = 5,000` bootstrap 95% confidence interval.
   - **Confound-adjusted partial Spearman correlations:**
     - `ρ_partial_heavy`: rank correlation between residuals of `rank(B) ~ rank(N_heavy)` and `rank(P) ~ rank(N_heavy)` (tests whether docking tracks potency beyond trivial heavy-atom count / molecular size).
     - `ρ_partial_oil`: rank correlation controlling for `rank(log10(λ_oil))` (tests whether docking explains potency variance beyond the Meyer–Overton olive-oil partition coefficient).
     - `ρ_partial_xlogp`: rank correlation controlling for `rank(XLogP)` (sensitivity check).

2. **Non-anaesthetic (non-immobilizer) separation:**
   - **Raw separation (`AUC_sep`, `ΔB_raw`):** ROC AUC = `P(B_anaes > B_non) + 0.5 P(B_anaes == B_non)` across `n = 27` anaesthetics vs `n = 7` non-immobilizers (`AUC > 0.5` means anaesthetics bind stronger than non-immobilizers; `AUC < 0.5` means non-immobilizers bind stronger than anaesthetics), with two-sided permutation p-value (`10,000` label shuffles) and `ΔB_raw = median(B_anaes) − median(B_non)` (kcal/mol).
   - **Lipophilicity-adjusted non-immobilizer residual (`r_non_oil`, `n = 5` non-immobilizers with measured `λ_oil`):** Fit OLS `B ~ log10(λ_oil)` on the `n = 27` true anaesthetics alone, compute residuals `e_i = B_i − B_hat(λ_oil,i)` for all 32 compounds with `λ_oil`, and test whether `mean(e_non) < 0` (non-immobilizers bind weaker than predicted from their fat solubility; two-sided permutation p-value over `10,000` shuffles of `e_i`).
   - **Size-adjusted non-immobilizer residual (`r_non_heavy`, all `n = 7` non-immobilizers):** Fit OLS `B ~ N_heavy` on the `n = 27` true anaesthetics alone, compute residuals `e_i = B_i − B_hat(N_heavy,i)` for all 34 compounds, and test whether `mean(e_non) < 0` (non-immobilizers bind weaker than anaesthetics of the same heavy-atom count; two-sided permutation p-value).

3. **Target specificity (Tubulin vs. Rivals and Controls):**
   - Paired bootstrap (`B = 5,000` resamples of molecules with replacement, stratified by class `[27 anaesthetics, 7 non-immobilizers]`, seed `20261123`) computing 95% confidence intervals for:
     - `Δρ_pot(T1 − T2) = ρ_pot(T1) − ρ_pot(T2)`
     - `ΔAUC_sep(T1 − T2) = AUC_sep(T1) − AUC_sep(T2)`
     - `Δr_non_oil(T1 − T2) = (−r_non_oil(T1)) − (−r_non_oil(T2))` (positive means `T1` rejects non-immobilizers more strongly than `T2`)
   - Evaluated for both `B_best` (multi-pocket best site) and `B_single` (strict 1-pocket comparison: `tubulin_1jff:site_7` vs single pocket on each comparator).

4. **Physical & Methodological Diagnostics (reported descriptively):**
   - Per-site breakdown across all 8 Craddock tubulin sites on `1JFF` and `4I4T`.
   - Comparison against Craddock et al. (2017) Table S2 MOE scores on the overlapping 11-compound set.
   - Correlation of `B` with `N_heavy`, `MW`, and `XLogP` on every target to quantify docking's intrinsic size/hydrophobicity bias.

## 7. Pre-Registered Verdict Rule

Evaluated on the primary `vina` scoring function (`n = 27` anaesthetics, `n = 7` non-immobilizers) with `tubulin_1jff` primary and `tubulin_4i4t` + `vinardo` as pre-registered replication/robustness checks:

1. **`tubulin_selective`** (supports selective microtubule targeting):
   - `tubulin_1jff` (`B_best` AND replicated on `tubulin_4i4t`) shows significant positive potency tracking (`ρ_pot > 0`, permutation `p < 0.05`) **AND** genuine non-immobilizer rejection (`AUC_sep > 0.65` with `p < 0.05`, OR `r_non_oil < 0` with `p < 0.05`), **AND** significantly outperforms both negative controls (`lysozyme_1dpx`, `ubiquitin_1ubq`) and both non-conscious soluble controls (`hsa_1e7b`, `luciferase_1ba3`) on `Δρ_pot` or `ΔAUC_sep` (paired bootstrap 95% CI strictly `> 0`), while matching or exceeding `gabaa_6x3t` and `glic_3p4w`.
2. **`generic_hydrophobic_binding`** (binding tracks potency/size generically across proteins, with no tubulin specificity):
   - `tubulin_1jff` shows positive potency correlation (`ρ_pot > 0`, `p < 0.05`), **AND** its potency tracking and non-immobilizer separation do **not** significantly exceed the non-conscious soluble controls (`hsa_1e7b`, `luciferase_1ba3`) or negative globular controls (`lysozyme_1dpx`, `ubiquitin_1ubq`) (paired bootstrap 95% CIs include `0` or favor controls), **OR** non-immobilizers fail to bind weaker than anaesthetics (`AUC_sep ≤ 0.55` and `r_non_oil ≥ 0`).
3. **`no_potency_or_selectivity`** (docking on tubulin fails to track potency and fails to separate non-immobilizers):
   - `tubulin_1jff` (`B_best`) fails to achieve significant positive potency tracking (`ρ_pot ≤ 0` or `p ≥ 0.05`) **AND** fails to reject non-immobilizers (`AUC_sep ≤ 0.55` and `r_non_oil ≥ 0` or `p ≥ 0.05`).
4. **`mixed_or_scoring_dependent`**:
   - Primary and replication targets (`1JFF` vs `4I4T`) or primary and secondary scoring functions (`vina` vs `vinardo`) yield qualitatively opposite outcomes, or tubulin satisfies potency tracking and control superiority without non-immobilizer separation (or vice versa).

## 8. Known Limits (Declared Before Running)

- **Rigid-receptor docking:** AutoDock Vina treats protein side chains and backbone as rigid crystal/cryo-EM snapshots; induced-fit pocket expansion, protein dynamics, and water-bridge displacement are not modeled.
- **Empirical scoring bias:** Empirical docking functions (`vina`, `vinardo`) are additive over heavy-atom contacts and typically correlate with ligand molecular weight / surface area; perfluorinated non-immobilizers (`F6`, `F8`, `TFMB`, `perfluoropentane`) have high heavy-atom counts, which makes the size-adjusted and lipophilicity-adjusted residual tests essential.
- **Binding energy vs. functional efficacy / THz dipole shifts:** Docking estimates equilibrium pocket affinity (`ΔG`), not downstream channel gating (`GABA_A`), microtubule polymerization dynamics, or Craddock et al. (2017)'s aromatic-network THz polarizability shift model. A null or generic docking result rules out *affinity-based selectivity* in standard docking, not every possible post-binding mechanism.
- **Single-species `MAC` compilation:** Clinical volatile `MAC` values (Subset A) are standard human values (Craddock 2017 Table S1), while experimental aromatics/cycloalkanes (Subset B) are rat `MAC` values (Fang et al. 1996); both subsets are analyzed pooled and separately (`clinical` vs `fang1996`) to verify no species-mixing artifact.
