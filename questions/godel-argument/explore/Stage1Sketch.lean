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

example : GodelDisjunctionRE := by
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

lemma models_of_sound {T : ArithmeticTheory} (h : Sound T) : ℕ↓[ℒₒᵣ] ⊧* T := ⟨fun {σ} hσ => h σ hσ⟩

lemma sigma1Sound_of_models (T : ArithmeticTheory) [h : ℕ↓[ℒₒᵣ] ⊧* T] : T.SoundOnHierarchy 𝚺 1 :=
  ⟨fun hp _ => models_of_provable h hp⟩

lemma con_eq (F : ArithmeticTheory) [F.Δ₁] : F.standardProvability.con = F.consistent.val := by
  simp [Provability.con, Theory.consistent, standardProvability_def]

example : KnownSoundMachineIsExceeded := by
  intro K F _ _ _ hclosed hcon hrefl
  have hKc : Entailment.Consistent (K : ArithmeticTheory) := hcon
  have hsub : F.theory ⊆ K := by
    intro σ hσ
    have h1 : Theory.craig F ⊢ σ := Entailment.WeakerThan.pbl (𝓢 := F) (mem_theory.mp hσ)
    have h2 : 𝗜𝚺₁ ⊢ (Theory.craig F).standardProvability σ := Provability.D1 h1
    have h3 : (K : ArithmeticTheory) ⊢ (Theory.craig F).standardProvability σ := Entailment.WeakerThan.pbl h2
    have h4 : (K : ArithmeticTheory) ⊢ (Theory.craig F).standardProvability σ 🡒 σ :=
      Entailment.Axiomatized.by_axm (hrefl ((Provability.mem_localReflectionOn_iff _).mpr ⟨σ, trivial, rfl⟩))
    exact hclosed (mem_theory.mpr (h4 ⨀ h3))
  have hFc : Entailment.Consistent F := by
    by_contra hc
    have hb : F ⊢ ⊥ := Entailment.inconsistent_iff_provable_bot.mp (Entailment.not_consistent_iff_inconsistent.mp hc)
    have : (K : ArithmeticTheory) ⊢ ⊥ := Entailment.Axiomatized.by_axm (hsub (mem_theory.mpr hb))
    exact (Entailment.not_consistent_iff_inconsistent.mpr (Entailment.inconsistent_iff_provable_bot.mpr this)) hKc
  refine ⟨hsub, fun h => ?_⟩
  have hin : (Theory.craig F).standardProvability.refl ⊥ ∈ K :=
    hrefl ((Provability.mem_localReflectionOn_iff _).mpr ⟨⊥, trivial, rfl⟩)
  have hp : F ⊢ (Theory.craig F).standardProvability ⊥ 🡒 ⊥ := mem_theory.mp (h hin)
  have hc : F ⊢ (Theory.craig F).standardProvability.con := by
    unfold Provability.con; cl_prover [hp]
  rw [con_eq] at hc
  exact craig_consistent_unprovable_of_RE F hc

example : SoundPlusTrueIsSound := by
  intro T σ hT hσ
  have : ℕ↓[ℒₒᵣ] ⊧* (T ∪ {σ} : ArithmeticTheory) := ⟨by
    rintro τ (h | h)
    · exact hT τ h
    · rw [Set.mem_singleton_iff] at h; subst h; exact hσ⟩
  exact sound_theory

example : SoundPlusItsSoundnessIsSound := by
  intro T _ hT
  have := models_of_sound hT
  have : ℕ↓[ℒₒᵣ] ⊧* (T ∪ T.localReflectionOn Set.univ) := models_localReflectionOn
  exact sound_theory

example : SecondMachine := by
  intro F _ _ hF
  have hm := models_of_sound hF
  have hs := sigma1Sound_of_models F
  have hcF : Entailment.Consistent F := inferInstance
  have hre : Theory.RE (F ∪ {Con F}) := Theory.RE.add inferInstance (Theory.RE.ofFinite (Set.finite_singleton _))
  have htrue : IsTrue (Con F) := con_true (Theory.craig F)
  have hm' : ℕ↓[ℒₒᵣ] ⊧* (F ∪ {Con F} : ArithmeticTheory) := ⟨by
    rintro τ (h | h)
    · exact hF τ h
    · rw [Set.mem_singleton_iff] at h; subst h; exact htrue⟩
  have hs' := sigma1Sound_of_models (F ∪ {Con F})
  have hle : 𝗜𝚺₁ ⪯ (F ∪ {Con F} : ArithmeticTheory) :=
    Entailment.WeakerThan.trans (inferInstance : 𝗜𝚺₁ ⪯ F) (Entailment.Axiomatized.weakerThanOfSubset Set.subset_union_left)
  refine ⟨hre, sound_theory, ?_, ?_, ?_⟩
  · exact mem_theory.mpr (Entailment.Axiomatized.by_axm (Set.mem_union_right _ rfl))
  · intro h; exact craig_consistent_unprovable_of_RE F (mem_theory.mp h)
  · intro h; exact craig_consistent_unprovable_of_RE (F ∪ {Con F}) (mem_theory.mp h)

example : GodelDisjunction := by
  intro K hK
  by_cases hmech : IsMechanical K
  · right
    obtain ⟨F, hRE, hKF⟩ := hmech
    unfold IsTheoremSetOf at hKF
    have hFs : Sound F := fun σ hσ => hK σ (hKF ▸ mem_theory.mpr (Entailment.Axiomatized.by_axm hσ))
    let T : ArithmeticTheory := F ∪ 𝗣𝗔
    have hTre : T.RE := Theory.RE.add hRE inferInstance
    have hmod : ℕ↓[ℒₒᵣ] ⊧* T := ⟨by
      rintro σ (hσ | hσ)
      · exact hFs σ hσ
      · exact Semantics.modelsSet_iff.mp (inferInstance : ℕ↓[ℒₒᵣ] ⊧* 𝗣𝗔) hσ⟩
    have hS := sigma1Sound_of_models T
    have hle : 𝗜𝚺₁ ⪯ T := Entailment.WeakerThan.trans (inferInstance : 𝗜𝚺₁ ⪯ 𝗣𝗔)
      (Entailment.Axiomatized.weakerThanOfSubset Set.subset_union_right)
    have hT : IsTrue (Con T) := con_true (Theory.craig T)
    refine ⟨Con T, ?_, hT, fun h => ?_, fun h => ?_⟩
    · simp [IsPi1, Con]
    · rw [hKF] at h
      exact craig_consistent_unprovable_of_RE T
        (Entailment.WeakerThan.pbl (𝓢 := F) (mem_theory.mp h))
    · have : ℕ↓[ℒₒᵣ] ⊧ ∼(Con T) := hK _ h
      simp at this
      exact this hT
  · left; exact hmech

#print axioms consistent_unprovable
#print axioms craig_consistent_unprovable_of_RE
#print axioms ProvabilityAbstraction.löb_theorem
#print axioms exists_true_but_unprovable_sentence_of_RE_of_sigma1sound
#print axioms consistent_localReflection_of_sound

end GodelArgument
