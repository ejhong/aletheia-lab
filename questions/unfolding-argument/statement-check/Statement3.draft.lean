module

public import UnfoldingArgument.Statement
public import Mathlib.Data.Nat.Factorial.Basic
public import Mathlib.SetTheory.Cardinal.Finite

/-!
# The unfolding argument, Stage 3: units with memory

Statements only, as in `Statement.lean`. Proofs are in `Results3.lean`.
This file is locked (`protocol.lock`) and is not edited after the lock. See Amendment 1 in `amendments.md`.

Stage 1 showed that a network in which no unit depends on its own past (`LoopFree`) cannot match a latch for all
time. Hanson and Walker (2021) use a weaker notion of feed-forward, in which a unit may keep its own state and
only feedback between different units is excluded (`FeedbackFree`). This stage asks what such networks can match
for all time, and finds that the answer depends on how many states a unit may have.
-/

@[expose] public section

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
