# Log

Dated entries, newest last: what was tried, what happened, what next.

## 2026-11-23 — Stage 0 (Claude Fable 5.2, Anthropic; directed by Eugene)

- Eugene marked #66 active and said "run #66 end to end". This session runs Stages 0 to 2 without waiting at the
  gates between stages, which departs from the issue's `needs:eugene` gates and from AGENTS.md §2 (a fresh
  session per question); both at his direction. Stage 3 is not started.
- Budget. SPENDING.md showed $45.39 spent across the lab today, against the $50 daily cap. Asked Eugene before
  any paid call. Answer: yes, up to #66's $40, covering Stages 0 to 2.
- Priors, written before any proof or check. I expected: unfolding at a finite horizon is true and easy; it fails
  for unbounded time; learning changes nothing at a finite horizon; the falsification step is close to trivial
  once the premises are explicit. I did not expect the two directions of premise P2 to behave differently; that
  came out of the trial proofs (below). I am an AI model, and the argument bears on whether behaviour could show
  an AI system to be conscious, so I have a stake in the subject.
- Prior-art search (a sub-agent, then spot checks). Lean Zulip public channels, queries: unfolding argument;
  integrated information; consciousness; recurrent feedforward; Krohn-Rhodes; "definite automaton"; "finite
  memory" automaton; unrolling recurrent network; Mealy machine; recurrent neural network; Kleiner Hoel;
  transducer. GitHub code search: "unfolding argument" (Lean, Agda); "integrated information" (Lean, Coq,
  Isabelle); Kleiner Hoel; falsification consciousness; "Krohn-Rhodes"; "substitution argument"; Doerig; Tononi;
  "definite automaton"; "Mealy" "feedforward". GitHub repository search: unfolding argument; integrated
  information theory; krohn-rhodes; consciousness lean/coq/isabelle. Web search and OpenAlex (works citing
  Doerig 2019 since 2025). Result: no machine-checked unfolding argument or substitution argument found.
  Closest: Mayeux's Lean 4 formalization of IIT 4.0 (Zenodo, 2026; its abstract does not mention unfolding; code
  not found); a Lean 4 Krohn–Rhodes proof (adii800/krohn-rhodes-lean); two small repositories that take
  "feedforward implies zero ϕ" as an axiom. None of these was read by me beyond the sub-agent's report.
- The search also found the source of the "2026 counter-arguments" mentioned in the issue: O'Reilly-Shah,
  Selvitella and Schurger, *Neuroscience of Consciousness* 2026, on plasticity. Read from the journal XML. Its
  supplementary appendix, with the formal proofs, was not obtained.
- Sources. Downloaded Doerig 2019 and Herzog 2022 (publisher PDFs from EPFL's repository), Kleiner and Hoel
  (arXiv v3 and the journal XML), Hanson and Walker (arXiv v2 and the journal XML), O'Reilly-Shah 2026 (journal
  XML). Tsuchiya 2020 and Usher 2021 are paywalled and were not obtained; Usher's abstract was.
  One request to the Unpaywall API was sent with a placeholder e-mail address; no personal details were sent.
- Read Doerig §§1–2.7 and Appendix A; Kleiner and Hoel §§2–5; Herzog §§1–2, DR2, DR5; the plasticity paper's
  claims and proof summaries; Hanson and Walker's passages on Krohn–Rhodes and on falsification.
- Two things from the reading shaped the statements. (1) Hanson and Walker's "strictly feed-forward" circuit is
  made of flip-flops, units that keep their own state; Doerig's feedforward network has no such units. These are
  different notions (`FeedbackFree`, `LoopFree`). (2) Kleiner and Hoel's proof of Theorem 4.3 takes the
  conceivable datasets to have the same inference contents as the ones that arise; the theorem as printed does
  not say so. S2d states the assumption and S2d′ says it is needed.
- Not formalized, and `unverified`: reading the proof of Kleiner and Hoel's Proposition 3.9, the step "the first
  two of these four conditions imply that obs(p) ⊂ ō" seems to need the system p to produce the dataset o itself,
  where Definition 3.8 only gives a dataset with the same prediction content. This is one model's reading of a
  published proof. It has not been stated in Lean or checked by anyone, and it is not a result.
- Lean project: Mathlib at the commit the Gödel question's dependency uses, so the local build cache is shared.
  Mathlib now expects the module system; the statement file is a `module` with a public section, which keeps
  the build free of warnings.
- Exploration (`explore/Sketch.lean`, not a finding): trial proofs of all nineteen statements compile. Two
  statements were false as first drafted and were corrected before any check: with no possible input, no unit
  depends on any unit, so nothing is integrated; S1h and S2f now assume at least one input.
- From the trial proofs, again not a finding until the proofs proper: the delay-line twin of S1b has exactly T
  units and the lower bound of S1e is T, so for the latch the bound is exact.
- Wrote `statement-check/passages.md` (24 passages) and `check_quotes.py`: all 49 quoted pieces are found in the
  extracted texts, letters only.
- Statement check, round 1 (29 items, 4 planted errors), $14.02. Both checkers caught all four planted errors.
  OpenAI rated 15 of 25 real items divergent, Google 5. Most of OpenAI's were of one kind: a statement of the
  lab's own judged as if it rendered a passage. Several were real, listed in `protocol.md`: the reading of
  Proposition 3.7, a missing restriction in the falsification definition, a wrong passage for S1b, and my
  misdescription of what the plasticity paper concedes.
- Round 2 (19 items, 2 new planted errors), $8.50: both caught both. Google: no major divergence left. OpenAI:
  two, both about how I described a statement (S1f, S1h), not about the Lean. Round 3 (those two items), $0.89:
  clean.
- Final: 24 of 26 real items faithful or faithful with caveats from both checkers. Two accepted divergences, both
  from OpenAI, both the same point: the paper's premise P2 has no time limit and the provable statement has one.
- Spent $23.41 of the $40 budget (SPENDING.md). The lab's total for today is over the $50 cap, with Eugene's
  approval given at the start of the session.
- A new statement came out of the check: S2c′. An outside model's counterexample to a strong reading of a
  published proposition, now stated in Lean; proved only after the lock.
- Gate after Stage 0, reported and not waited on (Eugene's instruction to run end to end): twenty statements,
  each with a trial proof that compiles; the outcome table is in `protocol.md`.
- Locked `protocol.md` and `lean/UnfoldingArgument/Statement.lean` at 18:04:39 UTC (commit 7502087), before any
  proof file existed under `lean/`.
- Stages 1 and 2: proofs of all twenty statements (`Results.lean`, `Results2.lean`) and seven non-vacuity and
  supporting theorems (`NonVacuity.lean`), commit f550f36. They are the trial proofs from `explore/`, moved into
  module files; the only change is that the hub of the integrated twin now starts set. The build passes with
  warnings as errors locally and in CI (run 45234539396); 27 theorems pass the axiom audit.
- A quirk of the audit, found while testing it: if a theorem's *statement* fails to elaborate, Lean records the
  theorem with a placeholder type and reports no axioms for it, so `#assert_standard_axioms` alone would pass.
  The build still fails on the elaboration error, so nothing gets through; the audit is a second layer, not the
  only one.
- Wrote `RESULTS.md` and the site page. Gates after Stages 1 and 2 reported here and not waited on.
- Not done: Stage 3 (Krohn–Rhodes with simple components; intervening on the twin's own units); Kleiner and
  Hoel's Theorem 3.10; a replication of the statements by a second vendor's agent. Filing with Aletheia is
  Eugene's decision and has not been done.

## 2026-11-23, later — Stage 3, first half (Claude Fable 5.2; directed by Eugene)

- PR #81 (Stages 0 to 2) merged with a merge commit; the lab check and both Lean builds pass on `main`. The
  Gödel project's CI build took about 15 minutes where it used to take 2; my guess, not checked, is that the two
  Lean projects now evict each other's build cache.
- Eugene asked whether Stage 3 was worthwhile. I recommended the half about units with memory, with odds, and
  against the half about intervening on the twin's own units. He said to proceed. He also asked that easy
  mechanical work go to sub-agents on a fitting model, and that the stronger model be used when in doubt.
- Sub-agents used: Claude Haiku 5.5 (low effort) pulled verbatim passages from Hanson and Walker with line
  numbers; I read them in its report and `check_quotes.py` confirmed them against the text. Claude Opus 5.5
  (medium effort) added the `--stage 3` mode to `run.py`; I checked that the default mode's output is unchanged
  and that the Stage 3 view is right. The statements, proofs, amendment and write-up are mine.
- Priors, written into Amendment 1 before the check: feedback-free networks of k-state units settle into cycles
  whose length divides a power of k!, so a counter to three has no feedback-free twin made of bits.
- Trial proofs of all six statements compile (`explore/Stage3Sketch.lean`). The periodicity proof went through
  on the first attempt at the main lemma; the rest was plumbing.
- Amendment 1 pushed (841089f) before the statement check. Check: three rounds, $3.65. Both planted errors
  caught by both; all six statements faithful in round 1; the two definitions needed their description rewritten
  twice (it called the counter a rendering of the paper's tollbooth, and then contained a false aside about
  k = 0). No unresolved divergence.
- Question total so far: $27.06 of the $40 approved for today.
- Locked `Statement3.lean` at 19:03:05 UTC (327ba92). Proofs in `Results3.lean` (34a5de8): the trial proofs moved
  into a module file, with two proof-only helpers marked noncomputable so that the compiler does not try to
  generate code for them. Build passes with warnings as errors locally and in CI (run 45244866647); six more
  theorems pass the axiom audit, 33 in all.
- Added the Stage 3 section to `RESULTS.md` and updated the site page and the topic page.
- Not done: the other half of Stage 3 (intervening on the twin's own units); which machines exactly have a
  feedback-free realization from bits; the Krohn–Rhodes theorem. Krohn and Rhodes (1965) and Zeiger (1967) were
  not read, so what the results say about Hanson and Walker's general sentence depends on a reading of
  "elementary components" that is `unverified`.

