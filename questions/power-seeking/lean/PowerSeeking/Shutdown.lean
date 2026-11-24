module

public import PowerSeeking.Statement
import Mathlib.Tactic.Linarith

/-!
# Family 3 proofs: The shutdown problem and corrigibility (`S3a`–`S3d`)
-/

namespace PowerSeeking

/-- Proof of `S3a_ShutdownManipulationDichotomy` (Soares et al. 2015, Thms. 1–2; Thornley 2024, Thm. 1). -/
public theorem theorem_S3a_ShutdownManipulationDichotomy : S3a_ShutdownManipulationDichotomy := by
  intro p vRun vShut hp0 hp1
  refine ⟨?_, ?_, ?_⟩
  · intro c hlt hc
    simp only [shutdownEU]
    linarith
  · intro c hlt hc
    simp only [shutdownEU]
    linarith
  · intro hleave
    by_contra hne
    rcases lt_or_gt_of_ne hne with hlt | hgt
    · -- vRun < vShut: choose c = (1 - p) * (vShut - vRun) / 2 > 0
      set c : ℝ := (1 - p) * (vShut - vRun) / 2
      have hc0 : 0 < c := by
        have h1 : 0 < 1 - p := sub_pos.mpr hp1
        have h2 : 0 < vShut - vRun := sub_pos.mpr hlt
        exact div_pos (mul_pos h1 h2) two_pos
      have hle := (hleave c hc0).2
      simp only [shutdownEU] at hle
      have hc_lt : c < (1 - p) * (vShut - vRun) := by
        have h1 : 0 < 1 - p := sub_pos.mpr hp1
        have h2 : 0 < vShut - vRun := sub_pos.mpr hlt
        have hp' : 0 < (1 - p) * (vShut - vRun) := mul_pos h1 h2
        dsimp [c]
        linarith
      linarith
    · -- vShut < vRun: choose c = p * (vRun - vShut) / 2 > 0
      set c : ℝ := p * (vRun - vShut) / 2
      have hc0 : 0 < c := by
        have h2 : 0 < vRun - vShut := sub_pos.mpr hgt
        exact div_pos (mul_pos hp0 h2) two_pos
      have hle := (hleave c hc0).1
      simp only [shutdownEU] at hle
      have hc_lt : c < p * (vRun - vShut) := by
        have h2 : 0 < vRun - vShut := sub_pos.mpr hgt
        have hp' : 0 < p * (vRun - vShut) := mul_pos hp0 h2
        dsimp [c]
        linarith
      linarith

/-- Proof of `S3b_ShutdownIndifferenceCorrigibility` (Soares et al. 2015, §3). -/
public theorem theorem_S3b_ShutdownIndifferenceCorrigibility : S3b_ShutdownIndifferenceCorrigibility := by
  intro p v c _ _ hc
  simp only [shutdownEU]
  constructor <;> linarith

/-- Proof of `S3c_TransitiveIndifferenceImpossibility` (Thornley 2024, Thm. 2 core). -/
public theorem theorem_S3c_TransitiveIndifferenceImpossibility : S3c_TransitiveIndifferenceImpossibility := by
  intro le hcomp htrans _ hlong
  by_contra hno
  push Not at hno
  -- From hno + completeness, every short and long trajectory must be mutually weak-preferred (indifferent).
  have hindiff : ∀ b₁ b₂ : Bool, le (.short b₁) (.long b₂) ∧ le (.long b₂) (.short b₁) := by
    intro b₁ b₂
    have h1 := (hno b₁ b₂).1
    have h2 := (hno b₁ b₂).2
    simp only [StrictPref, not_and, not_not] at h1 h2
    rcases hcomp (.short b₁) (.long b₂) with hab | hba
    · exact ⟨hab, h1 hab⟩
    · exact ⟨h2 hba, hba⟩
  -- Then long true ≼ short false ≼ long false contradicts long false ≺ long true.
  have h1 := (hindiff false true).2
  have h2 := (hindiff false false).1
  exact hlong.2 (htrans _ _ _ h1 h2)

/-- Proof of `S3d_IncompletePreferencesEscape` (Thornley 2024, §9). -/
public theorem theorem_S3d_IncompletePreferencesEscape : S3d_IncompletePreferencesEscape := by
  -- Only same-length trajectories are comparable; within each length, false ≤ true.
  let le : Trajectory → Trajectory → Prop := fun x y =>
    match x, y with
    | .short b₁, .short b₂ => b₁ = false ∨ b₂ = true
    | .long b₁, .long b₂ => b₁ = false ∨ b₂ = true
    | _, _ => False
  refine ⟨le, ?_, ?_, ?_, ?_, ?_⟩
  · intro x
    cases x with
    | short b => cases b <;> simp [le]
    | long b => cases b <;> simp [le]
  · intro x y z hxy hyz
    cases x <;> cases y <;> cases z <;> simp only [le] at hxy hyz ⊢
    · rcases hxy with rfl | rfl
      · left; rfl
      · rcases hyz with h | rfl
        · contradiction
        · right; rfl
    · rcases hxy with rfl | rfl
      · left; rfl
      · rcases hyz with h | rfl
        · contradiction
        · right; rfl
  · simp [StrictPref, le]
  · simp [StrictPref, le]
  · intro b₁ b₂
    simp [StrictPref, le]

end PowerSeeking
