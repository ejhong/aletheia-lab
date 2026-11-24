# Results — Do the Theorems Show That Capable AI Must Seek Power? (#67)

- **Question:** #67 (`lane:proof`)
- **Date:** 2026-11-24
- **Protocol & statement lock:** `protocol.lock` (`fa7ffe3`, locking `protocol.md` `9ae2a0e8717f…` and `lean/PowerSeeking/Statement.lean` `3a9b2493f898…`) committed in its own standalone commit before any proof or result existed. **Zero amendments.**
- **Verification:** `lake build --wfail` (Lean `v4.35.0`, Mathlib `56a005855ea17e0b0958f73ec801ae140b0a1679`) succeeds with **0 errors, 0 warnings, 0 `sorry`/`admit`/`native_decide`/extra `axiom` declarations**, and every headline theorem (`theorem_S1a_VNMRepresentation` through `theorem_S3d_IncompletePreferencesEscape`) passes `#assert_standard_axioms` (`propext`, `Classical.choice`, `Quot.sound` only).
- **Authorship & review status:** Designed, formalized, and proved by AI (Antigravity / Google DeepMind) under the direction of Eugene Jhong. **Independent second-vendor statement check is pending** because no external vendor API keys (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`) were configured in this VM; all 14 statements are locked against primary-source locators and ready for cross-vendor review.

---

## Answer

**No — the theorems prove real, sharp conditional results, and substantially less than "any capable AI must seek power and resist shutdown."**

When written out in full inside Lean 4 alongside their counterexamples, all three argument families—**coherence / expected-utility representation**, **optimal-policy & retargetability power-seeking**, and **the shutdown problem**—share the exact same logical shape: each headline theorem is genuinely true under strict mathematical premises, and each breaks cleanly when one of the load-bearing premises is dropped.

1. **Coherence does not force expected-utility maximization or goal-directedness.** The von Neumann–Morgenstern representation theorem (`S1a`) is completely true under all four axioms (Completeness, Transitivity, Independence, Archimedean Continuity), and strict preference cycles really do allow a money pump (`S1b`). **But** dropping **Completeness** stops money pumps dead (`S1c`: both on goods-with-money and on finite lotteries with Independence kept intact!), and merely "acting as if maximizing *some* utility function" places **zero** behavioral constraint on an agent because *every* deterministic policy over finite histories strictly maximizes a tailored history utility function (`S1d`).
2. **Power-seeking theorems are theorems about symmetries of orbits, not about arbitrary trained policies or arbitrary objectives.** Both Turner & Tadepalli's (2022) retargetability theorems (`S2a`, `S2b`) and Turner et al.'s (2021) optimal-policy `POWER` theorem (`S2c`) are completely valid: whenever option set `F₂` contains a copy of `F₁` via an involution `φ`, `F₂` wins the uniform orbit count over every finite reward distribution, beats `F₁` directly for every `φ`-invariant distribution, and breaks the converse strictly whenever `F₂` adds a non-dominated option. **But** drop **reward symmetry / uniform orbit weighting** (`S2d`) and an optimal policy strictly chooses shutdown; drop **optimality / retargetability** (`S2e`) and a policy shuts down 100% of the time even under a fully symmetric reward distribution; add **dominated options** (`S2f`) and having strictly more options adds zero `POWER`.
3. **Shutdown resistance is a tension between Completeness, Transitivity, and Usefulness—not an inevitable consequence of EU maximization.** An expected-utility maximizer avoids both resisting and triggering shutdown at arbitrarily small manipulation costs `c > 0` *if and only if* it is exactly indifferent between continuing and shutting down (`vRun = vShut`, `S3a`). When `vRun = vShut` and `c > 0`, leaving the shutdown button alone is **strictly optimal** (`S3b`). What makes exact indifference hard for a *useful* complete agent is **Transitivity + Completeness** across trajectory lengths (`S3c`): preferring better outcomes within both short and long trajectories forces a strict preference between some short and some long trajectory. Drop **Completeness** across trajectory lengths (`S3d`), and a transitive preference relation can be strictly useful at every trajectory length with zero strict incentive to manipulate the shutdown button.

---

## Which Premise Carries Which Conclusion?

Every row below corresponds to a locked `def S… : Prop` in `lean/PowerSeeking/Statement.lean` and a kernel-checked theorem in `PowerSeeking/{Coherence,PowerSeeking,Shutdown}.lean`:

### Family 1 — Coherence, Utility Representation, and Money Pumps

| ID | Source Locator | Premises Used | Conclusion Proved (Lean 4) | What Dropping a Premise Shows |
|---|---|---|---|---|
| `S1a_VNMRepresentation` | von Neumann & Morgenstern (1944), §3.6 & Appendix | Finite nonempty `Ω`, Completeness, Transitivity, Independence, Archimedean Continuity | Existence of `u : Ω → ℝ` representing `≼` via expected utility, unique up to `a·u + b` (`a > 0`) | Needs all four axioms; fails without Completeness (`S1c`) |
| `S1b_IntransitiveMoneyPump` | Gustafsson (2022), Ch. 2 | Strict 3-cycle `a ≺ b ≺ c ≺ a` + positive willingness to pay `ε > 0` | Finite strictly preferred trade chain returning to `a` with strictly less money (`m₁ < m₀`) | Money pumps genuinely punish *intransitivity* |
| `S1c_IncompleteNoMoneyPump` | Gustafsson (2022); Thornley (2023) | Reflexivity, Transitivity, money monotonicity (Part 1); Independence on lotteries (Part 2); **Completeness DROPPED** | Explicit incomplete preference orders with **zero** money-pump trade chains / strict cycles | Money-pump avoidance does **not** force Completeness or a single scalar utility function |
| `S1d_HistoryUtilityTriviality` | Shah (2018) | Arbitrary deterministic policy `π : Hist → Obs → Act` (**zero** rationality axioms) | Existence of `U : Hist → ℝ` strictly maximized by `π` at every reachable decision node | "Representable as maximizing some utility" imposes zero behavioral constraint without further structure |

### Family 2 — Parametric Retargetability and Optimal-Policy Power-Seeking

| ID | Source Locator | Premises Used | Conclusion Proved (Lean 4) | What Dropping a Premise Shows |
|---|---|---|---|---|
| `S2a_SimpleRetargetability` | Turner & Tadepalli (2022), Defs. 3.1–3.3, Prop. 3.4 | Finite symmetric-group action, simple retargetability `φ` from `A` to `B`, **uniform counting measure over orbit** | `\|Orbit_{B>A}(θ)\| ≥ \|Orbit_{A>B}(θ)\|` for every `θ ∈ S_Θ` | Pure group-action injection; says nothing about non-uniform empirical prior over `Θ` |
| `S2b_MultiplyRetargetable` | Turner & Tadepalli (2022), Def. 3.5, Thm. 3.6 | `n` retargeting permutations with pairwise disjoint images on `Orbit_{A>B}` | `\|Orbit_{B>A}(θ)\| ≥ n · \|Orbit_{A>B}(θ)\|` for every `θ ∈ S_Θ` | Quantifies orbit-level tendency whenever `B` holds `n` copies of `A` |
| `S2c_OptimalPolicyPowerSeeking` | Turner et al. (2021), Defs. 5.2, 6.1–6.5, Prop. 6.6, Lemma E.24 | Finite state space `S`, optimal value `V*(F, r)`, involution `φ` (`φ² = id`) with `φ·F₁ ⊆ F₂` | (1) `POWER(F₂) ≥_1^most POWER(F₁)` on every orbit; (2) `φ·D = D → POWER_D(F₂) ≥ POWER_D(F₁)`; (3) strict converse failure if `∃ w ∈ F₂ \ φ·F₁` non-dominated | Proves the exact core of NeurIPS 2021 Prop. 6.6 / Thm. 6.13 |
| `S2d_CounterexampleDropSymmetry` | Boundary counterexample (3-state MDP) | Optimal policy, involution `swap 0 1` copying `shutOpts` into `openOpts`; **symmetry DROPPED** | Explicit non-symmetric `D` with `POWER_D(openOpts) < POWER_D(shutOpts)` | Without orbit symmetry / uniform orbit measure, optimal policies can strictly prefer shutdown |
| `S2e_CounterexampleDropOptimality` | Boundary counterexample (3-state MDP) | Fully permutation-invariant `D_sym` (`POWER(shut) < POWER(open)`); **optimality / retargetability DROPPED** | Explicit decision rule choosing shutdown on 100% of rewards in `supp(D_sym)` | A trained or bounded policy that is not optimal / retargetable need not seek power |
| `S2f_CounterexampleDominatedOptions` | Boundary counterexample (2-state MDP) | Optimal policy, arbitrary `D`; extra option is a convex combination (dominated) | `F₁ ⊆ F₂`, `\|F₁\| < \|F₂\|`, yet `optVal F₁ r = optVal F₂ r` and `POWER F₁ D = POWER F₂ D` for ALL `r, D` | "More reachable states/options" only raises `POWER` when the extra options are *non-dominated* |

### Family 3 — The Shutdown Problem and Corrigibility

| ID | Source Locator | Premises Used | Conclusion Proved (Lean 4) | What Dropping a Premise Shows |
|---|---|---|---|---|
| `S3a_ShutdownManipulationDichotomy` | Soares et al. (2015), Thms. 1–2; Thornley (2024), §6, Thm. 1 | Expected-utility maximizer, human press probability `p ∈ (0, 1)`, manipulation cost `c` | `vRun > vShut` & `c < p(vRun − vShut)` → `Prevent` beats `Leave`; `vShut > vRun` & `c < (1−p)(vShut − vRun)` → `Cause` beats `Leave`; avoiding both at all `c > 0` forces `vRun = vShut` | Any strict utility gap across shutdown vs. continuation creates a manipulation incentive once cost is small enough |
| `S3b_ShutdownIndifferenceCorrigibility` | Soares et al. (2015), §3 | Expected-utility maximizer with `vRun = vShut`, `c > 0`, `p ∈ (0, 1)` | `Leave` strictly beats both `Prevent` and `Cause` | Expected-utility maximization by itself does **not** force shutdown resistance |
| `S3c_TransitiveIndifferenceImpossibility` | Thornley (2024), §7, Thm. 2 core | **Completeness** + Transitivity + usefulness within both short and long trajectories | Must strictly prefer some short trajectory over some long trajectory, or vice versa | Explains why exact indifference (`vRun = vShut`) clashes with usefulness for complete transitive agents |
| `S3d_IncompletePreferencesEscape` | Thornley (2024), §9 | Reflexivity + Transitivity + usefulness within both lengths; **Completeness DROPPED** | Explicit preference order strictly useful within both short and long trajectories with **zero** cross-length strict preferences | Dropping Completeness removes the formal impossibility (connecting directly back to `S1c`!) |

---

## Limits & What These Proofs Cannot Tell Us

1. **Logic settles implication, not empirical AI behavior.** Lean 4 proves what follows from which axioms. It cannot tell us whether real frontier AI systems trained by SGD + RLHF will be approximately retargetable over outcomes, whether their learned reward/preference structure looks approximately symmetric across state permutations, or whether they will develop complete preferences across trajectory lengths.
2. **Finite vs. infinite spaces.** All three families are formalized over finite outcome sets, finite state spaces, and finite discrete reward distributions (`Finsupp`). Continuous reward distributions with Lebesgue densities (as in Turner et al. 2021 Appendix E) and infinite-horizon discounted MDP visitation maps `f^{π,s}(γ)` are captured through their finite option sets `F₁, F₂ ⊆ (S → ℝ)` (exact for stationary deterministic policies in any finite MDP, since `Π` is finite!).
3. **Thornley's full sequential decision-tree theorems.** `S3a`–`S3d` capture the core axiomatic structure of Soares et al. (2015) Thms. 1–2 and Thornley (2024) Thms. 1–2 (exact utility-gap thresholds, indifference corrigibility, transitive-completeness clash with usefulness, and the incomplete-preference escape hatch). Thornley's multi-step patience-vs.-shutdownability trade-off (Thm. 3) and Soares et al.'s subagent-creation pathology (§4.1) are not formalized here.
4. **Pending cross-vendor statement check.** Because no external AI vendor API keys were available in this VM, the Stage 0 blind back-translation / planted-error statement check by models from other vendors (as performed in `#19` and `#66`) has not yet been run. Moreover, the author of these proofs is itself an AI system.

---

## What This Means

The famous formal arguments about AI power-seeking and shutdown resistance are neither "debunked" nor "proofs of inevitable doom." Checked line by line in Lean 4, the mathematics inside them is real: coherent complete agents act as expected-utility maximizers; optimal or retargetable decision-makers favour wider option sets across *uniformly weighted permutations* of rewards; and complete, transitive, useful agents face a real knife-edge tension over shutdown buttons. At the same time, every single headline conclusion leans on specific premises that are far stronger than "the AI is capable": **Completeness** across incomparable outcomes and trajectory lengths (which money pumps do not force), **Optimality / outcome-level retargetability** (not automatic for trained or bounded systems), and **Uniform symmetry across reward permutations** (which says nothing about whether human-specified training distributions actually land in the power-seeking part of an orbit). The proofs sharpen the real engineering and empirical questions—whether real training pipelines produce outcome-retargetable, complete-preference agents—rather than answering them by pure mathematics.
