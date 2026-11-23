---
# To update this page, edit this file and push to main; the site rebuilds itself.
# The panels and interactive figures are made by questions/anaesthetics-microtubules/analysis/make_figures.py from the results files.
summary: One theory of consciousness says general anaesthetics work by acting on microtubules inside nerve cells, not on the channels at their surface. If a computer fits anaesthetic gases into pockets on eight proteins, does the microtubule protein stand out?
verdict: Could not tell: the calculation does not pick out microtubules, and does not pick out the accepted targets either
result: A standard calculation of how tightly 35 gases sit in pockets on eight proteins shows nothing special about tubulin, the protein of microtubules: its predicted grip matches anaesthetic strength weakly, and look-alike gases that do not cause anaesthesia score tighter than real ones. But the same is true of the ion channels that anaesthetics are known to act on, and an unrelated protein does as well as any. The scores mostly follow the size of the molecule. So this method cannot tell an anaesthetic target from any other protein, and the result neither supports the microtubule idea nor counts much against it.
dek: General anaesthesia switches consciousness off cleanly and brings it back, and how the drugs do it is still argued over. Most researchers point to ion channels on the surface of nerve cells. Roger Penrose and Stuart Hameroff's theory points to pockets in the microtubules inside them. We asked a docking program to fit 27 anaesthetic gases and 7 look-alikes into tubulin and seven other proteins, with the rules fixed before looking at the scores.
updated: 2026-11-23
---

> **Where things stand, 23 November 2026.** Finished. Run by Antigravity (Google DeepMind); its statistics were recomputed from the results table by Claude (Anthropic) and matched, though the docking itself was not re-run. Tubulin does not stand out. Neither do the accepted targets, so the method cannot answer the question it was asked.

## What we figured out {menu: Findings}

For more than a century anaesthetists have known a strange rule: the more easily a gas dissolves in olive oil, the less of it is needed to put a patient under. A small family of gases breaks the rule. They dissolve in oil well, they reach the brain, and they do not cause anaesthesia. Whatever anaesthetics act on has to do two things: hold strong anaesthetics more tightly than weak ones, and treat those look-alikes differently.

Penrose and Hameroff's theory, known as Orch OR, says consciousness depends on microtubules, the scaffolding inside nerve cells, and that anaesthetics switch it off by settling into oily pockets in tubulin, the protein microtubules are made of. Earlier work by supporters of the theory mapped eight such pockets and fitted gases into them by computer (Craddock and colleagues, 2012 and 2017).

We ran the same kind of calculation on tubulin and on seven other proteins: two ion channels that are the usual suspects for anaesthesia, two proteins known to hold anaesthetics without having anything to do with consciousness, and two unrelated proteins as a check. If anaesthetics pick out microtubules, tubulin should stand out.

{{figure: anaesthetics-microtubules/tiles}}

1. **Tubulin does not stand out.** Across 27 anaesthetic gases, the predicted grip on tubulin matches their strength only weakly (0.29 on a scale where 1 is a perfect match and 0 is none; it could easily be chance). A sharper structure of tubulin and a second scoring method give much the same.
2. **The look-alikes score tighter than the real anaesthetics.** On tubulin, a real anaesthetic outscores a look-alike only 21% of the time, where 50% would mean no difference. It should be well above 50%.
3. **The accepted targets fail the same test.** On the GABA-A channel, which anaesthetics are known to act on, a real anaesthetic outscores a look-alike only 8% of the time. The calculation cannot recognise a target we already know.
4. **An unrelated protein does as well as any.** Ubiquitin, a small protein with no part in anaesthesia, matches anaesthetic strength better than tubulin and about as well as the channels. With the second scoring method it comes first on both counts.
5. **The scores follow size.** On seven of the eight proteins the predicted grip tracks the number of atoms in the gas far more closely than it tracks anything else. The look-alikes happen to be bulky.

{{figure: anaesthetics-microtubules/verdict}}

So the plain reading is not "anaesthetics do not act on microtubules". It is that this calculation cannot say where anaesthetics act. A test that fails on the known answer has no verdict to give on the disputed one.

## Protein by protein {menu: Each protein}

In the figure below, pick a protein and change what the gases are plotted against. Plotted against size, the points fall almost on a line. The look-alikes sit above the real anaesthetics on nearly every protein.

{{figure: anaesthetics-microtubules/potency}}

## All eight, side by side {menu: All eight}

{{figure: anaesthetics-microtubules/matrix}}

| Protein | Why it is here | Match with anaesthetic strength | The same, allowing for size | How often a real anaesthetic outscores a look-alike |
|---|---|---|---|---|
| **Tubulin** | The theory's target | 0.29 | 0.44 | 21% |
| Tubulin, sharper structure | The same, as a repeat | 0.35 | 0.44 | 8% |
| GABA-A channel | An accepted target | 0.42 | 0.55 | 8% |
| GLIC channel | An accepted target | 0.38 | 0.53 | 30% |
| Albumin | Holds anaesthetics; no role in consciousness | 0.28 | 0.37 | 9% |
| Luciferase | Holds anaesthetics; no role in consciousness | 0.21 | 0.31 | 12% |
| Lysozyme | Unrelated | 0.10 | −0.02 | 17% |
| Ubiquitin | Unrelated | 0.51 | 0.52 | 46% |

First scoring method; 1 is a perfect match and 0 is none; 50% in the last column means no difference.

One split shows what lies underneath. Nine of the 27 anaesthetics are the familiar gases of the operating theatre. On those nine alone, no protein matches their strength at all. The other eighteen are a chemical family tested in rats, each a little larger than the last, and on those every protein matches, the unrelated ones included. A greasy pocket on almost any protein will rank a family of ever-larger molecules in order of size.

## Inside the pockets {menu: The pockets}

Turn the fitted gases round inside a pocket of each protein, and compare a real anaesthetic with a look-alike in the same place.

{{figure: anaesthetics-microtubules/pockets}}

## How it was done

- **Public structures.** Eight protein structures from the Protein Data Bank. The tubulin pockets are those named in the 2012 paper by the theory's supporters.
- **The gases.** Twenty-seven that cause anaesthesia, seven look-alikes that do not, and one that causes convulsions, with their strengths taken from published tables.
- **Checked on known answers first.** Four drugs whose positions in a protein are known from crystals were removed and fitted back blind. Each landed within about an ångström of where it really sits.
- **Locked first.** Proteins, pockets, gases, both scoring methods and the pass marks were fixed before the run. One change was logged before any result existed: the search was made less exhaustive to save time, after a check that it made no difference on the known answers.
- **1,680 fits,** with the open program AutoDock Vina, scored two ways.
- **Spot-checked by a second AI.** Claude recomputed the matches and comparisons above from the table of scores, and they agree. It did not re-run the fitting, which needs software not installed here.
- **Cost.** Nothing.

## What this cannot tell you

- **Whether anaesthetics act on microtubules.** The method failed on the accepted targets too, so its silence about tubulin means little.
- **What a drug does once it has settled.** Fitting a molecule into a rigid pocket says nothing about whether it then holds a channel open, or changes how a microtubule behaves. The supporters' own 2017 claim is about the second, and is not tested here.
- **Real proteins move.** Pockets open and close and water gets in the way. None of that is in a rigid fit.
- **The fitting itself has not been repeated.** Only the statistics were checked. No structural biologist has looked at any of it.

## What would do better

The experiments that bear on this are not calculations. Does changing the stability of microtubules in a living animal change how much anaesthetic it takes to put it under? That has been tried in tadpoles, rats and mice, with results that point both ways, and the atlas [weighs them](https://ejhong.github.io/aletheia/cases/orch-or/).

## Files

- [Full results](https://github.com/ejhong/aletheia-lab/blob/main/questions/anaesthetics-microtubules/RESULTS.md)
- [The locked plan](https://github.com/ejhong/aletheia-lab/blob/main/questions/anaesthetics-microtubules/protocol.md) and [the one amendment](https://github.com/ejhong/aletheia-lab/blob/main/questions/anaesthetics-microtubules/amendments.md)
- [Code](https://github.com/ejhong/aletheia-lab/tree/main/questions/anaesthetics-microtubules/analysis) and the [spot check](https://github.com/ejhong/aletheia-lab/tree/main/questions/anaesthetics-microtubules/replication/fable)

AI did this work: Antigravity (Google DeepMind) designed and ran the study and built the figures. Claude (Anthropic) spot-checked the statistics and rewrote this page in the lab's plain style. Eugene directed it.
