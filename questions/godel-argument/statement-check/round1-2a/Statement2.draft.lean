import Foundation.Propositional.Entailment.Cl

/-!
# The Gödel argument: definitions and statements for Stage 2A (a knowledge operator)

This file holds *statements only*, like `Statement.lean`. It is hashed by the protocol lock once checked.

Setting. Stage 1 had no way to say "I know". Here a knowledge operator `K` is added, abstractly:

* `Fm` is any type of sentences with the classical connectives;
* `𝓑` (the base) and `𝓢` are two proof systems over `Fm`, both closed under classical propositional reasoning
  (`Entailment.Cl`). Think of `𝓑` as epistemic arithmetic EA and of `𝓢` as a system that includes it;
* `K : Fm → Fm` sends a sentence `φ` to the sentence "it is known that `φ`". It is an operator on sentences,
  not a predicate of code numbers;
* `F : Fm → Fm` sends `φ` to a sentence read as "`F` holds of `φ`", for example "the formal system `F` proves `φ`".
  In the sources this is `F(⌜φ⌝)` for a formula `F(x)`; here nothing is assumed about `F` unless stated.

Nothing about arithmetic, coding or quantifiers is built in. Every fact the sources obtain from arithmetic
(a Gödel sentence, the formalized second incompleteness theorem) and every principle about `K` appears as an
explicit hypothesis of the statement that uses it.

Source locators are in `amendments.md` (Amendment 2), keyed by the names used here (D11–D15, S2a–S2d).
-/

namespace GodelArgument

open FFL

section

variable {Fm S₀ S : Type} [LogicalConnective Fm] [LogicalNeutral Fm] [Entailment S₀ Fm] [Entailment S Fm]

/-! ## Definitions -/

/-- **D11. The base is known.** Whatever the base system `𝓑` proves, `𝓢` proves to be known. -/
def KnowsTheoremsOf (𝓑 : S₀) (𝓢 : S) (K : Fm → Fm) : Prop := ∀ φ, 𝓑 ⊢ φ → 𝓢 ⊢ K φ

/-- **D12. Knowledge is closed under modus ponens** (axiom K2). -/
def KnowledgeClosedUnderMP (𝓢 : S) (K : Fm → Fm) : Prop := ∀ φ ψ, 𝓢 ⊢ K (φ 🡒 ψ) 🡒 K φ 🡒 K ψ

/-- **D13. Knowledge is factive** (axiom K3): what is known is so. -/
def Factive (𝓢 : S) (K : Fm → Fm) : Prop := ∀ φ, 𝓢 ⊢ K φ 🡒 φ

/-- **D14. The knower knows that its knowledge is factive**: `K` applied to each instance of K3. -/
def KnowsOwnFactivity (𝓢 : S) (K : Fm → Fm) : Prop := ∀ φ, 𝓢 ⊢ K (K φ 🡒 φ)

/-- **D15. `F` has a Gödel sentence over the base**: some `ψ` that the base proves equivalent to "`F` does not
hold of `ψ`". -/
def HasGödelSentence (𝓑 : S₀) (F : Fm → Fm) : Prop := ∃ ψ, 𝓑 ⊢ ψ 🡘 ∼F ψ

end

/-! ## Statements -/

/-- **S2a. Reinhardt's Theorem 3.** If it is known, sentence by sentence, that whatever `F` holds of is so, then
some sentence `ψ` is known and it is known that `F` does not hold of `ψ`. -/
def ReinhardtTheorem3 : Prop :=
  ∀ (Fm S₀ S : Type) [LogicalConnective Fm] [LogicalNeutral Fm] [Entailment S₀ Fm] [Entailment S Fm]
    (𝓑 : S₀) (𝓢 : S) [Entailment.Cl 𝓑] [Entailment.Cl 𝓢] (K F : Fm → Fm),
    KnowsTheoremsOf 𝓑 𝓢 K → KnowledgeClosedUnderMP 𝓢 K →
    HasGödelSentence 𝓑 F →
    (∀ φ, 𝓢 ⊢ K (F φ 🡒 φ)) →
    ∃ ψ, 𝓢 ⊢ K ψ ⋏ K (∼F ψ)

/-- **S2a′. The knower exceeds a system it knows to be sound.** With factivity added: some sentence is known
that `F` does not hold of. -/
def KnowerExceedsKnownSoundSystem : Prop :=
  ∀ (Fm S₀ S : Type) [LogicalConnective Fm] [LogicalNeutral Fm] [Entailment S₀ Fm] [Entailment S Fm]
    (𝓑 : S₀) (𝓢 : S) [Entailment.Cl 𝓑] [Entailment.Cl 𝓢] (K F : Fm → Fm),
    KnowsTheoremsOf 𝓑 𝓢 K → KnowledgeClosedUnderMP 𝓢 K → Factive 𝓢 K →
    HasGödelSentence 𝓑 F →
    (∀ φ, 𝓢 ⊢ K (F φ 🡒 φ)) →
    ∃ ψ, 𝓢 ⊢ K ψ ⋏ ∼F ψ

/-- **S2b. An absolute version of the second incompleteness theorem** (Reinhardt's Theorem 4, with a proviso
made explicit). Suppose it is known, sentence by sentence, that whatever is known `F` holds of, and the base
proves the formalized second incompleteness theorem for `F` ("if `F` holds of its own consistency statement
then `F` holds of falsehood"). Then it is known that the consistency of `F` is not known. The consistency
statement of `F` is `∼F ⊥`. -/
def AbsoluteSecondIncompleteness : Prop :=
  ∀ (Fm S₀ S : Type) [LogicalConnective Fm] [LogicalNeutral Fm] [Entailment S₀ Fm] [Entailment S Fm]
    (𝓑 : S₀) (𝓢 : S) [Entailment.Cl 𝓑] [Entailment.Cl 𝓢] (K F : Fm → Fm),
    KnowsTheoremsOf 𝓑 𝓢 K → KnowledgeClosedUnderMP 𝓢 K → KnowsOwnFactivity 𝓢 K →
    𝓑 ⊢ F (∼F ⊥) 🡒 F ⊥ →
    (∀ φ, 𝓢 ⊢ K (K φ 🡒 F φ)) →
    𝓢 ⊢ K (∼K (∼F ⊥))

/-- **S2c. Knowing which system you are is contradictory.** If it is known, sentence by sentence, that being
known coincides with `F` holding, then `𝓢` proves a contradiction. Nothing assumes `F` is a machine: only that
`F` has a Gödel sentence. -/
def KnowingWhichSystemIsContradictory : Prop :=
  ∀ (Fm S₀ S : Type) [LogicalConnective Fm] [LogicalNeutral Fm] [Entailment S₀ Fm] [Entailment S Fm]
    (𝓑 : S₀) (𝓢 : S) [Entailment.Cl 𝓑] [Entailment.Cl 𝓢] (K F : Fm → Fm),
    KnowsTheoremsOf 𝓑 𝓢 K → KnowledgeClosedUnderMP 𝓢 K → Factive 𝓢 K → KnowsOwnFactivity 𝓢 K →
    HasGödelSentence 𝓑 F →
    (∀ φ, 𝓢 ⊢ K (K φ 🡘 F φ)) →
    𝓢 ⊢ ⊥

/-- **S2d. The diagonal core.** For no sentence `p` can it be known that `p` holds exactly when `∼p` is known.
No Gödel sentence and no arithmetic are assumed. -/
def NoKnownSelfDiagonal : Prop :=
  ∀ (Fm S₀ S : Type) [LogicalConnective Fm] [LogicalNeutral Fm] [Entailment S₀ Fm] [Entailment S Fm]
    (𝓑 : S₀) (𝓢 : S) [Entailment.Cl 𝓑] [Entailment.Cl 𝓢] (K : Fm → Fm),
    KnowsTheoremsOf 𝓑 𝓢 K → KnowledgeClosedUnderMP 𝓢 K → Factive 𝓢 K → KnowsOwnFactivity 𝓢 K →
    ∀ p : Fm, 𝓢 ⊢ ∼K (K (∼p) 🡘 p)

end GodelArgument
