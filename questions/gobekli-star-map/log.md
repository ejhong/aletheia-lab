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
