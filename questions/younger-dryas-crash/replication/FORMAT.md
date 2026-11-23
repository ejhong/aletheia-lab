# Format notes for the replication

These notes describe the files and the output wanted. They add no analysis choice; every choice is in
`protocol.md`.

## Input files (paths relative to the working directory)

- `data/p3k14c_scrubbed_fuzzed.csv`: UTF-8, comma-separated with quoted fields and a header line. Columns
  include `Age`, `Error`, `Material`, `Taxa`, `SiteID`, `SiteName`, `Continent`. 173,946 rows. `Age` and `Error`
  are numbers in every row. Use a CSV reader; fields contain commas and quotes.
- `data/intcal20.14c`: lines beginning `#` are comments; the rest are comma-separated: calendar age (cal BP),
  radiocarbon age, its error, and two further fields. The rows run from old to young.

Python 3.12 and numpy are available. No other packages.

## Output wanted

Write to the directory given as the first command-line argument.

1. `curves.tsv`: tab-separated with a header: `region`, `cal_bp`, `summed`. One row per region and grid point
   from 10,000 to 16,000 cal BP inclusive.
2. `summary.json`: an object with `overall` (one of `supported`, `supported as widespread`, `not supported`,
   `undetermined`) and `regions`, keyed by `North America`, `Europe`, `Asia`, each with: `dates`, `bins`,
   `step_at_target`, `p_at_target`, `power_halving`, `share_of_halvings_with_step_at_or_above_real`, `verdict`
   (one of `drop detected`, `a halving is excluded`, `cannot tell`).
