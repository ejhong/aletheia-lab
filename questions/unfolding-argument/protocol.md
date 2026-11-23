# Machine-check the unfolding argument

Issue: #66 · Lane: proof · Budget: $40 (Stages 0–2: statement checks and any paid sources)

## Question

What does the unfolding argument prove, and from which premises? Concretely: which of the twenty statements
S1a–S1i and S2a–S2i in `lean/UnfoldingArgument/Statement.lean` are theorems of Lean 4 with the pinned Mathlib,
using no axioms beyond Lean's standard three?

This settles what follows from what. It does not settle which systems are conscious, and it does not compute
integrated information for any system.

## Why it matters

The argument (Doerig, Schurger, Hess and Herzog 2019) says that any system with feedback loops can be replaced by
one without them that behaves the same, so a theory that ties consciousness to feedback or to internal causal
structure is false or outside science. It bears on whether any test of behaviour could tell us if an animal, a
patient or an AI system is conscious. The dispute has a mathematical core and contested assumptions: a finite time
horizon, fixed weights, evidence limited to behaviour, and the size of the replacement. A paper from 2026
(O'Reilly-Shah, Selvitella and Schurger) claims that plasticity breaks the equivalence.

Prior art, searched on 2026-11-23 (Lean Zulip public channels, GitHub code and repository search, web search,
OpenAlex): no machine-checked version of the unfolding argument or of Kleiner and Hoel's substitution argument was
found. The closest items found are a Lean 4 formalization of integrated information theory itself (Mayeux 2026,
Zenodo; not read) and a Lean 4 proof of the Krohn–Rhodes theorem (not read). Queries are in `log.md`.

Aletheia link: none known. The lab files the result with the atlas; it does not grade any claim.

## Data and sources

No datasets. Sources are papers; the copies read are in `MANIFEST.md`, and the passages each statement is tied to
are quoted in `statement-check/passages.md`. `statement-check/check_quotes.py` compares every quotation with the
extracted text of its source.

Two of the replies were not read in the original, because they are paywalled: Tsuchiya, Andrillon and Haun (2020)
and Usher (2021). What they argue is taken from Usher's abstract and from Herzog, Schurger and Doerig (2022), who
are their opponents. Statements tied to them say so.

The one software dependency is Mathlib (Apache-2.0), pinned in `lean/lakefile.toml` to commit
`56a005855ea17e0b0958f73ec801ae140b0a1679`, with every transitive dependency pinned in `lean/lake-manifest.json`
and the toolchain in `lean/lean-toolchain` (Lean v4.35.0).

## Statements and their sources

Definitions (D) and statements (S). The Lean text is authoritative; the gloss is a reading aid.

| Name in `Statement.lean` | Gloss | Source passage |
|---|---|---|
| D1 `Network` | Finitely many units, each with a state; discrete time; each unit updates from the current states and the input; a readout | Doerig 2019, pp. 51–52; Herzog 2022, p. 10 |
| D2 `response` | Input-output behaviour: the output after each finite input sequence | Doerig 2019, p. 51 |
| D3, D4 `AgreeUpTo`, `AgreeAlways` | Same behaviour for T steps; at every horizon | Doerig 2019, p. 53 (P2, P3) |
| D5 `DependsOn`, `Influences` | The causal graph: whose update depends on whose state | Doerig 2019, p. 51 |
| D6, D7 `LoopFree`, `Recurrent` | Feedforward: no directed cycle of any length. Recurrent: some cycle | Doerig 2019, p. 51 |
| D8 `Integrated` | Every unit on a feedback loop with every unit. The lab's stand-in; not ϕ | Doerig 2019, p. 52 |
| D9 `FeedbackFree` | No feedback between different units; a unit may have memory | Hanson and Walker 2021 |
| D10 `size` | Number of units | Doerig 2019, p. 54 |
| D11 `unfold` | Unrolling through time: T copies of the network | Herzog 2022, p. 10; Doerig 2019, p. 52 |
| D12 `latch` | One unit, one bit, set for good by an input | the lab's example |
| D13 `PlasticSystem` | Activity and weights; the weights change by a learning rule | O'Reilly-Shah 2026, "Proofs" |
| D14 `perturbedResponse` | Responses when the experimenter also intervenes on the internal state | Doerig 2019, p. 51 |
| D15–D18 `Testing`, `FalsificationAt`, `SubstitutionAt`, `UniversalSubstitution` | Kleiner and Hoel's setup: datasets, predictions, inference from the report part of a dataset; a falsification at a dataset that can arise | Kleiner and Hoel 2021, §§2.1–2.4, Defs 2.1, 3.1, 3.2 |
| S1a `UnfoldingAtFiniteHorizon` | The unfolded network is loop-free, matches for T steps, and has T times the units | Doerig 2019, pp. 52–53 (P2); Herzog 2022, p. 10 |
| S1b `EveryBehaviourHasLoopFreeRealizer` | Any input-output function over T steps has a loop-free realizer with T units | Doerig 2019, p. 51; Herzog 2022, p. 11 |
| S1c `LoopFreeHasFiniteMemory` | A loop-free network with d units forgets everything older than d steps | O'Reilly-Shah 2026, "Proofs" |
| S1d `LatchHasNoLoopFreeTwin` | The latch is recurrent and has no loop-free twin at every horizon | the lab's; against P2 read without a time limit |
| S1e `LatchTwinNeedsHorizonManyNodes` | A loop-free twin of the latch for T steps has at least T units | the lab's; Doerig 2019, p. 54; Herzog 2022, p. 10 |
| S1f `PlasticSystemHasLoopFreeTwin` | A learning system has a loop-free twin with T units for T steps | O'Reilly-Shah 2026, abstract and "Proofs" |
| S1g `PerturbedNetworkHasLoopFreeTwin` | So does a network probed from inside, if the probe counts as input | Doerig 2019, p. 51; Usher 2021, abstract |
| S1h `EveryNetworkHasIntegratedTwin` | Every network has an integrated twin at every horizon, with one more unit | Doerig 2019, pp. 52–53 ("vice-versa") and Appendix A |
| S1i `EveryNetworkHasSingleUnitTwin` | If a unit may have memory, a single unit matches any network forever | the lab's; Hanson and Walker 2021 |
| S2a `SubstitutionGivesFalsification` | A substitution gives a falsification | Kleiner and Hoel 2021, Lemmas 3.3 and 3.5 |
| S2b `UniversalSubstitutionFalsifiesEveryReport` | A universal substitution gives one for every report | Kleiner and Hoel 2021, Prop. 3.6 |
| S2c `EveryInferenceWrongOrTheoryWrong` | Then every report is wrong about at least one system, or some prediction is wrong | Kleiner and Hoel 2021, Prop. 3.7 |
| S2c′ `SomeInferenceCanStillBeRight` | It cannot be read more strongly: with every prediction right, some inference can still be right | the lab's; about Prop. 3.7 |
| S2d `StrictDependenceLeavesNothingToTest` | Under strict dependence, and if every conceivable report already occurs, experiments add nothing | Kleiner and Hoel 2021, Theorem 4.3 and its proof |
| S2d′ `StrictDependenceCanStillBeTested` | Without that second assumption the conclusion fails | the lab's; about Theorem 4.3 as printed |
| S2e `UnfoldingArgumentAtFiniteHorizon` | A theory that excludes loop-free systems disagrees with every rule that infers consciousness from T steps of behaviour | Doerig 2019, p. 53 (P1–P4, C) |
| S2f `FoldingArgumentAtEveryHorizon` | A theory that counts every integrated system as conscious disagrees with every rule that infers from the whole behaviour | Doerig 2019, pp. 52–53 and Appendix A |
| S2g `LoopFreeExclusionSurvivesUnboundedHorizon` | A theory that only excludes loop-free systems can agree with a rule that uses behaviour over unbounded time | the lab's |
| S2h `SparedIffDeterminedByBehaviour` | The argument spares exactly the theories whose verdict depends on behaviour alone | the lab's; Kleiner and Hoel 2021, §§3–4 |
| S2i `FurtherEvidenceRemovesMismatch` | If evidence beyond behaviour is admitted, nothing forces a mismatch | Herzog 2022, pp. 4 and 9 (reporting Tsuchiya 2020); Kleiner and Hoel 2021, §5.2 |

How the premises of Doerig et al. (2019, p. 53) appear in the Lean:

- **P1, P3, P4** (science relies on measurements; systems with the same input-output function cannot be told
  apart; brain activity cannot be used as an indicator in advance). Together they say that evidence about
  consciousness is a function of input-output behaviour. In S2e and S2f this is the type of the inference rule:
  a function from behaviour to a verdict. S2i drops it.
- **P2** (every recurrent system has a feedforward twin, and vice versa). Not assumed. S1a and S1b prove the first
  half at a finite horizon; S1d and S1e give its limits; S1h proves the second half at every horizon.
- **A causal structure theory** is a verdict on networks with one or both of: no loop-free network is conscious
  (S2e); every integrated network is conscious (S2f).
- **The conclusion** is rendered as Kleiner and Hoel's falsification: the theory's verdict and the inferred
  verdict differ on some system. "Outside the realm of science" is not a formal statement here; S2c and S2h are
  the nearest formal content.

## Method

### Stage 0: statements, then the statement check, then the lock

1. Write the definitions and statements as `def … : Prop` in `lean/UnfoldingArgument/Statement.lean`. The file
   must compile against the pinned library.
2. Exploration is allowed before the lock, in `explore/`, to make sure no statement is false as written. Nothing
   there is a finding.
3. Run the statement check, `statement-check/run.py`:
   - Checkers: OpenAI `gpt-6.2-astra` (reasoning effort high) and Google `gemini-4-neon`. xAI `grok-4.7` is the
     tie-breaker, run only if the two disagree on whether an item is `divergent` and the lab cannot settle it by
     reading the two reports.
   - Phase A, blind: the checker gets the notation key, all the definitions and one target, with comments removed
     and every name the lab chose (definitions, structure fields, bound variables such as `conscious`) replaced
     by a neutral label. It translates the target into English.
   - Phase B: the same checker is shown the source passage(s) and the lab's claim about the target, and returns a
     verdict (`faithful`, `faithful_with_caveats`, `divergent`) with each divergence rated major or minor. Where
     the target is the lab's own statement and not a rendering of a passage, the claim says so, and the checker
     is asked two things: whether the Lean says what the lab's description says, and whether the description
     reports the passages accurately.
   - Planted wrong items (`statement-check/items.json`, "decoys") are mixed in: four in round 1, two more in
     round 2. A planted error is caught when the verdict is `divergent`.
   - The check may be run in rounds. Each round's inputs and raw outputs are kept (`statement-check/round1/` and
     so on; `statement-check/out/` is the round that the locked statements went through).
   - The exact prompts are the constants `PROMPT_A`, `PROMPT_B` and `PROMPT_B_OWN` in `run.py`. The summary is
     `statement-check/REPORT.md`.
4. Act on the report before locking:
   - A major divergence on a real item is fixed in `Statement.lean` (and the item re-checked), or accepted with
     the reason written in the outcome section below.
   - If a checker misses a planted error, its `faithful` verdicts are not relied on; say so in `RESULTS.md`.
   - Unresolved divergences are carried into `RESULTS.md`.
5. `python scripts/lock.py questions/unfolding-argument --statement …`, committed on its own, before any proof
   file exists under `lean/`. Eugene asked on 2026-11-23 for the question to be run end to end in one session, so
   the gates between stages are reported in `log.md` and not waited on.

### Stage 1: the mathematical core

6. Prove S1a–S1i in `lean/UnfoldingArgument/Results.lean` as `theorem name : Statement.Name`. Where a proof is a
   restatement of a Mathlib theorem, the results table names it.
7. Non-vacuity, in `lean/UnfoldingArgument/NonVacuity.lean`: for each statement that starts from assumptions, an
   instance showing the assumptions can hold together. In particular: a loop-free network exists (S1c); a
   loop-free network that matches the latch for T steps exists, with exactly T units, so the bound in S1e is met
   (S1e).

### Stage 2: the falsification argument and the replies

8. Prove S2a–S2i (with S2c′ and S2d′) in `lean/UnfoldingArgument/Results2.lean` in the same way. Non-vacuity: a setup with a substitution (S2a) and with a universal
   substitution (S2b, S2c); a setup satisfying the assumptions of S2d with a falsification on both sides; a
   verdict satisfying the assumptions of S2e, and one satisfying those of S2f.
9. Audit: `#assert_standard_axioms` on every headline theorem, inside the build. CI
   (`.github/workflows/lean.yml`) builds with warnings as errors and rejects `sorry`, `admit`, `native_decide`
   and new `axiom` declarations.
10. Write `RESULTS.md`: a table of claim / Lean name / premises required / status / source locator; a table of
    the replies, saying for each which premise it denies and what the argument still yields without it; the
    statement check outcome including every unresolved divergence; amendments; models, vendors and dates; and a
    plain summary of what follows from what, with no verdict on any theory of consciousness.

### Not in this protocol

Stage 3 of the issue: Hanson and Walker's version over finite automata with the Krohn–Rhodes decomposition into
simple components, and intervention on the twin's own units as a second kind of evidence. Kleiner and Hoel's
Theorem 3.10 (independence implies a universal substitution) is also not stated here. Anything added later goes in
a new statement file with its own statement check, entered in `amendments.md` and locked before any proof.

## What would count

- **For** a statement: CI builds its proof with standard axioms only. Conclusion: the statement holds as
  formalized, under the premises in its hypotheses, to the extent the statement check found it faithful.
- **Against** a statement: a Lean proof of its negation, or a counterexample to it. Conclusion: the formalized
  claim is false; report it, and say whether the fault is in the argument or in our formalization.
- **Inconclusive:** no proof and no refutation within the budget; or a major statement-check divergence that
  could not be resolved, in which case the theorem is reported as proved but not as a formalization of the source.

What a full set of proofs would and would not support, written before any of them is in the build:

- It would support: the replacement of a recurrent system by a loop-free one is sound at any fixed finite horizon,
  with or without learning, and with internal probes counted as input; it is not available for unbounded time,
  and its cost grows with the horizon; the opposite replacement, loop-free by integrated, is available for
  unbounded time at the cost of one unit. So the replies that appeal to time, size or plasticity bear on theories
  that make feedback *necessary* for consciousness, and not on theories that make it *sufficient*.
- It would not show that any theory of consciousness is true or false. The falsification statements say that a
  theory's verdict and a behaviour-based inference differ somewhere; they do not say which is wrong.

## Known weaknesses

- **No ϕ.** Integrated information is not computed anywhere. "Loop-free" and "integrated" are graph properties of
  a network. Doerig et al. say that ϕ is zero for feedforward systems and positive for recurrent ones; the Lean
  takes verdicts with those properties as hypotheses and does not check that IIT has them.
- **Units are abstract.** A unit is any state machine and the readout is any function of the joint state. The
  sources talk about neurons with weights and about approximation. Here equivalence is exact. One consequence:
  S1b's twin keeps the inputs in a delay line and does all the work in the readout, a lookup table. S1a's twin
  reuses the original's units, at T times the count.
- **Dependence is counterfactual.** "Unit n depends on unit m" is judged over all joint states, reachable or not.
  IIT also perturbs a system into all of its states, but a reader may want dependence along the actual run.
- **Two notions of feedforward.** `LoopFree` forbids a unit from depending on its own past, as in a layered
  network. `FeedbackFree` allows it, as in Hanson and Walker's flip-flop circuits. The limits S1c–S1e hold for
  the first only; S1i shows they fail for the second if units may be arbitrarily complex. The interesting middle
  case, simple units with memory (Krohn–Rhodes), is Stage 3.
- **Discrete time, deterministic, one output per step.** No noise, no continuous dynamics.
- **Two replies were not read in the original** (Tsuchiya et al. 2020; Usher 2021). The statements tied to them
  (S1g, S2i) formalize a description of the reply by its opponents or by an abstract.
- **Some statements are easy.** S2a–S2c, S2h and S2i are a few lines each. That is itself part of the answer to
  "what does the argument prove", but nobody should take their proofs as an achievement.
- **The statement check is done by language models.** It can miss errors; the planted errors estimate how often.
- **The author has a stake.** The statements and proofs were written by an AI model, and the argument bears on
  whether behaviour could show an AI system to be conscious. The check by other vendors' models is the control.

## Statement check outcome and accepted divergences

Run on 2026-11-23 with OpenAI `gpt-6.2-astra` and Google `gemini-4-neon`, in three rounds. Full detail:
`statement-check/REPORT.md` (final), `statement-check/round1/` and `statement-check/round2/`. The tie-breaker was
not run. Cost: $23.41.

**Planted errors.** Both checkers returned `divergent` on all six: four in round 1, two more in round 2.

**Changes made because of the check.**

- Round 1 found (both checkers) that Proposition 3.7's "every single inference operation is wrong" is stronger
  than what S2c says, which is that every report is wrong about at least one system. OpenAI gave a setup in which
  the stronger reading fails. S2c's claim now states the weaker reading, and the setup became a statement of its
  own, S2c′.
- Round 1 found (OpenAI) that a falsification was not restricted to datasets that can arise, as Definition 2.1
  requires. `FalsificationAt` now includes it, and S2a and S2b are stated through it.
- Round 1 found (both) that my description of S1f was wrong: O'Reilly-Shah et al. concede finite-horizon
  equivalence for fixed parameters only, so S1f is not "the equivalence they do not refute". It contradicts their
  claim, under one notion of equivalence and not under theirs. The description now says which.
- Round 1 found (both) that S1b was tied to the wrong sentence: the one quoted is about recurrent networks. The
  passage on feedforward networks and the caption of Fig. 2 were added (P-D51c).
- Round 1 found (Google) that `FeedbackFree` captures only the ordering condition in Hanson and Walker's
  architecture, not their requirement that the components be simple. The claim now says only that.
- Round 1 found (OpenAI) that `unfold` is a pipeline in which every copy runs at every step, where the passages
  describe copy k as evaluated once, for step k. The definition is unchanged; it is now described as a real-time
  variant, with the differences listed.
- Round 1 found (OpenAI) that `PlasticSystem` allows a learning rule that changes nothing. Unchanged; the claim
  now says the class includes plastic systems, not that it is exactly them. Round 2 found (OpenAI) that even
  "includes every system with plasticity" claimed too much; the description now says the class is offered as a
  model of plasticity and that nothing shows every plastic system has this form.
- After round 1 the lab's own statements were marked as such, and compared with a prompt that asks whether the
  Lean says what the description says and whether the description reports the passages accurately. In round 1
  the standard prompt had counted "the passage does not assert this" as a major divergence for them.
- Round 2 found (OpenAI) that my description of S1h called agreement on every finite history a strengthening of
  P2, which has no time limit to strengthen. Corrected; checked again in round 3.

**Final verdicts.** Of 26 real items, both checkers gave `faithful` or `faithful_with_caveats` on 24. The
exceptions and the decisions:

| Item | Divergence | Decision |
|---|---|---|
| S1a `UnfoldingAtFiniteHorizon` | OpenAI: `divergent`. Premise P2 states no time limit; S1a gives, for each T, a twin that matches for T steps only. "If N computes a running OR", the T-layer twin differs from it on a longer input. Google: `faithful_with_caveats`, with the same point rated minor. | Accepted and carried into `RESULTS.md`. The divergence is the finding: P2 as printed is not what can be proved. S1a is the provable form, S1d says the printed form is false, and the checker's running OR is the latch of S1d. |
| S2e `UnfoldingArgumentAtFiniteHorizon` | OpenAI: `divergent`, for the same reason: the passage speaks of identical input-output functions without a time bound, and at each fixed T the Lean lets the inference see only T steps. Google: `faithful_with_caveats`. | Accepted and carried into `RESULTS.md`. S2e is the argument in the form the mathematics supports. S2g shows that the form without a time bound fails for a theory that only excludes loop-free systems, and S2f gives the form that does hold without a time bound. |

**Caveats both checkers raise on most items** (all rated minor, all carried into `RESULTS.md`): units are arbitrary
state machines and not neurons, and equivalence is exact, not approximate; time is discrete, updates are
synchronous and deterministic, with a fixed starting state; dependence between units is judged over all joint
states, including ones the system never reaches; `Integrated` is a property of a graph and is not ϕ; a verdict is
any predicate with the stated properties, so the hypotheses of S2e and S2f are satisfied by "theories" that have
nothing to do with causal structure; an inference rule is any function of behaviour, whether or not an experiment
could compute it; the unit counts in S1b, S1f and S1g do not count the complexity of the readout.
