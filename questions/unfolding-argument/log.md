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
