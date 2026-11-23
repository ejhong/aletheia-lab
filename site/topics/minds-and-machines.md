---
# A topic page. "questions:" lists issue numbers in reading order. Edit and push to main; the site rebuilds itself.
# The scorecard and tiles are made by scripts/make_topic_figures.py; rerun it when a result changes.
title: Penrose, Gödel and the machine
summary: Can mathematics settle whether a mind is a machine, or whether a machine could be conscious? Two famous arguments say yes, and a proof checker went through both. Penrose's own physical theory of consciousness has had a first, inconclusive test.
questions: 19, 66, 48, 1
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

Penrose did not stop at logic. With the anaesthetist Stuart Hameroff he proposed where in the brain the non-mechanical thing happens: in microtubules, the scaffolding inside nerve cells, through an effect of quantum physics. The theory is called Orch OR. One of its plainest claims is about anaesthesia: that the gases which switch consciousness off do so by settling into pockets in the microtubule protein, and not, as most researchers think, by acting on channels at the cell's surface.

That part can be approached with a computer. A docking program was asked how tightly 27 anaesthetic gases, and 7 look-alike gases that do not cause anaesthesia, would sit in pockets on the microtubule protein and on seven others. The microtubule protein did not stand out. But neither did the channels that anaesthetics are known to act on, and an unrelated protein did as well as any. The scores mostly followed the size of the molecule.

{{figure: anaesthetics-microtubules/verdict}}

A test that cannot recognise the known answer has nothing to say about the disputed one. This result neither supports the microtubule idea nor counts much against it. The experiments that do bear on it are on living animals, and the atlas weighs those. Read more: [the docking study](../../questions/anaesthetics-microtubules/).

## What this does not settle

- **Whether the assumptions are true of real minds.** A proof checker says what follows from what. An argument that fails as a proof may still have a true conclusion.
- **Whether anaesthetics act on microtubules.** The one test made here could not tell. It fits molecules into rigid pockets, and says nothing about what a drug does once it has settled, which is what the theory's supporters now claim matters.
- **The rest of Penrose's physics.** Whether quantum effects survive in warm, wet microtubules, and whether gravity collapses them, are questions for laboratories.
- **Whether machines will in fact do what Penrose said they could not.** A standing watch on that is planned.
- **Exactly which machines can lose their loops for good.** A further stage of the unfolding check looked at circuits whose parts remember their own state. Memory bits without feedback between them can count to eight forever and can never count to three, so the answer depends on how big a part may be. The classical theorem on the subject (Krohn and Rhodes) was not formalized.
- **The limits of the work itself.** AI models wrote the formal statements, the proofs and the docking study. Outside models checked that each formal statement says what its source says; the docking study's statistics were recomputed by a second model, though the docking was not re-run. No human specialist has checked any of it, and the authors are themselves the kind of system these arguments are about.
