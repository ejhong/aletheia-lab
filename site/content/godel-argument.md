---
# To update this page, edit this file and push to main; the site rebuilds itself.
#   Tick a step:     change "- [ ]" to "- [x]".
#   Move a stage:    set its "Status:" line to done, in progress or not started.
#   Report results:  replace the note under "## Results" with text or a Markdown table.
#   Also update the "Where things stand" note and the "updated:" date below.
summary: What exactly does the Lucas–Penrose argument prove, and from which premises?
dek: What exactly does the Lucas–Penrose argument prove, and from which premises? The plan is to write the argument and its standard replies in Lean 4, so that a proof checker shows which premises carry which conclusion.
updated: 2026-11-23
---

> **Where things stand, 23 November 2026.** Stages 0, 1 and 2 are done. Thirty-five statements are locked and proved in Lean, using only Lean's three standard axioms. In short: Penrose's modest conclusion, that we are not running an algorithm we can know to be sound, is proved. His proof of the stronger conclusion, that the mind is no machine at all, does not establish it: the argument is valid, but two of its rules contradict themselves, and with the rules repaired it reaches only something weaker. The stronger conclusion itself is neither proved nor refuted. Nothing here touches Penrose's physics.

## The question

What exactly does the Lucas–Penrose argument prove, and from which premises? The plan is to formalize the argument and its standard analyses in Lean 4, a language in which a small trusted kernel checks every step of a proof, so that the kernel shows which premises carry which conclusion.

This settles what follows from what. It does not settle whether minds are machines.

Roughly, as the argument is usually summarised: Gödel's second incompleteness theorem says that a consistent formal system strong enough for basic arithmetic, whose axioms a machine can list, cannot prove its own consistency. Lucas and Penrose argued that a human mathematician can see that such a system is consistent, so human mathematical understanding is not the output of any such system. The replies turn on what the human would have to know for that to work: that the system is consistent, and which system it is.

## Why it matters

- **The atlas has an open claim on it.** Aletheia's claim [ORCH-C040](https://ejhong.github.io/aletheia/claims/ORCH-C040/), "Human mathematical understanding is not the execution of any knowably sound formal algorithm", is rated Unresolved in the atlas (as read on 22 November 2026). It sits in the atlas case on Orch OR, [Collapse, Not Computation](https://ejhong.github.io/aletheia/cases/orch-or/).
- **Prose hides premises; a proof checker does not.** In Lean every assumption has to be written into a theorem's statement, and the kernel rejects a proof that leans on anything else. That makes it possible to say exactly which premises each conclusion needs.
- **Most of the mathematics already exists.** The Foundation library has machine-checked Gödel's first and second incompleteness theorems, Löb's theorem and local reflection. What the lab adds is the mind/machine reading, the source locators, and a table of which premises carry which conclusion.
- **It appears not to have been done.** Searches on 22 November 2026 found no earlier machine-checked version of the Lucas–Penrose argument, epistemic arithmetic, the knower paradox or Gödel's disjunction. One project planned the same formalization and deferred it (see Sources).

The lab does not grade the atlas. A finished result is filed with Aletheia as an outside source, and Stage 1's report gives no verdict on ORCH-C040.

## The plan

Four stages. Each ends at a gate where Eugene decides what happens next (on GitHub, the label `needs:eugene`). The ticks below mark steps as they are finished.

### Stage 0 · Statements only
Status: done
Gate: Eugene reviews the checkers' divergences, then `lean/Statement.lean` is locked.

Write down exactly what will be proved, and check that it says what was meant, before proving anything.

- [x] Definitions, each with an English gloss and a locator to the passage it formalizes: formal system as r.e. theory; soundness; consistency; an idealized mind as a set K of sentences; "K is the theorem set of some machine"; and plain-arithmetic stand-ins for "K knows which machine" and "K knows the machine is sound".
- [x] Statements in `lean/GodelArgument/Statement.lean` as `def … : Prop`: 11 definitions and 13 statements, compiling against the pinned Foundation library. Proofs elsewhere must have exactly those types, so the lock covers the statements while proofs stay free to change.
- [x] The proof-lane Lean CI, set up on the question's branch, with a build-time check that a theorem uses only Lean's three standard axioms.
- [x] The statement check. OpenAI `gpt-6.2-astra` and Google `gemini-4-neon` each translated every Lean statement back into English blind, then compared it with the source passage. Three deliberately wrong statements were mixed in. In the final round both checkers caught all three. Their criticism in the earlier rounds led to five statements being rewritten. Of 17 items with a source passage, 15 ended as faithful or faithful with caveats from both checkers; two divergences are accepted with reasons and will be reported with the results. One statement, the halting form, could not be checked against its source because *Shadows of the Mind* is not yet in hand.
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
Condition: Eugene approved it on 23 November 2026. All three tiers are done, for $27.56 in statement checks.
Gate: Each tier gets its own statement check, entered through `amendments.md` before anything in it is proved.

This is where the new work is: theories in which the knower K is an operator with its own axioms (K1–K4), as in Reinhardt's epistemic arithmetic. The targets, as stated in Koellner (2018, Part I), are Reinhardt's Theorem 3 (p. 354), Theorem 5 (p. 355) and Theorem 6 (p. 357). Theorems 7 and 8, consistency results by Reinhardt and by Carlson, are cited, not proved. Statements are to be taken from Reinhardt's own papers, since Koellner's summary is informal in places.

- [x] **2A, small.** Done 23 November. An abstract layer: K is an operator on sentences, and each principle about it is a stated assumption. Nine statements locked after statement checks, then proved: Reinhardt's theorem that a knower exceeds any system it knows to be sound; his absolute version of the second incompleteness theorem; a sentence-by-sentence counterpart of his result that knowing which system you are is contradictory, with the core of his own proof; and two results showing which assumptions cannot be dropped. Seven were locked before Reinhardt's 1985 paper was in hand. It arrived the same day, corrected one of them, and two more were added from it.
- [x] **2B.** Done 23 November, on a smaller scope than first planned. Reinhardt's paper shows that his two central theorems need no arithmetic. So this tier builds a real formal language with the knowledge operator and quantifiers, with his proof system, and proves those two theorems in it: knowing which set you are is refuted, and being some set gives a truth you cannot know. Six statements, locked after two rounds of statement check, then proved. Epistemic arithmetic itself, with its arithmetic and its truth predicate, is not built.
- [x] **2C.** Done 23 November. Penrose's new argument, in the eight steps Koellner's Part II gives it, in an abstract setting with truth, knowledge and determinateness as operations on sentences. Seven statements, locked after two rounds of statement check, then proved: the argument is valid from its rules; each rule, unrestricted, is inconsistent; with restricted rules the argument needs two statements to be determinate; and for a determinate version of the thesis it yields only something weaker. Koellner's system itself is not built, so his theorems that the thesis is indeterminate and that neither side of the disjunction can be proved are cited, not re-proved.

### Stage 3 · Stretch
Status: not started
Condition: Only after reporting on the earlier stages.

- [ ] Independence results by model construction.
- [ ] The untyped-truth inconsistency.

Out of scope: Carlson's consistency proof, which is cited instead. Dropped for now: the stably-computable version, because its author's own arXiv comment on 2208.04752v3 says "The framework currently has gaps".

## The rules

These come from the lab's proof lane and from issue #19.

- **A statement check by other vendors' models.** Before anything is proved, models from two other vendors translate each formal statement back into English without seeing the lab's gloss or the proof, and list where it differs from the source passage. Deliberately wrong statements are mixed in to test the checkers. Unresolved divergences are reported in `RESULTS.md`.
- **The lock.** The statements are definitions in `lean/Statement.lean`. Once checked, the file's SHA-256 is committed in `protocol.lock` before any proof. A proof can change freely but cannot quietly prove something else. A corrected statement is a new file plus a dated amendment, never an edit.
- **No `sorry`.** No `sorry`, no `admit`, no new `axiom`. Each headline theorem may depend only on `propext`, `Classical.choice` and `Quot.sound`, checked inside the build so that a violation fails it.
- **No vacuous theorems.** Every assumed premise is a hypothesis in the theorem's statement, and each headline theorem comes with an instance showing its hypotheses can hold together (for example PA in the standard model). Nothing may be true only because its premises contradict each other.
- **Keep "is a machine" and "knows which machine" apart.** The whole dispute lives in that gap. In Koellner's notation: WMT `∃e (K = F_e)`, SMT `K∃e (K = F_e)`, SSMT `∃e K(K = F_e)`. Stage 1 can express "knows which machine" only by proxy, because plain arithmetic has no way to say "me"; each gloss says which side of that trade-off its statement is on.
- **Credit the library.** Where a result restates a theorem Foundation already proves, `RESULTS.md` names that theorem. Incompleteness is not rebuilt from scratch.

## Results

> **Stage 1, 22 November 2026.** All thirteen statements are proved. This is not a verdict on ORCH-C040, and it does not say whether minds are machines.

Model an idealized mind as the set K of arithmetic statements it would ever accept, and a machine as a formal system F whose axioms can be listed mechanically. Then:

- **The conditional holds.** If a consistent K is exactly what F proves, K does not contain F's consistency statement. In the form Penrose's conclusion is usually given: a consistent, logically closed mind that accepts "whatever F proves is so" contains everything F proves and something more. It is not F.
- **Being a sound machine is not contradictory.** Peano arithmetic is sound, consistent and mechanical, and cannot prove its own true consistency statement. The machine even proves "if I am consistent, my Gödel sentence holds". What a mind would need, to outdo F, is knowledge that F is consistent; supplying it yields a second machine with a blind spot of its own.
- **The troublesome premise is self-knowledge of soundness, not mechanism.** Any system that can talk about its own beliefs in the standard way and asserts its own consistency is inconsistent, machine or not. Asserting the soundness of a different sound system is harmless.
- **Gödel's disjunction holds.** If everything in K is true, either no formal system generates K, or some true statement of the simple "for all numbers" kind is undecided by K.

So the argument establishes "not a machine you know to be sound". It does not establish "not a machine".

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

**How it was checked.** The Lean kernel checked every proof; the build fails if any theorem uses more than Lean's three standard axioms. For each statement there is also a proof that its assumptions can hold together, so nothing is true only because its premises clash. Before anything was proved, models from OpenAI and Google translated each statement back into English blind and compared it with the source; in the final round both caught all three deliberately wrong statements mixed in.

**What is not new.** The underlying theorems (Gödel's two incompleteness theorems, Löb's theorem, reflection) are already proved in the Foundation library. The lab adds the mind-and-machine reading, the source locators and the table of premises.

**Limits that qualify the table.**

- Plain arithmetic cannot say "I am this machine" or "I know". Set membership stands in for knowing. One checker judged the second row a stand-in, not a formalization of Gödel's remark; that is right. Stage 2A's third row is the version with a knowledge operator.
- Penrose's second argument is not covered by Stage 1. Tier 2C of Stage 2 takes it up; see below.
- Gödel's words are quoted through Koellner; that book was not in hand. Penrose's were checked against photographs of pp. 72–77 of *Shadows of the Mind*.
- Penrose's own conclusion on p. 76 is that mathematicians are not using a "knowably sound algorithm". That is the version the proofs support. He calls the claim that thought is non-computational "the stronger deduction".
- Nothing here tests whether a person is well modelled as a consistent, logically closed set of statements.

> **Stage 2A, 23 November 2026.** All nine statements are proved. They are about an abstract knowledge operator, not about epistemic arithmetic itself, and this too is no verdict on ORCH-C040.

Add an operator K, read "it is known that". F is any system; it need not be a machine. Then:

- **A knower exceeds any system it knows to be sound.** If it is known, sentence by sentence, that whatever F asserts is so, then something is known that F does not assert.
- **A knower that knows a system captures all it knows cannot know that system consistent.** Nothing is assumed about F. "Consistent" means that F never asserts a sentence together with its negation. This is Reinhardt's absolute version of the second incompleteness theorem.
- **A correction.** This page first said that theorem needed an extra condition on F which the literature leaves out. That was wrong. Reinhardt's own paper states it with no condition; what a later summary leaves out is his definition of "consistent". The statement written before his paper was read is still true, but it is a weaker result, not a repair of his.
- **Knowing which system you are is contradictory.** A logical core of this needs no arithmetic at all, and is the heart of Reinhardt's own proof.
- **What carries it is knowing that your knowledge is true.** Take K to be "Peano arithmetic proves". It satisfies every other assumption, trivially knows which system it is, and no contradiction arises. A machine's own notion of proof passes every test of a knower here except knowing that what it proves is true.

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

**How it was checked.** As in Stage 1. The checks ran before each lock and changed the statements three times. Both checkers caught all six planted errors. One divergence stands: Google's model judged the "contradiction follows" row weaker than Reinhardt's theorem, because it works sentence by sentence for a fixed F and has no quantifier over machines inside the language. That is right, and closing the gap is tier 2B.

**Limits.** The layer is abstract: facts the literature derives from arithmetic are assumed here, and nothing with a quantifier inside the language is expressed. Reinhardt's 1985 paper was read only after the first seven statements were locked; his other papers were not read.

> **Tier 2B, 23 November 2026.** All six statements are proved, in a formal language that has the knowledge operator and real quantifiers. No verdict on ORCH-C040.

Read U(e, x) as "x belongs to the e-th set"; think of the outputs of the e-th machine. Then:

- **Knowing which set you are is refuted, inside the language.** There is no e such that it is known that the things known not to belong to themselves are exactly the e-th set.
- **Being some set gives a truth you cannot know.** If for some e those things are exactly the e-th set, known or not, then for some e: e is not in the e-th set, and that can never be known. This is Gödel's disjunction: either the knower is no such set, or there are truths it can never know.
- **"What is proved is known" is derived, not assumed**, and the logic is consistent.

The first two differ only in where "it is known that" stands.

| Claim | Lean name | Axioms for K used | Status |
|---|---|---|---|
| What the logic proves, it proves to be known | `necessitationIsDerived` | distribution; known to be known; K of each axiom | Proved |
| Every theory proves ¬∃e K∀x(K¬U(x,x) ↔ U(e,x)) | `knowingWhichSetRefuted` | distribution; what is known is so, and K of it; K∀xφ → ∀xKφ | Proved; Reinhardt's Theorem 5 |
| If T proves ∃e∀x(K¬U(x,x) ↔ U(e,x)), T proves ∃e(¬U(e,e) ∧ ¬K¬U(e,e)) | `thesisGivesUnknownTruth` | what is known is so | Proved; Reinhardt's Theorem 3 |
| The same, as "absolutely undecidable" | `thesisGivesAbsolutelyUndecidable` | what is known is so | Proved |
| The same, known | `knownThesisGivesKnownUnknownTruth` | as the first and third rows | Proved |
| The logic does not prove falsehood | `logicIsConsistent` | none | Proved |

**How it was checked.** As before, and this time the definition of the logic was checked too. Both checkers caught all three planted errors, one of them inside the axioms. Round 1 found the draft allowed axioms with free variables; they are now sentences. No divergence stands.

**Limits.** The language is a fragment with no arithmetic, so "the e-th machine" is a reading: nothing says the sets are computable. Only the one diagonal instance of Reinhardt's schema is stated. That "I am some set" is consistent with these axioms is Reinhardt's result, cited, not proved here.

> **Tier 2C, 23 November 2026.** All seven statements are proved. They concern Koellner's eight-step rendering of Penrose's second argument, not Penrose's text, and they give no verdict on ORCH-C040.

Penrose's second argument is the one meant to show "I am not the machine F", for any F. It uses three principles: what is known is true; whatever is so is true; whatever is proved is known. Truth and knowledge are applied to sentences that themselves speak of truth and knowledge.

- **The argument is valid.** From those rules and six facts taken from arithmetic, "I am not F" follows. If it fails, it fails in its rules.
- **Its rules contradict themselves.** "Whatever is so is true" yields a contradiction as soon as there is a liar sentence. "Whatever is proved is known" yields one as soon as a sentence says of itself that it is not known. From contradictory rules anything follows.
- **Repaired, it needs something it lacks.** Restrict both rules to sentences that are true or false. The argument then needs two of its own statements to be of that kind. They are not, if "I am F" is not, and Koellner proves that it is not. That theorem is cited, not re-proved here.
- **For a safe version of "I am F", it stops short.** Restricted to arithmetic, "I am F" is true or false, but then the last step fails. What is left is weaker: something is known that F does not prove.

| Claim | Lean name | Status |
|---|---|---|
| The eight steps yield "I am not F" from the unrestricted rules | `penroseArgumentValid` | Proved |
| "Whatever is so is true", unrestricted, is inconsistent | `unrestrictedTInInconsistent` | Proved |
| "Whatever is proved is known", unrestricted, is inconsistent | `unrestrictedKIntroInconsistent` | Proved; stronger than Koellner's remark |
| Knowing every logical validity is inconsistent with self-applicable truth | `knownValiditiesInconsistent` | Proved |
| With restricted rules the argument works if two named statements are determinate | `penroseArgumentUnderDeterminateness` | Proved |
| If "I am F" is indeterminate, so are those two statements | `stepsIndeterminateIfThesisIs` | Proved; a reduction of a theorem Koellner states without proof |
| For a determinate "I am F": something is known that F does not prove | `restrictedThesisGivesUnprovableKnowledge` | Proved; the lab's own |

**How it was checked.** As before. Both checkers caught all three planted errors. Round 1 found one statement using the wrong determinateness premises; it now uses the two statements Koellner names. One divergence stands: the third row is stronger than the remark of Koellner's that it supports.

**Limits.** A reconstruction was checked, not Penrose's own wording. Koellner's system is not built, so three of his theorems are cited, not proved. Only one theory of self-applicable truth is considered. The reply to Koellner by Corradini and Galvan could not be obtained and is not covered.

Full report: [`RESULTS.md`](https://github.com/ejhong/aletheia-lab/blob/main/questions/godel-argument/RESULTS.md). Proofs: [`lean/GodelArgument/`](https://github.com/ejhong/aletheia-lab/tree/main/questions/godel-argument/lean/GodelArgument). Cost: $40.26, all on statement checks.

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

#### Bibliographic details verified, text not read

- Koellner, "II: Penrose's New Argument", *Journal of Philosophy* 115(9) (2018) 453–484.
- Reinhardt, "The Consistency of a Variant of Church's Thesis with an Axiomatic Theory of an Epistemic Notion", *Revista Colombiana de Matemáticas* 19(1–2) (1985) 177–200.
- Reinhardt, "Epistemic Theories and the Interpretation of Gödel's Incompleteness Theorems", *Journal of Philosophical Logic* 15(4) (1986) 427–474.
- Carlson, "Knowledge, Machines, and the Consistency of Reinhardt's Strong Mechanistic Thesis", *Annals of Pure and Applied Logic* 105(1–3) (2000) 51–82.
- Gödel, "Some Basic Theorems on the Foundations of Mathematics and Their Implications" (1951), in *Collected Works* III (OUP 1995) 304–323; the disjunction is at p. 310 (as cited in Koellner Part I).
- Corradini and Galvan, "Analysis of Penrose's Second Argument Formalised in DTK System", *Logic and Logical Philosophy* 31(3) (2022) 471–500, [doi:10.12775/LLP.2021.019](https://doi.org/10.12775/LLP.2021.019); a follow-up in the same journal, vol. 33 (2024).
- Savelyev, [arXiv:2001.07592](https://arxiv.org/abs/2001.07592) (its arXiv comment: "superseded by arxiv:2208.04752") and [arXiv:2208.04752](https://arxiv.org/abs/2208.04752) (comment on v3: "The framework currently has gaps").

#### Unverified until the protocol checks them

- Penrose, *Shadows of the Mind* (1994) ch. 2–3; "Beyond the Doubting of a Shadow", *Psyche* 2 (1996).
- Lucas, "Minds, Machines and Gödel", *Philosophy* 36 (1961).
- Chalmers, "Minds, Machines, and Mathematics", *Psyche* 2 (1995). Lindström, *Journal of Philosophical Logic* 30 (2001). Shapiro, *Journal of Philosophical Logic* 32 (2003).
- Suggested addition: Stern, "Proving that the Mind is Not a Machine?" (2018).

#### Prior art and dependencies, checked 22 November 2026

- [moritzbrantner/formal-logos](https://github.com/moritzbrantner/formal-logos) (formerly `truth-core`), [issue 366](https://github.com/moritzbrantner/formal-logos/issues/366), planned the same formalization. It was closed on 15 November 2026 as deferred when that project narrowed its scope; it never added Foundation and has no Lean file on the topic. Cited as prior art.
- Lean Zulip, public channels, searched for "Lucas Penrose", "anti-mechanist", "epistemic arithmetic", "Gödel's disjunction", "Koellner" and "Penrose": nothing relevant. Private channels can't be searched.
- GitHub code search (Lean files) and web search: no machine-checked version of the Lucas–Penrose argument, epistemic arithmetic, the knower paradox or Gödel's disjunction found.
- [FormalizedFormalLogic/Foundation](https://github.com/FormalizedFormalLogic/Foundation) (Apache-2.0), candidate pin `fbcfee52cb4a892087fa978366282a9ebd844f29` (12 November 2026; Lean v4.35.0, Mathlib v4.35.0). Its paper: Saitou and Noguchi, [arXiv:2609.13780](https://arxiv.org/abs/2609.13780).

---

The plan was assessed by Claude (Opus 5.5) and revised the same day by Claude (Fable 5.2) after reading Foundation and Koellner Part I, on 22 November 2026, from Eugene's brief. The work is done by AI agents and directed by Eugene Jhong. This page summarises [issue #19](https://github.com/ejhong/aletheia-lab/issues/19), which holds the full text.
