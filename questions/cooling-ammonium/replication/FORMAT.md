# Format notes for the replication

These notes describe the files and the output wanted. They add no analysis choice; every choice is in
`protocol.md`.

## Input files (paths relative to the working directory)

- `data/pangaea/935814.tab`: NGRIP 10-yr file. `data/pangaea/935831.tab`: NEEM 10-yr file. UTF-8. A header block
  ends with a line beginning `*/`; then one line of column names; then tab-separated rows: age in ka b2k,
  conductivity, sodium, calcium, ammonium, nitrate. Trailing empty fields may be absent from a row, so pad short
  rows. Age in years is the ka value times 1000, rounded to the nearest whole number; all are multiples of 10.
- `events.tsv`: tab-separated with a header line: `event`, `ngrip_depth_m`, `age_b2k`, `kind` (`stadial onset`
  or `other`), `definition_uncertainty` (`4yr`, `a`, `b`, `c`, `d`, `f`, or empty). 111 rows.

Python 3.12 and numpy are available. No other packages.

## Output wanted

Write to the directory given as the first command-line argument.

1. `events.tsv`: one row per chemical (`ammonium`, `calcium`), core (`NGRIP`, `NEEM`) and cooling that passes the
   selection rules, evaluable or not. Tab-separated, with columns `ion`, `core`, `event`, `D`, `D_pct`, `P`,
   `P_pct`, `R`, `R_pct`, `H`. Leave a field empty where a value does not exist.
2. `summary.json` with: `coolings` (the list of event names that pass the selection rules); `quiet_times` (an
   object giving the number of quiet times with D defined for `ammonium` and `calcium`, each by core);
   `general` (one of `general`, `not seen`, `mixed`) and `younger_dryas` (one of `the largest`,
   `among the largest`, `not among the largest`), both for ammonium on D; and `rank` (GS-1's rank on D for
   ammonium, by core).
