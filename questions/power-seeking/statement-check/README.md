# Statement check of `power-seeking`

Done on 2026-11-24 by Anthropic's models, at Eugene's request, after the proofs were finished. The statements and
proofs are by Antigravity (Google DeepMind). The `proof` lane asks for a plain check, by a model from another vendor,
that each formal statement says what was meant. In the two earlier proof studies (#19, #66) that check ran before the
lock, so statements could still be mended. Here the statements were locked unchecked, so nothing found below could
change them. What changed is the report: `../RESULTS.md` now says what each statement proves.

Three parts.

1. **The build** (Claude Fable 5.2). `lake build --wfail` on a clean copy, Lean v4.35.0, Mathlib at the pinned
   commit: 1,131 jobs, no warnings; all 14 theorems have the locked `def … : Prop` as their type and depend on
   `propext`, `Classical.choice` and `Quot.sound` only. Both hashes in `protocol.lock` match, and `Statement.lean`
   did not change between the lock commit and the results commit.
2. **Blind back-translation** (Claude Opus 5.5). The reader was given `Statement.lean` and nothing else: no report,
   no plan, no proofs. It was told to translate each Lean term literally, ignore names and docstrings until after,
   and say whether each is a general theorem, a small example, or trivially true. Its findings are in the table
   below. `Triviality.lean` holds the short proofs it wrote to test its claims (run with
   `lake env lean statement-check/Triviality.lean` from `lean/`); Claude Fable 5.2 compiled it again.
3. **Sources** (Claude Opus 5.5). Each cited place was looked up in the paper. `sources-check.md` is that report,
   with quotations and page numbers. The papers were read from a scratch folder that is not in the repository
   (`spot4-power/…` in that file); Claude Fable 5.2 checked the main quotations against the texts.

## What each statement says

| | What the Lean term says, literally | Kind | Against its source |
|---|---|---|---|
| S1a | For preferences over lotteries on a finite set that are complete, transitive, independent and Archimedean, there is an expected-utility function, unique up to positive scale and shift. | General theorem | The von Neumann–Morgenstern theorem in its modern four-axiom form. Same. |
| S1b | Given a cycle a, b, c and the assumption that each paid trade along it is accepted, there is a chain of trades from a back to a with less money. | Three applications of its own hypothesis | The simple money pump. Gustafsson (2022, p. 3) grants that foresight blocks this version. Simplified. |
| S1c | There are reflexive, transitive, incomplete relations (one on two goods with money, one on lotteries) with no chain of weakly preferred trades that loses money and no strict cycle. | Small example | The "no pump" part follows from transitivity alone; a complete relation passes the same test (`Triviality.lean`). Trades between incomparable options, which are what the disputed pump uses, are excluded by definition. Credited to Gustafsson, ch. 2; his ch. 3 argues the opposite. Does not show what was claimed. |
| S1d | For any deterministic policy there is a utility on whole histories that the policy's action beats every other action on, one step ahead. | Trivial by design | Shah (2018), his own construction. Same. |
| S2a | If one permutation sends every parameter favouring A to one favouring B, then in every orbit at least as many favour B as A. | General, short | Turner and Tadepalli (2022), Prop. 3.4. Same. |
| S2b | With n such permutations whose images do not overlap, at least n times as many. | General, short | Thm. 3.6. Same. |
| S2c | For finite sets of vectors F₁, F₂ and an involution φ with φ·F₁ ⊆ F₂: over the orbit of any finitely supported reward distribution, the average of the best inner product is higher for F₂ at least as often as for F₁; it is at least as high whenever the distribution is φ-invariant; and the reverse fails when F₂ has a further non-dominated element. | General theorem | A special case of Turner et al. (2021), Lemma E.24, and so of Prop. 6.12 at discount 1. The term has no decision process, policy, discounting or normalisation. It is not Thm. 6.13. Special case, named for more than it is. |
| S2d | Some reward distribution gives {e₀} a higher value than {e₁, e₂}. | One point mass | The paper says the same (p. 5), and its theorem never assumed a symmetric distribution. Not a dropped premise. |
| S2e | There is a symmetric distribution under which the larger set is worth more, and a function to {true, false} that is false on its support. | The function is unconstrained; a constant does | Turner and Tadepalli put systems that are not retargetable outside their scope (§6.2). Shows nothing about optimality. |
| S2f | There are sets F₁ ⊂ F₂ with the same best value for every reward. | One example | Built into the source (non-dominated elements, Def. 3.6). |
| S3a | In a table with rows leave = p·vShut + (1−p)·vRun, prevent = vRun − c, cause = vShut − c: prevent beats leave when c < p(vRun − vShut); cause beats leave when c < (1−p)(vShut − vRun); neither does for every c > 0 only if vRun = vShut. | Arithmetic | Echoes Soares et al. (2015), eq. 10, and Thornley's First Theorem. Neither theorem. Simplified. |
| S3b | If vRun = vShut and c > 0, leave beats both. | One line | Indifference is assumed, not built. Soares et al., §4, give two ways the indifference approach fails. Simplified. |
| S3c | A complete, transitive relation on four points (short or long, worse or better) that ranks better above worse at each length has a strict preference between some short and some long point. | A finite fact | A two-by-two case of what Thornley (2025) draws from his Second Theorem. Special case. |
| S3d | A reflexive, transitive relation on the same four points exists with no strict preference across lengths. | One example | A four-point picture of the proposal in Thornley et al. (2024, arXiv:2407.00805). It shows such a relation exists, not that an agent holding it stays shutdownable. Credited to the wrong section of the wrong paper. |

Tally: six say what a source says (S1a, S1d, S2a, S2b, and the special cases S2c and S3c); three are simplified
versions (S1b, S3a, S3b); five are small examples that do not carry the conclusion the first report drew from them
(S1c, S2d, S2e, S2f, S3d).
