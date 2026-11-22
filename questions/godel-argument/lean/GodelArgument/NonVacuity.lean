import GodelArgument.Results

/-!
# Non-vacuity

When a theorem starts from assumptions, it could hold merely because the assumptions contradict each other. Each
theorem here exhibits a concrete case in which the assumptions of a Stage 1 statement hold together. The
witness is Peano arithmetic throughout.
-/

namespace GodelArgument

open FFL FFL.FirstOrder FFL.FirstOrder.Arithmetic FFL.FirstOrder.ProvabilityAbstraction

/-- S1a, S1a′: a consistent mind that is the theorem set of a formal system including basic arithmetic. -/
theorem penroseConditional_nonvacuous :
    ∃ (K : Mind) (F : ArithmeticTheory) (_ : F.RE) (_ : 𝗜𝚺₁ ⪯ F), IsTheoremSetOf K F ∧ Consistent K :=
  ⟨𝗣𝗔.theory, 𝗣𝗔, inferInstance, inferInstance, rfl, consistent_theory_of_models⟩

/-- The Craig presentation of Peano arithmetic is sound. -/
lemma sound_craig_PA : Sound (Theory.craig 𝗣𝗔) := fun _ hσ =>
  models_of_provable (inferInstance : ℕ↓[ℒₒᵣ] ⊧* 𝗣𝗔)
    (Entailment.WeakerThan.pbl (𝓢 := Theory.craig 𝗣𝗔) (Entailment.Axiomatized.by_axm hσ))

/-- S1a″: a consistent, deductively closed mind, able to do basic arithmetic, that contains the soundness of a
formal system. The mind is the theorem set of Peano arithmetic plus "whatever Peano arithmetic proves is so". -/
theorem knownSoundMachineIsExceeded_nonvacuous :
    ∃ (K : Mind) (F : ArithmeticTheory) (_ : F.RE) (_ : 𝗜𝚺₁ ⪯ F) (_ : 𝗜𝚺₁ ⪯ (K : ArithmeticTheory)),
      DeductivelyClosed K ∧ Consistent K ∧ ContainsSoundnessOf K F := by
  let U : ArithmeticTheory := 𝗣𝗔 ∪ (Theory.craig 𝗣𝗔).localReflectionOn Set.univ
  have hRfn : Sound ((Theory.craig 𝗣𝗔).localReflectionOn Set.univ) := by
    have := models_of_sound sound_craig_PA
    have hm : ℕ↓[ℒₒᵣ] ⊧* (Theory.craig 𝗣𝗔 ∪ (Theory.craig 𝗣𝗔).localReflectionOn Set.univ) :=
      models_localReflectionOn
    exact fun σ hσ => Semantics.modelsSet_iff.mp hm (Set.mem_union_right _ hσ)
  have hU : ℕ↓[ℒₒᵣ] ⊧* U := models_union sound_PA hRfn
  have hle : 𝗜𝚺₁ ⪯ (U.theory : ArithmeticTheory) :=
    ⟨fun _ h => Entailment.Axiomatized.by_axm (mem_theory.mpr
      (Entailment.WeakerThan.pbl (𝓢 := 𝗣𝗔) (𝓣 := U)
        (Entailment.WeakerThan.pbl (𝓢 := 𝗜𝚺₁) (𝓣 := 𝗣𝗔) h)))⟩
  have hback : (U.theory : ArithmeticTheory) ⪯ U := by
    apply Entailment.WeakerThan.ofAxm!
    intro φ hφ
    exact mem_theory.mp hφ
  refine ⟨U.theory, 𝗣𝗔, inferInstance, inferInstance, hle, ?_, consistent_theory_of_models, ?_⟩
  · intro σ hσ
    exact mem_theory.mpr (Entailment.WeakerThan.pbl (mem_theory.mp hσ))
  · intro σ hσ
    exact mem_theory.mpr (Entailment.Axiomatized.by_axm (Set.mem_union_right _ hσ))

/-- S1b(ii): a consistent formal system, with a Δ₁ presentation, including basic arithmetic. -/
theorem machineProvesConditional_nonvacuous :
    ∃ (F : ArithmeticTheory) (_ : F.Δ₁) (_ : 𝗜𝚺₁ ⪯ F), Entailment.Consistent F :=
  ⟨𝗣𝗔, inferInstance, inferInstance, inferInstance⟩

/-- S1b(iii): a sound formal system including basic arithmetic. -/
theorem secondMachine_nonvacuous :
    ∃ (F : ArithmeticTheory) (_ : F.RE) (_ : 𝗜𝚺₁ ⪯ F), Sound F :=
  ⟨𝗣𝗔, inferInstance, inferInstance, sound_PA⟩

/-- S1c, S1c′: Chalmers's assumptions (1)–(3) and the ability to form self-referential sentences hold of a
consistent system, namely Peano arithmetic with its standard provability predicate. So the contradiction in
S1c comes from adding assumption (4), not from (1)–(3). -/
theorem chalmersPoint_nonvacuous :
    ∃ (T₀ T : Theory ℒₒᵣ) (_ : Diagonalization T₀) (_ : T₀ ⪯ T) (𝔅 : Provability T₀ T) (_ : 𝔅.HBL),
      Entailment.Consistent T :=
  ⟨𝗜𝚺₁, 𝗣𝗔, inferInstance, inferInstance, (𝗣𝗔 : ArithmeticTheory).standardProvability, inferInstance, inferInstance⟩

/-- S1c″: a sound system and a true sentence. -/
theorem soundPlusTrueIsSound_nonvacuous :
    ∃ (T : ArithmeticTheory) (σ : ArithmeticSentence), Sound T ∧ IsTrue σ :=
  ⟨𝗣𝗔, Con 𝗣𝗔, sound_PA, con_true (Theory.craig 𝗣𝗔)⟩

/-- S1c‴: a sound system with a Δ₁ presentation. -/
theorem soundPlusItsSoundnessIsSound_nonvacuous :
    ∃ (T : ArithmeticTheory) (_ : T.Δ₁), Sound T :=
  ⟨𝗣𝗔, inferInstance, sound_PA⟩

/-- S1d: a sound set of sentences that is the theorem set of a machine, so the second alternative of the
disjunction is the one that applies. -/
theorem godelDisjunction_nonvacuous : ∃ K : Mind, Sound K ∧ IsMechanical K :=
  ⟨𝗣𝗔.theory, sound_theory, ⟨𝗣𝗔, inferInstance, rfl⟩⟩

/-- S1d′: a sound, recursively enumerable set of sentences (the axioms of Peano arithmetic). -/
theorem godelDisjunctionRE_nonvacuous : ∃ K : Mind, Sound K ∧ Theory.RE (K : ArithmeticTheory) :=
  ⟨𝗣𝗔, sound_PA, inferInstance⟩

/-- S1e: a recursively enumerable, sound certifier of non-halting. The simplest one certifies nothing. -/
theorem penroseTuring_nonvacuous :
    ∃ A : ℕ → Prop, REPred A ∧ ∀ n, A n → ¬ ((Denumerable.ofNat Nat.Partrec.Code n).eval n).Dom :=
  ⟨fun _ => False, REPred.const False, fun _ h => h.elim⟩

#assert_standard_axioms penroseConditional_nonvacuous knownSoundMachineIsExceeded_nonvacuous
#assert_standard_axioms machineProvesConditional_nonvacuous secondMachine_nonvacuous chalmersPoint_nonvacuous
#assert_standard_axioms soundPlusTrueIsSound_nonvacuous soundPlusItsSoundnessIsSound_nonvacuous
#assert_standard_axioms godelDisjunction_nonvacuous godelDisjunctionRE_nonvacuous penroseTuring_nonvacuous

end GodelArgument
