# Machine-check the Gödel argument

Issue: #19 · Lane: proof · Budget: $50 (Stages 0–1: statement checks and any paid sources)

## Question

What does the Lucas–Penrose argument against mechanism prove, and from which premises? Concretely: which of the
fourteen statements S1a–S1e in `lean/GodelArgument/Statement.lean` are theorems of Lean 4 with the pinned Foundation
library, using no axioms beyond Lean's standard three?

This settles what follows from what. It does not settle whether minds are machines.

## Why it matters

Aletheia claim ORCH-C040, "human mathematical understanding is not any knowably sound algorithm", is Unresolved.
The logic has been argued on paper since Lucas (1961). As far as the lab could find on 2026-11-22 (Lean Zulip
public channels, GitHub code search, web search), no machine-checked version of the argument and its standard
analyses exists. A premise table checked by the Lean kernel lets the atlas see which conclusion rests on which
premise. The lab files the result with the atlas; it does not grade the claim.

## Data and sources

No datasets. Sources are papers; the copies read are in `MANIFEST.md`, and the passages each statement is tied
to are quoted in `statement-check/passages.md`.

The one software dependency is FormalizedFormalLogic/Foundation (Apache-2.0), pinned in `lean/lakefile.toml` to
commit `fbcfee52cb4a892087fa978366282a9ebd844f29`, with every transitive dependency pinned in
`lean/lake-manifest.json` and the toolchain in `lean/lean-toolchain` (Lean v4.35.0).

## Statements and their sources

Definitions (D) and Stage 1 statements (S). The Lean text is authoritative; the gloss is a reading aid.

| Name in `Statement.lean` | Gloss | Source passage |
|---|---|---|
| D1 `Mind` | The set K of arithmetic sentences an idealized mind would accept | Koellner 2018a, pp. 350–351 |
| D2 `IsTrue` | True in the standard natural numbers | Koellner 2018a, p. 350 (T) |
| D3 `Sound` | Everything in K is true (K ⊆ T) | Koellner 2018a, p. 349 |
| D4 `Consistent` | No contradiction is derivable from K | Koellner 2018a, pp. 344–345 |
| D5 `IsTheoremSetOf` | K is exactly what F proves | Koellner 2018a, p. 350; Lucas 1961, p. 115 |
| D6 `IsMechanical` | K is the theorem set of some r.e. axiom set (WMT) | Koellner 2018a, p. 357 |
| D7 `Con` | The consistency statement of F, for one fixed description of F | Koellner 2018a, p. 345 |
| D7′ `KnowsOwnMachineConsistent` | K is F's theorem set and contains Con(F) | Koellner 2018a, pp. 358–359 (Gödel via Wang) |
| D8 `ContainsSoundnessOf` | For every σ, K contains "if F proves σ then σ" | Koellner 2018a, p. 354 (the pointwise scheme) |
| D9 `IsPi1` | σ is a Π₁ sentence | Koellner 2018a, p. 345 |
| S1a `PenroseConditional` | A consistent K that is the theorem set of F does not contain Con(F) | Chalmers 1995, §1, item (c); Koellner 2018a, p. 345 |
| S1a′ `NoConsistentMindKnowsOwnMachineConsistent` | No consistent K satisfies D7′ | Koellner 2018a, pp. 358–359 |
| S1a″ `KnownConsistentMachineIsExceeded` | If K contains F's theorems and Con(F), K strictly exceeds F | Koellner 2018a, pp. 354, 356 |
| S1a‴ `KnownSoundMachineIsExceeded` | If K contains F's theorems and F's soundness (D8), K strictly exceeds F | Koellner 2018a, pp. 354, 356, quoting Penrose 1994, p. 76 |
| S1b(i) `StandardObjectionWitness` | PA's theorems are mechanical, sound and consistent, and lack the true sentence Con(PA) | Chalmers 1995, §1 |
| S1b(ii) `MachineProvesConditional` | F itself proves "if F is consistent then G_F" | Chalmers 1995, §1, item (b) |
| S1b(iii) `SecondMachine` | For any sound F: F + Con(F) is again a sound machine, proves Con(F), and cannot prove its own consistency statement | Lucas 1961, pp. 116–117 |
| S1c `ChalmersPoint` | A system satisfying Chalmers's (1)–(3) that asserts its own consistency is inconsistent; no machine assumption | Chalmers 1995, §2 |
| S1c′ `SelfSoundnessInconsistent` | The same for asserting one's own soundness, sentence by sentence (Löb) | Chalmers 1995, §2, conclusion |
| S1c″ `SoundPlusTrueIsSound` | A sound system plus a true statement is sound | Chalmers 1995, §2, step (2) |
| S1c‴ `SoundPlusItsSoundnessIsSound` | A sound T plus the assertions of T's soundness is sound | The lab's contrast case; applies Chalmers 1995, §2, step (2) |
| S1d `GodelDisjunction` | For sound K: no formal system has K as its theorem set, or some true Π₁ sentence is undecided by K | Koellner 2018a, p. 349, quoting Gödel 1951, p. 310 |
| S1d′ `GodelDisjunctionRE` | For sound K, not necessarily deductively closed: K is not r.e., or some true sentence is undecided by K | as S1d |
| S1e `PenroseTuring` | No sound r.e. certifier of non-halting certifies its own diagonal case | Penrose 1994, §2.5 (book not in hand; `unverified`) |

## Method

### Stage 0: statements, then the statement check, then the lock

1. Write the definitions and statements as `def … : Prop` in `lean/GodelArgument/Statement.lean`. The file must
   compile against the pinned library.
2. Exploration is allowed before the lock, in `explore/`, to make sure no statement is false as written. Nothing
   there is a finding.
3. Run the statement check, `statement-check/run.py`:
   - Checkers: OpenAI `gpt-6.2-astra` (reasoning effort high) and Google `gemini-4-neon`. xAI `grok-4.7` is the
     tie-breaker, run only if the two disagree on an item's verdict.
   - Phase A, blind: the checker gets the notation key, the definitions and one target, with comments removed
     and the lab's names replaced by neutral labels. It translates the target into English.
   - Phase B: the same checker is shown the source passage(s) and the claim, and returns a verdict (`faithful`,
     `faithful_with_caveats`, `divergent`) with each divergence rated major or minor.
   - Three planted wrong items (`statement-check/items.json`, "decoys") are mixed in. A planted error is caught
     when the verdict is `divergent`.
   - The check may be run in rounds. Each round's inputs and raw outputs are kept (`statement-check/round1/` is
     the first draft; `statement-check/out/` is the round that the locked statements went through).
   - The exact prompts are the constants `PROMPT_A` and `PROMPT_B` in `run.py`. Raw outputs go in
     `statement-check/out/`, the summary in `statement-check/REPORT.md`.
4. Act on the report before locking:
   - A major divergence on a real item is fixed in `Statement.lean` (and the item re-checked), or accepted with
     the reason written in the table below.
   - If a checker misses a planted error, its `faithful` verdicts are not relied on; say so in `RESULTS.md`.
   - Unresolved divergences are carried into `RESULTS.md`.
5. Eugene reviews the report. Then `python scripts/lock.py questions/godel-argument`, committed on its own.

### Stage 1: proofs

6. Prove each S-statement in `lean/GodelArgument/` as `theorem name : Statement.Name`. Where the proof is a
   restatement of a Foundation theorem, the results table names that theorem.
7. Non-vacuity: for every statement that starts from assumptions (all except S1b(i), which is itself a concrete
   instance), also prove an instance showing the assumptions can hold together. For S1c and S1c′, whose
   conclusion is inconsistency, the instance shows that assumptions (1)–(3) hold of a consistent system.
8. Audit: `#assert_standard_axioms` on every headline theorem, inside the build. CI (`.github/workflows/lean.yml`)
   builds with warnings as errors and rejects `sorry`, `admit`, `native_decide` and new `axiom` declarations.
9. Write `RESULTS.md`: a table of claim / Lean name / premises required / status / source locator; the statement
   check outcome including every unresolved divergence; amendments; models, vendors and dates; and a plain
   summary under 300 words of what follows from what, with no verdict on ORCH-C040.

### Later stages

Stage 2 (epistemic arithmetic: Koellner 2018a Theorems 3, 5, 6) and anything after it are not covered by this
lock. Each adds a new statement file with its own statement check, entered in `amendments.md` and locked with
`scripts/lock.py --statement` before any proof. Stage 2 starts only if Eugene approves it after Stage 1.

## What would count

- **For** a statement: CI builds its proof with standard axioms only. Conclusion: the statement holds as
  formalized, under the premises in its hypotheses, to the extent the statement check found it faithful.
- **Against** a statement: a Lean proof of its negation, or a counterexample to it. Conclusion: the formalized
  claim is false; report it, and say whether the fault is in the argument or in our formalization.
- **Inconclusive:** no proof and no refutation within the budget; or a major statement-check divergence that
  could not be resolved, in which case the theorem is reported as proved but not as a formalization of the source.

A full set of proofs would support exactly this and no more: the conditional form of the Lucas–Penrose conclusion
holds; the premise doing the work is the mind's knowledge of its own machine's consistency; and that premise
causes trouble with or without mechanism. It would not show that minds are, or are not, machines.

## Known weaknesses

- **Arithmetic cannot say "me".** Stage 1 expresses "knows which machine it is" by a proxy (D7′). The first-person
  version needs a knowledge operator (Stage 2). In arithmetic a system can know its own code but not its own
  consistency; in epistemic arithmetic the knower is factive by axiom and cannot know its own code. Stage 1 sits
  on the first side of that trade-off.
- **Con(F) depends on the description of F.** D7 fixes one description (Foundation's Craig presentation of an
  r.e. axiom set). S1a quantifies over every r.e. axiomatization, but each is still read through that one
  construction.
- **Idealization.** A mind is modelled as a set of sentences; the results that mention deduction take it to be
  deductively closed. Whether any human is like that is outside the scope.
- **Stage 1 is mostly restatement.** The underlying theorems (Gödel I and II, Löb, reflection) are already proved
  in Foundation. What is new is the mind/machine reading, the source locators and the premise table.
- **The statement check is done by language models.** It can miss errors; the planted errors estimate how often.
- **Secondary quotation.** Penrose's conclusion is quoted via Koellner; *Shadows of the Mind* was not in hand, so
  S1e has no passage check.
- **Truth is truth in ℕ in Lean's logic** (S1b, S1c″, S1d), not a truth predicate inside a formal theory.

## Statement check outcome and accepted divergences

Run on 2026-11-22 with OpenAI `gpt-6.2-astra` and Google `gemini-4-neon`. Full detail: `statement-check/REPORT.md`
(final), `statement-check/round1/` (first draft) and `statement-check/superseded/` (items replaced after round 2).

**Planted errors.** Final round: both checkers returned `divergent` on all three. Round 1: OpenAI 3 of 3; Google 2
of 3. The one Google rated minor in round 1 was a badly chosen decoy: dropping the clause "¬σ ∉ K" from the
disjunction leaves a logically equivalent statement when K is sound, which Google pointed out. It was replaced.

**Changes made because of the check.**

- Round 1 found that S1a did not have the shape of the source's conditional ("if K knows F is sound then F ⊊ K").
  Added D8 and S1a″.
- Round 1 found the first alternative of the disjunction should be "no formal system has K as its theorem set",
  not "K is not r.e.". S1d now says that, and requires a Π₁ witness; the old form is kept as the variant S1d′.
- Round 1 found the "second machine" was stated only for PA, without the new machine's own limitation. S1b(iii)
  is now general and includes it.
- Round 1 found S1c″ concluded consistency where Chalmers says soundness, for one special addition. It is now two
  statements, both concluding soundness.
- Round 2 found (both checkers) that the first S1a″ assumed half its conclusion, the inclusion of F's theorems in
  K. It now derives both halves from K being consistent, deductively closed and able to do basic arithmetic (D10
  added). A second statement with knowledge of consistency as the premise was dropped: it was Gödel II restated.
- The claims and the phase B prompt were tightened after round 1 so that a missing proof, or parts of a passage
  covered by other items, are not counted as divergences.

**Final verdicts.** Of 17 real items with a passage, both checkers gave `faithful` or `faithful_with_caveats` on
15. The exceptions and the decisions:

| Item | Divergence | Decision |
|---|---|---|
| S1a′ `NoConsistentMindKnowsOwnMachineConsistent` | OpenAI: `divergent` against Gödel's remark via Wang. The passage excludes *knowing* which machine one is together with *knowing* it is sound; the Lean has actual equality and membership of a consistency sentence. Google: `faithful_with_caveats`. | Accepted and carried into `RESULTS.md`. This is the declared limit of plain arithmetic (Known weaknesses, first item). The faithful version is Koellner's Theorem 6, in Stage 2. |
| S1d′ `GodelDisjunctionRE` | OpenAI: `divergent`. The first alternative, "K is not r.e.", is not the passage's "no formal system has K as its theorem set". Google: `faithful_with_caveats`. | Accepted. S1d′ is a declared variant for sets that are not deductively closed; S1d is the form tied to the passage. |
| S1e `PenroseTuring` | No passage check: *Shadows of the Mind* §2.5 not in hand. | Carried into `RESULTS.md` as unchecked against its source until the book is available. |

**Caveats both checkers raise on most items** (all rated minor, all carried into `RESULTS.md`): membership in a
set K stands in for knowing; the language is fixed to first-order arithmetic; "formal system" is read as an r.e.
axiom set including 𝗜𝚺₁; the consistency statement is tied to one description of F (the Craig presentation);
statements are about every K of a given kind, not about a designated human K.
