# Protocol — Do the Theorems Show That Capable AI Must Seek Power? (#67)

- **Issue:** #67 (`lane:proof`)
- **Date:** 2026-11-24
- **Budget:** $0 (local Lean 4.35.0 + Mathlib v4.35.0 verification; zero paid API calls available in this VM)
- **Locked statement file:** `lean/PowerSeeking/Statement.lean`

## 1. Exact Question

Two families of formal results—**coherence / expected-utility representation theorems** and **optimal-policy / retargetability power-seeking theorems**—together with **shutdown-problem theorems**, are widely cited for the claim that a capable AI system must act as an expected-utility maximizer, pursue power, and resist being switched off.

What exactly follows from which premises when written out in full inside a proof assistant (Lean 4), alongside the standard counterexamples and limits?

## 2. Primary Sources & Locators

All definitions and statements in `lean/PowerSeeking/Statement.lean` are tied to the following primary texts (archived and hashed in `MANIFEST.md`):

1. **von Neumann & Morgenstern (1944)**, *Theory of Games and Economic Behavior*, §3.6 & Appendix — finite lottery space, Completeness, Transitivity, Independence, Archimedean Continuity, expected-utility representation & positive affine uniqueness (`S1a`).
2. **Gustafsson (2022)**, *Money-Pump Arguments*, Cambridge University Press (`doi:10.1017/9781108754750`), Ch. 2 — intransitive 3-cycle money pump (`S1b`) and incomplete-preference non-exploitability (`S1c`).
3. **Shah (2018)**, "Coherence arguments do not imply goal-directed behavior" — triviality of history-based utility maximization for arbitrary deterministic policies (`S1d`).
4. **Turner & Tadepalli (2022)**, "Parametrically Retargetable Decision-Makers Tend To Seek Power", NeurIPS / `arXiv:2206.13477`, Defs. 3.1–3.5, Prop. 3.4 (`S2a`), Thm. 3.6 (`S2b`).
5. **Turner, Smith, Shah, Critch & Tadepalli (2021)**, "Optimal Policies Tend to Seek Power", NeurIPS / `arXiv:1912.01683`, Defs. 5.2, 6.1–6.5, Prop. 6.6 & Lemma E.24 / Thm. 6.13 (`S2c`), plus boundary counterexamples dropping symmetry (`S2d`), dropping optimality (`S2e`), and adding dominated options (`S2f`).
6. **Soares, Fallenstein, Yudkowsky & Armstrong (2015)**, "Corrigibility", AAAI Workshop, Thms. 1–2 & §3 (`S3a`, `S3b`).
7. **Thornley (2024)**, "The shutdown problem: an AI engineering puzzle for decision theorists", *Philosophical Studies* 182 (`doi:10.1007/s11098-024-02153-3`), §6–7, Thms. 1–2 (`S3a`, `S3c`) & incomplete-preference escape hatch (`S3d`).

## 3. Formal Target Statements (`lean/PowerSeeking/Statement.lean`)

All 14 statements are written as `def S… : Prop` in `lean/PowerSeeking/Statement.lean` and locked via `protocol.lock` before any proof is written:

| ID | Statement | Family | Role |
|---|---|---|---|
| `S1a_VNMRepresentation` | Completeness + Transitivity + Independence + Archimedean Continuity on finite lotteries → EU representation unique up to `a·u + b` (`a > 0`) | Coherence | Positive theorem |
| `S1b_IntransitiveMoneyPump` | Strict 3-cycle + willingness to pay `ε > 0` → finite trade chain ending at same good with strictly less money | Coherence | Positive theorem |
| `S1c_IncompleteNoMoneyPump` | Reflexive, transitive, money-monotone (and independent on lotteries) INCOMPLETE preferences immune to money pumps / strict cycles | Coherence | Limit / counterexample |
| `S1d_HistoryUtilityTriviality` | Every deterministic policy `π` over finite histories strictly maximizes some history utility function `U` | Coherence | Triviality limit |
| `S2a_SimpleRetargetability` | Simply `(S_Θ, A → B)`-retargetable decision function → `fB ≥_1^most fA` on every orbit | Power-seeking | Positive theorem |
| `S2b_MultiplyRetargetable` | `n`-fold multiply retargetable function → `fB ≥_n^most fA` on every orbit | Power-seeking | Positive theorem |
| `S2c_OptimalPolicyPowerSeeking` | Involution copy `φ • F₁ ⊆ F₂` → (1) `POWER(F₂) ≥_1^most POWER(F₁)` on every orbit, (2) direct `POWER_D(F₂) ≥ POWER_D(F₁)` for `φ`-invariant `D`, (3) strict converse failure if `∃ w ∈ F₂ \ φ • F₁` non-dominated | Power-seeking | Positive theorem |
| `S2d_CounterexampleDropSymmetry` | On a 3-state MDP where `openOpts` strictly copies `shutOpts`, a non-symmetric reward distribution makes optimal policies strictly choose shutdown | Power-seeking | Boundary counterexample |
| `S2e_CounterexampleDropOptimality` | On the same 3-state MDP under a fully permutation-invariant distribution, a non-optimal policy chooses shutdown 100% of the time | Power-seeking | Boundary counterexample |
| `S2f_CounterexampleDominatedOptions` | Adding dominated convex combinations increases `|F|` without changing `optVal` or `POWER` for any reward or distribution | Power-seeking | Boundary counterexample |
| `S3a_ShutdownManipulationDichotomy` | Complete EU maximizer with `p ∈ (0,1)` resists shutdown if `vRun > vShut` and `c < p(vRun − vShut)`, causes shutdown if `vShut > vRun` and `c < (1−p)(vShut − vRun)`, and avoids both at all `c > 0` only if `vRun = vShut` | Shutdown | Positive theorem |
| `S3b_ShutdownIndifferenceCorrigibility` | Whenever `vRun = vShut` and `c > 0`, `leave` strictly beats both `prevent` and `cause` for every `p ∈ (0,1)` | Shutdown | Boundary counterexample |
| `S3c_TransitiveIndifferenceImpossibility` | Any complete, transitive preference that is useful within both short and long trajectories must have a strict preference between some short and some long trajectory | Shutdown | Positive theorem |
| `S3d_IncompletePreferencesEscape` | Dropping completeness admits a reflexive, transitive preference that is strictly useful within both short and long trajectories with zero cross-length strict preferences | Shutdown | Escape / limit |

## 4. Verification & Acceptance Criteria

1. **Clean Lean 4 build:** `lake build --wfail` compiles with zero errors and zero warnings.
2. **Forbidden-token clean:** Zero occurrences of `sorry`, `admit`, `native_decide`, or new `axiom` declarations anywhere outside `Audit.lean` (matching `.github/workflows/lean.yml`).
3. **Kernel axiom audit:** Every headline theorem (`S1a`–`S3d`) is checked inside the build via `#assert_standard_axioms` to depend solely on Lean's three standard axioms (`propext`, `Classical.choice`, `Quot.sound`).
4. **Statement-check transparency:** Because no external vendor API keys (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`) are configured in this VM, automated multi-vendor statement review cannot be run inside this session. All statements are locked before proving, tied directly to primary-source locators, and flagged clearly in `RESULTS.md` as awaiting independent second-vendor statement check.
