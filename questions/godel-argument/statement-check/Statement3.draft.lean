import GodelArgument.Statement2

/-!
# The Gödel argument: statements added after reading Reinhardt (1985) (Amendment 3)

Statements only, like `Statement.lean` and `Statement2.lean`, and in the same abstract setting as `Statement2.lean`.

Two statements taken from Reinhardt's own text, which was not in hand when `Statement2.lean` was locked:

* his Theorem 6, the absolute version of the second incompleteness theorem, with his definition of the
  consistency statement and no condition on the system `F`;
* case (ii) of his Theorem 1.

Source locators are in `amendments.md` (Amendment 3), keyed by the names used here (D16, S2f, S2g).
-/

namespace GodelArgument

open FFL

section

variable {Fm S₀ S : Type} [LogicalConnective Fm] [LogicalNeutral Fm] [Entailment S₀ Fm] [Entailment S Fm]

/-- **D16. Knowledge is self-reflective** (axiom K4, the "KK law"): what is known is known to be known. -/
def KnowledgeSelfReflective (𝓑 : S₀) (K : Fm → Fm) : Prop := ∀ φ, 𝓑 ⊢ K φ 🡒 K (K φ)

end

/-- **S2f. Reinhardt's Theorem 6: an absolute version of the second incompleteness theorem.** Suppose it is
known, sentence by sentence, that whatever is known `F` holds of. Then it is known that the consistency of `F`
is not known. Nothing is assumed about `F` itself. `conF` is the consistency statement of `F`; all that is used
of it is that the base proves, for each sentence `σ`, that if `conF` holds then `F` does not hold of both `σ`
and `∼σ`. The base is closed under necessitation and proves K2 and K4; factivity enters only in its known
form. The sentence `s` is a fixed point: the base proves `s` equivalent to "it is known that `F` holds of
`∼s`". -/
def ReinhardtTheorem6 : Prop :=
  ∀ (Fm S₀ S : Type) [LogicalConnective Fm] [LogicalNeutral Fm] [Entailment S₀ Fm] [Entailment S Fm]
    (𝓑 : S₀) (𝓢 : S) [Entailment.Cl 𝓑] [Entailment.Cl 𝓢] (K F : Fm → Fm) (conF : Fm),
    ClosedUnderNecessitation 𝓑 K → KnowledgeClosedUnderMP 𝓑 K → KnowledgeSelfReflective 𝓑 K → 𝓑 ⪯ 𝓢 →
    KnowsOwnFactivity 𝓢 K →
    (∃ s, 𝓑 ⊢ s 🡘 K (F (∼s))) →
    (∀ σ, 𝓑 ⊢ conF 🡒 ∼(F σ ⋏ F (∼σ))) →
    (∀ σ, 𝓢 ⊢ K (K σ 🡒 F σ)) →
    𝓢 ⊢ K (∼K conF)

/-- **S2g. Reinhardt's Theorem 1, case (ii).** If it is known, sentence by sentence, that whatever `F` holds of
is known, then some sentence `ψ` is known and it is known that `F` does not hold of `ψ`. -/
def ReinhardtTheorem1Safe : Prop :=
  ∀ (Fm S₀ S : Type) [LogicalConnective Fm] [LogicalNeutral Fm] [Entailment S₀ Fm] [Entailment S Fm]
    (𝓑 : S₀) (𝓢 : S) [Entailment.Cl 𝓑] [Entailment.Cl 𝓢] (K F : Fm → Fm),
    ClosedUnderNecessitation 𝓑 K → 𝓑 ⪯ 𝓢 → KnowledgeClosedUnderMP 𝓢 K → KnowsOwnFactivity 𝓢 K →
    HasGödelSentence 𝓑 F →
    (∀ φ, 𝓢 ⊢ K (F φ 🡒 K φ)) →
    ∃ ψ, 𝓢 ⊢ K ψ ⋏ K (∼F ψ)

end GodelArgument
