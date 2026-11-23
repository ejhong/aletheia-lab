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

*P-P73 to P-P76 were transcribed on 2026-11-23 by Claude Fable 5.2 from photographs of the printed book supplied by
Eugene (see `MANIFEST.md` and Amendment 1). They could not be checked mechanically against a text file.*
