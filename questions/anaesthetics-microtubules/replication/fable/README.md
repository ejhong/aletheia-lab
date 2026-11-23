# Spot check of anaesthetics-microtubules by a second vendor

Claude Fable 5.2 (Anthropic), 23 November 2026, directed by Eugene. The study was run by Antigravity (Google
DeepMind). Eugene asked for a look-over and a spot check in place of a full re-run.

## What was checked

`spot_check.py` recomputes the study's main statistics from the committed table of docking scores
(`results/affinities.tsv`, 1,680 rows), written from `protocol.md` without using the study's analysis code.
`output.txt` holds what it printed. Every figure compared agrees with `RESULTS.md`:

| Protein | Potency correlation | After size | Anaesthetic outscores non-immobilizer |
|---|---|---|---|
| Tubulin 1JFF | +0.285 | +0.436 | 0.212 |
| Tubulin 4I4T | +0.347 | +0.441 | 0.079 |
| GABA-A | +0.416 | +0.548 | 0.079 |
| GLIC | +0.380 | +0.534 | 0.302 |
| Albumin | +0.279 | +0.373 | 0.085 |
| Luciferase | +0.212 | +0.313 | 0.116 |
| Lysozyme | +0.099 | −0.015 | 0.169 |
| Ubiquitin | +0.512 | +0.519 | 0.460 |

Also agreeing: the second scoring function (ubiquitin +0.596 and 0.794), the clinical-only correlations (tubulin
−0.133, GABA-A −0.067, GLIC +0.033), and the correlation of score with heavy-atom count (0.79 to 0.97 on seven
proteins).

**Not checked:** the docking itself. AutoDock Vina and Open Babel are not installed on this machine, so the 1,680
scores are taken as given. Nor the permutation p-values, the bootstrap comparisons, the potency values against
their sources, or the figures.

The lock is in its own commit, in the same second as the protocol commit. Amendment 1 (a less exhaustive search)
was committed four minutes later and an hour before the results; the log says the partial first run was deleted
unread. There was no outside review before the lock.

## Review notes

The statistics are right and the verdict follows from the rule. The reading needs care.

1. **The method fails its positive control, and that should lead.** On the GABA-A channel, an accepted
   anaesthetic target, non-immobilizers also score tighter than anaesthetics (0.08), and the unrelated protein
   ubiquitin tracks potency as well as anything. A calculation that cannot recognise a known target has no
   verdict to give on a disputed one. The study says this, as its fifth finding and in its limits, but its
   headline and its scorecard entry ("No tubulin signal", "Not found") read as a result against microtubules. The
   site page and the topic page now put it as "could not tell".
2. **The verdict rule had no outcome for this.** It asked whether tubulin tracked potency and beat the controls.
   It did not ask first whether the accepted targets did. A rule that began with the positive control would have
   returned "method not informative".
3. **Size explains most of it.** The scores follow the number of heavy atoms, and the non-immobilizers are bulky.
   The eighteen non-clinical anaesthetics are a homologous series, so any pocket ranks them by size; the nine
   clinical gases are tracked by no protein.
4. **The claim tested is the older and simpler one.** The 2017 paper by the theory's supporters is about what a
   bound anaesthetic does to oscillations in tubulin, not about binding strength. The study is clear that it does
   not test that.
5. **Tools.** Vina 1.2.5 and Open Babel 3.1.1 are pinned in the protocol. The run was on another machine, so the
   environment cannot be confirmed from here.
