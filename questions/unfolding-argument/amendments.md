# Amendments

Changes after the lock, dated, each with its reason, written before the changed part runs.

## Amendment 1 (2026-11-23): Stage 3, units with memory

**What changed.** After Stages 0 to 2 were merged, Eugene asked whether Stage 3 was worthwhile. I recommended
half of it, and he said to proceed. This amendment adds that half: what a feed-forward network can match for all
time when its units may keep their own state. The other half of Stage 3 in the issue, intervening on the twin's
own units, is not started. Written before the statement check below is run and before anything in it is proved.

**Budget.** $15 for this stage, as proposed to Eugene. With the $23.41 already spent that stays inside the $40
he approved for #66 today. Expected cost of the statement check: $4 to $8.

**Why.** Stage 1 proved that a `LoopFree` network cannot match a latch for all time (S1c to S1e). In a `LoopFree`
network no unit depends on its own past. Hanson and Walker (2021) use a weaker notion of feed-forward, in which
"each component depends solely on itself or earlier components", and say that "any abstract deterministic
finite-state automata (FSA) can be realized using a strictly feed-forward causal architecture comprised solely of
simple elementary components". Their example is a counter modulo 8 built from three binary flip-flops. If that
sentence holds for binary components in general, the limit proved in Stage 1 says nothing about integrated
information theory, whose own notion of a system without integration allows such units. Stage 1's S1i covered
only the degenerate case of one arbitrarily complex unit.

**My expectation, written down before the check.** A feedback-free network of units with at most k states can
only settle into cycles whose length divides a power of k!, so a counter modulo 3 has no feedback-free twin made
of two-state units. I reached this by an elementary period argument, not from the Krohn–Rhodes literature, which
I have not read. Trial proofs of all six statements compile (`explore/Stage3Sketch.lean`); that is exploration
and not a finding.

**Statements** (drafted in `statement-check/Statement3.draft.lean`; the file moves to
`lean/UnfoldingArgument/Statement3.lean` in the commit that locks it; passages in `statement-check/passages.md`).

| Name | Gloss | Source |
|---|---|---|
| D19 `UnitsHaveAtMost` | Every unit has finitely many states, at most k | Hanson and Walker 2021 ("binary memory storage devices (bits)") |
| D20 `counter` | The counter modulo m: one unit, advances on input `true`, output says whether it is at 0 | Hanson and Walker 2021 ("a mod-eight counter") |
| S3a `FeedbackFreeIsEventuallyPeriodic` | A feedback-free network with at most k states per unit, fed one input over and over, ends up repeating with period (k!)^(number of units) | the lab's |
| S3b `CounterTwinForcesDivisibility` | If such a network matches the counter modulo m forever, m divides (k!)^(number of units) | the lab's |
| S3b′ `CounterMod3HasNoBinaryFeedbackFreeTwin` | No feedback-free network of two-state units matches the counter modulo 3 forever | the lab's; against Hanson and Walker's general sentence read with binary components |
| S3c `CounterMod8HasBinaryFeedbackFreeTwin` | Three two-state units with no feedback between them match the counter modulo 8 forever | Hanson and Walker 2021, their example |
| S3d `CounterHasNoLoopFreeTwin` | No loop-free network matches a counter modulo m ≥ 2 forever | the lab's; Stage 1 applied to the counter |
| S3e `CounterIsOneUnitWithMemory` | The counter modulo m is itself feedback-free: one unit with m states | the lab's |

**Sources.** Hanson and Walker (2021), journal text from Europe PMC, already in the manifest. For this stage the
passages on the tollbooth, the flip-flops and the feed-forward circuit were pulled out by a sub-agent (Claude
Haiku 5.5, verbatim with line numbers), then read by me in those extracts and checked mechanically against the
text by `check_quotes.py`. The paper's Methods are in a supplement that was not obtained. Krohn and Rhodes (1965)
and Zeiger (1967) were not read; nothing here is claimed about what the Krohn–Rhodes theorem says beyond Hanson
and Walker's own sentence.

**Method.** As in Stages 0 to 2.

1. Statement check with OpenAI `gpt-6.2-astra` and Google `gemini-4-neon`: `statement-check/run.py --stage 3`,
   items in `items3.json`, outputs in `out3/`, report in `REPORT-3.md`. Two planted errors are mixed in (the
   divisibility in S3b reversed; three-state units in place of two-state in S3b′). All six statements are the
   lab's own and are compared with `PROMPT_B_OWN`; the two definitions are compared with the standard prompt.
   The `--stage 3` mode of `run.py` was added by a sub-agent (Claude Opus 5.5) and checked by me: the default
   mode's output is unchanged.
2. If a real item is rated `divergent`, either the statement or its description is rewritten and re-checked, or
   the divergence is accepted and carried into the results. Each case is recorded below before the lock.
3. Lock `lean/UnfoldingArgument/Statement3.lean` with `scripts/lock.py --statement`, in its own commit.
4. Proofs in `lean/UnfoldingArgument/Results3.lean`, with exactly the locked types; a non-vacuity instance for
   S3a and S3b (S3c supplies one: a feedback-free network of two-state units that matches a counter); the axiom
   audit on every theorem; a Stage 3 section in `RESULTS.md`.

**What would count.** For: CI builds the proofs with standard axioms only. Then, within this model, whether a
finite machine has a feed-forward twin for all time depends on how many states a unit may have, and the general
sentence in Hanson and Walker fails for binary components. Against: a statement cannot be proved as written, or a
checker shows that "feed-forward with binary components" is not a fair reading of the paper; either is reported.
It would not show that the Krohn–Rhodes theorem is wrong, and it says nothing about ϕ.

**Known weaknesses.** The comparison is of input-output behaviour, with the output reduced to "is the count 0".
The paper's claim is about realizing an automaton, state for state. A counter modulo 3 that also had to expose
its state would be no easier to build, so the negative result is not weakened by this, but the positive one
(S3c) is about less than the paper's circuit does. "Elementary component" is read as "unit with at most k
states"; the Krohn–Rhodes theorem, as I understand it second-hand, allows larger units for some machines, and if
so Hanson and Walker's sentence is true of those and S3b′ is a remark about what "elementary" has to mean.
