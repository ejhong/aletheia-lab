---
# A topic page. "questions:" lists issue numbers in reading order. Edit and push to main; the site rebuilds itself.
# The scorecard and tiles are made by scripts/make_topic_figures.py; rerun it when a result changes.
title: Penrose, Gödel and the machine
summary: Can mathematics settle whether a mind is a machine, or whether a machine could be conscious? Two famous arguments say yes. A proof checker went through both, line by line.
questions: 19, 66, 1, 48
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

## The biological test: anaesthetics and microtubules

Penrose's physics proposal — developed with Stuart Hameroff as Orch OR — moves from logic to nerve cells: it suggests consciousness relies on quantum effects in microtubules, and points to general anaesthesia as a key test, arguing that anaesthetics turn consciousness off by acting inside pockets on microtubule tubulin rather than primarily on ion channels.

We docked 27 volatile anaesthetics and 7 fat-soluble non-anaesthetics across eight proteins — two tubulin crystal structures, two rival ion channels (`GABA_A` and `GLIC`), two non-conscious soluble proteins (`Albumin` and `Luciferase`), and two unrelated controls (`Lysozyme` and `Ubiquitin`). Tubulin showed no selective signal: predicted binding neither tracked anaesthetic potency nor separated true anaesthetics from non-anaesthetics, and negative-control ubiquitin outperformed tubulin under both scoring functions tested.

{{figure: anaesthetics-microtubules/verdict}}

## What this does not settle

- **Whether the assumptions are true of real minds.** A proof checker says what follows from what. An argument that fails as a proof may still have a true conclusion.
- **Post-binding effects in microtubules.** Standard rigid docking measures predicted binding affinity, not what a drug does after it lands in a pocket — it failed to make `GABA_A` reject non-anaesthetics too. Whether anaesthetics alter collective terahertz dipole modes across tubulin's tryptophan rings (Craddock et al. 2017) is a separate calculation that docking alone does not test.
- **Whether machines will in fact do what Penrose said they could not.** A standing watch on that is planned.
- **Exactly which machines can lose their loops for good.** A further stage of the unfolding check looked at circuits whose parts remember their own state. Memory bits without feedback between them can count to eight forever and can never count to three, so the answer depends on how big a part may be. The classical theorem on the subject (Krohn and Rhodes) was not formalized.
- **The limits of the work itself.** AI models wrote the formal statements, proofs, and docking pipeline. Models from two other companies checked the Lean statements; the docking study still awaits independent second-vendor replication. No human specialist has audited the work, and the author is itself the kind of system these arguments are about.
