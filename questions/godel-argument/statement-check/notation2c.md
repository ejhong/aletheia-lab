# Notation key for tier 2C (Lean 4, Foundation library at commit fbcfee52)

These statements use only the abstract part of the FormalizedFormalLogic "Foundation" library. Nothing about arithmetic, Gödel numbering or quantifiers inside the formal language is built in.

- `Fm`, `S₀`, `S` are arbitrary types. `Fm` is a type of sentences. `S₀` and `S` are types of proof systems.
- `[LogicalConnective Fm] [LogicalNeutral Fm]`: the sentences have the connectives `🡒` (implication), `⋏` (conjunction), `⋎` (disjunction), `∼` (negation), and the constants `⊤` (truth) and `⊥` (falsehood). `φ 🡘 ψ` abbreviates `(φ 🡒 ψ) ⋏ (ψ 🡒 φ)`. These are connectives *inside* the formal language, as opposed to Lean's own `→`, `∧`, `¬`, `↔`.
- `[Entailment S Fm]`: each system `𝓢 : S` has a provability relation on sentences. `𝓢 ⊢ φ` means the system `𝓢` proves the sentence `φ`.
- `[Entailment.Cl 𝓢]`: the system `𝓢` proves every classical propositional tautology in these connectives and is closed under modus ponens. Nothing else is assumed about `𝓢`; in particular nothing says it is consistent, and nothing says that `𝓢 ⊢ φ` implies `𝓢 ⊢ K φ`.
- `K : Fm → Fm` and `F : Fm → Fm` are arbitrary functions from sentences to sentences. `K φ` is the sentence obtained by applying `K` to `φ`. Function application binds tighter than the connectives: `∼F ψ` is `∼(F ψ)`, and `K φ 🡒 φ` is `(K φ) 🡒 φ`. `🡒` associates to the right: `a 🡒 b 🡒 c` is `a 🡒 (b 🡒 c)`.
- `∀ (x : A), P x` is universal quantification, `∃`, `∧`, `→` are the usual connectives of the meta-language. A statement that begins `∀ (Fm S₀ S : Type) […] (𝓑 : S₀) (𝓢 : S) […] (K F : Fm → Fm), …` holds for every choice of sentence type, connectives, pair of systems and functions `K`, `F`.
- Arguments in square brackets are hypotheses or structure supplied to the statement.
- A line beginning `variable` declares the types and structure that the definitions after it take as implicit parameters.
- `𝓑 ⪯ 𝓢`: every sentence provable in `𝓑` is provable in `𝓢`.
- `¬ 𝓢 ⊢ φ`: the system `𝓢` does not prove `φ`. `Entailment.Consistent 𝓢`: `𝓢` does not prove every sentence.
- Two statements are about first-order arithmetic. `ArithmeticSentence`: a closed formula of first-order arithmetic. `ArithmeticTheory`: a set of arithmetic sentences used as axioms; `T ⊢ σ` means σ is derivable from T in classical first-order logic. `𝗣𝗔`: Peano arithmetic. In those statements `K` and `F` are arbitrary functions from arithmetic sentences to arithmetic sentences; they need not be given by formulas.
- `T.standardProvability σ`, for an arithmetic theory `T` given by a Δ₁ definition of its axioms (such as `𝗣𝗔`): the arithmetic sentence `Prov_T(⌜σ⌝)`, "T proves σ", built from the standard Σ₁ provability predicate of `T` and the Gödel numeral of σ.
- `T.localReflectionOn Set.univ`: the set of all sentences `Prov_T(⌜σ⌝) 🡒 σ`, one for every sentence σ. `A ∪ B`: union of two sets of axioms.
- `let x : A := e` followed by a statement: `x` abbreviates `e` in that statement.
- `T`, `K`, `D : Fm → Fm` are arbitrary functions from sentences to sentences. `S₀`, `S'`, `σ`, `G`, `P`, `Q`, `X`, `lam`, `kap` are arbitrary sentences; in this tier `S₀` and `S'` are sentences, not systems.
- `𝓢 ⊢ φ → 𝓢 ⊢ ψ`, with Lean's own arrow between two provability claims, is a rule: if the system proves `φ` then it proves `ψ`. `𝓢 ⊢ φ 🡒 ψ` says the system proves the implication.

