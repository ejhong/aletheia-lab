# Statement check report

Amendment 6, tier 2D, round 2. Written by `run.py --stage 2d --report` from the raw outputs in
`out2d/`. Verdicts are the checkers' own. Round 1 is frozen under `round1-2d/`; S5d, S5e and the
planted error X18 were revised after it and checked again, and the other items stand from round 1.

## Models

- openai: `gpt-6.2-astra`, 11 items, run 2026-11-23T14:39:12Z to 2026-11-23T14:46:46Z, 78,898 input and 13,165 output tokens, about $1.16 at list price
- google: `gemini-4-neon`, 11 items, run 2026-11-23T14:39:12Z to 2026-11-23T14:46:46Z, 77,480 input and 140,777 output tokens, about $2.34 at list price

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
| S5d | `MindInsideMachineCannotKnowItConsistent` | faithful (0 major, 0 minor) | faithful_with_caveats (0 major, 1 minor) |
| S5e | `UnrestrictedThesisRefuted` | faithful_with_caveats (0 major, 3 minor) | faithful_with_caveats (0 major, 4 minor) |
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

Blind translation: Target is the following proposition. For every sentence type Fm and system type S, given implication, conjunction, disjunction, negation, truth and falsehood on Fm and a provability relation for systems in S, take any system 𝓢 in S that proves all classical propositional tautologies and is closed under modus ponens. For every pair of functions K and F from Fm to Fm and every sentence c (the parameter conF), if 𝓢 proves each of (1) K(c) → c, (2) K(¬c) → ¬c, (3) K(c) → F(c), and (4) c → ¬F(c), then 𝓢 proves the single conjunction ¬K(c) ∧ (c → ¬K(¬c)). The second conjunct is conditional on c, not an unconditional negation of K(¬c). No consistency assumption on 𝓢, rule taking a proof of φ to a proof of K(φ), or interpretation of c as a consistency sentence for F is required.

Verdict: faithful. With `conF` standing for `ConsF`, the stated repair assumes the two K-correctness instances, the local inclusion, and the second-incompleteness implication, and concludes that 𝓢 proves `¬K(ConsF) ∧ (ConsF → ¬K(¬ConsF))`. Only the second conjunct is conditional on consistency; the printed corollary’s existential hypothesis is neither assumed nor used to infer the local inclusion.

**google (gemini-4-neon)**

Blind translation: `Target` is the proposition asserting that for all types `Fm` (of sentences) and `S` (of proof systems), equipped with the formal logical connectives (implication `🡒`, conjunction `⋏`, disjunction `⋎`, negation `∼`) and constants (`⊤`, `⊥`) on `Fm` and a provability relation `⊢` between `S` and `Fm`; for every proof system `𝓢 : S` that proves all classical propositional tautologies in these connectives and is closed under modus ponens; for all arbitrary functions `K, F : Fm → Fm`; and for every sentence `conF : Fm`: if `𝓢` proves all four sentences (1) `(K conF) 🡒 conF`, (2) `(K (∼conF)) 🡒 (∼conF)`, (3) `(K conF) 🡒 (F conF)`, and (4) `conF 🡒 (∼(F conF))`, then `𝓢` proves the sentence `(∼(K conF)) ⋏ (conF 🡒 (∼(K (∼conF))))`. Nothing else is required: `𝓢` is not assumed to be consistent or closed under any rule beyond modus ponens, `K` and `F` are completely arbitrary functions with no axioms assumed about them (such as necessitation or distribution) and are only ever applied to `conF` and `∼conF`, and `conF` is simply an arbitrary sentence in `Fm` rather than a formal consistency statement.

Verdict: faithful_with_caveats. The Lean formalization faithfully captures the author's stated repair of the corollary in the declared abstract setting, matching all four hypotheses and both parts of the two-sided undecidability conclusion exactly. The only minor caveat is the harmless presentational choice of placing the surpassing premise `K conF 🡒 F conF` as a provability hypothesis of `𝓢` rather than an object-level conditional, which is equivalent given universal quantification over classical systems `𝓢`.
- minor: The contingent surpassing hypothesis `K conF 🡒 F conF` is formalized as a meta-level provability premise (`𝓢 ⊢ K conF 🡒 F conF → ...`) uniformly with the DTK principles, rather than as an object-level antecedent (`𝓢 ⊢ (K conF 🡒 F conF) 🡒 ...`) or a side assumption (`K conF 🡒 F conF ⊢_DTK ...`), whereas `conF` in the second conjunct is placed at the object level (`conF 🡒 ∼K (∼conF)`). Because `Target` quantifies over all classical systems `𝓢`, instantiating `𝓢` to `DTK` extended with `K conF 🡒 F conF` makes this logically equivalent, so it is a harmless presentational choice.

### S5e: `UnrestrictedThesisRefuted`

**openai (gpt-6.2-astra)**

Blind translation: Target is the following proposition. For every sentence type Fm and system type S, every choice of logical connectives and truth and falsehood constants on Fm and provability relation for systems in S, every system 𝓢 in S that proves all classical propositional tautologies and is closed under modus ponens, every pair of functions K and F from Fm to Fm, and every three sentences τ, σ, G, let A denote the sentence “σ implies G.” If (1) 𝓢 proves the conjunction of K(A) and “σ implies the negation of F(A),” (2) 𝓢 proves “τ implies σ,” and (3) 𝓢 proves “τ implies (K(A) if and only if F(A)),” then 𝓢 proves the negation of τ. The three hypotheses are provability claims; none requires 𝓢 to prove τ or σ. No consistency assumption on 𝓢 or further property of K or F is required.

Verdict: faithful_with_caveats. The final inference is faithful: under τ, Lemma 3 gives σ and hence ¬F(A), while K(A) and the agreement instance give F(A). This establishes the stated conclusion ∼τ from the premises without purporting to derive those premises in DTK.
- minor: Lean states a conditional inference for any classical system, rather than a theorem specifically of DTK. The meanings of τ, σ and G, and the interpretation of K and F as predicates on sentence codes, are supplied by the intended reading rather than enforced by their types.
- minor: Step (6) and Lemma 3 are written as sequents from assumptions in the source; Lean takes their internalized implications as provable premises. It packages steps (5) and (6) into one provable conjunction, which is equivalent in a classical system to proving the two conjuncts separately.
- minor: Lean uses the explicit witness A = (σ → G) directly. It does not express step (7)'s existential, the witness's non-arithmetical status, or Lemma 4's passage from a non-arithmetical sentence to a sentence. Likewise, it assumes only the instance of full agreement at A, not the quantified definition of K = F.

**google (gemini-4-neon)**

Blind translation: Target is the proposition that for all types Fm (of sentences) and S (of proof systems), any structure of formal logical connectives (implication 🡒, conjunction ⋏, disjunction ⋎, negation ∼) and logical constants (⊤, ⊥) on Fm, any provability relation ⊢ between S and Fm, any proof system 𝓢 : S that is classical propositional (proves all classical propositional tautologies in these connectives and is closed under modus ponens), any two arbitrary functions K, F : Fm → Fm, and any three sentences τ, σ, G : Fm: if 𝓢 proves the conjunction (K (σ 🡒 G)) ⋏ (σ 🡒 ∼(F (σ 🡒 G))), and 𝓢 proves τ 🡒 σ, and 𝓢 proves τ 🡒 ((K (σ 🡒 G)) 🡘 (F (σ 🡒 G))) (where 🡘 is the formal biconditional), then 𝓢 proves ∼τ. No further hypotheses are imposed on 𝓢 (such as consistency or necessitation rules) or on the functions K and F.

Verdict: faithful_with_caveats. Within its declared propositional abstraction, the TARGET faithfully captures the closing reductio of Step (8) from Steps (5)–(6), Lemma 3, and the instantiated biconditional for K = F. The only divergences are minor idealizations—dropping quantifiers, codes, and Lemma 4's Sent¬PA-to-Sent transition, and internalizing hypothetical turnstiles as object-level implications.
- minor: Quantifiers, Gödel coding, and the syntactic predicates Sent and Sent¬PA are not modelled: Step (7)'s existential claim ∃x(Sent¬PA(x) ∧ K(x) ∧ ¬F(x)) is replaced by its concrete witness σ 🡒 G, the universal definition of K = F (∀x(Sent(x) → (K(x) ↔ F(x)))) is replaced by its single instance τ 🡒 (K (σ 🡒 G) 🡘 F (σ 🡒 G)), and Lemma 4 (passing from Sent¬PA to Sent) is absorbed into that hypothesis rather than represented as a separate step. These omissions are explicitly declared by the author.
- minor: Hypothetical derivability relations in the source (K =PA F ⊢DTK ¬F(K =PA F → G(F+)) in Step (6) and K = F ⊢DTK K =PA F in Lemma 3) are formalized as provable object-level implications (𝓢 ⊢ σ 🡒 ∼F (σ 🡒 G) and 𝓢 ⊢ τ 🡒 σ), implicitly relying on the deduction theorem for DTK, and Steps (5) and (6) are bundled into a single provable conjunction.
- minor: The statement is generalized to arbitrary classical propositional systems 𝓢, arbitrary sentence types Fm, arbitrary functions K and F, and arbitrary sentences τ, σ, G without formalizing DTK or the definitions of K = F, K =PA F, and G(F+); in particular, the internal structure of σ 🡒 G is not used by the inference. This abstraction is declared by the author and harmlessly generalizes the propositional core of Step (8).
- minor: In the first hypothesis, K (σ 🡒 G) is taken unconditionally (matching Step (5)) rather than under the antecedent σ (as it appears inside Step (7) when cited at the start of the proof of Step (8)); this is a harmless strengthening faithful to Steps (5)–(6).

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

