import GodelArgument.Statement6
import GodelArgument.Results
import GodelArgument.Results2
import GodelArgument.Results5

/-!
# Tier 2D results (Amendment 6)

Each theorem has exactly the type of a statement in `Statement6.lean`.

The arithmetic results rest on two theorems of the Foundation library: Gödel's second incompleteness theorem
for recursively enumerable theories (`craig_consistent_unprovable_of_RE`), and the fact that a sentence is
unprovable exactly when adding its negation is consistent (`unprovable_iff_consistent_adjoin`). The abstract
results are propositional reasoning from their hypotheses.
-/

namespace GodelArgument

open FFL FFL.FirstOrder FFL.FirstOrder.Arithmetic FFL.FirstOrder.ProvabilityAbstraction

/-! ## Helper lemmas -/

/-- Adding one sentence to Peano arithmetic leaves it recursively enumerable. -/
instance paPlusNotCon_RE : Theory.RE PAPlusNotCon :=
  Theory.RE.add inferInstance (Theory.RE.ofFinite (Set.finite_singleton _))

/-- The theorem set of `F`, used as axioms, proves no more than `F`. -/
lemma theory_le (F : ArithmeticTheory) : (F.theory : ArithmeticTheory) ⪯ F :=
  Entailment.WeakerThan.ofAxm! (fun hσ => mem_theory.mp hσ)

/-- A theorem set is deductively closed. -/
lemma deductivelyClosed_theory (F : ArithmeticTheory) : DeductivelyClosed F.theory := by
  intro σ hσ
  have := theory_le F
  exact mem_theory.mpr (Entailment.WeakerThan.pbl (𝓢 := (F.theory : ArithmeticTheory)) (mem_theory.mp hσ))

/-- Peano arithmetic does not prove its own consistency, so adding the denial of it is consistent. -/
instance paPlusNotCon_consistent : Entailment.Consistent PAPlusNotCon := by
  have h : 𝗣𝗔 ⊬ Con 𝗣𝗔 := craig_consistent_unprovable_of_RE 𝗣𝗔
  have : Entailment.Consistent (insert (∼Con 𝗣𝗔) 𝗣𝗔 : ArithmeticTheory) :=
    Entailment.unprovable_iff_consistent_adjoin.mp h
  simpa [PAPlusNotCon, Set.union_singleton] using this

/-- The consistency statement of Peano arithmetic is true. -/
lemma con_PA_true : IsTrue (Con 𝗣𝗔) := con_true (Theory.craig 𝗣𝗔)

/-- So its negation is false. -/
lemma notCon_false : ¬ IsTrue (∼Con 𝗣𝗔) := by
  have h := con_PA_true
  unfold IsTrue at h ⊢
  simpa using h

/-- The system D28 proves the sentence it was given as an axiom. -/
lemma notCon_mem : (∼Con 𝗣𝗔) ∈ PAPlusNotCon.theory :=
  mem_theory.mpr (Entailment.Axiomatized.by_axm (Set.mem_union_right _ rfl))

/-- The consistency statement of D28 is true, because D28 is consistent. -/
lemma con_paPlusNotCon_true : IsTrue (Con PAPlusNotCon) := con_true (Theory.craig PAPlusNotCon)

/-! ## Arithmetic -/

/-- S5a. Consistency from Gödel's second incompleteness theorem for Peano arithmetic. -/
theorem consistencyDoesNotGiveSoundness : ConsistencyDoesNotGiveSoundness := by
  refine ⟨inferInstance, ?_, con_paPlusNotCon_true, notCon_mem, notCon_false⟩
  have := theory_le PAPlusNotCon
  exact Entailment.Consistent.of_le paPlusNotCon_consistent this

/-- S5b. The mind is the theorem set of Peano arithmetic together with the consistency statement of D28. -/
theorem machineOutrunsMindThatKnowsItConsistent : MachineOutrunsMindThatKnowsItConsistent := by
  refine ⟨inferInstance, fun K hK => ⟨_, notCon_mem, fun h => notCon_false (hK _ h)⟩, ?_⟩
  have hm := models_union_singleton sound_PA con_paPlusNotCon_true
  refine ⟨(𝗣𝗔 ∪ {Con PAPlusNotCon}).theory, ⟨_, ?_, rfl⟩, sound_theory, deductivelyClosed_theory _, ?_, ?_⟩
  · exact Theory.RE.add inferInstance (Theory.RE.ofFinite (Set.finite_singleton _))
  · intro σ hσ
    have : 𝗣𝗔 ⪯ (𝗣𝗔 ∪ {Con PAPlusNotCon} : ArithmeticTheory) :=
      Entailment.Axiomatized.weakerThanOfSubset Set.subset_union_left
    exact mem_theory.mpr (Entailment.WeakerThan.pbl (𝓢 := 𝗣𝗔) (mem_theory.mp hσ))
  · exact mem_theory.mpr (Entailment.Axiomatized.by_axm (Set.mem_union_right _ rfl))

/-- S5g. The machine is Peano arithmetic. The non-machine is the set of all true sentences; that it is the
theorem set of no machine follows from Gödel's disjunction (S1d), since it leaves no true sentence out. -/
theorem mindAssumptionsDoNotDecide : MindAssumptionsDoNotDecide := by
  refine ⟨⟨𝗣𝗔.theory, sound_theory, consistent_theory_of_models, deductivelyClosed_theory _, subset_rfl,
    ⟨𝗣𝗔, inferInstance, rfl⟩⟩, ?_⟩
  let K : Mind := {σ | IsTrue σ}
  have hK : Sound K := fun σ hσ => hσ
  have hmod : ℕ↓[ℒₒᵣ] ⊧* (K : ArithmeticTheory) := models_of_sound hK
  refine ⟨K, hK, Theory.consistent_of_satisfiable ⟨ℕ↓[ℒₒᵣ], hmod⟩, ?_, ?_, ?_⟩
  · intro σ hσ
    exact models_of_provable hmod (mem_theory.mp hσ)
  · intro σ hσ
    exact sound_theory (F := 𝗣𝗔) σ hσ
  · intro hmech
    rcases godelDisjunction K hK with h | ⟨σ, _, hσ, hn, _⟩
    · exact h hmech
    · exact hn hσ

/-! ## Abstract -/

/-- S5c. Two uses of closure under modus ponens. -/
theorem corollaryHoldsWhereConsistencyGivesSoundness : CorollaryHoldsWhereConsistencyGivesSoundness := by
  intro Fm S _ _ _ 𝓢 _ K F conF φ hmp h1 h2
  cl_prover [hmp conF (F φ 🡒 φ), hmp (F φ) φ, h1, h2]

/-- S5d. Propositional reasoning from the four hypotheses. -/
theorem mindInsideMachineCannotKnowItConsistent : MindInsideMachineCannotKnowItConsistent := by
  intro Fm S _ _ _ 𝓢 _ K F conF h1 h2 h3 h4
  cl_prover [h1, h2, h3, h4]

/-- S5e. Propositional reasoning from the three hypotheses. -/
theorem unrestrictedThesisRefuted : UnrestrictedThesisRefuted := by
  intro Fm S _ _ _ 𝓢 _ K F τ σ G h1 h2 h3
  cl_prover [h1, h2, h3]

/-- S5f. One instance of the determinateness axiom for conditionals. -/
theorem conditionalDeterminateIfPartsAre : ConditionalDeterminateIfPartsAre := by
  intro Fm S _ _ _ 𝓢 _ T D σ G hdi h1 h2
  cl_prover [hdi σ G, h1, h2]

#assert_standard_axioms consistencyDoesNotGiveSoundness machineOutrunsMindThatKnowsItConsistent
#assert_standard_axioms mindAssumptionsDoNotDecide corollaryHoldsWhereConsistencyGivesSoundness
#assert_standard_axioms mindInsideMachineCannotKnowItConsistent unrestrictedThesisRefuted
#assert_standard_axioms conditionalDeterminateIfPartsAre

end GodelArgument
