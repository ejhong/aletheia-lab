module

public import PowerSeeking.Statement
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.FieldSimp
import Mathlib.Order.ConditionallyCompleteLattice.Basic
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Algebra.BigOperators.Field
import Mathlib.Algebra.Order.Archimedean.Real.Basic

/-!
# Family 1 proofs: Coherence, von Neumann–Morgenstern representation, money pumps, and limits (`S1a`–`S1d`)
-/

namespace PowerSeeking

open scoped BigOperators

/-! ## Lottery algebra helpers -/

private lemma eu_pure {Ω : Type} [Fintype Ω] [DecidableEq Ω] (u : Ω → ℝ) (x : Ω) :
    Lottery.eu u (Lottery.pure x) = u x := by
  unfold Lottery.eu Lottery.pure
  simp

private lemma eu_mix {Ω : Type} [Fintype Ω] (u : Ω → ℝ) (p q : Lottery Ω)
    (α : ℝ) (h0 : 0 ≤ α) (h1 : α ≤ 1) :
    Lottery.eu u (Lottery.mix p q α h0 h1) = α * Lottery.eu u p + (1 - α) * Lottery.eu u q := by
  unfold Lottery.eu Lottery.mix
  simp only [add_mul, mul_assoc, Finset.sum_add_distrib, ← Finset.mul_sum]

private lemma mix_comm {Ω : Type} [Fintype Ω] (p q : Lottery Ω) (α : ℝ) (h0 : 0 ≤ α) (h1 : α ≤ 1) :
    Lottery.mix p q α h0 h1 = Lottery.mix q p (1 - α) (sub_nonneg.mpr h1) (by linarith) := by
  ext x
  simp only [Lottery.mix]
  ring

private lemma mix_zero {Ω : Type} [Fintype Ω] (p q : Lottery Ω) :
    Lottery.mix p q 0 le_rfl zero_le_one = q := by
  ext x
  simp [Lottery.mix]

private lemma mix_one {Ω : Type} [Fintype Ω] (p q : Lottery Ω) :
    Lottery.mix p q 1 zero_le_one le_rfl = p := by
  ext x
  simp [Lottery.mix]

private lemma mix_self {Ω : Type} [Fintype Ω] (p : Lottery Ω) (α : ℝ) (h0 : 0 ≤ α) (h1 : α ≤ 1) :
    Lottery.mix p p α h0 h1 = p := by
  ext x
  simp only [Lottery.mix]
  ring

private lemma mix_mix_same {Ω : Type} [Fintype Ω] (p q : Lottery Ω)
    (α β γ : ℝ) (hα0 : 0 ≤ α) (hα1 : α ≤ 1) (hβ0 : 0 ≤ β) (hβ1 : β ≤ 1)
    (hγ0 : 0 ≤ γ) (hγ1 : γ ≤ 1) :
    Lottery.mix (Lottery.mix p q α hα0 hα1) (Lottery.mix p q β hβ0 hβ1) γ hγ0 hγ1 =
      Lottery.mix p q (γ * α + (1 - γ) * β)
        (by nlinarith) (by nlinarith) := by
  ext x
  simp only [Lottery.mix]
  ring

/-! ## vNM axiom derived lemmas -/

section VNM

variable {Ω : Type} [Fintype Ω] {le : Lottery Ω → Lottery Ω → Prop}

private lemma vnm_refl (h : VNMAxioms le) (p : Lottery Ω) : le p p := by
  rcases h.complete p p with hp | hp <;> exact hp

private lemma vnm_lt_of_not_le (h : VNMAxioms le) {p q : Lottery Ω} (hn : ¬ le q p) :
    StrictPref le p q := by
  rcases h.complete p q with hpq | hqp
  · exact ⟨hpq, hn⟩
  · exact absurd hqp hn

private lemma vnm_lt_of_lt_of_le (h : VNMAxioms le) {p q r : Lottery Ω}
    (hpq : StrictPref le p q) (hqr : le q r) : StrictPref le p r :=
  ⟨h.trans p q r hpq.1 hqr, fun hrp => hpq.2 (h.trans q r p hqr hrp)⟩

private lemma vnm_lt_of_le_of_lt (h : VNMAxioms le) {p q r : Lottery Ω}
    (hpq : le p q) (hqr : StrictPref le q r) : StrictPref le p r :=
  ⟨h.trans p q r hpq hqr.1, fun hrp => hqr.2 (h.trans r p q hrp hpq)⟩

private lemma vnm_indep_right (h : VNMAxioms le) (p q r : Lottery Ω)
    (α : ℝ) (h0 : 0 ≤ α) (h1 : α < 1) :
    le p q ↔ le (Lottery.mix r p α h0 (le_of_lt h1)) (Lottery.mix r q α h0 (le_of_lt h1)) := by
  rw [mix_comm r p α, mix_comm r q α]
  exact h.indep p q r (1 - α) (sub_pos.mpr h1) (by linarith)

private lemma vnm_indep_lt (h : VNMAxioms le) {p q : Lottery Ω} (r : Lottery Ω)
    (α : ℝ) (h0 : 0 < α) (h1 : α ≤ 1) :
    StrictPref le p q ↔
      StrictPref le (Lottery.mix p r α (le_of_lt h0) h1) (Lottery.mix q r α (le_of_lt h0) h1) := by
  unfold StrictPref
  rw [h.indep p q r α h0 h1, h.indep q p r α h0 h1]

private lemma vnm_indep_both (h : VNMAxioms le) {p₁ q₁ p₂ q₂ : Lottery Ω}
    (h1 : le p₁ q₁) (h2 : le p₂ q₂) (α : ℝ) (hα0 : 0 ≤ α) (hα1 : α ≤ 1) :
    le (Lottery.mix p₁ p₂ α hα0 hα1) (Lottery.mix q₁ q₂ α hα0 hα1) := by
  rcases eq_or_lt_of_le hα0 with rfl | hpos
  · simpa [mix_zero] using h2
  · rcases eq_or_lt_of_le hα1 with rfl | hlt1
    · simpa [mix_one] using h1
    · have step1 : le (Lottery.mix p₁ p₂ α hα0 hα1) (Lottery.mix q₁ p₂ α hα0 hα1) :=
        (h.indep p₁ q₁ p₂ α hpos hα1).mp h1
      have step2 : le (Lottery.mix q₁ p₂ α hα0 hα1) (Lottery.mix q₁ q₂ α hα0 hα1) :=
        (vnm_indep_right h p₂ q₂ q₁ α hα0 hlt1).mp h2
      exact h.trans _ _ _ step1 step2

private lemma vnm_mix_strict_mono (h : VNMAxioms le) {b w : Lottery Ω}
    (hbw : StrictPref le b w) {α β : ℝ}
    (hα0 : 0 ≤ α) (hα1 : α ≤ 1) (hβ0 : 0 ≤ β) (hβ1 : β ≤ 1) (hαβ : α < β) :
    StrictPref le (Lottery.mix w b α hα0 hα1) (Lottery.mix w b β hβ0 hβ1) := by
  have hβpos : 0 < β := lt_of_le_of_lt hα0 hαβ
  set t : ℝ := α / β
  have ht0 : 0 ≤ t := div_nonneg hα0 (le_of_lt hβpos)
  have ht1 : t < 1 := (div_lt_one hβpos).mpr hαβ
  have hmid : StrictPref le (Lottery.mix w b t ht0 (le_of_lt ht1)) w := by
    have h1 : StrictPref le (Lottery.mix w b t ht0 (le_of_lt ht1))
        (Lottery.mix w w t ht0 (le_of_lt ht1)) := by
      unfold StrictPref
      rw [← vnm_indep_right h b w w t ht0 ht1, ← vnm_indep_right h w b w t ht0 ht1]
      exact hbw
    simpa [mix_self] using h1
  have hstep := (vnm_indep_lt h b β hβpos hβ1).mp hmid
  have hEq : Lottery.mix (Lottery.mix w b t ht0 (le_of_lt ht1)) b β (le_of_lt hβpos) hβ1 =
      Lottery.mix w b α hα0 hα1 := by
    ext x
    simp only [Lottery.mix]
    have hβne : β ≠ 0 := ne_of_gt hβpos
    have hmul : β * t = α := mul_div_cancel₀ α hβne
    calc
      β * (t * w.prob x + (1 - t) * b.prob x) + (1 - β) * b.prob x
          = (β * t) * w.prob x + (1 - β * t) * b.prob x := by ring
      _ = α * w.prob x + (1 - α) * b.prob x := by rw [hmul]
  rwa [hEq] at hstep

private lemma exists_min_max_pure [DecidableEq Ω] [Nonempty Ω] (h : VNMAxioms le) :
    ∃ xmin xmax : Ω, ∀ x : Ω,
      le (Lottery.pure xmin) (Lottery.pure x) ∧ le (Lottery.pure x) (Lottery.pure xmax) := by
  suffices ∀ (S : Finset Ω), S.Nonempty →
      ∃ xmin ∈ S, ∃ xmax ∈ S, ∀ x ∈ S,
        le (Lottery.pure xmin) (Lottery.pure x) ∧ le (Lottery.pure x) (Lottery.pure xmax) by
    rcases this Finset.univ Finset.univ_nonempty with ⟨xmin, _, xmax, _, hbound⟩
    exact ⟨xmin, xmax, fun x => hbound x (Finset.mem_univ x)⟩
  intro S
  induction S using Finset.induction_on with
  | empty => intro hne; exact absurd hne (by simp)
  | @insert a s ha ih =>
    intro _
    rcases s.eq_empty_or_nonempty with rfl | hs
    · exact ⟨a, by simp, a, by simp, fun x hx => by
        rw [Finset.mem_singleton.mp hx]
        exact ⟨vnm_refl h _, vnm_refl h _⟩⟩
    · rcases ih hs with ⟨xmin, hminS, xmax, hmaxS, hbound⟩
      have hmin_case : ∃ m ∈ insert a s, ∀ x ∈ insert a s, le (Lottery.pure m) (Lottery.pure x) := by
        rcases h.complete (Lottery.pure a) (Lottery.pure xmin) with hax | hxa
        · refine ⟨a, Finset.mem_insert_self a s, fun x hx => ?_⟩
          rcases Finset.mem_insert.mp hx with rfl | hxs
          · exact vnm_refl h _
          · exact h.trans _ _ _ hax (hbound x hxs).1
        · refine ⟨xmin, Finset.mem_insert_of_mem hminS, fun x hx => ?_⟩
          rcases Finset.mem_insert.mp hx with rfl | hxs
          · exact hxa
          · exact (hbound x hxs).1
      have hmax_case : ∃ M ∈ insert a s, ∀ x ∈ insert a s, le (Lottery.pure x) (Lottery.pure M) := by
        rcases h.complete (Lottery.pure xmax) (Lottery.pure a) with hxa | hax
        · refine ⟨a, Finset.mem_insert_self a s, fun x hx => ?_⟩
          rcases Finset.mem_insert.mp hx with rfl | hxs
          · exact vnm_refl h _
          · exact h.trans _ _ _ (hbound x hxs).2 hxa
        · refine ⟨xmax, Finset.mem_insert_of_mem hmaxS, fun x hx => ?_⟩
          rcases Finset.mem_insert.mp hx with rfl | hxs
          · exact hax
          · exact (hbound x hxs).2
      rcases hmin_case with ⟨m, hm, hm_all⟩
      rcases hmax_case with ⟨M, hM, hM_all⟩
      exact ⟨m, hm, M, hM, fun x hx => ⟨hm_all x hx, hM_all x hx⟩⟩

/-- Support-induction decomposition: any property preserved by convex mixtures and holding on
pure lotteries holds on every finite lottery. -/
private lemma lottery_induction [DecidableEq Ω] (P : Lottery Ω → Prop)
    (hpure : ∀ x : Ω, P (Lottery.pure x))
    (hmix : ∀ p q α (h0 : 0 ≤ α) (h1 : α ≤ 1), P p → P q → P (Lottery.mix p q α h0 h1))
    (p : Lottery Ω) : P p := by
  suffices ∀ (S : Finset Ω) (q : Lottery Ω), (∀ x, x ∉ S → q.prob x = 0) → P q from
    this Finset.univ p (fun x hx => absurd (Finset.mem_univ x) hx)
  intro S
  induction S using Finset.induction_on with
  | empty =>
    intro q hq
    have hsum : ∑ x : Ω, q.prob x = 0 :=
      Finset.sum_eq_zero (fun x _ => hq x (Finset.notMem_empty x))
    linarith [q.sum_one]
  | @insert a s ha ih =>
    intro q hq
    have ha0 : 0 ≤ q.prob a := q.nonneg a
    have ha1 : q.prob a ≤ 1 := by
      have hle : q.prob a ≤ ∑ x : Ω, q.prob x :=
        Finset.single_le_sum (fun x _ => q.nonneg x) (Finset.mem_univ a)
      linarith [q.sum_one]
    rcases eq_or_lt_of_le ha0 with hzero | hpos
    · apply ih q
      intro x hxs
      by_cases hxa : x = a
      · subst hxa; exact hzero.symm
      · exact hq x (by simp [hxa, hxs])
    · rcases eq_or_lt_of_le ha1 with hone | hlt1
      · have hqpure : q = Lottery.pure a := by
          ext x
          by_cases hxa : x = a
          · subst hxa; simp [Lottery.pure, hone]
          · simp only [Lottery.pure, hxa, ↓reduceIte]
            have hrem : ∑ y ∈ Finset.univ.erase a, q.prob y = 0 := by
              have hsplit := Finset.add_sum_erase Finset.univ q.prob (Finset.mem_univ a)
              linarith [q.sum_one]
            have hzero_y := (Finset.sum_eq_zero_iff_of_nonneg (fun y _ => q.nonneg y)).mp hrem
            exact hzero_y x (Finset.mem_erase.mpr ⟨hxa, Finset.mem_univ x⟩)
        rw [hqpure]
        exact hpure a
      · have h1m_pos : 0 < 1 - q.prob a := sub_pos.mpr hlt1
        let q' : Lottery Ω := {
          prob := fun x => if x = a then 0 else q.prob x / (1 - q.prob a)
          nonneg := fun x => by
            split_ifs
            · exact le_rfl
            · exact div_nonneg (q.nonneg x) (le_of_lt h1m_pos)
          sum_one := by
            have hsplit : ∑ x : Ω, (if x = a then (0 : ℝ) else q.prob x / (1 - q.prob a)) =
                ∑ x ∈ Finset.univ.erase a, q.prob x / (1 - q.prob a) := by
              rw [← Finset.add_sum_erase _ _ (Finset.mem_univ a)]
              simp only [↓reduceIte, zero_add]
              apply Finset.sum_congr rfl
              intro x hx
              have hxa : x ≠ a := (Finset.mem_erase.mp hx).1
              simp [hxa]
            rw [hsplit, ← Finset.sum_div]
            have hrest : ∑ x ∈ Finset.univ.erase a, q.prob x = 1 - q.prob a := by
              have hs := Finset.add_sum_erase Finset.univ q.prob (Finset.mem_univ a)
              linarith [q.sum_one]
            rw [hrest, div_self (ne_of_gt h1m_pos)]
        }
        have hq'supp : ∀ x, x ∉ s → q'.prob x = 0 := by
          intro x hxs
          dsimp [q']
          split_ifs with hxa
          · rfl
          · rw [hq x (by simp [hxa, hxs]), zero_div]
        have hq_eq : q = Lottery.mix (Lottery.pure a) q' (q.prob a) ha0 ha1 := by
          ext x
          simp only [Lottery.mix, Lottery.pure, q']
          by_cases hxa : x = a
          · subst hxa; simp
          · simp only [hxa, ↓reduceIte, mul_zero, zero_add]
            exact (mul_div_cancel₀ (q.prob x) (ne_of_gt h1m_pos)).symm
        rw [hq_eq]
        exact hmix (Lottery.pure a) q' (q.prob a) ha0 ha1 (hpure a) (ih q' hq'supp)

private lemma affine_eq_eu [DecidableEq Ω] (U : Lottery Ω → ℝ)
    (haff : ∀ p q α (h0 : 0 ≤ α) (h1 : α ≤ 1),
      U (Lottery.mix p q α h0 h1) = α * U p + (1 - α) * U q) (p : Lottery Ω) :
    U p = Lottery.eu (fun x => U (Lottery.pure x)) p := by
  refine lottery_induction (fun q => U q = Lottery.eu (fun x => U (Lottery.pure x)) q) ?_ ?_ p
  · intro x
    rw [eu_pure]
  · intro p₁ p₂ α h0 h1 ih1 ih2
    rw [haff p₁ p₂ α h0 h1, eu_mix, ih1, ih2]

end VNM

/-- Proof of `S1a_VNMRepresentation` (von Neumann & Morgenstern 1944, §3.6 & Appendix). -/
public theorem theorem_S1a_VNMRepresentation : S1a_VNMRepresentation := by
  intro Ω _ _ _ le hvnm
  constructor
  · -- Part 1: Existence of expected-utility representation
    rcases exists_min_max_pure hvnm with ⟨xmin, xmax, hminmax⟩
    let b : Lottery Ω := Lottery.pure xmin
    let w : Lottery Ω := Lottery.pure xmax
    have hbounds : ∀ p : Lottery Ω, le b p ∧ le p w := by
      intro p
      refine lottery_induction (fun q => le b q ∧ le q w) ?_ ?_ p
      · intro x; exact hminmax x
      · intro p₁ p₂ α h0 h1 ⟨hb1, hw1⟩ ⟨hb2, hw2⟩
        constructor
        · have := vnm_indep_both hvnm hb1 hb2 α h0 h1
          rwa [mix_self] at this
        · have := vnm_indep_both hvnm hw1 hw2 α h0 h1
          rwa [mix_self] at this
    by_cases hdeg : le w b
    · -- Degenerate case: all lotteries are indifferent
      refine ⟨fun _ => 0, fun p q => ?_⟩
      simp only [Lottery.eu, mul_zero, Finset.sum_const_zero, le_refl, iff_true]
      exact hvnm.trans p w q (hbounds p).2 (hvnm.trans w b q hdeg (hbounds q).1)
    · -- Non-degenerate case: b ≺ w
      have hbw : StrictPref le b w := ⟨(hbounds w).1, hdeg⟩
      let Sset : Lottery Ω → Set ℝ := fun p =>
        { t : ℝ | ∃ h0 : 0 ≤ t, ∃ h1 : t ≤ 1, le (Lottery.mix w b t h0 h1) p }
      let U : Lottery Ω → ℝ := fun p => sSup (Sset p)
      have hS_ne : ∀ p, (Sset p).Nonempty := by
        intro p
        refine ⟨0, le_rfl, zero_le_one, ?_⟩
        simpa [mix_zero] using (hbounds p).1
      have hS_bdd : ∀ p, BddAbove (Sset p) := by
        intro p
        exact ⟨1, fun t ⟨_, h1, _⟩ => h1⟩
      have hU0 : ∀ p, 0 ≤ U p := by
        intro p
        exact le_csSup (hS_bdd p) ⟨le_rfl, zero_le_one, by simpa [mix_zero] using (hbounds p).1⟩
      have hU1 : ∀ p, U p ≤ 1 := by
        intro p
        exact csSup_le (hS_ne p) (fun t ⟨_, h1, _⟩ => h1)
      have hcalib : ∀ p, Indiff le (Lottery.mix w b (U p) (hU0 p) (hU1 p)) p := by
        intro p
        constructor
        · -- Show mix w b (U p) ≼ p
          by_contra hnot
          have hlt : StrictPref le p (Lottery.mix w b (U p) (hU0 p) (hU1 p)) :=
            vnm_lt_of_not_le hvnm hnot
          by_cases hpb : le p b
          · -- Then no t > 0 is in Sset p, so U p = 0, contradicting p ≺ mix w b 0 = b
            have hle0 : U p ≤ 0 := by
              apply csSup_le (hS_ne p)
              intro t ⟨ht0, ht1, htle⟩
              by_contra htpos
              push Not at htpos
              have hmono := vnm_mix_strict_mono hvnm hbw le_rfl zero_le_one ht0 ht1 htpos
              rw [mix_zero] at hmono
              exact hmono.2 (hvnm.trans _ p _ htle hpb)
            have hUeq : U p = 0 := le_antisymm hle0 (hU0 p)
            have : StrictPref le p b := by
              have hmix0 : Lottery.mix w b (U p) (hU0 p) (hU1 p) = b := by
                ext x; simp [Lottery.mix, hUeq]
              rwa [hmix0] at hlt
            exact this.2 (hbounds p).1
          · have hbp : StrictPref le b p := vnm_lt_of_not_le hvnm hpb
            rcases hvnm.cont b p (Lottery.mix w b (U p) (hU0 p) (hU1 p)) hbp hlt with
              ⟨_, β, _, _, hβ0, hβ1, _, hqlt⟩
            have hUp_pos : 0 < U p := by
              by_contra hUp0
              have hUeq : U p = 0 := le_antisymm (not_lt.mp hUp0) (hU0 p)
              have hmix0 : Lottery.mix w b (U p) (hU0 p) (hU1 p) = b := by
                ext x; simp [Lottery.mix, hUeq]
              rw [hmix0] at hlt
              exact hlt.2 (hbounds p).1
            have hmix_eq : Lottery.mix (Lottery.mix w b (U p) (hU0 p) (hU1 p)) b β
                (le_of_lt hβ0) (le_of_lt hβ1) =
                Lottery.mix w b (β * U p) (by nlinarith) (by nlinarith [hU1 p]) := by
              ext x; simp only [Lottery.mix]; ring
            rw [hmix_eq] at hqlt
            have hub : U p ≤ β * U p := by
              apply csSup_le (hS_ne p)
              intro t ⟨ht0, ht1, htle⟩
              by_contra hgt
              push Not at hgt
              have hmono := vnm_mix_strict_mono hvnm hbw (by nlinarith) (by nlinarith [hU1 p]) ht0 ht1 hgt
              exact (vnm_lt_of_lt_of_le hvnm (vnm_lt_of_lt_of_le hvnm hqlt hmono.1) htle).2 (vnm_refl hvnm p)
            nlinarith
        · -- Show p ≼ mix w b (U p)
          by_contra hnot
          have hlt : StrictPref le (Lottery.mix w b (U p) (hU0 p) (hU1 p)) p :=
            vnm_lt_of_not_le hvnm hnot
          by_cases hwp : le w p
          · -- Then 1 ∈ Sset p, so U p = 1, contradicting mix w b 1 = w ≺ p
            have h1in : (1 : ℝ) ∈ Sset p := ⟨zero_le_one, le_rfl, by simpa [mix_one] using hwp⟩
            have hUeq : U p = 1 := le_antisymm (hU1 p) (le_csSup (hS_bdd p) h1in)
            have hmix1 : Lottery.mix w b (U p) (hU0 p) (hU1 p) = w := by
              ext x; simp [Lottery.mix, hUeq]
            rw [hmix1] at hlt
            exact hlt.2 (hbounds p).2
          · have hpw : StrictPref le p w := vnm_lt_of_not_le hvnm hwp
            rcases hvnm.cont (Lottery.mix w b (U p) (hU0 p) (hU1 p)) p w hlt hpw with
              ⟨α, _, hα0, hα1, _, _, halt, _⟩
            have hU_lt1 : U p < 1 := by
              by_contra hge
              have hUeq : U p = 1 := le_antisymm (hU1 p) (not_lt.mp hge)
              have hmix1 : Lottery.mix w b (U p) (hU0 p) (hU1 p) = w := by
                ext x; simp [Lottery.mix, hUeq]
              rw [hmix1] at hlt
              exact hlt.2 (hbounds p).2
            set t' : ℝ := α + (1 - α) * U p
            have ht'0 : 0 ≤ t' := by nlinarith [hU0 p]
            have ht'1 : t' ≤ 1 := by nlinarith [hU1 p]
            have hmix_eq : Lottery.mix w (Lottery.mix w b (U p) (hU0 p) (hU1 p)) α
                (le_of_lt hα0) (le_of_lt hα1) = Lottery.mix w b t' ht'0 ht'1 := by
              ext x; simp only [Lottery.mix, t']; ring
            rw [hmix_eq] at halt
            have ht'in : t' ∈ Sset p := ⟨ht'0, ht'1, halt.1⟩
            have hle := le_csSup (hS_bdd p) ht'in
            nlinarith
      have hrep : ∀ p q, le p q ↔ U p ≤ U q := by
        intro p q
        constructor
        · intro hpq
          by_contra hgt
          push Not at hgt
          have hmono := vnm_mix_strict_mono hvnm hbw (hU0 q) (hU1 q) (hU0 p) (hU1 p) hgt
          have h1 : le (Lottery.mix w b (U p) (hU0 p) (hU1 p)) (Lottery.mix w b (U q) (hU0 q) (hU1 q)) :=
            hvnm.trans _ p _ (hcalib p).1 (hvnm.trans p q _ hpq (hcalib q).2)
          exact hmono.2 h1
        · intro hle
          rcases eq_or_lt_of_le hle with heq | hlt
          · have hmix_eq : Lottery.mix w b (U p) (hU0 p) (hU1 p) =
                Lottery.mix w b (U q) (hU0 q) (hU1 q) := by
              ext x; simp [Lottery.mix, heq]
            exact hvnm.trans p _ q (hcalib p).2 (hmix_eq ▸ (hcalib q).1)
          · have hmono := vnm_mix_strict_mono hvnm hbw (hU0 p) (hU1 p) (hU0 q) (hU1 q) hlt
            exact hvnm.trans p _ q (hcalib p).2 (hvnm.trans _ _ q hmono.1 (hcalib q).1)
      have haff : ∀ p q α (h0 : 0 ≤ α) (h1 : α ≤ 1),
          U (Lottery.mix p q α h0 h1) = α * U p + (1 - α) * U q := by
        intro p q α h0 h1
        let m_lhs := Lottery.mix (Lottery.mix w b (U p) (hU0 p) (hU1 p))
          (Lottery.mix w b (U q) (hU0 q) (hU1 q)) α h0 h1
        have hle1 : le m_lhs (Lottery.mix p q α h0 h1) :=
          vnm_indep_both hvnm (hcalib p).1 (hcalib q).1 α h0 h1
        have hle2 : le (Lottery.mix p q α h0 h1) m_lhs :=
          vnm_indep_both hvnm (hcalib p).2 (hcalib q).2 α h0 h1
        have hm_eq : m_lhs = Lottery.mix w b (α * U p + (1 - α) * U q)
            (by nlinarith [hU0 p, hU0 q]) (by nlinarith [hU1 p, hU1 q]) :=
          mix_mix_same w b (U p) (U q) α (hU0 p) (hU1 p) (hU0 q) (hU1 q) h0 h1
        have hU_m : U (Lottery.mix w b (α * U p + (1 - α) * U q)
            (by nlinarith [hU0 p, hU0 q]) (by nlinarith [hU1 p, hU1 q])) =
            α * U p + (1 - α) * U q := by
          let t := α * U p + (1 - α) * U q
          have ht0 : 0 ≤ t := by nlinarith [hU0 p, hU0 q]
          have ht1 : t ≤ 1 := by nlinarith [hU1 p, hU1 q]
          let mt := Lottery.mix w b t ht0 ht1
          by_contra hne
          rcases lt_or_gt_of_ne hne with hlt | hgt
          · have hmono := vnm_mix_strict_mono hvnm hbw (hU0 mt) (hU1 mt) ht0 ht1 hlt
            exact hmono.2 (hcalib mt).2
          · have hmono := vnm_mix_strict_mono hvnm hbw ht0 ht1 (hU0 mt) (hU1 mt) hgt
            exact hmono.2 (hcalib mt).1
        have hUeq : U (Lottery.mix p q α h0 h1) = U m_lhs :=
          le_antisymm ((hrep _ _).mp hle2) ((hrep _ _).mp hle1)
        rw [hUeq, hm_eq]
        exact hU_m
      refine ⟨fun x => U (Lottery.pure x), fun p q => ?_⟩
      rw [hrep p q, affine_eq_eu U haff p, affine_eq_eu U haff q]
  · -- Part 2: Positive affine uniqueness
    intro u v hu hv
    have huv : ∀ p q, Lottery.eu u p ≤ Lottery.eu u q ↔ Lottery.eu v p ≤ Lottery.eu v q :=
      fun p q => (hu p q).symm.trans (hv p q)
    by_cases hconst : ∀ x y : Ω, u x = u y
    · obtain ⟨x0⟩ := ‹Nonempty Ω›
      refine ⟨1, v x0 - u x0, zero_lt_one, fun x => ?_⟩
      have hux : u x = u x0 := hconst x x0
      have hvx : v x = v x0 := by
        have h1 : Lottery.eu u (Lottery.pure x) ≤ Lottery.eu u (Lottery.pure x0) := by
          simp [eu_pure, hux]
        have h2 : Lottery.eu u (Lottery.pure x0) ≤ Lottery.eu u (Lottery.pure x) := by
          simp [eu_pure, hux]
        have hv1 := (huv (Lottery.pure x) (Lottery.pure x0)).mp h1
        have hv2 := (huv (Lottery.pure x0) (Lottery.pure x)).mp h2
        simp only [eu_pure] at hv1 hv2
        linarith
      linarith
    · push Not at hconst
      rcases hconst with ⟨x1, x2, hne⟩
      -- Pick a pair with u lo < u hi
      have hex : ∃ lo hi : Ω, u lo < u hi := by
        rcases lt_or_gt_of_ne hne with h | h
        · exact ⟨x1, x2, h⟩
        · exact ⟨x2, x1, h⟩
      rcases hex with ⟨lo, hi, hulo_hi⟩
      have hvlo_hi : v lo < v hi := by
        by_contra hge
        push Not at hge
        have := (huv (Lottery.pure hi) (Lottery.pure lo)).mpr (by simpa [eu_pure] using hge)
        simp only [eu_pure] at this
        linarith
      set a : ℝ := (v hi - v lo) / (u hi - u lo)
      set b : ℝ := v lo - a * u lo
      have ha_pos : 0 < a := div_pos (sub_pos.mpr hvlo_hi) (sub_pos.mpr hulo_hi)
      refine ⟨a, b, ha_pos, fun x => ?_⟩
      -- Use a mixture between {lo, hi, x} depending on where u x sits relative to [u lo, u hi]
      have h_in_interval : ∀ y z t : Ω, u y < u z → u y ≤ u t → u t ≤ u z →
          (v t - v y) * (u z - u y) = (v z - v y) * (u t - u y) := by
        intro y z t hyz hyt htz
        set α : ℝ := (u t - u y) / (u z - u y)
        have hα0 : 0 ≤ α := div_nonneg (sub_nonneg.mpr hyt) (le_of_lt (sub_pos.mpr hyz))
        have hα1 : α ≤ 1 := (div_le_one (sub_pos.mpr hyz)).mpr (by linarith)
        let m := Lottery.mix (Lottery.pure z) (Lottery.pure y) α hα0 hα1
        have heu_u : Lottery.eu u m = u t := by
          rw [eu_mix, eu_pure, eu_pure]
          dsimp [α]
          field_simp [ne_of_gt (sub_pos.mpr hyz)]
          ring
        have h1 : Lottery.eu v (Lottery.pure t) ≤ Lottery.eu v m :=
          (huv (Lottery.pure t) m).mp (by rw [eu_pure, heu_u])
        have h2 : Lottery.eu v m ≤ Lottery.eu v (Lottery.pure t) :=
          (huv m (Lottery.pure t)).mp (by rw [eu_pure, heu_u])
        have heu_v : v t = α * v z + (1 - α) * v y := by
          rw [eu_pure, eu_mix, eu_pure, eu_pure] at h1 h2
          linarith
        have hne_yz : u z - u y ≠ 0 := ne_of_gt (sub_pos.mpr hyz)
        dsimp [α] at heu_v
        field_simp [hne_yz] at heu_v
        linarith
      have hcross : (v x - v lo) * (u hi - u lo) = (v hi - v lo) * (u x - u lo) := by
        by_cases h1 : u x < u lo
        · have h := h_in_interval x hi lo (by linarith) (le_of_lt h1) (le_of_lt hulo_hi)
          linarith
        · push Not at h1
          by_cases h2 : u x ≤ u hi
          · exact h_in_interval lo hi x hulo_hi h1 h2
          · push Not at h2
            have h := h_in_interval lo x hi (by linarith) (le_of_lt hulo_hi) (le_of_lt h2)
            linarith
      have hne_lh : u hi - u lo ≠ 0 := ne_of_gt (sub_pos.mpr hulo_hi)
      dsimp [a, b]
      field_simp [hne_lh]
      linarith

/-! ## Money pumps, incomplete preferences, and history-utility triviality (`S1b`, `S1c`, `S1d`) -/

/-- Proof of `S1b_IntransitiveMoneyPump` (Gustafsson 2022, Ch. 2). -/
public theorem theorem_S1b_IntransitiveMoneyPump : S1b_IntransitiveMoneyPump := by
  intro G base_lt lt a b c hab hbc hca hpay m₀
  rcases hpay a b m₀ hab with ⟨ε₁, hε₁, hstep1⟩
  rcases hpay b c (m₀ - ε₁) hbc with ⟨ε₂, hε₂, hstep2⟩
  rcases hpay c a (m₀ - ε₁ - ε₂) hca with ⟨ε₃, hε₃, hstep3⟩
  refine ⟨m₀ - ε₁ - ε₂ - ε₃, by linarith, ?_⟩
  exact TradeChain.trans hstep1 (TradeChain.trans hstep2 (TradeChain.step hstep3))

/-- Proof of `S1c_IncompleteNoMoneyPump` (Gustafsson 2022 / Thornley 2023). -/
public theorem theorem_S1c_IncompleteNoMoneyPump : S1c_IncompleteNoMoneyPump := by
  constructor
  · -- Part 1: Goods with money (Fin 2 × ℝ)
    let le : (Fin 2 × ℝ) → (Fin 2 × ℝ) → Prop := fun s t => s.1 = t.1 ∧ s.2 ≤ t.2
    have hchain : ∀ s t, TradeChain le s t → le s t := by
      intro s t hc
      induction hc with
      | step h => exact h
      | trans h _ ih => exact ⟨h.1.trans ih.1, h.2.trans ih.2⟩
    refine ⟨le, ?_, ?_, ?_, ?_, ?_⟩
    · intro s; exact ⟨rfl, le_rfl⟩
    · intro s t u hst htu; exact ⟨hst.1.trans htu.1, hst.2.trans htu.2⟩
    · intro g m₁ m₂ hlt
      exact ⟨⟨rfl, le_of_lt hlt⟩, fun h => not_le_of_gt hlt h.2⟩
    · refine ⟨(0, 0), (1, 0), ?_, ?_⟩
      · intro h; exact absurd h.1 (by decide)
      · intro h; exact absurd h.1 (by decide)
    · intro g m₀ m₁ hc
      exact (hchain (g, m₀) (g, m₁) hc).2
  · -- Part 2: Finite lotteries over Fin 3 with Pareto dominance of two utility functions
    let u₁ : Fin 3 → ℝ := fun i => if i = 0 then 1 else 0
    let u₂ : Fin 3 → ℝ := fun i => if i = 1 then 1 else 0
    let le : Lottery (Fin 3) → Lottery (Fin 3) → Prop :=
      fun p q => Lottery.eu u₁ p ≤ Lottery.eu u₁ q ∧ Lottery.eu u₂ p ≤ Lottery.eu u₂ q
    have hstrict_sum : ∀ p q, StrictPref le p q →
        Lottery.eu u₁ p + Lottery.eu u₂ p < Lottery.eu u₁ q + Lottery.eu u₂ q := by
      intro p q ⟨⟨h1, h2⟩, hnot⟩
      by_contra hge
      push Not at hge
      have heq1 : Lottery.eu u₁ p = Lottery.eu u₁ q := by linarith
      have heq2 : Lottery.eu u₂ p = Lottery.eu u₂ q := by linarith
      exact hnot ⟨by linarith, by linarith⟩
    have hchain_lt : ∀ p q, TradeChain (StrictPref le) p q →
        Lottery.eu u₁ p + Lottery.eu u₂ p < Lottery.eu u₁ q + Lottery.eu u₂ q := by
      intro p q hc
      induction hc with
      | step h => exact hstrict_sum _ _ h
      | trans h _ ih => exact lt_trans (hstrict_sum _ _ h) ih
    refine ⟨le, ?_, ?_, ?_, ?_, ?_⟩
    · intro p; exact ⟨le_rfl, le_rfl⟩
    · intro p q r hpq hqr; exact ⟨hpq.1.trans hqr.1, hpq.2.trans hqr.2⟩
    · intro p q r α h0 h1
      simp only [le, eu_mix]
      constructor
      · intro ⟨h1', h2'⟩
        exact ⟨by nlinarith, by nlinarith⟩
      · intro ⟨h1', h2'⟩
        exact ⟨by nlinarith, by nlinarith⟩
    · refine ⟨Lottery.pure 0, Lottery.pure 1, ?_, ?_⟩
      · intro h
        have h2 := h.1
        simp only [eu_pure, u₁] at h2
        norm_num at h2
      · intro h
        have h2 := h.2
        simp only [eu_pure, u₂] at h2
        norm_num at h2
    · intro p hc
      exact lt_irrefl _ (hchain_lt p p hc)

private lemma consistentWith_append_singleton {Obs Act : Type}
    (π : List (Obs × Act) → Obs → Act) (h : List (Obs × Act)) (o : Obs) (a : Act) :
    ConsistentWith π (h ++ [(o, a)]) ↔ ConsistentWith π h ∧ a = π h o := by
  induction h generalizing π with
  | nil =>
    simp [ConsistentWith]
  | cons hd tl ih =>
    rcases hd with ⟨o₀, a₀⟩
    simp only [List.cons_append, ConsistentWith]
    rw [ih (fun h' o' => π ((o₀, a₀) :: h') o')]
    tauto

/-- Proof of `S1d_HistoryUtilityTriviality` (Shah 2018). -/
public theorem theorem_S1d_HistoryUtilityTriviality : S1d_HistoryUtilityTriviality := by
  classical
  intro Obs Act π
  refine ⟨fun h => if ConsistentWith π h then 1 else 0, ?_⟩
  intro h o a hcons hne
  have h1 : ConsistentWith π (h ++ [(o, π h o)]) :=
    (consistentWith_append_singleton π h o (π h o)).mpr ⟨hcons, rfl⟩
  have h2 : ¬ ConsistentWith π (h ++ [(o, a)]) := by
    rw [consistentWith_append_singleton]
    intro ⟨_, ha⟩
    exact hne ha
  simp [h1, h2]

end PowerSeeking
