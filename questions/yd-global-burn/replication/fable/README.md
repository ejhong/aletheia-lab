# Independent replication by a second vendor

Claude Fable 5.2 (Anthropic), 23 November 2026, at Eugene's request, before the pull request was merged.

Two short programs were written from `protocol.md` alone, without reading `analysis/burn.py`. The data were
downloaded afresh from the URLs in `MANIFEST.md`; all six SHA-256 hashes match. The replicator had read the pull
request's summary of results before writing the programs, so it was not blind to the numbers, only to the code.

    python replication/fable/archive_a.py .      # run from questions/yd-global-burn
    python replication/fable/archive_b.py .

## What was recomputed, and how it compares

| Measure | Original | Replication |
|---|---|---|
| `WAIS_CO2`: value, rank | +4.52 ppm, 14 of 38 | +4.522 ppm, 14 of 38 |
| `TG_BURN`: value, rank | 0.488 ppm·‰, 7 of 54 | 0.488 ppm·‰, 7 of 54 |
| `TG_D13C`: value, rank | 0.113 ‰, 6 of 54 | 0.113 ‰, 6 of 54 |
| `TG_BURN`: seven highest windows | 15,950; 12,350; 39,650; 16,250; 16,850; 39,350; 12,650 | the same, same values |
| `EGG_D13C`: value, rank | 0.030 ‰, 4 of 499, 2 ties | 0.030 ‰, 4 of 499, **3 ties** |
| Charcoal Tier C1: sites | 19 | 19 |
| `E_mean`: value, rank | 0.000 SD, 20 of 45 | 0.000 SD, 20 of 45 |
| `F_peak` (≥ +1.0 SD): value, rank | 0.053 (1 of 19 sites), 38 of 45 | 0.053 (1 of 19 sites), 38 of 45 |
| `F_peak`: highest window | 11,450–11,750 (0.294) | 11,450–11,750 (0.294) |

Also done: `analysis/test_burn.py` passes (10 tests), and rerunning `analysis/burn.py` on the fresh downloads
reproduces every committed file under `results/` byte for byte.

**The verdicts follow:** Archive A "single-record only", Archive B "not met", joint "partial / mixed".

## The one difference

For `EGG_D13C` the replication counts three windows tied with the target at 0.030 ‰ (starting 16,550, 17,750 and
47,150), where the original counts two and lists the window starting 17,750 as rank 7. The record is given to
three decimals and the measure is a difference of interpolated values, so whether 0.030 equals 0.030 turns on
floating-point noise; the replication rounds to six decimals before comparing. With three ties the realised
fraction is 7 of 499 (1.4%), not 6 of 499 (1.2%). The rank is 4 either way, so the verdict does not change.

## Not replicated

`E_100`, tiers C2 and C3, the regional breakdown, the width and phase variants, the made-up fire pulses and the
mass-balance figures.
