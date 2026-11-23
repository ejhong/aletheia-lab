module

public import UnfoldingArgument.Statement
import UnfoldingArgument.Results
public import UnfoldingArgument.Results2
import UnfoldingArgument.Audit
import Mathlib.Tactic

/-!
# Non-vacuity

A theorem with assumptions can hold only because the assumptions cannot be met. Each instance here shows that
the assumptions of some statement can hold together. Also here: the two definitions `Recurrent` and `LoopFree`
are each other's negation, and an integrated network is recurrent.
-/

namespace Unfolding

open Relation

public theorem recurrent_iff_not_loopFree {I O : Type} (N : Network I O) : N.Recurrent ↔ ¬ N.LoopFree := by
  unfold Network.Recurrent Network.LoopFree
  push Not
  rfl

public theorem integrated_recurrent {I O : Type} (N : Network I O) (h : N.Integrated) : N.Recurrent := by
  obtain ⟨⟨n⟩, hall⟩ := h
  exact ⟨n, hall n n⟩

/-- The assumptions of S2d hold in a setup that does have a falsification on both sides. -/
public theorem strictDependence_instance :
    ∃ (ic : Bool → Bool) (rc : Bool → Bool) (pred : Bool → Set Bool) (inf : Bool → Bool) (O Obar : Set Bool),
      O ⊆ Obar ∧ (∀ o ∈ Obar, ∃ o' ∈ O, rc o' = rc o) ∧ (∃ f : Bool → Bool, ∀ o ∈ Obar, ic o = f (rc o)) ∧
      (∃ o ∈ O, inf (rc o) ∉ pred (ic o)) := by
  refine ⟨id, id, fun _ => {true}, id, Set.univ, Set.univ, subset_rfl, ?_, ⟨id, fun _ _ => rfl⟩, ?_⟩
  · intro o _; exact ⟨o, Set.mem_univ _, rfl⟩
  · exact ⟨false, Set.mem_univ _, by simp⟩

/-- S1c is not vacuous: a loop-free network exists. -/
public theorem loopFree_exists : ∃ N : Network Bool Bool, N.LoopFree :=
  ⟨latch.unfold 1, (unfoldingAtFiniteHorizon Bool Bool latch 1).1⟩

/-- S1e is not vacuous, and its bound is met: for every `T` there is a loop-free network that behaves as
the latch for `T` steps and has exactly `T` nodes. -/
public theorem latch_twin_with_exactly_T_nodes (T : ℕ) :
    ∃ N : Network Bool Bool, N.LoopFree ∧ Network.AgreeUpTo T N latch ∧ N.size = T := by
  obtain ⟨h1, h2, h3⟩ := unfoldingAtFiniteHorizon Bool Bool latch T
  refine ⟨latch.unfold T, h1, h2, ?_⟩
  rw [h3]
  show T * Fintype.card Unit = T
  simp

/-- S2a to S2c are not vacuous: the two-system setup has a substitution at its one inference content,
which arises, and so has a universal substitution. -/
public theorem substitution_exists :
    twoSystems.SubstitutionAt () ∧ twoSystems.Arises () ∧ twoSystems.UniversalSubstitution :=
  ⟨twoSystems_substitution, twoSystems_arises, twoSystems_universal⟩

/-- The assumptions of S2e and of S2f hold together for one verdict: "conscious exactly when recurrent". -/
public theorem causal_structure_verdict_exists :
    ∃ conscious : Network Bool Bool → Prop,
      (∀ N, N.LoopFree → ¬ conscious N) ∧ (∃ N, conscious N) ∧
      (∀ N, N.Integrated → conscious N) ∧ (∃ N, ¬ conscious N) := by
  refine ⟨fun N => N.Recurrent, ?_, ⟨latch, latchHasNoLoopFreeTwin.1⟩, integrated_recurrent, ?_⟩
  · intro N hN hR
    exact (recurrent_iff_not_loopFree N).mp hR hN
  · obtain ⟨N, hN⟩ := loopFree_exists
    exact ⟨N, fun hR => (recurrent_iff_not_loopFree N).mp hR hN⟩

end Unfolding

#assert_standard_axioms Unfolding.recurrent_iff_not_loopFree Unfolding.integrated_recurrent
  Unfolding.strictDependence_instance Unfolding.loopFree_exists Unfolding.latch_twin_with_exactly_T_nodes
  Unfolding.substitution_exists Unfolding.causal_structure_verdict_exists
