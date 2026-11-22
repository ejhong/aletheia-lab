# Notation key (Lean 4, Foundation library at commit fbcfee52)

The statements are written in Lean 4 using the FormalizedFormalLogic "Foundation" library. Meanings of the symbols used:

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
- Arguments in square brackets, such as `[F.RE]` or `[𝗜𝚺₁ ⪯ F]`, are hypotheses of the statement.
- `∀ (x : A), P x` is universal quantification, `∃`, `∧`, `∨`, `¬`, `→` are the usual connectives of the meta-language, `∈`/`∉` set membership, `∪` union.
