# Format notes for the replication

These notes describe the files and the output wanted. They add no analysis choice; every choice is in
`protocol.md`.

## Input files (paths relative to the working directory)

- `events.tsv`: tab-separated with a header line: `kind` (`calendar` or `earthquake`), `event`, `start_utc`,
  `control_start_utc` (both `YYYY-MM-DD HH:MM:SS`, UTC), `in_test` (`yes` or `no`), `why_not`. Use the rows with
  `in_test` = `yes` (58 of them). Each window is the 86,400 seconds beginning at its start.
- `data/basketdata-YYYY-MM-DD.csv.gz`: one gzip-compressed text file per UTC day. Example lines:

      10,1,10,"Samples per record"
      11,1,37,"Eggs reporting"
      12,"gmtime",,1,28,34,37
      13,1000166400,,105,108,,98

  The `12` line lists the egg numbers from the fourth field on. Each `13` line is one second: the Unix time,
  an empty field, then one trial sum per egg in the same order, empty where the egg did not report. Trailing
  empty fields may be missing from a line. The Unix time of 00:00:00 UTC on a day is the first second of its
  file. Egg numbers can differ from day to day.

Python 3.12 and numpy are available. No other packages. A day's array is about 86,400 × 40 values.

## Output wanted

Write to the directory given as the first command-line argument.

1. `windows.tsv`: one row per event in the test. Tab-separated, with columns `event`, `start_utc`, `z`,
   `seconds_used`, `eggs_usable`, `control_start_utc`, `control_z`, `control_seconds_used`,
   `control_eggs_usable`. Leave `z` or `control_z` empty for a window that is not evaluable.
2. `summary.json` with: `n_events` (evaluable events); `z_all`; `n_controls`; `z_controls`; `sd_controls`;
   `departure` (one of `departure`, `suggestive`, `no positive excess detected`); `size` (one of
   `smaller than the benchmark`, `not shown smaller than the benchmark`); `calibration_in_doubt` (true or
   false); `paired` (an object with `pairs`, `mean_difference`, `p_one_sided_sign_flip`).
