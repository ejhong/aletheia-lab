# Amendments

Changes after the lock, dated, each with its reason, written before the changed part runs.

## Amendment 1 (2026-11-23): check S1e against Penrose's text

**What changed.** The protocol left S1e (`PenroseTuring`) without a passage check because *Shadows of the Mind*
was not in hand. On 2026-11-23 Eugene supplied photographs of pp. 72–77 (§2.5 and the start of §2.6). Written
before anything below is run.

**What will be done, in this order.**

1. Transcribe the relevant passages into `statement-check/passages.md` (P-P73 to P-P76). The transcription is by
   Claude Fable 5.2 from the photographs and cannot be checked mechanically against a text file, unlike the other
   passages. The photographs are not stored in the repository (copyright); their SHA-256 values go in `MANIFEST.md`.
2. Run the comparison step for S1e with the same two checkers, models and prompt as round 2. Their blind
   translations of 2026-11-22 are reused unchanged: they were made before any passage existed for this item.
3. Decision rule, fixed now. If both verdicts are `faithful` or `faithful_with_caveats`, S1e stands and
   `RESULTS.md` replaces `unverified` with the verdicts and caveats. If either checker reports a major divergence,
   S1e stays as locked with the divergence reported, and a source-shaped statement S1e′ is written in a new file
   `lean/GodelArgument/Statement2.lean`, put through the full check by both checkers (blind translation, then
   comparison), locked with `scripts/lock.py --statement`, and only then proved.
4. Compare Koellner's quotation of Penrose's conclusion 𝒢 (p. 76), used for S1a″, with the book.

**Why.** The protocol named this as the one statement not checked against its source.

**Cost.** Expected under $2, inside the $50 budget.

**My reading before the run**, so that it is on record. Against Penrose's steps (H) to (M), S1e differs in three
ways. (a) Penrose's A takes a pair (q, n) and is sound for every pair; S1e's A is a recursively enumerable
property of one number, sound on the diagonal only. That makes S1e's assumption weaker and the theorem stronger.
(b) Penrose's k is the index of the computation n ↦ A(n, n), so that A(k, k) is the same computation as C_k(k);
S1e says only that some k exists. (c) The step "if we know that A is sound, then we know that C_k(k) does not
stop" cannot be said in this setting. I expect caveats; (b) may be rated major.

**Erratum.** The locked protocol's first paragraph says "fourteen statements". The locked statement file has
thirteen: one variant was dropped before the lock and the count was not updated. Nothing of substance changes.

**Outcome (2026-11-23, after the run).** OpenAI `gpt-6.2-astra`: `faithful_with_caveats`, two minor divergences.
Google `gemini-4-neon`: `faithful_with_caveats`, three minor divergences. Neither rated (b) major. By the rule
above S1e stands as locked and no S1e′ is added. Koellner's quotation of 𝒢 matches p. 76 of the book word for
word. Cost $0.32 at list price ($0.06 OpenAI, $0.25 Google).

**Second erratum, found while writing this up.** The locked protocol and the first version of `RESULTS.md` say
"of 17 real items with a passage". Seventeen was the number of real items; sixteen had a passage, because S1e had
none. The figures at the lock were 14 of 16 clean from both checkers. With S1e now checked they are 15 of 17.

## Amendment 2 (2026-11-23): Stage 2A, a knowledge operator

**What changed.** On 2026-11-23 Eugene approved Stage 2 ("Go ahead with stage 2"). I take that as tier 2A of the
plan in issue #19, the tier recommended to him. Tiers 2B and 2C are not started. Written before the statement
check below is run and before anything in Stage 2A is proved.

**Budget.** The issue says Stage 2 gets its own budget if approved. None was named, so Stage 2A stays inside the
question's $50, of which $12.70 is spent. Expected cost of the statement check: $6 to $12. I stop and ask before
going over $50.

**The question for this stage.** Stage 1 could not say "I know". With a knowledge operator K added, which
principles about K carry the three results that Koellner's analysis rests on: the knower exceeds any system it
knows to be sound (Theorem 3), it cannot know its own consistency under mechanism (Theorem 4), and it cannot know
which system it is (Theorem 6)?

**Setting.** Abstract, in the style of Foundation's `ProvabilityAbstraction`. Sentences are any type with
classical connectives. K and F are functions on sentences. There is a base system 𝓑 (think EA) and a system 𝓢
that includes it. Arithmetic, Gödel numbering and quantifiers are not modelled. Each fact the sources get from
arithmetic, and each principle about K, is an explicit hypothesis of the statement that uses it.

**Statements** (drafted in `statement-check/Statement2.draft.lean`; the file moves to
`lean/GodelArgument/Statement2.lean` in the commit that locks it; passages in `statement-check/passages.md`).

| Name | Gloss | Source |
|---|---|---|
| D11 `KnowsTheoremsOf` | What the base proves, 𝓢 proves to be known | Koellner 2018a, pp. 352–353 (K1, EA = Σ ∪ KΣ); Alexander 2014, Def. 3. A derived rule there; a hypothesis here |
| D12 `KnowledgeClosedUnderMP` | K2 | Koellner 2018a, p. 352; Alexander 2014, Def. 3 (E2) |
| D13 `Factive` | K3: what is known is so | same (E3) |
| D14 `KnowsOwnFactivity` | K applied to each instance of K3 | same; a member of KΣ |
| D15 `HasGödelSentence` | The base proves ψ ↔ ¬F(ψ) for some ψ | the diagonal lemma; no passage |
| S2a `ReinhardtTheorem3` | If K(F(φ) → φ) for each φ, then for some ψ: Kψ and K¬F(ψ) | Koellner 2018a, p. 354, Theorem 3 |
| S2a′ `KnowerExceedsKnownSoundSystem` | With K3: something is known that F does not hold of | Koellner 2018a, pp. 354, 356 (second claim; Penrose's 𝒢) |
| S2b `AbsoluteSecondIncompleteness` | If K(Kφ → F(φ)) for each φ, and the base proves the formalized second incompleteness theorem for F, then K¬K(Con F) | Koellner 2018a, p. 354, Theorem 4, with a proviso added |
| S2c `KnowingWhichSystemIsContradictory` | If K(Kφ ↔ F(φ)) for each φ, then 𝓢 proves a contradiction | Koellner 2018a, p. 357, Theorem 6 (SSMT), in the sentence-by-sentence form of Alexander 2014, Theorem 12(3) |
| S2d `NoKnownSelfDiagonal` | For no p is it known that p holds exactly when ¬p is known | the lab's own core of a refutation of one instance of Reinhardt's schema (Alexander 2014, Def. 4) |

**Sources.** Koellner 2018a (already in the manifest). Alexander, "A machine that knows its own code",
arXiv:1305.6080v2, published in *Studia Logica* 102(3) (2014); retrieved 2026-11-23. Cheng, arXiv:1902.05902v2,
for attributions. Reinhardt's 1985 and 1986 papers are not in hand: every attribution to Reinhardt here is
through Koellner, Alexander or Cheng, and is `unverified` against Reinhardt's text.

**Method.** As in Stages 0 and 1.

1. Statement check: OpenAI `gpt-6.2-astra` and Google `gemini-4-neon` each translate every item blind, then
   compare with the passages. Three planted errors are mixed in (K dropped from the hypothesis of S2c; a negation
   dropped from the conclusion of S2a; the hypothesis of S2b reversed). Script: `statement-check/run.py --stage 2a`.
2. If a real item is rated `divergent`, either the statement is rewritten and re-checked, or the divergence is
   accepted and carried into the results. Each case is recorded below before the lock.
3. Lock `Statement2.lean` with `scripts/lock.py --statement`, in its own commit.
4. Proofs in `Results2.lean`, with exactly the locked types; non-vacuity instances in `NonVacuity2.lean`; the
   axiom audit on every theorem; a Stage 2A section in `RESULTS.md`.

**What would count.** Each statement proved with Lean's three standard axioms is a row of the premise table: the
hypotheses in its statement are sufficient. A statement that cannot be proved as written is reported as such.
Whether a hypothesis is also *necessary* is not settled by a proof; for known factivity the evidence is
Alexander's theorem that a machine can know its own code without it, which is cited, not proved here.

**Exploration before the lock.** A proof sketch of each draft statement was compiled first, to make sure none is
false as written (`explore/Stage2Sketch.lean`). It is exploratory and is not a finding.

**Known weaknesses, declared in advance.**

- The layer is abstract. Nothing here builds EA or EA_T as formal systems, so no statement is literally about
  them. That is tier 2B.
- `KnowsTheoremsOf` is assumed. In the sources it is derived from K1, K2, K4 and the shape Σ ∪ KΣ. K4 therefore
  never appears as a hypothesis.
- The Gödel sentence is assumed, not constructed.
- S2c is a scheme, one instance per sentence, for a fixed F. The single sentence ∃e K(K = F_e) and the
  quantifier over machines are not expressed.
- S2b adds a hypothesis that is not on Koellner's page. As printed, for an arbitrary formula F(x) and with Con(F)
  read as ¬F(⌜⊥⌝), Theorem 4 fails: take F(x) to be x ≠ ⌜⊥⌝. What Reinhardt requires of F is `unverified`.
- S2d rests on a derivation of mine. The source says only that Reinhardt found an inconsistent instance of his
  schema, not which one.
- The consistency side is cited, not proved: EA_T + WMT (Reinhardt) and EA_T + SMT (Carlson) are consistent, and
  knowing one's own code is consistent without known factivity (Alexander).
- The non-vacuity witnesses will use the trivial knower, K φ := φ. They show that the hypotheses do not clash.
  They do not exhibit an interesting knower.

**My expectation before the run.** S2b will probably be rated `divergent`, because of the added proviso. S2c and
S2d will draw caveats, perhaps `divergent`, for the missing quantifiers.

**Round 1 of the Stage 2A statement check (2026-11-23), and what changed.** Inputs and outputs are frozen under
`statement-check/round1-2a/`. Cost $3.98 at list price.

- Planted errors: both checkers caught all three.
- Real items with a passage (7): both checkers gave `faithful_with_caveats` on D12–D14, S2a′ and S2c. OpenAI
  rated D11 and S2a `divergent`; both rated S2b `divergent`; Google rated S2d `divergent`.

| Finding | Response |
|---|---|
| D11, S2a, S2b (OpenAI, major): nothing required 𝓢 to include the base, and the source's rule "if EA proves φ then EA proves Kφ" is internal to EA. | Accepted. D11 is now `ClosedUnderNecessitation`, a rule of the base alone, and every statement takes inclusion `𝓑 ⪯ 𝓢` as a separate hypothesis. This matches the source's "S includes EA". |
| S2b (both, major): the hypothesis that the base proves the formalized second incompleteness theorem for F is not on the page. | Kept, as declared before the run: without it the statement is false. New statement S2b′ says so formally: a system in which every other hypothesis of S2b holds and its conclusion is not provable. S2b is reported as a repaired variant of Theorem 4, not as the printed theorem. |
| S2d (Google, major): the Lean cannot express Reinhardt's schema, and the step from the schema to K(K(¬p) ↔ p) is not formalized. | Accepted as a limit. S2d is now claimed only as a lemma of the lab's about K; its link to Reinhardt's schema is informal and is not claimed as a formalization. |
| The amendment said necessity of known factivity was "cited, not proved". | Strengthened. New statement S2e: a consistent system containing Peano arithmetic in which every hypothesis of S2c except known factivity holds, and in which the sentence excluded by S2d is known. The intended witness is Peano arithmetic's own provability predicate, used as K. This is a counterpart in the abstract layer of Alexander's theorem, not that theorem. |

New rows for the statements table:

| Name | Gloss | Source |
|---|---|---|
| D11 `ClosedUnderNecessitation` (replaces `KnowsTheoremsOf`) | What the base proves, the base proves to be known | as before |
| S2b′ `SecondIncompletenessProvisoCannotBeDropped` | Some system satisfies every hypothesis of S2b but the proviso, and does not prove S2b's conclusion | the lab's own; bears on Koellner 2018a, p. 354, Theorem 4 |
| S2e `KnownFactivityCannotBeDropped` | Some consistent system satisfies every hypothesis of S2c but known factivity | counterpart of Alexander 2014, §1 and Theorem 12 |

A fourth planted error is added for round 2: S2e with known factivity put back among the conjuncts, which
contradicts S2c. All items are re-checked in round 2, since the definitions changed. A proof sketch of each
revised and new statement was compiled first (`explore/Stage2Sketch.lean`, exploratory).
