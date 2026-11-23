---
# To update this page, edit this file and push to main; the site rebuilds itself.
# The panels and interactive figures are made by questions/anaesthetics-microtubules/analysis/make_figures.py from the results files.
summary: One theory of consciousness proposes that general anaesthetics put the brain under by acting on microtubules inside nerve cells rather than on ion channels. Does molecular docking of real anaesthetics and look-alike non-anaesthetics single out microtubules?
verdict: Standard molecular docking finds no tubulin signal. Non-anaesthetics bind tighter than real drugs, and an unrelated control protein beats tubulin
result: Across 1,680 dockings of 35 volatile gases onto eight proteins, predicted binding to microtubule tubulin neither tracks clinical potency nor rejects fat-soluble gases that fail to cause anaesthesia. Bulky fluorinated non-anaesthetics score tighter than real drugs on almost every protein because docking rewards heavy-atom count, and even after correcting for size or switching scoring functions, tubulin shows no advantage over ion channels, soluble bystander proteins or ubiquitin. Rigid docking cannot test what a drug does after it lands in a pocket, so post-binding effects remain separate, but docking itself does not pick out microtubules.
dek: General anaesthesia switches consciousness off cleanly and reversibly, yet how the drugs do it is still argued over. Most neuroscientists point to ion channels at synapses; the Orch OR theory points to hydrophobic pockets inside the cell's microtubule scaffolding. We docked 27 volatile anaesthetics and 7 fat-soluble non-anaesthetics into tubulin and seven comparison proteins, with the rules fixed before looking at the scores.
updated: 2026-11-23
---

> **Where things stand, 23 November 2026.** Run and written up; awaiting independent replication by a second AI system from the locked plan. Under open molecular docking, microtubule tubulin fails to track anaesthetic potency, fails to reject non-anaesthetics, and is outperformed by an unrelated control protein (ubiquitin).

## What we figured out {menu: Findings}

For more than a century, anaesthesiologists have known a strange rule: the more easily a volatile gas dissolves in olive oil, the smaller the dose needed to put a patient under. Yet a small family of fat-soluble fluorinated gases breaks that rule completely. They dissolve in oil just fine, reach the brain, and still do not cause anaesthesia. Any serious target for general anaesthesia has to do two things: bind stronger anaesthetics more readily than weaker ones, and treat those look-alike "non-immobilizers" differently.

Roger Penrose and Stuart Hameroff's Orch OR theory proposes that the crucial target is not an ion channel at the synapse, but αβ-tubulin — the protein brick that builds microtubules inside nerve cells. Prior computational work (Craddock et al. 2012, 2017) mapped eight pockets on tubulin and docked volatile gases into them. We asked a simpler, head-to-head question: **if you run the exact same open docking pipeline on tubulin and seven comparison proteins — two classic ion-channel targets (`GABA_A` and `GLIC`), two non-conscious soluble proteins known to bind anaesthetics (`Albumin` and `Firefly Luciferase`), and two unrelated bystander proteins (`Lysozyme` and `Ubiquitin`) — does tubulin stand out?**

{{figure: anaesthetics-microtubules/tiles}}

Five things came out.

1. **Predicted binding on tubulin does not track how strong an anaesthetic is.** Across 27 volatile anaesthetics (9 familiar clinical gases plus 18 aromatic and cycloalkane gases tested in rats by Fang et al. 1996), primary tubulin (`1JFF`) gives a weak, non-significant correlation with potency (`ρ = +0.29`, `p = 0.146`). A higher-resolution tubulin crystal (`4I4T`, 1.80 Å) gives `ρ = +0.35` (`p = 0.074`), and an alternative scoring function (`Vinardo`) on `1JFF` gives `ρ = +0.28` (`p = 0.151`). Restricting tubulin to its single most-cited pocket (`site 7`) drops the correlation to `ρ = +0.12`.
2. **Non-anaesthetics actually score tighter than real anaesthetics on almost every protein.** On tubulin (`1JFF`), the seven confirmed non-immobilizers bind with a median affinity of `6.05 kcal/mol`, tighter than the `5.50 kcal/mol` median of the 27 real anaesthetics (`AUC = 0.21`, where `0.50` is a coin flip and values below `0.50` mean non-anaesthetics bind tighter). The same inversion appears on high-resolution tubulin (`AUC = 0.08`), `GABA_A` (`0.08`), Albumin (`0.09`), Luciferase (`0.12`), and Lysozyme (`0.17`).
3. **Heavy-atom size bias drives the whole show.** Under `AutoDock Vina`, predicted binding strength correlates at `ρ = +0.79` to `+0.97` with the number of heavy atoms in the gas across seven of the eight proteins. Bulky fluorinated non-immobilizers such as `TFMB` (18 heavy atoms, `8.27 kcal/mol` on tubulin) and `perfluoropentane` (17 heavy atoms) pack more atoms into a rigid cavity than compact clinical drugs like halothane (7 heavy atoms) or nitrous oxide (3 heavy atoms). Even on the 9 clinical anaesthetics alone, *none* of the eight proteins tracks clinical potency — reproducing Craddock et al. (2017)'s own published `MOE` docking scores (`ρ = +0.05` across their 8 anaesthetics; our `Vina` scores correlate with their `MOE` scores at `ρ = +0.89`).
4. **Tubulin has no edge over rival channels or bystander proteins.** Even after removing heavy-atom size bias (`ρ = +0.44` on `1JFF`), tubulin is beaten by `GABA_A` (`+0.55`), `GLIC` (`+0.53`), and negative-control **Ubiquitin** (`+0.52`), and is statistically indistinguishable from non-conscious Albumin (`+0.37`) and Luciferase (`+0.31`). Under `Vinardo` (which reduces size bias), Ubiquitin — a tiny 76-residue protein with no role in consciousness or anaesthesia — finishes first overall on both potency (`ρ = +0.60`, `p = 0.002`) and non-immobilizer separation (`AUC = 0.79`, `p = 0.015`).
5. **Rigid docking also misses what makes `GABA_A` special, and that is a finding too.** Classic ion channels failed to reject non-immobilizers under rigid docking just as tubulin did. That points straight to the limit of the method: docking measures whether a small greasy molecule fits into a pocket, not whether it props a channel gate open or triggers a collective change once inside.

{{figure: anaesthetics-microtubules/verdict}}

## Explore each protein yourself {menu: Target explorer}

Pick any of the eight proteins below, switch between the `Vina` and `Vinardo` scoring functions, or change the horizontal axis from anaesthetic potency to olive-oil solubility or heavy-atom count. Notice how tightly the points line up once you switch the axis to **Heavy atoms**, and how the red diamonds (non-immobilizers) sit *above* the gold circles (real anaesthetics) on almost every target.

{{figure: anaesthetics-microtubules/potency}}

## All eight proteins, side by side {menu: All eight proteins}

The scorecard and molecule-by-molecule matrix below line up all 35 compounds across all eight proteins. Click any column header to sort, or switch between raw binding strength and size-adjusted residuals.

{{figure: anaesthetics-microtubules/matrix}}

| Protein (PDB) | Role | Vina Potency `ρ` (`p`) | Vina `ρ` after size (`p`) | Vina Non-Imm `AUC` | Vinardo Potency `ρ` (`p`) | Vinardo Non-Imm `AUC` |
|---|---|---:|---:|---:|---:|---:|
| **Tubulin (`1JFF`, 8 sites)** | Primary Orch OR target | `+0.29` (`0.146`) | `+0.44` (`0.027`) | `0.21` | `+0.28` (`0.151`) | `0.46` |
| **Tubulin (`4I4T`, 1.80 Å)** | High-res replication | `+0.35` (`0.074`) | `+0.44` (`0.023`) | `0.08` | `+0.50` (`0.008`) | `0.27` |
| **`GABA_A` (`6X3T`, 2 sites)** | Rival ion channel | `+0.42` (`0.030`) | `+0.55` (`0.004`) | `0.08` | `+0.57` (`0.003`) | `0.27` |
| **`GLIC` (`3P4W`, 1 site)** | Rival ion channel | `+0.38` (`0.050`) | `+0.53` (`0.003`) | `0.30` | `+0.35` (`0.073`) | `0.58` |
| **Albumin (`1E7B`, 2 sites)** | Non-conscious soluble control | `+0.28` (`0.153`) | `+0.37` (`0.054`) | `0.09` | `+0.51` (`0.007`) | `0.27` |
| **Luciferase (`1BA3`, 1 site)** | Non-conscious soluble control | `+0.21` (`0.290`) | `+0.31` (`0.116`) | `0.12` | `+0.50` (`0.008`) | `0.28` |
| **Lysozyme (`1DPX`, 1 site)** | Negative control | `+0.10` (`0.623`) | `−0.02` (`0.942`) | `0.17` | `+0.13` (`0.527`) | `0.34` |
| **Ubiquitin (`1UBQ`, 1 site)** | Negative control | **`+0.51` (`0.006`)** | **`+0.52` (`0.009`)** | `0.46` | **`+0.60` (`0.002`)** | **`0.79`** |

Splitting the 27 anaesthetics into the two source groups shows what is going on underneath. On the **9 clinical gases alone**, *none* of the eight proteins tracks potency (`1JFF` `ρ = −0.13`, `GABA_A` `−0.07`, `GLIC` `+0.03`). On the **18 homologous aromatic and cycloalkane gases** from Fang et al. (1996), *every single protein* tracks potency under `Vinardo` (`ρ = +0.64` to `+0.88`), including Lysozyme (`+0.77`) and Ubiquitin (`+0.85`). A generic greasy pocket picks up the aromatic series on almost any protein, and misses the clinical gases on all of them.

## Inside the binding pockets {menu: Inside the pockets}

Drag to rotate the docked 3D poses inside representative pockets of tubulin (`1JFF` and `4I4T`), `GABA_A`, `GLIC`, Albumin, and Luciferase. You can compare a clinical anaesthetic (`halothane` or `isoflurane`), a bulky non-immobilizer (`F6` or `TFMB`), and the convulsant `flurothyl` sitting inside the same hydrophobic cavity.

{{figure: anaesthetics-microtubules/pockets}}

## How it was done

- **Public structures and primary sources.** Eight structures downloaded from the RCSB Protein Data Bank (`1JFF`, `4I4T`, `6X3T`, `3P4W`, `1E7B`, `1BA3`, `1DPX`, `1UBQ`), with pocket definitions taken verbatim from Craddock et al. (2012, Tables 2 & 3) and crystallographic ligand coordinates. Potency (`MAC`) and olive-oil solubility values for all 35 gases came directly from Craddock et al. (2017, Table S1), Fang et al. (1996, Tables 1–5), Koblin et al. (1994), and Steffey et al. (1998); molecular geometries came from PubChem.
- **Checked on known crystal poses first.** Before locking the plan, we stripped the native bound drugs from four co-crystal structures (`GLIC + desflurane`, `GABA_A + propofol`, `Luciferase + bromoform`, `Albumin + halothane`) and redocked them blind. Every one landed within `0.28–1.31 Å` of its experimental position.
- **Locked first, with one pre-results amendment.** The plan, pockets, molecules, scoring functions (`AutoDock Vina v1.2.5` with `vina` and `vinardo`), random seed, and verdict rules were locked with a SHA-256 hash before running the test panel. One operational amendment (`Amendment 1`) was logged and committed *before* any results were produced or inspected: reducing Vina search exhaustiveness from `16` to `4` after confirming on positive controls that top affinities agreed to `0.000–0.011 kcal/mol`.
- **1,680 dockings.** Every one of the 35 gases was docked into all 24 pockets under both `vina` and `vinardo`, followed by `10,000`-permutation significance tests and `5,000`-resample paired bootstraps.
- **Cost.** Nothing: public structural data, open-source docking software (`AutoDock Vina v1.2.5`, `Open Babel 3.1.1`), and local CPU time.

## What this cannot tell you

- **What happens after a drug binds.** Rigid docking estimates how snugly a molecule sits in a static pocket. It cannot simulate ion-channel gating (holding `GABA_A` open) or Craddock et al. (2017)'s post-binding quantum-optical claim that anaesthetics shift collective terahertz oscillations across tubulin's tryptophan rings. Those require different physics and separate tests.
- **Protein flexibility and water.** Real proteins breathe, pockets expand around bound gases, and displaced water molecules change free energy. Static crystal and cryo-EM snapshots miss induced fit and polymerized microtubule seam geometry.
- **Independent replication.** One AI system designed, ran, and wrote up this study. A second AI system from another vendor has not yet re-run it from the locked plan, and no human structural biologist has checked it.

## Files

- [Full results](https://github.com/ejhong/aletheia-lab/blob/main/questions/anaesthetics-microtubules/RESULTS.md)
- [The locked plan](https://github.com/ejhong/aletheia-lab/blob/main/questions/anaesthetics-microtubules/protocol.md) and [amendments](https://github.com/ejhong/aletheia-lab/blob/main/questions/anaesthetics-microtubules/amendments.md)
- [Code and tests](https://github.com/ejhong/aletheia-lab/tree/main/questions/anaesthetics-microtubules/analysis)

AI did this work: Antigravity (Google DeepMind) extracted the primary data, designed and ran the docking study, built the interactive figures, and wrote this page on 23 November 2026. Eugene directed it.
