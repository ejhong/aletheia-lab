# Spot check of taurid-swarm by a second vendor

Claude Fable 5.2 (Anthropic), 23 November 2026, directed by Eugene. The study was run by Antigravity (Google
DeepMind). Eugene asked for a look-over and a spot check in place of a full re-run, so this is not the complete
replication that the `data` lane describes.

## What was checked

`spot_check.py` was written from `protocol.md` without using `analysis/taurid.py`, and run on both NASA archives
downloaded afresh the same day. `output.txt` holds what it printed.

| Number | Study | Spot check |
|---|---|---|
| Near-Earth asteroids with full orbits | 43,156 | 43,156 |
| On Taurid-like orbits, by size: the largest; to 1 km; to 400 m; to 150 m; all | 17; 64; 331; 848; 2,470 | the same |
| Alignment toward Encke at those sizes | +0.557; −0.001; −0.068; −0.068; −0.068 | the same |
| Share within 45° of Encke | 64.7%; 31.2%; 21.7%; 20.5%; 19.6% | 64.7%; 31.2%; 21.8%; 20.5%; 19.6% |
| Rounder-orbit comparison group, alignment | −0.356; −0.324; −0.337; −0.323; −0.185 | the same |
| Airbursts 1994 to 2025 | 1,045 | 1,045 |
| In the autumn weeks; expected | 133; 134.5 | 133; 134.5 |
| In the summer weeks; expected | 81; 88.7 | 81; 88.7 |
| Autumn, 1 kt and over; expected | 12; 14.8 | 12; 14.8 |
| Share in the autumn weeks: swarm years; other years | 12.70%; 12.96% | 12.70%; 12.96% |

Not checked: the 7:2 resonance test, the permutation p-values, the sensitivity runs, the figures.

The lock commit precedes the results commit by six minutes and follows the protocol commit in the same second.
There was no outside review before the lock.

## Review notes

The numbers are right and the verdict follows from the rule. These points are about how to read it.

1. **The seventeen largest are not a fresh test.** The study presents the alignment at the largest size as
   Napier's finding "still appearing". Large near-Earth asteroids were almost all known by 2010, so these are the
   bodies he counted. The catalogue repeats his observation; it does not test it again. The new evidence is from
   the smaller bodies.
2. **"The exact opposite of a fragmenting comet" is too strong.** The smaller bodies show no alignment, which is
   not what a break-up predicts. But the fainter sizes are dominated by the general population of asteroids, so a
   small aligned family would be diluted there. The excess of aligned bodies at the largest size is about seven
   objects, and an excess of that size could not be seen among 331.
3. **One comparison group is a poor control, as the study itself explains.** Rounder orbits are herded toward
   Jupiter's direction, away from Encke's. Against them the Taurid-like orbits look aligned at every size
   (p 0.0014 at the main size). Against the steeper-tilt group they do not. The pass rule needed both a departure
   from an even spread and a win over the first control, so the first control did no harm; but a reader should
   know that the "win" over it means nothing.
4. **A hint the write-up buries.** Down to about 150 m, 36 of 174 aligned asteroids are in the 7:2 band against
   11.7% of unaligned ones (p 0.0025), about 15 more than expected; against the other control p is 0.051. It was a
   sensitivity size, not a test, and the catalogue is incomplete there. The site page now states it.
5. **The airburst test has limited reach.** About 134 airbursts fall in the autumn weeks, so an excess of a
   fifth or so could hide. And the swarm is known from ground cameras for bodies of centimetres to decimetres; what
   it holds at metres is the open question, so a null here is informative but not decisive.
6. **Sources named in the write-up** (Egal et al. 2022; Ye et al. 2025; Wiegert et al. 2025) were not read by the
   checker. The list of swarm years rests on them.
