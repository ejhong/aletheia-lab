---
kicker: How it works
title: How the lab works
dek: An agent can try a hundred analyses in an hour and report the one that looks striking. The lab's rules are built so that the honest path is the easy one.
---

## The lab never grades the atlas

The lab produces evidence; the [Aletheia atlas](https://ejhong.github.io/aletheia/) judges it. A finished result is filed with Aletheia as an outside source, through the atlas's own process: its constitution, panel and checks. Nothing in the lab edits the atlas, merges into it, or tells its operator what to conclude, and lab agents hold no credentials for it.

## One question at a time

Each question has a GitHub issue, a folder (`questions/<slug>/`) and a branch (`q/<slug>`), and is worked on in a fresh session that ends in a pull request. At most two questions are active at once, and Eugene picks which. Nothing else is worked on.

## The lock

Every question goes through the same stages, in order:

1. **Explore** (optional). Poke at the data, try things, read around. Anything goes, but it lives in `explore/` and is labelled exploratory everywhere it is mentioned. Exploration is never evidence.
2. **Protocol.** Write `protocol.md`: the exact question, the data (with a manifest), what will be measured, how it will be judged, what result would count for and against, and the budget.
3. **Lock.** `scripts/lock.py` writes the SHA-256 of `protocol.md` and the UTC time into `protocol.lock`, which is committed on its own, before any result exists. The push timestamps it publicly.
4. **Run.** Results go in `results/` and `RESULTS.md`.
5. **Amend**, if reality intervenes: a dataset moved, or a method can't work. The locked protocol is never edited. A dated entry in `amendments.md` says what changed and why, before the changed part runs, and the results report every amendment.

The lab's checks run on every push and pull request. They fail if results exist without an earlier lock, if `protocol.md` changed after locking, or if a locked statement file changed.

What gets locked depends on the lane:

- **Data and model:** the full lock. The hypotheses, the exact test, the baseline, the threshold, and what would be concluded either way; for model experiments also the prompts, models, sample sizes and scoring rubric.
- **Proof:** the Lean compiler is the judge, so only the formal statement is locked, after models from two other vendors have checked that it says what was meant. The proof itself can change freely.
- **Audit:** the search scope and the grading rubric, before reading for the answer.
- **Protocol and watch:** no lock, because nothing is being measured.

## Lanes

Each question carries one lane, and the lane decides what "done" looks like.

{{lanes}}

## Evidence rules

These follow Aletheia's constitution, which wins on any conflict.

- Real citations only. No invented source, quotation, locator, dataset or number. Anything not yet checked is labelled `unverified`.
- Primary sources first; popular summaries help with discovery only.
- What a source states is kept separate from what the lab infers from it.
- Null and negative results are published in full, with the same care as positive ones. Many of these questions will end with "no mystery here", and that is a result.
- Every dataset has a URL, retrieval date, licence and SHA-256 in the question's manifest, so it can be downloaded again.

## Spending

Each protocol states a budget in dollars, and every paid run is logged in `SPENDING.md` with its date, question, service and cost. Agents stop and ask Eugene before going over a question's budget, or over $50 in one day across the lab. They reuse existing API keys and never create accounts or keys.

{{spending}}

## Who does the work

AI agents do the work: Claude and models from other vendors, named in each result. Eugene Jhong directs it. He picks which questions are active, and agents ask him before going over a budget or doing anything irreversible or outward-facing, such as sending email, posting, contacting researchers or submitting to a journal.

Every `RESULTS.md` names the models, vendors and dates involved, and says that Eugene directed the work. This site is generated from the repository by `scripts/build_site.py`, which was written by Claude.
