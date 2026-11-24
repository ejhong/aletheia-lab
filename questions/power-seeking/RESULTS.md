# Results — Do the theorems show that capable AI must seek power? (#67)

- **Question:** #67, `lane:proof`.
- **Plan and statements locked:** 2026-11-24T17:43:54Z (`protocol.lock`, commit `fa7ffe3`), before the proofs were committed. Neither has changed since.
- **Build:** `lake build --wfail`, Lean v4.35.0, Mathlib `56a005855ea17e0b0958f73ec801ae140b0a1679`. No errors, no warnings, no `sorry`. All 14 theorems depend on Lean's three standard axioms only. Rebuilt from a clean copy during the check.
- **Statement check:** done on 24 November 2026, after the lock, by Anthropic's models (`statement-check/`). It is the reason this report was rewritten.
- **Who did the work:** AI did. Antigravity (Google DeepMind) wrote the statements and the proofs. Claude Fable 5.2 (Anthropic), with Claude Opus 5.5 sub-agents, rebuilt the proofs, checked the statements and the sources, and wrote this corrected report. Eugene Jhong directed both. No specialist has reviewed it.

## Answer

**No, and the authors of the theorems say so themselves. This study adds less to that answer than its first report claimed.**

The proofs are correct. Every one of the 14 statements is proved, and the proof checker accepts them. The trouble is in what the statements say. A statement check by a second company's models, which the plan left for later, found that only six of the 14 say what a published source says. Three are simplified versions. Five are small examples that do not carry the conclusions drawn from them.

What stands:

- **The expected-utility theorem** (S1a) is the real one, in full: preferences over gambles that are complete, transitive, independent and continuous can be scored by an expected utility, unique up to scale and shift. It needs all four conditions.
- **"Acts as if maximising some utility" is empty by itself** (S1d). Any fixed way of behaving maximises a utility defined over whole histories. This is Rohin Shah's 2018 observation, checked.
- **The counting lemmas behind "retargetable decision-makers tend to seek power"** (S2a, S2b) are the paper's own.
- **The lemma behind "optimal policies tend to seek power"** (S2c) is proved for finite sets of options and finitely many reward functions: if one set of options contains a relabelled copy of another, then across the relabellings of any spread of rewards, the larger set is worth more at least as often as less.
- **A small case of the clash at the centre of the shutdown problem** (S3c): an agent with complete, transitive preferences that prefers better to worse among short lives and among long ones must strictly prefer some short life to some long one, or the reverse.

What does not stand, from the first report:

- **"Dropping completeness stops money pumps dead."** The statement behind this (S1c) does not test it. Its "no money pump" clause follows from transitivity alone, and a complete preference passes the same test. The money pump that is actually in dispute works by trading across the gaps in an incomplete preference, and the statement's definition of a trade rules those trades out. The claim was credited to Johan Gustafsson's book, whose third chapter argues the opposite. Whether incomplete preferences can be exploited is a live dispute, with Gustafsson on one side and Thornley and Petersen on the other. Nothing here settles it.
- **"Power-seeking needs reward symmetry and optimality; drop either and it fails."** The three "counterexamples" (S2d, S2e, S2f) drop no premise of the theorems. The theorem never assumed a symmetric spread of rewards; it is a statement about most relabellings of any spread, and the paper itself points out that some spreads favour the smaller set. The "non-optimal policy" in S2e is an unconstrained function, and a constant satisfies it. None of the three involves a decision process or a policy; they are sets of three vectors.
- **"Expected-utility maximisation alone does not force shutdown resistance."** S3b shows that if staying on and being shut down are worth exactly the same, and meddling with the button costs anything, the agent leaves the button alone. The equal worth is assumed. Building an agent for which it holds is the hard part, and the paper cited for it (Soares and others, 2015) goes on to show two ways the approach fails and concludes that "a corrigible solution to the shutdown problem does not yet exist".
- **"Dropping completeness resolves the shutdown problem."** S3d shows that a preference with no strict ranking between short and long lives can exist, on four points. It does not show that an agent holding one stays willing to be shut down.
- **"All three arguments share the exact same logical shape."** They do not, once the counterexamples are set aside.
- **"Proves the exact core of Theorem 6.13."** S2c is a special case of Lemma E.24 of the 2021 paper. Theorem 6.13 is a different result, about where policies that maximise average reward end up.

What the authors say about their own theorems:

- Turner and others (2021): "We make no claims about when large-scale AI power-seeking behavior could become plausible", and "Our results do not mathematically prove that hypothetical superintelligent AI agents will seek power."
- Turner and Tadepalli (2022): "Our results do not prove that we will build unaligned AI agents which seek power over the world."
- They also say what they do expect. The 2021 paper: "Average-optimal agents would generally stop us from deactivating them, if physically possible." The 2022 paper: "Our theory suggests that when RL training processes become sufficiently advanced, the trained agents will tend to seek power over the world."

So the first report's headline answered a claim that the cited papers do not make.

## The fourteen statements

"Same" means the statement is the source's. "Special case" means it is the source's result in a narrower setting. "Simplified" means it keeps the idea and loses the substance. "Example only" means it exhibits one small object and does not support the conclusion first drawn from it.

### Coherence

| | What the statement says | Source | Standing |
|---|---|---|---|
| S1a | Complete, transitive, independent, continuous preferences over lotteries on a finite set have an expected-utility representation, unique up to positive scale and shift. | von Neumann and Morgenstern, *Theory of Games and Economic Behavior*, §3.6 and the Appendix of the second edition (1947), in the later four-axiom form | Same |
| S1b | If each paid trade round a cycle of three is accepted, the agent ends where it began with less money. | The plain money pump. Gustafsson (2022), p. 3, grants that foresight blocks this version and builds stronger ones | Simplified |
| S1c | Transitive preferences with gaps exist that have no losing chain of preferred trades. | None. See above | Example only |
| S1d | Any deterministic policy maximises some utility over histories. | Shah (2018), "Coherence arguments do not entail goal-directed behavior" | Same |

### Power-seeking

| | What the statement says | Source | Standing |
|---|---|---|---|
| S2a | If one relabelling turns every parameter favouring A into one favouring B, then in each family of relabellings at least as many favour B. | Turner and Tadepalli (2022), Prop. 3.4 | Same |
| S2b | With n such relabellings that do not overlap, at least n times as many. | Turner and Tadepalli (2022), Thm. 3.6 | Same |
| S2c | If a set of options contains a relabelled copy of another, it is worth more at least as often as less across the relabellings of any finite spread of rewards; it is worth at least as much whenever the spread is unchanged by the relabelling; and the reverse fails when it has a further option that is sometimes strictly best. | Turner and others (2021), Lemma E.24; with Lemma E.51 this is Prop. 6.12 at discount 1 | Special case. No decision process, policy or discounting appears in the statement |
| S2d | Some spread of rewards favours the smaller set. | The paper says so (p. 5: one distribution "even gives maximal POWER" to the terminal state) | Example only |
| S2e | A function that always answers "the smaller set" exists. | Turner and Tadepalli, §6.2, put decision-makers that are not retargetable outside their results | Example only |
| S2f | Adding an option that is never strictly best changes nothing. | Built into the paper's definitions (non-dominated options, Def. 3.6) | Example only |

### Shutdown

| | What the statement says | Source | Standing |
|---|---|---|---|
| S3a | In a three-row table of payoffs (leave the button, block it, press it), blocking pays when running is worth more and blocking is cheap; pressing pays when shutdown is worth more and pressing is cheap; neither pays at every small cost only if the two are worth the same. | Echoes Soares and others (2015), eq. 10 and note 5, and Thornley's First Theorem (2025, §7). Neither theorem | Simplified |
| S3b | If the two are worth the same and meddling costs anything, leaving the button alone is best. | Soares and others (2015), §3, with the indifference assumed | Simplified |
| S3c | Complete, transitive preferences that rank better above worse at each of two lengths of life include a strict preference across lengths. | A two-by-two case of what Thornley draws from his Second Theorem (2025, §8, p. 1665) | Special case |
| S3d | Without completeness, such preferences can have no strict preference across lengths. | A four-point picture of the proposal in Thornley and others (2024), arXiv:2407.00805 | Example only |

## Limits

1. **Proof settles what follows from what.** It says nothing about how any AI system will behave, or whether trained systems are retargetable over outcomes, have complete preferences, or are close to optimal.
2. **Finite settings only.** S1a is for lotteries over a finite set. S2c is for finite sets of options and finitely many reward functions; the first report said continuous reward distributions were "captured", and they are not.
3. **No decision process.** The 2021 paper's theorems are about Markov decision processes, discounting and the states an agent can reach. None of that is formalised. S2c is the lemma about sets of vectors that those theorems rest on.
4. **Thornley's theorems are not formalised.** His three theorems concern preferences over lotteries of trajectories. S3a and S3c are small relatives.
5. **Statements were locked before they were checked.** In the lab's two earlier proof studies the check came first and several statements were mended before the lock. Here the check came after, so the weak statements could only be reported, not replaced.
6. **Not read:** the first edition of von Neumann and Morgenstern (a 1953 printing was read); most of Gustafsson's second chapter; the file of Thornley's paper that the study hashed, which is not in the repository.

## Departures from the plan

Recorded in `amendments.md`: the statement check ran after the lock; five source locators were wrong and are corrected; the plan's wording for S2d and S2e ("3-state MDP", "optimal policies") is not what the statements contain. Nothing in `lean/` was changed.

## Spending

Nothing was paid for. The proofs and the checks ran on local machines.

## What this means

Three kinds of mathematical result are often cited together as showing that a capable AI must behave like a single-minded maximiser, gather power and resist being switched off. Do they show it? No. The results are real, and they are conditional: they say what an agent of a certain idealised kind would do, and their own authors write that they do not prove any future system will be of that kind. This study put four of the underlying results through a proof checker and they hold. It also tried to show, by counterexample, exactly which assumption each conclusion hangs on, and that part did not come off: the counterexamples are too small to bear the weight, and one of them was aimed at a question (whether an agent with gaps in its preferences can be exploited) that philosophers are still arguing about. The useful next step is the one the earlier proof studies took: have the statements checked against the papers before they are locked, then formalise the disputed arguments themselves.
