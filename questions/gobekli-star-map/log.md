# Log

Dated entries, newest last: what was tried, what happened, what next.

## 2026-11-23: design (Claude Fable 5.2, Anthropic; directed by Eugene)

- Eugene said to do the audit (#74) "and after the star map". Marked #92 active while #74's locked run was
  going; it is run in the same session as #66 and #74 (AGENTS.md §2 asks for a fresh one), at his direction.
  Spending: the lab was over its $50 daily cap; asked, and he approved up to #92's $20 today.
- Priors, before any judging. The scorpion will be ranked first for the scorpion figure by every judge. For the
  other seven I expect blind judges not to reproduce the paper's ranks: my guess is that the claimed symbol's
  mean rank is 4 to 6 out of 12, and the label without the scorpion comes out "do not see them" (70%), "weak or
  mixed" (25%), "see the claimed matches" (5%). The issue put the odds of a real result at 3%.
- A sub-agent (Claude Opus 5.5) gathered the sources: the 2017 paper, the excavators' reply and the authors'
  answer, the 2024 accepted manuscript and the 2018 preprint. It extracted the assignments, the dating step,
  the statistical appendix and the excavators' objections with page numbers. I read the paper's p. 239 and its
  appendix myself and checked every quotation used in the protocol against the text files.
- What the reading changed. The issue imagined a shuffle test of positions on the pillar with star positions
  carried back by precession. The paper's statistics do not use positions or dates at all: the one-in-5-million
  figure is 2(P+1)/Q with P+1 = 2, from the authors' own ranking of which animal best fits each of eight stick
  figures. So the test that bears on the number is whether anyone else ranks them the same way. In 2024
  Sweatman himself named the ranking table as the place to challenge the argument, "since this is based on a
  subjective evaluation".
- A second sub-agent (Opus 5.5) extracted the 20 pictures of Table 1 from the PDF; they are stored there as
  separate images, so nothing was cropped. I looked at the contact sheet.
- Wrote the analysis program and checked its exact enumeration against brute force on a small case.
- A third sub-agent (Opus 5.5) built the stimuli and the judging script and tested the plumbing on made-up shapes
  only: all three vendors took images and ranked a triangle outline with the triangle first. Probe cost $0.20
  plus xAI tokens at an unknown price. I looked at the eight line-only figures: each keeps its whole red drawing.
- Review, one round, two vendors ($0.73). It separated three questions my first plan had mixed (are the claimed
  animals ranked first; is the pairing better than a shuffle; what does the paper's formula give), moved the
  pairing test to the pillar's own animals, added a competence check on the scorpion and a coverage rule, and
  made the arithmetic exact. Reasoning budgets were raised. `review/README.md` has the list and what was not
  done.
- A fourth sub-agent (Opus 5.5) wrote 21 tests for the analysis program, with expected values from brute force.
  All pass. It found no bug; it noted that rankings were not validated on reading (now asserted) and that the
  paper's formula can exceed 1 with tied tables, which the plan already calls "not a probability".
- No picture from the paper has been shown to any judge. Next: lock, then the judging.

- Locked 2026-11-23T21:03:35Z. After the lock and before any judging, one line of `analysis/analyse.py` was
  changed (commit `f1d805a`): the input check I had added just before the lock was too strict for the reader's own
  unit test. It checks the shape of a ranking, not its content.
- Judging started about 21:05 UTC. OpenAI and Google finished 80 trials each within minutes, all valid at the
  first attempt. xAI's model takes about three minutes a trial. To find out what that costs I sent it one request
  made of the made-up shapes: about 12,900 hidden reasoning tokens, $0.086 by the API's own figure. So xAI's 80
  trials should cost about $7, and the question stays inside its $20.
- While checking those token counts I printed one of xAI's replies: a string of twelve letters. Without the
  trial's letter key it says nothing about which symbol was ranked where, and I did not look the key up.
- The recognition questions were put to OpenAI and Google once their own ranking trials were done; xAI's follow
  when its trials finish. Calls are stateless, so one judge's recognition call cannot reach another's rankings.
- Replication: Google's model wrote its program from the protocol and format notes at 21:10 UTC, before any
  ranking was analysed. On made-up rankings it agrees with our program on all 23 numbers. One outside vendor for
  the replication, as Eugene now prefers; the review had already used two.
- A fifth and sixth sub-agent (Opus 5.5) adapted the replication scripts and wrote the figure script, both on
  made-up data, told not to open the judging output.
- xAI finished at 22:12 UTC. All 240 rankings valid at the first attempt. The locked analysis left out all three
  judges: none ranked the scorpion photograph near the top for the scorpion figure (6.4, 7.8, 10.8). Both labels:
  "not testable". I had not listed that outcome among my guesses.
- Checked for a fault of ours before accepting it: the pictures match the paper's printed table (white patches
  and all), one trial decoded by hand matches `rankings.tsv`, and the made-up-shapes test had passed. None found.
- Google's replication program gives the same exclusions and labels.
- Afterwards, and labelled as such: `explore/no_gate.py` runs the locked program with the competence check off,
  to describe what the judges did. Recognition replies read: all three name the site and the 2017 paper.
- Figures, site page, Deep memory topic page and scorecard written. Spend about $16.20 of $20.
