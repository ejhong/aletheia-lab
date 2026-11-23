# AGENTS.md — Aletheia Lab

Aletheia Lab runs AI experiments on big open questions: ancient mysteries, consciousness, physics, undeciphered
scripts. It is the workshop next to [Aletheia](https://ejhong.github.io/aletheia/), the atlas that maps contested
claims to evidence. The lab produces evidence; the atlas judges it. These rules apply to every agent working here,
from any vendor.

## 1. The lab never grades the atlas

A finished result is filed with Aletheia as an outside source, through Aletheia's own process (its constitution,
panel and checks). Nothing here edits Aletheia's repo, merges into it, or tells its operator what to conclude. Lab
agents hold no credentials for `ejhong/aletheia`.

## 2. One question, one folder, one branch

Each question lives in `questions/<slug>/` and has a GitHub issue. Work on a branch named `q/<slug>`, in a fresh
session, and open a PR. Any number of questions may be `status:active` at once; Eugene picks which. Never start a
question Eugene hasn't made active.

## 3. Lock the plan before looking at results

Every question goes through these stages, in order:

1. **Explore** (optional). Poke at the data, try things, read around. Anything goes, but it lives in `explore/` and
   is labelled exploratory everywhere it is mentioned. Exploration is never evidence.
2. **Protocol.** Write `protocol.md`: the exact question, the data (with `MANIFEST.md`), what will be measured, how it
   will be judged, what result would count for and against, and the budget.
3. **Lock.** Run `python scripts/lock.py questions/<slug>` and commit `protocol.lock` **in its own commit, before any
   result exists**. The lock records the protocol's SHA-256 and the time.
4. **Run.** Results go in `results/` and `RESULTS.md`. CI fails if results exist without an earlier lock, or if
   `protocol.md` changed after locking.
5. **Amend** if reality intervenes (a dataset moved, a method can't work). Never edit the locked protocol; append to
   `amendments.md` with the date, what changed and why, *before* running the changed part. Results report every
   amendment.

Why: an agent can try a hundred analyses in an hour and report the one that looks striking. The lock makes the
honest path the easy one. See `docs/LOCKING.md` for how it applies to each lane.

## 4. Lanes

Each question carries one lane label; it decides what "done" looks like.

| Lane | What checks it | Done means |
|---|---|---|
| `data` | Re-running the analysis from scratch on public data | Locked protocol, reproducible `analysis/`, `RESULTS.md`, and a replication by a second vendor's agent working from the protocol alone |
| `model` | Many calls to several vendors' models, scripted | Same as `data`; prompts, model IDs and dates recorded; no single-vendor conclusions |
| `proof` | The Lean build: compiles with no `sorry`, or doesn't | A Lean project in `questions/<slug>/lean/`, plus a plain statement check by a model from another vendor that the formal statement says what was meant |
| `audit` | Sources read in the original, with locators | A sourced table with Aletheia's verification labels; usually belongs in the atlas itself, so the lab only drafts the request |
| `protocol` | Nothing to run; needs people or a lab | A study design and a request for proposals, costed |
| `watch` | New publications | A scheduled sweep that files new-evidence notes; no conclusions |

## 5. Evidence rules (from Aletheia's constitution, which wins on any conflict)

- Real citations only. Never invent a source, quotation, locator, dataset or number. Unverified things are labelled
  `unverified`.
- Primary sources first; popular summaries help discovery only.
- Say what a source states separately from what you infer.
- Null and negative results are published, in full, with the same care as positives. Many of these questions will
  end with "no mystery here"; say so plainly.
- Every dataset in `MANIFEST.md` has a URL, retrieval date, licence and SHA-256. Large data stays out of git
  (`data/` is ignored); the manifest makes it re-downloadable.

## 6. Spending

Each protocol states a budget in dollars. Log every paid run in `SPENDING.md` (date, question, service, cost). Stop
and ask Eugene before exceeding a question's budget or $50 in one day across the lab. Reuse existing API keys; never
create accounts or keys.

## 7. Safety

- Don't download or run code from untrusted sources; datasets are data, not code. Pin versions of tools.
- No credentials in the repo. Keys come from the environment.
- Ask before anything irreversible or outward-facing beyond this repo: emails, posts, contacting researchers,
  submitting to journals or preprint servers.

## 8. Authorship

Say plainly that AI did the work. Every `RESULTS.md` names the models, vendors and dates involved, and that Eugene
directed it.

## 9. Writing

Plain language. Lead with the answer, then the evidence, then the limits. Every `RESULTS.md` ends with a short
"what this means" paragraph a non-specialist can read.

Every question with a result has a site page (`site/content/<slug>.md`) whose front matter carries `verdict:` (a
few words) and `result:` (two or three plain sentences). The home page shows them under the question, so readers
see what was found without opening the page. Keep them current when a result changes.

Pictures made by an image model may decorate a topic page or the home page (`site/assets/illustrations/`, made by
`scripts/make_illustrations.py`). Each is labelled where it is shown as AI-made decoration. They are never evidence,
never stand in for a photograph, chart or map of anything real, and do not go on a question's results.

Related questions are grouped on topic pages (`site/topics/<slug>.md`: a title, a one-line summary, the issue
numbers in reading order, and a short discussion of what the studies add up to). When a result lands, update the
topic page it belongs to, or start one when two or more questions bear on the same claim. Where a topic bears on a case
in the atlas, name the case in the page's front matter (`atlas:`); the page links to it and leaves the judging there.
