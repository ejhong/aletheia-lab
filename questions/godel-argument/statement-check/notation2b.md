# Notation key for tier 2B (Lean 4)

These statements use plain Lean 4 with Mathlib's sets. No logic library is involved: the formal language and its proof system are defined in the context itself.

- `inductive Name : Type` followed by lines beginning `|` defines a type by listing the ways of building its elements. `inductive Name : Form → Prop` followed by lines beginning `|` defines a property of formulas by listing rules: the property holds exactly of the formulas obtainable by those rules. In a rule, `A → B → Name φ` means: if `A` and `B` hold then the property holds of `φ`.
- A definition by cases (`def f (x : ℕ) : Form → Prop` followed by lines `| pattern => value`) is recursion on the structure of the formula.
- `ℕ` is the natural numbers; variables of the formal language are natural numbers. `Set Form` is the type of sets of formulas, `∅` the empty set, `φ ∈ T` membership.
- `Prop` is the type of propositions of the meta-language. `∀`, `∃`, `∧`, `∨`, `¬`, `→`, `↔`, `=`, `≠` are the usual connectives of the meta-language, as opposed to the constructors of the formal language (`imp`, `all`, `neg`, `and`, `iff`, `ex`, `K`, `fls`).
- `if c then a else b` is a case distinction. Arguments in curly braces, such as `{φ : Form}`, are implicit.
- Names of the form `Def1`, `Def2`, …, `Target` replace the original names. Names of constructors and of the basic connectives are kept.
