# Format notes for the replication

These notes describe the files and the output wanted. They add no analysis choice; every choice is in
`protocol.md`.

## Input files (paths relative to the working directory, `questions/tunguska-calibration/`)

`data/standard/<core>.tsv`, one per core, tab-separated, UTF-8, with a header line `year	nh4	no3	bc	s`.
One row per sample, sorted by `year`. `year` is a decimal year CE (for example `1894.3712`). The other four cells
are positive numbers, or empty where the core has no value for that sample (a core that does not measure a
chemical has that column empty in every row).

The cores and their sites:

| File | Site | Role |
|---|---|---|
| `neem_s1.tsv` | NEEM | test |
| `tunu2013.tsv`, `tunu2022a.tsv` | Tunu | test |
| `humboldt.tsv` | Humboldt | test |
| `act11d.tsv` | ACT11d | test |
| `negis.tsv` | NEGIS | test |
| `ngrip1.tsv` | NGRIP | test |
| `summit2010.tsv`, `summit2023.tsv` | Summit | reported apart |
| `tunu2022b.tsv`, `tunu_n.tsv` | Tunu | reported apart (doubtful dating) |
| `ht95.tsv` | Hans Tausen | reported apart (doubtful dating) |
| `b20.tsv` | B20 | reported apart (doubtful dating) |

Python 3.12 and numpy are available. No other packages.

## Output wanted

Write `summary.json` to the directory given as the first command-line argument: an object keyed by `nh4`, `no3`,
`bc` and `s`, each holding

- `sites`: the sites used, sorted;
- `windows`: the number of counted windows;
- `network`: `{"value", "rank", "n", "fraction"}` for the target window;
- `verdict`: one of `exceptional`, `elevated`, `ordinary`, `not testable`;
- `by_site`: for each site used, `{"value", "rank", "n", "fraction"}` for the target window among the tiling
  windows where that site has a score;
- `excess_over_typical_year`: for each site, the size defined in the protocol; and `excess_median_of_sites`;
- `top_windows`: the ten largest counted windows as `[score, start year]` pairs, largest first;
- `variants`: an object with the keys `three-year window, 1907 to 1909`, `largest sample of each year in place of
  its mean`, `without <site>` for each site used, `DRI sites only`, `other laboratories only`, each holding
  `{"network": {...}, "verdict": ...}` (`network` may be null). The variant with the cores of doubtful dating is
  not needed;
- `reported_apart`: for each core reported apart that measures the chemical, `{"rank": {"value", "rank", "n",
  "fraction"}, "excess": number}`;
- for `s` only, `katmai_window_1912`: `{"value", "rank", "n", "fraction"}` of the window 1912 in the sulphur
  network;
- for `nh4` only, `power`: an object keyed `share 1.0, pulse 0.1` and so on (shares 1.0 and 0.5; pulses 0.1,
  0.25, 0.5, 1.0, 2.0, 4.0), each `{"elevated": share of trials called elevated or better, "exceptional": share
  called exceptional}`.

Print nothing but a short line per chemical. Round nothing before comparing; round to 4 decimals on output.
