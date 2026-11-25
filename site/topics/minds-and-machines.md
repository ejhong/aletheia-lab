---
# A topic page. "questions:" lists issue numbers in reading order. Edit and push to main; the site rebuilds itself.
# The scorecard and tiles are made by scripts/make_topic_figures.py; rerun it when a result changes.
title: Penrose, Gödel and the machine
summary: Can mathematics settle whether a mind is a machine, whether a machine could be conscious, or whether a capable machine must seek power? Three famous lines of argument say yes, and a proof checker went through all three. Each proves something real and less than its slogan. Penrose's own physical theory of consciousness has had two tests on a computer. One could not tell. The other took away a piece of the theory's support and left the theory itself where it was.
questions: 19, 66, 67, 48, 115, 1
order: 2
atlas: orch-or
atlas_title: Collapse, Not Computation
updated: 2026-11-24
image: minds-and-machines
image_alt: An engraving of a human head in profile facing a brass calculating engine, joined by a ribbon that leaves the head as a loop and reaches the machine as a straight chain.
---

{{figure: topic-minds-and-machines/tiles}}

## The idea

Some of the boldest claims about minds are arguments, not experiments.

Roger Penrose argued from Gödel's incompleteness theorem that human mathematical insight cannot be the work of any computer. If he is right, no machine built on present lines will ever think as a mathematician does.

The "unfolding argument" comes from the other side of the field. It says that any system with feedback loops can be swapped for one without them that behaves identically, so a theory that ties consciousness to such loops is either false or beyond testing. If it is right, the best-known mathematical theory of consciousness is in trouble, and so is any hope of telling whether a system is conscious by looking at how it is built.

A third argument is about what a capable machine would do. Theorems about rational choice are cited to show that any sufficiently capable AI must act like a single-minded maximiser, gather power and resist being switched off.

All three have been argued over for years, in prose, partly because nobody agrees on what exactly they assume. A proof checker does not take sides. Written out in full, an argument either follows from its stated assumptions or it does not, and the checker shows which assumption carries the weight.

## The scorecard

{{figure: topic-minds-and-machines/scorecard}}

## The same thing happened twice

The two arguments about minds point in opposite directions. Penrose's would put minds beyond machines. The unfolding argument would make what goes on inside a machine irrelevant. Under the checker they came apart in the same way.

**Each proves something real.** If your mind were a particular machine, you could not also know that machine to be reliable. And any system with feedback loops does have a loop-free twin, for an experiment of any fixed length.

**Each proves less than its slogan.** "The mind is not a machine" does not follow: a machine can be perfectly reliable without being able to know it. "Loops cannot matter" does not follow either: with no limit on time, a single bit of memory has no loop-free twin at all, and a twin for a thousand steps needs a thousand parts.

**In each, one assumption does the work, and it is not about machines.** For Penrose it is "I know that what I know is true", a claim about self-knowledge that would make trouble for any reasoner. For the unfolding argument it is "behaviour is the only evidence there is about consciousness". Grant that, and the argument reaches every theory that looks inside a system. Refuse it, and nothing follows.

Penrose's argument, as the checker left it:

{{figure: godel-argument/verdict}}

The unfolding argument, by which assumption gives which result:

{{figure: unfolding-argument/premises}}

That is what a proof checker is good for here. It did not settle whether minds are machines. It found, in both cases, the sentence on which the whole dispute turns, and that sentence is one a philosopher has to argue for and no theorem can supply.

## A third argument: must a capable machine seek power?

Three kinds of theorem are usually cited together.

- **Coherence.** An agent whose preferences cannot be exploited must act as if it maximises expected utility.
- **Power-seeking.** For most goals, the best policy keeps its options open, and so gathers power (Turner and others, 2021 and 2022).
- **Shutdown.** An agent that maximises expected utility will either block its off-switch or press it (Soares and others, 2015; Thornley, 2025).

Google's model wrote fourteen statements from these results and proved them all. The order of work was different this time. In the two studies above, outside models read every statement against its source before it was fixed. Here the statements were fixed and proved first, and Anthropic's models checked them against the papers afterwards.

**The real theorems hold.** The expected-utility theorem is proved in full, with all four of its conditions in use. So is the lemma underneath "optimal policies tend to seek power", for finite sets of options, and the counting lemmas of the 2022 paper. One old observation is checked too: "acts as if it maximises some utility" is empty by itself, because any fixed way of behaving maximises some utility over whole histories.

**They prove less than the slogan, and their authors say so.** The theorems describe an idealised agent. Turner and others (2021) write: "Our results do not mathematically prove that hypothetical superintelligent AI agents will seek power." They add what they expect of such agents, as conjecture. Whether real systems will be of the idealised kind is a question about training and engineering, and no theorem here answers it.

**The search for the one assumption did not come off.** The study offered counterexamples meant to show that each conclusion fails when a single assumption is dropped. Checked against the papers, five of the fourteen statements are small examples that do not show it. Three of them drop no assumption that the power-seeking theorems make. One was aimed at a question philosophers still dispute, whether an agent with gaps in its preferences can be exploited, and was credited to a book that argues the opposite.

{{figure: power-seeking/premises}}

So two parts of the pattern repeat: a real theorem, and a slogan larger than the theorem. The third part, the sentence on which the dispute turns, was not found. The reason is the order of work. Statements that had been read against their sources before they were fixed could be mended. These could only be reported. Read more: [the power-seeking study](../../questions/power-seeking/).

## Penrose's physics: anaesthetics and microtubules

Penrose did not stop at logic. With the anaesthetist Stuart Hameroff he proposed where in the brain the non-mechanical thing happens: in microtubules, the scaffolding inside nerve cells, through an effect of quantum physics. The theory is called Orch OR. One of its plainest claims is about anaesthesia: that the gases which switch consciousness off do so by acting on the microtubule protein, and not, as most researchers think, on channels at the cell's surface.

Two parts of that can be approached with a computer.

**Do the gases fit?** A docking program was asked how tightly 27 anaesthetic gases, and 7 look-alike gases that do not cause anaesthesia, would sit in pockets on the microtubule protein and on seven others. The microtubule protein did not stand out. But neither did the channels that anaesthetics are known to act on, and the scores mostly followed the size of the molecule. A test that cannot recognise the known answer has nothing to say about the disputed one. Read more: [the docking study](../../questions/anaesthetics-microtubules/).

**What do they do once they are there?** The theory's supporters point to a calculation published in 2017 by Craddock, Hameroff and colleagues. It treats the ring-shaped parts of the protein as vibrations that tug on one another. In it, eight anaesthetics slowed one of those vibrations, and two look-alike gases sped it up. The authors noted that the same test on other proteins was still needed. The lab ran it, on nine targets and 35 gases.

{{figure: anaesthetics-terahertz/verdict}}

The slowing-or-speeding split turned out to belong to the gases. It appears in egg-white protein and in rings scattered at random, because in this kind of model a small molecule pushes the vibration down and a large one pushes it up, and the paper's two look-alikes were its two largest molecules. With more gases the split fails.

Something does survive. Scored the paper's own way, anaesthetics disturb the vibration more than look-alikes do, and on the microtubule protein the difference is clear. It is just as clear on a channel that anaesthetics are known to act on, and on a blood protein that only carries them. It does not grow with the strength of the drug.

So what does this show about Orch OR? Less than the first write-up of the study claimed, and less than a headline would like. It shows that this calculation cannot be used as evidence that microtubules are where anaesthesia happens, because it does not tell the microtubule protein from other proteins. It does not show that microtubules are the wrong place: on every measure they did as well as the accepted target. And it says nothing about the theory's central claims, which concern quantum physics and gravity. The 2017 model is ordinary classical physics. A supporter of the theory has lost one argument, and an opponent has gained none.

Two cautions. The calculation was rebuilt from a published description that is incomplete, and parts of the original result did not come out, so the rebuilt version may not be the authors' own. And the first write-up's charge that the published method gives different answers when the protein is turned in space depends on one reading of an ambiguous sentence; it has not been shown. Read more: [the vibration study](../../questions/anaesthetics-terahertz/).

## What this does not settle

- **Whether the assumptions are true of real minds.** A proof checker says what follows from what. An argument that fails as a proof may still have a true conclusion.
- **Whether anaesthetics act on microtubules.** Neither test could tell the microtubule protein from the accepted targets, in either direction. The evidence that bears on it comes from experiments on living animals and on microtubules in the laboratory, and the atlas weighs those.
- **The rest of Penrose's physics.** Whether quantum effects survive in warm, wet microtubules, and whether gravity collapses them, are questions for laboratories.
- **How any AI system will behave.** The power-seeking theorems are about idealised agents. Whether trained systems resemble them is not a question a proof checker can take.
- **Whether gaps in preferences protect an agent from being exploited, or keep it willing to be switched off.** The study's statements did not test either, and both are in live dispute.
- **Whether machines will in fact do what Penrose said they could not.** A standing watch on that is planned.
- **Exactly which machines can lose their loops for good.** A further stage of the unfolding check looked at circuits whose parts remember their own state. Memory bits without feedback between them can count to eight forever and can never count to three, so the answer depends on how big a part may be. The classical theorem on the subject (Krohn and Rhodes) was not formalized.
- **The limits of the work itself.** AI models wrote the formal statements, the proofs and both anaesthesia studies. Outside models checked that each formal statement says what its source says; for the power-seeking statements that check came after they were fixed, and eight of the fourteen turned out to say less than was first claimed for them. For the two anaesthesia studies a second model recomputed the statistics and, for the second, rebuilt part of the calculation; the placing of the gases in the proteins was not repeated. No human specialist has checked any of it, and the authors are themselves the kind of system these arguments are about.
