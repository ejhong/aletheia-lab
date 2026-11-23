Exploratory work. Nothing here is a finding.

`Sketch.lean` holds trial proofs of every statement in `lean/UnfoldingArgument/Statement.lean`, written before
the lock to make sure no statement is false as written. Compile it from `lean/` with
`lake env lean ../explore/Sketch.lean`. The proofs proper are in `lean/UnfoldingArgument/Results.lean`.

What the trial proofs changed before the lock: two statements (S1h and S2f) were false as first drafted, because
a network with no possible input has no causal dependence at all. Both now assume at least one possible input.
