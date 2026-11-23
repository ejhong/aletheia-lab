import GodelArgument.Results5
import GodelArgument.NonVacuity2

/-!
# Tier 2C: the hypotheses can hold together

For the statements of tier 2C that end in a positive conclusion (S4a, S4e, S4f, S4g), a consistent system in which
every hypothesis holds. The witnesses are deliberately trivial: Peano arithmetic, with `T φ` and `K φ` read as
`φ` and `D φ` as truth, and with falsehood for `σ`. They show that the hypotheses do not clash, and nothing
more. S4b, S4c and S4d end in a contradiction, so their hypotheses cannot all hold in a consistent system; that
is their content.
-/

namespace GodelArgument

open FFL FFL.FirstOrder FFL.FirstOrder.Arithmetic

/-- S4a, S4e, S4g: every hypothesis holds in a consistent system. -/
theorem penroseArgument_nonvacuous :
    ∃ (𝓢 : ArithmeticTheory) (T K D : ArithmeticSentence → ArithmeticSentence) (σ S₀ S' G P Q : ArithmeticSentence),
      𝓢 ⊢ σ 🡒 T σ ∧ KIntro 𝓢 K ∧ DeterminateTruth 𝓢 D T ∧ DKIntro 𝓢 D K ∧ DeterminateImp 𝓢 D T ∧
      DeterminateK 𝓢 D K ∧ 𝓢 ⊢ D σ ∧ 𝓢 ⊢ D (σ 🡒 G) ∧ 𝓢 ⊢ D (σ 🡒 S') ∧ 𝓢 ⊢ D (K (σ 🡒 G)) ∧
      𝓢 ⊢ σ 🡒 S₀ ∧ 𝓢 ⊢ S₀ 🡒 T σ 🡒 S' ∧ 𝓢 ⊢ S' 🡒 G ∧ 𝓢 ⊢ S' 🡒 ∼P ∧ 𝓢 ⊢ Q 🡒 P ∧ 𝓢 ⊢ σ 🡒 K (σ 🡒 G) 🡒 Q ∧
      Entailment.Consistent 𝓢 := by
  refine ⟨𝗣𝗔, id, id, fun _ => ⊤, ⊥, ⊥, ⊥, ⊤, ⊥, ⊥, by simp only [id]; cl_prover, fun φ h => h,
    fun φ => by simp only [id]; cl_prover, fun φ h _ => h, fun φ ψ => by simp only [id]; cl_prover,
    fun φ => by cl_prover, by cl_prover, by cl_prover, by cl_prover, by cl_prover, by cl_prover,
    by simp only [id]; cl_prover, by cl_prover, by cl_prover, by cl_prover, by simp only [id]; cl_prover,
    inferInstance⟩

/-- S4f: every hypothesis holds in a consistent system. `D` is falsehood throughout, so nothing is determinate. -/
theorem stepsIndeterminate_nonvacuous :
    ∃ (𝓢 : ArithmeticTheory) (T K D : ArithmeticSentence → ArithmeticSentence) (σ : ArithmeticSentence),
      DeterminateImp 𝓢 D T ∧ DeterminateK 𝓢 D K ∧ 𝓢 ⊢ ∼D σ ∧ Entailment.Consistent 𝓢 := by
  refine ⟨𝗣𝗔, id, id, fun _ => ⊥, ⊤, fun φ ψ => by cl_prover, fun φ => by cl_prover, by cl_prover, inferInstance⟩

#assert_standard_axioms penroseArgument_nonvacuous stepsIndeterminate_nonvacuous

end GodelArgument
