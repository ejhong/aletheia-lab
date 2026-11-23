# Notation key (Lean 4 with Mathlib)

- `structure S where f : T …`: a record type. A value of type `S` has one component for each listed field; `x.f` is
  the field `f` of `x`. A field may be a type (`f : Type`), and later fields may depend on earlier ones.
- `(n : A) → B n`: a function that takes `n` in `A` and returns a value in the type `B n`, which may depend on `n`
  (a choice of one element of `B n` for every `n`). `A → B` is an ordinary function type.
- `fun x => e`: the function sending `x` to `e`.
- `Fintype A`: a proof that the type `A` has finitely many elements. `Fintype.card A`: how many.
  `attribute [instance] …` only tells Lean to use such a field automatically.
- `Type`: the collection of types. `Prop`: the type of propositions. `def Name : Prop := …` names a proposition; it
  does not assert or prove it.
- `List X`: finite sequences of elements of `X`. `[]`: the empty sequence. `xs.length`: its length.
  `xs ++ ys`: `xs` followed by `ys`.
- `xs.foldl f a`: start from `a` and apply `f` once for each element of `xs`, left to right:
  `[x1, x2].foldl f a = f (f a x1) x2`.
- `{xs : List X // xs.length ≤ T}`: the type of sequences of length at most `T`. For `xs` of that type, `xs.1` is
  the underlying sequence.
- `Fin T`: the natural numbers `0, …, T - 1`. For `k : Fin T`, `k.val` is the number. `⟨j, proof⟩ : Fin T` is the
  number `j` together with a proof that `j < T`; `by omega` is such a proof, found automatically.
- `A × B`: pairs. For `a : A × B`, `a.1` and `a.2` are the two parts. `(x, y)` is a pair.
- `Unit`: the type with exactly one element, written `()`. `Bool`: `true` and `false`; `||` is "or".
- `if h : c then a else b`: `a` if `c` holds, otherwise `b`.
- `Relation.TransGen r a b`: there is a chain `a = c0, c1, …, ck = b` with `k ≥ 1` and `r ci c(i+1)` at each step
  (the transitive closure of `r`; a single step counts, zero steps do not).
- `Nonempty A`: `A` has at least one element.
- `Set A`: sets of elements of `A`. `x ∈ s`, `x ∉ s`: membership. `s ⊆ t`: subset. `s ∩ t`: intersection.
  `∅`: the empty set. `{x | P x}`: the set of `x` with `P x`. `∃ o ∈ s, P o`: some element of `s` satisfies `P`.
- `t.Produces r → t.Produces r` where `t.Produces r` is a set: a function from the elements of that set to
  elements of that set. For `p` an element of the set taken this way, `p.1` is the underlying element.
- `∀`, `∃`, `∧`, `∨`, `¬`, `→`, `↔`, `=`, `≠`: the usual logical symbols. `ℕ`: the natural numbers.
- `universe u v w` and `Type u`: types of arbitrary size; this can be ignored when reading.
- `inferInstance`: "found automatically"; here, the proof that a type is finite.
