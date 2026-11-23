# Machine-check the unfolding argument: results for Stages 0 to 3

Issue #66 · Lane: proof · Protocol and statements locked 2026-11-23T18:04:39Z (commit `7502087`) · Stage 3 statements locked
2026-11-23T19:03:05Z (commit `327ba92`) · One amendment

## Answer

Stages 0 to 2: all twenty locked statements are proved in Lean 4. Stage 3: all six are proved as well; see
[Stage 3](#stage-3-units-with-memory) below. That makes twenty-six. The rest of this section, and everything down
to the Stage 3 heading, is about Stages 0 to 2.

All twenty locked statements are proved in Lean 4. Each proof depends only on Lean's three standard axioms, and
the build passes in CI with warnings treated as errors
([run 45234539396](https://github.com/ejhong/aletheia-lab/actions/runs/45234539396), commit `f550f36`).

In one sentence: the unfolding argument's mathematical premise is true at any fixed time horizon and false without
one, but the argument does not need it in the direction that fails, because the opposite replacement, adding
feedback that does nothing, works for all time; what carries the conclusion is the premise that evidence about
consciousness is a function of behaviour.

The mathematics is elementary and none of it is surprising to someone who knows automata theory. What the lab adds
is the exact statements, the tie from each to a source passage, the table of which premise carries which
conclusion, and a kernel that has checked every step.

## What follows from what (plain summary)

A system here is a finite set of units, each with a state, updated in steps from the current states and the
current input, with an output read from the states. Its behaviour is the output after each finite sequence of
inputs. Its causal structure is the graph of which unit's update depends on which unit's state. It is *loop-free*
(feedforward) if that graph has no cycle, and *recurrent* if it has one.

1. **Unfolding works at any fixed horizon.** Copy the system T times, let copy k+1 compute from copy k, and read
   the last copy. The result is loop-free and behaves exactly as the original for T steps (S1a). Any behaviour at
   all over T steps, computable or not, has a loop-free realizer with T units that stores the inputs and looks the
   answer up (S1b).
2. **It does not work without a horizon.** A loop-free system with d units has forgotten everything older than d
   steps (S1c). So one bit that is set once and stays set, the *latch*, has no loop-free twin that matches it
   forever (S1d), and a loop-free twin that matches it for T steps needs at least T units (S1e). The unfolded
   latch has exactly T, so the bound is met. The twin must grow by one unit for every further step of the
   experiment.
3. **Learning changes nothing at a fixed horizon.** A system whose weights change as it runs still has a loop-free
   twin with fixed rules and T units for T steps (S1f). The same holds when the experimenter also intervenes
   inside the system, if the intervention is counted as part of the input (S1g). What blocks unfolding is
   unbounded time, and the latch shows that fixed weights already suffice for that.
4. **The other direction works for all time.** Add one unit, wire it in a loop with every other unit, and let the
   output ignore it. Every system has such a twin, with the same behaviour forever (S1h). Feedback that does
   nothing is cheap.
5. **The falsification step is short.** Suppose evidence about consciousness is a function of behaviour over T
   steps. Then a theory that calls no loop-free system conscious, and calls some system conscious, disagrees with
   the evidence about that system or about its unfolded twin (S2e). And if evidence is a function of the whole
   behaviour, with no time limit, a theory that calls every integrated system conscious, and some system not
   conscious, disagrees with the evidence about that system or about its twin with the idle loop (S2f).
6. **So time, size and plasticity help only half of a causal structure theory.** They bear on the claim that
   feedback is *necessary* for consciousness. A theory that only excludes loop-free systems is consistent with
   behavioural evidence taken over unbounded time (S2g). They do nothing for the claim that feedback is
   *sufficient*.
7. **The argument reaches far beyond causal structure.** Some rule of inference from behaviour agrees with a
   theory everywhere exactly when the theory never distinguishes two systems with the same behaviour (S2h). The
   theory that survives in point 6 is of that kind: it calls a system conscious when no loop-free system could
   behave as it does, which is a claim about behaviour.
8. **Everything rests on the evidence premise.** Admit any evidence beyond behaviour and nothing forces a mismatch
   (S2i). That is trivial to prove, and it is where the dispute actually is.

Nothing here says whether evidence beyond behaviour exists, whether any theory of consciousness is right, or what
the integrated information of any system is.

## Results table: Stage 1, the mathematical core

"Premises" are the hypotheses of the theorem. Every statement is in `lean/UnfoldingArgument/Statement.lean`, every
proof in `lean/UnfoldingArgument/Results.lean`.

| | Claim | Lean name | Premises | Status | Source |
|---|---|---|---|---|---|
| S1a | The network unfolded over T layers is loop-free, behaves as the original for T steps, and has T times the units | `UnfoldingAtFiniteHorizon` | none | proved | Doerig 2019, pp. 52–53 (P2); Herzog 2022, p. 10 |
| S1b | Any input-output function over T steps has a loop-free realizer with exactly T units | `EveryBehaviourHasLoopFreeRealizer` | none | proved | Doerig 2019, pp. 51–52; Herzog 2022, p. 11 |
| S1c | After as many inputs as it has units, a loop-free network's output does not depend on anything earlier | `LoopFreeHasFiniteMemory` | the network is loop-free | proved | O'Reilly-Shah 2026, "Proofs" |
| S1d | The latch is recurrent, and no loop-free network behaves as it does at every horizon | `LatchHasNoLoopFreeTwin` | none | proved | the lab's; against P2 without a time limit |
| S1e | A loop-free network that behaves as the latch for T steps has at least T units | `LatchTwinNeedsHorizonManyNodes` | loop-free; agrees with the latch for T steps | proved; the bound is met (`latch_twin_with_exactly_T_nodes`) | the lab's |
| S1f | A system that learns while it runs has a loop-free twin with T units for T steps | `PlasticSystemHasLoopFreeTwin` | none | proved | the lab's; against O'Reilly-Shah 2026 |
| S1g | A network probed from inside has a loop-free twin with T units for T steps, if the probe counts as input | `PerturbedNetworkHasLoopFreeTwin` | none | proved | the lab's; Doerig 2019, p. 51 |
| S1h | Every network has an integrated twin with one more unit and the same behaviour at every horizon | `EveryNetworkHasIntegratedTwin` | at least one possible input | proved | the lab's; Doerig 2019, p. 53 ("vice-versa"), Appendix A |
| S1i | Every network has a single-unit twin with the same behaviour at every horizon | `EveryNetworkHasSingleUnitTwin` | none | proved | the lab's; Hanson and Walker 2021 |

The witnesses, all defined in the Lean files:

- **S1a: `unfold`.** T copies of the units in a pipeline. Every copy starts in the original's starting state and
  receives the current input; copy 0 always computes from the starting state, copy k+1 from copy k. After t ≤ T
  inputs the last copy holds the original's state. Each unit of the twin is a copy of a unit of the original.
- **S1b, S1f, S1g: `lookup`.** A delay line of T units, unit k holding the input from k+1 steps ago. The readout
  recovers the input history and applies the target function to it. All the work is in the readout.
- **S1h: `integrate`.** One hub unit holding a bit, and one extra bit on every original unit. Each original unit
  copies the hub's bit; the hub flips according to its own bit and whether all the extra bits are set. The output
  ignores all of this. The hub starts set, so that the extra bits change along the run and the loop is not
  idle in the sense of never being exercised; that last remark is by inspection and is not a theorem.
- **S1i: `collapse`.** The whole network as one unit.

## Results table: Stage 2, the falsification argument

Proofs in `lean/UnfoldingArgument/Results2.lean`.

| | Claim | Lean name | Premises | Status | Source |
|---|---|---|---|---|---|
| S2a | A substitution at a report gives a falsification at a dataset with that report | `SubstitutionGivesFalsification` | a substitution exists | proved | Kleiner and Hoel 2021, Lemmas 3.3, 3.5 |
| S2b | A universal substitution gives a falsification for every report that arises | `UniversalSubstitutionFalsifiesEveryReport` | a universal substitution | proved | Kleiner and Hoel 2021, Prop. 3.6 |
| S2c | Then, whatever the true experiences are: every report is wrong about at least one system, or some prediction is wrong | `EveryInferenceWrongOrTheoryWrong` | a universal substitution | proved | Kleiner and Hoel 2021, Prop. 3.7 |
| S2c′ | "Every inference is wrong" cannot be read more strongly: with a universal substitution and every prediction right, some inference can be right | `SomeInferenceCanStillBeRight` | none (an example) | proved | the lab's; about Prop. 3.7 |
| S2d | Under strict dependence, if every conceivable report already occurs in the experiment, there is a falsification among the conceivable datasets exactly when there is one in the experiment | `StrictDependenceLeavesNothingToTest` | strict dependence; every conceivable report occurs | proved | Kleiner and Hoel 2021, Theorem 4.3 and its proof |
| S2d′ | Without the second premise of S2d the conclusion fails | `StrictDependenceCanStillBeTested` | none (an example) | proved | the lab's; about Theorem 4.3 as printed |
| S2e | A verdict that calls no loop-free network conscious and some network conscious disagrees, on some network, with any rule that infers consciousness from T steps of behaviour | `UnfoldingArgumentAtFiniteHorizon` | the two properties of the verdict; inference is a function of T-step behaviour | proved | Doerig 2019, p. 53 (P1–P4, C) |
| S2f | A verdict that calls every integrated network conscious and some network not conscious disagrees, on some network, with any rule that infers from the whole behaviour | `FoldingArgumentAtEveryHorizon` | the two properties of the verdict; inference is a function of behaviour; one possible input | proved | the lab's; Doerig 2019, pp. 52–53, Appendix A |
| S2g | Some verdict calls no loop-free network conscious, calls some network conscious, and agrees everywhere with a rule that infers from the whole behaviour | `LoopFreeExclusionSurvivesUnboundedHorizon` | none (an example) | proved | the lab's |
| S2h | Some rule of inference from behaviour agrees with a theory everywhere exactly when the theory gives the same prediction to systems with the same behaviour | `SparedIffDeterminedByBehaviour` | at least one possible prediction | proved | the lab's |
| S2i | For any theory there is a further observable such that a rule of inference from behaviour and that observable agrees with the theory everywhere | `FurtherEvidenceRemovesMismatch` | none | proved | the lab's; Herzog 2022, pp. 4, 9; Kleiner and Hoel 2021, §5.2 |

### The premises of Doerig et al. (2019, p. 53), and what carries the conclusion

| Premise | In the Lean | Carries the conclusion? |
|---|---|---|
| P1, P3, P4: evidence about consciousness comes from measurements; systems with the same input-output function cannot be told apart; brain activity cannot be used as an indicator in advance | One assumption: the inference about consciousness is a function of input-output behaviour (the type of the rule in S2e and S2f) | Yes. Drop it and nothing follows (S2i). With it, every theory that distinguishes two systems with the same behaviour is in conflict with the inference somewhere (S2h) |
| P2, first half: every recurrent system has a feedforward twin | Proved for any fixed number of steps (S1a, S1b). False without a time limit (S1d). The twin needs a unit per step (S1e) | Needed only against the claim that feedback is necessary, and then only if evidence is limited to a fixed number of steps (S2e, S2g) |
| P2, "and vice-versa": every feedforward system has a recurrent twin | Proved for all time, at the cost of one unit (S1h) | Enough by itself against the claim that feedback is sufficient (S2f) |
| The theory is a causal structure theory | The verdict calls no loop-free network conscious (S2e), or every integrated network conscious (S2f) | Each half is used separately |
| C: the theory is falsified, or outside science | The verdict and the inferred verdict differ on some system (S2e, S2f). Which of the two is wrong is not something the Lean says | |

### The replies

| Reply | Premise it denies | What the proofs say | What the argument still yields |
|---|---|---|---|
| **The twin is too large** (Usher 2021, as reported by Herzog 2022, pp. 3, 10; Doerig 2019, p. 54, concedes "many more neurons") | P2, as a practical matter | True and exact for the latch: one unit per time step, no fewer (S1e), and T units always suffice for any behaviour (S1b). | Everything, at a fixed horizon: size is not a logical obstacle (S1a). The reply becomes a logical one only together with the next. |
| **It only works for a bounded time** (implicit in "unrolling"; O'Reilly-Shah 2026 grant equivalence only "over finite time horizons") | P2 without a time limit | Correct. A one-bit latch has no loop-free twin at every horizon (S1d). | Against "feedback is sufficient": everything (S1h, S2f). Against "feedback is necessary": nothing, once evidence may run over unbounded time (S2g). But the theory that survives is one whose verdict is fixed by behaviour (S2h). |
| **Plasticity breaks the equivalence** (O'Reilly-Shah, Selvitella and Schurger 2026) | P2 for systems that learn | Not at a fixed horizon, when equivalence means the same output after every input history: a learning system has a loop-free twin with fixed rules (S1f). Over unbounded time there is no twin, but that is already so for a latch with fixed weights (S1d). The paper compares a mapping that changes over time with a static one, which is a different notion of equivalence; under it the paper's claim is not touched by S1f. | As for the previous row. Plasticity is not what does the work; unbounded memory is. |
| **Perturbing the system from inside tells them apart** (Usher 2021, abstract; O'Reilly-Shah 2026) | P3 | If the perturbation is an input to both systems, no: the twin reproduces the responses (S1g), as Doerig et al. say (p. 51). If it means intervening on the twin's own units, the Lean says nothing; that is Stage 3. | Unsettled here. |
| **First-person evidence is not behaviour** (Tsuchiya, Andrillon and Haun 2020, as reported by Herzog 2022, p. 9) | P1, P4 | If any evidence beyond behaviour is admitted, no mismatch is forced (S2i). | Nothing. Whether such evidence is admissible is not a mathematical question, and it is the whole dispute. |
| **The argument proves too much** (Kleiner and Hoel 2021 present it as a generalization: it applies to "any minimally informative theory") | none; it is about scope | Correct in the single-valued setting: every theory that distinguishes two systems with the same behaviour is reached (S2h). | Only theories whose verdict is a function of behaviour are spared. |
| **Then behaviourist theories are unfalsifiable** (Kleiner and Hoel 2021, Theorem 4.3) | none; the second horn of their dilemma | Holds with a premise the printed theorem does not state: every conceivable report already occurs in the experiment (S2d). Without it the conclusion fails (S2d′). | The dilemma stands for experiments that already see every conceivable report. |
| **Feed-forward circuits with memory match forever** (Hanson and Walker 2021, via Krohn–Rhodes) | the limit in S1d | If a unit may keep its own state and may be arbitrarily complex, one unit matches any system forever (S1i); the limits S1c–S1e hold only when no unit depends on its own past. | Stage 3 takes the case that matters, simple units with memory: a counter to eight has such a circuit of bits (S3c), a counter to three has none (S3b′). |

The issue attributed the "overreach" reply to Usher. That attribution is `unverified`: Usher's article was not in
hand, and its abstract argues the other points in the table.

## Non-vacuity

A theorem with premises can hold only because the premises cannot be met. `lean/UnfoldingArgument/NonVacuity.lean`
gives an instance for each statement that has premises:

- A loop-free network exists (`loopFree_exists`), for S1c.
- For every T there is a loop-free network that behaves as the latch for T steps and has exactly T units
  (`latch_twin_with_exactly_T_nodes`). So S1e's premises can be met, and its bound cannot be improved.
- A setup with a substitution, and with a universal substitution, exists (`substitution_exists`), for S2a to S2c.
- The premises of S2d hold in a setup that does have a falsification (`strictDependence_instance`).
- One verdict meets the premises of S2e and of S2f at once: "conscious exactly when recurrent"
  (`causal_structure_verdict_exists`).

Also proved there: `Recurrent` is the negation of `LoopFree`, and an integrated network is recurrent.

## Statement check

Before the lock, models from two other vendors read every definition and statement: OpenAI `gpt-6.2-astra` and
Google `gemini-4-neon`, on 2026-11-23, in three rounds. Each first translated the Lean into English without seeing
the source, the lab's names or its comments, and then compared the Lean with the source passages and the lab's
claim. Full detail: `statement-check/REPORT.md`; the history of changes is in `protocol.md`.

- **Planted errors.** Six wrong statements were mixed in. Both checkers called all six divergent.
- **Final verdicts.** Of 26 real items (6 groups of definitions, 20 statements), both checkers gave `faithful` or
  `faithful_with_caveats` on 24.
- **What the check changed.** A definition was corrected; one statement was added (S2c′, from a counterexample
  the OpenAI checker gave); several of my descriptions of statements were wrong or overclaimed and were rewritten,
  among them my account of what the plasticity paper concedes; one statement was tied to the wrong passage.

### Unresolved divergences

| Item | Who | Divergence | Standing |
|---|---|---|---|
| S1a | OpenAI: `divergent`. Google: the same point, rated minor | Premise P2 as printed has no time limit. S1a gives, for each T, a twin that matches for T steps only | Accepted. This is the result, not a defect of the formalization: the printed premise is false (S1d) and S1a is what can be proved |
| S2e | OpenAI: `divergent`. Google: `faithful_with_caveats` | The same: the passage speaks of identical input-output functions without a time bound; in S2e the inference sees T steps | Accepted. Without a time bound the argument fails against a theory that only excludes loop-free systems (S2g) and holds against one that includes integrated systems (S2f) |

### Caveats both checkers raise (all rated minor)

- Units are arbitrary state machines, not neurons, and "the same function" is exact equality, not approximation.
  The sources' appeal to universal approximation theorems is not formalized.
- Time is discrete; updates are synchronous and deterministic, from a fixed starting state; one output is read
  after each input.
- Dependence between units is judged over all joint states, including ones the system never reaches.
- `Integrated` is a property of a graph. It is not ϕ and is not claimed to imply ϕ > 0.
- The premises of S2e and S2f are met by any verdict with the stated properties, including ones that have nothing
  to do with causal structure. That makes the theorems more general than the argument, not less.
- An inference rule is any function of behaviour, whether or not an experiment could compute it.
- The unit counts in S1b, S1f and S1g do not count the complexity of the readout, which is a lookup table.
- S2c attaches a true experience to each physical system. Kleiner and Hoel's formalism has no such thing.
- In S2d the prediction and the inference are functions of the two parts of a dataset. The paper's are defined on
  whole datasets.

## What the proofs cannot tell us

- **Whether any system is conscious, or any theory right.** S2e and S2f say that a theory's verdict and a
  behaviour-based inference differ somewhere. They do not say which is wrong. "Falsified" is Kleiner and Hoel's
  word for the mismatch; whether a mismatch counts against the theory or against the inference is the dispute.
- **Whether evidence beyond behaviour exists or is admissible.** S2i shows the argument needs the premise that it
  does not. Tsuchiya and colleagues deny that premise and Herzog and colleagues defend it. Nothing in Lean bears
  on who is right.
- **Anything about ϕ.** Integrated information is not computed for any system. That feedforward systems have
  ϕ = 0 and that feedback gives ϕ > 0 are taken from Doerig et al. as properties a verdict might have. Whether
  IIT's verdicts have them, and in particular whether IIT would count the idle loop of S1h as making the system
  conscious, is not checked. An IIT proponent can say the loop forms its own small conscious entity and leaves
  the rest of the system as it was; the Lean has no way to express that.
- **Anything about neurons.** The twins are abstract. That a twin exists as a network of realistic neurons of
  reasonable size is not shown, and S1e says the size cannot stay bounded as the experiment lengthens.
- **Whether intervening inside the twin tells it apart from the original.** S1g covers interventions that both
  systems receive as inputs. Intervening on the twin's own units is Stage 3.
- **The full picture for units with memory.** Stage 3 shows that feed-forward circuits of bits match some
  machines forever and not others. It does not say exactly which machines, and it does not formalize the
  Krohn–Rhodes theorem.
- **What the two unread replies say.** Tsuchiya, Andrillon and Haun (2020) and Usher (2021) were not read in the
  original. S1g and S2i formalize descriptions of them by an abstract and by their opponents.

## Limits

- The statements are elementary. S2a to S2c, S2h and S2i are a few lines each, and S1a to S1e are textbook
  material in automata theory (a loop-free network is a definite, or finite-memory, machine). No claim of
  mathematical novelty is made. The prior-art search found no machine-checked version, which is a weaker claim.
- S2c′ and S2d′ say that two results in Kleiner and Hoel (2021), read literally, need a weaker conclusion or one
  more premise. Both are small. In each case the paper's own proof or explanation supports the reading that the
  Lean proves, so these are remarks about wording. The authors have not been asked.
- S1f contradicts the sentence "rapid plasticity negates the functional equivalence" only under the notion of
  equivalence used here: the same output after every input history, with the loop-free system free to carry
  state. O'Reilly-Shah et al. compare a mapping that changes over time with a static one. Their supplementary
  appendix, where the formal definitions and proofs are, was not obtained, so how far the two notions differ is
  judged from the main text.
- The statement check was done by language models. Both caught every planted error, which says they read
  carefully, not that they miss nothing.
- One AI session read the sources, wrote the statements and proofs, and wrote this report. No human has checked
  the Lean statements against the papers. The Lean kernel has checked the proofs.
- The author is an AI model, and the argument bears on whether behaviour could show an AI system to be conscious.

## Stage 3: units with memory

Statements locked 2026-11-23T19:03:05Z (commit `327ba92`), under Amendment 1. Only the first half of the issue's Stage 3 was done; intervening on the
twin's own units was not started.

### Answer

All six locked statements are proved, on the three standard axioms, and the build passes in CI
([run 45244866647](https://github.com/ejhong/aletheia-lab/actions/runs/45244866647), commit `34a5de8`).

In one sentence: once a unit may remember its own state, some machines can be built without feedback between
units for all time and others cannot, and which is which depends on how many states a unit may have.

### What follows from what (plain summary)

Stage 1 called a network loop-free when no unit depends on anything in a cycle, its own past included. Hanson and
Walker (2021) use a weaker notion, here called feedback-free: a unit may depend on its own past, as a flip-flop
does, but no two different units influence each other. Their example is a counter that counts to eight, built
from three flip-flops. They report Φ = 0 for that circuit, so for integrated information theory the weaker
notion is the one that matters, and the question is whether Stage 1's time limit survives under it. That Φ is
zero there is taken from them and not checked.

1. **A feedback-free network of small units can only tick in certain rhythms.** If every unit has at most k
   states, then under one repeated input the network ends up repeating itself with period (k!) to the power of
   the number of units (S3a). For two-state units that is a power of two.
2. **So a counter to three cannot be built from two-state units without feedback.** If a feedback-free network
   with at most k states per unit matches the counter modulo m forever, m divides a power of k! (S3b). With
   k = 2 and m = 3 that is impossible, however many units are used (S3b′).
3. **A counter to eight can.** Three two-state units, each depending on itself and the earlier ones, match the
   counter modulo 8 forever (S3c). This is Hanson and Walker's example, and it checks.
4. **Neither counter has a loop-free twin for all time** in Stage 1's strict sense (S3d), like the latch.
5. **With bigger units there is nothing to prove.** The counter modulo m is one unit with m states, and one unit
   has no feedback between units (S3e).

So the answer to "can the loops be removed for good?" has three layers. With no memory in the units: never, for
anything that remembers. With memory in arbitrarily large units: always, trivially. With memory in units of a
fixed size, such as bits: for some machines and not others. By S3b and a line of arithmetic, counting modulo a
number with a prime factor larger than the unit size is on the wrong side; only the case of three and bits is
stated as a theorem in Lean.

### Results table

Proofs in `lean/UnfoldingArgument/Results3.lean`.

| | Claim | Lean name | Premises | Status | Source |
|---|---|---|---|---|---|
| S3a | A feedback-free network with at most k states per unit, fed any inputs and then one input repeated, ends up repeating its outputs with period (k!)^(number of units) | `FeedbackFreeIsEventuallyPeriodic` | feedback-free; at most k states per unit | proved | the lab's |
| S3b | If such a network matches the counter modulo m at every horizon, m divides (k!)^(number of units) | `CounterTwinForcesDivisibility` | as S3a; agrees with the counter | proved | the lab's |
| S3b′ | No feedback-free network of two-state units matches the counter modulo 3 at every horizon | `CounterMod3HasNoBinaryFeedbackFreeTwin` | none | proved | the lab's; bears on Hanson and Walker 2021 |
| S3c | Some feedback-free network of three two-state units matches the counter modulo 8 at every horizon | `CounterMod8HasBinaryFeedbackFreeTwin` | none | proved | Hanson and Walker 2021, their example |
| S3d | For m ≥ 2, no loop-free network matches the counter modulo m at every horizon | `CounterHasNoLoopFreeTwin` | m ≥ 2 | proved | the lab's; Stage 1's S1c applied |
| S3e | The counter modulo m is feedback-free, with one unit of m states | `CounterIsOneUnitWithMemory` | none | proved | the lab's |

Non-vacuity: the premises of S3a and S3b are met by the witness of S3c, a feedback-free network of two-state
units that matches a counter.

### What this does to the earlier results

- **The reply in the last row of the replies table is now answered in part.** "Feed-forward circuits with memory
  match forever" is true of Hanson and Walker's counter to eight (S3c) and false, for binary units, of a counter
  to three (S3b′).
- **Their general sentence needs a reading.** They write that "any abstract deterministic finite-state automata
  (FSA) can be realized using a strictly feed-forward causal architecture comprised solely of simple elementary
  components". If "elementary components" means binary memory devices, as in their circuit, the sentence fails
  for the counter modulo 3, at the level of input-output behaviour. If it means the components the Krohn–Rhodes
  theorem actually uses, which as I understand it second-hand include larger units for machines that count
  modulo a number other than a power of two, the sentence stands, and then "feed-forward" is paid for in the
  size of the units. Krohn and Rhodes (1965) and Zeiger (1967) were not read, so the second reading is
  `unverified`.
- **For a theory that counts units,** this means the choice of what a unit is cannot be left open. The same
  counter modulo 3 is one unit without feedback, or several bits that must feed back on each other.
- **Stage 1's limit stands as stated** (S3d): in the strict sense, with no memory in the units, nothing that
  remembers has a twin for all time.

### Statement check

OpenAI `gpt-6.2-astra` and Google `gemini-4-neon`, 2026-11-23, three rounds, $3.65. Detail:
`statement-check/REPORT-3.md`; the history is at the end of Amendment 1.

- **Planted errors.** Two; both checkers called both divergent.
- **Statements.** All six `faithful` or `faithful_with_caveats` from both checkers in the first round. None was
  changed.
- **Definitions.** OpenAI rated the two definitions `divergent` in round 1 because my description called the
  counter a rendering of the paper's tollbooth. It is not: the paper's machine sends its whole state as output
  and this counter says only whether the count is 0. The Lean was kept, since a counter that reveals less makes
  the impossibility results stronger; the description was corrected, twice, and both checkers then rated it
  `faithful`.
- **Unresolved divergences.** None.
- **Caveats both raise (minor).** The counter's interface is the lab's own; "network" means finitely many units,
  updated together and deterministically; dependence is judged over all states, reachable or not.

### Limits of Stage 3

- The comparison is of input-output behaviour, and the counter's output is reduced to "is the count 0". Hanson
  and Walker realize an automaton state for state. That makes S3b′ stronger than it needs to be and S3c weaker
  than their circuit.
- S3a is proved for one repeated input after an arbitrary start. Nothing is proved about periodic inputs with a
  longer pattern, though the same argument should cover them.
- The period (k!)^n is an upper bound in the sense of divisibility; it is not claimed to be the least.
- Nothing here is new to automata theory, where the groups inside a machine are known to be the obstruction to
  taking it apart. The prior-art search did not look for this result specifically.
- No ϕ is computed. That a feedback-free network has ϕ = 0, as Hanson and Walker report for their circuit, is
  taken from them.

## Amendments

- **Amendment 1 (2026-11-23): Stage 3, units with memory.** Six statements in a new file, with their own
  statement check and lock, written and pushed before the check ran. It covers half of the issue's Stage 3; the
  other half, intervening on the twin's own units, was not started. Nothing in Stages 0 to 2 was changed by it.

Everything the first statement check changed was changed before the first lock, and is listed in `protocol.md`.

Departures from the lab's process, both at Eugene's direction and recorded in `log.md`: the question was run in
one session from Stage 0 to Stage 2 without waiting at the gates between stages; and the lab's $50 daily
spending cap was exceeded.

## Spending

$27.06 in all, all on statement checks (`SPENDING.md`). Stages 0 to 2: $23.41 of a $40 budget (OpenAI $6.36,
Google $17.05). Stage 3: $3.65 of $15 (OpenAI $1.30, Google $2.35).

## Who did the work

AI did this work. Claude Fable 5.2 (Anthropic) searched for prior art, read the sources, wrote the definitions,
statements, proofs and this report, on 2026-11-23. A sub-agent of the same model ran the prior-art search.
OpenAI `gpt-6.2-astra` and Google `gemini-4-neon` checked the statements on the same day. For Stage 3, two
sub-agents did mechanical work: Claude Haiku 5.5 pulled verbatim passages from Hanson and Walker, which were then
checked mechanically against the text, and Claude Opus 5.5 added a mode to the checking script. The Lean 4 kernel
(v4.35.0, with Mathlib at commit `56a0058`) checked the proofs. Eugene directed it: he chose the question and
said to run it end to end.

## What this means

The unfolding argument says that feedback loops cannot be what makes a system conscious, because any system with
loops can be swapped for one without them that behaves the same. A proof checker has now been through it. The swap
is real, but only for an experiment of fixed length: the loop-free copy needs one more part for every further
moment it has to keep up, and no finite copy keeps up forever, even with a system that does nothing but remember
one bit. Learning does not change this. The swap in the other direction is easy and lasts forever: bolt a loop
that does nothing onto any system. So if a theory says loops are *enough* for consciousness, the argument bites
however long you watch. If it says only that loops are *needed*, the argument bites for any experiment of fixed
length and not beyond. Either way the argument has force only if what a system does is all the evidence there is
about what it feels. The proofs show that this one assumption carries the whole conclusion, and that with it the
same reasoning applies to every theory that looks inside, not just to theories about loops. Whether the
assumption is true is not a question a proof can answer.

Stage 3 adds a twist about what counts as a part. If each part may remember its own state, as a memory bit does,
then some machines can be built with no feedback between parts and run forever: a counter to eight is one. A
counter to three is not; with two-state parts it cannot be done at any size. Let a part have three states and it
is trivial. So "can the loops be removed?" has no answer until one says how big a part may be.
