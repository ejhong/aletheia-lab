import Foundation.FirstOrder.Incompleteness.Examples
import Foundation.FirstOrder.Incompleteness.Löb
import Foundation.FirstOrder.Incompleteness.Reflection.Local

/-!
# The Gödel argument: definitions and statements (Stage 0 and Stage 1)

This file holds *statements only*. Each claim is a `def … : Prop`; proofs live in other files and must have
exactly these types. The file is hashed by the protocol lock, so nothing here changes after locking.

Setting: sentences of first-order arithmetic (`ArithmeticSentence`), provability `T ⊢ σ` in classical first-order
logic from a set of axioms `T`, and truth in the standard natural numbers. All of this comes from the Foundation
library; the lab adds only the definitions and statements below.

Source locators are in `protocol.md`, keyed by the names used here (D1–D10, S1a–S1e).
-/

namespace GodelArgument

open FFL FFL.FirstOrder FFL.FirstOrder.Arithmetic FFL.FirstOrder.ProvabilityAbstraction

/-! ## Definitions -/

/-- **D1. Idealized mind.** The set `K` of arithmetic sentences the mind would ever accept as established. -/
abbrev Mind := Set ArithmeticSentence

/-- **D2. Truth.** `σ` is true in the standard natural numbers. -/
def IsTrue (σ : ArithmeticSentence) : Prop := ℕ↓[ℒₒᵣ] ⊧ σ

/-- **D3. Soundness.** Everything in `K` is true. -/
def Sound (K : Mind) : Prop := ∀ σ ∈ K, IsTrue σ

/-- **D4. Consistency.** No contradiction is derivable from `K`. -/
def Consistent (K : Mind) : Prop := Entailment.Consistent (K : ArithmeticTheory)

/-- **D5. Formal system, and its theorem set.** A formal system is a recursively enumerable set `F` of axioms
(`F.RE`). `K` is the theorem set of `F` when `K` is exactly the set of sentences provable from `F`. -/
def IsTheoremSetOf (K : Mind) (F : ArithmeticTheory) : Prop := K = F.theory

/-- **D6. "K is the theorem set of some machine."** Some recursively enumerable axiom set generates exactly `K`.
Nothing is said about whether `K` contains any statement about that machine. -/
def IsMechanical (K : Mind) : Prop := ∃ F : ArithmeticTheory, F.RE ∧ IsTheoremSetOf K F

/-- **D7. The consistency statement of a formal system.** For a recursively enumerable `F`, the arithmetic
sentence saying "no contradiction is provable from the axioms of `F`", built from one fixed description of `F`
(its Craig presentation). Different descriptions of the same axiom set give different sentences. -/
noncomputable def Con (F : ArithmeticTheory) [F.RE] : ArithmeticSentence := F.craig.consistent.val

/-- **D7′. "K knows which machine it is, and that the machine is consistent"**, as far as plain arithmetic can
say it: `K` is the theorem set of `F` and `K` contains the consistency statement of `F`. This is a proxy.
Arithmetic has no way to say "me"; the first-person version needs the knowledge operator of Stage 2. -/
def KnowsOwnMachineConsistent (K : Mind) (F : ArithmeticTheory) [F.RE] : Prop :=
  IsTheoremSetOf K F ∧ Con F ∈ K

/-- **D8. "K knows that F is sound"**, one sentence at a time: for every sentence `σ`, `K` contains the
arithmetic sentence "if `F` proves `σ` then `σ`". Arithmetic cannot say "everything `F` proves is true" in a single
sentence, so this is a schema, read through the same fixed description of `F` as D7. -/
def ContainsSoundnessOf (K : Mind) (F : ArithmeticTheory) [F.RE] : Prop :=
  F.craig.localReflectionOn Set.univ ⊆ K

/-- **D9. Π₁ sentence.** `σ` has the logical form "for all numbers, a checkable condition holds". Statements
that a computation never halts, or that a Diophantine equation has no solution, are of this form. -/
def IsPi1 (σ : ArithmeticSentence) : Prop := ℬ[<, ℒₒᵣ].Hierarchy 𝚷 1 σ

/-- **D10. Deductively closed.** Whatever follows from `K` by classical first-order logic is already in `K`. -/
def DeductivelyClosed (K : Mind) : Prop := Theory.theory (K : ArithmeticTheory) ⊆ K

/-! ## Stage 1 statements -/

/-- **S1a. Penrose's conclusion as a conditional.** If a consistent mind `K` is the theorem set of a formal
system `F` that includes basic arithmetic (`𝗜𝚺₁`), then `K` does not contain the consistency statement of `F`.
This holds for every recursively enumerable axiomatization `F` of `K`. -/
def PenroseConditional : Prop :=
  ∀ (K : Mind) (F : ArithmeticTheory) [F.RE] [𝗜𝚺₁ ⪯ F],
    IsTheoremSetOf K F → Consistent K → Con F ∉ K

/-- **S1a′. The same, as a refutation.** No consistent mind satisfies D7′ for a system including basic
arithmetic. -/
def NoConsistentMindKnowsOwnMachineConsistent : Prop :=
  ∀ (K : Mind) (F : ArithmeticTheory) [F.RE] [𝗜𝚺₁ ⪯ F],
    Consistent K → ¬ KnowsOwnMachineConsistent K F

/-- **S1a″. A mind that knows a machine is sound strictly exceeds it.** Let the mind `K` be consistent,
deductively closed, and able to do basic arithmetic. Let `F` be a formal system including basic arithmetic. If
`K` contains, for every sentence `σ`, "if `F` proves `σ` then `σ`" (D8), then `K` contains every theorem of `F`
and something more: `F`'s theorems are a strict subset of `K`. In particular `K` is not the theorem set of `F`. -/
def KnownSoundMachineIsExceeded : Prop :=
  ∀ (K : Mind) (F : ArithmeticTheory) [F.RE] [𝗜𝚺₁ ⪯ F] [𝗜𝚺₁ ⪯ (K : ArithmeticTheory)],
    DeductivelyClosed K → Consistent K → ContainsSoundnessOf K F → F.theory ⊂ K

/-- **S1b(i). The standard objection, as a witness.** The theorems of Peano arithmetic form a mind that is
mechanical, sound and consistent, whose machine's consistency statement is true, and which does not contain
that statement. So "is a sound, consistent machine" does not lead to contradiction; only the added premise of
D7′ does. -/
def StandardObjectionWitness : Prop :=
  IsMechanical 𝗣𝗔.theory ∧ Sound 𝗣𝗔.theory ∧ Consistent 𝗣𝗔.theory ∧
    IsTrue (Con 𝗣𝗔) ∧ Con 𝗣𝗔 ∉ 𝗣𝗔.theory

/-- **S1b(ii). The machine proves the conditional itself.** Every formal system `F` including basic arithmetic
proves "if `F` is consistent then `G`", where `G` is the Gödel sentence of `F`. So what a mind would need, to
see `G` where `F` cannot, is exactly the consistency of `F`. -/
def MachineProvesConditional : Prop :=
  ∀ (F : ArithmeticTheory) [F.Δ₁] [𝗜𝚺₁ ⪯ F],
    F ⊢ (F.consistent.val 🡒 gödel F.standardProvability)

/-- **S1b(iii). The second machine.** Take any sound formal system `F` including basic arithmetic, and add its
consistency statement as a new axiom. The result is again a formal system (recursively enumerable) and again
sound; it proves the consistency statement of `F`, which `F` could not; and it has a consistency statement of
its own that it cannot prove. -/
def SecondMachine : Prop :=
  ∀ (F : ArithmeticTheory) [F.RE] [𝗜𝚺₁ ⪯ F], Sound F →
    ∃ _ : Theory.RE (F ∪ {Con F}),
      Sound (F ∪ {Con F}).theory ∧ Con F ∈ (F ∪ {Con F}).theory ∧ Con F ∉ F.theory ∧
        Con (F ∪ {Con F}) ∉ (F ∪ {Con F}).theory

/-- **S1c. Chalmers's point.** Take any theory `T` with a belief predicate `𝔅` in its own language satisfying
Chalmers's assumptions (1)–(3) (the derivability conditions D1–D3) and able to form self-referential sentences
(diagonalization over a base theory `T₀ ⪯ T`). If `T` asserts its own consistency, `¬𝔅(⊥)`, then `T` is
inconsistent. `𝔅` is any formula; nothing assumes `T` is a machine. -/
def ChalmersPoint : Prop :=
  ∀ (L : Language.{0}) [L.DecidableEq] [L.ReferenceableBy L] (T₀ T : Theory L)
    [Diagonalization T₀] [T₀ ⪯ T] (𝔅 : Provability T₀ T) [𝔅.HBL],
    T ⊢ 𝔅.con → Entailment.Inconsistent T

/-- **S1c′. The same for soundness (Löb's theorem).** If such a `T` proves "if I believe `σ` then `σ`" for every
sentence `σ`, then `T` is inconsistent. -/
def SelfSoundnessInconsistent : Prop :=
  ∀ (L : Language.{0}) [L.DecidableEq] [L.ReferenceableBy L] (T₀ T : Theory L)
    [Diagonalization T₀] [T₀ ⪯ T] (𝔅 : Provability T₀ T) [𝔅.HBL],
    (∀ σ : Sentence L, T ⊢ (𝔅 σ 🡒 σ)) → Entailment.Inconsistent T

/-- **S1c″. Adding a true statement to a sound system gives a sound system.** If every axiom of `T` is true and
`σ` is true, then everything provable from `T` together with `σ` is true. -/
def SoundPlusTrueIsSound : Prop :=
  ∀ (T : ArithmeticTheory) (σ : ArithmeticSentence), Sound T → IsTrue σ → Sound (T ∪ {σ}).theory

/-- **S1c‴. Asserting the soundness of a system other than yourself is harmless.** If every axiom of `T` is true,
then `T` together with "if `T` proves `σ` then `σ`", for every sentence `σ`, proves only truths. The trouble in
S1c and S1c′ arises only when a system asserts this of itself. -/
def SoundPlusItsSoundnessIsSound : Prop :=
  ∀ (T : ArithmeticTheory) [T.Δ₁], Sound T → Sound (T ∪ T.localReflectionOn Set.univ).theory

/-- **S1d. Gödel's disjunction, semantic form.** For any set `K` of true arithmetic sentences: either no formal
system has exactly `K` as its theorem set, or there is a true Π₁ sentence that `K` leaves undecided (neither it
nor its negation is in `K`). "True" is truth in the standard natural numbers, judged in Lean's own logic, not by
a truth predicate inside a formal theory. -/
def GodelDisjunction : Prop :=
  ∀ K : Mind, Sound K →
    (¬ IsMechanical K) ∨ ∃ σ : ArithmeticSentence, IsPi1 σ ∧ IsTrue σ ∧ σ ∉ K ∧ (∼σ) ∉ K

/-- **S1d′. The same for sets that need not be deductively closed.** For any set `K` of true arithmetic
sentences: either `K` is not recursively enumerable, or some true sentence is undecided by `K`. -/
def GodelDisjunctionRE : Prop :=
  ∀ K : Mind, Sound K →
    (¬ Theory.RE (K : ArithmeticTheory)) ∨ ∃ σ : ArithmeticSentence, IsTrue σ ∧ σ ∉ K ∧ (∼σ) ∉ K

/-- **S1e. Penrose's argument in halting form.** Number the computations `C₀, C₁, …` (partial recursive
functions, by code). Let `A` be a recursively enumerable set of numbers that is a sound certificate of
non-halting on the diagonal: whenever `n ∈ A`, the computation `Cₙ` does not halt on input `n`. Then there is a
`k` such that `C_k` does not halt on input `k`, yet `k ∉ A`. -/
def PenroseTuring : Prop :=
  ∀ A : ℕ → Prop, REPred A →
    (∀ n, A n → ¬ ((Denumerable.ofNat Nat.Partrec.Code n).eval n).Dom) →
    ∃ k, ¬ ((Denumerable.ofNat Nat.Partrec.Code k).eval k).Dom ∧ ¬ A k

end GodelArgument
