import GodelArgument.Statement

/-!
# Helper lemmas

Small facts connecting the lab's definitions to the Foundation library. Nothing here is a headline result.
-/

namespace GodelArgument

open FFL FFL.FirstOrder FFL.FirstOrder.Arithmetic FFL.FirstOrder.ProvabilityAbstraction

/-- Membership in a theorem set is provability. -/
lemma mem_theory {T : ArithmeticTheory} {σ : ArithmeticSentence} : σ ∈ T.theory ↔ T ⊢ σ := by
  simp [Theory.theory]

/-- A theory that proves a contradiction is not consistent. -/
lemma not_consistent_of_provable_bot {T : ArithmeticTheory} (h : T ⊢ ⊥) : ¬ Entailment.Consistent T :=
  Entailment.not_consistent_iff_inconsistent.mpr (Entailment.inconsistent_iff_provable_bot.mpr h)

/-- A theory that is not consistent proves a contradiction. -/
lemma provable_bot_of_not_consistent {T : ArithmeticTheory} (h : ¬ Entailment.Consistent T) : T ⊢ ⊥ :=
  Entailment.inconsistent_iff_provable_bot.mp (Entailment.not_consistent_iff_inconsistent.mp h)

/-- If the theorem set of `F` is consistent, so is `F`. -/
lemma consistent_of_theory {F : ArithmeticTheory} (h : Entailment.Consistent (F.theory : ArithmeticTheory)) :
    Entailment.Consistent F := by
  by_contra hc
  exact not_consistent_of_provable_bot
    (Entailment.Axiomatized.by_axm (mem_theory.mpr (provable_bot_of_not_consistent hc))) h

/-- Sound axioms are true in the standard model, in Foundation's sense. -/
lemma models_of_sound {T : ArithmeticTheory} (h : Sound T) : ℕ↓[ℒₒᵣ] ⊧* T := ⟨fun {σ} hσ => h σ hσ⟩

/-- Soundness theorem: if the axioms are true, every theorem is true. -/
lemma sound_theory {F : ArithmeticTheory} [ℕ↓[ℒₒᵣ] ⊧* F] : Sound F.theory := by
  intro σ hσ
  exact models_of_provable inferInstance (mem_theory.mp hσ)

/-- A theory with true axioms has a consistent theorem set. -/
lemma consistent_theory_of_models {F : ArithmeticTheory} [ℕ↓[ℒₒᵣ] ⊧* F] :
    Entailment.Consistent (F.theory : ArithmeticTheory) :=
  Theory.consistent_of_satisfiable ⟨ℕ↓[ℒₒᵣ], ⟨fun {σ} hσ => sound_theory σ hσ⟩⟩

/-- A theory with true axioms is Σ₁-sound. -/
lemma sigma1Sound_of_models (T : ArithmeticTheory) [h : ℕ↓[ℒₒᵣ] ⊧* T] : T.SoundOnHierarchy 𝚺 1 :=
  ⟨fun hp _ => models_of_provable h hp⟩

/-- True axioms stay true when one true sentence is added. -/
lemma models_union_singleton {T : ArithmeticTheory} {σ : ArithmeticSentence} (hT : Sound T) (hσ : IsTrue σ) :
    ℕ↓[ℒₒᵣ] ⊧* (T ∪ {σ} : ArithmeticTheory) := ⟨by
  rintro τ (h | h)
  · exact hT τ h
  · rw [Set.mem_singleton_iff] at h; subst h; exact hσ⟩

/-- Two sets of true axioms together are true. -/
lemma models_union {T U : ArithmeticTheory} (hT : Sound T) (hU : Sound U) :
    ℕ↓[ℒₒᵣ] ⊧* (T ∪ U : ArithmeticTheory) := ⟨by
  rintro τ (h | h)
  · exact hT τ h
  · exact hU τ h⟩

/-- Peano arithmetic is sound. -/
lemma sound_PA : Sound 𝗣𝗔 := fun _ hσ =>
  Semantics.modelsSet_iff.mp (inferInstance : ℕ↓[ℒₒᵣ] ⊧* 𝗣𝗔) hσ

/-- The abstract consistency statement of the standard provability predicate is Foundation's `consistent`. -/
lemma con_eq (F : ArithmeticTheory) [F.Δ₁] : F.standardProvability.con = F.consistent.val := by
  simp [Provability.con, Theory.consistent, standardProvability_def]

/-- The consistency statement of a consistent Δ₁-presented theory is true. -/
lemma con_true (F : ArithmeticTheory) [F.Δ₁] [Entailment.Consistent F] : IsTrue F.consistent.val := by
  unfold IsTrue
  rw [← con_eq]
  simp [Provability.con, models_standardProvability_iff]

/-- The instance of "if `F` proves `σ` then `σ`" belongs to the reflection schema. -/
lemma refl_mem (F : ArithmeticTheory) [F.Δ₁] (σ : ArithmeticSentence) :
    F.standardProvability.refl σ ∈ F.localReflectionOn Set.univ :=
  (Provability.mem_localReflectionOn_iff _).mpr ⟨σ, trivial, rfl⟩

/-- A theory proving "if I prove ⊥ then ⊥" proves its own consistency statement. -/
lemma con_of_refl_bot {T : ArithmeticTheory} (F : ArithmeticTheory) [F.Δ₁]
    (h : T ⊢ F.standardProvability.refl ⊥) : T ⊢ F.consistent.val := by
  have hp : T ⊢ F.standardProvability ⊥ 🡒 ⊥ := h
  have hc : T ⊢ F.standardProvability.con := by
    unfold Provability.con; cl_prover [hp]
  rwa [con_eq] at hc

end GodelArgument
