import GodelArgument.Statement5
import GodelArgument.Results2

/-!
# Results for Penrose's new argument (Amendment 5, tier 2C)

Each theorem has exactly the type of a statement in `Statement5.lean`. All seven are derivations in classical
propositional logic from the stated hypotheses, with one or two applications of a rule (K-Intro or DK-Intro).
-/

namespace GodelArgument

open FFL

/-- S4a. Koellner's steps. From (1), T-In at `σ` and the first bridge: (2) `σ → S'`. Then (3) `σ → G`. K-Intro
gives (5) `K(σ → G)`. From (2), (4) and the deduction bridge: (6) `σ → ¬Q`. The last bridge with (5) gives
`σ → Q`. So `¬σ`. -/
theorem penroseArgumentValid : PenroseArgumentValid := by
  intro Fm S _ _ _ 𝓢 _ T K σ S₀ S' G P Q hTin hK b1 b2 b3 b4 b6 b7
  have l3 : 𝓢 ⊢ σ 🡒 G := by cl_prover [hTin, b1, b2, b3]
  have l5 : 𝓢 ⊢ K (σ 🡒 G) := hK _ l3
  cl_prover [hTin, b1, b2, b4, b6, b7, l5]

/-- S4b. The liar: if `lam` then `T lam` (T-In), so not `lam`. Hence `T lam`, and by T-Out `lam`. -/
theorem unrestrictedTInInconsistent : UnrestrictedTInInconsistent := by
  intro Fm S _ _ _ 𝓢 _ T hin hout ⟨lam, hl⟩
  cl_prover [hin lam, hout lam, hl]

/-- S4c. The knower: if `K kap` then `kap` (K → T, T-Out), so not `K kap`. Hence `kap` is proved, and K-Intro
gives `K kap`. -/
theorem unrestrictedKIntroInconsistent : UnrestrictedKIntroInconsistent := by
  intro Fm S _ _ _ 𝓢 _ T K hK hkt hout ⟨kap, hk⟩
  have h1 : 𝓢 ⊢ kap := by cl_prover [hkt kap, hout kap, hk]
  have h2 : 𝓢 ⊢ K kap := hK _ h1
  cl_prover [h1, h2, hk]

/-- S4d. Koellner's quicker proof: the known validity is true, so `lam` is true or false, so `lam` obeys the
truth biconditional, which a liar cannot. -/
theorem knownValiditiesInconsistent : KnownValiditiesInconsistent := by
  intro Fm S _ _ _ 𝓢 _ T K lam hl h1 h2 h3 h4
  cl_prover [hl, h1, h2, h3, h4]

/-- S4e. By D4 the determinateness of `σ → S'` gives that of `σ`; by D7 the determinateness of "`σ → G` is
known" gives that of `σ → G`. Then as S4a, with `σ → T σ` from the truth biconditional and step (5) by
DK-Intro. -/
theorem penroseArgumentUnderDeterminateness : PenroseArgumentUnderDeterminateness := by
  intro Fm S _ _ _ 𝓢 _ T K D σ S₀ S' G P Q hdt hdk hdi hdK d2 d5 b1 b2 b3 b4 b6 b7
  have dσ : 𝓢 ⊢ D σ := by cl_prover [hdi σ S', d2]
  have dσG : 𝓢 ⊢ D (σ 🡒 G) := by cl_prover [hdK (σ 🡒 G), d5]
  have hTin : 𝓢 ⊢ σ 🡒 T σ := by cl_prover [hdt σ, dσ]
  have l3 : 𝓢 ⊢ σ 🡒 G := by cl_prover [hTin, b1, b2, b3]
  have l5 : 𝓢 ⊢ K (σ 🡒 G) := hdk _ l3 dσG
  cl_prover [hTin, b1, b2, b4, b6, b7, l5]

/-- S4f. By D4 a conditional with an indeterminate antecedent is indeterminate; by D7 so is the statement that
it is known. -/
theorem stepsIndeterminateIfThesisIs : StepsIndeterminateIfThesisIs := by
  intro Fm S _ _ _ 𝓢 _ T K D σ X G hdi hdk hn
  cl_prover [hdi σ X, hdi σ G, hdk (σ 🡒 G), hn]

/-- S4g. Steps (1) to (6), which do not use the last bridge. -/
theorem restrictedThesisGivesUnprovableKnowledge : RestrictedThesisGivesUnprovableKnowledge := by
  intro Fm S _ _ _ 𝓢 _ T K D σ S₀ S' G P Q hdt hdk dσ dσG b1 b2 b3 b4 b6
  have hTin : 𝓢 ⊢ σ 🡒 T σ := by cl_prover [hdt σ, dσ]
  have l3 : 𝓢 ⊢ σ 🡒 G := by cl_prover [hTin, b1, b2, b3]
  have l5 : 𝓢 ⊢ K (σ 🡒 G) := hdk _ l3 dσG
  cl_prover [hTin, b1, b2, b4, b6, l5]

#assert_standard_axioms penroseArgumentValid unrestrictedTInInconsistent unrestrictedKIntroInconsistent
#assert_standard_axioms knownValiditiesInconsistent penroseArgumentUnderDeterminateness
#assert_standard_axioms stepsIndeterminateIfThesisIs restrictedThesisGivesUnprovableKnowledge

end GodelArgument
