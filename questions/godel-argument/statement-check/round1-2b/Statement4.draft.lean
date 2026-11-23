import Foundation.Logic.Entailment

/-!
# The Gödel argument: a concrete logic of knowledge with quantifiers (Amendment 4, tier 2B)

Statements only, like the other `Statement` files. Unlike `Statement2.lean` and `Statement3.lean`, nothing here is
abstract: this file defines a formal language with a knowledge operator `K` and real quantifiers, and a proof
system for it, following Reinhardt (1985), pp. 322–323. The statements are about what that proof system proves.

The language is a fragment of Reinhardt's. It has binary relation symbols applied to variables, falsehood,
implication, the universal quantifier and `K`. It has no function symbols, no constants and no arithmetic.
Reinhardt's Theorems 3 and 5 do not use arithmetic, and they are the statements made here.

Source locators are in `amendments.md` (Amendment 4), keyed by the names used here (D17–D19, S3a–S3f).

The import is there only to reach Mathlib's sets. No definition from the Foundation library is used in this file.
-/

namespace GodelArgument.QEL

/-! ## D17. The language -/

/-- Formulas. Variables are natural numbers. `atom r x y` is the `r`-th binary relation symbol applied to the
variables `x` and `y`; `fls` is falsehood; `all x φ` is "for all `x`, `φ`"; `K φ` is "it is known that `φ`". -/
inductive Form : Type
  | atom (r x y : ℕ) : Form
  | fls : Form
  | imp (φ ψ : Form) : Form
  | all (x : ℕ) (φ : Form) : Form
  | K (φ : Form) : Form

namespace Form

/-- Negation: `φ` implies falsehood. -/
def neg (φ : Form) : Form := imp φ fls

/-- Conjunction. -/
def and (φ ψ : Form) : Form := neg (imp φ (neg ψ))

/-- Biconditional. -/
def iff (φ ψ : Form) : Form := and (imp φ ψ) (imp ψ φ)

/-- "For some `x`, `φ`". -/
def ex (x : ℕ) (φ : Form) : Form := neg (all x (neg φ))

/-- The variable `x` occurs free in the formula. -/
def Free (x : ℕ) : Form → Prop
  | atom _ a b => x = a ∨ x = b
  | fls => False
  | imp φ ψ => Free x φ ∨ Free x ψ
  | all y φ => x ≠ y ∧ Free x φ
  | K φ => Free x φ

/-- Replace the free occurrences of the variable `x` by the variable `y`. -/
def subst (x y : ℕ) : Form → Form
  | atom r a b => atom r (if a = x then y else a) (if b = x then y else b)
  | fls => fls
  | imp φ ψ => imp (subst x y φ) (subst x y ψ)
  | all z φ => if z = x then all z φ else all z (subst x y φ)
  | K φ => K (subst x y φ)

/-- `y` is free for `x` in the formula: no free occurrence of `x` lies within the scope of a quantifier on
`y`. -/
def FreeFor (y x : ℕ) : Form → Prop
  | atom _ _ _ => True
  | fls => True
  | imp φ ψ => FreeFor y x φ ∧ FreeFor y x ψ
  | all z φ => z = x ∨ ¬ Free x φ ∨ (z ≠ y ∧ FreeFor y x φ)
  | K φ => FreeFor y x φ

end Form

open Form

/-! ## D18. The proof system -/

/-- A truth assignment to all formulas that respects falsehood and implication. Atoms, quantified formulas and
formulas `K φ` receive arbitrary truth values. -/
def PropVal (v : Form → Prop) : Prop := ¬ v fls ∧ ∀ φ ψ, v (imp φ ψ) ↔ (v φ → v ψ)

/-- A tautology: true under every such assignment. -/
def Tautology (φ : Form) : Prop := ∀ v, PropVal v → v φ

/-- The axiom schemas: tautologies; universal instantiation; distribution of the quantifier over implication;
vacuous quantification; and the four axioms for `K`: distribution over implication, "what is known is so", "what
is known is known to be known", and "if it is known that all `x` are `φ`, then of each `x` it is known that it
is `φ`". -/
inductive BaseAx : Form → Prop
  | taut {φ : Form} : Tautology φ → BaseAx φ
  | inst (x y : ℕ) (φ : Form) : FreeFor y x φ → BaseAx (imp (all x φ) (subst x y φ))
  | dist (x : ℕ) (φ ψ : Form) : BaseAx (imp (all x (imp φ ψ)) (imp (all x φ) (all x ψ)))
  | vac (x : ℕ) (φ : Form) : ¬ Free x φ → BaseAx (imp φ (all x φ))
  | k2 (φ ψ : Form) : BaseAx (imp (K (imp φ ψ)) (imp (K φ) (K ψ)))
  | k3 (φ : Form) : BaseAx (imp (K φ) φ)
  | k4 (φ : Form) : BaseAx (imp (K φ) (K (K φ)))
  | kall (x : ℕ) (φ : Form) : BaseAx (imp (K (all x φ)) (all x (K φ)))

/-- The schemas under any prefix of universal quantifiers. -/
inductive Sig : Form → Prop
  | base {φ : Form} : BaseAx φ → Sig φ
  | gen (x : ℕ) {φ : Form} : Sig φ → Sig (all x φ)

/-- The axioms: every such formula, and `K` of every such formula. -/
def Axiom (φ : Form) : Prop := Sig φ ∨ ∃ ψ, Sig ψ ∧ φ = K ψ

/-- `Proves T φ`: `φ` is derivable from the axioms and the formulas in `T` by modus ponens alone. -/
inductive Proves (T : Set Form) : Form → Prop
  | ax {φ : Form} : Axiom φ → Proves T φ
  | hyp {φ : Form} : φ ∈ T → Proves T φ
  | mp {φ ψ : Form} : Proves T (imp φ ψ) → Proves T φ → Proves T ψ

/-! ## D19. The diagonal formulas -/

/-- `U a b`: a fixed binary relation symbol, read "`b` belongs to the `a`-th set". -/
def U (a b : ℕ) : Form := atom 0 a b

/-- With `x` the variable 0 and `e` the variable 1: "for all `x`: it is known that `x` is not in the `x`-th set,
exactly when `x` is in the `e`-th set". -/
def diagAll : Form := all 0 (iff (K (neg (U 0 0))) (U 1 0))

/-- "`e` is not in the `e`-th set", with `e` the variable 1. -/
def diagQ : Form := neg (U 1 1)

/-! ## Statements -/

/-- **S3a. Necessitation is a derived rule.** Whatever the logic proves outright, it proves to be known. -/
def NecessitationIsDerived : Prop := ∀ φ : Form, Proves ∅ φ → Proves ∅ (K φ)

/-- **S3b. Reinhardt's Theorem 5.** No theory in this logic is consistent with "for some `e`, it is known that
the things known not to belong to themselves are exactly the members of the `e`-th set": every theory proves
its negation. -/
def KnowingWhichSetRefuted : Prop := ∀ T : Set Form, Proves T (neg (ex 1 (K diagAll)))

/-- **S3c. Reinhardt's Theorem 3.** If a theory proves "for some `e`, the things known not to belong to
themselves are exactly the members of the `e`-th set", it proves "for some `e`: `e` is not in the `e`-th set,
and that is not known". -/
def ThesisGivesUnknownTruth : Prop :=
  ∀ T : Set Form, Proves T (ex 1 diagAll) → Proves T (ex 1 (and diagQ (neg (K diagQ))))

/-- **S3d. The same, in the form "absolutely undecidable".** Under the same hypothesis the theory proves "for
some `e`: it is not known that `e` is not in the `e`-th set, and it is not known that it is". -/
def ThesisGivesAbsolutelyUndecidable : Prop :=
  ∀ T : Set Form, Proves T (ex 1 diagAll) → Proves T (ex 1 (and (neg (K diagQ)) (neg (K (neg diagQ)))))

/-- **S3e. The same, known.** If a theory proves that the hypothesis of S3c is known, it proves that the
conclusion of S3c is known. -/
def KnownThesisGivesKnownUnknownTruth : Prop :=
  ∀ T : Set Form, Proves T (K (ex 1 diagAll)) → Proves T (K (ex 1 (and diagQ (neg (K diagQ)))))

/-- **S3f. The logic is consistent.** It does not prove falsehood. -/
def LogicIsConsistent : Prop := ¬ Proves ∅ fls

end GodelArgument.QEL
