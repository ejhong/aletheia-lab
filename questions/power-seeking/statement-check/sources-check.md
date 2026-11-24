# Sources and prose check: power-seeking (#67)

Checker: Claude Opus 5.5 (Anthropic), 24 Nov 2026. Resumed an interrupted check; reused the sources already downloaded and fetched only what was missing.

Sources read (all in `spot4-power/sources/` and `spot4-power/sources2/`, text in `spot4-power/text/`):
- Turner et al., arXiv:1912.01683v10 (28 Jan 2023). The SHA-256 matches MANIFEST. Also the NeurIPS 2021 proceedings paper and supplement, which are scanned images; I OCR'd them with tesseract (`spot4-power/ocr2/`).
- Turner & Tadepalli, arXiv:2206.13477v2. SHA-256 matches MANIFEST.
- Soares et al. 2015, MIRI PDF. SHA-256 matches MANIFEST.
- Thornley, *Philosophical Studies* 182 (2025):1653–1680, published online 19 June 2024 (ORA PDF of the published version), and the author's preprint ("Forthcoming in Philosophical Studies").
- Fetched new: Gustafsson 2022 (open access, CC-BY 4.0, from Cambridge Core); Shah 2018; Thornley 2023, "There are no coherence theorems"; Petersen 2023; Thornley et al. 2024, arXiv:2407.00805; von Neumann & Morgenstern, archive.org scan of the 3rd-edition printing, which contains the 2nd-edition preface and §3.6.

## (a) What holds

1. **Locators for Turner et al. (2021) mostly exist, and the numbering is the same in arXiv v10 and the proceedings.**
   - Defs. 5.2 and 6.1–6.5, Prop. 6.6, Thm. 6.13, Lemma E.24 and Lemma E.51 all exist with these numbers in v10 and in the NeurIPS 2021 paper and supplement (I checked by OCR).
   - Lemma E.24 (v10 p. 31, "Expectation superiority lemma") is the real finite-vector core of S2c: "Let A,B ⊊ R^|S| be finite … If B contains a copy B′ of ND(A) via φ, then E_{r∼D_bound}[g(max_{a∈A} aᵀr)] ≤most E[g(max_{b∈B} bᵀr)]".
   - S2c part (1) is a special case of it: g = identity, D finitely supported, and the copy is of all of A rather than ND(A).
2. **The paper's "≥most" relation is orbit-wise counting over every distribution, as S2c states it.**
   - Def. 6.5 (v10 p. 7): "for all D ∈ 𝒟 … |{D′∈S_|S|·D | f1(D′)>f2(D′)}| ≥ |{D′∈S_|S|·D | f1(D′)<f2(D′)}|".
   - The Lean `OrbitAtLeast`/`distOrbit` encode this faithfully.
3. **Turner & Tadepalli (2022): every locator exists (v2 pp. 4–5) and S2a/S2b say what the paper says.**
   - Def. 3.1 orbit (with Orbit|Θ), Def. 3.2 ≥ⁿmost, Def. 3.3 simply retargetable, Prop. 3.4, Def. 3.5 with items 1–3, Thm. 3.6.
   - S2a/S2b are faithful. The paper itself notes "Turner et al. [2021]'s definition 6.5 is the special case of definition 3.2 where n = 1".
4. **Soares et al. (2015): Thms. 1–2 (pp. 4–5), §1.2, §2.1, §3 and §4.1 all exist.**
   - S3a part 3 restates Soares's own remark (p. 5): choosing c_high as in eq. (10) "ensures that there is the same amount of expected utility available in both cases", and fn. 5: "As the costs of manipulation fall, the actual value of chigh must grow closer to this value."
5. **Shah (2018) is the source of S1d's construction, and S1d is faithful.**
   - Shah: "no matter what the policy is, we can view the agent as an EU maximizer … U(h, a) = 1 if the policy would take action a given history h, else 0."
6. **S3c is a faithful small instance of what Thornley draws from his Second Theorem.**
   - Thornley, published p. 1665: such an agent "can lack a preference between each short trajectory and at most one of the long trajectories".
7. **Scope statements by the authors themselves support the report's limits section.**
   - The site page does say, twice, that no other vendor's model has checked the statements: in the opening callout and under "What this cannot tell you". RESULTS.md says so too.
8. **MANIFEST bibliographic data are right** for Turner et al. (authors, NeurIPS 2021, arXiv id), Turner & Tadepalli (NeurIPS 2022 poster per the arXiv comment), Soares et al. (AAAI-15 workshops, Austin, 25–26 Jan 2015), the Thornley DOI and its CC-BY 4.0 licence, and the Gustafsson DOI.

## (b) What does not hold or is overstated

### B1. S1c is attributed to a source that argues the opposite

S1c is titled "Incomplete Preferences Cannot Be Money-Pumped; Gustafsson 2022 / Thornley 2023". The protocol's locator is "Gustafsson (2022) … Ch. 2 — … incomplete-preference non-exploitability (S1c)".

- Ch. 2 of Gustafsson is "Acyclicity" (pp. 3–23). Completeness is Ch. 3 (pp. 24–38), and it builds a money pump **for** Completeness. Gustafsson concludes (p. 37): "So we have a money-pump argument that Completeness is a requirement of rationality". He also says (p. 3, n. 8): "The money-pump argument for Completeness does not rely on the other basic axioms."
- "Thornley (2023)" is in neither the protocol nor MANIFEST. The likeliest piece is "There are no coherence theorems" (AI Alignment Forum / LessWrong, 20 Feb 2023, written by EJT, posted by Dan H; Thornley et al. 2024 cite it as Thornley 2023). It does argue that incomplete agents can avoid money pumps, but only through a *dynamic choice policy*: "if I previously turned down some option X, I will not choose any option that I strictly disprefer to X".
- The point is disputed:
  - Gustafsson (2022, Ch. 3) argues for Completeness.
  - Thornley (2023) and Petersen ("Invulnerable Incomplete Preferences: A Formal Statement", AF, 30 Aug 2023: "Having shown that incompleteness does not imply that agents will pursue dominated strategies") argue against.
  - Petersen names John Wentworth and David Lorell as arguing that preferential gaps "make agents play strictly dominated strategies". I have not read their post.
- RESULTS ("dropping Completeness stops money pumps dead"; "Money-pump avoidance does not force Completeness") and the page ("Avoiding exploitation pushes toward transitivity, not completeness") state one side of this dispute as settled fact.

### B2. The formal S1c does not test the money pump that is in dispute

- In the Chang/Gustafsson "Single-Souring Money Pump" (Gustafsson p. 26; Thornley 2023), the agent trades **across preferential gaps**: A ∥ B and B ∥ A⁻, with A ≻ A⁻.
- S1c's `TradeChain le` lets a trade happen only when it is weakly preferred, so trades between incomparable options are excluded by definition. The blind reader is right.
- The Part 1 witness is `le s t := s.1 = t.1 ∧ s.2 ≤ t.2`. This agent never trades one good for another, so "no money pump" holds trivially.
- Part 2's "no strict cycle" follows from transitivity alone.
- Gustafsson himself makes this point (p. 25): "if we … take some preferences that satisfy Expected Utility Theory and replace all indifference relations with preferential gaps, the resulting preferences would be no more exploitable than the original preferences."
- So S1c shows nothing specific to incompleteness.

### B3. S1b formalises the version Gustafsson says foresight blocks

- Gustafsson p. 3: "While foresight blocks the standard version of the money-pump argument, there are other versions that work for agents who use foresight (Section 2.1)."
- S1b is a static trade chain whose hypothesis already grants that every paid trade is accepted. It is the naive version, not Gustafsson's argument.

### B4. S2c: "proves the exact core of NeurIPS 2021 Prop. 6.6 / Thm. 6.13" is overstated, and wrong for Thm. 6.13

- **Thm. 6.13** (v10 p. 9) is about *average-optimality probability* of sets of recurrent state distributions: "P_Dany(D, average) ≥most P_Dany(D′, average)". It needs a pairwise-orthogonality hypothesis. It is not about POWER, and S2c does not touch it.
- **Prop. 6.6** (p. 7) concerns POWER, defined in Def. 5.2 as E[max_{f∈F(s)} ((1−γ)/γ)(f(γ) − e_s)ᵀr], for bounded-support D, for all γ ∈ [0,1], with a copy of F_nd(s′).
  - Lean's `powerVal` has no normalisation, no −e_s term, no γ and no MDP.
  - The bridge "exact for stationary deterministic policies in any finite MDP" is plausible at a fixed γ ∈ (0,1) after a translation the study never writes down or proves.
- **The closest exact match is Prop. 6.12 (γ = 1).** Lemma E.51 (p. 42) gives POWER(s,1) = E[max_{d∈RSD(s)} dᵀr], which is exactly `powerVal` with F = RSD(s). The proof of Prop. 6.12 applies Lemma E.24.
- Accurate wording: "a special case of Lemma E.24 (g = identity, finitely supported D), which with F = RSD(s) is Prop. 6.12 at γ = 1 for finitely supported D."
- Wrong locators in the Statement.lean docstrings:
  - `NonDominated` cites "Def. 6.10 / §3". Def. 6.10 is *Recurrent state distributions*; non-domination is **Def. 3.6**.
  - `powerVal` cites "Def. 5.2 / Lemma E.51". E.51 is the γ = 1 identity. That is fine if the γ = 1 reading is meant, but it is not Def. 5.2.

### B5. RESULTS Limit 2 misstates scope

"Continuous reward distributions with Lebesgue densities (as in Turner et al. 2021 Appendix E) … are captured through their finite option sets". They are not.

- `RewardDist` is a `Finsupp`, a finitely supported distribution.
- Finite option sets do not capture continuous reward distributions.
- Turner's strictness results are stated for continuous bounded IID distributions (Lemma E.24, "strict for all D_X-IID ∈ D_C/B/IID"), and these are not covered.
- The site page gets this right ("continuous Lebesgue densities … were not formalized"). RESULTS contradicts it.

### B6. S2d, S2e and S2f are framed as "dropping premises", but these are not premises of the theorem, and the authors say so themselves

- **S2d** ("drop reward symmetry / uniform orbit weighting"):
  - Prop. 6.6 never assumes a symmetric D. It is a statement about every orbit, and S2d's point-mass D is consistent with it: in the orbit {e0, e1, e2}, F₂ wins 2 to 1.
  - Turner et al. make S2d's point themselves (p. 5): "POWER is sensitive to choice of distribution … D∅ even gives maximal POWER_D∅ to ∅!" and (p. 4) "'what do optimal policies "tend" to look like?' seems to depend on one's prior beliefs."
  - On the counting measure, fn. 4 (p. 7; proceedings p. 6): "we have endowed each orbit with the counting measure. However, a priori, we might expect that some orbit elements are more empirically likely to be specified than other orbit elements."
  - §7 (p. 11): "we have prior information: AI designers usually try to specify a good reward function."
  - "Uniform orbit weighting" is part of what ≥most *means*. It is not a hypothesis a counterexample can drop.
  - S2d also contains no policy, so "optimal policies strictly choose shutdown" says more than the statement does.
- **S2e** ("drop optimality / retargetability"):
  - `choose` is the constant function `fun _ => false`. There is no MDP and no policy.
  - Turner & Tadepalli list this exact case as outside their scope (§6.2, p. 10): "Our results do not prove that we will build unaligned AI agents which seek power … 2. The AI's decision-making is not retargetable (definition 3.5)."
  - Turner & Tadepalli also show optimality is *not* required ("Section A shows that optimality is not required", p. 9). Pairing "optimality / retargetability" as a single premise misdescribes their result. The page's result line ("requires both optimality/retargetability and uniform reward-orbit symmetry") has the same problem.
- **S2f**: dominated options adding nothing is built into the source. Def. 3.6 and Lemma E.11 say "Maximal value is invariant to restriction to non-dominated functionals", and the strict clause of Prop. 6.6 requires F_nd(s) \ φ·F_nd(s′) to be non-empty.
- None of the three counterexamples has a source locator, and none is a counterexample to anything the papers claim.
- "On a 3-state MDP" (RESULTS and the page) is wrong: the Lean has three basis vectors, not an MDP.

### B7. Thornley (2024) locators are wrong or mixed between versions, and S3d is mis-attributed

Section numbering in the two versions:
- Published version: §6 is "The setting for the first theorem" (Leave/Prevent/Cause), §7 the First Theorem, §8 the Second Theorem, §9 the Third Theorem, §10 the Conclusion.
- Author's preprint (sections numbered from 0): §6 First, §7 Second, §8 Third, §9 Conclusion.

How the study's citations fit:
- "§6, Thm 1" and "§7, Thm 2" fit the preprint, while the study cites the published DOI.
- The D12 docstring's "§6" for the three actions fits the published version.
- **"§9" for the incomplete-preference escape (S3d) is wrong in both versions.** It is the Third Theorem in one and the Conclusion in the other.
- The published Conclusion (p. 1673) says the opposite of an escape: "my cursory examination in this paper reveals zero conditions for which both answers are a clear 'yes.'"
- The paper mentions incompleteness only as future work (§8, p. 1665): "In work-in-progress (Thornley, 2024), I'm exploring the possibility of keeping agents shutdownable by training them to violate Completeness."

Where S3d actually comes from:
- S3d's relation is Thornley's later POST condition. Thornley, Roman, Ziakas, Ho & Thomson, "Towards Shutdownable Agents via Stochastic Choice", arXiv:2407.00805 (v1, 30 Jun 2024): "(2) The agent lacks a preference between every pair of different-length trajectories".
- That paper's references also list Thornley 2024b, "The Shutdown Problem: Incomplete Preferences as a Solution", AI Alignment Forum.
- That paper says such preferences "will plausibly keep the agent shutdownable". A static order existing (S3d) does not show this; it needs a dynamic choice rule (Petersen 2023).
- "Connecting directly back to S1c" adds nothing: S1c has no trajectory lengths, and it fails for the reason in B2.

Thornley's verdict is the opposite of the study's tone. His theorems "suggest that agents satisfying some innocuous-seeming conditions will often try to prevent or cause the pressing of the shutdown button" (abstract).

### B8. S3a and S3b are toy EU analogues, and S3b omits the source's own negative verdict

**S3a.**
- Thornley's First Theorem is about preferences, not expected utility: Option Set Independence, Backward Induction, Indifference to Attempted Button Manipulation, Indifference between Indifference-Shifted Lotteries, Transitivity, Better Chances.
- Its setting excludes costs: "These actions have no effect on the probabilities of each future trajectory conditional on reaching each state" (p. 1659). Costs enter only in the Third Theorem.
- S3a at c = 0, with f = 0 and h = 1, is an EU special case of First Theorem clauses 1–2. The cost term is borrowed from Soares's χ.
- Soares's thresholds are on c_high (the shutdown utility). S3a's are on c.
- Classification: an analogue.

**S3b** ("EU maximisation by itself does not force shutdown resistance", citing Soares §3).
- No cited author claims it does. Soares p. 3: "for almost any utility function U a U-agent has incentives to prevent its own shutdown". Thornley's claim is that useful agents will "often" do so.
- Soares §3 builds utility indifference, and §4 then shows it fails:
  - §4.1: "there is no UN-cost … that the agent is willing to pay in order to make the heavy machinery respond to a shutdown command".
  - §4.2: "This gives U-agents a perverse incentive to 'manage the news' by ensuring that unfortunate observations cause the shutdown button to be pressed … this violates Desideratum 3", and, symmetrically, Desideratum 2.
  - §5: "a corrigible solution to the shutdown problem does not yet exist".
- RESULTS mentions §4.1 only as "not formalized". It never mentions §4.2. The site page presents S3b as a positive escape.
- The one-shot payoff table cannot express either failure.
- Thornley too (p. 1665) notes indifference agents "would violate Option Set Independence" and that "Soares et al. (2015, sec. 4) note various respects in which these agents fail to be shutdownable."

**Family-3 headline.** "Shutdown resistance is a tension between Completeness, Transitivity and Usefulness — not an inevitable consequence of EU maximization" muddles the logic.
- EU maximisers are complete and transitive by the vNM theorem, so S3c applies to them.
- Thornley's First Theorem needs no Completeness at all.

### B9. von Neumann & Morgenstern locator

- "(1944), §3.6 & Appendix": §3.6, "The axioms and their interpretation", exists (p. 26).
- The Appendix did not exist in 1944. Preface to the second edition: "We have added an Appendix containing an axiomatic derivation of numerical utility … A publication of this proof in a periodical was promised in the first edition".
- §3.6.1 axiomatises an abstract mixture system with (3:A) complete ordering, (3:B:a–d) ordering and combining, and (3:C) algebra of combining. S1a's form is the later textbook form on finite lotteries (Completeness, Transitivity, mixture Independence as a biconditional, Archimedean continuity). That is the same theorem in substance, but not vNM's own axiom list.
- Cite as "vNM (1947, 2nd ed.), §3.6 and Appendix", or name a modern statement.

### B10. Other bibliographic errors

- **Shah (2018)** has the wrong title. The real title is "Coherence arguments do not **entail** goal-directed behavior" (Rohin Shah, LessWrong/AF, 3 Dec 2018). Shah credits the construction to an earlier paper (arXiv:1811.07871, p. 6).
- **Gustafsson (2022)** is open access under CC-BY 4.0, but MANIFEST archived only Crossref metadata. Its locators were never checked against the text.
- **Thornley year/volume.** "Thornley (2024) … Philosophical Studies 182" should read 182 (2025): 1653–1680, published online 19 June 2024.
- **The MANIFEST's `thornley2024.html`** came from link.springer.com. My fetch of that URL returned a 3 KB bot-challenge page. The study's hashed file is not in the worktree, so I cannot tell whether it held the article. The section numbers the study uses match the author preprint, which suggests the locators were not taken from the hashed file.

### B11. Overstated sentences

**RESULTS.md**
- "share the exact same logical shape: each headline theorem is genuinely true … and each breaks cleanly when one of the load-bearing premises is dropped". S1c, S2d, S2e and S2f do not drop a premise of any cited theorem.
- "The von Neumann–Morgenstern representation theorem (S1a) is completely true". The theorem is fine; the vNM locator is not (B9).
- "dropping **Completeness** stops money pumps dead (S1c …)". Wrong on the formal content (B2) and one-sided on the literature (B1).
- "merely 'acting as if maximizing some utility function' places **zero** behavioral constraint" (S1d). True of deterministic policies over histories; that is Shah's own point and should be credited as such.
- "Both … retargetability theorems … and … POWER theorem are completely valid: whenever option set F₂ contains a copy of F₁ via an involution φ". Turner & Tadepalli's theorems are not about option-set copies.
- "But drop reward symmetry / uniform orbit weighting (S2d) and an optimal policy strictly chooses shutdown". No policy, and not a premise (B6).
- "Proves the exact core of NeurIPS 2021 Prop. 6.6 / Thm. 6.13" (B4).
- S3b's row: "Expected-utility maximization by itself does **not** force shutdown resistance" (B8).
- S3d's row: "Thornley (2024), §9" and "(connecting directly back to S1c!)" (B7).
- Limit 2 on continuous distributions (B5).
- "What this means": "Completeness … (which money pumps do not force)", and "Uniform symmetry across reward permutations" listed as a premise.

**Site page**
- Result line: "money pumps do not force completeness, power-seeking requires both optimality/retargetability and uniform reward-orbit symmetry, and shutdown resistance requires complete, transitive preferences across trajectory lengths rather than EU maximization alone".
- "Avoiding exploitation pushes toward *transitivity*, not *completeness*."
- "On a 3-state MDP … optimal policies strictly choose shutdown."
- "a non-optimal stationary policy still chooses shutdown 100% of the time".
- "linking Thornley's shutdown escape hatch directly back to … (S1c)".
- "The von Neumann–Morgenstern representation theorem (S1a) is rock solid" is fine.

**The headline answer** ("No — … substantially less than 'any capable AI must seek power and resist shutdown'") answers a claim that none of the cited papers makes, and several explicitly disclaim it:
- Turner et al. 2021, p. 2 (also proceedings p. 2): "We make no claims about when large-scale AI power-seeking behavior could become plausible."
- Turner et al. 2021, v10 p. 11, proceedings p. 10: "We caution that many real-world tasks are partially observable and that learned policies are rarely optimal. Our results do not mathematically prove that hypothetical superintelligent AI agents will seek power."
- Turner et al. 2021, v10 §7 p. 10: "Emphatically, optimal policies are often qualitatively divorced from the actual policies learned by reinforcement learning."
- Turner & Tadepalli 2022, p. 10: "Our results do not prove that we will build unaligned AI agents which seek power over the world."
- Soares et al. 2015, p. 3: "for almost any utility function U" — not every one.
- Thornley 2024: "will often try".

For balance, the authors do make hedged strong suggestions, and the report should quote these too:
- Turner et al. §7: "Average-optimal agents would generally stop us from deactivating them, if physically possible."
- Turner & Tadepalli §6.3: "Our theory suggests that when RL training processes become sufficiently advanced, the trained agents will tend to seek power over the world."

The fair headline is that the formal results match the authors' own stated scope. The slogan belongs to secondary discussion, which the study never cites. Thornley 2023's appendix lists such sources for the coherence argument.

### B12. Process, compared with #19 and #66

- The earlier proof-lane studies (`godel-argument`, `unfolding-argument`) ran their statement check *before* locking, with source passages in `statement-check/passages.md` and a quote checker (`check_quotes.py`).
- This study locked with no passages and no check. A passage file would have caught B1 and B7 before the lock.
- Fixing them now has to go through amendments or prose corrections, because the statements are locked.

## (c) The 14 statements

| ID | Attributed source / locator | Does the locator exist and say this? | Lean statement vs source |
|---|---|---|---|
| S1a | vNM (1944) §3.6 & Appendix | §3.6 yes (axioms 3:A–3:C, p. 26). Appendix only from the 2nd ed. (1947) | Same theorem, modern axiomatisation (finite lotteries, mixture independence) |
| S1b | Gustafsson (2022) Ch. 2 | Ch. 2 "Acyclicity", pp. 3–23, yes | Simplified analogue: static chain, hypothesis grants the trades; the no-foresight version Gustafsson says is blocked (p. 3) |
| S1c | Gustafsson (2022); Thornley (2023) | Gustafsson: no. Ch. 3 argues *for* Completeness via a money pump (p. 37). Thornley 2023 unidentified; most likely "There are no coherence theorems" (AF, 20 Feb 2023), which argues the point via a dynamic policy | Own construction. Excludes trades across preferential gaps, so it does not test the disputed money pump. Holds for complete transitive relations too |
| S1d | Shah (2018) | Exists, but the title is "…do not **entail**…" | Same construction (deterministic policies) |
| S2a | T&T (2022) Defs. 3.1–3.3, Prop. 3.4 | Yes (v2 p. 4) | Same (finite Θ) |
| S2b | T&T (2022) Def. 3.5, Thm. 3.6 | Yes (v2 pp. 4–5) | Same |
| S2c | Turner et al. (2021) Defs. 5.2, 6.1–6.5, Prop. 6.6, Lemma E.24, Thm. 6.13 | All exist with these numbers in v10 and in the proceedings. Thm. 6.13 is about average-optimality probability, not POWER. The docstring's "Def. 6.10" (cited for non-domination) is RSDs; non-domination is Def. 3.6 | Special case of Lemma E.24 (g = identity, finitely supported D). Equals Prop. 6.12 at γ = 1 via Lemma E.51 when F = RSD(s). Prop. 6.6 for γ < 1 only after an unproved translation. Not Thm. 6.13 |
| S2d | "Boundary counterexample" (no source) | none | Own construction. Consistent with Prop. 6.6. Turner et al. make the same point (p. 5, fn. 4) |
| S2e | "Boundary counterexample" (no source) | none | Own construction (constant function, no MDP). Excluded by T&T §6.2 item 2 |
| S2f | "Boundary counterexample" (no source) | none | Own construction. Built into Turner Def. 3.6 / Lemma E.11 |
| S3a | Soares Thms. 1–2; Thornley §6 Thm. 1 | Soares yes (pp. 4–5). Thornley's First Theorem is §7 in the published version, §6 in the preprint | Analogue: EU payoff table with cost. Parts 1–2 at c = 0 are the EU special case of Thornley Thm. 1 (f = 0, h = 1). Part 3 = Soares eq. (10) / fn. 5 |
| S3b | Soares §3 | Yes (pp. 5–7) | Analogue of Thm. 4's no-manipulation conclusion in a one-shot toy. Omits §4.1–4.2, where the source says indifference fails |
| S3c | Thornley §7 Thm. 2 | Second Theorem is §8 in the published version (§7 in the preprint) | Special case (2×2) of the corollary drawn on p. 1665 |
| S3d | Thornley (2024) §9 | No. §9 is the Third Theorem (published) or the Conclusion (preprint); the Conclusion finds no clear escape | Faithful static toy of POST (Thornley et al. 2024, arXiv:2407.00805; Thornley 2024b), but mis-attributed. Does not show shutdownability |

## (d) What I could not check

- The study's own hashed `thornley2024.html` is not in the worktree (no `data/`). Springer served me a bot challenge.
- The vNM 1944 first edition itself. I read the archive.org scan of the 3rd-edition printing (1953), which includes the 2nd-edition preface.
- Turner & Tadepalli v1 and the NeurIPS 2022 proceedings numbering. I checked v2 only, which is the version MANIFEST hashed.
- Gustafsson Ch. 2 in detail beyond its opening.
- Thornley 2024b (the AF post) and Wentworth & Lorell, both of which I know only through citations.
- OCR of the proceedings is imperfect, but the numbering lines were legible.
- I did not re-check the Lean proofs beyond reading the witnesses for S1c, S2d and S2e.

## (e) Corrections I would make

1. **S1c.** Remove "Gustafsson 2022" as support. Say Gustafsson (2022, Ch. 3, pp. 24–38) gives a money-pump argument *for* Completeness. Identify Thornley (2023) as "There are no coherence theorems" (AF) and Petersen (2023) as the replies.
   - State plainly that S1c's chains exclude trades across preferential gaps, so it holds equally for complete relations and does not bear on the dispute.
   - Replace "stops money pumps dead" and "money-pump avoidance does not force Completeness" with: "whether money pumps force Completeness is disputed; our S1c does not settle it."
2. **S2c.** Replace "exact core of Prop. 6.6 / Thm. 6.13" with "a special case of Lemma E.24 (finitely supported D, identity g); with F = RSD(s) this is Prop. 6.12 at γ = 1 via Lemma E.51. Not Thm. 6.13."
   - Fix the docstring locators: non-domination is Def. 3.6.
   - Delete the Limit-2 claim about continuous distributions.
3. **S2d/S2e/S2f.** Reframe them as illustrations of caveats the authors state themselves (Turner p. 5, fn. 4 and §7; T&T §6.2), not as dropped premises. Drop "MDP" and "policy" wording. Stop pairing "optimality / retargetability" (T&T show optimality is not needed).
   - Fix the page's result line to match.
4. **Thornley locators.** Use published numbering: First Theorem §7, Second §8, Third §9. Re-attribute S3d to Thornley 2024b and Thornley et al. 2024 (arXiv:2407.00805, POST).
   - Quote the Conclusion's "zero conditions for which both answers are a clear 'yes'".
   - Correct to *Philosophical Studies* 182 (2025): 1653–1680.
5. **S3b.** Add that Soares et al. themselves show utility indifference fails (§4.1 subagents; §4.2 "manage the news" incentives that violate Desiderata 2 and 3) and conclude no solution exists.
   - Change "EU maximization by itself does not force shutdown resistance" to "a one-shot EU agent that is exactly indifferent has no incentive in this toy; the source shows this does not survive richer settings."
   - Fix the Family-3 headline: EU agents are complete and transitive, so S3c applies to them.
6. **vNM.** Cite the 2nd ed. (1947) for the Appendix, and say S1a uses the modern four-axiom form.
7. **Shah.** Correct the title to "…do not entail goal-directed behavior" (3 Dec 2018) and credit S1d's construction to him.
8. **Headline.** Keep the "No", but say that the cited authors themselves disclaim the slogan. Quote Turner et al.'s "Our results do not mathematically prove that hypothetical superintelligent AI agents will seek power" and T&T's "Our results do not prove…", plus the authors' hedged stronger suggestions.
   - Remove "exact same logical shape", "completely valid / completely true", "stops money pumps dead" and "proves the exact core".
9. **MANIFEST.** Archive Gustafsson (it is open access), Shah, Thornley 2023 and the incomplete-preferences sources. Confirm that `thornley2024.html` is the article and not a challenge page.
10. **Process.** Before the planned second-vendor check, write a `passages.md` with one quoted source passage per statement, as in #19 and #66. Fold the passage problems into amendments or prose corrections; the locked statements stay as they are.
