# Log

Dated entries, newest last: what was tried, what happened, what next.

## 2026-11-23: design (Claude Fable 5.2, Anthropic; directed by Eugene)

- Eugene said "do the audit" after #66 was closed. Marked #74 active; it is the fourth active question, at his
  direction, and it runs in the session that ran #66, not a fresh one (AGENTS.md §2). Spending: the lab was over
  its $50 daily cap; asked, and he approved up to #74's $10 today.
- Priors, before any data. I expect the published scores to reproduce roughly (r above 0.8), because #47's
  program came within 0.4 of six of them. I expect the controls to come out near zero under pooled
  standardising. So my guess is "the excess is in the event windows", at perhaps 60%, which would leave the
  choice of events and windows as the open question. I give 25% to a mixed outcome and 15% to the controls
  showing the excess too. I wrote #47, which found nothing on fresh events, so I have a stake in the original
  result being explainable.
- Read the project's registry, results and analysis pages. Saved the first two.
- A sub-agent (Claude Opus 5.5) parsed the two tables into TSV files with a script, and checked 14 rows of each
  by eye against the HTML. Its count: 512 registry rows, 513 published; the 13 rows marked with an asterisk are
  the registry's 13 "No" rows; without them the published scores are 500 and combine to 7.312, against the
  page's 7.310. I re-ran the script and read its output.
- Fixed the events by rule from the tables alone (`analysis/build_windows.py`): 396 in the test, with a control
  window each, 868 day files. Their published scores combine to 6.664.
- The archive's server was fast today. Started the download of all 868 files before the lock; files are checked
  for length and for decompressing, and not parsed.
- Wrote the scoring program (`analysis/audit.py`), from #47's with three changes: windows of any length, a
  reference pool taken from whole control days outside every registered window, and no minimum of five eggs per
  second (the early network had fewer).
- The chi-square to normal conversion: the exact conversion returns minus infinity in the far lower tail; the
  Wilson–Hilferty formula agrees with it to 0.002 where both work. Kept Wilson–Hilferty.
