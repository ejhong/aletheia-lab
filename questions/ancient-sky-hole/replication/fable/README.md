# Independent replication: the hole in the ancient sky

**Replication by Claude Opus 5.5 (Anthropic) on 2026-11-23, directed by Eugene, working from `protocol.md` and
`MANIFEST.md` alone.** The original study was run by Google's model. I wrote my own program
(`skyrep.py`, `ltp.py`) before opening any of the original code, results, `RESULTS.md`, `log.md`, `amendments.md` or
the site. I opened `results/summary.json` only after `output.json` was on disk. After that I read parts of
`analysis/skyhole.py` to explain the differences listed below, and `diag_after_compare.py` was written at that stage.

## The answer

**All the main numbers reproduce, and so does the verdict under the locked rule ("excludes pre-3000 BCE").** The
primary fit, all 13 variants, the 3000 BCE likelihood gap and all 21 leave-one-out refits match exactly in epoch and
latitude. Four things differ slightly, and I traced each one to a known cause:

1. The log-likelihoods differ by about 0.04. The original rounds V50 and sV to four decimals before using them in the
   fit; I didn't. With the rounded values my code gives the original's -935.7886 exactly.
2. The M3 epoch: 10 BCE against their 41 BCE. The protocol gives M3 only a 0.5° grid for R, and they refined R to
   0.2°. With their grid my code gives -40, R = 41.7°, lnL = -874.3134 exactly.
3. The bootstrap bounds differ a little. The random draws differ, and the original never runs the refined grid inside
   the bootstrap.
4. The M4 offset: 4.12° against their 3.94°. The grids differ, and the likelihood surface is flat there.

## What I did

- **Data.** Downloaded the three VizieR files with the manifest's URLs into a separate scratch directory. **None of
  the raw SHA-256 hashes match the manifest.** That is expected: each VizieR TSV header carries the query date and
  time (`#Date: 2026-11-23T19:11:30`, `request_date=`). The row counts match the manifest exactly: Ptolemy 1,028;
  Hipparcos 15,544 (15,537 with valid positions, as in the protocol); BSC 9,110. The BSC was not used.
- **Precession.** I wrote my own vectorised Vondrák–Capitaine–Wallace (2011) `ltpequ` (`ltp.py`). It agrees with
  `erfa.ltpequ` from pyerfa 2.0.1.5 (installed in a throwaway scratch venv, used only for the check) to 0.005″
  everywhere in ±200,000 yr. Sanity checks: the pole passes 0.22° from Thuban in 2750 BCE and 2.7° from Vega in
  12,000 BCE. The obliquity is 23.439° at J2000 and 24.019° at 3000 BCE. All in `check_ltp.py`.
- **Models.** M1 to M4, the spatial block bootstrap (B = 500, seed 20261123), LOCO, the envelope and the decision
  rule, each implemented as the protocol describes them. The bootstrap runs the full M1 refit, coarse grid and then
  refined grid, on every resample.
- **Tools.** Python 3.12.16, NumPy 2.3.5, no other packages; pyerfa 2.0.1.5 only for the cross-check. The full run
  took 82 s on one core (`run.log`).

## Comparison table

| Quantity | Mine | Original | Match? |
|---|---|---|---|
| Hipparcos stars, valid position | 15,537 | 15,537 (protocol) | exact |
| Universe, V ≤ 5.5 | 2,848 | (cap 690 + test 2,158 = 2,848) | exact |
| Calibration cap (β > 30°, V ≤ 5.5) | 690 | 690 | exact |
| Test region (β ≤ 30°, V ≤ 5.5) | 2,158 | 2,158 | exact |
| Unique HIP catalogued, any magnitude: all48 / in_figure / aratus_core / strict_id | 1,020 / 912 / 895 / 1,006 | 1,020 (protocol, all48) | exact where stated |
| Catalogued in universe V ≤ 5.5 (same order) | 989 / 884 / 868 / 978 | not reported | – |
| Catalogued in test region (same order) | 767 / 673 / 657 / 757 | 767 / 673 / 657 / 757 | exact |
| Catalogued in cap: all48 / in_figure / aratus_core / strict_id | 222 / 211 / 211 / 221 | 222 / 211 / 211 / 221 | exact |
| Calibration all48 (V50, sV) | 4.41549, 0.30894 | 4.4155, 0.3089 | exact (to 4 dp) |
| Calibration in_figure = aratus_core | 4.31300, 0.37556 | 4.313, 0.3756 | exact |
| Calibration strict_id | 4.41483, 0.30497 | 4.4148, 0.305 | exact |
| **M1 primary epoch, latitude** | **910 CE, 25.8° N** | **910 CE, 25.8° N** | exact |
| M1 primary max lnL | -935.750 | -935.789 | differs by 0.04 (rounded calibration; reproduced exactly) |
| ΔlnL, 3000 BCE (best φ) vs best | -106.16 (t = -2999, φ = 19.15°) | -106.2 (t = -3000 grid row, φ = 19.0°) | match |
| Naive star-level 95% CI, epoch | 320 – 1000 CE | 350 – 1000 CE | grid resolution (mine 10 yr, theirs 50 yr coarse) |
| Naive star-level 95% CI, latitude | 24.3 – 27.9° | 24.5 – 27.5° | grid resolution |
| M1 kV = 0.15 | 210 CE, 33.2° | 210 CE, 33.2° | exact |
| M1 kV = 0.20 | 880 CE, 28.0° | 880 CE, 28.0° | exact |
| M1 kV = 0.25 | 910 CE, 25.8° | 910 CE, 25.8° | exact |
| M1 kV = 0.30 | 820 CE, 24.0° | 820 CE, 24.0° | exact |
| M1 kV = 0.35 | 720 CE, 22.5° | 720 CE, 22.5° | exact |
| in_figure | 670 CE, 27.0° | 670 CE, 27.0° | exact |
| aratus_core | 500 CE, 28.2° | 500 CE, 28.2° | exact |
| strict_id | 930 CE, 25.8° | 930 CE, 25.8° | exact |
| V ≤ 4.0 | 121 BCE (t = -120), 31.8° | -120, 31.8° | exact |
| V ≤ 4.5 | 50 CE, 30.3° | 50 CE, 30.3° | exact |
| V ≤ 5.0 | 610 CE, 27.0° | 610 CE, 27.0° | exact |
| M2 best (kV, epoch, latitude) | 0.10, 160 CE, 35.7° | 0.10, 160 CE, 35.7° | exact (kV hits the lower edge of its grid in both) |
| M3 best (epoch, R) | t = -10 (11 BCE), R = 41.5° | t = -40 (41 BCE), R = 41.7° | differs by 30 yr: their finer R grid (reproduced exactly) |
| LOCO epoch range | 680 – 1000 CE | 680 – 1000 CE | exact |
| LOCO latitude range | 25.8 – 26.7° | 25.8 – 26.7° | exact |
| Most influential constellation | Piscis Austrinus (-230 yr, +0.9°) | Piscis Austrinus (-230 yr, +0.9°) | exact (all 21 refits identical) |
| Bootstrap 95%, epoch | -206 (207 BCE) – 1000 CE | -200 (201 BCE) – 1000 CE | close (different draws; theirs coarse grid only) |
| Bootstrap 95%, latitude | 22.7 – 30.5° | 21.5 – 30.5° | close; lower end differs by 1.2° |
| Bootstrap 68%, epoch / latitude | 302 – 1000 / 24.7 – 27.8° | 300 – 1000 / 24.5 – 28.0° | close |
| Bootstrap median epoch / latitude | 900 CE / 26.0° | 900 CE / 26.0° | exact |
| M4 off-track angle (M1-based free pole) | 4.12° (closest track epoch 1036 CE, 2ΔlnL = 9.19, φ = 25.3°) | 3.94° (1075 CE, 2ΔlnL = 9.08, φ = 25.5°) | close (grid detail) |
| M4 off-track angle (M3-based free pole) | 1.05° (track epoch 46 BCE, 2ΔlnL = 0.88) | not computed | – |
| Systematic envelope, epoch | -120 – 930 | -120 – 930 | exact |
| Systematic envelope, latitude | 22.5 – 35.7° | 22.5 – 35.7° | exact |
| **Combined range, epoch** | **-206 – 1000 (207 BCE – 1000 CE)** | **-200 – 1000 (201 BCE – 1000 CE)** | close |
| Combined range, latitude | 22.5 – 35.7° | 21.5 – 35.7° | close |
| **Verdict (locked rule)** | **1: excludes pre-3000 BCE** (t_lo = -206 > -2999; off-track 4.1° ≤ 6°) | **excludes_pre_3000_bce** | **reproduced** |

The upper end of 1000 CE in the bootstrap and combined ranges is the edge of the search domain, not a measured limit.

## Diagnosis of each difference (after reading `analysis/skyhole.py`)

1. **Log-likelihoods are 0.04 lower in the original.** It stores V50 and sV rounded to four decimals
   (`round(v50, 4)`) and feeds the rounded values into every fit. Evaluating my code at (910 CE, 25.8°) with
   V50 = 4.4155 and sV = 0.3089 gives -935.78864, which is their figure to the last digit. The difference is harmless
   but slightly departs from "fit by maximum likelihood".
2. **M3 epoch, -40 against -10.** The original refines M3 on a 10 yr × 0.2° grid in R (±4°) around the coarse
   optimum. The protocol states R only "step 0.5°". With their grid my code reproduces t = -40, R = 41.7°,
   lnL = -874.3134. The M3 surface is flat in epoch to within tens of years.
3. **Bootstrap.** (a) The original takes each resample's maximum on the coarse 50 yr × 0.5° grid only, with no
   refinement. Their bootstrap epochs are all multiples of 50, for example -650, -600, -450. I refined every resample,
   as §5.2 describes the M1 fit. (b) They draw counts with `rng.multinomial`; I used `rng.integers`. The random
   streams therefore differ, as expected. Neither choice changes the verdict: 0 of 500 resamples fall before
   3000 BCE in my run, and the lowest of theirs is 651 BCE.
4. **M4.** The original fits only the M1 version of the free pole, at t0 = the M1 best epoch, with φ on a 1° grid.
   Its refinement uses 0.5° steps in β, against the protocol's 0.25°. I used an area-uniform 2° pole grid and a
   0.25° tangent-plane refinement, and found a pole 0.2° away with lnL 0.05 higher. Both stay well under the 6°
   threshold.

## Ambiguities in the protocol I had to resolve

1. **Raw hashes cannot match on re-download.** VizieR stamps the query time into the header. The manifest should
   hash the data rows only (header lines starting `#` removed), or keep a copy of the file.
2. **Ecliptic coordinates for β.** The protocol doesn't say which ecliptic or epoch. I used the J2000 mean ecliptic
   (ε = 84381.406″) at the J2000 positions; the original used J1991.25 positions. The cap and test counts are
   identical.
3. **Refraction.** "Bennett's formula" is normally apparent→true. The protocol's worked value (h = 0 → +0.57°) only
   fits if Bennett's formula is applied to the geometric altitude, so that is what I did. The original did the same.
4. **Calibration likelihood.** I fitted a plain logistic without the lapse ε, as the formula in §5.1 is written.
5. **Magnitude cut-off variants.** §5.1 freezes the calibration from the V ≤ 5.5 cap, so I kept it and applied the
   cut only to the test set. The original did the same. As a side check, refitting the calibration at each cut gives
   V ≤ 4.5: 20 CE, 29.2°; V ≤ 5.0: 590 CE, 27.3°. At V ≤ 4.0 the cap logistic is nearly perfectly separated
   (103 of 109 stars catalogued), so that refit is not meaningful.
6. **in_figure / aratus_core.** I took the excluded stars as y = 0, the literal reading, not dropped from the sky.
   The original did the same.
7. **Refined grid at the domain edge.** I clipped the refined window to the coarse domain (t ≤ 1000, 15 ≤ φ ≤ 50).
   This matters because the primary fit (910 CE) and the bootstrap's upper bound sit at or near the 1000 CE ceiling.
8. **M2 search.** The protocol doesn't say how to search jointly. I ran a full M1 coarse+refine fit at each of the
   21 kV values and took the best. The original did the same. The best kV, 0.10, is the grid's lower edge, so M2 is
   not actually maximised inside its stated range.
9. **M3 refinement.** None is stated. I refined the epoch only, keeping R on its stated 0.5° grid. This one choice
   is what produces the 30 yr difference.
10. **Bootstrap refit.** Should "refit Model M1" include the refined grid? I said yes; the original said no.
11. **M4.** The protocol leaves open which model's free-pole offset feeds the decision rule (M3 or M1), and what
    "t0" is. I computed both versions, with t0 = each model's best epoch, and used the larger offset (the M1 one,
    4.1°) in the rule. The original used only the M1 version. The track was −p_N(t) for t ∈ [-24000, 2000].
12. **LOCO.** I resolved four points: (a) which stars define "a constellation with a star south of −15°" (I used its
    I ≤ 3 identified stars of any magnitude); (b) a star listed in two constellations is dropped with either; (c) the
    calibration is not refit; (d) "most influential" means the largest |Δepoch|. The original's choices give the same
    21 constellations and identical refits.
13. **Systematic envelope.** I included the primary fit itself, and M3 for the epoch only, as §6 lists.

## What this means

A second AI, from a different company, wrote its own code from the locked plan alone and got the same answers. The
primary date and latitude, every variant, every leave-one-out refit and the verdict all come out the same: the empty
southern patch in Ptolemy's catalogue cannot be fitted by a sky from before 3000 BCE. The few small differences come
from grid spacing and rounding, which the plan left open. They never move a date by more than 30 years in a fit, or
by a few years in the headline range. The replication confirms the arithmetic. It does not settle what the
arithmetic measures. The study dates the southern edge of the stars Ptolemy (and Hipparchus before him) catalogued.
That is not necessarily the date the constellation figures were invented (see below).

## Replicator's view: does the study measure what its verdict says?

The study measures when and where the southern edge of the **catalogued stars** was set. A cataloguer adds every
star he can see to an existing figure: the feet of Centaurus (now Crux and α Cen), the keel of Argo with Canopus, and
the lower stars of Ara and Lupus are exactly the stars that set the edge. So the edge dates the last and southernmost
observer, not the first. A pre-3000 BCE origin of the *figures*, with later Greek observers filling in the stars they
could see, predicts the same catalogued edge. The verdict sentence "excludes an origin before 3000 BCE" therefore
claims more than the test can show. The data say that Ptolemy's catalogue has the southern edge of a Hellenistic
observer, which nobody doubts. The M1 primary fit also lands 770 years after Ptolemy, a sign that its extinction model
is misspecified.

None of the variants removes the cataloguer. *V ≤ 4.0* keeps the bright edge stars (α Cen, the stars of Crux,
Canopus), which Hipparchus and Ptolemy themselves placed. *in_figure* and *aratus_core* drop the 108 informes and two
late constellations, but keep Ptolemy's own choice of which faint and southern stars belong to every remaining figure.
Aratus names figures; he gives no star list, and the variant borrows the star list from Ptolemy. *M3* removes the
extinction model, not the cataloguer. That all of them land between 121 BCE and 670 CE is what you would expect if
the cataloguer sets the edge, so their agreement is not independent support for a late *origin*.

A test of the constellations' own age needs evidence fixed before Hipparchus: the figures' extents as described in
Aratus' *Phaenomena* and in the Eudoxus passages Hipparchus quotes in his *Commentary* (rising and setting
statements, horizon-grazing figures), or MUL.APIN for the Mesopotamian layer. The unit would be the figure, or the
gaps *between* figures, not Ptolemy's star list. One telling check: bright stars that Ptolemy could see but left out
of every figure, such as α Gru (V = 1.7, about 4.5° up at Alexandria) and α Phe (V = 2.4, about 6°), sit in a gap
between figures that he did not fill. A model of where the *figures* stop could carry older information. The
counts would be small and the power low, so an honest result might well be "cannot tell". The worry is not
overblown for the verdict's wording. It is overblown only if the claim is narrowed to "Ptolemy's catalogued southern
edge is Hellenistic", which the study shows robustly.
