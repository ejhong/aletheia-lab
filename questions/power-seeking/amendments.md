# Amendments — Do the theorems show that capable AI must seek power? (#67)

## Record added after the statement check — 2026-11-24

Nothing in `lean/` was changed. `Statement.lean` is locked, so its docstrings stand as written, including the ones
this record corrects.

1. **The statement check came after the lock.** The plan said no other vendor's model was available and left the
   check pending. It was done on 24 November 2026 by Anthropic's models (`statement-check/`). Six of the 14
   statements say what a source says, three are simplified versions, and five are small examples that do not carry
   the conclusions the first report drew from them. `RESULTS.md` has been rewritten to say what each proves.
2. **Source locators corrected.**
   - S1c was credited to Gustafsson (2022), ch. 2. That chapter is on acyclicity. His ch. 3 argues that completeness
     is required by a money-pump argument, the opposite of what S1c was said to show. The view that incomplete
     preferences escape money pumps is Thornley's ("There are no coherence theorems", 2023) and Petersen's (2023).
   - S2c is a special case of Turner et al. (2021), Lemma E.24, and of Prop. 6.12 at discount 1. It is not
     Thm. 6.13. Non-domination is Def. 3.6, not Def. 6.10.
   - Thornley's paper is *Philosophical Studies* 182 (2025), 1653–1680, online 19 June 2024. In the published
     version the First Theorem is in §7 and the Second in §8. The proposal S3d pictures is in Thornley et al.
     (2024), arXiv:2407.00805, not in "§9".
   - Shah's post is "Coherence arguments do not entail goal-directed behavior" (3 December 2018).
   - The Appendix of von Neumann and Morgenstern is in the second edition (1947).
3. **Wording in the locked plan that the statements do not support.** The plan's table calls S2d and S2e
   counterexamples "on a 3-state MDP" with "optimal policies" and "a non-optimal policy". The Lean terms contain
   three basis vectors, no decision process and no policy.
