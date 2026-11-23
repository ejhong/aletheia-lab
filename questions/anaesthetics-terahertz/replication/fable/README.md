# Spot check by a second model

Claude (Fable 5.2, Anthropic) looked this study over on 23 November 2026, at Eugene's request. It is a spot check and
not a full replication: the positions of the gases in each protein come from the docking run of #48, which was not
repeated here (AutoDock Vina is not installed on this machine). What follows was done without using the study's
solver.

## What was checked

1. **The statistics, from the results table.** Recomputed from `results/shifts.tsv` with separate code: the
   correlation with drug strength, the separation of anaesthetics from look-alike gases, the counts of downward and
   upward shifts and the 303 of 315 figure, for all nine targets. All match `RESULTS.md`.
2. **The empty-protein spectrum, from the structure files.** `spot_check.py` rebuilds the ring network of tubulin
   (1JFF) from the public file and gets 81 rings, 468.0 to 695.5 THz and 16 modes between 605 and 621 THz. That is
   the study's figure to the last digit.
3. **The direction of the shift.** A featureless probe of adjustable size was placed next to rings in tubulin, in
   lysozyme and in a cloud of 81 rings placed at random. In every case a small probe pushes the 613 THz band down
   and a large one pushes it up, and the changeover comes where the probe's own frequency crosses the band. The
   protein makes no difference. This agrees with the study's main finding.
4. **The two source papers, read in the original.** Kurian et al. 2018 (arXiv:1608.08097, LaTeX source) and
   Craddock et al. 2017 (PMC5575257) with its supplementary Table S1.

`output.txt` is the output of `spot_check.py`. To run it: `python spot_check.py <folder holding 1JFF.pdb and
1DPX.pdb>` (numpy only; the files are the ones in `MANIFEST.md`, and their checksums matched).

## Where this check agrees with the write-up

- The split between anaesthetics and look-alike gases in this model is set by the gas, not by the protein. The
  paper's own numbers fit that: it reports that both look-alike gases add a vibration below 594 THz, under the
  band, and Table S1 shows they are the two most polarisable molecules of its eleven (11.50 and 16.37 cubic
  ångströms; the anaesthetics run from 2.86 to 10.70).
- On the wider panel the split cannot hold. This does not depend on the details of the model. Anaesthetics and
  look-alikes overlap in polarisability (2.6 to 12.8 against 7.8 to 15.5), so no rule that turns on polarisability
  can sort them: ranking by polarisability alone gives 64% where 50% is chance.
- The calculation therefore gives no reason to single out tubulin.

## Where it does not

- **"Rebuilt the exact Hamiltonian" is too strong.** The paper's description is not complete enough to rebuild
  exactly, and is not consistent with itself. Craddock 2017 defines the mean polarisability as a third of the sum
  of the three values but takes the frequency from the root of the summed squares of three frequencies. Applied as
  printed, that puts a single tryptophan ring at 1,519 THz, far outside the paper's own range of 480 to 700 THz.
  The formula in Kurian 2018 (Table III: the root of the summed squares of the three polarisabilities) gives 531,
  579 and 605 THz for the three kinds of ring and does reproduce the range, so the study was right to use it. But
  it is a reconstruction.
- **The original result was only partly reproduced.** Seven of eight anaesthetics shift downward and both
  look-alikes upward. The paper's other result, that the shift grows with the strength of the drug, did not come
  out (correlation +0.12 across the eight). The rebuilt shifts are also much larger than the paper's ("of an order
  of 1 to 100 GHz" there; hundreds to thousands here). The structure, the gas positions and the estimate of the
  gases' polarisability all differ from the original, which used a simulation snapshot that is not public.
- **The rotation finding rests on one reading of one sentence.** Both papers say the diagonal elements of the
  polarisability tensor are kept and that the dipole direction is "the vector (α′xx, α′yy, α′zz) in the protein
  coordinate frame". The study reads this as: turn the tensor into the protein's frame, then keep the diagonal.
  Read that way the result does depend on how the file is oriented, and this check confirms it (the lowest mode of
  empty tubulin moves between 444 and 521 THz over 20 random turns). The sentence can also be read as: treat the
  three values as an arrow fixed to the ring, and turn the arrow. Kurian's Table III, which gives a single
  magnitude for each kind of ring, fits that reading better. Under it nothing changes when the structure is turned
  (492.8 THz every time), and the direction of the shift still follows the size of the gas. The authors' program is
  not public. So the study shows a weakness in the method as described, and has not shown an error in the
  published numbers.
- **"The split breaks down on the wider panel" is true of one measure and not of the paper's own.** The study
  judged the question on the signed largest shift in the band (`d_613_ghz`), as its locked plan said it would. The
  paper scored each gas by "the maximum frequency decrease in this range", which the study recorded as
  `d_down_613_ghz` and reported only in passing. `own_measure.py` works that column through (output in
  `own_measure.txt`). On it, anaesthetics outscore look-alikes 89% of the time on tubulin 1JFF (p = 0.001), and
  this is not molecular size: among the fifteen large molecules alone the figure is 92%. The GABA-A channel scores
  85% and albumin 83%; 4I4T scores 77% and GLIC 76%; lysozyme, ubiquitin, luciferase and the random rings score 68
  to 75%. Resampling the gases, tubulin 1JFF's lead over each of the last four has a 95% interval that stays above
  zero (for the random rings, +0.03 to +0.30). With gas positions from the second docking program the lead over
  the random rings shrinks (interval −0.02 to +0.30). The score does not follow drug strength on any target.
  This comparison was chosen after the results were known, is not corrected for the number of comparisons, and
  rests on seven look-alike gases. It is exploratory.
- **The same pattern shows in the orientation-proof version (Model B).** There tubulin 1JFF sorts the two classes
  at 79% (p = 0.016) and the two channels at 69% and 80%, while the unrelated proteins and the random rings sit
  between 38% and 59%. But 4I4T gives 51%.

Taken together: the model does respond to where a gas sits in a large protein with real pockets, and tubulin is
one of the proteins where it responds. It is not alone, and a protein that merely carries anaesthetics in the
blood does as well. "A level-repulsion artefact with no biology in it" describes the down-or-up split. It does not
describe everything in the results table.

## What it adds up to

The 2017 calculation, as far as it can be rebuilt, is not evidence that anaesthetics act on microtubules in
particular. Its best-known feature, anaesthetics pushing the vibration down and look-alikes pushing it up, follows
from the size of the molecules and appears for any set of rings. What survives, a larger disturbance from
anaesthetics than from look-alikes, appears equally in a known anaesthetic target and in a blood protein. The
paper's authors wrote that tests on other proteins were needed to see whether the effect was "universal or unique
to tubulin"; on these numbers it is not unique.

That is as far as the result goes. It is not evidence that anaesthetics do not act on microtubules: tubulin does
as well as the accepted target on every measure here. And it says nothing about the quantum physics of Orch OR,
which this classical model does not contain.
