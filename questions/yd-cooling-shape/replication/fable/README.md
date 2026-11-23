# Replication of yd-cooling-shape by a second vendor

Claude Fable 5.2 (Anthropic), 23 November 2026, directed by Eugene. The original run was by Antigravity (Google
DeepMind).

`shape_rep.py` was written from `protocol.md` alone, without reading `analysis/shape.py`, and run on files
downloaded afresh from the URLs in `MANIFEST.md`. All five files matched the manifest's SHA-256 hashes.

    python3 -I shape_rep.py <data dir> ../../events.tsv > output.json

## Result: every number checked is reproduced

| Measure | Original | This replication |
|---|---|---|
| Coolings in the three pools | 19, 25, 10 | 19, 25, 10 |
| First 60 years, oxygen isotopes (D1) | 0.93 ‰, rank 17 of 19 | 0.927 ‰, rank 17 of 19 |
| Full temperature drop (D2) | 5.01 °C, rank 9 of 25 | 5.005 °C, rank 9 of 25 |
| Full dust jump (D2) | ×3.12, rank 10 of 25 | ln 1.137 (×3.12), rank 10 of 25 |
| Slope before the onset (D3) | +0.93 ‰ per century, rank 5 of 19 | +0.930, rank 5 of 19 |
| Antarctic change, seven-core mean (D4) | +0.042 °C, rank 8 of 10 | +0.042 °C, rank 8 of 10 |
| First 60 years, temperature | 1.71 °C, rank 22 of 25 | 1.713 °C, rank 22 of 25 |
| First 60 years, dust | ×1.13, rank 25 of 25 | ln 0.123 (×1.13), rank 25 of 25 |
| WAIS Divide | +0.044 °C, rank 10 of 10 | +0.044 °C, rank 10 of 10 |

Medians and quartiles of the other coolings agree to the printed digits. The verdict, "indistinguishable from
natural coolings" (0 of 4 criteria), follows.

Not re-derived: the three-core cross-check, the alternative windows, the accumulation measure, the figures.

## Review notes

None of these changes the verdict. They bear on how it should be worded.

1. **What the test can and cannot say.** It tests the claim that the cooling was too sharp, too deep or too
   worldwide to be natural. It does not test whether an impact set off an otherwise ordinary cooling: a comet that
   triggered the usual ocean mechanism would leave a cooling that looks like the others.
2. **"Antarctica warmed" is too strong.** The change is +0.04 °C in a reconstruction on a 40-year grid. That is no
   change. The other nine coolings show a median of −0.10 °C. The fair statement is that Antarctica did not cool.
   A winter of a few years would not show in this record in any case.
3. **Resolution.** The isotope record is in 20-year means and the temperature record is a smoothed reconstruction,
   so "abruptness" here means over decades. Published work on annual layers (Steffensen et al. 2008, from memory,
   not re-read) reports that some signals shifted within a few years at this transition while the isotopes took
   much longer. A slow start in the isotopes is therefore a known feature, and this study confirms it against
   other coolings.
4. **Blindness is limited.** The shape of the Younger Dryas onset in Greenland isotopes is among the most
   published curves in the field, and question #60 in this lab had already reported its dust rank.
5. **Process.** The lock commit is one second after the protocol commit and three minutes before the results. That
   meets the rule. There was no review by another vendor before the lock. The report names the tool
   (Antigravity) but not the model.
