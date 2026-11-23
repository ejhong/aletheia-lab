import GodelArgument.Results2

/-!
# Stage 2A: the hypotheses can hold together

For each statement of Stage 2A that starts from assumptions, a consistent system in which the assumptions hold.
All three witnesses use the trivial knower, `K φ := φ`, over Peano arithmetic. They show that the hypotheses do
not clash. They do not exhibit an interesting knower; S2e does that, for a knower without known factivity.
-/

namespace GodelArgument

open FFL FFL.FirstOrder FFL.FirstOrder.Arithmetic FFL.FirstOrder.ProvabilityAbstraction

/-- S2a, S2a′: every hypothesis holds in a consistent system. `F` is "Peano arithmetic proves", and the system is
Peano arithmetic with reflection, which proves "if `F` holds of φ then φ" for every φ. -/
theorem reinhardtTheorem3_nonvacuous :
    ∃ (𝓢 : ArithmeticTheory) (K F : ArithmeticSentence → ArithmeticSentence),
      ClosedUnderNecessitation (𝗣𝗔 : ArithmeticTheory) K ∧ (𝗣𝗔 : ArithmeticTheory) ⪯ 𝓢 ∧
      KnowledgeClosedUnderMP 𝓢 K ∧ Factive 𝓢 K ∧ HasGödelSentence (𝗣𝗔 : ArithmeticTheory) F ∧
      (∀ φ, 𝓢 ⊢ K (F φ 🡒 φ)) ∧ Entailment.Consistent 𝓢 := by
  refine ⟨PAWithReflection, id, provablePA, fun φ h => h,
    Entailment.Axiomatized.weakerThanOfSubset Set.subset_union_left, fun φ ψ => by simp only [id]; cl_prover,
    fun φ => by simp only [id]; cl_prover,
    ⟨gödel (𝗣𝗔 : ArithmeticTheory).standardProvability,
      Entailment.WeakerThan.pbl (𝓢 := (𝗜𝚺₁ : ArithmeticTheory)) gödel_spec⟩, ?_, consistent_PAWithReflection⟩
  intro φ
  have : (𝗣𝗔 : ArithmeticTheory).standardProvability.refl φ ∈ PAWithReflection :=
    Set.mem_union_right _ ((Provability.mem_localReflectionOn_iff _).mpr ⟨φ, trivial, rfl⟩)
  exact Entailment.Axiomatized.by_axm this

/-- S2b: every hypothesis holds in a consistent system. `F` holds of everything (`F φ := ⊤`), the degenerate
case of an inconsistent `F`; S2b's conclusion is then that it is known that `F`'s consistency is not known. -/
theorem absoluteSecondIncompleteness_nonvacuous :
    ∃ (𝓢 : ArithmeticTheory) (K F : ArithmeticSentence → ArithmeticSentence),
      ClosedUnderNecessitation (𝗣𝗔 : ArithmeticTheory) K ∧ (𝗣𝗔 : ArithmeticTheory) ⪯ 𝓢 ∧
      KnowledgeClosedUnderMP 𝓢 K ∧ KnowsOwnFactivity 𝓢 K ∧
      ((𝗣𝗔 : ArithmeticTheory) ⊢ F (∼F ⊥) 🡒 F ⊥) ∧ (∀ φ, 𝓢 ⊢ K (K φ 🡒 F φ)) ∧ Entailment.Consistent 𝓢 := by
  refine ⟨𝗣𝗔, id, fun _ => ⊤, fun φ h => h, inferInstance, fun φ ψ => by simp only [id]; cl_prover,
    fun φ => by simp only [id]; cl_prover, by cl_prover, fun φ => by simp only [id]; cl_prover, inferInstance⟩

/-- S2c, S2d: the hypotheses about `K`, and a Gödel sentence for `F`, hold in a consistent system. So the
contradiction in S2c comes from adding "it is known that being known coincides with `F`". -/
theorem knowingWhichSystem_nonvacuous :
    ∃ (𝓢 : ArithmeticTheory) (K F : ArithmeticSentence → ArithmeticSentence),
      ClosedUnderNecessitation (𝗣𝗔 : ArithmeticTheory) K ∧ (𝗣𝗔 : ArithmeticTheory) ⪯ 𝓢 ∧
      KnowledgeClosedUnderMP 𝓢 K ∧ Factive 𝓢 K ∧ KnowsOwnFactivity 𝓢 K ∧
      HasGödelSentence (𝗣𝗔 : ArithmeticTheory) F ∧ Entailment.Consistent 𝓢 := by
  refine ⟨𝗣𝗔, id, provablePA, fun φ h => h, inferInstance, fun φ ψ => by simp only [id]; cl_prover,
    fun φ => by simp only [id]; cl_prover, fun φ => by simp only [id]; cl_prover,
    ⟨gödel (𝗣𝗔 : ArithmeticTheory).standardProvability,
      Entailment.WeakerThan.pbl (𝓢 := (𝗜𝚺₁ : ArithmeticTheory)) gödel_spec⟩, inferInstance⟩

#assert_standard_axioms reinhardtTheorem3_nonvacuous absoluteSecondIncompleteness_nonvacuous
#assert_standard_axioms knowingWhichSystem_nonvacuous

end GodelArgument
