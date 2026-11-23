# Notation key for tier 2D (Lean 4, Foundation library at commit fbcfee52)

This tier has statements of two kinds. Some are about first-order arithmetic (part A). The others are abstract (part B): they use no arithmetic at all. A statement of one kind uses none of the notation of the other, although definitions of both kinds are listed as context.

## Part A: arithmetic

- `ArithmeticSentence`: a closed formula of first-order arithmetic (language `ℒₒᵣ`: 0, 1, +, ·, =, <).
- `ArithmeticTheory`: a set of arithmetic sentences, used as axioms. It is the same type as `Set ArithmeticSentence`; it need not be closed under deduction.
- `T ⊢ σ`: σ is derivable from the axioms T in classical first-order logic. `T ⊬ σ`: it is not.
- `T.theory`: the set `{σ | T ⊢ σ}` of all theorems of T.
- `Entailment.Consistent T`: T does not prove a contradiction. `Entailment.Inconsistent T`: T proves every sentence.
- `ℕ↓[ℒₒᵣ] ⊧ σ`: σ is true in the standard model, the natural numbers.
- `F.RE` (also written `Theory.RE F`): the set F is recursively enumerable. `REPred A`: the predicate A on a countable type is recursively enumerable (the domain of a partial recursive function).
- `F.Δ₁`: F comes with a Δ₁ arithmetical definition of its axiom set, which is what lets one write "provable from F" inside arithmetic.
- `F.craig`: Craig's trick. For a recursively enumerable F, a Δ₁-presented axiom set with exactly the same theorems as F.
- `T ⪯ U`: every theorem of T is a theorem of U.
- `𝗜𝚺₁`: basic arithmetic with induction for Σ₁ formulas. `𝗣𝗔`: Peano arithmetic.
- `T.consistent.val`: the arithmetic sentence `¬Prov_T(⌜⊥⌝)`, where `Prov_T` is the standard provability predicate built from T's Δ₁ presentation. `T.Con`: the one-element set containing that sentence.
- `🡒`, `🡘`, `∼`, `⊥`: implication, biconditional, negation and falsehood *inside* the formal language (as opposed to Lean's `→`, `↔`, `¬`).
- `Provability T₀ T`: a formula `prov(x)` of the language such that whenever `T ⊢ σ`, also `T₀ ⊢ prov(⌜σ⌝)` (derivability condition D1). For `𝔅 : Provability T₀ T`, `𝔅 σ` is the sentence `prov(⌜σ⌝)` and `𝔅.con` is `∼𝔅 ⊥`. Nothing requires `prov` to define a recursively enumerable set.
- `𝔅.HBL`: the other two derivability conditions. D2: `T₀ ⊢ 𝔅 (σ 🡒 τ) 🡒 𝔅 σ 🡒 𝔅 τ`. D3: `T₀ ⊢ 𝔅 σ 🡒 𝔅 (𝔅 σ)`.
- `Diagonalization T₀`: for every formula θ(x) there is a sentence γ with `T₀ ⊢ γ 🡘 θ(⌜γ⌝)`.
- `gödel 𝔅`: the sentence γ obtained that way from θ(x) := `¬prov(x)`, so `T₀ ⊢ γ 🡘 ∼𝔅 γ`.
- `T.standardProvability`: the standard provability predicate of a Δ₁-presented arithmetic theory T, as a `Provability 𝗜𝚺₁ T`.
- `L.ReferenceableBy L`, `L.DecidableEq`: the language L has Gödel numerals for its own sentences, and decidable equality of symbols.
- `T.localReflectionOn Set.univ`: the set of all sentences `Prov_T(⌜σ⌝) 🡒 σ`, one for every sentence σ.
- `Nat.Partrec.Code`: codes (programs) for partial recursive functions on ℕ. `Denumerable.ofNat Nat.Partrec.Code n`: the n-th code. `c.eval n`: the result of running c on input n, a partial value; `(c.eval n).Dom` means the run halts.
- `ℬ[<, ℒₒᵣ].Hierarchy 𝚷 1 σ`: σ is a Π₁ formula of arithmetic (a block of universal quantifiers in front of a formula with only bounded quantifiers), up to the library's syntactic definition of the hierarchy.
- `A ⊆ B`: A is a subset of B. `A ⊂ B`: A is a strict subset of B (A ⊆ B and not B ⊆ A). `{x}`: the one-element set. `∃ _ : P, Q`: P holds and Q holds (P is a hypothesis needed to state Q).
- Arguments in square brackets, such as `[F.RE]` or `[𝗜𝚺₁ ⪯ F]`, are hypotheses of the statement.
- `∀ (x : A), P x` is universal quantification, `∃`, `∧`, `∨`, `¬`, `→` are the usual connectives of the meta-language, `∈`/`∉` set membership, `∪` union.
- `(S : ArithmeticTheory)` after a set `S` of sentences, or a set used where axioms are expected: the same set, used as axioms.
- `{σ | P σ}`: the set of all sentences σ with property P.

## Part B: abstract

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
