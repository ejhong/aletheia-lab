# Format notes for the replication

These notes describe the files and the output wanted. They add no analysis choice; every choice is in
`protocol.md`.

## Input files (paths relative to the working directory)

- `windows.tsv`: tab-separated with a header line, one row per event in the project's registry: `num` (the
  registry number), `description`, `begin_utc`, `end_utc` (both `YYYY-MM-DD HH:MM:SS`, UTC; `end_utc` is the last
  second of the window, so the window is the `seconds` seconds beginning at `begin_utc`), `seconds`, `published_z`
  (the project's published score for the event), `in_test` (`1` or `0`), `why_out` (empty when `in_test` is `1`),
  `control_begin_utc` (`YYYY-MM-DD HH:MM:SS`, UTC; empty when `in_test` is `0`), `control_shift_days`. Use the rows
  with `in_test` = `1` (396 of them); in the other rows the times can be free text and other fields can be empty.
  Each control window is the same number of seconds, beginning at
  `control_begin_utc`. A window can cross midnight and can be longer than a day, so it may need more than one day
  file.
- `sources/blocked.tsv`: tab-separated with a header line: `begin_unix`, `end_unix`. Each row is a stretch of
  Unix seconds, both ends included.
- `data/basketdata-YYYY-MM-DD.csv.gz`: one gzip-compressed text file per UTC day. Example lines:

      10,1,10,"Samples per record"
      11,1,37,"Eggs reporting"
      12,"gmtime",,1,28,34,37
      13,1000166400,,105,108,,98

  The `12` line lists the egg numbers from the fourth field on. Each `13` line is one second: the Unix time,
  an empty field, then one trial sum per egg in the same order, empty where the egg did not report. Trailing
  empty fields may be missing from a line. The Unix time of 00:00:00 UTC on a day is the first second of its
  file. Egg numbers can differ from day to day.

Python 3.12 and numpy are available. No other packages. A day's array is 86,400 × (number of eggs) values.

## Output wanted

Write to the directory given as the first command-line argument.

1. `windows.tsv`: one row per event in the test. Tab-separated, with columns `num`, `begin_utc`, `event_z`,
   `event_seconds_used`, `event_eggs_usable`, `control_begin_utc`, `control_z`, `control_seconds_used`,
   `control_eggs_usable`. Leave a window's `_z` and `_seconds_used` empty when the window is not evaluable.
2. `summary.json` with: `n_events` (evaluable events); `z_all` (their combined score); `n_controls` (evaluable
   controls); `z_controls`; `sd_controls`; `pairs` (an object for the pairs in which both windows are evaluable,
   with `n`, `z_events`, `z_controls`, `sd_controls`, `mean_difference`, `p_one_sided_sign_flip`);
   `reproduction` (an object with `n`, `r`, `median_abs_difference`, `combined_ours`, `combined_published`, for
   the main scores); `verdicts` (an object with `reproduction` (one of `reproduces closely`, `reproduces
   roughly`, `does not reproduce`), `events` (one of `departure`, `suggestive`, `no positive excess detected`),
   `controls` (one of `calibration failure detected`, `no calibration failure detected`) and `overall` (one of
   `insufficient coverage`, `no excess found`, `the excess is in the event windows`, `the excess is not specific
   to the events`, `mixed`)).

The scores with theoretical standardising, the scores without the egg check, the cross-egg part and the
breakdowns by year, length, overlap and control direction are not needed.
