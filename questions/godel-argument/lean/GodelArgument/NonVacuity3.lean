import GodelArgument.Results3
import GodelArgument.NonVacuity2

/-!
# Statements from Reinhardt (1985): the hypotheses can hold together

One consistent system in which every hypothesis of S2f holds, and one for S2g. Both use the trivial knower,
`K φ := φ`, over Peano arithmetic, and for S2f the degenerate `F` that holds of every sentence. They show that
the hypotheses do not clash, and nothing more.
-/

namespace GodelArgument

open FFL FFL.FirstOrder FFL.FirstOrder.Arithmetic FFL.FirstOrder.ProvabilityAbstraction

/-- S2f: every hypothesis holds in a consistent system. `F` holds of everything, so its consistency statement
is falsehood, and the fixed point is truth. -/
theorem reinhardtTheorem6_nonvacuous :
    ∃ (𝓢 : ArithmeticTheory) (K F : ArithmeticSentence → ArithmeticSentence) (conF : ArithmeticSentence),
      ClosedUnderNecessitation (𝗣𝗔 : ArithmeticTheory) K ∧ KnowledgeClosedUnderMP (𝗣𝗔 : ArithmeticTheory) K ∧
      KnowledgeSelfReflective (𝗣𝗔 : ArithmeticTheory) K ∧ (𝗣𝗔 : ArithmeticTheory) ⪯ 𝓢 ∧ KnowsOwnFactivity 𝓢 K ∧
      (∃ s, 𝓢 ⊢ K (s 🡘 K (F (∼s)))) ∧ (∀ σ, (𝗣𝗔 : ArithmeticTheory) ⊢ conF 🡒 ∼(F σ ⋏ F (∼σ))) ∧
      (∀ σ, 𝓢 ⊢ K (K σ 🡒 F σ)) ∧ Entailment.Consistent 𝓢 := by
  refine ⟨𝗣𝗔, id, fun _ => ⊤, ⊥, fun φ h => h, fun φ ψ => by simp only [id]; cl_prover,
    fun φ => by simp only [id]; cl_prover, inferInstance, fun φ => by simp only [id]; cl_prover,
    ⟨⊤, by simp only [id]; cl_prover⟩, fun σ => by cl_prover, fun σ => by simp only [id]; cl_prover, inferInstance⟩

/-- S2g: every hypothesis holds in a consistent system. `F` is "Peano arithmetic proves", and with the trivial
knower "whatever `F` holds of is known" is the reflection schema. -/
theorem reinhardtTheorem1Safe_nonvacuous :
    ∃ (𝓢 : ArithmeticTheory) (K F : ArithmeticSentence → ArithmeticSentence),
      ClosedUnderNecessitation (𝗣𝗔 : ArithmeticTheory) K ∧ (𝗣𝗔 : ArithmeticTheory) ⪯ 𝓢 ∧
      KnowledgeClosedUnderMP 𝓢 K ∧ KnowsOwnFactivity 𝓢 K ∧ HasGödelSentence (𝗣𝗔 : ArithmeticTheory) F ∧
      (∀ φ, 𝓢 ⊢ K (F φ 🡒 K φ)) ∧ Entailment.Consistent 𝓢 := by
  refine ⟨PAWithReflection, id, provablePA, fun φ h => h,
    Entailment.Axiomatized.weakerThanOfSubset Set.subset_union_left, fun φ ψ => by simp only [id]; cl_prover,
    fun φ => by simp only [id]; cl_prover,
    ⟨gödel (𝗣𝗔 : ArithmeticTheory).standardProvability,
      Entailment.WeakerThan.pbl (𝓢 := (𝗜𝚺₁ : ArithmeticTheory)) gödel_spec⟩, ?_, consistent_PAWithReflection⟩
  intro φ
  have : (𝗣𝗔 : ArithmeticTheory).standardProvability.refl φ ∈ PAWithReflection :=
    Set.mem_union_right _ ((Provability.mem_localReflectionOn_iff _).mpr ⟨φ, trivial, rfl⟩)
  exact Entailment.Axiomatized.by_axm this

#assert_standard_axioms reinhardtTheorem6_nonvacuous reinhardtTheorem1Safe_nonvacuous

end GodelArgument
