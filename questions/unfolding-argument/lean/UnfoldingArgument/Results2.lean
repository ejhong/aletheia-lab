module

public import UnfoldingArgument.Statement
import UnfoldingArgument.Results
import UnfoldingArgument.Audit
import Mathlib.Tactic

/-!
# Stage 2 results: the falsification argument and the replies

Each headline theorem has exactly the type of a statement in `Statement.lean`. S2e, S2f and S2g use the Stage 1
theorems S1a, S1h and S1d. `twoSystems` is the two-system setup used for S2c′ and for the non-vacuity of S2a to
S2c. None of the proofs is a restatement of a Mathlib theorem.
-/

namespace Unfolding

universe u v w

open Relation

/-! ### Stage 2 -/

public theorem substitutionGivesFalsification : SubstitutionGivesFalsification := by
  intro P D E R t r ⟨S, p, hdisj⟩
  obtain ⟨o, ho, hor⟩ := p.2
  obtain ⟨o', ho', hor'⟩ := (S p).2
  by_cases h : t.inf r ∈ t.pred o
  · refine ⟨o', hor', ⟨_, ho'⟩, ?_⟩
    intro h'
    rw [hor'] at h'
    have : t.inf r ∈ t.predOf p.1 ∩ t.predOf (S p).1 := ⟨⟨o, ho, h⟩, ⟨o', ho', h'⟩⟩
    rw [hdisj] at this
    exact this
  · refine ⟨o, hor, ⟨_, ho⟩, ?_⟩
    intro h'
    rw [hor] at h'
    exact h h'

public theorem universalSubstitutionFalsifiesEveryReport : UniversalSubstitutionFalsifiesEveryReport := by
  intro P D E R t hU r hr
  exact substitutionGivesFalsification P D E R t r (hU r hr)

public theorem everyInferenceWrongOrTheoryWrong : EveryInferenceWrongOrTheoryWrong := by
  intro P D E R t hU truth
  by_cases h : ∃ p, ∃ o ∈ t.obs p, truth p ∉ t.pred o
  · exact Or.inr h
  · left
    push Not at h
    intro r hr
    obtain ⟨o, hor, ⟨p, hop⟩, hf⟩ := universalSubstitutionFalsifiesEveryReport P D E R t hU r hr
    refine ⟨p, o, hop, hor, ?_⟩
    intro heq
    apply hf
    rw [hor, heq]
    exact h p o hop

/-- A testing setup with a substitution at every inference content: two systems, one report. -/
@[expose] public def twoSystems : Testing Bool Bool Bool Unit where
  obs := fun p => {p}
  pred := fun o => {o}
  rep := fun _ => ()
  inf := fun _ => true

public theorem twoSystems_substitution : twoSystems.SubstitutionAt () := by
  have hmem : ∀ b : Bool, b ∈ twoSystems.Produces () := fun b => ⟨b, rfl, rfl⟩
  refine ⟨fun p => ⟨!p.1, hmem _⟩, ⟨true, hmem _⟩, ?_⟩
  ext e
  simp only [Set.mem_inter_iff, Set.mem_empty_iff_false, iff_false, not_and]
  rintro ⟨o, ho, he⟩ ⟨o', ho', he'⟩
  have h1 : o = true := ho
  have h2 : o' = false := ho'
  have h3 : e = o := he
  have h4 : e = o' := he'
  rw [h3, h1] at h4
  rw [h2] at h4
  exact Bool.noConfusion h4

public theorem twoSystems_universal : twoSystems.UniversalSubstitution := by
  intro r _
  cases r
  exact twoSystems_substitution

public theorem twoSystems_arises : twoSystems.Arises () := ⟨true, ⟨true, rfl⟩, rfl⟩

public theorem someInferenceCanStillBeRight : SomeInferenceCanStillBeRight := by
  refine ⟨Bool, Bool, Bool, Unit, twoSystems, id, twoSystems_universal, ?_, ⟨true, true, rfl, rfl⟩⟩
  intro p o ho
  have h : o = p := ho
  rw [h]
  rfl

public theorem strictDependenceLeavesNothingToTest : StrictDependenceLeavesNothingToTest := by
  intro D Ic Rc E ic rc pred inf O Obar hsub hrep ⟨f, hf⟩
  constructor
  · rintro ⟨o, ho, hfal⟩
    obtain ⟨o', ho', hr⟩ := hrep o ho
    refine ⟨o', ho', ?_⟩
    rw [hf o' (hsub ho'), hr, ← hf o ho]
    exact hfal
  · rintro ⟨o, ho, hfal⟩
    exact ⟨o, hsub ho, hfal⟩

public theorem strictDependenceCanStillBeTested : StrictDependenceCanStillBeTested := by
  refine ⟨Bool, Bool, Bool, Bool, id, id, fun _ => {true}, id, {true}, Set.univ, ?_, ⟨id, ?_⟩, ?_, ?_⟩
  · exact Set.subset_univ _
  · intro o _; rfl
  · rintro ⟨o, ho, h⟩
    apply h
    simp only [Set.mem_singleton_iff] at ho
    simp [ho]
  · exact ⟨false, Set.mem_univ _, by simp⟩

public theorem unfoldingArgumentAtFiniteHorizon : UnfoldingArgumentAtFiniteHorizon := by
  intro I O T conscious hlf ⟨N, hN⟩ inf
  by_cases h : inf (N.behaviourUpTo T)
  · refine ⟨N.unfold T, ?_⟩
    obtain ⟨hloop, hagree, _⟩ := unfoldingAtFiniteHorizon I O N T
    have hb : (N.unfold T).behaviourUpTo T = N.behaviourUpTo T := by
      funext xs
      exact hagree xs.1 xs.2
    rw [hb]
    intro hiff
    exact hlf _ hloop (hiff.mpr h)
  · exact ⟨N, fun hiff => h (hiff.mp hN)⟩

public theorem foldingArgumentAtEveryHorizon : FoldingArgumentAtEveryHorizon := by
  intro I O hI conscious hint ⟨N, hN⟩ inf
  obtain ⟨N', hN', _, hagree⟩ := everyNetworkHasIntegratedTwin I O hI N
  have hb : N'.response = N.response := funext hagree
  by_cases h : inf N.response
  · exact ⟨N, fun hiff => hN (hiff.mpr h)⟩
  · refine ⟨N', ?_⟩
    rw [hb]
    intro hiff
    exact h (hiff.mp (hint N' hN'))

public theorem loopFreeExclusionSurvivesUnboundedHorizon : LoopFreeExclusionSurvivesUnboundedHorizon := by
  refine ⟨fun N => ¬ ∃ N' : Network Bool Bool, N'.LoopFree ∧ Network.AgreeAlways N' N,
    fun b => ¬ ∃ N' : Network Bool Bool, N'.LoopFree ∧ ∀ xs, N'.response xs = b xs, ?_, ?_, ?_⟩
  · intro N hN h
    exact h ⟨N, hN, fun _ => rfl⟩
  · exact ⟨latch, latchHasNoLoopFreeTwin.2⟩
  · intro N
    exact Iff.rfl

public theorem sparedIffDeterminedByBehaviour : SparedIffDeterminedByBehaviour.{u, v, w} := by
  intro Sys Beh E hE beh pred
  classical
  constructor
  · rintro ⟨inf, hinf⟩ s s' hb
    rw [hinf s, hinf s', hb]
  · intro h
    obtain ⟨e0⟩ := hE
    refine ⟨fun b => if hb : ∃ s, beh s = b then pred (Classical.choose hb) else e0, ?_⟩
    intro s
    have hb : ∃ s', beh s' = beh s := ⟨s, rfl⟩
    simp only [hb, dite_true]
    exact h _ _ (Classical.choose_spec hb).symm

public theorem furtherEvidenceRemovesMismatch : FurtherEvidenceRemovesMismatch.{u, v, w} := by
  intro Sys Beh E beh pred
  exact ⟨E, pred, fun bx => bx.2, fun _ => rfl⟩

end Unfolding

#assert_standard_axioms Unfolding.substitutionGivesFalsification Unfolding.universalSubstitutionFalsifiesEveryReport Unfolding.everyInferenceWrongOrTheoryWrong Unfolding.someInferenceCanStillBeRight Unfolding.strictDependenceLeavesNothingToTest Unfolding.strictDependenceCanStillBeTested Unfolding.unfoldingArgumentAtFiniteHorizon Unfolding.foldingArgumentAtEveryHorizon Unfolding.loopFreeExclusionSurvivesUnboundedHorizon Unfolding.sparedIffDeterminedByBehaviour Unfolding.furtherEvidenceRemovesMismatch
