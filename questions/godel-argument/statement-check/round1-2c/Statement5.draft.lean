import GodelArgument.Statement2

/-!
# The Gödel argument: Penrose's new argument (Amendment 5, tier 2C)

Statements only, in the abstract setting of `Statement2.lean`: sentences are any type with classical connectives,
and `𝓢` is a proof system closed under classical propositional reasoning. Here there are three operations on
sentences: `T φ` ("`φ` is true"), `K φ` ("`φ` is known") and `D φ` ("`φ` is determinate", that is, true or
false). In the sources these are predicates applied to the code of `φ`; truth and knowledge are type-free, so
`T` and `K` may be applied to sentences that contain `T` and `K`.

Nothing about arithmetic or coding is built in. Each fact the sources take from arithmetic, and each principle
about `T`, `K` and `D`, is an explicit hypothesis of the statement that uses it.

The sentences of Penrose's argument, as Koellner sets it out, are abstract parameters:

* `σ`: "K = F_e", I am the machine `F_e`;
* `S`: "F_e ⊆ T", `F_e` is sound; `S'`: "F_e⁺ ⊆ T", where `F_e⁺` is `F_e` with the sentence `σ` added;
* `G`: the Gödel sentence of `F_e⁺`; `P`: "F_e⁺ proves G"; `Q`: "F_e proves σ → G".

Source locators are in `amendments.md` (Amendment 5), keyed by the names used here (D20–D27, S4a–S4g).
-/

namespace GodelArgument

open FFL

section

variable {Fm S : Type} [LogicalConnective Fm] [LogicalNeutral Fm] [Entailment S Fm]

/-! ## Definitions -/

/-- **D20. T-In**, unrestricted: whatever is so is true. -/
def TIn (𝓢 : S) (T : Fm → Fm) : Prop := ∀ φ, 𝓢 ⊢ φ 🡒 T φ

/-- **D21. T-Out**: whatever is true is so. -/
def TOut (𝓢 : S) (T : Fm → Fm) : Prop := ∀ φ, 𝓢 ⊢ T φ 🡒 φ

/-- **D22. K-Intro**, unrestricted, a rule: whatever is proved is known. -/
def KIntro (𝓢 : S) (K : Fm → Fm) : Prop := ∀ φ, 𝓢 ⊢ φ → 𝓢 ⊢ K φ

/-- **D23. K → T**: whatever is known is true. -/
def KnownIsTrue (𝓢 : S) (K T : Fm → Fm) : Prop := ∀ φ, 𝓢 ⊢ K φ 🡒 T φ

/-- **D24. DK-Intro**, a rule: whatever is proved, and proved determinate, is known. -/
def DKIntro (𝓢 : S) (D K : Fm → Fm) : Prop := ∀ φ, 𝓢 ⊢ φ → 𝓢 ⊢ D φ → 𝓢 ⊢ K φ

/-- **D25. The truth biconditional for determinate sentences**: if `φ` is determinate, then `φ` is true exactly
when it is so. -/
def DeterminateTruth (𝓢 : S) (D T : Fm → Fm) : Prop := ∀ φ, 𝓢 ⊢ D φ 🡒 (T φ 🡘 φ)

/-- **D26. Determinateness of a conditional** (axiom D4): `φ → ψ` is determinate exactly when `φ` is
determinate and, if `φ` is true, `ψ` is determinate. -/
def DeterminateImp (𝓢 : S) (D T : Fm → Fm) : Prop := ∀ φ ψ, 𝓢 ⊢ D (φ 🡒 ψ) 🡘 (D φ ⋏ (T φ 🡒 D ψ))

/-- **D27. Determinateness of a knowledge statement** (axiom D7): "`φ` is known" is determinate exactly when
`φ` is. -/
def DeterminateK (𝓢 : S) (D K : Fm → Fm) : Prop := ∀ φ, 𝓢 ⊢ D (K φ) 🡘 D φ

end

/-! ## Statements -/

/-- **S4a. Penrose's new argument is valid from its rules.** Given T-In at `σ`, the rule K-Intro, and six
bridging facts (lines (1), (3), (4), (6) of the argument and the two facts used in passing from (1) to (2) and
from (5), (6) to (7)), the system proves that `σ` fails: I am not the machine `F_e`. -/
def PenroseArgumentValid : Prop :=
  ∀ (Fm S : Type) [LogicalConnective Fm] [LogicalNeutral Fm] [Entailment S Fm] (𝓢 : S) [Entailment.Cl 𝓢]
    (T K : Fm → Fm) (σ S₀ S' G P Q : Fm),
    𝓢 ⊢ σ 🡒 T σ → KIntro 𝓢 K →
    𝓢 ⊢ σ 🡒 S₀ →
    𝓢 ⊢ S₀ 🡒 T σ 🡒 S' →
    𝓢 ⊢ S' 🡒 G →
    𝓢 ⊢ S' 🡒 ∼P →
    𝓢 ⊢ Q 🡒 P →
    𝓢 ⊢ σ 🡒 K (σ 🡒 G) 🡒 Q →
    𝓢 ⊢ ∼σ

/-- **S4b. Unrestricted T-In is inconsistent with T-Out.** If whatever is so is true, whatever is true is so,
and there is a liar sentence, the system proves a contradiction. -/
def UnrestrictedTInInconsistent : Prop :=
  ∀ (Fm S : Type) [LogicalConnective Fm] [LogicalNeutral Fm] [Entailment S Fm] (𝓢 : S) [Entailment.Cl 𝓢]
    (T : Fm → Fm),
    TIn 𝓢 T → TOut 𝓢 T → (∃ lam, 𝓢 ⊢ lam 🡘 ∼T lam) → 𝓢 ⊢ ⊥

/-- **S4c. Unrestricted K-Intro is inconsistent with K → T and T-Out.** If whatever is proved is known, whatever
is known is true, whatever is true is so, and there is a sentence that says of itself that it is not known, the
system proves a contradiction. -/
def UnrestrictedKIntroInconsistent : Prop :=
  ∀ (Fm S : Type) [LogicalConnective Fm] [LogicalNeutral Fm] [Entailment S Fm] (𝓢 : S) [Entailment.Cl 𝓢]
    (T K : Fm → Fm),
    KIntro 𝓢 K → KnownIsTrue 𝓢 K T → TOut 𝓢 T → (∃ kap, 𝓢 ⊢ kap 🡘 ∼K kap) → 𝓢 ⊢ ⊥

/-- **S4d. Knowing every logical validity is inconsistent with type-free truth.** Let `lam` be a liar sentence.
If the validity "`lam` or not `lam`" is known, what is known is true, truth distributes over that disjunction,
and a sentence that is true or false obeys the truth biconditional, the system proves a contradiction. -/
def KnownValiditiesInconsistent : Prop :=
  ∀ (Fm S : Type) [LogicalConnective Fm] [LogicalNeutral Fm] [Entailment S Fm] (𝓢 : S) [Entailment.Cl 𝓢]
    (T K : Fm → Fm) (lam : Fm),
    𝓢 ⊢ lam 🡘 ∼T lam →
    𝓢 ⊢ K (lam ⋎ ∼lam) →
    𝓢 ⊢ K (lam ⋎ ∼lam) 🡒 T (lam ⋎ ∼lam) →
    𝓢 ⊢ T (lam ⋎ ∼lam) 🡒 (T lam ⋎ T (∼lam)) →
    𝓢 ⊢ (T lam ⋎ T (∼lam)) 🡒 (T lam 🡘 lam) →
    𝓢 ⊢ ⊥

/-- **S4e. With the rules restricted to determinate sentences, the argument goes through if `σ` is
determinate.** Replace T-In by the truth biconditional for determinate sentences and K-Intro by DK-Intro. If
the system proves that `σ` and `σ → G` are determinate, then from the same six bridging facts it proves that
`σ` fails. -/
def PenroseArgumentUnderDeterminateness : Prop :=
  ∀ (Fm S : Type) [LogicalConnective Fm] [LogicalNeutral Fm] [Entailment S Fm] (𝓢 : S) [Entailment.Cl 𝓢]
    (T K D : Fm → Fm) (σ S₀ S' G P Q : Fm),
    DeterminateTruth 𝓢 D T → DKIntro 𝓢 D K →
    𝓢 ⊢ D σ → 𝓢 ⊢ D (σ 🡒 G) →
    𝓢 ⊢ σ 🡒 S₀ →
    𝓢 ⊢ S₀ 🡒 T σ 🡒 S' →
    𝓢 ⊢ S' 🡒 G →
    𝓢 ⊢ S' 🡒 ∼P →
    𝓢 ⊢ Q 🡒 P →
    𝓢 ⊢ σ 🡒 K (σ 🡒 G) 🡒 Q →
    𝓢 ⊢ ∼σ

/-- **S4f. If `σ` is indeterminate, so are the two statements at which the rules are applied.** From the
determinateness axioms for conditionals and for knowledge statements: if the system proves that `σ` is not
determinate, it proves that `σ → X` is not determinate, for any `X`, and that "`σ → G` is known" is not
determinate. -/
def StepsIndeterminateIfThesisIs : Prop :=
  ∀ (Fm S : Type) [LogicalConnective Fm] [LogicalNeutral Fm] [Entailment S Fm] (𝓢 : S) [Entailment.Cl 𝓢]
    (T K D : Fm → Fm) (σ X G : Fm),
    DeterminateImp 𝓢 D T → DeterminateK 𝓢 D K →
    𝓢 ⊢ ∼D σ →
    𝓢 ⊢ ∼D (σ 🡒 X) ⋏ ∼D (K (σ 🡒 G))

/-- **S4g. What the argument yields for a determinate thesis that does not cover its own conditional.** Keep
everything in S4e except the last bridging fact, which says that `σ` makes knowledge and `F_e` agree on the
sentence `σ → G`. Then the system proves that `σ → G` is known, and that if `σ` holds then `F_e` does not
prove `σ → G`. -/
def RestrictedThesisGivesUnprovableKnowledge : Prop :=
  ∀ (Fm S : Type) [LogicalConnective Fm] [LogicalNeutral Fm] [Entailment S Fm] (𝓢 : S) [Entailment.Cl 𝓢]
    (T K D : Fm → Fm) (σ S₀ S' G P Q : Fm),
    DeterminateTruth 𝓢 D T → DKIntro 𝓢 D K →
    𝓢 ⊢ D σ → 𝓢 ⊢ D (σ 🡒 G) →
    𝓢 ⊢ σ 🡒 S₀ →
    𝓢 ⊢ S₀ 🡒 T σ 🡒 S' →
    𝓢 ⊢ S' 🡒 G →
    𝓢 ⊢ S' 🡒 ∼P →
    𝓢 ⊢ Q 🡒 P →
    𝓢 ⊢ K (σ 🡒 G) ⋏ (σ 🡒 ∼Q)

end GodelArgument
