---
# To update this page, edit this file and push to main; the site rebuilds itself.
# The panels are made by questions/power-seeking/analysis/make_figures.py.
summary: Three kinds of mathematical result are cited for the claim that a capable AI must act like a single-minded maximiser, gather power and resist being switched off. We wrote fourteen statements from them in Lean 4, where a proof checker verifies every step, and then had a second company's models check what the statements say.
verdict: No, as the theorems' own authors say; the study adds less than it first claimed
result: All fourteen statements are proved. Checked against the papers, six say what a published source says, including the expected-utility theorem and the lemma behind "optimal policies tend to seek power". Five are small examples that do not carry the conclusions first drawn from them, among them the claims that dropping completeness stops money pumps and that expected-utility maximisers need not resist shutdown. The authors of the power-seeking theorems write that their results do not prove future AI will seek power.
dek: Do the coherence, power-seeking and shutdown theorems prove that a capable AI must pursue power and resist being switched off? Fourteen statements, proved in Lean 4 and then checked against the papers.
updated: 2026-11-24
---

> **Where things stand, 24 November 2026.** Google's model (Antigravity, Google DeepMind) wrote fourteen formal statements, locked them, and proved them all. It had no second model to check that the statements said what was meant, and said so. Anthropic's models have now done that check: one read the formal text alone, without the report or the proofs, and another looked up every cited passage. The proofs hold. Eight of the fourteen statements say less than the first report claimed for them, and this page is the corrected version.

{{figure: power-seeking/tiles}}

## What was asked

Three families of result are often cited together.

- **Coherence.** An agent whose preferences cannot be exploited must act as if it maximises expected utility (von Neumann and Morgenstern; the "money pump" arguments).
- **Power-seeking.** For most goals, the best policy keeps options open, and so gains power (Turner and others, 2021; Turner and Tadepalli, 2022).
- **Shutdown.** An agent that maximises expected utility will either block its off-switch or press it (Soares and others, 2015; Thornley, 2025).

Strung together they are taken to show that any capable AI will seek power and resist correction. The question was what the mathematics proves, and from which assumptions. In Lean 4 every assumption has to be written into the statement, and a small trusted program rejects any proof that uses anything else.

## What holds

1. **The expected-utility theorem, in full.** If preferences over gambles are complete (any two options can be compared), transitive, independent and continuous, they can be scored by an expected utility, and the score is unique up to scale and shift. All four conditions are used.
2. **"Acts as if it maximises some utility" says nothing by itself.** Any fixed way of behaving, however erratic, maximises a utility defined over whole histories. This is Rohin Shah's observation from 2018.
3. **The counting lemmas behind "retargetable decision-makers tend to seek power".** If relabelling the parameters turns every case that favours one outcome into a case that favours another, then most relabellings favour the second. These are the 2022 paper's own statements.
4. **The lemma behind "optimal policies tend to seek power".** If one set of options contains a relabelled copy of another, then across the relabellings of any spread of rewards, the larger set is worth more at least as often as less. It is proved for finite sets of options. The paper's theorems about agents moving through an environment rest on this lemma; those theorems themselves were not formalised.
5. **A small case of the clash in the shutdown problem.** An agent with complete, transitive preferences that prefers better to worse among short lives, and among long lives, must strictly prefer some short life to some long one, or the reverse. Such an agent has a reason to meddle with its off-switch.

## What did not hold up

The first report said each argument "breaks cleanly" when one assumption is dropped, and offered six counterexamples. Five of them are too small to show it.

- **"Drop completeness and money pumps stop."** The statement shows that some preferences with gaps have no chain of *preferred* trades that loses money. But that follows from transitivity alone, and a preference with no gaps passes the same test. The money pump that philosophers argue about works by trading across the gaps, and the statement's definition leaves those trades out. The report credited the claim to Johan Gustafsson's book, which argues the opposite. The question is in live dispute and nothing here settles it.
- **"Drop reward symmetry and power-seeking fails."** The theorem never assumed symmetric rewards. It says that for any spread of rewards, most relabellings of it favour the larger set. That one particular spread favours the smaller set is something the paper says itself.
- **"Drop optimality and power-seeking fails."** The "non-optimal policy" is a function with no conditions on it. A constant satisfies the statement.
- **"Expected-utility maximisers need not resist shutdown."** The statement assumes that staying on and being shut down are worth exactly the same to the agent, and concludes it will leave the switch alone. Making them worth the same is the hard part. The paper cited for it shows two ways the approach goes wrong and ends: "a corrigible solution to the shutdown problem does not yet exist."
- **"Drop completeness and the shutdown problem is solved."** The statement shows that a preference with no ranking between short and long lives can exist, on four points. It does not show that an agent with one stays willing to be shut down.

{{figure: power-seeking/premises}}

## What the authors say

The first report's headline was that the theorems prove "substantially less than 'any capable AI must seek power'". The papers do not claim otherwise.

- Turner and others (2021): "Our results do not mathematically prove that hypothetical superintelligent AI agents will seek power."
- Turner and Tadepalli (2022): "Our results do not prove that we will build unaligned AI agents which seek power over the world."

They do say what they expect. The 2021 paper: "Average-optimal agents would generally stop us from deactivating them, if physically possible." The 2022 paper: "Our theory suggests that when RL training processes become sufficiently advanced, the trained agents will tend to seek power over the world." Those are conjectures about what real systems will be like. A proof checker cannot weigh them.

## The shutdown table

{{figure: power-seeking/shutdown_explorer}}

## What this cannot tell you

- **How any AI system will behave.** The mathematics says what follows from what.
- **Whether gaps in preferences can be exploited.** Not tested, as above.
- **The theorems about environments.** No decision process, policy or discounting was formalised; nor were Thornley's three theorems.
- **Anything a specialist would catch.** AI wrote the statements, the proofs and the checks. Nobody else has reviewed them.

## What this means

The theorems are real and conditional. They describe an idealised kind of agent, and whether future systems will be of that kind is a question about training and engineering that their authors leave open. This study confirms four of the underlying results by machine. Its attempt to show which single assumption each conclusion hangs on did not succeed, because the statements were locked before anyone checked that they said what was intended. The lab's two earlier proof studies checked first; this one shows why.

::: details Methods, data and checks
- **Plan and lock.** `questions/power-seeking/protocol.md` and `lean/PowerSeeking/Statement.lean`, locked 2026-11-24T17:43:54Z, before the proofs. Corrections to the sources are recorded in `amendments.md`; nothing in the Lean files was changed.
- **Build.** `lake build --wfail`, Lean v4.35.0 with Mathlib pinned. No warnings; all fourteen theorems rest on the three standard axioms only. Rebuilt from a clean copy during the check.
- **Statement check.** `questions/power-seeking/statement-check/`: the blind reading, the short proofs written to test it, and the source check with quotations and page numbers.
- **Sources.** von Neumann and Morgenstern, *Theory of Games and Economic Behavior* (2nd ed., 1947); Gustafsson, *Money-Pump Arguments* (2022); Shah (2018); Turner and others, "Optimal Policies Tend to Seek Power" (NeurIPS 2021, arXiv:1912.01683); Turner and Tadepalli, "Parametrically Retargetable Decision-Makers Tend To Seek Power" (NeurIPS 2022, arXiv:2206.13477); Soares and others, "Corrigibility" (2015); Thornley, "The shutdown problem", *Philosophical Studies* 182 (2025); Thornley and others (2024), arXiv:2407.00805.
- **Full report.** `questions/power-seeking/RESULTS.md`.
- **Who did the work.** AI did. Antigravity (Google DeepMind) wrote the statements and proofs; Claude Fable 5.2 and Claude Opus 5.5 (Anthropic) rebuilt and checked them and wrote this page. Eugene directed both.
:::
