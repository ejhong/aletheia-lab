# Source passages for the statement check

Short verbatim quotations, each with a locator. Mathematical symbols lost in text extraction were restored from
the page images. Copies read are listed in `../MANIFEST.md`.

## P-K350 — Koellner (2018), Part I, p. 350, §II.1

> In the informal setting 'F' was used to stand for the set of sentences provable relative to a given formal system (or, in the variant formulation, the set of sentences that can be produced by "an idealized finite machine"). It is well-known how to sharpen this notion. In fact, in this case we have a substantive analysis of the notion: The informal notion of being "provable relative to a given formal system" is rendered mathematically precise in terms of the notion of being "provable relative to a recursive set of axioms." […] We will let 'F_e' stand for the set of sentences provable relative to the e-th recursively enumerable set of axioms, where 'e' ranges over the natural numbers.

## P-K351 — Koellner (2018), Part I, pp. 350–351, §§II.2–II.3

> In the informal setting 'T' was used to stand for the set of sentences that are true. […] In the informal setting 'K' was used to stand for the set of sentences that are "absolutely provable" (or, in the variant formulation, the set of sentences that can be produced by "the idealized human mind").

## P-K345 — Koellner (2018), Part I, pp. 344–345, §I.2

> Theorem 1 (Gödel). Assume that PA is consistent. Then there is a sentence φ in L_PA such that PA cannot prove φ, and PA cannot prove ¬φ. […] Theorem 2 (Gödel). Assume that PA is consistent. Then PA cannot prove Con(PA). Here 'Con(PA)' is a statement in L_PA which formally renders the informal statement that PA is consistent. The point, for present purposes, is that this is a Π⁰₁-statement. […] It is important to stress that these theorems are perfectly general. We have stated them for one particular system, namely, PA, but they apply to any sufficiently strong formal system.

## P-K354 — Koellner (2018), Part I, p. 354, §III.2

> The second claim involves K. It asserts that for any formal system F, K(F ⊆ T) → F ⊊ K. This is also provable in EA_T. In fact, something stronger is provable already in EA. The antecedent of the above conditional is the statement that it is absolutely provable that F is correct (that is, K(F ⊆ T)). But a weaker condition is the scheme asserting that for any φ in L_PA, it is absolutely provable that if F holds of φ then φ holds (that is, for any φ in L_PA, K(F(⌜φ⌝) → φ)). […] Theorem 3 (Reinhardt). Assume that S includes EA. Suppose F(x) is a formula with one free variable and is such that for each sentence φ, S ⊢ K(F(⌜φ⌝) → φ). Then there is a sentence ψ such that S ⊢ Kψ ∧ K¬F(⌜ψ⌝).

## P-K357 — Koellner (2018), Part I, p. 357, §IV.2

> it is useful to distinguish (following Reinhardt) three grades of the mechanistic thesis: (1) (WMT) ∃e (K = F_e); (2) (SMT) K ∃e (K = F_e); (3) (SSMT) ∃e K(K = F_e). The first thesis is the weak mechanistic thesis. It asserts that there is a Turing machine which coincides with the idealized human mind (in the sense that the two have the same outputs). This is simply the first disjunct of Gödel's Disjunction. […] The third thesis is the super strong mechanistic thesis. It asserts that there is a particular Turing machine such that the idealized human mind knows that that particular machine coincides with the idealized human mind.

## P-K359 — Koellner (2018), Part I, pp. 358–359, §IV.3, quoting Wang's report of Gödel (Wang, *A Logical Journey*, §6.1.7, p. 186); bracketed glosses are Koellner's

> The incompleteness results do not rule out the possibility that there is a theorem-proving computer [F_e] which is in fact equivalent to mathematical intuition [K = F_e]. But they imply that, in such a—highly unlikely for other reasons—case, either we do not know the exact specification of the computer [¬K(K = F_e)] or we do not know that it works correctly [¬K(F_e ⊆ T)].

## P-K356 — Koellner (2018), Part I, p. 356, §IV.1, quoting Penrose, *Shadows of the Mind*, p. 76

> It turns out that the first generation of arguments for the first disjunct are really just versions of Gödel's argument for his second claim, namely that if K(F ⊆ T) then F ⊊ K. In the words of Penrose: "Human mathematicians are not using a knowably sound algorithm in order to ascertain mathematical truth." […] However, as Gödel (and many logicians who followed) pointed out, the argument does not yield the first disjunct; rather, it provides us with a conditional statement, and to arrive at the consequent of the conditional, one needs to discharge the antecedent; that is, one needs the additional premise that K(F ⊆ T). The question, then, is whether for any F one can determine (in the sense of absolutely prove or refute) whether or not F is correct. This would involve, in the very least, being able to determine whether or not F is consistent.

## P-C1 — Chalmers (1995), §1 "The First Argument"

> what would we expect, given the truth of Gödel's theorem, if our reasoning powers could be captured by some formal system F. One possibility is that F is essentially unsound, so that Gödel's theorem does not apply. But what if F is sound? Then we would expect that: (a) F could not prove its Gödel sentence G(F); (b) F could prove the conditional "If F is consistent, then G(F) is true"; (c) F could not prove that F is consistent. If our reasoning powers are capturable by some sound formal system F, then, we should expect that we will be unable to see that F is consistent. […] There does not seem to be anything especially paradoxical about this situation. Many arguments from Gödel's theorem, such as that given by Lucas, founder at just this point: they offer us no reason to believe that we can see the truth of our own Gödel sentence, as we may be unable to see the consistency of the associated formal system.

## P-C1b — Chalmers (1995), §1, closing sentence

> I conclude that none of Penrose's argument up to this point put a dent in the natural AI position: that our reasoning powers may be captured by a sound formal system F, where we cannot determine that F is sound.

## P-C2 — Chalmers (1995), §2 "Penrose's Second Argument"

> we can argue that any system that "unassailably" believes in its own consistency will in fact be led to a contradiction (under certain plausible further assumptions). […] we can assume it has a symbol B, representing belief, where B(n) corresponds to the statement that it believes the statement with Gödel number n. […] And let us write |- A if the system has the power to "unassailably" assert A. (By using this notation I do not intend to beg the question about whether the system is computational!) Then the following assumptions are reasonable (suppressing universal qualifiers): (1) If |- A, then |- B(A). (2) |- B(A_1) & B(A_1 -> A2) -> B(A2) (3) |- B(A) -> B(B(A)) […] To these we add the key assumption: (4) |- not B(false) which says that the system asserts that it is not inconsistent. It turns out that these assumptions, along with the assumption that the system has the resources to do Peano arithmetic, lead to a contradiction. To see this, we simply construct a sentence G such that (5) |- G <-> not B(G). This is a standard diagonal construction, and does not rely on any assumptions about the system's computability.

## P-C2b — Chalmers (1995), §2, conclusion

> We can see, then, that the assumption that we know we are sound leads to a contradiction. […] All Gödelian arguments appeal to this premise somewhere, but in fact the premise generates a contradiction. Perhaps we are sound, but we cannot know unassailably that we are sound.

## P-C2c — Chalmers (1995), §2, step (2) of his summary of Penrose's argument

> Given that I know that I am F, I know that F is sound (as I know that I am sound). Indeed, I know that the larger system F' is sound, where F' is F supplemented by the further assumption "I am F". (Supplementing a sound system with a true statement yields a sound system.)

## P-L115 — Lucas (1961), pp. 115–116

> The conclusions it is possible for the machine to produce as being true will therefore correspond to the theorems that can be proved in the corresponding formal system. We now construct a Gödelian formula in this formal system. This formula cannot be proved-in-the-system. Therefore the machine cannot produce the corresponding formula as being true. But we can see that the Gödelian formula is true […] for every machine there is a truth which it cannot produce as being true, but which a mind can. This shows that a machine cannot be a complete and adequate model of the mind.

## P-L116 — Lucas (1961), pp. 116–117

> those who, finding a formula their first machine cannot produce as being true, concede that that machine is indeed inadequate, but thereupon seek to construct a second, more adequate, machine, in which the formula can be produced as being true. This they can indeed do: but then the second machine will have a Gödelian formula all of its own, constructed by applying Gödel's procedure to the formal system which represents its (the second machine's) own, enlarged, scheme of operations.

## P-K349 — Koellner (2018), Part I, p. 349, quoting Gödel (1951), *Collected Works* III, p. 310

> So the following disjunctive conclusion is inevitable: Either mathematics is incompletable in this sense, that its evident axioms can never be comprised in a finite rule, that is to say, the human mind (even within the realm of pure mathematics) infinitely surpasses the powers of any finite machine, or else there exist absolutely unsolvable diophantine problems of the type specified (where the case that both terms of the disjunction are true is not excluded, so that there are, strictly speaking, three alternatives). In other words, we have Gödel's Disjunction: Claim 3. Either (¬∃F (F = K)) or (∃φ (φ ∈ T ∧ φ ∉ K ∧ ¬φ ∉ K)). The argument for the disjunction is not too hard to provide informally: Suppose that there were an F* such that F* = K. Then we have F* ⊆ T (since K ⊆ T). So, by the incompleteness theorems, we have F* ⊊ T. Thus, there is a φ ∈ T such that φ ∉ F*, and for any such φ we also have ¬φ ∉ F* (since if ¬φ ∈ F* then ¬φ ∈ T (as F* ⊆ T), which is impossible since φ ∈ T). But F* = K. So this φ is such that φ ∈ T and yet neither φ ∈ K nor ¬φ ∈ K.

## P-P73 — Penrose (1994), *Shadows of the Mind*, §2.5, p. 73 (footnote mark and italics omitted)

> Suppose, then, that we have some computational procedure A which, when it terminates, provides us with a demonstration that a computation such as C(n) actually does not ever stop. We are going to try to imagine that A encapsulates all the procedures available to human mathematicians for convincingly demonstrating that computations do not stop. […] I am certainly not requiring that A can always decide that C(n) does not stop when in fact it does not, but I do insist that A does not ever give us wrong answers, i.e. that if it comes to the conclusion that C(n) does not stop, then in fact it does not. If A does not in fact give us wrong answers, we say that A is sound.

## P-P74 — Penrose (1994), *Shadows of the Mind*, §2.5, p. 74 (subscripts written C_q; italics omitted)

> All the possible different computations C can in fact be listed, say as C_0, C_1, C_2, C_3, C_4, C_5, . . ., and we can refer to C_q as the qth computation. […] A is just any sound set of computational rules for ascertaining that some computations C_q(n) do not ever halt. Being dependent upon the two numbers q and n, the computation that A performs can be written A(q, n), and we have: (H) If A(q, n) stops, then C_q(n) does not stop.

## P-P75 — Penrose (1994), *Shadows of the Mind*, §2.5, p. 75 (subscripts written C_k; italics omitted)

> With q equal to n, we now have: (I) If A(n, n) stops, then C_n(n) does not stop. We now notice that A(n, n) depends upon just one number n, not two, so it must be one of the computations C_0, C_1, C_2, C_3, . . . (as applied to n), since this was supposed to be a listing of all the computations that can be performed on a single natural number n. Let us suppose that it is in fact C_k, so we have: (J) A(n, n) = C_k(n). Now examine the particular value n = k. […] We have, from (J), (K) A(k, k) = C_k(k) and, from (I), with n = k: (L) If A(k, k) stops, then C_k(k) does not stop. Substituting (K) in (L), we find: (M) If C_k(k) stops, then C_k(k) does not stop. From this, we must deduce that the computation C_k(k) does not in fact stop. (For if it did then it does not, according to (M)!) But A(k, k) cannot stop either, since by (K), it is the same as C_k(k). Thus, our procedure A is incapable of ascertaining that this particular computation C_k(k) does not stop even though it does not. Moreover, if we know that A is sound, then we know that C_k(k) does not stop. Thus, we know something that A is unable to ascertain. It follows that A cannot encapsulate our understanding.

## P-P76 — Penrose (1994), *Shadows of the Mind*, §2.5, pp. 75–76 (italics omitted)

> We have found a computation C_k(k) that we know does not stop; yet the given computational procedure A is not powerful enough to ascertain that fact. This is the Gödel(–Turing) theorem in the form that I require. It applies to any computational procedure A whatever for ascertaining that computations do not stop, so long as we know it to be sound. We deduce that no knowably sound set of computational rules (such as A) can ever suffice for ascertaining that computations do not stop, since there are some non-stopping computations (such as C_k(k)) that must elude these rules. Moreover, since from the knowledge of A and of its soundness, we can actually construct a computation C_k(k) that we can see does not ever stop, we deduce that A cannot be a formalization of the procedures available to mathematicians for ascertaining that computations do not stop, no matter what A is. Hence: 𝒢 Human mathematicians are not using a knowably sound algorithm in order to ascertain mathematical truth.

## P-K352 — Koellner (2018), Part I, pp. 351–352, §II.3

> In the formal setting we will treat 'K' as an operator. The basic axioms of absolute provability are: (K1) Universal closures of formulas of the form Kφ where φ is a first-order validity. (K2) Universal closures of formulas of the form (K(φ → ψ) ∧ Kφ) → Kψ. (K3) Universal closures of formulas of the form Kφ → φ. (K4) Universal closures of formulas of the form Kφ → KKφ.

## P-K353 — Koellner (2018), Part I, p. 353, §II.4

> The language L_EA is L_PA expanded to include an operator 'K' that takes formulae of L_EA as arguments. The axioms of arithmetic are simply those of PA, only now the induction scheme is taken to cover all formulas in L_EA. For a collection Γ of formulas in L_EA, let 'KΓ' denote the collection of formulas 'Kφ' where 'φ' is in Γ. The system EA is the theory axiomatized by Σ ∪ KΣ, where Σ consists of the axioms of PA (in the language L_EA) and the basic axioms of absolute provability.

## P-K354b — Koellner (2018), Part I, p. 354, §III.2, after Theorem 3

> Notice that here 'F(x)' stands for any formula in L_EA with one free variable. It need not be a formula defining what is provable relative to a recursive set of axioms; that is, it need not be a Σ⁰₁-statement. The result applies to even richer notions of relative provability. It is worth mentioning that one also obtains an absolute version of the second incompleteness theorem: Theorem 4 (Reinhardt). Assume that S includes EA. Suppose F(x) is a formula with one free variable and is such that for each sentence φ, S ⊢ K(Kφ → F(⌜φ⌝)). Then S ⊢ K¬K(Con(F)). In other words, if it is absolutely provable (pointwise) that the system F captures everything that is absolutely provable then (it is absolutely provable that) the consistency of F is not absolutely provable.

## P-K357b — Koellner (2018), Part I, p. 357, §IV.2

> Theorem 6 (Reinhardt). 'EA_T + SSMT' is inconsistent. In other words, in the context of EA_T, it is true that there cannot be a Turing machine such that the idealized human mind knows that it coincides with that machine.

## P-A1 — Alexander (2014), arXiv:1305.6080v2, §1

> It is well known that a suitably idealized mechanical "knowing agent" capable of logic, arithmetic, and self-reflection, cannot know the index of a Turing machine that represents its own knowledge. […] However, the proofs always involve (in various guises) the machine knowing its own factivity: that the machine satisfies K(Kφ → φ).

## P-A3 — Alexander (2014), arXiv:1305.6080v2, §2, Definition 3

> The pre-closure axioms of knowledge are given by the following schemata. E1: The universal closure of Kφ whenever φ is valid. E2: The universal closure of K(φ → ψ) → Kφ → Kψ. E3: The universal closure of Kφ → φ. […] E4: The universal closure of Kφ → KKφ. […] The axioms of epistemic arithmetic consist of the pre-closure axioms of knowledge along with Kφ whenever φ is a pre-closure axiom of knowledge or φ is an axiom of Peano arithmetic for L.

## P-A4 — Alexander (2014), arXiv:1305.6080v2, §2, Definition 4; "[10]" is Reinhardt (1985), *Noûs* 19

> By Reinhardt's schema we mean the following schema ([10], p. 327) ∃eK∀x(Kφ ↔ x ∈ W_e), whenever FV(φ) ⊆ {x}. Reinhardt demonstrated that a formalization of "I am a Turing machine and I know which one" cannot be consistent with epistemic arithmetic. To do this, he found a particular instance of Reinhardt's schema that was inconsistent with epistemic arithmetic.

## P-A12 — Alexander (2014), arXiv:1305.6080v2, §3, Theorem 12

> M_Σ(n) satisfies the axioms of epistemic arithmetic mod factivity. […] Additionally, there is a fixed m ∈ N such that M_Σ(n) satisfies the schema K(Kφ ↔ ⌜φ⌝ ∈ W_m), where φ ranges over L-sentences. Thus, the machine that knows the things known by M_Σ(n) is a machine that knows its own code.

## P-R323 — Reinhardt (1985), *Noûs* 19(3), pp. 322–323 (B is Reinhardt's operator "it is provable that", written K elsewhere here)

> The formal language we consider is that of arithmetic, together with the new formation rule: if p is a formula, so is Bp. […] We adopt all the usual schemas of logic and arithmetic (or rather their universal closures), as well as Bp for each such sentence p. The additional special axioms involving B are given by the following schemas (again, more properly their universal closures, optionally prefixed by B): Bp → p; B(p → q) → (Bp → Bq); Bp → BBp; B∀xP → ∀x Bp.

## P-R324 — Reinhardt (1985), *Noûs* 19(3), pp. 324–325, Theorem 1 and remarks from its proof ([p] is the numeral for the Gödel number of p)

> Theorem 1. Suppose T includes Q. Let F be any formula with one free variable x such that one of the following holds for each sentence p: (i) T ⊢ B(F[p] → p) (i.e., F is intuitively correct, considered as describing e.g. a formal system), or (ii) T ⊢ B(F[p] → Bp) (i.e., F describes a "safe" set of sentences, all of which are knowable). Then there is a sentence s such that T ⊢ Bs & B¬F[s] (i.e., s is intuitively provable, but known not to be provable in F). […] Note that this argument uses almost no properties of B: only distributivity over implication and Bp for tautologies p. The fixed point theorem uses in addition only Bp for the most elementary axioms of arithmetic and the logic of equality. […] We now assume (ii). Using the logical principle B(Bp → p), (i) follows and we are done.

## P-R327 — Reinhardt (1985), *Noûs* 19(3), pp. 327–328, Theorem 5 and its proof (Uex is U(e,x), "x belongs to the e-th set"; pe is p(e))

> Theorem 5. The schema ∃e B∀x(Bp(x) ↔ Uex) is inconsistent. Proof. (Note: the proof does not use the BB axiom.) We show that ∃e∀xB(Bp(x) ↔ Uex) is inconsistent. By the B∀ axiom, this will suffice. Let p(x) be ¬U(x,x). Now by the correctness of B, B(Bp(x) → p(x)), whereas by the assumed schema, B(Bp(x) ↔ Uex). Thus, taking x to be e, B(Bpe → pe), B(Bpe ↔ ¬pe), from which, via tautologies and distributivity of B, we get B(pe & ¬Bpe), and similarly from this, Bpe & B¬Bpe; a final application of the correctness of B yields the contradiction: Bpe & ¬Bpe.

## P-R328 — Reinhardt (1985), *Noûs* 19(3), pp. 328–330, Theorem 6, the definition of Con q, the first step of the proof, and remark (iii)

> There are no derivability conditions on the system; rather the assumption on q is that it is known to be complete for intuitive provability: that is, anything provable in the intuitive sense is provable in the sense of q. […] Theorem 6. Suppose there is a formula q(x) with one free variable x such that for every sentence s of T, (B ≤ q) T ⊢ B(Bs → q[s]) (i.e., q is an intuitive upper bound on what is provable). Then T ⊢ B¬B Con q (i.e., the consistency of q is absolutely unprovable). Here by Con q we mean specifically ∀x¬(q(x) & q(ng(x))), where ng is a primitive recursive term of arithmetic representing negation. Proof. Choose s by the fixed point theorem so that T ⊢ B(s ↔ Bq(ng[s])). […] We have used very strongly the property B → BB. However, examination of the proof shows that the correctness of B need not be used, but only B(Bp → p).

## P-R321 — Reinhardt (1985), *Noûs* 19(3), pp. 320–321 ("p / Bp" is a rule written as a fraction in the original)

> Thus we suppose that what is humanly provable is closed under modus ponens, contains all tautologies (however complex), and the usual logical axiom schemas as well. […] Finally, there is the obvious rule p / Bp; to say that intuitive provability may use this rule is just to say that Bp → BBp is true.

## P-R323b — Reinhardt (1985), *Noûs* 19(3), p. 323, after the axioms for B

> (We mention explicitly that universal generalization ∀xp → p(x/t) and Leibniz' law x = y → (p(u/x) → p(u/y)) are both allowed. We need not regard the former as a logical law here, but because of our restriction on terms t these have no undesirable or unintuitive consequences.) If T is a set of sentences, then T ⊢ p means p is deducible by means of modus ponens using logical axioms and sentences of T.

## P-R326 — Reinhardt (1985), *Noûs* 19(3), pp. 325–327, Theorem 3, parts of its proof, and Remark 4

> These results, however, do not really depend on the Gödel fixed point construction, but are more basic, as the next theorem shows. Theorem 3. Let U(e,x) be any formula with two free variables e,x. Suppose in addition that (for each formula p with one free variable x) T has the following thesis (in case U is an r.e. formula of arithmetic which is universal for r.e. sets, this is just the Post-Turing thesis): a) T ⊢ ∃e∀x(Bp(x) ↔ U(e,x)). Then there is a formula q(e) with one free variable e such that b) T ⊢ ∃e(q(e) & ¬Bq(e)). […] Moreover, if a) holds with B prefixed, then so does b) (that is, knowledge of the Turing thesis entails knowledge that there exists an absolutely undecidable sentence). Proof. Note that reading U(e,x) as x ∈ e, a) is very similar to the paradoxical class construction scheme. Taking q(x) = ¬U(x,x) for p in a) yields […] Note that the correctness of B together with b) implies c) T ⊢ ∃e(¬Bq(e) & ¬B¬q(e)), which is the natural reading for "q(e) is absolutely undecidable". […] In this argument we of course make essential use of quantification into the modal context Bq(x), but as pointed out already, the only axiom for B used is the correctness of B […] Remark 4. The hypothesis of the above theorem (in the Post-Turing form), ∃e∀x(Bq(x) ↔ U(e,x)), is known to be consistent with our axioms (see Reinhardt (1981)). The consistency of the stronger claim (i.e. with B prefixed) is an open problem.

## P-K2-460 — Koellner (2018), Part II, *J. Phil.* 115(9), pp. 460–461, §I (F_e+ is the system obtained by adding the sentence 'K = F_e' to F_e; G(·) is the Gödel sentence)

> The argument involves several principles governing F_e, K, and T, three of which it will be useful to state at the outset: (K → T) K ⊆ T; (T-In) φ → T(φ); (K-Intro) the rule: from φ infer K(φ). Here is the argument, step by step: Let e be an arbitrary natural number and consider F_e. (1) K = F_e → F_e ⊆ T. [This follows by the rule 'K → T'.] (2) K = F_e → F_e+ ⊆ T. […] This line follows from (1) by the rule 'T-In'.] (3) K = F_e → G(F_e+). […] This line follows from (2) by reflection and the nature of the Gödel sentence.] (4) K = F_e → F_e+ ⊬ G(F_e+). [This line follows from (2) by the incompleteness theorem.] (5) K(K = F_e → G(F_e+)). [This line follows from (3) by the rule 'K-Intro'.] (6) K = F_e → F_e ⊬ (K = F_e → G(F_e+)). [This line follows from (4).] (7) K = F_e → K ≠ F_e. [This line follows from (5) and (6) since under the assumption that K = F_e lines (5) and (6) show that K and F_e disagree on 'K = F_e → G(F_e+)'.] (8) K ≠ F_e. [This line follows from (7) by logic.]

## P-K2-463 — Koellner (2018), Part II, pp. 462–463, §II.2 (D(x) is defined as T(x) ∨ T(¬x); dots under connectives omitted)

> The system DT is an extension of PA. […] Suffice it to say that the axioms governing 'D' include […] (D4) (∀x)(∀y)[Sent(x) ∧ Sent(y) → (D(x → y) ↔ D(x) ∧ (T(x) → D(y)))] […] Theorem 1 (Feferman). For all φ ∈ L_DT, DT ⊢ D(φ) → (T(φ) ↔ φ). It follows that in DT certain statements—like the liar sentence, λ—are indeterminate, and provably so.

## P-K2-464 — Koellner (2018), Part II, pp. 464–465, §II.4 (the two rules are written as fractions in the original)

> Let EA_DT be the resulting system. Unfortunately: Theorem 2. EA_DT is inconsistent. In hindsight, this is perhaps not so surprising. For the axioms of EA are completely unrestricted, but once we enter the realm of indeterminate sentences we should condition our principles of absolute provability on determinateness, just as we did in the case of the principles governing truth. […] The resulting system, DTK, has, in addition to the axioms of DT, the following axioms governing 'K': (K1) (∀x)[Sent(x) → (K(x) → T(x))]; (K2) (∀x)(∀y)[Sent(x) ∧ Sent(y) → (K(x → y) ∧ K(x) → K(y))]; (K3) (∀x)[Sent(x) → (K(x) → K(K(x)))]; along with the inference rules (DK-Intro) from φ ∧ D(φ) infer K(φ), and (DT-Intro) from φ ∧ D(φ) infer T(φ). Notice that here the inference rules are explicitly conditioned on determinateness and the three fundamental principles are implicitly conditioned on determinateness through the connection between K and T given in K1. […] Theorem 4. For all φ ∈ L_DTK, DTK ⊢ D(φ) → (T(φ) ↔ φ).

## P-K2-467 — Koellner (2018), Part II, p. 467, §IV.1

> Recall that the argument employed the principles 'K → T', 'T-In', and 'K-Intro'. In DTK we have 'K → T' (this is just K1) but we do not have 'T-In' and 'K-Intro'. In fact, if one adds 'T-In' and 'K-Intro' then the resulting system can be shown to be inconsistent. This is not surprising, since once one enters the realm of type-free truth and encounters indeterminate sentences like the liar, these rules are only plausible provided one conditions on determinateness. It is for this reason that in DTK we have (of necessity) only the restricted versions of these rules, namely, 'DT-In' and 'DK-Intro'. Now, in Penrose's argument, the rules 'T-In' and 'K-Intro' are applied to the statements 'K = F_e → F_e+ ⊆ T' and 'K(K = F_e → G(F_e+))' (in steps (2) and (5), respectively). This application is legitimate only if these statements are determinate. It turns out that these statements are not determinate; in fact, they are provably indeterminate: Theorem 7. The system DTK proves: (1) ¬D(K = F_e → F_e+ ⊆ T) (2) ¬D(K(K = F_e → G(F_e+))). So the inferences in steps (2) and (5) are not legitimate.

## P-K2-468 — Koellner (2018), Part II, pp. 467–468, §IV.2 (the subscript PA marks the version with quantifiers restricted to the language of PA)

> To describe the limitative results we need to distinguish two versions of the disjunction and its disjuncts—the full versions and the restricted versions. […] In fact, in the fully general case, the disjunction and each of its disjuncts is indeterminate, and provably so: Theorem 8. DTK ⊢ ¬D(GD) ∧ ¬D(¬WMT) ∧ ¬D(AU). […] In this case it turns out that the statements in question are provably determinate: Theorem 9. DTK ⊢ D(GD_PA) ∧ D(¬WMT_PA) ∧ D(AU_PA). […] Theorem 11. Assume that DTK is correct for arithmetical statements. Then DTK can neither prove nor refute either ¬WMT_PA or AU_PA.

## P-K16-168 — Koellner (2016), "Gödel's Disjunction", in Horsten and Welch (eds.), §7.12, pp. 167–169 (E1 is "K of every first-order validity"; I is "Kφ → T(φ)" for each sentence φ)

> Theorem 7.12.1 EA_DT is inconsistent. […] (There is an even quicker way to see the inconsistency in EA_DT as follows. Let λ be the liar sentence, λ ∨ ¬λ is valid. So by E1 we have K(λ ∨ ¬λ) and by I we have T(λ ∨ ¬λ). But T(λ ∨ ¬λ) is equivalent to T(λ) ∨ T(¬λ) which, by the definition of 'D', is equivalent to D(λ). Hence we have D(λ), which is a contradiction.)

## P-K16-170 — Koellner (2016), "Gödel's Disjunction", §§7.13–7.14, pp. 169–171 (dots over and under symbols omitted)

> (D7) (∀x)[D(K(x)) ↔ D(x)]. […] Lemma 7.14.4 For each φ ∈ L_DTK, DTK ⊢ D(φ) → (T(φ) ↔ φ), and hence DTK ⊢ T(φ) → φ. (T Out)

## P-K16-175 — Koellner (2016), "Gödel's Disjunction", §7.15, pp. 174–175

> The full versions WMT, SMT, and [SSMT] are not determinate (on either reading) since, for example, in the case of the first reading, the component Sent(λ) → (K(λ) → W_e(λ)) is not determinate. […] Theorem 7.15.1 In DTK the statements WMT_PA, SMT_PA, and SSMT_PA are provably determinate, while the statements WMT, SMT, and SSMT are provably indeterminate.

*P-K16-168 to P-K16-175 were transcribed on 2026-11-23 by Claude Fable 5.2 from the pages as displayed in Kindle for
Web, in a copy of the book bought by Eugene. Page numbers are those the reader shows. They could not be checked
mechanically. The bracketed "[SSMT]" corrects what looks like a misprint ("DTK") on the page.*

*P-R321 to P-R328 were transcribed on 2026-11-23 by Claude Fable 5.2 from the page images of the JSTOR scan supplied
by Eugene. The scan's text layer garbles the logical symbols, so only the words could be checked mechanically.*

*P-P73 to P-P76 were transcribed on 2026-11-23 by Claude Fable 5.2 from photographs of the printed book supplied by
Eugene (see `MANIFEST.md` and Amendment 1). They could not be checked mechanically against a text file.*
