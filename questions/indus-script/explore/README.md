# Exploration before the lock

Everything here is **exploratory**. It was run on 27 November 2026, before `protocol.md` was locked, on the
preprint's own archived lists only. No control language existed. None of it is evidence about the question; it
decided what the plan should test.

| File | What it is |
|---|---|
| `check_against_archive_rep1.json` | `analysis/check_against_archive.py`: the lab's contest program against the preprint's 40 archived runs of REP-1. 40 of 40 identical. (The 40 runs of REP-3, Tamil and Akkadian, were checked the same way by hand: 40 of 40.) |
| `where_score_comes_from.py`, `.json` | The preprint's Tamil list, splits 0 to 9: each sign left unread in turn; every name part given one label; grammatical endings removed; names left whole. |
| `archived_lists_at_600.py`, `.json` | The preprint's Tamil, Sanskrit and Akkadian lists at 600 names a round over 100 rounds, with and without the jar sign. |
| `dry_run_preprint_lists_only.json` | A dry run of `analysis/run_all.py` with no control inputs present. It also shows the preprint's Akkadian list with its letters mapped into the sound table, which was therefore seen before the lock. |

To rerun: unpack the preprint's `tests_archive.zip` and fetch `inscriptions.csv` (see `MANIFEST.md`), then for
example `python3 -I explore/where_score_comes_from.py <unpacked>/REP-1_tamil_vs_sanskrit <inscriptions.csv> out.json`.
