# Format notes for the replication

These notes describe the files and the output wanted. They add no analysis choice; every choice is in
`protocol.md`.

## Input files (paths relative to the working directory)

- `data/pangaea/935814.tab`: NGRIP 10-yr file. `data/pangaea/935831.tab`: NEEM 10-yr file.
  `data/pangaea/935818.tab`: NGRIP 1 mm file (77 MB, 1,525,701 data rows). UTF-8. A header block ends with a line
  beginning `*/`; then one line of column names; then tab-separated rows. Trailing empty fields may be absent
  from a row, so pad short rows.
- `data/noaa/gicc05-60ka-20yr.txt`: Latin-1. Free text, then data rows of four whitespace-separated numbers.
- `data/noaa/iond.txt`: Latin-1. Free text, then a header line whose first tab-separated field is `Top`, then a
  blank line, then tab-separated rows of 12 fields.

Python 3.12 and numpy are available. No other packages.

## Output wanted

Write to the directory given as the first command-line argument.

1. `windows_<series>.tsv` for each of the 14 series (N10, E10, N20, E20, G20, N60, E60, G60, N3, N1, G10, E10h,
   G20h, G60h), ammonium, 300-year windows. One row per usable window; tab-separated; columns:
   `k`, `start`, `end`, `bins`, `with_value`, `E`, `E_age`, `H`, `H_age`, `Z`, `Z_age`, `mean`.
   `E_age` is the start age of the bin that gives E, and likewise for H and Z. Write `nan` for a missing value.
2. `summary.json` with: `verdict` (one of `not testable`, `exceptional`, `unusual`, `not corroborated`,
   `not met`); `ranks`, an object keyed by measure (`E`, `H`, `Z`) then by series, each with `value`,
   `rank`, `N`, `in_top1`, `in_top5` for the target window (or null if the target lacks that measure).

The other reported items (widths, bin phase, one-sided backgrounds, nitrate, made-up fires) are not needed.
