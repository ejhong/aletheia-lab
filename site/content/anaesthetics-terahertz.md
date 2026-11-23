---
# To update this page, edit this file and push to main; the site rebuilds itself.
# The panels and interactive figures are made by questions/anaesthetics-terahertz/analysis/make_figures.py from the results files.
summary: A 2017 paper, often cited for Penrose and Hameroff's theory, calculated that anaesthetic gases slow a vibration in the microtubule protein while look-alike gases that do not cause anaesthesia speed it up. Does that calculation single out microtubules?
verdict: Not microtubules in particular: the famous split is a matter of molecule size, and where the calculation does tell anaesthetics apart, a nerve-cell channel and a blood protein do as well
result: Rebuilt from the paper's description, the calculation gives the paper's split on the microtubule protein, and the same split on egg-white protein and on rings placed at random. Whether a gas slows or speeds the vibration is set by the size of its molecule, and with more gases that split fails. Counted the paper's own way, anaesthetics do disturb the vibration more than look-alikes, but equally in a known anaesthetic target and in a blood protein, and not in step with drug strength. The calculation gives no reason to pick out microtubules. It does not count against them either, and it does not touch the quantum physics of the theory.
dek: The earlier docking study could not say what a gas does once it has settled in a protein. A 2017 paper said what: it changes how the protein's ring-shaped parts vibrate together, one way for anaesthetics and the other way for look-alike gases. The lab rebuilt that calculation and ran it on more gases and on other proteins, a test the paper's authors said was still needed.
updated: 2026-11-23
---

> **Where things stand, 23 November 2026.** Run by one AI system and looked over by a second, which recomputed the statistics and rebuilt part of the calculation with its own code. The two agree on the main finding. They differ on how hard it lands. The first write-up called the paper's result an artefact and its method broken. The second reading, given here, is narrower: the calculation does not single out microtubules, part of it does survive, and an error in the published method has not been shown.

## What we figured out {menu: Findings}

Penrose and Hameroff's theory, Orch OR, places consciousness in microtubules, the scaffolding inside nerve cells. One of its claims is that anaesthetic gases work by acting there. [An earlier study](../anaesthetics-microtubules/) asked how tightly such gases fit into pockets on the microtubule protein, tubulin, and could not tell: the method failed to pick out even the targets everyone accepts.

The theory's supporters say fit is not the point. What matters is what the gas does once it is there. A 2017 paper by Craddock, Hameroff and colleagues put numbers on that. It treated the ring-shaped parts of tubulin as a set of electrical vibrations that tug on one another, with a gas molecule added as one more. In the paper, eight anaesthetics slowed a vibration near 613 terahertz, by more for the stronger drugs. Two look-alike gases, fat-soluble like anaesthetics but causing no anaesthesia, sped it up.

The paper tried ten gases and one protein, and its authors wrote that tests on other proteins were needed to see whether the effect was "universal or unique to tubulin". The lab rebuilt the calculation from the published description and ran it on 35 gases and nine targets: two structures of tubulin, two channels that anaesthetics are accepted to act on, four unrelated proteins including the lysozyme of egg white, and 81 rings scattered at random.

{{figure: anaesthetics-terahertz/tiles}}

1. **The split came out, and it came out everywhere.** On tubulin, seven of the eight anaesthetics slowed the vibration and both look-alikes sped it up. Lysozyme gave the same seven and two. So did the random rings.
2. **The direction of the shift is set by the gas.** Two vibrations that are coupled push each other apart. A gas whose own vibration lies above 613 terahertz pushes the protein's down; one below pushes it up. In this kind of model a gas's own frequency depends only on how easily its electrons are pushed about, which goes with the size of the molecule. That one fact about the gas gives the direction of the shift in 303 of 315 cases, whatever the protein.
3. **In the 2017 paper the two look-alikes were the two largest molecules.** Its own table shows it, and the paper reports that both look-alikes added a vibration below the band while the anaesthetics added one above. That is the pattern point 2 predicts.
4. **With more gases the down-or-up split fails.** Eleven of 27 anaesthetics, the xylenes and methoxyflurane among them, are large molecules and speed the vibration up as the look-alikes did. Two of seven look-alikes are small and slow it down. Anaesthetics and look-alikes overlap in size, so nothing that turns on size can sort them.
5. **Counted the paper's own way, something survives.** The paper scored each gas by the largest slowing it causes anywhere near 613 terahertz, even if its largest effect is a speeding-up. On that score an anaesthetic beats a look-alike 89% of the time on tubulin, where 50% is chance. Size does not explain it: among the large molecules alone the figure is 92%.
6. **But tubulin shares it.** The GABA-A channel, which anaesthetics are accepted to act on, scores 85%, and albumin, a blood protein that is known to bind these gases, scores 83%. The small proteins and the random rings score 68 to 75%. So in this model it matters where a gas sits in a real protein with real pockets. It does not matter that the protein is tubulin.
7. **Stronger drugs do not shift it more.** Across the 27 anaesthetics the effect on tubulin does not follow the strength of the drug (correlation −0.08, or −0.09 scored the paper's way). Nor did it across the paper's own eight (+0.12 and +0.29), where the paper reported a near-perfect fit. That part of the paper was not reproduced.

{{figure: anaesthetics-terahertz/verdict}}

## How much weight this carries {menu: What it means}

**What it shows.** The striking part of the 2017 result, anaesthetics pushing one way and look-alikes the other, is about the size of the molecules and would come out for any protein. What is left once that is set aside is real but modest: in the model, anaesthetics disturb the rings' vibrations more than look-alikes do when they sit in a large protein with pockets. Tubulin is one such protein. A channel that anaesthetics are known to act on is another, and a blood protein that merely carries them is a third. Nothing in the calculation picks tubulin out of that company, so it cannot be used as evidence that microtubules are where anaesthesia happens.

**What it does not show.** It is not evidence against microtubules. Tubulin does as well as the accepted target on every count; the calculation simply cannot choose between them. And none of this bears on the heart of Orch OR, which is a claim about quantum physics and gravity. This model is ordinary classical physics and contains none of that. The paper's authors were also more careful than some who cite it: they asked for exactly this test, and suggested the effect might be common to many proteins. On our numbers that suggestion looks right.

**Three cautions about our own work.**

- *It is a reconstruction.* The paper used a simulated structure that is not public, its own placements of the gases and its own estimate of their properties. Ours differ in all three. The shifts we get are far larger than the paper's, and the link to drug strength did not come out. The printed formulas are also not consistent with each other: taken as printed, one of them puts a single ring at about 1,500 terahertz, far outside the paper's own range of 480 to 700.
- *The orientation problem is a doubt, not a demonstrated error.* The first write-up of this study said the published method gives different answers when the whole protein is turned in space, which no physical quantity should. That is true of the method on one reading of the paper's description. On another reading of the same sentence it is not, and the authors' program is not public. Our second check rebuilt both readings: the main finding, that the gas sets the direction, holds under either.
- *The comparison in point 6 was made after the results were in.* The plan fixed in advance judged the study on the direction of the largest shift, not on the paper's own score, and compared tubulin with the other targets only on that. Tubulin's lead over the small proteins and the random rings on the paper's score is larger than chance would easily give (it stays above zero in more than 95 of 100 resamplings of the gases), but it shrinks when the gases are placed by a second docking program, and there are only seven look-alike gases. It should be tested again on gases chosen in advance.

## Try it: which way does each gas push? {menu: Each gas}

Each dot is a gas. Dots above the line slow the vibration near 613 terahertz, which the paper reported for anaesthetics. Dots below speed it up. Switch between all 35 gases and the paper's own eleven, and swap tubulin for lysozyme or for the random rings. With the gas's own frequency along the bottom, the picture is the same for every target: gases to the right of 613 push down, and gases to the left push up.

{{figure: anaesthetics-terahertz/repulsion}}

## All nine targets, and the turning test {menu: All nine targets}

The top chart puts the nine targets side by side. Filled dots are the 35-gas panel and hollow rings are the paper's ten gases. The strip beneath turns the same tubulin and gas to 20 random orientations: under the study's reading of the published method the answer moves about, and under a version built so that it cannot, all 20 fall on one point.

{{figure: anaesthetics-terahertz/proteins}}

| Target | Why it is here | Paper's ten gases: slowed / sped up | Direction given by the gas alone | 27 against 7, by direction | 27 against 7, the paper's score | Link to drug strength |
|---|---|---:|---:|---:|---:|---:|
| **Tubulin (1JFF)** | The theory's target | 7/8 · 2/2 | 32 of 35 | 70% | 89% | −0.08 |
| Tubulin (4I4T, sharper) | The same protein, as a repeat | 7/8 · 2/2 | 35 of 35 | 59% | 77% | −0.13 |
| GABA-A channel | Accepted target | 7/8 · 2/2 | 32 of 35 | 60% | 85% | +0.02 |
| GLIC channel | Accepted target | 7/8 · 2/2 | 35 of 35 | 73% | 76% | −0.10 |
| Albumin | Blood protein that binds these gases | 6/8 · 2/2 | 30 of 35 | 57% | 83% | −0.15 |
| Firefly luciferase | Enzyme | 7/8 · 2/2 | 34 of 35 | 67% | 70% | −0.41 |
| **Lysozyme (egg white)** | Small unrelated protein | 7/8 · 2/2 | 35 of 35 | 66% | 69% | −0.26 |
| Ubiquitin (3 rings) | The smallest network | 7/8 · 2/2 | 35 of 35 | 68% | 68% | −0.16 |
| **81 random rings** | No protein at all | 7/8 · 2/2 | 35 of 35 | 70% | 75% | −0.12 |

The two "27 against 7" columns say how often a randomly chosen anaesthetic outscores a randomly chosen look-alike; 50% is chance. "By direction" uses the largest shift, counted as positive when it slows the vibration. This is the measure the plan fixed in advance, and on it no target is reliably better than chance. "The paper's score" counts only the largest slowing.

## The rings and their vibrations {menu: Rings and spectrum}

On the left, drag to turn the network of rings in tubulin or another protein. On the right, pick a gas and see how it moves each of tubulin's 81 vibrations. The dashed line marks the gas's own frequency and the shaded band is 613 terahertz. When the dashed line is to the right of the band, the band moves down; when it is to the left, the band moves up.

{{figure: anaesthetics-terahertz/spectrum}}

## How it was done

- **The model.** Taken from the two papers that describe it: Craddock and colleagues (*Scientific Reports* 7:9877, 2017) and Kurian and colleagues (*Physics Letters A* 382:33, 2018). Where the two disagree, the formula that reproduces the paper's stated range of frequencies was used. Empty tubulin comes out at 468 to 696 terahertz against the paper's 480 to 700.
- **The gases.** The 35 gases and their positions in each protein are those of the docking study. How easily each gas's electrons are pushed about was worked out with a standard method and checked against the paper's own table for its eleven gases; the two agree closely.
- **The plan was fixed first.** What would be measured and how it would be judged were written down and locked before any gas was added to any protein. Nothing was changed afterwards.
- **A second look.** A second AI system recomputed the statistics from the results table, rebuilt the empty-protein calculation with its own code and got the same numbers, tested the push-apart rule with a probe of adjustable size on three targets, read both source papers, and worked out the comparison on the paper's own score. It did not repeat the placing of the gases, so everything that depends on where each gas sits rests on the first system's run.
- **Cost.** Nothing: public structures and free software.

## What this cannot tell you

- **Whether anaesthetics act on microtubules in a living brain.** That is a matter for experiments on animals and on microtubules in the laboratory, and the atlas weighs those.
- **Anything about the quantum side of Orch OR.** The calculation tested here has no quantum physics in it.
- **Whether the authors' own program has the weaknesses of our rebuilt one.** Only their code and data could show that.
- **What a specialist would make of it.** Two AI systems did the work and no physicist or pharmacologist has checked it.

## Files

- [Full results](https://github.com/ejhong/aletheia-lab/blob/main/questions/anaesthetics-terahertz/RESULTS.md)
- [The locked plan](https://github.com/ejhong/aletheia-lab/blob/main/questions/anaesthetics-terahertz/protocol.md) and [the list of data](https://github.com/ejhong/aletheia-lab/blob/main/questions/anaesthetics-terahertz/MANIFEST.md)
- [The second system's check](https://github.com/ejhong/aletheia-lab/tree/main/questions/anaesthetics-terahertz/replication/fable)
- [Code](https://github.com/ejhong/aletheia-lab/tree/main/questions/anaesthetics-terahertz/analysis)

AI did this work. Antigravity (Google DeepMind) designed the study, wrote and ran the calculation and built the figures on 23 November 2026. Claude (Anthropic) checked it the same day and wrote this page. Eugene directed it.
