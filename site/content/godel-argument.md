---
# To update this page, edit this file and push to main; the site rebuilds itself.
#   The panels and diagrams are HTML fragments in site/figures/godel-argument/, included with {{figure: ...}}.
#   Tick a step:     change "- [ ]" to "- [x]".
#   Move a stage:    set its "Status:" line to done, in progress or not started.
#   Fold a section:  "::: details Title" opens it and ":::" closes it.
#   Also update the "Where things stand" note and the "updated:" date below.
summary: Penrose argued from Gödel's theorem that the mind is not a machine. A proof checker went through the argument. The modest conclusion holds; the proof of the strong one does not.
verdict: The modest conclusion is proved; the proof of the strong one fails
result: Penrose's modest conclusion is proved by a proof checker. His proof of the stronger one, that the mind is no machine at all, does not hold up. The stronger conclusion itself is neither proved nor refuted, and nothing here touches his physics.
dek: Roger Penrose argued from Gödel's theorem that the human mind cannot be a machine. We wrote his argument and the standard replies in Lean 4, where a proof checker verifies every step and every assumption has to be stated.
updated: 2026-11-23
card_alt: A line from Gödel's theorem to "not a machine we can know is sound", marked proved, continuing as a dotted line to "not a machine at all", marked not established.
---

> **Where things stand, 23 November 2026.** Finished, as far as it was planned. Penrose's modest conclusion is proved. His proof of the stronger one, that the mind is no machine at all, does not hold up. The stronger conclusion itself is neither proved nor refuted, and nothing here touches his physics.

## What we figured out

Gödel showed in 1931 that a consistent formal system strong enough for arithmetic cannot prove its own consistency. Since 1961 the philosopher John Lucas, and later the physicist Roger Penrose, have argued that this sets minds apart from machines: a machine is such a system, a mathematician can see what it cannot prove, so the mathematician is not that machine. Logicians have mostly answered that the argument assumes too much. The dispute has run for sixty years, in prose.

We put it to a proof checker. In Lean 4 every assumption must be written into the statement of a theorem, and a small trusted program rejects any proof that leans on anything else. So the checker can say exactly which assumptions carry which conclusion. Forty-two statements were fixed in advance, each read by AI models from two other companies, and then proved.

{{figure: godel-argument/verdict}}

Four things came out.

1. **The argument proves something real.** If your mind were a particular machine, you could not also know that machine to be reliable. That is the conclusion Penrose himself states in 1994: mathematicians are not using a "knowably sound algorithm".
2. **It does not prove that the mind is not a machine.** A machine can be perfectly reliable without being able to know it. Peano arithmetic is one. Knowing its reliability from outside just gives a second machine with the same blind spot.
3. **The trouble is self-knowledge, not machinery.** The assumption that does the damage is "I know that what I know is true". It is what makes "I know which machine I am" contradictory, for any reasoner. No proof here uses the difference between a mind and a machine.
4. **Penrose's second, subtler argument is valid but rests on rules that contradict themselves.** With the rules repaired it reaches only this: if I am a machine in my arithmetic, I know something that machine cannot prove. Antonella Corradini and Sergio Galvan showed that on paper in 2022.

In short: the old argument is right about something smaller than it claims. The mathematics is not new; what is new is that a proof checker has been through it, and the table of which assumption does what.

{{figure: godel-argument/tiles}}

## Who stands where

This is easily read as a fight between people who think the mind is a machine and people who think it is not. It is not that. Nobody below argues that the mind is a machine. They disagree about a proof, and about how much of it is left standing.

{{figure: godel-argument/stances}}

- **Penrose** gave the proof and holds its conclusion. He also has reasons from physics, which no one on this page examines.
- **Koellner** is a critic of the proof, not of the conclusion. He wrote the argument out exactly in order to test it, and found two steps that break. One of his own theorems is that his system can prove neither that the mind is a machine nor that it is not.
- **Corradini and Galvan** accept Koellner's system and answer that he stopped too soon. Take "I am F" to be about arithmetic only and the two steps hold; they prove that in detail. What the argument then shows is less than Penrose claimed, and they say so. They still count it as a real difference between mind and machine.
- **This check** sides with no one. It confirms that the argument is valid, that its rules are inconsistent as stated, and that a repaired version proves something weaker.

### What is left of the proof

Corradini and Galvan worked out what survives in 2022, on paper. We wrote our statement S4g before reading their papers, knowing only roughly what their abstract concludes. Set side by side, the two are the same result.

{{figure: godel-argument/salvage}}

- **The same result, and theirs first.** Their step 7 (2022, p. 490) and our S4g say the same thing of the same sentence. They reached it four years earlier, and the credit for it is theirs.
- **What they prove and we assume.** The repaired rules apply only to sentences that are definitely true or false. They prove, inside Koellner's system, that the two sentences in question are (Lemmas 1 and 2, pp. 488–490). That is their answer to Koellner and the heart of their paper. Our statement takes both facts as assumptions. The second lemma follows from the first by one axiom, and that step is now checked in Lean; the first is not.
- **What Lean adds.** Their proof is on paper and in places a sketch. Ours is checked by a kernel, but it is of a thinner statement. Nothing here checks their two lemmas.
- **Why it stops there.** They give the reason we gave. The known sentence contains "is known", so it is not a sentence of arithmetic, and a machine that matches my arithmetic need not prove it (Note 11, p. 491).
- **One step further.** They also show that Koellner's system derives "no formal system matches everything I know", arithmetic and beyond (step 8, pp. 490–493). But in that system the sentence is itself neither true nor false, so it cannot be asserted as true, and they say so. The last inference of that step is now checked in Lean.
- **What their reading rests on.** Not on that sentence. It rests on the restricted form, their step 8′ (2022, p. 493; Theorem 2 of the 2024 note), where both the assumption and the sentence that is known are definitely true or false. That is the form S4g matches.

They read the result more strongly than we would. A machine may equal the mind in mathematics, they write, but then not in what the mind knows beyond it, and in this sense "the difference between mind and machine is demonstrated" (2024, p. 560). How much weight that carries is a question of philosophy, not of proof.

Nothing in their result contradicts Koellner's theorems, as they note themselves (2022, p. 474). So the dispute is smaller than it looks. All sides can agree on what the repaired argument proves, and differ on how much it matters.

### A corollary that does not hold as printed

Their second paper adds a corollary (2024, p. 562): if a machine proves some arithmetic the mind does not know, the mind cannot know that machine to be consistent. Its proof uses the step "consistency implies soundness": a machine that never contradicts itself proves only truths. That step is false, and on the most natural reading the corollary falls with it.

- **The counterexample.** Take Peano arithmetic and add the sentence "Peano arithmetic is inconsistent". By Gödel's theorem the result never contradicts itself. Yet it proves a false sentence, the one that was added. No sound mind knows that sentence, since it is false. But a sound mind, itself a machine, can know that this system is consistent.
- **Where the proof goes wrong.** At that one step and nowhere else. For any sentence for which consistency does guarantee truth, their proof goes through. The simplest statements of arithmetic are of that kind; that is a textbook fact we did not re-prove.
- **What does hold.** If all the arithmetic the mind knows is provable by the machine, the mind cannot know the machine consistent. And if the machine is in fact consistent, the mind cannot know it inconsistent either. This is close to results of the earlier stages and is not new.
- **Limits.** These are proofs about arithmetic, and about minds taken as sets of sentences. They do not show that Koellner's system itself refutes the corollary; that would need the system built. The authors' prose speaks of a machine that "surpasses" the mind, so they may have meant a stronger hypothesis than they printed. We have not contacted them.

An outside review of this page by a Google model, in a chat Eugene shared, proposed the same counterexample without having been told of our doubt. Two models agreeing is not a check. The check is the proof.

## The first argument

Model an idealized mind as the set of arithmetic statements it would ever accept, and a machine as a formal system whose axioms can be listed mechanically. Thirteen statements were proved in this setting.

{{figure: godel-argument/reach}}

- **The conditional holds.** If a consistent mind is exactly what machine F proves, it does not contain the statement that F is consistent. Put Penrose's way: a mind that accepts "whatever F proves is so" contains everything F proves and something more.
- **Being a sound machine is not contradictory.** Peano arithmetic is sound, consistent and mechanical, and cannot prove its own true consistency statement. It even proves "if I am consistent, then my Gödel sentence holds". So all a mind would need, to outdo it, is knowledge that it is consistent.
- **Supplying that knowledge gives another machine.** Add the consistency statement and you have a second sound machine, with a Gödel sentence of its own. This is the reply Lucas anticipated in 1961.
- **Asserting your own soundness is contradictory for anyone.** Any system that can talk about its own beliefs in the standard way and asserts that they are all true is inconsistent, machine or not. This is David Chalmers's criticism of 1995, and it holds.
- **Gödel's own conclusion holds.** If everything a mind accepts is true, then either no formal system generates it, or some true statement of a simple kind is left undecided by it. Gödel claimed this either/or, and no more.
- **The assumptions do not decide the matter.** Everything this section assumes of a mind is true of one mind that is a machine, Peano arithmetic, and of one that is not, the set of all arithmetic truths. So nothing follows from those assumptions alone about which kind we are.

Penrose is careful about this himself. On page 76 of *Shadows of the Mind* he states the modest conclusion as proved, and calls the claim that thought is non-computational "the stronger deduction", to be argued for separately.

## Adding "I know"

Arithmetic cannot say "I know" or "I am this machine". So the second stage adds an operator K, read "it is known that", with the principles that William Reinhardt gave it in 1985. The question is which of those principles each result actually needs.

{{figure: godel-argument/premises}}

Then a small formal language was built in which "there is a machine such that…" can be said inside the language itself. Two of Reinhardt's theorems were proved in it. They differ only in where "I know" stands.

{{figure: godel-argument/which}}

Together these are Gödel's either/or again, now inside a logic of knowledge. A reasoner cannot know which machine it is. It can still be one, and then there are truths it can never know. The proofs do not say which of the two holds. Penrose's second argument is the attempt to rule out being a machine altogether.

## The second argument

The first argument fails because no one can know that the machine they are is sound. So Penrose went another way round. Do not claim to know it. Suppose, for the sake of argument, that I am the machine F, and see what follows. Chalmers, who thought this the more interesting argument, pointed out that it no longer depends on being able to see that F is sound.

This is the argument meant to reach "I am not the machine F, whatever F is". The logician Peter Koellner set it out in eight steps in 2018. It lets truth and knowledge apply to sentences that themselves speak of truth and knowledge, and it uses two rules, marked below.

{{figure: godel-argument/steps}}

- **Rule one fails.** "Whatever is so is true" contradicts "whatever is true is so" as soon as there is a liar sentence, one that says of itself that it is not true.
- **Rule two fails.** "Whatever is proved is known" contradicts "what is known is true" as soon as a sentence says of itself that it is not known.
- **The repair.** Restrict both rules to sentences that are definitely true or false. The argument still runs, provided two of its own lines are of that kind. Koellner states as a theorem that they are not. Our reduction shows why: "I am F", taken over the whole language, is not. That last fact is his theorem too, quoted here and not re-proved.
- **What survives.** Restrict "I am F" to arithmetic, where it is definitely true or false. Then the last step fails, because the sentence the argument produces is no longer a sentence of arithmetic. What is left is weaker: something is known that F does not prove. This is Corradini and Galvan's result of 2022.

Put together, there are three ways to run the argument.

{{figure: godel-argument/routes}}

So the proof of the strong claim does not go through. That is not a proof that the strong claim is false. Koellner's further result, also quoted and not re-proved, is that in his system neither side of Gödel's either/or can be proved or refuted.

## The objections, and what happens to them

Is the best objection Chalmers's or Koellner's? Neither one alone. There are five serious objections, aimed at different steps, and the oldest is still the one that does most of the work. None of them says the mind is a machine. Each says the proof does not show that it is not.

{{figure: godel-argument/objections}}

Three things stand out.

- **No objection is overturned.** Every one that a proof checker can reach comes out as its author said. The first two are now machine-checked, with every assumption on show.
- **Chalmers's objection is narrower than it sounds.** He writes that "the deepest flaw lies in the assumption that we know that we are sound". Penrose replied in 1996 that the contradiction goes away if belief is confined to statements of one simple arithmetical kind, which cannot speak of belief. On that point the logic is with Penrose: in the small logic of Stage 2, "I know that what I know is so" is an axiom, and the logic is proved consistent. With arithmetic added, consistency is a theorem of Reinhardt and Carlson, quoted here and not re-proved.
- **But the same restriction stops the argument.** Confine "I am F" to arithmetic and the last step of the second argument fails, as [the comparison above](#what-is-left-of-the-proof) shows. So Penrose can avoid Chalmers's contradiction or reach his conclusion, and the proofs here find no way to do both. Tying statement S4g to Penrose's own restriction is our reading of his reply, not something he or his critics say.

Two things the objections leave standing. The modest claim, that we are not a machine we can know to be sound, survives all five; Chalmers and Koellner both grant it. And something survives of the second argument: a machine that matches the mind's arithmetic still misses something the mind knows.

The case that the mind *is* a machine does not come from logic at all. It comes from physics and biology: the brain is a physical thing, and the known physics of such things can be simulated. Penrose's answer, as Chalmers reports it, is that the physics must then be non-computable. That is a question of evidence, and nothing on this page bears on it.

## How it was checked

- **Statements first.** Each claim was written as a formal statement before any proof existed, and tied to the page of the source it formalizes.
- **Two outside AIs read every statement.** Models from OpenAI and Google translated each one back into English without seeing our explanation, then compared it with the source passage. Deliberately wrong statements were mixed in to test them. In the final rounds both caught all eighteen.
- **Their objections changed the statements.** More than a dozen were rewritten before being locked, and four disagreements that could not be resolved are reported with the results.
- **Then the lock.** The statement files were hashed and committed before the proofs. A proof can change freely; it cannot quietly prove something else.
- **Then the proofs.** Lean's kernel checked each one. The build fails if any theorem uses `sorry` or any assumption beyond Lean's three standard axioms, and for each result there is a proof that its assumptions can hold together.

The underlying theorems of Stage 1 (Gödel's two incompleteness theorems, Löb's theorem) were already proved in the [Foundation](https://github.com/FormalizedFormalLogic/Foundation) library. The work here adds the reading in terms of minds and machines, the links to the sources, and the map of assumptions.

## What we got wrong

One claim of ours was false, and it was published here briefly. Working from a summary of Reinhardt's 1985 paper, we said that his theorem "a knower cannot know consistent a system that captures all it knows" needed an extra condition that the summary had left out, and we offered a repaired version. Then the paper itself arrived. Reinhardt states the theorem with no such condition. What the summary leaves out is his definition of "consistent": that the system never asserts a sentence together with its negation.

The theorem was then stated as he states it, checked, and proved. The plan had said to take statements from the original papers. We went ahead from a summary, and that is where the error came from.

## What this cannot tell you

- **Whether minds are machines.** The proofs show what follows from what. They say nothing about what a brain is.
- **Whether a person is well described as an ideal reasoner** with a fixed, consistent, logically closed body of knowledge. Every result here is about such idealized reasoners.
- **Whether Penrose would accept the eight steps** as his argument. A reconstruction was checked, not his wording.
- **Whether another theory of truth would save the argument.** One was used, Solomon Feferman's. Koellner argues that others would not help; that was not checked.
- **The two central theorems of Koellner's analysis** are quoted, not re-proved. Checking them means building his whole system in Lean, which was not done.
- **Whether Koellner's system refutes that corollary.** Our counterexample is about arithmetic and about minds as sets of sentences. Carrying it into his system needs the system built.
- **Whether Corradini and Galvan's lemmas hold.** Their answer to Koellner rests on two lemmas proved on paper inside his system. We have read them and not machine-checked them, and our own statement assumes what they prove.
- **Whether the whole picture is fair to Penrose.** The outside AIs checked each statement against a passage. They were not asked whether a fixed set of accepted sentences, closed under logic, is the right picture of mathematical understanding, which grows and corrects itself. Planted errors test for slips inside a framework, not for the choice of framework.
- **Anything about physics.** Penrose's proposal that quantum gravity is non-computable, and the Orch OR theory built on it, stand or fall on evidence of another kind.

This is no verdict on the atlas's claim [ORCH-C040](https://ejhong.github.io/aletheia/claims/ORCH-C040/). The lab does not grade the atlas.

## The plan

Three stages were planned and a fourth held in reserve. Each ended at a gate where Eugene decided what happened next.

### Stage 0 · Statements only
Status: done
Gate: Eugene reviews the checkers' divergences, then `lean/Statement.lean` is locked.

Write down exactly what will be proved, and check that it says what was meant, before proving anything.

- [x] Definitions, each with an English gloss and a locator to the passage it formalizes: formal system as r.e. theory; soundness; consistency; an idealized mind as a set K of sentences; "K is the theorem set of some machine"; and plain-arithmetic stand-ins for "K knows which machine" and "K knows the machine is sound".
- [x] Statements in `lean/GodelArgument/Statement.lean` as `def … : Prop`: 11 definitions and 13 statements, compiling against the pinned Foundation library. Proofs elsewhere must have exactly those types, so the lock covers the statements while proofs stay free to change.
- [x] The proof-lane Lean CI, set up on the question's branch, with a build-time check that a theorem uses only Lean's three standard axioms.
- [x] The statement check. OpenAI `gpt-6.2-astra` and Google `gemini-4-neon` each translated every Lean statement back into English blind, then compared it with the source passage. Three deliberately wrong statements were mixed in. In the final round both checkers caught all three. Their criticism in the earlier rounds led to five statements being rewritten. Of 17 items with a source passage, 15 ended as faithful or faithful with caveats from both checkers; two divergences are accepted with reasons and will be reported with the results. One statement, the halting form, had no source in hand at the time; it was checked the next day, when photographs of the pages arrived, and both checkers found it faithful.
- [x] Eugene reviews the report; then the protocol and the statement file are locked. Locked on 22 November 2026, 17:49 UTC.

### Stage 1 · Core results in plain arithmetic
Status: done
Gate: A report; Eugene decides on Stage 2.

Thin wrappers: Foundation already proves the underlying theorems (their names are in code type), and `RESULTS.md` must say so.

- [x] **a. Penrose's conclusion as a conditional.** If K is consistent and is the theorem set of F, then K does not contain Con(F). Stated for every r.e. axiomatization F of K, because Con(F) depends on how F is described. And in the shape the sources give it: a consistent, deductively closed mind that accepts "whatever F proves is so" strictly exceeds F. (`consistent_unprovable`, `craig_consistent_unprovable_of_RE`)
- [x] **b. The standard objection**, in three parts. A witness: PA is sound, consistent and a machine's theorem set, and lacks Con(PA). The machine proves the conditional itself, F ⊢ Con(F) → G_F, so the human's only edge is knowing Con(F) (`gödel_iff_con`). And the second machine: for any sound F, F + Con(F) is again a sound machine, with a consistency statement of its own that it cannot prove.
- [x] **c. Chalmers's point via Löb.** A system that proves its own soundness for every sentence is inconsistent, with no assumption that it is a machine (`löb_theorem`). By contrast, adding the soundness *of T* to a sound T gives a sound system.
- [x] **d. Gödel's disjunction, semantic form.** For any set K of true arithmetic sentences, either no formal system has K as its theorem set, or some true Π₁ sentence is undecided by K. Truth here means truth in ℕ in Lean's own logic.
- [x] **e. Penrose's argument in halting form** No sound r.e. certifier of non-halting certifies its own diagonal computation. Proved. Checked against *Shadows of the Mind* §2.5 on 23 November, once the pages were in hand: both checkers found it faithful, with minor caveats.

### Stage 2 · Epistemic arithmetic
Status: done
Condition: Eugene approved it on 23 November 2026. All four tiers are done, for $32.25 in statement checks.
Gate: Each tier gets its own statement check, entered through `amendments.md` before anything in it is proved.

This is where the new work is: theories in which the knower K is an operator with its own axioms (K1–K4), as in Reinhardt's epistemic arithmetic. The targets, as stated in Koellner (2018, Part I), are Reinhardt's Theorem 3 (p. 354), Theorem 5 (p. 355) and Theorem 6 (p. 357). Theorems 7 and 8, consistency results by Reinhardt and by Carlson, are cited, not proved. Statements are to be taken from Reinhardt's own papers, since Koellner's summary is informal in places.

- [x] **2A, small.** Done 23 November. An abstract layer: K is an operator on sentences, and each principle about it is a stated assumption. Nine statements locked after statement checks, then proved: Reinhardt's theorem that a knower exceeds any system it knows to be sound; his absolute version of the second incompleteness theorem; a sentence-by-sentence counterpart of his result that knowing which system you are is contradictory, with the core of his own proof; and two results showing which assumptions cannot be dropped. Seven were locked before Reinhardt's 1985 paper was in hand. It arrived the same day, corrected one of them, and two more were added from it.
- [x] **2B.** Done 23 November, on a smaller scope than first planned. Reinhardt's paper shows that his two central theorems need no arithmetic. So this tier builds a real formal language with the knowledge operator and quantifiers, with his proof system, and proves those two theorems in it: knowing which set you are is refuted, and being some set gives a truth you cannot know. Six statements, locked after two rounds of statement check, then proved. Epistemic arithmetic itself, with its arithmetic and its truth predicate, is not built.
- [x] **2C.** Done 23 November. Penrose's new argument, in the eight steps Koellner's Part II gives it, in an abstract setting with truth, knowledge and determinateness as operations on sentences. Seven statements, locked after two rounds of statement check, then proved: the argument is valid from its rules; each rule, unrestricted, is inconsistent; with restricted rules the argument needs two statements to be determinate; and for a determinate version of the thesis it yields only something weaker. Koellner's system itself is not built, so his theorems that the thesis is indeterminate and that neither side of the disjunction can be proved are cited, not re-proved.
- [x] **2D.** Done 23 November. Added after Corradini and Galvan's two papers were read. Seven statements, locked after two rounds of statement check, then proved: a step in the proof of their 2024 corollary, "consistency implies soundness", is false, with a counterexample; the corollary fails when a mind is read as a set of sentences; the rest of its proof is sound; a nearby statement holds; and two steps of their 2022 paper follow from what they rest on. Their system is still not built.

### Stage 3 · Stretch
Status: not started
Condition: Only after reporting on the earlier stages.

- [ ] Independence results by model construction.
- [ ] The untyped-truth inconsistency.

Out of scope: Carlson's consistency proof, which is cited instead. Dropped for now: the stably-computable version, because its author's own arXiv comment on 2208.04752v3 says "The framework currently has gaps".

## Every result

The forty-two statements, with the name of each proof in the repository. "Proved" means Lean's kernel accepted the proof and the proof uses only Lean's three standard axioms.

::: details Stage 1: thirteen statements in plain arithmetic

| Claim | Lean name | Premises required | Status | Source |
|---|---|---|---|---|
| A consistent mind that is F's theorem set does not contain Con(F) | `penroseConditional` | K is exactly F's theorems; K consistent; F includes basic arithmetic | Proved | Chalmers 1995, §1; Koellner 2018, p. 345 |
| No consistent mind is F's theorem set and contains Con(F) | `noConsistentMindKnowsOwnMachineConsistent` | K consistent; F includes basic arithmetic | Proved; stand-in only, see below | Koellner 2018, pp. 358–359 |
| A mind that accepts F's soundness strictly exceeds F | `knownSoundMachineIsExceeded` | K consistent, logically closed, does basic arithmetic, and contains "if F proves σ then σ" for every σ | Proved | Koellner 2018, pp. 354, 356, quoting Penrose 1994, p. 76 |
| A sound, consistent machine lacking its own true Con | `standardObjectionWitness` | none: it is about Peano arithmetic | Proved | Chalmers 1995, §1 |
| F proves "if F is consistent then G_F" | `machineProvesConditional` | F includes basic arithmetic | Proved | Chalmers 1995, §1 |
| The second machine: F + Con(F) is sound, proves Con(F), cannot prove its own Con | `secondMachine` | F sound; F includes basic arithmetic | Proved | Lucas 1961, pp. 116–117 |
| A system that asserts its own consistency is inconsistent | `chalmersPoint` | a belief predicate satisfying the three derivability conditions; self-reference available; no machine assumption | Proved | Chalmers 1995, §2 |
| A system that asserts its own soundness is inconsistent | `selfSoundnessInconsistent` | as above | Proved | Chalmers 1995, §2 |
| A sound system plus a true statement is sound | `soundPlusTrueIsSound` | T's axioms true; σ true | Proved | Chalmers 1995, §2 |
| A sound T plus the assertions of T's soundness is sound | `soundPlusItsSoundnessIsSound` | T's axioms true | Proved | the lab's contrast case |
| Gödel's disjunction | `godelDisjunction` | everything in K is true | Proved | Koellner 2018, p. 349, quoting Gödel 1951, p. 310 |
| Variant for sets not closed under deduction | `godelDisjunctionRE` | everything in K is true | Proved; a variant | as above |
| Penrose's argument in halting form | `penroseTuring` | A is a sound, mechanically listable certifier of non-halting | Proved | Penrose 1994, §2.5, pp. 73–75 |

:::

::: details Stage 2A: nine statements about a knowledge operator

| Claim | Lean name | Assumptions about K | Other assumptions | Status |
|---|---|---|---|---|
| If K(F(φ) → φ) for each φ, then for some ψ: Kψ and K¬F(ψ) | `reinhardtTheorem3` | base known; closed under modus ponens | F has a Gödel sentence | Proved |
| Then something is known that F does not hold of | `knowerExceedsKnownSoundSystem` | as above, and what is known is so | F has a Gödel sentence | Proved |
| The same from K(F(φ) → Kφ) for each φ | `reinhardtTheorem1Safe` | base known; closed under modus ponens; known that what is known is so | F has a Gödel sentence | Proved |
| If K(Kσ → F(σ)) for each σ, then K¬K(Con F), for any F | `reinhardtTheorem6` | base known; closed under modus ponens; what is known is known to be known; known that what is known is so | Con F means F never holds of a sentence and its negation; a known fixed point | Proved; Reinhardt's theorem |
| A variant with Con F read as "F does not hold of falsehood" | `absoluteSecondIncompleteness` | base known; closed under modus ponens; known that what is known is so | the second incompleteness theorem holds for F, provably | Proved; the lab's own, weaker |
| In that variant the extra condition cannot be dropped | `secondIncompletenessProvisoCannotBeDropped` | none: it exhibits a system | none | Proved |
| If K(Kφ ↔ F(φ)) for each φ, a contradiction follows | `knowingWhichSystemIsContradictory` | all four | F has a Gödel sentence | Proved; a counterpart of Reinhardt's result by another route |
| For no p is it known that p holds exactly when ¬p is known | `noKnownSelfDiagonal` | all four | none | Proved; the core of Reinhardt's own proof |
| "Known that what is known is so" cannot be dropped: "Peano arithmetic proves" satisfies the rest | `knownFactivityCannotBeDropped` | none: it names a system | none | Proved |

:::

::: details Stage 2B: six statements in a logic with real quantifiers

| Claim | Lean name | Axioms for K used | Status |
|---|---|---|---|
| What the logic proves, it proves to be known | `necessitationIsDerived` | distribution; known to be known; K of each axiom | Proved |
| Every theory proves ¬∃e K∀x(K¬U(x,x) ↔ U(e,x)) | `knowingWhichSetRefuted` | distribution; what is known is so, and K of it; K∀xφ → ∀xKφ | Proved; Reinhardt's Theorem 5 |
| If T proves ∃e∀x(K¬U(x,x) ↔ U(e,x)), T proves ∃e(¬U(e,e) ∧ ¬K¬U(e,e)) | `thesisGivesUnknownTruth` | what is known is so | Proved; Reinhardt's Theorem 3 |
| The same, as "absolutely undecidable" | `thesisGivesAbsolutelyUndecidable` | what is known is so | Proved |
| The same, known | `knownThesisGivesKnownUnknownTruth` | as the first and third rows | Proved |
| The logic does not prove falsehood | `logicIsConsistent` | none | Proved |

:::

::: details Stage 2C: seven statements about the second argument

| Claim | Lean name | Status |
|---|---|---|
| The eight steps yield "I am not F" from the unrestricted rules | `penroseArgumentValid` | Proved |
| "Whatever is so is true", unrestricted, is inconsistent | `unrestrictedTInInconsistent` | Proved |
| "Whatever is proved is known", unrestricted, is inconsistent | `unrestrictedKIntroInconsistent` | Proved; stronger than Koellner's remark |
| Knowing every logical validity is inconsistent with self-applicable truth | `knownValiditiesInconsistent` | Proved |
| With restricted rules the argument works if two named statements are determinate | `penroseArgumentUnderDeterminateness` | Proved |
| If "I am F" is indeterminate, so are those two statements | `stepsIndeterminateIfThesisIs` | Proved; a reduction of a theorem Koellner states without proof |
| For a determinate "I am F": something is known that F does not prove | `restrictedThesisGivesUnprovableKnowledge` | Proved; in substance Corradini and Galvan's step 7 (2022), found after it was locked |

:::

::: details Stage 2D: seven statements from Corradini and Galvan's papers

| Claim | Lean name | Status |
|---|---|---|
| Peano arithmetic plus "Peano arithmetic is inconsistent" is consistent and proves a false sentence | `consistencyDoesNotGiveSoundness` | Proved; against "Cons implies Sound" (2024, p. 562) |
| That machine proves what no sound mind knows, yet a sound mind can know it consistent | `machineOutrunsMindThatKnowsItConsistent` | Proved; against the corollary, read at the level of sets |
| The corollary's proof works for any sentence for which consistency gives soundness | `corollaryHoldsWhereConsistencyGivesSoundness` | Proved |
| A mind whose arithmetic lies inside a machine cannot know it consistent, nor, if it is consistent, inconsistent | `mindInsideMachineCannotKnowItConsistent` | Proved; the lab's repair, not new |
| From step 7: no formal system matches everything known | `unrestrictedThesisRefuted` | Proved; the last inference of their step 8 |
| A conditional with determinate parts is determinate | `conditionalDeterminateIfPartsAre` | Proved; their Lemma 2, given Lemma 1 |
| The Stage 1 assumptions are met by a machine and by a non-machine | `mindAssumptionsDoNotDecide` | Proved; the lab's own |

:::

Full report, with every limit and every disagreement: [`RESULTS.md`](https://github.com/ejhong/aletheia-lab/blob/main/questions/godel-argument/RESULTS.md). Proofs: [`lean/GodelArgument/`](https://github.com/ejhong/aletheia-lab/tree/main/questions/godel-argument/lean/GodelArgument). Changes of plan: [`amendments.md`](https://github.com/ejhong/aletheia-lab/blob/main/questions/godel-argument/amendments.md). Cost: $44.95, all for the outside AIs' checks.

## Sources

#### Read on 22 November 2026

- Koellner, "On the Question of Whether the Mind Can Be Mechanized, I: From Gödel to Penrose", *Journal of Philosophy* 115(7) (2018) 337–360. Formal content at pp. 349–359: axioms K1–K4 (p. 352), EA and EA_T (p. 353), Theorems 3–8 (pp. 354–358). The copy read was a course-hosted PDF of the published article; the protocol needs a properly sourced copy.
- Alexander, "A machine that knows its own code", *Studia Logica* 102(3) (2014) 567–576, [arXiv:1305.6080](https://arxiv.org/abs/1305.6080). Read through a fetch sub-agent's report of the arXiv HTML.

#### Read on 23 November 2026

- Penrose, *Shadows of the Mind* (1994), pp. 72–77, from photographs of the printed book supplied by Eugene.
- Alexander, "A machine that knows its own code", [arXiv:1305.6080v2](https://arxiv.org/abs/1305.6080v2), read in full from the PDF.
- Cheng, "Gödel's incompleteness theorem and the Anti-Mechanist Argument: revisited", [arXiv:1902.05902v2](https://arxiv.org/abs/1902.05902v2). Used for attributions only.
- Reinhardt, "Absolute Versions of Incompleteness Theorems", *Noûs* 19(3) (1985) 317–346, [JSTOR](https://www.jstor.org/stable/2214945), pp. 320–332, from a scan supplied by Eugene.
- Koellner, "On the Question of Whether the Mind Can Be Mechanized, II: Penrose's New Argument", *Journal of Philosophy* 115(9) (2018) 453–484, §§I–IV, from a copy supplied by Eugene.
- Koellner, "Gödel's Disjunction", in Horsten and Welch (eds.), *Gödel's Disjunction* (OUP, 2016), sections 7.9 to 7.17, read on screen in a Kindle copy bought by Eugene.

#### Read for the objections

- Chalmers, "Minds, Machines, and Mathematics", *Psyche* 2(9) (1995), [the author's copy](https://consc.net/papers/penrose.html), §§1–2. Read on 22 November 2026. The sentence quoted above is from the end of §2.
- Lucas, "Minds, Machines and Gödel", *Philosophy* 36 (1961) 112–127. Read on 22 November 2026.
- Penrose, "Beyond the Doubting of a Shadow", *Psyche* 2(23) (1996), §§3.4–3.13 (the reply to Chalmers) and §6 (on errors). Read on 23 November 2026.
- Koellner, Part II (above), p. 470, for his doubt that the question has a definite sense.

Named in the objections table but not read by us, so what they argue is not described here beyond their place in the debate: Putnam, "Minds and Machines" (1960); Benacerraf, "God, the Devil, and Gödel", *The Monist* 51 (1967) 9–32; Shapiro, "Incompleteness, Mechanism, and Optimism", *Bulletin of Symbolic Logic* 4 (1998) 273–302; Boolos's introductory note to Gödel's 1951 lecture. Their places are taken from Koellner (Part I, p. 340 and note 7, p. 358 and note 44; Part II, p. 470, note 22) and from Cheng's survey. Gödel's remark to Wang is quoted in Koellner, Part I, pp. 358–359.

#### Read on 23 November 2026, after every statement was locked and proved

- Corradini and Galvan, "Analysis of Penrose's Second Argument Formalised in DTK System", *Logic and Logical Philosophy* 31(3) (2022) 471–500, [doi:10.12775/LLP.2021.019](https://doi.org/10.12775/LLP.2021.019). Read in full, from a copy supplied by Eugene.
- Corradini and Galvan, "A Note on Gödel's First Disjunct Formalised in DTK System", *Logic and Logical Philosophy* 33(4) (2024) 555–565, [doi:10.12775/LLP.2024.025](https://doi.org/10.12775/LLP.2024.025). Read in full, from a copy supplied by Eugene.

Before that, only their abstracts were known: first roughly, from a search, when statement S4g was written, then exactly, from the publisher's records at Crossref.

#### Bibliographic details verified, text not read

- Koellner, "II: Penrose's New Argument", *Journal of Philosophy* 115(9) (2018) 453–484.
- Reinhardt, "The Consistency of a Variant of Church's Thesis with an Axiomatic Theory of an Epistemic Notion", *Revista Colombiana de Matemáticas* 19(1–2) (1985) 177–200.
- Reinhardt, "Epistemic Theories and the Interpretation of Gödel's Incompleteness Theorems", *Journal of Philosophical Logic* 15(4) (1986) 427–474.
- Carlson, "Knowledge, Machines, and the Consistency of Reinhardt's Strong Mechanistic Thesis", *Annals of Pure and Applied Logic* 105(1–3) (2000) 51–82.
- Gödel, "Some Basic Theorems on the Foundations of Mathematics and Their Implications" (1951), in *Collected Works* III (OUP 1995) 304–323; the disjunction is at p. 310 (as cited in Koellner Part I).
- Savelyev, [arXiv:2001.07592](https://arxiv.org/abs/2001.07592) (its arXiv comment: "superseded by arxiv:2208.04752") and [arXiv:2208.04752](https://arxiv.org/abs/2208.04752) (comment on v3: "The framework currently has gaps").

#### Unverified until the protocol checks them

- Penrose, *Shadows of the Mind* (1994), the rest of ch. 2–3 beyond pp. 72–77.
- Lindström, *Journal of Philosophical Logic* 30 (2001). Shapiro, *Journal of Philosophical Logic* 32 (2003).
- Suggested addition: Stern, "Proving that the Mind is Not a Machine?" (2018).

#### Prior art and dependencies, checked 22 November 2026

- [moritzbrantner/formal-logos](https://github.com/moritzbrantner/formal-logos) (formerly `truth-core`), [issue 366](https://github.com/moritzbrantner/formal-logos/issues/366), planned the same formalization. It was closed on 15 November 2026 as deferred when that project narrowed its scope; it never added Foundation and has no Lean file on the topic. Cited as prior art.
- Lean Zulip, public channels, searched for "Lucas Penrose", "anti-mechanist", "epistemic arithmetic", "Gödel's disjunction", "Koellner" and "Penrose": nothing relevant. Private channels can't be searched.
- GitHub code search (Lean files) and web search: no machine-checked version of the Lucas–Penrose argument, epistemic arithmetic, the knower paradox or Gödel's disjunction found.
- [FormalizedFormalLogic/Foundation](https://github.com/FormalizedFormalLogic/Foundation) (Apache-2.0), candidate pin `fbcfee52cb4a892087fa978366282a9ebd844f29` (12 November 2026; Lean v4.35.0, Mathlib v4.35.0). Its paper: Saitou and Noguchi, [arXiv:2609.13780](https://arxiv.org/abs/2609.13780).

---

The plan was assessed by Claude (Opus 5.5) and revised the same day by Claude (Fable 5.2) after reading Foundation and Koellner Part I, on 22 November 2026, from Eugene's brief. The work is done by AI agents and directed by Eugene Jhong. This page summarises [issue #19](https://github.com/ejhong/aletheia-lab/issues/19), which holds the full text.
