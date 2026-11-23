import UnfoldingArgument.Statement
import Mathlib.Tactic

/-!
Exploratory: instances showing that the assumptions of the statements can hold together.
Nothing here is a finding. The setup `twoSystems` used for S2a to S2c is in `Sketch.lean`, where S2c′ needs it.
-/

namespace Unfolding

open Relation

theorem recurrent_iff_not_loopFree {I O : Type} (N : Network I O) : N.Recurrent ↔ ¬ N.LoopFree := by
  unfold Network.Recurrent Network.LoopFree
  push Not
  rfl

theorem integrated_recurrent {I O : Type} (N : Network I O) (h : N.Integrated) : N.Recurrent := by
  obtain ⟨⟨n⟩, hall⟩ := h
  exact ⟨n, hall n n⟩

/-- The assumptions of S2d hold in a setup that does have a falsification on both sides. -/
theorem strictDependence_instance :
    ∃ (ic : Bool → Bool) (rc : Bool → Bool) (pred : Bool → Set Bool) (inf : Bool → Bool) (O Obar : Set Bool),
      O ⊆ Obar ∧ (∀ o ∈ Obar, ∃ o' ∈ O, rc o' = rc o) ∧ (∃ f : Bool → Bool, ∀ o ∈ Obar, ic o = f (rc o)) ∧
      (∃ o ∈ O, inf (rc o) ∉ pred (ic o)) := by
  refine ⟨id, id, fun _ => {true}, id, Set.univ, Set.univ, subset_rfl, ?_, ⟨id, fun _ _ => rfl⟩, ?_⟩
  · intro o _; exact ⟨o, Set.mem_univ _, rfl⟩
  · exact ⟨false, Set.mem_univ _, by simp⟩

end Unfolding
