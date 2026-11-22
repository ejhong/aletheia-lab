import GodelArgument.Basic
import GodelArgument.Audit

/-!
# Stage 1 results

Each theorem has exactly the type of a statement in `Statement.lean`. Where the proof is a restatement of a
theorem already in the Foundation library, the docstring names it.
-/

namespace GodelArgument

open FFL FFL.FirstOrder FFL.FirstOrder.Arithmetic FFL.FirstOrder.ProvabilityAbstraction

/-- S1a. Restates Foundation's `craig_consistent_unprovable_of_RE` (Gödel's second incompleteness theorem for
recursively enumerable theories). -/
theorem penroseConditional : PenroseConditional := by
  intro K F _ _ hK hcon hmem
  unfold IsTheoremSetOf at hK; subst hK
  have : Entailment.Consistent F := consistent_of_theory hcon
  exact craig_consistent_unprovable_of_RE F (mem_theory.mp hmem)

/-- S1a′. The same theorem, read as a refutation. -/
theorem noConsistentMindKnowsOwnMachineConsistent : NoConsistentMindKnowsOwnMachineConsistent := by
  intro K F _ _ hcon ⟨hK, hmem⟩
  exact penroseConditional K F hK hcon hmem

/-- S1a″. Inclusion uses derivability condition D1 for Foundation's standard provability predicate; strictness
uses `craig_consistent_unprovable_of_RE`. -/
theorem knownSoundMachineIsExceeded : KnownSoundMachineIsExceeded := by
  intro K F _ _ _ hclosed hcon hrefl
  have hKc : Entailment.Consistent (K : ArithmeticTheory) := hcon
  -- Every theorem of `F` is in `K`: basic arithmetic proves "F proves σ", and `K` accepts "if F proves σ then σ".
  have hsub : F.theory ⊆ K := by
    intro σ hσ
    have h1 : Theory.craig F ⊢ σ := Entailment.WeakerThan.pbl (𝓢 := F) (mem_theory.mp hσ)
    have h2 : 𝗜𝚺₁ ⊢ (Theory.craig F).standardProvability σ := Provability.D1 h1
    have h3 : (K : ArithmeticTheory) ⊢ (Theory.craig F).standardProvability σ := Entailment.WeakerThan.pbl h2
    have h4 : (K : ArithmeticTheory) ⊢ (Theory.craig F).standardProvability σ 🡒 σ :=
      Entailment.Axiomatized.by_axm (hrefl (refl_mem (Theory.craig F) σ))
    exact hclosed (mem_theory.mpr (h4 ⨀ h3))
  -- So `F` is consistent, because `K` is.
  have hFc : Entailment.Consistent F := by
    by_contra hc
    exact not_consistent_of_provable_bot
      (Entailment.Axiomatized.by_axm (hsub (mem_theory.mpr (provable_bot_of_not_consistent hc)))) hKc
  -- And `K` holds a sentence `F` cannot prove: "if F proves ⊥ then ⊥".
  refine ⟨hsub, fun h => ?_⟩
  have hin : (Theory.craig F).standardProvability.refl ⊥ ∈ K := hrefl (refl_mem (Theory.craig F) ⊥)
  exact craig_consistent_unprovable_of_RE F (con_of_refl_bot (Theory.craig F) (mem_theory.mp (h hin)))

/-- S1b(i). Uses Foundation's instances for Peano arithmetic and `craig_consistent_unprovable_of_RE`. -/
theorem standardObjectionWitness : StandardObjectionWitness := by
  refine ⟨⟨𝗣𝗔, inferInstance, rfl⟩, sound_theory, consistent_theory_of_models, ?_, ?_⟩
  · exact con_true (Theory.craig 𝗣𝗔)
  · intro h
    exact craig_consistent_unprovable_of_RE 𝗣𝗔 (mem_theory.mp h)

/-- S1b(ii). Restates Foundation's `gödel_iff_con` (formalized first incompleteness theorem). -/
theorem machineProvesConditional : MachineProvesConditional := by
  intro F _ _
  have h : 𝗜𝚺₁ ⊢ gödel F.standardProvability 🡘 F.standardProvability.con := gödel_iff_con
  have h' : F ⊢ gödel F.standardProvability 🡘 F.standardProvability.con := Entailment.WeakerThan.pbl h
  rw [con_eq] at h'
  cl_prover [h']

/-- S1b(iii). Uses `craig_consistent_unprovable_of_RE` twice: for the first machine and for the second. -/
theorem secondMachine : SecondMachine := by
  intro F _ _ hF
  have hm := models_of_sound hF
  have hs := sigma1Sound_of_models F
  have hre : Theory.RE (F ∪ {Con F}) :=
    Theory.RE.add inferInstance (Theory.RE.ofFinite (Set.finite_singleton _))
  have htrue : IsTrue (Con F) := con_true (Theory.craig F)
  have hm' := models_union_singleton hF htrue
  have hs' := sigma1Sound_of_models (F ∪ {Con F})
  have hle : 𝗜𝚺₁ ⪯ (F ∪ {Con F} : ArithmeticTheory) :=
    Entailment.WeakerThan.trans (inferInstance : 𝗜𝚺₁ ⪯ F)
      (Entailment.Axiomatized.weakerThanOfSubset Set.subset_union_left)
  refine ⟨hre, sound_theory, ?_, ?_, ?_⟩
  · exact mem_theory.mpr (Entailment.Axiomatized.by_axm (Set.mem_union_right _ rfl))
  · intro h; exact craig_consistent_unprovable_of_RE F (mem_theory.mp h)
  · intro h; exact craig_consistent_unprovable_of_RE (F ∪ {Con F}) (mem_theory.mp h)

/-- S1c. Restates Foundation's abstract `con_unprovable` (Gödel's second incompleteness theorem for any
predicate satisfying the derivability conditions). -/
theorem chalmersPoint : ChalmersPoint := by
  intro L _ _ T₀ T _ _ 𝔅 _ h
  by_contra hc
  have : Entailment.Consistent T := Entailment.not_inconsistent_iff_consistent.mp hc
  exact con_unprovable (𝔅 := 𝔅) h

/-- S1c′. Restates Foundation's abstract `löb_theorem`, applied to falsehood. -/
theorem selfSoundnessInconsistent : SelfSoundnessInconsistent := by
  intro L _ _ T₀ T _ _ 𝔅 _ h
  exact Entailment.inconsistent_iff_provable_bot.mpr (ProvabilityAbstraction.löb_theorem (𝔅 := 𝔅) (h ⊥))

/-- S1c″. The soundness theorem of first-order logic, as in Foundation's `models_of_provable`. -/
theorem soundPlusTrueIsSound : SoundPlusTrueIsSound := by
  intro T σ hT hσ
  have := models_union_singleton hT hσ
  exact sound_theory

/-- S1c‴. Uses Foundation's `models_localReflectionOn`. -/
theorem soundPlusItsSoundnessIsSound : SoundPlusItsSoundnessIsSound := by
  intro T _ hT
  have := models_of_sound hT
  have : ℕ↓[ℒₒᵣ] ⊧* (T ∪ T.localReflectionOn Set.univ) := models_localReflectionOn
  exact sound_theory

/-- S1d. The undecided sentence is the consistency statement of the machine together with Peano arithmetic;
its unprovability is `craig_consistent_unprovable_of_RE`. -/
theorem godelDisjunction : GodelDisjunction := by
  intro K hK
  by_cases hmech : IsMechanical K
  · right
    obtain ⟨F, hRE, hKF⟩ := hmech
    unfold IsTheoremSetOf at hKF
    have hFs : Sound F := fun σ hσ => hK σ (hKF ▸ mem_theory.mpr (Entailment.Axiomatized.by_axm hσ))
    let T : ArithmeticTheory := F ∪ 𝗣𝗔
    have hTre : T.RE := Theory.RE.add hRE inferInstance
    have hmod : ℕ↓[ℒₒᵣ] ⊧* T := models_union hFs sound_PA
    have hS := sigma1Sound_of_models T
    have hle : 𝗜𝚺₁ ⪯ T := Entailment.WeakerThan.trans (inferInstance : 𝗜𝚺₁ ⪯ 𝗣𝗔)
      (Entailment.Axiomatized.weakerThanOfSubset Set.subset_union_right)
    have hT : IsTrue (Con T) := con_true (Theory.craig T)
    refine ⟨Con T, ?_, hT, fun h => ?_, fun h => ?_⟩
    · simp [IsPi1, Con]
    · rw [hKF] at h
      exact craig_consistent_unprovable_of_RE T (Entailment.WeakerThan.pbl (𝓢 := F) (mem_theory.mp h))
    · have : ℕ↓[ℒₒᵣ] ⊧ ∼(Con T) := hK _ h
      simp at this
      exact this hT
  · left; exact hmech

/-- S1d′. Uses Foundation's `exists_true_but_unprovable_sentence_of_RE_of_sigma1sound` (Gödel's first
incompleteness theorem for sound recursively enumerable theories). -/
theorem godelDisjunctionRE : GodelDisjunctionRE := by
  intro K hK
  by_cases hre : Theory.RE (K : ArithmeticTheory)
  · right
    let T : ArithmeticTheory := K ∪ 𝗣𝗔
    have hRE : T.RE := Theory.RE.add hre inferInstance
    have hmod : ℕ↓[ℒₒᵣ] ⊧* T := models_union hK sound_PA
    have hR : 𝗥₀ ⪯ T := Entailment.WeakerThan.trans (inferInstance : 𝗥₀ ⪯ 𝗣𝗔)
      (Entailment.Axiomatized.weakerThanOfSubset Set.subset_union_right)
    have hS := sigma1Sound_of_models T
    obtain ⟨δ, hδ, hnot⟩ := exists_true_but_unprovable_sentence_of_RE_of_sigma1sound T
    refine ⟨δ, hδ, fun h => hnot (Entailment.Axiomatized.by_axm (Set.mem_union_left _ h)), fun h => ?_⟩
    have : ℕ↓[ℒₒᵣ] ⊧ ∼δ := hK _ h
    simp at this
    exact this hδ
  · left; exact hre

/-- S1e. A direct diagonal argument on Mathlib's codes for partial recursive functions. -/
theorem penroseTuring : PenroseTuring := by
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

#assert_standard_axioms penroseConditional noConsistentMindKnowsOwnMachineConsistent knownSoundMachineIsExceeded
#assert_standard_axioms standardObjectionWitness machineProvesConditional secondMachine
#assert_standard_axioms chalmersPoint selfSoundnessInconsistent soundPlusTrueIsSound soundPlusItsSoundnessIsSound
#assert_standard_axioms godelDisjunction godelDisjunctionRE penroseTuring

end GodelArgument
