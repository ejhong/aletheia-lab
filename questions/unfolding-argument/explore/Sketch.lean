import UnfoldingArgument.Statement
import Mathlib.Tactic

/-!
Exploratory proofs, written before the lock to make sure no statement is false as written.
Nothing here is a finding. The proofs proper are in `lean/UnfoldingArgument/Results.lean`, after the lock.
-/

namespace Unfolding

open Relation

namespace Network

variable {I O : Type}

theorem run_nil (N : Network I O) : N.run [] = N.init := rfl

theorem run_snoc (N : Network I O) (xs : List I) (x : I) :
    N.run (xs ++ [x]) = N.next (N.run xs) x := by
  simp [run, List.foldl_append]

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

end Network

/-! ### S1a -/

theorem unfold_step_zero {I O : Type} (N : Network I O) (T : ℕ) (a : (N.unfold T).Node)
    (σ : (N.unfold T).State) (x : I) (h : a.1.val = 0) :
    (N.unfold T).step a σ x = N.step a.2 N.init x := by
  show N.step a.2 _ x = _
  congr 1
  funext m
  simp [h]

theorem unfold_step_succ {I O : Type} (N : Network I O) (T : ℕ) (a : (N.unfold T).Node)
    (σ : (N.unfold T).State) (x : I) (h : a.1.val ≠ 0) :
    (N.unfold T).step a σ x = N.step a.2 (fun m => σ (⟨a.1.val - 1, by omega⟩, m)) x := by
  show N.step a.2 (fun m => if h : a.1.val = 0 then N.init m else σ (⟨a.1.val - 1, by omega⟩, m)) x = _
  congr 1
  funext m
  exact dite_eq_right h

theorem unfold_influences {I O : Type} (N : Network I O) (T : ℕ) (a b : (N.unfold T).Node)
    (h : (N.unfold T).Influences a b) : a.1.val + 1 = b.1.val := by
  obtain ⟨σ, σ', x, hagree, hne⟩ := h
  by_contra hcon
  apply hne
  by_cases hb : b.1.val = 0
  · exact (unfold_step_zero N T b σ x hb).trans (unfold_step_zero N T b σ' x hb).symm
  · refine (unfold_step_succ N T b σ x hb).trans (Eq.trans ?_ (unfold_step_succ N T b σ' x hb).symm)
    congr 1
    funext m
    apply hagree
    intro heq
    apply hcon
    have : a.1.val = b.1.val - 1 := by rw [← heq]
    omega

theorem unfold_loopFree {I O : Type} (N : Network I O) (T : ℕ) : (N.unfold T).LoopFree := by
  have key : ∀ a b, TransGen (N.unfold T).Influences a b → a.1.val < b.1.val := by
    intro a b h
    induction h with
    | single h => have := unfold_influences N T _ _ h; omega
    | tail _ h ih => have := unfold_influences N T _ _ h; omega
  intro n hn
  exact lt_irrefl _ (key n n hn)

theorem unfold_run {I O : Type} (N : Network I O) (T : ℕ) (xs : List I) :
    ∀ (k : ℕ) (hk : k < T) (m : N.Node),
      (N.unfold T).run xs (⟨k, hk⟩, m) = N.run (xs.drop (xs.length - (k + 1))) m := by
  induction xs using List.reverseRecOn with
  | nil => intro k hk m; simp [Network.run, Network.unfold]
  | append_singleton xs x ih =>
    intro k hk m
    rw [Network.run_snoc]
    show (N.unfold T).step (⟨k, hk⟩, m) _ x = _
    rcases Nat.eq_zero_or_pos k with rfl | hpos
    · refine (unfold_step_zero N T (⟨0, hk⟩, m) _ x rfl).trans ?_
      have : (xs ++ [x]).drop ((xs ++ [x]).length - (0 + 1)) = [x] := by simp
      rw [this]
      rfl
    · have hk0 : k ≠ 0 := by omega
      refine (unfold_step_succ N T (⟨k, hk⟩, m) _ x hk0).trans ?_
      have hd : (xs ++ [x]).drop ((xs ++ [x]).length - (k + 1))
          = xs.drop (xs.length - (k - 1 + 1)) ++ [x] := by
        have h1 : (xs ++ [x]).length - (k + 1) = xs.length - (k - 1 + 1) := by simp; omega
        rw [h1, List.drop_append_of_le_length (by omega)]
      rw [hd, Network.run_snoc]
      show _ = N.step m _ x
      congr 1
      funext m'
      exact ih (k - 1) (by omega) m'

theorem unfold_out_zero {I O : Type} (N : Network I O) (σ : (N.unfold 0).State) :
    (N.unfold 0).out σ = N.out N.init := rfl

theorem unfold_out_pos {I O : Type} (N : Network I O) (T : ℕ) (hT : T ≠ 0) (σ : (N.unfold T).State) :
    (N.unfold T).out σ = N.out (fun m => σ (⟨T - 1, by omega⟩, m)) := by
  show (if h : T = 0 then _ else _) = _
  simp [hT]

theorem unfoldingAtFiniteHorizon : UnfoldingAtFiniteHorizon := by
  intro I O N T
  refine ⟨unfold_loopFree N T, ?_, ?_⟩
  · intro xs hxs
    show (N.unfold T).out _ = N.out _
    by_cases hT : T = 0
    · subst hT
      have : xs = [] := List.length_eq_zero_iff.mp (by omega)
      subst this
      rfl
    · rw [unfold_out_pos N T hT]
      congr 1
      funext m
      have := unfold_run N T xs (T - 1) (by omega) m
      have h0 : xs.length - (T - 1 + 1) = 0 := by omega
      rw [h0, List.drop_zero] at this
      exact this
  · exact (Fintype.card_prod (Fin T) N.Node).trans (by rw [Fintype.card_fin]; rfl)

/-! ### S1b -/

open Classical in
/-- The delay line with a lookup readout: node `k` holds the input that arrived `k + 1` steps ago. -/
noncomputable def lookup {I O : Type} (f : List I → O) (T : ℕ) : Network I O where
  Node := Fin T
  fintypeNode := inferInstance
  St := fun _ => Option I
  init := fun _ => none
  step := fun k σ x => if h : k.val = 0 then some x else σ ⟨k.val - 1, by omega⟩
  out := fun σ =>
    if h : ∃ xs : List I, xs.length ≤ T ∧ ∀ k : Fin T, σ k = xs.reverse[k.val]? then
      f (Classical.choose h) else f []

theorem lookup_step_zero {I O : Type} (f : List I → O) (T : ℕ) (k : Fin T)
    (σ : (lookup f T).State) (x : I) (h : k.val = 0) :
    ((lookup f T).step k σ x : Option I) = some x := by
  exact dite_eq_left h

theorem lookup_step_succ {I O : Type} (f : List I → O) (T : ℕ) (k : Fin T)
    (σ : (lookup f T).State) (x : I) (h : k.val ≠ 0) :
    ((lookup f T).step k σ x : Option I) = σ ⟨k.val - 1, by omega⟩ := by
  exact dite_eq_right h

theorem lookup_run {I O : Type} (f : List I → O) (T : ℕ) (xs : List I) :
    ∀ k : Fin T, ((lookup f T).run xs k : Option I) = xs.reverse[k.val]? := by
  induction xs using List.reverseRecOn with
  | nil => intro k; rfl
  | append_singleton xs x ih =>
    intro k
    rw [Network.run_snoc]
    show ((lookup f T).step k _ x : Option I) = _
    by_cases hk : k.val = 0
    · refine (lookup_step_zero f T k _ x hk).trans ?_
      show @Eq (Option I) _ _
      rw [List.reverse_append, hk]
      rfl
    · refine (lookup_step_succ f T k _ x hk).trans ?_
      refine (ih _).trans ?_
      obtain ⟨j, hj⟩ : ∃ j, k.val = j + 1 := ⟨k.val - 1, by omega⟩
      show @Eq (Option I) _ _
      rw [List.reverse_append]
      simp only [hj]
      rfl

theorem lookup_influences {I O : Type} (f : List I → O) (T : ℕ) (a b : (lookup f T).Node)
    (h : (lookup f T).Influences a b) : a.val + 1 = b.val := by
  obtain ⟨σ, σ', x, hagree, hne⟩ := h
  by_contra hcon
  apply hne
  by_cases hb : b.val = 0
  · exact (lookup_step_zero f T b σ x hb).trans (lookup_step_zero f T b σ' x hb).symm
  · refine (lookup_step_succ f T b σ x hb).trans (Eq.trans ?_ (lookup_step_succ f T b σ' x hb).symm)
    apply hagree
    intro heq
    apply hcon
    have : a.val = b.val - 1 := by rw [← heq]
    omega

theorem lookup_loopFree {I O : Type} (f : List I → O) (T : ℕ) : (lookup f T).LoopFree := by
  have key : ∀ a b, TransGen (lookup f T).Influences a b → a.val < b.val := by
    intro a b h
    induction h with
    | single h => have := lookup_influences f T _ _ h; omega
    | tail _ h ih => have := lookup_influences f T _ _ h; omega
  intro n hn
  exact lt_irrefl _ (key n n hn)

open Classical in
theorem lookup_out {I O : Type} (f : List I → O) (T : ℕ) (σ : (lookup f T).State)
    (h : ∃ xs : List I, xs.length ≤ T ∧ ∀ k : Fin T, σ k = xs.reverse[k.val]?) :
    (lookup f T).out σ = f (Classical.choose h) := by
  exact dite_eq_left h

theorem lookup_response {I O : Type} (f : List I → O) (T : ℕ) (xs : List I) (hxs : xs.length ≤ T) :
    (lookup f T).response xs = f xs := by
  have hex : ∃ ys : List I, ys.length ≤ T ∧ ∀ k : Fin T, (lookup f T).run xs k = ys.reverse[k.val]? :=
    ⟨xs, hxs, lookup_run f T xs⟩
  show (lookup f T).out ((lookup f T).run xs) = f xs
  rw [lookup_out f T _ hex]
  congr 1
  obtain ⟨hlen, hk⟩ := Classical.choose_spec hex
  have hrev : (Classical.choose hex).reverse = xs.reverse := by
    apply List.ext_getElem?
    intro i
    by_cases hi : i < T
    · exact (hk ⟨i, hi⟩).symm.trans (lookup_run f T xs ⟨i, hi⟩)
    · rw [List.getElem?_eq_none (by simp; omega), List.getElem?_eq_none (by simp; omega)]
  exact List.reverse_injective hrev

theorem everyBehaviourHasLoopFreeRealizer : EveryBehaviourHasLoopFreeRealizer := by
  intro I O f T
  exact ⟨lookup f T, lookup_loopFree f T, Fintype.card_fin T, lookup_response f T⟩

/-! ### S1c -/

/-- The number of nodes that influence `n` along some path. -/
noncomputable def rank {I O : Type} (N : Network I O) (n : N.Node) : ℕ := by
  classical
  exact (Finset.univ.filter (fun m => TransGen N.Influences m n)).card

theorem rank_lt_of_influences {I O : Type} (N : Network I O) (hN : N.LoopFree) (m n : N.Node)
    (h : N.Influences m n) : rank N m < rank N n := by
  classical
  unfold rank
  apply Finset.card_lt_card
  rw [Finset.ssubset_iff_of_subset]
  · refine ⟨m, ?_, ?_⟩
    · simp [TransGen.single h]
    · simp [hN m]
  · intro k
    simp only [Finset.mem_filter, Finset.mem_univ, true_and]
    intro hk
    exact TransGen.tail hk h

theorem rank_lt_size {I O : Type} (N : Network I O) (hN : N.LoopFree) (n : N.Node) :
    rank N n < N.size := by
  classical
  unfold rank Network.size
  rw [← Finset.card_univ]
  apply Finset.card_lt_card
  rw [Finset.ssubset_iff_of_subset (Finset.filter_subset _ _)]
  exact ⟨n, Finset.mem_univ _, by simp [hN n]⟩

theorem run_eq_of_rank_lt {I O : Type} (N : Network I O) (hN : N.LoopFree) (xs ys zs : List I) :
    ∀ n, rank N n < zs.length → N.run (xs ++ zs) n = N.run (ys ++ zs) n := by
  induction zs using List.reverseRecOn with
  | nil => intro n hn; simp at hn
  | append_singleton zs z ih =>
    intro n hn
    rw [← List.append_assoc, ← List.append_assoc, Network.run_snoc, Network.run_snoc]
    by_contra hne
    obtain ⟨m, hm, hdep⟩ := Network.exists_dependsOn_of_step_ne N n _ _ z hne
    have hlt := rank_lt_of_influences N hN m n hdep
    apply hm
    apply ih
    simp at hn
    omega

theorem loopFree_run_eq {I O : Type} (N : Network I O) (hN : N.LoopFree) (xs ys zs : List I)
    (hz : N.size ≤ zs.length) : N.run (xs ++ zs) = N.run (ys ++ zs) := by
  funext n
  exact run_eq_of_rank_lt N hN xs ys zs n (lt_of_lt_of_le (rank_lt_size N hN n) hz)

theorem loopFreeHasFiniteMemory : LoopFreeHasFiniteMemory := by
  intro I O N hN xs ys zs hz
  show N.out _ = N.out _
  rw [loopFree_run_eq N hN xs ys zs hz]

/-! ### S1d, S1e -/

theorem latch_run (xs : List Bool) : latch.run xs () = xs.any id := by
  induction xs using List.reverseRecOn with
  | nil => rfl
  | append_singleton xs x ih =>
    rw [Network.run_snoc]
    show (latch.run xs () || x) = _
    rw [ih]
    simp

theorem latch_response (xs : List Bool) : latch.response xs = xs.any id := latch_run xs

theorem latch_recurrent : latch.Recurrent := by
  refine ⟨(), TransGen.single ?_⟩
  refine ⟨fun _ => false, fun _ => true, false, ?_, ?_⟩
  · intro k hk; exact absurd rfl hk
  · show (false || false) ≠ (true || false)
    decide

theorem latchTwinNeedsHorizonManyNodes : LatchTwinNeedsHorizonManyNodes := by
  intro T N hN hagree
  by_contra hlt
  push Not at hlt
  have hmem := loopFreeHasFiniteMemory Bool Bool N hN [true] [false]
    (List.replicate N.size false) (by simp)
  rw [hagree _ (by simp; omega), hagree _ (by simp; omega), latch_response, latch_response] at hmem
  simp at hmem

theorem latchHasNoLoopFreeTwin : LatchHasNoLoopFreeTwin := by
  refine ⟨latch_recurrent, ?_⟩
  rintro ⟨N, hN, hagree⟩
  have := latchTwinNeedsHorizonManyNodes (N.size + 1) N hN (fun xs _ => hagree xs)
  omega

/-! ### S1f, S1g -/

theorem plasticSystemHasLoopFreeTwin : PlasticSystemHasLoopFreeTwin := by
  intro I O P T
  exact everyBehaviourHasLoopFreeRealizer I O P.response T

theorem perturbedNetworkHasLoopFreeTwin : PerturbedNetworkHasLoopFreeTwin := by
  intro I O P N act T
  exact everyBehaviourHasLoopFreeRealizer (I × P) O (N.perturbedResponse act) T

/-! ### S1h -/

/-- State types of the integrated twin: the hub holds a bit; every other node gets one extra bit. -/
def IntSt {I O : Type} (N : Network I O) : Option N.Node → Type
  | none => Bool
  | some n => N.St n × Bool

/-- The integrated twin: one hub node; every original node copies the hub's bit into its extra bit;
the hub flips according to its own bit and whether all the extra bits are set. The output ignores
all of this. -/
def integrate {I O : Type} (N : Network I O) : Network I O where
  Node := Option N.Node
  fintypeNode := inferInstance
  St := IntSt N
  init := fun o => match o with
    | none => false
    | some n => (N.init n, false)
  step := fun o σ x => match o with
    | none => xor (σ none : Bool) (decide (∀ n, ((σ (some n) : N.St n × Bool)).2 = true))
    | some n => (N.step n (fun m => ((σ (some m) : N.St m × Bool)).1) x, (σ none : Bool))
  out := fun σ => N.out (fun m => ((σ (some m) : N.St m × Bool)).1)

theorem integrate_run {I O : Type} (N : Network I O) (xs : List I) :
    (fun m => (((integrate N).run xs (some m) : N.St m × Bool)).1) = N.run xs := by
  induction xs using List.reverseRecOn with
  | nil => rfl
  | append_singleton xs x ih =>
    rw [Network.run_snoc, Network.run_snoc]
    funext m
    show N.step m (fun m' => (((integrate N).run xs (some m') : N.St m' × Bool)).1) x = _
    rw [ih]
    rfl

theorem integrate_hub_to {I O : Type} [Inhabited I] (N : Network I O) (b : (integrate N).Node) :
    (integrate N).Influences none b := by
  classical
  let σ : (integrate N).State := fun o => match o with
    | none => false
    | some n => (N.init n, true)
  let σ' : (integrate N).State := fun o => match o with
    | none => true
    | some n => (N.init n, true)
  have hagree : ∀ k, k ≠ none → σ k = σ' k := by
    intro k hk
    cases k with
    | none => exact absurd rfl hk
    | some n => rfl
  refine ⟨σ, σ', default, hagree, ?_⟩
  cases b with
  | none =>
    show xor false (decide (∀ n : N.Node, true = true)) ≠ xor true (decide (∀ n : N.Node, true = true))
    simp
  | some n =>
    show (N.step n (fun m => N.init m) default, false) ≠ (N.step n (fun m => N.init m) default, true)
    simp

theorem integrate_to_hub {I O : Type} [Inhabited I] (N : Network I O) (a : (integrate N).Node) :
    (integrate N).Influences a none := by
  classical
  cases a with
  | none => exact integrate_hub_to N none
  | some n =>
    let σ : (integrate N).State := fun o => match o with
      | none => false
      | some m => (N.init m, true)
    let σ' : (integrate N).State := fun o => match o with
      | none => false
      | some m => (N.init m, decide (m ≠ n))
    have hagree : ∀ k, k ≠ some n → σ k = σ' k := by
      intro k hk
      cases k with
      | none => rfl
      | some m =>
        have hmn : m ≠ n := fun h => hk (by rw [h])
        show (N.init m, true) = (N.init m, decide (m ≠ n))
        simp [hmn]
    refine ⟨σ, σ', default, hagree, ?_⟩
    show xor false (decide (∀ m : N.Node, true = true))
       ≠ xor false (decide (∀ m : N.Node, decide (m ≠ n) = true))
    simp

theorem everyNetworkHasIntegratedTwin : EveryNetworkHasIntegratedTwin := by
  intro I O hI N
  obtain ⟨x0⟩ := hI
  haveI : Inhabited I := ⟨x0⟩
  refine ⟨integrate N, ⟨⟨none⟩, ?_⟩, ?_, ?_⟩
  · intro a b
    exact TransGen.tail (TransGen.single (integrate_to_hub N a)) (integrate_hub_to N b)
  · exact Fintype.card_option
  · intro xs
    show N.out _ = N.out _
    rw [integrate_run]

/-! ### S1i -/

/-- The whole network as one unit. -/
def collapse {I O : Type} (N : Network I O) : Network I O where
  Node := Unit
  fintypeNode := inferInstance
  St := fun _ => N.State
  init := fun _ => N.init
  step := fun _ σ x => N.next (σ ()) x
  out := fun σ => N.out (σ ())

theorem collapse_run {I O : Type} (N : Network I O) (xs : List I) :
    (collapse N).run xs () = N.run xs := by
  induction xs using List.reverseRecOn with
  | nil => rfl
  | append_singleton xs x ih =>
    rw [Network.run_snoc, Network.run_snoc]
    show N.next ((collapse N).run xs ()) x = _
    rw [ih]

theorem everyNetworkHasSingleUnitTwin : EveryNetworkHasSingleUnitTwin := by
  intro I O N
  refine ⟨collapse N, rfl, ?_, ?_⟩
  · intro m n hmn
    exact absurd rfl hmn
  · intro xs
    show N.out ((collapse N).run xs ()) = N.out _
    rw [collapse_run]

/-! ### Stage 2 -/

theorem substitutionGivesFalsification : SubstitutionGivesFalsification := by
  intro P D E R t r ⟨S, p, hdisj⟩
  obtain ⟨o, ho, hor⟩ := p.2
  obtain ⟨o', ho', hor'⟩ := (S p).2
  by_cases h : t.inf r ∈ t.pred o
  · refine ⟨o', ⟨_, ho'⟩, hor', ?_⟩
    intro h'
    rw [hor'] at h'
    have : t.inf r ∈ t.predOf p.1 ∩ t.predOf (S p).1 := ⟨⟨o, ho, h⟩, ⟨o', ho', h'⟩⟩
    rw [hdisj] at this
    exact this
  · refine ⟨o, ⟨_, ho⟩, hor, ?_⟩
    intro h'
    rw [hor] at h'
    exact h h'

theorem universalSubstitutionFalsifiesEveryReport : UniversalSubstitutionFalsifiesEveryReport := by
  intro P D E R t hU r hr
  exact substitutionGivesFalsification P D E R t r (hU r hr)

theorem everyInferenceWrongOrTheoryWrong : EveryInferenceWrongOrTheoryWrong := by
  intro P D E R t hU truth
  by_cases h : ∃ p, ∃ o ∈ t.obs p, truth p ∉ t.pred o
  · exact Or.inr h
  · left
    push Not at h
    intro r hr
    obtain ⟨o, ⟨p, hop⟩, hor, hf⟩ := universalSubstitutionFalsifiesEveryReport P D E R t hU r hr
    refine ⟨p, o, hop, hor, ?_⟩
    intro heq
    apply hf
    rw [hor, heq]
    exact h p o hop

theorem strictDependenceLeavesNothingToTest : StrictDependenceLeavesNothingToTest := by
  intro D Ic Rc E ic rc pred inf O Obar hsub hrep ⟨f, hf⟩
  constructor
  · rintro ⟨o, ho, hfal⟩
    obtain ⟨o', ho', hr⟩ := hrep o ho
    refine ⟨o', ho', ?_⟩
    rw [hf o' (hsub ho'), hr, ← hf o ho]
    exact hfal
  · rintro ⟨o, ho, hfal⟩
    exact ⟨o, hsub ho, hfal⟩

theorem strictDependenceCanStillBeTested : StrictDependenceCanStillBeTested := by
  refine ⟨Bool, Bool, Bool, Bool, id, id, fun _ => {true}, id, {true}, Set.univ, ?_, ⟨id, ?_⟩, ?_, ?_⟩
  · exact Set.subset_univ _
  · intro o _; rfl
  · rintro ⟨o, ho, h⟩
    apply h
    simp only [Set.mem_singleton_iff] at ho
    simp [ho]
  · exact ⟨false, Set.mem_univ _, by simp⟩

theorem unfoldingArgumentAtFiniteHorizon : UnfoldingArgumentAtFiniteHorizon := by
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

theorem foldingArgumentAtEveryHorizon : FoldingArgumentAtEveryHorizon := by
  intro I O hI conscious hint ⟨N, hN⟩ inf
  obtain ⟨N', hN', _, hagree⟩ := everyNetworkHasIntegratedTwin I O hI N
  have hb : N'.response = N.response := funext hagree
  by_cases h : inf N.response
  · exact ⟨N, fun hiff => hN (hiff.mpr h)⟩
  · refine ⟨N', ?_⟩
    rw [hb]
    intro hiff
    exact h (hiff.mp (hint N' hN'))

theorem loopFreeExclusionSurvivesUnboundedHorizon : LoopFreeExclusionSurvivesUnboundedHorizon := by
  refine ⟨fun N => ¬ ∃ N' : Network Bool Bool, N'.LoopFree ∧ Network.AgreeAlways N' N,
    fun b => ¬ ∃ N' : Network Bool Bool, N'.LoopFree ∧ ∀ xs, N'.response xs = b xs, ?_, ?_, ?_⟩
  · intro N hN h
    exact h ⟨N, hN, fun _ => rfl⟩
  · exact ⟨latch, latchHasNoLoopFreeTwin.2⟩
  · intro N
    exact Iff.rfl

theorem sparedIffDeterminedByBehaviour : SparedIffDeterminedByBehaviour.{u, v, w} := by
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

theorem furtherEvidenceRemovesMismatch : FurtherEvidenceRemovesMismatch.{u, v, w} := by
  intro Sys Beh E beh pred
  exact ⟨E, pred, fun bx => bx.2, fun _ => rfl⟩

end Unfolding
