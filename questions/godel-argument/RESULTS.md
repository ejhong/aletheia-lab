# Machine-check the Gödel argument: Stage 1 results

Issue #19 · Lane: proof · Protocol locked 2026-11-22T17:49:01Z · No amendments

## Answer

All thirteen locked statements are proved in Lean 4. Each proof depends only on Lean's three standard axioms, and
the build passes in CI with warnings treated as errors
([run 45051792273](https://github.com/ejhong/aletheia-lab/actions/runs/45051792273), commit `d1968cd`).

The underlying mathematics is not new. Gödel's two incompleteness theorems, Löb's theorem and the reflection
results come from the Foundation library (Saitou and Noguchi, arXiv:2609.13780). What the lab adds is the reading
in terms of minds and machines, the tie from each statement to a source passage, and the table of premises below.

## What follows from what (plain summary)

Model an idealized mind as the set K of arithmetic statements it would ever accept, and a machine as a formal
system F whose axioms can be listed mechanically.

1. **The conditional holds.** If a consistent K is exactly what F proves, then K does not contain F's consistency
   statement. Put the way Penrose's conclusion is usually put: a consistent, logically closed mind that accepts
   "whatever F proves is so" contains everything F proves and something more. It is not F.
2. **Being a sound machine is not contradictory.** Peano arithmetic is one: sound, consistent, mechanical, and
   unable to prove its own true consistency statement. The machine even proves "if I am consistent, then my Gödel
   sentence holds". So what a mind would need, to outdo F, is knowledge that F is consistent. Supplying that
   knowledge yields a second machine with a blind spot of its own.
3. **The troublesome premise is self-knowledge of soundness, not mechanism.** Any system that can talk about its
   own beliefs in the standard way and asserts its own consistency is inconsistent, whether or not it is a
   machine. Asserting the soundness of a *different* sound system is harmless.
4. **Gödel's disjunction holds.** If everything in K is true, then either no formal system generates K, or some
   true statement of the simple "for all numbers" kind is left undecided by K.

So the argument establishes "not a machine you know to be sound". It does not establish "not a machine". Whether
people are well modelled by such a K is outside what was checked. This is no verdict on ORCH-C040.

## Results table

"Premises required" lists every assumption in the theorem statement. F is always a recursively enumerable set of
axioms unless noted; "includes basic arithmetic" means it proves every theorem of 𝗜𝚺₁. Lean names are in
`lean/GodelArgument/Results.lean`; the statements are in `lean/GodelArgument/Statement.lean`.

| Claim | Lean name | Premises required | Status | Source locator | Foundation theorem used |
|---|---|---|---|---|---|
| S1a. A consistent mind that is F's theorem set does not contain Con(F) | `penroseConditional` | K is exactly F's theorems; K consistent; F includes basic arithmetic | Proved | Chalmers 1995, §1, item (c); Koellner 2018a, p. 345 | `craig_consistent_unprovable_of_RE` |
| S1a′. No consistent mind is F's theorem set and contains Con(F) | `noConsistentMindKnowsOwnMachineConsistent` | K consistent; F includes basic arithmetic | Proved | Koellner 2018a, pp. 358–359 (Gödel via Wang) | as S1a |
| S1a″. A mind that accepts F's soundness strictly exceeds F | `knownSoundMachineIsExceeded` | K consistent, deductively closed, proves basic arithmetic; K contains "if F proves σ then σ" for every σ; F includes basic arithmetic | Proved | Koellner 2018a, pp. 354, 356, quoting Penrose 1994, p. 76 | D1 of the standard provability predicate; `craig_consistent_unprovable_of_RE` |
| S1b(i). The standard objection: a sound, consistent machine lacking its own true Con | `standardObjectionWitness` | none (it is about Peano arithmetic) | Proved | Chalmers 1995, §1 | PA instances; `craig_consistent_unprovable_of_RE` |
| S1b(ii). F proves "if F is consistent then G_F" | `machineProvesConditional` | F has a Δ₁ presentation and includes basic arithmetic | Proved | Chalmers 1995, §1, item (b) | `gödel_iff_con` |
| S1b(iii). The second machine: F + Con(F) is a sound machine, proves Con(F), cannot prove its own Con | `secondMachine` | F sound; F includes basic arithmetic | Proved | Lucas 1961, pp. 116–117 | `craig_consistent_unprovable_of_RE`, twice |
| S1c. A system that asserts its own consistency is inconsistent | `chalmersPoint` | a belief predicate satisfying derivability conditions D1–D3; diagonalization over a base theory the system extends; the system proves ¬𝔅(⊥). No assumption that it is a machine | Proved | Chalmers 1995, §2 | abstract `con_unprovable` |
| S1c′. A system that asserts its own soundness, sentence by sentence, is inconsistent | `selfSoundnessInconsistent` | as S1c, with "proves 𝔅(σ) → σ for every σ" | Proved | Chalmers 1995, §2, conclusion | abstract `löb_theorem` |
| S1c″. A sound system plus a true statement is sound | `soundPlusTrueIsSound` | T's axioms true; σ true | Proved | Chalmers 1995, §2, step (2) | `models_of_provable` |
| S1c‴. A sound T plus the assertions of T's soundness is sound | `soundPlusItsSoundnessIsSound` | T's axioms true; T has a Δ₁ presentation | Proved | the lab's contrast case; applies Chalmers 1995, §2, step (2) | `models_localReflectionOn` |
| S1d. Gödel's disjunction | `godelDisjunction` | everything in K is true | Proved | Koellner 2018a, p. 349, quoting Gödel 1951, p. 310 | `craig_consistent_unprovable_of_RE` |
| S1d′. Variant for sets not closed under deduction | `godelDisjunctionRE` | everything in K is true | Proved | as S1d | `exists_true_but_unprovable_sentence_of_RE_of_sigma1sound` |
| S1e. Penrose's argument in halting form | `penroseTuring` | A is recursively enumerable; whenever A certifies n, computation n does not halt on input n | Proved | Penrose 1994, §2.5 (`unverified`: book not in hand) | none; Mathlib's `Nat.Partrec.Code` |

**Non-vacuity.** For every statement that starts from assumptions, `lean/GodelArgument/NonVacuity.lean` proves
that the assumptions can hold together, with Peano arithmetic as the witness. For S1c and S1c′ it shows that the
structural assumptions hold of a consistent system, so the contradiction comes from the added self-assertion.

**Audit.** Twenty-three theorems (13 results, 10 non-vacuity instances) pass `#assert_standard_axioms` inside the
build: each depends only on `propext`, `Classical.choice` and `Quot.sound`. The source has no `sorry`, `admit`,
`native_decide` or `axiom`. Toolchain Lean v4.35.0; Foundation at commit
`fbcfee52cb4a892087fa978366282a9ebd844f29`; all dependencies pinned in `lean/lake-manifest.json`.

## Statement check

Before the lock, OpenAI `gpt-6.2-astra` and Google `gemini-4-neon` each translated every statement back into
English without seeing the source or the lab's glosses, then compared it with the source passage. Three
deliberately wrong statements were mixed in. Details: `statement-check/REPORT.md`, and the protocol's last section.

- **Planted errors:** in the final round both checkers caught all three. In round 1 Google rated one as minor;
  that decoy was badly chosen (it was logically equivalent to the correct statement) and was replaced.
- **Real items:** of 17 with a source passage, 15 ended as `faithful` or `faithful_with_caveats` from both.
- **The check changed the statements.** Five were rewritten after round 1, and one of the rewrites again after
  round 2. The protocol lists each change.

**Unresolved divergences.** These stand, and qualify the results above.

| Item | Divergence | Effect on what is claimed |
|---|---|---|
| S1a′ | OpenAI: `divergent` against Gödel's remark as reported by Wang. The remark is about *knowing* which machine one is and *knowing* that it works correctly. The Lean says K *is* F's theorem set and *contains* a consistency sentence. Google: `faithful_with_caveats`. | S1a′ is a theorem about arithmetic, offered as a stand-in. It is not a formalization of Gödel's remark. That needs a knowledge operator (Koellner's Theorem 6; Stage 2). |
| S1d′ | OpenAI: `divergent`. "K is not recursively enumerable" is not the passage's "no formal system has K as its theorem set". Google: `faithful_with_caveats`. | S1d′ is a variant. S1d is the statement tied to the passage. |
| S1e | Not checked against a passage. *Shadows of the Mind* §2.5 was not in hand; Penrose's 1996 reply (§2.1) confirms only that §2.5 exhibits a computation "C_k(k)" obtained from an algorithm A. | S1e is a correct theorem of the right general shape. Whether it matches Penrose's text is unverified. |

**Caveats raised on most items**, rated minor by both checkers:

- Membership in a set K stands in for "knows" or "accepts". Plain arithmetic has no knowledge operator.
- The language is fixed to first-order arithmetic, and "formal system" is read as a recursively enumerable axiom
  set including 𝗜𝚺₁. The sources speak more loosely of "sufficiently strong" systems.
- The consistency statement is tied to one description of F (Foundation's Craig presentation). Different
  descriptions of the same axioms give different sentences.
- Each statement is about every K of a given kind, not about a designated human K.
- Soundness and truth mean truth in the standard natural numbers, judged in Lean's own logic.

## Limits

- **"Me" is missing.** Arithmetic cannot say "I am this machine". Stage 1 therefore shows one side of a trade-off:
  a system can know its own code, but then not its own consistency. The other side, a knower that is truthful by
  axiom and cannot know its own code (Reinhardt), needs Stage 2.
- **Penrose's second argument is not covered.** The "new argument" of *Shadows* ch. 3, and Koellner's analysis of
  it in a type-free theory of truth, are Stage 2C. Chalmers's reply to it (S1c) is covered.
- **Secondary quotation.** Penrose's conclusion (p. 76) is quoted through Koellner, and Gödel's disjunction through
  Koellner. Neither book was in hand.
- **Idealization.** Nothing here tests whether a person is a consistent, deductively closed set of sentences.
- **Checked by models.** The statement check was done by language models, calibrated only by three planted errors.
- **Exploration before the lock.** As the protocol allows, a proof sketch of each statement was compiled before
  locking, to make sure none was false as written (`explore/Stage1Sketch.lean`). The statements were then fixed by
  the lock and the proofs here were written against them.

## Amendments

None.

## Spending

$12.38 of the $50 budget, all on the statement check (`SPENDING.md`).

## Who did the work

AI agents did this work, directed by Eugene Jhong. All dates are 2026-11-22.

- **Anthropic, Claude Opus 5.5:** first assessment of the brief; issue #19.
- **Anthropic, Claude Fable 5.2:** second assessment, source reading, statements, protocol, statement-check
  design, proofs and this document.
- **OpenAI, `gpt-6.2-astra`** and **Google, `gemini-4-neon`:** the statement check.
- **xAI, `grok-4.7`:** named as tie-breaker; not needed.
- **The Lean 4 kernel** checked the proofs.

## What this means

For sixty years people have argued about whether Gödel's theorem shows that the human mind is not a machine. This
work had a proof checker go through the logical core of that argument and the standard replies to it. The checker
confirms one thing the argument's defenders say: if your mind were a particular machine, you could not also know
that machine to be reliable. It also confirms what the critics say: that is not the same as showing your mind is
not a machine, because a machine can be perfectly reliable without being able to know it, and because "I know I
am reliable" leads to contradiction for any reasoner of this kind, machine or not. So the old argument proves
something real but smaller than its conclusion. Penrose's later, subtler argument is not settled here; that is
the next stage.
