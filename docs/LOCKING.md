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

`protocol.lock` holds the SHA-256 of `protocol.md` and the UTC time. `scripts/check.py` (run by CI on every push and
PR) fails when:

- `results/` or `RESULTS.md` exists but there is no `protocol.lock`;
- `protocol.md` no longer matches the hash in `protocol.lock`;
- the commit that added the first result is not strictly later than the commit that added the lock.

Changes after locking go in `amendments.md`, dated, with the reason, before the changed part runs.

## By lane

- **data / model:** the full lock. State the hypotheses, the exact test, the null distribution or baseline, the
  threshold, and what you'd conclude either way. For model experiments, also the prompts, models, sample sizes and
  scoring rubric.
- **proof:** the Lean compiler is the judge, so lock only the *formal statement* (`lean/Statement.lean`, quoted in
  `protocol.md`) after the statement check. The proof itself can be explored freely.
- **audit:** lock the search scope and the grading rubric (which texts, which editions, what counts as a
  description of X) before reading for the answer.
- **protocol / watch:** no lock; nothing is being measured here.

## Exploration

`explore/` is outside the lock on purpose. Looking around first is how good protocols get written. The only rule
is that nothing from `explore/` is presented as a finding.
