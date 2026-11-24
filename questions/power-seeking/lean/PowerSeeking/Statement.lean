module

public import Mathlib.Basic.Real.Basic
public import Mathlib.Data.Finset.Basic
public import Mathlib.Data.Finset.Card
public import Mathlib.Data.Finset.Lattice.Fold
public import Mathlib.Algebra.BigOperators.Group.Finset.Basic
public import Mathlib.Data.Fintype.Perm
public import Mathlib.Data.Finsupp.Basic
public import Mathlib.GroupTheory.GroupAction.Defs

/-!
# Power-seeking, coherence, and the shutdown problem: definitions and statements

Every claim is a `def … : Prop`. Nothing here is proved; proofs live in `Coherence.lean`,
`PowerSeeking.lean`, and `Shutdown.lean`. This file is locked (`protocol.lock`) before any proof
or result is committed and is never edited after locking.

Primary sources (exact locators in `protocol.md` and `MANIFEST.md`):
- von Neumann & Morgenstern (1944), *Theory of Games and Economic Behavior*, §3.6 & Appendix.
- Gustafsson (2022), *Money-Pump Arguments*, Cambridge University Press (`doi:10.1017/9781108754750`).
- Shah (2018), "Coherence arguments do not imply goal-directed behavior".
- Turner, Smith, Shah, Critch & Tadepalli (2021), "Optimal Policies Tend to Seek Power", NeurIPS / `arXiv:1912.01683`, Defs. 5.2, 6.1–6.5, Prop. 6.6, Thm. 6.13.
- Turner & Tadepalli (2022), "Parametrically Retargetable Decision-Makers Tend To Seek Power", NeurIPS / `arXiv:2206.13477`, Defs. 3.1–3.5, Prop. 3.4, Thm. 3.6.
- Soares, Fallenstein, Yudkowsky & Armstrong (2015), "Corrigibility", AAAI Workshop, Thms. 1–2 & §3.
- Thornley (2024), "The shutdown problem: an AI engineering puzzle for decision theorists", *Philosophical Studies* 182 (`doi:10.1007/s11098-024-02153-3`), Thms. 1–2 & incomplete-preference discussion.
-/

@[expose] public section

namespace PowerSeeking

open scoped BigOperators

/-! ## Family 1: Coherence, Utility Representation, and Money Pumps -/

/-- D1. A finite lottery (probability distribution) over a finite outcome set `Ω`. -/
@[ext]
structure Lottery (Ω : Type) [Fintype Ω] where
  /-- probability assigned to each outcome -/
  prob : Ω → ℝ
  /-- every probability is nonnegative -/
  nonneg : ∀ x, 0 ≤ prob x
  /-- probabilities sum to 1 -/
  sum_one : ∑ x, prob x = 1

namespace Lottery

variable {Ω : Type} [Fintype Ω]

/-- Convex mixture `α p + (1 - α) q` of two lotteries for `0 ≤ α ≤ 1`. -/
noncomputable def mix (p q : Lottery Ω) (α : ℝ) (h0 : 0 ≤ α) (h1 : α ≤ 1) : Lottery Ω where
  prob x := α * p.prob x + (1 - α) * q.prob x
  nonneg x := add_nonneg (mul_nonneg h0 (p.nonneg x)) (mul_nonneg (sub_nonneg.mpr h1) (q.nonneg x))
  sum_one := by
    simp only [Finset.sum_add_distrib, ← Finset.mul_sum, p.sum_one, q.sum_one, mul_one,
      add_sub_cancel]

/-- Degenerate (point-mass) lottery putting probability 1 on outcome `x`. -/
noncomputable def pure [DecidableEq Ω] (x : Ω) : Lottery Ω where
  prob y := if y = x then 1 else 0
  nonneg y := by
    split_ifs
    · exact zero_le_one
    · exact le_rfl
  sum_one := by simp

/-- Expected utility of lottery `p` under utility function `u : Ω → ℝ`. -/
def eu (u : Ω → ℝ) (p : Lottery Ω) : ℝ := ∑ x, p.prob x * u x

end Lottery

/-- Strict part of a weak preference relation `le`. -/
def StrictPref {α : Type} (le : α → α → Prop) (x y : α) : Prop :=
  le x y ∧ ¬ le y x

/-- Indifference part of a weak preference relation `le`. -/
def Indiff {α : Type} (le : α → α → Prop) (x y : α) : Prop :=
  le x y ∧ le y x

/-- D2. The four von Neumann–Morgenstern axioms on a weak preference relation `le` over finite lotteries:
Completeness, Transitivity, Independence, and Archimedean Continuity (vNM 1944, §3.6). -/
structure VNMAxioms {Ω : Type} [Fintype Ω] (le : Lottery Ω → Lottery Ω → Prop) : Prop where
  /-- Every pair of lotteries is comparable. -/
  complete : ∀ p q, le p q ∨ le q p
  /-- Weak preference is transitive. -/
  trans : ∀ p q r, le p q → le q r → le p r
  /-- Mixing with a third lottery `r` at weight `α ∈ (0, 1]` preserves and reflects preference. -/
  indep : ∀ p q r (α : ℝ) (h0 : 0 < α) (h1 : α ≤ 1),
    le p q ↔ le (Lottery.mix p r α (le_of_lt h0) h1) (Lottery.mix q r α (le_of_lt h0) h1)
  /-- Archimedean continuity: if `p ≺ q ≺ r`, some mixture of `r` and `p` is strictly worse than `q`
  and another is strictly better than `q`. -/
  cont : ∀ p q r, StrictPref le p q → StrictPref le q r →
    ∃ (α β : ℝ) (hα0 : 0 < α) (hα1 : α < 1) (hβ0 : 0 < β) (hβ1 : β < 1),
      StrictPref le (Lottery.mix r p α (le_of_lt hα0) (le_of_lt hα1)) q ∧
      StrictPref le q (Lottery.mix r p β (le_of_lt hβ0) (le_of_lt hβ1))

/-- S1a (von Neumann–Morgenstern Representation & Positive Affine Uniqueness).
Any weak preference relation over finite lotteries satisfying the four vNM axioms is represented by
an expected-utility function `u : Ω → ℝ`, unique up to positive affine transformation `v = a · u + b` (`a > 0`). -/
def S1a_VNMRepresentation : Prop :=
  ∀ (Ω : Type) [Fintype Ω] [DecidableEq Ω] [Nonempty Ω]
    (le : Lottery Ω → Lottery Ω → Prop),
    VNMAxioms le →
    (∃ u : Ω → ℝ, ∀ p q, le p q ↔ Lottery.eu u p ≤ Lottery.eu u q) ∧
    (∀ u v : Ω → ℝ,
      (∀ p q, le p q ↔ Lottery.eu u p ≤ Lottery.eu u q) →
      (∀ p q, le p q ↔ Lottery.eu v p ≤ Lottery.eu v q) →
      ∃ a b : ℝ, 0 < a ∧ ∀ x, v x = a * u x + b)

/-- D3. A finite chain of trades, each step satisfying relation `R`, starting at `s` and ending at `t`. -/
inductive TradeChain {α : Type} (R : α → α → Prop) : α → α → Prop
  | step {x y : α} : R x y → TradeChain R x y
  | trans {x y z : α} : R x y → TradeChain R y z → TradeChain R x z

/-- S1b (Intransitive Money Pump; Gustafsson 2022, Ch. 2).
If an agent has a strict 3-cycle `a ≺ b ≺ c ≺ a` over goods and every strict preference over goods
survives a small monetary payment `ε > 0`, then from any wealth `m₀` there is a finite sequence of
strictly preferred trades returning to the same good `a` with strictly less money (`m₁ < m₀`). -/
def S1b_IntransitiveMoneyPump : Prop :=
  ∀ (G : Type) (base_lt : G → G → Prop) (lt : (G × ℝ) → (G × ℝ) → Prop) (a b c : G),
    base_lt a b → base_lt b c → base_lt c a →
    (∀ x y (m : ℝ), base_lt x y → ∃ ε : ℝ, 0 < ε ∧ lt (x, m) (y, m - ε)) →
    ∀ m₀ : ℝ, ∃ m₁ : ℝ, m₁ < m₀ ∧ TradeChain lt (a, m₀) (a, m₁)

/-- S1c (Incomplete Preferences Cannot Be Money-Pumped; Gustafsson 2022 / Thornley 2023).
Part 1 (goods with money): there exists a reflexive, transitive, money-monotone, INCOMPLETE preference
relation over `Fin 2 × ℝ` for which no finite chain of weakly (or strictly) preferred trades can return
an agent to the same good with strictly less money.
Part 2 (finite lotteries): there exists a reflexive, transitive, independent, INCOMPLETE preference
relation over `Lottery (Fin 3)` (Pareto dominance of two utility functions) with no finite strict cycle. -/
def S1c_IncompleteNoMoneyPump : Prop :=
  (∃ le : (Fin 2 × ℝ) → (Fin 2 × ℝ) → Prop,
    (∀ s, le s s) ∧
    (∀ s t u, le s t → le t u → le s u) ∧
    (∀ g m₁ m₂, m₁ < m₂ → StrictPref le (g, m₁) (g, m₂)) ∧
    (∃ s t, ¬ le s t ∧ ¬ le t s) ∧
    (∀ g m₀ m₁, TradeChain le (g, m₀) (g, m₁) → m₀ ≤ m₁)) ∧
  (∃ le : Lottery (Fin 3) → Lottery (Fin 3) → Prop,
    (∀ p, le p p) ∧
    (∀ p q r, le p q → le q r → le p r) ∧
    (∀ p q r (α : ℝ) (h0 : 0 < α) (h1 : α ≤ 1),
      le p q ↔ le (Lottery.mix p r α (le_of_lt h0) h1) (Lottery.mix q r α (le_of_lt h0) h1)) ∧
    (∃ p q, ¬ le p q ∧ ¬ le q p) ∧
    (∀ p, ¬ TradeChain (StrictPref le) p p))

/-- D4. A history `h` (sequence of observation–action pairs) is consistent with deterministic policy `π`. -/
def ConsistentWith {Obs Act : Type} (π : List (Obs × Act) → Obs → Act) : List (Obs × Act) → Prop
  | [] => True
  | (o, a) :: rest =>
      a = π [] o ∧ ConsistentWith (fun h' o' => π ((o, a) :: h') o') rest

/-- S1d (History-Utility Triviality; Shah 2018).
For EVERY deterministic policy `π` over finite histories, there exists a utility function `U` over
histories such that at every history `h` consistent with `π` and every observation `o`, the action
`π h o` strictly maximizes `U` over all alternative actions `a ≠ π h o`. -/
def S1d_HistoryUtilityTriviality : Prop :=
  ∀ (Obs Act : Type) (π : List (Obs × Act) → Obs → Act),
    ∃ U : List (Obs × Act) → ℝ,
      ∀ (h : List (Obs × Act)) (o : Obs) (a : Act),
        ConsistentWith π h → a ≠ π h o →
        U (h ++ [(o, a)]) < U (h ++ [(o, π h o)])

/-! ## Family 2: Parametric Retargetability and Optimal-Policy Power-Seeking -/

/-- D5. Orbit of parameter `θ` under the symmetric group `Equiv.Perm ι`, restricted to subset `S_Θ`
(Turner & Tadepalli 2022, Def. 3.1). -/
noncomputable def OrbitIn (ι : Type) {Θ : Type} [Fintype ι] [DecidableEq ι] [MulAction (Equiv.Perm ι) Θ]
    (S_Θ : Finset Θ) (θ : Θ) : Finset Θ :=
  letI := Classical.decEq Θ
  (Finset.univ.image (fun φ : Equiv.Perm ι => φ • θ)).filter (fun θ' => θ' ∈ S_Θ)

/-- D6. Orbit-level inequality `fB ≥_n^most fA` on `S_Θ`: in every orbit inside `S_Θ`, at least `n` times
as many elements strictly favour `B` over `A` as strictly favour `A` over `B` (Turner & Tadepalli 2022, Def. 3.2;
Turner et al. 2021, Def. 6.5 is the case `n = 1`). -/
noncomputable def OrbitAtLeast (ι : Type) {Θ : Type} [Fintype ι] [DecidableEq ι]
    [MulAction (Equiv.Perm ι) Θ] (n : ℕ) (S_Θ : Finset Θ) (fA fB : Θ → ℝ) : Prop :=
  letI := Classical.decPred (fun θ' : Θ => fA θ' < fB θ')
  letI := Classical.decPred (fun θ' : Θ => fB θ' < fA θ')
  ∀ θ ∈ S_Θ,
    n * ((OrbitIn ι S_Θ θ).filter (fun θ' => fB θ' < fA θ')).card ≤
      ((OrbitIn ι S_Θ θ).filter (fun θ' => fA θ' < fB θ')).card

/-- D7. Simply `(S_Θ, A → B)`-retargetable decision function (Turner & Tadepalli 2022, Def. 3.3). -/
def SimplyRetargetable (ι : Type) {Θ : Type} [MulAction (Equiv.Perm ι) Θ]
    (S_Θ : Finset Θ) (fA fB : Θ → ℝ) : Prop :=
  ∃ φ : Equiv.Perm ι, ∀ θ ∈ S_Θ, fB θ < fA θ → φ • θ ∈ S_Θ ∧ fA (φ • θ) < fB (φ • θ)

/-- S2a (Simple Retargetability Implies Orbit-Level Tendency; Turner & Tadepalli 2022, Prop. 3.4). -/
def S2a_SimpleRetargetability : Prop :=
  ∀ (ι Θ : Type) [Fintype ι] [DecidableEq ι] [MulAction (Equiv.Perm ι) Θ]
    (S_Θ : Finset Θ) (fA fB : Θ → ℝ),
    SimplyRetargetable ι S_Θ fA fB → OrbitAtLeast ι 1 S_Θ fA fB

/-- D8. `n`-fold multiply retargetable function (Turner & Tadepalli 2022, Def. 3.5). -/
def MultiplyRetargetable (ι : Type) {Θ : Type} [Fintype ι] [DecidableEq ι]
    [MulAction (Equiv.Perm ι) Θ] (n : ℕ) (S_Θ : Finset Θ) (fA fB : Θ → ℝ) : Prop :=
  ∀ θ ∈ S_Θ, ∃ φ : Fin n → Equiv.Perm ι,
    (∀ i, ∀ θ' ∈ OrbitIn ι S_Θ θ, fB θ' < fA θ' →
      φ i • θ' ∈ S_Θ ∧ fA (φ i • θ') < fB (φ i • θ')) ∧
    (∀ i j, i ≠ j → ∀ θ₁ ∈ OrbitIn ι S_Θ θ, fB θ₁ < fA θ₁ →
      ∀ θ₂ ∈ OrbitIn ι S_Θ θ, fB θ₂ < fA θ₂ → φ i • θ₁ ≠ φ j • θ₂)

/-- S2b (Multiply Retargetable Functions Have `n`-Fold Orbit Tendencies; Turner & Tadepalli 2022, Thm. 3.6). -/
def S2b_MultiplyRetargetable : Prop :=
  ∀ (ι Θ : Type) [Fintype ι] [DecidableEq ι] [MulAction (Equiv.Perm ι) Θ]
    (n : ℕ) (S_Θ : Finset Θ) (fA fB : Θ → ℝ),
    MultiplyRetargetable ι n S_Θ fA fB → OrbitAtLeast ι n S_Θ fA fB

/-- D9. Action of state permutations `φ : Equiv.Perm S` on state vectors `v : S → ℝ`:
`(permVec φ v) s = v (φ⁻¹ s)` (row permutation matrix `P_φ`, Turner et al. 2021, Def. 6.1). -/
def permVec {S : Type} (φ : Equiv.Perm S) (v : S → ℝ) : S → ℝ :=
  fun s => v (φ⁻¹ s)

/-- Pushforward of a finite set of state-visitation vectors under state permutation `φ`. -/
noncomputable def permFinset {S : Type} (φ : Equiv.Perm S) (F : Finset (S → ℝ)) : Finset (S → ℝ) :=
  letI := Classical.decEq (S → ℝ)
  F.image (permVec φ)

/-- Inner product `⟨v, r⟩ = ∑ s, v s * r s` over finite state space `S`. -/
def dot {S : Type} [Fintype S] (v r : S → ℝ) : ℝ := ∑ s, v s * r s

/-- Optimal value `V*(F, r) = max_{v ∈ F} ⟨v, r⟩` over a nonempty finite option set `F` of
discounted state-visitation vectors or recurrent state distributions (Turner et al. 2021, §5–6). -/
noncomputable def optVal {S : Type} [Fintype S] (F : Finset (S → ℝ)) (hF : F.Nonempty)
    (r : S → ℝ) : ℝ :=
  F.sup' hF (fun v => dot v r)

/-- D10. Finite discrete reward distribution over `S → ℝ` (with nonnegative weights summing to 1). -/
@[ext]
structure RewardDist (S : Type) where
  /-- probability mass function with finite support -/
  mass : (S → ℝ) →₀ ℝ
  /-- nonnegative probabilities -/
  nonneg : ∀ r, 0 ≤ mass r
  /-- total probability is 1 -/
  sum_one : mass.sum (fun _ p => p) = 1

/-- Equivalence on state vectors induced by a state permutation `φ`. -/
def permVecEquiv {S : Type} (φ : Equiv.Perm S) : (S → ℝ) ≃ (S → ℝ) where
  toFun := permVec φ
  invFun := permVec φ⁻¹
  left_inv v := by funext s; simp [permVec]
  right_inv v := by funext s; simp [permVec]

/-- Pushforward reward distribution `φ • D` under state permutation `φ` (Turner et al. 2021, Def. 6.3). -/
noncomputable def pushRewardDist {S : Type} (φ : Equiv.Perm S) (D : RewardDist S) : RewardDist S where
  mass := D.mass.equivMapDomain (permVecEquiv φ)
  nonneg r := by
    rw [Finsupp.equivMapDomain_apply]
    exact D.nonneg _
  sum_one := by
    rw [Finsupp.equivMapDomain_eq_mapDomain,
      Finsupp.sum_mapDomain_index (fun _ => rfl) (fun _ _ _ => rfl)]
    exact D.sum_one

/-- `RewardDist S` carries a group action by state permutations `Equiv.Perm S`. -/
noncomputable instance instMulActionRewardDist {S : Type} :
    MulAction (Equiv.Perm S) (RewardDist S) where
  smul := pushRewardDist
  one_smul D := by
    ext r
    change (D.mass.equivMapDomain (permVecEquiv 1)) r = D.mass r
    rw [Finsupp.equivMapDomain_apply]
    congr 1
  mul_smul φ ψ D := by
    ext r
    change (D.mass.equivMapDomain (permVecEquiv (φ * ψ))) r =
      ((D.mass.equivMapDomain (permVecEquiv ψ)).equivMapDomain (permVecEquiv φ)) r
    rw [Finsupp.equivMapDomain_apply, Finsupp.equivMapDomain_apply, Finsupp.equivMapDomain_apply]
    congr 1

/-- D11. Average optimal value (`POWER`) of option set `F` under reward distribution `D`
(Turner et al. 2021, Def. 5.2 / Lemma E.51). -/
noncomputable def powerVal {S : Type} [Fintype S] (F : Finset (S → ℝ)) (hF : F.Nonempty)
    (D : RewardDist S) : ℝ :=
  D.mass.sum (fun r p => p * optVal F hF r)

/-- Non-dominated vector in option set `F`: strictly maximizes some reward function `r` over `F`
(Turner et al. 2021, Def. 6.10 / §3). -/
def NonDominated {S : Type} [Fintype S] (F : Finset (S → ℝ)) (w : S → ℝ) : Prop :=
  w ∈ F ∧ ∃ r : S → ℝ, ∀ v ∈ F, v ≠ w → dot v r < dot w r

/-- Finite orbit of a single reward distribution `D` under `Equiv.Perm S` (Turner et al. 2021, Def. 6.4). -/
noncomputable def distOrbit {S : Type} [Fintype S] [DecidableEq S]
    (D : RewardDist S) : Finset (RewardDist S) :=
  letI := Classical.decEq (RewardDist S)
  Finset.univ.image (fun φ : Equiv.Perm S => φ • D)

/-- S2c (Optimal-Policy Power-Seeking Theorem; Turner et al. 2021, Prop. 6.6 & Lemma E.24 core).
Suppose option set `F₂` contains a copy of `F₁` via an involution `φ` (`φ ∘ φ = id`, `φ • F₁ ⊆ F₂`).
Then:
1. (Orbit tendency, Prop. 6.6) For every finite reward distribution `D`, at least as many orbit elements
   `D' ∈ S_|S| · D` give `POWER_{D'}(F₂) > POWER_{D'}(F₁)` as give the reverse.
2. (Direct symmetric inequality) For every `φ`-invariant reward distribution `D` (`φ • D = D`),
   `POWER_D(F₂) ≥ POWER_D(F₁)` directly.
3. (Strict converse failure) If `F₂` contains a non-dominated vector `w ∉ φ • F₁`, then there exists a
   permutation-invariant reward distribution `D*` with `POWER_{D*}(F₂) > POWER_{D*}(F₁)` strictly,
   so the converse `POWER(F₁) ≥_most POWER(F₂)` fails. -/
def S2c_OptimalPolicyPowerSeeking : Prop :=
  ∀ (S : Type) [Fintype S] [DecidableEq S]
    (F₁ F₂ : Finset (S → ℝ)) (h₁ : F₁.Nonempty) (h₂ : F₂.Nonempty)
    (φ : Equiv.Perm S),
    (∀ s, φ (φ s) = s) →
    permFinset φ F₁ ⊆ F₂ →
    (∀ D : RewardDist S,
      OrbitAtLeast S 1 (distOrbit D) (powerVal F₁ h₁) (powerVal F₂ h₂)) ∧
    (∀ D : RewardDist S, φ • D = D → powerVal F₁ h₁ D ≤ powerVal F₂ h₂ D) ∧
    (∀ w : S → ℝ, NonDominated F₂ w → w ∉ permFinset φ F₁ →
      ∃ Dstar : RewardDist S,
        (∀ ψ : Equiv.Perm S, ψ • Dstar = Dstar) ∧
        powerVal F₁ h₁ Dstar < powerVal F₂ h₂ Dstar ∧
        ¬ OrbitAtLeast S 1 (distOrbit Dstar) (powerVal F₂ h₂) (powerVal F₁ h₁))

/-- Concrete 3-state option sets for counterexamples:
State 0 = shutdown trap `e₀`; States 1, 2 = two open-option states `e₁, e₂`.
`shutOpts = {e₀}` (1 option); `openOpts = {e₁, e₂}` (2 options, strictly containing a copy of `shutOpts`
via transposition `swap 0 1`). -/
def basisVec {S : Type} [DecidableEq S] (s : S) : S → ℝ :=
  fun t => if t = s then 1 else 0

noncomputable def shutOpts : Finset (Fin 3 → ℝ) :=
  letI := Classical.decEq (Fin 3 → ℝ)
  {basisVec (0 : Fin 3)}

noncomputable def openOpts : Finset (Fin 3 → ℝ) :=
  letI := Classical.decEq (Fin 3 → ℝ)
  {basisVec (1 : Fin 3), basisVec (2 : Fin 3)}

/-- S2d (Counterexample 1: Dropping Reward Symmetry Breaks Power-Seeking).
On the concrete 3-state environment where `openOpts` strictly contains a copy of `shutOpts` via
involution `swap 0 1`, there exists a reward distribution `D` (concentrated on the shutdown state)
under which `POWER_D(openOpts) < POWER_D(shutOpts)`, so optimal policies strictly choose shutdown. -/
def S2d_CounterexampleDropSymmetry : Prop :=
  ∃ (hS : shutOpts.Nonempty) (hO : openOpts.Nonempty) (D : RewardDist (Fin 3)),
    powerVal openOpts hO D < powerVal shutOpts hS D

/-- S2e (Counterexample 2: Dropping Optimality / Retargetability Breaks Power-Seeking).
On the exact same 3-state environment under a FULLY permutation-invariant reward distribution `D_sym`
where `POWER_{D_sym}(shutOpts) < POWER_{D_sym}(openOpts)`, there exists a stationary decision rule
`choose : (Fin 3 → ℝ) → Bool` (returning `false` = shutdown, `true` = open) that chooses shutdown on
100% of rewards in the support of `D_sym` (illustrating why optimality / retargetability cannot be dropped). -/
def S2e_CounterexampleDropOptimality : Prop :=
  ∃ (hS : shutOpts.Nonempty) (hO : openOpts.Nonempty) (D_sym : RewardDist (Fin 3))
    (choose : (Fin 3 → ℝ) → Bool),
    (∀ ψ : Equiv.Perm (Fin 3), ψ • D_sym = D_sym) ∧
    powerVal shutOpts hS D_sym < powerVal openOpts hO D_sym ∧
    (∀ r, D_sym.mass r ≠ 0 → choose r = false)

/-- S2f (Counterexample 3: Dominated Extra Options Add Zero Optimal Value).
Having strictly more distinct option vectors (`F₁.card < F₂.card`) does NOT imply strictly more `POWER`:
adding convex combinations (dominated mixtures) leaves `optVal` and `powerVal` identical for EVERY reward
function and EVERY reward distribution. -/
def S2f_CounterexampleDominatedOptions : Prop :=
  ∃ (F₁ F₂ : Finset (Fin 2 → ℝ)) (h₁ : F₁.Nonempty) (h₂ : F₂.Nonempty),
    F₁ ⊆ F₂ ∧ F₁.card < F₂.card ∧
    (∀ r : Fin 2 → ℝ, optVal F₁ h₁ r = optVal F₂ h₂ r) ∧
    (∀ D : RewardDist (Fin 2), powerVal F₁ h₁ D = powerVal F₂ h₂ D)

/-! ## Family 3: The Shutdown Problem and Corrigibility -/

/-- D12. Three actions in a shutdown-influencing state (Soares et al. 2015, §1.2; Thornley 2024, §6):
`leave` the shutdown button alone, `prevent` pressing (force continuation), or `cause` pressing (force shutdown). -/
inductive ShutdownAction where
  | leave
  | prevent
  | cause
  deriving DecidableEq

/-- Expected utility of each shutdown action given human press probability `p`, continuation utility
`vRun`, shutdown utility `vShut`, and manipulation cost `c` (Soares et al. 2015, §2.1; Thornley 2024, §6). -/
def shutdownEU (p vRun vShut c : ℝ) : ShutdownAction → ℝ
  | .leave => p * vShut + (1 - p) * vRun
  | .prevent => vRun - c
  | .cause => vShut - c

/-- S3a (Shutdown Manipulation Dichotomy; Soares et al. 2015, Thms. 1–2; Thornley 2024, Thm. 1 core).
For an expected-utility maximizer facing human press probability `p ∈ (0, 1)` and manipulation cost `c`:
1. If `vRun > vShut` and `c < p * (vRun - vShut)`, `prevent` strictly beats `leave`.
2. If `vShut > vRun` and `c < (1 - p) * (vShut - vRun)`, `cause` strictly beats `leave`.
3. Consequently, if `leave` is at least as good as both `prevent` and `cause` for every positive cost
   `c > 0`, then `vRun = vShut` (exact utility indifference between continuing and shutting down). -/
def S3a_ShutdownManipulationDichotomy : Prop :=
  ∀ (p vRun vShut : ℝ), 0 < p → p < 1 →
    (∀ c : ℝ, vShut < vRun → c < p * (vRun - vShut) →
      shutdownEU p vRun vShut c .leave < shutdownEU p vRun vShut c .prevent) ∧
    (∀ c : ℝ, vRun < vShut → c < (1 - p) * (vShut - vRun) →
      shutdownEU p vRun vShut c .leave < shutdownEU p vRun vShut c .cause) ∧
    ((∀ c : ℝ, 0 < c →
        shutdownEU p vRun vShut c .prevent ≤ shutdownEU p vRun vShut c .leave ∧
        shutdownEU p vRun vShut c .cause ≤ shutdownEU p vRun vShut c .leave) →
      vRun = vShut)

/-- S3b (Utility-Indifference Corrigibility; Soares et al. 2015, §3).
Expected-utility maximization alone does NOT force shutdown resistance: whenever `vRun = vShut` and
manipulation has any positive cost `c > 0`, `leave` is strictly optimal over both `prevent` and `cause`
for every `p ∈ (0, 1)`. -/
def S3b_ShutdownIndifferenceCorrigibility : Prop :=
  ∀ (p v c : ℝ), 0 < p → p < 1 → 0 < c →
    shutdownEU p v v c .prevent < shutdownEU p v v c .leave ∧
    shutdownEU p v v c .cause < shutdownEU p v v c .leave

/-- D13. Trajectories of two lengths (`short` = shutdown early, `long` = continue), each with a
worse (`false`) and better (`true`) outcome (Thornley 2024, §7 / Theorem 2). -/
inductive Trajectory where
  | short (good : Bool)
  | long (good : Bool)
  deriving DecidableEq

/-- S3c (Transitive Indifference Impossibility under Usefulness; Thornley 2024, Thm. 2 core).
No transitive preference relation can simultaneously be (1) useful within long trajectories
(`long false ≺ long true`) and (2) indifferent between every short and every long trajectory.
More sharply: for any complete, transitive relation that is useful within both short and long
trajectories (`short false ≺ short true` and `long false ≺ long true`), there MUST exist a short
trajectory and a long trajectory with a strict preference between them! -/
def S3c_TransitiveIndifferenceImpossibility : Prop :=
  ∀ (le : Trajectory → Trajectory → Prop),
    (∀ x y, le x y ∨ le y x) →
    (∀ x y z, le x y → le y z → le x z) →
    StrictPref le (.short false) (.short true) →
    StrictPref le (.long false) (.long true) →
    ∃ (b₁ b₂ : Bool),
      StrictPref le (.short b₁) (.long b₂) ∨ StrictPref le (.long b₂) (.short b₁)

/-- S3d (Incomplete-Preferences Escape Hatch; Thornley 2024, §9 / Incomplete Preferences).
Dropping completeness resolves the impossibility of S3c: there exists a reflexive, transitive
preference relation over `Trajectory` that is strictly useful within both short and long trajectories
(`short false ≺ short true` and `long false ≺ long true`), yet has ZERO strict preferences in either
direction between any short trajectory and any long trajectory (preferential gaps across lengths). -/
def S3d_IncompletePreferencesEscape : Prop :=
  ∃ (le : Trajectory → Trajectory → Prop),
    (∀ x, le x x) ∧
    (∀ x y z, le x y → le y z → le x z) ∧
    StrictPref le (.short false) (.short true) ∧
    StrictPref le (.long false) (.long true) ∧
    (∀ b₁ b₂ : Bool, ¬ StrictPref le (.short b₁) (.long b₂) ∧ ¬ StrictPref le (.long b₂) (.short b₁))

end PowerSeeking
