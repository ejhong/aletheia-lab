import GodelArgument.Results6

/-!
# Tier 2D: the hypotheses can hold together

For the abstract statements of tier 2D (S5c to S5f), a consistent system in which every hypothesis holds. The
witnesses are deliberately trivial, over Peano arithmetic. They show that the hypotheses do not clash, and
nothing more. S5a, S5b and S5g have no hypotheses: they exhibit systems.
-/

namespace GodelArgument

open FFL FFL.FirstOrder FFL.FirstOrder.Arithmetic

/-- S5c: every hypothesis holds in a consistent system. `K φ` is read as `φ`, and `F` holds of nothing. -/
theorem corollaryWhereSound_nonvacuous :
    ∃ (𝓢 : ArithmeticTheory) (K F : ArithmeticSentence → ArithmeticSentence) (conF φ : ArithmeticSentence),
      KnowledgeClosedUnderMP 𝓢 K ∧ 𝓢 ⊢ K (conF 🡒 F φ 🡒 φ) ∧ 𝓢 ⊢ F φ 🡒 K (F φ) ∧ Entailment.Consistent 𝓢 := by
  refine ⟨𝗣𝗔, id, fun _ => ⊥, ⊤, ⊤, fun φ ψ => by simp only [id]; cl_prover, by simp only [id]; cl_prover,
    by simp only [id]; cl_prover, inferInstance⟩

/-- S5d: every hypothesis holds in a consistent system. Nothing is known and `F` holds of nothing. -/
theorem mindInsideMachine_nonvacuous :
    ∃ (𝓢 : ArithmeticTheory) (K F : ArithmeticSentence → ArithmeticSentence) (conF : ArithmeticSentence),
      𝓢 ⊢ K conF 🡒 conF ∧ 𝓢 ⊢ K (∼conF) 🡒 ∼conF ∧ 𝓢 ⊢ K conF 🡒 F conF ∧ 𝓢 ⊢ conF 🡒 ∼F conF ∧
      Entailment.Consistent 𝓢 := by
  refine ⟨𝗣𝗔, fun _ => ⊥, fun _ => ⊥, ⊤, by cl_prover, by cl_prover, by cl_prover, by cl_prover,
    inferInstance⟩

/-- S5e: every hypothesis holds in a consistent system. `K φ` is read as `φ`, `F` holds of nothing, and
`τ` and `σ` are falsehood. -/
theorem unrestrictedThesis_nonvacuous :
    ∃ (𝓢 : ArithmeticTheory) (K F : ArithmeticSentence → ArithmeticSentence) (τ σ G : ArithmeticSentence),
      𝓢 ⊢ K (σ 🡒 G) ⋏ (σ 🡒 ∼F (σ 🡒 G)) ∧ 𝓢 ⊢ τ 🡒 σ ∧ 𝓢 ⊢ τ 🡒 (K (σ 🡒 G) 🡘 F (σ 🡒 G)) ∧
      Entailment.Consistent 𝓢 := by
  refine ⟨𝗣𝗔, id, fun _ => ⊥, ⊥, ⊥, ⊤, by simp only [id]; cl_prover, by cl_prover,
    by simp only [id]; cl_prover, inferInstance⟩

/-- S5f: every hypothesis holds in a consistent system. Everything is determinate. -/
theorem conditionalDeterminate_nonvacuous :
    ∃ (𝓢 : ArithmeticTheory) (T D : ArithmeticSentence → ArithmeticSentence) (σ G : ArithmeticSentence),
      DeterminateImp 𝓢 D T ∧ 𝓢 ⊢ D σ ∧ 𝓢 ⊢ D G ∧ Entailment.Consistent 𝓢 := by
  refine ⟨𝗣𝗔, id, fun _ => ⊤, ⊤, ⊤, fun φ ψ => by cl_prover, by cl_prover, by cl_prover, inferInstance⟩

#assert_standard_axioms corollaryWhereSound_nonvacuous mindInsideMachine_nonvacuous
#assert_standard_axioms unrestrictedThesis_nonvacuous conditionalDeterminate_nonvacuous

end GodelArgument
