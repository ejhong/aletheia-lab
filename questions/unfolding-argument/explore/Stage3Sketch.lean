import UnfoldingArgument.Results
import Mathlib.Tactic
import Mathlib.SetTheory.Cardinal.Finite

/-!
Exploratory. The first part repeats the draft statements of Stage 3 (now locked as `lean/UnfoldingArgument/Statement3.lean`);
the second part is trial proofs. Nothing here is a finding.
-/

namespace Unfolding

/-- D19. Every unit of the network has finitely many states, and at most `k` of them. -/
def Network.UnitsHaveAtMost {I O : Type} (N : Network I O) (k : ℕ) : Prop :=
  ∀ n, Finite (N.St n) ∧ Nat.card (N.St n) ≤ k

/-- D20. The counter modulo `m`: one unit holding a number from `0` to `m - 1`, which starts at `0` and
advances by one, wrapping round, each time the input is `true`. The output says whether the number is
`0`. -/
def counter (m : ℕ) [NeZero m] : Network Bool Bool where
  Node := Unit
  fintypeNode := inferInstance
  St := fun _ => Fin m
  init := fun _ => 0
  step := fun _ σ x => if x then σ () + 1 else σ ()
  out := fun σ => decide (σ () = 0)

/-- S3a. A feedback-free network whose units have at most `k` states each, fed any inputs and then one
input `x` over and over, ends up repeating its outputs with period `(k!)^(number of units)`. -/
def FeedbackFreeIsEventuallyPeriodic : Prop :=
  ∀ (I O : Type) (N : Network I O) (k : ℕ), N.FeedbackFree → N.UnitsHaveAtMost k →
    ∀ (ws : List I) (x : I), ∃ t₀ : ℕ, ∀ t : ℕ, t₀ ≤ t →
      N.response (ws ++ List.replicate (t + k.factorial ^ N.size) x)
        = N.response (ws ++ List.replicate t x)

/-- S3b. If a feedback-free network whose units have at most `k` states each behaves as the counter
modulo `m` at every horizon, then `m` divides `(k!)^(number of units)`. -/
def CounterTwinForcesDivisibility : Prop :=
  ∀ (m : ℕ) [NeZero m] (k : ℕ) (N : Network Bool Bool),
    N.FeedbackFree → N.UnitsHaveAtMost k → Network.AgreeAlways N (counter m) →
    m ∣ k.factorial ^ N.size

/-- S3b′. No feedback-free network of two-state units, however many, behaves as the counter modulo 3 at
every horizon. -/
def CounterMod3HasNoBinaryFeedbackFreeTwin : Prop :=
  ¬ ∃ N : Network Bool Bool,
      N.FeedbackFree ∧ N.UnitsHaveAtMost 2 ∧ Network.AgreeAlways N (counter 3)

/-- S3c. Some feedback-free network of three two-state units behaves as the counter modulo 8 at every
horizon. -/
def CounterMod8HasBinaryFeedbackFreeTwin : Prop :=
  ∃ N : Network Bool Bool,
    N.FeedbackFree ∧ N.UnitsHaveAtMost 2 ∧ N.size = 3 ∧ Network.AgreeAlways N (counter 8)

/-- S3d. For `m` at least 2, no loop-free network behaves as the counter modulo `m` at every horizon. -/
def CounterHasNoLoopFreeTwin : Prop :=
  ∀ (m : ℕ) [NeZero m], 2 ≤ m →
    ¬ ∃ N : Network Bool Bool, N.LoopFree ∧ Network.AgreeAlways N (counter m)

/-- S3e. The counter modulo `m` is itself a feedback-free network: one unit, with `m` states. -/
def CounterIsOneUnitWithMemory : Prop :=
  ∀ (m : ℕ) [NeZero m],
    (counter m).FeedbackFree ∧ (counter m).UnitsHaveAtMost m ∧ (counter m).size = 1

end Unfolding

/-!
Exploratory proofs for Stage 3, written before the lock of `Statement3.lean`. Nothing here is a finding.
-/

namespace Unfolding

open Relation

namespace Stage3

variable {I O : Type}

theorem run_snoc (N : Network I O) (xs : List I) (x : I) :
    N.run (xs ++ [x]) = N.next (N.run xs) x := by
  simp [Network.run, List.foldl_append]

/-- If two joint states make node `n` update differently, they differ at a node `n` depends on. -/
theorem exists_dependsOn_of_step_ne (N : Network I O) (n : N.Node) (σ σ' : N.State) (x : I)
    (h : N.step n σ x ≠ N.step n σ' x) : ∃ m, σ m ≠ σ' m ∧ N.DependsOn n m := by
  classical
  by_contra hcon
  push Not at hcon
  apply h
  have key : ∀ s : Finset N.Node,
      N.step n (fun k => if k ∈ s then σ' k else σ k) x = N.step n σ x := by
    intro s
    induction s using Finset.induction_on with
    | empty => simp
    | insert a s ha ih =>
      rw [← ih]
      by_cases hd : σ a = σ' a
      · congr 1
        funext k
        by_cases hk : k = a
        · subst hk; simp [ha, hd]
        · simp [Finset.mem_insert, hk]
      · have hnd := hcon a hd
        by_contra hne
        apply hnd
        refine ⟨_, _, x, ?_, hne⟩
        intro k hk
        simp [Finset.mem_insert, hk]
  have := key Finset.univ
  simp only [Finset.mem_univ, ite_true] at this
  exact this.symm

theorem step_eq_of_agree (N : Network I O) (n : N.Node) (σ σ' : N.State) (x : I)
    (h : ∀ m, N.DependsOn n m → σ m = σ' m) : N.step n σ x = N.step n σ' x := by
  by_contra hne
  obtain ⟨m, hm, hdep⟩ := exists_dependsOn_of_step_ne N n σ σ' x hne
  exact hm (h m hdep)

/-- The number of other nodes that influence `n` along some path. -/
noncomputable def rk (N : Network I O) (n : N.Node) : ℕ := by
  classical
  exact (Finset.univ.filter (fun m => m ≠ n ∧ TransGen N.Influences m n)).card

theorem rk_lt_of_influences (N : Network I O) (hN : N.FeedbackFree) (m n : N.Node)
    (h : N.Influences m n) (hmn : m ≠ n) : rk N m < rk N n := by
  classical
  unfold rk
  apply Finset.card_lt_card
  rw [Finset.ssubset_iff_of_subset]
  · refine ⟨m, ?_, ?_⟩
    · simp [hmn, TransGen.single h]
    · simp
  · intro a
    simp only [Finset.mem_filter, Finset.mem_univ, true_and]
    rintro ⟨ham, hta⟩
    refine ⟨?_, TransGen.tail hta h⟩
    intro han
    subst han
    exact hN m a hmn ⟨TransGen.single h, hta⟩

theorem rk_lt_size (N : Network I O) (n : N.Node) : rk N n < N.size := by
  classical
  unfold rk Network.size
  rw [← Finset.card_univ]
  apply Finset.card_lt_card
  rw [Finset.ssubset_iff_of_subset (Finset.filter_subset _ _)]
  exact ⟨n, Finset.mem_univ _, by simp⟩

theorem mult_period {α : Type} (f : ℕ → α) (t₀ p : ℕ) (h : ∀ t, t₀ ≤ t → f (t + p) = f t) :
    ∀ j t, t₀ ≤ t → f (t + j * p) = f t := by
  intro j
  induction j with
  | zero => intro t _; simp
  | succ j ih =>
    intro t ht
    have : t + (j + 1) * p = (t + j * p) + p := by ring
    rw [this, h _ (by omega), ih t ht]

/-- A trajectory under one repeated input: every node is eventually periodic. -/
theorem node_periodic (N : Network I O) (hN : N.FeedbackFree) (k : ℕ) (hk : N.UnitsHaveAtMost k)
    (x : I) (s : ℕ → N.State) (hs : ∀ t, s (t + 1) = N.next (s t) x) :
    ∀ n, ∃ t₀, ∀ t, t₀ ≤ t → s (t + k.factorial ^ (rk N n + 1)) n = s t n := by
  classical
  intro n
  induction hr : rk N n using Nat.strong_induction_on generalizing n with
  | _ r ih =>
    subst hr
    set K := k.factorial with hK
    set P := K ^ rk N n with hP
    -- the other nodes that `n` depends on are periodic with period `P` from some common time on
    have hlow : ∃ T₀, ∀ m, N.DependsOn n m → m ≠ n → ∀ t, T₀ ≤ t → s (t + P) m = s t m := by
      have hex : ∀ m, N.DependsOn n m → m ≠ n →
          ∃ t₀, ∀ t, t₀ ≤ t → s (t + K ^ (rk N m + 1)) m = s t m :=
        fun m hd hmn => ih (rk N m) (rk_lt_of_influences N hN m n hd hmn) m rfl
      let g : N.Node → ℕ := fun m =>
        if h : N.DependsOn n m ∧ m ≠ n then Classical.choose (hex m h.1 h.2) else 0
      refine ⟨Finset.univ.sup g, ?_⟩
      intro m hd hmn t ht
      have hg : g m ≤ t := le_trans (Finset.le_sup (f := g) (Finset.mem_univ m)) ht
      have hspec := Classical.choose_spec (hex m hd hmn)
      have hgm : g m = Classical.choose (hex m hd hmn) := by
        simp only [g]
        exact dite_eq_left ⟨hd, hmn⟩
      have hlt := rk_lt_of_influences N hN m n hd hmn
      have hpow : P = K ^ (rk N n - (rk N m + 1)) * K ^ (rk N m + 1) := by
        rw [hP, ← pow_add]
        congr 1
        omega
      rw [hpow]
      exact mult_period (fun t => s t m) _ _ (fun t ht => hspec t ht) _ t (by rw [← hgm]; exact hg)
    obtain ⟨T₀, hT₀⟩ := hlow
    -- pigeonhole on the states of `n` at times `T₀ + i * P`
    obtain ⟨hfin, hcard⟩ := hk n
    have := Fintype.ofFinite (N.St n)
    have hcard' : Fintype.card (N.St n) < Fintype.card (Fin (k + 1)) := by
      rw [Fintype.card_fin, ← Nat.card_eq_fintype_card]
      omega
    obtain ⟨i, j, hij, hsame⟩ :=
      Fintype.exists_ne_map_eq_of_card_lt (fun i : Fin (k + 1) => s (T₀ + i.val * P) n) hcard'
    -- order the two indices
    have key : ∀ i j : Fin (k + 1), i.val < j.val → s (T₀ + i.val * P) n = s (T₀ + j.val * P) n →
        ∃ t₀, ∀ t, t₀ ≤ t → s (t + K ^ (rk N n + 1)) n = s t n := by
      intro i j hlt hsame
      set d := (j.val - i.val) * P with hd
      set t₁ := T₀ + i.val * P with ht₁
      have hstart : s (t₁ + d) n = s t₁ n := by
        have : t₁ + d = T₀ + j.val * P := by
          rw [ht₁, hd, Nat.sub_mul]
          have : i.val * P ≤ j.val * P := Nat.mul_le_mul_right _ (le_of_lt hlt)
          omega
        rw [this]
        exact hsame.symm
      have hA : ∀ u, s (t₁ + u + d) n = s (t₁ + u) n := by
        intro u
        induction u with
        | zero => simpa using hstart
        | succ u ihu =>
          have e1 : t₁ + (u + 1) + d = (t₁ + u + d) + 1 := by ring
          have e2 : t₁ + (u + 1) = (t₁ + u) + 1 := by ring
          rw [e1, e2, hs, hs]
          show N.step n (s (t₁ + u + d)) x = N.step n (s (t₁ + u)) x
          apply step_eq_of_agree
          intro m hdep
          by_cases hmn : m = n
          · subst hmn; exact ihu
          · exact mult_period (fun t => s t m) T₀ P (fun t ht => hT₀ m hdep hmn t ht)
              (j.val - i.val) (t₁ + u) (by omega)
      have hper : ∀ t, t₁ ≤ t → s (t + d) n = s t n := by
        intro t ht
        obtain ⟨u, rfl⟩ : ∃ u, t = t₁ + u := ⟨t - t₁, by omega⟩
        exact hA u
      -- `d` divides `K * P`
      have hpos : 0 < j.val - i.val := by omega
      have hle : j.val - i.val ≤ k := by have := j.isLt; omega
      obtain ⟨c, hc⟩ := Nat.dvd_factorial hpos hle
      refine ⟨t₁, fun t ht => ?_⟩
      have : K ^ (rk N n + 1) = c * d := by
        rw [pow_succ, ← hP, hd, hK, hc]
        ring
      rw [this]
      exact mult_period (fun t => s t n) t₁ d hper c t ht
    rcases Nat.lt_or_gt_of_ne (fun h => hij (Fin.ext h)) with hlt | hgt
    · exact key i j hlt hsame
    · exact key j i hgt hsame.symm

theorem all_periodic (N : Network I O) (hN : N.FeedbackFree) (k : ℕ) (hk : N.UnitsHaveAtMost k)
    (x : I) (s : ℕ → N.State) (hs : ∀ t, s (t + 1) = N.next (s t) x) :
    ∃ t₀, ∀ t, t₀ ≤ t → s (t + k.factorial ^ N.size) = s t := by
  classical
  have h := node_periodic N hN k hk x s hs
  let g : N.Node → ℕ := fun n => Classical.choose (h n)
  refine ⟨Finset.univ.sup g, fun t ht => ?_⟩
  funext n
  have hg : g n ≤ t := le_trans (Finset.le_sup (f := g) (Finset.mem_univ n)) ht
  have hspec := Classical.choose_spec (h n)
  have hlt := rk_lt_size N n
  have hpow : k.factorial ^ N.size
      = k.factorial ^ (N.size - (rk N n + 1)) * k.factorial ^ (rk N n + 1) := by
    rw [← pow_add]
    congr 1
    omega
  rw [hpow]
  exact mult_period (fun t => s t n) _ _ (fun t ht => hspec t ht) _ t hg

end Stage3

open Stage3

theorem feedbackFreeIsEventuallyPeriodic : FeedbackFreeIsEventuallyPeriodic := by
  intro I O N k hN hk ws x
  have hs : ∀ t, N.run (ws ++ List.replicate (t + 1) x) = N.next (N.run (ws ++ List.replicate t x)) x := by
    intro t
    rw [List.replicate_succ', ← List.append_assoc, run_snoc]
  obtain ⟨t₀, h⟩ := all_periodic N hN k hk x (fun t => N.run (ws ++ List.replicate t x)) hs
  refine ⟨t₀, fun t ht => ?_⟩
  show N.out _ = N.out _
  rw [h t ht]

/-- The number the counter holds after the inputs `xs`, as an element of `Fin m`. -/
def counterState (m : ℕ) [NeZero m] (xs : List Bool) : Fin m := (counter m).run xs ()

theorem counterState_nil (m : ℕ) [NeZero m] : counterState m [] = 0 := rfl

theorem counterState_snoc (m : ℕ) [NeZero m] (xs : List Bool) (x : Bool) :
    counterState m (xs ++ [x]) = if x then counterState m xs + 1 else counterState m xs := by
  unfold counterState
  rw [run_snoc]
  rfl

theorem counterState_val (m : ℕ) [NeZero m] (xs : List Bool) :
    (counterState m xs).val = xs.count true % m := by
  induction xs using List.reverseRecOn with
  | nil => simp [counterState_nil]
  | append_singleton xs x ih =>
    rw [counterState_snoc]
    cases x
    · simpa using ih
    · simp only [ite_true, Fin.val_add, ih, Fin.val_one', List.count_append,
        List.count_singleton_self]
      rw [← Nat.add_mod]

theorem counter_response (m : ℕ) [NeZero m] (xs : List Bool) :
    (counter m).response xs = decide (xs.count true % m = 0) := by
  show decide (counterState m xs = 0) = _
  rw [← counterState_val m xs]
  apply decide_eq_decide.mpr
  constructor
  · intro h; rw [h]; simp
  · intro h; exact Fin.ext (by simpa using h)

theorem counterTwinForcesDivisibility : CounterTwinForcesDivisibility := by
  intro m _ k N hN hk hagree
  obtain ⟨t₀, h⟩ := feedbackFreeIsEventuallyPeriodic Bool Bool N k hN hk [] true
  have h1 := h (m * t₀) (Nat.le_mul_of_pos_left _ (NeZero.pos m))
  simp only [List.nil_append] at h1
  rw [hagree, hagree, counter_response, counter_response] at h1
  simp only [List.count_replicate_self, Nat.mul_add_mod, Nat.mul_mod_right, decide_true,
    decide_eq_true_eq] at h1
  exact Nat.dvd_of_mod_eq_zero h1

theorem counterMod3HasNoBinaryFeedbackFreeTwin : CounterMod3HasNoBinaryFeedbackFreeTwin := by
  rintro ⟨N, hN, hk, hagree⟩
  have h := counterTwinForcesDivisibility 3 2 N hN hk hagree
  rw [Nat.factorial_two] at h
  have := Nat.Prime.dvd_of_dvd_pow Nat.prime_three h
  omega

/-- The update rule of a ripple counter: three bits, each depending on itself and the lower bits. -/
def rippleStep (i : Fin 3) (σ : Fin 3 → Bool) (x : Bool) : Bool :=
  if i = 0 then xor (σ 0) x
  else if i = 1 then xor (σ 1) (x && σ 0)
  else xor (σ 2) (x && σ 0 && σ 1)

/-- The number held by the three bits. -/
def rippleValue (σ : Fin 3 → Bool) : Fin 8 :=
  (if σ 0 then 1 else 0) + (if σ 1 then 2 else 0) + (if σ 2 then 4 else 0)

/-- A ripple counter modulo 8 made of three two-state units. -/
def ripple : Network Bool Bool where
  Node := Fin 3
  fintypeNode := inferInstance
  St := fun _ => Bool
  init := fun _ => false
  step := rippleStep
  out := fun σ => decide (rippleValue σ = 0)

theorem ripple_step (σ : Fin 3 → Bool) (x : Bool) :
    rippleValue (fun i => rippleStep i σ x) = if x then rippleValue σ + 1 else rippleValue σ := by
  revert σ x
  decide

/-- The three bits after the inputs `xs`, as a plain function. -/
def rippleState (xs : List Bool) : Fin 3 → Bool := ripple.run xs

theorem rippleState_snoc (xs : List Bool) (x : Bool) :
    rippleState (xs ++ [x]) = fun i => rippleStep i (rippleState xs) x := by
  unfold rippleState
  rw [run_snoc]
  rfl

theorem ripple_run (xs : List Bool) : rippleValue (rippleState xs) = counterState 8 xs := by
  induction xs using List.reverseRecOn with
  | nil => rfl
  | append_singleton xs x ih =>
    rw [rippleState_snoc, counterState_snoc, ripple_step, ih]

theorem rippleStep_local (b : Fin 3) (σ σ' : Fin 3 → Bool) (x : Bool)
    (h : ∀ k : Fin 3, k.val ≤ b.val → σ k = σ' k) : rippleStep b σ x = rippleStep b σ' x := by
  fin_cases b
  · simp [rippleStep, h 0 (by simp)]
  · simp [rippleStep, h 0 (by simp), h 1 (by simp)]
  · simp [rippleStep, h 0 (by simp), h 1 (by simp), h 2 (by simp)]

theorem ripple_influences (a b : Fin 3) (h : ripple.Influences a b) : a.val ≤ b.val := by
  obtain ⟨σ, σ', x, hagree, hne⟩ := h
  by_contra hcon
  apply hne
  apply rippleStep_local
  intro k hk
  apply hagree
  intro hka
  rw [hka] at hk
  omega

theorem counterMod8HasBinaryFeedbackFreeTwin : CounterMod8HasBinaryFeedbackFreeTwin := by
  refine ⟨ripple, ?_, ?_, rfl, ?_⟩
  · have key : ∀ a b, TransGen ripple.Influences a b → a.val ≤ b.val := by
      intro a b h
      induction h with
      | single h => exact ripple_influences _ _ h
      | tail _ h ih => exact le_trans ih (ripple_influences _ _ h)
    intro a b hab ⟨h1, h2⟩
    exact hab (Fin.ext (le_antisymm (key _ _ h1) (key _ _ h2)))
  · intro n
    refine ⟨inferInstanceAs (Finite Bool), ?_⟩
    show Nat.card Bool ≤ 2
    simp
  · intro xs
    show decide (rippleValue (rippleState xs) = 0) = decide (counterState 8 xs = 0)
    rw [ripple_run]

theorem counterHasNoLoopFreeTwin : CounterHasNoLoopFreeTwin := by
  intro m _ hm
  rintro ⟨N, hN, hagree⟩
  have h := loopFreeHasFiniteMemory Bool Bool N hN [true] [false] (List.replicate N.size false)
    (by simp)
  rw [hagree, hagree, counter_response, counter_response] at h
  have h1 : 1 % m = 1 := Nat.mod_eq_of_lt (by omega)
  simp [List.count_replicate, h1] at h

theorem counterIsOneUnitWithMemory : CounterIsOneUnitWithMemory := by
  intro m _
  refine ⟨?_, ?_, rfl⟩
  · intro a b hab
    exact absurd rfl hab
  · intro n
    refine ⟨inferInstanceAs (Finite (Fin m)), ?_⟩
    show Nat.card (Fin m) ≤ m
    simp

end Unfolding
