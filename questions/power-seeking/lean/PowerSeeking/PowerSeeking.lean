module

public import PowerSeeking.Statement
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.FinCases
import Mathlib.Data.Finset.Card
import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Algebra.BigOperators.Fin
import Mathlib.Algebra.Order.BigOperators.Group.Finset

/-!
# Family 2 proofs: Parametric retargetability and optimal-policy power-seeking (`S2a`–`S2f`)
-/

namespace PowerSeeking

open scoped BigOperators

/-! ## Helper lemmas for orbits and retargetability -/

private lemma mem_orbitIn_iff {ι Θ : Type} [Fintype ι] [DecidableEq ι]
    [MulAction (Equiv.Perm ι) Θ] (S_Θ : Finset Θ) (θ θ' : Θ) :
    θ' ∈ OrbitIn ι S_Θ θ ↔ (∃ ψ : Equiv.Perm ι, ψ • θ = θ') ∧ θ' ∈ S_Θ := by
  classical
  unfold OrbitIn
  simp only [Finset.mem_filter, Finset.mem_image, Finset.mem_univ, true_and]

private lemma smul_mem_orbitIn {ι Θ : Type} [Fintype ι] [DecidableEq ι]
    [MulAction (Equiv.Perm ι) Θ] {S_Θ : Finset Θ} {θ θ' : Θ} (φ : Equiv.Perm ι)
    (hθ' : θ' ∈ OrbitIn ι S_Θ θ) (hmem : φ • θ' ∈ S_Θ) :
    φ • θ' ∈ OrbitIn ι S_Θ θ := by
  rw [mem_orbitIn_iff] at hθ' ⊢
  rcases hθ' with ⟨⟨ψ, rfl⟩, _⟩
  exact ⟨⟨φ * ψ, by rw [mul_smul]⟩, hmem⟩

private lemma smul_injective {ι Θ : Type} [MulAction (Equiv.Perm ι) Θ] (φ : Equiv.Perm ι) :
    Function.Injective (fun θ : Θ => φ • θ) := by
  intro θ₁ θ₂ h
  have := congrArg (fun x => φ⁻¹ • x) h
  simpa [inv_smul_smul] using this

/-- Proof of `S2a_SimpleRetargetability` (Turner & Tadepalli 2022, Prop. 3.4). -/
public theorem theorem_S2a_SimpleRetargetability : S2a_SimpleRetargetability := by
  classical
  intro ι Θ _ _ _ S_Θ fA fB ⟨φ, hφ⟩ θ _
  simp only [one_mul]
  let Aset := (OrbitIn ι S_Θ θ).filter (fun θ' => fB θ' < fA θ')
  let Bset := (OrbitIn ι S_Θ θ).filter (fun θ' => fA θ' < fB θ')
  change Aset.card ≤ Bset.card
  refine Finset.card_le_card_of_injOn (fun θ' => φ • θ') ?_ ?_
  · intro θ' hθ'
    simp only [Aset, Bset, Finset.mem_coe, Finset.mem_filter] at hθ' ⊢
    have hθ'S : θ' ∈ S_Θ := ((mem_orbitIn_iff S_Θ θ θ').mp hθ'.1).2
    have ⟨hmem, hlt⟩ := hφ θ' hθ'S hθ'.2
    exact ⟨smul_mem_orbitIn φ hθ'.1 hmem, hlt⟩
  · intro θ₁ _ θ₂ _ h
    exact smul_injective φ h

/-- Proof of `S2b_MultiplyRetargetable` (Turner & Tadepalli 2022, Thm. 3.6). -/
public theorem theorem_S2b_MultiplyRetargetable : S2b_MultiplyRetargetable := by
  classical
  intro ι Θ _ _ _ n S_Θ fA fB hmult θ hθ
  rcases hmult θ hθ with ⟨φ, hret, hdisj⟩
  let Aset := (OrbitIn ι S_Θ θ).filter (fun θ' => fB θ' < fA θ')
  let Bset := (OrbitIn ι S_Θ θ).filter (fun θ' => fA θ' < fB θ')
  change n * Aset.card ≤ Bset.card
  let img : Fin n → Finset Θ := fun i => Aset.image (fun θ' => φ i • θ')
  have hsub : Finset.univ.biUnion img ⊆ Bset := by
    intro y hy
    simp only [Finset.mem_biUnion, Finset.mem_univ, true_and, img, Finset.mem_image] at hy
    rcases hy with ⟨i, θ', hθ', rfl⟩
    simp only [Aset, Bset, Finset.mem_filter] at hθ' ⊢
    have ⟨hmem, hlt⟩ := hret i θ' hθ'.1 hθ'.2
    exact ⟨smul_mem_orbitIn (φ i) hθ'.1 hmem, hlt⟩
  have hpair : Set.PairwiseDisjoint (↑(Finset.univ : Finset (Fin n))) img := by
    intro i _ j _ hij
    change Disjoint (img i) (img j)
    rw [Finset.disjoint_left]
    intro y hyi hyj
    simp only [img, Finset.mem_image, Aset, Finset.mem_filter] at hyi hyj
    rcases hyi with ⟨θ₁, ⟨h1orb, h1lt⟩, rfl⟩
    rcases hyj with ⟨θ₂, ⟨h2orb, h2lt⟩, hEq⟩
    exact hdisj i j hij θ₁ h1orb h1lt θ₂ h2orb h2lt hEq.symm
  have hcard_union : (Finset.univ.biUnion img).card = ∑ i : Fin n, (img i).card :=
    Finset.card_biUnion (fun i hi j hj hij => hpair hi hj hij)
  have hcard_each : ∀ i : Fin n, (img i).card = Aset.card := by
    intro i
    exact Finset.card_image_of_injective Aset (smul_injective (φ i))
  calc
    n * Aset.card = ∑ _i : Fin n, Aset.card := by simp
    _ = ∑ i : Fin n, (img i).card := Finset.sum_congr rfl (fun i _ => (hcard_each i).symm)
    _ = (Finset.univ.biUnion img).card := hcard_union.symm
    _ ≤ Bset.card := Finset.card_le_card hsub

/-! ## Helper lemmas for inner products, `optVal`, and `powerVal` -/

private lemma dot_permVec {S : Type} [Fintype S] (φ : Equiv.Perm S) (v r : S → ℝ) :
    dot (permVec φ v) (permVec φ r) = dot v r := by
  unfold dot permVec
  exact Equiv.sum_comp φ⁻¹ (fun s => v s * r s)

private lemma permVec_involution {S : Type} {φ : Equiv.Perm S} (hφ : ∀ s, φ (φ s) = s)
    (v : S → ℝ) : permVec φ (permVec φ v) = v := by
  funext s
  simp only [permVec]
  have hinv : φ⁻¹ = φ := by
    ext x
    apply φ.injective
    simp [hφ]
  rw [hinv, hφ]

private lemma permFinset_nonempty {S : Type} (φ : Equiv.Perm S)
    {F : Finset (S → ℝ)} (hF : F.Nonempty) : (permFinset φ F).Nonempty := by
  classical
  unfold permFinset
  exact hF.image (permVec φ)

private lemma mem_permFinset {S : Type} (φ : Equiv.Perm S) (F : Finset (S → ℝ)) (v : S → ℝ) :
    v ∈ permFinset φ F ↔ ∃ u ∈ F, permVec φ u = v := by
  classical
  unfold permFinset
  exact Finset.mem_image

private lemma optVal_permFinset {S : Type} [Fintype S] (φ : Equiv.Perm S)
    (F : Finset (S → ℝ)) (hF : F.Nonempty) (r : S → ℝ) :
    optVal (permFinset φ F) (permFinset_nonempty φ hF) (permVec φ r) = optVal F hF r := by
  unfold optVal
  apply le_antisymm
  · rw [Finset.sup'_le_iff]
    intro v hv
    rw [mem_permFinset] at hv
    rcases hv with ⟨u, hu, rfl⟩
    rw [dot_permVec]
    exact Finset.le_sup' (fun w => dot w r) hu
  · rw [Finset.sup'_le_iff]
    intro u hu
    rw [← dot_permVec φ u r]
    have hmem : permVec φ u ∈ permFinset φ F := (mem_permFinset φ F _).mpr ⟨u, hu, rfl⟩
    exact Finset.le_sup' (fun w => dot w (permVec φ r)) hmem

private lemma optVal_mono {S : Type} [Fintype S] {F₁ F₂ : Finset (S → ℝ)}
    (h₁ : F₁.Nonempty) (h₂ : F₂.Nonempty) (hsub : F₁ ⊆ F₂) (r : S → ℝ) :
    optVal F₁ h₁ r ≤ optVal F₂ h₂ r := by
  unfold optVal
  rw [Finset.sup'_le_iff]
  intro v hv
  exact Finset.le_sup' (fun w => dot w r) (hsub hv)

private lemma permFinset_subset_symm {S : Type} {F₁ F₂ : Finset (S → ℝ)} {φ : Equiv.Perm S}
    (hφ : ∀ s, φ (φ s) = s) (hsub : permFinset φ F₁ ⊆ F₂) :
    F₁ ⊆ permFinset φ F₂ := by
  intro v hv
  have h1 : permVec φ v ∈ permFinset φ F₁ := (mem_permFinset φ F₁ _).mpr ⟨v, hv, rfl⟩
  have h2 : permVec φ v ∈ F₂ := hsub h1
  have h3 : permVec φ (permVec φ v) ∈ permFinset φ F₂ := (mem_permFinset φ F₂ _).mpr ⟨_, h2, rfl⟩
  rwa [permVec_involution hφ v] at h3

private lemma optVal_involution_gap {S : Type} [Fintype S] {F₁ F₂ : Finset (S → ℝ)}
    (h₁ : F₁.Nonempty) (h₂ : F₂.Nonempty) {φ : Equiv.Perm S}
    (hφ : ∀ s, φ (φ s) = s) (hsub : permFinset φ F₁ ⊆ F₂) (r : S → ℝ) :
    optVal F₁ h₁ r - optVal F₂ h₂ r ≤
      optVal F₂ h₂ (permVec φ r) - optVal F₁ h₁ (permVec φ r) := by
  have hA : optVal F₁ h₁ r ≤ optVal F₂ h₂ (permVec φ r) := by
    rw [← optVal_permFinset φ F₁ h₁ r]
    exact optVal_mono (permFinset_nonempty φ h₁) h₂ hsub (permVec φ r)
  have hB : optVal F₁ h₁ (permVec φ r) ≤ optVal F₂ h₂ r := by
    rw [← optVal_permFinset φ F₂ h₂ r]
    exact optVal_mono h₁ (permFinset_nonempty φ h₂) (permFinset_subset_symm hφ hsub) (permVec φ r)
  linarith

private lemma powerVal_smul {S : Type} [Fintype S] (F : Finset (S → ℝ)) (hF : F.Nonempty)
    (φ : Equiv.Perm S) (D : RewardDist S) :
    powerVal F hF (φ • D) = D.mass.sum (fun r p => p * optVal F hF (permVec φ r)) := by
  change (D.mass.equivMapDomain (permVecEquiv φ)).sum (fun r p => p * optVal F hF r) = _
  rw [Finsupp.equivMapDomain_eq_mapDomain]
  rw [Finsupp.sum_mapDomain_index (fun _ => by simp) (fun _ _ _ => by ring)]
  rfl

private lemma powerVal_involution_gap {S : Type} [Fintype S] {F₁ F₂ : Finset (S → ℝ)}
    (h₁ : F₁.Nonempty) (h₂ : F₂.Nonempty) {φ : Equiv.Perm S}
    (hφ : ∀ s, φ (φ s) = s) (hsub : permFinset φ F₁ ⊆ F₂) (D : RewardDist S) :
    powerVal F₁ h₁ D - powerVal F₂ h₂ D ≤
      powerVal F₂ h₂ (φ • D) - powerVal F₁ h₁ (φ • D) := by
  rw [powerVal_smul, powerVal_smul]
  unfold powerVal
  simp only [Finsupp.sum, ← Finset.sum_sub_distrib]
  apply Finset.sum_le_sum
  intro r _
  have hp : 0 ≤ D.mass r := D.nonneg r
  have hgap := optVal_involution_gap h₁ h₂ hφ hsub r
  nlinarith

private lemma finsupp_sum_finset_sum {α β : Type} (s : Finset α) (f : α → β →₀ ℝ)
    (g : β → ℝ → ℝ) (hg0 : ∀ b, g b 0 = 0) (hgadd : ∀ b x y, g b (x + y) = g b x + g b y) :
    (∑ i ∈ s, f i).sum g = ∑ i ∈ s, (f i).sum g := by
  classical
  induction s using Finset.induction_on with
  | empty => simp
  | @insert a t ha ih =>
    rw [Finset.sum_insert ha, Finsupp.sum_add_index (fun b _ => hg0 b) (fun b _ => hgadd b),
      ih, Finset.sum_insert ha]

/-- Uniform orbit-averaged reward distribution over all permutations of `r0`. -/
private noncomputable def orbitAvgDist {S : Type} [Fintype S] [DecidableEq S]
    (r0 : S → ℝ) : RewardDist S where
  mass := ∑ ψ : Equiv.Perm S,
    Finsupp.single (permVec ψ r0) (1 / (Fintype.card (Equiv.Perm S) : ℝ))
  nonneg r := by
    classical
    rw [Finsupp.finsetSum_apply]
    apply Finset.sum_nonneg
    intro ψ _
    rw [Finsupp.single_apply]
    split_ifs
    · positivity
    · exact le_rfl
  sum_one := by
    rw [finsupp_sum_finset_sum _ _ _ (fun _ => rfl) (fun _ _ _ => rfl)]
    have hterm : ∀ ψ : Equiv.Perm S,
        (Finsupp.single (permVec ψ r0) (1 / (Fintype.card (Equiv.Perm S) : ℝ))).sum (fun _ p => p) =
          1 / (Fintype.card (Equiv.Perm S) : ℝ) :=
      fun ψ => Finsupp.sum_single_index rfl
    simp_rw [hterm]
    have hcard : (Fintype.card (Equiv.Perm S) : ℝ) ≠ 0 := by
      exact_mod_cast Fintype.card_ne_zero
    simp [Finset.sum_const, nsmul_eq_mul, hcard]

private lemma orbitAvgDist_invariant {S : Type} [Fintype S] [DecidableEq S]
    (r0 : S → ℝ) (χ : Equiv.Perm S) :
    χ • orbitAvgDist r0 = orbitAvgDist r0 := by
  classical
  ext r
  change ((orbitAvgDist r0).mass.equivMapDomain (permVecEquiv χ)) r = (orbitAvgDist r0).mass r
  rw [Finsupp.equivMapDomain_apply]
  simp only [orbitAvgDist, Finsupp.finsetSum_apply]
  refine Fintype.sum_equiv (Equiv.mulLeft χ) _ _ ?_
  intro ψ
  simp only [Finsupp.single_apply]
  have hmul : (Equiv.mulLeft χ) ψ = χ * ψ := rfl
  rw [hmul]
  have hiff : permVec ψ r0 = (permVecEquiv χ).symm r ↔ permVec (χ * ψ) r0 = r := by
    constructor
    · intro h
      have := congrArg (permVec χ) h
      have hL : permVec χ (permVec ψ r0) = permVec (χ * ψ) r0 := by
        funext s; simp [permVec, Equiv.Perm.mul_apply]
      have hR : permVec χ ((permVecEquiv χ).symm r) = r := (permVecEquiv χ).apply_symm_apply r
      rwa [hL, hR] at this
    · intro h
      have := congrArg (permVec χ⁻¹) h
      have hL : permVec χ⁻¹ (permVec (χ * ψ) r0) = permVec ψ r0 := by
        funext s; simp [permVec, Equiv.Perm.mul_apply]
      rw [hL] at this
      exact this
  simp only [hiff]

private lemma powerVal_orbitAvgDist {S : Type} [Fintype S] [DecidableEq S]
    (F : Finset (S → ℝ)) (hF : F.Nonempty) (r0 : S → ℝ) :
    powerVal F hF (orbitAvgDist r0) =
      (1 / (Fintype.card (Equiv.Perm S) : ℝ)) *
        ∑ ψ : Equiv.Perm S, optVal F hF (permVec ψ r0) := by
  unfold powerVal orbitAvgDist
  rw [finsupp_sum_finset_sum _ _ _ (fun _ => by ring) (fun _ _ _ => by ring)]
  have hterm : ∀ ψ : Equiv.Perm S,
      (Finsupp.single (permVec ψ r0) (1 / (Fintype.card (Equiv.Perm S) : ℝ))).sum
        (fun r p => p * optVal F hF r) =
      (1 / (Fintype.card (Equiv.Perm S) : ℝ)) * optVal F hF (permVec ψ r0) :=
    fun ψ => Finsupp.sum_single_index (zero_mul _)
  simp_rw [hterm]
  rw [Finset.mul_sum]

/-- Proof of `S2c_OptimalPolicyPowerSeeking` (Turner et al. 2021, Prop. 6.6 & Lemma E.24). -/
public theorem theorem_S2c_OptimalPolicyPowerSeeking : S2c_OptimalPolicyPowerSeeking := by
  classical
  intro S _ _ F₁ F₂ h₁ h₂ φ hφ hsub
  refine ⟨?_, ?_, ?_⟩
  · -- Part 1: Orbit tendency via simple retargetability
    intro D
    apply theorem_S2a_SimpleRetargetability
    refine ⟨φ, ?_⟩
    intro D' hD' hlt
    have hmem : φ • D' ∈ distOrbit D := by
      unfold distOrbit at hD' ⊢
      rw [Finset.mem_image] at hD' ⊢
      rcases hD' with ⟨ψ, _, rfl⟩
      exact ⟨φ * ψ, Finset.mem_univ _, by rw [mul_smul]⟩
    have hgap := powerVal_involution_gap h₁ h₂ hφ hsub D'
    exact ⟨hmem, by linarith⟩
  · -- Part 2: Direct symmetric inequality
    intro D hinv
    have hgap := powerVal_involution_gap h₁ h₂ hφ hsub D
    rw [hinv] at hgap
    linarith
  · -- Part 3: Strict converse failure using uniform orbit-averaged distribution
    intro w ⟨hwF₂, r0, hr0⟩ hwnot
    let Dstar := orbitAvgDist r0
    have hinv : ∀ ψ : Equiv.Perm S, ψ • Dstar = Dstar := orbitAvgDist_invariant r0
    have hstrict : powerVal F₁ h₁ Dstar < powerVal F₂ h₂ Dstar := by
      rw [powerVal_orbitAvgDist, powerVal_orbitAvgDist]
      have hcard_pos : (0 : ℝ) < 1 / (Fintype.card (Equiv.Perm S) : ℝ) := by positivity
      apply mul_lt_mul_of_pos_left _ hcard_pos
      suffices h2sum :
          2 * ∑ ψ : Equiv.Perm S, optVal F₁ h₁ (permVec ψ r0) <
            2 * ∑ ψ : Equiv.Perm S, optVal F₂ h₂ (permVec ψ r0) by linarith
      have hreindex : ∀ (g : (S → ℝ) → ℝ),
          ∑ ψ : Equiv.Perm S, g (permVec (φ * ψ) r0) = ∑ ψ : Equiv.Perm S, g (permVec ψ r0) := by
        intro g
        exact Fintype.sum_equiv (Equiv.mulLeft φ) _ _ (fun _ => rfl)
      have hL : 2 * ∑ ψ : Equiv.Perm S, optVal F₁ h₁ (permVec ψ r0) =
          ∑ ψ : Equiv.Perm S, (optVal F₁ h₁ (permVec ψ r0) + optVal F₁ h₁ (permVec (φ * ψ) r0)) := by
        rw [Finset.sum_add_distrib, hreindex (optVal F₁ h₁)]
        ring
      have hR : 2 * ∑ ψ : Equiv.Perm S, optVal F₂ h₂ (permVec ψ r0) =
          ∑ ψ : Equiv.Perm S, (optVal F₂ h₂ (permVec ψ r0) + optVal F₂ h₂ (permVec (φ * ψ) r0)) := by
        rw [Finset.sum_add_distrib, hreindex (optVal F₂ h₂)]
        ring
      rw [hL, hR]
      have hpair_le : ∀ ψ : Equiv.Perm S,
          optVal F₁ h₁ (permVec ψ r0) + optVal F₁ h₁ (permVec (φ * ψ) r0) ≤
            optVal F₂ h₂ (permVec ψ r0) + optVal F₂ h₂ (permVec (φ * ψ) r0) := by
        intro ψ
        have hcomp : permVec (φ * ψ) r0 = permVec φ (permVec ψ r0) := by
          funext s; simp [permVec, Equiv.Perm.mul_apply]
        rw [hcomp]
        have hgap := optVal_involution_gap h₁ h₂ hφ hsub (permVec ψ r0)
        linarith
      have hpair_strict :
          optVal F₁ h₁ (permVec 1 r0) + optVal F₁ h₁ (permVec (φ * 1) r0) <
            optVal F₂ h₂ (permVec 1 r0) + optVal F₂ h₂ (permVec (φ * 1) r0) := by
        have h1 : permVec (1 : Equiv.Perm S) r0 = r0 := by funext s; rfl
        rw [h1, mul_one]
        have hlt1 : optVal F₁ h₁ (permVec φ r0) < optVal F₂ h₂ r0 := by
          have heq : optVal F₁ h₁ (permVec φ r0) =
              optVal (permFinset φ F₁) (permFinset_nonempty φ h₁) r0 := by
            have := optVal_permFinset φ F₁ h₁ (permVec φ r0)
            rw [permVec_involution hφ r0] at this
            exact this.symm
          rw [heq]
          have hsup_lt : optVal (permFinset φ F₁) (permFinset_nonempty φ h₁) r0 < dot w r0 := by
            unfold optVal
            rw [Finset.sup'_lt_iff]
            intro v hv
            exact hr0 v (hsub hv) (fun hvw => hwnot (hvw ▸ hv))
          have hw_le : dot w r0 ≤ optVal F₂ h₂ r0 :=
            Finset.le_sup' (fun v => dot v r0) hwF₂
          linarith
        have hle2 : optVal F₁ h₁ r0 ≤ optVal F₂ h₂ (permVec φ r0) := by
          rw [← optVal_permFinset φ F₁ h₁ r0]
          exact optVal_mono (permFinset_nonempty φ h₁) h₂ hsub (permVec φ r0)
        linarith
      exact Finset.sum_lt_sum (fun ψ _ => hpair_le ψ) ⟨1, Finset.mem_univ 1, hpair_strict⟩
    refine ⟨Dstar, hinv, hstrict, ?_⟩
    intro hconv
    have hDmem : Dstar ∈ distOrbit Dstar := by
      unfold distOrbit
      rw [Finset.mem_image]
      exact ⟨1, Finset.mem_univ 1, one_smul _ _⟩
    have horb_eq : OrbitIn S (distOrbit Dstar) Dstar = {Dstar} := by
      ext D'
      rw [mem_orbitIn_iff, Finset.mem_singleton]
      constructor
      · rintro ⟨⟨ψ, rfl⟩, _⟩
        exact hinv ψ
      · rintro rfl
        exact ⟨⟨1, one_smul _ _⟩, hDmem⟩
    have hcard := hconv Dstar hDmem
    rw [horb_eq] at hcard
    simp only [one_mul, Finset.filter_singleton] at hcard
    have hnotlt : ¬ (powerVal F₂ h₂ Dstar < powerVal F₁ h₁ Dstar) := not_lt.mpr (le_of_lt hstrict)
    simp [hstrict, hnotlt] at hcard

/-! ## Boundary counterexamples (`S2d`, `S2e`, `S2f`) -/

private lemma dot_basisVec {S : Type} [Fintype S] [DecidableEq S] (s : S) (r : S → ℝ) :
    dot (basisVec s) r = r s := by
  unfold dot basisVec
  simp

private noncomputable def pointDist {S : Type} (r0 : S → ℝ) : RewardDist S where
  mass := Finsupp.single r0 1
  nonneg r := by
    classical
    rw [Finsupp.single_apply]
    split_ifs <;> norm_num
  sum_one := by simp

private lemma powerVal_pointDist {S : Type} [Fintype S] (F : Finset (S → ℝ)) (hF : F.Nonempty)
    (r0 : S → ℝ) : powerVal F hF (pointDist r0) = optVal F hF r0 := by
  unfold powerVal pointDist
  simp

/-- Proof of `S2d_CounterexampleDropSymmetry`. -/
public theorem theorem_S2d_CounterexampleDropSymmetry : S2d_CounterexampleDropSymmetry := by
  classical
  have hS : shutOpts.Nonempty := ⟨basisVec 0, by simp [shutOpts]⟩
  have hO : openOpts.Nonempty := ⟨basisVec 1, by simp [openOpts]⟩
  let r0 : Fin 3 → ℝ := basisVec 0
  refine ⟨hS, hO, pointDist r0, ?_⟩
  rw [powerVal_pointDist, powerVal_pointDist]
  have hshut : optVal shutOpts hS r0 = 1 := by
    unfold optVal shutOpts
    simp [dot_basisVec, r0, basisVec]
  have hopen : optVal openOpts hO r0 = 0 := by
    unfold optVal openOpts
    simp [dot_basisVec, r0, basisVec]
  linarith

/-- Proof of `S2e_CounterexampleDropOptimality`. -/
public theorem theorem_S2e_CounterexampleDropOptimality : S2e_CounterexampleDropOptimality := by
  classical
  have hS : shutOpts.Nonempty := ⟨basisVec 0, by simp [shutOpts]⟩
  have hO : openOpts.Nonempty := ⟨basisVec 1, by simp [openOpts]⟩
  let φ : Equiv.Perm (Fin 3) := Equiv.swap 0 1
  have hφ : ∀ s, φ (φ s) = s := fun s => Equiv.swap_apply_self 0 1 s
  have hsub : permFinset φ shutOpts ⊆ openOpts := by
    intro v hv
    rw [mem_permFinset] at hv
    rcases hv with ⟨u, hu, rfl⟩
    simp only [shutOpts, Finset.mem_singleton] at hu
    subst hu
    have hswap2 : φ (2 : Fin 3) = (2 : Fin 3) :=
      Equiv.swap_apply_of_ne_of_ne (by decide) (by decide)
    have heq : permVec φ (basisVec (0 : Fin 3)) = basisVec (1 : Fin 3) := by
      funext s
      fin_cases s <;> simp [permVec, basisVec, φ, hswap2]
    rw [heq]
    simp [openOpts]
  have hw_nd : NonDominated openOpts (basisVec (2 : Fin 3)) := by
    refine ⟨by simp [openOpts], basisVec (2 : Fin 3), ?_⟩
    intro v hv hne
    simp only [openOpts, Finset.mem_insert, Finset.mem_singleton] at hv
    rcases hv with rfl | rfl
    · simp [dot_basisVec, basisVec]
    · exact absurd rfl hne
  have hwnot : basisVec (2 : Fin 3) ∉ permFinset φ shutOpts := by
    rw [mem_permFinset]
    rintro ⟨u, hu, hEq⟩
    simp only [shutOpts, Finset.mem_singleton] at hu
    subst hu
    have h2 := congrFun hEq (2 : Fin 3)
    have hswap2 : φ (2 : Fin 3) = (2 : Fin 3) :=
      Equiv.swap_apply_of_ne_of_ne (by decide) (by decide)
    simp [permVec, basisVec, φ, hswap2] at h2
  have ⟨_, _, hstrict_fn⟩ := theorem_S2c_OptimalPolicyPowerSeeking (Fin 3) shutOpts openOpts hS hO φ hφ hsub
  rcases hstrict_fn (basisVec 2) hw_nd hwnot with ⟨Dstar, hinv, hlt, _⟩
  exact ⟨hS, hO, Dstar, fun _ => false, hinv, hlt, fun _ _ => rfl⟩

/-- Proof of `S2f_CounterexampleDominatedOptions`. -/
public theorem theorem_S2f_CounterexampleDominatedOptions : S2f_CounterexampleDominatedOptions := by
  classical
  let e0 : Fin 2 → ℝ := basisVec 0
  let e1 : Fin 2 → ℝ := basisVec 1
  let mid : Fin 2 → ℝ := fun s => (1 / 2 : ℝ) * e0 s + (1 / 2 : ℝ) * e1 s
  let F₁ : Finset (Fin 2 → ℝ) := {e0, e1}
  let F₂ : Finset (Fin 2 → ℝ) := {e0, e1, mid}
  have h₁ : F₁.Nonempty := ⟨e0, by simp [F₁]⟩
  have h₂ : F₂.Nonempty := ⟨e0, by simp [F₂]⟩
  have hsub : F₁ ⊆ F₂ := by
    intro v hv
    simp only [F₁, F₂, Finset.mem_insert, Finset.mem_singleton] at hv ⊢
    rcases hv with rfl | rfl
    · left; rfl
    · right; left; rfl
  have hne01 : e0 ≠ e1 := by
    intro h
    have := congrFun h 0
    simp [e0, e1, basisVec] at this
  have hne_mid0 : mid ≠ e0 := by
    intro h
    have := congrFun h 0
    simp [mid, e0, e1, basisVec] at this
  have hne_mid1 : mid ≠ e1 := by
    intro h
    have := congrFun h 1
    simp [mid, e0, e1, basisVec] at this
  have hcard : F₁.card < F₂.card := by
    have hc1 : F₁.card = 2 := by
      simp [F₁, Finset.card_pair hne01]
    have hmid_not : mid ∉ F₁ := by
      simp [F₁, hne_mid0, hne_mid1]
    have hF2eq : F₂ = insert mid F₁ := by
      ext v
      simp [F₁, F₂, or_comm, or_left_comm]
    rw [hF2eq, Finset.card_insert_of_notMem hmid_not, hc1]
    omega
  have hopt : ∀ r : Fin 2 → ℝ, optVal F₁ h₁ r = optVal F₂ h₂ r := by
    intro r
    apply le_antisymm
    · exact optVal_mono h₁ h₂ hsub r
    · unfold optVal
      rw [Finset.sup'_le_iff]
      intro v hv
      simp only [F₂, Finset.mem_insert, Finset.mem_singleton] at hv
      rcases hv with rfl | rfl | rfl
      · exact Finset.le_sup' (fun w => dot w r) (by simp [F₁])
      · exact Finset.le_sup' (fun w => dot w r) (by simp [F₁])
      · have h0 : dot e0 r ≤ F₁.sup' h₁ (fun w => dot w r) :=
          Finset.le_sup' (fun w => dot w r) (by simp [F₁])
        have h1 : dot e1 r ≤ F₁.sup' h₁ (fun w => dot w r) :=
          Finset.le_sup' (fun w => dot w r) (by simp [F₁])
        have hmid : dot mid r = (1 / 2 : ℝ) * dot e0 r + (1 / 2 : ℝ) * dot e1 r := by
          unfold dot mid
          simp [Fin.sum_univ_two, e0, e1, basisVec]
        linarith
  refine ⟨F₁, F₂, h₁, h₂, hsub, hcard, hopt, ?_⟩
  intro D
  unfold powerVal
  congr 1
  funext r p
  rw [hopt r]

end PowerSeeking
