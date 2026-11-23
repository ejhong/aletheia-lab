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
- Sub-agents (Claude Opus 5.5) wrote the unit tests from a description of the program and adapted #47's review
  and replication scripts. The tests found no bug in the first version; they did find that a control overlapping
  a blocked stretch would be mis-handled (it cannot happen, and the program now asserts so) and, later, that a
  30% error of scale would pass as "reproduces closely" (a slope condition was added). I read both reports, ran
  the tests, and edited two tests myself after the slope change.
- Review, round 1 (two vendors, $0.83). The main change: an event and its control now share one reference pool,
  built from the control days of events within 183 days and cleaned day by day. Also: labels made exclusive,
  reproduction judged per event, published dates of disputed rows blocked (one control moved, 868 files still).
  Not done: a placebo calendar, which both asked for. `review/README.md` has the full list.
- Review, round 2, errors only ($1.07). No error in the method; wording about what each outcome means was
  tightened.
- All 868 day files present; hashes in `sources/files.sha256`. 17 unit tests pass.
- No event or control window has been scored. Next: lock.

## 2026-11-23: locked run, replication, write-up (Claude Fable 5.2)

- **Lock:** 2026-11-23T20:33:03Z, commit `e6cf1f2`. Results committed after it.
- **Locked run:** 395 events combine to +6.08 (published, same events: 6.61). Controls −0.42. Paired difference
  +0.33, p = 5 × 10⁻⁶. Labels: reproduces closely (both standardisings); departure; no calibration failure
  detected; the excess is in the event windows. One event (469) not evaluable: one device with enough data.
- The program parsed day files one at a time, about ten a minute. After half an hour I ran a helper that filled
  the same cache in parallel with the program's own reader, writing under temporary names. No score depends on
  how the cache was filled; the replications, which have their own readers, agree.
- **Replication:** OpenAI's and Google's programs both ran first time and match every window score to 0.000001,
  with the same degrees of freedom and device counts, combined scores and labels. I saw one line of OpenAI's run
  log (its agreement measures) before our own run finished.
- A detail found while writing up: the registry page's note about the live display from June 2005 sits inside an
  HTML comment and is not shown on the page.
- Spent $3.37 of $10.
- Not done: a placebo calendar; the 104 events with other recipes; reading the project's technical papers. An
  idea for a follow-up, not run: score each event's window shifted by a few hours either way. A window chosen
  with sight of the data should lose its excess when moved; an effect tied to the event should fade more slowly.

