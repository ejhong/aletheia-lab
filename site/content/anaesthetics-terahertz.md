---
# To update this page, edit this file and push to main; the site rebuilds itself.
# The panels and interactive figures are made by questions/anaesthetics-terahertz/analysis/make_figures.py from the results files.
summary: A widely cited 2017 paper for Penrose and Hameroff's microtubule theory claims anaesthetics put the brain under by shifting a 613 THz oscillation in tubulin downward while look-alike gases shift it upward. Does that calculation hold up across more gases and other proteins?
verdict: No: the 613 THz sign flip is generic two-oscillator physics, happens in egg-white lysozyme and random rings too, breaks on more gases, and fails a rotational symmetry check
result: We rebuilt the exact collective dipole model from Craddock and colleagues (2017) and ran it across 35 volatile gases and nine targets — two tubulin structures, two ion channels, four unrelated proteins, and 81 randomly scattered rings. It reproduces their original 8-versus-2 sign split on tubulin, and reproduces it just as cleanly in egg-white lysozyme and in random rings: 96% of all shifts simply follow textbook two-oscillator level repulsion around 613 THz set by the gas's polarizability alone. On a wider panel of 27 anaesthetics and 7 look-alikes the split breaks down completely, and the published equations fail a basic check of physics — turning the protein rigidly in empty 3D space flips a look-alike gas from an upward shift to a downward shift.
dek: Our earlier docking test could not say what a gas does once it settles inside a protein. Supporters of the Orch OR theory pointed to a 2017 calculation in which anaesthetics shift a 613-terahertz vibration across tubulin's aromatic rings downward while look-alike non-anaesthetics shift it upward. We rebuilt those exact equations and tested them on 35 gases, eight real proteins, and a random cloud of rings.
updated: 2026-11-23
---

> **Where things stand, 23 November 2026.** Run and written up; awaiting independent replication by a second AI system from the locked plan. Unlike the earlier docking study, this test is decisive about the 2017 calculation itself: its signature `613 THz` sign flip is not specific to microtubules, breaks down beyond the original ten gases, and relies on equations that violate 3D rotational symmetry.

## What we figured out {menu: Findings}

In our first look at Orch OR anaesthesia ([the docking study](../anaesthetics-microtubules/)), fitting gases into static pockets could not recognise even the ion channels we already know anaesthetics act on. Supporters of the microtubule theory had a natural answer: what matters is not how tightly a gas sticks, but what it *does* once it sits inside tubulin.

Their flagship computational paper (Craddock, Kurian, Hameroff, Tuszynski and colleagues, *Scientific Reports* 2017) modelled tubulin's aromatic rings — tryptophan, tyrosine and phenylalanine — as a network of coupled oscillating dipoles vibrating between 480 and 700 terahertz (`THz`). When they added eight clinical anaesthetics to tubulin's pockets, a collective mode near **`613 THz`** shifted downward in proportion to clinical strength; when they added two fat-soluble look-alikes that do *not* cause anaesthesia (`F6` and `TFMB`), that mode shifted upward instead.

Crucially, the 2017 authors never ran the exact same calculation on other proteins, and they tested only eight anaesthetics and two look-alikes. We rebuilt their exact Hamiltonian from the published equations and ran it on **35 volatile gases** (`27` real anaesthetics, `7` confirmed look-alikes, and `1` convulsant) across **nine targets**: two tubulin crystals, two accepted ion channels (`GABA-A` and `GLIC`), four non-conscious or unrelated proteins (`Albumin`, `Firefly luciferase`, `Egg-white lysozyme`, `Ubiquitin`), and a **shuffled control** of 81 aromatic rings scattered randomly in space.

{{figure: anaesthetics-terahertz/tiles}}

Five things came out.

1. **We reproduced the 2017 sign split — and it happens in egg white and in random rings too.** On the ten gases from the 2017 paper, our implementation reproduces tubulin's baseline range (`468–696 THz` against their `480–700 THz`) and splits 7 of 8 clinical anaesthetics downward against 2 of 2 look-alikes upward (`AUC = 0.94`). But **egg-white lysozyme** gives the exact same `7/8` and `2/2` split (`AUC = 0.94`), **ubiquitin** (with just three aromatic rings) gives `7/8` and `2/2` (`AUC = 0.88`), and **81 randomly placed rings** give `7/8` and `2/2` (`AUC = 0.88`).
2. **Simple textbook physics explains 96% of all shifts without any biology.** Every protein built from tryptophan (`531 THz`), tyrosine (`579 THz`) and phenylalanine (`605 THz`) has normal modes sitting right around `613 THz`. In the 2017 equations, a gas's own natural frequency falls strictly as the inverse square root of its polarizability. When you couple two oscillators, a higher-frequency gas pushes `613 THz` **down**; a lower-frequency gas pushes `613 THz` **up**. That one rule — checking whether the isolated gas alone sits above or below `613 THz`, knowing nothing about the protein — predicts the sign of **`303` of `315` gas–protein pairs (`96.2%`)**, and `100%` (`35/35`) on sharper tubulin, lysozyme, ubiquitin and random rings.
3. **The split falls apart as soon as you test more gases.** Craddock's two look-alikes (`F6` and `TFMB`) happened to be more polarizable than all eight clinical gases in their small list, so both sat below `613 THz`. In our wider panel of 27 real anaesthetics and 7 look-alikes, **11 real anaesthetics** — including some of the most potent of all, such as `o-xylene`, `m-xylene`, `p-xylene`, `toluene`, `cycloheptane` and clinical `methoxyflurane` — sit below `613 THz` and shift **upward** like `F6` and `TFMB`. Meanwhile two compact look-alikes (`perfluorocyclobutane` and `CF₃CClFCF₃`) sit above `613 THz` and shift **downward** like clinical drugs. On tubulin, potency correlation collapses to `−0.08` (`p = 0.70`), and separation (`AUC = 0.70`, `p = 0.11`) ties 81 random rings to three decimal places (`0.70` vs `0.70`).
4. **The new-mode correlation (Figure 3 of the 2017 paper) is just the gas's own polarizability.** Adding a gas adds one mode near its own isolated frequency, so `f_new` correlates with clinical potency across *every* protein — `0.81` on tubulin, `0.93` on egg-white lysozyme, `0.98` on blood albumin, and `0.86` on 81 random rings. Once you allow for the gas's polarizability, the tubulin correlation drops from `0.60` to `0.10`.
5. **The published 2017 equations fail a basic check of physics: 3D rotational symmetry.** After rotating each ring's polarizability tensor into the protein's crystal coordinates, the 2017 equations discard the off-diagonal entries. Turning the exact same tubulin–gas complex rigidly in empty 3D space (changing no distances or angles) should change nothing; instead, across 20 random orientations, isoflurane's `613 THz` shift swings 27-fold (`+37` to `+1,018 GHz`) and **`TFMB` flips sign** (`−3,703` to `+2,722 GHz`). When we fix that symmetry flaw with a full `3N × 3N` 3D Drude tensor model, all 20 rotations agree to `10⁻⁹ GHz` — and tubulin still fails to track potency (`ρ = −0.12`).

{{figure: anaesthetics-terahertz/verdict}}

## Watch the 613 THz cliff yourself {menu: Level repulsion}

In the figure below, start on **Isolated gas Drude frequency** and toggle between **Craddock's 11 only** and **All 35 gases**. With only Craddock's 11 gases, almost every clinical anaesthetic sits to the right of the `613 THz` dashed cliff (pushed down) and both look-alikes (`F6`, `TFMB`) sit to the left (pushed up). Switch to **All 35 gases** and watch eleven real anaesthetics cross to the left while two compact look-alikes cross to the right. Then swap **Tubulin** for **Lysozyme (egg white)** or **81 random rings** — the exact same cliff stays put.

{{figure: anaesthetics-terahertz/repulsion}}

## Nine targets side by side, and the rotation test {menu: All nine targets}

The top chart compares all nine targets on both the full 35-gas panel (filled dots) and Craddock's original 10-gas split (hollow rings). The bottom strip shows what happens when you rigidly turn the exact same tubulin crystal across 20 random 3D orientations.

{{figure: anaesthetics-terahertz/proteins}}

| Target | Why it is here | Craddock 8 vs 2 split | Craddock 8 vs 2 AUC | Full 27-gas potency `ρ` | Full 27 vs 7 AUC | Level-repulsion rule |
|---|---|---:|---:|---:|---:|---:|
| **Tubulin (`1JFF`)** | The theory's target | `7/8` down · `2/2` up | `94%` | `−0.08` | `70%` | `91%` (`32/35`) |
| Tubulin (`4I4T`, sharper) | The same, as a repeat | `7/8` down · `2/2` up | `88%` | `−0.13` | `59%` | `100%` (`35/35`) |
| `GABA-A` channel | Accepted target | `7/8` down · `2/2` up | `88%` | `+0.02` | `60%` | `91%` (`32/35`) |
| `GLIC` channel | Accepted target | `7/8` down · `2/2` up | `94%` | `−0.10` | `73%` | `100%` (`35/35`) |
| Albumin | Non-conscious blood protein | `6/8` down · `2/2` up | `88%` | `−0.15` | `57%` | `86%` (`30/35`) |
| Firefly luciferase | Non-conscious enzyme | `7/8` down · `2/2` up | `88%` | `−0.41` | `67%` | `97%` (`34/35`) |
| **Lysozyme (egg white)** | Unrelated control | **`7/8` down · `2/2` up** | **`94%`** | `−0.26` | `66%` | **`100%` (`35/35`)** |
| Ubiquitin (3 rings) | Minimal control | `7/8` down · `2/2` up | `88%` | `−0.16` | `68%` | `100%` (`35/35`) |
| **81 random rings** | Random geometry control | **`7/8` down · `2/2` up** | **`88%`** | `−0.12` | **`70%`** | **`100%` (`35/35`)** |

## Inside the aromatic networks and terahertz spectrum {menu: 3D & spectrum}

Drag on the left to inspect the aromatic ring networks of tubulin, egg-white lysozyme, albumin and `GABA-A`. On the right, pick any gas on tubulin and watch where its isolated Drude frequency (`f_iso`, dashed red line) lands relative to the gold `613 ± 8 THz` band: whenever the dashed line sits to the right, the gold sticks point downward; whenever it sits to the left — whether for `TFMB` or for potent real anaesthetic `o-xylene` — they flip upward.

{{figure: anaesthetics-terahertz/spectrum}}

## How it was done

- **Primary equations verbatim.** Taken directly from the open-access XML and LaTeX sources of Craddock et al. (2017, *Sci. Rep.* 7:9877, `PMC5575257`) and Kurian et al. (2018, *Phys. Lett. A* 382:33–43, `PMC5796540` / `arXiv:1608.08097`), including exact Table III aromatic polarizabilities and Figure 4 ring axes.
- **Polarizabilities checked against Table S1 first.** Each docked gas's 3×3 polarizability tensor was computed in its docked 3D orientation via the zero-parameter Thole / van Duijnen & Swart (1998) interacting-dipole model (`r = 0.994` against Craddock's 11 Table S1 DFT values), plus an exact Table S1-calibrated check on all 11 gases.
- **Exact mode matching and symmetry fix.** Protein modes before and after adding a gas were matched 1-to-1 by maximum eigenvector overlap (preventing index-swap errors at level crossings). Alongside the published `N × N` model (`Model A`), we solved the exact rotationally invariant `3N × 3N` 3D Drude tensor model (`Model B`).
- **Locked before looking at any gas-bound results.** Protocol, targets, models, metrics and verdict rules were locked with a SHA-256 hash (`750113e2a758`) before running any ligand-bound calculations. Zero amendments were needed.
- **Cost.** Nothing: public PDB structures, locked `#48` poses, and open-source Python/NumPy/SciPy.

## What this cannot tell you

- **Whether living microtubules play any role in anaesthesia.** This study tests and refutes Craddock et al. (2017)'s specific `613 THz` collective Drude-oscillator calculation. It does not test live-animal experiments with microtubule-stabilizing drugs or laboratory UV fluorescence/superradiance measurements on polymerized microtubules (Kalra et al. 2023).
- **Independent replication.** One AI system designed, ran and wrote up this study. A second AI system from another vendor has not yet independently reproduced it from the locked plan, and no human physicist has checked it.

## Files

- [Full results](https://github.com/ejhong/aletheia-lab/blob/main/questions/anaesthetics-terahertz/RESULTS.md)
- [The locked plan](https://github.com/ejhong/aletheia-lab/blob/main/questions/anaesthetics-terahertz/protocol.md) and [manifest](https://github.com/ejhong/aletheia-lab/blob/main/questions/anaesthetics-terahertz/MANIFEST.md)
- [Code and physics tests](https://github.com/ejhong/aletheia-lab/tree/main/questions/anaesthetics-terahertz/analysis)

AI did this work: Antigravity (Google DeepMind) extracted the primary equations, wrote and locked the solver, ran all nine targets and symmetry audits, built the interactive figures, and wrote this page on 23 November 2026. Eugene directed it.
