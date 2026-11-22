# Locking a protocol

The lock is a light form of preregistration: write down what you will measure and how you will judge it, freeze
that, and only then look at the answer.

## How

```
python scripts/lock.py questions/<slug>     # writes questions/<slug>/protocol.lock
git add questions/<slug>/protocol.lock
git commit -m "Lock protocol: <slug>"
git push                                    # the push timestamps it publicly
```

`protocol.lock` holds the SHA-256 of `protocol.md` and the UTC time, plus the SHA-256 of each locked formal
statement file (proof lane, below). `scripts/check.py` (run by CI on every push and PR) fails when:

- `results/` or `RESULTS.md` exists but there is no `protocol.lock`;
- `protocol.md` no longer matches the hash in `protocol.lock`;
- a locked statement file is missing or no longer matches its hash;
- results exist while some `lean/**/Statement*.lean` is not in the lock;
- the commit that added the first result is not strictly later than the commit that added the lock.

Changes after locking go in `amendments.md`, dated, with the reason, before the changed part runs.

## By lane

- **data / model:** the full lock. State the hypotheses, the exact test, the null distribution or baseline, the
  threshold, and what you'd conclude either way. For model experiments, also the prompts, models, sample sizes and
  scoring rubric.
- **proof:** the Lean compiler is the judge, so lock only the *formal statement* after the statement check. The
  proof itself can be explored freely. Details in "Proof lane" below.
- **audit:** lock the search scope and the grading rubric (which texts, which editions, what counts as a
  description of X) before reading for the answer.
- **protocol / watch:** no lock; nothing is being measured here.

## Proof lane

- **Statements are definitions.** `lean/Statement.lean` holds each claim as `def Name : Prop := …` and nothing
  else that needs proving. Proofs live in other files as `theorem name : Statement.Name := …`. The lock hashes the
  statement file, so a proof can change freely but cannot quietly prove something else.
- **Statement check before the lock.** Models from two other vendors each get the Lean statement and the
  definitions it depends on, not our gloss and not the proof. Each translates it back into English, then compares
  that with the source passage and lists divergences. Mix in a couple of deliberately wrong statements to see
  whether the checkers catch them. Unresolved divergences go in `RESULTS.md`.
- **Later stages.** A stage that adds new statements puts them in a new file (for example
  `lean/Stage2/Statement.lean`), runs its own statement check, notes it in `amendments.md`, and locks the file
  with `python scripts/lock.py questions/<slug> --statement lean/Stage2/Statement.lean` before proving anything
  in it. A locked statement file is never edited; a corrected statement is a new file plus an amendment.
- **No vacuous theorems.** When premises are hypotheses, a theorem can hold only because the premises contradict
  each other. Each headline theorem comes with an instance showing its hypotheses can hold together.
- **Axioms.** No `sorry`, no `admit`, no new `axiom`. Each headline theorem may depend only on `propext`,
  `Classical.choice` and `Quot.sound`, checked inside the build so that a violation fails it. Pin the toolchain
  and every dependency to a commit.
- **Credit the library.** When a result is a restatement of a theorem a dependency already proves, `RESULTS.md`
  names that theorem.

## Exploration

`explore/` is outside the lock on purpose. Looking around first is how good protocols get written. The only rule
is that nothing from `explore/` is presented as a finding.
