import GodelArgument.Statement
import GodelArgument.Statement5

/-!
# The Gödel argument: Corradini and Galvan's steps, and a corollary (Amendment 6, tier 2D)

Statements only. Two settings are used, each already defined in an earlier file.

* **Arithmetic** (`Statement.lean`): a mind is a set of arithmetic sentences, a machine is a recursively
  enumerable set of axioms, and truth is truth in the standard natural numbers.
* **Abstract** (`Statement2.lean`, `Statement5.lean`): sentences are any type with classical connectives, `𝓢` is a
  proof system closed under classical propositional reasoning, and `T`, `K`, `D`, `F` are operations on
  sentences read "is true", "is known", "is determinate", "is provable in the formal system F". Each fact the
  sources take from arithmetic is an explicit hypothesis.

Source locators are in `amendments.md` (Amendment 6), keyed by the names used here (D28, S5a–S5g).
-/

namespace GodelArgument

open FFL FFL.FirstOrder FFL.FirstOrder.Arithmetic FFL.FirstOrder.ProvabilityAbstraction

/-! ## Arithmetic: a consistent machine need not be sound -/

/-- **D28. Peano arithmetic with the denial of its own consistency.** The axioms of Peano arithmetic together
with the one sentence "Peano arithmetic is inconsistent". -/
noncomputable def PAPlusNotCon : ArithmeticTheory := 𝗣𝗔 ∪ {∼Con 𝗣𝗔}

/-- **S5a. Consistency does not give soundness.** The system D28 is a formal system (recursively enumerable).
It is consistent, and its own consistency statement is true. Yet it proves the sentence "Peano arithmetic is
inconsistent", which is false. -/
def ConsistencyDoesNotGiveSoundness : Prop :=
  ∃ _ : Theory.RE PAPlusNotCon,
    Consistent PAPlusNotCon.theory ∧ IsTrue (Con PAPlusNotCon) ∧
      (∼Con 𝗣𝗔) ∈ PAPlusNotCon.theory ∧ ¬ IsTrue (∼Con 𝗣𝗔)

/-- **S5b. A machine can prove what a mind cannot know, while the mind knows the machine consistent.** Take the
machine D28. Every sound mind lacks some sentence that this machine proves. And there is a mind that is sound,
deductively closed, contains every theorem of Peano arithmetic, is itself the theorem set of a machine, and
contains the consistency statement of D28. -/
def MachineOutrunsMindThatKnowsItConsistent : Prop :=
  ∃ _ : Theory.RE PAPlusNotCon,
    (∀ K : Mind, Sound K → ∃ σ, σ ∈ PAPlusNotCon.theory ∧ σ ∉ K) ∧
    (∃ K : Mind, IsMechanical K ∧ Sound K ∧ DeductivelyClosed K ∧ 𝗣𝗔.theory ⊆ K ∧ Con PAPlusNotCon ∈ K)

/-- **S5g. The assumptions of Stage 1 about a mind are met by a machine and by a non-machine.** There is a mind
that is sound, consistent, deductively closed, contains every theorem of Peano arithmetic, and is the theorem
set of a machine. There is another with the same four properties that is the theorem set of no machine. -/
def MindAssumptionsDoNotDecide : Prop :=
  (∃ K : Mind, Sound K ∧ Consistent K ∧ DeductivelyClosed K ∧ 𝗣𝗔.theory ⊆ K ∧ IsMechanical K) ∧
  (∃ K : Mind, Sound K ∧ Consistent K ∧ DeductivelyClosed K ∧ 𝗣𝗔.theory ⊆ K ∧ ¬ IsMechanical K)

/-! ## Abstract: the corollary, and two more steps of Corradini and Galvan -/

/-- **S5c. The corollary holds for a sentence for which consistency gives soundness.** Let `conF` stand for
"F is consistent". Suppose knowledge is closed under modus ponens, it is known that if F is consistent then
whatever F proves of `φ` is so ("if F proves `φ` then `φ`"), and whenever F proves `φ` it is known that F proves
`φ`. Then: if `φ` is not known and F proves `φ`, the consistency of F is not known. -/
def CorollaryHoldsWhereConsistencyGivesSoundness : Prop :=
  ∀ (Fm S : Type) [LogicalConnective Fm] [LogicalNeutral Fm] [Entailment S Fm] (𝓢 : S) [Entailment.Cl 𝓢]
    (K F : Fm → Fm) (conF φ : Fm),
    KnowledgeClosedUnderMP 𝓢 K →
    𝓢 ⊢ K (conF 🡒 F φ 🡒 φ) →
    𝓢 ⊢ F φ 🡒 K (F φ) →
    𝓢 ⊢ ∼K φ ⋏ F φ 🡒 ∼K conF

/-- **S5d. A mind whose arithmetic lies inside a machine cannot know that machine consistent.** Let `conF`
stand for "F is consistent". Suppose that if `conF` is known then it is so, that if `conF` is known then F
proves it, and that if F is consistent then F does not prove `conF` (the second incompleteness theorem for F).
Then `conF` is not known. -/
def MindInsideMachineCannotKnowItConsistent : Prop :=
  ∀ (Fm S : Type) [LogicalConnective Fm] [LogicalNeutral Fm] [Entailment S Fm] (𝓢 : S) [Entailment.Cl 𝓢]
    (K F : Fm → Fm) (conF : Fm),
    𝓢 ⊢ K conF 🡒 conF →
    𝓢 ⊢ K conF 🡒 F conF →
    𝓢 ⊢ conF 🡒 ∼F conF →
    𝓢 ⊢ ∼K conF

/-- **S5e. From the restricted result to the refutation of the unrestricted thesis** (Corradini and Galvan's
step 8). Let `σ` say that knowledge and F agree on arithmetic sentences, and `τ` that they agree on all
sentences. Suppose the system proves that `σ → G` is known and that, if `σ`, F does not prove `σ → G` (with `Q`
for "F proves `σ → G`"). Suppose `τ` implies `σ`, and `τ` implies that if `σ → G` is known then F proves it.
Then the system proves that `τ` fails. -/
def UnrestrictedThesisRefuted : Prop :=
  ∀ (Fm S : Type) [LogicalConnective Fm] [LogicalNeutral Fm] [Entailment S Fm] (𝓢 : S) [Entailment.Cl 𝓢]
    (K : Fm → Fm) (τ σ G Q : Fm),
    𝓢 ⊢ K (σ 🡒 G) ⋏ (σ 🡒 ∼Q) →
    𝓢 ⊢ τ 🡒 σ →
    𝓢 ⊢ τ 🡒 K (σ 🡒 G) 🡒 Q →
    𝓢 ⊢ ∼τ

/-- **S5f. A conditional with determinate parts is determinate** (Corradini and Galvan's Lemma 2, given
Lemma 1). By the determinateness axiom for conditionals: if the system proves `σ` determinate and proves `G`
determinate, it proves `σ → G` determinate. -/
def ConditionalDeterminateIfPartsAre : Prop :=
  ∀ (Fm S : Type) [LogicalConnective Fm] [LogicalNeutral Fm] [Entailment S Fm] (𝓢 : S) [Entailment.Cl 𝓢]
    (T D : Fm → Fm) (σ G : Fm),
    DeterminateImp 𝓢 D T → 𝓢 ⊢ D σ → 𝓢 ⊢ D G → 𝓢 ⊢ D (σ 🡒 G)

end GodelArgument
