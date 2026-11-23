# Statement check report

Amendment 6, tier 2D. Written by `run.py --stage 2d --report` from the raw outputs in `out2d/`.
Verdicts are the checkers' own.

## Models

- openai: `gpt-6.2-astra`, 11 items, run 2026-11-23T14:39:12Z to 2026-11-23T14:40:16Z, 78,097 input and 15,166 output tokens, about $1.23 at list price
- google: `gemini-4-neon`, 11 items, run 2026-11-23T14:39:12Z to 2026-11-23T14:43:49Z, 76,608 input and 137,711 output tokens, about $2.30 at list price

## Planted errors

| Item | Planted error | openai | google |
|---|---|---|---|
| X16 | The second conjunct says the system's theorem set is Sound (all its theorems are true) where the claim says it is consistent. That contradicts the last two conjuncts and makes the statement false. | divergent | divergent |
| X17 | The second hypothesis is 'conF → (F φ → φ)' without K in front, where the claim and the passage have it known (the line after K-intro). Without K the conclusion does not follow. | divergent | divergent |
| X18 | Lemma 3 is reversed: the hypothesis is σ → τ where the claim and the passage have τ → σ. With the reversed hypothesis the conclusion does not follow. | divergent | divergent |

A planted error counts as caught when the verdict is `divergent`.

## Real items

| Item | Lean names | openai | google |
|---|---|---|---|
| DEF-P | `PAPlusNotCon` | faithful_with_caveats (0 major, 1 minor) | faithful_with_caveats (0 major, 1 minor) |
| S5a | `ConsistencyDoesNotGiveSoundness` | faithful_with_caveats (0 major, 2 minor) | faithful_with_caveats (0 major, 1 minor) |
| S5b | `MachineOutrunsMindThatKnowsItConsistent` | faithful (0 major, 0 minor) | faithful_with_caveats (0 major, 1 minor) |
| S5g | `MindAssumptionsDoNotDecide` | faithful (0 major, 0 minor) | faithful (0 major, 0 minor) |
| S5c | `CorollaryHoldsWhereConsistencyGivesSoundness` | faithful_with_caveats (0 major, 3 minor) | faithful_with_caveats (0 major, 4 minor) |
| S5d | `MindInsideMachineCannotKnowItConsistent` | divergent (1 major, 0 minor) | divergent (1 major, 3 minor) |
| S5e | `UnrestrictedThesisRefuted` | faithful_with_caveats (0 major, 4 minor) | divergent (2 major, 4 minor) |
| S5f | `ConditionalDeterminateIfPartsAre` | faithful_with_caveats (0 major, 2 minor) | faithful_with_caveats (0 major, 2 minor) |

## Divergences listed for real items

### DEF-P: `PAPlusNotCon`

**openai (gpt-6.2-astra)**

Blind translation: Target is a noncomputable definition of an arithmetic theory. Its axioms are exactly the axioms of Peano arithmetic (PA) together with one sentence: the formal negation of the consistency sentence for PA’s Craig presentation. This presentation is obtained from PA’s recursively enumerable axiom set and has the same theorems as PA. Its consistency sentence says that falsehood is not provable from that presentation; the added axiom negates that sentence. The definition takes the union of axiom sets, not their deductive closure. It has no quantified parameters or additional hypotheses and does not assert that PA is actually inconsistent.

Verdict: faithful_with_caveats. The definition keeps PA’s axioms and adds exactly one sentence, without taking deductive closure. The only caveat is the choice of presentation used to express PA’s inconsistency.
- minor: The added axiom is the negation of the consistency sentence for `𝗣𝗔.craig`, rather than the literal sentence `∼𝗣𝗔.consistent.val`. The Craig presentation proves exactly the same theorems as PA, so the added sentence still expresses PA’s inconsistency in the standard natural numbers.

**google (gemini-4-neon)**

Blind translation: Target defines an arithmetic theory—a set of sentences of first-order arithmetic (in the language ℒₒᵣ) used as axioms, not closed under deduction by definition—taking no parameters or explicit hypotheses. Specifically, it is the union of Peano arithmetic (PA) and the singleton set containing the object-language negation of the standard consistency sentence of PA.craig. Here PA.craig is the Δ₁-presented axiom set obtained by applying Craig's trick to PA (using that PA is recursively enumerable, yielding a Δ₁-presented theory with the same theorems as PA), and its consistency sentence is the arithmetic sentence ¬Prov_{PA.craig}(⌜⊥⌝), where Prov_{PA.craig} is the standard provability predicate built from PA.craig's Δ₁ presentation. Thus Target is the axiom set PA ∪ {¬(¬Prov_{PA.craig}(⌜⊥⌝))}, where both negations are inside the formal language; notably, the added axiom negates the consistency sentence constructed from the Craig's-trick presentation PA.craig rather than directly from a Δ₁ presentation of PA itself.

Verdict: faithful_with_caveats. The definition faithfully constructs the axiom set `PA ∪ {¬Con(PA)}` as claimed, with only the minor technical caveat that the consistency sentence is formed via Craig's trick (`Def7 𝗣𝗔 = 𝗣𝗔.craig.consistent.val`) rather than directly from `𝗣𝗔`'s native Δ₁ presentation.
- minor: Because `Target` uses `Def7 𝗣𝗔` (`𝗣𝗔.craig.consistent.val`), the added sentence is the negation of the consistency statement built from the Craig's-trick Δ₁ re-axiomatization `𝗣𝗔.craig` rather than directly from `𝗣𝗔`'s native Δ₁ presentation (`𝗣𝗔.consistent.val`). Since `𝗣𝗔.craig` has the exact same theorems as `𝗣𝗔`, this is a harmless implementation choice that preserves the intended role of `PA + ¬Con(PA)` as a consistent, recursively enumerable, unsound theory.

### S5a: `ConsistencyDoesNotGiveSoundness`

**openai (gpt-6.2-astra)**

Blind translation: For a recursively enumerable arithmetic axiom set A, write C(A) for the arithmetic sentence saying that no contradiction is provable from the Craig presentation of A. Let B be PA with the single additional axiom ¬C(PA). Target says that there exists a witness that B is recursively enumerable such that, using that witness to form C(B), all four conditions hold: (1) the set of all theorems of B, itself used as an axiom set, does not prove a contradiction; (2) C(B) is true in the standard natural numbers; (3) ¬C(PA) belongs to the set of theorems of B; and (4) that same sentence, ¬C(PA), is not true in the standard natural numbers. Condition (2) does not require B to prove C(B).

Verdict: faithful_with_caveats. The target gives the claimed standard-model counterexample: `Def9` is recursively enumerable and consistent, its consistency sentence is true, and it proves the false arithmetic sentence `∼Def7 𝗣𝗔`. Thus the quoted implication fails on the arithmetic-truth reading; the target makes no claim about what DTK proves.
- minor: `Def7` uses the consistency sentence of a Craig presentation, both for PA and for `Def9`. This need not be syntactically identical to a consistency sentence built from the original axioms, but the Craig presentation has the same theorems, so it expresses the intended consistency in the standard model.
- minor: `Def4 Def9.theory` asserts consistency of the theorems of `Def9` used as axioms, rather than consistency of `Def9` directly. These are equivalent because taking deductive closure does not change what is provable.

**google (gemini-4-neon)**

Blind translation: For any recursively enumerable arithmetic theory F, let Con*(F) denote the arithmetic sentence ¬Prov_{F.craig}(⌜⊥⌝), the standard consistency sentence built from Craig's Δ₁-presented axiom set F.craig (which has the same theorems as F). Let T be the arithmetic theory 𝗣𝗔 ∪ {∼Con*(𝗣𝗔)}, obtained by adjoining the formal negation of Con*(𝗣𝗔) to Peano arithmetic 𝗣𝗔. Target is the proposition (with no hypotheses or outer quantifiers) asserting that: (1) T is recursively enumerable (supplying the hypothesis needed to form Con*(T)); (2) the set of all theorems of T, used as an arithmetic theory, is consistent (does not prove a contradiction in classical first-order logic); (3) the sentence Con*(T) is true in the standard model of arithmetic ℕ; (4) the sentence ∼Con*(𝗣𝗔) belongs to the set of all theorems of T (i.e., is derivable from T); and (5) the sentence ∼Con*(𝗣𝗔) is not true in the standard model of arithmetic ℕ.

Verdict: faithful_with_caveats. Target matches all five clauses of the author's claim and provides a valid standard-model counterexample to 'ConsF → (∀ϕ ∈ L(PA))(Fϕ → ϕ)': Def9 is a consistent, recursively enumerable extension of PA whose consistency sentence is true in ℕ, yet it proves an arithmetic sentence (∼Def7 𝗣𝗔) that is false in ℕ. The only minor caveat is that consistency sentences are formed uniformly via Craig's trick presentations rather than PA's native Δ₁ presentation.
- minor: Def7 constructs consistency sentences uniformly via Craig's trick (F.craig.consistent.val), so ∼Def7 𝗣𝗔 is the inconsistency sentence for the Craig-trick Δ₁ presentation of PA rather than PA's canonical Δ₁ presentation (and similarly Def7 Def9 uses Def9.craig). Because F.craig has the same theorems as F, this is a harmless implementation choice that does not affect the validity of the counterexample.

### S5b: `MachineOutrunsMindThatKnowsItConsistent`

**openai (gpt-6.2-astra)**

Blind translation: For a recursively enumerable arithmetic axiom set F, let C(F) be the arithmetic sentence saying that falsehood is not provable from the Δ₁ axiom presentation obtained by Craig’s trick from F. Let A be the PA axioms together with the single additional axiom ¬C(PA). Target is the proposition that there is a witness that A is recursively enumerable and, with this witness used to form C(A), both of the following hold. (1) For every set K of arithmetic sentences, if every member of K is true in the standard natural numbers, then there is a sentence σ provable from A that is not a member of K. Here σ may depend on K; K need not be effectively presented or deductively closed, and the conclusion is nonmembership, not unprovability from K. (2) There exists a set K of arithmetic sentences such that there exists a recursively enumerable arithmetic axiom set F whose set of theorems is exactly K; every member of K is true in the standard natural numbers; every sentence provable using K as axioms belongs to K; every theorem of PA belongs to K (not necessarily a strict inclusion); and C(A) belongs to K.

Verdict: faithful. The TARGET states both (i) and (ii) for the same system A = PA + ¬Con(PA), using Craig presentations for the consistency sentences. Applying (i) to the sound mind K from (ii) gives an A-theorem outside K even though Con(A) belongs to K, contradicting the set-level implication without making any claim about DTK.

**google (gemini-4-neon)**

Blind translation: Let T be the arithmetic theory obtained by adding to Peano arithmetic (PA) the single axiom given by the formal negation of the standard consistency sentence for Craig's Δ₁ presentation of PA (that is, T = PA ∪ {∼(¬Prov_{PA.craig}(⌜⊥⌝))}, where for any recursively enumerable arithmetic theory F, its consistency sentence is formed as ¬Prov_{F.craig}(⌜⊥⌝) from Craig's Δ₁-presented version of F). Target is the proposition asserting that:
1. T is recursively enumerable;
2. for every set K of arithmetic sentences, if every sentence in K is true in the standard model of arithmetic (the natural numbers), then there exists an arithmetic sentence σ such that σ is a theorem of T (derivable from T in classical first-order logic) and σ is not in K; and
3. there exists a set K of arithmetic sentences such that:
   (a) there exists a recursively enumerable arithmetic theory F whose set of theorems (in classical first-order logic) equals K,
   (b) every sentence in K is true in the standard model of arithmetic,
   (c) K is closed under classical first-order deduction (every arithmetic sentence derivable from K belongs to K),
   (d) every theorem of PA belongs to K, and
   (e) the standard consistency sentence for Craig's Δ₁ presentation of T (namely ¬Prov_{T.craig}(⌜⊥⌝), formed using the recursive enumerability of T from (1)) belongs to K.

Verdict: faithful_with_caveats. The TARGET states exactly (i) and (ii) for the recursively enumerable system PA ∪ {∼Con(PA)}, and (i) and (ii) together directly contradict the set-level reading of Corradini and Galvan's corollary by instantiating (i) at the sound mind K witnessed by (ii). The only caveat is the minor technical choice of expressing consistency statements uniformly via Craig's Δ₁ re-axiomatization.
- minor: The consistency sentence Def7 F is defined via Craig's trick (F.craig.consistent.val) from a noncomputably chosen RE enumeration of F, rather than from a canonical Δ₁ presentation of PA and PA ∪ {¬Con(PA)}, and Def9 adjoins the classically equivalent double-negated form ∼(¬Prov_{PA.craig}(⌜⊥⌝)) rather than Prov_{PA}(⌜⊥⌝). Because consistency sentences are intensional (presentation-dependent), this is a technical representation choice, though standard for defining consistency uniformly on arbitrary RE theories.

### S5g: `MindAssumptionsDoNotDecide`

**openai (gpt-6.2-astra)**

Blind translation: Target defines a proposition as the conjunction of two existence claims. First, there is a set K of arithmetic sentences such that every member of K is true in the standard natural numbers, K used as axioms does not prove a contradiction, every sentence derivable from K belongs to K, every theorem of Peano arithmetic belongs to K, and there exists a recursively enumerable arithmetic axiom set F whose set of theorems is exactly K. Second, there is a set K′ of arithmetic sentences satisfying the same first four conditions, but there is no recursively enumerable arithmetic axiom set F whose set of theorems is exactly K′. The sets K and K′ are quantified separately and must differ because their last conditions are incompatible. Recursive enumerability is imposed on the presenting axiom set F, which is not required to equal the set of its theorems.

Verdict: faithful. Both minds are sound in the standard natural numbers, consistent, deductively closed, and contain every PA theorem. One is exactly the theorem set of a recursively enumerable axiom set and the other is not the theorem set of any such set, so the four conditions do not determine mechanicality; the target makes no claim about DTK or Reinhardt’s theorem.

**google (gemini-4-neon)**

Blind translation: Target is the proposition asserting the conjunction of two existential statements: (1) there exists a set K of sentences of first-order arithmetic such that every sentence in K is true in the standard model (the natural numbers), K is consistent (does not derive a contradiction in classical first-order logic), every arithmetic sentence derivable from K in classical first-order logic belongs to K, every theorem of Peano arithmetic belongs to K, and there exists a recursively enumerable set F of arithmetic sentences such that K equals the set of all arithmetic sentences derivable from F in classical first-order logic; and (2) there exists a set K of sentences of first-order arithmetic such that every sentence in K is true in the standard model (the natural numbers), K is consistent, every arithmetic sentence derivable from K in classical first-order logic belongs to K, every theorem of Peano arithmetic belongs to K, and there does not exist any recursively enumerable set F of arithmetic sentences such that K equals the set of all arithmetic sentences derivable from F in classical first-order logic.

Verdict: faithful. Target faithfully formalizes the author's claim: it asserts both the existence of a sound, consistent, deductively closed set of arithmetic sentences extending the theorems of PA that equals the theorem set of an RE axiom set, and the existence of another such set that is not the theorem set of any RE axiom set. Nothing in the formalization makes the statement trivial or stronger than claimed, and the contrast with Reinhardt's theorem in the source passage is explicitly disclaimed.

### S5c: `CorollaryHoldsWhereConsistencyGivesSoundness`

**openai (gpt-6.2-astra)**

Blind translation: Target is the following proposition. For every sentence type Fm and system type S, with implication, conjunction, disjunction, negation, truth and falsehood on Fm and a provability relation on Fm for systems in S; for every system 𝓢 in S that proves all classical propositional tautologies and is closed under modus ponens; for every pair of functions K and F from sentences to sentences; and for every pair of sentences conF and φ, suppose that (1) for every pair of sentences α and β, 𝓢 proves ‘K(α implies β) implies (K(α) implies K(β))’; (2) 𝓢 proves K applied to the entire sentence ‘conF implies (F(φ) implies φ)’; and (3) 𝓢 proves ‘F(φ) implies K(F(φ))’. Then 𝓢 proves the single implication ‘(not K(φ) and F(φ)) implies not K(conF)’. Hypotheses (2) and (3) concern the chosen sentences, not all instances. No consistency assumption on 𝓢, rule taking proofs of α to proofs of K(α), or interpretation of conF as a consistency sentence for F is required.

Verdict: faithful_with_caveats. The target faithfully captures the conditional reasoning for one sentence: given the local known conditional, distributivity and (∗) yield exactly the stated conclusion. It is a propositional analogue of the proof, not a derivation of the local premise from DTK’s quantified K-intro theorem.
- minor: The source applies K-intro to one sentence, ConsF → (∀φ ∈ L(PA))(Fφ → φ), with the quantifier inside K. It does not literally assert a family of theorems K(ConsF → (Fφ → φ)). Lean assumes this local analogue; obtaining it from the source’s line would require justifying specialization under K, not just ordinary universal elimination.
- minor: The source concludes a sequent from the existence of an arithmetic witness. Lean proves an object-language implication for a fixed φ: its antecedent supplies the witness properties directly, so neither the membership reasoning using (∗∗) nor the existential step is represented.
- minor: The result is schematic over classical systems and uninterpreted K, F and conF. It does not enforce that φ is arithmetic, that F expresses derivability on sentence codes, or that conF expresses consistency of that same formalism.

**google (gemini-4-neon)**

Blind translation: Target asserts the following proposition: For all types Fm (of sentences) and S (of proof systems), any choice of formal logical connectives (implication 🡒, conjunction ⋏, disjunction ⋎, negation ∼, truth ⊤, and falsehood ⊥) on Fm, any provability relation ⊢ between S and Fm, any proof system 𝓢 in S that proves every classical propositional tautology in these connectives and is closed under modus ponens, any functions K and F from Fm to Fm, and any sentences conF and φ in Fm: if (1) for all sentences α and β in Fm, 𝓢 proves K (α 🡒 β) 🡒 (K α 🡒 K β), (2) 𝓢 proves K (conF 🡒 (F φ 🡒 φ)), and (3) 𝓢 proves F φ 🡒 K (F φ), then 𝓢 proves ((∼(K φ)) ⋏ (F φ)) 🡒 ∼(K conF). Nothing else is assumed: 𝓢 is not required to be consistent or closed under any additional rules (such as necessitation for K or F); K and F are arbitrary functions from Fm to Fm with no further properties required; and conF is simply an arbitrary sentence in Fm with no requirement relating it to F or to consistency beyond its appearance in hypothesis (2) and the conclusion.

Verdict: faithful_with_caveats. As a single-sentence abstract rendering of the downstream proof of the corollary, the TARGET is faithful: its three hypotheses match Distributivity of K, the single-sentence instantiation of the K-intro line, and line (∗), and its conclusion matches the single-sentence form of the corollary. The divergences are minor and largely declared: the Lean omits arithmetic, coding, quantifiers, line (∗∗), the quantifier-K step, and the upstream derivations of (∗) and the K-intro line.
- minor: Quantifier elimination and omission of line (∗∗): the source derives the corollary from K(ConsF → (∀ϕ ∈ L(PA))(Fϕ → ϕ)), which requires moving the bounded universal quantifier outside K using line (∗∗) (ϕ ∈ L(PA) → K(ϕ ∈ L(PA))) and a quantifier-modality step (elided in the source's '[…]'). The TARGET instantiates the K-intro line inside K at a single sentence φ—namely K(conF 🡒 F φ 🡒 φ)—omitting the quantifiers, membership in L(PA), line (∗∗), and the quantifier-K interaction step. This is explicitly declared by the author as a single-sentence idealization.
- minor: Upstream derivations entered as hypotheses: the source proves line (∗) (Fϕ → K(Fϕ)) from Σ1-completeness and the Rule of mathematical knowledge, and proves the K-intro line from 'Cons implies Sound', determinateness, and the K-intro rule. The TARGET omits those upstream derivations and takes both lines as hypotheses, formalizing only the downstream classical-epistemic deduction to the corollary (as stated in the claim).
- minor: Abstract idealization of the system and predicates: 𝓢 is an arbitrary classical propositional system and K, F, conF, φ are arbitrary functions and sentences, with no modelling of arithmetic, Gödel coding, the specific system DTK, or the relationship between conF and F. This is a harmless strengthening/idealization relative to the propositional core of the proof.
- minor: Object-level implication vs. derivability from a premise: the source states the corollary as (∃ϕ ∈ L(PA))(¬Kϕ ∧ Fϕ) ⊢DTK ¬K(ConsF), whereas the TARGET concludes with an internal conditional theorem 𝓢 ⊢ ∼K φ ⋏ F φ 🡒 ∼K conF. Under classical logic this is a harmless presentational choice (and yields the premise-to-conclusion derivability by modus ponens).

### S5d: `MindInsideMachineCannotKnowItConsistent`

**openai (gpt-6.2-astra)**

Blind translation: Target is defined to be the following proposition. For every sentence type Fm and system type S, every choice of logical connectives and truth and falsehood constants on Fm, and every provability relation for systems of type S on sentences of type Fm, take any system 𝓢 in S that proves all classical propositional tautologies and is closed under modus ponens. For every pair of functions K and F from Fm to Fm and every sentence conF in Fm: if 𝓢 proves ‘K(conF) implies conF’, then if 𝓢 proves ‘K(conF) implies F(conF)’, then if 𝓢 proves ‘conF implies not F(conF)’, 𝓢 proves ‘not K(conF)’. The conclusion is a proof of a negation, not a claim that 𝓢 fails to prove K(conF). No consistency assumption on 𝓢 or additional property of K or F is required, and conF need not express consistency or have any prescribed relationship to F.

Verdict: divergent. The TARGET states the proposed repair exactly: its three provable implications suffice for `𝓢 ⊢ ∼K conF`. The local inclusion premise comes from the stipulated reading of “surpasses,” not from the existence of an F-derivable sentence that is not known.
- major: The TARGET concludes `𝓢 ⊢ ∼K conF`: it is not known that F is consistent. On the usual two-sided reading of “humanly undecidable,” the passage also rules out knowing that F is inconsistent. That would require `𝓢 ⊢ ∼K (∼conF)`, which does not follow from the premises. The printed corollary is not quoted, so the excerpts do not establish whether its literal conclusion is just the one-sided claim.

**google (gemini-4-neon)**

Blind translation: Target is the proposition stating that for every type Fm of sentences (equipped with the formal propositional connectives 🡒, ⋏, ⋎, ∼ and constants ⊤, ⊥), every type S of proof systems (equipped with a provability relation ⊢ on Fm), every proof system 𝓢 of type S that proves all classical propositional tautologies in these connectives and is closed under modus ponens, all arbitrary functions K and F from Fm to Fm, and every sentence conF of type Fm: if 𝓢 proves (K conF) 🡒 conF, 𝓢 proves (K conF) 🡒 (F conF), and 𝓢 proves conF 🡒 ∼(F conF), then 𝓢 proves ∼(K conF). Nothing else is required: 𝓢 is not assumed to be consistent or to satisfy any modal or necessitation rules, K and F are completely arbitrary functions with no assumed properties (and are only applied to the single sentence conF), and conF is an arbitrary sentence rather than a formal consistency statement.

Verdict: divergent. The TARGET matches the author's description of the repaired propositional inference—deriving `𝓢 ⊢ ∼K conF` from K-correctness at `conF`, inclusion `K conF 🡒 F conF`, and `conF 🡒 ∼F conF`—but its conclusion is materially weaker than the corollary's conclusion. Showing only `∼K conF` (that ConsF is not known) does not establish that the consistency of F is humanly undecidable, since it neither assumes F's consistency nor rules out `K(∼conF)`.
- major: The TARGET concludes only `𝓢 ⊢ ∼K conF` (that ConsF is not humanly known), whereas the corollary in [P-CG2-563] concludes that 'the consistency of F is humanly undecidable'. Undecidability requires that neither ConsF nor ¬ConsF is known (`∼K conF ⋏ ∼K(∼conF)`, or `∼D conF` in DTK's determinacy vocabulary); `∼K conF` establishes only one half (unverifiability of ConsF) and does not rule out `K(∼conF)`. In fact, `Target` omits any consistency assumption `conF` and any K-correctness instance `K(∼conF) 🡒 ∼conF`, so it applies even when F is inconsistent—a case in which ¬ConsF would be provable in PA and hence humanly known by the rule of mathematical knowledge in [P-CG2-557], making ConsF humanly decided rather than undecidable.
- minor: The TARGET omits the passage's clause that F derives some mathematical proposition not accessible to human knowledge (`∃ φ, F φ ∧ ¬K φ`) and replaces the general inclusion of K in F (read into 'F surpasses K') and the full K-correctness schema (`⊢DTK Kϕ → ϕ`) with single instances at `conF` (`𝓢 ⊢ K conF 🡒 F conF` and `𝓢 ⊢ K conF 🡒 conF`). Under the claim's reading of 'surpasses' as including `K ⊆ F`, these are weakenings of the hypotheses (strengthenings of the implication), though the printed passage does not explicitly state `K ⊆ F`.
- minor: Because of the declared abstract setting, arithmetic, coding, quantifiers, formal derivability in F, and the definition of ConsF are not modelled: `K` and `F` are arbitrary functions on an arbitrary sentence type, `conF` is an arbitrary sentence, and Gödel's second incompleteness theorem (`conF 🡒 ∼F conF`) is supplied as an uninterpreted hypothesis, reducing `Target` to a three-atom classical propositional tautology.
- minor: The TARGET expresses the dependence on the inclusion hypothesis as a derivability rule (`𝓢 ⊢ K conF 🡒 F conF → 𝓢 ⊢ ∼K conF`) requiring `𝓢` to prove the inclusion at `conF`, rather than as an object-level conditional or a meta-level semantic hypothesis about F and K (though quantifying over all classical systems `𝓢` allows recovering the object-level conditional via extension).

### S5e: `UnrestrictedThesisRefuted`

**openai (gpt-6.2-astra)**

Blind translation: Target is the following proposition. For every sentence type Fm and system type S, with logical connectives and truth and falsehood constants on Fm and a provability relation for systems in S, take any system 𝓢 in S that proves all classical propositional tautologies and is closed under modus ponens. For every function K from Fm to Fm and every choice of sentences τ, σ, G, Q in that order, if (1) 𝓢 proves the conjunction (K(σ implies G) and (σ implies not Q)), (2) 𝓢 proves (τ implies σ), and (3) 𝓢 proves (τ implies (K(σ implies G) implies Q)), then 𝓢 proves the negation of τ. In (1), K applies only to the sentence ‘σ implies G’, not to the whole conjunction. No property of K and no consistency of 𝓢 are required. The conclusion is provability of ‘not τ’, not a claim that 𝓢 does not prove τ.

Verdict: faithful_with_caveats. The target faithfully captures the propositional inference of step (8): under τ, Lemma 3 supplies σ and hence ¬Q, while knowledge of the same witness and the equality instance supply Q. The conclusion is provability of ¬τ, as in the passage.
- minor: The target states a conditional inference for any classical system, rather than a theorem specifically of DTK. It packages step (5) and the implication form of step (6) into one provable conjunction, and likewise writes Lemma 3 as a provable implication rather than a sequent. These changes preserve their use in step (8).
- minor: The intended meanings of τ, σ, G and Q are supplied by the interpretation, not enforced by Lean. In particular, Q is a sentence parameter, not the application of a formalized F to σ → G. Only K occurs as an operator, applied directly to sentences; codes, the arithmetic restriction in σ, and the construction of G from F+ are not represented.
- minor: The target uses the witness σ → G directly. It does not express step (7)'s existential or witness-identification clause, classify the witness as non-arithmetical, or express Lemma 4's passage from a non-arithmetical sentence to a sentence. Instead it assumes just the known-to-derivable direction of equality at that witness, which suffices for the contradiction.
- minor: The target is silent on determinacy. The author's gloss also misidentifies the scope of the source's final remark: the passage calls ∃F(K = F) and its negation provably indeterminate, not ¬τ for the fixed F of step (8). This does not change the step (8) conclusion.

**google (gemini-4-neon)**

Blind translation: `Target` is the proposition asserting that for every type `Fm` of sentences equipped with logical connectives (`🡒`, `⋏`, `⋎`, `∼`) and logical constants (`⊤`, `⊥`), every type `S` of proof systems equipped with a provability relation `⊢` between systems in `S` and sentences in `Fm`, every proof system `𝓢 : S` that proves every classical propositional tautology in these connectives and is closed under modus ponens, every arbitrary function `K : Fm → Fm`, and all sentences `τ`, `σ`, `G`, `Q : Fm`: if (1) `𝓢` proves `K(σ 🡒 G) ⋏ (σ 🡒 ∼Q)`, (2) `𝓢` proves `τ 🡒 σ`, and (3) `𝓢` proves `τ 🡒 (K(σ 🡒 G) 🡒 Q)`, then `𝓢` proves `∼τ`. Nothing further is assumed about `𝓢` (for instance, it need not be consistent) or about `K` (it is an arbitrary function from sentences to sentences with no axioms or inference rules required of it, and `G` appears only inside `K(σ 🡒 G)`).

Verdict: divergent. Target is divergent from Step (8) of Corradini and Galvan (2022) because it strips away DTK, the predicate F, quantifiers, sentence-hood domains (Sent, SentPA, Sent¬PA), the definitions of K = F and K =PA F, and Lemma 4, leaving only a three-premise tautology of arbitrary classical propositional logic. While the propositional skeleton mirrors the final reductio once every substantive step is assumed as an ad-hoc hypothesis, it fails to capture what Step (8) actually establishes.
- major: The formalization collapses Step (8) into a trivial tautology of arbitrary classical propositional logic (from A ∧ (σ → ¬Q), τ → σ, and τ → A → Q, derive ¬τ). No axioms or structure of DTK, K, F, T, or D are present; τ, σ, G, and Q are unconstrained sentences, K(σ 🡒 G) functions merely as an opaque propositional atom with K and G playing no formal role, and all substantive premises of Step (8) are assumed outright as ad-hoc propositional hypotheses rather than derived from the definitions of K = F and K =PA F.
- major: Quantifiers, coding, sentence-hood predicates (Sent, SentPA, Sent¬PA), and the quantified definitions of K = F (∀x(Sent(x) → (K(x) ↔ F(x)))) and K =PA F cannot be expressed and are omitted. Consequently, the existential witness structure and coding equivalence of Step (7) are dropped, Lemma 3 is merely assumed as τ 🡒 σ, Lemma 4 (lifting a non-arithmetical witness from Sent¬PA to Sent) disappears completely, and the universal biconditional K = F is replaced by a single one-way conditional instance τ 🡒 (K(σ 🡒 G) 🡒 Q). This erases the central conceptual distinction of Step (8): why the non-arithmetical witness refutes K = F without refuting K =PA F.
- minor: Even within the abstract propositional setting (where the author describes F as a function on sentences alongside K), the provability predicate F is not modelled as a function Fm → Fm at all; instead, F(K =PA F → G(F+)) is represented by an arbitrary, unlinked sentence Q.
- minor: Meta-level derivability from assumptions in DTK (such as K =PA F ⊢DTK ¬F(...) in Step (6), K = F ⊢DTK K =PA F in Lemma 3, and the intermediate lines of Step (8)) is internalized as provable object-language implications (𝓢 ⊢ σ 🡒 ∼Q, 𝓢 ⊢ τ 🡒 σ, 𝓢 ⊢ τ 🡒 K(σ 🡒 G) 🡒 Q), implicitly relying on a deduction theorem for DTK.
- minor: The first hypothesis 𝓢 ⊢ K(σ 🡒 G) ⋏ (σ 🡒 ∼Q) asserts K(σ 🡒 G) unconditionally (matching Step (5) combined with Step (6)), which is slightly stronger than Step (7) alone, where K(ψ) ∧ ¬F(ψ) appears under the assumption K =PA F.
- minor: The passage's concluding observation that ∃F(K = F) and ¬∃F(K = F) are provably indeterminate is not modelled (requiring both the determinacy predicate D and quantification over formal systems F). Note also that the claim describes this unmodelled remark as saying that ¬τ (i.e., K ≠ F) is indeterminate, whereas the passage states it for ∃F(K = F) and ¬∃F(K = F).

### S5f: `ConditionalDeterminateIfPartsAre`

**openai (gpt-6.2-astra)**

Blind translation: Target is defined to be the following proposition. For every sentence type Fm and system type S, every choice of implication, conjunction, disjunction, negation, truth and falsehood on Fm, every provability relation for S on Fm, every system 𝓢 in S that proves all classical propositional tautologies and is closed under modus ponens, every pair of functions T, D from Fm to Fm, and every pair of sentences σ, G in Fm: if (1) for every sentence φ and every sentence ψ, 𝓢 proves the biconditional D(φ ⇒ ψ) ⇔ (D(φ) ∧ (T(φ) ⇒ D(ψ))), (2) 𝓢 proves D(σ), and (3) 𝓢 proves D(G), then 𝓢 proves D(σ ⇒ G). The biconditional, conjunction and implications within the displayed sentences are connectives of Fm; the outer if–then is a rule about provability. Neither consistency of 𝓢 nor a proof of σ, G or T(σ) is required.

Verdict: faithful_with_caveats. Within the declared abstraction, the inference is exact: the relevant D4 instance and proofs of D(σ) and D(G) suffice for a proof of D(σ → G), without a proof of T(σ).
- minor: The TARGET states a rule for any classical system and any sentences σ and G. It does not identify them with DTK, K =PA F, and G(F+); the determinateness results for those particular sentences enter as premises.
- minor: Def11 requires the system to prove each sentence instance of D4. It does not express the source’s single internally quantified axiom over codes: the type Fm takes the place of the Sent guards.

**google (gemini-4-neon)**

Blind translation: Target is the proposition that for every type Fm of sentences equipped with the formal logical connectives (implication 🡒, conjunction ⋏, disjunction ⋎, negation ∼, with biconditional 🡘 abbreviating (a 🡒 b) ⋏ (b 🡒 a)) and logical constants (⊤ and ⊥), every type S of proof systems equipped with a provability relation ⊢ on Fm, every proof system 𝓢 in S that proves all classical propositional tautologies and is closed under modus ponens, every pair of arbitrary functions T and D from Fm to Fm, and every pair of sentences σ and G in Fm: if (1) for all sentences φ and ψ in Fm, 𝓢 proves D (φ 🡒 ψ) 🡘 (D φ ⋏ (T φ 🡒 D ψ)) (i.e., Def11 𝓢 D T holds), (2) 𝓢 proves D σ, and (3) 𝓢 proves D G, then 𝓢 proves D (σ 🡒 G). No other assumptions are made: in particular, 𝓢 is not required to be consistent or to satisfy any necessitation rule, and T and D are arbitrary functions from sentences to sentences with no assumptions other than (1).

Verdict: faithful_with_caveats. The TARGET accurately formalizes the claimed propositional inference step of Lemma 2 from axiom D4 (as a schema) and the determinateness of σ and G to the determinateness of σ → G. The only divergences from the source passage are the declared idealizations of working in an abstract classical propositional setting without arithmetic, coding, quantifiers, or the derivations of the two determinateness premises.
- minor: Axiom D4 is formalized in Def11 as a propositional schema (meta-quantified over all sentences φ and ψ) rather than the single object-language universally quantified axiom over Gödel codes of sentences in DT, since arithmetic, coding, and quantifiers are not modelled.
- minor: In the source, Lemma 2 is an unconditional theorem of the specific arithmetical system DTK for the specific sentences 'K =PA F' and 'G(F+)'; the Lean statement generalizes this to an arbitrary classical propositional system 𝓢, arbitrary operators D and T (omitting the definition of D(x) as T(x) ∨ T(¬x)), and arbitrary sentences σ and G, taking 𝓢 ⊢ D σ and 𝓢 ⊢ D G as explicit hypotheses rather than deriving them from Lemma 1 and the arithmeticality of G(F+).

