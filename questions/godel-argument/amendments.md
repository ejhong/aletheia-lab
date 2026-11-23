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
