# Data & Software Manifest — `anaesthetics-microtubules`

All downloaded structures live in `questions/anaesthetics-microtubules/data/` (git-ignored) and can be reproduced verbatim from the public URLs below.

## 1. Protein Structures (RCSB Protein Data Bank)

Retrieved on **2026-11-23** from RCSB PDB (`CC0 1.0 Universal Public Domain Dedication`).

| Local Path | PDB ID | Protein & Role | Resolution | Source URL | SHA-256 |
|---|---|---|---:|---|---|
| `data/pdb/1JFF.pdb` | `1JFF` | Bovine αβ-tubulin dimer (Orch OR primary target; Löwe et al. 2001) | 3.50 Å | `https://files.rcsb.org/download/1JFF.pdb` | `8fcc2ee63f39ee86e7854128e9b2251bedc78e4cc552ab6ac6180c3a0b9e6798` |
| `data/pdb/4I4T.pdb` | `4I4T` | Mammalian αβ-tubulin complex (high-res replication target; Prota et al. 2013) | 1.80 Å | `https://files.rcsb.org/download/4I4T.pdb` | `b9ddfc0829b183e5b09b5ff0ff3a6a0deced432109e9104ee631140abee4b964` |
| `data/pdb/6X3T.pdb` | `6X3T` | Human `GABA_A` α1β2γ2 + GABA + propofol (rival synaptic receptor; Kim et al. 2020) | 2.55 Å | `https://files.rcsb.org/download/6X3T.pdb` | `a28d55a230662ffb08a4207b8f82f511409017ea888480bbb9bbb75465c9ac19` |
| `data/pdb/3P4W.pdb` | `3P4W` | `GLIC` pentameric ion channel + desflurane (rival channel; Nury et al. 2011) | 3.20 Å | `https://files.rcsb.org/download/3P4W.pdb` | `945f25ee0f220bbecaa924178b9503f8b0f2432b7250d27f58c77199f99024b0` |
| `data/pdb/1E7B.pdb` | `1E7B` | Human Serum Albumin + halothane (positive non-conscious control; Bhattacharya et al. 2000) | 2.38 Å | `https://files.rcsb.org/download/1E7B.pdb` | `4cea6a1ab2bf589e4311906c6837170d1fa2307b2933ee8b683b00737b0d8565` |
| `data/pdb/1BA3.pdb` | `1BA3` | Firefly Luciferase + bromoform (positive non-conscious control; Franks et al. 1998) | 2.20 Å | `https://files.rcsb.org/download/1BA3.pdb` | `a304920ee2ad14ce94511d5ce711d5ffb07b5d37ab6fd1bfa2b76bfb75e7f1de` |
| `data/pdb/1DPX.pdb` | `1DPX` | Hen Egg-White Lysozyme (negative globular control) | 1.65 Å | `https://files.rcsb.org/download/1DPX.pdb` | `00582ec39810fe609df85ae65a3c7a61af3b9b39a0472a72caf194918a5c7ef3` |
| `data/pdb/1UBQ.pdb` | `1UBQ` | Human Ubiquitin (negative globular control) | 1.80 Å | `https://files.rcsb.org/download/1UBQ.pdb` | `d4a6812d8951cf6594e6a0763f089e35f5a80b62acb3c117b2c5565228a7b161` |

## 2. Primary Literature & Chemical Structure Tables

- **Craddock et al. (2017) Supplementary Information (`data/craddock2017_esm.doc`):**
  - Source URL: `https://static-content.springer.com/esm/art%3A10.1038%2Fs41598-017-09992-7/MediaObjects/41598_2017_9992_MOESM1_ESM.doc`
  - Retrieved: `2026-11-23`
  - Licence: `CC BY 4.0` (*Scientific Reports* 7:9877, `PMC5575257`)
  - SHA-256: `43df0622ee056598f71357378ee2794f76b01a66b07d95f69e28284ada9b48fc`
- **Craddock et al. (2012, *PLoS ONE* 7(6):e37251, `PMC3382613`):**
  - Source URL: `https://pmc.ncbi.nlm.nih.gov/articles/PMC3382613/` (CC BY 4.0; Tables 2 & 3 tubulin site residue definitions).
- **Fang et al. (1996, *Anesth. Analg.* 83:1097–1104):**
  - Full-text PDF inspected directly (Tables 1–5) for rat `MAC` and 37 °C olive-oil/gas partition coefficients of 18 volatile aromatic/cycloalkane anaesthetics and 2 non-immobilizers (`1,3,5-tris(trifluoromethyl)benzene`, `cyclooctane`).
- **Koblin et al. (1994, *Anesth. Analg.* 79:1043–1048, PubMed `7978424`) & Steffey et al. (1998, *Anesth. Analg.* 86:145–150):**
  - Non-immobilizer classification and olive-oil/gas partition coefficients (`F6` = 43.5, `F8` = 25, `perfluoropentane` = 0.662, `perfluorocyclobutane`, `CF3CClFCF3`).
- **PubChem Compound Database (`https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/...`, NIH Public Domain):**
  - Retrieved `2026-11-23` for canonical SMILES, molecular weights, heavy-atom counts, and `XLogP3` values of all 35 panel compounds (CIDs recorded inline in `protocol.md` and `analysis/dock_anaesthetics.py`).

## 3. Pinned Software & Pre-Lock Code Hashes

- **AutoDock Vina:** `AutoDock Vina v1.2.5` (Ubuntu 24.04 package `autodock-vina 1.2.5-2build1`, Apache-2.0)
- **Open Babel:** `Open Babel 3.1.1` (Ubuntu 24.04 package `openbabel 3.1.1+dfsg-9ubuntu5`, GPL-2.0)
- **Python:** `Python 3.12.16` with `NumPy`

| Analysis Script | SHA-256 (Pre-Lock) |
|---|---|
| `analysis/dock_anaesthetics.py` | `3f4046e350a7c010a696e236c26952120dbb767abb86fc4870834c776fa048c6` |
| `analysis/test_docking.py` | `8932ad71442a2fbc598e5acadc289ed687c4cbccaaf3ab24668042f723e3db90` |
