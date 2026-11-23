import GodelArgument.Results
import GodelArgument.Results2
import GodelArgument.Results5
/-! Exploratory only. Draft statements of Amendment 6 with trial proofs, compiled before the lock to make
sure no draft statement is false as written. Not a finding. -/
namespace GodelArgument

open FFL FFL.FirstOrder FFL.FirstOrder.Arithmetic FFL.FirstOrder.ProvabilityAbstraction

/-! ## Arithmetic: a consistent machine need not be sound -/

/-- **D28. Peano arithmetic with the denial of its own consistency.** The axioms of Peano arithmetic together
with the one sentence "Peano arithmetic is inconsistent". -/
noncomputable def PAPlusNotCon : ArithmeticTheory := 𝗣𝗔 ∪ {∼Con 𝗣𝗔}

/-- **S5a. Consistency does not give soundness.** The system D28 is a formal system (recursively enumerable).
It is consistent, and its own consistency statement is true. Yet it proves the sentence "Peano arithmetic is
inconsistent", which is false. -/
def ConsistencyDoesNotGiveSoundness : Prop :=
  ∃ _ : Theory.RE PAPlusNotCon,
    Consistent PAPlusNotCon.theory ∧ IsTrue (Con PAPlusNotCon) ∧
      (∼Con 𝗣𝗔) ∈ PAPlusNotCon.theory ∧ ¬ IsTrue (∼Con 𝗣𝗔)

/-- **S5b. A machine can prove what a mind cannot know, while the mind knows the machine consistent.** Take the
machine D28. Every sound mind lacks some sentence that this machine proves. And there is a mind that is sound,
deductively closed, contains every theorem of Peano arithmetic, is itself the theorem set of a machine, and
contains the consistency statement of D28. -/
def MachineOutrunsMindThatKnowsItConsistent : Prop :=
  ∃ _ : Theory.RE PAPlusNotCon,
    (∀ K : Mind, Sound K → ∃ σ, σ ∈ PAPlusNotCon.theory ∧ σ ∉ K) ∧
    (∃ K : Mind, IsMechanical K ∧ Sound K ∧ DeductivelyClosed K ∧ 𝗣𝗔.theory ⊆ K ∧ Con PAPlusNotCon ∈ K)

/-- **S5g. The assumptions of Stage 1 about a mind are met by a machine and by a non-machine.** There is a mind
that is sound, consistent, deductively closed, contains every theorem of Peano arithmetic, and is the theorem
set of a machine. There is another with the same four properties that is the theorem set of no machine. -/
def MindAssumptionsDoNotDecide : Prop :=
  (∃ K : Mind, Sound K ∧ Consistent K ∧ DeductivelyClosed K ∧ 𝗣𝗔.theory ⊆ K ∧ IsMechanical K) ∧
  (∃ K : Mind, Sound K ∧ Consistent K ∧ DeductivelyClosed K ∧ 𝗣𝗔.theory ⊆ K ∧ ¬ IsMechanical K)

/-! ## Abstract: the corollary, and two more steps of Corradini and Galvan -/

/-- **S5c. The corollary holds for a sentence for which consistency gives soundness.** Let `conF` stand for
"F is consistent". Suppose knowledge is closed under modus ponens, it is known that if F is consistent then
whatever F proves of `φ` is so ("if F proves `φ` then `φ`"), and whenever F proves `φ` it is known that F proves
`φ`. Then: if `φ` is not known and F proves `φ`, the consistency of F is not known. -/
def CorollaryHoldsWhereConsistencyGivesSoundness : Prop :=
  ∀ (Fm S : Type) [LogicalConnective Fm] [LogicalNeutral Fm] [Entailment S Fm] (𝓢 : S) [Entailment.Cl 𝓢]
    (K F : Fm → Fm) (conF φ : Fm),
    KnowledgeClosedUnderMP 𝓢 K →
    𝓢 ⊢ K (conF 🡒 F φ 🡒 φ) →
    𝓢 ⊢ F φ 🡒 K (F φ) →
    𝓢 ⊢ ∼K φ ⋏ F φ 🡒 ∼K conF

/-- **S5d. A mind whose arithmetic lies inside a machine cannot know that machine consistent.** Let `conF`
stand for "F is consistent". Suppose that what is known about `conF` is so, in both directions (if `conF` is
known it holds; if its negation is known, its negation holds); that if `conF` is known then F proves it; and
that if F is consistent then F does not prove `conF` (the second incompleteness theorem for F). Then `conF` is
not known; and if F is consistent, the negation of `conF` is not known either. -/
def MindInsideMachineCannotKnowItConsistent : Prop :=
  ∀ (Fm S : Type) [LogicalConnective Fm] [LogicalNeutral Fm] [Entailment S Fm] (𝓢 : S) [Entailment.Cl 𝓢]
    (K F : Fm → Fm) (conF : Fm),
    𝓢 ⊢ K conF 🡒 conF →
    𝓢 ⊢ K (∼conF) 🡒 ∼conF →
    𝓢 ⊢ K conF 🡒 F conF →
    𝓢 ⊢ conF 🡒 ∼F conF →
    𝓢 ⊢ ∼K conF ⋏ (conF 🡒 ∼K (∼conF))

/-- **S5e. From the restricted result to the refutation of the unrestricted thesis** (Corradini and Galvan's
step 8). Let `σ` say that knowledge and F agree on arithmetic sentences, and `τ` that they agree on all
sentences. Suppose the system proves that `σ → G` is known and that, if `σ`, F does not prove `σ → G`. Suppose
`τ` implies `σ`, and `τ` implies that `σ → G` is known exactly when F proves it. Then the system proves that `τ`
fails. -/
def UnrestrictedThesisRefuted : Prop :=
  ∀ (Fm S : Type) [LogicalConnective Fm] [LogicalNeutral Fm] [Entailment S Fm] (𝓢 : S) [Entailment.Cl 𝓢]
    (K F : Fm → Fm) (τ σ G : Fm),
    𝓢 ⊢ K (σ 🡒 G) ⋏ (σ 🡒 ∼F (σ 🡒 G)) →
    𝓢 ⊢ τ 🡒 σ →
    𝓢 ⊢ τ 🡒 (K (σ 🡒 G) 🡘 F (σ 🡒 G)) →
    𝓢 ⊢ ∼τ

/-- **S5f. A conditional with determinate parts is determinate** (Corradini and Galvan's Lemma 2, given
Lemma 1). By the determinateness axiom for conditionals: if the system proves `σ` determinate and proves `G`
determinate, it proves `σ → G` determinate. -/
def ConditionalDeterminateIfPartsAre : Prop :=
  ∀ (Fm S : Type) [LogicalConnective Fm] [LogicalNeutral Fm] [Entailment S Fm] (𝓢 : S) [Entailment.Cl 𝓢]
    (T D : Fm → Fm) (σ G : Fm),
    DeterminateImp 𝓢 D T → 𝓢 ⊢ D σ → 𝓢 ⊢ D G → 𝓢 ⊢ D (σ 🡒 G)



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

-- #assert_standard_axioms consistencyDoesNotGiveSoundness machineOutrunsMindThatKnowsItConsistent
-- #assert_standard_axioms mindAssumptionsDoNotDecide corollaryHoldsWhereConsistencyGivesSoundness
-- #assert_standard_axioms mindInsideMachineCannotKnowItConsistent unrestrictedThesisRefuted
-- #assert_standard_axioms conditionalDeterminateIfPartsAre


end GodelArgument
