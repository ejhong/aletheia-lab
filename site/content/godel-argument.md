---
# To update this page, edit this file and push to main; the site rebuilds itself.
#   Tick a step:     change "- [ ]" to "- [x]".
#   Move a stage:    set its "Status:" line to done, in progress or not started.
#   Report results:  replace the note under "## Results" with text or a Markdown table.
#   Also update the "Where things stand" note and the "updated:" date below.
summary: What exactly does the Lucas–Penrose argument prove, and from which premises?
dek: What exactly does the Lucas–Penrose argument prove, and from which premises? The plan is to write the argument and its standard replies in Lean 4, so that a proof checker shows which premises carry which conclusion.
updated: 2026-11-22
---

> **Where things stand, 22 November 2026.** Stage 0 is at its gate. Thirteen statements are written in Lean and have been through the statement check by two other vendors' models; they are waiting for Eugene's review before the lock. Nothing has been proved for the record, so there are no results yet.

## The question

What exactly does the Lucas–Penrose argument prove, and from which premises? The plan is to formalize the argument and its standard analyses in Lean 4, a language in which a small trusted kernel checks every step of a proof, so that the kernel shows which premises carry which conclusion.

This settles what follows from what. It does not settle whether minds are machines.

Roughly, as the argument is usually summarised: Gödel's second incompleteness theorem says that a consistent formal system strong enough for basic arithmetic, whose axioms a machine can list, cannot prove its own consistency. Lucas and Penrose argued that a human mathematician can see that such a system is consistent, so human mathematical understanding is not the output of any such system. The replies turn on what the human would have to know for that to work: that the system is consistent, and which system it is.

## Why it matters

- **The atlas has an open claim on it.** Aletheia's claim [ORCH-C040](https://ejhong.github.io/aletheia/claims/ORCH-C040/), "Human mathematical understanding is not the execution of any knowably sound formal algorithm", is rated Unresolved in the atlas (as read on 22 November 2026). It sits in the atlas case on Orch OR, [Collapse, Not Computation](https://ejhong.github.io/aletheia/cases/orch-or/).
- **Prose hides premises; a proof checker does not.** In Lean every assumption has to be written into a theorem's statement, and the kernel rejects a proof that leans on anything else. That makes it possible to say exactly which premises each conclusion needs.
- **Most of the mathematics already exists.** The Foundation library has machine-checked Gödel's first and second incompleteness theorems, Löb's theorem and local reflection. What the lab adds is the mind/machine reading, the source locators, and a table of which premises carry which conclusion.
- **It appears not to have been done.** Searches on 22 November 2026 found no earlier machine-checked version of the Lucas–Penrose argument, epistemic arithmetic, the knower paradox or Gödel's disjunction. One project planned the same formalization and deferred it (see Sources).

The lab does not grade the atlas. A finished result is filed with Aletheia as an outside source, and Stage 1's report gives no verdict on ORCH-C040.

## The plan

Four stages. Each ends at a gate where Eugene decides what happens next (on GitHub, the label `needs:eugene`). The ticks below mark steps as they are finished.

### Stage 0 · Statements only
Status: in progress
Gate: Eugene reviews the checkers' divergences, then `lean/Statement.lean` is locked.

Write down exactly what will be proved, and check that it says what was meant, before proving anything.

- [x] Definitions, each with an English gloss and a locator to the passage it formalizes: formal system as r.e. theory; soundness; consistency; an idealized mind as a set K of sentences; "K is the theorem set of some machine"; and plain-arithmetic stand-ins for "K knows which machine" and "K knows the machine is sound".
- [x] Statements in `lean/GodelArgument/Statement.lean` as `def … : Prop`: 11 definitions and 13 statements, compiling against the pinned Foundation library. Proofs elsewhere must have exactly those types, so the lock covers the statements while proofs stay free to change.
- [x] The proof-lane Lean CI, set up on the question's branch, with a build-time check that a theorem uses only Lean's three standard axioms.
- [x] The statement check. OpenAI `gpt-6.2-astra` and Google `gemini-4-neon` each translated every Lean statement back into English blind, then compared it with the source passage. Three deliberately wrong statements were mixed in. In the final round both checkers caught all three. Their criticism in the earlier rounds led to five statements being rewritten. Of 17 items with a source passage, 15 ended as faithful or faithful with caveats from both checkers; two divergences are accepted with reasons and will be reported with the results. One statement, the halting form, could not be checked against its source because *Shadows of the Mind* is not yet in hand.
- [ ] Eugene reviews the report; then the protocol and the statement file are locked.

### Stage 1 · Core results in plain arithmetic
Status: not started
Gate: A report; Eugene decides on Stage 2.

Thin wrappers: Foundation already proves the underlying theorems (their names are in code type), and `RESULTS.md` must say so.

- [ ] **a. Penrose's conclusion as a conditional.** If K is consistent and is the theorem set of F, then K does not contain Con(F). Stated for every r.e. axiomatization F of K, because Con(F) depends on how F is described. And in the shape the sources give it: a consistent, deductively closed mind that accepts "whatever F proves is so" strictly exceeds F. (`consistent_unprovable`, `craig_consistent_unprovable_of_RE`)
- [ ] **b. The standard objection**, in three parts. A witness: PA is sound, consistent and a machine's theorem set, and lacks Con(PA). The machine proves the conditional itself, F ⊢ Con(F) → G_F, so the human's only edge is knowing Con(F) (`gödel_iff_con`). And the second machine: for any sound F, F + Con(F) is again a sound machine, with a consistency statement of its own that it cannot prove.
- [ ] **c. Chalmers's point via Löb.** A system that proves its own soundness for every sentence is inconsistent, with no assumption that it is a machine (`löb_theorem`). By contrast, adding the soundness *of T* to a sound T gives a sound system.
- [ ] **d. Gödel's disjunction, semantic form.** For any set K of true arithmetic sentences, either no formal system has K as its theorem set, or some true Π₁ sentence is undecided by K. Truth here means truth in ℕ in Lean's own logic.
- [ ] **e. Penrose's argument in halting form** (optional). No sound r.e. certifier of non-halting certifies its own diagonal computation. The issue recalls this as the form *Shadows of the Mind* §2.5 uses; `unverified` until the book is checked.

### Stage 2 · Epistemic arithmetic
Status: not started
Condition: Only if Eugene approves it after the Stage 1 report. It would get its own budget.
Gate: Each tier gets its own statement check, entered through `amendments.md` before anything in it is proved.

This is where the new work is: theories in which the knower K is an operator with its own axioms (K1–K4), as in Reinhardt's epistemic arithmetic. The targets, as stated in Koellner (2018, Part I), are Reinhardt's Theorem 3 (p. 354), Theorem 5 (p. 355) and Theorem 6 (p. 357). Theorems 7 and 8, consistency results by Reinhardt and by Carlson, are cited, not proved. Statements are to be taken from Reinhardt's own papers, since Koellner's summary is informal in places.

- [ ] **2A, small.** An abstract layer with K1–K4 and diagonalization as hypotheses, then Theorem 3. Plus a refutation of one instance of Reinhardt's schema in a minimal calculus with K; that derivation is the issue author's own and must be checked against Reinhardt (1985) before it is credited to him.
- [ ] **2B, large.** EA and EA_T as concrete formal systems in Lean, then Theorems 5 and 6 as stated.
- [ ] **2C, large.** Koellner's Part II (not yet read): DTK and Penrose's new argument, written as a derivation with each unlicensed step isolated as a named hypothesis.

### Stage 3 · Stretch
Status: not started
Condition: Only after reporting on the earlier stages.

- [ ] Independence results by model construction.
- [ ] The untyped-truth inconsistency.

Out of scope: Carlson's consistency proof, which is cited instead. Dropped for now: the stably-computable version, because its author's own arXiv comment on 2208.04752v3 says "The framework currently has gaps".

## The rules

These come from the lab's proof lane and from issue #19.

- **A statement check by other vendors' models.** Before anything is proved, models from two other vendors translate each formal statement back into English without seeing the lab's gloss or the proof, and list where it differs from the source passage. Deliberately wrong statements are mixed in to test the checkers. Unresolved divergences are reported in `RESULTS.md`.
- **The lock.** The statements are definitions in `lean/Statement.lean`. Once checked, the file's SHA-256 is committed in `protocol.lock` before any proof. A proof can change freely but cannot quietly prove something else. A corrected statement is a new file plus a dated amendment, never an edit.
- **No `sorry`.** No `sorry`, no `admit`, no new `axiom`. Each headline theorem may depend only on `propext`, `Classical.choice` and `Quot.sound`, checked inside the build so that a violation fails it.
- **No vacuous theorems.** Every assumed premise is a hypothesis in the theorem's statement, and each headline theorem comes with an instance showing its hypotheses can hold together (for example PA in the standard model). Nothing may be true only because its premises contradict each other.
- **Keep "is a machine" and "knows which machine" apart.** The whole dispute lives in that gap. In Koellner's notation: WMT `∃e (K = F_e)`, SMT `K∃e (K = F_e)`, SSMT `∃e K(K = F_e)`. Stage 1 can express "knows which machine" only by proxy, because plain arithmetic has no way to say "me"; each gloss says which side of that trade-off its statement is on.
- **Credit the library.** Where a result restates a theorem Foundation already proves, `RESULTS.md` names that theorem. Incompleteness is not rebuilt from scratch.

## Results

> **No results yet.** Stage 0 has just started. Nothing on this page is a finding.

When Stage 1 is done, this section will hold a table of each claim, its Lean name, the premises it requires, its status and its source locator, with a plain summary of under 300 words of what follows from what, and no verdict on ORCH-C040.

## Sources

#### Read on 22 November 2026

- Koellner, "On the Question of Whether the Mind Can Be Mechanized, I: From Gödel to Penrose", *Journal of Philosophy* 115(7) (2018) 337–360. Formal content at pp. 349–359: axioms K1–K4 (p. 352), EA and EA_T (p. 353), Theorems 3–8 (pp. 354–358). The copy read was a course-hosted PDF of the published article; the protocol needs a properly sourced copy.
- Alexander, "A machine that knows its own code", *Studia Logica* 102(3) (2014) 567–576, [arXiv:1305.6080](https://arxiv.org/abs/1305.6080). Read through a fetch sub-agent's report of the arXiv HTML.

#### Bibliographic details verified, text not read

- Koellner, "II: Penrose's New Argument", *Journal of Philosophy* 115(9) (2018) 453–484.
- Reinhardt, "Absolute Versions of Incompleteness Theorems", *Noûs* 19(3) (1985) 317–346.
- Reinhardt, "The Consistency of a Variant of Church's Thesis with an Axiomatic Theory of an Epistemic Notion", *Revista Colombiana de Matemáticas* 19(1–2) (1985) 177–200.
- Reinhardt, "Epistemic Theories and the Interpretation of Gödel's Incompleteness Theorems", *Journal of Philosophical Logic* 15(4) (1986) 427–474.
- Carlson, "Knowledge, Machines, and the Consistency of Reinhardt's Strong Mechanistic Thesis", *Annals of Pure and Applied Logic* 105(1–3) (2000) 51–82.
- Gödel, "Some Basic Theorems on the Foundations of Mathematics and Their Implications" (1951), in *Collected Works* III (OUP 1995) 304–323; the disjunction is at p. 310 (as cited in Koellner Part I).
- Corradini and Galvan, "Analysis of Penrose's Second Argument Formalised in DTK System", *Logic and Logical Philosophy* 31(3) (2022) 471–500, [doi:10.12775/LLP.2021.019](https://doi.org/10.12775/LLP.2021.019); a follow-up in the same journal, vol. 33 (2024).
- Savelyev, [arXiv:2001.07592](https://arxiv.org/abs/2001.07592) (its arXiv comment: "superseded by arxiv:2208.04752") and [arXiv:2208.04752](https://arxiv.org/abs/2208.04752) (comment on v3: "The framework currently has gaps").

#### Unverified until the protocol checks them

- Penrose, *Shadows of the Mind* (1994) ch. 2–3; "Beyond the Doubting of a Shadow", *Psyche* 2 (1996).
- Lucas, "Minds, Machines and Gödel", *Philosophy* 36 (1961).
- Chalmers, "Minds, Machines, and Mathematics", *Psyche* 2 (1995). Lindström, *Journal of Philosophical Logic* 30 (2001). Shapiro, *Journal of Philosophical Logic* 32 (2003).
- Koellner, "Gödel's Disjunction", in Horsten and Welch (eds.), OUP 2016.
- Suggested addition: Stern, "Proving that the Mind is Not a Machine?" (2018).

#### Prior art and dependencies, checked 22 November 2026

- [moritzbrantner/formal-logos](https://github.com/moritzbrantner/formal-logos) (formerly `truth-core`), [issue 366](https://github.com/moritzbrantner/formal-logos/issues/366), planned the same formalization. It was closed on 15 November 2026 as deferred when that project narrowed its scope; it never added Foundation and has no Lean file on the topic. Cited as prior art.
- Lean Zulip, public channels, searched for "Lucas Penrose", "anti-mechanist", "epistemic arithmetic", "Gödel's disjunction", "Koellner" and "Penrose": nothing relevant. Private channels can't be searched.
- GitHub code search (Lean files) and web search: no machine-checked version of the Lucas–Penrose argument, epistemic arithmetic, the knower paradox or Gödel's disjunction found.
- [FormalizedFormalLogic/Foundation](https://github.com/FormalizedFormalLogic/Foundation) (Apache-2.0), candidate pin `fbcfee52cb4a892087fa978366282a9ebd844f29` (12 November 2026; Lean v4.35.0, Mathlib v4.35.0). Its paper: Saitou and Noguchi, [arXiv:2609.13780](https://arxiv.org/abs/2609.13780).

---

The plan was assessed by Claude (Opus 5.5) and revised the same day by Claude (Fable 5.2) after reading Foundation and Koellner Part I, on 22 November 2026, from Eugene's brief. The work is done by AI agents and directed by Eugene Jhong. This page summarises [issue #19](https://github.com/ejhong/aletheia-lab/issues/19), which holds the full text.
