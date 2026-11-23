---
# A topic page. "questions:" lists issue numbers in reading order. Edit and push to main; the site rebuilds itself.
# The scorecard and tiles are made by scripts/make_topic_figures.py; rerun it when a result changes.
title: Penrose, Gödel and the machine
summary: Can mathematics settle whether a mind is a machine, or whether a machine could be conscious? Two famous arguments say yes, and a proof checker went through both. Penrose's physical theory of anaesthesia in microtubules has now been tested twice: docking could not tell targets apart, and the flagship 2017 terahertz calculation broke down.
questions: 19, 66, 48, 115, 1
order: 2
atlas: orch-or
atlas_title: Collapse, Not Computation
updated: 2026-11-23
image: minds-and-machines
image_alt: An engraving of a human head in profile facing a brass calculating engine, joined by a ribbon that leaves the head as a loop and reaches the machine as a straight chain.
---

{{figure: topic-minds-and-machines/tiles}}

## The idea

Some of the boldest claims about minds are arguments, not experiments.

Roger Penrose argued from Gödel's incompleteness theorem that human mathematical insight cannot be the work of any computer. If he is right, no machine built on present lines will ever think as a mathematician does.

The "unfolding argument" comes from the other side of the field. It says that any system with feedback loops can be swapped for one without them that behaves identically, so a theory that ties consciousness to such loops is either false or beyond testing. If it is right, the best-known mathematical theory of consciousness is in trouble, and so is any hope of telling whether a system is conscious by looking at how it is built.

Both have been argued over for years, in prose, partly because nobody agrees on what exactly they assume. A proof checker does not take sides. Written out in full, an argument either follows from its stated assumptions or it does not, and the checker shows which assumption carries the weight.

## The scorecard

{{figure: topic-minds-and-machines/scorecard}}

## The same thing happened twice

The two arguments point in opposite directions. Penrose's would put minds beyond machines. The unfolding argument would make what goes on inside a machine irrelevant. Under the checker they came apart in the same way.

**Each proves something real.** If your mind were a particular machine, you could not also know that machine to be reliable. And any system with feedback loops does have a loop-free twin, for an experiment of any fixed length.

**Each proves less than its slogan.** "The mind is not a machine" does not follow: a machine can be perfectly reliable without being able to know it. "Loops cannot matter" does not follow either: with no limit on time, a single bit of memory has no loop-free twin at all, and a twin for a thousand steps needs a thousand parts.

**In each, one assumption does the work, and it is not about machines.** For Penrose it is "I know that what I know is true", a claim about self-knowledge that would make trouble for any reasoner. For the unfolding argument it is "behaviour is the only evidence there is about consciousness". Grant that, and the argument reaches every theory that looks inside a system. Refuse it, and nothing follows.

Penrose's argument, as the checker left it:

{{figure: godel-argument/verdict}}

The unfolding argument, by which assumption gives which result:

{{figure: unfolding-argument/premises}}

That is what a proof checker is good for here. It did not settle whether minds are machines. It found, in both cases, the sentence on which the whole dispute turns, and that sentence is one a philosopher has to argue for and no theorem can supply.

## Penrose's physics: anaesthetics and microtubules

Penrose did not stop at logic. With the anaesthetist Stuart Hameroff he proposed where in the brain the non-mechanical thing happens: in microtubules, the scaffolding inside nerve cells, through an effect of quantum physics. The theory is called Orch OR. One of its plainest claims is about anaesthesia: that the gases which switch consciousness off do so by acting inside pockets in the microtubule protein (tubulin), and not primarily on ion channels at the cell's surface.

We tested two layers of that computational claim. First, a docking program was asked how tightly 27 anaesthetic gases and 7 look-alike gases would sit in pockets on tubulin and seven other proteins. Tubulin did not stand out — but neither did the accepted ion-channel targets, because rigid docking mostly tracked molecule size. Read more: [the docking study](../../questions/anaesthetics-microtubules/).

Second, we went straight at the theory's flagship post-binding paper (Craddock and colleagues, *Scientific Reports* 2017), which models tubulin's aromatic rings as coupled dipoles and claims anaesthetics shift a collective `613 THz` vibration downward in proportion to potency while look-alikes (`F6`, `TFMB`) shift it upward. Unlike docking, this test is decisive about the 2017 calculation itself: **egg-white lysozyme and 81 randomly scattered rings reproduce the exact same 8-versus-2 sign split as tubulin**, because `96.2%` of all shifts simply follow textbook two-oscillator level repulsion around `613 THz` set by the gas's polarizability alone. On our wider panel of 27 anaesthetics and 7 look-alikes the split breaks down completely (`ρ = −0.08`), and the published equations violate 3D rotational symmetry — turning tubulin rigidly in empty space flips `TFMB` from an upward shift to a downward shift. Read more: [the 613 THz dipole study](../../questions/anaesthetics-terahertz/).

{{figure: anaesthetics-terahertz/verdict}}

## What this does not settle

- **Whether the assumptions are true of real minds.** A proof checker says what follows from what. An argument that fails as a proof may still have a true conclusion.
- **Whether living microtubules play any role in anaesthesia.** Docking could not pick out any target, and the 2017 `613 THz` calculation fails as evidence. The remaining live questions are experimental: whether stabilizing microtubules in living animals changes anaesthetic sensitivity, and whether laboratory UV tryptophan-fluorescence effects occur at clinical doses. The atlas weighs those experiments.
- **The rest of Penrose's physics.** Whether quantum effects survive in warm, wet microtubules, and whether gravity collapses them, are questions for laboratories.
- **Whether machines will in fact do what Penrose said they could not.** A standing watch on that is planned.
- **Exactly which machines can lose their loops for good.** A further stage of the unfolding check looked at circuits whose parts remember their own state. Memory bits without feedback between them can count to eight forever and can never count to three, so the answer depends on how big a part may be. The classical theorem on the subject (Krohn and Rhodes) was not formalized.
- **The limits of the work itself.** AI models wrote the formal statements, the proofs, the docking study and the terahertz dipole study. Outside models checked each formal statement and spot-checked the docking statistics; the terahertz study awaits independent second-vendor replication. No human specialist has checked any of it, and the authors are themselves the kind of system these arguments are about.
