# Review before the lock

One outside model, Google `gemini-4-neon`, read `protocol.md` twice on 2026-11-23, before any value from 1905 to
1912 had been looked at. (Eugene asked on that day for one outside vendor in place of two.)

- `round1/`: a full critique of the first plan. Its main points, all accepted:
  1. Two-year windows that advance by one year compete with themselves: a real 1908 signal also lifts the window
     1907 and can push 1908 down the ranking. Fixed by windows that do not overlap.
  2. Moving three cores' dates by the year of their largest sulphur value near 1912 is unsafe: the marker is noisy,
     industrial sulphur is rising, the move is one-sided, and it could carry the fires of 1910 into the window.
     Fixed by altering no dates and choosing cores by a correlation check on a century of sulphur.
  3. Windows averaged over different numbers of sites are not comparable. Fixed by using the same sites in every
     window.
  4. "Ordinary" was turned into a hard upper bound on the size of Tunguska's mark. Removed.
  5. Nitrate and black carbon cannot separate an airburst from a fire year in 1908. The plan now says so and
     claims no attribution.
  6. Many points of ambiguity for an independent programmer. Specified.
  Not adopted: clamping values at or below zero in place of dropping them (they are few; the counts are stated);
  absolute fluxes for the Younger Dryas comparison (the cores' snowfall is not in the files; the comparison is
  kept as an illustration with its limits listed); ratios of ammonium to soot against known fire years (left for
  a follow-up, since the reviewer's own point is that soot is a weak guide in 1908).
- `round2/`: a narrow check of the revised plan for errors of logic and contradictions. Two found and fixed.

`run_review.py` is the script used. Cost at list price: $0.46 and $0.50.
