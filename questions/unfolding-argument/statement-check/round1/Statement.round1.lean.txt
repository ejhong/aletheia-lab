module

public import Mathlib.Data.Fintype.Card
public import Mathlib.Data.Fintype.Option
public import Mathlib.Data.Fintype.Prod
public import Mathlib.Logic.Relation
public import Mathlib.Data.Set.Basic

/-!
# The unfolding argument: definitions and statements

Every claim is a `def … : Prop`. Nothing here is proved; proofs are in `Results.lean`.
This file is locked (`protocol.lock`) and is not edited after the lock.

Sources (see `statement-check/passages.md` for the passages):
Doerig, Schurger, Hess and Herzog 2019; Kleiner and Hoel 2021; Hanson and Walker 2021;
Herzog, Schurger and Doerig 2022; O'Reilly-Shah, Selvitella and Schurger 2026.
-/

@[expose] public section

namespace Unfolding

universe u v w

/-! ## Definitions: systems, behaviour, causal structure -/

/-- D1. A system made of finitely many units ("nodes"). Each node has its own state. Time is discrete.
At each step every node computes its next state from the current states of the nodes and the current
input. The output is read off the current states. -/
structure Network (I O : Type) where
  /-- the units -/
  Node : Type
  /-- there are finitely many units -/
  fintypeNode : Fintype Node
  /-- the possible states of each unit -/
  St : Node → Type
  /-- the starting state of each unit -/
  init : (n : Node) → St n
  /-- the update rule of each unit: from the current states of all units and the current input -/
  step : (n : Node) → ((m : Node) → St m) → I → St n
  /-- the readout: the output as a function of the current states -/
  out : ((m : Node) → St m) → O

attribute [instance] Network.fintypeNode

namespace Network

variable {I O : Type}

/-- A joint state: one state for every node. -/
abbrev State (N : Network I O) : Type := (m : N.Node) → N.St m

/-- One time step: every node updates at once. -/
def next (N : Network I O) (σ : N.State) (x : I) : N.State := fun n => N.step n σ x

/-- The joint state after the inputs `xs` have been fed in, one per step, from the starting state. -/
def run (N : Network I O) (xs : List I) : N.State := xs.foldl N.next N.init

/-- D2. Input-output behaviour: the output after the inputs `xs` have been fed in. As `xs` ranges over
all input sequences this is the system's whole input-output function. -/
def response (N : Network I O) (xs : List I) : O := N.out (N.run xs)

/-- D3. Same behaviour over a horizon of `T` steps: the same output after every input sequence of
length at most `T`. -/
def AgreeUpTo (T : ℕ) (N N' : Network I O) : Prop :=
  ∀ xs : List I, xs.length ≤ T → N.response xs = N'.response xs

/-- D4. Same behaviour at every horizon. -/
def AgreeAlways (N N' : Network I O) : Prop := ∀ xs : List I, N.response xs = N'.response xs

/-- D5. `N.DependsOn n m`: the next state of node `n` depends on the current state of node `m`. That
is, there are two joint states that differ at most at `m`, and an input, for which `n` updates
differently. -/
def DependsOn (N : Network I O) (n m : N.Node) : Prop :=
  ∃ (σ σ' : N.State) (x : I), (∀ k, k ≠ m → σ k = σ' k) ∧ N.step n σ x ≠ N.step n σ' x

/-- `N.Influences m n`: an arrow from `m` to `n` in the causal graph (`n` depends on `m`). -/
def Influences (N : Network I O) (m n : N.Node) : Prop := N.DependsOn n m

/-- D6. Loop-free (feedforward): the causal graph has no directed cycle of any length. In particular
no node depends on its own previous state. -/
def LoopFree (N : Network I O) : Prop := ∀ n, ¬ Relation.TransGen N.Influences n n

/-- D7. Recurrent: the causal graph has a directed cycle. This is the negation of `LoopFree`. -/
def Recurrent (N : Network I O) : Prop := ∃ n, Relation.TransGen N.Influences n n

/-- D8. Integrated: there is at least one node, and every node influences every node (itself included)
along some directed path. Every node then lies on a feedback loop with every other. -/
def Integrated (N : Network I O) : Prop :=
  Nonempty N.Node ∧ ∀ m n, Relation.TransGen N.Influences m n

/-- D9. Feedback-free: no two different nodes influence each other, directly or through other nodes.
A node may still depend on its own previous state (a unit with memory). -/
def FeedbackFree (N : Network I O) : Prop :=
  ∀ m n, m ≠ n → ¬ (Relation.TransGen N.Influences m n ∧ Relation.TransGen N.Influences n m)

/-- D10. Size: the number of nodes. -/
def size (N : Network I O) : ℕ := Fintype.card N.Node

/-- D11. Unfolding in time. `N.unfold T` has `T` layers, each a copy of the nodes of `N`. A node in
layer 0 updates as its original would from the starting state of `N`. A node in layer `k + 1` updates
as its original would from the current states of layer `k`. Every layer receives the current input.
The output is read from the last layer. -/
def unfold (N : Network I O) (T : ℕ) : Network I O where
  Node := Fin T × N.Node
  fintypeNode := inferInstance
  St := fun a => N.St a.2
  init := fun a => N.init a.2
  step := fun a σ x =>
    N.step a.2 (fun m => if h : a.1.val = 0 then N.init m else σ (⟨a.1.val - 1, by omega⟩, m)) x
  out := fun σ =>
    if h : T = 0 then N.out N.init else N.out (fun m => σ (⟨T - 1, by omega⟩, m))

end Network

/-- D12. The latch: one node holding one bit, which starts at `false` and becomes `true` for good once
an input `true` has arrived. The output is the bit. -/
def latch : Network Bool Bool where
  Node := Unit
  fintypeNode := inferInstance
  St := fun _ => Bool
  init := fun _ => false
  step := fun _ σ x => σ () || x
  out := fun σ => σ ()

/-- D13. A system that learns while it runs: an activity state and connection weights. At each step the
activity is updated using the current weights, and the weights are updated by a learning rule. -/
structure PlasticSystem (I O : Type) where
  /-- the possible weights -/
  W : Type
  /-- the possible activity states -/
  A : Type
  /-- the starting weights -/
  w0 : W
  /-- the starting activity -/
  a0 : A
  /-- the activity update, which uses the current weights -/
  act : W → A → I → A
  /-- the learning rule, which changes the weights -/
  learn : W → A → I → W
  /-- the readout -/
  out : A → O

namespace PlasticSystem

variable {I O : Type}

/-- Weights and activity after the inputs `xs`. -/
def run (P : PlasticSystem I O) (xs : List I) : P.W × P.A :=
  xs.foldl (fun s x => (P.learn s.1 s.2 x, P.act s.1 s.2 x)) (P.w0, P.a0)

/-- The output after the inputs `xs`. -/
def response (P : PlasticSystem I O) (xs : List I) : O := P.out (P.run xs).2

end PlasticSystem

/-- D14. A network probed from inside. At each step the experimenter supplies an input and an
intervention `p`; after the nodes update, `intervene p` rewrites the joint state. The response is the
output after a sequence of such pairs. -/
def Network.perturbedResponse {I O P : Type} (N : Network I O) (intervene : P → N.State → N.State)
    (xs : List (I × P)) : O :=
  N.out (xs.foldl (fun σ xp => intervene xp.2 (N.next σ xp.1)) N.init)

/-! ## Stage 1 statements: the mathematical core -/

/-- S1a. Unfolding works at a finite horizon. For every network and every `T`, the network unfolded
over `T` layers is loop-free, behaves as the original for `T` steps, and has `T` times as many nodes. -/
def UnfoldingAtFiniteHorizon : Prop :=
  ∀ (I O : Type) (N : Network I O) (T : ℕ),
    (N.unfold T).LoopFree ∧ Network.AgreeUpTo T (N.unfold T) N ∧ (N.unfold T).size = T * N.size

/-- S1b. Any input-output function at all, over a horizon of `T` steps, is computed by some loop-free
network with exactly `T` nodes. -/
def EveryBehaviourHasLoopFreeRealizer : Prop :=
  ∀ (I O : Type) (f : List I → O) (T : ℕ),
    ∃ N : Network I O, N.LoopFree ∧ N.size = T ∧ ∀ xs : List I, xs.length ≤ T → N.response xs = f xs

/-- S1c. A loop-free network has finite memory. Once at least as many inputs as it has nodes have been
fed in, its output no longer depends on anything that came before them. -/
def LoopFreeHasFiniteMemory : Prop :=
  ∀ (I O : Type) (N : Network I O), N.LoopFree →
    ∀ xs ys zs : List I, N.size ≤ zs.length → N.response (xs ++ zs) = N.response (ys ++ zs)

/-- S1d. The limit of unfolding. The latch is recurrent, and no loop-free network, however large, has
the same behaviour as the latch at every horizon. -/
def LatchHasNoLoopFreeTwin : Prop :=
  latch.Recurrent ∧ ¬ ∃ N : Network Bool Bool, N.LoopFree ∧ Network.AgreeAlways N latch

/-- S1e. The size of the twin. A loop-free network that behaves as the latch for `T` steps has at least
`T` nodes. -/
def LatchTwinNeedsHorizonManyNodes : Prop :=
  ∀ (T : ℕ) (N : Network Bool Bool), N.LoopFree → Network.AgreeUpTo T N latch → T ≤ N.size

/-- S1f. Learning does not block unfolding at a finite horizon. Every system that learns while it runs
has, for every `T`, a loop-free network with `T` nodes and fixed update rules that gives the same
outputs for `T` steps. -/
def PlasticSystemHasLoopFreeTwin : Prop :=
  ∀ (I O : Type) (P : PlasticSystem I O) (T : ℕ),
    ∃ N : Network I O, N.LoopFree ∧ N.size = T ∧
      ∀ xs : List I, xs.length ≤ T → N.response xs = P.response xs

/-- S1g. Probing from inside, counted as input, does not block unfolding at a finite horizon. For every
network, every family of interventions on its state and every `T`, some loop-free network that takes
the pairs (input, intervention) as its inputs gives the same outputs for `T` steps. -/
def PerturbedNetworkHasLoopFreeTwin : Prop :=
  ∀ (I O P : Type) (N : Network I O) (intervene : P → N.State → N.State) (T : ℕ),
    ∃ N' : Network (I × P) O, N'.LoopFree ∧ N'.size = T ∧
      ∀ xs : List (I × P), xs.length ≤ T → N'.response xs = N.perturbedResponse intervene xs

/-- S1h. Folding, the other direction, works at every horizon. If there is at least one possible
input, every network has a twin with one more node that is integrated and has the same behaviour at
every horizon. -/
def EveryNetworkHasIntegratedTwin : Prop :=
  ∀ (I O : Type), Nonempty I → ∀ (N : Network I O),
    ∃ N' : Network I O, N'.Integrated ∧ N'.size = N.size + 1 ∧ Network.AgreeAlways N' N

/-- S1i. If a unit may have memory, one unit is enough. Every network has a twin with a single node,
hence with no feedback between different nodes, and the same behaviour at every horizon. -/
def EveryNetworkHasSingleUnitTwin : Prop :=
  ∀ (I O : Type) (N : Network I O),
    ∃ N' : Network I O, N'.size = 1 ∧ N'.FeedbackFree ∧ Network.AgreeAlways N' N

/-! ## Definitions: testing a theory (Kleiner and Hoel) -/

/-- D15. An experimental setup for testing a theory of consciousness. `P`: physical systems. `D`:
datasets. `E`: experiences. `R`: inference contents (reports). -/
structure Testing (P D E R : Type) where
  /-- the datasets that measuring a system can give -/
  obs : P → Set D
  /-- the experiences the theory predicts from a dataset -/
  pred : D → Set E
  /-- the inference content (report part) of a dataset -/
  rep : D → R
  /-- the experience the experimenter infers from the inference content -/
  inf : R → E

namespace Testing

variable {P D E R : Type}

/-- The datasets that can arise from some system. -/
def Datasets (t : Testing P D E R) : Set D := {o | ∃ p, o ∈ t.obs p}

/-- D16. A falsification at a dataset: the inferred experience is not among the predicted ones. -/
def FalsificationAt (t : Testing P D E R) (o : D) : Prop := t.inf (t.rep o) ∉ t.pred o

/-- The systems that can give a dataset with inference content `r`. -/
def Produces (t : Testing P D E R) (r : R) : Set P := {p | ∃ o ∈ t.obs p, t.rep o = r}

/-- All experiences predicted from some dataset of system `p`. -/
def predOf (t : Testing P D E R) (p : P) : Set E := {e | ∃ o ∈ t.obs p, e ∈ t.pred o}

/-- D17. A substitution at inference content `r`: a map from the systems that can give `r` to
themselves, and one such system whose predicted experiences share nothing with those of its image. -/
def SubstitutionAt (t : Testing P D E R) (r : R) : Prop :=
  ∃ (S : t.Produces r → t.Produces r) (p : t.Produces r), t.predOf p.1 ∩ t.predOf (S p).1 = ∅

/-- `r` is the inference content of some dataset that can arise. -/
def Arises (t : Testing P D E R) (r : R) : Prop := ∃ o ∈ t.Datasets, t.rep o = r

/-- D18. A universal substitution: a substitution at every inference content that arises. -/
def UniversalSubstitution (t : Testing P D E R) : Prop := ∀ r, t.Arises r → t.SubstitutionAt r

end Testing

/-! ## Stage 2 statements: the falsification argument and the replies -/

/-- S2a. A substitution gives a falsification, at a dataset with that same inference content. -/
def SubstitutionGivesFalsification : Prop :=
  ∀ (P D E R : Type) (t : Testing P D E R) (r : R),
    t.SubstitutionAt r → ∃ o ∈ t.Datasets, t.rep o = r ∧ t.FalsificationAt o

/-- S2b. A universal substitution gives a falsification for every inference content that arises. -/
def UniversalSubstitutionFalsifiesEveryReport : Prop :=
  ∀ (P D E R : Type) (t : Testing P D E R),
    t.UniversalSubstitution → ∀ r, t.Arises r → ∃ o ∈ t.Datasets, t.rep o = r ∧ t.FalsificationAt o

/-- S2c. With a universal substitution, whatever the true experience of each system is: either every
inference content that arises has a case where the inference is wrong, or some prediction is wrong. -/
def EveryInferenceWrongOrTheoryWrong : Prop :=
  ∀ (P D E R : Type) (t : Testing P D E R), t.UniversalSubstitution →
    ∀ truth : P → E,
      (∀ r, t.Arises r → ∃ p, ∃ o ∈ t.obs p, t.rep o = r ∧ t.inf r ≠ truth p) ∨
      (∃ p, ∃ o ∈ t.obs p, truth p ∉ t.pred o)

/-- S2d. Strict dependence. Take datasets with a prediction content `ic o` and an inference content
`rc o`, the datasets `O` that can arise in the experiment, and a larger class `Obar` of conceivable
datasets. Suppose the prediction content is a function of the inference content throughout `Obar`,
and every inference content in `Obar` already occurs in `O`. Then there is a falsification somewhere
in `Obar` exactly when there is one in `O`. -/
def StrictDependenceLeavesNothingToTest : Prop :=
  ∀ (D Ic Rc E : Type) (ic : D → Ic) (rc : D → Rc) (pred : Ic → Set E) (inf : Rc → E)
    (O Obar : Set D),
    O ⊆ Obar → (∀ o ∈ Obar, ∃ o' ∈ O, rc o' = rc o) → (∃ f : Rc → Ic, ∀ o ∈ Obar, ic o = f (rc o)) →
    ((∃ o ∈ Obar, inf (rc o) ∉ pred (ic o)) ↔ (∃ o ∈ O, inf (rc o) ∉ pred (ic o)))

/-- S2d′. The second assumption of S2d is needed. There is a setup with strict dependence throughout
`Obar` and no falsification in `O`, but with a falsification in `Obar`. -/
def StrictDependenceCanStillBeTested : Prop :=
  ∃ (D Ic Rc E : Type) (ic : D → Ic) (rc : D → Rc) (pred : Ic → Set E) (inf : Rc → E)
    (O Obar : Set D),
    O ⊆ Obar ∧ (∃ f : Rc → Ic, ∀ o ∈ Obar, ic o = f (rc o)) ∧
    (¬ ∃ o ∈ O, inf (rc o) ∉ pred (ic o)) ∧ (∃ o ∈ Obar, inf (rc o) ∉ pred (ic o))

/-- The behaviour of a network over a horizon of `T` steps, as an object: the output after each input
sequence of length at most `T`. -/
def Network.behaviourUpTo {I O : Type} (N : Network I O) (T : ℕ) : {xs : List I // xs.length ≤ T} → O :=
  fun xs => N.response xs.1

/-- S2e. The unfolding argument at a finite horizon. Take any verdict on which networks are conscious
that calls no loop-free network conscious and calls some network conscious. Take any rule that infers
"conscious or not" from behaviour over `T` steps. Then the verdict and the rule disagree on some
network. -/
def UnfoldingArgumentAtFiniteHorizon : Prop :=
  ∀ (I O : Type) (T : ℕ) (conscious : Network I O → Prop),
    (∀ N, N.LoopFree → ¬ conscious N) → (∃ N, conscious N) →
    ∀ inf : ({xs : List I // xs.length ≤ T} → O) → Prop,
      ∃ N : Network I O, ¬ (conscious N ↔ inf (N.behaviourUpTo T))

/-- S2f. The folding argument at every horizon. Suppose there is at least one possible input. Take any
verdict that calls every integrated network conscious and calls some network not conscious. Take any
rule that infers "conscious or not" from the whole input-output behaviour. Then the verdict and the
rule disagree on some network. -/
def FoldingArgumentAtEveryHorizon : Prop :=
  ∀ (I O : Type), Nonempty I → ∀ (conscious : Network I O → Prop),
    (∀ N, N.Integrated → conscious N) → (∃ N, ¬ conscious N) →
    ∀ inf : (List I → O) → Prop,
      ∃ N : Network I O, ¬ (conscious N ↔ inf N.response)

/-- S2g. What survives when behaviour over unbounded time counts. There is a verdict that calls no
loop-free network conscious and calls some network conscious, and a rule that infers the verdict from
the whole input-output behaviour, which agree on every network. -/
def LoopFreeExclusionSurvivesUnboundedHorizon : Prop :=
  ∃ (conscious : Network Bool Bool → Prop) (inf : (List Bool → Bool) → Prop),
    (∀ N, N.LoopFree → ¬ conscious N) ∧ (∃ N, conscious N) ∧
    ∀ N : Network Bool Bool, (conscious N ↔ inf N.response)

/-- S2h. Which theories the argument spares. A theory's predictions agree with some rule of inference
from behaviour on every system exactly when the theory gives the same prediction to any two systems
with the same behaviour. -/
def SparedIffDeterminedByBehaviour : Prop :=
  ∀ (Sys : Type u) (Beh : Type v) (E : Type w), Nonempty E → ∀ (beh : Sys → Beh) (pred : Sys → E),
    ((∃ inf : Beh → E, ∀ s, pred s = inf (beh s)) ↔ (∀ s s', beh s = beh s' → pred s = pred s'))

/-- S2i. Evidence beyond behaviour removes the forced mismatch. For any theory there is some further
observable of systems and a rule of inference from behaviour together with that observable which
agrees with the theory on every system. -/
def FurtherEvidenceRemovesMismatch : Prop :=
  ∀ (Sys : Type u) (Beh : Type v) (E : Type w) (beh : Sys → Beh) (pred : Sys → E),
    ∃ (X : Type w) (extra : Sys → X) (inf : Beh × X → E), ∀ s, pred s = inf (beh s, extra s)

end Unfolding
