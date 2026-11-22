import GodelArgument.Statement
/-! Exploratory only: checks that the Stage 1 statements are provable as written. Not a finding. -/
namespace GodelArgument
open FFL FFL.FirstOrder FFL.FirstOrder.Arithmetic FFL.FirstOrder.ProvabilityAbstraction

lemma mem_theory {T : ArithmeticTheory} {σ : ArithmeticSentence} : σ ∈ T.theory ↔ T ⊢ σ := by
  simp [Theory.theory]

example : ChalmersPoint := by
  intro L _ _ T₀ T _ _ 𝔅 _ h
  by_contra hc
  have : Entailment.Consistent T := Entailment.not_inconsistent_iff_consistent.mp hc
  exact con_unprovable (𝔅 := 𝔅) h

example : SelfSoundnessInconsistent := by
  intro L _ _ T₀ T _ _ 𝔅 _ h
  exact Entailment.inconsistent_iff_provable_bot.mpr (ProvabilityAbstraction.löb_theorem (𝔅 := 𝔅) (h ⊥))

lemma consistent_of_theory {F : ArithmeticTheory} (h : Entailment.Consistent (F.theory : ArithmeticTheory)) :
    Entailment.Consistent F := by
  by_contra hc
  have hb : F ⊢ ⊥ := Entailment.inconsistent_iff_provable_bot.mp (Entailment.not_consistent_iff_inconsistent.mp hc)
  have : (F.theory : ArithmeticTheory) ⊢ ⊥ := Entailment.Axiomatized.by_axm (mem_theory.mpr hb)
  exact (Entailment.not_consistent_iff_inconsistent.mpr (Entailment.inconsistent_iff_provable_bot.mpr this)) h

example : PenroseConditional := by
  intro K F _ _ hK hcon hmem
  unfold IsTheoremSetOf at hK; subst hK
  have : Entailment.Consistent F := consistent_of_theory hcon
  exact craig_consistent_unprovable_of_RE F (mem_theory.mp hmem)

example : MachineProvesConditional := by
  intro F _ _
  have h : 𝗜𝚺₁ ⊢ gödel F.standardProvability 🡘 F.standardProvability.con := gödel_iff_con
  have h' : F ⊢ gödel F.standardProvability 🡘 F.standardProvability.con := Entailment.WeakerThan.pbl h
  have e : F.standardProvability.con = F.consistent.val := by
    simp [Provability.con, Theory.consistent, standardProvability_def]
  rw [e] at h'
  cl_prover [h']

example : SoundnessOfAnotherIsConsistent := by
  intro T _ hs
  have : ℕ↓[ℒₒᵣ] ⊧* T := ⟨fun {σ} hσ => hs σ hσ⟩
  exact consistent_localReflection_of_sound

example : NoConsistentMindKnowsOwnMachineConsistent := by
  intro K F _ _ hcon ⟨hK, hmem⟩
  unfold IsTheoremSetOf at hK; subst hK
  have : Entailment.Consistent F := consistent_of_theory hcon
  exact craig_consistent_unprovable_of_RE F (mem_theory.mp hmem)

lemma sound_theory {F : ArithmeticTheory} [ℕ↓[ℒₒᵣ] ⊧* F] : Sound F.theory := by
  intro σ hσ
  exact models_of_provable inferInstance (mem_theory.mp hσ)

lemma consistent_theory_of_models {F : ArithmeticTheory} [ℕ↓[ℒₒᵣ] ⊧* F] :
    Entailment.Consistent (F.theory : ArithmeticTheory) :=
  Theory.consistent_of_satisfiable ⟨ℕ↓[ℒₒᵣ], ⟨fun {σ} hσ => sound_theory σ hσ⟩⟩

lemma con_true (F : ArithmeticTheory) [F.Δ₁] [Entailment.Consistent F] : IsTrue F.consistent.val := by
  have e : F.standardProvability.con = F.consistent.val := by
    simp [Provability.con, Theory.consistent, standardProvability_def]
  have h : ¬ F ⊢ ⊥ := fun hb =>
    (Entailment.not_consistent_iff_inconsistent.mpr (Entailment.inconsistent_iff_provable_bot.mpr hb)) inferInstance
  unfold IsTrue
  rw [← e]
  simpa [Provability.con, models_standardProvability_iff] using h
  -- (simp alone may close this; `h` kept for clarity)

example : StandardObjectionWitness := by
  refine ⟨⟨𝗣𝗔, inferInstance, rfl⟩, sound_theory, consistent_theory_of_models, ?_, ?_⟩
  · exact con_true (Theory.craig 𝗣𝗔)
  · intro h
    exact craig_consistent_unprovable_of_RE 𝗣𝗔 (mem_theory.mp h)

example : GodelDisjunctionSemantic := by
  intro K hK
  by_cases hre : Theory.RE (K : ArithmeticTheory)
  · right
    let T : ArithmeticTheory := K ∪ 𝗣𝗔
    have hRE : T.RE := Theory.RE.add hre inferInstance
    have hmod : ℕ↓[ℒₒᵣ] ⊧* T := ⟨by
      rintro σ (hσ | hσ)
      · exact hK σ hσ
      · exact Semantics.modelsSet_iff.mp (inferInstance : ℕ↓[ℒₒᵣ] ⊧* 𝗣𝗔) hσ⟩
    have hR : 𝗥₀ ⪯ T := Entailment.WeakerThan.trans (inferInstance : 𝗥₀ ⪯ 𝗣𝗔)
      (Entailment.Axiomatized.weakerThanOfSubset (Set.subset_union_right))
    have hS : T.SoundOnHierarchy 𝚺 1 := ⟨fun h _ => models_of_provable hmod h⟩
    obtain ⟨δ, hδ, hnot⟩ := exists_true_but_unprovable_sentence_of_RE_of_sigma1sound T
    refine ⟨δ, hδ, fun h => hnot (Entailment.Axiomatized.by_axm (Set.mem_union_left _ h)), fun h => ?_⟩
    have : ℕ↓[ℒₒᵣ] ⊧ ∼δ := hK _ h
    simp at this
    exact this hδ
  · left; exact hre

example : PenroseTuring := by
  intro A hA hsound
  obtain ⟨f, hf, hdom⟩ := REPred.iff'.mp hA
  let g : ℕ →. ℕ := fun n => (f n).map (fun _ => 0)
  have hg : Nat.Partrec g := Partrec.nat_iff.mp (hf.map (Computable.const 0).to₂)
  obtain ⟨c, hc⟩ := Nat.Partrec.Code.exists_code.mp hg
  have key : ∀ n, (c.eval n).Dom ↔ A n := by
    intro n; rw [hc, hdom n]; simp [g]
  refine ⟨Encodable.encode c, ?_, ?_⟩
  · rw [Denumerable.ofNat_encode]
    intro hd
    exact hsound _ ((key _).mp hd) (by rw [Denumerable.ofNat_encode]; exact hd)
  · intro hA'
    exact hsound _ hA' (by rw [Denumerable.ofNat_encode]; exact (key _).mpr hA')

example : KnowingConOnlySeparates := by
  have hmod : ℕ↓[ℒₒᵣ] ⊧* (𝗣𝗔 ∪ 𝗣𝗔.Con : ArithmeticTheory) := ⟨by
    rintro σ (hσ | hσ)
    · exact Semantics.modelsSet_iff.mp (inferInstance : ℕ↓[ℒₒᵣ] ⊧* 𝗣𝗔) hσ
    · rw [Set.mem_singleton_iff] at hσ; subst hσ; exact con_true 𝗣𝗔⟩
  refine ⟨⟨_, Theory.RE.add inferInstance (Theory.RE.ofFinite (Set.finite_singleton _)), rfl⟩, sound_theory, ?_, ?_⟩
  · exact mem_theory.mpr (Entailment.Axiomatized.by_axm (Set.mem_union_right _ rfl))
  · intro h; exact consistent_unprovable 𝗣𝗔 (mem_theory.mp h)

#print axioms consistent_unprovable
#print axioms craig_consistent_unprovable_of_RE
#print axioms ProvabilityAbstraction.löb_theorem
#print axioms exists_true_but_unprovable_sentence_of_RE_of_sigma1sound
#print axioms consistent_localReflection_of_sound

end GodelArgument
